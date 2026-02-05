 # 🗺️ **MULTI-PLAN ADAPTIVE LOGIC: DETAILED IMPLEMENTATION PLAN**

## **Step-by-Step Execution Guide for Development Team**

---

**Document Version**: 1.0  
**Created**: January 20, 2026  
**Implementation Owner**: Lenskart Development Team  
**Estimated Timeline**: 4 weeks  
**Priority**: HIGH

---

## 📋 **PREREQUISITES CHECKLIST**

Before beginning implementation, verify:

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Access to `app/DXF_Controller.py` (19,537 lines)
- [ ] Access to `dashboard/ai_fixture_mover.py` (368 lines)
- [ ] Gemini API key configured in environment
- [ ] Test DXF files available in `assets/` directory
- [ ] Understanding of existing codebase architecture
- [ ] Review of `MATHEMATICAL_MODEL_INTEGRATION_PLAN.md`
- [ ] Review of `MULTI_PLAN_ADAPTIVE_LOGIC_DOCUMENTATION.md`

---

## 🎯 **IMPLEMENTATION PHASES**

```
Phase 1: Repository Setup          [Week 1] ──┐
Phase 2: Core Logic Implementation [Week 2] ──┤
Phase 3: Prompt Integration        [Week 3] ──┤──> Complete System
Phase 4: Testing & Refinement      [Week 4] ──┘
```

---

## 📦 **PHASE 1: PLAN REPOSITORY SETUP (Week 1)**

### **Day 1-2: Data Structure Enhancement**

#### **Task 1.1: Enhance fixture_dict with plan metadata**

**File**: `app/DXF_Controller.py`  
**Location**: Lines ~51-310 (fixture_dict definition)

**Action**: Add metadata for multi-plan support

```python
# BEFORE (Current structure):
"Clinic_with_sink": {
    "name": "Clinic_with_sink",
    "path": "assets/clinic/Clinic_with_sink.dxf",
    "type": "clinic"
}

# AFTER (Enhanced structure):
"Clinic_with_sink": {
    "name": "Clinic_with_sink",
    "path": "assets/clinic/Clinic_with_sink.dxf",
    "type": "clinic",
    "dimensions": {
        "width": 2600,      # mm
        "height": 1700,     # mm
        "clearance": 800    # mm (required circulation space)
    },
    "priority": 1,          # Lower = higher priority (Plan A)
    "use_case": "Standard store layout with plumbing",
    "plan_category": "Plan_A"
}
```

**Implementation Steps**:

1. **Measure actual fixture dimensions**:
   ```python
   # Add this helper function to DXF_Controller class
   def measure_fixture_dimensions(self, fixture_name: str) -> dict:
       """Extract actual dimensions from DXF file"""
       fixture_path = self.fixture_dict[fixture_name]["path"]
       fixture_obj = Fixture.Fixture(fixture_name, fixture_path)
       bbox = fixture_obj.bounding_box
       
       return {
           "width": bbox.size.x,
           "height": bbox.size.y,
           "depth": bbox.size.z if hasattr(bbox.size, 'z') else 0
       }
   ```

2. **Run measurement script for all clinics**:
   ```python
   # Create: scripts/measure_all_fixtures.py
   from app.DXF_Controller import DXF_Controller
   import json
   
   # Dummy initialization to access fixture_dict
   clinic_fixtures = [
       "Clinic_with_sink",
       "Clinic_regular", 
       "ROC_clinic"
   ]
   
   measurements = {}
   for fixture in clinic_fixtures:
       # Measure and record
       # Output to JSON file
   ```

3. **Update fixture_dict with measurements**:
   - Copy measurements to fixture definitions
   - Add priority rankings
   - Add use_case descriptions

**Acceptance Criteria**:
- ✅ All clinic fixtures have complete metadata
- ✅ All euro center fixtures have grid_config
- ✅ Priority values assigned (1=Plan A, 2=Plan B, 3=Plan C)
- ✅ No runtime errors when loading fixture_dict

---

#### **Task 1.2: Create plan initialization functions**

**File**: `app/DXF_Controller.py`  
**Location**: Add to `__init__` method (around line 400)

**Action**: Add plan loading during initialization

