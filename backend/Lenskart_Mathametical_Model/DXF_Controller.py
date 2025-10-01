import subprocess
import sys
import os
import logging
import traceback
from typing import List, Dict, Any, Optional, Tuple
import Fixture
import CV_Controller as cvCon
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
    
    

    # The rest of the DossierParser class (_create_size_prioritized_queue, 
    # orchestrate_wall_and_overflow_placement, etc.) remains unchanged as its
    # internal logic is still valid.
    def _create_size_prioritized_queue(self) -> list:
        """
        Creates a single list of fixture names, heavily prioritizing
        larger sizes to fill the queue first. This list is then passed to the
        placement engine to be placed in a single, continuous pass.
        """
        size_mapping = {
            "jj_fixture_family": ["jj_fixture_large", "jj_fixture_medium"],
            "vc_fixture_family": ["vc_fixture_large", "vc_fixture_medium"],
            "jj_super_hybrid_family": ["jj_super_hybrid_large", "jj_super_hybrid_medium", "jj_super_hybrid_small"],
            "window_family": ["window_3_section", "window_1_section"],
        }
        placement_queue = []

        family_processing_order = ["jj_fixture_family", "jj_super_hybrid_family", "vc_fixture_family", "window_family"]


        # First, build the queue family by family to keep them sequential
        for family_name in family_processing_order:
            total_count = self.family_totals.get(family_name, 0)
            if total_count > 0 and family_name in size_mapping:
                available_sizes = size_mapping[family_name]
                remaining_count = total_count
                num_large = math.ceil(remaining_count * 0.9)
                for _ in range(int(num_large)):
                    if remaining_count > 0:
                        placement_queue.append((available_sizes[0], 1))
                        remaining_count -= 1
                if remaining_count > 0 and len(available_sizes) > 1:
                    for _ in range(int(remaining_count)):
                        placement_queue.append((available_sizes[1], 1))
        print(f"  -> Generated a size-prioritized queue with {len(placement_queue)} fixtures.")
        return placement_queue

    def get_wall_fixture_needs(self) -> Dict[str, int]:
        """
        Returns a dictionary of the total counts needed for each wall fixture family.
        This serves as a "shopping list" for the placement engine.
        """
        print("  -> Generating wall fixture needs dictionary.")
        # self.family_totals is already calculated in the __init__ method
        return self.family_totals.copy()

    def orchestrate_wall_and_overflow_placement(self, total_retail_wall_length: float, floor_area: float, primary_side: str = "left"):
        """
        [UPGRADED] Main orchestration method. Now includes the dynamic ratio calculation
        to determine the optimal number of wall vs. floor fixtures before placement.
        """
        from Fixture import Fixture
        print(f"\n--- 🧠 Orchestrating Wall Fixtures (Primary Side: {primary_side.upper()}) ---")
        
        initial_fixture_list = self._create_size_prioritized_queue()
        if not initial_fixture_list:
            print("  -> SKIPPED: No wall fixtures specified for placement.")
            return

        all_fixture_objects = []
        for name, _ in initial_fixture_list:
            try:
                all_fixture_objects.append(Fixture(name, self.fixture_dict[name]["path"]))
            except (KeyError, ValueError) as e:
                print(f"  -> WARNING: Could not load fixture '{name}' for dimension calculation. It will be skipped. Error: {e}")
                continue
        
        mirror_config = self.fixtures.get("mirror_selection", {})
        selected_mirror_name = next((name for name, selected in mirror_config.items() if selected > 0), "mirror")
        try:
            mirror_fixture = Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
            mirror_height = mirror_fixture.height
        except (KeyError, ValueError):
            mirror_height = 300.0

        print("  -> Running dynamic ratio calculation with REAL fixture dimensions...")
        display_count = len(all_fixture_objects)
        ratio_parts = 4
        initial_floor_count = int(display_count / ratio_parts)
        initial_wall_count = display_count - initial_floor_count
        wall_count = initial_wall_count
        valid = False
        attempts = 0
        MAX_ATTEMPTS = 20

        while not valid and attempts < MAX_ATTEMPTS:
            fixtures_on_wall = all_fixture_objects[:wall_count]
            wall_space_needed = sum(f.height for f in fixtures_on_wall) + (len(fixtures_on_wall) * mirror_height)
            if wall_space_needed <= total_retail_wall_length:
                valid = True
            else:
                wall_count -= 1
            attempts += 1

        final_wall_count = wall_count
        overflow_count = display_count - final_wall_count
        
        if overflow_count > 0:
            overflow_fixtures = initial_fixture_list[final_wall_count:]
            self._calculate_and_add_overflow_euros(overflow_fixtures)
        else:
            print("  -> No overflow fixtures. No extra Euro_centre(s) needed.")
        
        master_fixture_list = initial_fixture_list[:final_wall_count]
        if not master_fixture_list:
            print("  -> No wall fixtures to place after dynamic calculation.")
            return

        total_to_place = len(master_fixture_list)
        primary_count = int(math.ceil(total_to_place / 2.0))
        primary_list = master_fixture_list[:primary_count]
        secondary_list = master_fixture_list[primary_count:]
        primary_queue = collections.deque(primary_list)
        secondary_queue = collections.deque(secondary_list)
        
        if primary_side == "right":
            print(f"  -> PASS 1 (Primary): Placing {len(primary_queue)} fixtures on RIGHT wall(s).")
            self.place_fixtures_on_right_wall_new(primary_queue)
            unplaced_from_primary = list(primary_queue)
            if unplaced_from_primary:
                print(f"  -> {len(unplaced_from_primary)} fixtures unplaced. Moving to secondary (LEFT) queue.")
                secondary_queue.extendleft(reversed(unplaced_from_primary))
            if secondary_queue:
                print(f"  -> PASS 2 (Secondary): Placing {len(secondary_queue)} fixtures on LEFT wall(s).")
                self.place_fixtures_on_left_wall(secondary_queue)
        else:
            print(f"  -> PASS 1 (Primary): Placing {len(primary_queue)} fixtures on LEFT wall(s).")
            unplaced_from_primary = self.place_fixtures_on_left_wall(primary_queue)
            if unplaced_from_primary:
                secondary_queue.extendleft(reversed(unplaced_from_primary))
            if secondary_queue:
                self.place_fixtures_on_right_wall_new(secondary_queue)

    def _calculate_and_add_overflow_euros(self, unplaced_list: List[Tuple[str, int]]):
        """
        Calculates the number of extra Euro Centres needed for overflow.
        """
        overflow_candidates = [name for name, _ in unplaced_list if "vc_fixture" in name]

        if not overflow_candidates:
            print("  -> No overflow candidates of the required type (VC Family) found.")
            return
        extra_euros_needed = math.ceil(len(overflow_candidates) / 1.0)
        if extra_euros_needed > 0:
            self.fixtures["floor_fixtures"]["Euro_centre"] += int(extra_euros_needed)
            print(f"  -> Adding {int(extra_euros_needed)} EXTRA Euro_centre(s) for overflow.")

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

            if proto_value <= 8:
                clinic_counts["Clinic_with_sink"] = 1

            elif proto_value <= 12:
                clinic_counts["Clinic_regular"] = 1
                # clinic_counts["ROC_clinic"] = 1
                clinic_counts["Clinic_with_sink"] = 1

            elif 12 <= proto_value <= 15:
                clinic_counts["Clinic_with_sink"] = 1
                clinic_counts["ROC_clinic"] = 1
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
    

    def _get_accurate_obstacle_bboxes(self, include_all=False):
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
                
                if include_all or fixture_type in ['clinic', 'boh', 'boh_preset'] or best_match_key == "Eye_massage_area":
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

        # return {
        #     "start_point": p1,
        #     "end_point": p2,
        #     "angle_deg": math.degrees(wall_vector.angle),
        #     "length": wall_vector.magnitude,
        #     "vector": wall_vector,
        #     "side": side  # <-- This is the only line that has been added
        # }



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
                if bbox.has_data:
                    minx, miny, minz = bbox.extmin
                    maxx, maxy, maxz = bbox.extmax
                    area = (maxx-minx)*(maxy-miny)
                    if area < (2600*1700)+1000: # max clinic size + buffer
                        back_side_entities.append(entity)
                        print(f"\tadding {block_name_upper}")

        if not back_side_entities:
            print("  -> ⚠️ SKIPPED: No back-side fixtures found to define the separation line.")
            return

        # --- 2. Calculate the combined bounding box and find the bottom edge ---
        combined_bbox = extents(back_side_entities)
        separation_y = combined_bbox.extmin.y - margin
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
    
    def _find_best_combination_for_row_og(self, clinic_names_to_place: list, available_width: float, force_orientation: Optional[str] = None) -> Optional[dict]:
        """
        Universal "Puzzle Solver" for clinic placement in a single row.
        - TUNED: Can now be forced to only consider a specific orientation (e.g., 'V').
        """
        from itertools import product
        from Fixture import Fixture

        V_V_GAP = 800.0
        H_GAP = 50.0     
        
        best_layout = {'score': -1}

        orientations_to_test = ['H', 'V']
        if force_orientation == 'V':
            orientations_to_test = ['V']
        elif force_orientation == 'H':
            orientations_to_test = ['H']

        for n in range(len(clinic_names_to_place), 0, -1):
            try:
                current_fixtures = [Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"]) for name in clinic_names_to_place[:n]]
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

                # --- NEW LOGIC: Calculate total required space including side margins ---
                start_margin = 800.0 if combo[0] == 'V' else 50.0
                end_margin = 800.0 if combo[-1] == 'V' else 50.0
                total_required_space = start_margin + required_width + end_margin
                # --- END OF NEW LOGIC ---

                # --- MODIFIED: Check against total required space ---
                if total_required_space <= available_width:
                    score = (n * 10000) + required_width
                    if score > best_layout['score']:
                        best_layout = {
                            'score': score,
                            'combo': combo,
                            'gaps': gaps,
                            'fixtures_for_row': current_fixtures,
                            'start_margin': start_margin, # --- ADDED: Store the margin
                            'remaining_fixtures_names': clinic_names_to_place[n:]
                        }

            if best_layout['score'] > -1:
                return best_layout

        return None
    

    def _find_best_combination_for_row(self, clinic_names_to_place: list, available_width: float, force_orientation: Optional[str] = None) -> List[dict]:
        """
        # --- MODIFIED: Now returns a LIST of valid layouts, ranked by score. ---
        Universal "Puzzle Solver" for clinic placement in a single row.
        """
        from itertools import product
        from Fixture import Fixture

        V_V_GAP = 800.0
        H_GAP = 50.0

        # --- MODIFIED: Initialize a list to hold all valid layouts ---
        valid_layouts = []

        orientations_to_test = ['H', 'V']
        if force_orientation == 'V':
            orientations_to_test = ['V']
        elif force_orientation == 'H':
            orientations_to_test = ['H']

        for n in range(len(clinic_names_to_place), 0, -1):
            try:
                current_fixtures = [Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"]) for name in clinic_names_to_place[:n]]
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
        # Check 1: Is the entire fixture polygon safely inside the main floorplan?
        # is_inside = self.floorplan_polygon.contains(fixture_polygon)
        is_inside = self.validation_hull_polygon.contains(fixture_polygon)
        # Check 2: Does the fixture's bounding box overlap with any previously placed objects?
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
    
    def _validate_and_place_in_open_space(self, fixture, target_center, angle_deg, placed_bboxes, xscale=1.0, yscale=1.0):
        """
        ### MIRROR LOGIC ADDED ###
        Now accepts xscale and yscale to validate and place mirrored fixtures.
        """
        from shapely.geometry import Polygon
        from ezdxf.math import Matrix44, Vec2, BoundingBox2d
        import math

        # --- Step 1: Calculate the Transformation Matrix ---
        local_center = fixture.bounding_box.center
        transform = Matrix44.chain(
            # 1. Move fixture's center to origin (0,0).
            Matrix44.translate(-local_center.x, -local_center.y, 0),
            # 2. Apply mirroring.
            Matrix44.scale(xscale, yscale, 1.0),
            # 3. Rotate around origin.
            Matrix44.z_rotate(math.radians(angle_deg)),
            # 4. Move to final target position.
            Matrix44.translate(target_center.x, target_center.y, 0)
        )

        # --- Step 2: Calculate the Fixture's Final Position and Shape ---
        world_corners = list(transform.transform_vertices(fixture.bounding_box.rect_vertices()))
        fixture_polygon = Polygon([(p.x, p.y) for p in world_corners])
        aabb = BoundingBox2d(world_corners)

        # --- Step 3: Perform Validation Checks ---
        is_inside = self.floorplan_polygon.contains(fixture_polygon)
        is_overlapping = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

        # --- Step 4: Place the Fixture if Valid ---
        if is_inside and not is_overlapping:
            # Correct the insertion point to account for the offset between the fixture's center and its file's origin (0,0).
            local_center_scaled = Vec2(local_center.x * xscale, local_center.y * yscale)
            rotated_offset = local_center_scaled.rotate(math.radians(angle_deg))
            final_insert_point = target_center - rotated_offset
            
            # Actually draw the fixture in the DXF file.
            self.place_fixture(fixture, (final_insert_point.x, final_insert_point.y, 0), angle_deg, True, xscale=xscale, yscale=yscale)
            
            # Add the new fixture's bounding box to the master list of obstacles.
            new_bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)
            placed_bboxes.append(new_bbox_tuple) 
            
            return new_bbox_tuple # Return the coordinates on success.
            
        return None # Return None on failure.

    def _create_boh_room_from_zone_og(self, boh_zone_poly: Polygon, wall_thickness: float = 50.0, layer_name: str = "BOH_WALL", hatch_color: int = 252):
        """
        Takes a Shapely Polygon and draws it as a proper, hatched wall with a given thickness.
        NOW includes explicit wall outlines.
        """
        if not boh_zone_poly or boh_zone_poly.is_empty:
            return

        # 1. Create the inner boundary by offsetting inwards
        inner_boundary = boh_zone_poly.buffer(-wall_thickness)

        # 2. Create a new hatch object for the wall fill
        hatch = self.msp.add_hatch(color=hatch_color)
        hatch.dxf.layer = layer_name
        
        # 3. Add the outer boundary as the first path for the hatch
        outer_path = hatch.paths.add_edge_path()
        outer_coords = list(boh_zone_poly.exterior.coords)
        for i in range(len(outer_coords) - 1):
            outer_path.add_line(outer_coords[i], outer_coords[i+1])

        # 4. Add the inner boundary as a "hole" in the hatch
        if not inner_boundary.is_empty:
            inner_path = hatch.paths.add_edge_path()
            inner_coords = list(inner_boundary.exterior.coords)
            for i in range(len(inner_coords) - 1):
                inner_path.add_line(inner_coords[i], inner_coords[i+1])

        # 5. Set the visual style of the hatch pattern
        hatch.set_pattern_fill('ANSI32', scale=10)
        hatch.dxf.pattern_angle = 90

        # --- NEW: Add Explicit Wall Outlines ---
        # Draw the outer wall line
        self.msp.add_lwpolyline(
            outer_coords, 
            close=True, 
            dxfattribs={"layer": f"{layer_name}_OUTLINE", "color": 251, "lineweight": 25}
        )
        # Draw the inner wall line
        if not inner_boundary.is_empty:
            self.msp.add_lwpolyline(
                list(inner_boundary.exterior.coords), 
                close=True, 
                dxfattribs={"layer": f"{layer_name}_OUTLINE", "color": 251, "lineweight": 25}
            )
        # --- END OF NEW CODE ---
        
        print(f"  -> ✅ Drew BOH zone as a {wall_thickness}mm thick wall on layer '{layer_name}'.")

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
            inner_boundary = poly.buffer(-wall_thickness)

            # 2. Create a new hatch object for this polygon's wall fill
            hatch = self.msp.add_hatch(color=hatch_color)
            hatch.dxf.layer = layer_name
            
            # 3. Add the outer boundary of THIS polygon
            outer_path = hatch.paths.add_edge_path()
            outer_coords = list(poly.exterior.coords)
            for i in range(len(outer_coords) - 1):
                outer_path.add_line(outer_coords[i], outer_coords[i+1])

            # 4. Add the inner boundary as a "hole" if it exists
            if not inner_boundary.is_empty:
                inner_path = hatch.paths.add_edge_path()
                inner_coords = list(inner_boundary.exterior.coords)
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
            if not inner_boundary.is_empty:
                self.msp.add_lwpolyline(
                    list(inner_boundary.exterior.coords), 
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
      
    
    # In DXF_Controller.py

    def _calculate_opportunistic_boh_zone_og(self, last_clinic_bbox: tuple, placed_bboxes: List[tuple], last_clinic_orientation: str) -> Tuple[Optional[Polygon], float]:
        """
        # --- MODIFIED: Now accepts 'last_clinic_orientation' to add a dynamic gap. ---
        Calculates a potential BOH zone by creating an L-shaped polygon.
        """
        from shapely.geometry import box, Polygon
        
        lc_min_x, lc_min_y, lc_max_x, lc_max_y = last_clinic_bbox
        fp_min_x, fp_min_y, fp_max_x, fp_max_y = self.floorplan_polygon.bounds
        
        # --- NEW: Add a horizontal gap for vertically placed clinics ---
        start_x_for_box = lc_max_x
        if last_clinic_orientation == 'V':
            print("    -> 💡 Applying architectural rule: Adding 800mm horizontal gap for vertical clinic.")
            start_x_for_box += 800.0
        # --- END OF NEW LOGIC ---

        # Use the new starting X-coordinate for the slicing box
        slicing_box = box(start_x_for_box, lc_min_y, fp_max_x + 100, fp_max_y + 100)

        boh_zone_poly = self.floorplan_polygon.intersection(slicing_box)

        if any(boh_zone_poly.intersects(box(*b)) for b in placed_bboxes):
            return None, 0.0

        area_in_sqmm = boh_zone_poly.area
        SQMM_PER_SQFT = 92903.04
        area_in_sqft = area_in_sqmm / SQMM_PER_SQFT
        
        return boh_zone_poly, area_in_sqft


    def create_boh_zone_from_last_clinic_og(self, placed_clinics_on_top_wall: list, placed_bboxes: list):
        """
        [DEFINITIVE BOH STRATEGY V5] Creates the BOH zone.
        - Stops at the first partition that is both to the right AND within the
          same horizontal Y-range as the BOH itself.
        - Applies conditional 800mm gap for odd-numbered vertical clinics.
        """
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

        # ######################################################################
        # ########## NEW, MORE PRECISE PARTITION FILTERING LOGIC START #########
        # ######################################################################

        print("  -> Checking for internal partitions within the BOH's Y-range...")
        boh_max_x = self.cvc.max_x + 1000 
        internal_partitions = self.cvc.get_internal_wall_partitions(20.0, 200.0)
        
        # Define the BOH's vertical "lane" or Y-range.
        boh_min_y = anchor_point_y
        boh_max_y = self.cvc.max_y

        # A partition is relevant only if it's to the right AND its Y-range overlaps with the BOH's Y-range.
        relevant_partitions = [
            p for p in internal_partitions 
            if p[0] > start_x and (boh_min_y < p[3] and p[1] < boh_max_y) # p[1]=min_y, p[3]=max_y
        ]
        
        if relevant_partitions:
            first_partition = min(relevant_partitions, key=lambda p: p[0])
            boh_max_x = first_partition[0]
            print(f"    -> ✅ Found partition in path at x={boh_max_x:.0f}. BOH zone will stop here.")
        else:
            print("    -> No blocking partitions found in path. BOH will extend to the room's natural edge.")

        # ####################################################################
        # ########### NEW, MORE PRECISE PARTITION FILTERING LOGIC END ##########
        # ####################################################################

        # 4. Create and draw the BOH zone (Unchanged)
        boh_box = box(start_x, anchor_point_y, boh_max_x, self.cvc.max_y + 1000)
        final_boh_poly = self.floorplan_polygon.intersection(boh_box)

        if final_boh_poly.is_empty:
            print("  -> ⚠️ FAILED: The calculated BOH zone resulted in an empty area.")
            return
            
        self._create_boh_room_from_zone(final_boh_poly, layer_name="BOH_WALL_VALID")
        placed_bboxes.append(final_boh_poly.bounds)

    

    def create_boh_zone_from_last_clinic( self, placed_clinics_on_top_wall: list, placed_bboxes: list, big_partition_threshold_mm: float = 800.0):
        """
        [DEFINITIVE BOH STRATEGY V5] Creates the BOH zone.
        - Stops at the first partition that is both to the right AND within the
          same horizontal Y-range as the BOH itself.
        - Applies conditional 800mm gap for odd-numbered vertical clinics.
        """
        # --- ADD THIS BLOCK AT THE TOP ---
        debug_layer_name = "DEBUG_STOPPER_PARTITIONS"
        if debug_layer_name not in self.doc.layers:
            self.doc.layers.add(name=debug_layer_name, color=1) # Color 1 is Red
        # --- END OF NEW BLOCK ---
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

    
        # ######################################################################

        print("  -> Checking for internal partitions within the BOH's Y-range...")
        boh_max_x = self.cvc.max_x + 1000 
        # stopper_partitions = self.cvc.get_internal_wall_partitions(max_length=big_partition_threshold_mm, thickness=0)
        # In create_boh_zone_from_last_clinic() around line 2030
        # --- THIS IS THE NEW, CORRECTED CALL ---
        # stopper_partitions = self.cvc.get_internal_wall_partitions_boh(min_length_mm=big_partition_threshold_mm, thickness=0)
        stopper_partitions = self.cvc.get_internal_wall_partitions_boh(
            min_length_mm=big_partition_threshold_mm, 
            thickness=0,
            msp_debug=None #self.msp 
        )
        # ####################################################################
       


        print("  -> Filtering for partitions that are connected AND vertical...")
        proximity_threshold = 50.0
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
        # ####################################################################
        # ########################## END OF NEW BLOCK ##########################
        # ####################################################################


        # internal_partitions = self.cvc.get_internal_wall_partitions(20.0, 200.0)
        
        # Define the BOH's vertical "lane" or Y-range.
        boh_min_y = anchor_point_y
        boh_max_y = self.cvc.max_y

        # A partition is relevant only if it's to the right AND its Y-range overlaps with the BOH's Y-range.
        # relevant_partitions = [
        #     p for p in stopper_partitions 
        #     if p[0] > start_x and (boh_min_y < p[3] and p[1] < boh_max_y) # p[1]=min_y, p[3]=max_y
        # ]
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

        # ####################################################################
        # ########### NEW, MORE PRECISE PARTITION FILTERING LOGIC END ##########
        # ####################################################################

        # 4. Create and draw the BOH zone (Unchanged)
        boh_box = box(start_x, anchor_point_y, boh_max_x, self.cvc.max_y + 1000)
        # final_boh_poly = self.floorplan_polygon.intersection(boh_box)
        # final_boh_poly = self.floorplan_polygon.convex_hull.intersection(boh_box)
        # AFTER (Correct):
        final_boh_poly = self.floorplan_polygon.intersection(boh_box)

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
    

    def place_clinics_with_best_fit_and_fallback_og(self, placed_bboxes: List[tuple]):
        """
        Master function for clinic placement using the final, fully-featured
        "Opportunistic BOH Reservation" strategy with a custom, corner-filling zone.
        - FINAL VERSION: Now draws a visual boundary for the BOH zone in all cases.
        """
        from Fixture import Fixture
        from shapely.geometry import Polygon
        print("\n--- 🧠 Executing Final Clinic & BOH Placement Strategy ---")

        # --- Setup: Load a list of all clinic NAMES ---
        clinic_config = self.fixtures.get("clinic_fixtures", {})
        clinic_names_queue = collections.deque([name for name, count in clinic_config.items() if count > 0 for _ in range(count)])
        
        if not clinic_names_queue:
            print("  -> SKIPPED: No clinics to place.")
            return

        # --- Plan A: The Row-by-Row Placement Engine ---
        print("\n  -> Plan A: Initiating Row-by-Row Placement Engine...")
        placed_count_plan_a = 0
        is_first_row = True
        y_cursor = 0
        last_row_details = {}
        
        while clinic_names_queue:
            available_width, anchor_details = 0, {}
            force_orientation_for_row = None

            if is_first_row:
                ordered_corners = self._get_reordered_corners_top_left()
                perimeter_path = []
                if ordered_corners:
                    for i in range(len(ordered_corners)):
                        p1, p2 = Vec2(ordered_corners[i]), Vec2(ordered_corners[(i + 1) % len(ordered_corners)])
                        if p1.distance(p2) > 100: perimeter_path.append((p1, p2))
                if not perimeter_path: break
                
                p1_top, p2_top = perimeter_path[0]
                available_width = p1_top.distance(p2_top)
                anchor_details = { "type": "wall", "segment": (p1_top, p2_top) }
            else:
                # Logic for subsequent rows (unchanged and correct)
                intersection = self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, y_cursor), (self.cvc.max_x + 100, y_cursor)]))
                if not isinstance(intersection, LineString) or intersection.is_empty:
                    print("      -> ⚠️ No more vertical space available."); break
                local_bounds = intersection.bounds
                available_width = local_bounds[2] - local_bounds[0]
                anchor_details = { "type": "open_space", "bounds": local_bounds }
                if last_row_details.get("orientation") == 'H':
                    force_orientation_for_row = 'V'
                    print("    -> Last row was horizontal, forcing this row to be vertical.")

            best_layout = self._find_best_combination_for_row(list(clinic_names_queue), available_width, force_orientation=force_orientation_for_row)
            # =========================================================================
            # =========== NEW LOGIC TO REMOVE GAP BEFORE LAST VERTICAL CLINIC ===========
            # =========================================================================
            if best_layout:
                combo = best_layout['combo']
                gaps = best_layout['gaps']
                
                # This is the new rule: If the last two clinics in the planned row are
                # both vertical, remove the gap between them to create a solid block.
                if len(combo) > 1 and combo[-1] == 'V' and combo[-2] == 'V':
                    print("    -> 💡 Applying special rule: Removing gap between the last two vertical clinics.")
                    # The gap list has one less item than the combo list. The gap between
                    # the second-to-last and last fixture is the second-to-last item in the gaps list.
                    gaps[-2] = 800.0 # Set the gap to 0
                    best_layout['gaps'] = gaps # IMPORTANT: Update the dictionary with the new gaps
            # =========================================================================
            # ======================== END OF NEW LOGIC ===============================
            # =========================================================================
            if not best_layout:
                if is_first_row: placed_count_plan_a = 0
                break

            print(f"    -> Best layout for this row: {best_layout['combo']}")
            
            if is_first_row:
                row_fixtures = best_layout['fixtures_for_row']
                row_combo = best_layout['combo']
                row_gaps = best_layout['gaps']
                
                start_margin = best_layout.get('start_margin', 50.0) # Default to 50 if not found
                placement_details, current_x = [], anchor_details["segment"][0].x + start_margin

                vertical_clinic_count = 0
                for i in range(len(row_fixtures)):
                    fxtr, orient = row_fixtures[i], row_combo[i]
                    w = fxtr.width if orient == 'H' else fxtr.height
                    xscale, yscale = (-1.0 if orient == 'H' else 1.0), 1.0
                    if orient == 'V':
                        vertical_clinic_count += 1
                        if vertical_clinic_count % 2 == 0: yscale = -1.0
                    
                    p1, p2 = anchor_details["segment"]
                    wall_vector, wall_angle_deg = (p2 - p1).normalize(), math.degrees((p2 - p1).angle)
                    inward_normal = wall_vector.orthogonal().normalize()
                    if not self.floorplan_polygon.contains(Point(p1 + inward_normal)): inward_normal *= -1
                    
                    center_on_wall = p1 + wall_vector * (current_x - p1.x + w / 2)
                    target_center = center_on_wall + inward_normal * (50.0 + (fxtr.height if orient == 'H' else fxtr.width) / 2)
                    rotation = wall_angle_deg if orient == 'H' else wall_angle_deg + 90

                    placement_details.append({'fxtr': fxtr, 'center': target_center, 'rot': rotation, 'xscale': xscale, 'yscale': yscale})
                    current_x += w + row_gaps[i]
                # --- B: Place all clinics EXCEPT the last one unconditionally ---
                placed_bboxes_in_this_row = []
                for details in placement_details[:-1]:
                    new_bbox = self._validate_and_place_on_wall(details['fxtr'], details['center'], details['rot'], placed_bboxes, xscale=details['xscale'], yscale=details['yscale'])
                    if new_bbox:
                        placed_bboxes_in_this_row.append(new_bbox)
                        placed_count_plan_a += 1
                        clinic_names_queue.popleft()
                
                # --- C: Perform the "what-if" check for the LAST clinic ---
                if placement_details:
                    last_clinic_details = placement_details[-1]
                    hypothetical_bbox = self._validate_and_place_on_wall(
                        last_clinic_details['fxtr'], last_clinic_details['center'], last_clinic_details['rot'], 
                        placed_bboxes, xscale=last_clinic_details['xscale'], yscale=last_clinic_details['yscale'], 
                        place_actually=False
                    )
                    
                    if hypothetical_bbox:
                        boh_zone_poly, boh_area_sqft = self._calculate_opportunistic_boh_zone(hypothetical_bbox, placed_bboxes)
                        print(f"    -> What-If Check: Placing last clinic leaves a {boh_area_sqft:.2f} sq. ft. zone for BOH.")

                        if boh_area_sqft >= 40.0:
                            print("    -> ✅ Success: Committing clinic and creating BOH zone.")
                            final_bbox = self._validate_and_place_on_wall(
                                last_clinic_details['fxtr'], last_clinic_details['center'], last_clinic_details['rot'], 
                                placed_bboxes, xscale=last_clinic_details['xscale'], yscale=last_clinic_details['yscale'],
                                place_actually=True
                            )
                            if final_bbox:
                                placed_bboxes_in_this_row.append(final_bbox)
                                placed_count_plan_a += 1
                                clinic_names_queue.popleft()
                                # --- REPLACED CODE STARTS HERE ---
                                # Draw the valid BOH zone as a proper wall
                                if boh_zone_poly and not boh_zone_poly.is_empty:
                                    self._create_boh_room_from_zone(boh_zone_poly, wall_thickness=50.0, layer_name="BOH_WALL_VALID", hatch_color=150) # Blue-ish hatch
                                    placed_bboxes.append(boh_zone_poly.bounds)
                                # --- REPLACED CODE ENDS HERE ---
                        else:
                            print("    -> ⚠️ BOH space would be too small. Deferring last clinic to the next row.")
                            last_placed_bbox = placed_bboxes_in_this_row[-1] if placed_bboxes_in_this_row else None
                            if last_placed_bbox:
                                undersized_boh_poly, undersized_area_sqft = self._calculate_opportunistic_boh_zone(last_placed_bbox, [])
                                print(f"    -> The undersized BOH area is {undersized_area_sqft:.2f} sq. ft.")
                                # --- REPLACED CODE STARTS HERE ---
                                if undersized_boh_poly and not undersized_boh_poly.is_empty:
                                    # Draw the undersized BOH zone as a different colored wall
                                    # self._create_boh_room_from_zone(undersized_boh_poly, wall_thickness=50.0, layer_name="BOH_WALL_OVERSIZED", hatch_color=252) # Gray hatch
                                    self._create_boh_room_from_zone(undersized_boh_poly, wall_thickness=50.0, layer_name="BOH_WALL_VALID", hatch_color=252) # Gray hatch
                                # --- REPLACED CODE ENDS HERE ---
                    else:
                        print("    -> ⚠️ Last clinic in row is blocked. Deferring to next row.")
            
            # --- Standard placement for subsequent rows (2nd, 3rd, etc.) ---
            else:
                row_fixtures = best_layout['fixtures_for_row']
                total_row_width = sum((f.width if o == 'H' else f.height) for f, o in zip(row_fixtures, best_layout['combo'])) + sum(best_layout['gaps'])
                LEFT_NUDGE = 0.0
                row_start_x = last_row_details.get("bbox", [anchor_details["bounds"][0]])[0] + LEFT_NUDGE
                placed_bboxes_in_this_row = []
                vertical_clinic_count_in_row = 0
                for i, (orient, fxtr) in enumerate(zip(best_layout['combo'], row_fixtures)):
                    w, h, gap = (fxtr.width if orient == 'H' else fxtr.height), (fxtr.height if orient == 'H' else fxtr.width), best_layout['gaps'][i]
                    xscale, yscale = (-1.0 if orient == 'H' else 1.0), 1.0
                    if orient == 'V':
                        vertical_clinic_count_in_row += 1
                        if vertical_clinic_count_in_row % 2 == 0: yscale = -1.0
                    
                    target_y = y_cursor - h
                    target_center = Vec2(row_start_x + w/2, target_y + h/2)
                    rotation = 0 if orient == 'H' else 90
                    new_bbox = self._validate_and_place_in_open_space(fxtr, target_center, rotation, placed_bboxes, xscale=xscale, yscale=yscale)
                    if new_bbox:
                        placed_bboxes_in_this_row.append(new_bbox)
                        placed_count_plan_a += 1
                        clinic_names_queue.popleft()
                        row_start_x += w + gap
                    else:
                        print(f"      -> ⚠️ Could not place '{fxtr.name}'. Halting row placement.")
                        clinic_names_queue.clear(); break
            
            # --- Update state for the next row ---
            if placed_bboxes_in_this_row:
                min_x = min(b[0] for b in placed_bboxes_in_this_row); min_y = min(b[1] for b in placed_bboxes_in_this_row)
                max_x = max(b[2] for b in placed_bboxes_in_this_row); max_y = max(b[3] for b in placed_bboxes_in_this_row)
                combined_row_bbox = (min_x, min_y, max_x, max_y)
                h_count = best_layout['combo'].count('H'); v_count = best_layout['combo'].count('V')
                dominant_orientation = 'H' if h_count >= v_count else 'V'
                last_row_details = {"bbox": combined_row_bbox, "orientation": dominant_orientation}
                VERTICAL_ROW_GAP = 10.0
                y_cursor = combined_row_bbox[1] - VERTICAL_ROW_GAP
                if is_first_row: is_first_row = False
            else: 
                # If nothing was placed in the row, we must advance the state to avoid an infinite loop
                if is_first_row: is_first_row = False
                y_cursor -= 500 # Nudge y_cursor down to try a new area
        
        # --- Plan B Fallback ---
        if placed_count_plan_a == 0 and [name for name, count in clinic_config.items() if count > 0]:
             print("\n  -> Plan A failed to place any clinics. Activating Fallback...")
             clinics_to_place_obj = [Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"]) for name, count in clinic_config.items() if count > 0 for _ in range(count)]
             remaining = self.place_clinics_by_perimeter_walk(clinics_to_place_obj, placed_bboxes)
             if remaining: print(f"    -> ⚠️ Fallback finished with {len(remaining)} unplaced clinics.")
        else:
             print(f"\n✅ Plan A Succeeded. Placed {placed_count_plan_a} clinics.")



    def _find_and_place_row_in_zone_og(self, zone, layouts_ranked: list, clinics_queue, placed_bboxes, placed_clinics_on_top_wall,start_vertical_count: int = 0):
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
        inward_normal = wall_vector.orthogonal().normalize()
        if not self.floorplan_polygon.contains(Point(p1 + inward_normal)): inward_normal *= -1

        # --- 1. Find the best possible placement WITHOUT drawing anything yet ---
        
        # This variable will store our final choice after searching the whole zone.
        best_placement_details = None
        final_vertical_count_state = start_vertical_count

        # Loop through every possible start position in the zone.
        search_cursor = 50.0
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
                    center_on_wall = p1 + wall_vector * (validation_cursor + w / 2)
                    target_center = center_on_wall + inward_normal * (50.0 + (fxtr.height if orient == 'H' else fxtr.width) / 2)
                    snapped_angle_deg = round(wall_angle_deg / 90.0) * 90.0
                    # rotation = wall_angle_deg + 90 if orient == 'V' else wall_angle_deg
                    rotation = snapped_angle_deg if orient == 'H' else snapped_angle_deg + 90
                    # xscale, yscale = (-1.0 if orient == 'H' else 1.0), 1.0
                    # if orient == 'V':
                    #     vertical_clinic_count += 1
                    #     if vertical_clinic_count % 2 == 0: yscale = -1.0
                    # --- CORRECTED MIRRORING LOGIC ---
                    if orient == 'H':
                        # Horizontal clinics are mirrored horizontally
                        xscale, yscale = -1.0, 1.0
                    else:  # This handles the case where orient == 'V'
                        # Vertical clinics are mirrored horizontally by default
                        xscale, yscale = -1.0, 1.0
                        
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
            search_cursor += 100

        # --- 2. If a best placement was found, COMMIT it now ---
        if best_placement_details:
            print(f"    -> ✅ Best spot found. Committing {len(best_placement_details)} clinics to the wall.")
            for details in best_placement_details:
                if details['orient'] == 'V':
                    final_vertical_count_state += 1
                self._validate_and_place_on_wall(details['fxtr'], details['center'], details['rot'], placed_bboxes, xscale=details['xscale'], yscale=details['yscale'], place_actually=True)
                placed_clinics_on_top_wall.append(details)
                clinics_queue.popleft()
            return len(best_placement_details), final_vertical_count_state

        # If the loops finish and no placement was found
        return 0, start_vertical_count
    

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
                    center_on_wall = p1 + wall_vector * (validation_cursor + w / 2)
                    target_center = center_on_wall + inward_normal * (50.0 + (fxtr.height if orient == 'H' else fxtr.width) / 2)
                    snapped_angle_deg = round(wall_angle_deg / 90.0) * 90.0
                    rotation = wall_angle_deg + 90 if orient == 'V' else wall_angle_deg
                    # rotation = snapped_angle_deg if orient == 'H' else snapped_angle_deg + 90
                    # xscale, yscale = (-1.0 if orient == 'H' else 1.0), 1.0
                    # if orient == 'V':
                    #     vertical_clinic_count += 1
                    #     if vertical_clinic_count % 2 == 0: yscale = -1.0
                    # --- CORRECTED MIRRORING LOGIC ---
                    if orient == 'H':
                        # Horizontal clinics are mirrored horizontally
                        xscale, yscale = -1.0, 1.0
                    else:  # This handles the case where orient == 'V'
                        # Vertical clinics are mirrored horizontally by default
                        xscale, yscale = -1.0, 1.0
                        
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

        # --- 2. If a best placement was found, COMMIT it now ---
        if best_placement_details:
            print(f"    -> ✅ Best spot found. Committing {len(best_placement_details)} clinics to the wall.")
            for details in best_placement_details:
                if details['orient'] == 'V':
                    final_vertical_count_state += 1
                # self._validate_and_place_on_wall(details['fxtr'], details['center'], details['rot'], placed_bboxes, xscale=details['xscale'], yscale=details['yscale'], place_actually=True)
                # placed_clinics_on_top_wall.append(details)
                # # clinics_queue.popleft()

                # Inside _find_and_place_row_in_zone, in the final "commit" loop
                # --- MODIFICATION START ---
                # The validation function now returns the bounding box
                new_bbox_tuple = self._validate_and_place_on_wall(details['fxtr'], details['center'], details['rot'], placed_bboxes, xscale=details['xscale'], yscale=details['yscale'], place_actually=True)
                
                if new_bbox_tuple:
                    # Capture the block_ref of the last created entity
                    block_ref = self.msp[-1] 
                    details['bbox'] = new_bbox_tuple # Update details with the accurate bbox
                    details['block_ref'] = block_ref # *** ADD THIS LINE to store the direct object reference
                    
                    placed_clinics_on_top_wall.append(details)
                    clinics_queue.popleft()
                # --- MODIFICATION END ---
            return len(best_placement_details), final_vertical_count_state
            

        # If the loops finish and no placement was found
        return 0, start_vertical_count
    
   
    
 
    ##--new-test--with---greedy method-- strategy -----space for boh
    ##--new-test--with---greedy method-- strategy -----space for boh----in top row itself
    ##--new-test--with---greedy method-- strategy -----space for boh----in top row itself

    def place_clinics_master_strategy(self, placed_bboxes: List[tuple]):
        """
        [MODIFIED with "Place-Then-Verify" logic]
        Places all top-wall clinics first, then verifies if a valid BOH can be
        created. If not, it "undoes" the last clinic placement.
        [MASTER STRATEGY] Merges "Smart Walk" with a "Resilient Sliding Search"
        and "Opportunistic BOH" placement logic for the most robust placement.
        """
        self.clinic_placement_method = 'Unknown'
        from Fixture import Fixture
        from shapely.geometry import Polygon, LineString, Point
        from ezdxf.math import Vec2
        from ezdxf.bbox import extents
        import collections
        import math

        # Create a temporary obstacle list for clinics (Unchanged)
        obstacles_for_clinics = list(placed_bboxes)
        internal_wall_obstacles = self.cvc.get_internal_wall_partitions(2000, 20)
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
            Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"])
            for name, count in clinic_config.items() if count > 0 for _ in range(count)
        ])
        if not clinics_queue:
            print("  -> SKIPPED: No clinics to place.")
            return

        # =========================================================================
        # =========== PHASE 1: UNCONDITIONAL TOP-WALL PLACEMENT ===================
        # =========================================================================
        print("\n  -> Phase 1: Placing all possible clinics on the top wall...")
        top_wall_zones = self._analyze_top_wall_with_bulge_detection_new()
        
        placed_clinics_on_top_wall = []
        is_first_zone_processed = False
        first_row_orientation = 'H'
        total_vertical_clinics_placed_on_top = 0

        for zone in top_wall_zones:
            if not clinics_queue: break
            
            available_width = zone['length']
            print(f"\n  -> Analyzing placement zone of width {available_width:.0f}mm...")

            clinic_names_for_solver = [fxtr.name for fxtr in clinics_queue]
            best_layouts_ranked = self._find_best_combination_for_row(clinic_names_for_solver, available_width)

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
            
            # Perform the "what-if" check for the BOH area
            boh_zone_poly, boh_area_sqft = self._calculate_opportunistic_boh_zone(
                final_anchor_clinic_details['bbox'],
                [], # Pass empty obstacles as we only care about potential area
                final_anchor_clinic_details['orient']
            )
            print(f"    -> Final check: Potential BOH area is {boh_area_sqft:.2f} sq. ft.")

            # Define your mandatory minimum area
            MINIMUM_BOH_AREA = 30.0
            
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

    
            y_cursor = self.cvc.max_y
            
            if placed_clinics_on_top_wall:
                y_cursor = min(d['bbox'][1] for d in placed_clinics_on_top_wall)
                print(f"  -> First row placed. Starting next search below y={y_cursor:.0f}")
            
            is_second_row = True
            last_placed_row_orientation = first_row_orientation
            
            while clinics_queue and y_cursor > self.cvc.min_y:
                # --- NEW LOGIC BLOCK (REVISED) ---
                
                # 1. First, determine if we should FORCE a vertical orientation for this row.
                force_orientation = 'V' if is_second_row and first_row_orientation == 'H' else None


                if force_orientation == 'V' or (is_second_row and first_row_orientation == 'V'):
                    VERTICAL_ROW_GAP = 50.0
                    print(f"  -> Intending to place a VERTICAL row. Using a tight {VERTICAL_ROW_GAP}mm gap.")
                else:
                    VERTICAL_ROW_GAP = 800.0
                    print(f"  -> Intending to place a HORIZONTAL/MIXED row. Using a wide {VERTICAL_ROW_GAP}mm gap.")
                # --- END OF CORRECTION ---

                # 3. Apply the gap.
                y_cursor -= VERTICAL_ROW_GAP

                # 4. Find the available space at the new y_cursor.
                intersection = self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, y_cursor), (self.cvc.max_x + 100, y_cursor)]))
                if not isinstance(intersection, LineString) or intersection.is_empty:
                    y_cursor -= 500; continue
                
                local_bounds, row_width = intersection.bounds, intersection.length
                # --- END OF NEW LOGIC BLOCK ---
                is_second_row = False
                
                best_layouts_ranked = self._find_best_combination_for_row([f.name for f in clinics_queue], row_width, force_orientation=force_orientation)
                
                if best_layouts_ranked:
                    best_layout_used = best_layouts_ranked[0]
                    print(f"    -> Found valid spot for a new row at y={y_cursor:.0f}. Placing {len(best_layout_used['combo'])} clinics.")
                    row_fixtures = best_layout_used['fixtures_for_row']
                    
                    margin_from_left_wall = 50.0
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
                        
                        if self._validate_and_place_in_open_space(fxtr, target_center, rotation, placed_bboxes, xscale=xscale, yscale=yscale):
                            clinics_queue.popleft()
                            row_start_x += w + best_layout_used['gaps'][i]
                        else:
                            clinics_queue.clear(); break
                        
                    # --- ADD THIS NEW CODE BLOCK AT THE END OF THE 'if best_layouts_ranked:' BLOCK ---
                    # Determine the dominant orientation of the row we just placed
                    h_count = best_layout_used['combo'].count('H')
                    v_count = len(best_layout_used['fixtures_for_row']) - h_count
                    last_placed_row_orientation = 'H' if h_count >= v_count else 'V'
                    
                    # Update y_cursor to the bottom of the row just placed for the next iteration
                    if max_row_height > 0: y_cursor -= max_row_height
                    # --- END OF NEW CODE ---                  
                    # if max_row_height > 0: y_cursor -= (max_row_height + 1500)
                    else: y_cursor -= 500
                else:
                    y_cursor -= 500
        
        if clinics_queue:
            print(f"\n  -> {len(clinics_queue)} clinics still remain. Starting Final Fallback (Perimeter Walk)...")
            self.place_clinics_by_perimeter_walk(list(clinics_queue), obstacles_for_clinics)

        print("\n✅ Master clinic placement process complete.")



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


    def place_clinics_with_best_fit_and_fallback(self, placed_bboxes: List[tuple]):
        """
        Master function for clinic placement using the final, fully-featured
        "Opportunistic BOH Reservation" strategy with a custom, corner-filling zone.
        - FINAL VERSION: Now draws a visual boundary for the BOH zone in all cases.
        """
        from Fixture import Fixture
        from shapely.geometry import Polygon
        print("\n--- 🧠 Executing Final Clinic & BOH Placement Strategy ---")

        # --- Setup: Load a list of all clinic NAMES ---
        clinic_config = self.fixtures.get("clinic_fixtures", {})
        clinic_names_queue = collections.deque([name for name, count in clinic_config.items() if count > 0 for _ in range(count)])
        
        if not clinic_names_queue:
            print("  -> SKIPPED: No clinics to place.")
            return

        # --- Plan A: The Row-by-Row Placement Engine ---
        print("\n  -> Plan A: Initiating Row-by-Row Placement Engine...")
        placed_count_plan_a = 0
        is_first_row = True
        y_cursor = 0
        last_row_details = {}
        
        while clinic_names_queue:
            available_width, anchor_details = 0, {}
            force_orientation_for_row = None

            if is_first_row:
                ordered_corners = self._get_reordered_corners_top_left()
                perimeter_path = []
                if ordered_corners:
                    for i in range(len(ordered_corners)):
                        p1, p2 = Vec2(ordered_corners[i]), Vec2(ordered_corners[(i + 1) % len(ordered_corners)])
                        if p1.distance(p2) > 100: perimeter_path.append((p1, p2))
                if not perimeter_path: break
                
                p1_top, p2_top = perimeter_path[0]
                available_width = p1_top.distance(p2_top)
                anchor_details = { "type": "wall", "segment": (p1_top, p2_top) }
            else:
                # Logic for subsequent rows (unchanged and correct)
                intersection = self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, y_cursor), (self.cvc.max_x + 100, y_cursor)]))
                if not isinstance(intersection, LineString) or intersection.is_empty:
                    print("      -> ⚠️ No more vertical space available."); break
                local_bounds = intersection.bounds
                available_width = local_bounds[2] - local_bounds[0]
                anchor_details = { "type": "open_space", "bounds": local_bounds }
                if last_row_details.get("orientation") == 'H':
                    force_orientation_for_row = 'V'
                    print("    -> Last row was horizontal, forcing this row to be vertical.")

            best_layout = self._find_best_combination_for_row(list(clinic_names_queue), available_width, force_orientation=force_orientation_for_row)
            # =========================================================================
            # =========== NEW LOGIC TO REMOVE GAP BEFORE LAST VERTICAL CLINIC ===========
            # =========================================================================
            if best_layout:
                combo = best_layout['combo']
                gaps = best_layout['gaps']
                
                # This is the new rule: If the last two clinics in the planned row are
                # both vertical, remove the gap between them to create a solid block.
                if len(combo) > 1 and combo[-1] == 'V' and combo[-2] == 'V':
                    print("    -> 💡 Applying special rule: Removing gap between the last two vertical clinics.")
                    # The gap list has one less item than the combo list. The gap between
                    # the second-to-last and last fixture is the second-to-last item in the gaps list.
                    gaps[-2] = 0.0 # Set the gap to 0
                    best_layout['gaps'] = gaps # IMPORTANT: Update the dictionary with the new gaps
            # =========================================================================
            # ======================== END OF NEW LOGIC ===============================
            # =========================================================================
            if not best_layout:
                if is_first_row: placed_count_plan_a = 0
                break

            print(f"    -> Best layout for this row: {best_layout['combo']}")
            
            if is_first_row:
                row_fixtures = best_layout['fixtures_for_row']
                row_combo = best_layout['combo']
                row_gaps = best_layout['gaps']
                
                start_margin = best_layout.get('start_margin', 50.0) # Default to 50 if not found
                placement_details, current_x = [], anchor_details["segment"][0].x + start_margin

                vertical_clinic_count = 0
                for i in range(len(row_fixtures)):
                    fxtr, orient = row_fixtures[i], row_combo[i]
                    w = fxtr.width if orient == 'H' else fxtr.height
                    xscale, yscale = (-1.0 if orient == 'H' else 1.0), 1.0
                    if orient == 'V':
                        vertical_clinic_count += 1
                        if vertical_clinic_count % 2 == 0: yscale = -1.0
                    
                    p1, p2 = anchor_details["segment"]
                    wall_vector, wall_angle_deg = (p2 - p1).normalize(), math.degrees((p2 - p1).angle)
                    inward_normal = wall_vector.orthogonal().normalize()
                    if not self.floorplan_polygon.contains(Point(p1 + inward_normal)): inward_normal *= -1
                    
                    center_on_wall = p1 + wall_vector * (current_x - p1.x + w / 2)
                    target_center = center_on_wall + inward_normal * (50.0 + (fxtr.height if orient == 'H' else fxtr.width) / 2)
                    rotation = wall_angle_deg if orient == 'H' else wall_angle_deg + 90

                    placement_details.append({'fxtr': fxtr, 'center': target_center, 'rot': rotation, 'xscale': xscale, 'yscale': yscale})
                    current_x += w + row_gaps[i]
                # --- B: Place all clinics EXCEPT the last one unconditionally ---
                placed_bboxes_in_this_row = []
                for details in placement_details[:-1]:
                    new_bbox = self._validate_and_place_on_wall(details['fxtr'], details['center'], details['rot'], placed_bboxes, xscale=details['xscale'], yscale=details['yscale'])
                    if new_bbox:
                        placed_bboxes_in_this_row.append(new_bbox)
                        placed_count_plan_a += 1
                        clinic_names_queue.popleft()
                
                # --- C: Perform the "what-if" check for the LAST clinic ---
                if placement_details:
                    last_clinic_details = placement_details[-1]
                    hypothetical_bbox = self._validate_and_place_on_wall(
                        last_clinic_details['fxtr'], last_clinic_details['center'], last_clinic_details['rot'], 
                        placed_bboxes, xscale=last_clinic_details['xscale'], yscale=last_clinic_details['yscale'], 
                        place_actually=False
                    )
                    
                    if hypothetical_bbox:
                        boh_zone_poly, boh_area_sqft = self._calculate_opportunistic_boh_zone(hypothetical_bbox, placed_bboxes)
                        print(f"    -> What-If Check: Placing last clinic leaves a {boh_area_sqft:.2f} sq. ft. zone for BOH.")

                        if boh_area_sqft >= 40.0:
                            print("    -> ✅ Success: Committing clinic and creating BOH zone.")
                            final_bbox = self._validate_and_place_on_wall(
                                last_clinic_details['fxtr'], last_clinic_details['center'], last_clinic_details['rot'], 
                                placed_bboxes, xscale=last_clinic_details['xscale'], yscale=last_clinic_details['yscale'],
                                place_actually=True
                            )
                            if final_bbox:
                                placed_bboxes_in_this_row.append(final_bbox)
                                placed_count_plan_a += 1
                                clinic_names_queue.popleft()
                                # --- REPLACED CODE STARTS HERE ---
                                # Draw the valid BOH zone as a proper wall
                                if boh_zone_poly and not boh_zone_poly.is_empty:
                                    self._create_boh_room_from_zone(boh_zone_poly, wall_thickness=50.0, layer_name="BOH_WALL_VALID", hatch_color=150) # Blue-ish hatch
                                    placed_bboxes.append(boh_zone_poly.bounds)
                                # --- REPLACED CODE ENDS HERE ---
                        else:
                            print("    -> ⚠️ BOH space would be too small. Deferring last clinic to the next row.")
                            last_placed_bbox = placed_bboxes_in_this_row[-1] if placed_bboxes_in_this_row else None
                            if last_placed_bbox:
                                undersized_boh_poly, undersized_area_sqft = self._calculate_opportunistic_boh_zone(last_placed_bbox, [])
                                print(f"    -> The undersized BOH area is {undersized_area_sqft:.2f} sq. ft.")
                                # --- REPLACED CODE STARTS HERE ---
                                if undersized_boh_poly and not undersized_boh_poly.is_empty:
                                    # Draw the undersized BOH zone as a different colored wall
                                    # self._create_boh_room_from_zone(undersized_boh_poly, wall_thickness=50.0, layer_name="BOH_WALL_OVERSIZED", hatch_color=252) # Gray hatch
                                    self._create_boh_room_from_zone(undersized_boh_poly, wall_thickness=50.0, layer_name="BOH_WALL_VALID", hatch_color=252) # Gray hatch
                                # --- REPLACED CODE ENDS HERE ---
                    else:
                        print("    -> ⚠️ Last clinic in row is blocked. Deferring to next row.")
            
            # --- Standard placement for subsequent rows (2nd, 3rd, etc.) ---
            else:
                row_fixtures = best_layout['fixtures_for_row']
                total_row_width = sum((f.width if o == 'H' else f.height) for f, o in zip(row_fixtures, best_layout['combo'])) + sum(best_layout['gaps'])
                LEFT_NUDGE = 0.0
                row_start_x = last_row_details.get("bbox", [anchor_details["bounds"][0]])[0] + LEFT_NUDGE
                placed_bboxes_in_this_row = []
                vertical_clinic_count_in_row = 0
                for i, (orient, fxtr) in enumerate(zip(best_layout['combo'], row_fixtures)):
                    w, h, gap = (fxtr.width if orient == 'H' else fxtr.height), (fxtr.height if orient == 'H' else fxtr.width), best_layout['gaps'][i]
                    xscale, yscale = (-1.0 if orient == 'H' else 1.0), 1.0
                    if orient == 'V':
                        vertical_clinic_count_in_row += 1
                        if vertical_clinic_count_in_row % 2 == 0: yscale = -1.0
                    
                    target_y = y_cursor - h
                    target_center = Vec2(row_start_x + w/2, target_y + h/2)
                    rotation = 0 if orient == 'H' else 90
                    new_bbox = self._validate_and_place_in_open_space(fxtr, target_center, rotation, placed_bboxes, xscale=xscale, yscale=yscale)
                    if new_bbox:
                        placed_bboxes_in_this_row.append(new_bbox)
                        placed_count_plan_a += 1
                        clinic_names_queue.popleft()
                        row_start_x += w + gap
                    else:
                        print(f"      -> ⚠️ Could not place '{fxtr.name}'. Halting row placement.")
                        clinic_names_queue.clear(); break
            
            # --- Update state for the next row ---
            if placed_bboxes_in_this_row:
                min_x = min(b[0] for b in placed_bboxes_in_this_row); min_y = min(b[1] for b in placed_bboxes_in_this_row)
                max_x = max(b[2] for b in placed_bboxes_in_this_row); max_y = max(b[3] for b in placed_bboxes_in_this_row)
                combined_row_bbox = (min_x, min_y, max_x, max_y)
                h_count = best_layout['combo'].count('H'); v_count = best_layout['combo'].count('V')
                dominant_orientation = 'H' if h_count >= v_count else 'V'
                last_row_details = {"bbox": combined_row_bbox, "orientation": dominant_orientation}
                VERTICAL_ROW_GAP = 10.0
                y_cursor = combined_row_bbox[1] - VERTICAL_ROW_GAP
                if is_first_row: is_first_row = False
            else: 
                # If nothing was placed in the row, we must advance the state to avoid an infinite loop
                if is_first_row: is_first_row = False
                y_cursor -= 500 # Nudge y_cursor down to try a new area
        
        # --- Plan B Fallback ---
        if placed_count_plan_a == 0 and [name for name, count in clinic_config.items() if count > 0]:
             print("\n  -> Plan A failed to place any clinics. Activating Fallback...")
             clinics_to_place_obj = [Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"]) for name, count in clinic_config.items() if count > 0 for _ in range(count)]
             remaining = self.place_clinics_by_perimeter_walk(clinics_to_place_obj, placed_bboxes)
             if remaining: print(f"    -> ⚠️ Fallback finished with {len(remaining)} unplaced clinics.")
        else:
             print(f"\n✅ Plan A Succeeded. Placed {placed_count_plan_a} clinics.")

    # In DXF_Controller.py
    # In DXF_Controller.py

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


    def _analyze_top_wall_with_bulge_detection_new(self, small_bulge_max_width=250, small_bulge_max_depth=150):
        """
        [FINAL ROBUST VERSION] Performs a "smart walk" along the top wall.
        - NEW: Intelligently finds ALL top wall segments, regardless of corner order,
        making it robust for any floorplan shape.
        - Classifies diversions as small (ignorable) or large (obstacles).
        """
        from ezdxf.math import Vec2
        print("  -> Starting 'Smart Walk' analysis of top wall...")
        
        ### --- ROBUST TOP WALL IDENTIFICATION (NEW LOGIC) --- ###
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
            # Check if the segment's midpoint is in the top zone
            if (p1.y + p2.y) / 2 > y_threshold:
                # Check if the segment is mostly horizontal
                if abs(p1.y - p2.y) < abs(p1.x - p2.x):
                    # Ensure segment goes from left to right for consistent walking
                    if p1.x < p2.x:
                        top_segments.append((p1, p2))
                    else:
                        top_segments.append((p2, p1))
        
        # 3. Sort the found top segments from left to right to create the "walk" path
        top_segments.sort(key=lambda seg: seg[0].x)
        ### --- END OF NEW LOGIC --- ###

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
                # This is a small, ignorable gap/bulge, so we continue the current wall
                continue
            else:
                # This is a large bulge/step. End the current zone.
                print(f"    -> Found LARGE diversion (w:{deviation_width:.0f}, d:{deviation_depth:.0f}). Ending wall zone.")
                placeable_zones.append({
                    'start': current_flat_wall_start, 
                    'end': current_seg_end, 
                    'length': current_seg_end.distance(current_flat_wall_start)
                })
                # Start a new zone from the beginning of the next segment
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


        
    def _analyze_top_wall_with_bulge_detection_new_og(self, small_bulge_max_width=200.0, small_bulge_max_depth=100.0):
        """
        [FINAL ROBUST VERSION] Performs a "smart walk" along the top wall.
        - NEW: Intelligently finds ALL top wall segments, regardless of corner order,
        making it robust for any floorplan shape.
        - Classifies diversions as small (ignorable) or large (obstacles).
        """
        from ezdxf.math import Vec2
        print("  -> Starting 'Smart Walk' analysis of top wall...")
        
        ### --- ROBUST TOP WALL IDENTIFICATION (NEW LOGIC) --- ###
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
            # Check if the segment's midpoint is in the top zone
            if (p1.y + p2.y) / 2 > y_threshold:
                # Check if the segment is mostly horizontal
                if abs(p1.y - p2.y) < abs(p1.x - p2.x):
                    # Ensure segment goes from left to right for consistent walking
                    if p1.x < p2.x:
                        top_segments.append((p1, p2))
                    else:
                        top_segments.append((p2, p1))
        
        # 3. Sort the found top segments from left to right to create the "walk" path
        top_segments.sort(key=lambda seg: seg[0].x)
        ### --- END OF NEW LOGIC --- ###

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
                # This is a small, ignorable gap/bulge, so we continue the current wall
                continue
            else:
                # This is a large bulge/step. End the current zone.
                print(f"    -> Found LARGE diversion (w:{deviation_width:.0f}, d:{deviation_depth:.0f}). Ending wall zone.")
                placeable_zones.append({
                    'start': current_flat_wall_start, 
                    'end': current_seg_end, 
                    'length': current_seg_end.distance(current_flat_wall_start)
                })
                # Start a new zone from the beginning of the next segment
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

    
            
    ##--new-test--with---greedy method-- strategy ---- new -- wall-walk method
    ##--new-test--with---greedy method-- strategy ---- new -- wall-walk method


    




#---- CLINIC PLACEMENT FUNCTION FINISHED HERE ----


#---- PICKUP WINDOW PLACEMENT FUNCTION STARTS HERE ----

    

    def place_pickup_window_next_to_clinic_og(self, placed_bboxes: List[tuple]):
        """
        Places the Pick_up_window fixture using a multi-tiered strategy.
        - Primary: Places the fixture flush against the right-most wall, searching
          inward if the edge is blocked.
        - Fallback: If the primary strategy fails, places the fixture 800mm to the
          right of the last-numbered clinic.
        """
        from Fixture import Fixture
        from ezdxf.bbox import extents
        from shapely.geometry import box

        print("\n--- 🧠 Placing Pick-up Window (Right Wall Strategy with Fallback) ---")

        # 1. SETUP: Load fixture (Unchanged)
        try:
            config = self.fixtures.get("pickup_window", {})
            fixture_count = config.get("Pick_up_window", 0)
            if fixture_count <= 0:
                print("  -> SKIPPED: No Pick_up_window fixture specified.")
                return
            fixture_obj = Fixture("Pick_up_window", self.fixture_dict["Pick_up_window"]["path"])
        except Exception as e:
            print(f"  -> 🔥 ERROR during Pick_up_window setup: {e}")
            return

        # 2. Find and sort clinics for the primary strategy (Unchanged)
        clinic_entities = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
        if not clinic_entities:
            print("  -> ⚠️ FAILED: Cannot place Pick_up_window because no clinics were found.")
            return
        clinic_entities.sort(key=lambda e: e.dxf.insert.x, reverse=True)
        print(f"  -> Found {len(clinic_entities)} clinic(s) to use as vertical anchors.")

        # 3. PRIMARY STRATEGY: Loop through clinics and search inward from the right wall
        is_placed = False
        margin_from_wall = 50.0

        for i, anchor_clinic in enumerate(clinic_entities):
            anchor_bbox = extents([anchor_clinic])
            print(f"  -> Attempting to anchor to clinic #{i+1} (right-most).")

            ideal_x = self.cvc.max_x - fixture_obj.width - margin_from_wall
            target_y = anchor_bbox.center.y - (fixture_obj.height / 2)
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

            if is_placed:
                break 

        # --- NEW: FINAL FALLBACK STRATEGY ---
        if not is_placed:
            print(f"\n  -> ⚠️ Primary wall strategy failed. Attempting final fallback: Place 800mm from last clinic.")

            # 1. Find the last clinic by its number
            def get_clinic_number(entity):
                try: return int(entity.dxf.name.split('_')[-1])
                except (ValueError, IndexError): return float('inf')

            all_clinics = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
            if not all_clinics:
                print("  -> ⚠️ FALLBACK FAILED: No clinics found to anchor to.")
                return

            all_clinics.sort(key=get_clinic_number)
            last_clinic_entity = all_clinics[-1]
            anchor_bbox = extents([last_clinic_entity])
            print(f"  -> Fallback anchor: '{last_clinic_entity.dxf.name}'")

            # 2. Calculate position with a fixed 800mm gap
            gap = 800.0
            target_x = anchor_bbox.extmax.x + gap
            target_y = anchor_bbox.center.y - (fixture_obj.height / 2)

            # 3. Validate and place
            candidate_box = box(target_x, target_y, target_x + fixture_obj.width, target_y + fixture_obj.height)
            is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
            is_inside = self.floorplan_polygon.contains(candidate_box)

            if is_inside and not is_overlapping:
                self.place_fixture(fixture_obj, (target_x, target_y, 0), 0, False)
                placed_bboxes.append(candidate_box.bounds)
                print(f"    ✅ SUCCESS (Fallback): Placed '{fixture_obj.name}' with a {gap:.0f}mm gap.")
            else:
                print(f"  -> ⚠️ FINAL FAILURE: The fallback spot was also blocked or outside the boundary.")

    def place_pickup_window_next_to_clinic(self, placed_bboxes: List[tuple]):
        """
        [MODIFIED V3] Places the Pick_up_window fixture using a consistent vertical anchor.
        - An anchor clinic (the last one placed) determines the Y-level for all attempts.
        - Primary: Tries to place the window at this Y-level against the right wall.
        - Fallback: If the wall is blocked, places it at the same Y-level next to the anchor clinic.
        """
        from Fixture import Fixture
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
            fixture_obj = Fixture("Pick_up_window", self.fixture_dict["Pick_up_window"]["path"])
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
            print(f"\n  -> ⚠️ Primary wall strategy failed. Attempting Fallback: Place next to anchor clinic.")
            
            # The anchor is already identified as y_anchor_clinic.
            fallback_anchor_bbox = y_anchor_bbox
            print(f"  -> Fallback anchor is '{y_anchor_clinic.dxf.name}'")

            # Determine anchor's orientation and set gap
            rotation = y_anchor_clinic.dxf.rotation
            is_vertical = (85 < rotation < 95) or (265 < rotation < 275)

            if is_vertical:
                gap = 800.0
                print("    -> Anchor clinic is VERTICAL. Using 800mm gap.")
            else:
                gap = 50.0
                print("    -> Anchor clinic is HORIZONTAL. Using 50mm gap.")
            
            # Calculate fallback position (X changes, Y stays the same)
            target_x_fallback = fallback_anchor_bbox.extmax.x + gap
            # The target_y is already calculated and is consistent for both strategies.

            # Validate and place at fallback position
            candidate_box_fallback = box(target_x_fallback, target_y, target_x_fallback + fixture_obj.width, target_y + fixture_obj.height)
            is_overlapping_fallback = any(candidate_box_fallback.intersects(box(*b)) for b in placed_bboxes)
            is_inside_fallback = self.floorplan_polygon.contains(candidate_box_fallback)

            if is_inside_fallback and not is_overlapping_fallback:
                self.place_fixture(fixture_obj, (target_x_fallback, target_y, 0), 0, False)
                placed_bboxes.append(candidate_box_fallback.bounds)
                print(f"    ✅ SUCCESS (Fallback): Placed '{fixture_obj.name}' with a {gap:.0f}mm gap.")
            else:
                print(f"  -> ⚠️ FINAL FAILURE: The fallback spot was also blocked or outside the boundary.")

    
#---------------------NEW_PICKUP_WINDOW FUNCTION WITH PICKUP TABLE FALL BACK SETUP---------------------
#---------------------NEW_PICKUP_WINDOW FUNCTION WITH PICKUP TABLE FALL BACK SETUP---------------------


    # In DXF_Controller.py -> Add these three functions

    def place_pickup_area_fixture(self, placed_bboxes: List[tuple]):
        """
        [NEW DISPATCHER] Intelligently places either the 'pickup_table' or 'Pick_up_window'
        based on the method used for clinic placement.
        - Plan A (Standard Clinic Placement): Places 'pickup_table' in the BOH zone.
        - Plan B (Fallback Clinic Placement): Places 'Pick_up_window' next to the last clinic.
        """
        print("\n---  Orchestrating Pickup Area Fixture Placement ---")

        # Check the flag set by the clinic placement strategy
        if not hasattr(self, 'clinic_placement_method') or self.clinic_placement_method == 'Unknown':
            print("  -> SKIPPED: Clinic placement method is unknown. Cannot determine which pickup fixture to place.")
            return

        if self.clinic_placement_method == 'Plan_A':
            print("  -> Clinic placement used Plan A. Placing 'pickup_table' in BOH zone.")
            self._place_pickup_table_in_boh(placed_bboxes)
        
        elif self.clinic_placement_method == 'Plan_B':
            print("  -> Clinic placement used Plan B Fallback. Placing 'Pick_up_window'.")
            # self._place_pickup_window_fallback(placed_bboxes)
            self.place_pickup_window_next_to_clinic(placed_bboxes)


    def _place_pickup_table_in_boh(self, placed_bboxes: List[tuple]):
        """
        [MODIFIED] Places the 'pickup_table' in the BOH zone. It starts at the
        bottom-left and searches rightwards along the bottom edge until a
        clear spot is found. Includes a 150mm downward nudge for better aesthetics.
        """
        from Fixture import Fixture
        from shapely.geometry import box
        
        # 1. Load fixture
        try:
            pickup_config = self.fixtures.get("pickup_window", {})
            boh_config = self.fixtures.get("boh_fixtures", {})
            
            if pickup_config.get("pickup_table", 0) <= 0 and boh_config.get("pickup_table", 0) <= 0:
                print("  -> SKIPPED: 'pickup_table' not specified in configuration.")
                return
            
            fixture_obj = Fixture("pickup_table", self.fixture_dict["pickup_table"]["path"])
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
    
    def _place_pickup_window_fallback(self, placed_bboxes: List[tuple]):
        """Places the Pick_up_window next to the last-placed clinic with a dynamic gap."""
        from Fixture import Fixture
        from ezdxf.bbox import extents
        from shapely.geometry import box
        import math

        try:
            config = self.fixtures.get("pickup_window", {})
            if config.get("Pick_up_window", 0) <= 0:
                print("  -> SKIPPED: 'Pick_up_window' not specified in configuration.")
                return
            fixture_obj = Fixture("Pick_up_window", self.fixture_dict["Pick_up_window"]["path"])
        except Exception as e:
            print(f"  -> 🔥 ERROR during Pick_up_window setup: {e}"); return

        all_clinics = [e for e in self.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
        if not all_clinics:
            print("  -> ⚠️ FAILED: No clinics found to anchor to."); return

        def get_clinic_number(entity):
            try: return int(entity.dxf.name.split('_')[-1])
            except (ValueError, IndexError): return float('inf')

        all_clinics.sort(key=get_clinic_number)
        anchor_clinic = all_clinics[-1]
        anchor_bbox = extents([anchor_clinic])
        print(f"  -> Fallback anchor is '{anchor_clinic.dxf.name}'")

        rotation = anchor_clinic.dxf.rotation
        is_vertical = (85 < rotation < 95) or (265 < rotation < 275)
        gap = 800.0 if is_vertical else 50.0
        print(f"    -> Anchor clinic is {'VERTICAL' if is_vertical else 'HORIZONTAL'}. Using {gap:.0f}mm gap.")
        
        target_x = anchor_bbox.extmax.x + gap
        target_y = anchor_bbox.center.y - (fixture_obj.height / 2)

        candidate_box = box(target_x, target_y, target_x + fixture_obj.width, target_y + fixture_obj.height)
        is_overlapping = any(candidate_box.intersects(box(*b)) for b in placed_bboxes)
        is_inside = self.floorplan_polygon.contains(candidate_box)

        if is_inside and not is_overlapping:
            self.place_fixture(fixture_obj, (target_x, target_y, 0), 0, False)
            placed_bboxes.append(candidate_box.bounds)
            print(f"    ✅ SUCCESS (Fallback): Placed '{fixture_obj.name}' with a {gap:.0f}mm gap.")
        else:
            print(f"  -> ⚠️ FINAL FAILURE: The fallback spot was also blocked or outside the boundary.")
#---------------------NEW_PICKUP_WINDOW FUNCTION WITH PICKUP TABLE FALL BACK SETUP---------------------
#---------------------NEW_PICKUP_WINDOW FUNCTION WITH PICKUP TABLE FALL BACK SETUP---------------------


#---- PICKUP WINDOW PLACEMENT FUNCTION FINISHED HERE ----


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
        from Fixture import Fixture

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
                    fxtr = Fixture(name, self.fixture_dict[name]["path"])
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
        from Fixture import Fixture
        import collections

        print("\n--- 🏥 Placing Clinics at Top Wall ---")
        clinic_config = self.fixtures.get("clinic_fixtures", {})
        if not any(clinic_config.values()):
            print("  -> INFO: No clinic fixtures specified.")
            return

        clinics_to_place = []
        for clinic_type, count in clinic_config.items():
            if count > 0:
                fxtr = Fixture(self.fixture_dict[clinic_type]["name"], self.fixture_dict[clinic_type]["path"])
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
        from Fixture import Fixture
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
                preset_fxtr = Fixture(preset_name, self.fixture_dict[preset_name]["path"])
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
        [MODIFIED] Finds the created BOH room and furnishes it using a two-phase strategy.
        - It now correctly checks against ALL previously placed fixtures (including the pickup_table)
          to prevent overlaps.
        """
        from Fixture import Fixture
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
                    fxtr = Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"])
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
            while fallback_queue:
                fixture_to_place = fallback_queue.popleft()
                placed_in_fallback = False

                for y_try in range(int(max_y - fixture_to_place.height), int(min_y), -int(step)):
                    for x_try in range(int(min_x), int(max_x - fixture_to_place.width), int(step)):
                        
                        target_center = Vec2(x_try + fixture_to_place.width / 2, y_try + fixture_to_place.height / 2)
                        
                        local_center = fixture_to_place.bounding_box.center
                        transform = Matrix44.chain(
                            Matrix44.translate(-local_center.x, -local_center.y, 0),
                            Matrix44.scale(-1.0, -1.0, 1.0),
                            Matrix44.z_rotate(math.radians(0)),
                            Matrix44.translate(target_center.x, target_center.y, 0)
                        )
                        world_corners = list(transform.transform_vertices(fixture_to_place.bounding_box.rect_vertices()))
                        fixture_polygon = Polygon([(p.x, p.y) for p in world_corners])
                        aabb = BoundingBox2d(world_corners)

                        is_inside = boh_placement_zone.contains(fixture_polygon.buffer(-1.0))

                        # ******************** MODIFICATION 2 ********************
                        # This also now checks against the main 'placed_bboxes' list.
                        is_overlapping = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)
                        # ********************************************************

                        if is_inside and not is_overlapping:
                            local_center_scaled = Vec2(local_center.x * -1.0, local_center.y * -1.0)
                            final_insert_point = target_center - local_center_scaled
                            self.place_fixture(fixture_to_place, (final_insert_point.x, final_insert_point.y, 0), 0, True, xscale=-1.0, yscale=-1.0)
                            
                            bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)
                            placed_bboxes.append(bbox_tuple) # Add to the main list
                            internal_boh_bboxes.append(bbox_tuple) # Also add to the internal list
                            
                            print(f"    -> Placed '{fixture_to_place.name}' in open space (Fallback).")
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

    

#----NEW-BOH-PLACEMENT-STRATEGY-BOH-AREA----
#----NEW-BOH-PLACEMENT-STRATEGY-BOH-AREA----
#---- BOH PLACEMENT FUNCTION FINISHED HERE ----


#--CATEGORY :- Seating (clinic/AR)

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

    def _calculate_dynamic_vertical_gap_strategy_2(self) -> float:
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
            gap = 8.0
            print(f"      -> Area is small (<= 500 sq. ft.). Using a tight gap of {gap} mm.")
        elif floor_area_sqft <= 750:
            gap = 8.0
            print(f"      -> Area is medium-small (<= 750 sq. ft.). Using a gap of {gap} mm.")
        elif floor_area_sqft <= 1000:
            gap = 8.0
            print(f"      -> Area is medium (<= 1000 sq. ft.). Using a standard gap of {gap} mm.")
        elif floor_area_sqft <= 1250:
            gap = 8.0
            print(f"      -> Area is medium-large (<= 1250 sq. ft.). Using a wider gap of {gap} mm.")
        elif floor_area_sqft <= 1500:
            gap = 8.0
            print(f"      -> Area is large (<= 1500 sq. ft.). Using a very wide gap of {gap} mm.")
        else:  # for floorplans larger than 1500 sq. ft.
            gap = 8.0
            print(f"      -> Area is very large (> 1500 sq. ft.). Using a maximum gap of {gap} mm.")

        return gap

    def place_central_fixtures_portrait_strategy_2(self, placed_bboxes: List[tuple], bottom_margin_pct: float = 0.20) -> None:
        """
        Places central fixtures in a portrait orientation by creating and placing
        vertical stacks. This function corrects the placement logic for rotated fixtures
        to ensure proper alignment and avoid validation failures.
        """
        from Fixture import Fixture
        from shapely.geometry import box, LineString
        import math
        import collections

        print("\n--- 🧠 Placing Central Fixtures with Vertical Stacking (Portrait Mode) ---")

        # --- 1. SETUP & LOAD FIXTURES ---
        GAP_EURO_TO_EURO = 2000.0
        GAP_LENSBAR_TO_LENSBAR = 50.0 
        
        
        # We will use this to determine the maximum number of fixtures to try in a stack
        # based on the total number of euros requested.
        total_euros = self.fixtures.get("floor_fixtures", {}).get("Euro_centre", 0)

        # A single dynamic variable to control all vertical spacing
        # This keeps things consistent across the entire floorplan
        vertical_row_spacing = self._calculate_dynamic_vertical_gap_strategy_2() # Add a buffer

        config = self.fixtures.get("floor_fixtures", {})
        euro_count = config.get("Euro_centre", 0)
        lensbar_count = config.get("Lensbar", 0)
        if euro_count + lensbar_count == 0:
            return

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

        # --- 2. DEFINE PLACEMENT ZONE & PARAMETERS ---
        room_height = self.cvc.max_y - self.cvc.min_y
        # This is a fixed margin from the bottom, no longer dynamic
        aisle_buffer = room_height * bottom_margin_pct
        
        cursor_y = self.cvc.min_y + aisle_buffer
        cursor_y_end = self.cvc.max_y - 5.0

        print("  -> Configuring for PORTRAIT (Vertical Iteration, Horizontal Rows)")

        def _is_rotated_row_valid(start_x, y, fixtures_in_row, gap):
            current_x_in_row = start_x
            for i, fxtr in enumerate(fixtures_in_row):
                rotated_width, rotated_height = fxtr.height, fxtr.width
                candidate_box = box(current_x_in_row, y, current_x_in_row + rotated_width, y + rotated_height)
                if not self.floorplan_polygon.contains(candidate_box.buffer(-1.0)) or any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                    return False
                if i < len(fixtures_in_row) - 1:
                    current_x_in_row += rotated_width + gap
            return True
        
        def _calculate_dynamic_euro_gap(num_in_stack):
            """Calculates a dynamic horizontal gap for Euros based on stack size."""
            if num_in_stack <= 1:
                return 0.0
            elif num_in_stack == 2:
                return 1000.0
            elif num_in_stack == 3:
                return 1200.0
            else:
                # A tighter gap for more than 2 fixtures
                return 1200
        
        def _find_best_stack_size(local_width, walking_margin, total_euros_in_queue, fixture_obj):
            """
            Finds the largest possible stack that fits within the available space.
            Returns the stack size and the gap to use.1
            """
            max_to_try = 3
            for n in range(min(max_to_try, total_euros_in_queue), 0, -1):
                gap = _calculate_dynamic_euro_gap(n)
                required_width = (fixture_obj.height * n) + (gap * (n - 1)) + walking_margin 
                if required_width <= local_width:
                    return n, gap
            return 0, 0


        # --- 3. MAIN PLACEMENT LOOP ---
        while fixture_queue:
            if cursor_y > cursor_y_end:
                print("    -> ⚠️ Ran out of vertical space. Stopping placement.")
                break

            next_fxtr_obj = fixture_queue[0]
            stack_width = next_fxtr_obj.height # The rotated dimension

            # Get the available horizontal space at this vertical position
            intersection = self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, cursor_y + (next_fxtr_obj.width / 2)), (self.cvc.max_x + 100, cursor_y + (next_fxtr_obj.width / 2))]))

            if not isinstance(intersection, LineString) or intersection.is_empty:
                cursor_y += 100
                continue

            local_space_bounds = intersection.bounds
            local_width = local_space_bounds[2] - local_space_bounds[0]
            local_start_x = local_space_bounds[0]

            # Use a dynamic margin that shrinks as the available space gets tighter
            walking_space_margin = max(300.0, local_width * 0.50)

            # Determine the stack size and gap
            num_to_place = 0
            horizontal_gap = 0
            if next_fxtr_obj.name == "Lensbar":
                # Lensbars are typically placed one at a time
                if next_fxtr_obj.height + walking_space_margin <= local_width:
                    num_to_place = 1
            elif next_fxtr_obj.name == "Euro_centre":
                num_to_place, horizontal_gap = _find_best_stack_size(local_width, walking_space_margin, len(fixture_queue), next_fxtr_obj)

            if num_to_place == 0:
                cursor_y += 100
                continue

            # --- 4. EXECUTION WITH RESILIENT SEARCH ---
            fixtures_for_this_row = [fixture_queue[i] for i in range(num_to_place)]
            total_row_width = (stack_width * num_to_place) + (horizontal_gap * (num_to_place - 1))
            
            ideal_start_x = local_start_x + (local_width - total_row_width) / 2
            
            valid_start_x = None
            search_offset = 0
            # Search out from the ideal center until a spot is found
            while valid_start_x is None and search_offset < local_width / 2:
                for sign in [1, -1]:
                    test_x = ideal_start_x + (search_offset * sign) - 5
                    if _is_rotated_row_valid(test_x, cursor_y, fixtures_for_this_row, horizontal_gap):
                        valid_start_x = test_x
                        break
                search_offset += 100
            
            if valid_start_x is None:
                print(f"    -> ⚠️ Could not find a valid horizontal spot for the row. Skipping.")
                cursor_y += 100
                continue

            current_x_in_row = valid_start_x
            for i in range(num_to_place):
                fxtr = fixture_queue.popleft()
                rotated_width, rotated_height = fxtr.height, fxtr.width
                
                target_center_x = current_x_in_row + (rotated_width / 2)
                target_center_y = cursor_y + (rotated_height / 2)
                
                if self._validate_and_place_at_point(fxtr, Vec2(target_center_x, target_center_y), 90, placed_bboxes):
                    print(f"    -> Placed '{fxtr.name}' at ({current_x_in_row:.0f}, {cursor_y:.0f})")
                else:
                    print(f"    -> ⚠️ Final validation failed for '{fxtr.name}' during placement.")
                
                current_x_in_row += rotated_width + horizontal_gap

            cursor_y += rotated_height + vertical_row_spacing

        if fixture_queue:
            print(f"\n--- ⚠️ Finished with {len(fixture_queue)} unplaced fixtures ---")
        else:
            print("\n--- ✅ Finished Dynamic Central Fixture Placement ---")


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
            gap = 200.0
            print(f"      -> Area is small (<= 500 sq. ft.). Using a tight gap of {gap} mm.")
        elif floor_area_sqft <= 750:
            gap = 600.0
            print(f"      -> Area is medium-small (<= 750 sq. ft.). Using a gap of {gap} mm.")
        elif floor_area_sqft <= 1000:
            gap = 1200.0
            print(f"      -> Area is medium (<= 1000 sq. ft.). Using a standard gap of {gap} mm.")
        elif floor_area_sqft <= 1250:
            gap = 1200.0
            print(f"      -> Area is medium-large (<= 1250 sq. ft.). Using a wider gap of {gap} mm.")
        elif floor_area_sqft <= 1500:
            gap = 1200.0
            print(f"      -> Area is large (<= 1500 sq. ft.). Using a very wide gap of {gap} mm.")
        else:  # for floorplans larger than 1500 sq. ft.
            gap = 1200.0
            print(f"      -> Area is very large (> 1500 sq. ft.). Using a maximum gap of {gap} mm.")

        return gap

    def place_central_fixtures_portrait(self, placed_bboxes: List[tuple], bottom_margin_pct: float = 0.20) -> None:
        """
        Places central fixtures in a portrait orientation using an adaptive strategy.
        - MODIFIED: Now dynamically calculates the number of fixtures per row based on available width.
        """
        # Import necessary libraries for geometry and data structures.
        from Fixture import Fixture
        from shapely.geometry import box, LineString
        import math
        import collections

        print("\n--- 🧠 Placing Central Fixtures with DYNAMIC ROW SIZING (Portrait Mode) ---")

        # --- Define Horizontal Gaps ---
        # These constants define the fixed spacing between fixtures when they are placed side-by-side in a row.
        GAP_EURO_TO_EURO = 5.0       # The gap between two Euro_centre fixtures. (horizontal gap)
        GAP_LENSBAR_TO_LENSBAR = 50.0 # The gap between two Lensbar fixtures.
        
        
        # This variable controls the vertical spacing BETWEEN each row of fixtures.
        # It's calculated dynamically based on the store's size to ensure good proportions.
        VERTICAL_ROW_GAP = self._calculate_dynamic_vertical_gap()

        # 1. SETUP & LOAD FIXTURES
        # --------------------------
        # Load the fixture counts (e.g., 5 Euro_centre, 2 Lensbar) from the main configuration.
        config = self.fixtures.get("floor_fixtures", {})
        euro_count = config.get("Euro_centre", 0)
        lensbar_count = config.get("Lensbar", 0)
        # If no central fixtures are requested, exit the function early.
        if euro_count + lensbar_count == 0: return

        # A deque (a double-ended queue) is used as an efficient "to-do list" of fixtures.
        fixture_queue = collections.deque()
        try:
            # Load the fixture data (like dimensions and file path) for each type.
            euro_fxtr_template = Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"]) if euro_count > 0 else None
            lensbar_fxtr_template = Fixture("Lensbar", self.fixture_dict["Lensbar"]["path"]) if lensbar_count > 0 else None
            
            # Add the requested number of fixture objects to our to-do list.
            if lensbar_count > 0:
                fixture_queue.extend([lensbar_fxtr_template] * lensbar_count)
            if euro_count > 0:
                fixture_queue.extend([euro_fxtr_template] * euro_count)
        except Exception as e:
            print(f"🔥 FATAL: Could not load a central fixture: {e}")
            return

        # 2. DEFINE PORTRAIT-SPECIFIC PARAMETERS
        # --------------------------------------
        print("  -> Configuring for PORTRAIT (Vertical Iteration, Horizontal Rows)")
        # Calculate the total height of the room available for placement.
        room_height = self.cvc.max_y - self.cvc.min_y
        # Create a buffer at the bottom of the room to act as a main aisle.
        aisle_buffer = room_height * bottom_margin_pct
        
        # Set up a "cursor" that will move from the bottom of the room upwards.
        # This defines the vertical zone where fixtures can be placed.
        cursor_pos = self.cvc.min_y + aisle_buffer
        cursor_end = self.cvc.max_y - 50.0 # this we can set as a fixed top margin to make good retail  space adjusting
        # A quick helper function to find out how wide the floorplan is at any given height (y-coordinate).
        get_local_space = lambda y: self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, y), (self.cvc.max_x + 100, y)]))

        def _is_row_valid(start_x, y, fixtures_in_row, gap):
            """
            Checks if a proposed row of fixtures would fit without going outside 
            the floorplan boundary or overlapping any already-placed objects.
            """
            current_x = start_x
            for i, fxtr in enumerate(fixtures_in_row):
                # Create a virtual box representing the fixture's position.
                candidate_box = box(current_x, y, current_x + fxtr.width, y + fxtr.height)
                # If the box is outside the floorplan or hits another object, the row is invalid.
                if not self.floorplan_polygon.contains(candidate_box.buffer(-1.0)) or any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                    return False
                # Move the virtual cursor to the right for the next fixture in the row.
                if i < len(fixtures_in_row) - 1:
                    current_x += fxtr.width + gap
            return True

        # ⭐ --- THIS IS THE CORE DECISION-MAKING LOGIC --- ⭐
        def _find_best_row_size(available_width, margin, fixtures_in_queue, fixture_obj, gap):
            """
            Finds the largest number of fixtures that can fit in a standard horizontal row.
            This is adapted from strategy_2 but uses fixture.width (no rotation).
            """
            # Set a hard limit on the maximum number of fixtures allowed in a single row.
            max_fixtures_to_try = 3 

            # This loop implements the "greedy" or "count down" strategy.
            # It starts by trying to fit the maximum possible number (e.g., 3) and works down to 1.
            # The first number that fits is guaranteed to be the best (largest) option.
            for n in range(min(max_fixtures_to_try, fixtures_in_queue), 0, -1):
                # Calculate the total space needed for 'n' fixtures.
                # This is: (total width of all fixtures) + (total width of all gaps) + (a safety margin).
                required_width = (fixture_obj.width * n) + (gap * (n - 1)) + margin
                
                # If the space we need is less than or equal to the space we have...
                if required_width <= available_width:
                    print(f"  -> Determined that {n} fixtures can fit in the available space.")
                    return n # ...then we've found our answer. Return this number and stop checking.
            
            # If the loop finishes without finding a fit, it means not even one fixture could be placed.
            return 0 

        # 3. ADAPTIVE PLACEMENT LOOP
        # --------------------------
        # This is the main loop that continues as long as there are fixtures in our "to-do list".
        while fixture_queue:
            # Safety check: if our vertical cursor goes past the top boundary, stop.
            if cursor_pos > cursor_end:
                print("    -> ⚠️ Ran out of vertical space. Stopping placement.")
                break

            # Peek at the next fixture in line to get its dimensions, without removing it yet.
            next_fxtr_obj = fixture_queue[0]
            # The "footprint" of a row is determined by the height of the fixtures in it.
            footprint = next_fxtr_obj.height
            # Get the available horizontal space at the current vertical position of our cursor.
            intersection = get_local_space(cursor_pos + (footprint / 2))
            if not isinstance(intersection, LineString) or intersection.is_empty:
                cursor_pos += 100 # If there's no space here, nudge the cursor up and try again.
                continue

            # Get the exact start and end coordinates of the available horizontal space.
            local_space_bounds = intersection.bounds
            local_width = local_space_bounds[2] - local_space_bounds[0]
            local_start_x = local_space_bounds[0]

            # 4. ⭐ --- DYNAMIC DECISION LOGIC --- ⭐
            # ------------------------------------
            # The margin for walking space is a percentage of the room's width,
            # so it automatically adapts to narrower or wider areas of the floorplan.
            walking_space_margin = max(300.0, local_width * 0.60) 
            
            # Get the name of the next fixture (e.g., "Euro_centre").
            fixture_type = next_fxtr_obj.name
            
            # We only want to group fixtures of the same type (e.g., a row of Euros).
            # This loop counts how many fixtures of the same type are at the front of the queue.
            count_of_same_type_in_queue = 0
            for f in fixture_queue:
                if f.name == fixture_type:
                    count_of_same_type_in_queue += 1
                else:
                    break
            
            # Determine which horizontal gap value to use based on the fixture type.
            horizontal_gap = 0
            if fixture_type == "Euro_centre":
                horizontal_gap = GAP_EURO_TO_EURO
            elif fixture_type == "Lensbar":
                horizontal_gap = GAP_LENSBAR_TO_LENSBAR

            # This is the crucial call to our helper function. Based on the available width and fixture
            # dimensions, it decides exactly how many fixtures (`num_to_place`) we should attempt to place in this row.
            num_to_place = _find_best_row_size(
                local_width, 
                walking_space_margin, 
                count_of_same_type_in_queue, 
                next_fxtr_obj, 
                horizontal_gap
            )
            
            # If the helper function returned 0, it means nothing could fit.
            # We nudge the cursor up and continue to the next iteration of the main loop.
            if num_to_place == 0:
                cursor_pos += 100
                continue

            # 5. EXECUTION WITH RESILIENT SEARCH
            # ----------------------------------
            # Get the list of fixtures we are about to place in this row.
            fixtures_for_this_row = [fixture_queue[i] for i in range(num_to_place)]
            # If we're only placing one fixture, there's no gap needed.
            current_gap = horizontal_gap if num_to_place > 1 else 0
            # Calculate the exact total width of our new row.
            total_row_width = sum(f.width for f in fixtures_for_this_row) + (current_gap * (num_to_place - 1))
            
            # Calculate the starting X-coordinate that would perfectly center the row.
            ideal_start_x = local_start_x + (local_width - total_row_width) / 2
            
            # The ideal center spot might be blocked. This "resilient search" loop will
            # check the center, then slightly to the right, then slightly to the left,
            # expanding outwards until it finds a clear spot for the entire row.
            valid_start_x = None
            search_offset = 0
            max_search = local_width / 2

            while search_offset < max_search:
                for sign in [1, -1]: # sign=1 checks right, sign=-1 checks left
                    if sign == -1 and search_offset == 0: continue
                    test_x = ideal_start_x + (search_offset * sign)
                    # Use our validation helper to see if this spot is clear.
                    if _is_row_valid(test_x, cursor_pos, fixtures_for_this_row, current_gap):
                        valid_start_x = test_x # If it's clear, we've found our spot!
                        break
                if valid_start_x is not None:
                    break
                search_offset += 100 # If not clear, increase the offset and search further out.
            
            # If the search completes and we couldn't find a valid spot, skip this row.
            if valid_start_x is None:
                print(f"    -> ⚠️ Could not find a valid horizontal spot for the row. Skipping.")
                cursor_pos += 100
                continue

            # If we found a valid spot, this loop actually places the fixtures.
            current_x_in_row = valid_start_x
            for i in range(num_to_place):
                # Take the fixture off the "to-do list".
                fxtr = fixture_queue.popleft()
                x1, y1 = current_x_in_row, cursor_pos
                # This function draws the fixture in the DXF file and records its position.
                if self._validate_and_place_at_point(fxtr, Vec2(x1 + fxtr.width/2, y1 + fxtr.height/2), 0, placed_bboxes):
                    print(f"    -> Placed '{fxtr.name}' at ({x1:.0f}, {y1:.0f})")
                else:
                    print(f"    -> ⚠️ Final validation failed for '{fxtr.name}' during placement.")
                
                # Move the horizontal cursor for the next fixture in this same row.
                current_x_in_row += fxtr.width + current_gap

            # After the row is finished, move the main vertical cursor up to prepare for the next row.
            cursor_pos += footprint + VERTICAL_ROW_GAP

        # After the main `while` loop finishes, check if there are any fixtures left.
        if fixture_queue:
            # If the queue isn't empty, it means we ran out of space.
            print(f"\n--- ⚠️ Finished with {len(fixture_queue)} unplaced fixtures ---")
        else:
            # If the queue is empty, all fixtures were placed successfully.
            print("\n--- ✅ Finished Dynamic Central Fixture Placement ---")
           
    
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
                    margin_pct = 0.30
                elif total_vertical_units <= 8:    # Medium congestion
                    margin_pct = 0.30
                else:                              # High congestion
                    margin_pct = 0.30
            
            # Logic for MEDIUM stores (e.g., 750 to 1250 sq. ft.)
            elif floor_area_sqft <= 1250:
                print("      -> Store size is MEDIUM.")
                if total_vertical_units <= 4:      # Low congestion
                    margin_pct = 0.15
                elif total_vertical_units <= 8:    # Medium congestion
                    margin_pct = 0.20
                else:                              # High congestion
                    margin_pct = 0.20

            elif floor_area_sqft <= 2500:
                print("      -> Store size is MEDIUM.")
                if total_vertical_units <= 4:      # Low congestion
                    margin_pct = 0.15
                elif total_vertical_units <= 8:    # Medium congestion
                    margin_pct = 0.15
                else:                              # High congestion
                    margin_pct = 0.10

            # Logic for LARGE stores (e.g., more than 1250 sq. ft.)
            else:
                print("      -> Store size is LARGE.")
                if total_vertical_units <= 4:      # Low congestion
                    margin_pct = 0.15
                elif total_vertical_units <= 8:    # Medium congestion
                    margin_pct = 0.10
                else:                              # High congestion
                    margin_pct = 0.05
            
            print(f"      -> Final dynamic margin selected: {margin_pct:.0%}")
            return margin_pct

        except Exception as e:
            print(f"    -> ⚠️ Could not calculate dynamic margin due to an error: {e}")
            return 0.20 # Return a safe default
    
    
    def _calculate_dynamic_bottom_margin_percentage_str(self) -> float:
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
                    margin_pct = 0.30
                elif total_vertical_units <= 8:    # Medium congestion
                    margin_pct = 0.30
                else:                              # High congestion
                    margin_pct = 0.30
            
            # Logic for MEDIUM stores (e.g., 750 to 1250 sq. ft.)
            elif floor_area_sqft <= 1250:
                print("      -> Store size is MEDIUM.")
                if total_vertical_units <= 4:      # Low congestion
                    margin_pct = 0.15
                elif total_vertical_units <= 8:    # Medium congestion
                    margin_pct = 0.15
                else:                              # High congestion
                    margin_pct = 0.15

            elif floor_area_sqft <= 2500:
                print("      -> Store size is MEDIUM.")
                if total_vertical_units <= 4:      # Low congestion
                    margin_pct = 0.15
                elif total_vertical_units <= 8:    # Medium congestion
                    margin_pct = 0.15
                else:                              # High congestion
                    margin_pct = 0.10

            # Logic for LARGE stores (e.g., more than 1250 sq. ft.)
            else:
                print("      -> Store size is LARGE.")
                if total_vertical_units <= 4:      # Low congestion
                    margin_pct = 0.15
                elif total_vertical_units <= 8:    # Medium congestion
                    margin_pct = 0.10
                else:                              # High congestion
                    margin_pct = 0.05
            
            print(f"      -> Final dynamic margin selected: {margin_pct:.0%}")
            return margin_pct

        except Exception as e:
            print(f"    -> ⚠️ Could not calculate dynamic margin due to an error: {e}")
            return 0.20 # Return a safe default


#---------------------new  test for euro center placement
#---------------------new  test for euro center placement


    def place_central_fixtures_from_qms(self, placed_bboxes: List[tuple]) -> None:
        """
        Places central fixtures by anchoring them a fixed distance above the
        highest placed QMS/Greeter desk, instead of the bottom wall.
        The placement stops before hitting standing tables or the top wall.
        """
        from Fixture import Fixture
        from shapely.geometry import box, LineString
        import math
        import collections
        from ezdxf.bbox import extents

        print("\n--- 🧠 Placing Central Fixtures Anchored to QMS Desk ---")

        # --- 1. SETUP & LOAD FIXTURES (Unchanged) ---
        vertical_row_spacing = self._calculate_dynamic_vertical_gap_strategy_2()
        config = self.fixtures.get("floor_fixtures", {})
        euro_count = config.get("Euro_centre", 0)
        lensbar_count = config.get("Lensbar", 0)
        if euro_count + lensbar_count == 0:
            return

        fixture_queue = collections.deque()
        try:
            if lensbar_count > 0:
                fixture_queue.extend([Fixture("Lensbar", self.fixture_dict["Lensbar"]["path"])] * lensbar_count)
            if euro_count > 0:
                fixture_queue.extend([Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"])] * euro_count)
        except Exception as e:
            print(f"🔥 FATAL: Could not load a central fixture: {e}")
            return

        # --- 2. DEFINE PLACEMENT ZONE (MODIFIED) ---
        qms_entities = [e for e in self.msp.query('INSERT') if "QMS_DESK" in e.dxf.name.upper()]
        
        if not qms_entities:
            print("    -> ⚠️ Could not find a QMS Desk to anchor to. Aborting placement.")
            return

        qms_bbox = extents(qms_entities)
        qms_top_y = qms_bbox.extmax.y
        
        GAP_ABOVE_QMS = 800.0
        cursor_y = qms_top_y + GAP_ABOVE_QMS
        
        
        # =================== THIS SECTION HAS BEEN CHANGED ===================
        standing_table_entities = [e for e in self.msp.query('INSERT') if "STANDING_TABLE" in e.dxf.name.upper()]

        if standing_table_entities:
            # Get a representative fixture to know the height of the rows to be placed.
            if not fixture_queue:
                # Fallback if the queue is somehow empty
                cursor_y_end = self.cvc.max_y - 50.0
            else:
                representative_fixture = fixture_queue[0]
                # When rotated 90 degrees, the fixture's width becomes its effective height.
                fixture_row_height = representative_fixture.width
                
                standing_tables_bbox = extents(standing_table_entities)
                standing_tables_bottom_y = standing_tables_bbox.extmin.y
                
                # The final visual gap you want to see.
                FINAL_VISUAL_GAP = 1050.0
                
                # Adjust the "Do Not Cross" line to account for the fixture's height AND the gap.
                cursor_y_end = standing_tables_bottom_y - FINAL_VISUAL_GAP - fixture_row_height
                
                print(f"  -> Standing Tables found. Adjusting end point for a fixed {FINAL_VISUAL_GAP}mm gap.")
                print(f"    -> Final placement will stop before y={cursor_y_end:.0f}.")
        else:
            # Fallback to the old logic if no standing tables are present.
            cursor_y_end = self.cvc.max_y - 50.0
            print(f"  -> No Standing Tables found. Using top wall as placement end point at y={cursor_y_end:.0f}.")
        # =================== END OF MODIFICATION ===================




        print(f"  -> Anchoring to QMS Desk. Starting placement at y={cursor_y:.0f}.")

        # --- Helper functions (Unchanged) ---
        def _is_rotated_row_valid(start_x, y, fixtures_in_row, gap):
            current_x_in_row = start_x
            for i, fxtr in enumerate(fixtures_in_row):
                rotated_width, rotated_height = fxtr.height, fxtr.width
                candidate_box = box(current_x_in_row, y, current_x_in_row + rotated_width, y + rotated_height)
                if not self.floorplan_polygon.contains(candidate_box.buffer(-1.0)) or any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                    return False
                if i < len(fixtures_in_row) - 1:
                    current_x_in_row += rotated_width + gap
            return True
        
        def _calculate_dynamic_euro_gap(num_in_stack):
            if num_in_stack <= 1: return 0.0
            elif num_in_stack == 2: return 1000.0
            elif num_in_stack == 3: return 1200.0
            else: return 1200.0
        
        def _find_best_stack_size(local_width, walking_margin, total_euros_in_queue, fixture_obj):
            max_to_try = 3
            for n in range(min(max_to_try, total_euros_in_queue), 0, -1):
                gap = _calculate_dynamic_euro_gap(n)
                required_width = (fixture_obj.height * n) + (gap * (n - 1)) + walking_margin 
                if required_width <= local_width:
                    return n, gap
            return 0, 0

        # --- 3. MAIN PLACEMENT LOOP (Unchanged) ---
        while fixture_queue:
            if cursor_y > cursor_y_end:
                print("    -> ⚠️ Ran out of vertical space. Stopping placement.")
                break

            next_fxtr_obj = fixture_queue[0]
            stack_width = next_fxtr_obj.height
            intersection = self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, cursor_y + (next_fxtr_obj.width / 2)), (self.cvc.max_x + 100, cursor_y + (next_fxtr_obj.width / 2))]))
            if not isinstance(intersection, LineString) or intersection.is_empty:
                cursor_y += 100
                continue
            local_space_bounds = intersection.bounds
            # local_width = local_space_bounds[2] - local_bounds[0]
            local_width = local_space_bounds[2] - local_space_bounds[0]
            local_start_x = local_space_bounds[0]
            walking_space_margin = max(300.0, local_width * 0.50)
            num_to_place, horizontal_gap = 0, 0
            if next_fxtr_obj.name == "Lensbar":
                if next_fxtr_obj.height + walking_space_margin <= local_width:
                    num_to_place = 1
            elif next_fxtr_obj.name == "Euro_centre":
                num_to_place, horizontal_gap = _find_best_stack_size(local_width, walking_space_margin, len(fixture_queue), next_fxtr_obj)
            if num_to_place == 0:
                cursor_y += 100
                continue
            fixtures_for_this_row = [fixture_queue[i] for i in range(num_to_place)]
            total_row_width = (stack_width * num_to_place) + (horizontal_gap * (num_to_place - 1))
            ideal_start_x = local_start_x + (local_width - total_row_width) / 2
            valid_start_x = None
            search_offset = 0
            while valid_start_x is None and search_offset < local_width / 2:
                for sign in [1, -1]:
                    test_x = ideal_start_x + (search_offset * sign) - 5
                    if _is_rotated_row_valid(test_x, cursor_y, fixtures_for_this_row, horizontal_gap):
                        valid_start_x = test_x
                        break
                search_offset += 100
            if valid_start_x is None:
                cursor_y += 100
                continue
            current_x_in_row = valid_start_x
            for i in range(num_to_place):
                fxtr = fixture_queue.popleft()
                rotated_width, rotated_height = fxtr.height, fxtr.width
                target_center_x = current_x_in_row + (rotated_width / 2)
                target_center_y = cursor_y + (rotated_height / 2)
                if self._validate_and_place_at_point(fxtr, Vec2(target_center_x, target_center_y), 90, placed_bboxes):
                    print(f"    -> Placed '{fxtr.name}' at ({current_x_in_row:.0f}, {cursor_y:.0f})")
                else:
                    print(f"    -> ⚠️ Final validation failed for '{fxtr.name}' during placement.")
                current_x_in_row += rotated_width + horizontal_gap
            cursor_y += rotated_height + vertical_row_spacing

        if fixture_queue:
            print(f"\n--- ⚠️ Finished with {len(fixture_queue)} unplaced fixtures ---")
        else:
            print("\n--- ✅ Finished Dynamic Central Fixture Placement ---")



    def calculate_max_euro_capacity(self) -> int:
        """
        Calculates the maximum possible number of Euro_centre fixtures that can fit
        in the designated zone between the QMS desk and the Standing Tables.
        This function is a simulation and does not place any fixtures.
        """
        from Fixture import Fixture
        from shapely.geometry import LineString
        from ezdxf.bbox import extents
        import collections

        print("\n--- 🔬 Simulating Euro Centre Capacity ---")

        # --- 1. Load a representative fixture to get dimensions ---
        try:
            euro_fxtr = Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"])
            # When rotated 90 degrees, the fixture's width becomes its height
            fixture_row_height = euro_fxtr.width 
            vertical_row_spacing = self._calculate_dynamic_vertical_gap_strategy_2()
        except Exception as e:
            print(f"  -> 🔥 Could not load Euro_centre fixture for simulation: {e}")
            return 0

        # --- 2. Define the Vertical Placement Zone ---
        # Find START of zone (above QMS desk)
        qms_entities = [e for e in self.msp.query('INSERT') if "QMS_DESK" in e.dxf.name.upper()]
        if not qms_entities:
            print("  -> ⚠️ Cannot calculate capacity: QMS Desk not found.")
            return 0
        qms_top_y = extents(qms_entities).extmax.y
        start_y = qms_top_y + 50.0

        # Find END of zone (below standing tables)
        standing_table_entities = [e for e in self.msp.query('INSERT') if "STANDING_TABLE" in e.dxf.name.upper()]
        if not standing_table_entities:
            print("  -> ⚠️ Cannot calculate capacity: Standing Tables not found.")
            return 0
        standing_tables_bottom_y = extents(standing_table_entities).extmin.y
        end_y = standing_tables_bottom_y - 1050.0 - fixture_row_height

        print(f"  -> Simulation Zone: y={start_y:.0f} to y={end_y:.0f}")

        if start_y >= end_y:
            print("  -> No vertical space available between QMS and Standing Tables.")
            return 0

        # --- 3. Loop through the zone and count fixtures ---
        total_euro_count = 0
        cursor_y = start_y

        while cursor_y < end_y:
            # Measure local width at the current cursor position
            intersection = self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, cursor_y + (fixture_row_height / 2)), (self.cvc.max_x + 100, cursor_y + (fixture_row_height / 2))]))
            if not isinstance(intersection, LineString) or intersection.is_empty:
                cursor_y += 100 # Nudge up if no valid space
                continue
            
            local_width = intersection.bounds[2] - intersection.bounds[0]
            walking_space_margin = max(300.0, local_width * 0.50)

            def _calculate_dynamic_euro_gap(num_in_stack):
                if num_in_stack <= 1: return 0.0
                elif num_in_stack == 2: return 1000.0
                elif num_in_stack == 3: return 1200.0
                else: return 1200.0
            
            # Calculate how many can fit in this row
            def _find_best_stack_size(local_width, walking_margin, total_euros_in_queue, fixture_obj):
                max_to_try = 3
                for n in range(min(max_to_try, total_euros_in_queue), 0, -1):
                    gap = _calculate_dynamic_euro_gap(n)
                    required_width = (fixture_obj.height * n) + (gap * (n - 1)) + walking_margin 
                    if required_width <= local_width:
                        return n, gap
                return 0, 0
            num_to_place, _ = _find_best_stack_size(local_width, walking_space_margin, 100, euro_fxtr) 
            

            if num_to_place > 0:
                print(f"    -> Row at y={cursor_y:.0f} can fit {num_to_place} Euro(s).")
                total_euro_count += num_to_place
                # Advance the cursor to the next available row position
                cursor_y += fixture_row_height + vertical_row_spacing
            else:
                # If no fixtures fit, nudge the cursor up slightly to check the next spot
                cursor_y += 100

        print(f"\n--- ✅ Simulation Complete ---")
        print(f"--- Maximum Euro Centre Capacity: {total_euro_count} ---")
        return total_euro_count

#---------------------new  test for euro center placement
#---------------------new  test for euro center placement

#---------------------new  test for euro center placement-zero-rotation
#---------------------new  test for euro center placement-zero-rotation

    def place_central_fixtures_from_qms_v2(self, placed_bboxes: List[tuple]) -> None:
        """
        [V2] Places central fixtures anchored to the QMS desk with ZERO rotation.
        - Fixtures are placed in horizontal rows (un-rotated).
        - Vertical gap between rows is fixed at 2000mm.
        - Horizontal gap between fixtures in a row is fixed at 5mm.
        - The placement corridor is still defined between the QMS desk and Standing Tables.
        """
        from Fixture import Fixture
        from shapely.geometry import box, LineString
        import math
        import collections
        from ezdxf.bbox import extents

        print("\n--- 🧠 Placing Central Fixtures Anchored to QMS Desk (V2 - Zero Rotation) ---")

        # --- 1. SETUP & LOAD FIXTURES ---
        vertical_row_spacing = 1200.0  # CHANGED: Fixed vertical gap
        horizontal_gap = 5.0  # CHANGED: Fixed horizontal gap

        config = self.fixtures.get("floor_fixtures", {})
        euro_count = config.get("Euro_centre", 0)
        lensbar_count = config.get("Lensbar", 0)
        if euro_count + lensbar_count == 0:
            return

        fixture_queue = collections.deque()
        try:
            if lensbar_count > 0:
                fixture_queue.extend([Fixture("Lensbar", self.fixture_dict["Lensbar"]["path"])] * lensbar_count)
            if euro_count > 0:
                fixture_queue.extend([Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"])] * euro_count)
        except Exception as e:
            print(f"🔥 FATAL: Could not load a central fixture: {e}")
            return

        # --- 2. DEFINE PLACEMENT ZONE ---
        qms_entities = [e for e in self.msp.query('INSERT') if "QMS_DESK" in e.dxf.name.upper()]
        if not qms_entities:
            print("    -> ⚠️ Could not find a QMS Desk to anchor to. Aborting placement.")
            return

        qms_bbox = extents(qms_entities)
        qms_top_y = qms_bbox.extmax.y
        
        GAP_ABOVE_QMS = 800.0
        cursor_y = qms_top_y + GAP_ABOVE_QMS
        
        standing_table_entities = [e for e in self.msp.query('INSERT') if "STANDING_TABLE" in e.dxf.name.upper()]
        if standing_table_entities:
            representative_fixture = fixture_queue[0]
            # CHANGED: The effective row height is now the fixture's actual height.
            fixture_row_height = representative_fixture.height
            
            standing_tables_bbox = extents(standing_table_entities)
            standing_tables_bottom_y = standing_tables_bbox.extmin.y
            
            FINAL_VISUAL_GAP = 1050.0
            cursor_y_end = standing_tables_bottom_y - FINAL_VISUAL_GAP - fixture_row_height
            
            print(f"  -> Standing Tables found. Adjusting end point for a fixed {FINAL_VISUAL_GAP}mm gap.")
            print(f"    -> Final placement will stop before y={cursor_y_end:.0f}.")
        else:
            cursor_y_end = self.cvc.max_y - 50.0
            print(f"  -> No Standing Tables found. Using top wall as placement end point at y={cursor_y_end:.0f}.")

        print(f"  -> Anchoring to QMS Desk. Starting placement at y={cursor_y:.0f}.")

        # --- Helper functions (adapted for zero rotation) ---
        def _is_row_valid(start_x, y, fixtures_in_row, gap):
            current_x_in_row = start_x
            for i, fxtr in enumerate(fixtures_in_row):
                # CHANGED: Use standard width and height
                width, height = fxtr.width, fxtr.height
                candidate_box = box(current_x_in_row, y, current_x_in_row + width, y + height)
                if not self.floorplan_polygon.contains(candidate_box.buffer(-1.0)) or any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                    return False
                if i < len(fixtures_in_row) - 1:
                    current_x_in_row += width + gap
            return True
        
        def _find_best_row_size(local_width, walking_margin, total_fixtures_in_queue, fixture_obj, gap):
            max_to_try = 5 # Allow more fixtures per row since they are narrower
            for n in range(min(max_to_try, total_fixtures_in_queue), 0, -1):
                # CHANGED: Use standard fixture width for calculation
                required_width = (fixture_obj.width * n) + (gap * (n - 1)) + walking_margin 
                if required_width <= local_width:
                    return n
            return 0

        # --- 3. MAIN PLACEMENT LOOP (adapted for zero rotation) ---
        while fixture_queue:
            if cursor_y > cursor_y_end:
                print("    -> ⚠️ Ran out of vertical space. Stopping placement.")
                break

            next_fxtr_obj = fixture_queue[0]
            # CHANGED: The height of the row is now the fixture's height
            row_height = next_fxtr_obj.height
            intersection = self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, cursor_y + (row_height / 2)), (self.cvc.max_x + 100, cursor_y + (row_height / 2))]))
            
            if not isinstance(intersection, LineString) or intersection.is_empty:
                cursor_y += 100
                continue

            local_space_bounds = intersection.bounds
            local_width = local_space_bounds[2] - local_space_bounds[0]
            local_start_x = local_space_bounds[0]
            walking_space_margin = max(300.0, local_width * 0.70)

            # Determine how many of the same type are available to be placed in a row
            fixture_type = next_fxtr_obj.name
            count_of_same_type = sum(1 for f in fixture_queue if f.name == fixture_type)

            num_to_place = _find_best_row_size(local_width, walking_space_margin, count_of_same_type, next_fxtr_obj, horizontal_gap)

            if num_to_place == 0:
                cursor_y += 100
                continue

            fixtures_for_this_row = [fixture_queue[i] for i in range(num_to_place)]
            total_row_width = (next_fxtr_obj.width * num_to_place) + (horizontal_gap * (num_to_place - 1))
            
            ideal_start_x = local_start_x + (local_width - total_row_width) / 2
            
            valid_start_x = None
            search_offset = 0
            while valid_start_x is None and search_offset < local_width / 2:
                for sign in [1, -1]:
                    test_x = ideal_start_x + (search_offset * sign)
                    if _is_row_valid(test_x, cursor_y, fixtures_for_this_row, horizontal_gap):
                        valid_start_x = test_x
                        break
                search_offset += 100
            
            if valid_start_x is None:
                cursor_y += 100
                continue

            current_x_in_row = valid_start_x
            for i in range(num_to_place):
                fxtr = fixture_queue.popleft()
                # CHANGED: Use standard width and height for placement
                width, height = fxtr.width, fxtr.height
                
                target_center_x = current_x_in_row + (width / 2)
                target_center_y = cursor_y + (height / 2)

                # CHANGED: Use rotation=0
                if self._validate_and_place_at_point(fxtr, Vec2(target_center_x, target_center_y), 0, placed_bboxes):
                    print(f"    -> Placed '{fxtr.name}' at ({current_x_in_row:.0f}, {cursor_y:.0f})")
                else:
                    print(f"    -> ⚠️ Final validation failed for '{fxtr.name}' during placement.")
                
                current_x_in_row += width + horizontal_gap

            # CHANGED: Advance cursor by the row's actual height
            cursor_y += row_height + vertical_row_spacing

        if fixture_queue:
            print(f"\n--- ⚠️ Finished with {len(fixture_queue)} unplaced fixtures ---")
        else:
            print("\n--- ✅ Finished Dynamic Central Fixture Placement (V2) ---")

    def calculate_max_euro_capacity_v2(self) -> int:
        """
        [V2] Calculates the maximum possible number of Euro_centre fixtures based on
        the logic of place_central_fixtures_from_qms_v2() (zero rotation).
        This function is a simulation and does not place any fixtures.
        """
        from Fixture import Fixture
        from shapely.geometry import LineString
        from ezdxf.bbox import extents
        import collections

        print("\n--- 🔬 Simulating Euro Centre Capacity (V2 - Zero Rotation) ---")

        # --- 1. Load a representative fixture to get dimensions ---
        try:
            euro_fxtr = Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"])
            # CHANGED: The row height is the fixture's actual height (no rotation)
            fixture_row_height = euro_fxtr.height
            # CHANGED: The vertical gap is now a fixed value
            vertical_row_spacing = 1200.0
        except Exception as e:
            print(f"  -> 🔥 Could not load Euro_centre fixture for simulation: {e}")
            return 0

        # --- 2. Define the Vertical Placement Zone (Logic remains the same) ---
        qms_entities = [e for e in self.msp.query('INSERT') if "QMS_DESK" in e.dxf.name.upper()]
        if not qms_entities:
            print("  -> ⚠️ Cannot calculate capacity: QMS Desk not found.")
            return 0
        qms_top_y = extents(qms_entities).extmax.y
        start_y = qms_top_y + 800.0

        standing_table_entities = [e for e in self.msp.query('INSERT') if "STANDING_TABLE" in e.dxf.name.upper()]
        if not standing_table_entities:
            print("  -> ⚠️ Cannot calculate capacity: Standing Tables not found.")
            return 0
        standing_tables_bottom_y = extents(standing_table_entities).extmin.y
        # Note: This calculation is correct because fixture_row_height was updated above
        end_y = standing_tables_bottom_y - 1050.0 - fixture_row_height

        print(f"  -> Simulation Zone: y={start_y:.0f} to y={end_y:.0f}")

        if start_y >= end_y:
            print("  -> No vertical space available between QMS and Standing Tables.")
            return 0

        # --- 3. Loop through the zone and count fixtures ---
        total_euro_count = 0
        cursor_y = start_y

        while cursor_y < end_y:
            # Note: This calculation is correct because fixture_row_height was updated
            intersection = self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, cursor_y + (fixture_row_height / 2)), (self.cvc.max_x + 100, cursor_y + (fixture_row_height / 2))]))
            if not isinstance(intersection, LineString) or intersection.is_empty:
                cursor_y += 100
                continue
            
            local_width = intersection.bounds[2] - intersection.bounds[0]
            walking_space_margin = max(300.0, local_width * 0.50)

            # CHANGED: Helper function adapted for zero rotation and fixed gap
            def _find_best_row_size(local_width, walking_margin, total_fixtures_in_queue, fixture_obj):
                max_to_try = 5  # Allow more fixtures per row since they are narrower
                gap = 5.0  # Fixed horizontal gap
                for n in range(min(max_to_try, total_fixtures_in_queue), 0, -1):
                    # Use standard width for calculation
                    required_width = (fixture_obj.width * n) + (gap * (n - 1)) + walking_margin
                    if required_width <= local_width:
                        return n  # Only need to return the count
                return 0
            
            # We pass 100 as a large number for total_fixtures_in_queue to find the absolute max
            num_to_place = _find_best_row_size(local_width, walking_space_margin, 100, euro_fxtr)
            
            if num_to_place > 0:
                print(f"    -> Row at y={cursor_y:.0f} can fit {num_to_place} Euro(s).")
                total_euro_count += num_to_place
                # Advance the cursor using the updated row height and spacing
                cursor_y += fixture_row_height + vertical_row_spacing
            else:
                cursor_y += 100

        print(f"\n--- ✅ Simulation Complete (V2) ---")
        print(f"--- Maximum Euro Centre Capacity (Zero Rotation): {total_euro_count} ---")
        return total_euro_count

#---------------------new  test for euro center placement-zero-rotation
#---------------------new  test for euro center placement-zero-rotation
#---------------------new  test for euro center placement--new_setup of centering
#---------------------new  test for euro center placement--new_setup of centering

    def place_central_fixtures_from_qms_lane_strategy(self, placed_bboxes: List[tuple]) -> None:
        """
        Places central fixtures using an intelligent "lane" strategy.
        - The first row establishes a horizontal "lane".
        - Subsequent rows try to stay in that lane.
        - If a blockage occurs, it finds a new lane and continues from there.
        """
        from Fixture import Fixture
        from shapely.geometry import box, LineString
        import math
        import collections
        from ezdxf.bbox import extents

        print("\n--- 🧠 Placing Central Fixtures with 'Lane' Strategy ---")

        # --- 1. SETUP & LOAD FIXTURES (Unchanged) ---
        vertical_row_spacing = self._calculate_dynamic_vertical_gap_strategy_2()
        config = self.fixtures.get("floor_fixtures", {})
        euro_count = config.get("Euro_centre", 0)
        lensbar_count = config.get("Lensbar", 0)
        if euro_count + lensbar_count == 0:
            return

        fixture_queue = collections.deque()
        try:
            if lensbar_count > 0:
                fixture_queue.extend([Fixture("Lensbar", self.fixture_dict["Lensbar"]["path"])] * lensbar_count)
            if euro_count > 0:
                fixture_queue.extend([Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"])] * euro_count)
        except Exception as e:
            print(f"🔥 FATAL: Could not load a central fixture: {e}")
            return

        # --- 2. DEFINE PLACEMENT ZONE (Unchanged) ---
        qms_entities = [e for e in self.msp.query('INSERT') if "QMS_DESK" in e.dxf.name.upper()]
        if not qms_entities:
            print("    -> ⚠️ Could not find a QMS Desk to anchor to. Aborting placement.")
            return
        qms_bbox = extents(qms_entities)
        qms_top_y = qms_bbox.extmax.y
        GAP_ABOVE_QMS = 800.0
        cursor_y = qms_top_y + GAP_ABOVE_QMS
        
        standing_table_entities = [e for e in self.msp.query('INSERT') if "STANDING_TABLE" in e.dxf.name.upper()]
        if standing_table_entities:
            representative_fixture = fixture_queue[0]
            fixture_row_height = representative_fixture.width
            standing_tables_bbox = extents(standing_table_entities)
            standing_tables_bottom_y = standing_tables_bbox.extmin.y
            FINAL_VISUAL_GAP = 1050.0
            cursor_y_end = standing_tables_bottom_y - FINAL_VISUAL_GAP - fixture_row_height
        else:
            cursor_y_end = self.cvc.max_y - 50.0
        
        # Helper functions (Unchanged)
        def _is_rotated_row_valid(start_x, y, fixtures_in_row, gap):
            current_x_in_row = start_x
            for i, fxtr in enumerate(fixtures_in_row):
                rotated_width, rotated_height = fxtr.height, fxtr.width
                candidate_box = box(current_x_in_row, y, current_x_in_row + rotated_width, y + rotated_height)
                if not self.floorplan_polygon.contains(candidate_box.buffer(-1.0)) or any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                    return False
                if i < len(fixtures_in_row) - 1:
                    current_x_in_row += rotated_width + gap
            return True
        
        def _calculate_dynamic_euro_gap(num_in_stack):
            if num_in_stack <= 1: return 0.0
            elif num_in_stack == 2: return 1000.0
            elif num_in_stack == 3: return 1200.0
            else: return 1200.0
        
        def _find_best_stack_size(local_width, walking_margin, total_euros_in_queue, fixture_obj):
            max_to_try = 3
            for n in range(min(max_to_try, total_euros_in_queue), 0, -1):
                gap = _calculate_dynamic_euro_gap(n)
                required_width = (fixture_obj.height * n) + (gap * (n - 1)) + walking_margin 
                if required_width <= local_width:
                    return n, gap
            return 0, 0
            
        # <<< --- NEW LANE LOGIC START --- >>>
        lane_start_x = None  # This will store the X-coordinate of our current lane
        # <<< --- NEW LANE LOGIC END --- >>>

        # --- 3. MAIN PLACEMENT LOOP ---
        while fixture_queue:
            if cursor_y > cursor_y_end:
                print("    -> ⚠️ Ran out of vertical space. Stopping placement.")
                break

            # (The logic to determine num_to_place, gaps, etc. is unchanged)
            next_fxtr_obj = fixture_queue[0]
            stack_width = next_fxtr_obj.height
            intersection = self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, cursor_y + (next_fxtr_obj.width / 2)), (self.cvc.max_x + 100, cursor_y + (next_fxtr_obj.width / 2))]))
            if not isinstance(intersection, LineString) or intersection.is_empty:
                cursor_y += 100; continue
            local_space_bounds = intersection.bounds
            local_width = local_space_bounds[2] - local_space_bounds[0]
            local_start_x = local_space_bounds[0]
            walking_space_margin = max(300.0, local_width * 0.50)
            num_to_place, horizontal_gap = 0, 0
            if next_fxtr_obj.name == "Lensbar":
                if next_fxtr_obj.height + walking_space_margin <= local_width: num_to_place = 1
            elif next_fxtr_obj.name == "Euro_centre":
                num_to_place, horizontal_gap = _find_best_stack_size(local_width, walking_space_margin, len(fixture_queue), next_fxtr_obj)
            if num_to_place == 0:
                cursor_y += 100; continue
            
            fixtures_for_this_row = [fixture_queue[i] for i in range(num_to_place)]
            total_row_width = (stack_width * num_to_place) + (horizontal_gap * (num_to_place - 1))
            
            # <<< --- MODIFIED CENTERING & PLACEMENT LOGIC START --- >>>
            valid_start_x = None

            if lane_start_x is None:
                # This is the FIRST row. Find the initial lane using the resilient search.
                print("    -> Establishing initial placement lane...")
                ideal_start_x = local_start_x + (local_width - total_row_width) / 2
                search_offset = 0
                while valid_start_x is None and search_offset < local_width / 2:
                    for sign in [1, -1]:
                        test_x = ideal_start_x + (search_offset * sign)
                        if _is_rotated_row_valid(test_x, cursor_y, fixtures_for_this_row, horizontal_gap):
                            valid_start_x = test_x
                            lane_start_x = valid_start_x  # << SET THE LANE!
                            print(f"    -> Initial lane established at x={lane_start_x:.0f}")
                            break
                    search_offset += 100
            else:
                # For SUBSEQUENT rows, first try to stay in the established lane.
                if _is_rotated_row_valid(lane_start_x, cursor_y, fixtures_for_this_row, horizontal_gap):
                    valid_start_x = lane_start_x # Success! Stay in the lane.
                else:
                    # BLOCKAGE! The current lane is blocked. Find a new one.
                    print(f"    -> ⚠️ Blockage detected at x={lane_start_x:.0f}! Searching for a new lane...")
                    ideal_start_x = local_start_x + (local_width - total_row_width) / 2
                    search_offset = 0
                    while valid_start_x is None and search_offset < local_width / 2:
                        for sign in [1, -1]:
                            test_x = ideal_start_x + (search_offset * sign)
                            if _is_rotated_row_valid(test_x, cursor_y, fixtures_for_this_row, horizontal_gap):
                                valid_start_x = test_x
                                lane_start_x = valid_start_x  # << SET THE NEW LANE!
                                print(f"    -> New lane established at x={lane_start_x:.0f}")
                                break
                        search_offset += 100
            
            # --- This part is the final execution, which remains the same ---
            if valid_start_x is None:
                print(f"    -> ⚠️ Could not find any valid horizontal spot for the row. Skipping.")
                cursor_y += 100
                continue

            current_x_in_row = valid_start_x
            for i in range(num_to_place):
                fxtr = fixture_queue.popleft()
                rotated_width, rotated_height = fxtr.height, fxtr.width
                target_center_x = current_x_in_row + (rotated_width / 2)
                target_center_y = cursor_y + (rotated_height / 2)
                if self._validate_and_place_at_point(fxtr, Vec2(target_center_x, target_center_y), 90, placed_bboxes):
                    print(f"    -> Placed '{fxtr.name}' at ({current_x_in_row:.0f}, {cursor_y:.0f})")
                else:
                    print(f"    -> ⚠️ Final validation failed for '{fxtr.name}' during placement.")
                current_x_in_row += rotated_width + horizontal_gap
            
            cursor_y += rotated_height + vertical_row_spacing
            # <<< --- MODIFIED CENTERING & PLACEMENT LOGIC END --- >>>

        if fixture_queue:
            print(f"\n--- ⚠️ Finished with {len(fixture_queue)} unplaced fixtures ---")
        else:
            print("\n--- ✅ Finished Dynamic Central Fixture Placement ('Lane' Strategy) ---")

    def place_central_fixtures_from_qms_v1_og(self, placed_bboxes: List[tuple]) -> None:
        """
        [V2] Places central fixtures using an advanced "lane" strategy.
        - Re-centers and establishes a new lane WHENEVER the optimal number
          of fixtures per row changes, or when a hard blockage is hit.
        """
        from Fixture import Fixture
        from shapely.geometry import box, LineString
        import math
        import collections
        from ezdxf.bbox import extents

        print("\n--- 🧠 Placing Central Fixtures with Advanced 'Lane' Strategy (V2) ---")

        # --- 1. SETUP & LOAD FIXTURES (Unchanged) ---
        # (This section is identical to the previous version)
        vertical_row_spacing = self._calculate_dynamic_vertical_gap_strategy_2()
        config = self.fixtures.get("floor_fixtures", {})
        euro_count = config.get("Euro_centre", 0)
        lensbar_count = config.get("Lensbar", 0)
        if euro_count + lensbar_count == 0:
            return
        fixture_queue = collections.deque()
        try:
            if lensbar_count > 0:
                fixture_queue.extend([Fixture("Lensbar", self.fixture_dict["Lensbar"]["path"])] * lensbar_count)
            if euro_count > 0:
                fixture_queue.extend([Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"])] * euro_count)
        except Exception as e:
            print(f"🔥 FATAL: Could not load a central fixture: {e}"); return

        # --- 2. DEFINE PLACEMENT ZONE (Unchanged) ---
        # (This section is identical to the previous version)
        qms_entities = [e for e in self.msp.query('INSERT') if "QMS_DESK" in e.dxf.name.upper()]
        if not qms_entities:
            print("    -> ⚠️ Could not find a QMS Desk to anchor to. Aborting placement."); return
        qms_bbox = extents(qms_entities)
        qms_top_y = qms_bbox.extmax.y
        GAP_ABOVE_QMS = 50.0
        cursor_y = qms_top_y + GAP_ABOVE_QMS
        standing_table_entities = [e for e in self.msp.query('INSERT') if "STANDING_TABLE" in e.dxf.name.upper()]
        if standing_table_entities:
            representative_fixture = fixture_queue[0]
            fixture_row_height = representative_fixture.width
            standing_tables_bbox = extents(standing_table_entities)
            standing_tables_bottom_y = standing_tables_bbox.extmin.y
            FINAL_VISUAL_GAP = 1050.0
            cursor_y_end = standing_tables_bottom_y - FINAL_VISUAL_GAP - fixture_row_height
        else:
            cursor_y_end = self.cvc.max_y - 50.0
        
        # Helper functions (Unchanged)
        def _is_rotated_row_valid(start_x, y, fixtures_in_row, gap):
            current_x_in_row = start_x
            for i, fxtr in enumerate(fixtures_in_row):
                rotated_width, rotated_height = fxtr.height, fxtr.width
                candidate_box = box(current_x_in_row, y, current_x_in_row + rotated_width, y + rotated_height)
                if not self.floorplan_polygon.contains(candidate_box.buffer(-1.0)) or any(candidate_box.intersects(box(*b)) for b in placed_bboxes): return False
                if i < len(fixtures_in_row) - 1: current_x_in_row += rotated_width + gap
            return True
        def _calculate_dynamic_euro_gap(num_in_stack):
            if num_in_stack <= 1: return 0.0
            elif num_in_stack == 2: return 1000.0
            elif num_in_stack == 3: return 1200.0
            else: return 1200.0
        def _find_best_stack_size(local_width, walking_margin, total_euros_in_queue, fixture_obj):
            max_to_try = 3
            for n in range(min(max_to_try, total_euros_in_queue), 0, -1):
                gap = _calculate_dynamic_euro_gap(n)
                required_width = (fixture_obj.height * n) + (gap * (n - 1)) + walking_margin 
                if required_width <= local_width: return n, gap
            return 0, 0
            
        # <<< --- NEW STATE VARIABLES --- >>>
        lane_start_x = None
        lane_fixture_count = 0 # Track the number of fixtures the lane is based on
        # <<< --- END NEW STATE VARIABLES --- >>>

        # --- 3. MAIN PLACEMENT LOOP ---
        while fixture_queue:
            if cursor_y > cursor_y_end:
                print("    -> ⚠️ Ran out of vertical space. Stopping placement."); break

            # (Logic to determine num_to_place is unchanged)
            next_fxtr_obj = fixture_queue[0]
            stack_width = next_fxtr_obj.height
            intersection = self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, cursor_y + (next_fxtr_obj.width / 2)), (self.cvc.max_x + 100, cursor_y + (next_fxtr_obj.width / 2))]))
            if not isinstance(intersection, LineString) or intersection.is_empty:
                cursor_y += 100; continue
            local_space_bounds = intersection.bounds
            local_width = local_space_bounds[2] - local_space_bounds[0]
            local_start_x = local_space_bounds[0]
            walking_space_margin = max(300.0, local_width * 0.50)
            num_to_place, horizontal_gap = 0, 0
            if next_fxtr_obj.name == "Lensbar":
                if next_fxtr_obj.height + walking_space_margin <= local_width: num_to_place = 1
            elif next_fxtr_obj.name == "Euro_centre":
                num_to_place, horizontal_gap = _find_best_stack_size(local_width, walking_space_margin, len(fixture_queue), next_fxtr_obj)
            if num_to_place == 0:
                cursor_y += 100; continue
            
            fixtures_for_this_row = [fixture_queue[i] for i in range(num_to_place)]
            total_row_width = (stack_width * num_to_place) + (horizontal_gap * (num_to_place - 1))
            
            # <<< --- V2: MODIFIED RE-CENTERING TRIGGER --- >>>
            valid_start_x = None

            # This condition now triggers for the first row OR if the row size changes.
            if lane_start_x is None or num_to_place != lane_fixture_count:
                if lane_start_x is not None: # This means the row size changed
                    print(f"    -> Row size changed from {lane_fixture_count} to {num_to_place}. Re-centering and establishing new lane...")
                else: # This is the first row
                    print("    -> Establishing initial placement lane...")

                # Perform the full resilient search to find the best center for the NEW group size.
                ideal_start_x = local_start_x + (local_width - total_row_width) / 2
                search_offset = 0
                while valid_start_x is None and search_offset < local_width / 2:
                    for sign in [1, -1]:
                        test_x = ideal_start_x + (search_offset * sign)
                        if _is_rotated_row_valid(test_x, cursor_y, fixtures_for_this_row, horizontal_gap):
                            valid_start_x = test_x
                            lane_start_x = valid_start_x       # Set the new lane X
                            lane_fixture_count = num_to_place  # Set the new lane count
                            print(f"    -> New lane for {lane_fixture_count} fixture(s) established at x={lane_start_x:.0f}")
                            break
                    if valid_start_x is not None: break
                    search_offset += 100
            else:
                # Row size is the same, so try to stay in the established lane.
                if _is_rotated_row_valid(lane_start_x, cursor_y, fixtures_for_this_row, horizontal_gap):
                    valid_start_x = lane_start_x # Success! Stay in the lane.
                else:
                    # BLOCKAGE! The lane is blocked even with the same number of fixtures.
                    print(f"    -> ⚠️ Blockage detected in lane at x={lane_start_x:.0f}! Searching for a new lane...")
                    ideal_start_x = local_start_x + (local_width - total_row_width) / 2
                    search_offset = 0
                    while valid_start_x is None and search_offset < local_width / 2:
                        for sign in [1, -1]:
                            test_x = ideal_start_x + (search_offset * sign)
                            if _is_rotated_row_valid(test_x, cursor_y, fixtures_for_this_row, horizontal_gap):
                                valid_start_x = test_x
                                lane_start_x = valid_start_x       # Set the new lane X
                                # lane_fixture_count is already correct
                                print(f"    -> New lane for {lane_fixture_count} fixture(s) established at x={lane_start_x:.0f}")
                                break
                        if valid_start_x is not None: break
                        search_offset += 100
            
            # --- Final Execution (Unchanged) ---
            if valid_start_x is None:
                print(f"    -> ⚠️ Could not find any valid horizontal spot for the row. Skipping."); cursor_y += 100; continue

            current_x_in_row = valid_start_x
            for i in range(num_to_place):
                fxtr = fixture_queue.popleft()
                rotated_width, rotated_height = fxtr.height, fxtr.width
                target_center_x = current_x_in_row + (rotated_width / 2)
                target_center_y = cursor_y + (rotated_height / 2)
                if self._validate_and_place_at_point(fxtr, Vec2(target_center_x, target_center_y), 90, placed_bboxes):
                    print(f"    -> Placed '{fxtr.name}' at ({current_x_in_row:.0f}, {cursor_y:.0f})")
                else:
                    print(f"    -> ⚠️ Final validation failed for '{fxtr.name}' during placement.")
                current_x_in_row += rotated_width + horizontal_gap
            
            cursor_y += rotated_height + vertical_row_spacing

        if fixture_queue:
            print(f"\n--- ⚠️ Finished with {len(fixture_queue)} unplaced fixtures ---")


        else:
            print("\n--- ✅ Finished Dynamic Central Fixture Placement ('Advanced Lane' Strategy V2) ---")

    def place_central_fixtures_from_qms_v1(self, placed_bboxes: List[tuple]) -> None:
        """
        [V3] Places central fixtures using a continuous "lane" strategy.
        - Grants placement "privilege" to ignore standing tables when the cursor is in their zone.
        """
        from Fixture import Fixture
        from shapely.geometry import box, LineString
        import math
        import collections
        from ezdxf.bbox import extents

        print("\n--- 🧠 Placing Central Fixtures with Continuous Lane Strategy (V1 - Rotated) ---")

        # --- 1. SETUP & LOAD FIXTURES ---
        vertical_row_spacing = self._calculate_dynamic_vertical_gap_strategy_2()
        config = self.fixtures.get("floor_fixtures", {})
        fixture_queue = collections.deque([
            Fixture(name, self.fixture_dict[name]["path"])
            for name, count in config.items() if count > 0 for _ in range(count)
        ])
        if not fixture_queue: return

        # --- 2. DEFINE PLACEMENT ZONE & BOUNDARIES ---
        qms_entities = [e for e in self.msp.query('INSERT') if "QMS_DESK" in e.dxf.name.upper()]
        if not qms_entities:
            print("    -> ⚠️ Could not find QMS Desk to anchor. Aborting."); return
        cursor_y = extents(qms_entities).extmax.y + 50.0

        separator_line = self.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
        cursor_y_end = separator_line.dxf.start.y - 1050.0 if separator_line else self.cvc.max_y - 50.0
        
        # --- 3. SETUP THE "PRIVILEGE ZONE" ---
        standing_table_entities = [e for e in self.msp.query('INSERT') if "STANDING_TABLE" in e.dxf.name.upper()]
        fallback_obstacles = list(placed_bboxes)
        standing_tables_bbox = None
        if standing_table_entities:
            standing_tables_bbox = extents(standing_table_entities)
            standing_table_bboxes_to_ignore = [(b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y) for e in standing_table_entities if (b := extents([e]))]
            fallback_obstacles = [b for b in placed_bboxes if b not in standing_table_bboxes_to_ignore]
            print(f"  -> Standing tables detected. Will grant placement privilege between y={standing_tables_bbox.extmin.y:.0f} and y={standing_tables_bbox.extmax.y:.0f}.")

        # --- 4. HELPERS ---
        def _is_rotated_row_valid(start_x, y, fixtures_in_row, gap, obstacles_to_check):
            current_x_in_row = start_x
            for i, fxtr in enumerate(fixtures_in_row):
                rotated_width, rotated_height = fxtr.height, fxtr.width
                candidate_box = box(current_x_in_row, y, current_x_in_row + rotated_width, y + rotated_height)
                if not self.floorplan_polygon.contains(candidate_box.buffer(-1.0)) or any(candidate_box.intersects(box(*b)) for b in obstacles_to_check): return False
                if i < len(fixtures_in_row) - 1: current_x_in_row += rotated_width + gap
            return True

        def _calculate_dynamic_euro_gap(num_in_stack):
            if num_in_stack <= 1: return 0.0
            elif num_in_stack == 2: return 1000.0
            else: return 1200.0

        def _find_best_stack_size(local_width, walking_margin, total_euros, fxtr_obj):
            max_to_try = 3
            for n in range(min(max_to_try, total_euros), 0, -1):
                gap = _calculate_dynamic_euro_gap(n)
                required = (fxtr_obj.height * n) + (gap * (n - 1)) + walking_margin
                if required <= local_width: return n, gap
            return 0, 0

        lane_start_x, lane_fixture_count = None, 0

        # --- 5. UNIFIED PLACEMENT LOOP ---
        while fixture_queue:
            fixture_row_height = fixture_queue[0].width
            if cursor_y > (cursor_y_end - fixture_row_height):
                print("    -> ⚠️ Ran out of vertical space. Stopping placement."); break

            # DYNAMICALLY CHOOSE OBSTACLE LIST
            active_obstacles = placed_bboxes
            if standing_tables_bbox and standing_tables_bbox.extmin.y <= cursor_y <= standing_tables_bbox.extmax.y:
                active_obstacles = fallback_obstacles
            
            # (Rest of the loop logic is the same, but uses active_obstacles)
            next_fxtr_obj = fixture_queue[0]
            stack_width = next_fxtr_obj.height
            intersection = self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, cursor_y + (next_fxtr_obj.width/2)), (self.cvc.max_x + 100, cursor_y + (next_fxtr_obj.width/2))]))
            if not isinstance(intersection, LineString) or intersection.is_empty:
                cursor_y += 100; continue
            local_bounds = intersection.bounds
            local_width, local_start_x = local_bounds[2] - local_bounds[0], local_bounds[0]
            walking_margin = max(300.0, local_width * 0.50)
            num_to_place, h_gap = 0, 0
            if next_fxtr_obj.name == "Lensbar":
                if next_fxtr_obj.height + walking_margin <= local_width: num_to_place = 1
            else:
                num_to_place, h_gap = _find_best_stack_size(local_width, walking_margin, len(fixture_queue), next_fxtr_obj)
            if num_to_place == 0:
                cursor_y += 100; continue
                
            fixtures_for_row = [fixture_queue[i] for i in range(num_to_place)]
            total_row_width = (stack_width * num_to_place) + (h_gap * (num_to_place - 1))
            
            valid_start_x = None
            if lane_start_x is None or num_to_place != lane_fixture_count:
                if lane_start_x: print(f"    -> Row size changed. Re-centering...")
                else: print("    -> Establishing initial placement lane...")
                ideal_x = local_start_x + (local_width - total_row_width) / 2
                offset = 0
                while valid_start_x is None and offset < local_width / 2:
                    for sign in [1, -1]:
                        test_x = ideal_x + (offset * sign)
                        if _is_rotated_row_valid(test_x, cursor_y, fixtures_for_row, h_gap, active_obstacles):
                            valid_start_x = test_x; lane_start_x = valid_start_x; lane_fixture_count = num_to_place
                            print(f"    -> New lane for {lane_fixture_count} fixture(s) established at x={lane_start_x:.0f}"); break
                    if valid_start_x: break
                    offset += 100
            else:
                if _is_rotated_row_valid(lane_start_x, cursor_y, fixtures_for_row, h_gap, active_obstacles):
                    valid_start_x = lane_start_x
                else:
                    print(f"    -> ⚠️ Blockage in lane! Searching for new lane..."); ideal_x = local_start_x + (local_width - total_row_width) / 2; offset = 0
                    while valid_start_x is None and offset < local_width / 2:
                        for sign in [1, -1]:
                            test_x = ideal_x + (offset * sign)
                            if _is_rotated_row_valid(test_x, cursor_y, fixtures_for_row, h_gap, active_obstacles):
                                valid_start_x = test_x; lane_start_x = valid_start_x
                                print(f"    -> New lane established at x={lane_start_x:.0f}"); break
                        if valid_start_x: break
                        offset += 100
            
            if valid_start_x is None:
                cursor_y += 100; continue
                
            current_x = valid_start_x
            for _ in range(num_to_place):
                fxtr = fixture_queue.popleft()
                rw, rh = fxtr.height, fxtr.width
                center_x, center_y = current_x + (rw / 2), cursor_y + (rh / 2)
                if self._validate_and_place_at_point(fxtr, Vec2(center_x, center_y), 90, placed_bboxes):
                    print(f"    -> Placed '{fxtr.name}' at ({current_x:.0f}, {cursor_y:.0f})")
                else:
                    print(f"    -> ⚠️ Final validation failed for '{fxtr.name}'.")
                current_x += rw + h_gap
            cursor_y += rh + vertical_row_spacing

        if fixture_queue:
            print(f"\n--- ⚠️ Finished with {len(fixture_queue)} unplaced fixtures. ---")
        else:
            print("\n--- ✅ All central fixtures placed successfully. ---")
            
    def place_central_fixtures_from_qms_v2_(self, placed_bboxes: List[tuple]) -> None:
        """
        [LANE STRATEGY V3] Places central fixtures with ZERO rotation,
        using a continuous lane strategy that has privilege to place over standing tables.
        """
        from Fixture import Fixture
        from shapely.geometry import box, LineString
        import math
        import collections
        from ezdxf.bbox import extents

        print("\n--- 🧠 Placing Central Fixtures (V2 - Zero Rotation) with Continuous Lane Strategy ---")
        
        # (Setup and Main Placement Loop remain the same)
        vertical_row_spacing = 1200.0; horizontal_gap = 5.0
        config = self.fixtures.get("floor_fixtures", {});
        fixture_queue = collections.deque([Fixture(n, self.fixture_dict[n]["path"]) for n, c in config.items() if c > 0 for _ in range(c)])
        if not fixture_queue: return
        qms_entities = [e for e in self.msp.query('INSERT') if "QMS_DESK" in e.dxf.name.upper()]
        if not qms_entities: print("    -> ⚠️ Could not find QMS Desk to anchor. Aborting."); return
        cursor_y = extents(qms_entities).extmax.y + 800.0
        separator_line = self.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
        cursor_y_end = separator_line.dxf.start.y - 1050.0 if separator_line else self.cvc.max_y - 50.0

        # SETUP THE "PRIVILEGE ZONE"
        standing_table_entities = [e for e in self.msp.query('INSERT') if "STANDING_TABLE" in e.dxf.name.upper()]
        fallback_obstacles = list(placed_bboxes)
        standing_tables_bbox = None
        if standing_table_entities:
            standing_tables_bbox = extents(standing_table_entities)
            standing_table_bboxes_to_ignore = [(b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y) for e in standing_table_entities if (b := extents([e]))]
            fallback_obstacles = [b for b in placed_bboxes if b not in standing_table_bboxes_to_ignore]
            print(f"  -> Standing tables detected. Will grant placement privilege between y={standing_tables_bbox.extmin.y:.0f} and y={standing_tables_bbox.extmax.y:.0f}.")
        
        # HELPERS
        def _is_row_valid(start_x, y, fixtures_in_row, gap, obstacles_to_check):
            current_x = start_x
            for i, fxtr in enumerate(fixtures_in_row):
                w, h = fxtr.width, fxtr.height
                cb = box(current_x, y, current_x + w, y + h)
                if not self.floorplan_polygon.contains(cb.buffer(-1.0)) or any(cb.intersects(box(*b)) for b in obstacles_to_check): return False
                if i < len(fixtures_in_row) - 1: current_x += w + gap
            return True
        def _find_best_row_size(local_width, walking_margin, total_fixtures, fxtr_obj, gap):
            max_to_try = 5
            for n in range(min(max_to_try, total_fixtures), 0, -1):
                if (fxtr_obj.width * n) + (gap * (n - 1)) + walking_margin <= local_width: return n
            return 0

        lane_start_x, lane_fixture_count = None, 0
        while fixture_queue:
            row_height = fixture_queue[0].height
            if cursor_y > (cursor_y_end - row_height):
                print("    -> ⚠️ Ran out of vertical space."); break
            
            active_obstacles = placed_bboxes
            if standing_tables_bbox and standing_tables_bbox.extmin.y <= cursor_y <= standing_tables_bbox.extmax.y:
                active_obstacles = fallback_obstacles
            
            intersection = self.floorplan_polygon.intersection(LineString([(self.cvc.min_x-100, cursor_y + (row_height/2)), (self.cvc.max_x+100, cursor_y + (row_height/2))]))
            if not isinstance(intersection, LineString) or intersection.is_empty:
                cursor_y += 100; continue
            local_bounds = intersection.bounds
            local_width, local_start_x = local_bounds[2] - local_bounds[0], local_bounds[0]
            walking_margin = max(300.0, local_width * 0.70)
            next_fxtr_obj = fixture_queue[0]
            count_of_same_type = sum(1 for f in fixture_queue if f.name == next_fxtr_obj.name)
            num_to_place = _find_best_row_size(local_width, walking_margin, count_of_same_type, next_fxtr_obj, horizontal_gap)
            if num_to_place == 0:
                cursor_y += 100; continue
                
            fixtures_for_row = [fixture_queue[i] for i in range(num_to_place)]
            total_row_width = (next_fxtr_obj.width * num_to_place) + (horizontal_gap * (num_to_place - 1))
            
            valid_start_x = None
            if lane_start_x is None or num_to_place != lane_fixture_count:
                if lane_start_x: print(f"    -> Row size changed. Re-centering...")
                else: print("    -> Establishing initial placement lane...")
                ideal_x = local_start_x + (local_width - total_row_width) / 2; offset = 0
                while valid_start_x is None and offset < local_width / 2:
                    for sign in [1, -1]:
                        test_x = ideal_x + (offset * sign)
                        if _is_row_valid(test_x, cursor_y, fixtures_for_row, horizontal_gap, active_obstacles):
                            valid_start_x = test_x; lane_start_x = valid_start_x; lane_fixture_count = num_to_place
                            print(f"    -> New lane for {lane_fixture_count} fixture(s) established at x={lane_start_x:.0f}"); break
                    if valid_start_x: break
                    offset += 100
            else:
                if _is_row_valid(lane_start_x, cursor_y, fixtures_for_row, horizontal_gap, active_obstacles):
                    valid_start_x = lane_start_x
                else:
                    print(f"    -> ⚠️ Blockage in lane! Searching for new lane..."); ideal_x = local_start_x + (local_width - total_row_width) / 2; offset = 0
                    while valid_start_x is None and offset < local_width / 2:
                        for sign in [1, -1]:
                            test_x = ideal_x + (offset * sign)
                            if _is_row_valid(test_x, cursor_y, fixtures_for_row, horizontal_gap, active_obstacles):
                                valid_start_x = test_x; lane_start_x = valid_start_x
                                print(f"    -> New lane established at x={lane_start_x:.0f}"); break
                        if valid_start_x: break
                        offset += 100
            if valid_start_x is None:
                cursor_y += 100; continue
            
            current_x = valid_start_x
            for _ in range(num_to_place):
                fxtr = fixture_queue.popleft()
                w, h = fxtr.width, fxtr.height
                center_x, center_y = current_x + (w / 2), cursor_y + (h / 2)
                if self._validate_and_place_at_point(fxtr, Vec2(center_x, center_y), 0, placed_bboxes):
                    print(f"    -> Placed '{fxtr.name}' at ({current_x:.0f}, {cursor_y:.0f})")
                else:
                    print(f"    -> ⚠️ Final validation failed for '{fxtr.name}'.")
                current_x += w + horizontal_gap
            cursor_y += row_height + vertical_row_spacing

        if fixture_queue:
            print(f"\n--- ⚠️ Finished with {len(fixture_queue)} unplaced fixtures. ---")
        else:
            print("\n--- ✅ All central fixtures placed successfully. ---")


    def place_central_fixtures_from_qms_v2_og(self, placed_bboxes: List[tuple]) -> None:
        """
        [LANE STRATEGY FOR V2] Places central fixtures with ZERO rotation,
        using the advanced lane strategy to re-center only when the row size
        changes or a blockage is hit.
        """
        from Fixture import Fixture
        from shapely.geometry import box, LineString
        import math
        import collections
        from ezdxf.bbox import extents

        print("\n--- 🧠 Placing Central Fixtures (V2 - Zero Rotation) with Advanced 'Lane' Strategy ---")

        # --- 1. SETUP & LOAD FIXTURES (from v2) ---
        vertical_row_spacing = 1200#2000.0
        horizontal_gap = 5.0

        config = self.fixtures.get("floor_fixtures", {})
        euro_count = config.get("Euro_centre", 0)
        lensbar_count = config.get("Lensbar", 0)
        if euro_count + lensbar_count == 0:
            return

        fixture_queue = collections.deque()
        try:
            if lensbar_count > 0:
                fixture_queue.extend([Fixture("Lensbar", self.fixture_dict["Lensbar"]["path"])] * lensbar_count)
            if euro_count > 0:
                fixture_queue.extend([Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"])] * euro_count)
        except Exception as e:
            print(f"🔥 FATAL: Could not load a central fixture: {e}")
            return

        # --- 2. DEFINE PLACEMENT ZONE (from v2) ---
        qms_entities = [e for e in self.msp.query('INSERT') if "QMS_DESK" in e.dxf.name.upper()]
        if not qms_entities:
            print("    -> ⚠️ Could not find a QMS Desk to anchor to. Aborting placement.")
            return

        qms_bbox = extents(qms_entities)
        qms_top_y = qms_bbox.extmax.y
        GAP_ABOVE_QMS = 800.0
        cursor_y = qms_top_y + GAP_ABOVE_QMS
        
        standing_table_entities = [e for e in self.msp.query('INSERT') if "STANDING_TABLE" in e.dxf.name.upper()]
        if standing_table_entities:
            representative_fixture = fixture_queue[0]
            fixture_row_height = representative_fixture.height # Using un-rotated height
            
            standing_tables_bbox = extents(standing_table_entities)
            standing_tables_bottom_y = standing_tables_bbox.extmin.y
            
            FINAL_VISUAL_GAP = 1050.0
            cursor_y_end = standing_tables_bottom_y - FINAL_VISUAL_GAP - fixture_row_height
        else:
            cursor_y_end = self.cvc.max_y - 50.0

        # --- Helper functions (adapted for zero rotation) ---
        def _is_row_valid(start_x, y, fixtures_in_row, gap):
            current_x_in_row = start_x
            for i, fxtr in enumerate(fixtures_in_row):
                width, height = fxtr.width, fxtr.height
                candidate_box = box(current_x_in_row, y, current_x_in_row + width, y + height)
                if not self.floorplan_polygon.contains(candidate_box.buffer(-1.0)) or any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                    return False
                if i < len(fixtures_in_row) - 1:
                    current_x_in_row += width + gap
            return True
        
        def _find_best_row_size(local_width, walking_margin, total_fixtures_in_queue, fixture_obj, gap):
            max_to_try = 5
            for n in range(min(max_to_try, total_fixtures_in_queue), 0, -1):
                required_width = (fixture_obj.width * n) + (gap * (n - 1)) + walking_margin 
                if required_width <= local_width:
                    return n
            return 0

        # <<< --- NEW STATE VARIABLES (from lane_strategy_v2) --- >>>
        lane_start_x = None
        lane_fixture_count = 0
        # <<< --- END NEW STATE VARIABLES --- >>>

        # --- 3. MAIN PLACEMENT LOOP ---
        while fixture_queue:
            if cursor_y > cursor_y_end:
                print("    -> ⚠️ Ran out of vertical space. Stopping placement.")
                break

            next_fxtr_obj = fixture_queue[0]
            row_height = next_fxtr_obj.height
            intersection = self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, cursor_y + (row_height / 2)), (self.cvc.max_x + 100, cursor_y + (row_height / 2))]))
            
            if not isinstance(intersection, LineString) or intersection.is_empty:
                cursor_y += 100
                continue

            local_space_bounds = intersection.bounds
            local_width = local_space_bounds[2] - local_space_bounds[0]
            local_start_x = local_space_bounds[0]
            walking_space_margin = max(300.0, local_width * 0.70)
            fixture_type = next_fxtr_obj.name
            count_of_same_type = sum(1 for f in fixture_queue if f.name == fixture_type)
            num_to_place = _find_best_row_size(local_width, walking_space_margin, count_of_same_type, next_fxtr_obj, horizontal_gap)

            if num_to_place == 0:
                cursor_y += 100
                continue

            fixtures_for_this_row = [fixture_queue[i] for i in range(num_to_place)]
            total_row_width = (next_fxtr_obj.width * num_to_place) + (horizontal_gap * (num_to_place - 1))
            
            # <<< --- MODIFIED RE-CENTERING TRIGGER (from lane_strategy_v2) --- >>>
            valid_start_x = None
            if lane_start_x is None or num_to_place != lane_fixture_count:
                if lane_start_x is not None:
                    print(f"    -> Row size changed from {lane_fixture_count} to {num_to_place}. Re-centering and establishing new lane...")
                else:
                    print("    -> Establishing initial placement lane...")
                
                ideal_start_x = local_start_x + (local_width - total_row_width) / 2
                search_offset = 0
                while valid_start_x is None and search_offset < local_width / 2:
                    for sign in [1, -1]:
                        test_x = ideal_start_x + (search_offset * sign)
                        if _is_row_valid(test_x, cursor_y, fixtures_for_this_row, horizontal_gap):
                            valid_start_x = test_x
                            lane_start_x = valid_start_x
                            lane_fixture_count = num_to_place
                            print(f"    -> New lane for {lane_fixture_count} fixture(s) established at x={lane_start_x:.0f}")
                            break
                    if valid_start_x is not None: break
                    search_offset += 100
            else:
                if _is_row_valid(lane_start_x, cursor_y, fixtures_for_this_row, horizontal_gap):
                    valid_start_x = lane_start_x
                else:
                    print(f"    -> ⚠️ Blockage detected in lane at x={lane_start_x:.0f}! Searching for a new lane...")
                    ideal_start_x = local_start_x + (local_width - total_row_width) / 2
                    search_offset = 0
                    while valid_start_x is None and search_offset < local_width / 2:
                        for sign in [1, -1]:
                            test_x = ideal_start_x + (search_offset * sign)
                            if _is_row_valid(test_x, cursor_y, fixtures_for_this_row, horizontal_gap):
                                valid_start_x = test_x
                                lane_start_x = valid_start_x
                                print(f"    -> New lane for {lane_fixture_count} fixture(s) established at x={lane_start_x:.0f}")
                                break
                        if valid_start_x is not None: break
                        search_offset += 100
            
            # --- Final Execution ---
            if valid_start_x is None:
                cursor_y += 100
                continue

            current_x_in_row = valid_start_x
            for i in range(num_to_place):
                fxtr = fixture_queue.popleft()
                width, height = fxtr.width, fxtr.height
                target_center_x = current_x_in_row + (width / 2)
                target_center_y = cursor_y + (height / 2)
                if self._validate_and_place_at_point(fxtr, Vec2(target_center_x, target_center_y), 0, placed_bboxes):
                    print(f"    -> Placed '{fxtr.name}' at ({current_x_in_row:.0f}, {cursor_y:.0f})")
                else:
                    print(f"    -> ⚠️ Final validation failed for '{fxtr.name}' during placement.")
                current_x_in_row += width + horizontal_gap
            
            cursor_y += row_height + vertical_row_spacing

        if fixture_queue:
            print(f"\n--- ⚠️ Finished with {len(fixture_queue)} unplaced fixtures ---")
        else:
            print("\n--- ✅ Finished Dynamic Central Fixture Placement (V2 with Lane Strategy) ---")

    
#---------------------new  test for euro center placement--new_setup of centering
#---------------------new  test for euro center placement--new_setup of centering
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
    




    def find_right_wall_bottom_point_og(self) -> Optional[Tuple[float, float]]:
        """
        A robust helper to find the true bottom-right corner where walls intersect.
        This ensures fixtures start from the actual corner, not with a gap.
        """
        print("  -> Finding the exact bottom-right corner intersection...")
        
        # 1. Get the actual room bounds
        min_x, min_y = self.cvc.min_x, self.cvc.min_y
        max_x, max_y = self.cvc.max_x, self.cvc.max_y
        
        # 2. Find the bottom-right corner from the actual corner points
        corners = self.cvc.corners
        if not corners:
            print("    -> ⚠️ No corners found.")
            return None
        
        # Find the corner closest to the theoretical bottom-right
        target_x, target_y = max_x, min_y
        bottom_right_corner = min(corners, 
                                key=lambda corner: math.hypot(corner[0] - target_x, corner[1] - target_y))
        
        print(f"    -> ✅ Found exact bottom-right corner at: ({bottom_right_corner[0]:.0f}, {bottom_right_corner[1]:.0f})")
        return bottom_right_corner



    def get_retail_boundary_y(self) -> float:
        """
        Finds the lowest Y-coordinate of the clinic/BOH cluster to determine
        the stop line for the retail wall space calculation.
        """
        # This function reuses your existing logic to find only the 'stoppage' obstacles.
        stop_bboxes = self._get_accurate_obstacle_bboxes(include_all=False)
        
        if not stop_bboxes:
            print("  -> No BOH/Clinic boundary found; entire wall length is available.")
            # If no obstacles, return the top of the floorplan so the whole wall is measured.
            return self.cvc.max_y
        
        # The boundary is the lowest point of this cluster, minus a small margin.
        lowest_y = min(b[1] for b in stop_bboxes)
        margin = 100.0 
        boundary_y = lowest_y - margin
        
        print(f"  -> Retail boundary line calculated at Y-coordinate: {boundary_y:.0f}")
        return boundary_y

    def _get_perimeter_path_from_bottom_right__og(self):
        """
        Helper to get a perimeter path starting from the bottom-right corner,
        ensuring a CLOCKWISE direction to walk up the right wall first.
        """
        corners = self.cvc.corners
        if not corners: return []
        
        # Find the corner closest to the theoretical bottom-right
        start_idx = min(range(len(corners)), 
                           key=lambda i: math.hypot(corners[i][0] - self.cvc.max_x, corners[i][1] - self.cvc.min_y))
        
        reordered = corners[start_idx:] + corners[:start_idx]
        
        # Check winding order. A negative area means it's already Clockwise (CW).
        signed_area = 0.5 * sum(x1*y2 - x2*y1 for (x1, y1), (x2, y2) in zip(reordered, reordered[1:] + [reordered[0]]))
        
        # If the area is positive (Counter-Clockwise), we must reverse it.
        if signed_area > 0:
            reordered = reordered[0:1] + reordered[1:][::-1]
        
        perimeter_path = []
        for i in range(len(reordered)):
            p1_coords = reordered[i]
            p2_coords = reordered[(i + 1) % len(reordered)]
            if Vec2(p1_coords).distance(Vec2(p2_coords)) > 100:
                 perimeter_path.append((p1_coords, p2_coords))
        
        return perimeter_path

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
    
    def find_right_wall_bottom_point(self) -> Optional[Tuple[float, float]]:
        """
        A robust helper to find the true bottom-right corner where walls intersect.
        This ensures fixtures start from the actual corner, not with a gap.
        """
        print("  -> Finding the exact bottom-right corner intersection...")
        
        # 1. Get the actual room bounds
        min_x, min_y = self.cvc.min_x, self.cvc.min_y
        max_x, max_y = self.cvc.max_x, self.cvc.max_y
        
        # 2. Find the bottom-right corner from the actual corner points
        corners = self.cvc.corners
        if not corners:
            print("    -> ⚠️ No corners found.")
            return None
        
        # Find the corner closest to the theoretical bottom-right
        target_x, target_y = max_x, min_y
        bottom_right_corner = min(corners, 
                                key=lambda corner: math.hypot(corner[0] - target_x, corner[1] - target_y))
        
        print(f"    -> ✅ Found exact bottom-right corner at: ({bottom_right_corner[0]:.0f}, {bottom_right_corner[1]:.0f})")
        return bottom_right_corner
    


    def calculate_retail_wall_length(self, side: str) -> float:
        """
        Calculates the available retail wall length for a given side ('left' or 'right')
        by walking the perimeter until it hits the BOH/clinic boundary.
        """
        stop_line_y = self.get_retail_boundary_y()
        
        if side == 'left':
            perimeter_path = self._get_perimeter_path_from_bottom_left()
        elif side == 'right':
            perimeter_path = self._get_perimeter_path_from_bottom_right()
        else:
            return 0.0

        if not perimeter_path: return 0.0

        total_length = 0.0
        for p1_coords, p2_coords in perimeter_path:
            p1 = Vec2(p1_coords)
            p2 = Vec2(p2_coords)
            
            # If the entire segment is above the stop line, we're done.
            if p1.y >= stop_line_y and p2.y >= stop_line_y:
                break
                
            # If the segment is entirely below the line, add its full length.
            if p1.y < stop_line_y and p2.y < stop_line_y:
                total_length += p1.distance(p2)
            # If the segment crosses the line, calculate and add the partial length.
            else:
                # Ensure p1 is the lower point
                if p1.y > p2.y:
                    p1, p2 = p2, p1 # Swap points
                
                # Calculate intersection factor 't'
                if (p2.y - p1.y) == 0: continue # Avoid division by zero for horizontal lines
                t = (stop_line_y - p1.y) / (p2.y - p1.y)
                
                if 0 <= t <= 1:
                    partial_length = p1.distance(p2) * t
                    total_length += partial_length
                
                break # Stop after finding the first crossing segment

        print(f"  -> Calculated available '{side}' wall retail length: {total_length:.0f} mm")
        return total_length 


    
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


#-----------------newww setup--------trying----------------------------------------------------------------------------------
#-----------------newww setup--------trying----------------------------------------------------------------------------------


    def _analyze_perimeter_for_placeable_zones(self, perimeter_path: list, angle_tolerance_deg: float = 2.0, lateral_tolerance: float = 50.0):
        """
        [UPGRADED & ROBUST VERSION] Performs a "smart walk" along a continuous perimeter path.
        It now detects both sharp angle changes (corners) and lateral deviations (juts/partitions).

        Args:
            perimeter_path (list): An ordered list of segments [(p1, p2), ...] defining the path.
            angle_tolerance_deg (float): Max angle deviation from the main wall direction.
            lateral_tolerance (float): Max perpendicular distance a segment can be from the main wall line.
        """
        from ezdxf.math import Vec2
        import math
        
        print("  -> Starting 'Smart Walk' analysis (Robust Angle + Lateral Check)...")
        
        if not perimeter_path:
            return []

        placeable_zones = []
        if not perimeter_path:
            return placeable_zones

        current_zone_start = Vec2(perimeter_path[0][0])
        main_direction_vector = (Vec2(perimeter_path[0][1]) - current_zone_start).normalize()

        for i in range(len(perimeter_path)):
            current_seg_start = Vec2(perimeter_path[i][0])
            current_seg_end = Vec2(perimeter_path[i][1])
            
            # Create a vector for the current small segment
            current_segment_vector = (current_seg_end - current_seg_start).normalize()
            
            # --- CHECK 1: ANGLE DEVIATION ---
            # Does this segment's direction differ too much from the main flat wall's direction?
            try:
                angle_deg = abs(math.degrees(main_direction_vector.angle_between(current_segment_vector)))
            except ZeroDivisionError:
                angle_deg = 0.0

            # --- CHECK 2: LATERAL DEVIATION ---
            # How far is this segment's start point from the infinite line defined by the main flat wall?
            vec_to_point = current_seg_start - current_zone_start
            # Project this vector onto the main direction's perpendicular to get the lateral distance.
            lateral_dist = abs(vec_to_point.dot(main_direction_vector.orthogonal()))

            # --- DECISION ---
            # If it's either a sharp turn OR a significant sideways jut, the zone ends.
            if angle_deg > angle_tolerance_deg or lateral_dist > lateral_tolerance:
                
                # The previous segment's start point is the end of our flat zone.
                zone_end_point = Vec2(perimeter_path[i-1][1]) if i > 0 else current_zone_start
                zone_length = zone_end_point.distance(current_zone_start)
                
                print(f"    -> Deviation found (Angle: {angle_deg:.1f}°, Lateral: {lateral_dist:.1f}mm). Ending zone.")

                if zone_length > 500:
                    placeable_zones.append({
                        'start': current_zone_start, 
                        'end': zone_end_point, 
                        'length': zone_length
                    })
                
                # Start a new zone from the beginning of the current segment
                current_zone_start = current_seg_start
                main_direction_vector = current_segment_vector
        
        # After the loop, add the final zone that was being built
        last_point = Vec2(perimeter_path[-1][1])
        zone_length = last_point.distance(current_zone_start)
        if zone_length > 500:
            placeable_zones.append({
                'start': current_zone_start, 
                'end': last_point, 
                'length': zone_length
            })

        print(f"  -> Smart Walk complete. Found {len(placeable_zones)} placeable zones.")
        return placeable_zones
    

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
            margin_from_wall = 1.0

            # --- Setup ---
            mirror_config = self.fixtures.get("mirror_selection", {})
            selected_mirror_name = next((name for name, selected in mirror_config.items() if selected > 0), "mirror")
            horizontal_inset_for_hybrid = 0.0 if selected_mirror_name == "mirror_different" else 50.0

            placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
            stop_bboxes = self._get_accurate_obstacle_bboxes(include_all=False)
            # Call the new function in CV_Controller to get partition walls
            internal_wall_obstacles = self.cvc.get_internal_wall_partitions(2000,10)
            
            # Add the partitions to our main list of things to avoid
            placed_bboxes.extend(internal_wall_obstacles)
            print(f"  -> Total obstacles including partitions: {len(placed_bboxes)}")
            ### END OF CHANGE ###
            unplaced_fixtures = collections.deque()
            perimeter_path = self._get_perimeter_path_from_bottom_left()
            if not perimeter_path:
                return fixture_queue

            placeable_zones = self._analyze_perimeter_for_placeable_zones(perimeter_path)

            # --- Main Loop (Iterates over ZONES, not segments) ---
            for zone in placeable_zones:
                if not fixture_queue: 
                    break # Stop if all fixtures have been placed

                print(f"\n  -> Placing fixtures in Zone (Length: {zone['length']:.0f}mm)...")
                
                # Use the data from the current zone.
                p1, p2 = zone['start'], zone['end']
                wall_length = zone['length']
                wall_vector = (p2 - p1).normalize()
                wall_angle_rad = wall_vector.angle
                wall_angle_deg = math.degrees(wall_angle_rad)
                inward_normal = wall_vector.orthogonal().normalize()
                if not self.floorplan_polygon.contains(Point(p1 + inward_normal * 1.0)):
                    inward_normal = -inward_normal

                # Use a single cursor, reset for each new zone.
                cursor = 1.0

                ### CHANGE: This is the correctly structured inner loop.
                ### It tries to fill the CURRENT zone with fixtures as long as there is space.
                while cursor < wall_length - 50.0:
                    if not fixture_queue: 
                        break
                    
                    ### CHANGE: "Peek" at the fixture, don't pop it from the queue yet.
                    item_to_try = fixture_queue[0]
                    fixture_name, _ = item_to_try
                    
                    try:
                        hybrid_fxtr = Fixture(fixture_name, self.fixture_dict[fixture_name]["path"])
                        mirror_fxtr = Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
                    except (KeyError, ValueError) as e:
                        # Pop the bad data from the queue and add to unplaced list
                        unplaced_fixtures.append(fixture_queue.popleft())
                        continue

                    # Check if the next pair can theoretically fit in the remaining space
                    pair_width = hybrid_fxtr.width + mirror_fxtr.width
                    if cursor + pair_width > wall_length - 50.0:
                        break # Not enough space left in this zone, move to the NEXT zone.

                    ### CHANGE: The incorrect 'for segment in perimeter_path:' loop has been REMOVED.
                    ### All validation now correctly uses the 'zone' data (p1, wall_vector) and the 'cursor'.

                    # --- 1. VALIDATE HYBRID SPOT (using cursor, not search_distance) ---
                    footprint_start_h = p1 + wall_vector * cursor
                    center_on_wall_h = footprint_start_h + wall_vector * (hybrid_fxtr.width / 2.0)
                    offset_dist_h = margin_from_wall + (hybrid_fxtr.height / 2.0) + horizontal_inset_for_hybrid
                    target_center_h = center_on_wall_h + inward_normal * offset_dist_h
                    local_center_h = hybrid_fxtr.bounding_box.center
                    transform_h = Matrix44.chain(Matrix44.translate(-local_center_h.x, -local_center_h.y, 0), Matrix44.z_rotate(wall_angle_rad), Matrix44.translate(target_center_h.x, target_center_h.y, 0))
                    world_corners_h = list(transform_h.transform_vertices(hybrid_fxtr.bounding_box.rect_vertices()))
                    poly_h = Polygon([(p.x, p.y) for p in world_corners_h])
                    aabb_h = BoundingBox2d(world_corners_h)

                    if any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in stop_bboxes):
                        print(f"    -> 🛑 HARD STOP: Obstacle detected. Terminating Pass 1.")
                        # Return all remaining fixtures, including the one we were trying
                        unplaced_fixtures.extend(fixture_queue)
                        return unplaced_fixtures

                    hybrid_is_valid = self.floorplan_polygon.contains(poly_h) and not any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                    if hybrid_is_valid:
                        # --- 2. VALIDATE MIRROR SPOT ---
                        mirror_cursor_start = cursor + hybrid_fxtr.width
                        mirror_is_valid = False
                        aabb_m = BoundingBox2d()
                        
                        if mirror_cursor_start + mirror_fxtr.width <= wall_length:
                            footprint_start_m = p1 + wall_vector * mirror_cursor_start
                            center_on_wall_m = footprint_start_m + wall_vector * (mirror_fxtr.width / 2.0)
                            offset_dist_m = margin_from_wall + (mirror_fxtr.height / 2.0) + horizontal_inset_for_hybrid
                            target_center_m = center_on_wall_m + inward_normal * offset_dist_m
                            local_center_m = mirror_fxtr.bounding_box.center
                            transform_m = Matrix44.chain(Matrix44.translate(-local_center_m.x, -local_center_m.y, 0), Matrix44.z_rotate(wall_angle_rad), Matrix44.translate(target_center_m.x, target_center_m.y, 0))
                            world_corners_m = list(transform_m.transform_vertices(mirror_fxtr.bounding_box.rect_vertices()))
                            poly_m = Polygon([(p.x, p.y) for p in world_corners_m])
                            aabb_m = BoundingBox2d(world_corners_m)
                            
                            if self.floorplan_polygon.contains(poly_m) and not any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes):
                                mirror_is_valid = True

                        # --- 3. PLACE FIXTURES ---
                        final_insert_point_h = target_center_h - local_center_h.rotate(wall_angle_rad)
                        self.place_fixture(hybrid_fxtr, (final_insert_point_h.x, final_insert_point_h.y, 0), wall_angle_deg, True)
                        placed_bboxes.append((aabb_h.extmin.x, aabb_h.extmin.y, aabb_h.extmax.x, aabb_h.extmax.y))

                        if mirror_is_valid:
                            final_insert_point_m = target_center_m - local_center_m.rotate(wall_angle_rad)
                            self.place_fixture(mirror_fxtr, (final_insert_point_m.x, final_insert_point_m.y, 0), wall_angle_deg, True)
                            placed_bboxes.append((aabb_m.extmin.x, aabb_m.extmin.y, aabb_m.extmax.x, aabb_m.extmax.y))
                            print(f"✅ Placed pair '{hybrid_fxtr.name}' & '{mirror_fxtr.name}'.")
                        else:
                            print(f"✅ Placed '{hybrid_fxtr.name}' alone (mirror blocked).")

                        ### CHANGE: Pop ONLY after a successful placement.
                        fixture_queue.popleft()
                        
                        # --- 4. UPDATE CURSOR ---
                        placed_width = hybrid_fxtr.width + (mirror_fxtr.width if mirror_is_valid else 0)
                        cursor += placed_width + GAP_BETWEEN_PAIRS
                    
                    else:
                        # If spot was blocked, nudge search forward on the SAME wall
                        cursor += 10.0

            # After all zones are processed, anything left is unplaced
            unplaced_fixtures.extend(fixture_queue)
            return unplaced_fixtures

        except Exception as e:
            print(f"🔥 An error occurred during wall placement: {e}")
            traceback.print_exc()
            unplaced_fixtures.extend(fixture_queue)
            return unplaced_fixtures
        
    

    def place_fixtures_on_right_wall_new_og(self, fixture_queue: collections.deque):
        """
        FINAL CORRECTED VERSION for Pass 2.
        - Implements the same robust "zone-based" placement as the left wall.
        - Correctly distinguishes between skippable partitions and critical "stop" obstacles.
        """
        from Fixture import Fixture
        from shapely.geometry import Polygon, Point
        from ezdxf.math import BoundingBox2d, Vec2, Matrix44
        import math
        import traceback
        import collections

        print(f"\n--- Placing Wall Fixtures (Pass 2: Corrected Zone-Based Walk) ---")

        ### CHANGE: Initialize unplaced_fixtures at the start for robust error handling ###
        unplaced_fixtures = collections.deque()

        try:
            if not fixture_queue:
                return unplaced_fixtures

            GAP_BETWEEN_PAIRS = 0
            margin_from_wall = 1.0

            # --- Setup (Same as left wall) ---
            mirror_config = self.fixtures.get("mirror_selection", {})
            selected_mirror_name = next((name for name, selected in mirror_config.items() if selected > 0), "mirror")
            horizontal_inset_for_hybrid = 0.0 if selected_mirror_name == "mirror_different" else 50.0

            placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
            stop_bboxes = self._get_accurate_obstacle_bboxes(include_all=False)
            
            internal_wall_obstacles = self.cvc.get_internal_wall_partitions(200, 200)
            placed_bboxes.extend(internal_wall_obstacles)
            print(f"  -> Total obstacles including partitions: {len(placed_bboxes)}")

            # --- Get Clean Placeable Zones (Same as left wall) ---
            perimeter_path = self._get_perimeter_path_from_bottom_right()
            # perimeter_path = self.find_right_wall_bottom_point()
            if not perimeter_path:
                unplaced_fixtures.extend(fixture_queue)
                return unplaced_fixtures

            starting_corner = self.find_right_wall_bottom_point()
            if starting_corner:
                first_segment_start = perimeter_path[0][0]
                print(f"  -> Starting from bottom-right corner: ({starting_corner[0]:.0f}, {starting_corner[1]:.0f})")
                print(f"  -> First segment starts at: ({first_segment_start[0]:.0f}, {first_segment_start[1]:.0f})")

            placeable_zones = self._analyze_perimeter_for_placeable_zones(perimeter_path)

            # --- Main Loop (Iterates over ZONES) ---
            for zone in placeable_zones:
                if not fixture_queue: 
                    break

                print(f"\n  -> Placing fixtures in Zone (Length: {zone['length']:.0f}mm)...")
                
                p1, p2 = zone['start'], zone['end']
                wall_length = zone['length']
                wall_vector = (p2 - p1).normalize()
                wall_angle_rad = wall_vector.angle
                wall_angle_deg = math.degrees(wall_angle_rad)
                
                inward_normal = wall_vector.orthogonal().normalize()
                if not self.floorplan_polygon.contains(Point(p1 + inward_normal * 1.0)):
                    inward_normal = -inward_normal

                cursor = 10.0

                while cursor < wall_length - 50.0:
                    if not fixture_queue: 
                        break
                    
                    item_to_try = fixture_queue[0]
                    fixture_name, _ = item_to_try
                    
                    try:
                        hybrid_fxtr = Fixture(fixture_name, self.fixture_dict[fixture_name]["path"])
                        mirror_fxtr = Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
                    except (KeyError, ValueError):
                        unplaced_fixtures.append(fixture_queue.popleft())
                        continue

                    pair_width = hybrid_fxtr.width + mirror_fxtr.width
                    if cursor + pair_width > wall_length - 50.0:
                        break

                    ### CHANGE: Replaced the old collision logic with the correct two-part validation ###
                    
                    # --- 1. VALIDATE HYBRID SPOT ---
                    footprint_start_h = p1 + wall_vector * cursor
                    center_on_wall_h = footprint_start_h + wall_vector * (hybrid_fxtr.width / 2.0)
                    offset_dist_h = margin_from_wall + (hybrid_fxtr.height / 2.0) + horizontal_inset_for_hybrid
                    target_center_h = center_on_wall_h + inward_normal * offset_dist_h
                    local_center_h = hybrid_fxtr.bounding_box.center
                    transform_h = Matrix44.chain(Matrix44.translate(-local_center_h.x, -local_center_h.y, 0), Matrix44.z_rotate(wall_angle_rad), Matrix44.translate(target_center_h.x, target_center_h.y, 0))
                    world_corners_h = list(transform_h.transform_vertices(hybrid_fxtr.bounding_box.rect_vertices()))
                    poly_h = Polygon([(p.x, p.y) for p in world_corners_h])
                    aabb_h = BoundingBox2d(world_corners_h)

                    # --- HARD STOP CHECK: Against 'stop_bboxes' ONLY ---
                    if any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in stop_bboxes):
                        print(f"    -> 🛑 HARD STOP: Obstacle detected. Terminating Pass 2.")
                        unplaced_fixtures.extend(fixture_queue)
                        return unplaced_fixtures

                    # --- REGULAR COLLISION CHECK: Against 'placed_bboxes' (includes partitions) ---
                    hybrid_is_valid = self.floorplan_polygon.contains(poly_h) and not any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)

                    if hybrid_is_valid:
                        # --- 2. VALIDATE MIRROR SPOT ---
                        mirror_cursor_start = cursor + hybrid_fxtr.width
                        mirror_is_valid = False
                        
                        if mirror_cursor_start + mirror_fxtr.width <= wall_length:
                            # (Validation logic for mirror is the same as the left wall)
                            footprint_start_m = p1 + wall_vector * mirror_cursor_start
                            center_on_wall_m = footprint_start_m + wall_vector * (mirror_fxtr.width / 2.0)
                            offset_dist_m = margin_from_wall + (mirror_fxtr.height / 2.0) + horizontal_inset_for_hybrid
                            target_center_m = center_on_wall_m + inward_normal * offset_dist_m
                            local_center_m = mirror_fxtr.bounding_box.center
                            transform_m = Matrix44.chain(Matrix44.translate(-local_center_m.x, -local_center_m.y, 0), Matrix44.z_rotate(wall_angle_rad), Matrix44.translate(target_center_m.x, target_center_m.y, 0))
                            world_corners_m = list(transform_m.transform_vertices(mirror_fxtr.bounding_box.rect_vertices()))
                            poly_m = Polygon([(p.x, p.y) for p in world_corners_m])
                            aabb_m = BoundingBox2d(world_corners_m)
                            if self.floorplan_polygon.contains(poly_m) and not any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes):
                                mirror_is_valid = True

                        # --- 3. PLACE FIXTURES ---
                        final_insert_point_h = target_center_h - local_center_h.rotate(wall_angle_rad)
                        self.place_fixture(hybrid_fxtr, (final_insert_point_h.x, final_insert_point_h.y, 0), wall_angle_deg, True)
                        placed_bboxes.append((aabb_h.extmin.x, aabb_h.extmin.y, aabb_h.extmax.x, aabb_h.extmax.y))

                        if mirror_is_valid:
                            final_insert_point_m = target_center_m - local_center_m.rotate(wall_angle_rad)
                            self.place_fixture(mirror_fxtr, (final_insert_point_m.x, final_insert_point_m.y, 0), wall_angle_deg, True)
                            placed_bboxes.append((aabb_m.extmin.x, aabb_m.extmin.y, aabb_m.extmax.x, aabb_m.extmax.y))
                            print(f"✅ Placed pair '{hybrid_fxtr.name}' & '{mirror_fxtr.name}'.")
                        else:
                            print(f"✅ Placed '{hybrid_fxtr.name}' alone (mirror blocked).")

                        fixture_queue.popleft()
                        
                        placed_width = hybrid_fxtr.width + (mirror_fxtr.width if mirror_is_valid else 0)
                        cursor += placed_width + GAP_BETWEEN_PAIRS
                    
                    else: # This 'else' corresponds to 'if hybrid_is_valid:'
                        # If the spot was blocked by a partition, nudge the cursor to "skip" it
                        cursor += 10.0
            
            unplaced_fixtures.extend(fixture_queue)
            return unplaced_fixtures

        except Exception as e:
            print(f"🔥 An error occurred during RIGHT wall placement: {e}")
            traceback.print_exc()
            unplaced_fixtures.extend(fixture_queue)
            return unplaced_fixtures


    def place_fixtures_on_right_wall_new(self, fixture_queue: collections.deque):
        """
        FINAL ROBUST VERSION for Pass 2.
        - CORRECTED: Loads all obstacles to enable partition skipping.
        - CORRECTED: Distinguishes between skippable partitions and critical stop obstacles.
        """
        from Fixture import Fixture
        from shapely.geometry import Polygon, Point, box
        from ezdxf.math import BoundingBox2d, Vec2, Matrix44
        import math
        import collections # Add collections for deque

        print(f"\n--- Placing Wall Fixtures (Pass 2: Walking Along Wall Path with Skipping) ---")
        
        unplaced_fixtures = collections.deque()

        try:
            if not fixture_queue:
                return unplaced_fixtures

            ### --- START OF MODIFICATION --- ###
            # --- 1. SETUP - Get ALL obstacles, including partitions and stops ---
            placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)
            stop_bboxes = self._get_accurate_obstacle_bboxes(include_all=False)

            internal_wall_obstacles = self.cvc.get_internal_wall_partitions(2000,10)
            placed_bboxes.extend(internal_wall_obstacles)
            print(f"  -> Total obstacles for skipping: {len(placed_bboxes)}")
            print(f"  -> Critical stop obstacles: {len(stop_bboxes)}")
            ### --- END OF MODIFICATION --- ###

            mirror_config = self.fixtures.get("mirror_selection", {})
            selected_mirror_name = next((name for name, selected in mirror_config.items() if selected > 0), "mirror")
            
            # --- 2. Get the perimeter path (Your original logic is correct) ---
            start_point_coords = self.find_right_wall_bottom_point()
            if not start_point_coords:
                unplaced_fixtures.extend(fixture_queue); return unplaced_fixtures

            start_point_vec = Vec2(start_point_coords)
            corners = self.cvc.corners
            start_idx = min(range(len(corners)), key=lambda i: start_point_vec.distance(Vec2(corners[i])))
            reordered = corners[start_idx:] + corners[:start_idx]
            
            signed_area = 0.5 * sum(x1*y2 - x2*y1 for (x1, y1), (x2, y2) in zip(reordered, reordered[1:] + [reordered[0]]))
            if signed_area < 0:
                reordered = reordered[0:1] + reordered[1:][::-1]

            perimeter_path = []
            for i in range(len(reordered)):
                p1 = Vec2(reordered[i]); p2 = Vec2(reordered[(i + 1) % len(reordered)])
                if p1.distance(p2) > 100:
                    perimeter_path.append((p1, p2))
            
            if not perimeter_path:
                unplaced_fixtures.extend(fixture_queue); return unplaced_fixtures

            # --- 4. Walk along each wall segment ---
            margin_from_wall = 1.0; gap_between_pairs = 0.0

            for segment_idx, (segment_start, segment_end) in enumerate(perimeter_path):
                if not fixture_queue: break
                    
                wall_length = segment_start.distance(segment_end)
                segment_vector = (segment_end - segment_start).normalize()
                wall_angle_deg = math.degrees(segment_vector.angle)
                
                inward_normal = segment_vector.orthogonal()
                mid_point_on_wall = segment_start + segment_vector * (wall_length / 2)
                if not self.floorplan_polygon.contains(Point(mid_point_on_wall + inward_normal * 10)):
                    inward_normal = -inward_normal

                placement_cursor = 10.0 # Use a consistent start margin
                
                while fixture_queue and placement_cursor < wall_length - 100:
                    item_to_try = fixture_queue[0]
                    fixture_name, _ = item_to_try
                    
                    try:
                        hybrid_fxtr = Fixture(fixture_name, self.fixture_dict[fixture_name]["path"])
                        mirror_fxtr = Fixture(selected_mirror_name, self.fixture_dict[selected_mirror_name]["path"])
                    except (KeyError, ValueError):
                        unplaced_fixtures.append(fixture_queue.popleft()); continue

                    fixture_rotation_deg = wall_angle_deg + 180
                    pair_width = hybrid_fxtr.width + mirror_fxtr.width
                    if placement_cursor + pair_width > wall_length - 50:
                        break

                    # --- VALIDATE HYBRID ---
                    footprint_start_h = segment_start + segment_vector * placement_cursor
                    center_on_wall_h = footprint_start_h + segment_vector * (hybrid_fxtr.width / 2.0)
                    offset_dist_h = margin_from_wall + (hybrid_fxtr.height / 2.0)
                    target_center_h = center_on_wall_h + inward_normal * offset_dist_h
                    local_center_h = hybrid_fxtr.bounding_box.center
                    
                    transform_h = Matrix44.chain(Matrix44.translate(-local_center_h.x, -local_center_h.y, 0), Matrix44.z_rotate(math.radians(fixture_rotation_deg)), Matrix44.translate(target_center_h.x, target_center_h.y, 0))
                    world_corners_h = list(transform_h.transform_vertices(hybrid_fxtr.bounding_box.rect_vertices()))
                    aabb_h = BoundingBox2d(world_corners_h)
                    hybrid_poly = Polygon([(p.x, p.y) for p in world_corners_h])
                    
                    ### --- START OF MODIFICATION --- ###
                    # --- HARD STOP CHECK (against stop_bboxes only) ---
                    
                    if any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in stop_bboxes):
                        print(f"    -> 🛑 HARD STOP: Obstacle detected. Terminating Pass 1.")
                        # Return all remaining fixtures, including the one we were trying
                        unplaced_fixtures.extend(fixture_queue)
                        return unplaced_fixtures

                    # --- REGULAR COLLISION/SKIP CHECK (against placed_bboxes, which includes partitions) ---
                    is_valid = self.floorplan_polygon.contains(hybrid_poly) and not any(aabb_h.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)
                    ### --- END OF MODIFICATION --- ###

                    if is_valid:
                        # --- VALIDATE AND PLACE MIRROR (This logic can remain) ---
                        mirror_cursor_start = placement_cursor + hybrid_fxtr.width
                        mirror_is_valid = False
                        if mirror_cursor_start + mirror_fxtr.width <= wall_length:
                            # Calculate the mirror's potential center point
                            footprint_start_m = segment_start + segment_vector * mirror_cursor_start
                            center_on_wall_m = footprint_start_m + segment_vector * (mirror_fxtr.width / 2.0)
                            offset_dist_m = margin_from_wall + (mirror_fxtr.height / 2.0)
                            target_center_m = center_on_wall_m + inward_normal * offset_dist_m
                            local_center_m = mirror_fxtr.bounding_box.center

                            # Create the transformation to find its final geometry
                            transform_m = Matrix44.chain(
                                Matrix44.translate(-local_center_m.x, -local_center_m.y, 0),
                                Matrix44.z_rotate(math.radians(fixture_rotation_deg)),
                                Matrix44.translate(target_center_m.x, target_center_m.y, 0)
                            )
                            world_corners_m = list(transform_m.transform_vertices(mirror_fxtr.bounding_box.rect_vertices()))
                            aabb_m = BoundingBox2d(world_corners_m)
                            mirror_poly = Polygon([(p.x, p.y) for p in world_corners_m])

                            # Check if the mirror is inside the floorplan and not overlapping anything
                            if self.floorplan_polygon.contains(mirror_poly) and not any(aabb_m.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes):
                                mirror_is_valid = True

                        # Place HYBRID
                        rotated_offset_h = local_center_h.rotate(math.radians(fixture_rotation_deg))
                        final_insert_point_h = target_center_h - rotated_offset_h
                        self.place_fixture(hybrid_fxtr, (final_insert_point_h.x, final_insert_point_h.y, 0), fixture_rotation_deg, True)
                        placed_bboxes.append(tuple(aabb_h.extmin) + tuple(aabb_h.extmax))

                        # Place MIRROR if valid
                        if mirror_is_valid:
                            rotated_offset_m = local_center_m.rotate(math.radians(fixture_rotation_deg))
                            final_insert_point_m = target_center_m - rotated_offset_m
                            self.place_fixture(mirror_fxtr, (final_insert_point_m.x, final_insert_point_m.y, 0), fixture_rotation_deg, True)
                            placed_bboxes.append(tuple(aabb_m.extmin) + tuple(aabb_m.extmax))
                            print(f"    -> ✅ Placed pair '{hybrid_fxtr.name}' & '{mirror_fxtr.name}'")
                        else:
                            print(f"    -> ✅ Placed '{hybrid_fxtr.name}' alone (mirror blocked)")

                        
                        fixture_queue.popleft()
                        placement_cursor += pair_width + gap_between_pairs
                    else:
                        # This is the "JUMP" logic. If the spot is blocked, nudge the cursor.
                        placement_cursor += 10.0

            unplaced_fixtures.extend(fixture_queue)
            print(f"    -> 🎯 Placement complete. {len(unplaced_fixtures)} fixtures remain unplaced from this pass.")
            return unplaced_fixtures

        except Exception as e:
            print(f"🔥 An error occurred during RIGHT wall placement: {e}")
            traceback.print_exc()
            unplaced_fixtures.extend(fixture_queue)
            return unplaced_fixtures
        
#-----------------newww setup--------trying----------------------------------------------------------------------------------
#-----------------newww setup--------trying-----NEW AGAIN--------------------------------------------------------------------------------
#-----------------newww setup--------trying-----NEW AGAIN--------------------------------------------------------------------------------

    

#-----------------newww setup--------trying-----NEW AGAIN--------------------------------------------------------------------------------
#-----------------newww setup--------trying-----NEW AGAIN--------------------------------------------------------------------------------

#-----------------------wall_fixture placement PLACEMENT FUNCTION FINISED HERE------------------------------------------------------------------------------------


# CATEGORY :- REMAINING FLOOR FIXTURES

#---- DISCUSSION TABLE PLACEMENT FUNCTION STARTED ----

    def place_discussion_tables_attached_to_euros(self, placed_bboxes):
        """
        Finds all placed Euro_centre fixtures and attaches discussion tables based on a
        simplified count. It automatically alternates placement on the left and right
        sides for each subsequent Euro_centre.
        """
        from Fixture import Fixture
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
                table_fxtr = Fixture(self.fixture_dict[table_fixture_name]["name"],
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

    def place_pos_ar_portrait_dynamically_og(self, placed_bboxes):
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
            placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)

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


    #new__test__
    #new__test__
    
    
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

            # --- FALLBACK A: Double Shopping (Place Below) ---
            if is_double_shopping:
                print("  -> Detected Double Shopping layout. Placing Blue_zero BELOW Euro Centres.")
                for target_bbox in fallback_anchors:
                    if placed_count >= blue_zero_count: break
                    target_x = target_bbox.center.x - (blue_zero_fxtr.width / 2)
                    target_y = target_bbox.extmin.y - margin - blue_zero_fxtr.height
                    candidate_box = box(target_x, target_y, target_x + blue_zero_fxtr.width, target_y + blue_zero_fxtr.height)
                    if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                        self.place_fixture(blue_zero_fxtr, (target_x, target_y, 0), 0, False)
                        placed_bboxes.append(candidate_box.bounds)
                        print(f"✅ Placed Blue_zero below a Euro Centre.")
                        placed_count += 1
            
            # --- FALLBACK B: Single Shopping (Place Left/Right) ---
            else:
                print("  -> Detected Single Shopping layout. Placing Blue_zero to the LEFT/RIGHT of Euro Centres.")
                for i, target_bbox in enumerate(fallback_anchors):
                    if placed_count >= blue_zero_count: break
                    
                    side = "left" if i % 2 == 0 else "right"
                    
                    if side == "left":
                        rotation = 270
                        insert_x = target_bbox.extmin.x - blue_zero_fxtr.height - margin
                        insert_y = target_bbox.center.y - (blue_zero_fxtr.width / 2)
                        final_insert_point = (insert_x, insert_y + blue_zero_fxtr.width, 0)
                        candidate_box = box(insert_x, insert_y, insert_x + blue_zero_fxtr.height, insert_y + blue_zero_fxtr.width)
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
        from Fixture import Fixture # Make sure Fixture is imported

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
            qms_fxtr = Fixture("QMS_desk", self.fixture_dict["QMS_desk"]["path"])
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

    def _get_standing_table_anchor_y(self) -> Optional[float]:
        """
        FINDS THE CORRECT ANCHOR LINE (Y-coordinate) to measure from for standing tables.
        1. Finds the lowest non-retail fixture.
        2. Checks if any Bench/AR fixture is within 500mm below it.
        3. Returns the Y-coordinate of the correct anchor (either the furniture or the non-retail fixture).
        """
        from ezdxf.bbox import extents
        print("\n  -> Finding dynamic anchor-Y for Standing Tables...")

        # --- STEP 1: Find the lowest placed non-retail fixture ---
        non_retail_entities = [
            e for e in self.msp.query('LINE[layer=="RETAIL_SEPARATOR"]')# if
            # "CLINIC" in e.dxf.name.upper() or "PICK_UP_WINDOW" in e.dxf.name.upper()
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

        # --- STEP 2: Check for Bench or AR within 500mm below that fixture ---
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
                    if furniture_bbox.extmax.y < lowest_non_retail_y:
                        gap = lowest_non_retail_y - furniture_bbox.extmax.y
                        if gap <= 500.0:
                            candidate_furniture.append(furniture_bbox)
                except (RuntimeError, TypeError):
                    continue
            
            if candidate_furniture:
                new_anchor_furniture_bbox = min(candidate_furniture, key=lambda b: b.extmin.y)

        # --- STEP 3: Determine and return the final anchor Y-coordinate ---
        if new_anchor_furniture_bbox:
            final_anchor_y = new_anchor_furniture_bbox.extmin.y
            print(f"    -> Found relevant furniture. Final anchor is the furniture's bottom edge at y={final_anchor_y:.0f}.")
            return final_anchor_y
        else:
            print("    -> No nearby furniture found. Final anchor is the non-retail fixture's bottom edge.")
            return lowest_non_retail_y
    
    def place_standing_tables_beside_euros(self, placed_bboxes):
        """
        Places Standing Tables using a top-down, adaptive row-based strategy.
        - ANCHOR: Finds the lowest point of the non-retail cluster (Clinics, BOH).
        - PLACEMENT: Places the first row 1200mm below this anchor.
        - DIRECTION: Stacks subsequent rows downwards.
        - A robust fallback places any remaining tables in the side aisles.
        """
        from ezdxf.bbox import extents
        from shapely.geometry import box, LineString
        import collections

        print("\n--- 🧠 Placing Standing Tables (Robust Top-Down Strategy) ---")

        # 1. Get configuration
        config = self.fixtures.get("table_fixtures", {})
        standing_table_count = config.get("Standing_table", 0)
        if standing_table_count <= 0:
            return

        try:
            standing_fxtr = Fixture.Fixture("Standing_table", self.fixture_dict["Standing_table"]["path"])
        except Exception as e:
            print(f"🔥 Could not load Standing_table fixture: {e}")
            return

        # --- NEW SIMPLIFIED Y-COORDINATE LOGIC ---

        # A. Find the non-retail fixtures to anchor to.
        non_retail_entities = [
            e for e in self.msp.query('INSERT') if
            "CLINIC" in e.dxf.name.upper() or "PICK_UP_WINDOW" in e.dxf.name.upper()
        ]
        all_polylines = self.msp.query('LWPOLYLINE')
        boh_outlines = [p for p in all_polylines if "BOH_WALL_" in p.dxf.layer and p.dxf.layer.endswith("_OUTLINE")]
        
        combined_non_retail_entities = non_retail_entities + boh_outlines
        
        if not combined_non_retail_entities:
            print("  -> ⚠️ SKIPPING: No non-retail fixtures found to anchor the placement.")
            return

        # B. Calculate the starting Y-coordinate based on the lowest point of the anchor group.
        top_boundary_box = extents(combined_non_retail_entities)
        anchor_y = self._get_standing_table_anchor_y()
        gap_below_anchor  = 950
        if anchor_y is None:
            print("  -> ⚠️ FAILED: Could not determine a valid anchor Y-coordinate. Aborting placement.")
            return

        # The y_cursor is the BOTTOM of the row, so we start at the anchor's lowest point and subtract the gap and fixture height.
        y_cursor_start =  y_cursor_start = anchor_y - gap_below_anchor - standing_fxtr.height #top_boundary_box.extmin.y - gap_below_non_retail - standing_fxtr.height
        print(f"  -> Top boundary found at y={top_boundary_box.extmin.y:.0f}. Starting first row at y={y_cursor_start:.0f}.")

        # --- (Unchanged logic for helpers and queue setup) ---
        horizontal_gap = 750.0
        vertical_row_gap = 750.0
        fixture_queue = collections.deque([standing_fxtr] * standing_table_count)

        def is_valid_row(start_x, y, fixtures_in_row):
            current_x = start_x
            for i, fxtr in enumerate(fixtures_in_row):
                candidate_box = box(current_x, y, current_x + fxtr.width, y + fxtr.height)
                if not self.floorplan_polygon.contains(candidate_box.buffer(-1.0)) or any(candidate_box.intersects(box(*b)) for b in placed_bboxes):
                    return False
                if i < len(fixtures_in_row) - 1:
                    current_x += fxtr.width + horizontal_gap
            return True

        def find_best_row_size(placeable_width, fxtr_obj, max_to_check):
            for n in range(min(max_to_check, 5), 0, -1):
                required_width = (fxtr_obj.width * n) + (horizontal_gap * (n - 1))
                if required_width <= placeable_width:
                    return n
            return 0

        # --- Main Adaptive Placement Loop (Moves DOWNWARDS) ---
        placed_count = 0
        y_cursor = y_cursor_start
        y_cursor_end = self.cvc.min_y # Stop when we reach the bottom of the room

        while fixture_queue and y_cursor > y_cursor_end:
            intersection = self.floorplan_polygon.intersection(LineString([(self.cvc.min_x - 100, y_cursor), (self.cvc.max_x + 100, y_cursor)]))
            if not isinstance(intersection, LineString) or intersection.is_empty:
                y_cursor -= 200; continue

            local_bounds, local_width, local_start_x = intersection.bounds, intersection.length, intersection.bounds[0]
            walking_space_margin = max(300.0, local_width * 0.30)
            placeable_width = local_width - walking_space_margin
            
            num_to_place_in_row = find_best_row_size(placeable_width, standing_fxtr, len(fixture_queue))
            if num_to_place_in_row == 0:
                y_cursor -= 200; continue

            tables_for_this_row = [fixture_queue[i] for i in range(num_to_place_in_row)]
            total_row_width = (standing_fxtr.width * num_to_place_in_row) + (horizontal_gap * (num_to_place_in_row - 1))
            ideal_start_x = local_start_x + (local_width - total_row_width) / 2
            
            valid_start_x = None
            search_offset = 0
            while search_offset < local_width / 2:
                for sign in [1, -1]:
                    test_x = ideal_start_x + (search_offset * sign)
                    if is_valid_row(test_x, y_cursor, tables_for_this_row):
                        valid_start_x = test_x; break
                if valid_start_x is not None: break
                search_offset += 100

            if valid_start_x is not None:
                current_x = valid_start_x
                for _ in range(num_to_place_in_row):
                    fxtr = fixture_queue.popleft()
                    self.place_fixture(fxtr, (current_x, y_cursor, 0), 0, False)
                    placed_bboxes.append((current_x, y_cursor, current_x + fxtr.width, y_cursor + fxtr.height))
                    current_x += fxtr.width + horizontal_gap
                placed_count += num_to_place_in_row
                y_cursor -= (standing_fxtr.height + vertical_row_gap)
            else:
                y_cursor -= 200
        
        # --- Fallback Strategy ---
        if fixture_queue:
            print(f"\n  -> Attempting Fallback: Placing {len(fixture_queue)} remaining tables in side columns...")
            anchor_bbox = None
            central_anchor_entities = [e for e in self.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
            if central_anchor_entities:
                anchor_bbox = extents(central_anchor_entities)

            if not anchor_bbox:
                print("    -> ⚠️ Fallback failed: No central fixtures found to anchor side columns.")
            else:
                def is_valid_spot_fallback(fixture, x, y):
                    w, h = fixture.width, fixture.height
                    candidate_box = box(x, y, x + w, y + h)
                    is_overlapping = any(candidate_box.intersects(box(*bbox)) for bbox in placed_bboxes)
                    is_inside = self.floorplan_polygon.contains(candidate_box)
                    return is_inside and not is_overlapping

                vertical_gap_fallback = 1500.0
                center_x_right = (anchor_bbox.extmax.x + self.cvc.max_x) / 2
                target_x_right = center_x_right - (standing_fxtr.width / 2)
                center_x_left = (anchor_bbox.extmin.x + self.cvc.min_x) / 2
                target_x_left = center_x_left - (standing_fxtr.width / 2)
                
                current_y_right = anchor_bbox.extmin.y + vertical_gap_fallback
                current_y_left = anchor_bbox.extmin.y + vertical_gap_fallback

                num_to_place_fallback = len(fixture_queue)
                for i in range(num_to_place_fallback):
                    if i % 2 == 0:
                        target_x, target_y, side = target_x_right, current_y_right, "right"
                    else:
                        target_x, target_y, side = target_x_left, current_y_left, "left"

                    if is_valid_spot_fallback(standing_fxtr, target_x, target_y):
                        fixture_queue.popleft()
                        self.place_fixture(standing_fxtr, (target_x, target_y, 0), 0, False)
                        placed_bboxes.append((target_x, target_y, target_x + standing_fxtr.width, target_y + standing_fxtr.height))
                        placed_count += 1
                        
                        if side == "right": current_y_right += standing_fxtr.height + vertical_gap_fallback
                        else: current_y_left += standing_fxtr.height + vertical_gap_fallback
                    else:
                        print(f"    -> ⚠️ Could not place fallback table on the {side} (spot blocked).")
        
        print(f"\n-> Finished: Placed {placed_count} of {standing_table_count} Standing Tables.")




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
        from Fixture import Fixture
        import collections
        from ezdxf.math import Vec2

        print("\n--- 🧠 Placing TV Screens with Hybrid Priority/Stacking Strategy ---")
        
        try:
            screen_config = self.fixtures.get("screen_fixtures", {})
            screens_to_place = collections.deque([
                Fixture(name, self.fixture_dict[name]["path"])
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
        from Fixture import Fixture
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
            table_config = self.fixtures.get("floor_fixtures_table", {})
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


#------ discussion_tables PLACEMENT FUNCTION FINISHED HERE ----


#------ pos_ar PLACEMENT FUNCTION STARTED HERE ----

    def place_pos_ar_landscape(self, placed_bboxes):
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



    def place_qms_at_entrance_center(self, placed_bboxes):
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

    #------ corian_table_set PLACEMENT FUNCTION FINISHED HERE ----

    #------ standing_tables PLACEMENT FUNCTION STARTED HERE ----


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

    # PLACEMENT LOGIC FOR BLUE_ZERO FIXTURES STARTED HERE


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
