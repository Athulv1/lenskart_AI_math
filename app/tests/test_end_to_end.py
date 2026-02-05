#!/usr/bin/env python3
"""
End-to-End Test for JSON Generation

This script tests the complete JSON generation workflow:
1. Load sample clinic and euro plans
2. Generate all 4 euro strategies per clinic plan
3. Write to JSON file
4. Validate JSON structure
5. Verify all components present
"""

import sys
import os
import json
import tempfile
import shutil

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from plan_extractors import (
    save_all_plans_to_json,
    generate_combined_plans,
    get_plans_output_path,
    write_plans_json,
    EURO_STRATEGIES
)


def load_sample_data():
    """Load sample data from test_sample_plan.json."""
    sample_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..', 'schemas', 'test_sample_plan.json'
    )
    
    if not os.path.exists(sample_path):
        raise FileNotFoundError(f"Sample data not found at {sample_path}")
    
    with open(sample_path, 'r') as f:
        return json.load(f)


def test_end_to_end():
    """Run complete end-to-end test."""
    print("=" * 60)
    print("🧪 END-TO-END JSON GENERATION TEST")
    print("=" * 60)
    
    # Create temp directory for output
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "test_floorplan_plans.json")
    
    try:
        # Step 1: Load sample data
        print("\n📂 Step 1: Loading sample data...")
        sample_data = load_sample_data()
        print(f"   ✅ Loaded floorplan: {sample_data.get('floorplan_id', 'unknown')}")
        
        clinic_plans = sample_data.get("clinic_plans", {})
        euro_plans = sample_data.get("euro_plans", {})
        
        num_clinic_layouts = len(clinic_plans.get("ranked_layouts", []))
        print(f"   ✅ Clinic layouts: {num_clinic_layouts}")
        print(f"   ✅ Euro patterns: {len(euro_plans.get('all_options', {}))}")
        
        # Step 2: Test path generation
        print("\n📍 Step 2: Testing path generation...")
        test_dxf = "/path/to/test_floorplan.dxf"
        generated_path = get_plans_output_path(test_dxf)
        expected_path = "/path/to/test_floorplan_plans.json"
        assert generated_path == expected_path, f"Path mismatch: {generated_path}"
        print(f"   ✅ Path generation: {test_dxf} -> {generated_path}")
        
        # Step 3: Generate complete plans
        print("\n🔧 Step 3: Generating complete plans...")
        result = save_all_plans_to_json(
            clinic_plans=clinic_plans,
            euro_plans=euro_plans,
            output_path=output_path,
            floorplan_id="test-e2e-001",
            metadata={
                "proto_value": "16L",
                "total_area_sqft": 1500,
                "test_run": True
            }
        )
        print(f"   ✅ Generated plans with id: {result['floorplan_id']}")
        
        # Step 4: Verify JSON file created
        print("\n📄 Step 4: Verifying JSON file...")
        assert os.path.exists(output_path), "JSON file not created!"
        file_size = os.path.getsize(output_path)
        print(f"   ✅ File created: {output_path}")
        print(f"   ✅ File size: {file_size:,} bytes")
        
        # Check file size is reasonable (between 1KB and 10MB)
        assert 1000 < file_size < 10_000_000, f"File size suspicious: {file_size}"
        print(f"   ✅ File size in reasonable range")
        
        # Step 5: Verify JSON is valid
        print("\n✅ Step 5: Verifying JSON validity...")
        with open(output_path, 'r') as f:
            loaded_data = json.load(f)
        print(f"   ✅ JSON is valid and parseable")
        
        # Step 6: Verify all clinic plans captured
        print("\n🏥 Step 6: Verifying clinic plans...")
        loaded_clinic_plans = loaded_data.get("clinic_plans", {})
        loaded_layouts = loaded_clinic_plans.get("ranked_layouts", [])
        assert len(loaded_layouts) == num_clinic_layouts, \
            f"Expected {num_clinic_layouts} layouts, got {len(loaded_layouts)}"
        print(f"   ✅ All {len(loaded_layouts)} clinic layouts captured")
        
        # Verify each layout has required fields
        for layout in loaded_layouts:
            assert "Rank" in layout, "Layout missing Rank"
            assert "fixtures" in layout, "Layout missing fixtures"
            assert "coordinates" in layout, "Layout missing coordinates"
        print(f"   ✅ All layouts have required fields")
        
        # Step 7: Verify all 4 euro strategies
        print("\n💶 Step 7: Verifying euro strategies...")
        euro_by_strategy = loaded_data.get("euro_plans_by_strategy", {})
        
        expected_strategies = ["strategy_1", "strategy_2", "strategy_3", "strategy_4"]
        for strat in expected_strategies:
            assert strat in euro_by_strategy, f"Missing {strat}"
            strat_data = euro_by_strategy[strat]
            assert "success" in strat_data, f"{strat} missing success flag"
            
            if strat_data["success"]:
                plan = strat_data["plan"]
                assert "strategy_name" in plan, f"{strat} plan missing strategy_name"
                assert "rotation" in plan, f"{strat} plan missing rotation"
                assert "placements" in plan, f"{strat} plan missing placements"
                print(f"   ✅ {strat}: {plan['strategy_name']} ({plan['rotation']}°, "
                      f"{len(plan['placements'])} placements)")
            else:
                print(f"   ⚠️ {strat}: Failed - {strat_data.get('error', 'unknown')}")
        
        # Count successful strategies
        successful = sum(1 for s in euro_by_strategy.values() if s.get("success"))
        print(f"   ✅ {successful}/4 strategies generated successfully")
        
        # Step 8: Verify summary statistics
        print("\n📊 Step 8: Verifying summary...")
        summary = loaded_data.get("summary", {})
        assert "total_clinic_layouts" in summary
        assert "euro_strategies_generated" in summary
        print(f"   ✅ Total clinic layouts: {summary['total_clinic_layouts']}")
        print(f"   ✅ Euro strategies generated: {summary['euro_strategies_generated']}")
        
        # Step 9: Verify metadata
        print("\n📋 Step 9: Verifying metadata...")
        metadata = loaded_data.get("metadata", {})
        assert metadata.get("proto_value") == "16L"
        assert metadata.get("test_run") == True
        print(f"   ✅ Metadata captured correctly")
        
        # Step 10: Test combined plans generation
        print("\n🔗 Step 10: Testing combined plans generation...")
        combinations = generate_combined_plans(clinic_plans, euro_plans)
        expected_combos = num_clinic_layouts * 4
        print(f"   ✅ Generated {len(combinations)} combinations "
              f"({num_clinic_layouts} clinics × 4 strategies = {expected_combos})")
        assert len(combinations) == expected_combos
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎉 ALL END-TO-END TESTS PASSED!")
        print("=" * 60)
        print(f"\n📈 Summary:")
        print(f"   • Clinic layouts: {num_clinic_layouts}")
        print(f"   • Euro strategies: 4")
        print(f"   • Combined plans: {len(combinations)}")
        print(f"   • Output file size: {file_size:,} bytes")
        print(f"   • JSON valid: ✅")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """Main entry point."""
    success = test_end_to_end()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
