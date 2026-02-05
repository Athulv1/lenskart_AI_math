"""
Test extraction for v2_og_non_rotated Euro placement coordinates.

This script validates the extraction of coordinate data from 
v2_og_non_rotated sample data, focusing on ZERO rotation specifics.
"""

import json
from pathlib import Path
from typing import List, Tuple, Dict, Any

SAMPLE_PATH = Path(__file__).parent / "v2_og_non_rotated_test_sample.json"


def load_sample_data() -> Dict[str, Any]:
    """Load the v2_og_non_rotated test sample."""
    with open(SAMPLE_PATH, 'r') as f:
        return json.load(f)


def validate_zero_rotation(data: Dict[str, Any]) -> bool:
    """Validate that all placements have 0° rotation."""
    for p in data.get("placements", []):
        if p.get("rotation") != 0.0:
            return False
    return True


def validate_fixed_horizontal_gap(data: Dict[str, Any]) -> bool:
    """Validate fixed 5mm horizontal gap is used."""
    return data.get("parameters", {}).get("horizontal_gap") == 5.0


def validate_original_dimensions(data: Dict[str, Any]) -> bool:
    """Validate that original dimensions are used (not swapped)."""
    for p in data.get("placements", []):
        # Width should be 1040, height should be 1175 (original, not swapped)
        if p.get("width") != 1040.0 or p.get("height") != 1175.0:
            return False
    return True


def validate_center_calculation(data: Dict[str, Any]) -> bool:
    """Validate center = corner + dimension/2 (using original dimensions)."""
    for p in data.get("placements", []):
        corner = p.get("corner", [0, 0])
        center = p.get("center", [0, 0])
        width = p.get("width", 0)
        height = p.get("height", 0)
        
        expected_cx = corner[0] + width / 2
        expected_cy = corner[1] + height / 2
        
        if abs(center[0] - expected_cx) > 0.01 or abs(center[1] - expected_cy) > 0.01:
            return False
    return True


def test_coordinate_extraction():
    """Test that v2_og coordinates can be extracted correctly."""
    data = load_sample_data()
    
    # Test 1: Sample data loads correctly
    assert data["strategy_name"] == "v2_og_non_rotated"
    print("✅ Test 1 PASSED: Sample data loaded correctly")
    
    # Test 2: Rotation is ZERO (key difference!)
    assert data["rotation_degrees"] == 0.0
    print("✅ Test 2 PASSED: Strategy uses 0° rotation")
    
    # Test 3: All placements have 0° rotation
    assert validate_zero_rotation(data)
    print("✅ Test 3 PASSED: All placements have 0° rotation")
    
    # Test 4: Fixed horizontal gap = 5.0mm
    assert validate_fixed_horizontal_gap(data)
    print("✅ Test 4 PASSED: Fixed horizontal_gap = 5.0mm")
    
    # Test 5: Fixed vertical spacing = 1200mm
    assert data["parameters"]["vertical_row_spacing"] == 1200.0
    print("✅ Test 5 PASSED: Fixed vertical_row_spacing = 1200mm")
    
    # Test 6: Original dimensions used (not swapped)
    assert validate_original_dimensions(data)
    print("✅ Test 6 PASSED: Original dimensions used (width=1040, height=1175)")
    
    # Test 7: Center calculation uses original dimensions
    assert validate_center_calculation(data)
    print("✅ Test 7 PASSED: Center calculation verified with original dimensions")
    
    # Test 8: Max fixtures per row can be > 3 (up to 5)
    row_0_count = sum(1 for p in data["placements"] if p["row_index"] == 0)
    assert row_0_count == 4  # More than max 3 for rotated strategies
    print("✅ Test 8 PASSED: More fixtures per row (4) than rotated strategies (max 3)")
    
    # Test 9: Row size change detected (4 → 3)
    row_sizes = {}
    for p in data["placements"]:
        row = p["row_index"]
        row_sizes[row] = row_sizes.get(row, 0) + 1
    assert row_sizes[0] == 4 and row_sizes[2] == 3
    print("✅ Test 9 PASSED: Row size change (4 → 3) verified")
    
    # Test 10: Walking margin is 0.70 (higher than rotated 0.50)
    margin_str = data["parameters"]["walking_space_margin"]
    assert "0.70" in margin_str
    print("✅ Test 10 PASSED: Walking margin is 70% (higher than rotated 50%)")
    
    print("\n" + "="*50)
    print("All 10 tests PASSED! ✅")
    print("="*50)
    return True


def print_extraction_summary(data: Dict[str, Any]):
    """Print a summary of extracted coordinates."""
    print("\n" + "="*50)
    print("V2_OG_NON_ROTATED EXTRACTION SUMMARY")
    print("="*50)
    
    print(f"\nStrategy: {data['strategy_name']}")
    print(f"Rotation: {data['rotation_degrees']}° (ZERO - no rotation)")
    
    params = data["parameters"]
    print(f"\nFixed Parameters (NOT dynamic):")
    print(f"  horizontal_gap: {params['horizontal_gap']}mm")
    print(f"  vertical_row_spacing: {params['vertical_row_spacing']}mm")
    print(f"  max_fixtures_per_row: {params['max_fixtures_per_row']}")
    
    print("\nDimensions (original, not swapped):")
    p0 = data["placements"][0]
    print(f"  width: {p0['width']}mm (original fixture width)")
    print(f"  height: {p0['height']}mm (original fixture height)")
    
    print("\nPlacements by Row:")
    rows = {}
    for p in data.get("placements", []):
        row = p["row_index"]
        if row not in rows:
            rows[row] = []
        rows[row].append(p)
    
    for row in sorted(rows.keys()):
        print(f"\n  Row {row} ({len(rows[row])} fixtures):")
        for p in rows[row]:
            print(f"    [{p['index']}] center={tuple(p['center'])}, "
                  f"rotation={p['rotation']}°")


if __name__ == "__main__":
    print("Testing v2_og_non_rotated coordinate extraction...\n")
    test_coordinate_extraction()
    
    data = load_sample_data()
    print_extraction_summary(data)
