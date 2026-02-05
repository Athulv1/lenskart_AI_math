#!/usr/bin/env python3
"""
Multi-Store Size JSON Generation Test

Tests JSON generation for 3 different store sizes:
- Small: 30 sqm (1-2 clinics, 2-3 euro fixtures)
- Medium: 45 sqm (2-3 clinics, 4-5 euro fixtures)  
- Large: 60 sqm (3-4 clinics, 6-8 euro fixtures)
"""

import sys
import os
import json
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from plan_extractors import (
    save_all_plans_to_json,
    generate_combined_plans,
    get_plans_output_path,
    EURO_STRATEGIES
)


# ============= MOCK DATA FOR DIFFERENT STORE SIZES =============

SMALL_STORE = {
    "name": "Small Store (30 sqm)",
    "area_sqm": 30,
    "clinic_plans": {
        "total_clinics_required": 1,
        "ranked_layouts": [
            {
                "Rank": 1,
                "Placed": True,
                "score": 1200.0,
                "fixtures": ["Clinic_regular"],
                "combo": ["H"],
                "coordinates": [
                    {"name": "Clinic_regular", "target_center": [3000, 5000], "zone_id": "Zone_1"}
                ]
            }
        ]
    },
    "euro_plans": {
        "required_count": 2,
        "best_pattern_name": "column_wise_even_cols",
        "all_options": {
            "row_wise_even_rows": {
                "count": 2, "rank": 2, "placed": False,
                "placements": {
                    "count_1": {"coordinates": [1500, 2000]},
                    "count_2": {"coordinates": [2500, 2000]}
                }
            },
            "column_wise_even_cols": {
                "count": 3, "rank": 1, "placed": False,
                "placements": {
                    "count_1": {"coordinates": [1500, 2000]},
                    "count_2": {"coordinates": [1500, 3000]},
                    "count_3": {"coordinates": [1500, 4000]}
                }
            }
        }
    }
}

MEDIUM_STORE = {
    "name": "Medium Store (45 sqm)",
    "area_sqm": 45,
    "clinic_plans": {
        "total_clinics_required": 2,
        "ranked_layouts": [
            {
                "Rank": 1,
                "Placed": True,
                "score": 1800.0,
                "fixtures": ["ROC_clinic", "Clinic_regular"],
                "combo": ["H", "V"],
                "coordinates": [
                    {"name": "ROC_clinic", "target_center": [5000, 8000], "zone_id": "Zone_1"},
                    {"name": "Clinic_regular", "target_center": [3000, 8000], "zone_id": "Zone_1"}
                ]
            },
            {
                "Rank": 2,
                "Placed": False,
                "score": 2100.0,
                "fixtures": ["Clinic_with_sink", "Clinic_regular"],
                "combo": ["H", "H"],
                "coordinates": [
                    {"name": "Clinic_with_sink", "target_center": [4500, 8000], "zone_id": "Zone_2"},
                    {"name": "Clinic_regular", "target_center": [2500, 8000], "zone_id": "Zone_2"}
                ]
            }
        ]
    },
    "euro_plans": {
        "required_count": 4,
        "best_pattern_name": "column_wise_even_cols",
        "all_options": {
            "row_wise_even_rows": {
                "count": 4, "rank": 2, "placed": False,
                "placements": {
                    "count_1": {"coordinates": [1500, 2500]},
                    "count_2": {"coordinates": [3000, 2500]},
                    "count_3": {"coordinates": [1500, 4500]},
                    "count_4": {"coordinates": [3000, 4500]}
                }
            },
            "column_wise_even_cols": {
                "count": 5, "rank": 1, "placed": False,
                "placements": {
                    "count_1": {"coordinates": [1500, 2500]},
                    "count_2": {"coordinates": [1500, 3500]},
                    "count_3": {"coordinates": [1500, 4500]},
                    "count_4": {"coordinates": [3500, 2500]},
                    "count_5": {"coordinates": [3500, 3500]}
                }
            }
        }
    }
}

