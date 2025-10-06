#!/usr/bin/env python3
"""
5_inference_v2.py

Generates and visualizes fixture placements from a trained Conditional VTN model.
This version automatically loads model configuration from the checkpoint,
simplifying command-line usage. It also adds rotated bounding box rendering.

Example (PowerShell):
---------------------
# The script now infers model dimensions and geometry settings from the checkpoint.
# You only need to specify the files and generation parameters.
& ".venv\Scripts\python.exe" 5_inference.py `
  --checkpoint "runs/vtn_30e/checkpoints/best.pt" `
  --image "data/2025.06.08_APPROVED LAYOUT PLAN-Model-5-ground.png" `
  --out_dir "outputs/your_floorplan" `
  --top_p 0.95 --temperature 0.9
"""

import argparse
import json
import shutil
from pathlib import Path
import math
from typing import Dict, List, Tuple, Optional, Any

import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont
from torchvision import transforms as T
import cv2

# Add parent directory to path for imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

# Import enhanced constraints
from enhanced_constraints_v2 import EnhancedConstraints as EnhancedOpticalStoreConstraints

# Import current model architecture (v2 naming not used in this repo)
try:
    from model_architecture import ConditionalVTN, VTNConfig, subsequent_mask
except ImportError:
    print("[WARN] Falling back to dummy model_architecture (file missing)")
    class VTNConfig:  # minimal placeholder
        def __init__(self, **kw): self.__dict__.update(kw)
    class ConditionalVTN(torch.nn.Module):
        def __init__(self, cfg): super().__init__(); self.cfg = cfg
        def generate(self, images, start_id, end_id, max_len=64, temperature=1.0, top_k=None):
            B = images.size(0)
            return torch.randint(0, 100, (B, max_len))


# ----------------------------
# Checkpoint & Model Loading
# ----------------------------

def load_model_from_checkpoint(checkpoint_path: Path, device: torch.device):
    """Loads model + vocab + config from training checkpoint produced by 4_train.py."""
    ckpt = torch.load(checkpoint_path, map_location=device)

    if 'model' not in ckpt:
        raise ValueError("Checkpoint missing 'model' state_dict")

    # Preferred new format: we stored run_cfg dict inside 'config'
    run_cfg = ckpt.get('config', {})
    # Backward compat: some alternate trainer may store 'args'
    args_like = ckpt.get('args', None)
    if args_like and not run_cfg:
        # convert argparse Namespace to dict
        if hasattr(args_like, '__dict__'):
            run_cfg = vars(args_like)
        else:
            run_cfg = dict(args_like)

    if not run_cfg:
        raise ValueError("No config/args found in checkpoint; cannot reconstruct model")

    vocab_path = run_cfg.get('vocab') or run_cfg.get('vocab_path') or 'data/vocab.json'
    vocab_path = Path(vocab_path)
    if not vocab_path.exists():
        raise FileNotFoundError(f"Vocab file '{vocab_path}' not found (from checkpoint config)")
    with open(vocab_path, 'r', encoding='utf-8') as f:
        vocab = json.load(f)

    # Derive channel count from stored flags (they were added into run_cfg)
    in_channels = run_cfg.get('in_channels')
    if in_channels is None:
        in_channels = 3 + sum([
            int(run_cfg.get('add_edge_channel', 0)),
            int(run_cfg.get('add_wall_mask', 0)),
            int(run_cfg.get('add_room_mask', 0))
        ])

    # Build config with safe defaults for fields possibly absent in old checkpoints
    cfg = VTNConfig(
        vocab_size=len(vocab),
        pad_id=run_cfg.get('pad_id', vocab.get('<PAD>', 0)),
        start_id=run_cfg.get('start_id', vocab.get('<START>', 1)),
        end_id=run_cfg.get('end_id', vocab.get('<END>', 2)),
        d_model=run_cfg.get('d_model', 512),
        n_heads=run_cfg.get('n_heads', 8),
        d_ff=run_cfg.get('d_ff', 2048),
        num_enc_layers=run_cfg.get('num_enc_layers', 4),
        num_dec_layers=run_cfg.get('num_dec_layers', 6),
        dropout=run_cfg.get('dropout', 0.1),
        in_channels=in_channels,
        cnn_out_dim=run_cfg.get('cnn_out_dim', 256),
        latent_dim=run_cfg.get('latent_dim', 128),
        beta_kl=run_cfg.get('beta_kl', 0.1),
        kl_warmup_steps=run_cfg.get('kl_warmup_steps', 0),
        free_bits=run_cfg.get('free_bits', 0.0),
        max_seq_len=run_cfg.get('max_seq_len', 512),
        tie_embeddings=True,
        label_smoothing=run_cfg.get('label_smoothing', 0.0),
        use_pretrained_cnn=run_cfg.get('use_pretrained_cnn', False),
        freeze_cnn=run_cfg.get('freeze_cnn', False),
        grad_checkpoint=False,
        use_token_type_emb=run_cfg.get('use_token_type_emb', False),
        num_token_types=run_cfg.get('num_token_types', 7),
    )

    model = ConditionalVTN(cfg)
    model.load_state_dict(ckpt['model'], strict=True)
    # Rebuild token type mapping (was not saved – buffer is non-persistent)
    if cfg.use_token_type_emb:
        mapping = torch.zeros(len(vocab), dtype=torch.long)
        for tok, tid in vocab.items():
            if tok.startswith('cls_'):
                mapping[tid] = 1
            elif tok.startswith('x_bin_'):
                mapping[tid] = 2
            elif tok.startswith('y_bin_'):
                mapping[tid] = 3
            elif tok.startswith('w_bin_'):
                mapping[tid] = 4
            elif tok.startswith('h_bin_'):
                mapping[tid] = 5
            elif tok.startswith('angle_bin_'):
                mapping[tid] = 6
        model.enc_tokens.set_token_type_ids(mapping)
    model.to(device).eval()
    return model, vocab, run_cfg

