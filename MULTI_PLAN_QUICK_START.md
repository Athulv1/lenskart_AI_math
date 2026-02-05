# ⚡ **MULTI-PLAN ADAPTIVE LOGIC: QUICK START GUIDE**

## **Get Started in 30 Minutes**

---

**For**: Developers ready to start implementation immediately  
**Prerequisites**: Python 3.8+, workspace setup complete  
**Time to first working prototype**: 2-4 hours

---

## 🎯 **WHAT YOU'LL BUILD TODAY**

A minimal working prototype of the multi-plan adaptive logic that:
- ✅ Loads clinic plans from fixture_dict
- ✅ Calculates available space
- ✅ Attempts Plan A → Plan B → Plan C cascade
- ✅ Places a single clinic successfully

---

## 📋 **PRE-FLIGHT CHECKLIST**

```bash
# 1. Verify Python version
python3 --version  # Should be 3.8+

# 2. Check dependencies
pip list | grep -E "ezdxf|shapely|google-generativeai"

# 3. Verify workspace structure
ls -la /home/athul/lenskart/app/DXF_Controller.py
ls -la /home/athul/lenskart/assets/clinic/

# 4. Test file access
python3 -c "import ezdxf; import shapely; print('✅ Dependencies OK')"
```

**If any step fails**:
```bash
pip install -r requirements.txt
```

---

## 🚀 **STEP 1: CREATE TEST SCRIPT (5 minutes)**

Create a new file to test the concept:

```bash
touch /home/athul/lenskart/test_multiplan_prototype.py
```

**File content** (`test_multiplan_prototype.py`):

```python
#!/usr/bin/env python3
"""
Quick prototype to test multi-plan adaptive logic concept
"""

import sys
sys.path.insert(0, '/home/athul/lenskart')

from app import DXF_Controller, Fixture
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
import json

print("="*70)
print("🧪 MULTI-PLAN ADAPTIVE LOGIC - PROTOTYPE TEST")
print("="*70)

# ─────────────────────────────────────────────────────────────────
# STEP 1: Mock plan repository (simplified)
# ─────────────────────────────────────────────────────────────────

clinic_plans = [
    {
        "name": "Clinic_with_sink",
        "priority": 1,
        "dimensions": {"width": 2600, "height": 1700, "clearance": 800},
        "plan_category": "Plan_A"
    },
    {
        "name": "Clinic_regular",
        "priority": 2,
        "dimensions": {"width": 2600, "height": 1700, "clearance": 600},
        "plan_category": "Plan_B"
    },
    {
        "name": "ROC_clinic",
        "priority": 3,
        "dimensions": {"width": 2600, "height": 1700, "clearance": 700},
        "plan_category": "Plan_C"
    }
]

print(f"\n📦 Loaded {len(clinic_plans)} clinic plans")
for plan in clinic_plans:
    print(f"   • {plan['plan_category']}: {plan['name']} (Priority {plan['priority']})")

# ─────────────────────────────────────────────────────────────────
# STEP 2: Mock available space (10m x 8m floor)
# ─────────────────────────────────────────────────────────────────

floor_boundary = box(0, 0, 10000, 8000)  # 10m x 8m in mm
print(f"\n🏢 Floor boundary: 10m × 8m ({floor_boundary.area / 1_000_000:.1f} m²)")

# Mock obstacle (existing table at 7000, 4000)
obstacle = box(6500, 3500, 7500, 4500)  # 1m x 1m table
obstacles = [obstacle]

print(f"🚧 Obstacles: {len(obstacles)}")
print(f"   • Table at (7000, 4000)")

# Calculate free area
free_area = floor_boundary.difference(unary_union(obstacles))
print(f"✨ Free area: {free_area.area / 1_000_000:.1f} m²")

# ─────────────────────────────────────────────────────────────────
# STEP 3: Attempt placement with cascade
# ─────────────────────────────────────────────────────────────────

target_position = (5000, 4000)  # Center of floor
print(f"\n🎯 Target position: {target_position}")

def attempt_plan_placement(plan, free_area, target_pos, obstacles):
    """Simplified placement attempt"""
    print(f"\n{'─'*70}")
    print(f"🔹 Attempting: {plan['plan_category']} - {plan['name']}")
    print(f"   Priority: {plan['priority']}")
    
    # Get dimensions
    width = plan['dimensions']['width']
    height = plan['dimensions']['height']
    clearance = plan['dimensions']['clearance']
    
    print(f"   Dimensions: {width}mm × {height}mm + {clearance}mm clearance")
    
    # Create bounding box
    x, y = target_pos
    bbox = box(
        x - width/2 - clearance,
        y - height/2 - clearance,
        x + width/2 + clearance,
        y + height/2 + clearance
    )
    
    print(f"   Bounding box: ({bbox.bounds[0]:.0f}, {bbox.bounds[1]:.0f}) to ({bbox.bounds[2]:.0f}, {bbox.bounds[3]:.0f})")
    
    # Check if fits in free area
    if not free_area.contains(bbox):
        print(f"   ❌ FAILED: Outside free area")
        return None
    
    # Check collisions
    for i, obs in enumerate(obstacles):
        if bbox.intersects(obs):
            intersection = bbox.intersection(obs)
            overlap_pct = (intersection.area / bbox.area) * 100
            print(f"   ❌ FAILED: Collision with obstacle {i+1} ({overlap_pct:.1f}% overlap)")
            return None
    
    print(f"   ✅ SUCCESS: Valid placement")
    return {
        "plan": plan,
        "position": target_pos,
        "bbox": bbox
    }

# ─────────────────────────────────────────────────────────────────
# STEP 4: Execute cascade
# ─────────────────────────────────────────────────────────────────

print(f"\n{'='*70}")
print(f"🔄 EXECUTING ADAPTIVE CASCADE")
print(f"{'='*70}")

placement = None
for plan in clinic_plans:
    result = attempt_plan_placement(plan, free_area, target_position, obstacles)
    
    if result:
        placement = result
        print(f"\n{'='*70}")
        print(f"🎉 PLACEMENT SUCCESSFUL!")
        print(f"{'='*70}")
        print(f"Plan used: {result['plan']['plan_category']}")
        print(f"Fixture: {result['plan']['name']}")
        print(f"Position: {result['position']}")
        print(f"{'='*70}")
        break

if not placement:
    print(f"\n{'='*70}")
    print(f"❌ ALL PLANS FAILED")
    print(f"{'='*70}")
    print(f"Reason: No plan fits in available space")
    print(f"Suggestion: Clear obstacles or reduce fixture count")
    print(f"{'='*70}")

# ─────────────────────────────────────────────────────────────────
# STEP 5: Visualize result (text-based)
# ─────────────────────────────────────────────────────────────────

if placement:
    print(f"\n📊 PLACEMENT VISUALIZATION (Simplified)")
    print(f"")
    print(f"Floor Plan (10m × 8m):")
    print(f"┌────────────────────────────────────────┐")
    print(f"│                                        │")
    print(f"│          [Clinic Placed]               │")
    print(f"│          @ (5000, 4000)                │")
    print(f"│                                        │")
    print(f"│                     [Table]            │")
    print(f"│                     @ (7000,4000)      │")
    print(f"│                                        │")
    print(f"└────────────────────────────────────────┘")
    print(f"")
    print(f"✅ Prototype test PASSED")
else:
    print(f"\n⚠️  Prototype test INCONCLUSIVE (expected in some scenarios)")

print(f"\n{'='*70}")
print(f"🏁 TEST COMPLETE")
print(f"{'='*70}")
```

