import subprocess
import sys
import os
import logging
import traceback
from typing import List, Dict, Any, Optional, Tuple
from . import Fixture
from . import CV_Controller as cvCon
from typing import List, Tuple
import uuid 
import ezdxf # type: ignore
import json
from ezdxf import units # type: ignore
from ezdxf.enums import InsertUnits # type: ignore
from ezdxf.math import Vec2, Vec3, Matrix44, BoundingBox2d # type: ignore
from ezdxf.addons import Importer # type: ignore
from ezdxf.bbox import extents # type: ignore 
from ezdxf.colors import rgb2int # type: ignore
import math
from shapely.geometry import Point, Polygon, LinearRing, LineString, box # type: ignore
from shapely.ops import linemerge, polygonize, unary_union     # type: ignore
import shapely.affinity as affinity # type: ignore
import collections
import itertools
import random




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

        # BOH Presets
        "basic_boh_preset_1": {
            "name": "basic_boh_preset_1",
            "path": "assets/boh_presets/basic_boh_preset_1.dxf",
            "type": "boh_preset"
        },
        "small_basic_boh": {
            "name": "small_basic_boh",
            "path": "assets/boh_presets/small_basic_boh.dxf",
            "type": "boh_preset"
        },
        "boh_vertical_horizontal_preset_basic": {
            "name": "boh_vertical_horizontal_preset_basic",
            "path": "assets/boh_presets/boh_vertical_horizontal_preset_basic.dxf",
            "type": "boh_preset"
        },
        "medium_basic_boh": {
            "name": "medium_basic_boh",
            "path": "assets/boh_presets/medium_basic_boh.dxf",
            "type": "boh_preset"
        },
        "Pick_up_window": {
            "name": "Pick_up_window",
            "path": "assets/boh_presets/Pick_up_window.dxf",
            "type": "pickup_window"
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
        "Door_Left" : {
            "name": "Door_Left",
            "path": "assets/loose/Door_Left.dxf",
            "type": "loose"
        },
        "Door_Right" : {
            "name": "Door_Right",
            "path": "assets/loose/Door_Right.dxf",
            "type": "loose"
        },
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

        # --- State variables that were in DossierParser ---
        self.fixtures = {} # This will be built by the new master method
        self.merch_data = {}
        self.parsed_counts = {}
        self.family_totals = {}
        # --- End of DossierParser state variables ---

        self.sofa_placed = False
        self.fixture_counter = {}
        self.back_room_location = None
        
        self.safe_types = {
            "LINE", "LWPOLYLINE", "CIRCLE", "ARC", "TEXT", "MTEXT",
            "ELLIPSE", "SPLINE", "SOLID", "INSERT", "ATTDEF"
        }

    # ==============================================================================
    # --- START: ALL METHODS FROM DossierParser ARE NOW PART OF DXF_Controller ---
    # ==============================================================================

    def _parse_json_data(self, merch_data: Dict[str, str]) -> Dict[str, int]:
        """
        Parses the flat dictionary data from the 'merch_mix_max' JSON object.
        """
        parsed_counts = {}
        ignore_keys = ["proto", "Shop_id", "Header", "Reading_Glasses", "Total"]
        for key, count_str in merch_data.items():
            if key not in ignore_keys:
                category = key.replace('_', ' ')
                try:
                    parsed_counts[category] = math.ceil(float(count_str))
                except (ValueError, IndexError):
                    parsed_counts[category] = 0
        return parsed_counts

    def _map_and_sum_wall_fixture_families(self) -> Dict[str, int]:
        """
        Applies new conditional mapping rules to sum counts into wall fixture families.
        (This function remains unchanged)
        """
        jj_eye_sun_sum = self.parsed_counts.get("JJ Eye", 0) + self.parsed_counts.get("JJ Sun", 0)
        jj_family_type = "jj_super_hybrid_family" if jj_eye_sun_sum <= 3 else "jj_fixture_family"
        print(f"  -> JJ Family Type set to: '{jj_family_type}'")

        CATEGORY_MAP = {
            "Branded Eye": jj_family_type, "Branded Sun": jj_family_type,
            "JJ Eye": jj_family_type, "JJ Sun": jj_family_type,
            "OD": jj_family_type, "LPL": jj_family_type,
            "VC Eye": "vc_fixture_family", "VC Sun": "vc_fixture_family",
            "VC Kids": "vc_fixture_family", "LK Air": "vc_fixture_family",
            "Reading Glasses": "vc_fixture_family",
            "CL": jj_family_type,
            "Tentpole": "floor", "Hustlr": "floor"
        }
        family_totals = collections.defaultdict(int)
        for category, count in self.parsed_counts.items():
            if category in CATEGORY_MAP and CATEGORY_MAP[category] != "floor":
                family_totals[CATEGORY_MAP[category]] += count
        return dict(family_totals)

    def generate_fixture_counts(self) -> Tuple[Dict[str, int], Dict[str, int]]:
        """
        Main public method to generate the INITIAL counts from the dossier.
        (This function remains unchanged)
        """
        print("--- Generating INITIAL Fixture Counts from DossierParser instance ---")
        floor_fixtures = self._setup_floor_fixtures()
        print("✅ Dossier INITIAL COUNTING Complete.")
        return self.family_totals, floor_fixtures
    
    def _setup_floor_fixtures(self) -> Dict[str, int]:
        """
        Calculates all dynamically generated floor fixtures, including Euro_centre
        and now also Standing_table.
        """
        # --- This part for Euro_centre remains the same ---
        tentpole_count = self.parsed_counts.get("Tentpole", 0)
        hustlr_count = self.parsed_counts.get("Hustlr", 0)
        total_racks = tentpole_count + hustlr_count
        euros_for_racks = math.ceil(total_racks / 2.0)
        
        initial_euro_count = int(euros_for_racks)
        if total_racks > 0 and initial_euro_count == 0:
            initial_euro_count = 1
        print(f"  -> Initial Euro Centre count set to {initial_euro_count} (for Tentpole/Hustlr).")
        # --- This is the new part for Standing_table ---
        # Call our new function to get the dynamic count
        standing_table_count = self._calculate_standing_tables()

        return {
            "Euro_centre": initial_euro_count,
            "Standing_table": standing_table_count
        }
    
    
    def calculate_greeter_to_standing_table_zone(self) -> Optional[Polygon]:
        """
        Calculates the usable area between the bottom of the standing tables and the top of the QMS/greeter desks.

        This function identifies the collective bounding boxes of both fixture groups,
        creates a slicing box representing the vertical space between them, and intersects
        it with the main floorplan polygon to find the actual area.

        Returns:
            A Shapely Polygon representing the valid placement zone, or None if the zone
            cannot be calculated (e.g., fixtures are missing or space is invalid).
        """
        from ezdxf.bbox import extents
        from shapely.geometry import box

        print("\n--- 📐 Calculating Zone Between Greeter and Standing Tables ---")

        # --- 1. Find Anchor Fixtures ---
        standing_table_entities = [e for e in self.msp.query('INSERT') if "STANDING_TABLE" in e.dxf.name.upper()]
        qms_entities = [e for e in self.msp.query('INSERT') if "QMS_DESK" in e.dxf.name.upper()]

        if not standing_table_entities:
            print("  -> ⚠️ FAILED: Could not find any 'Standing Table' fixtures to define the top boundary.")
            return None
        if not qms_entities:
            print("  -> ⚠️ FAILED: Could not find any 'QMS Desk' fixtures to define the bottom boundary.")
            return None

        # --- 2. Define Vertical Boundaries ---
        # The top of our zone is the lowest y-coordinate of the standing table group.
        standing_tables_bbox = extents(standing_table_entities)
        top_boundary_y = standing_tables_bbox.extmin.y

        # The bottom of our zone is the highest y-coordinate of the QMS/greeter group.
        qms_bbox = extents(qms_entities)
        bottom_boundary_y = qms_bbox.extmax.y
        
        # Validate that there is positive space between the two groups.
        if bottom_boundary_y >= top_boundary_y:
            print("  -> ⚠️ FAILED: The zone is invalid because the QMS desks are above or overlapping the standing tables.")
            return None
            
        print(f"  -> Zone boundaries defined: Top at y={top_boundary_y:.0f}, Bottom at y={bottom_boundary_y:.0f}")

        # --- 3. Create Slicing Box and Intersect with Floorplan ---
        # The horizontal boundaries are simply the extents of the entire room.
        slicing_box = box(self.cvc.min_x, bottom_boundary_y, self.cvc.max_x, top_boundary_y)
        
        # Intersecting the slicing box with the floorplan gives us the actual, usable area.
        zone_polygon = self.floorplan_polygon.intersection(slicing_box)

        if zone_polygon.is_empty:
            print("  -> ⚠️ FAILED: The calculated zone resulted in an empty area.")
            return None
        
        print(f"  -> ✅ Successfully calculated the placement zone. Area: {zone_polygon.area:,.0f} mm²")
        return zone_polygon


    def draw_greeter_to_standing_table_zone(self):
        """
        Calculates and then draws the boundary of the zone between the greeter
        and standing tables for visual debugging.

        The outline is drawn on a dedicated 'DEBUG' layer with a bright color.
        """
        print("\n--- 🎨 Drawing Greeter-to-Standing-Table Zone for Validation ---")
        
        # 1. Call the calculation function to get the polygon
        zone_polygon = self.calculate_greeter_to_standing_table_zone()

        # 2. Check if a valid polygon was returned
        if zone_polygon and not zone_polygon.is_empty:
            
            # 3. Define a new layer for the debug drawing
            layer_name = "DEBUG_GREET_TO_STAND_ZONE"
            if layer_name not in self.doc.layers:
                self.doc.layers.add(
                    name=layer_name,
                    color=2  # ACI color 2 is Yellow, which is highly visible
                )

            # 4. Get the coordinates of the polygon's boundary
            zone_boundary_coords = list(zone_polygon.exterior.coords)

            # 5. Add the polygon outline to the modelspace
            self.msp.add_lwpolyline(
                zone_boundary_coords,
                close=True,
                dxfattribs={"layer": layer_name, "lineweight": 35} # Make the line slightly thicker for visibility
            )
            
            print(f"  -> ✅ Zone boundary drawn on layer '{layer_name}'.")
        
        else:
            print("  -> ⚠️ SKIPPED DRAWING: The placement zone could not be calculated.")


    def display_count_calc(self, floor_area: float, wall_length: float, display_count: int) -> dict:
        """
        Calculates the optimal mix of floor and wall fixtures based on available space.

        This function takes the total floor area, available retail wall length, and the
        total number of displays required, then iteratively adjusts the counts of
        different fixture types (Euro centers, large/medium wall displays, mirrors)
        to find a valid layout that fits within the given constraints.

        Args:
            floor_area (float): The total available floor area in square millimeters.
            wall_length (float): The total available retail wall length in millimeters.
            display_count (int): The total number of display fixtures required.

        Returns:
            dict: A dictionary containing the calculated counts for each fixture type,
                  e.g., {'floor_fixtures': 3, 'large_wall_fixtures': 7,
                         'medium_wall_fixtures': 2, 'mirrors': 9, 'valid': True}
        """

        # --- DYNAMIC INITIALIZATION (Values are now calculated inside) ---
        print("\n--- Dynamically calculating inputs for fixture mix analysis ---")
        
        # 1. Get Floor Area in mm^2
        # MODIFIED: Calculate the area of the zone between the greeter and standing tables.
        zone_polygon = self.calculate_greeter_to_standing_table_zone()
        if zone_polygon and not zone_polygon.is_empty:
            floor_area = zone_polygon.area
            print("  -> Using the specific area between greeter and standing tables for calculation.")
        else:
            print("  -> ⚠️ WARNING: Could not calculate greeter-to-standing-table zone. Falling back to total floorplan area.")
            floor_area = self.floorplan_polygon.area

        print(f"  -> Floor Area for Calculation: {floor_area:,.0f} mm^2")

        # # 2. Get Wall Length
        # left_wall_data = self.get_retail_wall_data(side='left')
        # right_wall_data = self.get_retail_wall_data(side='right')
        # left_wall_length = left_wall_data["total_length"]
        # right_wall_length = right_wall_data["total_length"]
        # wall_length = left_wall_length + right_wall_length
        # print(f"  -> Total Retail Wall Length: {wall_length:.0f} mm")

        # 3. Get Display Count
        display_categories = [
            "Branded Eye", "Branded Sun", "JJ Eye", "JJ Sun", "OD", "LPL",
            "VC Eye", "VC Sun", "VC Kids", "LK Air", "Reading Glasses", "CL",
            "Tentpole", "Hustlr"
        ]
        display_count = sum(self.parsed_counts.get(cat, 0) for cat in display_categories)

        print(f"  -> Total Display Count: {display_count}")
        # --- END OF INITIALIZATION ---


        # --- Constants (gaps and fixture dimensions in mm) ---
        single_shopping = 1050
        display_large_length = 1200
        display_medium_length = 1010
        display_width = 250
        euro_length = 1175
        euro_width = 1040
        mirror_length = 300
        
        # --- Initial Calculation based on 3:1 Wall-to-Floor Ratio ---
        ratio_parts = 4
        floor_count = int(display_count / ratio_parts)
        wall_count = display_count - floor_count
        mirror_count = wall_count
        
        # Initialize the mix of large/medium wall fixtures
        num_large_wall = wall_count
        num_medium_wall = 0

        valid = False
        attempts = 0
        prev_action = -1  # -1: init, 0: both fail, 1: wall fail, 2: floor fail

        while not valid:
            # Sync the large/medium counts with the current total wall_count
            current_total_wall_fixtures = num_large_wall + num_medium_wall
            if current_total_wall_fixtures != wall_count:
                if wall_count > current_total_wall_fixtures:
                    num_large_wall += (wall_count - current_total_wall_fixtures)
                else:
                    to_remove = current_total_wall_fixtures - wall_count
                    removed_medium = min(to_remove, num_medium_wall)
                    num_medium_wall -= removed_medium
                    removed_large = min(to_remove - removed_medium, num_large_wall)
                    num_large_wall -= removed_large

            # --- Calculate Space Requirements for the Current Configuration ---
            wall_space_needed = (num_large_wall * display_large_length) + \
                                (num_medium_wall * display_medium_length) + \
                                (mirror_count * mirror_length)
            
            wall_fixture_area = wall_space_needed * (display_width + single_shopping)
            floor_fixture_area = (euro_length + 2000) * euro_width * floor_count
            remaining_floor_area = floor_area - wall_fixture_area - floor_fixture_area

            # --- Validation and Adjustment Logic ---
            if wall_space_needed <= wall_length and remaining_floor_area > 0:
                print("Valid floor/wall/mirror counts found.")
                valid = True
                
            elif wall_space_needed > wall_length:
                if remaining_floor_area <= 0: # Both wall and floor fail
                    prev_action = 0
                    print("ACTION: Insufficient space on BOTH floor and wall. Downsizing wall fixtures.")
                    if num_large_wall > 0:
                        num_large_wall -= 1
                        num_medium_wall += 1
                    elif mirror_count > wall_count / 2:
                        mirror_count -= 1
                    else:
                        break # No more options
                else: # Only wall fails
                    if prev_action == 2: # Flip-flop detected
                        print("DEAD END: Detected flip-flop (floor -> wall). Forcing downsize.")
                        if num_large_wall > 0:
                            num_large_wall -= 1
                            num_medium_wall += 1
                        elif mirror_count > wall_count / 2:
                            mirror_count -= 1
                        prev_action = -1 # Reset state
                    else:
                        prev_action = 1
                        print("ACTION: Not enough wall space. Trading wall fixture for floor fixture.")
                        wall_count -= 1
                        floor_count += 1
                        mirror_count -= 1
                
            elif remaining_floor_area <= 0: # Only floor fails
                if prev_action == 1: # Flip-flop detected
                    print("DEAD END: Detected flip-flop (wall -> floor). Forcing downsize.")
                    if num_large_wall > 0:
                        num_large_wall -= 1
                        num_medium_wall += 1
                    elif mirror_count > wall_count / 2:
                        mirror_count -= 1
                    prev_action = -1 # Reset state
                else:
                    prev_action = 2
                    print("ACTION: Not enough floor space. Trading floor fixture for wall fixture.")
                    floor_count -= 1
                    wall_count += 1
                    mirror_count += 1

            # --- Status Printout and Exit Conditions ---
            print(f"\n--- Attempt #{attempts + 1} ---")
            print(f"  Config: [Floor: {floor_count}, Wall: {wall_count} ({num_large_wall}L/{num_medium_wall}M), Mirror: {mirror_count}]")
            print(f"  Wall space needed: {wall_space_needed:.0f} (Available: {wall_length:.0f})")
            print(f"  Remaining floor area: {remaining_floor_area:.0f}")
            
            attempts += 1
            if attempts > 50: # Safety break
                print("STOPPING: Exceeded maximum attempts.")
                break
            
            if not valid and mirror_count <= (wall_count / 2) and wall_count > 0:
                print("STOPPING: Reached minimum mirror ratio without a solution.")
                break
            
            if floor_count < 0 or wall_count < 0:
                print("STOPPING: A valid configuration is not possible.")
                break

        # --- Final Result ---
        if valid:
            result = {
                'valid': True,
                'floor_fixtures': floor_count,
                'large_wall_fixtures': num_large_wall,
                'medium_wall_fixtures': num_medium_wall,
                'total_wall_fixtures': num_large_wall + num_medium_wall,
                'mirrors': mirror_count
            }
            print("\n--- Final Valid Layout ---")
            print(result)
            return result
        else:
            result = {
                'valid': False,
                'floor_fixtures': floor_count,
                'large_wall_fixtures': num_large_wall,
                'medium_wall_fixtures': num_medium_wall,
                'total_wall_fixtures': num_large_wall + num_medium_wall,
                'mirrors': mirror_count
            }
            print("\n--- Could not find a valid layout. Returning last attempted state. ---")
            print(result)
            return result

    def generate_specific_fixture_list_simplified_dp(self, planner_output: dict, family_totals: dict) -> list:
        """
        A simplified bridge function that distributes generic 'large' and 'medium' counts
        across specific fixture families based on a priority order.
        """
        print("\n--- Distributing Fixture Counts ---")
        
        # Define mappings and priority
        size_mapping = {
            "jj_fixture_family": ["jj_fixture_large", "jj_fixture_medium"],
            "vc_fixture_family": ["vc_fixture_large", "vc_fixture_medium"],
            "jj_super_hybrid_family": ["jj_super_hybrid_large", "jj_super_hybrid_medium"],
        }
        family_priority = ["jj_fixture_family", "jj_super_hybrid_family", "vc_fixture_family"]

        # Get the "budgets" for large and medium fixtures
        large_budget = planner_output.get('large_wall_fixtures', 0)
        medium_budget = planner_output.get('medium_wall_fixtures', 0)
        
        remaining_needs = family_totals.copy()
        final_fixture_list = []

        # Process each family in order of priority
        for family in family_priority:
            if family not in remaining_needs or remaining_needs[family] == 0:
                continue

            # 1. Assign LARGE fixtures for this family
            num_to_assign_large = min(large_budget, remaining_needs[family])
            if num_to_assign_large > 0:
                large_name = size_mapping[family][0]
                final_fixture_list.extend([large_name] * num_to_assign_large)
                large_budget -= num_to_assign_large
                remaining_needs[family] -= num_to_assign_large
                print(f"  -> Assigned {num_to_assign_large} of '{large_name}'")
                
            # 2. Assign MEDIUM fixtures for this family's *remaining* need
            num_to_assign_medium = min(medium_budget, remaining_needs[family])
            if num_to_assign_medium > 0:
                medium_name = size_mapping[family][1]
                final_fixture_list.extend([medium_name] * num_to_assign_medium)
                medium_budget -= num_to_assign_medium
                remaining_needs[family] -= num_to_assign_medium
                print(f"  -> Assigned {num_to_assign_medium} of '{medium_name}'")

        print("--- ✅ Distribution complete. ---")
        return final_fixture_list

    #---------------------validating get partition funtion now ------------------
    #---------------------validating get partition funtion now ------------------

    def draw_internal_wall_partitions_for_validation(self, min_length: float, max_length: float, thickness: float, layer_name: str, color: int):
            """
            Visually draws the bounding boxes identified by get_internal_wall_partitions for debugging.

            Args:
                max_length (float): The 'max_length' to pass to the target function.
                thickness (float): The 'thickness' to pass to the target function.
                layer_name (str): The name for the new DXF layer.
                color (int): The ACI color index for the new layer.
            """
            print(f"\n--- 🎨 Visualizing Internal Partitions (max_length={max_length}, thickness={thickness}) ---")
            
            # 1. Call the original function to get the list of partition bounding boxes
            partitions = self.cvc.get_internal_wall_partitions(min_length=min_length, max_length=max_length, thickness=thickness)
            
            if not partitions:
                print(f"  -> No partitions found with the given parameters.")
                return

            # 2. Create a dedicated layer in the DXF document for the visualization
            if layer_name not in self.doc.layers:
                self.doc.layers.add(name=layer_name, color=color)
            
            # 3. Loop through the found partitions and draw each bounding box
            for i, (min_x, min_y, max_x, max_y) in enumerate(partitions):
                # Define the 4 corners of the rectangular bounding box
                points = [
                    (min_x, min_y),
                    (max_x, min_y),
                    (max_x, max_y),
                    (min_x, max_y)
                ]
                # Add the rectangle to the modelspace on the specified layer
                self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": layer_name})

            print(f"  -> ✅ Drew {len(partitions)} partition boxes on layer '{layer_name}'.")

            
    #---------------------validating get partition funtion now ------------------
    #---------------------validating get partition funtion now ------------------


    
    

    #--------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------
    
    def _calculate_standing_tables(self) -> int:
        """
        Calculates the number of standing tables based on the 'proto' value.
        Rule: 1 table per 4 Lakhs, rounded to the nearest whole number.
        """
        try:
            # 1. Get the 'proto' string value (e.g., "16L")
            proto_str = self.merch_data.get("proto", "0L")
            
            # 2. Clean the string to get just the number (remove 'L' and convert to float)
            proto_value = float(proto_str.replace('L', ''))
            
            # 3. Apply the rule: divide by 4 and round to the nearest whole number
            standing_table_count = round(proto_value / 4.0)
            
            print(f"  -> Proto value is {proto_value}L. Calculated {int(standing_table_count)} Standing Tables.")
            return int(standing_table_count)
            
        except (ValueError, TypeError):
            print("  -> ⚠️  Could not parse 'proto' value. Defaulting to 0 standing tables.")
            return 0

    def generate_clinic_counts(self) -> Dict[str, int]:
        """
        Calculates the number and type of clinic fixtures based on the 'proto' value.
        """
        print("--- 🧠 Generating DYNAMIC Clinic Fixture Counts ---")

        clinic_counts = collections.defaultdict(int)

        try:
            proto_str = self.merch_data.get("proto", "0L")
            proto_value = float(proto_str.replace('L', ''))
            print(f"  -> Proto value for clinic calculation is {proto_value}L.")

            if proto_value <= 12:
                clinic_counts["ROC_clinic"] = 1
                # clinic_counts["Clinic_regular"] = 1
                clinic_counts["Clinic_with_sink"] = 1

            elif 12 < proto_value <= 15:
                clinic_counts["ROC_clinic"] = 1
                clinic_counts["Clinic_with_sink"] = 1
                clinic_counts["Clinic_regular"] = 1
            
            else:
                clinic_counts["ROC_clinic"] = 1
                clinic_counts["Clinic_with_sink"] = 1
                clinic_counts["Clinic_regular"] = 1
                options = ["Clinic_with_sink", "ROC_clinic", "Clinic_regular"]
                fourth_clinic = random.choice(options)
                clinic_counts[fourth_clinic] += 1
        
        except (ValueError, TypeError):
            print("  -> ⚠️ Could not parse 'proto' value for clinics. Defaulting to 1 sink clinic.")
            clinic_counts["Clinic_with_sink"] = 1
        
        return dict(clinic_counts)

    def merch_mix_cal(self, merch_mix_data: dict, static_fixtures: dict):
        """
        Parses merch data, generates all dynamic counts, and assembles the
        final master fixture dictionary for the entire project. This function
        populates `self.fixtures` with the complete plan.
        """
        # 4. Generate all dynamic fixture counts using the controller's internal methods
        print("--- ⚙️  Initializing Dossier data and generating counts... ---")
        self.merch_data = merch_mix_data
        self.parsed_counts = self._parse_json_data(merch_mix_data)
        self.family_totals = self._map_and_sum_wall_fixture_families()
        wall_family_totals, generated_floor_fixtures = self.generate_fixture_counts()
        dynamic_clinic_fixtures = self.generate_clinic_counts()
        dynamic_tv_count = self.calculate_dynamic_tv_count()

        # 5. Assemble the final, complete fixture dictionary
        print("--- 📋 Assembling final fixture master list... ---")
        final_fixtures = static_fixtures.copy()
        final_fixtures["wall_fixtures"] = wall_family_totals
        final_fixtures["clinic_fixtures"] = dynamic_clinic_fixtures
        final_fixtures["screen_fixtures"]["screen_55"] = dynamic_tv_count

        # Merge floor fixtures correctly
        if "Standing_table" in generated_floor_fixtures:
            final_fixtures["table_fixtures"]["Standing_table"] = generated_floor_fixtures.pop("Standing_table")
        
        floor_fixtures_final = final_fixtures.get("floor_fixtures", {}).copy()
        floor_fixtures_final.update(generated_floor_fixtures)
        floor_fixtures_final.update(final_fixtures.get("floor_fixtures_table", {}))
        final_fixtures["floor_fixtures"] = floor_fixtures_final

        # Set the final compiled dictionary on the controller instance
        self.fixtures = final_fixtures
        print("--- ✅ Master fixture list assembled and stored in the controller. ---")



    def load_merch_data_from_json(self, json_file_path: str) -> Optional[dict]:
        """
        Loads and validates the merchandise mix data from a JSON file.

        Args:
            json_file_path: The path to the merch_mix.json file.

        Returns:
            A dictionary containing the 'merch_mix_max' data on success,
            or None on failure.
        """
        print(f"--- 📂 Loading merchandise data from {json_file_path}... ---")
        try:
            with open(json_file_path, 'r') as f:
                merch_json_data = json.load(f)
            # Extract the 'merch_mix_max' object, which contains the final counts
            merch_mix_data = merch_json_data['merch_mix_max']
            print("--- ✅ Successfully loaded data. ---")
            return merch_mix_data
        except (FileNotFoundError, KeyError) as e:
            print(f"--- 🚨 ERROR: Could not load or parse {json_file_path}. Error: {e} ---")
            return None

    # ============================================================================
    # --- END: METHODS FROM DossierParser ---
    # ============================================================================


    

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
        self.validation_hull_polygon = self.floorplan_polygon.convex_hull

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
        

        # This is the line that actually places the fixture
        block_ref = self.msp.add_blockref(
            safe_block_name, 
            insert_point, 
            dxfattribs={
                "rotation": rotation,
                "xscale": xscale,
                "yscale": yscale
            }
        )
        # --- END of Modification ---

        print(f"✅ Placed '{fxtr.name}' as '{safe_block_name}' at ({insert_point[0]:.0f}, {insert_point[1]:.0f})")

        return block_ref

        
#---------------------FIXTURE PLACEMENT STARTS FROM HERE -----------------------------------------------------------
#---------------------FIXTURE PLACEMENT STARTS FROM HERE -----------------------------------------------------------
#---------------------FIXTURE PLACEMENT STARTS FROM HERE -----------------------------------------------------------

#---Common-Helper-Functions------------------------------------------------------------------
#---Common-Helper-Functions------------------------------------------------------------------

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
    
    
    def _get_placeable_wall_segments(self, side: str, min_length: float = 1000.0) -> List[Tuple[Vec2, Vec2]]:
        """
        Analyzes all wall segments from the floorplan data and returns a sorted list
        of only the segments that are valid for fixture placement on a given side.

        A segment is "placeable" if it's long enough, mostly vertical, and on the
        correct side of the floorplan.
        """
        print(f"  -> Filtering for placeable wall segments on the '{side}' side...")
        
        all_segments_raw = self.cvc.plan_final
        if not all_segments_raw:
            return []

        placeable_segments = []
        # Use a wider tolerance for identifying which side a wall is on
        side_tolerance = (self.cvc.max_x - self.cvc.min_x) * 0.40 
        
        for x1, y1, x2, y2 in all_segments_raw:
            p1 = Vec2(x1, y1)
            p2 = Vec2(x2, y2)
            
            # 1. Check Length
            if p1.distance(p2) < min_length:
                continue

            # 2. Check Orientation (must be mostly vertical)
            is_vertical = abs(p1.y - p2.y) > abs(p1.x - p2.x)
            if not is_vertical:
                continue

            # 3. Check Location (is it on the correct side?)
            midpoint_x = (p1.x + p2.x) / 2
            is_on_correct_side = False
            if side == 'left' and midpoint_x < self.cvc.min_x + side_tolerance:
                is_on_correct_side = True
            elif side == 'right' and midpoint_x > self.cvc.max_x - side_tolerance:
                is_on_correct_side = True

            if is_on_correct_side:
                # Ensure the segment vector points upwards for consistent processing
                if p1.y < p2.y:
                    placeable_segments.append((p1, p2))
                else:
                    placeable_segments.append((p2, p1))

        # Sort the final list from bottom to top
        placeable_segments.sort(key=lambda seg: seg[0].y)
        
        print(f"    -> Found {len(placeable_segments)} valid segments for placement on the '{side}' side.")
        return placeable_segments
    

    def _get_accurate_obstacle_bboxes(self, include_all=False, debug=False):
        """
        Returns accurate bounding boxes for fixtures.
        If include_all is False, it returns only 'clinic', 'boh', 'boh_preset', and 'Eye_massage_area' types.
        If include_all is True, it returns all fixtures.
        NOW INCLUDES the RETAIL_SEPARATOR line as a mandatory obstacle.
        """
        from ezdxf.bbox import extents
        bboxes = []
        msp = self.doc.modelspace()
        
        # --- Part 1: Find all fixture obstacles (existing logic) ---
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
                if debug:
                    print(f"&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&fixture_type: {fixture_type}, best_match_key: {best_match_key}")
                if include_all or fixture_type in ['clinic', 'boh', 'boh_preset', 'pickup_window'] or best_match_key in ["Eye_massage_area", 'medium_bench', "large_bench"]:
                    try:
                        entity_bbox = extents([entity], fast=True)
                        minx, miny, minz = entity_bbox.extmin
                        maxx, maxy, maxz = entity_bbox.extmax
                        area = (maxx-minx)*(maxy-miny)
                        if area <= (2600*1700)+1000: # max clinic size + buffer
                            bboxes.append((entity_bbox.extmin.x, entity_bbox.extmin.y, entity_bbox.extmax.x, entity_bbox.extmax.y))
                    except (RuntimeError, ZeroDivisionError, TypeError):
                        print(f"⚠️ Could not compute bounding box for '{entity.dxf.name}'.")

        # ******************** NEW SECTION STARTS HERE ********************
        # --- Part 2: Find the retail separation line obstacle ---
        # This runs regardless of the 'include_all' flag because the line is always a critical obstacle.
        separator_lines = msp.query('LINE[layer=="RETAIL_SEPARATOR"]')
        for line in separator_lines:
            try:
                start_pt = line.dxf.start
                end_pt = line.dxf.end
                # Create a thin bounding box for the line to act as an obstacle
                line_bbox = (
                    min(start_pt.x, end_pt.x),
                    min(start_pt.y, end_pt.y) - 1, # Add 1mm buffer below
                    max(start_pt.x, end_pt.x),
                    max(start_pt.y, end_pt.y) + 1  # Add 1mm buffer above
                )
                print(line_bbox)
                bboxes.append(line_bbox)
                print("  -> Found and added 'RETAIL_SEPARATOR' line as a stoppage obstacle.")
            except Exception as e:
                print(f"⚠️ Could not process the RETAIL_SEPARATOR line as an obstacle: {e}")
        # ********************* NEW SECTION ENDS HERE *********************

        print(f"✅ Found {len(bboxes)} obstacles to avoid.")
        return bboxes
    

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

#---Common-Helper-Functions------------------------------------------------------------------
#---Common-Helper-Functions------------------------------------------------------------------
#---Space-limiting-setup-functions------------------------------------------------------------------
#---Space-limiting-setup-functions------------------------------------------------------------------  

    from typing import Iterable, Tuple, List, Any
    def entities_intersecting_line(self, entities: Iterable[Any],
                                    p0: Vec2, p1: Vec2) -> List[Any]:
        from typing import Iterable, Tuple, List, Any

        # ---------- basic 2D segment math ----------

        # Vec2 = Tuple[float, float]
        Seg2 = Tuple[Vec2, Vec2]

        def bbox2(seg: Seg2) -> Tuple[float, float, float, float]:
            (x1, y1), (x2, y2) = seg
            return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))

        def bbox_overlap(a, b) -> bool:
            ax1, ay1, ax2, ay2 = a
            bx1, by1, bx2, by2 = b
            return not (ax2 < bx1 or bx2 < ax1 or ay2 < by1 or by2 < ay1)

        def _orient(a: Vec2, b: Vec2, c: Vec2) -> float:
            return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])

        def _on_segment(a: Vec2, b: Vec2, p: Vec2) -> bool:
            return (min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and
                    min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))

        def segseg_intersects(s1: Seg2, s2: Seg2) -> bool:
            a, b = s1
            c, d = s2
            o1 = _orient(a, b, c)
            o2 = _orient(a, b, d)
            o3 = _orient(c, d, a)
            o4 = _orient(c, d, b)
            if (o1 * o2 < 0) and (o3 * o4 < 0):
                return True
            if o1 == 0 and _on_segment(a, b, c): return True
            if o2 == 0 and _on_segment(a, b, d): return True
            if o3 == 0 and _on_segment(c, d, a): return True
            if o4 == 0 and _on_segment(c, d, b): return True
            return False

        # ---------- DXF helpers ----------

        def flatten_entities_wcs(entities: Iterable[Any]) -> List[Any]:
            """
            Recursively expand INSERTs (including nested) into concrete, transformed entities in WCS.
            Uses INSERT.virtual_entities() so transforms (move/rotate/scale) are applied as we go.
            Returns a flat list with no INSERTs.
            """
            out: List[Any] = []
            stack = list(entities)
            while stack:
                e = stack.pop()
                t = e.dxftype()
                if t == "INSERT":
                    # 1-level virtual expansion (already transformed to this INSERT's placement)
                    try:
                        vs = list(e.virtual_entities())
                    except Exception:
                        vs = []
                    for v in vs:
                        if v.dxftype() == "INSERT":
                            stack.append(v)  # recurse further
                        else:
                            out.append(v)
                else:
                    out.append(e)
            return out

        def segments_from_entity_2d(e) -> Iterable[Seg2]:
            """
            Yield 2D line segments for common straight-edge entities.
            (Curves are skipped; see note below to approx curves if needed.)
            """
            t = e.dxftype()

            if t == "LINE":
                s = getattr(e.dxf, "start", None); g = getattr(e.dxf, "end", None)
                if s is not None and g is not None:
                    yield ( (float(s[0]), float(s[1])), (float(g[0]), float(g[1])) )
                return

            if t == "LWPOLYLINE":
                # Handles straight edges (bulge==0). Add arc approx if needed.
                pts = []
                for vx in e:  # each vertex: (x, y, start_width, end_width, bulge)
                    x, y = vx[0], vx[1]
                    bulge = vx[4] if len(vx) > 4 else 0.0
                    pts.append((x, y, bulge))
                if getattr(e, "closed", False) and pts:
                    pts.append(pts[0])
                for (x1, y1, b1), (x2, y2, b2) in zip(pts, pts[1:]):
                    if b1 == 0.0 and b2 == 0.0:
                        yield ((float(x1), float(y1)), (float(x2), float(y2)))
                return

            if t == "POLYLINE":
                verts = [tuple(v.dxf.location) for v in e.vertices]  # (x,y,z)
                if getattr(e, "is_closed", False) and verts:
                    verts.append(verts[0])
                for (x1, y1, *_), (x2, y2, *_) in zip(verts, verts[1:]):
                    yield ((float(x1), float(y1)), (float(x2), float(y2)))
                return

            if t == "3DFACE":
                pts = [tuple(getattr(e.dxf, name)) for name in ("vtx0", "vtx1", "vtx2", "vtx3")
                    if hasattr(e.dxf, name)]
                border = [p for p in pts if p is not None]
                if len(border) >= 3:
                    ring = border[:3] if (len(border) == 3 or border[3] == border[2]) else border[:4]
                    ring = ring + [ring[0]]
                    for (x1, y1, *_), (x2, y2, *_) in zip(ring, ring[1:]):
                        yield ((float(x1), float(y1)), (float(x2), float(y2)))
                return
            # Extend with more types as needed.

        flat = flatten_entities_wcs(entities)
        # 2) Test your drawn line p0->p1:
        
        """
        Return original entities that intersect the 2D line segment p0->p1.
        (Curves ignored unless you extend segment extraction to approximate them.)
        """
        seg_q = (p0, p1)
        bb_q = bbox2(seg_q)
        hits = []
        for e in flat:
            # Test per-segment; early-out on first hit for e
            for seg in segments_from_entity_2d(e):
                if bbox_overlap(bb_q, bbox2(seg)) and segseg_intersects(seg_q, seg):
                    hits.append(e)
                    break
        return hits

    def draw_retail_separation_line(self, placed_bboxes: List[tuple], enabled: bool = True, margin: float = 100.0):
        """
        Identifies all "back side" fixtures (clinics, BOH), finds their
        lowest collective point, and draws a horizontal separation line.

        This line is placed on a dedicated layer for visibility control and
        can act as a validation object for subsequent placements.
        """
        import ezdxf
        from ezdxf.math import Vec2

        def print_insert_bounds(insert, depth=0):
            """
            Recursively list INSERTs and their WCS bounding boxes.
            """
            indent = "  " * depth
            name   = insert.dxf.name

            # Compute WCS bounding box of this insert
            try:
                bbox = extents(insert.virtual_entities())
                if bbox.has_data:
                    minx, miny, minz = bbox.extmin
                    maxx, maxy, maxz = bbox.extmax
                    bounds = f"({minx:.3f}, {miny:.3f}) -> ({maxx:.3f}, {maxy:.3f})"
                else:
                    bounds = "[empty]"
            except Exception as e:
                bounds = f"[error: {e}]"

            print(f"{indent}INSERT '{name}' bounds: {bounds}")

            # Recurse into nested INSERTs
            blk = insert.block()
            if blk:
                for e in blk.query("INSERT"):
                    print_insert_bounds(e, depth + 1)

        if not enabled:
            print("\n--- ⏩ Retail separation line is disabled. Skipping. ---")
            return

        print("\n---  çizgi Drawing Retail Separation Line ---")

        from ezdxf.bbox import extents
        from shapely.geometry import LineString, box
        # from ezdxf.proxygraphic import itervirtualentities

        # --- 1. Identify all "back side" fixtures ---
        back_side_entities = []
        back_side_types = {'clinic', 'boh', 'boh_preset', 'pickup_window'}
        
        for entity in self.msp.query('INSERT'):
            block_name_upper = entity.dxf.name.upper()
            best_match_key = ""
            for key in self.fixture_dict.keys():
                sanitized_key = key.upper().replace(" ", "_")
                if block_name_upper.startswith(sanitized_key):
                    if len(key) > len(best_match_key):
                        best_match_key = key
            
            if best_match_key and self.fixture_dict[best_match_key].get("type") in back_side_types:
                print(f"checking {block_name_upper}")
                bbox = extents(entity.virtual_entities())
                print("bbox:", bbox.extmin, bbox.extmax)
                if bbox.has_data:
                    minx, miny, minz = bbox.extmin
                    maxx, maxy, maxz = bbox.extmax
                    area = (maxx-minx)*(maxy-miny)
                    # print("area:", area)
                    # print("max area:", (2600*1700) + 1000)
                    # if area < (2600*1700)+1000: # max clinic size + buffer

                    back_side_entities.append(entity)
                    # print("  -> included",back_side_entities)
                    print(f"\tadding {block_name_upper}")

        if not back_side_entities:
            print("  -> ⚠️ SKIPPED: No back-side fixtures found to define the separation line.")
            return

        # --- 2. Calculate the combined bounding box and find the bottom edge ---
        combined_bbox = extents(back_side_entities)
        print("combined_bbox:", combined_bbox.extmin, combined_bbox.extmax)
        separation_y = combined_bbox.extmin.y - margin
        print(f"[DEBUG] Separation line Y value: {separation_y}")
        print(f"  -> Back-side fixture cluster ends at y={combined_bbox.extmin.y:.0f}. Placing line at y={separation_y:.0f} (with margin).")

        # --- 3. Determine the horizontal start and end points of the line ---
        horizontal_slicer = LineString([(self.cvc.min_x - 1000, separation_y), (self.cvc.max_x + 1000, separation_y)])

        # --------- usage ---------
        # Suppose you start with: entities = [ ... may include nested INSERTs ... ]
        # 1) Flatten inserts into concrete WCS geometry:
        retail_segment = self.floorplan_polygon.intersection(horizontal_slicer)
        
        # Handle cases where the intersection might not be a single clean line
        if retail_segment.is_empty:
             print("  -> ⚠️ SKIPPED: Could not determine the retail area width at the separation height.")
             return
        
        # If intersection results in multiple segments, use the overall bounds
        min_x, _, max_x, _ = retail_segment.bounds
        start_point = (min_x, separation_y)
        end_point = (max_x, separation_y)

        touched = self.entities_intersecting_line(back_side_entities, start_point, end_point)
        print([e.dxftype() for e in touched])

        # --- 4. Draw the line on a dedicated layer (WITH LINETYPE FIX) ---
        layer_name = "RETAIL_SEPARATOR"
        if layer_name not in self.doc.layers:
            self.doc.layers.add(
                name=layer_name, 
                color=4,  # Cyan for visibility
                linetype='DASHED' # Reference the linetype
            )
        
       
        if 'DASHED' not in self.doc.linetypes:
            # This defines what "DASHED" means: a dash of 200mm, a space of 100mm, repeat.
            self.doc.linetypes.add(
                name='DASHED',
                pattern=[200.0, -100.0],
                description="Dashed line for separators ----"
            )
        
        
        self.msp.add_line(start_point, end_point, dxfattribs={"layer": layer_name})
        print(f"  -> ✅ Line drawn on layer '{layer_name}' y={start_point[1]} from x={min_x:.0f} to x={max_x:.0f}.")

        # --- 5. Add a thin bounding box to act as an obstacle for validation ---
        # This makes the "invisible line" a real object for collision detection
        line_obstacle_bbox = (min_x, separation_y - 1, max_x, separation_y + 1)
        print("box:", line_obstacle_bbox)
        placed_bboxes.append(line_obstacle_bbox)
        print("  -> Added line as a validation obstacle.")


    # def create_invisible_retail_boundary(self, placed_bboxes: List[tuple], margin: float = 100.0):
    #     """
    #     Calculates the boundary between the back-of-house and retail areas and
    #     registers it as an INVISIBLE obstacle without drawing a visible line.

    #     This is used to set a boundary for other placement functions.
    #     """
    #     print("\n--- 🚧 Registering Invisible Retail Boundary ---")

    #     from ezdxf.bbox import extents
    #     from shapely.geometry import LineString

    #     # 1. Identify all "back side" fixtures (logic is identical to the original function)
    #     back_side_entities = []
    #     back_side_types = {'clinic', 'boh', 'boh_preset', 'pickup_window'}
        
    #     for entity in self.msp.query('INSERT'):
    #         block_name_upper = entity.dxf.name.upper()
    #         best_match_key = ""
    #         for key in self.fixture_dict.keys():
    #             sanitized_key = key.upper().replace(" ", "_")
    #             if block_name_upper.startswith(sanitized_key):
    #                 if len(key) > len(best_match_key):
    #                     best_match_key = key
            
    #         if best_match_key and self.fixture_dict[best_match_key].get("type") in back_side_types:
    #             back_side_entities.append(entity)

    #     if not back_side_entities:
    #         print("  -> ⚠️ SKIPPED: No back-side fixtures found to define the boundary.")
    #         return

    #     # 2. Calculate the combined bounding box and find the bottom edge (identical logic)
    #     combined_bbox = extents(back_side_entities)
    #     separation_y = combined_bbox.extmin.y - margin
    #     print(f"  -> Back-side fixture cluster ends at y={combined_bbox.extmin.y:.0f}. Registering invisible boundary at y={separation_y:.0f}.")

    #     # 3. Determine the horizontal start and end points of the boundary (identical logic)
    #     horizontal_slicer = LineString([(self.cvc.min_x - 1000, separation_y), (self.cvc.max_x + 1000, separation_y)])
    #     retail_segment = self.floorplan_polygon.intersection(horizontal_slicer)
        
    #     if retail_segment.is_empty:
    #          print("  -> ⚠️ SKIPPED: Could not determine the retail area width for the boundary.")
    #          return
        
    #     min_x, _, max_x, _ = retail_segment.bounds

    #     # --- DXF drawing commands are removed from this version ---
    #     # The function no longer creates a visible layer or draws a line entity.
        
    #     # 4. The critical part: Add a thin bounding box to act as an obstacle
    #     # This makes the "invisible line" a real object for collision detection.
    #     line_obstacle_bbox = (min_x, separation_y - 1, max_x, separation_y + 1)
    #     placed_bboxes.append(line_obstacle_bbox)
    #     print("  -> ✅ Invisible boundary registered as a validation obstacle.")



    
#---Space-limiting-setup-functions------------------------------------------------------------------
#---Space-limiting-setup-functions------------------------------------------------------------------




#---------------------PORTRAIT MODE FIXTURE PLACEMENT STARTS FROM HERE -----------------------------------------------------------
#---------------------PORTRAIT MODE FIXTURE PLACEMENT STARTS FROM HERE -----------------------------------------------------------

#---CATEGORY :- CLINIC

#---- CLINIC PLACEMENT FUNCTION STARTED ----
#----normal--place-clinic--function-----------------------------------------------------------
#----normal--place-clinic--function-----------------------------------------------------------
    
    
    

    ##--new-test--with---greedy method-- strategy -----space for boh
    ##--new-test--with---greedy method-- strategy -----space for boh    

    def _find_best_combination_for_row(self, clinic_names_to_place: list, available_width: float, force_orientation: Optional[str] = None) -> List[dict]:
        """
        # --- MODIFIED: Now returns a LIST of valid layouts, ranked by score. ---
        Universal "Puzzle Solver" for clinic placement in a single row.
        """
        from itertools import product
        # from Fixture import Fixture

        V_V_GAP = 800.0
        # H_GAP = 50.0
        H_GAP = -100.0

        # --- MODIFIED: Initialize a list to hold all valid layouts ---
        valid_layouts = []

        orientations_to_test = ['H', 'V']
        if force_orientation == 'V':
            orientations_to_test = ['V']
        elif force_orientation == 'H':
            orientations_to_test = ['H']

        for n in range(len(clinic_names_to_place), 0, -1):
            try:
                current_fixtures = [Fixture.Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"]) for name in clinic_names_to_place[:n]]
            except (KeyError, ValueError):
                continue
            
            orientations = list(product(orientations_to_test, repeat=n))

            for combo in orientations:
                required_width = 0
                gaps = []
                
                for i in range(n):
                    orient = combo[i]
                    fxtr = current_fixtures[i]
                    w = fxtr.width if orient == 'H' else fxtr.height
                    required_width += w
                    
                    if i < n - 1:
                        next_orient = combo[i+1]
                        gap = V_V_GAP if (orient == 'V' and next_orient == 'V') else H_GAP
                        required_width += gap
                        gaps.append(gap)
                gaps.append(0)

                start_margin = 10.0 if combo[0] == 'V' else 10.0
                end_margin = 10.0 if combo[-1] == 'V' else 10.0
                total_required_space = start_margin + required_width + end_margin

                if total_required_space <= available_width:
                    score = (n * 10000) - required_width # Prioritize more fixtures, then less width

                    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    # +++ NEW: ARCHITECTURAL BONUS FOR BETTER LAYOUTS +++
                    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    if 'H' in combo:
                        score += 500  # Give a bonus to any layout with horizontal fixtures
                    if 'V' in combo and 'H' in combo:
                        score += 200 # Extra bonus for mixed layouts
                    if combo.count('V') == 0 and len(combo) > 1:
                        score += 1000 # Big bonus for all-horizontal rows
                    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    
                    # --- MODIFIED: Append every valid layout to the list ---
                    valid_layouts.append({
                        'score': score,
                        'combo': combo,
                        'gaps': gaps,
                        'fixtures_for_row': current_fixtures,
                        'start_margin': start_margin,
                        'remaining_fixtures_names': clinic_names_to_place[n:]
                    })

        # --- NEW: Sort the list by score (highest first) before returning ---
        if valid_layouts:
            valid_layouts.sort(key=lambda x: x['score'], reverse=True)
            return valid_layouts

        return [] # Return an empty list if no layouts were found
    
    def _validate_and_place_on_wall(self, fixture, target_center, angle_deg, placed_bboxes, xscale=1.0, yscale=1.0, place_actually=True):
        """
        ### MIRROR LOGIC ADDED ###
        Now accepts xscale and yscale to validate and place mirrored fixtures.
        Can run in two modes:
        - Validation only (place_actually=False)
        - Validation AND Placement (place_actually=True)
        """
        from shapely.geometry import Polygon
        from ezdxf.math import Matrix44, Vec2, BoundingBox2d
        import math

        # --- Step 1: Calculate the Transformation Matrix ---
        # This matrix will move the fixture from its own file's coordinates to the final position in the floorplan.
        
        # Get the geometric center of the fixture in its own local coordinate system.
        local_center = fixture.bounding_box.center
        transform = Matrix44.chain(
            # 1. Move the fixture's center to the origin (0,0,0). This is essential for correct rotation and scaling.
            Matrix44.translate(-local_center.x, -local_center.y, 0),
            # 2. Apply scaling (mirroring). An xscale of -1 will flip it horizontally.
            Matrix44.scale(xscale, yscale, 1.0),
            # 3. Rotate the fixture around the origin.
            Matrix44.z_rotate(math.radians(angle_deg)),
            # 4. Move the fixture from the origin to its final target center in the world.
            Matrix44.translate(target_center.x, target_center.y, 0)
        )

        # --- Step 2: Calculate the Fixture's Final Position and Shape ---
        # Apply the transformation to the corners of the fixture's bounding box.
        world_corners = list(transform.transform_vertices(fixture.bounding_box.rect_vertices()))
        # Create a precise polygon shape from these new "world" coordinates for accurate checking.
        fixture_polygon = Polygon([(p.x, p.y) for p in world_corners])
        # Create a simple rectangular bounding box (Axis-Aligned Bounding Box) for faster collision checks.
        aabb = BoundingBox2d(world_corners)

        # --- Step 3: Perform Validation Checks ---
        # --- MODIFICATION: Allow clinics to ignore wall boundaries ---
        is_inside = True # Assume it's valid by default
        if "CLINIC" not in fixture.name.upper():
            # Only check for wall containment if the fixture is NOT a clinic
            is_inside = self.validation_hull_polygon.contains(fixture_polygon)
        # --- END OF MODIFICATION ---
        # Check 2: Does the fixture's bounding box overlap with any previously placed objects?
        is_overlapping = False
        if "CLINIC" not in fixture.name.upper():
            is_overlapping = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)
        

        # --- Step 4: Place the Fixture if Valid ---
        if is_inside and not is_overlapping:
            # If the spot is clear, get the coordinates of the new bounding box.
            new_bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)
            
            # This block only runs if the function is told to actually place the fixture.
            # This allows us to use the function for "check-only" validation passes.
            if place_actually:
                # To place a block in ezdxf, we need to provide the 'insertion point', which corresponds
                # to the block's origin (0,0) in its source file, not its geometric center.
                # This calculation corrects for the offset between the fixture's center and its origin.
                local_center_scaled = Vec2(local_center.x * xscale, local_center.y * yscale)
                rotated_offset = local_center_scaled.rotate(math.radians(angle_deg))
                final_insert_point = target_center - rotated_offset
                
                # This is the final call that actually draws the fixture into the DXF file.
                self.place_fixture(fixture, (final_insert_point.x, final_insert_point.y, 0), angle_deg, True, xscale=xscale, yscale=yscale)
                # Add the new fixture's bounding box to our master list of obstacles for future checks.
                placed_bboxes.append(new_bbox_tuple) 
            
            return new_bbox_tuple # Return the coordinates on success.
            
        return None # Return None on failure.
    
    def _validate_and_place_in_open_space(self, fixture, target_center, angle_deg, placed_bboxes, rotated, xscale=1.0, yscale=1.0):
        """
        ### MIRROR LOGIC ADDED ###
        Now accepts xscale and yscale to validate and place mirrored fixtures.
        """
        from shapely.geometry import Polygon
        from ezdxf.math import Matrix44, Vec2, BoundingBox2d
        import math

        # --- Step 1: Calculate the Transformation Matrix ---
        local_center = fixture.bounding_box.center
        angle = angle_deg
        if rotated:
            angle += 90
        transform = Matrix44.chain(
            # 1. Move fixture's center to origin (0,0).
            Matrix44.translate(-local_center.x, -local_center.y, 0),
            # 2. Apply mirroring.
            Matrix44.scale(xscale, yscale, 1.0),
            # 3. Rotate around origin.
            Matrix44.z_rotate(math.radians(angle)),
            # 4. Move to final target position.
            Matrix44.translate(target_center.x, target_center.y, 0)
        )

        # --- Step 2: Calculate the Fixture's Final Position and Shape ---
        world_corners = list(transform.transform_vertices(fixture.bounding_box.rect_vertices()))
        fixture_polygon = Polygon([(p.x, p.y) for p in world_corners])
        aabb = BoundingBox2d(world_corners)

        # # --- Step 3: Perform Validation Checks ---
        # is_inside = self.floorplan_polygon.contains(fixture_polygon)
        # is_overlapping = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

        # --- Step 3: Perform Validation Checks ---
        # --- MODIFICATION: Allow clinics to ignore wall and overlap checks ---
        is_inside = True # Assume it's valid by default
        is_overlapping = False # Assume it's not overlapping by default

        if "CLINIC" not in fixture.name.upper():
            # Only perform checks if the fixture is NOT a clinic
            is_inside = self.floorplan_polygon.contains(fixture_polygon)
            is_overlapping = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)
        # --- END OF MODIFICATION ---

        # --- Step 4: Place the Fixture if Valid ---
        if is_inside and not is_overlapping:
            # Correct the insertion point to account for the offset between the fixture's center and its file's origin (0,0).
            local_center_scaled = Vec2(local_center.x * xscale, local_center.y * yscale)
            # print(f"_____________________local_center_scaled: {local_center_scaled}_____________________")
            rotated_offset = local_center_scaled.rotate(math.radians(angle_deg))
            # print(f"_____________________rotated_offset: {rotated_offset}_____________________")
            translation = rotated_offset - local_center_scaled
            # print(f"_____________________translation: {translation}_____________________")
            if rotated:
                rotated_offset = rotated_offset.rotate(math.radians(90))
                angle_deg += 90
                # print(f"_____________________rotated_offset2: {rotated_offset}_____________________")
            final_insert_point = target_center - rotated_offset
            # print(f"_____________________final_insert_point: {final_insert_point}_____________________")
            final_insert_point = final_insert_point - translation
            # print(f"_____________________final_insert_point: {final_insert_point}_____________________")
            # if rotated:
            #     final_insert_point = Vec2(final_insert_point.x + fixture.height/2, final_insert_point.y - fixture.width/2)
            # else:
            #     final_insert_point = Vec2(final_insert_point.x + fixture.width/2, final_insert_point.y - fixture.height/2)
            # print(f"_____________________final_insert_point: {final_insert_point}_____________________")
            
            # Actually draw the fixture in the DXF file.
            print("wall_angle_deg for placement:", angle_deg)


            self.place_fixture(fixture, (final_insert_point.x, final_insert_point.y, 0), angle_deg, True, xscale=xscale, yscale=yscale)

            # Add the new fixture's bounding box to the master list of obstacles.
            new_bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)
            
            # print("Bounding box placed:", new_bbox_tuple)
            placed_bboxes.append(new_bbox_tuple) 
            
            
            return new_bbox_tuple # Return the coordinates on success.
            
        return None # Return None on failure.


    #------------new edit_foor wall_thickness for boh zone -----------------------------
    #------------new edit_foor wall_thickness for boh zone -----------------------------
    #------------new edit_foor wall_thickness for boh zone -----------------------------

    #------------new edit_foor wall_thickness for boh zone -----------------------------
    #------------new edit_foor wall_thickness for boh zone -----------------------------
    #------------new edit_foor wall_thickness for boh zone -----------------------------

    def _create_boh_room_from_zone(self, boh_zone_poly: Polygon, wall_thickness: float = 50.0, layer_name: str = "BOH_WALL", hatch_color: int = 252):
        """
        [ROBUST VERSION] Takes a Shapely Polygon OR MultiPolygon and draws it as a proper,
        hatched wall with a given thickness.
        """
        
        if not boh_zone_poly or boh_zone_poly.is_empty:
            return

        # --- NEW: Standardize the input to always be a list of polygons ---
        polygons_to_draw = []
        if boh_zone_poly.geom_type == 'MultiPolygon':
            # If it's a MultiPolygon, get the list of individual polygons
            polygons_to_draw = list(boh_zone_poly.geoms)
        elif boh_zone_poly.geom_type == 'Polygon':
            # If it's a single Polygon, put it inside a list to be processed in the same way
            polygons_to_draw = [boh_zone_poly]
        else:
            # If it's not a type we can handle, exit gracefully
            print(f"  -> WARNING: Cannot draw BOH zone from unexpected geometry type '{boh_zone_poly.geom_type}'.")
            return

        # --- NEW: Loop through each individual polygon and draw it ---
        for poly in polygons_to_draw:
            if poly.is_empty:
                continue

            # 1. Create the inner boundary for the current polygon
            # inner_boundary = poly.buffer(-wall_thickness)
            outer_boundary = poly.buffer(wall_thickness)

            # 2. Create a new hatch object for this polygon's wall fill
            hatch = self.msp.add_hatch(color=hatch_color)
            hatch.dxf.layer = layer_name
            
            # 3. Add the outer boundary of THIS polygon
            outer_path = hatch.paths.add_edge_path()
            outer_coords = list(poly.exterior.coords)
            for i in range(len(outer_coords) - 1):
                outer_path.add_line(outer_coords[i], outer_coords[i+1])

            # 4. Add the inner boundary as a "hole" if it exists
            if not outer_boundary.is_empty:
                inner_path = hatch.paths.add_edge_path()
                inner_coords = list(outer_boundary.exterior.coords)
                for i in range(len(inner_coords) - 1):
                    inner_path.add_line(inner_coords[i], inner_coords[i+1])

            # 5. Set the visual style of the hatch pattern
            hatch.set_pattern_fill('ANSI32', scale=10)
            hatch.dxf.pattern_angle = 90

            # 6. Add Explicit Wall Outlines for THIS polygon
            self.msp.add_lwpolyline(
                outer_coords, 
                close=True, 
                dxfattribs={"layer": f"{layer_name}_OUTLINE", "color": 251, "lineweight": 25}
            )
            if not outer_boundary.is_empty:
                self.msp.add_lwpolyline(
                    list(outer_boundary.exterior.coords), 
                    close=True, 
                    dxfattribs={"layer": f"{layer_name}_OUTLINE", "color": 251, "lineweight": 25}
                )
        
        print(f"  -> ✅ Drew BOH zone as a {wall_thickness}mm thick wall on layer '{layer_name}'.")


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

            cursor, margin_from_wall, gap_between_clinics = 4500.0, 50.0, 500.0

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
      
    


    def _expand_boh_zone_downwards_if_needed(self, initial_boh_poly: Polygon, initial_slicer_box: box, floorplan: Polygon) -> Polygon:
        """
        Checks if the initial BOH polygon meets a minimum area requirement.
        If not, it iteratively expands the polygon DOWNWARDS until it meets a
        target area or can no longer expand.
        """
        # --- 1. Define Constants ---
        MIN_BOH_SQFT = 80.0
        TARGET_BOH_SQFT = 60.0
        SQMM_PER_SQFT = 92903.04
        NUDGE_MM = 100.0
        MAX_ITERATIONS = 50 # Safety break

        # --- 2. Calculate Initial Area ---
        initial_area_sqft = initial_boh_poly.area / SQMM_PER_SQFT
        print(f"  -> Initial BOH zone area is {initial_area_sqft:.2f} sq. ft.")

        # --- 3. Check Condition and Start Expansion Loop ---
        if initial_area_sqft < MIN_BOH_SQFT:
            print(f"  -> Area is less than {MIN_BOH_SQFT} sq. ft. Attempting to expand downwards to at least {TARGET_BOH_SQFT} sq. ft.")
            
            current_poly = initial_boh_poly
            current_slicer = initial_slicer_box
            iterations = 0

            while (current_poly.area / SQMM_PER_SQFT) < TARGET_BOH_SQFT and iterations < MAX_ITERATIONS:
                iterations += 1
                
                min_x, min_y, max_x, max_y = current_slicer.bounds

                # ***** KEY CHANGE IS HERE *****
                # Expand the slicer box DOWNWARDS by subtracting from its min_y
                expanded_slicer_box = box(min_x, min_y - NUDGE_MM, max_x, max_y)
                
                new_poly = floorplan.intersection(expanded_slicer_box)

                if new_poly.is_empty or new_poly.area <= current_poly.area:
                    print(f"    -> Iteration {iterations}: Downward expansion failed to increase area. Stopping.")
                    break
                
                current_poly = new_poly
                current_slicer = expanded_slicer_box
                print(f"    -> Iteration {iterations}: Nudged bottom wall by {NUDGE_MM}mm. New area: {current_poly.area / SQMM_PER_SQFT:.2f} sq. ft.")

            # --- 4. Return the Final Polygon ---
            if (current_poly.area / SQMM_PER_SQFT) >= TARGET_BOH_SQFT:
                print(f"  -> ✅ Successfully expanded BOH zone to {current_poly.area / SQMM_PER_SQFT:.2f} sq. ft.")
                return current_poly
            else:
                print(f"  -> ⚠️ WARNING: Could not expand BOH to target area. Using last valid size of {current_poly.area / SQMM_PER_SQFT:.2f} sq. ft.")
                return current_poly
        
        return initial_boh_poly
    

    def create_boh_zone_from_last_clinic( self, placed_clinics_on_top_wall: list, placed_bboxes: list, big_partition_threshold_mm: float = 800.0):
        """
        [DEFINITIVE BOH STRATEGY V5] Creates the BOH zone.
        - Stops at the first partition that is both to the right AND within the
          same horizontal Y-range as the BOH itself.
        - Applies conditional 800mm gap for odd-numbered vertical clinics.
        """
        
        debug_layer_name = "DEBUG_STOPPER_PARTITIONS"
        if debug_layer_name not in self.doc.layers:
            self.doc.layers.add(name=debug_layer_name, color=1) # Color 1 is Red
        print(f"DEBUG: BOH zone is using a 'big_partition_threshold_mm' of {big_partition_threshold_mm}")

        print(f"  -> Checking for 'big' partitions (> {big_partition_threshold_mm}mm) to act as a hard boundary...")
        from shapely.geometry import box
        print("\n--- 🏛️  Creating BOH Zone Based on Final Clinic Position ---")

        if not placed_clinics_on_top_wall:
            print("  -> SKIPPED: No clinics were placed on the top wall to anchor the BOH.")
            return

        # 1. & 2. Find the anchor clinic and its details (Unchanged)
        anchor_clinic = max(placed_clinics_on_top_wall, key=lambda c: c['bbox'][2])
        anchor_bbox = anchor_clinic['bbox']
        anchor_orientation = anchor_clinic['orient']
        anchor_point_x = anchor_bbox[2]
        anchor_point_y = anchor_bbox[1]

        print(f"Clinic right-bottom corner: x={anchor_bbox[2]:.2f}, y={anchor_bbox[1]:.2f}")
        print(f"  -> Anchoring to '{anchor_clinic['fxtr'].name}' (Orientation: {anchor_orientation}).")

        # Conditional Gap Logic (Unchanged)
        total_vertical_clinics = sum(1 for clinic in placed_clinics_on_top_wall if clinic['orient'] == 'V')
        print(f"  -> Total vertical clinics on top wall: {total_vertical_clinics}")
        start_x = anchor_point_x
        if anchor_orientation == 'V' and total_vertical_clinics % 2 != 0:
            start_x += 800.0
            print(f"  -> Applying 800mm gap: Anchor is vertical and total V-count ({total_vertical_clinics}) is odd.")
        else:
            print(f"  -> SKIPPING 800mm gap: Condition not met (Anchor orient: {anchor_orientation}, V-count: {total_vertical_clinics}).")

    
        

        print("  -> Checking for internal partitions within the BOH's Y-range...")
        boh_max_x = self.cvc.max_x + 1000 
        stopper_partitions = self.cvc.get_internal_wall_partitions_boh(
            min_length_mm=big_partition_threshold_mm, 
            thickness=0,
            msp_debug=None #self.msp  
        )
              

        print("  -> Filtering for partitions that are connected AND vertical...")
        proximity_threshold = 1.0
        verticality_ratio = 2.0  # Wall must be twice as tall as it is wide
        perimeter_stoppers = []
        perimeter_corners = [Vec2(c) for c in self.cvc.corners]

        for partition_data in stopper_partitions:
            p1 = Vec2(partition_data['endpoints'][:2])
            p2 = Vec2(partition_data['endpoints'][2:])
            
            # 1. Check if it's connected to the main perimeter (same as before)
            p1_is_connected = any(p1.distance(corner) < proximity_threshold for corner in perimeter_corners)
            p2_is_connected = any(p2.distance(corner) < proximity_threshold for corner in perimeter_corners)
            
            is_connected = p1_is_connected or p2_is_connected

            # --- NEW: 2. Check if the partition is significantly vertical ---
            dy = abs(p2.y - p1.y)
            dx = abs(p2.x - p1.x)
            is_vertical = (dy > dx * verticality_ratio)
            
            if is_connected and is_vertical:
                perimeter_stoppers.append(partition_data['bbox']) # Keep this partition
            elif is_connected:
                print(f"    -> Discarding connected but non-vertical partition at x={p1.x:.0f}")
            else:
                print(f"    -> Discarding internal partition at x={p1.x:.0f}")

        print(f"    -> Kept {len(perimeter_stoppers)} partitions that are connected AND vertical.")
        

        
        boh_min_y = anchor_point_y
        boh_max_y = self.cvc.max_y

        
        relevant_partitions = [
            p for p in perimeter_stoppers 
            if p[0] > start_x and (boh_min_y < p[3] and p[1] < boh_max_y)
        ]
        
        if relevant_partitions:
            first_partition = min(relevant_partitions, key=lambda p: p[0])
            boh_max_x = first_partition[0]
            print(f"    -> ✅ Found partition in path at x={boh_max_x:.0f}. BOH zone will stop here.")
        else:
            print("    -> No blocking partitions found in path. BOH will extend to the room's natural edge.")

        

        # 4. Create and draw the BOH zone (Unchanged)
        boh_box = box(start_x, anchor_point_y, boh_max_x, self.cvc.max_y + 1000)
        
        final_boh_poly = self.floorplan_polygon.intersection(boh_box)

        
        final_boh_poly = self._expand_boh_zone_downwards_if_needed(final_boh_poly, boh_box, self.floorplan_polygon)
        
        if final_boh_poly.is_empty:
            print("  -> ⚠️ FAILED: The calculated BOH zone resulted in an empty area.")
            return
            
        self._create_boh_room_from_zone(final_boh_poly, layer_name="BOH_WALL_VALID")
        placed_bboxes.append(final_boh_poly.bounds)

    
    def _calculate_opportunistic_boh_zone(self, last_clinic_bbox: tuple, placed_bboxes: List[tuple], last_clinic_orientation: str) -> Tuple[Optional[Polygon], float]:
        """
        [ROBUST VERSION 2] Calculates the BOH zone by subtracting the retail area
        from the entire floorplan, making it robust against complex wall shapes.
        """
        from shapely.geometry import box, Polygon

        lc_min_x, lc_min_y, lc_max_x, lc_max_y = last_clinic_bbox
        fp_min_x, fp_min_y, fp_max_x, fp_max_y = self.floorplan_polygon.bounds
        
        # Add a horizontal gap for vertically placed clinics
        start_x_for_cutout = lc_max_x
        if last_clinic_orientation == 'V':
            print("    -> 💡 Applying architectural rule: Adding 800mm horizontal gap for vertical clinic.")
            start_x_for_cutout += 800.0

        # --- NEW ROBUST LOGIC ---
        # 1. Create a "retail mask" polygon. This is a large box that represents
        #    everything that is NOT the BOH (i.e., the area to the left of the last clinic).
        #    We make it extra tall to ensure it covers the full height of the floorplan.
        retail_mask = box(fp_min_x - 1000, fp_min_y - 1000, start_x_for_cutout, fp_max_y + 1000)

        # 2. The BOH zone is the entire floorplan with the retail area "carved out" or subtracted.
        #    This correctly handles any wall indentations or complex shapes.
        boh_zone_poly = self.floorplan_polygon.difference(retail_mask)
        # --- END OF NEW LOGIC ---

        # Safety check for overlaps (this logic remains the same)
        if any(boh_zone_poly.intersects(box(*b)) for b in placed_bboxes):
            return None, 0.0

        area_in_sqmm = boh_zone_poly.area
        SQMM_PER_SQFT = 92903.04
        area_in_sqft = area_in_sqmm / SQMM_PER_SQFT
        
        return boh_zone_poly, area_in_sqft

    def _calculate_opportunistic_boh_zone_real_one_need_to_use_future_for_arekere_adjustment_we_do_dont_use_it_now(self, last_clinic_bbox: tuple, placed_bboxes: List[tuple], last_clinic_orientation: str, big_partition_threshold_mm: float = 800.0) -> Tuple[Optional[Polygon], float]:
        """
        [ROBUST VERSION 3 - PARTITION AWARE] Calculates the BOH zone by subtracting the retail area
        from the entire floorplan, AND now stops at the first major internal partition.
        """
        from shapely.geometry import box, Polygon

        lc_min_x, lc_min_y, lc_max_x, lc_max_y = last_clinic_bbox
        fp_min_x, fp_min_y, fp_max_x, fp_max_y = self.floorplan_polygon.bounds
        
        # Add a horizontal gap for vertically placed clinics
        start_x_for_boh = lc_max_x
        if last_clinic_orientation == 'V':
            print("    -> (Verification) Applying architectural rule: Adding 800mm horizontal gap for vertical clinic.")
            start_x_for_boh += 800.0

        # --- NEW: PARTITION DETECTION LOGIC (Mirrors create_boh_zone_from_last_clinic) ---
        boh_max_x = self.cvc.max_x + 1000 
        stopper_partitions = self.cvc.get_internal_wall_partitions_boh(
            min_length_mm=big_partition_threshold_mm, 
            thickness=0,
            msp_debug=None
        )
        
        boh_min_y_for_check = lc_min_y
        boh_max_y_for_check = self.cvc.max_y

        relevant_partitions = [
            p['bbox'] for p in stopper_partitions 
            if p['bbox'][0] > start_x_for_boh and (boh_min_y_for_check < p['bbox'][3] and p['bbox'][1] < boh_max_y_for_check)
        ]
        
        if relevant_partitions:
            first_partition = min(relevant_partitions, key=lambda p: p[0])
            boh_max_x = first_partition[0]
            print(f"    -> (Verification) Found partition in path at x={boh_max_x:.0f}. Potential BOH zone will stop here.")
        else:
            print("    -> (Verification) No blocking partitions found. Potential BOH will extend to room's natural edge.")
        # --- END OF NEW LOGIC ---

        # Create a box representing the potential BOH area, respecting the partition stop.
        boh_zone_box = box(start_x_for_boh, lc_min_y, boh_max_x, fp_max_y + 1000)
        boh_zone_poly = self.floorplan_polygon.intersection(boh_zone_box)

        # Safety check for overlaps (this logic remains the same)
        if any(boh_zone_poly.intersects(box(*b)) for b in placed_bboxes):
            return None, 0.0

        area_in_sqmm = boh_zone_poly.area
        SQMM_PER_SQFT = 92903.04
        area_in_sqft = area_in_sqmm / SQMM_PER_SQFT
        
        return boh_zone_poly, area_in_sqft
    

    def _find_and_place_row_in_zone(self, zone, layouts_ranked: list, clinics_queue, placed_bboxes, placed_clinics_on_top_wall,start_vertical_count: int = 0):
        """
        [DEFINITIVE VERSION] Finds the single best placement for a row of clinics within
        an entire zone without creating the BOH. It is no longer "eager" and will
        search all positions to find the optimal spot for the best layout.
        """
        from shapely.geometry import Point
        from ezdxf.math import Vec2

        if not layouts_ranked:
            return 0

        p1, p2 = zone['start'], zone['end']
        wall_vector = (p2 - p1).normalize()
        wall_angle_deg = math.degrees(wall_vector.angle)
        print("wall angle deg:", wall_angle_deg)
        inward_normal = wall_vector.orthogonal().normalize()
        if not self.floorplan_polygon.contains(Point(p1 + inward_normal)): inward_normal *= -1

        # --- 1. Find the best possible placement WITHOUT drawing anything yet ---
        
        # This variable will store our final choice after searching the whole zone.
        best_placement_details = None
        final_vertical_count_state = start_vertical_count

        # Loop through every possible start position in the zone.
        search_cursor = 10.0
        while search_cursor < zone['length'] - 50.0:
            # Loop through every ranked layout, from best to worst.
            for layout in layouts_ranked:
                row_fixtures = layout['fixtures_for_row']
                total_row_width = sum((f.width if o == 'H' else f.height) for f, o in zip(row_fixtures, layout['combo'])) + sum(layout['gaps'])
                if search_cursor + total_row_width > zone['length'] - 50.0:
                    continue

                is_entire_row_valid = True
                hypothetical_placements = []
                validation_cursor = search_cursor
                vertical_clinic_count = start_vertical_count
                for i in range(len(row_fixtures)):
                    fxtr, orient = row_fixtures[i], layout['combo'][i]
                    w = fxtr.width if orient == 'H' else fxtr.height
                    center_on_wall = p1  + wall_vector * (validation_cursor + w / 2)
                    # target_center = center_on_wall + inward_normal * (50.0 + (fxtr.height if orient == 'H' else fxtr.width) / 2)
                    # target_center = center_on_wall + inward_normal * (-100.0 + (fxtr.height if orient == 'H' else fxtr.width) / 2)
                    # --- MODIFICATION: Add a leftward push for wall overlap ---
                    # Calculate the standard inward position
                    inward_position = center_on_wall + inward_normal * (-100.0 + (fxtr.height if orient == 'H' else fxtr.width) / 2)
                    # Add a constant vector pushing the fixture to the left
                    leftward_push_vector = Vec2(-100, 0) # Push 100mm to the left
                    target_center = inward_position + leftward_push_vector
                    # --- END OF MODIFICATION ---


                    # snapped_angle_deg = round(wall_angle_deg / 90.0) * 90.0
                    rotation = wall_angle_deg + 90 if orient == 'V' else wall_angle_deg
                    # rotation = snapped_angle_deg if orient == 'H' else snapped_angle_deg + 90
                    # --- CORRECTED MIRRORING LOGIC ---
                    if orient == 'H':
                        # Horizontal clinics are mirrored horizontally
                        xscale, yscale = -1.0, 1.0
                    else:  # This handles the case where orient == 'V'
                        # Vertical clinics are mirrored horizontally by default
                        xscale, yscale = 1.0, 1.0
                        
                        # We keep the alternating vertical flip for creating symmetrical pairs
                        vertical_clinic_count += 1
                        if vertical_clinic_count % 2 == 0:
                            yscale = -1.0
                    # --- END OF CORRECTION ---
                    
                    hypothetical_bbox = self._validate_and_place_on_wall(fxtr, target_center, rotation, placed_bboxes, xscale=xscale, yscale=yscale, place_actually=False)
                    if not hypothetical_bbox:
                        is_entire_row_valid = False
                        break
                    
                    hypothetical_placements.append({'fxtr': fxtr, 'orient': orient, 'center': target_center, 'rot': rotation, 'bbox': hypothetical_bbox, 'xscale': xscale, 'yscale': yscale})
                    validation_cursor += w + layout['gaps'][i]

                # If the entire row was valid at this spot...
                if is_entire_row_valid:
                    # ...we've found the best possible solution for the whole zone because
                    # we check the best layouts first at the earliest positions.
                    best_placement_details = hypothetical_placements
                    # Break the inner 'for' loop since we've found the best layout for this spot.
                    break 
            
            # If we stored a choice in the inner loop, we can also break the outer 'while' loop.
            if best_placement_details is not None:
                break
            
            # If we haven't found a placement yet, nudge the main cursor forward.
            search_cursor += 10

        # # --- 2. If a best placement was found, COMMIT it now ---
        if best_placement_details:
            print(f"    -> ✅ Best spot found. Committing {len(best_placement_details)} clinics to the wall.")
            
            # --- MODIFIED: This loop now places fixtures directly without re-validating ---
            for details in best_placement_details:
                # Get all details from our pre-validated plan
                fxtr = details['fxtr']
                target_center = details['center']
                rotation = details['rot']
                xscale = details['xscale']
                yscale = details['yscale']
                pre_validated_bbox = details['bbox']

                # --- Direct Placement Logic ---
                # Calculate the final insertion point needed by place_fixture()
                local_center = fxtr.bounding_box.center
                local_center_scaled = Vec2(local_center.x * xscale, local_center.y * yscale)
                rotated_offset = local_center_scaled.rotate(math.radians(rotation))
                final_insert_point = target_center - rotated_offset
                
                # Place the fixture without any overlap checks
                block_ref = self.place_fixture(
                    fxtr, 
                    (final_insert_point.x, final_insert_point.y, 0), 
                    rotation, True, xscale=xscale, yscale=yscale
                )
                
                # --- Update all state lists ---
                placed_bboxes.append(pre_validated_bbox) # Add the pre-validated bbox to obstacles
                
                details['block_ref'] = block_ref # Store the entity reference for the "undo" function
                placed_clinics_on_top_wall.append(details)
                clinics_queue.popleft()

                if details['orient'] == 'V':
                    final_vertical_count_state += 1

            return len(best_placement_details), final_vertical_count_state
        
        return 0, start_vertical_count
    
    
    
   
    
 
    ##--new-test--with---greedy method-- strategy -----space for boh
    ##--new-test--with---greedy method-- strategy -----space for boh----in top row itself


    def place_clinics_master_strategy_og(self, placed_bboxes: List[tuple]):
        """
        [MODIFIED with "Place-Then-Verify" logic]
        Places all top-wall clinics first, then verifies if a valid BOH can be
        created. If not, it "undoes" the last clinic placement.
        [MASTER STRATEGY] Merges "Smart Walk" with a "Resilient Sliding Search"
        and "Opportunistic BOH" placement logic for the most robust placement.
        """
        self.clinic_placement_method = 'Unknown'
        # from Fixture import Fixture
        from shapely.geometry import Polygon, LineString, Point
        from ezdxf.math import Vec2
        from ezdxf.bbox import extents
        import collections
        import math

        # Create a temporary obstacle list for clinics (Unchanged)
        obstacles_for_clinics = list(placed_bboxes)
        internal_wall_obstacles = self.cvc.get_internal_wall_partitions(1000,1200, 20) + self.cvc.get_internal_wall_partitions(2600,2800, 10)
        if internal_wall_obstacles:
            existing_obstacles = set(map(tuple, obstacles_for_clinics))
            new_obstacles = [obs for obs in internal_wall_obstacles if tuple(obs) not in existing_obstacles]
            if new_obstacles:
                obstacles_for_clinics.extend(new_obstacles)
                print(f"  -> Added {len(new_obstacles)} partitions to a temporary obstacle list FOR CLINIC PLACEMENT.")
        
        print("\n--- 🧠 Executing MASTER Clinic Placement (Place-Then-Verify Strategy) ---")

        # Setup and load clinic queue (Unchanged)
        clinic_config = self.fixtures.get("clinic_fixtures", {})
        clinics_queue = collections.deque([
            Fixture.Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"])
            for name, count in clinic_config.items() if count > 0 for _ in range(count)
        ])
        if not clinics_queue:
            print("  -> SKIPPED: No clinics to place.")
            return

        # =========================================================================
        # =========== PHASE 1: UNCONDITIONAL TOP-WALL PLACEMENT ===================
        # =========================================================================
        print("\n  -> Phase 1: Placing all possible clinics on the top wall...")
        top_wall_zones = self._analyze_top_wall_with_bulge_detection_new(
            small_bulge_max_width=1000, 
            small_bulge_max_depth=1000
        )
        
        placed_clinics_on_top_wall = []
        is_first_zone_processed = False
        first_row_orientation = 'H'
        total_vertical_clinics_placed_on_top = 0

        for zone in top_wall_zones:
            if not clinics_queue: break
            
            available_width = zone['length']
            print(f"\n  -> Analyzing placement zone of width {available_width:.0f}mm...")

            clinic_names_for_solver = [fxtr.name for fxtr in clinics_queue]
            best_layouts_ranked = self._find_best_combination_for_row(clinic_names_for_solver, available_width,force_orientation='H')

            if not best_layouts_ranked:
                print("    -> No combination of remaining clinics fits in this zone.")
                continue

            print(f"    -> Best layout for this zone: {best_layouts_ranked[0]['combo']}")

            # This helper function now just places clinics without BOH checks
            placed_count, total_vertical_clinics_placed_on_top = self._find_and_place_row_in_zone(
                zone, 
                best_layouts_ranked, 
                clinics_queue, 
                obstacles_for_clinics, # Use the temporary list with partitions
                placed_clinics_on_top_wall,
                start_vertical_count=total_vertical_clinics_placed_on_top
            ) # type: ignore

            if placed_count > 0 and not is_first_zone_processed:
                best_layout_used = best_layouts_ranked[0]
                h_count = best_layout_used['combo'].count('H')
                v_count = len(best_layout_used['fixtures_for_row']) - h_count
                first_row_orientation = 'H' if h_count >= v_count else 'V'
                is_first_zone_processed = True

        # =========================================================================
        # =========== PHASE 2 & 3: FINAL BOH CHECK AND "UNDO" LOGIC ===============
        # =========================================================================
        print("\n  -> Phase 2: Performing final BOH verification...")
        if not placed_clinics_on_top_wall:
            print("    -> No clinics were placed on the top wall. Skipping BOH check.")
        else:
            # Find the absolute right-most clinic from Phase 1
            final_anchor_clinic_details = max(placed_clinics_on_top_wall, key=lambda c: c['bbox'][2])
            
            
            # --- MODIFICATION: Pass the partition threshold to the verification function ---
            boh_zone_poly, boh_area_sqft = self._calculate_opportunistic_boh_zone(
                final_anchor_clinic_details['bbox'],
                [], # Pass empty obstacles as we only care about potential area
                final_anchor_clinic_details['orient'],
                # big_partition_threshold_mm=800.0 # Use the same threshold as the final drawing function
            )
            # --- END OF MODIFICATION ---
            print(f"    -> Final check: Potential BOH area is {boh_area_sqft:.2f} sq. ft.")

            # Define your mandatory minimum area
            MINIMUM_BOH_AREA = 200.0
            
            if boh_area_sqft >= MINIMUM_BOH_AREA:
                print("    -> ✅ Verification PASSED. Committing layout and drawing BOH.")
                # The layout is valid, so now we draw the BOH for real.
                self.clinic_placement_method = 'Plan_A'
                self.create_boh_zone_from_last_clinic(placed_clinics_on_top_wall, placed_bboxes)
            else:
                print(f"    -> ❌ Verification FAILED. BOH area is less than {MINIMUM_BOH_AREA} sq. ft.")
                # The layout is invalid. Call your new helper to "undo" the last placement.
                self._undo_last_clinic_placement(final_anchor_clinic_details, clinics_queue, placed_bboxes, placed_clinics_on_top_wall)
                # -------
                print("    -> Re-evaluating BOH zone with the updated clinic layout...")
                # This call will now use the modified 'placed_clinics_on_top_wall' list
                # to draw the BOH in the newly available space.
                self.create_boh_zone_from_last_clinic(placed_clinics_on_top_wall, placed_bboxes)
              
        # --- FALLBACK LOGIC  ---
        if clinics_queue:
            self.clinic_placement_method = 'Plan_B'
            print(f"\n  -> Plan B: {len(clinics_queue)} clinics remain. Starting Fallback (Row-by-Row)...")
            self._place_clinics_fallback_row_by_row(
                clinics_queue,
                placed_bboxes,
                placed_clinics_on_top_wall,
                first_row_orientation
            )    

        if clinics_queue:
            print(f"\n  -> {len(clinics_queue)} clinics still remain. Starting Final Fallback (Perimeter Walk)...")
            self.place_clinics_by_perimeter_walk(list(clinics_queue), obstacles_for_clinics)

        print("\n✅ Master clinic placement process complete.")

    

    def place_clinics_master_strategy(self, placed_bboxes: List[tuple]):
        """
        [MODIFIED with "Place-Then-Verify" logic]
        Places all top-wall clinics first, then verifies if a valid BOH can be
        created. If not, it "undoes" the last clinic placement.
        [MASTER STRATEGY] Merges "Smart Walk" with a "Resilient Sliding Search"
        and "Opportunistic BOH" placement logic for the most robust placement.
        """
        self.clinic_placement_method = 'Unknown'
        # from Fixture import Fixture
        from shapely.geometry import Polygon, LineString, Point
        from ezdxf.math import Vec2
        from ezdxf.bbox import extents
        import collections
        import math

        # Create a temporary obstacle list for clinics (Unchanged)
        obstacles_for_clinics = list(placed_bboxes)
        internal_wall_obstacles = self.cvc.get_internal_wall_partitions(1000,1200, 20) + self.cvc.get_internal_wall_partitions(2600,2800, 10)
        if internal_wall_obstacles:
            existing_obstacles = set(map(tuple, obstacles_for_clinics))
            new_obstacles = [obs for obs in internal_wall_obstacles if tuple(obs) not in existing_obstacles]
            if new_obstacles:
                obstacles_for_clinics.extend(new_obstacles)
                print(f"  -> Added {len(new_obstacles)} partitions to a temporary obstacle list FOR CLINIC PLACEMENT.")
        
        print("\n--- 🧠 Executing MASTER Clinic Placement (Place-Then-Verify Strategy) ---")

        # Setup and load clinic queue (Unchanged)
        clinic_config = self.fixtures.get("clinic_fixtures", {})
        clinics_queue = collections.deque([
            Fixture.Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"])
            for name, count in clinic_config.items() if count > 0 for _ in range(count)
        ])
        if not clinics_queue:
            print("  -> SKIPPED: No clinics to place.")
            return

        # =========================================================================
        # =========== PHASE 1: UNCONDITIONAL TOP-WALL PLACEMENT ===================
        # =========================================================================
        print("\n  -> Phase 1: Placing all possible clinics on the top wall...")
        top_wall_zones = self._analyze_top_wall_with_bulge_detection_new(
            small_bulge_max_width=1000, 
            small_bulge_max_depth=1000
        )
        
        placed_clinics_on_top_wall = []
        is_first_zone_processed = False
        first_row_orientation = 'H'
        total_vertical_clinics_placed_on_top = 0

        for zone in top_wall_zones:
            if not clinics_queue: break
            
            available_width = zone['length']
            print(f"\n  -> Analyzing placement zone of width {available_width:.0f}mm...")

            clinic_names_for_solver = [fxtr.name for fxtr in clinics_queue]
            best_layouts_ranked = self._find_best_combination_for_row(clinic_names_for_solver, available_width,force_orientation='H')

            if not best_layouts_ranked:
                print("    -> No combination of remaining clinics fits in this zone.")
                continue

            print(f"    -> Best layout for this zone: {best_layouts_ranked[0]['combo']}")

            # This helper function now just places clinics without BOH checks
            placed_count, total_vertical_clinics_placed_on_top = self._find_and_place_row_in_zone(
                zone, 
                best_layouts_ranked, 
                clinics_queue, 
                obstacles_for_clinics, # Use the temporary list with partitions
                placed_clinics_on_top_wall,
                start_vertical_count=total_vertical_clinics_placed_on_top
            ) # type: ignore

            if placed_count > 0 and not is_first_zone_processed:
                best_layout_used = best_layouts_ranked[0]
                h_count = best_layout_used['combo'].count('H')
                v_count = len(best_layout_used['fixtures_for_row']) - h_count
                first_row_orientation = 'H' if h_count >= v_count else 'V'
                is_first_zone_processed = True

        # =========================================================================
        # =========== PHASE 2 & 3: FINAL BOH CHECK AND "UNDO" LOGIC ===============
        # =========================================================================
        print("\n  -> Phase 2: Performing final BOH verification...")
        if not placed_clinics_on_top_wall:
            print("    -> No clinics were placed on the top wall. Skipping BOH check.")
        else:
            # Find the absolute right-most clinic from Phase 1
            final_anchor_clinic_details = max(placed_clinics_on_top_wall, key=lambda c: c['bbox'][2])
            
            
            # --- MODIFICATION: Pass the partition threshold to the verification function ---
            boh_zone_poly, boh_area_sqft = self._calculate_opportunistic_boh_zone(
                final_anchor_clinic_details['bbox'],
                [], # Pass empty obstacles as we only care about potential area
                final_anchor_clinic_details['orient'],
                # big_partition_threshold_mm=800.0 # Use the same threshold as the final drawing function
            )
            # --- END OF MODIFICATION ---
            print(f"    -> Final check: Potential BOH area is {boh_area_sqft:.2f} sq. ft.")

            # Define your mandatory minimum area
            MINIMUM_BOH_AREA = 200.0
            
            if boh_area_sqft >= MINIMUM_BOH_AREA:
                print("    -> ✅ Verification PASSED. Committing layout and drawing BOH.")
                # The layout is valid, so now we draw the BOH for real.
                self.clinic_placement_method = 'Plan_A'
                self.create_boh_zone_from_last_clinic(placed_clinics_on_top_wall, placed_bboxes)
            else:
                print(f"    -> ❌ Verification FAILED. BOH area is less than {MINIMUM_BOH_AREA} sq. ft.")
                # The layout is invalid. Call your new helper to "undo" the last placement.
                self._undo_last_clinic_placement(final_anchor_clinic_details, clinics_queue, placed_bboxes, placed_clinics_on_top_wall)
                # -------
                print("    -> Re-evaluating BOH zone with the updated clinic layout...")
                # This call will now use the modified 'placed_clinics_on_top_wall' list
                # to draw the BOH in the newly available space.
                self.create_boh_zone_from_last_clinic(placed_clinics_on_top_wall, placed_bboxes)
              
        # --- FALLBACK LOGIC  ---
        if clinics_queue:
            
            print(f"\n  -> Plan B: {len(clinics_queue)} clinics remain. Starting Fallback Strategies...")
            self.clinic_placement_method = 'Plan_B'
            # --- Strategy 2: Place directly under the first row ---
            self.place_clinic_under_first_row(
                clinics_queue=clinics_queue,
                placed_bboxes=placed_bboxes,
                placed_clinics_on_top_wall=placed_clinics_on_top_wall
            )
            print("completed placing under first row")
            

        if clinics_queue:
            # --- Strategy 3: Fallback to Row-by-Row Placement ---
            self.clinic_placement_method = 'Plan_B' # Set method for this fallback
            print(f"\n  -> {len(clinics_queue)} clinics remain. Starting Fallback (Row-by-Row)...")
            self._place_clinics_fallback_row_by_row(
                clinics_queue,
                placed_bboxes,
                placed_clinics_on_top_wall,
                first_row_orientation
            )    

        if clinics_queue:
            print(f"\n  -> {len(clinics_queue)} clinics still remain. Starting Final Fallback (Perimeter Walk)...")
            self.place_clinics_by_perimeter_walk(list(clinics_queue), obstacles_for_clinics)

        print("\n✅ Master clinic placement process complete.")


    def _draw_and_register_clinic_bboxes(self, placed_bboxes: List[tuple]):
        """
        Iteratively finds all placed clinic fixtures, draws their bounding boxes 
        as polygons on unique layers (e.g., LAYER_CLINIC_1), and adds the 
        coordinates to the master placed_bboxes list.
        
        CORRECTION: Uses entity.virtual_entities() to ensure rotation and scale 
        (including yscale=-1.0 for mirroring) are correctly applied before 
        calculating extents.
        """
        from ezdxf.bbox import extents
        from ezdxf.math import Vec2, Matrix44, BoundingBox
        import math
        
        print("\n--- 🎨 Drawing and Registering Clinic Bounding Boxes (CORRECTED) ---")
        
        # 1. Identify all clinic entities
        clinic_entities = [
            e for e in self.msp.query('INSERT') 
            if "CLINIC" in e.dxf.name.upper()
        ]

        if not clinic_entities:
            print("  -> No clinic fixtures found to process.")
            return

        # 2. Sort clinics by their placement order (based on suffix number)
        def get_clinic_number(entity):
            try: return int(entity.dxf.name.split('_')[-1])
            except (ValueError, IndexError): return 0
        
        clinic_entities.sort(key=get_clinic_number)
        
        existing_clinic_bboxes_count = 0
        
        for i, entity in enumerate(clinic_entities):
            clinic_number = get_clinic_number(entity)
            if clinic_number == 0:
                clinic_number = i + 1

            layer_name = f"LAYER_CLINIC_{clinic_number}"
            
            try:
                # *******************************************************************
                # ************ THE CRITICAL CORRECTION IS HERE ************
                # ezdxf.bbox.extents on a simple INSERT entity does not reliably account 
                # for non-uniform scaling (yscale=-1.0). virtual_entities() yields 
                # the transformed geometry in WCS, making the bounding box correct.
                # *******************************************************************
                
                # Use virtual_entities to get the fully transformed geometry
                transformed_entities = list(entity.virtual_entities())
                if not transformed_entities:
                    print(f"  -> ⚠️ Skipping '{entity.dxf.name}': No transformed entities found.")
                    continue
                    
                bbox = extents(transformed_entities)

                # Standard check for valid bbox data
                if not bbox.has_data:
                    print(f"  -> ⚠️ Skipping '{entity.dxf.name}': Calculated bbox has no data.")
                    continue
                    
                min_x, min_y, _, max_x, max_y, _ = bbox.extmin.x, bbox.extmin.y + 100, bbox.extmin.z, bbox.extmax.x, bbox.extmax.y, bbox.extmax.z
                
                # --- NEW: Limit width for horizontally placed clinics ---
                rotation = entity.dxf.rotation
                is_horizontal = (abs(rotation) < 5) or (abs(rotation - 180) < 5)
                
                # Define the 4 corners of the bounding box
                points = [
                    (min_x, min_y),
                    (max_x, min_y),
                    (max_x, max_y),
                    (min_x, max_y)
                ]

                if is_horizontal:
                    width = max_x - min_x
                    if width > 2600.0:
                        print(f"  -> Limiting width of '{entity.dxf.name}' to 2600mm and applying rotation.")
                        
                        height = max_y - min_y
                        new_width = 2600.0
                        
                        # Define the corners of the new 2600mm wide box at the origin, anchored at its own bottom-left
                        local_corners = [
                            Vec2(0, 0), Vec2(new_width, 0),
                            Vec2(new_width, height), Vec2(0, height)
                        ]
                        
                        # Create a transformation matrix to rotate and move the box
                        # It rotates around the origin (0,0) and then translates to the final position
                        transform = Matrix44.chain(
                            Matrix44.z_rotate(math.radians(rotation)),
                            Matrix44.translate(min_x, min_y, 0)
                        )
                        
                        # Apply the transformation to get the final world coordinates
                        points = [(p.x, p.y) for p in transform.transform_vertices(local_corners)]
                        
                        # Recalculate the axis-aligned bounding box for registration
                        # --- FIX: Use BoundingBox for coordinate tuples, not extents() ---
                        new_bbox = BoundingBox(points)
                        min_x, min_y = new_bbox.extmin.x, new_bbox.extmin.y
                        max_x, max_y = new_bbox.extmax.x, new_bbox.extmax.y
                        # --- END OF FIX ---

                # --- END OF NEW CODE ---

                bbox_coords = (min_x, min_y, max_x, max_y)
                
                # Create a new layer if it doesn't exist (color 2 is Yellow)
                if layer_name not in self.doc.layers:
                    self.doc.layers.add(name=layer_name, color=2)

                # Add the polygon outline to the modelspace
                self.msp.add_lwpolyline(
                    points, 
                    close=True, 
                    dxfattribs={"layer": layer_name, "lineweight": 70}
                )

                # Add the bounding box to the master list of obstacles
                if bbox_coords not in placed_bboxes:
                    placed_bboxes.append(bbox_coords)
                    print(f"  -> ✅ Registered and drew bbox for '{entity.dxf.name}' on layer '{layer_name}'.")
                    existing_clinic_bboxes_count += 1
                else:
                     print(f"  -> ℹ️ Bbox for '{entity.dxf.name}' already registered. Drawing layer '{layer_name}'.")

            except Exception as e:
                print(f"  -> ⚠️ ERROR processing clinic '{entity.dxf.name}': {e}")
                continue

        print(f"  -> Finished. Added {existing_clinic_bboxes_count} new bounding boxes to the obstacle list.")

 

    def _analyze_first_row_clinic_until_boh_last(self, top_row_clinic_bboxes: list, y_offset: float = 0.0, min_segment_length: float = 1500.0) -> List[dict]:
        """
        [MODIFIED] Analyzes the space directly underneath a given list of bounding boxes
        by walking along their bottom edges. This is more accurate than walking the main floorplan wall.
        It now accepts a simple list of bbox tuples.
        """
        from ezdxf.math import Vec2
        print("    -> Analyzing space under first row via 'Direct Bounding Box Walk'...")

        if not top_row_clinic_bboxes:
            print("      -> No top-row bounding boxes provided. Cannot analyze space.")
            return []


        # print

        # --- FIX: Use actual rotated corners instead of axis-aligned bbox ---
        # 1. Sort the clinic data from left to right to create an ordered path
        sorted_clinics = sorted(top_row_clinic_bboxes, key=lambda clinic_dict: clinic_dict['bbox'][0])
        
        valid_zones = []
        
        # 2. Iterate through each clinic to define a placement zone underneath it
        for i, clinic_dict in enumerate(sorted_clinics):
            block_ref = clinic_dict.get('block_ref')
            if not block_ref:
                print(f"      -> WARNING: Clinic data at index {i} is missing 'block_ref'. Cannot get accurate corners. Skipping.")
                continue

            # Get the four real-world corners of the rotated/placed clinic
            corners = self.get_outer_rect_corners_shapely(block_ref)
            if len(corners) != 4:
                continue

            # Find the two bottom-most corners to define the segment
            corners.sort(key=lambda c: c[1]) # Sort by Y-coordinate
            p1 = Vec2(corners[0])
            p2 = Vec2(corners[1])

            # Create a zone from these two points, allowing any angle
            zone = self._create_zone_from_points(p1, p2, index=i, angle_threshold=0, angle_tolerance=0)
            if zone and zone['length'] >= min_segment_length:
                valid_zones.append(zone)
            elif zone:
                print(f"        - Zone {i} length ({zone['length']:.0f}mm) is less than minimum ({min_segment_length:.0f}mm). Discarding.")
        # --- END OF FIX ---

        print(f"      -> Direct BBox Walk complete. Found {len(valid_zones)} valid placement zones.")
        return valid_zones
    
    def _analyze_first_row_clinic_until_boh_last_og(self, top_row_clinic_bboxes: list, y_offset: float = 0.0, min_segment_length: float = 1500.0) -> List[dict]:
        """
        [MODIFIED] Analyzes the space directly underneath a given list of bounding boxes
        by walking along their bottom edges. This is more accurate than walking the main floorplan wall.
        It now accepts a simple list of bbox tuples.
        """
        from ezdxf.math import Vec2
        print("    -> Analyzing space under first row via 'Direct Bounding Box Walk'...")

        if not top_row_clinic_bboxes:
            print("      -> No top-row bounding boxes provided. Cannot analyze space.")
            return []


        print

        # 1. Sort the bounding boxes from left to right to create an ordered path
        # FIX: The input is a list of dictionaries, so we need to access the 'bbox' key.
        sorted_bboxes = sorted(top_row_clinic_bboxes, key=lambda clinic_dict: clinic_dict['bbox'][0])
        all_clinic_entities = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
        for e in all_clinic_entities:
            # print(e.dxf.insert)
            corners = self.get_outer_rect_corners_shapely(e)
            segs = [(Vec2(corners[i][0], corners[i][1]), Vec2(corners[(i+1)%4][0], corners[(i+1)%4][1])) for i, c in enumerate(corners)]
            # print(segs)
            seg_angles = {}
            min_angle = 360
            for s in segs:
                # print(s)
                p1 = s[0]
                p2 = s[1]
                start_pt, end_pt = (p1, p2) if p1.x < p2.x else (p2, p1)
        
                segment_vec = end_pt - start_pt
                # print(f"start: {start_pt}, end: {end_pt}, segment_vec: {segment_vec}")
                segment_angle = math.degrees(segment_vec.angle)
                print("Segment angle:", segment_angle)
                seg_angles[s] = segment_angle
                min_angle = min(min_angle, segment_angle)
            
            final_seg = []
            
            for key, value in seg_angles.items():
                if abs(value - min_angle) < 1:
                    if len(final_seg) == 0:
                        final_seg.append(key)
                    else:
                        min_y_key = min(key[0].y, key[1].y)
                        # print("final_seg: ", final_seg)
                        min_y_fseg = min(final_seg[0][0].y, final_seg[0][1].y)
                        if min_y_key < min_y_fseg:
                            final_seg[0] = key

            print(final_seg)
            print()
            
        valid_zones = []
        
        # 2. Iterate through each bounding box to define a placement zone
        for clinic_dict in sorted_bboxes:
            # FIX: Extract the bbox tuple from the dictionary
            bbox = clinic_dict['bbox']
            print(f"___________________________ bbox: {bbox}___________________________")
            min_x, min_y, max_x, _ = bbox
            
            segment_length = max_x - min_x

            # 3. If the segment is long enough, create a zone from it
            if segment_length >= min_segment_length:
                # The zone is defined by the bottom edge of the bounding box
                p1 = Vec2(min_x, min_y - y_offset)
                p2 = Vec2(max_x, min_y - y_offset)
                # p1 = Vec2(-7249.4444, 3914.6325)
                # p2 = Vec2(-2155.5434, 3665.2885)
                
                # Use the existing helper to create a standardized zone dictionary
                # Assuming angle 0 (horizontal) and a wide tolerance
                segment_angle = math.degrees(segment_vec.angle)
                print("Segment angle new", segment_angle)
                zone = self._create_zone_from_points(p1, p2, len(valid_zones), segment_angle)
                # print(zone)

                if zone:
                    print("append")
                    valid_zones.append(zone)
            else:
                print(f"      -> Skipping short segment (Length: {segment_length:.0f}mm)")

        print(f"      -> Direct BBox Walk complete. Found {len(valid_zones)} valid placement zones.")
        return valid_zones

    

    def get_outer_rect_corners_shapely(self, insert, flatten_dist=0.5, debug=False):
        from shapely.geometry import MultiPoint, Polygon, LineString
        import math
        from ezdxf.path import make_path
        """
        Returns 4 WCS corners (x, y, z) of the oriented minimum bounding rectangle (OBR)
        for a given INSERT using Shapely's minimum_rotated_rectangle.

        Requires: shapely
        """

        def _log(msg):
            if debug: print(msg)

        # ---------- collect WCS sample points from the INSERT (incl. nested) ----------
        pts = []

        def _add_xy(pt):
            pts.append((float(pt[0]), float(pt[1])))

        def _sample_arc(cx, cy, r, a0, a1, steps=48):
            if a1 < a0: a1 += 2*math.pi
            for i in range(steps+1):
                t = a0 + (a1-a0) * (i/steps)
                _add_xy((cx + r*math.cos(t), cy + r*math.sin(t)))

        def _collect(entity):
            dxft = entity.dxftype()

            # nested inserts (defensive)
            if dxft == "INSERT":
                for ve in entity.virtual_entities():
                    _collect(ve)
                return

            # generic path first (covers many entities)
            try:
                p = make_path(entity)
                for v in p.flattening(distance=flatten_dist):
                    _add_xy((v.x, v.y))
                return
            except Exception:
                pass

            # fallback handlers
            if dxft == "LINE":
                _add_xy(entity.dxf.start); _add_xy(entity.dxf.end)

            elif dxft in ("LWPOLYLINE", "POLYLINE"):
                if hasattr(entity, "get_points"):
                    for t in entity.get_points(): _add_xy((t[0], t[1]))
                elif hasattr(entity, "points"):
                    for p in entity.points(): _add_xy((p[0], p[1]))

            elif dxft == "CIRCLE":
                c = entity.dxf.center; r = float(entity.dxf.radius)
                _sample_arc(c.x, c.y, r, 0.0, 2*math.pi, steps=72)

            elif dxft == "ARC":
                c = entity.dxf.center; r = float(entity.dxf.radius)
                a0 = math.radians(float(entity.dxf.start_angle))
                a1 = math.radians(float(entity.dxf.end_angle))
                _sample_arc(c.x, c.y, r, a0, a1, steps=48)

            elif dxft == "ELLIPSE":
                # use make_path above normally; if here, sample roughly using major axis/ratio
                center = entity.dxf.center
                major = entity.dxf.major_axis
                ratio = float(entity.dxf.ratio)
                a0 = float(entity.dxf.start_param); a1 = float(entity.dxf.end_param)
                ux, uy = major.x, major.y
                a = math.hypot(ux, uy)
                if a > 0:
                    ux, uy = ux/a, uy/a
                    vx, vy = -uy, ux
                    b = a*ratio
                    if a1 < a0: a1 += 2*math.pi
                    for i in range(73):
                        t = a0 + (a1-a0)*(i/72)
                        x = center.x + a*math.cos(t)*ux + b*math.sin(t)*vx
                        y = center.y + a*math.cos(t)*uy + b*math.sin(t)*vy
                        _add_xy((x, y))

            elif dxft in ("TEXT", "MTEXT", "IMAGE", "SOLID", "TRACE", "3DFACE", "HATCH", "SPLINE", "DIMENSION", "LEADER"):
                # We already tried make_path; if it failed, try bbox as a last resort
                try:
                    bbox = entity.bbox()
                    if bbox.has_data:
                        (minx, miny, _), (maxx, maxy, _) = bbox.extmin, bbox.extmax
                        _add_xy((minx, miny)); _add_xy((maxx, miny))
                        _add_xy((maxx, maxy)); _add_xy((minx, maxy))
                except Exception:
                    pass

        # gather
        for ve in insert.virtual_entities():  # WCS-transformed virtual geometry
            _collect(ve)

        if not pts:
            _log("No geometry collected from INSERT; cannot compute rectangle.")
            return []

        # ---------- Shapely: minimum rotated rectangle ----------
        cloud = MultiPoint(pts)
        mrr = cloud.minimum_rotated_rectangle  # Polygon

        # Extract 4 unique corners (Shapely closes ring with the first again)
        coords = list(mrr.exterior.coords)
        if len(coords) < 4:
            return []
        # dedupe the closing point and ensure exactly 4
        uniq = []
        for x, y in coords:
            if not uniq or (abs(x-uniq[-1][0]) > 1e-9 or abs(y-uniq[-1][1]) > 1e-9):
                uniq.append((x, y))
        if len(uniq) == 5 and abs(uniq[0][0]-uniq[-1][0]) < 1e-9 and abs(uniq[0][1]-uniq[-1][1]) < 1e-9:
            uniq = uniq[:-1]

        # Order: Shapely already returns CCW; start from lower-left (in the rect's own frame)
        # Find index of the vertex with minimal (y, then x)
        start = min(range(len(uniq)), key=lambda i: (uniq[i][1], uniq[i][0]))
        ordered = uniq[start:] + uniq[:start]  # rotate list

        # return as (x, y, z)
        return [(float(x), float(y), 0.0) for (x, y) in ordered]    

    def draw_under_row_placement_zones(self):
        """
        [DEBUG HELPER] Visualizes the placement zones found by 
        _analyze_first_row_clinic_until_boh_last().
        """
        from ezdxf.bbox import extents
        print("\n--- 🎨 Drawing 'Under First Row' Placement Zones for Validation ---")

        # 1. Reconstruct the list of clinics placed on the top wall.
        all_clinic_entities = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
        if not all_clinic_entities:
            print("  -> No clinics found in the drawing to analyze.")
            return

        # Find the highest Y coordinate among all clinics to identify the top row.
        max_y = max(extents([c]).extmax.y for c in all_clinic_entities)
        
        # Consider clinics in a band near the top as being on the top wall.
        top_wall_clinic_entities = [c for c in all_clinic_entities if extents([c]).extmax.y > max_y - 1500]

        placed_clinics_on_top_wall = []
        for entity in top_wall_clinic_entities:
            bbox = extents([entity])
            bbox_tuple = (bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y)
            # --- FIX: Add the 'block_ref' to the dictionary ---
            placed_clinics_on_top_wall.append({
                'bbox': bbox_tuple,
                'block_ref': entity  # Add the entity itself as the block_ref
            })
            # --- END OF FIX ---
        
        
        if not placed_clinics_on_top_wall:
            print("  -> Could not identify any clinics on the top wall.")
            return

        # 2. Call the analysis function to get the zones.
        placement_zones = self._analyze_first_row_clinic_until_boh_last(placed_clinics_on_top_wall)

        if not placement_zones:
            print("  -> No placement zones were found to draw.")
            return

        # 3. Create a new, highly visible layer for the debug drawing.
        layer_name = "DEBUG_UNDER_ROW_ZONES"
        if layer_name not in self.doc.layers:
            self.doc.layers.add(name=layer_name, color=3)  # ACI color 3 is Green

        # 4. Iterate through the zones and draw each one.
        for zone in placement_zones:
            start_point = zone['start']
            end_point = zone['end']
            
            # Draw the line segment for the zone.
            self.msp.add_line(
                start_point, 
                end_point, 
                dxfattribs={"layer": layer_name, "lineweight": 70}            )

            # Add a text label to identify the zone.
            mid_point = Vec2(start_point).lerp(Vec2(end_point))
            self.msp.add_mtext(
                f"{zone['id']} ({zone['length']:.0f}mm)",
                dxfattribs={
                    'char_height': 150,
                    'insert': mid_point + Vec2(0, 100),                    'layer': layer_name
                }
            )
        
        print(f"  -> ✅ Drew {len(placement_zones)} 'under row' zones on layer '{layer_name}'.")

    def _create_zone_from_points(self, p1: 'Vec2', p2: 'Vec2', index: int, angle_threshold: float, angle_tolerance: float = 15.0) -> dict:
        """Helper to create a zone dictionary and check its angle."""
        from ezdxf.math import Vec2
        
        # Ensure p1 is left and p2 is right
        start_pt, end_pt = (p1, p2) if p1.x < p2.x else (p2, p1)
        
        segment_vec = end_pt - start_pt
        print(f"start: {start_pt}, end: {end_pt}, segment_vec: {segment_vec}")
        segment_angle = math.degrees(segment_vec.angle)

        # --- NEW: Print the calculated angle immediately ---
        print(f"      -> [DEBUG] For Zone {index}, calculated segment angle: {segment_angle:.2f}°")
        # --- END OF NEW CODE ---
        
        # Check if the angle is similar to the top wall's angle
        # angle_diff = abs((segment_angle - angle_threshold + 180) % 360 - 180)
        # if angle_diff > angle_tolerance:
        #     print(f"        - Zone {index} angle ({segment_angle:.1f}°) differs too much from top wall ({angle_threshold:.1f}°). Discarding.")
        #     return None

        # print(f"        - Zone {index} angle ({segment_angle:.1f}°) differs too much from top wall ({angle_threshold:.1f}°). Discarding.")
        # print("angle_diff:", angle_diff)

        zone = {
            "id": f"under_row_{index}",
            "start": (start_pt.x, start_pt.y),
            "end": (end_pt.x, end_pt.y),
            "length": segment_vec.magnitude,
            "angle": segment_angle
        }
        print(f"      -> Found valid zone '{zone['id']}' (Length: {zone['length']:.0f}mm, Angle: {zone['angle']:.1f}°)")
        return zone




    def _create_zone_from_points_og(self, p1: 'Vec2', p2: 'Vec2', index: int, segment_angle: float) -> dict:
        """Helper to create a zone dictionary using a pre-calculated angle."""
        from ezdxf.math import Vec2
        
        # Ensure p1 is left and p2 is right
        start_pt, end_pt = (p1, p2) if p1.x < p2.x else (p2, p1)
        
        segment_vec = end_pt - start_pt
        
        zone = {
            "id": f"under_row_{index}",
            "start": (start_pt.x, start_pt.y),
            "end": (end_pt.x, end_pt.y),
            "length": segment_vec.magnitude,
            "angle": segment_angle  # Use the angle passed into the function
        }
        print(f"      -> Found valid zone '{zone['id']}' (Length: {zone['length']:.0f}mm, Angle: {zone['angle']:.1f}°)")
        return zone


    def place_clinic_under_first_row(self, clinics_queue: collections.deque, placed_bboxes: list, placed_clinics_on_top_wall: list):
        """
        [CORRECTED] Attempts to place remaining clinics in zones directly underneath the first row.
        """
        from ezdxf.math import Vec2
        if not clinics_queue:
            return
        
        # --- NEW: Synchronize bounding boxes before analysis ---
        # print("    -> Synchronizing clinic bounding boxes before analyzing under-row space...")
        # self._draw_and_register_clinic_bboxes(placed_bboxes)
        # --- END OF NEW CODE ---

        # --- FIX: Check for 'orientation' first, then fall back to 'orient' ---
        first_row_orientation = 'H'
        if placed_clinics_on_top_wall:
            first_clinic = placed_clinics_on_top_wall[0]
            first_row_orientation = first_clinic.get('orientation', first_clinic.get('orient', 'H'))
        # --- END OF FIX ---

        force_orientation = 'V' if first_row_orientation == 'H' else 'H'

        self.clinic_placement_method = 'Plan_B'
        placed_clinics_plan_b = []
        placement_zones = self._analyze_first_row_clinic_until_boh_last(placed_clinics_on_top_wall)
        if not placement_zones:
            print("    -> No suitable zones found to place clinics under the first row.")
            return

        for zone in placement_zones:
            if not clinics_queue:
                break

            print(f"    -> Attempting to fill Zone '{zone['id']}' (width: {zone['length']:.0f}mm)")

            if not (-15 <= zone['angle'] <= 15):
                print(f"      -> ⚠️ Zone angle ({zone['angle']:.1f}°) is too steep. Switching to fallback placement.")
                self._place_clinics_fallback_row_by_row(
                    clinics_queue,
                    placed_bboxes,
                    placed_clinics_on_top_wall,
                    first_row_orientation
                )
                return # Exit this function as the fallback has taken over

            print(f"\t{zone}")
            
            clinic_names_for_solver = [f.name for f in clinics_queue]
            layouts_ranked = self._find_best_combination_for_row(clinic_names_for_solver, zone['length'], force_orientation=force_orientation)
            
            if not layouts_ranked:
                print(f"      -> No combination of remaining clinics fits in Zone '{zone['id']}'.")
                continue

            best_layout = layouts_ranked[0]
            print(f"      -> Best layout for zone: {len(best_layout['fixtures_for_row'])} clinics, combo: {best_layout['combo']}")

            current_x = zone['start'][0]
            y_pos = zone['start'][1]

            
            # --- FIX: Iterate through Fixture objects directly ---
            for i, fxtr in enumerate(best_layout['fixtures_for_row']):
                if not clinics_queue: break
                
                orient = best_layout['combo'][i]
                width, height = (fxtr.height, fxtr.width) if orient == 'V' else (fxtr.width, fxtr.height)
                # --- END OF FIX ---

                target_center_x = current_x + width / 2
                target_center_y = y_pos - height / 2
                target_center = Vec2(target_center_x, target_center_y)
                # # target_center = Vec2(target_center_x - x_trans, target_center_y + y_trans)
                angle = 90 if orient == 'V' else 0


                # angle += zone["angle"]

                new_bbox = self._validate_and_place_in_open_space(
                    fixture=fxtr,
                    target_center=target_center,
                    angle_deg=zone["angle"],
                    placed_bboxes=placed_bboxes,
                    rotated=(angle==90)
                )
    

                if new_bbox:

                    placed_clinics_plan_b.append({
                        'bbox': new_bbox, 
                        # 'fxtr': fxtr, 
                        # 'orient': orientation
                    })
                    print(f"      -> ✅ Successfully placed '{fxtr.name}' under first row.",placed_clinics_plan_b)
                    last_right_bottom = (new_bbox[2], new_bbox[1])  # (max_x, min_y)
                    print(f"[Plan B - Under First Row] Placed clinic right-bottom: x={new_bbox[2]:.2f}, y={new_bbox[1]:.2f}")
                    print(f"        -> ✅ Placed '{fxtr.name}' at ({target_center.x:.0f}, {target_center.y:.0f})")
                    
                    # Find and remove the specific clinic instance from the queue
                    for item in list(clinics_queue):
                        if item.name == fxtr.name:
                            clinics_queue.remove(item)
                            break
                    
                    current_x += width + best_layout['gaps'][i]
                else:
                    print(f"        -> ❌ Collision detected for '{fxtr.name}'. Stopping placement in this zone.")
                    break

            return placed_clinics_plan_b


    def _get_last_clinic_right_bottom_coord(self) -> Optional[Tuple[float, float]]:
        """
        Finds the absolute rightmost X and lowest Y coordinate of the last placed 
        clinic block by analyzing the actual DXF entity geometry (WCS bounding box).
        This version prioritizes clinics placed in the Plan B (lower) zone.
        """
        from ezdxf.bbox import extents
        
        clinic_entities = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]

        if not clinic_entities:
            print("    -> ERROR: No clinic entities found in the drawing.")
            return None

        # --- Step 1: Find the target Y-band (the lowest 50% of the clinics) ---
        all_y_max = [extents(list(e.virtual_entities())).extmax.y for e in clinic_entities if extents(list(e.virtual_entities())).has_data]
        if not all_y_max: return None

        # Define the Y-band as the lower half of the total clinic height range.
        max_y_overall = max(all_y_max)
        min_y_overall = min(all_y_max)
        
        # We are interested in the area below 75% of the total clinic height range.
        Y_BAND_THRESHOLD = min_y_overall + (max_y_overall - min_y_overall) * 0.75 
        
        # --- Step 2: Filter for clinics within the lower Y-band (Plan B Zone) ---
        lower_band_clinics = [
            e for e in clinic_entities 
            if extents(list(e.virtual_entities())).extmax.y < Y_BAND_THRESHOLD
        ]

        # --- Step 3: Select the rightmost clinic from the filtered list ---
        if not lower_band_clinics:
            # Fallback: If no Plan B clinics were placed (or they are too high up), 
            # use the rightmost of all clinics (which defaults to the Plan A clinic).
            print("    -> WARNING: No clinics found in the lower Y-band. Falling back to absolute rightmost clinic.")
            target_clinics = clinic_entities
        else:
            print(f"    -> {len(lower_band_clinics)} clinics identified in the Plan B zone (Y-band below {Y_BAND_THRESHOLD:.0f}).")
            target_clinics = lower_band_clinics

        # Now, find the rightmost X in the chosen target group
        best_entity = None
        max_right_x = float('-inf')

        for entity in target_clinics:
            try:
                bbox = extents(list(entity.virtual_entities()))
                if not bbox.has_data: continue
                
                if bbox.extmax.x > max_right_x:
                    max_right_x = bbox.extmax.x
                    best_entity = entity
                    
            except Exception:
                continue

        if best_entity is None:
            return None

        # --- Step 4: Get the final coordinates ---
        try:
            final_bbox = extents(list(best_entity.virtual_entities()))
            final_max_x = final_bbox.extmax.x
            final_min_y = final_bbox.extmin.y
            
            print(f"    -> ✅ Found last anchor at (Max_X: {final_max_x:.0f}, Min_Y: {final_min_y:.0f})")
            return (final_max_x, final_min_y)
            
        except Exception as e:
            print(f"    -> ERROR in final BBox calculation: {e}")
            return None

    
    def _place_clinics_fallback_row_by_row(self, clinics_queue, placed_bboxes, placed_clinics_on_top_wall, first_row_orientation):
        """
        [RESTORED] Places remaining clinics in open space, row by row, from top to bottom.
        This is the "Plan B" fallback for the master clinic placement strategy, using the original gap logic.
        """
        from shapely.geometry import LineString, MultiLineString
        from ezdxf.math import Vec2

        self.clinic_placement_method = 'Plan_B'
        print(f"\n  -> Plan B: {len(clinics_queue)} clinics remain. Starting Fallback (Row-by-Row)...")

        y_cursor = self.cvc.max_y
        
        if placed_clinics_on_top_wall:
            y_cursor = min(d['bbox'][1] for d in placed_clinics_on_top_wall)
            print(f"  -> First row placed. Starting next search below y={y_cursor:.0f}")
        
        is_second_row = True
        
        while clinics_queue and y_cursor > self.cvc.min_y:
            force_orientation = 'V' if is_second_row and first_row_orientation == 'H' else None

            if force_orientation == 'V' or (is_second_row and first_row_orientation == 'V'):
                VERTICAL_ROW_GAP = -100.0
                print(f"  -> Intending to place a VERTICAL row. Using a tight {VERTICAL_ROW_GAP}mm gap.")
            else:
                VERTICAL_ROW_GAP = 800.0
                print(f"  -> Intending to place a HORIZONTAL/MIXED row. Using a wide {VERTICAL_ROW_GAP}mm gap.")

            y_cursor -= VERTICAL_ROW_GAP

            intersection = self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, y_cursor), (self.cvc.max_x + 100, y_cursor)]))
            
            if intersection.is_empty:
                y_cursor -= 500
                continue

            # Handle cases where the intersection might be multiple segments
            if isinstance(intersection, MultiLineString):
                # Use the longest segment if multiple are found
                intersection = max(intersection.geoms, key=lambda line: line.length)
            
            if not isinstance(intersection, LineString):
                y_cursor -= 500
                continue

            local_bounds, row_width = intersection.bounds, intersection.length
            is_second_row = False
            
            best_layouts_ranked = self._find_best_combination_for_row([f.name for f in clinics_queue], row_width, force_orientation=force_orientation)
            
            if best_layouts_ranked:
                best_layout_used = best_layouts_ranked[0]
                print(f"    -> Found valid spot for a new row at y={y_cursor:.0f}. Placing {len(best_layout_used['combo'])} clinics.")
                row_fixtures = best_layout_used['fixtures_for_row']
                
                margin_from_left_wall = -100.0
                row_start_x = local_bounds[0] + margin_from_left_wall
                max_row_height = 0
                vertical_clinic_count_in_row = 0

                for i, (orient, fxtr) in enumerate(zip(best_layout_used['combo'], row_fixtures)):
                    if not clinics_queue: break
                    w, h = (fxtr.width if orient == 'H' else fxtr.height), (fxtr.height if orient == 'H' else fxtr.width)
                    max_row_height = max(max_row_height, h)
                    target_center = Vec2(row_start_x + w/2, y_cursor - h/2)
                    rotation = 0 if orient == 'H' else 90

                    if orient == 'H':
                        xscale, yscale = 1.0, -1.0
                    else:
                        xscale, yscale = -1.0, 1.0
                        vertical_clinic_count_in_row += 1
                        if vertical_clinic_count_in_row % 2 == 0:
                            yscale = -1.0
                    
                    new_bbox = self._validate_and_place_in_open_space(fxtr, target_center, 0, placed_bboxes, rotation==90, xscale=xscale, yscale=yscale)
                    if new_bbox:
                        last_right_bottom = (new_bbox[2], new_bbox[1])
                        print(f"[Plan B - Fallback Row] Placed clinic right-bottom: x={target_center.x + w/2:.2f}, y={target_center.y - h/2:.2f}")
                        clinics_queue.popleft()
                        row_start_x += w + best_layout_used['gaps'][i]
                    else:
                        clinics_queue.clear()
                        break
                
                if max_row_height > 0: y_cursor -= max_row_height
                else: y_cursor -= 500
            else:
                y_cursor -= 500
                
        return last_right_bottom


    def _undo_last_clinic_placement(self, clinic_details_to_remove: dict, clinics_queue: collections.deque, placed_bboxes: list, placed_clinics_on_top_wall: list):
        """
        Undoes the placement of a single clinic using a direct object reference.
        1. Deletes the fixture entity from the DXF drawing.
        2. Removes its bounding box from the obstacle list.
        3. Adds the fixture object back to the main placement queue.
        """
        print("    -> Executing 'Undo' for the last placed clinic...")
        
        fxtr_to_remove = clinic_details_to_remove['fxtr']
        bbox_to_remove = clinic_details_to_remove['bbox']
        
        # --- RELIABLE DELETION LOGIC (v2 - Corrected Order) ---
        entity_to_delete = clinic_details_to_remove.get('block_ref')

        if entity_to_delete and entity_to_delete.is_alive:
            # === FIX START ===
            # 1. Get the name for the log message BEFORE deleting the entity.
            entity_name = entity_to_delete.dxf.name
            
            # 2. Now, delete the entity from the drawing.
            self.msp.delete_entity(entity_to_delete)
            
            # 3. Use the stored name in the success message.
            print(f"      -> Successfully deleted fixture '{entity_name}' from the drawing.")
            # === FIX END ===
        else:
            print(f"      -> ⚠️ Could not find a valid block reference for '{fxtr_to_remove.name}' to delete.")

        # Remove its bounding box from our obstacle lists (Unchanged)
        if bbox_to_remove in placed_bboxes:
            placed_bboxes.remove(bbox_to_remove)
        
        if clinic_details_to_remove in placed_clinics_on_top_wall:
            placed_clinics_on_top_wall.remove(clinic_details_to_remove)
        
        # Add the fixture object back to the front of the queue (Unchanged)
        clinics_queue.appendleft(fxtr_to_remove)
        print(f"      -> Added '{fxtr_to_remove.name}' back to the placement queue.")


    ##--new-test--with---greedy method-- strategy -----space for boh----in top row itself
    ##--new-test--with---greedy method-- strategy -----space for boh----in top row itself


    
# (This function can be placed where the old one was)

    # In DXF_Controller.py

    def _calculate_wall_capacity(self, zone_length: float, avg_clinic_width: float = 2400.0, avg_gap: float = 200.0) -> int:
        """
        [NEW HELPER] Estimates the maximum number of clinics that can fit in a given length.
        """
        if zone_length <= 0 or avg_clinic_width <= 0:
            return 0
        
        # Simple formula: How many "clinic + gap" blocks fit in the total length?
        capacity = math.floor(zone_length / (avg_clinic_width + avg_gap))
        print(f"    -> Wall Capacity Check: {zone_length:.0f}mm can hold approx. {int(max(0, capacity))} clinics.")
        return int(max(0, capacity))

            
    ##--new-test--with---greedy method-- strategy ---- new -- wall-walk method
    ##--new-test--with---greedy method-- strategy ---- new -- wall-walk method


    def _analyze_top_wall_with_bulge_detection_new(self, small_bulge_max_width=500, small_bulge_max_depth=700):
        """
        [RESTORED] Performs a "smart walk" along the top wall to find multiple placeable zones.
        - Intelligently finds ALL top wall segments, regardless of corner order.
        - Classifies diversions as small (ignorable) or large (which create a new zone).
        """
        from ezdxf.math import Vec2
        print("  -> Starting 'Smart Walk' analysis of top wall...")
        
        ### --- ROBUST TOP WALL IDENTIFICATION --- ###
        all_corners = self.cvc.corners
        if len(all_corners) < 3: return []

        # 1. Get all perimeter segments from the corners
        all_segments = []
        for i in range(len(all_corners)):
            p1 = Vec2(all_corners[i])
            p2 = Vec2(all_corners[(i + 1) % len(all_corners)])
            all_segments.append((p1, p2))

        # 2. Filter for segments in the top 20% of the floorplan that are mostly horizontal
        y_threshold = self.cvc.max_y - (self.cvc.max_y - self.cvc.min_y) * 0.20
        top_segments = []
        for p1, p2 in all_segments:
            # Check if the segment is in the top zone
            if (p1.y + p2.y) / 2 > y_threshold:
                # Check if it's mostly horizontal and has a minimum length
                if abs(p1.y - p2.y) < abs(p1.x - p2.x) and p1.distance(p2) > 1700:
                    # Ensure segments are ordered left-to-right
                    if p1.x > p2.x: p1, p2 = p2, p1
                    top_segments.append((p1, p2))
        
        if not top_segments:
            print("  -> No top segments > 1700mm found. Falling back to find any top horizontal segment.")
            for p1, p2 in all_segments:
                if (p1.y + p2.y) / 2 > y_threshold and abs(p1.y - p2.y) < abs(p1.x - p2.x):
                    if p1.x > p2.x: p1, p2 = p2, p1
                    top_segments.append((p1, p2))
        
        # 3. Sort the found top segments from left to right to create the "walk" path
        top_segments.sort(key=lambda seg: seg[0].x)
        ### --- END OF ROBUST IDENTIFICATION --- ###

        if not top_segments:
            print("  -> Smart Walk complete. No top wall zones found.")
            return []

        placeable_zones = []
        current_flat_wall_start = top_segments[0][0]
        
        for i in range(len(top_segments) - 1):
            current_seg_end = top_segments[i][1]
            next_seg_start = top_segments[i+1][0]
            
            # Calculate the deviation between the end of one segment and the start of the next
            deviation_width = abs(next_seg_start.x - current_seg_end.x)
            deviation_depth = abs(next_seg_start.y - current_seg_end.y)

            if deviation_width < small_bulge_max_width and deviation_depth < small_bulge_max_depth:
                # This is a small, ignorable bulge. Continue the current flat wall.
                pass
            else:
                # This is a large deviation. End the current zone and start a new one.
                placeable_zones.append({
                    'start': current_flat_wall_start, 
                    'end': current_seg_end, 
                    'length': current_seg_end.distance(current_flat_wall_start)
                })
                current_flat_wall_start = next_seg_start

        # After the loop, add the last remaining flat wall zone
        if current_flat_wall_start is not None:
            last_point = top_segments[-1][1]
            placeable_zones.append({
                'start': current_flat_wall_start, 
                'end': last_point, 
                'length': last_point.distance(current_flat_wall_start)
            })

        print(f"  -> Smart Walk complete. Found {len(placeable_zones)} placeable zones on the top wall.")
        return placeable_zones
    

    def draw__analyze_top_wall_with_bulge_detection_new(self):
        """
        [DEBUG HELPER] Visualizes the segments created by _analyze_top_wall_with_bulge_detection_new()
        and prints their lengths in JSON format.
        """
        import json
        print("\n--- 🎨 Drawing Top Wall Analysis Zones for Validation ---")

        # 1. Call the analysis function to get the zones
        placeable_zones = self._analyze_top_wall_with_bulge_detection_new(
            small_bulge_max_width=1000, 
            small_bulge_max_depth=1000
        )

        if not placeable_zones:
            print("  -> No placeable zones found to draw.")
            return

        # --- NEW: Prepare and print segment lengths in JSON format ---
        segment_lengths = {}
        for i, zone in enumerate(placeable_zones):
            zone_id = f"TOP_ZONE_{i+1}"
            segment_lengths[zone_id] = f"{zone['length']:.2f}mm"
        
        print("  -> Top Wall Segment Lengths:")
        print(json.dumps(segment_lengths, indent=4))
        # --- END OF NEW CODE ---

        # 2. Create a new, highly visible layer for the debug drawing
        layer_name = "DEBUG_TOP_WALL_ZONES"
        if layer_name not in self.doc.layers:
            self.doc.layers.add(name=layer_name, color=6)  # ACI color 6 is Magenta

        # 3. Iterate through the zones and draw each one
        for i, zone in enumerate(placeable_zones):
            start_point = zone['start']
            end_point = zone['end']
            
            # Draw the line segment for the zone
            self.msp.add_line(
                start_point, 
                end_point, 
                dxfattribs={"layer": layer_name, "lineweight": 70} # Use a thick lineweight
            )

            # Add a text label to identify the zone number
            mid_point = start_point.lerp(end_point)
            self.msp.add_mtext(
                f"TOP_ZONE_{i+1}",
                dxfattribs={
                    'char_height': 150,
                    'insert': mid_point,
                    'layer': layer_name
                }
            )
        
        print(f"  -> ✅ Drew {len(placeable_zones)} top wall zones on layer '{layer_name}'.")
        
    ##--new-test--with---greedy method-- strategy ---- new -- wall-walk method
    ##--new-test--with---greedy method-- strategy ---- new -- wall-walk method


    def place_clinics_master_strategy_opposite(self, placed_bboxes: List[tuple]):
        """
        [OPPOSITE STRATEGY] Places clinics from RIGHT to LEFT and creates BOH on the LEFT side.
        This is the mirror/opposite version of place_clinics_master_strategy.
        - Clinics: Placed RIGHT-TO-LEFT starting from the facade's right corner
        - BOH: Drawn from the leftmost clinic extending to the left wall
        - Clinics are horizontally flipped (xscale=-1) for proper orientation
        """
        self.clinic_placement_method = 'Unknown'
        from shapely.geometry import Polygon, LineString, Point
        from ezdxf.math import Vec2
        from ezdxf.bbox import extents
    
        print("\n--- 🧠 Executing OPPOSITE Clinic Placement (Right-to-Left with Left BOH) ---")
    
        # --- Create temporary obstacle list (same as original) ---
        obstacles_for_clinics = list(placed_bboxes)
        internal_wall_obstacles = self.cvc.get_internal_wall_partitions(1000, 1200, 20) + self.cvc.get_internal_wall_partitions(2600, 2800, 10)
        if internal_wall_obstacles:
            existing_obstacles = set(map(tuple, obstacles_for_clinics))
            new_obstacles = [obs for obs in internal_wall_obstacles if tuple(obs) not in existing_obstacles]
            if new_obstacles:
                obstacles_for_clinics.extend(new_obstacles)
                print(f"  -> Added {len(new_obstacles)} partitions to obstacle list.")
        
        # --- Setup clinic queue (same as original) ---
        clinic_config = self.fixtures.get("clinic_fixtures", {})
        clinics_queue = collections.deque([
            Fixture.Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"])
            for name, count in clinic_config.items() if count > 0 for _ in range(count)
        ])
        if not clinics_queue:
            print("  -> SKIPPED: No clinics to place.")
            return
    
        # =========================================================================
        # =========== PHASE 1: UNCONDITIONAL TOP-WALL PLACEMENT (RIGHT-TO-LEFT) ==
        # =========================================================================
        print("\n  -> Phase 1: Placing clinics RIGHT-TO-LEFT on the top wall...")
        
        # **KEY CHANGE**: Use right-start path instead of left-start
        top_wall_zones = self._analyze_top_wall_with_bulge_detection_opposite()
        
        placed_clinics_on_top_wall = []
        is_first_zone_processed = False
        first_row_orientation = 'H'
        total_vertical_clinics_placed_on_top = 0
    
        for zone in top_wall_zones:
            if not clinics_queue: break
            
            available_width = zone['length']
            print(f"\n  -> Analyzing placement zone of width {available_width:.0f}mm...")
    
            clinic_names_for_solver = [fxtr.name for fxtr in clinics_queue]
            best_layouts_ranked = self._find_best_combination_for_row(clinic_names_for_solver, available_width, force_orientation='H')
    
            if not best_layouts_ranked:
                print("    -> No combination of remaining clinics fits in this zone.")
                continue
    
            print(f"    -> Best layout for this zone: {best_layouts_ranked[0]['combo']}")
    
            # **KEY CHANGE**: Use opposite placement helper with horizontal flip
            placed_count, total_vertical_clinics_placed_on_top = self._find_and_place_row_in_zone_opposite(
                zone, 
                best_layouts_ranked, 
                clinics_queue, 
                obstacles_for_clinics,
                placed_clinics_on_top_wall,
                start_vertical_count=total_vertical_clinics_placed_on_top
            )
    
            if placed_count > 0 and not is_first_zone_processed:
                best_layout_used = best_layouts_ranked[0]
                h_count = best_layout_used['combo'].count('H')
                v_count = len(best_layout_used['fixtures_for_row']) - h_count
                first_row_orientation = 'H' if h_count >= v_count else 'V'
                is_first_zone_processed = True
    
        # =========================================================================
        # =========== PHASE 2 & 3: FINAL BOH CHECK AND "UNDO" LOGIC ==============
        # =========================================================================
        print("\n  -> Phase 2: Performing final BOH verification...")
        if not placed_clinics_on_top_wall:
            print("    -> No clinics were placed on the top wall. Skipping BOH check.")
        else:
            # **KEY CHANGE**: Find the leftmost clinic instead of rightmost
            final_anchor_clinic_details = min(placed_clinics_on_top_wall, key=lambda c: c['bbox'][0])
            
            # **KEY CHANGE**: Use opposite BOH calculation
            boh_zone_poly, boh_area_sqft = self._calculate_opportunistic_boh_zone_opposite(
                final_anchor_clinic_details['bbox'],
                [],
                final_anchor_clinic_details['orient']
            )
            print(f"    -> Final check: Potential BOH area is {boh_area_sqft:.2f} sq. ft.")
    
            MINIMUM_BOH_AREA = 160.0
            
            if boh_area_sqft >= MINIMUM_BOH_AREA:
                print("    -> ✅ Verification PASSED. Committing layout and drawing BOH.")
                self.clinic_placement_method = 'Plan_A'
                # **KEY CHANGE**: Use opposite BOH creation
                self.create_boh_zone_from_first_clinic_opposite(placed_clinics_on_top_wall, placed_bboxes)
            else:
                print(f"    -> ❌ Verification FAILED. BOH area is less than {MINIMUM_BOH_AREA} sq. ft.")
                self._undo_last_clinic_placement(final_anchor_clinic_details, clinics_queue, placed_bboxes, placed_clinics_on_top_wall)
                print("    -> Re-evaluating BOH zone with the updated clinic layout...")
                self.create_boh_zone_from_first_clinic_opposite(placed_clinics_on_top_wall, placed_bboxes)
                  
        # --- FALLBACK LOGIC (if clinics remain) ---
        if clinics_queue:
            self.clinic_placement_method = 'Plan_B'
            print(f"\n  -> Plan B: {len(clinics_queue)} clinics remain. Starting Fallback...")
            # Additional fallback logic can be added here if needed
    
        print("\n✅ Opposite clinic placement process complete.")
    
    
    def _analyze_top_wall_with_bulge_detection_opposite(self, small_bulge_max_width=200, small_bulge_max_depth=700):
        """
        [OPPOSITE VERSION - FULLY CORRECTED] Performs a "smart walk" along the top wall from RIGHT to LEFT.
        Returns zones ordered from right to left for opposite placement.
        **NOW CORRECTLY MIRRORS THE ORIGINAL FUNCTION'S LOGIC**
        """
        from ezdxf.math import Vec2
        print("  -> Starting 'Smart Walk' analysis of top wall (RIGHT-TO-LEFT)...")
        
        all_corners = self.cvc.corners
        if len(all_corners) < 3: return []

        # Get all perimeter segments
        all_segments = []
        for i in range(len(all_corners)):
            p1 = Vec2(all_corners[i])
            p2 = Vec2(all_corners[(i + 1) % len(all_corners)])
            all_segments.append((p1, p2))

        # Filter for top segments
        y_threshold = self.cvc.max_y - (self.cvc.max_y - self.cvc.min_y) * 0.20
        top_segments = []
        for p1, p2 in all_segments:
            if (p1.y + p2.y) / 2 > y_threshold:
                if p1.distance(p2) > 300 and abs(p1.y - p2.y) < abs(p1.x - p2.x):
                    top_segments.append((p1, p2))
        
        if not top_segments:
            print("  -> No top segments > 300mm found.")
            for p1, p2 in all_segments:
                if (p1.y + p2.y) / 2 > y_threshold:
                    top_segments.append((p1, p2))
        
        # **KEY CHANGE**: Sort RIGHT to LEFT (by the RIGHTMOST point of each segment)
        # This ensures we process segments from right to left
        top_segments.sort(key=lambda seg: max(seg[0].x, seg[1].x), reverse=True)

        if not top_segments:
            print("  -> Smart Walk complete. No top wall zones found.")
            return []

        # **CRITICAL FIX**: Start from the RIGHTMOST point of the first segment
        # The first segment after sorting is the rightmost one
        first_seg = top_segments[0]
        # Pick the point with the larger X value as our starting point
        current_flat_wall_start = first_seg[0] if first_seg[0].x > first_seg[1].x else first_seg[1]
        
        print(f"  -> Starting walk from rightmost point at x={current_flat_wall_start.x:.0f}, y={current_flat_wall_start.y:.0f}")
        
        placeable_zones = []
        
        for i in range(len(top_segments) - 1):
            # For the current segment, find which end connects to our current position
            current_seg = top_segments[i]
            
            # Determine the "end" of this segment (the point moving leftward)
            if i == 0:
                # For the first segment, we already know the start point
                # The end is the other point
                current_seg_end = current_seg[1] if current_seg[0].x > current_seg[1].x else current_seg[0]
            else:
                # For subsequent segments, the end is the point we haven't used yet
                current_seg_end = current_seg[0] if current_seg[0].x < current_seg[1].x else current_seg[1]
            
            # Look at the next segment
            next_seg = top_segments[i + 1]
            # The start of the next segment is the point closest to where we ended
            next_seg_start = next_seg[0] if next_seg[0].distance(current_seg_end) < next_seg[1].distance(current_seg_end) else next_seg[1]
            
            # Calculate deviation
            deviation_width = abs(next_seg_start.x - current_seg_end.x)
            deviation_depth = abs(next_seg_start.y - current_seg_end.y)

            # Check if this is a small bulge to ignore or a large gap
            if deviation_width < small_bulge_max_width and deviation_depth < small_bulge_max_depth:
                print(f"    -> Small bulge detected (w:{deviation_width:.0f}mm, d:{deviation_depth:.0f}mm). Continuing zone.")
                # Small bulge - continue the current zone
                continue
            else:
                # Large gap - end the current zone
                print(f"    -> Large diversion detected (w:{deviation_width:.0f}mm, d:{deviation_depth:.0f}mm). Ending wall zone.")
                zone_length = current_flat_wall_start.distance(current_seg_end)
                if zone_length > 300:
                    placeable_zones.append({
                        'start': current_flat_wall_start, 
                        'end': current_seg_end, 
                        'length': zone_length
                    })
                # Start a new zone from the next segment's start
                current_flat_wall_start = next_seg_start

        # Add the final zone (from current_flat_wall_start to the end of the last segment)
        last_seg = top_segments[-1]
        last_point = last_seg[0] if last_seg[0].x < last_seg[1].x else last_seg[1]  # Leftmost point of last segment
        zone_length = current_flat_wall_start.distance(last_point)
        if zone_length > 300:
            placeable_zones.append({
                'start': current_flat_wall_start, 
                'end': last_point, 
                'length': zone_length
            })

        print(f"  -> Smart Walk complete. Found {len(placeable_zones)} placeable zones (RIGHT-TO-LEFT).")
        return placeable_zones

        
    def _find_and_place_row_in_zone_opposite(self, zone, layouts_ranked: list, clinics_queue, placed_bboxes, placed_clinics_on_top_wall, start_vertical_count: int = 0):
        """
        [OPPOSITE VERSION - FULLY CORRECTED] Places clinics RIGHT-TO-LEFT with horizontal mirroring.
        **NOW CORRECTLY STARTS FROM THE RIGHT EDGE OF EACH SEGMENT**
        """
        from shapely.geometry import Point
        from ezdxf.math import Vec2

        if not layouts_ranked:
            return 0, start_vertical_count

        p1, p2 = zone['start'], zone['end']
        wall_vector = (p2 - p1).normalize()
        wall_angle_deg = math.degrees(wall_vector.angle)
        inward_normal = wall_vector.orthogonal().normalize()
        if not self.floorplan_polygon.contains(Point(p1 + inward_normal)): 
            inward_normal *= -1

        best_placement_details = None
        final_vertical_count_state = start_vertical_count

        # **KEY FIX**: p1 is rightmost, p2 is leftmost after the opposite sorting
        # We need to place starting FROM p1 (right) and move toward p2 (left)
        
        # Start searching from near the RIGHT edge (p1 is rightmost after sorting)
        search_cursor = 10.0
        zone_length = p1.distance(p2)
        
        while search_cursor < zone_length - 50.0:
            for layout in layouts_ranked:
                row_fixtures = layout['fixtures_for_row']
                
                total_row_width = sum((f.width if o == 'H' else f.height) for f, o in zip(row_fixtures, layout['combo'])) + sum(layout['gaps'])
                
                if search_cursor + total_row_width > zone_length - 50.0:
                    continue

                is_entire_row_valid = True
                hypothetical_placements = []
                
                # **CRITICAL FIX**: Start measuring from p1 (rightmost point)
                # The search_cursor is an offset from the right edge
                current_x = search_cursor
                
                vertical_clinic_count = start_vertical_count
                
                for i in range(len(row_fixtures)):
                    fxtr = row_fixtures[i]
                    orient = layout['combo'][i]
                    fixture_width = fxtr.width if orient == 'H' else fxtr.height
                    fixture_height = fxtr.height if orient == 'H' else fxtr.width
                    
                    # **KEY CHANGE**: Calculate position from p1 (rightmost)
                    # current_x increases as we move LEFT along the wall
                    # target_center = p1 + wall_vector * (current_x + fixture_width / 2) + inward_normal * (10.0 + fixture_height / 2)
                    # --- MODIFICATION: Add a rightward push for wall overlap ---
                    inward_position = p1 + wall_vector * (current_x + fixture_width / 2) + inward_normal * (-100.0 + fixture_height / 2)
                    rightward_push_vector = Vec2(100, 0) # Push 100mm to the right
                    target_center = inward_position + rightward_push_vector
                    # --- END OF MODIFICATION ---
                    
                    rotation = wall_angle_deg if orient == 'H' else wall_angle_deg + 90
                    
                    
                    # Apply horizontal flip
                    xscale = -1.0
                    yscale = -1.0
                    
                    bbox_result = self._validate_and_place_on_wall(fxtr, target_center, rotation, placed_bboxes, xscale=xscale, yscale=yscale, place_actually=False)
                    
                    if bbox_result is None:
                        is_entire_row_valid = False
                        break
                    
                    hypothetical_placements.append({
                        'fxtr': fxtr, 'center': target_center, 'rot': rotation,
                        'xscale': xscale, 'yscale': yscale, 'bbox': bbox_result, 'orient': orient
                    })
                    
                    if orient == 'V':
                        vertical_clinic_count += 1
                    
                    gap = layout['gaps'][i] if i < len(layout['gaps']) else 0
                    current_x += (fixture_width + gap)

                if is_entire_row_valid:
                    best_placement_details = hypothetical_placements
                    final_vertical_count_state = vertical_clinic_count
                    break
            
            if best_placement_details is not None:
                break
            
            search_cursor += 100

        # Place if found
        if best_placement_details:
            print(f"    -> ✅ Best spot found. Committing {len(best_placement_details)} clinics to the wall.")
            
            for details in best_placement_details:
                fxtr = details['fxtr']
                target_center = details['center']
                rotation = details['rot']
                xscale = details['xscale']
                yscale = details['yscale']
                pre_validated_bbox = details['bbox']

                local_center = fxtr.bounding_box.center
                local_center_scaled = Vec2(local_center.x * xscale, local_center.y * yscale)
                rotated_offset = local_center_scaled.rotate(math.radians(rotation))
                final_insert_point = target_center - rotated_offset
                
                block_ref = self.place_fixture(fxtr, (final_insert_point.x, final_insert_point.y, 0), rotation, True, xscale=xscale, yscale=yscale)
                
                placed_bboxes.append(pre_validated_bbox)
                details['block_ref'] = block_ref
                placed_clinics_on_top_wall.append(details)
                clinics_queue.popleft()

            return len(best_placement_details), final_vertical_count_state

        return 0, start_vertical_count
    
    
    def _calculate_opportunistic_boh_zone_opposite(self, first_clinic_bbox: tuple, placed_bboxes: List[tuple], first_clinic_orientation: str) -> Tuple[Optional[Polygon], float]:
        """
        [OPPOSITE VERSION] Calculates BOH zone on the LEFT side by subtracting retail area from floorplan.
        """
        from shapely.geometry import box, Polygon
    
        fc_min_x, fc_min_y, fc_max_x, fc_max_y = first_clinic_bbox
        fp_min_x, fp_min_y, fp_max_x, fp_max_y = self.floorplan_polygon.bounds
        
        # **KEY CHANGE**: Start from LEFT edge of first (leftmost) clinic
        end_x_for_cutout = fc_min_x
        if first_clinic_orientation == 'V':
            print("    -> 💡 Applying architectural rule: Adding 800mm horizontal gap for vertical clinic.")
            end_x_for_cutout -= 800.0
    
        # **KEY CHANGE**: Retail mask covers everything to the RIGHT of the cutout point
        retail_mask = box(end_x_for_cutout, fp_min_y - 1000, fp_max_x + 1000, fp_max_y + 1000)
    
        # BOH zone is on the LEFT (everything NOT in retail mask)
        boh_zone_poly = self.floorplan_polygon.difference(retail_mask)
    
        if any(boh_zone_poly.intersects(box(*b)) for b in placed_bboxes):
            return None, 0.0
    
        area_in_sqmm = boh_zone_poly.area
        SQMM_PER_SQFT = 92903.04
        area_in_sqft = area_in_sqmm / SQMM_PER_SQFT
        
        return boh_zone_poly, area_in_sqft
    
    def create_boh_zone_from_first_clinic_opposite(self, placed_clinics_on_top_wall: list, placed_bboxes: list, big_partition_threshold_mm: float = 1200.0):
        """
        [OPPOSITE VERSION - CORRECTED PARTITION DETECTION] Creates BOH zone on the LEFT side.
        **NOW PROPERLY DETECTS AND STOPS AT PARTITION WALLS WITHOUT ADDING GAPS**
        """
        from shapely.geometry import box
        from ezdxf.math import Vec2
        
        print(f"\n--- 🏛️  Creating BOH Zone on LEFT Side (Partition Detection) ---")

        if not placed_clinics_on_top_wall:
            print("  -> SKIPPED: No clinics were placed on the top wall to anchor the BOH.")
            return

        # Find the LEFTMOST clinic
        anchor_clinic = min(placed_clinics_on_top_wall, key=lambda c: c['bbox'][0])
        anchor_bbox = anchor_clinic['bbox']
        anchor_orientation = anchor_clinic['orient']
        anchor_point_x = anchor_bbox[0]  # LEFT edge
        anchor_point_y = anchor_bbox[1]
        
        print(f"  -> Anchoring to '{anchor_clinic['fxtr'].name}' at x={anchor_point_x:.0f}, y={anchor_point_y:.0f}")

        # Conditional Gap Logic
        total_vertical_clinics = sum(1 for clinic in placed_clinics_on_top_wall if clinic['orient'] == 'V')
        print(f"  -> Total vertical clinics on top wall: {total_vertical_clinics}")
        
        start_x = anchor_point_x
        if anchor_orientation == 'V' and total_vertical_clinics % 2 != 0:
            start_x -= 800.0
            print(f"  -> Applying 800mm gap: start_x adjusted to {start_x:.0f}")
        else:
            print(f"  -> NO gap applied. start_x remains at {start_x:.0f}")

        # Initial BOH boundary extends to LEFT wall
        boh_min_x = self.cvc.min_x
        
        # Get partitions using the proven method
        print(f"  -> Detecting partitions using get_internal_wall_partitions()...")
        stopper_partitions = self.cvc.get_internal_wall_partitions(
            min_length=900, 
            max_length=1200,
            thickness=20.0
        )
        
        print(f"  -> Found {len(stopper_partitions)} partitions")

        # Define BOH vertical range
        boh_min_y = anchor_point_y
        boh_max_y = self.cvc.max_y + 1000

        print(f"  -> BOH Y-range: {boh_min_y:.0f} to {boh_max_y:.0f}")
        print(f"  -> Looking for partitions between left wall ({self.cvc.min_x:.0f}) and start ({start_x:.0f})")

        # **KEY LOGIC**: Find partitions that block the BOH path
        blocking_partitions = []
        
        for partition_bbox in stopper_partitions:
            p_min_x, p_min_y, p_max_x, p_max_y = partition_bbox
            
            # Check 1: Partition must be to the LEFT of our starting point
            is_in_path = p_max_x < start_x and p_max_x > self.cvc.min_x
            
            # Check 2: Partition must overlap vertically with BOH zone
            has_vertical_overlap = not (p_max_y < boh_min_y or p_min_y > boh_max_y)
            
            print(f"    -> Checking partition at x=[{p_min_x:.0f}, {p_max_x:.0f}], y=[{p_min_y:.0f}, {p_max_y:.0f}]")
            print(f"       - In path? {is_in_path}")
            print(f"       - Vertical overlap? {has_vertical_overlap}")
            
            if is_in_path and has_vertical_overlap:
                blocking_partitions.append(partition_bbox)
                print(f"       ✓ BLOCKING - This partition stops the BOH")
        
        print(f"  -> Found {len(blocking_partitions)} blocking partitions")
        
        # Find the rightmost blocking partition (closest to our start point)
        if blocking_partitions:
            closest_partition = max(blocking_partitions, key=lambda p: p[2])  # p[2] is max_x
            
            # **NO GAP ADDED** - Stop exactly at the partition
            boh_min_x = closest_partition[2]
            
            print(f"  -> ✅ BOH will stop at partition edge at x={boh_min_x:.0f}")
            print(f"     Partition bounds: x=[{closest_partition[0]:.0f}, {closest_partition[2]:.0f}]")
        else:
            print(f"  -> No blocking partitions found. BOH extends to left wall at x={boh_min_x:.0f}")

        # Create BOH box
        print(f"\n  -> Creating BOH box:")
        print(f"     Left edge: {boh_min_x:.0f}")
        print(f"     Right edge: {start_x:.0f}")
        print(f"     Bottom: {anchor_point_y:.0f}")
        print(f"     Top: {boh_max_y:.0f}")
        
        boh_box = box(boh_min_x, anchor_point_y, start_x, boh_max_y)
        final_boh_poly = self.floorplan_polygon.intersection(boh_box)

        # Expansion logic
        final_boh_poly = self._expand_boh_zone_downwards_if_needed(final_boh_poly, boh_box, self.floorplan_polygon)

        if final_boh_poly.is_empty:
            print("  -> ⚠️ FAILED: The calculated BOH zone is empty.")
            return
            
        self._create_boh_room_from_zone(final_boh_poly, layer_name="BOH_WALL_VALID")
        placed_bboxes.append(final_boh_poly.bounds)
        
        print("  -> ✅ BOH zone created on LEFT side successfully.")
    
    ##--new-test--with---oppsite placement of whole 
    ##--new-test--with---oppsite placement of whole 



    


    ##--new-test--with---oppsite placement of whole 
    ##--new-test--with---oppsite placement of whole 


    




#---- CLINIC PLACEMENT FUNCTION FINISHED HERE ----


#---- PICKUP WINDOW PLACEMENT FUNCTION STARTS HERE ----

    


    def place_pickup_window_next_to_clinic(self, placed_bboxes: List[tuple]):
        """
        [MODIFIED V3] Places the Pick_up_window fixture using a consistent vertical anchor.
        - An anchor clinic (the last one placed) determines the Y-level for all attempts.
        - Primary: Tries to place the window at this Y-level against the right wall.
        - Fallback: If the wall is blocked, places it at the same Y-level next to the anchor clinic.
        """
        # from Fixture import Fixture
        from ezdxf.bbox import extents
        from shapely.geometry import box
        import math

        print("\n--- 🧠 Placing Pick-up Window (Consistent Y-Anchor Strategy) ---")

        # 1. SETUP: Load fixture
        try:
            config = self.fixtures.get("pickup_window", {})
            if config.get("Pick_up_window", 0) <= 0:
                print("  -> SKIPPED: No Pick_up_window fixture specified.")
                return
            fixture_obj = Fixture.Fixture("Pick_up_window", self.fixture_dict["Pick_up_window"]["path"])
        except Exception as e:
            print(f"  -> 🔥 ERROR during Pick_up_window setup: {e}")
            return

        # 2. FIND ALL CLINICS AND ESTABLISH THE CONSISTENT Y-ANCHOR
        all_clinics = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
        if not all_clinics:
            print("  -> ⚠️ FAILED: No clinics found to anchor the Pick_up_window to.")
            return

        def get_clinic_number(entity):
            """Helper to extract the numerical suffix from a block name."""
            try: return int(entity.dxf.name.split('_')[-1])
            except (ValueError, IndexError): return float('inf')

        # Sort all clinics by number to find the "last" one placed. This is our main anchor.
        all_clinics.sort(key=get_clinic_number)
        y_anchor_clinic = all_clinics[-1]
        y_anchor_bbox = extents([y_anchor_clinic])
        print(f"  -> Using '{y_anchor_clinic.dxf.name}' as the consistent vertical anchor.")
        
        # Calculate the single target Y-coordinate that will be used for all attempts.
        target_y = y_anchor_bbox.center.y - (fixture_obj.height / 2)
        print(f"  -> Target Y-level set to: {target_y:.0f}")

        is_placed = False

        # --- 3. PRIMARY STRATEGY: Attach to Right Wall at the Target Y-Level ---
        print("  -> Attempting Primary Strategy: Attach to right wall.")
        
        margin_from_wall = 50.0
        ideal_x = self.cvc.max_x - fixture_obj.width - margin_from_wall
        search_x = ideal_x
        search_limit = ideal_x - 1500.0 

        while search_x > search_limit:
            candidate_box = box(search_x, target_y, search_x + fixture_obj.width, target_y + fixture_obj.height)
            is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
            is_inside = self.floorplan_polygon.contains(candidate_box)

            if is_inside and not is_overlapping:
                self.place_fixture(fixture_obj, (search_x, target_y, 0), 0, False)
                placed_bboxes.append(candidate_box.bounds)
                print(f"    ✅ SUCCESS (Primary): Placed '{fixture_obj.name}' near the right wall at x={search_x:.0f}.")
                is_placed = True
                break 
            search_x -= 100.0

        # --- 4. FALLBACK STRATEGY: Place next to anchor clinic at the Target Y-Level ---
        if not is_placed:
            self._place_pickup_table_in_boh(placed_bboxes)
            print(f"\n  -> ⚠️ Primary wall strategy failed. Attempting Fallback: Place next to anchor clinic.")
            
            # # The anchor is already identified as y_anchor_clinic.
            # fallback_anchor_bbox = y_anchor_bbox
            # print(f"  -> Fallback anchor is '{y_anchor_clinic.dxf.name}'")

            # # Determine anchor's orientation and set gap
            # rotation = y_anchor_clinic.dxf.rotation
            # is_vertical = (85 < rotation < 95) or (265 < rotation < 275)

            # if is_vertical:
            #     gap = 800
            #     print("    -> Anchor clinic is VERTICAL. Using 800mm gap.")
            # else:
            #     gap = 50.0
            #     print("    -> Anchor clinic is HORIZONTAL. Using 50mm gap.")
            
            # # Calculate fallback position (X changes, Y stays the same)
            # target_x_fallback = fallback_anchor_bbox.extmax.x + gap
            # # The target_y is already calculated and is consistent for both strategies.

            # # Validate and place at fallback position
            # candidate_box_fallback = box(target_x_fallback, target_y, target_x_fallback + fixture_obj.width, target_y + fixture_obj.height)
            # is_overlapping_fallback = any(candidate_box_fallback.intersects(box(*b)) for b in placed_bboxes)
            # is_inside_fallback = self.floorplan_polygon.contains(candidate_box_fallback)

            # if is_inside_fallback and not is_overlapping_fallback:
            #     self.place_fixture(fixture_obj, (target_x_fallback, target_y, 0), 0, False)
            #     placed_bboxes.append(candidate_box_fallback.bounds)
            #     print(f"    ✅ SUCCESS (Fallback): Placed '{fixture_obj.name}' with a {gap:.0f}mm gap.")
            # else:
            #     print(f"  -> ⚠️ FINAL FAILURE: The fallback spot was also blocked or outside the boundary.")

              
#---------------------NEW_PICKUP_WINDOW FUNCTION WITH PICKUP TABLE FALL BACK SETUP---------------------
#---------------------NEW_PICKUP_WINDOW FUNCTION WITH PICKUP TABLE FALL BACK SETUP---------------------


    # In DXF_Controller.py -> Add these three functions

    
    def place_pickup_area_fixture(self, placed_bboxes: List[tuple]):
        """
        [MODIFIED DISPATCHER] Intelligently places pickup fixtures based on the
        clinic placement method and the size of the BOH zone.
        """
        from shapely.geometry import Polygon

        print("\n---  Orchestrating Pickup Area Fixture Placement ---")

        if not hasattr(self, 'clinic_placement_method') or self.clinic_placement_method == 'Unknown':
            print("  -> SKIPPED: Clinic placement method is unknown. Cannot determine which pickup fixture to place.")
            self._place_pickup_table_in_boh(placed_bboxes)
            return

        # --- Step 1: Check for Plan A ---
        if self.clinic_placement_method == 'Plan_A':
            print("  -> Clinic placement used Plan A. Placing 'pickup_table' in BOH zone.")
            self._place_pickup_table_in_boh(placed_bboxes)

        # --- Step 2 (NEW LOGIC): Check if BOH zone is large enough ---
        else:
            boh_zone = self._get_boh_zone_polygon()
            if boh_zone and not boh_zone.is_empty:
                # Conversion factor from square mm to square feet
                SQMM_PER_SQFT = 92903.04
                area_sqft = boh_zone.area / SQMM_PER_SQFT
                print(f"  -> BOH Zone found with an area of {area_sqft:.2f} sq. ft.")

                if area_sqft >= 50.0:
                    print("  -> BOH area is > 50 sq. ft. Placing 'pickup_table' in BOH Zone.")
                    self._place_pickup_table_in_boh(placed_bboxes)
                    return # Stop here since the table has been placed

            # --- Step 3: Fallback to Plan B if other conditions aren't met ---
            if self.clinic_placement_method == 'Plan_B':
                print("  -> Clinic placement used Plan B Fallback. Placing 'Pick_up_window'.")
                # self.place_pickup_window_next_to_clinic(placed_bboxes)
                self._place_pickup_table_in_boh(placed_bboxes)
            
            else:
                print("  -> No pickup fixture placement strategy was met.")


    def _place_pickup_table_in_boh(self, placed_bboxes: List[tuple]):
        """
        [MODIFIED] Places the 'pickup_table' in the BOH zone. It starts at the
        bottom-left and searches rightwards along the bottom edge until a
        clear spot is found. Includes a 150mm downward nudge for better aesthetics.
        """
        # from Fixture import Fixture
        from shapely.geometry import box
        
        # 1. Load fixture
        try:
            pickup_config = self.fixtures.get("pickup_window", {})
            boh_config = self.fixtures.get("boh_fixtures", {})
            
            if pickup_config.get("pickup_table", 0) <= 0 and boh_config.get("pickup_table", 0) <= 0:
                print("  -> SKIPPED: 'pickup_table' not specified in configuration.")
                return
            
            fixture_obj = Fixture.Fixture("pickup_table", self.fixture_dict["pickup_table"]["path"])
        except Exception as e:
            print(f"  -> 🔥 ERROR loading 'pickup_table': {e}")
            return

        # 2. Find BOH zone
        boh_zone = self._get_boh_zone_polygon()
        if not boh_zone:
            print("  -> ⚠️ FAILED: Could not find BOH zone to place pickup_table in.")
            return

        # 3. Setup for 2D Resilient Grid Search
        boh_bounds = boh_zone.bounds
        margin = 50.0
        
        # ******************** MODIFICATION IS HERE ********************
        # This line now subtracts 150mm to apply the new downward nudge.
        search_start_y = boh_bounds[1] + margin - 150.0
        # ************************************************************

        # Only search a 500mm vertical band to keep it near the bottom
        search_end_y = search_start_y + 500.0 
        
        search_start_x = boh_bounds[0] + margin
        search_end_x = boh_bounds[2] - fixture_obj.width - margin
        
        step = 100.0 # Grid step size in mm
        is_placed = False

        # 4. 2D Grid Search Loop (Searches upwards, then rightwards)
        print("  -> Searching for a spot along the bottom of the BOH zone (2D Grid Search)...")
        
        y_try = search_start_y
        while y_try < search_end_y:
            x_try = search_start_x
            while x_try < search_end_x:
                candidate_box = box(x_try, y_try, x_try + fixture_obj.width, y_try + fixture_obj.height)
                
                is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
                is_inside = boh_zone.contains(candidate_box)

                if is_inside and not is_overlapping:
                    self.place_fixture(fixture_obj, (x_try, y_try, 0), 0, False)
                    placed_bboxes.append(candidate_box.bounds)
                    print(f"    ✅ SUCCESS: Placed '{fixture_obj.name}' in the BOH zone at (x={x_try:.0f}, y={y_try:.0f}).")
                    is_placed = True
                    break # Exit inner x-loop on success
                
                x_try += step
            
            if is_placed:
                break # Exit outer y-loop on success
            
            y_try += step

        # 5. Final Failure Message
        if not is_placed:
            print("    -> ⚠️ FAILED: The entire bottom area of the BOH zone was blocked or invalid.")

    def _place_pickup_table_in_boh_right(self, placed_bboxes: List[tuple]):
        """
        [RIGHT SIDE VERSION] Places the 'pickup_table' in the BOH zone on the RIGHT side.
        It starts at the bottom-right and searches leftwards along the bottom edge until a
        clear spot is found. Includes a 150mm downward nudge for better aesthetics.
        """
        from shapely.geometry import box
        
        # 1. Load fixture
        try:
            pickup_config = self.fixtures.get("pickup_window", {})
            boh_config = self.fixtures.get("boh_fixtures", {})
            
            if pickup_config.get("pickup_table", 0) <= 0 and boh_config.get("pickup_table", 0) <= 0:
                print("  -> SKIPPED: 'pickup_table' not specified in configuration.")
                return
            
            fixture_obj = Fixture.Fixture("pickup_table", self.fixture_dict["pickup_table"]["path"])
        except Exception as e:
            print(f"  -> 🔥 ERROR loading 'pickup_table': {e}")
            return

        # 2. Find BOH zone
        boh_zone = self._get_boh_zone_polygon()
        if not boh_zone:
            print("  -> ⚠️ FAILED: Could not find BOH zone to place pickup_table in.")
            return

        # 3. Setup for 2D Resilient Grid Search (RIGHT SIDE)
        boh_bounds = boh_zone.bounds
        margin = 50.0
        
        # ***** KEY CHANGE: Start from the RIGHT side *****
        search_start_y = boh_bounds[1] + margin - 150.0  # Same downward nudge
        search_end_y = search_start_y + 500.0  # Search upward 500mm
        
        # ***** KEY CHANGE: Search from RIGHT to LEFT *****
        search_start_x = boh_bounds[2] - fixture_obj.width - margin  # Start from right edge
        search_end_x = boh_bounds[0] + margin  # End at left edge
        
        step = 100.0  # Grid step size in mm
        is_placed = False

        # 4. 2D Grid Search Loop (Searches upwards, then LEFTWARDS)
        print("  -> Searching for a spot along the bottom-right of the BOH zone (2D Grid Search)...")
        
        y_try = search_start_y
        while y_try < search_end_y:
            # ***** KEY CHANGE: Search from right to left (decreasing X) *****
            x_try = search_start_x
            while x_try > search_end_x:
                candidate_box = box(x_try, y_try, x_try + fixture_obj.width, y_try + fixture_obj.height)
                
                is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
                is_inside = boh_zone.contains(candidate_box)

                if is_inside and not is_overlapping:
                    self.place_fixture(fixture_obj, (x_try, y_try, 0), 0, False)
                    placed_bboxes.append(candidate_box.bounds)
                    print(f"    ✅ SUCCESS: Placed '{fixture_obj.name}' in the BOH zone at (x={x_try:.0f}, y={y_try:.0f}).")
                    is_placed = True
                    break # Exit inner x-loop on success
                
                x_try -= step  # ***** KEY CHANGE: Decrement instead of increment *****
            
            if is_placed:
                break # Exit outer y-loop on success
            
            y_try += step

        # 5. Final Failure Message
        if not is_placed:
            print("    -> ⚠️ FAILED: The entire bottom-right area of the BOH zone was blocked or invalid.")
    
#---------------------NEW_PICKUP_WINDOW FUNCTION WITH PICKUP TABLE FALL BACK SETUP---------------------
#---------------------NEW_PICKUP_WINDOW FUNCTION WITH PICKUP TABLE FALL BACK SETUP---------------------


#---- PICKUP WINDOW PLACEMENT FUNCTION FINISHED HERE ----

#-----back-room-finding--setup--------------------starts-here--------------------
#-----back-room-finding--setup--------------------starts-here--------------------


    def detect_back_corner_room_v1(self, partition_min_length: float = 1000.0) -> Optional[str]:
        """
        Detects if a room exists in a back corner (left or right).

        This works by finding internal partitions and checking for a specific
        pattern where a horizontal partition near the back wall meets a
        vertical partition near a side wall.

        Args:
            self: The DXF_Controller instance.
            partition_min_length (float): The minimum length for a wall segment to be
                                        considered a significant internal partition.

        Returns:
            'left' if a room is detected in the back-left corner.
            'right' if a room is detected in the back-right corner.
            None if no such room is detected.
        """
        print("\n--- 🔍 Detecting Back Corner Room ---")
        # 1. Get all significant internal partitions from the CV_Controller
        # Using a wider range to catch walls of different sizes.
        internal_partitions = self.cvc.get_internal_wall_partitions(min_length=1000,max_length=3000,thickness=0.0)
        if len(internal_partitions) < 2:
            print("  -> Not enough internal partitions to form a room.")
            return None

        # 2. Get floorplan dimensions for relative positioning
        min_x, max_x = self.cvc.min_x, self.cvc.max_x
        min_y, max_y = self.cvc.min_y, self.cvc.max_y
        width = max_x - min_x
        height = max_y - min_y

        # 3. Define zones for "back" and "side" walls (e.g., top 30% of height)
        back_zone_y_start = max_y - (height * 0.30)
        left_zone_x_end = min_x + (width * 0.30)
        right_zone_x_start = max_x - (width * 0.30)

        # 4. Categorize partitions into "red" (back, horizontal) and "blue" (side, vertical)
        red_lines = []
        blue_lines = []

        for p in internal_partitions:
            p_line = LineString([(p[0], p[1]), (p[2], p[3])])
            dx = abs(p[2] - p[0])
            dy = abs(p[3] - p[1])
            avg_y = (p[1] + p[3]) / 2
            avg_x = (p[0] + p[2]) / 2

            # Check for horizontal lines in the back zone ("red lines")
            if dx > dy and avg_y >= back_zone_y_start:
                red_lines.append(p_line)
            # Check for vertical lines in the side zones ("blue lines")
            elif dy > dx:
                if avg_x <= left_zone_x_end:
                    blue_lines.append({'line': p_line, 'side': 'left'})
                elif avg_x >= right_zone_x_start:
                    blue_lines.append({'line': p_line, 'side': 'right'})

        print(f"  -> Found {len(red_lines)} potential back walls (red) and {len(blue_lines)} potential side walls (blue).")

        # 5. Search for an intersection ("green dot") between a red and a blue line
        for red_line in red_lines:
            for blue_line_data in blue_lines:
                blue_line = blue_line_data['line']
                
                # ***** THE FIX IS HERE *****
                # Instead of a direct intersection, we create a small 5mm "halo" around the
                # red line to catch near-misses and almost-touching endpoints.
                if red_line.buffer(5.0).intersects(blue_line):
                    side = blue_line_data['side']
                    print(f"  -> ✅ Match found! Back corner room detected on the '{side}' side.")
                    return side

        print("  -> ℹ️ No back corner room pattern was detected.")
        return None
    
    def draw_detected_room_for_validation_v1(self, partition_min_length: float = 1000.0):
        """
        A debugging helper to visualize the partitions being analyzed by
        detect_back_corner_room.

        - "Red" lines are horizontal partitions in the back zone.
        - "Blue" lines are vertical partitions in the side zones.
        - "Green" dots are the intersection points that form a corner room.

        Args:
            self: The DXF_Controller instance.
            partition_min_length (float): The minimum length for a wall segment.
        """
        print("\n--- 🎨 Drawing Detected Room Partitions for Validation ---")
        internal_partitions = self.cvc.get_internal_wall_partitions(min_length=1000,max_length=3000,thickness=0.0)
        if len(internal_partitions) < 2:
            return

        # Define layers for visualization
        if "DEBUG_ROOM_RED" not in self.doc.layers:
            self.doc.layers.add(name="DEBUG_ROOM_RED", color=1)  # Red
        if "DEBUG_ROOM_BLUE" not in self.doc.layers:
            self.doc.layers.add(name="DEBUG_ROOM_BLUE", color=5)  # Blue
        if "DEBUG_ROOM_GREEN_DOT" not in self.doc.layers:
            self.doc.layers.add(name="DEBUG_ROOM_GREEN_DOT", color=3)  # Green

        # Get dimensions and define zones (same logic as detection function)
        min_x, max_x, min_y, max_y = self.cvc.min_x, self.cvc.max_x, self.cvc.min_y, self.cvc.max_y
        width, height = max_x - min_x, max_y - min_y
        back_zone_y_start = max_y - (height * 0.30)
        left_zone_x_end = min_x + (width * 0.30)
        right_zone_x_start = max_x - (width * 0.30)

        red_lines = []
        blue_lines = []

        # Categorize and draw the red/blue lines
        for p in internal_partitions:
            p_line = LineString([(p[0], p[1]), (p[2], p[3])])
            dx, dy = abs(p[2] - p[0]), abs(p[3] - p[1])
            avg_y, avg_x = (p[1] + p[3]) / 2, (p[0] + p[2]) / 2

            if dx > dy and avg_y >= back_zone_y_start:
                red_lines.append(p_line)
                self.msp.add_line(p_line.coords[0], p_line.coords[1], dxfattribs={"layer": "DEBUG_ROOM_RED", "lineweight": 50})
            elif dy > dx:
                if avg_x <= left_zone_x_end:
                    blue_lines.append({'line': p_line, 'side': 'left'})
                    self.msp.add_line(p_line.coords[0], p_line.coords[1], dxfattribs={"layer": "DEBUG_ROOM_BLUE", "lineweight": 50})
                elif avg_x >= right_zone_x_start:
                    blue_lines.append({'line': p_line, 'side': 'right'})
                    self.msp.add_line(p_line.coords[0], p_line.coords[1], dxfattribs={"layer": "DEBUG_ROOM_BLUE", "lineweight": 50})

        # Find and draw intersection points ("green dots")
        for red_line in red_lines:
            for blue_line_data in blue_lines:
                blue_line = blue_line_data['line']
                # ***** THE FIX IS HERE *****
                # Use the same buffered intersection logic as the detection function.
                if red_line.buffer(5.0).intersects(blue_line):
                    # Now, find the intersection between the BUFFERED red line and the blue line.
                    # The result is a small LineString where they cross.
                    intersection_geom = red_line.buffer(5.0).intersection(blue_line)
                    
                    if not intersection_geom.is_empty:
                        # The centroid of this small intersection LineString is the perfect spot for our dot.
                        intersection_point = intersection_geom.centroid
                        self.msp.add_circle(
                            center=intersection_point.coords[0], 
                            radius=100, 
                            dxfattribs={"layer": "DEBUG_ROOM_GREEN_DOT"}
                        )
        
        print("  -> Drawing complete. Check DXF for red/blue lines and green dots.")


    def detect_back_corner_room(self, partition_min_length: float = 1000.0) -> Optional[str]:
        """
        [V9 - FINAL BUFFER INCREASE] Increases the intersection buffer to handle
        larger geometric gaps between wall segments.
        """
        print("\n--- 🔍 Detecting Back Corner Room (v9 - Final Buffer Increase) ---")

        # (The setup and filtering logic from V8 is correct and remains unchanged)
        candidate_partitions = self.cvc.get_internal_wall_partitions(min_length=1000, max_length=3000, thickness=0.0)
        if not candidate_partitions: return None

        BOUNDARY_TOLERANCE = 150.0
        internal_partitions = [p for p in candidate_partitions if self.floorplan_polygon.boundary.distance(LineString([(p[0], p[1]), (p[2], p[3])]).centroid) > BOUNDARY_TOLERANCE]

        if len(internal_partitions) < 2:
            print("  -> Not enough true internal partitions after filtering.")
            return None

        top_wall_zones = self._analyze_top_wall_with_bulge_detection_new()
        if not top_wall_zones:
            print("  -> ⚠️ Could not determine main back wall orientation. Aborting.")
            return None
        
        p1_ref, p2_ref = top_wall_zones[0]['start'], top_wall_zones[0]['end']
        back_wall_angle_deg = math.degrees((p2_ref - p1_ref).normalize().angle)
        print(f"  -> Main back wall orientation detected at {back_wall_angle_deg:.1f}°")

        min_x, max_x, min_y, max_y = self.cvc.min_x, self.cvc.max_x, self.cvc.min_y, self.cvc.max_y
        width, height = max_x - min_x, max_y - min_y
        back_zone_y_start, left_zone_x_end, right_zone_x_start = max_y - (height * 0.40), min_x + (width * 0.40), max_x - (width * 0.40)

        red_lines, blue_lines = [], []
        ANGLE_TOLERANCE = 15.0 

        for p in internal_partitions:
            p1, p2 = Vec2(p[0], p[1]), Vec2(p[2], p[3])
            p_line = LineString([p1, p2])
            seg_vec = p2 - p1
            seg_angle_deg = math.degrees(seg_vec.angle)
            avg_y, avg_x = (p1.y + p2.y) / 2, (p1.x + p2.x) / 2
            if avg_y < back_zone_y_start: continue

            angle_diff_parallel = abs((seg_angle_deg - back_wall_angle_deg + 180) % 360 - 180)
            if angle_diff_parallel < ANGLE_TOLERANCE:
                red_lines.append(p_line)
                continue

            angle_diff_perp = abs((seg_angle_deg - (back_wall_angle_deg + 90) + 180) % 360 - 180)
            if angle_diff_perp < ANGLE_TOLERANCE:
                if avg_x <= left_zone_x_end:
                    blue_lines.append({'line': p_line, 'side': 'left'})
                elif avg_x >= right_zone_x_start:
                    blue_lines.append({'line': p_line, 'side': 'right'})

        print(f"  -> Found {len(red_lines)} potential back walls (red) and {len(blue_lines)} potential side walls (blue) after angle-based filtering.")

        # 5. Intersection check with LARGER BUFFER
        for red_line in red_lines:
            for blue_line_data in blue_lines:
                blue_line = blue_line_data['line']
                
                # ***** THE FIX IS HERE: Increased buffer from 50.0 to 150.0 *****
                buffered_red_line = red_line.buffer(150.0)
                
                if buffered_red_line.intersects(blue_line):
                    intersection_geom = buffered_red_line.intersection(blue_line)
                    if not intersection_geom.is_empty:
                        intersection_point = intersection_geom.centroid
                        distance_from_back_wall = max_y - intersection_point.y
                        if distance_from_back_wall > 600.0:
                            side = blue_line_data['side']
                            print(f"  -> ✅ Match found! Corner at y={intersection_point.y:.0f} is {distance_from_back_wall:.0f}mm from back wall.")
                            print(f"  -> Back corner room detected on the '{side}' side.")
                            return side
                        else:
                            print(f"  -> ℹ️ Match ignored. Corner is only {distance_from_back_wall:.0f}mm from back wall.")

        print("  -> ℹ️ No valid back corner room pattern was detected.")
        return None

    def draw_detected_room_for_validation(self, partition_min_length: float = 1000.0):
        """
        [V9] Visualizes partitions using the same increased buffer to correctly
        draw the green dot.
        """
        print("\n--- 🎨 Drawing Detected Room Partitions for Validation (v9) ---")

        candidate_partitions = self.cvc.get_internal_wall_partitions(min_length=1000, max_length=3000, thickness=0.0)
        if not candidate_partitions: return

        # (Setup logic is unchanged)
        BOUNDARY_TOLERANCE = 150.0
        internal_partitions = [p for p in candidate_partitions if self.floorplan_polygon.boundary.distance(LineString([(p[0], p[1]), (p[2], p[3])]).centroid) > BOUNDARY_TOLERANCE]
        if not internal_partitions: return
        top_wall_zones = self._analyze_top_wall_with_bulge_detection_new()
        if not top_wall_zones: return
        p1_ref, p2_ref = top_wall_zones[0]['start'], top_wall_zones[0]['end']
        back_wall_angle_deg = math.degrees((p2_ref - p1_ref).normalize().angle)
        if "DEBUG_ROOM_RED" not in self.doc.layers: self.doc.layers.add(name="DEBUG_ROOM_RED", color=1)
        if "DEBUG_ROOM_BLUE" not in self.doc.layers: self.doc.layers.add(name="DEBUG_ROOM_BLUE", color=5)
        if "DEBUG_ROOM_GREEN_DOT" not in self.doc.layers: self.doc.layers.add(name="DEBUG_ROOM_GREEN_DOT", color=3)
        min_x, max_x, min_y, max_y = self.cvc.min_x, self.cvc.max_x, self.cvc.min_y, self.cvc.max_y
        height, width = max_y - min_y, max_x - min_x
        back_zone_y_start, left_zone_x_end, right_zone_x_start = max_y - (height * 0.40), min_x + (width * 0.40), max_x - (width * 0.40)

        # Angle-based Categorization and Drawing (Unchanged)
        red_lines, blue_lines = [], []
        ANGLE_TOLERANCE = 15.0
        for p in internal_partitions:
            p1, p2 = Vec2(p[0], p[1]), Vec2(p[2], p[3])
            p_line = LineString([p1, p2])
            seg_vec = p2 - p1
            seg_angle_deg = math.degrees(seg_vec.angle)
            avg_y, avg_x = (p1.y + p2.y) / 2, (p1.x + p2.x) / 2
            if avg_y < back_zone_y_start: continue
            
            angle_diff_parallel = abs((seg_angle_deg - back_wall_angle_deg + 180) % 360 - 180)
            if angle_diff_parallel < ANGLE_TOLERANCE:
                red_lines.append(p_line)
                self.msp.add_line(p_line.coords[0], p_line.coords[1], dxfattribs={"layer": "DEBUG_ROOM_RED", "lineweight": 50})
                continue

            angle_diff_perp = abs((seg_angle_deg - (back_wall_angle_deg + 90) + 180) % 360 - 180)
            if angle_diff_perp < ANGLE_TOLERANCE:
                if avg_x <= left_zone_x_end:
                    blue_lines.append({'line': p_line, 'side': 'left'})
                    self.msp.add_line(p_line.coords[0], p_line.coords[1], dxfattribs={"layer": "DEBUG_ROOM_BLUE", "lineweight": 50})
                elif avg_x >= right_zone_x_start:
                    blue_lines.append({'line': p_line, 'side': 'right'})
                    self.msp.add_line(p_line.coords[0], p_line.coords[1], dxfattribs={"layer": "DEBUG_ROOM_BLUE", "lineweight": 50})

        # Intersection Drawing with LARGER BUFFER
        for red_line in red_lines:
            for blue_line_data in blue_lines:
                blue_line = blue_line_data['line']
                
                # ***** APPLYING THE SAME FIX HERE *****
                buffered_red_line = red_line.buffer(150.0)
                
                if buffered_red_line.intersects(blue_line):
                    intersection_geom = buffered_red_line.intersection(blue_line)
                    if not intersection_geom.is_empty:
                        intersection_point = intersection_geom.centroid
                        if (max_y - intersection_point.y) > 600.0:
                            self.msp.add_circle(center=intersection_point.coords[0], radius=200, dxfattribs={"layer": "DEBUG_ROOM_GREEN_DOT"})
        
        print("  -> Drawing complete. Check DXF for correctly filtered red/blue lines and green dots.")

    def orchestrate_clinic_placement(self, all_placed_bboxes: List[tuple]):
        """
        Orchestrates the main clinic placement by first detecting back corner rooms.
        If a room is found on the back-left, it executes the 'opposite' (right-to-left)
        placement strategy to keep the BOH area away from the room. Otherwise, it
        proceeds with the default (left-to-right) strategy.
        """
        print("\n--- 🧭 Orchestrating Main Clinic Placement Strategy ---")

        # First, detect if a room exists in a back corner and get its location.
        back_room_location = self.detect_back_corner_room()
        self.back_room_location = back_room_location # Store the result

        # If a room is detected on the 'left'...
        if back_room_location == 'left':
            print("  -> Back-left room detected. Executing OPPOSITE (right-to-left) clinic placement strategy.")
            # ...call the opposite placement function.
            self.place_clinics_master_strategy_opposite(all_placed_bboxes)
            all_placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
            self._place_pickup_table_in_boh_right(all_placed_bboxes)

        else:
            # If the room is on the right or not detected at all...
            if back_room_location == 'right':
                print("  -> Back-right room detected. Using DEFAULT (left-to-right) clinic placement strategy.")
            else:
                print("  -> No back corner room detected. Using DEFAULT (left-to-right) clinic placement strategy.")
            # ...call the default placement function.
            self.place_clinics_master_strategy(all_placed_bboxes)
            all_placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
            self.place_pickup_area_fixture(all_placed_bboxes)

#-----back-room-finding--setup--------------------stops-here--------------------
#-----back-room-finding--setup--------------------stops-here--------------------



#---- TOILET PLACEMENT FUNCTION STARTS HERE ----
    
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

#---- TOILET PLACEMENT FUNCTION FINISHED HERE ----
#---- Back-of-House (BOH) PLACEMENT FUNCTION STARTED HERE ----

#---------------------------------NEW-WALK-BY-SEGMENT-PLACING-FOR-BOH-FIXTURES------------------------------
#---------------------------------NEW-WALK-BY-SEGMENT-PLACING-FOR-BOH-FIXTURES------------------------------

    def _get_boh_perimeter_path_from_bottom_right_ccw(self):
        """
        [NEW HELPER] Gets the BOH inner perimeter path, starting from the
        bottom-right corner and proceeding counter-clockwise.
        """
        from ezdxf.math import Vec2
        import math

        # Step 1: Get the inner BOH polygon
        boh_outlines = list(self.msp.query('LWPOLYLINE[layer=="BOH_WALL_VALID_OUTLINE"]'))
        if not boh_outlines:
            boh_outlines = list(self.msp.query('LWPOLYLINE[layer=="BOH_PARTITION_OUTLINE"]'))
        if not boh_outlines:
            return []
        polygons = [Polygon(list(p.get_points('xy'))) for p in boh_outlines]
        if not polygons:
            return []
        boh_placement_zone = min(polygons, key=lambda p: p.area)
        
        perimeter_coords_tuples = list(boh_placement_zone.exterior.coords)[:-1] # Remove duplicate closing point
        
        # Step 2: Find the corner closest to the theoretical bottom-right
        if not perimeter_coords_tuples:
            return []

        boh_bounds = boh_placement_zone.bounds
        target_x = boh_bounds[2] # max_x
        target_y = boh_bounds[1] # min_y

        start_idx = min(range(len(perimeter_coords_tuples)),
                        key=lambda i: math.hypot(perimeter_coords_tuples[i][0] - target_x, perimeter_coords_tuples[i][1] - target_y))

        # Step 3: Reorder the path to start from that corner
        reordered_coords = perimeter_coords_tuples[start_idx:] + perimeter_coords_tuples[:start_idx]

        # Step 4: Check and enforce Counter-Clockwise (CCW) direction
        # A positive signed area means the path is already CCW.
        # A negative signed area means it's CW, so we must reverse it.
        path_points_vec = [Vec2(p) for p in reordered_coords]
        signed_area = 0.5 * sum(p1.x * p2.y - p2.x * p1.y for p1, p2 in zip(path_points_vec, path_points_vec[1:] + [path_points_vec[0]]))

        if signed_area < 0: # It's Clockwise, needs reversal
            print("  -> Path was clockwise. Reversing to ensure counter-clockwise direction from bottom-right.")
            # Keep the start point, but reverse the order of the rest of the points
            final_ordered_coords = reordered_coords[0:1] + reordered_coords[1:][::-1]
        else:
            final_ordered_coords = reordered_coords

        # Step 5: Build the final segment path
        final_path = []
        for i in range(len(final_ordered_coords)):
            p1 = Vec2(final_ordered_coords[i])
            p2 = Vec2(final_ordered_coords[(i + 1) % len(final_ordered_coords)])
            final_path.append((p1, p2))
            
        return final_path

    
    # DXF_Controller.py, Line 4725 approx.

    def get_boh_zone_wall_segment(self) -> dict:
        """
        [CORRECTED] Analyzes the BOH zone polygon, gets the raw segments, 
        and then reduces the effective length based on corner geometry.
        """
        from ezdxf.math import Vec2
        import math

        print("\n--- 🧱 Analyzing BOH Zone Wall Segments (Bottom-Right, CCW) ---")

        # 1. Get the ordered perimeter path (raw, unadjusted coordinates)
        perimeter_path = self._get_boh_perimeter_path_from_bottom_right_ccw()
        if not perimeter_path:
            print("  -> WARNING: Could not generate a BOH perimeter path.")
            return {}

        # 2. GENERATE UNADJUSTED SEGMENT DATA
        unadjusted_segments = {}
        for i, (p1, p2) in enumerate(perimeter_path):
            if p1.distance(p2) > 50:
                unadjusted_segments[i] = {
                    'start_point': (p1.x, p1.y), 
                    'end_point': (p2.x, p2.y), 
                    'length': p1.distance(p2), 
                    'angle': math.degrees((p2 - p1).angle),
                    'vector': (p2 - p1)
                }

        # 3. IDENTIFY INTERNAL CORNERS
        # **** CRITICAL CHANGE: Pass the raw segment data to the corner finder ****
        boh_internal_corners = self._find_internal_corners_from_raw_data(unadjusted_segments)
        corner_points_set = {
            (round(c['point'][0]), round(c['point'][1])) for c in boh_internal_corners
        }

        # 4. APPLY SEGMENT REDUCTION LOGIC
        wall_segments_data = {}
        CORNER_RESERVATION_MM = 300.0 
        
        for i in sorted(unadjusted_segments.keys()):
            seg_data = unadjusted_segments[i]
            p1 = Vec2(seg_data['start_point'])
            p2 = Vec2(seg_data['end_point'])
            segment_vector = seg_data['vector'].normalize()
            
            effective_p1 = p1
            effective_p2 = p2

            # Check if segment ENDS at an internal corner (p2 is the junction point)
            if (round(p2.x), round(p2.y)) in corner_points_set:
                effective_p2 = p2 - segment_vector * CORNER_RESERVATION_MM
                print(f"  -> Segment {i} ENDS at internal corner. Reducing length by {CORNER_RESERVATION_MM}mm.")

            # Check if segment STARTS at an internal corner (p1 is the junction point)
            if (round(p1.x), round(p1.y)) in corner_points_set:
                effective_p1 = p1 + segment_vector * CORNER_RESERVATION_MM
                print(f"  -> Segment {i} STARTS at internal corner. Reducing length by {CORNER_RESERVATION_MM}mm.")
            
            # 5. STORE FINAL, ADJUSTED DATA
            final_segment_length = effective_p1.distance(effective_p2)
            
            if final_segment_length > 450.0:
                wall_segments_data[i] = {
                    'start_point': (effective_p1.x, effective_p1.y),
                    'end_point': (effective_p2.x, effective_p2.y),
                    'length': final_segment_length,
                    'angle': math.degrees(segment_vector.angle)
                }

        print(f"  -> ✅ Successfully identified {len(wall_segments_data)} wall segments with CORNER RESERVATION applied.")
        return wall_segments_data

    def get_boh_zone_wall_segment_og(self) -> dict:
        """
        [MODIFIED] Analyzes the BOH zone polygon and returns details for each of its wall segments,
        starting from the bottom-right corner and proceeding counter-clockwise.
        """
        from ezdxf.math import Vec2
        import math

        print("\n--- 🧱 Analyzing BOH Zone Wall Segments (Bottom-Right, CCW) ---")

        # 1. Get the ordered perimeter path using the new helper function
        perimeter_path = self._get_boh_perimeter_path_from_bottom_right_ccw()
        if not perimeter_path:
            print("  -> WARNING: Could not generate a BOH perimeter path.")
            return {}

        wall_segments_data = {}
        
        # 2. Iterate through the correctly ordered segments
        for i, (p1, p2) in enumerate(perimeter_path):
            segment_length = p1.distance(p2)

            if segment_length < 50:
                continue

            segment_vector = p2 - p1
            segment_angle_deg = math.degrees(segment_vector.angle)

            # 3. Store the collected data
            wall_segments_data[i] = {
                'start_point': (p1.x, p1.y),
                'end_point': (p2.x, p2.y),
                'length': segment_length,
                'angle': segment_angle_deg
            }

        print(f"  -> ✅ Successfully identified {len(wall_segments_data)} wall segments, starting from the bottom-right.")
        return wall_segments_data

    def draw_boh_segment_order_for_validation_br_ccw(self):
        """
        [DEBUG HELPER] Draws numbered labels on the BOH inner wall segments,
        starting from the bottom-right corner and proceeding counter-clockwise,
        to visually confirm the processing order.
        """
        from ezdxf.math import Vec2
        import math

        print("\n--- 🎨 Drawing BOH Segment Order for Validation (Bottom-Right, CCW) ---")

        # 1. Get the correctly ordered perimeter path using the helper function
        perimeter_path = self._get_boh_perimeter_path_from_bottom_right_ccw()
        if not perimeter_path:
            print("  -> SKIPPED: No BOH perimeter path found to draw.")
            return
        
        # 2. Define a new, highly visible layer for the debug drawings
        layer_name = "DEBUG_BOH_SEGMENT_ORDER_BR_CCW"
        if layer_name not in self.doc.layers:
            self.doc.layers.add(name=layer_name, color=1) # ACI color 1 is Red

        # 3. Loop through the segments and draw a label on each one
        for i, (p1, p2) in enumerate(perimeter_path):
            # Skip very short, insignificant segments
            if p1.distance(p2) < 450:
                continue

            # Calculate the midpoint of the segment to place the label
            mid_point = p1.lerp(p2)
            
            # Add a numbered text label
            self.msp.add_mtext(
                f"BOH-{i+1}",
                dxfattribs={
                    'char_height': 150,  # Adjust text size as needed
                    'insert': mid_point,
                    'layer': layer_name
                }
            )
            
        print(f"  -> ✅ Drew {len(perimeter_path)} numbered labels on layer '{layer_name}'. Check the DXF file.")

    def get_boh_fixture_dimensions(self) -> dict:
        """
        Calculates and returns the width and height for all BOH (Back-of-House) fixtures.

        This function iterates through the main fixture dictionary, filters for fixtures
        of type 'boh', loads each one to get its bounding box dimensions, and
        returns the data in a structured dictionary.

        Returns:
            A dictionary where keys are the BOH fixture names and values are
            another dictionary containing 'width' and 'height'.
            Example:
            {
                'storage_rack': {'width': 1200.0, 'height': 450.0},
                'ups_rack': {'width': 600.0, 'height': 600.0}
            }
        """
        # import Fixture # Ensure the Fixture class is available
        print("\n--- 📏 Calculating Dimensions for BOH Fixtures ---")
        
        boh_dimensions = {}

        # Iterate through the master dictionary of all available fixtures
        for fixture_name, fixture_data in self.fixture_dict.items():
            # Check if the fixture is categorized as 'boh'
            if fixture_data.get("type") == "boh":
                try:
                    # Load the fixture object to access its geometric properties
                    fxtr = Fixture.Fixture(fixture_name, fixture_data["path"])
                    
                    # Store the width and height in the results dictionary
                    boh_dimensions[fixture_name] = {
                        'width': fxtr.width,
                        'height': fxtr.height
                    }
                except Exception as e:
                    print(f"  -> ⚠️ WARNING: Could not load fixture '{fixture_name}' to get dimensions. Error: {e}")
        
        print(f"  -> ✅ Found dimensions for {len(boh_dimensions)} BOH fixtures.")
        return boh_dimensions

    # DXF_Controller.py, Add this helper function

    def _find_internal_corners_from_raw_data(self, unadjusted_segment_data: dict) -> list:
        """
        [NEW HELPER] Analyzes the raw segment data (no length adjustment) to find 
        internal (concave) corners. This breaks the recursion loop.
        """
        segments = sorted(unadjusted_segment_data.items())

        if len(segments) < 2:
            return []

        internal_corners = []
        # The segment data contains the segment key (0, 1, 2, ...) and the segment details dict.
        for i in range(len(segments) - 1):
            # Extract the actual segment data dictionary
            segment_a = segments[i][1]
            segment_b = segments[i+1][1]

            angle_a = segment_a["angle"]
            angle_b = segment_b["angle"]
            
            # The corner point is the end point of segment A
            corner_point = segment_a["end_point"]

            # Calculate the angular change, normalized to [-180, 180]
            angle_difference = (angle_b - angle_a + 180) % 360 - 180
            
            # CRITERION: A right turn on a CCW path is an internal corner (negative angle).
            # The original logic for CCW path (line 4945) had an error checking for positive angles.
            # Correcting to check for a right turn (negative angle change).
            if 0 < angle_difference < 360: # Tolerance for a right turn on CCW path
                corner_details = {
                    "point": corner_point,
                    "angle_in": angle_a,
                    "angle_out": angle_b,
                    "angle_change": angle_difference
                }
                internal_corners.append(corner_details)

        return internal_corners

    # DXF_Controller.py, Line 4913 approx.

    def find_internal_corners_boh_zone(self) -> list:
        """
        [CORRECTED WRAPPER] Retrieves the raw segment data and finds the internal corners.
        This function no longer calls get_boh_zone_wall_segment() recursively.
        """
        print("\n--- 🔍 Finding Internal Corners of the BOH Zone (Wrapper) ---")

        # 1. Get the ordered perimeter path (raw, unadjusted coordinates)
        perimeter_path = self._get_boh_perimeter_path_from_bottom_right_ccw()
        if not perimeter_path:
            return []
            
        # 2. GENERATE UNADJUSTED SEGMENT DATA
        unadjusted_segments = {}
        for i, (p1, p2) in enumerate(perimeter_path):
            if p1.distance(p2) > 50:
                unadjusted_segments[i] = {
                    'start_point': (p1.x, p1.y), 
                    'end_point': (p2.x, p2.y), 
                    'length': p1.distance(p2), 
                    'angle': math.degrees((p2 - p1).angle),
                    'vector': (p2 - p1)
                }

        # 3. Call the internal helper with the raw data
        internal_corners = self._find_internal_corners_from_raw_data(unadjusted_segments)
        
        print(f"--- ✅ BOH Corner Finding Complete. Found {len(internal_corners)} internal corners. ---")
        return internal_corners
    

    def classify_boh_zone_shape(self, tolerance_mm: float = 1000.0) -> Tuple[str, Optional[float], Optional[float]]:
        """
        Calculates the bounding box dimensions of the actual BOH zone (inner wall) 
        and classifies it as 'Rectangular' ONLY if the dimension difference EXCEEDS the tolerance.
        
        Args:
            tolerance_mm (float): The threshold in mm.

        Returns:
            Tuple[str, Optional[float], Optional[float]]: (classification, width_mm, height_mm)
        """
        print("\n--- 📐 Classifying BOH Zone Shape (Reversed Logic) ---")
        
        # 1. Find the BOH zone polygon (Robustly selecting the INNER perimeter)
        boh_outlines = list(self.msp.query('LWPOLYLINE[layer=="BOH_WALL_VALID_OUTLINE"]'))
        if not boh_outlines:
            boh_outlines = list(self.msp.query('LWPOLYLINE[layer=="BOH_PARTITION_OUTLINE"]'))

        if not boh_outlines:
            print("  -> ERROR: BOH zone outline not found.")
            return ("Unknown", None, None)
            
        polygons = [Polygon(list(p.get_points('xy'))) for p in boh_outlines]
        if not polygons:
            return ("Unknown", None, None)
            
        # CRITICAL FIX: The inner perimeter is the one with the smallest area
        boh_placement_zone = min(polygons, key=lambda p: p.area)
        
        # 2. Get BOH zone bounding box dimensions from the selected INNER polygon
        min_x, min_y, max_x, max_y = boh_placement_zone.bounds
            
        width = max_x - min_x
        height = max_y - min_y
        
        # 3. Calculate the difference between the two dimensions
        dimension_difference = abs(width - height)
        
        # 4. Classify the shape using the REVERSED logic
        if dimension_difference > tolerance_mm:
            classification = "Rectangular"
            print(f"  -> Classification: {classification}")
            print(f"  -> Difference ({dimension_difference:.0f}mm) EXCEEDS the {tolerance_mm:.0f}mm tolerance.")
        else:
            classification = "Irregular Polygon"
            print(f"  -> Classification: {classification}")
            print(f"  -> Difference ({dimension_difference:.0f}mm) is WITHIN the {tolerance_mm:.0f}mm tolerance.")

        print(f"  -> BOH Zone Bounding Box: {width:.0f}mm (Width) x {height:.0f}mm (Height)")
        return (classification, width, height)
    

    def plan_boh_fixture_placement(self) -> list:
        """
        [MODIFIED] Plans the placement of BOH fixtures by packing them along the BOH walls with no gaps.
        - Applies a 200mm inset to subsequent segments to avoid corner overlaps.
        - If a back-left room is detected, it SKIPS segment 0 and starts placement from segment 1.
        """
        # import Fixture
        from ezdxf.math import Vec2
        from shapely.geometry import Point
        import math

        print("\n--- 📝 Planning BOH Fixture Placement (Greedy Packing with Corner Insets) ---")

        # --- 1. GATHER ALL NECESSARY DATA ---
        boh_counts = self.fixtures.get("boh_fixtures", {})
        boh_dimensions = self.get_boh_fixture_dimensions()
        wall_segments = self.get_boh_zone_wall_segment() 

        if not boh_counts or not boh_dimensions or not wall_segments:
            print("  -> ⚠️ FAILED: Missing counts, dimensions, or wall segments. Cannot create a plan.")
            return []

        # --- 2. CREATE A PRIORITIZED "TO-DO" LIST OF FIXTURES ---
        fixtures_to_plan = []
        for name, count in boh_counts.items():
            if count > 0 and name in boh_dimensions:
                for _ in range(count):
                    fixtures_to_plan.append({
                        "name": name,
                        "width": boh_dimensions[name]['width'],
                        "height": boh_dimensions[name]['height']
                    })
        
        fixtures_to_plan.sort(key=lambda f: f['width'], reverse=True)
        print(f"  -> Prioritized {len(fixtures_to_plan)} BOH fixtures to plan, starting with the widest.")

        # --- 3. EXECUTE THE PACKING ALGORITHM ---
        placement_plan = []
        margin_from_wall = 10.0 
        boh_zone_poly = self._get_boh_zone_polygon()

        # --- MODIFICATION START: Conditionally skip the first segment ---
        segment_ids = sorted(wall_segments.keys())
        segment_ids_to_process = segment_ids

        # Check the stored back room location
        if self.back_room_location == 'left' and len(segment_ids) > 1:
            print("  -> Back-left room detected. SKIPPING segment 0 to start BOH placement from segment 1.")
            # Create a new list of segments to process, starting from the second one
            segment_ids_to_process = segment_ids[1:]
        # --- MODIFICATION END ---
        
        # --- The loop now uses the potentially modified list ---
        for seg_id in segment_ids_to_process:
            segment = wall_segments[seg_id]
            p1 = Vec2(segment['start_point'])
            p2 = Vec2(segment['end_point'])
            seg_len = segment['length']
            seg_angle = segment['angle']
            
            wall_vector = (p2 - p1).normalize()
            inward_normal = wall_vector.orthogonal()
            if not boh_zone_poly.contains(Point(p1.lerp(p2) + inward_normal * 10)):
                inward_normal = -inward_normal

            # Inset logic now checks if it's the *first segment being processed*
            inset_for_corners = 100.0
            if seg_id == segment_ids_to_process[0]: # Check if this is the first item in our processing list
                cursor = 0.0 
                print(f"\n  -> Planning Segment {seg_id} (Length: {seg_len:.0f}mm) - Starting at edge.")
            elif seg_id == segment_ids_to_process[3]: # Check if this is the first item in our processing list
                cursor = 500.0 
                print(f"\n  -> Planning Segment {seg_id} (Length: {seg_len:.0f}mm) - Starting at edge.")
            else:
                cursor = inset_for_corners
                print(f"\n  -> Planning Segment {seg_id} (Length: {seg_len:.0f}mm) - Starting with {inset_for_corners}mm inset.")
            
            while True:
                found_a_fixture_to_place = False
                for i, fixture_data in enumerate(fixtures_to_plan):
                    fixture_width = fixture_data['width']
                    fixture_height = fixture_data['height']
                    
                    if fixture_width <= (seg_len - cursor):
                        center_on_wall = p1 + wall_vector * (cursor + fixture_width / 2)
                        target_center = center_on_wall + inward_normal * (margin_from_wall + fixture_height / 2)
                        local_center_offset = Vec2(fixture_width / 2, fixture_height / 2)
                        rotated_offset = local_center_offset.rotate(math.radians(seg_angle))
                        final_insert_point = target_center - rotated_offset

                        placement_plan.append({
                            'fixture_name': fixture_data['name'],
                            'x': final_insert_point.x,
                            'y': final_insert_point.y,
                            'angle': seg_angle,
                            'segment_vector': [wall_vector.x, wall_vector.y]
                        })
                        
                        cursor += fixture_width
                        fixtures_to_plan.pop(i)
                        found_a_fixture_to_place = True
                        break 
                
                if not found_a_fixture_to_place:
                    break 

        # --- 4. FINALIZE AND RETURN THE PLAN ---
        if fixtures_to_plan:
            print(f"  -> ⚠️ WARNING: Could not plan for {len(fixtures_to_plan)} fixtures. Not enough wall space.")
            for f in fixtures_to_plan:
                print(f"      - Unplaced: {f['name']}")

        print(f"\n--- ✅ BOH Placement Plan Complete. Generated {len(placement_plan)} placements. ---")
        return placement_plan



    def plan_boh_fixture_placement_rect(self) -> list:
        """
        Plans BOH fixture placement for a 'Rectangular' zone.
        - Determines single-sided or double-sided placement based on the smallest dimension.
        - Prioritizes placing on the largest available wall segments first, 
          UNLESS height > width, in which case it prioritizes the right-most segment.
        - Uses a NO-GAP packing strategy.
        """
        import math
        from ezdxf.math import Vec2
        from shapely.geometry import Point

        print("\n--- 📝 Planning BOH Fixture Placement for RECTANGLE (Prioritized No-Gap Packing) ---")

        # --- 1. GATHER ALL NECESSARY DATA ---
        boh_counts = self.fixtures.get("boh_fixtures", {})
        boh_dimensions = self.get_boh_fixture_dimensions()
        wall_segments = self.get_boh_zone_wall_segment_og()
        # wall_segments = self.get_boh_zone_wall_segment()

        if not boh_counts or not boh_dimensions or not wall_segments:
            print("  -> ⚠️ FAILED: Missing counts, dimensions, or wall segments. Cannot create a plan.")
            return []

        # --- 2. DETERMINE PLACEMENT MODE AND SHAPE ORIENTATION ---
        _, width, height = self.classify_boh_zone_shape() 
        
        if width is None or height is None:
             print("  -> ⚠️ FAILED: Could not determine BOH dimensions for mode selection.")
             return []
        
        min_dim = min(width, height)
        DOUBLE_SIDED_THRESHOLD = 1700.0
        is_double_sided = min_dim > DOUBLE_SIDED_THRESHOLD
        is_taller = height > width
        
        print(f"  -> BOH Shape: {'Taller' if is_taller else 'Wider'} ({height:.0f}H x {width:.0f}W)")
        print(f"  -> Mode: {'DOUBLE-SIDED' if is_double_sided else 'SINGLE-SIDED'}")

        # --- 3. CREATE A PRIORITIZED "TO-DO" LIST OF FIXTURES ---
        fixtures_to_plan = []
        for name, count in boh_counts.items():
            if count > 0 and name in boh_dimensions:
                for _ in range(count):
                    fixtures_to_plan.append({
                        "name": name,
                        "width": boh_dimensions[name]['width'],
                        "height": boh_dimensions[name]['height']
                    })
        
        fixtures_to_plan.sort(key=lambda f: f['width'], reverse=True)
        
        # --- 4. DETERMINE SEGMENT PROCESSING ORDER (CUSTOMIZED) ---
        segment_list = [(k, v) for k, v in wall_segments.items()]
        
        # Determine the initial segment (The "most prioritized" segment)
        initial_segment_data = None
        initial_segment_id = -1

        if is_taller:
            # New Rule: Start with the right-most vertical segment
            print("  -> Prioritization: Starting with the RIGHT-MOST segment (Tall/Narrow BOH).")
            
            # Find the segment closest to the max_x value (right wall)
            # Boh zone coordinates: (min_x, min_y, max_x, max_y)
            boh_zone = self._get_boh_zone_polygon()
            right_wall_x = boh_zone.bounds[2]

            def is_vertical(segment_data):
                p1 = Vec2(segment_data['start_point'])
                p2 = Vec2(segment_data['end_point'])
                return abs(p1.y - p2.y) > abs(p1.x - p2.x)

            right_segments = [
                (k, v) for k, v in wall_segments.items() 
                if is_vertical(v) and abs((Vec2(v['start_point']).x + Vec2(v['end_point']).x)/2 - right_wall_x) < 500 
            ]

            if right_segments:
                 # Find the segment closest to the top of the BOH wall (max_y) to ensure we start in a good location
                 initial_segment_id, initial_segment_data = max(right_segments, key=lambda item: max(item[1]['start_point'][1], item[1]['end_point'][1]))
            
        
        if initial_segment_id == -1 or not is_taller:
            # Default or Fallback: Start with the largest segment
            print("  -> Prioritization: Starting with the LARGEST segment (Wider BOH or Fallback).")
            initial_segment_id, initial_segment_data = max(segment_list, key=lambda item: item[1]['length'])
        
        # Build the final processing order list
        processing_order = []
        if initial_segment_id != -1:
            processing_order.append((initial_segment_id, initial_segment_data))
            segment_list.remove((initial_segment_id, initial_segment_data))
        
        # Add the rest of the segments, sorted by length (largest remaining first)
        segment_list.sort(key=lambda item: item[1]['length'], reverse=True)
        processing_order.extend(segment_list)
        
        # In double-sided mode, restrict to the longest (max 2) walls
        if is_double_sided and len(processing_order) > 2:
            processing_order = processing_order[:2]
            print("  -> Double-Sided mode active: Restricting to the top 2 longest walls.")

        # --- 5. EXECUTE THE NO-GAP PACKING ALGORITHM ---
        placement_plan = []
        margin_from_wall = 0.0 
        boh_zone_poly = self._get_boh_zone_polygon()
        
        # Temporary logic to place the pickup table on the shortest wall first (Unchanged from last step)
        pickup_table_name = 'pickup_table'
        if any(f['name'] == pickup_table_name for f in fixtures_to_plan):
            # Check for the shortest segment among the *original* set
            shortest_segment_id = min(wall_segments.keys(), key=lambda k: wall_segments[k]['length'])
            shortest_segment = wall_segments[shortest_segment_id]
            
            p_table_data = next(f for f in fixtures_to_plan if f['name'] == pickup_table_name)
            fixtures_to_plan.remove(p_table_data)
            
            p1 = Vec2(shortest_segment['start_point'])
            p2 = Vec2(shortest_segment['end_point'])
            seg_len = shortest_segment['length']
            seg_angle = shortest_segment['angle']
            
            p_table_width = p_table_data['width']
            p_table_height = p_table_data['height']
            
            if p_table_width <= seg_len:
                wall_vector = (p2 - p1).normalize()
                inward_normal = wall_vector.orthogonal()
                if not boh_zone_poly.contains(Point(p1.lerp(p2) + inward_normal * 10)):
                    inward_normal = -inward_normal
                
                cursor = (seg_len - p_table_width) / 2
                center_on_wall = p1 + wall_vector * (cursor + p_table_width / 2)
                target_center = center_on_wall + inward_normal * (margin_from_wall + p_table_height / 2)
                local_center_offset = Vec2(p_table_width / 2, p_table_height / 2)
                rotated_offset = local_center_offset.rotate(math.radians(seg_angle))
                final_insert_point = target_center - rotated_offset

                placement_plan.append({
                    'fixture_name': p_table_data['name'],
                    'x': final_insert_point.x,
                    'y': final_insert_point.y,
                    'angle': seg_angle,
                    'segment_vector': [wall_vector.x, wall_vector.y]
                })
                print(f"  -> Placed '{p_table_data['name']}' centered on the shortest wall.")
                
            # Remove the shortest wall from the processing list to reserve it
            # NOTE: This part needs to filter based on segment ID, not the tuple, due to reordering.
            processing_order = [item for item in processing_order if item[0] != shortest_segment_id]

        for seg_id, segment in processing_order:
            if not fixtures_to_plan:
                break
                
            p1 = Vec2(segment['start_point'])
            p2 = Vec2(segment['end_point'])
            seg_len = segment['length']
            seg_angle = segment['angle']
            
            wall_vector = (p2 - p1).normalize()
            inward_normal = wall_vector.orthogonal()
            if not boh_zone_poly.contains(Point(p1.lerp(p2) + inward_normal * 10)):
                inward_normal = -inward_normal

            cursor = 0.0
            print(f"\n  -> Planning Segment {seg_id} (Length: {seg_len:.0f}mm) - Starting at edge (No Gap).")

            inset_for_corners = 500.0
            # Determine inset based on segment properties
            segment_index = next((i for i, (sid, _) in enumerate(processing_order) if sid == seg_id), -1)
            if segment_index == 0:
                cursor = inset_for_corners  # First segment: no inset
                print(f"\n  -> Planning Segment {seg_id} (Length: {seg_len:.0f}mm) - Starting at edge.")
            elif seg_len < 2000:  # Small segments get smaller inset
                cursor = 0.0
                print(f"\n  -> Planning Segment {seg_id} (Length: {seg_len:.0f}mm) - Starting with 50mm inset (small segment).")
            else:
                cursor = 0.0  # Standard inset for normal segments
                print(f"\n  -> Planning Segment {seg_id} (Length: {seg_len:.0f}mm) - Starting with 100mm inset.")


            while True:
                found_a_fixture_to_place = False
                # Iterate over a copy of the list to safely remove items
                for i, fixture_data in enumerate(fixtures_to_plan): 
                    fixture_width = fixture_data['width']
                    fixture_height = fixture_data['height']
                    
                    if fixture_width <= (seg_len - cursor):
                        center_on_wall = p1 + wall_vector * (cursor + fixture_width / 2)
                        target_center = center_on_wall + inward_normal * (margin_from_wall + fixture_height / 2)
                        local_center_offset = Vec2(fixture_width / 2, fixture_height / 2)
                        rotated_offset = local_center_offset.rotate(math.radians(seg_angle))
                        final_insert_point = target_center - rotated_offset

                        placement_plan.append({
                            'fixture_name': fixture_data['name'],
                            'x': final_insert_point.x,
                            'y': final_insert_point.y,
                            'angle': seg_angle,
                            'segment_vector': [wall_vector.x, wall_vector.y]
                        })
                        
                        cursor += fixture_width 
                        fixtures_to_plan.pop(i) # Remove the placed fixture
                        found_a_fixture_to_place = True
                        break 
                
                if not found_a_fixture_to_place:
                    break 

        # --- 6. FINALIZE AND RETURN THE PLAN ---
        if fixtures_to_plan:
            print(f"  -> ⚠️ WARNING: Could not plan for {len(fixtures_to_plan)} fixtures. Not enough wall space.")

        print(f"\n--- ✅ BOH Placement Plan Complete. Generated {len(placement_plan)} placements. ---")
        return placement_plan
    
    def execute_boh_placement_plan(self, placement_plan: list, placed_bboxes: list):
        """
        Executes a pre-computed BOH placement plan, drawing each fixture in the DXF.

        This function iterates through the plan generated by 'plan_boh_fixture_placement'.
        For each item in the plan, it:
        1. Loads the specified fixture object.
        2. Places it at the calculated (x, y) coordinates with the correct angle.
        3. Calculates the bounding box of the newly placed fixture.
        4. Adds this bounding box to the master 'placed_bboxes' list to prevent future overlaps.
        """
        from ezdxf.bbox import extents
        # import Fixture

        print("\n--- 🚀 Executing BOH Placement Plan ---")

        if not placement_plan:
            print("  -> No placement plan provided. Nothing to execute.")
            return

        placed_count = 0
        for placement in placement_plan:
            fixture_name = placement['fixture_name']
            x = placement['x']
            y = placement['y']
            angle = placement['angle']

            try:
                # Load the fixture object
                fxtr = Fixture.Fixture(fixture_name, self.fixture_dict[fixture_name]["path"])

                # Place the fixture using the details from the plan
                # We use rotated=True as these are wall-aligned fixtures
                block_ref = self.place_fixture(fxtr, (x, y, 0), angle, rotated=True)

                # After placing, calculate its bounding box and register it as an obstacle
                if block_ref:
                    try:
                        bbox = extents([block_ref])
                        placed_bboxes.append((bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y))
                        placed_count += 1
                    except (RuntimeError, TypeError):
                        print(f"  -> ⚠️ WARNING: Could not calculate bounding box for placed fixture '{fixture_name}'.")

            except Exception as e:
                print(f"  -> ⚠️ WARNING: Could not place fixture '{fixture_name}'. Skipping. Error: {e}")
                continue
        
        print(f"\n--- ✅ BOH Placement Execution Complete. Placed {placed_count} fixtures. ---")


    def place_boh_fixtures(self, all_placed_bboxes: list):
        """
        Orchestrates the BOH fixture placement by classifying the zone shape
        and calling the appropriate planning and execution functions.
        """
        BOH_WALL_SEGMENTS = self.get_boh_zone_wall_segment()
        print(json.dumps(BOH_WALL_SEGMENTS, indent=4))
        # self.draw_boh_segment_order_for_validation_br_ccw()
        classification, width, height = self.classify_boh_zone_shape(tolerance_mm=1000.0)
        print(f"\n[BOH SHAPE RESULT] The BOH zone is classified as: {classification}")
        print(f"BOH Dimensions: {width:.0f}mm Width, {height:.0f}mm Height")
        if classification == "Rectangular":
            boh_placement_plan = self.plan_boh_fixture_placement_rect()
        else:
            # Use the original logic for irregular polygons
            boh_placement_plan = self.plan_boh_fixture_placement()    

        
        # Step 2: Execute the plan to place the fixtures
        self.execute_boh_placement_plan(boh_placement_plan, all_placed_bboxes)


    

    
#---------------------------------NEW-WALK-BY-SEGMENT-PLACING-FOR-BOH-FIXTURES------------------------------
#---------------------------------NEW-WALK-BY-SEGMENT-PLACING-FOR-BOH-FIXTURES------------------------------


    def place_boh_after_toilet(self, placed_bboxes):
        """
        Places all BOH furniture using a "Best of Both Worlds" strategy.
        1. Fixtures are organized into logical rows (Storage, Workstations, etc.).
        2. Within each row, fixtures are sorted from widest to narrowest for efficient packing.
        3. Placement occurs within a "Smart BOH Zone" matching the floorplan's true shape.
        """
        # from Fixture import Fixture
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
                        fxtr = Fixture.Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"])
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


   
    def place_boh_intelligently(self, placed_bboxes):
        """
        Places all BOH fixtures using a multi-phase, intelligent strategy.
        - V14 (FINAL): The partition wall shape is now adjusted to "carve out"
          any existing fixtures (like clinics) to prevent overlaps.
        """
        # from Fixture import Fixture
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
                    fxtr = Fixture.Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"])
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


    def place_boh_intelligently_n(self, placed_bboxes):
        """
        DEFINITIVE STRATEGY: Combines a "Layout Simulation Blueprint" with "Best Corner"
        analysis and a "Zoned Workflow" to create a perfectly sized and logically
        arranged BOH with guaranteed staff access.
        
        CORRECTED: Uses a HORIZONTAL FLIP (xscale=-1) combined with rotation for fixture orientation.
        """
        from shapely.geometry import box, LineString, Polygon
        from ezdxf.math import Matrix44, Vec2, BoundingBox2d
        import math
        import collections
        # from Fixture import Fixture

        print("\n--- 🏛️ Placing BOH with 'Top Corner Only' and Horizontal Flip ---")

        # --- 1. Load fixtures and categorize for simulation ---
        # (This section is unchanged and works correctly)
        boh_config = self.fixtures.get("boh_fixtures", {})
        if not any(boh_config.values()):
            print("  -> INFO: No BOH fixtures specified."); return
        fixtures_by_cat = collections.defaultdict(list)
        storage_types = ["storage_rack", "pickup_storage_1200", "pickup_storage_900", "ups_rack", "staff_rack"]
        workstation_types = ["QC_table_large", "QC_table_medium", "Repair_Table_large", "Repair_Table_medium", "pickup_table"]
        amenity_types = ["Dining_Table_large", "Dining_Table_medium", "water_dispenser"]
        for name, count in boh_config.items():
            if count > 0:
                try:
                    fxtr = Fixture.Fixture(name, self.fixture_dict[name]["path"])
                    cat = "other"
                    if name in storage_types: cat = "storage"
                    elif name in workstation_types: cat = "workstation"
                    elif name in amenity_types: cat = "amenity"
                    fixtures_by_cat[cat].extend([fxtr] * count)
                except (KeyError, ValueError): continue
        if not fixtures_by_cat: return

        # --- 2. LAYOUT SIMULATION BLUEPRINT ---
        # (This section is unchanged and works correctly)
        print("  -> Blueprint: Simulating layout to calculate precise room dimensions...")
        margin, gap, CORRIDOR_DEPTH = 150.0, 150.0, 1200.0
        storage_fixtures = fixtures_by_cat["storage"]
        sim_storage_len = sum(f.width for f in storage_fixtures) + (gap * (len(storage_fixtures) - 1)) if storage_fixtures else 0
        sim_storage_depth = max(f.height for f in storage_fixtures) if storage_fixtures else 0
        workstation_fixtures = fixtures_by_cat["workstation"]
        sim_workstation_len = sum(f.width for f in workstation_fixtures) + (gap * (len(workstation_fixtures) - 1)) if workstation_fixtures else 0
        sim_workstation_depth = max(f.height for f in workstation_fixtures) if workstation_fixtures else 0
        amenity_fixtures = fixtures_by_cat["amenity"]
        sim_amenity_len = sum(f.height for f in amenity_fixtures) + (gap * (len(amenity_fixtures) - 1)) if amenity_fixtures else 0
        sim_amenity_depth = max(f.width for f in amenity_fixtures) if amenity_fixtures else 0
        main_zone_width = max(sim_storage_len, sim_workstation_len)
        main_zone_height = sim_storage_depth + CORRIDOR_DEPTH + sim_workstation_depth
        boh_w = main_zone_width + sim_amenity_depth + (margin * 3)
        boh_h = max(main_zone_height, sim_amenity_len) + (margin * 2)
        if boh_w <= 400 or boh_h <= 400: print("  -> INFO: Not enough BOH fixtures to warrant a room."); return
        print(f"  -> Blueprint complete. Required room size: {boh_w:.0f}W x {boh_h:.0f}H")
        
        # --- 3. CANDIDATE ANALYSIS (Top Corners Only) ---
        # (This section is unchanged and works correctly)
        print("  -> Analyzing TOP corners to find the best BOH location...")
        corners = {"top_right": (self.cvc.max_x, self.cvc.max_y, -1, -1), "top_left": (self.cvc.min_x, self.cvc.max_y, 1, -1)}
        best_corner = {"name": "none", "score": -1, "shape": None}
        for name, (anchor_x, anchor_y, dir_x, dir_y) in corners.items():
            px1, py1 = (anchor_x if dir_x == -1 else anchor_x), (anchor_y if dir_y == -1 else anchor_y)
            px2, py2 = anchor_x + (boh_w * dir_x), anchor_y + (boh_h * dir_y)
            candidate_box = box(min(px1, px2), min(py1, py2), max(px1, px2), max(py1, py2))
            if any(candidate_box.intersects(box(*b)) for b in placed_bboxes): print(f"    - Candidate '{name}': SKIPPED - Overlaps with existing fixtures."); continue
            boh_shape = self.floorplan_polygon.intersection(candidate_box)
            if boh_shape.is_empty: continue
            fit_score = boh_shape.area / candidate_box.area
            remaining_retail_shape = self.floorplan_polygon.difference(boh_shape)
            if remaining_retail_shape.is_empty: continue
            flow_score = remaining_retail_shape.area / remaining_retail_shape.convex_hull.area
            total_score = (fit_score * 0.7) + (flow_score * 0.3)
            print(f"    - Candidate '{name}': Fit={fit_score:.2f}, Flow={flow_score:.2f} -> Score={total_score:.2f}")
            if total_score > best_corner["score"]: best_corner = {"name": name, "score": total_score, "shape": boh_shape}
        if best_corner["name"] == "none": print("  -> ⚠️ FAILED: Could not find a suitable top corner for the BOH room."); return
        print(f"  -> ✅ Best location found: '{best_corner['name']}' with a score of {best_corner['score']:.2f}")
        boh_room_shape = best_corner["shape"]
        
        # --- 4. Draw Wall with Doorway ---
        # (This section is unchanged and works correctly)
        partition_wall_geom = boh_room_shape.boundary.difference(self.floorplan_polygon.boundary.buffer(1.0))
        if not partition_wall_geom.is_empty:
            DOOR_WIDTH = 800.0
            if partition_wall_geom.length > DOOR_WIDTH * 1.5:
                door_pos = partition_wall_geom.interpolate(partition_wall_geom.length / 2)
                door_cutout = LineString([(door_pos.x - DOOR_WIDTH / 2, door_pos.y), (door_pos.x + DOOR_WIDTH / 2, door_pos.y)]).buffer(10.0)
                final_wall_geom = partition_wall_geom.difference(door_cutout)
                for geom in getattr(final_wall_geom, 'geoms', [final_wall_geom]):
                    if not geom.is_empty and isinstance(geom, LineString): self.msp.add_lwpolyline(list(geom.coords), dxfattribs={"layer": "BOH_PARTITION_OUTLINE", "color": 40, "lineweight": 50})
            elif isinstance(partition_wall_geom, LineString): self.msp.add_lwpolyline(list(partition_wall_geom.coords), dxfattribs={"layer": "BOH_PARTITION_OUTLINE", "color": 40, "lineweight": 50})

        # --- 5. Place Fixtures by Zone with ACCURATE HORIZONTAL FLIPPING ---
        zone_bounds = boh_room_shape.bounds
        placed_bboxes.append(zone_bounds)
        internal_boh_bboxes = []

        # --- NEW HELPER FUNCTION FOR ACCURATE FLIPPED/ROTATED PLACEMENT ---
        def _place_boh_fixture(fxtr, target_center, rotation_deg=0, xscale=1.0, yscale=1.0):
            local_center = fxtr.bounding_box.center
            transform = Matrix44.chain(
                Matrix44.translate(-local_center.x, -local_center.y, 0),
                Matrix44.scale(xscale, yscale, 1.0),
                Matrix44.z_rotate(math.radians(rotation_deg)),
                Matrix44.translate(target_center.x, target_center.y, 0)
            )
            world_corners = list(transform.transform_vertices(fxtr.bounding_box.rect_vertices()))
            fixture_polygon = Polygon([(p.x, p.y) for p in world_corners])
            aabb = BoundingBox2d(world_corners)

            is_inside = boh_room_shape.contains(fixture_polygon)
            is_overlapping = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in internal_boh_bboxes)

            if is_inside and not is_overlapping:
                local_center_scaled = Vec2(local_center.x * xscale, local_center.y * yscale)
                rotated_offset = local_center_scaled.rotate(math.radians(rotation_deg))
                final_insert_point = target_center - rotated_offset
                self.place_fixture(fxtr, (final_insert_point.x, final_insert_point.y, 0), rotation_deg, False, xscale=xscale, yscale=yscale)
                bbox = aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y
                internal_boh_bboxes.append(bbox); placed_bboxes.append(bbox)
                return True
            return False

        # Zone 1: Storage (Top Wall) -> Rotated 180 + HORIZONTAL FLIP
        cursor_x = zone_bounds[2] - margin - sim_amenity_depth - gap
        for fxtr in sorted(storage_fixtures, key=lambda f: f.width, reverse=True):
            target_center = Vec2(cursor_x - fxtr.width / 2, zone_bounds[3] - margin - fxtr.height / 2)
            if _place_boh_fixture(fxtr, target_center, rotation_deg=180, xscale=-1.0):
                cursor_x -= (fxtr.width + gap)

        # Zone 2: Workstations (Bottom Wall) -> NO FLIP
        cursor_x = zone_bounds[0] + margin
        for fxtr in sorted(workstation_fixtures, key=lambda f: f.width, reverse=True):
            target_center = Vec2(cursor_x + fxtr.width / 2, zone_bounds[1] + margin + fxtr.height / 2)
            if _place_boh_fixture(fxtr, target_center):
                cursor_x += (fxtr.width + gap)
                
        # Zone 3: Amenities (Right Wall) -> Rotated 90 + HORIZONTAL FLIP
        cursor_y = zone_bounds[3] - margin
        for fxtr in sorted(amenity_fixtures, key=lambda f: f.height, reverse=True):
            rotated_w, rotated_h = fxtr.height, fxtr.width
            target_center = Vec2(zone_bounds[2] - margin - rotated_w / 2, cursor_y - rotated_h / 2)
            if _place_boh_fixture(fxtr, target_center, rotation_deg=90, xscale=-1.0):
                cursor_y -= (rotated_h + gap)
                
        print("✅ Finished BOH placement in the optimal top corner.")

    def place_clinics_at_top(self, placed_bboxes: list):
        """
        Primary strategy for placing clinics. Places them in an organized
        row or double row along the top wall of the floorplan.
        """
        # from Fixture import Fixture
        import collections

        print("\n--- 🏥 Placing Clinics at Top Wall ---")
        clinic_config = self.fixtures.get("clinic_fixtures", {})
        if not any(clinic_config.values()):
            print("  -> INFO: No clinic fixtures specified.")
            return

        clinics_to_place = []
        for clinic_type, count in clinic_config.items():
            if count > 0:
                fxtr = Fixture.Fixture(self.fixture_dict[clinic_type]["name"], self.fixture_dict[clinic_type]["path"])
                clinics_to_place.extend([fxtr] * count)

        remaining_clinics = self.place_clinics_along_top_wall(clinics_to_place, placed_bboxes)

        if not remaining_clinics:
            print("✅ All clinics placed successfully along the top wall.")
        else:
            print(f"⚠️ {len(remaining_clinics)} clinics could not be placed along the top wall.")
        # Zone 2 & 3 (Workstations and Amenities) can be placed similarly on other walls
        # This simplified version prioritizes getting storage packed correctly.
        # Add logic for other zones here if needed, following the same pattern.

#------------new  strategy for Back-of-House (BOH) fixtures------------------------------
#------------new  strategy for Back-of-House (BOH) fixtures------------------------------




    def _get_transformed_preset_poly(self, fxtr: 'Fixture', target_center: 'Vec2', rotation_deg: float, xscale: float = 1.0) -> 'Polygon':
        """Helper to get the transformed shapely Polygon for a preset given placement parameters."""
        from shapely.geometry import Polygon
        from ezdxf.math import Matrix44
        
        local_center = fxtr.bounding_box.center
        transform = Matrix44.chain(
            Matrix44.translate(-local_center.x, -local_center.y, 0),
            Matrix44.scale(xscale, 1.0, 1.0),
            Matrix44.z_rotate(math.radians(rotation_deg)),
            Matrix44.translate(target_center.x, target_center.y, 0)
        )
        world_corners = list(transform.transform_vertices(fxtr.bounding_box.rect_vertices()))
        return Polygon([(p.x, p.y) for p in world_corners])

    def place_boh_preset(self, placed_bboxes):
        """
        Finds the absolute best BOH preset and its placement using a dynamic
        "Top 40% Perimeter Walk" strategy, mirroring the logic of place_clinic.
        """
        # from Fixture import Fixture
        from shapely.geometry import box, Point
        from ezdxf.math import Vec2
        import math

        print("\n--- 🧠 Placing BOH Preset with 'Top 40% Perimeter Walk' Strategy ---")

        # 1. PRESET PRIORITY ORDER
        preset_priority_order = [
            # "medium_basic_boh",
            # "basic_boh_preset_1",
            "boh_vertical_horizontal_preset_basic"
            "small_basic_boh",
            "medium_basic_boh",
        ]
        preset_config = self.fixtures.get("boh_presets", {})
        available_presets = [p for p in preset_priority_order if p in preset_config]

        if not available_presets:
            print("  -> SKIPPED: No BOH presets found in the configuration.")
            print("  -> 🔄 EXECUTING FALLBACK...")
            self.place_boh_intelligently_n(placed_bboxes)
            return

        # 2. SETUP
        best_candidate = {"score": -1, "name": "None"}

        # 3. GET AND FILTER WALLS FOR THE TOP 40% ZONE
        y_threshold = self.cvc.min_y + (self.cvc.max_y - self.cvc.min_y) * 0.80
        ordered_corners = self._get_reordered_corners_top_left()
        
        perimeter_path = []
        for i in range(len(ordered_corners)):
            p1 = Vec2(ordered_corners[i])
            p2 = Vec2(ordered_corners[(i + 1) % len(ordered_corners)])
            if p1.distance(p2) > 100: perimeter_path.append((p1, p2))
        
        top_zone_segments = [seg for seg in perimeter_path if (seg[0].y + seg[1].y) / 2 >= y_threshold]
        print(f"  -> Identified {len(top_zone_segments)} wall segments in the top 40% of the floorplan.")
        
        # 4. MASTER ANALYSIS LOOP
        for preset_name in available_presets:
            print(f"\n  -> Analyzing options for preset: '{preset_name}'...")
            try:
                preset_fxtr = Fixture.Fixture(preset_name, self.fixture_dict[preset_name]["path"])
            except Exception as e:
                print(f"    -> 🔥 Could not load fixture file. Skipping. Error: {e}")
                continue

            for segment_start, segment_end in top_zone_segments:
                segment_vector = (segment_end - segment_start).normalize()
                segment_length = segment_start.distance(segment_end)
                inward_normal = segment_vector.orthogonal()
                if not self.floorplan_polygon.contains(Point(segment_start + (segment_vector * 10) + inward_normal)):
                    inward_normal = -inward_normal

                cursor = 50.0
                while cursor + preset_fxtr.width < segment_length - 50.0:
                    rotation_deg = math.degrees(segment_vector.angle)
                    
                    # --- Determine Wall Type and Mirroring (same as place_clinic) ---
                    mid_x, mid_y = (segment_start.x + segment_end.x) / 2, (segment_start.y + segment_end.y) / 2
                    centroid = self.floorplan_polygon.centroid
                    norm_angle = abs(rotation_deg) % 180
                    is_vertical = (75 < norm_angle < 105)
                    wall_type = "top" if (not is_vertical and mid_y > centroid.y) else "other"
                    if is_vertical: wall_type = "left" if mid_x < centroid.x else "right"
                    x_scale = -1.0 if wall_type in ['left', 'right'] else 1.0

                    # --- Calculate Candidate Position & Polygon ---
                    fixture_footprint = preset_fxtr.width if x_scale == 1.0 else preset_fxtr.width
                    center_on_wall = segment_start + segment_vector * (cursor + fixture_footprint / 2)
                    center_offset = inward_normal * (50.0 + preset_fxtr.height / 2) # 50mm margin from wall
                    target_center = center_on_wall + center_offset
                    candidate_poly = self._get_transformed_preset_poly(preset_fxtr, target_center, rotation_deg, x_scale)

                    # --- CORE VALIDATION AND SCORING ---
                    if any(candidate_poly.intersects(box(*b)) for b in placed_bboxes):
                        cursor += 100; continue
                    
                    fit_score = self.floorplan_polygon.intersection(candidate_poly).area / candidate_poly.area
                    if fit_score < 0.98: # Must be a near-perfect fit against the wall
                        cursor += 100; continue

                    remaining_retail = self.floorplan_polygon.difference(candidate_poly)
                    flow_score = 0
                    if not remaining_retail.is_empty:
                        flow_score = remaining_retail.area / remaining_retail.convex_hull.area
                    
                    total_score = (fit_score * 0.6) + (flow_score * 0.4)

                    if total_score > best_candidate["score"]:
                        best_candidate = {
                            "score": total_score,
                            "name": f"'{preset_name}' on '{wall_type}' wall", "fixture_obj": preset_fxtr,
                            "target_center": target_center, "rotation": rotation_deg,
                            "xscale": x_scale, "bounds": candidate_poly.bounds
                        }
                    cursor += 100.0

        # 5. PLACE THE BEST OPTION OR EXECUTE FALLBACK
        if best_candidate["score"] > 0.5:
            print(f"\n  -> ✅ Best Option Found: {best_candidate['name']} with score {best_candidate['score']:.2f}")
            
            # Recalculate the final insertion point for placement
            fxtr, center, rot, xscale = best_candidate["fixture_obj"], best_candidate["target_center"], best_candidate["rotation"], best_candidate["xscale"]
            local_center_scaled = Vec2(fxtr.bounding_box.center.x * xscale, fxtr.bounding_box.center.y)
            rotated_offset = local_center_scaled.rotate(math.radians(rot))
            final_insert_point = center - rotated_offset

            self.place_fixture(
                fxtr, (final_insert_point.x, final_insert_point.y, 0),
                rot, True, xscale=xscale
            )
            placed_bboxes.append(best_candidate["bounds"])
            print("  -> Best BOH Preset placed and registered as an obstacle.")
        else:
            print("\n  -> ⚠️ FAILED: Could not find a suitable location for ANY BOH preset.")
            print("  -> 🔄 EXECUTING FALLBACK...")
            self.place_boh_intelligently(placed_bboxes)

#----NEW-BOH-PLACEMENT-STRATEGY-BOH-AREA----
#----NEW-BOH-PLACEMENT-STRATEGY-BOH-AREA----

    def place_boh_fixtures_in_room(self, placed_bboxes: List[tuple]):
        """
        [PERFECTED V11 - INNER WALL] Places fixtures against the BOH room's INNER wall.
        - Uses vertical mirroring for placement calculations and double mirror for drawing.
        - Includes a 10mm gap from the wall.
        """
        from shapely.geometry import Polygon, Point, LineString
        from ezdxf.math import Vec2, BoundingBox2d, Matrix44
        import collections
        import math

        print("\n--- 🛋️  Placing BOH Fixtures (Inner Wall Logic + Hybrid Mirror) ---")

        # 1. FIND THE BOH PLACEMENT ZONE
        boh_outlines = list(self.msp.query('LWPOLYLINE[layer=="BOH_WALL_VALID_OUTLINE"]'))
        if not boh_outlines:
            boh_outlines = list(self.msp.query('LWPOLYLINE[layer=="BOH_PARTITION_OUTLINE"]'))
            if not boh_outlines:
                print("  -> SKIPPED: No valid BOH room outline was found to place fixtures in.")
                return

        polygons = [Polygon(list(p.get_points('xy'))) for p in boh_outlines]
        if not polygons: return
        
        # ***** CHANGE IS HERE: Use min() to select the inner boundary *****
        if len(polygons) > 1:
            boh_placement_zone = min(polygons, key=lambda p: p.area)
            print("  -> Found multiple BOH boundaries. Selecting INNER wall for placement.")
        else:
            boh_placement_zone = polygons[0]
        # ***************************************************************
        
        # 2. LOAD BOH FIXTURES (Unchanged)
        boh_config = self.fixtures.get("boh_fixtures", {})
        fixtures_to_place = []
        for name, count in boh_config.items():
            if count > 0:
                try:
                    fxtr = Fixture.Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"])
                    fixtures_to_place.extend([fxtr] * count)
                except (KeyError, ValueError): continue
        
        if not fixtures_to_place:
            print("  -> SKIPPED: No BOH fixtures specified in config.")
            return
                
        fixture_queue = collections.deque(fixtures_to_place)
        internal_boh_bboxes = []

        # 3. --- PHASE 1: "WALL-HUGGING" PLACEMENT ---
        print("  -> Phase 1: Placing fixtures with 10mm gap from perimeter walls...")
        placement_cursors = {}
        perimeter_path = []
        perimeter_coords = list(boh_placement_zone.exterior.coords)
        for i in range(len(perimeter_coords) - 1):
            p1, p2 = Vec2(perimeter_coords[i]), Vec2(perimeter_coords[i+1])
            if p1.distance(p2) > 100:
                perimeter_path.append((p1, p2))
                placement_cursors[i] = 50.0
        
        unplaced_after_walk = collections.deque()
        while fixture_queue:
            fixture_to_try = fixture_queue.popleft()
            placed_this_fixture = False

            for i, (segment_start, segment_end) in enumerate(perimeter_path):
                segment_vector = (segment_end - segment_start).normalize()
                segment_length = segment_start.distance(segment_end)
                wall_angle_deg = math.degrees(segment_vector.angle)
                
                inward_normal = segment_vector.orthogonal(ccw=False)
                test_point = segment_start + (segment_vector * 10) + inward_normal
                if not boh_placement_zone.contains(Point(test_point.x, test_point.y)):
                    inward_normal = segment_vector.orthogonal(ccw=True)

                cursor = placement_cursors.get(i, 50.0)
                
                if cursor + fixture_to_try.width <= segment_length - 50.0:
                    center_on_wall = segment_start + segment_vector * (cursor + fixture_to_try.width / 2)
                    target_center = center_on_wall + inward_normal * (10.0 + fixture_to_try.height / 2)
                    
                    validation_transform = Matrix44.chain(
                        Matrix44.translate(-fixture_to_try.bounding_box.center.x, -fixture_to_try.bounding_box.center.y, 0),
                        Matrix44.scale(1.0, -1.0, 1.0),
                        Matrix44.z_rotate(math.radians(wall_angle_deg)),
                        Matrix44.translate(target_center.x, target_center.y, 0)
                    )
                    
                    world_corners = list(validation_transform.transform_vertices(fixture_to_try.bounding_box.rect_vertices()))
                    fixture_polygon = Polygon([(p.x, p.y) for p in world_corners])
                    aabb = BoundingBox2d(world_corners)

                    is_inside = boh_placement_zone.contains(fixture_polygon.buffer(-1.0))
                    is_overlapping = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                    if is_inside and not is_overlapping:
                        local_center_scaled = Vec2(fixture_to_try.bounding_box.center.x * -1.0, fixture_to_try.bounding_box.center.y * -1.0)
                        rotated_offset = local_center_scaled.rotate(math.radians(wall_angle_deg))
                        final_insert_point = target_center - rotated_offset
                        self.place_fixture(fixture_to_try, (final_insert_point.x, final_insert_point.y, 0), wall_angle_deg, True, xscale=-1.0, yscale=-1.0)
                        
                        bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)
                        placed_bboxes.append(bbox_tuple)
                        internal_boh_bboxes.append(bbox_tuple)
                        
                        placement_cursors[i] = cursor + fixture_to_try.width

                        placed_this_fixture = True
                        print(f"    -> Placed '{fixture_to_try.name}' on wall.")
                        break
            
            if not placed_this_fixture:
                unplaced_after_walk.append(fixture_to_try)

        # 4. --- PHASE 2: INTELLIGENT GRID SEARCH FALLBACK (Unchanged) ---
        if unplaced_after_walk:
            print(f"\n  -> Phase 2: Starting Intelligent Grid Search for {len(unplaced_after_walk)} items...")

            fallback_queue = collections.deque(sorted(unplaced_after_walk, key=lambda f: f.width * f.height, reverse=True))
            zone_bounds = boh_placement_zone.bounds
            min_x, min_y, max_x, max_y = zone_bounds
            step = 100.0

            boh_segments = []
            for p1_vec, p2_vec in perimeter_path:
                boh_segments.append((LineString([(p1_vec.x, p1_vec.y), (p2_vec.x, p2_vec.y)]), p1_vec, p2_vec))

            still_unplaced = collections.deque()
            while fallback_queue:
                fixture_to_place = fallback_queue.popleft()
                placed_in_fallback = False

                for y_try in range(int(max_y - fixture_to_place.height), int(min_y), -int(step)):
                    for x_try in range(int(min_x), int(max_x - fixture_to_place.width), int(step)):
                        
                        target_center = Vec2(x_try + fixture_to_place.width / 2, y_try + fixture_to_place.height / 2)
                        
                        rotation_deg = 0.0
                        if boh_segments:
                            nearest_seg_data = min(boh_segments, key=lambda s: s[0].distance(Point(target_center.x, target_center.y)))
                            p1_vec, p2_vec = nearest_seg_data[1], nearest_seg_data[2]
                            wall_vec = (p2_vec - p1_vec).normalize()
                            rotation_deg = math.degrees(wall_vec.angle)

                        validation_transform = Matrix44.chain(
                            Matrix44.translate(-fixture_to_place.bounding_box.center.x, -fixture_to_place.bounding_box.center.y, 0),
                            Matrix44.scale(1.0, -1.0, 1.0),
                            Matrix44.z_rotate(math.radians(rotation_deg)),
                            Matrix44.translate(target_center.x, target_center.y, 0)
                        )
                        
                        world_corners = list(validation_transform.transform_vertices(fixture_to_place.bounding_box.rect_vertices()))
                        fixture_polygon = Polygon([(p.x, p.y) for p in world_corners])
                        aabb = BoundingBox2d(world_corners)

                        is_inside = boh_placement_zone.contains(fixture_polygon.buffer(-1.0))
                        is_overlapping = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                        if is_inside and not is_overlapping:
                            local_center_scaled = Vec2(fixture_to_place.bounding_box.center.x * -1.0, fixture_to_place.bounding_box.center.y * -1.0)
                            rotated_offset = local_center_scaled.rotate(math.radians(rotation_deg))
                            final_insert_point = target_center - rotated_offset
                            self.place_fixture(fixture_to_place, (final_insert_point.x, final_insert_point.y, 0), rotation_deg, True, xscale=-1.0, yscale=-1.0)
                            
                            bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)
                            placed_bboxes.append(bbox_tuple)
                            internal_boh_bboxes.append(bbox_tuple)
                            
                            print(f"    -> Placed '{fixture_to_place.name}' in open space (rotated {rotation_deg:.0f}° to match wall).")
                            placed_in_fallback = True
                            break
                    if placed_in_fallback:
                        break
                
                if not placed_in_fallback:
                    still_unplaced.append(fixture_to_place)

            # 5. FINAL REPORT
            if still_unplaced:
                print(f"\n  -> ⚠️  Finished. Could not place all BOH fixtures. {len(still_unplaced)} items remain.")
            else:
                print("\n  -> ✅ Finished. All BOH fixtures were placed successfully.")
        else:
             print("\n  -> ✅ Finished. All BOH fixtures were placed successfully during Phase 1.")

    
    



    def place_boh_fixtures_in_room_og(self, placed_bboxes: List[tuple]):
        """
        [MODIFIED] Finds the created BOH room and furnishes it using a two-phase strategy.
        - It now correctly checks against ALL previously placed fixtures (including the pickup_table)
          to prevent overlaps.
        """
        # from Fixture import Fixture
        from shapely.geometry import Polygon, Point
        from ezdxf.math import Vec2, BoundingBox2d, Matrix44
        import collections
        import math

        print("\n--- 🛋️  Placing BOH Fixtures Inside BOH Room ---")

        # 1. FIND THE BOH PLACEMENT ZONE (Unchanged)
        boh_outlines = list(self.msp.query('LWPOLYLINE[layer=="BOH_WALL_VALID_OUTLINE"]'))
        if not boh_outlines:
            print("  -> SKIPPED: No valid BOH room was created to place fixtures in.")
            return

        polygons = [Polygon(list(p.get_points('xy'))) for p in boh_outlines]
        if not polygons: return
        boh_placement_zone = min(polygons, key=lambda p: p.area)
        
        # 2. LOAD BOH FIXTURES (Unchanged)
        boh_config = self.fixtures.get("boh_fixtures", {})
        fixtures_to_place = []
        for name, count in boh_config.items():
            if count > 0:
                try:
                    fxtr = Fixture.Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"])
                    fixtures_to_place.extend([fxtr] * count)
                except (KeyError, ValueError): continue
        
        if not fixtures_to_place:
            print("  -> SKIPPED: No BOH fixtures specified in config.")
            return
                
        fixture_queue = collections.deque(fixtures_to_place)

        # 3. --- PHASE 1: "WALK THE WALL" PLACEMENT ---
        print("  -> Phase 1: Placing fixtures along perimeter...")
        internal_boh_bboxes = [] # This list will still track fixtures placed *inside* this function
        placement_cursors = {i: 50.0 for i in range(len(list(boh_placement_zone.exterior.coords)))}
        perimeter_path = []
        perimeter_coords = list(boh_placement_zone.exterior.coords)
        for i in range(len(perimeter_coords) - 1):
            p1, p2 = Vec2(perimeter_coords[i]), Vec2(perimeter_coords[i+1])
            if p1.distance(p2) > 100: perimeter_path.append((p1, p2))
        
        unplaced_after_walk = collections.deque()
        while fixture_queue:
            fixture_to_try = fixture_queue.popleft()
            placed_this_fixture = False

            for i, (segment_start, segment_end) in enumerate(perimeter_path):
                segment_vector = (segment_end - segment_start).normalize()
                segment_length = segment_start.distance(segment_end)
                wall_angle_deg = math.degrees(segment_vector.angle)
                inward_normal = segment_vector.orthogonal(ccw=False)
                cursor = placement_cursors.get(i, 50.0)
                
                if cursor + fixture_to_try.width <= segment_length - 50.0:
                    center_on_wall = segment_start + segment_vector * (cursor + fixture_to_try.width / 2)
                    target_center = center_on_wall + inward_normal * (50.0 + fixture_to_try.height / 2)
                    
                    local_center = fixture_to_try.bounding_box.center
                    transform = Matrix44.chain(
                        Matrix44.translate(-local_center.x, -local_center.y, 0),
                        Matrix44.scale(-1.0, -1.0, 1.0),
                        Matrix44.z_rotate(math.radians(wall_angle_deg)),
                        Matrix44.translate(target_center.x, target_center.y, 0)
                    )
                    world_corners = list(transform.transform_vertices(fixture_to_try.bounding_box.rect_vertices()))
                    fixture_polygon = Polygon([(p.x, p.y) for p in world_corners])
                    aabb = BoundingBox2d(world_corners)
                    is_inside = boh_placement_zone.contains(fixture_polygon.buffer(-1.0))
                    
                    # ******************** MODIFICATION 1 ********************
                    # This now checks against the main 'placed_bboxes' list passed into the function.
                    is_overlapping = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)
                    # ********************************************************

                    if is_inside and not is_overlapping:
                        local_center_scaled = Vec2(local_center.x * -1.0, local_center.y * -1.0)
                        rotated_offset = local_center_scaled.rotate(math.radians(wall_angle_deg))
                        final_insert_point = target_center - rotated_offset
                        self.place_fixture(fixture_to_try, (final_insert_point.x, final_insert_point.y, 0), wall_angle_deg, True, xscale=-1.0, yscale=-1.0)
                        bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)
                        placed_bboxes.append(bbox_tuple) # Add to the main list
                        internal_boh_bboxes.append(bbox_tuple) # Also add to the internal list
                        placement_cursors[i] = cursor + fixture_to_try.width
                        placed_this_fixture = True
                        print(f"    -> Placed '{fixture_to_try.name}' on wall (Mirrored H & V).")
                        break
            
            if not placed_this_fixture:
                unplaced_after_walk.append(fixture_to_try)

        # 4. --- PHASE 2: FALLBACK GRID SEARCH ---
        if unplaced_after_walk:
            print(f"\n  -> Phase 2: Starting Fallback Grid Search for {len(unplaced_after_walk)} items...")

            fallback_queue = collections.deque(sorted(unplaced_after_walk, key=lambda f: f.width * f.height, reverse=True))
            zone_bounds = boh_placement_zone.bounds
            min_x, min_y, max_x, max_y = zone_bounds
            step = 100.0

            still_unplaced = collections.deque()
            # PRECOMPUTE BOH EXTERIOR SEGMENTS FOR ALIGNMENT
            boh_exterior_coords = list(boh_placement_zone.exterior.coords)
            boh_segments = []
            for i in range(len(boh_exterior_coords) - 1):
                p1 = boh_exterior_coords[i]
                p2 = boh_exterior_coords[i + 1]
                seg = LineString([p1, p2])
                boh_segments.append((seg, Vec2(p1), Vec2(p2)))

            while fallback_queue:
                fixture_to_place = fallback_queue.popleft()
                placed_in_fallback = False

                # iterate top-down so we attempt more valuable (higher) locations first
                for y_try in range(int(max_y - fixture_to_place.height), int(min_y), -int(step)):
                    for x_try in range(int(min_x), int(max_x - fixture_to_place.width), int(step)):

                        # compute candidate center
                        target_center = Vec2(x_try + fixture_to_place.width / 2, y_try + fixture_to_place.height / 2)
                        # find nearest BOH exterior segment to align with
                        nearest_seg = None
                        nearest_dist = float('inf')
                        nearest_angle_deg = 0.0
                        for seg, p1_vec, p2_vec in boh_segments:
                            d = seg.distance(Point(target_center.x, target_center.y))
                            if d < nearest_dist:
                                nearest_dist = d
                                nearest_seg = (p1_vec, p2_vec)
                        if nearest_seg:
                            p1_vec, p2_vec = nearest_seg
                            wall_vec = (p2_vec - p1_vec)
                            if wall_vec.magnitude == 0:
                                nearest_angle_deg = 0.0
                            else:
                                nearest_angle_deg = math.degrees(wall_vec.normalize().angle)
                        else:
                            nearest_angle_deg = 0.0

                        # Build transform: apply same mirroring as previous code but rotate to wall direction
                        local_center = fixture_to_place.bounding_box.center
                        transform = Matrix44.chain(
                            Matrix44.translate(-local_center.x, -local_center.y, 0),
                            Matrix44.scale(-1.0, -1.0, 1.0),
                            Matrix44.z_rotate(math.radians(nearest_angle_deg)),
                            Matrix44.translate(target_center.x, target_center.y, 0)
                        )
                        world_corners = list(transform.transform_vertices(fixture_to_place.bounding_box.rect_vertices()))
                        fixture_polygon = Polygon([(p.x, p.y) for p in world_corners])
                        aabb = BoundingBox2d(world_corners)

                        is_inside = boh_placement_zone.contains(fixture_polygon.buffer(-1.0))
                        is_overlapping = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                        if is_inside and not is_overlapping:
                            # calculate final insertion point compatible with place_fixture expectations
                            local_center_scaled = Vec2(local_center.x * -1.0, local_center.y * -1.0)
                            rotated_offset = local_center_scaled.rotate(math.radians(nearest_angle_deg))
                            final_insert_point = target_center - rotated_offset

                            # place with rotation parallel to BOH boundary
                            self.place_fixture(fixture_to_place, (final_insert_point.x, final_insert_point.y, 0), nearest_angle_deg, True, xscale=-1.0, yscale=-1.0)

                            bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)
                            placed_bboxes.append(bbox_tuple)  # Add to master list
                            internal_boh_bboxes.append(bbox_tuple)
                            print(f"    -> Placed '{fixture_to_place.name}' rotated {nearest_angle_deg:.1f}° in fallback at ({x_try:.0f},{y_try:.0f}).")
                            placed_in_fallback = True
                            break
                    if placed_in_fallback:
                        break

                if not placed_in_fallback:
                    still_unplaced.append(fixture_to_place)

            # 5. FINAL REPORT
            if still_unplaced:
                print(f"\n  -> ⚠️  Finished. Could not place all BOH fixtures. {len(still_unplaced)} items remain.")
            else:
                print("\n  -> ✅ Finished. All BOH fixtures were placed successfully.")


        # # 4. --- PHASE 2: FALLBACK GRID SEARCH ---
        # if unplaced_after_walk:
        #     print(f"\n  -> Phase 2: Starting Fallback Grid Search for {len(unplaced_after_walk)} items...")
            
        #     fallback_queue = collections.deque(sorted(unplaced_after_walk, key=lambda f: f.width * f.height, reverse=True))
        #     zone_bounds = boh_placement_zone.bounds
        #     min_x, min_y, max_x, max_y = zone_bounds
        #     step = 100.0

        #     still_unplaced = collections.deque()
        #     while fallback_queue:
        #         fixture_to_place = fallback_queue.popleft()
        #         placed_in_fallback = False

        #         for y_try in range(int(max_y - fixture_to_place.height), int(min_y), -int(step)):
        #             for x_try in range(int(min_x), int(max_x - fixture_to_place.width), int(step)):
                        
        #                 target_center = Vec2(x_try + fixture_to_place.width / 2, y_try + fixture_to_place.height / 2)
                        
        #                 local_center = fixture_to_place.bounding_box.center
        #                 transform = Matrix44.chain(
        #                     Matrix44.translate(-local_center.x, -local_center.y, 0),
        #                     Matrix44.scale(-1.0, -1.0, 1.0),
        #                     Matrix44.z_rotate(math.radians(0)),
        #                     Matrix44.translate(target_center.x, target_center.y, 0)
        #                 )
        #                 world_corners = list(transform.transform_vertices(fixture_to_place.bounding_box.rect_vertices()))
        #                 fixture_polygon = Polygon([(p.x, p.y) for p in world_corners])
        #                 aabb = BoundingBox2d(world_corners)

        #                 is_inside = boh_placement_zone.contains(fixture_polygon.buffer(-1.0))

        #                 # ******************** MODIFICATION 2 ********************
        #                 # This also now checks against the main 'placed_bboxes' list.
        #                 is_overlapping = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)
        #                 # ********************************************************

        #                 if is_inside and not is_overlapping:
        #                     local_center_scaled = Vec2(local_center.x * -1.0, local_center.y * -1.0)
        #                     final_insert_point = target_center - local_center_scaled
        #                     self.place_fixture(fixture_to_place, (final_insert_point.x, final_insert_point.y, 0), 0, True, xscale=-1.0, yscale=-1.0)
                            
        #                     bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)
        #                     placed_bboxes.append(bbox_tuple) # Add to the main list
        #                     internal_boh_bboxes.append(bbox_tuple) # Also add to the internal list
                            
        #                     print(f"    -> Placed '{fixture_to_place.name}' in open space (Fallback).")
        #                     placed_in_fallback = True
        #                     break
        #             if placed_in_fallback:
        #                 break
                
        #         if not placed_in_fallback:
        #             still_unplaced.append(fixture_to_place)

        #     # 5. FINAL REPORT
        #     if still_unplaced:
        #         print(f"\n  -> ⚠️  Finished. Could not place all BOH fixtures. {len(still_unplaced)} items remain.")
        #     else:
        #         print("\n  -> ✅ Finished. All BOH fixtures were placed successfully.")


    

    


#----NEW-BOH-PLACEMENT-STRATEGY-BOH-AREA----
#----NEW-BOH-PLACEMENT-STRATEGY-BOH-AREA----
#---- BOH PLACEMENT FUNCTION FINISHED HERE ----


#--CATEGORY :- Seating (clinic/AR)

#----bench placement starting here------------------------------------------------------
#-------------------------------------new bench placement tesing------------------------------------------------------
#-------------------------------------new bench placement tesing------------------------------------------------------
#-------------------------------------new bench placement tesing------------------------------------------------------

    def _get_clinic_bboxes_new(self, buffer=50.0):
        """
        Gets the bounding boxes of all clinic fixtures with an optional safety buffer.
        This identifies "no-go zones" for other fixture placements.
        """
        clinic_bboxes = []
        # Find all placed fixtures whose block names contain "CLINIC".
        clinic_entities = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
        print(len(clinic_entities))
        for entity in clinic_entities:
            try:
                # Calculate the precise bounding box of the clinic.
                bbox = extents([entity], fast=True)
                if (bbox.extmax.x-bbox.extmin.x)*(bbox.extmax.y-bbox.extmin.y) < ((2600*1700)+ 1000):
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

    def place_benches_near_clinics_with_multiple_strategies(self, placed_bboxes):
        """
        Places benches using a smart, multi-strategy approach to ensure they are
        placed near clinics without overlapping other fixtures.
        """
        from shapely.geometry import box, Point
        from ezdxf.bbox import extents
        from ezdxf.math import BoundingBox2d, Vec2
        import collections

        print("\n--- 🧠 Placing Benches with Multiple Strategies (Near Clinics) ---")

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
        clinic_bboxes = self._get_clinic_bboxes_new(buffer=0)
        
        if not clinic_bboxes:
            print("⚠️ No clinic fixtures found to anchor bench placement.")
            return

        # --- STRATEGY 1: Place vertically near clinics ---
        # remaining_benches = self._place_benches_vertically_near_clinics(remaining_benches, clinic_bboxes, placed_bboxes)
        if not remaining_benches:
            print("\n✅ All benches placed successfully using Strategy 1.")
            return

        # --- STRATEGY 2: Place on walls near clinics ---
        remaining_benches = self._place_benches_on_clinic_sides(remaining_benches, clinic_bboxes, placed_bboxes)
        if not remaining_benches:
            print("\n✅ All benches placed successfully using Strategies 1 & 2.")
            return

        # --- STRATEGY 3: Try all 4 sides of every clinic ---
        # remaining_benches = self._place_benches_on_clinic_sides(remaining_benches, clinic_bboxes, placed_bboxes)
        remaining_benches = self._place_benches_on_nearby_walls(remaining_benches, clinic_bboxes, placed_bboxes)
        
        # FINAL REPORT
        placed_count = len(benches_to_place) - len(remaining_benches)
        print(f"\n-> Intelligent Placement Complete: Placed {placed_count} of {len(benches_to_place)} benches.")
        if remaining_benches:
            print(f"⚠️ Could not find a suitable location for {len(remaining_benches)} benches after all strategies.")

    def _place_benches_vertically_near_clinics(self, benches_to_place_queue, clinic_bboxes, placed_bboxes):
        """
        Helper for Strategy 1: Places benches vertically near clinics.
        """
        from shapely.geometry import box
        from ezdxf.math import BoundingBox2d
        
        print("\n  -> Strategy 1: Attempting to place benches VERTICALLY near clinics...")
        remaining_benches = collections.deque()
        sorted_clinics = sorted(clinic_bboxes, key=lambda b: b[0])
        
        while benches_to_place_queue:
            bench = benches_to_place_queue.popleft()
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
                remaining_benches.append(bench)
        
        return remaining_benches
    
    def _place_benches_on_nearby_walls(self, benches_to_place_queue, clinic_bboxes, placed_bboxes):
        """
        Helper for Strategy 2: Places benches on walls near clinics.
        """
        from shapely.geometry import box, Point
        from ezdxf.bbox import extents
        
        print(f"\n  -> Strategy 2: Attempting to place {len(benches_to_place_queue)} benches on walls near clinics...")
        remaining_benches = collections.deque()
        
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

        while benches_to_place_queue:
            bench = benches_to_place_queue.popleft()
            is_placed = False
            for wall_data in prioritized_walls:
                if self._validate_and_place_on_segment_wall_new(bench, wall_data['segment'], placed_bboxes):
                    print(f"    ✅ SUCCESS: Placed '{bench.name}' on a wall near a clinic.")
                    is_placed = True
                    break
            if not is_placed:
                remaining_benches.append(bench)
        
        return remaining_benches

    def _place_benches_on_clinic_sides(self, benches_to_place_queue, clinic_bboxes, placed_bboxes):
        """
        Helper for Strategy 3: Places benches on all four sides of every clinic as a fallback.
        """
        from shapely.geometry import box
        from ezdxf.math import BoundingBox2d, Vec2
        
        print(f"\n  -> Strategy 3 (Fallback): Searching all sides of all clinics for {len(benches_to_place_queue)} benches...")
        remaining_benches = collections.deque()
        sorted_clinics = sorted(clinic_bboxes, key=lambda b: b[0])
        
        while benches_to_place_queue:
            bench = benches_to_place_queue.popleft()
            is_placed = False
            
            for bbox in sorted_clinics:
                clinic_bbox = BoundingBox2d([(bbox[0], bbox[1]), (bbox[2], bbox[3])])
                aisle_gap = 150.0

                spots_to_try = [
                    {"side": "top", "rot": 0, "w": bench.width, "h": bench.height, 
                     "x": clinic_bbox.center.x - (bench.width / 2), 
                     "y": clinic_bbox.extmax.y + aisle_gap},
                    {"side": "bottom", "rot": 0, "w": bench.width, "h": bench.height, 
                     "x": clinic_bbox.center.x - (bench.width / 2), 
                     "y": clinic_bbox.extmin.y - aisle_gap - bench.height},
                    # {"side": "left", "rot": 90, "w": bench.height, "h": bench.width, 
                    #  "x": clinic_bbox.extmin.x - aisle_gap - bench.height, 
                    #  "y": clinic_bbox.center.y - (bench.width / 2)},
                    # {"side": "right", "rot": 90, "w": bench.height, "h": bench.width, 
                    #  "x": clinic_bbox.extmax.x + aisle_gap, 
                    #  "y": clinic_bbox.center.y - (bench.width / 2)}
                ]

                for spot in spots_to_try:
                    print(spot)
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
                remaining_benches.append(bench)
    
        return remaining_benches

#----new bench placement starting here------------------------------------------------------
    #----new bench placement starting here------------------------------------------------------

    def place_benches_under_separation_line_left(self, placed_bboxes: List[tuple]):
            """
            Places benches in a row on the left side, parallel to and 10mm below
            the 'RETAIL_SEPARATOR' line.
            """
            from shapely.geometry import box
            print("\n--- 🛋️  Placing Benches Under Separation Line (Left Side) ---")

            # --- 1. Load Fixtures ---
            try:
                bench_config = self.fixtures.get("Bench_fixtures", {})
                benches_to_place = [
                    Fixture.Fixture(name, self.fixture_dict[name]["path"])
                    # ***** MODIFICATION: This now ignores the 'AR' fixture *****
                    for name, count in bench_config.items() if count > 0 and name != "AR"
                    for _ in range(count)
                ]
                if not benches_to_place:
                    print("  -> SKIPPED: No bench fixtures specified for placement.")
                    return
            except Exception as e:
                print(f"  -> 🔥 ERROR loading bench fixtures: {e}")
                return

            # --- 2. Find the Separation Line ---
            separator_line = self.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
            if not separator_line:
                print("  -> ⚠️ FAILED: 'RETAIL_SEPARATOR' line not found. Cannot place benches.")
                return

            # --- 3. Placement Logic ---
            GAP_BELOW_LINE = 10.0
            GAP_FROM_WALL = 100.0
            GAP_BETWEEN_BENCHES = 150.0

            # Start placing from the left side of the separation line
            current_x = separator_line.dxf.start.x + GAP_FROM_WALL
            line_y = separator_line.dxf.start.y
            placed_count = 0

            for i, bench_fxtr in enumerate(benches_to_place):
                # Calculate the Y-coordinate for the bottom-left corner of the bench
                target_y = line_y - GAP_BELOW_LINE - bench_fxtr.height

                # Create a candidate box for validation
                candidate_box = box(current_x, target_y, current_x + bench_fxtr.width, target_y + bench_fxtr.height)

                # Check for overlaps and if it's inside the floorplan
                is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
                is_inside = self.floorplan_polygon.contains(candidate_box)

                if is_inside and not is_overlapping:
                    # If the spot is clear, place the fixture
                    self.place_fixture(bench_fxtr, (current_x, target_y, 0), rotation=0, rotated=False)
                    
                    # Add its bounding box to the list of obstacles
                    new_bbox = candidate_box.bounds
                    placed_bboxes.append(new_bbox)
                    
                    print(f"    ✅ Placed '{bench_fxtr.name}' #{i+1} at (x={current_x:.0f}, y={target_y:.0f})")
                    
                    # Move the cursor for the next bench
                    current_x += bench_fxtr.width + GAP_BETWEEN_BENCHES
                    placed_count += 1
                else:
                    print(f"    -> ⚠️ Spot for '{bench_fxtr.name}' #{i+1} was blocked. Trying next spot...")
                    # If the spot is blocked, just nudge the cursor slightly and try again on the next iteration
                    current_x += 100.0
            
            print(f"\n-> Finished: Placed {placed_count} of {len(benches_to_place)} benches.")

    def place_benches_under_separation_line_right(self, placed_bboxes: List[tuple]):
        """
        Places benches in a row on the right side, parallel to and 10mm below
        the 'RETAIL_SEPARATOR' line.
        """
        from shapely.geometry import box
        print("\n--- 🛋️  Placing Benches Under Separation Line (Right Side) ---")

        # --- 1. Load Fixtures ---
        try:
            bench_config = self.fixtures.get("Bench_fixtures", {})
            benches_to_place = [
                Fixture.Fixture(name, self.fixture_dict[name]["path"])
                for name, count in bench_config.items() if count > 0 and name != "AR"
                for _ in range(count)
            ]
            if not benches_to_place:
                print("  -> SKIPPED: No bench fixtures specified for placement.")
                return
        except Exception as e:
            print(f"  -> 🔥 ERROR loading bench fixtures: {e}")
            return

        # --- 2. Find the Separation Line ---
        separator_line = self.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
        if not separator_line:
            print("  -> ⚠️ FAILED: 'RETAIL_SEPARATOR' line not found. Cannot place benches.")
            return

        # --- 3. Placement Logic ---
        GAP_BELOW_LINE = 10.0
        GAP_FROM_WALL = 100.0
        GAP_BETWEEN_BENCHES = 150.0

        # Start placing from the right side of the separation line
        current_x = separator_line.dxf.end.x - GAP_FROM_WALL
        line_y = separator_line.dxf.end.y
        placed_count = 0

        for i, bench_fxtr in enumerate(benches_to_place):
            # Calculate the Y-coordinate for the bottom-right corner of the bench
            target_y = line_y - GAP_BELOW_LINE - bench_fxtr.height
            # Place benches from right to left
            x_pos = current_x - bench_fxtr.width

            candidate_box = box(x_pos, target_y, x_pos + bench_fxtr.width, target_y + bench_fxtr.height)
            is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
            is_inside = self.floorplan_polygon.contains(candidate_box)

            if is_inside and not is_overlapping:
                self.place_fixture(bench_fxtr, (x_pos, target_y, 0), rotation=0, rotated=False)
                new_bbox = candidate_box.bounds
                placed_bboxes.append(new_bbox)
                print(f"    ✅ Placed '{bench_fxtr.name}' #{i+1} at (x={x_pos:.0f}, y={target_y:.0f})")
                # Move the cursor for the next bench (to the left)
                current_x = x_pos - GAP_BETWEEN_BENCHES
                placed_count += 1
            else:
                print(f"    -> ⚠️ Spot for '{bench_fxtr.name}' #{i+1} was blocked. Trying next spot...")
                current_x = x_pos - 100.0

        print(f"\n-> Finished: Placed {placed_count} of {len(benches_to_place)} benches.")

    def place_benches(self, all_placed_bboxes: List[tuple]):
        """
        for placing benches using different strategies based on room detection.
        1. Detects if a back corner room exists and its location (left/right).
        """
        print("\n--- 🧭 Orchestrating Main Clinic Placement Strategy ---")

        # First, detect if a room exists in a back corner and get its location.
        back_room_location = self.detect_back_corner_room()
        self.back_room_location = back_room_location # Store the result

        # If a room is detected on the 'left'...
        if back_room_location == 'left':
            print("  -> Back-left room detected. Executing OPPOSITE (right-to-left) clinic placement strategy.")
            # ...call the opposite placement function.
            self.place_benches_under_separation_line_right(all_placed_bboxes)
            all_placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)

        else:
            self.place_benches_under_separation_line_left(all_placed_bboxes)
            all_placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
            


    def place_ar_under_separation_line(self, placed_bboxes: List[tuple]):
        """
        Places a single AR fixture on the right side with a 270-degree rotation,
        parallel to and 10mm below the 'RETAIL_SEPARATOR' line.
        """
        from shapely.geometry import box
        print("\n--- 🤖 Placing AR Fixture Under Separation Line (Right Side, Rotated 270°) ---")

        # --- 1. Load Fixture (Unchanged) ---
        try:
            ar_count = self.fixtures.get("Bench_fixtures", {}).get("AR", 0)
            if ar_count == 0:
                print("  -> SKIPPED: No 'AR' fixture specified in the configuration.")
                return
            ar_fxtr = Fixture.Fixture("AR", self.fixture_dict["AR"]["path"])
        except Exception as e:
            print(f"  -> 🔥 ERROR loading AR fixture: {e}")
            return

        # --- 2. Define Dimensions and Constants ---
        separator_line = self.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
        GAP_BELOW_LINE = 10.0
        GAP_FROM_WALL = 500.0

        # ***** KEY CHANGE: Define rotated dimensions *****
        rotated_width = ar_fxtr.height
        rotated_height = ar_fxtr.width

        # --- 3. Primary Placement Logic (Using the line) ---
        if separator_line:
            print("  -> Found 'RETAIL_SEPARATOR' line. Anchoring placement to it.")
            line_y = separator_line.dxf.start.y
            
            # Calculate Y-coordinate using the new rotated height
            target_y = line_y - GAP_BELOW_LINE - rotated_height
            
            # Calculate X-coordinate from the RIGHT side using the new rotated width
            target_x = separator_line.dxf.end.x - rotated_width - GAP_FROM_WALL
            
            # Create a candidate box with the new rotated dimensions
            candidate_box = box(target_x, target_y, target_x + rotated_width, target_y + rotated_height)

            is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
            is_inside = self.floorplan_polygon.contains(candidate_box)

            if is_inside and not is_overlapping:
                # ***** KEY CHANGE: Adjust insertion point and rotation *****
                # For 270 deg rotation, the insertion point needs to be the top-left corner
                # of the final bounding box.
                insert_point = (target_x, target_y + rotated_height, 0)
                self.place_fixture(ar_fxtr, insert_point, rotation=270, rotated=True)
                
                placed_bboxes.append(candidate_box.bounds)
                print(f"    ✅ Placed 'AR' fixture at (x={target_x:.0f}, y={target_y:.0f}) with 270° rotation.")
            else:
                print("    -> ⚠️ Primary spot for rotated AR fixture was blocked.")
        
        # --- 4. Fallback Logic (If line is not found) ---
        else:
            print("  -> ⚠️ FAILED: 'RETAIL_SEPARATOR' line not found. Attempting fallback.")
            
            fallback_x = self.cvc.max_x - rotated_width - GAP_FROM_WALL
            fallback_y = self.cvc.min_y + GAP_FROM_WALL

            candidate_box = box(fallback_x, fallback_y, fallback_x + rotated_width, fallback_y + rotated_height)
            is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
            is_inside = self.floorplan_polygon.contains(candidate_box)

            if is_inside and not is_overlapping:
                # ***** KEY CHANGE: Adjust insertion point and rotation for fallback *****
                insert_point = (fallback_x, fallback_y + rotated_height, 0)
                self.place_fixture(ar_fxtr, insert_point, rotation=270, rotated=True)
                
                placed_bboxes.append(candidate_box.bounds)
                print(f"    ✅ Placed 'AR' fixture via fallback at (x={fallback_x:.0f}, y={fallback_y:.0f}) with 270° rotation.")
            else:
                print("    -> ⚠️ Fallback spot was also blocked.")

    def place_ar_under_separation_line_(self, placed_bboxes: List[tuple]):
        """
        Places a single AR fixture on the right side, parallel to and 10mm below
        the 'RETAIL_SEPARATOR' line.
        Includes a fallback to the bottom-right corner if the line isn't found.
        """
        from shapely.geometry import box
        print("\n--- 🤖 Placing AR Fixture Under Separation Line (Right Side) ---")

        # --- 1. Load Fixture ---
        try:
            # Check for the AR fixture specifically
            ar_count = self.fixtures.get("Bench_fixtures", {}).get("AR", 0)
            if ar_count == 0:
                print("  -> SKIPPED: No 'AR' fixture specified in the configuration.")
                return
            ar_fxtr = Fixture.Fixture("AR", self.fixture_dict["AR"]["path"])
        except Exception as e:
            print(f"  -> 🔥 ERROR loading AR fixture: {e}")
            return

        # --- 2. Find the Separation Line ---
        separator_line = self.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
        
        # Define constants for placement
        GAP_BELOW_LINE = 10.0
        GAP_FROM_WALL = 100.0

        # --- 3. Primary Placement Logic (Using the line) ---
        if separator_line:
            print("  -> Found 'RETAIL_SEPARATOR' line. Anchoring placement to it.")
            line_y = separator_line.dxf.start.y
            
            # Calculate Y-coordinate (same for both strategies)
            target_y = line_y - GAP_BELOW_LINE - ar_fxtr.height
            
            # Calculate X-coordinate from the RIGHT side of the line
            target_x = separator_line.dxf.end.x - ar_fxtr.width - GAP_FROM_WALL
            
            # Create a candidate box for validation
            candidate_box = box(target_x, target_y, target_x + ar_fxtr.width, target_y + ar_fxtr.height)

            # Check for overlaps and if it's inside the floorplan
            is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
            is_inside = self.floorplan_polygon.contains(candidate_box)

            if is_inside and not is_overlapping:
                self.place_fixture(ar_fxtr, (target_x, target_y, 0), rotation=0, rotated=False)
                placed_bboxes.append(candidate_box.bounds)
                print(f"    ✅ Placed 'AR' fixture at (x={target_x:.0f}, y={target_y:.0f})")
            else:
                print("    -> ⚠️ Primary spot for AR fixture was blocked. No further attempts will be made for this strategy.")
        
        # --- 4. Fallback Logic (If line is not found) ---
        else:
            print("  -> ⚠️ FAILED: 'RETAIL_SEPARATOR' line not found. Attempting fallback to bottom-right corner.")
            
            fallback_x = self.cvc.max_x - ar_fxtr.width - GAP_FROM_WALL
            fallback_y = self.cvc.min_y + GAP_FROM_WALL

            candidate_box = box(fallback_x, fallback_y, fallback_x + ar_fxtr.width, fallback_y + ar_fxtr.height)
            is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
            is_inside = self.floorplan_polygon.contains(candidate_box)

            if is_inside and not is_overlapping:
                self.place_fixture(ar_fxtr, (fallback_x, fallback_y, 0), rotation=0, rotated=False)
                placed_bboxes.append(candidate_box.bounds)
                print(f"    ✅ Placed 'AR' fixture via fallback at (x={fallback_x:.0f}, y={fallback_y:.0f})")
            else:
                print("    -> ⚠️ Fallback spot in the bottom-right corner was also blocked.")


#----new bench placement starting here------------------------------------------------------
#----new bench placement starting here------------------------------------------------------

    #----bench placement finishing  here------------------------------------------------------
    #----bench placement finishing  here------------------------------------------------------
    #----bench placement finishing  here------------------------------------------------------
    #----bench placement finishing  here------------------------------------------------------



    def _validate_and_place_on_segment_wall_new(self, bench, segment, placed_bboxes, fixed_normal=None):
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
            if self._validate_and_place_at_point_new(bench, target_center_wcs, wall_angle_deg, placed_bboxes):
                return True
            search_distance += 100
        return False
        
    def _validate_and_place_at_point_new(self, fixture, target_center, angle_deg, placed_bboxes):
        """
        A robust helper to validate if a fixture can be placed at a specific
        center point with a given rotation, and places it if valid.
        Returns True on success, False on failure.
        """
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

#---CATEGORY :- Wall Fixtures/Euro Centers
#---- CENTRAL FLOOR FIXTURE (EURO_CENTER,LENSBAR) PLACEMENT FUNCTION STARTED ----

#---------------------new--setup-for-findong-area-for-euro-center-placement--
#---------------------new--setup-for-findong-area-for-euro-center-placement--


    from typing import Optional
    from shapely.geometry import Polygon, box
    from shapely.ops import unary_union
    from ezdxf.bbox import extents

    def euro_center_placement_area(self) -> Optional[Polygon]:
        """
        [MODIFIED V5] Calculates the Euro Center placement zone with differential bottom margins.
        - Facade Walls: Applies a 1850 mm keep-out zone from the absolute bottom segments.
        - Normal Bottom Walls: Applies a 1350 mm keep-out zone from other bottom segments.
        - Side/Top Walls: Uses standard logic (1350mm inset / standing table anchor).
        """
        from ezdxf.bbox import extents
        from shapely.geometry import box, LineString, MultiPolygon
        from shapely.ops import unary_union
        import math

        print("\n--- 📐 Defining Euro Center zone (with Differentiated Bottom Margins) ---")

        # --- 1. Define Top Boundary (Unchanged) ---
        st_entities = [e for e in self.msp.query('INSERT') if "STANDING_TABLE" in e.dxf.name.upper()]
        if not st_entities:
            print("  -> ⚠️ Could not find Standing Tables. Cannot create zone.")
            return None
        st_bbox = extents(st_entities)
        top_boundary_y = st_bbox.extmin.y - 950.0

         # --- 2. Inset the full floorplan polygon (Unchanged) ---
        simplification_tolerance = 50.0
        simplified_floorplan_polygon = self.floorplan_polygon.simplify(simplification_tolerance, preserve_topology=True)

        wall_fixture_depth = 300.0
        shopping_aisle_gap = 1050.0
        total_side_gap = wall_fixture_depth + shopping_aisle_gap
        
        inset_polygon = simplified_floorplan_polygon.buffer(-total_side_gap, join_style=2)
        print(f"  -> Inset the full floorplan polygon by {total_side_gap:.0f}mm from all walls.")

       ### --- START OF MODIFICATION: DYNAMIC BOTTOM BOUNDARY --- ###

        # --- 3. Identify all "Bottom" Wall Segments ---
        # Helper to find segments near the bottom of the floorplan
        def find_bottom_segments(corners, slope_tol=0.1, y_band_height=500.0):
            min_y_overall = min(c[1] for c in corners)
            bottom_segments = []
            for i in range(len(corners)):
                p1 = corners[i]
                p2 = corners[(i + 1) % len(corners)]
                # Check if the segment is mostly horizontal and within the bottom band
                is_horizontal = abs(p2[1] - p1[1]) < abs(p2[0] - p1[0]) * slope_tol
                is_in_bottom_band = (p1[1] < min_y_overall + y_band_height) and \
                                    (p2[1] < min_y_overall + y_band_height)
                if is_horizontal and is_in_bottom_band:
                    bottom_segments.append((p1, p2))
            return bottom_segments

        bottom_segments = find_bottom_segments(self.cvc.corners)
        if not bottom_segments:
            print("  -> ⚠️ Could not identify any bottom wall segments.")
            return None
            
        # --- 4. Differentiate Facade vs. Normal and Create Keep-Out Zones ---
        facade_margin_V1 = self._calculate_dynamic_qms_margin() #1850.0
        facade_margin = facade_margin_V1 + 510 
        normal_bottom_margin = 1350.0
        facade_y_threshold = min(c[1] for c in self.cvc.corners) + 100 # Segments very close to the absolute bottom are facades

        bottom_keep_out_zones = []
        for p1, p2 in bottom_segments:
            segment_line = LineString([p1, p2])
            avg_y = (p1[1] + p2[1]) / 2
            
            # If the segment is a true facade (like your red line)
            if avg_y < facade_y_threshold:
                # Create a 1850mm buffer upwards from this line
                keep_out_poly = segment_line.buffer(facade_margin, single_sided=True)
                # Ensure the buffer goes "into" the floorplan
                if not self.floorplan_polygon.contains(keep_out_poly.centroid):
                    keep_out_poly = segment_line.buffer(-facade_margin, single_sided=True)
                bottom_keep_out_zones.append(keep_out_poly)
                print(f"  -> Identified FACADE segment, applying {facade_margin}mm keep-out zone.")
            # If the segment is a normal bottom wall (like your yellow line)
            else:
                keep_out_poly = segment_line.buffer(normal_bottom_margin, single_sided=True)
                if not self.floorplan_polygon.contains(keep_out_poly.centroid):
                    keep_out_poly = segment_line.buffer(-normal_bottom_margin, single_sided=True)
                bottom_keep_out_zones.append(keep_out_poly)
                print(f"  -> Identified NORMAL bottom segment, applying {normal_bottom_margin}mm keep-out zone.")

        # --- 5. Combine and Apply Bottom Keep-Out Zones ---
        if bottom_keep_out_zones:
            combined_bottom_keep_out = unary_union(bottom_keep_out_zones)
            # Carve the keep-out zones from the already side-inset polygon
            zone_after_bottom_inset = inset_polygon.difference(combined_bottom_keep_out)
        else:
            zone_after_bottom_inset = inset_polygon

        if zone_after_bottom_inset.is_empty:
            print("  -> ⚠️ Zone is empty after applying bottom keep-out zones.")
            return None

        ### --- END OF MODIFICATION --- ###

        # --- 6. Apply Vertical Top Constraint & Subtract Obstacles (Largely Unchanged) ---
        # The bottom_boundary_y is no longer needed; it's handled by the shape subtraction.
        final_slicer = box(self.cvc.min_x - 1000, self.cvc.min_y - 1000, self.cvc.max_x + 1000, top_boundary_y)
        zone_before_obstacles = zone_after_bottom_inset.intersection(final_slicer)

        if zone_before_obstacles.is_empty:
            print("  -> ⚠️ Zone is empty after slicing with top boundary.")
            return None
            
        # (The rest of the obstacle subtraction logic remains the same)
        all_obstacle_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
        qms_entities = [e for e in self.msp.query('INSERT') if "QMS_DESK" in e.dxf.name.upper()]
        qms_bboxes_tuples = [(b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y) for e in qms_entities if (b := extents([e]))]
        st_bboxes_tuples = [(b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y) for e in st_entities if (b := extents([e]))]
        zone_defining_bboxes = set(qms_bboxes_tuples + st_bboxes_tuples)
        other_obstacles = [b for b in all_obstacle_bboxes if b not in zone_defining_bboxes]
        
        if other_obstacles:
            zone_after_fixture_buffer = zone_before_obstacles
        else:
            zone_after_fixture_buffer = zone_before_obstacles

        internal_partitions = self.cvc.get_internal_wall_partitions(50,670, 0)
        if internal_partitions:
            partition_polygons = [box(*bbox) for bbox in internal_partitions]
            final_zone = zone_after_fixture_buffer.difference(unary_union(partition_polygons))
        else:
            final_zone = zone_after_fixture_buffer

        if final_zone.is_empty:
            print("  -> ⚠️ Final zone is empty after subtracting all obstacles.")
            return None
            
        zone_bounds = final_zone.bounds
        zone_width = zone_bounds[2] - zone_bounds[0]
        zone_height = zone_bounds[3] - zone_bounds[1]
        print(f"  -> ✅ Successfully defined final placement zone (W: {zone_width:.0f}mm x H: {zone_height:.0f}mm)")
        return final_zone
    
    

    def draw_euro_center_placement_zone(self):
        """
        Calls the main logic function to get the Euro Center zone and then
        draws its boundary on the DXF for visual validation.
        """
        print("\n--- 🎨 Drawing Euro Center Placement Zone for Validation ---")

        # MODIFIED: This now calls the corrected, stable function
        placement_zone_poly = self.euro_center_placement_area()

        # Check if the zone was successfully calculated
        if placement_zone_poly and not placement_zone_poly.is_empty:
            
            # Get the area from the polygon object and print it.
            area_in_sq_mm = placement_zone_poly.area
            print(f"  -> 📏 Calculated Area of the Zone: {area_in_sq_mm:,.2f} mm^2")
            
            # Define a new layer for the debug drawing
            layer_name = "DEBUG_PLACEMENT_ZONE"
            if layer_name not in self.doc.layers:
                self.doc.layers.add(
                    name=layer_name,
                    color=6  # ACI color 6 is Magenta, which is highly visible
                )

            # Get the coordinates of the polygon's boundary
            zone_boundary_coords = list(placement_zone_poly.exterior.coords)

            # Add the polygon outline to the modelspace
            self.msp.add_lwpolyline(
                zone_boundary_coords,
                close=True,
                dxfattribs={"layer": layer_name, "lineweight": 35} # Make the line slightly thicker
            )
            
            print(f"  -> ✅ Zone boundary drawn on layer '{layer_name}' for validation.")
        
        else:
            print("  -> ⚠️ SKIPPED DRAWING: The placement zone could not be calculated.")


    #---------GRID-ZONE-FOR-EURO-CENTER-PLACEMENT-----------------
    #---------GRID-ZONE-FOR-EURO-CENTER-PLACEMENT-------------------
    #---------GRID-ZONE-FOR-EURO-CENTER-PLACEMENT-------------------

    def generate_row_wise_grid_og(self) -> List[Tuple[float, float]]:
        """
        Calculates a grid for 0° rotation and iteratively centers it within its
        local available space to handle irregular zones correctly.
        """
        from shapely.geometry import box, LineString

        print("\n--- MATRIX Generating ROW-WISE grid (0° Rotation) with Local Centering ---")
        zone = self.euro_center_placement_area()
        if not zone or zone.is_empty: return []

        cell_width = 1040.0
        cell_height = 1175.0
        
        initial_grid_points = []
        min_x_zone, min_y_zone, max_x_zone, max_y_zone = zone.bounds
        current_y = min_y_zone
        while current_y + cell_height <= max_y_zone:
            current_x = min_x_zone
            while current_x + cell_width <= max_x_zone:
                cell_box = box(current_x, current_y, current_x + cell_width, current_y + cell_height)
                if zone.contains(cell_box.centroid):
                    initial_grid_points.append((current_x, current_y))
                current_x += cell_width
            current_y += cell_height
            
        if not initial_grid_points: return []

        # --- FINAL: Iterative LOCAL Centering Logic ---
        min_x_grid = min(p[0] for p in initial_grid_points)
        min_y_grid = min(p[1] for p in initial_grid_points)
        max_x_grid = max(p[0] for p in initial_grid_points) + cell_width
        max_y_grid = max(p[1] for p in initial_grid_points) + cell_height
        grid_center_x = (min_x_grid + max_x_grid) / 2
        grid_center_y = (min_y_grid + max_y_grid) / 2

        # Find available space at the grid's center level
        h_slice = zone.intersection(LineString([(min_x_zone - 100, grid_center_y), (max_x_zone + 100, grid_center_y)]))
        local_x_min, _, local_x_max, _ = h_slice.bounds
        target_center_x = (local_x_min + local_x_max) / 2
        
        v_slice = zone.intersection(LineString([(grid_center_x, min_y_zone - 100), (grid_center_x, max_y_zone + 100)]))
        _, local_y_min, _, local_y_max = v_slice.bounds
        target_center_y = (local_y_min + local_y_max) / 2
        
        total_offset_x = target_center_x - grid_center_x
        total_offset_y = target_center_y - grid_center_y
        
        current_grid_points = list(initial_grid_points)
        
        # Iteratively nudge on X-axis
        nudge_step = 50.0
        num_steps_x = int(abs(total_offset_x) / nudge_step)
        step_x = nudge_step if total_offset_x > 0 else -nudge_step
        for _ in range(num_steps_x):
            proposed_points = [(p[0] + step_x, p[1]) for p in current_grid_points]
            if all(zone.contains(box(x, y, x + cell_width, y + cell_height).centroid) for x, y in proposed_points):
                current_grid_points = proposed_points
            else:
                break

        # Iteratively nudge on Y-axis
        num_steps_y = int(abs(total_offset_y) / nudge_step)
        step_y = nudge_step if total_offset_y > 0 else -nudge_step
        for _ in range(num_steps_y):
            proposed_points = [(p[0], p[1] + step_y) for p in current_grid_points]
            if all(zone.contains(box(x, y, x + cell_width, y + cell_height).centroid) for x, y in proposed_points):
                current_grid_points = proposed_points
            else:
                break
                
        final_grid_points = current_grid_points
        print(f"  -> ✅ Locally centered {len(final_grid_points)} spots for row-wise placement.")
        return final_grid_points
    
    def generate_column_wise_grid_v1_og(self) -> List[Tuple[float, float]]:
        """
        [CORRECTED to use full box containment]
        Calculates a centered grid for placing fixtures horizontally in vertical columns.
        Cell dimensions: 1175 (width) x 1040 (height).
        """
        from shapely.geometry import box, LineString

        print("\n--- MATRIX Generating COLUMN-WISE grid (90° Rotation) with Local Centering ---")
        zone = self.euro_center_placement_area()
        if not zone or zone.is_empty:
            print("  -> SKIPPED: The placement zone is not defined.")
            return []

        # Swapped dimensions for rotated fixtures
        cell_width = 1175.0
        cell_height = 1040.0
        min_x_zone, min_y_zone, max_x_zone, max_y_zone = zone.bounds
        
        initial_grid_points = []
        current_y = min_y_zone
        while current_y + cell_height <= max_y_zone:
            current_x = min_x_zone
            while current_x + cell_width <= max_x_zone:
                cell_box = box(current_x, current_y, current_x + cell_width, current_y + cell_height)
                if zone.contains(cell_box.centroid):
                    initial_grid_points.append((current_x, current_y))
                current_x += cell_width
            current_y += cell_height
            
        if not initial_grid_points:
            return []

        # --- Iterative LOCAL Centering Logic ---
        min_x_grid = min(p[0] for p in initial_grid_points)
        min_y_grid = min(p[1] for p in initial_grid_points)
        max_x_grid = max(p[0] for p in initial_grid_points) + cell_width
        max_y_grid = max(p[1] for p in initial_grid_points) + cell_height
        grid_center_x = (min_x_grid + max_x_grid) / 2
        grid_center_y = (min_y_grid + max_y_grid) / 2

        h_slice = zone.intersection(LineString([(min_x_zone - 100, grid_center_y), (max_x_zone + 100, grid_center_y)]))
        local_x_min, _, local_x_max, _ = h_slice.bounds
        target_center_x = (local_x_min + local_x_max) / 2
        
        v_slice = zone.intersection(LineString([(grid_center_x, min_y_zone - 100), (grid_center_x, max_y_zone + 100)]))
        _, local_y_min, _, local_y_max = v_slice.bounds
        target_center_y = (local_y_min + local_y_max) / 2
        
        total_offset_x = target_center_x - grid_center_x
        total_offset_y = target_center_y - grid_center_y
        
        current_grid_points = list(initial_grid_points)
        
        # Iteratively nudge on X-axis
        nudge_step = 50.0
        num_steps_x = int(abs(total_offset_x) / nudge_step)
        step_x = nudge_step if total_offset_x > 0 else -nudge_step
        for _ in range(num_steps_x):
            proposed_points = [(p[0] + step_x, p[1]) for p in current_grid_points]
            # ### --- FIX APPLIED HERE --- ###
            if all(zone.contains(box(x, y, x + cell_width, y + cell_height)) for x, y in proposed_points):
                current_grid_points = proposed_points
            else:
                break

        # Iteratively nudge on Y-axis
        num_steps_y = int(abs(total_offset_y) / nudge_step)
        step_y = nudge_step if total_offset_y > 0 else -nudge_step
        for _ in range(num_steps_y):
            proposed_points = [(p[0], p[1] + step_y) for p in current_grid_points]
            # ### --- FIX APPLIED HERE --- ###
            if all(zone.contains(box(x, y, x + cell_width, y + cell_height)) for x, y in proposed_points):
                current_grid_points = proposed_points
            else:
                break
                
        final_grid_points = current_grid_points

        print(f"  -> ✅ Calculated {len(final_grid_points)} spots for column-wise placement.")
        return final_grid_points

    def generate_row_wise_grid(self) -> List[Tuple[float, float]]:
        """
        Calculates a grid for 0° rotation without any centering logic.
        The grid is aligned to the bottom-left of the placement zone's bounding box.
        """
        from shapely.geometry import box

        print("\n--- MATRIX Generating ROW-WISE grid (0° Rotation) - No Centering ---")
        zone = self.euro_center_placement_area()
        if not zone or zone.is_empty:
            return []

        cell_width = 1040.0
        cell_height = 1175.0
        
        final_grid_points = []
        min_x_zone, min_y_zone, max_x_zone, max_y_zone = zone.bounds
        
        current_y = min_y_zone
        while current_y + cell_height <= max_y_zone:
            current_x = min_x_zone
            while current_x + cell_width <= max_x_zone:
                # Create a box for the potential fixture placement
                cell_box = box(current_x, current_y, current_x + cell_width, current_y + cell_height)
                
                # Check if the center of the cell is within the valid zone
                if zone.contains(cell_box.centroid):
                    final_grid_points.append((current_x, current_y))
                
                current_x += cell_width
            current_y += cell_height
            
        print(f"  -> ✅ Generated {len(final_grid_points)} spots for row-wise placement (no centering).")
        return final_grid_points
    
    def generate_column_wise_grid(self) -> List[Tuple[float, float]]:
        """
        Calculates a grid for 90° rotation without any centering logic.
        The grid is aligned to the bottom-left of the placement zone's bounding box.
        """
        from shapely.geometry import box

        print("\n--- MATRIX Generating COLUMN-WISE grid (90° Rotation) - No Centering ---")
        zone = self.euro_center_placement_area()
        if not zone or zone.is_empty:
            return []

        # Swapped dimensions for rotated fixtures
        cell_width = 1175.0
        cell_height = 1040.0
        
        final_grid_points = []
        min_x_zone, min_y_zone, max_x_zone, max_y_zone = zone.bounds
        
        current_y = min_y_zone
        while current_y + cell_height <= max_y_zone:
            current_x = min_x_zone
            while current_x + cell_width <= max_x_zone:
                # Create a box for the potential fixture placement
                cell_box = box(current_x, current_y, current_x + cell_width, current_y + cell_height)
                
                # Check if the center of the cell is within the valid zone
                if zone.contains(cell_box.centroid):
                    final_grid_points.append((current_x, current_y))

                current_x += cell_width
            current_y += cell_height
                
        print(f"  -> ✅ Generated {len(final_grid_points)} spots for column-wise placement (no centering).")
        return final_grid_points

    

    def draw_grid_for_validation(self, grid_points: List[Tuple[float, float]], cell_width: float, cell_height: float, layer_name: str, color: int):
        """
        Draws a calculated placement grid onto a specified layer for visualization.
        """
        if not grid_points:
            return

        print(f"--- 🎨 Drawing the '{layer_name}' grid for validation ---")
        if layer_name not in self.doc.layers:
            self.doc.layers.add(name=layer_name, color=color)

        for x, y in grid_points:
            points = [(x, y), (x + cell_width, y), (x + cell_width, y + cell_height), (x, y + cell_height)]
            self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": layer_name})
        
        print(f"  -> ✅ Drew {len(grid_points)} grid cells on layer '{layer_name}'.")


    #---------GRID-ZONE-FOR-EURO-CENTER-PLACEMENT----NEW-SETUP---------------
    #---------GRID-ZONE-FOR-EURO-CENTER-PLACEMENT----NEW-SETUP---------------
    
    #---------GRID-ZONE-FOR-MAX--EURO-CENTER-CALCULATION--COUNT---------------
    #---------GRID-ZONE-FOR-MAX--EURO-CENTER-CALCULATION--COUNT---------------
    
    def _create_grid_matrix(self, grid_points: List[Tuple[float, float]]) -> Tuple[List[List[int]], List[float], List[float]]:
        """
        Private helper to convert a list of (x,y) grid points into a 2D matrix (0s and 1s).
        NOW ALSO returns the sorted lists of unique coordinates that define the grid.
        """
        if not grid_points:
            return [], [], []

        unique_y = sorted(list(set(p[1] for p in grid_points)))
        unique_x = sorted(list(set(p[0] for p in grid_points)))

        y_to_row_idx = {y: i for i, y in enumerate(unique_y)}
        x_to_col_idx = {x: i for i, x in enumerate(unique_x)}

        num_rows = len(unique_y)
        num_cols = len(unique_x)
        matrix = [[0] * num_cols for _ in range(num_rows)]

        for x, y in grid_points:
            row_idx = y_to_row_idx[y]
            col_idx = x_to_col_idx[x]
            matrix[row_idx][col_idx] = 1

        return matrix, unique_y, unique_x

    
    def analyze_placement_patterns_best_only(self) -> Dict[str, Any]:
        """
        Analyzes placement patterns, finds the best one, and returns a dictionary
        containing the exact coordinates for fixture placement based on that pattern.
        """
        print("\n--- 📊 Analyzing patterns and generating final placement coordinates ---")
        
        analysis_results = {
            'row_wise_even_rows': 0, 'row_wise_odd_rows': 0,
            'column_wise_even_cols': 0, 'column_wise_odd_cols': 0,
        }
        
        # --- Phase 1: Analyze Row-Wise Grid (0° Rotation) ---
        row_points = self.generate_row_wise_grid()
        row_matrix, _, _ = self._create_grid_matrix(row_points)
        if row_matrix:
            for i, row in enumerate(row_matrix):
                if i % 2 == 0:
                    analysis_results['row_wise_even_rows'] += sum(row)
                else:
                    analysis_results['row_wise_odd_rows'] += sum(row)
        
        # --- Phase 2: Analyze Column-Wise Grid (90° Rotation) ---
        col_points = self.generate_column_wise_grid()
        col_matrix, _, _ = self._create_grid_matrix(col_points)
        if col_matrix:
            num_rows = len(col_matrix)
            num_cols = len(col_matrix[0])
            for j in range(num_cols):
                col_sum = sum(col_matrix[i][j] for i in range(num_rows))
                if j % 2 == 0:
                    analysis_results['column_wise_even_cols'] += col_sum
                else:
                    analysis_results['column_wise_odd_cols'] += col_sum

        # --- Phase 3: Find the Best Pattern ---
        best_pattern_name = max(analysis_results, key=analysis_results.get)
        max_fixtures = analysis_results[best_pattern_name]

        print("---  Analysis Complete ---")
        print(f"  -> Even Rows (0°): {analysis_results['row_wise_even_rows']} fixtures")
        print(f"  -> Odd Rows (0°):  {analysis_results['row_wise_odd_rows']} fixtures")
        print(f"  -> Even Columns (90°): {analysis_results['column_wise_even_cols']} fixtures")
        print(f"  -> Odd Columns (90°):  {analysis_results['column_wise_odd_cols']} fixtures")
        print(f"  ->  BEST PATTERN: '{best_pattern_name}' with {max_fixtures} fixtures.")

        # --- Phase 4: Get the coordinates for the BEST pattern ---
        coordinates_for_placement = []
        
        if 'row_wise' in best_pattern_name:
            matrix, unique_y, unique_x = self._create_grid_matrix(row_points)
            is_even_pattern = 'even' in best_pattern_name
            for i, row in enumerate(matrix):
                if (is_even_pattern and i % 2 == 0) or (not is_even_pattern and i % 2 != 0):
                    for j, cell in enumerate(row):
                        if cell == 1:
                            coordinates_for_placement.append((unique_x[j], unique_y[i]))

        elif 'column_wise' in best_pattern_name:
            matrix, unique_y, unique_x = self._create_grid_matrix(col_points)
            is_even_pattern = 'even' in best_pattern_name
            if matrix:
                num_rows, num_cols = len(matrix), len(matrix[0])
                for j in range(num_cols):
                    if (is_even_pattern and j % 2 == 0) or (not is_even_pattern and j % 2 != 0):
                        for i in range(num_rows):
                            if matrix[i][j] == 1:
                                coordinates_for_placement.append((unique_x[j], unique_y[i]))
        
        # --- Phase 5: Format the final output dictionary ---
        euro_place_dict = {}
        # Sort coordinates primarily by Y (row), then by X (column) for predictable numbering
        coordinates_for_placement.sort(key=lambda p: (p[1], p[0]))
        for i, (x, y) in enumerate(coordinates_for_placement, start=1):
            euro_place_dict[f"count_{i}"] = {"coordinates": [x, y]}
            
        final_output = {"euro_place": euro_place_dict}
        print(f"  -> Returning coordinates for {len(euro_place_dict)} placements.")

        placements_dict = {}
        coordinates_for_placement.sort(key=lambda p: (p[1], p[0]))
        for i, (x, y) in enumerate(coordinates_for_placement, start=1):
            placements_dict[f"count_{i}"] = {"coordinates": [x, y]}
        
        print(f"  -> Returning blueprint for {len(placements_dict)} placements.")
        
        # return final_output
        return {
            "best_pattern_name": best_pattern_name,
            "placements": placements_dict
        }
    
    def analyze_placement_patterns(self) -> Dict[str, Any]:
        """
        [MODIFIED V2] Analyzes all four placement patterns and returns a comprehensive
        dictionary containing counts and ID-tagged coordinates for ALL options,
        as well as identifying the best one.
        """
        print("\n--- 📊 Analyzing ALL placement patterns and generating blueprints ---")
        
        all_patterns_data = {}
        
        row_points = self.generate_row_wise_grid()
        col_points = self.generate_column_wise_grid()

        pattern_names = [
            'row_wise_even_rows', 'row_wise_odd_rows',
            'column_wise_even_cols', 'column_wise_odd_cols'
        ]

        for pattern_name in pattern_names:
            coordinates_for_placement = []
            
            if 'row_wise' in pattern_name:
                matrix, unique_y, unique_x = self._create_grid_matrix(row_points)
                if not matrix: continue
                is_even_pattern = 'even' in pattern_name
                
                for i, row in enumerate(matrix):
                    if (is_even_pattern and i % 2 == 0) or (not is_even_pattern and i % 2 != 0):
                        for j, cell in enumerate(row):
                            if cell == 1:
                                coordinates_for_placement.append((unique_x[j], unique_y[i]))

            elif 'column_wise' in pattern_name:
                matrix, unique_y, unique_x = self._create_grid_matrix(col_points)
                if not matrix: continue
                is_even_pattern = 'even' in pattern_name
                
                num_rows, num_cols = len(matrix), len(matrix[0])
                for j in range(num_cols):
                    if (is_even_pattern and j % 2 == 0) or (not is_even_pattern and j % 2 != 0):
                        for i in range(num_rows):
                            if matrix[i][j] == 1:
                                coordinates_for_placement.append((unique_x[j], unique_y[i]))
            
            # =================== MODIFICATION IS HERE ===================
            # This block converts the list of coordinates into the requested dictionary format.
            
            # Sort coordinates for a predictable "count_1", "count_2" order.
            coordinates_for_placement.sort(key=lambda p: (p[1], p[0])) 
            
            placements_dict = {}
            for i, coords in enumerate(coordinates_for_placement, start=1):
                placements_dict[f"count_{i}"] = {"coordinates": coords}

            all_patterns_data[pattern_name] = {
                "count": len(placements_dict),
                "placements": placements_dict # Store the new dictionary structure
            }
            # ============================================================

        # if not all_patterns_data:
        #     best_pattern_name = "None"
        # else:
        #     best_pattern_name = max(all_patterns_data, key=lambda p: all_patterns_data[p]["count"])
        
        if not all_patterns_data:
            best_pattern_name = "None"
        else:
            # Prioritize by count, then by 'column_wise' pattern in case of a tie.
            best_pattern_name = max(
                all_patterns_data,
                key=lambda p: (all_patterns_data[p]["count"], 'column' in p)
            )
            
        print("---  Analysis Complete ---")
        for name, data in all_patterns_data.items():
            print(f"  -> Pattern '{name}': {data['count']} fixtures")
        print(f"  ->  BEST PATTERN: '{best_pattern_name}' with {all_patterns_data.get(best_pattern_name, {}).get('count', 0)} fixtures.")

        return {
            "best_pattern_name": best_pattern_name,
            "all_options": all_patterns_data
        }


    

    #---------GRID-ZONE-FOR-MAX--EURO-CENTER-CALCULATION--AREA---------------
    #---------GRID-ZONE-FOR-MAX--EURO-CENTER-CALCULATION--AREA---------------
    #---------GRID-ZONE-FOR-MAX--EURO-CENTER-CALCULATION--PLACEMENT--SETUP---------------
    #---------GRID-ZONE-FOR-MAX--EURO-CENTER-CALCULATION--PLACEMENT--SETUP---------------


    # In DXF_Controller class

    def place_euro_centers_from_blueprint_v5(self, placement_blueprint: dict, display_calcs: dict, placed_bboxes: list):
        """
        [MODIFIED V11 - Skip ONLY 4th SUCCESSFUL Placement + 0° Centering]
        Orchestrates Euro Centre placement:
        - Skips ONLY the spot that would be the 4th SUCCESSFUL placement within each group.
        - If a spot is blocked by the group rule OR an obstacle, moves to the next blueprint spot.
        - Horizontally centers the final placed group if using 0° rotation.

        Args:
            placement_blueprint (dict): Output from analyze_placement_patterns().
            display_calcs (dict): Output from display_count_calc().
            placed_bboxes (list): Master list of bounding boxes.
        """
        # from Fixture import Fixture # Assuming Fixture is imported elsewhere
        from ezdxf.math import Vec2
        from shapely.geometry import LineString # Import LineString
        import json

        print("\n--- 💶 Placing Euro Centre Fixtures (Skip ONLY 4th Placement + 0° Centering) ---")
        # --- Obstacle handling (Unchanged) ---
        temp_obstacles = list(placed_bboxes)
        partitions = self.cvc.get_internal_wall_partitions(min_length=50, max_length=670.0, thickness=0.0)
        if partitions:
            temp_obstacles.extend(partitions); print(f"  -> ✅ Added {len(partitions)} small partitions for validation.")
        separator_line = self.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
        if separator_line:
            start_pt, end_pt = separator_line.dxf.start, separator_line.dxf.end
            separator_bbox = (min(start_pt.x, end_pt.x), min(start_pt.y, end_pt.y) - 1, max(start_pt.x, end_pt.x), max(start_pt.y, end_pt.y) + 1)
            if separator_bbox in temp_obstacles:
                temp_obstacles.remove(separator_bbox); print("  -> ✅ Temporarily ignored 'RETAIL_SEPARATOR' for validation.")

        # --- Required count, Blueprint analysis, Initial overflow/cap (Unchanged) ---
        total_required_euros = display_calcs.get('floor_fixtures', 0)
        if total_required_euros == 0: total_required_euros = self.fixtures.get("floor_fixtures", {}).get("Euro_centre", 0)
        if total_required_euros <= 0: print("  -> SKIPPED: No Euro Centre fixtures required."); return
        print(f"  -> Total required Euro Centres: {total_required_euros}")
        best_pattern_name = placement_blueprint.get("best_pattern_name", "None")
        if best_pattern_name == "None": print("  -> ⚠️ FAILED: No optimal placement pattern found."); self.overflow_fixture_count = total_required_euros; return
        best_pattern_info = placement_blueprint["all_options"][best_pattern_name]
        max_possible_in_pattern = best_pattern_info.get("count", 0)
        placements = best_pattern_info.get("placements", {})
        print(f"  -> Best pattern '{best_pattern_name}' offers {max_possible_in_pattern} potential spots.")
        num_to_place = min(total_required_euros, max_possible_in_pattern)
        initial_overflow = total_required_euros - num_to_place
        print(f"  -> Initially planning to place {num_to_place} fixtures.")
        if initial_overflow > 0: print(f"  -> Initial overflow count: {initial_overflow}")
        EURO_PLACEMENT_CAP = 9
        remaining_after_cap = 0
        if num_to_place > EURO_PLACEMENT_CAP:
            remaining_after_cap = num_to_place - EURO_PLACEMENT_CAP
            num_to_place = EURO_PLACEMENT_CAP
            print(f"  -> NOTE: Capped planned placement to {EURO_PLACEMENT_CAP}. Added {remaining_after_cap} to potential overflow.")

        # --- Fixture loading and rotation setup (Unchanged) ---
        try: fxtr = Fixture.Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"])
        except Exception as e: print(f"  -> 🔥 FATAL: Could not load Euro_centre fixture: {e}"); return
        is_rotated = 'column_wise' in best_pattern_name
        rotation = 90.0 if is_rotated else 0.0
        cell_width = 1175.0 if is_rotated else 1040.0
        cell_height = 1040.0 if is_rotated else 1175.0

        # --- Convert placements to sorted coordinate list (Unchanged) ---
        placement_coords = []
        sorted_keys = sorted(placements.keys(), key=lambda k: int(k.split('_')[1]))
        for key in sorted_keys: coords = placements[key]["coordinates"]; placement_coords.append(tuple(coords))
        placement_coords.sort(key=lambda p: (p[1], p[0])) # Sort Y then X

        # --- PHASE 1: PRE-CALCULATE CENTERING SHIFT (Only for 0° Rotation) ---
        # (Unchanged)
        shift_x = 0.0
        if not is_rotated and placement_coords:
            print("\n  -> Pre-calculating horizontal centering shift for 0° placement...")
            min_x_pattern = min(x for x, y in placement_coords)
            max_x_pattern = max(x for x, y in placement_coords) + cell_width
            center_x_pattern = (min_x_pattern + max_x_pattern) / 2
            avg_y_pattern = sum(y for x, y in placement_coords) / len(placement_coords)
            horizontal_slice = self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, avg_y_pattern), (self.cvc.max_x + 100, avg_y_pattern)]))
            center_x_available = center_x_pattern
            if isinstance(horizontal_slice, LineString) and not horizontal_slice.is_empty:
                local_x_min, _, local_x_max, _ = horizontal_slice.bounds
                center_x_available = (local_x_min + local_x_max) / 2
                print(f"    -> Available space center at avg Y={avg_y_pattern:.0f} is X={center_x_available:.0f}")
            else: print(f"    -> WARNING: Could not determine available width at avg Y={avg_y_pattern:.0f}.")
            shift_x = center_x_available - center_x_pattern
            print(f"    -> Calculated Horizontal Shift: {shift_x:.0f} mm")
        elif is_rotated: print("\n  -> Skipping centering: Fixtures are rotated (90°).")
        else: print("\n  -> Skipping centering: No blueprint spots found.")


        # ====================================================================
        # --- PHASE 2: EXECUTE PLACEMENT (Corrected "Skip ONLY 4th Placement" Rule) ---
        # ====================================================================
        placed_count_actual = 0
        spot_index = 0
        current_group_id = None
        placed_in_current_group = 0 # Tracks SUCCESSFUL placements
        spot_sequence_in_group = 0   # Tracks sequential spot index within group
        actual_placed_coords_shifted = []

        print(f"\n  -> Starting placement loop (Target: {num_to_place})...")

        while placed_count_actual < num_to_place and spot_index < len(placement_coords):

            original_x, original_y = placement_coords[spot_index]
            group_id = original_y if not is_rotated else original_x

            # Check if we are starting a new group
            if group_id != current_group_id:
                current_group_id = group_id
                placed_in_current_group = 0 # Reset actual placement count
                spot_sequence_in_group = 1 # Reset sequence counter
                print(f"    -> Considering group (ID: {group_id:.0f}).")
            else:
                spot_sequence_in_group += 1 # Increment sequence counter

            # --- Apply the "Skip ONLY the 4th Placement" rule ---
            # Calculate what the count WOULD BE if this placement succeeds
            potential_placed_count = placed_in_current_group + 1

            # Check if this potential placement is EXACTLY the 4th in the group
            # =================== CRITICAL CHANGE IS HERE ===================
            if potential_placed_count == 4:
                print(f"    -> SKIPPING blueprint spot {spot_index+1} at ({original_x:.0f}, {original_y:.0f}). Rule: Skip the 4th PLACEMENT in group {current_group_id:.0f} (Seq #{spot_sequence_in_group}).")
                spot_index += 1 # Move pointer to next spot
                # DO NOT change placed_in_current_group here
                # We also decrement the sequence counter because we didn't use this spot number
                # This ensures the *next* spot is considered correctly if it belongs to the same group.
                spot_sequence_in_group -= 1
                continue # Skip to the next iteration
            # ===============================================================

            # --- If Rule is OK (Not the 4th placement), Attempt Placement ---
            final_x = original_x + shift_x
            final_y = original_y
            target_center = Vec2(final_x + (cell_width / 2), final_y + (cell_height / 2))

            # Determine next target center for nudge logic (Unchanged)
            next_target_center = None
            next_spot_index = spot_index + 1
            if next_spot_index < len(placement_coords):
                next_x_orig, next_y_orig = placement_coords[next_spot_index]
                next_x_shifted = next_x_orig + shift_x if not is_rotated else next_x_orig
                next_target_center = Vec2(next_x_shifted + (cell_width / 2), next_y_orig + (cell_height / 2))

            print(f"    -> Attempting placement #{placed_count_actual + 1} using spot {spot_index+1} -> shifted ({final_x:.0f}, {final_y:.0f}) (Seq in Group: {spot_sequence_in_group}, Placed in Group: {placed_in_current_group})...")

            # Attempt placement at the calculated spot
            if self._validate_and_place_at_point_euro(fxtr, target_center, rotation, temp_obstacles, debug_draw=False, next_target_center=next_target_center):
                print(f"      -> SUCCESS: Placed Euro_centre #{placed_count_actual + 1}.")
                placed_count_actual += 1
                placed_in_current_group += 1 # Increment successful placements IN THIS GROUP
                actual_placed_coords_shifted.append((final_x, final_y))
                spot_index += 1 # Move to the next spot for the next fixture attempt
            else:
                print(f"      -> FAILED: Spot {spot_index+1} at ({final_x:.0f}, {final_y:.0f}) was blocked/invalid.")
                spot_index += 1 # Failed placement, move pointer to next spot
                # Do NOT increment placed_in_current_group on failure

        # =============================================================
        # --- FINAL OVERFLOW CALCULATION (Unchanged) ---
        # =============================================================
        actual_overflow = total_required_euros - placed_count_actual
        self.overflow_fixture_count = actual_overflow
        self.remaining_floor_fixtures = getattr(self, 'remaining_floor_fixtures', 0) + actual_overflow - initial_overflow - remaining_after_cap

        print(f"\n--- ✅ Finished Euro Centre Placement ---")
        print(f"  -> Successfully placed: {placed_count_actual} fixtures.")
        if actual_overflow > 0:
            print(f"  -> Final overflow count (unplaced): {actual_overflow}")

    def place_euro_centers_from_blueprint_v1(self, placement_blueprint: dict, display_calcs: dict, placed_bboxes: list):
        """
        [MODIFIED V9 - Corrected Sequence Tracking for Skip Rule]
        Orchestrates Euro Centre placement:
        - Skips the 4th, 8th, 12th, etc. *sequential spot considered* within each group.
        - If a spot is blocked by the group rule OR an obstacle, moves to the next blueprint spot.
        - Horizontally centers the final placed group if using 0° rotation.

        Args:
            placement_blueprint (dict): Output from analyze_placement_patterns().
            display_calcs (dict): Output from display_count_calc().
            placed_bboxes (list): Master list of bounding boxes.
        """
        # from Fixture import Fixture # Assuming Fixture is imported elsewhere
        from ezdxf.math import Vec2
        from shapely.geometry import LineString # Import LineString
        import json

        print("\n--- 💶 Placing Euro Centre Fixtures (Corrected Skip 4th/8th/... + 0° Centering) ---")
        # --- Obstacle handling (Unchanged) ---
        temp_obstacles = list(placed_bboxes)
        partitions = self.cvc.get_internal_wall_partitions(min_length=50, max_length=670.0, thickness=0.0)
        if partitions:
            temp_obstacles.extend(partitions); print(f"  -> ✅ Added {len(partitions)} small partitions for validation.")
        separator_line = self.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
        if separator_line:
            start_pt, end_pt = separator_line.dxf.start, separator_line.dxf.end
            separator_bbox = (min(start_pt.x, end_pt.x), min(start_pt.y, end_pt.y) - 1, max(start_pt.x, end_pt.x), max(start_pt.y, end_pt.y) + 1)
            if separator_bbox in temp_obstacles:
                temp_obstacles.remove(separator_bbox); print("  -> ✅ Temporarily ignored 'RETAIL_SEPARATOR' for validation.")

        # --- Required count, Blueprint analysis, Initial overflow/cap (Unchanged) ---
        total_required_euros = display_calcs.get('floor_fixtures', 0)
        if total_required_euros == 0: total_required_euros = self.fixtures.get("floor_fixtures", {}).get("Euro_centre", 0)
        if total_required_euros <= 0: print("  -> SKIPPED: No Euro Centre fixtures required."); return
        print(f"  -> Total required Euro Centres: {total_required_euros}")
        best_pattern_name = placement_blueprint.get("best_pattern_name", "None")
        if best_pattern_name == "None": print("  -> ⚠️ FAILED: No optimal placement pattern found."); self.overflow_fixture_count = total_required_euros; return
        best_pattern_info = placement_blueprint["all_options"][best_pattern_name]
        max_possible_in_pattern = best_pattern_info.get("count", 0)
        placements = best_pattern_info.get("placements", {})
        print(f"  -> Best pattern '{best_pattern_name}' offers {max_possible_in_pattern} potential spots.")
        num_to_place = min(total_required_euros, max_possible_in_pattern)
        initial_overflow = total_required_euros - num_to_place
        print(f"  -> Initially planning to place {num_to_place} fixtures.")
        if initial_overflow > 0: print(f"  -> Initial overflow count: {initial_overflow}")
        EURO_PLACEMENT_CAP = 9
        remaining_after_cap = 0
        if num_to_place > EURO_PLACEMENT_CAP:
            remaining_after_cap = num_to_place - EURO_PLACEMENT_CAP
            num_to_place = EURO_PLACEMENT_CAP
            print(f"  -> NOTE: Capped planned placement to {EURO_PLACEMENT_CAP}. Added {remaining_after_cap} to potential overflow.")

        # --- Fixture loading and rotation setup (Unchanged) ---
        try: fxtr = Fixture.Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"])
        except Exception as e: print(f"  -> 🔥 FATAL: Could not load Euro_centre fixture: {e}"); return
        is_rotated = 'column_wise' in best_pattern_name
        rotation = 90.0 if is_rotated else 0.0
        cell_width = 1175.0 if is_rotated else 1040.0
        cell_height = 1040.0 if is_rotated else 1175.0

        # --- Convert placements to sorted coordinate list (Unchanged) ---
        placement_coords = []
        sorted_keys = sorted(placements.keys(), key=lambda k: int(k.split('_')[1]))
        for key in sorted_keys: coords = placements[key]["coordinates"]; placement_coords.append(tuple(coords))
        placement_coords.sort(key=lambda p: (p[1], p[0])) # Sort Y then X

        # --- PHASE 1: PRE-CALCULATE CENTERING SHIFT (Only for 0° Rotation) ---
        # (Unchanged)
        shift_x = 0.0
        if not is_rotated and placement_coords:
            print("\n  -> Pre-calculating horizontal centering shift for 0° placement...")
            min_x_pattern = min(x for x, y in placement_coords)
            max_x_pattern = max(x for x, y in placement_coords) + cell_width
            center_x_pattern = (min_x_pattern + max_x_pattern) / 2
            avg_y_pattern = sum(y for x, y in placement_coords) / len(placement_coords)
            horizontal_slice = self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, avg_y_pattern), (self.cvc.max_x + 100, avg_y_pattern)]))
            center_x_available = center_x_pattern
            if isinstance(horizontal_slice, LineString) and not horizontal_slice.is_empty:
                local_x_min, _, local_x_max, _ = horizontal_slice.bounds
                center_x_available = (local_x_min + local_x_max) / 2
                print(f"    -> Available space center at avg Y={avg_y_pattern:.0f} is X={center_x_available:.0f}")
            else: print(f"    -> WARNING: Could not determine available width at avg Y={avg_y_pattern:.0f}.")
            shift_x = center_x_available - center_x_pattern
            print(f"    -> Calculated Horizontal Shift: {shift_x:.0f} mm")
        elif is_rotated: print("\n  -> Skipping centering: Fixtures are rotated (90°).")
        else: print("\n  -> Skipping centering: No blueprint spots found.")


        # ====================================================================
        # --- PHASE 2: EXECUTE PLACEMENT (Corrected Sequence Tracking) ---
        # ====================================================================
        placed_count_actual = 0
        spot_index = 0
        current_group_id = None
        placed_in_current_group = 0 # Tracks SUCCESSFUL placements
        # *** NEW: Track the sequence number WITHIN the current group ***
        spot_sequence_in_group = 0
        actual_placed_coords_shifted = []

        print(f"\n  -> Starting placement loop (Target: {num_to_place})...")

        while placed_count_actual < num_to_place and spot_index < len(placement_coords):

            original_x, original_y = placement_coords[spot_index]
            group_id = original_y if not is_rotated else original_x

            # Check if we are starting a new group
            if group_id != current_group_id:
                current_group_id = group_id
                placed_in_current_group = 0 # Reset actual placement count
                spot_sequence_in_group = 1 # *** Reset sequence counter ***
                print(f"    -> Considering group (ID: {group_id:.0f}).")
            else:
                spot_sequence_in_group += 1 # *** Increment sequence counter ***

            # --- Apply the "Skip One After Three" rule using the SEQUENCE counter ---
            # Check if this spot is the 4th, 8th, 12th, etc. IN SEQUENCE for this group
            # if spot_sequence_in_group > 3 and (spot_sequence_in_group % 4 == 0):
            if spot_sequence_in_group > 3 and (spot_sequence_in_group  == 4):
                print(f"    -> SKIPPING blueprint spot {spot_index+1} at ({original_x:.0f}, {original_y:.0f}). Rule: Skip 4th/8th/... position (sequence #{spot_sequence_in_group}) in group {current_group_id:.0f}.")
                spot_index += 1 # Move pointer to next spot
                # DO NOT change placed_in_current_group here
                continue # Skip to the next iteration

            # --- If Sequence Rule is OK, Attempt Placement ---
            final_x = original_x + shift_x
            final_y = original_y
            target_center = Vec2(final_x + (cell_width / 2), final_y + (cell_height / 2))

            # Determine next target center for nudge logic (Unchanged)
            next_target_center = None
            next_spot_index = spot_index + 1
            if next_spot_index < len(placement_coords):
                next_x_orig, next_y_orig = placement_coords[next_spot_index]
                next_x_shifted = next_x_orig + shift_x if not is_rotated else next_x_orig
                next_target_center = Vec2(next_x_shifted + (cell_width / 2), next_y_orig + (cell_height / 2))

            print(f"    -> Attempting placement #{placed_count_actual + 1} using spot {spot_index+1} -> shifted ({final_x:.0f}, {final_y:.0f}) (Seq in Group: {spot_sequence_in_group}, Placed in Group: {placed_in_current_group})...")

            # Attempt placement at the calculated spot
            if self._validate_and_place_at_point_euro(fxtr, target_center, rotation, temp_obstacles, debug_draw=False, next_target_center=next_target_center):
                print(f"      -> SUCCESS: Placed Euro_centre #{placed_count_actual + 1}.")
                placed_count_actual += 1
                placed_in_current_group += 1 # Increment successful placements IN THIS GROUP
                actual_placed_coords_shifted.append((final_x, final_y))
                spot_index += 1 # Move to the next spot for the next fixture attempt
            else:
                print(f"      -> FAILED: Spot {spot_index+1} at ({final_x:.0f}, {final_y:.0f}) was blocked/invalid.")
                spot_index += 1 # Failed placement, move pointer to next spot
                # Do NOT increment placed_in_current_group on failure

        # =============================================================
        # --- FINAL OVERFLOW CALCULATION (Unchanged) ---
        # =============================================================
        actual_overflow = total_required_euros - placed_count_actual
        self.overflow_fixture_count = actual_overflow
        self.remaining_floor_fixtures = getattr(self, 'remaining_floor_fixtures', 0) + actual_overflow - initial_overflow - remaining_after_cap

        print(f"\n--- ✅ Finished Euro Centre Placement ---")
        print(f"  -> Successfully placed: {placed_count_actual} fixtures.")
        if actual_overflow > 0:
            print(f"  -> Final overflow count (unplaced): {actual_overflow}")

    def place_euro_centers_from_blueprint_v1(self, placement_blueprint: dict, display_calcs: dict, placed_bboxes: list):
        """
        [MODIFIED V5 - Centering for 0° + Group Limit]
        Orchestrates Euro Centre placement, enforcing a max of 3 per group
        AND horizontally centering the final selected group if placed at 0° rotation.

        Args:
            placement_blueprint (dict): Output from analyze_placement_patterns().
            display_calcs (dict): Output from display_count_calc().
            placed_bboxes (list): Master list of bounding boxes.
        """
        # from Fixture import Fixture # Assuming Fixture is imported elsewhere
        from ezdxf.math import Vec2
        from shapely.geometry import LineString # Import LineString
        import json

        print("\n--- 💶 Placing Euro Centre Fixtures (Max 3/Group + 0° Centering) ---")
        # --- Obstacle handling (Unchanged) ---
        temp_obstacles = list(placed_bboxes)
        partitions = self.cvc.get_internal_wall_partitions(min_length=50, max_length=670.0, thickness=0.0)
        if partitions:
            temp_obstacles.extend(partitions)
            print(f"  -> ✅ Added {len(partitions)} small partitions for validation.")
        separator_line = self.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
        if separator_line:
            start_pt, end_pt = separator_line.dxf.start, separator_line.dxf.end
            separator_bbox = (min(start_pt.x, end_pt.x), min(start_pt.y, end_pt.y) - 1, max(start_pt.x, end_pt.x), max(start_pt.y, end_pt.y) + 1)
            if separator_bbox in temp_obstacles:
                temp_obstacles.remove(separator_bbox)
                print("  -> ✅ Temporarily ignored 'RETAIL_SEPARATOR' for validation.")

        # --- Required count, Blueprint analysis, Initial overflow/cap (Unchanged) ---
        total_required_euros = display_calcs.get('floor_fixtures', 0)
        if total_required_euros == 0: total_required_euros = self.fixtures.get("floor_fixtures", {}).get("Euro_centre", 0)
        if total_required_euros <= 0: print("  -> SKIPPED: No Euro Centre fixtures required."); return
        print(f"  -> Total required Euro Centres: {total_required_euros}")
        best_pattern_name = placement_blueprint.get("best_pattern_name", "None")
        if best_pattern_name == "None": print("  -> ⚠️ FAILED: No optimal placement pattern found."); self.overflow_fixture_count = total_required_euros; return
        best_pattern_info = placement_blueprint["all_options"][best_pattern_name]
        max_possible_in_pattern = best_pattern_info.get("count", 0)
        placements = best_pattern_info.get("placements", {})
        print(f"  -> Best pattern '{best_pattern_name}' offers {max_possible_in_pattern} potential spots.")
        num_to_place = min(total_required_euros, max_possible_in_pattern)
        initial_overflow = total_required_euros - num_to_place
        print(f"  -> Initially planning to place {num_to_place} fixtures.")
        if initial_overflow > 0: print(f"  -> Initial overflow count: {initial_overflow}")
        EURO_PLACEMENT_CAP = 9
        remaining_after_cap = 0
        if num_to_place > EURO_PLACEMENT_CAP:
            remaining_after_cap = num_to_place - EURO_PLACEMENT_CAP
            num_to_place = EURO_PLACEMENT_CAP
            print(f"  -> NOTE: Capped planned placement to {EURO_PLACEMENT_CAP}. Added {remaining_after_cap} to potential overflow.")

        # --- Fixture loading and rotation setup (Unchanged) ---
        try: fxtr = Fixture.Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"])
        except Exception as e: print(f"  -> 🔥 FATAL: Could not load Euro_centre fixture: {e}"); return
        is_rotated = 'column_wise' in best_pattern_name
        rotation = 90.0 if is_rotated else 0.0
        cell_width = 1175.0 if is_rotated else 1040.0
        cell_height = 1040.0 if is_rotated else 1175.0

        # --- Convert placements to sorted coordinate list (Unchanged) ---
        placement_coords = []
        sorted_keys = sorted(placements.keys(), key=lambda k: int(k.split('_')[1]))
        for key in sorted_keys: coords = placements[key]["coordinates"]; placement_coords.append(tuple(coords))
        placement_coords.sort(key=lambda p: (p[1], p[0])) # Sort Y then X

        # =============================================================
        # --- PHASE 1: IDENTIFY SPOTS TO USE (Applying Group Limit) ---
        # =============================================================
        spots_to_place = [] # Store the (x, y) coordinates we intend to use
        current_group_id = None
        count_in_current_group = 0
        planned_count = 0 # How many we *intend* to place based on rules

        print(f"\n  -> Identifying spots to use (Target: {num_to_place}, Max 3 per group)...")

        for i, (x, y) in enumerate(placement_coords):
            if planned_count >= num_to_place: break

            group_id = y if not is_rotated else x

            if group_id != current_group_id:
                current_group_id = group_id
                count_in_current_group = 1
            else:
                count_in_current_group += 1

            if count_in_current_group > 3:
                print(f"    -> SKIPPING blueprint spot at ({x:.0f}, {y:.0f}). Exceeds max 3 in group.")
                continue # Skip this spot

            # If the spot is valid according to the rules, add it to our list
            spots_to_place.append((x, y))
            planned_count += 1
            print(f"    -> Planning to use spot #{planned_count} at ({x:.0f}, {y:.0f}) (Group Count: {count_in_current_group})")

        if not spots_to_place:
            print("  -> No valid spots identified after applying group limit rule.")
            self.overflow_fixture_count = total_required_euros # All required become overflow
            return

        # =============================================================
        # --- PHASE 2: CALCULATE CENTERING SHIFT (Only for 0° Rotation) ---
        # =============================================================
        final_spots_for_placement = spots_to_place # Default to original spots
        shift_x = 0.0 # Default shift

        if not is_rotated:
            print("\n  -> Calculating horizontal centering for 0° placement...")
            min_x_group = min(x for x, y in spots_to_place)
            max_x_group = max(x for x, y in spots_to_place) + cell_width # Use cell_width for 0°
            center_x_group = (min_x_group + max_x_group) / 2

            # Calculate the average Y of the selected spots to find the center line
            avg_y_group = sum(y for x, y in spots_to_place) / len(spots_to_place)

            # Find the available horizontal space at this average Y-level
            horizontal_slice = self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, avg_y_group), (self.cvc.max_x + 100, avg_y_group)]))

            center_x_available = center_x_group # Default if slice fails
            if isinstance(horizontal_slice, LineString) and not horizontal_slice.is_empty:
                local_x_min, _, local_x_max, _ = horizontal_slice.bounds
                center_x_available = (local_x_min + local_x_max) / 2
                print(f"    -> Available space center at Y={avg_y_group:.0f} is X={center_x_available:.0f}")
            else:
                print(f"    -> WARNING: Could not determine available width at Y={avg_y_group:.0f}. Centering may be inaccurate.")

            shift_x = center_x_available - center_x_group
            print(f"    -> Calculated Horizontal Shift: {shift_x:.0f} mm")

            # Apply the shift to the X coordinates
            final_spots_for_placement = [(x + shift_x, y) for x, y in spots_to_place]
        else:
            print("\n  -> Skipping centering: Fixtures are rotated (90°).")

        # =============================================================
        # --- PHASE 3: EXECUTE PLACEMENT USING FINAL SPOTS ---
        # =============================================================
        placed_count_actual = 0
        print(f"\n  -> Starting final placement loop for {len(final_spots_for_placement)} planned spots...")

        # --- Determine the sequence for next_target_center ---
        # Sort final spots again to ensure consistent neighbor checking
        final_spots_for_placement.sort(key=lambda p: (p[1], p[0]))
        final_target_centers = [Vec2(x + (cell_width / 2), y + (cell_height / 2)) for x, y in final_spots_for_placement]

        for i, (x, y) in enumerate(final_spots_for_placement):
            target_center = Vec2(x + (cell_width / 2), y + (cell_height / 2))

            # Provide the next center if it exists in the *final* placement list
            next_target_center = final_target_centers[i + 1] if i + 1 < len(final_target_centers) else None

            print(f"    -> Attempting final placement #{placed_count_actual + 1} at shifted ({x:.0f}, {y:.0f})...")
            if self._validate_and_place_at_point_euro(fxtr, target_center, rotation, temp_obstacles, debug_draw=False, next_target_center=next_target_center):
                print(f"      -> SUCCESS: Placed Euro_centre #{placed_count_actual + 1}.")
                placed_count_actual += 1
            else:
                print(f"      -> FAILED: Final validation blocked spot at ({x:.0f}, {y:.0f}).")

        # =============================================================
        # --- FINAL OVERFLOW CALCULATION ---
        # =============================================================
        actual_overflow = total_required_euros - placed_count_actual
        self.overflow_fixture_count = actual_overflow
        # Adjust remaining floor fixtures based on what was *actually* placed vs initially planned
        planned_but_not_placed = planned_count - placed_count_actual
        self.remaining_floor_fixtures = getattr(self, 'remaining_floor_fixtures', 0) + actual_overflow - initial_overflow - remaining_after_cap + planned_but_not_placed

        print(f"\n--- ✅ Finished Euro Centre Placement ---")
        print(f"  -> Successfully placed: {placed_count_actual} fixtures.")
        if actual_overflow > 0:
            print(f"  -> Final overflow count (unplaced due to rules/blocks): {actual_overflow}")
    
    def place_euro_centers_from_blueprint(self, placement_blueprint: dict, display_calcs: dict, placed_bboxes: list):
        """
        Orchestrates the placement of Euro Centre fixtures based on a comparison between
        the required count and the maximum optimal capacity of the floor space.

        Args:
            placement_blueprint (dict): The output from analyze_placement_patterns().
            display_calcs (dict): The output from display_count_calc(), providing the base count.
            placed_bboxes (list): The master list of bounding boxes for all placed objects.
        """
        # from Fixture import Fixture
        from ezdxf.math import Vec2
        import json

        print("\n--- 💶 Placing Euro Centre Fixtures from Blueprint ---")
        # --- NEW MODIFICATION TO IGNORE THE SEPARATOR LINE DURING PLACEMENT ---
        temp_obstacles = list(placed_bboxes) # Create a temporary copy
    
        partitions = self.cvc.get_internal_wall_partitions(min_length=50, max_length=670.0, thickness=0.0)
        if partitions:
            temp_obstacles.extend(partitions)
            print(f"  -> ✅ Added {len(partitions)} small partitions to the obstacle list for validation.")
        # --- END OF NEW CODE ---
        separator_line = self.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
        if separator_line:
            start_pt = separator_line.dxf.start
            end_pt = separator_line.dxf.end
            separator_bbox = (
                min(start_pt.x, end_pt.x),
                min(start_pt.y, end_pt.y) - 1,
                max(start_pt.x, end_pt.x),
                max(start_pt.y, end_pt.y) + 1
            )
            if separator_bbox in temp_obstacles:
                temp_obstacles.remove(separator_bbox)
                print("  -> ✅ Temporarily ignored 'RETAIL_SEPARATOR' line for validation.")
        # --- END OF MODIFICATION ---

        # --- CORRECTED LOGIC (V3) ---
        # The required count is taken directly from the 'display_calcs' dictionary.
        # NOTE: For the overflow count from wall fixtures to be included, you must call
        # a wall placement orchestration function (like 'orchestrate_wall_and_overflow_placement')
        # before this function. The current main.py script does not do this.
        total_required_euros = display_calcs.get('floor_fixtures', 0)
        
        
        # As a fallback, if display_calcs gives 0, check the original fixture list from the merch mix.
        if total_required_euros == 0:
            print("  -> 'display_calcs' reported 0 floor fixtures. Checking original merch mix count as a fallback.")
            total_required_euros = self.fixtures.get("floor_fixtures", {}).get("Euro_centre", 0)

        if total_required_euros <= 0:
            print("  -> SKIPPED: No Euro Centre fixtures required based on calculations and merch mix.")
            return

        print(f"  -> Total required Euro Centres to place: {total_required_euros}")

        # --- The rest of the function remains the same ---
        best_pattern_name = placement_blueprint.get("best_pattern_name", "None")

        if best_pattern_name == "None":
            print("  -> ⚠️ FAILED: Could not determine an optimal placement pattern. No fixtures will be placed.")
            self.overflow_fixture_count = total_required_euros
            print(f"  -> Overflow fixtures: {self.overflow_fixture_count}")
            return

        best_pattern_info = placement_blueprint["all_options"][best_pattern_name]
        max_count = best_pattern_info.get("count", 0)
        placements = best_pattern_info.get("placements", {})

        print(f"  -> Maximum optimal capacity found: {max_count} fixtures using pattern '{best_pattern_name}'.")

        num_to_place = 0
        self.overflow_fixture_count = 0

        if max_count <= total_required_euros:
            print("  -> Strategy: Space is limited. Placing maximum possible number of fixtures.")
            num_to_place = max_count
            self.overflow_fixture_count = total_required_euros - max_count
            print(f"  -> Overflow fixtures to be handled later: {self.overflow_fixture_count}")
        else:
            print("  -> Strategy: Ample space available. Placing the required number of fixtures.")
            num_to_place = total_required_euros

        # --- CAP: Place at most 7 Euro Centre fixtures here; add the rest to overflow
        EURO_PLACEMENT_CAP = 9
        if num_to_place == 0:
            print("  -> No fixtures to place based on the chosen strategy.")
            self.overflow_fixture_count = getattr(self, 'overflow_fixture_count', 0)
            self.remaining_floor_fixtures = getattr(self, 'remaining_floor_fixtures', 0)
            return

        if num_to_place > EURO_PLACEMENT_CAP:
            original_num = num_to_place
            num_to_place = EURO_PLACEMENT_CAP
            # remaining (not-placed) fixtures should be recorded for later handling
            remaining_after_cap = original_num - EURO_PLACEMENT_CAP
            # keep existing overflow and add this remaining
            self.overflow_fixture_count = getattr(self, 'overflow_fixture_count', 0) + remaining_after_cap
            # also record a convenience property for other parts of the app
            self.remaining_floor_fixtures = getattr(self, 'remaining_floor_fixtures', 0) + remaining_after_cap
            print(f"  -> NOTE: Capped placement to {EURO_PLACEMENT_CAP}. Added {remaining_after_cap} fixtures to overflow/remaining.")

        try:
            fxtr = Fixture.Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"])
        except Exception as e:
            print(f"  -> 🔥 FATAL: Could not load Euro_centre fixture: {e}")
            return

        is_rotated = 'column_wise' in best_pattern_name
        rotation = 90.0 if is_rotated else 0.0
        cell_width = 1175.0 if is_rotated else 1040.0
        cell_height = 1040.0 if is_rotated else 1175.0

        placement_coords = []
        for i in range(1, len(placements) + 1):
            key = f"count_{i}"
            if key in placements:
                coords = placements[key]["coordinates"]
                placement_coords.append(tuple(coords))

        placed_count = 0
        for i in range(num_to_place):
            if i >= len(placement_coords):
                break
            x, y = placement_coords[i]
            target_center = Vec2(x + (cell_width / 2), y + (cell_height / 2))

            # --- NEW: Look ahead for the next fixture's target center ---
            next_target_center = None
            if i + 1 < len(placement_coords):
                next_x, next_y = placement_coords[i + 1]
                # Calculate the center of the next cell
                next_target_center = Vec2(next_x + (cell_width / 2), next_y + (cell_height / 2))
            # --- END OF NEW LOGIC ---

            
            if self._validate_and_place_at_point_euro(fxtr, target_center, rotation, temp_obstacles, debug_draw=False,next_target_center=next_target_center):
                print(f"    -> Placed Euro_centre #{placed_count + 1} at ({x:.0f}, {y:.0f}) with {rotation}° rotation.")
                placed_count += 1
            else:
                print(f"    -> ⚠️ WARNING: Spot at ({x:.0f}, {y:.0f}) was blocked, skipping.")

        print(f"\n--- ✅ Finished Euro Centre Placement: Placed {placed_count} of {num_to_place} planned fixtures. ---")


    
    def _validate_and_place_at_point_euro(self, fixture, target_center, angle_deg, placed_bboxes, debug_draw=False, next_target_center: Optional[Vec2] = None):
        """
        [V9 - ROBUST SINGLE-FIXTURE NUDGE] Validates and places a fixture.
        - If the single-direction search is not possible (e.g., for the last or only fixture),
          it now FALLS BACK to a simple 4-directional search to find a clear spot.
        """
        from shapely.geometry import Polygon, box, Point
        from ezdxf.math import Matrix44, BoundingBox2d, Vec2
        import math

        # --- The internal 'check_spot' helper function remains unchanged ---
        def check_spot(center_point):
            AISLE_OVERLAP_TOLERANCE_AREA = 600000.0
            BODY_OVERLAP_TOLERANCE_AREA = 1000.0
            transform = Matrix44.chain(Matrix44.translate(-fixture.bounding_box.center.x, -fixture.bounding_box.center.y, 0), Matrix44.z_rotate(math.radians(angle_deg)), Matrix44.translate(center_point.x, center_point.y, 0))
            world_corners = list(transform.transform_vertices(fixture.bounding_box.rect_vertices()))
            current_aabb = BoundingBox2d(world_corners)
            fixture_polygon = Polygon([(p.x, p.y) for p in world_corners])
            if not self.floorplan_polygon.contains(fixture_polygon): return None, None
            for b in placed_bboxes:
                obstacle_poly = box(*b)
                if fixture_polygon.intersects(obstacle_poly):
                    if fixture_polygon.intersection(obstacle_poly).area > BODY_OVERLAP_TOLERANCE_AREA: return None, None
            if "euro_centre" in fixture.name.lower():
                clearance = 1050.0
                def is_aisle_significantly_blocked(clearance_poly):
                    for b in placed_bboxes:
                        obstacle_poly = box(*b)
                        if clearance_poly.intersects(obstacle_poly) and clearance_poly.intersection(obstacle_poly).area > AISLE_OVERLAP_TOLERANCE_AREA: return True
                    return False
                if 85 < angle_deg < 95 or 265 < angle_deg < 275:
                    left_aisle = box(current_aabb.extmin.x - clearance, current_aabb.extmin.y + 100, current_aabb.extmin.x, current_aabb.extmax.y - 100)
                    right_aisle = box(current_aabb.extmax.x, current_aabb.extmin.y + 100, current_aabb.extmax.x + clearance, current_aabb.extmax.y - 100)
                    if is_aisle_significantly_blocked(left_aisle) or is_aisle_significantly_blocked(right_aisle): return None, None
                else:
                    top_aisle = box(current_aabb.extmin.x + 100, current_aabb.extmax.y, current_aabb.extmax.x - 100, current_aabb.extmax.y + clearance)
                    bottom_aisle = box(current_aabb.extmin.x + 100, current_aabb.extmin.y - clearance, current_aabb.extmax.x - 100, current_aabb.extmin.y)
                    if is_aisle_significantly_blocked(top_aisle) or is_aisle_significantly_blocked(bottom_aisle): return None, None
            return current_aabb, center_point

        # --- Main Function Logic ---
        final_aabb, final_center = check_spot(target_center)

        if final_aabb is None:
            print(f"    -> Initial spot at ({target_center.x:.0f}, {target_center.y:.0f}) is blocked. Starting search...")

            # --- MODIFICATION START ---
            zone = self.euro_center_placement_area()
            if not zone or zone.is_empty:
                print("      -> Search failed: Cannot search without a valid placement zone.")
                return False

            # **PRIMARY SEARCH**: Use the "next fixture" direction if available
            if next_target_center:
                search_vector = (next_target_center - target_center).normalize()
                print(f"      -> Searching ONLY in the direction of the next fixture: {search_vector}")
                step = 50
                current_offset = step
                while True:
                    test_center = target_center + (search_vector * current_offset)
                    if not zone.contains(Point(test_center.x, test_center.y)):
                        print("      -> Search stopped: Reached placement zone boundary.")
                        break
                    found_aabb, found_center = check_spot(test_center)
                    if found_aabb:
                        final_aabb, final_center = found_aabb, found_center
                        break
                    current_offset += step

            # **FALLBACK SEARCH**: If no next fixture, perform a 4-directional search
            else:
                print("      -> No next fixture target provided. FALLING BACK to 4-directional search.")
                search_vectors = [Vec2(1, 0), Vec2(-1, 0), Vec2(0, 1), Vec2(0, -1)] # Right, Left, Up, Down
                search_radius = 1000  # Max distance to search
                step = 50

                for move_vec in search_vectors:
                    for i in range(1, int(search_radius / step) + 1):
                        offset_vec = move_vec * (i * step)
                        test_center = target_center + offset_vec

                        # Check if the test point is still in the valid zone before checking the spot
                        if not zone.contains(Point(test_center.x, test_center.y)):
                            continue # Skip points outside the zone

                        found_aabb, found_center = check_spot(test_center)
                        if found_aabb:
                            final_aabb, final_center = found_aabb, found_center
                            break # Found a spot, stop searching this direction
                    if final_aabb:
                        break # Found a spot, stop searching all directions
            # --- MODIFICATION END ---

        if final_aabb is None:
            return False

        if final_center: # Ensure final_center is not None before proceeding
            rotated_offset = fixture.bounding_box.center.rotate(math.radians(angle_deg))
            final_insert_point = final_center - rotated_offset
            self.place_fixture(fixture, (final_insert_point.x, final_insert_point.y, 0), angle_deg, True)
            placed_bboxes.append((final_aabb.extmin.x, final_aabb.extmin.y, final_aabb.extmax.x, final_aabb.extmax.y))
            return True
        else:
            # This case might happen if check_spot returns a valid aabb but None for center, though unlikely.
            return False



    def _validate_and_place_at_point_euro_og(self, fixture, target_center, angle_deg, placed_bboxes, debug_draw=False, next_target_center: Optional[Vec2] = None):
        """
        [V4 - FINAL] Validates and places a fixture with two-tiered overlap rules:
        - ZERO TOLERANCE: Any overlap on the fixture's physical body is a failure.
        - TOLERANCE: Minor overlaps on the 1050mm clearance aisles are ignored.
        """
        from shapely.geometry import Polygon, box
        from ezdxf.math import Matrix44, BoundingBox2d
        import math

        # --- Internal helper function to check any given spot ---
        def check_spot(center_point):
            """
            [MODIFIED] Performs a two-step validation check.
            """
            OVERLAP_TOLERANCE_AREA = 60000.0 # 10cm x 10cm

            # 1. Calculate fixture's footprint (unchanged)
            transform = Matrix44.chain(
                Matrix44.translate(-fixture.bounding_box.center.x, -fixture.bounding_box.center.y, 0),
                Matrix44.z_rotate(math.radians(angle_deg)),
                Matrix44.translate(center_point.x, center_point.y, 0)
            )
            world_corners = list(transform.transform_vertices(fixture.bounding_box.rect_vertices()))
            current_aabb = BoundingBox2d(world_corners)
            fixture_polygon = Polygon([(p.x, p.y) for p in world_corners])

            # 2. Perform standard validation (is it inside the room?)
            is_inside = self.floorplan_polygon.buffer(-1.0).contains(fixture_polygon)
            if not is_inside:
                return None, None

            # --- NEW LOGIC: STEP 1 - Check Fixture Body with ZERO Tolerance ---
            is_body_overlapping = False
            for b in placed_bboxes:
                obstacle_poly = box(*b)
                # Use a simple, direct intersection check. Any overlap is a failure.
                if fixture_polygon.intersects(obstacle_poly):
                    is_body_overlapping = True
                    break
            
            if is_body_overlapping:
                return None, None # Fail immediately if the body is touched
            # --- END OF NEW LOGIC ---

            # 3. Perform special Euro Centre clearance validation
            if "euro_centre" in fixture.name.lower():
                clearance = 1050.0
                
                # --- NEW LOGIC: STEP 2 - Check Aisles WITH Tolerance ---
                # This helper function still uses the area tolerance
                def is_aisle_significantly_blocked(clearance_poly):
                    for b in placed_bboxes:
                        obstacle_poly = box(*b)
                        if clearance_poly.intersects(obstacle_poly):
                            intersection_area = clearance_poly.intersection(obstacle_poly).area
                            if intersection_area > OVERLAP_TOLERANCE_AREA:
                                return True # Aisle is significantly blocked
                    return False # Aisle is clear or only has minor overlaps

                if 85 < angle_deg < 95 or 265 < angle_deg < 275: # Rotated
                    left_aisle = box(current_aabb.extmin.x - clearance, current_aabb.extmin.y + 100, current_aabb.extmin.x, current_aabb.extmax.y - 100)
                    right_aisle = box(current_aabb.extmax.x, current_aabb.extmin.y + 100, current_aabb.extmax.x + clearance, current_aabb.extmax.y - 100)
                    if is_aisle_significantly_blocked(left_aisle) or is_aisle_significantly_blocked(right_aisle):
                        return None, None
                else: # Not rotated
                    top_aisle = box(current_aabb.extmin.x + 100, current_aabb.extmax.y, current_aabb.extmax.x - 100, current_aabb.extmax.y + clearance)
                    bottom_aisle = box(current_aabb.extmin.x + 100, current_aabb.extmin.y - clearance, current_aabb.extmax.x - 100, current_aabb.extmin.y)
                    if is_aisle_significantly_blocked(top_aisle) or is_aisle_significantly_blocked(bottom_aisle):
                        return None, None
                # --- END OF NEW LOGIC ---

            # If all checks pass, return the valid data.
            return current_aabb, center_point

        # --- Main Function Logic (This part remains unchanged) ---
        
        final_aabb, final_center = check_spot(target_center)

        if final_aabb is None:
            print(f"    -> Initial spot at ({target_center.x:.0f}, {target_center.y:.0f}) is blocked. Starting directional search...")
            
            primary_direction = None
            if next_target_center:
                direction_vector = (next_target_center - target_center).normalize()
                if abs(direction_vector.x) > abs(direction_vector.y):
                    primary_direction = Vec2(1, 0) if direction_vector.x > 0 else Vec2(-1, 0)
                    print(f"      -> Prioritizing search in HORIZONTAL direction towards next fixture.")
                else:
                    primary_direction = Vec2(0, 1) if direction_vector.y > 0 else Vec2(0, -1)
                    print(f"      -> Prioritizing search in VERTICAL direction towards next fixture.")

            if not primary_direction:
                is_rotated = 85 < angle_deg < 95 or 265 < angle_deg < 275
                primary_direction = Vec2(0, 1) if is_rotated else Vec2(1, 0)
                print(f"      -> No next target given. Falling back to default search based on rotation.")
            
            secondary_direction = primary_direction.orthogonal()
            reverse_primary = -primary_direction
            reverse_secondary = -secondary_direction
            search_vectors = [primary_direction, secondary_direction, reverse_secondary, reverse_primary]

            search_radius = 1000
            step = 50

            for move_vec in search_vectors:
                for i in range(1, int(search_radius / step) + 1):
                    offset_vec = move_vec * (i * step)
                    test_center = target_center + offset_vec
                    
                    found_aabb, found_center = check_spot(test_center)
                    if found_aabb:
                        print(f"    -> ✅ Found valid spot after nudging by ({offset_vec.x}mm, {offset_vec.y}mm). New center: ({found_center.x:.0f}, {found_center.y:.0f})")
                        final_aabb = found_aabb
                        final_center = found_center
                        break 
                if final_aabb:
                    break
        
        if final_aabb is None:
            return False

        if debug_draw:
            self._draw_euro_clearance_zones_for_validation(final_aabb, angle_deg)
        
        rotated_offset = fixture.bounding_box.center.rotate(math.radians(angle_deg))
        final_insert_point = final_center - rotated_offset
        self.place_fixture(fixture, (final_insert_point.x, final_insert_point.y, 0), angle_deg, True)
        
        placed_bboxes.append((final_aabb.extmin.x, final_aabb.extmin.y, final_aabb.extmax.x, final_aabb.extmax.y))
        
        return True

    def _draw_euro_clearance_zones_for_validation(self, aabb, angle_deg, layer_name="DEBUG_EURO_CLEARANCE", color=30):
        """
        [DEBUG HELPER] Draws the 1050mm customer clearance zones for a Euro Centre.
        """
        from shapely.geometry import box

        if layer_name not in self.doc.layers:
            self.doc.layers.add(name=layer_name, color=color) # ACI color 30 is a shade of orange

        clearance = 1050.0
        
        # Rotated (Column-wise): Access is left and right
        if 85 < angle_deg < 95 or 265 < angle_deg < 275:
            left_box = box(aabb.extmin.x - clearance, aabb.extmin.y + 100, aabb.extmin.x, aabb.extmax.y - 100)
            self.msp.add_lwpolyline(list(left_box.exterior.coords), close=True, dxfattribs={"layer": layer_name})

            right_box = box(aabb.extmax.x, aabb.extmin.y + 100, aabb.extmax.x + clearance, aabb.extmax.y - 100)
            self.msp.add_lwpolyline(list(right_box.exterior.coords), close=True, dxfattribs={"layer": layer_name})
            
        # Not rotated (Row-wise): Access is top and bottom
        else:
            top_box = box(aabb.extmin.x + 100, aabb.extmax.y, aabb.extmax.x - 100, aabb.extmax.y + clearance)
            self.msp.add_lwpolyline(list(top_box.exterior.coords), close=True, dxfattribs={"layer": layer_name})

            bottom_box = box(aabb.extmin.x + 100, aabb.extmin.y - clearance, aabb.extmax.x - 100, aabb.extmin.y)
            self.msp.add_lwpolyline(list(bottom_box.exterior.coords), close=True, dxfattribs={"layer": layer_name})
        


    #---------GRID-ZONE-FOR-MAX--EURO-CENTER-CALCULATION--PLACEMENT--SETUP---------------
    #---------GRID-ZONE-FOR-MAX--EURO-CENTER-CALCULATION--PLACEMENT--SETUP---------------
 

    
        
#---------------------new--setup-for-findong-area-for-euro-center-placement--
#---------------------new--setup-for-findong-area-for-euro-center-placement--



#---- CENTRAL FLOOR FIXTURE (EURO_CENTER,LENSBAR) PLACEMENT FUNCTION FINISHED ----


    


#-----------------------wall_fixture placement PLACEMENT FUNCTION STARTED------------------------------------------------------------------------------------
#-----------------------new  for wall_fixture placement---------------------------------------------------------------------------------------



        
    def _get_perimeter_path_from_bottom_left(self):
        """
        [CORRECTED] Finds the true bottom-left corner, reorders the perimeter,
        and now uses a direct vector check to GUARANTEE a counter-clockwise path
        that starts by moving UP the left wall.
        """
        print("  -> Dynamically finding bottom-left corner to start perimeter path...")
        corners = self.cvc.corners
        if not corners:
            return []

        # 1. Identify all wall segments on the "left" side (this logic is unchanged)
        left_wall_segments = []
        tolerance = (self.cvc.max_x - self.cvc.min_x) * 0.15
        for p1_coords, p2_coords in self.cvc.get_wall_segments():
            is_vertical = abs(p1_coords[0] - p2_coords[0]) < abs(p1_coords[1] - p2_coords[1])
            is_on_left = (p1_coords[0] + p2_coords[0]) / 2 < self.cvc.min_x + tolerance
            if is_vertical and is_on_left:
                left_wall_segments.append((Vec2(p1_coords), Vec2(p2_coords)))
        
        if not left_wall_segments:
            print("    -> ⚠️ Could not find a distinct left wall. Using default corner.")
            start_idx = 0
        else:
            # 2. Find the lowest point among all left-wall segments (unchanged)
            min_y = float('inf')
            start_point_vec = None
            for p1, p2 in left_wall_segments:
                if p1.y < min_y: min_y, start_point_vec = p1.y, p1
                if p2.y < min_y: min_y, start_point_vec = p2.y, p2
            start_idx = min(range(len(corners)), key=lambda i: start_point_vec.distance(Vec2(corners[i])))
            print(f"    -> True bottom-left start point found at index {start_idx}.")

        # 3. Reorder the corners to start from our identified point (unchanged)
        reordered = corners[start_idx:] + corners[:start_idx]
        
        # 4. NEW & IMPROVED: Direct check to ensure the path goes UP the left wall
        p1 = Vec2(reordered[0])
        p2 = Vec2(reordered[1])
        first_segment_vector = p2 - p1

        # Check if the vector is primarily horizontal (going right along the bottom wall)
        if first_segment_vector.x > abs(first_segment_vector.y):
             print("    -> Path is going right (Clockwise). Reversing to ensure it goes up the left wall.")
             # Reverse the list, keeping the start point fixed
             reordered = reordered[0:1] + reordered[1:][::-1]
        else:
             print("    -> Path is correctly going up the left wall (Counter-Clockwise).")

        # 5. Create the final path of wall segments (unchanged)
        perimeter_path = []
        for i in range(len(reordered)):
            p1_coords = reordered[i]
            p2_coords = reordered[(i + 1) % len(reordered)]
            if Vec2(p1_coords).distance(Vec2(p2_coords)) > 100:
                 perimeter_path.append((p1_coords, p2_coords))
        
        return perimeter_path
   
    def _get_perimeter_path_from_facade_left_start(self):
        """
        [NEW ROBUST METHOD]
        Identifies the "facade" wall (the segment that gets the bottom_epsilon)
        and starts a counter-clockwise perimeter path from its leftmost point.
        """
        import math
        from ezdxf.math import Vec2
        print("  -> Dynamically finding facade's left corner to start perimeter path...")

        corners = self.cvc.corners
        if len(corners) < 3:
            return []

        # --- Step 1: Isolate the logic to find the bottom/facade segment ---
        # This is the exact helper function used by offset_polygon_with_bottom_gap
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

        # --- Step 2: Find the facade segments and their points ---
        is_facade_segment = find_bottom_chain(corners, slope_tol=0.05, y_tol=100)
        facade_points = []
        for i, is_facade in enumerate(is_facade_segment):
            if is_facade:
                # Add both the start and end point of the facade segment
                facade_points.append(corners[i])
                facade_points.append(corners[(i + 1) % len(corners)])
        
        if not facade_points:
            print("    -> ⚠️ Could not identify a facade segment. Falling back to default corner.")
            start_idx = 0
        else:
            # --- Step 3: Identify the leftmost point of the facade ---
            leftmost_point = min(facade_points, key=lambda p: p[0])
            
            # --- Step 4: Find the index of this point in the original corners list ---
            start_idx = corners.index(leftmost_point)
            print(f"    -> True facade start point found at index {start_idx}.")

        # --- Step 5: Reorder and ensure counter-clockwise direction (same as original functions) ---
        reordered = corners[start_idx:] + corners[:start_idx]
        
        p1 = Vec2(reordered[0])
        p2 = Vec2(reordered[1])
        first_segment_vector = p2 - p1

        # If the path is going right (Clockwise), reverse it to go up (Counter-Clockwise).
        if first_segment_vector.x > abs(first_segment_vector.y):
            print("    -> Path is clockwise. Reversing to ensure it goes up the left wall.")
            reordered = reordered[0:1] + reordered[1:][::-1]
        else:
            print("    -> Path is correctly counter-clockwise (up the left wall).")

        # Create the final path of wall segments
        perimeter_path = []
        for i in range(len(reordered)):
            p1_coords = reordered[i]
            p2_coords = reordered[(i + 1) % len(reordered)]
            if Vec2(p1_coords).distance(Vec2(p2_coords)) > 100:
                perimeter_path.append((p1_coords, p2_coords))
        
        return perimeter_path
    
    def get_retail_boundary_y_og(self, side="0") -> float:
        """
        [MODIFIED] Finds the boundary for the retail wall space.
        PRIORITY 1: Uses the Y-coordinate of the 'RETAIL_SEPARATOR' line if it exists.
        PRIORITY 2 (Fallback): Finds the lowest Y-coordinate of the clinic/BOH cluster.
        """
        
        # --- NEW: PRIORITY 1 - Check for the RETAIL_SEPARATOR line first ---
        separator_line = self.msp.query('LINE[layer=="BOH_WALL_VALID_OUTLINE"]').first
        if separator_line:
            boundary_y = separator_line.dxf.start.y
            print(f"  -> Retail boundary defined by 'RETAIL_SEPARATOR' line at Y-coordinate: {boundary_y:.0f}")
            # For this function's logic, we don't need the side-specific value when the line is present.
            if side != "0":
                return boundary_y, boundary_y
            return boundary_y

        # --- FALLBACK: If no line is found, use the original fixture-based logic ---
        print("  -> 'RETAIL_SEPARATOR' line not found. Falling back to fixture-based boundary calculation.")
        stop_bboxes = self._get_accurate_obstacle_bboxes(include_all=False, debug=False)
        
        if not stop_bboxes:
            print("  -> No BOH/Clinic boundary found; entire wall length is available.")
            if side != "0":
                return self.cvc.max_y, self.cvc.max_y
            return self.cvc.max_y

        margin = 400.0
        side_min = self.cvc.max_y - margin  # Default to top of the floorplan

        if side != "0":
            if side == "right":
                print("RIGHT SIDE (Fallback)")
                x_val = max([b[2] for b in stop_bboxes])
                arr = [b[1] for b in stop_bboxes if abs(b[2] - x_val) < 200]
                if arr:
                    side_min = min(arr) - margin
            else: # side == "left"
                print("LEFT SIDE (Fallback)")
                x_val = min([b[0] for b in stop_bboxes])
                arr = [b[1] for b in stop_bboxes if abs(b[0] - x_val) < 200]
                if arr:
                    side_min = min(arr) - margin
        
        # The overall lowest_y is still needed for the general boundary
        lowest_y = min(b[1] for b in stop_bboxes)
        boundary_y = lowest_y - margin
        
        print(f"  -> Retail boundary calculated from fixtures at Y-coordinate: {boundary_y:.0f}")
        if side != "0":
            return boundary_y, side_min
        return boundary_y


    def get_retail_boundary_y_(self, side="0") -> float:
        """
        Finds the lowest Y-coordinate of the clinic/BOH cluster to determine
        the stop line for the retail wall space calculation.
        Now also includes short internal wall partitions as obstacles.
        """
        # Get standard obstacles
        stop_bboxes = self._get_accurate_obstacle_bboxes(include_all=False, debug=True)

        # --- NEW: Add short internal wall partitions as obstacles ---
        short_partitions = self.cvc.get_internal_wall_partitions(min_length=400, max_length=1600, thickness=0)
        if short_partitions:
            stop_bboxes.extend(short_partitions)
            print(f"  -> Added {len(short_partitions)} short internal wall partitions to stop_bboxes.")

        # --- PRIORITY 1: Check for the RETAIL_SEPARATOR line first ---
        separator_line = self.msp.query('LINE[layer=="BOH_WALL_VALID_OUTLINE"]').first
        if separator_line:
            boundary_y = separator_line.dxf.start.y
            print(f"  -> Retail boundary defined by 'RETAIL_SEPARATOR' line at Y-coordinate: {boundary_y:.0f}")
            if side != "0":
                return boundary_y, boundary_y   
            return boundary_y

        if not stop_bboxes:
            print("  -> No BOH/Clinic boundary found; entire wall length is available.")
            return self.cvc.max_y

        if side != "0":
            temp = stop_bboxes.pop()
            margin = 100.0 
            print(f"******************************************************************************************************************")
            print(f"******************************************************************************************************************")
            if side == "right":
                print("RIGHT SIDE")
                x_val = max([b[2] for b in stop_bboxes])
                arr = [b[1] for b in stop_bboxes if abs(b[2] - x_val) < 200]
                side_min = min(arr) - margin
            else:
                print("LEFT SIDE")
                x_val = min([b[0] for b in stop_bboxes])
                arr = [b[1] for b in stop_bboxes if abs(b[0] - x_val) < 200]
                side_min = min(arr) - margin

            print(f"x_val: {x_val}\narr: {arr}\nside_min: {side_min}")
            print(f"******************************************************************************************************************")
            print(f"******************************************************************************************************************")
            stop_bboxes.append(temp)

        lowest_y = min(b[1] for b in stop_bboxes)
        margin = 100.0 
        boundary_y = lowest_y - margin

        print(f"  -> Retail boundary line calculated at Y-coordinate: {boundary_y:.0f}")
        if side != 0:
            return boundary_y, side_min
        return boundary_y
    


    def get_retail_boundary_y(self, side="0") -> float:
        """
        Finds the lowest Y-coordinate of the clinic/BOH cluster to determine
        the stop line for the retail wall space calculation.
        """
        # This function reuses your existing logic to find only the 'stoppage' obstacles.
        stop_bboxes = self._get_accurate_obstacle_bboxes(include_all=False, debug=True)


        # --- NEW: PRIORITY 1 - Check for the RETAIL_SEPARATOR line first ---
        separator_line = self.msp.query('LINE[layer=="BOH_WALL_VALID_OUTLINE"]').first
        if separator_line:
            boundary_y = separator_line.dxf.start.y
            print(f"  -> Retail boundary defined by 'RETAIL_SEPARATOR' line at Y-coordinate: {boundary_y:.0f}")
            # For this function's logic, we don't need the side-specific value when the line is present.
            if side != "0":
                return boundary_y, boundary_y   
            return boundary_y
        
        if not stop_bboxes:
            print("  -> No BOH/Clinic boundary found; entire wall length is available.")
            # If no obstacles, return the top of the floorplan so the whole wall is measured.
            return self.cvc.max_y
        
        if side != "0":
            temp = stop_bboxes.pop()
            margin = 10.0 
            print(f"******************************************************************************************************************")
            print(f"******************************************************************************************************************")
            # The boundary is the lowest point of this cluster, minus a small margin.
            if side == "right":
                print("RIGHT SIDE")
                x_val = max([b[2] for b in stop_bboxes])
                arr = [b[1] for b in stop_bboxes if abs(b[2] - x_val) < 200]
                side_min = min(arr) - margin
            else:
                print("LEFT SIDE")
                x_val = min([b[0] for b in stop_bboxes])
                arr = [b[1] for b in stop_bboxes if abs(b[0] - x_val) < 200]
                side_min = min(arr) - margin

            
            print(f"x_val: {x_val}\narr: {arr}\nside_min: {side_min}")
            print(f"******************************************************************************************************************")
            print(f"******************************************************************************************************************")
            stop_bboxes.append(temp)

        lowest_y = min(b[1] for b in stop_bboxes)
        margin = 100.0 
        boundary_y = lowest_y - margin
        
        print(f"  -> Retail boundary line calculated at Y-coordinate: {boundary_y:.0f}")
        if side != 0:
            return boundary_y, side_min
        return boundary_y

    
    def _get_perimeter_path_from_bottom_right(self):
        """
        Helper to get a perimeter path starting from the bottom-right corner,
        ensuring a CLOCKWISE direction to walk up the right wall first.
        """
        corners = self.cvc.corners
        if not corners: return []
        
        # # Find the corner closest to the theoretical bottom-right
        # start_idx = min(range(len(corners)), 
        #                    key=lambda i: math.hypot(corners[i][0] - self.cvc.max_x, corners[i][1] - self.cvc.min_y))
        

        # --- MODIFIED: Use the exact same logic as find_right_wall_bottom_point() ---
        target_x, target_y = self.cvc.max_x, self.cvc.min_y
        bottom_right_corner = min(corners, 
                                key=lambda corner: math.hypot(corner[0] - target_x, corner[1] - target_y))
        
        # Find the index of this corner in the corners list
        start_idx = corners.index(bottom_right_corner)
        # --- END OF MODIFICATION ---
       
       
        reordered = corners[start_idx:] + corners[:start_idx]
        
        # Check winding order. A negative area means it's already Clockwise (CW).
        signed_area = 0.5 * sum(x1*y2 - x2*y1 for (x1, y1), (x2, y2) in zip(reordered, reordered[1:] + [reordered[0]]))
        
        # If the area is positive (Counter-Clockwise), we must reverse it.
        if signed_area < 0:
            print("  -> Path was clockwise, reversing to ensure it goes up the right wall.")

            reordered = reordered[0:1] + reordered[1:][::-1]
        
        perimeter_path = []
        for i in range(len(reordered)):
            p1_coords = reordered[i]
            p2_coords = reordered[(i + 1) % len(reordered)]
            if Vec2(p1_coords).distance(Vec2(p2_coords)) > 100:
                 perimeter_path.append((p1_coords, p2_coords))
        
        return perimeter_path

    def _get_perimeter_path_from_facade_right_start(self):
        """
        [CORRECTED ROBUST METHOD - RIGHT SIDE]
        Identifies the "facade" wall and starts a CLOCKWISE perimeter path
        from its rightmost point, ensuring the path moves UP the right wall first.
        """
        import math
        from ezdxf.math import Vec2
        print("  -> Dynamically finding facade's right corner to start clockwise path...")

        corners = self.cvc.corners
        if len(corners) < 3:
            return []

        # --- Step 1 & 2: Find the facade points (Logic is unchanged) ---
        def find_bottom_chain(pts, slope_tol=0.05, y_tol=100.0):
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

        is_facade_segment = find_bottom_chain(corners)
        facade_points = []
        for i, is_facade in enumerate(is_facade_segment):
            if is_facade:
                facade_points.append(corners[i])
                facade_points.append(corners[(i + 1) % len(corners)])
        
        if not facade_points:
            print("    -> ⚠️ Could not identify a facade segment. Falling back to default corner.")
            start_idx = min(range(len(corners)), 
                           key=lambda i: math.hypot(corners[i][0] - self.cvc.max_x, corners[i][1] - self.cvc.min_y))
        else:
            # --- Step 3 & 4: Find the rightmost point and its index (Logic is unchanged) ---
            rightmost_point = max(facade_points, key=lambda p: p[0])
            start_idx = corners.index(rightmost_point)
            print(f"    -> True facade end point (right side start) found at index {start_idx}.")

        # --- Step 5: Reorder and ensure CLOCKWISE direction using a vector check ---
        reordered = corners[start_idx:] + corners[:start_idx]
        
        p1 = Vec2(reordered[0])
        p2 = Vec2(reordered[1])
        first_segment_vector = p2 - p1

        # Check if the first step is LEFT along the facade (meaning the path is CCW).
        if first_segment_vector.x < -abs(first_segment_vector.y):
            print("    -> Path is counter-clockwise. Reversing to ensure clockwise path (up the right wall).")
            # Reverse the list, keeping the start point fixed, to make the path clockwise.
            reordered = reordered[0:1] + reordered[1:][::-1]
        else:
            print("    -> Path is correctly clockwise (up the right wall).")

        # Create the final path of wall segments
        perimeter_path = []
        for i in range(len(reordered)):
            p1_coords = reordered[i]
            p2_coords = reordered[(i + 1) % len(reordered)]
            if Vec2(p1_coords).distance(Vec2(p2_coords)) > 100:
                perimeter_path.append((p1_coords, p2_coords))
        
        return perimeter_path

    def draw_perimeter_paths_for_validation(self):
        """
        [DEBUG HELPER - UPDATED]
        Draws the perimeter paths but STOPS them at the RETAIL_SEPARATOR line.
        """
        import math
        from ezdxf.math import Vec2
        print("\n--- 🎨 Drawing Perimeter Paths for Validation (Stopping at Retail Line) ---")

        # --- NEW: Get the retail separation line's Y-coordinate ---
        separator_line = self.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
        stop_line_y = None
        if separator_line:
            stop_line_y = separator_line.dxf.start.y
            print(f"  -> Found RETAIL_SEPARATOR line at y={stop_line_y:.0f}. Paths will stop here.")
        else:
            print("  -> No RETAIL_SEPARATOR line found. Paths will be drawn fully.")

        # --- Get both paths ---
        left_path_segments = self._get_perimeter_path_from_facade_left_start()
        right_path_segments = self._get_perimeter_path_from_facade_right_start()

        # --- Define Layers ---
        left_layer = "DEBUG_PATH_LEFT_CCW"
        right_layer = "DEBUG_PATH_RIGHT_CW"
        
        if left_layer not in self.doc.layers:
            self.doc.layers.add(name=left_layer, color=4)  # Cyan
        
        if right_layer not in self.doc.layers:
            self.doc.layers.add(name=right_layer, color=6)  # Magenta

        # --- Draw Left (Counter-Clockwise) Path ---
        if left_path_segments:
            print(f"  -> Drawing Left Path ({len(left_path_segments)} segments) on layer '{left_layer}'")
            left_path_stopped = False
            for i, (p1_coords, p2_coords) in enumerate(left_path_segments):
                if left_path_stopped: break

                p1 = Vec2(p1_coords)
                p2 = Vec2(p2_coords)
                
                # --- NEW: Logic to check and trim the segment ---
                final_p1, final_p2 = p1, p2
                if stop_line_y is not None:
                    # Case 1: The entire segment is above the stop line (skip it)
                    if p1.y > stop_line_y and p2.y > stop_line_y:
                        continue
                    
                    # Case 2: The segment crosses the stop line
                    elif (p1.y < stop_line_y and p2.y > stop_line_y) or (p1.y > stop_line_y and p2.y < stop_line_y):
                        # Ensure p1 is the lower point for consistent calculation
                        if p1.y > p2.y: p1, p2 = p2, p1
                        
                        t = (stop_line_y - p1.y) / (p2.y - p1.y)
                        intersection_point = p1.lerp(p2, t)
                        final_p2 = intersection_point
                        left_path_stopped = True # Signal to stop after this segment
                
                # Draw the (potentially trimmed) segment
                self.msp.add_line(final_p1, final_p2, dxfattribs={"layer": left_layer, "lineweight": 50})
                
                # Add a numbered label to the (potentially trimmed) segment
                mid_point = final_p1.lerp(final_p2)
                self.msp.add_mtext(f"L-{i+1}", dxfattribs={'char_height': 150, 'insert': mid_point, 'layer': left_layer})

        # --- Draw Right (Clockwise) Path (with the same new logic) ---
        if right_path_segments:
            print(f"  -> Drawing Right Path ({len(right_path_segments)} segments) on layer '{right_layer}'")
            right_path_stopped = False
            for i, (p1_coords, p2_coords) in enumerate(right_path_segments):
                if right_path_stopped: break

                p1 = Vec2(p1_coords)
                p2 = Vec2(p2_coords)
                
                final_p1, final_p2 = p1, p2
                if stop_line_y is not None:
                    if p1.y > stop_line_y and p2.y > stop_line_y:
                        continue
                    elif (p1.y < stop_line_y and p2.y > stop_line_y) or (p1.y > stop_line_y and p2.y < stop_line_y):
                        if p1.y > p2.y: p1, p2 = p2, p1
                        t = (stop_line_y - p1.y) / (p2.y - p1.y)
                        intersection_point = p1.lerp(p2, t)
                        final_p2 = intersection_point
                        right_path_stopped = True

                self.msp.add_line(final_p1, final_p2, dxfattribs={"layer": right_layer, "lineweight": 50})
                mid_point = final_p1.lerp(final_p2)
                self.msp.add_mtext(f"R-{i+1}", dxfattribs={'char_height': 150, 'insert': mid_point, 'layer': right_layer})
    

    


    #----------------new_setup------------------------------------
    #----------------new_setup------------------------------------
    

    def get_retail_wall_data(self, side: str, internal_corners: list, corner_box_size: float = 250.0) -> dict:
        """
        [CORRECTED] Calculates retail wall data, subtracting space from segments that
        START at or END at an internal corner.
        """
        _, stop_line_y = self.get_retail_boundary_y(side=side)
        
        if side == 'left':
            perimeter_path = self._get_perimeter_path_from_facade_left_start()
        elif side == 'right':
            perimeter_path = self._get_perimeter_path_from_facade_right_start()
        else:
            return {"total_length": 0.0, "segments": {}}

        if not perimeter_path:
            return {"total_length": 0.0, "segments": {}}

        total_length = 0.0
        segments_data = {}
        segment_index = 0
        
        corner_points_set = {
            (round(c['point'][0]), round(c['point'][1])) for c in internal_corners
        }

        for p1_coords, p2_coords in perimeter_path:
            p1 = Vec2(p1_coords)
            p2 = Vec2(p2_coords)

            # Skip segments that are too short to begin with
            if p1.distance(p2) < 1030:
                continue
            
            if p1.y >= stop_line_y and p2.y >= stop_line_y:
                break
                
            # --- MODIFICATION START: Adjust start/end points based on corners ---
            effective_p1 = p1
            effective_p2 = p2
            segment_vector = (p2 - p1).normalize() # Unit vector for direction

            # Check if the segment STARTS at an internal corner
            if (round(p1.x), round(p1.y)) in corner_points_set:
                # Move the start point 250mm along the wall
                effective_p1 = p1 + segment_vector * corner_box_size
                print(f"  -> Segment {segment_index} starts at a corner. Adjusting start point.")

            # Check if the segment ENDS at an internal corner
            if (round(p2.x), round(p2.y)) in corner_points_set:
                # Move the end point 250mm back along the wall
                effective_p2 = p2 - segment_vector * corner_box_size
                print(f"  -> Segment {segment_index} ends at a corner. Adjusting end point.")
            # --- MODIFICATION END ---
            
            # All subsequent calculations will now use the "effective" points.
            p1, p2 = effective_p1, effective_p2

            # Handle segments that cross the BOH boundary (this logic is unchanged)
            if p1.y >= stop_line_y and p2.y >= stop_line_y:
                continue
            elif (p1.y < stop_line_y and p2.y > stop_line_y) or (p1.y > stop_line_y and p2.y < stop_line_y):
                if p1.y > p2.y: p1, p2 = p2, p1
                if (p2.y - p1.y) == 0: continue
                t = (stop_line_y - p1.y) / (p2.y - p1.y)
                if 0 <= t <= 1:
                    p2 = p1.lerp(p2, t)
                else: # The adjusted segment is now fully outside the retail zone
                    continue
            
            # Calculate the final, adjusted length
            final_segment_length = p1.distance(p2)
            if final_segment_length < 1030: # Check length again after adjustments
                continue
                
            total_length += final_segment_length
            
            segments_data[segment_index] = {
                "segment": (p1.x, p1.y, p2.x, p2.y), # Store the adjusted coordinates
                "length": final_segment_length,      # Store the adjusted length
                "angle": math.degrees(segment_vector.angle),
                "placement": " "
            }
            segment_index += 1
        
        print(f"  -> Found {len(segments_data)} retail segments on '{side}' side with a CORRECTED total length of {total_length:.0f} mm")
        
        return {
            "total_length": total_length,
            "segments": segments_data
        }

   
    
    #----------------NEW-DEV-FOR-INTERNAL-CORNERS-FUNCTION-----------------
    #----------------NEW-DEV-FOR-INTERNAL-CORNERS-FUNCTION-----------------
    # In DXF_Controller.py

    def find_internal_corners(self, wall_data: dict, side: str) -> list: # Add the 'side' parameter
        """
        Analyzes wall segments to find internal corners.
        - For 'left' side (CCW path), an internal corner is a right turn (~-90 deg).
        - For 'right' side (CW path), an internal corner is a left turn (~+90 deg).
        """
        internal_corners = []
        
        segments = sorted(wall_data["segments"].items())
        
        if len(segments) < 2:
            return []

        for i in range(len(segments) - 1):
            segment_a = segments[i][1]
            segment_b = segments[i+1][1]

            if segment_a["length"] > 1030 and segment_b["length"] > 1030:
                
                angle_difference = (segment_b["angle"] - segment_a["angle"] + 180) % 360 - 180

                # ***** MODIFICATION IS HERE *****
                is_internal_corner = False
                if side == 'left':
                    # A right turn (-90 deg) on a counter-clockwise path is an internal corner.
                    # if -95 < angle_difference < -85:
                    if -155 < angle_difference < -55:
                        is_internal_corner = True
                elif side == 'right':
                    # A left turn (+90 deg) on a clockwise path is an internal corner.
                    # if 85 < angle_difference < 95:
                    if 55 < angle_difference < 155:
                        is_internal_corner = True
                # ********************************

                if is_internal_corner:
                    corner_point = (segment_a["segment"][2], segment_a["segment"][3])
                    
                    corner_details = {
                        "point": corner_point,
                        "angle_in": segment_a["angle"],
                        "angle_out": segment_b["angle"]
                    }
                    
                    internal_corners.append(corner_details)
                    print(f"✅ Found an INTERNAL corner at {corner_point} (Side: {side}, Angle Change: {angle_difference:.1f}°)")
        
        return internal_corners

    

    def _build_fixture_pattern(self, num_lf: int, num_mf: int, num_mirrors: int, needs_starting_mirror: bool, segment_id: str, primary_side: str, segment_length: float,**kwargs) -> List[str]:
        """
        Builds a fixture pattern by creating a base layout and then inserting mirrors into available slots.

        Args:
            num_lf (int): Number of Large Fixtures.
            num_mf (int): Number of Medium Fixtures.
            num_mirrors (int): The total number of mirrors to place.
            needs_starting_mirror (bool): If True, a mirror is prepended to the pattern.

        Returns:
            List[str]: The generated fixture pattern.
        """
        print("\n--- 🛠️  Building Fixture Pattern ---")
        print(f"    Breakdown: {num_lf} LF, {num_mf} MF, {num_mirrors} mirrors")

        fixtures = ['LF'] * num_lf + ['MF'] * num_mf

        if not fixtures:
            return []

        # --- NEW CORRECTED LOGIC ---
        # 1. Create a base pattern with a minimal number of mirrors using a F-M-F-F-M... grouping.
        pattern = []
        # --- EDIT HERE: Handle starting mirror at the beginning ---
        internal_mirrors_target = num_mirrors
        
        internal_mirrors_target = num_mirrors

        if needs_starting_mirror and num_mirrors == 1 and (num_lf + num_mf) >= 3:
            fixtures = ['LF'] * num_lf + ['MF'] * num_mf
            # Take first two fixtures, then mirror, then rest
            pattern = ['M']
            pattern += fixtures[:2]
            pattern += ['M']
            pattern += fixtures[2:]
            print(f"    -> Applied custom start-mirror pattern: {pattern}")
            return pattern
        if internal_mirrors_target == 0 and segment_length > 1320:
            internal_mirrors_target += 1
            print("    -> No mirrors to place so adding a mirror to it .")
            # Note: No 'else: continue' is needed here as per Python flow logic
        if needs_starting_mirror:
            pattern.append('M')
            internal_mirrors_target -= 1 # One mirror is used, so reduce the target
            print(f"\n    STEP 0 (Start Mirror):")
            print(f"      -> Pattern: {pattern}")
            print(f"      -> Internal Mirrors to Place: {internal_mirrors_target}")

        

        # --- Build the base pattern with the remaining fixtures ---
        base_pattern_part = []

        fixture_queue = collections.deque(fixtures)
        
        if fixture_queue:
            # Start with F-M
            pattern.append(fixture_queue.popleft())
            if fixture_queue:
                pattern.append('M')
        
        # Continue with F-F-M
        while fixture_queue:
            pattern.append(fixture_queue.popleft())
            if fixture_queue:
                pattern.append(fixture_queue.popleft())
            if fixture_queue:
                pattern.append('M')
        # --- END OF CORRECTION ---

        # 2. Count how many mirrors we've placed vs. how many we need.
        pattern.extend(base_pattern_part)
        mirrors_placed = pattern.count('M')
        # mirrors_to_add = num_mirrors - mirrors_placed
        # --- AND EDIT HERE: Use the adjusted target for internal mirrors ---
        mirrors_to_add = internal_mirrors_target - (mirrors_placed - (1 if needs_starting_mirror else 0))

        
        print(f"\n    STEP 1 (Base Pattern):")
        print(f"      -> Pattern: {pattern}")
        print(f"      -> Mirrors Remaining to Place: {mirrors_to_add}")

        # # 3. Iteratively add the remaining mirrors into the first available F-F gaps.
        # if mirrors_to_add > 0:
        #     print(f"\n    STEP 2 (Insert Remaining Mirrors from Right):")
        #     # Start from the second-to-last element and iterate backwards.
        #     i = len(pattern) - 2
        #     iter_count = 1
        #     while i >= 0 and mirrors_to_add > 0:
        #         # Find a gap: a fixture followed by another fixture
        #         if pattern[i] in ['LF', 'MF'] and pattern[i+1] in ['LF', 'MF']:
        #             pattern.insert(i + 1, 'M')
        #             print(f"      ITER_{iter_count}: {pattern}")
        #             mirrors_to_add -= 1
        #             print(f"      Remaining: {mirrors_to_add}")
        #             iter_count += 1
        #             # No need for extra index adjustment, as we are moving backwards
        #             # and the insertion happens after the current index.
        #         i -= 1

        # 3. Iteratively add the remaining mirrors into the first available F-F gaps.
        if mirrors_to_add > 0:
            print(f"\n    STEP 2 (Insert Remaining Mirrors from Right):")
            # Start from the second-to-last element and iterate backwards.
            i = len(pattern) - 2
            iter_count = 1
            while i >= 0 and mirrors_to_add > 0:
                # Find a gap: a fixture followed by another fixture
                if pattern[i] in ['LF', 'MF'] and pattern[i+1] in ['LF', 'MF']:
                    pattern.insert(i + 1, 'M')
                    print(f"      ITER_{iter_count}: {pattern}")
                    mirrors_to_add -= 1
                    print(f"      Remaining: {mirrors_to_add}")
                    iter_count += 1
                    # No need for extra index adjustment, as we are moving backwards
                    # and the insertion happens after the current index.
                i -= 1

        # --- NEW LOGIC FOR SINGLE-FIXTURE EDGE CASE ---
        if mirrors_to_add > 0 and (num_lf + num_mf) == 1:
            print(f"\n    STEP 3 (Single Fixture Mirror Placement):")
            is_first_primary_segment = (segment_id == f"{primary_side}_segments_0")
            
            while mirrors_to_add > 0:
                if is_first_primary_segment:
                    pattern.insert(0, 'M')
                    print(f"      -> Placing mirror on LEFT for first primary segment: {pattern}")
                else:
                    pattern.append('M')
                    print(f"      -> Placing mirror on RIGHT for subsequent segment: {pattern}")
                mirrors_to_add -= 1
        # --- END OF NEW LOGIC ---
        
        # # 4. Handle the starting mirror flag
        # if needs_starting_mirror:
        #     # Avoid double mirrors at the start
        #     if not pattern or pattern[0] != 'M':
        #         pattern.insert(0, 'M')
        #         print(f"\n    STEP 3 (Add Start Mirror):")
        #         print(f"      -> Final Pattern: {pattern}")

        print(f"--- Pattern Build Complete ---")
        return pattern

    

    def generate_wall_fixture_plan(self, wall_segments_data: dict, display_calculations: dict, primary_side: str) -> dict:
        """
        Generates a wall fixture placement plan using a hierarchical, iterative fitting algorithm
        for each segment independently.
        """
        print(f"\n--- 📝 Generating Wall Fixture Plan (Iterative Segment Fitting) ---")

        # --- 1. Initialize Constants and State ---
        LF_LEN, MF_LEN, M_LEN = 1200, 1010, 300
        total_fixture_count = display_calculations.get('large_wall_fixtures', 0) + display_calculations.get('medium_wall_fixtures', 0)
        
        final_plan = {}
        overflow_display_fixture = 0
        
        if total_fixture_count == 0:
            print("  -> No wall fixtures to plan. Aborting.")
            return {}, 0

        # --- 2. Build the Processing Order Based on Primary Side ---
        left_keys = sorted([f"left_segments_{k}" for k in wall_segments_data.get("left_segments", {})])
        right_keys = sorted([f"right_segments_{k}" for k in wall_segments_data.get("right_segments", {})])
        
        processing_order = []
        transition_index = -1
        if primary_side == 'left':
            processing_order.extend(left_keys)
            processing_order.extend(right_keys)
            transition_index = len(left_keys)
        else:
            processing_order.extend(right_keys)
            processing_order.extend(left_keys)
            transition_index = len(right_keys)
        
        # --- 3. CALCULATE PROPORTIONAL CAPACITY (Largest Remainder Method) ---
        ordered_lengths = []
        for key in processing_order:
            side_name, seg_index_str = key.rsplit('_', 1)
            segment_data = wall_segments_data[side_name][int(seg_index_str)]
            ordered_lengths.append(segment_data['length'])

        total_wall_length = sum(ordered_lengths)
        capacities = {}

        if total_wall_length > 0 and total_fixture_count > 0:
            len_pct_arr = [length / total_wall_length for length in ordered_lengths]
            fixture_division_float = [p * total_fixture_count for p in len_pct_arr]
            final_fixture_counts = self._distribute_integers_largest_remainder(fixture_division_float, int(total_fixture_count))
            for i, key in enumerate(processing_order):
                side_name, seg_index_str = key.rsplit('_', 1)
                segment_data = wall_segments_data[side_name][int(seg_index_str)]
                capacities[key] = {'capacity': final_fixture_counts[i], 'data': segment_data}
        else:
            for key in processing_order:
                side_name, seg_index_str = key.rsplit('_', 1)
                segment_data = wall_segments_data[side_name][int(seg_index_str)]
                capacities[key] = {'capacity': 0, 'data': segment_data}

        print("\n  --- Calculated Segment Capacities ---")
        for segment_id, data in capacities.items():
            print(f"    -> Segment '{segment_id}': Capacity = {data['capacity']} fixtures")
        print("  ------------------------------------")

        # --- 4. NEW ALGORITHM: Process Each Segment Independently ---
        last_segment_ended_with = 'M'
        for i, segment_id in enumerate(processing_order):
            # Handle transition between primary and secondary walls
            if i == transition_index and transition_index > 0:
                print("    -> Transitioning to secondary wall. Resetting mirror logic.")
                last_segment_ended_with = 'M'

            segment_data = capacities[segment_id]
            segment_length = segment_data['data']['length']
            initial_capacity = segment_data['capacity']
            
            print(f"\n  -> Planning Segment '{segment_id}' (Length: {segment_length:.0f}mm, Initial Capacity: {initial_capacity} fixtures)")

            if initial_capacity == 0:
                final_plan[segment_id] = []
                print("    -> Skipping segment: Zero capacity.")
                continue

            # ...existing code...
            # --- Outer Loop for Fixture Reduction (Phase 3) ---
            n = initial_capacity
            segment_plan_found = False
            mirror_count = n - 1  # Initialize mirror_count here, outside the loop
            
            while n > 0:
                # Determine if a starting mirror is needed based on the previous segment
                needs_starting_mirror = last_segment_ended_with in ['LF', 'MF']
                starting_mirror_len = M_LEN if needs_starting_mirror else 0
                

                # --- Phase 1: Try swapping Large to Medium fixtures with current mirror count ---
                print(f"\n       -> 💡 PHASE 1: Trying fixture swaps with {mirror_count} mirrors")
                print(f"          Segment length: {segment_length:.0f}mm")
                
                phase1_success = False
                for swaps in range(n + 1):
                    num_lf, num_mf = n - swaps, swaps
                    
                    # Calculate if starting mirror is needed
                    needs_starting_mirror = (last_segment_ended_with in ['LF', 'MF'])
                    starting_mirror_len = M_LEN if needs_starting_mirror else 0
                    
                    total_length = (num_lf * LF_LEN) + (num_mf * MF_LEN) + (mirror_count * M_LEN) + starting_mirror_len
                    
                    print(f"          -> Testing swap: {num_lf} LF + {num_mf} MF + {mirror_count} M + {starting_mirror_len} start")
                    print(f"             Total: {total_length:.0f}mm vs limit {segment_length:.0f}mm", end="")
                    
                    if total_length <= segment_length:
                        print(" ✅ FITS!")
                        # Build the pattern
                        base_pattern = ['MF'] * num_mf + ['LF'] * num_lf
                        # final_pattern = []
                        final_pattern = self._build_fixture_pattern(
                                num_lf, num_mf, mirror_count, needs_starting_mirror,
                                segment_id=segment_id, primary_side=primary_side, segment_length=segment_length
                            )
                        final_plan[segment_id] = final_pattern
                        if needs_starting_mirror: 
                            final_pattern.append('M')
                            print(f"             -> Added starting mirror")
                        
                  
                        for k in range(n):
                                final_pattern.append(base_pattern[k])
                                if k < n - 1:
                                    final_pattern.append('M')
                            
                        
                        
                        final_pattern = self._build_fixture_pattern(
                            num_lf, num_mf, mirror_count, needs_starting_mirror, 
                            segment_id=segment_id, primary_side=primary_side,segment_length=segment_length
                        )
                            
                        final_plan[segment_id] = final_pattern
                        print(f"\n          -> ✅ PHASE 1 SUCCESS!")
                        print(f"             Pattern: {final_pattern}")
                        print(f"             Breakdown: {num_lf} LF, {num_mf} MF, {mirror_count} mirrors")
                        phase1_success = True
                        segment_plan_found = True
                        break
                    else:
                        print(" ❌ Too long")
                
                if phase1_success:
                    break

                # --- Phase 2: Mirror Reduction & Swap-Down ---
                print("    -> Phase 1 failed. Entering Phase 2 (Mirror Reduction)...")
                phase2_success = False
                
                # **CORRECTED MINIMUM MIRROR CALCULATION**
                min_mirrors_base = math.ceil(n / 2)
                min_mirrors = min_mirrors_base  if min_mirrors_base % 2 != 0 else min_mirrors_base
                
                print(f"       -> Minimum mirrors for {n} fixtures: {min_mirrors}")
                
                # Start reducing mirrors from current mirror_count
                starting_mirror_count_for_phase2 = min(mirror_count, n-1)
                
                print(f"\n       -> 🔍 DETAILED PHASE 2 TRACE for {n} fixtures:")
                print(f"       -> Starting with {starting_mirror_count_for_phase2} mirrors")
                print(f"       -> Will reduce down to minimum of {min_mirrors} mirrors")
                print(f"       -> Segment length available: {segment_length:.0f}mm")
                
                # --- FIX: Initialize current_mirrors before the loop ---
                current_mirrors = starting_mirror_count_for_phase2

                # **CRITICAL FIX: Build the removal pattern correctly**
                for current_mirrors in range(starting_mirror_count_for_phase2, min_mirrors - 1, -1):
                    if current_mirrors < 0:
                        continue
                    
                    # Calculate which position to remove based on the reduction step
                    steps_reduced = starting_mirror_count_for_phase2 - current_mirrors
                    remove_position = steps_reduced + 2  # Start from 2nd last, then 3rd last, etc.
                    
                    print(f"\n       -> 💡 TRYING: {current_mirrors} mirrors (step {steps_reduced + 1})")
                    print(f"          Removing {remove_position}th mirror from end")
                    
                    # Try swapping fixtures from all LF to all MF with this mirror count
                    for swaps in range(n + 1):
                        num_lf, num_mf = n - swaps, swaps
                        total_length = (num_lf * LF_LEN) + (num_mf * MF_LEN) + (current_mirrors * M_LEN) + starting_mirror_len
                        
                        print(f"          -> Testing swap combination: {num_lf} LF + {num_mf} MF + {current_mirrors} M")
                        print(f"             Total length: {total_length:.0f}mm (limit: {segment_length:.0f}mm)", end="")
                        
                        if total_length <= segment_length:
                            print(" ✅ FITS!")
                            base_pattern = ['MF'] * num_mf + ['LF'] * num_lf
                            final_pattern = []
                            if needs_starting_mirror: 
                                final_pattern.append('M')
                            
                            # **CORRECTED: Build pattern by removing specific mirror positions from the END**
                            # Calculate which positions to skip (count from the end)
                            positions_to_skip = set()
                            for step in range(steps_reduced):
                                position_from_end = step + 2  # 2nd last, 3rd last, etc.
                                actual_index = n - position_from_end  # Convert to index from start
                                if 0 <= actual_index < n - 1:
                                    positions_to_skip.add(actual_index)
                                    print(f"             -> Will SKIP mirror after fixture at index {actual_index} ({position_from_end}th from end)")
                            
                            print(f"\n          -> 🔨 BUILDING PATTERN:")
                            print(f"             Base fixtures: {base_pattern}")
                            print(f"             Positions to skip mirrors: {sorted(positions_to_skip)}")
                            
                            # Build the pattern with selective mirror placement
                            for k in range(n):
                                final_pattern.append(base_pattern[k])
                                print(f"             [{k}] Added fixture: {base_pattern[k]}", end="")
                                
                                if k < n - 1:
                                    if k not in positions_to_skip:
                                        final_pattern.append('M')
                                        print(" + Mirror ✓")
                                    else:
                                        print(" (Mirror SKIPPED)")
                                else:
                                    print("")

                            final_pattern = self._build_fixture_pattern(num_lf, num_mf, current_mirrors, needs_starting_mirror, segment_id=segment_id, primary_side=primary_side,segment_length=segment_length)

                            print(f"\n          -> ✅ FINAL PATTERN CREATED:")
                            print(f"             {final_pattern}")
                            print(f"             Breakdown: {num_lf} LF, {num_mf} MF, {current_mirrors} mirrors")
                            print(f"             Pattern length: {len([x for x in final_pattern if x != 'M'])} fixtures, {len([x for x in final_pattern if x == 'M'])} mirrors")
                            
                            final_plan[segment_id] = final_pattern
                            print(f"\n    -> ✅ SUCCESS (Phase 2): Segment solved!")
                            phase2_success = True
                            mirror_count = current_mirrors
                            break
                        else:
                            print(" ❌ Too long")
                    
                    if phase2_success:
                        break
                
                # Update mirror_count even if Phase 2 failed
                if not phase2_success:
                    mirror_count = min_mirrors - 1
                    print(f"\n       -> ⚠️ Phase 2 exhausted all options.")
                    print(f"          Setting mirror_count to {mirror_count} for next iteration.")
                
                if phase2_success:
                    segment_plan_found = True
                    break

                # --- Phase 3: Fixture Reduction ---
                print(f"\n    -> ⚠️ Phase 2 failed for n={n}. Entering Phase 3 (Fixture Reduction)...")
                print(f"       -> Reducing fixture count from {n} to {n-1}")
                print(f"       -> Overflow count increases by 1 (now {overflow_display_fixture + 1})")
                print(f"       -> This fixture will be marked as overflow for later handling")
                
                n -= 1
                overflow_display_fixture += 1
                

                
            if not segment_plan_found:
                print(f"    -> ❌ FAILED: Could not fit any fixtures in this segment.")
                final_plan[segment_id] = []
            
            # Update the flag for the next segment
            last_segment_ended_with = final_plan.get(segment_id, ['M'])[-1] if final_plan.get(segment_id) else 'M'
            # ...existing code...

        # --- 5. Finalize and Return Plan ---
        print("\n--- ✅ Wall Fixture Plan Generation Complete ---")
        if overflow_display_fixture > 0:
            print(f"  -> INFO: {overflow_display_fixture} fixtures could not be planned due to space constraints (overflow).")

        print("  -> 🔄 Merging fixture plan with segment data for final output...")
        placement_dict = {}
        for segment_key, fixture_list in final_plan.items():
            try:
                side_name, seg_index_str = segment_key.rsplit('_', 1)
                seg_index = int(seg_index_str)
                if side_name not in placement_dict:
                    placement_dict[side_name] = {}
                if side_name in wall_segments_data and seg_index in wall_segments_data[side_name]:
                    original_segment_data = wall_segments_data[side_name][seg_index].copy()
                    original_segment_data["placement"] = fixture_list
                    placement_dict[side_name][seg_index_str] = original_segment_data
            except (ValueError, KeyError):
                continue
            
        return placement_dict, overflow_display_fixture
    
    def _distribute_integers_largest_remainder(self, float_values: List[float], total_sum: int) -> List[int]:
        """
        Distributes a total sum across a list of floats, converting them to integers
        while ensuring the final sum is correct, using the Largest Remainder Method.

        Args:
            float_values: A list of floating-point numbers (e.g., [2.8, 2.1, 2.1]).
            total_sum: The exact integer sum the final list must have (e.g., 7).

        Returns:
            A list of integers that sum up to total_sum.
        """
        # Step 1: Initial allocation using the integer part of each float.
        allocations = [int(v) for v in float_values]
        
        # Step 2: Calculate how many items are "leftover" after the initial allocation.
        remainder_to_distribute = total_sum - sum(allocations)
        
        # Step 3: Create a list of the fractional parts (the remainders) with their original index.
        remainders = [(i, float_values[i] - allocations[i]) for i in range(len(float_values))]
        
        # Step 4: Sort this list by the fractional part, from largest to smallest.
        remainders.sort(key=lambda x: x[1], reverse=True)
        
        # Step 5: Distribute the leftover items, one by one, to the allocations with the largest fractions.
        for i in range(remainder_to_distribute):
            # Get the index of the item with the next-largest fraction.
            index_to_increment = remainders[i][0]
            # Add 1 to its allocation.
            allocations[index_to_increment] += 1
            
        return allocations

    
    
    
    def place_fixtures_from_plan(self, placement_dict: dict, placed_bboxes: list):
        """
        Places wall fixtures, respects JJ->VC priority, mirrors on the right wall,
        and now appends the bounding boxes of placed fixtures to the master list to prevent overlaps.
        """
        # from Fixture import Fixture
        from shapely.geometry import Point
        from ezdxf.math import Vec2, Matrix44, BoundingBox2d
        import math

        print("\n--- 🏗️ Executing Wall Fixture Placement (JJ -> VC Priority & Right Wall Mirroring) ---")

        # 1. Get family counts from the merch mix (unchanged)
        family_totals = self.family_totals
        jj_family_key = next((key for key in family_totals if 'jj' in key), None)
        jj_family_count = family_totals.get(jj_family_key, 0)
        vc_family_count = family_totals.get('vc_fixture_family', 0)

        print(f"\n  -> Placement Priority based on Merch Mix:")
        print(f"     JJ Family Fixtures to Place: {jj_family_count}")
        print(f"     VC Family Fixtures to Place: {vc_family_count}")

        # 2. Setup counters and mirror selection (unchanged)
        jj_fixtures_placed = 0
        mirror_config = self.fixtures.get("mirror_selection", {})
        selected_mirror_name = next((name for name, selected in mirror_config.items() if selected > 0), "mirror")
        print(f"  -> Using '{selected_mirror_name}' for all mirror placements.")

        # Helper function for priority logic (unchanged)
        def get_next_fixture_name(code):
            nonlocal jj_fixtures_placed
            if jj_fixtures_placed < jj_family_count:
                jj_fixtures_placed += 1
                return 'jj_fixture_large' if code == 'LF' else 'jj_fixture_medium'
            else:
                return 'vc_fixture_large' if code == 'LF' else 'vc_fixture_medium'
            return None

        # 3. Main placement loop
        for side_key, segments in placement_dict.items():
            
            is_right_wall = "right" in side_key
            if is_right_wall:
                print(f"\n  -> Placing and MIRRORING fixtures on '{side_key}'...")
            else:
                print(f"\n  -> Placing fixtures on '{side_key}'...")

            for seg_index, segment_data in sorted(segments.items(), key=lambda item: int(item[0])):
                seg_coords = segment_data['segment']
                p1 = Vec2(seg_coords[0], seg_coords[1])
                p2 = Vec2(seg_coords[2], seg_coords[3])
                wall_vector = (p2 - p1).normalize()
                wall_angle_deg = math.degrees(wall_vector.angle)

                # (Robust inward_normal calculation is unchanged)
                inward_normal = wall_vector.orthogonal().normalize()
                mid_point_on_wall = p1.lerp(p2)
                test_point = mid_point_on_wall + inward_normal * 10
                if not self.floorplan_polygon.contains(Point(test_point)):
                    inward_normal *= -1

                pattern = segment_data.get('placement', [])
                if not pattern:
                    continue
                print(f"    -> Segment {seg_index}: Placing pattern {pattern}")
                cursor = 0.0
                margin_from_wall = 1.0

                for fixture_code in pattern:
                    fixture_name = None
                    if fixture_code == 'M':
                        fixture_name = selected_mirror_name
                    elif fixture_code in ['LF', 'MF']:
                        fixture_name = get_next_fixture_name(fixture_code)
                    if not fixture_name:
                        continue
                    try:
                        fxtr = Fixture.Fixture(fixture_name, self.fixture_dict[fixture_name]["path"])
                    except Exception as e:
                        continue
                    if cursor + fxtr.width > segment_data['length'] + 50:
                        break

                    xscale = 1.0 if is_right_wall else 1.0
                    yscale = -1.0 if is_right_wall else 1.0

                    center_on_wall = p1 + wall_vector * (cursor + fxtr.width / 2.0)
                    offset_from_wall = margin_from_wall + fxtr.height / 2.0
                    target_center = center_on_wall + inward_normal * offset_from_wall

                    local_center = fxtr.bounding_box.center
                    local_center_scaled = Vec2(local_center.x * xscale, local_center.y * yscale)
                    rotated_offset = local_center_scaled.rotate(math.radians(wall_angle_deg))
                    final_insert_point = target_center - rotated_offset

                    # --- Place the Fixture ---
                    self.place_fixture(
                        fxtr,
                        (final_insert_point.x, final_insert_point.y, 0),
                        wall_angle_deg,
                        rotated=True,
                        xscale=xscale,
                        yscale=yscale
                    )

                    # *** NEW: Calculate and append the bounding box to the master list ***
                    transform = Matrix44.chain(
                        Matrix44.translate(-local_center.x, -local_center.y, 0),
                        Matrix44.scale(xscale, yscale, 1.0),
                        Matrix44.z_rotate(math.radians(wall_angle_deg)),
                        Matrix44.translate(target_center.x, target_center.y, 0)
                    )
                    world_corners = list(transform.transform_vertices(fxtr.bounding_box.rect_vertices()))
                    aabb = BoundingBox2d(world_corners)
                    new_bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)

                    # Add the new bounding box to the master list of obstacles.
                    placed_bboxes.append(new_bbox_tuple)
                    # *** END NEW SECTION ***

                    cursor += fxtr.width

        print("\n--- ✅ Finished placing all wall fixtures from the plan. ---")

    

    def draw_corner_dummy_boxes(self, corners: list, placed_bboxes: list, size: float = 250.0, layer_name: str = "CORNER_DUMMY_BOX", draw_visual: bool = True):
        """
        [MODIFIED] Calculates a square box for an internal corner and registers it as an obstacle.
        Optionally draws the box on a specified layer for debugging.
        """
        if not corners:
            return

        if draw_visual:
            print(f"\n--- 🎨 Drawing and Registering {len(corners)} Dummy Boxes ---")
            if layer_name not in self.doc.layers:
                self.doc.layers.add(name=layer_name, color=1) # Red
        else:
            print(f"\n--- 🚧 Registering {len(corners)} Internal Corner Obstacles (no drawing) ---")

        for corner_data in corners:
            from ezdxf.math import Vec2
            import math
            p_corner = Vec2(corner_data['point'])
            v_in = Vec2.from_angle(math.radians(corner_data['angle_in'] + 180))
            v_out = Vec2.from_angle(math.radians(corner_data['angle_out']))
            
            # Define the points of the box
            p1 = p_corner + v_in.normalize() * size
            p2 = p_corner + v_out.normalize() * size
            p3 = p_corner + v_in.normalize() * size + v_out.normalize() * size
            points = [p_corner, p1, p3, p2]
            
            # Optionally draw the box
            if draw_visual:
                self.msp.add_lwpolyline(
                    points,
                    close=True,
                    dxfattribs={"layer": layer_name}
                )

            # Always register the box as an obstacle
            min_x = min(p.x for p in points)
            min_y = min(p.y for p in points)
            max_x = max(p.x for p in points)
            max_y = max(p.y for p in points)
            bbox = (min_x, min_y, max_x, max_y)
            
            placed_bboxes.append(bbox)
            
            if draw_visual:
                print(f"  -> Drew dummy box and registered obstacle at ({p_corner.x:.0f}, {p_corner.y:.0f})")

    def plan_and_place_wall_fixtures(self, all_placed_bboxes: list, primary_side: str, draw_debug: bool = False):
        """
        Orchestrates the entire wall fixture planning and placement process.
        - Finds internal corners to correctly calculate wall lengths.
        - Generates a fixture plan based on available space and merchandise mix.
        - Places the fixtures from the generated plan.
        - Optionally draws debug geometry for validation.
        - RETURNS: The number of remaining (unplaced) wall fixtures and the display calculations.
        """
        import json
        print("\n--- 🚀 Orchestrating Wall Fixture Planning and Placement ---")

        # 1. Find corners for BOTH sides first.
        right_wall_raw_data = self.get_retail_wall_data(side='right', internal_corners=[])
        internal_corners_on_right_wall = self.find_internal_corners(right_wall_raw_data, side='right')

        left_wall_raw_data = self.get_retail_wall_data(side='left', internal_corners=[])
        internal_corners_on_left_wall = self.find_internal_corners(left_wall_raw_data, side='left')

        # 2. Register internal corners as obstacles (and optionally draw them).
        if internal_corners_on_right_wall:
            if draw_debug:
                print("\n[DEBUG] Detected Internal Corners on the Right Wall:")
                for corner in internal_corners_on_right_wall:
                    print(f"  - Corner at: {corner['point']}, Angle In: {corner['angle_in']:.1f}°, Angle Out: {corner['angle_out']:.1f}°")
            self.draw_corner_dummy_boxes(internal_corners_on_right_wall, all_placed_bboxes, layer_name="DEBUG_INTERNAL_CORNERS", draw_visual=draw_debug)

        if internal_corners_on_left_wall:
            if draw_debug:
                print("\n[DEBUG] Detected Internal Corners on the Left Wall:")
                for corner in internal_corners_on_left_wall:
                    print(f"  - Corner at: {corner['point']}, Angle In: {corner['angle_in']:.1f}°, Angle Out: {corner['angle_out']:.1f}°")
            self.draw_corner_dummy_boxes(internal_corners_on_left_wall, all_placed_bboxes, layer_name="DEBUG_INTERNAL_CORNERS", draw_visual=draw_debug)

        # 3. Now, get the CORRECTED wall data by passing the corners you just found.
        right_wall_data = self.get_retail_wall_data(side='right', internal_corners=internal_corners_on_right_wall)
        left_wall_data = self.get_retail_wall_data(side='left', internal_corners=internal_corners_on_left_wall)
        
        if draw_debug:
            print("\n--- [DEBUG] Right Wall Data ---")
            print(json.dumps(right_wall_data, indent=4))
            print("\n--- [DEBUG] Left Wall Data ---")
            print(json.dumps(left_wall_data, indent=4))

        # 4. The rest of the planning logic now uses the CORRECTED data.
        left_wall_length = left_wall_data["total_length"]
        right_wall_length = right_wall_data["total_length"]
        total_retail_wall_length = left_wall_length + right_wall_length
        print(f"\nLeft wall length: {left_wall_length:.0f} mm, Right wall length: {right_wall_length:.0f} mm, Total: {total_retail_wall_length:.0f} mm")
        
        if primary_side == "right":
            all_wall_segments = {
                "right_segments": right_wall_data["segments"],
                "left_segments": left_wall_data["segments"]
            }
        else: # When primary_side == 'left'
            all_wall_segments = {
                "left_segments": left_wall_data["segments"],
                "right_segments": right_wall_data["segments"]
            }

        # 5. Generate and execute the placement plan.
        display_calcs = self.display_count_calc(floor_area=0, wall_length=total_retail_wall_length, display_count=0) 
        placement_dict, remaining_wall_fixtures = self.generate_wall_fixture_plan(
            wall_segments_data=all_wall_segments,
            display_calculations=display_calcs,
            primary_side=primary_side
        )

        print("\nRemaining wall fixtures after wall plan generation: ", remaining_wall_fixtures)
        self.place_fixtures_from_plan(placement_dict, all_placed_bboxes)
        
        if draw_debug:
            self.draw_perimeter_paths_for_validation()
        
        print("--- ✅ Wall Fixture Placement Complete ---")
        
        # Return the values needed by the next function
        return remaining_wall_fixtures, display_calcs


    # Now, ADD this new method to your DXF_Controller class for Euro Centers.

    def plan_and_place_euro_fixtures(self, all_placed_bboxes: list, remaining_wall_fixtures: int, display_calcs: dict, draw_debug: bool = False):
        """
        Orchestrates the planning and placement of Euro Center fixtures, accounting for
        any overflow from the wall fixture placement.
        """
        print("\n--- 🚀 Orchestrating Euro Center Fixture Planning and Placement ---")
        
        # 1. Define placement zone (and optionally draw it for debugging)
        # This call is necessary as it defines the zone used by the analysis functions.
        self.euro_center_placement_area() 
        if draw_debug:
            self.draw_euro_center_placement_zone()
            # --- Generate and draw the ROW-WISE grid (0° Rotation) ---
            row_wise_coords = self.generate_row_wise_grid()
            self.draw_grid_for_validation(
                grid_points=row_wise_coords,
                cell_width=1040.0,
                cell_height=1175.0,
                layer_name="DEBUG_GRID_ROW_WISE",
                color=3  # Green
            )

            # # --- Generate and draw the COLUMN-WISE grid (90° Rotation) ---
            column_wise_coords = self.generate_column_wise_grid()
            self.draw_grid_for_validation(
                grid_points=column_wise_coords,
                cell_width=1175.0,
                cell_height=1040.0,
                layer_name="DEBUG_GRID_COLUMN_WISE",
                color=4  # Cyan
            )


        # 2. Update floor fixture count with overflow from wall fixtures
        print(f"  -> Adding {remaining_wall_fixtures} remaining wall fixtures to the floor fixture count.")
        display_calcs['floor_fixtures'] = display_calcs.get('floor_fixtures', 0) + remaining_wall_fixtures
        print(f"  -> New total floor fixtures required: {display_calcs['floor_fixtures']}")

        # 3. Analyze placement patterns and place the fixtures
        placement_blueprint = self.analyze_placement_patterns()
        self.place_euro_centers_from_blueprint(placement_blueprint, display_calcs, all_placed_bboxes)
        
        print("--- ✅ Euro Center Placement Complete ---")
    

#-----------------------wall_fixture placement PLACEMENT FUNCTION FINISED HERE------------------------------------------------------------------------------------


# CATEGORY :- REMAINING FLOOR FIXTURES

#---- DISCUSSION TABLE PLACEMENT FUNCTION STARTED ----

    def place_discussion_tables_attached_to_euros(self, placed_bboxes):
        """
        Finds all placed Euro_centre fixtures and attaches discussion tables based on a
        simplified count. It automatically alternates placement on the left and right
        sides for each subsequent Euro_centre.
        """
        # from Fixture import Fixture
        from ezdxf.bbox import extents
        from shapely.geometry import box
        import collections

        print("\n--- Attaching Discussion Tables with new Alternating Logic ---")

        placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)

        # 1. Find all Euro_centre fixtures, same as before
        euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
        if not euro_entities:
            print("ℹ️ No Euro_centre fixtures found to attach tables to. Skipping.")
            return

        euro_entities.sort(key=lambda e: e.dxf.insert.y)

        # 2. NEW: Build a master placement queue from the simplified configuration
        placement_queue = collections.deque()
        # You can use "floor_fixtures" or "floor_fixtures_portrait" as the source
        config = self.fixtures.get("floor_fixtures_table", {}) 
        table_types = ["large", "medium", "small"]

        for table_type in table_types:
            # Construct key like "Discussion_table_medium"
            config_key = f"Discussion_table_{table_type}"
            count = config.get(config_key, 0)
            
            # Add a job for each table, alternating the side
            for i in range(count):
                side = "left" if i % 2 == 0 else "right"
                placement_queue.append({'type': table_type, 'side': side})
        
        if not placement_queue:
            print("ℹ️ No discussion tables specified in the configuration.")
            return
            
        print(f"  -> Generated a placement queue for {len(placement_queue)} tables.")

        # 3. Process the queue and attach tables sequentially
        placed_count = 0
        for i, job in enumerate(placement_queue):
            # Determine which Euro Centre to use. This ensures we fill up
            # Euro #1 (left and right) before moving to Euro #2.
            euro_index = i // 2
            
            if euro_index >= len(euro_entities):
                print(f"⚠️ Ran out of Euro Centres to attach the remaining {len(placement_queue) - i} tables to.")
                break
            
            euro_entity = euro_entities[euro_index]
            table_type = job['type']
            side = job['side']

            print(f"    -> Attempting to place a '{table_type}' table on the '{side}' of Euro Centre #{euro_index + 1}...")
            
            try:
                table_fixture_name = f"Discussion_table_{table_type}"
                table_fxtr = Fixture.Fixture(self.fixture_dict[table_fixture_name]["name"],
                                     self.fixture_dict[table_fixture_name]["path"])
            except Exception as e:
                print(f"    🔥 Could not load fixture for '{table_fixture_name}': {e}")
                continue

            euro_bbox = extents([euro_entity], fast=True)
            gap = 1

            
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
                if rotation == 270:
                    final_insert_point = (insert_x, insert_y + table_fxtr.width, 0)
                else: # rotation == 90
                    # final_insert_point = (insert_x + table_fxtr.height, insert_y, 0)
                    final_insert_point = (insert_x, insert_y, 0)

                self.place_fixture(table_fxtr, final_insert_point, rotation, True)
                placed_bboxes.append((x1, y1, x2, y2))
                print(f"      ✅ Success.")
                placed_count += 1
            else:
                print(f"      ⚠️ Spot was blocked or outside boundary.")

        
        if placed_count < len(placement_queue):
            print(f"\n⚠️ Warning: Placed only {placed_count} of {len(placement_queue)} requested discussion tables.")

    
#---- DISCUSSION TABLE PLACEMENT FUNCTION FINISHED ----

#---- POS/AR PLACEMENT FUNCTION STARTED ----

        
    def _get_boh_zone_polygon(self) -> Optional[Polygon]:
        """
        Finds all BOH wall outlines and merges them into a single Shapely Polygon.
        This represents the total area occupied by the BOH room.
        """
        from shapely.ops import unary_union
        from shapely.geometry import Polygon

        # --- FIX: Use a more robust, two-step query to avoid regex errors ---
        # Step 1: Get all polylines without a complex filter.
        all_polylines = self.msp.query('LWPOLYLINE')
        
        # Step 2: Filter them in Python, which is safer than a complex query string.
        boh_outlines = [
            p for p in all_polylines 
            if "BOH_WALL_" in p.dxf.layer and p.dxf.layer.endswith("_OUTLINE")
        ]
        # --- END OF FIX ---
        
        if not boh_outlines:
            return None

        polygons = [Polygon(list(p.get_points('xy'))) for p in boh_outlines]
        
        # Merge all found polygons into a single shape
        boh_zone = unary_union(polygons)
        
        return boh_zone if not boh_zone.is_empty else None
    
    def place_pos_ar_portrait_dynamically(self, placed_bboxes):
        """
        Places the POS and AR group using a resilient, iterative search strategy.
        - If POS is not selected, it places the AR unit by itself using a robust,
          BOH-AWARE, multi-strategy approach anchored to clinics.
        - FINAL FALLBACK: Places AR below the Pick_up_window if all else fails.
        """
        # --- DIAGNOSTIC PRINT TO CONFIRM THIS IS THE LATEST VERSION ---
        print("\n\n>>>> RUNNING THE NEWEST VERSION OF THE FUNCTION (WITH SPACE FIX) <<<<\n\n")
        # --- END DIAGNOSTIC ---

        from shapely.geometry import box, LineString, Point
        from ezdxf.bbox import extents
        from ezdxf.math import BoundingBox2d, Vec2
        import collections

        try:
            # --- 1. SETUP: Load fixtures and check for POS selection ---
            pos_config = self.fixtures.get("POS", {})
            selected_pos_name = next((name for name, selected in pos_config.items() if selected > 0), None)
            ar_fxtr = Fixture.Fixture("AR", self.fixture_dict["AR"]["path"])
            placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)

            # --- STRATEGY 1: Place POS + AR Group ---
            if selected_pos_name:
                print("\n--- 🧠 Placing POS/AR with Dynamic Iterative Strategy ---")
                pos_fxtr = Fixture.Fixture(selected_pos_name, self.fixture_dict[selected_pos_name]["path"])
                gap_between = 100
                total_group_width = pos_fxtr.width + gap_between + ar_fxtr.width
                max_group_height = max(pos_fxtr.height, ar_fxtr.height)
                anchor_y = 0
                anchor_fixtures = [e for e in self.msp.query('INSERT') if "CORIAN_TABLE" in e.dxf.name.upper() or "LOUNGE_SEAT" in e.dxf.name.upper()]
                if not anchor_fixtures:
                    anchor_fixtures = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
                if anchor_fixtures:
                    anchor_y = extents(anchor_fixtures).extmax.y
                    print(f"  -> Found anchor point at y={anchor_y:.0f}")
                else:
                    anchor_y = self.cvc.min_y + (self.cvc.max_y - self.cvc.min_y) * 0.6
                    print(f"  -> No primary anchors found. Using fallback y={anchor_y:.0f}")
                
                standing_table_count = self.fixtures.get("table_fixtures", {}).get("Standing_table", 0)
                gap_above_anchor = 2000.0 if standing_table_count > 0 else 300.0
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

            # --- BOH-AWARE STRATEGY FOR AR-ONLY PLACEMENT ---
            else:
                print("\n--- 🧠 Placing AR Only (BOH-Aware with Fallback) ---")
                is_placed = False
                
                boh_zone_poly = self._get_boh_zone_polygon()
                if boh_zone_poly:
                    print("  -> BOH zone identified. AR will not be placed inside it.")
                
                clinic_bboxes = self._get_clinic_bboxes_new(buffer=0)
                if not clinic_bboxes:
                    print("⚠️ No clinic fixtures found to anchor AR placement.")
                    return

                # --- STRATEGY 1: Place vertically near clinics ---
                sorted_clinics = sorted(clinic_bboxes, key=lambda b: b[0])
                for bbox in sorted_clinics:
                    clinic_bbox = BoundingBox2d([(bbox[0], bbox[1]), (bbox[2], bbox[3])])
                    rotated_width, rotated_height = ar_fxtr.height, ar_fxtr.width
                    x_pos = clinic_bbox.extmin.x - 100.0 - rotated_width
                    y_pos = clinic_bbox.center.y - (rotated_height / 2)
                    candidate_box = box(x_pos, y_pos, x_pos + rotated_width, y_pos + rotated_height)
                    is_in_boh = boh_zone_poly.intersects(candidate_box) if boh_zone_poly else False
                    if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in placed_bboxes) and not is_in_boh:
                        insert_point = (x_pos + rotated_width, y_pos, 0)
                        self.place_fixture(ar_fxtr, insert_point, 90, True)
                        placed_bboxes.append(candidate_box.bounds)
                        print(f"    ✅ SUCCESS: Placed 'AR' vertically near a clinic.")
                        is_placed = True
                        break
                
                # --- STRATEGY 2: Try top/bottom sides of every clinic ---
                if not is_placed:
                    aisle_gap = 200.0
                    for bbox in sorted_clinics:
                        if is_placed: break
                        clinic_bbox = BoundingBox2d([(bbox[0], bbox[1]), (bbox[2], bbox[3])])
                        spots_to_try = [
                            {"side": "top", "rot": 0, "w": ar_fxtr.width, "h": ar_fxtr.height, "x": clinic_bbox.center.x - (ar_fxtr.width / 2), "y": clinic_bbox.extmax.y + aisle_gap},
                            {"side": "bottom", "rot": 0, "w": ar_fxtr.width, "h": ar_fxtr.height, "x": clinic_bbox.center.x - (ar_fxtr.width / 2), "y": clinic_bbox.extmin.y - aisle_gap - ar_fxtr.height},
                        ]
                        for spot in spots_to_try:
                            candidate_box = box(spot["x"], spot["y"], spot["x"] + spot["w"], spot["y"] + spot["h"])
                            is_in_boh = boh_zone_poly.intersects(candidate_box) if boh_zone_poly else False
                            if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in placed_bboxes) and not is_in_boh:
                                insert_point = (spot["x"] + spot["w"], spot["y"], 0) if spot["rot"] == 90 else (spot["x"], spot["y"], 0)
                                self.place_fixture(ar_fxtr, insert_point, spot["rot"], True)
                                placed_bboxes.append(candidate_box.bounds)
                                print(f"    ✅ SUCCESS: Placed 'AR' on the {spot['side']} of a clinic via fallback.")
                                is_placed = True
                                break
                
                # --- FINAL FALLBACK: PLACE BELOW PICKUP WINDOW ---
                # if not is_placed:
                #     print(f"\n  -> ⚠️ All clinic-based spots were blocked or in BOH. Trying FINAL FALLBACK...")
                    
                #     # This is the line that was causing the error. It now has a space.
                    
                #     pickup_window_entities = [e for e in self.msp.query('INSERT') if "PICK_UP_WINDOW" in e.dxf.name.upper()]
                #     pickup_window_entity = pickup_window_entities[0] if pickup_window_entities else None

                #     if not pickup_window_entity:
                #         print("  -> ⚠️ FALLBACK FAILED: No 'Pick_up_window' found to anchor to.")
                #     else:
                #         anchor_bbox = extents([pickup_window_entity])
                #         target_x = anchor_bbox.center.x - (ar_fxtr.width / 2)
                #         target_y = anchor_bbox.extmin.y - 150.0 - ar_fxtr.height

                #         candidate_box = box(target_x, target_y, target_x + ar_fxtr.width, target_y + ar_fxtr.height)
                #         is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
                #         is_inside = self.floorplan_polygon.contains(candidate_box)

                #         if is_inside and not is_overlapping:
                #             self.place_fixture(ar_fxtr, (target_x, target_y, 0), 0, False)
                #             placed_bboxes.append(candidate_box.bounds)
                #             print(f"    ✅ SUCCESS (Fallback): Placed 'AR' below the Pick-up Window.")
                #             is_placed = True
                #         else:
                #             print("  -> ⚠️ FALLBACK FAILED: Spot below the Pick-up Window was blocked.")

                # if not is_placed:
                #     print(f"⚠️ Could not find a suitable location for the AR fixture after all strategies.")

                if not is_placed:
                    print(f"\n  -> ⚠️ All clinic-based spots were blocked or in BOH. Trying FINAL FALLBACK...")
                    
                    pickup_window_entities = [e for e in self.msp.query('INSERT') if "PICK_UP_WINDOW" in e.dxf.name.upper()]
                    pickup_window_entity = pickup_window_entities[0] if pickup_window_entities else None

                    if not pickup_window_entity:
                        print("    -> No Pick_up_window found for final fallback.")
                    else:
                        # Get the pickup window's bounding box
                        pickup_bbox = extents([pickup_window_entity])
                        
                        # Position AR directly below the pickup window (centered horizontally)
                        gap_below = 100.0  # Small gap between pickup window and AR
                        
                        # Calculate AR position
                        ar_x = pickup_bbox.center.x - (ar_fxtr.width / 2) + 600 # Center horizontally
                        ar_y = pickup_bbox.extmin.y - gap_below - ar_fxtr.height  # Position below with gap
                        
                        # Create candidate box for validation
                        candidate_box = box(ar_x, ar_y, ar_x + ar_fxtr.width, ar_y + ar_fxtr.height)
                        
                        # Check if position is valid
                        is_in_boh = boh_zone_poly.intersects(candidate_box) if boh_zone_poly else False
                        is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
                        is_inside = self.floorplan_polygon.contains(candidate_box)
                        
                        if is_inside and not is_overlapping and not is_in_boh:
                            # Place the AR fixture
                            self.place_fixture(ar_fxtr, (ar_x, ar_y, 0), 0, True)
                            placed_bboxes.append((ar_x, ar_y, ar_x + ar_fxtr.width, ar_y + ar_fxtr.height))
                            print(f"    ✅ SUCCESS (Final Fallback): Placed AR directly below Pick_up_window at ({ar_x:.0f}, {ar_y:.0f}).")
                            is_placed = True
                        else:
                            print("    -> ⚠️ Final fallback spot below pickup window is also blocked or invalid.")

        except Exception as e:
            print(f"🔥 FATAL: An error occurred during POS/AR placement: {e}")
            return
    
   


#---- POS/AR PLACEMENT FUNCTION FINISHED HERE ----
#---- lensometer PLACEMENT FUNCTION STARTED HERE ----

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

#---- lensometer PLACEMENT FUNCTION STOPPED HERE ----

#---- SOFA PLACEMENT FUNCTION STOPPED HERE ----
    
    def place_sofas_above_screen_ar(self, placed_bboxes, bottom_margin_pct=0.20, gap_above_ar=300):
        """
        Places sofa fixtures using a prioritized, multi-strategy approach.

        Strategy 1 (Primary): Places sofas a specific distance (`gap_above_ar`) above the POS/AR fixtures.
        Strategy 2 (Fallback): If the ideal gap is too large, it fits the sofas into the remaining space.
        Strategy 3 (Fallback): If there's no room above, it tries to place them in the bottom margin area.
        Strategy 4 (Final Fallback): Performs a global grid search for any available space.
        """
        # from Fixture import Fixture
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
                        fxtr = Fixture.Fixture(name, self.fixture_dict[name]["path"])
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


#---- BLUE_ZERO PLACEMENT FUNCTION STARTED HERE ----


    def place_Blue_Zero_attached(self, placed_bboxes):
        """
        Finds existing discussion tables and places "Blue_zero" fixtures.
        FALLBACK LOGIC: If no discussion tables are found, it anchors to Euro Centres
        using a context-aware strategy based on the store's layout.
        """
        from ezdxf.bbox import extents
        from shapely.geometry import box

        # 1. SETUP
        config = self.fixtures.get("discussion_table_attached", {})
        blue_zero_count = config.get("Blue_zero", 0)
        if blue_zero_count <= 0:
            return

        print("\n--- Attempting to place attached discussion fixtures (Blue_zero) ---")
        try:
            blue_zero_fxtr = Fixture.Fixture("Blue_zero", self.fixture_dict["Blue_zero"]["path"])
        except Exception as e:
            print(f"⚠️ Could not load the Blue_zero fixture file: {e}")
            return

        # 2. FIND PRIMARY ANCHORS (Discussion Tables)
        primary_anchors = []
        for entity in self.msp.query('INSERT'):
            if "DISCUSSION_TABLE" in entity.dxf.name.upper():
                try:
                    primary_anchors.append(extents([entity], fast=True))
                except (RuntimeError, TypeError):
                    continue

        placed_count = 0
        margin = 50.0

        # 3. EXECUTE PRIMARY STRATEGY (Place below Discussion Tables)
        if primary_anchors:
            print(f"  -> Found {len(primary_anchors)} Discussion Table(s) to use as primary anchors.")
            for target_bbox in primary_anchors:
                if placed_count >= blue_zero_count: break
                
                target_x = target_bbox.center.x - (blue_zero_fxtr.width / 2)
                target_y = target_bbox.extmin.y - margin - blue_zero_fxtr.height
                candidate_box = box(target_x, target_y, target_x + blue_zero_fxtr.width, target_y + blue_zero_fxtr.height)
                is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
                is_inside = self.floorplan_polygon.contains(candidate_box)

                if is_inside and not is_overlapping:
                    self.place_fixture(blue_zero_fxtr, (target_x, target_y, 0), 0, False)
                    placed_bboxes.append(candidate_box.bounds)
                    print(f"✅ Placed Blue_zero below a Discussion Table.")
                    placed_count += 1
                else:
                    print(f"ℹ️ Spot below a Discussion Table was blocked.")
        
        # 4. EXECUTE FALLBACK STRATEGY (Anchor to Euro Centres)
        if placed_count < blue_zero_count:
            print("\n  -> No more Discussion Table spots. Searching for Euro_centre fixtures as a fallback.")
            euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
            if not euro_entities:
                print("ℹ️ No Euro centres were found for fallback placement.")
                return

            euro_rotation = euro_entities[0].dxf.rotation
            is_double_shopping = (85 < euro_rotation < 95) or (265 < euro_rotation < 275)
            fallback_anchors = [extents([e]) for e in euro_entities]

            
            if is_double_shopping:
                print("  -> Detected Double Shopping layout. Placing Blue_zero BELOW Euro Centres.")
                for target_bbox in fallback_anchors:
                    if placed_count >= blue_zero_count:
                        break

                    was_placed = False

                    # --- ATTEMPT 1: Place BELOW (Original Logic) ---
                    target_x = target_bbox.center.x - (blue_zero_fxtr.width / 2)
                    target_y_below = target_bbox.extmin.y - margin - blue_zero_fxtr.height
                    candidate_box_below = box(target_x, target_y_below, target_x + blue_zero_fxtr.width, target_y_below + blue_zero_fxtr.height)
                    
                    if self.floorplan_polygon.contains(candidate_box_below) and not any(candidate_box_below.intersects(box(*b)) for b in placed_bboxes):
                        self.place_fixture(blue_zero_fxtr, (target_x, target_y_below, 0), 0, False)
                        placed_bboxes.append(candidate_box_below.bounds)
                        print(f"✅ Placed Blue_zero below a Euro Centre.")
                        placed_count += 1
                        was_placed = True

                    # --- ATTEMPT 2: Place ABOVE (New Fallback Logic) ---
                    if not was_placed:
                        # The X position is the same (centered), but the Y position is now above the Euro.
                        target_y_above = target_bbox.extmax.y + margin
                        candidate_box_above = box(target_x, target_y_above, target_x + blue_zero_fxtr.width, target_y_above + blue_zero_fxtr.height)

                        if self.floorplan_polygon.contains(candidate_box_above) and not any(candidate_box_above.intersects(box(*b)) for b in placed_bboxes):
                            self.place_fixture(blue_zero_fxtr, (target_x, target_y_above, 0), 0, False)
                            placed_bboxes.append(candidate_box_above.bounds)
                            print(f"✅ Placed Blue_zero ABOVE a Euro Centre (fallback).")
                            placed_count += 1
                            was_placed = True
            # --- FALLBACK B: Single Shopping (Place Left/Right) ---
            else:
                print("  -> Detected Single Shopping layout. Placing Blue_zero to the LEFT/RIGHT of Euro Centres.")
                for i, target_bbox in enumerate(fallback_anchors):
                    if placed_count >= blue_zero_count: break
                    
                    side = "left" if i % 2 == 0 else "right"
                    
                    if side == "left":
                        rotation = 90#270
                        # insert_x = target_bbox.extmin.x - blue_zero_fxtr.height - margin
                        # insert_y = target_bbox.center.y - (blue_zero_fxtr.width / 2)
                        insert_x = target_bbox.extmax.x + margin
                        insert_y = target_bbox.center.y - (blue_zero_fxtr.width / 2)
                        # final_insert_point = (insert_x, insert_y + blue_zero_fxtr.width, 0)
                        # candidate_box = box(insert_x, insert_y, insert_x + blue_zero_fxtr.height, insert_y + blue_zero_fxtr.width)
                        final_insert_point = (insert_x + blue_zero_fxtr.height + 300, insert_y, 0)
                        candidate_box = box(insert_x, insert_y, insert_x + blue_zero_fxtr.height + 300, insert_y + blue_zero_fxtr.width)
                    else: # side == "right"
                        rotation = 90
                        insert_x = target_bbox.extmax.x + margin
                        insert_y = target_bbox.center.y - (blue_zero_fxtr.width / 2)
                        final_insert_point = (insert_x, insert_y, 0)
                        candidate_box = box(insert_x, insert_y, insert_x + blue_zero_fxtr.height, insert_y + blue_zero_fxtr.width)

                    if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                        self.place_fixture(blue_zero_fxtr, final_insert_point, rotation, True)
                        placed_bboxes.append(candidate_box.bounds)
                        print(f"✅ Placed Blue_zero on the {side} of a Euro Centre.")
                        placed_count += 1

        if placed_count < blue_zero_count:
            print(f"⚠️ Warning: Placed only {placed_count} of {blue_zero_count} requested Blue_zero fixtures.")

#---- BLUE_ZERO PLACEMENT FUNCTION STOPPED HERE ----

#------ QMS/GREETR PLACEMENT FUNCTION STARTED HERE ----

    def _find_qms_placement_y_coordinate(self) -> Optional[float]:
        """
        Finds the ideal Y-coordinate to place the QMS desk.
        It calculates the midpoint of the available vertical space between the
        bottom of the central fixture block and the bottom wall of the room.
        
        Returns:
            The calculated Y-coordinate for placement, or None if no space is available.
        """
        from ezdxf.bbox import extents
        # from Fixture import Fixture # Make sure Fixture is imported

        print("\n  -> Calculating ideal Y-coordinate for QMS Desk...")

        # --- STEP 1: Find the central fixtures to anchor to ---
        # We search for any placed fixtures that are part of the central block.
        central_fixture_entities = [
            e for e in self.msp.query('INSERT') 
            if "EURO_CENTRE" in e.dxf.name.upper() or "LENSBAR" in e.dxf.name.upper()
        ]

        # If no central fixtures have been placed yet, we can't calculate the gap.
        if not central_fixture_entities:
            print("    -> ⚠️ Could not find central fixtures to anchor to. Using a fixed distance from the bottom wall.")
            # Fallback: return a fixed position from the bottom wall.
            return self.cvc.min_y + 1000.0

        # --- STEP 2: Find the lowest point of the central fixtures ---
        # We get the bounding box of all central fixtures and find the absolute bottom edge.
        central_fixtures_bbox = extents(central_fixture_entities)
        bottom_of_central_fixtures = central_fixtures_bbox.extmin.y
        
        # The bottom of the room is our other boundary.
        bottom_of_room = self.cvc.min_y

        # --- STEP 3: Calculate the available gap and see if the QMS desk fits ---
        available_gap = bottom_of_central_fixtures - bottom_of_room
        
        try:
            # Load the QMS desk fixture to get its height.
            qms_fxtr = Fixture.Fixture("QMS_desk", self.fixture_dict["QMS_desk"]["path"])
        except Exception as e:
            print(f"    -> 🔥 Could not load QMS_desk fixture to get its height: {e}")
            return None # Cannot proceed without fixture height

        # If the gap is smaller than the desk's height, it can't be placed.
        if available_gap < qms_fxtr.height + 200: # Add a small 200mm buffer
            print("    -> ⚠️ Not enough space between central fixtures and the bottom wall to place the QMS desk.")
            return None

        # --- STEP 4: Calculate the midpoint and return the coordinate ---
        # We find the remaining empty space after accounting for the desk's height.
        empty_space = available_gap - qms_fxtr.height
        
        # The ideal placement is at the bottom of the room, plus half of the remaining empty space.
        # This perfectly centers the desk in the gap.
        placement_y = bottom_of_room + (empty_space / 2)
        
        print(f"    -> ✅ Ideal placement Y-coordinate found: {placement_y:.0f} mm")
        return placement_y

    def _calculate_dynamic_qms_margin(self) -> float:
        """
        Calculates a dynamic bottom margin for the QMS desk based on a combination of
        total floor area and the floor plan's aspect ratio (shape).
        """
        print("\n    -> Calculating dynamic bottom margin for QMS desk (Area + Shape)...")

        # Your defined min/ideal/max values
        MIN_MARGIN = 1800.0
        IDEAL_MARGIN = 1950.0
        MAX_MARGIN = 2250.0

        # --- Part 1: Calculate a base margin from the total area ---
        floor_area_sqft = self.calculate_area_sqft()
        base_margin = 0.0
        if floor_area_sqft <= 750:
            base_margin = MIN_MARGIN
        elif floor_area_sqft <= 1250:
            base_margin = IDEAL_MARGIN
        else:
            base_margin = MAX_MARGIN
        print(f"      -> Base margin from area ({floor_area_sqft:.0f} sq. ft.): {base_margin} mm.")

        # --- Part 2: Calculate an adjustment factor from the shape ---
        height = self.cvc.max_y - self.cvc.min_y
        width = self.cvc.max_x - self.cvc.min_x
        
        # Avoid division by zero for unusual shapes
        if height == 0:
            aspect_ratio = 1.0
        else:
            aspect_ratio = width / height
        
        adjustment_factor = 1.0
        if aspect_ratio < 0.8:  # Identifies a TALL and NARROW floorplan
            adjustment_factor = 0.9  # Reduce the margin by 10%
            print(f"      -> Shape is TALL (Aspect Ratio: {aspect_ratio:.2f}). Adjusting margin down by 10%.")
        elif aspect_ratio > 1.25:  # Identifies a SHORT and WIDE floorplan
            adjustment_factor = 1.1  # Increase the margin by 10%
            print(f"      -> Shape is WIDE (Aspect Ratio: {aspect_ratio:.2f}). Adjusting margin up by 10%.")
        else:  # The shape is relatively balanced or "squarish"
            print(f"      -> Shape is balanced (Aspect Ratio: {aspect_ratio:.2f}). No adjustment.")
        
        # --- Part 3: Apply the adjustment and CLAMP the final value ---
        adjusted_margin = base_margin * adjustment_factor
        
        # This ensures the final value strictly respects your min/max rules
        final_margin = max(MIN_MARGIN, min(adjusted_margin, MAX_MARGIN))
        
        print(f"      -> Final Clamped Margin: {final_margin:.0f} mm.")
            
        return final_margin

    
    def place_qms_from_center(self, placed_bboxes):
        """
        Places QMS desks using a context-aware strategy based on the orientation
        of the central Euro Centre fixtures.
        - Double Shopping (rotated Euros): Places desks underneath the Euro block only,
        using a dynamic margin that is capped to prevent collisions.
        - Single Shopping (unrotated Euros): Places desks underneath the Euro block only.
        """
        from ezdxf.bbox import extents
        from shapely.geometry import box

        # --- 1. SETUP (Same as before) ---
        config = self.fixtures.get("table_fixtures", {})
        qms_count = config.get("QMS_desk", 0)
        if qms_count <= 0:
            return

        print(f"\n--- Attempting to place {qms_count} QMS Desk(s) with Context-Aware Strategy ---")

        try:
            qms_fxtr = Fixture.Fixture("QMS_desk", self.fixture_dict["QMS_desk"]["path"])
        except Exception as e:
            print(f"🔥 Could not load QMS_desk fixture: {e}")
            return

        euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
        if not euro_entities:
            print("⚠️ Cannot place QMS desks: Euro Centre anchor fixtures not found.")
            return
        
        euro_bbox = extents(euro_entities)
        
        # --- 2. DETECT ORIENTATION ---
        euro_rotation = euro_entities[0].dxf.rotation
        is_portrait_layout = (85 < euro_rotation < 95) or (265 < euro_rotation < 275)
        
        def is_valid_spot(fixture, x, y):
            w, h = fixture.width, fixture.height
            candidate_box = box(x, y, x + w, y + h)
            is_overlapping = any(candidate_box.intersects(box(*bbox)) for bbox in placed_bboxes)
            is_inside = self.floorplan_polygon.contains(candidate_box)
            return is_inside and not is_overlapping

        # =========================================================================
        # --- 3A. DOUBLE SHOPPING LOGIC (Rotated Euros) ---
        # =========================================================================
        if is_portrait_layout:
            # --- NEW LOGIC AS PER YOUR REQUEST ---
            print("  -> Detected Double Shopping layout. Placing QMS underneath using dynamic margin.")

            # 1. Calculate the ideal margin from the bottom wall
            ideal_bottom_margin = self._calculate_dynamic_qms_margin()
            ideal_start_y = self.cvc.min_y + ideal_bottom_margin

            # 2. Add a constraint to prevent overlapping the Euro Centres
            GAP_BELOW_EUROS = 100.0  # A small safety gap
            max_possible_y = euro_bbox.extmin.y - qms_fxtr.height - GAP_BELOW_EUROS

            # 3. Cap the final Y-position if the ideal margin is too large
            final_start_y = min(ideal_start_y, max_possible_y)

            if ideal_start_y > max_possible_y:
                print(f"    -> Dynamic margin was too large. Capping Y-position at {final_start_y:.0f} to avoid collision with Euro Centres.")
            else:
                print(f"    -> Dynamic margin is valid. Placing at Y-position {final_start_y:.0f}.")

            # 4. Use the resilient horizontal search to find a spot at this final Y-position
            ideal_x = euro_bbox.center.x - (qms_fxtr.width / 2)
            first_desk_placed = False
            final_start_x = 0 
            search_offset = 0
            max_search = (self.cvc.max_x - self.cvc.min_x) / 2
            while not first_desk_placed and search_offset < max_search:
                for sign in [1, -1]:
                    if sign == -1 and search_offset == 0: continue
                    test_x = ideal_x + search_offset * sign
                    if is_valid_spot(qms_fxtr, test_x, final_start_y):
                        final_start_x = test_x
                        first_desk_placed = True
                        break
                if first_desk_placed: break
                search_offset += 100

            if not first_desk_placed:
                print("⚠️ Could not find a clear spot for QMS desks below the Euro Centre block.")
                return
            # --- END OF NEW LOGIC ---

        # =========================================================================
        # --- 3B. SINGLE SHOPPING LOGIC (Unrotated Euros) ---
        # =========================================================================
        else:
            # This logic remains the same (it already does what you want)
            print("  -> Detected Single Shopping layout (unrotated Euros). Placing QMS underneath.")
            
            bottom_margin = self._calculate_dynamic_qms_margin()
            start_y = self.cvc.min_y + bottom_margin
            ideal_x = euro_bbox.center.x - (qms_fxtr.width / 2)
            
            first_desk_placed = False
            final_start_x, final_start_y = 0, 0
            search_offset = 0
            max_search = (self.cvc.max_x - self.cvc.min_x) / 2

            while not first_desk_placed and search_offset < max_search:
                for sign in [1, -1]:
                    if sign == -1 and search_offset == 0: continue
                    test_x = ideal_x + search_offset * sign
                    if is_valid_spot(qms_fxtr, test_x, start_y):
                        final_start_x, final_start_y = test_x, start_y
                        first_desk_placed = True
                        break
                if first_desk_placed: break
                search_offset += 100
            
            if not first_desk_placed:
                print("⚠️ Could not find a clear spot for QMS desks below the Euro Centre block.")
                return

        # =========================================================================
        # --- 4. EXECUTE PLACEMENT (This part is the same for both layouts) ---
        # =========================================================================
        
        qms_placed_count = 0
        placed_qms_bboxes = []
        
        self.place_fixture(qms_fxtr, (final_start_x, final_start_y, 0), 0, False)
        bbox_coords = (final_start_x, final_start_y, final_start_x + qms_fxtr.width, final_start_y + qms_fxtr.height)
        placed_bboxes.append(bbox_coords)
        placed_qms_bboxes.append(bbox_coords)
        qms_placed_count += 1
        print(f"✅ Placed central QMS_desk #{qms_placed_count} at ({final_start_x:.0f}, {final_start_y:.0f}).")

        if qms_count > 1:
            max_gap, min_gap, congestion_threshold = 2000, 1000, 5
            if qms_count <= 3: gap_horizontal = max_gap
            elif qms_count >= congestion_threshold: gap_horizontal = min_gap
            else: gap_horizontal = max_gap - ((qms_count - 2) / (congestion_threshold - 2) * (max_gap - min_gap))
            
            print(f"ℹ️ Dynamic horizontal gap set to {gap_horizontal:.0f}mm.")
            
            leftmost_bbox = placed_qms_bboxes[0]
            rightmost_bbox = placed_qms_bboxes[0]

            for i in range(qms_count - 1):
                if i % 2 == 0: # Place to the left
                    target_x = leftmost_bbox[0] - gap_horizontal - qms_fxtr.width
                    if is_valid_spot(qms_fxtr, target_x, final_start_y):
                        self.place_fixture(qms_fxtr, (target_x, final_start_y, 0), 0, False)
                        new_bbox = (target_x, final_start_y, target_x + qms_fxtr.width, final_start_y + qms_fxtr.height)
                        placed_bboxes.append(new_bbox); leftmost_bbox = new_bbox; qms_placed_count += 1
                        print(f"✅ Placed QMS_desk #{qms_placed_count} to the left.")
                    else: print("⚠️ Spot to the left is blocked.")
                else: # Place to the right
                    target_x = rightmost_bbox[2] + gap_horizontal
                    if is_valid_spot(qms_fxtr, target_x, final_start_y):
                        self.place_fixture(qms_fxtr, (target_x, final_start_y, 0), 0, False)
                        new_bbox = (target_x, final_start_y, target_x + qms_fxtr.width, final_start_y + qms_fxtr.height)
                        placed_bboxes.append(new_bbox); rightmost_bbox = new_bbox; qms_placed_count += 1
                        print(f"✅ Placed QMS_desk #{qms_placed_count} to the right.")
                    else: print("⚠️ Spot to the right is blocked.")

        print(f"-> Finished: Placed {qms_placed_count} of {qms_count} QMS desks.")


#------ QMS/GREETR PLACEMENT FUNCTION STOPPED HERE ----

#------ STANDING TABLE PLACEMENT FUNCTION STARTED HERE ----


    def _get_new_standing_table_anchor_y(self) -> Optional[float]:
        """
        [Plan B Logic] Calculates new anchor-Y for Standing Tables.

        Updated behaviour:
        - When the available horizontal width condition is met, prefer anchoring
          to the bottom (min-y) of the BOH zone if a BOH zone exists.
        - If no BOH zone is present, fall back to anchoring to the last clinic bottom.
        """
        from ezdxf.bbox import extents
        print("\n  -> [Plan B Logic] Calculating new anchor-Y for Standing Tables...")

        # 1a. Find the "last" placed clinic (the one furthest to the right)
        clinic_entities = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
        if not clinic_entities:
            print("    -> ⚠️ No clinics found. Falling back to standard anchor method.")
            return self._get_standing_table_anchor_y()

        last_clinic_coords = self._get_last_clinic_right_bottom_coord()
        
        if last_clinic_coords is None:
            print("    -> ⚠️ Could not get accurate last clinic coordinates. Falling back to standard anchor method.")
            return self._get_standing_table_anchor_y()

        last_clinic_right_edge_x, last_clinic_bottom_y = last_clinic_coords
        
        print(f"    -> Last clinic (right-most) found at x={last_clinic_right_edge_x:.0f}")
        print(f"    -> Last clinic (bottom) found at y={last_clinic_bottom_y:.0f}")

        # 1b. Find the right-side boundary (either the Pickup Window or the wall)
        right_boundary_x = self.cvc.max_x  # Default to the right wall

        pickup_window = None
        for entity in self.msp.query('INSERT'):
            if "PICK_UP_WINDOW" in entity.dxf.name.upper():
                pickup_window = entity
                break

        if pickup_window:
            pickup_bbox = extents([pickup_window])
            right_boundary_x = pickup_bbox.extmin.x
            print(f"    -> Pickup window found. Right boundary is at x={right_boundary_x:.0f}")
        else:
            print(f"    -> No pickup window. Right boundary is the wall at x={right_boundary_x:.0f}")

        # 1c. Calculate the available horizontal width
        available_width = right_boundary_x - last_clinic_right_edge_x
        print(f"    -> Horizontal space between last clinic and right boundary: {available_width:.0f}mm")

        # 2. Check the width and determine the anchor Y-coordinate
        # NOTE: preserved original condition; only change is to prefer BOH bottom as anchor
        # if available_width > -2000 or available_width < 1500:
        if available_width > 3000:
            print(f"    -> Available width is {available_width:.0f}mm.")

            # NEW: prefer BOH zone bottom as anchor when available
            boh_poly = None
            try:
                boh_poly = self._get_boh_zone_polygon()
            except Exception:
                boh_poly = None

            if boh_poly:
                boh_min_y = boh_poly.bounds[1]  # bounds -> (minx, miny, maxx, maxy)
                print(f"    -> Anchoring to BOH zone bottom at y={boh_min_y:.0f} instead of last clinic.")
                return boh_min_y
            else:
                print(f"    -> BOH zone not found. Anchoring to the bottom of the last clinic (y={last_clinic_bbox.extmin.y:.0f}).")
                return last_clinic_bbox.extmin.y
        else:
            # 3. If space is insufficient, fall back to the original method
            print(f"    -> Available width is {available_width:.0f}mm.")
            print("    -> Space is not > 1500mm. Falling back to the standard non-retail boundary anchor method.")
            return self._get_standing_table_anchor_y()
    
    def _get_new_standing_table_anchor_y_og(self) -> Optional[float]:
        """
        [Plan B Logic] Calculates new anchor-Y for Standing Tables.

        Updated behaviour:
        - When the available horizontal width condition is met, prefer anchoring
          to the bottom (min-y) of the BOH zone if a BOH zone exists.
        - If no BOH zone is present, fall back to anchoring to the last clinic bottom.
        """
        from ezdxf.bbox import extents
        print("\n  -> [Plan B Logic] Calculating new anchor-Y for Standing Tables...")

        # 1a. Find the "last" placed clinic (the one furthest to the right)
        clinic_entities = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
        print("clinic_entities:", clinic_entities)
        print("Number of clinics found:", len(clinic_entities))
        print("clinic coordinates:", [extents([e]) for e in clinic_entities])
        if not clinic_entities:
            print("    -> ⚠️ No clinics found. Falling back to standard anchor method.")
            return self._get_standing_table_anchor_y()

        last_clinic = max(clinic_entities, key=lambda e: extents([e]).extmax.x)
        last_clinic_bbox = extents([last_clinic])
        last_clinic_right_edge_x = last_clinic_bbox.extmax.x
        print(f"    -> Last clinic (right-most) found at x={last_clinic_right_edge_x:.0f}")

        # 1b. Find the right-side boundary (either the Pickup Window or the wall)
        right_boundary_x = self.cvc.max_x  # Default to the right wall

        pickup_window = None
        for entity in self.msp.query('INSERT'):
            if "PICK_UP_WINDOW" in entity.dxf.name.upper():
                pickup_window = entity
                break

        if pickup_window:
            pickup_bbox = extents([pickup_window])
            right_boundary_x = pickup_bbox.extmin.x
            print(f"    -> Pickup window found. Right boundary is at x={right_boundary_x:.0f}")
        else:
            print(f"    -> No pickup window. Right boundary is the wall at x={right_boundary_x:.0f}")

        # 1c. Calculate the available horizontal width
        available_width = right_boundary_x - last_clinic_right_edge_x
        print(f"    -> Horizontal space between last clinic and right boundary: {available_width:.0f}mm")

        # 2. Check the width and determine the anchor Y-coordinate
        # NOTE: preserved original condition; only change is to prefer BOH bottom as anchor
        # if available_width > -2000 or available_width < 1500:
        if available_width > -4500:
            print(f"    -> Available width is {available_width:.0f}mm.")

            # NEW: prefer BOH zone bottom as anchor when available
            boh_poly = None
            try:
                boh_poly = self._get_boh_zone_polygon()
            except Exception:
                boh_poly = None

            if boh_poly:
                boh_min_y = boh_poly.bounds[1]  # bounds -> (minx, miny, maxx, maxy)
                print(f"    -> Anchoring to BOH zone bottom at y={boh_min_y:.0f} instead of last clinic.")
                return boh_min_y
            else:
                print(f"    -> BOH zone not found. Anchoring to the bottom of the last clinic (y={last_clinic_bbox.extmin.y:.0f}).")
                return last_clinic_bbox.extmin.y
        else:
            # 3. If space is insufficient, fall back to the original method
            print(f"    -> Available width is {available_width:.0f}mm.")
            print("    -> Space is not > 1500mm. Falling back to the standard non-retail boundary anchor method.")
            return self._get_standing_table_anchor_y()
    
   

    def _get_standing_table_anchor_y(self) -> Optional[float]:
        """
        FINDS THE CORRECT ANCHOR LINE (Y-coordinate) to measure from for standing tables.
        1. Finds the lowest non-retail fixture.
        2. Checks if any Bench/AR fixture is within 500mm below it AND falls within the
        central "standing table corridor".
        3. Returns the Y-coordinate of the correct anchor.
        """
        from ezdxf.bbox import extents
        print("\n  -> Finding dynamic anchor-Y for Standing Tables (using Central Corridor Proxy)...")

        # --- STEP 1: Find the lowest placed non-retail fixture (No change here) ---
        non_retail_entities = [
            e for e in self.msp.query('LINE[layer=="RETAIL_SEPARATOR"]')
        ]
        all_polylines = self.msp.query('LWPOLYLINE')
        boh_outlines = [p for p in all_polylines if "BOH_WALL_" in p.dxf.layer and p.dxf.layer.endswith("_OUTLINE")]
        
        combined_non_retail_entities = non_retail_entities + boh_outlines
        
        if not combined_non_retail_entities:
            print("    -> ⚠️ SKIPPING: No non-retail fixtures found to anchor to.")
            return None

        non_retail_bboxes = [extents([e]) for e in combined_non_retail_entities if extents([e])]
        if not non_retail_bboxes:
            print("    -> ⚠️ SKIPPING: Could not calculate bounding boxes for non-retail fixtures.")
            return None

        lowest_non_retail_fixture_bbox = min(non_retail_bboxes, key=lambda b: b.extmin.y)
        lowest_non_retail_y = lowest_non_retail_fixture_bbox.extmin.y
        print(f"    -> Primary anchor (lowest non-retail) found at y={lowest_non_retail_y:.0f}.")

        ### --- START OF MODIFICATION --- ###

        # --- NEW: DEFINE THE PROXY ZONE for where standing tables will likely be placed ---
        # We'll define this as the central 50% of the room's width, leaving 25% for aisles on each side.
        room_width = self.cvc.max_x - self.cvc.min_x
        aisle_margin = room_width * 0.25 
        standing_table_zone_start_x = self.cvc.min_x + aisle_margin
        standing_table_zone_end_x = self.cvc.max_x - aisle_margin
        print(f"    -> Defined standing table proxy zone between x={standing_table_zone_start_x:.0f} and x={standing_table_zone_end_x:.0f}")

        # --- STEP 2: Check for Bench or AR within the PROXY ZONE ---
        furniture_entities = [
            e for e in self.msp.query('INSERT') if
            "BENCH" in e.dxf.name.upper() or "AR" in e.dxf.name.upper()
        ]
        
        new_anchor_furniture_bbox = None
        if furniture_entities:
            candidate_furniture = []
            for entity in furniture_entities:
                try:
                    furniture_bbox = extents([entity])
                    
                    # Condition 1: Vertically below and close to the BOH block
                    is_vertically_close = (furniture_bbox.extmax.y < lowest_non_retail_y) and \
                                        ((lowest_non_retail_y - furniture_bbox.extmax.y) <= 500.0)

                    # MODIFIED Condition 2: Horizontally inside the standing table proxy zone
                    is_in_central_zone = (
                        standing_table_zone_start_x < furniture_bbox.extmax.x and
                        furniture_bbox.extmin.x < standing_table_zone_end_x
                    )

                    # The furniture is only a candidate if BOTH conditions are true
                    if is_vertically_close and is_in_central_zone:
                        candidate_furniture.append(furniture_bbox)
                        
                except (RuntimeError, TypeError):
                    continue
            
            if candidate_furniture:
                new_anchor_furniture_bbox = min(candidate_furniture, key=lambda b: b.extmin.y)

        ### --- END OF MODIFICATION --- ###

        # --- STEP 3: Determine and return the final anchor Y-coordinate ---
        if new_anchor_furniture_bbox:
            final_anchor_y = new_anchor_furniture_bbox.extmin.y
            print(f"    -> Found relevant furniture in the central corridor. Final anchor is the furniture's bottom edge at y={final_anchor_y:.0f}.")
            return final_anchor_y
        else:
            print("    -> No furniture in the central path. Final anchor is the non-retail fixture's bottom edge.")
            return lowest_non_retail_y


    


    def place_standing_tables(self, placed_bboxes):
        """
        [MODIFIED] Places Standing Tables using a top-down, adaptive row-based strategy.
        - It now finds the nearest obstacles left and right to define a dynamic corridor.
        - Enforces fixed 800mm walking aisles on both sides of the table group.
        - Centers the tables within the remaining space.
        - CONDITIONALLY ignores the RETAIL_SEPARATOR line as an obstacle for Plan B layouts.
        """
        from ezdxf.bbox import extents
        from shapely.geometry import box, LineString
        import collections
        import math

        print("\n--- 🧠 Placing Standing Tables (Dynamic Corridor Strategy) ---")

        # 1. Get configuration (Unchanged)
        config = self.fixtures.get("table_fixtures", {})
        standing_table_count = config.get("Standing_table", 0)
        if standing_table_count <= 0:
            return

        try:
            standing_fxtr = Fixture.Fixture("Standing_table", self.fixture_dict["Standing_table"]["path"])
        except Exception as e:
            print(f"🔥 Could not load Standing_table fixture: {e}")
            return

        # --- Anchor-Y and Initial Setup (Unchanged) ---
        anchor_y = None
        # This check correctly determines if the Plan B anchor method will be used
        is_plan_b = hasattr(self, 'clinic_placement_method') and self.clinic_placement_method == 'Plan_B'

        #*********************************************
        # if is_plan_b:
        #     anchor_y = self._get_new_standing_table_anchor_y()
        # else:
        #     anchor_y = self._get_standing_table_anchor_y()

        
        if is_plan_b:
            last_clinic_coords = self._get_last_clinic_right_bottom_coord()
            anchor_y = self._get_new_standing_table_anchor_y()
            # Extract the actual coordinates if Plan B was used successfully
            if last_clinic_coords:
                last_clinic_right_edge_x, _ = last_clinic_coords
                print(f"  -> Plan B Active. Last Clinic Anchor X: {last_clinic_right_edge_x:.0f}")
            else:
                # If Plan B was active but no clinics were placed, revert to Plan A logic
                is_plan_b = False
                anchor_y = self._get_standing_table_anchor_y()
        else:
            anchor_y = self._get_standing_table_anchor_y()

        if anchor_y is None:
            print("  -> ⚠️ FAILED: Could not determine a valid anchor Y-coordinate. Aborting placement.")
            return

        gap_below_anchor = 950
        y_cursor_start = anchor_y - gap_below_anchor - standing_fxtr.height
        print(f"  -> Top boundary found at y={anchor_y:.0f}. Starting first row search at y={y_cursor_start:.0f}.")

        horizontal_gap = 750.0
        vertical_row_gap = 750.0
        fixture_queue = collections.deque([standing_fxtr] * standing_table_count)
        
        # --- NEW CONDITIONAL OBSTACLE LOGIC START ---

        # First, get all obstacles as usual
        all_obstacles = self._get_accurate_obstacle_bboxes(include_all=True)
       
        # --- NEW LOGIC: Check Plan B status and get coordinates ---
        is_plan_b = hasattr(self, 'clinic_placement_method') and self.clinic_placement_method == 'Plan_B'

        #*********************************************
        # Now, check if we are in Plan B. If so, remove the separator line from the obstacles.
        if is_plan_b:
            print("  -> Plan B active: Granting permission for standing tables to cross the separation line.")
            separator_line = self.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
            if separator_line:
                # Recreate the exact bounding box tuple that _get_accurate_obstacle_bboxes would have created
                start_pt = separator_line.dxf.start
                end_pt = separator_line.dxf.end
                separator_bbox = (
                    min(start_pt.x, end_pt.x),
                    min(start_pt.y, end_pt.y) - 1,
                    max(start_pt.x, end_pt.x),
                    max(start_pt.y, end_pt.y) + 1
                )
                
                # Use a list comprehension to create a new list without the separator's bbox
                all_obstacles = [obs for obs in all_obstacles if obs != separator_bbox]
                print("    -> Temporarily removed RETAIL_SEPARATOR as an obstacle for this placement.")

        # --- NEW CONDITIONAL OBSTACLE LOGIC END ---


        # Helper functions (Unchanged)
        def is_valid_row(start_x, y, fixtures_in_row):
            # (The rest of the function's logic remains exactly the same)
            current_x = start_x
            print(f"    -> Checking validity of row at y={y:.0f} starting x={start_x:.0f} for {len(fixtures_in_row)} tables.")
            for i, fxtr in enumerate(fixtures_in_row):
                candidate_box = box(current_x, y, current_x + fxtr.width, y + fxtr.height)
                if not self.floorplan_polygon.contains(candidate_box.buffer(-1.0)) or any(candidate_box.intersects(box(*b)) for b in all_obstacles):
                    return False
                if i < len(fixtures_in_row) - 1:
                    current_x += fxtr.width + horizontal_gap
            return True

        def find_best_row_size(width_for_tables, fxtr_obj, max_to_check):
            for n in range(min(max_to_check, 5), 0, -1):
                required_width = (fxtr_obj.width * n) + (horizontal_gap * (n - 1))
                if required_width <= width_for_tables:
                    return n
            return 0

        # --- Main Adaptive Placement Loop (Moves DOWNWARDS) ---
        y_cursor = y_cursor_start
        y_cursor_end = self.cvc.min_y

        while fixture_queue and y_cursor > y_cursor_end:
            
            # --- Corridor and Row Sizing Logic (Unchanged) ---
            intersection = self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, y_cursor), (self.cvc.max_x + 100, y_cursor)]))
            if not isinstance(intersection, LineString) or intersection.is_empty:
                y_cursor -= 200; continue

            local_bounds = intersection.bounds

            local_start_x, local_end_x = local_bounds[0], local_bounds[2]
            local_center_x = (local_start_x + local_end_x) / 2

            # # *******************************************************************
            # # ***** CRITICAL MODIFICATION BLOCK: Set the Left Obstacle X *****
            # # *******************************************************************
            # if is_plan_b and 'last_clinic_right_edge_x' in locals():
            #     # For Plan B, the left boundary is the right edge of the last placed clinic
            #     # coordinates = dxfc._get_last_clinic_right_bottom_coord()
            #     left_obstacle_x = last_clinic_right_edge_x
            #     # Ensure the local_start_x is not erroneously far to the right of the clinic's max_x
            #     left_obstacle_x = max(local_start_x, last_clinic_right_edge_x)

            # else:
            #     # For Plan A or if Plan B anchor failed, the boundary is the room's left edge
            #     left_obstacle_x = local_start_x
            
            # right_obstacle_x = local_end_x

            # available_corridor_width = right_obstacle_x - left_obstacle_x
            # if available_corridor_width < 3000:
            #     local_start_x, local_end_x = local_bounds[0], local_bounds[2]
            #     local_center_x = (local_start_x + local_end_x) / 2
            #     left_obstacle_x = local_start_x
            #     right_obstacle_x = local_end_x
            # else:
            #     continue

            # print(f"    -> Row at y={y_cursor:.0f}: Initial left boundary x={left_obstacle_x:.0f}, right boundary x={right_obstacle_x:.0f}.")

            # # left_obstacle_x = local_start_x
            # # right_obstacle_x = local_end_x

            # # for obs in all_obstacles:
            # #     obs_min_x, obs_min_y, obs_max_x, obs_max_y = obs
            # #     if obs_min_y <= y_cursor <= obs_max_y:
            # #         if obs_max_x < local_center_x:
            # #             left_obstacle_x = max(left_obstacle_x, obs_max_x)
            # #         if obs_min_x > local_center_x:
            # #             right_obstacle_x = min(right_obstacle_x, obs_min_x)
            # # Now iterate through obstacles to find the nearest left/right blockages
            # for obs in all_obstacles:
            #     obs_min_x, obs_min_y, obs_max_x, obs_max_y = obs
            #     if obs_min_y <= y_cursor <= obs_max_y:
                    
            #         # For the LEFT boundary, check if this obstacle is to the left of the center
            #         if obs_max_x < local_center_x:
            #             left_obstacle_x = max(left_obstacle_x, obs_max_x)
                        
            #         # For the RIGHT boundary, check if this obstacle is to the right of the center
            #         if obs_min_x > local_center_x:
            #             right_obstacle_x = min(right_obstacle_x, obs_min_x)
            
            # # *******************************************************************
            # # ***** END CRITICAL MODIFICATION BLOCK *****
            # # *******************************************************************

            # available_corridor_width = right_obstacle_x - left_obstacle_x
            # if available_corridor_width < 3000:
            #     local_start_x, local_end_x = local_bounds[0], local_bounds[2]
            #     local_center_x = (local_start_x + local_end_x) / 2
            #     left_obstacle_x = local_start_x
            #     right_obstacle_x = local_end_x
            # else:
            #     continue
            # --- Step 1: Initialize temporary boundary variables ---
            temp_left_obstacle_x = local_start_x
            temp_right_obstacle_x = local_end_x
            local_center_x = (local_start_x + local_end_x) / 2 # Ensure local_center_x is defined

            # --- Step 2: Tentatively apply Plan B anchor ---
            if is_plan_b and 'last_clinic_right_edge_x' in locals():
                # Anchor left boundary to the last clinic's right edge
                temp_left_obstacle_x = max(local_start_x, last_clinic_right_edge_x)

            # --- Step 3: Find the nearest right obstacles based on the current scan line ---
            for obs in all_obstacles:
                obs_min_x, obs_min_y, obs_max_x, obs_max_y = obs
                if obs_min_y <= y_cursor <= obs_max_y and obs_min_x > local_center_x:
                        temp_right_obstacle_x = min(temp_right_obstacle_x, obs_min_x)

            # --- Step 4: Perform the conditional width check and set final boundaries ---
            available_corridor_width = temp_right_obstacle_x - temp_left_obstacle_x
            MIN_CORRIDOR_WIDTH = 3000.0

            if available_corridor_width < MIN_CORRIDOR_WIDTH:
                print(f"    -> WARNING: Corridor width ({available_corridor_width:.0f}mm) is < {MIN_CORRIDOR_WIDTH:.0f}mm. REVERTING to full room width.")
                
                # Revert to Plan A boundaries (full room width)
                left_obstacle_x = local_start_x
                right_obstacle_x = local_end_x # Start with the room edge
                
                # Recalculate right_obstacle_x using the full room width and right-side obstacles
                for obs in all_obstacles:
                    obs_min_x, obs_min_y, obs_max_x, obs_max_y = obs
                    if obs_min_y <= y_cursor <= obs_max_y and obs_min_x > local_center_x:
                            right_obstacle_x = min(right_obstacle_x, obs_min_x)

            else:
                # Use the calculated Plan B boundaries (anchored to clinic)
                left_obstacle_x = temp_left_obstacle_x
                right_obstacle_x = temp_right_obstacle_x # Use the already calculated right boundary

                   
            corridor_width = right_obstacle_x - left_obstacle_x
            walking_aisle = 800.0
            width_for_tables = corridor_width - (walking_aisle * 2)
            
            num_to_place_in_row = find_best_row_size(width_for_tables, standing_fxtr, len(fixture_queue))
            if num_to_place_in_row == 0:
                y_cursor -= 200; continue

            # --- Final Placement Logic (Unchanged) ---
            tables_for_this_row = [fixture_queue[i] for i in range(num_to_place_in_row)]
            total_row_width = (standing_fxtr.width * num_to_place_in_row) + (horizontal_gap * (num_to_place_in_row - 1))
            remaining_space = width_for_tables - total_row_width
            final_start_x = left_obstacle_x + walking_aisle + (remaining_space / 2)

            if is_valid_row(final_start_x, y_cursor, tables_for_this_row):
                current_x = final_start_x
                for _ in range(num_to_place_in_row):
                    fxtr = fixture_queue.popleft()
                    self.place_fixture(fxtr, (current_x, y_cursor, 0), 0, False)
                    placed_bboxes.append((current_x, y_cursor, current_x + fxtr.width, y_cursor + fxtr.height))
                    all_obstacles.append((current_x, y_cursor, current_x + fxtr.width, y_cursor + fxtr.height))
                    current_x += fxtr.width + horizontal_gap
                y_cursor -= (standing_fxtr.height + vertical_row_gap)
            else:
                print(f"    -> ⚠️ Could not place row at y={y_cursor:.0f}, spot was invalid. Trying next level.")
                y_cursor -= 200
        
        # --- Fallback Strategy (Unchanged) ---
        if fixture_queue:
            print(f"\n  -> {len(fixture_queue)} fixtures remain unplaced after main strategy. Consider a fallback.")

        print(f"\n-> Finished Standing Table Placement.")






#------ STANDING TABLE PLACEMENT FUNCTION FIRST PHASE  OF FINDING SPACE HERE ----
#------ STANDING TABLE PLACEMENT FUNCTION FIRST PHASE  OF FINDING SPACE HERE ----
    from typing import List, Tuple, Dict, Any, Optional
    from shapely.geometry import Point, LineString, box
    import math

    def _get_euro_center_exclusion_zone(self) -> Optional[Polygon]:
        """
        Calculates the primary retail zone that should be EXCLUDED from the
        standing table relocation analysis, preserving it for Euro centers.
        
        Returns:
            A Shapely Polygon representing the central exclusion zone, or None.
        """
        from ezdxf.bbox import extents
        from shapely.geometry import box

        # Find the top and bottom boundaries (QMS and original Standing Tables)
        qms_entities = [e for e in self.msp.query('INSERT') if "QMS_DESK" in e.dxf.name.upper()]
        standing_table_entities = [e for e in self.msp.query('INSERT') if "STANDING_TABLE" in e.dxf.name.upper()]

        if not qms_entities or not standing_table_entities:
            return None # Cannot define the zone without these anchors

        # Vertical boundaries
        bottom_y = extents(qms_entities).extmax.y
        top_y = extents(standing_table_entities).extmin.y

        # Horizontal boundaries (use the central 60% of the floorplan)
        total_width = self.cvc.max_x - self.cvc.min_x
        margin = total_width * 0.20 # Leave 20% on each side for aisles
        left_x = self.cvc.min_x + margin
        right_x = self.cvc.max_x - margin

        if bottom_y >= top_y or left_x >= right_x:
            return None
            
        print("  -> Defined a central 'Exclusion Zone' to preserve space for Euro Centers.")
        return box(left_x, bottom_y, right_x, top_y)


    


    def analyze_relocation_opportunities(self) -> Tuple[List[List[Dict[str, float]]], List[List[int]]]:
        """
        Analyzes the retail space (FOH) to find optimal locations for relocating standing tables.

        This function implements Phase 1 of the relocation planning strategy. It scans a
        predefined zone below the BOH/FOH separation line and generates two 2D grids:
        1.  A detailed grid containing the clearance gap to the nearest obstacle in four
            directions for each point.
        2.  A simplified "score" grid that rates each point from 0 to 4 based on its
            suitability for placing one or more standing tables.


        Returns:
            A tuple containing two 2D lists (list of lists):
            - The first list is the `gap_data_grid`.
            - The second list is the `score_grid`.
        """
        print("\n--- 🧠 Phase 1: Analyzing FOH for Standing Table Relocation Opportunities ---")

        # --- 1. DEFINE SCAN ZONE & PARAMETERS ---
        SCAN_DISTANCE = 5000.0  # Scan 5000mm away from the separation line.
        GRID_STEP = 200.0       # Scan in a 200mm x 200mm grid.

        # Find the BOH/FOH separation line to define the top of our scan zone.
        separator_line_entity = self.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
        if not separator_line_entity:
            print("  -> ⚠️ WARNING: 'RETAIL_SEPARATOR' line not found. Cannot perform analysis.")
            return [], []

        # The top of the scan zone is the Y-coordinate of the separator line.
        scan_start_y = separator_line_entity.dxf.start.y
        scan_end_y = scan_start_y - SCAN_DISTANCE
        print(f"  -> Scan Zone Defined: Y from {scan_start_y:.0f} down to {scan_end_y:.0f}.")

        # --- 2. GATHER ALL OBSTACLES ---
        # This includes all fixtures, partitions, and the main floorplan walls.
        exclusion_zone = self._get_euro_center_exclusion_zone()
        all_obstacles_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
        wall_segments = self.cvc.get_wall_segments()

        # --- 3. INITIALIZE DATA GRIDS ---
        gap_data_grid = []
        score_grid = []

        # --- 4. PERFORM THE SCAN ---
        y_coord = scan_start_y
        while y_coord > scan_end_y:
            # For each row, find the valid horizontal scan range within the floorplan.
            horizontal_slice = self.floorplan_polygon.intersection(
                LineString([(self.cvc.min_x - 100, y_coord), (self.cvc.max_x + 100, y_coord)])
            )
            if not isinstance(horizontal_slice, LineString) or horizontal_slice.is_empty:
                y_coord -= GRID_STEP
                continue

            x_start, _, x_end, _ = horizontal_slice.bounds
            
            gap_row = []
            score_row = []

            x_coord = x_start
            while x_coord < x_end:
                scan_point = Point(x_coord, y_coord)

                # ***** NEW: Check if the current point is inside the exclusion zone *****
                if exclusion_zone and exclusion_zone.contains(scan_point):
                    # If it's in the no-go zone, give it a score of 0 and skip analysis
                    gap_row.append({'gap_above': 0, 'gap_below': 0, 'gap_left': 0, 'gap_right': 0})
                    score_row.append(0)
                    x_coord += GRID_STEP
                    continue # Move to the next point
                # ************************************************************************

                # --- 4a. Calculate Raw Gaps ---
                # This is a simplified ray-casting to find the nearest obstacle.
                gaps = {
                    'above': SCAN_DISTANCE, 'below': SCAN_DISTANCE,
                    'left': SCAN_DISTANCE, 'right': SCAN_DISTANCE
                }

                for obs_box in all_obstacles_bboxes:
                    min_x, min_y, max_x, max_y = obs_box
                    # Check above
                    if min_x <= x_coord < max_x and y_coord < min_y:
                        gaps['above'] = min(gaps['above'], min_y - y_coord)
                    # Check below
                    if min_x <= x_coord < max_x and y_coord > max_y:
                        gaps['below'] = min(gaps['below'], y_coord - max_y)
                    # Check right
                    if min_y <= y_coord < max_y and x_coord < min_x:
                        gaps['right'] = min(gaps['right'], min_x - x_coord)
                    # Check left
                    if min_y <= y_coord < max_y and x_coord > max_x:
                        gaps['left'] = min(gaps['left'], x_coord - max_x)
                
                # Also check against the main walls
                gaps['left'] = min(gaps['left'], x_coord - self.cvc.min_x)
                gaps['right'] = min(gaps['right'], self.cvc.max_x - x_coord)
                gaps['above'] = min(gaps['above'], self.cvc.max_y - y_coord)
                gaps['below'] = min(gaps['below'], y_coord - self.cvc.min_y)


                # --- 4b. Adjust Gaps with Required Clearances ---
                # These values are subtracted to account for necessary walking paths.
                clearances = {
                    'wall': 50.0,
                    'separator': 950.0,
                    'fixture': 1050.0
                }
                
                # A more advanced version could detect the obstacle type.
                # For now, we apply a general 'fixture' clearance.
                adjusted_gaps = {
                    'gap_above': max(0, gaps['above'] - clearances['fixture']),
                    'gap_below': max(0, gaps['below'] - clearances['fixture']),
                    'gap_left': max(0, gaps['left'] - clearances['fixture']),
                    'gap_right': max(0, gaps['right'] - clearances['fixture']),
                }
                gap_row.append(adjusted_gaps)

                # --- 4c. Calculate Score (Revised Logic) ---
                score = 0

                # First, check if any individual gap is zero or less.
                # If so, the spot is unusable regardless of the total sum.
                if any(gap <= 0 for gap in adjusted_gaps.values()):
                    score = 0
                else:
                    # If all gaps are positive, calculate the score based on their sum.
                    # sum_gap = sum(adjusted_gaps.values())
                    
                    # New thresholds are adjusted for the sum instead of the average.
                    # (These are roughly the old thresholds multiplied by 4).
                    # if sum_gap >= 12000:
                    #     score = 4
                    # elif sum_gap >= 8000:
                    #     score = 3
                    # elif sum_gap >= 6000:
                    #     score = 2
                    # elif sum_gap >= 3600:
                    #     score = 1
                    avg_gap = sum(adjusted_gaps.values()) / 4.0

                    if avg_gap >= 3000:
                        score = 4
                    elif avg_gap >= 2000:
                        score = 3
                    elif avg_gap >= 1500:
                        score = 2
                    elif avg_gap >= 900:
                        score = 1
                
                score_row.append(score)

                x_coord += GRID_STEP
            
            gap_data_grid.append(gap_row)
            score_grid.append(score_row)
            y_coord -= GRID_STEP
            
        print(f"  -> Analysis Complete. Generated a {len(score_grid)}x{len(score_grid[0]) if score_grid else 0} suitability grid.")
        return gap_data_grid, score_grid


#------ STANDING TABLE PLACEMENT FUNCTION FIRST PHASE  OF FINDING SPACE HERE ----
#------ STANDING TABLE PLACEMENT FUNCTION FIRST PHASE  OF FINDING SPACE HERE ----


#------ STANDING TABLE PLACEMENT FUNCTION STOPPED HERE ----
#------ STANDING TABLE PLACEMENT FUNCTION STOPPED HERE ----
#------ STANDING TABLE PLACEMENT FUNCTION STOPPED HERE ----

    def relocate_standing_tables_anywhere(self, placed_bboxes: List[tuple]) -> bool:
        """
        [GLOBAL SEARCH VERSION] Relocates standing tables by searching the ENTIRE
        floorplan for the highest possible valid spots. It only commits the move
        if the new position is a true improvement over the original.
        """
        from ezdxf.bbox import extents
        from shapely.geometry import box
        import collections

        print("\n--- 🔄 Attempting to Relocate Standing Tables (Global Search) ---")

        # --- STEP 1: ANALYZE ORIGINAL POSITION (Unchanged) ---
        standing_table_entities = [e for e in self.msp.query('INSERT') if "STANDING_TABLE" in e.dxf.name.upper()]
        if not standing_table_entities:
            print("  -> No standing tables found to relocate.")
            return False

        original_bbox = extents(standing_table_entities)
        original_bottom_y = original_bbox.extmin.y
        print(f"  -> Original standing tables bottom boundary is at y={original_bottom_y:.0f}")

        standing_table_bboxes_tuples = [(b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y) for e in standing_table_entities if (b := extents([e]))]
        original_bboxes = list(placed_bboxes)
        temp_placed_bboxes = [b for b in original_bboxes if b not in standing_table_bboxes_tuples]
        
        # --- STEP 2: SIMULATE NEW POSITION USING A GLOBAL GRID SEARCH ---
        print("  -> Simulating new positions using a global top-down grid search...")
        standing_fxtr = Fixture.Fixture("Standing_table", self.fixture_dict["Standing_table"]["path"])
        
        # Define search parameters
        search_start_y = self.cvc.max_y - standing_fxtr.height
        search_end_y = self.cvc.min_y
        search_start_x = self.cvc.min_x
        search_end_x = self.cvc.max_x - standing_fxtr.width
        step = 100  # Grid search step in mm

        simulated_new_positions = []
        temp_obstacles_for_sim = list(temp_placed_bboxes)
        
        for i, table_entity in enumerate(standing_table_entities):
            found_spot_for_table = False
            # Search from top to bottom, left to right, to find the highest, left-most spot
            for y_try in range(int(search_start_y), int(search_end_y), -step):
                for x_try in range(int(search_start_x), int(search_end_x), step):
                    candidate_box = box(x_try, y_try, x_try + standing_fxtr.width, y_try + standing_fxtr.height)
                    is_overlapping = any(candidate_box.intersects(box(*b)) for b in temp_obstacles_for_sim)
                    is_inside = self.floorplan_polygon.contains(candidate_box)

                    if is_inside and not is_overlapping:
                        # Found a valid spot for this table
                        simulated_new_positions.append({'entity': table_entity, 'pos': (x_try, y_try, 0)})
                        new_bbox = (x_try, y_try, x_try + standing_fxtr.width, y_try + standing_fxtr.height)
                        temp_obstacles_for_sim.append(new_bbox)
                        found_spot_for_table = True
                        print(f"    -> Found simulated spot for table #{i+1} at (x={x_try:.0f}, y={y_try:.0f})")
                        break  # Stop searching for this table
                if found_spot_for_table:
                    break  # Move to the next table

        if len(simulated_new_positions) != len(standing_table_entities):
            print(f"  -> ⚠️ Simulation failed: Could not find valid new spots for all {len(standing_table_entities)} tables.")
            return False

        # --- STEP 3: COMPARE AND COMMIT (Unchanged) ---
        new_bottom_y = min(p['pos'][1] for p in simulated_new_positions)
        print(f"  -> Best new position found. New bottom boundary would be at y={new_bottom_y:.0f}")

        if new_bottom_y > original_bottom_y:
            print(f"  -> ✅ Improvement detected ({new_bottom_y:.0f} > {original_bottom_y:.0f}). Committing the move.")
            for move_op in simulated_new_positions:
                move_op['entity'].dxf.insert = move_op['pos']
            placed_bboxes[:] = temp_obstacles_for_sim
            return True
        else:
            print(f"  -> ❌ Relocation aborted: Best new position (y={new_bottom_y:.0f}) would not improve space (current is y={original_bottom_y:.0f}).")
            return False

    def relocate_standing_tables_to_aisles_og(self, placed_bboxes: List[tuple]) -> bool:
        """
        [ROBUST VERSION 2] Attempts to find and move all standing tables to the side aisles.
        It now anchors the search from the vertical center of the room to avoid Euro Center conflicts.
        Returns True on success, False on failure.
        """
        from ezdxf.bbox import extents
        from shapely.geometry import box
        import collections

        print("\n--- 🔄 Attempting to Relocate Standing Tables to Side Aisles (Robust Search V2) ---")

        # 1. Find all standing table entities and their original bboxes
        standing_table_entities = [e for e in self.msp.query('INSERT') if "STANDING_TABLE" in e.dxf.name.upper()]
        if not standing_table_entities:
            print("  -> No standing tables found to relocate.")
            return False

        standing_table_bboxes = [(bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y) for e in standing_table_entities if (bbox := extents([e]))]

        # 2. Temporarily remove their bboxes from the main obstacle list
        original_bboxes = list(placed_bboxes)
        temp_placed_bboxes = [b for b in original_bboxes if b not in standing_table_bboxes]

        print(f"  -> Temporarily removed {len(standing_table_entities)} standing tables as obstacles to find new spots.")

        # 3. Load fixture data
        standing_fxtr = Fixture.Fixture("Standing_table", self.fixture_dict["Standing_table"]["path"])

        # 4. Define the side aisle columns
        aisle_gap = 400.0
        vertical_gap = 1200.0
        
        left_col_x = self.cvc.min_x + aisle_gap
        right_col_x = self.cvc.max_x - aisle_gap - standing_fxtr.width
        
        # === THIS IS THE CORRECTED LOGIC ===
        # Instead of anchoring to QMS, we find the room's vertical center.
        # This pushes the tables higher up, clearing the Euro Center placement zone.
        room_vertical_center = (self.cvc.min_y + self.cvc.max_y) / 2.0
        search_start_y = room_vertical_center
        print(f"  -> Anchoring aisle search from room's vertical center (y={search_start_y:.0f}) to avoid conflicts.")
        # === END OF CORRECTION ===
        
        potential_columns = [
            {'side': 'left', 'x': left_col_x},
            {'side': 'right', 'x': right_col_x}
        ]

        # 5. Try to find new positions for all tables
        new_positions = []
        
        def is_spot_valid(x, y, fixture, current_obstacles):
            candidate_box = box(x, y, x + fixture.width, y + fixture.height)
            is_overlapping = any(candidate_box.intersects(box(*b)) for b in current_obstacles)
            is_inside = self.floorplan_polygon.contains(candidate_box)
            return is_inside and not is_overlapping

        placed_tables_count = 0
        for col in potential_columns:
            y_cursor = search_start_y
            while placed_tables_count < len(standing_table_entities):
                if y_cursor > self.cvc.max_y - standing_fxtr.height:
                    break

                if is_spot_valid(col['x'], y_cursor, standing_fxtr, temp_placed_bboxes):
                    table_entity = standing_table_entities[placed_tables_count]
                    new_pos = {'entity': table_entity, 'pos': (col['x'], y_cursor, 0)}
                    new_positions.append(new_pos)
                    
                    temp_placed_bboxes.append((col['x'], y_cursor, col['x'] + standing_fxtr.width, y_cursor + standing_fxtr.height))
                    
                    y_cursor += standing_fxtr.height + vertical_gap
                    placed_tables_count += 1
                else:
                    y_cursor += 100

        # 6. Check if all tables were successfully relocated
        if len(new_positions) < len(standing_table_entities):
            print(f"  -> ⚠️ Relocation failed: Could only find valid spots for {len(new_positions)} of {len(standing_table_entities)} tables.")
            placed_bboxes[:] = original_bboxes
            return False

        # 7. If successful, execute the move and update bboxes
        print("  -> ✅ All standing tables found valid new positions. Executing move.")
        for move_op in new_positions:
            move_op['entity'].dxf.insert = move_op['pos']
        
        placed_bboxes[:] = temp_placed_bboxes
        return True
#------ STANDING TABLE PLACEMENT FUNCTION STOPPED HERE ----
#------ STANDING TABLE PLACEMENT FUNCTION STOPPED HERE ----

#------ LENSBAR PLACEMENT FUNCTION STARTED HERE FOR FUTURE SCOPE NOT USING NOW ----

    def place_lensbar(self, placed_bboxes):
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
            config = self.fixtures.get("floor_fixtures", {})
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
                        self.place_fixture(lensbar_fxtr, (x, y, 0), 0, False)
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

#------ LENSBAR PLACEMENT FUNCTION STOPPED HERE ----

#------ eye_massage_area PLACEMENT FUNCTION STARTED HERE ----

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

#------ eye_massage_area PLACEMENT FUNCTION STOPPED HERE ----


#------ drop_box PLACEMENT FUNCTION STARTED HERE ----

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

#------ drop_box PLACEMENT FUNCTION STOPPED HERE ----

#------ CORIAN TABLE SET PLACEMENT FUNCTION STARTED HERE ----

    def place_corian_table_set(self, placed_bboxes):
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



#------ CORIAN TABLE SET PLACEMENT FUNCTION STOPPED  HERE ----



# CATEGORY :- TV SCREENS
#---- TV SCREENS PLACEMENT FUNCTION STARTED HERE ----

    def _get_top_retail_boundary_y(self) -> float:
        """
        Finds the lowest Y-coordinate of all non-retail fixtures (clinics, BOH)
        to determine the top boundary of the retail area.
        """
        from ezdxf.bbox import extents

        # Query for all fixtures that define the back-of-house area
        non_retail_entities = [
            e for e in self.msp.query('INSERT') if
            "CLINIC" in e.dxf.name.upper() or 
            "BOH" in e.dxf.name.upper() or 
            "PICK_UP_WINDOW" in e.dxf.name.upper()
        ]
        
        if not non_retail_entities:
            print("  -> WARNING: No non-retail fixtures found to define the top of the retail space.")
            # Fallback to a percentage of the room height if no anchors are found
            return self.cvc.max_y - ((self.cvc.max_y - self.cvc.min_y) * 0.3)

        # Calculate the combined bounding box and find the lowest point
        non_retail_bbox = extents(non_retail_entities)
        return non_retail_bbox.extmin.y

    def calculate_dynamic_tv_count(self) -> int:
        """
        Calculates the number of TVs based on the height of the retail space (FOH).
        
        Rules:
        - Retail Height is from the bottom wall to the bottom of the non-retail fixtures.
        - If Retail Height > 6m, TVs are placed every 6m.
        - One TV is always placed at the facade (bottom wall).
        """
        import math
        print("\n--- 📺 Calculating Dynamic TV Count ---")

        # 1. Determine the boundaries of the retail space
        top_boundary = self._get_top_retail_boundary_y()
        bottom_boundary = self.cvc.min_y
        retail_height = top_boundary - bottom_boundary

        print(f"  -> Calculated Retail Height (FOH): {retail_height:.0f} mm")

        # Define thresholds in millimeters
        MINIMUM_SPACE_FOR_ONE_TV = 3000  # 3 meters
        SIX_METERS = 6000

        # 2. Apply the counting logic based on the available height
        tv_count = 0
        if retail_height < MINIMUM_SPACE_FOR_ONE_TV:
            tv_count = 0
            print(f"  -> Retail height is less than {MINIMUM_SPACE_FOR_ONE_TV}mm. TV count set to 0.")
        elif retail_height < SIX_METERS:
            tv_count = 1
            print(f"  -> Retail height is less than 6m. TV count set to 1 (at facade).")
        else:
            # Place one at the facade (0m) and then one for every 6m interval
            tv_count = math.floor(retail_height / SIX_METERS) + 1
            print(f"  -> Retail height is > 6m. TV count set to {tv_count}.")
            
        return int(tv_count)


    def place_tv_screens(self, placed_bboxes: List[tuple], primary_side: str = "left"):
        """
        Places TV screens using a hybrid strategy.
        - The first two TVs use a multi-spot priority search.
        - Subsequent TVs are stacked using a resilient downward search.
        """
        # from Fixture import Fixture
        import collections
        from ezdxf.math import Vec2

        print("\n--- 🧠 Placing TV Screens with Hybrid Priority/Stacking Strategy ---")
        
        try:
            screen_config = self.fixtures.get("screen_fixtures", {})
            screens_to_place = collections.deque([
                Fixture.Fixture(name, self.fixture_dict[name]["path"])
                for name, count in screen_config.items() if count > 0
                for _ in range(count)
            ])
            if not screens_to_place:
                print("  -> SKIPPED: No screen fixtures specified.")
                return
        except Exception as e:
            print(f"  -> 🔥 ERROR: Could not load screen fixtures: {e}")
            return

        placed_tv_count = 0
        last_tv_details = None 
        euro_spot_used = False

        while screens_to_place:
            screen = screens_to_place.popleft()
            is_placed = False

            # --- STRATEGY 1: Priority search for the first two TVs ---
            if placed_tv_count < 2:
                print(f"\n  -> Searching for spot for TV #{placed_tv_count + 1} (Priority Search)...")
                
                prime_spots = []
                secondary_side = "right" if primary_side == "left" else "left"

                def add_spot(spot_data, description):
                    if spot_data:
                        if isinstance(spot_data, tuple):
                            spot_data = {"target_center": spot_data[0], "angle_deg": spot_data[1]}
                        spot_data["description"] = description
                        prime_spots.append(spot_data)
                
                # --- This is the complete, recommended priority list ---
                add_spot(self._find_bottom_wall_corner_spot(secondary_side, screen), f"Bottom-{secondary_side} Corner")
                add_spot(self._find_spot_above_first_euro(placed_bboxes), "On First Euro Centre Row")
                add_spot(self._find_spot_stacked_above_euros(screen), "Stacked Above Euro Row")

                # --- ADD THESE LINES BACK IN HERE ---
                add_spot(self._find_bottom_wall_corner_spot(primary_side, screen), f"Bottom-{primary_side} Corner")
                add_spot(self._find_spot_between_euros(), "Between Euro Centres")
                add_spot(self._find_other_long_wall_spots([primary_side, secondary_side], screen)[0] if self._find_other_long_wall_spots([primary_side, secondary_side], screen) else None, "Center of Fallback Wall")
                # --- END OF ADDITION ---
                for i, spot in enumerate(prime_spots):
                    force_placement = (spot["description"] == "On First Euro Centre Row" and not euro_spot_used)
                    validation_bboxes = [b for b in placed_bboxes if "ignore_bbox" not in spot or b != spot["ignore_bbox"]]
                    new_bbox = self._validate_and_place_at_point_tv(screen, spot["target_center"], spot["angle_deg"], validation_bboxes, force=force_placement)
                    
                    if new_bbox:
                        placed_bboxes.append(new_bbox)
                        print(f"    ✅ Placed TV #{placed_tv_count + 1} in spot: {spot['description']}.")
                        is_placed = True
                        placed_tv_count += 1
                        last_tv_details = {"bbox": new_bbox, "center": spot["target_center"]}
                        if force_placement: euro_spot_used = True
                        break

            # --- STRATEGY 2: Call the dedicated stacking function ---
            else:
                is_placed, new_details = self._place_stacked_tv(screen, placed_bboxes, last_tv_details, placed_tv_count)
                if is_placed:
                    placed_tv_count += 1
                    last_tv_details = new_details # Update the anchor for the *next* stacked TV
            
            if not is_placed:
                print(f"    -> ⚠️ Could not place TV #{placed_tv_count + 1}; no suitable spots found.")

        print(f"\n-> Finished TV Placement: Placed {placed_tv_count} screen(s).")


                
    def _find_bottom_wall_corner_spot(self, side: str, screen: 'Fixture') -> Optional[Tuple[Vec2, float]]:
        """Finds a spot inset from a corner of the bottom wall, flush against it."""
        from shapely.geometry import Point
        from ezdxf.math import Vec2
        
        bottom_wall = self._get_wall_details('bottom')
        if not bottom_wall: return None

        p1, p2 = bottom_wall["start_point"], bottom_wall["end_point"]
        wall_vector = bottom_wall["vector"].normalize()
        wall_length = bottom_wall["length"]
        inset_dist = wall_length * 0.15 # Inset 15% from the corner

        anchor_point = p1 if side == "left" else p2
        direction_multiplier = 1 if side == "left" else -1
        
        target_point_on_wall = anchor_point + (wall_vector * inset_dist * direction_multiplier)
        
        inward_normal = wall_vector.orthogonal()
        if not self.floorplan_polygon.contains(Point(target_point_on_wall + inward_normal)):
            inward_normal = -inward_normal
            
        # UPDATED LINE: The offset is now half the screen's depth, removing any gap.
        offset_from_wall = screen.height / 2.0
        target_center = target_point_on_wall + inward_normal * offset_from_wall
        
        return (target_center, bottom_wall["angle_deg"])
    
    def _find_spot_above_first_euro(self, placed_bboxes) -> Optional[dict]:
        """
        Finds a spot centered ON the entire first row of Euro Centre fixtures.
        Returns a dictionary with the target center and the bounding box of the entire row to ignore.
        """
        from ezdxf.bbox import extents
        from ezdxf.math import Vec2
        import math

        all_euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
        if not all_euro_entities: 
            return None

        # 1. Find the Euro with the lowest Y-coordinate to identify the first row's height
        first_euro_in_row = min(all_euro_entities, key=lambda e: e.dxf.insert.y)
        first_row_y = first_euro_in_row.dxf.insert.y
        
        # 2. Define a tolerance to find all other fixtures in the same horizontal row
        y_tolerance = 100.0 
        
        # 3. Collect all entities that belong to the first row
        first_row_entities = [
            e for e in all_euro_entities 
            if math.isclose(e.dxf.insert.y, first_row_y, abs_tol=y_tolerance)
        ]

        if not first_row_entities:
            # Fallback in case something goes wrong, though unlikely
            return None
        
        # 4. Calculate the combined bounding box of the entire row
        row_bbox = extents(first_row_entities)

        # 5. The new target is the center of this entire row
        target_center = row_bbox.center
        
        # Return the necessary info for placement
        return {
            "target_center": target_center,
            "angle_deg": 0.0,
            # This tells the main function to ignore the entire row for the overlap check
            "ignore_bbox": (row_bbox.extmin.x, row_bbox.extmin.y, row_bbox.extmax.x, row_bbox.extmax.y)
        }
    

    def _place_stacked_tv(self, screen: 'Fixture', placed_bboxes: List[tuple], last_tv_details: dict, placed_tv_count: int):
        """
        Handles the resilient stacking logic for the 3rd TV and onwards.
        Searches downwards from an ideal gap until a valid spot is found.
        Returns a tuple: (was_placed_boolean, updated_last_tv_details_dict).
        """
        from ezdxf.math import Vec2

        if not last_tv_details:
            print("    -> ⚠️ SKIPPING: Cannot stack TV because no previous TV was placed.")
            return False, None

        last_bbox = last_tv_details["bbox"]
        last_center_x = last_tv_details["center"].x
        
        gap = 6000.0
        search_step = -100.0
        
        ideal_y = last_bbox[3] + gap + (screen.height / 2)
        search_limit_y = last_bbox[3] + (screen.height / 2) + 50.0
        
        current_y = ideal_y
        print(f"    -> Ideal target is {gap}mm above last TV. Starting search at y={current_y:.0f}")

        while current_y > search_limit_y:
            target_center = Vec2(last_center_x, current_y)
            new_bbox = self._validate_and_place_at_point_tv(screen, target_center, 0.0, placed_bboxes)
            
            if new_bbox:
                placed_bboxes.append(new_bbox)
                print(f"    ✅ Placed TV #{placed_tv_count + 1} using stacking logic at y={current_y:.0f}.")
                new_details = {"bbox": new_bbox, "center": target_center}
                return True, new_details # Return success and the new details
            
            current_y += search_step
        
        return False, None # Return failure
    

    def _find_spot_stacked_above_euros(self, screen: 'Fixture', gap: float = 800.0) -> Optional[dict]:
        """
        Finds a spot for a TV screen a specific 'gap' distance above the first row of Euro Centres.
        This creates a vertically stacked placement opportunity.
        """
        from ezdxf.bbox import extents
        from ezdxf.math import Vec2
        import math

        all_euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
        if not all_euro_entities: 
            return None

        # Find the first row of Euro Centres to use as an anchor
        first_euro_in_row = min(all_euro_entities, key=lambda e: e.dxf.insert.y)
        first_row_y = first_euro_in_row.dxf.insert.y
        y_tolerance = 100.0
        first_row_entities = [
            e for e in all_euro_entities 
            if math.isclose(e.dxf.insert.y, first_row_y, abs_tol=y_tolerance)
        ]

        if not first_row_entities:
            return None
        
        # Get the bounding box of the entire row
        row_bbox = extents(first_row_entities)

        # Calculate the target center:
        # X is horizontally centered with the row below.
        # Y is the top edge of the row + the gap + half the screen's height to center the screen.
        target_center_x = row_bbox.center.x
        target_center_y = row_bbox.extmax.y + gap + (screen.height / 2)
        
        target_center = Vec2(target_center_x, target_center_y)
        
        return {
            "target_center": target_center,
            "angle_deg": 0.0,
        }
    
    
    def _find_spot_between_euros(self) -> Optional[Tuple[Vec2, float]]:
        """Finds a spot in the vertical gap between the first two Euro Centres."""
        euro_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
        if len(euro_entities) < 2: return None

        euro_bboxes = sorted([extents([e]) for e in euro_entities], key=lambda b: b.extmin.y)
        
        gap_center_y = (euro_bboxes[0].extmax.y + euro_bboxes[1].extmin.y) / 2.0
        center_x = (self.cvc.min_x + self.cvc.max_x) / 2.0
        
        target_center = Vec2(center_x, gap_center_y)
        return (target_center, 0.0)


    def _find_other_long_wall_spots(self, sides_to_exclude: List[str], screen: 'Fixture') -> List[Tuple[Vec2, float]]:
        """Finds the center of any long wall that is not on an excluded side, flush against it."""
        from shapely.geometry import Point
        
        spots = []
        for side in ["top", "left", "right", "bottom"]:
            if side in sides_to_exclude: continue
            
            wall = self._get_wall_details(side)
            if wall and wall["length"] > 2000: # Only consider walls longer than 2m
                wall_vector = wall["vector"].normalize()
                center_on_wall = wall["start_point"] + wall_vector * (wall["length"] / 2.0)
                
                inward_normal = wall_vector.orthogonal()
                if not self.floorplan_polygon.contains(Point(center_on_wall + inward_normal)):
                    inward_normal = -inward_normal
                
                # UPDATED LINE: The offset is now half the screen's depth.
                offset_from_wall = screen.height / 2.0
                target_center = center_on_wall + inward_normal * offset_from_wall
                
                spots.append((target_center, wall["angle_deg"]))
        return spots
    
    # In DXF_Controller.py
    def _validate_and_place_at_point_tv(self, fixture, target_center, angle_deg, placed_bboxes, force=False):
        """
        Validates and places a fixture. On success, it returns the new bounding box tuple.
        On failure, it returns None.
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

        if force:
            is_inside = True
            is_overlapping = False
        else:
            is_inside = self.floorplan_polygon.contains(fixture_polygon.centroid)
            is_overlapping = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

        if is_inside and not is_overlapping:
            rotated_offset = local_center.rotate(math.radians(angle_deg))
            final_insert_point = target_center - rotated_offset
            self.place_fixture(fixture, (final_insert_point.x, final_insert_point.y, 0), angle_deg, True)
            
            new_bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)
            # --- THIS LINE IS REMOVED ---
            # placed_bboxes.append(new_bbox_tuple) 
            return new_bbox_tuple # Return the bbox on success
            
        return None # Return None on failuree

    
    #---new test tv placement
    #---new test tv placement

#---- TV SCREENS PLACEMENT FUNCTION FINISHED HERE ----

#---------------------PORTRAIT MODE FIXTURE PLACEMENT FINISHED FROM HERE -----------------------------------------------------------
#---------------------PORTRAIT MODE FIXTURE PLACEMENT FINISHED FROM HERE -----------------------------------------------------------
#---------------------PORTRAIT MODE FIXTURE PLACEMENT FINISHED FROM HERE -----------------------------------------------------------

#---------------------LANDSCAPE MODE FIXTURE PLACEMENT STARTS FROM HERE -----------------------------------------------------------
#---------------------LANDSCAPE MODE FIXTURE PLACEMENT STARTS FROM HERE -----------------------------------------------------------
#---------------------LANDSCAPE MODE FIXTURE PLACEMENT STARTS FROM HERE -----------------------------------------------------------

# CATEGORY :-  CLINIC


##------ CLINIC  PLACEMENT FUNCTION STARTED HERE ----


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


#------ CLINIC  PLACEMENT FUNCTION FINISHED HERE ----

#---CATEGORY :- Back Of House(BOH)
#---- BOH PLACEMENT SAME AS PORTRAIT ----

#---CATEGORY :- Seating (clinic/AR)
#---- Seating (clinic/AR) PLACEMENT SAME AS PORTRAIT ----

#---CATEGORY :- wall Fixtures/Euro Centers/Lensbars

#------  EURO_CENTER/LENSBAR PLACEMENT FUNCTION STARTED HERE ----

    def place_fixtures_iteratively_with_dynamic_stacks(self, placed_bboxes: List[tuple]) -> None:
        """
        Places both Lensbar and Euro_centre fixtures iteratively. This definitive version
        uses a robust helper function to guarantee correct centering of all rotated stacks.
        """
        # from Fixture import Fixture
        from shapely.geometry import box, LineString
        import math
        import collections

        print("\n--- 🧠 Placing Fixtures with Definitive 'Smart Stacking' Strategy ---")

        # --- 1. Architectural Rules (Unchanged) ---
        GAP_LENS_TO_LENS = 800.0
        GAP_LENS_TO_EURO = 800.0
        GAP_EURO_TO_EURO = 800.0
        LEFT_AISLE_PERCENTAGE = self._calculate_dynamic_left_aisle_percentage()
        VERTICAL_BUFFER_PERCENTAGE = 0.30

        # --- 2. Load fixtures into a UNIFIED QUEUE (Unchanged) ---
        config = self.fixtures.get("floor_fixtures", {})
        euro_count = config.get("Euro_centre", 0)
        lensbar_count = config.get("Lensbar", 0)
        if euro_count + lensbar_count == 0: return

        fixture_queue = collections.deque()
        try:
            if lensbar_count > 0:
                lensbar_fxtr = Fixture.Fixture("Lensbar", self.fixture_dict["Lensbar"]["path"])
                fixture_queue.extend([lensbar_fxtr] * lensbar_count)
            if euro_count > 0:
                euro_fxtr = Fixture.Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"])
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
        # from Fixture import Fixture
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
                aisle_pct = 0.40 # Use a spacious 40% aisle
                print(f"      -> Count is LOW. Using a spacious {aisle_pct:.0%} left aisle.")
            
            elif total_fixture_count <= 10: # Medium Congestion
                aisle_pct = 0.30 # Use a standard 30% aisle
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
    

#------ wall_fixtures PLACEMENT FUNCTION STARTED HERE ----

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
        size_mapping = {
            "jj_fixture_family": ["jj_fixture_large", "jj_fixture_medium"],
            "vc_fixture_family": ["vc_fixture_large", "vc_fixture_medium"],
            "jj_super_hybrid_family": ["jj_super_hybrid_large", "jj_super_hybrid_medium"],
            "window_family": ["window_3_section", "window_1_section"],
        }
        # 1. SETUP
        # wall_fixtures_config = self.fixtures.get("wall_fixtures", {})
        # master_queue = collections.deque()


        # for name, count in wall_fixtures_config.items():
        #     if count > 0:
        #         master_queue.extend([(name, 1)] * count)
        family_totals = self.fixtures.get("wall_fixtures", {})
        master_queue = collections.deque()

        for family_name, total_count in family_totals.items():
            if total_count > 0 and family_name in size_mapping:
                available_sizes = size_mapping[family_name]
                remaining_count = total_count
                
                # Heuristic: Fill with ~70% large fixtures first
                num_large = math.ceil(remaining_count * 0.7)
                
                # Add large fixtures to the queue
                for _ in range(int(num_large)):
                    if remaining_count > 0:
                        master_queue.append((available_sizes[0], 1))
                        remaining_count -= 1
                
                # Add remaining (medium/small) fixtures
                if remaining_count > 0 and len(available_sizes) > 1:
                    for _ in range(int(remaining_count)):
                        master_queue.append((available_sizes[1], 1))
        
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
            # if best_match_key and (self.fixture_dict[best_match_key].get("type") == 'boh' or self.fixture_dict[best_match_key].get("type") == 'boh_preset'):
                # boh_entities.append(entity)
            if best_match_key and (self.fixture_dict[best_match_key].get("type") in ('boh', 'boh_preset')):
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

    # def _get_fixture_aabb(self, fixture, target_center, angle_deg, xscale=1.0, yscale=1.0):
    #     """[UPGRADED] Helper to quickly get the AABB of a fixture at a potential location, including mirroring."""
    #     from ezdxf.math import Matrix44, Vec2, BoundingBox2d
    #     import math
    #     local_center = fixture.bounding_box.center
    #     transform = Matrix44.chain(
    #         Matrix44.translate(-local_center.x, -local_center.y, 0),
    #         Matrix44.scale(xscale, yscale, 1.0), # Apply mirroring
    #         Matrix44.z_rotate(math.radians(angle_deg)),
    #         Matrix44.translate(target_center.x, target_center.y, 0)
    #     )
    #     world_corners = list(transform.transform_vertices(fixture.bounding_box.rect_vertices()))
    #     return BoundingBox2d(world_corners)

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
    


#------ wall_fixtures PLACEMENT FUNCTION FINISHED HERE ----

# --CATEGORY :- Remaining Floor fixtures

#------ discussion_tables PLACEMENT FUNCTION STARTED HERE ----

    def place_discussion_tables_landscape(self, placed_bboxes):
        """
        Places discussion tables in a flexible manner above and below Euro Centre
        fixtures, treating all available spots as a pool. Any tables that cannot
        be placed are returned for fallback placement.
        """
        # from Fixture import Fixture
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
            table_config = self.fixtures.get("floor_fixtures_table", {})
            for name, total_count in table_config.items():
                if "Discussion_table" in name and total_count > 0:
                    fxtr = Fixture.Fixture(name, self.fixture_dict[name]["path"])
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


#------ discussion_tables PLACEMENT FUNCTION FINISHED HERE ----


#------ pos_ar PLACEMENT FUNCTION STARTED HERE ----

    def place_pos_ar_landscape(self, placed_bboxes):
        """
        Places the POS and AR units with an intelligent, conditional anchoring strategy.
        It determines the right-most fixture group to anchor to and searches for a
        valid spot, ensuring no overlaps.
        """
        # from Fixture import Fixture
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

            pos_fxtr = Fixture.Fixture(selected_pos_name, self.fixture_dict[selected_pos_name]["path"])
            ar_fxtr = Fixture.Fixture("AR", self.fixture_dict["AR"]["path"])

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

#------ pos_ar PLACEMENT FUNCTION FINISHED HERE ----

#------ QMS/GREETR PLACEMENT FUNCTION STARTED HERE ----

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

    #------ QMS/GREETR PLACEMENT FUNCTION NEW_SETUP FOR QMS/GREETR HERE ----
    #------ QMS/GREETR PLACEMENT FUNCTION NEW_SETUP FOR QMS/GREETR HERE ----

    def _get_facade_center_x(self) -> float:
        """
        [CORRECTED] Finds the horizontal center of the building's facade.
        This reuses the 'find_bottom_chain' logic to identify the front wall.
        """
        corners = self.cvc.corners
        if len(corners) < 3:
            return (self.cvc.min_x + self.cvc.max_x) / 2 # Fallback

        def find_bottom_chain(pts, slope_tol=0.05, y_tol=100):
            n = len(pts)
            ys = [p[1] for p in pts]
            min_y = min(ys)
            is_bottom = [False] * n
            for i in range(n):
                p1, p2 = pts[i], pts[(i + 1) % n]
                dy, dx = p2[1] - p1[1], p2[0] - p1[0]
                near_min = (abs(p1[1] - min_y) <= y_tol) and (abs(p2[1] - min_y) <= y_tol)
                slope_ok = abs(dy) <= slope_tol * max(1.0, abs(dx))
                if near_min and slope_ok:
                    is_bottom[i] = True
            return is_bottom

        is_facade_segment = find_bottom_chain(corners)
        
        # <<< FIX IS HERE >>>
        # Collect ALL points (start and end) of every facade segment.
        facade_points = []
        for i, is_facade in enumerate(is_facade_segment):
            if is_facade:
                facade_points.append(corners[i])
                facade_points.append(corners[(i + 1) % len(corners)])
        # <<< END OF FIX >>>

        if not facade_points:
            # Fallback to the center of the whole building if no facade is found
            return (self.cvc.min_x + self.cvc.max_x) / 2

        # Find the min and max x-coordinates of the entire facade
        min_x = min(p[0] for p in facade_points)
        max_x = max(p[0] for p in facade_points)
        
        facade_center_x = (min_x + max_x) / 2
        print(f"  -> Facade center X-coordinate correctly calculated at: {facade_center_x:.0f}")
        return facade_center_x


    def place_qms_at_entrance_center(self, placed_bboxes):
        """
        [MODIFIED] Places QMS desks anchored to the bottom wall and horizontally
        centered relative to the facade's midpoint.
        """
        from shapely.geometry import box, LineString

        # 1. SETUP (Unchanged)
        config = self.fixtures.get("table_fixtures", {})
        qms_count = config.get("QMS_desk", 0)
        if qms_count <= 0:
            return

        print(f"\n--- Attempting to place {qms_count} QMS Desk(s) at Entrance (Facade Centered) ---")

        try:
            qms_fxtr = Fixture.Fixture("QMS_desk", self.fixture_dict["QMS_desk"]["path"])
        except Exception as e:
            print(f"🔥 Could not load QMS_desk fixture: {e}")
            return

        # Helper function for validation (Unchanged)
        def is_valid_spot(fixture, x, y):
            w, h = fixture.width, fixture.height
            candidate_box = box(x, y, x + w, y + h)
            is_overlapping = any(candidate_box.intersects(box(*bbox)) for bbox in placed_bboxes)
            is_inside = self.floorplan_polygon.contains(candidate_box)
            return is_inside and not is_overlapping

        # 2. CALCULATE VERTICAL POSITION (Unchanged)
        bottom_margin = self._calculate_dynamic_qms_margin()
        start_y = self.cvc.min_y + bottom_margin
        print(f"  -> Anchoring to bottom wall. Calculated dynamic start Y-position: {start_y:.0f}")

        # <<< MODIFICATION START >>>
        # 3. RESILIENT HORIZONTAL SEARCH ANCHORED TO FACADE CENTER
        
        # Instead of using the local width, we get the facade's absolute center X.
        facade_center_x = self._get_facade_center_x()
        
        # Calculate the ideal starting X for the desk so its center aligns with the facade's center.
        ideal_x = facade_center_x - (qms_fxtr.width / 2)
        # <<< MODIFICATION END >>>

        first_desk_placed = False
        final_start_x, final_start_y = 0, 0
        search_offset = 0
        # The max search range can be based on the overall room width
        max_search = (self.cvc.max_x - self.cvc.min_x) / 2

        # The resilient search logic remains the same, but now starts from the new 'ideal_x'
        while not first_desk_placed and search_offset < max_search:
            for sign in [1, -1]:
                if sign == -1 and search_offset == 0: continue
                test_x = ideal_x + search_offset * sign
                if is_valid_spot(qms_fxtr, test_x, start_y):
                    final_start_x, final_start_y = test_x, start_y
                    first_desk_placed = True
                    break
            if first_desk_placed: break
            search_offset += 100

        if not first_desk_placed:
            print("⚠️ Could not find a clear spot for the first QMS desk after searching.")
            return

        # 4. EXECUTE PLACEMENT (Center-Out Pattern - Unchanged)
        # (The rest of this function's logic for placing multiple desks remains the same)
        qms_placed_count = 0
        placed_qms_bboxes = []

        self.place_fixture(qms_fxtr, (final_start_x, final_start_y, 0), 0, False)
        bbox_coords = (final_start_x, final_start_y, final_start_x + qms_fxtr.width, final_start_y + qms_fxtr.height)
        placed_bboxes.append(bbox_coords)
        placed_qms_bboxes.append(bbox_coords)
        qms_placed_count += 1
        print(f"✅ Placed central QMS_desk #{qms_placed_count} at ({final_start_x:.0f}, {final_start_y:.0f}).")

        if qms_count > 1:
            max_gap, min_gap, congestion_threshold = 500, 250, 5
            if qms_count <= 3: gap_horizontal = max_gap
            elif qms_count >= congestion_threshold: gap_horizontal = min_gap
            else: gap_horizontal = max_gap - ((qms_count - 2) / (congestion_threshold - 2) * (max_gap - min_gap))
            
            print(f"ℹ️ Dynamic horizontal gap set to {gap_horizontal:.0f}mm.")
            
            leftmost_bbox = placed_qms_bboxes[0]
            rightmost_bbox = placed_qms_bboxes[0]

            for i in range(qms_count - 1):
                if i % 2 == 0: # Place to the left
                    target_x = leftmost_bbox[0] - gap_horizontal - qms_fxtr.width
                    if is_valid_spot(qms_fxtr, target_x, final_start_y):
                        self.place_fixture(qms_fxtr, (target_x, final_start_y, 0), 0, False)
                        new_bbox = (target_x, final_start_y, target_x + qms_fxtr.width, final_start_y + qms_fxtr.height)
                        placed_bboxes.append(new_bbox); leftmost_bbox = new_bbox; qms_placed_count += 1
                        print(f"✅ Placed QMS_desk #{qms_placed_count} to the left.")
                    else: print("⚠️ Spot to the left is blocked.")
                else: # Place to the right
                    target_x = rightmost_bbox[2] + gap_horizontal
                    if is_valid_spot(qms_fxtr, target_x, final_start_y):
                        self.place_fixture(qms_fxtr, (target_x, final_start_y, 0), 0, False)
                        new_bbox = (target_x, final_start_y, target_x + qms_fxtr.width, final_start_y + qms_fxtr.height)
                        placed_bboxes.append(new_bbox); rightmost_bbox = new_bbox; qms_placed_count += 1
                        print(f"✅ Placed QMS_desk #{qms_placed_count} to the right.")
                    else: print("⚠️ Spot to the right is blocked.")

        print(f"-> Finished: Placed {qms_placed_count} of {qms_count} QMS desks.")

    def place_door(self, primary_side):
        """
        Places the door in the middle of the facade with the opening based on the primary_side
        """
        if primary_side == "left":
            door_fx = Fixture.Fixture("Door", self.fixture_dict["Door_Left"]["path"])
        else:
            door_fx = Fixture.Fixture("Door", self.fixture_dict["Door_Right"]["path"])

        facade_center_x = self._get_facade_center_x() - door_fx.width/2
        start_y = self.cvc.min_y - 105/2

        self.place_fixture(door_fx, (facade_center_x, start_y), 0, False)


        # print(door_fx.width)
        # print(door_fx.height)


    def place_qms_at_entrance_center_og(self, placed_bboxes):
        """
        Places QMS desks near the entrance, anchored to the bottom wall,
        but uses a resilient horizontal search to center them within the available space.
        This combines the bottom-wall anchoring of 'at_entrance' with the centering
        logic of 'from_center'.
        """
        from shapely.geometry import box, LineString

        # 1. SETUP
        config = self.fixtures.get("table_fixtures", {})
        qms_count = config.get("QMS_desk", 0)
        if qms_count <= 0:
            return

        print(f"\n--- Attempting to place {qms_count} QMS Desk(s) at Entrance (Horizontally Centered) ---")

        try:
            qms_fxtr = Fixture.Fixture("QMS_desk", self.fixture_dict["QMS_desk"]["path"])
        except Exception as e:
            print(f"🔥 Could not load QMS_desk fixture: {e}")
            return

        # Helper function for validation
        def is_valid_spot(fixture, x, y):
            w, h = fixture.width, fixture.height
            candidate_box = box(x, y, x + w, y + h)
            is_overlapping = any(candidate_box.intersects(box(*bbox)) for bbox in placed_bboxes)
            is_inside = self.floorplan_polygon.contains(candidate_box)
            return is_inside and not is_overlapping

        # 2. CALCULATE VERTICAL POSITION (Y-coordinate)
        # Use the dynamic margin calculation, anchored to the bottom wall.
        bottom_margin = self._calculate_dynamic_qms_margin()
        start_y = self.cvc.min_y + bottom_margin
        print(f"  -> Anchoring to bottom wall. Calculated dynamic start Y-position: {start_y:.0f}")

        # 3. RESILIENT HORIZONTAL SEARCH FOR CENTERING (X-coordinate)
        # Find the available width of the room at the calculated Y-level.
        horizontal_slice = LineString([(self.cvc.min_x - 100, start_y), (self.cvc.max_x + 100, start_y)])
        intersection = self.floorplan_polygon.intersection(horizontal_slice)

        if not isinstance(intersection, LineString) or intersection.is_empty:
            print(f"⚠️ Could not find a valid horizontal space at y={start_y:.0f}. Aborting QMS placement.")
            return

        local_bounds = intersection.bounds
        local_width = local_bounds[2] - local_bounds[0]
        local_start_x = local_bounds[0]

        # Calculate the ideal centered X position for the first desk.
        ideal_x = local_start_x + (local_width - qms_fxtr.width) / 2

        first_desk_placed = False
        final_start_x, final_start_y = 0, 0
        search_offset = 0
        max_search = local_width / 2

        while not first_desk_placed and search_offset < max_search:
            for sign in [1, -1]:
                if sign == -1 and search_offset == 0: continue
                test_x = ideal_x + search_offset * sign
                if is_valid_spot(qms_fxtr, test_x, start_y):
                    final_start_x, final_start_y = test_x, start_y
                    first_desk_placed = True
                    break
            if first_desk_placed: break
            search_offset += 100

        if not first_desk_placed:
            print("⚠️ Could not find a clear spot for the first QMS desk after searching.")
            return

        # 4. EXECUTE PLACEMENT (Center-Out Pattern)
        qms_placed_count = 0
        placed_qms_bboxes = []

        self.place_fixture(qms_fxtr, (final_start_x, final_start_y, 0), 0, False)
        bbox_coords = (final_start_x, final_start_y, final_start_x + qms_fxtr.width, final_start_y + qms_fxtr.height)
        placed_bboxes.append(bbox_coords)
        placed_qms_bboxes.append(bbox_coords)
        qms_placed_count += 1
        print(f"✅ Placed central QMS_desk #{qms_placed_count} at ({final_start_x:.0f}, {final_start_y:.0f}).")

        if qms_count > 1:
            max_gap, min_gap, congestion_threshold = 500, 250, 5
            if qms_count <= 3: gap_horizontal = max_gap
            elif qms_count >= congestion_threshold: gap_horizontal = min_gap
            else: gap_horizontal = max_gap - ((qms_count - 2) / (congestion_threshold - 2) * (max_gap - min_gap))
            
            print(f"ℹ️ Dynamic horizontal gap set to {gap_horizontal:.0f}mm.")
            
            leftmost_bbox = placed_qms_bboxes[0]
            rightmost_bbox = placed_qms_bboxes[0]

            for i in range(qms_count - 1):
                if i % 2 == 0: # Place to the left
                    target_x = leftmost_bbox[0] - gap_horizontal - qms_fxtr.width
                    if is_valid_spot(qms_fxtr, target_x, final_start_y):
                        self.place_fixture(qms_fxtr, (target_x, final_start_y, 0), 0, False)
                        new_bbox = (target_x, final_start_y, target_x + qms_fxtr.width, final_start_y + qms_fxtr.height)
                        placed_bboxes.append(new_bbox); leftmost_bbox = new_bbox; qms_placed_count += 1
                        print(f"✅ Placed QMS_desk #{qms_placed_count} to the left.")
                    else: print("⚠️ Spot to the left is blocked.")
                else: # Place to the right
                    target_x = rightmost_bbox[2] + gap_horizontal
                    if is_valid_spot(qms_fxtr, target_x, final_start_y):
                        self.place_fixture(qms_fxtr, (target_x, final_start_y, 0), 0, False)
                        new_bbox = (target_x, final_start_y, target_x + qms_fxtr.width, final_start_y + qms_fxtr.height)
                        placed_bboxes.append(new_bbox); rightmost_bbox = new_bbox; qms_placed_count += 1
                        print(f"✅ Placed QMS_desk #{qms_placed_count} to the right.")
                    else: print

        print(f"-> Finished: Placed {qms_placed_count} of {qms_count} QMS desks.")


    #------ QMS/GREETR PLACEMENT FUNCTION NEW_SETUP FOR QMS/GREETR HERE ----
    #------ QMS/GREETR PLACEMENT FUNCTION NEW_SETUP FOR QMS/GREETR HERE ----
    #------ QMS/GREETR PLACEMENT FUNCTION FINISHED HERE ----

    #------ corian_table_set PLACEMENT FUNCTION STARTED HERE ----


    def place_corian_table_set_landscape(self, placed_bboxes):
        """
        Main dispatcher for placing Corian Table sets. It checks if the number of
        sets is odd or even and calls the appropriate specialized placement strategy.
        """
        # from Fixture import Fixture
        
        print("\n--- Initializing Corian Table Set Placement ---")

        # 1. SETUP
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

    #------ corian_table_set PLACEMENT FUNCTION FINISHED HERE ----

    #------ standing_tables PLACEMENT FUNCTION STARTED HERE ----


    def place_standing_tables_landscape(self, placed_bboxes):
        """
        Main dispatcher for placing Standing Tables. It intelligently determines the
        anchor point, creates multiple columns as needed, and then calls the
        appropriate odd/even count placement strategy for each column.
        """
        # from Fixture import Fixture
        from ezdxf.bbox import extents
        
        print("\n--- Initializing Standing Table Placement with Multi-Column Logic ---")

        # 1. SETUP
        try:
            config = self.fixtures.get("table_fixtures", {})
            num_tables = config.get("Standing_table", 0)
            if num_tables <= 0:
                print("  -> Placement skipped: No Standing_table specified.")
                return
            standing_fxtr = Fixture.Fixture("Standing_table", self.fixture_dict["Standing_table"]["path"])
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

    # PLACEMENT LOGIC FOR BLUE_ZERO FIXTURES STARTED HERE


    def place_blue_zero_landscape(self, placed_bboxes):
        """
        Places Blue_zero fixtures in landscape mode using a two-phase "snaking"
        pattern. It first exhausts all Discussion Table spots from left to right,
        then places any remaining fixtures next to Euro Centres.
        """
        # from Fixture import Fixture
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
            blue_zero_fxtr = Fixture.Fixture("Blue_zero", self.fixture_dict["Blue_zero"]["path"])
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

    # PLACEMENT LOGIC FOR BLUE_ZERO FIXTURES FINISHED HERE

    # PLACEMENT LOGIC FOR SOFA FIXTURES STARTED HERE

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
        # from Fixture import Fixture
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
                    fxtr = Fixture.Fixture(name, self.fixture_dict[name]["path"])
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

    # PLACEMENT LOGIC FOR SOFA FIXTURES FINISHED HERE

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
