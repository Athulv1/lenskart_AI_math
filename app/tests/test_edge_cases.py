#!/usr/bin/env python3
"""
Edge Case Tests for JSON Generation

Tests edge cases:
- 0 clinic plans (should error)
- 1 clinic plan only
- >10 clinic plans (should warn)
- Empty euro patterns (should warn)
- Negative euro count (should error)
"""

import sys
import os
import json
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from plan_extractors import (
    save_all_plans_to_json,
    validate_plans_data,
    ValidationResult
)


def test_zero_clinic_plans():
    """Test: 0 clinic plans should raise ValueError."""
    print("\n" + "="*60)
    print("🧪 TEST 1: 0 Clinic Plans (should ERROR)")
    print("="*60)
    
    clinic_plans = {"ranked_layouts": []}  # Empty!
    euro_plans = {"all_options": {}}
    
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "test.json")
    
    try:
        # Should raise ValueError
        save_all_plans_to_json(clinic_plans, euro_plans, output_path)
        print("❌ FAIL: Should have raised ValueError")
        result = False
    except ValueError as e:
        print(f"✅ PASS: Correctly raised ValueError")
        print(f"   Error message: {e}")
        result = True
    except Exception as e:
        print(f"❌ FAIL: Wrong exception type: {type(e).__name__}: {e}")
        result = False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return result


def test_one_clinic_plan():
    """Test: 1 clinic plan should work fine."""
    print("\n" + "="*60)
    print("🧪 TEST 2: 1 Clinic Plan Only (should PASS)")
    print("="*60)
    
    clinic_plans = {
        "ranked_layouts": [
            {"Rank": 1, "Placed": True, "fixtures": ["Clinic_regular"]}
        ]
    }
    euro_plans = {"all_options": {}, "required_count": 2}
    
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "single_clinic.json")
    
    try:
        result_data = save_all_plans_to_json(clinic_plans, euro_plans, output_path)
        
        if os.path.exists(output_path):
            print(f"✅ PASS: JSON created successfully")
            print(f"   Clinic layouts: {len(result_data['clinic_plans']['ranked_layouts'])}")
            result = True
        else:
            print("❌ FAIL: JSON file not created")
            result = False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {e}")
        result = False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return result


def test_many_clinic_plans():
    """Test: >10 clinic plans should warn but succeed."""
    print("\n" + "="*60)
    print("🧪 TEST 3: 15 Clinic Plans (should WARN but PASS)")
    print("="*60)
    
    # Create 15 clinic layouts
    clinic_plans = {
        "ranked_layouts": [
            {"Rank": i, "Placed": i == 1, "fixtures": ["Clinic_regular"]}
            for i in range(1, 16)  # 15 layouts
        ]
    }
    euro_plans = {"all_options": {}, "required_count": 5}
    
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "many_clinics.json")
    
    try:
        # First check validation directly
        validation = validate_plans_data(clinic_plans, euro_plans)
        
        has_warning = any("Large number" in w for w in validation.warnings)
        print(f"   Validation warnings: {validation.warnings}")
        
        if has_warning:
            print("✅ Warning about large number of layouts detected")
        else:
            print("⚠️ Expected warning about large number of layouts")
        
        # Should still succeed despite warning
        result_data = save_all_plans_to_json(clinic_plans, euro_plans, output_path)
        
        if os.path.exists(output_path):
            print(f"✅ PASS: JSON created despite warning")
            print(f"   Clinic layouts: {len(result_data['clinic_plans']['ranked_layouts'])}")
            result = True
        else:
            print("❌ FAIL: JSON file not created")
            result = False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {e}")
        result = False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return result