```python
def __init__(self, fp_path, merch_mix, boundary_threshold=50.0):
    """Initialize DXF Controller with multi-plan support"""
    
    # ... existing initialization code ...
    
    # NEW: Initialize plan repository
    print("\n🔧 Initializing Multi-Plan Repository...")
    self.clinic_plans = self._initialize_clinic_plans()
    self.euro_plans = self._initialize_euro_plans()
    
    print(f"✅ Plan repository ready:")
    print(f"   Clinic plans: {len(self.clinic_plans)}")
    print(f"   Euro center plans: {len(self.euro_plans)}")
    
    # ... rest of initialization ...

def _initialize_clinic_plans(self) -> List[Dict]:
    """
    Extract and rank clinic fixture plans from fixture_dict.
    
    Returns:
        List of clinic plan dictionaries, sorted by priority
    """
    clinic_plans = []
    
    for key, value in self.fixture_dict.items():
        if value.get("type") == "clinic":
            # Pre-load fixture object
            try:
                fixture_obj = Fixture.Fixture(
                    value["name"], 
                    value["path"]
                )
                
                clinic_plans.append({
                    "name": value["name"],
                    "path": value["path"],
                    "dimensions": value.get("dimensions", {}),
                    "priority": value.get("priority", 99),
                    "use_case": value.get("use_case", ""),
                    "plan_category": value.get("plan_category", "Unknown"),
                    "fixture_obj": fixture_obj,
                    "bbox": fixture_obj.bounding_box
                })
                
                print(f"   Loaded: {value['name']} (Priority {value.get('priority', 99)})")
                
            except Exception as e:
                logger.warning(f"Could not load clinic fixture {key}: {e}")
                continue
    
    # Sort by priority (lower number = higher priority)
    clinic_plans.sort(key=lambda x: x["priority"])
    
    return clinic_plans

def _initialize_euro_plans(self) -> List[Dict]:
    """
    Extract and rank euro center grid patterns.
    
    Returns:
        List of euro plan dictionaries, sorted by priority
    """
    euro_plans = []
    
    # Define grid configurations
    # Plan A: Row-wise (0° rotation)
    euro_plans.append({
        "name": "Euro_centre",
        "path": self.fixture_dict["Euro_centre"]["path"],
        "grid_config": {
            "cell_width": 1040,
            "cell_height": 1175,
            "rotation": 0,
            "layout_pattern": "row_wise"
        },
        "priority": 1,
        "plan_category": "Plan_A",
        "pattern": "row_wise"
    })
    
    # Plan B: Column-wise (90° rotation)
    euro_plans.append({
        "name": "Euro_centre",
        "path": self.fixture_dict["Euro_centre"]["path"],
        "grid_config": {
            "cell_width": 1175,
            "cell_height": 1040,
            "rotation": 90,
            "layout_pattern": "column_wise"
        },
        "priority": 2,
        "plan_category": "Plan_B",
        "pattern": "column_wise"
    })
    
    # Plan C: Mixed/Optimized
    euro_plans.append({
        "name": "Euro_centre",
        "path": self.fixture_dict["Euro_centre"]["path"],
        "grid_config": {
            "cell_width": 1040,
            "cell_height": 1175,
            "rotation": "dynamic",
            "layout_pattern": "optimized"
        },
        "priority": 3,
        "plan_category": "Plan_C",
        "pattern": "optimized"
    })
    
    return euro_plans
```

**Testing**:
```python
# Create: tests/test_plan_initialization.py
def test_clinic_plans_loaded():
    dxfc = DXF_Controller("test_floor.dxf", {})
    assert len(dxfc.clinic_plans) >= 3
    assert dxfc.clinic_plans[0]["priority"] == 1  # Plan A first

def test_euro_plans_loaded():
    dxfc = DXF_Controller("test_floor.dxf", {})
    assert len(dxfc.euro_plans) == 3
    assert dxfc.euro_plans[0]["pattern"] == "row_wise"
```

**Acceptance Criteria**:
- ✅ `_initialize_clinic_plans()` returns sorted list
- ✅ `_initialize_euro_plans()` returns 3 patterns
- ✅ Fixture objects pre-loaded successfully
- ✅ No errors during initialization
- ✅ Unit tests pass

---

### **Day 3-4: Spatial Analysis Functions**

#### **Task 1.3: Implement calculate_free_area()**

**File**: `app/DXF_Controller.py`  
**Location**: Add new method (suggest after line 2800)

