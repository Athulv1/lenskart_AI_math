# 🎯 REQUEST TYPE LOGIC - QUICK REFERENCE

**Version**: 1.0  
**Date**: January 21, 2026  
**Project**: Lenskart AI 2.0 - Request-Specific Fixture Handling

---

## 📋 SUMMARY TABLE

| Request Type | Fixtures Redone | Logic Reason |
|-------------|-----------------|--------------|
| **BOH** | BOH Furniture + Clinics + Standing Tables + AR + Benches | Clinics define BOH zone boundary |
| **Clinic** | Clinics + Standing Tables + Benches + AR (if needed) | Clinical zone focus, dependent fixtures |
| **Wall Fixtures** | Wall merch validation + floor count adjustment | Merch mix compliance check |
| **Floor Fixtures** | Euro Centers + Floor displays (reuse or remake plans) | Adaptive based on count changes |

---

## 🔍 DETAILED BREAKDOWN

### 1️⃣ **BOH REQUEST**
**User Input**: `"Redo BOH"` or `"Rearrange back of house"`

**What Gets Redone**:
```
✅ BOH Furniture:
   - storage_rack, pickup_storage_900/1200
   - QC_table_large/medium
   - Repair_Table_large/medium
   - Dining_Table_large/medium
   - staff_rack, water_dispenser
   - drop_box, pick_up_counter

✅ Clinic Fixtures:
   - Clinic_regular
   - Clinic_with_sink
   - ROC_clinic

✅ Standing Tables:
   - Standing_table (anchored to clinics)

✅ AR Desks:
   - AR (Augmented Reality desk)

✅ Benches:
   - large_bench
   - medium_bench
```

**Why Clinics Are Included**:
- ✅ Clinics create the BOH zone boundary
- ✅ BOH furniture placed AFTER clinics define the zone
- ✅ Standing tables anchor to clinic positions
- ✅ Benches serve customers waiting for clinics

**Code Execution Order**:
```python
# BOH Request Flow:
1. place_clinics_with_best_fit_and_fallback()     # Define BOH boundary
2. place_boh_fixtures_in_room()                   # Fill BOH zone
3. place_standing_tables_landscape()              # Anchor to clinics
4. place_pos_ar_landscape()                       # Service desks
5. place_benches_near_clinics()                   # Customer seating
```

---

### 2️⃣ **CLINIC REQUEST**
**User Input**: `"Clinic"` or `"Reorganize clinic section"`

**What Gets Redone**:
```
✅ Clinic Fixtures ONLY:
   - Clinic_regular
   - Clinic_with_sink
   - ROC_clinic

✅ Standing Tables:
   - Standing_table (if anchored to clinics)

✅ Benches:
   - large_bench, medium_bench (near clinics)

✅ AR Desks:
   - AR (if position depends on clinic layout)
```

**What's NOT Touched**:
```
❌ BOH Furniture (stays in place)
❌ Wall Fixtures (perimeter stays fixed)
❌ Euro Centers (floor displays stay fixed)
❌ Discussion Tables (floor fixtures stay fixed)
```

**Code Execution Order**:
```python
# Clinic-Only Request Flow:
1. place_clinics_with_best_fit_and_fallback()     # Clinic placement only
2. place_standing_tables_landscape()              # Dependent fixtures
3. place_benches_near_clinics()                   # Adjacent seating
4. (Optional) place_pos_ar_landscape()            # If needed based on position
```

---

### 3️⃣ **WALL FIXTURES REQUEST**
**User Input**: `"Wall fixtures"` or `"Check merch mix wall placement"`

**What Gets Checked**:
```
✅ Wall Fixture Validation:
   - Count existing: jj_fixture_large/medium
   - Count existing: vc_fixture_large/medium
   - Count existing: window_1_section/3_section
   - Count existing: with_screen, jj_super_hybrid_*

✅ Merch Mix Comparison:
   - Compare against merch_mix.json requirements
   - Validate JJ_Eye, VC_Eye, JJ_Sun, VC_Sun totals

✅ Floor Count Adjustment (if needed):
   - If wall under-placed → Add more wall fixtures
   - If wall over-placed → Reduce floor fixtures
   - Maintain total merch mix balance
```

