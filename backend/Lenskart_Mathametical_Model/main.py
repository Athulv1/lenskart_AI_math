import os
import sys
import datetime
import glob
import json


# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import local modules
from DXF_Controller import DXF_Controller


# --- Configuration ---
json_merch_file = "merch_mix.json" # Define the JSON file name
image_path = "assets/test_horizontal.png"
base_name = "output/floorplan_test_"

# Generate a unique filename with a counter
existing_files = glob.glob(f"{base_name}*.dxf")
counter = len(existing_files) + 1
dxf_output = f"{base_name}{counter}.dxf"
overlay_output = "assets/overlay_output.png"

# --- Static Fixture Counts (Defaults & Non-Dossier Items) ---
# These are the fixture counts that are NOT derived from the dossier.
# They will be merged with the dynamic counts later.
static_fixtures = {
    "mirror_selection": { "mirror_different" : 1, "mirror": 0 },
 
    "Bench_fixtures":{ "large_bench" : 0, "AR": 0 , "medium_bench" : 1 },
    
    "lensometer_fixtures":{ "Lensometer_medium": 0, "Lensometer_small": 0, "Lensometer_large": 0 },
    
    "boh_fixtures": {
        "water_dispenser": 1, "ups_rack": 1, "staff_rack": 1, "pickup_storage_900": 0,
        "storage_rack": 1, "pickup_storage_1200": 0, "Dining_Table_large": 0,
        "QC_table_large": 0, "Dining_Table_medium": 1, "QC_table_medium": 0,
        "Repair_Table_large": 0, "Repair_Table_medium": 0, 
        "drop_box": 0, "pick_up_counter": 0
    },

    # "clinic_fixtures": { "ROC_clinic": 3,"Clinic_regular": 1, "Clinic_with_sink": 1,  "Eye_massage_area": 0 },

    "boh_presets": { "medium_basic_boh": 1, "basic_boh_preset_1": 0 ,"small_basic_boh": 0,"boh_vertical_horizontal_preset_basic": 0 },

    "pickup_window": { "Pick_up_window": 1 , "pickup_table": 1},

    "Eye_massage_area": { "Eye_massage_area": 0 },
    
    "Corian_table_set":{ "Corian_table" : 0, "Lounge_seat" : 0 },
    
    "loose_furniture": { "sofa": 0, "Sofa_large": 0, "Sofa_medium": 0 },
    
    "toilet_fixtures": { "toilet": 0 },
    
    "screen_fixtures": { "screen_43": 0, "screen_49": 0, "screen_55": 0, "screen_65": 0 },
    
    "POS": { "pos_with_screen_large": 0, "pos_with_screen_medium": 0, "pos_with_screen_small": 0, "pos_without_screen": 0 },
    
    "discussion_table_attached":{ "Blue_zero" : 1 },
    
    "table_fixtures": { "QMS_desk" : 1, 
                    #    "Standing_table" : 3
                         },
    
    "lensbar_and_dropbox": { "Lensbar": 0 },
    
    "floor_fixtures_table": { "Discussion_table_small": 0, "Discussion_table_medium": 0, "Discussion_table_large": 0 }
}


# ------------------- DYNAMIC SETUP AND EXECUTION -------------------

# 1. Initialize DXF_Controller with a temporary dictionary to analyze the floorplan.
# dxfc = DXF_Controller(image_path, dxf_output, overlay_output, "app/latest_go.json", {})
# dxfc = DXF_Controller(image_path, dxf_output, overlay_output, "app/kolanchery_version_3.json", {})
dxfc = DXF_Controller(image_path, dxf_output, overlay_output, "app/Vazhakala.json", {})
# dxfc = DXF_Controller(image_path, dxf_output, overlay_output, "app/pothencode_json.json", {})
# dxfc = DXF_Controller(image_path, dxf_output, overlay_output, "app/Bedigeri_ground_floor_.json", {})
# dxfc = DXF_Controller(image_path, dxf_output, overlay_output, "app/Arekere.json", {})
# dxfc = DXF_Controller(image_path, dxf_output, overlay_output, "app/White_filed_Bangalore.json", {})
# dxfc = DXF_Controller(image_path, dxf_output, overlay_output, "app/Bangalore_Gottigere_.json", {})

