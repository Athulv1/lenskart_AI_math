from __future__ import annotations
import subprocess
import sys
import os
import copy
import logging
import traceback
from typing import List, Dict, Any, Optional, Tuple, Iterable
from . import Fixture
from . import CV_Controller as cvCon
from . import DXF_Document as dxf_doc
import uuid 
import ezdxf # type: ignore
import json
from pathlib import Path
from ezdxf import units # type: ignore
from ezdxf.enums import InsertUnits # type: ignore
from ezdxf.math import Vec2, Vec3, Matrix44, BoundingBox2d, BoundingBox # type: ignore
from ezdxf.addons import Importer # type: ignore
from ezdxf.bbox import extents # type: ignore 
from ezdxf.colors import rgb2int # type: ignore
from ezdxf.path import make_path # type: ignore 
from ezdxf import const as DXFCONST # type: ignore
import math
from shapely.geometry import Point, Polygon, LinearRing, LineString, MultiLineString, MultiPoint, box, MultiPolygon # type: ignore
from shapely.ops import linemerge, polygonize, unary_union     # type: ignore
import shapely.affinity as affinity # type: ignore
import collections
from collections import defaultdict
import itertools 
from itertools import permutations, product
import random
from shapely.strtree import STRtree

logger = logging.getLogger("app")

class DXF_Controller:

    Point = Tuple[float, float]
    Segment = Tuple[Point, Point]
    Seg2D = Tuple[float, float, float, float]        # (x1, y1, x2, y2) mm
    Wall3D = Tuple[float, float, float, float, float]  # (x1, y1, x2, y2, height_mm)
    Seg2 = Tuple[Vec2, Vec2]

    DOOR_LAYER_NAME = "I-LK CURTAIN" # Define the identified layer name
    MM_PER_M = 1000.0
    WALL_THICKNESS = 200.0  # mm
    HATCH_LAYER = "LENS_HATCH_WALL"
    MERGE_TOL = 1.0
    
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
        self.docs = [dxf_doc.DXF_Document(0)]
        # self.doc = ezdxf.new(dxfversion='R2010', units=units.MM)
        # self.doc.header['$ACADVER'] = 'AC1024'  # R2010
        # self.doc.header['$INSUNITS'] = 4       # mm
        self.fixtures = fixtures


        # --- State variables that were in DossierParser ---
        self.fixtures = {} # This will be built by the new master method
        self.merch_data = {}
        self.parsed_counts = {}
        self.family_totals = {}
        # --- End of DossierParser state variables ---
        #--RASHEEQUE-EDITED-THE-LINE-04/12/2025--
        # --- OPTIMIZATION: Fixture Library ---
        self.fixture_library = {} # <--- ADD THIS LINE

        self.safe_types = {
            "LINE", "LWPOLYLINE", "CIRCLE", "ARC", "TEXT", "MTEXT",
            "ELLIPSE", "SPLINE", "SOLID", "INSERT", "ATTDEF"
        }

        

    # ==============================================================================
    # --- START: ALL METHODS FROM DossierParser ARE NOW PART OF DXF_Controller ---
    # ==============================================================================
    # touched
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

    # touched
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

    # touched
    def generate_fixture_counts(self) -> Tuple[Dict[str, int], Dict[str, int]]:
        """
        Main public method to generate the INITIAL counts from the dossier.
        (This function remains unchanged)
        """
        print("--- Generating INITIAL Fixture Counts from DossierParser instance ---")
        floor_fixtures = self._setup_floor_fixtures()
        print("✅ Dossier INITIAL COUNTING Complete.")
        return self.family_totals, floor_fixtures
    
    # touched
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
    
    # touched
    def calculate_greeter_to_standing_table_zone(self, doc) -> Optional[Polygon]:
        """
        Calculates the usable area between the bottom of the standing tables and the top of the QMS/greeter desks.

        This function identifies the collective bounding boxes of both fixture groups,
        creates a slicing box representing the vertical space between them, and intersects
        it with the main floorplan polygon to find the actual area.

        Returns:
            A Shapely Polygon representing the valid placement zone, or None if the zone
            cannot be calculated (e.g., fixtures are missing or space is invalid).
        """

        print("\n--- 📐 Calculating Zone Between Greeter and Standing Tables ---")

        # --- 1. Find Anchor Fixtures ---
        standing_table_entities = [e for e in doc.msp.query('INSERT') if "STANDING_TABLE" in e.dxf.name.upper()]
        qms_entities = [e for e in doc.msp.query('INSERT') if "QMS_DESK" in e.dxf.name.upper()]

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
    
    # touched
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

    # touched
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

            # if proto_value <= 12:
            if proto_value < 12:
                clinic_counts["ROC_clinic"] = 1
                clinic_counts["Clinic_with_sink"] = 1

            elif proto_value < 16:
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

    # touched
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

    # touched
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
        
    
    #

    # ============================================================================
    # --- END: METHODS FROM DossierParser ---
    # ============================================================================

    # touched
    def create_floorplan(self,debug=False):
        
        # print("walls:")
        # for c in self.cvc.plan_final:
        #     print(c)
        # print("\n\n")
        # print("doors:")
        # for c in self.cvc.doors:
        #     print(c)
        # print("\n\n")
        # print("windows:")
        # for c in self.cvc.windows:
        #     print(c)
        # print("\n\n")
        # self.draw_walls_debug(self.docs[0].msp, self.cvc.plan_final)
        # self.draw_doors_debug(self.docs[0].msp, self.cvc.doors, 1)
        # self.draw_doors_debug(self.docs[0].msp, self.cvc.windows, 80)

        self.corners = self.cvc.corners
        self.docs[0].doc.header["$LTSCALE"] = 1.0      # global scale
        self.docs[0].doc.header["$PSLTSCALE"] = 1      # paper-space scaling behavior

        # for key,val in self.cvc.plan_final.items():
        #     print(key, val)
        
        self.outline_segments = self.draw_outline(self.docs[0], self.cvc.plan_final, self.cvc.doors, self.cvc.windows)

        self.draw_shutter(self.docs[0])

        #---RASHEEQUE--EDITED--11-12-2025
        # CHANGE: Filter hatch segments to exclude the main door wall (front wall)
        # - Increased boundary tolerance from 3mm to 100mm to catch all wall segments after rotation/transformation
        # - Added front_wall_id check to identify and exclude segments on the main door wall from hatching
        # - Only the bottom wall (mainDoorWallId) should have no hatch pattern for door placement
        hatch_segs = []
        front_wall_id = self.cvc.front_wall_id
        
        print(f"\n=== HATCH FILTERING DEBUG ===")
        print(f"Total outline_segments: {len(self.outline_segments)}")
        print(f"Front wall ID: {front_wall_id}")
        if front_wall_id and front_wall_id in self.cvc.plan_final:
            front_wall = self.cvc.plan_final[front_wall_id]
            print(f"Front wall coords: {front_wall}")
        
        excluded_count = 0
        boundary_filtered = 0
        # Increased tolerance from 3 to 100mm to catch wall segments that may be slightly off due to rotation/transformations
        boundary_tolerance = 100.0
        for a, b in self.outline_segments:
            res = self.segment_along_polygon_edge(self.corners, (a, b), boundary_tolerance)
            if res["is_along_boundary"]:
                boundary_filtered += 1
                # Check if this segment belongs to the front wall
                is_front_wall = False
                if front_wall_id and front_wall_id in self.cvc.plan_final:
                    front_wall = self.cvc.plan_final[front_wall_id]
                    fx1, fy1, fx2, fy2 = front_wall[0], front_wall[1], front_wall[2], front_wall[3]
                    
                    # Check if segment (a, b) lies on the front wall line
                    # Use tolerance for floating point comparison
                    tolerance = 50.0  # 50mm tolerance for wall matching
                    seg_on_wall = self.is_segment_on_wall_line(a, b, (fx1, fy1, fx2, fy2), tolerance)
                    if seg_on_wall:
                        is_front_wall = True
                        excluded_count += 1
                        print(f"  EXCLUDED: {a} -> {b}")
                
                # Only add to hatch if it's NOT the front wall
                if not is_front_wall:
                    hatch_segs.append((a,b))
            else:
                print(f"  NOT ON BOUNDARY (filtered out): {a} -> {b}")
        
        print(f"Segments marked as on_boundary: {boundary_filtered}/{len(self.outline_segments)}")
        print(f"Total segments excluded from front wall: {excluded_count}")
        print(f"Total segments for hatch: {len(hatch_segs)}")
        print(f"=== END DEBUG ===\n")

        self.draw_hatch(self.docs[0], hatch_segs, rotation_angle=self.cvc.rotation_angle)

        # self.draw_shutter(self.docs[0])

        self.floorplan_polygon = self.points_to_polygon(self.corners)
        self.validation_hull_polygon = self.floorplan_polygon.convex_hull

        #--RASHEEQUE--EDITING--STARTS---HERE---01-12-2025
        # ---------------------------------------------------------
        # NEW: Detect Pillars automatically as part of floorplan creation
        # ---------------------------------------------------------
        # This registers them as obstacles immediately on the main doc
        self.detect_and_register_pillars(self.docs[0], debug=debug)
        # ---------------------------------------------------------
        #--RASHEEQUE--EDITING--ENDS---HERE---01-12-2025


        #--RASHEEQUE--ADDED---HERE---04-12-2025
        # --- [OPTIMIZATION] Build the Static Obstacle Tree HERE ---
        # This ensures it's ready before any placement logic runs
        self.build_static_obstacle_tree(self.docs[0])

    #---RASHEEQUE--EDITED--11-12-2025
    # CHANGE: Added helper method to check if a segment lies on a specific wall line
    # - Checks both perpendicular distance to wall line (within tolerance)
    # - Verifies segment is within wall's extent (not just on infinite line extension)
    # - Used to identify and exclude front wall segments from hatching
    def is_segment_on_wall_line(self, p1: Point, p2: Point, wall: Tuple[float, float, float, float], tolerance: float) -> bool:
        """
        Check if a segment (p1, p2) lies on the wall line AND within the wall's extent.
        
        Args:
            p1: First point of segment (x, y)
            p2: Second point of segment (x, y)
            wall: Wall coordinates (x1, y1, x2, y2)
            tolerance: Distance tolerance in mm
            
        Returns:
            True if both segment endpoints lie on the wall line AND within wall bounds
        """
        x1, y1, x2, y2 = wall
        
        # Wall vector and length
        wall_dx = x2 - x1
        wall_dy = y2 - y1
        wall_len_sq = wall_dx * wall_dx + wall_dy * wall_dy
        
        if wall_len_sq < 1e-10:  # Degenerate wall
            return False
        
        wall_len = math.sqrt(wall_len_sq)
        
        # Check both segment points
        for px, py in [p1, p2]:
            # Vector from wall start to point
            dx = px - x1
            dy = py - y1
            
            # Project point onto wall line (parameter t along wall)
            t = (dx * wall_dx + dy * wall_dy) / wall_len_sq
            
            # Check if projection falls WITHIN the wall segment (not just on the infinite line)
            # Add small margin for endpoints
            margin = tolerance / wall_len
            if t < -margin or t > 1.0 + margin:
                return False
            
            # Calculate perpendicular distance to wall line
            proj_x = x1 + t * wall_dx
            proj_y = y1 + t * wall_dy
            perp_dist = math.sqrt((px - proj_x)**2 + (py - proj_y)**2)
            
            if perp_dist > tolerance:
                return False
        
        return True

    # touched
    def draw_walls_debug(self, msp, walls_dict, color=7, layer_name="WALLS_DEBUG"):
        """
        Draws all wall segments in white for debugging.
        walls_dict: {"wall_id": [x1, y1, x2, y2], ...}  (all in mm)
        """
        for wall_id, (x1, y1, x2, y2) in walls_dict.items():
            msp.add_line(
                (x1, y1, 0.0),
                (x2, y2, 0.0),
                dxfattribs={
                    "layer": layer_name,
                    "color": color,   # white (AutoCAD color index)
                },
            )

    # touched
    def draw_doors_debug(self, msp, doors_list, color=1, layer_name="DOORS_DEBUG"):
        """
        Draws all doors in red as simple line segments between (x,z) coordinates.
        doors_list: list of {"start":[x, y, z], "end":[x, y, z], ...} (all in mm)
        """
        for d in doors_list:
            sx, sz = float(d["start"][0]), float(d["start"][2])
            ex, ez = float(d["end"][0]),   float(d["end"][2])
            msp.add_line(
                (sx, sz, 0.0),
                (ex, ez, 0.0),
                dxfattribs={
                    "layer": layer_name,
                    "color": color,   # red (AutoCAD color index)
                    "lineweight": 211
                },
            )

    # touched
    def draw_outline(self, doc, walls, doors, windows):

        msp = doc.msp

        all_segments = []
        for wall_id, w in walls.items():
            x1, y1, x2, y2 = w
            wall_len = self.wall_length(w)

            # Gather cutouts from doors/windows
            cuts = []
            for obj in doors + windows:
                if obj["wall"] == wall_id:
                    s = obj["start"]
                    e = obj["end"]
                    t1 = self.project_point_onto_wall(s[0], s[2], w)
                    t2 = self.project_point_onto_wall(e[0], e[2], w)
                    cuts.append((min(t1, t2), max(t1, t2)))

            merged_cuts = self.merge_intervals(cuts)

            # Compute solid segments
            solid_segments = []
            cursor = 0.0
            for start, end in merged_cuts:
                if start > cursor:
                    solid_segments.append((cursor, start))
                cursor = end
            if cursor < 1.0:
                solid_segments.append((cursor, 1.0))

            # Draw each remaining wall segment
            for t0, t1 in solid_segments:
                sx = x1 + (x2 - x1) * t0
                sy = y1 + (y2 - y1) * t0
                ex = x1 + (x2 - x1) * t1
                ey = y1 + (y2 - y1) * t1
                msp.add_line((sx, sy), (ex, ey), dxfattribs={"layer": "WALLS"})
                all_segments.append(((sx, sy), (ex, ey)))
    
        # Optional: draw door/window lines for reference
        for obj in doors:
            door_width = self.wall_length((obj["start"][0], obj["start"][2], obj["end"][0], obj["end"][2]))
            pts = self.rectangle_from_segment_outside(self.corners, ((obj["start"][0], obj["start"][2]), (obj["end"][0], obj["end"][2])), 20, 0.1)
            if pts:
                pts.append(pts[0])
                if door_width > 1000: # glazing 
                    lw = doc.msp.add_lwpolyline(pts, dxfattribs={"color": 150, "layer": "Glass-FrontGlazing"}, format="xy", close=True)
                else:
                    print("regular door")
                    if "DASHED" not in doc.doc.linetypes:
                        doc.doc.linetypes.new("DASHED", dxfattribs={"description": "Dashed __ __ __", "pattern": [0.75, 0.5, -0.25]})
                    lw = doc.msp.add_lwpolyline(pts, dxfattribs={"color": 160, "linetype": "DASHED", "layer": self.DOOR_LAYER_NAME}, format="xy", close=True)

        # # for obj in windows:
        #     msp.add_line((obj["start"][0], obj["start"][2]), (obj["end"][0], obj["end"][2]),
        #                 dxfattribs={"color": 5, "layer": "WINDOWS"})

        return all_segments
    

    def draw_shutter_n(self, doc):
        
        def find_bottom_chain(pts, slope_tol=0.05, y_tol=100):
            n = len(pts)
            ys = [p[1] for p in pts]
            min_y = min(ys)
            print("min_y", min_y)
            is_bottom = [False] * n
            for i in range(n):
                p1, p2 = pts[i], pts[(i + 1) % n]
                dy, dx = p2[1] - p1[1], p2[0] - p1[0]
                near_min = (abs(p1[1] - min_y) <= y_tol) and (abs(p2[1] - min_y) <= y_tol)
                slope_ok = abs(dy) <= slope_tol * max(1.0, abs(dx))
                if near_min and slope_ok:
                    is_bottom[i] = True
            return is_bottom

        is_facade_segment = find_bottom_chain(self.corners, slope_tol=0.05, y_tol=10)
        
        facade_points = []
        for i, is_facade in enumerate(is_facade_segment):
            if is_facade:
                # Add both the start and end point of the facade segment
                facade_points.append(self.corners[i])
                facade_points.append(self.corners[(i + 1) % len(self.corners)])


        print(facade_points)

        shutter_pts = self.rectangle_from_segment_outside(self.corners, facade_points, 100, 0.1)
        shutter_pts.append(shutter_pts[0])
        res = []
        for p in shutter_pts[:-1]:
            # print(p)
            if p[0] != facade_points[0][0] and p[1] != facade_points[0][1] and p[0] != facade_points[1][0] and p[1] != facade_points[1][1]:
                res.append(p)
        # print(res)
        lw = doc.msp.add_lwpolyline(res, dxfattribs={"color": 1, "layer": "Rolling Shutter"}, format="xy")

    #---RASHEEQUE--EDITED--12-12-2025
    # CHANGE: Updated draw_shutter to use mainDoorWallId (front_wall_id) instead of minimum Y coordinate
    # - Now correctly identifies facade wall using front_wall_id from CV_Controller
    # - Works with rotated floor plans where facade isn't necessarily at minimum Y
    def draw_shutter(self, doc):
        
        print("\n=== SHUTTER DRAWING DEBUG ===")
        # Get front wall (facade) from mainDoorWallId
        front_wall_id = self.cvc.front_wall_id
        print(f"Front wall ID: {front_wall_id}")
        
        if not front_wall_id or front_wall_id not in self.cvc.plan_final:
            print(f"❌ Warning: Could not find front wall '{front_wall_id}' for shutter placement")
            return
        
        # Get facade wall coordinates
        front_wall = self.cvc.plan_final[front_wall_id]
        fx1, fy1, fx2, fy2 = front_wall[0], front_wall[1], front_wall[2], front_wall[3]
        print(f"Front wall coords: ({fx1}, {fy1}) -> ({fx2}, {fy2})")
        
        # Facade points are the start and end of the front wall
        facade_points = [(fx1, fy1), (fx2, fy2)]
        print(f"Facade points: {facade_points}")
        
        # Create shutter rectangle extending 100mm outward from facade
        shutter_pts = self.rectangle_from_segment_outside(self.corners, tuple(facade_points), 100, 0.1)
        print(f"Shutter points from rectangle_from_segment_outside: {shutter_pts}")
        
        if not shutter_pts or len(shutter_pts) < 4:
            print(f"❌ Warning: Could not create shutter rectangle for facade")
            return
        
        # The rectangle has 4 points: [p1, p2, p2_out, p1_out]
        # We want only the outer 2 points (p2_out, p1_out) to form the shutter box
        # Points at index 2 and 3 are the outer points
        if len(shutter_pts) >= 4:
            res = [shutter_pts[2], shutter_pts[3]]  # Just the two outer points
            print(f"Outer shutter points: {res}")
            
            lw = doc.msp.add_lwpolyline(res, dxfattribs={"color": 1, "layer": "Rolling Shutter"}, format="xy")
            print(f"✅ Shutter drawn successfully with {len(res)} points")
        else:
            print(f"❌ Not enough points to draw shutter")
        print("=== END SHUTTER DEBUG ===\n")


    def draw_shutter_test_outer_plan(self, doc):
        
        def find_bottom_chain(pts, slope_tol=0.05, y_tol=100):
            n = len(pts)
            ys = [p[1] for p in pts]
            min_y = min(ys)
            is_bottom = [False] * n
            for i in range(n):
                p1 = pts[i]
                p2 = pts[(i + 1) % n]
                dy = abs(p1[1] - p2[1])
                dx = abs(p1[0] - p2[0])
                slope = dy / dx if dx > 0 else float('inf')
                avg_y = (p1[1] + p2[1]) / 2
                if slope < slope_tol and (avg_y - min_y) < y_tol:
                    is_bottom[i] = True
            return is_bottom

        is_facade_segment = find_bottom_chain(self.corners, slope_tol=0.05, y_tol=100)
        facade_points = []
        for i, is_facade in enumerate(is_facade_segment):
            if is_facade:
                facade_points.append(self.corners[i])
                facade_points.append(self.corners[(i + 1) % len(self.corners)])
                break

        # --- FIX: Check if facade_points is valid before proceeding ---
        if not facade_points or len(facade_points) < 2:
            print("  -> Warning: No valid facade segment found for shutter drawing.")
            return
        # --------------------------------------------------------------

        shutter_pts = self.rectangle_from_segment_outside(self.corners, facade_points, 100, 0.1)
        shutter_pts.append(shutter_pts[0])
        res = []
        for p in shutter_pts[:-1]:
            # print(p)
            if p[0] != facade_points[0][0] and p[1] != facade_points[0][1] and p[0] != facade_points[1][0] and p[1] != facade_points[1][1]:
                res.append(p)
        # print(res)
        lw = doc.msp.add_lwpolyline(res, dxfattribs={"color": 1, "layer": "Rolling Shutter"}, format="xy")


    # touched
    def wall_length(self, w):
        x1, y1, x2, y2 = w
        return math.hypot(x2 - x1, y2 - y1)
    
    # touched
    def project_point_onto_wall(self, px, py, w):
        x1, y1, x2, y2 = w
        wx, wy = x2 - x1, y2 - y1
        wall_len2 = wx**2 + wy**2
        t = ((px - x1) * wx + (py - y1) * wy) / wall_len2
        return max(0.0, min(1.0, t))  # clamp to [0,1]

    # touched
    def merge_intervals(self, intervals):
        if not intervals:
            return []
        intervals = sorted(intervals)
        merged = [intervals[0]]
        for start, end in intervals[1:]:
            last_start, last_end = merged[-1]
            if start <= last_end:
                merged[-1] = (last_start, max(last_end, end))
            else:
                merged.append((start, end))
        return merged
    
        
    # touched
    def rectangle_from_segment_outside(self, 
        polygon: List[Point],
        segment: Tuple[Point, Point],
        depth: float,
        tol: float = 1e-6,
    ) -> List[Point]:
        """
        Given:
        - polygon: ordered list of vertices (closed or open; last will be connected to first)
        - segment: ((x0,y0),(x1,y1)) lying on one polygon edge (possibly a sub-portion)
        - depth: outward offset distance (e.g., 10)
        Returns four points [s0, s1, s1_out, s0_out], forming the outside rectangle.
        Raises ValueError if the segment does not lie on exactly one polygon edge.
        """
        if depth <= 0:
            raise ValueError("depth must be positive")

        s0, s1 = segment
        # debug = False
        # if s0[0] == 1949.8460128624397 and s1[0]== 1805.952169243366:
        #     debug = True
        # if debug:
        #     print("True")

        # Find which polygon edge the segment sits on
        # edge_index: Optional[int] = None
        # n = len(polygon)
        # for i in range(n):
        #     a = polygon[i]
        #     b = polygon[(i+1) % n]
        #     # if debug and a[0] == 1949.846 and b[0] == 1805.952:
        #     #     print(1)
        #     #     one = self._segment_lies_on_edge(s0, s1, a, b, tol, debug)
        #     #     print(2)
        #     #     two = self._segment_lies_on_edge(s1, s0, a, b, tol, debug)
        #     #     print(one, two)
        #     # else:
        #     if self._segment_lies_on_edge(s0, s1, a, b, tol) or self._segment_lies_on_edge(s1, s0, a, b, tol):
        #         edge_index = i
        #         break

        # if edge_index is None:
        #     print("Segment does not lie on any polygon edge (within tolerance).:, ", segment, "\n", polygon)
        #     return None

        # Edge direction
        # a = polygon[edge_index]
        # b = polygon[(edge_index+1) % n]
        a = s0
        b = s1
        e = self._sub(b, a)
        elen = self._norm(e)
        if elen < tol:
            print("Degenerate polygon edge.")
            return None
            
        ex, ey = (e[0]/elen, e[1]/elen)

        # Determine polygon winding
        area = self._signed_area(polygon)
        # For CCW polygons, the OUTSIDE is the right side of each directed edge (a->b).
        # Right normal = (ey, -ex); Left normal = (-ey, ex)
        if area > 0:   # CCW
            nx, ny = (ey, -ex)           # outward normal
        else:          # CW
            nx, ny = (-ey, ex)           # outward normal

        # Offset vector (depth along outward normal)
        dn = (nx*depth, ny*depth)

        # Return rectangle in a consistent loop
        p0_out = self._add(s0, dn)
        p1_out = self._add(s1, dn)

        # Order as [s0, s1, s1_out, s0_out] which is a simple quad with no self-cross
        return [s0, s1, p1_out, p0_out]
    
    # touched
    def _segment_lies_on_edge(self, s0: Point, s1: Point, a: Point, b: Point, tol: float, debug=False) -> bool:
        # Both endpoints must lie on the same polygon edge
        # print(s0, s1, a, b)
        return self._is_point_on_segment_door(s0, a, b, tol, debug) and self._is_point_on_segment_door(s1, a, b, tol, debug) 

    def _is_point_on_segment_door(self, p: Point, a: Point, b: Point, tol: float, debug=False) -> bool:
        
        # a = [a[0]]
        ab = self._sub(b, a)
        ap = self._sub(p, a)
        # if debug:
        #     print("\t", )
        #     print("\t", a)
        #     print("\t", b)
        #     print("\t", p)
        #     print("\t", ab)
        #     print("\t", ap)
        # Collinearity via cross product magnitude
        cross = abs(ab[0]*ap[1] - ab[1]*ap[0])
        if cross > tol * max(1.0, self._norm(ab)):
            return False
        # Within segment bounds via dot products
        dot1 = self._dot(ap, ab)
        dot2 = self._dot(self._sub(p, b), self._sub(a, b))
        return dot1 >= -tol and dot2 >= -tol   
        
    def _signed_area(self, poly: List[Point]) -> float:
        return 0.5 * sum(
            poly[i][0]*poly[(i+1)%len(poly)][1] - poly[(i+1)%len(poly)][0]*poly[i][1]
            for i in range(len(poly))
        )

    def _norm(self, v: Point) -> float:
        return math.hypot(v[0], v[1])

    def _sub(self, a: Point, b: Point) -> Point:
        # print(a, b)
        return (a[0]-b[0], a[1]-b[1])

    def _add(self, a: Point, b: Point) -> Point:
        return (a[0]+b[0], a[1]+b[1])

    def _mul(self, v: Point, s: float) -> Point:
        return (v[0]*s, v[1]*s)

    def _dot(self, a: Point, b: Point) -> float:
        return a[0]*b[0] + a[1]*b[1]
    
    def _cross(self, a: Point, b: Point) -> float:
        return a[0]*b[1] - a[1]*b[0]
    
    # touched
    def points_to_polygon(self, points):
        if len(points) < 3:
            raise ValueError("A polygon requires at least 3 points")

        # Ensure closure (Shapely will auto-close, but this avoids ambiguity)
        if points[0] != points[-1]:
            points = points + [points[0]]

        return Polygon(points)
    
    # touched
    def unit(self, v): 
        l = v.magnitude;  return v / l if l else v
    
    # touched
    def right_normal(self, v): return Vec2(v.y, -v.x)
    
    # touched
    def left_normal(self, v):  return Vec2(-v.y, v.x)
    
    # touched
    def line_intersection(self, p, r, q, s):
        rxs = r.x * s.y - r.y * s.x
        if abs(rxs) < 1e-9: return None, False
        t = ((q - p).x * s.y - (q - p).y * s.x) / rxs
        return p + r * t, True
    
    # touched
    def miter_offset_open_polyline(self, points, offset, outward_is_right=True, miter_limit=20.0):
        pts = [Vec2(p) for p in points]
        
        if len(pts) < 2: return [tuple(p) for p in pts]
        
        dirs = [self.unit(pts[i+1]-pts[i]) for i in range(len(pts)-1)]
        normals = [self.right_normal(d) if outward_is_right else self.left_normal(d) for d in dirs]
        out_pts = [pts[0] + normals[0]*offset]
        
        for i in range(1, len(pts)-1):
            
            d_prev, d_next = dirs[i-1], dirs[i]
            n_prev, n_next = normals[i-1], normals[i]
            
            pA, rA = pts[i] + n_prev*offset, d_prev
            pB, rB = pts[i] + n_next*offset, d_next
            ip, ok = self.line_intersection(pA, rA, pB, rB)
            
            if ok and (ip - pts[i]).magnitude < miter_limit*offset:
                out_pts.append(ip)
            else:
                out_pts.append(pA); out_pts.append(pB)

        out_pts.append(pts[-1] + normals[-1]*offset)
        return [tuple(p) for p in out_pts]

    # touched
    def chain_touching_segments(self, segments, tol=1e-4):
        # returns runs = [[p0,p1,...], ...]
        from collections import defaultdict
        def key(p): return (round(p[0]/tol)*tol, round(p[1]/tol)*tol)
        ptmap = defaultdict(list)
        for i,(a,b) in enumerate(segments):
            ptmap[key(a)].append((i,0)); ptmap[key(b)].append((i,1))
        used = [False]*len(segments); runs=[]
        for i,(a,b) in enumerate(segments):
            if used[i]: continue
            used[i]=True; run=[a,b]
            # fwd
            cur=b
            while True:
                k=key(cur); nxt=None
                for si,_ in ptmap[k]:
                    if not used[si]: nxt=si; break
                if nxt is None: break
                used[nxt]=True
                na,nb=segments[nxt]
                if key(na)==k: run.append(nb); cur=nb
                else: run.append(na); cur=na
            # back
            cur=a
            while True:
                k=key(cur); nxt=None
                for si,_ in ptmap[k]:
                    if not used[si]: nxt=si; break
                if nxt is None: break
                used[nxt]=True
                na,nb=segments[nxt]
                if key(nb)==k: run.insert(0,na); cur=na
                else: run.insert(0,nb); cur=nb
            runs.append(run)
        return runs

    # touched
    def signed_area(self, poly):
        a=0.0
        for (x1,y1),(x2,y2) in zip(poly, poly[1:]+poly[:1]):
            a += x1*y2 - x2*y1
        return 0.5*a

    # touched
    def _k(self, p, tol=MERGE_TOL):
        return (round(p[0]/tol)*tol, round(p[1]/tol)*tol)

    # touched
    def merge_runs_at_junctions(self, runs, tol=MERGE_TOL):
        """ Merge runs that meet at endpoints, repeatedly, so a single run can
            turn corners instead of stopping there.
        """
        changed = True
        while changed:
            changed = False
            # index endpoints
            ends = {}
            for i, r in enumerate(runs):
                if len(r) < 2: continue
                ends.setdefault(self._k(r[0], tol), []).append((i, "start"))
                ends.setdefault(self._k(r[-1], tol), []).append((i, "end"))

            # try to merge pairs that share a keyed point
            for kp, arr in list(ends.items()):
                if len(arr) < 2:
                    continue
                # pick two different runs to merge
                (i1, s1), (i2, s2) = arr[0], arr[1]
                if i1 == i2:
                    continue

                r1, r2 = runs[i1], runs[i2]
                # orient them so the shared endpoint is r1 tail and r2 head
                if s1 == "start": r1 = list(reversed(r1))
                if s2 == "end":   r2 = list(reversed(r2))
                # ensure exact shared point (snap) to avoid tiny gaps
                joint = ((self._k(r1[-1], tol)[0], self._k(r1[-1], tol)[1]))
                r1[-1] = joint
                r2[0]  = joint

                merged = r1 + r2[1:]
                # replace in array: put merged at i1, blank i2
                runs[i1] = merged
                runs[i2] = []
                changed = True
                break  # rebuild index from scratch
            # compact
            runs = [r for r in runs if r]
        return runs

    # touched
    def add_corner_patch_if_needed(self, hatch, runA, runB, outerA, outerB, tol=MERGE_TOL):
        """ If runA end touches runB start (or vice versa), add a tiny wedge patch.
            patch ring: [inner_corner, outerA_corner, outerB_corner]
        """
        a_end = runA[-1]; b_start = runB[0]
        a_start = runA[0]; b_end = runB[-1]
        patch_pts = None
        if self._k(a_end,tol) == self._k(b_start,tol):
            patch_pts = (a_end, outerA[-1], outerB[0])
        elif self._k(b_end,tol) == self._k(a_start,tol):
            patch_pts = (b_end, outerB[-1], outerA[0])
        if patch_pts:
            ring = [patch_pts[0], patch_pts[1], patch_pts[2], patch_pts[0]]
            hatch.paths.add_polyline_path(ring, is_closed=True,
                                        flags=DXFCONST.BOUNDARY_PATH_EXTERNAL)

    def _collinear(self, p: Point, a: Point, b: Point, tol: float) -> bool:
        ax, ay = a[0]-p[0], a[1]-p[1]
        bx, by = b[0]-p[0], b[1]-p[1]
        return abs(self._cross((ax, ay), (bx, by))) <= tol

    def _point_on_segment(self, p: Point, a: Point, b: Point, tol: float) -> bool:
        # collinear and within bounding box
        if not self._collinear(p, a, b, tol):
            return False
        minx, maxx = (a[0], b[0]) if a[0] <= b[0] else (b[0], a[0])
        miny, maxy = (a[1], b[1]) if a[1] <= b[1] else (b[1], a[1])
        return (p[0] >= minx - tol and p[0] <= maxx + tol and
                p[1] >= miny - tol and p[1] <= maxy + tol)

    def _param_on_segment(self, p: Point, s: Segment) -> float:
        # return parameter t in [0,1] of p projected onto segment s (assumes collinear & within bounds)
        (x1, y1), (x2, y2) = s
        dx, dy = x2 - x1, y2 - y1
        # choose axis with larger magnitude for stability
        if abs(dx) >= abs(dy):
            return 0.0 if abs(dx) < 1e-30 else (p[0] - x1) / dx
        else:
            return 0.0 if abs(dy) < 1e-30 else (p[1] - y1) / dy

    def segment_along_polygon_edge(
        self, 
        polygon: List[Point],
        segment: Segment,
        tol: float = 1e-9
    ) -> Dict:
        """
        Returns:
        {
            'is_along_boundary': bool,               # True if the entire segment lies on the polygon boundary
            'supporting_edges': List[int],           # indices of polygon edges touched (edge i is from polygon[i] to polygon[i+1 mod n])
            'touch_points': List[Point],             # sorted points where segment meets polygon vertices (including endpoints)
            'reason': str                            # explanation if False
        }
        """
        n = len(polygon)
        if n < 2:
            return {'is_along_boundary': False, 'supporting_edges': [], 'touch_points': [], 'reason': 'Polygon too small.'}

        sA, sB = segment
        if (abs(sA[0]-sB[0]) <= tol and abs(sA[1]-sB[1]) <= tol):
            return {'is_along_boundary': False, 'supporting_edges': [], 'touch_points': [], 'reason': 'Degenerate segment.'}

        # 1) Quick reject: both endpoints must lie on the polygon boundary (some edge)
        def point_on_any_edge(p: Point) -> List[int]:
            hit = []
            for i in range(n):
                a = polygon[i]
                b = polygon[(i+1) % n]
                if self._point_on_segment(p, a, b, tol):
                    hit.append(i)
            return hit

        hits_A = point_on_any_edge(sA)
        hits_B = point_on_any_edge(sB)
        if not hits_A or not hits_B:
            return {'is_along_boundary': False, 'supporting_edges': [], 'touch_points': [], 'reason': 'Endpoint not on boundary.'}

        # 2) Gather all polygon vertices that lie on the segment, plus the segment endpoints.
        on_seg_vertices = []
        for i in range(n):
            v = polygon[i]
            if self._point_on_segment(v, sA, sB, tol):
                on_seg_vertices.append(v)

        # Include segment endpoints explicitly
        pts = on_seg_vertices + [sA, sB]

        # Deduplicate points within tol
        def uniq(points: List[Point]) -> List[Point]:
            out = []
            for p in points:
                if not any(abs(p[0]-q[0]) <= tol and abs(p[1]-q[1]) <= tol for q in out):
                    out.append(p)
            return out

        pts = uniq(pts)

        # 3) Sort these points along the segment parameter t
        pts_sorted = sorted(pts, key=lambda P: self._param_on_segment(P, segment))

        # 4) For each consecutive pair, check that their midpoint lies on SOME polygon edge
        supporting_edges = set()
        for i in range(len(pts_sorted)-1):
            p = pts_sorted[i]
            q = pts_sorted[i+1]
            # skip zero-length intervals (can happen when a vertex coincides with endpoint)
            if abs(p[0]-q[0]) <= tol and abs(p[1]-q[1]) <= tol:
                continue
            mid = ((p[0]+q[0])*0.5, (p[1]+q[1])*0.5)
            found_edge = False
            for e in range(n):
                a = polygon[e]
                b = polygon[(e+1) % n]
                if self._point_on_segment(mid, a, b, tol):
                    supporting_edges.add(e)
                    found_edge = True
                    break
            if not found_edge:
                return {
                    'is_along_boundary': False,
                    'supporting_edges': sorted(supporting_edges),
                    'touch_points': pts_sorted,
                    'reason': 'A portion of the segment is not on any edge.'
                }


        # Determine polygon segment endpoints:
        # Use the sorted touch_points, but snap to polygon vertices if endpoints lie on them
        poly_pts = on_seg_vertices[:]  # only polygon vertices on the segment

        # Determine the two extreme boundary points along the segment
        first_pt = pts_sorted[0]
        last_pt = pts_sorted[-1]

        # If endpoint matches a polygon vertex (within tol), use the exact vertex
        def snap_to_vertex(p):
            for v in polygon:
                if abs(p[0]-v[0]) <= tol and abs(p[1]-v[1]) <= tol:
                    return v
            return p

        seg_start = snap_to_vertex(first_pt)
        seg_end = snap_to_vertex(last_pt)

        polygon_segment = (seg_start, seg_end)


        # If we reached here, every subsegment lies on some polygon edge
        return {
            'is_along_boundary': True,
            'supporting_edges': sorted(supporting_edges),
            'touch_points': pts_sorted,
            'polygon_segment': polygon_segment,
            'reason': 'Entire segment lies on the polygon boundary.'
        }
    
    # touched
    #---RASHEEQUE--EDITED--11-12-2025
    # CHANGE: Added rotation_angle parameter to draw_hatch method
    # - Receives the floor plan rotation angle from CV_Controller
    # - Used to adjust hatch pattern angle to match floor plan orientation
    def draw_hatch(self, doc, all_segments, rotation_angle=0.0):
        """
        Draw wall hatches with pattern aligned to the floor plan rotation.
        rotation_angle: The rotation applied to the entire floor plan (in degrees)
        """
        def polyline_length(run):
            # run: [ (x,y), (x,y), ... ]
            return sum((Vec2(b) - Vec2(a)).magnitude for a, b in zip(run, run[1:]))
    
        # --- 1) Build the ORIGINAL perimeter (no cuts) and get its winding ---
        # full_perimeter_segs = [((w[0],w[1]), (w[2],w[3])) for w in self.cvc.plan_final.values()]
        full_perimeter_segs = []
        for idx, c in enumerate(self.corners):
            full_perimeter_segs.append(((c), (self.corners[(idx+1)%len(self.corners)])))

        outer_runs = self.chain_touching_segments(full_perimeter_segs)
        # assume one main loop; pick the longest run by chord length
        # outer = max(outer_runs, key=lambda r: sum(Vec2(b)-Vec2(a) for a,b in zip(r,r[1:])).magnitude)
        # outer = max(outer_runs, key=lambda r: (sum((Vec2(b) - Vec2(a)) for a, b in zip(r, r[1:]), start=Vec2(0, 0))).magnitude )
        outer = max(outer_runs, key=polyline_length)
        orientation_ccw = self.signed_area(outer) > 0  # CCW => True

        # --- 2) Build your solid (post-cut) segments as before, but keep direction as original (t0<t1) ---
        solid_segments_world = all_segments

        # --- 3) Chain solids into runs ---
        runs = self.chain_touching_segments(solid_segments_world, tol=self.MERGE_TOL)

        # 2) Merge runs that meet at corners so the band turns corners cleanly
        runs = self.merge_runs_at_junctions(runs, tol=self.MERGE_TOL)

        # 3) Build the hatch rings as before; keep a cache so we can patch any residual corner joints
        hatch = doc.msp.add_hatch()
        hatch.dxf.solid_fill = 0
        hatch.dxf.layer = self.HATCH_LAYER
        hatch.dxf.color = 250  # ACI: light gray
        hatch.dxf.true_color = rgb2int((120, 120, 120))  # Optional: matching RGB gray
        hatch.set_pattern_fill('ANSI32', scale=10)
        #---RASHEEQUE--EDITED--11-12-2025
        # CHANGE: Adjust hatch pattern angle based on floor plan rotation
        # - Was hardcoded to 90 degrees
        # - Now adds rotation_angle to keep hatch perpendicular to walls after floor plan rotation
        # - Example: if floor rotated -45°, hatch angle = 90 + (-45) = 45°
        hatch.dxf.pattern_angle = 90 + rotation_angle

        built = []  # store (run, outer) for optional corner patches
        # print(len(runs))

        for run in runs:
            if len(run) < 2:
                continue

            # decide outward side as in the previous message (global orientation logic)
            if orientation_ccw:
                outward_is_right = True   # CCW  interior left  outside right
            else:
                outward_is_right = False  # CW  interior right  outside left

            # make the outward offset with generous miter limit to avoid bevels on tight angles
            outer = self.miter_offset_open_polyline(run, self.WALL_THICKNESS, outward_is_right=outward_is_right, miter_limit=50.0)

            # ring between inner run and its outer offset
            ring = []
            ring.extend(run)
            ring.append(outer[-1])              # short cap
            ring.extend(reversed(outer))
            ring.append(run[0])                 # short cap back
            hatch.paths.add_polyline_path(ring, is_closed=True, flags=DXFCONST.BOUNDARY_PATH_EXTERNAL)

            def closed_no_dup(pts):
                pts = [tuple(p) for p in pts]
                if len(pts) > 1 and pts[0] == pts[-1]:
                    pts = pts[:-1]  # lwpolyline(close=True) will close it for us
                return pts

            outline_layer = "HATCH_OUTLINE"

            # ring is the same list you pass to hatch.paths.add_polyline_path(...)
            doc.msp.add_lwpolyline(
                closed_no_dup(ring),
                format="xy",
                close=True,
                dxfattribs={"layer": outline_layer, "lineweight": 25, "color": 7},
            )

            built.append((run, outer))

        # 4) (Optional) Corner patch in case two separate runs still meet at a corner
        #    This is rarely needed if merge_runs_at_junctions succeeded, but it guarantees no tiny gaps.
        for i in range(len(built)):
            for j in range(i+1, len(built)):
                runA, outerA = built[i]
                runB, outerB = built[j]
                self.add_corner_patch_if_needed(hatch, runA, runB, outerA, outerB, tol=self.MERGE_TOL)
    

    def _is_overlapping_raw(self, fixture_bbox, obstacles):
        """
        [OPTIMIZED] Raw float comparison for collision detection.
        Returns True if fixture_bbox overlaps with any box in obstacles.
        Treats touching edges (exactly equal coordinates) as NOT overlapping (valid).
        """
        fx_min_x, fx_min_y, fx_max_x, fx_max_y = fixture_bbox
        
        for b in obstacles:
            # b is tuple (minx, miny, maxx, maxy)
            # Overlap occurs only if ALL 4 separation checks fail:
            # 1. Right of fixture < Left of obstacle
            # 2. Left of fixture > Right of obstacle
            # 3. Top of fixture < Bottom of obstacle
            # 4. Bottom of fixture > Top of obstacle
            
            # Using strict inequalities (<, >) allows items to touch edges (flush).
            if (fx_min_x < b[2] and fx_max_x > b[0] and 
                fx_min_y < b[3] and fx_max_y > b[1]):
                return True
        return False
    
    # touched
    def get_existing_nonwall_bboxes(self):
        """
        Returns bounding boxes of all non-wall fixtures in the DXF drawing.
        """
        for doc in self.docs:
            bboxes = []
            for entity in doc.msp:
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
            doc.placed_bboxes = bboxes  

    # touched
    def _get_accurate_obstacle_bboxes(self, include_all=False, debug=False):
        """
        Returns accurate bounding boxes for fixtures.
        If include_all is False, it returns only 'clinic', 'boh', 'boh_preset', and 'Eye_massage_area' types.
        If include_all is True, it returns all fixtures.
        NOW INCLUDES the RETAIL_SEPARATOR line as a mandatory obstacle.
        """
        for doc in self.docs:
            
            bboxes = []
            msp = doc.msp
            
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
                    # if debug:
                        # print(f"&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&fixture_type: {fixture_type}, best_match_key: {best_match_key}")
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

            # print(f"✅ Found {len(bboxes)} obstacles to avoid.")
            doc.placed_bboxes = bboxes

    # touched
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
    
########################################################################################################################
########################################################################################################################
##############################################       HELPERS       #####################################################
##############################################       HELPERS       #####################################################
##############################################       HELPERS       #####################################################
########################################################################################################################
########################################################################################################################

    # touched
    def entities_intersecting_line(self, entities: Iterable[Any],
                                    p0: Vec2, p1: Vec2) -> List[Any]:


        def bbox2(seg) -> Tuple[float, float, float, float]: # type: ignore
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

        def segseg_intersects(s1, s2) -> bool: # type: ignore
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

        def segments_from_entity_2d(e):
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

    def get_outer_rect_corners_shapely(self, insert, flatten_dist=0.5, debug=False):
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

    def build_static_obstacle_tree(self, doc):
        """
        [OPTIMIZATION] Builds a spatial index (STRtree) for static obstacles like
        internal partitions and the retail separator line.
        This runs ONCE, allowing validation to check these items instantly later.
        """
        print("--- 🌳 Building Spatial Index for Static Obstacles ---")
        static_polygons = []

        # 1. Add Internal Partitions
        # We fetch them once here instead of inside the loop
        partitions = self.cvc.get_internal_wall_partitions(min_length=50, max_length=3500, thickness=200)
        if partitions:
            for p in partitions:
                # p is usually (minx, miny, maxx, maxy) or similar dict
                if isinstance(p, dict): p = p.get('bbox')
                if p and len(p) >= 4:
                    static_polygons.append(box(p[0], p[1], p[2], p[3]))

        # 2. Add Retail Separator Line (as a thin box)
        separator_line = doc.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
        if separator_line:
            s = separator_line.dxf.start
            e = separator_line.dxf.end
            # Create a 10mm thick buffer around the line
            line_poly = LineString([(s.x, s.y), (e.x, e.y)]).buffer(5.0)
            static_polygons.append(line_poly)

        # 3. Build and Store
        if static_polygons:
            from shapely.strtree import STRtree
            doc.static_obstacle_polygons = static_polygons
            doc.static_obstacle_tree = STRtree(static_polygons)
            print(f"  -> Indexed {len(static_polygons)} static obstacles in Tree.")
        else:
            print("  -> No static obstacles found to index.")


########################################################################################################################
########################################################################################################################
##############################################      CLINIC         #####################################################
##############################################      CLINIC         #####################################################
##############################################      CLINIC         #####################################################
########################################################################################################################
########################################################################################################################

    def orchestrate_clinic_placement(self, debug=False):
        """
        Orchestrates the complete top row clinic placement workflow.
        
        [MODIFIED] Now checks the result from detect_back_corner_room.
        - If a 'middle' room is found, it uses its returned segments directly.
        - Otherwise, it proceeds with the standard top-wall analysis.
        
        Args:
            all_placed_bboxes: List of existing obstacle bounding boxes
            debug (bool): If True, draws debug visualizations and prints debug info
        
        Returns:
            dict: Contains all relevant data from the placement process:
                - back_room_location: Location of detected back room
                - partition_x: X-coordinate of partition
                - raw_top_wall_zones: Raw zones from wall analysis
                - new_clinic_segments: Distributed clinic segments
                - all_ranked_plans: All ranked clinic placement plans
                - remaining_clinics_queue: Queue of clinics not yet placed
                - top_10_ranked_plans: Top 10 ranked plans
        """
        
        # Debug visualizations
        if debug:
            self.draw_detected_room_for_validation(self.docs[0])
            self.draw__analyze_top_wall_with_bulge_detection_new(self.docs[0])
        
        # 1. Get the back room location first
        # --- MODIFICATION: The second return value is now generic 'room_data' ---
        back_room_location, room_data = self.detect_back_corner_room()
        print("Back room location found at" ,back_room_location)
        
        if debug:
            print(f"Back room detected at: {back_room_location}")

        # --- START OF NEW LOGIC BLOCK ---
        
        new_clinic_segments = {}
        raw_top_wall_zones = [] # Initialize as empty
        partition_x = None      # Initialize as None

        if back_room_location == 'middle':
            # --- MIDDLE ROOM ('U-Shape') PATH ---
            print("  -> Middle 'U-shape' room detected. Using its segments directly for clinic planning.")
            
            # The room_data *is* the segment dictionary.
            new_clinic_segments = room_data 
            
            # For debug drawing, we can extract the zones
            if debug and new_clinic_segments:
                 raw_top_wall_zones = list(new_clinic_segments.values())

        else:
            # --- CORNER ROOM ('L-Shape') OR NO ROOM PATH (Original Logic) ---
            if back_room_location in ['left', 'right']:
                print(f"  -> '{back_room_location}' room detected. Using standard top-wall analysis.")
                # The room_data *is* the partition_x coordinate.
                partition_x = room_data 
            else:
                print("  -> No back room detected. Using standard top-wall analysis.")
                # partition_x remains None

            # 2. Get the raw top wall zones, correctly filtered
            raw_top_wall_zones = self._analyze_top_wall_with_bulge_detection_new(
                small_bulge_max_width=1000, 
                small_bulge_max_depth=1000, 
                back_room_location=back_room_location, 
                partition_x=partition_x
            )
            
            # 3. Call the new distribution function
            new_clinic_segments = self.distribute_top_wall_segment(
                raw_top_wall_zones, 
                back_room_location
            )
        
        # --- END OF NEW LOGIC BLOCK ---
        
        # Debug visualization (this now works for both paths)
        if debug:
            # --- MODIFICATION: Pass self.docs[0] to the draw function ---
            self.draw_distributed_top_wall_segments(self.docs[0], new_clinic_segments)
            print("\n--- New clinic segments (post-detection/distribution) ---")
            # Use json.dumps for a cleaner print of Vec2 objects
            print(json.dumps(new_clinic_segments, indent=2, default=str)) 
            print("--- End of clinic segments --- \n")
        
        # 4. Call the new Best Ranker Planner
        if debug:
            print("\n--- 5. Calling plan_clinic_best_ranker() ---")
        
        # This call is UNCHANGED. It works perfectly because 'new_clinic_segments'
        # is in the correct format, regardless of which path was taken.
        all_ranked_plans, remaining_clinics_queue = self.plan_clinic_best_ranker(
            distributed_segments=new_clinic_segments,
            back_room_location=back_room_location
        )
        
        if debug:
            print("remaining_clinics after planning: ", remaining_clinics_queue)
        
        #---RASHEEQUE--MAKE--EDITS-HERE---03-12-2025
        # --- MODIFICATION: Limit the number of plans to consider ---
        # Instead of considering all plans, only take the top 2. This drastically
        # reduces the number of documents created and layouts processed.
        ranked_plans = all_ranked_plans[:2] if all_ranked_plans else []  # type: ignore
        # ranked_plans = all_ranked_plans[:10] if all_ranked_plans else []
        
        if debug:
            print("\n--- Top 10 Ranked Clinic Plans ---")
            print(json.dumps(ranked_plans, indent=2))
            print("--- End of Top 10 Ranked Clinic Plans --- \n")


        # --- NEW: Place next ranked plan and compute remaining clinics correctly ---
        # Build the full clinic queue (same ordering used by planner)
        clinic_config = self.fixtures.get("clinic_fixtures", {}) or {}
        full_clinic_queue = collections.deque([
            Fixture.Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"])
            for name, count in clinic_config.items() if count > 0 for _ in range(count)
        ])
        # Total clinics desired from config
        total_clinics_desired = len(full_clinic_queue)
        # Count clinics already placed before executing the ranked plan
        pre_existing_clinic_count = len([e for e in self.docs[0].msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()])

        doc_copy = self.docs[0].clone(len(self.docs))

        placed = False
        for i, layout in enumerate(ranked_plans[0:2]):
        # for i, layout in enumerate(ranked_plans[1:2]):
            placed = False
            doc = self.docs[-1]
            print(len(self.docs))
            print(f"{i}******************************************{layout}******************************************")
            if not placed:
                if not layout["Placed"]:
                    self.place_clinics_from_ranked_plan(doc, layout, new_clinic_segments)
                    
                    if layout["Placed"]:
                        print("placed...APPENDING new doc")

                        # Count clinics after placement
                        post_existing_clinic_count = len([e for e in doc.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()])
                        # number placed during this operation
                        placed_during_run = max(0, post_existing_clinic_count - pre_existing_clinic_count)
                        # remaining clinics = desired - total placed in drawing
                        remaining_clinic_count = max(0, total_clinics_desired - post_existing_clinic_count)
                        # Build a remaining queue consistent with original ordering (take from end)
                        if remaining_clinic_count > 0:
                            remaining_clinics_list = list(full_clinic_queue)[-remaining_clinic_count:]
                            remaining_clinics_queue = collections.deque(remaining_clinics_list)
                        else:
                            remaining_clinics_queue = collections.deque()
                            
                        print(f"  -> Placed {placed_during_run} clinics in this pass. Remaining clinics (desired - placed): {remaining_clinic_count}")

                        doc.clinic_placement_results = {
                            'back_room_location': back_room_location,
                            'partition_x': partition_x,
                            'raw_top_wall_zones': raw_top_wall_zones,
                            'new_clinic_segments': new_clinic_segments,
                            'all_ranked_plans': all_ranked_plans,
                            'remaining_clinics_queue': remaining_clinics_queue,
                            'top_10_ranked_plans': ranked_plans
                        }

                        placed = True
                        ranked_plans[i]["Placed"] = True
                        
                        self.docs.append(doc_copy.clone(len(self.docs)))
                        self.docs[-1].ind = len(self.docs) - 1
        if placed:
            self.docs = self.docs[:-1]
        
        #--RASHEEQUE--MAKE--EDITS-HERE--
        for doc in self.docs:
            #--- NEW: call the under-row placement helper ---

            #--RASHEEQUE--MAKE--EDITS-HERE--11-11-2025---
            # --- NEW LINES TO ADD (SNAPSHOT) ---
            current_queue = doc.clinic_placement_results.get("remaining_clinics_queue")
            if current_queue is None:
                current_queue = collections.deque()
                print(f"  -> No remaining queue for Doc {doc.ind}. Skipping.")
                continue
            # Store a snapshot of the *initial* remaining count from Plan A
            initial_remaining_count = len(current_queue)
            doc.clinic_placement_results["initial_remaining_clinic_count"] = initial_remaining_count
            print(f"  -> Storing initial remaining clinic count (from Plan A): {initial_remaining_count}")
            # --- END OF NEW LINES ---
            #--RASHEEQUE--MAKE--EDITS-HERE--11-11-2025---
            under_results = self.place_remaining_clinic_under(doc, debug=False)
            print("Under-row plan generated, remaining queue:", remaining_clinics_queue)


       
    
########################################################################################################################
##########################################      DRAW AND DEBUG FUNCTIONS         ########################################
########################################################################################################################

    def draw_detected_room_for_validation(self, doc, partition_min_length: float = 1000.0):
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
        if "DEBUG_ROOM_RED" not in doc.doc.layers: doc.doc.layers.add(name="DEBUG_ROOM_RED", color=1)
        if "DEBUG_ROOM_BLUE" not in doc.doc.layers: doc.doc.layers.add(name="DEBUG_ROOM_BLUE", color=5)
        if "DEBUG_ROOM_GREEN_DOT" not in doc.doc.layers: doc.doc.layers.add(name="DEBUG_ROOM_GREEN_DOT", color=3)
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
                doc.msp.add_line(p_line.coords[0], p_line.coords[1], dxfattribs={"layer": "DEBUG_ROOM_RED", "lineweight": 50})
                continue

            angle_diff_perp = abs((seg_angle_deg - (back_wall_angle_deg + 90) + 180) % 360 - 180)
            if angle_diff_perp < ANGLE_TOLERANCE:
                if avg_x <= left_zone_x_end:
                    blue_lines.append({'line': p_line, 'side': 'left'})
                    doc.msp.add_line(p_line.coords[0], p_line.coords[1], dxfattribs={"layer": "DEBUG_ROOM_BLUE", "lineweight": 50})
                elif avg_x >= right_zone_x_start:
                    blue_lines.append({'line': p_line, 'side': 'right'})
                    doc.msp.add_line(p_line.coords[0], p_line.coords[1], dxfattribs={"layer": "DEBUG_ROOM_BLUE", "lineweight": 50})

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
                            doc.msp.add_circle(center=intersection_point.coords[0], radius=200, dxfattribs={"layer": "DEBUG_ROOM_GREEN_DOT"})
        
        print("  -> Drawing complete. Check DXF for correctly filtered red/blue lines and green dots.")
    
    def draw__analyze_top_wall_with_bulge_detection_new(self, doc):
        """
        [DEBUG HELPER] Visualizes the segments created by _analyze_top_wall_with_bulge_detection_new()
        and prints their lengths in JSON format.
        """
        print("\n--- 🎨 Drawing Top Wall Analysis Zones for Validation ---")

        # 1. Call the analysis function to get the zones
        back_room_location, partition_x = self.detect_back_corner_room()
        placeable_zones = self._analyze_top_wall_with_bulge_detection_new(
            small_bulge_max_width=1000, 
            small_bulge_max_depth=1000,back_room_location=back_room_location, partition_x=partition_x
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
        if layer_name not in doc.doc.layers:
            doc.doc.layers.add(name=layer_name, color=6)  # ACI color 6 is Magenta

        # 3. Iterate through the zones and draw each one
        for i, zone in enumerate(placeable_zones):
            start_point = zone['start']
            end_point = zone['end']
            
            # Draw the line segment for the zone
            doc.msp.add_line(
                start_point, 
                end_point, 
                dxfattribs={"layer": layer_name, "lineweight": 70} # Use a thick lineweight
            )

            # Add a text label to identify the zone number
            mid_point = start_point.lerp(end_point)
            doc.msp.add_mtext(
                f"TOP_ZONE_{i+1}",
                dxfattribs={
                    'char_height': 150,
                    'insert': mid_point,
                    'layer': layer_name
                }
            )
        
        print(f"  -> ✅ Drew {len(placeable_zones)} top wall zones on layer '{layer_name}'.")

    def draw_distributed_top_wall_segments(self, doc, distributed_zones: dict):
        """
        [DEBUG HELPER] Draws the distributed top wall segments on the DXF plan.
        - "clinic_reserved" zones are drawn in GREEN.
        - "boh_reserved" zones are drawn in RED.
        """
        
        print("\n--- 🎨 Drawing Distributed Top Wall Segments (BOH vs. Clinic) ---")

        # 1. Define Layers and Colors
        clinic_layer = "DEBUG_ZONE_CLINIC_RESERVED"
        boh_layer = "DEBUG_ZONE_BOH_RESERVED"
        clinic_color = 3  # Green
        boh_color = 1     # Red

        # 2. Add layers to the document if they don't exist
        if clinic_layer not in doc.doc.layers:
            doc.doc.layers.add(name=clinic_layer, color=clinic_color)
            print(f"  -> Created layer: {clinic_layer} (Green)")
        if boh_layer not in doc.doc.layers:
            doc.doc.layers.add(name=boh_layer, color=boh_color)
            print(f"  -> Created layer: {boh_layer} (Red)")

        if not distributed_zones:
            print("  -> No zones to draw.")
            return

        # 3. Iterate through the dictionary and draw each zone
        drawn_count = 0
        for zone_id, zone_data in distributed_zones.items():
            try:
                # Get data from the zone dictionary
                # These are already Vec2 objects from the previous function
                p1 = zone_data['start']
                p2 = zone_data['end']
                reservation_type = zone_data['distribute_for']
                zone_length = zone_data['length']

                # Determine which layer and color to use
                if reservation_type == "boh_reserved":
                    layer_to_use = boh_layer
                else:
                    layer_to_use = clinic_layer
                
                # Draw the line segment
                doc.msp.add_line(p1, p2, dxfattribs={
                    "layer": layer_to_use,
                    "lineweight": 70  # Make it thick and visible
                })

                # Draw the text label
                mid_point = p1.lerp(p2)
                label_text = f"{zone_id} ({reservation_type})\n{zone_length:.0f}mm"
                
                doc.msp.add_mtext(label_text, dxfattribs={
                    'char_height': 150,
                    'insert': mid_point,
                    'layer': layer_to_use
                })
                drawn_count += 1

            except (KeyError, TypeError) as e:
                print(f"  -> ⚠️ WARNING: Could not draw zone '{zone_id}'. Invalid data: {e}")

        print(f"  -> ✅ Drew {drawn_count} distributed zones on debug layers.")

    def draw_under_row_placement_zones(self, doc, placed_clinics_on_top_wall):
        """
        [DEBUG HELPER] Visualizes the placement zones found by 
        _analyze_first_row_clinic_until_boh_last().
        """
        print("\n--- 🎨 Drawing 'Under First Row' Placement Zones for Validation ---")
        
        if not placed_clinics_on_top_wall:
            print("  -> No top-row clinics found to analyze.")
            return # <-- This function still returns None

        # 2. Call the analysis function to get the zones.
        placement_zones = self._analyze_first_row_clinic_until_boh_last(placed_clinics_on_top_wall)

        if not placement_zones:
            print("  -> No placement zones were found to draw.")
            return

        # 3. Create a new, highly visible layer for the debug drawing.
        layer_name = "DEBUG_UNDER_ROW_ZONES"
        if layer_name not in doc.doc.layers:
            doc.doc.layers.add(name=layer_name, color=3)  # ACI color 3 is Green

        # 4. Iterate through the zones and draw each one.
        for zone in placement_zones:
            start_point = Vec2(zone['start']) # Use Vec2 to ensure .lerp() exists
            end_point = Vec2(zone['end'])
            
            # Draw the line segment for the zone.
            doc.msp.add_line(
                start_point, 
                end_point, 
                dxfattribs={"layer": layer_name, "lineweight": 70}
            )

            # Add a text label to identify the zone.
            mid_point = start_point.lerp(end_point) # Use .lerp() for midpoint
            doc.msp.add_mtext(
                f"{zone['id']} ({zone['length']:.0f}mm)",
                dxfattribs={
                    'char_height': 150,
                    'insert': mid_point + Vec2(0, 100), # Use Vec2 for offset
                    'layer': layer_name
                }
            )
        
        print(f"  -> ✅ Drew {len(placement_zones)} 'under row' zones on layer '{layer_name}'.")

    def get_and_draw_boh_bottom_segment(self, doc, debug: bool = False) -> List[dict]:
        """
        [NEW ANALYSIS FUNCTION - V2 - UN-TRIMMED]
        1. Gets the RAW BOH wall perimeter path, skipping all trimming.
        2. Identifies the "bottom" segment(s) based on the lowest Y-coordinate.
        3. Returns them in the same format as _analyze_first_row_clinic_until_boh_last().
        4. If debug=True, draws the identified segments on a new debug layer.
        """
        # --- CACHING CHECK ---
        if doc.boh_bottom_segment is not None:
            # If debug is True, we might want to let it run to redraw lines,
            # otherwise return cache
            if not debug:
                return doc.boh_bottom_segment
        # ---------------------
        
        
        print("\n--- 🔎 Identifying BOH Bottom Wall Segment(s) (RAW / UN-TRIMMED) ---")
        
        # --- Step 1: Get the RAW perimeter path ---
        # This call bypasses all trimming logic (corners, pickup curtain)
        raw_perimeter_path = self._get_boh_perimeter_path_from_bottom_right_ccw(doc)
        
        if not raw_perimeter_path:
            print("  -> ⚠️ FAILED: Could not retrieve any BOH wall segments.")
            return []

        # --- Step 2: Convert raw (p1, p2) tuples to the dictionary format ---
        all_segments_list = []
        for p1, p2 in raw_perimeter_path:
            segment_vector = p2 - p1
            all_segments_list.append({
                'start_point': (p1.x, p1.y),
                'end_point': (p2.x, p2.y),
                'length': segment_vector.magnitude,
                'angle': math.degrees(segment_vector.angle)
            })

        # --- Step 3: Identify the "bottom" segments ---
        min_y = float('inf')
        for seg in all_segments_list:
            min_y = min(min_y, seg['start_point'][1], seg['end_point'][1])
            
        print(f"  -> Lowest Y-coordinate found at: {min_y:.0f}")

        # Collect all segments that lie along this bottom edge (with a tolerance)
        y_tolerance = 100.0  # 100mm tolerance
        bottom_segments_list = []
        for seg in all_segments_list:
            is_start_bottom = abs(seg['start_point'][1] - min_y) < y_tolerance
            is_end_bottom = abs(seg['end_point'][1] - min_y) < y_tolerance
            
            # A segment is "bottom" if both its points are near the min_y
            if is_start_bottom and is_end_bottom:
                bottom_segments_list.append(seg)
                
        if not bottom_segments_list:
            print("  -> ⚠️ FAILED: Could not isolate any bottom segments from the raw path.")
            return []
            
        print(f"  -> Found {len(bottom_segments_list)} raw bottom segment(s).")
        
        # --- Step 4: Format the output ---
        formatted_output = []
        for i, seg_data in enumerate(bottom_segments_list):
            p1 = Vec2(seg_data['start_point'])
            p2 = Vec2(seg_data['end_point'])
            
            start_pt_vec, end_pt_vec = (p1, p2) if p1.x < p2.x else (p2, p1)
            
            formatted_output.append({
                "id": f"boh_bottom_raw_{i}",
                "start": (start_pt_vec.x, start_pt_vec.y),
                "end": (end_pt_vec.x, end_pt_vec.y),
                "length": seg_data['length'],
                "angle": seg_data['angle']
            })
            
        # --- Step 5: Visualize if debug=True ---
        if debug:
            layer_name = "DEBUG_BOH_BOTTOM_SEGMENT_RAW"
            if layer_name not in doc.doc.layers:
                doc.doc.layers.add(name=layer_name, color=3) # Green
            
            print(f"  -> 🎨 Drawing {len(formatted_output)} raw bottom segments on layer '{layer_name}'...")
            
            for seg in formatted_output:
                start_pt = seg['start']
                end_pt = seg['end']
                
                doc.msp.add_line(
                    start_pt, 
                    end_pt, 
                    dxfattribs={"layer": layer_name, "lineweight": 70}
                )
                
                mid_point = Vec2(start_pt).lerp(Vec2(end_pt))
                doc.msp.add_mtext(
                    f"{seg['id']} ({seg['length']:.0f}mm)",
                    dxfattribs={
                        'char_height': 150,
                        'insert': mid_point,
                        'layer': layer_name
                    }
                )

        # [BEFORE RETURN]
        doc.boh_bottom_segment = formatted_output
        return formatted_output
        # return formatted_output
    
    #--raasheeque--ADDED A NEW FUNCTION--11-11-2025--
    def place_clinic_under_segment(
            self, 
            doc: "dxf_doc.DXF_Document", 
            segment_data: dict, 
            clinic_queue: collections.deque
        ) -> bool:
            """
            [NEW SIMPLE PLACER - V2]
            Attempts to place a single clinic from the queue under a given segment.
            - If segment length >= 2600mm, it tries to place one 'Horizontal' clinic.
            - If segment length >= 1700mm, it tries to place one 'Vertical' clinic.
            
            [FIX] Now places the clinic FLUSH with the BOH wall (not overlapping)
            to avoid colliding with the pickup_table.
            """
            
            print(f"\n--- Trying to place clinic under segment {segment_data.get('id')} ---")
            
            # --- 1. Check if there are clinics to place ---
            if not clinic_queue:
                print("  -> FAILED: Clinic queue is empty.")
                return False
                
            clinic_to_place = clinic_queue[0] # "Peek" at the next clinic
            
            # --- 2. Get Clinic & Segment Geometry ---
            try:
                # --- FIX: Removed the '+ 100' ---
                length = segment_data['length'] + 100
                p1 = Vec2(segment_data['start'])
                p2 = Vec2(segment_data['end'])
                segment_angle = segment_data['angle']
                
                wall_vector = (p2 - p1).normalize()
                
                inward_normal = wall_vector.orthogonal().normalize()
                if inward_normal.y > 0:
                    inward_normal *= -1
                    
            except (KeyError, TypeError) as e:
                print(f"  -> FAILED: Segment data is invalid: {e}")
                return False

            # --- 3. Determine Orientation based on Length ---
            H_WIDTH = clinic_to_place.width  # 2600
            H_HEIGHT = clinic_to_place.height # 1700 (This is the depth)
            V_WIDTH = clinic_to_place.height # 1700
            V_HEIGHT = clinic_to_place.width  # 2600 (This is the depth)
            
            fixture_width, fixture_height, rotation, orientation = 0, 0, 0, None
            
            # --- FIX: Only attempt 'H' (shallow) placement ---
            # A 2600mm-deep 'V' clinic will almost always fail validation here.
            # We should only place the 1700mm-deep 'H' clinic.
            
            if length >= H_WIDTH:
                # orientation = 'H'
                orientation = 'V'
                # fixture_width = H_WIDTH
                # fixture_height = H_HEIGHT # Use 1700mm depth
                # rotation = segment_angle
                fixture_width = V_WIDTH   # 1700 (Width along segment)
                
                # *** THIS IS THE FIX ***
                # Force the depth to be H_HEIGHT (1700), NOT V_HEIGHT (2600)
                fixture_height = H_HEIGHT  
                print("    -> Using 'V' orientation (1700W) but shallow 'H' depth (1700D).")
                
                rotation = segment_angle + 90
                center_on_wall = p1.lerp(p2, 0.3) 
            # --- REMOVED 'elif' FOR 'V' CLINIC ---
            # By removing the 'V' clinic option, we prevent the 2600mm depth problem.
            # The 1772mm segment will now correctly fail this check, as it's
            # not wide enough for an 'H' clinic (which needs 2600mm).
                
            # --- START OF A BETTER FIX ---
            # Let's keep the 'V' clinic logic but FIX the depth.
            # We will assume that any clinic placed here must be 1700mm deep.
                
            elif length >= V_WIDTH:
                orientation = 'V'
                fixture_width = V_WIDTH   # 1700 (Width along segment)
                
                # *** THIS IS THE FIX ***
                # Force the depth to be H_HEIGHT (1700), NOT V_HEIGHT (2600)
                fixture_height = H_HEIGHT  
                print("    -> Using 'V' orientation (1700W) but shallow 'H' depth (1700D).")
                
                rotation = segment_angle + 90
                center_on_wall = p1.lerp(p2, 0.5)
                
            # --- END OF BETTER FIX ---
                
            else:
                print(f"  -> FAILED: Segment length ({length:.0f}mm) is too short for any clinic.")
                return False
                
            print(f"  -> Segment length {length:.0f}mm qualifies for a '{orientation}' clinic (Depth: {fixture_height}mm).")

            # --- 4. Calculate Placement Position ---
            
            # --- FIX: Place it 800mm *below* the BOH segment ---
            # This provides 800mm of space for the pickup table and its aisle.
            margin_from_segment = 500.0 
            
            # center_on_wall = p1.lerp(p2, 0.3) 
            # center_on_wall = p1.lerp(p2, 0.5) 
            
            target_center = center_on_wall + inward_normal * (margin_from_segment + fixture_height / 2)

            # --- 5. Validate and Place ---
            new_bbox = self._validate_under_segment(
                doc,
                clinic_to_place,
                target_center,
                rotation,
                doc.placed_bboxes, # Check against all existing obstacles
                force=False
            )
            
            # --- 6. Finalize ---
            if new_bbox:
                doc.placed_bboxes.append(new_bbox)
                clinic_queue.popleft() 
                print(f"  -> ✅ SUCCESS: Placed one '{orientation}' clinic under the segment.")
                return True
            else:
                print(f"  -> FAILED: The spot for the '{orientation}' clinic was blocked or outside the floorplan.")
                return False


    def _validate_under_segment(self, doc, fixture, target_center, angle_deg, placed_bboxes, force=False):
        """
        Validates and places a fixture. On success, it returns the new bounding box tuple.
        On failure, it returns None.
        """

        local_center = fixture.bounding_box.center
        transform = Matrix44.chain(
            Matrix44.translate(-local_center.x, -local_center.y, 0),
            Matrix44.z_rotate(math.radians(angle_deg)),
            Matrix44.translate(target_center.x, target_center.y, 0)
        )
        world_corners = list(transform.transform_vertices(fixture.bounding_box.rect_vertices()))
        fixture_polygon = Polygon([(p.x, p.y) for p in world_corners])
        # [OPTIMIZATION] Get raw bbox tuple
        aabb = BoundingBox2d(world_corners)
        fixture_bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)
        

        if force:
            is_inside = True
            is_overlapping = False
        else:
            is_inside = self.floorplan_polygon.contains(fixture_polygon.centroid)
            #--RASHEEQUE-EDITED-THE-LINE-04/12/2025--
            is_overlapping = self._is_overlapping_raw(fixture_bbox_tuple, placed_bboxes)
            # is_overlapping = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)


        if is_inside and not is_overlapping:
            rotated_offset = local_center.rotate(math.radians(angle_deg))
            final_insert_point = target_center - rotated_offset
            doc.place_fixture(fixture, (final_insert_point.x, final_insert_point.y + 50, 0), angle_deg, True)
            
            # new_bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)
            # --- THIS LINE IS REMOVED ---
            # placed_bboxes.append(new_bbox_tuple) 
            # return new_bbox_tuple # Return the bbox on success
            return fixture_bbox_tuple
            
        return None

        
    #--raasheeque--edited--11-11-2025--
########################################################################################################################
############################################        HELPER FUNCTIONS       #############################################
########################################################################################################################


    
    #--RASHEEQUE--EDITED---09-11
    def detect_back_corner_room(
        self, 
        partition_min_length: float = 1000.0, 
        debug: bool = False  # <-- ADDED: Debug flag parameter
    ) -> Tuple[Optional[str], Any]:
        """
        [MODIFIED v10] Fixes the "Undefined line type DASHED" error
        by explicitly defining the 'DASHED' linetype in the document
        if it does not already exist, before creating the debug layer.
        
        [USER-CORRECTED] Fixes the 'U-shape' coordinate logic to correctly
        use the (x, y) from the *same* point for distance calculation.
        
        [DEBUG-FLAG] All layer creation and drawing operations are
        now conditional on the 'debug=True' flag.
        """
        # --- CACHING CHECK ---
        # Architecture is global, so we check the master doc (docs[0])
        if self.docs[0].back_corner_room_details is not None:
            if debug: print("  -> [CACHE HIT] Using cached back room details.")
            return self.docs[0].back_corner_room_details
        # ---------------------
        print("\n--- 🔍 Detecting Back Room (Corners & Middle) [v10] ---")


        #----RASHEEQUE--REDITED---HERE----
        # +++ START OF NEW FAST-PATH LOGIC +++
        print("  -> ℹ️ Trying fast-path door detection first...")

        doc = self.docs[0]
        
        # Call the helper function that returns the (str, float) tuple
        door_result_tuple = self.detect_corner_room_by_door(doc)
        
        if door_result_tuple[0] is not None:
            print(f"  -> ✅ OVERRIDE: Fast-path door detection found a '{door_result_tuple[0]}' room. Using this result.")
            # Return immediately if a door is found
            return door_result_tuple
        else:
            print("  -> ℹ️ Fast-path door detection found nothing. Proceeding with wall-based detection...")
        # +++ END OF NEW FAST-PATH LOGIC +++
        #----RASHEEQUE--REDITED---HERE----

        

        candidate_partitions = self.cvc.get_internal_wall_partitions(min_length=1000, max_length=3000, thickness=0.0)
        if not candidate_partitions: return (None, None)

        BOUNDARY_TOLERANCE = 150.0
        internal_partitions = [p for p in candidate_partitions if self.floorplan_polygon.boundary.distance(LineString([(p[0], p[1]), (p[2], p[3])]).centroid) > BOUNDARY_TOLERANCE]

        if len(internal_partitions) < 2:
            print("  -> Not enough true internal partitions for detection.")
            return (None, None)
        
        top_wall_zones = self._analyze_top_wall_with_bulge_detection_new()
        if not top_wall_zones:
            print("  -> ⚠️ Could not determine main back wall orientation. Aborting detection.")
            return (None, None)
        
        p1_ref, p2_ref = top_wall_zones[0]['start'], top_wall_zones[0]['end']
        back_wall_angle_deg = math.degrees((p2_ref - p1_ref).normalize().angle)
        print(f"  -> Main back wall orientation detected at {back_wall_angle_deg:.1f}°")

        min_x, max_x, min_y, max_y = self.cvc.min_x, self.cvc.max_x, self.cvc.min_y, self.cvc.max_y
        width, height = max_x - min_x, max_y - min_y
        
        back_zone_y_start = max_y - (height * 0.40)
        left_zone_x_end = min_x + (width * 0.25)
        right_zone_x_start = max_x - (width * 0.25)
        print(f"  -> Corner zones defined (Left < {left_zone_x_end:.0f}, Right > {right_zone_x_start:.0f})")
        
        doc = self.docs[0] 
        
        if debug:  # <-- ADDED: Wrap all layer creation
            if "DEBUG_ROOM_RED" not in doc.doc.layers: doc.doc.layers.add(name="DEBUG_ROOM_RED", color=1)
            if "DEBUG_ROOM_BLUE" not in doc.doc.layers: doc.doc.layers.add(name="DEBUG_ROOM_BLUE", color=5)
            if "DEBUG_ROOM_GREEN_DOT" not in doc.doc.layers: doc.doc.layers.add(name="DEBUG_ROOM_GREEN_DOT", color=3)
            
            # +++ START OF FIX (v10) +++
            if "DEBUG_ROOM_DIST_LINES" not in doc.doc.layers:
                # 1. Define the linetype if it doesn't exist
                if 'DASHED' not in doc.doc.linetypes:
                    doc.doc.linetypes.add(
                        name='DASHED',
                        pattern=[200.0, -100.0], # 200mm dash, 100mm gap
                        description="Dashed line __ __"
                    )
                # 2. Now it is safe to create the layer
                doc.doc.layers.add(name="DEBUG_ROOM_DIST_LINES", color=6, linetype="DASHED") # Magenta, Dashed
            # +++ END OF FIX (v10) +++

        red_lines = []
        blue_lines_corner = []
        blue_lines_middle = []
        
        ANGLE_TOLERANCE = 25.0 
        print(f"  -> Using wide ANGLE_TOLERANCE of {ANGLE_TOLERANCE}°")

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
                if debug:  # <-- ADDED
                    doc.msp.add_line(p_line.coords[0], p_line.coords[1], dxfattribs={"layer": "DEBUG_ROOM_RED", "lineweight": 50})
                continue

            angle_diff_perp = abs((seg_angle_deg - (back_wall_angle_deg + 90) + 180) % 360 - 180)
            if angle_diff_perp < ANGLE_TOLERANCE:
                line_added = False  # <-- Helper var to avoid multiple debug checks
                if avg_x <= left_zone_x_end:
                    blue_lines_corner.append({'line': p_line, 'side': 'left'})
                    line_added = True
                elif avg_x >= right_zone_x_start:
                    blue_lines_corner.append({'line': p_line, 'side': 'right'})
                    line_added = True
                else:
                    blue_lines_middle.append({'line': p_line, 'side': 'middle'})
                    line_added = True
                
                if line_added and debug: # <-- ADDED (Consolidated check)
                    doc.msp.add_line(p_line.coords[0], p_line.coords[1], dxfattribs={"layer": "DEBUG_ROOM_BLUE", "lineweight": 50})


        print(f"  -> Found {len(red_lines)} red (parallel) lines.")
        print(f"  -> Found {len(blue_lines_corner)} blue (perp) lines in CORNERS.")
        print(f"  -> Found {len(blue_lines_middle)} blue (perp) lines in MIDDLE.")

        # --- CHECK 1: Look for CORNER rooms ("L" shape) ---
        print("  -> Checking for 'L-shape' corner rooms...")
        for red_line in red_lines:
            buffered_red = red_line.buffer(150.0) 
            for blue_line_data in blue_lines_corner:
                blue_line = blue_line_data['line']
                
                if buffered_red.intersects(blue_line):
                    intersection_geom = buffered_red.intersection(blue_line)
                    if not intersection_geom.is_empty:
                        intersection_point = intersection_geom.centroid
                        distance_from_back_wall = max_y - intersection_point.y
                        if distance_from_back_wall > 600.0:
                            if debug:  # <-- ADDED
                                doc.msp.add_circle(center=intersection_point.coords[0], radius=200, dxfattribs={"layer": "DEBUG_ROOM_GREEN_DOT"})
                            side = blue_line_data['side']
                            partition_x_coord = (blue_line.coords[0][0] + blue_line.coords[1][0]) / 2
                            print(f"  -> ✅ Match found! Corner at y={intersection_point.y:.0f} is {distance_from_back_wall:.0f}mm from back wall.")
                            print(f"  -> Back corner room detected on the '{side}' side at X={partition_x_coord:.0f}.")
                            return (side, partition_x_coord)
                        else:
                            print(f"  -> ℹ️ Match ignored. Corner is only {distance_from_back_wall:.0f}mm from back wall.")
        
        print("  -> ℹ️ No valid back corner room pattern was detected.")

        # --- CHECK 2: Look for MIDDLE rooms ("U" shape) ---
        print("  -> Checking for 'U-shape' middle rooms...")
        if len(blue_lines_middle) < 2:
            print("  -> ℹ️ No middle room detected (not enough middle-zone blue lines).")
            # return (None, None)
            result = (None, None)
            self.docs[0].back_corner_room_details = result
            return result

        blue_lines_middle.sort(key=lambda b: (b['line'].coords[0][0] + b['line'].coords[1][0]) / 2)

        for red_line in red_lines:
            buffered_red = red_line.buffer(150.0)
            intersecting_blue_lines = []
            for blue_line_data in blue_lines_middle:
                if buffered_red.intersects(blue_line_data['line']):
                    intersecting_blue_lines.append(blue_line_data)
            
            if len(intersecting_blue_lines) >= 2:
                left_blue_line_data = intersecting_blue_lines[0]
                right_blue_line_data = intersecting_blue_lines[-1]
                
                left_blue_line = left_blue_line_data['line']
                right_blue_line = right_blue_line_data['line']

                # Get coords from the first point of the left line
                room_partition_bottom_left_x = left_blue_line.coords[0][0]
                room_partition_bottom_left_y = left_blue_line.coords[1][1] # <-- CORRECTED (Was [1][1])
                print(f"  -> Found potential 'U-shape' left start point at X~{room_partition_bottom_left_x:.0f}, Y~{room_partition_bottom_left_y:.0f}")

                # Get coords from the first point of the right line
                room_partition_bottom_right_x = right_blue_line.coords[0][0]
                room_partition_bottom_right_y = right_blue_line.coords[1][1] # <-- CORRECTED (Was [1][1])
                print(f"  -> Found potential 'U-shape' right start point at X~{room_partition_bottom_right_x:.0f}, Y~{room_partition_bottom_right_y:.0f}")

                room_left_corner_vec = Vec2(room_partition_bottom_left_x, room_partition_bottom_left_y)
                room_right_corner_vec = Vec2(room_partition_bottom_right_x, room_partition_bottom_right_y)
           

                room_left_x = (left_blue_line.coords[0][0] + left_blue_line.coords[1][0]) / 2
                room_right_x = (right_blue_line.coords[0][0] + right_blue_line.coords[1][0]) / 2

                int_left = buffered_red.intersection(left_blue_line)
                int_right = buffered_red.intersection(right_blue_line)
                
                if int_left.is_empty or int_right.is_empty:
                    print(f"  -> ℹ️ U-shape found but failed to get intersection centroid.")
                    continue 

                dist_left = max_y - int_left.centroid.y
                dist_right = max_y - int_right.centroid.y
                
                if dist_left > 600.0 and dist_right > 600.0:
                    print(f"  -> ✅ Match found! 'U-shape' room detected.")
                    print(f"   -> Left corner {dist_left:.0f}mm, Right corner {dist_right:.0f}mm from back wall.")
                    print(f"   -> Room X-Bounds: ({room_left_x:.0f}, {room_right_x:.0f})")
                    
                    if debug:  # <-- ADDED
                        doc.msp.add_circle(center=int_left.centroid.coords[0], radius=200, dxfattribs={"layer": "DEBUG_ROOM_GREEN_DOT"})
                        doc.msp.add_circle(center=int_right.centroid.coords[0], radius=200, dxfattribs={"layer": "DEBUG_ROOM_GREEN_DOT"})
                    
                    fp_top_left_vec = top_wall_zones[0]['start']
                    fp_top_right_vec = top_wall_zones[-1]['end']
                    
                    
                    dist_to_top_left = room_left_corner_vec.distance(fp_top_left_vec)
                    dist_to_top_right = room_right_corner_vec.distance(fp_top_right_vec)
                    
                    print(f"   -> 📏 DISTANCE (Room Left Corner to FP Top-Left): {dist_to_top_left:.0f}mm")
                    print(f"   -> 📏 DISTANCE (Room Right Corner to FP Top-Right): {dist_to_top_right:.0f}mm")

                    if debug:  # <-- ADDED
                        doc.msp.add_line(
                            room_left_corner_vec,
                            fp_top_left_vec,
                            dxfattribs={"layer": "DEBUG_ROOM_DIST_LINES"}
                        )
                        doc.msp.add_line(
                            room_right_corner_vec,
                            fp_top_right_vec,
                            dxfattribs={"layer": "DEBUG_ROOM_DIST_LINES"}
                        )
                        print("   -> 🎨 Drew distance lines on 'DEBUG_ROOM_DIST_LINES' layer.")

                    # --- START: New Return Logic for 'U-Shape' ---
                    
                    segment_1 = {
                        "start": room_left_corner_vec,
                        "end": fp_top_left_vec,
                        "length": dist_to_top_left
                    }
                    
                    segment_2 = {
                        "start": room_right_corner_vec,
                        "end": fp_top_right_vec,
                        "length": dist_to_top_right
                    }
                    
                    
                    if segment_1['length'] > segment_2['length']:
                        segment_1['distribute_for'] = "clinic_reserved"
                        segment_2['distribute_for'] = "boh_reserved"
                    else:
                        segment_1['distribute_for'] = "boh_reserved"
                        segment_2['distribute_for'] = "clinic_reserved"
                        
                    result_data = {
                        "Zone_1": segment_1,
                        "Zone_2": segment_2
                    }
                    
                    print("   -> ✅ Returning 'U-shape' room segments for distribution.")
                    
                    # return ('middle', result_data)
                    result = ('middle', result_data)
                    self.docs[0].back_corner_room_details = result
                    return result
                    
                    # --- END: New Return Logic ---
                else:
                    print(f"  -> ℹ️ U-shape ignored. Corners are too close to back wall (Left: {dist_left:.0f}mm, Right: {dist_right:.0f}mm).")

        print("  -> ℹ️ No valid middle room 'U-shape' pattern was detected.")


        result = (None, None)
        self.docs[0].back_corner_room_details = result
        return result
        # return (None, None)


    #--RASHEEQUE--ADDED--NEW--FUNCTION--09-11-2025
    def detect_toilet_room_door(self, doc) -> Optional[str]:
        """
        [NEW HELPER] Checks for a door on the 'I-LK CURTAIN' layer at the
        back of the store to provide a fast-path for room detection.

        Args:
            doc (DXF_Document): The document to query.

        Returns:
            Optional[str]: 'left', 'middle', 'right', or None if no valid door is found.
        """
        # --- CACHING CHECK ---
        if doc.toilet_room_door_detection is not None:
            return doc.toilet_room_door_detection
        # ---------------------
        print("\n--- 🚪 Checking for 'I-LK CURTAIN' door... ---")

        # 1. Find Door(s) on the specified layer
        # Note: self.DOOR_LAYER_NAME is "I-LK CURTAIN"
        door_entities = list(doc.msp.query(f'INSERT[layer=="{self.DOOR_LAYER_NAME}"]'))
        
        # You might also need to check for lines/polylines if the door
        # isn't an INSERT block. This is a more robust query:
        if not door_entities:
            door_entities = list(doc.msp.query(f'*[layer=="{self.DOOR_LAYER_NAME}"]'))

        # 2. Handle 'Not Found'
        if not door_entities:
            print("  -> No entities found on 'I-LK CURTAIN' layer.")
            return None

        # 3. Find Position (Centroid of all found entities)
        try:
            combined_bbox = extents(door_entities)
            if not combined_bbox.has_data:
                print("  -> Found 'I-LK CURTAIN' entities but could not calculate bounds.")
                return None
            
            door_centroid = combined_bbox.center
            print(f"  -> Found 'I-LK CURTAIN' centroid at (X={door_centroid.x:.0f}, Y={door_centroid.y:.0f})")

        except (RuntimeError, TypeError) as e:
            print(f"  -> Error calculating 'I-LK CURTAIN' bounds: {e}")
            return None
            
        # 4. Check Y-Position (Back of Store)
        # Use the floorplan's precise boundaries
        min_y, max_y = self.cvc.min_y, self.cvc.max_y
        height = max_y - min_y
        
        # Check if the door's center is in the top 20% of the floorplan
        top_20_percent_threshold = max_y - (height * 0.20)
        
        if door_centroid.y < top_20_percent_threshold:
            print(f"  -> Door is too low (Y={door_centroid.y:.0f}), not in the back 20% (Y > {top_20_percent_threshold:.0f}). Ignoring.")
            return None

        # 5. Check X-Position (Left/Middle/Right)
        min_x, max_x = self.cvc.min_x, self.cvc.max_x
        width = max_x - min_x
        
        left_zone_end_x = min_x + (width * 0.25)
        right_zone_start_x = max_x - (width * 0.25)

        if door_centroid.x < left_zone_end_x:
            print(f"  -> ✅ Door found in 'left' zone.")
            # return "left"
            result = "left"
            doc.toilet_room_door_detection = result
            return result
        elif door_centroid.x > right_zone_start_x:
            print(f"  -> ✅ Door found in 'right' zone.")
            # return "right"
            result = "right"
            doc.toilet_room_door_detection = result
            return result
        else:
            print(f"  -> ✅ Door found in 'middle' zone.")
            # return "middle"
            result = "middle"
            doc.toilet_room_door_detection = result
            return result

    #--RASHEEQUE--ADDED--NEW--FUNCTION--09-11-2025
    #--RASHEEQUE--EDITED--THE--FUNCTION--04-12-2025
    def detect_corner_room_by_door(self, doc) -> Tuple[Optional[str], Optional[float]]:
        """
        [NEW HELPER] Checks for a door on the 'I-LK CURTAIN' layer at the
        back corners to provide a fast-path for L-shape room detection.
        
        [MODIFIED] Returns the X-coordinate of the door's inner-facing edge
        (right edge for a left-side door, left edge for a right-side door).
        
        NOTE: This function will ignore 'middle' doors.

        Args:
            doc (DXF_Document): The document to query.

        Returns:
            Tuple[Optional[str], Optional[float]]: 
            - ('left', 12345.0) if a left door is found (the door's right X-coord).
            - ('right', 67890.0) if a right door is found (the door's left X-coord).
            - (None, None) if no valid *corner* door is found.
        """
        # --- CACHING CHECK ---
        if doc.corner_room_by_door_detection is not None:
            return doc.corner_room_by_door_detection
        # ---------------------
        print("\n--- 🚪 [HELPER] Checking for 'I-LK CURTAIN' corner door... ---")

        # 1. Find Door(s)
        door_entities = list(doc.msp.query(f'INSERT[layer=="{self.DOOR_LAYER_NAME}"]'))
        if not door_entities:
            door_entities = list(doc.msp.query(f'*[layer=="{self.DOOR_LAYER_NAME}"]'))

        # 2. Handle 'Not Found'
        if not door_entities:
            print("  -> [HELPER] No entities found on 'I-LK CURTAIN' layer.")
            # return (None, None)
            result = (None, None) 
            doc.corner_room_by_door_detection = result
            return result 

        # 3. Find Position (Centroid and Bounding Box)
        try:
            # --- MODIFICATION: We now need the full bbox, not just the center ---
            combined_bbox = extents(door_entities)
            if not combined_bbox.has_data:
                print("  -> [HELPER] Found 'I-LK CURTAIN' entities but could not calculate bounds.")
                # return (None, None)
                result = (None, None) 
                doc.corner_room_by_door_detection = result
                return result 
            
            door_centroid = combined_bbox.center
            print(f"  -> [HELPER] Found 'I-LK CURTAIN' centroid at (X={door_centroid.x:.0f}, Y={door_centroid.y:.0f})")

        except (RuntimeError, TypeError) as e:
            print(f"  -> [HELPER] Error calculating 'I-LK CURTAIN' bounds: {e}")
            # return (None, None)
            result = (None, None) 
            doc.corner_room_by_door_detection = result
            return result 
            
        # 4. Check Y-Position (Back of Store)
        min_y, max_y = self.cvc.min_y, self.cvc.max_y
        height = max_y - min_y
        
        top_20_percent_threshold = max_y - (height * 0.20)
        
        if door_centroid.y < top_20_percent_threshold:
            print(f"  -> [HELPER] Door is too low (Y={door_centroid.y:.0f}), not in the back 20%. Ignoring.")
            # return (None, None)
            result = (None, None) 
            doc.corner_room_by_door_detection = result
            return result 

        # 5. Check X-Position (Left/Middle/Right)
        min_x, max_x = self.cvc.min_x, self.cvc.max_x
        width = max_x - min_x
        
        left_zone_x_end = min_x + (width * 0.25)
        right_zone_x_start = max_x - (width * 0.25)

        # --- THIS IS THE NEW LOGIC YOU REQUESTED ---
        
        if door_centroid.x < left_zone_x_end:
            print(f"  -> ✅ [HELPER] Door found in 'left' zone. Returning override.")
            # Get the RIGHT edge (max_x) of the door's bounding box
            partition_x = combined_bbox.extmax.x + 280.0  # Slightly inset to avoid wall overlap
            print(f"    -> Using door's RIGHT edge as partition: X={partition_x:.0f}")
            # return ("left", partition_x) 
            result = ("left", partition_x) 
            doc.corner_room_by_door_detection = result
            return result
        
        elif door_centroid.x > right_zone_x_start:
            print(f"  -> ✅ [HELPER] Door found in 'right' zone. Returning override.")
            # Get the LEFT edge (min_x) of the door's bounding box
            partition_x = combined_bbox.extmin.x - 280.0  # Slightly inset to avoid wall overlap
            print(f"    -> Using door's LEFT edge as partition: X={partition_x:.0f}")
            # return ("right", partition_x)
            result = ("right", partition_x)
            doc.corner_room_by_door_detection = result
            return result
        
        else:
            print("  -> [HELPER] Door found in 'middle' zone. Ignoring (cannot proxy for U-shape).")
            # return (None, None) # Ignore 'middle'  
            result = (None, None) 
            doc.corner_room_by_door_detection = result
            return result 

    
    def _analyze_top_wall_with_bulge_detection_new(self, small_bulge_max_width=1000, small_bulge_max_depth=700, 
                                                 back_room_location=None, partition_x=None): # <-- ADD NEW ARGUMENTS
        """
        [MODIFIED] Performs a "smart walk" along the top wall.
        It now clips the segments based on the back_room_location and partition_x
        *before* analyzing them for bulges.
        """
        print("  -> Starting 'Smart Walk' analysis of top wall...")
        # # --- CACHING: Only cache the full, unfiltered analysis ---
        # if back_room_location is None and partition_x is None and self.docs[0].top_wall_zones is not None:
        #     print("  -> Using cached 'Smart Walk' analysis of top wall...")
        #     return self.docs[0].top_wall_zones
        # --- CACHING CHECK ---
        # We only cache if this is the "pure" analysis (no room clipping parameters passed)
        if back_room_location is None and partition_x is None and self.docs[0].top_wall_analysis is not None:
            print("  -> [CACHE HIT] Using cached 'Smart Walk' analysis.")
            return self.docs[0].top_wall_analysis
        # ---------------------
        
        # --- 1. ROBUST TOP WALL IDENTIFICATION (Unchanged) ---
        all_corners = self.cvc.corners
        if len(all_corners) < 3: return []
        all_segments = []
        for i in range(len(all_corners)):
            p1 = Vec2(all_corners[i])
            p2 = Vec2(all_corners[(i + 1) % len(all_corners)])
            all_segments.append((p1, p2))

        y_threshold = self.cvc.max_y - (self.cvc.max_y - self.cvc.min_y) * 0.20
        top_segments = []
        for p1, p2 in all_segments:
            if (p1.y + p2.y) / 2 > y_threshold:
                if abs(p1.y - p2.y) < abs(p1.x - p2.x) and p1.distance(p2) > 1700:
                    if p1.x > p2.x: p1, p2 = p2, p1
                    top_segments.append((p1, p2))
        
        if not top_segments:
            for p1, p2 in all_segments:
                if (p1.y + p2.y) / 2 > y_threshold and abs(p1.y - p2.y) < abs(p1.x - p2.x):
                    if p1.x > p2.x: p1, p2 = p2, p1
                    top_segments.append((p1, p2))
        
        top_segments.sort(key=lambda seg: seg[0].x)
        # --- END OF ROBUST IDENTIFICATION ---

        # --- 2. NEW: PRE-FILTER SEGMENTS BASED ON ROOM LOCATION ---
        filtered_top_segments = []
        if back_room_location == 'right' and partition_x is not None:
            clip_x = partition_x
            print(f"  -> Back-right room detected. Clipping segments to end before X={clip_x:.0f}")
            for p1, p2 in top_segments:
                if p2.x <= clip_x: # Segment is fully before the room
                    filtered_top_segments.append((p1, p2))
                elif p1.x < clip_x: # Segment crosses the room partition
                    print(f"    -> Clipping segment {p1.x:.0f}-{p2.x:.0f} at {clip_x:.0f}")
                    # Calculate new p2 at the partition line
                    t = (clip_x - p1.x) / (p2.x - p1.x)
                    new_p2_y = p1.y + (p2.y - p1.y) * t
                    new_p2 = Vec2(clip_x, new_p2_y)
                    if p1.distance(new_p2) > 1700: # Check if the remaining part is still long enough
                        filtered_top_segments.append((p1, new_p2))
            
        elif back_room_location == 'left' and partition_x is not None:
            clip_x = partition_x
            print(f"  -> Back-left room detected. Clipping segments to start after X={clip_x:.0f}")
            for p1, p2 in top_segments:
                if p1.x >= clip_x: # Segment is fully after the room
                    filtered_top_segments.append((p1, p2))
                elif p2.x > clip_x: # Segment crosses the room partition
                    print(f"    -> Clipping segment {p1.x:.0f}-{p2.x:.0f} at {clip_x:.0f}")
                    # Calculate new p1 at the partition line
                    t = (clip_x - p1.x) / (p2.x - p1.x)
                    new_p1_y = p1.y + (p2.y - p1.y) * t
                    new_p1 = Vec2(clip_x, new_p1_y)
                    if new_p1.distance(p2) > 1700: # Check if the remaining part is still long enough
                        filtered_top_segments.append((new_p1, p2))
        else:
            # No room detected, use all segments
            filtered_top_segments = top_segments

        # --- 3. "SMART WALK" (Now uses the filtered list) ---
        if not filtered_top_segments:
            print("  -> Smart Walk complete. No top wall zones found after filtering.")
            return []

        placeable_zones = []
        # **MODIFICATION**: Use 'filtered_top_segments' instead of 'top_segments'
        current_flat_wall_start = filtered_top_segments[0][0] 
        
        for i in range(len(filtered_top_segments) - 1):
            current_seg_end = filtered_top_segments[i][1]
            next_seg_start = filtered_top_segments[i+1][0]
            
            # (The bulge detection logic remains exactly the same)
            deviation_width = abs(next_seg_start.x - current_seg_end.x)
            deviation_depth = abs(next_seg_start.y - current_seg_end.y)

            if deviation_width < small_bulge_max_width and deviation_depth < small_bulge_max_depth:
                pass
            else:
                placeable_zones.append({
                    'start': current_flat_wall_start, 
                    'end': current_seg_end, 
                    # 'length': current_seg_end.distance(current_flat_wall_start)
                    'length': last_point.distance(current_flat_wall_start)
                })
                current_flat_wall_start = next_seg_start
                
        print(f"  -> Smart Walk complete. Found {len(placeable_zones)} placeable zones on the top wall.")

        if current_flat_wall_start is not None:
            last_point = filtered_top_segments[-1][1]
            placeable_zones.append({
                'start': current_flat_wall_start, 
                'end': last_point, 
                'length': last_point.distance(current_flat_wall_start)
            })

        print(f"  -> Smart Walk complete. Found {len(placeable_zones)} placeable zones on the top wall.")
        
        # Save to cache only if this is the master analysis (no filtering)
        if back_room_location is None and partition_x is None:
            self.docs[0].top_wall_analysis = placeable_zones
            
        return placeable_zones
    
    def distribute_top_wall_segment(self, top_wall_zones: list, back_room_location: Optional[str]) -> dict:
        """
        Takes the list of zones from _analyze_top_wall_with_bulge_detection_new()
        and reserves a 2000mm segment for BOH placement based on the
        back_room_location.

        Args:
            top_wall_zones: The list of zone dictionaries.
            back_room_location: 'left', 'right', or None.

        Returns:
            A new dictionary of zones, keyed by "Zone_1", "Zone_2", etc.,
            with one zone marked as "boh_reserved".
        """
        # --- CACHING CHECK ---
        if self.docs[0].distributed_top_wall_segments is not None:
             # Assuming inputs haven't changed drastically
             return self.docs[0].distributed_top_wall_segments
        # ---------------------

        print(f"\n--- 📑 Distributing Top Wall Segments for BOH Reservation ---")
        print(f"  -> Back room location: {back_room_location}")

        # 1. Add default "distribute_for" key to all zones
        processed_zones = []
        for zone in top_wall_zones:
            new_zone = copy.deepcopy(zone) # Make a copy
            new_zone["distribute_for"] = "clinic_reserved"
            processed_zones.append(new_zone)

        final_zones_list = []
        boh_split_done = False
        BOH_RESERVE_LENGTH = 1700.0

        # 2. Handle 'left' case (reserve BOH at the start)
        if back_room_location == 'left':
            print("  -> Reserving BOH segment on the LEFT side (start of zones).")
            for zone in processed_zones:
                if not boh_split_done and zone['length'] > BOH_RESERVE_LENGTH:
                    print(f"  -> Splitting first available zone (length {zone['length']:.0f}mm)...")
                    boh_split_done = True
                    
                    p1 = zone['start']
                    p2 = zone['end']
                    vector = (p2 - p1).normalize()
                    
                    # Create the BOH zone
                    boh_zone = copy.deepcopy(zone)
                    boh_zone['end'] = p1 + vector * BOH_RESERVE_LENGTH
                    boh_zone['length'] = BOH_RESERVE_LENGTH
                    boh_zone['distribute_for'] = "boh_reserved"
                    final_zones_list.append(boh_zone)
                    
                    # Create the remaining clinic zone
                    clinic_zone = copy.deepcopy(zone)
                    clinic_zone['start'] = boh_zone['end']
                    clinic_zone['length'] = clinic_zone['length'] - BOH_RESERVE_LENGTH
                    # clinic_zone['distribute_for'] is already "clinic_reserved"
                    
                    # Only add the remaining part if it's still a usable length
                    if clinic_zone['length'] > 1000: # Using 1000mm as a minimum usable length
                        final_zones_list.append(clinic_zone)
                    else:
                        print(f"    -> Discarding remaining clinic segment (length {clinic_zone['length']:.0f}mm) as it is too short.")

                else:
                    # This zone is either not the first, or too short, or split is already done
                    final_zones_list.append(zone)

        # 3. Handle 'right' or 'None' case (reserve BOH at the end)
        else:
            if back_room_location == 'right':
                print("  -> Reserving BOH segment on the RIGHT side (end of zones).")
            else:
                print("  -> No back room detected. Defaulting to BOH segment on the RIGHT.")
            
            # Iterate in reverse to find the first suitable zone from the right
            for zone in reversed(processed_zones):
                if not boh_split_done and zone['length'] > BOH_RESERVE_LENGTH:
                    print(f"  -> Splitting last available zone (length {zone['length']:.0f}mm)...")
                    boh_split_done = True
                    
                    p1 = zone['start']
                    p2 = zone['end']
                    vector = (p2 - p1).normalize() # vector is still (end - start)
                    
                    # Calculate the split point from the end
                    split_point = p2 - vector * BOH_RESERVE_LENGTH

                    # Create the clinic zone (the first part)
                    clinic_zone = copy.deepcopy(zone)
                    clinic_zone['end'] = split_point
                    clinic_zone['length'] = clinic_zone['length'] - BOH_RESERVE_LENGTH
                    
                    if clinic_zone['length'] > 1000:
                        # Insert at the beginning of our *new* list
                        final_zones_list.insert(0, clinic_zone)
                    else:
                        print(f"    -> Discarding remaining clinic segment (length {clinic_zone['length']:.0f}mm) as it is too short.")

                    # Create the BOH zone (the second part)
                    boh_zone = copy.deepcopy(zone)
                    boh_zone['start'] = split_point
                    boh_zone['length'] = BOH_RESERVE_LENGTH
                    boh_zone['distribute_for'] = "boh_reserved"
                    final_zones_list.insert(1, boh_zone) # Insert after the clinic part

                else:
                    # Insert all other zones at the beginning to maintain reverse order
                    final_zones_list.insert(0, zone)

        # 4. Convert the final list to the desired dictionary output
        final_zones_dict = {}
        print("\n  --- Final Distributed Zones ---")
        for i, zone in enumerate(final_zones_list):
            zone_id = f"Zone_{i+1}"
            final_zones_dict[zone_id] = zone
            print(f"    -> {zone_id}: Length {zone['length']:.0f}mm, Reserved for: {zone['distribute_for']}")
            
        self.docs[0].distributed_top_wall_segments = final_zones_dict
        return final_zones_dict
        # return final_zones_dict    
        

    
    def plan_clinic_best_ranker(self, distributed_segments: dict, back_room_location: Optional[str] ) -> List[Dict[str, Any]]:
        """
        Analyzes all available clinic zones and generates every possible
        clinic layout permutation that fits.

        It then scores every valid layout based on its "depth" (distance from the
        top of the room) and a penalty for any unplaced clinics.

        The final output is a single, ranked list of all possible plans,
        ready for a subsequent function to select and execute the best one.

        Args:
            distributed_segments: The dictionary of zones from
                                distribute_top_wall_segment().
            back_room_location: 'left', 'right', or None from
                                detect_back_corner_room().
            clinic_queue: A deque of Fixture objects for all clinics to be placed.

        Returns:
            A list of dictionaries, where each dictionary is a complete,
            valid placement plan, ranked by score (ascending).
        """
        # --- CACHING CHECK ---
        if self.docs[0].clinic_ranked_plan is not None:
            print("  -> [CACHE HIT] Using cached Clinic Ranked Plan.")
            # Unpack the tuple from cache
            return self.docs[0].clinic_ranked_plan[0], self.docs[0].clinic_ranked_plan[1]
        # ---------------------
        print("\n--- 🧠 Planning Clinic Layouts (Best Ranker) ---")

        # -----------------------------------------------------------------
        # --- START: NEW CODE BLOCK TO CALL plan_clinic_best_ranker() ---
        # -----------------------------------------------------------------

        # 4. --- Create the Clinic Queue ---
        #    (This is the missing step you asked about)
        print("\n--- 4. Creating Clinic Queue for Planner ---")
        clinic_config = self.fixtures.get("clinic_fixtures", {})
        clinic_queue = collections.deque()
        if not clinic_config:
            print("  -> WARNING: No clinic fixtures found in the configuration.")
        else:
            for name, count in clinic_config.items():
                if count > 0 and name in self.fixture_dict:
                    for _ in range(count):
                        try:
                            fxtr = Fixture.Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"])
                            clinic_queue.append(fxtr)
                        except Exception as e:
                            print(f"  -> ERROR: Could not load fixture '{name}': {e}")
                elif name not in self.fixture_dict:
                    print(f"  -> WARNING: Clinic fixture '{name}' is in config but not in fixture_dict.")

        print(f"  -> Created a queue with {len(clinic_queue)} total clinic fixtures.")

        # --- 1. Initialize Constants and State ---
        V_V_GAP = 800.0
        H_GAP = -100.0
        PENALTY_PER_REMAINING = 1500.0
        all_valid_layouts = []
        
        # Get the names from the fixture objects in the queue
        clinic_names_to_place = [f.name for f in clinic_queue]
        total_clinics_to_place = len(clinic_names_to_place)
        
        # Set the master direction flag
        if back_room_location == 'left' or back_room_location == 'middle':
            # room_detected_at_left = back_room_location == "left"
            room_detected_at_left = True
        else:
            room_detected_at_left = False  # Default to False for 'middle' case

        

            
        # Get the absolute top of the room for scoring
        max_y = self.cvc.max_y
        print(f"  -> Room detected at: {back_room_location}")
        print(f"  -> Planning direction (Left Room = True): {room_detected_at_left}")

        # --- 2. Determine Zone Processing Order ---
        # Sort keys numerically (Zone_1, Zone_2, Zone_10)
        zone_keys = sorted(
            distributed_segments.keys(),
            key=lambda z: int(z.split("_")[1])
        )

        if room_detected_at_left:
            zone_keys.reverse()  # Plan from Zone_N -> Zone_1
            print("  -> Processing zones in REVERSE order (N -> 1)")
        else:
            print("  -> Processing zones in FORWARD order (1 -> N)")

        # --- 3. Iterate Through Every Available Clinic Zone ---
        for zone_id in zone_keys:
            zone = distributed_segments[zone_id]

            # Skip the zone reserved for the BOH
            if zone["distribute_for"] == "boh_reserved":
                print(f"\n  -> Skipping {zone_id} (reserved for BOH)")
                continue

            available_width = zone["length"]
            print(f"\n  -> Analyzing {zone_id} (Width: {available_width:.0f}mm)")

            # Get segment geometry
            p1 = Vec2(zone["start"])
            p2 = Vec2(zone["end"])
            # -----------------------------------------------------------
            # --- THIS IS THE FIX ---
            # -----------------------------------------------------------
            # DO NOT use self.cvc.max_y. Use the max_y of the *current wall segment*.
            max_y_for_scoring = max(p1.y, p2.y)
            print(f"    -> Setting scoring reference max_y for this zone to: {max_y_for_scoring:.0f}")
            # -----------------------------------------------------------
            # --- END OF FIX ---
            # -----------------------------------------------------------
            wall_vector = (p2 - p1).normalize()
            wall_angle_deg = math.degrees(wall_vector.angle)
            
            # Calculate the inward normal vector (away from the wall)
            inward_normal = wall_vector.orthogonal().normalize()
            # if not self.floorplan_polygon.contains(
            #     Point(p1 + inward_normal * 10)
            # ):
            # --- ROBUSTNESS FIX ---
            # Test from the MIDDLE of the segment, not the start point (p1),
            # which can be near a jagged corner and give a false result.
            mid_point = p1.lerp(p2)
            test_point = mid_point + inward_normal * 10
            if not self.floorplan_polygon.contains(
                Point(test_point.x, test_point.y) # <-- Use the new, safer test point
            ):
                inward_normal *= -1

            # --- 4. Core Planning Logic (based on _find_best_combination_for_row) ---
            # Test every possible number of clinics (n)
            for n in range(total_clinics_to_place, 0, -1):

                # -----------------------------------------------------------
                # --- THIS IS THE CHANGE YOU ASKED FOR ---
                # -----------------------------------------------------------
                
                # COMMENT OUT OR DELETE THIS LINE:
                # for order in itertools.permutations(clinic_names_to_place, n):
                
                # REPLACE IT WITH THESE TWO LINES:
                # This tests the *group* of clinics (a combination)
                # for order_tuple in itertools.combinations(clinic_names_to_place, n):
                    # order = list(order_tuple) # The rest of the code expects a list
                order = clinic_names_to_place[:n]
                # -----------------------------------------------------------
                # --- END OF CHANGE ---
                # -----------------------------------------------------------
                
                # Test every permutation (order) of that many clinics
                # for order in itertools.permutations(clinic_names_to_place, n):
                try:
                    fixtures = [
                        Fixture.Fixture(
                            self.fixture_dict[name]["name"],
                            self.fixture_dict[name]["path"]
                        ) for name in order
                    ]
                except KeyError:
                    continue  # Skip if a fixture name is invalid

                # Test every orientation combo for that order
                for combo in itertools.product(["H", "V"], repeat=n):
                    
                    # --- 4a. Calculate Width and Gaps ---
                    required_width = 0.0
                    gaps = []
                    total_v_clinics_in_combo = 0
                    
                    for i in range(n):
                        orient = combo[i]
                        fxtr = fixtures[i]
                        w = fxtr.width if orient == "H" else fxtr.height
                        required_width += w

                        if i < n - 1:
                            next_orient = combo[i + 1]
                            if orient == "V" and next_orient == "V":
                                projected_v_count = total_v_clinics_in_combo + 1
                                gap = (
                                    V_V_GAP
                                    if (projected_v_count % 2 == 1)
                                    else H_GAP
                                )
                            else:
                                gap = H_GAP
                            required_width += gap
                            gaps.append(gap)
                        
                        if orient == "V":
                            total_v_clinics_in_combo += 1
                    gaps.append(0)  # Add 0 gap for the last fixture

                    # --- 4b. Check if this layout FITS in the current zone ---
                    if required_width <= available_width:
                        # VALID LAYOUT FOUND!
                        # Now calculate score and coordinates.
                        
                        coordinates_list = []
                        v_clinic_count_for_mirroring = 0
                        cursor = 0.0
                        max_depth_in_row = 0.0  # Reset for each layout

                        # --- 4c. Calculate Coords, Mirroring, and Depth ---
                        for i in range(n):
                            fxtr = fixtures[i]
                            orient = combo[i]
                            w, h = (
                                (fxtr.width, fxtr.height)
                                if orient == "H"
                                else (fxtr.height, fxtr.width)
                            )

                            # --- Mirroring Logic ---
                            xscale, yscale = 1.0, 1.0
                            if back_room_location == 'middle':
                                if orient == "H":
                                    xscale, yscale = 1.0, -1.0
                                else:  # 'V'
                                    xscale = -1.0
                                    v_clinic_count_for_mirroring += 1
                                    yscale = (
                                        1.0
                                        if (v_clinic_count_for_mirroring % 2 == 0)
                                        else -1.0
                                    )
                            elif room_detected_at_left:
                                if orient == "H":
                                    xscale, yscale = 1.0, 1.0
                                else:  # 'V'
                                    xscale = 1.0
                                    yscale = (
                                        1.0
                                        if (v_clinic_count_for_mirroring % 2 == 1)
                                        else -1.0
                                    )
                                    v_clinic_count_for_mirroring += 1
                            else:  # Right or None
                                if orient == "H":
                                    xscale, yscale = -1.0, 1.0
                                else:  # 'V'
                                    xscale = 1.0
                                    v_clinic_count_for_mirroring += 1
                                    yscale = (
                                        -1.0
                                        if (v_clinic_count_for_mirroring % 2 == 0)
                                        else 1.0
                                    )
                            

                            # --- Position & Coordinate Logic ---
                            if room_detected_at_left:
                                # Plan from End -> Start
                                center_on_wall = p2 - wall_vector * (cursor + w / 2)
                            else:
                                # Plan from Start -> End
                                center_on_wall = p1 + wall_vector * (cursor + w / 2)
                            
                            # Overlap wall by 100mm for a clean look
                            target_center = center_on_wall + inward_normal * (
                                -100.0 + h / 2
                            )

                            # [MODIFICATION] Only apply this horizontal inset logic for
                            # top-wall placements, NOT for 'middle' (U-shape) rooms.
                            inset_x = 0.0
                            if back_room_location == 'middle':
                                # Apply the extra 100mm horizontal inset based on the flag
                                inset_x = -100.0
                            elif room_detected_at_left:
                                 # room_detected_at_left is True: add 100mm
                                inset_x = -100.0
                            else:
                                # room_detected_at_left is False: subtract 100mm
                                inset_x = -100.0
                                
                            # Apply the inset to the target_center's x-coordinate
                            target_center = Vec2(target_center.x + inset_x, target_center.y)
                            # -----------------------------------------------------------
                            # -----------------------------------------------------------

                            # --- Scoring Logic (Depth) ---
                            # Get the AABB (Axis-Aligned Bounding Box)
                            # to find the true bottom_y for scoring
                            local_center = fxtr.bounding_box.center
                            transform = Matrix44.chain(
                                Matrix44.translate(
                                    -local_center.x, -local_center.y, 0
                                ),
                                Matrix44.scale(xscale, yscale, 1.0),
                                Matrix44.z_rotate(math.radians(wall_angle_deg)),
                                Matrix44.translate(
                                    target_center.x, target_center.y, 0
                                ),
                            )
                            world_corners = list(
                                transform.transform_vertices(
                                    fxtr.bounding_box.rect_vertices()
                                )
                            )
                            aabb = BoundingBox2d(world_corners)
                            
                            bottom_y = aabb.extmin.y
                            print(f"      -> {fxtr.name} placed at Y={bottom_y:.2f}mm")
                            # depth = max_y - bottom_y
                            # -----------------------------------------------------------
                            # --- THIS IS THE FIX (inside the loop) ---
                            # -----------------------------------------------------------
                            # Use the zone-specific max_y, not the global one.
                            depth = max_y_for_scoring - bottom_y
                            # -----------------------------------------------------------

                            # The score for the row is its deepest clinic
                            max_depth_in_row = max(max_depth_in_row, depth)


                            # Store coordinate data for this fixture
                            coordinates_list.append(
                                {
                                    "name": fxtr.name,
                                    "target_center": [
                                        round(target_center.x, 2),
                                        round(target_center.y, 2),
                                    ],
                                    "mirror_scale": [xscale, yscale],
                                    "bottom_y": round(bottom_y, 2),
                                    "zone_id": zone_id,
                                }
                            )
                            
                            # Advance the cursor
                            cursor += w + gaps[i]
                        
                        # --- 4d. Calculate Final Score & Add to List ---
                        penalty = (
                            total_clinics_to_place - n
                        ) * PENALTY_PER_REMAINING

                        remaining_clinics = total_clinics_to_place - n
                        print("remaining clinics:", remaining_clinics)

                        H_BONUS = 0.0
                        for i in range(n):
                            if combo[i] == "H":
                                H_BONUS += 500.0  # Bonus for each horizontal clinic

                        final_score = max_depth_in_row + penalty - H_BONUS

                        all_valid_layouts.append(
                            {
                                "score": final_score,
                                "combo": combo,
                                "fixtures": [f.name for f in fixtures],
                                "gaps": gaps,
                                "Placed": False,
                                "Rank": 0,  # Will be calculated later
                                "coordinates": coordinates_list,
                                # Debug info
                                "_debug_zone": zone_id,
                                "_debug_depth_score": max_depth_in_row,
                                "_debug_penalty": penalty
                            }
                        )

        # --- 5. Final Ranking ---
        print(f"\n  -> Found {len(all_valid_layouts)} total valid layouts across all zones.")

        remaining_clinics = 0
        remaining_fixtures_queue = collections.deque() # Create an empty deque
        
        

        if not all_valid_layouts:
            # If NO plans were found, all clinics are remaining
            remaining_clinics = total_clinics_to_place
            remaining_fixtures_queue = collections.deque(clinic_queue) # Return the full queue
            print("  -> No valid layouts found. All clinics are considered remaining.")
            return [], remaining_fixtures_queue

        # ******************** CORRECTION STARTS HERE ********************

        # If plans WERE found, we need to find the MAXIMUM number of clinics 
        # that can be placed by selecting the best NON-OVERLAPPING layouts

        # Sort all layouts by score (best first) - this should already be done
        all_valid_layouts.sort(key=lambda x: x["score"])

        # Track which clinics have been "used" by selected layouts
        used_clinic_names = set()
        max_clinics_placeable = 0

        # Greedy selection: pick the best layouts that don't reuse clinics
        for layout in all_valid_layouts:
            layout_clinic_names = set(layout["fixtures"])
            
            # Check if this layout uses any clinics already selected
            if not layout_clinic_names.intersection(used_clinic_names):
                # This layout is compatible - add its clinics to the used set
                used_clinic_names.update(layout_clinic_names)
                max_clinics_placeable += len(layout["fixtures"])

        # Calculate remaining clinics
        remaining_clinics = total_clinics_to_place - max_clinics_placeable
        print(f"  -> Maximum clinics that can be placed: {max_clinics_placeable}")
        print(f"  -> Clinics remaining unplaced: {remaining_clinics}")

        # ******************** CORRECTION ENDS HERE ********************

        # --- NEW LOGIC TO CREATE THE REMAINING QUEUE ---
        if remaining_clinics > 0:
            # Get the fixtures from the *end* of the original full queue
            remaining_fixtures_list = list(clinic_queue)[-remaining_clinics:]
            remaining_fixtures_queue = collections.deque(remaining_fixtures_list)
            print(f"  -> Returning a new queue with {len(remaining_fixtures_queue)} remaining fixtures.")
        else:
            remaining_fixtures_queue = collections.deque()
            print("  -> The best plan used all fixtures. Returning an empty queue.")
        # --- END NEW LOGIC ---
           

        # Sort all found layouts by their score, ascending
        all_valid_layouts.sort(key=lambda x: x["score"])

        # Assign the final rank
        for i, layout in enumerate(all_valid_layouts):
            layout["Rank"] = i + 1

        # --- NEW LOGIC TO CREATE THE REMAINING QUEUE ---
        if remaining_clinics > 0:
            # Get the fixtures from the *end* of the original full queue
            remaining_fixtures_list = list(clinic_queue)[-remaining_clinics:]
            remaining_fixtures_queue = collections.deque(remaining_fixtures_list)
            print(f"  -> Returning a new queue with {len(remaining_fixtures_queue)} remaining fixtures.")
        else:
            print("  -> The best plan used all fixtures. Returning an empty queue.")
        # --- END NEW LOGIC ---

        print("  -> Ranking complete.")
        result = (all_valid_layouts, remaining_fixtures_queue)
        self.docs[0].clinic_ranked_plan = result
        return all_valid_layouts, remaining_fixtures_queue
        # return all_valid_layouts, remaining_fixtures_queue
    

    def place_clinics_from_ranked_plan(
        self, 
        doc,
        chosen_plan,
        distributed_segments: Dict[str, Any]
    ) -> bool: # <-- Returns bool (True if placed, False if no plans left)
        """
        Executes the *next available* (highest-ranked, unplaced) plan.
        
        It finds the first plan in the list with "Placed": false, executes it,
        and then updates that plan's dictionary to "Placed": true.
        
        Args:
            all_ranked_plans: The complete list of plan dictionaries. This list
                              WILL be modified in-place.
            distributed_segments: The dictionary of all wall zones.
            all_placed_bboxes: The master list of obstacles to be updated.

        Returns:
            bool: True if a plan was successfully found and placed,
                  False if no unplaced plans were found.
        """
        print("\n--- 🚀 Executing Next Highest-Ranked Unplaced Clinic Plan ---")

        # If no plan was found, it means we've placed them all.
        if not chosen_plan:
            print("  -> No more unplaced clinic plans available to execute.")
            return False # Signal to the main loop to stop

        doc.clinic_placement_method = 'Plan_A'

        coordinates = chosen_plan.get("coordinates")
        combo = chosen_plan.get("combo")
        
        if not coordinates or not combo or len(coordinates) != len(combo):
            print(f"  -> ⚠️ ERROR: Plan {chosen_plan.get('Rank')} is missing or has mismatched data. Skipping.")
            chosen_plan["Placed"] = True # Mark as "Placed" to avoid retrying
            return True # Return True to continue the loop (in case others are valid)

        print(f"  -> Found unplaced plan. Placing Rank {chosen_plan.get('Rank', 'N/A')}...")
        print(f"  -> Plan details: {chosen_plan.get('fixtures')}")

        # --- 2. Execute the placement logic ---
        for i, coord_data in enumerate(coordinates):
            try:
                # (The placement logic from here is the same as before)
                clinic_name = coord_data.get("name")
                target_center_coords = coord_data.get("target_center")
                mirror_scale = coord_data.get("mirror_scale")
                zone_id = coord_data.get("zone_id")
                orient = combo[i] 
                
                if not all([clinic_name, target_center_coords, mirror_scale, zone_id, orient]):
                    print(f"  -> ⚠️ WARNING: Skipping clinic {i+1} in Rank {chosen_plan.get('Rank')}, missing data.")
                    continue
                    
                target_center = Vec2(target_center_coords)
                xscale, yscale = mirror_scale[0], mirror_scale[1]

                zone_info = distributed_segments.get(zone_id)
                if not zone_info:
                    print(f"  -> ⚠️ WARNING: Could not find zone '{zone_id}' for clinic '{clinic_name}'. Skipping.")
                    continue
                
                p1 = Vec2(zone_info["start"])
                p2 = Vec2(zone_info["end"])
                
                wall_vector = (p2 - p1).normalize()
                wall_angle_deg = math.degrees(wall_vector.angle)

                if orient == 'V':
                    rotation = wall_angle_deg + 90
                else:
                    rotation = wall_angle_deg
                
                fxtr = Fixture.Fixture(clinic_name, self.fixture_dict[clinic_name]["path"])
                
                
                local_center = fxtr.bounding_box.center
                local_center_scaled = Vec2(local_center.x * xscale, local_center.y * yscale)
                rotated_offset = local_center_scaled.rotate(math.radians(rotation))
                final_insert_point = target_center - rotated_offset

                block_ref = doc.place_fixture(
                    fxtr, 
                    (final_insert_point.x, final_insert_point.y, 0), 
                    rotation, 
                    True,
                    xscale=xscale, 
                    yscale=yscale
                )
                print(f"    -> Placed '{clinic_name}' in '{zone_id}'")

                # Recalculate and Register Bounding Box
                transform = Matrix44.chain(
                    Matrix44.translate(-local_center.x, -local_center.y, 0),
                    Matrix44.scale(xscale, yscale, 1.0),
                    Matrix44.z_rotate(math.radians(wall_angle_deg)),
                    Matrix44.translate(target_center.x, target_center.y, 0)
                )
                world_corners = list(transform.transform_vertices(fxtr.bounding_box.rect_vertices()))
                aabb = BoundingBox2d(world_corners)
                new_bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)
                
                doc.placed_bboxes.append(new_bbox_tuple)

            except Exception as e:
                print(f"  -> 💥 ERROR placing clinic '{clinic_name}' from Rank {chosen_plan.get('Rank')}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # --- 3. Mark this plan as "Placed" in the list ---
        chosen_plan["Placed"] = True
        print(f"  -> ✅ Finished. Marked Rank {chosen_plan.get('Rank')} as 'Placed'.")
        
        return True # Signal that a plan was successfully found and processed
    
    # In DXF_Controller.py (add this anywhere with the other helper functions)

    def _get_details_from_entities(self, entity_list: list) -> List[dict]:
        """
        [NEW HELPER]
        Helper to get bounding box and block_ref from a provided list of entities.
        This is used by the iterative placer to analyze the *new* row.
        """
        details = []
        if not entity_list:
            return details
            
        for entity in entity_list:
            try:
                bbox = extents([entity])
                bbox_tuple = (bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y)
                details.append({
                    'bbox': bbox_tuple,
                    'block_ref': entity  # The entity itself
                })
            except Exception as e:
                print(f"  -> Warning: Could not get details for entity {entity.dxf.name}: {e}")
                continue
        return details

    # In DXF_Controller.py

    def _get_bottom_row_clinic_details(self, doc) -> List[dict]:
        """
        [NEW HELPER]
        Finds all placed clinics, identifies the "bottom row" (lowest
        Y-coordinate), and returns a list of dictionaries for those clinics.
        This is used to find the new anchor for iterative placement.
        """
        print("\n  -> 🔎 Identifying *bottom-most* row of clinic details...")

        all_clinic_entities = [e for e in doc.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
        if not all_clinic_entities:
            print("    -> No clinics found.")
            return []

        # Find the *lowest* Y coordinate (extmin.y) among all clinics
        all_bboxes = [extents([c]) for c in all_clinic_entities if extents([c]).has_data]
        if not all_bboxes:
            print("    -> Could not get clinic bboxes.")
            return []
            
        min_y = min(b.extmin.y for b in all_bboxes)
        
        # Identify the bottom row as clinics within a 1500mm band of the min Y
        # (This finds all clinics *in* that row)
        bottom_wall_clinic_entities = [
            all_clinic_entities[i] for i, b in enumerate(all_bboxes) 
            if b.extmin.y < min_y + 1500
        ]

        placed_clinics_on_bottom_wall = []
        for entity in bottom_wall_clinic_entities:
            bbox = extents([entity])
            bbox_tuple = (bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y)
            placed_clinics_on_bottom_wall.append({
                'bbox': bbox_tuple,
                'block_ref': entity
            })
        
        print(f"    -> Found {len(placed_clinics_on_bottom_wall)} clinics in the bottom-most row (anchor Y ~{min_y:.0f}).")
        return placed_clinics_on_bottom_wall

    # In DXF_Controller.py
    
    def place_remaining_clinic_under(self, doc, debug: bool = False): # <-- REMOVED anchor_entities_list
        """
        [MODIFIED] Now *automatically* finds the lowest-placed row of clinics
        and uses that as the anchor for the next placement pass.
        """

        # 1) detect back room (unchanged)
        back_room_location = doc.clinic_placement_results["back_room_location"]
        partition_x = doc.clinic_placement_results["partition_x"]
        if debug:
            print(f"Back room detected at: {back_room_location}, partition_x: {partition_x}")

        # 2) load remaining queue (unchanged)
        remaining_clinics_queue = doc.clinic_placement_results.get("remaining_clinics_queue")
        if remaining_clinics_queue is None:
            remaining_clinics_queue = collections.deque()
        
        if debug:
            print("Remaining clinics for this pass: ", remaining_clinics_queue)

        # 3) detect doors (unchanged)
        door_results = self.detect_and_visualize_clinic_doors(doc, draw_bboxes=bool(debug))

        # 5) get anchor clinics and analyze under-row segments
        # --- MODIFICATION: ALWAYS find the *bottom* row of clinics ---
        # On Iter 1, this will be the "top row".
        # On Iter 2, this will be the row just placed in Iter 1.
        print("  -> Finding the lowest-placed row of clinics to use as anchor...")
        anchor_clinics_for_this_pass = self._get_bottom_row_clinic_details(doc)
        # --- END MODIFICATION ---

        if debug:
            print("Anchor clinics for this pass: ", anchor_clinics_for_this_pass)
            self.draw_under_row_placement_zones(doc, anchor_clinics_for_this_pass)

        remaining_clinic_placement_segments = self._analyze_first_row_clinic_until_boh_last(
            anchor_clinics_for_this_pass # <-- Pass the new bottom row
        )
        if debug:
            print("Remaining clinic placement segments under this row: ", remaining_clinic_placement_segments)

        # 6) plan under-row clinics (unchanged)
        under_row_clinic_plan = self.plan_remaining_clinic_og_(
            remaining_clinic_placement_segments,
            remaining_clinics_queue,
            back_room_location
        )
        # ... (debug printing) ...

        # 7) execute plan (unchanged, but keep the 'newly_placed_entities' return)
        newly_placed_entities = self.execute_under_row_clinic_plan(doc, under_row_clinic_plan)

        # 8) refresh master bboxes (unchanged)
        all_placed_bboxes = self._get_accurate_obstacle_bboxes(include_all=True)

        # 9) return everything useful
        return {
            'back_room_location': back_room_location,
            'partition_x': partition_x,
            'remaining_clinics_queue': remaining_clinics_queue,
            'door_results': door_results,
            'placed_clinics_on_top_wall': anchor_clinics_for_this_pass, # Use the new name
            'remaining_clinic_placement_segments': remaining_clinic_placement_segments,
            'under_row_clinic_plan': under_row_clinic_plan,
            'all_placed_bboxes': all_placed_bboxes,
            'newly_placed_entities': newly_placed_entities # <-- Keep this
        }

    
    def _get_top_row_clinic_details(self, doc) -> List[dict]:
        """
        Finds all placed clinics, identifies the "top row" based on the highest
        Y-coordinate, and returns a list of dictionaries for those clinics.
        """
        print("\n  -> 🔎 Identifying top-row clinic details...")

        all_clinic_entities = [e for e in doc.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
        if not all_clinic_entities:
            print("    -> No clinics found.")
            return []

        # Find the highest Y coordinate among all clinics
        max_y = max(extents([c]).extmax.y for c in all_clinic_entities)
        
        # Identify the top row as clinics within a 1500mm band of the max Y
        top_wall_clinic_entities = [c for c in all_clinic_entities if extents([c]).extmax.y > max_y - 1500]

        placed_clinics_on_top_wall = []
        for entity in top_wall_clinic_entities:
            bbox = extents([entity])
            bbox_tuple = (bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y)
            placed_clinics_on_top_wall.append({
                'bbox': bbox_tuple,
                'block_ref': entity  # Add the entity itself as the block_ref
            })
        
        print(f"    -> Found {len(placed_clinics_on_top_wall)} clinics in the top row.")
        return placed_clinics_on_top_wall

    def _analyze_first_row_clinic_until_boh_last(self, top_row_clinic_bboxes: list, y_offset: float = 0.0, min_segment_length: float = 1500.0) -> List[dict]:
        """
        [MODIFIED] Analyzes the space directly underneath a given list of bounding boxes
        by walking along their bottom edges. This is more accurate than walking the main floorplan wall.
        It now accepts a simple list of bbox tuples.
        """
        print("    -> Analyzing space under first row via 'Direct Bounding Box Walk'...")

        if not top_row_clinic_bboxes:
            print("      -> No top-row bounding boxes provided. Cannot analyze space.")
            return []

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
       

        print(f"      -> Direct BBox Walk complete. Found {len(valid_zones)} valid placement zones.")
        return valid_zones
    
    def plan_remaining_clinic_og_(self,
                              remaining_clinic_placement_segments: List[dict], 
                              remaining_clinics_queue: collections.deque, 
                              back_room_location: Optional[str]
                             ) -> Dict[str, Any]:
        """
        [NEW PLANNER] Creates a "blueprint" (a placement plan) for all 
        remaining clinics to be placed in the under-row segments.

        This function *plans* the layout but does *not* place any fixtures.
        The plan is returned as a dictionary for another function to execute.

        It follows specific rules based on the back_room_location:
        - All placements are vertical.
        - Gaps between vertical clinics are handled by the solver (V_V_GAP = 800mm).
        - Mirroring logic and segment processing order change based on room location.
        """
        
        print(f"\n--- 🧠 Planning Remaining Clinics (Under-Row) ---")
        print(f"  -> Strategy based on Back Room Location: {back_room_location}")
        print(f"  -> {len(remaining_clinics_queue)} clinics to plan.")
        print(f"  -> {len(remaining_clinic_placement_segments)} segments to fill.")

        # 1. Initialize outputs and constants
        placement_plan_list = [] # This will hold all the dicts for each clinic to place
        final_plan_dict = {"placements": placement_plan_list}
        MARGIN_FROM_SEGMENT_ABOVE = -100.0 # As requested: zero gap

        # 2. Set up processing order and direction flags
        room_at_left = (back_room_location == 'left')

        # Sort segments by their ID number (e.g., under_row_0, under_row_1, ...)
        if room_at_left:
            print("  -> Processing segments in REVERSE order (Right-to-Left).")
            segment_order = sorted(remaining_clinic_placement_segments, 
                                   key=lambda s: int(s['id'].split('_')[-1]), 
                                   reverse=True)
        else:
            print("  -> Processing segments in FORWARD order (Left-to-Right).")
            segment_order = sorted(remaining_clinic_placement_segments, 
                                   key=lambda s: int(s['id'].split('_')[-1]))

        # 3. Main processing loop
        # This counter must persist across all segments to ensure
        # the alternating mirror pattern is continuous.
        total_v_clinics_placed = 0 

        for segment in segment_order:
            if not remaining_clinics_queue:
                print("  -> All clinics have been planned. Stopping.")
                break
            
            print(f"\n  -> Analyzing Segment '{segment['id']}' (Length: {segment['length']:.0f}mm)")

            available_width = segment['length']
            
            # --- a. Get clinic names for the solver ---
            clinic_names_for_solver = [f.name for f in remaining_clinics_queue]

            # --- b. Call the solver to find the best layout that fits ---
            # We force 'V' orientation and pass the persistent vertical count
            # for the solver to correctly calculate alternating 800mm gaps.
            layouts_ranked = self._find_best_combination_for_row(
                clinic_names_for_solver,
                available_width,
                force_orientation='V', # As requested
                start_vertical_count=total_v_clinics_placed 
            )

            if not layouts_ranked:
                print("    -> No 'V' layouts fit in this segment. Moving to next segment.")
                continue

            # --- c. Get the best layout and its details ---
            best_layout = layouts_ranked[0]
            fixtures_for_segment = best_layout['fixtures_for_row']
            gaps_for_segment = best_layout['gaps']
            num_to_place = len(fixtures_for_segment)
            
            print(f"    -> Best layout found: {num_to_place} clinics.")

            # --- d. Get segment geometry ---
            p1 = Vec2(segment['start'])
            p2 = Vec2(segment['end'])
            wall_vector = (p2 - p1).normalize()
            wall_angle_deg = segment['angle']
            
            # --- e. Get the "downward" normal vector ---
            inward_normal = wall_vector.orthogonal().normalize() # Default CCW normal (points "up")
            mid_point = p1.lerp(p2)
            # Test 10mm below the segment
            test_point_down = mid_point + Vec2(0, -10)
            
            # If "down" is inside the floorplan, flip the normal to point down
            if self.floorplan_polygon.contains(Point(test_point_down.x, test_point_down.y)):
                inward_normal *= -1

            # --- f. Generate the placement plan for this segment ---
            cursor = 0.0 # Always calculate from the left of the segment
            
            for i in range(num_to_place):
                fxtr = fixtures_for_segment[i]
                
                # Get dimensions (rotated)
                w = fxtr.height # Width along the segment is the clinic's height
                h = fxtr.width  # Depth away from segment is the clinic's width

                #--RASHEEQUE-MAKE-EDITS-HERE--09-11-2025
                # # Calculate center point
                # center_on_wall = p1 + wall_vector * (cursor + w / 2)
                # --- NEW CONDITIONAL PLACEMENT LOGIC ---
                if room_at_left:
                    # When room_at_left is True, place from the END (p2) backwards
                    center_on_wall = p2 - wall_vector * (cursor + w / 2)
                else:
                    # Original logic: place from the START (p1) forwards
                    center_on_wall = p1 + wall_vector * (cursor + w / 2)
                #--RASHEEQUE-MAKE-EDITS-HERE--
                
                target_center = center_on_wall + inward_normal * (MARGIN_FROM_SEGMENT_ABOVE + h / 2)

                # Calculate rotation
                rotation = wall_angle_deg + 90

                # --- g. Apply the correct CONDITIONAL mirroring logic ---
                xscale = -1.0
                yscale = 1.0
                
                if room_at_left:
                    # Mirroring for "right-to-left"
                    yscale = (1.0 if (total_v_clinics_placed % 2 == 1) else -1.0)
                    total_v_clinics_placed += 1
                else:
                    # Mirroring for "left-to-right" or None
                    total_v_clinics_placed += 1
                    yscale = (-1.0 if (total_v_clinics_placed % 2 == 0) else 1.0)
                    
                # --- h. Calculate final insertion point (for the placement function) ---
                local_center = fxtr.bounding_box.center
                local_center_scaled = Vec2(local_center.x * xscale, local_center.y * yscale)
                rotated_offset = local_center_scaled.rotate(math.radians(rotation))
                final_insert_point = target_center - rotated_offset

                # --- i. Add to the plan list ---
                plan_item = {
                    "clinic_name": fxtr.name,
                    "coordinates": (final_insert_point.x, final_insert_point.y, 0),
                    "xscale": xscale,
                    "yscale": yscale,
                    "rotation": rotation,
                    "segment_id": segment['id'] # For debugging
                }
                placement_plan_list.append(plan_item)
                
                print(f"    -> PLANNED: '{fxtr.name}' in Segment {segment['id']} with yscale={yscale}")
                
                # --- j. Update cursor and main queue ---
                cursor += w + gaps_for_segment[i]
                
                if remaining_clinics_queue:
                    remaining_clinics_queue.popleft()
        
        if remaining_clinics_queue:
            print(f"  -> ⚠️ WARNING: {len(remaining_clinics_queue)} clinics remain unplanned after all segments.")
        
        return final_plan_dict

    # In DXF_Controller.py
    
    # --- MODIFICATION 1: Add the '-> List' return type hint ---
    def execute_under_row_clinic_plan(self, doc, plan_dictionary: Dict[str, Any]) -> List:
        """
        [MODIFIED] Executes a pre-computed clinic placement plan.
        NOW RETURNS a list of the 'block_ref' entities it successfully placed.
        """

        print(f"\n--- 🚀 Executing Under-Row Clinic Placement Plan ---")
        
        placement_list = plan_dictionary.get("placements", [])
        
        newly_placed_entities = []
        
        if not placement_list:
            print("  -> No placements found in the plan. Nothing to execute.")
            # --- MODIFICATION 2: Return the EMPTY list, not None ---
            return newly_placed_entities 
        
        doc.clinic_placement_method = 'Plan_B'
        placed_count = 0
        
        for i, plan_item in enumerate(placement_list):
            try:
                # ... (all your existing code for placing the clinic) ...
                clinic_name = plan_item.get("clinic_name")
                coordinates = plan_item.get("coordinates") 
                xscale = plan_item.get("xscale", 1.0)
                yscale = plan_item.get("yscale", 1.0)
                rotation = plan_item.get("rotation", 0.0)
                segment_id = plan_item.get("segment_id", "Unknown")

                if not all([clinic_name, coordinates]):
                    print(f"  -> ⚠️ WARNING: Skipping plan item {i+1}, missing data.")
                    continue
                
                fxtr = Fixture.Fixture(clinic_name, self.fixture_dict[clinic_name]["path"])
                
                
                block_ref = doc.place_fixture(
                    fxtr, 
                    coordinates, 
                    rotation, 
                    True, 
                    xscale=xscale, 
                    yscale=yscale
                )
                print(f"    -> Placed '{clinic_name}' in Segment {segment_id} (yscale: {yscale})")

                if block_ref:
                    newly_placed_entities.append(block_ref)

                # ... (all your existing bounding box logic) ...
                local_center = fxtr.bounding_box.center
                local_center_scaled = Vec2(local_center.x * xscale, local_center.y * yscale)
                rotated_offset = local_center_scaled.rotate(math.radians(rotation))
                target_center = Vec2(coordinates[0], coordinates[1]) + rotated_offset
                transform = Matrix44.chain(
                    Matrix44.translate(-local_center.x, -local_center.y, 0),
                    Matrix44.scale(xscale, yscale, 1.0),
                    Matrix44.z_rotate(math.radians(rotation)),
                    Matrix44.translate(target_center.x, target_center.y, 0)
                )
                world_corners = list(transform.transform_vertices(fxtr.bounding_box.rect_vertices()))
                aabb = BoundingBox2d(world_corners)
                new_bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)
                doc.placed_bboxes.append(new_bbox_tuple)
                placed_count += 1

            except Exception as e:
                print(f"  -> 💥 ERROR placing clinic '{clinic_name}' from plan: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"--- ✅ Finished Execution. Placed {placed_count} / {len(placement_list)} planned clinics. ---")
        
        # --- MODIFICATION 3: Add the FINAL return statement ---
        return newly_placed_entities
    

    
    def _create_zone_from_points(self, p1: 'Vec2', p2: 'Vec2', index: int, angle_threshold: float, angle_tolerance: float = 15.0) -> dict:
        """Helper to create a zone dictionary and check its angle."""
        
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

    def _find_best_combination_for_row(self, clinic_names_to_place: list, available_width: float, force_orientation: Optional[str] = None, start_vertical_count: int = 0) -> List[dict]:
        """
        # --- MODIFIED: Now returns a LIST of valid layouts, ranked by score. ---
        Universal "Puzzle Solver" for clinic placement in a single row.
        """     
        print("\n--- _find_best_combination_for_row called ---")

        V_V_GAP = 800.0
        # H_GAP = 50.0
        H_GAP = -100.0

        # --- DEBUG: log inputs so we can see why no layouts are found ---
        print(f"  -> [DEBUG] _find_best_combination_for_row called with {len(clinic_names_to_place)} clinics, available_width={available_width:.0f}, force_orientation={force_orientation}, start_vertical_count={start_vertical_count}")
        # Resolve Fixture class robustly (works whether Fixture is module or class imported differently)

        try:
            widths = {}
            for name in clinic_names_to_place:
                data = self.fixture_dict.get(name)
                if not data:
                    widths[name] = "missing-fixture-key"
                    continue
                try:
                    fx = Fixture.Fixture(data["name"], data["path"])
                    widths[name] = {"w": getattr(fx, "width", None), "h": getattr(fx, "height", None)}
                except Exception as e:
                    widths[name] = f"error:{e}"
            else:
                # Fallback: report available dictionary entries without instantiation
                for name in clinic_names_to_place:
                    data = self.fixture_dict.get(name)
                    widths[name] = {"info": data or "missing-fixture-key"}
            print(f"  -> [DEBUG] Clinic fixture sizes: {widths}")
        except Exception as _:
            print("  -> [DEBUG] Could not probe clinic fixture sizes.")


        # --- MODIFIED: Initialize a list to hold all valid layouts ---
        valid_layouts = []

        orientations_to_test = ['H', 'V']
        if force_orientation == 'V':
            orientations_to_test = ['V']
        elif force_orientation == 'H':
            orientations_to_test = ['H']

        for n in range(len(clinic_names_to_place), 0, -1):

            ###########################################################
            ###########################################################
            ###########################################################
            try:
                current_fixtures = []
                for name in clinic_names_to_place[:n]:
                    d = self.fixture_dict.get(name)
                    if not d:
                        print(f"  -> [DEBUG] fixture key missing in fixture_dict: {name}")
                        continue
                    try:
                        current_fixtures.append(Fixture.Fixture(d["name"], d["path"]))
                    except Exception as e:
                        print(f"  -> [DEBUG] Failed to instantiate fixture '{name}': {e}")
            except (KeyError, ValueError):
                current_fixtures = []
            

            ###########################################################
            ###########################################################
            ###########################################################
            #     current_fixtures = [Fixture.Fixture(self.fixture_dict[name]["name"], self.fixture_dict[name]["path"]) for name in clinic_names_to_place[:n]]
            # except (KeyError, ValueError):
            #     continue
            
            orientations = list(product(orientations_to_test, repeat=n))

            for combo in orientations:
                required_width = 0
                gaps = []

                # start counting vertical clinics from the provided starting count
                total_vertical_clinics = int(start_vertical_count)
                
                for i in range(n):
                    orient = combo[i]
                    fxtr = current_fixtures[i]
                    w = fxtr.width if orient == 'H' else fxtr.height
                    required_width += w
                    
                    if i < n - 1:
                        next_orient = combo[i+1]
                        # --- PARTITION-AWARE alternating gap logic for vertical fixtures ---
                        if orient == 'V' and next_orient == 'V':
                            # we count the current vertical before deciding the gap between current and next
                            projected_v_count = total_vertical_clinics + 1
                            # Apply V_V_GAP when projected count is odd (keeps the 'every other' wide aisle continuing from prior rows)
                            gap = V_V_GAP if (projected_v_count % 2 == 1) else H_GAP
                        else:
                            gap = H_GAP
                        required_width += gap
                        gaps.append(gap)
                    
                    # increment after handling gap decision so projected count logic works correctly
                    if orient == 'V':
                        total_vertical_clinics += 1
                gaps.append(0)

                start_margin = 0.0 if combo[0] == 'V' else 0.0
                end_margin = 0.0 if combo[-1] == 'V' else 0.0
                total_required_space = start_margin + required_width + end_margin

                # Debug: show precise required vs available so we can diagnose near-miss fits
                print(f"    -> [DEBUG] combo={combo}, total_required_space={total_required_space:.3f}, available_width={available_width:.3f}")

                # MAKED CHANGES HERE---RASHEEQ
                if total_required_space <= available_width + 1.0:
                    BASE_FIXTURE_WEIGHT = 10000  # large -> fixture count dominates
                    WIDTH_PENALTY = 1.0          # subtract required_width * WIDTH_PENALTY
                    score = (n * BASE_FIXTURE_WEIGHT) - (required_width * WIDTH_PENALTY) # Prioritize more fixtures, then less width

                    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    # +++ NEW: ARCHITECTURAL BONUS FOR BETTER LAYOUTS +++
                    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    # Example: replace current score calculation with named weights
                    # (put this where score is computed inside _find_best_combination_for_row)
                    H_BONUS = 500
                    MIXED_BONUS = 200
                    ALL_H_BONUS = 5000
                    H_STARTER_BONUS = 0.0
                    if 'H' in combo:
                        score += H_BONUS  # Give a bonus to any layout with horizontal fixtures
                    if 'V' in combo and 'H' in combo:
                        score += MIXED_BONUS # Extra bonus for mixed layouts
                    if combo.count('V') == 0 and len(combo) > 1:
                        score += ALL_H_BONUS # Big bonus for all-horizontal rows
                    # if combo.count('H') == 0 and len(combo) > 1:
                    #     score += ALL_H_BONUS # Big bonus for all-horizontal rows

                    # --- APPLY NEW STARTER BONUS ---
                    if combo[0] == 'H':
                        score += H_STARTER_BONUS
                    # -------------------------------
                    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    
                    # --- MODIFIED: Append every valid layout to the list ---
                    layout =({
                        'score': score,
                        'combo': combo,
                        'gaps': gaps,
                        'fixtures_for_row': current_fixtures,
                        'start_margin': start_margin,
                        'remaining_fixtures_names': clinic_names_to_place[n:]
                    })
                     # Add the new key 'Placed' with default value False
                    layout["Placed"] = False
                    valid_layouts.append(layout)
        # --- NEW: Sort the list by score (highest first) before returning ---
        if valid_layouts:
            valid_layouts.sort(key=lambda x: x['score'], reverse=True)
            return valid_layouts

        return [] # Return an empty list if no layouts were found
    
########################################################################################################################
########################################################################################################################
##############################################         BOH         #####################################################
##############################################         BOH         #####################################################
##############################################         BOH         #####################################################
########################################################################################################################
########################################################################################################################

    #---RASHEEQUE-MODIFIED-FUNCTION---#
    def place_boh_fixtures(self):
        """
        [MODIFIED]
        Orchestrates the BOH fixture placement.
        - If a 'middle' room is detected, it calls the new 'create_middle_boh_zone' function.
        - Otherwise, it proceeds with the original 'draw_and_place_boh_fixtures' logic.
        
        After the zone is created by either method, it proceeds to plan and
        place the remaining BOH fixtures.
        """
        for doc in self.docs:
            if doc.skip:
                continue

            print (f" ----> placing doc {doc.ind}")

            # --- START OF NEW DISPATCHER LOGIC ---
            back_room_location = doc.clinic_placement_results.get("back_room_location")

            if back_room_location == 'middle':
                print("\n--- 🏛️  Middle Room Detected: Calling Special BOH Zone Creation ---")
                # Get the segment data returned by the room detection
                room_data = doc.clinic_placement_results.get('new_clinic_segments')
                if room_data:
                    # Call the new special function to create the BOH room
                    self.create_middle_boh_zone(doc, room_data, debug=False)
                    self.place_pickup_table(doc)

                else:
                    print("  -> ⚠️ ERROR: Middle room detected but no room data. Skipping BOH zone creation.")
                    doc.skip = True
                    print("SKIP DOC")
                    continue # Skip this doc
            else:
                # --- This is the original logic from place_boh_fixtures_og ---
                print("\n--- 🏛️  Standard BOH Placement (Left/Right/None) ---")
                under_results = self.draw_and_place_boh_fixtures(doc, debug=False)
                # We don't need to use the results, just run it for its side effects.
                if doc.skip: # Check if draw_and_place_boh_fixtures failed
                    continue
            
            # --- END OF NEW DISPATCHER LOGIC ---

            #--rasheeque-make-edits-here--09-11-2025
            # This logic now runs on whichever BOH zone was created (standard or middle)
            # If doc.skip is True (from either path), this will be skipped by the loop.
            # --- ADD THIS NEW LINE HERE ---
            self.draw_boh_door(doc)
            # --- END OF ADDITION ---
            #--rasheeque-make-edits-here--09-11-2025
            
            self.register_individual_clinic_bboxes(doc, placed_bboxes=None, inset_buffer_distance=0, visualize_debug=False)


            #--RASHEEQUE-MAKE-EDITS-HERE--11-11-2025
            # Now that all BOH fixtures are placed, decide how to draw the door.
            initial_remaining_count = doc.clinic_placement_results.get("initial_remaining_clinic_count", 0)

            # self.place_remaining_boh(doc)
            self.place_remaining_boh(doc, initial_remaining_count)

            if initial_remaining_count >= 2:
                # Pickup table was SKIPPED. Use the new "empty space" logic.
                print("  -> Pickup table was skipped. Drawing door in empty BOH wall space...")
                self.draw_boh_door_in_empty_space(doc)
            else:
                # Pickup table was PLACED. Use the original "anchor to table" logic.
                print("  -> Pickup table was placed. Drawing door anchored to table...")
                # self.draw_boh_door(doc)
            # --- END OF NEW DOOR LOGIC ---
            #--RASHEEQUE-MAKE-EDITS-HERE--11-11-2025

    #---RASHEEQUE-NEWLY-CREATED-FUNCTION---#
    def create_middle_boh_zone(self, doc, room_data: dict, default_depth: float = 1700.0, debug: bool = False):
        """
        [NEW & CORRECTED] Creates a BOH zone for the "middle" (U-shape) room layout.
        It uses the 'boh_reserved' segment from the room detection data as the top
        wall and re-uses the standard expansion and drawing logic.

        Args:
            doc (DXF_Document): The document to modify.
            room_data (dict): The 'new_clinic_segments' dictionary from the clinic placement results.
            default_depth (float): The ideal depth of the BOH room (e.g., 1700mm).
            debug (bool): Flag for verbose printing.
        """
        print("\n--- 🏛️  Creating BOH Zone for 'Middle' Room Layout ---")
        
        # --- 1. Identify the BOH Top Wall ---
        boh_segment = None
        for zone in room_data.values():
            if zone.get('distribute_for') == 'boh_reserved':
                boh_segment = zone
                break
        
        if not boh_segment:
            print("  -> ⚠️ FAILED: Could not find 'boh_reserved' segment in room data. Cannot create BOH zone.")
            doc.skip = True # Mark this doc as failed
            print("SKIP DOC")
            return

        top_p1 = Vec2(boh_segment['start'])
        top_p2 = Vec2(boh_segment['end'])
        print(f"  -> Found BOH top wall segment, length {boh_segment['length']:.0f}mm.")

        # --- 2. Define the "Ideal" BOH Shape ---
        # Create an ideal rectangle aligned with the top segment, 1700mm deep.
        ideal_points = [
            top_p1,
            top_p2,
            Vec2(top_p2.x, top_p2.y - default_depth),
            Vec2(top_p1.x, top_p1.y - default_depth)
        ]
        ideal_polygon = Polygon(ideal_points)
        
        # --- 3. Carve the "Natural" Walls ---
        # *** FIX 1: Access floorplan_polygon from 'self' (the controller), not 'doc' ***
        initial_boh_poly = self.floorplan_polygon.intersection(ideal_polygon)
        
        if initial_boh_poly.is_empty:
            print("  -> ⚠️ FAILED: Ideal BOH shape does not intersect the floorplan.")
            doc.skip = True
            print("SKIP DOC")
            return
            
        print("  -> Successfully carved initial BOH zone from floorplan.")

        # --- 4. Re-use Existing Logic: Find Door Obstacles ---
        # (This is the same logic as in 'draw_and_place_boh_fixtures')
        doc.door_results = self.detect_and_visualize_clinic_doors(doc, draw_bboxes=bool(debug))
        doc.placed_clinics_details = self._get_placed_clinic_details(doc)
        doc.door_aisle_polygons, doc.extended_aisle_bboxes_map = self._get_expanded_door_aisles(
            doc,
            doc.door_results,
            doc.placed_clinics_details,
            extension_distance=700.0,
            draw_visual=bool(debug)
        )
        
        obstacles_for_expansion = None
        if doc.door_aisle_polygons:
            obstacles_for_expansion = unary_union(doc.door_aisle_polygons)
            
        
        # --- 5. Re-use Existing Logic: Expand if Needed ---
        # We use the ideal_polygon's bounds as the slicer for the expansion logic
        initial_slicer_box = box(*ideal_polygon.bounds)
        #---RASHEEQUE-MAKE-EDITS-HERE--11-11-2025
        
        # --- START: New logic to set BOH target area based on remaining clinics ---
        initial_remaining_count = doc.clinic_placement_results.get("initial_remaining_clinic_count")
        if initial_remaining_count is None:
            initial_remaining_count = 0

        DEFAULT_TARGET_SQFT = 75.0 # Original value for this function
        LOWERED_TARGET_SQFT = 1.0  # Set to 1.0 to prevent any expansion

        if initial_remaining_count >= 2:
            target_sqft_for_boh = LOWERED_TARGET_SQFT
            print(f"  -> High clinic count ({initial_remaining_count}). Using SMALL BOH target: {target_sqft_for_boh} sq. ft. (No expansion)")
        else:
            target_sqft_for_boh = DEFAULT_TARGET_SQFT
            print(f"  -> Low clinic count ({initial_remaining_count}). Using DEFAULT BOH target: {target_sqft_for_boh} sq. ft.")
        # --- END: New logic ---

        final_boh_poly = self._expand_boh_zone_downwards_if_needed(
            initial_boh_poly=initial_boh_poly,
            initial_slicer_box=box(*ideal_polygon.bounds), 
            floorplan=self.floorplan_polygon, 
            obstacles_to_avoid=obstacles_for_expansion,
            TARGET_BOH_SQFT=target_sqft_for_boh # <-- This is the corrected line
        )
        # --- END: New logic ---
        #---RASHEEQUE-MAKE-EDITS-HERE--11-11-2025
        
        

        # --- 6. Re-use Existing Logic: Draw Final Walls ---
        self._create_boh_room_from_zone(doc, final_boh_poly, layer_name="BOH_WALL_VALID")
        
        final_area_sqft = final_boh_poly.area / 92903.04 # SQMM_PER_SQFT
        print(f"  -> ✅ 'Middle' BOH Zone creation complete. Final area: {final_area_sqft:.2f} sq. ft.")


    def draw_and_place_boh_fixtures(self, doc, debug: bool = False):
        """
        Detect doors, gather placed clinics, expand door aisles, create BOH zone and place pickup table.
        All prints/drawings only occur when debug=True.

        Returns a dict with useful outputs and the refreshed all_placed_bboxes.
        """

        new_clinic_segments=doc.clinic_placement_results['new_clinic_segments'],
        back_room_location = doc.clinic_placement_results["back_room_location"]
        partition_x = doc.clinic_placement_results["partition_x"]
        all_placed_bboxes=doc.placed_bboxes
        

        # 1) detect doors (visualize only when debug)
        if debug:
            print("-> Detecting clinic doors (visual debug ON)")
        doc.door_results = self.detect_and_visualize_clinic_doors(doc, draw_bboxes=bool(debug))

        # 2) get placed clinic details
        doc.placed_clinics_details = self._get_placed_clinic_details(doc)
        if debug:
            print("-> Placed clinics details:", doc.placed_clinics_details)

        # 4) create BOH zone (supply drawing behavior is internal to the function)
        try:
            boh_result = self.create_boh_zone(doc)
        except Exception as e:
            boh_result = None
            if debug:
                print("-> create_boh_zone raised:", e)

        if debug:
            print("-> BOH creation result:", boh_result)

        try:
            self.place_pickup_table(doc)
            
            # print("Placed pickup table")
            if debug:
                print("-> Placed pickup table (if applicable).")
        except Exception as e:
            if debug:
                print("-> place_pickup_table raised:", e)

        return {
            "door_results": doc.door_results,
            "placed_clinics_details": doc.placed_clinics_details,
            "boh_result": boh_result,
            "all_placed_bboxes": doc.placed_bboxes,
        }
    
    def detect_and_visualize_clinic_doors(self, doc, draw_bboxes: bool = True) -> dict:
        """
        Detects doors/curtains for all placed clinics based on the DOOR_LAYER_NAME
        and optionally draws their bounding boxes for visualization.

        Args:
            draw_bboxes (bool): If True, draws the detected bounding boxes on a debug layer.

        Returns:
            dict: A dictionary where keys are the clinic block reference names
                  and values are the detected door bounding box tuples (min_x, min_y, max_x, max_y),
                  or None if a door wasn't detected for that clinic.
        """
        # --- CACHING: Check if door detection has already run ---
        if doc.door_results is not None:
            print("\n--- 🚪 Using cached clinic door detection results ---")
            return doc.door_results

        print("\n--- 🚪 Detecting Doors for All Placed Clinics ---")
        # Find INSERT entities whose names start with CLINIC (case-insensitive check might be safer)
        # Using uppercase name for matching robustness
        placed_clinic_entities = [
            e for e in doc.msp.query('INSERT')
            if "CLINIC" in e.dxf.name.upper() # Check if "CLINIC" is anywhere in the uppercase name
        ]


        door_detection_results = {}

        if not placed_clinic_entities:
            print("  -> No placed clinic entities found.")
            return door_detection_results

        print(f"  -> Found {len(placed_clinic_entities)} potential clinic entities.")

        for clinic_entity in placed_clinic_entities:
            # Call the helper method to get the bounding box
            door_bbox = self.get_clinic_door_by_layer(clinic_entity)

            # Store the result (bbox tuple or None)
            door_detection_results[clinic_entity.dxf.name] = door_bbox

            if door_bbox:
                print(f"    -> Door detected for {clinic_entity.dxf.name} at: {door_bbox}")
                # Call the drawing helper only if requested and if a bbox was found
                if draw_bboxes:
                    self.draw_detected_door_bbox(door_bbox)
            # else: # Reduce verbosity - message already printed in get_clinic_door_by_layer
            #     print(f"    -> No door geometry found on the specified layer for {clinic_entity.dxf.name}.")

        print(f"--- ✅ Door Detection Phase Complete. Processed {len(placed_clinic_entities)} clinics. ---")
        # --- CACHING: Store the result before returning ---
        doc.door_results = door_detection_results
        return door_detection_results
    
    def _get_placed_clinic_details(self, doc) -> List[Dict[str, Any]]:
        """
        [MODIFIED V5] Finds all placed clinic fixtures and returns a detailed list
        containing their true bounding box, orientation, entity, and all
        four of its true, rotated wall segments in correct geometric order.
        """
        if doc.placed_clinics_details:
            return doc.placed_clinics_details
        
        print("\n  -> Gathering details for all placed clinic fixtures (V5 - Corrected Vectors)...")

        placed_clinic_entities = [
            e for e in doc.msp.query('INSERT')
            if "CLINIC" in e.dxf.name.upper()
        ]

        clinic_details_list = []

        if not placed_clinic_entities:
            print("    -> No placed clinic entities found.")
            return []

        for entity in placed_clinic_entities:
            try:
                # 1. Get the 4 true corners in WCS (CCW order).
                corners_tuples = self.get_outer_rect_corners_shapely(entity)
                
                if len(corners_tuples) < 4:
                    print(f"    -> WARNING: Could not get corners for {entity.dxf.name}. Skipping.")
                    continue

                corners_xy = [(c[0], c[1]) for c in corners_tuples]
                clinic_poly = Polygon(corners_xy)
                
                # 2. Get the axis-aligned bounding box (AABB)
                min_x, min_y, max_x, max_y = clinic_poly.bounds
                bbox_tuple = (min_x, min_y, max_x, max_y)

                # 3. Determine orientation
                width = max_x - min_x
                height = max_y - min_y
                orientation = 'V' if height > width else 'H'

                # 4. --- THIS IS THE FIX ---
                # The 4 corners (c1, c2, c3, c4) are in CCW order.
                corners_vecs = [Vec2(c[0], c[1]) for c in corners_xy]
                c1, c2, c3, c4 = corners_vecs[0], corners_vecs[1], corners_vecs[2], corners_vecs[3]
                
                # We define segments with parallel, same-direction vectors:
                # (c1->c2) is parallel to (c4->c3)
                # (c2->c3) is parallel to (c1->c4)
                
                bottom_segment = (c1, c2)  # Vector: c2 - c1
                right_segment = (c2, c3)   # Vector: c3 - c2
                top_segment = (c4, c3)     # Vector: c3 - c4 (Corrected from c3, c4)
                left_segment = (c1, c4)    # Vector: c4 - c1 (Corrected from c4, c1)
                # --- END OF FIX ---

                # 5. Append all details to the list
                clinic_details_list.append({
                    'bbox': bbox_tuple,
                    'orient': orientation,
                    'entity': entity,
                    'name': entity.dxf.name,
                    'rotated_corners': corners_xy,
                    'bottom_segment': bottom_segment,
                    'top_segment': top_segment,
                    'left_segment': left_segment,
                    'right_segment': right_segment
                })
                
                print(f"    -> Found {entity.dxf.name}: Orient='{orientation}'")

            except Exception as e:
                print(f"    -> ERROR processing {entity.dxf.name}: {e}")
                continue

        print(f"  -> Successfully gathered details (with correct vectors) for {len(clinic_details_list)} clinics.")
        doc.placed_clinics_details = clinic_details_list
        return clinic_details_list
    
    def _get_expanded_door_aisles(self, doc, 
                                    door_results: dict, 
                                    placed_clinics_details: List[dict], # Use the detailed list
                                    extension_distance: float = 700.0,
                                    draw_visual: bool = False) -> Tuple[List[Polygon], Dict[str, Tuple[float, float, float, float]]]:
        """
        [MODIFIED] Creates "keep-out" aisle zones for clinic doors based on Step 2.
        - Extends the bounding box's *larger* side outwards by `extension_distance`.
        - Optionally draws the resulting polygon for validation.
        - Returns a list of the aisle polygons AND a dictionary mapping clinic names
          to their corresponding *extended* aisle bounding boxes.
        """
        
        print("\n--- 🚪 Creating Expanded Door Aisle 'Keep-Out' Zones ---")
        aisle_polygons = []
        
        # This new dictionary will store the final aisle BBoxes for Step 3
        extended_aisle_bboxes_map = {}

        # Use the detailed clinic list to map door results to clinic names
        clinic_name_to_door_bbox = {}
        for clinic in placed_clinics_details:
            # Find the corresponding door result using the clinic's entity name
            clinic_name = clinic.get('name')
            if clinic_name and clinic_name in door_results:
                clinic_name_to_door_bbox[clinic_name] = door_results[clinic_name]

        if not clinic_name_to_door_bbox:
            print("  -> No door results provided or could not map to placed clinics. No aisle zones will be created.")
            return aisle_polygons, extended_aisle_bboxes_map

        for clinic_name, door_bbox in clinic_name_to_door_bbox.items():
            if not door_bbox:
                continue
            
            try:
                minx, miny, maxx, maxy = door_bbox
                width = maxx - minx
                height = maxy - miny
                
                # Default to the raw BBox
                expanded_bbox = (minx, miny, maxx, maxy)
                
                # --- LOGIC PER YOUR STEP 2 ---
                # "extend the bounding box larger side outwards"
                if width > height:
                    # Width is larger (horizontal door). Extend outwards (left/right).
                    expanded_bbox = (minx, miny - extension_distance, maxx, maxy + extension_distance)
                    print(f"  -> {clinic_name}: Horizontal door. Expanding X-axis to {expanded_bbox}")
                else:
                    expanded_bbox = (minx - extension_distance, miny - 1800, maxx + extension_distance, maxy)
                    # Height is larger (vertical door). Extend outwards (top/bottom).
                    print(f"  -> {clinic_name}: Vertical door. Expanding Y-axis to {expanded_bbox}")
                # --- END OF STEP 2 LOGIC ---

                aisle_poly = box(*expanded_bbox)
                if not aisle_poly.is_empty:
                    aisle_polygons.append(aisle_poly)
                    # Store the final expanded bbox tuple for Step 3
                    extended_aisle_bboxes_map[clinic_name] = expanded_bbox
                
                # --- VISUALIZATION LOGIC ---
                if draw_visual:
                    self.draw_debug_polygon(
                        doc,
                        aisle_poly, 
                        layer_name="DEBUG_DOOR_AISLE_ZONES", 
                        color= 12, # color 12 
                        visible_by_default=True
                    )

            except Exception as e:
                print(f"  -> ⚠️ ERROR processing door BBox for {clinic_name}: {e}")
                continue
                
        if draw_visual:
            print(f"  -> ✅ Drew {len(aisle_polygons)} door aisle keep-out zones on 'DEBUG_DOOR_AISLE_ZONES' layer.")
        else:
            print(f"  -> ✅ Created {len(aisle_polygons)} door aisle keep-out zones.")
            
        return aisle_polygons, extended_aisle_bboxes_map
    
    def create_boh_zone(self, doc):
        """
        [ENHANCED VERSION] Creates the BOH zone following an 8-step algorithm.
        [CORRECTED in Step 7] to be robust against polygon creation errors.
        """

        
        door_results = doc.door_results
        back_room_location = doc.clinic_placement_results["back_room_location"]
        partition_x = doc.clinic_placement_results["partition_x"]
        distributed_segments = doc.clinic_placement_results['new_clinic_segments']
        
        print("\n--- 🏛️  Creating BOH Zone (Enhanced 8-Step Algorithm) ---")
        
        # --- STEP 1: GATHER INPUTS ---
        placed_clinics_details = self._get_placed_clinic_details(doc)
        if not placed_clinics_details:
            print("  -> ⚠️ FAILED (Step 1): No placed clinics found.")
            return
        
        # --- STEP 2: CREATE CLINIC DOOR AISLE OBSTACLES ---
        # This will now use the corrected _get_expanded_door_aisles function
        doc.door_aisle_polygons, doc.extended_aisle_bboxes_map = self._get_expanded_door_aisles(
            doc,
            door_results,
            placed_clinics_details,
            extension_distance=700.0,
            draw_visual=False # Set to True to validate
        )
        
        obstacles_for_expansion = None
        if doc.door_aisle_polygons:
            obstacles_for_expansion = unary_union(doc.door_aisle_polygons)
            
        # --- HELPER: Get last clinic based on room location ---
        def get_anchor_clinic(is_left_room: bool):
            if is_left_room:
                return min(placed_clinics_details, key=lambda c: c['bbox'][0])
            else:
                return max(placed_clinics_details, key=lambda c: c['bbox'][2])
        
        # --- HELPER: Get door max_y for a clinic ---
        def get_door_max_y_from_map(clinic_name: str) -> Optional[float]:
            """Gets the max_y from the *extended* aisle map."""
            if clinic_name in doc.extended_aisle_bboxes_map:
                # extended_aisle_bboxes_map stores (minx, miny, maxx, maxy)
                return doc.extended_aisle_bboxes_map[clinic_name][3]  # max_y
            return None
        
        # Set flag
        room_detected_at_left = (back_room_location == 'left')
        MAX_WIDTH_BOH_ZONE = 3500.0
        
        anchor_clinic = get_anchor_clinic(room_detected_at_left)
        anchor_bbox = anchor_clinic['bbox']
        anchor_orient = anchor_clinic['orient']
        anchor_name = anchor_clinic.get('name', 'Unknown')
        
        print(f"  -> Anchor clinic: {anchor_name} (Orientation: {anchor_orient})")
        print(f"  -> Room detected at: {'LEFT' if room_detected_at_left else 'RIGHT/NONE'}")
        
        # --- STEP 3: CALCULATE BOTTOM WALL START COORDINATES ---
        print("  -> (Step 3) Calculating bottom wall START coordinates...")
        
        if room_detected_at_left:
            if partition_x is None:
                print("  -> ⚠️ FAILED (Step 3): Room detected at left, but 'partition_x' is None.")
                return
            start_bottom_x = partition_x
            
            if anchor_orient == 'H':
                start_bottom_y = anchor_bbox[1]  # bottom_y of clinic
            else:  # 'V'
                door_max_y = get_door_max_y_from_map(anchor_name)
                start_bottom_y = door_max_y if door_max_y else anchor_bbox[1] # Use extended door aisle max_y
        else:
            start_bottom_x = anchor_bbox[2]  # max_x (right edge)
            
            if anchor_orient == 'H':
                start_bottom_y = anchor_bbox[1]  # bottom_y
            else:  # 'V'
                door_max_y = get_door_max_y_from_map(anchor_name)
                start_bottom_y = door_max_y if door_max_y else anchor_bbox[1] # Use extended door aisle max_y
        
        print(f"    -> Bottom Start: ({start_bottom_x:.0f}, {start_bottom_y:.0f})")
        
        # --- STEP 4: CALCULATE BOTTOM WALL END COORDINATES ---
        print("  -> (Step 4) Calculating bottom wall END coordinates...")
        
        if room_detected_at_left:
            if partition_x is None: return # Should have been caught, but as a safety
            end_bottom_x = partition_x + MAX_WIDTH_BOH_ZONE
            leftmost_clinic_min_x = anchor_bbox[0]
            if end_bottom_x > leftmost_clinic_min_x:
                end_bottom_x = leftmost_clinic_min_x
            
            end_bottom_y = start_bottom_y # Y-coordinate is the same
        else:
            end_bottom_x = start_bottom_x + MAX_WIDTH_BOH_ZONE
            boh_segment = next((seg for seg in distributed_segments.values() 
                            if seg.get('distribute_for') == 'boh_reserved'), None)
            if boh_segment:
                boh_end_x = boh_segment['end'][0]
                if end_bottom_x > boh_end_x:
                    end_bottom_x = boh_end_x
            
            end_bottom_y = start_bottom_y # Y-coordinate is the same
        
        print(f"    -> Bottom End: ({end_bottom_x:.0f}, {end_bottom_y:.0f})")
        
        # --- STEP 5: CALCULATE TOP WALL START COORDINATES ---
        print("  -> (Step 5) Calculating top wall START coordinates...")
        
        if room_detected_at_left:
            if partition_x is None: return
            start_top_x = partition_x
            # Find the perimeter point on the partition wall that is at the top of the floorplan
            partition_line = LineString([(partition_x, self.cvc.min_y), (partition_x, self.cvc.max_y)])
            top_intersection = self.floorplan_polygon.boundary.intersection(partition_line)
            
            if not top_intersection.is_empty:
                if top_intersection.geom_type == 'MultiPoint':
                    start_top_y = max(p.y for p in top_intersection.geoms)
                else:
                    start_top_y = top_intersection.y
            else:
                start_top_y = anchor_bbox[3] # Fallback to clinic max_y
        else:
            start_top_x = anchor_bbox[2]  # max_x (right edge)
            start_top_y = anchor_bbox[3]  # max_y (top edge)
        
        print(f"    -> Top Start: ({start_top_x:.0f}, {start_top_y:.0f})")
        
        # --- STEP 6: CALCULATE TOP WALL END COORDINATES ---
        print("  -> (Step 6) Calculating top wall END coordinates...")
        
        if room_detected_at_left:
            if partition_x is None: return
            end_top_x = partition_x + MAX_WIDTH_BOH_ZONE
            leftmost_clinic_min_x = anchor_bbox[0]
            if end_top_x > leftmost_clinic_min_x:
                end_top_x = leftmost_clinic_min_x
            
            end_top_y = start_top_y # Use the same Y as the start, then nudge
        else:
            end_top_x = start_bottom_x + MAX_WIDTH_BOH_ZONE # Use start_bottom_x as anchor
            boh_segment = next((seg for seg in distributed_segments.values() 
                            if seg.get('distribute_for') == 'boh_reserved'), None)
            if boh_segment:
                boh_end_x = boh_segment['end'][0]
                if end_top_x > boh_end_x:
                    end_top_x = boh_end_x
            
            end_top_y = start_top_y # Use the same Y as the start, then nudge

        # --- Nudge logic for Top Y coordinate (Step 6) ---
        test_point = Point(end_top_x, end_top_y)
        nudge_y = end_top_y
        nudge_step = 20.0
        max_nudges = 100
        nudge_count = 0
        
        if not self.floorplan_polygon.contains(test_point):
            print(f"    -> Top-end point ({end_top_x:.0f}, {nudge_y:.0f}) is outside. Nudging down...")
            for _ in range(max_nudges):
                nudge_y -= nudge_step
                test_point = Point(end_top_x, nudge_y)
                if self.floorplan_polygon.contains(test_point):
                    end_top_y = nudge_y
                    print(f"    -> Nudged to valid Y: {end_top_y:.0f}")
                    break
                nudge_count += 1
            if nudge_y < start_bottom_y:
                print("    -> ⚠️ Nudge failed (went below bottom wall). Using original start_top_y.")
                end_top_y = start_top_y
        
        print(f"    -> Top End: ({end_top_x:.0f}, {end_top_y:.0f})")
        
        # --- STEP 7: CONSTRUCTING THE BOH ZONE POLYGON [ROBUST FIX] ---
        print("  -> (Step 7) Constructing BOH zone polygon...")
        try:
            # The 8-step algorithm defines four corner points.
            # We create a polygon directly from these four points.
            
            # Define the four corner points in counter-clockwise (CCW) order
            p1_bottom_left = (start_bottom_x, start_bottom_y)
            p2_bottom_right = (end_bottom_x, end_bottom_y)
            p3_top_right = (end_top_x, end_top_y)
            p4_top_left = (start_top_x, start_top_y)
            
            polygon_coords = [
                p1_bottom_left,
                p2_bottom_right,
                p3_top_right,
                p4_top_left
            ]
            
            # Create the simple "ideal" polygon
            boh_zone_poly_simple = Polygon(polygon_coords)

            # To "walk the natural wall" as requested, we intersect this
            # ideal box with the actual floorplan. This carves the
            # polygon to match the real wall shape.
            boh_zone_poly = self.floorplan_polygon.intersection(boh_zone_poly_simple)

            if boh_zone_poly.is_empty:
                print("  -> ⚠️ FAILED (Step 7): Polygon construction resulted in an empty shape.")
                return
            
            print(f"    -> Successfully constructed BOH polygon. Area: {boh_zone_poly.area:.0f} mm^2")

            # --- STEP 8: AREA CHECK AND EXPANSION ---
            # print("  -> (Step 8) Checking area and expanding if needed...")
            
            # # Use the bounds of the *simple* box as the slicer for expansion
            # initial_slicer_box = box(*boh_zone_poly_simple.bounds)
            # --- STEP 8: AREA CHECK AND EXPANSION ---
            print("  -> (Step 8) Checking area and expanding if needed...")
            
            # Use the bounds of the *simple* box as the slicer for expansion
            initial_slicer_box = box(*boh_zone_poly_simple.bounds)

            # --- START: New logic to set BOH target area based on remaining clinics ---
            initial_remaining_count = doc.clinic_placement_results.get("initial_remaining_clinic_count")
            if initial_remaining_count is None:
                initial_remaining_count = 0
            
            DEFAULT_TARGET_SQFT = 60.0  # The original default
            LOWERED_TARGET_SQFT = 40.0   # Set to 40.0 to prevent any expansion

            if initial_remaining_count >= 2:
                target_sqft_for_boh = LOWERED_TARGET_SQFT
                print(f"  -> (Step 8) High clinic count ({initial_remaining_count}). Using SMALL BOH target: {target_sqft_for_boh} sq. ft. (No expansion)")
            else:
                target_sqft_for_boh = DEFAULT_TARGET_SQFT
                print(f"  -> (Step 8) Low clinic count ({initial_remaining_count}). Using DEFAULT BOH target: {target_sqft_for_boh} sq. ft.")
            # --- END: New logic ---
            
            final_boh_poly = self._expand_boh_zone_downwards_if_needed(
                initial_boh_poly=boh_zone_poly,
                initial_slicer_box=initial_slicer_box,
                floorplan=self.floorplan_polygon,
                obstacles_to_avoid=obstacles_for_expansion, # Pass the door aisles
                TARGET_BOH_SQFT = target_sqft_for_boh
            )
            
            # --- FINAL DRAW ---
            self._create_boh_room_from_zone(doc, final_boh_poly, layer_name="BOH_WALL_VALID")
            
            final_area_sqft = final_boh_poly.area / 92903.04 # SQMM_PER_SQFT
            print(f"  -> ✅ BOH Zone creation complete. Final area: {final_area_sqft:.2f} sq. ft.")

        except Exception as e:
            print(f"  -> ⚠️ FAILED (Step 7/8): Error constructing or expanding polygon: {e}")
            import traceback
            traceback.print_exc()
            return
        
    def place_pickup_table(self, doc):
        """
        Orchestrates the main clinic placement by first detecting back corner rooms.
        If a room is found on the back-left, it executes the 'opposite' (right-to-left)
        placement strategy to keep the BOH area away from the room. Otherwise, it
        proceeds with the default (left-to-right) strategy.
        """
        print("\n--- 🧭 Orchestrating Main Clinic Placement Strategy ---")


        #----RASHEEQUE ADDING LOGIC HERE---11-11-2025-#
        # --- START OF NEW MODIFICATION (V2 - Corrected Logic) ---
        
        # 1. Get the *initial* remaining count (this is now a stable value)
        initial_remaining_count = doc.clinic_placement_results.get("initial_remaining_clinic_count")
        print(f"  -> Initial remaining clinic count retrieved: {initial_remaining_count}")
        
        # 2. Handle cases where the value might not exist (e.g., if Plan A placed all clinics)
        if initial_remaining_count is None:
            # If the value was never set (because the under-row loop was skipped),
            # it means the initial remaining count was 0.
            initial_remaining_count = 0
        
        # 3. Apply your decision logic
        if initial_remaining_count >= 2:
            print(f"  -> SKIPPING pickup table placement: Initial remaining clinic count ({initial_remaining_count}) was greater than 2.")
            # return # Exit the function immediately
            # Instead of returning immediately, attempt fallback steps:

            #EDITED THIS FUNCION RASHEEQUE FOR EDITING THE PLACING THE CLINIC IF NO PICKUP TABEL PLACED -11-11-2025-
            # 1) Try placing one clinic under the BOH bottom wall (if any remaining)
            try:
                remaining_queue = doc.clinic_placement_results.get("remaining_clinics_queue")
                print(f"  -> Fallback: Remaining clinics queue: {remaining_queue}")
                if remaining_queue:
                    boh_bottom_segments = self.get_and_draw_boh_bottom_segment(doc, debug=False)
                    if boh_bottom_segments:
                        was_placed = self.place_clinic_under_segment(doc, boh_bottom_segments[0], remaining_queue)
                        if was_placed:
                            print("  -> Fallback: Successfully placed one clinic under BOH.")
                        else:
                            print("  -> Fallback: Could not place clinic under BOH.")
                    else:
                        print("  -> Fallback: No BOH bottom segments found.")
                else:
                    print("  -> Fallback: No clinics in remaining queue to attempt placement.")
            except Exception as e:
                print(f"  -> Fallback: Error while attempting clinic-under-BOH placement: {e}")

            # 2) Refresh obstacle bboxes before attempting pickup-window
            try:
                self._get_accurate_obstacle_bboxes(include_all=True)
            except Exception:
                pass

            # 3) Attempt to place Pick_up_window even though we skipped pickup_table placement
            try:
                print("  -> Fallback: Attempting to place Pick_up_window (after skipping pickup_table).")
                self.place_pickup_window(doc, debug=False)
            except Exception as e:
                print(f"  -> Fallback: Error while attempting to place Pick_up_window: {e}")

            # Done with fallback sequence; exit function
            return


        print(f"  -> Proceeding with pickup table placement: Initial remaining clinic count is {initial_remaining_count}.")
        # --- END OF NEW MODIFICATION ---
        # --- END OF NEW MODIFICATION ---   
        #----RASHEEQUE ADDING LOGIC HERE---11-11-2025-#   

        # If a room is detected on the 'left'...
        if doc.clinic_placement_results["back_room_location"] == 'left':
            print("  -> Back-left room detected. Executing OPPOSITE (right-to-left) clinic placement strategy.")
            
            self._place_pickup_table_in_boh_right(doc)

        else:
            # If the room is on the right or not detected at all...
            if doc.clinic_placement_results["back_room_location"] == 'right':
                print("  -> Back-right room detected. Using DEFAULT (left-to-right) clinic placement strategy.")
            else:
                print("  -> No back corner room detected. Using DEFAULT (left-to-right) clinic placement strategy.")
            # ...call the default placement function.
            
            self.place_pickup_area_fixture(doc)

    #--RASHEEQUE--ADDED--NEW--FUNCTION--11-11-2025--#
    def place_pickup_window(self, doc: "dxf_doc.DXF_Document", debug: bool = False):
        """
        1. Anchors to ALL PLACED CLINICS (using the upgraded _get_placed_clinic_details).
        2. Checks ALL 4 segments (top, bottom, left, right) of EVERY clinic.
        3. Filters for HORIZONTAL segments only.
        4. Sorts valid segments by highest Y-coordinate.
        5. [FIX] Temporarily IGNORES BOH_WALL & PICKUP_TABLE, but *VALIDATES* against CLINICS.
        """
        print("\n--- 🪟 Attempting to place 'Pick_up_window' (Clinic Validation Active, V12) ---")

        # --- 1. Get Configuration & Load Fixture ---
        try:
            config = self.fixtures.get("pickup_window", {})
            if config.get("Pick_up_window", 0) <= 0:
                print("  -> SKIPPED: 'Pick_up_window' not specified in configuration.")
                return
            
            fixture = Fixture.Fixture("Pick_up_window", self.fixture_dict["Pick_up_window"]["path"])
        except Exception as e:
            print(f"  -> 🔥 FAILED: Could not load 'Pick_up_window' fixture: {e}")
            return

        # --- 2. Get ALL Placed Clinics Details (using the correct function) ---
        all_placed_clinics = self._get_placed_clinic_details_window(doc) # <-- Uses the V6 helper
        if not all_placed_clinics:
            print("  -> FAILED: Could not find any placed clinics to analyze.")
            return

        # --- 3. Extract ALL HORIZONTAL segments from ALL clinics ---
        clinic_horizontal_segments = []
        angle_tolerance = 15.0 

        for i, clinic_detail in enumerate(all_placed_clinics):
            segments = clinic_detail.get('segments', {}) 
            clinic_name = clinic_detail.get('name', f'clinic_{i}')
            
            if not segments:
                print(f"  -> WARNING: No 'segments' data found for {clinic_name}.")
                continue
                
            for seg_name, seg_points in segments.items():
                try:
                    p1, p2 = seg_points 
                    if p1.x > p2.x: p1, p2 = p2, p1
                    segment_vec = p2 - p1
                    segment_angle_deg = math.degrees(segment_vec.angle)

                    is_horizontal = (abs(segment_angle_deg) < angle_tolerance or
                                     abs(segment_angle_deg - 180) < angle_tolerance or
                                     abs(segment_angle_deg + 180) < angle_tolerance)
                    
                    if not is_horizontal:
                        continue
                    
                    clinic_horizontal_segments.append({
                        "id": f"{clinic_name}_{seg_name}",
                        "start": (p1.x, p1.y),
                        "end": (p2.x, p2.y),
                        "length": segment_vec.magnitude,
                        "angle": segment_angle_deg
                    })

                except (KeyError, TypeError, ValueError) as e:
                    print(f"  -> WARNING: Could not process {seg_name} for {clinic_name}: {e}")
                    continue
        
        if not clinic_horizontal_segments:
            print("  -> FAILED: No valid HORIZONTAL segments found on *any* clinic.")
            return
            
        print(f"  -> Found {len(clinic_horizontal_segments)} total HORIZONTAL clinic segments to analyze.")

        # --- 4. Sort Segments by Highest Y-coordinate First ---
        try:
            sorted_segments = sorted(
                clinic_horizontal_segments,
                key=lambda seg: seg['start'][1], # Y-coord
                reverse=True
            )
        except (KeyError, TypeError):
             print("  -> FAILED: Could not sort segments due to invalid data.")
             return

        # --- 5. [THIS IS THE FIX] ---
        # Create a filtered obstacle list that IGNORES BOH WALLS & PICKUP TABLES
        # It will *implicitly include* all clinics.
        # ---
        obstacles_for_window = []
        
        def get_bboxes_from_query(query_str: str) -> list:
            bboxes = []
            entities = [e for e in doc.msp.query('INSERT') if query_str in e.dxf.name.upper()]
            for entity in entities:
                try:
                    bbox = extents([entity])
                    if bbox.has_data:
                        bboxes.append((bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y))
                except Exception: continue
            return bboxes

        boh_wall_bboxes = []
        boh_wall_entities = list(doc.msp.query('LWPOLYLINE[layer=="BOH_WALL_VALID_OUTLINE"]'))
        if boh_wall_entities:
            try:
                boh_wall_union_bbox = extents(boh_wall_entities)
                boh_wall_bboxes.append((boh_wall_union_bbox.extmin.x, boh_wall_union_bbox.extmin.y, boh_wall_union_bbox.extmax.x, boh_wall_union_bbox.extmax.y))
            except Exception: pass
        
        pickup_table_bboxes = get_bboxes_from_query("PICKUP_TABLE")
        
        print(f"  -> Temporarily ignoring {len(pickup_table_bboxes)} pickup_table obstacle(s).")
        # --- The print for ignoring clinics is REMOVED ---

        def is_bbox_in_list(bbox_to_check, bbox_list):
            for b in bbox_list:
                if abs(bbox_to_check[0] - b[0]) < 1 and abs(bbox_to_check[1] - b[1]) < 1:
                    return True
            return False

        for bbox in doc.placed_bboxes:
            is_boh_wall = is_bbox_in_list(bbox, boh_wall_bboxes)
            is_pickup_table = is_bbox_in_list(bbox, pickup_table_bboxes)
            
            # --- [FIXED LOGIC] ---
            # Only append if it's NOT a wall or pickup table.
            # This means all other fixtures (like clinics) ARE appended.
            if not is_boh_wall and not is_pickup_table:
                obstacles_for_window.append(bbox)
            else:
                if is_boh_wall: print("  -> Temporarily ignoring a BOH_WALL obstacle.")
                if is_pickup_table: print("  -> Temporarily ignoring a PICKUP_TABLE obstacle.")
        # --- END OF FILTER FIX ---

        # --- 6. Iterate Through Segments (Unchanged) ---
        for target_segment in sorted_segments:
            print(f"\n  -> Attempting placement on horizontal segment '{target_segment['id']}' (Y: {target_segment['start'][1]:.0f})")

            # --- 6a. Check for Fit ---
            if target_segment['length'] + 300  < fixture.width:
                print(f"    -> SKIPPED: Segment is too short ({target_segment['length']:.0f}mm) for the window ({fixture.width}mm).")
                continue

            # --- 6b. Calculate Placement Coordinates (Unchanged) ---
            try:
                p1 = Vec2(target_segment['start'])
                p2 = Vec2(target_segment['end'])
                segment_vector = (p2 - p1).normalize()
                segment_angle = target_segment['angle']
                inward_normal = segment_vector.orthogonal().normalize()
                if inward_normal.y > 0: 
                    inward_normal *= -1 
                center_on_wall = p1.lerp(p2, 0.5)
                margin_from_segment = fixture.height / 2.0 
                target_center = center_on_wall + inward_normal * margin_from_segment
                allowed_distance = margin_from_segment + 150.0 
                print(f"    -> Placing centroid {margin_from_segment:.0f}mm from wall (aligns top edge)")
                print(f"    -> Setting validation tolerance to {allowed_distance:.0f}mm")
            except Exception as e:
                print(f"    -> FAILED: Error during coordinate calculation: {e}")
                continue 

            # --- 6c. Validate and Place (Unchanged) ---
            # This call now uses the 'obstacles_for_window' list, which correctly
            # includes all clinic bounding boxes.
            new_bbox = self._validate_and_place_pickup_window(
                doc,
                fixture,
                target_center,
                segment_angle,
                obstacles_for_window, # <-- This list is now correct
                force=False,
                allowed_boundary_distance=allowed_distance
            )
            
            if new_bbox:
                doc.placed_bboxes.append(new_bbox) 
                print(f"    -> ✅ SUCCESS: Placed 'Pick_up_window' on segment '{target_segment['id']}'.")
                return 
            else:
                # This failure message will now correctly trigger if it overlaps a clinic
                print(f"    -> FAILED: The spot on segment '{target_segment['id']}' was blocked (by a clinic or other fixture) or outside the floorplan.")

        # --- 7. Final Failure Message (Unchanged) ---
        print("\n  -> ⚠️ FAILED: Exhausted all HORIZONTAL clinic segments. 'Pick_up_window' could not be placed.")

    #--RASHEEQUE--ADDED--NEW--FUNCTION--11-11-2025--#
    def _validate_and_place_pickup_window(self, doc, fixture, target_center, angle_deg, placed_bboxes, force=False, allowed_boundary_distance=150.0):
        """
        [NEW VALIDATOR for Pickup Window - V3 - CLINIC AWARE]
        Validates and places the pickup window.
        [FIX] This function now *internally fetches all clinic bboxes* to
        guarantee it validates against them, as requested.
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

        if force:
            is_inside_check_passed = True
            is_overlapping = True
        else:
            # --- THIS IS THE FIX ---
            # 1. Create a new, complete list of obstacles
            all_obstacles_to_check = list(placed_bboxes) # Start with the list passed in
            
            # 2. Call the helper to get all placed clinic details
            print("    -> Validator is now re-fetching all clinic bboxes...")
            clinic_details = self._get_placed_clinic_details(doc)
            
            # 3. Add all clinic bboxes to the list
            clinic_bboxes = []
            for detail in clinic_details:
                if 'bbox' in detail:
                    clinic_bboxes.append(detail['bbox'])
            
            all_obstacles_to_check.extend(clinic_bboxes)
            print(f"    -> Validator is checking against {len(all_obstacles_to_check)} total obstacles (including {len(clinic_bboxes)} clinics).")
            # --- END OF FIX ---

            # # --- Validation checks (unchanged, but now use the new list) ---
            # centroid_distance_to_boundary = self.floorplan_polygon.boundary.distance(fixture_polygon.centroid)
            # is_inside_check_passed = centroid_distance_to_boundary < allowed_boundary_distance
            
            # if not is_inside_check_passed:
            #     print(f"    -> VALIDATION: Failed 'is_inside' check. Centroid distance {centroid_distance_to_boundary:.0f}mm > allowed {allowed_boundary_distance:.0f}mm")

            # More robust containment check: prefer precise polygon containment.
            # Fall back to centroid-distance heuristic only if containment fails.
            try:
                is_inside_check_passed = self.floorplan_polygon.contains(fixture_polygon)
            except Exception:
                is_inside_check_passed = False

            if not is_inside_check_passed:
                centroid_distance_to_boundary = self.floorplan_polygon.boundary.distance(fixture_polygon.centroid)
                is_inside_check_passed = centroid_distance_to_boundary < allowed_boundary_distance
                if not is_inside_check_passed:
                    print(f"    -> VALIDATION: Failed 'is_inside' check. Centroid distance {centroid_distance_to_boundary:.0f}mm > allowed {allowed_boundary_distance:.0f}mm and polygon not contained.")
                else:
                    print(f"    -> VALIDATION: Centroid heuristic passed (distance {centroid_distance_to_boundary:.0f}mm <= allowed {allowed_boundary_distance:.0f}mm) despite polygon not fully contained.")
            else:
                print("    -> VALIDATION: Fixture polygon is fully inside the floorplan.")
            # --- THIS CHECK NOW USES THE AUGMENTED LIST ---
            is_overlapping = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in all_obstacles_to_check)
            
            if is_overlapping:
                    print(f"    -> VALIDATION: Failed 'is_overlapping' check (Likely hit a clinic).")

        # --- Placement logic (unchanged) ---
        if is_inside_check_passed and not is_overlapping:
            rotated_offset = local_center.rotate(math.radians(angle_deg))
            final_insert_point = target_center - rotated_offset
            doc.place_fixture(fixture, (final_insert_point.x, final_insert_point.y + 100, 0), angle_deg, True)
            
            new_bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)
            return new_bbox_tuple
            
        return None

    #--RASHEEQUE--ADDED--NEW--FUNCTION--11-11-2025--#
    def _get_placed_clinic_details_window(self, doc) -> List[Dict[str, Any]]:
        """
        [MODIFIED V6 - UPGRADED & CORRECTED] 
        Finds all placed clinic fixtures and returns a detailed list
        containing their true bounding box, orientation, entity, and all
        four of its true, rotated wall segments in correct geometric order.
        
        - FIX 1: Changed 'entity' key to 'block_ref' to match other functions.
        - FIX 2: This function now correctly calculates and returns the 'segments' dict.
        """
        
        print("\n  -> Gathering details for all placed clinic fixtures (V6 - Upgraded)...")

        placed_clinic_entities = [
            e for e in doc.msp.query('INSERT')
            if "CLINIC" in e.dxf.name.upper()
        ]

        clinic_details_list = []

        if not placed_clinic_entities:
            print("    -> No placed clinic entities found.")
            return []

        for entity in placed_clinic_entities:
            try:
                # 1. Get the 4 true corners in WCS (CCW order).
                corners_tuples = self.get_outer_rect_corners_shapely(entity)
                
                if len(corners_tuples) < 4:
                    print(f"    -> WARNING: Could not get corners for {entity.dxf.name}. Skipping.")
                    continue

                corners_xy = [(c[0], c[1]) for c in corners_tuples]
                
                # 2. Get the axis-aligned bounding box (AABB)
                min_x = min(c[0] for c in corners_xy)
                min_y = min(c[1] for c in corners_xy)
                max_x = max(c[0] for c in corners_xy)
                max_y = max(c[1] for c in corners_xy)
                bbox_tuple = (min_x, min_y, max_x, max_y)

                # 3. Determine orientation
                width = max_x - min_x
                height = max_y - min_y
                orientation = 'V' if height > width else 'H'

                # 4. Define the 4 oriented segments
                corners_vecs = [Vec2(c[0], c[1]) for c in corners_xy]
                c1, c2, c3, c4 = corners_vecs[0], corners_vecs[1], corners_vecs[2], corners_vecs[3]
                
                segments = {
                    'bottom_segment': (c1, c2),  # Vector: c2 - c1
                    'right_segment': (c2, c3),   # Vector: c3 - c2
                    'top_segment': (c4, c3),     # Vector: c3 - c4
                    'left_segment': (c1, c4)     # Vector: c4 - c1
                }

                # 5. Append all details to the list
                clinic_details_list.append({
                    'bbox': bbox_tuple,
                    'orient': orientation,
                    'block_ref': entity,  # <--- THIS IS THE KEY FIX
                    'name': entity.dxf.name,
                    'rotated_corners': corners_xy,
                    'segments': segments  # <--- THIS IS THE ADDED LOGIC
                })
                
                print(f"    -> Found {entity.dxf.name}: Orient='{orientation}'")

            except Exception as e:
                print(f"    -> ERROR processing {entity.dxf.name}: {e}")
                continue

        print(f"  -> Successfully gathered details for {len(clinic_details_list)} clinics.")
        return clinic_details_list


    def draw_boh_door_in_empty_space(self, doc):
        """
        [NEW FUNCTION - V5 - PER USER PLAN]
        Draws a BOH door when the pickup_table is *not* present.
        
        [FIX] It now filters out any wall segment that is part of the
        main floorplan boundary (i.e., "external" walls) before
        searching for a spot.
        
        It then finds the longest "empty" segment that is in the
        BOTTOM 30% of the BOH zone.
        """
        print("\n--- 🚪 Drawing BOH Door in Empty Wall Space (Internal/Bottom 30% Rule) ---")

        DOOR_LENGTH = 750.0
        MIN_SEGMENT_LENGTH = 400.0
        AISLE_EXTENSION_AMOUNT = 700.0 # Creates a 700mm aisle

        # --- 1. Get ALL Raw BOH Wall Segments & Polygons ---
        inner_poly, outer_poly, boh_wall_poly = self._get_boh_wall_polygons(doc)
        
        if not inner_poly or inner_poly.is_empty:
             print("  -> ⚠️ FAILED: BOH inner wall polygon not found. Cannot find perimeter.")
             return
        if not boh_wall_poly or boh_wall_poly.is_empty:
            print("  -> ⚠️ FAILED: BOH wall polygon (hatched part) not found. Cannot draw door.")
            return
        
        perimeter_coords = list(inner_poly.exterior.coords)
        raw_lines = []
        for i in range(len(perimeter_coords) - 1):
             p1 = Vec2(perimeter_coords[i])
             p2 = Vec2(perimeter_coords[i+1])
             raw_lines.append(LineString([p1, p2]))
        
        raw_multiline = MultiLineString(raw_lines)
        print(f"  -> Found {len(raw_lines)} raw perimeter segments to analyze.")

        # --- 2. Get All Obstacles (Fixtures + Aisles) ---
        obstacle_polygons = []
        print(f"  -> Creating {AISLE_EXTENSION_AMOUNT}mm keep-out zones for BOH fixtures...")
        boh_wall_bounds = boh_wall_poly.bounds if boh_wall_poly else None

        for bbox_tuple in doc.placed_bboxes:
            if boh_wall_bounds and \
               abs(bbox_tuple[0] - boh_wall_bounds[0]) < 1 and \
               abs(bbox_tuple[1] - boh_wall_bounds[1]) < 1:
                continue
            min_x, min_y, max_x, max_y = bbox_tuple
            bbox_width = max_x - min_x
            bbox_height = max_y - min_y
            if bbox_height < bbox_width:
                ext_poly = box(min_x, min_y - AISLE_EXTENSION_AMOUNT, 
                               max_x, max_y + AISLE_EXTENSION_AMOUNT)
            else:
                ext_poly = box(min_x - AISLE_EXTENSION_AMOUNT, min_y,
                               max_x + AISLE_EXTENSION_AMOUNT, max_y)
            obstacle_polygons.append(ext_poly)
            
        if hasattr(doc, 'door_aisle_polygons') and doc.door_aisle_polygons:
            print("  -> Adding clinic door aisles to keep-out zone.")
            obstacle_polygons.extend(doc.door_aisle_polygons)
            
        if not obstacle_polygons:
            print("  -> No obstacles found. Using raw segments.")
            obstacles_union = Polygon()
        else:
            obstacles_union = unary_union(obstacle_polygons)
            print(f"  -> Identified {len(obstacle_polygons)} total extended obstacles (fixtures + aisles).")

        # --- 3. Trim Raw Segments with Obstacles ---
        keep_out_zone = obstacles_union
        trimmed_geom = raw_multiline.difference(keep_out_zone)

        # --- 4. Extract Empty Segments ---
        empty_segments = []
        if trimmed_geom.is_empty:
            print("  -> ⚠️ FAILED: No empty space remaining after trimming for obstacles.")
            return
        elif trimmed_geom.geom_type == 'LineString':
            if trimmed_geom.length >= MIN_SEGMENT_LENGTH:
                empty_segments.append(trimmed_geom)
        elif trimmed_geom.geom_type == 'MultiLineString':
            for line in trimmed_geom.geoms:
                if line.length >= MIN_SEGMENT_LENGTH:
                    empty_segments.append(line)
        
        if not empty_segments:
            print(f"  -> ⚠️ FAILED: No empty segments found that are > {MIN_SEGMENT_LENGTH}mm long.")
            return
            
        print(f"  -> Found {len(empty_segments)} empty segments.")

        # --- 5. [NEW] FILTER OUT "EXTERNAL" WALLS ---
        print("  -> Filtering out external floorplan walls...")
        # Create a "fuzzy" boundary of the main floorplan
        floorplan_boundary = self.floorplan_polygon.boundary.buffer(10.0)
        
        internal_empty_segments = []
        for segment_line in empty_segments:
            # If a segment intersects with the floorplan boundary, it's an "external" wall.
            # if segment_line.intersects(floorplan_boundary):
            #     print(f"  -> Ignoring segment at Y={segment_line.centroid.y:.0f}: It's part of the main building wall.")
            # else:
            #     # This segment is "internal" and valid.
            #     internal_empty_segments.append(segment_line)
            seg_centroid = segment_line.centroid
            # Compute distances for diagnostics
            try:
                dist_to_inner = inner_poly.distance(seg_centroid) if inner_poly is not None else float('inf')
            except Exception:
                dist_to_inner = float('inf')
            try:
                dist_to_outer = outer_poly.distance(seg_centroid) if outer_poly is not None else float('inf')
            except Exception:
                dist_to_outer = float('inf')
            try:
                dist_to_floor_boundary = float(self.floorplan_polygon.boundary.distance(seg_centroid))
            except Exception:
                dist_to_floor_boundary = float('inf')

            # Debug line for each candidate segment
            print(f"    -> SEG_DEBUG: centroid=({seg_centroid.x:.0f},{seg_centroid.y:.0f}) dist_inner={dist_to_inner:.1f} dist_outer={dist_to_outer:.1f} dist_floor_boundary={dist_to_floor_boundary:.1f}")

            # Accept if centroid is well inside inner poly
            try:
                if inner_poly is not None and inner_poly.contains(seg_centroid):
                    internal_empty_segments.append(segment_line)
                    continue
            except Exception:
                pass

            # Accept if centroid is slightly inside outer_poly (i.e., the segment sits just inside the wall)
            try:
                if outer_poly is not None and outer_poly.buffer(-5.0).contains(seg_centroid):
                    internal_empty_segments.append(segment_line)
                    continue
            except Exception:
                pass

            # Accept if the centroid is very close to the inner polygon (small gap <= 100mm)
            if dist_to_inner <= 100.0:
                internal_empty_segments.append(segment_line)
                continue

            # Fallback: if the segment does not intersect the floorplan boundary, keep it
            if not segment_line.intersects(floorplan_boundary):
                internal_empty_segments.append(segment_line)
            else:
                print(f"  -> Ignoring segment at Y={segment_line.centroid.y:.0f}: It's part of the main building wall.")

        if not internal_empty_segments:
            print(f"  -> ⚠️ FAILED: No *internal* empty segments found.")
            return
        
        print(f"  -> Found {len(internal_empty_segments)} internal empty segments.")

        # --- 6. [NEW] FILTER FOR "BOTTOM 30%" (using the internal list) ---
        print("  -> Filtering internal segments for 'Bottom 30%' of BOH zone...")
        
        min_x, min_y, max_x, max_y = inner_poly.bounds
        boh_height = max_y - min_y
        y_threshold = min_y + (boh_height * 0.30)
        print(f"  -> BOH Y-Range: ({min_y:.0f} to {max_y:.0f}). Bottom 30% threshold is Y < {y_threshold:.0f}")

        bottom_internal_segments = []
        for segment_line in internal_empty_segments:
            centroid_y = segment_line.centroid.y
            if centroid_y < y_threshold:
                bottom_internal_segments.append(segment_line)
            else:
                print(f"  -> Ignoring internal segment at Y={centroid_y:.0f} (above 30% threshold).")
        
        # if not bottom_internal_segments:
        #     print(f"  -> ⚠️ FAILED: No empty internal segments found in the bottom 30% of the BOH zone.")
        #     return
        if not bottom_internal_segments:
            # Fallback: relax the strict bottom-30% rule and pick the best available internal segment.
            # Preference: lowest centroid (closest to BOH bottom), then longest segment length.
            print("  -> WARNING: No internal segments in bottom 30%. Applying fallback selection (closest-to-bottom, prefer longest).")
            try:
                # get bounds for bottom reference
                min_x, min_y, max_x, max_y = inner_poly.bounds
                # try to find any raw perimeter segment lying near the bottom (within 100mm)
                bottom_candidates = []
                for ln in raw_lines:
                    ys = [c[1] for c in ln.coords]
                    if all(abs(y - min_y) <= 100.0 for y in ys):
                        bottom_candidates.append(ln)

                if bottom_candidates:
                    # choose longest bottom-aligned segment
                    candidate = max(bottom_candidates, key=lambda s: s.length)
                    print(f"  -> Fallback: selected bottom-aligned perimeter segment at Y≈{candidate.centroid.y:.0f}, length={candidate.length:.0f}mm")
                    bottom_internal_segments = [candidate]
                else:
                    # no true bottom-aligned perimeter found -> place at geometric bottom-center
                    # center_x = (min_x + max_x) / 2.0 + 300
                    center_x = max_x - 500
                    bottom_y = min_y
                    # create a short horizontal placeholder segment centered on bottom
                    half_len = 500.0  # initial probe length
                    p1 = Vec2((center_x - half_len, bottom_y))
                    p2 = Vec2((center_x + half_len, bottom_y))
                    candidate = LineString([p1, p2])
                    print(f"  -> Fallback: no bottom segment found. Using bottom-center at ({center_x:.0f},{bottom_y:.0f})")
                    bottom_internal_segments = [candidate]

            except Exception:
                print(f"  -> ⚠️ FAILED: No internal empty segments available for fallback.")
                return

        # --- 7. Find Best Spot (from the *doubly-filtered* list) ---
        longest_empty_segment = max(bottom_internal_segments, key=lambda line: line.length)
        print(f"  -> Found longest internal segment in bottom 30%: {longest_empty_segment.length:.0f}mm")

        # --- 8. Calculate Door "Cut Zone" ---
        shapely_center_point = longest_empty_segment.centroid
        center_point = Vec2(shapely_center_point.x, shapely_center_point.y)

        # --- NEW: NUDGE DOOR SLIGHTLY TO THE RIGHT (towards floorplan right/bottom side)
        # Move up to 25% of the segment length or 500mm, whichever is smaller.
        try:
            p1 = Vec2(longest_empty_segment.coords[0])
            p2 = Vec2(longest_empty_segment.coords[-1])
            seg_min_x = min(p1.x, p2.x)
            seg_max_x = max(p1.x, p2.x)
            seg_len = longest_empty_segment.length
            shift_amt = min(650.0, seg_len * 0.25) + 200
            # Prefer shifting to +X (right). Clamp to segment X extents.
            nudged_x = max(seg_min_x, min(seg_max_x, center_point.x + shift_amt))
            center_point = Vec2(nudged_x, center_point.y)
            print(f"  -> Fallback nudged door center to the right by {shift_amt:.0f}mm -> new center X={center_point.x:.0f}")
        except Exception:
            # If anything fails, keep the original center_point
            pass

        p1 = Vec2(longest_empty_segment.coords[0])
        p2 = Vec2(longest_empty_segment.coords[-1])
        segment_vector = (p2 - p1).normalize()
        normal_vector = segment_vector.orthogonal()
        
        half_len = DOOR_LENGTH / 2
        half_depth = 50.0 
        
        c1 = center_point + segment_vector * half_len + normal_vector * half_depth
        c2 = center_point - segment_vector * half_len + normal_vector * half_depth
        c3 = center_point - segment_vector * half_len - normal_vector * half_depth
        c4 = center_point + segment_vector * half_len - normal_vector * half_depth

        door_cut_box = Polygon([c1, c2, c3, c4])

        # --- 9. Draw the Door ---
        final_door_shape = boh_wall_poly.intersection(door_cut_box)

        if final_door_shape.is_empty:
            print(f"  -> ⚠️ FAILED: Calculated door box did not intersect with the BOH wall.")
            return

        layer_name = "BOH_ZONE_DOOR" 
        if layer_name not in doc.doc.layers:
            doc.doc.layers.add(name=layer_name, color=3) # Green

        if final_door_shape.geom_type == 'Polygon':
            geoms_to_draw = [final_door_shape]
        elif final_door_shape.geom_type == 'MultiPolygon':
            geoms_to_draw = list(final_door_shape.geoms)
        else:
            geoms_to_draw = []

        for poly_geom in geoms_to_draw:
            boundary_coords = list(poly_geom.exterior.coords)
            doc.msp.add_lwpolyline(
                boundary_coords, 
                close=True, 
                dxfattribs={"layer": layer_name}
            )
            
            try:
                hatch = doc.msp.add_hatch(color=3, dxfattribs={"layer": layer_name})
                hatch.set_pattern_fill('ANSI31', scale=1.0, angle=10) 
                hatch.paths.add_polyline_path(boundary_coords, is_closed=True)
            except Exception as e:
                print(f"      -> ⚠️ WARNING: Could not add hatch to door box: {e}")
        
        print(f"  -> ✅ Successfully drew BOH door in empty internal space on layer '{layer_name}'.")


    def draw_boh_door_in_empty_space_v1(self, doc):
        """
        [NEW FUNCTION - V3 - USER-SUGGESTED LOGIC]
        Draws a BOH door when the pickup_table is *not* present.
        It finds the longest "empty" part of the *ENTIRE* BOH wall perimeter,
        avoiding all placed BOH fixtures and clinic door aisles.
        
        [FIX] Instead of a simple buffer, this now extends the "smaller side"
        of each BOH fixture's bounding box by 700mm to create a proper
        aisle keep-out zone.
        """
        print("\n--- 🚪 Drawing BOH Door in Empty Wall Space (Aisle-Aware) ---")

        DOOR_LENGTH = 500.0
        MIN_SEGMENT_LENGTH = 400.0
        # --- REMOVED: OBSTACLE_BUFFER = 100.0 ---
        AISLE_EXTENSION_AMOUNT = 700.0 # Creates a 700mm aisle

        # --- 1. Get ALL Raw BOH Wall Segments ---
        raw_perimeter_path = self._get_boh_perimeter_path_from_bottom_right_ccw(doc)
        if not raw_perimeter_path:
            print("  -> ⚠️ FAILED: Could not find any raw BOH perimeter segments.")
            return

        raw_lines = [LineString([p1, p2]) for p1, p2 in raw_perimeter_path]
        raw_multiline = MultiLineString(raw_lines)
        print(f"  -> Found {len(raw_lines)} raw perimeter segments to analyze.")

        # --- 2. Get All Obstacles (Fixtures + Aisles) [MODIFIED] ---
        obstacle_polygons = []
        
        # a) Get BOH fixtures and extend their smaller side
        print(f"  -> Creating {AISLE_EXTENSION_AMOUNT}mm keep-out zones for BOH fixtures...")
        
        # We process all bboxes *except* the BOH wall itself.
        boh_wall_poly = self._get_boh_zone_polygon(doc)
        boh_wall_bounds = boh_wall_poly.bounds if boh_wall_poly else None

        for bbox_tuple in doc.placed_bboxes:
            # Check if this bbox is the BOH wall itself; if so, skip it.
            if boh_wall_bounds and \
               abs(bbox_tuple[0] - boh_wall_bounds[0]) < 1 and \
               abs(bbox_tuple[1] - boh_wall_bounds[1]) < 1:
                continue

            min_x, min_y, max_x, max_y = bbox_tuple
            bbox_width = max_x - min_x
            bbox_height = max_y - min_y

            if bbox_height < bbox_width:
                # This is a "horizontal" fixture (e.g., on a top/bottom wall).
                # Its smaller side is its depth (height). Extend it vertically.
                ext_poly = box(min_x, min_y - AISLE_EXTENSION_AMOUNT, 
                               max_x, max_y + AISLE_EXTENSION_AMOUNT)
            else:
                # This is a "vertical" fixture (e.g., on a left/right wall).
                # Its smaller side is its depth (width). Extend it horizontally.
                ext_poly = box(min_x - AISLE_EXTENSION_AMOUNT, min_y,
                               max_x + AISLE_EXTENSION_AMOUNT, max_y)
            
            obstacle_polygons.append(ext_poly)
            
        # b) Get Clinic Door Aisles (do not need extra extension)
        if hasattr(doc, 'door_aisle_polygons') and doc.door_aisle_polygons:
            print("  -> Adding clinic door aisles to keep-out zone.")
            obstacle_polygons.extend(doc.door_aisle_polygons)
            
        if not obstacle_polygons:
            print("  -> No obstacles found. Using raw segments.")
            obstacles_union = Polygon() # Empty polygon
        else:
            obstacles_union = unary_union(obstacle_polygons)
            print(f"  -> Identified {len(obstacle_polygons)} total extended obstacles (fixtures + aisles).")

        # --- 3. Trim Raw Segments with Obstacles [MODIFIED] ---
        # We no longer need .buffer() because the obstacles are already extended
        keep_out_zone = obstacles_union
        
        # Use .difference() to "cut" the lines
        trimmed_geom = raw_multiline.difference(keep_out_zone)

        # --- 4. Find the Best Spot (Longest Empty Segment) ---
        empty_segments = []
        if trimmed_geom.is_empty:
            print("  -> ⚠️ FAILED: No empty space remaining after trimming for obstacles.")
            return
        elif trimmed_geom.geom_type == 'LineString':
            if trimmed_geom.length >= MIN_SEGMENT_LENGTH:
                empty_segments.append(trimmed_geom)
        elif trimmed_geom.geom_type == 'MultiLineString':
            for line in trimmed_geom.geoms:
                if line.length >= MIN_SEGMENT_LENGTH:
                    empty_segments.append(line)
        
        if not empty_segments:
            print(f"  -> ⚠️ FAILED: No empty segments found that are > {MIN_SEGMENT_LENGTH}mm long.")
            return

        longest_empty_segment = max(empty_segments, key=lambda line: line.length)
        print(f"  -> Found longest empty segment: {longest_empty_segment.length:.0f}mm")

        # --- 5. Calculate Door "Cut Zone" & Get "Canvas" ---
        if not boh_wall_poly or boh_wall_poly.is_empty:
            print("  -> ⚠️ FAILED: BOH wall polygon not found. Cannot draw door.")
            return
            
        shapely_center_point = longest_empty_segment.centroid
        center_point = Vec2(shapely_center_point.x, shapely_center_point.y)
        
        p1 = Vec2(longest_empty_segment.coords[0])
        p2 = Vec2(longest_empty_segment.coords[-1])
        segment_vector = (p2 - p1).normalize()
        normal_vector = segment_vector.orthogonal()
        
        half_len = DOOR_LENGTH / 2
        half_depth = 50.0 
        
        c1 = center_point + segment_vector * half_len + normal_vector * half_depth
        c2 = center_point - segment_vector * half_len + normal_vector * half_depth
        c3 = center_point - segment_vector * half_len - normal_vector * half_depth
        c4 = center_point + segment_vector * half_len - normal_vector * half_depth

        door_cut_box = Polygon([c1, c2, c3, c4])

        # --- 6. Draw the Door ---
        final_door_shape = boh_wall_poly.intersection(door_cut_box)

        if final_door_shape.is_empty:
            print(f"  -> ⚠️ FAILED: Calculated door box did not intersect with the BOH wall.")
            return

        layer_name = "BOH_ZONE_DOOR" 
        if layer_name not in doc.doc.layers:
            doc.doc.layers.add(name=layer_name, color=3) # Green

        if final_door_shape.geom_type == 'Polygon':
            geoms_to_draw = [final_door_shape]
        elif final_door_shape.geom_type == 'MultiPolygon':
            geoms_to_draw = list(final_door_shape.geoms)
        else:
            geoms_to_draw = []

        for poly_geom in geoms_to_draw:
            boundary_coords = list(poly_geom.exterior.coords)
            doc.msp.add_lwpolyline(
                boundary_coords, 
                close=True, 
                dxfattribs={"layer": layer_name}
            )
            
            try:
                hatch = doc.msp.add_hatch(color=3, dxfattribs={"layer": layer_name})
                hatch.set_pattern_fill('ANSI31', scale=1.0, angle=10) 
                hatch.paths.add_polyline_path(boundary_coords, is_closed=True)
            except Exception as e:
                print(f"      -> ⚠️ WARNING: Could not add hatch to door box: {e}")
        
        print(f"  -> ✅ Successfully drew BOH door in empty space on layer '{layer_name}'.")

    #--RASHEEQUE--ADDED--NEW--FUNCTION--11-11-2025--END---#

    
    def _place_pickup_table_in_boh_right(self, doc):
        """
        [RIGHT SIDE VERSION] Places the 'pickup_table' in the BOH zone on the RIGHT side.
        It starts at the bottom-right and searches leftwards along the bottom edge until a
        clear spot is found. Includes a 150mm downward nudge for better aesthetics.
        """
        
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
        boh_zone = self._get_boh_zone_polygon(doc)
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
                
                is_overlapping = any(candidate_box.intersects(box(*b)) for b in doc.placed_bboxes)
                is_inside = boh_zone.contains(candidate_box)

                if is_inside and not is_overlapping:
                    doc.place_fixture(fixture_obj, (x_try, y_try - 130, 0), 0, False)
                    # doc.place_fixture(fixture_obj, (x_try, y_try, 0), 0, False)
                    doc.placed_bboxes.append(candidate_box.bounds)
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

    def _get_boh_zone_polygon(self, doc) -> Optional[Polygon]:
        """
        Finds all BOH wall outlines and merges them into a single Shapely Polygon.
        This represents the total area occupied by the BOH room.
        """
        # --- FIX: Use a more robust, two-step query to avoid regex errors ---
        # Step 1: Get all polylines without a complex filter.
        # CHECK CACHE FIRST
        if doc.boh_zone_polygon is not None:
            return doc.boh_zone_polygon
        all_polylines = doc.msp.query('LWPOLYLINE')
        
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

        # UPDATE CACHE BEFORE RETURNING
        doc.boh_zone_polygon = boh_zone
        # return boh_zone
        
        return boh_zone if not boh_zone.is_empty else None
    
        

    def _create_boh_room_from_zone(self, doc, boh_zone_poly: Polygon, wall_thickness: float = 50.0, layer_name: str = "BOH_WALL", hatch_color: int = 252):
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
            hatch = doc.msp.add_hatch(color=hatch_color)
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
            doc.msp.add_lwpolyline(
                outer_coords, 
                close=True, 
                dxfattribs={"layer": f"{layer_name}_OUTLINE", "color": 251, "lineweight": 25}
            )
            if not outer_boundary.is_empty:
                doc.msp.add_lwpolyline(
                    list(outer_boundary.exterior.coords), 
                    close=True, 
                    dxfattribs={"layer": f"{layer_name}_OUTLINE", "color": 251, "lineweight": 25}
                )
        
        print(f"  -> ✅ Drew BOH zone as a {wall_thickness}mm thick wall on layer '{layer_name}'.")

    def place_pickup_area_fixture(self, doc):
        """
        [MODIFIED DISPATCHER] Intelligently places pickup fixtures based on the
        clinic placement method and the size of the BOH zone.
        """

        print("\n---  Orchestrating Pickup Area Fixture Placement ---")

        if not hasattr(doc, 'clinic_placement_method') or doc.clinic_placement_method == 'Unknown':
            print("  -> SKIPPED: Clinic placement method is unknown. Cannot determine which pickup fixture to place.")
            self._place_pickup_table_in_boh(doc)
            return

        # --- Step 1: Check for Plan A ---
        if doc.clinic_placement_method == 'Plan_A':
            print("  -> Clinic placement used Plan A. Placing 'pickup_table' in BOH zone.")
            self._place_pickup_table_in_boh(doc)

        # --- Step 2 (NEW LOGIC): Check if BOH zone is large enough ---
        else:
            boh_zone = self._get_boh_zone_polygon(doc)
            if boh_zone and not boh_zone.is_empty:
                # Conversion factor from square mm to square feet
                SQMM_PER_SQFT = 92903.04
                area_sqft = boh_zone.area / SQMM_PER_SQFT
                print(f"  -> BOH Zone found with an area of {area_sqft:.2f} sq. ft.")

                if area_sqft >= 50.0:
                    print("  -> BOH area is > 50 sq. ft. Placing 'pickup_table' in BOH Zone.")
                    self._place_pickup_table_in_boh(doc)
                    return # Stop here since the table has been placed

            # --- Step 3: Fallback to Plan B if other conditions aren't met ---
            if doc.clinic_placement_method == 'Plan_B':
                print("  -> Clinic placement used Plan B Fallback. Placing 'Pick_up_window'.")
                # self.place_pickup_window_next_to_clinic(placed_bboxes)
                self._place_pickup_table_in_boh(doc)
            
            else:
                print("  -> No pickup fixture placement strategy was met.")

    def _place_pickup_table_in_boh(self, doc):
        """
        [MODIFIED] Places the 'pickup_table' in the BOH zone. It starts at the
        bottom-left and searches rightwards along the bottom edge until a
        clear spot is found. Includes a 150mm downward nudge for better aesthetics.
        """
        
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
        boh_zone = self._get_boh_zone_polygon(doc)
        if not boh_zone:
            print("  -> ⚠️ FAILED: Could not find BOH zone to place pickup_table in.")
            return
        # print(boh_zone)
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
                
                is_overlapping = any(candidate_box.intersects(box(*b)) for b in doc.placed_bboxes)
                is_inside = boh_zone.contains(candidate_box)

                if is_inside and not is_overlapping:
                    doc.place_fixture(fixture_obj, (x_try, y_try - 130, 0), 0, False)
                    # doc.place_fixture(fixture_obj, (x_try, y_try , 0), 0, False)
                    doc.placed_bboxes.append(candidate_box.bounds)
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

    #--RASHEEQUE-ADDED-NEW-FUNCTIONS---10-11-2025----1:22-Night-----------------
    def draw_boh_door(self, doc):
        """
        [FINAL VERSION]
        Places the BOH door frame by first drawing a solid white "mask"
        to hide the BOH wall hatch, and then drawing the dashed
        'I-LK CURTAIN' rectangle on top, just like the other doors.
        """
        print("\n--- 🚪 Drawing BOH Door (Mask + Frame) ---")

        try:
            from shapely.ops import nearest_points
        except ImportError:
            print("  -> ⚠️ FAILED: `shapely.ops.nearest_points` not available. Aborting door placement.")
            return

        # --- 1. Define Constants ---
        H_W_DIFFERENCE = 3000.0  # mm
        DOOR_LENGTH = 600.0      # mm
        DOOR_WIDTH = 50.0        # mm (This must match the BOH wall thickness)

        # --- 2. Determine Floorplan Shape ---
        try:
            height = self.cvc.max_y - self.cvc.min_y
            width = self.cvc.max_x - self.cvc.min_x
            
            if abs(height - width) > H_W_DIFFERENCE:
                floor_shape = "narrow"
            else:
                floor_shape = "wider"
            print(f"  -> Floorplan shape classified as: '{floor_shape}'")
        except Exception as e:
            print(f"  -> ⚠️ FAILED to determine floor shape: {e}. Aborting door placement.")
            return

        # --- 3. Get Back Room Location ---
        back_room_location = doc.clinic_placement_results.get("back_room_location")
        print(f"  -> Back room location is: '{back_room_location}'")

        
        # --- 7. Determine Anchor Point on Table ---
        anchor_point_on_table = None
        placement_description = ""

        if back_room_location == 'left':
            if floor_shape == 'narrow':
                self.draw_and_boh_zone_door(
                                            doc,
                                            extend_left= -1200.0,
                                            extend_right= 700.0,
                                            extend_top= 700.0,
                                            extend_bottom = -450.0,
                                            draw_visual = True,
                                        )
            else: # wider
                self.draw_and_boh_zone_door(
                                            doc,
                                            extend_left= 750,
                                            extend_right= -1200.0,
                                            extend_top= -450.0,
                                            extend_bottom = 100.0,
                                            draw_visual = True,
                                        )
                
        elif back_room_location == 'middle':
            self.draw_and_boh_zone_door(
                                        doc,
                                        extend_left= 700.0,
                                        extend_right= -1200.0,
                                        extend_top= 700.0,
                                        extend_bottom = -450.0,
                                        draw_visual = True,
                                    )
        elif back_room_location == 'right' or back_room_location is None:
            if floor_shape == 'narrow':
                self.draw_and_boh_zone_door(
                                            doc,
                                            extend_left= 650.0,
                                            extend_right= -1200.0,
                                            extend_top= 650.0,
                                            extend_bottom = -450.0,
                                            draw_visual = True
                                        )                
            else: # wider
                self.draw_and_boh_zone_door(
                                            doc,
                                            extend_left= -1200.0,
                                            extend_right= 700.0,
                                            extend_top= -450.0,
                                            extend_bottom = 100.0,
                                            draw_visual = True
                                        )                
        else:
            print(f"  -> SKIPPED: BOH door logic not defined for back_room_location '{back_room_location}'.")
            return

               
        print(f"  -> ✅ Successfully drew BOH door FRAME on layer 'BOH_DOOR_FRAME'.")


    # def place_remaining_boh(self, doc):
    def place_remaining_boh(self, doc, initial_remaining_clinic_count: int = 0):
        """
        Orchestrates the BOH fixture placement by classifying the zone shape
        and calling the appropriate planning and execution functions.
        """
        print("___place remaing___")
        pickup_curtain_bboxes = self.draw_and_get_pickup_curtain_bbox(
            doc,
            extend_left= 650.0,
            extend_right= 650.0,
            extend_top= 650.0,
            extend_bottom = 650.0,
            draw_visual = True
        )
        # pickup_curtain_bboxes = self.draw_and_get_pickup_curtain_bbox(
        #     doc,
        #     extend_left= 650.0,
        #     extend_right= -1200.0,
        #     extend_top= -450.0,
        #     extend_bottom = 100.0,
        #     draw_visual = True
        # )


        # BOH_WALL_SEGMENTS = self.get_boh_zone_wall_segment(doc)
        # print(json.dumps(BOH_WALL_SEGMENTS, indent=4))
        # self.draw_boh_segment_order_for_validation_br_ccw()
        classification, width, height = self.classify_boh_zone_shape(doc, tolerance_mm=1000.0)
        print(f"\n[BOH SHAPE RESULT] The BOH zone is classified as: {classification}")
        print(f"BOH Dimensions: {width:.0f}mm Width, {height:.0f}mm Height")
        # if classification == "Rectangular":
        #     print("RECT")
        #     boh_placement_plan = self.plan_boh_fixture_placement_rect(doc, pickup_curtain_bboxes)
        # else:
        if classification == "Rectangular":
            print("RECT")
            boh_placement_plan = self.plan_boh_fixture_placement_rect(
                doc, 
                pickup_curtain_bboxes,
                initial_remaining_clinic_count  # <-- Pass the new argument
            )
        else:
            print("REGULAR")
            # Use the original logic for irregular polygons
            boh_placement_plan = self.plan_boh_fixture_placement(doc, pickup_curtain_bboxes, initial_remaining_clinic_count)
            # print(f"\n[BOH SHAPE RESULT] Bypassing classification, routing directly to 'plan_boh_fixture_placement_rect'.")
        
            # boh_placement_plan = self.plan_boh_fixture_placement_rect(
            #     doc, 
            #     pickup_curtain_bboxes,
            #     initial_remaining_clinic_count
            # )

        # Step 2: Execute the plan to place the fixtures
        self.execute_boh_placement_plan(doc, boh_placement_plan)

    def classify_boh_zone_shape(self, doc, tolerance_mm: float = 1000.0) -> Tuple[str, Optional[float], Optional[float]]:
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
        boh_outlines = list(doc.msp.query('LWPOLYLINE[layer=="BOH_WALL_VALID_OUTLINE"]'))
        if not boh_outlines:
            boh_outlines = list(doc.msp.query('LWPOLYLINE[layer=="BOH_PARTITION_OUTLINE"]'))

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
    


    def plan_boh_fixture_placement(self, doc, pickup_curtain_bboxes: List[tuple], initial_remaining_clinic_count: int = 0) -> list:
        """
        [MODIFIED - V4 - 'TOP SEGMENT' FALLBACK]
        This function now contains the smart logic for all BOH shapes.
        - If pickup_table is skipped (clinic count >= 2) and BOH is wide/square:
            - Prioritizes the TOP wall segment first, then ANTI-CLOCKWISE.
        - [NEW] All other cases now *default* to prioritizing the TOP segment first.
        """

        print("\n--- 📝 Planning BOH Fixture Placement (Universal Smart Planner) ---")

        # --- 1. GATHER ALL NECESSARY DATA ---
        boh_counts = self.fixtures.get("boh_fixtures", {})
        boh_dimensions = self.get_boh_fixture_dimensions()
        wall_segments = self.get_boh_zone_wall_segment(doc, pickup_curtain_bboxes)

        if not boh_counts or not boh_dimensions or not wall_segments:
            print("  -> ⚠️ FAILED: Missing counts, dimensions, or wall segments. Cannot create a plan.")
            return []

        # --- 2. DETERMINE PLACEMENT MODE AND SHAPE ORIENTATION ---
        _, width, height = self.classify_boh_zone_shape(doc)
        
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
        initial_segment_data = None
        initial_segment_id = -1
        
        pickup_table_was_skipped = (initial_remaining_clinic_count >= 2)
        processing_order = [] # This will be our final list of (id, data) tuples

        # --- [USER'S RULE - CHECK FIRST] ---
        # This check now also covers "square" shapes (since not is_taller will be true)
        if pickup_table_was_skipped and not is_taller:
            print("  -> Prioritization: Pickup table skipped & BOH is wide/square. Placing from TOP segment first, then ANTI-CLOCKWISE.")
            
            def is_horizontal(segment_data, angle_tolerance=15.0):
                angle = segment_data['angle']
                return (abs(angle) <= angle_tolerance or 
                        abs(angle - 180) <= angle_tolerance or
                        abs(angle + 180) <= angle_tolerance)

            horizontal_segments = [ (k, v) for k, v in wall_segments.items() if is_horizontal(v) ]
            
            if horizontal_segments:
                # Find the horizontal segment with the highest Y-coordinate
                initial_segment_id, initial_segment_data = max(
                    horizontal_segments, 
                    key=lambda item: (item[1]['start_point'][1] + item[1]['end_point'][1]) / 2
                )
                print(f"    -> Found top segment (ID: {initial_segment_id}) as priority.")

                # --- NEW ANTI-CLOCKWISE SORT LOGIC ---
                processing_order.append((initial_segment_id, initial_segment_data))
                num_segments = len(wall_segments)
                current_id = initial_segment_id
                all_segment_keys = set(wall_segments.keys())

                for _ in range(num_segments - 1): 
                    current_id = (current_id + 1) % num_segments 
                    if current_id in all_segment_keys and current_id != initial_segment_id:
                        processing_order.append((current_id, wall_segments[current_id]))
                
                print(f"    -> Full anti-clockwise processing order: {[item[0] for item in processing_order]}")
                # --- END OF NEW LOGIC ---

            else:
                print("    -> WARNING: No horizontal top segment found. Will use fallback logic.")
                initial_segment_id = -1 # Force fallback
        
        # --- [NEW SIMPLIFIED FALLBACK (User's Rule)] ---
        # If the anti-clockwise logic was NOT triggered, use the new "TOP segment always" default.
        if not processing_order:
            if is_taller:
                print("  -> Prioritization: (TALL BOH) Defaulting to TOP segment.")
            else:
                print("  -> Prioritization: (WIDE BOH) Defaulting to TOP segment.")

            def is_horizontal(segment_data, angle_tolerance=15.0):
                angle = segment_data['angle']
                return (abs(angle) <= angle_tolerance or 
                        abs(angle - 180) <= angle_tolerance or
                        abs(angle + 180) <= angle_tolerance)

            horizontal_segments = [ (k, v) for k, v in wall_segments.items() if is_horizontal(v) ]
            
            if horizontal_segments:
                # Find the horizontal segment with the highest Y-coordinate
                initial_segment_id, initial_segment_data = max(
                    horizontal_segments, 
                    key=lambda item: (item[1]['start_point'][1] + item[1]['end_point'][1]) / 2
                )
                print(f"    -> Found top segment (ID: {initial_segment_id}) as priority.")
                processing_order.append((initial_segment_id, initial_segment_data)) # Add the first one
            elif wall_segments: 
                print("    -> WARNING: No horizontal top segment found. Falling back to LARGEST segment.")
                initial_segment_id, initial_segment_data = max(
                    wall_segments.items(), 
                    key=lambda item: item[1]['length']
                )
                processing_order.append((initial_segment_id, initial_segment_data))
            else:
                print("  -> ⚠️ FAILED: No segments available to process.")
                return [] 
        
        # --- [Common logic for FALLBACKS only] ---
        # If we *didn't* use the new anti-clockwise logic, we must fill the rest
        if len(processing_order) != len(wall_segments):
            print("  -> Filling remaining segments by length (fallback sort).")
            
            all_segments_tuples = [(k, v) for k, v in wall_segments.items()]
            
            # Use the already-found initial_segment_id and _data
            if (initial_segment_id, initial_segment_data) in all_segments_tuples:
                all_segments_tuples.remove((initial_segment_id, initial_segment_data))
            
            all_segments_tuples.sort(key=lambda item: item[1]['length'], reverse=True)
            processing_order.extend(all_segments_tuples)

        # --- 5. EXECUTE THE NO-GAP PACKING ALGORITHM ---
        placement_plan = []
        margin_from_wall = 0.0 
        boh_zone_poly = self._get_boh_zone_polygon(doc)
        
        # --- Pickup table logic (unchanged) ---
        pickup_table_name = 'pickup_table'
        if not pickup_table_was_skipped and any(f['name'] == pickup_table_name for f in fixtures_to_plan):
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
            processing_order = [item for item in processing_order if item[0] != shortest_segment_id]
        elif pickup_table_was_skipped:
             print("  -> Skipping special 'pickup_table' placement as it was not required.")
        # --- [END MODIFICATION] ---

        # --- [THIS IS THE FIX from last time] ---
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

            # --- [START OF NEW INSET LOGIC] ---
            inset_for_corners = 100.0 # Standard 100mm inset
            segment_index = next((i for i, (sid, _) in enumerate(processing_order) if sid == seg_id), -1)

            if segment_index == 0:
                # This is the FIRST segment (e.g., the Top wall), start at 0.
                cursor = 0.0
                print(f"\n  -> Planning Segment {seg_id} (Length: {seg_len:.0f}mm) - Starting at edge (cursor 0).")
            else:
                # This is a SUBSEQUENT segment, apply inset to avoid corner collision.
                cursor = inset_for_corners
                print(f"\n  -> Planning Segment {seg_id} (Length: {seg_len:.0f}mm) - Starting with {inset_for_corners}mm inset.")
            # --- [END OF NEW INSET LOGIC] ---

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

        # --- 6. FINALIZE AND RETURN THE PLAN ---
        if fixtures_to_plan:
            print(f"  -> ⚠️ WARNING: Could not plan for {len(fixtures_to_plan)} fixtures. Not enough wall space.")

        print(f"\n--- ✅ BOH Placement Plan Complete. Generated {len(placement_plan)} placements. ---")
        return placement_plan

    



    def plan_boh_fixture_placement_rect(self, doc, pickup_curtain_bboxes: List[tuple], initial_remaining_clinic_count: int = 0) -> list:
        """
        [MODIFIED - V3 - CORRECTED INSET LOGIC]
        Plans BOH fixture placement for a 'Rectangular' zone.
        - If pickup_table is skipped (clinic count >= 2) and BOH is wide:
            - Prioritizes the TOP wall segment first (cursor=0).
            - Processes all remaining segments in a strict ANTI-CLOCKWISE order (cursor=100).
        - Otherwise, uses fallback logic.
        """

        print("\n--- 📝 Planning BOH Fixture Placement for RECTANGLE (Prioritized No-Gap Packing) ---")

        # --- 1. GATHER ALL NECESSARY DATA ---
        boh_counts = self.fixtures.get("boh_fixtures", {})
        boh_dimensions = self.get_boh_fixture_dimensions()
        wall_segments = self.get_boh_zone_wall_segment(doc, pickup_curtain_bboxes)

        if not boh_counts or not boh_dimensions or not wall_segments:
            print("  -> ⚠️ FAILED: Missing counts, dimensions, or wall segments. Cannot create a plan.")
            return []

        # --- 2. DETERMINE PLACEMENT MODE AND SHAPE ORIENTATION ---
        _, width, height = self.classify_boh_zone_shape(doc)
        
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
        initial_segment_data = None
        initial_segment_id = -1
        
        pickup_table_was_skipped = (initial_remaining_clinic_count >= 2)
        processing_order = [] # This will be our final list of (id, data) tuples

        # --- [USER'S RULE - CHECK FIRST] ---
        if pickup_table_was_skipped and not is_taller:
            print("  -> Prioritization: Pickup table skipped & BOH is wide. Placing from TOP segment first, then ANTI-CLOCKWISE.")
            
            def is_horizontal(segment_data, angle_tolerance=15.0):
                angle = segment_data['angle']
                return (abs(angle) <= angle_tolerance or 
                        abs(angle - 180) <= angle_tolerance or
                        abs(angle + 180) <= angle_tolerance)

            horizontal_segments = [ (k, v) for k, v in wall_segments.items() if is_horizontal(v) ]
            
            if horizontal_segments:
                # Find the horizontal segment with the highest Y-coordinate
                initial_segment_id, initial_segment_data = max(
                    horizontal_segments, 
                    key=lambda item: (item[1]['start_point'][1] + item[1]['end_point'][1]) / 2
                )
                print(f"    -> Found top segment (ID: {initial_segment_id}) as priority.")

                # --- NEW ANTI-CLOCKWISE SORT LOGIC ---
                processing_order.append((initial_segment_id, initial_segment_data))
                num_segments = len(wall_segments)
                current_id = initial_segment_id
                all_segment_keys = set(wall_segments.keys())

                for _ in range(num_segments - 1): 
                    current_id = (current_id + 1) % num_segments 
                    if current_id in all_segment_keys and current_id != initial_segment_id:
                        processing_order.append((current_id, wall_segments[current_id]))
                
                print(f"    -> Full anti-clockwise processing order: {[item[0] for item in processing_order]}")
                # --- END OF NEW LOGIC ---

            else:
                print("    -> WARNING: No horizontal top segment found. Will use fallback logic.")
                initial_segment_id = -1 # Force fallback
        
        # --- [ORIGINAL TALL LOGIC - NOW FALLBACK] ---
        if not processing_order and is_taller:
            print("  -> Prioritization: (Fallback) Starting with the RIGHT-MOST segment (Tall/Narrow BOH).")
            boh_zone = self._get_boh_zone_polygon(doc)
            right_wall_x = boh_zone.bounds[2]
            def is_vertical(segment_data):
                p1 = Vec2(segment_data['start_point'])
                p2 = Vec2(segment_data['end_point'])
                return abs(p1.y - p2.y) > abs(p1.x - p2.x)
            right_segments = [ (k, v) for k, v in wall_segments.items() if is_vertical(v) and abs((Vec2(v['start_point']).x + Vec2(v['end_point']).x)/2 - right_wall_x) < 500 ]
            if right_segments:
                 initial_segment_id, initial_segment_data = max(right_segments, key=lambda item: max(item[1]['start_point'][1], item[1]['end_point'][1]))
                 processing_order.append((initial_segment_id, initial_segment_data)) 
            else:
                initial_segment_id = -1 

        # --- [FINAL FALLBACK - Original "Wider" logic] ---
        if not processing_order:
            print("  -> Prioritization: (Final FallBACK) Using default 'Wider BOH' logic (TOP segment).")
            def is_horizontal(segment_data, angle_tolerance=15.0):
                angle = segment_data['angle']
                return (abs(angle) <= angle_tolerance or 
                        abs(angle - 180) <= angle_tolerance or
                        abs(angle + 180) <= angle_tolerance)
            horizontal_segments = [ (k, v) for k, v in wall_segments.items() if is_horizontal(v) ]
            if horizontal_segments:
                initial_segment_id, initial_segment_data = max(
                    horizontal_segments, 
                    key=lambda item: (item[1]['start_point'][1] + item[1]['end_point'][1]) / 2
                )
                print(f"    -> Found top segment (ID: {initial_segment_id}) as priority.")
                processing_order.append((initial_segment_id, initial_segment_data))
            elif wall_segments: 
                print("    -> WARNING: No horizontal top segment found. Falling back to LARGEST segment.")
                initial_segment_id, initial_segment_data = max(
                    wall_segments.items(), 
                    key=lambda item: item[1]['length']
                )
                processing_order.append((initial_segment_id, initial_segment_data))
            else:
                print("  -> ⚠️ FAILED: No segments available to process.")
                return [] 
        
        # --- [Common logic for FALLBACKS only] ---
        if len(processing_order) != len(wall_segments):
            print("  -> Filling remaining segments by length (fallback sort).")
            all_segments_tuples = [(k, v) for k, v in wall_segments.items()]
            if (initial_segment_id, initial_segment_data) in all_segments_tuples:
                all_segments_tuples.remove((initial_segment_id, initial_segment_data))
            all_segments_tuples.sort(key=lambda item: item[1]['length'], reverse=True)
            processing_order.extend(all_segments_tuples)

        # --- 5. EXECUTE THE NO-GAP PACKING ALGORITHM ---
        placement_plan = []
        margin_from_wall = 0.0 
        boh_zone_poly = self._get_boh_zone_polygon(doc)
        
        # --- Pickup table logic (unchanged) ---
        pickup_table_name = 'pickup_table'
        if not pickup_table_was_skipped and any(f['name'] == pickup_table_name for f in fixtures_to_plan):
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
            processing_order = [item for item in processing_order if item[0] != shortest_segment_id]
        elif pickup_table_was_skipped:
             print("  -> Skipping special 'pickup_table' placement as it was not required.")
        # --- [END MODIFICATION] ---

        # --- [THIS IS THE FIX] ---
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

            # --- [START OF NEW INSET LOGIC] ---
            inset_for_corners = 100.0 # Standard 100mm inset
            segment_index = next((i for i, (sid, _) in enumerate(processing_order) if sid == seg_id), -1)

            if segment_index == 0:
                # This is the FIRST segment (e.g., the Top wall), start at 0.
                cursor = 400.0
                print(f"\n  -> Planning Segment {seg_id} (Length: {seg_len:.0f}mm) - Starting at edge (cursor 0).")
            else:
                # This is a SUBSEQUENT segment, apply inset to avoid corner collision.
                cursor = inset_for_corners
                print(f"\n  -> Planning Segment {seg_id} (Length: {seg_len:.0f}mm) - Starting with {inset_for_corners}mm inset.")
            # --- [END OF NEW INSET LOGIC] ---

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

        # --- 6. FINALIZE AND RETURN THE PLAN ---
        if fixtures_to_plan:
            print(f"  -> ⚠️ WARNING: Could not plan for {len(fixtures_to_plan)} fixtures. Not enough wall space.")

        print(f"\n--- ✅ BOH Placement Plan Complete. Generated {len(placement_plan)} placements. ---")
        return placement_plan

        
    def get_boh_zone_wall_segment_rect(self, doc) -> dict:
        """
        [MODIFIED] Analyzes the BOH zone polygon and returns details for each of its wall segments,
        starting from the bottom-right corner and proceeding counter-clockwise.
        """

        print("\n--- 🧱 Analyzing BOH Zone Wall Segments (Bottom-Right, CCW) ---")

        # 1. Get the ordered perimeter path using the new helper function
        perimeter_path = self._get_boh_perimeter_path_from_bottom_right_ccw(doc)
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
    
    def execute_boh_placement_plan(self, doc, placement_plan: list):
        """
        Executes a pre-computed BOH placement plan, drawing each fixture in the DXF.

        This function iterates through the plan generated by 'plan_boh_fixture_placement'.
        For each item in the plan, it:
        1. Loads the specified fixture object.
        2. Places it at the calculated (x, y) coordinates with the correct angle.
        3. Calculates the bounding box of the newly placed fixture.
        4. Adds this bounding box to the master 'placed_bboxes' list to prevent future overlaps.
        """

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
                block_ref = doc.place_fixture(fxtr, (x, y, 0), angle, rotated=True)

                # After placing, calculate its bounding box and register it as an obstacle
                if block_ref:
                    try:
                        bbox = extents([block_ref])
                        doc.placed_bboxes.append((bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y))
                        placed_count += 1
                    except (RuntimeError, TypeError):
                        print(f"  -> ⚠️ WARNING: Could not calculate bounding box for placed fixture '{fixture_name}'.")

            except Exception as e:
                print(f"  -> ⚠️ WARNING: Could not place fixture '{fixture_name}'. Skipping. Error: {e}")
                continue
        
        print(f"\n--- ✅ BOH Placement Execution Complete. Placed {placed_count} fixtures. ---")

    def draw_and_get_pickup_curtain_bbox(
        self, doc,
        extend_left: float = 750.0,
        extend_right: float = 750.0,
        extend_top: float = 750.0,
        extend_bottom: float = 750.0,
        draw_visual: bool = True
    ) -> List[Tuple[float, float, float, float]]:
        """
        [NEW FUNCTION - V4 - CONSTRAINED BY BOH ZONE]
        Finds the 'pickup_table' fixture(s), gets the 'TABLE' layer geometry,
        extends it on four sides, and THEN clips (intersects) the resulting
        box with the 'boh_zone_poly' to ensure it CANNOT go outside.
        """

        print(f"\n--- 🔍 Drawing Pickup Table Curtain (CONSTRAINED to BOH Zone) ---")
        print(f"    Extensions (L/R/T/B): {extend_left}/{extend_right}/{extend_top}/{extend_bottom}")

        curtain_bboxes = []
        layer_name = "PICKUP_TABLE_CURTAIN"

        # --- NEW: Get the BOH Zone Polygon for clipping ---
        boh_zone_poly = self._get_boh_zone_polygon(doc)
        if not boh_zone_poly or boh_zone_poly.is_empty:
            print("  -> ⚠️ FAILED: BOH zone polygon not found. Cannot create any curtain box.")
            return curtain_bboxes
        print("  -> Successfully loaded BOH zone for clipping.")
        # --- END NEW ---

        # --- 1. Query for the pickup_table fixtures ---
        pickup_table_entities = [
            e for e in doc.msp.query('INSERT')
            if "PICKUP_TABLE" in e.dxf.name.upper()
        ]
        if not pickup_table_entities:
            print("  -> No 'pickup_table' fixtures found in the drawing.")
            return curtain_bboxes
        
        print(f"  -> Found {len(pickup_table_entities)} 'pickup_table' fixture(s).")

        # --- 2. Process each found fixture ---
        for i, entity in enumerate(pickup_table_entities):
            print(f"  -> Processing fixture {i+1} ('{entity.dxf.name}')...")
            base_min_x, base_min_y, base_max_x, base_max_y = None, None, None, None

            try:
                # --- 3. Find 'TABLE' layer geometry (Same as before) ---
                block = doc.doc.blocks.get(entity.dxf.name)
                if not block:
                    print(f"    -> WARNING: Block definition '{entity.dxf.name}' not found. Using overall fixture.")
                    overall_bbox = extents([entity])
                    if not overall_bbox.has_data:
                        print(f"    -> Skipping fixture {i+1}: Could not calculate overall bounding box.")
                        continue
                    base_min_x, base_min_y = overall_bbox.extmin.x, overall_bbox.extmin.y
                    base_max_x, base_max_y = overall_bbox.extmax.x, overall_bbox.extmax.y
                else:
                    table_layer_entities = [
                        e for e in block if e.dxf.layer == 'TABLE'
                    ]
                    if table_layer_entities:
                        local_table_bbox = extents(table_layer_entities)
                        if local_table_bbox.has_data:
                            transform_matrix = entity.matrix44()
                            extmin, extmax = local_table_bbox.extmin, local_table_bbox.extmax
                            local_corners = [
                                Vec3(extmin.x, extmin.y, extmin.z), Vec3(extmax.x, extmin.y, extmin.z),
                                Vec3(extmax.x, extmax.y, extmin.z), Vec3(extmin.x, extmax.y, extmin.z),
                                Vec3(extmin.x, extmin.y, extmax.z), Vec3(extmax.x, extmin.y, extmax.z),
                                Vec3(extmax.x, extmax.y, extmax.z), Vec3(extmin.x, extmax.y, extmax.z)
                            ]
                            world_corners = list(transform_matrix.transform_vertices(local_corners))
                            wcs_table_bbox = BoundingBox(world_corners)
                            base_min_x, base_min_y = wcs_table_bbox.extmin.x, wcs_table_bbox.extmin.y
                            base_max_x, base_max_y = wcs_table_bbox.extmax.x, wcs_table_bbox.extmax.y
                            print(f"    -> Using 'TABLE' geometry for bounding box.")
                        else:
                            print(f"    -> WARNING: Could not calculate bbox for 'TABLE' entities. Using fallback.")
                            overall_bbox = extents([entity])
                            if overall_bbox.has_data:
                                base_min_x, base_min_y = overall_bbox.extmin.x, overall_bbox.extmin.y
                                base_max_x, base_max_y = overall_bbox.extmax.x, overall_bbox.extmax.y
                            else: continue
                    else:
                        print(f"    -> WARNING: No entities found on 'TABLE' layer. Using fallback.")
                        overall_bbox = extents([entity])
                        if overall_bbox.has_data:
                            base_min_x, base_min_y = overall_bbox.extmin.x, overall_bbox.extmin.y
                            base_max_x, base_max_y = overall_bbox.extmax.x, overall_bbox.extmax.y
                        else: continue

                # --- 4. Apply Unconstrained Extensions ---
                offset_min_x = base_min_x - extend_left
                offset_min_y = base_min_y - extend_bottom
                offset_max_x = base_max_x + extend_right
                offset_max_y = base_max_y + extend_top
                
                # Create the unconstrained Shapely box
                unconstrained_box = box(offset_min_x, offset_min_y, offset_max_x, offset_max_y)

                # --- 5. NEW: Constrain (clip) the box ---
                constrained_poly = boh_zone_poly.intersection(unconstrained_box)
                
                if constrained_poly.is_empty:
                    print(f"    -> ⚠️ WARNING: Extended box for {entity.dxf.name} does not overlap BOH zone. Skipping.")
                    continue
                
                # Get the bounds of the *final clipped shape*
                c_min_x, c_min_y, c_max_x, c_max_y = constrained_poly.bounds
                constrained_coords = (c_min_x, c_min_y, c_max_x, c_max_y)
                # --- END NEW ---

                curtain_bboxes.append(constrained_coords)
                print(f"    -> Calculated CONSTRAINED curtain box: {constrained_coords}")

                # --- 6. Optionally draw the *constrained* box ---
                if draw_visual:
                    if layer_name not in doc.doc.layers:
                        doc.doc.layers.add(name=layer_name, color=4) # Cyan
                    
                    # Draw the clipped polygon's exterior (handles non-rectangular shapes)
                    doc.msp.add_lwpolyline(
                        list(constrained_poly.exterior.coords), 
                        close=True, 
                        dxfattribs={"layer": layer_name}
                    )
                    print(f"      -> Drawn CONSTRAINED curtain box on layer '{layer_name}'.")

            except Exception as e:
                print(f"    -> ⚠️ ERROR processing fixture {i+1} ('{entity.dxf.name}'): {e}")
                import traceback
                traceback.print_exc()
                continue

        print(f"--- ✅ Finished Pickup Table Curtain Detection (CONSTRAINED) ---")
        return curtain_bboxes

    #--RASHEEQUE-ADDED-NEW-FUNCTIONS---10-11-2025----1:22-Night-----------------
    def _get_boh_wall_polygons(self, doc) -> Tuple[Optional[Polygon], Optional[Polygon], Optional[Polygon]]:
        """
        Finds the inner and outer BOH wall outlines and returns them,
        along with the polygon representing the wall area itself.
        """
        boh_outlines = list(doc.msp.query('LWPOLYLINE[layer=="BOH_WALL_VALID_OUTLINE"]'))
        if not boh_outlines:
            boh_outlines = list(doc.msp.query('LWPOLYLINE[layer=="BOH_PARTITION_OUTLINE"]'))

        if len(boh_outlines) < 2:
            # Try to find the single polygon and buffer it, assuming it's the inner one
            if len(boh_outlines) == 1:
                try:
                    inner_poly = Polygon(list(boh_outlines[0].get_points('xy')))
                    wall_thickness = 50.0 # Standard wall thickness
                    outer_poly = inner_poly.buffer(wall_thickness)
                    wall_poly = outer_poly.difference(inner_poly)
                    return inner_poly, outer_poly, wall_poly
                except Exception:
                    return None, None, None
            return None, None, None

        try:
            polygons = [Polygon(list(p.get_points('xy'))) for p in boh_outlines]
            
            # The inner polygon is the one with the smaller area
            inner_poly = min(polygons, key=lambda p: p.area)
            # The outer polygon is the one with the larger area
            outer_poly = max(polygons, key=lambda p: p.area)
            
            # The wall itself is the difference
            wall_poly = outer_poly.difference(inner_poly)
            
            return inner_poly, outer_poly, wall_poly
        
        except Exception as e:
            print(f"  -> ⚠️ ERROR in _get_boh_wall_polygons: {e}")
            return None, None, None

    
    #--RASHEEQUE-ADDED-NEW-FUNCTIONS---10-11-2025----1:22-Night-----------------
    def draw_and_boh_zone_door(
        self, doc,
        extend_left: float = 750.0,
        extend_right: float = 750.0,
        extend_top: float = 750.0,
        extend_bottom: float = 750.0,
        draw_visual: bool = True,
        color: int = 4
    ) -> List[Tuple[float, float, float, float]]:
        """
        [MODIFIED]
        Finds the 'pickup_table' fixture(s), gets its 'TABLE' layer geometry,
        extends it, and then clips (intersects) the resulting
        box with the BOH *wall* area, so it only draws inside the wall.
        """

        print(f"\n--- 🔍 Drawing BOH Door (CONSTRAINED to BOH Wall) ---") # Modified print
        print(f"    Extensions (L/R/T/B): {extend_left}/{extend_right}/{extend_top}/{extend_bottom}")

        curtain_bboxes = []
        layer_name = "BOH_ZONE_DOOR"

        # --- MODIFICATION: Get the BOH *wall* polygon ---
        inner_poly, outer_poly, boh_wall_poly = self._get_boh_wall_polygons(doc)
        
        if not boh_wall_poly or boh_wall_poly.is_empty:
            print("  -> ⚠️ FAILED: BOH wall polygon not found. Cannot create any door.")
            return curtain_bboxes
        print("  -> Successfully loaded BOH wall polygon for clipping.")
        # --- END MODIFICATION ---

        # --- 1. Query for the pickup_table fixtures ---
        pickup_table_entities = [
            e for e in doc.msp.query('INSERT')
            if "PICKUP_TABLE" in e.dxf.name.upper()
        ]
        if not pickup_table_entities:
            print("  -> No 'pickup_table' fixtures found in the drawing.")
            return curtain_bboxes
        
        print(f"  -> Found {len(pickup_table_entities)} 'pickup_table' fixture(s).")

        # --- 2. Process each found fixture ---
        for i, entity in enumerate(pickup_table_entities):
            print(f"  -> Processing fixture {i+1} ('{entity.dxf.name}')...")
            base_min_x, base_min_y, base_max_x, base_max_y = None, None, None, None

            try:
                # --- 3. Find 'TABLE' layer geometry (Same as before) ---
                block = doc.doc.blocks.get(entity.dxf.name)
                if not block:
                    print(f"    -> WARNING: Block definition '{entity.dxf.name}' not found. Using overall fixture.")
                    overall_bbox = extents([entity])
                    if not overall_bbox.has_data:
                        print(f"    -> Skipping fixture {i+1}: Could not calculate overall bounding box.")
                        continue
                    base_min_x, base_min_y = overall_bbox.extmin.x, overall_bbox.extmin.y
                    base_max_x, base_max_y = overall_bbox.extmax.x, overall_bbox.extmax.y
                else:
                    table_layer_entities = [
                        e for e in block if e.dxf.layer == 'TABLE'
                    ]
                    if table_layer_entities:
                        local_table_bbox = extents(table_layer_entities)
                        if local_table_bbox.has_data:
                            transform_matrix = entity.matrix44()
                            extmin, extmax = local_table_bbox.extmin, local_table_bbox.extmax
                            local_corners = [
                                Vec3(extmin.x, extmin.y, extmin.z), Vec3(extmax.x, extmin.y, extmin.z),
                                Vec3(extmax.x, extmax.y, extmin.z), Vec3(extmin.x, extmax.y, extmin.z),
                                Vec3(extmin.x, extmin.y, extmax.z), Vec3(extmax.x, extmin.y, extmax.z),
                                Vec3(extmax.x, extmax.y, extmax.z), Vec3(extmin.x, extmax.y, extmax.z)
                            ]
                            world_corners = list(transform_matrix.transform_vertices(local_corners))
                            wcs_table_bbox = BoundingBox(world_corners)
                            base_min_x, base_min_y = wcs_table_bbox.extmin.x, wcs_table_bbox.extmin.y
                            base_max_x, base_max_y = wcs_table_bbox.extmax.x, wcs_table_bbox.extmax.y
                            print(f"    -> Using 'TABLE' geometry for bounding box.")
                        else:
                            print(f"    -> WARNING: Could not calculate bbox for 'TABLE' entities. Using fallback.")
                            overall_bbox = extents([entity])
                            if overall_bbox.has_data:
                                base_min_x, base_min_y = overall_bbox.extmin.x, overall_bbox.extmin.y
                                base_max_x, base_max_y = overall_bbox.extmax.x, overall_bbox.extmax.y
                            else: continue
                    else:
                        print(f"    -> WARNING: No entities found on 'TABLE' layer. Using fallback.")
                        overall_bbox = extents([entity])
                        if overall_bbox.has_data:
                            base_min_x, base_min_y = overall_bbox.extmin.x, overall_bbox.extmin.y
                            base_max_x, base_max_y = overall_bbox.extmax.x, overall_bbox.extmax.y
                        else: continue

                # --- 4. Apply Unconstrained Extensions ---
                offset_min_x = base_min_x - extend_left
                offset_min_y = base_min_y - extend_bottom
                offset_max_x = base_max_x + extend_right
                offset_max_y = base_max_y + extend_top
                
                # Create the unconstrained Shapely box
                unconstrained_box = box(offset_min_x, offset_min_y, offset_max_x, offset_max_y)

                # --- 5. MODIFICATION: Constrain to the WALL polygon ---
                constrained_poly = boh_wall_poly.intersection(unconstrained_box)
                
                if constrained_poly.is_empty:
                    print(f"    -> ⚠️ WARNING: Extended box for {entity.dxf.name} does not overlap BOH *wall*. Skipping.")
                    continue
                # --- END MODIFICATION ---
                
                # Get the bounds of the *final clipped shape*
                c_min_x, c_min_y, c_max_x, c_max_y = constrained_poly.bounds
                constrained_coords = (c_min_x, c_min_y, c_max_x, c_max_y)

                curtain_bboxes.append(constrained_coords)
                print(f"    -> Calculated CONSTRAINED (to wall) door box: {constrained_coords}")

                # --- 6. Optionally draw the *constrained* box AND HATCH ---
                if draw_visual:
                    if layer_name not in doc.doc.layers:
                        doc.doc.layers.add(name=layer_name, color=3) 
                    
                    # Get the coordinates for the boundary
                    # Handle MultiPolygons just in case the intersection creates separate pieces
                    if constrained_poly.geom_type == 'Polygon':
                        geoms_to_draw = [constrained_poly]
                    elif constrained_poly.geom_type == 'MultiPolygon':
                        geoms_to_draw = list(constrained_poly.geoms)
                    else:
                        geoms_to_draw = []

                    for poly_geom in geoms_to_draw:
                        boundary_coords = list(poly_geom.exterior.coords)

                        # Draw the clipped polygon's exterior
                        doc.msp.add_lwpolyline(
                            boundary_coords, 
                            close=True, 
                            dxfattribs={"layer": layer_name}
                        )
                        
                        # --- ADDED HATCH ---
                        try:
                            hatch = doc.msp.add_hatch(
                                color=3, 
                                dxfattribs={"layer": layer_name}
                            )
                            # Use a simple diagonal line pattern
                            hatch.set_pattern_fill('ANSI31', scale=1.0, angle=10) 
                            
                            # Add the polygon boundary to the hatch
                            hatch.paths.add_polyline_path(boundary_coords, is_closed=True)
                            
                            # Add holes for any interiors
                            for interior in poly_geom.interiors:
                                hatch.paths.add_polyline_path(list(interior.coords), is_closed=True, flags=DXFCONST.BOUNDARY_PATH_OUTER)
                                
                        except Exception as e:
                            print(f"      -> ⚠️ WARNING: Could not add hatch to door box: {e}")
                        # --- END ADDED HATCH ---
                        
                    print(f"      -> Drawn CONSTRAINED door box and hatch on layer '{layer_name}'.")

            except Exception as e:
                print(f"    -> ⚠️ ERROR processing fixture {i+1} ('{entity.dxf.name}'): {e}")
                import traceback
                traceback.print_exc()
                continue

        print(f"--- ✅ Finished BOH Door Detection (CONSTRAINED to Wall) ---")
        return curtain_bboxes

    
    def _expand_boh_zone_downwards_if_needed(self, 
                                             initial_boh_poly: Polygon, 
                                             initial_slicer_box: box, 
                                             floorplan: Polygon,
                                             # --- NEW PARAMETER ---
                                             obstacles_to_avoid: Optional[Polygon] = None,
                                             TARGET_BOH_SQFT = 60.0
                                             ) -> Polygon:
        """
        [MODIFIED] Checks if the initial BOH polygon meets a minimum area requirement.
        If not, it iteratively expands the polygon DOWNWARDS until it meets a
        target area or can no longer expand, **now subtracting specified obstacles**.
        """
        # --- 1. Define Constants ---
        MIN_BOH_SQFT = 90.0
        # TARGET_BOH_SQFT = 60.0
        SQMM_PER_SQFT = 92903.04
        NUDGE_MM = 100.0
        MAX_ITERATIONS = 50 # Safety break

        # --- 2. Calculate Initial Area ---
        initial_area_sqft = initial_boh_poly.area / SQMM_PER_SQFT
        print(f"  -> Initial BOH zone area is {initial_area_sqft:.2f} sq. ft.")
        
        if obstacles_to_avoid and not obstacles_to_avoid.is_empty:
            print("  -> Expansion will avoid the registered clinic door aisles.")

        # --- 3. Check Condition and Start Expansion Loop ---
        if initial_area_sqft < MIN_BOH_SQFT:
            print(f"  -> Area is less than {MIN_BOH_SQFT} sq. ft. Attempting to expand downwards to at least {TARGET_BOH_SQFT} sq. ft.")
            
            current_poly = initial_boh_poly
            current_slicer = initial_slicer_box
            iterations = 0

            while (current_poly.area / SQMM_PER_SQFT) < TARGET_BOH_SQFT and iterations < MAX_ITERATIONS:
                iterations += 1
                
                min_x, min_y, max_x, max_y = current_slicer.bounds
                expanded_slicer_box = box(min_x, min_y - NUDGE_MM, max_x, max_y)
                
                # Intersect with the floorplan first
                new_poly = floorplan.intersection(expanded_slicer_box)
                
                # --- NEW LOGIC ---
                # Now, subtract the obstacles from the potential new area
                if obstacles_to_avoid and not obstacles_to_avoid.is_empty:
                    new_poly = new_poly.difference(obstacles_to_avoid)
                # --- END NEW LOGIC ---

                if new_poly.is_empty or new_poly.area <= current_poly.area:
                    print(f"    -> Iteration {iterations}: Downward expansion failed (hit obstacle or wall). Stopping.")
                    break
                
                current_poly = new_poly
                current_slicer = expanded_slicer_box
            
            # --- 4. Return the Final Polygon ---
            if (current_poly.area / SQMM_PER_SQFT) >= TARGET_BOH_SQFT:
                print(f"  -> ✅ Successfully expanded BOH zone to {current_poly.area / SQMM_PER_SQFT:.2f} sq. ft.")
                return current_poly
            else:
                print(f"  -> ⚠️ WARNING: Could not expand BOH to target area. Using last valid size of {current_poly.area / SQMM_PER_SQFT:.2f} sq. ft.")
                return current_poly
        
        return initial_boh_poly
    
    def get_boh_zone_wall_segment(self, doc, pickup_curtain_bboxes: List[tuple]) -> dict:
        """
        [CORRECTED & MODIFIED] Analyzes the BOH zone polygon, gets the raw segments,
        and then reduces the effective length based on corner geometry AND
        trims any segments that overlap the pickup curtain zone.
        """

        print("\n--- 🧱 Analyzing BOH Zone Wall Segments (Bottom-Right, CCW) ---")

        # 1. Get the ordered perimeter path (raw, unadjusted coordinates)
        perimeter_path = self._get_boh_perimeter_path_from_bottom_right_ccw(doc)
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
        boh_internal_corners = self._find_internal_corners_from_raw_data(unadjusted_segments)
        corner_points_set = {
            (round(c['point'][0]), round(c['point'][1])) for c in boh_internal_corners
        }

        print(corner_points_set)

        # 4. NEW: CREATE PICKUP CURTAIN OBSTACLE SHAPE
        pickup_obstacle_poly = None
        if pickup_curtain_bboxes:
            try:
                pickup_polygons = [box(*bbox) for bbox in pickup_curtain_bboxes]
                # Combine all pickup zones and add a buffer (similar to corners)
                pickup_obstacle_poly = unary_union(pickup_polygons).buffer(10.0) 
                print(f"  -> Applying {len(pickup_polygons)} pickup curtain obstacle(s) with 300mm buffer for trimming.")
            except Exception as e:
                print(f"  -> ⚠️ WARNING: Could not create pickup curtain obstacle shape: {e}")
                pickup_obstacle_poly = None
        
        # 5. APPLY SEGMENT REDUCTION & TRIMMING LOGIC
        wall_segments_data = {}
        CORNER_RESERVATION_MM = 300.0 
        
        segments_after_corner_trim = [] # Store lines for trimming

        # --- First Pass: Apply Internal Corner Trimming (Your existing logic) ---
        print("  -> Pass 1: Trimming segments for internal corners...")
        for i in sorted(unadjusted_segments.keys()):
            seg_data = unadjusted_segments[i]
            p1 = Vec2(seg_data['start_point'])
            p2 = Vec2(seg_data['end_point'])
            segment_vector = seg_data['vector'].normalize()
            
            effective_p1 = p1
            effective_p2 = p2

            if (round(p2.x), round(p2.y)) in corner_points_set:
                effective_p2 = p2 - segment_vector * CORNER_RESERVATION_MM
                print(f"  -> Segment {i} ENDS at internal corner. Trimming 300mm.")
            
            if (round(p1.x), round(p1.y)) in corner_points_set:
                effective_p1 = p1 + segment_vector * CORNER_RESERVATION_MM
                print(f"  -> Segment {i} STARTS at internal corner. Trimming 300mm.")
            
            if effective_p1.distance(effective_p2) > 50: # Only keep if it still has length
                segments_after_corner_trim.append(LineString([effective_p1, effective_p2]))
        
        print(f"  -> Segments after corner trimming: {len(segments_after_corner_trim)}")

        # --- Second Pass: Apply Pickup Curtain Trimming (NEW) ---
        final_trimmed_segments = []
        if pickup_obstacle_poly and not pickup_obstacle_poly.is_empty:
            print("  -> Pass 2: Trimming segments against pickup curtain obstacle...")
            for segment_line in segments_after_corner_trim:
                # Use shapely's .difference() to "cut" the segment
                remaining_geometry = segment_line.difference(pickup_obstacle_poly)
                
                if remaining_geometry.is_empty:
                    print(f"    -> Segment from {segment_line.coords[0]} was fully removed by pickup curtain.")
                    continue
                elif remaining_geometry.geom_type == 'LineString':
                    final_trimmed_segments.append(remaining_geometry)
                elif remaining_geometry.geom_type == 'MultiLineString':
                    # If the obstacle was in the middle, this adds the pieces on either side
                    final_trimmed_segments.extend(list(remaining_geometry.geoms))
            
            print(f"  -> Segments after pickup curtain trimming: {len(final_trimmed_segments)}")
        else:
            print("  -> Pass 2: No pickup curtain obstacle to apply. Skipping.")
            final_trimmed_segments = segments_after_corner_trim # Use the list from Pass 1
        
        # --- Final Pass: Convert valid LineStrings back to the data dict ---
        for i, line in enumerate(final_trimmed_segments):
            # Final validation check
            if line.length > 450.0:
                p1_vec = Vec2(line.coords[0])
                p2_vec = Vec2(line.coords[-1])
                segment_vector_vec = (p2_vec - p1_vec).normalize()
                
                wall_segments_data[i] = { # Use 'i' as the new, sequential key
                    'start_point': (p1_vec.x, p1_vec.y),
                    'end_point': (p2_vec.x, p2_vec.y),
                    'length': line.length,
                    'angle': math.degrees(segment_vector_vec.angle)
                }

        print(f"  -> ✅ Successfully identified {len(wall_segments_data)} final placeable segments.")
        return wall_segments_data
    
########################################################################################################################
########################################################################################################################
########################################            BACK WALL           ################################################
########################################            BACK WALL           ################################################
########################################            BACK WALL           ################################################
########################################################################################################################
########################################################################################################################

    def draw_back_wall(self):
        print("draw back wall")
        gap_threshold = 150
        layer_name = "BACK_WALL"
        hatch_color = 252
        door_width = 650

        for doc in self.docs:
            if doc.skip:
                continue

            doc.back_wall_y = self.cvc.max_y

            # get bottom of BOH
            boh_zone = self._get_boh_zone_polygon(doc)
            if not boh_zone:
                print("  -> ⚠️ FAILED: Could not find BOH zone to place back wall")
                doc.skip = True
                print("SKIP DOC")
                continue
            
            # get bottom of clinic
            back_side_entities = []
            pickup_ents = []
            back_side_types = {'clinic'}
            pickup_ent_typ = {"pickup_window"}
            
            for entity in doc.msp.query('INSERT'):
                block_name_upper = entity.dxf.name.upper()
                best_match_key = ""
                for key in self.fixture_dict.keys():
                    sanitized_key = key.upper().replace(" ", "_")
                    if block_name_upper.startswith(sanitized_key):
                        if len(key) > len(best_match_key):
                            best_match_key = key
                
                print("best_match_key: ", best_match_key)
                
                if best_match_key and self.fixture_dict[best_match_key].get("type") in back_side_types:
                    bbox = extents(entity.virtual_entities())
                    if bbox.has_data:
                        minx, miny, minz = bbox.extmin
                        maxx, maxy, maxz = bbox.extmax
                        area = (maxx-minx)*(maxy-miny)

                        back_side_entities.append(entity)

                elif best_match_key and self.fixture_dict[best_match_key].get("type") in pickup_ent_typ:
                    bbox = extents(entity.virtual_entities())
                    if bbox.has_data:
                        minx, miny, minz = bbox.extmin
                        maxx, maxy, maxz = bbox.extmax
                        area = (maxx-minx)*(maxy-miny)
                        
                        pickup_ents.append(entity)

            if not back_side_entities:
                print("  -> ⚠️ SKIPPED: No back-side fixtures found to define the back wall.")
                doc.skip = True
                print("SKIP DOC")
                continue
            
            pickup_room = False
            print("PIKCUP ENTS:", len(pickup_ents))
            if len(pickup_ents) > 0:
                pickup_room = True
                puw_bbox = extents(pickup_ents)
                print("PUW BB:", puw_bbox.extmin, puw_bbox.extmax)
                boh_zone = Polygon([(puw_bbox.extmin[0], puw_bbox.extmin[1]), (puw_bbox.extmax[0], puw_bbox.extmin[1]), (puw_bbox.extmax[0], puw_bbox.extmax[1]), (puw_bbox.extmin[0], puw_bbox.extmax[1])])
            y_val = boh_zone.bounds[1]

            combined_bbox = extents(back_side_entities)
            print("combined_bbox:", combined_bbox.extmin, combined_bbox.extmax)

            # within thhreshold --> draw line below clinic
            if abs(boh_zone.bounds[1] - combined_bbox.extmin[1]) < gap_threshold:
                print(1)
                y_val = min(boh_zone.bounds[1], combined_bbox.extmin[1])
            else:

                print("get bottom clinic door")
                placed_clinic_entities = [
                    e for e in doc.msp.query('INSERT')
                    if "CLINIC" in e.dxf.name.upper() # Check if "CLINIC" is anywhere in the uppercase name
                ]

                if not placed_clinic_entities:
                    print("  -> No placed clinic entities found.")
                    continue

                min_y = self.cvc.max_x
                for clinic_entity in placed_clinic_entities:
                    # Call the helper method to get the bounding box
                    door_bbox = self.get_clinic_door_by_layer(clinic_entity)
                    if door_bbox:
                        min_y = min(door_bbox[1], min_y)
                # print(min_y)

                # within thhreshold --> draw line below clinic
                if abs(boh_zone.bounds[1] - min_y) < gap_threshold:
                    print(2)
                    y_val = min(boh_zone.bounds[1], min_y)
                else:
                    y_val = max(boh_zone.bounds[1], combined_bbox.extmin[1])

            # draw line
            
            print(y_val)
            doc.back_wall_y = y_val

            boh_outlines = [
                p for p in doc.msp.query('LWPOLYLINE') 
                if "BOH_WALL_" in p.dxf.layer and p.dxf.layer.endswith("_OUTLINE")
            ]
            boh = boh_outlines[0]
            for b in boh_outlines:
                if len(b) < len(boh):
                    boh = b
            boh = boh[:-1]
            
            boh_segs = []
            for i, c in enumerate(boh):
                c1 = boh[(i+1)%len(boh)]
                p1 = [c[0], c[1], c[2]]
                p2 = [c1[0], c1[1], c1[2]]
                boh_segs.append([p1, p2])

            boh = [[b[0], b[1]] for b in boh]
            
            min_boh = self.cvc.max_y*2
            min_seg = []
            for seg in boh_segs:
                # print(seg)
                temp = seg[0][1] + seg[1][1]
                if min_boh > temp:
                    min_boh = temp
                    min_seg = seg
            
            if not boh_outlines:
                return None

            polygons = [Polygon(list(p.get_points('xy'))) for p in boh_outlines]
            # y_val += 10
            clinic_polygons = self._get_all_clinic_polygons(doc)
            best, gaps = self.horizontal_line_clear_of_entities(y0=y_val, bboxes=clinic_polygons, boh=boh_zone, boh_seg=min_seg, span=[self.cvc.min_x, self.cvc.max_x])
            # gaps = [[self.cvc.min_x, self.cvc.max_x]]
            if layer_name not in doc.doc.layers:
                doc.doc.layers.add(name=layer_name, color=1) # Red
                doc.doc.layers.add(name=layer_name + "_DOOR", color=1) # Red
            for gap in gaps:
                x0, x1 = gap
                
                wall_line = LineString([[x0, y_val], [x1, y_val]])
                wall_poly = wall_line.buffer(25)

                hatch = doc.msp.add_hatch(color=hatch_color)
                hatch.dxf.layer = layer_name
                
                # 3. Add the outer boundary of THIS polygon
                outer_path = hatch.paths.add_edge_path()
                outer_coords = list(wall_poly.exterior.coords)
                for i in range(len(outer_coords) - 1):
                    outer_path.add_line(outer_coords[i], outer_coords[i+1])

                # 5. Set the visual style of the hatch pattern
                hatch.set_pattern_fill('ANSI32', scale=10)
                hatch.dxf.pattern_angle = 90

                # 6. Add Explicit Wall Outlines for THIS polygon
                doc.msp.add_lwpolyline(
                    outer_coords, 
                    close=True, 
                    dxfattribs={"layer": layer_name, "color": 251, "lineweight": 25}
                )

                start = x0
                end = x1
                blocked = False
                placed = False
                print("", x0, x1)
                while start < end - door_width:
                    door_access_box = box(start, y_val + 1, start + door_width, y_val + 1 + door_width)
                    print("check against: ", door_access_box)
                    for p in clinic_polygons:
                        if not blocked:
                            constrained_area = door_access_box.intersection(box(p.bounds[0], p.bounds[1], p.bounds[2], p.bounds[3]))
                            # print(dir(constrained_area))
                            if not constrained_area.is_empty:
                                print(type(constrained_area))
                                print("\t", p.bounds)

                                print("\t", "Update blocked")
                                blocked = True
                                placed = False
                    # check if it intersects BOH
                    if not blocked:
                        constrained_area = door_access_box.intersection(box(boh_zone.bounds[0], boh_zone.bounds[1], boh_zone.bounds[2], boh_zone.bounds[3]))
                        if not constrained_area.is_empty:
                            self.polygon_intersects_box(boh, (boh_zone.bounds[0], boh_zone.bounds[1], boh_zone.bounds[2], boh_zone.bounds[3]), include_touches=False)

                    print(blocked, placed)
                    if not blocked and not placed:
                        print("\t**placed***", abs(end - start))
                        door_line = LineString([[start, y_val], [start+door_width, y_val]])
                        if abs(end - start) < 1050: # and abs(end - start) > door_width:
                            print("door width (segment) ", start-end)
                            door_line = LineString([[start, y_val], [end, y_val]])
                            start = end
                        door_poly = door_line.buffer(25)

                        hatch = doc.msp.add_hatch(
                            color=3, 
                            dxfattribs={"layer": layer_name + "_DOOR"}
                        )
                        
                        # 3. Add the outer boundary of THIS polygon
                        outer_path = hatch.paths.add_edge_path()
                        outer_coords = list(door_poly.exterior.coords)
                        for i in range(len(outer_coords) - 1):
                            outer_path.add_line(outer_coords[i], outer_coords[i+1])

                        # 5. Set the visual style of the hatch pattern
                        hatch.set_pattern_fill('ANSI31', scale=1.0, angle=10)

                        # 6. Add Explicit Wall Outlines for THIS polygon
                        doc.msp.add_lwpolyline(
                            outer_coords, 
                            close=True, 
                            dxfattribs={"layer": layer_name, "color": 251, "lineweight": 25}
                        )
                        start += door_width
                        placed = True

                    else:
                        if blocked:
                            blocked = False
                        start += 10
                        
                    print()
            print()

    def horizontal_line_clear_of_entities(
        self,
        y0: float,
        bboxes: Iterable,
        boh,
        boh_seg: List[Tuple[float, float]],
        *,
        span: Optional[Tuple[float, float]] = None,
        clearance: float = 0.0,
        eps: float = 1e-6,
    ):
        """
        Compute safe x-intervals for a horizontal line y=y0 that avoids the given entities.

        Args:
            y0: The Y value of the horizontal line.
            entities: Iterable of ezdxf entities (can include INSERTs).
            span: Optional (xmin, xmax) overall span to constrain the line.
                If None, span is derived from the union bbox of all provided entities.
            clearance: Inflate each entity's bbox by this amount.
            eps: Tolerance.

        Returns:
            best: Tuple (x_min, x_max) for the single longest safe segment, or None.
            gaps: List of all safe (x_min, x_max) segments within span.
        """

        # ---- helpers -------------------------------------------------------------
        print("horizontal_line_clear_of_entities")

        def _merge_intervals(intervals: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
            if not intervals:
                return []
            intervals.sort(key=lambda ab: ab[0])
            merged = [intervals[0]]
            for a, b in intervals[1:]:
                la, lb = merged[-1]
                if a <= lb + eps:  # overlap/touch
                    merged[-1] = (la, max(lb, b))
                else:
                    merged.append((a, b))
            return merged

        # ---- collect bboxes & determine working span ----------------------------
        print(y0)
        bboxes = [b.bounds for b in bboxes]
        for bbox in bboxes:
            print(bbox)
        if span is None:
            if not bboxes:
                return None, []
            X0 = min(bb[0] for bb in bboxes) - clearance
            X1 = max(bb[2] for bb in bboxes) + clearance
        else:
            X0, X1 = sorted(span)

        print(X0, X1)

        # ---- build blocked intervals at y=y0 ------------------------------------

        blocked: List[Tuple[float, float]] = []
        for xmin, ymin, xmax, ymax in bboxes:
            print("CHECK BLOCKED")
            # xmin, ymin, zmin = bbox.extmin
            # xmax, ymax, zmax = bbox.extmax
            ax = xmin - clearance
            bx = xmax + clearance
            ay = ymin - clearance
            by = ymax + clearance
            print(ax, ay, bx, by)
            if ay - eps <= y0 <= by + eps:
                print("BLOCKED")
                a = max(X0, ax)
                b = min(X1, bx)
                if a <= b:
                    blocked.append((a, b))
        if boh:
            print("BOH BOUNDS HORIZONTAL BLOCK")
            xmin, ymin, xmax, ymax = boh.bounds
            ax = xmin - clearance
            bx = xmax + clearance
            ay = ymin - clearance
            by = ymax + clearance
            print(ay, by)
            if ay - eps <= y0 <= by + eps:
                print("BLOCKED")
                a = max(X0, xmin)
                b = min(X1, xmax)
                if a <= b:
                    blocked.append((a, b))
        print(blocked)

        blocked = _merge_intervals(blocked)

        # ---- subtract from span to get gaps -------------------------------------

        gaps: List[Tuple[float, float]] = []
        cur = X0
        for a, b in blocked:
            if b <= cur + eps:
                continue
            if a > cur + eps:
                gaps.append((cur, a))
            cur = max(cur, b)
        if cur < X1 - eps:
            gaps.append((cur, X1))

        gaps = [(a, b) for a, b in gaps if b - a > eps]
        best = max(gaps, key=lambda ab: ab[1]-ab[0]) if gaps else None
        return best, gaps
    
    def polygon_intersects_box(
        self,
        poly_xy,
        rect_bounds,                 # (minx, miny, maxx, maxy)
        *,
        include_touches=True,        # True: count edge/vertex touches as intersection
        fix_invalid=True             # attempt to fix self-crossing rings, etc.
    ) -> bool:
        """
        Return True if the polygon intersects the given box.

        poly_xy: list/iterable of (x, y) tuples; can be closed or open.
        rect_bounds: (minx, miny, maxx, maxy)
        """
        # Build polygon
        poly = Polygon(poly_xy)

        # Optionally heal invalid polygons (from CAD rings, duplicate points, etc.)
        if fix_invalid and not poly.is_valid:
            if _HAS_MAKE_VALID:
                poly = make_valid(poly)
            else:
                # Shapely 1.x fallback
                poly = poly.buffer(0)

        rect = box(*rect_bounds)

        if include_touches:
            # True if they overlap in area OR just touch at edges/vertices
            return poly.intersects(rect)
        else:
            # Require positive-area overlap (no mere touching)
            return poly.intersection(rect).area > 0.0
    
########################################################################################################################
########################################################################################################################
########################################       RETAIL SEPARATION        ################################################
########################################       RETAIL SEPARATION        ################################################
########################################       RETAIL SEPARATION        ################################################
########################################################################################################################
########################################################################################################################

    def draw_retail_separation_line(self, enabled: bool = True, margin: float = 100.0):
        """
        Identifies all "back side" fixtures (clinics, BOH), finds their
        lowest collective point, and draws a horizontal separation line.

        This line is placed on a dedicated layer for visibility control and
        can act as a validation object for subsequent placements.
        """

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

        # from ezdxf.proxygraphic import itervirtualentities

        # --- 1. Identify all "back side" fixtures ---
        for doc in self.docs:
            
            back_side_entities = []
            back_side_types = {'clinic', 'boh', 'boh_preset', 'pickup_window'}
            
            for entity in doc.msp.query('INSERT'):
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
            if layer_name not in doc.doc.layers:
                doc.doc.layers.add(
                    name=layer_name, 
                    color=4,  # Cyan for visibility
                    linetype='DASHED' # Reference the linetype
                )
            
        
            if 'DASHED' not in doc.doc.linetypes:
                # This defines what "DASHED" means: a dash of 200mm, a space of 100mm, repeat.
                doc.doc.linetypes.add(
                    name='DASHED',
                    pattern=[200.0, -100.0],
                    description="Dashed line for separators ----"
                )
            
            
            doc.msp.add_line(start_point, end_point, dxfattribs={"layer": layer_name})
            print(f"  -> ✅ Line drawn on layer '{layer_name}' y={start_point[1]} from x={min_x:.0f} to x={max_x:.0f}.")

            # --- 5. Add a thin bounding box to act as an obstacle for validation ---
            # This makes the "invisible line" a real object for collision detection
            line_obstacle_bbox = (min_x, separation_y - 1, max_x, separation_y + 1)
            print("box:", line_obstacle_bbox)
            doc.placed_bboxes.append(line_obstacle_bbox)
            print("  -> Added line as a validation obstacle.")
    
########################################################################################################################
########################################################################################################################
#########################################       STANDING TABLES        #################################################
#########################################       STANDING TABLES        #################################################
#########################################       STANDING TABLES        #################################################
########################################################################################################################
########################################################################################################################

    def place_standing_tables(self):
        """
        [MODIFIED] Places Standing Tables using a top-down, adaptive row-based strategy.
        - It now finds the nearest obstacles left and right to define a dynamic corridor.
        - Enforces fixed 800mm walking aisles on both sides of the table group.
        - Centers the tables within the remaining space.
        - CONDITIONALLY ignores the RETAIL_SEPARATOR line as an obstacle for Plan B layouts.
        """

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
        for doc in self.docs:
            anchor_y = None
            # This check correctly determines if the Plan B anchor method will be used
            is_plan_b = hasattr(doc, 'clinic_placement_method') and doc.clinic_placement_method == 'Plan_B'

            #*********************************************
            # if is_plan_b:
            #     anchor_y = self._get_new_standing_table_anchor_y()
            # else:
            #     anchor_y = self._get_standing_table_anchor_y()

            
            if is_plan_b:
                last_clinic_coords = self._get_last_clinic_right_bottom_coord(doc)
                anchor_y = self._get_new_standing_table_anchor_y(doc)
                # Extract the actual coordinates if Plan B was used successfully
                if last_clinic_coords:
                    last_clinic_right_edge_x, _ = last_clinic_coords
                    print(f"  -> Plan B Active. Last Clinic Anchor X: {last_clinic_right_edge_x:.0f}")
                else:
                    # If Plan B was active but no clinics were placed, revert to Plan A logic
                    is_plan_b = False
                    anchor_y = self._get_standing_table_anchor_y(doc)
            else:
                anchor_y = self._get_standing_table_anchor_y(doc)

            if anchor_y is None:
                print("  -> ⚠️ FAILED: Could not determine a valid anchor Y-coordinate. Aborting placement.")
                return

            gap_below_anchor = 950
            y_cursor_start = anchor_y - gap_below_anchor - standing_fxtr.height
            print(f"  -> Top boundary found at y={anchor_y:.0f}. Starting first row search at y={y_cursor_start:.0f}.")

            horizontal_gap = 750.0
            vertical_row_gap = 750.0
            fixture_queue = collections.deque([standing_fxtr] * standing_table_count)
        
            # --- NEW LOGIC: Check Plan B status and get coordinates ---
            is_plan_b = hasattr(doc, 'clinic_placement_method') and doc.clinic_placement_method == 'Plan_B'

            #*********************************************
            # Now, check if we are in Plan B. If so, remove the separator line from the obstacles.
            if is_plan_b:
                print("  -> Plan B active: Granting permission for standing tables to cross the separation line.")
                separator_line = doc.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
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
                    all_obstacles = [obs for obs in doc.placed_bboxes if obs != separator_bbox]
                    print("    -> Temporarily removed RETAIL_SEPARATOR as an obstacle for this placement.")
                else:
                    all_obstacles = doc.placed_bboxes
            else:
                all_obstacles = doc.placed_bboxes

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
                # MIN_CORRIDOR_WIDTH = 3000.0
                #---RASHEEQUE
                MIN_CORRIDOR_WIDTH = 3000.0
                #---RASHEEQUE

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
                        doc.place_fixture(fxtr, (current_x + 700, y_cursor + 600, 0), 0, False,xscale= -1.0,yscale=-1.0)
                        doc.placed_bboxes.append((current_x, y_cursor, current_x + fxtr.width, y_cursor + fxtr.height))
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

    def _get_last_clinic_right_bottom_coord(self, doc) -> Optional[Tuple[float, float]]:
        """
        Finds the absolute rightmost X and lowest Y coordinate of the last placed 
        clinic block by analyzing the actual DXF entity geometry (WCS bounding box).
        This version prioritizes clinics placed in the Plan B (lower) zone.
        """
        
        clinic_entities = [e for e in doc.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]

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
        
########################################################################################################################
########################################################################################################################
#########################################        WALL FIXTURES         #################################################
#########################################        WALL FIXTURES         #################################################
#########################################        WALL FIXTURES         #################################################
########################################################################################################################
########################################################################################################################

    def plan_and_place_wall_fixtures(self, primary_side: str, draw_debug: bool = False):
        """
        Orchestrates the entire wall fixture planning and placement process.
        - Finds internal corners to correctly calculate wall lengths.
        - Generates a fixture plan based on available space and merchandise mix.
        - Places the fixtures from the generated plan.
        - Optionally draws debug geometry for validation.
        - RETURNS: The number of remaining (unplaced) wall fixtures and the display calculations.
        """

        print("\n--- 🚀 Orchestrating Wall Fixture Planning and Placement ---")

         # *** ADD THIS LINE HERE - BEFORE ANY WALL PLACEMENT LOGIC ***
        self._get_accurate_obstacle_bboxes(include_all=True, debug=False)
        # *** END OF NEW LINE ***

        # 1. Find corners for BOTH sides first.
        for doc in self.docs:
            if doc.skip:
                continue
            print (f" ----> placing doc {doc.ind}")
            
            right_wall_raw_data = self.get_retail_wall_data(doc, side='right', internal_corners=[])
            internal_corners_on_right_wall = self.find_internal_corners(right_wall_raw_data, side='right')

            left_wall_raw_data = self.get_retail_wall_data(doc, side='left', internal_corners=[])
            internal_corners_on_left_wall = self.find_internal_corners(left_wall_raw_data, side='left')

            # 2. Register internal corners as obstacles (and optionally draw them).
            if internal_corners_on_right_wall:
                if draw_debug:
                    print("\n[DEBUG] Detected Internal Corners on the Right Wall:")
                    for corner in internal_corners_on_right_wall:
                        print(f"  - Corner at: {corner['point']}, Angle In: {corner['angle_in']:.1f}°, Angle Out: {corner['angle_out']:.1f}°")
                self.draw_corner_dummy_boxes(doc, internal_corners_on_right_wall, layer_name="DEBUG_INTERNAL_CORNERS", draw_visual=draw_debug)

            if internal_corners_on_left_wall:
                if draw_debug:
                    print("\n[DEBUG] Detected Internal Corners on the Left Wall:")
                    for corner in internal_corners_on_left_wall:
                        print(f"  - Corner at: {corner['point']}, Angle In: {corner['angle_in']:.1f}°, Angle Out: {corner['angle_out']:.1f}°")
                self.draw_corner_dummy_boxes(doc, internal_corners_on_left_wall, layer_name="DEBUG_INTERNAL_CORNERS", draw_visual=draw_debug)

            # 3. Now, get the CORRECTED wall data by passing the corners you just found.
            right_wall_data = self.get_retail_wall_data(doc, side='right', internal_corners=internal_corners_on_right_wall)
            left_wall_data = self.get_retail_wall_data(doc, side='left', internal_corners=internal_corners_on_left_wall)
        
            if draw_debug:
                print("\n--- [DEBUG] Right Wall Data ---")
                print(json.dumps(right_wall_data, indent=4, default=str))
                print("\n--- [DEBUG] Left Wall Data ---")
                print(json.dumps(left_wall_data, indent=4, default=str))

            
            # 4. Detect Bulges
            right_bulge_details = self.detect_small_bulge_patterns(right_wall_data["segments"], side='right')
            left_bulge_details = self.detect_small_bulge_patterns(left_wall_data["segments"], side='left')

            # 5. VISUALIZE
            # (Pass only the doc, the segments, and the details list)
            if draw_debug:
                self.draw_detected_bulges(doc, right_wall_data["segments"], right_bulge_details)
                self.draw_detected_bulges(doc, left_wall_data["segments"], left_bulge_details)

            
            # 6. STRAIGHTEN WALLS (*** NEW STEP ***)
            right_wall_data = self.straighten_wall_segments(right_wall_data, right_bulge_details, side='right')
            left_wall_data = self.straighten_wall_segments(left_wall_data, left_bulge_details, side='left')
            # END OF NEW STEP


            # # 7. VISUALIZE THE STRAIGHTENING (New Step)
            if draw_debug:
                self.draw_straightened_wall_segments(doc, right_wall_data)
                self.draw_straightened_wall_segments(doc, left_wall_data)

            # --- NEW: APPLY 400mm FACADE INSET TRIM ---
            print("\n--- Applying 400mm Facade Inset Trim ---")
            FACADE_INSET_MM = 400.0
            right_wall_data = self._trim_facade_segment(right_wall_data, FACADE_INSET_MM)
            left_wall_data = self._trim_facade_segment(left_wall_data, FACADE_INSET_MM)
            # --- END OF NEW LOGIC ---

            # if draw_debug:
            #     #  this print statement to reflect the change
            #     print("\n--- [DEBUG] Right Wall Data (After Trim) ---")
            #     print(json.dumps(right_wall_data, indent=4, default=str))
            #     #  this print statement to reflect the change
            #     print("\n--- [DEBUG] Left Wall Data (After Trim) ---")
            #     print(json.dumps(left_wall_data, indent=4, default=str))

            # 8. The rest of the planning logic now uses the CORRECTED data.
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

            #---RASHEEQUE MODIFICATION---STARTS-TO-ADD-REAL-LAYER-NAMES---
            # ******************************************************
            # ***** START: MODIFIED CODE *****
            # ******************************************************
            
            print("  -> Attaching REAL layer information to wall segments...")
            
            # Loop through all segments we found
            for side_name, segment_group in all_wall_segments.items():
                for segment_index, segment_data in segment_group.items():
                    
                    # Get the segment's start and end points
                    seg_coords = segment_data["segment"]
                    p1 = Vec2(seg_coords[0], seg_coords[1])
                    p2 = Vec2(seg_coords[2], seg_coords[3])

                    # Call our new helper function to get the *real* type
                    segment_layer_name = self._check_segment_type(p1, p2)
                    
                    # Store the correct layer name in the dictionary
                    segment_data["layer_name"] = segment_layer_name
            
            print("  -> Finished attaching layer names.")
            
            # ******************************************************
            # ***** END: MODIFIED CODE *****
            # ******************************************************
            print("  -> Wall segments with layer info:")
            if draw_debug:
                #  this print statement to reflect the change
                print("\n--- [DEBUG] Right Wall Data (After Trim) ---")
                print(json.dumps(right_wall_data, indent=4, default=str))
                #  this print statement to reflect the change
                print("\n--- [DEBUG] Left Wall Data (After Trim) ---")
                print(json.dumps(left_wall_data, indent=4, default=str))
        
            #---RASHEEQUE MODIFICATION---ENDS---

            # 9. Generate and execute the placement plan.
            display_calcs = self.display_count_calc(doc, floor_area=0, wall_length=total_retail_wall_length, display_count=0) 
            
            # print("\n maximum floor capacity for floor ", display_calcs)
            placement_dict, remaining_wall_fixtures = self.generate_wall_fixture_plan(
                doc,
                wall_segments_data=all_wall_segments,
                display_calculations=display_calcs,
                primary_side=primary_side
            )

            print("\nRemaining wall fixtures after wall plan generation: ", remaining_wall_fixtures)
            self.place_fixtures_from_plan(placement_dict, doc)

            # 10. OPTIONAL: Draw debug geometry for validation.
            if draw_debug:
                self.draw_perimeter_paths_for_validation(doc)

            # RASHEEQUE--ADDED-NEW--FUNCTION--TO-CLEAN-TRAILING-MIRRORS---10/12/2025
            # --- NEW: Analyze and visualize remaining wall gaps with hatch fill ---
            print("\n--- Analyzing and Drawing Remaining Wall Gaps ---")
            remaining_gaps_data = self.analyze_remaining_wall_gaps(doc, all_wall_segments, draw=draw_debug)
            
            # Combine internal corners from both walls
            all_internal_corners = internal_corners_on_left_wall + internal_corners_on_right_wall
            
            # Filter to only corner gaps
            corner_gaps = self.filter_remaining_segments_near_corners(
                remaining_segments_data=remaining_gaps_data,
                internal_corners=all_internal_corners,
                threshold=1010.0  # 1010mm distance
            )
            
            # Draw hatches only for corner gaps
            self.draw_remaining_wall_gaps(doc, corner_gaps, depth=250.0, layer_name="CORNER_WALL_GAPS")
            print("--- ✅ Remaining wall gaps visualization complete ---")
            # --- END OF NEW LOGIC ---
            
            print("--- ✅ Wall Fixture Placement Complete ---")
        
            doc.remaining_wall_fixtures = remaining_wall_fixtures
            doc.display_calcs = display_calcs

    def _clean_trailing_mirrors(self, placement_dict: dict) -> dict:
        """
        Iterates through a generated placement plan and removes any
        trailing mirrors ('M') from the end of any segment's placement list.
        
        This acts as a "clean-up" step before placement to ensure no
        segment ends with a mirror.
        """
        print("\n--- 🧹 Cleaning up trailing mirrors from placement plan ---")
        cleaned_count = 0
        
        # Loop through both "right_segments" and "left_segments"
        for side_key in placement_dict.keys(): # e.g., "right_segments", "left_segments"
            segment_group = placement_dict.get(side_key, {})
            
            # Loop through each segment in the group (e.g., "0", "1", "2")
            for segment_index in segment_group.keys():
                segment_data = segment_group.get(segment_index, {})
                
                # Get the "placement" list for this segment
                placement_list = segment_data.get("placement", [])
                
                # Check if the list is not empty AND if its last item is 'M'
                if placement_list and placement_list[-1] == 'M':
                    # If it is, remove the last item
                    placement_list.pop()
                    print(f"  -> Cleaned trailing mirror from: {side_key} - Segment {segment_index}")
                    cleaned_count += 1
                    
                    # The list is modified in-place, so the dict is automatically updated

        if cleaned_count > 0:
            print(f"  -> ✅ Removed a total of {cleaned_count} trailing mirrors.")
        else:
            print("  -> No trailing mirrors found to remove.")
            
        return placement_dict # Return the modified dictionary

    
    #---RASHEEQUE--ADDED-NEW--FUNCTION--FOR--DETECTING--SEGMENT--TYPE---08/11/2025
    def _check_segment_type(self, p1: Vec2, p2: Vec2) -> str:
        """
        Checks a segment's midpoint against the CV data to determine
        if it's a solid wall, a glass facade, or a door.
        """
        mid_point = p1.lerp(p2, 0.5)
        tolerance = 150.0  # 15cm tolerance

        # 1. Check Doors (which includes glazing)
        for door in self.cvc.doors:
            try:
                s = door["start"]
                e = door["end"]
                p_start = Vec2(s[0], s[2])
                p_end = Vec2(e[0], e[2])
            except (KeyError, IndexError, TypeError):
                continue
            
            # Check if the segment's midpoint is on this door/glazing segment
            if self._is_point_on_segment_door(mid_point, p_start, p_end, tolerance):
                # Differentiate based on width, just like draw_outline does
                door_width = p_start.distance(p_end)
                if door_width > 1000:
                    return "Glass-FrontGlazing"  # This is a large glass facade
                else:
                    return "I-LK CURTAIN"        # This is a smaller door

        # 2. Check Windows (if any)
        for window in self.cvc.windows:
            try:
                s = window["start"]
                e = window["end"]
                p_start = Vec2(s[0], s[2])
                p_end = Vec2(e[0], e[2])
            except (KeyError, IndexError, TypeError):
                continue

            if self._is_point_on_segment_door(mid_point, p_start, p_end, tolerance):
                return "Window-Layer"  # You can customize this name

        # 3. If it's not a door or window, it's a solid wall
        return "Standard-Wall-Fixture-Layer"
            

    def get_retail_wall_data(self, doc, side: str, internal_corners: list, corner_box_size: float = 250.0) -> dict:
        """
        [CORRECTED] Calculates retail wall data, subtracting space from segments that
        START at or END at an internal corner.
        """

        # self._get_accurate_obstacle_bboxes(include_all=False, debug=True)
        _, stop_line_y = self.get_retail_boundary_y(doc, side=side)
        
        if side == 'left':
            perimeter_path = self._get_perimeter_path_from_facade_left_start(doc)
        elif side == 'right':
            perimeter_path = self._get_perimeter_path_from_facade_right_start(doc)
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

            #----RASHEEQUE MODIFICATION START----
            # Skip segments that are too short to begin with
            if p1.distance(p2) < 5:
                continue
            #----RASHEEQUE MODIFICATION START----
            
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
            
            #----RASHEEQUE MODIFICATION START----
            # Calculate the final, adjusted length
            final_segment_length = p1.distance(p2)
            if final_segment_length < 5: # Check length again after adjustments
                continue
            #----RASHEEQUE MODIFICATION START----
                
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


#------RASHEEQUE 22-11-2025---INTEGRATION ADDED FUNCTION END----------------------------------------------------------------------------
    def detect_small_bulge_patterns(self, segments_data: dict, side: str, max_bulge_depth: float = 900.0, max_bulge_face: float = 1500.0, small_col_threshold: float = 150.0) -> List[Dict]:
        """
        [UPDATED] Analyzes wall segments to find columns/jogs.
        1. Filters out Niches (wrong turn direction).
        2. Filters out Room Corners (main walls not parallel).
        """
        print(f"\n--- 🐫 Detecting Patterns on {side.upper()} Wall ---")
        
        try:
            # Ensure keys are sorted integers
            sorted_ids = sorted([int(k) for k in segments_data.keys()])
        except ValueError:
            return []

        detected_patterns = []
        i = 0
        
        while i < len(sorted_ids):
            if i >= len(sorted_ids) - 1: break

            id1 = sorted_ids[i]     # Potential Side 1
            id2 = sorted_ids[i+1]   # Potential Face

            seg1 = segments_data[id1]
            seg2 = segments_data[id2]
            
            # --- CHECK 1: TURN DIRECTION (Filter Niches) ---
            # We check the turn from the PREVIOUS segment to ensure we are entering a column (jutting in)
            # not a niche (jutting out) or a flat wall.
            prev_id = id1 - 1
            is_valid_entry_turn = False
            
            if prev_id in segments_data:
                seg_prev = segments_data[prev_id]
                angle_diff = (seg1['angle'] - seg_prev['angle'] + 180) % 360 - 180
                
                # Left Wall (CCW): Column Start = Right Turn (-90)
                if side == 'left' and -135 < angle_diff < -45: is_valid_entry_turn = True
                # Right Wall (CW): Column Start = Left Turn (+90)
                elif side == 'right' and 45 < angle_diff < 135: is_valid_entry_turn = True
            else:
                # If no previous segment (start of wall), we rely on geometry checks below.
                # Usually, a column won't be the very first segment unless the wall is split.
                is_valid_entry_turn = True 

            # --- CHECK 2: U-SHAPE (Column) ---
            if i < len(sorted_ids) - 2:
                id3 = sorted_ids[i+2]
                seg3 = segments_data[id3]

                # A. Check Dimensions
                is_side_1_short = seg1['length'] <= max_bulge_depth
                is_face_short   = seg2['length'] <= max_bulge_face
                is_side_2_short = seg3['length'] <= max_bulge_depth
                
                # B. Check Geometry: Side 1 and Side 2 should be roughly Parallel (opposite directions)
                # Angle diff should be ~180
                sides_parallel = 135 < abs(seg1['angle'] - seg3['angle']) < 225

                if is_side_1_short and is_face_short and is_side_2_short and sides_parallel and is_valid_entry_turn:
                    # Classify Size
                    avg_depth = (seg1['length'] + seg3['length']) / 2
                    if avg_depth < small_col_threshold:
                        u_type = 'U_SMALL'
                        label = "Small Column"
                    else:
                        u_type = 'U_LARGE'
                        label = "Large Column"

                    print(f"  -> 🛑 Found {u_type} ({label}): Segments {id1}, {id2}, {id3}")
                    detected_patterns.append({'type': u_type, 'ids': [id1, id2, id3]})
                    i += 3 
                    continue

            # --- CHECK 3: L-SHAPE (Jog) ---
            # A jog is valid ONLY if the wall BEFORE it and the wall AFTER it (the Face) are Parallel.
            # If they are Perpendicular, it's a ROOM CORNER.
            
            is_jog_depth = seg1['length'] <= 750.0
            is_jog_face  = seg2['length'] <= 900.0
            
            if is_jog_depth and is_jog_face and is_valid_entry_turn:
                if prev_id in segments_data:
                    seg_prev = segments_data[prev_id]
                    
                    # Check alignment: Prev Wall vs Face Wall
                    # They should be Parallel (0 deg diff) for a Jog.
                    # They will be Perpendicular (90 deg diff) for a Corner.
                    
                    main_walls_angle_diff = abs(seg_prev['angle'] - seg2['angle'])
                    if main_walls_angle_diff > 180: main_walls_angle_diff = 360 - main_walls_angle_diff
                    
                    if main_walls_angle_diff < 45: # Parallel-ish
                        print(f"  -> 🛑 Found L-SHAPE (Jog): Segments {id1}, {id2}")
                        detected_patterns.append({'type': 'L', 'ids': [id1, id2]})
                        i += 2 
                        continue
                    else:
                        # print(f"  -> Ignored Corner at {id1}: Walls are perpendicular ({main_walls_angle_diff:.0f}°).")
                        pass
                else:
                    # If no previous segment (Start of Path), it's almost certainly a Room Corner or Facade start.
                    # Safest to ignore it to prevent the "Left Wall Placement" bug.
                    pass

            i += 1

        return detected_patterns

        
    
    # --- UPDATED: Visualize Bulges (Handles U_SMALL and U_LARGE) ---
    def draw_detected_bulges(self, doc, wall_segments_data: dict, bulge_details: List[Dict]):
        """
        [UPDATED] Visualizes bulges with specific colors:
        - U_SMALL (Small Col) = GREEN (Layer: DEBUG_BULGE_SMALL)
        - U_LARGE (Large Col) = CYAN  (Layer: DEBUG_BULGE_LARGE)
        - L (Jog)             = YELLOW (Layer: DEBUG_BULGE_JOG)
        """
        print(f"\n--- 🎨 Visualizing {len(bulge_details)} Detected Bulge Patterns ---")
        
        if not bulge_details:
            return

        # Define Layers
        layer_u_small = "DEBUG_BULGE_SMALL"
        layer_u_large = "DEBUG_BULGE_LARGE"
        layer_l_jog   = "DEBUG_BULGE_JOG"

        # Create layers if they don't exist
        if layer_u_small not in doc.doc.layers: doc.doc.layers.add(name=layer_u_small, color=3) # Green
        if layer_u_large not in doc.doc.layers: doc.doc.layers.add(name=layer_u_large, color=4) # Cyan
        if layer_l_jog   not in doc.doc.layers: doc.doc.layers.add(name=layer_l_jog,   color=2) # Yellow

        count_us = 0
        count_ul = 0
        count_l  = 0

        for bulge in bulge_details:
            b_type = bulge['type']
            ids = bulge['ids']
            
            # Determine style based on type
            if b_type == 'U_SMALL':
                layer = layer_u_small
                label_text = "COL-S"
                count_us += 1
            elif b_type == 'U_LARGE':
                layer = layer_u_large
                label_text = "COL-L"
                count_ul += 1
            else: # L
                layer = layer_l_jog
                label_text = "JOG"
                count_l += 1
            
            # Collect points to draw a continuous polyline
            points = []
            for seg_id in ids:
                # Handle key lookup (int vs string keys)
                seg = wall_segments_data.get(seg_id) or wall_segments_data.get(str(seg_id))
                if not seg: continue
                
                coords = seg.get("segment") # (x1, y1, x2, y2)
                p1 = (coords[0], coords[1])
                p2 = (coords[2], coords[3])
                
                if not points:
                    points.append(p1)
                points.append(p2)
            
            if len(points) < 2: continue

            # Draw thick polyline
            doc.msp.add_lwpolyline(
                points,
                dxfattribs={
                    "layer": layer,
                    "lineweight": 50 # Thick line for visibility
                }
            )
            
            # Add a Text Label at the visual center of the bulge
            avg_x = sum(p[0] for p in points) / len(points)
            avg_y = sum(p[1] for p in points) / len(points)
            
            doc.msp.add_mtext(
                label_text,
                dxfattribs={
                    'char_height': 150,
                    'insert': (avg_x, avg_y),
                    'layer': layer,
                    'color': 7, # White text
                    'attachment_point': 5 # Middle Center
                }
            )
            
        print(f"  -> Drawn: {count_us} Small Cols (Green), {count_ul} Large Cols (Cyan), {count_l} Jogs (Yellow).")

    def straighten_wall_segments(self, wall_data: dict, bulge_details: List[Dict], side: str) -> dict:
        """
        [UPDATED - ROBUST] Straightens walls over columns.
        - Includes sanity checks to prevent infinite intersection coordinates.
        - Enforces Bottom-to-Top direction (Start < End).
        """
        print(f"\n--- 📏 Straightening Wall Segments on {side.upper()} side ---")
        
        segments = wall_data["segments"]
        if not segments: return wall_data
            
        sorted_ids = sorted([int(k) for k in segments.keys()])
        
        replacements = {}
        ids_to_remove = set()
        count_straightened = 0

        # Define a maximum allowed shift to prevent shooting off to infinity
        MAX_SHIFT_TOLERANCE = 3000.0  # 3 meters

        for bulge in bulge_details:
            if bulge['type'] == 'U_SMALL':
                col_ids = sorted(bulge['ids'])
                s1, f, s2 = col_ids[0], col_ids[1], col_ids[2]
                
                p = s1 - 1
                n = s2 + 1
                
                if p in segments and n in segments:
                    group_ids = {p, s1, f, s2, n}
                    if not group_ids.isdisjoint(ids_to_remove): continue 

                    print(f"  -> 🔍 STRAIGHTENING GROUP: Prev[{p}] -> Col[{s1}-{f}-{s2}] -> Next[{n}]")

                    # --- 1. Define Geometry ---
                    face_seg = segments[f]["segment"]
                    p_face_start = Vec2(face_seg[0], face_seg[1])
                    p_face_end = Vec2(face_seg[2], face_seg[3])
                    
                    prev_seg = segments[p]["segment"]
                    p_prev_start = Vec2(prev_seg[0], prev_seg[1]) 
                    p_prev_end = Vec2(prev_seg[2], prev_seg[3])   
                    
                    next_seg = segments[n]["segment"]
                    p_next_start = Vec2(next_seg[0], next_seg[1])
                    p_next_end = Vec2(next_seg[2], next_seg[3])   
                    
                    # --- 2. Calculate Intersection with SANITY CHECK ---
                    def get_safe_intersection(line_p1, line_p2, other_p1, other_p2, ref_point):
                        x1, y1, x2, y2 = line_p1.x, line_p1.y, line_p2.x, line_p2.y
                        x3, y3, x4, y4 = other_p1.x, other_p1.y, other_p2.x, other_p2.y
                        
                        denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
                        
                        # Check 1: Is denom too close to zero? (Parallel)
                        if abs(denom) < 1e-9: 
                            return None 
                        
                        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
                        intersect_pt = Vec2(x1 + ua * (x2 - x1), y1 + ua * (y2 - y1))
                        
                        # Check 2: Is the point wildly far away? (Geometric Explosion)
                        if intersect_pt.distance(ref_point) > MAX_SHIFT_TOLERANCE:
                            print(f"    -> ⚠️ Intersection rejected (Too far: {intersect_pt.distance(ref_point):.0f}mm). Using projection.")
                            return None
                            
                        return intersect_pt

                    # Try to intersect Face Line with the lines of the outer neighbors
                    # We use the original outer points (p_prev_start, p_next_end) as reference for the distance check
                    new_start = get_safe_intersection(p_face_start, p_face_end, p_prev_start, p_prev_end, p_prev_start)
                    new_end = get_safe_intersection(p_face_start, p_face_end, p_next_start, p_next_end, p_next_end)
                    
                    # --- 3. FALLBACK: Projection (If Parallel or Unsafe) ---
                    if new_start is None:
                        new_start = self._project_point_onto_infinite_line(p_prev_start, p_face_start, p_face_end)
                    
                    if new_end is None:
                        new_end = self._project_point_onto_infinite_line(p_next_end, p_face_start, p_face_end)

                    # --- 4. DIRECTION ENFORCEMENT ---
                    if side == 'left':
                        # Left Wall: Top-to-Bottom (Start Y > End Y)
                        if new_start.y < new_end.y:
                             new_start, new_end = new_end, new_start
                    elif side == 'right':
                        # Right Wall: Bottom-to-Top (Start Y < End Y)
                        if new_start.y > new_end.y:
                            new_start, new_end = new_end, new_start

                    new_length = new_start.distance(new_end)

                    # --- 5. Create New Segment ---
                    new_segment_data = {
                        "segment": (new_start.x, new_start.y, new_end.x, new_end.y),
                        "start": new_start,
                        "end": new_end,
                        "length": new_length,
                        "angle": segments[f]["angle"],
                        "layer_name": segments[f].get("layer_name", "Standard-Wall-Fixture-Layer"),
                        "placement": [],
                        "is_straightened": True,
                        "side": side
                    }

                    replacements[p] = new_segment_data
                    ids_to_remove.update(group_ids)
                    count_straightened += 1

        if count_straightened == 0:
            return wall_data

        # --- 6. Rebuild Dictionary ---
        new_segments_dict = {}
        new_index = 0
        i = 0
        
        while i < len(sorted_ids):
            original_id = sorted_ids[i]
            if original_id in replacements:
                new_segments_dict[new_index] = replacements[original_id]
                new_index += 1
                while i < len(sorted_ids) and sorted_ids[i] in ids_to_remove: i += 1
            elif original_id not in ids_to_remove:
                new_segments_dict[new_index] = segments[original_id]
                new_index += 1
                i += 1
            else:
                i += 1

        wall_data["segments"] = new_segments_dict
        wall_data["total_length"] = sum(s["length"] for s in new_segments_dict.values())
        
        print(f"  -> ✅ Replaced {count_straightened} column groups.")
        return wall_data

    def _project_point_onto_infinite_line(self, point: Vec2, line_p1: Vec2, line_p2: Vec2) -> Vec2:
        """Helper to project a point onto the infinite line passing through p1 and p2."""
        line_vec = line_p2 - line_p1
        if line_vec.magnitude == 0: return line_p1
        
        line_dir = line_vec.normalize()
        v = point - line_p1
        d = v.dot(line_dir)
        
        return line_p1 + line_dir * d

    def draw_straightened_wall_segments(self, doc, wall_data: dict):
        """
        [DEBUG] Visualizes ONLY the segments that were straightened.
        Draws them in Magenta on layer 'DEBUG_STRAIGHTENED_WALL'.
        """
        print("\n--- 🎨 Visualizing Straightened Wall Segments ---")
        
        layer_name = "DEBUG_STRAIGHTENED_WALL"
        # Create layer if missing (Color 6 = Magenta)
        if layer_name not in doc.doc.layers:
            doc.doc.layers.add(name=layer_name, color=6) 

        count = 0
        # Iterate through the segments to find the tag
        for seg_id, seg_data in wall_data.get("segments", {}).items():
            if seg_data.get("is_straightened"):
                # --- THIS IS THE FIX ---
                # The data is stored as 'start' and 'end' Vec2 objects, not in a "segment" tuple.
                p1_vec = seg_data.get("start")
                p2_vec = seg_data.get("end")

                if not p1_vec or not p2_vec:
                    continue # Skip if geometry is missing

                p1 = (p1_vec.x, p1_vec.y)
                p2 = (p2_vec.x, p2_vec.y)
                # --- END OF FIX ---
                
                # Draw thick line
                doc.msp.add_lwpolyline(
                    [p1, p2],
                    dxfattribs={
                        "layer": layer_name,
                        "lineweight": 70, # Very thick (0.70mm)
                        "color": 6
                    }
                )
                
                # Add Label
                mid_x = (p1[0] + p2[0]) / 2
                mid_y = (p1[1] + p2[1]) / 2
                doc.msp.add_mtext(
                    "STRAIGHTENED",
                    dxfattribs={
                        'char_height': 150,
                        'insert': (mid_x, mid_y),
                        'layer': layer_name,
                        'color': 6,
                        'attachment_point': 5 # Middle Center
                    }
                )
                count += 1
        
        print(f"  -> Drawn {count} straightened segments on layer '{layer_name}'.")


#------RASHEEQUE 22-11-2025---INTEGRATION ADDED FUNCTION END----------------------------------------------------------------------------

#-------RASHEEQUE ADDED A FUNCTION------------------------------------------------------------------------------
    def _trim_facade_segment(self, wall_data: dict, trim_amount_mm: float = 200.0) -> dict:
        """
        Trims the start of segment '0' to create an inset from the facade.

        Finds segment 0 (or "0") in wall_data["segments"], moves its start point
        inward by trim_amount_mm along the segment direction and updates lengths.
        If the segment is shorter than the trim amount it is removed and total_length
        adjusted. Returns the modified wall_data dict (in-place update).
        """
        try:
            from ezdxf.math import Vec2
        except Exception:
            # fallback: Vec2 should already be available in the module imports,
            # but if not, raise a clear error for debugging
            raise

        if not wall_data or "segments" not in wall_data:
            return wall_data

        # Accept either integer key 0 or string key "0"
        segs = wall_data.get("segments", {})
        segment_key = 0 if 0 in segs else ("0" if "0" in segs else None)
        if segment_key is None:
            # nothing to trim
            return wall_data

        segment_zero = segs.get(segment_key)
        if not segment_zero:
            return wall_data

        try:
            original_length = float(segment_zero.get("length", 0.0))
            # Ensure total_length exists
            if "total_length" not in wall_data:
                wall_data["total_length"] = float(original_length)

            # If too short, remove it
            if original_length <= trim_amount_mm:
                print(f"  -> WARNING: Facade segment '0' is too short ({original_length:.0f}mm) to trim. Removing it from plan.")
                wall_data["total_length"] = max(0.0, wall_data.get("total_length", 0.0) - original_length)
                # delete using the same key type
                del wall_data["segments"][segment_key]
                return wall_data

            # Read segment coords; expected stored as tuple (x1,y1,x2,y2)
            seg_coords = segment_zero.get("segment")
            if not seg_coords or len(seg_coords) < 4:
                return wall_data

            p1_x, p1_y, p2_x, p2_y = seg_coords
            p1 = Vec2(p1_x, p1_y)
            p2 = Vec2(p2_x, p2_y)

            seg_vec = (p2 - p1)
            seg_len = seg_vec.magnitude
            if seg_len <= 1e-6:
                return wall_data

            segment_vector = seg_vec.normalize()

            # new start point moved along segment_vector by trim_amount_mm
            new_p1 = p1 + segment_vector * trim_amount_mm
            new_length = new_p1.distance(p2)

            # update segment data
            segment_zero["segment"] = (new_p1.x, new_p1.y, p2.x, p2.y)
            segment_zero["length"] = float(new_length)

            # update total_length (defensive: ensure not negative)
            wall_data["total_length"] = max(0.0, wall_data.get("total_length", 0.0) - trim_amount_mm)

            print(f"  -> ✅ Trimmed facade segment '0' by {trim_amount_mm:.0f}mm. New length: {new_length:.0f}mm.")
            return wall_data

        except Exception as e:
            print(f"  -> ⚠️ ERROR during _trim_facade_segment: {e}")
            return wall_data


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
        


    def draw_corner_dummy_boxes(self, doc, corners: list, size: float = 250.0, layer_name: str = "CORNER_DUMMY_BOX", draw_visual: bool = True):
        """
        [MODIFIED] Calculates a box aligned with the wall angles for an internal corner 
        and registers it as an obstacle.
        """
        if not corners:
            return

        if draw_visual:
            print(f"--- 🎨 Drawing and Registering {len(corners)} Dummy Boxes ---")
            if layer_name not in doc.doc.layers:
                doc.doc.layers.add(name=layer_name, color=3) # Magenta
        else:
            print(f"--- 🛡️ Registering {len(corners)} Dummy Boxes (Hidden) ---")

        for corner_data in corners:
            # Use vector math to align the box with the walls
            p_corner = Vec2(corner_data['point'])
            
            # Vector pointing BACK along the incoming wall
            v_in = Vec2.from_angle(math.radians(corner_data['angle_in'] + 180))
            
            # Vector pointing FORWARD along the outgoing wall
            v_out = Vec2.from_angle(math.radians(corner_data['angle_out']))
            
            # Define the points of the box (Parallelogram aligned with walls)
            # p_corner is the vertex
            p1 = p_corner + v_in.normalize() * size
            p2 = p_corner + v_out.normalize() * size
            p3 = p_corner + v_in.normalize() * size + v_out.normalize() * size
            
            points = [p_corner, p1, p3, p2]
            
            # Register as obstacle (bbox tuple of the shape)
            min_x = min(p.x for p in points)
            min_y = min(p.y for p in points)
            max_x = max(p.x for p in points)
            max_y = max(p.y for p in points)
            
            bbox_tuple = (min_x, min_y, max_x, max_y)
            doc.placed_bboxes.append(bbox_tuple)
            
            if draw_visual:
                # Convert Vec2 to tuples for ezdxf
                points_tuples = [(p.x, p.y) for p in points]
                
                doc.msp.add_lwpolyline(
                    points_tuples, 
                    close=True, 
                    dxfattribs={"layer": layer_name, "lineweight": 30}
                )

    # touched
    #-------RASHEEQUE ADDED A FUNCTION REFINING PART 03-11-2025------------------------------------------------------------------------------
    def _get_perimeter_path_from_facade_left_start(self, doc):
        """
        [NEW ROBUST METHOD]
        Identifies the "facade" wall (the segment that gets the bottom_epsilon)
        and starts a counter-clockwise perimeter path from its leftmost point.
        """
         # --- CACHING: Check if the path has already been calculated ---
        if doc.perimeter_path_left_start is not None:
            return doc.perimeter_path_left_start

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
            # if Vec2(p1_coords).distance(Vec2(p2_coords)) > 100:
            if Vec2(p1_coords).distance(Vec2(p2_coords)) > 10:

                perimeter_path.append((p1_coords, p2_coords))
        
        # return perimeter_path
        # --- CACHING: Store the result before returning ---
        doc.perimeter_path_left_start = perimeter_path
        return perimeter_path

    def _get_perimeter_path_from_facade_right_start(self, doc):
        """
        [CORRECTED ROBUST METHOD - RIGHT SIDE]
        Identifies the "facade" wall and starts a CLOCKWISE perimeter path
        from its rightmost point, ensuring the path moves UP the right wall first.
        """
        # --- CACHING: Check if the path has already been calculated ---
        if doc.perimeter_path_right_start is not None:
            return doc.perimeter_path_right_start

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
            # if Vec2(p1_coords).distance(Vec2(p2_coords)) > 100:
            if Vec2(p1_coords).distance(Vec2(p2_coords)) > 10:
                perimeter_path.append((p1_coords, p2_coords))
        
        # return perimeter_path
        # --- CACHING: Store the result before returning ---
        doc.perimeter_path_right_start = perimeter_path
        return perimeter_path
    
    def get_retail_boundary_y(self, doc, side="0") -> float:
        """
        Finds the lowest Y-coordinate of the clinic/BOH cluster to determine
        the stop line for the retail wall space calculation.
        """

        # --- NEW: PRIORITY 1 - Check for the RETAIL_SEPARATOR line first ---
        separator_line = doc.msp.query('LINE[layer=="BOH_WALL_VALID_OUTLINE"]').first
        if separator_line:
            boundary_y = separator_line.dxf.start.y
            print(f"  -> Retail boundary defined by 'RETAIL_SEPARATOR' line at Y-coordinate: {boundary_y:.0f}")
            # For this function's logic, we don't need the side-specific value when the line is present.
            if side != "0":
                return boundary_y, boundary_y   
            return boundary_y
        
        if not doc.placed_bboxes:
            print("  -> No BOH/Clinic boundary found; entire wall length is available.")
            # If no obstacles, return the top of the floorplan so the whole wall is measured.
            return self.cvc.max_y
        
        print(f"\t\t\t\t{doc.placed_bboxes}")
        if side != "0":
            temp = doc.placed_bboxes.pop()
            margin = 10.0 
            # print(f"******************************************************************************************************************")
            # print(f"******************************************************************************************************************")
            # The boundary is the lowest point of this cluster, minus a small margin.
            if side == "right":
                print("RIGHT SIDE")
                x_val = max([b[2] for b in doc.placed_bboxes])
                arr = [b[1] for b in doc.placed_bboxes if abs(b[2] - x_val) < 200]
                side_min = min(arr) - margin
            else:
                print("LEFT SIDE")
                x_val = min([b[0] for b in doc.placed_bboxes])
                arr = [b[1] for b in doc.placed_bboxes if abs(b[0] - x_val) < 200]
                side_min = min(arr) - margin

            
            print(f"x_val: {x_val}\narr: {arr}\nside_min: {side_min}")
            # print(f"******************************************************************************************************************")
            # print(f"******************************************************************************************************************")
            doc.placed_bboxes.append(temp)

        lowest_y = min(b[1] for b in doc.placed_bboxes)
        margin = 100.0 
        boundary_y = lowest_y - margin
        
        print(f"  -> Retail boundary line calculated at Y-coordinate: {boundary_y:.0f}")
        if side != 0:
            return boundary_y, side_min
        return boundary_y
    
    def display_count_calc(self, doc, floor_area: float, wall_length: float, display_count: int) -> dict:
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
        zone_polygon = self.calculate_greeter_to_standing_table_zone(doc)
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


            #---RASHEEQUE MODIFICATION START---08-11-2025
            # --- Calculate Space Requirements for the Current Configuration ---
            # wall_space_needed = (num_large_wall * display_large_length) + \
            #                     (num_medium_wall * display_medium_length) + \
            #                     (mirror_count * mirror_length)
            
            # wall_fixture_area = wall_space_needed * (display_width + single_shopping)
            # floor_fixture_area = (euro_length + 2000) * euro_width * floor_count
            # remaining_floor_area = floor_area - wall_fixture_area - floor_fixture_area

            # # --- Validation and Adjustment Logic ---
            # if wall_space_needed <= wall_length and remaining_floor_area > 0:
            #     print("Valid floor/wall/mirror counts found.")
            #     valid = True
                
            # elif wall_space_needed > wall_length:
            #     if remaining_floor_area <= 0: # Both wall and floor fail
            #         prev_action = 0
            #         print("ACTION: Insufficient space on BOTH floor and wall. Downsizing wall fixtures.")
            #         if num_large_wall > 0:
            #             num_large_wall -= 1
            #             num_medium_wall += 1
            #         elif mirror_count > wall_count / 2:
            #             mirror_count -= 1
            #         else:
            #             break # No more options
            #     else: # Only wall fails
            #         if prev_action == 2: # Flip-flop detected
            #             print("DEAD END: Detected flip-flop (floor -> wall). Forcing downsize.")
            #             if num_large_wall > 0:
            #                 num_large_wall -= 1
            #                 num_medium_wall += 1
            #             elif mirror_count > wall_count / 2:
            #                 mirror_count -= 1
            #             prev_action = -1 # Reset state
            #         else:
            #             prev_action = 1
            #             print("ACTION: Not enough wall space. Trading wall fixture for floor fixture.")
            #             wall_count -= 1
            #             floor_count += 1
            #             mirror_count -= 1
                
            # elif remaining_floor_area <= 0: # Only floor fails
            #     if prev_action == 1: # Flip-flop detected
            #         print("DEAD END: Detected flip-flop (wall -> floor). Forcing downsize.")
            #         if num_large_wall > 0:
            #             num_large_wall -= 1
            #             num_medium_wall += 1
            #         elif mirror_count > wall_count / 2:
            #             mirror_count -= 1
            #         prev_action = -1 # Reset state
            #     else:
            #         prev_action = 2
            #         print("ACTION: Not enough floor space. Trading floor fixture for wall fixture.")
            #         floor_count -= 1
            #         wall_count += 1
            #         mirror_count += 1

            # --- Calculate Space Requirements for the Current Configuration ---
            
            # --- Check 1: Wall Fixture Length ---
            wall_space_needed = (num_large_wall * display_large_length) + \
                                (num_medium_wall * display_medium_length) + \
                                (mirror_count * mirror_length)
            
            # --- Check 2: Floor Fixture Area ---
            # This calculation is now INDEPENDENT of the wall fixtures.
            floor_fixture_area = (euro_length + 2000) * euro_width * floor_count
            remaining_floor_area = floor_area - floor_fixture_area # Only subtracts floor fixtures

            # --- Corrected Validation and Adjustment Logic ---
            wall_check_passed = (wall_space_needed <= wall_length)
            floor_check_passed = (remaining_floor_area > 0)

            if wall_check_passed and floor_check_passed:
                print("Valid floor/wall/mirror counts found.")
                valid = True
                
            elif not wall_check_passed: # Wall check failed
                if not floor_check_passed: # Both wall and floor fail
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
                
            elif not floor_check_passed: # Only floor fails
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
            # ----  RASHEEQUE MODIFICATION END  ----

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
        
    # def _build_fixture_pattern(self, num_lf: int, num_mf: int, num_mirrors: int, needs_starting_mirror: bool, segment_id: str, primary_side: str, segment_length: float,**kwargs) -> List[str]:
    def _build_fixture_pattern(self, num_lf, num_mf, num_mirrors, needs_starting_mirror, segment_id, primary_side, segment_length, last_segment_ended_with, **kwargs):
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
        print(f"DEBUG: last_segment_ended_with={last_segment_ended_with}, needs_starting_mirror={needs_starting_mirror}, segment_id={segment_id}")

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

    def generate_wall_fixture_plan(self, doc, wall_segments_data: dict, display_calculations: dict, primary_side: str) -> dict:
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
        
    # #----------------------------- RASHEEQUE MODIFICATION START---------------------06-11-2025-----
    # ##############################################################################
    #     #---Original--one
    #     # --- 3. CALCULATE PROPORTIONAL CAPACITY (Largest Remainder Method) ---
    #     ordered_lengths = []
    #     for key in processing_order:
    #         side_name, seg_index_str = key.rsplit('_', 1)
    #         segment_data = wall_segments_data[side_name][int(seg_index_str)]
    #         ordered_lengths.append(segment_data['length'])

    #     total_wall_length = sum(ordered_lengths)
    #     capacities = {}

    #     if total_wall_length > 0 and total_fixture_count > 0:
    #         len_pct_arr = [length / total_wall_length for length in ordered_lengths]
    #         fixture_division_float = [p * total_fixture_count for p in len_pct_arr]
    #         final_fixture_counts = self._distribute_integers_largest_remainder(fixture_division_float, int(total_fixture_count))
    #         for i, key in enumerate(processing_order):
    #             side_name, seg_index_str = key.rsplit('_', 1)
    #             segment_data = wall_segments_data[side_name][int(seg_index_str)]
    #             capacities[key] = {'capacity': final_fixture_counts[i], 'data': segment_data}
    #     else:
    #         for key in processing_order:
    #             side_name, seg_index_str = key.rsplit('_', 1)
    #             segment_data = wall_segments_data[side_name][int(seg_index_str)]
    #             capacities[key] = {'capacity': 0, 'data': segment_data}
    # ##############################################################################
    #-------------------------------------------------------------------
        # New robust capacity allocation (exclude too-short segments, map back to original order)
        MIN_LENGTH_FOR_CAPACITY = 1030.0
        # Build maps
        segment_data_map = {}
        valid_keys = []
        lengths_for_valid = []

        for key in processing_order:
            side_name, seg_index_str = key.rsplit('_', 1)
            seg = wall_segments_data[side_name][int(seg_index_str)]
            segment_data_map[key] = seg
            if seg['length'] >= MIN_LENGTH_FOR_CAPACITY:
                valid_keys.append(key)
                lengths_for_valid.append(seg['length'])

        total_wall_length = sum(lengths_for_valid)
        capacities = {}

        if total_wall_length > 0 and total_fixture_count > 0:
            # compute proportional floats for valid segments only
            len_pct_arr = [l / total_wall_length for l in lengths_for_valid]
            fixture_division_float = [p * total_fixture_count for p in len_pct_arr]
            final_fixture_counts = self._distribute_integers_largest_remainder(fixture_division_float, int(total_fixture_count))

            # map results back: valid ones get numbers, excluded ones get 0
            for i, key in enumerate(processing_order):
                seg = segment_data_map[key]
                if key in valid_keys:
                    capacities[key] = {'capacity': int(final_fixture_counts[valid_keys.index(key)]), 'data': seg}
                else:
                    capacities[key] = {'capacity': 0, 'data': seg}

        else:
            # Fallback: if we have fixtures but no valid segments, assign all to the longest segment
            if total_fixture_count > 0 and processing_order:
                # find the longest original segment
                longest_key = max(processing_order, key=lambda k: segment_data_map[k]['length'])
                for key in processing_order:
                    seg = segment_data_map[key]
                    capacities[key] = {'capacity': (total_fixture_count if key == longest_key else 0), 'data': seg}
            else:
                for key in processing_order:
                    capacities[key] = {'capacity': 0, 'data': segment_data_map[key]}


    #----------------------------- RASHEEQUE MODIFICATION END---------------------06-11-2025-----

    

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
                #----RASHEEQUE MODIFICATION START--08-11-2025--
                # --- THIS IS THE FIX ---
                # A skipped segment acts as a natural break, so we reset
                # the flag to 'M' to ensure the next segment starts with a fixture.
                last_segment_ended_with = 'M'
                print("    -> Resetting last_segment_ended_with = 'M'")
                # --- END OF FIX ---
                continue

            # ...existing code...
            # --- Outer Loop for Fixture Reduction (Phase 3) ---
            n = initial_capacity
            segment_plan_found = False
            mirror_count = n - 1  # Initialize mirror_count here, outside the loop
            
            # while n > 0:
            #     # Determine if a starting mirror is needed based on the previous segment
            #     needs_starting_mirror = last_segment_ended_with in ['LF', 'MF']
            #     starting_mirror_len = M_LEN if needs_starting_mirror else 0
                

            #     # --- Phase 1: Try swapping Large to Medium fixtures with current mirror count ---
            #     print(f"\n       -> 💡 PHASE 1: Trying fixture swaps with {mirror_count} mirrors")
            #     print(f"          Segment length: {segment_length:.0f}mm")
                
            #     phase1_success = False
            #     for swaps in range(n + 1):
            #         num_lf, num_mf = n - swaps, swaps
                    
            #         # Calculate if starting mirror is needed
            #         needs_starting_mirror = (last_segment_ended_with in ['LF', 'MF'])
            #         starting_mirror_len = M_LEN if needs_starting_mirror else 0
                    
            #         total_length = (num_lf * LF_LEN) + (num_mf * MF_LEN) + (mirror_count * M_LEN) + starting_mirror_len
                    
            #         print(f"          -> Testing swap: {num_lf} LF + {num_mf} MF + {mirror_count} M + {starting_mirror_len} start")
            #         print(f"             Total: {total_length:.0f}mm vs limit {segment_length:.0f}mm", end="")
                    
            #         #----RASHEEQUE----MODIFICATION START--24-11-2025--
            #         # Check 1: Does it fit WITH the starting mirror?
            #         if total_length <= segment_length:
            #             print(" ✅ FITS!")
            #             # Build the pattern
            #             base_pattern = ['MF'] * num_mf + ['LF'] * num_lf
            #             # final_pattern = []        
            #             final_pattern = self._build_fixture_pattern(
            #                     num_lf, num_mf, mirror_count, needs_starting_mirror,
            #                     segment_id=segment_id, primary_side=primary_side, segment_length=segment_length
            #                 )
            #             final_plan[segment_id] = final_pattern
            #             print(f"\n          -> ✅ PHASE 1 SUCCESS!")
            #             print(f"             Pattern: {final_pattern}")
            #             if needs_starting_mirror: 
            #                 final_pattern.append('M')
            #                 print(f"             -> Added starting mirror")
                        
                  
            #             for k in range(n):
            #                     final_pattern.append(base_pattern[k])
            #                     if k < n - 1:
            #                         final_pattern.append('M')
                            
                        
                        
            #             final_pattern = self._build_fixture_pattern(
            #                 num_lf, num_mf, mirror_count, needs_starting_mirror, 
            #                 segment_id=segment_id, primary_side=primary_side,segment_length=segment_length
            #             )
                            
            #             final_plan[segment_id] = final_pattern
            #             print(f"\n          -> ✅ PHASE 1 SUCCESS!")
            #             print(f"             Pattern: {final_pattern}")
            #             print(f"             Breakdown: {num_lf} LF, {num_mf} MF, {mirror_count} mirrors")
            #             phase1_success = True
            #             segment_plan_found = True
            #             break
            #         # Check 2: FALLBACK - Does it fit WITHOUT the starting mirror?
            #         # Only try this if we failed above AND a starting mirror was requested
            #         elif needs_starting_mirror:
            #             length_no_start_mirror = total_length - starting_mirror_len
            #             if length_no_start_mirror <= segment_length:
            #                 print(f"\n             ⚠️ STRICTLY FAILED, but FITS without start mirror ({length_no_start_mirror:.0f}mm). Dropping start mirror.")
                            
            #                 # Force disable start mirror for this placement
            #                 needs_starting_mirror = False 
                            
            #                 final_pattern = self._build_fixture_pattern(
            #                     num_lf, num_mf, mirror_count, needs_starting_mirror, # Pass False here
            #                     segment_id=segment_id, primary_side=primary_side, segment_length=segment_length
            #                 )
            #                 final_plan[segment_id] = final_pattern
            #                 # *** CRITICAL UPDATE HERE ***
            #                 # Since we dropped the start mirror, this segment now starts with a Fixture.
            #                 # It will likely end with a Fixture (since we usually strip trailing mirrors).
            #                 # Therefore, we must tell the NEXT loop that this one ended with a Fixture.
            #                 if final_pattern and final_pattern[-1] == 'M':
            #                     # If the pattern generator added a trailing mirror, the next one starts with Fixture
            #                     last_segment_ended_with = 'M' 
            #                 else:
            #                     # If it ended with a fixture (LF/MF), the next one MUST start with Mirror
            #                     last_segment_ended_with = 'LF'
            #                 print(f"\n          -> ✅ PHASE 1 SUCCESS (Fallback)!")
            #                 phase1_success = True
            #                 segment_plan_found = True
            #                 needs_starting_mirror = True  # Reset flag
            #                 break
            #             else:
            #                 print(" ❌ Too long (even without start mirror)")
            #         else:
            #             print(" ❌ Too long")
            #         # --- NEW LOGIC ENDS HERE ---
                    
                
            #     if phase1_success:
            #         break

            #     # --- Phase 2: Mirror Reduction & Swap-Down ---
            #     print("    -> Phase 1 failed. Entering Phase 2 (Mirror Reduction)...")
            #     phase2_success = False
                
            #     # **CORRECTED MINIMUM MIRROR CALCULATION**
            #     min_mirrors_base = math.ceil(n / 2)
            #     min_mirrors = min_mirrors_base  if min_mirrors_base % 2 != 0 else min_mirrors_base
                
            #     print(f"       -> Minimum mirrors for {n} fixtures: {min_mirrors}")
                
            #     # Start reducing mirrors from current mirror_count
            #     starting_mirror_count_for_phase2 = min(mirror_count, n-1)
                
            #     print(f"\n       -> 🔍 DETAILED PHASE 2 TRACE for {n} fixtures:")
            #     print(f"       -> Starting with {starting_mirror_count_for_phase2} mirrors")
            #     print(f"       -> Will reduce down to minimum of {min_mirrors} mirrors")
            #     print(f"       -> Segment length available: {segment_length:.0f}mm")
                
            #     # --- FIX: Initialize current_mirrors before the loop ---
            #     current_mirrors = starting_mirror_count_for_phase2

            #     # **CRITICAL FIX: Build the removal pattern correctly**
            #     for current_mirrors in range(starting_mirror_count_for_phase2, min_mirrors - 1, -1):
            #         if current_mirrors < 0:
            #             continue
                    
            #         # Calculate which position to remove based on the reduction step
            #         steps_reduced = starting_mirror_count_for_phase2 - current_mirrors
            #         remove_position = steps_reduced + 2  # Start from 2nd last, then 3rd last, etc.
                    
            #         print(f"\n       -> 💡 TRYING: {current_mirrors} mirrors (step {steps_reduced + 1})")
            #         print(f"          Removing {remove_position}th mirror from end")
                    
            #         # Try swapping fixtures from all LF to all MF with this mirror count
            #         for swaps in range(n + 1):
            #             num_lf, num_mf = n - swaps, swaps
            #             total_length = (num_lf * LF_LEN) + (num_mf * MF_LEN) + (current_mirrors * M_LEN) + starting_mirror_len
                        
            #             print(f"          -> Testing swap combination: {num_lf} LF + {num_mf} MF + {current_mirrors} M")
            #             print(f"             Total length: {total_length:.0f}mm (limit: {segment_length:.0f}mm)", end="")
                        
            #             if total_length <= segment_length:
            #                 print(" ✅ FITS!")
            #                 base_pattern = ['MF'] * num_mf + ['LF'] * num_lf
            #                 final_pattern = []
            #                 if needs_starting_mirror: 
            #                     final_pattern.append('M')
                            
            #                 # **CORRECTED: Build pattern by removing specific mirror positions from the END**
            #                 # Calculate which positions to skip (count from the end)
            #                 positions_to_skip = set()
            #                 for step in range(steps_reduced):
            #                     position_from_end = step + 2  # 2nd last, 3rd last, etc.
            #                     actual_index = n - position_from_end  # Convert to index from start
            #                     if 0 <= actual_index < n - 1:
            #                         positions_to_skip.add(actual_index)
            #                         print(f"             -> Will SKIP mirror after fixture at index {actual_index} ({position_from_end}th from end)")
                            
            #                 print(f"\n          -> 🔨 BUILDING PATTERN:")
            #                 print(f"             Base fixtures: {base_pattern}")
            #                 print(f"             Positions to skip mirrors: {sorted(positions_to_skip)}")
                            
            #                 # Build the pattern with selective mirror placement
            #                 for k in range(n):
            #                     final_pattern.append(base_pattern[k])
            #                     print(f"             [{k}] Added fixture: {base_pattern[k]}", end="")
                                
            #                     if k < n - 1:
            #                         if k not in positions_to_skip:
            #                             final_pattern.append('M')
            #                             print(" + Mirror ✓")
            #                         else:
            #                             print(" (Mirror SKIPPED)")
            #                     else:
            #                         print("")

            #                 final_pattern = self._build_fixture_pattern(num_lf, num_mf, current_mirrors, needs_starting_mirror, segment_id=segment_id, primary_side=primary_side,segment_length=segment_length)

            #                 print(f"\n          -> ✅ FINAL PATTERN CREATED:")
            #                 print(f"             {final_pattern}")
            #                 print(f"             Breakdown: {num_lf} LF, {num_mf} MF, {current_mirrors} mirrors")
            #                 print(f"             Pattern length: {len([x for x in final_pattern if x != 'M'])} fixtures, {len([x for x in final_pattern if x == 'M'])} mirrors")
                            
            #                 final_plan[segment_id] = final_pattern
            #                 print(f"\n    -> ✅ SUCCESS (Phase 2): Segment solved!")
            #                 phase2_success = True
            #                 mirror_count = current_mirrors
            #                 break
            #             else:
            #                 print(" ❌ Too long")
                    
            #         if phase2_success:
            #             break
                
            #     # Update mirror_count even if Phase 2 failed
            #     if not phase2_success:
            #         mirror_count = min_mirrors - 1
            #         print(f"\n       -> ⚠️ Phase 2 exhausted all options.")
            #         print(f"          Setting mirror_count to {mirror_count} for next iteration.")
                
            #     if phase2_success:
            #         segment_plan_found = True
            #         break

            #     # --- Phase 3: Fixture Reduction ---
            #     print(f"\n    -> ⚠️ Phase 2 failed for n={n}. Entering Phase 3 (Fixture Reduction)...")
            #     print(f"       -> Reducing fixture count from {n} to {n-1}")
            #     print(f"       -> Overflow count increases by 1 (now {overflow_display_fixture + 1})")
            #     print(f"       -> This fixture will be marked as overflow for later handling")
                
            #     n -= 1
            #     overflow_display_fixture += 1

            #----RASHEEQUE----MODIFICATION START--24-11-2025--
            while n > 0:
                # Determine if a starting mirror is needed based on the previous segment
                needs_starting_mirror = (last_segment_ended_with in ['LF', 'MF'])
                starting_mirror_len = M_LEN if needs_starting_mirror else 0
                
                print(f"\n       -> 💡 PHASE 1: Trying fixture swaps with {mirror_count} mirrors")
                print(f"          Segment length: {segment_length:.0f}mm")
                
                phase1_success = False
                best_solution = None # Format: (num_lf, num_mf, keep_start_mirror)

                # --- PASS 1: STRICT (Try to KEEP the Start Mirror) ---
                if needs_starting_mirror:
                    # We don't print a header for Pass 1 to keep logs clean, 
                    # but we iterate exactly as before to show every test case.
                    for swaps in range(n + 1):
                        num_lf, num_mf = n - swaps, swaps
                        
                        # Calculate length WITH Start Mirror
                        total_length = (num_lf * LF_LEN) + (num_mf * MF_LEN) + (mirror_count * M_LEN) + starting_mirror_len
                        
                        print(f"          -> Testing swap: {num_lf} LF + {num_mf} MF + {mirror_count} M + {starting_mirror_len} start")
                        print(f"             Total: {total_length:.0f}mm vs limit {segment_length:.0f}mm", end="")
                        
                        if total_length <= segment_length:
                            print(" ✅ FITS! (Strict Match)")
                            best_solution = (num_lf, num_mf, True)
                            break # Stop at the first match
                        else:
                            print(" ❌ Too long")

                # --- PASS 2: FALLBACK (Drop Start Mirror) ---
                # Only run this if Pass 1 failed OR if we didn't need a mirror anyway
                if best_solution is None:
                    # If we already tried Pass 1, let the user know we are retrying without the mirror
                    if needs_starting_mirror:
                        print(f"          -> ⚠️ Strict check failed. Retrying without start mirror...")
                    
                    for swaps in range(n + 1):
                        num_lf, num_mf = n - swaps, swaps
                        
                        # Calculate length WITHOUT Start Mirror
                        # Note: if needs_starting_mirror was False, starting_mirror_len is 0 anyway
                        total_length_no_start = (num_lf * LF_LEN) + (num_mf * MF_LEN) + (mirror_count * M_LEN)
                        
                        # Only print these tests if we are actually in a fallback scenario (to avoid duplicate logs)
                        # If needs_starting_mirror was False, this is just the standard check.
                        if needs_starting_mirror:
                            print(f"          -> Testing swap (No Start Mirror): {num_lf} LF + {num_mf} MF + {mirror_count} M")
                            print(f"             Total: {total_length_no_start:.0f}mm vs limit {segment_length:.0f}mm", end="")
                        else:
                            # Standard printing for segments that didn't need a mirror anyway
                            print(f"          -> Testing swap: {num_lf} LF + {num_mf} MF + {mirror_count} M")
                            print(f"             Total: {total_length_no_start:.0f}mm vs limit {segment_length:.0f}mm", end="")
                        
                        if total_length_no_start <= segment_length:
                            print(" ✅ FITS! (Fallback/Standard Match)")
                            # If we needed a mirror but dropped it, pass False. If we didn't need one, also False.
                            best_solution = (num_lf, num_mf, False)
                            break
                        else:
                            print(" ❌ Too long")
                
                # --- APPLY SOLUTION ---
                if best_solution:
                    num_lf, num_mf, keep_start_mirror = best_solution
                    
                    # Update the flag for the builder function
                    needs_starting_mirror = keep_start_mirror 
                    
                    # final_pattern = self._build_fixture_pattern(
                    #     num_lf, num_mf, mirror_count, needs_starting_mirror,
                    #     segment_id=segment_id, primary_side=primary_side, segment_length=segment_length
                    # )
                    final_pattern = self._build_fixture_pattern(
                        num_lf, num_mf, mirror_count, needs_starting_mirror,
                        segment_id=segment_id, primary_side=primary_side, segment_length=segment_length,
                        last_segment_ended_with=last_segment_ended_with
                    )
                    final_plan[segment_id] = final_pattern


                    # RASHEEQUE--MODIFICATION--START--25/11/2025--
                    # --- FIX STARTS HERE (REPLACE OLD FLAG LOGIC WITH THIS) ---
                    # 1. Calculate exact used length to find remaining space
                    actual_used_length = (num_lf * LF_LEN) + (num_mf * MF_LEN) + (mirror_count * M_LEN)
                    if keep_start_mirror:
                        actual_used_length += M_LEN
                        
                    remaining_space = segment_length - actual_used_length
                    
                    
                    # 2. Set flag based on Pattern OR Remaining Space
                    if final_pattern and final_pattern[-1] == 'M':
                        # Priority 1: If pattern actually ends with a Mirror
                        last_segment_ended_with = 'M'
                    elif 200 <= remaining_space <= 299:
                        # Priority 2: If small gap remains, trick next segment (act as if it ended with Mirror)
                        print(f"             -> Remaining space ({remaining_space:.0f}mm) forces next segment to start with Fixture (Flag='M')")
                        last_segment_ended_with = 'M'
                    else:
                        # Priority 3: Otherwise, it ended with a Fixture
                        last_segment_ended_with = 'LF' 
                    # --- FIX ENDS HERE ---
                    #---RASHEEQUE--MODIFICATION--ENDS--25/11/2025--
                    # # Update continuity flag for the NEXT segment
                    # if final_pattern and final_pattern[-1] == 'M':
                    #     last_segment_ended_with = 'M'
                    # else:
                    #     last_segment_ended_with = 'LF' 
                        
                    print(f"\n          -> ✅ PHASE 1 SUCCESS!")
                    if not keep_start_mirror and starting_mirror_len > 0:
                        print(f"             ⚠️ (Start Mirror was dropped to fit capacity)")
                        
                    phase1_success = True
                    segment_plan_found = True
                    break # Exit while loop for this segment

                if phase1_success:
                    break

                # --- Phase 2: Mirror Reduction & Swap-Down ---
                print("    -> Phase 1 failed. Entering Phase 2 (Mirror Reduction)...")
                phase2_success = False
                
                min_mirrors_base = math.ceil(n / 2)
                min_mirrors = min_mirrors_base if min_mirrors_base % 2 != 0 else min_mirrors_base
                
                print(f"       -> Minimum mirrors for {n} fixtures: {min_mirrors}")
                
                starting_mirror_count_for_phase2 = min(mirror_count, n-1)
                
                print(f"\n       -> 🔍 DETAILED PHASE 2 TRACE for {n} fixtures:")
                print(f"       -> Starting with {starting_mirror_count_for_phase2} mirrors")
                print(f"       -> Will reduce down to minimum of {min_mirrors} mirrors")
                print(f"       -> Segment length available: {segment_length:.0f}mm")
                
                # Loop through reducing mirror counts
                for current_mirrors in range(starting_mirror_count_for_phase2, min_mirrors - 1, -1):
                    if current_mirrors < 0: continue
                    
                    steps_reduced = starting_mirror_count_for_phase2 - current_mirrors
                    remove_position = steps_reduced + 2
                    
                    print(f"\n       -> 💡 TRYING: {current_mirrors} mirrors (step {steps_reduced + 1})")
                    print(f"          Removing {remove_position}th mirror from end")

                    # Inside Phase 2, we apply the same "Check with Mirror -> Check without" logic
                    for swaps in range(n + 1):
                        num_lf, num_mf = n - swaps, swaps
                        
                        # 1. Check WITH mirror first (if needed)
                        if needs_starting_mirror:
                            len_with = (num_lf * LF_LEN) + (num_mf * MF_LEN) + (current_mirrors * M_LEN) + starting_mirror_len
                            
                            print(f"          -> Testing swap: {num_lf} LF + {num_mf} MF + {current_mirrors} M + {starting_mirror_len} start")
                            print(f"             Total: {len_with:.0f}mm vs limit {segment_length:.0f}mm", end="")

                            if len_with <= segment_length:
                                 print(" ✅ FITS!")
                                #  final_pattern = self._build_fixture_pattern(num_lf, num_mf, current_mirrors, True, segment_id=segment_id, primary_side=primary_side, segment_length=segment_length)
                                 final_pattern = self._build_fixture_pattern(
                                        num_lf, num_mf, mirror_count, needs_starting_mirror,
                                        segment_id=segment_id, primary_side=primary_side, segment_length=segment_length,
                                        last_segment_ended_with=last_segment_ended_with
                                    )
                                 final_plan[segment_id] = final_pattern
                                 
                                 if final_pattern and final_pattern[-1] == 'M': last_segment_ended_with = 'M'
                                 else: last_segment_ended_with = 'LF'

                                 phase2_success = True
                                 segment_plan_found = True
                                 break
                            else:
                                print(" ❌ Too long")
                        
                        # 2. Check WITHOUT mirror second
                        len_without = (num_lf * LF_LEN) + (num_mf * MF_LEN) + (current_mirrors * M_LEN)
                        
                        if needs_starting_mirror:
                             print(f"          -> Testing swap (No Start Mirror): {num_lf} LF + {num_mf} MF + {current_mirrors} M")
                        else:
                             print(f"          -> Testing swap: {num_lf} LF + {num_mf} MF + {current_mirrors} M")
                        
                        print(f"             Total: {len_without:.0f}mm vs limit {segment_length:.0f}mm", end="")

                        if len_without <= segment_length:
                            print(" ✅ FITS! (Fallback)")
                            # final_pattern = self._build_fixture_pattern(num_lf, num_mf, current_mirrors, False, segment_id=segment_id, primary_side=primary_side, segment_length=segment_length)
                            final_pattern = self._build_fixture_pattern(
                                num_lf, num_mf, mirror_count, needs_starting_mirror,
                                segment_id=segment_id, primary_side=primary_side, segment_length=segment_length,
                                last_segment_ended_with=last_segment_ended_with
                            )
                            final_plan[segment_id] = final_pattern

                            #---RASHEEQUE--MODIFICATION--START--FIXED--25/11/2025--    
                            remaining_space = segment_length - len_without
                            
                            # Priority 1: If the pattern actually ends with a mirror
                            if final_pattern and final_pattern[-1] == 'M': 
                                print("             -> Pattern ends with Mirror, so next segment starts with Fixture (Flag='M')")
                                last_segment_ended_with = 'M'
                            
                            # Priority 2: If remaining space is small (100-299mm), trick next segment to start with Fixture
                            elif 200 <= remaining_space <= 299:
                                print(f"             -> Remaining space ({remaining_space:.0f}mm) forces next segment to start with Fixture (Flag='M')")
                                last_segment_ended_with = 'M'
                            
                            # Priority 3: Otherwise, assume it ended with a fixture
                            else: 
                                last_segment_ended_with = 'LF'
                            #---RASHEEQUE--MODIFICATION--END--FIXED---25/11/2025-  
                            
                            # if final_pattern and final_pattern[-1] == 'M': last_segment_ended_with = 'M'
                            # else: last_segment_ended_with = 'LF'
                                
                            phase2_success = True
                            segment_plan_found = True
                            break
                        else:
                            print(" ❌ Too long")
                    
                    if phase2_success: break

                if not phase2_success:
                    mirror_count = min_mirrors - 1
                    print(f"\n       -> ⚠️ Phase 2 exhausted all options.")
                    print(f"          Setting mirror_count to {mirror_count} for next iteration.")

                if phase2_success:
                    break

                # --- Phase 3: Fixture Reduction ---
                print(f"\n    -> ⚠️ Phase 2 failed for n={n}. Entering Phase 3 (Fixture Reduction)...")
                print(f"       -> Reducing fixture count from {n} to {n-1}")
                print(f"       -> Overflow count increases by 1 (now {overflow_display_fixture + 1})")
                
                n -= 1
                overflow_display_fixture += 1    

                
            if not segment_plan_found:
                print(f"    -> ❌ FAILED: Could not fit any fixtures in this segment.")
                final_plan[segment_id] = []
            
            #----RASHEEQUE----MODIFICATION START(COMMENTED)--24-11-2025--
            # Update the flag for the next segment
            # last_segment_ended_with = final_plan.get(segment_id, ['M'])[-1] if final_plan.get(segment_id) else 'M'
            #----RASHEEQUE----MODIFICATION ENDS(COMMENTED)--24-11-2025--
            #----RASHEEQUE----MODIFICATION START--24-11-2025--

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

    def place_fixtures_from_plan(self, placement_dict: dict, doc):
        """
        Places wall fixtures, respects JJ->VC priority, mirrors on the right wall,
        and DELETES any trailing mirror from the end of a segment.
        """

        print("\n--- 🏗️ Executing Wall Fixture Placement (JJ -> VC Priority & Right Wall Mirroring) ---")

        # 1. Get family counts (Unchanged)
        family_totals = self.family_totals
        jj_family_key = next((key for key in family_totals if 'jj' in key), None)
        jj_family_count = family_totals.get(jj_family_key, 0)
        vc_family_count = family_totals.get('vc_fixture_family', 0)

        print(f"\n  -> Placement Priority based on Merch Mix:")
        print(f"     JJ Family Fixtures to Place: {jj_family_count}")
        print(f"     VC Family Fixtures to Place: {vc_family_count}")
        
        jj_fixtures_placed = 0

        # Helper function (Unchanged)
        def get_next_fixture_name(code, current_segment_data): 
            nonlocal jj_fixtures_placed
            layer_name = current_segment_data.get("layer_name", "Standard-Wall-Fixture-Layer")

            if jj_fixtures_placed < jj_family_count:
                jj_fixtures_placed += 1
                if layer_name == "Glass-FrontGlazing":
                    print(f"    -> Using 'jj_fixture_different' for Glass-FrontGlazing segment.")
                    return 'jj_fixture_different_large' if code == 'LF' else 'jj_fixture_different_medium'
                else:
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
                # ... (segment setup: p1, p2, wall_vector, etc. is all unchanged) ...
                seg_coords = segment_data['segment']
                p1 = Vec2(seg_coords[0], seg_coords[1])
                p2 = Vec2(seg_coords[2], seg_coords[3])
                wall_vector = (p2 - p1).normalize()
                wall_angle_deg = math.degrees(wall_vector.angle)
                inward_normal = wall_vector.orthogonal().normalize()
                mid_point_on_wall = p1.lerp(p2)
                test_point = mid_point_on_wall + inward_normal * 10
                if not self.floorplan_polygon.contains(Point(test_point)):
                    inward_normal *= -1

                pattern = segment_data.get('placement', [])
                if not pattern:
                    continue
                print(f"    -> Segment {seg_index}: Placing pattern {pattern}")

                # --- NEW: Store details of the last placed item ---
                last_placed_item_details = None
                # --- END NEW ---
                
                cursor = 0.0
                margin_from_wall = 1.0

                for fixture_code in pattern:
                    fixture_name = None
                    if fixture_code == 'M':
                        layer_name = segment_data.get("layer_name", "Standard-Wall-Fixture-Layer")
                        if layer_name == "Glass-FrontGlazing":
                            fixture_name = 'mirror'
                            print(f"    -> Using 'mirror_different' for Glass-FrontGlazing segment.")
                        else:
                            fixture_name = 'mirror_different'
                    elif fixture_code in ['LF', 'MF']:
                        fixture_name = get_next_fixture_name(fixture_code, segment_data)
                    
                    if not fixture_name:
                        continue
                    try:
                        fxtr = Fixture.Fixture(fixture_name, self.fixture_dict[fixture_name]["path"])
                    except Exception as e:
                        continue
                    if cursor + fxtr.width > segment_data['length'] + 50:
                        break                       
                    # --- Calculate Insertion Point ---
                    xscale = 1.0 if is_right_wall else 1.0
                    yscale = -1.0 if is_right_wall else 1.0
                    
                    # ... (calculation for target_center, final_insert_point is unchanged) ...
                    center_on_wall = p1 + wall_vector * (cursor + fxtr.width / 2.0)
                    offset_from_wall = margin_from_wall + fxtr.height / 2.0
                    target_center = center_on_wall + inward_normal * offset_from_wall
                    local_center = fxtr.bounding_box.center
                    local_center_scaled = Vec2(local_center.x * xscale, local_center.y * yscale)
                    rotated_offset = local_center_scaled.rotate(math.radians(wall_angle_deg))
                    final_insert_point = target_center - rotated_offset

                    # --- Place the Fixture ---
                    block_ref = doc.place_fixture(
                        fxtr,
                        (final_insert_point.x, final_insert_point.y, 0),
                        wall_angle_deg,
                        rotated=True,
                        xscale=xscale,
                        yscale=yscale
                    )

                    # *** Calculate and add Bounding Box ***
                    transform = Matrix44.chain(
                        Matrix44.translate(-local_center.x, -local_center.y, 0),
                        Matrix44.scale(xscale, yscale, 1.0),
                        Matrix44.z_rotate(math.radians(wall_angle_deg)),
                        Matrix44.translate(target_center.x, target_center.y, 0)
                    )
                    world_corners = list(transform.transform_vertices(fxtr.bounding_box.rect_vertices()))
                    aabb = BoundingBox2d(world_corners)
                    new_bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)

                    doc.placed_bboxes.append(new_bbox_tuple)

                    # --- NEW: Update the last placed item's details ---
                    last_placed_item_details = {
                        "code": fixture_code,
                        "block_ref": block_ref,
                        "bbox_tuple": new_bbox_tuple
                    }
                    # --- END NEW ---

                    cursor += fxtr.width
                
                # --- NEW: Check and delete trailing mirror AFTER segment loop ---
                if last_placed_item_details and last_placed_item_details["code"] == 'M':
                    print(f"  -> POST-PLACEMENT: Deleting trailing mirror from {side_key} - Segment {seg_index}")
                    
                    try:
                        # 1. Get the items to remove
                        mirror_ref_to_delete = last_placed_item_details["block_ref"]
                        mirror_bbox_to_remove = last_placed_item_details["bbox_tuple"]
                        
                        # 2. Delete the entity from modelspace
                        doc.msp.delete_entity(mirror_ref_to_delete)
                        
                        # 3. Remove its bounding box from the master list (by value, to be safe)
                        if mirror_bbox_to_remove in doc.placed_bboxes:
                            doc.placed_bboxes.remove(mirror_bbox_to_remove)
                            print(f"    -> Removed its bounding box: {mirror_bbox_to_remove}")
                        else:
                            print(f"    -> ⚠️ Could not find mirror's bounding box to remove: {mirror_bbox_to_remove}")

                    except Exception as e:
                        print(f"    -> ⚠️ Could not delete entity or its bbox: {e}")
                # --- END NEW ---

        print("\n--- ✅ Finished placing all wall fixtures from the plan. ---")

    def draw_perimeter_paths_for_validation(self, doc):
        """
        [DEBUG HELPER - UPDATED]
        Draws the perimeter paths but STOPS them at the RETAIL_SEPARATOR line.
        """
        print("\n--- 🎨 Drawing Perimeter Paths for Validation (Stopping at Retail Line) ---")

        # --- NEW: Get the retail separation line's Y-coordinate ---
        separator_line = doc.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
        # separator_line = doc.msp.query('LINE[layer=="BACK_WALL"]').first
        stop_line_y = None
        if separator_line:
            stop_line_y = separator_line.dxf.start.y
            print(f"  -> Found RETAIL_SEPARATOR line at y={stop_line_y:.0f}. Paths will stop here.")
        else:
            print("  -> No RETAIL_SEPARATOR line found. Paths will be drawn fully.")

        # --- Get both paths ---
        left_path_segments = self._get_perimeter_path_from_facade_left_start(doc)
        right_path_segments = self._get_perimeter_path_from_facade_right_start(doc)

        # --- Define Layers ---
        left_layer = "DEBUG_PATH_LEFT_CCW"
        right_layer = "DEBUG_PATH_RIGHT_CW"
        
        if left_layer not in doc.doc.layers:
            doc.doc.layers.add(name=left_layer, color=4)  # Cyan
        
        if right_layer not in doc.doc.layers:
            doc.doc.layers.add(name=right_layer, color=6)  # Magenta

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
                doc.msp.add_line(final_p1, final_p2, dxfattribs={"layer": left_layer, "lineweight": 50})
                
                # Add a numbered label to the (potentially trimmed) segment
                mid_point = final_p1.lerp(final_p2)
                doc.msp.add_mtext(f"L-{i+1}", dxfattribs={'char_height': 150, 'insert': mid_point, 'layer': left_layer})

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

                doc.msp.add_line(final_p1, final_p2, dxfattribs={"layer": right_layer, "lineweight": 50})
                mid_point = final_p1.lerp(final_p2)
                doc.msp.add_mtext(f"R-{i+1}", dxfattribs={'char_height': 150, 'insert': mid_point, 'layer': right_layer})


    #----RASHEEQUE----MODIFICATION START--24-11-2025--
    def analyze_remaining_wall_gaps(self, doc, wall_segments_data: dict, draw: bool = False) -> dict:
        """
        Calculates the remaining empty spaces on retail walls after fixture placement.
        It subtracts all placed fixture bounding boxes from the original wall segments.
        
        Returns:
            dict: A structure mirroring wall_segments_data, but containing lists of 
                  remaining gap segments instead of single wall definitions.
        """
        print("\n--- 📉 Analyzing Remaining Wall Gaps (Post-Placement) ---")
        
        remaining_data = {
            "left_segments": {},
            "right_segments": {}
        }
        
        # 1. Create a Union of ALL obstacles (Reality Check)
        # We buffer slightly (1.0mm) to handle floating point touches
        if doc.placed_bboxes:
            all_obstacles = [box(*b).buffer(1.0) for b in doc.placed_bboxes]
            combined_obstacles = unary_union(all_obstacles)
        else:
            combined_obstacles = Polygon()

        # Setup debug layer
        if draw:
            layer_name = "DEBUG_REMAINING_GAPS"
            if layer_name not in doc.doc.layers:
                doc.doc.layers.add(name=layer_name, color=2) # Yellow

        total_gaps_found = 0

        # 2. Iterate through Left and Right walls
        for side_key in ["left_segments", "right_segments"]:
            segments_dict = wall_segments_data.get(side_key, {})
            
            for seg_index, original_data in segments_dict.items():
                # Get original geometry
                coords = original_data["segment"] # (x1, y1, x2, y2)
                p1 = (coords[0], coords[1])
                p2 = (coords[2], coords[3])
                
                original_line = LineString([p1, p2])
                
                # 3. Perform the Subtraction (Wall - Obstacles)
                try:
                    remaining_geom = original_line.difference(combined_obstacles)
                except Exception as e:
                    print(f"  -> Error processing segment {side_key}_{seg_index}: {e}")
                    continue

                # 4. Process the result into a clean list of segments
                gaps_list = []
                
                # Helper to process a single linestring result
                def process_gap(line_geom):
                    # Ignore tiny gaps (e.g., < 50mm)
                    if line_geom.length > 50.0:
                        p_start = line_geom.coords[0]
                        p_end = line_geom.coords[-1]
                        
                        # Calculate vector for angle
                        vec = Vec2(p_end) - Vec2(p_start)
                        angle = math.degrees(vec.angle)
                        
                        gap_info = {
                            "segment": (p_start[0], p_start[1], p_end[0], p_end[1]),
                            "length": line_geom.length,
                            "angle": angle,
                            "original_segment_id": f"{side_key}_{seg_index}"
                        }
                        gaps_list.append(gap_info)
                        
                        # Visualize if requested
                        if draw:
                            doc.msp.add_line(
                                p_start, 
                                p_end, 
                                dxfattribs={
                                    "layer": layer_name, 
                                    "color": 2, # Yellow
                                    "lineweight": 50 # Thick line
                                }
                            )
                            # Add length label
                            mid = line_geom.centroid
                            doc.msp.add_mtext(
                                f"{line_geom.length:.0f}",
                                dxfattribs={
                                    "layer": layer_name, 
                                    "char_height": 100, 
                                    "color": 2, 
                                    "insert": (mid.x, mid.y)
                                }
                            )

                if remaining_geom.is_empty:
                    pass # No space left
                elif remaining_geom.geom_type == 'LineString':
                    process_gap(remaining_geom)
                elif remaining_geom.geom_type == 'MultiLineString':
                    for geom in remaining_geom.geoms:
                        process_gap(geom)
                
                # Store results
                if gaps_list:
                    remaining_data[side_key][seg_index] = gaps_list
                    total_gaps_found += len(gaps_list)

        print(f"  -> ✅ Analysis complete. Found {total_gaps_found} usable gaps.")
        return remaining_data

    def draw_remaining_wall_gaps(self, doc, remaining_segments_data: dict, depth: float = 250.0, layer_name: str = "REMAINING_WALL_GAPS"):
        """
        Draws rectangles representing the remaining empty wall spaces.
        The rectangle is formed by the wall segment and an offset line (depth) inward.
        """
        print(f"\n--- 🎨 Drawing Remaining Wall Gaps (Depth: {depth}mm) ---")
        
        # Create layer if it doesn't exist (Color 2 = Yellow)
        if layer_name not in doc.doc.layers:
            doc.doc.layers.add(name=layer_name, color=2) 

        count = 0
        
        # Loop through both sides
        for side_key in ["left_segments", "right_segments"]:
            segments_dict = remaining_segments_data.get(side_key, {})
            
            # Loop through original segments
            for seg_index, gaps_list in segments_dict.items():
                # Loop through the calculated gaps for that segment
                for gap in gaps_list:
                    try:
                        # 1. Get segment geometry
                        coords = gap["segment"] # (x1, y1, x2, y2)
                        p1 = Vec2(coords[0], coords[1])
                        p2 = Vec2(coords[2], coords[3])
                        
                        # 2. Calculate Inward Normal
                        wall_vec = (p2 - p1).normalize()
                        normal = wall_vec.orthogonal() # 90 deg rotation
                        
                        # Verify direction: Check a point slightly offset by the normal
                        # If that point is NOT inside the floorplan, flip the normal
                        test_point = p1.lerp(p2) + normal * 10.0
                        if not self.floorplan_polygon.contains(Point(test_point.x, test_point.y)):
                            normal = -normal
                        
                        # 3. Calculate the 4 corners of the rectangle
                        # Order: Start -> End -> End_Inward -> Start_Inward
                        p1_in = p1 + normal * depth
                        p2_in = p2 + normal * depth
                        
                        points = [
                            (p1.x, p1.y),
                            (p2.x, p2.y),
                            (p2_in.x, p2_in.y),
                            (p1_in.x, p1_in.y)
                        ]
                        
                        # 4. Draw the Outline
                        doc.msp.add_lwpolyline(
                            points, 
                            close=True, 
                            dxfattribs={"layer": layer_name, "lineweight": 25}
                        )
                        
                        # 5. Add a Hatch (ANSI31 pattern) for visibility
                        hatch = doc.msp.add_hatch(color=2, dxfattribs={"layer": layer_name})
                        # hatch.set_pattern_fill('ANSI31', scale=5.0, angle=45)
                        hatch.set_pattern_fill('SOLID', scale=1.0, angle=45)
                        hatch.paths.add_polyline_path(points, is_closed=True)
                        
                        count += 1
                    except Exception as e:
                        print(f"  -> Error drawing gap for {side_key}_{seg_index}: {e}")
        
        print(f"  -> Drawn {count} gap rectangles on layer '{layer_name}'.")

    def filter_remaining_segments_near_corners(self, remaining_segments_data: dict, internal_corners: list, threshold: float = 100.0) -> dict:
        """
        Filters the remaining wall segments, returning only those that are physically close
        to an internal corner. This helps identify usable corner nooks.
        
        Args:
            remaining_segments_data: The dictionary of gaps from analyze_remaining_wall_gaps.
            internal_corners: A list of corner dictionaries (containing 'point': (x,y)).
            threshold: Max distance (mm) to consider a segment "near" a corner.
        """
        print("\n--- 🔍 Filtering Remaining Segments Near Internal Corners ---")
        
        filtered_data = {
            "left_segments": {},
            "right_segments": {}
        }
        
        if not internal_corners:
            print("  -> No internal corners provided. Returning empty filter result.")
            return filtered_data

        # Create a set of corner points for fast lookup/distance check
        corner_points = [Vec2(c['point']) for c in internal_corners]
        
        count_found = 0

        for side_key in ["left_segments", "right_segments"]:
            segments_dict = remaining_segments_data.get(side_key, {})
            
            for seg_index, gaps_list in segments_dict.items():
                # This list will hold gaps that pass the check
                valid_gaps = []
                
                for gap in gaps_list:
                    coords = gap["segment"] # (x1, y1, x2, y2)
                    p1 = Vec2(coords[0], coords[1])
                    p2 = Vec2(coords[2], coords[3])
                    
                    # Check if P1 or P2 is close to any corner point
                    is_near = False
                    for cp in corner_points:
                        if p1.distance(cp) <= threshold or p2.distance(cp) <= threshold:
                            is_near = True
                            break
                    
                    if is_near:
                        valid_gaps.append(gap)
                        count_found += 1
                
                if valid_gaps:
                    filtered_data[side_key][seg_index] = valid_gaps

        print(f"  -> Found {count_found} segments near internal corners.")
        return filtered_data

    #----RASHEEQUE----MODIFICATION END --24-11-2025--

########################################################################################################################
########################################################################################################################
#########################################        FLOOR FIXTURES        #################################################
#########################################        FLOOR FIXTURES        #################################################
#########################################        FLOOR FIXTURES        #################################################
########################################################################################################################
########################################################################################################################

    
    #RASHEEQUE--EDITTED--THIS--FUNCTION--11-11-2025--
    def plan_and_place_euro_fixtures(self, draw_debug: bool = False):
        """
        Orchestrates the planning and placement of Euro Center fixtures, accounting for
        any overflow from the wall fixture placement.
        """
        print("\n--- 🚀 Orchestrating Euro Center Fixture Planning and Placement ---")

        # --- NEW LIST TO HOLD OUR RESULTS ---
        final_documents_list = []
        
        # 1. Define placement zone (and optionally draw it for debugging)
        # This call is necessary as it defines the zone used by the analysis functions.
        for doc in list(self.docs):
            
            # store calculated zone on the document so draw/grid funcs can use it
            doc.euro_zone = self.euro_center_placement_area(doc)
            if draw_debug:
                self.draw_euro_center_placement_zone(doc)
                # --- Generate and draw the ROW-WISE grid (0° Rotation) ---
                row_wise_coords = self.generate_row_wise_grid(doc)
                self.draw_grid_for_validation(
                    doc,
                    grid_points=row_wise_coords,
                    cell_width=1040.0,
                    cell_height=1175.0,
                    layer_name="DEBUG_GRID_ROW_WISE",
                    color=3  # Green
                )

                # # --- Generate and draw the COLUMN-WISE grid (90° Rotation) ---
                column_wise_coords = self.generate_column_wise_grid(doc)
                self.draw_grid_for_validation(
                    doc,
                    grid_points=column_wise_coords,
                    cell_width=1175.0,
                    cell_height=1040.0,
                    layer_name="DEBUG_GRID_COLUMN_WISE",
                    color=4  # Cyan
                )

        # 2. Update floor fixture count with     overflow from wall fixtures
        doc_len = len(self.docs)
        for i in range(doc_len):
            doc = self.docs[i]

            if doc.skip:
                print(f"  -> Doc {doc.ind} is already skipped. Carrying over.")
                final_documents_list.append(doc)
                continue

            print(f" ----> placing doc {doc.ind}")

            print(f"  -> for doc {doc.ind}")
            print(f"  -> Adding {doc.remaining_wall_fixtures} remaining wall fixtures to the floor fixture count.")
            doc.display_calcs['floor_fixtures'] = doc.display_calcs.get('floor_fixtures', 0) + doc.remaining_wall_fixtures
            print(f"  -> New total floor fixtures required: {doc.display_calcs['floor_fixtures']}")

            doc.euro_zone = self.euro_center_placement_area(doc)
            # self.draw_euro_center_placement_zone(doc)

            # 3. Analyze placement patterns and place the fixtures
            placement_blueprint = self.analyze_placement_patterns(doc)
            
            placement_blueprint = json.loads(json.dumps(placement_blueprint.get('all_options', {})))
            # print("\n--- Analyzed Placement Patterns ---")
            # print(json.dumps(placement_blueprint, indent=1))
            
            available_patterns  = []
            for key,value in placement_blueprint.items():
                available_patterns.append({key: value})
            
            available_patterns = sorted(
                available_patterns,
                key=lambda item: list(item.values())[0]['rank']
            )

            for key in available_patterns[:2]:
                print(key)
                print()
            print()

            print(len(self.docs))
            
            # doc_copy = doc.clone(len(self.docs))
            # # TODO: SPLIT THE PLANS HERE
            # if len(available_patterns) > 0:
            #     if len(available_patterns) > 1:
            #         doc_ind = doc.ind

            #         cur_len = len(self.docs)
            #         print("cur_len:", len(self.docs))
            #         self.docs.append(doc_copy.clone(len(self.docs)))
            #         self.docs[-1].ind = cur_len

            #         for obj in available_patterns[:2]:
            #             print("doc_ind: ", {doc_ind})
            #             for a,b in obj.items():
            #                 chosen_pattern_name = a
            #                 chosen_pattern_data = b
                        
            #             final_plan_details = self.arranging_analyzed_function(self.docs[doc_ind], chosen_pattern_name, chosen_pattern_data)
            #             # print("final_plan_details:", final_plan_details)
            #             print("\n--- Analyzed Placement Patterns ---")
            #             print(json.dumps(final_plan_details, indent=1))
                    
            #             # Store overflow count from the arrangement phase
            #             doc.overflow_fixture_count = final_plan_details.get('overflow_display', 0)
            #             print(f"  -> Overflow fixtures calculated during arrangement: {doc.overflow_fixture_count}")

            #             # 5. Place based on the arranged plan
            #             # ***MODIFICATION: Pass the main analysis_result_to_update dictionary***
            #             self.place_by_plan_euro(self.docs[doc_ind], final_plan_details)

            #             print("\n--- Analysis Result after Placement Update ---")
            #             print("cur_len:", len(self.docs))

            #             doc_ind = cur_len
            #         # self.docs = self.docs[:-1]

            #     else:
            #         chosen_pattern_name, chosen_pattern_data = available_patterns[0]
            #         final_plan_details = self.arranging_analyzed_function(doc, chosen_pattern_name, chosen_pattern_data)
                    
            #         # Store overflow count from the arrangement phase
            #         doc.overflow_fixture_count = final_plan_details.get('overflow_display', 0)
            #         print(f"  -> Overflow fixtures calculated during arrangement: {doc.overflow_fixture_count}")

            #         # 5. Place based on the arranged plan
            #         # ***MODIFICATION: Pass the main analysis_result_to_update dictionary***
            #         self.place_by_plan_euro(doc, final_plan_details)

            #         print("\n--- Analysis Result after Placement Update ---")
            # else:
            #     doc.skip = True
            #     print("SKIP DOC")
            #     print("could not find pattern for doc ")
        
            if len(available_patterns) > 0:
                # We have patterns. The original 'doc' will be replaced by clones.

                # Get the top 2 patterns
                for i, pattern_data_tuple in enumerate(available_patterns[:2]):
                    # Extract pattern name and data from the tuple
                    chosen_pattern_name, chosen_pattern_data = list(pattern_data_tuple.items())[0]

                    # 1. Create a NEW clone from the original doc
                    # We give it a temporary index; we'll fix it later.
                    new_doc_clone = doc.clone(ind=doc.ind * 10 + i) 

                    print(f"  -> Creating new plan (Doc {new_doc_clone.ind}) using pattern: '{chosen_pattern_name}'")

                    # 2. Run arrangement logic ON THE CLONE
                    final_plan_details = self.arranging_analyzed_function(new_doc_clone, chosen_pattern_name, chosen_pattern_data)

                    # 3. Store overflow count ON THE CLONE
                    new_doc_clone.overflow_fixture_count = final_plan_details.get('overflow_display', 0)

                    # 4. Place fixtures ON THE CLONE
                    self.place_by_plan_euro(new_doc_clone, final_plan_details)

                    # 5. Add the fully populated CLONE to our NEW list
                    final_documents_list.append(new_doc_clone)

            else:
                # No patterns were found for this doc. Mark it as skipped
                # and add the original doc to the final list.
                doc.skip = True
                print(f"SKIP DOC {doc.ind}: could not find any Euro patterns.")
                final_documents_list.append(doc)
        print("--- ✅ Euro Center Placement Orchestration Complete ---")
        

        # --- ADD THESE LINES AFTER IT ---

        # Now, replace the old list with our new, clean list
        self.docs = final_documents_list

        # Re-index all docs to be sequential (0, 1, 2, ...)
        for i, doc in enumerate(self.docs):
            doc.ind = i

        print(f"  -> Final document count after processing: {len(self.docs)}")

########################################################################################################################
########################################################################################################################
#########################################              TV              #################################################
#########################################              TV              #################################################
#########################################              TV              #################################################
########################################################################################################################
########################################################################################################################

    
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

    def draw_debug_polygon(self, doc, polygon: Polygon, layer_name: str, color: int = 1, visible_by_default: bool = False):
            """Draws a Shapely Polygon or MultiPolygon on a specified layer."""
            if not polygon or polygon.is_empty:
                return

            # --- START OF MODIFICATION ---
            
            # 1. Get or create the layer
            layer = None
            if layer_name not in doc.doc.layers:
                layer = doc.doc.layers.add(name=layer_name, color=abs(color)) 
            else:
                layer = doc.doc.layers.get(layer_name)

            if not layer:
                print(f"  -> ⚠️ ERROR: Could not get or create layer '{layer_name}'.")
                return
            
            # --- END OF MODIFICATION ---

            def draw_single_poly(poly):
                if poly.exterior:
                    doc.msp.add_lwpolyline(
                        list(poly.exterior.coords),
                        close=True,
                        dxfattribs={"layer": layer_name}
                    )
                for interior in poly.interiors:
                    doc.msp.add_lwpolyline(
                        list(interior.coords),
                        close=True,
                        dxfattribs={"layer": layer_name}
                    )

            # 2. DRAW THE GEOMETRY *FIRST*
            if polygon.geom_type == 'Polygon':
                draw_single_poly(polygon)
            elif polygon.geom_type == 'MultiPolygon':
                for poly in polygon.geoms:
                    draw_single_poly(poly)
            
            # --- START OF MODIFICATION ---
            # 3. SET THE VISIBILITY *AFTER* all entities have been added.
            #    This overrides any implicit "turn on" behavior from drawing.
            # layer.is_off = not visible_by_default
            if not visible_by_default:
                layer.freeze()
            else:
                layer.thaw()
            # --- END OF MODIFICATION ---

            visibility_status = "'Off'" if layer.is_off else "'On'"
            print(f"    -> Drawn debug shape on layer '{layer_name}' (Layer is now {visibility_status} by default)")

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

    #--RASHEEQU--EDITED--THIS--FUNCTION--03-12-2025--
    def _get_boh_perimeter_path_from_bottom_right_ccw(self, doc):
        """
        [NEW HELPER] Gets the BOH inner perimeter path, starting from the
        bottom-right corner and proceeding counter-clockwise.
        """

        # --- CACHING: Check if the path has already been calculated ---
        if doc.boh_perimeter_path is not None:
            return doc.boh_perimeter_path
        
        # Step 1: Get the inner BOH polygon
        boh_outlines = list(doc.msp.query('LWPOLYLINE[layer=="BOH_WALL_VALID_OUTLINE"]'))
        if not boh_outlines:
            boh_outlines = list(doc.msp.query('LWPOLYLINE[layer=="BOH_PARTITION_OUTLINE"]'))
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

        # --- CACHING: Store the result before returning ---
        doc.boh_perimeter_path = final_path
        return final_path


    def draw_boh_segment_order_for_validation_br_ccw(self, doc):
        """
        [DEBUG HELPER] Draws numbered labels on the BOH inner wall segments,
        starting from the bottom-right corner and proceeding counter-clockwise,
        to visually confirm the processing order.
        """

        print("\n--- 🎨 Drawing BOH Segment Order for Validation (Bottom-Right, CCW) ---")

        # 1. Get the correctly ordered perimeter path using the helper function
        perimeter_path = self._get_boh_perimeter_path_from_bottom_right_ccw(doc)
        if not perimeter_path:
            print("  -> SKIPPED: No BOH perimeter path found to draw.")
            return
        
        # 2. Define a new, highly visible layer for the debug drawings
        layer_name = "DEBUG_BOH_SEGMENT_ORDER_BR_CCW"
        if layer_name not in doc.doc.layers:
            doc.doc.layers.add(name=layer_name, color=1) # ACI color 1 is Red

        # 3. Loop through the segments and draw a label on each one
        for i, (p1, p2) in enumerate(perimeter_path):
            # Skip very short, insignificant segments
            if p1.distance(p2) < 450:
                continue

            # Calculate the midpoint of the segment to place the label
            mid_point = p1.lerp(p2)
            
            # Add a numbered text label
            doc.msp.add_mtext(
                f"BOH-{i+1}",
                dxfattribs={
                    'char_height': 150,  # Adjust text size as needed
                    'insert': mid_point,
                    'layer': layer_name
                }
            )
            
        print(f"  -> ✅ Drew {len(perimeter_path)} numbered labels on layer '{layer_name}'. Check the DXF file.")

    # touched
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

    # touched
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

    # touched
    def place_benches_3(self):
        for doc in self.docs:
            doc.door_results = self.detect_and_visualize_clinic_doors(doc, draw_bboxes=False)

            doc.pickup_table_debug_bboxes = self.detect_and_draw_pickup_table_bboxes(doc ,floor_unit_offset=750.0,draw_visual=False)

            doc.walkable_corners_raw, doc.walkable_segments_raw= self.detect_walkable_path_segments(doc)

            doc.trimmed_path_lines = self.trim_walkable_path_for_doors(doc, pickup_buffer=10.0) # Adjust this buffer around pickup tables as needed

            doc.trimmed_segments_json = self.segments_to_json(doc)

            self.place_benches_along_trimmed_path(doc)

        self._get_accurate_obstacle_bboxes(include_all=True) # Ensure bboxes are up-to-date
        
        # for doc in self.docs:
            # self.place_AR_along_trimmed_path(doc)
        # --- THIS IS THE MODIFIED LOOP ---
        for doc in self.docs:
            if doc.skip:
                continue
                
            # 1. Run the main placement and CATCH the remaining queue
            remaining_ar_queue = self.place_AR_along_trimmed_path(doc)

            # 2. If any ARs remain, start the NEW fallback logic
            if remaining_ar_queue:
                print(f"  -> Main AR placement left {len(remaining_ar_queue)} fixtures. Running new fallback...")
                
                # 2a. Get the anchor Y-coordinate
                min_y_clinic = self.get_clinic_min_y(doc)
                if min_y_clinic:
                    # 2b. Get the anchor X-coordinates
                    left_x, right_x = self.get_wall_x_for_AR(doc, min_y=min_y_clinic)
                    
                    # 2c. Create the fallback segments
                    fallback_segments_list = self.create_fallback_ar_segments_along_wall(
                        doc, 
                        min_y=min_y_clinic, 
                        left_x=left_x, 
                        right_x=right_x,
                        debug=False  # Keep debug on to see the lines
                    )
                    
                    # 2d. Call the new placement function with the segments
                    if fallback_segments_list:
                        self.place_AR_fallback_on_segments(
                            doc, 
                            remaining_ar_queue, 
                            fallback_segments_list,
                            debug=True # Enable debug drawing for validation
                        )
                    else:
                        print("  -> Could not create fallback segments. ARs will remain unplaced.")
                else:
                    print("  -> Could not get clinic min_y. Fallback aborted.")


            # 2. If any ARs remain, run the new fallback function
            # if remaining_ar_queue:
            #     print(f"  -> Main AR placement left {len(remaining_ar_queue)} fixtures. Running fallback...")
            #     self.place_AR_fallback_on_bench_segments(doc, remaining_ar_queue)
        # --- END OF MODIFICATION ---

    # touched
    def get_clinic_door_by_layer(self, clinic_entity) -> Optional[Tuple[float, float, float, float]]:
        """
        Finds the door/curtain location by searching for entities on a specific
        layer within the placed clinic's virtual entities. (Helper method)
        """
        # --- This function's code remains exactly the same as before ---
        print(f"  -> Searching for door geometry on layer '{self.DOOR_LAYER_NAME}' within {clinic_entity.dxf.name}...")
        try:
            door_entities = []
            for virtual_entity in clinic_entity.virtual_entities():
                if virtual_entity.dxf.hasattr('layer') and \
                   virtual_entity.dxf.layer.upper() == self.DOOR_LAYER_NAME.upper():
                    door_entities.append(virtual_entity)

            if not door_entities:
                print(f"    -> No entities found on layer '{self.DOOR_LAYER_NAME}'.") # Reduced verbosity
                return None

            bbox = extents(door_entities, fast=True)

            if bbox.has_data:
                bbox_coords = (bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y)
                print(f"    -> Found door geometry bounding box: {bbox_coords}") # Reduced verbosity
                return bbox_coords
            else:
                 print(f"    -> Warning: Found entities on layer '{self.DOOR_LAYER_NAME}' but could not calculate bounding box.")
                 return None

        except Exception as e:
            print(f"  -> ERROR searching for door geometry by layer in {clinic_entity.dxf.name}: {e}")
            # traceback.print_exc() # Keep commented unless debugging needed
            return None
        
    # touched
    def draw_detected_door_bbox(self, doc, door_bbox_coords: Tuple[float, float, float, float]):
        """
        [DEBUG HELPER] Draws the bounding box found by get_clinic_door_by_layer. (Helper method)
        """
         # --- This function's code remains exactly the same as before ---
        if not door_bbox_coords:
            return

        min_x, min_y, max_x, max_y = door_bbox_coords
        layer_name = "DEBUG_DOOR_DETECTION"
        if layer_name not in doc.doc.layers:
            doc.doc.layers.add(name=layer_name, color=1) # Red

        points = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
        doc.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": layer_name})
        # print(f"    -> Drawn detected door bounding box on layer '{layer_name}'.") # Reduced verbosity

    # touched
    def detect_and_draw_pickup_table_bboxes(self, doc, floor_unit_offset: float = 500.0, fallback_offset: float = 150.0, draw_visual: bool = True) -> List[Tuple[float, float, float, float]]:
        """
        [MODIFIED V4 - Fixed extent_vertices call] Detects placed 'pickup_table' fixtures.
        Calculates a bounding box based *specifically* on geometry on the 'Floor-Unit' layer,
        applies a larger offset (`floor_unit_offset`) to it, and constrains it to the BOH zone.
        If the 'Floor-Unit' layer is not found, it falls back to using the overall
        fixture bounding box with a smaller `fallback_offset` and constrains that.
        Optionally draws the final constrained box for debugging.

        Args:
            floor_unit_offset (float): Offset applied outwards if 'Floor-Unit' layer is found.
            fallback_offset (float): Offset applied outwards if 'Floor-Unit' is NOT found.
            draw_visual (bool): If True, draws the constrained offset bounding boxes.

        Returns:
            List[Tuple[float, float, float, float]]: A list containing the coordinates
                                                    (min_x, min_y, max_x, max_y)
                                                    of each CONSTRAINED offset bounding box.
        """

        print(f"\n--- 🔍 Detecting Pickup Tables (Layer Specific Offset, Constrained) ---")
        print(f"    Floor-unit Offset: {floor_unit_offset}mm, Fallback Offset: {fallback_offset}mm, Draw: {draw_visual}")

        layer_name = "DEBUG_PICKUP_TABLE_BBOX_CONSTRAINED"

    
        constrained_offset_bboxes = []

        # --- 1. Get the BOH Zone Polygon (Unchanged) ---
        boh_zone_poly = self._get_boh_zone_polygon(doc)
        if not boh_zone_poly or boh_zone_poly.is_empty:
            print("  -> ⚠️ WARNING: BOH zone polygon not found or is empty. Cannot constrain bounding boxes.")
            return constrained_offset_bboxes
        print("  -> Successfully obtained BOH zone polygon for constraining.")

        # --- 2. Query for the pickup_table fixtures (Unchanged) ---
        pickup_table_entities = [
            e for e in doc.msp.query('INSERT')
            if "PICKUP_TABLE" in e.dxf.name.upper()
        ]
        if not pickup_table_entities:
            print("  -> No 'pickup_table' fixtures found in the drawing.")
            return constrained_offset_bboxes
        print(f"  -> Found {len(pickup_table_entities)} 'pickup_table' fixture(s).")

        # --- 3. Process each found fixture ---
        for i, entity in enumerate(pickup_table_entities):
            print(f"  -> Processing fixture {i+1} ('{entity.dxf.name}')...")
            base_min_x, base_min_y, base_max_x, base_max_y = None, None, None, None
            offset_to_apply = fallback_offset # Default to fallback
            found_floor_unit = False

            try:
                # --- 4. Find 'Floor-Unit' geometry ---
                block = doc.doc.blocks.get(entity.dxf.name)
                if not block:
                    print(f"    -> WARNING: Block definition '{entity.dxf.name}' not found. Using fallback.")
                    overall_bbox = extents([entity])
                    if overall_bbox.has_data:
                        base_min_x, base_min_y = overall_bbox.extmin.x, overall_bbox.extmin.y
                        base_max_x, base_max_y = overall_bbox.extmax.x, overall_bbox.extmax.y
                    else:
                        print(f"    -> Skipping fixture {i+1}: Could not calculate overall bounding box.")
                        continue
                else:
                    # <<< Corrected Layer Name Check >>>
                    floor_unit_entities_local = [
                        e for e in block if e.dxf.layer == 'TABLE' # Use the exact name
                    ]
                    # <<< End Correction >>>

                    if floor_unit_entities_local:
                        print(f"    -> Found {len(floor_unit_entities_local)} entities on 'TABLE' layer.")
                        local_floor_unit_bbox = extents(floor_unit_entities_local)

                        if local_floor_unit_bbox.has_data:
                            transform_matrix = entity.matrix44()

                            # *********************************************************
                            # ******** THE FIX IS HERE - ADD PARENTHESES () ********
                            # world_corners = list(transform_matrix.transform_vertices(local_floor_unit_bbox.extent_vertices()))
                            # *********************************************************
                            # Build the four local corner points from extmin/extmax and transform them
                            extmin = local_floor_unit_bbox.extmin
                            extmax = local_floor_unit_bbox.extmax
                            # local 3D corners (z from extmin/extmax; usually 0)
                            local_corners = [
                                (extmin.x, extmin.y, getattr(extmin, "z", 0.0)),
                                (extmax.x, extmin.y, getattr(extmin, "z", 0.0)),
                                (extmax.x, extmax.y, getattr(extmax, "z", 0.0)),
                                (extmin.x, extmax.y, getattr(extmax, "z", 0.0)),
                            ]
                            world_corners = list(transform_matrix.transform_vertices(local_corners))
                        # Now world_corners is a list of transformed 3D points suitable for BoundingBox

                            wcs_floor_unit_bbox = BoundingBox(world_corners)
                            base_min_x, base_min_y = wcs_floor_unit_bbox.extmin.x, wcs_floor_unit_bbox.extmin.y
                            base_max_x, base_max_y = wcs_floor_unit_bbox.extmax.x, wcs_floor_unit_bbox.extmax.y

                            offset_to_apply = floor_unit_offset
                            found_floor_unit = True
                            print(f"    -> Using 'TABLE' geometry for bounding box.")

                        else:
                            print(f"    -> WARNING: Could not calculate bbox for 'TABLE' entities. Using fallback.")
                            overall_bbox = extents([entity])
                            if overall_bbox.has_data:
                                base_min_x, base_min_y = overall_bbox.extmin.x, overall_bbox.extmin.y
                                base_max_x, base_max_y = overall_bbox.extmax.x, overall_bbox.extmax.y
                            else:
                                print(f"    -> Skipping fixture {i+1}: Could not calculate overall bounding box.")
                                continue
                    else:
                        print(f"    -> WARNING: No entities found on 'Floor-Unit' layer. Using fallback.")
                        overall_bbox = extents([entity])
                        if overall_bbox.has_data:
                            base_min_x, base_min_y = overall_bbox.extmin.x, overall_bbox.extmin.y
                            base_max_x, base_max_y = overall_bbox.extmax.x, overall_bbox.extmax.y
                        else:
                            print(f"    -> Skipping fixture {i+1}: Could not calculate overall bounding box.")
                            continue

                # --- 5. Apply Offset (Unchanged) ---
                print(f"    -> Applying offset of {offset_to_apply}mm.")
                offset_min_x = base_min_x - offset_to_apply
                offset_min_y = base_min_y - offset_to_apply
                offset_max_x = base_max_x + offset_to_apply
                offset_max_y = base_max_y + offset_to_apply
                unconstrained_offset_box = box(offset_min_x, offset_min_y, offset_max_x, offset_max_y)

                # --- 6. CONSTRAINT LOGIC (Unchanged) ---
                constrained_area = unconstrained_offset_box.intersection(boh_zone_poly)
                if constrained_area.is_empty:
                    print(f"    -> Skipping fixture {i+1}: Offset area does not overlap with BOH zone.")
                    continue
                c_min_x, c_min_y, c_max_x, c_max_y = constrained_area.bounds
                constrained_coords = (c_min_x, c_min_y - 130, c_max_x, c_max_y)
                constrained_offset_bboxes.append(constrained_coords)
                print(f"    -> Calculated CONSTRAINED offset box: {constrained_coords}")

                # --- 7. Optionally draw (Unchanged) ---
                if draw_visual:
                    if layer_name not in doc.doc.layers:
                        doc.doc.layers.add(name=layer_name, color=3) # Green
                    points = [
                        (c_min_x, c_min_y), (c_max_x, c_min_y),
                        (c_max_x, c_max_y), (c_min_x, c_max_y)
                    ]
                    doc.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": layer_name})
                    print(f"      -> Drawn constrained debug box on layer '{layer_name}'.")

            except Exception as e:
                print(f"    -> ⚠️ ERROR processing fixture {i+1} ('{entity.dxf.name}'): {e}")
                import traceback
                traceback.print_exc()
                continue

        print(f"--- ✅ Finished Constrained Pickup Table Detection (Layer Specific) ---")
        return constrained_offset_bboxes

    # touched
    def detect_walkable_path_segments(self, doc) -> Tuple[List[Tuple[float, float]], List[Tuple[Tuple[float, float], Tuple[float, float]]]]:
        """
        [ROBUST V6] Detects the true walkable path using a pure geometric approach.
        1. Creates a "total back area" shape by uniting all BOH and Clinic polygons.
        2. Creates a "total retail area" polygon by subtracting the back area from the floorplan.
        3. The walkable path is the boundary of the retail area that is *shared* with the
           back area, effectively ignoring the main room walls.
        """
        print("\n--- 🚶 Detecting Walkable Path Segments (Robust Geometric Difference Strategy) ---")
        
        # A small tolerance for intersection/buffering operations
        tolerance = 1.0 
        # --- 1. Get all BOH and Clinic polygons ---
        clinic_polygons = self._get_all_clinic_polygons(doc)
        boh_polygons = self._get_all_boh_polygons(doc)
        back_wall = self._get_back_wall_polygons(doc)
        pickup_windows = self._get_all_pickup_window_polygons(doc)

        # all_component_polygons = clinic_polygons + boh_polygons + pickup_windows + back_wall
        # all_component_polygons = clinic_polygons + boh_polygons + pickup_windows #+ back_wall
        # --- NEW: Conditional logic based on floorplan dimensions ---
        height = self.cvc.max_y - self.cvc.min_y
        width = self.cvc.max_x - self.cvc.min_x
        dimension_difference = abs(height - width)
        
        if dimension_difference > 2000.0:
            print(f"  -> Floorplan dimension difference ({dimension_difference:.0f}mm) > 2000mm: Excluding back_wall")
            all_component_polygons = clinic_polygons + boh_polygons + pickup_windows
        else:
            print(f"  -> Floorplan dimension difference ({dimension_difference:.0f}mm) <= 2000mm: Including back_wall")
            all_component_polygons = clinic_polygons + boh_polygons + pickup_windows #+ back_wall
        # --- END NEW LOGIC ---

        if not all_component_polygons:
            print("  -> No BOH or Clinic shapes found. No path to detect.")
            return [], []
            
        # --- 2. Create the "total back area" shape ---
        # unary_union dissolves all internal shared walls
        all_back_area = unary_union(all_component_polygons)
        if all_back_area.is_empty:
            print("  -> BOH/Clinic shapes were empty. No path to detect.")
            return [], []

        # --- 3. Create the "total retail area" polygon ---
        # This is the floorplan with the BOH/Clinic islands "punched out"
        retail_polygon = self.floorplan_polygon.difference(all_back_area)

        # --- 4. Find the walkable path ---
        # The boundary of the retail area consists of two parts:
        # 1. The main room walls (from floorplan_polygon.boundary)
        # 2. The internal walls (from all_back_area.boundary)
        # We only want part 2.
        
        # By intersecting the retail boundary with a *slightly larger* back area,
        # we can isolate *only* the segments that come from the back area.
        walkable_path_geom = retail_polygon.boundary.intersection(all_back_area.buffer(tolerance))
        
        # --- 5. Process the resulting geometry ---
        walkable_segment_tuples = []
        
        def extract_segments(geom):
            if geom.is_empty:
                return
            elif geom.geom_type == 'LineString':
                coords = list(geom.coords)
                for i in range(len(coords) - 1):
                    p1 = coords[i]
                    p2 = coords[i+1]
                    if LineString([p1, p2]).length > 50: # Filter out tiny segments
                        walkable_segment_tuples.append((p1, p2))
            elif geom.geom_type in ['MultiLineString', 'GeometryCollection']:
                for g in geom.geoms:
                    extract_segments(g)
            # We don't care about Points or Polygons resulting from the intersection

        extract_segments(walkable_path_geom)

        # --- 6. Extract final points and return in the required format ---
        unique_points = set()
        for p1_tuple, p2_tuple in walkable_segment_tuples:
            unique_points.add( (round(p1_tuple[0], 3), round(p1_tuple[1], 3)) )
            unique_points.add( (round(p2_tuple[0], 3), round(p2_tuple[1], 3)) )

        final_corner_points = list(unique_points)
        
        print(f"\n  -> Robust geometric detection complete. Found {len(walkable_segment_tuples)} final path segments.")
        
        return final_corner_points, walkable_segment_tuples

    # touched
    def _get_all_clinic_polygons(self, doc) -> List[Polygon]:
        """
        [NEW ROBUST HELPER]
        Finds all placed clinic entities and returns a list of their exact
        Shapely Polygon geometries using get_outer_rect_corners_shapely.
        """
        print("    -> [Robust Path] Getting all individual clinic polygons...")
        
        clinic_entities = [e for e in doc.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
        polygons = []
        
        for entity in clinic_entities:
            try:
                # get_outer_rect_corners_shapely returns 4 (x, y, z) tuples
                corners_tuples = self.get_outer_rect_corners_shapely(entity)
                if len(corners_tuples) >= 4:
                    # Shapely Polygons are 2D, so we only take (x, y)
                    corners_xy = [(c[0], c[1]) for c in corners_tuples]
                    polygons.append(Polygon(corners_xy))
                else:
                    print(f"    -> WARNING: Could not get valid corners for {entity.dxf.name}")
            except Exception as e:
                print(f"    -> ERROR getting polygon for {entity.dxf.name}: {e}")
                
        print(f"    -> [Robust Path] Found {len(polygons)} clinic polygons.")
        return polygons

    # touched
    def _get_all_boh_polygons(self, doc) -> List[Polygon]:
        """
        [NEW ROBUST HELPER]
        Gets the BOH zone polygon and correctly returns a list of one or more
        polygons, handling the case where the BOH zone is a MultiPolygon.
        """
        
        boh_shape = self._get_boh_zone_polygon(doc)
        
        if not boh_shape or boh_shape.is_empty:
            return []
            
        if boh_shape.geom_type == 'Polygon':
            return [boh_shape]
        elif boh_shape.geom_type == 'MultiPolygon':
            return list(boh_shape.geoms)
            
        return []
    
    def _get_back_wall_polygons(self, doc) -> List[Polygon]:
        # --- FIX: Use a more robust, two-step query to avoid regex errors ---
        # Step 1: Get all polylines without a complex filter.
        all_polylines = doc.msp.query('LWPOLYLINE')
        
        # Step 2: Filter them in Python, which is safer than a complex query string.
        back_outlines = [
            p for p in all_polylines 
            if "BACK_WALL" in p.dxf.layer
        ]
        # --- END OF FIX ---
        
        if not back_outlines:
            return None

        polygons = [Polygon(list(p.get_points('xy'))) for p in back_outlines]
        
        # Merge all found polygons into a single shape
        boh_zone = unary_union(polygons)
        
        if not boh_zone or boh_zone.is_empty:
            return []
            
        if boh_zone.geom_type == 'Polygon':
            return [boh_zone]
        elif boh_zone.geom_type == 'MultiPolygon':
            return list(boh_zone.geoms)
            
        return []

    #--RASHEEQUE--ADD--THIS--FUNCTION--12-11-2025
    def _get_all_pickup_window_polygons(self, doc) -> List[Polygon]:
        """
        [NEW HELPER]
        Finds all placed pickup window / pickup-related INSERTs and returns a list
        of their exact Shapely Polygon geometries using get_outer_rect_corners_shapely.
        Behaviour mirrors _get_all_clinic_polygons but searches for PICKUP-related blocks.
        """
        print("    -> [Robust Path] Getting all pickup-window polygons...")

        # find INSERTs that likely represent pickup windows (robust substring match)
        pickup_entities = [e for e in doc.msp.query('INSERT') if "PICKUP" in e.dxf.name.upper()]
        polygons: List[Polygon] = []

        for entity in pickup_entities:
            try:
                # Prefer precise rotated corners when available
                corners_tuples = self.get_outer_rect_corners_shapely(entity)
                if corners_tuples and len(corners_tuples) >= 4:
                    corners_xy = [(c[0], c[1]) for c in corners_tuples]
                    polygons.append(Polygon(corners_xy))
                    continue

                # Fallback: use axis-aligned extents of the virtual entities
                bbox = extents(list(entity.virtual_entities()))
                if bbox.has_data:
                    minx, miny = bbox.extmin.x, bbox.extmin.y
                    maxx, maxy = bbox.extmax.x, bbox.extmax.y
                    polygons.append(Polygon([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)]))
                else:
                    print(f"    -> WARNING: Could not derive bbox for {entity.dxf.name}")
            except Exception as exc:
                print(f"    -> ERROR getting pickup polygon for {getattr(entity, 'dxf', {}).get('name', 'UNKNOWN')}: {exc}")

        print(f"    -> [Robust Path] Found {len(polygons)} pickup-window polygons.")
        return polygons



    # touched
    def trim_walkable_path_for_doors(self,
                                    doc, 
                                    pickup_buffer: float = 750.0, # Buffer around pickup table zones
                                    door_buffer: float = 30.0,
                                    door_extend_x: float = 0.0,
                                    door_extend_y: float = 0.0
                                    ) -> List[LineString]:
        """
        [MODIFIED] Takes the walkable path segments and trims them where they intersect
        with detected door bounding boxes AND optionally pickup table bounding boxes.

        Includes buffers around both types of obstacles.
        """
        print("\n--- ✂️ Trimming Walkable Path Segments for Doors & Pickup Tables ---")
        if not doc.walkable_segments_raw:
            print("  -> No walkable segments provided to trim.")
            return []

        # --- MODIFIED: Combine ALL obstacle polygons ---
        all_obstacle_polygons = []

        # 1. Process Door BBoxes (existing logic)
        if doc.door_results:
            print(f"  -> Processing {len(doc.door_results)} door bounding boxes...")
            valid_door_polygons = []
            for bbox in doc.door_results.values():
                if bbox:
                    try:
                        minx, miny, maxx, maxy = bbox
                        if door_extend_x or door_extend_y:
                            expanded_bbox = (minx - abs(door_extend_x), miny - abs(door_extend_y),
                                            maxx + abs(door_extend_x), maxy + abs(door_extend_y))
                            debug_msg = f"(override extend X={door_extend_x}, Y={door_extend_y})"
                        else:
                            OUTWARD_EXTEND = 500.0
                            width = maxx - minx
                            height = maxy - miny
                            if width >= height:
                                expanded_bbox = (minx + 25, miny - OUTWARD_EXTEND, maxx - 25, maxy + OUTWARD_EXTEND)
                                debug_msg = f"(auto-extended X by {OUTWARD_EXTEND}mm)"
                            else:
                                expanded_bbox = (minx - OUTWARD_EXTEND, miny + 25, maxx + OUTWARD_EXTEND, maxy - 25)
                                debug_msg = f"(auto-extended Y by {OUTWARD_EXTEND}mm)"

                        door_poly = box(*expanded_bbox).buffer(door_buffer, join_style=2)
                        if not door_poly.is_empty:
                            valid_door_polygons.append(door_poly)
                            print(f"    -> Door bbox expanded {debug_msg}: {expanded_bbox}") # Optional debug
                    except Exception as e:
                        print(f"    -> Warning: Could not process a door bbox: {e}")
            all_obstacle_polygons.extend(valid_door_polygons)
            print(f"    -> Added {len(valid_door_polygons)} door obstacle polygons.")

        # 2. Process Pickup Table BBoxes (NEW logic)
        if doc.pickup_table_debug_bboxes:
            print(f"  -> Processing {len(doc.pickup_table_debug_bboxes)} pickup table bounding boxes...")
            valid_pickup_polygons = []
            for bbox_tuple in doc.pickup_table_debug_bboxes:
                try:
                    pickup_poly = box(*bbox_tuple).buffer(pickup_buffer, join_style=2)
                    if not pickup_poly.is_empty:
                        valid_pickup_polygons.append(pickup_poly)
                except Exception as e:
                    print(f"    -> Warning: Could not process a pickup table bbox {bbox_tuple}: {e}")
            all_obstacle_polygons.extend(valid_pickup_polygons)
            print(f"    -> Added {len(valid_pickup_polygons)} pickup table obstacle polygons (buffer={pickup_buffer}mm).")
        # --- END MODIFICATION ---

        if not all_obstacle_polygons:
            print("  -> No valid obstacle polygons created (doors or pickup tables). Returning original segments.")
            return [LineString(segment) for segment in doc.walkable_segments_raw]

        # Combine ALL obstacle areas
        obstacles_union = unary_union(all_obstacle_polygons)
        print(f"  -> Created a combined shape for {len(all_obstacle_polygons)} total obstacle areas.")
        

        # Draw combined debug shape (optional)
        # self.draw_debug_polygon(obstacles_union, "DEBUG_COMBINED_OBSTACLE_UNION", color=6) # Magenta
        self.draw_debug_polygon(doc, obstacles_union, "DEBUG_COMBINED_OBSTACLE_UNION", color=6, visible_by_default=False) # Magenta, hidden by default

        # Trim segments using the combined obstacles (existing logic)
        trimmed_segments = []
        for i, segment_tuple in enumerate(doc.walkable_segments_raw):
            try:
                segment_line = LineString(segment_tuple)
                remaining_geometry = segment_line.difference(obstacles_union) # Use combined union here

                # print(f"    -> Segment {i}: Original Length={segment_line.length:.0f}, After Difference: {remaining_geometry.geom_type}, New Length={remaining_geometry.length:.0f}") # Optional debug

                if remaining_geometry.is_empty:
                    continue
                elif remaining_geometry.geom_type == 'LineString':
                    trimmed_segments.append(remaining_geometry)
                elif remaining_geometry.geom_type == 'MultiLineString':
                    trimmed_segments.extend(list(remaining_geometry.geoms))

            except Exception as e:
                print(f"    -> Warning: Error processing segment {segment_tuple}: {e}")

        print(f"  -> Trimming complete. Resulted in {len(trimmed_segments)} final path segments.")
        return trimmed_segments

    # touched
    def segments_to_json(self, doc) -> str:
        """
        Converts a list of Shapely LineString segments into a JSON string.
        Each segment is represented as an object with 'start' and 'end' points.

        Args:
            segment_lines: A list of Shapely LineString objects.

        Returns:
            A JSON formatted string representing the segments (including their lengths), or an empty list '[]' if input is empty.
        """
        output_data = []
        if not doc.trimmed_path_lines:
            return json.dumps(output_data) # Return empty JSON list

        print(f"\n--- 📄 Converting {len(doc.trimmed_path_lines)} trimmed segments to JSON ---")

        for i, line in enumerate(doc.trimmed_path_lines):
            if line.length < 1.0: # Skip very small remnants
                continue

            # Extract start and end coordinates
            start_point = line.coords[0]
            end_point = line.coords[-1]

            segment_dict = {
                "id": f"segment_{i+1}",
                "start": [round(start_point[0], 2), round(start_point[1], 2)],
                "end": [round(end_point[0], 2), round(end_point[1], 2)],
                "length": round(line.length, 2) # Add the length here
            }
            output_data.append(segment_dict)

        # Convert the list of dictionaries to a JSON string with indentation
        json_output = json.dumps(output_data, indent=2)
        print("  -> Conversion complete.")
        return json_output
    
    # touched
    def place_benches_along_trimmed_path(self, doc):
        """
        Places benches along the trimmed walkable path, prioritizing clinic-adjacent segments
        and placing larger benches first. NOW PASSES combined_shape to helper.
        """

        # --- NEW: Filter out RETAIL_SEPARATOR from obstacles for bench placement ---
        temp_obstacles_for_benches = list(doc.placed_bboxes) # Work with a copy
        separator_line = doc.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
        if separator_line:
            start_pt = separator_line.dxf.start
            end_pt = separator_line.dxf.end
            # Recreate the exact bbox tuple used when adding the obstacle
            separator_bbox = (
                min(start_pt.x, end_pt.x),
                min(start_pt.y, end_pt.y) - 1,
                max(start_pt.x, end_pt.x),
                max(start_pt.y, end_pt.y) + 1
            )
            # Remove it if found
            if separator_bbox in temp_obstacles_for_benches:
                temp_obstacles_for_benches.remove(separator_bbox)
                print("  -> Ignoring 'RETAIL_SEPARATOR' line during bench placement validation.")
            else:
                 print("  -> 'RETAIL_SEPARATOR' bbox not found in obstacle list (might have been removed already).")

        # --- END NEW ---

        print("\n--- 🛋️ Placing Benches Along Trimmed Walkable Path ---")

        # 1. Load Benches (Unchanged)
        # ... (keep existing bench loading code) ...
        try:
            bench_config = self.fixtures.get("Bench_fixtures", {})
            benches_to_place_list = [
                Fixture.Fixture(name, self.fixture_dict[name]["path"])
                for name, count in bench_config.items() if count > 0 and name != "AR" # Exclude AR
                for _ in range(count)
            ]
            if not benches_to_place_list:
                print("  -> SKIPPED: No bench fixtures (excluding AR) specified.")
                return

            benches_to_place_list.sort(key=lambda f: f.width, reverse=True)
            bench_queue = collections.deque(benches_to_place_list)
            print(f"  -> Loaded {len(bench_queue)} benches to place (largest first).")

        except Exception as e:
            print(f"  -> 🔥 ERROR loading bench fixtures: {e}")
            return


        # --- NEW: Calculate Combined Clinic/BOH Shape ---
        boh_zone_poly = self._get_boh_zone_polygon(doc)
        if boh_zone_poly and boh_zone_poly.is_empty: boh_zone_poly = None
        clinic_polygons_list = []
        clinic_entities = [e for e in doc.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
        if clinic_entities:
            for entity in clinic_entities:
                try:
                    bbox = extents(list(entity.virtual_entities()))
                    if bbox.has_data: clinic_polygons_list.append(box(bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y))
                except Exception: pass
        shapes_to_combine = [p for p in ([boh_zone_poly] + clinic_polygons_list) if p]
        combined_shape = unary_union(shapes_to_combine) if shapes_to_combine else None
        if not combined_shape or combined_shape.is_empty:
             print("  -> ⚠️ WARNING: Could not determine combined Clinic/BOH shape. Bench orientation might be incorrect.")
             # Create a dummy empty polygon to avoid errors later
             combined_shape = Polygon()
        # --- END NEW ---

        # 2. Get Clinic and BOH Polygons (Keep original logic for proximity check)
        # ... (keep existing clinic_polygons_union and boh_polygon calculation for proximity) ...
        clinic_polygons = []
        if clinic_entities:
            for entity in clinic_entities:
                try:
                    bbox = extents(list(entity.virtual_entities()))
                    if bbox.has_data: clinic_polygons.append(box(bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y))
                except Exception: pass
        clinic_polygons_union = unary_union(clinic_polygons) if clinic_polygons else None
        boh_polygon = self._get_boh_zone_polygon(doc)


        # 3. Classify and Prepare Segments
        classified_segments = {'clinic': [], 'boh': [], 'other': []}
        for i, line in enumerate(doc.trimmed_path_lines):
            proximity = self._get_segment_proximity(line, clinic_polygons_union, boh_polygon) # type: ignore
            if line.length > 900: # Only consider segments longer than 900mm
                # --- NEW: Calculate angle ---
                p1 = Vec2(line.coords[0])
                p2 = Vec2(line.coords[-1])
                segment_angle_deg = math.degrees((p2 - p1).normalize().angle)
                # --- END NEW ---
                classified_segments[proximity].append({
                    'id': i,
                    'line': line,
                    'length': line.length,
                    'available_length': line.length,
                    'cursor': 5.0,
                    'start_from_end': True,
                    'angle': segment_angle_deg # Store the angle
                })

        # --- NEW: Custom Sorting Logic ---
        def sort_key(segment_data):
            proximity = segment_data['proximity'] # We'll add this key temporarily
            angle = segment_data['angle']
            length = segment_data['length']

            # Define angle categories
            is_vertical = (75 <= abs(angle) <= 125) or (255 <= abs(angle) <= 285) or (-75 <= abs(angle) <= -125) or (-255 <= abs(angle) <= -285)
            # Check for horizontal: angle close to 0 or 180
            is_horizontal = (abs(angle) <= 15) or (abs(angle - 180) <= 15) or (abs(angle + 180) <= 15) or (abs(angle - 360) <= 15) or (abs(angle + 360) <= 15)

            # Assign primary priority based on proximity
            if proximity == 'clinic':
                priority_proximity = 0
                # Assign secondary priority based on angle (vertical first)
                priority_angle = 0 if is_vertical else 1
            elif proximity == 'boh':
                priority_proximity = 1
                # Assign secondary priority based on angle (horizontal first)
                priority_angle = 0 if is_horizontal else 1
            else: # 'other'
                priority_proximity = 2
                priority_angle = 0 # No angle preference for 'other'

            # Final key: Proximity -> Angle Preference -> Length (descendinegment_priority_order = classified_segments['clinic'] + classified_g)
            return (priority_proximity, priority_angle, -length)

        # Add proximity key temporarily for sorting
        all_segments_with_proximity = []
        for prox, segments in classified_segments.items():
            for seg in segments:
                seg['proximity'] = prox
                all_segments_with_proximity.append(seg)

        # Sort using the custom key
        all_segments_with_proximity.sort(key=sort_key)

        # Remove the temporary proximity key
        for seg in all_segments_with_proximity:
            del seg['proximity']

        # The final prioritized order
        segment_priority_order = all_segments_with_proximity
        # --- END NEW SORTING LOGIC ---

        print(f"  -> Classified and PRIORITIZED segments:")
        for i, seg_data in enumerate(segment_priority_order):
             print(f"     {i+1}. Segment {seg_data['id']} (Length: {seg_data['length']:.0f}mm, Angle: {seg_data['angle']:.1f}°, Type: {'Clinic-V' if (75 <= abs(seg_data['angle']) <= 125) else ('BOH-H' if (abs(seg_data['angle']) <= 15 or abs(seg_data['angle']-180) <= 15) else 'Other')})")

        # 4. Define Placement Order (Unchanged)
        # segment_priority_order = classified_segments['clinic'] + classified_segments['boh']

        # 5. Iterative Placement
        placed_count = 0
        total_to_place = len(bench_queue)

        for segment_data in segment_priority_order:
            if not bench_queue: break

            print(f"  -> Processing Segment {segment_data['id']} (Length: {segment_data['length']:.0f}mm)...")

            while bench_queue and segment_data['available_length'] > 50:
                bench_to_try = bench_queue[0]

                # --- MODIFIED CALL: Pass combined_shape ---
                # was_placed = self._place_bench_on_segment(bench_to_try, segment_data, placed_bboxes, combined_shape)
                # --- MODIFIED CALL: Pass the filtered obstacle list ---
                was_placed = self._place_bench_on_segment(
                    doc,
                    bench_to_try,
                    segment_data,
                    temp_obstacles_for_benches, # Use the filtered list for validation
                    combined_shape,
                )
                # --- END MODIFIED CALL ---
                # --- END MODIFIED CALL ---

                if was_placed:
                    bench_queue.popleft()
                    placed_count += 1
                else:
                    if segment_data['available_length'] < bench_to_try.width:
                         print(f"    -> No more space on segment {segment_data['id']} for '{bench_to_try.name}'. Moving to next segment.")
                         break

        # 6. Final Report (Unchanged)
        # ... (keep existing final report code) ...
        print(f"\n--- ✅ Bench Placement Along Path Complete ---")
        print(f"  -> Placed {placed_count} out of {total_to_place} benches.")
        if bench_queue:
            print(f"  -> ⚠️ Could not place {len(bench_queue)} benches:")
            for bench in bench_queue:
                print(f"     - {bench.name}")
 
    # touched
    def place_AR_along_trimmed_path(self, doc):
        """
        [MODIFIED] Places AR fixture(s) along the trimmed walkable path.
        - Now passes the outward_normal vector to the validation function
          to enable aisle checking.
        """

        print("\n--- 🤖 Placing AR Fixture(s) Along Trimmed Walkable Path (Prioritized, Parallel) ---")

        # --- 1. Load AR Fixture(s) ---
        try:
            ar_count = self.fixtures.get("Bench_fixtures", {}).get("AR", 0)
            if ar_count <= 0:
                print("  -> SKIPPED: No 'AR' fixture specified.")
                return
            ar_fxtr_template = Fixture.Fixture("AR", self.fixture_dict["AR"]["path"])
            ar_fxtr_list = [ar_fxtr_template] * ar_count
            ar_queue = collections.deque(ar_fxtr_list)
            print(f"  -> Loaded {len(ar_queue)} AR fixture(s) to place.")
        except Exception as e:
            print(f"  -> 🔥 ERROR loading AR fixture: {e}")
            traceback.print_exc()
            return

        # --- 2. Calculate Combined Shape & Proximity Anchors ---
        boh_zone_poly = self._get_boh_zone_polygon(doc)
        if boh_zone_poly and boh_zone_poly.is_empty: boh_zone_poly = None
        clinic_polygons_list = []
        clinic_entities = [e for e in doc.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
        if clinic_entities:
            for entity in clinic_entities:
                try:
                    bbox = extents(list(entity.virtual_entities()))
                    if bbox.has_data: clinic_polygons_list.append(box(bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y))
                except Exception: pass
        clinic_polygons_union = unary_union(clinic_polygons_list) if clinic_polygons_list else None
        shapes_to_combine = [p for p in ([boh_zone_poly] + clinic_polygons_list) if p]
        combined_shape = unary_union(shapes_to_combine) if shapes_to_combine else Polygon()
        if combined_shape.is_empty:
             print("  -> ⚠️ WARNING: Could not determine combined shape. Orientation might be incorrect.")

        # --- 3. Classify, Filter, Prepare Segments ---
        classified_segments = {
            'clinic_horizontal': [], 'clinic_vertical': [],
            'boh_horizontal': [], 'boh_vertical': [],
            'other': []
        }
        horizontal_angle_tolerance = 15.0
        vertical_angle_tolerance = 15.0
        min_segment_length = 100.0

        for i, line in enumerate(doc.trimmed_path_lines):
            if line.length <= min_segment_length:
                continue
            proximity = self._get_segment_proximity(line, clinic_polygons_union, boh_zone_poly)
            p1 = Vec2(line.coords[0])
            p2 = Vec2(line.coords[-1])
            segment_vector = (p2 - p1).normalize()
            segment_angle_deg = math.degrees(segment_vector.angle)
            norm_angle = abs(segment_angle_deg + 360) % 360
            is_horizontal = (norm_angle <= horizontal_angle_tolerance or
                             abs(norm_angle - 180) <= horizontal_angle_tolerance or
                             abs(norm_angle - 360) <= horizontal_angle_tolerance)
            is_vertical = (abs(norm_angle - 90) <= vertical_angle_tolerance or
                           abs(norm_angle - 270) <= vertical_angle_tolerance)
            segment_data = {
                'id': i, 'line': line, 'length': line.length,
                'available_length': line.length, 'cursor': 5.0,
                'start_from_end': True
            }
            if proximity == 'clinic':
                if is_horizontal: classified_segments['clinic_horizontal'].append(segment_data)
                elif is_vertical: classified_segments['clinic_vertical'].append(segment_data)
                else: classified_segments['other'].append(segment_data)
            elif proximity == 'boh':
                if is_horizontal: classified_segments['boh_horizontal'].append(segment_data)
                elif is_vertical: classified_segments['boh_vertical'].append(segment_data)
                else: classified_segments['other'].append(segment_data)
            else: classified_segments['other'].append(segment_data)

        # --- 4. Sort within each category ---
        for key in classified_segments:
            classified_segments[key].sort(key=lambda s: s['length'], reverse=False)

        # --- 5. Create Final Prioritized Order ---
        segment_priority_order = (
            classified_segments['boh_horizontal'] +
            classified_segments['clinic_horizontal'] +
            classified_segments['clinic_vertical'] +
            classified_segments['boh_vertical'] +
            classified_segments['other']
        )
        print(f"  -> Prepared {len(segment_priority_order)} potential segments (>= {min_segment_length}mm) for placement (Prioritized).")

        # --- 6. Iterative Placement ---
        placed_count = 0
        total_to_place = len(ar_queue)
        temp_obstacles_for_validation = list(doc.placed_bboxes) 
        separator_line = doc.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
        if separator_line:
            try:
                start_pt = separator_line.dxf.start
                end_pt = separator_line.dxf.end
                separator_bbox_tuple = (
                    min(start_pt.x, end_pt.x),
                    min(start_pt.y, end_pt.y) - 1, 
                    max(start_pt.x, end_pt.x),
                    max(start_pt.y, end_pt.y) + 1  
                )
                if separator_bbox_tuple in temp_obstacles_for_validation:
                    temp_obstacles_for_validation.remove(separator_bbox_tuple)
                    print("  -> ✅ Successfully removed 'RETAIL_SEPARATOR' line from obstacles FOR AR VALIDATION.")
            except Exception as e:
                print(f"  -> ⚠️ Error removing separator line obstacle: {e}")
        
        for segment_data in segment_priority_order:
            if not ar_queue: break
            print(f"  -> Processing Segment {segment_data['id']} (Length: {segment_data['length']:.0f}mm)...")
            while ar_queue and segment_data['available_length'] > 50:
                ar_to_try = ar_queue[0]

                # *** MODIFIED CALL: Pass the combined_shape ***
                was_placed = self._place_ar_on_segment(
                    doc,
                    ar_to_try,
                    segment_data,
                    temp_obstacles_for_validation, 
                    combined_shape, # Pass the combined shape
                    gap_from_path=0.0
                )
                # *** END MODIFIED CALL ***

                if was_placed:
                    ar_queue.popleft()
                    placed_count += 1
                    if doc.placed_bboxes:
                        temp_obstacles_for_validation.append(doc.placed_bboxes[-1])
                        # Also add the aisle box, which is the new last item
                        if len(doc.placed_bboxes) > 1:
                            temp_obstacles_for_validation.append(doc.placed_bboxes[-2])
                    print(f"    -> Successfully placed AR #{placed_count} on segment {segment_data['id']}.")
                else:
                    ar_width_along_path = ar_to_try.width if ar_to_try.width >= ar_to_try.height else ar_to_try.height
                    if segment_data['available_length'] < ar_width_along_path:
                        print(f"    -> Not enough remaining space on segment {segment_data['id']} for AR. Moving to next segment.")
                        break
                    else:
                        print(f"    -> Could not place AR on segment {segment_data['id']} at current cursor (blocked).")
                        # Nudge the cursor to avoid getting stuck
                        segment_data['cursor'] += 100.0
                        segment_data['available_length'] -= 100.0


        # --- 7. Final Report ---
        print(f"\n--- ✅ AR Placement Along Path Complete ---")
        print(f"  -> Placed {placed_count} out of {total_to_place} AR fixtures.")
        if ar_queue:
            print(f"  -> ⚠️ Could not place {len(ar_queue)} AR fixtures due to space constraints or overlaps.")

        return ar_queue

    
    def _place_ar_on_segment(self, doc, ar_fxtr: Fixture, segment_data: dict, temp_obstacles_for_validation: list, combined_shape: Polygon, gap_from_path: float = 0.0) -> bool:
        """
        [MODIFIED WITH FALLBACK] Attempts to place an AR fixture.
        - Tries placing the LONGEST side parallel first.
        - If that fails, tries placing the SHORTER side parallel.
        - Includes wall nudge logic for both attempts.
        """

        try:
            segment_line = segment_data['line']
            start_point = Vec2(segment_line.coords[0])
            end_point = Vec2(segment_line.coords[-1])
            cursor = segment_data['cursor']
            available_length = segment_data['available_length']
            start_from_end = segment_data.get('start_from_end', True)
        except (KeyError, IndexError, TypeError) as e:
             print(f"    -> ERROR: Invalid segment_data for AR: {e}")
             return False

        base_segment_angle_deg = math.degrees((end_point - start_point).normalize().angle)

        # --- Calculate Outward Normal (shared by both attempts) ---
        segment_vector = (end_point - start_point).normalize()
        mid_point_vec = start_point.lerp(end_point)
        normal_cw = segment_vector.orthogonal(ccw=False).normalize()
        normal_ccw = segment_vector.orthogonal(ccw=True).normalize()
        point_cw = Point(mid_point_vec + normal_cw * 10.0)
        point_ccw = Point(mid_point_vec + normal_ccw * 10.0)
        outward_normal = normal_cw # Default
        if combined_shape and not combined_shape.is_empty:
             if combined_shape.contains(point_ccw):
                 outward_normal = normal_cw
             elif combined_shape.contains(point_cw):
                 outward_normal = normal_ccw
        # --- End Normal Calculation ---

        # --- Define the two orientations to try ---
        
        ar_width_native = ar_fxtr.width
        ar_height_native = ar_fxtr.height

        # Orientation 1: Longest side parallel (thin profile)
        dim_along_1 = ar_width_native
        dim_perp_1 = ar_height_native
        add_rot_1 = 0
        if ar_height_native > ar_width_native: # If TALL
            dim_along_1 = ar_height_native
            dim_perp_1 = ar_width_native
            add_rot_1 = 90
        
        # Orientation 2: Shorter side parallel (wide profile)
        dim_along_2 = dim_perp_1
        dim_perp_2 = dim_along_1
        add_rot_2 = (add_rot_1 + 90) % 180

        orientations_to_try = [
            {"name": "Long side parallel", "dim_along": dim_along_1, "dim_perp": dim_perp_1, "add_rot": add_rot_1},
            {"name": "Short side parallel", "dim_along": dim_along_2, "dim_perp": dim_perp_2, "add_rot": add_rot_2},
        ]

        # --- Loop through both attempts ---
        for attempt, config in enumerate(orientations_to_try):
            
            dimension_along_path = config["dim_along"]
            dimension_perpendicular = config["dim_perp"]
            final_placement_angle_deg = (base_segment_angle_deg + config["add_rot"]) % 360

            print(f"    -> Attempt {attempt + 1} ({config['name']}): Trying spot for '{ar_fxtr.name}'. Angle: {final_placement_angle_deg:.1f}°")

            if dimension_along_path > available_length + 300 :
                print(f"      -> Fixture ({dimension_along_path:.0f}mm) too long for remaining segment space ({available_length:.0f}mm). Skipping orientation.")
                continue # Skip this orientation, try the next one

            # --- Calculate Target Center ---
            if start_from_end:
                center_along_segment = end_point - segment_vector * (cursor + dimension_along_path / 2.0)
            else:
                center_along_segment = start_point + segment_vector * (cursor + dimension_along_path / 2.0)

            center_offset_outward = outward_normal * (gap_from_path + dimension_perpendicular / 2.0)
            target_center = center_along_segment + center_offset_outward

            # --- Attempt 1: Validate and Place at Initial Position ---
            new_bbox_tuple = self._validate_and_place_at_point_new_bench( 
                doc, ar_fxtr, target_center, final_placement_angle_deg,
                temp_obstacles_for_validation, 
                outward_normal=outward_normal,
                debug=False
            )

            if new_bbox_tuple:
                # --- Success ---
                gap_between = 0.0 
                segment_data['cursor'] += dimension_along_path + gap_between
                segment_data['available_length'] -= (dimension_along_path + gap_between)
                print(f"    -> Placed '{ar_fxtr.name}' on segment {segment_data['id']}.")
                return True
            else:
                # --- Initial Placement Failed - Check for Wall Overlap ---
                print(f"      -> Initial spot blocked. Checking for wall overlap...")
                
                local_center = ar_fxtr.bounding_box.center
                transform = Matrix44.chain(
                    Matrix44.translate(-local_center.x, -local_center.y, 0),
                    Matrix44.z_rotate(math.radians(final_placement_angle_deg)),
                    Matrix44.translate(target_center.x, target_center.y, 0)
                )
                world_corners = list(transform.transform_vertices(ar_fxtr.bounding_box.rect_vertices()))
                failed_polygon = Polygon([(p.x, p.y) for p in world_corners])
                is_hitting_wall = False
                if not self.floorplan_polygon.buffer(-10.0).contains(failed_polygon):
                     boundary_zone = self.floorplan_polygon.buffer(10.0).difference(self.floorplan_polygon.buffer(-10.0))
                     overlap_area = failed_polygon.intersection(boundary_zone).area
                     if overlap_area > 1000.0:
                         is_hitting_wall = True
                         print(f"      -> Detected overlap with floorplan boundary (Area: {overlap_area:.0f} mm^2).")

                if is_hitting_wall:
                    # --- Attempt 1.5: Nudge Away from Wall ---
                    nudge_distance = 25.0
                    nudged_target_center = target_center + outward_normal * nudge_distance
                    print(f"      -> Nudging AR {nudge_distance}mm away from wall and retrying validation...")

                    nudged_bbox_tuple = self._validate_and_place_at_point_new_bench( 
                        doc, ar_fxtr, nudged_target_center, final_placement_angle_deg,
                        temp_obstacles_for_validation, 
                        outward_normal=outward_normal,
                        debug=False
                    )

                    if nudged_bbox_tuple:
                        # --- Success after nudging ---
                        gap_between = 0.0
                        segment_data['cursor'] += dimension_along_path + gap_between
                        segment_data['available_length'] -= (dimension_along_path + gap_between)
                        print(f"    -> Placed '{ar_fxtr.name}' after nudging away from wall.")
                        return True
                    else:
                        print(f"      -> Nudged spot also blocked.")
                
                # If we are here, it means Attempt 1 (and its nudge) failed for a reason
                # *other* than just wall overlap (e.g., blocked by a bench).
                # The loop will now continue to Attempt 2.
                print(f"    -> {config['name']} orientation failed at this spot.")
        
        # --- Both orientations failed at this cursor position ---
        print(f"    -> Both orientations failed for '{ar_fxtr.name}'. Nudging cursor.")
        nudge = 50.0 
        segment_data['cursor'] += nudge
        segment_data['available_length'] -= nudge
        return False

    
    
    def place_AR_fallback_on_bench_segments(self, doc, remaining_ar_queue: collections.deque):
        """
        [NEW FALLBACK v3] Force-places remaining ARs by anchoring them
        to the LEFT side of existing benches, using the "short-side parallel"
        (wide) orientation.
        
        *** WARNING: THIS FUNCTION PERFORMS NO VALIDATION. ***
        Fixtures will be placed regardless of overlaps or floor boundaries.
        """
        print("\n--- 🤖 Running Fallback AR Placement (FORCE-PLACE Anchor to Bench Left-Side) ---")

        if not remaining_ar_queue:
            print("  -> No remaining ARs in queue. Skipping fallback.")
            return

        total_to_place = len(remaining_ar_queue)
        placed_count = 0

        # --- 1. Get AR "Short-Side" Placement Dimensions ---
        try:
            ar_fxtr_template = Fixture.Fixture("AR", self.fixture_dict["AR"]["path"])
        except Exception as e:
            print(f"  -> ⚠️ FAILED: Could not load AR fixture template: {e}")
            return

        ar_width_native = ar_fxtr_template.width
        ar_height_native = ar_fxtr_template.height

        # Logic to get "Orientation 2" (short side parallel)
        dim_along_1 = ar_width_native
        dim_perp_1 = ar_height_native
        add_rot_1 = 0
        if ar_height_native > ar_width_native: # If TALL (like the AR)
            dim_along_1 = ar_height_native     # 1014
            dim_perp_1 = ar_width_native       # 530
            add_rot_1 = 90
        
        ar_placement_width = dim_perp_1    # 530 (short side along X-axis)
        ar_placement_depth = dim_along_1   # 1014 (long side along Y-axis)
        placement_rotation = (add_rot_1 + 90) % 180 # 180 degrees

        print(f"  -> Using short-side AR profile: {ar_placement_width:.0f}mm wide, {ar_placement_depth:.0f}mm deep. (Rotation: {placement_rotation}°)")

        # --- 2. Get All Benches and Obstacles ---
        bench_entities = [e for e in doc.msp.query('INSERT') if "BENCH" in e.dxf.name.upper()]
        if not bench_entities:
            print("  -> No benches found. Cannot run fallback placement.")
            return

        gap_from_bench = 10.0
        print(f"  -> Found {len(bench_entities)} benches to use as anchors...")

        # --- 3. Iterative Placement Loop (per-bench) ---
        for bench_entity in bench_entities:
            if not remaining_ar_queue:
                break # Stop if we've placed all ARs

            try:
                bench_bbox = extents([bench_entity])
                if not bench_bbox.has_data:
                    continue
            except Exception:
                continue
            
            print(f"\n  -> Anchoring to bench '{bench_entity.dxf.name}'...")

            # --- 4. Calculate Target Position ---
            bench_center_y = (bench_bbox.extmin.y + bench_bbox.extmax.y) / 2
            ar_target_center_y = bench_center_y
            ar_target_center_x = bench_bbox.extmin.x - gap_from_bench - (ar_placement_width / 2)
            
            target_center_vec = Vec2(ar_target_center_x, ar_target_center_y)
            
            ar_fxtr = remaining_ar_queue.popleft() # Take the next AR from the queue
            placed_count += 1

            # --- 5. FORCE-PLACE FIXTURE (NO VALIDATION) ---
            try:
                print(f"    -> ✅ FORCE-PLACING AR to the left of the bench.")
                
                # Calculate insertion point from target center
                local_center = ar_fxtr.bounding_box.center
                rotated_offset = local_center.rotate(math.radians(placement_rotation))
                final_insert_point = target_center_vec - rotated_offset

                # Place the fixture
                block_ref = doc.place_fixture(
                    ar_fxtr,
                    (final_insert_point.x, final_insert_point.y - 250, 0),
                    placement_rotation,
                    True # is_rotated
                )
                
                # Register its bounding box so it becomes an obstacle for future placements
                if block_ref:
                    bbox = extents([block_ref])
                    if bbox.has_data:
                        new_bbox_tuple = (bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y)
                        doc.placed_bboxes.append(new_bbox_tuple)
                
            except Exception as e:
                print(f"    -> ⚠️ Error during force-placement: {e}")
            
        print(f"\n--- ✅ Fallback AR Placement Complete ---")
        print(f"  -> Force-placed {placed_count} of {total_to_place} remaining ARs.")

#---------------AR------------NEW-----------------FALL_BACK----------SOLUTION------------
    def get_clinic_min_y(self, doc) -> Optional[float]:
        """
        [NEW HELPER] Finds the lowest Y-coordinate (min_y) among all
        placed clinic fixtures in the document.

        Args:
            doc (DXF_Document): The document to query.

        Returns:
            Optional[float]: The lowest Y-coordinate (extmin.y) found,
                             or None if no clinics are placed.
        """
        print(f"\n--- 🔎 Finding lowest Y-coordinate of all placed clinics (Doc {doc.ind}) ---")

        # 1. Query for all placed clinic entities
        clinic_entities = [
            e for e in doc.msp.query('INSERT')
            if "CLINIC" in e.dxf.name.upper()
        ]

        if not clinic_entities:
            print("  -> No clinic entities found.")
            return None

        # 2. Get the extents for each clinic
        all_extents = []
        for entity in clinic_entities:
            try:
                # Use virtual_entities() for accurate rotated bounds
                bbox = extents(list(entity.virtual_entities()))
                if bbox.has_data:
                    all_extents.append(bbox)
            except Exception as e:
                print(f"  -> ⚠️ Could not get extents for {entity.dxf.name}: {e}")
                continue
        
        if not all_extents:
            print("  -> Found clinic entities, but could not get valid extents.")
            return None

        # 3. Find the minimum 'extmin.y' value
        min_y = min(bbox.extmin.y for bbox in all_extents)
        
        print(f"  -> ✅ Lowest clinic Y-coordinate (min_y) found at: {min_y:.0f}")
        return min_y

    

    def get_wall_x_for_AR(self, doc, min_y: float) -> Optional[Tuple[float, float]]:
        """
        [NEW HELPER] Finds the left-most (left_x) and right-most (right_x)
        X-coordinates of the main floorplan polygon at a specific Y-level.

        Args:
            doc (DXF_Document): The document to query (unused, but for consistency).
            min_y (float): The Y-coordinate to slice the floorplan at.

        Returns:
            Optional[Tuple[float, float]]: A tuple of (left_x, right_x),
                                          or None if the boundaries cannot be found.
        """
        print(f"\n--- 📏 Finding floorplan X-boundaries at Y={min_y:.0f} ---")

        # 1. Check if the floorplan polygon exists
        if not hasattr(self, 'floorplan_polygon') or self.floorplan_polygon.is_empty:
            print("  -> ⚠️ FAILED: Floorplan polygon not found.")
            return None
            
        if not hasattr(self, 'cvc'):
             print("  -> ⚠️ FAILED: CV_Controller (cvc) not available for boundaries.")
             return None

        try:
            # 2. Create a horizontal "slicer" line across the whole floorplan
            slicer_line = LineString([
                (self.cvc.min_x - 100, min_y), 
                (self.cvc.max_x + 100, min_y)
            ])

            # 3. Find where this line intersects the floorplan
            intersection = self.floorplan_polygon.intersection(slicer_line)

            if intersection.is_empty:
                print(f"  -> ⚠️ FAILED: Slicer line at Y={min_y:.0f} does not intersect the floorplan.")
                return None

            # 4. Get the bounds of the resulting line(s)
            # The bounds will give the absolute min and max X of all intersections.
            min_x, _, max_x, _ = intersection.bounds
            
            left_x = min_x
            right_x = max_x

            print(f"  -> ✅ Success: Found boundaries at Y={min_y:.0f}:")
            print(f"    -> Left X: {left_x:.0f}")
            print(f"    -> Right X: {right_x:.0f}")
            
            return left_x, right_x

        except Exception as e:
            print(f"  -> ⚠️ FAILED during intersection or bounds calculation: {e}")
            return None


    def create_fallback_ar_segments_along_wall(self, doc, min_y: Optional[float], left_x: Optional[float], right_x: Optional[float], segment_length: float = 3000.0, debug: bool = False) -> List[dict]:
        """
        [MODIFIED v2 - ROBUST VALIDATION]
        Creates two 1-meter vertical segments for fallback AR placement.
        Now validates using INTERSECTION instead of midpoint containment.
        *** MODIFIED: RIGHT segment is now added FIRST, then LEFT ***
        """
        
        print("\n--- 🚧 Creating Fallback AR Placement Segments ---")
        
        fallback_segments = []

        # --- 1. Validate Inputs (unchanged) ---
        if min_y is None or left_x is None or right_x is None:
            print("  -> ⚠️ FAILED: Missing min_y, left_x, or right_x. Cannot create segments.")
            return fallback_segments
            
        if not hasattr(self, 'floorplan_polygon') or self.floorplan_polygon.is_empty:
            print("  -> ⚠️ FAILED: Floorplan polygon not found. Cannot validate segments.")
            return fallback_segments

        # --- Setup Debug Layer (unchanged) ---
        layer_name = "DEBUG_FALLBACK_AR_SEGMENTS"
        if debug:
            if layer_name not in doc.doc.layers:
                doc.doc.layers.add(name=layer_name, color=3)
            print(f"  -> Debug drawing is ON. Segments will be drawn on '{layer_name}'.")

        # *** MODIFICATION START: Process RIGHT segment FIRST ***
        
        # --- 2. RIGHT Segment (NOW PROCESSED FIRST) ---
        try:
            p1_right = Vec2(right_x, min_y)
            p2_right = Vec2(right_x, min_y - segment_length)
            
            segment_line_right = LineString([(p1_right.x, p1_right.y), (p2_right.x, p2_right.y)])
            
            if not self.floorplan_polygon.intersection(segment_line_right).is_empty:
                clipped_segment_right = self.floorplan_polygon.intersection(segment_line_right)
                
                if clipped_segment_right.length > 500:
                    print(f"  -> ✅ Created valid RIGHT fallback segment at X={right_x:.0f}")
                    
                    if debug:
                        doc.msp.add_line(
                            (p1_right.x, p1_right.y),
                            (p2_right.x, p2_right.y),
                            dxfattribs={"layer": layer_name, "color": 3}
                        )
                    
                    fallback_segments.append({
                        "id": "right_fallback",
                        "start": (p1_right.x, p1_right.y),
                        "end": (p2_right.x, p2_right.y),
                        "length": segment_length,
                        "angle": -90.0
                    })
                else:
                    print(f"  -> ℹ️ Right segment clipped too short ({clipped_segment_right.length:.0f}mm). Discarding.")
            else:
                print(f"  -> ℹ️ Right fallback segment at X={right_x:.0f} is completely outside the floorplan. Discarding.")
                
        except Exception as e:
            print(f"  -> ⚠️ Error processing right segment: {e}")

        # --- 3. LEFT Segment (NOW PROCESSED SECOND) ---
        try:
            p1_left = Vec2(left_x, min_y)
            p2_left = Vec2(left_x, min_y - segment_length)
            
            segment_line_left = LineString([(p1_left.x, p1_left.y), (p2_left.x, p2_left.y)])
            
            if not self.floorplan_polygon.intersection(segment_line_left).is_empty:
                clipped_segment_left = self.floorplan_polygon.intersection(segment_line_left)
                
                if clipped_segment_left.length > 500:
                    print(f"  -> ✅ Created valid LEFT fallback segment at X={left_x:.0f}")
                    
                    if debug:
                        doc.msp.add_line(
                            (p1_left.x, p1_left.y),
                            (p2_left.x, p2_left.y),
                            dxfattribs={"layer": layer_name, "color": 3}
                        )
                    
                    fallback_segments.append({
                        "id": "left_fallback",
                        "start": (p1_left.x, p1_left.y),
                        "end": (p2_left.x, p2_left.y),
                        "length": segment_length,
                        "angle": -90.0
                    })
                else:
                    print(f"  -> ℹ️ Left segment clipped too short ({clipped_segment_left.length:.0f}mm). Discarding.")
            else:
                print(f"  -> ℹ️ Left fallback segment at X={left_x:.0f} is completely outside the floorplan. Discarding.")

        except Exception as e:
            print(f"  -> ⚠️ Error processing left segment: {e}")

        # *** MODIFICATION END ***

        return fallback_segments
    
    
    def place_AR_fallback_on_segments(self, doc, remaining_ar_queue: collections.deque, fallback_segments: List[dict], debug: bool = False):
        """
        [NEW FALLBACK - V2 - ROBUST OBSTACLE REFRESH]
        Attempts to place remaining AR fixtures on the
        dynamically generated fallback segments (near clinics).
        Tries both 'long-side' and 'short-side' parallel orientations.
        
        *** FIX: Now refreshes obstacles BEFORE EVERY PLACEMENT ATTEMPT ***
        """
        print("\n--- 🤖 Running Final AR Fallback Placement (on generated segments) [V2] ---")

        if not remaining_ar_queue:
            print("  -> No remaining ARs in queue. Skipping fallback.")
            return

        if not fallback_segments:
            print("  -> No fallback segments were provided. Skipping.")
            return

        total_to_place = len(remaining_ar_queue)
        placed_count = 0

        # --- 1. Get AR Fixture Template (for dimensions) ---
        try:
            ar_fxtr_template = Fixture.Fixture("AR", self.fixture_dict["AR"]["path"])
        except Exception as e:
            print(f"  -> 🔥 FAILED: Could not load AR fixture template: {e}")
            return

        # --- 2. Define the two orientations to try ---
        ar_width_native = ar_fxtr_template.width
        ar_height_native = ar_fxtr_template.height

        dim_along_1 = ar_width_native
        dim_perp_1 = ar_height_native
        add_rot_1 = 0
        if ar_height_native > ar_width_native:
            dim_along_1 = ar_height_native
            dim_perp_1 = ar_width_native
            add_rot_1 = 90
        
        dim_along_2 = dim_perp_1
        dim_perp_2 = dim_along_1
        add_rot_2 = (add_rot_1 + 90) % 180

        orientations_to_try = [
            {"name": "Long side parallel", "dim_along": dim_along_1, "dim_perp": dim_perp_1, "add_rot": add_rot_1},
            {"name": "Short side parallel", "dim_along": dim_along_2, "dim_perp": dim_perp_2, "add_rot": add_rot_2},
        ]

        # *** REMOVED: The single obstacle refresh from here ***
        # We will now refresh obstacles INSIDE the placement loop

        # *** NEW: Add safety margin to prevent boundary violations ***
        SAFETY_MARGIN_FROM_WALL = 10.0  # 10mm safety buffer
        # *** END NEW ***

        # --- 4. Loop through each segment ---
        for segment_data in fallback_segments:
            if not remaining_ar_queue:
                break

            print(f"  -> Scanning fallback segment '{segment_data['id']}' (Length: {segment_data['length']:.0f}mm)...")

            try:
                p1 = Vec2(segment_data['start'])
                p2 = Vec2(segment_data['end'])
                seg_len = segment_data['length']
                base_segment_angle_deg = segment_data['angle']
                segment_vector = (p2 - p1).normalize()
            except Exception as e:
                print(f"    -> ⚠️ Invalid segment data: {e}. Skipping segment.")
                continue

            # --- 5. Determine "outward" normal ---
            outward_normal = None
            if segment_data['id'] == 'left_fallback':
                outward_normal = segment_vector.orthogonal(ccw=True).normalize()
            elif segment_data['id'] == 'right_fallback':
                outward_normal = segment_vector.orthogonal(ccw=False).normalize()
            
            if outward_normal is None:
                print("    -> ⚠️ Could not determine outward normal. Skipping segment.")
                continue
            
            # --- 6. Inner loop: Scan along this segment ---
            cursor = SAFETY_MARGIN_FROM_WALL
            nudge_amount = 100.0

            effective_seg_len = seg_len - (SAFETY_MARGIN_FROM_WALL * 2)

            while cursor + 50.0 < effective_seg_len:
                if not remaining_ar_queue:
                    break

                ar_fxtr = remaining_ar_queue[0]
                
                # *** THIS IS THE KEY FIX ***
                # Refresh obstacles RIGHT BEFORE each placement attempt
                print("      -> Refreshing obstacle list (includes ALL placed wall fixtures)...")
                self._get_accurate_obstacle_bboxes(include_all=True, debug=False)
                temp_obstacles = list(doc.placed_bboxes)
                print(f"      -> Current obstacle count: {len(temp_obstacles)}")
                # *** END OF FIX ***
                
                was_placed_at_this_spot = False
                for attempt, config in enumerate(orientations_to_try):
                    
                    dimension_along_path = config["dim_along"]
                    dimension_perpendicular = config["dim_perp"]
                    
                    if cursor + dimension_along_path > effective_seg_len:
                        continue

                    final_placement_angle_deg = (base_segment_angle_deg + config["add_rot"]) % 360

                    # Calculate target center
                    center_along_segment = p1 + segment_vector * (cursor + dimension_along_path / 2.0)
                    center_offset_outward = outward_normal * (dimension_perpendicular / 2.0 + SAFETY_MARGIN_FROM_WALL)
                    target_center = center_along_segment + center_offset_outward

                    # --- 8. Validate! (Now using the FRESHLY UPDATED obstacle list) ---
                    new_bbox_tuple = self._validate_and_place_at_point_new_bench_fallback( 
                        doc, ar_fxtr, target_center, final_placement_angle_deg,
                        temp_obstacles,  # <-- This list is now current
                        outward_normal=outward_normal,
                        debug=False
                    )

                    if new_bbox_tuple:
                        print(f"    -> ✅ Placed '{ar_fxtr.name}' on '{segment_data['id']}' ({config['name']}).")
                        ar_fxtr_placed = remaining_ar_queue.popleft()
                        placed_count += 1
                        
                        # *** IMPORTANT: Also update the temp list for the next iteration ***
                        temp_obstacles.append(new_bbox_tuple)
                        # Add to master list
                        if doc.placed_bboxes[-1] != new_bbox_tuple:
                            doc.placed_bboxes.append(new_bbox_tuple)

                        cursor += dimension_along_path
                        was_placed_at_this_spot = True
                        break 
                
                if not was_placed_at_this_spot:
                    cursor += nudge_amount
            
        # --- 9. Final Report ---
        print(f"\n--- ✅ Fallback AR Placement Complete ---")
        print(f"  -> Placed {placed_count} of {total_to_place} remaining ARs.")

    def _validate_and_place_at_point_new_bench_fallback(self, doc, fixture, target_center, angle_deg, placed_bboxes_for_check: list, outward_normal: Optional[Vec2] = None, debug=False):
        """
        [MODIFIED] Validates placement against partitions, floor boundary, and other fixtures.
        If the fixture is a BENCH or AR, it ALSO validates a 750mm outward aisle.
        If all checks pass, it places the fixture and registers BOTH the fixture
        and its aisle as new obstacles.
        Returns the new fixture bbox tuple on success, None on failure.
        [VISUAL DEBUG ADDED + 25mm INSET]
        
        [V2-UPDATE]: Now includes 'DEBUG_COMBINED_OBSTACLE_UNION' as a real obstacle.
        """

        # --- NEW: Augment obstacle list with DEBUG_COMBINED_OBSTACLE_UNION ---
        # Create a copy to avoid modifying the list passed in by reference
        augmented_obstacles = list(placed_bboxes_for_check)
        
        # Query for any entities on the debug layer
        debug_obstacle_entities = list(doc.msp.query(f'*[layer=="DEBUG_COMBINED_OBSTACLE_UNION"]'))
        if debug_obstacle_entities:
            # print("      -> Found DEBUG_COMBINED_OBSTACLE_UNION. Adding to obstacle list for this check.")
            for entity in debug_obstacle_entities:
                try:
                    # Calculate the bounding box of the debug shape
                    bbox = extents([entity])
                    if bbox.has_data:
                        augmented_obstacles.append((bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y))
                except Exception as e:
                    print(f"      -> Warning: could not get bbox for debug obstacle: {e}")
        # --- END OF NEW CODE ---

        # *******************************************************************
        # *************** THIS IS THE CHANGE YOU REQUESTED ***************
        # *******************************************************************
        # This call adds all clinic bboxes to the 'augmented_obstacles' list
        # for this validation check.
        # I've set visualize_debug=False to prevent it from re-drawing
        # the shapes every time, which would be very slow.
        # print("      -> Dynamically adding clinic bboxes to obstacle list for bench check...")
        self.register_individual_clinic_bboxes(doc, augmented_obstacles, inset_buffer_distance=-300, visualize_debug=False)
        # *******************************************************************
        # *******************************************************************


        # --- 1. Calculate fixture's proposed position and shape ---
        local_center = fixture.bounding_box.center
        transform = Matrix44.chain(
            Matrix44.translate(-local_center.x, -local_center.y, 0),
            Matrix44.z_rotate(math.radians(angle_deg)),
            Matrix44.translate(target_center.x, target_center.y, 0)
        )
        world_corners_vecs = [Vec2(v) for v in transform.transform_vertices(fixture.bounding_box.rect_vertices())]
        fixture_polygon = Polygon([(p.x, p.y) for p in world_corners_vecs])
        aabb = BoundingBox2d(world_corners_vecs)
        #--RASHEEQUEE-ADDED-THE-LINE-04/12/2025--
        fixture_bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)

        # --- 2. Internal Partition Check ---
        # internal_partitions_boh = self.cvc.get_internal_wall_partitions(min_length=600.0, max_length=2500.0, thickness=200.0)
        # OLD SLOW WAY: internal_partitions_boh = self.cvc.get_internal_wall_partitions(...)
        # NEW FAST WAY: Query the cached tree
        if doc.static_obstacle_tree:
            # Query the tree for objects that might intersect with the fixture
            candidate_indices = doc.static_obstacle_tree.query(fixture_polygon)
            
            # Check actual intersection only for candidates
            for idx in candidate_indices:
                obstacle = doc.static_obstacle_polygons[idx]
                if fixture_polygon.intersects(obstacle):
                    # print("      -> Blocked by static obstacle (Tree hit)")
                    return None
        # partition_polygons = []
        # for p in internal_partitions_boh or []:
        #     if isinstance(p, dict):
        #         bbox = p.get('bbox')
        #     else:
        #         bbox = p
        #     if bbox and hasattr(bbox, '__len__') and len(bbox) >= 4:
        #         try:
        #             minx, miny, maxx, maxy = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
        #             partition_polygons.append(box(minx, miny, maxx, maxy))
        #         except Exception:
        #            continue
        # is_overlapping_partition = False
        # for partition_poly in partition_polygons:
        #     if fixture_polygon.intersects(partition_poly):
        #         is_overlapping_partition = True
        #         # print("      -> Validation Failed: Fixture body overlaps internal BOH partition.")
        #         break 
        # if is_overlapping_partition:
        #     return None 

        # --- 3. Existing validation checks (floorplan and other fixtures) ---
        is_inside = self.floorplan_polygon.buffer(-1.0).contains(fixture_polygon)

        # 1. Fast Tree Check (Static Obstacles)
        if doc.static_obstacle_tree:
            # Query the tree for objects that might intersect with the fixture
            candidate_indices = doc.static_obstacle_tree.query(fixture_polygon)
            
            # Check actual intersection only for candidates
            for idx in candidate_indices:
                obstacle = doc.static_obstacle_polygons[idx]
                if fixture_polygon.intersects(obstacle):
                    # print("  -> Blocked by static obstacle (Tree hit)")
                    return None
        
        # ***MODIFICATION***: Use the new 'augmented_obstacles' list
        # [OPTIMIZATION] Use Raw Math Check instead of Object Creation
        #--RASHEEQUE-EDITED-THE-LINE-04/12/2025--
        is_overlapping_fixture = self._is_overlapping_raw(fixture_bbox_tuple, augmented_obstacles)
        # is_overlapping_fixture = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in augmented_obstacles)

        if is_inside and not is_overlapping_fixture:
            
            # --- 4. NEW AISLE VALIDATION ---
            aisle_box_poly = None
            if outward_normal and ("BENCH" in fixture.name.upper() or "AR" in fixture.name.upper()):
                AISLE_DEPTH = 750.0
                # print("      -> Validating 750mm walking aisle...")

                corners_with_projection = []
                for corner_vec in world_corners_vecs:
                    vec_from_center = corner_vec - target_center
                    projection = vec_from_center.dot(outward_normal)
                    corners_with_projection.append((projection, corner_vec))
                corners_with_projection.sort(key=lambda item: item[0], reverse=True)
                outward_corner_1 = corners_with_projection[0][1]
                outward_corner_2 = corners_with_projection[1][1]
                pushed_corner_1 = outward_corner_1 + outward_normal * AISLE_DEPTH
                pushed_corner_2 = outward_corner_2 + outward_normal * AISLE_DEPTH
                
                aisle_box_poly_raw = Polygon([
                    (outward_corner_1.x, outward_corner_1.y),
                    (outward_corner_2.x, outward_corner_2.y),
                    (pushed_corner_2.x, pushed_corner_2.y),
                    (pushed_corner_1.x, pushed_corner_1.y)
                ])

                aisle_box_poly = aisle_box_poly_raw.buffer(-25.0)
                # print("      -> Applied 25mm inset to aisle validation box.")

                # DEBUG: draw aisle validation polygon for visual inspection
                if debug:
                    try:
                        self.draw_debug_polygon(doc, aisle_box_poly, "DEBUG_AISLE_BOX", color=30, visible_by_default=True)
                    except Exception as e:
                        print(f"    -> Could not draw aisle debug polygon: {e}")
                
                #---RASHEEQUE--MODIFICATION---STARTS--08-11-2025---
                # is_overlapping_aisle = False
                
                # Check 1: Is the aisle fully inside the floorplan?
                if not self.floorplan_polygon.contains(aisle_box_poly):
                    # print("      -> Validation Failed: Proposed 750mm aisle (inset) goes outside the main floorplan walls.")
                    return None # Fail validation

                # Check 2: Does the aisle overlap other fixtures?
                is_overlapping_fixture_aisle = False
                for b in augmented_obstacles: 
                    if aisle_box_poly.intersects(box(*b)):
                        is_overlapping_fixture_aisle = True
                        # print("      -> Validation Failed: Proposed 750mm aisle (inset) overlaps an existing fixture or debug shape.")
                        break
                if is_overlapping_fixture_aisle:
                    return None
                
                # Check 3: Does the aisle overlap internal partitions?
                # is_overlapping_partition_aisle = False
                # for partition_poly in partition_polygons: 
                #     if aisle_box_poly.intersects(partition_poly):
                #         is_overlapping_partition_aisle = True
                #         # print("      -> Validation Failed: Proposed 750mm aisle (inset) overlaps an internal partition.")
                #         break
                # if is_overlapping_partition_aisle:
                #     return None

                #---RASHEEQUE--MODIFICATION---ENDS--08-11-2025---

            
            
            # --- 5. PLACEMENT (All checks passed) ---
            rotated_offset = local_center.rotate(math.radians(angle_deg))
            final_insert_point = target_center - rotated_offset
            # print("placed at angle:", angle_deg)
            doc.place_fixture(fixture, (final_insert_point.x, final_insert_point.y, 0), angle_deg, True)

            new_bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)
            doc.placed_bboxes.append(new_bbox_tuple)
            
            if aisle_box_poly and not aisle_box_poly.is_empty:
                aisle_bounds = aisle_box_poly.bounds
                doc.placed_bboxes.append(aisle_bounds)
                # print("      -> Successfully validated and registered 750mm aisle box (inset) as an obstacle.")

            return new_bbox_tuple
        
        else: # Original validation failed
            if not is_inside:
                print("      -> Validation Failed: Fixture body not fully inside floorplan.")
            if is_overlapping_fixture:
                print("      -> Validation Failed: Fixture body overlaps existing fixture or debug shape.")
            return None
    

#---------------AR------------NEW-----------------FALL_BACK----------SOLUTION------------

    # touched
    def _get_segment_proximity(self, segment_line: LineString, clinic_polygons_union: Polygon, boh_polygon: Polygon, threshold: float = 2000.0) -> str:
        """Determines if a segment is closer to clinics or the BOH zone."""
        if segment_line.is_empty:
            return 'other'

        centroid = segment_line.centroid
        dist_to_clinics = float('inf')
        dist_to_boh = float('inf')

        if clinic_polygons_union and not clinic_polygons_union.is_empty:
            dist_to_clinics = centroid.distance(clinic_polygons_union)

        if boh_polygon and not boh_polygon.is_empty:
            dist_to_boh = centroid.distance(boh_polygon)

        # print(f"  -> Segment centroid dist to Clinics: {dist_to_clinics:.0f}, dist to BOH: {dist_to_boh:.0f}") # Debug

        if dist_to_clinics <= threshold and dist_to_clinics < dist_to_boh:
            return 'clinic'
        elif dist_to_boh <= threshold and dist_to_boh < dist_to_clinics:
            return 'boh'
        elif dist_to_clinics <= threshold: # Close to clinics, even if BOH is closer (but maybe far)
             return 'clinic'
        elif dist_to_boh <= threshold: # Close to BOH
             return 'boh'
        else:
            return 'other'
        
    # touched
    def _place_bench_on_segment(self, doc, bench_fxtr: Fixture, segment_data: dict, temp_obstacles_for_validation: list, combined_shape: Polygon, gap_from_path: float = 0.0) -> bool:
        """
        Attempts to place a bench using validation. If blocked by a wall,
        nudges away by 50mm and retries. Updates the original_placed_bboxes list on success.
        [MODIFIED to pass outward_normal to validation]
        """
        # ... (setup code remains the same) ...
        try:
            segment_line = segment_data['line']
            start_point = Vec2(segment_line.coords[0])
            end_point = Vec2(segment_line.coords[-1])
            cursor = segment_data['cursor']
            available_length = segment_data['available_length']
            start_from_end = segment_data.get('start_from_end', False)
        except (KeyError, IndexError, TypeError) as e:
             print(f"    -> ERROR: Invalid segment_data: {e}")
             return False

        bench_width = bench_fxtr.width
        bench_height = bench_fxtr.height

        if bench_width > available_length:
            return False

        segment_vector = (end_point - start_point).normalize()
        segment_angle_deg = math.degrees(segment_vector.angle)
        
        # --- Calculate Outward Normal (remains the same) ---
        mid_point_vec = start_point.lerp(end_point)
        normal_cw = segment_vector.orthogonal(ccw=False).normalize()
        normal_ccw = segment_vector.orthogonal(ccw=True).normalize()
        point_cw = Point(mid_point_vec + normal_cw * 10.0)
        point_ccw = Point(mid_point_vec + normal_ccw * 10.0)
        if combined_shape and not combined_shape.is_empty and combined_shape.contains(point_ccw):
            outward_normal = normal_cw
        else:
            outward_normal = normal_ccw
        # --- End Normal Calculation ---

        # --- Calculate Initial Target Center (remains the same) ---

        height = self.cvc.max_y - self.cvc.min_y
        width = self.cvc.max_x - self.cvc.min_x
        dimension_difference = abs(height - width)
        
        if dimension_difference > 2000.0:
            if start_from_end:
                # center_along_segment = end_point - segment_vector * (cursor + bench_width / 2.0)
                # print_direction = "from end"
                center_along_segment = start_point + segment_vector * (cursor + bench_width / 2.0)
                print_direction = "from start"
                
            else:
                center_along_segment = start_point + segment_vector * (cursor + bench_width / 2.0)
                print_direction = "from start"
                
                # center_along_segment = end_point - segment_vector * (cursor + bench_width / 2.0)
                # print_direction = "from end"
        else:
            if start_from_end:
                center_along_segment = start_point + segment_vector * (cursor + bench_width / 2.0)
                print_direction = "from end"
            else:
                center_along_segment = end_point - segment_vector * (cursor + bench_width / 2.0)
                print_direction = "from end"


        center_offset_outward = outward_normal * (gap_from_path + bench_height / 2.0)
        target_center = center_along_segment + center_offset_outward

        print(f"    -> Trying placement for '{bench_fxtr.name}' on segment {segment_data['id']} ({print_direction})...")

        # --- Attempt 1: Validate and Place at Initial Position ---
        # *** MODIFIED CALL: Pass the outward_normal ***
        new_bbox_tuple = self._validate_and_place_at_point_new_bench(
            doc,
            bench_fxtr,
            target_center,
            segment_angle_deg,
            temp_obstacles_for_validation, # Check against temp list
            outward_normal=outward_normal,  # Pass the normal vector
            debug=False
        )

        if new_bbox_tuple:
            # --- Success on first try ---
            gap_between_benches = 0.0
            segment_data['cursor'] += bench_width + gap_between_benches
            segment_data['available_length'] -= (bench_width + gap_between_benches)
            print(f"    -> Placed '{bench_fxtr.name}' flush against segment {segment_data['id']} (Retail Side).")
            return True
        else:
            # --- Initial Placement Failed - Check for Wall Overlap ---
            print(f"    -> Initial spot blocked. Checking for wall overlap...")
            
            # ... (Wall overlap check logic remains the same) ...
            local_center = bench_fxtr.bounding_box.center
            transform = Matrix44.chain(
                Matrix44.translate(-local_center.x, -local_center.y, 0),
                Matrix44.z_rotate(math.radians(segment_angle_deg)),
                Matrix44.translate(target_center.x, target_center.y, 0)
            )
            world_corners = list(transform.transform_vertices(bench_fxtr.bounding_box.rect_vertices()))
            failed_polygon = Polygon([(p.x, p.y) for p in world_corners])
            WALL_OVERLAP_THRESHOLD_AREA = 1000.0 
            is_hitting_wall = False
            if not self.floorplan_polygon.buffer(-10.0).contains(failed_polygon):
                 boundary_zone = self.floorplan_polygon.buffer(10.0).difference(self.floorplan_polygon.buffer(-10.0))
                 overlap_area = failed_polygon.intersection(boundary_zone).area
                 if overlap_area > WALL_OVERLAP_THRESHOLD_AREA:
                     is_hitting_wall = True
                     print(f"    -> Detected overlap with floorplan boundary (Area: {overlap_area:.0f} mm^2).")

            if is_hitting_wall:
                # --- Attempt 2: Nudge Away from Wall and Re-validate ---
                nudge_distance = 50.0
                nudged_target_center = target_center + outward_normal * nudge_distance
                print(f"    -> Nudging bench 50mm away from wall and retrying validation...")

                # *** MODIFIED CALL: Pass the outward_normal again ***
                nudged_bbox_tuple = self._validate_and_place_at_point_new_bench(
                    doc,
                    bench_fxtr,
                    target_center,
                    segment_angle_deg,
                    temp_obstacles_for_validation, # Check against temp list
                    outward_normal=outward_normal,  # Pass the normal vector
                    debug=False
                )



                if nudged_bbox_tuple:
                    # --- Success after nudging ---
                    gap_between_benches = 0.0
                    segment_data['cursor'] += bench_width + gap_between_benches
                    segment_data['available_length'] -= (bench_width + gap_between_benches)
                    print(f"    -> Placed '{bench_fxtr.name}' after nudging away from wall.")
                    return True
                else:
                    print(f"    -> Nudged spot also blocked.")
            
            # --- Standard Failure Logic ---
            print(f"    -> Spot for '{bench_fxtr.name}' blocked by another fixture or invalid.")
            nudge = 100.0 
            segment_data['cursor'] += nudge
            segment_data['available_length'] -= nudge
            return False
  
        
    # touched
    def _validate_and_place_at_point_new_bench(self, doc, fixture, target_center, angle_deg, placed_bboxes_for_check: list, outward_normal: Optional[Vec2] = None, debug=False):
        """
        [MODIFIED] Validates placement against partitions, floor boundary, and other fixtures.
        If the fixture is a BENCH or AR, it ALSO validates a 750mm outward aisle.
        If all checks pass, it places the fixture and registers BOTH the fixture
        and its aisle as new obstacles.
        Returns the new fixture bbox tuple on success, None on failure.
        [VISUAL DEBUG ADDED + 25mm INSET]
        
        [V2-UPDATE]: Now includes 'DEBUG_COMBINED_OBSTACLE_UNION' as a real obstacle.
        """

        # --- NEW: Augment obstacle list with DEBUG_COMBINED_OBSTACLE_UNION ---
        # Create a copy to avoid modifying the list passed in by reference
        augmented_obstacles = list(placed_bboxes_for_check)
        
        # Query for any entities on the debug layer
        debug_obstacle_entities = list(doc.msp.query(f'*[layer=="DEBUG_COMBINED_OBSTACLE_UNION"]'))
        if debug_obstacle_entities:
            # print("      -> Found DEBUG_COMBINED_OBSTACLE_UNION. Adding to obstacle list for this check.")
            for entity in debug_obstacle_entities:
                try:
                    # Calculate the bounding box of the debug shape
                    bbox = extents([entity])
                    if bbox.has_data:
                        augmented_obstacles.append((bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y))
                except Exception as e:
                    print(f"      -> Warning: could not get bbox for debug obstacle: {e}")
        # --- END OF NEW CODE ---

        # *******************************************************************
        # *************** THIS IS THE CHANGE YOU REQUESTED ***************
        # *******************************************************************
        # This call adds all clinic bboxes to the 'augmented_obstacles' list
        # for this validation check.
        # I've set visualize_debug=False to prevent it from re-drawing
        # the shapes every time, which would be very slow.
        # print("      -> Dynamically adding clinic bboxes to obstacle list for bench check...")
        self.register_individual_clinic_bboxes(doc, augmented_obstacles, inset_buffer_distance=-300, visualize_debug=False)
        # *******************************************************************
        # *******************************************************************


        # --- 1. Calculate fixture's proposed position and shape ---
        local_center = fixture.bounding_box.center
        transform = Matrix44.chain(
            Matrix44.translate(-local_center.x, -local_center.y, 0),
            Matrix44.z_rotate(math.radians(angle_deg)),
            Matrix44.translate(target_center.x, target_center.y, 0)
        )
        world_corners_vecs = [Vec2(v) for v in transform.transform_vertices(fixture.bounding_box.rect_vertices())]
        fixture_polygon = Polygon([(p.x, p.y) for p in world_corners_vecs])
        aabb = BoundingBox2d(world_corners_vecs)

        # # --- 2. Internal Partition Check ---
        # internal_partitions_boh = self.cvc.get_internal_wall_partitions(min_length=600.0, max_length=2500.0, thickness=200.0)
        # partition_polygons = []
        # for p in internal_partitions_boh or []:
        #     if isinstance(p, dict):
        #         bbox = p.get('bbox')
        #     else:
        #         bbox = p
        #     if bbox and hasattr(bbox, '__len__') and len(bbox) >= 4:
        #         try:
        #             minx, miny, maxx, maxy = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
        #             partition_polygons.append(box(minx, miny, maxx, maxy))
        #         except Exception:
        #            continue
        # is_overlapping_partition = False
        # for partition_poly in partition_polygons:
        #     if fixture_polygon.intersects(partition_poly):
        #         is_overlapping_partition = True
        #         # print("      -> Validation Failed: Fixture body overlaps internal BOH partition.")
        #         break 
        # if is_overlapping_partition:
        #     return None 
        # --- 2. Internal Partition Check (OPTIMIZED TREE QUERY) ---
        # Instead of recalculating partitions every time, we query the static tree.
        if doc.static_obstacle_tree:
            # Query the tree for objects that might intersect
            candidate_indices = doc.static_obstacle_tree.query(fixture_polygon)
            
            # Check actual intersection only for candidates
            for idx in candidate_indices:
                obstacle = doc.static_obstacle_polygons[idx]
                if fixture_polygon.intersects(obstacle):
                    # print("      -> Blocked by internal partition (Tree hit)")
                    return None

        # --- 3. Existing validation checks (floorplan and other fixtures) ---
        is_inside = self.floorplan_polygon.buffer(-1.0).contains(fixture_polygon)
        
        # ***MODIFICATION***: Use the new 'augmented_obstacles' list
        is_overlapping_fixture = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in augmented_obstacles)

        if is_inside and not is_overlapping_fixture:
            
            # --- 4. NEW AISLE VALIDATION ---
            aisle_box_poly = None
            if outward_normal and ("BENCH" in fixture.name.upper() or "AR" in fixture.name.upper()):
                AISLE_DEPTH = 750.0
                # print("      -> Validating 750mm walking aisle...")

                corners_with_projection = []
                for corner_vec in world_corners_vecs:
                    vec_from_center = corner_vec - target_center
                    projection = vec_from_center.dot(outward_normal)
                    corners_with_projection.append((projection, corner_vec))
                corners_with_projection.sort(key=lambda item: item[0], reverse=True)
                outward_corner_1 = corners_with_projection[0][1]
                outward_corner_2 = corners_with_projection[1][1]
                pushed_corner_1 = outward_corner_1 + outward_normal * AISLE_DEPTH
                pushed_corner_2 = outward_corner_2 + outward_normal * AISLE_DEPTH
                
                aisle_box_poly_raw = Polygon([
                    (outward_corner_1.x, outward_corner_1.y),
                    (outward_corner_2.x, outward_corner_2.y),
                    (pushed_corner_2.x, pushed_corner_2.y),
                    (pushed_corner_1.x, pushed_corner_1.y)
                ])

                aisle_box_poly = aisle_box_poly_raw.buffer(-25.0)
                # print("      -> Applied 25mm inset to aisle validation box.")

                # DEBUG: draw aisle validation polygon for visual inspection
                if debug:
                    try:
                        self.draw_debug_polygon(doc, aisle_box_poly, "DEBUG_AISLE_BOX", color=30, visible_by_default=True)
                    except Exception as e:
                        print(f"    -> Could not draw aisle debug polygon: {e}")
                
                #---RASHEEQUE--MODIFICATION---STARTS--08-11-2025---
                # is_overlapping_aisle = False
                
                # # ***MODIFICATION***: Use the new 'augmented_obstacles' list
                # for b in augmented_obstacles: 
                #     if aisle_box_poly.intersects(box(*b)):
                #         is_overlapping_aisle = True
                #         print("      -> Validation Failed: Proposed 750mm aisle (inset) overlaps an existing fixture or debug shape.")
                #         break
                # if not is_overlapping_aisle:
                #     for partition_poly in partition_polygons: 
                #         if aisle_box_poly.intersects(partition_poly):
                #             is_overlapping_aisle = True
                #             print("      -> Validation Failed: Proposed 750mm aisle (inset) overlaps an internal partition.")
                #             break
                # if is_overlapping_aisle:
                #     return None 
                # Check 1: Is the aisle fully inside the floorplan?
                if not self.floorplan_polygon.contains(aisle_box_poly):
                    # print("      -> Validation Failed: Proposed 750mm aisle (inset) goes outside the main floorplan walls.")
                    return None # Fail validation

                # Check 2: Does the aisle overlap other fixtures?
                is_overlapping_fixture_aisle = False
                for b in augmented_obstacles: 
                    if aisle_box_poly.intersects(box(*b)):
                        is_overlapping_fixture_aisle = True
                        # print("      -> Validation Failed: Proposed 750mm aisle (inset) overlaps an existing fixture or debug shape.")
                        break
                if is_overlapping_fixture_aisle:
                    return None
                
                # Check 3: Does the aisle overlap internal partitions?
                # is_overlapping_partition_aisle = False
                # for partition_poly in partition_polygons: 
                #     if aisle_box_poly.intersects(partition_poly):
                #         is_overlapping_partition_aisle = True
                #         # print("      -> Validation Failed: Proposed 750mm aisle (inset) overlaps an internal partition.")
                #         break
                # if is_overlapping_partition_aisle:
                #     return None
                

                #---RASHEEQUE--MODIFICATION---ENDS--08-11-2025---

            
            
            # --- 5. PLACEMENT (All checks passed) ---
            rotated_offset = local_center.rotate(math.radians(angle_deg))
            final_insert_point = target_center - rotated_offset
            # print("placed at angle:", angle_deg)
            doc.place_fixture(fixture, (final_insert_point.x, final_insert_point.y, 0), angle_deg, True)

            new_bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)
            doc.placed_bboxes.append(new_bbox_tuple)
            
            if aisle_box_poly and not aisle_box_poly.is_empty:
                aisle_bounds = aisle_box_poly.bounds
                doc.placed_bboxes.append(aisle_bounds)
                # print("      -> Successfully validated and registered 750mm aisle box (inset) as an obstacle.")

            return new_bbox_tuple
        
        else: # Original validation failed
            if not is_inside:
                print("      -> Validation Failed: Fixture body not fully inside floorplan.")
            if is_overlapping_fixture:
                print("      -> Validation Failed: Fixture body overlaps existing fixture or debug shape.")
            return None
    
    # touched
    def register_individual_clinic_bboxes(self, doc, placed_bboxes=None, inset_buffer_distance=-300.0, visualize_debug: bool = False) -> None:
        """
        Calculates the individual bounding box for EVERY placed clinic fixture,
        applies a -300mm inset, and registers that *smaller* box as the obstacle.

        If visualize_debug is True, it draws the same inset polygon.

        Args:
            placed_bboxes (list): The master list of placed bounding boxes.
                                  This list will be modified in-place.
            visualize_debug (bool): If True, draws the inset polygons
                                    on unique, colored layers.
        """

        print("\n--- 🏥 Registering INDIVIDUAL Clinic BBoxes (Actual -300mm Inset) ---")

        # 1. Get the list of individual, rotated clinic polygons
        clinic_polygons = self._get_all_clinic_polygons(doc)

        if not clinic_polygons:
            print("  -> No clinic polygons found. Nothing to register.")
            return

        # 2. Define colors for visualization
        debug_colors = [1, 2, 3, 4, 5, 6] # ACI: R, Y, G, C, B, M
        
        new_bboxes_found = []
        visual_polys_drawn = 0

        # 3. Process each clinic polygon individually
        for i, clinic_poly in enumerate(clinic_polygons):
            if clinic_poly.is_empty:
                continue

            # --- THIS IS THE KEY CHANGE ---
            # 4. Apply the -300mm buffer *before* calculating the bounding box.
            # inset_buffer_distance = 0.0
            inset_poly = clinic_poly.buffer(inset_buffer_distance)
            
            # 5. If the inset polygon is valid, use it to get the bounding box
            if not inset_poly.is_empty:
                # Get the bbox *from the smaller inset polygon*
                min_x, min_y, max_x, max_y = inset_poly.bounds 
                bbox_tuple = (min_x, min_y, max_x, max_y)
                new_bboxes_found.append(bbox_tuple)
                
                # 6. (Optional) Draw the *INSET* shape
                if visualize_debug:
                    layer_name = f"DEBUG_CLINIC_{i+1}_INSET"
                    color = debug_colors[i % len(debug_colors)] 
                    
                    if layer_name not in doc.doc.layers:
                        doc.doc.layers.add(name=layer_name, color=color) 
                    
                    # Get coordinates from the same inset polygon
                    points = list(inset_poly.exterior.coords)
                    
                    doc.msp.add_lwpolyline(
                        points, 
                        close=True, 
                        dxfattribs={"layer": layer_name, "lineweight": 35}
                    )
                    visual_polys_drawn += 1
            else:
                print(f"  -> Note: Clinic {i+1} was too small for a -300mm inset. Skipping registration.")

        # 7. Add the new *inset bounding boxes* to the master list
        if new_bboxes_found:
            if placed_bboxes:
                placed_bboxes.extend(new_bboxes_found)
            else:
                doc.placed_bboxes.extend(new_bboxes_found)
            print(f"  -> Registered {len(new_bboxes_found)} *inset* clinic bboxes as obstacles.")
            # print(f"bbox generated", new_bboxes_found)
            if visualize_debug:
                print(f"  -> Drew {visual_polys_drawn} unique colored inset shapes.")

    #-----RASHEEQUE--MODIFIED--VERSION----------------10-16-2025-----#
    def euro_center_placement_area(self, doc) -> Optional[Polygon]:
        """
        [MODIFIED v3] Calculates the Euro Center placement zone.
        - The "top" boundary is now a combination of two rules:
          1. A hard "ceiling" is set at the absolute TOP (max_y) of the
             entire standing table cluster.
          2. The *individual* bounding boxes of all standing tables,
             each with an 800mm "keep-out" buffer, are subtracted.
        - This creates the "natural line" gap from the user's diagram
          AND prevents placement in any space *above* the standing tables.
        """

        print("\n--- 📐 Defining Euro Center zone (Hybrid 'Natural' + 'Ceiling' Boundary) ---")

        # --- 1. Inset the full floorplan polygon (Unchanged) ---
        simplification_tolerance = 50.0
        simplified_floorplan_polygon = self.floorplan_polygon.simplify(simplification_tolerance, preserve_topology=True)

        wall_fixture_depth = 300.0
        shopping_aisle_gap = 1050.0
        total_side_gap = wall_fixture_depth + shopping_aisle_gap
        
        inset_polygon = simplified_floorplan_polygon.buffer(-total_side_gap, join_style=1)
        if inset_polygon.is_empty:
            print("  -> ⚠️ FAILED: Floorplan is too narrow for side insets.")
            return None
        print(f"  -> Inset the full floorplan polygon by {total_side_gap:.0f}mm from all walls.")

        # --- 2. Define and Apply Differentiated Bottom Boundary (Unchanged) ---
        # (This logic correctly defines the bottom/facade keep-out zones)
        
        facade_margin_V1 = self._calculate_dynamic_qms_margin()
        facade_margin = facade_margin_V1 + 510 
        normal_bottom_margin = 1350.0
        
        def find_bottom_segments(corners, slope_tol=0.1, y_band_height=500.0):
            min_y_overall = min(c[1] for c in corners)
            bottom_segments = []
            for i in range(len(corners)):
                p1 = corners[i]
                p2 = corners[(i + 1) % len(corners)]
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
            
        facade_y_threshold = min(c[1] for c in self.cvc.corners) + 100
        bottom_keep_out_zones = []
        for p1, p2 in bottom_segments:
            segment_line = LineString([p1, p2])
            avg_y = (p1[1] + p2[1]) / 2
            
            if avg_y < facade_y_threshold:
                keep_out_poly = segment_line.buffer(facade_margin, single_sided=True)
                if not self.floorplan_polygon.contains(keep_out_poly.centroid):
                    keep_out_poly = segment_line.buffer(-facade_margin, single_sided=True)
                bottom_keep_out_zones.append(keep_out_poly)
                print(f"  -> Identified FACADE segment, applying {facade_margin}mm keep-out zone.")
            else:
                keep_out_poly = segment_line.buffer(normal_bottom_margin, single_sided=True)
                if not self.floorplan_polygon.contains(keep_out_poly.centroid):
                    keep_out_poly = segment_line.buffer(-normal_bottom_margin, single_sided=True)
                bottom_keep_out_zones.append(keep_out_poly)
                print(f"  -> Identified NORMAL bottom segment, applying {normal_bottom_margin}mm keep-out zone.")

        if bottom_keep_out_zones:
            combined_bottom_keep_out = unary_union(bottom_keep_out_zones)
            zone_after_bottom_inset = inset_polygon.difference(combined_bottom_keep_out)
        else:
            zone_after_bottom_inset = inset_polygon

        if zone_after_bottom_inset.is_empty:
            print("  -> ⚠️ Zone is empty after applying bottom keep-out zones.")
            return None

        # --- 3. NEW: Apply the "Hard Ceiling" (Top Slicer) ---
        st_entities = [e for e in doc.msp.query('INSERT') if "STANDING_TABLE" in e.dxf.name.upper()]
        if not st_entities:
            print("  -> ⚠️ FAILED: No Standing Tables found. Cannot create zone.")
            return None

        st_bbox = extents(st_entities)
        # This is the absolute highest point of the standing table cluster
        top_slicer_y = st_bbox.extmax.y - 800
        
        print(f"  -> Applying hard 'ceiling' at Y={top_slicer_y:.0f} (top of standing tables).")
        
        # Create a slicer box that cuts off *everything* above this Y-coordinate
        top_slicer_box = box(
            self.cvc.min_x - 1000, self.cvc.min_y - 1000, 
            self.cvc.max_x + 1000, top_slicer_y
        )
        
        # Apply the slice
        zone_after_top_slice = zone_after_bottom_inset.intersection(top_slicer_box)

        if zone_after_top_slice.is_empty:
            print("  -> ⚠️ Zone is empty after applying the 'ceiling' slice.")
            return None

        # --- 4. NEW: Subtract ALL Obstacles with Buffers ---
        print("  -> Subtracting all obstacles with dynamic buffers...")

        # Get entities for all obstacles
        qms_entities = [e for e in doc.msp.query('INSERT') if "QMS_DESK" in e.dxf.name.upper()]
        
        # Get all *other* obstacles from the pre-calculated list
        st_bboxes_tuples = [(b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y) for e in st_entities if (b := extents([e]))]
        qms_bboxes_tuples = [(b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y) for e in qms_entities if (b := extents([e]))]
        zone_defining_bboxes = set(st_bboxes_tuples + qms_bboxes_tuples)
        other_obstacles_bboxes = [b for b in doc.placed_bboxes if b not in zone_defining_bboxes]

        obstacle_polygons_to_subtract = []

        # A) Add Standing Tables with their 800mm gap
        for entity in st_entities:
            try:
                # Get the *precise* rotated polygon for the table
                # corners = self.get_outer_rect_corners_shapely(entity)
                # if len(corners) < 4: continue
                # poly = Polygon([(c[0], c[1]) for c in corners])
                # # Buffer this precise polygon by the 800mm gap
                # obstacle_polygons_to_subtract.append(poly.buffer(800.0, join_style=2))
                # [NEW FAST WAY] - Use Bounding Box
                # This avoids complex polygon math and is much faster
                bbox = extents([entity])
                if bbox.has_data:
                    # Create a simple box and buffer that
                    simple_box = box(bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y)
                    obstacle_polygons_to_subtract.append(simple_box.buffer(800.0, join_style=2))
            except Exception as e:
                print(f"    -> Warning: Could not get precise shape for {entity.dxf.name}. Using bbox. {e}")
                bbox = extents([entity])
                if bbox.has_data:
                    obstacle_polygons_to_subtract.append(box(bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y).buffer(800.0, join_style=2))

        # B) Add other obstacles (BOH, clinics, etc.) with a small 1mm buffer
        for bbox_tuple in other_obstacles_bboxes:
            obstacle_polygons_to_subtract.append(box(*bbox_tuple).buffer(1.0, join_style=2))
        
        # C) Add internal partitions
        internal_partitions = self.cvc.get_internal_wall_partitions(50, 670, 0)
        if internal_partitions:
            for bbox_tuple in internal_partitions:
                obstacle_polygons_to_subtract.append(box(*bbox_tuple))
        
        print(f"  -> Subtracting {len(obstacle_polygons_to_subtract)} total obstacle zones...")

        # --- 5. Final Subtraction ---
        if obstacle_polygons_to_subtract:
            all_obstacles_union = unary_union(obstacle_polygons_to_subtract)
            # We subtract from the "zone_after_top_slice"
            final_zone = zone_after_top_slice.difference(all_obstacles_union)
        else:
            final_zone = zone_after_top_slice

        if final_zone.is_empty:
            print("  -> ⚠️ Final zone is empty after subtracting all obstacles.")
            return None

        # --- 6. Clean up small fragments ---
        if final_zone.geom_type == 'MultiPolygon':
            print("  -> Zone is fragmented. Selecting the largest valid area.")
            # Select the largest polygon piece from the fragments
            min_area_threshold = 500000 # 0.5 sq m
            valid_pieces = [p for p in final_zone.geoms if p.area > min_area_threshold]
            if not valid_pieces:
                print("  -> ⚠️ All zone fragments are too small to be usable.")
                return None
            final_zone = max(valid_pieces, key=lambda p: p.area)
        
        zone_bounds = final_zone.bounds
        zone_width = zone_bounds[2] - zone_bounds[0]
        zone_height = zone_bounds[3] - zone_bounds[1]
        print(f"  -> ✅ Successfully defined final 'natural' + 'ceiling' zone (W: {zone_width:.0f}mm x H: {zone_height:.0f}mm)")
        return final_zone

    
    
    # touched
    def draw_euro_center_placement_zone(self, doc):
        """
        Calls the main logic function to get the Euro Center zone and then
        draws its boundary on the DXF for visual validation.
        """
        print("\n--- 🎨 Drawing Euro Center Placement Zone for Validation ---")

        # MODIFIED: This now calls the corrected, stable function
        placement_zone_poly = doc.euro_zone

        # Check if the zone was successfully calculated
        if placement_zone_poly and not placement_zone_poly.is_empty:
            
            # Get the area from the polygon object and print it.
            area_in_sq_mm = placement_zone_poly.area
            print(f"  -> 📏 Calculated Area of the Zone: {area_in_sq_mm:,.2f} mm^2")
            
            # Define a new layer for the debug drawing
            layer_name = "DEBUG_PLACEMENT_ZONE"
            if layer_name not in doc.doc.layers:
                doc.doc.layers.add(
                    name=layer_name,
                    color=6  # ACI color 6 is Magenta, which is highly visible
                )

            # Get the coordinates of the polygon's boundary
            zone_boundary_coords = list(placement_zone_poly.exterior.coords)

            # Add the polygon outline to the modelspace
            doc.msp.add_lwpolyline(
                zone_boundary_coords,
                close=True,
                dxfattribs={"layer": layer_name, "lineweight": 35} # Make the line slightly thicker
            )
            
            print(f"  -> ✅ Zone boundary drawn on layer '{layer_name}' for validation.")
        
        else:
            print("  -> ⚠️ SKIPPED DRAWING: The placement zone could not be calculated.")
            
    #--RASHEEQUE--ADDED--THE--FUNCTION---10/11
    def _get_floorplan_main_angle(self) -> float:
        """
        Finds the angle of the longest wall segment of the main floorplan
        to be used as the base_angle for grid alignment.
        """
        print("  -> Finding floorplan main angle...")
        try:
            # Use the existing CV_Controller's wall data
            all_segments = self.cvc.get_wall_segments(min_length=100)
            if not all_segments:
                print("    -> No wall segments found, defaulting to 0 degrees.")
                return 0.0

            # Find the longest segment
            longest_segment = max(all_segments, key=lambda seg: Vec2(seg[0]).distance(Vec2(seg[1])))
            
            p1 = Vec2(longest_segment[0])
            p2 = Vec2(longest_segment[1])
            
            # Ensure vector is "positive" (mostly pointing right or up)
            if p1.x > p2.x:
                p1, p2 = p2, p1
            
            wall_vector = (p2 - p1)
            base_angle = wall_vector.angle # Angle in radians
            
            print(f"    -> Longest wall found. Base angle set to: {math.degrees(base_angle):.2f} degrees.")
            return base_angle # Return in radians for math functions

        except Exception as e:
            print(f"    -> ⚠️ ERROR in _get_floorplan_main_angle: {e}. Defaulting to 0.")
            return 0.0

    
    # touched
    #--RASHEEQUE EDITED--THIS--FUNCTION--02/12
    def generate_row_wise_grid(self, doc) -> List[Tuple[float, float]]:
        """
        [OPTIMIZED v3] Calculates grid for 0° rotation.
        Uses STRtree for efficient collision detection instead of Unary Union.
        """
        print("\n--- MATRIX Generating ROW-WISE grid (0° Rotation) [Optimized] ---")
        zone = doc.euro_zone
        if not zone or zone.is_empty:
            return []

        # --- Setup Obstacles ---
        all_obstacle_bboxes = doc.placed_bboxes
        separator_line = doc.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
        if separator_line:
            start_pt, end_pt = separator_line.dxf.start, separator_line.dxf.end
            separator_bbox = (min(start_pt.x, end_pt.x), min(start_pt.y, end_pt.y) - 1, max(start_pt.x, end_pt.x), max(start_pt.y, end_pt.y) + 1)
            all_obstacle_bboxes = [b for b in doc.placed_bboxes if b != separator_bbox]

        partition_bboxes = self.cvc.get_internal_wall_partitions(min_length=50, max_length=670.0, thickness=0.0)
        
        # Convert to polygons
        obstacle_polygons = [box(*b) for b in all_obstacle_bboxes]
        partition_polygons = [box(*b) for b in partition_bboxes]
        
        # Combine lists for the tree
        fixed_obstacles_for_aisle_check = obstacle_polygons + partition_polygons
        
        # --- THE OPTIMIZATION: Build Spatial Index ---
        # Instead of unary_union (slow), we use a tree
        tree = STRtree(fixed_obstacles_for_aisle_check) if fixed_obstacles_for_aisle_check else None

        # --- Grid Parameters ---
        cell_width = 1040.0
        cell_height = 1175.0
        aisle_width = 1050.0
        min_containment_ratio = 0.90 
        max_aisle_blockage_ratio = 0.01

        final_grid_points = []
        min_x_zone, min_y_zone, max_x_zone, max_y_zone = zone.bounds

        current_y = min_y_zone
        while current_y + cell_height <= max_y_zone:
            current_x = min_x_zone
            while current_x + cell_width <= max_x_zone:
                cell_box = box(current_x, current_y, current_x + cell_width, current_y + cell_height)
                
                # --- Rule 1: Containment ---
                intersection_area = zone.intersection(cell_box).area
                if (intersection_area / cell_box.area) < min_containment_ratio:
                    current_x += cell_width
                    continue

                # --- Rule 2: Partition Overlap (Fast Check) ---
                hits_partition = False
                for pp in partition_polygons:
                    if cell_box.intersects(pp):
                        hits_partition = True
                        break
                if hits_partition:
                    current_x += cell_width
                    continue

                # --- Rule 3: Aisle Clearance (Optimized) ---
                top_aisle = box(current_x, current_y + cell_height, current_x + cell_width, current_y + cell_height + aisle_width)
                bottom_aisle = box(current_x, current_y - aisle_width, current_x + cell_width, current_y)
                aisles_valid = True

                for aisle_box in [top_aisle, bottom_aisle]:
                    if not tree: break # No obstacles, valid
                    
                    overlap_area = 0.0
                    # Fast Query: Get only nearby obstacles
                    indices = tree.query(aisle_box)
                    
                    for i in indices:
                        obstacle = fixed_obstacles_for_aisle_check[i]
                        if aisle_box.intersects(obstacle):
                            overlap_area += aisle_box.intersection(obstacle).area
                    
                    if (overlap_area / aisle_box.area) > max_aisle_blockage_ratio:
                        aisles_valid = False
                        break

                if aisles_valid:
                    final_grid_points.append((current_x, current_y))
                
                current_x += cell_width
            current_y += cell_height

        print(f"  -> ✅ Generated {len(final_grid_points)} spots.")
        return final_grid_points
    
    
    # touched
    

    #--RASHEEQUE EDITED--THIS--FUNCTION--02/12
    def generate_column_wise_grid(self, doc) -> List[Tuple[float, float]]:
        """
        [OPTIMIZED v3] Calculates grid for 90° rotation.
        Uses STRtree for efficient collision detection.
        """
        print("\n--- MATRIX Generating COLUMN-WISE grid (90° Rotation) [Optimized] ---")
        zone = doc.euro_zone
        if not zone or zone.is_empty:
            return []

        # --- Setup Obstacles ---
        all_obstacle_bboxes = doc.placed_bboxes
        separator_line = doc.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
        if separator_line:
            start_pt, end_pt = separator_line.dxf.start, separator_line.dxf.end
            separator_bbox = (min(start_pt.x, end_pt.x), min(start_pt.y, end_pt.y) - 1, max(start_pt.x, end_pt.x), max(start_pt.y, end_pt.y) + 1)
            all_obstacle_bboxes = [b for b in doc.placed_bboxes if b != separator_bbox]

        partition_bboxes = self.cvc.get_internal_wall_partitions(min_length=50, max_length=670.0, thickness=0.0)
        
        obstacle_polygons = [box(*b) for b in all_obstacle_bboxes]
        partition_polygons = [box(*b) for b in partition_bboxes]
        fixed_obstacles_for_aisle_check = obstacle_polygons + partition_polygons
        
        # --- THE OPTIMIZATION: Build Spatial Index ---
        tree = STRtree(fixed_obstacles_for_aisle_check) if fixed_obstacles_for_aisle_check else None

        # --- Grid Parameters ---
        cell_width = 1175.0
        cell_height = 1040.0
        aisle_width = 1050.0
        min_containment_ratio = 0.90 
        max_aisle_blockage_ratio = 0.10 

        final_grid_points = []
        min_x_zone, min_y_zone, max_x_zone, max_y_zone = zone.bounds

        current_y = min_y_zone
        while current_y + cell_height <= max_y_zone:
            current_x = min_x_zone
            while current_x + cell_width <= max_x_zone:
                cell_box = box(current_x, current_y, current_x + cell_width, current_y + cell_height)
                
                # --- Rule 1: Containment ---
                intersection_area = zone.intersection(cell_box).area
                if (intersection_area / cell_box.area) < min_containment_ratio:
                    current_x += cell_width
                    continue

                # --- Rule 2: Partition Overlap ---
                hits_partition = False
                for pp in partition_polygons:
                    if cell_box.intersects(pp):
                        hits_partition = True
                        break
                if hits_partition:
                    current_x += cell_width
                    continue

                # --- Rule 3: Aisle Clearance (Left & Right) ---
                left_aisle = box(current_x - aisle_width, current_y, current_x, current_y + cell_height)
                right_aisle = box(current_x + cell_width, current_y, current_x + cell_width + aisle_width, current_y + cell_height)
                aisles_valid = True

                for aisle_box in [left_aisle, right_aisle]:
                    if not tree: break
                    
                    overlap_area = 0.0
                    indices = tree.query(aisle_box)
                    
                    for i in indices:
                        obstacle = fixed_obstacles_for_aisle_check[i]
                        if aisle_box.intersects(obstacle):
                            overlap_area += aisle_box.intersection(obstacle).area

                    if (overlap_area / aisle_box.area) > max_aisle_blockage_ratio:
                        aisles_valid = False
                        break

                if aisles_valid:
                    final_grid_points.append((current_x, current_y))

                current_x += cell_width
            current_y += cell_height

        print(f"  -> ✅ Generated {len(final_grid_points)} spots.")
        return final_grid_points

        
    # touched
    def draw_grid_for_validation(self, doc, grid_points: List[Tuple[float, float]], cell_width: float, cell_height: float, layer_name: str, color: int):
        """
        Draws a calculated placement grid onto a specified layer for visualization.
        """
        if not grid_points:
            return

        print(f"--- 🎨 Drawing the '{layer_name}' grid for validation ---")
        if layer_name not in doc.doc.layers:
            doc.doc.layers.add(name=layer_name, color=color)

        for x, y in grid_points:
            points = [(x, y), (x + cell_width, y), (x + cell_width, y + cell_height), (x, y + cell_height)]
            doc.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": layer_name})
        
        print(f"  -> ✅ Drew {len(grid_points)} grid cells on layer '{layer_name}'.")
    
    # touched
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
    
    # touched
    def analyze_placement_patterns(self, doc) -> Dict[str, Any]:
        """
        Analyzes all four placement patterns and returns a comprehensive
        dictionary containing counts and ID-tagged coordinates for ALL options,
        as well as identifying the best one. Adds rank and placed keywords directly.
        """
        print("\n--- 📊 Analyzing ALL placement patterns and generating blueprints ---")
        
        all_patterns_data = {}
        
        row_points = self.generate_row_wise_grid(doc)
        col_points = self.generate_column_wise_grid(doc)

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

        # --- Phase 3: Find the Best Pattern ---
        if not all_patterns_data:
            best_pattern_name = "None"
        else:
            # Prioritize by count, then by 'column_wise' pattern in case of a tie.
            best_pattern_name = max(
                all_patterns_data,
                key=lambda p: (all_patterns_data[p]["count"], 'column' in p)
            )
            
        # print("---  Analysis Complete ---")
        # for name, data in all_patterns_data.items():
        #     print(f"  -> Pattern '{name}': {data['count']} fixtures")
        # print(f"  ->  BEST PATTERN: '{best_pattern_name}' with {all_patterns_data.get(best_pattern_name, {}).get('count', 0)} fixtures.")

        # Add rank and placed keywords
        print("\n--- Adding rank and placed keywords to all_patterns_data ---")
        sorted_patterns = sorted(all_patterns_data.items(), key=lambda x: x[1]["count"], reverse=True)

        rank = 1
        for pattern_name, pattern_data in sorted_patterns:
            pattern_data["rank"] = rank
            pattern_data["placed"] = False  # Default to False
            rank += 1

        # # Mark the best pattern as placed
        # if best_pattern_name in all_patterns_data:
        #     all_patterns_data[best_pattern_name]["placed"] = True

        print("---  Analysis Complete ---")
        for name, data in all_patterns_data.items():
            print(f"  -> Pattern '{name}': {data['count']} fixtures, Rank: {data['rank']}, Placed: {data['placed']}")
        print(f"  ->  BEST PATTERN: '{best_pattern_name}' with {all_patterns_data.get(best_pattern_name, {}).get('count', 0)} fixtures.")


        return {
            "best_pattern_name": best_pattern_name,
            "all_options": all_patterns_data
        }

    

    # touched
    def arranging_analyzed_function(self, doc, chosen_pattern_name, chosen_pattern_data) -> dict:
        """
        [MODIFIED v4] Refines the placement plan based on required count vs. available spots.
        Applies DYNAMIC aesthetic grouping (even distribution) if space allows.
        Selects the best available pattern but DOES NOT mark it as placed.

        Args:
            display_calcs: Dictionary containing the required 'floor_fixtures' count.
            analysis_result: The full output dictionary from analyze_placement_patterns().
                            This dictionary itself is NOT modified by this function.

        Returns:
            A dictionary containing the plan for the *single best available* pattern:
            {
                'chosen_pattern_name': str,
                'placements': dict, # The coordinates to use for placement
                'overflow_display': int
            }
            Returns an empty dict if no suitable pattern is found.
        """
        print("\n--- 🧠 Arranging Euro Centre Placement Plan (with DYNAMIC Gaps) ---")
        # Make a deep copy to avoid modifying the input analysis_result
        

        required_count = doc.display_calcs.get('floor_fixtures', 0)
        overflow_display = 0
        final_placements = {}
        max_count = chosen_pattern_data.get('count', 0)

        print(f"  -> Required Euro Centres: {required_count}")

        print(f"  -> Selected best available pattern: '{chosen_pattern_name}' (Rank {chosen_pattern_data['rank']}, Capacity: {max_count})")

        original_coordinates_dict = chosen_pattern_data.get('placements', {})


        # available_coords = sorted(
        #     [tuple(item['coordinates']) for item in original_coordinates_dict.values()],
        #     key=lambda p: (p[1], p[0]) # Sort Y then X
        # )
        #--------RASHEEQUE MAKES CHANGE HERE TO FIX THE SORTING ISSUE---------
        # Sort differently based on pattern type
        if 'column_wise' in chosen_pattern_name:
            # For column-wise: sort by X first, then Y (to get column-by-column order)
            available_coords = sorted(
                [tuple(item['coordinates']) for item in original_coordinates_dict.values()],
                key=lambda p: (p[0], p[1])  # Sort X then Y
            )
            print(f"  -> Using COLUMN-WISE sorting (X, Y)")
        else:
            # For row-wise: sort by Y first, then X (to get row-by-row order)
            available_coords = sorted(
                [tuple(item['coordinates']) for item in original_coordinates_dict.values()],
                key=lambda p: (p[1], p[0])  # Sort Y then X
            )
            print(f"  -> Using ROW-WISE sorting (Y, X)")
        #--------RASHEEQUE MAKES CHANGES ENDED HERE---------

        selected_coords_final = []

        # --- Scenario A: Place with DYNAMIC Gaps (required_count < max_count) ---
        if 0 < required_count < max_count:
            print(f"  -> Scenario A: Sufficient space ({max_count} slots for {required_count} fixtures). Applying dynamic even distribution.")
            remaining_grid_space = max_count - required_count
            print(f"     -> Will insert {remaining_grid_space} skips.")

            # --- Calculate target indices for placement ---
            N = max_count  # Total slots
            K = required_count # Fixtures to place
            target_indices = set()
            if K > 0: # Avoid division by zero if required_count is 0
                for k in range(K):
                    # Calculate the ideal index for fixture k
                    grid_index = math.floor(k * N / K)
                    # Ensure index stays within bounds (although it should naturally)
                    target_indices.add(min(grid_index, N - 1))

            print(f"     -> Calculated target grid indices for placement: {sorted(list(target_indices))}")

            # --- Select coordinates based on calculated indices ---
            if len(available_coords) == N: # Double-check we have the expected number of coordinates
                for grid_index in range(N):
                    if grid_index in target_indices:
                        selected_coords_final.append(available_coords[grid_index])
                        print(f"       -> Selecting coordinate at grid index {grid_index}")
                    else:
                        print(f"       -> Skipping coordinate at grid index {grid_index}")
            else:
                print(f"     -> ⚠️ WARNING: Mismatch between max_count ({N}) and number of available coordinates ({len(available_coords)}). Falling back to simple consecutive placement for safety.")
                selected_coords_final = available_coords[:required_count] # Fallback

            print(f"     -> Selected {len(selected_coords_final)} coordinates using dynamic distribution.")
            overflow_display = 0

        # --- Scenario B: Place Consecutively (required_count >= max_count) ---
        else: # Handles required_count == 0, required_count == max_count, required_count > max_count
            if required_count == 0:
                print("  -> Scenario B: Required count is 0. No fixtures needed.")
                selected_coords_final = []
                overflow_display = 0
            elif required_count >= max_count:
                print(f"  -> Scenario B: Space limited or exact fit (Required: {required_count}, Max: {max_count}). Placing {max_count} consecutively.")
                # Ensure we don't try to take more coordinates than available
                num_to_select = min(required_count, max_count, len(available_coords))
                selected_coords_final = available_coords[:num_to_select]
                overflow_display = required_count - num_to_select # Calculate overflow based on actual selected count
                if overflow_display > 0:
                    print(f"     -> Overflow calculated: {overflow_display}")


        # --- Build final placements dictionary ---
        final_placements = {}
        for i, coords in enumerate(selected_coords_final, start=1):
            final_placements[f"count_{i}"] = {"coordinates": list(coords)}

        print(f"  -> Final count for placement in this pattern: {len(final_placements)}")

        # --- Return the plan for execution ---
        return {
            'chosen_pattern_name': chosen_pattern_name,
            'placements': final_placements,
            'overflow_display': overflow_display
        }


    

    #--RASHEEQUE EDITED--THIS--FUNCTION--02/12
    def place_by_plan_euro(self, doc, arranged_plan: dict):
        """
        [RESTORED] Places Euro Centres directly from the plan coordinates.
        No redundant validation is performed, ensuring alignment with the grid.
        """
        print("\n--- 💶 Placing Euro Centres Directly from Arranged Plan ---")

        chosen_pattern_name = arranged_plan.get('chosen_pattern_name', "None")
        placements_to_execute = arranged_plan.get('placements', {})

        if not placements_to_execute:
            print("  -> SKIPPED: No valid placement plan provided.")
            return

        # --- 1. Load Fixture & Setup ---
        base_angle_rad = self._get_floorplan_main_angle()
        base_angle_deg = math.degrees(base_angle_rad)
        
        try:
            fxtr = Fixture.Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"])
        except Exception as e:
            print(f"  -> 🔥 FATAL: Could not load Euro_centre fixture: {e}")
            return

        is_rotated = 'column_wise' in chosen_pattern_name
        
        # Rotation logic
        height = self.cvc.max_y - self.cvc.min_y
        width = self.cvc.max_x - self.cvc.min_x
        is_tall_floorplan = height > width
        
        relative_rotation = 0.0
        if is_tall_floorplan:
            relative_rotation = 0.0 if is_rotated else 90.0
        else:
            relative_rotation = 90.0 if is_rotated else 0.0
        
        rotation = base_angle_deg + relative_rotation
        cell_width = fxtr.height if is_rotated else fxtr.width
        cell_height = fxtr.width if is_rotated else fxtr.height
        
        doc.euro_placement_rotation = rotation 
        doc.euro_grid_is_column_wise = is_rotated

        # --- 2. Placement Loop ---
        placed_count = 0
        sorted_placement_keys = sorted(placements_to_execute.keys(), key=lambda k: int(k.split('_')[1]))

        for key in sorted_placement_keys:
            placement_data = placements_to_execute[key]
            coords = placement_data.get('coordinates')
            if not coords or len(coords) != 2: continue

            x, y = coords[0], coords[1]
            # Calculate center relative to the grid cell
            target_center = Vec2(x + (cell_width / 2), y + (cell_height / 2))

            try:
                # Calculate insertion point for rotation
                rotated_offset = fxtr.bounding_box.center.rotate(math.radians(rotation)) 
                final_insert_point = target_center - rotated_offset

                # Place directly
                block_ref = doc.place_fixture(
                    fxtr,
                    (final_insert_point.x, final_insert_point.y, 0),
                    rotation, 
                    is_rotated 
                )

                # Update Obstacles
                if block_ref:
                    bbox = extents([block_ref]) 
                    if bbox.has_data:
                        new_bbox_tuple = (bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y)
                        doc.placed_bboxes.append(new_bbox_tuple)
                        print(f"    -> Placed Euro_centre {key} at ({x:.0f}, {y:.0f}).")
                        placed_count += 1
            
            except Exception as e:
                print(f"    -> ⚠️ Error placing Euro_centre {key}: {e}")

        print(f"\n--- ✅ Finished Direct Placement: Placed {placed_count} Euro Centres. ---")


    
    # touched
    def place_euro_centers_from_blueprint(self, placement_blueprint: dict, doc):
        """
        Orchestrates the placement of Euro Centre fixtures by iterating through
        placement patterns based on their **rank** (lowest rank first).
        
        It attempts to place the required number of fixtures using the highest-ranked
        available pattern (placed=False). Once a pattern is successfully used, 
        its 'placed' flag is set to True.

        Args:
            placement_blueprint (dict): The output from analyze_placement_patterns() 
                                        containing 'all_options' with 'rank' and 'placed' keys.
            display_calcs (dict): The output from display_count_calc(), providing the base count.
            placed_bboxes (list): The master list of bounding boxes for all placed objects.
        """
        print("\n--- 💶 Placing Euro Centre Fixtures from Ranked Blueprint ---")
        
        # --- 1. Setup Obstacles (Same as original) ---
        temp_obstacles = list(doc.placed_bboxes)
        partitions = self.cvc.get_internal_wall_partitions(min_length=50, max_length=670.0, thickness=0.0)
        if partitions:
            temp_obstacles.extend(partitions)
        separator_line = doc.msp.query('LINE[layer=="RETAIL_SEPARATOR"]').first
        if separator_line:
            start_pt, end_pt = separator_line.dxf.start, separator_line.dxf.end
            separator_bbox = (min(start_pt.x, end_pt.x), min(start_pt.y, end_pt.y) - 1, max(start_pt.x, end_pt.x), max(start_pt.y, end_pt.y) + 1)
            if separator_bbox in temp_obstacles:
                temp_obstacles.remove(separator_bbox)
        # --- End Setup ---

        # --- 2. Determine Required Count (Same as original) ---
        total_required_euros = doc.display_calcs.get('floor_fixtures', 0)
        if total_required_euros == 0:
            total_required_euros = self.fixtures.get("floor_fixtures", {}).get("Euro_centre", 0)

        if total_required_euros <= 0:
            print("  -> SKIPPED: No Euro Centre fixtures required.")
            return

        print(f"  -> Total required Euro Centres to place: {total_required_euros}")
        
        all_options = placement_blueprint.get("all_options", {})
        if not all_options:
            print("  -> ⚠️ FAILED: Placement options list is empty.")
            doc.overflow_fixture_count = total_required_euros
            return

        # --- 3. Find the Best AVAILABLE Pattern by Rank ---
        
        # Sort options by rank (1, 2, 3...)
        ranked_options = sorted(all_options.items(), key=lambda item: item[1].get('rank', float('inf')))

        selected_pattern_name = None
        selected_pattern_info = None

        for name, info in ranked_options:
            if not info.get('placed', False) and info.get('count', 0) > 0:
                selected_pattern_name = name
                selected_pattern_info = info
                break

        if selected_pattern_name is None:
            print("  -> ⚠️ FAILED: No available patterns found with capacity > 0.")
            doc.overflow_fixture_count = total_required_euros
            return
            
        # --- 4. Placement Decision and Capacity Check (Modified) ---
        
        max_capacity = selected_pattern_info.get("count", 0)
        placements = selected_pattern_info.get("placements", {})
        
        print(f"  -> Selected Pattern: '{selected_pattern_name}' (Rank: {selected_pattern_info['rank']}) with max capacity: {max_capacity}.")

        num_to_place = 0
        doc.overflow_fixture_count = 0
        EURO_PLACEMENT_CAP = 9

        # Determine how many to physically place and calculate overflow
        if max_capacity <= total_required_euros:
            num_to_place = max_capacity
            doc.overflow_fixture_count = total_required_euros - max_capacity
        else:
            num_to_place = total_required_euros

        # Apply the hard cap
        if num_to_place > EURO_PLACEMENT_CAP:
            remaining_after_cap = num_to_place - EURO_PLACEMENT_CAP
            num_to_place = EURO_PLACEMENT_CAP
            doc.overflow_fixture_count += remaining_after_cap
            print(f"  -> NOTE: Capped placement to {EURO_PLACEMENT_CAP}. Added {remaining_after_cap} to overflow.")

        if num_to_place == 0:
            print("  -> No fixtures to place based on the chosen strategy.")
            doc.overflow_fixture_count = total_required_euros
            return

        # --- 5. Execute Placement and Finalize ---
        
        # Mark the chosen pattern as placed
        selected_pattern_info["placed"] = True 

        # Load fixture (Same as original)
        try:
            fxtr = Fixture.Fixture("Euro_centre", self.fixture_dict["Euro_centre"]["path"])
        except Exception as e:
            print(f"  -> 🔥 FATAL: Could not load Euro_centre fixture: {e}")
            return

        # Determine rotation and cell dimensions (Same as original)
        is_rotated = 'column_wise' in selected_pattern_name
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

            next_target_center = None
            if i + 1 < len(placement_coords):
                next_x, next_y = placement_coords[i + 1]
                next_target_center = Vec2(next_x + (cell_width / 2), next_y + (cell_height / 2))

            if self._validate_and_place_at_point_euro(doc, fxtr, target_center, rotation, temp_obstacles, debug_draw=False, next_target_center=next_target_center):
                print(f"    -> Placed Euro_centre #{placed_count + 1} at ({x:.0f}, {y:.0f}) with {rotation}° rotation.")
                placed_count += 1
            else:
                print(f"    -> ⚠️ WARNING: Spot at ({x:.0f}, {y:.0f}) was blocked, skipping.")

        print(f"\n--- ✅ Finished Euro Centre Placement: Placed {placed_count} of {num_to_place} planned fixtures. ---")

    # touched
    #--RASHEEQUE EDITED--THIS--FUNCTION--02/12/2025
    def _validate_and_place_at_point_euro(self, doc, fixture, target_center, angle_deg, placed_bboxes, debug_draw=False, next_target_center: Optional[Vec2] = None, spatial_index=None):
        """
        [OPTIMIZED & RELAXED] Validates and places a fixture.
        Uses Spatial Index (STRtree) and allows 90% containment to match grid logic.
        """

        # --- Internal Helper: Check a specific spot ---
        def check_spot(center_point):
            AISLE_OVERLAP_TOLERANCE_AREA = 600000.0
            BODY_OVERLAP_TOLERANCE_AREA = 1000.0
            MIN_CONTAINMENT_RATIO = 0.90  # Match the grid generation tolerance
            
            # 1. Calculate Geometry
            transform = Matrix44.chain(
                Matrix44.translate(-fixture.bounding_box.center.x, -fixture.bounding_box.center.y, 0), 
                Matrix44.z_rotate(math.radians(angle_deg)), 
                Matrix44.translate(center_point.x, center_point.y, 0)
            )
            world_corners = list(transform.transform_vertices(fixture.bounding_box.rect_vertices()))
            current_aabb = BoundingBox2d(world_corners)
            fixture_polygon = Polygon([(p.x, p.y) for p in world_corners])
            
            # 2. Relaxed Floorplan Boundary Check
            # Instead of strict .contains(), we check intersection area
            if not self.floorplan_polygon.contains(fixture_polygon):
                intersection_area = self.floorplan_polygon.intersection(fixture_polygon).area
                if (intersection_area / fixture_polygon.area) < MIN_CONTAINMENT_RATIO:
                    return None, None

            # 3. FAST COLLISION CHECK (Spatial Index vs Linear Scan)
            potential_collisions = []
            
            if spatial_index:
                indices = spatial_index.query(fixture_polygon)
                for i in indices:
                    potential_collisions.append(spatial_index.geometries[i])
            else:
                potential_collisions = [box(*b) for b in placed_bboxes]

            # 4. Detailed Intersection Check
            for obstacle_poly in potential_collisions:
                if fixture_polygon.intersects(obstacle_poly):
                    if fixture_polygon.intersection(obstacle_poly).area > BODY_OVERLAP_TOLERANCE_AREA: 
                        return None, None

            # 5. Aisle Blockage Check (Euro Centre specific)
            if "euro_centre" in fixture.name.lower():
                clearance = 1050.0
                
                if 85 < angle_deg < 95 or 265 < angle_deg < 275:
                    aisles = [
                        box(current_aabb.extmin.x - clearance, current_aabb.extmin.y + 100, current_aabb.extmin.x, current_aabb.extmax.y - 100),
                        box(current_aabb.extmax.x, current_aabb.extmin.y + 100, current_aabb.extmax.x + clearance, current_aabb.extmax.y - 100)
                    ]
                else:
                    aisles = [
                        box(current_aabb.extmin.x + 100, current_aabb.extmax.y, current_aabb.extmax.x - 100, current_aabb.extmax.y + clearance),
                        box(current_aabb.extmin.x + 100, current_aabb.extmin.y - clearance, current_aabb.extmax.x - 100, current_aabb.extmin.y)
                    ]

                for aisle_poly in aisles:
                    if spatial_index:
                        aisle_indices = spatial_index.query(aisle_poly)
                        aisle_potential = [spatial_index.geometries[i] for i in aisle_indices]
                    else:
                        aisle_potential = potential_collisions

                    for obstacle_poly in aisle_potential:
                        if aisle_poly.intersects(obstacle_poly) and aisle_poly.intersection(obstacle_poly).area > AISLE_OVERLAP_TOLERANCE_AREA:
                            return None, None

            return current_aabb, center_point

        # --- Main Logic (Search Strategy) ---
        final_aabb, final_center = check_spot(target_center)

        if final_aabb is None:
            # Re-fetch zone only if nudging is required
            zone = doc.euro_zone 
            if not zone or zone.is_empty: return False

            if next_target_center:
                search_vector = (next_target_center - target_center).normalize()
                step = 50
                current_offset = step
                # Try nudging up to 500mm towards the next fixture
                while current_offset <= 500:
                    test_center = target_center + (search_vector * current_offset)
                    # Relaxed check for search points: center must be in zone
                    if not zone.contains(Point(test_center.x, test_center.y)): break
                    found_aabb, found_center = check_spot(test_center)
                    if found_aabb:
                        final_aabb, final_center = found_aabb, found_center
                        break
                    current_offset += step
            else:
                search_vectors = [Vec2(1, 0), Vec2(-1, 0), Vec2(0, 1), Vec2(0, -1)]
                step = 50
                for move_vec in search_vectors:
                    for i in range(1, 6): # limit search radius
                        test_center = target_center + (move_vec * (i * step))
                        if not zone.contains(Point(test_center.x, test_center.y)): continue
                        found_aabb, found_center = check_spot(test_center)
                        if found_aabb:
                            final_aabb, final_center = found_aabb, found_center
                            break
                    if final_aabb: break

        if final_aabb is None:
            return False

        if final_center:
            rotated_offset = fixture.bounding_box.center.rotate(math.radians(angle_deg))
            final_insert_point = final_center - rotated_offset
            doc.place_fixture(fixture, (final_insert_point.x, final_insert_point.y, 0), angle_deg, True)
            doc.placed_bboxes.append((final_aabb.extmin.x, final_aabb.extmin.y, final_aabb.extmax.x, final_aabb.extmax.y))
            return True
            
        return False
    
    # touched
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
            
            benches_to_place_arr = []
            for name, count in bench_config.items():
                if count > 0:
                    try:
                        fxtr = Fixture.Fixture(name, self.fixture_dict[name]["path"])
                        benches_to_place_arr.extend([fxtr] * count)
                    except (KeyError, ValueError) as e:
                        print(f"⚠️ Warning: lensometer fixture '{name}' could not be loaded: {e}")
            
            if not benches_to_place_arr:
                return

            all_segments = self.cvc.get_wall_segments(min_length=500)
            if not all_segments:
                print("⚠️ No suitable wall segments found. Try reducing min_length in get_wall_segments.")
                return
            
            for doc in self.docs:
                if doc.skip:
                    continue

                print(f" ----> placing doc {doc.ind}")

                benches_to_place = copy.deepcopy(benches_to_place_arr)

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
                            is_overlapping = any(bench_aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in doc.placed_bboxes)

                            if is_inside and not is_overlapping:
                                doc.place_fixture(bench, (final_insert_point.x, final_insert_point.y, 0), wall_angle_deg, True)
                                print(f"  ✅ SUCCESS: Placed '{bench.name}'.")
                                doc.placed_bboxes.append((bench_aabb.extmin.x, bench_aabb.extmin.y, bench_aabb.extmax.x, bench_aabb.extmax.y))
                                benches_placed_count += 1
                                is_bench_placed = True
                                break
                            
                            search_distance += 100 
                        
                        if is_bench_placed:
                            break

                    if not is_bench_placed:
                        doc.skip = True
                        print("SKIP DOC")
                        print(f"⚠️ Could not find a valid position for lensometer '{bench.name}' on any wall.")
                
                print(f"-> Placed {benches_placed_count} of {len(benches_to_place)} requested lensometers.")

        except Exception as e:
            print(f"🔥 An error occurred during lensometer placement: {e}")
            traceback.print_exc()
            raise


    #---RASHEEQUE--EDITTED--THIS--FUNCTION--11/11
    def place_Blue_Zero_attached(self):
        """
        [FINAL, FINAL CORRECTED VERSION - v3]
        Places "Blue_zero" fixtures, respecting the accessible aisles of Euro Centres.
        - Reads the 'euro_grid_is_column_wise' flag.
        - Column-wise Grid (Vertical Euros): Aisles are L/R -> Places on TOP/BOTTOM.
        - Row-wise Grid (Horizontal Euros): Aisles are T/B -> Places on LEFT/RIGHT.
        """

        # 1. SETUP (Unchanged)
        config = self.fixtures.get("discussion_table_attached", {})
        blue_zero_count = config.get("Blue_zero", 0)
        if blue_zero_count <= 0:
            return

        print("\n--- Attempting to place attached discussion fixtures (Blue_zero) [AISLE AWARE v3] ---")
        try:
            blue_zero_fxtr = Fixture.Fixture("Blue_zero", self.fixture_dict["Blue_zero"]["path"])
        except Exception as e:
            print(f"⚠️ Could not load the Blue_zero fixture file: {e}")
            return

        for doc in self.docs:
            if doc.skip:
                continue
            
            print(f" ----> placing doc {doc.ind}")
            
            # 2. FIND PRIMARY ANCHORS (Unchanged)
            primary_anchors = []
            for entity in doc.msp.query('INSERT'):
                if "DISCUSSION_TABLE" in entity.dxf.name.upper():
                    try:
                        primary_anchors.append(extents([entity], fast=True))
                    except (RuntimeError, TypeError):
                        continue

            placed_count = 0
            margin = 5.0 # Reduced margin to tuck it closer

            # 3. EXECUTE PRIMARY STRATEGY (Unchanged)
            if primary_anchors:
                print(f"  -> Found {len(primary_anchors)} Discussion Table(s) to use as primary anchors.")
                for target_bbox in primary_anchors:
                    if placed_count >= blue_zero_count: break
                    
                    target_x = target_bbox.center.x - (blue_zero_fxtr.width / 2)
                    target_y = target_bbox.extmin.y - margin - blue_zero_fxtr.height
                    candidate_box = box(target_x, target_y, target_x + blue_zero_fxtr.width, target_y + blue_zero_fxtr.height)
                    is_overlapping = any(candidate_box.intersects(box(*b)) for b in doc.placed_bboxes)
                    is_inside = self.floorplan_polygon.contains(candidate_box)

                    if is_inside and not is_overlapping:
                        doc.place_fixture(blue_zero_fxtr, (target_x, target_y, 0), 0, False)
                        doc.placed_bboxes.append(candidate_box.bounds)
                        print(f"✅ Placed Blue_zero below a Discussion Table.")
                        placed_count += 1
                    else:
                        print(f"ℹ️ Spot below a Discussion Table was blocked.")
            
            # 4. EXECUTE FALLBACK STRATEGY (Anchor to Euro Centres)
            if placed_count < blue_zero_count:
                print("\n  -> No more Discussion Table spots. Searching for Euro_centre fixtures as a fallback.")
                euro_entities = [e for e in doc.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
                if not euro_entities:
                    print("ℹ️ No Euro centres were found for fallback placement.")
                    return

                # --- START OF MODIFICATION ---
                # Get the *grid orientation flag* we stored, not the final rotation angle.
                # Default to False (row-wise) if the flag wasn't set for any reason.
                is_column_wise_grid = getattr(doc, 'euro_grid_is_column_wise', False)
                # --- END OF MODIFICATION ---

                fallback_anchors = [extents([e]) for e in euro_entities]

                # --- START OF SWAPPED LOGIC ---

                if is_column_wise_grid:
                    # --- STRATEGY A: COLUMN-WISE (Vertical Euros) ---
                    # Aisles are LEFT/RIGHT. Place on TOP/BOTTOM.
                    print("  -> Detected Column-wise layout. Placing Blue_zero on TOP/BOTTOM sides.")
                    for target_bbox in fallback_anchors:
                        if placed_count >= blue_zero_count:
                            break
                        was_placed = False

                        # Attempt 1: Place BELOW
                        target_x = target_bbox.center.x - (blue_zero_fxtr.width / 2)
                        target_y_below = target_bbox.extmin.y - margin - blue_zero_fxtr.height
                        candidate_box_below = box(target_x, target_y_below, target_x + blue_zero_fxtr.width, target_y_below + blue_zero_fxtr.height)
                        
                        if self.floorplan_polygon.contains(candidate_box_below) and not any(candidate_box_below.intersects(box(*b)) for b in doc.placed_bboxes):
                            doc.place_fixture(blue_zero_fxtr, (target_x, target_y_below, 0), 0, False)
                            doc.placed_bboxes.append(candidate_box_below.bounds)
                            print(f"✅ Placed Blue_zero BELOW a Euro Centre.")
                            placed_count += 1
                            was_placed = True

                        # Attempt 2: Place ABOVE
                        if not was_placed:
                            target_y_above = target_bbox.extmax.y + margin
                            candidate_box_above = box(target_x, target_y_above, target_x + blue_zero_fxtr.width, target_y_above + blue_zero_fxtr.height)

                            if self.floorplan_polygon.contains(candidate_box_above) and not any(candidate_box_above.intersects(box(*b)) for b in doc.placed_bboxes):
                                doc.place_fixture(blue_zero_fxtr, (target_x, target_y_above, 0), 0, False)
                                doc.placed_bboxes.append(candidate_box_above.bounds)
                                print(f"✅ Placed Blue_zero ABOVE a Euro Centre (fallback).")
                                placed_count += 1
                                was_placed = True
                
                else:
                    # --- STRATEGY B: ROW-WISE (Horizontal Euros) ---
                    # Aisles are TOP/BOTTOM. Place on LEFT/RIGHT.
                    print("  -> Detected Row-wise layout. Placing Blue_zero on LEFT/RIGHT sides.")
                    
                    rotated_width = blue_zero_fxtr.height
                    rotated_height = blue_zero_fxtr.width
                    rotation = 90.0

                    for i, target_bbox in enumerate(fallback_anchors):
                        if placed_count >= blue_zero_count: break
                        
                        side = "left" if i % 2 == 0 else "right"
                        
                        if side == "left":
                            # Place on LEFT side of Euro
                            insert_x = target_bbox.extmin.x - margin
                            insert_y = target_bbox.center.y - (rotated_height / 2)
                            final_insert_point = (insert_x, insert_y, 0)
                            
                            candidate_box_x_start = insert_x - rotated_width
                            candidate_box = box(candidate_box_x_start, insert_y, 
                                                candidate_box_x_start + rotated_width, insert_y + rotated_height)

                        else: # side == "right"
                            # Place on RIGHT side of Euro
                            insert_x = target_bbox.extmax.x + margin + rotated_width
                            insert_y = target_bbox.center.y - (rotated_height / 2)
                            final_insert_point = (insert_x, insert_y, 0)
                            
                            candidate_box_x_start = insert_x - rotated_width
                            candidate_box = box(candidate_box_x_start, insert_y, 
                                                candidate_box_x_start + rotated_width, insert_y + rotated_height)
                            
                        # Common Validation & Placement
                        if self.floorplan_polygon.contains(candidate_box) and not any(candidate_box.intersects(box(*b)) for b in doc.placed_bboxes):
                            doc.place_fixture(blue_zero_fxtr, final_insert_point, rotation, True)
                            doc.placed_bboxes.append(candidate_box.bounds)
                            print(f"✅ Placed Blue_zero on the {side} of a Euro Centre.")
                            placed_count += 1
                        else:
                            print(f"ℹ️ Spot on the {side} of Euro Centre was blocked.")
                            
                # --- END OF SWAPPED LOGIC ---

            if placed_count < blue_zero_count:
                print(f"⚠️ Warning: Placed only {placed_count} of {blue_zero_count} requested Blue_zero fixtures.")


    
    # touched
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

    # touched 
    def _get_new_standing_table_anchor_y(self, doc) -> Optional[float]:
        """
        [Plan B Logic] Calculates new anchor-Y for Standing Tables.

        Updated behaviour:
        - When the available horizontal width condition is met, prefer anchoring
          to the bottom (min-y) of the BOH zone if a BOH zone exists.
        - If no BOH zone is present, fall back to anchoring to the last clinic bottom.
        """
        
        print("\n  -> [Plan B Logic] Calculating new anchor-Y for Standing Tables...")

        # 1a. Find the "last" placed clinic (the one furthest to the right)
        clinic_entities = [e for e in doc.msp.query('INSERT') if "CLINIC" in e.dxf.name.upper()]
        if not clinic_entities:
            print("    -> ⚠️ No clinics found. Falling back to standard anchor method.")
            return self._get_standing_table_anchor_y(doc)

        last_clinic_coords = self._get_last_clinic_right_bottom_coord(doc)
        
        if last_clinic_coords is None:
            print("    -> ⚠️ Could not get accurate last clinic coordinates. Falling back to standard anchor method.")
            return self._get_standing_table_anchor_y(doc)

        last_clinic_right_edge_x, last_clinic_bottom_y = last_clinic_coords
        
        print(f"    -> Last clinic (right-most) found at x={last_clinic_right_edge_x:.0f}")
        print(f"    -> Last clinic (bottom) found at y={last_clinic_bottom_y:.0f}")

        # 1b. Find the right-side boundary (either the Pickup Window or the wall)
        right_boundary_x = self.cvc.max_x  # Default to the right wall

        pickup_window = None
        for entity in doc.msp.query('INSERT'):
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
        #---RASHEEQUE----
        if available_width > 3000:
        #---RASHEEQUE----
            print(f"    -> Available width is {available_width:.0f}mm.")

            # NEW: prefer BOH zone bottom as anchor when available
            boh_poly = None
            try:
                boh_poly = self._get_boh_zone_polygon(doc)
            except Exception:
                boh_poly = None

            if boh_poly:
                boh_min_y = boh_poly.bounds[1]  # bounds -> (minx, miny, maxx, maxy)
                print(f"    -> Anchoring to BOH zone bottom at y={boh_min_y:.0f} instead of last clinic.")
                return boh_min_y
            else:
                final_anchor_clinic_details = max(doc.placed_clinics_on_top_wall, key=lambda c: c['bbox'][2])
                
                print(f"    -> BOH zone not found. Anchoring to the bottom of the last clinic (y={final_anchor_clinic_details['bbox'].extmin.y:.0f}).")
                return final_anchor_clinic_details['bbox'].extmin.y
        else:
            # 3. If space is insufficient, fall back to the original method
            print(f"    -> Available width is {available_width:.0f}mm.")
            print("    -> Space is not > 1500mm. Falling back to the standard non-retail boundary anchor method.")
            return self._get_standing_table_anchor_y(doc)
    
    # touched
    def _get_standing_table_anchor_y(self, doc) -> Optional[float]:
        """
        FINDS THE CORRECT ANCHOR LINE (Y-coordinate) to measure from for standing tables.
        1. Finds the lowest non-retail fixture.
        2. Checks if any Bench/AR fixture is within a vertical gap threshold below it 
        AND falls within the central "standing table corridor".
        3. Returns the Y-coordinate of the correct anchor.
        """

        # --- CONFIGURABLE CONSTANTS ---
        VERTICAL_GAP_THRESHOLD_MM = 500.0    # Max distance below BOH to check for furniture
        HORIZONTAL_AISLE_RATIO = 0.25        # Percentage of room width for side aisles (25% each side = 50% center)
        # --- END CONSTANTS ---

        print("\n  -> Finding dynamic anchor-Y for Standing Tables (using Central Corridor Proxy)...")

        # --- STEP 1: Find the lowest placed non-retail fixture ---
        non_retail_entities = [
            e for e in doc.msp.query('LINE[layer=="RETAIL_SEPARATOR"]')
        ]
        all_polylines = doc.msp.query('LWPOLYLINE')
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

        # --- STEP 2: DEFINE THE PROXY ZONE (Central Corridor) ---
        room_width = self.cvc.max_x - self.cvc.min_x
        aisle_margin = room_width * HORIZONTAL_AISLE_RATIO  # Use the constant
        standing_table_zone_start_x = self.cvc.min_x + aisle_margin
        standing_table_zone_end_x = self.cvc.max_x - aisle_margin
        
        print(f"    -> Defined standing table proxy zone:")
        print(f"       X-Range: {standing_table_zone_start_x:.0f} to {standing_table_zone_end_x:.0f}")
        print(f"       (Central {int((1 - 2*HORIZONTAL_AISLE_RATIO)*100)}% of room width, {int(HORIZONTAL_AISLE_RATIO*100)}% aisles on each side)")

        # --- STEP 3: Check for Bench or AR within the PROXY ZONE ---
        furniture_entities = [
            e for e in doc.msp.query('INSERT') if
            "BENCH" in e.dxf.name.upper() or "AR" in e.dxf.name.upper()
        ]
        
        new_anchor_furniture_bbox = None
        if furniture_entities:
            candidate_furniture = []
            for entity in furniture_entities:
                try:
                    furniture_bbox = extents([entity])
                    
                    # Condition 1: Vertically below and within threshold distance
                    vertical_distance = lowest_non_retail_y - furniture_bbox.extmax.y
                    is_vertically_close = (
                        furniture_bbox.extmax.y < lowest_non_retail_y and 
                        vertical_distance <= VERTICAL_GAP_THRESHOLD_MM  # Use the constant
                    )

                    # Condition 2: Horizontally inside the standing table proxy zone
                    is_in_central_zone = (
                        standing_table_zone_start_x < furniture_bbox.extmax.x and
                        furniture_bbox.extmin.x < standing_table_zone_end_x
                    )

                    # Debug output for rejected furniture (optional)
                    if not (is_vertically_close and is_in_central_zone):
                        rejection_reason = []
                        if not is_vertically_close:
                            rejection_reason.append(f"too far vertically ({vertical_distance:.0f}mm > {VERTICAL_GAP_THRESHOLD_MM}mm)")
                        if not is_in_central_zone:
                            rejection_reason.append("outside central corridor")
                        print(f"       Rejected {entity.dxf.name}: {', '.join(rejection_reason)}")

                    # The furniture is only a candidate if BOTH conditions are true
                    if is_vertically_close and is_in_central_zone:
                        candidate_furniture.append(furniture_bbox)
                        print(f"       ✓ Accepted {entity.dxf.name} as candidate (vertical gap: {vertical_distance:.0f}mm)")
                        
                except (RuntimeError, TypeError) as e:
                    print(f"       ⚠️ Error processing {entity.dxf.name}: {e}")
                    continue
            
            if candidate_furniture:
                new_anchor_furniture_bbox = min(candidate_furniture, key=lambda b: b.extmin.y)

        # --- STEP 4: Determine and return the final anchor Y-coordinate ---
        if new_anchor_furniture_bbox:
            final_anchor_y = new_anchor_furniture_bbox.extmin.y
            print(f"    -> ✅ Found relevant furniture in the central corridor.")
            print(f"       Final anchor is the furniture's bottom edge at y={final_anchor_y:.0f}.")
            return final_anchor_y
        else:
            print(f"    -> ℹ️ No qualifying furniture in the central path within {VERTICAL_GAP_THRESHOLD_MM}mm.")
            print(f"       Final anchor is the non-retail fixture's bottom edge at y={lowest_non_retail_y:.0f}.")
            return lowest_non_retail_y


    def _get_standing_table_anchor_y_new(self, doc) -> Optional[float]:
        """
        FINDS THE CORRECT ANCHOR LINE (Y-coordinate) to measure from for standing tables.
        1. Finds the lowest non-retail fixture.
        2. Checks if any Bench/AR fixture is within 500mm below it AND falls within the
        central "standing table corridor".
        3. Returns the Y-coordinate of the correct anchor.
        """
    
        print("\n  -> Finding dynamic anchor-Y for Standing Tables (using Central Corridor Proxy)...")

        # --- STEP 1: Find the lowest placed non-retail fixture (No change here) ---
        non_retail_entities = [
            e for e in doc.msp.query('LINE[layer=="RETAIL_SEPARATOR"]')
        ]
        all_polylines = doc.msp.query('LWPOLYLINE')
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
            e for e in doc.msp.query('INSERT') if
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

    # touched
    def place_corian_table_set(self):
        """
        Places Corian Table sets using a multi-strategy approach with a resilient
        horizontal search to find a clear, centered position.
        """
        print("\n--- Attempting to place Corian Table Set with Resilient Centering ---")

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
        def _place_single_set(set_x, set_y, doc):
            print(f"    ✅ Found valid spot. Placing components for set at ({set_x:.0f}, {set_y:.0f})...")

            table_x = set_x + (set_width - table_fxtr.width) / 2
            table_y = set_y + seat_fxtr.height + gap_table_to_seat
            doc.place_fixture(table_fxtr, (table_x, table_y, 0), 0, False)
            doc.placed_bboxes.append((table_x, table_y, table_x + table_fxtr.width, table_y + table_fxtr.height))

            top_seats_x_start = set_x + (set_width - (seat_fxtr.width * 2 + gap_between_seats)) / 2
            top_seats_y = table_y + table_fxtr.height + gap_table_to_seat
            doc.place_fixture(seat_fxtr, (top_seats_x_start + seat_fxtr.width, top_seats_y + seat_fxtr.height, 0), 180, False)
            doc.placed_bboxes.append((top_seats_x_start, top_seats_y, top_seats_x_start + seat_fxtr.width, top_seats_y + seat_fxtr.height))
            
            seat2_x = top_seats_x_start + seat_fxtr.width + gap_between_seats
            doc.place_fixture(seat_fxtr, (seat2_x + seat_fxtr.width, top_seats_y + seat_fxtr.height, 0), 180, False)
            doc.placed_bboxes.append((seat2_x, top_seats_y, seat2_x + seat_fxtr.width, top_seats_y + seat_fxtr.height))
            
            bottom_seats_x_start = top_seats_x_start
            bottom_seats_y = set_y
            doc.place_fixture(seat_fxtr, (bottom_seats_x_start, bottom_seats_y, 0), 0, False)
            doc.placed_bboxes.append((bottom_seats_x_start, bottom_seats_y, bottom_seats_x_start + seat_fxtr.width, bottom_seats_y + seat_fxtr.height))
            
            seat4_x = bottom_seats_x_start + seat_fxtr.width + gap_between_seats
            doc.place_fixture(seat_fxtr, (seat4_x, bottom_seats_y, 0), 0, False)
            doc.placed_bboxes.append((seat4_x, bottom_seats_y, seat4_x + seat_fxtr.width, seat_fxtr.height))

        for doc in self.docs:
            if doc.skip:
                continue

            print(f" ----> placing doc {doc.ind}")
            # 4. FIND A VALID Y-LEVEL
            ideal_y = None
            strategy_found = False
            
            # *** FIX APPLIED ON THIS LINE ***
            euro_entities = [e for e in doc.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
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
                    doc.skip = True
                    print("SKIP DOC")
                    print(f"⚠️ FAILED: Not enough horizontal width ({intersection.length:.0f}mm) at the chosen Y-level for the Corian sets ({total_group_width:.0f}mm).")
                    continue
                    
                local_x_min, _, local_x_max, _ = intersection.bounds
                
                ideal_x = local_x_min + (intersection.length - total_group_width) / 2
                
                found_spot_x = None
                search_offset = 0
                while search_offset < intersection.length / 2:
                    for sign in [1, -1]:
                        if sign == -1 and search_offset == 0: continue
                        
                        test_x = ideal_x + (search_offset * sign)
                        group_box = box(test_x, ideal_y, test_x + total_group_width, ideal_y + set_height)
                        
                        if not any(group_box.intersects(box(*b)) for b in doc.placed_bboxes):
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
                        _place_single_set(current_set_x, ideal_y, doc)
                        placed_sets += 1
                    print(f"\n-> Finished Corian Table Set Placement: Placed {placed_sets} of {num_sets} requested sets.")
                else:
                    doc.skip = True
                    print("SKIP DOC")
                    print(f"⚠️ FAILED: Could not find a clear horizontal spot for the Corian sets at y={ideal_y:.0f}.")
            else:
                doc.skip = True
                print("SKIP DOC")
                print(f"⚠️ FAILED: Could not determine a valid Y-level for Corian Table Sets after all strategies.")

    # touched
    def _get_top_retail_boundary_y(self) -> float:
        """
        Finds the lowest Y-coordinate of all non-retail fixtures (clinics, BOH)
        to determine the top boundary of the retail area.
        """

        # Query for all fixtures that define the back-of-house area
        non_retail_entities = [
            e for e in self.docs[0].msp.query('INSERT') if
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

    # touched
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

    # touched
    def place_tv_screens(self, primary_side: str = "left"):
        """
        Places TV screens using a hybrid strategy.
        - The first two TVs use a multi-spot priority search.
        - Subsequent TVs are stacked using a resilient downward search.
        """

        print("\n--- 🧠 Placing TV Screens with Hybrid Priority/Stacking Strategy ---")
        
        try:
            screen_config = self.fixtures.get("screen_fixtures", {})
            screens_to_place_arr = collections.deque([
                Fixture.Fixture(name, self.fixture_dict[name]["path"])
                for name, count in screen_config.items() if count > 0
                for _ in range(count)
            ])
            if not screens_to_place_arr:
                print("  -> SKIPPED: No screen fixtures specified.")
                return
        except Exception as e:
            print(f"  -> 🔥 ERROR: Could not load screen fixtures: {e}")
            return

        placed_tv_count = 0
        last_tv_details = None 
        euro_spot_used = False

        for doc in self.docs:
            if doc.skip:
                continue

            print (f" ----> placing doc {doc.ind}")

            screens_to_place = copy.deepcopy(screens_to_place_arr)

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
                    add_spot(self._find_spot_above_first_euro(doc), "On First Euro Centre Row")
                    add_spot(self._find_spot_stacked_above_euros(doc, screen), "Stacked Above Euro Row")

                    # --- ADD THESE LINES BACK IN HERE ---
                    add_spot(self._find_bottom_wall_corner_spot(primary_side, screen), f"Bottom-{primary_side} Corner")
                    add_spot(self._find_spot_between_euros(doc), "Between Euro Centres")
                    add_spot(self._find_other_long_wall_spots([primary_side, secondary_side], screen)[0] if self._find_other_long_wall_spots([primary_side, secondary_side], screen) else None, "Center of Fallback Wall")
                    # --- END OF ADDITION ---
                    for i, spot in enumerate(prime_spots):
                        force_placement = (spot["description"] == "On First Euro Centre Row" and not euro_spot_used)
                        validation_bboxes = [b for b in doc.placed_bboxes if "ignore_bbox" not in spot or b != spot["ignore_bbox"]]
                        new_bbox = self._validate_and_place_at_point_tv(doc, screen, spot["target_center"], spot["angle_deg"], validation_bboxes, force=force_placement)
                        
                        if new_bbox:
                            doc.placed_bboxes.append(new_bbox)
                            print(f"    ✅ Placed TV #{placed_tv_count + 1} in spot: {spot['description']}.")
                            is_placed = True
                            placed_tv_count += 1
                            last_tv_details = {"bbox": new_bbox, "center": spot["target_center"]}
                            if force_placement: euro_spot_used = True
                            break

                # --- STRATEGY 2: Call the dedicated stacking function ---
                else:
                    is_placed, new_details = self._place_stacked_tv(doc, screen, doc.placed_bboxes, last_tv_details, placed_tv_count)
                    if is_placed:
                        placed_tv_count += 1
                        last_tv_details = new_details # Update the anchor for the *next* stacked TV
                
                if not is_placed:
                    print(f"    -> ⚠️ Could not place TV #{placed_tv_count + 1}; no suitable spots found.")

            print(f"\n-> Finished TV Placement: Placed {placed_tv_count} screen(s).")


    # touched
    def _find_bottom_wall_corner_spot(self, side: str, screen: 'Fixture') -> Optional[Tuple[Vec2, float]]:
        """Finds a spot inset from a corner of the bottom wall, flush against it."""
        
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
    
    # touched
    def _find_spot_above_first_euro(self, doc) -> Optional[dict]:
        """
        Finds a spot centered ON the entire first row of Euro Centre fixtures.
        Returns a dictionary with the target center and the bounding box of the entire row to ignore.
        """

        all_euro_entities = [e for e in doc.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
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
    
    # touched
    def _place_stacked_tv(self, doc, screen: 'Fixture', placed_bboxes: List[tuple], last_tv_details: dict, placed_tv_count: int):
        """
        Handles the resilient stacking logic for the 3rd TV and onwards.
        Searches downwards from an ideal gap until a valid spot is found.
        Returns a tuple: (was_placed_boolean, updated_last_tv_details_dict).
        """

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
            new_bbox = self._validate_and_place_at_point_tv(doc, screen, target_center, 0.0, placed_bboxes)
            
            if new_bbox:
                doc.placed_bboxes.append(new_bbox)
                print(f"    ✅ Placed TV #{placed_tv_count + 1} using stacking logic at y={current_y:.0f}.")
                new_details = {"bbox": new_bbox, "center": target_center}
                return True, new_details # Return success and the new details
            
            current_y += search_step
        
        return False, None # Return failure
    
    # touched
    def _find_spot_stacked_above_euros(self, doc, screen: 'Fixture', gap: float = 800.0) -> Optional[dict]:
        """
        Finds a spot for a TV screen a specific 'gap' distance above the first row of Euro Centres.
        This creates a vertically stacked placement opportunity.
        """

        all_euro_entities = [e for e in doc.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
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
    
    # touched
    def _find_spot_between_euros(self, doc) -> Optional[Tuple[Vec2, float]]:
        """Finds a spot in the vertical gap between the first two Euro Centres."""
        euro_entities = [e for e in doc.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
        if len(euro_entities) < 2: return None

        euro_bboxes = sorted([extents([e]) for e in euro_entities], key=lambda b: b.extmin.y)
        
        gap_center_y = (euro_bboxes[0].extmax.y + euro_bboxes[1].extmin.y) / 2.0
        center_x = (self.cvc.min_x + self.cvc.max_x) / 2.0
        
        target_center = Vec2(center_x, gap_center_y)
        return (target_center, 0.0)

    # touched
    def _find_other_long_wall_spots(self, sides_to_exclude: List[str], screen: 'Fixture') -> List[Tuple[Vec2, float]]:
        """Finds the center of any long wall that is not on an excluded side, flush against it."""
        
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
    
    # touched
    def _validate_and_place_at_point_tv(self, doc, fixture, target_center, angle_deg, placed_bboxes, force=False):
        """
        Validates and places a fixture. On success, it returns the new bounding box tuple.
        On failure, it returns None.
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
        #--RASHEEQUE-EDITED-THE-LINE-04/12/2025--
        fixture_bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)

        if force:
            is_inside = True
            is_overlapping = False
        else:
            is_inside = self.floorplan_polygon.contains(fixture_polygon.centroid)
            # is_overlapping = any(aabb.has_intersection(BoundingBox2d([Vec2(b[0], b[1]), Vec2(b[2], b[3])])) for b in placed_bboxes)
            #--RASHEEQUE-EDITED-THE-LINE-04/12/2025--
            is_overlapping = self._is_overlapping_raw(fixture_bbox_tuple, placed_bboxes)

        if is_inside and not is_overlapping:
            rotated_offset = local_center.rotate(math.radians(angle_deg))
            final_insert_point = target_center - rotated_offset
            doc.place_fixture(fixture, (final_insert_point.x, final_insert_point.y, 0), angle_deg, True)
            
            # new_bbox_tuple = (aabb.extmin.x, aabb.extmin.y, aabb.extmax.x, aabb.extmax.y)
            # --- THIS LINE IS REMOVED ---
            # placed_bboxes.append(new_bbox_tuple) 
            # return new_bbox_tuple # Return the bbox on success
            #--RASHEEQUE-EDITED-THE-LINE-04/12/2025--
            return fixture_bbox_tuple
            
        return None # Return None on failuree

    # touched
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
        # print(f"  -> Facade center X-coordinate correctly calculated at: {facade_center_x:.0f}")
        return facade_center_x


    #---RASHEEQUE--EDITTED---THIS--FUNCTION--ON--11/11/2025
    def place_qms_at_entrance_center(self):
        """
        [MODIFIED] Places QMS desks based on the Euro Centre placement.
        - Applies resilient horizontal search for BOTH 0 and 90 degree modes.
        - Applies user-specified offsets and scales at the final placement step.
        """

        # 1. SETUP (Same as before)
        config = self.fixtures.get("table_fixtures", {})
        qms_count = config.get("QMS_desk", 0)
        if qms_count <= 0:
            return
        print(f"\n--- Attempting to place {qms_count} QMS Desk(s) [Euro-Dependent Strategy] ---")
        try:
            qms_fxtr = Fixture.Fixture("QMS_desk", self.fixture_dict["QMS_desk"]["path"])
        except Exception as e:
            print(f"🔥 Could not load QMS_desk fixture: {e}")
            return

        # 2. CALCULATE SHARED VALUES
        bottom_margin = self._calculate_dynamic_qms_margin()
        start_y_base = self.cvc.min_y + bottom_margin
        facade_center_x = self._get_facade_center_x()
        
        print(f"  -> Anchoring to bottom wall. Dynamic Y-margin starts at: {start_y_base:.0f}")
        print(f"  -> Facade Center X: {facade_center_x:.0f}")

        # 3. HELPER FUNCTION (Same as before)
        def is_valid_spot_rotated(fixture_obj, x, y, rotation, placed_bboxes):
            # Calculate polygon for the *rotated* fixture
            w, h = (fixture_obj.width, fixture_obj.height)
            center_x, center_y = (x + w/2, y + h/2) # Simple center
            
            if rotation == 90.0:
                w, h = (fixture_obj.height, fixture_obj.width)
                center_x, center_y = (x + w/2, y + h/2) # Center of rotated box

            try:
                # Use the robust transform method for validation
                transform = Matrix44.chain(
                    Matrix44.translate(-fixture_obj.bounding_box.center.x, -fixture_obj.bounding_box.center.y, 0),
                    Matrix44.z_rotate(math.radians(rotation)),
                    Matrix44.translate(center_x, center_y, 0)
                )
                world_corners = list(transform.transform_vertices(fixture_obj.bounding_box.rect_vertices()))
                qms_polygon = Polygon([(p.x, p.y) for p in world_corners])
            except Exception:
                # Fallback to simple box if transform fails
                qms_polygon = box(x, y, x + w, y + h)

            is_overlapping = any(qms_polygon.intersects(box(*bbox)) for bbox in placed_bboxes)
            is_inside = self.floorplan_polygon.contains(qms_polygon)
            return is_inside and not is_overlapping

        # 4. PER-DOCUMENT PLACEMENT LOGIC
        for doc in self.docs:
            if doc.skip:
                continue
            
            print(f" \t ----> attempting QMS placement for plan {doc.ind}")
            
            # --- Read Euro rotation and set QMS parameters ---
            euro_rotation = getattr(doc, 'euro_placement_rotation', 0.0)
            
            qms_rotation = 0.0
            qms_width = qms_fxtr.width
            qms_height = qms_fxtr.height
            qms_is_rotated = False
            final_start_x = 0
            first_desk_placed = False

            # Use math.isclose to handle floating point imprecision
            if math.isclose(euro_rotation, 90.0, abs_tol=0.1):
                # --- STRATEGY A: Column-wise Euros (90°) ---
                print("  -> Strategy: Column-wise (90°). Placing QMS at 90° with resilient horizontal search.")
                qms_rotation = 90.0
                qms_width = qms_fxtr.height # Flipped dimensions
                qms_height = qms_fxtr.width
                qms_is_rotated = True
                
                ideal_x = facade_center_x - (qms_width / 2) # Uses flipped qms_width
            
            else:
                # --- STRATEGY B: Row-wise Euros (0°) ---
                print("  -> Strategy: Row-wise (0°). Placing QMS at 0° with resilient horizontal search.")
                # qms_rotation, qms_width, qms_height, qms_is_rotated are already 0/False
                ideal_x = facade_center_x - (qms_width / 2) # Uses standard qms_width

            # --- COMMON RESILIENT SEARCH LOGIC ---
            start_y = start_y_base
            search_offset = 0
            max_search = (self.cvc.max_x - self.cvc.min_x) / 2

            while not first_desk_placed and search_offset < max_search:
                for sign in [1, -1]:
                    if sign == -1 and search_offset == 0: continue
                    test_x = ideal_x + search_offset * sign
                    # Check using the correct rotation for this strategy
                    if is_valid_spot_rotated(qms_fxtr, test_x, start_y, qms_rotation, doc.placed_bboxes):
                        final_start_x = test_x
                        first_desk_placed = True
                        break
                if first_desk_placed: break
                search_offset += 100

            if not first_desk_placed:
                print(f"⚠️ {qms_rotation}-degree: Could not find a clear spot for the QMS desk near center ({ideal_x:.0f}). SKIPPING.")
                doc.skip = True
                print("SKIP DOC")
                continue
            
            # 5. EXECUTE PLACEMENT (Center-Out Pattern for all strategies)
            qms_placed_count = 0
            placed_qms_bboxes = [] # BBoxes for this doc's newly placed desks
            start_y = start_y_base # Re-confirm Y position

            # ******************************************************
            # ******** MODIFICATION IS HERE ********
            # Apply user-requested offsets and scales
            # ******************************************************
            insert_x = final_start_x
            insert_y = start_y
            xscale = -1.0
            yscale = -1.0
            
            # if euro_rotation == 90.0:
            # Use math.isclose to handle floating point imprecision
            if math.isclose(euro_rotation, 90.0, abs_tol=0.1):
                insert_x = final_start_x - 600
                insert_y = start_y + 450
                print(f"    -> Applying 90-deg offset/scale. Insert: ({insert_x:.0f}, {insert_y:.0f})")
            else: # 0-degree rotation
                insert_x = final_start_x + 450
                insert_y = start_y + 450
                print(f"    -> Applying 0-deg offset/scale. Insert: ({insert_x:.0f}, {insert_y:.0f})")

            # Place the first desk with offsets and scales
            doc.place_fixture(qms_fxtr, (insert_x, insert_y, 0), qms_rotation, qms_is_rotated, xscale=xscale, yscale=yscale)
            
            # The bounding box MUST use the original (un-offset) coordinates from validation
            bbox_coords = (final_start_x, start_y, final_start_x + qms_width, start_y + qms_height)
            doc.placed_bboxes.append(bbox_coords)
            # ******************************************************
            # ******** END OF MODIFICATION ********
            # ******************************************************
            
            placed_qms_bboxes.append(bbox_coords)
            qms_placed_count += 1
            print(f"✅ Placed central {qms_rotation}-degree QMS_desk at ({final_start_x:.0f}, {start_y:.0f}).")
            
            # Place additional desks
            if qms_count > 1:
                max_gap, min_gap, congestion_threshold = 500, 250, 5
                gap_horizontal = max_gap # (This logic remains the same)
                
                leftmost_bbox = placed_qms_bboxes[0]
                rightmost_bbox = placed_qms_bboxes[0]

                for i in range(qms_count - 1):
                    if i % 2 == 0: # Place to the left
                        target_x = leftmost_bbox[0] - gap_horizontal - qms_width
                        if is_valid_spot_rotated(qms_fxtr, target_x, start_y, qms_rotation, doc.placed_bboxes):
                            
                            # ******************************************************
                            # Apply offsets to the found 'target_x'
                            # if euro_rotation == 90.0:
                            # Use math.isclose to handle floating point imprecision
                            if math.isclose(euro_rotation, 90.0, abs_tol=0.1):
                                insert_x = target_x - 600
                                insert_y = start_y + 450
                            else: # 0-degree rotation
                                insert_x = target_x + 450
                                insert_y = start_y + 450
                            
                            doc.place_fixture(qms_fxtr, (insert_x, insert_y, 0), qms_rotation, qms_is_rotated, xscale=xscale, yscale=yscale)
                            # Bounding box still uses the geometric target_x
                            new_bbox = (target_x, start_y, target_x + qms_width, start_y + qms_height)
                            # ******************************************************
                            
                            doc.placed_bboxes.append(new_bbox); leftmost_bbox = new_bbox; qms_placed_count += 1
                            print(f"✅ Placed QMS_desk #{qms_placed_count} to the left.")
                        else:
                            print("⚠️ Spot to the left is blocked.")
                    else: # Place to the right
                        target_x = rightmost_bbox[2] + gap_horizontal
                        if is_valid_spot_rotated(qms_fxtr, target_x, start_y, qms_rotation, doc.placed_bboxes):
                            
                            # ******************************************************
                            # Apply offsets to the found 'target_x'
                            if math.isclose(euro_rotation, 90.0, abs_tol=0.1):
                            
                                insert_x = target_x - 600
                                insert_y = start_y + 450
                            else: # 0-degree rotation
                                insert_x = target_x + 450
                                insert_y = start_y + 450
                                
                            doc.place_fixture(qms_fxtr, (insert_x, insert_y, 0), qms_rotation, qms_is_rotated, xscale=xscale, yscale=yscale)
                            # Bounding box still uses the geometric target_x
                            new_bbox = (target_x, start_y, target_x + qms_width, start_y + qms_height)
                            # ******************************************************

                            doc.placed_bboxes.append(new_bbox); rightmost_bbox = new_bbox; qms_placed_count += 1
                            print(f"✅ Placed QMS_desk #{qms_placed_count} to the right.")
                        else:
                            print("⚠️ Spot to the right is blocked.")
            
            print(f"-> Finished: Placed {qms_placed_count} of {qms_count} QMS desks for this doc.")



    # touched
    def place_door(self, primary_side):
        """
        Places the door in the middle of the facade with the opening based on the primary_side
        """
        if primary_side == "left":
            door_fx = Fixture.Fixture("Door", self.fixture_dict["Door_Left"]["path"])
        else:
            door_fx = Fixture.Fixture("Door", self.fixture_dict["Door_Right"]["path"])

        for doc in self.docs:
            if doc.skip:
                continue

            print (f" ----> placing doc {doc.ind}")
            facade_center_x = self._get_facade_center_x() - door_fx.width/2
            start_y = self.cvc.min_y - 105/2

            doc.place_fixture(door_fx, (facade_center_x, start_y), 0, False)
            print(f"✅ Placed Door at ({facade_center_x:.0f}, {start_y:.0f}) in plan {doc.ind}.")

    # touched
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

    # touched
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

    # touched
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

    # touched
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

    # touched
    def place_standing_tables_landscape(self, placed_bboxes):
        """
        Main dispatcher for placing Standing Tables. It intelligently determines the
        anchor point, creates multiple columns as needed, and then calls the
        appropriate odd/even count placement strategy for each column.
        """
        
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

    # touched
    def _place_standing_tables_center_out(self, tables_to_place, standing_fxtr, placed_bboxes, start_x):
        """
        Fills a SINGLE column with tables, stacking center-out.
        Returns any tables that could not be placed.
        """

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

    # touched
    def _place_standing_tables_discussion_anchored(self, tables_to_place, standing_fxtr, placed_bboxes, start_x):
        """
        Fills a SINGLE column with an EVEN number of tables, using top/bottom anchors.
        If anchors are not found, it defaults to the center-out strategy.
        Returns any tables that could not be placed.
        """

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

    # touched
    def place_blue_zero_landscape(self, placed_bboxes):
        """
        Places Blue_zero fixtures in landscape mode using a two-phase "snaking"
        pattern. It first exhausts all Discussion Table spots from left to right,
        then places any remaining fixtures next to Euro Centres.
        """

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

    # touched
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

        for i, doc in enumerate(self.docs):
            if not doc.skip:
                doc.close_plan(self.dxf_out)

















########################################################################################################################
########################################################################################################################
########################################     STANDING TABLE NEW ALGORITHM STARTS  ######################################
########################################     STANDING TABLE NEW ALGORITHM STARTS  ######################################
########################################     STANDING TABLE NEW ALGORITHM STARTS  ######################################
########################################################################################################################
########################################################################################################################

    def get_placed_details(self, doc: dxf_doc.DXF_Document) -> List[Dict[str, Any]]:
            """
            Finds all placed floor fixtures (clinics, benches, euros, etc.) and
            returns a detailed list of their true, oriented geometry using
            get_outer_rect_corners_shapely().

            Args:
                doc: The DXF_Document object to analyze.

            Returns:
                A list of dictionaries, where each dictionary contains the
                details for one placed fixture.
                
                Example format:
                [
                    {
                        'name': 'CLINIC_REGULAR_1',
                        'entity': <Insert entity>,
                        'bbox': (min_x, min_y, max_x, max_y),
                        'segments': {
                            'bottom_segment': (<Vec2>, <Vec2>),
                            'right_segment': (<Vec2>, <Vec2>),
                            'top_segment': (<Vec2>, <Vec2>),
                            'left_segment': (<Vec2>, <Vec2>)
                        },
                        'corners_wcs': [(x,y), (x,y), (x,y), (x,y)]
                    },
                    ...
                ]
            """
            print(f"\n--- 🔎 Getting placed fixture details for Doc {doc.ind} ---")
            
            all_details = []
            
            # --- 1. Get all INSERT entities ---
            all_inserts = doc.msp.query('INSERT')
            
            for entity in all_inserts:
                block_name_upper = entity.dxf.name.upper()
                
                # --- 2. Filter to find matching fixture type ---
                best_match_key = ""
                for key in self.fixture_dict.keys():
                    sanitized_key = key.upper().replace(" ", "_")
                    if block_name_upper.startswith(sanitized_key):
                        if len(key) > len(best_match_key):
                            best_match_key = key
                
                if not best_match_key:
                    continue # Not a recognized fixture
                    
                fixture_type = self.fixture_dict[best_match_key].get("type")
                
                # --- 3. Only process "floor" fixtures, not wall/screen fixtures ---
                # We explicitly include types that are placed on the floor
                valid_types = {'clinic', 'boh_preset', 'floor', 'loose', 'pos', 'table_fixtures'}
                # valid_types = {'clinic', 'boh_preset', 'floor', 'loose', 'pos', 'table_fixtures', 'boh','boh_fixtures'}
                if fixture_type not in valid_types and 'table' not in best_match_key.lower():
                    continue

                print(f"  -> Processing: {entity.dxf.name} (Type: {fixture_type})")

                try:
                    # --- 4. Use get_outer_rect_corners_shapely() ---
                    # This returns 4 (x, y, z) tuples in CCW order
                    corners_tuples = self.get_outer_rect_corners_shapely(entity)
                    
                    if len(corners_tuples) < 4:
                        print(f"    -> WARNING: Could not get corners for {entity.dxf.name}. Skipping.")
                        continue

                    # Convert to 2D Vec2 objects for easier use
                    corners_xy = [(c[0], c[1]) for c in corners_tuples]
                    corners_vecs = [Vec2(c[0], c[1]) for c in corners_xy]
                    
                    # --- 5. Calculate AABB (Axis-Aligned Bounding Box) ---
                    min_x = min(c[0] for c in corners_xy)
                    min_y = min(c[1] for c in corners_xy)
                    max_x = max(c[0] for c in corners_xy)
                    max_y = max(c[1] for c in corners_xy)
                    bbox_tuple = (min_x, min_y, max_x, max_y)

                    # --- 6. Define the 4 oriented segments ---
                    c1, c2, c3, c4 = corners_vecs[0], corners_vecs[1], corners_vecs[2], corners_vecs[3]
                    
                    # Segments are defined with parallel, same-direction vectors
                    segments = {
                        'bottom_segment': (c1, c2),  # Vector: c2 - c1
                        'right_segment': (c2, c3),   # Vector: c3 - c2
                        'top_segment': (c4, c3),     # Vector: c3 - c4
                        'left_segment': (c1, c4)    # Vector: c4 - c1
                    }

                    # --- 7. Append all details to the list ---
                    all_details.append({
                        'name': entity.dxf.name,
                        'entity': entity,
                        'bbox': bbox_tuple,
                        'segments': segments,
                        'corners_wcs': corners_xy # The 4 corners as (x,y) tuples
                    })
                    
                except Exception as e:
                    print(f"    -> ⚠️ ERROR processing {entity.dxf.name}: {e}")
                    continue

            print(f"  -> ✅ Found details for {len(all_details)} placed floor fixtures.")
            return all_details

    def analyze_and_print_all_document_details(self, debug: bool = False):
        """
        If debug=True, iterates through all generated documents, calls
        get_placed_details(), prints a detailed analysis, AND
        draws the colored, oriented bounding boxes for each fixture.
        """
        if not debug:
            return  # Do nothing if debug is False

        print("\n" + "="*50)
        print(f"ANALYZING ALL {len(self.docs)} DOCUMENT VARIANTS")
        print("="*50)

        # --- [NEW] Define color and layer mappings ---
        LAYER_MAP = {
            'CLINIC': 'DEBUG_BBOX_CLINIC',
            'STANDING_TABLE': 'DEBUG_BBOX_TABLE',
            'BENCH': 'DEBUG_BBOX_BENCH',
            'QMS_DESK': 'DEBUG_BBOX_QMS',
            'EURO_CENTRE': 'DEBUG_BBOX_EURO',
            'DEFAULT': 'DEBUG_BBOX_OTHER'
        }
        COLOR_MAP = {
            'CLINIC': 4,  # Cyan
            'STANDING_TABLE': 3,  # Green
            'BENCH': 1,  # Red
            'QMS_DESK': 6,  # Magenta
            'EURO_CENTRE': 2, # Yellow
            'DEFAULT': 5   # Blue
        }
        # --- [END NEW] ---

        for doc in self.docs:
            if doc.skip:
                print(f"\n--- Document {doc.ind}: SKIPPED (No valid placement found) ---")
                continue

            print(f"\n--- Document {doc.ind}: All Placed Fixture Details ---")
            
            # Call the get_placed_details function for the current doc
            all_fixture_details = self.get_placed_details(doc)

            if not all_fixture_details:
                print("  -> No placed fixtures found in this document.")
                continue

            # --- [NEW] Visualization Loop ---
            # Ensure all debug layers exist
            for layer_name, color in zip(LAYER_MAP.values(), COLOR_MAP.values()):
                if layer_name not in doc.doc.layers:
                    doc.doc.layers.add(name=layer_name, color=color)

            for detail in all_fixture_details:
                name_upper = detail['name'].upper()
                
                # Determine the correct type for color/layer
                fixture_type = 'DEFAULT'
                if 'CLINIC' in name_upper:
                    fixture_type = 'CLINIC'
                elif 'STANDING_TABLE' in name_upper:
                    fixture_type = 'STANDING_TABLE'
                elif 'BENCH' in name_upper:
                    fixture_type = 'BENCH'
                elif 'QMS_DESK' in name_upper:
                    fixture_type = 'QMS_DESK'
                elif 'EURO_CENTRE' in name_upper:
                    fixture_type = 'EURO_CENTRE'
                
                layer_to_use = LAYER_MAP[fixture_type]
                color_to_use = COLOR_MAP[fixture_type]
                
                # Get the 4 oriented corners from get_placed_details
                corners = detail.get('corners_wcs')
                if not corners or len(corners) < 4:
                    continue
                    
                # Draw the oriented bounding box as a closed polyline
                doc.msp.add_lwpolyline(
                    points=corners,
                    close=True,
                    dxfattribs={
                        'layer': layer_to_use,
                        'color': color_to_use  # Set color explicitly
                    }
                )
            print(f"  -> Drawn {len(all_fixture_details)} debug bounding boxes on 'DEBUG_BBOX_*' layers.")
            # --- [END NEW] Visualization Loop ---


            # --- Print Loop (Original logic) ---
            for i, detail in enumerate(all_fixture_details):
                print(f"\n  Fixture #{i+1}: {detail['name']}")
                print(f"    BBox: {detail['bbox']}")
                
                bottom_seg = detail['segments']['bottom_segment']
                right_seg = detail['segments']['right_segment']
                
                print(f"    Bottom Edge Length: {bottom_seg[0].distance(bottom_seg[1]):.0f} mm")
                print(f"    Right Edge Length: {right_seg[0].distance(right_seg[1]):.0f} mm")
                print(f"    Right Edge Segments: {right_seg}")

        print("="*50)
        print("ANALYSIS COMPLETE")
        print("="*50 + "\n")
   
    
    def get_horizontal_debug_line_at_y(self, 
                                        y_coordinate: float, 
                                        debug: bool = False, 
                                        layer_name: str = "DEBUG_Y_COORDINATE_LINE", 
                                        color: int = 1) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """
        Calculates a horizontal line at a specific Y-coordinate, clipped
        to the floorplan's boundaries.
        
        If debug=True, it ALSO draws the line.
        
        It ALWAYS returns a list of (start, end) coordinate tuples.
        """
        
        segment_details = []

        # --- STEP 1: ALWAYS CALCULATE THE SEGMENTS ---
        print(f"\n--- 🎨 Calculating horizontal line at y={y_coordinate} ---")

        if not hasattr(self, 'floorplan_polygon') or self.floorplan_polygon.is_empty:
            print("  -> ⚠️ FAILED: Floorplan polygon not found. Cannot calculate line.")
            return segment_details # Return an empty list

        try:
            # 1. Create a very wide horizontal "slicer" line
            slicer_line = LineString([
                (self.cvc.min_x - 1000, y_coordinate), 
                (self.cvc.max_x + 1000, y_coordinate)
            ])

            # 2. Find all parts of that line that are "inside the floorplan"
            intersection_geom = self.floorplan_polygon.intersection(slicer_line)

            if intersection_geom.is_empty:
                print("  -> ⚠️ Line does not intersect the floorplan.")
                return segment_details # Return an empty list

            # 3. Extract coordinates and store them
            if intersection_geom.geom_type == 'LineString':
                start, end = intersection_geom.coords[0], intersection_geom.coords[-1]
                segment_details.append((start, end))
            elif intersection_geom.geom_type == 'MultiLineString':
                for line in intersection_geom.geoms:
                    start, end = line.coords[0], line.coords[-1]
                    segment_details.append((start, end))
            
            print(f"  -> ✅ Successfully calculated {len(segment_details)} segment(s).")

        except Exception as e:
            print(f"  -> ⚠️ FAILED to calculate debug line: {e}")
            return [] # Return an empty list on failure

        # --- STEP 2: ONLY DRAW IF DEBUG IS TRUE ---
        if debug:
            print(f"  -> 🎨 Drawing debug line on layer '{layer_name}'...")
            drawn_on_docs = 0
            for doc in self.docs:
                if doc.skip:
                    continue
                
                # Ensure the layer exists
                if layer_name not in doc.doc.layers:
                    doc.doc.layers.add(name=layer_name, color=color)

                # Draw each segment that we just stored
                for start, end in segment_details:
                    doc.msp.add_line(start, end, dxfattribs={'layer': layer_name, 'color': color})
                
                drawn_on_docs += 1
            
            print(f"  -> ✅ Successfully drew on {drawn_on_docs} document(s).")
        
        # --- STEP 3: ALWAYS RETURN THE CALCULATED DETAILS ---
        return segment_details


    def get_exact_standing_table_width(self, 
                                       doc: dxf_doc.DXF_Document, 
                                       y_coordinate: float, 
                                       debug: bool = False) -> Dict[str, Any]:
        """
        Calculates the exact, available horizontal segments at a specific 
        Y-coordinate by trimming them against all placed fixtures.

        This function:
        1. Gets the raw horizontal segments from get_horizontal_debug_line_at_y().
        2. Gets the bounding boxes of all placed fixtures using get_placed_details().
        3. "Cuts" the raw segments with any fixture that overlaps that Y-level.
        4. Returns a dictionary of the final, trimmed segments.
        5. If debug=True, draws the final trimmed segments.

        Args:
            doc: The DXF_Document object to analyze.
            y_coordinate: The Y-level to slice at.
            debug: If True, draws the final segments.

        Returns:
            A dictionary with the Y-coordinate and a list of segment details.
            Example:
            {
                'y_coordinate': 6000.0,
                'segments': [
                    {'start': (x1, y), 'end': (x2, y), 'length': 1200.0},
                    {'start': (x3, y), 'end': (x4, y), 'length': 850.5}
                ]
            }
        """
        
        print(f"\n--- 📏 Calculating Exact Available Width at Y={y_coordinate} ---")

        # --- Step 1: Get the base horizontal line(s) inside the floorplan ---
        # We call this with debug=False because we only want the data,
        # not the drawing from that function.
        base_segments_coords = self.get_horizontal_debug_line_at_y(
            y_coordinate, 
            debug=False
        )
        
        if not base_segments_coords:
            print("  -> No base segments found inside the floorplan at this Y-level.")
            return {'y_coordinate': y_coordinate, 'segments': []}
            
        # Convert raw coordinates to Shapely LineStrings
        base_lines = [LineString(segment) for segment in base_segments_coords]
        base_multiline = MultiLineString(base_lines)

        # --- Step 2: Get all placed fixtures (our obstacles) ---
        all_fixture_details = self.get_placed_details(doc)

        # --- Step 3: Find all obstacles that intersect this Y-coordinate ---
        obstacle_polygons = []
        for detail in all_fixture_details:
            min_x, min_y, max_x, max_y = detail['bbox']
            
            # Check if the fixture's bounding box crosses our Y-coordinate
            if min_y <= y_coordinate <= max_y:
                # This fixture is an obstacle at this Y-level.
                # We create a box from its axis-aligned bounding box.
                obstacle_polygons.append(box(min_x, min_y, max_x, max_y))
        
        if not obstacle_polygons:
            print("  -> No obstacles found at this Y-level. Segments are clear.")
            # If no obstacles, we can just use the base segments.
        else:
            print(f"  -> Found {len(obstacle_polygons)} obstacles to trim against.")
        
        # --- Step 4: Trim the base lines with the obstacles ---
        final_trimmed_segments = []
        if obstacle_polygons:
            # Combine all obstacles into one single shape for efficiency
            all_obstacles_union = unary_union(obstacle_polygons)
            
            # Use .difference() to "cut" the lines
            trimmed_geom = base_multiline.difference(all_obstacles_union)
            
            # The result could be one line or many lines
            if trimmed_geom.is_empty:
                pass # No segments remain
            elif trimmed_geom.geom_type == 'LineString':
                final_trimmed_segments.append(trimmed_geom)
            elif trimmed_geom.geom_type == 'MultiLineString':
                final_trimmed_segments.extend(list(trimmed_geom.geoms))
        else:
            # No obstacles, so the final segments are just the base lines
            final_trimmed_segments = base_lines

        # --- Step 5: Format the output and optionally draw debug lines ---
        result_data = {'y_coordinate': y_coordinate, 'segments': []}
        layer_name = "DEBUG_TRIMMED_WIDTHS"
        color = 1  # Green
        
        if debug and final_trimmed_segments:
            if layer_name not in doc.doc.layers:
                doc.doc.layers.add(name=layer_name, color=color)

        for line in final_trimmed_segments:
            # Filter out tiny slivers that are not useful
            if line.length < 50: 
                continue

            start_coords = line.coords[0]
            end_coords = line.coords[-1]
            
            # Ensure start is always on the left
            s, e = (start_coords, end_coords) if start_coords[0] < end_coords[0] else (end_coords, start_coords)

            segment_detail = {
                'start': (round(s[0], 2), round(s[1], 2)),
                'end': (round(e[0], 2), round(e[1], 2)),
                'length': round(line.length, 2)
            }
            result_data['segments'].append(segment_detail)
            
            # Draw if debug is enabled
            if debug:
                doc.msp.add_line(
                    s, 
                    e, 
                    dxfattribs={'layer': layer_name, 'color': color, 'lineweight': 70}
                )

        if debug:
            print(f"  -> Drawn {len(result_data['segments'])} final trimmed segments on layer '{layer_name}'.")
        
        print(f"  -> ✅ Calculation complete. Found {len(result_data['segments'])} available segments.")
        return result_data


    def analyze_standing_table_widths_all_docs(self, y_coordinate: float, debug: bool = False):
        """
        Runs the 'get_exact_standing_table_width' analysis for a specific
        Y-coordinate across ALL active documents and prints the results.
        """
        if not debug:
            return # Skip this entire analysis if debug is off

        print("\n" + "="*50)
        print(f"ANALYZING EXACT STANDING TABLE WIDTHS AT Y={y_coordinate}")
        print("="*50)

        for doc in self.docs:
            if doc.skip:
                print(f"\n--- Skipping Doc {doc.ind} (marked as skip) ---")
                continue
                
            print(f"\n--- Analyzing Doc {doc.ind} for available width ---")
            
            # Call the function for this specific doc
            available_width_data = self.get_exact_standing_table_width(
                doc, 
                y_coordinate=y_coordinate, 
                debug=debug # Pass the debug flag to draw the lines
            )
            
            # Print the results
            print(json.dumps(available_width_data, indent=2))

        print("="*50)
        print("WIDTH ANALYSIS COMPLETE")
        print("="*50 + "\n")

    def _find_overlapping_segments(self, top_segments_data: dict, bottom_segments_data: dict) -> List[dict]:
        """
        [NEW HELPER] Compares segments from two Y-levels and returns a new
        list of segments representing the shared, overlapping X-spans.
        """
        common_segments = []
        top_segments = top_segments_data.get('segments', [])
        bottom_segments = bottom_segments_data.get('segments', [])

        if not top_segments or not bottom_segments:
            return [] # No overlap possible if one is empty

        try:
            # Use Y=0 for all lines, we only care about the X-span
            top_lines = [LineString([(s['start'][0], 0), (s['end'][0], 0)]) for s in top_segments]
            bottom_lines = [LineString([(s['start'][0], 0), (s['end'][0], 0)]) for s in bottom_segments]

            # Combine all segments at each level into a single geometry
            top_union = unary_union(top_lines)
            bottom_union = unary_union(bottom_lines)

            # Find the intersection of the two levels
            common_geom = top_union.intersection(bottom_union)
            
            # This is the Y-coordinate of the top of the row, for reference
            reference_y = top_segments_data.get('y_coordinate', 0) 

            if common_geom.is_empty:
                return []
            
            # Collect the resulting common segments
            geoms_to_process = []
            if common_geom.geom_type == 'LineString':
                geoms_to_process.append(common_geom)
            elif common_geom.geom_type == 'MultiLineString':
                geoms_to_process.extend(list(common_geom.geoms))

            for line in geoms_to_process:
                if line.length > 0:
                    start_x = line.coords[0][0]
                    end_x = line.coords[-1][0]
                    # Ensure start_x is always the smaller one
                    if start_x > end_x:
                        start_x, end_x = end_x, start_x
                    
                    # Store the common segment details
                    common_segments.append({
                        'start': (start_x, reference_y), # (start_x, y_top)
                        'end': (end_x, reference_y),   # (end_x, y_top)
                        'length': line.length
                    })
            
            return common_segments
        except Exception as e:
            print(f"  -> ⚠️ ERROR in _find_overlapping_segments: {e}")
            return []



    def plan_and_place_standing_tables_new(self, debug: bool = False):
        """
        [NEW ALGORITHM v3] Places standing tables using a robust row-by-row
        method.
        
        - Starts from the top of the floorplan.
        - Validates width at both the top (y_top) and bottom (y_bottom) of the row.
        - **NEW**: Validates a clear ST_GAP (800mm) *above* y_top before placing.
        - Nudges down until it finds a row that passes all three checks.
        """
        print("\n--- 🧠 Planning Standing Tables (New Top-Down Algorithm v3) ---")

        # --- 1. Constants & Fixture Loading ---
        ST_GAP = 750.0  # Used for aisle, between_ST, vertical_gap, initial_gap
        NUDGE_STEP = 100.0
        
        try:
            config = self.fixtures.get("table_fixtures", {})
            tables_to_place_count = config.get("Standing_table", 0)
            if tables_to_place_count <= 0:
                print("  -> SKIPPED: No Standing_table fixtures required in config.")
                return

            fxtr_obj = Fixture.Fixture("Standing_table", self.fixture_dict["Standing_table"]["path"])
            
            width_ST = 700.0
            height_ST = 600.0
            min_required_width = width_ST + (2 * ST_GAP) # 2300.0
            
            print(f"  -> Loaded {tables_to_place_count} tables to place.")
            print(f"  -> Constants: W={width_ST}, H={height_ST}, Gap/Aisle={ST_GAP}, MinWidth={min_required_width}")

        except Exception as e:
            print(f"  -> ⚠️ FAILED: Could not load Standing_table fixture: {e}")
            return

        # --- Main loop for each document ---
        for doc in self.docs:
            if doc.skip:
                print(f"\n--- Skipping Standing Table placement for Doc {doc.ind} (marked as skip) ---")
                continue
            
            print(f"\n--- 🧠 Planning Standing Tables for Doc {doc.ind} ---")
            
            tables_to_place_queue = collections.deque([fxtr_obj] * tables_to_place_count)

            # --- 2. Get Anchor Y (Top of Floorplan) ---
            if not hasattr(self, 'cvc') or self.cvc.max_y is None:
                print(f"  -> ⚠️ FAILED (Doc {doc.ind}): Floorplan boundaries (cvc.max_y) not found. Cannot anchor.")
                continue

            clinic_horizontal_height = 1700.0
            inset = clinic_horizontal_height
            anchor_y = doc.back_wall_y
            print(f"  -> Anchoring to absolute floorplan top: y={anchor_y:.0f}")

            # --- 3. Initialize Loop ---
            y_cursor = anchor_y - ST_GAP # This is y_top for the *first potential* row
            safety_y_limit = self.cvc.min_y - (height_ST * 2)
            
            # --- [NEW] Get a snapshot of obstacles to check against ---
            
            while tables_to_place_queue:
                if y_cursor < safety_y_limit:
                    print("  -> ⚠️ STOPPING: Y-cursor is below floorplan limit. Aborting.")
                    break
                # We get this once per document for efficiency in the loop
                obstacle_polygons = [box(*b) for b in doc.placed_bboxes]
                split = False
                    
                placed_in_this_pass = False
                
                # --- 4. Get Row Footprint & Gaps ---
                y_top = y_cursor
                y_bottom = y_top - height_ST
                
                print(f"\n  -> Checking row at y_top={y_top:.0f}, y_bottom={y_bottom:.0f}")
                
                top_segments_data = self.get_exact_standing_table_width(doc, y_top, debug=debug)
                bottom_segments_data = self.get_exact_standing_table_width(doc, y_bottom, debug=debug)
                
                common_segments = self._find_overlapping_segments(top_segments_data, bottom_segments_data)
                
                if not common_segments:
                    print("    -> No clear, overlapping segments found at this Y-level.")
                
                # --- 5. Iterate Common Segments ---
                for segment in common_segments:
                    if not tables_to_place_queue: break
                    
                    W = segment['length']
                    print("semgent length: ", W)
                    
                    if W >= min_required_width:
                        print("sufficient width")
                        # --- 6. [NEW VALIDATION] Check for clear gap ABOVE ---
                        is_gap_above_clear = True
                        y_check_above = y_top + ST_GAP
                        seg_start_x = segment['start'][0]
                        seg_end_x = segment['end'][0]
                        
                        # Create a "check box" from the top of the row up to the ST_GAP
                        check_box = box(seg_start_x, y_top, seg_end_x, y_check_above)
                        print("check box: ", check_box)
                        
                        for obstacle in obstacle_polygons:
                            if check_box.intersects(obstacle):
                                split = True
                                # obstacle_polygons.remove(obstacle)
                                minx = obstacle.bounds[0] - 10
                                maxx = obstacle.bounds[2] + 10
                                common_segments.append({
                                                            "start": [seg_start_x, segment["start"][1]],
                                                            "end": [minx, segment["start"][1]],
                                                            "length": minx - seg_start_x
                                                        })
                                common_segments.append({
                                                            "start": [maxx, segment["start"][1]],
                                                            "end": [seg_end_x, segment["start"][1]],
                                                            "length": seg_end_x - maxx
                                                        })
                                is_gap_above_clear = False
                                print(f"    -> REJECTED: Row at y={y_top:.0f} is blocked by an obstacle within {ST_GAP}mm above it.")
                                # break # Stop checking obstacles
                        
                        if not is_gap_above_clear:
                            # print("gap above not clear")
                            continue # Move to the next segment
                        
                        # --- 7. Place Tables (All checks passed) ---
                        print("CHECKS PASSED")
                        valid_width = W - (2 * ST_GAP)
                        n_float = (valid_width + ST_GAP) / (width_ST + ST_GAP)
                        n = math.floor(n_float)
                        
                        if n > 0:
                            n_to_place = min(n, len(tables_to_place_queue))
                            print(f"    -> SUCCESS: Segment at y={y_top:.0f} is clear. Can fit {n} tables. Placing {n_to_place}.")
                            
                            occupied_width = (n_to_place * width_ST) + (ST_GAP * (n_to_place - 1))
                            remaining_space = valid_width - occupied_width
                            left_margin = remaining_space / 2
                            start_x = seg_start_x + ST_GAP + left_margin
                            
                            for i in range(n_to_place):
                                fxtr = tables_to_place_queue.popleft()
                                table_x = start_x + i * (width_ST + ST_GAP)
                                table_y = y_bottom
                                
                                # block_ref = doc.place_fixture(fxtr, (table_x, table_y, 0), 0, False)
                                block_ref = doc.place_fixture(fxtr, (table_x + 700, table_y + 700, 0), 0, False,xscale= -1.0,yscale=-1.0)
                                
                                # Add the new table to our obstacle lists
                                new_bbox_tuple = (table_x, table_y, table_x + width_ST, table_y + height_ST)
                                doc.placed_bboxes.append(new_bbox_tuple)
                                obstacle_polygons.append(box(*new_bbox_tuple)) # Add to our loop's checker
                                
                            placed_in_this_pass = True
                        else:
                            print(f"    -> Segment is valid but cannot fit n=1 table.")
                    else:
                        print(f"    -> Segment width ({W:.0f}mm) is less than min required ({min_required_width:.0f}mm).")

                # --- 8. Update Y-Cursor ---
                if placed_in_this_pass and not split:
                    print(f"  -> Placed tables. Moving to next row...")
                    y_cursor = y_bottom - ST_GAP # Move down a full row
                else:
                    print(f"  -> No valid spots found at this level. Nudging down...")
                    y_cursor = y_top - NUDGE_STEP # Nudge 100mm
            
            if tables_to_place_queue:
                print(f"  -> ⚠️ WARNING (Doc {doc.ind}): Finished loop but {len(tables_to_place_queue)} tables remain unplaced.")
            else:
                print(f"  -> ✅ (Doc {doc.ind}) Successfully placed all required standing tables.")



########################################################################################################################
########################################################################################################################
########################################     STANDING TABLE NEW ALGORITHM ENDS  ########################################
########################################     STANDING TABLE NEW ALGORITHM ENDS  ########################################
########################################     STANDING TABLE NEW ALGORITHM ENDS  ########################################
########################################################################################################################
########################################################################################################################

########################################################################################################################
########################################################################################################################
########################################     STANDING TABLE NEW ALGORITHM SIMILAR TO EURO ##############################
########################################     STANDING TABLE NEW ALGORITHM SIMILAR TO EURO ##############################
########################################     STANDING TABLE NEW ALGORITHM SIMILAR TO EURO ##############################
########################################################################################################################
########################################################################################################################


    def get_standing_table_placement_zone(self, doc, debug: bool = False) -> Optional[Polygon]:
        """
        [NEW ZONE FUNCTION FOR STANDING TABLES - v6 - "CARVE-OUT" METHOD]
        Calculates the total valid area for standing tables by "carving out"
        all anchor fixtures from the main floorplan, matching the user's
        red-line drawing.

        - Top Anchor: This is now a dynamic, complex polygon boundary
                      that follows the bottom edge of all anchor fixtures.
        - Bottom Anchor: (Removed) The zone now extends to the bottom of the
                         available retail space (it is no longer a 3000mm slice).
        - Side Aisles: 800mm.
        - Obstacles: Subtracts all other floor fixtures (Euros, Benches, QMS, etc.).
        """
        print("\n--- 📐 Defining Standing Table Placement Zone (Dynamic Carve-Out v6) ---")

        # --- 1. Define Constants ---
        SIDE_AISLE_GAP = 800.0 + 300.0 # 800mm side aisle + 300mm buffer
        TOP_BOUNDARY_GAP = -200.0 # Gap below clinics/BOH 1050-800 = 250
        BOTTOM_BOUNDARY_THRESHOLD = self._calculate_dynamic_standing_table_threshold(doc, percentage=0.40)#3000.0 # Distance from the bottom of the floorplan
        
        # --- 2. Get All Fixture Details ---
        print("  -> (Step 2) Dynamically finding all fixtures...")
        all_details = self.get_placed_details_ST(doc)
        
        anchor_types = {'clinic', 'boh', 'boh_preset', 'pickup_window'}
        anchor_names = {'BACK_WALL'}
        
        anchor_polygons = []
        other_obstacle_polygons = []

        # --- 3. Sort Fixtures into "Anchors" and "Obstacles" ---
        for detail in all_details:
            block_name_upper = detail['name'].upper()
            
            # Use the robust "best_match_key" logic
            best_match_key = ""
            for key in self.fixture_dict.keys():
                sanitized_key = key.upper().replace(" ", "_")
                if block_name_upper.startswith(sanitized_key):
                    if len(key) > len(best_match_key):
                        best_match_key = key
            
            fixture_type = None
            if best_match_key:
                fixture_type = self.fixture_dict[best_match_key].get("type")

            # Check if this fixture is an ANCHOR
            is_anchor_type = fixture_type in anchor_types
            is_anchor_name = any(name_check in detail['name'].upper() for name_check in anchor_names)
            is_target = 'STANDING_TABLE' in detail['name'].upper()

            try:
                # Create the polygon from the true WCS corners
                poly = Polygon(detail['corners_wcs'])
                
                if is_anchor_type or is_anchor_name:
                    anchor_polygons.append(poly)
                    print(f"    -> Found ANCHOR: {detail['name']}")
                elif not is_target:
                    other_obstacle_polygons.append(poly)
                    print(f"    -> Found OBSTACLE: {detail['name']}")

            except Exception as e:
                print(f"    -> Warning: Could not create polygon for {detail['name']}: {e}")

        # --- 4. Get BOH/Back_Wall Polygons/Lines (Anchors) ---
        try:
            boh_poly = self._get_boh_zone_polygon(doc)
            if boh_poly and not boh_poly.is_empty:
                anchor_polygons.append(boh_poly)
                print("    -> Found ANCHOR: BOH Wall Polygon")
        except Exception as e:
            print(f"    -> ⚠️ Could not check for BOH wall polygon: {e}")

        try:
            back_wall_lines = list(doc.msp.query('LINE[layer=="BACK_WALL"]'))
            if back_wall_lines:
                back_wall_bbox = extents(back_wall_lines)
                if back_wall_bbox.has_data:
                    # Buffer the line to give it thickness
                    anchor_polygons.append(box(*back_wall_bbox.extmin, *back_wall_bbox.extmax).buffer(50))
                    print("    -> Found ANCHOR: BACK_WALL Line")
        except Exception as e:
            print(f"    -> ⚠️ Could not check for BACK_WALL line: {e}")

        try:
            back_wall_poly = self._get_back_wall_polygons(doc)
            if back_wall_poly:
                anchor_polygons.extend(back_wall_poly)
                print("  -> (Step 4b) Added BACK_WALL to anchors.")
        except Exception as e:
            print(f"  -> ⚠️ Could not get BACK_WALL polygon: {e}")


        # --- 5. Create the "Carved-Out" Retail Zone ---
        if not anchor_polygons:
            print("  -> ⚠️ FAILED: No anchor fixtures found. Cannot carve zone.")
            return None

        # Combine all anchors into one shape
        all_anchors_union = unary_union(anchor_polygons)

        # --- NEW: Apply the top boundary gap ---
        if TOP_BOUNDARY_GAP > 0:
            all_anchors_union = all_anchors_union.buffer(TOP_BOUNDARY_GAP, join_style=1) # Mitre join
            print(f"  -> Applied {TOP_BOUNDARY_GAP}mm gap below anchor fixtures.")
        
        # Start with the full floorplan and subtract the anchors
        # This creates the exact "dovetail" shape you drew
        full_retail_zone = self.floorplan_polygon.difference(all_anchors_union)
        print("  -> (Step 5) Successfully carved anchor fixtures from floorplan.")

        # --- 6. Subtract Other Obstacles ---
        # (This list is likely empty, but this is for future robustness)
        if other_obstacle_polygons:
            all_other_obstacles_union = unary_union(other_obstacle_polygons)
            full_retail_zone = full_retail_zone.difference(all_other_obstacles_union)
            print("  -> (Step 6) Subtracted other pre-existing obstacles.")

        # --- 7. Apply Side Aisles ---
        zone_after_aisles = full_retail_zone.buffer(-SIDE_AISLE_GAP, join_style=1) # join_style 2 = MITRE
        if zone_after_aisles.is_empty:
            print(f"  -> ⚠️ FAILED: Zone is too narrow after subtracting {SIDE_AISLE_GAP}mm side aisles.")
            return None
        print(f"  -> (Step 7) Subtracted {SIDE_AISLE_GAP}mm side aisles.")
        
        final_zone = zone_after_aisles

        # --- NEW: Apply Bottom Boundary Threshold ---
        if BOTTOM_BOUNDARY_THRESHOLD > 0:
            slicer_y = self.cvc.min_y + BOTTOM_BOUNDARY_THRESHOLD
            slicer_box = box(self.cvc.min_x, slicer_y, self.cvc.max_x, self.cvc.max_y)
            final_zone = final_zone.intersection(slicer_box)
            print(f"  -> Applied bottom boundary threshold, keeping area above Y={slicer_y:.0f}")


        # --- 8. Clean Up Fragments ---
        if final_zone.geom_type == 'MultiPolygon':
            print("  -> Zone is fragmented. Selecting the largest valid area.")
            min_area_threshold = 500000 # 0.5 sq m
            valid_pieces = [p for p in final_zone.geoms if p.area > min_area_threshold]
            if not valid_pieces:
                print("  -> ⚠️ FAILED: All zone fragments are too small to be usable.")
                return None
            final_zone = max(valid_pieces, key=lambda p: p.area)
        
        zone_bounds = final_zone.bounds
        zone_width = zone_bounds[2] - zone_bounds[0]
        zone_height = zone_bounds[3] - zone_bounds[1]
        print(f"  -> ✅ Successfully defined final Standing Table zone (W: {zone_width:.0f}mm x H: {zone_height:.0f}mm)")

        # --- 9. Debug Visualization ---
        if debug:
            print("  -> 🎨 Drawing debug zone...")
            self.draw_debug_polygon(
                doc, 
                final_zone, 
                "DEBUG_STANDING_TABLE_ZONE", 
                color=3, # Green
                visible_by_default=True
            )

        return final_zone

    def draw_debug_polygon(self, doc, polygon: Polygon, layer_name: str, color: int = 1, visible_by_default: bool = False):
        """
        [DEBUG HELPER]
        Draws a Shapely Polygon or MultiPolygon on a specified layer.
        Manages layer creation and visibility.
        """
        if not polygon or polygon.is_empty:
            print(f"  -> ⚠️ WARNING (draw_debug_polygon): Polygon for layer '{layer_name}' is empty. Nothing to draw.")
            return

        try:
            # 1. Get or create the layer
            layer = None
            if layer_name not in doc.doc.layers:
                layer = doc.doc.layers.add(name=layer_name, color=abs(color)) 
            else:
                layer = doc.doc.layers.get(layer_name)

            if not layer:
                print(f"  -> ⚠️ ERROR: Could not get or create layer '{layer_name}'.")
                return

            def draw_single_poly(poly):
                if poly.exterior:
                    doc.msp.add_lwpolyline(
                        list(poly.exterior.coords),
                        close=True,
                        dxfattribs={"layer": layer_name}
                    )
                for interior in poly.interiors:
                    doc.msp.add_lwpolyline(
                        list(interior.coords),
                        close=True,
                        dxfattribs={"layer": layer_name}
                    )

            # 2. Draw the geometry
            if polygon.geom_type == 'Polygon':
                draw_single_poly(polygon)
            elif polygon.geom_type == 'MultiPolygon':
                for poly in polygon.geoms:
                    draw_single_poly(poly)
            
            # 3. Set the visibility
            if not visible_by_default:
                layer.freeze()
            else:
                layer.thaw()
            
            visibility_status = "'On'" if layer.is_on else "'Off/Frozen'"
            # print(f"    -> Drawn debug shape on layer '{layer_name}' (Layer is {visibility_status})") # Reduced verbosity

        except Exception as e:
            print(f"  -> ⚠️ ERROR in draw_debug_polygon: {e}")

    def get_placed_details_ST(self, doc: dxf_doc.DXF_Document) -> List[Dict[str, Any]]:
            """
            [MODIFIED - v2 - Anchor Fix]
            Finds all placed floor fixtures (clinics, benches, euros, etc.) and
            returns a detailed list of their true, oriented geometry.
            
            *** CORRECTION:*** Added 'boh' and 'pickup_window' to valid_types
            so that get_standing_table_placement_zone() can see its anchors.
            """
            print(f"\n--- 🔎 Getting placed fixture details for Doc {doc.ind} (v2 Anchor Fix) ---")
            
            all_details = []
            
            # --- 1. Get all INSERT entities ---
            all_inserts = doc.msp.query('INSERT')
            
            for entity in all_inserts:
                block_name_upper = entity.dxf.name.upper()
                
                # --- 2. Filter to find matching fixture type ---
                best_match_key = ""
                for key in self.fixture_dict.keys():
                    sanitized_key = key.upper().replace(" ", "_")
                    if block_name_upper.startswith(sanitized_key):
                        if len(key) > len(best_match_key):
                            best_match_key = key
                
                if not best_match_key:
                    continue # Not a recognized fixture
                    
                fixture_type = self.fixture_dict[best_match_key].get("type")
                
                # --- 3. Only process "floor" fixtures, not wall/screen fixtures ---
                
                # ******************************************************
                # ******** THIS IS THE CORRECTED LINE ********
                # ******************************************************
                valid_types = {'clinic', 'boh_preset', 'boh', 'pickup_window', 'floor', 'loose', 'pos', 'table_fixtures','wall_fixtures'}
                
                # ******************************************************
                # ******************************************************

                if fixture_type not in valid_types and 'table' not in best_match_key.lower():
                    continue

                print(f"  -> Processing: {entity.dxf.name} (Type: {fixture_type})")

                try:
                    # --- 4. Use get_outer_rect_corners_shapely() ---
                    corners_tuples = self.get_outer_rect_corners_shapely(entity)
                    
                    if len(corners_tuples) < 4:
                        print(f"    -> WARNING: Could not get corners for {entity.dxf.name}. Skipping.")
                        continue

                    corners_xy = [(c[0], c[1]) for c in corners_tuples]
                    corners_vecs = [Vec2(c[0], c[1]) for c in corners_xy]
                    
                    # --- 5. Calculate AABB (Axis-Aligned Bounding Box) ---
                    min_x = min(c[0] for c in corners_xy)
                    min_y = min(c[1] for c in corners_xy)
                    max_x = max(c[0] for c in corners_xy)
                    max_y = max(c[1] for c in corners_xy)
                    bbox_tuple = (min_x, min_y, max_x, max_y)

                    # --- 6. Define the 4 oriented segments ---
                    c1, c2, c3, c4 = corners_vecs[0], corners_vecs[1], corners_vecs[2], corners_vecs[3]
                    
                    segments = {
                        'bottom_segment': (c1, c2),  # Vector: c2 - c1
                        'right_segment': (c2, c3),   # Vector: c3 - c2
                        'top_segment': (c4, c3),     # Vector: c3 - c4
                        'left_segment': (c1, c4)    # Vector: c4 - c1
                    }

                    # --- 7. Append all details to the list ---
                    all_details.append({
                        'name': entity.dxf.name,
                        'entity': entity,
                        'bbox': bbox_tuple,
                        'segments': segments,
                        'corners_wcs': corners_xy 
                    })
                    
                except Exception as e:
                    print(f"    -> ⚠️ ERROR processing {entity.dxf.name}: {e}")
                    continue

            print(f"  -> ✅ Found details for {len(all_details)} placed floor fixtures.")
            return all_details

    def _calculate_dynamic_standing_table_threshold(self, doc, percentage: float = 0.60) -> float:
        """
        Calculates a dynamic threshold for the standing table zone's bottom boundary.

        This is calculated as a percentage of the vertical space between the
        lowest clinic and the bottom of the floorplan.

        Args:
            doc: The DXF_Document to analyze.
            percentage: The percentage of the height to use (e.g., 0.60 for 60%).

        Returns:
            The calculated threshold distance in millimeters.
        """
        print("\n    -> Calculating dynamic standing table bottom threshold...")

        # Get the top of the lower retail area (bottom of clinics)
        clinic_min_y = self.get_clinic_min_y(doc)
        if clinic_min_y is None:
            print("      -> ⚠️ Could not find clinic min_y. Defaulting to a fixed threshold of 3000mm.")
            return 3000.0

        # Get the bottom of the floorplan
        floorplan_bottom_y = self.cvc.min_y

        # Calculate the height of this lower retail space
        lower_retail_height = clinic_min_y - floorplan_bottom_y
        if lower_retail_height <= 0:
            print(f"      -> ⚠️ No vertical space found below clinics (Height: {lower_retail_height:.0f}mm). Defaulting to 3000mm.")
            return 3000.0

        # Calculate the threshold as a percentage of this height
        dynamic_threshold = lower_retail_height * percentage
        
        print(f"      -> Lower retail height: {lower_retail_height:.0f}mm")
        print(f"      -> Dynamic threshold ({percentage*100:.0f}%): {dynamic_threshold:.0f}mm")

        return dynamic_threshold

    def generate_alternating_grid(self, doc, rotation: int, start_type: str, debug: bool = False) -> List[Tuple[float, float]]:
        """
        [SMART GREEDY PACKING] 
        Iterates row by row. For each potential spot, it checks if placing a table there
        would touch ANY table in the row directly above (Vertically or Diagonally).
        
        - If the Row above is dense (T-G-T), this logic effectively skips the current row.
        - If the Row above has gaps (Walls/Obstacles), this logic fills the safe pockets below.
        """
        
        # --- 1. Get the Zone ---
        zone = getattr(doc, 'standing_table_zone', None)
        if not zone or zone.is_empty:
            return []

        # --- 2. Define Dimensions ---
        ST_GAP = 900.0
        
        if rotation == 0:
            row_height = 750.0
            table_w = 700.0
            gap_w = ST_GAP
            table_h = 600.0 
            debug_prefix = "DEBUG_GRID_0_DEG"
        else: # 90 degrees
            row_height = 750.0
            table_w = 600.0 
            gap_w = ST_GAP
            table_h = 700.0 
            debug_prefix = "DEBUG_GRID_90_DEG"

        # --- 3. Get Obstacles ---
        partition_bboxes = self.cvc.get_internal_wall_partitions(min_length=50, max_length=670.0, thickness=0.0)
        partition_polygons = [box(*b) for b in partition_bboxes]

        final_grid_points = []
        min_x_zone, min_y_zone, max_x_zone, max_y_zone = zone.bounds
        
        # Helper to draw debug boxes
        def draw_debug_box(x, y, w, h, type_code):
            if not debug: return
            color = 3 if type_code == "VALID" else (1 if type_code == "INVALID" else 8)
            layer = f"{debug_prefix}_{start_type.upper()}_{type_code}"
            if layer not in doc.doc.layers:
                doc.doc.layers.add(name=layer, color=color)
            pts = [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]
            doc.msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})

        # --- 4. Smart Row Logic ---
        current_y = max_y_zone - row_height 
        
        # We track the intervals occupied by tables in the PREVIOUS row
        # Format: List of tuples (x_start, x_end)
        prev_row_occupied_intervals = [] 

        # Start Offset logic (for Pattern shifting)
        start_with_table = (start_type == 'Table')

        while current_y >= min_y_zone:
            current_x = min_x_zone
            current_row_intervals = [] # Track what we place in this row
            
            # Reset Horizontal toggle for new row
            is_placing_table = start_with_table 
            
            while current_x < max_x_zone:
                
                if is_placing_table:
                    # --- 1. Define the Candidate Spot ---
                    cand_start = current_x
                    cand_end = current_x + table_w
                    cell_box = box(cand_start, current_y, cand_end, current_y + table_h)
                    
                    # --- 2. Check "Smart" Restrictions (Vertical & Diagonal) ---
                    # A spot is INVALID if it overlaps with the "Restricted Zone" of any table in the row above.
                    # The Restricted Zone of a table extends 'table_w' to the left and right.
                    # This covers: Direct Below (Vertical), Left Diagonal, and Right Diagonal.
                    
                    is_restricted_by_above = False
                    for prev_start, prev_end in prev_row_occupied_intervals:
                        # Define the danger zone from the table above
                        # Expanded by table_w to cover diagonals
                        danger_start = prev_start - table_w + 10 # +10 tolerance
                        danger_end = prev_end + table_w - 10     # -10 tolerance
                        
                        # Check intersection
                        if not (cand_end < danger_start or cand_start > danger_end):
                            is_restricted_by_above = True
                            break
                    
                    # --- 3. Check Standard Obstacles ---
                    intersection_area = zone.intersection(cell_box).area
                    containment_ratio = intersection_area / cell_box.area if cell_box.area > 0 else 0
                    hits_partition = any(cell_box.intersects(p) for p in partition_polygons)
                    
                    # --- 4. Final Decision ---
                    if containment_ratio >= 0.50 and not hits_partition and not is_restricted_by_above:
                        # Valid! Place it.
                        final_grid_points.append((current_x, current_y))
                        current_row_intervals.append((cand_start, cand_end))
                        draw_debug_box(current_x, current_y, table_w, table_h, "VALID")
                    else:
                        # Invalid
                        # We draw a special color for "Restricted by Row Above" if needed, strictly using standard here
                        draw_debug_box(current_x, current_y, table_w, table_h, "INVALID")
                    
                    current_x += table_w
                    is_placing_table = False # Next is Gap
                    
                else:
                    # --- PLACE GAP ---
                    draw_debug_box(current_x, current_y, gap_w, row_height, "GAP")
                    current_x += gap_w
                    is_placing_table = True # Next is Table

            # --- End of Row Updates ---
            # Update the "Previous Row" tracker for the next iteration
            prev_row_occupied_intervals = current_row_intervals
            
            # Move down
            current_y -= row_height
            
            # Note: We do NOT flip 'start_with_table' here because we want strict alignment 
            # to test vertical stacking. The smart logic handles the rest.

        return final_grid_points

    
    def analyze_standing_table_patterns(self, doc, debug: bool = False) -> dict:
        """
        [UPDATED v5] Analyzes 4 specific alternating blueprints to find the best layout.
        Now passes 'debug' to the generator to verify grid logic.
        """
        print("\n--- 🧠 Analyzing Standing Table Patterns (v5 - Alternating Grid) ---")

        # --- 1. Get Inputs ---
        config = self.fixtures.get("table_fixtures", {})
        standing_table_count = config.get("Standing_table", 0)
        
        if standing_table_count <= 0:
            return {}

        # --- 2. Generate the 4 Blueprints ---
        # We pass 'debug' here so it draws the boxes while generating
        blueprints = {
            "0_deg_Start_Table": self.generate_alternating_grid(doc, 0, "Table", debug),
            "0_deg_Start_Gap":   self.generate_alternating_grid(doc, 0, "Gap", debug),
            "90_deg_Start_Table": self.generate_alternating_grid(doc, 90, "Table", debug),
            "90_deg_Start_Gap":   self.generate_alternating_grid(doc, 90, "Gap", debug),
        }

        # --- 3. Score and Rank ---
        def _create_and_score_plan(name, coords, required_count):
            # Sort by Y (highest first) to fill from top
            sorted_coords = sorted(coords, key=lambda p: p[1], reverse=True)
            
            # Take up to the required amount
            final_coords = sorted_coords[:required_count]
            count = len(final_coords)
            
            if count == 0:
                return {'name': name, 'score': -1, 'count': 0, 'placements': {}}

            # Score is average Y (higher is better)
            avg_y = sum(p[1] for p in final_coords) / count
            
            # Create format for executor
            placements_dict = {
                f"count_{i+1}": {"coordinates": c} 
                for i, c in enumerate(final_coords)
            }
            
            return {
                'name': name,
                'score': avg_y,
                'count': count,
                'placements': placements_dict
            }

        plans = []
        for name, coords in blueprints.items():
            print(f"  -> Blueprint '{name}' found {len(coords)} valid spots.")
            plans.append(_create_and_score_plan(name, coords, standing_table_count))

        if not plans:
            print("  -> ⚠️ FAILED: No valid spots found in any blueprint.")
            return {}

        # --- 4. Sorting Logic (Best Fit) ---
        # Priority 1: Meets required count
        # Priority 2: Highest Y score
        sufficient_plans = [p for p in plans if p['count'] >= standing_table_count]
        
        if sufficient_plans:
            sorted_plans = sorted(sufficient_plans, key=lambda p: p['score'], reverse=True)
            # Append insufficient ones at the end just in case
            insufficient = sorted([p for p in plans if p['count'] < standing_table_count], key=lambda p: p['count'], reverse=True)
            sorted_plans.extend(insufficient)
        else:
            # If none meet requirement, pick the one with the most tables
            sorted_plans = sorted(plans, key=lambda p: (p['count'], p['score']), reverse=True)

        # --- 5. Format Output ---
        all_patterns = {}
        print("\n  --- Final Ranked Blueprints ---")
        for i, plan in enumerate(sorted_plans):
            rank = i + 1
            all_patterns[plan['name']] = {
                'rank': rank,
                'count': plan['count'],
                'placements': plan['placements'],
                'placed': False,
                '_score': plan['score']
            }
            print(f"    Rank {rank}: '{plan['name']}' (Count: {plan['count']}, Avg Y: {plan['score']:.0f})")

        return all_patterns

 
    
    
    def place_by_plan_standing_tables(self, doc, placement_plan: dict):
        """
        [EXECUTOR] Places Standing Tables based on the selected plan.
        
        Updates:
        1. Detects rotation (0 vs 90) from the pattern name.
        2. Swaps cell dimensions to find the correct center target.
        3. Rotates the fixture to match the grid.
        """
        print("\n--- 🚀 Executing Standing Table Placement ---")

        placements = placement_plan.get('placements', {})
        pattern_name = placement_plan.get('chosen_pattern_name', '')
        
        if not placements:
            print("  -> No tables to place in this plan.")
            return

        # --- 1. Load Fixture ---
        try:
            fxtr = Fixture.Fixture("Standing_table", self.fixture_dict["Standing_table"]["path"])
        except Exception as e:
            print(f"  -> 🔥 FATAL: Could not load 'Standing_table': {e}")
            return

        # --- 2. Determine Rotation & Geometry ---
        # Check if the winning plan was a 90-degree layout
        is_rotated = "90_deg" in pattern_name
        
        if is_rotated:
            rotation = 90.0
            cell_w = 600.0  # Width is narrower
            cell_h = 700.0  # Height is taller
        else:
            rotation = 0.0
            cell_w = 700.0  # Width is wider
            cell_h = 600.0  # Height is shorter
            
        print(f"  -> Pattern: '{pattern_name}' | Rotation: {rotation}° | Cell: {cell_w}x{cell_h}")

        count = 0
        
        # --- 3. Placement Loop ---
        for key, data in placements.items():
            # The grid generator gives us the Bottom-Left corner of the valid box
            grid_x, grid_y = data['coordinates']
            
            # A. Calculate the Target Center of the grid cell
            target_center = Vec2(grid_x + (cell_w / 2), grid_y + (cell_h / 2))
            
            try:
                # B. Calculate Insertion Point
                # We calculate where to put the insertion point so the fixture's center 
                # lands exactly on 'target_center'
                local_center = fxtr.bounding_box.center
                
                # Rotate the offset based on our decided angle
                rotated_offset = local_center.rotate(math.radians(rotation))
                final_insert_point = target_center - rotated_offset
                
                # C. Place the Fixture
                xscale, yscale = -1.0, -1.0
                # x_inset, y_inset = 750,700
                # x_inset, y_inset = -600,750
                if is_rotated:
                    x_inset, y_inset = -600, 750
                else:
                    x_inset, y_inset = 750, 700

                block_ref = doc.place_fixture(
                    fxtr,
                    (final_insert_point.x + x_inset, final_insert_point.y + y_inset, 0),
                    rotation,
                    rotated=True, # Important: Tell place_fixture we are handling rotation
                    xscale=xscale,
                    yscale=yscale
                )
                
                # D. Register Obstacle (Bounding Box)
                if block_ref:
                    bbox = extents([block_ref])
                    if bbox.has_data:
                        doc.placed_bboxes.append((bbox.extmin.x, bbox.extmin.y, bbox.extmax.x, bbox.extmax.y))
                        count += 1
                        
            except Exception as e:
                print(f"    -> ⚠️ Error placing table at {key}: {e}")

        print(f"  -> ✅ Successfully placed {count} Standing Tables.")



    

    #----------------------------------------SOME----NEW-----------GRID-------------APPROACH----------------------
    #----------------------------------------SOME----NEW-----------GRID-------------APPROACH----------------------


    def plan_and_place_standing_tables(self, debug: bool = False):
        """
        [ORCHESTRATOR v3 - Final] 
        Manages the end-to-end placement of Standing Tables:
        1. Defines the valid 'Carve-Out' Zone.
        2. Analyzes 4 alternating blueprints to find the best fit.
        3. Selects the Rank 1 plan.
        4. Executes placement directly on the document.
        """
        print("\n--- 🧠 Orchestrating Standing Table Placement (Neat Version) ---")

        # --- 1. Check Configuration ---
        config = self.fixtures.get("table_fixtures", {})
        standing_table_count = config.get("Standing_table", 0)

        if standing_table_count <= 0:
            print("  -> SKIPPED: No standing tables required.")
            return

        for doc in self.docs:
            if doc.skip:
                continue
            
            print(f"\n--- Processing Standing Tables for Doc {doc.ind} ---")

            # --- 2. Calculate Zone ---
            # Calculates the polygon by subtracting Clinics, BOH, and Aisles
            placement_zone = self.get_standing_table_placement_zone(doc, debug=debug)
            
            if not placement_zone or placement_zone.is_empty:
                print(f"  -> ⚠️ FAILED: No valid placement zone found.")
                doc.skip = True # Mark doc as failed if we can't place core tables
                continue
            
            # Store zone for the generator functions to use
            doc.standing_table_zone = placement_zone

            # --- 3. Analyze Patterns ---
            # Generates 4 blueprints, scores them, and returns them ranked.
            all_patterns = self.analyze_standing_table_patterns(doc, debug=debug)
            
            if not all_patterns:
                print(f"  -> ⚠️ FAILED: No valid patterns fit in the zone.")
                doc.skip = True
                continue

            # --- 4. Select Best Plan (Rank 1) ---
            # Find the pattern dictionary where rank == 1
            best_pattern_name = None
            best_plan_data = None
            
            for name, data in all_patterns.items():
                if data['rank'] == 1:
                    best_pattern_name = name
                    best_plan_data = data
                    break
            
            if not best_plan_data:
                print("  -> ⚠️ ERROR: Analyzer finished but no Rank 1 plan was found.")
                continue

            print(f"  -> 🏆 Selected Winner: '{best_pattern_name}'")
            print(f"     (Capacity: {best_plan_data['count']}/{standing_table_count}, Score: {best_plan_data['_score']:.0f})")

            # --- 5. Execute Placement ---
            # Inject the name into the data so the placer knows the rotation
            best_plan_data['chosen_pattern_name'] = best_pattern_name
            
            self.place_by_plan_standing_tables(doc, best_plan_data)
            
            # --- 6. Refresh Obstacles ---
            # Update master list so subsequent fixtures (Wall/Euro) avoid these tables
            self._get_accurate_obstacle_bboxes(include_all=True)

        print("\n--- ✅ Standing Table Orchestration Complete ---")


    
    

########################################################################################################################
########################################################################################################################
########################################     STANDING TABLE NEW ALGORITHM SIMILAR TO EURO   ############################
########################################     STANDING TABLE NEW ALGORITHM SIMILAR TO EURO   ############################
########################################     STANDING TABLE NEW ALGORITHM SIMILAR TO EURO   ############################
########################################################################################################################
########################################################################################################################




########################################################################################################################
########################################################################################################################
################################                   TV PLACEMENT STARTING HERE              #############################
########################################################################################################################
########################################################################################################################

    def get_clinic_min_y(self, doc) -> Optional[float]:
        """
        [NEW HELPER] Finds the lowest Y-coordinate (min_y) among all
        placed clinic fixtures in the document.

        Args:
            doc (DXF_Document): The document to query.

        Returns:
            Optional[float]: The lowest Y-coordinate (extmin.y) found,
                             or None if no clinics are placed.
        """
        print(f"\n--- 🔎 Finding lowest Y-coordinate of all placed clinics (Doc {doc.ind}) ---")

        # 1. Query for all placed clinic entities
        clinic_entities = [
            e for e in doc.msp.query('INSERT')
            if "CLINIC" in e.dxf.name.upper()
        ]

        if not clinic_entities:
            print("  -> No clinic entities found.")
            return None

        # 2. Get the extents for each clinic
        all_extents = []
        for entity in clinic_entities:
            try:
                # Use virtual_entities() for accurate rotated bounds
                bbox = extents(list(entity.virtual_entities()))
                if bbox.has_data:
                    all_extents.append(bbox)
            except Exception as e:
                print(f"  -> ⚠️ Could not get extents for {entity.dxf.name}: {e}")
                continue
        
        if not all_extents:
            print("  -> Found clinic entities, but could not get valid extents.")
            return None

        # 3. Find the minimum 'extmin.y' value
        min_y = min(bbox.extmin.y for bbox in all_extents)
        
        print(f"  -> ✅ Lowest clinic Y-coordinate (min_y) found at: {min_y:.0f}")
        return min_y

    def get_tv_count(self, doc) -> int:
        """
        Calculates the number of TVs to place based on the FOH (Front of House)
        vertical length, as per your request.
        
        - FOH length is from the floorplan bottom (min_y) to the bottom of the
          lowest clinic fixture (get_clinic_min_y).
        - Rule: 1 TV is placed at the bottom, plus 1 additional TV for
          every 6 meters (6000mm) of FOH length.
        """
        import math
        print("\n--- 📺 Calculating Dynamic TV Count (New Strategy) ---")

        # 1. Find the top boundary of the FOH (bottom of clinics)
        try:
            top_boundary_y = self.get_clinic_min_y(doc)
            if top_boundary_y is None:
                 print("  -> ⚠️ FAILED: Could not determine top boundary (no clinics found). Defaulting to 0 TVs.")
                 return 0
        except Exception as e:
            print(f"  -> ⚠️ FAILED: Error getting top boundary: {e}. Defaulting to 0 TVs.")
            return 0
            
        # 2. Find the bottom boundary of the FOH (floorplan min_y)
        try:
            bottom_boundary_y = self.cvc.min_y
        except Exception as e:
            print(f"  -> ⚠️ FAILED: Could not get floorplan min_y: {e}. Defaulting to 0 TVs.")
            return 0

        # 3. Calculate FOH length
        foh_length = top_boundary_y - bottom_boundary_y
        
        if foh_length <= 0:
            print(f"  -> No FOH space found (Length: {foh_length:.0f}mm). TV count set to 0.")
            return 0
            
        print(f"  -> Calculated FOH vertical length: {foh_length:.0f} mm")

        # 4. Apply the placement rule: 1 + (1 for every 6 meters)
        SIX_METERS_MM = 6000.0
        
        # math.floor(length / 6000) gives the number of *additional* 6m chunks.
        # We add 1 for the first TV placed at the bottom (facade).
        tv_count = math.floor(foh_length / SIX_METERS_MM) + 1
        
        print(f"  -> ✅ TV Count calculated: {int(tv_count)}")
        
        return int(tv_count)
    

    def place_tv_screens_new(self, primary_side: str = "left"):
        """
        [NEW STRATEGY v3] Places TV screens using a "search-and-anchor" logic.
        - TV #1: Facade, opposite primary side.
        - TV #2+:
            1. Define a 6000mm vertical "search zone" above the last placed TV.
            2. Search for Euro Centres within this zone.
            3. If a Euro is found, anchor the new TV to its center.
            4. If no Euro is found, place the new TV stacked 6000mm
               vertically above the last one.
        - All TVs are force-placed to allow overlap.
        """
        print("\n--- 📺 Placing TV Screens (New FOH-based Strategy v3) ---")

        # Loop through each document variant
        for doc in self.docs:
            if doc.skip:
                continue
            
            print(f" \n ----> Planning TVs for Doc {doc.ind} ----")

            # --- 1. Get TV Count (using your new function) ---
            tv_count = self.get_tv_count(doc)
            if tv_count <= 0:
                print("  -> SKIPPED: No TVs required based on FOH length.")
                continue

            try:
                # We assume "screen_55" is the standard
                screen_fxtr = Fixture.Fixture("screen_55", self.fixture_dict["screen_55"]["path"])
                screens_to_place = collections.deque([screen_fxtr] * tv_count)
                print(f"  -> Queue created for {tv_count} TVs.")
            except Exception as e:
                print(f"  -> 🔥 FAILED: Could not load 'screen_55' fixture: {e}")
                continue

            placed_tv_count = 0
            last_tv_details = None # Stores {'bbox': tuple, 'center': Vec2}

            # --- 2. Place TV #1 (Facade, Opposite Side) ---
            if screens_to_place:
                screen_to_place = screens_to_place.popleft()
                tv_number = placed_tv_count + 1
                
                target_side = "right" if primary_side == "left" else "left"
                print(f"  -> Placing TV #{tv_number} on Facade (Opposite Side: {target_side})...")
                
                spot_data = self._find_bottom_wall_corner_spot(target_side, screen_to_place)
                
                if spot_data:
                    target_center, angle_deg = spot_data
                    # Force=True allows overlapping the facade/door
                    new_bbox = self._validate_and_place_at_point_tv(
                        doc, screen_to_place, target_center, angle_deg, 
                        doc.placed_bboxes, force=True
                    )
                    
                    if new_bbox:
                        doc.placed_bboxes.append(new_bbox)
                        print(f"    ✅ Placed TV #{tv_number} at facade {target_side} side.")
                        last_tv_details = {"bbox": new_bbox, "center": target_center}
                        placed_tv_count += 1
                    else:
                        print(f"    -> ⚠️ FAILED to place TV #{tv_number} (spot invalid even with force).")
                        screens_to_place.appendleft(screen_to_place) # Add back to queue
                else:
                    print(f"    -> ⚠️ FAILED: Could not find any spot on facade {target_side} side.")
                    screens_to_place.appendleft(screen_to_place) # Add back to queue


            # --- 3. Place TV #2+ (Search-and-Anchor or Stack) ---
            while screens_to_place:
                if not last_tv_details:
                    print("    -> ⚠️ FAILED: Cannot stack TV, last TV details are missing.")
                    break # Stop placing TVs for this doc

                screen_to_place = screens_to_place.popleft()
                tv_number = placed_tv_count + 1
                print(f"  -> Placing TV #{tv_number} (Search-and-Anchor)...")

                # --- A. Define the 6000mm search zone ---
                search_y_start = last_tv_details["bbox"][3] # Top of last TV
                search_y_end = search_y_start + 6000.0
                print(f"    -> Defining 6m search zone from Y={search_y_start:.0f} to Y={search_y_end:.0f}")

                # --- B. Search for Euro Centres in this zone ---
                euro_entities = [e for e in doc.msp.query('INSERT') if "EURO_CENTRE" in e.dxf.name.upper()]
                anchor_euros_in_zone = []
                for entity in euro_entities:
                    try:
                        euro_bbox = extents([entity])
                        # Check if the Euro's *center* is within the search zone
                        if search_y_start < euro_bbox.center.y < search_y_end:
                            anchor_euros_in_zone.append(entity)
                    except Exception:
                        continue
                
                target_center = None
                angle_deg = 0.0
                ignore_bbox = None
                placement_desc = ""

                # --- C. Apply the new logic ---
                if anchor_euros_in_zone:
                    # Rule Met: Euro(s) found. Anchor to them.
                    print(f"    -> Rule: Found {len(anchor_euros_in_zone)} Euro Centre(s) in zone. Anchoring to their center.")
                    
                    # Get the combined bounding box of *all* euros found in the zone
                    combined_euro_bbox = extents(anchor_euros_in_zone)
                    target_center = combined_euro_bbox.center
                    angle_deg = 0.0 # Euro-anchored TVs are always 0 degrees
                    ignore_bbox = (combined_euro_bbox.extmin.x, combined_euro_bbox.extmin.y,
                                   combined_euro_bbox.extmax.x, combined_euro_bbox.extmax.y)
                    placement_desc = "anchored to Euro Centre (found within 6m zone)"
                
                else:
                    # Rule Failed: No Euros found. Stack 6000mm vertically.
                    print("    -> Rule: No Euro Centre found in 6m zone. Stacking vertically.")
                    target_y = last_tv_details["bbox"][3] + 6000.0 + (screen_to_place.height / 2.0)
                    target_center = Vec2(last_tv_details["center"].x, target_y)
                    angle_deg = 0.0
                    placement_desc = "stacked 6000mm above previous TV"

                # --- D. Place the TV at the chosen spot ---
                if target_center:
                    validation_bboxes = [b for b in doc.placed_bboxes if b != ignore_bbox]
                    
                    new_bbox = self._validate_and_place_at_point_tv(
                        doc, screen_to_place, target_center, angle_deg, 
                        validation_bboxes, force=True
                    )
                    
                    if new_bbox:
                        doc.placed_bboxes.append(new_bbox)
                        print(f"    ✅ Placed TV #{tv_number} {placement_desc}.")
                        last_tv_details = {"bbox": new_bbox, "center": target_center}
                        placed_tv_count += 1
                    else:
                        print(f"    -> ⚠️ FAILED to place TV #{tv_number} at {placement_desc}.")
                        screens_to_place.appendleft(screen_to_place) # Add back
                        break # Stop if one fails
                else:
                    # This case should not be reachable
                    print("    -> ⚠️ FAILED: Target center was not set.")
                    screens_to_place.appendleft(screen_to_place)
                    break
            
            print(f"-> Finished TV placement for Doc {doc.ind}. Placed {placed_tv_count} of {tv_count}.")



########################################################################################################################
##############       TV PLACEMENT ENDING HERE                        ################################################
########################################################################################################################
########################################################################################################################


########################################################################################################################
##############       COLUMN HATCH FILLING STARTING HERE                        ################################################
########################################################################################################################
########################################################################################################################

      
    def draw_pillar(self, doc, polygon):
        """
        Draws a pillar with the standard wall hatching and outline styles.
        """
        if polygon.is_empty:
            return

        coords = list(polygon.exterior.coords)

        # 1. Create the Hatch (Same style as main walls)
        hatch = doc.msp.add_hatch()
        hatch.dxf.layer = self.HATCH_LAYER
        hatch.dxf.color = 250  # ACI: light gray
        hatch.dxf.true_color = rgb2int((120, 120, 120))
        hatch.set_pattern_fill('ANSI32', scale=10)
        hatch.dxf.pattern_angle = 90
        
        # Add the polygon boundary to the hatch
        hatch.paths.add_polyline_path(coords, is_closed=True)

        # 2. Draw the Outline (Same style as HATCH_OUTLINE)
        doc.msp.add_lwpolyline(
            coords,
            close=True,
            dxfattribs={"layer": "HATCH_OUTLINE", "lineweight": 25, "color": 7}
        )

    def detect_and_register_pillars(self, doc, debug: bool = False):
        """
        [FINAL] Detects pillars using precision snapping, registers them as obstacles,
        and draws them with the standard wall hatch.
        """
        print("\n--- 🏛️ Detecting Center Pillars (Precision Snapping & Hatching) ---")
        
        # --- Helper: Snap points close to each other ---
        def snap_lines(raw_coords, tolerance=50.0):
            unique_points = []
            def get_close_point(pt):
                for existing_pt in unique_points:
                    if math.dist(pt, existing_pt) < tolerance:
                        return existing_pt
                return None

            snapped_lines = []
            for coords in raw_coords:
                p1 = (coords[0], coords[1])
                p2 = (coords[2], coords[3])
                
                # Snap P1
                close_p1 = get_close_point(p1)
                final_p1 = close_p1 if close_p1 else p1
                if not close_p1: unique_points.append(p1)
                
                # Snap P2
                close_p2 = get_close_point(p2)
                final_p2 = close_p2 if close_p2 else p2
                if not close_p2: unique_points.append(p2)
                
                if final_p1 != final_p2:
                    snapped_lines.append(LineString([final_p1, final_p2]))
            return snapped_lines

        # 1. Gather Raw Data
        raw_coords_list = []
        if hasattr(self.cvc, 'plan_final'):
            for coords in self.cvc.plan_final.values():
                raw_coords_list.append(coords)
        
        if not raw_coords_list:
            print("  -> No wall data found.")
            return

        # 2. Process Geometry
        snapped_geometry = snap_lines(raw_coords_list, tolerance=50.0)
        candidate_polygons = list(polygonize(snapped_geometry))
        
        # 3. Filter and Draw
        SQFT_TO_SQMM = 92903.04
        MAX_PILLAR_AREA = 10.0 * SQFT_TO_SQMM
        MIN_PILLAR_AREA = 0.5 * SQFT_TO_SQMM
        
        pillars_found = 0
        
        if debug:
            layer_name = "DEBUG_PILLARS"
            if layer_name not in doc.doc.layers:
                doc.doc.layers.add(name=layer_name, color=1) # Red

        for poly in candidate_polygons:
            area = poly.area
            
            if MIN_PILLAR_AREA < area < MAX_PILLAR_AREA:
                pillars_found += 1
                pillar_id = f"pillar_{pillars_found}"
                area_sqft = area / SQFT_TO_SQMM
                
                print(f"  -> Found Pillar #{pillars_found}: {area_sqft:.2f} sq ft.")

                # A. Register Exact Bounding Box as Obstacle
                minx, miny, maxx, maxy = poly.bounds
                doc.placed_bboxes.append((minx-10, miny-10, maxx+10, maxy+10))
                
                # B. Draw Production Hatch (Matches Walls)
                self.draw_pillar(doc, poly)
                
                # C. Visual Debugging (Labels)
                if debug:
                    centroid = poly.centroid
                    doc.msp.add_mtext(
                        f"{pillar_id}\n{area_sqft:.1f}sf",
                        dxfattribs={
                            'char_height': 150,
                            'insert': (centroid.x, centroid.y),
                            'layer': layer_name,
                            'color': 1, # Red Text
                            'attachment_point': 5
                        }
                    )

        if pillars_found == 0:
            print(f"  -> No pillars detected (Scanned {len(candidate_polygons)} loops).")
        else:
            print(f"  -> ✅ Registered and hatched {pillars_found} pillars.")


########################################################################################################################
##############       COLUMN HATCH FILLING ENDING HERE                        ################################################
########################################################################################################################
########################################################################################################################