```python
def calculate_free_area(
    self, 
    doc: "dxf_doc.DXF_Document",
    zone_filter: Optional[str] = None
) -> Polygon:
    """
    Calculate available placement area by subtracting obstacles
    from the floor boundary polygon.
    
    This implements STEP A of the adaptive selection algorithm.
    
    Args:
        doc: DXF_Document instance
        zone_filter: Optional zone name to limit calculation 
                     (e.g., "clinic", "boh", "floor")
    
    Returns:
        Polygon: Free_Area_Polygon (shapely.geometry.Polygon)
        
    Example:
        >>> free_area = dxfc.calculate_free_area(doc, zone_filter="clinic")
        >>> print(f"Available space: {free_area.area / 1_000_000:.2f} m²")
    """
    print(f"\n{'='*70}")
    print(f"🔍 SPATIAL ANALYSIS: Calculating Free Area")
    print(f"{'='*70}")
    
    if zone_filter:
        print(f"Zone filter: {zone_filter}")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 1: Get floor boundary
    # ─────────────────────────────────────────────────────────────────
    if zone_filter and hasattr(doc, f"{zone_filter}_zone"):
        # Use specific zone boundary if available
        floor_boundary = getattr(doc, f"{zone_filter}_zone")
        print(f"Using zone-specific boundary: {zone_filter}_zone")
    else:
        # Use full floor boundary
        floor_boundary = doc.floor_boundary_polygon
        print(f"Using full floor boundary")
    
    floor_area = floor_boundary.area / 1_000_000  # Convert to m²
    print(f"Floor boundary area: {floor_area:.2f} m²")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 2: Collect all obstacles
    # ─────────────────────────────────────────────────────────────────
    obstacles = []
    
    # 2a. Wall polygons (with thickness buffer)
    wall_count = 0
    if hasattr(doc, 'wall_segments'):
        for wall_seg in doc.wall_segments:
            try:
                # Convert wall segment to polygon with thickness
                p1 = Vec2(wall_seg[0], wall_seg[1])
                p2 = Vec2(wall_seg[2], wall_seg[3])
                
                # Create perpendicular offset
                wall_vector = (p2 - p1).normalize()
                perpendicular = wall_vector.orthogonal() * (self.WALL_THICKNESS / 2)
                
                # Create wall polygon
                wall_poly = Polygon([
                    (p1.x + perpendicular.x, p1.y + perpendicular.y),
                    (p2.x + perpendicular.x, p2.y + perpendicular.y),
                    (p2.x - perpendicular.x, p2.y - perpendicular.y),
                    (p1.x - perpendicular.x, p1.y - perpendicular.y)
                ])
                
                obstacles.append(wall_poly)
                wall_count += 1
                
            except Exception as e:
                logger.warning(f"Could not process wall segment: {e}")
                continue
    
    print(f"Wall obstacles: {wall_count}")
    
    # 2b. Existing fixtures (from bounding box registry)
    fixture_count = 0
    if hasattr(doc, 'all_placed_bboxes'):
        for bbox in doc.all_placed_bboxes:
            try:
                # Convert bounding box to polygon
                fixture_poly = box(
                    bbox.extmin.x, 
                    bbox.extmin.y, 
                    bbox.extmax.x, 
                    bbox.extmax.y
                )
                obstacles.append(fixture_poly)
                fixture_count += 1
                
            except Exception as e:
                logger.warning(f"Could not process fixture bbox: {e}")
                continue
    
    print(f"Fixture obstacles: {fixture_count}")
    
    # 2c. Restricted zones (doors, windows, circulation paths)
    restricted_count = 0
    if hasattr(doc, 'restricted_zones'):
        for zone in doc.restricted_zones:
            try:
                obstacles.append(zone.polygon)
                restricted_count += 1
            except:
                continue
    
    print(f"Restricted zones: {restricted_count}")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 3: Calculate free area (floor - obstacles)
    # ─────────────────────────────────────────────────────────────────
    if obstacles:
        # Union all obstacles into single geometry
        obstacle_union = unary_union(obstacles)
        obstacle_area = obstacle_union.area / 1_000_000
        
        # Subtract from floor boundary
        free_area = floor_boundary.difference(obstacle_union)
        free_area_m2 = free_area.area / 1_000_000
        
        print(f"\nObstacle area: {obstacle_area:.2f} m²")
        print(f"Free area: {free_area_m2:.2f} m²")
        print(f"Utilization: {(1 - free_area_m2/floor_area)*100:.1f}%")
    else:
        # No obstacles, entire floor is free
        free_area = floor_boundary
        print(f"\nNo obstacles detected")
        print(f"Free area: {floor_area:.2f} m² (100%)")
    
    print(f"{'='*70}\n")
    
    return free_area
```

**Testing**:
```python
# Create: tests/test_spatial_analysis.py
def test_calculate_free_area_no_obstacles():
    dxfc = DXF_Controller("test_floor.dxf", {})
    doc = dxfc.docs[0]
    free_area = dxfc.calculate_free_area(doc)
    
    assert free_area.area > 0
    assert free_area.is_valid

def test_calculate_free_area_with_fixtures():
    # Setup: Place some fixtures
    # Test: Free area should be reduced
    pass
```

**Acceptance Criteria**:
- ✅ Function returns valid Polygon
- ✅ Handles empty obstacle list
- ✅ Correctly subtracts obstacles
- ✅ Area calculations accurate
- ✅ Unit tests pass

---

### **Day 5: Documentation & Review**

#### **Task 1.4: Create developer documentation**

**File**: Create `docs/DEVELOPER_GUIDE_PHASE1.md`

**Content**:
- Overview of plan repository structure
- How to add new fixture plans
- How to modify plan priorities
- Usage examples for `calculate_free_area()`
- Troubleshooting common issues

#### **Task 1.5: Phase 1 code review**

**Checklist**:
- [ ] All functions documented with docstrings
- [ ] Unit tests written and passing
- [ ] No breaking changes to existing code
- [ ] Performance benchmarks acceptable
- [ ] Peer review completed

---

## 🧮 **PHASE 2: CORE LOGIC IMPLEMENTATION (Week 2)**

### **Day 1-2: Placement Attempt Functions**

#### **Task 2.1: Implement attempt_plan_placement()**

