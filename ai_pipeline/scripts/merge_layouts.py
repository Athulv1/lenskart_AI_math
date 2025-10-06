import json
import sys
import math
import os
from shapely.geometry import Polygon, LineString, MultiPolygon
from shapely.ops import unary_union
import ezdxf
from ezdxf.enums import TextEntityAlignment
from ezdxf.addons import Importer
from ezdxf.math import Vec2, BoundingBox2d, Matrix44
from typing import List, Tuple, Dict, Any

# ==============================================================================
# Helper functions (Unchanged)
# ==============================================================================
def rotate_xy(x: float, y: float, cx: float, cy: float, theta_deg: float) -> Tuple[float, float]:
    th = math.radians(theta_deg)
    ct, st = math.cos(th), math.sin(th)
    dx, dy = x - cx, y - cy
    rx = dx * ct - dy * st + cx
    ry = dx * st + dy * ct + cy
    return rx, ry

def rotate_layout(
    polygon_coords: List[Tuple[float, float]],
    fixtures: List[Dict[str, Any]],
    angle_deg: float
) -> Tuple[List[Tuple[float, float]], List[Dict[str, Any]]]:
    if not polygon_coords:
        return [], fixtures
        
    poly = Polygon(polygon_coords)
    centroid_x, centroid_y = poly.centroid.x, poly.centroid.y
    
    rotated_polygon = [rotate_xy(x, y, centroid_x, centroid_y, angle_deg) for x, y in polygon_coords]
    rotated_fixtures = []
    for fixture in fixtures:
        f_center_x, f_center_y = fixture['center_mm']['x'], fixture['center_mm']['y']
        new_center_x, new_center_y = rotate_xy(f_center_x, f_center_y, centroid_x, centroid_y, angle_deg)
        rotated_fixture = fixture.copy()
        rotated_fixture['center_mm'] = {'x': new_center_x, 'y': new_center_y}
        rotated_fixture['rotation_deg'] = (fixture.get('rotation_deg', 0) + angle_deg) % 360
        rotated_fixtures.append(rotated_fixture)
        
    return rotated_polygon, rotated_fixtures

# ==============================================================================
# Robust Polygon Extraction Logic (Unchanged)
# ==============================================================================
def extract_floor_polygon(wall_data):
    wall_segments = wall_data.get('walls', [])
    if not wall_segments:
        raise ValueError("No wall segments found in the wall JSON.")
    print(f"🏗️ Processing {len(wall_segments)} wall segments with buffer strategy...")
    lines = []
    for wall in wall_segments:
        start_x, start_z = wall['start'][0] * 1000, wall['start'][2] * 1000
        end_x, end_z = wall['end'][0] * 1000, wall['end'][2] * 1000
        lines.append(LineString([(start_x, start_z), (end_x, end_z)]))
    if not lines:
        raise ValueError("Could not create any lines from the wall data.")
    buffer_amount = 1.0 
    buffered_lines = [line.buffer(buffer_amount) for line in lines]
    merged_shape = unary_union(buffered_lines)
    if isinstance(merged_shape, MultiPolygon):
        main_polygon = max(merged_shape.geoms, key=lambda p: p.area)
    elif isinstance(merged_shape, Polygon):
        main_polygon = merged_shape
    else:
        raise ValueError("Could not form a valid polygon shape from the walls.")
    boundary_points = list(main_polygon.exterior.coords)
    min_x = min(p[0] for p in boundary_points)
    min_y = min(p[1] for p in boundary_points)
    transformed_coords = [(x - min_x, y - min_y) for x, y in boundary_points]
    print(f"✅ Successfully identified outer perimeter with {len(transformed_coords)} corners.")
    return transformed_coords