def test_empty_euro_patterns():
    """Test: Empty euro patterns should warn but succeed."""
    print("\n" + "="*60)
    print("🧪 TEST 4: Empty Euro Patterns (should WARN but PASS)")
    print("="*60)
    
    clinic_plans = {
        "ranked_layouts": [{"Rank": 1, "Placed": True}]
    }
    euro_plans = {"all_options": {}}  # Empty!
    
    validation = validate_plans_data(clinic_plans, euro_plans)
    
    has_warning = any("empty" in w.lower() for w in validation.warnings)
    print(f"   Warnings: {validation.warnings}")
    
    if has_warning:
        print("✅ PASS: Warning about empty euro patterns detected")
        return True
    else:
        print("❌ FAIL: Expected warning about empty euro patterns")
        return False


def test_negative_euro_count():
    """Test: Negative euro count should error."""
    print("\n" + "="*60)
    print("🧪 TEST 5: Negative Euro Count (should ERROR)")
    print("="*60)
    
    clinic_plans = {
        "ranked_layouts": [{"Rank": 1, "Placed": True}]
    }
    euro_plans = {"all_options": {}}
    
    validation = validate_plans_data(clinic_plans, euro_plans, required_euro_count=-5)
    
    print(f"   Errors: {validation.errors}")
    
    if not validation.is_valid and any("negative" in e.lower() for e in validation.errors):
        print("✅ PASS: Error for negative euro count detected")
        return True
    else:
        print("❌ FAIL: Expected error for negative euro count")
        return False


def test_high_euro_count():
    """Test: High euro count (>20) should warn."""
    print("\n" + "="*60)
    print("🧪 TEST 6: High Euro Count (25) (should WARN)")
    print("="*60)
    
    clinic_plans = {
        "ranked_layouts": [{"Rank": 1, "Placed": True}]
    }
    euro_plans = {"all_options": {}}
    
    validation = validate_plans_data(clinic_plans, euro_plans, required_euro_count=25)
    
    print(f"   Warnings: {validation.warnings}")
    
    if any("high" in w.lower() for w in validation.warnings):
        print("✅ PASS: Warning for high euro count detected")
        return True
    else:
        print("❌ FAIL: Expected warning for high euro count")
        return False


def test_skip_validation():
    """Test: skip_validation=True should bypass validation."""
    print("\n" + "="*60)
    print("🧪 TEST 7: Skip Validation Flag")
    print("="*60)
    
    clinic_plans = {"ranked_layouts": []}  # Invalid: 0 layouts
    euro_plans = {"all_options": {}}
    
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "skip_validation.json")
    
    try:
        # With skip_validation=True, should NOT raise error
        result_data = save_all_plans_to_json(
            clinic_plans, euro_plans, output_path,
            skip_validation=True
        )
        
        if os.path.exists(output_path):
            print("✅ PASS: JSON created with validation skipped")
            result = True
        else:
            print("❌ FAIL: JSON file not created")
            result = False
    except ValueError as e:
        print(f"❌ FAIL: Should not have raised error with skip_validation=True: {e}")
        result = False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return result


def run_all_tests():
    """Run all edge case tests."""
    print("\n" + "="*60)
    print("🔬 EDGE CASE TESTS FOR JSON GENERATION")
    print("="*60)
    
    tests = [
        ("0 Clinic Plans (Error)", test_zero_clinic_plans),
        ("1 Clinic Plan (OK)", test_one_clinic_plan),
        (">10 Clinic Plans (Warn)", test_many_clinic_plans),
        ("Empty Euro Patterns (Warn)", test_empty_euro_patterns),
        ("Negative Euro Count (Error)", test_negative_euro_count),
        ("High Euro Count (Warn)", test_high_euro_count),
        ("Skip Validation Flag", test_skip_validation),
    ]
    
    results = []
    for name, test_func in tests:
        passed = test_func()
        results.append((name, passed))
    
    # Final Summary
    print("\n" + "="*60)
    print("📊 EDGE CASE TEST SUMMARY")
    print("="*60)
    
    passed_count = 0
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
        if passed:
            passed_count += 1
    
    print(f"\n📈 Results: {passed_count}/{len(results)} tests passed")
    
    if passed_count == len(results):
        print("🎉 ALL EDGE CASE TESTS PASSED!")
        return True
    else:
        print("⚠️ SOME TESTS FAILED")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
