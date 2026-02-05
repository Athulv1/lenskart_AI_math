#!/usr/bin/env python3
"""
Test save_all_plans_to_json() and generate_combined_plans() functions.

Tests the complete plan generation workflow including:
- Generating 4 Euro variations per clinic plan
- JSON file saving
- Error handling
- Combined plan generation
"""

import unittest
import sys
import os
import json
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plan_extractors import (
    save_all_plans_to_json,
    generate_combined_plans,
    EURO_STRATEGIES
)


class TestSaveAllPlansToJson(unittest.TestCase):
    """Test save_all_plans_to_json() function."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample clinic plans
        self.clinic_plans = {
            "total_clinics_required": 2,
            "ranked_layouts": [
                {
                    "Rank": 1,
                    "Placed": False,
                    "score": 1800.0,
                    "fixtures": ["ROC_clinic"],
                    "combo": ["H"],
                    "coordinates": [
                        {"name": "ROC_clinic", "target_center": [1000, 2000], "zone_id": "Zone_1"}
                    ]
                },
                {
                    "Rank": 2,
                    "Placed": False,
                    "score": 2100.0,
                    "fixtures": ["Clinic_regular"],
                    "combo": ["V"],
                    "coordinates": [
                        {"name": "Clinic_regular", "target_center": [3000, 4000], "zone_id": "Zone_2"}
                    ]
                }
            ]
        }
        
        # Sample euro plans (from analyze_placement_patterns output)
        self.euro_plans = {
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
        
        # Create temp directory for output files
        self.temp_dir = tempfile.mkdtemp()
        self.output_path = os.path.join(self.temp_dir, "output", "plans.json")
    
    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generates_all_four_strategies(self):
        """Test that all 4 euro strategies are generated."""
        result = save_all_plans_to_json(
            self.clinic_plans,
            self.euro_plans,
            self.output_path
        )
        
        self.assertIn("euro_plans_by_strategy", result)
        strategies = result["euro_plans_by_strategy"]
        
        self.assertIn("strategy_1", strategies)
        self.assertIn("strategy_2", strategies)
        self.assertIn("strategy_3", strategies)
        self.assertIn("strategy_4", strategies)
    
    def test_includes_clinic_plans(self):
        """Test that clinic plans are included in output."""
        result = save_all_plans_to_json(
            self.clinic_plans,
            self.euro_plans,
            self.output_path
        )
        
        self.assertIn("clinic_plans", result)
        self.assertEqual(
            result["clinic_plans"]["total_clinics_required"],
            2
        )
    
    def test_adds_summary(self):
        """Test that summary statistics are added."""
        result = save_all_plans_to_json(
            self.clinic_plans,
            self.euro_plans,
            self.output_path
        )
        
        self.assertIn("summary", result)
        self.assertEqual(result["summary"]["total_clinic_layouts"], 2)
        self.assertGreater(result["summary"]["euro_strategies_generated"], 0)
    
    def test_saves_to_file(self):
        """Test that output is saved to JSON file."""
        result = save_all_plans_to_json(
            self.clinic_plans,
            self.euro_plans,
            self.output_path
        )
        
        self.assertTrue(os.path.exists(self.output_path))
        
        with open(self.output_path, 'r') as f:
            loaded = json.load(f)
        
        self.assertIn("floorplan_id", loaded)
        self.assertIn("timestamp", loaded)
    
    def test_generates_floorplan_id(self):
        """Test that floorplan_id is auto-generated if not provided."""
        result = save_all_plans_to_json(
            self.clinic_plans,
            self.euro_plans,
            self.output_path
        )
        
        self.assertIn("floorplan_id", result)
        self.assertTrue(len(result["floorplan_id"]) > 0)
    
    def test_uses_provided_floorplan_id(self):
        """Test that provided floorplan_id is used."""
        result = save_all_plans_to_json(
            self.clinic_plans,
            self.euro_plans,
            self.output_path,
            floorplan_id="custom-123"
        )
        
        self.assertEqual(result["floorplan_id"], "custom-123")
    
    def test_includes_metadata(self):
        """Test that metadata is included."""
        result = save_all_plans_to_json(
            self.clinic_plans,
            self.euro_plans,
            self.output_path,
            metadata={"proto_value": "16L", "area": 1500}
        )
        
        self.assertEqual(result["metadata"]["proto_value"], "16L")
        self.assertEqual(result["metadata"]["area"], 1500)
    
    def test_strategy_success_flag(self):
        """Test that each strategy has success flag."""
        result = save_all_plans_to_json(
            self.clinic_plans,
            self.euro_plans,
            self.output_path
        )
        
        for strategy_key in result["euro_plans_by_strategy"]:
            self.assertIn("success", result["euro_plans_by_strategy"][strategy_key])


class TestGenerateCombinedPlans(unittest.TestCase):
    """Test generate_combined_plans() function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.clinic_plans = {
            "ranked_layouts": [
                {"Rank": 1, "Placed": False, "fixtures": ["ROC_clinic"]},
                {"Rank": 2, "Placed": False, "fixtures": ["Clinic_regular"]}
            ]
        }
        
        self.euro_plans = {
            "required_count": 4,
            "all_options": {
                "row_wise_even_rows": {
                    "count": 4,
                    "rank": 1,
                    "placed": False,
                    "placements": {
                        "count_1": {"coordinates": [1000, 2000]},
                        "count_2": {"coordinates": [2000, 2000]},
                        "count_3": {"coordinates": [1000, 3000]},
                        "count_4": {"coordinates": [2000, 3000]}
                    }
                },
                "column_wise_even_cols": {
                    "count": 4,
                    "rank": 2,
                    "placed": False,
                    "placements": {
                        "count_1": {"coordinates": [1000, 2000]},
                        "count_2": {"coordinates": [1000, 3000]},
                        "count_3": {"coordinates": [3000, 2000]},
                        "count_4": {"coordinates": [3000, 3000]}
                    }
                }
            }
        }
    
    def test_generates_all_combinations(self):
        """Test that all clinic × euro combinations are generated."""
        combinations = generate_combined_plans(
            self.clinic_plans,
            self.euro_plans
        )
        
        # 2 clinic plans × 4 euro strategies = 8 combinations
        self.assertEqual(len(combinations), 8)
    
    def test_combination_structure(self):
        """Test structure of each combination."""
        combinations = generate_combined_plans(
            self.clinic_plans,
            self.euro_plans
        )
        
        for combo in combinations:
            self.assertIn("clinic_rank", combo)
            self.assertIn("clinic_layout", combo)
            self.assertIn("euro_strategy_num", combo)
            self.assertIn("euro_strategy_name", combo)
            self.assertIn("combined_id", combo)
    
    def test_combined_id_format(self):
        """Test combined_id follows expected format."""
        combinations = generate_combined_plans(
            self.clinic_plans,
            self.euro_plans
        )
        
        # Check first combination
        self.assertEqual(combinations[0]["combined_id"], "clinic_1_euro_1")
    
    def test_all_strategies_covered(self):
        """Test that all 4 strategies are used for each clinic."""
        combinations = generate_combined_plans(
            self.clinic_plans,
            self.euro_plans
        )
        
        # Check clinic rank 1 has all 4 strategies
        clinic_1_strategies = [
            c["euro_strategy_num"] 
            for c in combinations 
            if c["clinic_rank"] == 1
        ]
        self.assertEqual(set(clinic_1_strategies), {1, 2, 3, 4})


class TestWithRealSampleData(unittest.TestCase):
    """Test with real sample data file."""
    
    def setUp(self):
        """Load sample data."""
        self.temp_dir = tempfile.mkdtemp()
        sample_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "..", "schemas", "test_sample_plan.json"
        )
        
        if os.path.exists(sample_path):
            with open(sample_path, 'r') as f:
                self.sample_data = json.load(f)
        else:
            self.sample_data = None
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_with_sample_data(self):
        """Test with real sample data."""
        if self.sample_data is None:
            self.skipTest("Sample data not found")
        
        output_path = os.path.join(self.temp_dir, "sample_output.json")
        
        result = save_all_plans_to_json(
            clinic_plans=self.sample_data["clinic_plans"],
            euro_plans=self.sample_data["euro_plans"],
            output_path=output_path
        )
        
        # Should generate all 4 strategies successfully
        successful = sum(
            1 for v in result["euro_plans_by_strategy"].values()
            if v.get("success", False)
        )
        self.assertEqual(successful, 4)
        
        # File should exist
        self.assertTrue(os.path.exists(output_path))


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 SAVE ALL PLANS TO JSON TESTS")
    print("=" * 60)
    
    unittest.main(verbosity=2)