**Adjustment Logic**:
```python
# Wall Fixture Validation:
total_wall_units = count_placed_wall_fixtures()
required_units = merch_mix["JJ_Eye"] + merch_mix["VC_Eye"] + ...

if total_wall_units < required_units:
    # Under-placed: Add more wall fixtures
    add_wall_fixtures(required_units - total_wall_units)
    
elif total_wall_units > required_units:
    # Over-placed: Flag warning, adjust floor if possible
    adjust_floor_fixture_count(total_wall_units - required_units)
```

**Example Scenario**:
```
Merch Mix Required: JJ_Eye = 4.0 units
Currently Placed: 3.5 units (3 large + 1 medium)
Action: Add 1 more jj_fixture_medium OR adjust floor count
```

---

### 4️⃣ **FLOOR FIXTURES REQUEST**
**User Input**: `"Floor fixtures"` or `"Optimize euro centers"`

**What Gets Handled**:
```
✅ Floor Fixture Types:
   - Euro_centre (Reading Glasses displays)
   - Discussion_table_large/medium/small (VC_Kids)
   - Lensometer_large/medium/small (LK_Air)
   - QMS_desk, pos_with_screen_*, AR
   - sofa, Blue_zero, Standing_table
   - Corian_table, Lounge_seat

✅ Adaptive Logic:
   - Check existing plans (euro_plans.json)
   - If counts unchanged → Reuse existing plans
   - If counts changed → Regenerate plans
   - If no plans exist → Generate from scratch
```

**Decision Tree**:
```
┌─────────────────────────────────────────┐
│ Floor Fixture Request Received          │
└──────────────┬──────────────────────────┘
               │
               ▼
     ┌─────────────────────┐
     │ Check euro_plans.json│
     └─────────┬────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
   ┌───────┐      ┌─────────┐
   │ Exists│      │ Missing │
   └───┬───┘      └────┬────┘
       │               │
       ▼               ▼
┌──────────────┐  ┌───────────────┐
│Count Changed?│  │Generate Fresh │
└──┬────────┬──┘  │  Plans        │
   │        │     └───────────────┘
   ▼        ▼
 ┌────┐  ┌──────┐
 │YES │  │ NO   │
 └─┬──┘  └──┬───┘
   │        │
   ▼        ▼
┌─────┐  ┌──────┐
│Regen│  │Reuse │
└─────┘  └──────┘
```

**Example - Euro Center Count Change**:
```
Previous: 6 Euro_centre → euro_plans.json has 4 patterns
Request: "Add 2 more euro centers"
New Total: 8 Euro_centre

Action:
1. Detect count change (6 → 8)
2. Invalidate old plans
3. Generate new patterns:
   - Pattern A: 2x4 grid (row-wise)
   - Pattern B: 4x2 grid (column-wise)
   - Pattern C: 2-3-3 mixed (optimized)
   - Pattern D: Compact 8 (tight spacing)
4. Rank by efficiency & space utilization
5. Execute top 2 patterns → 2 DXF outputs
```

---

## 🔄 COMBINED VS SEPARATED LOGIC

### **Current Implementation (Combined)**

```
"Redo BOH" = Everything in BOH Zone
├── BOH Furniture (storage, workstations)
├── Clinics (define zone boundary)
├── Standing Tables (anchor to clinics)
├── AR Desks (service area)
└── Benches (customer seating)
```

**Why Combined?**:
- ✅ Clinics define the BOH zone boundary
- ✅ Can't place BOH furniture without knowing clinic positions
- ✅ Standing tables and benches depend on clinic locations
- ✅ Single workflow ensures spatial coherence

### **Future Option (Separated)**

If you want to separate BOH furniture from clinics:

```
"Redo BOH furniture only" 
└── JUST: storage_rack, QC_table, Dining_Table, etc.
    (Assumes clinics already placed)

"Redo clinic section"
└── JUST: Clinics + Standing Tables + Benches
    (Separate from BOH furniture)

"Redo complete BOH zone"
└── EVERYTHING: BOH furniture + Clinics + All dependents
    (Current behavior)
```

**Implementation Change Needed**:
```python
# Current:
def handle_boh_request():
    place_clinics()          # Always included
    place_boh_furniture()
    place_standing_tables()
    place_benches()

# Separated Option:
def handle_boh_request(scope: str):
    if scope == "furniture_only":
        place_boh_furniture()  # Skip clinic placement
    elif scope == "clinic_only":
        place_clinics()
        place_standing_tables()
        place_benches()
    else:  # "complete"
        place_clinics()
        place_boh_furniture()
        place_standing_tables()
        place_benches()
```