**File**: `app/DXF_Controller.py`  
**Location**: Add after `calculate_free_area()`

```python
def attempt_plan_placement(
    self, 
    plan: Dict, 
    free_area: Polygon, 
    target_position: Tuple[float, float],
    rotation: float = 0.0
) -> Optional[Dict]:
    """
    Attempt to place a fixture plan at the target position.
    
    This implements STEP B of the adaptive selection algorithm.
    
    Args:
        plan: Plan dictionary from clinic_plans or euro_plans
        free_area: Available space polygon
        target_position: (x, y) coordinates for placement
        rotation: Rotation angle in degrees
    
    Returns:
        Dict with placement details if successful, None if fails
        
    Example:
        >>> plan = dxfc.clinic_plans[0]  # Plan A
        >>> placement = dxfc.attempt_plan_placement(
        ...     plan, free_area, (5000, 3000)
        ... )
        >>> if placement:
        ...     print(f"Success: {placement['plan_name']}")
    """
    print(f"\n🎯 ATTEMPTING PLACEMENT: {plan['name']}")
    print(f"   Plan category: {plan.get('plan_category', 'Unknown')}")
    print(f"   Priority: {plan['priority']}")
    print(f"   Target position: {target_position}")
    print(f"   Rotation: {rotation}°")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 1: Extract plan dimensions
    # ─────────────────────────────────────────────────────────────────
    dimensions = plan.get("dimensions", {})
    width = dimensions.get("width", 0)
    height = dimensions.get("height", 0)
    clearance = dimensions.get("clearance", 0)
    
    if width == 0 or height == 0:
        print(f"   ❌ ERROR: Invalid dimensions in plan")
        return None
    
    print(f"   Dimensions: {width}mm x {height}mm")
    print(f"   Clearance: {clearance}mm")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 2: Create bounding box at target position
    # ─────────────────────────────────────────────────────────────────
    x, y = target_position
    
    # Create box with clearance
    placement_bbox = box(
        x - (width / 2) - clearance,
        y - (height / 2) - clearance,
        x + (width / 2) + clearance,
        y + (height / 2) + clearance
    )
    
    # Apply rotation if needed
    if rotation != 0.0:
        placement_bbox = affinity.rotate(
            placement_bbox, 
            rotation, 
            origin=(x, y)
        )
    
    bbox_area = placement_bbox.area / 1_000_000
    print(f"   Bounding box: {placement_bbox.bounds}")
    print(f"   Required area: {bbox_area:.2f} m²")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 3: Check if bbox fits within free area
    # ─────────────────────────────────────────────────────────────────
    if not free_area.contains(placement_bbox):
        # Check how much is outside
        if not placement_bbox.intersects(free_area):
            print(f"   ❌ FAILED: Bbox completely outside free area")
            return None
        
        intersection = placement_bbox.intersection(free_area)
        overlap_pct = (intersection.area / placement_bbox.area) * 100
        
        if overlap_pct < 90:  # Require 90% inside
            print(f"   ❌ FAILED: Only {overlap_pct:.1f}% inside free area")
            return None
        else:
            print(f"   ⚠️  WARNING: {overlap_pct:.1f}% inside (marginal)")
    
    print(f"   ✅ SUCCESS: Bbox fits within free area")
    
    # ─────────────────────────────────────────────────────────────────
    # STEP 4: Return placement details
    # ─────────────────────────────────────────────────────────────────
    return {
        "plan_name": plan["name"],
        "plan_category": plan.get("plan_category", "Unknown"),
        "priority": plan["priority"],
        "position": target_position,
        "rotation": rotation,
        "bbox": placement_bbox,
        "dimensions": dimensions,
        "fixture": plan.get("fixture_obj"),
        "use_case": plan.get("use_case", "")
    }
```

**Acceptance Criteria**:
- ✅ Handles various fixture sizes correctly
- ✅ Rotation applied properly
- ✅ Clearance buffer included
- ✅ Returns None for invalid placements
- ✅ Logs detailed information

---

#### **Task 2.2: Implement validate_placement()**

**File**: `app/DXF_Controller.py`  
**Location**: Add after `attempt_plan_placement()`

