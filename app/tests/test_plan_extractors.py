#!/usr/bin/env python3
"""
Unit Tests for Coordinate Extraction Helpers

Tests the plan_extractors module with various scenarios including:
- Different orientations (H/V)
- Different mirror scales
- Edge cases and error handling
- Vec2 conversion
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plan_extractors import (
    extract_clinic_coordinates,
    extract_all_clinic_coordinates,
    extract_euro_coordinates,
    _vec2_to_tuple,
    _safe_get,
    ClinicCoordinate,
    EuroCoordinate
)


class TestVec2Conversion(unittest.TestCase):
    """Test Vec2 and coordinate conversion functions."""
    
    def test_list_conversion(self):
        """Test conversion from list."""
        result = _vec2_to_tuple([100.5, 200.75])
        self.assertEqual(result, (100.5, 200.75))
    
    def test_tuple_conversion(self):
        """Test conversion from tuple."""
        result = _vec2_to_tuple((300.0, 400.0))
        self.assertEqual(result, (300.0, 400.0))
    
    def test_list_with_extra_elements(self):
        """Test list with more than 2 elements."""
        result = _vec2_to_tuple([1.0, 2.0, 3.0])
        self.assertEqual(result, (1.0, 2.0))
    
    def test_object_with_xy_attributes(self):
        """Test object with x, y attributes."""
        class MockVec2:
            x = 500.0
            y = 600.0
        result = _vec2_to_tuple(MockVec2())
        self.assertEqual(result, (500.0, 600.0))
    
    def test_none_raises_error(self):
        """Test that None raises ValueError."""
        with self.assertRaises(ValueError):
            _vec2_to_tuple(None)
    
    def test_short_list_raises_error(self):
        """Test that single-element list raises error."""
        with self.assertRaises(ValueError):
            _vec2_to_tuple([100.0])
    
    def test_string_raises_error(self):
        """Test that string raises error."""
        with self.assertRaises(ValueError):
            _vec2_to_tuple("100, 200")


class TestSafeGet(unittest.TestCase):
    """Test _safe_get helper function."""
    
    def test_existing_key(self):
        """Test getting existing key."""
        data = {"name": "test", "value": 123}
        self.assertEqual(_safe_get(data, "name"), "test")
    
    def test_missing_key_with_default(self):
        """Test missing key returns default."""
        data = {"name": "test"}
        self.assertEqual(_safe_get(data, "missing", default="default"), "default")
    
    def test_required_missing_raises(self):
        """Test required missing key raises error."""
        data = {"name": "test"}
        with self.assertRaises(ValueError):
            _safe_get(data, "missing", required=True)


class TestClinicCoordinateExtraction(unittest.TestCase):
    """Test clinic coordinate extraction with various scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_layout_horizontal = {
            "Rank": 1,
            "Placed": False,
            "score": 1500.0,
            "fixtures": ["ROC_clinic", "Clinic_with_sink"],
            "combo": ["H", "H"],
            "gaps": [-100.0, 0.0],
            "coordinates": [
                {
                    "name": "ROC_clinic",
                    "target_center": [8000.0, 12000.0],
                    "mirror_scale": [1.0, 1.0],
                    "bottom_y": 10000.0,
                    "zone_id": "Zone_1"
                },
                {
                    "name": "Clinic_with_sink",
                    "target_center": [5500.0, 12000.0],
                    "mirror_scale": [1.0, 1.0],
                    "bottom_y": 10000.0,
                    "zone_id": "Zone_1"
                }
            ]
        }
        
        self.sample_layout_vertical = {
            "Rank": 2,
            "Placed": False,
            "score": 2000.0,
            "fixtures": ["ROC_clinic", "Clinic_regular"],
            "combo": ["V", "V"],
            "gaps": [800.0, 0.0],
            "coordinates": [
                {
                    "name": "ROC_clinic",
                    "target_center": [7000.0, 11500.0],
                    "mirror_scale": [1.0, -1.0],
                    "bottom_y": 9500.0,
                    "zone_id": "Zone_2"
                },
                {
                    "name": "Clinic_regular",
                    "target_center": [4500.0, 11500.0],
                    "mirror_scale": [1.0, 1.0],
                    "bottom_y": 9500.0,
                    "zone_id": "Zone_2"
                }
            ]
        }
        
        self.sample_layout_mixed = {
            "Rank": 3,
            "Placed": False,
            "score": 1800.0,
            "fixtures": ["ROC_clinic", "Clinic_with_sink", "Clinic_regular"],
            "combo": ["H", "V", "V"],
            "gaps": [-100.0, 800.0, 0.0],
            "coordinates": [
                {
                    "name": "ROC_clinic",
                    "target_center": [8500.0, 13000.0],
                    "mirror_scale": [1.0, 1.0],
                    "bottom_y": 11000.0,
                    "zone_id": "Zone_1"
                },
                {
                    "name": "Clinic_with_sink",
                    "target_center": [6000.0, 13000.0],
                    "mirror_scale": [1.0, -1.0],
                    "bottom_y": 11200.0,
                    "zone_id": "Zone_1"
                },
                {
                    "name": "Clinic_regular",
                    "target_center": [3000.0, 13000.0],
                    "mirror_scale": [-1.0, 1.0],
                    "bottom_y": 11100.0,
                    "zone_id": "Zone_1"
                }
            ]
        }
    
    def test_horizontal_orientation_extraction(self):
        """Test extraction of horizontal (H) orientation clinics."""
        coords = extract_clinic_coordinates(self.sample_layout_horizontal)
        
        self.assertEqual(len(coords), 2)
        
        # First clinic
        self.assertEqual(coords[0].name, "ROC_clinic")
        self.assertEqual(coords[0].orientation, "H")
        self.assertEqual(coords[0].rotation, 0.0)
        self.assertEqual(coords[0].target_center, (8000.0, 12000.0))
        self.assertEqual(coords[0].mirror_scale, (1.0, 1.0))
        
        # Second clinic
        self.assertEqual(coords[1].name, "Clinic_with_sink")
        self.assertEqual(coords[1].orientation, "H")
        self.assertEqual(coords[1].rotation, 0.0)
    
    def test_vertical_orientation_extraction(self):
        """Test extraction of vertical (V) orientation clinics."""
        coords = extract_clinic_coordinates(self.sample_layout_vertical)
        
        self.assertEqual(len(coords), 2)
        
        # First clinic - V orientation with mirror
        self.assertEqual(coords[0].name, "ROC_clinic")
        self.assertEqual(coords[0].orientation, "V")
        self.assertEqual(coords[0].rotation, 90.0)
        self.assertEqual(coords[0].mirror_scale, (1.0, -1.0))
        
        # Second clinic - V orientation no mirror
        self.assertEqual(coords[1].name, "Clinic_regular")
        self.assertEqual(coords[1].orientation, "V")
        self.assertEqual(coords[1].rotation, 90.0)
        self.assertEqual(coords[1].mirror_scale, (1.0, 1.0))
    
    def test_mixed_orientation_extraction(self):
        """Test extraction with mixed H and V orientations."""
        coords = extract_clinic_coordinates(self.sample_layout_mixed)
        
        self.assertEqual(len(coords), 3)
        
        # Check orientations
        self.assertEqual(coords[0].orientation, "H")
        self.assertEqual(coords[0].rotation, 0.0)
        
        self.assertEqual(coords[1].orientation, "V")
        self.assertEqual(coords[1].rotation, 90.0)
        
        self.assertEqual(coords[2].orientation, "V")
        self.assertEqual(coords[2].rotation, 90.0)
    
    def test_mirror_scale_variations(self):
        """Test different mirror scale values."""
        coords = extract_clinic_coordinates(self.sample_layout_mixed)
        
        # No mirror
        self.assertEqual(coords[0].mirror_scale, (1.0, 1.0))
        
        # Vertical flip
        self.assertEqual(coords[1].mirror_scale, (1.0, -1.0))
        
        # Horizontal flip
        self.assertEqual(coords[2].mirror_scale, (-1.0, 1.0))
    
    def test_zone_id_extraction(self):
        """Test zone_id is correctly extracted."""
        coords = extract_clinic_coordinates(self.sample_layout_horizontal)
        self.assertEqual(coords[0].zone_id, "Zone_1")
        
        coords2 = extract_clinic_coordinates(self.sample_layout_vertical)
        self.assertEqual(coords2[0].zone_id, "Zone_2")
    
    def test_bottom_y_extraction(self):
        """Test bottom_y is correctly extracted."""
        coords = extract_clinic_coordinates(self.sample_layout_horizontal)
        self.assertEqual(coords[0].bottom_y, 10000.0)
    
    def test_all_coordinates_captured(self):
        """Test all coordinates are captured from layout."""
        coords = extract_clinic_coordinates(self.sample_layout_mixed)
        
        # Verify count
        self.assertEqual(len(coords), 3)
        
        # Verify all names captured
        names = [c.name for c in coords]
        self.assertIn("ROC_clinic", names)
        self.assertIn("Clinic_with_sink", names)
        self.assertIn("Clinic_regular", names)
        
        # Verify all coordinates are tuples with 2 elements
        for coord in coords:
            self.assertIsInstance(coord.target_center, tuple)
            self.assertEqual(len(coord.target_center), 2)
            self.assertIsInstance(coord.target_center[0], float)
            self.assertIsInstance(coord.target_center[1], float)
    
    def test_to_dict_conversion(self):
        """Test ClinicCoordinate.to_dict() method."""
        coords = extract_clinic_coordinates(self.sample_layout_horizontal)
        dict_output = coords[0].to_dict()
        
        self.assertIn("name", dict_output)
        self.assertIn("target_center", dict_output)
        self.assertIn("mirror_scale", dict_output)
        self.assertIn("zone_id", dict_output)
        self.assertIn("orientation", dict_output)
        self.assertIn("rotation", dict_output)
        
        # Verify list conversion for JSON compatibility
        self.assertIsInstance(dict_output["target_center"], list)
        self.assertIsInstance(dict_output["mirror_scale"], list)
    
    def test_empty_layout_error(self):
        """Test error handling for empty layout."""
        empty_layout = {
            "fixtures": [],
            "combo": [],
            "coordinates": []
        }
        coords = extract_clinic_coordinates(empty_layout)
        self.assertEqual(len(coords), 0)
    
    def test_missing_required_field_error(self):
        """Test error when required field is missing."""
        invalid_layout = {
            "fixtures": ["ROC_clinic"],
            "combo": ["H"]
            # Missing 'coordinates'
        }
        with self.assertRaises(ValueError):
            extract_clinic_coordinates(invalid_layout)
    
    def test_mismatched_arrays_error(self):
        """Test error when fixtures and combo lengths don't match."""
        mismatched_layout = {
            "fixtures": ["ROC_clinic", "Clinic_with_sink"],
            "combo": ["H"],  # Only one orientation for two fixtures
            "coordinates": [
                {"name": "ROC_clinic", "target_center": [100, 200], "zone_id": "Zone_1"}
            ]
        }
        with self.assertRaises(ValueError):
            extract_clinic_coordinates(mismatched_layout)


