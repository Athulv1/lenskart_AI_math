#!/usr/bin/env python3
"""
Analyze the most recently generated JSON file to check if strategies have unique coordinates.
"""

import json
import os
import glob

# Find most recent JSON file
json_files = glob.glob('/home/athul/lenskart/*_floorplan_output/*_plans.json')
if not json_files:
    print("No JSON files found")
    exit(1)

# Get most recent by modification time
latest_json = max(json_files, key=os.path.getmtime)
print(f"Analyzing: {latest_json}")
print(f"Modified: {os.path.getmtime(latest_json)}")
print("=" * 80)

with open(latest_json, 'r') as f:
    data = json.load(f)

# Get first clinic
clinics = data.get('clinics', [])
if not clinics:
    print("No clinics found")
    exit(1)

clinic = clinics[0]
print(f"\nClinic Rank: {clinic.get('clinic_rank')}")
print(f"Clinic Placed: {clinic.get('placed')}")
print()

euros = clinic.get('corresponding_euros', [])

print("=" * 80)
print("EURO STRATEGIES ANALYSIS")
print("=" * 80)

for euro in euros:
    if not euro.get('success'):
        continue
    
    plan = euro.get('plan', {})
    strategy_num = plan.get('strategy_num')
    strategy_name = plan.get('strategy_name')
    pattern = plan.get('chosen_pattern_name')
    placed = euro.get('placed')
    placements = plan.get('placements', [])
    
    print(f"\nStrategy {strategy_num}: {strategy_name}")
    print(f"  Pattern: {pattern}")
    print(f"  Placed: {'✓' if placed else '✗'}")
    print(f"  Coordinates (first 3):")
    for i, p in enumerate(placements[:3], 1):
        coords = p['coordinates']
        print(f"    {i}. ({coords[0]:.2f}, {coords[1]:.2f})")

# Check for duplicates
print("\n" + "=" * 80)
print("COORDINATE UNIQUENESS CHECK")
print("=" * 80)

coord_data = {}
for euro in euros:
    if euro.get('success') and euro.get('plan'):
        plan = euro['plan']
        strategy_num = plan['strategy_num']
        coords = tuple(tuple(p['coordinates']) for p in plan['placements'])
        coord_data[strategy_num] = {
            'pattern': plan['chosen_pattern_name'],
            'coords': coords
        }

# Compare
all_unique = True
for i in range(1, 4):
    for j in range(i + 1, 5):
        if i in coord_data and j in coord_data:
            if coord_data[i]['coords'] == coord_data[j]['coords']:
                print(f"❌ Strategy {i} and {j} have IDENTICAL coordinates")
                print(f"   Both use pattern: {coord_data[i]['pattern']}, {coord_data[j]['pattern']}")
                all_unique = False

if all_unique:
    print("✅ ALL STRATEGIES HAVE UNIQUE COORDINATES")
    for num, info in sorted(coord_data.items()):
        print(f"  Strategy {num} → {info['pattern']}")
else:
    print("\n❌ PROBLEM: Some strategies still have identical coordinates")
    print("This means the code changes haven't taken effect yet.")
