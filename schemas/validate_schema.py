#!/usr/bin/env python3
"""
Schema Validation Test Script for Lenskart Floor Plans
Tests the plans_schema.json against sample data files.
"""

import json
import sys
from pathlib import Path

try:
    import jsonschema
    from jsonschema import validate, ValidationError, Draft7Validator
except ImportError:
    print("❌ jsonschema not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "jsonschema"])
    import jsonschema
    from jsonschema import validate, ValidationError, Draft7Validator


def load_json(filepath: str) -> dict:
    """Load JSON file and return parsed content."""
    with open(filepath, 'r') as f:
        return json.load(f)


def validate_schema(schema: dict, data: dict, data_name: str) -> tuple[bool, list]:
    """
    Validate data against schema.
    Returns (is_valid, list_of_errors)
    """
    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(data))
    
    if not errors:
        return True, []
    
    error_messages = []
    for error in errors:
        path = " → ".join(str(p) for p in error.absolute_path) or "root"
        error_messages.append({
            "path": path,
            "message": error.message,
            "validator": error.validator,
            "schema_path": list(error.schema_path)
        })
    
    return False, error_messages


def run_test_cases(schema: dict) -> dict:
    """Run various test cases to thoroughly validate the schema."""
    results = {
        "passed": [],
        "failed": [],
        "warnings": []
    }
    
    # Test Case 1: Valid complete data
    print("\n📋 Test Case 1: Valid complete sample data")
    valid_data = load_json("schemas/test_sample_plan.json")
    is_valid, errors = validate_schema(schema, valid_data, "test_sample_plan.json")
    if is_valid:
        print("   ✅ PASSED: Valid data validates successfully")
        results["passed"].append("Valid complete data")
    else:
        print(f"   ❌ FAILED: {len(errors)} validation errors")
        for e in errors[:5]:  # Show first 5 errors
            print(f"      - {e['path']}: {e['message']}")
        results["failed"].append(("Valid complete data", errors))
    
    # Test Case 2: Missing required field
    print("\n📋 Test Case 2: Missing required field (floorplan_id)")
    invalid_data = valid_data.copy()
    del invalid_data["floorplan_id"]
    is_valid, errors = validate_schema(schema, invalid_data, "missing_field")
    if not is_valid:
        print("   ✅ PASSED: Schema correctly rejects missing required field")
        results["passed"].append("Missing required field detection")
    else:
        print("   ❌ FAILED: Schema should reject missing floorplan_id")
        results["failed"].append(("Missing required field detection", []))
    
    # Test Case 3: Invalid UUID format
    print("\n📋 Test Case 3: Invalid UUID format")
    invalid_data = json.loads(json.dumps(valid_data))
    invalid_data["floorplan_id"] = "not-a-valid-uuid"
    is_valid, errors = validate_schema(schema, invalid_data, "invalid_uuid")
    if not is_valid:
        print("   ✅ PASSED: Schema correctly rejects invalid UUID")
        results["passed"].append("Invalid UUID rejection")
    else:
        print("   ❌ FAILED: Schema should reject invalid UUID format")
        results["failed"].append(("Invalid UUID rejection", []))
    
    # Test Case 4: Invalid clinic fixture name
    print("\n📋 Test Case 4: Invalid clinic fixture name")
    invalid_data = json.loads(json.dumps(valid_data))
    invalid_data["clinic_plans"]["ranked_layouts"][0]["fixtures"] = ["Invalid_Clinic"]
    is_valid, errors = validate_schema(schema, invalid_data, "invalid_fixture")
    if not is_valid:
        print("   ✅ PASSED: Schema correctly rejects invalid fixture name")
        results["passed"].append("Invalid fixture name rejection")
    else:
        print("   ⚠️ WARNING: Schema allows unknown fixture names (may need stricter enum)")
        results["warnings"].append("Schema allows unknown fixture names")
    
    # Test Case 5: Invalid orientation (combo)
    print("\n📋 Test Case 5: Invalid orientation value")
    invalid_data = json.loads(json.dumps(valid_data))
    invalid_data["clinic_plans"]["ranked_layouts"][0]["combo"] = ["H", "X", "V"]
    is_valid, errors = validate_schema(schema, invalid_data, "invalid_combo")
    if not is_valid:
        print("   ✅ PASSED: Schema correctly rejects invalid orientation")
        results["passed"].append("Invalid orientation rejection")
    else:
        print("   ❌ FAILED: Schema should reject 'X' as orientation")
        results["failed"].append(("Invalid orientation rejection", []))
    
    # Test Case 6: Invalid euro pattern name
    print("\n📋 Test Case 6: Invalid euro pattern name")
    invalid_data = json.loads(json.dumps(valid_data))
    invalid_data["euro_plans"]["best_pattern_name"] = "invalid_pattern"
    is_valid, errors = validate_schema(schema, invalid_data, "invalid_pattern")
    if not is_valid:
        print("   ✅ PASSED: Schema correctly rejects invalid pattern name")
        results["passed"].append("Invalid pattern name rejection")
    else:
        print("   ❌ FAILED: Schema should reject invalid pattern name")
        results["failed"].append(("Invalid pattern name rejection", []))
    
    # Test Case 7: Invalid back_room_location
    print("\n📋 Test Case 7: Invalid back_room_location enum")
    invalid_data = json.loads(json.dumps(valid_data))
    invalid_data["metadata"]["back_room_location"] = "top"
    is_valid, errors = validate_schema(schema, invalid_data, "invalid_location")
    if not is_valid:
        print("   ✅ PASSED: Schema correctly rejects invalid location")
        results["passed"].append("Invalid location rejection")
    else:
        print("   ❌ FAILED: Schema should reject 'top' as location")
        results["failed"].append(("Invalid location rejection", []))
    
    # Test Case 8: Empty clinic_plans
    print("\n📋 Test Case 8: Empty ranked_layouts array")
    empty_data = json.loads(json.dumps(valid_data))
    empty_data["clinic_plans"]["ranked_layouts"] = []
    is_valid, errors = validate_schema(schema, empty_data, "empty_layouts")
    if is_valid:
        print("   ✅ PASSED: Schema allows empty ranked_layouts (valid state)")
        results["passed"].append("Empty ranked_layouts allowed")
    else:
        print("   ⚠️ INFO: Schema requires non-empty ranked_layouts")
        results["warnings"].append("Empty ranked_layouts may be valid")
    
    # Test Case 9: Negative rank
    print("\n📋 Test Case 9: Negative or zero Rank value")
    invalid_data = json.loads(json.dumps(valid_data))
    invalid_data["clinic_plans"]["ranked_layouts"][0]["Rank"] = 0
    is_valid, errors = validate_schema(schema, invalid_data, "zero_rank")
    if not is_valid:
        print("   ✅ PASSED: Schema correctly rejects Rank=0")
        results["passed"].append("Zero rank rejection")
    else:
        print("   ⚠️ WARNING: Schema allows Rank=0")
        results["warnings"].append("Rank=0 allowed but may be invalid")
    
    # Test Case 10: Proto value format
    print("\n📋 Test Case 10: Proto value format validation")
    invalid_data = json.loads(json.dumps(valid_data))
    invalid_data["metadata"]["proto_value"] = "16"  # Missing 'L' suffix
    is_valid, errors = validate_schema(schema, invalid_data, "invalid_proto")
    if not is_valid:
        print("   ✅ PASSED: Schema correctly rejects invalid proto format")
        results["passed"].append("Proto format validation")
    else:
        print("   ❌ FAILED: Schema should reject proto without 'L' suffix")
        results["failed"].append(("Proto format validation", []))
    
    return results


