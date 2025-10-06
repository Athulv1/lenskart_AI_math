# AI Pipeline for Lenskart Layout Generation

This directory contains the complete AI pipeline for optical store layout generation with enhanced merchmix integration.

## 🚀 Features

- **VTN Model Inference**: Initial layout generation from floor plans
- **Gemini 2.5 Flash**: Enhanced image generation with merchmix requirements
- **Gemini 2.5 Pro**: JSON conversion with compliance validation
- **Layout Merger**: Combines wall boundaries with fixture placements

## 📁 Directory Structure

```
ai_pipeline/
├── main_orchestrator.py          # Main pipeline orchestrator
├── scripts/                      # Individual pipeline scripts
│   ├── 5_inference.py            # VTN model inference
│   ├── gemini_25_layout_generator.py  # Gemini image generation
│   ├── gemini_image_to_json.py   # Gemini JSON conversion
│   └── merge_layouts.py          # Layout merger
├── config/                       # Configuration files
│   ├── prompt.txt                # Gemini prompt template
│   └── vtn_enhanced_500epoch/    # VTN model configuration
├── data/                         # Sample floor plan images
├── examples/                     # Example configurations
└── outputs/                      # Generated outputs
```

## 🔧 Setup

### Model Files Required

The VTN model checkpoint files are too large for GitHub (>500MB each). Download them separately:

1. `best.pt` - Main model checkpoint
2. `best_ema.pt` - EMA model checkpoint  
3. `last.pt` - Latest model checkpoint

Place these files in: `config/vtn_enhanced_500epoch/checkpoints/`

### Environment Variables

Required environment variables for Gemini API:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

## 🚀 Usage

### Complete Pipeline with Merchmix Integration

```bash
python main_orchestrator.py \
  --image "data/floorplan_whitefield.png" \
  --wall-json "input_wall_json/White_filed_Bangalore.json" \
  --merchmix "White_Field_merch_mix.json" \
  --output-dir "results"
```

### Parameters

- `--image`: Input floor plan image
- `--wall-json`: Wall boundary definitions (JSON)
- `--merchmix`: Merchmix fixture requirements (JSON)
- `--output-dir`: Output directory for results

## 📊 Pipeline Flow

1. **VTN Model** → Generates initial layout from image
2. **Gemini Image Generator** → Creates enhanced layout with merchmix requirements
3. **Gemini JSON Converter** → Converts image to JSON with compliance validation
4. **Layout Merger** → Combines wall boundaries + fixtures → Final merged layout

## 🎯 Enhanced Merchmix Integration

The pipeline now accepts **"prompt.txt + merchmix.json + image"** as input and generates:

- Enhanced layout images with fixture requirements
- JSON outputs with merchmix compliance validation
- Merged layouts combining wall boundaries and fixture placements
- DXF files for CAD integration

## 📈 Outputs

- **JSON**: Structured layout data with fixture positions
- **PNG**: Visual layout representations
- **DXF**: CAD-compatible files for design software
- **Compliance Reports**: Merchmix validation results