```python
def validate_placement(
    self, 
    placement: Dict, 
    obstacles: List[Polygon],
    doc: Optional["dxf_doc.DXF_Document"] = None
) -> Tuple[bool, str]:
    """
    Validate placement against all obstacles and design rules.
    
    This implements STEP C of the adaptive selection algorithm.
    
    Args:
        placement: Placement dictionary from attempt_plan_placement()
        obstacles: List of obstacle polygons
        doc: Optional document for additional context
    
    Returns:
        (is_valid, reason) tuple
        
    Example:
        >>> is_valid, reason = dxfc.validate_placement(
        ...     placement, obstacles, doc
        ... )
        >>> if is_valid:
        ...     print("Placement approved")
        >>> else:
        ...     print(f"Rejected: {reason}")
    """
    print(f"\n✔️  VALIDATING PLACEMENT: {placement['plan_name']}")
    
    placement_bbox = placement["bbox"]
    
    # ─────────────────────────────────────────────────────────────────
    # CHECK 1: Collision detection with obstacles
    # ─────────────────────────────────────────────────────────────────
    print(f"   Checking collisions with {len(obstacles)} obstacles...")
    
    for i, obstacle in enumerate(obstacles):
        if placement_bbox.intersects(obstacle):
            intersection = placement_bbox.intersection(obstacle)
            intersection_area = intersection.area
            overlap_pct = (intersection_area / placement_bbox.area) * 100
            
            # Allow minor overlaps (< 1%) due to floating point errors
            if overlap_pct > 1.0:
                reason = (
                    f"Collision with obstacle {i+1}: "
                    f"{overlap_pct:.1f}% overlap "
                    f"({intersection_area / 1_000_000:.3f} m²)"
                )
                print(f"   ❌ INVALID: {reason}")
                return False, reason
    
    print(f"   ✅ No collisions detected")
    
    # ─────────────────────────────────────────────────────────────────
    # CHECK 2: Design rule compliance
    # ─────────────────────────────────────────────────────────────────
    design_valid, design_reason = self._check_design_rules(placement, doc)
    
    if not design_valid:
        print(f"   ❌ INVALID: {design_reason}")
        return False, design_reason
    
    print(f"   ✅ Design rules satisfied")
    
    # ─────────────────────────────────────────────────────────────────
    # CHECK 3: Accessibility check (optional)
    # ─────────────────────────────────────────────────────────────────
    # Ensure fixture is accessible (not completely surrounded)
    # This can be enhanced based on specific requirements
    
    print(f"   ✅ Placement VALID")
    return True, "Valid placement"

def _check_design_rules(
    self, 
    placement: Dict, 
    doc: Optional["dxf_doc.DXF_Document"] = None
) -> Tuple[bool, str]:
    """
    Verify compliance with Lenskart design guidelines.
    
    Design rules include:
    - Minimum clearance requirements
    - Circulation path widths
    - Distance from doors/exits
    - Zoning restrictions
    
    Args:
        placement: Placement dictionary
        doc: Document for context
    
    Returns:
        (is_valid, reason) tuple
    """
    dimensions = placement.get("dimensions", {})
    clearance = dimensions.get("clearance", 0)
    
    # Rule 1: Minimum clearance (varies by fixture type)
    MIN_CLEARANCES = {
        "clinic": 800,    # mm
        "floor": 600,     # mm
        "boh": 500        # mm
    }
    
    # Determine fixture type
    fixture_type = placement.get("plan_name", "").lower()
    if "clinic" in fixture_type:
        min_clearance = MIN_CLEARANCES["clinic"]
    elif "euro" in fixture_type:
        min_clearance = MIN_CLEARANCES["floor"]
    else:
        min_clearance = MIN_CLEARANCES["boh"]
    
    if clearance < min_clearance:
        return False, f"Insufficient clearance: {clearance}mm < {min_clearance}mm"
    
    # Rule 2: Minimum circulation corridor (1200mm)
    # This would require checking distance to nearest wall/obstacle
    # Implementation depends on available spatial data
    
    # Rule 3: No fixtures within 500mm of doors
    # This would require door location data
    if doc and hasattr(doc, 'door_locations'):
        for door in doc.door_locations:
            door_point = Point(door[0], door[1])
            distance = placement["bbox"].distance(door_point)
            if distance < 500:
                return False, f"Too close to door: {distance:.0f}mm < 500mm"
    
    # All checks passed
    return True, "Design rules satisfied"
```

**Acceptance Criteria**:
- ✅ Accurate collision detection
- ✅ Design rules enforced
- ✅ Clear error messages
- ✅ Handles edge cases
- ✅ Performance acceptable (< 100ms per validation)

---

### **Day 3-4: Intelligent Placement Core**

#### **Task 2.3: Implement intelligent_place_clinic()**

**File**: `app/DXF_Controller.py`  
**Location**: Add after validation functions

**Implementation**: See full code in `MULTI_PLAN_ADAPTIVE_LOGIC_DOCUMENTATION.md` section 4.1

**Key Points**:
1. Collect obstacles from `doc.all_placed_bboxes`
2. Calculate target positions using `_calculate_optimal_positions()`
3. Loop through plans in priority order
4. Execute placement and update obstacles
5. Return comprehensive results

**Testing**:
```python
# Create: tests/test_intelligent_placement.py
def test_intelligent_place_single_clinic():
    dxfc = DXF_Controller("test_floor.dxf", {})
    doc = dxfc.docs[0]
    free_area = dxfc.calculate_free_area(doc)
    
    placements = dxfc.intelligent_place_clinic(
        doc, free_area, "clinic", quantity=1
    )
    
    assert len(placements) == 1
    assert placements[0]["success"] == True

def test_intelligent_place_fallback_to_plan_b():
    # Create constrained space where Plan A won't fit
    # Verify Plan B is used
    pass
```