def main():
    print("=" * 60)
    print("🔍 LENSKART PLANS SCHEMA VALIDATION TEST")
    print("=" * 60)
    
    # Change to project root
    import os
    os.chdir("/home/athul/lenskart")
    
    # Load schema
    print("\n📂 Loading schema from schemas/plans_schema.json...")
    try:
        schema = load_json("schemas/plans_schema.json")
        print("   ✅ Schema loaded successfully")
    except Exception as e:
        print(f"   ❌ Failed to load schema: {e}")
        return 1
    
    # Validate schema itself
    print("\n🔧 Validating schema structure (meta-validation)...")
    try:
        Draft7Validator.check_schema(schema)
        print("   ✅ Schema is valid JSON Schema Draft-07")
    except jsonschema.SchemaError as e:
        print(f"   ❌ Schema is invalid: {e.message}")
        return 1
    
    # Run all test cases
    results = run_test_cases(schema)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"   ✅ Passed: {len(results['passed'])}")
    print(f"   ❌ Failed: {len(results['failed'])}")
    print(f"   ⚠️ Warnings: {len(results['warnings'])}")
    
    if results["failed"]:
        print("\n❌ FAILED TESTS:")
        for name, errors in results["failed"]:
            print(f"   - {name}")
            if errors:
                for e in errors[:3]:
                    print(f"      Path: {e['path']}")
                    print(f"      Error: {e['message']}")
    
    if results["warnings"]:
        print("\n⚠️ WARNINGS:")
        for warning in results["warnings"]:
            print(f"   - {warning}")
    
    print("\n" + "=" * 60)
    if not results["failed"]:
        print("✅ ALL VALIDATION TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED - SCHEMA ADJUSTMENTS MAY BE NEEDED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