# ----------------------------
# Image & Geometry Loading
# ----------------------------

def _get(cfg, key, default=None):
    if isinstance(cfg, dict):
        return cfg.get(key, default)
    return getattr(cfg, key, default)

def load_image_with_geometry(img_path: Path, train_args, expected_in_channels: int = None) -> Tuple[torch.Tensor, Tuple[int, int]]:
    """Loads an image and its corresponding geometry channels based on training args (dict or Namespace)."""
    image_size = int(_get(train_args, 'image_size', 256))
    geom_dir = _get(train_args, 'geom_dir', 'data/geom_masks')
    with Image.open(img_path).convert("RGB") as im:
        orig_W, orig_H = im.size
        tfm = T.Compose([
            T.Resize((image_size, image_size)),
            T.ToTensor(),
            T.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)),
        ])
        rgb_t = tfm(im)

    channels = [rgb_t]
    
    # Helper to load and resize a mask
    def _get_mask(mask_type: str) -> Optional[torch.Tensor]:
        mask_path = Path(geom_dir) / f"{img_path.stem}_{mask_type}.png"
        if mask_path.exists():
            mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
            mask = cv2.resize(mask, (image_size, image_size), interpolation=cv2.INTER_NEAREST)
            return torch.from_numpy(mask).float().div(255.0).unsqueeze(0)
        return None

    if bool(_get(train_args, 'add_edge_channel', False)):
        edge_mask = _get_mask('edge')
        if edge_mask is not None:
            channels.append(edge_mask)
        else: # Fallback to Canny edge detection
            rgb_np = (rgb_t.cpu().numpy() * 0.5 + 0.5).clip(0,1) * 255
            gray = cv2.cvtColor(rgb_np.transpose(1, 2, 0).astype(np.uint8), cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            channels.append(torch.from_numpy(edges).float().div(255.0).unsqueeze(0))

    if bool(_get(train_args, 'add_wall_mask', False)):
        wall_mask = _get_mask('wall')
        if wall_mask is not None: channels.append(wall_mask)

    if bool(_get(train_args, 'add_room_mask', False)):
        room_mask = _get_mask('room')
        if room_mask is not None: channels.append(room_mask)

    img_tensor = torch.cat(channels, dim=0)  # [C,H,W]
    if expected_in_channels is not None and img_tensor.size(0) != expected_in_channels:
        C, H, W = img_tensor.shape
        if C < expected_in_channels:
            pad = torch.zeros(expected_in_channels - C, H, W, dtype=img_tensor.dtype)
            img_tensor = torch.cat([img_tensor, pad], dim=0)
        elif C > expected_in_channels:
            img_tensor = img_tensor[:expected_in_channels]
    return img_tensor.unsqueeze(0), (orig_W, orig_H)

# ----------------------------
# Token Parsing
# ----------------------------

def parse_layout_tokens(tokens: List[str], img_size_px: Tuple[int, int], expect_angle: bool = True) -> List[Dict]:
    """Robustly parse tokens of pattern: cls_X, x_bin_i, y_bin_j, w_bin_k, h_bin_l, (optional angle_bin_m).

    The old parser assumed every fixture had angle and strictly ordered tokens; this version:
    - Validates each geometry token prefix before consuming.
    - Treats angle token as optional.
    - Skips (rather than crashes) on malformed spans.
    - Stops at END if present.
    """
    W, H = img_size_px
    out: List[Dict[str, Any]] = []
    NUM_BINS = 256
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t == '<END>':
            break
        if not t.startswith('cls_'):
            i += 1
            continue
        category = t[4:]
        # Need at least next 4 geometry tokens
        j = i + 1
        needed = []
        for pref in ['x_bin_', 'y_bin_', 'w_bin_', 'h_bin_']:
            if j < len(tokens) and tokens[j].startswith(pref):
                needed.append(tokens[j]); j += 1
            else:
                needed = []
                break
        if not needed:
            # Could not parse geometry for this class; advance one and retry
            i += 1
            continue
        angle_token = None
        if expect_angle and j < len(tokens) and tokens[j].startswith('angle_bin_'):
            angle_token = tokens[j]; j += 1
        try:
            x_bin = int(needed[0].split('_')[-1])
            y_bin = int(needed[1].split('_')[-1])
            w_bin = int(needed[2].split('_')[-1])
            h_bin = int(needed[3].split('_')[-1])
            x = (x_bin + 0.5) / NUM_BINS * W
            y = (y_bin + 0.5) / NUM_BINS * H
            w = (w_bin + 0.5) / NUM_BINS * W
            h = (h_bin + 0.5) / NUM_BINS * H
            item = {
                'category': category,
                'bbox_center': [round(x,2), round(y,2)],
                'bbox_size': [round(w,2), round(h,2)],
                'x': round(x,2),  # Center x for enhanced constraints
                'y': round(y,2),  # Center y for enhanced constraints
                'w': round(w,2),  # Width for enhanced constraints
                'h': round(h,2)   # Height for enhanced constraints
            }
            if angle_token is not None:
                angle_bin = int(angle_token.split('_')[-1])
                angle = (angle_bin + 0.5) / NUM_BINS * 360.0
                item['angle'] = round(angle,2)
            out.append(item)
        except ValueError:
            pass
        i = j
    return out
    
# ----------------------------
# Visualization
# ----------------------------
def draw_overlay(base_img_path: Path, fixtures: List[Dict], out_png: Path, alpha: float = 0.3):
    """Draws rotated bounding boxes and labels on the base image."""
    im = Image.open(base_img_path).convert("RGBA")
    overlay = Image.new("RGBA", im.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    font = ImageFont.load_default()

    for item in fixtures:
        category = item["category"]
        cx, cy = item["bbox_center"]
        w, h = item["bbox_size"]
        angle = -item.get("angle", 0.0) # default 0 if absent; PIL uses clockwise rotation
        
        # Create a rectangle patch
        w_i = max(3, int(round(w))); h_i = max(3, int(round(h)))
        rect = Image.new('RGBA', (w_i, h_i))
        rect_draw = ImageDraw.Draw(rect)
        
        color = tuple(np.random.randint(50, 200, 3))
        fill_color = (*color, int(alpha * 255))
        outline_color = (*color, 255)
        
        rect_draw.rectangle([(0, 0), (w_i, h_i)], fill=fill_color, outline=outline_color, width=3)
        
        # Rotate and paste the rectangle onto the overlay
        rotated_rect = rect.rotate(angle, expand=True, resample=Image.BICUBIC)
        paste_x = int(cx - rotated_rect.width / 2)
        paste_y = int(cy - rotated_rect.height / 2)
        overlay.paste(rotated_rect, (paste_x, paste_y), rotated_rect)
        
        # Draw label
        draw.text((cx, cy), category, fill="black", font=font, anchor="ms")

    # Composite the overlay onto the original image
    im = Image.alpha_composite(im, overlay).convert("RGB")
    im.save(out_png)
    print(f"[OK] Wrote overlay PNG -> {out_png.resolve()}")

# ----------------------------
# Fixture Post-Processing
# ----------------------------

def _snap_inside_room(fixtures, masks, img_wh):
    """Post-snap fixtures inside room before saving (full box fits)"""
    W,H = img_wh
    room = masks.get("room"); 
    if room is None: return fixtures
    safe = (room > 0).astype(np.uint8)
    for f in fixtures:
        # erode mask by half box to keep entire rect inside
        w_px, h_px = f["bbox_size"]
        rx = max(1, int((w_px/W)*256/2))
        ry = max(1, int((h_px/H)*256/2))
        ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*rx+1, 2*ry+1))
        safe_erode = cv2.erode(safe, ker, iterations=1)

        xi = int((f["bbox_center"][0]/W)*255)
        yi = int((f["bbox_center"][1]/H)*255)
        if 0<=yi<256 and 0<=xi<256 and safe_erode[yi,xi]:
            continue
        ys,xs = np.where(safe_erode>0)
        if len(xs)==0: continue
        idx = np.argmin((xs-xi)**2 + (ys-yi)**2)
        xi2, yi2 = int(xs[idx]), int(ys[idx])
        f["bbox_center"][0] = (xi2+0.5)/256*W
        f["bbox_center"][1] = (yi2+0.5)/256*H
        f["x"], f["y"] = f["bbox_center"]
    return fixtures