# ==============================================================================
# MODIFIED Merging Logic
# ==============================================================================
def merge_layouts(wall_json_path, fixture_json_path, output_json_path):
    with open(wall_json_path, 'r') as f:
        wall_data = json.load(f)
    with open(fixture_json_path, 'r') as f:
        fixture_data = json.load(f)

    # Step 1: Extract the raw, potentially rotated polygon
    floor_polygon_coords_raw = extract_floor_polygon(wall_data['room_measurements'])

    # --- NEW FIX STARTS HERE ---
    # Step 2: Straighten the walls FIRST by applying the inverse rotation from the JSON
    rotation_angle = wall_data.get("rotation", 0.0)
    if rotation_angle != 0.0:
        print(f"🔄 Wall data has a rotation of {rotation_angle}°. Applying inverse rotation to straighten walls...")
        # We apply the NEGATIVE of the angle to straighten it.
        # The `rotate_layout` function needs a dummy fixtures list, so we provide an empty one `[]`.
        straight_polygon_coords, _ = rotate_layout(floor_polygon_coords_raw, [], -rotation_angle)
        floor_polygon_coords = straight_polygon_coords
    else:
        floor_polygon_coords = floor_polygon_coords_raw
    # --- NEW FIX ENDS HERE ---

    # Step 3: Now that the walls are straight, calculate bounds and scale fixtures
    min_x, min_y, max_x, max_y = Polygon(floor_polygon_coords).bounds
    real_width, real_height = max_x - min_x, max_y - min_y

    placed_fixtures = []
    for fixture in fixture_data['room_measurements']['fixtures']:
        placed_fixtures.append({
            "name": fixture.get('type', fixture.get('name', 'unknown_fixture')),
            "center_mm": {
                "x": min_x + (fixture['center']['x'] * real_width),
                "y": min_y + (fixture['center']['y'] * real_height)
            },
            "size_mm": {
                "width": fixture['size']['width'] * real_width,
                "height": fixture['size']['height'] * real_height
            },
            "rotation_deg": fixture.get('rotation', 0)
        })
    
    # The final rotation step is no longer needed as we've aligned everything
    # to a 90-degree orientation from the start.

    final_layout = wall_data.copy()
    final_layout['project_name'] += " (with Fixtures)"
    final_layout['room_measurements']['placed_fixtures'] = placed_fixtures
    final_layout['room_measurements']['floor_polygon_mm'] = floor_polygon_coords

    with open(output_json_path, 'w') as f:
        json.dump(final_layout, f, indent=2)
    print(f"\nSuccessfully merged layout saved to: {output_json_path}")
    return final_layout

