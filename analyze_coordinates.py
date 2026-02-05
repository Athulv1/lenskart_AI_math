#!/usr/bin/env python3
"""
Script to analyze the actual coordinates in the generated JSON
to verify if they are truly identical or different.
"""

import json
import sys

json_path = "/home/athul/lenskart/d32f8f4e-8fd9-489a-933c-5cee8b257adc_floorplan_output/output_0_plans.json"

try:
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    print("=" * 80)
    print("ANALYZING EURO STRATEGY COORDINATES")
    print("=" * 80)
    
    # Get the first placed clinic
    clinics = data.get('clinics', [])
    if not clinics:
        print("No clinics found in JSON")
        sys.exit(1)
    
    # Find first placed clinic
    placed_clinic = None
    for clinic in clinics:
        if clinic.get('placed'):
            placed_clinic = clinic
            break
    
    if not placed_clinic:
        print("No placed clinic found")
        sys.exit(1)
    
    print(f"Analyzing Clinic Rank: {placed_clinic.get('clinic_rank')}")
    print()
    
    euros = placed_clinic.get('corresponding_euros', [])
    
    # Collect all coordinates
    all_coords = {}
    
    for euro in euros:
        if not euro.get('success'):
            continue
        
        plan = euro.get('plan', {})
        strategy_num = plan.get('strategy_num')
        strategy_name = plan.get('strategy_name')
        pattern = plan.get('chosen_pattern_name')
        placements = plan.get('placements', [])
        
        coords_list = [tuple(p['coordinates']) for p in placements]
        all_coords[strategy_num] = {
            'name': strategy_name,
            'pattern': pattern,
            'coordinates': coords_list
        }
        
        print(f"Strategy {strategy_num}: {strategy_name}")
        print(f"  Pattern: {pattern}")
        print(f"  Placed: {euro.get('placed')}")
        print(f"  First 3 coordinates:")
        for i, coords in enumerate(coords_list[:3], 1):
            print(f"    {i}. ({coords[0]:.2f}, {coords[1]:.2f})")
        print()
    
    # Check if all coordinates are identical
    print("=" * 80)
    print("COORDINATE COMPARISON")
    print("=" * 80)
    
    coord_sets = {}
    for strat_num, data in all_coords.items():
        coord_set = frozenset(data['coordinates'])
        coord_sets[strat_num] = coord_set
    
    # Compare strategies pairwise
    strategies = sorted(all_coords.keys())
    identical_found = False
    
    for i in range(len(strategies)):
        for j in range(i + 1, len(strategies)):
            strat_1 = strategies[i]
            strat_2 = strategies[j]
            
            if coord_sets[strat_1] == coord_sets[strat_2]:
                print(f"❌ Strategy {strat_1} and Strategy {strat_2} have IDENTICAL coordinates")
                print(f"   Pattern 1: {all_coords[strat_1]['pattern']}")
                print(f"   Pattern 2: {all_coords[strat_2]['pattern']}")
                identical_found = True
            else:
                print(f"✓ Strategy {strat_1} and Strategy {strat_2} have DIFFERENT coordinates")
    
    print()
    if identical_found:
        print("❌ PROBLEM CONFIRMED: Some strategies have identical coordinates")
    else:
        print("✅ ALL STRATEGIES HAVE UNIQUE COORDINATES")
    
except FileNotFoundError:
    print(f"❌ JSON file not found: {json_path}")
    print("Please process a floorplan first to generate the JSON")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
