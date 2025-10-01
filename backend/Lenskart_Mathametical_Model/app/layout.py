#!/usr/bin/env python3
"""
JSON (meters) → DXF (millimeters) using ezdxf only.

Axes & transforms:
- Map JSON (x, z) → DXF (X, Y) for plan; JSON y is ignored.
- Height comes ONLY from `height` and is applied along DXF Z (up).
- Apply rotation (deg) from JSON about XY centroid.
- **Then flip horizontally across the vertical axis at centroid X** (left↔right).

What it does:
- Draws 2D wall centerlines on layer `WALLS` (XY plane)
- Creates one vertical rectangular 3DFACE per wall on layer `WALLS_3D` (Z = 0..height)
- Computes outer boundary corners in CCW order **after rotation+flip** and writes them to JSON

Usage:
  python walls_from_json_to_dxf.py /path/to/latest.json

Output:
  <json_stem>_walls_mm.dxf and <json_stem>_corners_ccw.json next to the input JSON
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

from typing import List, Tuple
from shapely.geometry import LinearRing, Polygon
from shapely.geometry.polygon import orient

import ezdxf
from ezdxf import units

# Types
Seg2D = Tuple[float, float, float, float]        # (x1, y1, x2, y2) mm
Wall3D = Tuple[float, float, float, float, float]  # (x1, y1, x2, y2, height_mm)
Pt = Tuple[float, float]

SNAP_MM = 1e-6  # quantization grid for node snapping during graph build


def load_json(path: Path) -> dict:
    with path.open("r") as f:
        return json.load(f)


def extract_walls_mm(data: dict) -> Tuple[List[Seg2D], List[Wall3D], float]:
    walls = (data.get("room_measurements") or {}).get("walls") or []
    rotation_deg = float(data.get("rotation", 0.0))

    plan: List[Seg2D] = []
    walls3d: List[Wall3D] = []

    for w in walls:
        sx, sy, sz = w.get("start", [0.0, 0.0, 0.0])
        ex, ey, ez = w.get("end", [0.0, 0.0, 0.0])
        h_m = float(w.get("height", 0.0))

        # Map JSON (x, z) -> DXF (X, Y). Ignore JSON Y.
        x1 = float(sx) * 1000.0
        y1 = float(sz) * 1000.0
        x2 = float(ex) * 1000.0
        y2 = float(ez) * 1000.0
        h_mm = h_m * 1000.0

        plan.append((x1, y1, x2, y2))
        walls3d.append((x1, y1, x2, y2, h_mm))

    return plan, walls3d, rotation_deg


def centroid_xy(plan_segments: List[Seg2D]) -> Tuple[float, float]:
    xs: List[float] = []
    ys: List[float] = []
    for x1, y1, x2, y2 in plan_segments:
        xs.extend([x1, x2])
        ys.extend([y1, y2])
    if not xs:
        return 0.0, 0.0
    return sum(xs) / len(xs), sum(ys) / len(ys)


def rotate_xy(x: float, y: float, cx: float, cy: float, theta_deg: float) -> Tuple[float, float]:
    th = math.radians(theta_deg)
    ct, st = math.cos(th), math.sin(th)
    dx, dy = x - cx, y - cy
    rx = dx * ct - dy * st + cx
    ry = dx * st + dy * ct + cy
    return rx, ry


def apply_rotation(plan_segments: List[Seg2D], walls3d: List[Wall3D], rot_deg: float) -> Tuple[List[Seg2D], List[Wall3D]]:
    if abs(rot_deg) < 1e-12:
        return list(plan_segments), list(walls3d)
    cx, cy = centroid_xy(plan_segments)

    plan_rot: List[Seg2D] = []
    for x1, y1, x2, y2 in plan_segments:
        rx1, ry1 = rotate_xy(x1, y1, cx, cy, rot_deg)
        rx2, ry2 = rotate_xy(x2, y2, cx, cy, rot_deg)
        plan_rot.append((rx1, ry1, rx2, ry2))

    walls_rot: List[Wall3D] = []
    for x1, y1, x2, y2, h in walls3d:
        rx1, ry1 = rotate_xy(x1, y1, cx, cy, rot_deg)
        rx2, ry2 = rotate_xy(x2, y2, cx, cy, rot_deg)
        walls_rot.append((rx1, ry1, rx2, ry2, h))

    return plan_rot, walls_rot


def flip_horizontal(plan_segments: List[Seg2D], walls3d: List[Wall3D]) -> Tuple[List[Seg2D], List[Wall3D]]:
    """Mirror across the vertical axis through centroid X (y-axis at center x)."""
    cx, cy = centroid_xy(plan_segments)
    plan_flipped: List[Seg2D] = []
    for x1, y1, x2, y2 in plan_segments:
        fx1 = 2 * cx - x1
        fx2 = 2 * cx - x2
        plan_flipped.append((fx1, y1, fx2, y2))

    walls_flipped: List[Wall3D] = []
    for x1, y1, x2, y2, h in walls3d:
        fx1 = 2 * cx - x1
        fx2 = 2 * cx - x2
        walls_flipped.append((fx1, y1, fx2, y2, h))

    return plan_flipped, walls_flipped


# ------------------ Outer Perimeter Corners ------------------
def unique_points_with_buffer(
    plan_segments: List[Seg2D],
    buffer_mm: float = 100.0,
    rounding: int = 3,
) -> Dict[Tuple[float, float], int]:
    """
    Group endpoints whose pairwise distance <= buffer_mm and count appearances.
    Returns { (centroid_x, centroid_y): count } with coordinates rounded to `rounding` decimals.
    """
    # Collect all endpoints
    pts: List[Tuple[float, float]] = []
    for x1, y1, x2, y2 in plan_segments:
        pts.append((float(x1), float(y1)))
        pts.append((float(x2), float(y2)))

    n = len(pts)
    if n == 0:
        return {}

    # Union-Find (Disjoint Set)
    parent = list(range(n))
    rank = [0] * n

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if rank[ra] < rank[rb]:
            parent[ra] = rb
        elif rank[ra] > rank[rb]:
            parent[rb] = ra
        else:
            parent[rb] = ra
            rank[ra] += 1

    # Cluster points within buffer
    thr2 = buffer_mm * buffer_mm
    for i in range(n):
        xi, yi = pts[i]
        for j in range(i + 1, n):
            xj, yj = pts[j]
            dx = xi - xj
            dy = yi - yj
            if dx * dx + dy * dy <= thr2:
                union(i, j)

    # Gather clusters
    clusters: Dict[int, List[int]] = {}
    for idx in range(n):
        r = find(idx)
        clusters.setdefault(r, []).append(idx)

    # Build result: centroid (rounded) -> count
    result: Dict[Tuple[float, float], int] = {}
    for indices in clusters.values():
        sx = sy = 0.0
        for k in indices:
            x, y = pts[k]
            sx += x
            sy += y
        cx = sx / len(indices)
        cy = sy / len(indices)
        key = (round(cx, rounding), round(cy, rounding))
        result[key] = len(indices)

    return result

def ring_order_from_points(
    plan_segments: List[Seg2D],
    corners: List[Pt],               # your list of points with count>=2 (clustered at 100mm)
    assign_thresh_mm: float = 100.0, # must match how you clustered
    prefer: str = "cw",              # "cw" or "ccw" walk
) -> List[Pt]:
    """
    Order 'corners' into a single perimeter ring using only the input segments.
    - We map each segment endpoint to its nearest corner (<= assign_thresh_mm).
    - Build a planar graph (adjacency) between corner nodes.
    - Sort neighbors by polar angle at each node.
    - Walk the outside using a right-hand (cw) or left-hand (ccw) rule,
      starting from the lowest, then leftmost corner.

    Returns a list of points in ring order (first==last not repeated).
    """
    if len(corners) < 3:
        return []

    # --- map each segment endpoint to the nearest corner (within threshold)
    C = [(float(x), float(y)) for x, y in corners]
    nC = len(C)
    thr2 = assign_thresh_mm * assign_thresh_mm

    def nearest_corner_id(x: float, y: float) -> int:
        best_i, best_d2 = -1, thr2
        for i, (cx, cy) in enumerate(C):
            dx, dy = x - cx, y - cy
            d2 = dx*dx + dy*dy
            if d2 <= best_d2:
                best_d2 = d2
                best_i = i
        return best_i  # -1 if nothing within threshold

    nbrs: Dict[int, set] = {i: set() for i in range(nC)}
    for x1, y1, x2, y2 in plan_segments:
        a = nearest_corner_id(x1, y1)
        b = nearest_corner_id(x2, y2)
        if a == -1 or b == -1 or a == b:
            continue
        nbrs[a].add(b)
        nbrs[b].add(a)

    # remove isolated/non-incident corners
    nbrs = {i: list(s) for i, s in nbrs.items() if s}
    if len(nbrs) < 3:
        return []

    # --- sort neighbors by absolute angle at each node
    ang: Dict[Tuple[int, int], float] = {}
    for v in nbrs:
        x0, y0 = C[v]
        nbrs[v].sort(key=lambda u: math.atan2(C[u][1] - y0, C[u][0] - x0))
        for u in nbrs[v]:
            ang[(v, u)] = math.atan2(C[u][1] - y0, C[u][0] - x0)

    # --- helper: pick next neighbor at node u given incoming angle θ_in
    def next_neighbor(u: int, theta_in: float, cw: bool) -> Tuple[int, float]:
        """Return (w, theta_out) where theta_out is angle of u->w."""
        a_list = [ang[(u, w)] for w in nbrs[u]]
        if cw:
            # take the neighbor with angle JUST BELOW theta_in (right-most turn); wrap if needed
            idx = None
            for i, a in enumerate(a_list):
                if a < theta_in:
                    idx = i
            if idx is None:
                idx = len(a_list) - 1
            w = nbrs[u][idx]
        else:
            # take the neighbor with angle JUST ABOVE theta_in (left-most turn); wrap if needed
            idx = None
            for i, a in enumerate(a_list):
                if a > theta_in:
                    idx = i
                    break
            if idx is None:
                idx = 0
            w = nbrs[u][idx]
        return w, ang[(u, w)]

    # --- start at the lowest, then leftmost corner
    start = min(nbrs.keys(), key=lambda i: (C[i][1], C[i][0]))
    cw = (prefer.lower() != "ccw")
    # incoming direction: pretend we arrived from a point to the LEFT of start
    theta_in = math.pi  # angle of vector (start -> virtual_prev = left)

    ring_ids: List[int] = []
    u = start
    safety = 0
    while True:
        ring_ids.append(u)
        w, theta_out = next_neighbor(u, theta_in, cw=cw)
        # next node and its incoming angle
        v = w
        theta_in = math.atan2(C[u][1] - C[v][1], C[u][0] - C[v][0])
        u = v
        safety += 1
        if u == start and len(ring_ids) > 1:
            break
        if safety > 10000:  # just in case
            return []

    # de-duplicate trailing start if present
    if len(ring_ids) >= 2 and ring_ids[0] == ring_ids[-1]:
        ring_ids.pop()

    return [C[i] for i in ring_ids]

def ring_from_points(points: List[Pt], orientation: str = "keep") -> LinearRing:
    """
    Build a Shapely LinearRing from perimeter-ordered points.
    orientation: "keep" | "ccw" | "cw"
    """
    if len(points) < 3:
        raise ValueError("Need at least 3 points")

    # Ensure closed (Shapely will close automatically, but this is explicit)
    closed = points if points[0] == points[-1] else points + [points[0]]

    ring = LinearRing(closed)
    if not ring.is_valid:
        raise ValueError("Ring is invalid (likely self-intersecting)")

    if orientation == "keep":
        return ring

    # Re-orient by wrapping in a Polygon and using orient()
    poly = Polygon(ring)
    if orientation.lower() == "ccw":
        poly = orient(poly, sign=+1.0)
    elif orientation.lower() == "cw":
        poly = orient(poly, sign=-1.0)
    else:
        raise ValueError("orientation must be 'keep', 'ccw', or 'cw'")

    return LinearRing(list(poly.exterior.coords))  # coords already closed

def remove_nearly_straight_vertices(
    ordered_pts: List[Pt],
    tol_deg: float = 2.0,
    min_edge_len: float = 1e-6,
    iterative: bool = True,
    keep_closed: bool = True,
) -> List[Pt]:
    """
    Remove vertices whose turn angle is ~0° (i.e., point lies almost on a straight run).

    Args:
        ordered_pts: perimeter-ordered points; may be closed (first==last) or open.
        tol_deg:   consider a vertex "nearly straight" if turn angle <= tol_deg.
        min_edge_len: ignore edges shorter than this (mm) when computing angles.
        iterative: repeatedly re-check after removals until stable (recommended).
        keep_closed: if input was closed, return a closed ring as well.

    Returns:
        Filtered list of points, same orientation as input.
    """
    if not ordered_pts:
        return []

    # normalize to open list; remember closure
    was_closed = len(ordered_pts) >= 2 and ordered_pts[0] == ordered_pts[-1]
    pts = ordered_pts[:-1] if was_closed else list(ordered_pts)

    if len(pts) < 3:
        return ordered_pts if was_closed and keep_closed else pts

    def unit(dx: float, dy: float):
        L = math.hypot(dx, dy)
        if L < min_edge_len:
            return (0.0, 0.0), 0.0
        return (dx / L, dy / L), L

    def angle_between(u, v) -> float:
        ux, uy = u; vx, vy = v
        dot = max(-1.0, min(1.0, ux * vx + uy * vy))
        return math.degrees(math.acos(dot))  # 0° = straight, 180° = U-turn

    def turns(pts_: List[Pt]) -> List[float]:
        n = len(pts_)
        angs = [0.0] * n
        for i in range(n):
            px, py = pts_[(i - 1) % n]
            cx, cy = pts_[i]
            nx, ny = pts_[(i + 1) % n]
            v1, L1 = unit(cx - px, cy - py)
            v2, L2 = unit(nx - cx, ny - cy)
            if L1 < min_edge_len or L2 < min_edge_len:
                angs[i] = 0.0  # treat degenerate as removable
            else:
                angs[i] = angle_between(v1, v2)
        return angs

    def one_pass(p: List[Pt]) -> List[Pt]:
        if len(p) < 3:
            return p
        angs = turns(p)
        keep = [angs[i] > tol_deg for i in range(len(p))]
        # ensure we don't drop below triangle
        if sum(keep) < 3:
            # keep the three "most corner-like" vertices
            idx_sorted = sorted(range(len(p)), key=lambda i: angs[i], reverse=True)
            keep = [False] * len(p)
            for i in idx_sorted[:3]:
                keep[i] = True
        return [pt for i, pt in enumerate(p) if keep[i]]

    if iterative:
        prev_len = None
        while prev_len != len(pts):
            prev_len = len(pts)
            pts = one_pass(pts)
            if len(pts) < 3:
                break
    else:
        pts = one_pass(pts)

    # re-close if requested and the input was closed
    if was_closed and keep_closed:
        if not pts or pts[0] != pts[-1]:
            pts = pts + [pts[0]]

    return pts


def main() -> None:
    ap = argparse.ArgumentParser(description="Convert JSON walls (meters) to DXF (mm) with rotation, horizontal flip, 3D faces (Z-up), and CCW corners.")
    ap.add_argument("json_path", help="Path to input JSON file")
    ap.add_argument("--no-flip", action="store_true", help="Disable the horizontal flip across centroid X.")
    args = ap.parse_args()

    json_file = Path(args.json_path)
    if not json_file.exists():
        raise SystemExit(f"JSON not found: {json_file}")

    data = load_json(json_file)
    plan_mm, walls3d_mm, rot_deg = extract_walls_mm(data)
    plan_rot, walls3d_rot = apply_rotation(plan_mm, walls3d_mm, rot_deg)
    if args.no_flip:
        plan_final, walls3d_final = plan_rot, walls3d_rot
    else:
        plan_final, walls3d_final = flip_horizontal(plan_rot, walls3d_rot)

    # corners in CCW from final plan (after rotation + optional flip)
    all_points = unique_points_with_buffer(plan_final)

    # out_path = json_file.with_name(json_file.stem + "_walls_mm.dxf")
    # write_dxf(plan_final, walls3d_final, out_path)

    # print(plan_final)
    for i in plan_final:
        print(i[0], i[1], i[2], i[3])
    print()
    for i in walls3d_final:
        print(i[0], i[1], i[2], i[3], i[4])
    print()
    corners = [pt for pt, cnt in all_points.items() if cnt > 1]

    ordered = ring_order_from_points(plan_final, corners, assign_thresh_mm=100.0, prefer="cw")
    cleaned_points = remove_nearly_straight_vertices(ordered, tol_deg=2.0)
    for p in cleaned_points:
        print(p[0], p[1])

if __name__ == "__main__":
    main()