# (The rest of the file - get_fixture_dict, find_fixture_in_dict, DXF functions, etc. - remains unchanged)
# ... [rest of the file is the same as the previous correct version] ...
# ==============================================================================
def get_fixture_dict():
    base_path = "/home/athul/json"
    return {
        "jj_fixture_different_large": {"name": "jj_fixture_different_large", "path": f"{base_path}/assets/wall_fixtures/jj_fixture_different_large.dxf", "type": "wall"},
        "jj_fixture_different_medium": {"name": "jj_fixture_different_medium", "path": f"{base_path}/assets/wall_fixtures/jj_fixture_different_medium.dxf", "type": "wall"},
        "jj_fixture_large": {"name": "jj_fixture_large", "path": f"{base_path}/assets/wall_fixtures/jj_fixture_large.dxf", "type": "wall"},
        "jj_fixture_medium": {"name": "jj_fixture_medium", "path": f"{base_path}/assets/wall_fixtures/jj_fixture_medium.dxf", "type": "wall"},
        "jj_super_hybrid_large": {"name": "jj_super_hybrid_large", "path": f"{base_path}/assets/wall_fixtures/jj_super_hybrid_large.dxf", "type": "wall"},
        "jj_super_hybrid_medium": {"name": "jj_super_hybrid_medium", "path": f"{base_path}/assets/wall_fixtures/jj_super_hybrid_medium.dxf", "type": "wall"},
        "jj_super_hybrid_small": {"name": "jj_super_hybrid_small", "path": f"{base_path}/assets/wall_fixtures/jj_super_hybrid_small.dxf", "type": "wall"},
        "mirror_different": {"name": "mirror_different", "path": f"{base_path}/assets/wall_fixtures/mirror_different.dxf", "type": "wall"},
        "mirror": {"name": "mirror", "path": f"{base_path}/assets/wall_fixtures/mirror.dxf", "type": "wall"},
        "pick_up_counter": {"name": "pick_up_counter", "path": f"{base_path}/assets/wall_fixtures/pick_up_counter.dxf", "type": "wall"},
        "vc_fixture_large": {"name": "vc_fixture_large", "path": f"{base_path}/assets/wall_fixtures/vc_fixture_large.dxf", "type": "wall"},
        "vc_fixture_medium": {"name": "vc_fixture_medium", "path": f"{base_path}/assets/wall_fixtures/vc_fixture_medium.dxf", "type": "wall"},
        "window_1_section": {"name": "window_1_section", "path": f"{base_path}/assets/wall_fixtures/window_1_section.dxf", "type": "wall"},
        "window_3_section": {"name": "window_3_section", "path": f"{base_path}/assets/wall_fixtures/window_3_section.dxf", "type": "wall"},
        "with_screen": {"name": "with_screen", "path": f"{base_path}/assets/wall_fixtures/with_screen.dxf", "type": "wall"},
        "AR": {"name": "AR", "path": f"{base_path}/assets/floor/AR.dxf", "type": "floor"},
        "Blue_zero": {"name": "Blue_zero", "path": f"{base_path}/assets/floor/Blue_zero.dxf", "type": "floor"},
        "Discussion_table_large": {"name": "Discussion_table_large", "path": f"{base_path}/assets/floor/Discussion_table_large.dxf", "type": "floor"},
        "Discussion_table_medium": {"name": "Discussion_table_medium", "path": f"{base_path}/assets/floor/Discussion_table_medium.dxf", "type": "floor"},
        "Discussion_table_small": {"name": "Discussion_table_small", "path": f"{base_path}/assets/floor/Discussion_table_small.dxf", "type": "floor"},
        "drop_box": {"name": "drop_box", "path": f"{base_path}/assets/floor/drop_box.dxf", "type": "floor"},
        "Euro_centre": {"name": "Euro_centre", "path": f"{base_path}/assets/floor/Euro_centre.dxf", "type": "floor"},
        "Lensbar": {"name": "Lensbar", "path": f"{base_path}/assets/floor/Lensbar.dxf", "type": "floor"},
        "Lensometer_large": {"name": "Lensometer_large", "path": f"{base_path}/assets/floor/Lensometer_large.dxf", "type": "floor"},
        "Lensometer_medium": {"name": "Lensometer_medium", "path": f"{base_path}/assets/floor/Lensometer_medium.dxf", "type": "floor"},
        "Lensometer_small": {"name": "Lensometer_small", "path": f"{base_path}/assets/floor/Lensometer_small.dxf", "type": "floor"},
        "QMS_desk": {"name": "QMS_desk", "path": f"{base_path}/assets/floor/QMS_desk.dxf", "type": "floor"},
        "sofa": {"name": "sofa", "path": f"{base_path}/assets/floor/sofa.dxf", "type": "floor"},
        "Standing_table": {"name": "Standing_table", "path": f"{base_path}/assets/floor/Standing_table.dxf", "type": "floor"},
        "Dining_Table_large": {"name": "Dining_Table_large", "path": f"{base_path}/assets/boh_furniture/Dining_Table_large.dxf", "type": "boh"},
        "Dining_Table_medium": {"name": "Dining_Table_medium", "path": f"{base_path}/assets/boh_furniture/Dining_Table_medium.dxf", "type": "boh"},
        "pickup_storage_900": {"name": "pickup_storage_900", "path": f"{base_path}/assets/boh_furniture/pickup_storage_900.dxf", "type": "boh"},
        "pickup_storage_1200": {"name": "pickup_storage_1200", "path": f"{base_path}/assets/boh_furniture/pickup_storage_1200.dxf", "type": "boh"},
        "pickup_table": {"name": "pickup_table", "path": f"{base_path}/assets/boh_furniture/pickup_table.dxf", "type": "boh"},
        "QC_table_large": {"name": "QC_table_large", "path": f"{base_path}/assets/boh_furniture/QC_table_large.dxf", "type": "boh"},
        "QC_table_medium": {"name": "QC_table_medium", "path": f"{base_path}/assets/boh_furniture/QC_table_medium.dxf", "type": "boh"},
        "Repair_Table_large": {"name": "Repair_Table_large", "path": f"{base_path}/assets/boh_furniture/Repair_Table_large.dxf", "type": "boh"},
        "Repair_Table_medium": {"name": "Repair_Table_medium", "path": f"{base_path}/assets/boh_furniture/Repair_Table_medium.dxf", "type": "boh"},
        "staff_rack": {"name": "staff_rack", "path": f"{base_path}/assets/boh_furniture/staff_rack.dxf", "type": "boh"},
        "storage_rack": {"name": "storage_rack", "path": f"{base_path}/assets/boh_furniture/storage_rack.dxf", "type": "boh"},
        "ups_rack": {"name": "ups_rack", "path": f"{base_path}/assets/boh_furniture/ups_rack.dxf", "type": "boh"},
        "water_dispenser": {"name": "water_dispenser", "path": f"{base_path}/assets/boh_furniture/water_dispenser.dxf", "type": "boh"},
        "screen_43": {"name": 'screen_43', "path": f"{base_path}/assets/screen/screen_43.dxf", "type": "screen"},
        "screen_49": {"name": 'screen_49', "path": f"{base_path}/assets/screen/screen_49.dxf", "type": "screen"},
        "screen_55": {"name": 'screen_55', "path": f"{base_path}/assets/screen/screen_55.dxf", "type": "screen"},
        "screen_65": {"name": 'screen_65', "path": f"{base_path}/assets/screen/screen_65.dxf", "type": "screen"},
        "Clinic_with_sink": {"name": "Clinic_with_sink", "path": f"{base_path}/assets/clinic/Clinic_with_sink.dxf", "type": "clinic"},
        "Clinic_regular": {"name": "Clinic_regular", "path": f"{base_path}/assets/clinic/Clinic_regular.dxf", "type": "clinic"},
        "ROC_clinic": {"name": "ROC_clinic", "path": f"{base_path}/assets/clinic/ROC_clinic.dxf", "type": "clinic"},
        "pos_with_screen_large": {"name": "pos_with_screen_large", "path": f"{base_path}/assets/pos/pos_with_screen_large.dxf", "type": "pos"},
        "pos_with_screen_medium": {"name": "pos_with_screen_medium", "path": f"{base_path}/assets/pos/pos_with_screen_medium.dxf", "type": "pos"},
        "pos_without_screen": {"name": "pos_without_screen", "path": f"{base_path}/assets/pos/pos_without_screen.dxf", "type": "pos"},
        "large_bench" : {"name": "large_bench", "path": f"{base_path}/assets/loose/large_bench.dxf", "type": "loose"},
    }

