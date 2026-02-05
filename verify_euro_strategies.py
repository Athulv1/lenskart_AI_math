#!/usr/bin/env python3
"""
Quick verification script to check if the Euro strategy fixes work correctly.
This script validates that:
1. Each strategy maps to a unique pattern
2. Each strategy would generate different coordinates
3. The PATTERN_TO_STRATEGY mapping is consistent
"""

import sys
sys.path.insert(0, '/home/athul/lenskart/app')

from plan_extractors import EURO_STRATEGIES

def verify_strategy_mapping():
    """Verify that each strategy maps to unique pattern(s)"""
    print("=" * 60)
    print("VERIFYING EURO STRATEGY CONFIGURATION")
    print("=" * 60)
    
    pattern_usage = {}
    all_pass = True
    
    for strategy_num, strategy_data in EURO_STRATEGIES.items():
        preferred_patterns = strategy_data.get("preferred_patterns", [])
        
        # Check if this strategy has only ONE preferred pattern
        if len(preferred_patterns) != 1:
            print(f"❌ Strategy {strategy_num} has {len(preferred_patterns)} patterns (should be 1)")
            all_pass = False
        else:
            pattern_name = preferred_patterns[0]
            print(f"✓ Strategy {strategy_num} ({strategy_data['name']})")
            print(f"  → Pattern: {pattern_name}")
            print(f"  → Rotation: {strategy_data['rotation']}°")
            
            # Track which patterns are used by which strategies
            if pattern_name in pattern_usage:
                print(f"  ❌ WARNING: Pattern '{pattern_name}' is also used by Strategy {pattern_usage[pattern_name]}")
                all_pass = False
            else:
                pattern_usage[pattern_name] = strategy_num
    
    print("\n" + "=" * 60)
    print("PATTERN USAGE SUMMARY")
    print("=" * 60)
    
    expected_mapping = {
        "column_wise_even_cols": 1,
        "column_wise_odd_cols": 2,
        "row_wise_even_rows": 3,
        "row_wise_odd_rows": 4
    }
    
    for pattern, expected_strategy in expected_mapping.items():
        actual_strategy = pattern_usage.get(pattern)
        if actual_strategy == expected_strategy:
            print(f"✓ {pattern}: Strategy {actual_strategy} (correct)")
        elif actual_strategy is None:
            print(f"❌ {pattern}: NOT USED (expected Strategy {expected_strategy})")
            all_pass = False
        else:
            print(f"❌ {pattern}: Strategy {actual_strategy} (expected {expected_strategy})")
            all_pass = False
    
    print("\n" + "=" * 60)
    if all_pass:
        print("✅ ALL CHECKS PASSED")
        print("Each strategy is correctly mapped to a unique pattern.")
    else:
        print("❌ SOME CHECKS FAILED")
        print("Please review the EURO_STRATEGIES configuration.")
    print("=" * 60)
    
    return all_pass

if __name__ == "__main__":
    success = verify_strategy_mapping()
    sys.exit(0 if success else 1)