class TestEuroCoordinateExtraction(unittest.TestCase):
    """Test Euro coordinate extraction."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_euro_plans = {
            "required_count": 6,
            "best_pattern_name": "column_wise_even_cols",
            "all_options": {
                "row_wise_even_rows": {
                    "count": 4,
                    "rank": 2,
                    "placed": False,
                    "placements": {
                        "count_1": {"coordinates": [1000.0, 2000.0]},
                        "count_2": {"coordinates": [2000.0, 2000.0]},
                        "count_3": {"coordinates": [1000.0, 3500.0]},
                        "count_4": {"coordinates": [2000.0, 3500.0]}
                    }
                },
                "column_wise_even_cols": {
                    "count": 6,
                    "rank": 1,
                    "placed": False,
                    "placements": {
                        "count_1": {"coordinates": [1000.0, 2000.0]},
                        "count_2": {"coordinates": [1000.0, 3000.0]},
                        "count_3": {"coordinates": [1000.0, 4000.0]},
                        "count_4": {"coordinates": [3000.0, 2000.0]},
                        "count_5": {"coordinates": [3000.0, 3000.0]},
                        "count_6": {"coordinates": [3000.0, 4000.0]}
                    }
                }
            }
        }
    
    def test_best_pattern_extraction(self):
        """Test extraction using best pattern (default)."""
        coords = extract_euro_coordinates(self.sample_euro_plans)
        
        self.assertEqual(len(coords), 6)
        self.assertEqual(coords[0].pattern_name, "column_wise_even_cols")
    
    def test_specific_pattern_extraction(self):
        """Test extraction of specific pattern."""
        coords = extract_euro_coordinates(
            self.sample_euro_plans, 
            pattern_name="row_wise_even_rows"
        )
        
        self.assertEqual(len(coords), 4)
        self.assertEqual(coords[0].pattern_name, "row_wise_even_rows")
    
    def test_rotation_based_on_pattern(self):
        """Test rotation is set based on pattern type."""
        # Column-wise should be 90°
        col_coords = extract_euro_coordinates(
            self.sample_euro_plans, 
            pattern_name="column_wise_even_cols"
        )
        self.assertEqual(col_coords[0].rotation, 90.0)
        
        # Row-wise should be 0°
        row_coords = extract_euro_coordinates(
            self.sample_euro_plans,
            pattern_name="row_wise_even_rows"
        )
        self.assertEqual(row_coords[0].rotation, 0.0)
    
    def test_coordinates_sorted_by_index(self):
        """Test coordinates are returned sorted by index."""
        coords = extract_euro_coordinates(self.sample_euro_plans)
        
        indices = [c.index for c in coords]
        self.assertEqual(indices, [1, 2, 3, 4, 5, 6])
    
    def test_invalid_pattern_raises_error(self):
        """Test error when pattern doesn't exist."""
        with self.assertRaises(ValueError):
            extract_euro_coordinates(
                self.sample_euro_plans,
                pattern_name="invalid_pattern"
            )
    
    def test_no_pattern_returns_empty(self):
        """Test empty result when best_pattern is None."""
        no_pattern = {
            "best_pattern_name": "None",
            "all_options": {}
        }
        coords = extract_euro_coordinates(no_pattern)
        self.assertEqual(len(coords), 0)


