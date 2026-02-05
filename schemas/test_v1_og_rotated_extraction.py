"""
Test extraction for v1_og_rotated Euro placement coordinates.

This script validates the extraction of coordinate data from 
v1_og_rotated sample data, including row-size-triggered lane changes.
"""

import json
from pathlib import Path
from typing import List, Tuple, Dict, Any

SAMPLE_PATH = Path(__file__).parent / "v1_og_rotated_test_sample.json"


def load_sample_data() -> Dict[str, Any]:
    """Load the v1_og_rotated test sample."""
    with open(SAMPLE_PATH, 'r') as f:
        return json.load(f)


def extract_lane_changes(data: Dict[str, Any]) -> List[Dict]:
    """Extract lane change events."""
    return data.get("lane_changes", [])


def extract_row_size_changes(data: Dict[str, Any]) -> List[Dict]:
    """Extract row size change events specifically."""
    return [lc for lc in data.get("lane_changes", []) 
            if lc.get("reason") == "row_size_changed"]


def validate_lane_fixture_count(data: Dict[str, Any]) -> bool:
    """Validate that lane_fixture_count matches actual fixtures in each lane."""
    placements = data.get("placements", [])
    lanes = {}
    
    for p in placements:
        lane_id = p.get("lane_id")
        expected_count = p.get("lane_fixture_count")
        row_index = p.get("row_index")
        
        key = (lane_id, row_index)
        if key not in lanes:
            lanes[key] = {"expected": expected_count, "actual": 0}
        lanes[key]["actual"] += 1
    
    # For each row, verify count matches expected
    for (lane_id, row_index), counts in lanes.items():
        if counts["actual"] != counts["expected"]:
            print(f"  ❌ Lane {lane_id}, Row {row_index}: "
                  f"expected {counts['expected']}, got {counts['actual']}")
            return False
    return True


def test_coordinate_extraction():
    """Test that v1_og coordinates can be extracted correctly."""
    data = load_sample_data()
    
    # Test 1: Sample data loads correctly
    assert data["strategy_name"] == "v1_og_rotated"
    assert data["rotation_degrees"] == 90.0
    print("✅ Test 1 PASSED: Sample data loaded correctly")
    
    # Test 2: GAP_ABOVE_QMS is 50mm (key difference from lane_strategy)
    assert data["parameters"]["GAP_ABOVE_QMS"] == 50.0
    print("✅ Test 2 PASSED: GAP_ABOVE_QMS = 50.0mm (different from lane_strategy)")
    
    # Test 3: Extract lane changes
    lane_changes = extract_lane_changes(data)
    assert len(lane_changes) >= 2  # At least initial + one row size change
    print("✅ Test 3 PASSED: Lane changes extracted")
    
    # Test 4: Row size change detected
    row_size_changes = extract_row_size_changes(data)
    assert len(row_size_changes) >= 1
    assert row_size_changes[0]["reason"] == "row_size_changed"
    print("✅ Test 4 PASSED: Row size change event detected")
    
    # Test 5: lane_fixture_count tracked
    for lc in lane_changes:
        assert "lane_fixture_count" in lc
    print("✅ Test 5 PASSED: lane_fixture_count tracked in lane changes")
    
    # Test 6: Validate lane_fixture_count matches actual placement
    assert validate_lane_fixture_count(data)
    print("✅ Test 6 PASSED: Fixture counts match lane_fixture_count")
    
    # Test 7: All placements have lane_fixture_count field
    for p in data["placements"]:
        assert "lane_fixture_count" in p
    print("✅ Test 7 PASSED: All placements have lane_fixture_count")
    
    # Test 8: Row 0 has 3 fixtures, Row 3 has 2 fixtures (row size change scenario)
    row_0_fixtures = [p for p in data["placements"] if p["row_index"] == 0]
    row_3_fixtures = [p for p in data["placements"] if p["row_index"] == 3]
    assert len(row_0_fixtures) == 3
    assert len(row_3_fixtures) == 2
    print("✅ Test 8 PASSED: Row size change verified (3 → 2)")
    
    # Test 9: Coordinate format validation
    first_placement = data["placements"][0]
    center = first_placement["center"]
    corner = first_placement["corner"]
    rw = first_placement["rotated_width"]
    rh = first_placement["rotated_height"]
    
    # Center should be corner + half dimensions
    expected_cx = corner[0] + rw / 2
    expected_cy = corner[1] + rh / 2
    assert abs(center[0] - expected_cx) < 0.01
    assert abs(center[1] - expected_cy) < 0.01
    print("✅ Test 9 PASSED: Center coordinate calculation verified")
    
    # Test 10: Summary statistics
    summary = data.get("summary", {})
    assert summary["row_size_changes"] >= 1
    print("✅ Test 10 PASSED: Summary tracks row_size_changes count")
    
    print("\n" + "="*50)
    print("All 10 tests PASSED! ✅")
    print("="*50)
    return True


def print_extraction_summary(data: Dict[str, Any]):
    """Print a summary of extracted coordinates."""
    print("\n" + "="*50)
    print("V1_OG_ROTATED EXTRACTION SUMMARY")
    print("="*50)
    
    print(f"\nStrategy: {data['strategy_name']}")
    print(f"Rotation: {data['rotation_degrees']}°")
    print(f"GAP_ABOVE_QMS: {data['parameters']['GAP_ABOVE_QMS']}mm")
    
    print("\nLane Changes (including row size changes):")
    for lc in data.get("lane_changes", []):
        print(f"  Lane {lc['lane_id']}: X={lc['lane_start_x']}, "
              f"count={lc['lane_fixture_count']}, "
              f"row={lc['established_at_row']}, "
              f"reason={lc['reason']}")
    
    print("\nPlacements by Row:")
    rows = {}
    for p in data.get("placements", []):
        row = p["row_index"]
        if row not in rows:
            rows[row] = []
        rows[row].append(p)
    
    for row in sorted(rows.keys()):
        print(f"\n  Row {row} ({len(rows[row])} fixtures, lane_count={rows[row][0]['lane_fixture_count']}):")
        for p in rows[row]:
            print(f"    [{p['index']}] center={tuple(p['center'])}, lane={p['lane_id']}")


if __name__ == "__main__":
    print("Testing v1_og_rotated coordinate extraction...\n")
    test_coordinate_extraction()
    
    data = load_sample_data()
    print_extraction_summary(data)