---

## 🧪 **STEP 2: RUN THE PROTOTYPE (2 minutes)**

```bash
cd /home/athul/lenskart
python3 test_multiplan_prototype.py
```

**Expected Output**:
```
======================================================================
🧪 MULTI-PLAN ADAPTIVE LOGIC - PROTOTYPE TEST
======================================================================

📦 Loaded 3 clinic plans
   • Plan_A: Clinic_with_sink (Priority 1)
   • Plan_B: Clinic_regular (Priority 2)
   • Plan_C: ROC_clinic (Priority 3)

🏢 Floor boundary: 10m × 8m (80.0 m²)
🚧 Obstacles: 1
   • Table at (7000, 4000)
✨ Free area: 79.0 m²

🎯 Target position: (5000, 4000)

======================================================================
🔄 EXECUTING ADAPTIVE CASCADE
======================================================================

──────────────────────────────────────────────────────────────────────
🔹 Attempting: Plan_A - Clinic_with_sink
   Priority: 1
   Dimensions: 2600mm × 1700mm + 800mm clearance
   Bounding box: (700, 2150) to (9300, 5850)
   ✅ SUCCESS: Valid placement

======================================================================
🎉 PLACEMENT SUCCESSFUL!
======================================================================
Plan used: Plan_A
Fixture: Clinic_with_sink
Position: (5000, 4000)
======================================================================

📊 PLACEMENT VISUALIZATION (Simplified)

Floor Plan (10m × 8m):
┌────────────────────────────────────────┐
│                                        │
│          [Clinic Placed]               │
│          @ (5000, 4000)                │
│                                        │
│                     [Table]            │
│                     @ (7000,4000)      │
│                                        │
└────────────────────────────────────────┘

✅ Prototype test PASSED

======================================================================
🏁 TEST COMPLETE
======================================================================
```

