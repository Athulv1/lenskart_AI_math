"""
Test extraction for lane_strategy Euro placement coordinates.

This script validates the extraction of coordinate data from 
lane_strategy sample data.
"""

import json
import os
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Test sample path
SAMPLE_PATH = Path(__file__).parent / "lane_strategy_test_sample.json"


def load_sample_data() -> Dict[str, Any]:
    """Load the lane_strategy test sample."""
    with open(SAMPLE_PATH, 'r') as f:
        return json.load(f)


def extract_center_coordinates(data: Dict[str, Any]) -> List[Tuple[float, float]]:
    """Extract center coordinates from placements."""
    centers = []
    for placement in data.get("placements", []):
        center = placement.get("center", [0, 0])
        centers.append(tuple(center))
    return centers


def extract_corner_coordinates(data: Dict[str, Any]) -> List[Tuple[float, float]]:
    """Extract corner coordinates from placements."""
    corners = []
    for placement in data.get("placements", []):
        corner = placement.get("corner", [0, 0])
        corners.append(tuple(corner))
    return corners


def convert_corner_to_center(
    corner_x: float, 
    corner_y: float, 
    rotated_width: float, 
    rotated_height: float
) -> Tuple[float, float]:
    """Convert corner coordinates to center."""
    return (corner_x + rotated_width / 2, corner_y + rotated_height / 2)


def validate_lane_consistency(data: Dict[str, Any]) -> bool:
    """Validate that fixtures within the same lane share X-coordinate."""
    placements = data.get("placements", [])
    lanes = {}
    
    for p in placements:
        lane_id = p.get("lane_id")
        if p.get("position_in_row") == 0:  # First fixture in row sets lane
            corner_x = p.get("corner", [0, 0])[0]
            if lane_id in lanes:
                if lanes[lane_id] != corner_x:
                    return False  # Lane X changed unexpectedly
            else:
                lanes[lane_id] = corner_x
    return True


def test_coordinate_extraction():
    """Test that coordinates can be extracted correctly."""
    data = load_sample_data()
    
    # Test 1: Sample data loads correctly
    assert data["strategy_name"] == "lane_strategy"
    print("✅ Test 1 PASSED: Sample data loaded correctly")
    
    # Test 2: Extract center coordinates
    centers = extract_center_coordinates(data)
    assert len(centers) == 6
    assert centers[0] == (3387.5, 3820.0)
    print("✅ Test 2 PASSED: Center coordinates extracted correctly")
    
    # Test 3: Extract corner coordinates
    corners = extract_corner_coordinates(data)
    assert len(corners) == 6
    assert corners[0] == (2800.0, 3300.0)
    print("✅ Test 3 PASSED: Corner coordinates extracted correctly")
    
    # Test 4: Corner to center conversion
    corner = corners[0]
    rotated_width = data["placements"][0]["rotated_width"]
    rotated_height = data["placements"][0]["rotated_height"]
    calculated_center = convert_corner_to_center(
        corner[0], corner[1], rotated_width, rotated_height
    )
    expected_center = centers[0]
    assert abs(calculated_center[0] - expected_center[0]) < 0.01
    assert abs(calculated_center[1] - expected_center[1]) < 0.01
    print("✅ Test 4 PASSED: Corner to center conversion verified")
    
    # Test 5: Lane consistency
    assert validate_lane_consistency(data)
    print("✅ Test 5 PASSED: Lane consistency validated")
    
    # Test 6: Rotation is 90 degrees for all placements
    for p in data["placements"]:
        assert p["rotation"] == 90.0
    print("✅ Test 6 PASSED: All placements have 90° rotation")
    
    # Test 7: Lane change detection
    lane_positions = data.get("lane_positions", [])
    assert len(lane_positions) == 2
    assert lane_positions[0]["reason"] == "initial_lane"
    assert lane_positions[1]["reason"] == "blockage_detected"
    print("✅ Test 7 PASSED: Lane change events detected correctly")
    
    # Test 8: Summary statistics
    summary = data.get("summary", {})
    assert summary["total_placed"] == 6
    assert summary["lane_changes"] == 1
    print("✅ Test 8 PASSED: Summary statistics correct")
    
    print("\n" + "="*50)
    print("All 8 tests PASSED! ✅")
    print("="*50)
    
    return True


def print_extraction_summary(data: Dict[str, Any]):
    """Print a summary of extracted coordinates."""
    print("\n" + "="*50)
    print("LANE_STRATEGY EXTRACTION SUMMARY")
    print("="*50)
    
    print(f"\nStrategy: {data['strategy_name']}")
    print(f"Rotation: {data['rotation_degrees']}°")
    print(f"Zone: Y={data['zone']['start_y']} to Y={data['zone']['end_y']}")
    
    print("\nLane Positions:")
    for lane in data.get("lane_positions", []):
        print(f"  Lane {lane['lane_id']}: X={lane['lane_start_x']} "
              f"(row {lane['established_at_row']}, {lane['reason']})")
    
    print("\nPlacements:")
    for p in data.get("placements", []):
        print(f"  [{p['index']}] {p['fixture_name']}: "
              f"center={tuple(p['center'])}, "
              f"corner={tuple(p['corner'])}, "
              f"row={p['row_index']}, lane={p['lane_id']}")
    
    print(f"\nSummary:")
    summary = data.get("summary", {})
    print(f"  Total placed: {summary.get('total_placed', 0)}")
    print(f"  Capacity: {summary.get('capacity', 0)}")
    print(f"  Overflow: {summary.get('overflow', 0)}")
    print(f"  Lane changes: {summary.get('lane_changes', 0)}")


if __name__ == "__main__":
    print("Testing lane_strategy coordinate extraction...\n")
    
    # Run tests
    test_coordinate_extraction()
    
    # Print extraction summary
    data = load_sample_data()
    print_extraction_summary(data)
