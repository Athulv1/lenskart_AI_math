#!/usr/bin/env python3
"""
Test script to verify that _generate_euro_plan() selects different patterns
for each strategy when given the same euro_placement_blueprint.
"""

import sys
sys.path.insert(0, '/home/athul/lenskart/app')

from plan_extractors import _generate_euro_plan

# Mock blueprint data with all 4 patterns
mock_blueprint = {
    "best_pattern_name": "column_wise_even_cols",
    "all_options": {
        "column_wise_even_cols": {
            "count": 8,
            "rank": 1,
            "placed": False,
            "placements": {
                "count_1": {"coordinates": (100, 200)},
                "count_2": {"coordinates": (300, 200)},
                "count_3": {"coordinates": (500, 200)},
            }
        },
        "column_wise_odd_cols": {
            "count": 7,
            "rank": 2,
            "placed": False,
            "placements": {
                "count_1": {"coordinates": (200, 200)},
                "count_2": {"coordinates": (400, 200)},
                "count_3": {"coordinates": (600, 200)},
            }
        },
        "row_wise_even_rows": {
            "count": 6,
            "rank": 3,
            "placed": False,
            "placements": {
                "count_1": {"coordinates": (100, 100)},
                "count_2": {"coordinates": (100, 300)},
                "count_3": {"coordinates": (100, 500)},
            }
        },
        "row_wise_odd_rows": {
            "count": 5,
            "rank": 4,
            "placed": False,
            "placements": {
                "count_1": {"coordinates": (200, 100)},
                "count_2": {"coordinates": (200, 300)},
                "count_3": {"coordinates": (200, 500)},
            }
        }
    }
}

print("=" * 80)
print("TESTING _generate_euro_plan() WITH ALL 4 STRATEGIES")
print("=" * 80)
print()

all_coordinates = {}

for strategy_num in [1, 2, 3, 4]:
    try:
        plan = _generate_euro_plan(mock_blueprint, strategy_num, required_count=3)
        
        pattern = plan['chosen_pattern_name']
        coords = [tuple(p['coordinates']) for p in plan['placements']]
        
        all_coordinates[strategy_num] = {
            'pattern': pattern,
            'coordinates': coords
        }
        
        print(f"Strategy {strategy_num}: {plan['strategy_name']}")
        print(f"  Chosen Pattern: {pattern}")
        print(f"  Coordinates: {coords}")
        print()
        
    except Exception as e:
        print(f"❌ Strategy {strategy_num} FAILED: {e}")
        import traceback
        traceback.print_exc()
        print()

print("=" * 80)
print("VERIFICATION: Checking if patterns are unique")
print("=" * 80)

patterns_used = [data['pattern'] for data in all_coordinates.values()]
if len(patterns_used) == len(set(patterns_used)):
    print("✅ ALL STRATEGIES USE DIFFERENT PATTERNS")
    for strat, data in all_coordinates.items():
        print(f"  Strategy {strat} → {data['pattern']}")
else:
    print("❌ SOME STRATEGIES USE THE SAME PATTERN")
    for strat, data in all_coordinates.items():
        print(f"  Strategy {strat} → {data['pattern']}")

print()
print("=" * 80)
print("VERIFICATION: Checking if coordinates are unique")
print("=" * 80)

coord_sets = {s: frozenset(d['coordinates']) for s, d in all_coordinates.items()}
unique_coords = len(set(coord_sets.values())) == len(coord_sets)

if unique_coords:
    print("✅ ALL STRATEGIES HAVE DIFFERENT COORDINATES")
else:
    print("❌ SOME STRATEGIES HAVE IDENTICAL COORDINATES")
    
    # Find duplicates
    for i in [1, 2, 3]:
        for j in range(i + 1, 5):
            if coord_sets[i] == coord_sets[j]:
                print(f"  Strategies {i} and {j} have identical coordinates!")