# ----------------------------
# Main Execution
# ----------------------------
def main(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # --- Load Model ---
    model, vocab, train_args = load_model_from_checkpoint(Path(args.checkpoint), device)
    if model is None:
        print("[ERROR] Failed to load model from checkpoint. Please ensure it's a valid checkpoint from 4_train_v2.py")
        return
        
    id2tok = {v: k for k, v in vocab.items()}

    # --- Safety: clamp max_len to model positional capacity ---
    model_max_len = getattr(model.config, 'max_seq_len', None) if hasattr(model, 'config') else None
    if model_max_len is not None and args.max_len > model_max_len:
        print(f"[WARN] Requested max_len={args.max_len} exceeds model max_seq_len={model_max_len}. Clamping to {model_max_len}.")
        args.max_len = model_max_len

    # --- Prepare Image ---
    img_path = Path(args.image)
    expected_c = getattr(model.config, 'in_channels', None)
    image_tensor, (orig_W, orig_H) = load_image_with_geometry(img_path, train_args, expected_in_channels=expected_c)
    image_tensor = image_tensor.to(device)

    # --- Generate Tokens ---
    cfg = model.config if hasattr(model, 'config') else None
    start_id = cfg.start_id if cfg else vocab.get('<START>', 1)
    end_id = cfg.end_id if cfg else vocab.get('<END>', 2)

    def apply_sampling_filters(logits: torch.Tensor) -> torch.Tensor:
        if args.top_k is not None and args.top_k > 0:
            topk = min(args.top_k, logits.size(-1))
            vals, idx = torch.topk(logits, k=topk, dim=-1)
            masked = torch.full_like(logits, float('-inf'))
            masked.scatter_(1, idx, vals)
            logits = masked
        # temperature
        logits = logits / max(args.temperature, 1e-6)
        probs = torch.softmax(logits, dim=-1)
        if args.top_p is not None:
            sorted_probs, sorted_idx = torch.sort(probs, descending=True, dim=-1)
            cumulative = torch.cumsum(sorted_probs, dim=-1)
            cutoff = cumulative > args.top_p
            cutoff[..., 1:] = cutoff[..., :-1].clone()
            cutoff[..., 0] = False
            sorted_probs[cutoff] = 0.0
            sorted_probs = sorted_probs / sorted_probs.sum(dim=-1, keepdim=True)
            probs = torch.zeros_like(probs).scatter(1, sorted_idx, sorted_probs)
        return probs

    with torch.no_grad():
        c_img = model.encode_condition(image_tensor)
        mu_p, logvar_p = model.prior(c_img)
        z = mu_p + torch.exp(0.5 * logvar_p) * torch.randn_like(mu_p)
        seq = torch.full((1, 1), start_id, dtype=torch.long, device=device)
        attn = torch.ones(1, 1, dtype=torch.long, device=device)

        # Precompute token groups for constrained mode
        token_groups = {}
        if args.constrained:
            # id2tok: id -> token string
            token_groups = {
                'class': [tid for tid, tok in id2tok.items() if tok.startswith('cls_')],
                'x': [tid for tid, tok in id2tok.items() if tok.startswith('x_bin_')],
                'y': [tid for tid, tok in id2tok.items() if tok.startswith('y_bin_')],
                'w': [tid for tid, tok in id2tok.items() if tok.startswith('w_bin_')],
                'h': [tid for tid, tok in id2tok.items() if tok.startswith('h_bin_')],
                'angle': [tid for tid, tok in id2tok.items() if tok.startswith('angle_bin_')],
            }

        # Initialize constraints object
        def _get(train_args, key, default):
            return getattr(train_args, key, default) if hasattr(train_args, key) else default
        
        constraints_obj = EnhancedOpticalStoreConstraints(geom_dir=_get(train_args,'geom_dir','data/geom_masks')) \
                          if args.use_rules else None

        # Parse max_per_class and helper to count current fixtures
        max_per = {}
        if args.max_per_class:
            for kv in args.max_per_class.split(","):
                if not kv: continue
                k,v = kv.split(":"); max_per[k.strip()] = int(v)
        
        # Update constraints object with CLI overrides
        if constraints_obj and max_per:
            constraints_obj.update_max_per_class(max_per)

        def _counts(fixt):
            d={}
            for f in fixt: d[f["category"]] = d.get(f["category"],0)+1
            return d

        def step_logits(current_seq: torch.Tensor) -> torch.Tensor:
            L = current_seq.size(1)
            pos = torch.arange(L, device=device).unsqueeze(0)
            tgt = model.enc_tokens.embed_tokens(current_seq, pos)
            tgt_pad = attn == 0
            causal = subsequent_mask(L, device=device)
            mem = model.dec.cond_proj(torch.cat([c_img, z], dim=1)).unsqueeze(1)
            h = model.dec.decoder(
                tgt=tgt,
                memory=mem,
                tgt_mask=causal,
                tgt_key_padding_mask=tgt_pad,
                memory_key_padding_mask=None
            )
            h = model.dec.layer_norm(h)
            return model.dec.output_proj(h)[:, -1, :]

        fixtures_emitted = 0
        expected_phase = 'class'  # class -> x -> y -> w -> h -> (angle?) -> class
        geom_order = ['x', 'y', 'w', 'h']
        geom_idx = 0
        while seq.size(1) < args.max_len:
            logits = step_logits(seq)
            # Constrained filtering
            if args.constrained:
                allowed_ids = None
                if expected_phase == 'class':
                    if args.max_fixtures and fixtures_emitted >= args.max_fixtures:
                        # force END
                        seq = torch.cat([seq, torch.tensor([[end_id]], device=device)], dim=1)
                        break
                    
                    # MATHEMATICAL MODEL INTEGRATION: Check fixture limits during class selection
                    if args.use_rules and constraints_obj is not None:
                        current_tokens = [id2tok.get(int(t), '') for t in seq[0].tolist()]
                        placed_fixtures = parse_layout_tokens(current_tokens, (orig_W, orig_H), expect_angle=args.expect_angle)
                        fixture_counts = _counts(placed_fixtures)
                        
                        # Filter out classes that have reached their mathematical model limits
                        filtered_class_ids = []
                        for tid in token_groups['class']:
                            class_name = id2tok[tid][4:]  # Remove 'cls_' prefix
                            current_count = fixture_counts.get(class_name, 0)
                            max_allowed = constraints_obj.max_per_class.get(class_name, float('inf'))
                            
                            if current_count < max_allowed:
                                filtered_class_ids.append(tid)
                            else:
                                if args.debug:
                                    print(f"DEBUG: MATHEMATICAL MODEL BLOCK - {class_name} at limit {current_count}/{max_allowed}")
                        
                        allowed_ids = filtered_class_ids
                    else:
                        allowed_ids = token_groups['class']
                elif expected_phase in geom_order:
                    allowed_ids = token_groups[expected_phase]
                elif expected_phase == 'angle':
                    allowed_ids = token_groups['angle'] if args.expect_angle else []
                    
                if allowed_ids:
                    mask = torch.full_like(logits, float('-inf'))
                    mask[0, allowed_ids] = logits[0, allowed_ids]
                    logits = mask
            # Enhanced domain rule spatial biases using detailed optical store constraints  
            if args.use_rules and args.constrained and expected_phase in ['x','y'] and constraints_obj is not None:
                # build cached bin pairs once
                if not hasattr(model, '_rule_cache_v2'):
                    x_pairs = [(tid, int(id2tok[tid].split('_')[-1])) for tid in token_groups['x']]
                    y_pairs = [(tid, int(id2tok[tid].split('_')[-1])) for tid in token_groups['y']]
                    model._rule_cache_v2 = {'x_pairs': x_pairs, 'y_pairs': y_pairs}

                # parse context fixtures so far
                current_tokens = [id2tok.get(int(t), '') for t in seq[0].tolist()]
                placed_fixtures = parse_layout_tokens(current_tokens, (orig_W, orig_H), expect_angle=args.expect_angle)

                # last class being placed
                last_class = next((tok[4:] for tok in reversed(current_tokens) if tok.startswith('cls_')), None)
                if last_class:
                    token_pairs = model._rule_cache_v2['x_pairs' if expected_phase == 'x' else 'y_pairs']
                    logits = constraints_obj.apply_enhanced_logit_constraints(
                        logits, token_pairs, last_class, expected_phase,
                        context_fixtures=placed_fixtures, image_name=Path(args.image).name
                    )

            # MATHEMATICAL MODEL SIZE CONSTRAINTS for w_bin and h_bin phases
            if args.use_rules and args.constrained and expected_phase in ['w', 'h'] and constraints_obj is not None:
                # build cached bin pairs for width/height
                if not hasattr(model, '_size_cache'):
                    w_pairs = [(tid, int(id2tok[tid].split('_')[-1])) for tid in token_groups['w']]
                    h_pairs = [(tid, int(id2tok[tid].split('_')[-1])) for tid in token_groups['h']]
                    model._size_cache = {'w_pairs': w_pairs, 'h_pairs': h_pairs}

                # parse context fixtures so far
                current_tokens = [id2tok.get(int(t), '') for t in seq[0].tolist()]
                placed_fixtures = parse_layout_tokens(current_tokens, (orig_W, orig_H), expect_angle=args.expect_angle)

                # last class being placed
                last_class = next((tok[4:] for tok in reversed(current_tokens) if tok.startswith('cls_')), None)
                if last_class and hasattr(constraints_obj, 'apply_mathematical_size_constraints'):
                    token_pairs = model._size_cache['w_pairs' if expected_phase == 'w' else 'h_pairs']
                    logits = constraints_obj.apply_mathematical_size_constraints(
                        logits, token_pairs, last_class, expected_phase,
                        context_fixtures=placed_fixtures, image_name=Path(args.image).name
                    )

            # Enhanced class-phase constraints (max counts, prerequisites, required classes)
            if args.constrained and expected_phase == 'class':
                # parse what we have so far
                cur_tokens = [id2tok.get(int(t), '') for t in seq[0].tolist()]
                placed = parse_layout_tokens(cur_tokens, (orig_W, orig_H), expect_angle=args.expect_angle)
                counts = _counts(placed)

                # ULTRA-STRICT MATHEMATICAL MODEL ENFORCEMENT during generation
                if constraints_obj is not None:
                    # Get mathematical model limits
                    max_per_class = getattr(constraints_obj, 'max_per_class', {})
                    
                    # ABSOLUTE BLOCKING for limits reached
                    blocked_categories = set()
                    for cat, count in counts.items():
                        max_allowed = max_per_class.get(cat, float('inf'))
                        if count >= max_allowed:
                            blocked_categories.add(cat)
                            print(f"MATHEMATICAL MODEL BLOCK: {cat} at limit {count}/{max_allowed}")
                    
                    # SPECIAL ULTRA-STRICT EURO CENTRE ENFORCEMENT (This works perfectly!)
                    euro_count = counts.get('euro_centre', 0)
                    if euro_count >= 2:
                        blocked_categories.add('euro_centre')
                        print(f"EURO CENTRE MATHEMATICAL LIMIT: Already {euro_count} euro centres, BLOCKING FURTHER GENERATION")
                    
                    # APPLY SAME ULTRA-STRICT LOGIC TO ALL CRITICAL CATEGORIES
                    # VC Fixtures - Apply euro centre level blocking
                    vc_large_count = counts.get('vc_fixture_large', 0)
                    if vc_large_count >= 5:
                        blocked_categories.add('vc_fixture_large')
                        print(f"VC LARGE MATHEMATICAL LIMIT: Already {vc_large_count} vc_fixture_large, BLOCKING FURTHER GENERATION")
                    
                    vc_medium_count = counts.get('vc_fixture_medium', 0) 
                    if vc_medium_count >= 7:
                        blocked_categories.add('vc_fixture_medium')
                        print(f"VC MEDIUM MATHEMATICAL LIMIT: Already {vc_medium_count} vc_fixture_medium, BLOCKING FURTHER GENERATION")
                    
                    # Block disabled fixtures (0 limits) completely - ULTRA STRICT
                    for cat, limit in max_per_class.items():
                        if limit == 0:
                            blocked_categories.add(cat)
                            print(f"DISABLED FIXTURE BLOCK: {cat} is disabled (limit=0)")
                    
                    # ADDITIONAL EXPLICIT BLOCKING for problematic categories
                    always_blocked = ['jj_fixture_different_large', 'mirror_different', 'discussion_table_large', 'discussion_table_small', 'large_bench']
                    for cat in always_blocked:
                        if cat not in blocked_categories:
                            blocked_categories.add(cat)
                            print(f"EXPLICIT MATHEMATICAL BLOCK: {cat} (mathematical model disabled)")
                    
                    # Apply blocks to logits with MAXIMUM STRENGTH
                    if blocked_categories:
                        for tid in token_groups['class']:
                            cat = id2tok[int(tid)][4:]
                            if cat in blocked_categories:
                                logits[0, tid] = float('-inf')

                # hard/soft class constraints from rules
                if constraints_obj is not None:
                    logits = constraints_obj.apply_class_constraints(logits, token_groups['class'], id2tok, placed)

                # enforce max_per caps from CLI
                if max_per:
                    for tid in token_groups['class']:
                        cat = id2tok[int(tid)][4:]
                        if cat in max_per and counts.get(cat,0) >= max_per[cat]:
                            logits[0, tid] = float('-inf')

                # ensure required classes
                if args.required:
                    missing = {c for c in args.required if counts.get(c,0) == 0}
                    if missing:
                        if args.force_required_first:
                            mask = torch.full_like(logits, float('-inf'))
                            for tid in token_groups['class']:
                                cat = id2tok[int(tid)][4:]
                                if cat in missing:
                                    mask[0, tid] = logits[0, tid]
                            logits = mask
                        else:
                            for tid in token_groups['class']:
                                cat = id2tok[int(tid)][4:]
                                if cat in missing:
                                    logits[0, tid] += 6.0    # strong boost
                    
            probs = apply_sampling_filters(logits)
            next_tok = torch.multinomial(probs, 1)
            tok_id = next_tok.item()
            seq = torch.cat([seq, next_tok], dim=1)
            attn = torch.cat([attn, torch.ones(1,1,dtype=torch.long, device=device)], dim=1)
            if tok_id == end_id:
                break
            if args.constrained:
                tok_str = id2tok.get(tok_id, '')
                if expected_phase == 'class' and tok_str.startswith('cls_'):
                    expected_phase = 'x'; geom_idx = 0
                elif expected_phase in geom_order and tok_str.startswith(f'{expected_phase}_bin_'):
                    geom_idx += 1
                    if geom_idx < len(geom_order):
                        expected_phase = geom_order[geom_idx]
                    else:
                        # Finished x,y,w,h. Only count a fixture if we're NOT expecting an angle.
                        if args.expect_angle and token_groups.get('angle'):
                            expected_phase = 'angle'
                        else:
                            expected_phase = 'class'
                            fixtures_emitted += 1
                elif expected_phase == 'angle' and tok_str.startswith('angle_bin_'):
                    expected_phase = 'class'
                    fixtures_emitted += 1
                # else: leave phase unchanged and let the model self-correct on next step
        seq_ids = seq[0]
    
    tokens = [id2tok.get(int(i), "<UNK>") for i in seq_ids.tolist()]
    
    # --- Process and Save Results ---
    fixtures = parse_layout_tokens(tokens, (orig_W, orig_H), expect_angle=args.expect_angle)
    
    # Apply ULTRA-STRICT mathematical model post-generation filter for absolute compliance
    # NOTE: Adding ultra-strict post-generation filtering to achieve ultra_strict_test accuracy
    if constraints_obj is not None and args.use_rules:
        print(f"[INFO] Applying ULTRA-STRICT mathematical model post-generation filter")
        original_count = len(fixtures)
        
        # Custom ultra-strict filtering matching ultra_strict_test success
        max_per_class = getattr(constraints_obj, 'max_per_class', {})
        filtered_fixtures = []
        category_counts = {}
        
        # STEP 1: Completely remove all disabled fixtures (0 limits)
        always_blocked = ['jj_fixture_different_large', 'mirror_different', 'discussion_table_large', 'discussion_table_small', 'large_bench']
        
        for fixture in fixtures:
            category = fixture.get('category', 'unknown')
            
            # ABSOLUTE BLOCK: Remove disabled fixtures
            if category in always_blocked:
                print(f"ULTRA-STRICT FILTER: Removing DISABLED fixture {category}")
                continue
                
            # ABSOLUTE BLOCK: Check mathematical model limits
            max_allowed = max_per_class.get(category, float('inf'))
            if max_allowed == 0:
                print(f"ULTRA-STRICT FILTER: Removing mathematical model disabled {category}")
                continue
                
            current_count = category_counts.get(category, 0)
            if current_count < max_allowed:
                filtered_fixtures.append(fixture)
                category_counts[category] = current_count + 1
                print(f"ULTRA-STRICT FILTER: Keeping {category} ({current_count + 1}/{max_allowed})")
            else:
                print(f"ULTRA-STRICT FILTER: Removing excess {category} (limit: {max_allowed})")
        
        fixtures = filtered_fixtures
        print(f"[INFO] ULTRA-STRICT mathematical model filter: {original_count} → {len(fixtures)} fixtures")
    
    # Apply fixture snapping to keep them inside room bounds
    if constraints_obj is not None:
        masks = constraints_obj.load_geometric_masks(Path(args.image).name, (256,256))
        fixtures = _snap_inside_room(fixtures, masks, (orig_W, orig_H))
    
    # Create output directory
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save a copy of the original input image for reference
    try:
        dest_original = out_dir / img_path.name
        if not dest_original.exists():  # avoid overwriting silently
            shutil.copy2(img_path, dest_original)
            print(f"[OK] Copied original image -> {dest_original.resolve()}")
        else:
            print(f"[INFO] Original image already exists in output folder: {dest_original.name}")
    except Exception as e:
        print(f"[WARN] Could not copy original image: {e}")

    # Also save the resized (model input) RGB image for debugging (denormalized)
    try:
        # image_tensor shape: [1, C, H, W]; first 3 channels are RGB (normalized to (-1,1))
        resized_rgb = image_tensor[0, :3].detach().cpu().clone()
        resized_rgb = (resized_rgb * 0.5 + 0.5).clamp(0, 1)  # denormalize
        resized_np = (resized_rgb.numpy() * 255).astype('uint8').transpose(1, 2, 0)
        resized_pil = Image.fromarray(resized_np)
        resized_path = out_dir / f"{img_path.stem}_resized.png"
        resized_pil.save(resized_path)
        print(f"[OK] Saved resized model-input image -> {resized_path.resolve()}")
    except Exception as e:
        print(f"[WARN] Could not save resized image: {e}")
    
    # Save JSON
    json_path = out_dir / f"{img_path.stem}_layout.json"
    result = {
        "image_filename": img_path.name,
        "image_size": {"width": orig_W, "height": orig_H},
        "num_fixtures": len(fixtures),
        "tokens": tokens,
        "fixtures": fixtures,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"[OK] Wrote layout JSON -> {json_path.resolve()}")
    
    # Save PNG Overlay (unless disabled) - renamed to *_layout.png per user preference
    if not getattr(args, 'no_overlay', False):
        png_path = out_dir / f"{img_path.stem}_layout.png"
        draw_overlay(img_path, fixtures, png_path)
    else:
        print("[INFO] Overlay generation skipped (--no_overlay)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate layouts with a trained Conditional VTN model.")
    
    # Required Paths
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to the model checkpoint (best.pt or last.pt).")
    parser.add_argument("--image", type=str, required=True, help="Path to the input floorplan image.")
    parser.add_argument("--out_dir", type=str, default="outputs/inference_run", help="Directory to save the output JSON and PNG.")

    # Generation Parameters
    parser.add_argument("--max_len", type=int, default=300, help="Maximum number of tokens to generate.")
    parser.add_argument("--temperature", type=float, default=1.0, help="Sampling temperature. Higher is more random.")
    parser.add_argument("--top_k", type=int, default=None, help="Top-K sampling. K most likely next words are filtered.")
    parser.add_argument("--top_p", type=float, default=0.95, help="Nucleus sampling. Chooses from the smallest set of words whose probability adds up to top_p.")
    parser.add_argument("--no_overlay", action="store_true", help="Skip saving overlay PNG (only JSON output).")
    parser.add_argument("--constrained", action="store_true", help="Use constrained decoding (enforces cls->x->y->w->h->(angle) pattern).")
    parser.add_argument("--max_fixtures", type=int, default=None, help="Maximum number of fixtures to attempt to emit in constrained mode.")
    parser.add_argument("--expect_angle", action="store_true", help="Expect angle tokens during parsing & constrained decoding.")
    parser.add_argument("--use_rules", action="store_true", help="Apply domain rule-based spatial logit biases for x/y bins.")
    parser.add_argument("--debug", action="store_true", help="Enable debug prints for constraint application.")
    
    # New CLI flags for enhanced constraints
    parser.add_argument("--required", nargs="*", default=[],
        help="Class names that must appear at least once (e.g. euro_centre screen_55 lensometer).")
    parser.add_argument("--force_required_first", action="store_true",
        help="Until all --required are emitted, mask other classes.")
    parser.add_argument("--max_per_class", type=str, default="",
        help="Comma list cat:count,... to cap duplicates (e.g. regular_clinic:1,clinic_with_sink:1)")

    args = parser.parse_args()
    main(args)