dxfc.create_floorplan()
dxfc.cvc.get_metadata()
dxfc.cvc.reorder_bot_left()
DRAW_SEPARATOR_LINE = True 


# 2. Load the merchandise data from the JSON file
merch_mix_data = dxfc.load_merch_data_from_json(json_merch_file)

# 4. NEW: Call the single setup and calculation function
dxfc.merch_mix_cal(merch_mix_data, static_fixtures) # type: ignore

# --- PLACEMENT PHASE ---
all_placed_bboxes = dxfc.get_existing_nonwall_bboxes()
floor_area = dxfc.calculate_area_sqft()
orientation = dxfc.cvc.orientation
Primary = "right"
print("Primary side for the floorplan is ", Primary)


if orientation == 'landscape':
    print("--- Applying LANDSCAPE placement strategy---")
    # dxfc.place_clinics_perimeter_walk(all_placed_bboxes)
    # dxfc.place_boh_intelligently(all_placed_bboxes)
    # dxfc.place_boh_preset(all_placed_bboxes)
    dxfc.place_clinics_with_best_fit_and_fallback(all_placed_bboxes)
    dxfc.place_boh_fixtures_in_room(all_placed_bboxes) 
    dxfc.place_wall_fixtures_perimeter_until_boh(all_placed_bboxes)
    dxfc.place_benches_near_clinics_with_multiple_strategies(all_placed_bboxes)
    dxfc.place_fixtures_iteratively_with_dynamic_stacks(all_placed_bboxes)
    remaining_tables = dxfc.place_discussion_tables_landscape(all_placed_bboxes)
    if remaining_tables:
        dxfc.place_remaining_tables_in_aisles(remaining_tables, all_placed_bboxes)
    dxfc.place_corian_table_set_landscape(all_placed_bboxes)
    dxfc.place_standing_tables_landscape(all_placed_bboxes)
    dxfc.place_blue_zero_landscape(all_placed_bboxes)
    dxfc.place_pos_ar_landscape(all_placed_bboxes)
    dxfc.place_qms_at_entrance(all_placed_bboxes)
    dxfc.place_sofas_dynamically_landscape(all_placed_bboxes)

else: # Default to portrait
    print("---Applying PORTRAIT placement strategy---")
    # ***** ADD THE NEW FUNCTION CALL HERE *****
    
    # dxfc.place_clinics_with_best_fit_and_fallback_og(all_placed_bboxes) 
    dxfc.place_clinics_master_strategy(all_placed_bboxes) 
    
    all_placed_bboxes = dxfc._get_accurate_obstacle_bboxes(include_all=True)
#     # Refresh the list of obstacles AFTER placing clinics
    # dxfc.place_pickup_window_next_to_clinic(all_placed_bboxes)
    dxfc.place_pickup_area_fixture(all_placed_bboxes)
    # dxfc.place_boh_preset(all_placed_bboxes)
    all_placed_bboxes = dxfc._get_accurate_obstacle_bboxes(include_all=True)