class TestExtractAllClinicCoordinates(unittest.TestCase):
    """Test extract_all_clinic_coordinates function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.clinic_plans = {
            "total_clinics_required": 3,
            "ranked_layouts": [
                {
                    "Rank": 1,
                    "Placed": False,
                    "fixtures": ["ROC_clinic"],
                    "combo": ["H"],
                    "coordinates": [
                        {"name": "ROC_clinic", "target_center": [100, 200], "zone_id": "Zone_1"}
                    ]
                },
                {
                    "Rank": 2,
                    "Placed": True,
                    "fixtures": ["Clinic_with_sink"],
                    "combo": ["V"],
                    "coordinates": [
                        {"name": "Clinic_with_sink", "target_center": [300, 400], "zone_id": "Zone_2"}
                    ]
                },
                {
                    "Rank": 3,
                    "Placed": False,
                    "fixtures": ["Clinic_regular"],
                    "combo": ["H"],
                    "coordinates": [
                        {"name": "Clinic_regular", "target_center": [500, 600], "zone_id": "Zone_1"}
                    ]
                }
            ]
        }
    
    def test_extract_all_unplaced(self):
        """Test extracting only unplaced plans."""
        result = extract_all_clinic_coordinates(self.clinic_plans, only_unplaced=True)
        
        self.assertIn(1, result)
        self.assertNotIn(2, result)  # Placed=True
        self.assertIn(3, result)
    
    def test_extract_all_including_placed(self):
        """Test extracting all plans including placed."""
        result = extract_all_clinic_coordinates(self.clinic_plans, only_unplaced=False)
        
        self.assertIn(1, result)
        self.assertIn(2, result)
        self.assertIn(3, result)
    
    def test_max_rank_filter(self):
        """Test filtering by max rank."""
        result = extract_all_clinic_coordinates(
            self.clinic_plans, 
            only_unplaced=False,
            max_rank=2
        )
        
        self.assertIn(1, result)
        self.assertIn(2, result)
        self.assertNotIn(3, result)  # Rank > 2


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 COORDINATE EXTRACTION UNIT TESTS")
    print("=" * 60)
    
    # Run tests with verbosity
    unittest.main(verbosity=2)