def find_fixture_in_dict(json_fixture_name: str, fixture_dict: Dict) -> Dict:
    NAME_MAPPINGS = {
        "vc_repair_table": "Repair_Table_medium", "sc_front_desk": "pos_without_screen",
        "nummi_bilen": "jj_fixture_medium", "soins_lens_large": "Lensbar",
        "vasagle_storage_cabinet": "storage_rack", "wascon_desk_meallier": "QC_table_medium",
        "screen_55": "screen_55", "euro_ccvlite": "Euro_centre", "staff_rack": "staff_rack",
        "vc_future_medium": "vc_fixture_medium", "jjke_lens": "jj_fixture_medium",
        "pos_Noire_medium": "pos_with_screen_medium", "mirror_different": "mirror_different",
        "jjtensoldfone_large": "jj_fixture_large", "mirror_large": "mirror",
        "euro_centre": "Euro_centre", "seimony_lens": "Lensbar",
        "euro_csinle": "Euro_centre", "accuairte": "Lensometer_small", "large_bench": "large_bench",
    }
    mapped_name = NAME_MAPPINGS.get(json_fixture_name)
    if mapped_name and mapped_name in fixture_dict:
        return fixture_dict[mapped_name]
    for key, value in fixture_dict.items():
        if key.lower() == json_fixture_name.lower():
            return value
    return None

def place_fixture_dxf(doc, msp, fixture_info: Dict, insert_point: tuple, rotation: float, fixture_counter: dict):
    try:
        src_doc = ezdxf.readfile(fixture_info['path'])
    except IOError:
        print(f"  ❌ ERROR: Cannot read fixture file: {fixture_info['path']}")
        return False
    importer = Importer(src_doc, doc)
    name = fixture_info['name']
    fixture_counter[name] = fixture_counter.get(name, 0) + 1
    safe_block_name = f"{name.upper().replace(' ', '_')}_{fixture_counter[name]}"
    try:
        source_bbox = ezdxf.bbox.extents(src_doc.modelspace(), fast=True)
        base_pt = source_bbox.center
    except:
        base_pt = (0, 0)
    block = doc.blocks.new(name=safe_block_name, base_point=base_pt)
    for entity in src_doc.modelspace():
        try:
            block.add_entity(entity.copy())
        except ezdxf.DXFStructureError:
            continue
    importer.import_tables()
    importer.import_blocks(src_doc.blocks.block_names())
    msp.add_blockref(safe_block_name, insert_point, dxfattribs={"rotation": rotation})
    return True

