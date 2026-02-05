#!/usr/bin/env python3
"""
Unit Tests for Euro Plan Generator Helper

Tests the _generate_euro_plan() function with various scenarios including:
- Valid strategy selection (1-4)
- Invalid strategy handling
- Pattern preference based on strategy
- Capacity and overflow calculations
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plan_extractors import (
    _generate_euro_plan,
    get_euro_strategy_info,
    list_euro_strategies,
    EURO_STRATEGIES
)


class TestEuroStrategiesConstant(unittest.TestCase):
    """Test EURO_STRATEGIES constant configuration."""
    
    def test_has_four_strategies(self):
        """Test that all 4 strategies are defined."""
        self.assertEqual(len(EURO_STRATEGIES), 4)
        self.assertIn(1, EURO_STRATEGIES)
        self.assertIn(2, EURO_STRATEGIES)
        self.assertIn(3, EURO_STRATEGIES)
        self.assertIn(4, EURO_STRATEGIES)
    
    def test_strategy_has_required_fields(self):
        """Test each strategy has required fields."""
        required_fields = ["name", "rotation", "description", "method", "preferred_patterns", "parameters"]
        for num, strategy in EURO_STRATEGIES.items():
            for field in required_fields:
                self.assertIn(field, strategy, f"Strategy {num} missing field: {field}")
    
    def test_rotated_strategies_have_90_degrees(self):
        """Test strategies 1-3 have 90° rotation."""
        for num in [1, 2, 3]:
            self.assertEqual(EURO_STRATEGIES[num]["rotation"], 90.0)
    
    def test_non_rotated_strategy_has_0_degrees(self):
        """Test strategy 4 has 0° rotation."""
        self.assertEqual(EURO_STRATEGIES[4]["rotation"], 0.0)
    
    def test_preferred_patterns(self):
        """Test preferred patterns based on rotation."""
        # 90° strategies prefer column_wise
        for num in [1, 2, 3]:
            self.assertTrue(
                any("column_wise" in p for p in EURO_STRATEGIES[num]["preferred_patterns"])
            )
        # 0° strategy prefers row_wise
        self.assertTrue(
            any("row_wise" in p for p in EURO_STRATEGIES[4]["preferred_patterns"])
        )


class TestGetEuroStrategyInfo(unittest.TestCase):
    """Test get_euro_strategy_info() helper."""
    
    def test_valid_strategy(self):
        """Test getting valid strategy info."""
        info = get_euro_strategy_info(1)
        self.assertEqual(info["name"], "basic_qms")
        self.assertEqual(info["rotation"], 90.0)
    
    def test_invalid_strategy_raises(self):
        """Test invalid strategy raises error."""
        with self.assertRaises(ValueError):
            get_euro_strategy_info(5)
        with self.assertRaises(ValueError):
            get_euro_strategy_info(0)


class TestListEuroStrategies(unittest.TestCase):
    """Test list_euro_strategies() helper."""
    
    def test_returns_list(self):
        """Test returns list of all strategies."""
        strategies = list_euro_strategies()
        self.assertEqual(len(strategies), 4)
    
    def test_includes_num_field(self):
        """Test each entry has num field."""
        strategies = list_euro_strategies()
        for s in strategies:
            self.assertIn("num", s)
            self.assertIn("name", s)


class TestGenerateEuroPlan(unittest.TestCase):
    """Test _generate_euro_plan() function."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample euro_plans_data matching analyze_placement_patterns() output
        self.sample_euro_data = {
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
                "row_wise_odd_rows": {
                    "count": 3,
                    "rank": 4,
                    "placed": False,
                    "placements": {
                        "count_1": {"coordinates": [1000.0, 2750.0]},
                        "count_2": {"coordinates": [2000.0, 2750.0]},
                        "count_3": {"coordinates": [1000.0, 4250.0]}
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
                },
                "column_wise_odd_cols": {
                    "count": 5,
                    "rank": 3,
                    "placed": False,
                    "placements": {
                        "count_1": {"coordinates": [2000.0, 2000.0]},
                        "count_2": {"coordinates": [2000.0, 3000.0]},
                        "count_3": {"coordinates": [2000.0, 4000.0]},
                        "count_4": {"coordinates": [2000.0, 5000.0]},
                        "count_5": {"coordinates": [2000.0, 6000.0]}
                    }
                }
            }
        }
    
    def test_valid_strategy_1(self):
        """Test generating plan for strategy 1 (basic_qms)."""
        plan = _generate_euro_plan(self.sample_euro_data, strategy_num=1)
        
        self.assertEqual(plan["strategy_num"], 1)
        self.assertEqual(plan["strategy_name"], "basic_qms")
        self.assertEqual(plan["rotation"], 90.0)
        # Should select column_wise pattern (preferred for 90° rotation)
        self.assertIn("column_wise", plan["chosen_pattern_name"])
    
    def test_valid_strategy_4(self):
        """Test generating plan for strategy 4 (v2_og_non_rotated)."""
        plan = _generate_euro_plan(self.sample_euro_data, strategy_num=4)
        
        self.assertEqual(plan["strategy_num"], 4)
        self.assertEqual(plan["strategy_name"], "v2_og_non_rotated")
        self.assertEqual(plan["rotation"], 0.0)
        # Should select row_wise pattern (preferred for 0° rotation)
        self.assertIn("row_wise", plan["chosen_pattern_name"])
    
    def test_invalid_strategy_raises(self):
        """Test invalid strategy number raises error."""
        with self.assertRaises(ValueError) as ctx:
            _generate_euro_plan(self.sample_euro_data, strategy_num=5)
        self.assertIn("Invalid strategy_num", str(ctx.exception))
    
    def test_output_format(self):
        """Test output format has required fields."""
        plan = _generate_euro_plan(self.sample_euro_data, strategy_num=1)
        
        required_fields = [
            "strategy_num", "strategy_name", "rotation", "chosen_pattern_name",
            "max_capacity", "placed_count", "overflow", "placements"
        ]
        for field in required_fields:
            self.assertIn(field, plan, f"Missing field: {field}")
    
    def test_placements_format(self):
        """Test placements list format."""
        plan = _generate_euro_plan(self.sample_euro_data, strategy_num=1)
        
        self.assertIsInstance(plan["placements"], list)
        self.assertGreater(len(plan["placements"]), 0)
        
        first = plan["placements"][0]
        self.assertIn("index", first)
        self.assertIn("coordinates", first)
        self.assertIsInstance(first["coordinates"], tuple)
        self.assertEqual(len(first["coordinates"]), 2)
    
    def test_max_capacity_extracted(self):
        """Test max_capacity matches pattern count."""
        plan = _generate_euro_plan(self.sample_euro_data, strategy_num=1)
        
        # column_wise_even_cols has 6 fixtures
        self.assertEqual(plan["max_capacity"], 6)
        self.assertEqual(plan["placed_count"], 6)
        self.assertEqual(plan["overflow"], 0)
    
    def test_required_count_limits_placements(self):
        """Test required_count limits placed fixtures."""
        plan = _generate_euro_plan(
            self.sample_euro_data, 
            strategy_num=1,
            required_count=3
        )
        
        self.assertEqual(plan["placed_count"], 3)
        self.assertEqual(len(plan["placements"]), 3)
        self.assertEqual(plan["overflow"], 0)
    
    def test_overflow_calculated(self):
        """Test overflow calculated when required > capacity."""
        plan = _generate_euro_plan(
            self.sample_euro_data,
            strategy_num=1,
            required_count=10
        )
        
        # column_wise_even_cols has 6 max
        self.assertEqual(plan["max_capacity"], 6)
        self.assertEqual(plan["placed_count"], 6)
        self.assertEqual(plan["overflow"], 4)  # 10 - 6 = 4
    
    def test_empty_options_raises(self):
        """Test empty all_options raises error."""
        empty_data = {"best_pattern_name": "None", "all_options": {}}
        
        with self.assertRaises(ValueError) as ctx:
            _generate_euro_plan(empty_data, strategy_num=1)
        self.assertIn("No placement patterns", str(ctx.exception))


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 EURO PLAN GENERATOR UNIT TESTS")
    print("=" * 60)
    
    # Run tests with verbosity
    unittest.main(verbosity=2)