**Acceptance Criteria**:
- ✅ Successfully places fixtures
- ✅ Fallback cascade works
- ✅ Returns detailed results
- ✅ Updates obstacle registry
- ✅ Unit tests pass

---

#### **Task 2.4: Implement _execute_placement()**

**Implementation**: See full code in `MULTI_PLAN_ADAPTIVE_LOGIC_DOCUMENTATION.md` section 4.1

**Key Functions**:
- Calculate insertion point from center
- Apply transformation matrix
- Insert block reference into DXF
- Update `doc.all_placed_bboxes`
- Return bounding box

**Acceptance Criteria**:
- ✅ Fixtures placed at correct positions
- ✅ Rotation applied correctly
- ✅ Bounding boxes registered
- ✅ No DXF corruption

---

### **Day 5: Integration with Existing Functions**

#### **Task 2.5: Enhance place_clinics_from_ranked_plan()**

**File**: `app/DXF_Controller.py`  
**Location**: Lines 4049-4150

**Action**: Add fallback to adaptive logic

```python
def place_clinics_from_ranked_plan(
    self, 
    doc,
    chosen_plan,
    distributed_segments: Dict[str, Any]
) -> bool:
    """
    [EXISTING FUNCTION - ENHANCED]
    
    Executes clinic placement with adaptive fallback.
    """
    print("\n--- 🚀 Executing Clinic Placement Plan ---")
    
    if not chosen_plan:
        print("  -> No plan available.")
        return False
    
    # ... existing placement logic ...
    
    try:
        # ... attempt original plan placement ...
        success = self._place_original_plan(chosen_plan, distributed_segments)
        
        if success:
            return True
    
    except PlacementError as e:
        print(f"  -> Primary plan failed: {e}")
    
    # NEW: Fallback to adaptive logic if primary fails
    print("\n⚡ PRIMARY PLAN FAILED - Activating Adaptive Logic...")
    
    # Calculate available space
    free_area = self.calculate_free_area(doc, zone_filter="clinic")
    
    # Determine quantity from plan
    quantity = len(chosen_plan.get("combo", []))
    
    # Try intelligent placement
    placements = self.intelligent_place_clinic(
        doc,
        free_area,
        target_zone="clinic",
        quantity=quantity
    )
    
    # Check if at least partial success
    successful = sum(1 for p in placements if p["success"])
    
    if successful > 0:
        print(f"  -> Adaptive logic succeeded: {successful}/{quantity} placed")
        return True
    else:
        print(f"  -> Adaptive logic also failed")
        return False
```

**Acceptance Criteria**:
- ✅ Original logic preserved
- ✅ Fallback triggered on failure
- ✅ No breaking changes
- ✅ Integration tests pass

---

## 💬 **PHASE 3: PROMPT INTEGRATION (Week 3)**

### **Day 1-2: Prompt Classifier Enhancement**

#### **Task 3.1: Create PromptInterpreter class**

**File**: Create `dashboard/prompt_interpreter.py`

**Implementation**: See full code in `MULTI_PLAN_ADAPTIVE_LOGIC_DOCUMENTATION.md` section 3.1

**Key Features**:
- Verb-based logic routing
- Fixture type extraction
- Quantity parsing
- Strategy determination

**Testing**:
```python
# Create: tests/test_prompt_interpreter.py
def test_arrange_prompt():
    interpreter = PromptInterpreter()
    result = interpreter.interpret_prompt("Arrange clinics")
    
    assert result["verb"] == "arrange"
    assert result["action"] == "clear_and_place"
    assert result["preferred_plan"] == "Plan_A"

def test_add_prompt():
    interpreter = PromptInterpreter()
    result = interpreter.interpret_prompt("Add 2 more clinics")
    
    assert result["verb"] == "add"
    assert result["quantities"]["Clinic_regular"] == 2
    assert result["preferred_plan"] == "Plan_B"
```

---

### **Day 3-4: Pipeline Integration**

#### **Task 3.2: Enhance EnhancedAIPipeline**

**File**: `dashboard/enhanced_ai_pipeline.py`

**Action**: Integrate PromptInterpreter

```python
from dashboard.prompt_interpreter import PromptInterpreter

class EnhancedAIPipeline:
    def __init__(self, gemini_api_key: str):
        self.classifier = PromptClassifier()
        self.interpreter = PromptInterpreter()  # NEW
        self.math_model = None
        self.ai_mover = AIFixtureMover(gemini_api_key)
    
    def process_prompt(
        self,
        prompt: str,
        session_data: dict
    ) -> dict:
        """
        [ENHANCED] Main entry point with interpretation
        """
        # Step 1: Classify prompt
        classification = self.classifier.classify(prompt)
        
        # Step 2: Interpret prompt (NEW)
        interpretation = self.interpreter.interpret_prompt(prompt)
        
        print(f"\n📋 PROMPT INTERPRETATION:")
        print(f"   Verb: {interpretation['verb']}")
        print(f"   Action: {interpretation['action']}")
        print(f"   Strategy: {interpretation['strategy']}")
        print(f"   Preferred plan: {interpretation['preferred_plan']}")
        
        # Step 3: Route to appropriate pipeline
        if classification['requires_math_model']:
            return self._process_complex(
                prompt, 
                session_data, 
                classification,
                interpretation  # Pass interpretation
            )
        else:
            return self._process_simple(prompt, session_data)
```