#     # dxfc.place_boh_intelligently_n(all_placed_bboxes)
    dxfc.place_boh_fixtures_in_room(all_placed_bboxes)
    all_placed_bboxes = dxfc._get_accurate_obstacle_bboxes(include_all=True)
    dxfc.draw_retail_separation_line(all_placed_bboxes, enabled=DRAW_SEPARATOR_LINE)
    all_placed_bboxes = dxfc._get_accurate_obstacle_bboxes(include_all=True)
    # dxfc.create_invisible_retail_boundary(all_placed_bboxes)
    dxfc.place_benches_near_clinics_with_multiple_strategies(all_placed_bboxes)
    dxfc.place_qms_at_entrance_center(all_placed_bboxes)
    dxfc.place_standing_tables_beside_euros(all_placed_bboxes)
    left_wall_length = dxfc.calculate_retail_wall_length(side='left')
    right_wall_length = dxfc.calculate_retail_wall_length(side='right')
    total_retail_wall_length = left_wall_length + right_wall_length

    dxfc.orchestrate_wall_and_overflow_placement(
        total_retail_wall_length=total_retail_wall_length,
        floor_area=floor_area,
        primary_side=Primary
    )

    # ==========================================================================
    # ***** ✅ ADD THE NEW TEST CALL HERE *****
    # ==========================================================================
    print("\n--- RUNNING RELOCATION ANALYSIS ---")
    gap_grid, score_grid = dxfc.analyze_relocation_opportunities()

    # Optional: Print the score grid to the console to see the results
    # if score_grid:
    #     print("--- Relocation Suitability Score Grid ---")
    #     # Print the grid row by row
    #     for row in score_grid:
    #         # Join the numbers in the row with spaces for readability
    #         print(" ".join(map(str, row)))
    # if gap_grid:
    #     print("--- Relocation Gap Grid ---")
    #     # Print the grid row by row
    #     for row in gap_grid:
    #         # Join the numbers in the row with spaces for readability
    #         print(" ".join(map(str, row)))
    # print("--- ANALYSIS COMPLETE --- \n")
    # ==========================================================================
    all_placed_bboxes = dxfc._get_accurate_obstacle_bboxes(include_all=True)
    
    # ==========================================================================
    # =========== NEW: Intelligent Euro Centre Placement Logic =================
    # ==========================================================================
    print("\n--- ⚖️  Running Simulations to Determine Optimal Euro Centre Strategy ---")

    # Step 1: Run both simulations to get the maximum possible count for each strategy.    
    capacity_v1 = dxfc.calculate_max_euro_capacity()
    capacity_v2 = dxfc.calculate_max_euro_capacity_v2()

    # Get the number of Euros we actually need to place
    needed_euros = dxfc.fixtures.get("floor_fixtures", {}).get("Euro_centre", 0)
    max_capacity = max(capacity_v1, capacity_v2)

    # Step 2: Compare the results and call the function that yields a higher count.
    if capacity_v1 >= capacity_v2:
        print(f"\n--- ✅ V1 (Rotated) is Optimal ({capacity_v1} vs {capacity_v2}). Executing V1 Placement. ---")
        dxfc.place_central_fixtures_from_qms_v1_og(
            placed_bboxes=all_placed_bboxes
        )
    else:
        print(f"\n--- ✅ V2 (Zero Rotation) is Optimal ({capacity_v2} vs {capacity_v1}). Executing V2 Placement. ---")
        dxfc.place_central_fixtures_from_qms_v1_og(
            placed_bboxes=all_placed_bboxes
        )
    # ==========================================================================
    # ======================== END OF NEW LOGIC ================================
    # ==========================================================================

    dxfc.place_discussion_tables_attached_to_euros(all_placed_bboxes)
    dxfc.place_corian_table_set(all_placed_bboxes)
    dxfc.place_pos_ar_portrait_dynamically(all_placed_bboxes)
    all_placed_bboxes = dxfc._get_accurate_obstacle_bboxes(include_all=True)    
    # dxfc.place_sofas_above_screen_ar(all_placed_bboxes, bottom_margin_pct=euro_bottom_margin, gap_above_ar=200)
    dxfc.place_Blue_Zero_attached(all_placed_bboxes)
    dxfc.place_tv_screens(all_placed_bboxes, primary_side=Primary)


dxfc.place_lensometer()

# --- Save and close ---
dxfc.close_plan()