---

## 🎯 REQUEST CLASSIFICATION LOGIC

### **How System Determines Request Type**

```python
def classify_fixture_request(user_prompt: str) -> str:
    """
    Classify user request into specific fixture categories
    
    Returns:
        - "boh_complete": BOH + Clinics + Standing Tables + AR + Benches
        - "clinic_only": Clinics + Standing Tables + Benches (no BOH furniture)
        - "wall_fixtures": Wall merch validation + count adjustment
        - "floor_fixtures": Euro centers + floor displays (adaptive)
    """
    
    prompt_lower = user_prompt.lower()
    
    # BOH Request (includes clinics)
    if any(kw in prompt_lower for kw in 
           ["boh", "back of house", "storage area", "work area", "back area"]):
        return "boh_complete"
    
    # Clinic-Only Request
    elif any(kw in prompt_lower for kw in 
             ["clinic", "examination", "patient area", "exam room"]):
        return "clinic_only"
    
    # Wall Fixtures Request
    elif any(kw in prompt_lower for kw in 
             ["wall fixtures", "wall merch", "perimeter", "wall display"]):
        return "wall_fixtures"
    
    # Floor Fixtures Request
    elif any(kw in prompt_lower for kw in 
             ["floor fixtures", "euro", "euro center", "discussion table", 
              "lensometer", "floor merch", "floor display"]):
        return "floor_fixtures"
    
    # Default: analyze context
    else:
        return analyze_context(user_prompt)
```

---

## 📊 MERCH MIX VALIDATION

### **All Requests Validate Against Merch Mix**

```json
// merch_mix.json
{
  "merch_mix_min": {
    "JJ_Eye": "4.0",        // → Wall: jj_fixture_*
    "JJ_Sun": "1.0",        // → Wall: jj_super_hybrid_*
    "VC_Eye": "4.1",        // → Wall: vc_fixture_*
    "VC_Sun": "2.2",        // → Wall: window_*, with_screen
    "LK_Air": "4.7",        // → Floor: Lensometer_*
    "VC_Kids": "2.0",       // → Floor: Discussion_table_*
    "Reading_Glasses": "0.0", // → Floor: Euro_centre
    "CL": "0.0",            // → Clinic: Clinic_regular
    "OD": "0.0",            // → Clinic: Clinic_with_sink
    "LPL": "0.0"            // → Clinic: ROC_clinic
  }
}
```

### **Validation Process**

```
STEP 1: Count Placed Fixtures
├── Wall: jj_fixture_large (2.0 units each)
├── Wall: vc_fixture_medium (1.5 units each)
├── Floor: Euro_centre (1.0 unit each)
└── Clinic: Clinic_with_sink (1.0 unit each)

STEP 2: Calculate Category Totals
├── JJ_Eye: 4.0 units (2 large = 4.0)
├── VC_Eye: 4.5 units (3 medium = 4.5)
├── Reading_Glasses: 6.0 units (6 euro = 6.0)
└── CL: 3.0 units (3 clinics = 3.0)

STEP 3: Compare Against Merch Mix
├── JJ_Eye: 4.0 >= 4.0 ✅ (meets minimum)
├── VC_Eye: 4.5 >= 4.1 ✅ (exceeds minimum by 0.4)
├── Reading_Glasses: 6.0 >= 0.0 ✅ (optional, placed)
└── CL: 3.0 >= 0.0 ✅ (optional, placed)

STEP 4: Flag Issues
├── Under-placed: JJ_Sun (0.0 < 1.0) ⚠️ WARNING
├── Over-placed: VC_Eye (+0.4) ℹ️ INFO
└── Missing: LK_Air (not placed) ⚠️ WARNING

STEP 5: Suggest Adjustments
└── "Add 1 jj_super_hybrid_medium to meet JJ_Sun requirement"
└── "Add 3-5 Lensometer fixtures to meet LK_Air requirement"
```

---

## 🚦 QUICK DECISION GUIDE

### **"Should I redo clinics when BOH is requested?"**