---

### **Day 5: API Integration**

#### **Task 3.3: Update generate_with_ai endpoint**

**File**: `dashboard/api.py`

**Action**: Use enhanced pipeline

```python
@dashboard_api.post("/generate_with_ai")
def generate_with_ai(request, data: AiGenerateSchema):
    """
    [ENHANCED] AI generation with multi-plan adaptive logic
    """
    session_data = utils.load_session(data.session_id)
    if not session_data:
        return {"error": "Invalid session"}, 404
    
    # Initialize enhanced pipeline
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    pipeline = EnhancedAIPipeline(GEMINI_API_KEY)
    
    # Process prompt (now includes interpretation)
    result = pipeline.process_prompt(data.prompt, session_data)
    
    if result.get('error'):
        return {"success": False, "error": result['error']}, 400
    
    # Log plan usage for analytics
    plan_used = result.get('plan_category', 'Unknown')
    logger.info(f"Placement used {plan_used} for prompt: {data.prompt}")
    
    # Apply modifications to DXF
    output_path = utils.apply_modifications_to_dxf(
        session_data['original_dxf'],
        result['fixtures'],
        data.session_id
    )
    
    # Update session
    session_data['ai_output_path'] = output_path
    session_data['modifications'].append({
        "prompt": data.prompt,
        "plan_used": plan_used,
        "fixtures_modified": len(result['fixtures']),
        "timestamp": datetime.now().isoformat()
    })
    utils.save_session(data.session_id, session_data)
    
    return {
        'success': True,
        'operation_type': result.get('operation_type'),
        'plan_used': plan_used,
        'fixtures_modified': len(result['fixtures']),
        'download_url': f'/api/dashboard/download/{data.session_id}'
    }
```

---

## 🧪 **PHASE 4: TESTING & REFINEMENT (Week 4)**

### **Day 1-2: Comprehensive Testing**

#### **Task 4.1: Integration tests**

**File**: Create `tests/test_integration_multiplan.py`

```python
import pytest
from app.DXF_Controller import DXF_Controller
from dashboard.enhanced_ai_pipeline import EnhancedAIPipeline

class TestMultiPlanIntegration:
    
    @pytest.fixture
    def setup_controller(self):
        return DXF_Controller("test_assets/test_floor.dxf", {})
    
    def test_end_to_end_arrange_clinics(self, setup_controller):
        """Test complete flow: prompt → placement → DXF update"""
        dxfc = setup_controller
        prompt = "Arrange clinics"
        
        # Execute through pipeline
        pipeline = EnhancedAIPipeline(API_KEY)
        result = pipeline.process_prompt(prompt, session_data)
        
        # Verify results
        assert result['success'] == True
        assert len(result['fixtures']) >= 1
        assert result['plan_used'] in ['Plan_A', 'Plan_B', 'Plan_C']
    
    def test_fallback_cascade(self, setup_controller):
        """Test that fallback works when Plan A fails"""
        # Create constrained scenario
        # Verify Plan B or C is used
        pass
    
    def test_multiple_prompts_sequence(self, setup_controller):
        """Test sequential prompts maintain state"""
        prompts = [
            "Arrange clinics",
            "Add 1 more clinic",
            "Move clinic_1 left by 500mm"
        ]
        # Execute all, verify state consistency
        pass
```

#### **Task 4.2: Performance benchmarking**

**File**: Create `tests/benchmark_multiplan.py`

```python
import time
from app.DXF_Controller import DXF_Controller

def benchmark_intelligent_placement():
    """Measure performance of adaptive logic"""
    
    dxfc = DXF_Controller("test_floor.dxf", {})
    doc = dxfc.docs[0]
    free_area = dxfc.calculate_free_area(doc)
    
    start = time.time()
    placements = dxfc.intelligent_place_clinic(
        doc, free_area, "clinic", quantity=5
    )
    end = time.time()
    
    print(f"Time for 5 placements: {end - start:.2f}s")
    print(f"Average per placement: {(end - start) / 5:.2f}s")
    
    # Target: < 1s per placement
    assert (end - start) / 5 < 1.0

def benchmark_vs_original():
    """Compare adaptive logic vs original"""
    # Run both approaches, compare time and success rate
    pass
```

**Acceptance Criteria**:
- ✅ Average placement time < 1s
- ✅ Success rate > 90%
- ✅ Memory usage acceptable
- ✅ No memory leaks

---

### **Day 3-4: User Acceptance Testing**

#### **Task 4.3: Create UAT test suite**

**Test Scenarios**:

1. **Simple Prompts** (should use direct AI, not adaptive logic)
   - "Move clinic_1 left by 500mm"
   - "Rotate Euro_centre 90 degrees"
   
2. **Complex Prompts** (should use adaptive logic)
   - "Arrange clinics"
   - "Add 2 more clinics"
   - "Rearrange back of house"
   - "Optimize floor fixtures"
   
3. **Edge Cases**
   - Very constrained spaces
   - Empty floor plans
   - Maximum fixture counts
   - Conflicting prompts

4. **Error Handling**
   - Invalid prompts
   - Impossible placements
   - Corrupted DXF files

#### **Task 4.4: Bug fixes and refinements**

Based on UAT results:
- Fix any edge case failures
- Improve error messages
- Optimize performance bottlenecks
- Enhance logging

---

### **Day 5: Documentation & Deployment**

#### **Task 4.5: Finalize documentation**

**Documents to create/update**:
1. `CHANGELOG.md` - Document all changes
2. `API_DOCUMENTATION.md` - Updated endpoint specs
3. `USER_GUIDE.md` - How to use new features
4. `DEVELOPER_GUIDE.md` - Architecture and extension points
5. `TROUBLESHOOTING.md` - Common issues and solutions

#### **Task 4.6: Deployment preparation**

**Checklist**:
- [ ] All tests passing
- [ ] Performance benchmarks met
- [ ] Documentation complete
- [ ] Code reviewed and approved
- [ ] Backwards compatibility verified
- [ ] Migration plan prepared
- [ ] Rollback procedure documented

---

## 📈 **SUCCESS METRICS**

### **Quantitative Metrics**

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Placement Success Rate | > 90% | Automated tests |
| Average Placement Time | < 1s | Performance benchmarks |
| Fallback Usage Rate | 20-40% | Analytics logging |
| API Response Time | < 3s | Endpoint monitoring |
| Test Coverage | > 85% | pytest-cov |
| Code Quality Score | > 8.0/10 | pylint |

### **Qualitative Metrics**

- User satisfaction (survey)
- Reduction in support tickets
- Developer experience feedback
- System stability (crash rate)

---

## 🚨 **RISK MANAGEMENT**

### **Identified Risks**

| Risk | Probability | Impact | Mitigation |
|------|------------|---------|------------|
| Performance degradation | Medium | High | Benchmarking, optimization |
| Breaking existing features | Low | Critical | Extensive testing, feature flags |
| User confusion | Medium | Medium | Clear documentation, training |
| Edge case failures | High | Medium | Comprehensive test suite |
| API changes | Low | High | Versioning, deprecation plan |

### **Contingency Plans**

1. **Performance Issues**: 
   - Implement caching for frequent calculations
   - Add async processing for large operations
   - Provide "quick mode" with simpler logic

2. **Breaking Changes**:
   - Feature flag to disable new logic
   - Provide compatibility mode
   - Gradual rollout to subset of users

3. **Production Bugs**:
   - Hot-fix process defined
   - Rollback procedure tested
   - Monitoring and alerting configured

---

## 📞 **SUPPORT & RESOURCES**

### **Team Contacts**

- **Technical Lead**: [Name] - Architecture decisions
- **Backend Developer**: [Name] - DXF_Controller modifications
- **Frontend Developer**: [Name] - API integration
- **QA Engineer**: [Name] - Testing coordination
- **DevOps**: [Name] - Deployment support

### **Resources**

- **Slack Channel**: #lenskart-multiplan-logic
- **Wiki**: https://wiki.internal/lenskart/multiplan
- **Issue Tracker**: JIRA Project LKT-MULTIPLAN
- **Code Repository**: feature/multiplan-adaptive-logic branch

### **Weekly Meetings**

- **Monday 10 AM**: Sprint planning
- **Wednesday 3 PM**: Technical sync
- **Friday 4 PM**: Demo & retrospective

---

## ✅ **FINAL CHECKLIST**

Before marking implementation complete:

### **Code**
- [ ] All functions implemented
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Performance benchmarks met
- [ ] Code reviewed and approved
- [ ] No linting errors
- [ ] No security vulnerabilities

### **Documentation**
- [ ] README updated
- [ ] API docs updated
- [ ] Developer guide complete
- [ ] User guide complete
- [ ] Troubleshooting guide ready
- [ ] CHANGELOG updated

### **Testing**
- [ ] Unit tests: 100+ tests, >85% coverage
- [ ] Integration tests: 20+ scenarios
- [ ] Performance tests: Benchmarks met
- [ ] UAT: 10+ user scenarios
- [ ] Edge case tests: 15+ cases

### **Deployment**
- [ ] Feature flag configured
- [ ] Monitoring set up
- [ ] Alerts configured
- [ ] Rollback tested
- [ ] Migration script ready
- [ ] Deployment plan approved

---

**Implementation Start Date**: [To be determined]  
**Target Completion Date**: [4 weeks from start]  
**Next Review Date**: [End of Phase 1]

---

**This implementation plan is a living document and will be updated as the project progresses.**