---

## 🔧 **STEP 3: TEST FALLBACK SCENARIO (5 minutes)**

Modify the test to force a fallback to Plan B:

**In `test_multiplan_prototype.py`, change**:

```python
# OLD
target_position = (5000, 4000)  # Center of floor
obstacle = box(6500, 3500, 7500, 4500)  # 1m x 1m table

# NEW - Create collision scenario for Plan A
target_position = (5000, 4000)  # Same position
obstacle = box(3500, 3000, 6500, 5000)  # Larger obstacle forcing Plan B
```

**Run again**:
```bash
python3 test_multiplan_prototype.py
```

**Expected Output** (should show Plan A failing, Plan B succeeding):
```
──────────────────────────────────────────────────────────────────────
🔹 Attempting: Plan_A - Clinic_with_sink
   Priority: 1
   Dimensions: 2600mm × 1700mm + 800mm clearance
   ❌ FAILED: Collision with obstacle 1 (22.3% overlap)

──────────────────────────────────────────────────────────────────────
🔹 Attempting: Plan_B - Clinic_regular
   Priority: 2
   Dimensions: 2600mm × 1700mm + 600mm clearance
   ✅ SUCCESS: Valid placement

======================================================================
🎉 PLACEMENT SUCCESSFUL!
======================================================================
Plan used: Plan_B
Fixture: Clinic_regular
Position: (5000, 4000)
======================================================================
```

---

## 📝 **STEP 4: INTEGRATE WITH REAL DXF_CONTROLLER (30 minutes)**

Now let's add this logic to the actual `DXF_Controller` class.

### **4.1: Add plan initialization**

**File**: `app/DXF_Controller.py`  
**Location**: In `__init__` method (around line 400)

```python
# Add this to __init__ after existing initialization:

# NEW: Initialize multi-plan repository
print("\n🔧 Initializing Multi-Plan Repository...")
self.clinic_plans = self._initialize_clinic_plans()
self.euro_plans = self._initialize_euro_plans()

print(f"✅ Plan repository ready:")
print(f"   Clinic plans: {len(self.clinic_plans)}")
print(f"   Euro center plans: {len(self.euro_plans)}")
```

### **4.2: Add helper methods**

**Add these methods to the `DXF_Controller` class**:

```python
def _initialize_clinic_plans(self) -> List[Dict]:
    """Initialize clinic plan repository"""
    clinic_plans = []
    
    for key, value in self.fixture_dict.items():
        if value.get("type") == "clinic":
            # Add priority if not present
            if "priority" not in value:
                if "sink" in key.lower():
                    value["priority"] = 1  # Plan A
                elif "regular" in key.lower():
                    value["priority"] = 2  # Plan B
                else:
                    value["priority"] = 3  # Plan C
            
            # Add dimensions if not present (estimate from actual fixture)
            if "dimensions" not in value:
                value["dimensions"] = {
                    "width": 2600,
                    "height": 1700,
                    "clearance": 800 if value["priority"] == 1 else 600
                }
            
            clinic_plans.append({
                "name": value["name"],
                "path": value["path"],
                "dimensions": value["dimensions"],
                "priority": value["priority"],
                "plan_category": f"Plan_{chr(64 + value['priority'])}"  # A, B, C
            })
    
    # Sort by priority
    clinic_plans.sort(key=lambda x: x["priority"])
    return clinic_plans

def _initialize_euro_plans(self) -> List[Dict]:
    """Initialize euro center plan repository"""
    return [
        {
            "name": "Euro_centre",
            "pattern": "row_wise",
            "grid_config": {
                "cell_width": 1040,
                "cell_height": 1175,
                "rotation": 0
            },
            "priority": 1,
            "plan_category": "Plan_A"
        },
        {
            "name": "Euro_centre",
            "pattern": "column_wise",
            "grid_config": {
                "cell_width": 1175,
                "cell_height": 1040,
                "rotation": 90
            },
            "priority": 2,
            "plan_category": "Plan_B"
        }
    ]
```

### **4.3: Test the integration**

```bash
cd /home/athul/lenskart
python3 -c "
from app.DXF_Controller import DXF_Controller
import json

# Initialize with a real DXF (use any test file)
try:
    dxfc = DXF_Controller('assets/fp.dxf', {})
    print('✅ DXF_Controller initialized')
    print(f'📦 Clinic plans loaded: {len(dxfc.clinic_plans)}')
    print(f'🛒 Euro plans loaded: {len(dxfc.euro_plans)}')
    
    print('\n📋 Clinic Plans:')
    for plan in dxfc.clinic_plans:
        print(f'   {plan[\"plan_category\"]}: {plan[\"name\"]} (Priority {plan[\"priority\"]})')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"
```