LARGE_STORE = {
    "name": "Large Store (60 sqm)",
    "area_sqm": 60,
    "clinic_plans": {
        "total_clinics_required": 3,
        "ranked_layouts": [
            {
                "Rank": 1,
                "Placed": True,
                "score": 1500.0,
                "fixtures": ["ROC_clinic", "Clinic_with_sink", "Clinic_regular"],
                "combo": ["H", "V", "V"],
                "coordinates": [
                    {"name": "ROC_clinic", "target_center": [7000, 10000], "zone_id": "Zone_1"},
                    {"name": "Clinic_with_sink", "target_center": [5000, 10000], "zone_id": "Zone_1"},
                    {"name": "Clinic_regular", "target_center": [3000, 10000], "zone_id": "Zone_1"}
                ]
            },
            {
                "Rank": 2,
                "Placed": False,
                "score": 1800.0,
                "fixtures": ["ROC_clinic", "Clinic_regular", "Clinic_regular"],
                "combo": ["H", "H", "V"],
                "coordinates": [
                    {"name": "ROC_clinic", "target_center": [6500, 10000], "zone_id": "Zone_2"},
                    {"name": "Clinic_regular", "target_center": [4500, 10000], "zone_id": "Zone_2"},
                    {"name": "Clinic_regular", "target_center": [2500, 10000], "zone_id": "Zone_2"}
                ]
            },
            {
                "Rank": 3,
                "Placed": False,
                "score": 2100.0,
                "fixtures": ["Clinic_with_sink", "Clinic_with_sink"],
                "combo": ["H", "H"],
                "coordinates": [
                    {"name": "Clinic_with_sink", "target_center": [5500, 10000], "zone_id": "Zone_3"},
                    {"name": "Clinic_with_sink", "target_center": [3500, 10000], "zone_id": "Zone_3"}
                ]
            }
        ]
    },
    "euro_plans": {
        "required_count": 6,
        "best_pattern_name": "column_wise_even_cols",
        "all_options": {
            "row_wise_even_rows": {
                "count": 6, "rank": 2, "placed": False,
                "placements": {
                    "count_1": {"coordinates": [1500, 2500]},
                    "count_2": {"coordinates": [3500, 2500]},
                    "count_3": {"coordinates": [5500, 2500]},
                    "count_4": {"coordinates": [1500, 5000]},
                    "count_5": {"coordinates": [3500, 5000]},
                    "count_6": {"coordinates": [5500, 5000]}
                }
            },
            "row_wise_odd_rows": {
                "count": 5, "rank": 4, "placed": False,
                "placements": {
                    "count_1": {"coordinates": [2500, 3750]},
                    "count_2": {"coordinates": [4500, 3750]},
                    "count_3": {"coordinates": [2500, 6250]},
                    "count_4": {"coordinates": [4500, 6250]},
                    "count_5": {"coordinates": [2500, 8750]}
                }
            },
            "column_wise_even_cols": {
                "count": 8, "rank": 1, "placed": False,
                "placements": {
                    "count_1": {"coordinates": [1500, 2500]},
                    "count_2": {"coordinates": [1500, 3750]},
                    "count_3": {"coordinates": [1500, 5000]},
                    "count_4": {"coordinates": [1500, 6250]},
                    "count_5": {"coordinates": [4000, 2500]},
                    "count_6": {"coordinates": [4000, 3750]},
                    "count_7": {"coordinates": [4000, 5000]},
                    "count_8": {"coordinates": [4000, 6250]}
                }
            },
            "column_wise_odd_cols": {
                "count": 7, "rank": 3, "placed": False,
                "placements": {
                    "count_1": {"coordinates": [2750, 2500]},
                    "count_2": {"coordinates": [2750, 3750]},
                    "count_3": {"coordinates": [2750, 5000]},
                    "count_4": {"coordinates": [2750, 6250]},
                    "count_5": {"coordinates": [5250, 2500]},
                    "count_6": {"coordinates": [5250, 3750]},
                    "count_7": {"coordinates": [5250, 5000]}
                }
            }
        }
    }
}