def draw_rectangle_fixture(msp, center, width, height, angle, fixture_name):
    points = [(-width/2, -height/2), (width/2, -height/2), (width/2, height/2), (-width/2, height/2)]
    transform = Matrix44.chain(
        Matrix44.z_rotate(math.radians(angle)),
        Matrix44.translate(center[0], center[1], 0)
    )
    msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "Fixtures"}).transform(transform)
    msp.add_text(
        text=fixture_name,
        dxfattribs={'layer': 'FixtureLabels', 'height': min(width, height) * 0.2, 'rotation': angle}
    ).set_placement(center, align=TextEntityAlignment.MIDDLE_CENTER)

def create_dxf_layout(layout_data, output_dxf_path):
    print(f"\n🏗️  Creating DXF layout with enhanced coordinate system...")
    fixture_dict = get_fixture_dict() 
    doc = ezdxf.new()
    msp = doc.modelspace()
    doc.layers.add("FloorPlan", color=1)
    doc.layers.add("Fixtures", color=3)
    doc.layers.add("FixtureLabels", color=2)
    floor_polygon = layout_data['room_measurements']['floor_polygon_mm']
    msp.add_lwpolyline(floor_polygon, close=True, dxfattribs={"layer": "FloorPlan"})
    print(f"🏗️ Floor polygon coordinates: {len(floor_polygon)} points")
    print(f"🎯 Wall bounds: X({min(p[0] for p in floor_polygon):.0f} to {max(p[0] for p in floor_polygon):.0f}), Y({min(p[1] for p in floor_polygon):.0f} to {max(p[1] for p in floor_polygon):.0f})")
    
    real, rects = 0, 0
    fixture_counter = {}
    for data in layout_data['room_measurements']['placed_fixtures']:
        name, center = data['name'], (data['center_mm']['x'], data['center_mm']['y'])
        width, height, angle = data['size_mm']['width'], data['size_mm']['height'], data['rotation_deg']
        print(f"🎯 Placing {name} at ({center[0]:.0f}, {center[1]:.0f}) size:{width:.0f}x{height:.0f} rot:{angle:.0f}°")
        matched_info = find_fixture_in_dict(name, fixture_dict)
        if matched_info:
            if place_fixture_dxf(doc, msp, matched_info, center, angle, fixture_counter):
                real += 1
                print(f"  ✅ Placed actual fixture: {name} -> {matched_info['name']}")
            else:
                rects += 1
                print(f"  ⚠️  Failed to place DXF for {name}, using rectangle")
                draw_rectangle_fixture(msp, center, width, height, angle, name)
        else:
            rects += 1
            print(f"  ⚠️  No DXF found for '{name}', using rectangle")
            draw_rectangle_fixture(msp, center, width, height, angle, name)
    doc.saveas(output_dxf_path)
    print("\n📊 DXF Generation Summary:")
    print(f"  • Actual fixtures placed: {real}")
    print(f"  • Rectangle fallbacks: {rects}")
    print(f"💾 DXF layout saved to: {output_dxf_path}")

if __name__ == "__main__":
    if len(sys.argv) == 4:
        wall_file, fixture_file, output_json_file = sys.argv[1], sys.argv[2], sys.argv[3]
    else:
        wall_file, fixture_file = "wall_layout.json", "fixture_layout.json"
        output_dir = "output"
        if not os.path.exists(output_dir): os.makedirs(output_dir)
        output_json_file = os.path.join(output_dir, "merged_floorplan.json")
        print("Using default files:")
        print(f"  Wall file: {wall_file}\n  Fixture file: {fixture_file}\n  Output JSON: {output_json_file}")

    try:
        merged_data = merge_layouts(wall_file, fixture_file, output_json_file)
        import glob
        base_dxf_name = os.path.splitext(output_json_file)[0]
        dxf_output_path = f"{base_dxf_name}.dxf"
        create_dxf_layout(merged_data, dxf_output_path)
    except FileNotFoundError as e:
        print(f"Error: Input file not found - {e}")
    except (ValueError, KeyError, Exception) as e:
        print(f"Error: Could not process file. Check format. Details: {e}")