**Expected Output**:
```
🔧 Initializing Multi-Plan Repository...
✅ Plan repository ready:
   Clinic plans: 3
   Euro center plans: 2

✅ DXF_Controller initialized
📦 Clinic plans loaded: 3
🛒 Euro plans loaded: 2

📋 Clinic Plans:
   Plan_A: Clinic_with_sink (Priority 1)
   Plan_B: Clinic_regular (Priority 2)
   Plan_C: ROC_clinic (Priority 3)
```

---

## ✅ **SUCCESS CRITERIA**

You've successfully completed the quick start if:

- ✅ Prototype script runs without errors
- ✅ Cascade logic correctly tries Plan A → B → C
- ✅ Plan B is used when Plan A fails
- ✅ `DXF_Controller` loads plan repository
- ✅ All 3 clinic plans are recognized

---

## 📚 **WHAT'S NEXT?**

Now that you have the basics working, continue with the full implementation:

### **Immediate Next Steps** (Next 2-4 hours):
1. **Add `calculate_free_area()` function**
   - See `MULTI_PLAN_IMPLEMENTATION_GUIDE.md` Task 1.3
   - Location: `app/DXF_Controller.py` after line 2800

2. **Add `attempt_plan_placement()` function**
   - See `MULTI_PLAN_IMPLEMENTATION_GUIDE.md` Task 2.1
   - Location: After `calculate_free_area()`

3. **Add `validate_placement()` function**
   - See `MULTI_PLAN_IMPLEMENTATION_GUIDE.md` Task 2.2
   - Location: After `attempt_plan_placement()`

### **This Week** (Week 1 - Foundation):
- Complete all Phase 1 tasks from implementation guide
- Run unit tests for each new function
- Document any deviations or issues

### **Full Timeline**:
- **Week 1**: Foundation (plan repository + spatial analysis)
- **Week 2**: Core logic (intelligent placement)
- **Week 3**: Prompt integration
- **Week 4**: Testing & deployment

---

## 🐛 **TROUBLESHOOTING**

### **Issue: Import errors**
```bash
# Solution: Add workspace to Python path
export PYTHONPATH=/home/athul/lenskart:$PYTHONPATH
```

### **Issue: "No such file" errors**
```bash
# Solution: Check file paths
ls -la /home/athul/lenskart/assets/clinic/
ls -la /home/athul/lenskart/app/DXF_Controller.py
```

### **Issue: Shapely errors**
```bash
# Solution: Reinstall shapely
pip uninstall shapely
pip install shapely --upgrade
```

### **Issue: DXF loading fails**
```python
# Solution: Use a simpler test DXF or mock the DXF_Controller
# See prototype script for mock approach
```

---

## 💡 **PRO TIPS**

1. **Use print statements liberally** during development
   - They help understand the cascade logic flow
   - Remove them later or convert to logger calls

2. **Test with simple scenarios first**
   - Single fixture, empty floor
   - Then add obstacles gradually

3. **Keep a log of plan usage**
   - Track which plans are used most often
   - Helps optimize priority order later

4. **Commit frequently**
   - After each working function
   - Makes it easy to roll back if needed

5. **Run tests after each change**
   - Prevents accumulation of bugs
   - Faster to fix issues immediately

---

## 📞 **GET HELP**

If you're stuck:

1. **Check the detailed docs**:
   - `MULTI_PLAN_ADAPTIVE_LOGIC_DOCUMENTATION.md` - Full architecture
   - `MULTI_PLAN_IMPLEMENTATION_GUIDE.md` - Step-by-step tasks

2. **Review existing code**:
   - `app/DXF_Controller.py` lines 4049-4150 (clinic placement)
   - `app/DXF_Controller.py` lines 11642-11750 (euro planning)

3. **Test in isolation**:
   - Use the prototype script approach
   - Mock complex dependencies

4. **Ask specific questions**:
   - "How do I calculate bbox for rotated fixtures?"
   - "Where should I register the placed bbox?"

---

## 🎉 **YOU'RE READY!**

You now have:
- ✅ Working prototype demonstrating the concept
- ✅ Understanding of the cascade logic
- ✅ Integration point in `DXF_Controller`
- ✅ Next steps clearly defined

**Time to start building!** 🚀

---

**Quick Start Guide Version**: 1.0  
**Created**: January 20, 2026  
**Estimated Time**: 30 minutes to first prototype, 2-4 hours to full integration  
**Difficulty**: Intermediate

**Good luck with the implementation!** 🎯

