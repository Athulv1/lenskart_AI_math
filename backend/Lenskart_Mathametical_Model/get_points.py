import json
import sys
from collections import defaultdict, deque

MM = 1000.0
TOLERANCES_MM = [0.1, 0.25, 0.5, 1, 2, 3, 5, 7.5, 10]

def snap_pt_tol(pt, tol_mm):
    x, y = pt
    gx = round(x / tol_mm) * tol_mm
    gy = round(y / tol_mm) * tol_mm
    return (gx, gy)

def load_segments_mm(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)
    segs = []
    for wall in data["room_measurements"]["walls"]:
        s = wall["start"]
        e = wall["end"]
        segs.append(((s[0]*MM, s[2]*MM), (e[0]*MM, e[2]*MM)))
    return segs

def build_graph_snapped(segments, tol_mm):
    adj = defaultdict(set)
    edges = set()
    for (x1, y1), (x2, y2) in segments:
        a = snap_pt_tol((x1, y1), tol_mm)
        b = snap_pt_tol((x2, y2), tol_mm)
        if a == b:
            continue
        adj[a].add(b)
        adj[b].add(a)
        edges.add(tuple(sorted((a, b))))
    return adj, edges

def is_single_simple_cycle(adj, edges):
    verts = list(adj.keys())
    if not verts:
        return False, "no vertices"
    degrees = {v: len(adj[v]) for v in verts}
    if not all(deg == 2 for deg in degrees.values()):
        return False, f"degree_issue:{degrees}"
    seen = set()
    q = deque([verts[0]])
    while q:
        v = q.popleft()
        if v in seen:
            continue
        seen.add(v)
        for n in adj[v]:
            if n not in seen:
                q.append(n)
    if len(seen) != len(verts):
        return False, "not_connected"
    if len(edges) != len(verts):
        return False, f"V({len(verts)})!=E({len(edges)})"
    return True, "ok"

def walk_cycle(adj):
    start = min(adj.keys())
    ordered = [start]
    prev = None
    curr = start
    while True:
        neigh = adj[curr]
        nxt = next(n for n in neigh if n != prev)
        if nxt == start:
            if len(ordered) == len(adj):
                break
            raise RuntimeError("Closed early; multiple cycles?")
        ordered.append(nxt)
        prev, curr = curr, nxt
    return ordered

def signed_area(poly):
    s = 0.0
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + [poly[0]]):
        s += x1*y2 - x2*y1
    return 0.5 * s

def extract_polygon_points(json_path, ensure_ccw=True):
    segments = load_segments_mm(json_path)
    target_count = len(segments)
    best = None
    for tol in TOLERANCES_MM:
        adj, edges = build_graph_snapped(segments, tol)
        ok, status = is_single_simple_cycle(adj, edges)
        if ok:
            ordered = walk_cycle(adj)
            if ensure_ccw and signed_area(ordered) < 0:
                ordered.reverse()
            return {
                "ok": True,
                "tolerance_mm": tol,
                "unique_points_count": len(adj),
                "target_walls": target_count,
                "ordered_points_mm": ordered,
            }
        v, e = len(adj), len(edges)
        score = abs(v - e)
        if best is None or score < best[3] or (score == best[3] and tol > best[0]):
            best = (tol, adj, edges, score, status)
    tol, adj, edges, score, status = best
    degrees = {v: len(adj[v]) for v in adj}
    return {
        "ok": False,
        "tolerance_mm": tol,
        "unique_points_count": len(adj),
        "target_walls": target_count,
        "reason": f"Could not form a single simple polygon. status={status}",
        "degree_histogram": {d: [v for v, deg in degrees.items() if deg == d] for d in set(degrees.values())},
    }

import math
from typing import Iterable, Tuple, List

def rotate_points_about_center(points: Iterable[Tuple[float, float]],
                               angle_deg: float) -> List[Tuple[float, float]]:
    """
    Rotate 2D points by angle_deg (counter-clockwise) about their centroid.

    Args:
        points: Iterable of (x, y) points (e.g., [(x1, y1), (x2, y2), ...]).
        angle_deg: Rotation angle in degrees (positive = CCW).

    Returns:
        List of (x, y) points rotated by angle_deg about the center.
    """
    pts = [(float(x), float(y)) for x, y in points]
    if not pts:
        return []

    # 1) Compute centroid (arithmetic mean of x's and y's)
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)

    # 2) Convert angle to radians
    theta = math.radians(angle_deg)
    ct = math.cos(theta)
    st = math.sin(theta)

    # 3) Rotate each point about the centroid
    rotated: List[Tuple[float, float]] = []
    for x, y in pts:
        dx = x - cx
        dy = y - cy
        rx = dx * ct - dy * st
        ry = dx * st + dy * ct
        rotated.append((rx + cx, ry + cy))

    return rotated


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_points.py <path_to_json>")
        sys.exit(1)
    json_file = sys.argv[1]
    result = extract_polygon_points(json_file, ensure_ccw=True)
    if result["ok"]:
        # print(f"✅ Formed single loop at tolerance {result['tolerance_mm']} mm")
        # print(f"Unique points: {result['unique_points_count']} (target walls: {result['target_walls']})")
        # print("\nOrdered polygon vertices (mm):")
        # for p in result["ordered_points_mm"]:
        #     print(p)
        # print(result["ordered_points_mm"])
        with open(json_file, 'r') as file:
            data = json.load(file)
        rotation = data["rotation"]

        points = rotate_points_about_center(result["ordered_points_mm"], rotation)
        # points = result["ordered_points_mm"]
        for p in points:
            print(p)
    else:
        print(f"⚠️ Failed to form a single loop at best tolerance {result['tolerance_mm']} mm")
        print(f"Unique points: {result['unique_points_count']} (target walls: {result['target_walls']})")
        print(f"Reason: {result['reason']}")
        print("Degree breakdown:")
        for deg, verts in sorted(result["degree_histogram"].items()):
            print(f"  Degree {deg}: {len(verts)} vertices")