**YES** - Because:
1. ✅ Clinics define where the BOH zone starts
2. ✅ BOH furniture is placed AFTER clinics create the boundary
3. ✅ Standing tables anchor to clinic positions
4. ✅ Benches serve customers waiting for clinics

### **"Should I adjust floor counts when wall fixtures change?"**

**YES** - Because:
1. ✅ Merch mix has TOTAL requirements (wall + floor combined)
2. ✅ Over-placing wall fixtures reduces floor fixture budget
3. ✅ Under-placing wall fixtures requires floor compensation
4. ✅ Maintain total brand representation balance

### **"Should I regenerate plans if floor fixture count changes?"**

**YES** - Because:
1. ✅ Grid patterns optimized for specific counts
2. ✅ 6 Euro Centers use different patterns than 8
3. ✅ Spatial efficiency depends on fixture quantity
4. ✅ Old plans may not accommodate new counts

### **"Can I place BOH furniture without moving clinics?"**

**MAYBE** - If:
1. ✅ Clinics already define a valid BOH zone
2. ✅ BOH zone has sufficient depth (1800-2400mm)
3. ✅ No spatial conflicts with new BOH furniture layout
4. ❌ Otherwise, clinics must be repositioned first

---

## 🎯 IMPLEMENTATION CHECKLIST

### **For BOH Requests:**
- [ ] Classify as "boh_complete"
- [ ] Execute clinic placement first
- [ ] Create BOH zone based on clinic positions
- [ ] Place BOH furniture in zone
- [ ] Anchor standing tables to clinics
- [ ] Position benches near clinic entrances
- [ ] Place AR desks if needed

### **For Clinic Requests:**
- [ ] Classify as "clinic_only"
- [ ] Execute clinic placement
- [ ] Update standing table positions
- [ ] Reposition benches near new clinic locations
- [ ] Optionally adjust AR desk positions
- [ ] Leave BOH furniture untouched
- [ ] Leave wall fixtures untouched

### **For Wall Fixture Requests:**
- [ ] Classify as "wall_fixtures"
- [ ] Count existing wall fixtures by type
- [ ] Calculate total wall merch mix units
- [ ] Compare against merch_mix.json requirements
- [ ] Flag under-placed categories
- [ ] Suggest floor count adjustments if needed
- [ ] Do NOT move existing fixtures unless required

### **For Floor Fixture Requests:**
- [ ] Classify as "floor_fixtures"
- [ ] Check for existing euro_plans.json
- [ ] Compare current count vs planned count
- [ ] IF counts match → Reuse existing plans
- [ ] IF counts differ → Regenerate plans
- [ ] IF no plans → Generate from scratch
- [ ] Execute top-ranked patterns

---

## 📝 EXAMPLES

### **Example 1: BOH Request**
```
User: "Redo BOH"
System:
  1. Classifies as: boh_complete
  2. Executes: clinics → BOH furniture → standing tables → benches
  3. Result: Complete BOH zone reorganized
```

### **Example 2: Clinic Request**
```
User: "Reorganize clinics"
System:
  1. Classifies as: clinic_only
  2. Executes: clinics → standing tables → benches
  3. Result: Clinical area optimized, BOH furniture untouched
```

### **Example 3: Wall Fixtures Request**
```
User: "Check wall merch mix"
System:
  1. Classifies as: wall_fixtures
  2. Counts: JJ_Eye (3.5 units) < Required (4.0 units)
  3. Suggests: "Add 1 jj_fixture_medium"
  4. Result: Merch mix compliance restored
```

### **Example 4: Floor Fixtures Request**
```
User: "Add 2 more euro centers"
System:
  1. Classifies as: floor_fixtures
  2. Detects: Count changed (6 → 8)
  3. Regenerates: New grid patterns for 8 units
  4. Executes: Top 2 patterns → 2 DXF outputs
  5. Result: 8 Euro Centers optimally arranged
```

---

## 🔗 RELATED DOCUMENTATION

- **MAIN_DOCUMENTATION.md**: Complete system architecture
- **MULTI_PLAN_ADAPTIVE_LOGIC_DOCUMENTATION.md**: Plan generation algorithms
- **USAGE_EXAMPLES.md**: Real-world request examples
- **COMPLEX_PROMPT_FLOW_DIAGRAMS.md**: Decision flow visualization

---

**Last Updated**: January 21, 2026  
**Maintained By**: Lenskart AI Development Team