def run_store_test(store_data: dict, temp_dir: str, test_num: int) -> dict:
    """Run test for a single store size."""
    print(f"\n{'='*60}")
    print(f"🧪 TEST {test_num}: {store_data['name']}")
    print(f"{'='*60}")
    
    # Create mock DXF path
    mock_dxf_name = f"store_{store_data['area_sqm']}sqm.dxf"
    mock_dxf_path = os.path.join(temp_dir, mock_dxf_name)
    
    # Get expected JSON output path
    json_output_path = get_plans_output_path(mock_dxf_path)
    
    result = {
        "store_name": store_data["name"],
        "area_sqm": store_data["area_sqm"],
        "json_path": json_output_path,
        "success": False,
        "json_valid": False,
        "clinic_count": 0,
        "euro_strategies": 0,
        "file_size": 0
    }
    
    try:
        # Generate JSON
        print(f"📁 Output path: {json_output_path}")
        
        plans_result = save_all_plans_to_json(
            clinic_plans=store_data["clinic_plans"],
            euro_plans=store_data["euro_plans"],
            output_path=json_output_path,
            floorplan_id=f"test-{store_data['area_sqm']}sqm",
            metadata={
                "area_sqm": store_data["area_sqm"],
                "test_run": True
            },
            required_euro_count=store_data["euro_plans"]["required_count"]
        )
        
        # Check if file was created
        if os.path.exists(json_output_path):
            result["success"] = True
            result["file_size"] = os.path.getsize(json_output_path)
            print(f"✅ JSON file created ({result['file_size']:,} bytes)")
            
            # Verify JSON validity
            try:
                with open(json_output_path, 'r') as f:
                    loaded = json.load(f)
                result["json_valid"] = True
                print(f"✅ JSON is valid")
                
                # Count clinic layouts
                clinic_layouts = loaded.get("clinic_plans", {}).get("ranked_layouts", [])
                result["clinic_count"] = len(clinic_layouts)
                print(f"✅ Clinic layouts: {result['clinic_count']}")
                
                # Count euro strategies
                euro_strats = loaded.get("euro_plans_by_strategy", {})
                successful_strats = sum(1 for v in euro_strats.values() if v.get("success"))
                result["euro_strategies"] = successful_strats
                print(f"✅ Euro strategies: {result['euro_strategies']}/4")
                
                # Show summary
                summary = loaded.get("summary", {})
                print(f"📊 Summary: {json.dumps(summary, indent=2)}")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON is INVALID: {e}")
        else:
            print(f"❌ JSON file NOT created")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    return result


def run_all_tests():
    """Run tests for all store sizes."""
    print("\n" + "="*60)
    print("🏪 MULTI-STORE JSON GENERATION TEST")
    print("="*60)
    
    temp_dir = tempfile.mkdtemp()
    print(f"📂 Temp directory: {temp_dir}")
    
    stores = [SMALL_STORE, MEDIUM_STORE, LARGE_STORE]
    results = []
    
    try:
        for i, store in enumerate(stores, start=1):
            result = run_store_test(store, temp_dir, i)
            results.append(result)
        
        # Final Summary
        print("\n" + "="*60)
        print("📊 FINAL RESULTS SUMMARY")
        print("="*60)
        
        all_passed = True
        for r in results:
            status = "✅ PASS" if (r["success"] and r["json_valid"]) else "❌ FAIL"
            if not (r["success"] and r["json_valid"]):
                all_passed = False
            print(f"\n{r['store_name']}:")
            print(f"  Status: {status}")
            print(f"  File size: {r['file_size']:,} bytes")
            print(f"  Clinic layouts: {r['clinic_count']}")
            print(f"  Euro strategies: {r['euro_strategies']}/4")
        
        print("\n" + "="*60)
        if all_passed:
            print("🎉 ALL TESTS PASSED!")
        else:
            print("⚠️ SOME TESTS FAILED")
        print("="*60)
        
        # Verify different plan counts
        print("\n📈 Plan Count Verification:")
        clinic_counts = [r["clinic_count"] for r in results]
        print(f"  Clinic counts: {clinic_counts}")
        if len(set(clinic_counts)) > 1:
            print("  ✅ Different clinic counts across stores")
        else:
            print("  ⚠️ Same clinic count for all stores")
        
        return all_passed
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
