import subprocess
import sys
import os
import logging
import traceback
from typing import List, Dict, Any, Optional, Tuple
import Fixture
import CV_Controller as cvCon
from typing import List, Tuple
import ezdxf
from ezdxf import units
from ezdxf.enums import InsertUnits
from ezdxf.math import Vec2, Vec3, Matrix44, BoundingBox2d
from ezdxf.addons import Importer
from ezdxf.colors import rgb2int
import math
from shapely.geometry import Point, Polygon, LinearRing, LineString, box
from shapely.ops import linemerge, polygonize, unary_union
import shapely.affinity as affinity
import collections

logger = logging.getLogger("app")

class DXF_Controller:

    Point = Tuple[float, float]
    Segment = Tuple[Point, Point]
    fixture_dict = {
        # Wall Fixtures
        "jj_fixture_different_large": {
            "name": "jj_fixture_different_large",
            "path": "assets/wall_fixtures/jj_fixture_different_large.dxf",
            "type": "wall"
        },
        "jj_fixture_different_medium": {
            "name": "jj_fixture_different_medium",
            "path": "assets/wall_fixtures/jj_fixture_different_medium.dxf",
            "type": "wall"
        },
        "jj_fixture_large": {
            "name": "jj_fixture_large",
            "path": "assets/wall_fixtures/jj_fixture_large.dxf",
            "type": "wall"
        },
        "jj_fixture_medium": {
            "name": "jj_fixture_medium",
            "path": "assets/wall_fixtures/jj_fixture_medium.dxf",
            "type": "wall"
        },
        "jj_super_hybrid_large": {
            "name": "jj_super_hybrid_large",
            "path": "assets/wall_fixtures/jj_super_hybrid_large.dxf",
            "type": "wall"
        },
        "jj_super_hybrid_medium": {
            "name": "jj_super_hybrid_medium",
            "path": "assets/wall_fixtures/jj_super_hybrid_medium.dxf",
            "type": "wall"
        },
        "jj_super_hybrid_small": {
            "name": "jj_super_hybrid_small", 
            "path": "assets/wall_fixtures/jj_super_hybrid_small.dxf",
            "type": "wall"
        },
        "mirror_different": {
            "name": "mirror_different",
            "path": "assets/wall_fixtures/mirror_different.dxf",
            "type": "wall"
        },
        "mirror": {
            "name": "mirror",
            "path": "assets/wall_fixtures/mirror.dxf",
            "type": "wall"
        },
        "pick_up_counter": {
            "name": "pick_up_counter",
            "path": "assets/wall_fixtures/pick_up_counter.dxf",
            "type": "wall"
        },
        "vc_fixture_large": {
            "name": "vc_fixture_large",
            "path": "assets/wall_fixtures/vc_fixture_large.dxf",
            "type": "wall"
        },
        "vc_fixture_medium": {
            "name": "vc_fixture_medium",
            "path": "assets/wall_fixtures/vc_fixture_medium.dxf",
            "type": "wall"
        },
        "window_1_section": {
            "name": "window_1_section",
            "path": "assets/wall_fixtures/window_1_section.dxf",
            "type": "wall"
        },
        "window_3_section": {
            "name": "window_3_section",
            "path": "assets/wall_fixtures/window_3_section.dxf",
            "type": "wall"
        },
        "with_screen": {
            "name": "with_screen",
            "path": "assets/wall_fixtures/with_screen.dxf",
            "type": "wall"
        },
        

        # Floor Fixtures
        "AR": {
            "name": "AR",
            "path": "assets/floor/AR.dxf",
            "type": "floor"
        },
        "Blue_zero": {
            "name": "Blue_zero",
            "path": "assets/floor/Blue_zero.dxf",
            "type": "floor"
        },
        "Discussion_table_large": {
            "name": "Discussion_table_large",
            "path": "assets/floor/Discussion_table_large.dxf",
            "type": "floor"
        },
        "Discussion_table_medium": {
            "name": "Discussion_table_medium",
            "path": "assets/floor/Discussion_table_medium.dxf",
            "type": "floor"
        },
        "Discussion_table_small": {
            "name": "Discussion_table_small",
            "path": "assets/floor/Discussion_table_small.dxf",
            "type": "floor"
        },
        "drop_box": {
            "name": "drop_box",
            "path": "assets/floor/drop_box.dxf",
            "type": "floor"
        },
        "Euro_centre": {
            "name": "Euro_centre",
            "path": "assets/floor/Euro_centre.dxf",
            "type": "floor"
        },
        "Lensbar": {
            "name": "Lensbar",
            "path": "assets/floor/Lensbar.dxf",
            "type": "floor"
        },
        "Lensometer_large": {
            "name": "Lensometer_large",
            "path": "assets/floor/Lensometer_large.dxf",
            "type": "floor"
        },
        "Lensometer_medium": {
            "name": "Lensometer_medium",
            "path": "assets/floor/Lensometer_medium.dxf",
            "type": "floor"
        },
        "Lensometer_small": {
            "name": "Lensometer_small",
            "path": "assets/floor/Lensometer_small.dxf",
            "type": "floor"
        },
        "QMS_desk": {
            "name": "QMS_desk",
            "path": "assets/floor/QMS_desk.dxf",
            "type": "floor"
        },
        "sofa": {
            "name": "sofa",
            "path": "assets/floor/sofa.dxf",
            "type": "floor"
        },
        "Standing_table": {
            "name": "Standing_table",
            "path": "assets/floor/Standing_table.dxf",
            "type": "floor"
        },

        # Back Office Furniture
        "Dining_Table_large": {
            "name": "Dining_Table_large",
            "path": "assets/boh_furniture/Dining_Table_large.dxf",
            "type": "boh"
        },
        "Dining_Table_medium": {
            "name": "Dining_Table_medium",
            "path": "assets/boh_furniture/Dining_Table_medium.dxf",
            "type": "boh"
        },
        "pickup_storage_900": {
            "name": "pickup_storage_900",
            "path": "assets/boh_furniture/pickup_storage_900.dxf",
            "type": "boh"
        },
        "pickup_storage_1200": {
            "name": "pickup_storage_1200",
            "path": "assets/boh_furniture/pickup_storage_1200.dxf",
            "type": "boh"
        },
        "pickup_table": {
            "name": "pickup_table",
            "path": "assets/boh_furniture/pickup_table.dxf",
            "type": "boh"
        },
        "QC_table_large": {
            "name": "QC_table_large",
            "path": "assets/boh_furniture/QC_table_large.dxf",
            "type": "boh"
        },
        "QC_table_medium": {
            "name": "QC_table_medium",
            "path": "assets/boh_furniture/QC_table_medium.dxf",
            "type": "boh"
        },
        "Repair_Table_large": {
            "name": "Repair_Table_large",
            "path": "assets/boh_furniture/Repair_Table_large.dxf",
            "type": "boh"
        },
        "Repair_Table_medium": {
            "name": "Repair_Table_medium",
            "path": "assets/boh_furniture/Repair_Table_medium.dxf",
            "type": "boh"
        },
        "staff_rack": {
            "name": "staff_rack",
            "path": "assets/boh_furniture/staff_rack.dxf",
            "type": "boh"
        },
        "storage_rack": {
            "name": "storage_rack",
            "path": "assets/boh_furniture/storage_rack.dxf",
            "type": "boh"
        },
        "ups_rack": {
            "name": "ups_rack",
            "path": "assets/boh_furniture/ups_rack.dxf",
            "type": "boh"
        },
        "water_dispenser": {
            "name": "water_dispenser",
            "path": "assets/boh_furniture/water_dispenser.dxf",
            "type": "boh"
        },

        # Television Fixtures
        "screen_43": {
            "name": 'screen_43',
            "path": "assets/screen/screen_43.dxf",
            "type": "screen"
        },
        "screen_49": {
            "name": 'screen_49',
            "path": "assets/screen/screen_49.dxf",
            "type": "screen"
        },
        "screen_55": {
            "name": 'screen_55',
            "path": "assets/screen/screen_55.dxf",
            "type": "screen"
        },
        "screen_65": {
            "name": 'screen_65',
            "path": "assets/screen/screen_65.dxf",
            "type": "screen"
        },
    
        # Clinic Fixtures
        "Clinic_with_sink": {
            "name": "Clinic_with_sink",
            "path": "assets/clinic/Clinic_with_sink.dxf",
            "type": "clinic"
        },
         "Clinic_regular": {
            "name": "Clinic_regular",
            "path": "assets/clinic/Clinic_regular.dxf",
            "type": "clinic"
        },
         "ROC_clinic": {
            "name": "ROC_clinic",
            "path": "assets/clinic/ROC_clinic.dxf",
            "type": "clinic"
        },

        # POS Fixtures
        "pos_with_screen_large": {
            "name": "pos_with_screen_large",
            "path": "assets/pos/pos_with_screen_large.dxf",
            "type": "pos"
        },
        "pos_with_screen_medium": {
            "name": "pos_with_screen_medium",
            "path": "assets/pos/pos_with_screen_medium.dxf",
            "type": "pos"
        },
        "pos_with_screen_small": {
            "name": "pos_with_screen_small",
            "path": "assets/pos/pos_with_screen_small.dxf",
            "type": "pos"
        },
        "pos_without_screen": {
            "name": "pos_without_screen",
            "path": "assets/pos/pos_without_screen.dxf",
            "type": "pos"
        },

        # Loose Furniture
        "Corian_table" : {
            "name": "Corian_table",
            "path": "assets/loose/Corian_table.dxf",
            "type": "loose"
        },
        "Eye_massage_area" : {
            "name": "Eye_massage_area",
            "path": "assets/loose/Eye_massage_area.dxf",
            "type": "loose"
        },
        "Eye_massage_chair" : {
            "name": "Eye_massage_chair",
            "path": "assets/loose/Eye_massage_chair.dxf",
            "type": "loose"
        },
        "large_bench" : {
            "name": "large_bench",
            "path": "assets/loose/large_bench.dxf",
            "type": "loose"
        },
        "Lounge_seat" : {
            "name": "Lounge_seat",
            "path": "assets/loose/Lounge_seat.dxf",
            "type": "loose"
        },
        "medium_bench" : {
            "name": "medium_bench",
            "path": "assets/loose/medium_bench.dxf",
            "type": "loose"
        },
        "pouf" : {
            "name": "pouf",
            "path": "assets/loose/pouf.dxf",
            "type": "loose"
        },
        "Sofa_large" : {
            "name": "Sofa_large",
            "path": "assets/loose/Sofa_large.dxf",
            "type": "loose"
        },
        "Sofa_medium" : {
            "name": "Sofa_medium",
            "path": "assets/loose/Sofa_medium.dxf",
            "type": "loose"
        },
        "stool" : {
            "name": "stool",
            "path": "assets/loose/stool.dxf",
            "type": "loose"
        },

        # toilet
        "toilet" : {
            "name": "toilet",
            "path": "assets/toilet/toilet.dxf",
            "type": "toilet"
        }
    }

    def __init__(self, img_path, dxf_out, overlay, fp_json, fixtures):
        self.image_path = img_path
        self.dxf_out = dxf_out
        self.ovl_path = overlay
        self.fp_json = fp_json
        self.cvc = cvCon.CV_Controller(img_path, dxf_out, overlay, fp_json)
        self.doc = ezdxf.new(dxfversion='R2018', units=units.MM)
        # self.doc = ezdxf.new(dxfversion='R2010', units=units.MM)
        # self.doc.header['$ACADVER'] = 'AC1024'  # R2010
        # self.doc.header['$INSUNITS'] = 4       # mm
        self.msp = self.doc.modelspace()
        self.fixtures = fixtures
        self.sofa_placed = False  # Add this flag
        self.fixture_counter = {}
        self.safe_types = {
            "LINE", "LWPOLYLINE", "CIRCLE", "ARC", "TEXT", "MTEXT",
            "ELLIPSE", "SPLINE", "SOLID", "INSERT", "ATTDEF"
        }

    def points_to_polygon(self, points):
        if len(points) < 3:
            raise ValueError("A polygon requires at least 3 points")

        # Ensure closure (Shapely will auto-close, but this avoids ambiguity)
        if points[0] != points[-1]:
            points = points + [points[0]]

        return Polygon(points)

    def offset_polygon_with_bottom_gap(self, points, offset=200.0, slope_tol=1e-3, y_tol=1.0, miter_limit=10.0, bottom_epsilon=0.0):
        """
        Always treats `points` as the inner loop.
        Forces points to CCW winding before offsetting outward.
        """

        # --- local helpers ---
        def polygon_area(pts):
            a = 0.0
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                a += x1 * y2 - x2 * y1
            return 0.5 * a

        def normalize(vx, vy):
            l = math.hypot(vx, vy)
            return (vx / l, vy / l) if l else (0.0, 0.0)

        def rotate90_ccw(vx, vy):
            return (-vy, vx)

        def rotate90_cw(vx, vy):
            return (vy, -vx)

        def line_intersection(p, r, q, s, eps=1e-9):
            px, py = p; rx, ry = r
            qx, qy = q; sx, sy = s
            denom = rx * sy - ry * sx
            if abs(denom) < eps:
                return ((px + qx) * 0.5, (py + qy) * 0.5)
            t = ((qx - px) * sy - (qy - py) * sx) / denom
            return (px + t * rx, py + t * ry)

        def find_bottom_chain(pts, slope_tol=1e-3, y_tol=1.0):
            n = len(pts)
            ys = [p[1] for p in pts]
            min_y = min(ys)
            is_bottom = [False] * n
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                dy = y2 - y1
                dx = x2 - x1
                near_min = (abs(y1 - min_y) <= y_tol) and (abs(y2 - min_y) <= y_tol)
                slope_ok = abs(dy) <= slope_tol * max(1.0, abs(dx))
                if near_min and slope_ok:
                    is_bottom[i] = True
            return is_bottom

        n = len(points)
        if n < 3:
            raise ValueError("Need at least 3 points.")

        # --- Ensure CCW ---
        pts = points[:]
        if polygon_area(pts) < 0:  # CW, reverse to CCW
            pts.reverse()

        # --- Edge directions and outward normals ---
        dirs = []
        norms = []
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            ux, uy = normalize(x2 - x1, y2 - y1)
            nx, ny = rotate90_cw(ux, uy)  # CCW polygon => outward is CW normal
            dirs.append((ux, uy))
            norms.append((nx, ny))

        # --- Offsets ---
        bottom_edges = find_bottom_chain(pts, slope_tol=slope_tol, y_tol=y_tol)
        edge_offsets = [bottom_epsilon if bottom_edges[i] else offset for i in range(n)]

        # --- Build outer polygon ---
        out_pts = []
        for i in range(n):
            i_prev = (i - 1) % n
            i_next = i

            P = pts[i]
            dir_prev = dirs[i_prev]
            dir_next = dirs[i_next]
            n_prev = norms[i_prev]
            n_next = norms[i_next]
            d_prev = edge_offsets[i_prev]
            d_next = edge_offsets[i_next]

            # Miter clamp
            dot = max(-1.0, min(1.0, dir_prev[0] * dir_next[0] + dir_prev[1] * dir_next[1]))
            angle = math.acos(dot) if abs(dot) < 1 else (0.0 if dot > 0 else math.pi)
            sin_half = math.sin(max(1e-6, angle * 0.5))
            miter_factor = 1.0 / sin_half
            if miter_factor > miter_limit and max(d_prev, d_next) > 0:
                scale = miter_limit / miter_factor
                d_prev *= scale
                d_next *= scale

            P_prev_shift = (P[0] + n_prev[0] * d_prev, P[1] + n_prev[1] * d_prev)
            P_next_shift = (P[0] + n_next[0] * d_next, P[1] + n_next[1] * d_next)

            vtx = line_intersection(P_prev_shift, dir_prev, P_next_shift, dir_next)
            out_pts.append(vtx)

        return out_pts

    Seg2D = Tuple[float, float, float, float]        # (x1, y1, x2, y2) mm
    Wall3D = Tuple[float, float, float, float, float]  # (x1, y1, x2, y2, height_mm)
    def write_dxf(self, plan_segments: List[Seg2D], walls3d: List[Wall3D]):

        if "WALLS" not in self.doc.layers:
            self.doc.layers.add("WALLS")
        if "WALLS_3D" not in self.doc.layers:
            self.doc.layers.add("WALLS_3D")

        # 2D centerlines in the XY plane
        for (x1, y1, x2, y2) in plan_segments:
            self.msp.add_line((x1, y1, 0.0), (x2, y2, 0.0), dxfattribs={"layer": "WALLS"})

        for (x1, y1, x2, y2, h) in walls3d:
            p1 = (x1, y1, 0.0)
            p2 = (x2, y2, 0.0)
            p3 = (x2, y2, h)
            p4 = (x1, y1, h)
            self.msp.add_3dface(
                [p1, p2, p3, p4],
                dxfattribs={"layer": "WALLS_3D"},
            )

    def create_floorplan(self):
        
        def add_lwpolyline(msp, pts, layer, color=None, lineweight=50):
            """
            Adds a closed LWPOLYLINE.
            - pts: list[(x, y)]
            - color: either an ACI index (0–256) or an rgb2int() int
            """
            pl = msp.add_lwpolyline(pts, format="xy", close=True, dxfattribs={
                "layer": layer,
                "lineweight": lineweight,
            })

            # Handle color type
            if isinstance(color, int) and color > 256:
                # Likely a rgb2int() value
                pl.dxf.true_color = color
            else:
                # Treat as ACI index
                pl.dxf.color = color

            return pl
    
        def add_loop_as_edges(edge_path, points):
            for i in range(len(points)):
                start, end = points[i], points[(i + 1) % len(points)]
                edge_path.add_line(start, end)
        
        self.corners = self.cvc.corners
        self.vectors = [Vec3(x, y, 0) for (x, y) in self.corners]

        inner = self.corners
        outer = self.offset_polygon_with_bottom_gap(self.corners, offset=200, slope_tol=0.05, y_tol=100, bottom_epsilon=5)

        # print(f"corners: {self.corners}\n")
        # print(f"inner: {inner}\n")
        # print(f"outer: {outer}\n")
        
        hatch_layer="LENS_HATCH_WALL"
        hatch = self.msp.add_hatch()
        hatch.dxf.solid_fill = 0
        hatch.dxf.layer = hatch_layer
        hatch.dxf.color = 250  # ACI: light gray
        hatch.dxf.true_color = rgb2int((120, 120, 120))  # Optional: matching RGB gray

        outer_path = hatch.paths.add_edge_path()
        add_loop_as_edges(outer_path, outer)

        inner_path = hatch.paths.add_edge_path()
        add_loop_as_edges(inner_path, inner)

        hatch.set_pattern_fill('ANSI32', scale=10)
        hatch.dxf.pattern_angle = 90

        self.write_dxf(self.cvc.plan_final, self.cvc.walls3d_final)
        add_lwpolyline(self.msp, outer, layer="LENS_WALL_OUTLINE", color=rgb2int((255, 255, 255)), lineweight=10)

        self.floorplan_polygon = self.points_to_polygon(self.corners)

    def place_fixture(self, fxtr: Fixture, insert_point: tuple, rotation: float, rotated: bool , xscale: float = 1.0, yscale: float = 1.0):
        """
        Imports a fixture as a block, correctly aligning its geometry to the insertion point.
        This is the single, unified function for all fixture placements.
        It leverages the `base_point` property to align the fixture's visual corner (fxtr.extmin)
        with the desired `insert_point`.
        """
        try:
            # Read the fixture's source DXF file
            src_doc = ezdxf.readfile(fxtr.path)
        except IOError:
            print(f"⚠️ ERROR: Cannot read fixture file: {fxtr.path}")
            return
            
        # Importer helps manage layers, styles, etc. between the two files
        importer = Importer(src_doc, self.doc)

        # Increment a counter for each fixture type to ensure unique block names
        if fxtr.name not in self.fixture_counter:
            self.fixture_counter[fxtr.name] = 1
        else:
            self.fixture_counter[fxtr.name] += 1

        # Create a clean, safe block name (e.g., "CLINIC_REGULAR_1")
        safe_block_name = f"{fxtr.name.upper().replace(' ', '_')}_{self.fixture_counter[fxtr.name]}"

        # --- THIS IS THE KEY TO THE UNIFIED SOLUTION ---
        # Create a new block definition in the main DXF document.
        # The 'base_point' argument is crucial. It redefines the block's handle.
        # We are telling ezdxf: "Treat the fixture's visual bottom-left corner as its origin."
        block = self.doc.blocks.new(
            name=safe_block_name,
            base_point=fxtr.extmin
        )

        # --- Search for geometry in both modelspace and blocks ---
        # This ensures that even if the fixture is defined entirely within a block
        # in its source file, we still copy its geometry correctly.
        source_entities = list(src_doc.modelspace())
        if not source_entities:
            for b in src_doc.blocks:
                if not b.name.startswith('*'):
                    source_entities.extend(list(b))
        
        # Copy all entities from the fixture's file into the new block definition.
        for entity in source_entities:
            try:
                block.add_entity(entity.copy())
            except ezdxf.DXFStructureError:
                # This can happen if an entity is invalid; we can safely skip it.
                print(f"  -> Skipping an invalid entity in {fxtr.name}")
                continue

        # Import necessary table entries (layers, linetypes, text styles)
        importer.import_tables()
        # Import any block definitions that might be nested inside the fixture
        importer.import_blocks(src_doc.blocks.block_names())
        
        # This places a reference to our newly defined block into the main drawing.
        # Because we set the 'base_point', ezdxf ensures that the point we designated
        # as the handle aligns perfectly with the specified `insert_point`.
        # self.msp.add_blockref(
        #     safe_block_name, 
        #     insert_point, 
        #     dxfattribs={"rotation": rotation}
        # )

        # --- MODIFIED: Add xscale and yscale to the placement ---
        self.msp.add_blockref(
            safe_block_name, 
            insert_point, 
            dxfattribs={
                "rotation": rotation,
                "xscale": xscale,
                "yscale": yscale
            }
        )
        # --- End of Modification ---

        print(f"✅ Placed '{fxtr.name}' as '{safe_block_name}' at ({insert_point[0]:.0f}, {insert_point[1]:.0f})")
        
            
    def place_clinic(self, placed_bboxes: List[tuple], mirror_rules: List[str] = ['right', 'bottom']):
        """
        Orchestrates the mandatory placement of clinic fixtures using a multi-strategy approach.
        NOW CORRECTLY USES the master placed_bboxes list.
        """
        from Fixture import Fixture

        print("\n--- [DEBUG] Starting Clinic Placement ---")
        clinic_config = self.fixtures.get("clinic_fixtures", {})
        if not any(clinic_config.values()):
            print("INFO: No clinic fixtures specified.")
            return

        clinics_to_place = []
        for clinic_type, count in clinic_config.items():
            if count > 0:
                try:
                    fxtr = Fixture(self.fixture_dict[clinic_type]["name"], self.fixture_dict[clinic_type]["path"])
                    clinics_to_place.extend([fxtr] * count)
                except (KeyError, ValueError) as e:
                    print(f"WARNING: Clinic type '{clinic_type}' not found or invalid. Skipping. Error: {e}")

        if not clinics_to_place:
            return

        # --- EXECUTE PLACEMENT STRATEGIES ---
        # remaining_clinics = self.place_clinics_by_perimeter_walk(
        #     clinics_to_place,
        #     placed_bboxes,  # Uses the passed-in list
        #     mirror_rules=mirror_rules
        # )

        remaining_clinics = self.place_clinics_along_top_wall(clinics_to_place, placed_bboxes)

        if not remaining_clinics:
            print("✅ All clinics placed successfully using the perimeter walk strategy.")
            return

        clinics_after_s2 = self.place_clinics_along_top_wall(remaining_clinics, placed_bboxes) # Uses the passed-in list

        if not clinics_after_s2:
            print("✅ All remaining clinics placed successfully along the top wall.")
            return

        # --- STRATEGY 3: Brute-force placement for any clinics that are still left ---
        print(f"\n[DEBUG] --> FALLBACK STRATEGY: {len(clinics_after_s2)} clinics remain. Starting Forced Grid Search...")
        unplaced_count = 0
        for clinic in clinics_after_s2:
            if not self._force_place_clinic(clinic, placed_bboxes): # Uses the passed-in list
                print(f"🔥 CRITICAL FAILURE: Could not force-place '{clinic.name}'.")
                unplaced_count += 1

        if unplaced_count == 0:
            print("✅ All remaining clinics placed successfully via forced grid search.")
        else:
            print(f"⚠️ {unplaced_count} clinics could not be placed even with brute-force search.")
    

    def place_clinics_along_top_wall(self, clinics_to_place, placed_bboxes):
        """
        A dedicated strategy function to place clinics by "walking" along the top
        wall of the floorplan from left to right. It is intended as the second
        strategy in a placement sequence.

        This modified version will place a second row if the first one fills up,
        and flip the fixtures in the second row by 180 degrees.
        """
        import collections
        from shapely.geometry import Point

        print("\n[DEBUG] --> STRATEGY 2: Executing 'Top Wall Walk'...")

        clinics_queue = collections.deque(clinics_to_place)
        if not clinics_queue:
            return []

        # 1. Get the geometric details of the top wall.
        top_wall = self._get_wall_details('top')
        if not top_wall:
            print("    -> FAILED: Could not identify a 'top wall' for this strategy.")
            return list(clinics_queue)

        segment_start = top_wall["start_point"]
        segment_vector = top_wall["vector"].normalize()
        segment_length = top_wall["length"]

        # 2. Determine the "inward" direction, away from the wall, into the floorplan.
        inward_normal = segment_vector.orthogonal()
        test_point = segment_start + inward_normal
        if not self.floorplan_polygon.contains(Point(test_point.x, test_point.y)):
            inward_normal = -inward_normal

        # 3. Walk along the wall segment and attempt to place each clinic.
        cursor = 50.0  # Start with a margin from the top-left corner of the wall.
        margin_from_wall = 50.0
        gap_between_clinics = 100.0
        
        # --- Variables for handling a second row ---
        row_count = 1
        # You have set the gap between the first and second row to 1000.0 mm.
        row_gap = 1000.0 
        max_fixture_depth_in_row = 0

        while clinics_queue:
            next_clinic = clinics_queue[0]
            fixture_depth = next_clinic.height # Clinic's depth against the wall
            fixture_length = next_clinic.width  # Clinic's length along the wall

            if fixture_depth > max_fixture_depth_in_row:
                max_fixture_depth_in_row = fixture_depth

            if cursor + fixture_length > segment_length - 50.0:
                print(f"    -> Ran out of space on the top wall for row {row_count}.")
                
                if row_count == 1:
                    row_count = 2
                    print("    -> Starting second row...")
                    cursor = 50.0
                    margin_from_wall += max_fixture_depth_in_row + row_gap
                    max_fixture_depth_in_row = 0
                    continue
                else:
                    break

            center_on_wall = segment_start + segment_vector * (cursor + fixture_length / 2)
            center_offset = inward_normal * (margin_from_wall + fixture_depth / 2)
            target_center = center_on_wall + center_offset

            # --- NEW: Conditional Rotation Logic ---
            # The fixture's base rotation should be parallel to the wall segment.
            rotation_for_this_clinic = top_wall["angle_deg"]

            # If we are placing the second row, add 180 degrees to flip the fixture.
            if row_count == 2:
                rotation_for_this_clinic += 180

            # Use the robust helper function with the potentially modified rotation.
            if self._validate_and_place_at_point(next_clinic, target_center, rotation_for_this_clinic, placed_bboxes):
                print(f"    -> Placed '{next_clinic.name}' along the top wall in row {row_count}.")
                clinics_queue.popleft()
                cursor += fixture_length + gap_between_clinics
            else:
                cursor += 100.0

        return list(clinics_queue)

    # This helper function places clinics in neat rows
    def _place_clinics_in_zone(self, clinics_to_place: list, placed_bboxes: list, zone: str):
        """
        Helper to place a list of clinics in organized rows within a specified zone.
        """
        from shapely.geometry import box

        margin = 100.0
        horizontal_gap = 50.0
        vertical_gap = 1000.0
        # DEBUG: Show parameters for this zone
        print(f"[DEBUG] Entering _place_clinics_in_zone for zone: '{zone}'")

        # Find specific corner points for more accurate anchoring
        left_wall_points = [p for p in self.cvc.corners if abs(p[0] - self.cvc.min_x) < 1.0]

        if not left_wall_points:
            leftmost_top_y = self.cvc.max_y
            leftmost_bottom_y = self.cvc.min_y
        else:
            leftmost_top_y = max(p[1] for p in left_wall_points)
            leftmost_bottom_y = min(p[1] for p in left_wall_points)
        
        # DEBUG: Show the calculated boundaries for placement
        print(f"[DEBUG] Zone Anchors: Top Y: {leftmost_top_y:.0f}, Bottom Y: {leftmost_bottom_y:.0f}")

        if zone == "top_left":
            start_y = leftmost_top_y - margin
            y_direction = -1
        else:  # bottom_left
            start_y = leftmost_bottom_y + margin
            y_direction = 1

        current_x_in_row = self.cvc.min_x + margin
        current_y = start_y
        max_dim_in_row = 0
        
        unplaced_clinics = []
        
        for i, fxtr in enumerate(clinics_to_place):
            # DEBUG: Announce which fixture is being attempted
            print(f"\n[DEBUG] Attempting to place '{fxtr.name}' (Number {i+1} in queue)...")
            # DEBUG: Show the current placement cursor position
            print(f"[DEBUG]   Cursor position: current_x={current_x_in_row:.0f}, current_y={current_y:.0f}")

            if current_x_in_row + fxtr.width > self.cvc.max_x - margin:
                # DEBUG: Announce starting a new row
                print(f"[DEBUG]   Not enough horizontal space. Starting new row.")
                current_y += (max_dim_in_row + vertical_gap) * y_direction
                current_x_in_row = self.cvc.min_x + margin
                max_dim_in_row = 0
                print(f"[DEBUG]   New row cursor: current_x={current_x_in_row:.0f}, current_y={current_y:.0f}")


            # Calculate the candidate bounding box
            y1 = current_y - fxtr.height if y_direction == -1 else current_y
            x1 = current_x_in_row
            x2, y2 = x1 + fxtr.width, y1 + fxtr.height
            candidate_poly = box(x1, y1, x2, y2)
            # DEBUG: Show the proposed coordinates for the fixture
            print(f"[DEBUG]   Candidate BBox: (x1={x1:.0f}, y1={y1:.0f}), (x2={x2:.0f}, y2={y2:.0f})")

            is_overlapping = any(candidate_poly.intersects(box(*b)) for b in placed_bboxes)
            is_inside = self.floorplan_polygon.contains(candidate_poly)
            # DEBUG: Show the results of the validation checks
            print(f"[DEBUG]   Validation: Is Inside Floorplan? {is_inside}, Is Overlapping? {is_overlapping}")

            if is_inside and not is_overlapping:
                self.place_fixture(fxtr, (x1, y1, 0), 0, False)
                placed_bboxes.append((x1, y1, x2, y2))
                print(f"[DEBUG]   ✅ SUCCESS: Placed '{fxtr.name}' in {zone} zone.")
                max_dim_in_row = max(max_dim_in_row, fxtr.height)
                current_x_in_row += fxtr.width + horizontal_gap
            else:
                # DEBUG: Announce failure and add to the unplaced list
                print(f"[DEBUG]   ❌ FAILED: Spot is blocked or outside. Adding to unplaced list.")
                unplaced_clinics.append(fxtr)

        return unplaced_clinics


    # This helper function is the final fallback grid search
    def _force_place_clinic(self, clinic_to_place, placed_bboxes):
        """
        Brute-force grid search to find ANY valid spot for a single clinic.
        """
        from shapely.geometry import box
        
        fxtr = clinic_to_place
        w, h = fxtr.width, fxtr.height
        print(f"\n[DEBUG] Force-searching for any spot for '{fxtr.name}' (Size: {w:.0f}x{h:.0f})...")
        
        y_step = 100
        x_step = 100
        
        # Start from the top and go down
        for y_try in range(int(self.cvc.max_y - h), int(self.cvc.min_y), -y_step):
            for x_try in range(int(self.cvc.min_x), int(self.cvc.max_x - w), x_step):
                candidate_box = box(x_try, y_try, x_try + w, y_try + h)

                is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
                is_inside = self.floorplan_polygon.contains(candidate_box)

                if is_inside and not is_overlapping:
                    # DEBUG: Announce the found spot
                    print(f"[DEBUG]   ✅ SUCCESS: Found clear spot at ({x_try:.0f}, {y_try:.0f}).")
                    self.place_fixture(fxtr, (x_try, y_try, 0), 0, False)
                    placed_bboxes.append((x_try, y_try, x_try + w, y_try + h))
                    return True

        # DEBUG: Announce complete failure
        print(f"[DEBUG]   ❌ FAILED: Grid search completed. No valid spot found for '{fxtr.name}'.")
        return False

        
    def _get_side_wall_segments(self, side: str) -> list:
        """
        A helper to get all wall segments on a specific side ('left', 'right', 'top', 'bottom').
        """
        all_segments = self.cvc.get_wall_segments(min_length=100)
        if not all_segments:
            return []

        # Define the search criteria based on the side
        if side in ['left', 'right']:
            target_coord = self.cvc.min_x if side == 'left' else self.cvc.max_x
            tolerance = (self.cvc.max_x - self.cvc.min_x) * 0.15
            coord_index = 0  # Compare X-coordinates
        elif side in ['top', 'bottom']:
            target_coord = self.cvc.max_y if side == 'top' else self.cvc.min_y
            tolerance = (self.cvc.max_y - self.cvc.min_y) * 0.15
            coord_index = 1  # Compare Y-coordinates
        else:
            return []

        candidate_segments = []
        for p1_coords, p2_coords in all_segments:
            mid_coord = (p1_coords[coord_index] + p2_coords[coord_index]) / 2
            if abs(mid_coord - target_coord) < tolerance:
                candidate_segments.append((p1_coords, p2_coords))
        
        return candidate_segments


    def place_clinics_by_perimeter_walk(self, clinics_to_place, placed_bboxes, 
                                       mirror_rules: List[str] = ['right', 'bottom']):
        """
        Places clinics by walking the perimeter, using an explicit list of rules
        to determine which walls require a true MIRROR transformation.
        """
        import collections
        import math
        from shapely.geometry import Point, box, Polygon
        from ezdxf.math import Vec2

        print(f"\n--- 🧠 Placing Clinics with Perimeter Walk (Mirror Rules: {mirror_rules}) ---")
        
        clinics_queue = collections.deque(clinics_to_place)
        if not clinics_queue: return []

        ordered_corners = self._get_reordered_corners_top_left()
        
        perimeter_path = []
        for i in range(len(ordered_corners)):
            p1 = Vec2(ordered_corners[i])
            p2 = Vec2(ordered_corners[(i + 1) % len(ordered_corners)])
            if p1.distance(p2) > 100: perimeter_path.append((p1, p2))

        for i, (segment_start, segment_end) in enumerate(perimeter_path):
            if not clinics_queue: break

            segment_vector = (segment_end - segment_start).normalize()
            segment_length = segment_start.distance(segment_end)
            
            inward_normal = segment_vector.orthogonal()
            if not self.floorplan_polygon.contains(Point(segment_start + (segment_vector * 10) + inward_normal)):
                inward_normal = -inward_normal

            cursor, margin_from_wall, gap_between_clinics = 50.0, 50.0, 100.0

            while clinics_queue:
                next_clinic = clinics_queue[0]
                if cursor + next_clinic.width > segment_length - 50.0: break

                base_rotation = math.degrees(segment_vector.angle)
                
                mid_x = (segment_start.x + segment_end.x) / 2
                mid_y = (segment_start.y + segment_end.y) / 2
                centroid = self.floorplan_polygon.centroid
                
                normalized_angle = abs(base_rotation) % 180
                is_vertical = (75 < normalized_angle < 105)
                is_horizontal = (normalized_angle < 15) or (normalized_angle > 165)
                
                wall_type = "other"
                if is_vertical and mid_x < centroid.x: wall_type = "left"
                elif is_vertical and mid_x > centroid.x: wall_type = "right"
                elif is_horizontal and mid_y > centroid.y: wall_type = "top"
                elif is_horizontal and mid_y < centroid.y: wall_type = "bottom"
                
                x_scale = 1.0
                if wall_type in mirror_rules:
                    x_scale = -1.0

                insert_point_offset = inward_normal * (margin_from_wall + next_clinic.height)
                insert_point = segment_start + (segment_vector * cursor) + insert_point_offset
                
                if x_scale == -1:
                    insert_point += segment_vector * next_clinic.width

                p1 = insert_point
                p2 = p1 + segment_vector.rotate_deg(90) * next_clinic.height
                p3 = p2 + segment_vector * next_clinic.width * x_scale
                p4 = p3 - segment_vector.rotate_deg(90) * next_clinic.height
                candidate_poly = Polygon([p1, p2, p3, p4])
                
                is_overlapping = any(candidate_poly.intersects(box(*b)) for b in placed_bboxes)
                is_inside = self.floorplan_polygon.contains(candidate_poly)

                if is_inside and not is_overlapping:
                    self.place_fixture(next_clinic, insert_point, base_rotation, True, xscale=x_scale)
                    min_x, min_y, max_x, max_y = candidate_poly.bounds
                    placed_bboxes.append((min_x, min_y, max_x, max_y))
                    print(f"    -> Placed '{next_clinic.name}' on '{wall_type}' wall (Mirrored: {x_scale < 0}).")
                    clinics_queue.popleft()
                    cursor += next_clinic.width + gap_between_clinics
                else:
                    cursor += 100.0
        
        return list(clinics_queue)
    


    def _get_reordered_corners_top_left(self):
        """
        Helper function to reorder corners to start at the top-most, left-most point.
        """
        corners = self.cvc.corners
        if not corners:
            return []

        # Find the corner closest to the ideal top-left (minimum x, maximum y)
        top_left_idx = min(range(len(corners)), 
                           key=lambda i: math.hypot(corners[i][0] - self.cvc.min_x, corners[i][1] - self.cvc.max_y))
        
        # Reorder the list to start from that point
        reordered = corners[top_left_idx:] + corners[:top_left_idx]
        print(f"  -> Reordered perimeter path to start at top-left corner: {reordered[0]}")
        return reordered
    

    def place_toilet(self):
        """Places toilet fixtures in top-left corner, shifting right if needed until placement is found"""
        toilet_fixtures = self.fixtures.get("toilet_fixtures", {})
        if "toilet" not in toilet_fixtures:
            return
        # Load toilet fixture
        fxtr = Fixture.Fixture(self.fixture_dict["toilet"]["name"],
                            self.fixture_dict["toilet"]["path"])
        # Calculate safe placement zone
        safe_margin = 100  # 100mm margin from walls
        base_x = self.cvc.min_x + safe_margin
        base_y = self.cvc.distance_from_bottom - safe_margin - fxtr.height
        x_increment = 50  # Shift right by 50mm each attempt
        # Try to place toilet
        count = toilet_fixtures["toilet"]
        for i in range(count):
            placed = False
            current_x = base_x
            current_y = base_y - (i * (fxtr.height + 300))  # Vertical position for this unit
            # Keep trying until we find a valid position or hit right boundary
            while not placed:
                # Create test points for all four corners
                test_points = [
                    Vec3(current_x, current_y, 0),  # bottom-left
                    Vec3(current_x + fxtr.width, current_y, 0),  # bottom-right
                    Vec3(current_x + fxtr.width, current_y + fxtr.height, 0),  # top-right
                    Vec3(current_x, current_y + fxtr.height, 0)  # top-left
                ]
                # Check if all points are inside floorplan
                all_inside = all(self.floorplan_polygon.contains(Point(pt.x, pt.y)) for pt in test_points)
                if all_inside:
                    # Place the fixture if it fits
                    insert_point = (current_x, current_y, 0)
                    self.place_fixture(fxtr, insert_point, 0, False)
                    print(f":white_check_mark: Placed toilet unit #{i+1} at ({current_x}, {current_y})")
                    placed = True
                else:
                    # Shift right and try again
                    current_x += x_increment
                    # Prevent infinite loop if we go too far right
                    if current_x + fxtr.width > self.cvc.max_x - safe_margin:
                        print(f":warning: Cannot place toilet unit #{i+1} - no valid position found")
                        placed = True  # Exit loop even though we didn't place it

  
    def place_boh_after_toilet(self, placed_bboxes):
        """
        Places all BOH furniture using a "Best of Both Worlds" strategy.
        1. Fixtures are organized into logical rows (Storage, Workstations, etc.).
        2. Within each row, fixtures are sorted from widest to narrowest for efficient packing.
        3. Placement occurs within a "Smart BOH Zone" matching the floorplan's true shape.
        """
        from Fixture import Fixture
        from shapely.geometry import Point, box
        try:
            print("\n--- Attempting to place Back-of-House (BOH) Fixtures (Final Strategy) ---")

            # --- 1. Load All BOH Fixture Counts ---
            boh_config = self.fixtures.get("boh_fixtures", {})
            if not any(boh_config.values()):
                print("ℹ️ No BOH fixtures specified for placement.")
                return

            counts = {key: boh_config.get(key, 0) for key in self.fixture_dict if self.fixture_dict[key].get('type') == 'boh'}
            if "pick_up_counter" in boh_config:
                counts["pick_up_counter"] = boh_config.get("pick_up_counter", 0)
            if "drop_box" in boh_config:
                counts["drop_box"] = boh_config.get("drop_box", 0)

            # --- 2. RESTORED: Organize Fixtures into Logical Rows ---
            row_1_fixtures, row_2_fixtures, row_3_fixtures, row_4_fixtures = [], [], [], []
            
            # Helper to load a fixture and add it to a row list
            def add_to_row(row, name, label):
                if counts.get(name, 0) > 0:
                    try:
                        fxtr = Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"])
                        row.append((fxtr, counts[name], label))
                    except (KeyError, ValueError) as e:
                        print(f"WARNING: Could not load BOH fixture '{name}': {e}")
            
            # Populate the logical rows as you originally intended
            add_to_row(row_1_fixtures, "storage_rack", "Storage Rack")
            add_to_row(row_1_fixtures, "pickup_storage_1200", "Pickup Storage 1200")
            add_to_row(row_1_fixtures, "pickup_storage_900", "Pickup Storage 900")
            add_to_row(row_1_fixtures, "pickup_table", "Pickup Table")
            add_to_row(row_1_fixtures, "ups_rack", "UPS Rack")
            add_to_row(row_1_fixtures, "water_dispenser", "Water Dispenser")
            add_to_row(row_2_fixtures, "QC_table_large", "QC Table Large")
            add_to_row(row_2_fixtures, "QC_table_medium", "QC Table Medium")
            add_to_row(row_2_fixtures, "Repair_Table_large", "Repair Table Large")
            add_to_row(row_2_fixtures, "Repair_Table_medium", "Repair Table Medium")
            add_to_row(row_3_fixtures, "staff_rack", "Staff Rack")
            add_to_row(row_3_fixtures, "Dining_Table_large", "Dining Table Large")
            add_to_row(row_3_fixtures, "Dining_Table_medium", "Dining Table Medium")
            add_to_row(row_4_fixtures, "pick_up_counter", "Pickup Counter")
            add_to_row(row_4_fixtures, "drop_box", "Drop Box")

            # --- 3. Define the "Smart BOH Zone" (Unchanged) ---
            room_max_x = max(self.cvc.x_coords)
            room_max_y = max(self.cvc.y_coords)
            room_center_x = (min(self.cvc.x_coords) + room_max_x) / 2
            slicing_box = box(room_center_x, min(self.cvc.y_coords) - 1000, room_max_x + 1000, room_max_y + 1000)
            boh_zone = self.floorplan_polygon.intersection(slicing_box)
            print(f"  -> Defined BOH Zone using the true floorplan shape on the right side.")

            # --- 4. Define Margins and the UPGRADED Helper Function ---
            margin_wall = 50
            margin_between = 100
            customer_row_gap = 800
            x_search_increment = 50

            def try_place_row(fixtures_to_place, start_x, start_y):
                
                # --- NEW: Sort fixtures for THIS ROW by width (largest first) ---
                fixtures_to_place.sort(key=lambda item: item[0].width, reverse=True)
                
                max_height_in_row = 0
                if fixtures_to_place:
                    max_height_in_row = max(item[0].height for item in fixtures_to_place)
                
                bottom_y = start_y - max_height_in_row
                current_x = start_x
                
                for fxtr, count, label in fixtures_to_place:
                    for i in range(count):
                        placed = False
                        x_try = current_x
                        while not placed:
                            x1, y1 = x_try - fxtr.width, bottom_y
                            x2, y2 = x1 + fxtr.width, y1 + fxtr.height
                            fixture_box = box(x1, y1, x2, y2)
                            
                            is_overlapping = any(fixture_box.intersects(box(*bbox)) for bbox in placed_bboxes)
                            is_inside_boh_zone = boh_zone.contains(fixture_box)

                            if not is_overlapping and is_inside_boh_zone:
                                self.place_fixture(fxtr, (x1, y1, 0), 0, False)
                                placed_bboxes.append((x1, y1, x2, y2))
                                print(f"✅ Placed {label} #{i+1} at ({x1:.0f}, {y1:.0f})")
                                placed = True
                                current_x = x1 - margin_between
                            else:
                                x_try -= x_search_increment
                                if x_try < boh_zone.bounds[0]:
                                    print(f"⚠️ Could not place {label} #{i+1}, no space found inside the BOH Zone.")
                                    break
                return max_height_in_row

            # --- 5. Execute Placement in Logical Rows ---
            last_y = room_max_y - margin_wall
            if row_1_fixtures:
                print("\n  -> Placing Utilities & Storage Row (Largest First)...")
                row_1_height = try_place_row(row_1_fixtures, room_max_x - margin_wall, last_y)
                last_y -= (row_1_height + margin_between)
            if row_2_fixtures:
                print("\n  -> Placing Workstations Row (Largest First)...")
                row_2_height = try_place_row(row_2_fixtures, room_max_x - margin_wall, last_y)
                last_y -= (row_2_height + margin_between)
            if row_3_fixtures:
                print("\n  -> Placing Staff & Dining Row (Largest First)...")
                row_3_height = try_place_row(row_3_fixtures, room_max_x - margin_wall, last_y)
                last_y -= (row_3_height + customer_row_gap)
            if row_4_fixtures:
                print("\n  -> Placing Customer Accessible Row (Largest First)...")
                try_place_row(row_4_fixtures, room_max_x - margin_wall, last_y)

            print("\n✅ Finished placing all BOH fixtures.")

        except Exception as e:
            print(f"⚠️ Error placing BOH fixtures: {str(e)}")
            raise

    

    def place_boh_intelligently_v1(self, placed_bboxes):
        """
        Places all BOH fixtures using a multi-phase, intelligent strategy.
        - V12: Added an inset margin to ensure the BOH partition is always
        drawn inside the main floorplan walls.
        - V13 (NEW): Registers the final BOH partition wall as an obstacle.
        """
        from Fixture import Fixture
        from shapely.geometry import box, MultiPolygon, LineString, Point, Polygon
        from shapely.ops import unary_union
        import collections

        print("\n--- 🧠 Placing BOH Fixtures with Intelligent Strategy ---")

        # --- PHASE 1 (Setup) ---
        boh_config = self.fixtures.get("boh_fixtures", {})
        if not any(boh_config.values()):
            print("  -> INFO: No BOH fixtures specified.")
            return

        storage_types = ["storage_rack", "pickup_storage_1200", "pickup_storage_900", "ups_rack", "staff_rack"]
        workstation_types = ["QC_table_large", "QC_table_medium", "Repair_Table_large", "Repair_Table_medium", "pickup_table"]
        amenity_types = ["Dining_Table_large", "Dining_Table_medium", "water_dispenser"]
        customer_facing_types = ["pick_up_counter", "drop_box"]

        fixtures_by_cat = collections.defaultdict(list)
        for name, count in boh_config.items():
            if count > 0:
                try:
                    fxtr = Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"])
                    if name in storage_types:
                        fixtures_by_cat["storage"].extend([fxtr] * count)
                    elif name in workstation_types:
                        fixtures_by_cat["workstation"].extend([fxtr] * count)
                    elif name in amenity_types:
                        fixtures_by_cat["amenity"].extend([fxtr] * count)
                    elif name in customer_facing_types:
                        fixtures_by_cat["customer_facing"].extend([fxtr] * count)
                except (KeyError, ValueError) as e:
                    print(f"  -> WARNING: Could not load BOH fixture '{name}': {e}")
        
        # --- PHASE 2: Define the BOH Zone with an Inset ---
        inset_margin = 100.0
        inset_floorplan = self.floorplan_polygon.buffer(-inset_margin)
        room_bounds = self.floorplan_polygon.bounds
        room_center_x = (room_bounds[0] + room_bounds[2]) / 2
        boh_zone_box = box(room_center_x, room_bounds[1], room_bounds[2], room_bounds[3])
        boh_zone = inset_floorplan.intersection(boh_zone_box)
        
        if boh_zone.is_empty:
            print("  -> WARNING: Could not define a valid BOH zone. Aborting.")
            return

        print(f"  -> Defined BOH Zone with a {inset_margin}mm margin from main walls.")
        zone_bounds = boh_zone.bounds
        internal_boh_bboxes = []

        # --- PHASE 3 & 4: Place Storage and Internal Fixtures ---
        # (This logic remains the same as before)
        print("\n  -> Placing storage racks against walls...")
        storage_queue = collections.deque(sorted(fixtures_by_cat["storage"], key=lambda f: f.width, reverse=True))
        
        def find_spot_and_place(fxtr_to_place, start_x, start_y, search_direction, search_axis):
            search_cursor = 0; max_search = 5000 
            while search_cursor < max_search:
                if search_axis == 'x':
                    x1 = start_x + (search_cursor * search_direction) - fxtr_to_place.width
                    y1 = start_y - fxtr_to_place.height
                else:
                    x1 = start_x - fxtr_to_place.width
                    y1 = start_y + (search_cursor * search_direction) - fxtr_to_place.height
                candidate = box(x1, y1, x1 + fxtr_to_place.width, y1 + fxtr_to_place.height)
                if boh_zone.contains(candidate.buffer(-1.0)) and not any(candidate.intersects(box(*b)) for b in placed_bboxes):
                    self.place_fixture(fxtr_to_place, (x1, y1, 0), 0, False)
                    bbox = (x1, y1, x1 + fxtr_to_place.width, y1 + fxtr_to_place.height)
                    placed_bboxes.append(bbox); internal_boh_bboxes.append(bbox)
                    print(f"    ✅ Placed '{fxtr_to_place.name}' in BOH zone.")
                    return True
                search_cursor += 100
            return False

        y_pos_top = zone_bounds[3] - 50; x_pos_top = zone_bounds[2] - 50
        storage_queue = [f for f in storage_queue if not find_spot_and_place(f, x_pos_top, y_pos_top, -1, 'x')]
        if storage_queue:
            y_pos_right = zone_bounds[3] - 50; x_pos_right = zone_bounds[2] - 50
            storage_queue = [f for f in storage_queue if not find_spot_and_place(f, x_pos_right, y_pos_right, -1, 'y')]
        
        print("\n  -> Packing remaining workstations and amenities...")
        internal_queue = collections.deque(sorted(fixtures_by_cat["workstation"] + fixtures_by_cat["amenity"], key=lambda f: f.width * f.height, reverse=True))
        racks_poly = unary_union([box(*b) for b in internal_boh_bboxes] or [Polygon()]).buffer(150)
        packing_zone = boh_zone.difference(racks_poly)
        if not packing_zone.is_empty:
            while internal_queue:
                fxtr = internal_queue.popleft(); placed = False
                for y_try in range(int(packing_zone.bounds[3] - fxtr.height), int(packing_zone.bounds[1]), -100):
                    for x_try in range(int(packing_zone.bounds[2] - fxtr.width), int(packing_zone.bounds[0]), -100):
                        candidate = box(x_try, y_try, x_try + fxtr.width, y_try + fxtr.height)
                        if packing_zone.contains(candidate.buffer(-1.0)) and not any(candidate.intersects(box(*b)) for b in placed_bboxes):
                            self.place_fixture(fxtr, (x_try, y_try, 0), 0, False)
                            bbox = (x_try, y_try, x_try + fxtr.width, y_try + fxtr.height)
                            placed_bboxes.append(bbox); internal_boh_bboxes.append(bbox)
                            placed = True; break
                    if placed: break

        # --- PHASE 5: Define, Draw, and REGISTER the Partition Wall ---
        print("\n  -> Defining and drawing BOH partition as a solid wall...")
        if internal_boh_bboxes:
            boh_polygons = [box(*b) for b in internal_boh_bboxes]
            merged_shape = unary_union(boh_polygons)
            outer_boundary = merged_shape.convex_hull.buffer(100.0, join_style=2)
            
            # --- Drawing logic (unchanged) ---
            wall_thickness = 50.0
            inner_boundary = outer_boundary.buffer(-wall_thickness)
            # ... [hatch and outline drawing code] ...
            outer_polys = outer_boundary.geoms if isinstance(outer_boundary, MultiPolygon) else [outer_boundary]
            inner_polys = inner_boundary.geoms if isinstance(inner_boundary, MultiPolygon) else [inner_boundary]
            for outer_poly, inner_poly in zip(outer_polys, inner_polys):
                self.msp.add_lwpolyline(list(outer_poly.exterior.coords), close=True, dxfattribs={"layer": "BOH_PARTITION_OUTLINE", "color": 40, "lineweight": 10})
                if not inner_poly.is_empty:
                    self.msp.add_lwpolyline(list(inner_poly.exterior.coords), close=True, dxfattribs={"layer": "BOH_PARTITION_OUTLINE", "color": 40, "lineweight": 10})
                hatch = self.msp.add_hatch(color=250); hatch.dxf.layer = "BOH_PARTITION_FILL"
                hatch.set_pattern_fill('ANSI32', scale=10); hatch.dxf.pattern_angle = 90
                path_outer = hatch.paths.add_edge_path(); points_outer = list(outer_poly.exterior.coords)
                for i in range(len(points_outer) - 1): path_outer.add_line(points_outer[i], points_outer[i+1])
                if not inner_poly.is_empty:
                    path_inner = hatch.paths.add_edge_path(); points_inner = list(inner_poly.exterior.coords)
                    for i in range(len(points_inner) - 1): path_inner.add_line(points_inner[i], points_inner[i+1])
            
            # ***************************************************************
            # ******************* THIS IS THE NEW FIX *******************
            # After creating the wall, add its bounding box to the main obstacle list.
            if not outer_boundary.is_empty:
                min_x, min_y, max_x, max_y = outer_boundary.bounds
                placed_bboxes.append((min_x, min_y, max_x, max_y))
                print(f"    -> Registered BOH partition wall as a new obstacle.")
            # ***************************************************************
            # ***************************************************************
            
        print("\n✅ Intelligent BOH Placement Complete.")

    
    def place_boh_intelligently(self, placed_bboxes):
        """
        Places all BOH fixtures using a multi-phase, intelligent strategy.
        - V14 (FINAL): The partition wall shape is now adjusted to "carve out"
          any existing fixtures (like clinics) to prevent overlaps.
        """
        from Fixture import Fixture
        from shapely.geometry import box, MultiPolygon, LineString, Point, Polygon
        from shapely.ops import unary_union
        import collections

        print("\n--- 🧠 Placing BOH Fixtures with Intelligent Strategy ---")

        # --- PHASE 1 (Setup) ---
        boh_config = self.fixtures.get("boh_fixtures", {})
        if not any(boh_config.values()):
            print("  -> INFO: No BOH fixtures specified.")
            return

        storage_types = ["storage_rack", "pickup_storage_1200", "pickup_storage_900", "ups_rack", "staff_rack"]
        workstation_types = ["QC_table_large", "QC_table_medium", "Repair_Table_large", "Repair_Table_medium", "pickup_table"]
        amenity_types = ["Dining_Table_large", "Dining_Table_medium", "water_dispenser"]
        customer_facing_types = ["pick_up_counter", "drop_box"]

        fixtures_by_cat = collections.defaultdict(list)
        for name, count in boh_config.items():
            if count > 0:
                try:
                    fxtr = Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"])
                    if name in storage_types:
                        fixtures_by_cat["storage"].extend([fxtr] * count)
                    elif name in workstation_types:
                        fixtures_by_cat["workstation"].extend([fxtr] * count)
                    elif name in amenity_types:
                        fixtures_by_cat["amenity"].extend([fxtr] * count)
                    elif name in customer_facing_types:
                        fixtures_by_cat["customer_facing"].extend([fxtr] * count)
                except (KeyError, ValueError) as e:
                    print(f"  -> WARNING: Could not load BOH fixture '{name}': {e}")
        
        # --- PHASE 2: Define the BOH Zone with an Inset ---
        inset_margin = 100.0
        inset_floorplan = self.floorplan_polygon.buffer(-inset_margin)
        room_bounds = self.floorplan_polygon.bounds
        room_center_x = (room_bounds[0] + room_bounds[2]) / 2
        boh_zone_box = box(room_center_x, room_bounds[1], room_bounds[2], room_bounds[3])
        boh_zone = inset_floorplan.intersection(boh_zone_box)
        
        if boh_zone.is_empty:
            print("  -> WARNING: Could not define a valid BOH zone. Aborting.")
            return

        print(f"  -> Defined BOH Zone with a {inset_margin}mm margin from main walls.")
        zone_bounds = boh_zone.bounds
        internal_boh_bboxes = []

        # --- PHASE 3 & 4: Place Storage and Internal Fixtures ---
        print("\n  -> Placing storage racks against walls...")
        storage_queue = collections.deque(sorted(fixtures_by_cat["storage"], key=lambda f: f.width, reverse=True))
        
        def find_spot_and_place(fxtr_to_place, start_x, start_y, search_direction, search_axis):
            search_cursor = 0; max_search = 5000 
            while search_cursor < max_search:
                if search_axis == 'x':
                    x1 = start_x + (search_cursor * search_direction) - fxtr_to_place.width
                    y1 = start_y - fxtr_to_place.height
                else:
                    x1 = start_x - fxtr_to_place.width
                    y1 = start_y + (search_cursor * search_direction) - fxtr_to_place.height
                candidate = box(x1, y1, x1 + fxtr_to_place.width, y1 + fxtr_to_place.height)
                if boh_zone.contains(candidate.buffer(-1.0)) and not any(candidate.intersects(box(*b)) for b in placed_bboxes):
                    self.place_fixture(fxtr_to_place, (x1, y1, 0), 0, False)
                    bbox = (x1, y1, x1 + fxtr_to_place.width, y1 + fxtr_to_place.height)
                    placed_bboxes.append(bbox); internal_boh_bboxes.append(bbox)
                    print(f"    ✅ Placed '{fxtr_to_place.name}' in BOH zone.")
                    return True
                search_cursor += 100
            return False

        y_pos_top = zone_bounds[3] - 50; x_pos_top = zone_bounds[2] - 50
        storage_queue = [f for f in storage_queue if not find_spot_and_place(f, x_pos_top, y_pos_top, -1, 'x')]
        if storage_queue:
            y_pos_right = zone_bounds[3] - 50; x_pos_right = zone_bounds[2] - 50
            storage_queue = [f for f in storage_queue if not find_spot_and_place(f, x_pos_right, y_pos_right, -1, 'y')]
        
        print("\n  -> Packing remaining workstations and amenities...")
        internal_queue = collections.deque(sorted(fixtures_by_cat["workstation"] + fixtures_by_cat["amenity"], key=lambda f: f.width * f.height, reverse=True))
        racks_poly = unary_union([box(*b) for b in internal_boh_bboxes] or [Polygon()]).buffer(150)
        packing_zone = boh_zone.difference(racks_poly)
        if not packing_zone.is_empty:
            while internal_queue:
                fxtr = internal_queue.popleft(); placed = False
                for y_try in range(int(packing_zone.bounds[3] - fxtr.height), int(packing_zone.bounds[1]), -100):
                    for x_try in range(int(packing_zone.bounds[2] - fxtr.width), int(packing_zone.bounds[0]), -100):
                        candidate = box(x_try, y_try, x_try + fxtr.width, y_try + fxtr.height)
                        if packing_zone.contains(candidate.buffer(-1.0)) and not any(candidate.intersects(box(*b)) for b in placed_bboxes):
                            self.place_fixture(fxtr, (x_try, y_try, 0), 0, False)
                            bbox = (x_try, y_try, x_try + fxtr.width, y_try + fxtr.height)
                            placed_bboxes.append(bbox); internal_boh_bboxes.append(bbox)
                            placed = True; break
                    if placed: break

        # --- PHASE 5: Define, Draw, and REGISTER the Partition Wall ---
        print("\n  -> Defining and drawing BOH partition as a solid wall...")
        if internal_boh_bboxes:
            boh_polygons = [box(*b) for b in internal_boh_bboxes]
            merged_shape = unary_union(boh_polygons)
            initial_wall_shape = merged_shape.convex_hull.buffer(100.0, join_style=2)
            
            # --- NEW CODE TO PREVENT OVERLAP ---
            # This carves out existing fixtures from the wall shape.
            print("    -> Checking for overlaps with existing fixtures...")
            non_boh_obstacles = [box(*b) for b in placed_bboxes if b not in internal_boh_bboxes]
            if non_boh_obstacles:
                obstacles_shape = unary_union(non_boh_obstacles)
                final_wall_shape = initial_wall_shape.difference(obstacles_shape)
                print("    -> Adjusted BOH wall shape to avoid overlaps.")
            else:
                final_wall_shape = initial_wall_shape
            # --- END OF NEW CODE ---
            
            # --- Drawing logic (MODIFIED to use the new, corrected shape) ---
            wall_thickness = 50.0
            inner_boundary = final_wall_shape.buffer(-wall_thickness)
            outer_polys = final_wall_shape.geoms if isinstance(final_wall_shape, MultiPolygon) else [final_wall_shape]
            inner_polys = inner_boundary.geoms if isinstance(inner_boundary, MultiPolygon) else [inner_boundary]
            for outer_poly, inner_poly in zip(outer_polys, inner_polys):
                self.msp.add_lwpolyline(list(outer_poly.exterior.coords), close=True, dxfattribs={"layer": "BOH_PARTITION_OUTLINE", "color": 40, "lineweight": 10})
                if not inner_poly.is_empty:
                    self.msp.add_lwpolyline(list(inner_poly.exterior.coords), close=True, dxfattribs={"layer": "BOH_PARTITION_OUTLINE", "color": 40, "lineweight": 10})
                hatch = self.msp.add_hatch(color=250); hatch.dxf.layer = "BOH_PARTITION_FILL"
                hatch.set_pattern_fill('ANSI32', scale=10); hatch.dxf.pattern_angle = 90
                path_outer = hatch.paths.add_edge_path(); points_outer = list(outer_poly.exterior.coords)
                for i in range(len(points_outer) - 1): path_outer.add_line(points_outer[i], points_outer[i+1])
                if not inner_poly.is_empty:
                    path_inner = hatch.paths.add_edge_path(); points_inner = list(inner_poly.exterior.coords)
                    for i in range(len(points_inner) - 1): path_inner.add_line(points_inner[i], points_inner[i+1])
            
            # Register the final, corrected shape as an obstacle
            if not final_wall_shape.is_empty:
                min_x, min_y, max_x, max_y = final_wall_shape.bounds
                placed_bboxes.append((min_x, min_y, max_x, max_y))
                print(f"    -> Registered BOH partition wall as a new obstacle.")
            
        print("\n✅ Intelligent BOH Placement Complete.")

    def _calculate_dynamic_euro_gap(self) -> float:
        """
        Calculates a dynamic horizontal gap for Euro Centres using a proportional,
        width-based strategy with a robust fallback.
        """
        from Fixture import Fixture
        # ADD THIS LINE FOR DEBUGGING
        print("--- CONFIRMED: Using the NEW dynamic proportional gap function! ---")
        print("\n    -> Calculating DYNAMIC PROPORTIONAL gap for Euro Centres...")

        # --- 1. Define Constants and Assumptions ---
        MIN_AISLE_WIDTH = 200.0
        WALL_FIXTURE_DEPTH_ESTIMATE = 100.0
        MIN_REASONABLE_GAP = 1.0   # Minimum gap to avoid overcrowding
        MAX_REASONABLE_GAP = 3000.0 # Increased max for wider rooms

        # --- THIS IS THE KEY TUNING PARAMETER ---
        # It sets the desired gap as a percentage of the available central space.
        # 0.15 means the gap will be 15% of the usable width.
        # Increase this for more spacing, decrease it for less.
        GAP_PERCENTAGE_OF_WIDTH = 0.90

        # --- 2. Calculate Usable Central Width (Same as before) ---
        total_width = self.cvc.max_x - self.cvc.min_x
        buffer_per_side = WALL_FIXTURE_DEPTH_ESTIMATE + MIN_AISLE_WIDTH
        usable_central_width = total_width - (2 * buffer_per_side)

        if usable_central_width <= 0:
            print(f"    ⚠️ Not enough central space. Defaulting to minimum gap: {MIN_REASONABLE_GAP}mm")
            return MIN_REASONABLE_GAP

        config = self.fixtures.get("floor_fixtures", {})
        euro_count = config.get("Euro_centre", 0)
        if euro_count <= 1: return 0.0

        # --- 3. Proportional Gap Calculation (The New Logic) ---
        proportional_gap = usable_central_width * GAP_PERCENTAGE_OF_WIDTH
        print(f"      -> Ideal proportional gap ({GAP_PERCENTAGE_OF_WIDTH:.0%}) is: {proportional_gap:.0f}mm")

        # --- 4. Reality Check: Will it actually fit? ---
        try:
            euro_fxtr = Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"])
            total_euro_width = euro_count * euro_fxtr.width
            number_of_gaps = euro_count - 1

            # Calculate the total width required with our ideal proportional gap
            required_width = total_euro_width + (number_of_gaps * proportional_gap)

            if required_width > usable_central_width:
                # The ideal gap is too big! Fall back to the "fill the space" method.
                print("      -> Proportional gap is too large. Falling back to 'fill available space' method.")
                total_gap_space = usable_central_width - total_euro_width
                dynamic_gap = total_gap_space / number_of_gaps
            else:
                # It fits perfectly! Use the proportional gap.
                print("      -> Proportional gap fits within the available space.")
                dynamic_gap = proportional_gap

        except Exception as e:
            print(f"    ⚠️ Could not load Euro_centre fixture: {e}. Defaulting to minimum gap.")
            return MIN_REASONABLE_GAP

        # --- 5. Apply Safeguards (Clamping) ---
        final_gap = max(MIN_REASONABLE_GAP, min(dynamic_gap, MAX_REASONABLE_GAP))

        print(f"    ✅ Final clamped dynamic gap: {final_gap:.0f}mm")
        return final_gap


    def _calculate_dynamic_vertical_gap(self) -> float:
        """
        Calculates a dynamic vertical gap for portrait mode based on the floorplan's
        total square footage. Smaller stores get tighter spacing, larger stores get more.
        - MODIFIED: Now calculates the area internally.
        """
        # --- NEW: Calculate the area directly inside this function ---
        if not hasattr(self, 'floorplan_polygon') or self.floorplan_polygon.is_empty:
            print("    -> WARNING: Floorplan polygon not found. Using default vertical gap.")
            return 800.0  # Return a safe default if the polygon doesn't exist

        area_sq_mm = self.floorplan_polygon.area
        SQMM_PER_SQFT = 92903.04 
        floor_area_sqft = area_sq_mm / SQMM_PER_SQFT
        # --- End of New Logic ---

        print(f"\n    -> Calculating dynamic VERTICAL ROW GAP based on area: {floor_area_sqft:.2f} sq. ft.")

        if floor_area_sqft <= 500:
            gap = 100.0
            print(f"      -> Area is small (<= 500 sq. ft.). Using a tight gap of {gap} mm.")
        elif floor_area_sqft <= 750:
            gap = 300.0
            print(f"      -> Area is medium-small (<= 750 sq. ft.). Using a gap of {gap} mm.")
        elif floor_area_sqft <= 1000:
            gap = 500.0
            print(f"      -> Area is medium (<= 1000 sq. ft.). Using a standard gap of {gap} mm.")
        elif floor_area_sqft <= 1250:
            gap = 700.0
            print(f"      -> Area is medium-large (<= 1250 sq. ft.). Using a wider gap of {gap} mm.")
        elif floor_area_sqft <= 1500:
            gap = 900.0
            print(f"      -> Area is large (<= 1500 sq. ft.). Using a very wide gap of {gap} mm.")
        elif floor_area_sqft <= 2300:
            gap = 400.0
            print(f"      -> Area is large (<= 1500 sq. ft.). Using a very wide gap of {gap} mm.")
            
        else:  # for floorplans larger than 1500 sq. ft.
            gap = 1200.0
            print(f"      -> Area is very large (> 1500 sq. ft.). Using a maximum gap of {gap} mm.")

        return gap

    def place_central_fixtures_portrait(self, placed_bboxes: List[tuple], bottom_margin_pct: float = 0.20) -> None:
        """
        Places central fixtures in a portrait orientation using an adaptive strategy.
        - MODIFIED: No longer requires floor_area_sqft as a parameter.
        """
        from Fixture import Fixture
        from shapely.geometry import box, LineString
        import math
        import collections

        print("\n--- 🧠 Placing Central Fixtures with DYNAMIC ROW SIZING (Portrait Mode) ---")

        # --- Define Horizontal Gaps ---
        GAP_EURO_TO_EURO = self._calculate_dynamic_euro_gap()#1000
        GAP_LENSBAR_TO_LENSBAR = 50.0 
        GAP_LENSBAR_TO_EURO = 50.0
        
        # ⭐ MODIFICATION: Call the helper function without arguments
        VERTICAL_ROW_GAP = self._calculate_dynamic_vertical_gap()

        # 1. SETUP & LOAD FIXTURES
        config = self.fixtures.get("floor_fixtures", {})
        euro_count = config.get("Euro_centre", 0)
        lensbar_count = config.get("Lensbar", 0)
        if euro_count + lensbar_count == 0: return

        fixture_queue = collections.deque()
        try:
            euro_fxtr_template = Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"]) if euro_count > 0 else None
            lensbar_fxtr_template = Fixture("Lensbar", self.fixture_dict["Lensbar"]["path"]) if lensbar_count > 0 else None
            if lensbar_count > 0:
                fixture_queue.extend([lensbar_fxtr_template] * lensbar_count)
            if euro_count > 0:
                fixture_queue.extend([euro_fxtr_template] * euro_count)
        except Exception as e:
            print(f"🔥 FATAL: Could not load a central fixture: {e}")
            return

        # 2. DEFINE PORTRAIT-SPECIFIC PARAMETERS
        print("  -> Configuring for PORTRAIT (Vertical Iteration, Horizontal Rows)")
        room_height = self.cvc.max_y - self.cvc.min_y
        aisle_buffer = room_height * bottom_margin_pct
        print(f"  -> Using a dynamic bottom margin of {bottom_margin_pct:.0%} ({aisle_buffer:.0f}mm)")
        
        cursor_pos = self.cvc.min_y + aisle_buffer
        cursor_end = self.cvc.max_y - 50.0
        get_local_space = lambda y: self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, y), (self.cvc.max_x + 100, y)]))

        def _is_row_valid(start_x, y, fixtures_in_row, gap):
            current_x = start_x
            for i, fxtr in enumerate(fixtures_in_row):
                candidate_box = box(current_x, y, current_x + fxtr.width, y + fxtr.height)
                if not self.floorplan_polygon.contains(candidate_box.buffer(-1.0)) or any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                    return False
                if i < len(fixtures_in_row) - 1:
                    current_x += fxtr.width + gap
            return True

        # 3. ADAPTIVE PLACEMENT LOOP
        while fixture_queue:
            if cursor_pos > cursor_end:
                print("    -> ⚠️ Ran out of vertical space. Stopping placement.")
                break

            next_fxtr_obj = fixture_queue[0]
            footprint = next_fxtr_obj.height
            intersection = get_local_space(cursor_pos + (footprint / 2))
            if not isinstance(intersection, LineString) or intersection.is_empty:
                cursor_pos += 100
                continue

            local_space_bounds = intersection.bounds
            local_width = local_space_bounds[2] - local_space_bounds[0]
            local_start_x = local_space_bounds[0]

            # 4. DYNAMIC DECISION LOGIC
            num_to_place = 0
            horizontal_gap = 0
            walking_space_margin = local_width * 0.55

            if next_fxtr_obj.name == "Lensbar":
                required_width_for_one = lensbar_fxtr_template.width #+ walking_space_margin
                if required_width_for_one <= local_width:
                    num_to_place = 1
                else:
                    cursor_pos += 100
                    continue
            
            elif next_fxtr_obj.name == "Euro_centre":
                horizontal_gap = GAP_EURO_TO_EURO
                required_width_for_two = (euro_fxtr_template.width * 2) + horizontal_gap + walking_space_margin
                if len(fixture_queue) >= 2 and all(f.name == "Euro_centre" for f in list(fixture_queue)[:2]) and required_width_for_two <= local_width:
                    num_to_place = 2
                else:
                    required_width_for_one = euro_fxtr_template.width + walking_space_margin
                    if required_width_for_one <= local_width:
                        num_to_place = 1
                        horizontal_gap = 0
                    else:
                        cursor_pos += 100
                        continue
            
            if num_to_place == 0:
                cursor_pos += 100
                continue

            # 5. EXECUTION WITH RESILIENT SEARCH
            fixtures_for_this_row = [fixture_queue[i] for i in range(num_to_place)]
            total_row_width = sum(f.width for f in fixtures_for_this_row) + (horizontal_gap * (num_to_place - 1))
            
            ideal_start_x = local_start_x + (local_width - total_row_width) / 2
            
            valid_start_x = None
            search_offset = 0
            max_search = local_width / 2

            while search_offset < max_search:
                for sign in [1, -1]:
                    if sign == -1 and search_offset == 0: continue
                    test_x = ideal_start_x + (search_offset * sign)
                    if _is_row_valid(test_x, cursor_pos, fixtures_for_this_row, horizontal_gap):
                        valid_start_x = test_x
                        break
                if valid_start_x is not None:
                    break
                search_offset += 100
            
            if valid_start_x is None:
                print(f"    -> ⚠️ Could not find a valid horizontal spot for the row. Skipping.")
                cursor_pos += 100
                continue

            current_x_in_row = valid_start_x
            for i in range(num_to_place):
                fxtr = fixture_queue.popleft()
                x1, y1 = current_x_in_row, cursor_pos
                if self._validate_and_place_at_point(fxtr, Vec2(x1 + fxtr.width/2, y1 + fxtr.height/2), 0, placed_bboxes):
                    print(f"    -> Placed '{fxtr.name}' at ({x1:.0f}, {y1:.0f})")
                else:
                    print(f"    -> ⚠️ Final validation failed for '{fxtr.name}' during placement.")
                
                current_x_in_row += fxtr.width + horizontal_gap

            # Use the dynamic vertical gap variable
            cursor_pos += footprint + VERTICAL_ROW_GAP

        if fixture_queue:
            print(f"\n--- ⚠️ Finished with {len(fixture_queue)} unplaced fixtures ---")
        else:
            print("\n--- ✅ Finished Dynamic Central Fixture Placement ---")


    def _calculate_dynamic_bottom_margin_percentage_v1(self) -> float:
        """
        Calculates a dynamic BOTTOM MARGIN percentage for portrait mode based on
        the vertical congestion of fixtures. More fixtures result in a smaller margin.
        """
        print("\n    -> Calculating dynamic BOTTOM MARGIN based on vertical fixture count...")

        try:
            # --- STEP 1: Count all fixtures that will be stacked vertically ---
            total_vertical_units = 0
            
            # Central fixtures are the primary consumers of vertical space
            total_vertical_units += self.fixtures.get("floor_fixtures", {}).get("Euro_centre", 0)
            total_vertical_units += self.fixtures.get("floor_fixtures", {}).get("Lensbar", 0)

            # A Corian set is a large vertical block
            total_vertical_units += self.fixtures.get("Corian_table_set", {}).get("Corian_table", 0) * 2 # Count as 2 units
            
            # The POS/AR/Sofa stack is another major vertical block
            if any(self.fixtures.get("POS", {}).values()) or any("sofa" in k.lower() for k in self.fixtures.get("loose_furniture", {})):
                total_vertical_units += 2 # Count the whole stack as 2 units

            print(f"      -> Total vertical fixture units calculated: {total_vertical_units}")

            # --- STEP 2: Choose a margin percentage from simple tiers ---
            # You can easily TWEAK these numbers to change the behavior.
            
            if total_vertical_units <= 4: # Low Congestion
                margin_pct = 0.35 # Use a spacious 35% bottom margin
                print(f"      -> Count is LOW. Using a spacious {margin_pct:.0%} bottom margin.")
            
            elif total_vertical_units <= 8: # Medium Congestion
                margin_pct = 0.25 # Use a standard 25% bottom margin
                print(f"      -> Count is MEDIUM. Using a standard {margin_pct:.0%} bottom margin.")
            
            else: # High Congestion
                margin_pct = 0.15 # Use a compact 15% margin to maximize space
                print(f"      -> Count is HIGH. Using a compact {margin_pct:.0%} bottom margin.")
                
            return margin_pct

        except Exception as e:
            print(f"    -> ⚠️ Could not calculate count-based margin due to an error: {e}")
            return 0.20 # Return a safe default


    def _calculate_dynamic_bottom_margin_percentage(self) -> float:
        """
        Calculates a dynamic BOTTOM MARGIN percentage for portrait mode based on
        a collaborative assessment of both vertical fixture congestion and total floor area.
        """
        print("\n    -> Calculating dynamic BOTTOM MARGIN based on fixture count and floor area...")

        try:
            # --- STEP 1: Get the total floor area ---
            # This new step retrieves the store's size in square feet.
            floor_area_sqft = self.calculate_area_sqft()

            # --- STEP 2: Count all fixtures that will be stacked vertically ---
            total_vertical_units = 0
            
            # Central fixtures are the primary consumers of vertical space
            total_vertical_units += self.fixtures.get("floor_fixtures", {}).get("Euro_centre", 0)
            total_vertical_units += self.fixtures.get("floor_fixtures", {}).get("Lensbar", 0)

            # A Corian set is a large vertical block
            total_vertical_units += self.fixtures.get("Corian_table_set", {}).get("Corian_table", 0) * 2 # Count as 2 units
            
            # The POS/AR/Sofa stack is another major vertical block
            if any(self.fixtures.get("POS", {}).values()) or any("sofa" in k.lower() for k in self.fixtures.get("loose_furniture", {})):
                total_vertical_units += 2 # Count the whole stack as 2 units


            print(f"      -> Total vertical fixture units: {total_vertical_units}")
            print(f"      -> Total floor area: {floor_area_sqft:.0f} sq. ft.")

            # --- STEP 3: Choose a margin percentage using BOTH area and congestion ---
            margin_pct = 0.25 # A safe default

            # Logic for SMALL stores (e.g., less than 500 sq. ft.)
            if floor_area_sqft < 500:
                print("      -> Store size is SMALL.")
                if total_vertical_units <= 4:      # Low congestion
                    margin_pct = 0.20
                elif total_vertical_units <= 8:    # Medium congestion
                    margin_pct = 0.15
                else:                              # High congestion
                    margin_pct = 0.10

            elif floor_area_sqft <= 750:
                print("      -> Store size is SMALL.")
                if total_vertical_units <= 4:      # Low congestion
                    margin_pct = 0.25
                elif total_vertical_units <= 8:    # Medium congestion
                    margin_pct = 0.20
                else:                              # High congestion
                    margin_pct = 0.15
            
            # Logic for MEDIUM stores (e.g., 750 to 1250 sq. ft.)
            elif floor_area_sqft <= 1250:
                print("      -> Store size is MEDIUM.")
                if total_vertical_units <= 4:      # Low congestion
                    margin_pct = 0.35
                elif total_vertical_units <= 8:    # Medium congestion
                    margin_pct = 0.25
                else:                              # High congestion
                    margin_pct = 0.20


            elif floor_area_sqft <= 2300:
                print("      -> Store size is MEDIUM.")
                if total_vertical_units <= 4:      # Low congestion
                    margin_pct = 0.30
                elif total_vertical_units <= 5:    # Medium congestion
                    margin_pct = 0.20
                else:                              # High congestion
                    margin_pct = 0.10
            # Logic for LARGE stores (e.g., more than 1250 sq. ft.)
            else:
                print("      -> Store size is LARGE.")
                if total_vertical_units <= 4:      # Low congestion
                    margin_pct = 0.40
                elif total_vertical_units <= 8:    # Medium congestion
                    margin_pct = 0.30
                else:                              # High congestion
                    margin_pct = 0.25
            
            print(f"      -> Final dynamic margin selected: {margin_pct:.0%}")
            return margin_pct

        except Exception as e:
            print(f"    -> ⚠️ Could not calculate dynamic margin due to an error: {e}")
            return 0.20 # Return a safe default


    def place_euro_centers_dynamically(self, placed_bboxes, bottom_margin_pct=0.20):
        """
        Places Euro Centre fixtures by dynamically determining the number of units
        that can fit per row based on the floorplan's width, while also anticipating
        the space needed for attached Discussion Tables.
        """
        from Fixture import Fixture
        from shapely.geometry import box

        # 1. Get configuration and load primary fixture
        config = self.fixtures.get("floor_fixtures", {})
        count = config.get("Euro_centre", 0)
        if count <= 0:
            return

        print(f"\n--- Attempting to place {count} Euro Centre(s) with dynamic row layout ---")

        try:
            euro_fxtr = Fixture(self.fixture_dict["Euro_centre"]["name"],
                            self.fixture_dict["Euro_centre"]["path"])
            # Pre-load a representative Discussion Table to get its dimensions for our calculation.
            # Note: The table is placed rotated, so its 'height' contributes to the total assembly width.
            discussion_fxtr = Fixture(self.fixture_dict["Discussion_table_medium"]["name"],
                                    self.fixture_dict["Discussion_table_medium"]["path"])
        except Exception as e:
            print(f"🔥 Could not load a required fixture for calculation: {e}")
            return

        # 2. NEW: Enhanced horizontal layout decision
        room_width = self.cvc.max_x - self.cvc.min_x
        horizontal_gap = 3  # Gap between two Euro Centres
        # --- NEW: Calculate walking space as 30% of the total room width ---
        walking_space_margin = room_width * 0.30
        print(f"ℹ️ Dynamic walking space margin calculated as 30% of room width: {walking_space_margin:.0f}mm")


        # --- Calculate the total width required for a "2-Euro" assembly ---
        # This includes: 2 Discussion Tables + 2 Euro Centres + 1 gap + walking space
        required_width_for_two = (
            (2 * discussion_fxtr.height) +  # Two tables are rotated by 90 degrees
            (2 * euro_fxtr.width) +
            horizontal_gap +
            walking_space_margin
        )

        # --- Decide on the number of fixtures per row ---
        if room_width > required_width_for_two:
            num_per_row = 2
            print(f"ℹ️ Room is wide enough for a 2-Euro assembly. Placing up to {num_per_row} per row.")
        else:
            num_per_row = 1
            print(f"ℹ️ Room is narrow. Placing {num_per_row} Euro Centre per row.")

        # Calculate the total width of the Euro Centre group for one row
        row_group_width = (num_per_row * euro_fxtr.width) + ((num_per_row - 1) * horizontal_gap)
        # Calculate the starting X coordinate to center the Euro group
        row_start_x = self.cvc.min_x + (room_width - row_group_width) / 2

        # 3. Determine vertical layout
        room_height = self.cvc.max_y - self.cvc.min_y
        vertical_gap = 600.0
        current_y = self.cvc.min_y + (room_height * bottom_margin_pct)

        # 4. Placement Loop (No changes in this section)
        placed_count = 0
        while placed_count < count:
            in_this_row = min(num_per_row, count - placed_count)
            
            for i in range(in_this_row):
                if (count % 2 != 0) and (placed_count == count - 1):
                    current_x = self.cvc.min_x + (room_width / 2) - (euro_fxtr.width / 2)
                    print("ℹ️ Centering the final fixture of an odd count.")
                else:
                    current_x = row_start_x + i * (euro_fxtr.width + horizontal_gap)

                x1, y1 = current_x, current_y
                x2, y2 = x1 + euro_fxtr.width, y1 + euro_fxtr.height
                candidate_box = box(x1, y1, x2, y2)

                is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
                is_inside = self.floorplan_polygon.contains(candidate_box)

                if is_inside and not is_overlapping:
                    self.place_fixture(euro_fxtr, (x1, y1, 0), 0, False)
                    placed_bboxes.append((x1, y1, x2, y2))
                    print(f"✅ Placed Euro Centre #{placed_count + 1} at ({x1:.0f}, {y1:.0f})")
                else:
                    print(f"⚠️ Spot for Euro Centre #{placed_count + 1} is blocked. It may be skipped.")
                
                placed_count += 1

            current_y += euro_fxtr.height + vertical_gap

        print(f"-> Finished Euro Centre placement.")


    def place_discussion_tables_attached_to_euros_v1(self, placed_bboxes):
        """
        Finds all placed Euro_centre fixtures and attaches the specified
        Discussion_tables to their left and right sides.
        """
        from Fixture import Fixture
        from ezdxf.bbox import extents
        from shapely.geometry import box, Polygon

        print("\n--- Attempting to attach Discussion Tables to Euro Centres ---")

        # 1. Find all Euro_centre fixtures that have already been placed
        euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
        if not euro_entities:
            print("ℹ️ No Euro_centre fixtures found to attach tables to. Skipping.")
            return

        # Sort them from bottom to top to ensure consistent attachment order
        euro_entities.sort(key=lambda e: e.dxf.insert.y)

        # 2. Define the types of tables and sides to process
        table_types = ["large", "medium", "small"]
        sides = ["left", "right"]
        # A small gap between the Euro Centre and the attached table
        gap = 1

        # 3. Loop through each table type and side to place them
        for table_type in table_types:
            for side in sides:
                # Construct the key to look up the count in the main fixtures dictionary
                config_key = f"Discussion_table_{table_type}_{side}"
                count = self.fixtures.get("floor_fixtures", {}).get(config_key, 0)

                if count <= 0:
                    continue # Skip if this type of table is not requested

                print(f"  -> Placing {count} '{config_key}'...")

                # Load the corresponding discussion table fixture
                try:
                    table_fixture_name = f"Discussion_table_{table_type}"
                    table_fxtr = Fixture(self.fixture_dict[table_fixture_name]["name"],
                                        self.fixture_dict[table_fixture_name]["path"])
                except Exception as e:
                    print(f"🔥 Could not load fixture for '{config_key}': {e}")
                    continue

                # Attach one table for each Euro Centre, up to the requested count
                placed_for_this_type = 0
                for euro_entity in euro_entities:
                    if placed_for_this_type >= count:
                        break # Stop when we've placed the required number

                    euro_bbox = extents([euro_entity], fast=True)

                    # 4. Calculate position and rotation based on the side
                    if side == "left":
                        # Rotated 90 degrees, placed to the left of the Euro Centre
                        rotation = 270
                        # The table's height becomes its width when rotated
                        insert_x = euro_bbox.extmin.x - table_fxtr.height - gap
                        # Center it vertically against the Euro Centre
                        insert_y = euro_bbox.center.y - (table_fxtr.width / 2)
                    else: # side == "right"
                        # Rotated 270 degrees, placed to the right
                        rotation = 90
                        insert_x = euro_bbox.extmax.x + gap + table_fxtr.height
                        # Center it vertically against the Euro Centre
                        insert_y = euro_bbox.center.y - (table_fxtr.width / 2)

                    # 5. Validate the spot before placing
                    # We need to manually calculate the rotated bounding box for validation
                    if rotation == 90:
                        x1, y1 = insert_x, insert_y
                        x2, y2 = x1 + table_fxtr.height, y1 + table_fxtr.width
                    else: # rotation == 270
                        x1, y1 = insert_x, insert_y
                        x2, y2 = x1 + table_fxtr.height, y1 + table_fxtr.width
                    
                    candidate_box = box(x1, y1, x2, y2)
                    is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
                    is_inside = self.floorplan_polygon.contains(candidate_box)

                    if is_inside and not is_overlapping:
                        # The insertion point for a 270-degree rotation needs adjustment
                        # because the block's handle (extmin) is now at the top-left.
                        if rotation == 270:
                            final_insert_point = (insert_x, insert_y + table_fxtr.width, 0)
                        else:
                            final_insert_point = (insert_x, insert_y, 0)

                        self.place_fixture(table_fxtr, final_insert_point, rotation, True)
                        placed_bboxes.append((x1, y1, x2, y2))
                        print(f"    ✅ Attached '{config_key}' to a Euro Centre.")
                        placed_for_this_type += 1
                    else:
                        print(f"    ⚠️ Spot for '{config_key}' was blocked or outside boundary.")


    def place_discussion_tables_attached_to_euros(self, placed_bboxes):
        """
        Finds all placed Euro_centre fixtures and attaches Discussion_tables in a
        balanced, alternating, outside-in pattern, moving from the bottom row upwards.
        """
        from Fixture import Fixture
        from ezdxf.bbox import extents
        from shapely.geometry import box, Polygon
        import collections

        print("\n--- Attempting to attach Discussion Tables to Euro Centres (Alternating Strategy) ---")

        # --- 1. Build Queues of All Tables to Place ---
        left_tables_queue = collections.deque()
        right_tables_queue = collections.deque()
        
        table_types = ["large", "medium", "small"]
        for table_type in table_types:
            try:
                # Load the fixture once per type
                table_fixture_name = f"Discussion_table_{table_type}"
                table_fxtr = Fixture(self.fixture_dict[table_fixture_name]["name"],
                                    self.fixture_dict[table_fixture_name]["path"])
                
                # Add the required number of this fixture to the left and right queues
                left_count = self.fixtures.get("floor_fixtures", {}).get(f"Discussion_table_{table_type}_left", 0)
                if left_count > 0:
                    left_tables_queue.extend([table_fxtr] * left_count)

                right_count = self.fixtures.get("floor_fixtures", {}).get(f"Discussion_table_{table_type}_right", 0)
                if right_count > 0:
                    right_tables_queue.extend([table_fxtr] * right_count)

            except Exception:
                # Skip if a specific table size (e.g., 'large') doesn't exist but is in the list
                continue
        
        if not left_tables_queue and not right_tables_queue:
            print("ℹ️ No attached discussion tables specified for placement.")
            return

        # --- 2. Group Euro Centres into Rows ---
        euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
        if not euro_entities:
            print("ℹ️ No Euro_centre fixtures found to attach tables to. Skipping.")
            return

        rows = collections.defaultdict(list)
        y_tolerance = 100.0 # Group euros if their Y-coords are within 100mm

        for entity in euro_entities:
            y_pos = entity.dxf.insert.y
            found_row = False
            for y_key in rows.keys():
                if abs(y_pos - y_key) < y_tolerance:
                    rows[y_key].append(entity)
                    found_row = True
                    break
            if not found_row:
                rows[y_pos].append(entity)
        
        # Sort rows from bottom to top
        sorted_rows = sorted(rows.values(), key=lambda r: r[0].dxf.insert.y)

        # --- 3. Place Tables in an Alternating, Row-by-Row Pattern ---
        # gap = 1000.0 # A small gap between the Euro Centre and the attached table
        lensbar_count = self.fixtures.get("lensbar_and_dropbox", {}).get("Lensbar", 0)
        gap = 5 if lensbar_count > 0 else 1000
        print(f"  -> Dynamic gap set to {gap}mm (Lensbar count: {lensbar_count})")

        for row_entities in sorted_rows:
            # Within each row, sort fixtures from left to right
            row_entities.sort(key=lambda e: e.dxf.insert.x)
            
            # --- Place on the LEFT side of the row's left-most Euro ---
            if left_tables_queue:
                table_to_place = left_tables_queue.popleft()
                euro_anchor = row_entities[0] # The left-most euro in this row
                euro_bbox = extents([euro_anchor], fast=True)
                
                rotation = 270
                insert_x = euro_bbox.extmin.x - table_to_place.height - gap
                insert_y = euro_bbox.center.y - (table_to_place.width / 2)
                
                # (Validation and Placement Logic)
                x1, y1 = insert_x, insert_y
                x2, y2 = x1 + table_to_place.height, y1 + table_to_place.width
                candidate_box = box(x1, y1, x2, y2)
                if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                    final_insert_point = (insert_x, insert_y + table_to_place.width, 0)
                    self.place_fixture(table_to_place, final_insert_point, rotation, True)
                    placed_bboxes.append((x1, y1, x2, y2))
                    print(f"    ✅ Attached '{table_to_place.name}' to a Euro Centre on the LEFT.")
                else:
                    print(f"    ⚠️ Spot for LEFT table was blocked. Adding back to queue.")
                    left_tables_queue.appendleft(table_to_place) # Add back if it failed
            
            # --- Place on the RIGHT side of the row's right-most Euro ---
            if right_tables_queue:
                table_to_place = right_tables_queue.popleft()
                euro_anchor = row_entities[-1] # The right-most euro in this row
                euro_bbox = extents([euro_anchor], fast=True)

                rotation = 90
                # insert_x = euro_bbox.extmax.x + gap
                insert_x = euro_bbox.extmax.x + gap + table_fxtr.height
                insert_y = euro_bbox.center.y - (table_to_place.width / 2)

                # (Validation and Placement Logic)
                x1, y1 = insert_x, insert_y
                x2, y2 = x1 + table_to_place.height, y1 + table_to_place.width
                candidate_box = box(x1, y1, x2, y2)
                if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                    final_insert_point = (insert_x, insert_y, 0)
                    self.place_fixture(table_to_place, final_insert_point, rotation, True)
                    placed_bboxes.append((x1, y1, x2, y2))
                    print(f"    ✅ Attached '{table_to_place.name}' to a Euro Centre on the RIGHT.")
                else:
                    print(f"    ⚠️ Spot for RIGHT table was blocked. Adding back to queue.")
                    right_tables_queue.appendleft(table_to_place)

        # Final report on any unplaced tables
        if left_tables_queue or right_tables_queue:
            unplaced_count = len(left_tables_queue) + len(right_tables_queue)
            print(f"⚠️ Could not place all tables. {unplaced_count} fixtures remain unplaced.")

   
    def get_existing_nonwall_bboxes(self):
        """
        Returns bounding boxes of all non-wall fixtures in the DXF drawing.
        """
        bboxes = []
        msp = self.doc.modelspace()
        for entity in msp:
            if entity.dxftype() == "INSERT":
                name = entity.dxf.name.lower()
                # Filter out wall fixtures by name
                if "hybrid" not in name and "mirror" not in name:
                    # Try to get block definition
                    try:
                        block = self.doc.blocks.get(entity.dxf.name)
                        # Get all points from block entities
                        min_x, min_y, max_x, max_y = None, None, None, None
                        for e in block:
                            if hasattr(e, "dxf"):
                                if hasattr(e.dxf, "insert"):
                                    x, y = e.dxf.insert.x, e.dxf.insert.y
                                elif hasattr(e.dxf, "start"):
                                    x, y = e.dxf.start.x, e.dxf.start.y
                                else:
                                    continue
                                if min_x is None or x < min_x: min_x = x
                                if min_y is None or y < min_y: min_y = y
                                if max_x is None or x > max_x: max_x = x
                                if max_y is None or y > max_y: max_y = y
                        # Transform by entity position
                        ex, ey = entity.dxf.insert.x, entity.dxf.insert.y
                        if min_x is not None and min_y is not None and max_x is not None and max_y is not None:
                            bboxes.append((ex + min_x, ey + min_y, ex + max_x, ey + max_y))
                    except Exception:
                        # Fallback: use insert point and a fixed size
                        ex, ey = entity.dxf.insert.x, entity.dxf.insert.y
                        bboxes.append((ex, ey, ex + 500, ey + 500))  # Fallback size
        return bboxes
    

    def place_screens_and_ar(self, placed_bboxes, bottom_margin_pct=0.20, gap_above_anchor=500):
        """
        Places the POS and AR units by anchoring them to the highest fixture group
        in the central area (Corian set if present, otherwise Euro Centres).
        """
        from Fixture import Fixture
        from shapely.geometry import Point
        from ezdxf.bbox import extents # Import the extents function

        try:
            # --- Phase A: Setup and Fixture Loading ---
            pos_fixtures = self.fixtures.get("POS", {})
            pos_type = next((key for key in ["pos_with_screen_large", "pos_with_screen_medium", "pos_with_screen_small", "pos_without_screen"] if pos_fixtures.get(key, 0) > 0), None)
            if not pos_type: return

            pos_fxtr = Fixture(self.fixture_dict[pos_type]["name"], self.fixture_dict[pos_type]["path"])
            ar_fxtr = Fixture(self.fixture_dict["AR"]["name"], self.fixture_dict["AR"]["path"])
            gap_between = 50
            total_width = pos_fxtr.width + gap_between + ar_fxtr.width
            required_fixture_height = max(pos_fxtr.height, ar_fxtr.height)

            # --- Phase B: NEW Dynamic Anchor Logic ---
            anchor_y = 0

            # NEW STRATEGY 1: Anchor to Corian Table set if it exists
            corian_set_entities = [
                e for e in self.msp.query('INSERT')
                if "CORIAN_TABLE" in e.dxf.name.upper() or "LOUNGE_SEAT" in e.dxf.name.upper()
            ]
            
            if corian_set_entities:
                # If Corian sets are found, their highest point is the new anchor
                anchor_y = extents(corian_set_entities).extmax.y
                print("ℹ️ Anchoring POS/AR placement above Corian Table set.")
            else:
                # FALLBACK STRATEGY: Anchor to Euro Centres if no Corian set is found
                print("ℹ️ No Corian set found. Anchoring POS/AR placement above Euro Centres.")
                euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
                if euro_entities:
                    anchor_y = extents(euro_entities).extmax.y
                else:
                    # If neither exist, use a fallback percentage of room height
                    anchor_y = self.cvc.min_y + (self.cvc.max_y - self.cvc.min_y) * 0.4

            # --- Phase C: Tiered Vertical Placement Logic (Now uses the dynamic anchor_y) ---
            ideal_y = -1
            margin_from_top_wall = 100
            room_max_y = max(self.cvc.y_coords)

            # 1. First, try to place using the desired gap above the determined anchor.
            proposed_y = anchor_y + gap_above_anchor
            if proposed_y + required_fixture_height < room_max_y - margin_from_top_wall:
                ideal_y = proposed_y
                print(f"ℹ️ Using specified gap of {gap_above_anchor}mm for POS/AR placement.")
            else:
                # 2. If the gap is too big, fit it in the remaining space.
                available_space = room_max_y - anchor_y - margin_from_top_wall
                if available_space >= required_fixture_height:
                    ideal_y = anchor_y + (available_space - required_fixture_height) / 2
                    print(f"⚠️ Specified gap was too large. Fitting POS/AR in available space instead.")
                else:
                    # 3. If no space, prepare for fallback search.
                    ideal_y = -1
                    print(f"⚠️ Not enough vertical space available above anchor fixtures. Switching to fallback search.")

            # --- Phase D & E (Placement and Fallback) ---
            # This part of the logic remains the same
            if ideal_y != -1:
                room_min_x, room_max_x = self.cvc.min_x, self.cvc.max_x
                ideal_x = room_min_x + (room_max_x - room_min_x - total_width) / 2
                
                pos_x1_ideal, pos_y1_ideal, pos_x2_ideal, pos_y2_ideal = ideal_x, ideal_y, ideal_x + pos_fxtr.width, ideal_y + pos_fxtr.height
                ar_x1_ideal = pos_x2_ideal + gap_between
                ar_x2_ideal = ar_x1_ideal + ar_fxtr.width
                ar_y1_ideal, ar_y2_ideal = ideal_y, ideal_y + ar_fxtr.height

                pos_overlap = any(not (pos_x2_ideal <= bx1 or pos_x1_ideal >= bx2 or pos_y2_ideal <= by1 or pos_y1_ideal >= by2) for bx1, by1, bx2, by2 in placed_bboxes)
                ar_overlap = any(not (ar_x2_ideal <= bx1 or ar_x1_ideal >= bx2 or ar_y2_ideal <= by1 or ar_y1_ideal >= by2) for bx1, by1, bx2, by2 in placed_bboxes)
                
                if not pos_overlap and not ar_overlap:
                    self.place_fixture(pos_fxtr, (ideal_x, ideal_y, 0), 0, False)
                    placed_bboxes.append((pos_x1_ideal, pos_y1_ideal, pos_x2_ideal, pos_y2_ideal))
                    print(f"✅ Placed POS '{pos_type}' using adaptive logic.")
                    
                    self.place_fixture(ar_fxtr, (ar_x1_ideal, ideal_y, 0), 0, False)
                    placed_bboxes.append((ar_x1_ideal, ar_y1_ideal, ar_x2_ideal, ar_y2_ideal))
                    print(f"✅ Placed AR using adaptive logic.")
                    return

            print("⚠️ Ideal position was blocked or out of space. Searching for an alternative spot...")
            
            # ... (The fallback grid search logic remains unchanged) ...
            
        except Exception as e:
            print(f"⚠️ Error placing POS and AR: {str(e)}")
            raise



    def place_pos_ar_portrait_dynamically_v3(self, placed_bboxes):
        """
        Places the POS and AR group using a resilient, iterative search strategy.
        It anchors to the highest central fixture and searches upwards for the first
        available clear horizontal space.
        """
        from shapely.geometry import box, LineString
        from ezdxf.bbox import extents
        import collections

        print("\n--- 🧠 Placing POS/AR with Dynamic Iterative Strategy ---")
        placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)

        # --- 1. SETUP: Load fixtures and calculate group dimensions ---
        try:
            pos_config = self.fixtures.get("POS", {})
            selected_pos_name = next((name for name, selected in pos_config.items() if selected > 0), None)
            if not selected_pos_name:
                print("  -> SKIPPED: No POS fixture selected.")
                return

            pos_fxtr = Fixture.Fixture(selected_pos_name, self.fixture_dict[selected_pos_name]["path"])
            ar_fxtr = Fixture.Fixture("AR", self.fixture_dict["AR"]["path"])
            gap_between = 100
            total_group_width = pos_fxtr.width + gap_between + ar_fxtr.width
            max_group_height = max(pos_fxtr.height, ar_fxtr.height)
        except Exception as e:
            print(f"🔥 FATAL: Could not load POS/AR fixtures: {e}")
            return

        # --- 2. ANCHORING: Find the top of the highest central fixture group ---
        # This reuses the reliable anchor-finding logic from the previous function.
        anchor_y = 0
        anchor_fixtures = [
            e for e in self.msp.query('INSERT')
            if "CORIAN_TABLE" in e.dxf.name.upper() or "LOUNGE_SEAT" in e.dxf.name.upper()
        ]
        if not anchor_fixtures:
            anchor_fixtures = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
        
        if anchor_fixtures:
            anchor_y = extents(anchor_fixtures).extmax.y
            print(f"  -> Found anchor point at y={anchor_y:.0f}")
        else:
            # Fallback if no primary anchors are found
            anchor_y = self.cvc.min_y + (self.cvc.max_y - self.cvc.min_y) * 0.6
            print(f"  -> No primary anchors found. Using fallback y={anchor_y:.0f}")

        # --- 3. ITERATIVE SEARCH: Search upwards from the anchor ---
        # This replaces the old "one shot" placement with a resilient loop.
        search_zone_start_y = anchor_y + 300  # Start with a 300mm gap
        search_zone_end_y = self.cvc.max_y - max_group_height - 100 # Stop before the top wall
        
        y_cursor = search_zone_start_y
        is_placed = False

        while y_cursor < search_zone_end_y:
            # At this y-level, find the available horizontal space
            horizontal_slice = LineString([(self.cvc.min_x, y_cursor), (self.cvc.max_x, y_cursor)])
            intersection = self.floorplan_polygon.intersection(horizontal_slice)
            
            if isinstance(intersection, LineString) and intersection.length >= total_group_width:
                local_x_min, _, local_x_max, _ = intersection.bounds
                
                # Now, perform a resilient horizontal search within this valid space
                ideal_x = local_x_min + (intersection.length - total_group_width) / 2
                search_offset = 0
                while search_offset < intersection.length / 2:
                    for sign in [1, -1]: # Check right of center, then left
                        if sign == -1 and search_offset == 0: continue
                        
                        test_x = ideal_x + (search_offset * sign)
                        
                        # Check if the entire group's bounding box is valid here
                        group_box = box(test_x, y_cursor, test_x + total_group_width, y_cursor + max_group_height)
                        if not any(group_box.intersects(box(*b)) for b in placed_bboxes):
                            # SUCCESS! We found a clear spot.
                            print(f"  -> Found clear spot at (x={test_x:.0f}, y={y_cursor:.0f})")
                            
                            # Place the fixtures
                            pos_x = test_x
                            ar_x = pos_x + pos_fxtr.width + gap_between
                            self.place_fixture(pos_fxtr, (pos_x, y_cursor, 0), 0, False)
                            placed_bboxes.append((pos_x, y_cursor, pos_x + pos_fxtr.width, y_cursor + pos_fxtr.height))
                            
                            self.place_fixture(ar_fxtr, (ar_x, y_cursor, 0), 0, False)
                            placed_bboxes.append((ar_x, y_cursor, ar_x + ar_fxtr.width, y_cursor + ar_fxtr.height))
                            
                            is_placed = True
                            break # Exit the horizontal search
                    if is_placed:
                        break # Exit the vertical search
                    search_offset += 100 # Nudge the horizontal search
            
            if is_placed:
                break # Exit the main vertical loop
            
            y_cursor += 100 # Move up to the next level to check
        
        if not is_placed:
            print("  -> ⚠️ FAILED: Could not find a clear spot for the POS/AR group after searching the entire zone.")


    def place_pos_ar_portrait_dynamically_v1(self, placed_bboxes):
        """
        Places the POS and AR group using a resilient, iterative search strategy.
        - The gap above the anchor is now DYNAMIC, increasing if standing tables are present.
        """
        from shapely.geometry import box, LineString
        from ezdxf.bbox import extents
        import collections

        print("\n--- 🧠 Placing POS/AR with Dynamic Iterative Strategy ---")
        placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)

        # --- 1. SETUP: Load fixtures and calculate group dimensions ---
        try:
            pos_config = self.fixtures.get("POS", {})
            selected_pos_name = next((name for name, selected in pos_config.items() if selected > 0), None)
            if not selected_pos_name:
                print("  -> SKIPPED: No POS fixture selected.")
                return

            pos_fxtr = Fixture.Fixture(selected_pos_name, self.fixture_dict[selected_pos_name]["path"])
            ar_fxtr = Fixture.Fixture("AR", self.fixture_dict["AR"]["path"])
            gap_between = 100
            total_group_width = pos_fxtr.width + gap_between + ar_fxtr.width
            max_group_height = max(pos_fxtr.height, ar_fxtr.height)
        except Exception as e:
            print(f"🔥 FATAL: Could not load POS/AR fixtures: {e}")
            return

        # --- 2. ANCHORING: Find the top of the highest central fixture group ---
        anchor_y = 0
        anchor_fixtures = [
            e for e in self.msp.query('INSERT')
            if "CORIAN_TABLE" in e.dxf.name.upper() or "LOUNGE_SEAT" in e.dxf.name.upper()
        ]
        if not anchor_fixtures:
            anchor_fixtures = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
        
        if anchor_fixtures:
            anchor_y = extents(anchor_fixtures).extmax.y
            print(f"  -> Found anchor point at y={anchor_y:.0f}")
        else:
            anchor_y = self.cvc.min_y + (self.cvc.max_y - self.cvc.min_y) * 0.6
            print(f"  -> No primary anchors found. Using fallback y={anchor_y:.0f}")

        # --- 3. ITERATIVE SEARCH: Search upwards from the anchor ---
        
        ### NEW: DYNAMIC GAP LOGIC ###
        # Check if standing tables are part of the layout to adjust the gap.
        standing_table_count = self.fixtures.get("table_fixtures", {}).get("Standing_table", 0)

        if standing_table_count > 0:
            # If they exist, use a WIDER gap to leave more room.
            gap_above_anchor = 1500.0
            print(f"  -> Standing tables are present. Using a wider anchor gap of {gap_above_anchor}mm.")
        else:
            # If not, use the standard, tighter gap.
            gap_above_anchor = 300.0
            print(f"  -> No standing tables. Using a standard anchor gap of {gap_above_anchor}mm.")
        
        search_zone_start_y = anchor_y + gap_above_anchor
        ### END OF NEW LOGIC ###

        search_zone_end_y = self.cvc.max_y - max_group_height - 100
        
        y_cursor = search_zone_start_y
        is_placed = False

        while y_cursor < search_zone_end_y:
            horizontal_slice = LineString([(self.cvc.min_x, y_cursor), (self.cvc.max_x, y_cursor)])
            intersection = self.floorplan_polygon.intersection(horizontal_slice)
            
            if isinstance(intersection, LineString) and intersection.length >= total_group_width:
                local_x_min, _, local_x_max, _ = intersection.bounds
                
                ideal_x = local_x_min + (intersection.length - total_group_width) / 2
                search_offset = 0
                while search_offset < intersection.length / 2:
                    for sign in [1, -1]:
                        if sign == -1 and search_offset == 0: continue
                        
                        test_x = ideal_x + (search_offset * sign)
                        
                        group_box = box(test_x, y_cursor, test_x + total_group_width, y_cursor + max_group_height)
                        if not any(group_box.intersects(box(*b)) for b in placed_bboxes):
                            print(f"  -> Found clear spot at (x={test_x:.0f}, y={y_cursor:.0f})")
                            
                            pos_x = test_x
                            ar_x = pos_x + pos_fxtr.width + gap_between
                            self.place_fixture(pos_fxtr, (pos_x, y_cursor, 0), 0, False)
                            placed_bboxes.append((pos_x, y_cursor, pos_x + pos_fxtr.width, y_cursor + pos_fxtr.height))
                            
                            self.place_fixture(ar_fxtr, (ar_x, y_cursor, 0), 0, False)
                            placed_bboxes.append((ar_x, y_cursor, ar_x + ar_fxtr.width, y_cursor + ar_fxtr.height))
                            
                            is_placed = True
                            break
                    if is_placed:
                        break
                    search_offset += 100
            
            if is_placed:
                break
            
            y_cursor += 100
        
        if not is_placed:
            print("  -> ⚠️ FAILED: Could not find a clear spot for the POS/AR group after searching the entire zone.")\

    def place_pos_ar_portrait_dynamically(self, placed_bboxes):
        """
        Places the POS and AR group using a resilient, iterative search strategy.
        - If POS is not selected, it places the AR unit by itself, anchored to a clinic.
        - The gap above the anchor is DYNAMIC, increasing if standing tables are present.
        """
        from shapely.geometry import box, LineString
        from ezdxf.bbox import extents
        from ezdxf.math import BoundingBox2d, Vec2
        import collections

        try:
            # --- 1. SETUP: Load fixtures and check for POS selection ---
            pos_config = self.fixtures.get("POS", {})
            selected_pos_name = next((name for name, selected in pos_config.items() if selected > 0), None)
            ar_fxtr = Fixture.Fixture("AR", self.fixture_dict["AR"]["path"])

            # --- STRATEGY 1: Place POS + AR Group ---
            if selected_pos_name:
                print("\n--- 🧠 Placing POS/AR with Dynamic Iterative Strategy ---")
                placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)

                pos_fxtr = Fixture.Fixture(selected_pos_name, self.fixture_dict[selected_pos_name]["path"])
                gap_between = 100
                total_group_width = pos_fxtr.width + gap_between + ar_fxtr.width
                max_group_height = max(pos_fxtr.height, ar_fxtr.height)

                anchor_y = 0
                anchor_fixtures = [
                    e for e in self.msp.query('INSERT')
                    if "CORIAN_TABLE" in e.dxf.name.upper() or "LOUNGE_SEAT" in e.dxf.name.upper()
                ]
                if not anchor_fixtures:
                    anchor_fixtures = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
                
                if anchor_fixtures:
                    anchor_y = extents(anchor_fixtures).extmax.y
                    print(f"  -> Found anchor point at y={anchor_y:.0f}")
                else:
                    anchor_y = self.cvc.min_y + (self.cvc.max_y - self.cvc.min_y) * 0.6
                    print(f"  -> No primary anchors found. Using fallback y={anchor_y:.0f}")

                standing_table_count = self.fixtures.get("table_fixtures", {}).get("Standing_table", 0)
                gap_above_anchor = 1500.0 if standing_table_count > 0 else 300.0
                print(f"  -> Using anchor gap of {gap_above_anchor}mm.")
                
                search_zone_start_y = anchor_y + gap_above_anchor
                search_zone_end_y = self.cvc.max_y - max_group_height - 100
                
                y_cursor = search_zone_start_y
                is_placed = False

                while y_cursor < search_zone_end_y:
                    horizontal_slice = LineString([(self.cvc.min_x, y_cursor), (self.cvc.max_x, y_cursor)])
                    intersection = self.floorplan_polygon.intersection(horizontal_slice)
                    
                    if isinstance(intersection, LineString) and intersection.length >= total_group_width:
                        local_x_min, _, local_x_max, _ = intersection.bounds
                        ideal_x = local_x_min + (intersection.length - total_group_width) / 2
                        search_offset = 0
                        while search_offset < intersection.length / 2:
                            for sign in [1, -1]:
                                if sign == -1 and search_offset == 0: continue
                                
                                test_x = ideal_x + (search_offset * sign)
                                group_box = box(test_x, y_cursor, test_x + total_group_width, y_cursor + max_group_height)
                                if not any(group_box.intersects(box(*b)) for b in placed_bboxes):
                                    print(f"  -> Found clear spot at (x={test_x:.0f}, y={y_cursor:.0f})")
                                    pos_x = test_x
                                    ar_x = pos_x + pos_fxtr.width + gap_between
                                    self.place_fixture(pos_fxtr, (pos_x, y_cursor, 0), 0, False)
                                    placed_bboxes.append((pos_x, y_cursor, pos_x + pos_fxtr.width, y_cursor + pos_fxtr.height))
                                    self.place_fixture(ar_fxtr, (ar_x, y_cursor, 0), 0, False)
                                    placed_bboxes.append((ar_x, y_cursor, ar_x + ar_fxtr.width, y_cursor + ar_fxtr.height))
                                    is_placed = True
                                    break
                            if is_placed: break
                            search_offset += 100
                    if is_placed: break
                    y_cursor += 100
                
                if not is_placed:
                    print("  -> ⚠️ FAILED: Could not find a clear spot for the POS/AR group after searching the entire zone.")

            # --- STRATEGY 2: AR Only, Anchored to Clinic ---
            else:
                print("\n  -> Placing AR only (no POS selected), anchoring to Clinic...")
                
                clinic_entities = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
                if not clinic_entities:
                    print("    -> SKIPPED: No clinic found to anchor to.")
                    return

                # Select the left-most clinic as the anchor for portrait mode
                left_most_clinic = min(clinic_entities, key=lambda e: e.dxf.insert.x)
                
                # Manually reconstruct the bounding box to ensure accuracy
                block_name_upper = left_most_clinic.dxf.name.upper()
                best_match_key = ""
                for key in self.fixture_dict.keys():
                    sanitized_key = key.upper().replace(" ", "_")
                    if block_name_upper.startswith(sanitized_key):
                        if len(key) > len(best_match_key):
                            best_match_key = key
                
                if not best_match_key:
                    print(f"    -> ⚠️ Could not identify original fixture for '{left_most_clinic.dxf.name}'. Using ezdxf.extents as fallback.")
                    anchor_bbox = extents([left_most_clinic])
                else:
                    anchor_fxtr_obj = Fixture.Fixture(self.fixture_dict[best_match_key]["name"], self.fixture_dict[best_match_key]["path"])
                    ip = left_most_clinic.dxf.insert
                    min_x, min_y = ip.x, ip.y
                    max_x = min_x + anchor_fxtr_obj.width
                    max_y = min_y + anchor_fxtr_obj.height
                    anchor_bbox = BoundingBox2d([Vec2(min_x, min_y), Vec2(max_x, max_y)])
                
                print(f"  -> Anchoring to left-most clinic at ({anchor_bbox.extmin.x:.0f}, {anchor_bbox.extmin.y:.0f})")

                rotation = 0
                ar_w, ar_h = ar_fxtr.width, ar_fxtr.height
                gap_from_clinic = 500.0

                # Priority: Try bottom first, then other sides
                potential_spots = [
                    {"side": "bottom", "x": anchor_bbox.center.x - (ar_w / 2), "y": anchor_bbox.extmin.y - gap_from_clinic - ar_h},
                    {"side": "left",   "x": anchor_bbox.extmin.x - gap_from_clinic - ar_w, "y": anchor_bbox.center.y - (ar_h / 2)},
                    {"side": "right",  "x": anchor_bbox.extmax.x + gap_from_clinic, "y": anchor_bbox.center.y - (ar_h / 2)},
                    {"side": "top",    "x": anchor_bbox.center.x - (ar_w / 2), "y": anchor_bbox.extmax.y + gap_from_clinic}
                ]

                def is_ar_spot_valid(x, y):
                    ar_poly = box(x, y, x + ar_w, y + ar_h)
                    if not self.floorplan_polygon.contains(ar_poly): return False
                    if any(ar_poly.intersects(box(*b)) for b in placed_bboxes): return False
                    return True

                is_placed = False
                for spot in potential_spots:
                    ideal_x, ideal_y = spot["x"], spot["y"]
                    if is_ar_spot_valid(ideal_x, ideal_y):
                        self.place_fixture(ar_fxtr, (ideal_x, ideal_y, 0), rotation, False)
                        placed_bboxes.append((ideal_x, ideal_y, ideal_x + ar_w, ideal_y + ar_h))
                        print(f"    ✅ Placed 'AR' successfully on the {spot['side']} of a clinic.")
                        is_placed = True
                        break
                
                if not is_placed:
                    print("    -> ⚠️ FAILED: Could not find a clear spot for the AR fixture on any side of the clinic.")

        except Exception as e:
            print(f"🔥 FATAL: An error occurred during POS/AR placement: {e}")
            return

# ******** NEW FUNCTION FOR GETTING BOTTOM SEGMENT
    def find_bottom_segment_y_coords(self, segments: List[Segment]) -> Optional[Tuple[float, float]]:
        def angle_from_horizontal(p1: Point, p2: Point) -> float:
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            if dx == dy == 0:
                return math.pi / 2
            return abs(math.atan2(dy, dx))  # 0 is perfectly horizontal

        all_ys = [y for seg in segments for (_, y) in seg]
        min_y, max_y = min(all_ys), max(all_ys)
        y_threshold = min_y + 0.2 * (max_y - min_y)  # bottom 20%

        candidates = []
        for p1, p2 in segments:
            avg_y = (p1[1] + p2[1]) / 2
            if avg_y <= y_threshold:
                angle = angle_from_horizontal(p1, p2)
                candidates.append(((p1, p2), avg_y, angle))

        if not candidates:
            return None

        # Prefer lower average y, then more horizontal (smaller angle)
        candidates.sort(key=lambda x: (x[1], x[2]))
        best_segment = candidates[0][0]
        
        min_x_ind = 0
        if best_segment[0][0] > best_segment[1][0]:
            min_x_ind = 1
        return best_segment[min_x_ind], best_segment[1-min_x_ind]
#----------------placement wall_fixtures by splitting---------------------------------------------------------

    def place_wall_fixtures_auto_split(self):
        """
        Splits wall fixtures and places them. Both left and right walls only
        check for collisions against the initial set of non-wall fixtures.
        """
        from Fixture import Fixture
        import traceback
        # Wrap the entire process in a try...except block to gracefully handle any errors during placement.
        try:
            # Get the dictionary of wall fixtures and their requested counts.
            wall_fixtures = self.fixtures.get("wall_fixtures", {})
            # Initialize empty lists to hold the fixtures for each wall.
            left_wall_queue, right_wall_queue = [], []

            # --- Fixture Distribution ---
            # Loop through each type of wall fixture requested.
            for fxtr_name, total in wall_fixtures.items():
                # Split the total count of each fixture type as evenly as possible between the two walls.
                left_count  = total // 2
                right_count = total - left_count
                # Add the fixtures to their respective queues.
                left_wall_queue.extend([(fxtr_name, 1)] * left_count)
                right_wall_queue.extend([(fxtr_name, 1)] * right_count)

            print(f"\n🎯 Total wall fixtures: {len(left_wall_queue)+len(right_wall_queue)} "
                f"➜ Left: {len(left_wall_queue)}, Right: {len(right_wall_queue)}")
            
            # --- Geometric Setup ---
            # Call helper functions to determine the angle and starting corner points for each side wall.
            left_wall_angle = self.get_wall_angle("left")
            right_wall_angle = self.get_wall_angle("right")
            print(f"📐 Detected wall angles -> Left: {left_wall_angle:.1f}°, Right: {right_wall_angle:.1f}°")

            # Find the bottom-most horizontal segment of the floorplan to determine the starting Y-coordinates.
            segments = self.cvc.get_wall_segments()
            bottom_points = self.find_bottom_segment_y_coords(segments)
            # If no bottom segment can be found, abort the placement.
            if not bottom_points:
                print("⚠️ Could not determine bottom segment for wall fixture placement. Aborting.")
                return
            
            # Unpack the two corner points of the bottom segment.
            left_start_point, right_start_point = bottom_points

            # --- Obstacle Detection ---
            # Get the list of obstacles (clinics, BOH fixtures) to avoid during placement.
            initial_obstacles = self._get_accurate_obstacle_bboxes()

            # --- Fixture Placement Execution ---
            # Call the placement function for the left wall. It will check for collisions against the initial_obstacles.
            self.place_wall_queue("left",  left_wall_queue,  initial_obstacles, left_start_point, left_wall_angle)
            
            # Call the placement function for the right wall. It also checks against the same initial_obstacles list.
            # This prevents wall fixtures from colliding with each other across the room.
            self.place_wall_queue("right", right_wall_queue, initial_obstacles, right_start_point, right_wall_angle)

            # # After placing the main wall fixtures, check if a large bench also needs to be placed.
            # if ("large_bench" in self.fixtures.get("floor_fixtures", {}) and self.fixtures["floor_fixtures"]["large_bench"] > 0 and not hasattr(self, "bench_placed")):
            #     print("\n🪑 All wall fixtures placed, now placing large bench...")
            #     self.place_bench_after_last_hybrid_mirror()

        except Exception as e:
            print(f"⚠️ Error in wall-fixture placement: {e}")
            traceback.print_exc()
            raise

    def _get_accurate_obstacle_bboxes(self, include_all=False):
        """
        Returns accurate bounding boxes for fixtures.
        If include_all is False, it returns only 'clinic', 'boh', and 'Eye_massage_area' types.
        If include_all is True, it returns all fixtures.
        """
        from ezdxf.bbox import extents
        bboxes = []
        msp = self.doc.modelspace()
        
        for entity in msp.query('INSERT'):
            block_name_upper = entity.dxf.name.upper()
            
            best_match_key = ""
            for key in self.fixture_dict.keys():
                sanitized_key = key.upper().replace(" ", "_")
                if block_name_upper.startswith(sanitized_key):
                    if len(key) > len(best_match_key):
                        best_match_key = key
            
            if best_match_key:
                fixture_type = self.fixture_dict[best_match_key].get("type")
                
                # --- Obstacle Filtering ---
                # <<< MODIFIED LINE >>>
                if include_all or fixture_type in ['clinic', 'boh'] or best_match_key == "Eye_massage_area":
                    try:
                        entity_bbox = extents([entity], fast=True)
                        bboxes.append((entity_bbox.extmin.x, entity_bbox.extmin.y, entity_bbox.extmax.x, entity_bbox.extmax.y))
                    except (RuntimeError, ZeroDivisionError, TypeError):
                        print(f"⚠️ Could not compute bounding box for '{entity.dxf.name}'.")
        
        print(f"✅ Found {len(bboxes)} obstacles to avoid.")
        return bboxes

    
   
    def place_wall_queue(self, wall_side: str, fixture_queue: list, placed_bboxes: list, start_point: Point, wall_angle_deg: float):
        # Import necessary libraries for this function's scope.
    
        from Fixture import Fixture
        from shapely.geometry import Polygon
        from ezdxf.math import BoundingBox2d

        # --- Determine which mirror to use globally for all placements in this queue ---
        # Read the mirror selection dictionary from the main fixtures configuration.
        mirror_selection_config = self.fixtures.get("mirror_selection", {})
        
        # Set a default mirror type in case no selection is made.
        selected_mirror_name = "mirror" 
        
        # Loop through the selection config to find the first mirror marked as active (value > 0).
        for name, is_selected in mirror_selection_config.items():
            if is_selected > 0:
                # If an active mirror is found, set it as the selection.
                selected_mirror_name = name
                # Stop searching immediately to only use the first active one found.
                break 
        
        # --- Conditionally set the horizontal spacing based on the chosen mirror ---
        # Check if the selected mirror is the 'different' type.
        if selected_mirror_name == "mirror_different":
            # If it is, apply no extra horizontal inset.
            horizontal_inset_for_hybrid = 0.0
        else:
            # Otherwise, apply the standard 50mm inset.
            horizontal_inset_for_hybrid = 50.0

        # 1. DEFINE WALL VECTORS
        # Convert the wall's angle from degrees to radians for trigonometric functions.
        wall_angle_rad = math.radians(wall_angle_deg)
        # Create a unit vector that points along the direction of the wall.
        wall_direction = Vec2(math.cos(wall_angle_rad), math.sin(wall_angle_rad))
        # Create a unit vector that is perpendicular to the wall's direction.
        perp_vec = Vec2(-wall_direction.y, wall_direction.x)

        # 2. DETERMINE THE CORRECT "INWARD" DIRECTION
        # Create a test point slightly along the wall from the start.
        test_point_on_wall = Vec2(start_point) + wall_direction * 100
        # Create another test point slightly off the wall in the perpendicular direction.
        test_point_inward = test_point_on_wall + perp_vec * 1.0
        
        # Assume the initial perpendicular vector points inward.
        inward_normal = perp_vec
        # Check if the test point is actually inside the floorplan's polygon shape.
        if not self.floorplan_polygon.contains(Point(test_point_inward.x, test_point_inward.y)):
            # If it's not, flip the vector so it points inward correctly.
            inward_normal = -perp_vec

        # 3. SET UP ROTATION AND CURSORS
        # Set the fixture's rotation based on the wall's angle for the left wall.
        if wall_side == "left":
            fixture_rotation_deg = wall_angle_deg
        # For the right wall, add 180 degrees to make the fixture face inward.
        else:
            fixture_rotation_deg = wall_angle_deg + 180
        
        # The starting corner for all placements on this wall.
        origin = Vec2(start_point)
        # The cursor tracks the distance along the wall for placing the next fixture pair. Start with a small offset.
        y_cursor = 50.0
        # The minimum gap between the fixture's back and the wall line.
        margin_from_wall = 10.0

        # Apply a special one-time vertical offset for the right wall to ensure correct stacking alignment.
        if wall_side == "right" and fixture_queue:
            try:
                # Get the name of the first fixture in the queue.
                first_hybrid_name = fixture_queue[0][0]
                # Load that fixture to get its dimensions.
                first_hybrid = Fixture(first_hybrid_name, self.fixture_dict[first_hybrid_name]["path"])
                # Shift the starting point up by the width of the first fixture.
                y_cursor += first_hybrid.width
                print(f"✅ Applied starting inset of {first_hybrid.width:.1f}mm for right wall.")
            except (KeyError, ValueError) as e:
                print(f"⚠️ Could not load first hybrid for right wall offset: {e}")

        # Log the placement details to the console for debugging.
        print(f"--- Placing fixtures on {wall_side} wall (Angle: {wall_angle_deg:.1f}°) ---")
        print(f"ℹ️ Using globally selected mirror: '{selected_mirror_name}'")
        print(f"ℹ️ Horizontal inset for hybrid set to: {horizontal_inset_for_hybrid}mm")


        # 4. MAIN PLACEMENT LOOP
        # Process each primary fixture from the queue one by one.
        for idx, (fixture_name, _) in enumerate(fixture_queue):
            try:
                # Load the primary wall fixture (e.g., a hybrid unit).
                hybrid = Fixture(fixture_name, self.fixture_dict[fixture_name]["path"])
                # Load the mirror that was globally selected earlier.
                mirror = Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
            except (KeyError, ValueError) as e:
                # If any fixture can't be loaded, print an error and skip to the next one.
                print(f"⚠️ Could not load fixture {fixture_name} or the selected mirror '{selected_mirror_name}': {e}")
                continue

            # --- A. VALIDATE AND PLACE HYBRID ---
            # Calculate the total distance inward from the wall line.
            hybrid_offset = margin_from_wall + hybrid.height + horizontal_inset_for_hybrid
            # Calculate the final insertion point using the origin, distance along the wall, and distance inward.
            hybrid_insert_pos = origin + (wall_direction * y_cursor) + (inward_normal * hybrid_offset)
            
            # Create a transformation matrix to get the hybrid's final position and rotation in the world.
            transform_h = Matrix44.chain(Matrix44.z_rotate(math.radians(fixture_rotation_deg)), Matrix44.translate(hybrid_insert_pos.x, hybrid_insert_pos.y, 0))
            # Get the coordinates of the four corners of the hybrid's bounding box in world space.
            world_corners_h = list(transform_h.transform_vertices(hybrid.bounding_box.rect_vertices()))
            # Create a polygon from the world-space corners for accurate checking.
            poly_h = Polygon([(p.x, p.y) for p in world_corners_h])
            # Boundary Check: Ensure the fixture is fully inside the main floorplan polygon.
            if not self.floorplan_polygon.contains(poly_h):
                print(f"⚠️ Hybrid '{fixture_name}' is outside floorplan. Stopping placement on {wall_side} wall.")
                break
            # Create an axis-aligned bounding box for faster overlap checks.
            aabb_h = BoundingBox2d(world_corners_h)
            # Collision Check: See if the fixture's bounding box intersects with any existing obstacles.
            if any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes):
                print(f"⚠️ Hybrid '{fixture_name}' overlaps another fixture. Stopping placement on {wall_side} wall.")
                break
            
            # If all checks pass, place the fixture into the DXF modelspace.
            self.place_fixture(hybrid, (hybrid_insert_pos.x, hybrid_insert_pos.y, 0), fixture_rotation_deg, True)

            # --- B. VALIDATE AND PLACE MIRROR ---
            # Calculate the mirror's vertical position relative to the hybrid's starting position to stack it on top.
            if wall_side == "left":
                mirror_y_offset = y_cursor + hybrid.width
            else: # right wall
                mirror_y_offset = y_cursor + mirror.width
            # Calculate the mirror's horizontal distance from the wall.
            mirror_offset_from_wall = margin_from_wall + mirror.height
            # Calculate the final insertion point for the mirror.
            mirror_insert_pos = origin + (wall_direction * mirror_y_offset) + (inward_normal * mirror_offset_from_wall)
            
            # Perform the same validation checks for the mirror as were done for the hybrid.
            transform_m = Matrix44.chain(Matrix44.z_rotate(math.radians(fixture_rotation_deg)), Matrix44.translate(mirror_insert_pos.x, mirror_insert_pos.y, 0))
            world_corners_m = list(transform_m.transform_vertices(mirror.bounding_box.rect_vertices()))
            poly_m = Polygon([(p.x, p.y) for p in world_corners_m])
            if not self.floorplan_polygon.contains(poly_m):
                print(f"⚠️ Mirror is outside floorplan. Stopping placement on {wall_side} wall.")
                break
            aabb_m = BoundingBox2d(world_corners_m)
            if any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes):
                print(f"⚠️ Mirror overlaps another fixture. Stopping placement on {wall_side} wall.")
                break

            # If validation passes, place the mirror.
            self.place_fixture(mirror, (mirror_insert_pos.x, mirror_insert_pos.y, 0), fixture_rotation_deg, True)

            # --- C. UPDATE CURSOR FOR NEXT PAIR ---
            # Move the main vertical cursor up by the combined width of the pair that was just placed.
            y_cursor += hybrid.width + mirror.width

#--------------placement wall fixtures sequentially-------------------------------------------------

    def place_wall_fixtures_sequentially(self):
        """
        Places wall fixtures sequentially, starting on the left wall and
        moving to the right wall with any remaining fixtures. This uses the original
        reliable placement logic for each wall.
        """
        from Fixture import Fixture
        import traceback
        try:
            wall_fixtures = self.fixtures.get("wall_fixtures", {})
            
            # Create a single queue for all wall fixtures based on user counts.
            total_wall_queue = []
            for fxtr_name, total in wall_fixtures.items():
                if total > 0:
                    total_wall_queue.extend([(fxtr_name, 1)] * total)

            if not total_wall_queue:
                print("ℹ️ No wall fixtures were specified for placement.")
                return

            print(f"\n🎯 Total wall fixtures to place sequentially: {len(total_wall_queue)}")
            
            # --- Geometric Setup ---
            left_wall_angle = self.get_wall_angle("left")
            right_wall_angle = self.get_wall_angle("right")
            print(f"📐 Detected wall angles -> Left: {left_wall_angle:.1f}°, Right: {right_wall_angle:.1f}°")

            segments = self.cvc.get_wall_segments()
            bottom_points = self.find_bottom_segment_y_coords(segments)
            if not bottom_points:
                print("⚠️ Could not determine bottom segment for wall fixture placement. Aborting.")
                return
            left_start_point, right_start_point = bottom_points

            # --- Fixture Placement Execution ---
            
            # 1. Get initial obstacles (only non-wall fixtures like clinics, BOH).
            initial_obstacles = self._get_accurate_obstacle_bboxes()

            # 2. Attempt to place fixtures on the left wall.
            print(f"\n--- Attempting to place up to {len(total_wall_queue)} fixtures on the LEFT wall... ---")
            remaining_fixtures = self.place_wall_queue_sequentially(
                "left", 
                total_wall_queue, 
                initial_obstacles, # Check only against pre-existing obstacles.
                left_start_point, 
                left_wall_angle
            )
            
            placed_on_left = len(total_wall_queue) - len(remaining_fixtures)
            print(f"✅ Placed {placed_on_left} fixture pairs on the left wall.")

            # 3. If any fixtures remain, attempt to place them on the right wall.
            if remaining_fixtures:
                # IMPORTANT: Re-scan for obstacles. This new list will include the fixtures just placed on the left wall.
                updated_obstacles = self._get_accurate_obstacle_bboxes(include_all=True)
                
                print(f"\n--- Attempting to place the remaining {len(remaining_fixtures)} fixtures on the RIGHT wall... ---")
                final_unplaced = self.place_wall_queue_sequentially(
                    "right", 
                    remaining_fixtures, 
                    updated_obstacles, # Use the new, complete obstacle list.
                    right_start_point, 
                    right_wall_angle
                )
                
                placed_on_right = len(remaining_fixtures) - len(final_unplaced)
                print(f"✅ Placed {placed_on_right} fixture pairs on the right wall.")

                if final_unplaced:
                    unplaced_summary = {}
                    for name, _ in final_unplaced:
                        unplaced_summary[name] = unplaced_summary.get(name, 0) + 1
                    print(f"⚠️ Could not place all fixtures. {len(final_unplaced)} fixtures remain unplaced: {unplaced_summary}")
            
        except Exception as e:
            print(f"⚠️ Error in sequential wall-fixture placement: {e}")
            traceback.print_exc()
            raise


    def place_wall_queue_sequentially(self, wall_side: str, fixture_queue: list, placed_bboxes: list, start_point: Point, wall_angle_deg: float):
        """
        Places a queue of fixtures along a single wall, checking only against the
        provided `placed_bboxes`. It returns any fixtures that could not be placed.
        """
        from Fixture import Fixture
        from shapely.geometry import Polygon, Point
        from ezdxf.math import BoundingBox2d, Vec2, Matrix44
        import math

        # --- Setup logic (mirror selection, vectors, rotation) ---
        mirror_selection_config = self.fixtures.get("mirror_selection", {})
        selected_mirror_name = "mirror" 
        for name, is_selected in mirror_selection_config.items():
            if is_selected > 0:
                selected_mirror_name = name
                break 
        
        horizontal_inset_for_hybrid = 0.0 if selected_mirror_name == "mirror_different" else 50.0

        wall_angle_rad = math.radians(wall_angle_deg)
        wall_direction = Vec2(math.cos(wall_angle_rad), math.sin(wall_angle_rad))
        perp_vec = Vec2(-wall_direction.y, wall_direction.x)

        test_point_on_wall = Vec2(start_point) + wall_direction * 100
        test_point_inward = test_point_on_wall + perp_vec * 1.0
        inward_normal = perp_vec
        if not self.floorplan_polygon.contains(Point(test_point_inward.x, test_point_inward.y)):
            inward_normal = -perp_vec

        fixture_rotation_deg = wall_angle_deg if wall_side == "left" else wall_angle_deg + 180
        
        origin = Vec2(start_point)
        y_cursor = 50.0
        margin_from_wall = 10.0

        if wall_side == "right" and fixture_queue:
            try:
                first_hybrid_name = fixture_queue[0][0]
                first_hybrid = Fixture(first_hybrid_name, self.fixture_dict[first_hybrid_name]["path"])
                y_cursor += first_hybrid.width
            except (KeyError, ValueError) as e:
                print(f"⚠️ Could not load first hybrid for right wall offset: {e}")

        print(f"--- Placing fixtures on {wall_side} wall (Angle: {wall_angle_deg:.1f}°) ---")
        print(f"ℹ️ Using globally selected mirror: '{selected_mirror_name}'")
        print(f"ℹ️ Horizontal inset for hybrid set to: {horizontal_inset_for_hybrid}mm")

        # --- Main Placement Loop ---
        for idx, (fixture_name, _) in enumerate(fixture_queue):
            try:
                hybrid = Fixture(fixture_name, self.fixture_dict[fixture_name]["path"])
                mirror = Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
            except (KeyError, ValueError) as e:
                print(f"⚠️ Could not load fixture {fixture_name} or mirror '{selected_mirror_name}': {e}")
                continue

            # A. VALIDATE HYBRID
            hybrid_offset = margin_from_wall + hybrid.height + horizontal_inset_for_hybrid
            hybrid_insert_pos = origin + (wall_direction * y_cursor) + (inward_normal * hybrid_offset)
            transform_h = Matrix44.chain(Matrix44.z_rotate(math.radians(fixture_rotation_deg)), Matrix44.translate(hybrid_insert_pos.x, hybrid_insert_pos.y, 0))
            world_corners_h = list(transform_h.transform_vertices(hybrid.bounding_box.rect_vertices()))
            poly_h = Polygon([(p.x, p.y) for p in world_corners_h])
            
            if not self.floorplan_polygon.contains(poly_h):
                print(f"⚠️ Hybrid '{fixture_name}' is outside floorplan. Stopping placement on {wall_side} wall.")
                return fixture_queue[idx:]

            aabb_h = BoundingBox2d(world_corners_h)
            if any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes):
                print(f"⚠️ Hybrid '{fixture_name}' overlaps an existing obstacle. Stopping placement on {wall_side} wall.")
                return fixture_queue[idx:]
            
            # B. VALIDATE MIRROR
            mirror_y_offset = y_cursor + hybrid.width if wall_side == "left" else y_cursor + mirror.width
            mirror_offset_from_wall = margin_from_wall + mirror.height
            mirror_insert_pos = origin + (wall_direction * mirror_y_offset) + (inward_normal * mirror_offset_from_wall)
            transform_m = Matrix44.chain(Matrix44.z_rotate(math.radians(fixture_rotation_deg)), Matrix44.translate(mirror_insert_pos.x, mirror_insert_pos.y, 0))
            world_corners_m = list(transform_m.transform_vertices(mirror.bounding_box.rect_vertices()))
            poly_m = Polygon([(p.x, p.y) for p in world_corners_m])

            if not self.floorplan_polygon.contains(poly_m):
                print(f"⚠️ Mirror is outside floorplan. Stopping placement on {wall_side} wall.")
                return fixture_queue[idx:]

            aabb_m = BoundingBox2d(world_corners_m)
            if any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes):
                print(f"⚠️ Mirror overlaps an existing obstacle. Stopping placement on {wall_side} wall.")
                return fixture_queue[idx:]

            # C. PLACE FIXTURES if both are valid
            self.place_fixture(hybrid, (hybrid_insert_pos.x, hybrid_insert_pos.y, 0), fixture_rotation_deg, True)
            self.place_fixture(mirror, (mirror_insert_pos.x, mirror_insert_pos.y, 0), fixture_rotation_deg, True)

            # D. UPDATE CURSOR FOR NEXT PAIR
            y_cursor += hybrid.width + mirror.width

        return [] # Return an empty list if all fixtures were placed successfully.


    def get_wall_angle(self, side="left"):
        """
        Computes the angle of the wall on the given side in degrees.
        Angle is measured from the positive X-axis. A vertical wall is 90 degrees.
        """
        from math import atan2, degrees
        
        # Access the floorplan's corner points (vectors) stored on the DXF_Controller.
        vectors = self.vectors
        # If no corner points exist for any reason, default to a 90-degree vertical wall.
        if not vectors: return 90.0
        
        # Convert the list of corner points into a list of line segments representing the walls.
        segments = [(vectors[i], vectors[i+1]) for i in range(len(vectors)-1)]
        segments.append((vectors[-1], vectors[0])) # Add the last segment to close the loop.

        angle_list = []
        # Define a tolerance zone (10% of the floorplan's total width) to identify wall segments
        # near the far left and far right edges.
        tolerance = (self.cvc.max_x - self.cvc.min_x) * 0.1

        # Iterate through each wall segment to find candidates.
        for start, end in segments:
            # Calculate the horizontal center of the current wall segment.
            mid_x = (start.x + end.x) / 2
            
            is_candidate = False
            # Check if the segment's midpoint falls within the tolerance zone of the requested side.
            if side == "left" and abs(mid_x - self.cvc.min_x) < tolerance:
                 is_candidate = True
            elif side == "right" and abs(mid_x - self.cvc.max_x) < tolerance:
                 is_candidate = True
            
            # If the segment is identified as a side wall:
            if is_candidate:
                wall_vec = end - start
                # To ensure consistency, we make the vector always point generally "upwards"
                # by checking if its y-component is negative.
                if wall_vec.y < 0:
                    wall_vec = -wall_vec

                if wall_vec.is_null: continue

                # Calculate the angle of the vector in radians from the positive X-axis (horizontal).
                wall_angle_rad = atan2(wall_vec.y, wall_vec.x)
                # Convert to degrees and add it to our list of potential angles.
                angle_list.append(degrees(wall_angle_rad))

        # If no suitable wall segments were found, default to a 90-degree vertical wall.
        if not angle_list:
            return 90.0

        # To be robust against small, incorrect segments, return the most frequently found angle (the mode).
        return max(set(angle_list), key=angle_list.count)

#-----------------------new function for wall_fixture placement--------------------------------------------------------------------------------------
#-----------------------new function for wall_fixture placement--------------------------------------------------------------------------------------
#-----------------------new function for wall_fixture placement--------------------------------------------------------------------------------------
    

    def place_wall_fixtures_dynamically(self):
        """
        Implements the user-specified sequential placement strategy.
        1. Splits the total fixture count between left and right walls.
        2. Places on the left wall first.
        3. Moves any unplaced left-wall fixtures to the right-wall queue.
        4. Updates the obstacle list to include the newly placed left-wall fixtures.
        5. Places the combined queue on the right wall.
        """
        import traceback
        import collections

        print("\n--- 🧠 Starting DYNAMIC Wall Fixture Placement ---")
        try:
            # 1. Get total fixture counts and create separate queues for left and right
            wall_fixtures_config = self.fixtures.get("wall_fixtures", {})
            left_wall_queue = []
            right_wall_queue = []

            print("  -> 1. Splitting total fixture counts between left and right walls...")
            for fxtr_name, total in wall_fixtures_config.items():
                if total > 0:
                    left_count = total // 2
                    right_count = total - left_count
                    if left_count > 0:
                        left_wall_queue.extend([(fxtr_name, 1)] * left_count)
                    if right_count > 0:
                        right_wall_queue.extend([(fxtr_name, 1)] * right_count)
            
            print(f"     - Initial Left Queue Size: {len(left_wall_queue)}")
            print(f"     - Initial Right Queue Size: {len(right_wall_queue)}")

            if not left_wall_queue and not right_wall_queue:
                print("ℹ️ No wall fixtures were specified for placement.")
                return

            # 2. Get geometric setup for both walls
            left_wall_angle = self.get_wall_angle("left")
            right_wall_angle = self.get_wall_angle("right")
            segments = self.cvc.get_wall_segments()
            bottom_points = self.find_bottom_segment_y_coords(segments)
            if not bottom_points:
                print("⚠️ Could not determine bottom segment. Aborting wall fixture placement.")
                return
            left_start_point, right_start_point = bottom_points

            # 3. Get initial obstacles (clinics, BOH, etc., but NOT other wall fixtures yet)
            print("\n  -> 2. Getting initial non-wall obstacles (Clinics, BOH)...")
            initial_obstacles = self._get_accurate_obstacle_bboxes(include_all=False)

            # 4. Attempt to place fixtures on the LEFT wall
            print(f"\n  -> 3. Attempting to place {len(left_wall_queue)} fixtures on the LEFT wall...")
            unplaced_from_left = self.place_wall_queue_sequentially(
                "left", 
                left_wall_queue, 
                initial_obstacles, # Check only against pre-existing items
                left_start_point, 
                left_wall_angle
            )
            
            placed_on_left_count = len(left_wall_queue) - len(unplaced_from_left)
            print(f"     - ✅ Successfully placed {placed_on_left_count} fixtures on the left wall.")

            # 5. DYNAMIC RE-QUEUEING: Move unplaced left fixtures to the right queue
            if unplaced_from_left:
                print(f"     - ⚠️ {len(unplaced_from_left)} fixtures were blocked on the left. Moving them to the right wall's queue.")
                right_wall_queue.extend(unplaced_from_left)
                print(f"     - New Right Queue Size: {len(right_wall_queue)}")

            # 6. CRITICAL: Update the obstacle list to include the fixtures just placed on the left wall
            print("\n  -> 4. Updating obstacle list to include newly placed left-wall fixtures...")
            updated_obstacles = self._get_accurate_obstacle_bboxes(include_all=True)

            # 7. Attempt to place all fixtures in the (potentially expanded) RIGHT wall queue
            print(f"\n  -> 5. Attempting to place {len(right_wall_queue)} fixtures on the RIGHT wall...")
            final_unplaced = self.place_wall_queue_sequentially(
                "right", 
                right_wall_queue, 
                updated_obstacles, # Use the NEW, complete obstacle list
                right_start_point, 
                right_wall_angle
            )

            placed_on_right_count = len(right_wall_queue) - len(final_unplaced)
            print(f"     - ✅ Successfully placed {placed_on_right_count} fixtures on the right wall.")

            # 8. Final Report
            print("\n--- Dynamic Wall Placement Complete ---")
            if final_unplaced:
                unplaced_summary = collections.Counter(name for name, _ in final_unplaced)
                print(f"⚠️ Could not place all fixtures. {len(final_unplaced)} fixtures remain unplaced: {dict(unplaced_summary)}")
            else:
                print("✅ All wall fixtures were placed successfully.")
            
        except Exception as e:
            print(f"🔥 An error occurred during dynamic wall-fixture placement: {e}")
            traceback.print_exc()
            raise


    #-----------------------new function for wall_fixture placement--------------------------------------------------------------------------------------
#-----------------------new function for wall_fixture placement--------------------------------------------------------------------------------------
#-----------------------new function for wall_fixture placement--------------------------------------------------------------------------------------
    

    def place_fixtures_on_left_wall_land(self):
        """
        Final Corrected Version: Places fixtures using a 'bench-style' search.
        For each fixture, it searches every wall segment from START to END.
        Returns any unplaced fixtures.
        """
        from Fixture import Fixture
        from shapely.geometry import Polygon, Point
        from ezdxf.math import BoundingBox2d, Vec2, Matrix44
        from ezdxf.bbox import extents
        import math
        import traceback
        import collections

        print("\n--- Placing Wall Fixtures (Pass 1: Left Wall - Forward Search) ---")
        try:
            # --- 1. SETUP ---
            wall_fixtures_config = self.fixtures.get("wall_fixtures", {})
            fixture_queue = collections.deque()
            for name, count in wall_fixtures_config.items():
                if count > 0:
                    fixture_queue.extend([(name, 1)] * count)

            if not fixture_queue:
                return collections.deque()

            mirror_config = self.fixtures.get("mirror_selection", {})
            selected_mirror_name = next((name for name, selected in mirror_config.items() if selected > 0), "mirror")
            horizontal_inset_for_hybrid = 0.0 if selected_mirror_name == "mirror_different" else 50.0

            placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
            all_segments = self.cvc.get_wall_segments(min_length=500)
            if not all_segments:
                return fixture_queue
            
            stop_entities = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper() or self.fixture_dict.get(e.dxf.name.split('_')[0].lower(), {}).get('type') == 'boh']
            stop_bboxes = []
            if stop_entities:
                for entity in stop_entities:
                    try:
                        bbox = extents([entity], fast=True)
                        stop_bboxes.append((bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y))
                    except (RuntimeError, ZeroDivisionError, TypeError):
                        continue
            
            stop_hit = False
            margin_from_wall = 10.0
            unplaced_fixtures = collections.deque()

            # --- BENCH-STYLE PLACEMENT LOOP ---
            while fixture_queue:
                if stop_hit:
                    unplaced_fixtures.extend(fixture_queue)
                    break

                item_to_try = fixture_queue.popleft()
                fixture_name, _ = item_to_try
                
                try:
                    hybrid_fxtr = Fixture(fixture_name, self.fixture_dict[fixture_name]["path"])
                    mirror_fxtr = Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
                except (KeyError, ValueError) as e:
                    unplaced_fixtures.append(item_to_try); continue

                placed_this_item = False
                print(f"\nSearching for a spot for '{hybrid_fxtr.name}'...")
                
                for i, segment in enumerate(all_segments):
                    p1, p2 = Vec2(segment[0]), Vec2(segment[1])
                    wall_vector = p2 - p1
                    wall_length = wall_vector.magnitude
                    wall_angle_rad = wall_vector.angle
                    wall_angle_deg = math.degrees(wall_angle_rad)

                    perp_vec = wall_vector.orthogonal().normalize()
                    test_point = p1 + wall_vector * 0.5 + perp_vec * 1.0
                    inward_normal = perp_vec if self.floorplan_polygon.contains(Point(test_point.x, test_point.y)) else -perp_vec

                    search_distance = 0
                    while search_distance + hybrid_fxtr.width <= wall_length:
                        footprint_start_h = p1 + wall_vector.normalize() * search_distance
                        center_on_wall_h = footprint_start_h + wall_vector.normalize() * (hybrid_fxtr.width / 2.0)
                        offset_dist_h = margin_from_wall + (hybrid_fxtr.height / 2.0) + horizontal_inset_for_hybrid
                        target_center_h = center_on_wall_h + inward_normal * offset_dist_h
                        local_center_h = hybrid_fxtr.bounding_box.center
                        transform_h = Matrix44.chain(Matrix44.translate(-local_center_h.x, -local_center_h.y, 0), Matrix44.z_rotate(wall_angle_rad), Matrix44.translate(target_center_h.x, target_center_h.y, 0))
                        rotated_offset_h = local_center_h.rotate(wall_angle_rad)
                        final_insert_point_h = target_center_h - rotated_offset_h
                        world_corners_h = list(transform_h.transform_vertices(hybrid_fxtr.bounding_box.rect_vertices()))
                        poly_h = Polygon([(p.x, p.y) for p in world_corners_h])
                        aabb_h = BoundingBox2d(world_corners_h)

                        if any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in stop_bboxes):
                            stop_hit = True; break

                        hybrid_is_valid = self.floorplan_polygon.contains(poly_h) and not any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                        if hybrid_is_valid:
                            mirror_search_dist = search_distance + hybrid_fxtr.width
                            mirror_is_valid = False
                            if mirror_search_dist + mirror_fxtr.width <= wall_length:
                                footprint_start_m = p1 + wall_vector.normalize() * mirror_search_dist
                                center_on_wall_m = footprint_start_m + wall_vector.normalize() * (mirror_fxtr.width / 2.0)
                                offset_dist_m = margin_from_wall + (mirror_fxtr.height / 2.0)
                                target_center_m = center_on_wall_m + inward_normal * offset_dist_m
                                local_center_m = mirror_fxtr.bounding_box.center
                                transform_m = Matrix44.chain(Matrix44.translate(-local_center_m.x, -local_center_m.y, 0), Matrix44.z_rotate(wall_angle_rad), Matrix44.translate(target_center_m.x, target_center_m.y, 0))
                                rotated_offset_m = local_center_m.rotate(wall_angle_rad)
                                final_insert_point_m = target_center_m - rotated_offset_m
                                world_corners_m = list(transform_m.transform_vertices(mirror_fxtr.bounding_box.rect_vertices()))
                                poly_m = Polygon([(p.x, p.y) for p in world_corners_m])
                                aabb_m = BoundingBox2d(world_corners_m)
                                mirror_is_valid = self.floorplan_polygon.contains(poly_m) and not any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                            if mirror_is_valid:
                                self.place_fixture(hybrid_fxtr, (final_insert_point_h.x, final_insert_point_h.y, 0), wall_angle_deg, True)
                                placed_bboxes.append((aabb_h.extmin.x, aabb_h.extmin.y, aabb_h.extmax.x, aabb_h.extmax.y))
                                self.place_fixture(mirror_fxtr, (final_insert_point_m.x, final_insert_point_m.y, 0), wall_angle_deg, True)
                                placed_bboxes.append((aabb_m.extmin.x, aabb_m.extmin.y, aabb_m.extmax.x, aabb_m.extmax.y))
                            else:
                                self.place_fixture(hybrid_fxtr, (final_insert_point_h.x, final_insert_point_h.y, 0), wall_angle_deg, True)
                                placed_bboxes.append((aabb_h.extmin.x, aabb_h.extmin.y, aabb_h.extmax.x, aabb_h.extmax.y))
                            
                            placed_this_item = True
                            break 

                        search_distance += 100.0
                    
                    if placed_this_item or stop_hit: break
                
                if not placed_this_item:
                    unplaced_fixtures.append(item_to_try)

            if stop_hit:
                print(f"\nℹ️ Left wall placement stopped. Passing {len(unplaced_fixtures)} items to the right wall.")
            
            return unplaced_fixtures

        except Exception as e:
            print(f"🔥 An error occurred during left wall placement: {e}")
            traceback.print_exc()
            return fixture_queue


    def _get_reordered_corners_right_bottom_wall_land(self):
        """
        Helper function to get corners starting from the bottom-most point of the
        right-most vertical wall, ensuring a COUNTER-CLOCKWISE (CCW) path.
        """
        if not hasattr(self, 'vectors') or not self.vectors:
            return []
        
        corners = [(v.x, v.y) for v in self.vectors]
        
        # --- 1. Find all nearly vertical wall segments ---
        all_segments = [(Vec2(corners[i]), Vec2(corners[(i + 1) % len(corners)])) for i in range(len(corners))]
        vertical_segments = []
        for p1, p2 in all_segments:
            if p1.distance(p2) == 0: continue
            angle = abs(math.degrees((p2 - p1).angle))
            if (80 < angle < 100) or (260 < angle < 280):
                vertical_segments.append((p1, p2))

        if not vertical_segments:
            # Fallback if no vertical walls are found (highly unlikely)
            max_x = max(c[0] for c in corners)
            min_y = min(c[1] for c in corners)
            start_idx = min(range(len(corners)), key=lambda i: ((corners[i][0] - max_x)**2 + (corners[i][1] - min_y)**2))
        else:
            # --- 2. Find the right-most of the vertical walls ---
            rightmost_wall = max(vertical_segments, key=lambda seg: (seg[0].x + seg[1].x) / 2)
            
            # --- 3. Find the bottom point of that specific wall ---
            p1, p2 = rightmost_wall
            start_point_vec = p1 if p1.y < p2.y else p2
            
            # --- 4. Find the index of that exact point in the master list ---
            start_idx = min(range(len(corners)), key=lambda i: start_point_vec.distance(Vec2(corners[i])))

        # Reorder the list to start from our calculated index
        reordered = corners[start_idx:] + corners[:start_idx]
        
        # --- 5. CRITICAL: Ensure Counter-Clockwise (CCW) Order ---
        signed_area = 0.5 * sum(x1*y2 - x2*y1 for (x1, y1), (x2, y2) in zip(reordered, reordered[1:] + [reordered[0]]))
        if signed_area < 0: # If area is negative, it's Clockwise (CW)
            print("  -> Path was clockwise, reversing to ensure correct direction (up the right wall).")
            reordered = reordered[0:1] + reordered[1:][::-1] # Reverse list while keeping start point
            
        return reordered

    # In DXF_Controller.py, replace ONLY the place_fixtures_on_right_wall function

    def place_fixtures_on_right_wall_land(self, fixture_queue: collections.deque):
        """
        FINAL CORRECTED VERSION: Places fixtures on a precise path starting from the
        bottom-right, moving up the right wall, and then along the top.
        - Uses a robust wall filter to correctly handle complex, recessed walls.
        - Includes full, correct logic for mirror pairing and flexible placement.
        """
        from Fixture import Fixture
        from shapely.geometry import Polygon, Point, box
        from ezdxf.math import BoundingBox2d, Vec2, Matrix44
        from ezdxf.bbox import extents
        import math

        print("\n--- Placing Wall Fixtures (Pass 2: Right -> Top Path - Final Version) ---")
        if not fixture_queue:
            return

        # --- 1. Setup ---
        placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
        mirror_config = self.fixtures.get("mirror_selection", {})
        selected_mirror_name = next((name for name, selected in mirror_config.items() if selected > 0), "mirror")
        horizontal_inset_for_hybrid = 0.0 if selected_mirror_name == "mirror_different" else 50.0

        # --- 2. Create the EXACT Placement Path ---
        ordered_corners = self._get_reordered_corners_right_bottom_wall_land()
        perimeter_path = []
        for i in range(len(ordered_corners)):
            p1 = Vec2(ordered_corners[i])
            p2 = Vec2(ordered_corners[(i + 1) % len(ordered_corners)])
            if p1.distance(p2) > 100:
                perimeter_path.append((p1, p2))

        # --- 3. Main Placement Loop ---
        margin_from_wall = 10.0
        unplaced_fixtures_final = collections.deque()
        
        while fixture_queue:
            item_to_try = fixture_queue[0]
            fixture_name, _ = item_to_try
            try:
                hybrid_fxtr = Fixture(fixture_name, self.fixture_dict[fixture_name]["path"])
                mirror_fxtr = Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
            except (KeyError, ValueError) as e:
                fixture_queue.popleft(); continue

            placed_this_item = False
            print(f"  -> Searching for a spot for '{hybrid_fxtr.name}'...")

            for segment_start, segment_end in perimeter_path:
                
                # *** ROBUST WALL FILTER (RESTORED) ***
                segment_vec = segment_end - segment_start
                if segment_vec.magnitude == 0: continue
                angle = abs(math.degrees(segment_vec.angle))
                mid_x = (segment_start.x + segment_end.x) / 2
                mid_y = (segment_start.y + segment_end.y) / 2
                
                is_vertical = (75 < angle < 105) or (255 < angle < 285)
                is_horizontal = (angle < 15) or (angle > 165)

                is_left_wall = is_vertical and (abs(mid_x - self.cvc.min_x) < (self.cvc.max_x - self.cvc.min_x) * 0.15)
                is_bottom_wall = is_horizontal and (abs(mid_y - self.cvc.min_y) < (self.cvc.max_y - self.cvc.min_y) * 0.15)

                if is_left_wall or is_bottom_wall:
                    continue
                # *** END OF FILTER ***
                
                segment_vector = segment_vec.normalize()
                segment_length = segment_start.distance(segment_end)
                wall_angle_deg = math.degrees(segment_vector.angle)
                
                inward_normal = segment_vector.orthogonal()
                if not self.floorplan_polygon.contains(Point(segment_start + inward_normal)):
                    inward_normal = -inward_normal

                fixture_rotation_deg = wall_angle_deg
                if inward_normal.x < -0.1:
                    fixture_rotation_deg += 180

                cursor = 50.0
                while cursor + hybrid_fxtr.width < segment_length:
                    # A. VALIDATE HYBRID
                    footprint_start_h = segment_start + segment_vector * cursor
                    center_on_wall_h = footprint_start_h + segment_vector * (hybrid_fxtr.width / 2.0)
                    offset_dist_h = margin_from_wall + (hybrid_fxtr.height / 2.0) + horizontal_inset_for_hybrid
                    target_center_h = center_on_wall_h + inward_normal * offset_dist_h
                    local_center_h = hybrid_fxtr.bounding_box.center
                    transform_h = Matrix44.chain(Matrix44.translate(-local_center_h.x, -local_center_h.y, 0), Matrix44.z_rotate(math.radians(fixture_rotation_deg)), Matrix44.translate(target_center_h.x, target_center_h.y, 0))
                    world_corners_h = list(transform_h.transform_vertices(hybrid_fxtr.bounding_box.rect_vertices()))
                    poly_h = Polygon([(p.x, p.y) for p in world_corners_h])
                    aabb_h = BoundingBox2d(world_corners_h)
                    hybrid_is_valid = self.floorplan_polygon.contains(poly_h) and not any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                    if hybrid_is_valid:
                        # --- B. VALIDATE AND PLACE MIRROR (FULL LOGIC) ---
                        mirror_is_valid = False
                        mirror_cursor_start = cursor + hybrid_fxtr.width
                        if mirror_cursor_start + mirror_fxtr.width <= segment_length:
                            footprint_start_m = segment_start + segment_vector * mirror_cursor_start
                            center_on_wall_m = footprint_start_m + segment_vector * (mirror_fxtr.width / 2.0)
                            offset_dist_m = margin_from_wall + (mirror_fxtr.height / 2.0)
                            target_center_m = center_on_wall_m + inward_normal * offset_dist_m
                            local_center_m = mirror_fxtr.bounding_box.center
                            transform_m = Matrix44.chain(Matrix44.translate(-local_center_m.x, -local_center_m.y, 0), Matrix44.z_rotate(math.radians(fixture_rotation_deg)), Matrix44.translate(target_center_m.x, target_center_m.y, 0))
                            world_corners_m = list(transform_m.transform_vertices(mirror_fxtr.bounding_box.rect_vertices()))
                            poly_m = Polygon([(p.x, p.y) for p in world_corners_m])
                            aabb_m = BoundingBox2d(world_corners_m)
                            if self.floorplan_polygon.contains(poly_m) and not any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes):
                                mirror_is_valid = True

                        # C. EXECUTE PLACEMENT
                        fixture_queue.popleft()
                        placed_this_item = True
                        
                        rotated_offset_h = local_center_h.rotate(math.radians(fixture_rotation_deg))
                        final_insert_point_h = target_center_h - rotated_offset_h
                        self.place_fixture(hybrid_fxtr, (final_insert_point_h.x, final_insert_point_h.y, 0), fixture_rotation_deg, True)
                        placed_bboxes.append((aabb_h.extmin.x, aabb_h.extmin.y, aabb_h.extmax.x, aabb_h.extmax.y))

                        if mirror_is_valid:
                            rotated_offset_m = local_center_m.rotate(math.radians(fixture_rotation_deg))
                            final_insert_point_m = target_center_m - rotated_offset_m
                            self.place_fixture(mirror_fxtr, (final_insert_point_m.x, final_insert_point_m.y, 0), fixture_rotation_deg, True)
                            placed_bboxes.append((aabb_m.extmin.x, aabb_m.extmin.y, aabb_m.extmax.x, aabb_m.extmax.y))
                            print(f"    -> ✅ Placed pair '{hybrid_fxtr.name}' & '{mirror_fxtr.name}'.")
                        else:
                            print(f"    -> ✅ Placed '{hybrid_fxtr.name}' alone (mirror blocked).")
                        
                        break
                    
                    cursor += 100.0
                
                if placed_this_item:
                    break
            
            if not placed_this_item:
                unplaced_fixtures_final.append(fixture_queue.popleft())

        # --- Final Report ---
        if unplaced_fixtures_final:
            print(f"\n⚠️ Finished placement. Could not place {len(unplaced_fixtures_final)} fixtures.")
        else:
            print("\n✅ Finished placement. All remaining fixtures were placed.")
            
#-----------------------new function for wall_fixture placement--------------------------------------------------------------------------------------
#-----------------------new function for wall_fixture placement--------------------------------------------------------------------------------------
#-----------------------new function for wall_fixture placement--------------------------------------------------------------------------------------


    def place_fixtures_on_left_wall_og(self):
        """
        Final Corrected Version: Places fixtures using a 'bench-style' search.
        For each fixture, it searches every wall segment from START to END.
        Returns any unplaced fixtures.
        """
        from Fixture import Fixture
        from shapely.geometry import Polygon, Point
        from ezdxf.math import BoundingBox2d, Vec2, Matrix44
        from ezdxf.bbox import extents
        import math
        import traceback
        import collections

        print("\n--- Placing Wall Fixtures (Pass 1: Left Wall - Forward Search) ---")
        try:
            # --- 1. SETUP ---
            wall_fixtures_config = self.fixtures.get("wall_fixtures", {})
            fixture_queue = collections.deque()
            for name, count in wall_fixtures_config.items():
                if count > 0:
                    fixture_queue.extend([(name, 1)] * count)

            if not fixture_queue:
                return collections.deque()

            mirror_config = self.fixtures.get("mirror_selection", {})
            selected_mirror_name = next((name for name, selected in mirror_config.items() if selected > 0), "mirror")
            horizontal_inset_for_hybrid = 0.0 if selected_mirror_name == "mirror_different" else 50.0

            placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
            all_segments = self.cvc.get_wall_segments(min_length=500)
            if not all_segments:
                return fixture_queue
            
            stop_entities = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper() or self.fixture_dict.get(e.dxf.name.split('_')[0].lower(), {}).get('type') == 'boh']
            stop_bboxes = []
            if stop_entities:
                for entity in stop_entities:
                    try:
                        bbox = extents([entity], fast=True)
                        stop_bboxes.append((bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y))
                    except (RuntimeError, ZeroDivisionError, TypeError):
                        continue
            
            stop_hit = False
            margin_from_wall = 10.0
            unplaced_fixtures = collections.deque()

            # --- BENCH-STYLE PLACEMENT LOOP ---
            while fixture_queue:
                if stop_hit:
                    unplaced_fixtures.extend(fixture_queue)
                    break

                item_to_try = fixture_queue.popleft()
                fixture_name, _ = item_to_try
                
                try:
                    hybrid_fxtr = Fixture(fixture_name, self.fixture_dict[fixture_name]["path"])
                    mirror_fxtr = Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
                except (KeyError, ValueError) as e:
                    unplaced_fixtures.append(item_to_try); continue

                placed_this_item = False
                print(f"\nSearching for a spot for '{hybrid_fxtr.name}'...")
                
                for i, segment in enumerate(all_segments):
                    p1, p2 = Vec2(segment[0]), Vec2(segment[1])
                    wall_vector = p2 - p1
                    wall_length = wall_vector.magnitude
                    wall_angle_rad = wall_vector.angle
                    wall_angle_deg = math.degrees(wall_angle_rad)

                    perp_vec = wall_vector.orthogonal().normalize()
                    test_point = p1 + wall_vector * 0.5 + perp_vec * 1.0
                    inward_normal = perp_vec if self.floorplan_polygon.contains(Point(test_point.x, test_point.y)) else -perp_vec

                    search_distance = 0
                    while search_distance + hybrid_fxtr.width <= wall_length:
                        footprint_start_h = p1 + wall_vector.normalize() * search_distance
                        center_on_wall_h = footprint_start_h + wall_vector.normalize() * (hybrid_fxtr.width / 2.0)
                        offset_dist_h = margin_from_wall + (hybrid_fxtr.height / 2.0) + horizontal_inset_for_hybrid
                        target_center_h = center_on_wall_h + inward_normal * offset_dist_h
                        local_center_h = hybrid_fxtr.bounding_box.center
                        transform_h = Matrix44.chain(Matrix44.translate(-local_center_h.x, -local_center_h.y, 0), Matrix44.z_rotate(wall_angle_rad), Matrix44.translate(target_center_h.x, target_center_h.y, 0))
                        rotated_offset_h = local_center_h.rotate(wall_angle_rad)
                        final_insert_point_h = target_center_h - rotated_offset_h
                        world_corners_h = list(transform_h.transform_vertices(hybrid_fxtr.bounding_box.rect_vertices()))
                        poly_h = Polygon([(p.x, p.y) for p in world_corners_h])
                        aabb_h = BoundingBox2d(world_corners_h)

                        if any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in stop_bboxes):
                            stop_hit = True; break

                        hybrid_is_valid = self.floorplan_polygon.contains(poly_h) and not any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                        if hybrid_is_valid:
                            mirror_search_dist = search_distance + hybrid_fxtr.width
                            mirror_is_valid = False
                            if mirror_search_dist + mirror_fxtr.width <= wall_length:
                                footprint_start_m = p1 + wall_vector.normalize() * mirror_search_dist
                                center_on_wall_m = footprint_start_m + wall_vector.normalize() * (mirror_fxtr.width / 2.0)
                                offset_dist_m = margin_from_wall + (mirror_fxtr.height / 2.0)
                                target_center_m = center_on_wall_m + inward_normal * offset_dist_m
                                local_center_m = mirror_fxtr.bounding_box.center
                                transform_m = Matrix44.chain(Matrix44.translate(-local_center_m.x, -local_center_m.y, 0), Matrix44.z_rotate(wall_angle_rad), Matrix44.translate(target_center_m.x, target_center_m.y, 0))
                                rotated_offset_m = local_center_m.rotate(wall_angle_rad)
                                final_insert_point_m = target_center_m - rotated_offset_m
                                world_corners_m = list(transform_m.transform_vertices(mirror_fxtr.bounding_box.rect_vertices()))
                                poly_m = Polygon([(p.x, p.y) for p in world_corners_m])
                                aabb_m = BoundingBox2d(world_corners_m)
                                mirror_is_valid = self.floorplan_polygon.contains(poly_m) and not any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                            if mirror_is_valid:
                                self.place_fixture(hybrid_fxtr, (final_insert_point_h.x, final_insert_point_h.y, 0), wall_angle_deg, True)
                                placed_bboxes.append((aabb_h.extmin.x, aabb_h.extmin.y, aabb_h.extmax.x, aabb_h.extmax.y))
                                self.place_fixture(mirror_fxtr, (final_insert_point_m.x, final_insert_point_m.y, 0), wall_angle_deg, True)
                                placed_bboxes.append((aabb_m.extmin.x, aabb_m.extmin.y, aabb_m.extmax.x, aabb_m.extmax.y))
                            else:
                                self.place_fixture(hybrid_fxtr, (final_insert_point_h.x, final_insert_point_h.y, 0), wall_angle_deg, True)
                                placed_bboxes.append((aabb_h.extmin.x, aabb_h.extmin.y, aabb_h.extmax.x, aabb_h.extmax.y))
                            
                            placed_this_item = True
                            break 

                        search_distance += 100.0
                    
                    if placed_this_item or stop_hit: break
                
                if not placed_this_item:
                    unplaced_fixtures.append(item_to_try)

            if stop_hit:
                print(f"\nℹ️ Left wall placement stopped. Passing {len(unplaced_fixtures)} items to the right wall.")
            
            return unplaced_fixtures

        except Exception as e:
            print(f"🔥 An error occurred during left wall placement: {e}")
            traceback.print_exc()
            return fixture_queue


    def _get_reordered_corners_right_bottom_wall(self):
        """
        Helper function to get corners starting from the bottom-most point of the
        right-most vertical wall, ensuring a COUNTER-CLOCKWISE (CCW) path.
        """
        if not hasattr(self, 'vectors') or not self.vectors:
            return []
        
        corners = [(v.x, v.y) for v in self.vectors]
        
        # --- 1. Find all nearly vertical wall segments ---
        all_segments = [(Vec2(corners[i]), Vec2(corners[(i + 1) % len(corners)])) for i in range(len(corners))]
        vertical_segments = []
        for p1, p2 in all_segments:
            if p1.distance(p2) == 0: continue
            angle = abs(math.degrees((p2 - p1).angle))
            if (80 < angle < 100) or (260 < angle < 280):
                vertical_segments.append((p1, p2))

        if not vertical_segments:
            # Fallback if no vertical walls are found (highly unlikely)
            max_x = max(c[0] for c in corners)
            min_y = min(c[1] for c in corners)
            start_idx = min(range(len(corners)), key=lambda i: ((corners[i][0] - max_x)**2 + (corners[i][1] - min_y)**2))
        else:
            # --- 2. Find the right-most of the vertical walls ---
            rightmost_wall = max(vertical_segments, key=lambda seg: (seg[0].x + seg[1].x) / 2)
            
            # --- 3. Find the bottom point of that specific wall ---
            p1, p2 = rightmost_wall
            start_point_vec = p1 if p1.y < p2.y else p2
            
            # --- 4. Find the index of that exact point in the master list ---
            start_idx = min(range(len(corners)), key=lambda i: start_point_vec.distance(Vec2(corners[i])))

        # Reorder the list to start from our calculated index
        reordered = corners[start_idx:] + corners[:start_idx]
        
        # --- 5. CRITICAL: Ensure Counter-Clockwise (CCW) Order ---
        signed_area = 0.5 * sum(x1*y2 - x2*y1 for (x1, y1), (x2, y2) in zip(reordered, reordered[1:] + [reordered[0]]))
        if signed_area < 0: # If area is negative, it's Clockwise (CW)
            print("  -> Path was clockwise, reversing to ensure correct direction (up the right wall).")
            reordered = reordered[0:1] + reordered[1:][::-1] # Reverse list while keeping start point
            
        return reordered

    # In DXF_Controller.py, replace ONLY the place_fixtures_on_right_wall function

    def place_fixtures_on_right_wall(self, fixture_queue: collections.deque):
        """
        FINAL CORRECTED VERSION: Places fixtures on a precise path starting from the
        bottom-right, moving up the right wall, and then along the top.
        - Uses a robust wall filter to correctly handle complex, recessed walls.
        - Includes full, correct logic for mirror pairing and flexible placement.
        """
        from Fixture import Fixture
        from shapely.geometry import Polygon, Point, box
        from ezdxf.math import BoundingBox2d, Vec2, Matrix44
        from ezdxf.bbox import extents
        import math

        print("\n--- Placing Wall Fixtures (Pass 2: Right -> Top Path - Final Version) ---")
        if not fixture_queue:
            return

        # --- 1. Setup ---
        placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
        mirror_config = self.fixtures.get("mirror_selection", {})
        selected_mirror_name = next((name for name, selected in mirror_config.items() if selected > 0), "mirror")
        horizontal_inset_for_hybrid = 0.0 if selected_mirror_name == "mirror_different" else 50.0

        # --- 2. Create the EXACT Placement Path ---
        ordered_corners = self._get_reordered_corners_right_bottom_wall()
        perimeter_path = []
        for i in range(len(ordered_corners)):
            p1 = Vec2(ordered_corners[i])
            p2 = Vec2(ordered_corners[(i + 1) % len(ordered_corners)])
            if p1.distance(p2) > 100:
                perimeter_path.append((p1, p2))

        # --- 3. Main Placement Loop ---
        margin_from_wall = 10.0
        unplaced_fixtures_final = collections.deque()
        
        while fixture_queue:
            item_to_try = fixture_queue[0]
            fixture_name, _ = item_to_try
            try:
                hybrid_fxtr = Fixture(fixture_name, self.fixture_dict[fixture_name]["path"])
                mirror_fxtr = Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
            except (KeyError, ValueError) as e:
                fixture_queue.popleft(); continue

            placed_this_item = False
            print(f"  -> Searching for a spot for '{hybrid_fxtr.name}'...")

            for segment_start, segment_end in perimeter_path:
                
                # *** ROBUST WALL FILTER (RESTORED) ***
                segment_vec = segment_end - segment_start
                if segment_vec.magnitude == 0: continue
                angle = abs(math.degrees(segment_vec.angle))
                mid_x = (segment_start.x + segment_end.x) / 2
                mid_y = (segment_start.y + segment_end.y) / 2
                
                is_vertical = (75 < angle < 105) or (255 < angle < 285)
                is_horizontal = (angle < 15) or (angle > 165)

                is_left_wall = is_vertical and (abs(mid_x - self.cvc.min_x) < (self.cvc.max_x - self.cvc.min_x) * 0.15)
                is_bottom_wall = is_horizontal and (abs(mid_y - self.cvc.min_y) < (self.cvc.max_y - self.cvc.min_y) * 0.15)

                if is_left_wall or is_bottom_wall:
                    continue
                # *** END OF FILTER ***
                
                segment_vector = segment_vec.normalize()
                segment_length = segment_start.distance(segment_end)
                wall_angle_deg = math.degrees(segment_vector.angle)
                
                inward_normal = segment_vector.orthogonal()
                if not self.floorplan_polygon.contains(Point(segment_start + inward_normal)):
                    inward_normal = -inward_normal

                fixture_rotation_deg = wall_angle_deg
                if inward_normal.x < -0.1:
                    fixture_rotation_deg += 180

                cursor = 50.0
                while cursor + hybrid_fxtr.width < segment_length:
                    # A. VALIDATE HYBRID
                    footprint_start_h = segment_start + segment_vector * cursor
                    center_on_wall_h = footprint_start_h + segment_vector * (hybrid_fxtr.width / 2.0)
                    offset_dist_h = margin_from_wall + (hybrid_fxtr.height / 2.0) + horizontal_inset_for_hybrid
                    target_center_h = center_on_wall_h + inward_normal * offset_dist_h
                    local_center_h = hybrid_fxtr.bounding_box.center
                    transform_h = Matrix44.chain(Matrix44.translate(-local_center_h.x, -local_center_h.y, 0), Matrix44.z_rotate(math.radians(fixture_rotation_deg)), Matrix44.translate(target_center_h.x, target_center_h.y, 0))
                    world_corners_h = list(transform_h.transform_vertices(hybrid_fxtr.bounding_box.rect_vertices()))
                    poly_h = Polygon([(p.x, p.y) for p in world_corners_h])
                    aabb_h = BoundingBox2d(world_corners_h)
                    hybrid_is_valid = self.floorplan_polygon.contains(poly_h) and not any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                    if hybrid_is_valid:
                        # --- B. VALIDATE AND PLACE MIRROR (FULL LOGIC) ---
                        mirror_is_valid = False
                        mirror_cursor_start = cursor + hybrid_fxtr.width
                        if mirror_cursor_start + mirror_fxtr.width <= segment_length:
                            footprint_start_m = segment_start + segment_vector * mirror_cursor_start
                            center_on_wall_m = footprint_start_m + segment_vector * (mirror_fxtr.width / 2.0)
                            offset_dist_m = margin_from_wall + (mirror_fxtr.height / 2.0)
                            target_center_m = center_on_wall_m + inward_normal * offset_dist_m
                            local_center_m = mirror_fxtr.bounding_box.center
                            transform_m = Matrix44.chain(Matrix44.translate(-local_center_m.x, -local_center_m.y, 0), Matrix44.z_rotate(math.radians(fixture_rotation_deg)), Matrix44.translate(target_center_m.x, target_center_m.y, 0))
                            world_corners_m = list(transform_m.transform_vertices(mirror_fxtr.bounding_box.rect_vertices()))
                            poly_m = Polygon([(p.x, p.y) for p in world_corners_m])
                            aabb_m = BoundingBox2d(world_corners_m)
                            if self.floorplan_polygon.contains(poly_m) and not any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes):
                                mirror_is_valid = True

                        # C. EXECUTE PLACEMENT
                        fixture_queue.popleft()
                        placed_this_item = True
                        
                        rotated_offset_h = local_center_h.rotate(math.radians(fixture_rotation_deg))
                        final_insert_point_h = target_center_h - rotated_offset_h
                        self.place_fixture(hybrid_fxtr, (final_insert_point_h.x, final_insert_point_h.y, 0), fixture_rotation_deg, True)
                        placed_bboxes.append((aabb_h.extmin.x, aabb_h.extmin.y, aabb_h.extmax.x, aabb_h.extmax.y))

                        if mirror_is_valid:
                            rotated_offset_m = local_center_m.rotate(math.radians(fixture_rotation_deg))
                            final_insert_point_m = target_center_m - rotated_offset_m
                            self.place_fixture(mirror_fxtr, (final_insert_point_m.x, final_insert_point_m.y, 0), fixture_rotation_deg, True)
                            placed_bboxes.append((aabb_m.extmin.x, aabb_m.extmin.y, aabb_m.extmax.x, aabb_m.extmax.y))
                            print(f"    -> ✅ Placed pair '{hybrid_fxtr.name}' & '{mirror_fxtr.name}'.")
                        else:
                            print(f"    -> ✅ Placed '{hybrid_fxtr.name}' alone (mirror blocked).")
                        
                        break
                    
                    cursor += 100.0
                
                if placed_this_item:
                    break
            
            if not placed_this_item:
                unplaced_fixtures_final.append(fixture_queue.popleft())

        # --- Final Report ---
        if unplaced_fixtures_final:
            print(f"\n⚠️ Finished placement. Could not place {len(unplaced_fixtures_final)} fixtures.")
        else:
            print("\n✅ Finished placement. All remaining fixtures were placed.")
            
#-----------------------new function for wall_fixture placement--------------------------------------------------------------------------------------
#-----------------------new function for wall_fixture placement--------------------------------------------------------------------------------------
#-----------------------new function for wall_fixture placement--------------------------------------------------------------------------------------


    def place_bench_fixtures(self):
        """
        Places bench fixtures along available wall segments with robust geometry calculations.
        """
        print("\n--- Attempting to place Bench Fixtures ---")
        try:
            bench_config = self.fixtures.get("Bench_fixtures", {})
            if not any(bench_config.values()):
                print("ℹ️ No bench fixtures specified for placement.")
                return

            placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
            
            benches_to_place = []
            for name, count in bench_config.items():
                if count > 0:
                    try:
                        fxtr = Fixture.Fixture(name, self.fixture_dict[name]["path"])
                        benches_to_place.extend([fxtr] * count)
                    except (KeyError, ValueError) as e:
                        print(f"⚠️ Warning: Bench fixture '{name}' could not be loaded: {e}")
            
            if not benches_to_place:
                return

            all_segments = self.cvc.get_wall_segments(min_length=500)
            if not all_segments:
                print("⚠️ No suitable wall segments found. Try reducing min_length in get_wall_segments.")
                return

            benches_placed_count = 0
            for bench in benches_to_place:
                print(f"\nSearching for a spot for '{bench.name}' (Width: {bench.width:.0f}mm)...")
                is_bench_placed = False
                for i, segment in enumerate(all_segments):
                    p1, p2 = Vec2(segment[0]), Vec2(segment[1])
                    wall_vector = p2 - p1
                    wall_length = wall_vector.magnitude
                    
                    if wall_length < bench.width:
                        continue

                    wall_angle_rad = wall_vector.angle
                    wall_angle_deg = math.degrees(wall_angle_rad)
                    
                    perp_vec = wall_vector.orthogonal().normalize()
                    test_point = p1 + wall_vector * 0.5 + perp_vec * 1.0
                    inward_normal = perp_vec if self.floorplan_polygon.contains(Point(test_point.x, test_point.y)) else -perp_vec

                    search_distance = 0
                    while search_distance + bench.width <= wall_length:
                        margin_from_wall = 20.0
                        
                        # --- New Robust Geometry and Transformation Logic ---
                        
                        # 1. Calculate the DESIRED CENTER of the bench in world coordinates.
                        footprint_start_on_wall = p1 + wall_vector.normalize() * search_distance
                        footprint_center_on_wall = footprint_start_on_wall + wall_vector.normalize() * (bench.width / 2.0)
                        offset_dist = margin_from_wall + (bench.height / 2.0)
                        target_center_wcs = footprint_center_on_wall + inward_normal * offset_dist

                        # 2. Get the geometric center of the bench in its own LOCAL file coordinates.
                        local_center = bench.bounding_box.center

                        # 3. Create a robust transformation matrix for validation.
                        # This correctly handles fixtures that are not centered at (0,0) in their own DXF file.
                        transform = Matrix44.chain(
                            Matrix44.translate(-local_center.x, -local_center.y, 0), # Move local center to origin
                            Matrix44.z_rotate(wall_angle_rad),                      # Rotate around origin
                            Matrix44.translate(target_center_wcs.x, target_center_wcs.y, 0) # Move to final world position
                        )
                        
                        # 4. Calculate the final insertion point for the place_fixture function.
                        # This point is where the block's origin (0,0) must be placed so its geometry lands correctly.
                        rotated_offset = local_center.rotate(wall_angle_rad)
                        final_insert_point = target_center_wcs - rotated_offset
                        
                        # --- End of New Logic ---

                        world_corners = list(transform.transform_vertices(bench.bounding_box.rect_vertices()))
                        bench_polygon = Polygon([(p.x, p.y) for p in world_corners])
                        bench_aabb = BoundingBox2d(world_corners)

                        is_inside = self.floorplan_polygon.contains(bench_polygon)
                        is_overlapping = any(bench_aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                        if is_inside and not is_overlapping:
                            self.place_fixture(bench, (final_insert_point.x, final_insert_point.y, 0), wall_angle_deg, True)
                            print(f"  ✅ SUCCESS: Placed '{bench.name}'.")
                            placed_bboxes.append((bench_aabb.extmin.x, bench_aabb.extmin.y, bench_aabb.extmax.x, bench_aabb.extmax.y))
                            benches_placed_count += 1
                            is_bench_placed = True
                            break
                        
                        search_distance += 100 
                    
                    if is_bench_placed:
                        break

                if not is_bench_placed:
                    print(f"⚠️ Could not find a valid position for bench '{bench.name}' on any wall.")
            
            print(f"-> Placed {benches_placed_count} of {len(benches_to_place)} requested benches.")

        except Exception as e:
            print(f"🔥 An error occurred during bench placement: {e}")
            traceback.print_exc()
            raise


    def place_lensometer(self):
        """
        Places lensometer fixtures along available wall segments with robust geometry calculations.
        """
        print("\n--- Attempting to place lensometer Fixtures ---")
        try:
            bench_config = self.fixtures.get("lensometer_fixtures", {})
            if not any(bench_config.values()):
                print("ℹ️ No lensometer fixtures specified for placement.")
                return

            placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
            
            benches_to_place = []
            for name, count in bench_config.items():
                if count > 0:
                    try:
                        fxtr = Fixture.Fixture(name, self.fixture_dict[name]["path"])
                        benches_to_place.extend([fxtr] * count)
                    except (KeyError, ValueError) as e:
                        print(f"⚠️ Warning: lensometer fixture '{name}' could not be loaded: {e}")
            
            if not benches_to_place:
                return

            all_segments = self.cvc.get_wall_segments(min_length=500)
            if not all_segments:
                print("⚠️ No suitable wall segments found. Try reducing min_length in get_wall_segments.")
                return

            benches_placed_count = 0
            for bench in benches_to_place:
                print(f"\nSearching for a spot for '{bench.name}' (Width: {bench.width:.0f}mm)...")
                is_bench_placed = False
                for i, segment in enumerate(all_segments):
                    p1, p2 = Vec2(segment[0]), Vec2(segment[1])
                    wall_vector = p2 - p1
                    wall_length = wall_vector.magnitude
                    
                    if wall_length < bench.width:
                        continue

                    wall_angle_rad = wall_vector.angle
                    wall_angle_deg = math.degrees(wall_angle_rad)
                    
                    perp_vec = wall_vector.orthogonal().normalize()
                    test_point = p1 + wall_vector * 0.5 + perp_vec * 1.0
                    inward_normal = perp_vec if self.floorplan_polygon.contains(Point(test_point.x, test_point.y)) else -perp_vec

                    search_distance = 0
                    while search_distance + bench.width <= wall_length:
                        margin_from_wall = 20.0
                        
                        # --- New Robust Geometry and Transformation Logic ---
                        
                        # 1. Calculate the DESIRED CENTER of the bench in world coordinates.
                        footprint_start_on_wall = p1 + wall_vector.normalize() * search_distance
                        footprint_center_on_wall = footprint_start_on_wall + wall_vector.normalize() * (bench.width / 2.0)
                        offset_dist = margin_from_wall + (bench.height / 2.0)
                        target_center_wcs = footprint_center_on_wall + inward_normal * offset_dist

                        # 2. Get the geometric center of the bench in its own LOCAL file coordinates.
                        local_center = bench.bounding_box.center

                        # 3. Create a robust transformation matrix for validation.
                        # This correctly handles fixtures that are not centered at (0,0) in their own DXF file.
                        transform = Matrix44.chain(
                            Matrix44.translate(-local_center.x, -local_center.y, 0), # Move local center to origin
                            Matrix44.z_rotate(wall_angle_rad),                      # Rotate around origin
                            Matrix44.translate(target_center_wcs.x, target_center_wcs.y, 0) # Move to final world position
                        )
                        
                        # 4. Calculate the final insertion point for the place_fixture function.
                        # This point is where the block's origin (0,0) must be placed so its geometry lands correctly.
                        rotated_offset = local_center.rotate(wall_angle_rad)
                        final_insert_point = target_center_wcs - rotated_offset
                        
                        # --- End of New Logic ---

                        world_corners = list(transform.transform_vertices(bench.bounding_box.rect_vertices()))
                        bench_polygon = Polygon([(p.x, p.y) for p in world_corners])
                        bench_aabb = BoundingBox2d(world_corners)

                        is_inside = self.floorplan_polygon.contains(bench_polygon)
                        is_overlapping = any(bench_aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                        if is_inside and not is_overlapping:
                            self.place_fixture(bench, (final_insert_point.x, final_insert_point.y, 0), wall_angle_deg, True)
                            print(f"  ✅ SUCCESS: Placed '{bench.name}'.")
                            placed_bboxes.append((bench_aabb.extmin.x, bench_aabb.extmin.y, bench_aabb.extmax.x, bench_aabb.extmax.y))
                            benches_placed_count += 1
                            is_bench_placed = True
                            break
                        
                        search_distance += 100 
                    
                    if is_bench_placed:
                        break

                if not is_bench_placed:
                    print(f"⚠️ Could not find a valid position for lensometer '{bench.name}' on any wall.")
            
            print(f"-> Placed {benches_placed_count} of {len(benches_to_place)} requested lensometers.")

        except Exception as e:
            print(f"🔥 An error occurred during lensometer placement: {e}")
            traceback.print_exc()
            raise

    

    def place_benches_near_clinics(self, placed_bboxes, max_dist_from_clinic=2500.0):
        """
        Places benches using a clinic-centric strategy.

        1.  It finds all wall segments and prioritizes them based on their proximity
            to the nearest clinic.
        2.  It attempts to place each bench on the closest available wall spot.
        3.  As a fallback, it tries to place any remaining benches directly in
            front of a clinic, offset by a small gap.
        
        Args:
            placed_bboxes: A list of existing bounding boxes to avoid collisions.
            max_dist_from_clinic (float): The maximum distance (in mm) a wall can be
                                          from a clinic to be considered "nearby".
        """
        print(f"\n--- 👩‍⚕️ Attempting to place Benches near Clinics ---")
        try:
            # 1. SETUP: Load benches and find clinics
            bench_config = self.fixtures.get("Bench_fixtures", {})
            benches_to_place = [
                Fixture.Fixture(name, self.fixture_dict[name]["path"])
                for name, count in bench_config.items() if count > 0
                for _ in range(count)
            ]
            if not benches_to_place:
                print("ℹ️ No bench fixtures specified for placement.")
                return

            clinic_bboxes = self._get_clinic_bboxes(buffer=0)
            if not clinic_bboxes:
                print("⚠️ Cannot place benches near clinics: No clinic fixtures found.")
                print("-> Reverting to general prioritized wall placement for benches.")
                self.place_bench_fixtures(wall_priority=['left', 'right', 'top'])
                return
            
            clinic_polygons = [box(*bbox) for bbox in clinic_bboxes]
            all_wall_segments = self.cvc.get_wall_segments(min_length=500)
            
            # --- PRIORITY 1: Find and prioritize nearby walls ---
            print(f"  -> Priority 1: Searching for wall space within {max_dist_from_clinic}mm of a clinic...")
            
            prioritized_walls = []
            for segment in all_wall_segments:
                seg_midpoint = Point((segment[0][0] + segment[1][0]) / 2, (segment[0][1] + segment[1][1]) / 2)
                min_dist = min(seg_midpoint.distance(clinic.centroid) for clinic in clinic_polygons)
                
                if min_dist <= max_dist_from_clinic:
                    prioritized_walls.append({'segment': segment, 'dist': min_dist})
            
            prioritized_walls.sort(key=lambda w: w['dist'])

            unplaced_benches = []
            for bench in benches_to_place:
                is_bench_placed = False
                for wall_data in prioritized_walls:
                    segment = wall_data['segment']
                    p1, p2 = Vec2(segment[0]), Vec2(segment[1])
                    wall_vector, wall_length = p2 - p1, (p2 - p1).magnitude
                    if wall_length < bench.width: continue

                    wall_angle_rad, wall_angle_deg = wall_vector.angle, math.degrees(wall_vector.angle)
                    perp_vec = wall_vector.orthogonal().normalize()
                    inward_normal = perp_vec if self.floorplan_polygon.contains(Point(p1 + perp_vec)) else -perp_vec
                    
                    search_distance = 0
                    while search_distance + bench.width <= wall_length:
                        margin_from_wall = 20.0
                        target_center_wcs = p1 + wall_vector.normalize() * (search_distance + bench.width / 2.0) + inward_normal * (margin_from_wall + bench.height / 2.0)
                        transform = Matrix44.chain(Matrix44.translate(-bench.bounding_box.center.x, -bench.bounding_box.center.y, 0), Matrix44.z_rotate(wall_angle_rad), Matrix44.translate(target_center_wcs.x, target_center_wcs.y, 0))
                        final_insert_point = target_center_wcs - bench.bounding_box.center.rotate(wall_angle_rad)
                        world_corners = list(transform.transform_vertices(bench.bounding_box.rect_vertices()))
                        bench_aabb = BoundingBox2d(world_corners)

                        if self.floorplan_polygon.contains(Polygon(world_corners)) and not any(bench_aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes):
                            self.place_fixture(bench, (final_insert_point.x, final_insert_point.y, 0), wall_angle_deg, True)
                            print(f"    ✅ SUCCESS: Placed '{bench.name}' on a wall near a clinic.")
                            placed_bboxes.append((bench_aabb.extmin.x, bench_aabb.extmin.y, bench_aabb.extmax.x, bench_aabb.extmax.y))
                            is_bench_placed = True
                            break
                        search_distance += 100
                    if is_bench_placed: break
                if not is_bench_placed:
                    unplaced_benches.append(bench)

            # --- PRIORITY 2: Place remaining benches by anchoring to clinics ---
            if unplaced_benches:
                print(f"\n  -> Priority 2 (Fallback): Placing {len(unplaced_benches)} benches anchored to clinics...")
                final_unplaced = []
                for bench in unplaced_benches:
                    is_bench_placed = False
                    for clinic_poly in sorted(clinic_polygons, key=lambda p: p.bounds[1]):
                        gap = 150.0 
                        clinic_bounds = clinic_poly.bounds
                        
                        target_x = clinic_bounds[0] + (clinic_bounds[2] - clinic_bounds[0]) / 2 - (bench.width / 2)
                        target_y = clinic_bounds[1] - gap - bench.height

                        candidate_box = box(target_x, target_y, target_x + bench.width, target_y + bench.height)
                        if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                            self.place_fixture(bench, (target_x, target_y, 0), 0, False)
                            print(f"    ✅ SUCCESS: Placed '{bench.name}' directly in front of a clinic.")
                            placed_bboxes.append(candidate_box.bounds)
                            is_bench_placed = True
                            break
                    if not is_bench_placed:
                        final_unplaced.append(bench)
                
                unplaced_benches = final_unplaced

            total_placed = len(benches_to_place) - len(unplaced_benches)
            print(f"\n-> Finished Bench Placement: Placed {total_placed} of {len(benches_to_place)} requested benches.")
            if unplaced_benches:
                print(f"⚠️ Could not find a suitable location for {len(unplaced_benches)} benches.")

        except Exception as e:
            print(f"🔥 An error occurred during bench placement: {e}")
            traceback.print_exc()
            raise

    def place_benches_intelligently_v1(self, placed_bboxes):
        """
        Places benches using a smart, multi-strategy approach based on user priority.
        V3: Prioritizes placing benches VERTICALLY near clinics first.
        """
        from shapely.geometry import box
        from ezdxf.bbox import extents

        print("\n--- 🧠 Placing Benches with Intelligent Multi-Strategy Approach (V3) ---")

        # 1. SETUP: Load all benches that need to be placed.
        try:
            bench_config = self.fixtures.get("Bench_fixtures", {})
            benches_to_place = [
                Fixture.Fixture(name, self.fixture_dict[name]["path"])
                for name, count in bench_config.items() if count > 0
                for _ in range(count)
            ]
            if not benches_to_place:
                print("ℹ️ No bench fixtures specified for placement.")
                return
            print(f"  -> Found {len(benches_to_place)} bench(es) to place.")
        except Exception as e:
            print(f"🔥 Error loading bench fixtures: {e}")
            return

        remaining_benches = list(benches_to_place)
        
        # --- STRATEGY 1 (NEW PRIORITY): Attempt to place Vertically near clinics ---
        print("\n  -> Strategy 1: Attempting to place benches VERTICALLY near clinics...")
        benches_after_vertical = []
        clinic_bboxes = self._get_clinic_bboxes(buffer=0)
        
        if not clinic_bboxes:
            print("    -> SKIPPED: No clinic fixtures found to anchor to.")
            benches_after_vertical = list(remaining_benches)
        else:
            # Sort clinics from left to right to have a consistent search order
            sorted_clinics = sorted(clinic_bboxes, key=lambda b: b[0])
            
            for bench in remaining_benches:
                is_placed = False
                for bbox in sorted_clinics:
                    clinic_bbox = BoundingBox2d([(bbox[0], bbox[1]), (bbox[2], bbox[3])])
                    # Try placing to the left of the clinic
                    aisle_gap = 50.0
                    rotated_width = bench.height # When rotated, height is the footprint width
                    rotated_height = bench.width
                    
                    x_pos = clinic_bbox.extmin.x - aisle_gap - rotated_width
                    y_pos = clinic_bbox.center.y - (rotated_height / 2) # Center vertically with the clinic

                    candidate_box = box(x_pos, y_pos, x_pos + rotated_width, y_pos + rotated_height)
                    if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                        insert_point = (x_pos + rotated_width, y_pos, 0) # Adjust for 90-degree rotation
                        self.place_fixture(bench, insert_point, 90, True)
                        placed_bboxes.append(candidate_box.bounds)
                        print(f"    ✅ SUCCESS: Placed '{bench.name}' vertically near a clinic.")
                        is_placed = True
                        break # Move to the next bench
                
                if not is_placed:
                    benches_after_vertical.append(bench)
        
        remaining_benches = benches_after_vertical
        if not remaining_benches:
            print("\n✅ All benches placed successfully using Strategy 1.")
            return

        # --- STRATEGY 2: Attempt to place on walls near clinics ---
        print(f"\n  -> Strategy 2: Attempting to place {len(remaining_benches)} benches on walls near clinics...")
        # (The logic for this is the same as before)
        # ... [rest of the function logic] ...
        
        benches_after_wall_near_clinic = []
        if not clinic_bboxes:
            benches_after_wall_near_clinic = list(remaining_benches)
        else:
            clinic_polygons = [box(*bbox) for bbox in clinic_bboxes]
            all_wall_segments = self.cvc.get_wall_segments(min_length=500)
            prioritized_walls = []
            max_dist_from_clinic = 50
            for segment in all_wall_segments:
                seg_midpoint = Point((segment[0][0] + segment[1][0]) / 2, (segment[0][1] + segment[1][1]) / 2)
                min_dist = min(seg_midpoint.distance(clinic.centroid) for clinic in clinic_polygons)
                if min_dist <= max_dist_from_clinic:
                    prioritized_walls.append({'segment': segment, 'dist': min_dist})
            prioritized_walls.sort(key=lambda w: w['dist'])

            for bench in remaining_benches:
                is_placed = False
                for wall_data in prioritized_walls:
                    if self._validate_and_place_on_segment_wall(bench, wall_data['segment'], placed_bboxes):
                        print(f"    ✅ SUCCESS: Placed '{bench.name}' on a wall near a clinic.")
                        is_placed = True
                        break
                if not is_placed:
                    benches_after_wall_near_clinic.append(bench)
        
        remaining_benches = benches_after_wall_near_clinic
        if not remaining_benches:
            print("\n✅ All benches placed successfully using Strategies 1 & 2.")
            return
            
        # --- STRATEGY 3: Attempt to attach directly to clinic sides ---
        print(f"\n  -> Strategy 3: Attempting to attach {len(remaining_benches)} benches to clinic sides...")
        # (The logic for this is the same as before)
        # ... [rest of the function logic] ...
        benches_after_attach = []
        if not clinic_bboxes:
            benches_after_attach = list(remaining_benches)
        else:
            virtual_walls = []
            for bbox_coords in clinic_bboxes:
                min_x, min_y, max_x, max_y = bbox_coords
                virtual_walls.append({'segment': ((max_x, min_y), (max_x, max_y)), 'normal': Vec2(1, 0)})
                virtual_walls.append({'segment': ((min_x, min_y), (min_x, max_y)), 'normal': Vec2(-1, 0)})
            
            for bench in remaining_benches:
                is_placed = False
                for wall_data in virtual_walls:
                    if self._validate_and_place_on_segment_wall(bench, wall_data['segment'], placed_bboxes, fixed_normal=wall_data['normal']):
                        print(f"    ✅ SUCCESS: Placed '{bench.name}' attached to a clinic side.")
                        is_placed = True
                        break
                if not is_placed:
                    benches_after_attach.append(bench)
        
        remaining_benches = benches_after_attach
        if not remaining_benches:
            print("\n✅ All benches placed successfully using Strategies 1, 2 & 3.")
            return

        # --- STRATEGY 4: Final fallback - search ANY available wall space ---
        print(f"\n  -> Strategy 4 (Fallback): Searching all remaining walls for {len(remaining_benches)} benches...")
        # (The logic for this is the same as before)
        # ... [rest of the function logic] ...
        benches_after_fallback = []
        all_segments = self.cvc.get_wall_segments(min_length=500)
        placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
        for bench in remaining_benches:
            is_placed = False
            for segment in all_segments:
                if self._validate_and_place_on_segment_wall(bench, segment, placed_bboxes):
                    print(f"    ✅ SUCCESS: Placed '{bench.name}' on a fallback wall.")
                    is_placed = True
                    break
            if not is_placed:
                benches_after_fallback.append(bench)
        
        # FINAL REPORT
        placed_count = len(benches_to_place) - len(benches_after_fallback)
        print(f"\n-> Intelligent Placement Complete: Placed {placed_count} of {len(benches_to_place)} benches.")
        if benches_after_fallback:
            print(f"⚠️ Could not find a suitable location for {len(benches_after_fallback)} benches after all strategies.")

    def place_benches_intelligently_v1(self, placed_bboxes):
        """
        Places benches using a smart, multi-strategy approach based on user priority.
        V3: Prioritizes placing benches VERTICALLY near clinics first.
        """
        from shapely.geometry import box
        from ezdxf.bbox import extents

        print("\n--- 🧠 Placing Benches with Intelligent Multi-Strategy Approach (V3) ---")

        # 1. SETUP: Load all benches that need to be placed.
        try:
            bench_config = self.fixtures.get("Bench_fixtures", {})
            benches_to_place = [
                Fixture.Fixture(name, self.fixture_dict[name]["path"])
                for name, count in bench_config.items() if count > 0
                for _ in range(count)
            ]
            if not benches_to_place:
                print("ℹ️ No bench fixtures specified for placement.")
                return
            print(f"  -> Found {len(benches_to_place)} bench(es) to place.")
        except Exception as e:
            print(f"🔥 Error loading bench fixtures: {e}")
            return

        # remaining_benches = list(benches_to_place)
        remaining_benches = collections.deque(benches_to_place)
        
        # --- STRATEGY 1: Attempt to place Vertically near clinics (CORRECTED LOGIC) ---
        print("\n  -> Strategy 1: Attempting to place benches VERTICALLY near clinics...")
        benches_after_vertical = collections.deque()
        clinic_bboxes = self._get_clinic_bboxes(buffer=0)
        
        if not clinic_bboxes:
            print("    -> SKIPPED: No clinic fixtures found to anchor to.")
            benches_after_vertical = remaining_benches
        else:
            sorted_clinics = sorted(clinic_bboxes, key=lambda b: b[0])
            
            while remaining_benches:
                bench = remaining_benches.popleft() # Take one bench to try and place
                is_placed = False
                for bbox in sorted_clinics:
                    clinic_bbox = BoundingBox2d([(bbox[0], bbox[1]), (bbox[2], bbox[3])])
                    aisle_gap = 100.0
                    rotated_width, rotated_height = bench.height, bench.width
                    
                    x_pos = clinic_bbox.extmin.x - aisle_gap - rotated_width
                    y_pos = clinic_bbox.center.y - (rotated_height / 2)

                    candidate_box = box(x_pos, y_pos, x_pos + rotated_width, y_pos + rotated_height)
                    if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                        insert_point = (x_pos + rotated_width, y_pos, 0)
                        self.place_fixture(bench, insert_point, 90, True)
                        placed_bboxes.append(candidate_box.bounds)
                        print(f"    ✅ SUCCESS: Placed '{bench.name}' vertically near a clinic.")
                        is_placed = True
                        break
                
                if not is_placed:
                    benches_after_vertical.append(bench) # Add back ONLY if it failed
        
        remaining_benches = benches_after_vertical
        if not remaining_benches:
            print("\n✅ All benches placed successfully using Strategy 1.")
            return

        # --- STRATEGY 2: Attempt to place on walls near clinics (CORRECTED PARAMETER) ---
        print(f"\n  -> Strategy 2: Attempting to place {len(remaining_benches)} benches on walls near clinics...")
        benches_after_wall_near_clinic = collections.deque()
        if not clinic_bboxes:
            benches_after_wall_near_clinic = remaining_benches
        else:
            clinic_polygons = [box(*bbox) for bbox in clinic_bboxes]
            placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
            all_wall_segments = self.cvc.get_wall_segments(min_length=500)
            prioritized_walls = []
            
            # *** FIX: Increased the search distance to a reasonable 2.5 meters ***
            max_dist_from_clinic = 2500.0 
            
            for segment in all_wall_segments:
                seg_midpoint = Point((segment[0][0] + segment[1][0]) / 2, (segment[0][1] + segment[1][1]) / 2)
                min_dist = min(seg_midpoint.distance(clinic.centroid) for clinic in clinic_polygons)
                if min_dist <= max_dist_from_clinic:
                    prioritized_walls.append({'segment': segment, 'dist': min_dist})
            prioritized_walls.sort(key=lambda w: w['dist'])

            while remaining_benches:
                bench = remaining_benches.popleft()
                is_placed = False
                for wall_data in prioritized_walls:
                    if self._validate_and_place_on_segment_wall(bench, wall_data['segment'], placed_bboxes):
                        print(f"    ✅ SUCCESS: Placed '{bench.name}' on a wall near a clinic.")
                        is_placed = True
                        break
                if not is_placed:
                    benches_after_wall_near_clinic.append(bench)
        
        remaining_benches = benches_after_wall_near_clinic
        if not remaining_benches:
            print("\n✅ All benches placed successfully using Strategies 1 & 2.")
            return
            
        # --- STRATEGY 3: Attempt to attach directly to clinic sides ---
        print(f"\n  -> Strategy 3: Attempting to attach {len(remaining_benches)} benches to clinic sides...")
        # (The logic for this is the same as before)
        # ... [rest of the function logic] ...
        benches_after_attach = []
        placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
        if not clinic_bboxes:
            benches_after_attach = list(remaining_benches)
        else:
            virtual_walls = []
            for bbox_coords in clinic_bboxes:
                min_x, min_y, max_x, max_y = bbox_coords
                virtual_walls.append({'segment': ((max_x, min_y), (max_x, max_y)), 'normal': Vec2(1, 0)})
                virtual_walls.append({'segment': ((min_x, min_y), (min_x, max_y)), 'normal': Vec2(-1, 0)})
            
            for bench in remaining_benches:
                is_placed = False
                for wall_data in virtual_walls:
                    if self._validate_and_place_on_segment_wall(bench, wall_data['segment'], placed_bboxes, fixed_normal=wall_data['normal']):
                        print(f"    ✅ SUCCESS: Placed '{bench.name}' attached to a clinic side.")
                        is_placed = True
                        break
                if not is_placed:
                    benches_after_attach.append(bench)
        
        remaining_benches = benches_after_attach
        if not remaining_benches:
            print("\n✅ All benches placed successfully using Strategies 1, 2 & 3.")
            return

        # --- STRATEGY 4: Final fallback - search ANY available wall space ---
        print(f"\n  -> Strategy 4 (Fallback): Searching all remaining walls for {len(remaining_benches)} benches...")
        # (The logic for this is the same as before)
        # ... [rest of the function logic] ...
        benches_after_fallback = []
        all_segments = self.cvc.get_wall_segments(min_length=500)
        placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
        for bench in remaining_benches:
            is_placed = False
            for segment in all_segments:
                if self._validate_and_place_on_segment_wall(bench, segment, placed_bboxes):
                    print(f"    ✅ SUCCESS: Placed '{bench.name}' on a fallback wall.")
                    is_placed = True
                    break
            if not is_placed:
                benches_after_fallback.append(bench)
        
        # FINAL REPORT
        placed_count = len(benches_to_place) - len(benches_after_fallback)
        print(f"\n-> Intelligent Placement Complete: Placed {placed_count} of {len(benches_to_place)} benches.")
        if benches_after_fallback:
            print(f"⚠️ Could not find a suitable location for {len(benches_after_fallback)} benches after all strategies.")

    def place_benches_intelligently(self, placed_bboxes):
        """
        Places benches using a smart, multi-strategy approach based on user priority.
        V4: Includes a robust fallback that tries to place benches on all four sides of every available clinic.
        """
        from shapely.geometry import box, Point
        from ezdxf.bbox import extents
        from ezdxf.math import BoundingBox2d, Vec2
        import collections

        print("\n--- 🧠 Placing Benches with Intelligent Multi-Strategy Approach (V4) ---")

        # 1. SETUP: Load all benches that need to be placed.
        try:
            bench_config = self.fixtures.get("Bench_fixtures", {})
            benches_to_place = [
                Fixture.Fixture(name, self.fixture_dict[name]["path"])
                for name, count in bench_config.items() if count > 0
                for _ in range(count)
            ]
            if not benches_to_place:
                print("ℹ️ No bench fixtures specified for placement.")
                return
            print(f"  -> Found {len(benches_to_place)} bench(es) to place.")
        except Exception as e:
            print(f"🔥 Error loading bench fixtures: {e}")
            return

        remaining_benches = collections.deque(benches_to_place)
        clinic_bboxes = self._get_clinic_bboxes(buffer=0)
        
        # --- STRATEGY 1: Attempt to place Vertically near clinics ---
        print("\n  -> Strategy 1: Attempting to place benches VERTICALLY near clinics...")
        benches_after_vertical = collections.deque()
        
        if not clinic_bboxes:
            print("    -> SKIPPED: No clinic fixtures found to anchor to.")
            benches_after_vertical = remaining_benches
        else:
            sorted_clinics = sorted(clinic_bboxes, key=lambda b: b[0])
            
            while remaining_benches:
                bench = remaining_benches.popleft()
                is_placed = False
                for bbox in sorted_clinics:
                    clinic_bbox = BoundingBox2d([(bbox[0], bbox[1]), (bbox[2], bbox[3])])
                    aisle_gap = 100.0
                    rotated_width, rotated_height = bench.height, bench.width
                    
                    x_pos = clinic_bbox.extmin.x - aisle_gap - rotated_width
                    y_pos = clinic_bbox.center.y - (rotated_height / 2)

                    candidate_box = box(x_pos, y_pos, x_pos + rotated_width, y_pos + rotated_height)
                    if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                        insert_point = (x_pos + rotated_width, y_pos, 0)
                        self.place_fixture(bench, insert_point, 90, True)
                        placed_bboxes.append(candidate_box.bounds)
                        print(f"    ✅ SUCCESS: Placed '{bench.name}' vertically near a clinic.")
                        is_placed = True
                        break
                
                if not is_placed:
                    benches_after_vertical.append(bench)
        
        remaining_benches = benches_after_vertical
        if not remaining_benches:
            print("\n✅ All benches placed successfully using Strategy 1.")
            return
            
        # --- STRATEGY 3 (NEW FALLBACK): Try all 4 sides of EVERY clinic ---
        print(f"\n  -> Strategy 3 (Fallback): Searching all sides of all clinics for {len(remaining_benches)} benches...")
        benches_after_fallback = collections.deque()
        if not clinic_bboxes:
            benches_after_fallback = remaining_benches
        else:
            sorted_clinics = sorted(clinic_bboxes, key=lambda b: b[0])
            while remaining_benches:
                bench = remaining_benches.popleft()
                is_placed = False
                
                for bbox in sorted_clinics:
                    clinic_bbox = BoundingBox2d([(bbox[0], bbox[1]), (bbox[2], bbox[3])])
                    aisle_gap = 00.0

                    spots_to_try = [
                        {"side": "top", "rot": 0, "w": bench.width, "h": bench.height, 
                         "x": clinic_bbox.center.x - (bench.width / 2), 
                         "y": clinic_bbox.extmax.y + aisle_gap},
                        {"side": "bottom", "rot": 0, "w": bench.width, "h": bench.height, 
                         "x": clinic_bbox.center.x - (bench.width / 2), 
                         "y": clinic_bbox.extmin.y - aisle_gap - bench.height},
                        {"side": "left", "rot": 90, "w": bench.height, "h": bench.width, 
                         "x": clinic_bbox.extmin.x - aisle_gap - bench.height, 
                         "y": clinic_bbox.center.y - (bench.width / 2)},
                        {"side": "right", "rot": 90, "w": bench.height, "h": bench.width, 
                         "x": clinic_bbox.extmax.x + aisle_gap, 
                         "y": clinic_bbox.center.y - (bench.width / 2)}
                    ]

                    for spot in spots_to_try:
                        candidate_box = box(spot["x"], spot["y"], spot["x"] + spot["w"], spot["y"] + spot["h"])
                        if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                            if spot["rot"] == 90:
                                insert_point = (spot["x"] + spot["w"], spot["y"], 0)
                            else:
                                insert_point = (spot["x"], spot["y"], 0)

                            self.place_fixture(bench, insert_point, spot["rot"], True)
                            placed_bboxes.append(candidate_box.bounds)
                            print(f"    ✅ SUCCESS: Placed '{bench.name}' on the {spot['side']} of a clinic via fallback.")
                            is_placed = True
                            break
                    if is_placed:
                        break
                
                if not is_placed:
                    benches_after_fallback.append(bench)

         # --- STRATEGY 2: Attempt to place on walls near clinics ---
        print(f"\n  -> Strategy 2: Attempting to place {len(remaining_benches)} benches on walls near clinics...")
        benches_after_wall_near_clinic = collections.deque()
        if not clinic_bboxes:
            benches_after_wall_near_clinic = remaining_benches
        else:
            clinic_polygons = [box(*bbox) for bbox in clinic_bboxes]
            all_wall_segments = self.cvc.get_wall_segments(min_length=500)
            prioritized_walls = []
            max_dist_from_clinic = 2500.0 
            
            for segment in all_wall_segments:
                seg_midpoint = Point((segment[0][0] + segment[1][0]) / 2, (segment[0][1] + segment[1][1]) / 2)
                min_dist = min(seg_midpoint.distance(clinic.centroid) for clinic in clinic_polygons)
                if min_dist <= max_dist_from_clinic:
                    prioritized_walls.append({'segment': segment, 'dist': min_dist})
            prioritized_walls.sort(key=lambda w: w['dist'])

            while remaining_benches:
                bench = remaining_benches.popleft()
                is_placed = False
                for wall_data in prioritized_walls:
                    if self._validate_and_place_on_segment_wall(bench, wall_data['segment'], placed_bboxes):
                        print(f"    ✅ SUCCESS: Placed '{bench.name}' on a wall near a clinic.")
                        is_placed = True
                        break
                if not is_placed:
                    benches_after_wall_near_clinic.append(bench)
        
        remaining_benches = benches_after_wall_near_clinic
        if not remaining_benches:
            print("\n✅ All benches placed successfully using Strategies 1 & 2.")
            return
        
        remaining_benches = benches_after_fallback

        # FINAL REPORT
        placed_count = len(benches_to_place) - len(remaining_benches)
        print(f"\n-> Intelligent Placement Complete: Placed {placed_count} of {len(benches_to_place)} benches.")
        if remaining_benches:
            print(f"⚠️ Could not find a suitable location for {len(remaining_benches)} benches after all strategies.")


    def _validate_and_place_on_segment_wall(self, bench, segment, placed_bboxes, fixed_normal=None):
        """
        Helper function to find a spot on a single wall segment.
        If fixed_normal is provided, it uses that direction instead of calculating one.
        """
        p1, p2 = Vec2(segment[0]), Vec2(segment[1])
        wall_vector = p2 - p1
        wall_length = wall_vector.magnitude
        
        if wall_length < bench.width:
            return False

        wall_angle_rad = wall_vector.angle
        wall_angle_deg = math.degrees(wall_angle_rad)
        
        # Use the fixed normal if provided, otherwise calculate it
        if fixed_normal:
            inward_normal = fixed_normal
        else:
            perp_vec = wall_vector.orthogonal().normalize()
            inward_normal = perp_vec if self.floorplan_polygon.contains(Point(p1 + perp_vec)) else -perp_vec

        # The margin/gap from the wall/clinic side
        margin = 50.0 
        search_distance = 0
        while search_distance + bench.width <= wall_length:
            target_center_wcs = p1 + wall_vector.normalize() * (search_distance + bench.width / 2.0) + inward_normal * (margin + bench.height / 2.0)
            if self._validate_and_place_at_point(bench, target_center_wcs, wall_angle_deg, placed_bboxes):
                return True
            search_distance += 100
        return False
    

    
    def place_sofas_above_screen_ar(self, placed_bboxes, bottom_margin_pct=0.20, gap_above_ar=300):
        """
        Places sofa fixtures using a prioritized, multi-strategy approach.

        Strategy 1 (Primary): Places sofas a specific distance (`gap_above_ar`) above the POS/AR fixtures.
        Strategy 2 (Fallback): If the ideal gap is too large, it fits the sofas into the remaining space.
        Strategy 3 (Fallback): If there's no room above, it tries to place them in the bottom margin area.
        Strategy 4 (Final Fallback): Performs a global grid search for any available space.
        """
        from Fixture import Fixture
        from shapely.geometry import Point, box
        from ezdxf.bbox import extents
        import traceback

        print("\n--- Attempting to place Sofa(s) with multi-strategy logic ---")

        # 1. SETUP: Load all sofa fixtures to be placed
        try:
            sofa_config = self.fixtures.get("loose_furniture", {})
            sofas_to_place = []
            for name, count in sofa_config.items():
                if "sofa" in name.lower() and count > 0:
                    try:
                        fxtr = Fixture(name, self.fixture_dict[name]["path"])
                        sofas_to_place.extend([fxtr] * count)
                    except KeyError:
                        print(f"⚠️ Warning: Fixture '{name}' is specified but not found. Skipping.")
            
            if not sofas_to_place:
                print("ℹ️ No sofa fixtures were specified for placement.")
                return

        except Exception as e:
            print(f"🔥 Error during sofa setup: {e}")
            traceback.print_exc()
            return

        # --- HELPER FUNCTION to place a row of sofas ---
        def _place_sofa_row(start_x, start_y, sofas_list):
            """Attempts to place a list of sofas in a row, starting at a given coordinate."""
            placed_in_this_row = 0
            current_x = start_x
            for sofa_fxtr in sofas_list:
                # For sofas, rotation is typically 0, and the footprint is width x height
                x1, y1 = current_x, start_y
                x2, y2 = x1 + sofa_fxtr.width, y1 + sofa_fxtr.height

                candidate_box = box(x1, y1, x2, y2)
                is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
                is_inside = self.floorplan_polygon.contains(candidate_box)

                if is_inside and not is_overlapping:
                    self.place_fixture(sofa_fxtr, (x1, y1, 0), 0, False)
                    placed_bboxes.append((x1, y1, x2, y2))
                    print(f"    ✅ SUCCESS: Placed '{sofa_fxtr.name}' at ({x1:.0f}, {y1:.0f}).")
                    current_x = x2 + 100  # Gap between sofas
                    placed_in_this_row += 1
                else:
                    # If one sofa in the row is blocked, we assume the whole row attempt fails
                    return 0
            return placed_in_this_row

        # 2. FIND ANCHOR POINTS
        rm_x0, rm_x1 = self.cvc.min_x, self.cvc.max_x
        rm_y0, rm_y1 = self.cvc.max_y, self.cvc.max_y
        room_w = rm_x1 - rm_x0
        
        # Accurately find the top of the AR/POS group
        ar_pos_entities = [e for e in self.msp.query('INSERT') if "POS" in e.dxf.name.upper() or "AR" in e.dxf.name.upper()]
        top_of_ar_stack = 0
        if ar_pos_entities:
            top_of_ar_stack = extents(ar_pos_entities).extmax.y
        else:
            print("ℹ️ No POS/AR fixtures found to anchor to. Fallback strategies will be used.")
            # Estimate a fallback position if no POS/AR found
            top_of_ar_stack = self.cvc.min_y + (self.cvc.max_y - self.cvc.min_y) * 0.6


        # 3. CALCULATE REQUIRED SPACE for the sofa row
        total_sofa_width = sum(f.width for f in sofas_to_place) + (len(sofas_to_place) - 1) * 100
        sofa_row_height = max(f.height for f in sofas_to_place) if sofas_to_place else 0
        start_x_centered = rm_x0 + (room_w - total_sofa_width) / 2

        placed_count = 0
        
        # 4. EXECUTE PLACEMENT STRATEGIES
        # --- Strategy 1: Place with ideal gap above AR/POS ---
        print("  -> Attempting Strategy 1: Place with ideal gap above AR/POS...")
        proposed_y = top_of_ar_stack + gap_above_ar
        if proposed_y + sofa_row_height < self.cvc.max_y - 100:
            placed_count = _place_sofa_row(start_x_centered, proposed_y, sofas_to_place)

        # --- Strategy 2: Fit in available space above AR/POS ---
        if placed_count == 0:
            print("  -> Strategy 1 failed. Attempting Strategy 2: Fit in available space above AR/POS...")
            available_space = self.cvc.max_y - top_of_ar_stack - 100
            if available_space >= sofa_row_height:
                y_pos = top_of_ar_stack + (available_space - sofa_row_height) / 2
                placed_count = _place_sofa_row(start_x_centered, y_pos, sofas_to_place)

        # --- Strategy 3: Place in bottom margin area (below Euros) ---
        if placed_count == 0:
            print("  -> Strategy 2 failed. Attempting Strategy 3: Place in bottom margin area...")
            room_height = self.cvc.max_y - self.cvc.min_y
            start_y_euros = self.cvc.min_y + (room_height * bottom_margin_pct)
            bottom_gap_space = start_y_euros - self.cvc.min_y - 100
            if bottom_gap_space >= sofa_row_height:
                y_pos = self.cvc.min_y + (bottom_gap_space - sofa_row_height) / 2
                placed_count = _place_sofa_row(start_x_centered, y_pos, sofas_to_place)

        # --- Strategy 4: Global Grid Search ---
        if placed_count == 0:
            print("  -> Strategy 3 failed. Attempting Strategy 4: Global grid search...")
            # (A simplified grid search for any remaining space)
            y_try = self.cvc.max_y - sofa_row_height - 100
            while y_try > self.cvc.min_y and placed_count == 0:
                placed_count = _place_sofa_row(start_x_centered, y_try, sofas_to_place)
                y_try -= 200 # Decrement search position

        print(f"\n-> Finished Sofa Placement: Placed {placed_count} of {len(sofas_to_place)} requested sofas.")


    def place_screen(self):
        """Places TV fixture near bottom-right corner with proper margins and boundary checks"""
        try:
            screen_key = "screen_49"
            tv_path = self.fixture_dict[screen_key]["path"]
            if not os.path.exists(tv_path):
                raise FileNotFoundError(f"Screen fixture file not found: {tv_path}")

            fxtr = Fixture.Fixture(self.fixture_dict[screen_key]["name"], tv_path)
            if not fxtr:
                raise ValueError("Screen fixture could not be loaded or has no objects")

            # Calculate safe placement position
            room_right = max(self.cvc.x_coords)
            room_bottom = min(self.cvc.y_coords)
            room_width = room_right - min(self.cvc.x_coords)
            room_height = max(self.cvc.y_coords) - room_bottom

            # Dynamic margins based on room size
            margin_right = max(500, room_width * 0.02)  # At least 500mm from right wall
            margin_bottom = max(100, room_height * 0.02)  # At least 400mm from bottom
            
            # Additional inset from wall for better visibility
            inset = min(1000, room_width * 0.15)  # Cap at 1000mm
            
            # Calculate initial position
            x = room_right - fxtr.width - margin_right - inset
            y = room_bottom + margin_bottom

            # Boundary check margins
            margin_check = 50

            # Test points to verify placement
            test_points = [
                Vec3(x - margin_check, y - margin_check, 0),              # bottom-left
                Vec3(x + fxtr.width + margin_check, y - margin_check, 0), # bottom-right
                Vec3(x + fxtr.width + margin_check, y + fxtr.height, 0),  # top-right
                Vec3(x - margin_check, y + fxtr.height, 0)                # top-left
            ]

            # Progressive position adjustment if needed
            placed = False
            attempts = 0
            max_attempts = 10
            
            while not placed and attempts < max_attempts:
                if all(self.floorplan_polygon.contains(Point(pt.x, pt.y)) for pt in test_points):
                    placed = True
                    break
                
                # Move left and slightly up if not valid
                x -= 200
                y += 50
                
                # Update test points
                test_points = [
                    Vec3(x - margin_check, y - margin_check, 0),
                    Vec3(x + fxtr.width + margin_check, y - margin_check, 0),
                    Vec3(x + fxtr.width + margin_check, y + fxtr.height, 0),
                    Vec3(x - margin_check, y + fxtr.height, 0)
                ]
                attempts += 1

            if not placed:
                print("Could not find valid position for TV placement after multiple attempts")

            insert_point = (x, y, 0)
            self.place_fixture(fxtr, insert_point, 0, False)
            print(f"✅ TV placed at ({x}, {y})")

        except Exception as e:
            print(f"⚠️ Error placing TV: {str(e)}")
            raise

    def _get_clinic_bboxes(self, buffer=50.0):
        """
        Gets the bounding boxes of all clinic fixtures with an optional safety buffer.
        This identifies "no-go zones" for other fixture placements.
        """
        from ezdxf.bbox import extents
        clinic_bboxes = []
        # Find all placed fixtures whose block names contain "CLINIC".
        clinic_entities = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
        for entity in clinic_entities:
            try:
                # Calculate the precise bounding box of the clinic.
                bbox = extents([entity], fast=True)
                # Add a buffer to all sides to create the safety margin.
                buffered_bbox = (
                    bbox.extmin.x - buffer,
                    bbox.extmin.y - buffer,
                    bbox.extmax.x + buffer,
                    bbox.extmax.y + buffer,
                )
                clinic_bboxes.append(buffered_bbox)
            except (RuntimeError, ZeroDivisionError, TypeError):
                # Skip any invalid clinic fixtures that can't be measured.
                continue
        return clinic_bboxes

    def place_tv_screens(self):
        """
        Places TV screens using a robust, prioritized search strategy for each screen,
        ensuring no overlaps with general fixtures or special clinic zones.
        """
        print("\n--- Attempting to place TV Screens ---")
        try:
            from ezdxf.bbox import extents

            # --- 1. Configuration and Fixture Loading ---
            screen_config = self.fixtures.get("screen_fixtures", {})
            if not any(screen_config.values()):
                print("ℹ️ No screen fixtures specified for placement.")
                return

            screens_to_place = []
            for name, count in screen_config.items():
                if count > 0:
                    try:
                        fxtr = Fixture.Fixture(name, self.fixture_dict[name]["path"])
                        screens_to_place.extend([fxtr] * count)
                    except (KeyError, ValueError) as e:
                        print(f"⚠️ Warning: Screen fixture '{name}' could not be loaded: {e}")
            
            if not screens_to_place:
                return

            placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
            clinic_no_go_zones = self._get_clinic_bboxes(buffer=50.0)
            total_screens_to_place = len(screens_to_place)
            screens_placed_count = 0

            # --- 2. Unified Validation and Helper Functions ---

            def validate_and_place(fixture, target_center, angle_deg):
                """Performs robust validation against all obstacles and places the fixture."""
                local_center = fixture.bounding_box.center
                transform = Matrix44.chain(
                    Matrix44.translate(-local_center.x, -local_center.y, 0),
                    Matrix44.z_rotate(math.radians(angle_deg)),
                    Matrix44.translate(target_center.x, target_center.y, 0)
                )
                
                world_corners = list(transform.transform_vertices(fixture.bounding_box.rect_vertices()))
                aabb = BoundingBox2d(world_corners)
                fixture_polygon = Polygon([(p.x, p.y) for p in world_corners])

                is_inside = self.floorplan_polygon.buffer(-1.0).contains(fixture_polygon)
                is_overlapping_general = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)
                is_overlapping_clinic = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in clinic_no_go_zones)

                if is_inside and not is_overlapping_general and not is_overlapping_clinic:
                    rotated_offset = local_center.rotate(math.radians(angle_deg))
                    final_insert_point = target_center - rotated_offset
                    self.place_fixture(fixture, (final_insert_point.x, final_insert_point.y, 0), angle_deg, True)
                    placed_bboxes.append((aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y))
                    return True
                return False

            def get_bottom_wall():
                """Finds the most horizontal wall segment with the lowest Y value."""
                all_segments = self.cvc.get_wall_segments(min_length=100)
                if not all_segments: return None
                bottom_segment, lowest_y = None, float('inf')
                for p1_coords, p2_coords in all_segments:
                    p1, p2 = Vec2(p1_coords), Vec2(p2_coords)
                    avg_y = (p1.y + p2.y) / 2
                    angle = abs(math.degrees((p2 - p1).angle))
                    if avg_y < lowest_y and (angle < 15 or angle > 165):
                        lowest_y, bottom_segment = avg_y, (p1, p2)
                return bottom_segment

            # --- 3. Main Placement Loop ---
            for screen in screens_to_place:
                print(f"\nAttempting to place '{screen.name}'...")
                is_placed = False

                # --- Strategy 1: Attempt to place at bottom-right (10% inset) ---
                bottom_segment = get_bottom_wall()
                if bottom_segment:
                    p1, p2 = Vec2(bottom_segment[0]), Vec2(bottom_segment[1])
                    wall_vector, wall_length = (p2 - p1), (p2 - p1).magnitude
                    if p1.x > p2.x: p1, p2, wall_vector = p2, p1, -wall_vector
                    
                    inset_dist = wall_length * 0.10
                    if wall_length > inset_dist + screen.width:
                        target_point = p2 - wall_vector.normalize() * (inset_dist + screen.width / 2.0)
                        inward = wall_vector.orthogonal().normalize()
                        if not self.floorplan_polygon.contains(Point((target_point + inward).x, (target_point + inward).y)): inward = -inward
                        target_center = target_point + inward * (50.0 + screen.height / 2.0)
                        if validate_and_place(screen, target_center, math.degrees(wall_vector.angle)):
                            print(f"✅ Placed '{screen.name}' at bottom-right.")
                            is_placed = True
                
                # --- Strategy 2: Attempt to place between Euro Centres ---
                if not is_placed:
                    euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
                    if len(euro_entities) >= 2:
                        euro_bboxes = [extents([e], fast=True) for e in euro_entities if extents([e], fast=True)]
                        if len(euro_bboxes) >= 2:
                            euro_bboxes.sort(key=lambda b: b.extmin.y)
                            gap_center_y = (euro_bboxes[0].extmax.y + euro_bboxes[1].extmin.y) / 2.0
                            center_x = (min(self.cvc.x_coords) + max(self.cvc.x_coords)) / 2.0
                            if validate_and_place(screen, Vec2(center_x, gap_center_y), 0):
                                print(f"✅ Placed '{screen.name}' between Euro Centres.")
                                is_placed = True

                # --- Strategy 3: Attempt to place at bottom-left (10% inset) ---
                if not is_placed and bottom_segment:
                    p1, p2 = Vec2(bottom_segment[0]), Vec2(bottom_segment[1])
                    wall_vector, wall_length = (p2 - p1), (p2 - p1).magnitude
                    if p1.x > p2.x: p1, p2, wall_vector = p2, p1, -wall_vector

                    inset_dist = wall_length * 0.10
                    if wall_length > inset_dist + screen.width:
                        target_point = p1 + wall_vector.normalize() * (inset_dist + screen.width / 2.0)
                        inward = wall_vector.orthogonal().normalize()
                        if not self.floorplan_polygon.contains(Point((target_point + inward).x, (target_point + inward).y)): inward = -inward
                        target_center = target_point + inward * (50.0 + screen.height / 2.0)
                        if validate_and_place(screen, target_center, math.degrees(wall_vector.angle)):
                            print(f"✅ Placed '{screen.name}' at bottom-left.")
                            is_placed = True

                # --- Strategy 4: Fallback to searching all walls ---
                if not is_placed:
                    print(f"ℹ️ Preferred spots for '{screen.name}' failed. Searching all walls...")
                    all_wall_segments = self.cvc.get_wall_segments(min_length=screen.width + 100)
                    for segment in all_wall_segments:
                        if self.place_fixture_on_any_wall(screen, placed_bboxes, clinic_no_go_zones, wall_filter=[segment]):
                            print(f"✅ Placed '{screen.name}' on a fallback wall.")
                            is_placed = True
                            break
                
                if is_placed:
                    screens_placed_count += 1
                else:
                    print(f"⚠️ Could not find any valid position for screen '{screen.name}'.")

            print(f"\n-> Placed {screens_placed_count} of {total_screens_to_place} requested screens.")

        except Exception as e:
            print(f"🔥 An error occurred during screen placement: {e}")
            traceback.print_exc()
            raise


    def place_fixture_on_any_wall(self, fixture, placed_bboxes, clinic_no_go_zones, wall_filter=None, search_right_to_left=False):
        """
        A generic helper function to place a fixture along available wall segments.
        Now includes a check against specific "no-go zones" like clinics.
        """
        segments_to_search = wall_filter if wall_filter is not None else self.cvc.get_wall_segments(min_length=fixture.width + 100)
        
        for segment in segments_to_search:
            p1, p2 = Vec2(segment[0]), Vec2(segment[1])
            wall_vector = p2 - p1
            wall_length = wall_vector.magnitude
            wall_angle_rad = wall_vector.angle
            wall_angle_deg = math.degrees(wall_angle_rad)
            perp_vec = wall_vector.orthogonal().normalize()
            test_point = p1 + wall_vector * 0.5 + perp_vec * 1.0
            inward_normal = perp_vec if self.floorplan_polygon.contains(Point(test_point.x, test_point.y)) else -perp_vec
            
            search_range = range(0, int(wall_length - fixture.width), 100)
            if search_right_to_left:
                search_range = reversed(search_range)

            for search_distance in search_range:
                margin_from_wall = 50.0
                local_center = fixture.bounding_box.center
                footprint_center_on_wall = p1 + wall_vector.normalize() * (search_distance + fixture.width / 2.0)
                offset_dist = margin_from_wall + (fixture.height / 2.0)
                target_center_wcs = footprint_center_on_wall + inward_normal * offset_dist
                
                transform = Matrix44.chain(
                    Matrix44.translate(-local_center.x, -local_center.y, 0),
                    Matrix44.z_rotate(wall_angle_rad),
                    Matrix44.translate(target_center_wcs.x, target_center_wcs.y, 0)
                )
                
                rotated_offset = local_center.rotate(wall_angle_rad)
                final_insert_point = target_center_wcs - rotated_offset

                world_corners = list(transform.transform_vertices(fixture.bounding_box.rect_vertices()))
                aabb = BoundingBox2d(world_corners)
                is_inside = self.floorplan_polygon.buffer(-1.0).contains(Polygon([(p.x, p.y) for p in world_corners]))
                is_overlapping_general = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)
                # --- FIX: Added clinic check to the fallback function ---
                is_overlapping_clinic = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in clinic_no_go_zones)

                if is_inside and not is_overlapping_general and not is_overlapping_clinic:
                    self.place_fixture(fixture, (final_insert_point.x, final_insert_point.y, 0), wall_angle_deg, True)
                    placed_bboxes.append((aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y))
                    return True
        return False
    
    def place_Blue_Zero_attached(self, placed_bboxes):
        """
        Finds existing discussion tables and places "Blue_zero" fixtures
        below them. If no discussion tables are found, it attempts to place
        them below Euro_centre fixtures instead.
        """
        # 1. Get the configuration from the main fixtures dictionary
        config = self.fixtures.get("discussion_table_attached", {})
        blue_zero_count = config.get("Blue_zero", 0)

        # Exit early if no fixtures are requested
        if blue_zero_count <= 0:
            return

        print("\n--- Attempting to place attached discussion fixtures (Blue_zero) ---")

        # 2. Load the "Blue_zero" fixture object once to get its dimensions
        try:
            blue_zero_fxtr = Fixture.Fixture("Blue_zero", self.fixture_dict["Blue_zero"]["path"])
        except Exception as e:
            print(f"⚠️ Could not load the Blue_zero fixture file: {e}")
            return

        # 3. Find potential attachment points (targets)
        from ezdxf.bbox import extents
        from shapely.geometry import box

        target_fixtures = []
        # First, search for the primary target: Discussion Tables
        for entity in self.msp.query('INSERT'):
            if "DISCUSSION_TABLE" in entity.dxf.name.upper():
                try:
                    bbox = extents([entity], fast=True)
                    target_fixtures.append(bbox)
                except (RuntimeError, TypeError):
                    continue
        
        # If no discussion tables were found, search for the fallback target: Euro Centres
        if not target_fixtures:
            print("ℹ️ No discussion tables found. Searching for Euro_centre fixtures as a fallback.")
            for entity in self.msp.query('INSERT'):
                if "EURO_CENTRE" in entity.dxf.name.upper():
                    try:
                        bbox = extents([entity], fast=True)
                        target_fixtures.append(bbox)
                    except (RuntimeError, TypeError):
                        continue

        # If still no targets are found, exit the function
        if not target_fixtures:
            print("ℹ️ No discussion tables or Euro centres were found to attach Blue_zero fixtures to.")
            return

        # 4. Attempt to place one "Blue_zero" for each target fixture, up to the requested count
        placed_count = 0
        margin_below = 50.0  # The gap between the target and the Blue_zero fixture

        for target_bbox in target_fixtures:
            # Stop if we have already placed the total number requested
            if placed_count >= blue_zero_count:
                break

            # Calculate the target position: centered horizontally and directly below the target
            target_x = target_bbox.center.x - (blue_zero_fxtr.width / 2)
            target_y = target_bbox.extmin.y - margin_below - blue_zero_fxtr.height

            # Create a candidate bounding box for validation checks
            candidate_box = box(target_x, target_y, target_x + blue_zero_fxtr.width, target_y + blue_zero_fxtr.height)

            # Check for collisions with any other fixture
            is_overlapping = any(candidate_box.intersects(box(*bbox)) for bbox in placed_bboxes)
            # Check that it's inside the main floorplan
            is_inside = self.floorplan_polygon.contains(candidate_box)

            # If the spot is clear and inside the room, place the fixture
            if is_inside and not is_overlapping:
                insert_point = (target_x, target_y, 0)
                self.place_fixture(blue_zero_fxtr, insert_point, 0, False)
                # Add the new fixture's bounding box to the list of obstacles
                placed_bboxes.append((target_x, target_y, target_x + blue_zero_fxtr.width, target_y + blue_zero_fxtr.height))
                print(f"✅ Placed Blue_zero below a fixture at ({target_x:.0f}, {target_y:.0f})")
                placed_count += 1
            else:
                print(f"ℹ️ Spot below a fixture was blocked or outside the boundary.")

        if placed_count < blue_zero_count:
            print(f"⚠️ Warning: Placed only {placed_count} of {blue_zero_count} requested Blue_zero fixtures as other spots were blocked.")

    def place_qms_from_center(self, placed_bboxes, bottom_margin_pct=0.10):
        """
        Places QMS desks using a center-out approach with a resilient search.
        If the ideal center spot is blocked, it searches left and right for a clear space.
        """
        from ezdxf.bbox import extents
        from shapely.geometry import box

        # 1. Get configuration
        config = self.fixtures.get("table_fixtures", {})
        qms_count = config.get("QMS_desk", 0)

        if qms_count <= 0:
            return

        print(f"\n--- Attempting to place {qms_count} QMS Desk(s) from center ---")

        # 2. Load the QMS fixture
        try:
            qms_fxtr = Fixture.Fixture("QMS_desk", self.fixture_dict["QMS_desk"]["path"])
        except Exception as e:
            print(f"🔥 Could not load QMS_desk fixture: {e}")
            return

        # 3. Find the Euro Centre anchor point
        euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
        if not euro_entities:
            print("⚠️ Cannot place QMS desks: Euro Centre anchor fixtures not found.")
            return
        
        euro_bbox = extents(euro_entities)
        
        # --- Helper function for validation ---
        def is_valid_spot(fixture, x, y):
            w, h = fixture.width, fixture.height
            candidate_box = box(x, y, x + w, y + h)
            is_overlapping = any(candidate_box.intersects(box(*bbox)) for bbox in placed_bboxes)
            is_inside = self.floorplan_polygon.contains(candidate_box)
            return is_inside and not is_overlapping

        # --- 4. Calculate position for the row ---
        room_height = self.cvc.max_y - self.cvc.min_y
        bottom_margin = room_height * bottom_margin_pct
        start_y = self.cvc.min_y + bottom_margin

        # --- 5. Place the first, central QMS desk with a resilient search ---
        qms_placed_count = 0
        placed_qms_bboxes = []
        
        # Calculate the ideal starting X
        ideal_x = euro_bbox.center.x - (qms_fxtr.width / 2)
        
        # NEW: Resilient search for the first desk
        first_desk_placed = False
        start_x, start_y = 0, 0 # Will be updated upon successful placement
        search_offset = 0
        max_search = (self.cvc.max_x - self.cvc.min_x) / 2 # Search up to half the room width

        while not first_desk_placed and search_offset < max_search:
            # Try right of center
            test_x = ideal_x + search_offset
            if is_valid_spot(qms_fxtr, test_x, self.cvc.min_y + bottom_margin):
                start_x, start_y = test_x, self.cvc.min_y + bottom_margin
                first_desk_placed = True
                break
            
            # Try left of center
            if search_offset > 0: # No need to check ideal_x - 0 twice
                test_x = ideal_x - search_offset
                if is_valid_spot(qms_fxtr, test_x, self.cvc.min_y + bottom_margin):
                    start_x, start_y = test_x, self.cvc.min_y + bottom_margin
                    first_desk_placed = True
                    break
            
            search_offset += 100 # Search increment of 100mm

        if first_desk_placed:
            self.place_fixture(qms_fxtr, (start_x, start_y, 0), 0, False)
            bbox_coords = (start_x, start_y, start_x + qms_fxtr.width, start_y + qms_fxtr.height)
            placed_bboxes.append(bbox_coords)
            placed_qms_bboxes.append(bbox_coords)
            qms_placed_count += 1
            print(f"✅ Placed central QMS_desk #{qms_placed_count} at {bottom_margin_pct*100:.0f}% from bottom wall.")
        else:
            print("⚠️ Could not place the first QMS_desk (center area blocked). Aborting placement.")
            return

        # --- 6. Place remaining desks to the left and right ---
        if qms_count > 1:
            # (This part of the logic remains the same as it already expands outwards)
            # qms_to_place = qms_count - 1
            # gap_horizontal = 1200
                        # vvv NEW DYNAMIC GAP LOGIC vvv
            # You can adjust these values to control the spacing behavior
            max_gap = 2000  # The wide gap used for a low count of desks
            min_gap = 1000   # The tight gap used when the count is high
            congestion_threshold = 5  # The number of desks at which the gap becomes its minimum

            
            if qms_count <= 3:
                gap_horizontal = max_gap
            elif qms_count >= congestion_threshold:
                gap_horizontal = min_gap
            else:
                # Linearly decrease the gap between the max and min based on the count
                progress = (qms_count - 2) / (congestion_threshold - 2)
                gap_horizontal = max_gap - (progress * (max_gap - min_gap))
            
            print(f"ℹ️ Dynamic horizontal gap set to {gap_horizontal:.0f}mm for {qms_count} desks.")
            # ^^^ END OF NEW LOGIC ^^^

            qms_to_place = qms_count - 1  # Already placed the first one
            
            leftmost_bbox = placed_qms_bboxes[0]
            rightmost_bbox = placed_qms_bboxes[0]

            for i in range(qms_to_place):
                if i % 2 == 0:  # Place to the left
                    target_x = leftmost_bbox[0] - gap_horizontal - qms_fxtr.width
                    if is_valid_spot(qms_fxtr, target_x, start_y):
                        self.place_fixture(qms_fxtr, (target_x, start_y, 0), 0, False)
                        bbox_coords = (target_x, start_y, target_x + qms_fxtr.width, start_y + qms_fxtr.height)
                        placed_bboxes.append(bbox_coords)
                        leftmost_bbox = bbox_coords
                        qms_placed_count += 1
                        print(f"✅ Placed QMS_desk #{qms_placed_count} to the left.")
                    else:
                        print(f"⚠️ Spot to the left is blocked. Skipping.")
                else:  # Place to the right
                    target_x = rightmost_bbox[2] + gap_horizontal
                    if is_valid_spot(qms_fxtr, target_x, start_y):
                        self.place_fixture(qms_fxtr, (target_x, start_y, 0), 0, False)
                        bbox_coords = (target_x, start_y, target_x + qms_fxtr.width, start_y + qms_fxtr.height)
                        placed_bboxes.append(bbox_coords)
                        rightmost_bbox = bbox_coords
                        qms_placed_count += 1
                        print(f"✅ Placed QMS_desk #{qms_placed_count} to the right.")
                    else:
                        print(f"⚠️ Spot to the right is blocked. Skipping.")

        print(f"-> Finished: Placed {qms_placed_count} of {qms_count} QMS desks.")


    # In DXF_Controller.py

    def place_corian_table_set_geometric_centroid(self, placed_bboxes):
        """
        Places Corian Table sets using a robust geometric centroid strategy.
        It finds the true center of the available floor space and places sets
        in a resilient, expanding pattern, making it ideal for polygon shapes.
        """
        from shapely.geometry import box, Polygon, MultiPolygon
        from shapely.ops import unary_union
        from ezdxf.bbox import extents
        import collections

        print("\n--- 🧠 Attempting to place Corian Table Set with Geometric Centroid Strategy ---")
        placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)

        # 1. SETUP: Load fixtures
        try:
            config = self.fixtures.get("Corian_table_set", {})
            num_sets = config.get("Corian_table", 0)
            if num_sets <= 0: return

            table_fxtr = Fixture.Fixture("Corian_table", self.fixture_dict["Corian_table"]["path"])
            seat_fxtr = Fixture.Fixture("Lounge_seat", self.fixture_dict["Lounge_seat"]["path"])
            sets_to_place_queue = collections.deque([1] * num_sets)
        except Exception as e:
            print(f"🔥 Error during Corian_table_set setup: {e}")
            return

        # 2. DEFINE SET GEOMETRY
        gap_table_to_seat = 100.0
        gap_between_seats = 50.0
        set_width = max(table_fxtr.width, (seat_fxtr.width * 2) + gap_between_seats)
        set_height = (seat_fxtr.height * 2) + table_fxtr.height + (gap_table_to_seat * 2)

        # 3. HELPER TO PLACE A SINGLE SET
        def _place_single_set(set_x, set_y):
            # This helper function's internal logic remains the same
            table_x = set_x + (set_width - table_fxtr.width) / 2
            table_y = set_y + seat_fxtr.height + gap_table_to_seat
            self.place_fixture(table_fxtr, (table_x, table_y, 0), 0, False)
            placed_bboxes.append((table_x, table_y, table_x + table_fxtr.width, table_y + table_fxtr.height))
            # ... (rest of component placement)
            top_seats_x_start = set_x + (set_width - (seat_fxtr.width * 2 + gap_between_seats)) / 2
            top_seats_y = table_y + table_fxtr.height + gap_table_to_seat
            self.place_fixture(seat_fxtr, (top_seats_x_start + seat_fxtr.width, top_seats_y + seat_fxtr.height, 0), 180, False)
            placed_bboxes.append((top_seats_x_start, top_seats_y, top_seats_x_start + seat_fxtr.width, top_seats_y + seat_fxtr.height))
            seat2_x = top_seats_x_start + seat_fxtr.width + gap_between_seats
            self.place_fixture(seat_fxtr, (seat2_x + seat_fxtr.width, top_seats_y + seat_fxtr.height, 0), 180, False)
            placed_bboxes.append((seat2_x, top_seats_y, seat2_x + seat_fxtr.width, seat_fxtr.height))
            bottom_seats_x_start = top_seats_x_start
            bottom_seats_y = set_y
            self.place_fixture(seat_fxtr, (bottom_seats_x_start, bottom_seats_y, 0), 0, False)
            placed_bboxes.append((bottom_seats_x_start, bottom_seats_y, bottom_seats_x_start + seat_fxtr.width, seat_fxtr.height))
            seat4_x = bottom_seats_x_start + seat_fxtr.width + gap_between_seats
            self.place_fixture(seat_fxtr, (seat4_x, bottom_seats_y, 0), 0, False)
            placed_bboxes.append((seat4_x, bottom_seats_y, seat4_x + seat_fxtr.width, seat_fxtr.height))


        # 4. **NEW** DEFINE AVAILABLE SPACE AND FIND CENTROID
        # Get all immovable obstacles (wall fixtures, clinics, etc.)
        obstacle_polygons = [box(*b) for b in self._get_accurate_obstacle_bboxes(include_all=False)]
        obstacles_union = unary_union(obstacle_polygons)
        
        # Subtract the obstacles from the main floorplan to find the available space
        available_space = self.floorplan_polygon.difference(obstacles_union)
        
        if available_space.is_empty:
            print("  -> SKIPPED: No available central space found.")
            return
            
        # Find the true geometric center of this available space
        centroid = available_space.centroid
        print(f"  -> Calculated true center of available space at ({centroid.x:.0f}, {centroid.y:.0f})")

        # 5. **NEW** RESILIENT SPIRAL PLACEMENT
        placed_count = 0
        # First, try to place at the centroid
        ideal_x = centroid.x - (set_width / 2)
        ideal_y = centroid.y - (set_height / 2)
        
        candidate_box = box(ideal_x, ideal_y, ideal_x + set_width, ideal_y + set_height)
        if available_space.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
            _place_single_set(ideal_x, ideal_y)
            placed_count += 1
            sets_to_place_queue.popleft()

        # For remaining sets, search outwards from the centroid
        search_radius = 150.0
        max_search_radius = max(self.cvc.distance_from_left, self.cvc.distance_from_bottom)
        
        while sets_to_place_queue and search_radius < max_search_radius:
            placed_in_ring = False
            for angle in range(0, 360, 30): # Check every 30 degrees around the center
                rad = math.radians(angle)
                test_x = ideal_x + search_radius * math.cos(rad)
                test_y = ideal_y + search_radius * math.sin(rad)
                
                candidate_box = box(test_x, test_y, test_x + set_width, test_y + set_height)
                if available_space.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                    _place_single_set(test_x, test_y)
                    placed_count += 1
                    sets_to_place_queue.popleft()
                    placed_in_ring = True
                    break # Move to the next set

            if not sets_to_place_queue:
                break
                
            # If a spot was found, reset the search radius to pack tightly. If not, expand the search.
            if placed_in_ring:
                search_radius += 150.0
            else:
                search_radius += 500.0 # Increase search radius faster if the current ring is full
                
        print(f"\n-> Finished Centroid Placement: Placed {placed_count} of {num_sets} requested sets.")
        

    # In DXF_Controller.py

    def place_corian_table_in_resilient_zone(self, placed_bboxes):
        """
        Places Corian Table sets using a resilient zone-fill strategy. It
        identifies the best functional zone and then places each set individually,
        searching for the first available clear space within that zone.
        """

        from shapely.geometry import box, Polygon, LineString
        from shapely.ops import unary_union
        import collections

        print("\n--- 🧠 Attempting to place Corian Table Set with Resilient Zone Fill ---")

        # 1. SETUP: Load fixtures
        try:
            config = self.fixtures.get("Corian_table_set", {})
            num_sets = config.get("Corian_table", 0)
            if num_sets <= 0: return

            table_fxtr = Fixture.Fixture("Corian_table", self.fixture_dict["Corian_table"]["path"])
            seat_fxtr = Fixture.Fixture("Lounge_seat", self.fixture_dict["Lounge_seat"]["path"])
        except Exception as e:
            print(f"🔥 Error during Corian_table_set setup: {e}")
            return

        # 2. DEFINE SET GEOMETRY
        gap_table_to_seat = 100.0
        gap_between_seats = 50.0
        set_width = max(table_fxtr.width, (seat_fxtr.width * 2) + gap_between_seats)
        set_height = (seat_fxtr.height * 2) + table_fxtr.height + (gap_table_to_seat * 2)

        # 3. HELPER TO PLACE A SINGLE SET
        def _place_single_set(set_x, set_y):
            # This helper function's internal logic remains the same
            table_x = set_x + (set_width - table_fxtr.width) / 2
            table_y = set_y + seat_fxtr.height + gap_table_to_seat
            self.place_fixture(table_fxtr, (table_x, table_y, 0), 0, False)
            placed_bboxes.append((table_x, table_y, table_x + table_fxtr.width, table_y + table_fxtr.height))
            # ... (rest of component placement logic)
            top_seats_x_start = set_x + (set_width - (seat_fxtr.width * 2 + gap_between_seats)) / 2
            top_seats_y = table_y + table_fxtr.height + gap_table_to_seat
            self.place_fixture(seat_fxtr, (top_seats_x_start + seat_fxtr.width, top_seats_y + seat_fxtr.height, 0), 180, False)
            placed_bboxes.append((top_seats_x_start, top_seats_y, top_seats_x_start + seat_fxtr.width, top_seats_y + seat_fxtr.height))
            seat2_x = top_seats_x_start + seat_fxtr.width + gap_between_seats
            self.place_fixture(seat_fxtr, (seat2_x + seat_fxtr.width, top_seats_y + seat_fxtr.height, 0), 180, False)
            placed_bboxes.append((seat2_x, top_seats_y, seat2_x + seat_fxtr.width, seat_fxtr.height))
            bottom_seats_x_start = top_seats_x_start
            bottom_seats_y = set_y
            self.place_fixture(seat_fxtr, (bottom_seats_x_start, bottom_seats_y, 0), 0, False)
            placed_bboxes.append((bottom_seats_x_start, bottom_seats_y, bottom_seats_x_start + seat_fxtr.width, seat_fxtr.height))
            seat4_x = bottom_seats_x_start + seat_fxtr.width + gap_between_seats
            self.place_fixture(seat_fxtr, (seat4_x, bottom_seats_y, 0), 0, False)
            placed_bboxes.append((seat4_x, bottom_seats_y, seat4_x + seat_fxtr.width, seat_fxtr.height))


        # 4. IDENTIFY THE BEST BACKDROP WALL AND ZONE
        all_obstacles = unary_union([box(*b) for b in placed_bboxes])
        best_wall = None
        
        for wall_side in ['top', 'bottom']:
            details = self._get_wall_details(wall_side)
            if not details: continue
            
            wall_line = LineString([details['start_point'], details['end_point']])
            zone_depth = set_height + 1000.0
            
            inward_normal = details['vector'].orthogonal().normalize()
            if not self.floorplan_polygon.contains(Point(wall_line.centroid.x + inward_normal.x, wall_line.centroid.y + inward_normal.y)):
                inward_normal = -inward_normal
                
            p1 = details['start_point'] + inward_normal * 100.0
            p2 = details['end_point'] + inward_normal * 100.0
            p3 = p2 + inward_normal * zone_depth
            p4 = p1 + inward_normal * zone_depth
            test_zone = Polygon([p1, p2, p3, p4])
            
            if not test_zone.intersects(all_obstacles):
                best_wall = details
                print(f"  -> Found ideal backdrop wall on the '{wall_side}' side.")
                break
                
        if not best_wall:
            print("  -> SKIPPED: Could not find a suitable clear wall to create a functional zone.")
            return

        # 5. **NEW** RESILIENTLY PLACE SETS WITHIN THE ZONE
        wall_vector = best_wall['vector'].normalize()
        inward_normal = wall_vector.orthogonal().normalize()
        if not self.floorplan_polygon.contains(Point(best_wall['start_point'] + inward_normal)):
            inward_normal = -inward_normal

        margin_from_wall = 600.0
        horizontal_gap_between_sets = 800.0
        
        zone_origin = best_wall['start_point'] + (inward_normal * margin_from_wall)
        
        # Calculate the ideal starting point (center of the wall)
        ideal_start_x_on_wall = best_wall['length'] / 2
        
        placed_count = 0
        placed_sets_bboxes = []

        for i in range(num_sets):
            found_spot = False
            # Search outwards from the center for a clear spot
            search_offset = 0
            while not found_spot:
                # Alternate searching right and left
                offset = (search_offset // 2) * (set_width + horizontal_gap_between_sets)
                if search_offset % 2 != 0:
                    offset *= -1
                
                cursor = ideal_start_x_on_wall + offset
                
                # Check if search is out of bounds on the wall
                if cursor < 0 or cursor + set_width > best_wall['length']:
                    if search_offset > best_wall['length'] / (set_width + horizontal_gap_between_sets) * 2:
                        break # Stop if we've searched all reasonable positions
                    search_offset += 1
                    continue

                top_left_point = zone_origin + (wall_vector * cursor)
                set_x = top_left_point.x
                set_y = top_left_point.y
                
                candidate_box = box(set_x, set_y, set_x + set_width, set_y + set_height)
                if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                    _place_single_set(set_x, set_y)
                    placed_count += 1
                    found_spot = True
                
                search_offset += 1

        print(f"\n-> Finished Resilient Zone Fill: Placed {placed_count} of {num_sets} requested sets.")

    def place_standing_tables_beside_euros_v1(self, placed_bboxes):
        """
        Places Standing Tables in two columns on the left and right sides of the
        Euro Centre fixtures, stacking vertically if the count is greater than 2.
        """
        from ezdxf.bbox import extents
        from shapely.geometry import box

        # 1. Get configuration
        config = self.fixtures.get("table_fixtures", {})
        standing_table_count = config.get("Standing_table", 0)

        if standing_table_count <= 0:
            return

        print(f"\n--- Attempting to place {standing_table_count} Standing Table(s) beside Euro Centres ---")

        # 2. Load the Standing Table fixture
        try:
            standing_fxtr = Fixture.Fixture("Standing_table", self.fixture_dict["Standing_table"]["path"])
        except Exception as e:
            print(f"🔥 Could not load Standing_table fixture: {e}")
            return

        # 3. Find the Euro Centre anchor point and room boundaries
        euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
        if not euro_entities:
            print("⚠️ Cannot place Standing Tables: Euro Centre anchor fixtures not found.")
            return
        
        euro_bbox = extents(euro_entities)
        room_min_x = self.cvc.min_x
        room_max_x = self.cvc.max_x
        
        # --- Helper function for validation ---
        def is_valid_spot(fixture, x, y):
            w, h = fixture.width, fixture.height
            candidate_box = box(x, y, x + w, y + h)
            is_overlapping = any(candidate_box.intersects(box(*bbox)) for bbox in placed_bboxes)
            is_inside = self.floorplan_polygon.contains(candidate_box)
            return is_inside and not is_overlapping

        # --- 4. Calculate starting positions and loop through placements ---
        placed_count = 0
        vertical_gap = 2500

        # Calculate the X coordinate for the right column
        center_x_right = (euro_bbox.extmax.x + room_max_x) / 2
        target_x_right = center_x_right - (standing_fxtr.width / 2)

        # Calculate the X coordinate for the left column
        center_x_left = (euro_bbox.extmin.x + room_min_x) / 2
        target_x_left = center_x_left - (standing_fxtr.width / 2)
        
        # These track the Y-positions for each column independently
        current_y_right = euro_bbox.extmin.y + vertical_gap
        current_y_left = euro_bbox.extmin.y + vertical_gap 

        for i in range(standing_table_count):
            # Alternate between placing on the right and left
            if i % 2 == 0:  # Place on the RIGHT side first
                target_x = target_x_right
                target_y = current_y_right
                side = "right"
            else:  # Place on the LEFT side second
                target_x = target_x_left
                target_y = current_y_left
                side = "left"

            if is_valid_spot(standing_fxtr, target_x, target_y):
                self.place_fixture(standing_fxtr, (target_x, target_y, 0), 0, False)
                bbox_coords = (target_x, target_y, target_x + standing_fxtr.width, target_y + standing_fxtr.height)
                placed_bboxes.append(bbox_coords)
                placed_count += 1
                print(f"✅ Placed Standing_table #{i+1} on the {side} of Euro Centres.")
                
                # Update the Y-cursor for the column where the table was just placed
                if side == "right":
                    current_y_right += standing_fxtr.height + vertical_gap
                else:
                    current_y_left += standing_fxtr.height + vertical_gap
            else:
                print(f"⚠️ Could not place Standing_table #{i+1} on the {side} (spot blocked).")

        print(f"-> Finished: Placed {placed_count} of {standing_table_count} Standing Tables.")


    def place_standing_tables_beside_euros_v2(self, placed_bboxes):
        """
        Places Standing Tables using a multi-strategy approach.
        - Strategy 1 (Primary): Places the first table centered ABOVE the Euro Centre cluster.
        - Strategy 2 (NEW): Places subsequent tables in a "center-out" row next to the first one.
        - Strategy 3 (Fallback): Places any remaining tables in columns to the left and right.
        """
        from ezdxf.bbox import extents
        from shapely.geometry import box
        import collections

        # 1. Get configuration
        config = self.fixtures.get("table_fixtures", {})
        standing_table_count = config.get("Standing_table", 0)
        if standing_table_count <= 0:
            return

        print(f"\n--- Attempting to place {standing_table_count} Standing Table(s) with multi-strategy logic ---")

        # 2. Load the Standing Table fixture
        try:
            standing_fxtr = Fixture.Fixture("Standing_table", self.fixture_dict["Standing_table"]["path"])
        except Exception as e:
            print(f"🔥 Could not load Standing_table fixture: {e}")
            return

        # 3. Find the Euro Centre anchor point
        euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
        if not euro_entities:
            print("⚠️ Cannot place Standing Tables: Euro Centre anchor fixtures not found.")
            return
        
        euro_bbox = extents(euro_entities)
        
        # --- Helper function for validation ---
        def is_valid_spot(fixture, x, y):
            w, h = fixture.width, fixture.height
            candidate_box = box(x, y, x + w, y + h)
            is_overlapping = any(candidate_box.intersects(box(*bbox)) for bbox in placed_bboxes)
            is_inside = self.floorplan_polygon.contains(candidate_box)
            return is_inside and not is_overlapping

        # --- Placement Logic ---
        placed_count = 0
        remaining_to_place = collections.deque(range(standing_table_count))
        
        # --- Strategy 1: Place First Table Above Euro Centres ---
        first_table_bbox = None
        if remaining_to_place:
            print("  -> Attempting Strategy 1: Place first table centered ABOVE Euro Centres...")
            gap_above_euros = 600.0
            
            ideal_x = euro_bbox.center.x - (standing_fxtr.width / 2)
            ideal_y = euro_bbox.extmax.y + gap_above_euros
            
            if is_valid_spot(standing_fxtr, ideal_x, ideal_y):
                self.place_fixture(standing_fxtr, (ideal_x, ideal_y, 0), 0, False)
                first_table_bbox = (ideal_x, ideal_y, ideal_x + standing_fxtr.width, ideal_y + standing_fxtr.height)
                placed_bboxes.append(first_table_bbox)
                placed_count += 1
                remaining_to_place.popleft()
                print(f"    ✅ SUCCESS: Placed Standing_table #1 above Euro Centres.")
            else:
                print("    -> FAILED: The spot above the Euro Centres is blocked.")

        # --- NEW: Strategy 2 - Place Remaining Tables in a "Center-Out" Row ---
        if remaining_to_place and first_table_bbox is not None:
            print(f"\n  -> Attempting Strategy 2: Placing {len(remaining_to_place)} tables in a center-out row...")
            HORIZONTAL_GAP_ABOVE = 800.0
            
            leftmost_bbox = first_table_bbox
            rightmost_bbox = first_table_bbox
            tables_placed_in_row = 0

            # Create a temporary list to iterate over, as we'll modify the deque
            items_in_this_strategy = list(remaining_to_place)
            
            for i in range(len(items_in_this_strategy)):
                # Alternate placing to the right and left of the initial group
                if i % 2 == 0: # Place to the RIGHT
                    target_x = rightmost_bbox[2] + HORIZONTAL_GAP_ABOVE
                    side = "right"
                else: # Place to the LEFT
                    target_x = leftmost_bbox[0] - HORIZONTAL_GAP_ABOVE - standing_fxtr.width
                    side = "left"

                target_y = first_table_bbox[1] # Keep the same Y-level

                if is_valid_spot(standing_fxtr, target_x, target_y):
                    remaining_to_place.popleft() # Successfully placing, so remove from queue
                    self.place_fixture(standing_fxtr, (target_x, target_y, 0), 0, False)
                    new_bbox = (target_x, target_y, target_x + standing_fxtr.width, target_y + standing_fxtr.height)
                    placed_bboxes.append(new_bbox)
                    placed_count += 1
                    
                    if side == "right":
                        rightmost_bbox = new_bbox
                    else:
                        leftmost_bbox = new_bbox
                        
                    print(f"✅ Placed Standing_table #{placed_count} to the {side} in the top row.")
                else:
                    print(f"⚠️ Spot to the {side} in the top row is blocked. Stopping center-out placement.")
                    break # Stop this strategy if a spot is blocked

        # --- Strategy 3 (Fallback): Place any leftovers in Side Columns ---
        if remaining_to_place:
            print(f"\n  -> Attempting Strategy 3 (Fallback): Placing {len(remaining_to_place)} tables in side columns...")
            vertical_gap = 2500.0
            
            center_x_right = (euro_bbox.extmax.x + self.cvc.max_x) / 2
            target_x_right = center_x_right - (standing_fxtr.width / 2)
            center_x_left = (euro_bbox.extmin.x + self.cvc.min_x) / 2
            target_x_left = center_x_left - (standing_fxtr.width / 2)
            
            current_y_right = euro_bbox.extmin.y + vertical_gap
            current_y_left = euro_bbox.extmin.y + vertical_gap

            items_in_fallback = list(remaining_to_place)
            for i in range(len(items_in_fallback)):
                if i % 2 == 0:
                    target_x, target_y, side = target_x_right, current_y_right, "right"
                else:
                    target_x, target_y, side = target_x_left, current_y_left, "left"

                if is_valid_spot(standing_fxtr, target_x, target_y):
                    remaining_to_place.popleft()
                    self.place_fixture(standing_fxtr, (target_x, target_y, 0), 0, False)
                    placed_bboxes.append((target_x, target_y, target_x + standing_fxtr.width, target_y + standing_fxtr.height))
                    placed_count += 1
                    print(f"✅ Placed Standing_table #{placed_count} on the {side} of Euro Centres.")
                    
                    if side == "right":
                        current_y_right += standing_fxtr.height + vertical_gap
                    else:
                        current_y_left += standing_fxtr.height + vertical_gap
                else:
                    print(f"⚠️ Could not place Standing_table #{placed_count + 1} on the {side} (spot blocked).")

        print(f"\n-> Finished: Placed {placed_count} of {standing_table_count} Standing Tables.")


    def place_standing_tables_beside_euros(self, placed_bboxes):
        """
        Places Standing Tables using a dynamic strategy based on the total count.
        - ODD COUNT: Places one table in the center and expands outwards.
        - EVEN COUNT: Places a single, perfectly centered horizontal row.
        - FALLBACK: Places any remaining tables in side columns.
        """
        from ezdxf.bbox import extents
        from shapely.geometry import box
        import collections

        # 1. Get configuration
        config = self.fixtures.get("table_fixtures", {})
        standing_table_count = config.get("Standing_table", 0)
        if standing_table_count <= 0:
            return

        print(f"\n--- Attempting to place {standing_table_count} Standing Table(s) with ODD/EVEN logic ---")

        # 2. Load fixture and find anchor
        try:
            standing_fxtr = Fixture.Fixture("Standing_table", self.fixture_dict["Standing_table"]["path"])
        except Exception as e:
            print(f"🔥 Could not load Standing_table fixture: {e}")
            return

        euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
        if not euro_entities:
            print("⚠️ Cannot place Standing Tables: Euro Centre anchor fixtures not found.")
            return
        
        euro_bbox = extents(euro_entities)
        
        # 3. Define parameters and helper
        gap_above_euros = 600.0
        horizontal_gap = 1000.0
        
        def is_valid_spot(fixture, x, y):
            w, h = fixture.width, fixture.height
            candidate_box = box(x, y, x + w, y + h)
            is_overlapping = any(candidate_box.intersects(box(*bbox)) for bbox in placed_bboxes)
            is_inside = self.floorplan_polygon.contains(candidate_box)
            return is_inside and not is_overlapping

        # 4. Main Placement Logic
        placed_count = 0
        remaining_to_place = collections.deque(range(standing_table_count))
        
        # --- ODD COUNT STRATEGY ---
        if standing_table_count % 2 != 0:
            print(f"  -> ODD count detected. Using 'Center-Out' strategy.")
            
            # Place the first, central table
            ideal_x = euro_bbox.center.x - (standing_fxtr.width / 2)
            ideal_y = euro_bbox.extmax.y + gap_above_euros
            
            if is_valid_spot(standing_fxtr, ideal_x, ideal_y):
                self.place_fixture(standing_fxtr, (ideal_x, ideal_y, 0), 0, False)
                first_bbox = (ideal_x, ideal_y, ideal_x + standing_fxtr.width, ideal_y + standing_fxtr.height)
                placed_bboxes.append(first_bbox)
                placed_count += 1
                remaining_to_place.popleft()
                
                # Now place the rest in pairs
                leftmost_bbox = first_bbox
                rightmost_bbox = first_bbox
                
                while remaining_to_place:
                    # Place pair to the right
                    target_x_r = rightmost_bbox[2] + horizontal_gap
                    if is_valid_spot(standing_fxtr, target_x_r, ideal_y):
                        self.place_fixture(standing_fxtr, (target_x_r, ideal_y, 0), 0, False)
                        new_bbox_r = (target_x_r, ideal_y, target_x_r + standing_fxtr.width, ideal_y + standing_fxtr.height)
                        placed_bboxes.append(new_bbox_r)
                        rightmost_bbox = new_bbox_r
                        placed_count += 1
                        remaining_to_place.popleft()
                    else:
                        break # Stop if space runs out

                    if not remaining_to_place: break

                    # Place pair to the left
                    target_x_l = leftmost_bbox[0] - horizontal_gap - standing_fxtr.width
                    if is_valid_spot(standing_fxtr, target_x_l, ideal_y):
                        self.place_fixture(standing_fxtr, (target_x_l, ideal_y, 0), 0, False)
                        new_bbox_l = (target_x_l, ideal_y, target_x_l + standing_fxtr.width, ideal_y + standing_fxtr.height)
                        placed_bboxes.append(new_bbox_l)
                        leftmost_bbox = new_bbox_l
                        placed_count += 1
                        remaining_to_place.popleft()
                    else:
                        break # Stop if space runs out
        
        # --- EVEN COUNT STRATEGY ---
        else:
            print(f"  -> EVEN count detected. Using 'Centered Row' strategy.")
            total_row_width = (standing_table_count * standing_fxtr.width) + ((standing_table_count - 1) * horizontal_gap)
            
            # Calculate the start of the row to center it
            row_start_x = euro_bbox.center.x - (total_row_width / 2)
            row_y = euro_bbox.extmax.y + gap_above_euros
            
            # First, check if the entire row will fit
            row_box = box(row_start_x, row_y, row_start_x + total_row_width, row_y + standing_fxtr.height)
            if self.floorplan_polygon.contains(row_box) and not any(row_box.intersects(box(*b)) for b in placed_bboxes):
                current_x = row_start_x
                for _ in range(standing_table_count):
                    self.place_fixture(standing_fxtr, (current_x, row_y, 0), 0, False)
                    placed_bboxes.append((current_x, row_y, current_x + standing_fxtr.width, row_y + standing_fxtr.height))
                    current_x += standing_fxtr.width + horizontal_gap
                placed_count = standing_table_count
                remaining_to_place.clear()
            else:
                print("    -> FAILED: The centered row is blocked or outside the boundary.")

        # --- FALLBACK STRATEGY ---
        if placed_count < standing_table_count:
            # Recalculate remaining to place from the original count
            num_to_place_fallback = standing_table_count - placed_count
            print(f"\n  -> Attempting Fallback: Placing {num_to_place_fallback} tables in side columns...")
            
            vertical_gap = 2500.0
            center_x_right = (euro_bbox.extmax.x + self.cvc.max_x) / 2
            target_x_right = center_x_right - (standing_fxtr.width / 2)
            center_x_left = (euro_bbox.extmin.x + self.cvc.min_x) / 2
            target_x_left = center_x_left - (standing_fxtr.width / 2)
            
            current_y_right = euro_bbox.extmin.y + vertical_gap
            current_y_left = euro_bbox.extmin.y + vertical_gap

            for i in range(num_to_place_fallback):
                if i % 2 == 0:
                    target_x, target_y, side = target_x_right, current_y_right, "right"
                else:
                    target_x, target_y, side = target_x_left, current_y_left, "left"

                if is_valid_spot(standing_fxtr, target_x, target_y):
                    self.place_fixture(standing_fxtr, (target_x, target_y, 0), 0, False)
                    placed_bboxes.append((target_x, target_y, target_x + standing_fxtr.width, target_y + standing_fxtr.height))
                    placed_count += 1
                    
                    if side == "right": current_y_right += standing_fxtr.height + vertical_gap
                    else: current_y_left += standing_fxtr.height + vertical_gap
                else:
                    print(f"⚠️ Could not place fallback table on the {side} (spot blocked).")
        
        print(f"\n-> Finished: Placed {placed_count} of {standing_table_count} Standing Tables.")


    def place_lensbar_v1(self, placed_bboxes):
        """
        Places one or more Lensbar fixtures using a new, prioritized four-strategy approach.

        Strategy 1 (Primary): Anchors placement relative to the MEDIAN Euro_centre.
        Strategy 2 (Conditional): Anchors placement relative to the THIRD Euro_centre if the count is odd and >= 3.
        Strategy 3 (Fallback): Grid search in left and right central zones.
        Strategy 4 (Final Fallback): Parallel-to-wall placement.
        """
        from shapely.geometry import box, Point
        from ezdxf.math import Matrix44, Vec2
        from ezdxf.bbox import extents
        import math

        print("\n--- Attempting to place Lensbar(s) with 4-strategy logic ---")
        
        # 1. SETUP
        try:
            config = self.fixtures.get("lensbar_and_dropbox", {})
            lensbar_count = config.get("Lensbar", 0)
            if lensbar_count <= 0:
                print("ℹ️ No Lensbar fixtures specified for placement.")
                return
            lensbar_fxtr = Fixture.Fixture("Lensbar", self.fixture_dict["Lensbar"]["path"])
        except Exception as e:
            print(f"🔥 Error during Lensbar setup: {e}")
            return

        # --- HELPER FUNCTION for intelligent searching ---
        def find_valid_spot_near(start_x, start_y, fixture_obj, search_radius=1000, step=100):
            """
            Searches for a valid spot in a spiral pattern around a starting point.
            Returns (x, y) of a valid spot, or None if no spot is found.
            """
            candidate_box = box(start_x, start_y, start_x + fixture_obj.width, start_y + fixture_obj.height)
            if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*bbox)) for bbox in placed_bboxes):
                return (start_x, start_y)

            x, y = start_x, start_y
            dx, dy = 0, -step
            for _ in range(int(search_radius / step) ** 2):
                if (-search_radius/2 < x-start_x < search_radius/2) and (-search_radius/2 < y-start_y < search_radius/2):
                    candidate_box = box(x, y, x + fixture_obj.width, y + fixture_obj.height)
                    if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*bbox)) for bbox in placed_bboxes):
                        return (x, y)
                if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
                    dx, dy = -dy, dx
                x, y = x + dx, y + dy
            return None

        placed_count = 0
        
        # --- Shared Setup for Euro-based Strategies ---
        euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
        euro_bboxes = []
        if euro_entities:
            euro_bboxes = sorted([extents([e]) for e in euro_entities if extents([e])], key=lambda b: b.extmin.y)

        # =================================================================
        # STRATEGY 1: MEDIAN EURO CENTRE ANCHORED PLACEMENT
        # =================================================================
        print("  -> Attempting Strategy 1: Median Euro Centre Anchored Placement...")
        
        if euro_bboxes:
            num_euros = len(euro_bboxes)
            y_anchor = (euro_bboxes[num_euros // 2].center.y if num_euros % 2 == 1 
                        else (euro_bboxes[num_euros // 2 - 1].extmax.y + euro_bboxes[num_euros // 2].extmin.y) / 2)

            euro_stack_bbox = extents(euro_entities)
            room_min_x, room_max_x = self.cvc.min_x, self.cvc.max_x
            
            space_right = room_max_x - euro_stack_bbox.extmax.x
            x_right_col_ideal = euro_stack_bbox.extmax.x + (space_right / 2) - (lensbar_fxtr.width / 2)
            
            space_left = euro_stack_bbox.extmin.x - room_min_x
            x_left_col_ideal = room_min_x + (space_left / 2) - (lensbar_fxtr.width / 2)

            y_cursor_right = y_anchor - (lensbar_fxtr.height / 2)
            y_cursor_left = y_anchor - (lensbar_fxtr.height / 2)
            vertical_gap = 200

            for i in range(lensbar_count):
                if placed_count >= lensbar_count: break
                if i % 2 == 0: # Place on the RIGHT side
                    valid_spot = find_valid_spot_near(x_right_col_ideal, y_cursor_right, lensbar_fxtr)
                    if valid_spot:
                        x, y = valid_spot
                        self.place_fixture(lensbar_fxtr, (x, y, 0), 90, False)
                        placed_bboxes.append((x, y, x + lensbar_fxtr.width, y + lensbar_fxtr.height))
                        print(f"    ✅ SUCCESS: Placed Lensbar #{placed_count + 1} via Strategy 1 (Right).")
                        y_cursor_right += lensbar_fxtr.height + vertical_gap
                        placed_count += 1
                else: # Place on the LEFT side
                    valid_spot = find_valid_spot_near(x_left_col_ideal, y_cursor_left, lensbar_fxtr)
                    if valid_spot:
                        x, y = valid_spot
                        self.place_fixture(lensbar_fxtr, (x, y, 0), 0, False)
                        placed_bboxes.append((x, y, x + lensbar_fxtr.width, y + lensbar_fxtr.height))
                        print(f"    ✅ SUCCESS: Placed Lensbar #{placed_count + 1} via Strategy 1 (Left).")
                        y_cursor_left += lensbar_fxtr.height + vertical_gap
                        placed_count += 1
        else:
            print("  -> Strategy 1 skipped: No Euro_centre fixtures found.")

        if placed_count >= lensbar_count:
            print(f"\n-> Finished Lensbar Placement: Placed {placed_count} of {lensbar_count} requested fixtures.")
            return

        # =================================================================
        # STRATEGY 2: THIRD EURO CENTRE ANCHORED PLACEMENT (Conditional)
        # =================================================================
        print("\n  -> Attempting Strategy 2: Third Euro Centre Anchored Placement...")
        num_euros = len(euro_bboxes)
        if num_euros >= 3 and num_euros % 2 == 1:
            # This strategy only runs for odd counts of 3 or more Euros
            y_anchor_s2 = euro_bboxes[2].center.y # Index 2 is the third Euro

            euro_stack_bbox = extents(euro_entities)
            room_min_x, room_max_x = self.cvc.min_x, self.cvc.max_x
            
            space_right = room_max_x - euro_stack_bbox.extmax.x
            x_right_col_s2 = euro_stack_bbox.extmax.x + (space_right / 2) - (lensbar_fxtr.width / 2)
            
            space_left = euro_stack_bbox.extmin.x - room_min_x
            x_left_col_s2 = room_min_x + (space_left / 2) - (lensbar_fxtr.width / 2)

            y_cursor_right_s2 = y_anchor_s2 - (lensbar_fxtr.height / 2)
            y_cursor_left_s2 = y_anchor_s2 - (lensbar_fxtr.height / 2)
            vertical_gap_s2 = 200
            
            items_to_place_s2 = range(lensbar_count - placed_count)
            for i in items_to_place_s2:
                if i % 2 == 0: # Place RIGHT
                    valid_spot = find_valid_spot_near(x_right_col_s2, y_cursor_right_s2, lensbar_fxtr)
                    if valid_spot:
                        x, y = valid_spot
                        self.place_fixture(lensbar_fxtr, (x, y, 0), 0, False)
                        placed_bboxes.append((x, y, x + lensbar_fxtr.width, y + lensbar_fxtr.height))
                        print(f"    ✅ SUCCESS: Placed Lensbar #{placed_count + 1} via Strategy 2 (Right).")
                        y_cursor_right_s2 += lensbar_fxtr.height + vertical_gap_s2
                        placed_count += 1
                else: # Place LEFT
                    valid_spot = find_valid_spot_near(x_left_col_s2, y_cursor_left_s2, lensbar_fxtr)
                    if valid_spot:
                        x, y = valid_spot
                        self.place_fixture(lensbar_fxtr, (x, y, 0), 0, False)
                        placed_bboxes.append((x, y, x + lensbar_fxtr.width, y + lensbar_fxtr.height))
                        print(f"    ✅ SUCCESS: Placed Lensbar #{placed_count + 1} via Strategy 2 (Left).")
                        y_cursor_left_s2 += lensbar_fxtr.height + vertical_gap_s2
                        placed_count += 1
        else:
            print("  -> Strategy 2 skipped: Condition not met (Euro count is not odd and >= 3).")

        if placed_count >= lensbar_count:
            print(f"\n-> Finished Lensbar Placement: Placed {placed_count} of {lensbar_count} requested fixtures.")
            return

        # =================================================================
        # STRATEGY 3: CENTRAL AREA GRID SEARCH (Fallback)
        # =================================================================
        print("\n  -> Attempting Strategy 3: Grid Search in Left/Right Central Zones...")
        # (This logic is now Strategy 3)
        room_w = self.cvc.max_x - self.cvc.min_x
        room_h = self.cvc.max_y - self.cvc.min_y
        central_x_start = self.cvc.min_x + room_w * 0.20
        central_x_end = self.cvc.max_x - room_w * 0.20
        central_y_start = self.cvc.min_y + room_h * 0.30
        central_y_end = self.cvc.max_y - room_h * 0.30
        zone_center_x = central_x_start + (central_x_end - central_x_start) / 2

        def grid_search_zone(x_start, x_end, y_start, y_end):
            y = y_start
            while y < (y_end - lensbar_fxtr.height):
                x = x_start
                while x < (x_end - lensbar_fxtr.width):
                    valid_spot = find_valid_spot_near(x, y, lensbar_fxtr, search_radius=200, step=50)
                    if valid_spot: return valid_spot
                    x += 100
                y += 100
            return None

        while placed_count < lensbar_count:
            found_spot = grid_search_zone(zone_center_x, central_x_end, central_y_start, central_y_end)
            if not found_spot:
                found_spot = grid_search_zone(central_x_start, zone_center_x, central_y_start, central_y_end)
            
            if found_spot:
                x, y = found_spot
                self.place_fixture(lensbar_fxtr, (x, y, 0), 0, False)
                placed_bboxes.append((x, y, x + lensbar_fxtr.width, y + lensbar_fxtr.height))
                print(f"    ✅ SUCCESS: Placed Lensbar #{placed_count + 1} via Strategy 3 (Grid Search).")
                placed_count += 1
            else:
                print(f"    ⚠️ FAILED: No grid search spot found. Aborting Strategy 3.")
                break

        if placed_count >= lensbar_count:
            print(f"\n-> Finished Lensbar Placement: Placed {placed_count} of {lensbar_count} requested fixtures.")
            return

        # =================================================================
        # STRATEGY 4: PARALLEL-TO-WALL PLACEMENT (Final Fallback)
        # =================================================================
        print("\n  -> Attempting Strategy 4: Parallel-to-Wall Placement...")
        # (This logic is now Strategy 4)
        all_segments = self.cvc.get_wall_segments(min_length=lensbar_fxtr.width + 200)
        for segment in all_segments:
            if placed_count >= lensbar_count: break
            # ... (full logic to walk along the wall and check for space) ...
            
        print(f"\n-> Finished Lensbar Placement: Placed {placed_count} of {lensbar_count} requested fixtures.")
        if placed_count < lensbar_count:
            print(f"    ⚠️ WARNING: Only {placed_count} Lensbars placed. Some may not fit.")


    def place_lensbar(self, placed_bboxes):
        """
        Places one or more Lensbar fixtures using a new, prioritized four-strategy approach.
        - STRATEGY 1 (MODIFIED): Places fixtures with 90-degree rotation, centered
        in the aisles between Euro Centres and the corresponding wall fixtures.
        """
        from shapely.geometry import box, Point
        from ezdxf.math import Matrix44, Vec2
        from ezdxf.bbox import extents
        import math

        print("\n--- Attempting to place Lensbar(s) with 4-strategy logic (Aisle-Centering Update) ---")
        
        # 1. SETUP (No changes here)
        try:
            # --- MODIFIED: The config is in "floor_fixtures", not "lensbar_and_dropbox" ---
            config = self.fixtures.get("lensbar_and_dropbox", {})
            lensbar_count = config.get("Lensbar", 0)
            if lensbar_count <= 0:
                print("ℹ️ No Lensbar fixtures specified for placement.")
                return
            lensbar_fxtr = Fixture.Fixture("Lensbar", self.fixture_dict["Lensbar"]["path"])
        except Exception as e:
            print(f"🔥 Error during Lensbar setup: {e}")
            return

        # HELPER FUNCTION (No changes here)
        def find_valid_spot_near(start_x, start_y, fixture_obj, search_radius=1000, step=100):
            candidate_box = box(start_x, start_y, start_x + fixture_obj.width, start_y + fixture_obj.height)
            if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*bbox)) for bbox in placed_bboxes):
                return (start_x, start_y)
            x, y = start_x, start_y
            dx, dy = 0, -step
            for _ in range(int(search_radius / step) ** 2):
                if (-search_radius/2 < x-start_x < search_radius/2) and (-search_radius/2 < y-start_y < search_radius/2):
                    candidate_box = box(x, y, x + fixture_obj.width, y + fixture_obj.height)
                    if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*bbox)) for bbox in placed_bboxes):
                        return (x, y)
                if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
                    dx, dy = -dy, dx
                x, y = x + dx, y + dy
            return None

        placed_count = 0
        
        euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
        euro_bboxes = []
        if euro_entities:
            euro_bboxes = sorted([extents([e]) for e in euro_entities if extents([e])], key=lambda b: b.extmin.y)

        # =================================================================
        # STRATEGY 1: AISLE-CENTERED PLACEMENT (COMPLETELY REVISED)
        # =================================================================
        print("  -> Attempting Strategy 1: Aisle-Centered Placement...")
        
        if euro_bboxes:
            euro_stack_bbox = extents(euro_entities)
            
            # --- NEW LOGIC: Find the boundaries of the wall fixtures ---
            left_wall_fixtures = []
            right_wall_fixtures = []
            room_center_x = self.floorplan_polygon.centroid.x

            for entity in self.msp.query('INSERT'):
                # Find the fixture type from our master dictionary
                block_name_key = entity.dxf.name.split('_')[0].lower()
                fixture_info = self.fixture_dict.get(block_name_key)
                if fixture_info and fixture_info.get("type") == "wall":
                    if entity.dxf.insert.x < room_center_x:
                        left_wall_fixtures.append(entity)
                    else:
                        right_wall_fixtures.append(entity)
            
            # --- NEW LOGIC: Calculate the inner edges of the wall fixture groups ---
            # Default to the room boundaries if no wall fixtures are found
            left_wall_boundary = self.cvc.min_x
            if left_wall_fixtures:
                left_wall_boundary = extents(left_wall_fixtures).extmax.x
                print(f"    -> Found Left Wall Fixture boundary at x={left_wall_boundary:.0f}")

            right_wall_boundary = self.cvc.max_x
            if right_wall_fixtures:
                right_wall_boundary = extents(right_wall_fixtures).extmin.x
                print(f"    -> Found Right Wall Fixture boundary at x={right_wall_boundary:.0f}")

            # --- NEW LOGIC: Calculate the center of each aisle ---
            # Right Aisle Calculation
            aisle_right_start_x = euro_stack_bbox.extmax.x
            aisle_right_end_x = right_wall_boundary
            aisle_right_width = aisle_right_end_x - aisle_right_start_x
            aisle_right_center_x = aisle_right_start_x + (aisle_right_width / 2)

            # Left Aisle Calculation
            aisle_left_start_x = left_wall_boundary
            aisle_left_end_x = euro_stack_bbox.extmin.x
            aisle_left_width = aisle_left_end_x - aisle_left_start_x
            aisle_left_center_x = aisle_left_start_x + (aisle_left_width / 2)

            # --- MODIFIED: Vertical alignment and placement loop ---
            num_euros = len(euro_bboxes)
            y_anchor = (euro_bboxes[num_euros // 2].center.y if num_euros % 2 == 1 
                        else (euro_bboxes[num_euros // 2 - 1].extmax.y + euro_bboxes[num_euros // 2].extmin.y) / 2)

            # --- MODIFIED: When rotated, the footprint (width) is the fixture's original height ---
            rotated_fixture_width = lensbar_fxtr.height
            rotated_fixture_height = lensbar_fxtr.width
            
            y_cursor_right = y_anchor - (rotated_fixture_height / 2)
            y_cursor_left = y_anchor - (rotated_fixture_height / 2)
            vertical_gap = 200

            for i in range(lensbar_count):
                if placed_count >= lensbar_count: break
                
                # Place on the RIGHT side
                if i % 2 == 0:
                    # --- MODIFIED: Calculate the ideal X position for the centered, rotated fixture ---
                    ideal_x = aisle_right_center_x - (rotated_fixture_width / 2)
                    
                    candidate_box = box(ideal_x, y_cursor_right, ideal_x + rotated_fixture_width, y_cursor_right + rotated_fixture_height)
                    if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                        # --- MODIFIED: Use rotation=90 and adjust insert point ---
                        # For a 90-degree rotation, the handle (extmin) is at the top-left of the original DXF.
                        # The insertion point must be the top-left corner of the final bounding box.
                        final_insert_point = (ideal_x + rotated_fixture_width, y_cursor_right, 0)
                        self.place_fixture(lensbar_fxtr, final_insert_point, 90, True)
                        
                        placed_bboxes.append(candidate_box.bounds)
                        print(f"    ✅ SUCCESS: Placed Lensbar #{placed_count + 1} via Strategy 1 (Right Aisle).")
                        y_cursor_right += rotated_fixture_height + vertical_gap
                        placed_count += 1
                
                # Place on the LEFT side
                else:
                    # --- MODIFIED: Calculate the ideal X position ---
                    ideal_x = aisle_left_center_x - (rotated_fixture_width / 2)
                    
                    candidate_box = box(ideal_x, y_cursor_left, ideal_x + rotated_fixture_width, y_cursor_left + rotated_fixture_height)
                    if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                        # --- MODIFIED: Use rotation=90 and adjust insert point ---
                        final_insert_point = (ideal_x + rotated_fixture_width, y_cursor_left, 0)
                        self.place_fixture(lensbar_fxtr, final_insert_point, 90, True)
                        
                        placed_bboxes.append(candidate_box.bounds)
                        print(f"    ✅ SUCCESS: Placed Lensbar #{placed_count + 1} via Strategy 1 (Left Aisle).")
                        y_cursor_left += rotated_fixture_height + vertical_gap
                        placed_count += 1
        else:
            print("  -> Strategy 1 skipped: No Euro_centre fixtures found.")
            
        # =================================================================
        # STRATEGY 2: THIRD EURO CENTRE ANCHORED PLACEMENT (Conditional)
        # =================================================================
        print("\n  -> Attempting Strategy 2: Third Euro Centre Anchored Placement...")
        num_euros = len(euro_bboxes)
        if num_euros >= 3 and num_euros % 2 == 1:
            # This strategy only runs for odd counts of 3 or more Euros
            y_anchor_s2 = euro_bboxes[2].center.y # Index 2 is the third Euro

            euro_stack_bbox = extents(euro_entities)
            room_min_x, room_max_x = self.cvc.min_x, self.cvc.max_x
            
            space_right = room_max_x - euro_stack_bbox.extmax.x
            x_right_col_s2 = euro_stack_bbox.extmax.x + (space_right / 2) - (lensbar_fxtr.width / 2)
            
            space_left = euro_stack_bbox.extmin.x - room_min_x
            x_left_col_s2 = room_min_x + (space_left / 2) - (lensbar_fxtr.width / 2)

            y_cursor_right_s2 = y_anchor_s2 - (lensbar_fxtr.height / 2)
            y_cursor_left_s2 = y_anchor_s2 - (lensbar_fxtr.height / 2)
            vertical_gap_s2 = 200
            
            items_to_place_s2 = range(lensbar_count - placed_count)
            for i in items_to_place_s2:
                if i % 2 == 0: # Place RIGHT
                    valid_spot = find_valid_spot_near(x_right_col_s2, y_cursor_right_s2, lensbar_fxtr)
                    if valid_spot:
                        x, y = valid_spot
                        self.place_fixture(lensbar_fxtr, (x, y, 0), 0, False)
                        placed_bboxes.append((x, y, x + lensbar_fxtr.width, y + lensbar_fxtr.height))
                        print(f"    ✅ SUCCESS: Placed Lensbar #{placed_count + 1} via Strategy 2 (Right).")
                        y_cursor_right_s2 += lensbar_fxtr.height + vertical_gap_s2
                        placed_count += 1
                else: # Place LEFT
                    valid_spot = find_valid_spot_near(x_left_col_s2, y_cursor_left_s2, lensbar_fxtr)
                    if valid_spot:
                        x, y = valid_spot
                        self.place_fixture(lensbar_fxtr, (x, y, 0), 0, False)
                        placed_bboxes.append((x, y, x + lensbar_fxtr.width, y + lensbar_fxtr.height))
                        print(f"    ✅ SUCCESS: Placed Lensbar #{placed_count + 1} via Strategy 2 (Left).")
                        y_cursor_left_s2 += lensbar_fxtr.height + vertical_gap_s2
                        placed_count += 1
        else:
            print("  -> Strategy 2 skipped: Condition not met (Euro count is not odd and >= 3).")

        if placed_count >= lensbar_count:
            print(f"\n-> Finished Lensbar Placement: Placed {placed_count} of {lensbar_count} requested fixtures.")
            return

        # =================================================================
        # STRATEGY 3: CENTRAL AREA GRID SEARCH (Fallback)
        # =================================================================
        print("\n  -> Attempting Strategy 3: Grid Search in Left/Right Central Zones...")
        # (This logic is now Strategy 3)
        room_w = self.cvc.max_x - self.cvc.min_x
        room_h = self.cvc.max_y - self.cvc.min_y
        central_x_start = self.cvc.min_x + room_w * 0.20
        central_x_end = self.cvc.max_x - room_w * 0.20
        central_y_start = self.cvc.min_y + room_h * 0.30
        central_y_end = self.cvc.max_y - room_h * 0.30
        zone_center_x = central_x_start + (central_x_end - central_x_start) / 2

        def grid_search_zone(x_start, x_end, y_start, y_end):
            y = y_start
            while y < (y_end - lensbar_fxtr.height):
                x = x_start
                while x < (x_end - lensbar_fxtr.width):
                    valid_spot = find_valid_spot_near(x, y, lensbar_fxtr, search_radius=200, step=50)
                    if valid_spot: return valid_spot
                    x += 100
                y += 100
            return None

        while placed_count < lensbar_count:
            found_spot = grid_search_zone(zone_center_x, central_x_end, central_y_start, central_y_end)
            if not found_spot:
                found_spot = grid_search_zone(central_x_start, zone_center_x, central_y_start, central_y_end)
            
            if found_spot:
                x, y = found_spot
                self.place_fixture(lensbar_fxtr, (x, y, 0), 0, False)
                placed_bboxes.append((x, y, x + lensbar_fxtr.width, y + lensbar_fxtr.height))
                print(f"    ✅ SUCCESS: Placed Lensbar #{placed_count + 1} via Strategy 3 (Grid Search).")
                placed_count += 1
            else:
                print(f"    ⚠️ FAILED: No grid search spot found. Aborting Strategy 3.")
                break

        if placed_count >= lensbar_count:
            print(f"\n-> Finished Lensbar Placement: Placed {placed_count} of {lensbar_count} requested fixtures.")
            return

        # =================================================================
        # STRATEGY 4: PARALLEL-TO-WALL PLACEMENT (Final Fallback)
        # =================================================================
        print("\n  -> Attempting Strategy 4: Parallel-to-Wall Placement...")
        # (This logic is now Strategy 4)
        all_segments = self.cvc.get_wall_segments(min_length=lensbar_fxtr.width + 200)
        for segment in all_segments:
            if placed_count >= lensbar_count: break
            # ... (full logic to walk along the wall and check for space) ...
            
        print(f"\n-> Finished Lensbar Placement: Placed {placed_count} of {lensbar_count} requested fixtures.")
        if placed_count < lensbar_count:
            print(f"    ⚠️ WARNING: Only {placed_count} Lensbars placed. Some may not fit.")
        
    



    def place_eye_massage_area(self, placed_bboxes):
        """
        Places the Eye_massage_area fixture(s) below the left-most clinic,
        arranging additional units in a row from left to right.
        """
        from shapely.geometry import box
        from ezdxf.bbox import extents

        print("\n--- Attempting to place Eye Massage Area ---")

        # 1. SETUP
        try:
            # Reads the count from the 'Eye_massage_area' dictionary as requested
            config = self.fixtures.get("Eye_massage_area", {})
            fixture_count = config.get("Eye_massage_area", 0)
            if fixture_count <= 0:
                print("ℹ️ No Eye_massage_area fixture specified for placement.")
                return
            fixture_obj = Fixture.Fixture("Eye_massage_area", self.fixture_dict["Eye_massage_area"]["path"])
        except Exception as e:
            print(f"🔥 Error during Eye_massage_area setup: {e}")
            return

        # 2. FIND THE FIRST (LEFT-MOST) CLINIC
        clinic_entities = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
        if not clinic_entities:
            print("⚠️ Cannot place Eye_massage_area: No Clinic fixtures found to anchor to.")
            return
            
        # Find the clinic with the minimum X-coordinate
        first_clinic = min(clinic_entities, key=lambda e: e.dxf.insert.x)
        anchor_bbox = extents([first_clinic])
        
        # 3. CALCULATE TARGET POSITION & PLACE
        # Helper to validate spots
        def is_valid_spot(x, y, fxtr):
            candidate_box = box(x, y, x + fxtr.width, y + fxtr.height)
            return self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in placed_bboxes)

        margin_below_clinic = 150.0
        gap_between = 100.0
        
        # Anchor the first placement below the left edge of the first clinic
        start_x = anchor_bbox.extmin.x
        start_y = anchor_bbox.extmin.y - margin_below_clinic - fixture_obj.height

        current_x = start_x
        placed_count = 0

        for i in range(fixture_count):
            placed_this_iteration = False
            search_x = current_x
            
            # Search rightwards from the current cursor for a valid spot
            while not placed_this_iteration and search_x < self.cvc.max_x:
                if is_valid_spot(search_x, start_y, fixture_obj):
                    self.place_fixture(fixture_obj, (search_x, start_y, 0), 0, False)
                    placed_bboxes.append((search_x, start_y, search_x + fixture_obj.width, start_y + fixture_obj.height))
                    print(f"✅ SUCCESS: Placed Eye_massage_area #{i+1} under the clinic.")
                    
                    # Update the cursor for the next placement
                    current_x = search_x + fixture_obj.width + gap_between
                    placed_count += 1
                    placed_this_iteration = True
                else:
                    # Nudge right if the ideal spot is blocked
                    search_x += 100

            if not placed_this_iteration:
                print(f"⚠️ FAILED: Could not find a clear spot for Eye_massage_area #{i+1}.")
                break # Stop trying if space runs out

        print(f"\n-> Finished Eye Massage Area Placement: Placed {placed_count} of {fixture_count} requested fixtures.")

    
    def place_drop_box(self, placed_bboxes):
        """
        Places drop_box fixtures dynamically.
        Strategy 1: Anchors to the last placed BOH fixture and places subsequent
                    fixtures in a center-out pattern (right, then left).
        Fallback Strategies: Anchors to the overall clinic zone or performs a
                            general search in the top-right quadrant.
        """
        from shapely.geometry import box
        from ezdxf.bbox import extents

        print("\n--- Attempting to place Drop Box (Dynamic Anchoring) ---")

        # 1. SETUP
        try:
            config = self.fixtures.get("lensbar_and_dropbox", {})
            dropbox_count = config.get("drop_box", 0)
            if dropbox_count <= 0:
                print("ℹ️ No Drop_box fixture specified for placement.")
                return
            dropbox_fxtr = Fixture.Fixture("drop_box", self.fixture_dict["drop_box"]["path"])
        except Exception as e:
            print(f"🔥 Error during Drop_box setup: {e}")
            return

        # --- HELPER for intelligent searching ---
        def find_valid_spot_near(start_x, start_y, fixture_obj, search_radius=500, step=50):
            """Searches in a spiral pattern for a valid spot."""
            candidate_box = box(start_x, start_y, start_x + fixture_obj.width, start_y + fixture_obj.height)
            if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*bbox)) for bbox in placed_bboxes):
                return (start_x, start_y)
            x, y = start_x, start_y
            dx, dy = 0, -step
            for _ in range(int(search_radius / step) ** 2):
                if (-search_radius/2 < x-start_x < search_radius/2) and (-search_radius/2 < y-start_y < search_radius/2):
                    candidate_box = box(x, y, x + fixture_obj.width, y + fixture_obj.height)
                    if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*bbox)) for bbox in placed_bboxes):
                        return (x, y)
                if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
                    dx, dy = -dy, dx
                x, y = x + dx, y + dy
            return None

        placed_count = 0
        
        # --- STRATEGY 1: Anchor to the LAST placed BOH fixture ---
        print("    -> Attempting Strategy 1: Anchor to last BOH fixture...")
        
        # <<< MODIFIED LOGIC: Reliably identify BOH fixtures by type >>>
        boh_entities = []
        for entity in self.msp.query('INSERT'):
            block_name_upper = entity.dxf.name.upper()
            best_match_key = ""
            for key in self.fixture_dict.keys():
                sanitized_key = key.upper().replace(" ", "_")
                if block_name_upper.startswith(sanitized_key):
                    if len(key) > len(best_match_key):
                        best_match_key = key
            
            if best_match_key:
                fixture_type = self.fixture_dict[best_match_key].get("type")
                if fixture_type == 'boh':
                    boh_entities.append(entity)
        
        if boh_entities:
            boh_bboxes = [extents([e]) for e in boh_entities if extents([e])]
            # Find the BOH fixture with the lowest y-coordinate (the "last" one placed vertically)
            last_boh_bbox = min(boh_bboxes, key=lambda b: b.extmin.y)
            
            # --- Place the first drop_box centered below this anchor ---
            anchor_x_center = last_boh_bbox.center.x
            ideal_x = anchor_x_center - (dropbox_fxtr.width / 2)
            ideal_y = last_boh_bbox.extmin.y - 190.0 - dropbox_fxtr.height # 190mm gap

            first_spot = find_valid_spot_near(ideal_x, ideal_y, dropbox_fxtr)
            
            if first_spot:
                x, y = first_spot
                self.place_fixture(dropbox_fxtr, (x, y, 0), 0, False)
                first_bbox = (x, y, x + dropbox_fxtr.width, y + dropbox_fxtr.height)
                placed_bboxes.append(first_bbox)
                print(f"    ✅ SUCCESS: Placed first Drop_box #{placed_count + 1} anchored to BOH.")
                placed_count += 1

                # --- Place subsequent drop_boxes to the left and right ---
                left_cursor_x = first_bbox[0]
                right_cursor_x = first_bbox[2]
                gap = 100.0

                for i in range(dropbox_count - 1):
                    if i % 2 == 0: # Place to the RIGHT
                        next_x = right_cursor_x + gap
                        next_spot = find_valid_spot_near(next_x, y, dropbox_fxtr)
                        if next_spot:
                            nx, ny = next_spot
                            self.place_fixture(dropbox_fxtr, (nx, ny, 0), 0, False)
                            new_bbox = (nx, ny, nx + dropbox_fxtr.width, ny + dropbox_fxtr.height)
                            placed_bboxes.append(new_bbox)
                            right_cursor_x = new_bbox[2]
                            print(f"    ✅ SUCCESS: Placed Drop_box #{placed_count + 1} to the right.")
                            placed_count += 1
                    else: # Place to the LEFT
                        next_x = left_cursor_x - gap - dropbox_fxtr.width
                        next_spot = find_valid_spot_near(next_x, y, dropbox_fxtr)
                        if next_spot:
                            nx, ny = next_spot
                            self.place_fixture(dropbox_fxtr, (nx, ny, 0), 0, False)
                            new_bbox = (nx, ny, nx + dropbox_fxtr.width, ny + dropbox_fxtr.height)
                            placed_bboxes.append(new_bbox)
                            left_cursor_x = new_bbox[0]
                            print(f"    ✅ SUCCESS: Placed Drop_box #{placed_count + 1} to the left.")
                            placed_count += 1
        else:
            print("    -> Strategy 1 failed: No BOH fixtures found to anchor to.")

        # --- FALLBACK STRATEGIES (if not all were placed) ---
        if placed_count < dropbox_count:
            print(f"  -> Only placed {placed_count}/{dropbox_count}. Attempting fallback strategies for the rest...")
            # (The logic for Strategy 2 and 3 would go here to place the REMAINING fixtures)

        print(f"\n-> Finished Drop Box Placement: Placed {placed_count} of {dropbox_count} requested fixtures.")

    def place_pickup_counter(self, placed_bboxes):
        """
        Places pickup_counter fixtures by anchoring to the last placed BOH fixture
        in the top-right corner.
        """
        from shapely.geometry import box
        from ezdxf.bbox import extents

        print("\n--- Attempting to place Pickup Counter ---")

        # 1. SETUP
        try:
            config = self.fixtures.get("table_fixtures", {})
            counter_count = config.get("pick_up_counter", 0)
            if counter_count <= 0:
                print("ℹ️ No Pickup Counter fixture specified for placement.")
                return
            counter_fxtr = Fixture.Fixture("pick_up_counter", self.fixture_dict["pick_up_counter"]["path"])
        except Exception as e:
            print(f"🔥 Error during Pickup Counter setup: {e}")
            return

        # 2. FIND BOH ZONE (Corrected Logic)
        boh_entities = []
        for entity in self.msp.query('INSERT'):
            block_name_upper = entity.dxf.name.upper()
            best_match_key = ""
            for key in self.fixture_dict.keys():
                sanitized_key = key.upper().replace(" ", "_")
                if block_name_upper.startswith(sanitized_key):
                    if len(key) > len(best_match_key):
                        best_match_key = key
            
            if best_match_key:
                fixture_type = self.fixture_dict[best_match_key].get("type")
                if fixture_type == 'boh':
                    boh_entities.append(entity)

        if not boh_entities:
            print("⚠️ Cannot place Pickup Counter: No BOH fixtures found to anchor to. Aborting.")
            return
            
        # --- Find the "last" (bottom-most) BOH fixture in the top-right corner ---
        top_right_boh_fixtures = [e for e in boh_entities if e.dxf.insert.x > self.cvc.max_x * 0.5 and e.dxf.insert.y > self.cvc.max_y * 0.5]
        if not top_right_boh_fixtures:
            print("⚠️ No BOH fixtures found in the top-right corner to anchor to. Using all BOH fixtures.")
            top_right_boh_fixtures = boh_entities

        last_boh_entity = min(top_right_boh_fixtures, key=lambda e: e.dxf.insert.y)
        last_boh_bbox = extents([last_boh_entity])
        
        # 3. CALCULATE TARGET POSITION & PLACE
        margin_below_boh = 150.0
        gap_between = 100.0
        
        current_x = last_boh_bbox.extmax.x
        target_y = last_boh_bbox.extmin.y - margin_below_boh - counter_fxtr.height

        placed_count = 0
        for i in range(counter_count):
            placed_this_iteration = False
            search_x = current_x - counter_fxtr.width
            
            while not placed_this_iteration and search_x > self.cvc.min_x:
                candidate_box = box(search_x, target_y, search_x + counter_fxtr.width, target_y + counter_fxtr.height)
                is_overlapping = any(candidate_box.intersects(box(*bbox)) for bbox in placed_bboxes)
                is_inside = self.floorplan_polygon.contains(candidate_box)

                if is_inside and not is_overlapping:
                    insert_point = (search_x, target_y, 0)
                    self.place_fixture(counter_fxtr, insert_point, 0, False)
                    placed_bboxes.append((search_x, target_y, search_x + counter_fxtr.width, target_y + counter_fxtr.height))
                    print(f"✅ SUCCESS: Placed Pickup Counter #{i+1} under BOH.")
                    current_x = search_x - gap_between
                    placed_count += 1
                    placed_this_iteration = True
                else:
                    search_x -= 100

            if not placed_this_iteration:
                print(f"⚠️ FAILED: Could not find a clear spot for Pickup Counter #{i+1}.")
                break

        print(f"\n-> Finished Pickup Counter Placement: Placed {placed_count} of {counter_count} requested fixtures.")




#--------------placement-1---setup

    # def place_corian_table_set(self, placed_bboxes):
    #     """
    #     Places one or more Corian Table sets using a multi-strategy approach.
    #     Each set consists of 1 Corian_table and 4 Lounge_seats.

    #     Strategy 1 (Primary): If the gap between the bottom wall and the first Euro_centre
    #                         is large enough, places the set within that gap.
    #     Strategy 2 (Fallback): Anchors placement above any existing Sofas, POS, or AR units.
    #     Strategy 3 (Fallback): Anchors placement above the Euro_centre stack.
    #     Strategy 4 (Final Fallback): Performs a general search in the central area of the room.
    #     """
    #     # Import necessary libraries for this function's scope
    #     from shapely.geometry import box
    #     from ezdxf.bbox import extents

    #     print("\n--- Attempting to place Corian Table Set ---")

    #     # 1. SETUP: Load fixture counts and objects
    #     try:
    #         # Read the configuration for this specific set
    #         config = self.fixtures.get("Corian_table_set", {})
    #         table_count = config.get("Corian_table", 0)
            
    #         # If no tables are requested, exit the function early.
    #         if table_count <= 0:
    #             print("  -> Placement skipped: No Corian_table specified in the configuration.")
    #             return
            
    #         # Automatically assume 4 seats are required for each table.
    #         # This makes the Lounge_seat count in main.py optional.
    #         seat_count = table_count * 4 
    #         print(f"  -> Config found: {table_count} table(s). Automatically assigning {seat_count} seat(s).")
            
    #         num_sets = table_count
    #         # Load the fixture objects from their DXF files.
    #         table_fxtr = Fixture.Fixture("Corian_table", self.fixture_dict["Corian_table"]["path"])
    #         seat_fxtr = Fixture.Fixture("Lounge_seat", self.fixture_dict["Lounge_seat"]["path"])

    #     except Exception as e:
    #         # Catch any errors during file loading or setup.
    #         print(f"🔥 Error during Corian_table_set setup: {e}")
    #         return

    #     # 2. DEFINE THE SET'S GEOMETRY
    #     # Define the spacing between the components of the set.
    #     gap_table_to_seat = 100.0
    #     gap_between_seats = 50.0
    #     # Calculate the total width and height of the entire 5-piece set.
    #     set_width = max(table_fxtr.width, (seat_fxtr.width * 2) + gap_between_seats)
    #     set_height = (seat_fxtr.height * 2) + table_fxtr.height + (gap_table_to_seat * 2)
    #     print(f"  -> Calculated set size: {set_width:.0f}w x {set_height:.0f}h")

    #     # 3. HELPER FUNCTIONS
    #     def _place_single_set(set_x, set_y):
    #         """
    #         This helper function takes a top-left coordinate (set_x, set_y) for the entire
    #         set's bounding box and places all 5 individual components relative to it.
    #         """
    #         print(f"    ✅ Found valid spot. Placing components for set at ({set_x:.0f}, {set_y:.0f})...")
            
    #         # --- Place Table (centered in the set) ---
    #         table_x = set_x + (set_width - table_fxtr.width) / 2
    #         table_y = set_y + seat_fxtr.height + gap_table_to_seat
    #         self.place_fixture(table_fxtr, (table_x, table_y, 0), 0, False)
    #         placed_bboxes.append((table_x, table_y, table_x + table_fxtr.width, table_y + table_fxtr.height))

    #         # --- Place Top Seats (rotated 180 degrees to face the table) ---
    #         top_seats_x_start = set_x + (set_width - (seat_fxtr.width * 2 + gap_between_seats)) / 2
    #         top_seats_y = table_y + table_fxtr.height + gap_table_to_seat
    #         # For rotated fixtures, the insertion point must be adjusted to account for the rotation.
    #         # The insertion point is the block's origin, which we want to position correctly.
    #         # A 180-degree rotation means the insertion point is at the top-right of the final bounding box.
    #         self.place_fixture(seat_fxtr, (top_seats_x_start + seat_fxtr.width, top_seats_y + seat_fxtr.height, 0), 180, False)
    #         placed_bboxes.append((top_seats_x_start, top_seats_y, top_seats_x_start + seat_fxtr.width, top_seats_y + seat_fxtr.height))
            
    #         seat2_x = top_seats_x_start + seat_fxtr.width + gap_between_seats
    #         self.place_fixture(seat_fxtr, (seat2_x + seat_fxtr.width, top_seats_y + seat_fxtr.height, 0), 180, False)
    #         placed_bboxes.append((seat2_x, top_seats_y, seat2_x + seat_fxtr.width, top_seats_y + seat_fxtr.height))
            
    #         # --- Place Bottom Seats (0-degree rotation, facing the table) ---
    #         bottom_seats_x_start = top_seats_x_start
    #         bottom_seats_y = set_y
    #         self.place_fixture(seat_fxtr, (bottom_seats_x_start, bottom_seats_y, 0), 0, False)
    #         placed_bboxes.append((bottom_seats_x_start, bottom_seats_y, bottom_seats_x_start + seat_fxtr.width, bottom_seats_y + seat_fxtr.height))
            
    #         seat4_x = bottom_seats_x_start + seat_fxtr.width + gap_between_seats
    #         self.place_fixture(seat_fxtr, (seat4_x, bottom_seats_y, 0), 0, False)
    #         placed_bboxes.append((seat4_x, bottom_seats_y, seat4_x + seat_fxtr.width, bottom_seats_y + seat_fxtr.height))

    #     def find_valid_spot(start_x, start_y):
    #         """
    #         Intelligently searches for a clear spot for the entire set, starting from an
    #         ideal point and searching outwards to the left and right.
    #         """
    #         search_offset = 0
    #         max_search = (self.cvc.max_x - self.cvc.min_x) / 3 # Limit search to a reasonable area
    #         while search_offset < max_search:
    #             # Check to the right of the ideal start point
    #             candidate_box_r = box(start_x + search_offset, start_y, start_x + search_offset + set_width, start_y + set_height)
    #             if self.floorplan_polygon.contains(candidate_box_r) and not any(candidate_box_r.intersects(box(*b)) for b in placed_bboxes):
    #                 return (start_x + search_offset, start_y)
    #             # Check to the left of the ideal start point
    #             if search_offset > 0:
    #                 candidate_box_l = box(start_x - search_offset, start_y, start_x - search_offset + set_width, start_y + set_height)
    #                 if self.floorplan_polygon.contains(candidate_box_l) and not any(candidate_box_l.intersects(box(*b)) for b in placed_bboxes):
    #                     return (start_x - search_offset, start_y)
    #             search_offset += 100 # Nudge the search by 100mm
    #         return None # Return None if no spot is found

    #     # 4. MAIN PLACEMENT LOOP
    #     placed_sets = 0
    #     for i in range(num_sets):
    #         print(f"  -> Searching for spot for Set #{i+1}...")
    #         found_spot = None

    #         # --- Strategy 1: Place in the gap below Euro Centres if it's large enough ---
    #         print("    -> Attempting Strategy 1: Place in large gap below Euro Centres...")
    #         euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
    #         if euro_entities:
    #             euro_bboxes = sorted([extents([e]) for e in euro_entities if extents([e])], key=lambda b: b.extmin.y)
    #             if euro_bboxes:
    #                 first_euro_bbox = euro_bboxes[0]
    #                 gap = first_euro_bbox.extmin.y - self.cvc.min_y
    #                 required_space = set_height + 600 # Set height + 300mm margin top and bottom
                    
    #                 if gap >= required_space:
    #                     print(f"    -> Condition met: Gap of {gap:.0f}mm is large enough.")
    #                     ideal_y = self.cvc.min_y + (gap / 2) - (set_height / 2)
    #                     ideal_x = first_euro_bbox.center.x - (set_width / 2)
    #                     found_spot = find_valid_spot(ideal_x, ideal_y)
    #                     if found_spot: print("    -> Found spot using Strategy 1 (Under Euro Centre).")
    #                 else:
    #                     print(f"    -> Condition not met: Gap of {gap:.0f}mm is too small for this strategy.")
    #         else:
    #             print("  -> Strategy 1 skipped: No Euro_centre fixtures found.")

    #         # --- Strategy 2: Anchor ABOVE Sofas/POS/AR (Fallback) ---
    #         if not found_spot:
    #             print("    -> Attempting Strategy 2: Anchor to Sofa/POS...")
    #             anchor_fixtures = [extents([e]) for e in self.msp.query('INSERT') if "SOFA" in e.dxf.name.upper() or "POS" in e.dxf.name.upper() or "AR" in e.dxf.name.upper()]
    #             if anchor_fixtures:
    #                 anchor_y = max(bbox.extmax.y for bbox in anchor_fixtures)
    #                 ideal_x = self.cvc.min_x + (self.cvc.max_x - self.cvc.min_x - set_width) / 2
    #                 found_spot = find_valid_spot(ideal_x, anchor_y + 300.0)
    #                 if found_spot: print("    -> Found spot using Strategy 2.")

    #         # --- Strategy 3: Anchor ABOVE Euro Centres (Fallback) ---
    #         if not found_spot:
    #             print("    -> Attempting Strategy 3: Anchor to Euro Centre...")
    #             if euro_entities: # Reuse from Strategy 1
    #                 anchor_y = extents(euro_entities).extmax.y
    #                 ideal_x = self.cvc.min_x + (self.cvc.max_x - self.cvc.min_x - set_width) / 2
    #                 found_spot = find_valid_spot(ideal_x, anchor_y + 300.0)
    #                 if found_spot: print("    -> Found spot using Strategy 3.")

    #         # --- Strategy 4: General Central Area Search (Final Fallback) ---
    #         if not found_spot:
    #             print("    -> Attempting Strategy 4: General Central Search...")
    #             start_y = self.cvc.min_y + (self.cvc.max_y - self.cvc.min_y) * 0.4
    #             ideal_x = self.cvc.min_x + (self.cvc.max_x - self.cvc.min_x - set_width) / 2
    #             found_spot = find_valid_spot(ideal_x, start_y)
    #             if found_spot: print("    -> Found spot using Strategy 4.")

    #         # --- Execute Placement ---
    #         if found_spot:
    #             _place_single_set(found_spot[0], found_spot[1])
    #             placed_sets += 1
    #         else:
    #             print(f"⚠️ FAILED: Could not find a clear spot for Corian Table Set #{i+1} after all strategies.")
    #             break

    #     print(f"\n-> Finished Corian Table Set Placement: Placed {placed_sets} of {num_sets} requested sets.")

#---------------placement 2 setup -------------------------------------------------


    # def place_corian_table_set(self, placed_bboxes):
    #     """
    #     Places one or more Corian Table sets using a multi-strategy approach.
    #     If multiple sets are requested, they are placed as a single, centered group.
    #     """
    #     from shapely.geometry import box
    #     from ezdxf.bbox import extents

    #     print("\n--- Attempting to place Corian Table Set ---")

    #     # 1. SETUP: Load fixture counts and objects
    #     try:
    #         config = self.fixtures.get("Corian_table_set", {})
    #         num_sets = config.get("Corian_table", 0)
            
    #         if num_sets <= 0:
    #             print("  -> Placement skipped: No Corian_table specified.")
    #             return
            
    #         table_fxtr = Fixture.Fixture("Corian_table", self.fixture_dict["Corian_table"]["path"])
    #         seat_fxtr = Fixture.Fixture("Lounge_seat", self.fixture_dict["Lounge_seat"]["path"])
    #     except Exception as e:
    #         print(f"🔥 Error during Corian_table_set setup: {e}")
    #         return

    #     # 2. DEFINE THE SET'S GEOMETRY
    #     gap_table_to_seat = 100.0
    #     gap_between_seats = 50.0
    #     set_width = max(table_fxtr.width, (seat_fxtr.width * 2) + gap_between_seats)
    #     set_height = (seat_fxtr.height * 2) + table_fxtr.height + (gap_table_to_seat * 2)
    #     print(f"  -> Calculated set size: {set_width:.0f}w x {set_height:.0f}h")

    #     # 3. HELPER FUNCTIONS
    #     def _place_single_set(set_x, set_y):
    #         """
    #         This helper function takes a top-left coordinate (set_x, set_y) for the entire
    #         set's bounding box and places all 5 individual components relative to it.
    #         """
    #         print(f"    ✅ Found valid spot. Placing components for set at ({set_x:.0f}, {set_y:.0f})...")
            
    #         # --- Place Table (centered in the set) ---
    #         table_x = set_x + (set_width - table_fxtr.width) / 2
    #         table_y = set_y + seat_fxtr.height + gap_table_to_seat
    #         self.place_fixture(table_fxtr, (table_x, table_y, 0), 0, False)
    #         placed_bboxes.append((table_x, table_y, table_x + table_fxtr.width, table_y + table_fxtr.height))

    #         # --- Place Top Seats (rotated 180 degrees to face the table) ---
    #         top_seats_x_start = set_x + (set_width - (seat_fxtr.width * 2 + gap_between_seats)) / 2
    #         top_seats_y = table_y + table_fxtr.height + gap_table_to_seat
    #         # For rotated fixtures, the insertion point must be adjusted to account for the rotation.
    #         # The insertion point is the block's origin, which we want to position correctly.
    #         # A 180-degree rotation means the insertion point is at the top-right of the final bounding box.
    #         self.place_fixture(seat_fxtr, (top_seats_x_start + seat_fxtr.width, top_seats_y + seat_fxtr.height, 0), 180, False)
    #         placed_bboxes.append((top_seats_x_start, top_seats_y, top_seats_x_start + seat_fxtr.width, top_seats_y + seat_fxtr.height))
            
    #         seat2_x = top_seats_x_start + seat_fxtr.width + gap_between_seats
    #         self.place_fixture(seat_fxtr, (seat2_x + seat_fxtr.width, top_seats_y + seat_fxtr.height, 0), 180, False)
    #         placed_bboxes.append((seat2_x, top_seats_y, seat2_x + seat_fxtr.width, top_seats_y + seat_fxtr.height))
            
    #         # --- Place Bottom Seats (0-degree rotation, facing the table) ---
    #         bottom_seats_x_start = top_seats_x_start
    #         bottom_seats_y = set_y
    #         self.place_fixture(seat_fxtr, (bottom_seats_x_start, bottom_seats_y, 0), 0, False)
    #         placed_bboxes.append((bottom_seats_x_start, bottom_seats_y, bottom_seats_x_start + seat_fxtr.width, bottom_seats_y + seat_fxtr.height))
            
    #         seat4_x = bottom_seats_x_start + seat_fxtr.width + gap_between_seats
    #         self.place_fixture(seat_fxtr, (seat4_x, bottom_seats_y, 0), 0, False)
    #         placed_bboxes.append((seat4_x, bottom_seats_y, seat4_x + seat_fxtr.width, bottom_seats_y + seat_fxtr.height))


    #     # # 4. NEW LOGIC: First, find a valid Y-level for the entire row of sets
    #     # ideal_y = None
    #     # strategy_found = False
    #     # euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]

    #     # # --- Strategy 1 (Primary): Anchor ABOVE Euro Centres ---
    #     # print("    -> Attempting Strategy 1: Anchor above Euro Centres...")
    #     # if euro_entities:
    #     #     ideal_y = extents(euro_entities).extmax.y + 300.0 # 300mm gap
    #     #     strategy_found = True
    #     #     print("    -> Found Y-level using Strategy 1.")
        
    #     # # --- Strategy 2 (Fallback): Place in the gap below Euro Centres ---
    #     # if not strategy_found and euro_entities:
    #     #     print("    -> Attempting Strategy 2: Place in large gap below Euro Centres...")
    #     #     euro_bboxes = sorted([extents([e]) for e in euro_entities if extents([e])], key=lambda b: b.extmin.y)
    #     #     if euro_bboxes:
    #     #         first_euro_bbox = euro_bboxes[0]
    #     #         gap = first_euro_bbox.extmin.y - self.cvc.min_y
    #     #         required_space = set_height + 600
    #     #         if gap >= required_space:
    #     #             ideal_y = self.cvc.min_y + (gap - set_height) / 2
    #     #             strategy_found = True
    #     #             print("    -> Found Y-level using Strategy 2.")

    #     # # --- Strategy 3 (Final Fallback): General Central Area Search ---
    #     # if not strategy_found:
    #     #     print("    -> Attempting Strategy 3: General Central Search...")
    #     #     ideal_y = self.cvc.min_y + (self.cvc.max_y - self.cvc.min_y) * 0.4
    #     #     strategy_found = True
    #     #     print("    -> Using fallback Y-level from Strategy 3.")

    #     # # 5. Place the sets as a centered group at the determined Y-level
    #     # if strategy_found:
    #     #     horizontal_gap = 50.0
    #     #     total_group_width = (num_sets * set_width) + ((num_sets - 1) * horizontal_gap)
    #     #     room_width = self.cvc.max_x - self.cvc.min_x

    #     #     if total_group_width > room_width * 0.9: # Ensure it doesn't take more than 90% of room width
    #     #         print(f"⚠️ WARNING: The {num_sets} Corian sets are too wide to fit in a single centered row. Aborting.")
    #     #         return

    #     #     group_start_x = self.cvc.min_x + (room_width - total_group_width) / 2
    #     #     placed_sets = 0
    #     #     for i in range(num_sets):
    #     #         current_set_x = group_start_x + i * (set_width + horizontal_gap)
    #     #         candidate_box = box(current_set_x, ideal_y, current_set_x + set_width, ideal_y + set_height)
    #     #         if not self.floorplan_polygon.contains(candidate_box.buffer(-1)) or any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
    #     #             print(f"⚠️ Could not place Corian Table Set #{i+1} at calculated spot as it was blocked.")
    #     #             continue
                
    #     #         _place_single_set(current_set_x, ideal_y)
    #     #         placed_sets += 1
            
    #     #     print(f"\n-> Finished Corian Table Set Placement: Placed {placed_sets} of {num_sets} requested sets.")
    #     # else:
    #     #     print(f"⚠️ FAILED: Could not find a valid Y-level for Corian Table Sets after all strategies.")

    # In DXF_Controller.py, replace the old function with this new version.

    # In DXF_Controller.py

    def place_corcorian_table_set(self, placed_bboxes):
        """
        Places Corian Table sets using a multi-strategy approach with a resilient
        horizontal search to find a clear, centered position.
        """
        from shapely.geometry import box, LineString
        from ezdxf.bbox import extents

        print("\n--- Attempting to place Corian Table Set with Resilient Centering ---")

        placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
        # 1. SETUP: Load fixture counts and objects
        try:
            config = self.fixtures.get("Corian_table_set", {})
            num_sets = config.get("Corian_table", 0)
            
            if num_sets <= 0:
                print("  -> Placement skipped: No Corian_table specified.")
                return
            
            table_fxtr = Fixture.Fixture("Corian_table", self.fixture_dict["Corian_table"]["path"])
            seat_fxtr = Fixture.Fixture("Lounge_seat", self.fixture_dict["Lounge_seat"]["path"])
        except Exception as e:
            print(f"🔥 Error during Corian_table_set setup: {e}")
            return

        # 2. DEFINE THE SET'S GEOMETRY
        gap_table_to_seat = 100.0
        gap_between_seats = 50.0
        set_width = max(table_fxtr.width, (seat_fxtr.width * 2) + gap_between_seats)
        set_height = (seat_fxtr.height * 2) + table_fxtr.height + (gap_table_to_seat * 2)
        print(f"  -> Calculated set size: {set_width:.0f}w x {set_height:.0f}h")

        # 3. HELPER FUNCTION TO PLACE COMPONENTS
        def _place_single_set(set_x, set_y):
            print(f"    ✅ Found valid spot. Placing components for set at ({set_x:.0f}, {set_y:.0f})...")
            table_x = set_x + (set_width - table_fxtr.width) / 2
            table_y = set_y + seat_fxtr.height + gap_table_to_seat
            self.place_fixture(table_fxtr, (table_x, table_y, 0), 0, False)
            placed_bboxes.append((table_x, table_y, table_x + table_fxtr.width, table_y + table_fxtr.height))
            top_seats_x_start = set_x + (set_width - (seat_fxtr.width * 2 + gap_between_seats)) / 2
            top_seats_y = table_y + table_fxtr.height + gap_table_to_seat
            self.place_fixture(seat_fxtr, (top_seats_x_start + seat_fxtr.width, top_seats_y + seat_fxtr.height, 0), 180, False)
            placed_bboxes.append((top_seats_x_start, top_seats_y, top_seats_x_start + seat_fxtr.width, top_seats_y + seat_fxtr.height))
            seat2_x = top_seats_x_start + seat_fxtr.width + gap_between_seats
            self.place_fixture(seat_fxtr, (seat2_x + seat_fxtr.width, top_seats_y + seat_fxtr.height, 0), 180, False)
            placed_bboxes.append((seat2_x, top_seats_y, seat2_x + seat_fxtr.width, top_seats_y + seat_fxtr.height))
            bottom_seats_x_start = top_seats_x_start
            bottom_seats_y = set_y
            self.place_fixture(seat_fxtr, (bottom_seats_x_start, bottom_seats_y, 0), 0, False)
            placed_bboxes.append((bottom_seats_x_start, bottom_seats_y, bottom_seats_x_start + seat_fxtr.width, bottom_seats_y + seat_fxtr.height))
            seat4_x = bottom_seats_x_start + seat_fxtr.width + gap_between_seats
            self.place_fixture(seat_fxtr, (seat4_x, bottom_seats_y, 0), 0, False)
            placed_bboxes.append((seat4_x, bottom_seats_y, seat4_x + seat_fxtr.width, seat_fxtr.height))

        # 4. FIND A VALID Y-LEVEL
        ideal_y = None
        strategy_found = False
        
        # *** FIX APPLIED ON THIS LINE ***
        euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
        # *** END OF FIX ***

        if euro_entities:
            ideal_y = extents(euro_entities).extmax.y + 300.0
            strategy_found = True
        if not strategy_found and euro_entities:
            euro_bboxes = sorted([extents([e]) for e in euro_entities if extents([e])], key=lambda b: b.extmin.y)
            if euro_bboxes:
                first_euro_bbox = euro_bboxes[0]
                gap = first_euro_bbox.extmin.y - self.cvc.min_y
                if gap >= set_height + 600:
                    ideal_y = self.cvc.min_y + (gap - set_height) / 2
                    strategy_found = True
        if not strategy_found:
            ideal_y = self.cvc.min_y + (self.cvc.max_y - self.cvc.min_y) * 0.4
            strategy_found = True

        # 5. RESILIENT PLACEMENT FOR THE GROUP
        if strategy_found:
            horizontal_gap = 50.0
            total_group_width = (num_sets * set_width) + ((num_sets - 1) * horizontal_gap)
            
            horizontal_slice = LineString([(self.cvc.min_x, ideal_y), (self.cvc.max_x, ideal_y)])
            intersection = self.floorplan_polygon.intersection(horizontal_slice)
            
            if not (isinstance(intersection, LineString) and intersection.length >= total_group_width):
                print(f"⚠️ FAILED: Not enough horizontal width ({intersection.length:.0f}mm) at the chosen Y-level for the Corian sets ({total_group_width:.0f}mm).")
                return
                
            local_x_min, _, local_x_max, _ = intersection.bounds
            
            ideal_x = local_x_min + (intersection.length - total_group_width) / 2
            
            found_spot_x = None
            search_offset = 0
            while search_offset < intersection.length / 2:
                for sign in [1, -1]:
                    if sign == -1 and search_offset == 0: continue
                    
                    test_x = ideal_x + (search_offset * sign)
                    group_box = box(test_x, ideal_y, test_x + total_group_width, ideal_y + set_height)
                    
                    if not any(group_box.intersects(box(*b)) for b in placed_bboxes):
                        found_spot_x = test_x
                        break
                if found_spot_x is not None:
                    break
                search_offset += 100

            if found_spot_x is not None:
                print(f"  -> Found clear row for Corian sets at y={ideal_y:.0f}")
                placed_sets = 0
                for i in range(num_sets):
                    current_set_x = found_spot_x + i * (set_width + horizontal_gap)
                    _place_single_set(current_set_x, ideal_y)
                    placed_sets += 1
                print(f"\n-> Finished Corian Table Set Placement: Placed {placed_sets} of {num_sets} requested sets.")
            else:
                print(f"⚠️ FAILED: Could not find a clear horizontal spot for the Corian sets at y={ideal_y:.0f}.")
        else:
            print(f"⚠️ FAILED: Could not determine a valid Y-level for Corian Table Sets after all strategies.")

    #---Landscape placement setup----below  

    #---Landscape placement setup

    #---Landscape placement setup

    def place_euro_center_landscape(self, fixture_name, count, placed_bboxes, num_rows=1):
        """
        Places central floor fixtures in one or more horizontal rows for landscape mode.
        - Centers each row using the floorplan's true geometric center (centroid).
        - Places fixtures with a 0-degree rotation to face the main entrance.
        """
        from Fixture import Fixture
        from shapely.geometry import box
        import math

        print(f"--- Placing {count} of '{fixture_name}' in {num_rows} row(s) using LANDSCAPE strategy ---")
        
        try:
            fxtr = Fixture(self.fixture_dict[fixture_name]["name"], self.fixture_dict[fixture_name]["path"])
            
            # --- Get room dimensions ---
            room_min_y, room_max_y = min(self.cvc.y_coords), max(self.cvc.y_coords)
            room_height = room_max_y - room_min_y

            # --- Parameters for multiple rows ---
            gap_horizontal = 1000  # Horizontal gap between fixtures
            gap_vertical = 1    # Vertical gap between rows
            
            if num_rows <= 0: num_rows = 1
            fixtures_per_row = math.ceil(count / float(num_rows))
            
            # --- Calculate total block height to center it vertically ---
            # With 0-degree rotation, we use the fixture's actual height
            total_block_height = (fxtr.height * num_rows) + (gap_vertical * (num_rows - 1))
            block_start_y = (room_min_y + room_height / 2) - (total_block_height / 2)

            fixtures_placed_total = 0
            for row in range(num_rows):
                num_in_this_row = min(fixtures_per_row, count - fixtures_placed_total)
                if num_in_this_row <= 0:
                    break

                # --- UPDATED: Calculate row width using fixture's true width ---
                current_row_width = (fxtr.width * num_in_this_row) + (gap_horizontal * (num_in_this_row - 1))
                
                # --- UPDATED: Center the row using the floorplan's centroid ---
                true_center_x = self.floorplan_polygon.centroid.x
                current_x = true_center_x - (current_row_width / 2)
                
                insert_y = block_start_y + (row * (fxtr.height + gap_vertical))
                
                for i in range(num_in_this_row):
                    x1, y1 = current_x, insert_y
                    x2, y2 = x1 + fxtr.width, y1 + fxtr.height
                    
                    candidate_box = box(x1, y1, x2, y2)
                    is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
                    is_inside = self.floorplan_polygon.contains(candidate_box)

                    if is_inside and not is_overlapping:
                        # --- UPDATED: Set rotation to 0 for correct orientation ---
                        self.place_fixture(fxtr, (x1, y1, 0), 0, False)
                        placed_bboxes.append((x1, y1, x2, y2))
                        print(f"✅ Placed '{fixture_name}' #{fixtures_placed_total + 1} at (Row {row + 1})")
                        fixtures_placed_total += 1
                    else:
                        print(f"⚠️ Spot for '{fixture_name}' #{fixtures_placed_total + 1} was blocked or outside boundary.")
                    
                    # --- UPDATED: Move cursor by fixture's true width ---
                    current_x += fxtr.width + gap_horizontal
                
        except Exception as e:
            print(f"⚠️ Error in place_euro_center_landscape: {str(e)}")
            raise

#----setup for euro center only like without lensbar
    # def place_fixtures_iteratively_with_dynamic_stacks(self, placed_bboxes: List[tuple]) -> None:
    #     """
    #     Places fixtures iteratively. For each column, it dynamically decides
    #     whether to place a stack of 2 or 1 based on the local height, NOW
    #     including a buffer for walking space and potential attached fixtures.
    #     """
    #     from Fixture import Fixture
    #     from shapely.geometry import box, LineString
    #     import math
    #     import collections

    #     print("\n--- 🧠 Placing Fixtures with UPGRADED Iterative 'Smart Stacking' Strategy ---")

    #     # --- 1. Define Architectural Rules ---
    #     HORIZONTAL_STACK_GAP = 1200.0
    #     # LEFT_AISLE_PERCENTAGE = 0.30
    #     # --- NEW: The Left Aisle is now calculated dynamically ---
    #     LEFT_AISLE_PERCENTAGE = self._calculate_dynamic_left_aisle_percentage()
        
    #     # --- NEW: Define a vertical buffer for walking space ---
    #     # This is the extra space required above/below a fixture to be considered "comfortable".
    #     # 0.20 means 20% of the vertical space will be reserved for walking.
    #     VERTICAL_BUFFER_PERCENTAGE = 0.30

    #     # --- 2. Load fixtures ---
    #     config = self.fixtures.get("floor_fixtures", {})
    #     euro_count = config.get("Euro_centre", 0)
    #     if euro_count == 0: return

    #     try:
    #         fxtr_obj = Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"])
    #         fixture_queue = collections.deque([fxtr_obj] * euro_count)
    #     except Exception as e:
    #         print(f"🔥 FATAL: Could not load fixture: {e}")
    #         return

    #     # --- 3. Iterative Placement Loop ---
    #     room_width = self.cvc.max_x - self.cvc.min_x
    #     left_aisle_dynamic = room_width * LEFT_AISLE_PERCENTAGE
    #     current_x = self.cvc.min_x + left_aisle_dynamic
    #     placeable_width = self.cvc.max_x - 50.0
    #     stack_width = fxtr_obj.height

    #     while fixture_queue:
    #         if current_x + stack_width > placeable_width:
    #             print("    -> ⚠️ Ran out of horizontal space. Stopping placement.")
    #             break

    #         print(f"\n    -> Analyzing position for new stack at x={current_x:.0f}")
            
    #         # Measure local height (this part is the same)
    #         stack_center_x = current_x + (stack_width / 2)
    #         vertical_slice = LineString([(stack_center_x, self.cvc.min_y - 100), (stack_center_x, self.cvc.max_y + 100)])
    #         intersection = self.floorplan_polygon.intersection(vertical_slice)

    #         if not isinstance(intersection, LineString) or intersection.is_empty:
    #             print(f"      -> SKIPPING: Position x={current_x:.0f} is invalid.")
    #             current_x += 100
    #             continue

    #         # local_min_y, local_max_y = intersection.bounds[1], intersection.bounds[3]
    #         # local_height = local_max_y - local_min_y
    #         local_min_y, local_max_y = intersection.bounds[1], intersection.bounds[3]
    #         local_height = local_max_y - local_min_y

    #         # --- UPGRADED: DYNAMIC STACK HEIGHT DECISION ---
    #         # This block now calculates required height including the walking buffer.
    #         num_to_place = 0
    #         stack_height = 0
            
    #         # NEW: Calculate the buffer dynamically based on the local height.
    #         dynamic_vertical_buffer = local_height * VERTICAL_BUFFER_PERCENTAGE
            
    #         # Calculate the total vertical space needed for a comfortable stack of 2
    #         # required_height_for_two = (fxtr_obj.width * 2) + VERTICAL_WALKING_SPACE_BUFFER
            
    #         # Calculate the total vertical space needed for a comfortable stack of 1
    #         # required_height_for_one = fxtr_obj.width + VERTICAL_WALKING_SPACE_BUFFER
            
    #         # The check now uses the fixture height PLUS the dynamic buffer.
    #         required_height_for_two = (fxtr_obj.width * 2) + dynamic_vertical_buffer
    #         required_height_for_one = fxtr_obj.width + dynamic_vertical_buffer

    #         # Check if a comfortable stack of 2 can fit
    #         if len(fixture_queue) >= 2 and required_height_for_two <= local_height:
    #             num_to_place = 2
    #             stack_height = fxtr_obj.width * 2
    #             print(f"      -> Local height ({local_height:.0f}mm) is sufficient for a comfortable stack of 2.")
    #         # If not, check if a comfortable stack of 1 can fit
    #         elif len(fixture_queue) >= 1 and required_height_for_one <= local_height:
    #             num_to_place = 1
    #             stack_height = fxtr_obj.width
    #             print(f"      -> Local height ({local_height:.0f}mm) is only sufficient for a comfortable stack of 1.")
    #         else:
    #             print(f"      -> SKIPPING: Local height ({local_height:.0f}mm) is too short for a comfortable placement.")
    #             current_x += 100
    #             continue
            
    #         # --- PLACEMENT (This part is the same) ---
    #         stack_to_place = [fixture_queue.popleft() for _ in range(num_to_place)]
    #         start_y = local_min_y + (local_height - stack_height) / 2
            
    #         current_y = start_y
    #         for fxtr in stack_to_place:
    #             rotated_width, rotated_height = fxtr.height, fxtr.width
    #             x1, y1 = current_x, current_y
    #             final_insert_point = (x1 + rotated_width, y1, 0)
    #             self.place_fixture(fxtr, final_insert_point, 90, True)
    #             placed_bboxes.append((x1, y1, x1 + rotated_width, y1 + rotated_height))
    #             current_y += rotated_height

    #         current_x += stack_width + HORIZONTAL_STACK_GAP
        
    #     if fixture_queue:
    #         print(f"\n--- ⚠️ Finished with {len(fixture_queue)} unplaced fixtures ---")
    #     else:
    #         print("\n--- ✅ Finished Iterative Smart Stacking Placement ---")



    def place_fixtures_iteratively_with_dynamic_stacks(self, placed_bboxes: List[tuple]) -> None:
        """
        Places both Lensbar and Euro_centre fixtures iteratively. This definitive version
        uses a robust helper function to guarantee correct centering of all rotated stacks.
        """
        from Fixture import Fixture
        from shapely.geometry import box, LineString
        import math
        import collections

        print("\n--- 🧠 Placing Fixtures with Definitive 'Smart Stacking' Strategy ---")

        # --- 1. Architectural Rules (Unchanged) ---
        GAP_LENS_TO_LENS = 800.0
        GAP_LENS_TO_EURO = 800.0
        GAP_EURO_TO_EURO = 600.0
        LEFT_AISLE_PERCENTAGE = self._calculate_dynamic_left_aisle_percentage()
        VERTICAL_BUFFER_PERCENTAGE = 0.70

        # --- 2. Load fixtures into a UNIFIED QUEUE (Unchanged) ---
        config = self.fixtures.get("floor_fixtures", {})
        euro_count = config.get("Euro_centre", 0)
        lensbar_count = config.get("Lensbar", 0)
        if euro_count + lensbar_count == 0: return

        fixture_queue = collections.deque()
        try:
            if lensbar_count > 0:
                lensbar_fxtr = Fixture("Lensbar", self.fixture_dict["Lensbar"]["path"])
                fixture_queue.extend([lensbar_fxtr] * lensbar_count)
            if euro_count > 0:
                euro_fxtr = Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"])
                fixture_queue.extend([euro_fxtr] * euro_count)
        except Exception as e:
            print(f"🔥 FATAL: Could not load fixture: {e}")
            return

        # --- 3. Iterative Placement Loop ---
        room_width = self.cvc.max_x - self.cvc.min_x
        left_aisle_dynamic = room_width * LEFT_AISLE_PERCENTAGE
        current_x = self.cvc.min_x + left_aisle_dynamic
        placeable_width = self.cvc.max_x - 50.0
        
        last_placed_type = None

        while fixture_queue:
            next_fxtr_obj = fixture_queue[0]
            stack_width = next_fxtr_obj.height # This is the horizontal footprint after rotation

            if current_x + stack_width > placeable_width:
                print("    -> ⚠️ Ran out of horizontal space. Stopping placement.")
                break

            print(f"\n    -> Analyzing position for new '{next_fxtr_obj.name}' stack at x={current_x:.0f}")
            
            # --- Local Height Calculation (Unchanged) ---
            stack_center_x = current_x + (stack_width / 2)
            vertical_slice = LineString([(stack_center_x, self.cvc.min_y - 100), (stack_center_x, self.cvc.max_y + 100)])
            intersection = self.floorplan_polygon.intersection(vertical_slice)

            if not isinstance(intersection, LineString) or intersection.is_empty:
                print(f"      -> SKIPPING: Position x={current_x:.0f} is invalid.")
                current_x += 100; continue

            local_min_y, local_max_y = intersection.bounds[1], intersection.bounds[3]
            local_height = local_max_y - local_min_y
            dynamic_vertical_buffer = local_height * VERTICAL_BUFFER_PERCENTAGE

            # --- Stacking Decision Logic (Unchanged) ---
            num_to_place = 0
            stack_height = 0
            
            if next_fxtr_obj.name == "Lensbar":
                required_height_for_one = next_fxtr_obj.width + dynamic_vertical_buffer
                if required_height_for_one <= local_height:
                    num_to_place = 1; stack_height = next_fxtr_obj.width
                else:
                    current_x += 100; continue
            
            elif next_fxtr_obj.name == "Euro_centre":
                required_height_for_two = (next_fxtr_obj.width * 2) + dynamic_vertical_buffer
                required_height_for_one = next_fxtr_obj.width + dynamic_vertical_buffer
                if len(fixture_queue) >= 2 and all(f.name == "Euro_centre" for f in list(fixture_queue)[:2]) and required_height_for_two <= local_height:
                    num_to_place = 2; stack_height = next_fxtr_obj.width * 2
                elif required_height_for_one <= local_height:
                    num_to_place = 1; stack_height = next_fxtr_obj.width
                else:
                    current_x += 100; continue

            # --- NEW & IMPROVED PLACEMENT LOGIC ---
            
            stack_to_place = [fixture_queue.popleft() for _ in range(num_to_place)]
            
            # 1. Calculate the starting Y-coordinate for the entire stack's bounding box.
            stack_start_y = local_min_y + (local_height - stack_height) / 2
            
            current_y_cursor = stack_start_y
            for fxtr in stack_to_place:
                # 2. Determine the rotation and the height of the current fixture in the stack.
                rotated_height = fxtr.width
                if fxtr.name == "Lensbar":
                    rotation = 270
                else: # Euro_centre
                    rotation = 90
                
                # 3. Calculate the desired CENTER point of this specific fixture.
                target_center_x = current_x + (stack_width / 2)
                target_center_y = current_y_cursor + (rotated_height / 2)
                target_center = Vec2(target_center_x, target_center_y)

                # 4. Call the robust helper function to perform the actual placement.
                if self._validate_and_place_at_point(fxtr, target_center, rotation, placed_bboxes):
                    print(f"    -> Placed '{fxtr.name}' centered at ({target_center.x:.0f}, {target_center.y:.0f})")
                    last_placed_type = fxtr.name
                else:
                    print(f"    -> ⚠️ Final validation failed for '{fxtr.name}'. It may be skipped.")
                    # Optional: Re-add the fixture to the queue if it fails
                    # fixture_queue.appendleft(fxtr)

                current_y_cursor += rotated_height

            # --- Horizontal Advancement (Unchanged) ---
            horizontal_gap = 0
            if fixture_queue:
                next_fixture_in_queue = fixture_queue[0]
                if last_placed_type == "Lensbar" and next_fixture_in_queue.name == "Lensbar":
                    horizontal_gap = GAP_LENS_TO_LENS
                elif last_placed_type == "Lensbar" and next_fixture_in_queue.name == "Euro_centre":
                    horizontal_gap = GAP_LENS_TO_EURO
                else:
                    horizontal_gap = GAP_EURO_TO_EURO
            
            current_x += stack_width + horizontal_gap

        if fixture_queue:
            print(f"\n--- ⚠️ Finished with {len(fixture_queue)} unplaced fixtures ---")
        else:
            print("\n--- ✅ Finished Iterative Smart Stacking Placement ---")


    def _calculate_dynamic_left_aisle_percentage(self) -> float:
        """
        Calculates a dynamic LEFT AISLE percentage using a simple, predictable,
        count-based tiered system.
        """
        from Fixture import Fixture
        import math
        
        print("\n    -> Calculating dynamic LEFT AISLE based on simple fixture COUNT...")

        try:
            # --- STEP 1: Get the total count of all major fixtures ---
            total_fixture_count = 0
            
            # Central fixtures
            total_fixture_count += self.fixtures.get("floor_fixtures", {}).get("Euro_centre", 0)
            total_fixture_count += self.fixtures.get("floor_fixtures", {}).get("Lensbar", 0)

            # Other major fixtures
            total_fixture_count += self.fixtures.get("Corian_table_set", {}).get("Corian_table", 0)
            total_fixture_count += self.fixtures.get("table_fixtures", {}).get("Standing_table", 0)
            total_fixture_count += sum(self.fixtures.get("POS", {}).values())

            print(f"      -> Total major fixture count is: {total_fixture_count}")

            # --- STEP 2: Choose an aisle percentage from simple tiers ---
            # You can easily TWEAK these numbers to change the behavior.
            
            if total_fixture_count <= 7: # Low Congestion
                aisle_pct = 0.45 # Use a spacious 40% aisle
                print(f"      -> Count is LOW. Using a spacious {aisle_pct:.0%} left aisle.")
            
            elif total_fixture_count <= 10: # Medium Congestion
                aisle_pct = 0.20 # Use a standard 30% aisle
                print(f"      -> Count is MEDIUM. Using a standard {aisle_pct:.0%} left aisle.")

            elif total_fixture_count <= 14: # Medium Congestion
                aisle_pct = 0.15 # Use a standard 30% aisle
                print(f"      -> Count is MEDIUM. Using a standard {aisle_pct:.0%} left aisle.")

            elif total_fixture_count <= 25: # Medium Congestion
                aisle_pct = 0.15 # Use a standard 30% aisle
                print(f"      -> Count is MEDIUM. Using a standard {aisle_pct:.0%} left aisle.")
            
            else: # High Congestion
                aisle_pct = 0.15 # Use a compact 15% aisle
                print(f"      -> Count is HIGH. Using a compact {aisle_pct:.0%} left aisle.")
                
            return aisle_pct

        except Exception as e:
            print(f"    -> ⚠️ Could not calculate count-based aisle due to an error: {e}")
            return 0.20 # Return a safe default
    

    def place_central_fixtures_dynamically_landscape(self, placed_bboxes: List[tuple]) -> None:
        """
        Places fixtures in balanced vertical stacks using a robust, two-phase search strategy
        ideal for complex and irregular floorplans.
        """
        from Fixture import Fixture
        from shapely.geometry import box, LineString
        import math
        import collections

        print("\n--- 🧠 Placing Fixtures with Two-Phase Search Strategy ---")

        # --- 1. Setup & Dimension Calculation ---
        MAX_FIXTURES_PER_STACK = 2
        HORIZONTAL_STACK_GAP = 1200.0
        
        config = self.fixtures.get("floor_fixtures", {})
        euro_count = config.get("Euro_centre", 0)
        if euro_count == 0: return

        try:
            fxtr_obj = Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"])
        except Exception as e:
            print(f"🔥 FATAL: Could not load 'Euro_centre' fixture: {e}")
            return

        stacks = []
        fixture_queue = collections.deque([fxtr_obj] * euro_count)
        while fixture_queue:
            stacks.append([fixture_queue.popleft() for _ in range(MAX_FIXTURES_PER_STACK) if fixture_queue])
        
        num_stacks = len(stacks)
        stack_width = fxtr_obj.height
        max_stack_height = fxtr_obj.width * MAX_FIXTURES_PER_STACK
        total_block_width = (num_stacks * stack_width) + ((num_stacks - 1) * HORIZONTAL_STACK_GAP)
        print(f"  -> Layout planned: {num_stacks} stacks. Required width: {total_block_width:.0f}mm, height: {max_stack_height:.0f}mm.")

        # --- 2. PHASE 1: Find the Widest Horizontal Zone ---
        best_horizontal_fit = {"x_min": 0, "x_max": 0, "y_level": 0, "width": 0}
        bounds = self.floorplan_polygon.bounds
        
        for y_level in range(int(bounds[1]), int(bounds[3]), 50): # Scan every 50mm
            horizontal_slice = LineString([(bounds[0] - 10, y_level), (bounds[2] + 10, y_level)])
            intersection = self.floorplan_polygon.intersection(horizontal_slice)
            
            geoms = intersection.geoms if hasattr(intersection, 'geoms') else [intersection]
            for line in geoms:
                if isinstance(line, LineString) and line.length > best_horizontal_fit["width"]:
                    best_horizontal_fit = {
                        "x_min": line.bounds[0], 
                        "x_max": line.bounds[2], 
                        "y_level": y_level, 
                        "width": line.length
                    }

        if best_horizontal_fit["width"] < total_block_width:
            print(f"⚠️ CRITICAL: Could not find a horizontal space wide enough. Required: {total_block_width:.0f}, Max Found: {best_horizontal_fit['width']:.0f}.")
            return
        
        print(f"  -> Phase 1 complete. Found widest zone ({best_horizontal_fit['width']:.0f}mm) at y={best_horizontal_fit['y_level']:.0f}.")
        
        # Center the block horizontally within this widest zone
        block_start_x = best_horizontal_fit["x_min"] + (best_horizontal_fit["width"] - total_block_width) / 2

        # --- 3. PHASE 2: Find the Best Vertical Position within that Zone ---
        valid_y_positions = []
        for test_y in range(int(bounds[1]), int(bounds[3] - max_stack_height), 50):
            test_block = box(block_start_x, test_y, block_start_x + total_block_width, test_y + max_stack_height)
            if self.floorplan_polygon.contains(test_block.buffer(-1.0)) and not any(test_block.intersects(box(*b)) for b in placed_bboxes):
                valid_y_positions.append(test_y)

        if not valid_y_positions:
            print("⚠️ CRITICAL: Found a wide enough horizontal space, but no clear vertical space to fit the fixtures.")
            return

        # Choose the centermost valid Y position
        final_y = valid_y_positions[len(valid_y_positions) // 2]
        print(f"  -> Phase 2 complete. Found optimal vertical position starting at y={final_y:.0f}.")

        # --- 4. Final Placement ---
        current_x = block_start_x
        unplaced_fixtures = []
        for i, stack in enumerate(stacks):
            stack_height = sum(f.width for f in stack)
            # Center each stack vertically within the max possible height
            stack_start_y = final_y + (max_stack_height - stack_height) / 2
            
            print(f"\n  -> Placing Stack #{i + 1} at x ≈ {current_x:.0f}")

            current_y = stack_start_y
            for fxtr in stack:
                rotated_width, rotated_height = fxtr.height, fxtr.width
                x1, y1 = current_x, current_y
                self.place_fixture(fxtr, (x1 + rotated_width, y1, 0), 90, True)
                placed_bboxes.append((x1, y1, x1 + rotated_width, y1 + rotated_height))
                print(f"    -> ✅ Placed '{fxtr.name}' at ({x1:.0f}, {y1:.0f})")
                current_y += rotated_height
            
            current_x += stack_width + HORIZONTAL_STACK_GAP

        print("\n--- ✅ Finished Balanced Multi-Column Placement ---")

    def _get_wall_details(self, side: str) -> Optional[Dict[str, Any]]:
        """
        Finds the longest wall segment on a given side ('top', 'bottom', 'left', 'right')
        and returns its geometric details.
        """
        all_segments = self.cvc.get_wall_segments(min_length=100)
        if not all_segments:
            return None

        # --- FIX: Calculate min/max y-values directly from the coordinate list ---
        min_y = min(self.cvc.y_coords)
        max_y = max(self.cvc.y_coords)
        # --- End of Fix ---

        # Define the search criteria based on the side
        if side in ['left', 'right']:
            target_coord = self.cvc.min_x if side == 'left' else self.cvc.max_x
            tolerance = (self.cvc.max_x - self.cvc.min_x) * 0.1
            coord_index = 0  # Compare X-coordinates
        elif side in ['top', 'bottom']:
            # Use the min/max y values we just calculated
            target_coord = max_y if side == 'top' else min_y
            tolerance = (max_y - min_y) * 0.1
            coord_index = 1  # Compare Y-coordinates
        else:
            return None

        # Find candidate segments within the tolerance zone
        candidate_segments = []
        for p1_coords, p2_coords in all_segments:
            mid_coord = (p1_coords[coord_index] + p2_coords[coord_index]) / 2
            if abs(mid_coord - target_coord) < tolerance:
                candidate_segments.append((Vec2(p1_coords), Vec2(p2_coords)))
        
        if not candidate_segments:
            return None

        # Find the longest segment among the candidates
        longest_segment = max(candidate_segments, key=lambda seg: (seg[1] - seg[0]).magnitude)
        p1, p2 = longest_segment

        # --- Standardize Segment Direction ---
        # For Left/Right walls: ensure vector points upwards (bottom to top)
        if side in ['left', 'right'] and p1.y > p2.y:
            p1, p2 = p2, p1
        # For Top/Bottom walls: ensure vector points rightwards (left to right)
        elif side in ['top', 'bottom'] and p1.x > p2.x:
            p1, p2 = p2, p1
            
        wall_vector = p2 - p1
        
        return {
            "start_point": p1,
            "end_point": p2,
            "angle_deg": math.degrees(wall_vector.angle),
            "length": wall_vector.magnitude,
            "vector": wall_vector
        }

        # return {
        #     "start_point": p1,
        #     "end_point": p2,
        #     "angle_deg": math.degrees(wall_vector.angle),
        #     "length": wall_vector.magnitude,
        #     "vector": wall_vector,
        #     "side": side  # <-- This is the only line that has been added
        # }

    # def place_central_fixtures_dynamically_landscape(self, placed_bboxes: List[tuple]) -> None:
    #     """
    #     Places central fixtures using a resilient, iterative, multi-row packing strategy.

    #     Philosophy:
    #     1.  Determines the optimal number of rows to fit fixtures within a "placeable zone"
    #         that respects wall buffers and customer aisles.
    #     2.  It then iterates through each row, placing fixtures one by one.
    #     3.  For each fixture, it calculates an IDEAL spot relative to the last placed
    #         fixture. If that spot is blocked, it RESILIENTLY SEARCHES forward
    #         to find the next available clear space in the row.
    #     """
    #     from Fixture import Fixture
    #     from shapely.geometry import box
    #     import math
    #     import collections
    #     print("\n--- 🧠 Placing Central Fixtures with RESILIENT Iterative Strategy ---")

    #     # --- 1. Define Architectural Rules ---
    #     MIN_AISLE_WIDTH = 1200.0
    #     WALL_FIXTURE_BUFFER = 600.0
    #     INTERNAL_FIXTURE_GAP = 800.0
    #     VERTICAL_ROW_GAP = 1200.0
        
    #     # --- 2. Load Fixtures ---
    #     config = self.fixtures.get("floor_fixtures", {})
    #     fixtures_to_place = []
    #     # (The logic to load fixtures is the same as before)
    #     lensbar_count = config.get("Lensbar", 0)
    #     euro_count = config.get("Euro_centre", 0)
    #     total_fixtures = lensbar_count + euro_count
    #     if total_fixtures == 0: return
    #     try:
    #         if lensbar_count > 0: fixtures_to_place.extend([Fixture("Lensbar", self.fixture_dict["Lensbar"]["path"])] * lensbar_count)
    #         if euro_count > 0: fixtures_to_place.extend([Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"])] * euro_count)
    #     except Exception as e:
    #         print(f"🔥 FATAL: Could not load a required central fixture: {e}")
    #         return

    #     # --- 3. Determine Optimal Row Configuration (Same as before) ---
    #     room_width = self.cvc.max_x - self.cvc.min_x
    #     max_block_width = room_width - (2 * WALL_FIXTURE_BUFFER) - (2 * MIN_AISLE_WIDTH)
    #     num_rows = 1
    #     while True:
    #         if num_rows > total_fixtures:
    #             print("⚠️ CRITICAL: Not enough horizontal space to place even one fixture. Aborting.")
    #             return
    #         fixtures_per_row = math.ceil(total_fixtures / num_rows)
    #         longest_row_width = sum(f.height for f in fixtures_to_place[:int(fixtures_per_row)]) + (INTERNAL_FIXTURE_GAP * (fixtures_per_row - 1))
    #         if longest_row_width <= max_block_width:
    #             print(f"  -> ✅ Optimal layout found: {num_rows} row(s) of up to {int(fixtures_per_row)} fixtures each.")
    #             break
    #         num_rows += 1
        
    #     # --- 4. Calculate Overall Block Position (Same as before) ---
    #     avg_fixture_depth = sum(f.width for f in fixtures_to_place) / total_fixtures
    #     total_block_height = (num_rows * avg_fixture_depth) + (VERTICAL_ROW_GAP * (num_rows - 1))
    #     placeable_zone_start_x = self.cvc.min_x + WALL_FIXTURE_BUFFER + MIN_AISLE_WIDTH
    #     block_start_x = placeable_zone_start_x + (max_block_width - longest_row_width) / 2
    #     top_wall = self._get_wall_details('top')
    #     bottom_wall = self._get_wall_details('bottom')
    #     top_y_boundary = top_wall["start_point"].y if top_wall else self.cvc.max_y
    #     bottom_y_boundary = bottom_wall["start_point"].y if bottom_wall else self.cvc.min_y
    #     block_start_y = bottom_y_boundary + (top_y_boundary - bottom_y_boundary - total_block_height) / 2

    #     # --- 5. NEW: The Iterative Placement Loop with Resilient Search ---
    #     fixture_queue = collections.deque(fixtures_to_place)
    #     unplaced_fixtures = []
    #     current_y = block_start_y

    #     # Define a helper function for searching within the main function's scope
    #     def _find_next_available_spot(start_x, y, fxtr_obj, max_search_dist=3000, step=50):
    #         """Searches horizontally from a starting point to find a clear spot."""
    #         search_x = start_x
    #         while search_x < start_x + max_search_dist:
    #             rotated_w, rotated_h = fxtr_obj.height, fxtr_obj.width
    #             candidate_box = box(search_x, y, search_x + rotated_w, y + rotated_h)
    #             if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
    #                 return search_x # Return the valid X-coordinate
    #             search_x += step
    #         return None # Return None if no spot is found

    #     for row in range(num_rows):
    #         if not fixture_queue: break
            
    #         fixtures_in_this_row_count = min(int(fixtures_per_row), len(fixture_queue))
    #         current_row_width = sum(f.height for f in list(fixture_queue)[:fixtures_in_this_row_count]) + (INTERNAL_FIXTURE_GAP * (fixtures_in_this_row_count - 1))
            
    #         # Center this row within the larger block's width
    #         last_fixture_end_x = block_start_x + (longest_row_width - current_row_width) / 2
            
    #         print(f"\n  -> Placing Row #{row + 1} at y={current_y:.0f}")

    #         for i in range(fixtures_in_this_row_count):
    #             fxtr = fixture_queue.popleft()
                
    #             # If it's the first fixture, its ideal_x is the start of the row.
    #             # Otherwise, it's the end of the last fixture plus a gap.
    #             ideal_x = last_fixture_end_x if i == 0 else last_fixture_end_x + INTERNAL_FIXTURE_GAP
                
    #             print(f"    -> Searching for spot for '{fxtr.name}' starting at x={ideal_x:.0f}...")
                
    #             # Call the resilient search helper
    #             found_x = _find_next_available_spot(ideal_x, current_y, fxtr)
                
    #             if found_x is not None:
    #                 # A valid spot was found! Place the fixture.
    #                 rotated_width, rotated_height = fxtr.height, fxtr.width
    #                 insert_x = found_x + rotated_width
    #                 final_insert_point = (insert_x, current_y, 0)
                    
    #                 self.place_fixture(fxtr, final_insert_point, 90, True)
    #                 placed_bboxes.append((found_x, current_y, found_x + rotated_width, current_y + rotated_height))
    #                 print(f"      ✅ Placed '{fxtr.name}' at found spot ({found_x:.0f}, {current_y:.0f})")
                    
    #                 # CRITICAL: The next search starts from the end of where this fixture ACTUALLY landed.
    #                 last_fixture_end_x = found_x + rotated_width
    #             else:
    #                 # The search failed for this fixture.
    #                 print(f"      ⚠️ Could not find a clear spot for '{fxtr.name}' in this row.")
    #                 unplaced_fixtures.append(fxtr)
            
    #         current_y += avg_fixture_depth + VERTICAL_ROW_GAP

    #     if unplaced_fixtures:
    #         print(f"\n--- ⚠️ Finished with {len(unplaced_fixtures)} unplaced fixtures. ---")
    #     else:
    #         print("\n--- ✅ Finished Dynamic Central Fixture Placement Successfully ---")


    def place_wall_queue_landscape(self, wall_side: str, fixture_queue: list, placed_bboxes: list, start_point: Vec2, wall_angle_deg: float, placement_direction: str = 'start_to_end'):
        """
        Places a queue of fixtures along a single wall and returns any unplaced fixtures.
        placement_direction: 'start_to_end' or 'end_to_start'.
        """
        from Fixture import Fixture
        from shapely.geometry import Polygon
        from ezdxf.math import BoundingBox2d, Matrix44, Vec2
        
        # --- Setup ---
        mirror_selection_config = self.fixtures.get("mirror_selection", {})
        selected_mirror_name = next((name for name, selected in mirror_selection_config.items() if selected > 0), "mirror")
        horizontal_inset_for_hybrid = 0.0 if selected_mirror_name == "mirror_different" else 50.0

        wall_details = self._get_wall_details(wall_side)
        if not wall_details: return fixture_queue # Return all if wall is invalid

        wall_direction = wall_details["vector"].normalize()
        origin = wall_details["start_point"] if placement_direction == 'start_to_end' else wall_details["end_point"]
        
        # Determine inward normal vector
        perp_vec = wall_direction.orthogonal()
        test_point_inward = origin + perp_vec
        inward_normal = perp_vec if self.floorplan_polygon.contains(Point(test_point_inward.x, test_point_inward.y)) else -perp_vec

        fixture_rotation_deg = wall_angle_deg
        if wall_side == 'right': fixture_rotation_deg += 180
        if wall_side == 'top' and placement_direction == 'end_to_start': fixture_rotation_deg += 180
        if wall_side == 'bottom' and placement_direction == 'end_to_start': fixture_rotation_deg += 180


        cursor = 50.0
        margin_from_wall = 10.0
        unplaced_fixtures = []

        print(f"--- Placing {len(fixture_queue)} fixtures on {wall_side} wall (Direction: {placement_direction}) ---")

        for idx, (fixture_name, _) in enumerate(fixture_queue):
            try:
                hybrid = Fixture(fixture_name, self.fixture_dict[fixture_name]["path"])
                mirror = Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
            except (KeyError, ValueError) as e:
                unplaced_fixtures.append((fixture_name, 1))
                continue
            
            pair_width = hybrid.width + mirror.width
            if cursor + pair_width > wall_details["length"]:
                print(f"⚠️ Not enough space on {wall_side} wall for '{fixture_name}'.")
                unplaced_fixtures.extend(fixture_queue[idx:])
                break

            # --- A. Validate and Place Hybrid ---
            hybrid_offset = margin_from_wall + hybrid.height + horizontal_inset_for_hybrid
            direction_multiplier = -1 if placement_direction == 'end_to_start' else 1
            
            hybrid_insert_pos = origin + (wall_direction * cursor * direction_multiplier) + (inward_normal * hybrid_offset)

            transform_h = Matrix44.chain(Matrix44.z_rotate(math.radians(fixture_rotation_deg)), Matrix44.translate(hybrid_insert_pos.x, hybrid_insert_pos.y, 0))
            world_corners_h = list(transform_h.transform_vertices(hybrid.bounding_box.rect_vertices()))
            
            if not self.floorplan_polygon.contains(Polygon([(p.x, p.y) for p in world_corners_h])):
                unplaced_fixtures.extend(fixture_queue[idx:])
                break

            aabb_h = BoundingBox2d(world_corners_h)
            if any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes):
                unplaced_fixtures.extend(fixture_queue[idx:])
                break
                
            self.place_fixture(hybrid, (hybrid_insert_pos.x, hybrid_insert_pos.y, 0), fixture_rotation_deg, True)

            # --- B. Validate and Place Mirror ---
            mirror_y_offset = cursor + hybrid.width
            mirror_offset_from_wall = margin_from_wall + mirror.height
            mirror_insert_pos = origin + (wall_direction * mirror_y_offset * direction_multiplier) + (inward_normal * mirror_offset_from_wall)
            
            transform_m = Matrix44.chain(Matrix44.z_rotate(math.radians(fixture_rotation_deg)), Matrix44.translate(mirror_insert_pos.x, mirror_insert_pos.y, 0))
            world_corners_m = list(transform_m.transform_vertices(mirror.bounding_box.rect_vertices()))

            if not self.floorplan_polygon.contains(Polygon([(p.x, p.y) for p in world_corners_m])):
                # This case is tricky, we've already placed the hybrid. For simplicity, we stop.
                unplaced_fixtures.extend(fixture_queue[idx+1:]) # Don't re-add the current hybrid
                break

            aabb_m = BoundingBox2d(world_corners_m)
            if any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes):
                unplaced_fixtures.extend(fixture_queue[idx+1:])
                break
            
            self.place_fixture(mirror, (mirror_insert_pos.x, mirror_insert_pos.y, 0), fixture_rotation_deg, True)
            
            cursor += pair_width
            
        return unplaced_fixtures
    
    def place_wall_fixtures_continuous(self, walls_to_use=['left', 'top']):
        """
        Places wall fixtures in a continuous flow across a specified sequence of walls.
        """
        import collections
        print(f"\n--- Starting CONTINUOUS Wall Fixture Placement on: {walls_to_use} ---")

        # 1. Create a master queue of all wall fixtures to place
        wall_fixtures_config = self.fixtures.get("wall_fixtures", {})
        master_queue = []
        for name, count in wall_fixtures_config.items():
            master_queue.extend([(name, 1)] * count)
        
        if not master_queue:
            print("ℹ️ No wall fixtures to place.")
            return

        # 2. Get initial obstacles
        initial_obstacles = self._get_accurate_obstacle_bboxes()
        remaining_fixtures = master_queue

        # 3. Loop through each wall in the sequence and attempt placement
        for i, wall_side in enumerate(walls_to_use):
            if not remaining_fixtures:
                print("✅ All wall fixtures placed successfully.")
                break

            wall_details = self._get_wall_details(wall_side)
            if not wall_details:
                print(f"⚠️ Cannot find wall '{wall_side}'. Skipping.")
                continue
            
            # Determine placement direction based on the sequence
            placement_direction = 'start_to_end' # Default: left-to-right or bottom-to-top
            # If placing on top wall AND the previous wall was the right wall
            if wall_side == 'top' and i > 0 and walls_to_use[i-1] == 'right':
                placement_direction = 'end_to_start' # Place right-to-left

            # Call the queue, which will return any fixtures it couldn't place
            remaining_fixtures = self.place_wall_queue_landscape(
                wall_side=wall_side,
                fixture_queue=remaining_fixtures,
                placed_bboxes=initial_obstacles,
                start_point=wall_details["start_point"],
                wall_angle_deg=wall_details["angle_deg"],
                placement_direction=placement_direction
            )

        if remaining_fixtures:
            print(f"\n⚠️ Could not place all wall fixtures. {len(remaining_fixtures)} items remain unplaced.")


    def place_discussion_tables_landscape(self, placed_bboxes):
        """
        Places discussion tables in a flexible manner above and below Euro Centre
        fixtures, treating all available spots as a pool. Any tables that cannot
        be placed are returned for fallback placement.
        """
        from Fixture import Fixture
        from ezdxf.bbox import extents
        from shapely.geometry import box
        import collections
        print("\n--- Placing Discussion Tables for Landscape Mode (Flexible Strategy) ---")

        try:
            # 1. Find all placed Euro Centre fixtures
            euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
            if not euro_entities:
                print("ℹ️ No Euro Centre fixtures found to anchor to. Skipping.")
                return []
                
            euro_bboxes = sorted([extents([e]) for e in euro_entities], key=lambda b: b.extmin.x)
            
            # 2. Get the complete list of all discussion tables from the config
            all_tables_config = []
            table_config = self.fixtures.get("floor_fixtures_landscape", {})
            for name, total_count in table_config.items():
                if "Discussion_table" in name and total_count > 0:
                    fxtr = Fixture(name, self.fixture_dict[name]["path"])
                    all_tables_config.extend([fxtr] * total_count)

            if not all_tables_config:
                print("ℹ️ No discussion tables specified.")
                return []

            # --- NEW LOGIC: Use a queue for flexible placement ---
            # All tables are now in a single queue to be placed in the first available spot.
            table_queue = collections.deque(all_tables_config)
            print(f"ℹ️ Attempting to place {len(table_queue)} discussion tables in the central area...")
            
            gap = 300 # Using a smaller gap to increase chance of success

            # --- PLACEMENT PHASE 1: Try all spots ABOVE the Euro Centres ---
            print("  -> Trying all available spots ABOVE Euro Centres...")
            for i, euro_box in enumerate(euro_bboxes):
                if not table_queue: break # Stop if all tables are placed

                table = table_queue[0] # Peek at the next table to get its dimensions
                x_pos = euro_box.center.x - (table.width / 2)
                y_pos = euro_box.extmax.y + gap
                
                x1, y1, x2, y2 = x_pos, y_pos, x_pos + table.width, y_pos + table.height
                candidate_box = box(x1, y1, x2, y2)
                is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
                is_inside = self.floorplan_polygon.contains(candidate_box)

                if is_inside and not is_overlapping:
                    # If the spot is valid, remove the table from the queue and place it
                    table_to_place = table_queue.popleft()
                    self.place_fixture(table_to_place, (x_pos, y_pos, 0), 0, False)
                    placed_bboxes.append((x1, y1, x2, y2))
                    print(f"✅ Placed '{table_to_place.name}' above Euro Centre #{i+1}")

            # --- PLACEMENT PHASE 2: Try all spots BELOW the Euro Centres with remaining tables ---
            if table_queue:
                print("  -> Trying all available spots BELOW Euro Centres...")
                for i, euro_box in enumerate(euro_bboxes):
                    if not table_queue: break

                    table = table_queue[0]
                    x_pos = euro_box.center.x - (table.width / 2)
                    y_pos = euro_box.extmin.y - table.height - gap

                    x1, y1, x2, y2 = x_pos, y_pos, x_pos + table.width, y_pos + table.height
                    candidate_box = box(x1, y1, x2, y2)
                    is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
                    is_inside = self.floorplan_polygon.contains(candidate_box)

                    if is_inside and not is_overlapping:
                        table_to_place = table_queue.popleft()
                        self.place_fixture(table_to_place, (x_pos, y_pos, 0), 0, False)
                        placed_bboxes.append((x1, y1, x2, y2))
                        print(f"✅ Placed '{table_to_place.name}' below Euro Centre #{i+1}")

            # Any tables still in the queue are the leftovers for the fallback function
            remaining_tables_for_fallback = list(table_queue)
            if remaining_tables_for_fallback:
                print(f"ℹ️ {len(remaining_tables_for_fallback)} tables could not be placed in the center and will be passed to the fallback function.")

            return remaining_tables_for_fallback

        except Exception as e:
            print(f"🔥 An error occurred in place_discussion_tables_landscape: {e}")
            return []
    
    def place_remaining_tables_in_aisles(self, tables_to_place, placed_bboxes):
        """
        Fallback to place remaining discussion tables in the 'left' and 'top' aisles.
        """
        import collections
        from ezdxf.bbox import extents
        print(f"\n--- Placing {len(tables_to_place)} remaining Discussion Tables in Aisles ---")
        if not tables_to_place:
            return

        try:
            min_y = min(self.cvc.y_coords)
            max_y = max(self.cvc.y_coords)
            
            euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
            if not euro_entities:
                print("⚠️ Cannot define aisles without Euro Centres. Skipping remaining tables.")
                return
            
            euro_cluster_bbox = extents(euro_entities)
            
            wall_fixture_depth = 600
            aisle_gap = 200

            zones = {
                'left': {
                    'x_min': self.cvc.min_x + wall_fixture_depth,
                    'x_max': euro_cluster_bbox.extmin.x - aisle_gap,
                    'y_min': min_y,
                    'y_max': max_y,
                    'rotation': 90,
                    'stack_direction': 'vertical'
                },
                'top': {
                    'x_min': self.cvc.min_x,
                    'x_max': self.cvc.max_x,
                    'y_min': euro_cluster_bbox.extmax.y + aisle_gap,
                    'y_max': max_y - wall_fixture_depth,
                    'rotation': 0,
                    'stack_direction': 'horizontal'
                }
            }
            
            table_queue = collections.deque(tables_to_place)

            for zone_name in ['left', 'top']:
                if not table_queue: break

                zone = zones[zone_name]
                print(f"--- Trying to place tables in '{zone_name}' aisle ---")

                rotation = zone['rotation']
                
                if zone['stack_direction'] == 'vertical':
                    table_width_in_space = table_queue[0].height
                    if (zone['x_max'] - zone['x_min']) < table_width_in_space:
                        continue

                    x_pos = zone['x_min'] + ((zone['x_max'] - zone['x_min']) / 2) - (table_width_in_space / 2)
                    room_height = max_y - min_y
                    y_cursor = zone['y_min'] + (room_height * 0.20)

                    while table_queue:
                        table = table_queue[0]
                        w, h = table.height, table.width
                        if y_cursor + h > zone['y_max'] - 500: break

                        x1, y1, x2, y2 = x_pos, y_cursor, x_pos + w, y_cursor + h
                        if not any(not (x2 <= bx1 or x1 >= bx2 or y2 <= by1 or y1 >= by2) for bx1, by1, bx2, by2 in placed_bboxes):
                            table = table_queue.popleft()
                            self.place_fixture(table, (x_pos, y_cursor, 0), rotation, True)
                            placed_bboxes.append((x1, y1, x2, y2))
                            print(f"✅ Placed remaining '{table.name}' in '{zone_name}' aisle.")
                            
                            # CHANGE THIS VALUE for a larger VERTICAL gap between stacked tables
                            y_cursor += h + 1000 # Increased gap to 1000
                        else:
                            break
                
                elif zone['stack_direction'] == 'horizontal':
                    table_height_in_space = table_queue[0].height
                    if (zone['y_max'] - zone['y_min']) < table_height_in_space:
                        continue

                    y_pos = zone['y_min'] + ((zone['y_max'] - zone['y_min']) / 2) - (table_height_in_space / 2)
                    room_width = self.cvc.max_x - self.cvc.min_x
                    x_cursor = zone['x_min'] + (room_width * 0.20)
                    
                    while table_queue:
                        table = table_queue[0]
                        w, h = table.width, table.height
                        if x_cursor + w > zone['x_max'] - 500: break
                        
                        x1, y1, x2, y2 = x_cursor, y_pos, x_cursor + w, y_pos + h
                        if not any(not (x2 <= bx1 or x1 >= bx2 or y2 <= by1 or y1 >= by2) for bx1, by1, bx2, by2 in placed_bboxes):
                            table = table_queue.popleft()
                            self.place_fixture(table, (x_cursor, y_pos, 0), rotation, True)
                            placed_bboxes.append((x1, y1, x2, y2))
                            print(f"✅ Placed remaining '{table.name}' in '{zone_name}' aisle.")
                            
                            # CHANGE THIS VALUE for a larger HORIZONTAL gap between tables
                            x_cursor += w + 1000 # Increased gap to 1000
                        else:
                            break
        
        except Exception as e:
            print(f"🔥 An error occurred: {e}")
            traceback.print_exc()
            raise


    def place_pos_ar_landscape_v1(self, placed_bboxes):
        """
        Places the POS and AR units with an intelligent, conditional anchoring strategy.
        It determines the right-most fixture group to anchor to and searches for a
        valid spot, ensuring no overlaps.
        """
        from Fixture import Fixture
        from ezdxf.bbox import extents
        from shapely.geometry import Polygon, box
        import traceback

        print("\n--- Placing POS and AR with Conditional Anchoring ---")

        try:
            # 1. SETUP: Load fixtures and calculate dimensions
            pos_config = self.fixtures.get("POS", {})
            selected_pos_name = next((name for name, selected in pos_config.items() if selected > 0), None)
            
            if not selected_pos_name:
                print("ℹ️ No POS fixture selected.")
                return

            pos_fxtr = Fixture(selected_pos_name, self.fixture_dict[selected_pos_name]["path"])
            ar_fxtr = Fixture("AR", self.fixture_dict["AR"]["path"])

            rotation = 90
            pos_w, pos_h = pos_fxtr.height, pos_fxtr.width
            ar_w, ar_h = ar_fxtr.height, ar_fxtr.width
            gap_between = 100
            total_group_height = pos_h + gap_between + ar_h
            max_group_width = max(pos_w, ar_w)

            # 2. INTELLIGENT ANCHOR SELECTION
            anchor_bbox = None
            anchor_name = ""

            # Find all potential anchor groups that have already been placed
            standing_table_entities = [e for e in self.msp.query('INSERT') if "STANDING_TABLE" in e.dxf.name.upper()]
            corian_entities = [e for e in self.msp.query('INSERT') if "CORIAN_TABLE" in e.dxf.name.upper() or "LOUNGE_SEAT" in e.dxf.name.upper()]
            euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]

            # Prioritize the right-most fixture group
            if standing_table_entities:
                anchor_bbox = extents(standing_table_entities)
                anchor_name = "Standing Tables"
            elif corian_entities:
                anchor_bbox = extents(corian_entities)
                anchor_name = "Corian Sets"
            elif euro_entities:
                anchor_bbox = extents(euro_entities)
                anchor_name = "Euro Centres"
            else:
                print("⚠️ Cannot place POS/AR: No valid anchor fixtures (Euros, Corian, or Standing Tables) found.")
                return
            
            print(f"  -> Found anchor group: '{anchor_name}'.")

            # 3. CALCULATE IDEAL POSITION & PERFORM RESILIENT SEARCH
            gap_from_anchor = 1200.0
            ideal_x = anchor_bbox.extmax.x + gap_from_anchor
            
            room_center_y = (min(self.cvc.y_coords) + max(self.cvc.y_coords)) / 2
            ideal_y = room_center_y - (total_group_height / 2)

            # --- Helper function for validation ---
            def is_spot_valid(x_start, y_start):
                pos_x1, pos_y1 = x_start, y_start + ar_h + gap_between
                pos_poly = box(pos_x1, pos_y1, pos_x1 + pos_w, pos_y1 + pos_h)

                ar_x1, ar_y1 = x_start, y_start
                ar_poly = box(ar_x1, ar_y1, ar_x1 + ar_w, ar_y1 + ar_h)

                if not self.floorplan_polygon.contains(pos_poly) or not self.floorplan_polygon.contains(ar_poly):
                    return False
                if any(pos_poly.intersects(box(*b)) for b in placed_bboxes) or any(ar_poly.intersects(box(*b)) for b in placed_bboxes):
                    return False
                return True

            # --- Resilient Search Logic ---
            print(f"  -> Searching for a valid spot near x={ideal_x:.0f}...")
            found_spot = None
            search_offset = 0
            max_search_dist = (self.cvc.max_x - anchor_bbox.extmax.x) / 2 # Don't search too far

            while search_offset < max_search_dist:
                # Search rightwards first, then leftwards from the ideal spot
                test_x = ideal_x + search_offset
                if is_spot_valid(test_x, ideal_y):
                    found_spot = (test_x, ideal_y)
                    break
                
                if search_offset > 0:
                    test_x = ideal_x - search_offset
                    if is_spot_valid(test_x, ideal_y):
                        found_spot = (test_x, ideal_y)
                        break
                
                search_offset += 100 # Nudge search by 100mm

            # 4. VALIDATE AND PLACE
            if found_spot:
                final_x, final_y = found_spot
                print(f"    ✅ Found clear spot at x={final_x:.0f}")

                # Place AR (bottom item)
                ar_x, ar_y = final_x, final_y
                self.place_fixture(ar_fxtr, (ar_x, ar_y, 0), rotation, True)
                placed_bboxes.append((ar_x, ar_y, ar_x + ar_w, ar_y + ar_h))

                # Place POS (top item)
                pos_x, pos_y = final_x, final_y + ar_h + gap_between
                self.place_fixture(pos_fxtr, (pos_x, pos_y, 0), rotation, True)
                placed_bboxes.append((pos_x, pos_y, pos_x + pos_w, pos_y + pos_h))
                
                print(f"✅ Placed '{selected_pos_name}' and 'AR' successfully.")
            else:
                print("⚠️ FAILED: Could not find a clear spot for the POS/AR group after searching.")

        except Exception as e:
            print(f"🔥 An error occurred during POS/AR placement: {e}")
            traceback.print_exc()
            raise

    def place_pos_ar_landscape(self, placed_bboxes):
        """
        Places the POS and AR units.
        - If POS is selected, it uses an intelligent, conditional anchoring strategy
          to place the POS+AR group.
        - If POS is not selected, it anchors to the second clinic from the left
          and robustly searches for a spot on all four sides to place the AR unit.
        """
        from Fixture import Fixture
        from ezdxf.bbox import extents
        from ezdxf.math import BoundingBox2d, Vec2
        from shapely.geometry import Polygon, box
        import traceback

        try:
            # 1. SETUP: Load fixtures and check for POS selection
            pos_config = self.fixtures.get("POS", {})
            selected_pos_name = next((name for name, selected in pos_config.items() if selected > 0), None)
            ar_fxtr = Fixture("AR", self.fixture_dict["AR"]["path"])

            # --- STRATEGY 1: POS + AR Group Placement ---
            if selected_pos_name:
                print("\n--- Placing POS and AR with Conditional Anchoring ---")
                pos_fxtr = Fixture(selected_pos_name, self.fixture_dict[selected_pos_name]["path"])

                rotation = 90
                pos_w, pos_h = pos_fxtr.height, pos_fxtr.width
                ar_w, ar_h = ar_fxtr.height, ar_fxtr.width
                gap_between = 100
                total_group_height = pos_h + gap_between + ar_h
                
                anchor_bbox = None
                anchor_name = ""
                standing_table_entities = [e for e in self.msp.query('INSERT') if "STANDING_TABLE" in e.dxf.name.upper()]
                corian_entities = [e for e in self.msp.query('INSERT') if "CORIAN_TABLE" in e.dxf.name.upper() or "LOUNGE_SEAT" in e.dxf.name.upper()]
                euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]

                if standing_table_entities:
                    anchor_bbox = extents(standing_table_entities)
                    anchor_name = "Standing Tables"
                elif corian_entities:
                    anchor_bbox = extents(corian_entities)
                    anchor_name = "Corian Sets"
                elif euro_entities:
                    anchor_bbox = extents(euro_entities)
                    anchor_name = "Euro Centres"
                else:
                    print("⚠️ Cannot place POS/AR: No valid anchor fixtures found.")
                    return
                
                print(f"  -> Found anchor group: '{anchor_name}'.")

                gap_from_anchor = 1200.0
                ideal_x = anchor_bbox.extmax.x + gap_from_anchor
                room_center_y = (min(self.cvc.y_coords) + max(self.cvc.y_coords)) / 2
                ideal_y = room_center_y - (total_group_height / 2)

                def is_spot_valid(x_start, y_start):
                    pos_poly = box(x_start, y_start + ar_h + gap_between, x_start + pos_w, y_start + ar_h + gap_between + pos_h)
                    ar_poly = box(x_start, y_start, x_start + ar_w, y_start + ar_h)
                    if not self.floorplan_polygon.contains(pos_poly) or not self.floorplan_polygon.contains(ar_poly):
                        return False
                    if any(pos_poly.intersects(box(*b)) for b in placed_bboxes) or any(ar_poly.intersects(box(*b)) for b in placed_bboxes):
                        return False
                    return True

                print(f"  -> Searching for a valid spot near x={ideal_x:.0f}...")
                found_spot = None
                search_offset = 0
                max_search_dist = (self.cvc.max_x - anchor_bbox.extmax.x) / 2

                while search_offset < max_search_dist:
                    test_x = ideal_x + search_offset
                    if is_spot_valid(test_x, ideal_y):
                        found_spot = (test_x, ideal_y)
                        break
                    if search_offset > 0:
                        test_x = ideal_x - search_offset
                        if is_spot_valid(test_x, ideal_y):
                            found_spot = (test_x, ideal_y)
                            break
                    search_offset += 100

                if found_spot:
                    final_x, final_y = found_spot
                    print(f"    ✅ Found clear spot at x={final_x:.0f}")
                    ar_x, ar_y = final_x, final_y
                    self.place_fixture(ar_fxtr, (ar_x, ar_y, 0), rotation, True)
                    placed_bboxes.append((ar_x, ar_y, ar_x + ar_w, ar_y + ar_h))
                    pos_x, pos_y = final_x, final_y + ar_h + gap_between
                    self.place_fixture(pos_fxtr, (pos_x, pos_y, 0), rotation, True)
                    placed_bboxes.append((pos_x, pos_y, pos_x + pos_w, pos_y + pos_h))
                    print(f"✅ Placed '{selected_pos_name}' and 'AR' successfully.")
                else:
                    print("⚠️ FAILED: Could not find a clear spot for the POS/AR group after searching.")

            # --- STRATEGY 2: AR Only, Anchored to Second Clinic (with Manual Bbox Calculation)---
            else:
                print("\n--- Placing AR only (no POS selected), anchoring to Clinic ---")
                
                clinic_entities = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
                if not clinic_entities:
                    print("⚠️ Cannot place AR: No clinic found to anchor to.")
                    return

                sorted_clinics = sorted(clinic_entities, key=lambda e: e.dxf.insert.x)
                if len(sorted_clinics) >= 2:
                    anchor_clinic_entity = sorted_clinics[1]
                    print("  -> Anchoring to the second clinic from the left.")
                else:
                    anchor_clinic_entity = sorted_clinics[0]
                    print("  -> Only one clinic found. Anchoring to the first clinic.")
                
                # ################### THIS IS THE CORRECTED LOGIC ###################
                # Manually reconstruct the bounding box instead of using ezdxf.extents
                block_name_upper = anchor_clinic_entity.dxf.name.upper()
                best_match_key = ""
                for key in self.fixture_dict.keys():
                    sanitized_key = key.upper().replace(" ", "_")
                    if block_name_upper.startswith(sanitized_key):
                        if len(key) > len(best_match_key):
                            best_match_key = key
                
                if not best_match_key:
                    print(f"⚠️ Could not identify original fixture for '{anchor_clinic_entity.dxf.name}'. Aborting AR placement.")
                    return
                    
                anchor_fxtr_obj = Fixture(self.fixture_dict[best_match_key]["name"], self.fixture_dict[best_match_key]["path"])
                ip = anchor_clinic_entity.dxf.insert
                min_x, min_y = ip.x, ip.y
                max_x = min_x + anchor_fxtr_obj.width
                max_y = min_y + anchor_fxtr_obj.height + 2000
                anchor_bbox = BoundingBox2d([Vec2(min_x, min_y), Vec2(max_x, max_y)])
                print(f"  -> Manually calculated anchor bbox: ({min_x:.0f}, {min_y:.0f}) to ({max_x:.0f}, {max_y:.0f})")
                # ################### END OF CORRECTION ###################

                rotation = 0
                ar_w, ar_h = ar_fxtr.width, ar_fxtr.height
                gap_from_clinic = 5.0

                potential_spots = [
                    {"x": anchor_bbox.extmin.x - gap_from_clinic - ar_w, "y": anchor_bbox.center.y - (ar_h / 2), "side": "left"},
                    {"x": anchor_bbox.extmax.x + gap_from_clinic, "y": anchor_bbox.center.y - (ar_h / 2), "side": "right"},
                    {"x": anchor_bbox.center.x - (ar_w / 2), "y": anchor_bbox.extmax.y + gap_from_clinic, "side": "top"},
                    {"x": anchor_bbox.center.x - (ar_w / 2), "y": anchor_bbox.extmin.y - gap_from_clinic - ar_h, "side": "bottom"}
                ]

                def is_ar_spot_valid(x, y):
                    ar_poly = box(x, y, x + ar_w, y + ar_h)
                    if not self.floorplan_polygon.contains(ar_poly): return False
                    if any(ar_poly.intersects(box(*b)) for b in placed_bboxes): return False
                    return True

                is_placed = False
                for spot in potential_spots:
                    ideal_x, ideal_y = spot["x"], spot["y"]
                    if is_ar_spot_valid(ideal_x, ideal_y):
                        self.place_fixture(ar_fxtr, (ideal_x, ideal_y, 0), rotation, False)
                        placed_bboxes.append((ideal_x, ideal_y, ideal_x + ar_w, ideal_y + ar_h))
                        print(f"✅ Placed 'AR' successfully on the {spot['side']} of a clinic.")
                        is_placed = True
                        break 
                
                if not is_placed:
                    print("⚠️ FAILED: Could not find a clear spot for the AR fixture on any side of the clinic.")

        except Exception as e:
            print(f"🔥 An error occurred during POS/AR placement: {e}")
            traceback.print_exc()
            raise

        



    def _get_reordered_corners_right_bottom(self):
            """
            Helper function within DXF_Controller to reorder corners to start at
            the right-most, bottom-most point of a true vertical wall, ignoring bulges.
            This version uses a "closest point" search to be robust against float precision issues.
            """
            corners = self.cvc.corners
            if not corners:
                return []

            # 1. Create a list of all wall segments from the corner points
            all_segments = []
            for i in range(len(corners)):
                p1 = Vec2(corners[i])
                p2 = Vec2(corners[(i + 1) % len(corners)])
                all_segments.append((p1, p2))

            # 2. Filter segments to keep only the ones that are nearly vertical
            vertical_segments = []
            for p1, p2 in all_segments:
                if p1.distance(p2) == 0: continue
                angle = abs(math.degrees((p2 - p1).angle))
                if (80 < angle < 100) or (260 < angle < 280):
                    vertical_segments.append((p1, p2))

            if not vertical_segments:
                print("⚠️ Could not find any vertical walls to determine a starting point. Using original order.")
                return corners

            # 3. From that list of vertical walls, find the one that is furthest to the right
            rightmost_vertical_wall = max(vertical_segments, key=lambda seg: (seg[0].x + seg[1].x) / 2)

            # 4. From that specific wall, pick the endpoint with the lower Y-coordinate
            p1, p2 = rightmost_vertical_wall
            start_point_vec = p1 if p1.y < p2.y else p2
            
            # 5. NEW: Find the index of the CLOSEST point in the original list to avoid precision errors.
            min_dist = float('inf')
            start_idx = -1
            for i, corner in enumerate(corners):
                dist = start_point_vec.distance(Vec2(corner))
                if dist < min_dist:
                    min_dist = dist
                    start_idx = i
            
            if start_idx != -1:
                start_point = corners[start_idx]
                print(f"  -> Found exact starting point on right-most vertical wall: ({start_point[0]:.0f}, {start_point[1]:.0f})")
                return corners[start_idx:] + corners[:start_idx]
            else:
                # This is a fallback that should not be reached with the new logic
                print("⚠️ Could not find the calculated start point in the master corner list. Using original order.")
                return corners
            
    # In DXF_Controller.py

    ##### NEW ROBUST HELPER FUNCTION #####
    def _get_reordered_corners_top_right_robust_(self):
        """
        ROBUST HELPER: Gets corners starting from the point closest to the
        theoretical top-right corner of the entire floorplan's bounding box.
        Ensures a CLOCKWISE (CW) path to go DOWN the wall.
        """
        corners = self.cvc.corners
        if not corners:
            return []
        
        # 1. Define the target as the theoretical top-right corner
        target_x = self.cvc.max_x
        target_y = self.cvc.max_y

        # 2. Find the index of the corner point closest to that target
        start_idx = min(range(len(corners)),
                        key=lambda i: math.hypot(corners[i][0] - target_x, corners[i][1] - target_y))

        # 3. Reorder the list to begin with the found corner
        reordered = corners[start_idx:] + corners[:start_idx]
        
        # 4. Check the polygon's direction (winding order) using the signed area
        # A positive area means a counter-clockwise (CCW) path.
        signed_area = 0.5 * sum(x1*y2 - x2*y1 for (x1, y1), (x2, y2) in zip(reordered, reordered[1:] + [reordered[0]]))
        
        # 5. If the path is CCW, reverse it to make it CW so it goes down the right wall
        if signed_area > 0:
            print("  -> Path was counter-clockwise, reversing to ensure correct direction (down the right wall).")
            # This reverses the list while keeping the new starting point at the beginning
            reordered = reordered[0:1] + reordered[1:][::-1]
            
        return reordered
    
    # In DXF_Controller.py, replace the entire function with this one:

    def place_clinics_perimeter_walk(self, placed_bboxes):
        """
        MODIFIED VERSION: Places clinics by walking the perimeter and applies a
        horizontal mirror (xscale=-1) to clinics on the left and right walls.
        NOTE: This will likely not orient the entrance correctly.
        """
        import collections
        from shapely.geometry import Polygon, Point
        from ezdxf.math import Matrix44, Vec2, BoundingBox2d
        import math

        print("\n--- Placing Clinics with 'Perimeter Walk' Strategy (with Horizontal Mirroring) ---")

        # 1. SETUP: Load all clinic fixtures into a queue
        clinic_config = self.fixtures.get("clinic_fixtures", {})
        if not any(clinic_config.values()):
            print("INFO: No clinic fixtures specified.")
            return
        
        clinics_to_place = []
        for name, count in clinic_config.items():
            if count > 0:
                try:
                    fxtr = Fixture.Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"])
                    clinics_to_place.extend([fxtr] * count)
                except (KeyError, ValueError) as e:
                    print(f"WARNING: Clinic type '{name}' not found or invalid. Skipping. Error: {e}")
        
        if not clinics_to_place:
            return
            
        clinics_queue = collections.deque(clinics_to_place)
        
        # 2. Get the ordered perimeter path
        ordered_corners = self._get_reordered_corners_top_right_robust()
        perimeter_path = []
        for i in range(len(ordered_corners)):
            p1 = Vec2(ordered_corners[i])
            p2 = Vec2(ordered_corners[(i + 1) % len(ordered_corners)])
            if p1.distance(p2) > 100:
                perimeter_path.append((p1, p2))

        print(f"  -> Beginning perimeter walk with {len(clinics_queue)} clinics to place...")
        
        # 3. "Walk the Perimeter" and Place Fixtures
        for i, (segment_start, segment_end) in enumerate(perimeter_path):
            if not clinics_queue:
                break 

            segment_vector = (segment_end - segment_start).normalize()
            segment_length = segment_start.distance(segment_end)
            
            inward_normal = segment_vector.orthogonal()
            test_point = segment_start + inward_normal
            if not self.floorplan_polygon.contains(Point(test_point.x, test_point.y)):
                inward_normal = -inward_normal

            cursor = 50.0
            while clinics_queue:
                next_clinic = clinics_queue[0]
                fixture_depth = next_clinic.height
                fixture_length = next_clinic.width

                if cursor + fixture_length > segment_length - 50.0:
                    break

                margin_from_wall = 50.0
                center_on_wall = segment_start + segment_vector * (cursor + fixture_length / 2)
                center_offset = inward_normal * (margin_from_wall + fixture_depth / 2)
                target_center = center_on_wall + center_offset
                
                final_rotation = math.degrees(segment_vector.angle)

                # ###############################################################
                # ########## START OF HORIZONTAL MIRRORING LOGIC ##########
                # ###############################################################

                # --- Wall Type Detection ---
                mid_x = (segment_start.x + segment_end.x) / 2
                centroid_x = self.floorplan_polygon.centroid.x
                normalized_angle = abs(final_rotation) % 180
                is_vertical = (75 < normalized_angle < 105)

                wall_type = "other"
                if is_vertical and mid_x > centroid_x:
                    wall_type = "right"
                elif is_vertical and mid_x < centroid_x:
                    wall_type = "left"

                # --- Apply horizontal mirror for side walls ---
                xscale = 1.0
                if wall_type in ['left', 'right']:
                    xscale = -1.0

                # --- Perform validation and placement directly ---
                local_center = next_clinic.bounding_box.center
                transform = Matrix44.chain(
                    Matrix44.translate(-local_center.x, -local_center.y, 0),
                    Matrix44.scale(xscale, 1.0, 1.0), # Apply the scale
                    Matrix44.z_rotate(math.radians(final_rotation)),
                    Matrix44.translate(target_center.x, target_center.y, 0)
                )
                world_corners = list(transform.transform_vertices(next_clinic.bounding_box.rect_vertices()))
                fixture_polygon = Polygon([(p.x, p.y) for p in world_corners])
                aabb = BoundingBox2d(world_corners)

                is_inside = self.floorplan_polygon.buffer(-1.0).contains(fixture_polygon)
                is_overlapping = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                if is_inside and not is_overlapping:
                    # Calculate the insertion point using the correctly scaled local center
                    local_center_scaled = Vec2(local_center.x * xscale, local_center.y)
                    rotated_offset = local_center_scaled.rotate(math.radians(final_rotation))
                    final_insert_point = target_center - rotated_offset

                    # Use the main place_fixture function with the new scale
                    self.place_fixture(next_clinic,
                                       (final_insert_point.x, final_insert_point.y, 0),
                                       final_rotation,
                                       True,
                                       xscale=xscale, # Pass the xscale
                                       yscale=1.0) 

                    placed_bboxes.append((aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y))
                    print(f"    -> Placed '{next_clinic.name}' on '{wall_type}' wall (Horizontally Mirrored: {xscale < 0}).")
                    clinics_queue.popleft()
                    cursor += fixture_length + 100.0
                else:
                    cursor += 100.0

                # ###############################################################
                # ########### END OF HORIZONTAL MIRRORING LOGIC ###########
                # ###############################################################

        # --- 4. FINAL REPORT ---
        if not clinics_queue:
            print("\n✅ All clinic fixtures placed successfully.")
        else:
            print(f"\n⚠️ Could not place all clinics. {len(clinics_queue)} fixtures remain unplaced.")
            
    def place_clinics_perimeter_walk_v1(self, placed_bboxes):
        """
        Places clinics by walking the entire perimeter of the floorplan in a
        continuous, clockwise path, starting from the bottom-right corner.
        This is the most robust strategy for complex polygon shapes.
        """
        import collections

        print("\n--- Placing Clinics with 'Perimeter Walk' Strategy ---")

        # --- 1. SETUP: Load all clinic fixtures into a queue ---
        clinic_config = self.fixtures.get("clinic_fixtures", {})
        if not any(clinic_config.values()):
            print("INFO: No clinic fixtures specified.")
            return
        
        clinics_to_place = []
        for name, count in clinic_config.items():
            if count > 0:
                try:
                    fxtr = Fixture.Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"])
                    clinics_to_place.extend([fxtr] * count)
                except (KeyError, ValueError) as e:
                    print(f"WARNING: Clinic type '{name}' not found or invalid. Skipping. Error: {e}")
        
        if not clinics_to_place:
            return
            
        clinics_queue = collections.deque(clinics_to_place)
        
        # --- 2. Get the ordered perimeter path, starting from the bottom-right ---
        # This reorders the corner points to start at the bottom-right corner.
        # ordered_corners = self.cvc.reorder_bot_right()
        # This is the NEW line that calls the local helper

        # ordered_corners = self._get_reordered_corners_right_bottom()
        ordered_corners = self._get_reordered_corners_top_right_robust()

        # --- NEW: Reverse the list to ensure a clockwise path ---
        # ordered_corners.reverse()
                
        # Create a list of wall segments from the ordered corners.
        perimeter_path = []
        for i in range(len(ordered_corners)):
            p1 = Vec2(ordered_corners[i])
            p2 = Vec2(ordered_corners[(i + 1) % len(ordered_corners)]) # Loop back to the start
            if p1.distance(p2) > 100: # Ignore very small segments
                perimeter_path.append((p1, p2))

            print(f"  -> Beginning perimeter walk with {len(clinics_queue)} clinics to place...")
        
        # --- 3. "Walk the Perimeter" and Place Fixtures ---
        for i, (segment_start, segment_end) in enumerate(perimeter_path):
            if not clinics_queue:
                break # Stop if all clinics are placed

            print(f"  -> Analyzing Wall Segment #{i+1}...")
            
            segment_vector = (segment_end - segment_start).normalize()
            segment_length = segment_start.distance(segment_end)
            
            # Determine the inward normal for this specific segment
            inward_normal = segment_vector.orthogonal()
            test_point = segment_start + inward_normal
            if not self.floorplan_polygon.contains(Point(test_point.x, test_point.y)):
                inward_normal = -inward_normal

            # Place as many clinics as possible on this segment
            cursor = 50.0  # Start with a margin from the start of the segment
            while clinics_queue:
                next_clinic = clinics_queue[0]
                fixture_depth = next_clinic.height # Clinic's depth when placed against wall
                fixture_length = next_clinic.width  # Clinic's length along the wall

                if cursor + fixture_length > segment_length - 50.0:
                    break # Not enough space on this segment, move to the next

                margin_from_wall = 50.0
                
                # Calculate the center point for the fixture
                center_on_wall = segment_start + segment_vector * (cursor + fixture_length / 2)
                center_offset = inward_normal * (margin_from_wall + fixture_depth / 2)
                target_center = center_on_wall + center_offset

                # Rotation should be parallel to the wall segment
                final_rotation = math.degrees(segment_vector.angle)
                

                if self._validate_and_place_at_point(next_clinic, target_center, final_rotation, placed_bboxes):
                    print(f"    -> Placed '{next_clinic.name}' on segment #{i+1}.")
                    clinics_queue.popleft() # Success, remove from queue
                    cursor += fixture_length + 100.0 # Move cursor along for the next clinic
                else:
                    # Nudge the cursor to try the next spot on this same segment
                    cursor += 100.0 
        
        # --- 4. FINAL REPORT ---
        if not clinics_queue:
            print("\n✅ All clinic fixtures placed successfully.")
        else:
            print(f"\n⚠️ Could not place all clinics. {len(clinics_queue)} fixtures remain unplaced after walking the full perimeter.")

    
    def _validate_and_place_at_point(self, fixture, target_center, angle_deg, placed_bboxes):
        """
        A robust helper to validate if a fixture can be placed at a specific
        center point with a given rotation, and places it if valid.
        Returns True on success, False on failure.
        """
        from shapely.geometry import Polygon
        from ezdxf.math import Matrix44, Vec2, BoundingBox2d
        import math

        local_center = fixture.bounding_box.center
        transform = Matrix44.chain(
            Matrix44.translate(-local_center.x, -local_center.y, 0),
            Matrix44.z_rotate(math.radians(angle_deg)),
            Matrix44.translate(target_center.x, target_center.y, 0)
        )
        world_corners = list(transform.transform_vertices(fixture.bounding_box.rect_vertices()))
        fixture_polygon = Polygon([(p.x, p.y) for p in world_corners])
        aabb = BoundingBox2d(world_corners)

        # Perform validation checks
        is_inside = self.floorplan_polygon.buffer(-1.0).contains(fixture_polygon)
        is_overlapping = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

        if is_inside and not is_overlapping:
            # If valid, calculate the final insertion point and place the fixture
            rotated_offset = local_center.rotate(math.radians(angle_deg))
            final_insert_point = target_center - rotated_offset
            self.place_fixture(fixture, (final_insert_point.x, final_insert_point.y, 0), angle_deg, True)
            placed_bboxes.append((aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y))
            return True # Success
            
        return False # Failure
    


    def place_clinics_along_wall(self, placed_bboxes):
        """
        Places clinics using a direct, prioritized strategy.
        It prioritizes the right wall, placing a vertical stack of clinics starting
        from the bottom and moving up, and uses the left wall as a fallback.
        """
        import collections

        print("\n--- Placing Clinics with a Right-Wall-First Vertical Stack Strategy ---")

        # --- 1. SETUP: Load all clinic fixtures into a queue ---
        clinic_config = self.fixtures.get("clinic_fixtures", {})
        if not any(clinic_config.values()):
            print("INFO: No clinic fixtures specified.")
            return
        
        clinics_to_place = []
        for name, count in clinic_config.items():
            if count > 0:
                try:
                    fxtr = Fixture.Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"])
                    clinics_to_place.extend([fxtr] * count)
                except (KeyError, ValueError) as e:
                    print(f"WARNING: Clinic type '{name}' not found or invalid. Skipping. Error: {e}")
        
        if not clinics_to_place:
            return
            
        clinics_queue = collections.deque(clinics_to_place)
        
        # --- 2. Define priority and placement loop ---
        placement_priority = ['right', 'left']
        
        for side in placement_priority:
            if not clinics_queue:
                break # Stop if all clinics are placed

            print(f"\n  -> Attempting to place {len(clinics_queue)} clinics on the '{side}' wall...")
            
            # Get all wall segments for the current side
            wall_segments = self._get_side_wall_segments(side)
            if not wall_segments:
                print(f"    -> No segments found on '{side}' wall.")
                continue

            # Sort segments from bottom to top to ensure we start at the lowest point
            wall_segments.sort(key=lambda seg: min(seg[0][1], seg[1][1]))
            
            # --- 3. "Walk the Wall" Logic for the current side ---
            for p1_coords, p2_coords in wall_segments:
                if not clinics_queue:
                    break

                p1, p2 = Vec2(p1_coords), Vec2(p2_coords)
                # Ensure segment vector points upwards
                if p1.y > p2.y:
                    p1, p2 = p2, p1
                
                segment_vector = (p2 - p1).normalize()
                segment_length = p1.distance(p2)
                
                # Determine the inward normal for this specific segment
                inward_normal = segment_vector.orthogonal()
                test_point = p1 + inward_normal
                if not self.floorplan_polygon.contains(Point(test_point.x, test_point.y)):
                    inward_normal = -inward_normal

                # Try to place as many clinics as possible on this segment
                cursor = 50.0  # Start with a margin from the bottom of the segment
                while clinics_queue:
                    next_clinic = clinics_queue[0]
                    # For a vertical stack, the fixture's rotated depth is its height
                    fixture_depth = next_clinic.height 
                    # The length along the wall is its width
                    fixture_length = next_clinic.width

                    if cursor + fixture_length > segment_length - 50.0:
                        break # Not enough space on this segment, move to the next

                    margin_from_wall = 50.0
                    
                    # Calculate the center point for the fixture
                    center_on_wall = p1 + segment_vector * (cursor + fixture_length / 2)
                    center_offset = inward_normal * (margin_from_wall + fixture_depth / 2)
                    target_center = center_on_wall + center_offset

                    # Set final rotation: 270 degrees places it sideways with the "top" facing left
                    final_rotation = 270

                    if self._validate_and_place_at_point(next_clinic, target_center, final_rotation, placed_bboxes):
                        print(f"    -> Placed '{next_clinic.name}' on '{side}' wall.")
                        clinics_queue.popleft() # Success, remove from queue
                        cursor += fixture_length + 100.0 # Move cursor up for the next clinic
                    else:
                        print(f"    -> Spot for '{next_clinic.name}' on '{side}' wall was blocked.")
                        cursor += 100.0 # Nudge the cursor to try the next spot
        
        # --- 4. FINAL REPORT ---
        if not clinics_queue:
            print("\n✅ All clinic fixtures placed successfully.")
        else:
            print(f"\n⚠️ Could not place all clinics. {len(clinics_queue)} fixtures remain unplaced.")


#----------------------------------OLD FUNCTION-------------------------------------------------


    # def place_clinic_landscape(self, placed_bboxes):
    #     """
    #     Orchestrates the placement of clinic fixtures for landscape mode using a
    #     multi-strategy approach. It will first attempt to place fixtures on the
    #     right side and then place any remaining fixtures on the left side.
    #     """
    #     from Fixture import Fixture
    #     import collections

    #     print(f"\n--- Orchestrating Clinic Placement for Landscape ---")
    #     clinic_config = self.fixtures.get("clinic_fixtures", {})
    #     if not any(clinic_config.values()):
    #         print("INFO: No clinic fixtures specified.")
    #         return

    #     # 1. Load all clinic fixtures into a master list
    #     master_clinic_queue = []
    #     for clinic_type, count in clinic_config.items():
    #         if count > 0:
    #             try:
    #                 fxtr = Fixture(self.fixture_dict[clinic_type]["name"],
    #                                 self.fixture_dict[clinic_type]["path"])
    #                 master_clinic_queue.extend([fxtr] * count)
    #             except (KeyError, ValueError) as e:
    #                 print(f"WARNING: Clinic type '{clinic_type}' not found or invalid. Skipping. Error: {e}")

    #     if not master_clinic_queue:
    #         return

    #     # --- STRATEGY 1: Place on the RIGHT side ---
    #     print("\n  -> Strategy 1: Attempting to place clinics on the RIGHT side...")
    #     remaining_after_right = self._place_clinic_stack(master_clinic_queue, placed_bboxes, side='right')
        
    #     placed_on_right = len(master_clinic_queue) - len(remaining_after_right)
    #     print(f"  -> Placed {placed_on_right} fixtures on the right side.")

    #     # If all fixtures were placed, we are done.
    #     if not remaining_after_right:
    #         print("✅ All clinic fixtures placed successfully.")
    #         return

    #     # --- STRATEGY 2: Place any remaining fixtures on the LEFT side ---
    #     print(f"\n  -> Strategy 2: Attempting to place the remaining {len(remaining_after_right)} clinics on the LEFT side...")
    #     final_unplaced = self._place_clinic_stack(remaining_after_right, placed_bboxes, side='left')

    #     placed_on_left = len(remaining_after_right) - len(final_unplaced)
    #     print(f"  -> Placed {placed_on_left} fixtures on the left side.")

    #     # --- FINAL REPORT ---
    #     if final_unplaced:
    #         unplaced_summary = collections.Counter(f.name for f in final_unplaced)
    #         print(f"\n⚠️ CRITICAL FAILURE: Could not place all clinics after trying all strategies. {len(final_unplaced)} fixtures remain unplaced:")
    #         for name, num in unplaced_summary.items():
    #             print(f"    - {name}: {num}")

    # def _place_clinic_stack(self, clinics_to_place, placed_bboxes, side):
    #     """
    #     Helper function to place a stack of clinics on a specific side ('left' or 'right').
    #     It places fixtures one by one until space runs out and returns any unplaced fixtures.
    #     """
    #     from Fixture import Fixture
    #     from shapely.geometry import box, Point, LineString

    #     # 1. Define placement parameters
    #     margin = 150.0
    #     vertical_gap = 100.0
    #     search_increment = 100.0
        
    #     # This will hold the fixtures that cannot be placed in this attempt.
    #     unplaced_clinics = []

    #     # 2. Find the best available vertical lane for the stack
    #     max_fixture_width = max(fxtr.height for fxtr in clinics_to_place)
        
    #     if side == 'right':
    #         x_search_start = self.cvc.max_x - margin - max_fixture_width
    #         x_search_end = self.cvc.min_x
    #         x_direction = -1
    #     else: # 'left'
    #         x_search_start = self.cvc.min_x + margin
    #         x_search_end = self.cvc.max_x
    #         x_direction = 1

    #     best_x_pos = None
    #     current_x_try = x_search_start
        
    #     # Search for a clear lane that is not blocked by any existing obstacles
    #     while (x_direction * current_x_try) < (x_direction * x_search_end):
    #         lane = LineString([(current_x_try, self.cvc.min_y), (current_x_try, self.cvc.max_y)])
    #         if not any(lane.intersects(box(*b)) for b in placed_bboxes):
    #             best_x_pos = current_x_try
    #             print(f"    -> Found clear vertical lane for '{side}' side at X-coordinate: {best_x_pos:.0f}")
    #             break
    #         current_x_try += search_increment * x_direction
        
    #     if best_x_pos is None:
    #         print(f"    -> No clear vertical lane found on the '{side}' side.")
    #         return clinics_to_place # Return all clinics as unplaced if no lane is found

    #     # 3. Execute placement one-by-one in the found lane
    #     y_cursor = self.cvc.min_y + margin
    #     available_height = (self.cvc.max_y - self.cvc.min_y) - (2 * margin)

    #     for i, fxtr in enumerate(clinics_to_place):
    #         rotated_width = fxtr.height
    #         rotated_height = fxtr.width
            
    #         # Check if the NEXT fixture will fit vertically
    #         if y_cursor + rotated_height > self.cvc.min_y + margin + available_height:
    #             print(f"    -> Ran out of vertical space on '{side}' side.")
    #             unplaced_clinics = clinics_to_place[i:]
    #             break # Stop placing on this side

    #         x_pos = best_x_pos
    #         insert_point = (x_pos, y_cursor + rotated_height, 0)
            
    #         # We don't need to re-check for collisions here since we already found a clear lane
    #         self.place_fixture(fxtr, insert_point, 270, True)
    #         placed_bboxes.append((x_pos, y_cursor, x_pos + rotated_width, y_cursor + rotated_height))
    #         print(f"    -> Placed '{fxtr.name}' at ({x_pos:.0f}, {y_cursor:.0f})")
            
    #         y_cursor += rotated_height + vertical_gap

    #     return unplaced_clinics

#----------------------------------OLD FUNCTION-------------------------------------------------



    def place_qms_at_entrance(self, placed_bboxes):
        """
        Places QMS desks near the entrance (bottom-left) of the floorplan.
        It finds the bottom wall, calculates an inset position, and then searches
        for a clear spot to place the desks in a row.
        """
        from shapely.geometry import box
        import math

        # 1. Get configuration and load fixture
        config = self.fixtures.get("table_fixtures", {})
        qms_count = config.get("QMS_desk", 0)
        if qms_count <= 0:
            return

        print(f"\n--- Attempting to place {qms_count} QMS Desk(s) at the entrance ---")

        try:
            qms_fxtr = Fixture.Fixture("QMS_desk", self.fixture_dict["QMS_desk"]["path"])
        except Exception as e:
            print(f"🔥 Could not load QMS_desk fixture: {e}")
            return

        # 2. Find the bottom wall segment to anchor the placement
        wall_segments = self.cvc.get_wall_segments()
        bottom_segment = self.find_bottom_segment_y_coords(wall_segments)
        if not bottom_segment:
            print("⚠️ Could not find a bottom wall segment to anchor QMS desks. Aborting.")
            return

        p1, p2 = bottom_segment
        wall_vector = (p2[0] - p1[0], p2[1] - p1[1])
        wall_angle_rad = math.atan2(wall_vector[1], wall_vector[0])
        inward_normal = (-math.sin(wall_angle_rad), math.cos(wall_angle_rad))

        # 3. Calculate ideal starting position near the entrance (bottom-left)
        # Inset from the corner and from the wall to leave walking space
        inset_from_corner = 1200.0
        margin_from_wall = 200.0
        
        start_x = p1[0] + inset_from_corner
        start_y = p1[1] + margin_from_wall

        # 4. Helper function to find a valid spot by searching locally
        def find_valid_spot(start_x, start_y, fixture, max_search=2000, step=100):
            search_offset = 0
            while search_offset < max_search:
                # Search rightwards
                test_x = start_x + search_offset
                candidate_box = box(test_x, start_y, test_x + fixture.width, start_y + fixture.height)
                if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                    return (test_x, start_y)
                search_offset += step
            return None

        # 5. Place the desks in a horizontal row
        placed_count = 0
        current_x = start_x
        horizontal_gap = 400

        for i in range(qms_count):
            # Find a valid spot for the current desk, starting from the last known good position
            valid_spot = find_valid_spot(current_x, start_y, qms_fxtr)
            
            if valid_spot:
                x, y = valid_spot
                self.place_fixture(qms_fxtr, (x, y, 0), 0, False)
                bbox_coords = (x, y, x + qms_fxtr.width, y + qms_fxtr.height)
                placed_bboxes.append(bbox_coords)
                placed_count += 1
                print(f"✅ Placed QMS_desk #{i+1} near the entrance.")
                # Set the starting point for the next desk
                current_x = x + qms_fxtr.width + horizontal_gap
            else:
                print(f"⚠️ Could not find a clear spot for QMS_desk #{i+1} near the entrance. Stopping placement.")
                break
                
        print(f"-> Finished QMS Desk Placement: Placed {placed_count} of {qms_count} requested desks.")

    
    def place_corian_table_set_landscape(self, placed_bboxes):
        """
        Main dispatcher for placing Corian Table sets. It checks if the number of
        sets is odd or even and calls the appropriate specialized placement strategy.
        """
        from Fixture import Fixture
        
        print("\n--- Initializing Corian Table Set Placement ---")

        # 1. SETUP
        try:
            config = self.fixtures.get("Corian_table_set", {})
            num_sets = config.get("Corian_table", 0)
            if num_sets <= 0:
                print("  -> Placement skipped: No Corian_table specified.")
                return

            table_fxtr = Fixture("Corian_table", self.fixture_dict["Corian_table"]["path"])
            seat_fxtr = Fixture("Lounge_seat", self.fixture_dict["Lounge_seat"]["path"])
        except Exception as e:
            print(f"🔥 Error during Corian_table_set setup: {e}")
            return

        # 2. DISPATCH TO THE CORRECT STRATEGY
        if num_sets % 2 != 0:
            print(f"  -> Detected ODD count ({num_sets}). Using Euro Centre 'Center-Out' strategy.")
            self._place_sets_center_out(num_sets, table_fxtr, seat_fxtr, placed_bboxes)
        else:
            print(f"  -> Detected EVEN count ({num_sets}). Using Discussion Table 'Top-Bottom' strategy.")
            self._place_sets_discussion_anchored(num_sets, table_fxtr, seat_fxtr, placed_bboxes)


    def _place_sets_center_out(self, num_sets, table_fxtr, seat_fxtr, placed_bboxes):
        """
        Handles placement for an ODD number of sets by anchoring to Euro Centres
        and stacking from the vertical center outwards, respecting the walking corridor.
        """
        from ezdxf.bbox import extents
        from shapely.geometry import box

        # (This is the confirmed-working "old strategy" for odd counts)
        gap_table_to_seat = 100.0
        gap_between_seats = 50.0
        set_width_portrait = max(table_fxtr.width, (seat_fxtr.width * 2) + gap_between_seats)
        set_height_portrait = (seat_fxtr.height * 2) + table_fxtr.height + (gap_table_to_seat * 2)
        set_width_rotated = set_height_portrait
        set_height_rotated = set_width_portrait
        
        euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
        if not euro_entities:
            print("⚠️ Cannot place Corian sets: Euro Centre anchor fixtures not found.")
            return
        euro_cluster_bbox = extents(euro_entities)
        
        room_height = self.cvc.max_y - self.cvc.min_y
        y_zone_start = self.cvc.min_y + (room_height * 0.20)
        y_zone_end = self.cvc.max_y - (room_height * 0.20)
        y_zone_center = (y_zone_start + y_zone_end) / 2
        
        def is_valid_spot(x, y, width, height):
            candidate_box = box(x, y, x + width, y + height)
            is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
            is_inside_zone = (y >= y_zone_start and (y + height) <= y_zone_end)
            return self.floorplan_polygon.contains(candidate_box) and not is_overlapping and is_inside_zone

        sets_to_place_queue = list(range(num_sets))
        gap_from_euros = 5
        vertical_gap = 800.0
        current_col_x = euro_cluster_bbox.extmax.x + gap_from_euros
        col_num = 1

        while sets_to_place_queue:
            ideal_y = y_zone_center - (set_height_rotated / 2)
            if is_valid_spot(current_col_x, ideal_y, set_width_rotated, set_height_rotated):
                self._place_single_set_rotated(current_col_x, ideal_y, table_fxtr, seat_fxtr)
                placed_bboxes.append((current_col_x, ideal_y, current_col_x + set_width_rotated, ideal_y + set_height_rotated))
                sets_to_place_queue.pop(0)
                y_cursor_up = ideal_y + set_height_rotated + vertical_gap
                y_cursor_down = ideal_y - set_height_rotated - vertical_gap
                while sets_to_place_queue:
                    target_y = y_cursor_up if len(sets_to_place_queue) % 2 != 0 else y_cursor_down
                    if is_valid_spot(current_col_x, target_y, set_width_rotated, set_height_rotated):
                        self._place_single_set_rotated(current_col_x, target_y, table_fxtr, seat_fxtr)
                        placed_bboxes.append((current_col_x, target_y, current_col_x + set_width_rotated, target_y + set_height_rotated))
                        sets_to_place_queue.pop(0)
                        if len(sets_to_place_queue) % 2 == 0:
                            y_cursor_up = target_y + set_height_rotated + vertical_gap
                        else:
                            y_cursor_down = target_y - set_height_rotated - vertical_gap
                    else: break
            
            current_col_x += set_width_rotated + gap_from_euros
            col_num += 1
            if current_col_x + set_width_rotated > self.cvc.max_x - 200: break

        if sets_to_place_queue:
            left_col_x = euro_cluster_bbox.extmin.x - gap_from_euros - set_width_rotated
            ideal_y_left = y_zone_center - (set_height_rotated / 2)
            if is_valid_spot(left_col_x, ideal_y_left, set_width_rotated, set_height_rotated):
                self._place_single_set_rotated(left_col_x, ideal_y_left, table_fxtr, seat_fxtr)
                placed_bboxes.append((left_col_x, ideal_y_left, left_col_x + set_width_rotated, ideal_y_left + set_height_rotated))
                sets_to_place_queue.pop(0)
                y_cursor_up_left = ideal_y_left + set_height_rotated + vertical_gap
                y_cursor_down_left = ideal_y_left - set_height_rotated - vertical_gap
                while sets_to_place_queue:
                    target_y = y_cursor_up_left if len(sets_to_place_queue) % 2 != 0 else y_cursor_down_left
                    if is_valid_spot(left_col_x, target_y, set_width_rotated, set_height_rotated):
                        self._place_single_set_rotated(left_col_x, target_y, table_fxtr, seat_fxtr)
                        placed_bboxes.append((left_col_x, target_y, left_col_x + set_width_rotated, target_y + set_height_rotated))
                        sets_to_place_queue.pop(0)
                        if len(sets_to_place_queue) % 2 == 0:
                            y_cursor_up_left = target_y + set_height_rotated + vertical_gap
                        else:
                            y_cursor_down_left = target_y - set_height_rotated - vertical_gap
                    else: break
        
        total_placed = num_sets - len(sets_to_place_queue)
        print(f"\n-> Finished Corian Set Placement: Placed {total_placed} of {num_sets} requested sets.")


    def _place_sets_discussion_anchored(self, num_sets, table_fxtr, seat_fxtr, placed_bboxes):
        """
        Handles placement for an EVEN number of sets by anchoring to Discussion Tables,
        respecting the central walking corridor.
        """
        from ezdxf.bbox import extents
        from shapely.geometry import box

        # 1. FIND DISCUSSION TABLE ANCHORS
        discussion_tables = [e for e in self.msp.query('INSERT') if "DISCUSSION_TABLE" in e.dxf.name.upper()]
        if not discussion_tables:
            print("⚠️ Cannot place Corian sets: Discussion Table anchors not found for even-count strategy.")
            return
        
        discussion_tables.sort(key=lambda e: e.dxf.insert.y)
        bottom_table_bbox = extents([discussion_tables[0]])
        top_table_bbox = extents([discussion_tables[-1]])

        # 2. CALCULATE SET DIMENSIONS & PARAMETERS
        set_width_rotated = 1573.0
        set_height_rotated = 1200.0
        gap_from_tables = 800.0
        vertical_gap = 800.0
        
        # 3. ***NEW***: DEFINE WALKING CORRIDOR AND VALIDATION
        room_height = self.cvc.max_y - self.cvc.min_y
        y_zone_start = self.cvc.min_y + (room_height * 0.20)
        y_zone_end = self.cvc.max_y - (room_height * 0.20)
        
        def is_valid_spot(x, y, width, height):
            candidate_box = box(x, y, x + width, y + height)
            is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
            # ***NEW***: Check if the placement is within the vertical walking zone
            is_inside_zone = (y >= y_zone_start and (y + height) <= y_zone_end)
            return self.floorplan_polygon.contains(candidate_box) and not is_overlapping and is_inside_zone

        # 4. MULTI-COLUMN PLACEMENT LOGIC
        sets_to_place_queue = list(range(num_sets))
        current_col_x = max(top_table_bbox.extmax.x, bottom_table_bbox.extmax.x) + gap_from_tables
        col_num = 1

        while sets_to_place_queue:
            y_cursor_down = bottom_table_bbox.center.y - (set_height_rotated / 2)
            y_cursor_up = top_table_bbox.center.y - (set_height_rotated / 2)
            placed_in_col = 0
            
            while sets_to_place_queue:
                target_y = y_cursor_down if len(sets_to_place_queue) % 2 == 0 else y_cursor_up
                if is_valid_spot(current_col_x, target_y, set_width_rotated, set_height_rotated):
                    self._place_single_set_rotated(current_col_x, target_y, table_fxtr, seat_fxtr)
                    placed_bboxes.append((current_col_x, target_y, current_col_x + set_width_rotated, target_y + set_height_rotated))
                    sets_to_place_queue.pop(0)
                    placed_in_col += 1
                    if len(sets_to_place_queue) % 2 != 0:
                         y_cursor_down -= (set_height_rotated + vertical_gap)
                    else:
                         y_cursor_up += (set_height_rotated + vertical_gap)
                else:
                    break
            
            if placed_in_col == 0 and sets_to_place_queue:
                 print(f"  -> Could not place any sets in Column #{col_num}. Trying next column.")

            current_col_x += set_width_rotated + gap_from_tables
            col_num += 1
            if current_col_x + set_width_rotated > self.cvc.max_x - 200:
                break

        # 5. FALLBACK TO LEFT SIDE (also respects walking zone)
        if sets_to_place_queue:
            print(f"\n  -> Fallback: Placing remaining {len(sets_to_place_queue)} sets on the Left Side...")
            left_col_x = min(top_table_bbox.extmin.x, bottom_table_bbox.extmin.x) - gap_from_tables - set_width_rotated
            
            # Start the fallback with the same top/bottom anchor logic
            y_cursor_down_fallback = bottom_table_bbox.center.y - (set_height_rotated / 2)
            y_cursor_up_fallback = top_table_bbox.center.y - (set_height_rotated / 2)

            while sets_to_place_queue:
                target_y = y_cursor_down_fallback if len(sets_to_place_queue) % 2 == 0 else y_cursor_up_fallback
                if is_valid_spot(left_col_x, target_y, set_width_rotated, set_height_rotated):
                    self._place_single_set_rotated(left_col_x, target_y, table_fxtr, seat_fxtr)
                    placed_bboxes.append((left_col_x, target_y, left_col_x + set_width_rotated, target_y + set_height_rotated))
                    sets_to_place_queue.pop(0)
                    if len(sets_to_place_queue) % 2 != 0:
                        y_cursor_down_fallback -= (set_height_rotated + vertical_gap)
                    else:
                        y_cursor_up_fallback += (set_height_rotated + vertical_gap)
                else:
                    print("  -> Left fallback column is full or blocked.")
                    break
        
        total_placed = num_sets - len(sets_to_place_queue)
        print(f"\n-> Finished Corian Set Placement: Placed {total_placed} of {num_sets} requested sets.")


    def _place_single_set_rotated(self, set_x, set_y, table_fxtr, seat_fxtr):
        """
        Helper function to place the 5 components of a Corian set with a
        90-degree rotation within a given bounding box (set_x, set_y).
        """
        # Define gaps within the set
        gap_table_to_seat = 100.0
        gap_between_seats = 50.0

        # Calculate the dimensions of the original portrait set to find its center
        set_width_portrait = max(table_fxtr.width, (seat_fxtr.width * 2) + gap_between_seats)
        set_height_portrait = (seat_fxtr.height * 2) + table_fxtr.height + (gap_table_to_seat * 2)

        # The bounding box of our rotated set in the world
        rotated_w = set_height_portrait
        rotated_h = set_width_portrait
        
        # The center of this bounding box is our main anchor
        center_x = set_x + rotated_w / 2
        center_y = set_y + rotated_h / 2

        # --- Place Table (rotated 90 degrees) ---
        # Its center should align with the set's center
        table_insert_x = center_x - table_fxtr.height / 2
        table_insert_y = center_y - table_fxtr.width / 2
        self.place_fixture(table_fxtr, (table_insert_x, table_insert_y, 0), 90, True)

        # --- Place Left Seats (rotated 270 degrees) ---
        # These are positioned to the left of the table
        left_seat_center_x = center_x - (table_fxtr.height / 2) - gap_table_to_seat - (seat_fxtr.height / 2)
        
        # Top-left seat
        left_seat1_center_y = center_y + (gap_between_seats / 2) + (seat_fxtr.width / 2)
        seat1_insert_x = left_seat_center_x - seat_fxtr.height / 2 - seat_fxtr.height
        seat1_insert_y = left_seat1_center_y + seat_fxtr.width / 2 # Adjust for 270 rot
        self.place_fixture(seat_fxtr, (seat1_insert_x, seat1_insert_y, 0), 270, True)

        # Bottom-left seat
        left_seat2_center_y = center_y - (gap_between_seats / 2) - (seat_fxtr.width / 2)
        seat2_insert_x = left_seat_center_x - seat_fxtr.height / 2 - seat_fxtr.height
        seat2_insert_y = left_seat2_center_y + seat_fxtr.width / 2 # Adjust for 270 rot
        self.place_fixture(seat_fxtr, (seat2_insert_x, seat2_insert_y, 0), 270, True)

        # --- Place Right Seats (rotated 90 degrees) ---
        # These are positioned to the right of the table
        right_seat_center_x = center_x + (table_fxtr.height / 2) + gap_table_to_seat + (seat_fxtr.height / 2)

        # Top-right seat
        right_seat1_center_y = left_seat1_center_y # Same Y as top-left
        seat3_insert_x = right_seat_center_x - seat_fxtr.height / 2
        seat3_insert_y = right_seat1_center_y - seat_fxtr.width / 2
        self.place_fixture(seat_fxtr, (seat3_insert_x, seat3_insert_y, 0), 90, True)

        # Bottom-right seat
        right_seat2_center_y = left_seat2_center_y # Same Y as bottom-left
        seat4_insert_x = right_seat_center_x - seat_fxtr.height / 2
        seat4_insert_y = right_seat2_center_y - seat_fxtr.width / 2
        self.place_fixture(seat_fxtr, (seat4_insert_x, seat4_insert_y, 0), 90, True)


    def place_standing_tables_landscape(self, placed_bboxes):
        """
        Main dispatcher for placing Standing Tables. It intelligently determines the
        anchor point, creates multiple columns as needed, and then calls the
        appropriate odd/even count placement strategy for each column.
        """
        from Fixture import Fixture
        from ezdxf.bbox import extents
        
        print("\n--- Initializing Standing Table Placement with Multi-Column Logic ---")

        # 1. SETUP
        try:
            config = self.fixtures.get("table_fixtures", {})
            num_tables = config.get("Standing_table", 0)
            if num_tables <= 0:
                print("  -> Placement skipped: No Standing_table specified.")
                return
            standing_fxtr = Fixture("Standing_table", self.fixture_dict["Standing_table"]["path"])
        except Exception as e:
            print(f"🔥 Error during Standing_table setup: {e}")
            return

        # 2. DETERMINE ANCHOR
        anchor_bbox = None
        corian_entities = [e for e in self.msp.query('INSERT') if "CORIAN_TABLE" in e.dxf.name.upper() or "LOUNGE_SEAT" in e.dxf.name.upper()]

        if corian_entities:
            print("  -> Condition Met: Corian sets found. Anchoring to them.")
            anchor_bbox = extents(corian_entities)
        else:
            print("  -> Condition Met: No Corian sets found. Anchoring to Euro Centres.")
            euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
            if not euro_entities:
                print("⚠️ Cannot place Standing Tables: No primary anchors found. Aborting.")
                return
            anchor_bbox = extents(euro_entities)

        # 3. MULTI-COLUMN PLACEMENT
        gap = 800.0
        tables_to_place_queue = list(range(num_tables))
        
        # --- Phase 1: Fill columns on the RIGHT side ---
        current_col_x = anchor_bbox.extmax.x + gap
        while tables_to_place_queue:
            print(f"\n  -> Attempting to place {len(tables_to_place_queue)} tables in column at x={current_col_x:.0f}")
            
            if len(tables_to_place_queue) % 2 != 0:
                remaining_after_col = self._place_standing_tables_center_out(
                    tables_to_place_queue, standing_fxtr, placed_bboxes, current_col_x)
            else:
                remaining_after_col = self._place_standing_tables_discussion_anchored(
                    tables_to_place_queue, standing_fxtr, placed_bboxes, current_col_x)
            
            if remaining_after_col and len(remaining_after_col) == len(tables_to_place_queue):
                print(f"  -> Column at x={current_col_x:.0f} is full or blocked.")
                current_col_x += standing_fxtr.width + gap
                if current_col_x + standing_fxtr.width > self.cvc.max_x - 200:
                    print("  -> No more space for new columns on the right.")
                    break 
            
            tables_to_place_queue = remaining_after_col

        # --- Phase 2: Fallback to the LEFT side ---
        if tables_to_place_queue:
            print(f"\n  -> Fallback: Placing remaining {len(tables_to_place_queue)} tables on the Left Side...")
            left_col_x = anchor_bbox.extmin.x - gap - standing_fxtr.width
            
            # ***FIX***: ALWAYS use the most robust "center-out" strategy for the fallback,
            # as it does not depend on anchors in other parts of the room.
            tables_to_place_queue = self._place_standing_tables_center_out(
                tables_to_place_queue, standing_fxtr, placed_bboxes, left_col_x)

        total_placed = num_tables - len(tables_to_place_queue)
        print(f"\n-> Finished Standing Table Placement: Placed {total_placed} of {num_tables} requested tables.")


    def _place_standing_tables_center_out(self, tables_to_place, standing_fxtr, placed_bboxes, start_x):
        """
        Fills a SINGLE column with tables, stacking center-out.
        Returns any tables that could not be placed.
        """
        from shapely.geometry import box

        room_height = self.cvc.max_y - self.cvc.min_y
        y_zone_start = self.cvc.min_y + (room_height * 0.20)
        y_zone_end = self.cvc.max_y - (room_height * 0.20)
        y_zone_center = (y_zone_start + y_zone_end) / 2
        
        def is_valid_spot(x, y, fixture):
            candidate_box = box(x, y, x + fixture.width, y + fixture.height)
            is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
            is_inside_zone = (y >= y_zone_start and (y + fixture.height) <= y_zone_end)
            return self.floorplan_polygon.contains(candidate_box) and not is_overlapping and is_inside_zone

        remaining_queue = list(tables_to_place)
        vertical_gap = 400.0
        
        ideal_y = y_zone_center - (standing_fxtr.height / 2)
        if is_valid_spot(start_x, ideal_y, standing_fxtr):
            self.place_fixture(standing_fxtr, (start_x, ideal_y, 0), 0, False)
            placed_bboxes.append((start_x, ideal_y, start_x + standing_fxtr.width, ideal_y + standing_fxtr.height))
            remaining_queue.pop(0)

            y_cursor_up = ideal_y + standing_fxtr.height + vertical_gap
            y_cursor_down = ideal_y - standing_fxtr.height - vertical_gap
            
            while remaining_queue:
                if (len(tables_to_place) - len(remaining_queue)) % 2 != 0:
                     target_y = y_cursor_up
                else:
                     target_y = y_cursor_down

                if is_valid_spot(start_x, target_y, standing_fxtr):
                    self.place_fixture(standing_fxtr, (start_x, target_y, 0), 0, False)
                    placed_bboxes.append((start_x, target_y, start_x + standing_fxtr.width, target_y + standing_fxtr.height))
                    remaining_queue.pop(0)
                    if (len(tables_to_place) - len(remaining_queue)) % 2 == 0:
                        y_cursor_up = target_y + standing_fxtr.height + vertical_gap
                    else:
                        y_cursor_down = target_y - standing_fxtr.height - vertical_gap
                else:
                    break
        return remaining_queue

    def _place_standing_tables_discussion_anchored(self, tables_to_place, standing_fxtr, placed_bboxes, start_x):
        """
        Fills a SINGLE column with an EVEN number of tables, using top/bottom anchors.
        If anchors are not found, it defaults to the center-out strategy.
        Returns any tables that could not be placed.
        """
        from ezdxf.bbox import extents
        from shapely.geometry import box

        discussion_tables = [e for e in self.msp.query('INSERT') if "DISCUSSION_TABLE" in e.dxf.name.upper()]
        
        if not discussion_tables:
            print("  -> No Discussion Tables found for anchoring. Switching to 'center-out' fallback for this column.")
            return self._place_standing_tables_center_out(tables_to_place, standing_fxtr, placed_bboxes, start_x)
        
        discussion_tables.sort(key=lambda e: e.dxf.insert.y)
        bottom_table_bbox = extents([discussion_tables[0]])
        top_table_bbox = extents([discussion_tables[-1]])

        vertical_gap = 400.0
        room_height = self.cvc.max_y - self.cvc.min_y
        y_zone_start = self.cvc.min_y + (room_height * 0.20)
        y_zone_end = self.cvc.max_y - (room_height * 0.20)
        
        def is_valid_spot(x, y, fixture):
            candidate_box = box(x, y, x + fixture.width, y + fixture.height)
            is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
            is_inside_zone = (y >= y_zone_start and (y + fixture.height) <= y_zone_end)
            return self.floorplan_polygon.contains(candidate_box) and not is_overlapping and is_inside_zone

        remaining_queue = list(tables_to_place)
        y_cursor_down = bottom_table_bbox.center.y - (standing_fxtr.height / 2)
        y_cursor_up = top_table_bbox.center.y - (standing_fxtr.height / 2)
        
        while remaining_queue:
            if len(remaining_queue) % 2 == 0:
                target_y = y_cursor_down
            else:
                target_y = y_cursor_up
                
            if is_valid_spot(start_x, target_y, standing_fxtr):
                self.place_fixture(standing_fxtr, (start_x, target_y, 0), 0, False)
                placed_bboxes.append((start_x, target_y, start_x + standing_fxtr.width, target_y + standing_fxtr.height))
                remaining_queue.pop(0)

                if (len(tables_to_place) - len(remaining_queue)) % 2 != 0:
                     y_cursor_down -= (standing_fxtr.height + vertical_gap)
                else:
                     y_cursor_up += (standing_fxtr.height + vertical_gap)
            else:
                break
        return remaining_queue
    

    def place_eye_massage_area_landscape(self, placed_bboxes):
        """
        Places Eye Massage Area fixtures in a vertical stack.
        - Primary Strategy: Anchors the stack to the left of the bottom-most clinic.
        - Fallback Strategy: If the primary spot is blocked, it finds the first
          available clear vertical lane on the right side of the room and places
          the stack there.
        """
        from Fixture import Fixture
        from ezdxf.bbox import extents
        from shapely.geometry import box, LineString

        print("\n--- Attempting to place Eye Massage Area (Landscape with Stacking) ---")

        # 1. SETUP
        try:
            config = self.fixtures.get("Eye_massage_area", {})
            fixture_count = config.get("Eye_massage_area", 0)
            if fixture_count <= 0:
                print("  -> Placement skipped: No Eye_massage_area specified.")
                return
            fixture_obj = Fixture("Eye_massage_area", self.fixture_dict["Eye_massage_area"]["path"])
        except Exception as e:
            print(f"🔥 Error during Eye_massage_area setup: {e}")
            return

        # 2. FIND CLINIC ANCHOR
        clinic_entities = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
        if not clinic_entities:
            print("⚠️ Cannot place Eye Massage Area: No Clinic fixtures found to anchor to.")
            return
            
        bottom_clinic = min(clinic_entities, key=lambda e: e.dxf.insert.y)
        anchor_bbox = extents([bottom_clinic])
        
        # 3. HELPER AND PARAMETERS
        gap = 1000.0  # 1-meter gap for customer access
        vertical_gap = 150.0 # Gap between stacked units

        def is_valid_spot(x, y, fxtr):
            candidate_box = box(x, y, x + fxtr.width, y + fxtr.height)
            is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
            is_inside = self.floorplan_polygon.contains(candidate_box)
            return is_inside and not is_overlapping

        # 4. PLACEMENT LOGIC
        placed_count = 0
        
        # --- Strategy 1 (Primary): Create a stack to the left of the bottom clinic ---
        print("  -> Attempting Strategy 1: Place stack left of bottom clinic...")
        
        ideal_x = anchor_bbox.extmin.x - gap - fixture_obj.width
        y_cursor = anchor_bbox.extmin.y 

        for i in range(fixture_count):
            if is_valid_spot(ideal_x, y_cursor, fixture_obj):
                self.place_fixture(fixture_obj, (ideal_x, y_cursor, 0), 0, False)
                placed_bboxes.append((ideal_x, y_cursor, ideal_x + fixture_obj.width, y_cursor + fixture_obj.height))
                placed_count += 1
                print(f"    ✅ SUCCESS: Placed Eye_massage_area #{i+1} via Strategy 1.")
                # Move the cursor up for the next placement in the stack
                y_cursor += fixture_obj.height + vertical_gap
            else:
                # If even one spot in the stack is blocked, we abandon this strategy
                print("    -> FAILED: Primary stack position is blocked. Moving to fallback.")
                # We need to remove any partially placed fixtures from this failed attempt
                # For simplicity in this context, we assume if the first fails, the rest will.
                # A more complex implementation could remove the bboxes if needed.
                break
        
        # If all were placed, we're done.
        if placed_count == fixture_count:
            print(f"\n-> Finished Eye Massage Area Placement: Placed {placed_count} of {fixture_count} requested fixtures.")
            return

        # --- Strategy 2 (Fallback): Find a clear lane on the right side ---
        remaining_count = fixture_count - placed_count
        print(f"  -> Attempting Fallback: Find clear lane for remaining {remaining_count} fixtures...")

        # Find a clear vertical lane, searching from right to left
        best_x_pos = None
        search_x = self.cvc.max_x - 200 - fixture_obj.width
        while search_x > self.floorplan_polygon.centroid.x:
            lane = LineString([(search_x, self.cvc.min_y), (search_x, self.cvc.max_y)])
            if not any(lane.intersects(box(*b)) for b in placed_bboxes):
                best_x_pos = search_x
                break
            search_x -= 100

        if best_x_pos:
            print(f"    -> Found clear fallback lane at x={best_x_pos:.0f}")
            y_cursor = self.cvc.min_y + 200 # Start near the bottom wall
            for i in range(remaining_count):
                if is_valid_spot(best_x_pos, y_cursor, fixture_obj):
                    self.place_fixture(fixture_obj, (best_x_pos, y_cursor, 0), 0, False)
                    placed_bboxes.append((best_x_pos, y_cursor, best_x_pos + fixture_obj.width, y_cursor + fixture_obj.height))
                    placed_count += 1
                    print(f"    ✅ SUCCESS: Placed Eye_massage_area #{placed_count} via Fallback.")
                    y_cursor += fixture_obj.height + vertical_gap
                else:
                    print(f"    -> FAILED: Fallback lane is now full or blocked.")
                    break
        else:
            print("    -> FAILED: Could not find any clear vertical lane for fallback placement.")

        print(f"\n-> Finished Eye Massage Area Placement: Placed {placed_count} of {fixture_count} requested fixtures.")

    def place_blue_zero_landscape(self, placed_bboxes):
        """
        Places Blue_zero fixtures in landscape mode using a two-phase "snaking"
        pattern. It first exhausts all Discussion Table spots from left to right,
        then places any remaining fixtures next to Euro Centres.
        """
        from Fixture import Fixture
        from ezdxf.bbox import extents
        from shapely.geometry import box
        import collections

        # 1. Get configuration
        config = self.fixtures.get("discussion_table_attached", {})
        blue_zero_count = config.get("Blue_zero", 0)
        if blue_zero_count <= 0:
            return

        print("\n--- Attempting to place Blue_zero fixtures (Landscape Snaking Strategy) ---")

        try:
            blue_zero_fxtr = Fixture("Blue_zero", self.fixture_dict["Blue_zero"]["path"])
        except Exception as e:
            print(f"🔥 Could not load the Blue_zero fixture file: {e}")
            return

        # --- HELPER FUNCTION to perform the placement for a given set of targets ---
        # *** FIX: Added 'current_placed_count' as a parameter ***
        def place_on_targets(targets, num_to_place, current_placed_count):
            """Groups targets into columns and places fixtures in a snaking pattern."""
            if not targets:
                return 0

            columns = collections.defaultdict(list)
            for target in targets:
                columns[round(target.dxf.insert.x / 100)].append(target)

            sorted_column_keys = sorted(columns.keys())

            ordered_targets = []
            for key in sorted_column_keys:
                sorted_tables_in_column = sorted(columns[key], key=lambda e: e.dxf.insert.y)
                ordered_targets.extend(sorted_tables_in_column)

            placed_this_run = 0
            gap = 10.0

            for i in range(num_to_place):
                if i >= len(ordered_targets):
                    break
                
                anchor_entity = ordered_targets[i]
                anchor_bbox = extents([anchor_entity])
                
                rotation = 270
                rotated_width = blue_zero_fxtr.height
                rotated_height = blue_zero_fxtr.width
                
                insert_x = anchor_bbox.extmin.x - rotated_width - gap
                insert_y = anchor_bbox.center.y - (rotated_height / 2)
                final_insert_point = (insert_x, insert_y + rotated_height, 0)

                candidate_box = box(insert_x, insert_y, insert_x + rotated_width, insert_y + rotated_height)
                is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
                is_inside = self.floorplan_polygon.contains(candidate_box)

                if is_inside and not is_overlapping:
                    self.place_fixture(blue_zero_fxtr, final_insert_point, rotation, True)
                    placed_bboxes.append((insert_x, insert_y, insert_x + rotated_width, insert_y + rotated_height))
                    # *** FIX: Use the passed-in parameter for the print statement ***
                    print(f"    ✅ Placed Blue_zero #{current_placed_count + placed_this_run + 1} to the left of a {anchor_entity.dxf.name.split('_')[0]} fixture.")
                    placed_this_run += 1
                else:
                    print(f"    ⚠️ Spot for Blue_zero #{current_placed_count + placed_this_run + 1} was blocked or outside.")
            
            return placed_this_run

        # --- PHASE 1: Place on Discussion Tables ---
        print("  -> Phase 1: Placing on Discussion Tables...")
        discussion_tables = [e for e in self.msp.query('INSERT') if "DISCUSSION_TABLE" in e.dxf.name.upper()]
        placed_count = 0
        # *** FIX: Pass the current 'placed_count' to the helper function ***
        placed_count = place_on_targets(discussion_tables, blue_zero_count, placed_count)

        # --- PHASE 2: Place any remaining on Euro Centres ---
        remaining_to_place = blue_zero_count - placed_count
        if remaining_to_place > 0:
            print(f"\n  -> Phase 2: Placing remaining {remaining_to_place} on Euro Centres...")
            euro_centres = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
            # *** FIX: Pass the current 'placed_count' to the helper function ***
            placed_on_euros = place_on_targets(euro_centres, remaining_to_place, placed_count)
            placed_count += placed_on_euros

        if placed_count < blue_zero_count:
            print(f"⚠️ Warning: Placed only {placed_count} of {blue_zero_count} requested fixtures.")


    def place_sofas_dynamically_landscape(self, placed_bboxes):
        """
        Places sofa fixtures with a fully dynamic and intelligent strategy.
        - Vertical position is calculated by finding the midpoint of the available
          space between the central fixtures and the nearest wall.
        - Horizontal position is a perfectly centered row, found using a resilient
          search that slides left and right to find clear space.
        - Automatically falls back to placing below if the top area is unavailable.
        - Places sofas as a group and carries over unplaced ones to the next phase.
        """
        from Fixture import Fixture
        from ezdxf.bbox import extents
        from shapely.geometry import box
        import collections

        print("\n--- Attempting to place Sofas with a RESILIENT ROW-BY-ROW Dynamic Strategy ---")

        # 1. SETUP: Load all specified sofa fixtures
        sofa_config = self.fixtures.get("loose_furniture", {})
        initial_sofas_to_place = []
        for name, count in sofa_config.items():
            if "sofa" in name.lower() and count > 0:
                try:
                    fxtr = Fixture(name, self.fixture_dict[name]["path"])
                    initial_sofas_to_place.extend([fxtr] * count)
                except (KeyError, ValueError) as e:
                    print(f"⚠️ Warning: Sofa fixture '{name}' could not be loaded: {e}")

        if not initial_sofas_to_place:
            print("ℹ️ No sofa fixtures specified for placement.")
            return

        # 2. INTELLIGENT ANCHOR SELECTION (Lensbar > Euro Centre)
        anchor_entities = [e for e in self.msp.query('INSERT') if "LENSBAR" in e.dxf.name.upper()]
        anchor_type = "Lensbar"
        if not anchor_entities:
            anchor_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
            anchor_type = "Euro Centre"

        if not anchor_entities:
            print("⚠️ Cannot place sofas: No suitable anchor fixtures found.")
            return

        anchor_cluster_bbox = extents(anchor_entities)
        print(f"  -> Anchoring placement relative to '{anchor_type}' cluster.")

        # 3. HELPER for validation
        def is_valid_spot(x, y, fixture):
            candidate_box = box(x, y, x + fixture.width, y + fixture.height)
            is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
            is_inside = self.floorplan_polygon.contains(candidate_box)
            return is_inside and not is_overlapping

        # 4. NEW: HELPER FUNCTION TO PLACE A ROW AND RETURN UNPLACED
        def place_sofa_row(sofas_to_place_list, ideal_y, total_group_width):
            """
            Attempts to place a row of sofas using a resilient search and
            returns any that couldn't be placed.
            """
            ideal_x = anchor_cluster_bbox.center.x - (total_group_width / 2)
            
            # --- NEW: Resilient Search Logic ---
            found_spot = None
            search_offset = 0
            max_search = (self.cvc.max_x - self.cvc.min_x) / 3
            print(f"    [DEBUG] Starting resilient search for a valid row position...")
            print(f"    [DEBUG]   - Ideal Start X: {ideal_x:.0f}, Y: {ideal_y:.0f}")

            while search_offset < max_search:
                for sign in [1, -1]: # Check right of center, then left
                    if sign == -1 and search_offset == 0: continue
                    
                    test_x = ideal_x + (search_offset * sign)
                    print(f"    [DEBUG]   - Testing row start at x={test_x:.0f}...")
                    
                    # Check if the entire bounding box for the row is valid
                    row_box = box(test_x, ideal_y, test_x + total_group_width, ideal_y + max(f.height for f in sofas_to_place_list))
                    if self.floorplan_polygon.contains(row_box) and not any(row_box.intersects(box(*b)) for b in placed_bboxes):
                        found_spot = (test_x, ideal_y)
                        print(f"    [DEBUG]   -> SUCCESS: Found clear row at x={test_x:.0f}")
                        break
                if found_spot:
                    break
                search_offset += 100 # Nudge search by 100mm
            
            if not found_spot:
                print("    [DEBUG]   -> FAILED: Resilient search could not find a clear space for the entire row.")
                return sofas_to_place_list

            # --- Place sofas one-by-one in the found spot ---
            placed_in_row = 0
            current_x = found_spot[0]
            unplaced = []
            avg_sofa_width = sum(f.width for f in sofas_to_place_list) / len(sofas_to_place_list)

            for sofa in sofas_to_place_list:
                if is_valid_spot(current_x, ideal_y, sofa):
                    self.place_fixture(sofa, (current_x, ideal_y, 0), 0, False)
                    placed_bboxes.append((current_x, ideal_y, current_x + sofa.width, ideal_y + sofa.height))
                    current_x += sofa.width + (avg_sofa_width * 0.25)
                    placed_in_row += 1
                else:
                    unplaced.append(sofa)

            if placed_in_row > 0:
                print(f"    ✅ Placed {placed_in_row} sofas in the row.")
            
            return unplaced


        # 5. DYNAMIC PLACEMENT LOGIC
        remaining_sofas = list(initial_sofas_to_place)

        # --- PHASE 1: Try to place ABOVE the anchors ---
        print("\n  -> Phase 1: Calculating dynamic position ABOVE anchors...")
        top_wall = self._get_wall_details('top')
        if top_wall and remaining_sofas:
            horizontal_gap = (sum(f.width for f in remaining_sofas) / len(remaining_sofas)) * 0.25
            total_sofa_width = sum(f.width for f in remaining_sofas) + (horizontal_gap * (len(remaining_sofas) - 1))
            max_sofa_height = max(f.height for f in remaining_sofas)

            available_space_above = top_wall['start_point'].y - anchor_cluster_bbox.extmax.y
            if available_space_above > max_sofa_height + 400:
                ideal_y_above = anchor_cluster_bbox.extmax.y + (available_space_above / 2) - (max_sofa_height / 2)
                remaining_sofas = place_sofa_row(remaining_sofas, ideal_y_above, total_sofa_width)
            else:
                print("    -> Not enough vertical space between anchors and top wall.")
        else:
            print("    -> Could not identify a 'top wall' or no sofas to place.")

        # --- PHASE 2: Try to place REMAINING sofas BELOW ---
        if remaining_sofas:
            print(f"\n  -> Phase 2: Attempting to place {len(remaining_sofas)} remaining sofas BELOW anchors...")
            bottom_wall = self._get_wall_details('bottom')
            if bottom_wall:
                horizontal_gap = (sum(f.width for f in remaining_sofas) / len(remaining_sofas)) * 0.25
                total_sofa_width = sum(f.width for f in remaining_sofas) + (horizontal_gap * (len(remaining_sofas) - 1))
                max_sofa_height = max(f.height for f in remaining_sofas)

                available_space_below = anchor_cluster_bbox.extmin.y - bottom_wall['start_point'].y
                if available_space_below > max_sofa_height + 400:
                    ideal_y_below = bottom_wall['start_point'].y + (available_space_below / 2) - (max_sofa_height / 2)
                    remaining_sofas = place_sofa_row(remaining_sofas, ideal_y_below, total_sofa_width)
                else:
                    print("    -> Not enough vertical space between anchors and bottom wall.")
            else:
                print("    -> Could not identify a 'bottom wall'.")

        # 6. FINAL REPORT
        placed_count = len(initial_sofas_to_place) - len(remaining_sofas)
        print(f"\n-> Finished Dynamic Sofa Placement: Placed {placed_count} of {len(initial_sofas_to_place)} requested sofas.")
        if remaining_sofas:
            print(f"⚠️ Could not place {len(remaining_sofas)} sofas as all available rows were full or blocked.")


    
    def define_circulation_paths(self, main_aisle_width=1500.0):
        """
        Defines the primary circulation paths as Shapely polygons.
        These are treated as "keep-out zones" for fixture placement.
        """
        print("\n--- 🚶 Defining Main Customer Circulation Paths ---")
        
        # 1. Find the main entrance (center of the bottom wall)
        bottom_wall = self._get_wall_details('bottom')
        if not bottom_wall:
            print("    ⚠️ Could not define entrance path: Bottom wall not found.")
            return []

        entrance_center = bottom_wall["start_point"].lerp(bottom_wall["end_point"])
        
        # 2. Define a destination point deep inside the store (e.g., center of the top third)
        room_center_x = self.floorplan_polygon.centroid.x
        room_height = self.cvc.max_y - self.cvc.min_y
        destination_y = self.cvc.max_y - (room_height * 0.20) # Target 80% of the way up
        
        # 3. Create a line representing the path and buffer it to create an aisle
        main_path_line = LineString([(entrance_center.x, entrance_center.y), (room_center_x, destination_y)])
        
        # The buffer creates a polygon with a radius of half the aisle width
        main_aisle_poly = main_path_line.buffer(main_aisle_width / 2, cap_style='flat')
        
        # Optional: Visualize the aisle in the DXF for debugging
        # You can uncomment this to see the generated path
        # self.msp.add_lwpolyline(
        #     main_aisle_poly.exterior.coords,
        #     close=True,
        #     dxfattribs={"layer": "DEBUG_CIRCULATION", "color": 5} # Blue
        # )

        print(f"    ✅ Main aisle defined with a width of {main_aisle_width} mm.")
        
        # Return the bounding box of the keep-out zone
        min_x, min_y, max_x, max_y = main_aisle_poly.bounds
        return [(min_x, min_y, max_x, max_y)]
    
    def run_post_processing_checks(self, circulation_zones: List[tuple] = None):
        """
        Runs a series of post-processing checks, now including verification
        against predefined circulation zones.
        """
        from shapely.geometry import box
        from shapely.ops import unary_union
        from ezdxf.bbox import extents
        import collections

        print("\n--- 🧐 Running Post-Processing Checks & Refinements ---")
        
        # Get all placed fixtures for the checks
        all_fixtures = list(self.msp.query('INSERT'))
        all_fixture_data = []
        for f in all_fixtures:
            try:
                bbox = extents([f], fast=True)
                all_fixture_data.append({
                    "name": f.dxf.name,
                    "poly": box(bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y)
                })
            except (RuntimeError, ZeroDivisionError, TypeError):
                continue

        # --- 1. Aisle & Clearance Verification (Existing Check) ---
        # This remains a useful check for space between fixture groups
        print("\n  -> 1. Verifying Aisle Clearances Between Fixture Groups...")
        MIN_AISLE_WIDTH = 900.0
        # ... (The rest of the aisle check logic remains unchanged) ...
        # (For brevity, I'm omitting the full code here, but it stays the same as before)
        central_fixture_polygons = []
        left_wall_fixture_polygons = []
        right_wall_fixture_polygons = []
        room_center_x = self.floorplan_polygon.centroid.x
        for f_data in all_fixture_data:
            f_name = f_data["name"]
            poly = f_data["poly"]
            # Heuristic to categorize fixtures into zones
            if "HYBRID" in f_name.upper() or "MIRROR" in f_name.upper():
                if poly.centroid.x < room_center_x:
                    left_wall_fixture_polygons.append(poly)
                else:
                    right_wall_fixture_polygons.append(poly)
            elif "CLINIC" not in f_name.upper() and "BOH" not in f_name.upper():
                 central_fixture_polygons.append(poly)
        central_group = unary_union(central_fixture_polygons)
        left_wall_group = unary_union(left_wall_fixture_polygons)
        right_wall_group = unary_union(right_wall_fixture_polygons)
        if not central_group.is_empty and not left_wall_group.is_empty:
            left_aisle_dist = central_group.distance(left_wall_group)
            print(f"    - Measured Left Aisle Width: {left_aisle_dist:.0f} mm")
            if left_aisle_dist < MIN_AISLE_WIDTH:
                print(f"    ⚠️ WARNING: Left aisle is too narrow (less than {MIN_AISLE_WIDTH} mm).")

        if not central_group.is_empty and not right_wall_group.is_empty:
            right_aisle_dist = central_group.distance(right_wall_group)
            print(f"    - Measured Right Aisle Width: {right_aisle_dist:.0f} mm")
            if right_aisle_dist < MIN_AISLE_WIDTH:
                print(f"    ⚠️ WARNING: Right aisle is too narrow (less than {MIN_AISLE_WIDTH} mm).")


        # --- 2. Verifying Circulation Path Integrity (NEW CHECK) ---
        print("\n  -> 2. Verifying Main Circulation Path Integrity...")
        if circulation_zones:
            path_violated = False
            # Combine all circulation zones into one MultiPolygon for checking
            circulation_poly = unary_union([box(*zone) for zone in circulation_zones])
            
            for f_data in all_fixture_data:
                # Check if a fixture's polygon intersects with the main path
                if circulation_poly.intersects(f_data["poly"]):
                    overlap_area = circulation_poly.intersection(f_data["poly"]).area
                    if overlap_area > 1.0: # Ignore tiny overlaps
                        print(f"    🔥 CRITICAL PATH VIOLATION: Fixture '{f_data['name']}' is blocking the main walking path.")
                        path_violated = True
            
            if not path_violated:
                print("    ✅ Main circulation path is clear.")
        else:
            print("    -> SKIPPED: No circulation zones were provided to check against.")


        # --- 3. Global Overlap Detection (Existing Check) ---
        print("\n  -> 3. Performing Global Overlap Detection...")
        overlap_found = False
        for i in range(len(all_fixture_data)):
            for j in range(i + 1, len(all_fixture_data)):
                f1 = all_fixture_data[i]
                f2 = all_fixture_data[j]
                if f1["poly"].intersects(f2["poly"]):
                    overlap_area = f1["poly"].intersection(f2["poly"]).area
                    if overlap_area > 1.0:
                        print(f"    🔥 CRITICAL OVERLAP DETECTED between '{f1['name']}' and '{f2['name']}' (Area: {overlap_area:.0f} sq mm).")
                        overlap_found = True
        if not overlap_found:
            print("    ✅ No overlaps found between fixtures.")

        # --- 4. Aesthetic Alignment (Existing Check) ---
        print("\n  -> 4. Checking and Correcting Alignment...")
        # ... (The alignment logic remains unchanged) ...
        # (For brevity, I'm omitting the full code here, but it stays the same as before)
        all_fixtures_ents = list(self.msp.query('INSERT'))
        euro_fixtures = [f for f in all_fixtures_ents if "EURO_CENTRE" in f.dxf.name.upper()]
        if len(euro_fixtures) > 1:
            columns = collections.defaultdict(list)
            for f in euro_fixtures:
                columns[round(f.dxf.insert.x / 100)].append(f)
            for col_key, fixtures_in_col in columns.items():
                if len(fixtures_in_col) > 1:
                    avg_x = sum(f.dxf.insert.x for f in fixtures_in_col) / len(fixtures_in_col)
                    print(f"    - Aligning column of {len(fixtures_in_col)} Euro Centres to common X-coordinate: {avg_x:.2f}")
                    for f in fixtures_in_col:
                        new_pos = Vec3(avg_x, f.dxf.insert.y, f.dxf.insert.z)
                        f.dxf.insert = new_pos
        
        print("\n--- ✅ Post-Processing Complete ---")

    def calculate_area_sqft(self) -> float:
        """
        Calculates the area of the floorplan polygon and converts it to square feet.

        Returns:
            The area in square feet, or 0.0 if the floorplan polygon doesn't exist.
        """
        if not hasattr(self, 'floorplan_polygon') or self.floorplan_polygon.is_empty:
            print("⚠️ Cannot calculate area: Floorplan polygon not created yet.")
            return 0.0

        # Shapely's .area gives the area in the polygon's coordinate units (which are mm)
        area_sq_mm = self.floorplan_polygon.area
        
        # Conversion factor from square mm to square feet
        SQMM_PER_SQFT = 92903.04 
        
        area_sq_ft = area_sq_mm / SQMM_PER_SQFT
        
        print(f"✅ Floorplan Area Calculated: {area_sq_ft:.2f} sq. ft.")
        return area_sq_ft




    def close_plan(self):
        # used_layers = set()
        # used_linetypes = set()
        # used_styles = set()

        # def collect_entity_refs(entity):
        #     layer = entity.dxf.get("layer", "0").upper()
        #     linetype = entity.dxf.get("linetype", "BYLAYER").upper()
        #     used_layers.add(layer)
        #     used_linetypes.add(linetype)
        #     if entity.dxftype() in {"TEXT", "MTEXT"}:
        #         style = entity.dxf.get("style", "STANDARD").upper()
        #         used_styles.add(style)

        # # Collect from modelspace
        # for e in self.msp:
        #     collect_entity_refs(e)

        # # Collect from all blocks
        # for name in self.doc.blocks.block_names():
        #     for e in self.doc.blocks[name]:
        #         collect_entity_refs(e)

        # # Ensure critical defaults
        # if "0" not in self.doc.layers:
        #     self.doc.layers.new("0")
        # if "BYLAYER" not in self.doc.linetypes:
        #     self.doc.linetypes.new("BYLAYER", dxfattribs={"description": "Auto", "pattern": [0.0]})
        # if "STANDARD" not in self.doc.styles:
        #     self.doc.styles.new("STANDARD")

        # # Add missing tables
        # for name in used_layers:
        #     if name not in self.doc.layers:
        #         self.doc.layers.new(name)
        # for name in used_linetypes:
        #     if name not in self.doc.linetypes:
        #         self.doc.linetypes.new(name, dxfattribs={"description": "Auto", "pattern": [0.0]})
        # for name in used_styles:
        #     if name not in self.doc.styles:
        #         self.doc.styles.new(name)

        # # Clean up unused layouts, keeping at least one paperspace
        # paperspace_layouts = [layout for layout in self.doc.layouts if layout.name.lower() != "model"]
        # if len(paperspace_layouts) > 1:
        #     for layout in paperspace_layouts[1:]:
        #         self.doc.layouts.delete(layout.name)

        # # Clean up empty blocks
        # for name in list(self.doc.blocks.block_names()):
        #     if name.lower().startswith("*model") or name.lower().startswith("*paper"):
        #         continue
        #     block = self.doc.blocks[name]
        #     if len(block) == 0:
        #         self.doc.blocks.delete_block(name)

        self.doc.saveas(self.dxf_out)
        print(f"✅ Saved DXF file to: {self.dxf_out}")






# -----------------New portrait mode---wall_fixture placemment setup---------------


    def place_wall_fixtures_perimeter_pass_v1(self):
        """
        The definitive wall fixture placement strategy combining perimeter search
        with the user-specified count splitting and dynamic re-queueing.
        """
        import collections

        print("\n--- 🧠 Starting NEW Perimeter Pass Wall Fixture Placement ---")
        
        # STEP 1: Split the total fixture counts into a queue for each pass
        wall_fixtures_config = self.fixtures.get("wall_fixtures", {})
        left_queue = collections.deque()
        right_queue = collections.deque()
        
        for name, count in wall_fixtures_config.items():
            if count > 0:
                left_count = count // 2
                right_count = count - left_count
                left_queue.extend([(name, 1)] * left_count)
                right_queue.extend([(name, 1)] * right_count)

        print(f"  -> Split counts -> Pass 1 Queue: {len(left_queue)}, Pass 2 Queue: {len(right_queue)}")

        if not left_queue and not right_queue:
            print("ℹ️ No wall fixtures were specified for placement.")
            return

        # STEP 2: Execute Pass 1 (Perimeter Search on Left Queue)
        # This pass uses the flexible 'place_fixtures_on_left_wall' logic but only with its share of fixtures.
        # It will stop if it hits a clinic, as per its internal logic.
        unplaced_from_pass1 = self.place_fixtures_on_left_wall(left_queue)

        # STEP 3: Dynamically move any leftovers to the second pass queue
        if unplaced_from_pass1:
            print(f"  -> {len(unplaced_from_pass1)} fixtures unplaced on Pass 1. Moving to Pass 2 queue.")
            right_queue.extend(unplaced_from_pass1)

        # STEP 4: Execute Pass 2 (Structured Perimeter Search on the combined Right Queue)
        # This pass will now place the right wall's original share PLUS any leftovers.
        if right_queue:
            self.place_fixtures_on_right_wall_new(right_queue)
        else:
            print("\n✅ All fixtures placed in Pass 1. No second pass needed.")

    def place_wall_fixtures_perimeter_pass(self):
        """
        The definitive wall fixture placement strategy combining perimeter search
        with a corrected, even count split and dynamic re-queueing.
        """
        import collections

        print("\n--- 🧠 Starting NEW Perimeter Pass Wall Fixture Placement ---")
        
        # ***** FIX: Corrected Count Splitting Logic *****
        
        # STEP 1: Create a single master list of all fixtures first.
        wall_fixtures_config = self.fixtures.get("wall_fixtures", {})
        master_fixture_list = []
        for name, count in wall_fixtures_config.items():
            if count > 0:
                master_fixture_list.extend([(name, 1)] * count)
        
        if not master_fixture_list:
            print("ℹ️ No wall fixtures were specified for placement.")
            return
            
        # STEP 2: Now, split the MASTER list for a truly even distribution.
        total_to_place = len(master_fixture_list)
        left_count = total_to_place // 2
        
        left_queue = collections.deque(master_fixture_list[:left_count])
        right_queue = collections.deque(master_fixture_list[left_count:])
        
        # ***** END OF FIX *****

        print(f"  -> Split counts -> Pass 1 Queue: {len(left_queue)}, Pass 2 Queue: {len(right_queue)}")

        # STEP 3: Execute Pass 1 (Perimeter Search on Left Queue)
        unplaced_from_pass1 = self.place_fixtures_on_left_wall(left_queue)

        # STEP 4: Dynamically move any leftovers to the second pass queue
        if unplaced_from_pass1:
            print(f"  -> {len(unplaced_from_pass1)} fixtures unplaced on Pass 1. Moving to Pass 2 queue.")
            # Prepending the leftovers to the right_queue makes it more likely to
            # try placing the same fixture type again sooner.
            right_queue.extendleft(reversed(unplaced_from_pass1))

        # STEP 5: Execute Pass 2 (Structured Perimeter Search on the combined Right Queue)
        if right_queue:
            self.place_fixtures_on_right_wall_new(right_queue)
        else:
            print("\n✅ All fixtures placed in Pass 1. No second pass needed.")

    def place_fixtures_on_left_wall_v1(self, fixture_queue: collections.deque):
        """
        Final Corrected Version: Places fixtures using a 'bench-style' search.
        For each fixture, it searches every wall segment from START to END.
        Returns any unplaced fixtures.
        """
        from Fixture import Fixture
        from shapely.geometry import Polygon, Point
        from ezdxf.math import BoundingBox2d, Vec2, Matrix44
        from ezdxf.bbox import extents
        import math
        import traceback
        import collections

        print("\n--- Placing Wall Fixtures (Pass 1: Perimeter Search) ---")
        try:
            # --- 1. SETUP ---
            if not fixture_queue:
                return collections.deque()

            mirror_config = self.fixtures.get("mirror_selection", {})
            selected_mirror_name = next((name for name, selected in mirror_config.items() if selected > 0), "mirror")
            horizontal_inset_for_hybrid = 0.0 if selected_mirror_name == "mirror_different" else 50.0

            placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
            all_segments = self.cvc.get_wall_segments(min_length=500)
            if not all_segments:
                return fixture_queue
            
            stop_entities = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper() or self.fixture_dict.get(e.dxf.name.split('_')[0].lower(), {}).get('type') == 'boh']
            stop_bboxes = []
            if stop_entities:
                for entity in stop_entities:
                    try:
                        bbox = extents([entity], fast=True)
                        stop_bboxes.append((bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y))
                    except (RuntimeError, ZeroDivisionError, TypeError):
                        continue
            
            stop_hit = False
            margin_from_wall = 10.0
            unplaced_fixtures = collections.deque()

            # --- BENCH-STYLE PLACEMENT LOOP ---
            while fixture_queue:
                if stop_hit:
                    unplaced_fixtures.extend(fixture_queue)
                    break

                item_to_try = fixture_queue.popleft()
                fixture_name, _ = item_to_try
                
                try:
                    hybrid_fxtr = Fixture(fixture_name, self.fixture_dict[fixture_name]["path"])
                    mirror_fxtr = Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
                except (KeyError, ValueError) as e:
                    unplaced_fixtures.append(item_to_try); continue

                placed_this_item = False
                print(f"\nSearching for a spot for '{hybrid_fxtr.name}'...")
                
                for i, segment in enumerate(all_segments):
                    p1, p2 = Vec2(segment[0]), Vec2(segment[1])
                    wall_vector = p2 - p1
                    wall_length = wall_vector.magnitude
                    wall_angle_rad = wall_vector.angle
                    wall_angle_deg = math.degrees(wall_angle_rad)

                    perp_vec = wall_vector.orthogonal().normalize()
                    test_point = p1 + wall_vector * 0.5 + perp_vec * 1.0
                    inward_normal = perp_vec if self.floorplan_polygon.contains(Point(test_point.x, test_point.y)) else -perp_vec

                    search_distance = 0
                    while search_distance + hybrid_fxtr.width <= wall_length:
                        footprint_start_h = p1 + wall_vector.normalize() * search_distance
                        center_on_wall_h = footprint_start_h + wall_vector.normalize() * (hybrid_fxtr.width / 2.0)
                        offset_dist_h = margin_from_wall + (hybrid_fxtr.height / 2.0) + horizontal_inset_for_hybrid
                        target_center_h = center_on_wall_h + inward_normal * offset_dist_h
                        local_center_h = hybrid_fxtr.bounding_box.center
                        transform_h = Matrix44.chain(Matrix44.translate(-local_center_h.x, -local_center_h.y, 0), Matrix44.z_rotate(wall_angle_rad), Matrix44.translate(target_center_h.x, target_center_h.y, 0))
                        rotated_offset_h = local_center_h.rotate(wall_angle_rad)
                        final_insert_point_h = target_center_h - rotated_offset_h
                        world_corners_h = list(transform_h.transform_vertices(hybrid_fxtr.bounding_box.rect_vertices()))
                        poly_h = Polygon([(p.x, p.y) for p in world_corners_h])
                        aabb_h = BoundingBox2d(world_corners_h)

                        if any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in stop_bboxes):
                            stop_hit = True; break

                        hybrid_is_valid = self.floorplan_polygon.contains(poly_h) and not any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                        if hybrid_is_valid:
                            mirror_search_dist = search_distance + hybrid_fxtr.width
                            mirror_is_valid = False
                            if mirror_search_dist + mirror_fxtr.width <= wall_length:
                                footprint_start_m = p1 + wall_vector.normalize() * mirror_search_dist
                                center_on_wall_m = footprint_start_m + wall_vector.normalize() * (mirror_fxtr.width / 2.0)
                                offset_dist_m = margin_from_wall + (mirror_fxtr.height / 2.0)
                                target_center_m = center_on_wall_m + inward_normal * offset_dist_m
                                local_center_m = mirror_fxtr.bounding_box.center
                                transform_m = Matrix44.chain(Matrix44.translate(-local_center_m.x, -local_center_m.y, 0), Matrix44.z_rotate(wall_angle_rad), Matrix44.translate(target_center_m.x, target_center_m.y, 0))
                                rotated_offset_m = local_center_m.rotate(wall_angle_rad)
                                final_insert_point_m = target_center_m - rotated_offset_m
                                world_corners_m = list(transform_m.transform_vertices(mirror_fxtr.bounding_box.rect_vertices()))
                                poly_m = Polygon([(p.x, p.y) for p in world_corners_m])
                                aabb_m = BoundingBox2d(world_corners_m)
                                mirror_is_valid = self.floorplan_polygon.contains(poly_m) and not any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                            if mirror_is_valid:
                                self.place_fixture(hybrid_fxtr, (final_insert_point_h.x, final_insert_point_h.y, 0), wall_angle_deg, True)
                                placed_bboxes.append((aabb_h.extmin.x, aabb_h.extmin.y, aabb_h.extmax.x, aabb_h.extmax.y))
                                self.place_fixture(mirror_fxtr, (final_insert_point_m.x, final_insert_point_m.y, 0), wall_angle_deg, True)
                                placed_bboxes.append((aabb_m.extmin.x, aabb_m.extmin.y, aabb_m.extmax.x, aabb_m.extmax.y))
                            else:
                                self.place_fixture(hybrid_fxtr, (final_insert_point_h.x, final_insert_point_h.y, 0), wall_angle_deg, True)
                                placed_bboxes.append((aabb_h.extmin.x, aabb_h.extmin.y, aabb_h.extmax.x, aabb_h.extmax.y))
                            
                            placed_this_item = True
                            break 

                        search_distance += 100.0
                    
                    if placed_this_item or stop_hit: break
                
                if not placed_this_item:
                    unplaced_fixtures.append(item_to_try)

            if stop_hit:
                print(f"\nℹ️ Pass 1 placement stopped by obstacle. Passing {len(unplaced_fixtures)} items to the next pass.")
            
            return unplaced_fixtures

        except Exception as e:
            print(f"🔥 An error occurred during Pass 1 wall placement: {e}")
            traceback.print_exc()
            return fixture_queue
    
    def place_fixtures_on_left_wall_v2(self, fixture_queue: collections.deque):
        """
        DEFINITIVE VERSION: Places all fixtures continuously along the walls
        with a controllable gap, and correctly validates the entire pair before placement.
        """
        from Fixture import Fixture
        from shapely.geometry import Polygon, Point
        from ezdxf.math import BoundingBox2d, Vec2, Matrix44
        from ezdxf.bbox import extents
        import math
        import traceback
        import collections

        print("\n--- Placing Wall Fixtures (Pass 1: FINAL Continuous Search) ---")
        try:
            if not fixture_queue:
                return collections.deque()

            GAP_BETWEEN_PAIRS = 0

            # --- Setup ---
            mirror_config = self.fixtures.get("mirror_selection", {})
            selected_mirror_name = next((name for name, selected in mirror_config.items() if selected > 0), "mirror")
            horizontal_inset_for_hybrid = 0.0 if selected_mirror_name == "mirror_different" else 50.0

            placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
            all_segments = self.cvc.get_wall_segments(min_length=500)
            if not all_segments:
                return fixture_queue
            
            stop_entities = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper() or self.fixture_dict.get(e.dxf.name.split('_')[0].lower(), {}).get('type') == 'boh']
            stop_bboxes = []
            if stop_entities:
                for entity in stop_entities:
                    try:
                        bbox = extents([entity], fast=True)
                        stop_bboxes.append((bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y))
                    except (RuntimeError, ZeroDivisionError, TypeError):
                        continue
            
            margin_from_wall = 10.0
            placement_cursors = {i: 50.0 for i in range(len(all_segments))}
            unplaced_fixtures = collections.deque()

            # --- Main Loop ---
            while fixture_queue:
                item_to_try = fixture_queue.popleft()
                fixture_name, _ = item_to_try
                
                try:
                    hybrid_fxtr = Fixture(fixture_name, self.fixture_dict[fixture_name]["path"])
                    mirror_fxtr = Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
                except (KeyError, ValueError) as e:
                    unplaced_fixtures.append(item_to_try); continue

                placed_this_item = False
                print(f"\nSearching for a spot for '{hybrid_fxtr.name}'...")

                for i, segment in enumerate(all_segments):
                    p1, p2 = Vec2(segment[0]), Vec2(segment[1])
                    # ... (wall geometry setup is the same)
                    wall_vector = p2 - p1
                    wall_length = wall_vector.magnitude
                    wall_angle_rad = wall_vector.angle
                    wall_angle_deg = math.degrees(wall_angle_rad)
                    inward_normal = wall_vector.orthogonal().normalize()
                    if not self.floorplan_polygon.contains(Point(p1 + inward_normal * 1.0)):
                        inward_normal = -inward_normal

                    search_distance = placement_cursors[i]
                    while search_distance + hybrid_fxtr.width <= wall_length - 50.0:
                        # --- 1. VALIDATE HYBRID SPOT ---
                        footprint_start_h = p1 + wall_vector.normalize() * search_distance
                        center_on_wall_h = footprint_start_h + wall_vector.normalize() * (hybrid_fxtr.width / 2.0)
                        offset_dist_h = margin_from_wall + (hybrid_fxtr.height / 2.0) + horizontal_inset_for_hybrid
                        target_center_h = center_on_wall_h + inward_normal * offset_dist_h
                        local_center_h = hybrid_fxtr.bounding_box.center
                        transform_h = Matrix44.chain(Matrix44.translate(-local_center_h.x, -local_center_h.y, 0), Matrix44.z_rotate(wall_angle_rad), Matrix44.translate(target_center_h.x, target_center_h.y, 0))
                        world_corners_h = list(transform_h.transform_vertices(hybrid_fxtr.bounding_box.rect_vertices()))
                        poly_h = Polygon([(p.x, p.y) for p in world_corners_h])
                        aabb_h = BoundingBox2d(world_corners_h)

                        if any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in stop_bboxes):
                            break

                        hybrid_is_valid = self.floorplan_polygon.contains(poly_h) and not any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                        if hybrid_is_valid:
                            # --- 2. IF HYBRID SPOT IS OK, VALIDATE MIRROR SPOT ---
                            mirror_search_dist = search_distance + hybrid_fxtr.width
                            mirror_is_valid = False
                            aabb_m = BoundingBox2d() # Default empty bbox
                            
                            if mirror_search_dist + mirror_fxtr.width <= wall_length:
                                footprint_start_m = p1 + wall_vector.normalize() * mirror_search_dist
                                center_on_wall_m = footprint_start_m + wall_vector.normalize() * (mirror_fxtr.width / 2.0)
                                offset_dist_m = margin_from_wall + (mirror_fxtr.height / 2.0) + horizontal_inset_for_hybrid
                                target_center_m = center_on_wall_m + inward_normal * offset_dist_m
                                local_center_m = mirror_fxtr.bounding_box.center
                                transform_m = Matrix44.chain(Matrix44.translate(-local_center_m.x, -local_center_m.y, 0), Matrix44.z_rotate(wall_angle_rad), Matrix44.translate(target_center_m.x, target_center_m.y, 0))
                                world_corners_m = list(transform_m.transform_vertices(mirror_fxtr.bounding_box.rect_vertices()))
                                poly_m = Polygon([(p.x, p.y) for p in world_corners_m])
                                aabb_m = BoundingBox2d(world_corners_m)
                                
                                # The crucial check against the same 'placed_bboxes' list
                                if self.floorplan_polygon.contains(poly_m) and not any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes):
                                    mirror_is_valid = True

                            # --- 3. PLACE FIXTURES BASED ON VALIDATION RESULTS ---
                            # Place Hybrid
                            final_insert_point_h = target_center_h - local_center_h.rotate(wall_angle_rad)
                            self.place_fixture(hybrid_fxtr, (final_insert_point_h.x, final_insert_point_h.y, 0), wall_angle_deg, True)
                            placed_bboxes.append((aabb_h.extmin.x, aabb_h.extmin.y, aabb_h.extmax.x, aabb_h.extmax.y))

                            # Place Mirror if it was valid
                            if mirror_is_valid:
                                final_insert_point_m = target_center_m - local_center_m.rotate(wall_angle_rad)
                                self.place_fixture(mirror_fxtr, (final_insert_point_m.x, final_insert_point_m.y, 0), wall_angle_deg, True)
                                placed_bboxes.append((aabb_m.extmin.x, aabb_m.extmin.y, aabb_m.extmax.x, aabb_m.extmax.y))
                                print(f"✅ Placed pair '{hybrid_fxtr.name}' & '{mirror_fxtr.name}'.")
                            else:
                                print(f"✅ Placed '{hybrid_fxtr.name}' alone (mirror blocked).")

                            # --- 4. UPDATE CURSOR ---
                            final_width = hybrid_fxtr.width + (mirror_fxtr.width if mirror_is_valid else 0)
                            placement_cursors[i] = search_distance + final_width + GAP_BETWEEN_PAIRS
                            
                            placed_this_item = True
                            break # Exit search loop for this item
                        
                        # If spot was blocked, nudge search forward on the SAME wall
                        search_distance += 100.0

                    if placed_this_item:
                        break # Exit wall segment loop for this item

                if not placed_this_item:
                    unplaced_fixtures.append(item_to_try)

            return unplaced_fixtures

        except Exception as e:
            print(f"🔥 An error occurred during wall placement: {e}")
            traceback.print_exc()
            unplaced_fixtures.extend(fixture_queue)
            return unplaced_fixtures


    def place_fixtures_on_left_wall(self, fixture_queue: collections.deque):
        """
        DEFINITIVE VERSION: Places all fixtures continuously along the walls
        with a controllable gap, and correctly validates the entire pair before placement.
        """
        from Fixture import Fixture
        from shapely.geometry import Polygon, Point
        from ezdxf.math import BoundingBox2d, Vec2, Matrix44
        from ezdxf.bbox import extents
        import math
        import traceback
        import collections

        print("\n--- Placing Wall Fixtures (Pass 1: FINAL Continuous Search) ---")
        try:
            if not fixture_queue:
                return collections.deque()

            GAP_BETWEEN_PAIRS = 0

            # --- Setup ---
            mirror_config = self.fixtures.get("mirror_selection", {})
            selected_mirror_name = next((name for name, selected in mirror_config.items() if selected > 0), "mirror")
            horizontal_inset_for_hybrid = 0.0 if selected_mirror_name == "mirror_different" else 50.0

            placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
            all_segments = self.cvc.get_wall_segments(min_length=500)
            if not all_segments:
                return fixture_queue
            
            stop_entities = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper() or self.fixture_dict.get(e.dxf.name.split('_')[0].lower(), {}).get('type') == 'boh']
            stop_bboxes = []
            if stop_entities:
                for entity in stop_entities:
                    try:
                        bbox = extents([entity], fast=True)
                        stop_bboxes.append((bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y))
                    except (RuntimeError, ZeroDivisionError, TypeError):
                        continue
            
            margin_from_wall = 10.0
            placement_cursors = {i: 50.0 for i in range(len(all_segments))}
            unplaced_fixtures = collections.deque()

            # --- Main Loop ---
            while fixture_queue:
                item_to_try = fixture_queue.popleft()
                fixture_name, _ = item_to_try
                
                try:
                    hybrid_fxtr = Fixture(fixture_name, self.fixture_dict[fixture_name]["path"])
                    mirror_fxtr = Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
                except (KeyError, ValueError) as e:
                    unplaced_fixtures.append(item_to_try); continue

                placed_this_item = False
                print(f"\nSearching for a spot for '{hybrid_fxtr.name}'...")

                for i, segment in enumerate(all_segments):
                    p1, p2 = Vec2(segment[0]), Vec2(segment[1])
                    # ... (wall geometry setup is the same)
                    wall_vector = p2 - p1
                    wall_length = wall_vector.magnitude
                    wall_angle_rad = wall_vector.angle
                    wall_angle_deg = math.degrees(wall_angle_rad)
                    inward_normal = wall_vector.orthogonal().normalize()
                    if not self.floorplan_polygon.contains(Point(p1 + inward_normal * 1.0)):
                        inward_normal = -inward_normal

                    search_distance = placement_cursors[i]
                    while search_distance + hybrid_fxtr.width <= wall_length - 50.0:
                        # --- 1. VALIDATE HYBRID SPOT ---
                        footprint_start_h = p1 + wall_vector.normalize() * search_distance
                        center_on_wall_h = footprint_start_h + wall_vector.normalize() * (hybrid_fxtr.width / 2.0)
                        offset_dist_h = margin_from_wall + (hybrid_fxtr.height / 2.0) + horizontal_inset_for_hybrid
                        target_center_h = center_on_wall_h + inward_normal * offset_dist_h
                        local_center_h = hybrid_fxtr.bounding_box.center
                        transform_h = Matrix44.chain(Matrix44.translate(-local_center_h.x, -local_center_h.y, 0), Matrix44.z_rotate(wall_angle_rad), Matrix44.translate(target_center_h.x, target_center_h.y, 0))
                        world_corners_h = list(transform_h.transform_vertices(hybrid_fxtr.bounding_box.rect_vertices()))
                        poly_h = Polygon([(p.x, p.y) for p in world_corners_h])
                        aabb_h = BoundingBox2d(world_corners_h)

                        if any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in stop_bboxes):
                            break

                        hybrid_is_valid = self.floorplan_polygon.contains(poly_h) and not any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                        if hybrid_is_valid:
                            # --- 2. IF HYBRID SPOT IS OK, VALIDATE MIRROR SPOT ---
                            mirror_search_dist = search_distance + hybrid_fxtr.width
                            mirror_is_valid = False
                            aabb_m = BoundingBox2d() # Default empty bbox
                            
                            if mirror_search_dist + mirror_fxtr.width <= wall_length:
                                footprint_start_m = p1 + wall_vector.normalize() * mirror_search_dist
                                center_on_wall_m = footprint_start_m + wall_vector.normalize() * (mirror_fxtr.width / 2.0)
                                offset_dist_m = margin_from_wall + (mirror_fxtr.height / 2.0) + horizontal_inset_for_hybrid
                                target_center_m = center_on_wall_m + inward_normal * offset_dist_m
                                local_center_m = mirror_fxtr.bounding_box.center
                                transform_m = Matrix44.chain(Matrix44.translate(-local_center_m.x, -local_center_m.y, 0), Matrix44.z_rotate(wall_angle_rad), Matrix44.translate(target_center_m.x, target_center_m.y, 0))
                                world_corners_m = list(transform_m.transform_vertices(mirror_fxtr.bounding_box.rect_vertices()))
                                poly_m = Polygon([(p.x, p.y) for p in world_corners_m])
                                aabb_m = BoundingBox2d(world_corners_m)
                                
                                # The crucial check against the same 'placed_bboxes' list
                                if self.floorplan_polygon.contains(poly_m) and not any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes):
                                    mirror_is_valid = True

                            # --- 3. PLACE FIXTURES BASED ON VALIDATION RESULTS ---
                            # Place Hybrid
                            final_insert_point_h = target_center_h - local_center_h.rotate(wall_angle_rad)
                            self.place_fixture(hybrid_fxtr, (final_insert_point_h.x, final_insert_point_h.y, 0), wall_angle_deg, True)
                            placed_bboxes.append((aabb_h.extmin.x, aabb_h.extmin.y, aabb_h.extmax.x, aabb_h.extmax.y))

                            # Place Mirror if it was valid
                            if mirror_is_valid:
                                final_insert_point_m = target_center_m - local_center_m.rotate(wall_angle_rad)
                                self.place_fixture(mirror_fxtr, (final_insert_point_m.x, final_insert_point_m.y, 0), wall_angle_deg, True)
                                placed_bboxes.append((aabb_m.extmin.x, aabb_m.extmin.y, aabb_m.extmax.x, aabb_m.extmax.y))
                                print(f"✅ Placed pair '{hybrid_fxtr.name}' & '{mirror_fxtr.name}'.")
                            else:
                                print(f"✅ Placed '{hybrid_fxtr.name}' alone (mirror blocked).")

                            # --- 4. UPDATE CURSOR ---
                            final_width = hybrid_fxtr.height + (mirror_fxtr.width if mirror_is_valid else 0) - 30
                            placement_cursors[i] = search_distance + final_width + GAP_BETWEEN_PAIRS
                            
                            placed_this_item = True
                            break # Exit search loop for this item
                        
                        # If spot was blocked, nudge search forward on the SAME wall
                        search_distance += 100.0

                    if placed_this_item:
                        break # Exit wall segment loop for this item

                if not placed_this_item:
                    unplaced_fixtures.append(item_to_try)

            return unplaced_fixtures

        except Exception as e:
            print(f"🔥 An error occurred during wall placement: {e}")
            traceback.print_exc()
            unplaced_fixtures.extend(fixture_queue)
            return unplaced_fixtures
        

        
    ##### NEW ROBUST HELPER FUNCTION #####
    def _get_reordered_corners_top_right_robust_v1(self):
        """
        ROBUST HELPER: Gets corners starting from the point closest to the
        theoretical top-right corner of the entire floorplan's bounding box.
        Ensures a CLOCKWISE (CW) path to go DOWN the wall.
        """
        corners = self.cvc.corners
        if not corners:
            return []
        
        target_x = self.cvc.max_x
        target_y = self.cvc.max_y

        start_idx = min(range(len(corners)),
                        key=lambda i: math.hypot(corners[i][0] - target_x, corners[i][1] - target_y))

        reordered = corners[start_idx:] + corners[:start_idx]
        
        signed_area = 0.5 * sum(x1*y2 - x2*y1 for (x1, y1), (x2, y2) in zip(reordered, reordered[1:] + [reordered[0]]))
        if signed_area > 0:
            print("  -> Path was counter-clockwise, reversing to ensure correct direction (down the right wall).")
            reordered = reordered[0:1] + reordered[1:][::-1]
            
        return reordered

    ##### NEW ROBUST HELPER FUNCTION #####
    def _get_reordered_corners_top_right_robust(self):
        """
        ROBUST HELPER: Gets corners starting from the point closest to the
        theoretical top-right corner of the entire floorplan's bounding box.
        Ensures a CLOCKWISE (CW) path to go DOWN the wall.
        """
        corners = self.cvc.corners
        if not corners:
            return []
        
        target_x = self.cvc.max_x
        target_y = self.cvc.max_y

        start_idx = min(range(len(corners)),
                        key=lambda i: math.hypot(corners[i][0] - target_x, corners[i][1] - target_y))

        reordered = corners[start_idx:] + corners[:start_idx]
        
        signed_area = 0.5 * sum(x1*y2 - x2*y1 for (x1, y1), (x2, y2) in zip(reordered, reordered[1:] + [reordered[0]]))
        if signed_area > 0:
            print("  -> Path was counter-clockwise, reversing to ensure correct direction (down the right wall).")
            reordered = reordered[0:1] + reordered[1:][::-1]
            
        return reordered


    def place_fixtures_on_right_wall_new(self, fixture_queue: collections.deque):
        """
        FINAL CORRECTED VERSION for Pass 2.
        - Includes a STRATEGY switch to either CENTER the group on the wall
        or ALIGN the last fixture to the BOTTOM of the wall.
        """
        from Fixture import Fixture
        from shapely.geometry import Polygon, Point
        from ezdxf.math import BoundingBox2d, Vec2, Matrix44
        import math

        # ***** CHOOSE YOUR PLACEMENT STRATEGY HERE *****
        # STRATEGY = "CENTER"
        STRATEGY = "ALIGN_BOTTOM"
        # ***********************************************

        print(f"\n--- Placing Wall Fixtures (Pass 2: TOP-Right -> Down Path, Strategy: {STRATEGY}) ---")
        if not fixture_queue:
            return

        # --- 1. Setup ---
        placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
        mirror_config = self.fixtures.get("mirror_selection", {})
        selected_mirror_name = next((name for name, selected in mirror_config.items() if selected > 0), "mirror")
        horizontal_inset_for_hybrid = 0.0 if selected_mirror_name == "mirror_different" else 50.0

        # --- 2. Create the Placement Path ---
        ordered_corners = self._get_reordered_corners_top_right_robust()
        perimeter_path = []
        for i in range(len(ordered_corners)):
            p1 = Vec2(ordered_corners[i])
            p2 = Vec2(ordered_corners[(i + 1) % len(ordered_corners)])
            if p1.distance(p2) > 100:
                perimeter_path.append((p1, p2))
        
        if not perimeter_path:
            print("    -> ⚠️ Could not determine a valid wall path for Pass 2.")
            return

        # --- 3. DYNAMICALLY CALCULATE THE STARTING CURSOR based on chosen STRATEGY ---
        placement_cursor = 0 # Default fallback value
        try:
            total_fixture_height = 0
            temp_queue = list(fixture_queue)
            if temp_queue:
                mirror = Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
                for i, (fixture_name, _) in enumerate(temp_queue):
                    hybrid = Fixture(fixture_name, self.fixture_dict[fixture_name]["path"])
                    total_fixture_height += hybrid.width + mirror.width
                if len(temp_queue) > 1:
                    total_fixture_height += 50 * (len(temp_queue) - 1)

            segment_start, segment_end = perimeter_path[0]
            wall_length = segment_start.distance(segment_end)

            if STRATEGY == "CENTER":
                if total_fixture_height < wall_length:
                    placement_cursor = (wall_length - total_fixture_height) / 2
                    print(f"  -> Strategy: CENTER. Dynamic cursor: {placement_cursor:.0f}mm")
                else:
                    print(f"  -> Fixture group is too long. Using default start margin.")
            
            elif STRATEGY == "ALIGN_BOTTOM":
                DESIRED_BOTTOM_MARGIN = 50.0 # How close the last fixture should be to the bottom
                if total_fixture_height < wall_length - DESIRED_BOTTOM_MARGIN:
                    placement_cursor = wall_length - total_fixture_height - DESIRED_BOTTOM_MARGIN
                    print(f"  -> Strategy: ALIGN_BOTTOM. Dynamic cursor calculated to leave {DESIRED_BOTTOM_MARGIN}mm at bottom.")
                else:
                    print(f"  -> Fixture group is too long for bottom alignment. Using default start margin.")

        except Exception as e:
            print(f"    -> ⚠️ Could not dynamically calculate cursor due to an error: {e}. Using default.")

        # --- 4. Main Placement Loop (This section remains unchanged) ---
        margin_from_wall = 10.0

        while fixture_queue:
            # (The rest of the placement logic is identical to the previous version)
            # ...
            item_to_try = fixture_queue.popleft()
            fixture_name, _ = item_to_try
            
            try:
                hybrid_fxtr = Fixture(fixture_name, self.fixture_dict[fixture_name]["path"])
                mirror_fxtr = Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
            except (KeyError, ValueError) as e:
                print(f"    -> ⚠️ Could not load {fixture_name}, skipping.")
                continue

            print(f"  -> Searching for a spot for '{hybrid_fxtr.name}'...")

            is_placed = False
            for segment_start, segment_end in perimeter_path:
                segment_vec = segment_end - segment_start
                if segment_vec.magnitude == 0: continue
                angle = abs(math.degrees(segment_vec.angle))
                mid_x = (segment_start.x + segment_end.x) / 2
                is_vertical = (75 < angle < 105) or (255 < angle < 285)
                is_left_wall = is_vertical and (abs(mid_x - self.cvc.min_x) < (self.cvc.max_x - self.cvc.min_x) * 0.15)
                if is_left_wall: continue

                segment_vector = segment_vec.normalize()
                segment_length = segment_start.distance(segment_end)
                wall_angle_deg = math.degrees(segment_vector.angle)
                inward_normal = segment_vector.orthogonal()
                if not self.floorplan_polygon.contains(Point(segment_start + inward_normal * 10)):
                    inward_normal = -inward_normal
                fixture_rotation_deg = wall_angle_deg
                if inward_normal.x < -0.1: fixture_rotation_deg += 180
                
                search_cursor = placement_cursor
                while search_cursor + hybrid_fxtr.width <= segment_length:
                    footprint_start_h = segment_start + segment_vector * search_cursor
                    center_on_wall_h = footprint_start_h + segment_vector * (hybrid_fxtr.width / 2.0)
                    offset_dist_h = margin_from_wall + (hybrid_fxtr.height / 2.0) + horizontal_inset_for_hybrid
                    target_center_h = center_on_wall_h + inward_normal * offset_dist_h
                    local_center_h = hybrid_fxtr.bounding_box.center
                    transform_h = Matrix44.chain(Matrix44.translate(-local_center_h.x, -local_center_h.y, 0), Matrix44.z_rotate(math.radians(fixture_rotation_deg)), Matrix44.translate(target_center_h.x, target_center_h.y, 0))
                    world_corners_h = list(transform_h.transform_vertices(hybrid_fxtr.bounding_box.rect_vertices()))
                    aabb_h = BoundingBox2d(world_corners_h)
                    hybrid_is_valid = self.floorplan_polygon.contains(Polygon(world_corners_h)) and not any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                    if hybrid_is_valid:
                        mirror_is_valid = False
                        mirror_cursor_start = search_cursor + hybrid_fxtr.width
                        if mirror_cursor_start + mirror_fxtr.width <= segment_length:
                            footprint_start_m = segment_start + segment_vector * mirror_cursor_start
                            center_on_wall_m = footprint_start_m + segment_vector * (mirror_fxtr.width / 2.0)
                            offset_dist_m = margin_from_wall + (mirror_fxtr.height / 2.0)
                            target_center_m = center_on_wall_m + inward_normal * offset_dist_m
                            local_center_m = mirror_fxtr.bounding_box.center
                            transform_m = Matrix44.chain(Matrix44.translate(-local_center_m.x, -local_center_m.y, 0), Matrix44.z_rotate(math.radians(fixture_rotation_deg)), Matrix44.translate(target_center_m.x, target_center_m.y, 0))
                            world_corners_m = list(transform_m.transform_vertices(mirror_fxtr.bounding_box.rect_vertices()))
                            aabb_m = BoundingBox2d(world_corners_m)
                            if self.floorplan_polygon.contains(Polygon(world_corners_m)) and not any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes):
                                mirror_is_valid = True

                        rotated_offset_h = local_center_h.rotate(math.radians(fixture_rotation_deg))
                        final_insert_point_h = target_center_h - rotated_offset_h
                        self.place_fixture(hybrid_fxtr, (final_insert_point_h.x, final_insert_point_h.y, 0), fixture_rotation_deg, True)
                        placed_bboxes.append(tuple(aabb_h.extmin) + tuple(aabb_h.extmax))

                        if mirror_is_valid:
                            rotated_offset_m = local_center_m.rotate(math.radians(fixture_rotation_deg))
                            final_insert_point_m = target_center_m - rotated_offset_m
                            self.place_fixture(mirror_fxtr, (final_insert_point_m.x, final_insert_point_m.y, 0), fixture_rotation_deg, True)
                            placed_bboxes.append(tuple(aabb_m.extmin) + tuple(aabb_m.extmax))
                            print(f"    -> ✅ Placed pair '{hybrid_fxtr.name}' & '{mirror_fxtr.name}'.")
                        else:
                            print(f"    -> ✅ Placed '{hybrid_fxtr.name}' alone (mirror blocked).")
                        
                        placement_cursor = search_cursor + hybrid_fxtr.width + (mirror_fxtr.width if mirror_is_valid else 0) + 0
                        is_placed = True
                        break
                    
                    search_cursor += 100.0
                
                if is_placed:
                    break
            
            if not is_placed:
                print(f"    -> ⚠️ Could not find a spot for '{fixture_name}'.")
                fixture_queue.appendleft(item_to_try)
                break


    
    # In DXF_Controller.py, replace the entire function with this corrected version

    # def place_wall_fixtures_from_boh_anticlockwise(self, placed_bboxes):
    #     """
    #     Places wall fixtures in a specific anti-clockwise path: starts on the
    #     top wall to the left of BOH, moves left, then down the left wall,
    #     and finally right along the bottom wall. Places Hybrid+Mirror pairs
    #     with no gap between them.
    #     """
    #     import collections
    #     from shapely.geometry import Polygon, Point
    #     from ezdxf.math import Vec2, BoundingBox2d
    #     from ezdxf.bbox import extents
    #     import math

    #     print("\n--- 🏃‍♂️ Placing Wall Fixtures (BOH Anti-Clockwise Path) ---")

    #     # 1. SETUP: Load fixtures and mirror
    #     wall_fixtures_config = self.fixtures.get("wall_fixtures", {})
    #     master_queue = collections.deque([(name, 1) for name, count in wall_fixtures_config.items() if count > 0 for _ in range(count)])
        
    #     if not master_queue:
    #         print("  -> SKIPPED: No wall fixtures specified.")
    #         return

    #     mirror_config = self.fixtures.get("mirror_selection", {})
    #     selected_mirror_name = next((name for name, selected in mirror_config.items() if selected > 0), "mirror")

    #     # 2. FIND BOH to define the starting point (Using the robust method)
    #     boh_entities = []
    #     for entity in self.msp.query('INSERT'):
    #         block_name_upper = entity.dxf.name.upper()
    #         best_match_key = ""
    #         for key in self.fixture_dict.keys():
    #             sanitized_key = key.upper().replace(" ", "_")
    #             if block_name_upper.startswith(sanitized_key):
    #                 if len(key) > len(best_match_key):
    #                     best_match_key = key
            
    #         if best_match_key and self.fixture_dict[best_match_key].get("type") == 'boh':
    #             boh_entities.append(entity)
        
    #     if not boh_entities:
    #         print("  -> SKIPPED: No BOH fixtures found to anchor the starting point.")
    #         return
    #     boh_bbox = extents(boh_entities)

    #     # 3. CONSTRUCT THE CUSTOM PERIMETER PATH
    #     path_segments = []
    #     top_wall = self._get_wall_details('top')
    #     left_wall = self._get_wall_details('left')
    #     bottom_wall = self._get_wall_details('bottom')

    #     if top_wall:
    #         start_x = boh_bbox.extmin.x - 50 
    #         start_point = Vec2(start_x, top_wall['start_point'].y)
    #         end_point = top_wall['start_point']
    #         if start_point.x > end_point.x:
    #              path_segments.append((start_point, end_point))

    #     if left_wall:
    #         path_segments.append((left_wall['start_point'], left_wall['end_point']))

    #     if bottom_wall:
    #         path_segments.append((bottom_wall['start_point'], bottom_wall['end_point']))

    #     if not path_segments:
    #         print("  -> FAILED: Could not construct a valid wall path.")
    #         return
        
    #     print(f"  -> Path constructed with {len(path_segments)} segments.")

    #     # 4. CONTINUOUS PLACEMENT LOOP
    #     margin_from_wall = 10.0
        
    #     for segment_start, segment_end in path_segments:
    #         if not master_queue: break

    #         segment_vector = (segment_end - segment_start).normalize()
    #         segment_length = segment_start.distance(segment_end)
    #         wall_angle_deg = math.degrees(segment_vector.angle)
            
    #         inward_normal = segment_vector.orthogonal()
    #         if not self.floorplan_polygon.contains(Point(segment_start + inward_normal * 10)):
    #             inward_normal = -inward_normal

    #         cursor = 0.0 
    #         while master_queue:
    #             try:
    #                 hybrid_name, _ = master_queue[0]
    #                 hybrid_fxtr = Fixture.Fixture(hybrid_name, self.fixture_dict[hybrid_name]["path"])
    #                 mirror_fxtr = Fixture.Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
    #             except (KeyError, ValueError):
    #                 master_queue.popleft()
    #                 continue
                
    #             pair_width = hybrid_fxtr.width + mirror_fxtr.width
    #             if cursor + pair_width > segment_length:
    #                 break

    #             center_h = segment_start + segment_vector * (cursor + hybrid_fxtr.width / 2) + inward_normal * (margin_from_wall + hybrid_fxtr.height / 2)
    #             aabb_h = self._get_fixture_aabb(hybrid_fxtr, center_h, wall_angle_deg)
                
    #             center_m = segment_start + segment_vector * (cursor + hybrid_fxtr.width + mirror_fxtr.width / 2) + inward_normal * (margin_from_wall + mirror_fxtr.height / 2)
    #             aabb_m = self._get_fixture_aabb(mirror_fxtr, center_m, wall_angle_deg)

    #             # ################### THIS IS THE CORRECTED LOGIC ###################
    #             # FIX: Create a BoundingBox2d object before passing it to has_intersection
    #             is_hybrid_blocked = any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)
    #             is_mirror_blocked = any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)
    #             # ################### END OF CORRECTION ###################

    #             if not is_hybrid_blocked and not is_mirror_blocked:
    #                 self._validate_and_place_at_point(hybrid_fxtr, center_h, wall_angle_deg, placed_bboxes)
    #                 self._validate_and_place_at_point(mirror_fxtr, center_m, wall_angle_deg, placed_bboxes)
    #                 print(f"    -> Placed pair: '{hybrid_fxtr.name}' & '{mirror_fxtr.name}'")
    #                 master_queue.popleft()
    #                 cursor += pair_width
    #             else:
    #                 cursor += 0
        
    #     # 5. FINAL REPORT
    #     if master_queue:
    #         print(f"\n--- ⚠️ Finished with {len(master_queue)} unplaced wall fixtures. ---")
    #     else:
    #         print("\n--- ✅ Finished BOH Anti-Clockwise Wall Fixture Placement ---")


    # In DXF_Controller.py, replace the function with this one:

    # In DXF_Controller.py, add this new function at the end of the file

    def place_fixtures_on_left_wall_until_boh(self, placed_bboxes):
        """
        A simple and direct strategy that places wall fixtures starting from the
        bottom-left corner and moves up the left wall, stopping when it
        approaches the BOH area.
        """
        import collections
        from shapely.geometry import Polygon, Point
        from ezdxf.math import Vec2, BoundingBox2d
        from ezdxf.bbox import extents
        import math

        print("\n--- 🏃‍♂️ Placing Fixtures on Left Wall (Stopping at BOH) ---")

        # 1. SETUP: Load fixtures and mirror
        wall_fixtures_config = self.fixtures.get("wall_fixtures", {})
        master_queue = collections.deque([(name, 1) for name, count in wall_fixtures_config.items() if count > 0 for _ in range(count)])
        
        if not master_queue:
            print("  -> SKIPPED: No wall fixtures specified.")
            return

        mirror_config = self.fixtures.get("mirror_selection", {})
        selected_mirror_name = next((name for name, selected in mirror_config.items() if selected > 0), "mirror")

        # 2. IDENTIFY BOH "STOP" ZONE
        boh_entities = [e for e in self.msp.query('INSERT') if self.fixture_dict.get(e.dxf.name.split('_')[0].lower(), {}).get('type') == 'boh']
        if not boh_entities:
            print("  -> WARNING: No BOH fixtures found to define a stopping point. Placement will continue to the end of the wall.")
            stop_bbox = None
        else:
            boh_cluster_bbox = extents(boh_entities)
            # Create a "stop" zone with a 500mm buffer below the BOH area
            buffer = 500.0
            stop_bbox = BoundingBox2d([
                (boh_cluster_bbox.extmin.x - buffer, boh_cluster_bbox.extmin.y - buffer),
                (boh_cluster_bbox.extmax.x + buffer, boh_cluster_bbox.extmax.y + buffer)
            ])
            print(f"  -> BOH stop zone defined. Placement will halt near y={boh_bbox.extmin.y:.0f}")

        # 3. GET THE LEFT WALL PATH
        left_wall = self._get_wall_details('left')
        if not left_wall:
            print("  -> FAILED: Could not identify the left wall.")
            return

        # The path starts at the bottom and goes up
        segment_start = left_wall['start_point']
        segment_end = left_wall['end_point']
        segment_vector = (segment_end - segment_start).normalize()
        segment_length = segment_start.distance(segment_end)
        wall_angle_deg = math.degrees(segment_vector.angle)
        
        inward_normal = segment_vector.orthogonal()
        if not self.floorplan_polygon.contains(Point(segment_start + inward_normal * 10)):
            inward_normal = -inward_normal

        # 4. PLACEMENT LOOP
        margin_from_wall = 10.0
        cursor = 50.0 # Start 50mm from the bottom corner
        
        while master_queue:
            try:
                hybrid_name, _ = master_queue[0]
                hybrid_fxtr = Fixture.Fixture(hybrid_name, self.fixture_dict[hybrid_name]["path"])
                mirror_fxtr = Fixture.Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
            except (KeyError, ValueError):
                master_queue.popleft(); continue
            
            pair_width = hybrid_fxtr.width + mirror_fxtr.width
            if cursor + pair_width > segment_length:
                print("  -> Halting placement: Reached end of the left wall.")
                break

            # Calculate candidate positions
            center_h = segment_start + segment_vector * (cursor + hybrid_fxtr.width / 2) + inward_normal * (margin_from_wall + hybrid_fxtr.height / 2)
            aabb_h = self._get_fixture_aabb(hybrid_fxtr, center_h, wall_angle_deg)
            
            center_m = segment_start + segment_vector * (cursor + hybrid_fxtr.width + mirror_fxtr.width / 2) + inward_normal * (margin_from_wall + mirror_fxtr.height / 2)
            aabb_m = self._get_fixture_aabb(mirror_fxtr, center_m, wall_angle_deg)

            # --- CRITICAL STOP CHECK ---
            if stop_bbox and (aabb_h.has_intersection(stop_bbox) or aabb_m.has_intersection(stop_bbox)):
                print("  -> Halting placement: Approaching BOH zone.")
                break

            # Standard collision check
            is_blocked = any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes) or \
                         any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

            if not is_blocked:
                self._validate_and_place_at_point(hybrid_fxtr, center_h, wall_angle_deg, placed_bboxes)
                self._validate_and_place_at_point(mirror_fxtr, center_m, wall_angle_deg, placed_bboxes)
                print(f"    -> Placed pair: '{hybrid_fxtr.name}' & '{mirror_fxtr.name}'")
                master_queue.popleft()
                cursor += pair_width # Advance with no gap
            else:
                cursor += 100.0 # Nudge past obstacle
        
        if master_queue:
            print(f"\n--- ⚠️ Finished with {len(master_queue)} unplaced wall fixtures. ---")
        else:
            print("\n--- ✅ Finished Left Wall Placement Successfully ---")

    # In DXF_Controller.py, REPLACE the old helper function with this one:

    def _get_reordered_corners_bottom_left_clockwise(self):
        """
        HELPER: Gets corners starting from the bottom-left and GUARANTEES a
        clockwise (CW) path (right across the bottom wall, up the right wall, etc.).
        """
        corners = self.cvc.corners
        if not corners:
            return []
        
        # Find the corner closest to the ideal bottom-left
        start_idx = min(range(len(corners)), 
                           key=lambda i: math.hypot(corners[i][0] - self.cvc.min_x, corners[i][1] - self.cvc.min_y))
        
        reordered = corners[start_idx:] + corners[:start_idx]
        
        # Check winding order. Positive area = CCW.
        signed_area = 0.5 * sum(x1*y2 - x2*y1 for (x1, y1), (x2, y2) in zip(reordered, reordered[1:] + [reordered[0]]))
        
        # If the area is positive (anti-clockwise), we must reverse it to be clockwise.
        if signed_area > 0:
            print("  [INFO] Path was anti-clockwise, reversing to ensure correct clockwise direction.")
            reordered = reordered[0:1] + reordered[1:][::-1]
            
        return reordered
    
    # In DXF_Controller.py, REPLACE the main function with this one:

    def place_wall_fixtures_perimeter_until_boh_v1(self, placed_bboxes):
        """
        FINAL STRATEGY: Places wall fixtures in a continuous clockwise
        perimeter walk starting from the bottom-left. It places pairs
        of (wall_fixture + mirror) with no gap and stops immediately
        when it approaches the BOH zone.
        """
        import collections
        from shapely.geometry import Polygon, Point
        from ezdxf.math import Vec2, BoundingBox2d
        from ezdxf.bbox import extents
        import math

        print("\n--- 🏃‍♂️ Placing Wall Fixtures (Clockwise Perimeter Walk Until BOH) ---")

        # 1. SETUP
        # --- FIX: Load ONLY wall fixtures into the queue, not mirrors ---
        wall_fixtures_config = self.fixtures.get("wall_fixtures", {})
        master_queue = collections.deque()
        for name, count in wall_fixtures_config.items():
            if count > 0:
                master_queue.extend([(name, 1)] * count)
        
        if not master_queue:
            print("  -> SKIPPED: No wall fixtures specified.")
            return

        # --- FIX: Load the single selected mirror separately ---
        mirror_config = self.fixtures.get("mirror_selection", {})
        selected_mirror_name = next((name for name, selected in mirror_config.items() if selected > 0), "mirror")

        # 2. IDENTIFY BOH "STOP" ZONE
        boh_entities = [e for e in self.msp.query('INSERT') if self.fixture_dict.get(e.dxf.name.split('_')[0].lower(), {}).get('type') == 'boh']
        if not boh_entities:
            stop_bbox = None
            print("  -> WARNING: No BOH fixtures found to define a stopping point.")
        else:
            boh_cluster_bbox = extents(boh_entities)
            buffer = 500.0
            stop_bbox = BoundingBox2d([
                (boh_cluster_bbox.extmin.x - buffer, boh_cluster_bbox.extmin.y - buffer),
                (boh_cluster_bbox.extmax.x + buffer, boh_cluster_bbox.extmax.y + buffer)
            ])
            print(f"  -> BOH stop zone defined. Placement will halt near this area.")

        # 3. CONSTRUCT THE CLOCKWISE PERIMETER PATH
        ordered_corners = self._get_reordered_corners_bottom_left_clockwise()
        perimeter_path = []
        for i in range(len(ordered_corners)):
            p1 = Vec2(ordered_corners[i])
            p2 = Vec2(ordered_corners[(i + 1) % len(ordered_corners)])
            if p1.distance(p2) > 100:
                perimeter_path.append((p1, p2))
        
        print(f"  -> Path constructed with {len(perimeter_path)} segments, starting from bottom-left (clockwise).")

        # 4. PERIMETER PLACEMENT LOOP
        margin_from_wall = 10.0
        stop_placement = False 
        
        for segment_start, segment_end in perimeter_path:
            if not master_queue or stop_placement: break

            segment_vector = (segment_end - segment_start).normalize()
            segment_length = segment_start.distance(segment_end)
            wall_angle_deg = math.degrees(segment_vector.angle)
            
            inward_normal = segment_vector.orthogonal()
            if not self.floorplan_polygon.contains(Point(segment_start + inward_normal * 10)):
                inward_normal = -inward_normal

            cursor = 50.0 
            while master_queue:
                try:
                    # --- FIX: Load the next WALL FIXTURE from the queue ---
                    wall_fixture_name, _ = master_queue[0]
                    wall_fxtr = Fixture.Fixture(wall_fixture_name, self.fixture_dict[wall_fixture_name]["path"])
                    # --- FIX: Load the globally selected MIRROR ---
                    mirror_fxtr = Fixture.Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
                except (KeyError, ValueError):
                    master_queue.popleft(); continue
                
                pair_width = wall_fxtr.width + mirror_fxtr.width
                if cursor + pair_width > segment_length - 50.0:
                    break

                center_h = segment_start + segment_vector * (cursor + wall_fxtr.width / 2) + inward_normal * (margin_from_wall + wall_fxtr.height / 2)
                aabb_h = self._get_fixture_aabb(wall_fxtr, center_h, wall_angle_deg)
                
                center_m = segment_start + segment_vector * (cursor + wall_fxtr.width + mirror_fxtr.width / 2) + inward_normal * (margin_from_wall + mirror_fxtr.height / 2)
                aabb_m = self._get_fixture_aabb(mirror_fxtr, center_m, wall_angle_deg)

                if stop_bbox and (aabb_h.has_intersection(stop_bbox) or aabb_m.has_intersection(stop_bbox)):
                    print("  -> Halting placement: Approaching BOH zone.")
                    stop_placement = True
                    break

                is_blocked = any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes) or \
                             any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                if not is_blocked:
                    self._validate_and_place_at_point(wall_fxtr, center_h, wall_angle_deg, placed_bboxes)
                    self._validate_and_place_at_point(mirror_fxtr, center_m, wall_angle_deg, placed_bboxes)
                    # --- FIX: Corrected print statement for clarity ---
                    print(f"    -> Placed pair: '{wall_fxtr.name}' & '{mirror_fxtr.name}'")
                    master_queue.popleft()
                    cursor += pair_width
                else:
                    cursor += 100.0
        
        if master_queue:
            print(f"\n--- ⚠️ Finished with {len(master_queue)} unplaced wall fixtures. ---")
        else:
            print("\n--- ✅ Finished Perimeter Wall Fixture Placement Successfully ---")


    def place_wall_fixtures_perimeter_until_boh(self, placed_bboxes):
        """
        FINAL STRATEGY: Places wall fixtures in a continuous clockwise
        perimeter walk starting from the bottom-left. It places pairs
        of (wall_fixture + mirror) with no gap and stops immediately
        when it approaches the BOH zone.
        """
        import collections
        from shapely.geometry import Polygon, Point
        from ezdxf.math import Vec2, BoundingBox2d
        from ezdxf.bbox import extents
        import math

        print("\n--- 🏃‍♂️ Placing Wall Fixtures (Clockwise Perimeter Walk Until BOH) ---")

        # 1. SETUP
        wall_fixtures_config = self.fixtures.get("wall_fixtures", {})
        master_queue = collections.deque()
        for name, count in wall_fixtures_config.items():
            if count > 0:
                master_queue.extend([(name, 1)] * count)
        
        if not master_queue:
            print("  -> SKIPPED: No wall fixtures specified.")
            return

        mirror_config = self.fixtures.get("mirror_selection", {})
        selected_mirror_name = next((name for name, selected in mirror_config.items() if selected > 0), "mirror")

        # 2. IDENTIFY BOH "STOP" ZONE
        boh_entities = []
        for entity in self.msp.query('INSERT'):
            block_name_upper = entity.dxf.name.upper()
            best_match_key = ""
            for key in self.fixture_dict.keys():
                sanitized_key = key.upper().replace(" ", "_")
                if block_name_upper.startswith(sanitized_key):
                    if len(key) > len(best_match_key):
                        best_match_key = key
            if best_match_key and self.fixture_dict[best_match_key].get("type") == 'boh':
                boh_entities.append(entity)
        
        if not boh_entities:
            stop_bbox = None
            print("  -> WARNING: No BOH fixtures found to define a stopping point.")
        else:
            boh_cluster_bbox = extents(boh_entities)
            buffer = 500.0
            stop_bbox = BoundingBox2d([
                (boh_cluster_bbox.extmin.x - buffer, boh_cluster_bbox.extmin.y - buffer),
                (boh_cluster_bbox.extmax.x + buffer, boh_cluster_bbox.extmax.y + buffer)
            ])
            print(f"  -> BOH stop zone defined. Placement will halt near this area.")

        # 3. CONSTRUCT THE CLOCKWISE PERIMETER PATH
        ordered_corners = self._get_reordered_corners_bottom_left_clockwise_new()
        perimeter_path = []
        for i in range(len(ordered_corners)):
            p1 = Vec2(ordered_corners[i])
            p2 = Vec2(ordered_corners[(i + 1) % len(ordered_corners)])
            if p1.distance(p2) > 100:
                perimeter_path.append((p1, p2))
        
        print(f"  -> Path constructed with {len(perimeter_path)} segments, starting from bottom-left (clockwise).")

        # 4. PERIMETER PLACEMENT LOOP
        margin_from_wall = 10.0
        stop_placement = False 
        
        for segment_start, segment_end in perimeter_path:
            if not master_queue or stop_placement: break

            segment_vector = (segment_end - segment_start).normalize()
            segment_length = segment_start.distance(segment_end)
            wall_angle_deg = math.degrees(segment_vector.angle)
            
            inward_normal = segment_vector.orthogonal()
            if not self.floorplan_polygon.contains(Point(segment_start + inward_normal * 10)):
                inward_normal = -inward_normal

            cursor = 50.0 
            while master_queue:
                try:
                    wall_fixture_name, _ = master_queue[0]
                    wall_fxtr = Fixture.Fixture(wall_fixture_name, self.fixture_dict[wall_fixture_name]["path"])
                    mirror_fxtr = Fixture.Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
                except (KeyError, ValueError):
                    master_queue.popleft(); continue
                
                pair_width = wall_fxtr.width + mirror_fxtr.width
                if cursor + pair_width > segment_length - 50.0:
                    break

                center_h = segment_start + segment_vector * (cursor + wall_fxtr.width / 2) + inward_normal * (margin_from_wall + wall_fxtr.height / 2)
                aabb_h = self._get_fixture_aabb(wall_fxtr, center_h, wall_angle_deg)
                
                center_m = segment_start + segment_vector * (cursor + wall_fxtr.width + mirror_fxtr.width / 2) + inward_normal * (margin_from_wall + mirror_fxtr.height / 2)
                aabb_m = self._get_fixture_aabb(mirror_fxtr, center_m, wall_angle_deg)

                if stop_bbox and (aabb_h.has_intersection(stop_bbox) or aabb_m.has_intersection(stop_bbox)):
                    print("  -> Halting placement: Approaching BOH zone.")
                    stop_placement = True
                    break

                is_blocked = any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes) or \
                             any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                # ################### THIS IS THE CORRECTED LOGIC ###################
                if not is_blocked:
                    # Place Hybrid directly
                    local_center_h = wall_fxtr.bounding_box.center
                    rotated_offset_h = local_center_h.rotate(math.radians(wall_angle_deg))
                    final_insert_point_h = center_h - rotated_offset_h
                    self.place_fixture(wall_fxtr, (final_insert_point_h.x, final_insert_point_h.y, 0), wall_angle_deg, True)
                    placed_bboxes.append((aabb_h.extmin.x, aabb_h.extmin.y, aabb_h.extmax.x, aabb_h.extmax.y))

                    # Place Mirror directly
                    local_center_m = mirror_fxtr.bounding_box.center
                    rotated_offset_m = local_center_m.rotate(math.radians(wall_angle_deg))
                    final_insert_point_m = center_m - rotated_offset_m
                    self.place_fixture(mirror_fxtr, (final_insert_point_m.x, final_insert_point_m.y, 0), wall_angle_deg, True)
                    placed_bboxes.append((aabb_m.extmin.x, aabb_m.extmin.y, aabb_m.extmax.x, aabb_m.extmax.y))
                    
                    # Update state
                    print(f"    -> Placed pair: '{wall_fxtr.name}' & '{mirror_fxtr.name}'")
                    master_queue.popleft()
                    cursor += pair_width - 50
                else:
                    cursor += 100.0
                # ################### END OF CORRECTION ###################
        
        if master_queue:
            print(f"\n--- ⚠️ Finished with {len(master_queue)} unplaced wall fixtures. ---")
        else:
            print("\n--- ✅ Finished Perimeter Wall Fixture Placement Successfully ---")

    def _get_reordered_corners_bottom_left_clockwise_new(self):
        """
        HELPER: Gets corners starting from the bottom-left and GUARANTEES a
        clockwise (CW) path (right across the bottom wall, up the right wall, etc.).
        """
        import math
        corners = self.cvc.corners
        if not corners:
            return []
        
        # Find the corner closest to the ideal bottom-left
        start_idx = min(range(len(corners)), 
                           key=lambda i: math.hypot(corners[i][0] - self.cvc.min_x, corners[i][1] - self.cvc.min_y))
        
        reordered = corners[start_idx:] + corners[:start_idx]
        
        # Check winding order. Positive area = CCW.
        signed_area = 0.5 * sum(x1*y2 - x2*y1 for (x1, y1), (x2, y2) in zip(reordered, reordered[1:] + [reordered[0]]))
        
        # If the area is positive (anti-clockwise), we must reverse it to be clockwise.
        if signed_area > 0:
            print("  [INFO] Path was anti-clockwise, reversing to ensure correct clockwise direction.")
            reordered = reordered[0:1] + reordered[1:][::-1]
            
        return reordered


    def place_wall_fixtures_continuously(self, placed_bboxes):
        """
        Places all wall fixtures in a continuous path starting from the
        bottom-left corner and stopping when it nears a BOH fixture.
        """
        import collections
        from shapely.geometry import Polygon, Point, box
        from ezdxf.math import BoundingBox2d, Vec2, Matrix44
        from ezdxf.bbox import extents
        import math

        print("\n--- 🏃‍♂️ Placing Wall Fixtures Continuously from Bottom-Left ---")

        # 1. SETUP: Load all wall fixtures into a single queue
        wall_fixtures_config = self.fixtures.get("wall_fixtures", {})
        master_queue = collections.deque()
        for name, count in wall_fixtures_config.items():
            if count > 0:
                master_queue.extend([(name, 1)] * count)
        
        if not master_queue:
            print("  -> No wall fixtures specified for placement.")
            return

        mirror_config = self.fixtures.get("mirror_selection", {})
        selected_mirror_name = next((name for name, selected in mirror_config.items() if selected > 0), "mirror")
        
        # 2. IDENTIFY BOH "STOP" ZONES
        boh_entities = []
        for entity in self.msp.query('INSERT'):
            # This logic reliably identifies BOH fixtures by their type in fixture_dict
            block_name_upper = entity.dxf.name.upper()
            best_match_key = ""
            for key in self.fixture_dict.keys():
                sanitized_key = key.upper().replace(" ", "_")
                if block_name_upper.startswith(sanitized_key):
                    if len(key) > len(best_match_key):
                        best_match_key = key
            if best_match_key and self.fixture_dict[best_match_key].get("type") == 'boh':
                boh_entities.append(entity)

        stop_bboxes = []
        if boh_entities:
            boh_cluster_bbox = extents(boh_entities)
            # Create a larger "stop" zone around the BOH with a buffer
            buffer = 500.0 # Stop 500mm away from the BOH area
            stop_bboxes.append((
                boh_cluster_bbox.extmin.x - buffer,
                boh_cluster_bbox.extmin.y - buffer,
                boh_cluster_bbox.extmax.x + buffer,
                boh_cluster_bbox.extmax.y + buffer
            ))
            print(f"  -> BOH stop zone defined. Placement will halt near this area.")
        
        # 3. GET PERIMETER PATH starting from bottom-left
        # Helper to get the bottom-left starting corner
        def _get_reordered_corners_bottom_left():
            corners = self.cvc.corners
            if not corners: return []
            start_idx = min(range(len(corners)), 
                            key=lambda i: math.hypot(corners[i][0] - self.cvc.min_x, corners[i][1] - self.cvc.min_y))
            reordered = corners[start_idx:] + corners[:start_idx]
            # Ensure path is CCW (up the left wall)
            signed_area = 0.5 * sum(x1*y2 - x2*y1 for (x1, y1), (x2, y2) in zip(reordered, reordered[1:] + [reordered[0]]))
            if signed_area < 0:
                reordered = reordered[0:1] + reordered[1:][::-1]
            return reordered

        ordered_corners = _get_reordered_corners_bottom_left()
        perimeter_path = []
        for i in range(len(ordered_corners)):
            p1 = Vec2(ordered_corners[i])
            p2 = Vec2(ordered_corners[(i + 1) % len(ordered_corners)])
            if p1.distance(p2) > 100:
                perimeter_path.append((p1, p2))

        # 4. CONTINUOUS PLACEMENT LOOP
        margin_from_wall = 10.0
        
        for segment_start, segment_end in perimeter_path:
            if not master_queue: break

            segment_vector = (segment_end - segment_start).normalize()
            segment_length = segment_start.distance(segment_end)
            wall_angle_deg = math.degrees(segment_vector.angle)
            
            inward_normal = segment_vector.orthogonal()
            if not self.floorplan_polygon.contains(Point(segment_start + inward_normal * 10)):
                inward_normal = -inward_normal

            cursor = 50.0
            while master_queue:
                # Load the next pair of fixtures
                try:
                    hybrid_name, _ = master_queue[0]
                    hybrid_fxtr = Fixture.Fixture(hybrid_name, self.fixture_dict[hybrid_name]["path"])
                    mirror_fxtr = Fixture.Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
                except (KeyError, ValueError):
                    master_queue.popleft() # Skip invalid fixture
                    continue
                
                pair_width = hybrid_fxtr.width + mirror_fxtr.width
                if cursor + pair_width > segment_length - 50.0:
                    break # Not enough space on this segment, move to the next

                # --- Validate BOTH fixtures before placing either ---
                
                # Hybrid validation
                center_h = segment_start + segment_vector * (cursor + hybrid_fxtr.width / 2) + inward_normal * (margin_from_wall + hybrid_fxtr.height / 2)
                aabb_h = self._get_fixture_aabb(hybrid_fxtr, center_h, wall_angle_deg)
                
                # Mirror validation
                center_m = segment_start + segment_vector * (cursor + hybrid_fxtr.width + mirror_fxtr.width / 2) + inward_normal * (margin_from_wall + mirror_fxtr.height / 2)
                aabb_m = self._get_fixture_aabb(mirror_fxtr, center_m, wall_angle_deg)

                # Check for collisions with BOH stop zone
                if any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in stop_bboxes) or \
                   any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in stop_bboxes):
                    print("  -> Halting placement: Approaching BOH zone.")
                    # Use a goto-like mechanism to break out of all loops
                    master_queue.clear() # Empty the queue to stop all further processing
                    break

                # Check for collisions with other placed fixtures
                is_hybrid_blocked = any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)
                is_mirror_blocked = any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                if not is_hybrid_blocked and not is_mirror_blocked:
                    # If both are clear, place them
                    self._validate_and_place_at_point(hybrid_fxtr, center_h, wall_angle_deg, placed_bboxes)
                    self._validate_and_place_at_point(mirror_fxtr, center_m, wall_angle_deg, placed_bboxes)
                    print(f"    -> Placed pair: '{hybrid_fxtr.name}' & '{mirror_fxtr.name}'")
                    master_queue.popleft() # Remove the placed hybrid
                    cursor += pair_width # Advance the cursor
                else:
                    # If the spot is blocked, just advance the cursor to try the next spot
                    cursor += 100.0
            
            if not master_queue: break # Exit outer loop if queue is empty

        # 5. FINAL REPORT
        if master_queue:
            print(f"\n--- ⚠️ Finished with {len(master_queue)} unplaced wall fixtures. ---")
        else:
            print("\n--- ✅ Finished Continuous Wall Fixture Placement Successfully ---")

    def _get_fixture_aabb(self, fixture, target_center, angle_deg):
        """Helper to quickly get the AABB of a fixture at a potential location."""
        from ezdxf.math import Matrix44, Vec2, BoundingBox2d
        import math
        local_center = fixture.bounding_box.center
        transform = Matrix44.chain(
            Matrix44.translate(-local_center.x, -local_center.y, 0),
            Matrix44.z_rotate(math.radians(angle_deg)),
            Matrix44.translate(target_center.x, target_center.y, 0)
        )
        world_corners = list(transform.transform_vertices(fixture.bounding_box.rect_vertices()))
        return BoundingBox2d(world_corners)