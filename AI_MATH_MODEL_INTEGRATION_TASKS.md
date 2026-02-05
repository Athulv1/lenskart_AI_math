# 🚀 AI + Mathematical Model Integration - Detailed Task Breakdown

**Project:** Lenskart Floor Planning System - AI Integration  
**Version:** 2.0  
**Date:** January 22, 2026  
**Total Duration:** 4 weeks (134 hours)

---

## 📊 SPRINT 1: Mathematical Model Enhancement (Week 1)

### Week 1 - JSON Export Foundation & DXF_Controller Analysis

| Task ID | Task | Activities | Notes/Challenges | Dev Time (hours) | Sprint |
|---------|------|------------|------------------|------------------|--------|
| **T1.1** | **Study DXF_Controller architecture** | • Read `app/DXF_Controller.py` structure (first 500 lines)<br>• Understand class initialization<br>• Map out key instance variables<br>• Document fixture_dict structure<br>• Find clinic_ranked_plan storage location | **Challenge:** 19,537 lines to navigate<br>**Tools:** VS Code search, grep<br>**Output:** Architecture diagram | 3 hours | Sprint 1 |
| **T1.2** | **Locate clinic plan storage** | • Search for `clinic_ranked_plan` in codebase<br>• Find where plans are generated (around line 4000-4500)<br>• Understand plan dictionary structure<br>• Document keys: Rank, Placed, score, fixtures, coordinates<br>• Create sample plan dict for reference | **Challenge:** Complex nested structures<br>**Output:** Data structure documentation | 2 hours | Sprint 1 |
| **T1.3** | **Locate euro plan generation** | • Search for euro strategy methods<br>• Find: basic_qms, lane_strategy, v1_og, v2_og<br>• Understand how each strategy is calculated<br>• Document strategy differences<br>• Find capacity calculation logic | **Challenge:** Multiple strategy types<br>**Output:** Euro strategy documentation | 3 hours | Sprint 1 |
| **T1.4** | **Design JSON schema** | • Create `schemas/plans_schema.json` file<br>• Define top-level structure (floorplan_id, timestamp)<br>• Define clinic_plans structure<br>• Define euro_plans nested structure<br>• Add validation rules<br>• Include example with annotations | **Challenge:** Capture all necessary data<br>**Output:** JSON schema v1.0 | 2 hours | Sprint 1 |
| **T1.5** | **Test JSON schema with sample data** | • Create sample plan data manually<br>• Validate against schema<br>• Test with JSON validator tools<br>• Adjust schema based on findings<br>• Document schema decisions | **Challenge:** Edge cases<br>**Output:** Validated schema | 1 hour | Sprint 1 |
| **T1.6** | **Implement coordinate extraction helper** | • Create `_extract_clinic_coordinates()` method<br>• Extract: name, target_center, mirror_scale<br>• Extract: zone_id, orientation, rotation<br>• Handle Vec2 to list conversion<br>• Add error handling for missing data | **Challenge:** Type conversions (Vec2 → list)<br>**Output:** Helper function | 3 hours | Sprint 1 |
| **T1.7** | **Test coordinate extraction** | • Unit test with sample clinic<br>• Test with different orientations (H/V)<br>• Test with different mirror scales<br>• Verify all coordinates captured<br>• Fix any conversion bugs | **Challenge:** Coordinate accuracy<br>**Output:** Passing tests | 2 hours | Sprint 1 |
| **T1.8** | **Find euro strategy 1: basic_qms** | • Search for basic_qms implementation<br>• Understand placement logic<br>• Find capacity calculation<br>• Document coordinate format<br>• Test extraction with sample | **Challenge:** Understanding strategy logic<br>**Output:** Strategy 1 documented | 2 hours | Sprint 1 |
| **T1.9** | **Find euro strategy 2: lane_strategy** | • Search for lane_strategy implementation<br>• Understand placement logic<br>• Find capacity calculation<br>• Document coordinate format<br>• Test extraction with sample | **Challenge:** Different from basic_qms<br>**Output:** Strategy 2 documented | 2 hours | Sprint 1 |
| **T1.10** | **Find euro strategy 3: v1_og_rotated** | • Search for v1_og implementation<br>• Understand rotation logic<br>• Find capacity calculation<br>• Document coordinate format<br>• Test extraction with sample | **Challenge:** Rotation handling<br>**Output:** Strategy 3 documented | 2 hours | Sprint 1 |
| **T1.11** | **Find euro strategy 4: v2_og_non_rotated** | • Search for v2_og implementation<br>• Understand non-rotated placement<br>• Find capacity calculation<br>• Document coordinate format<br>• Test extraction with sample | **Challenge:** Non-rotated specifics<br>**Output:** Strategy 4 documented | 2 hours | Sprint 1 |
| **T1.12** | **Implement euro plan generator helper** | • Create `_generate_euro_plan()` method<br>• Accept clinic_plan and strategy_num as params<br>• Call appropriate strategy method<br>• Extract coordinates from result<br>• Calculate max_capacity<br>• Return formatted dict | **Challenge:** Calling existing strategy methods<br>**Output:** Euro generator function | 4 hours | Sprint 1 |
| **T1.13** | **Test euro plan generator** | • Test with strategy_num=1 (basic_qms)<br>• Test with strategy_num=2 (lane_strategy)<br>• Test with strategy_num=3 (v1_og_rotated)<br>• Test with strategy_num=4 (v2_og_non_rotated)<br>• Verify all coordinates captured<br>• Verify capacity calculations correct | **Challenge:** Strategy-specific validation<br>**Output:** 4 passing tests | 3 hours | Sprint 1 |
| **T1.14** | **Implement main JSON save function** | • Create `save_all_plans_to_json()` method<br>• Get all_clinic_plans from cache<br>• Loop through each clinic plan<br>• Call euro generator 4 times per plan<br>• Build complete JSON structure<br>• Handle errors gracefully | **Challenge:** Large data structures<br>**Output:** Save function | 4 hours | Sprint 1 |
| **T1.15** | **Add file writing logic** | • Determine output path (same dir as DXF)<br>• Create filename: `{dxf_name}_plans.json`<br>• Write JSON with pretty formatting (indent=2)<br>• Add timestamp metadata<br>• Add error handling for file I/O<br>• Log success/failure | **Challenge:** File permissions<br>**Output:** File write logic | 2 hours | Sprint 1 |
| **T1.16** | **Test JSON generation end-to-end** | • Use a small test floor plan<br>• Run Mathematical Model<br>• Verify JSON file created<br>• Verify JSON is valid<br>• Verify all clinic plans captured<br>• Verify all 4 euro strategies per plan<br>• Check file size reasonable | **Challenge:** Full pipeline test<br>**Output:** Working JSON generation | 3 hours | Sprint 1 |
| **T1.17** | **Find DXF generation completion point** | • Search for where DXF is saved<br>• Find main orchestration method<br>• Identify right place to call JSON save<br>• Ensure it runs AFTER all placements<br>• Document the call location | **Challenge:** Right execution point<br>**Output:** Integration point identified | 2 hours | Sprint 1 |
| **T1.18** | **Integrate JSON save into pipeline** | • Add call to `save_all_plans_to_json()`<br>• Pass correct parameters<br>• Add try-catch error handling<br>• Log integration success<br>• Don't break existing DXF generation | **Challenge:** Don't break existing flow<br>**Output:** Integrated call | 2 hours | Sprint 1 |
| **T1.19** | **Test with 3 different floor plans** | • Test 1: Small store (30 sqm)<br>• Test 2: Medium store (45 sqm)<br>• Test 3: Large store (60 sqm)<br>• Verify JSON created for each<br>• Verify different plan counts (may vary)<br>• Check JSON validity | **Challenge:** Different plan counts<br>**Output:** 3 successful tests | 2 hours | Sprint 1 |
| **T1.20** | **Handle edge cases** | • Test with 0 clinic plans (should error)<br>• Test with 1 clinic plan only<br>• Test with >10 clinic plans<br>• Add validation for minimum data<br>• Add warnings for unusual cases | **Challenge:** Edge case handling<br>**Output:** Robust error handling | 2 hours | Sprint 1 |
| **T1.21** | **Sprint 1 review and documentation** | • Review all code changes<br>• Update inline comments<br>• Create schema documentation file<br>• Document JSON format for developers<br>• Create example JSON files<br>• Git commit with clear message | **Challenge:** Complete documentation<br>**Output:** Sprint 1 complete | 2 hours | Sprint 1 |

**Sprint 1 Total: 50 hours** (Week 1 + spillover)

---

## 🤖 SPRINT 2: AI Components Foundation (Week 2)

### Week 2 - Classifier, Handler, Validator, Executor

| Task ID | Task | Activities | Notes/Challenges | Dev Time (hours) | Sprint |
|---------|------|------------|------------------|------------------|--------|
| **T2.1** | **Create prompt_classifier.py skeleton** | • Create file `dashboard/prompt_classifier.py`<br>• Add imports (re, typing)<br>• Create `PromptClassifier` class<br>• Add docstrings<br>• Define class structure | **Challenge:** None<br>**Output:** File skeleton | 0.5 hours | Sprint 2 |
| **T2.2** | **Define classification keywords** | • Define SIMPLE_KEYWORDS list<br>  - move, shift, drag, rotate, by, mm, left, right<br>• Define COMPLEX_KEYWORDS list<br>  - rearrange, optimize, add, remove, all<br>• Define fixture type keywords<br>• Document keyword rationale | **Challenge:** Comprehensive coverage<br>**Output:** Keyword lists | 1 hour | Sprint 2 |
| **T2.3** | **Define classification regex patterns** | • Define SIMPLE_PATTERNS (regex)<br>  - "move \w+ left by \d+"<br>• Define COMPLEX_PATTERNS (regex)<br>  - "rearrange (boh|clinic)"<br>• Test regex patterns individually<br>• Document pattern examples | **Challenge:** Regex accuracy<br>**Output:** Pattern lists | 1.5 hours | Sprint 2 |
| **T2.4** | **Implement classify() method** | • Accept prompt string parameter<br>• Convert to lowercase<br>• Check simple patterns first<br>• Check complex patterns<br>• Calculate confidence score<br>• Extract intent (move/rearrange/add/remove)<br>• Return classification dict | **Challenge:** Confidence calculation<br>**Output:** Classify method | 2 hours | Sprint 2 |
| **T2.5** | **Implement confidence scoring** | • Count keyword matches<br>• Weight pattern matches higher<br>• Check for ambiguity indicators<br>• Return 0.0-1.0 score<br>• Add threshold logic (0.7 = complex) | **Challenge:** Balanced scoring<br>**Output:** Scoring logic | 1.5 hours | Sprint 2 |
| **T2.6** | **Create classifier test file** | • Create `tests/test_prompt_classifier.py`<br>• Import pytest<br>• Create test fixture<br>• Define 10 simple test cases<br>• Define 10 complex test cases<br>• Add edge cases (empty, gibberish) | **Challenge:** Comprehensive tests<br>**Output:** Test file with 20+ cases | 2 hours | Sprint 2 |
| **T2.7** | **Run and fix classifier tests** | • Run pytest<br>• Fix failing simple classifications<br>• Fix failing complex classifications<br>• Adjust keywords/patterns as needed<br>• Aim for 90%+ accuracy<br>• Document any known limitations | **Challenge:** Achieve 90%+ accuracy<br>**Output:** Passing tests | 2 hours | Sprint 2 |
| **T2.8** | **Create plans_validator.py skeleton** | • Create file `dashboard/plans_validator.py`<br>• Add imports (shapely, ezdxf)<br>• Create `PlansValidator` class<br>• Add docstrings<br>• Define class structure | **Challenge:** None<br>**Output:** File skeleton | 0.5 hours | Sprint 2 |
| **T2.9** | **Implement boundary validation** | • Create `_check_boundaries()` method<br>• Accept fixture bbox and floor polygon<br>• Use shapely.contains()<br>• Return True/False + error message<br>• Test with sample fixtures | **Challenge:** Shapely polygon creation<br>**Output:** Boundary check | 2 hours | Sprint 2 |
| **T2.10** | **Implement collision detection** | • Create `_check_collisions()` method<br>• Accept new fixture bbox<br>• Accept list of existing bboxes<br>• Use shapely.intersects()<br>• Return True/False + colliding fixture<br>• Test with overlapping fixtures | **Challenge:** Accurate intersection<br>**Output:** Collision check | 2 hours | Sprint 2 |
| **T2.11** | **Implement spacing validation** | • Create `_check_spacing()` method<br>• Accept fixture bbox and existing bboxes<br>• Calculate minimum distance<br>• Compare to MIN_SPACING (800mm)<br>• Return True/False + closest distance<br>• Test with various distances | **Challenge:** Distance calculation<br>**Output:** Spacing check | 2 hours | Sprint 2 |
| **T2.12** | **Implement main validate_clinic_plan()** | • Accept clinic_plan dict<br>• Accept floor boundaries<br>• Accept existing fixtures<br>• Loop through all coordinates<br>• Call boundary/collision/spacing checks<br>• Return validation result dict<br>• Include all error details | **Challenge:** Comprehensive validation<br>**Output:** Main validator | 2 hours | Sprint 2 |
| **T2.13** | **Test validator with valid plans** | • Create test DXF with valid plan<br>• Run validator<br>• Should return True<br>• Test with 3 different valid plans<br>• Verify no false negatives | **Challenge:** Test data creation<br>**Output:** Passing validation tests | 1.5 hours | Sprint 2 |
| **T2.14** | **Test validator with invalid plans** | • Test with out-of-bounds fixture<br>• Test with overlapping fixtures<br>• Test with insufficient spacing<br>• Should return False with details<br>• Verify no false positives | **Challenge:** Creating invalid cases<br>**Output:** Rejection tests passing | 1.5 hours | Sprint 2 |
| **T2.15** | **Study DXF_Controller's place methods** | • Read `place_clinics_from_ranked_plan()`<br>• Read `place_fixtures_from_plan()`<br>• Document method signatures<br>• Document required parameters<br>• Understand return values | **Challenge:** Complex method logic<br>**Output:** Method documentation | 3 hours | Sprint 2 |
| **T2.16** | **Create placement_executor.py skeleton** | • Create file `dashboard/placement_executor.py`<br>• Import DXF_Controller<br>• Import Fixture, ezdxf<br>• Create `PlacementExecutor` class<br>• Add __init__ with dxf_path param | **Challenge:** Import paths<br>**Output:** File skeleton | 0.5 hours | Sprint 2 |
| **T2.17** | **Implement DXF_Controller initialization** | • In __init__, create DXF_Controller instance<br>• Pass dxf_path, merch_mix, boundary_threshold<br>• Store controller in self.controller<br>• Get doc reference: self.doc<br>• Add error handling for init failure | **Challenge:** Correct initialization params<br>**Output:** Controller initialized | 2 hours | Sprint 2 |
| **T2.18** | **Implement remove_fixtures_by_type()** | • Create method with fixture_type param<br>• Define type patterns dict (clinic/euro/boh/wall)<br>• Query modelspace for INSERT entities<br>• Match block names to patterns<br>• Delete matched entities<br>• Log removal count | **Challenge:** Pattern matching<br>**Output:** Removal method | 2 hours | Sprint 2 |
| **T2.19** | **Test fixture removal** | • Create test DXF with various fixtures<br>• Test remove clinics<br>• Test remove euros<br>• Test remove BOH<br>• Verify correct fixtures removed<br>• Verify other fixtures untouched | **Challenge:** Selective removal<br>**Output:** Removal tests passing | 1.5 hours | Sprint 2 |
| **T2.20** | **Implement execute_clinic_plan()** | • Accept clinic_plan dict parameter<br>• Call remove_fixtures_by_type("clinic")<br>• Call controller.place_clinics_from_ranked_plan()<br>• Pass required parameters correctly<br>• Return success boolean<br>• Add error handling and logging | **Challenge:** Correct parameter passing<br>**Output:** Clinic execution method | 3 hours | Sprint 2 |
| **T2.21** | **Find euro placement methods** | • Search DXF_Controller for euro methods<br>• Likely: `plan_and_place_euro_fixtures()`<br>• Document method signature<br>• Document required parameters<br>• Test calling method manually | **Challenge:** Finding right method<br>**Output:** Euro method identified | 2 hours | Sprint 2 |
| **T2.22** | **Implement execute_euro_plan()** | • Accept euro_plan dict parameter<br>• Call remove_fixtures_by_type("euro")<br>• Convert euro_plan to controller format<br>• Call controller's euro placement method<br>• Return success boolean<br>• Add error handling and logging | **Challenge:** Format conversion<br>**Output:** Euro execution method | 3 hours | Sprint 2 |
| **T2.23** | **Implement save() method** | • Accept optional output_path<br>• Default: {dxf_name}_modified.dxf<br>• Call controller.docs[0].doc.saveas()<br>• Verify file created<br>• Return output path<br>• Add error handling | **Challenge:** File path handling<br>**Output:** Save method | 1 hour | Sprint 2 |
| **T2.24** | **Test PlacementExecutor end-to-end** | • Create test DXF with sample plan JSON<br>• Initialize PlacementExecutor<br>• Execute clinic plan<br>• Execute euro plan<br>• Save output<br>• Verify output DXF valid<br>• Verify fixtures placed correctly | **Challenge:** Full integration test<br>**Output:** E2E test passing | 3 hours | Sprint 2 |
| **T2.25** | **Create complex_prompt_handler.py** | • Create file `dashboard/complex_prompt_handler.py`<br>• Import validator, executor<br>• Create `ComplexPromptHandler` class<br>• Add __init__ with plans_json param<br>• Load and parse plans JSON | **Challenge:** None<br>**Output:** File skeleton | 1 hour | Sprint 2 |
| **T2.26** | **Implement handle_rearrange_boh()** | • Accept prompt parameter<br>• Load current plan state from session<br>• Start checking from plan_3 onwards<br>• Validate each plan with validator<br>• Select first valid plan<br>• Select best euro strategy (highest capacity)<br>• Return result dict | **Challenge:** Plan selection logic<br>**Output:** BOH handler | 3 hours | Sprint 2 |
| **T2.27** | **Implement handle_euro_adjustment()** | • Accept prompt and count_change params<br>• Parse: add/remove X euros<br>• Calculate new required capacity<br>• Check current euro plan capacity<br>• If insufficient, find plan with higher capacity<br>• Return result dict | **Challenge:** Capacity logic<br>**Output:** Euro adjustment handler | 3 hours | Sprint 2 |
| **T2.28** | **Implement handle_rearrange_euros()** | • Load current euro plan<br>• Get unused euro strategies<br>• Select highest capacity unused strategy<br>• Return result dict<br>• Handle case of no unused strategies | **Challenge:** Strategy selection<br>**Output:** Euro rearrange handler | 2 hours | Sprint 2 |
| **T2.29** | **Test ComplexPromptHandler** | • Test handle_rearrange_boh()<br>• Test handle_euro_adjustment() (add)<br>• Test handle_euro_adjustment() (remove)<br>• Test handle_rearrange_euros()<br>• Verify correct plan selection<br>• Verify error handling | **Challenge:** Multiple scenarios<br>**Output:** Handler tests passing | 2 hours | Sprint 2 |
| **T2.30** | **Sprint 2 review and documentation** | • Review all new modules<br>• Update docstrings<br>• Create API documentation<br>• Document class interactions<br>• Create usage examples<br>• Git commit | **Challenge:** Complete docs<br>**Output:** Sprint 2 complete | 2 hours | Sprint 2 |

**Sprint 2 Total: 56 hours** (Week 2 + spillover)

---

## 🔗 SPRINT 3: Integration & Workflow (Week 3)

### Week 3 - Connect AI Dashboard with New Components

| Task ID | Task | Activities | Notes/Challenges | Dev Time (hours) | Sprint |
|---------|------|------------|------------------|------------------|--------|
| **T3.1** | **Study current dashboard/api.py** | • Read existing `/upload` endpoint<br>• Read existing `/generate_with_ai` endpoint<br>• Understand current session flow<br>• Document current data structures<br>• Identify integration points | **Challenge:** Understanding current code<br>**Output:** Integration plan | 2 hours | Sprint 3 |
| **T3.2** | **Modify upload endpoint - Add plans JSON check** | • In `/upload` endpoint<br>• After DXF upload, check for `_plans.json`<br>• If exists, load plans JSON<br>• Validate JSON structure<br>• Store in session_data["plans_json"] | **Challenge:** File existence check<br>**Output:** Enhanced upload | 1.5 hours | Sprint 3 |
| **T3.3** | **Test upload with plans JSON** | • Upload DXF WITH plans JSON<br>• Verify JSON loaded<br>• Verify stored in session<br>• Upload DXF WITHOUT plans JSON<br>• Verify graceful handling (no error) | **Challenge:** Both scenarios<br>**Output:** Upload tests passing | 1 hour | Sprint 3 |
| **T3.4** | **Backup current generate_with_ai** | • Copy current implementation<br>• Save as `generate_with_ai_simple_only()`<br>• Keep as fallback<br>• Document reason for backup | **Challenge:** None<br>**Output:** Backup created | 0.5 hours | Sprint 3 |
| **T3.5** | **Add prompt classification to generate_with_ai** | • Import PromptClassifier<br>• At start of endpoint, classify prompt<br>• Log classification result<br>• Store in local variable<br>• Don't change flow yet | **Challenge:** None<br>**Output:** Classification added | 1 hour | Sprint 3 |
| **T3.6** | **Test classification in endpoint** | • Send simple prompt, verify classified as simple<br>• Send complex prompt, verify classified as complex<br>• Check logs for classification results<br>• Verify no errors | **Challenge:** None<br>**Output:** Classification working | 0.5 hours | Sprint 3 |
| **T3.7** | **Implement simple branch (keep existing logic)** | • If classification["type"] == "simple"<br>• Call existing AI logic (unchanged)<br>• Return existing response format<br>• Log: "Using simple AI path" | **Challenge:** None - preserve existing<br>**Output:** Simple branch | 1 hour | Sprint 3 |
| **T3.8** | **Test simple operations still work** | • Test "move left 500mm"<br>• Test "rotate 90 degrees"<br>• Test drag-and-drop<br>• Verify no regression<br>• Verify performance unchanged | **Challenge:** No regressions<br>**Output:** Simple ops working | 1 hour | Sprint 3 |
| **T3.9** | **Implement complex branch skeleton** | • If classification["type"] == "complex"<br>• Check if plans_json exists<br>• If not, return error: "Complex operations require Mathematical Model plans"<br>• Log: "Using complex path" | **Challenge:** Error handling<br>**Output:** Complex branch skeleton | 1 hour | Sprint 3 |
| **T3.10** | **Load plans JSON in complex branch** | • Get plans_json from session_data<br>• If missing, return helpful error<br>• Parse JSON<br>• Validate structure<br>• Log plan counts | **Challenge:** Validation<br>**Output:** Plans loaded | 1 hour | Sprint 3 |
| **T3.11** | **Initialize ComplexPromptHandler** | • Import ComplexPromptHandler<br>• Create instance with plans_json<br>• Add error handling for init failure<br>• Log handler initialized | **Challenge:** Import paths<br>**Output:** Handler initialized | 0.5 hours | Sprint 3 |
| **T3.12** | **Route to appropriate handler method** | • Check classification["intent"]<br>• If "rearrange_boh" → handle_rearrange_boh()<br>• If "adjust_euro_count" → handle_euro_adjustment()<br>• If "rearrange_euros" → handle_rearrange_euros()<br>• Else → return "Intent not supported yet" | **Challenge:** Intent routing<br>**Output:** Handler routing | 1.5 hours | Sprint 3 |
| **T3.13** | **Handle handler result** | • Get result dict from handler<br>• Check result["success"]<br>• If False, return error to user<br>• If True, extract clinic_plan_id and euro_plan_id<br>• Log selected plan IDs | **Challenge:** Error propagation<br>**Output:** Result handling | 1 hour | Sprint 3 |
| **T3.14** | **Initialize PlacementExecutor** | • Import PlacementExecutor<br>• Create instance with dxf_path and session_data<br>• Add error handling for init failure<br>• Log executor initialized | **Challenge:** Correct params<br>**Output:** Executor initialized | 1 hour | Sprint 3 |
| **T3.15** | **Execute clinic plan placement** | • Get clinic_plan from plans_json<br>• Call executor.execute_clinic_plan()<br>• Check return value<br>• If False, return error<br>• Log placement success | **Challenge:** Error handling<br>**Output:** Clinic placement | 1.5 hours | Sprint 3 |
| **T3.16** | **Execute euro plan placement** | • Get euro_plan from clinic_plan<br>• Call executor.execute_euro_plan()<br>• Check return value<br>• If False, return error<br>• Log placement success | **Challenge:** Nested plan access<br>**Output:** Euro placement | 1.5 hours | Sprint 3 |
| **T3.17** | **Save modified DXF** | • Call executor.save()<br>• Get output_path<br>• Verify file created<br>• Log save location | **Challenge:** File permissions<br>**Output:** DXF saved | 0.5 hours | Sprint 3 |
| **T3.18** | **Update session state** | • Mark selected plan as placed=true<br>• Mark selected euro plan as placed=true<br>• Update session_data["plans_json"]<br>• Save session<br>• Log state update | **Challenge:** State consistency<br>**Output:** State updated | 1.5 hours | Sprint 3 |
| **T3.19** | **Create success response** | • Build response dict:<br>  - success: true<br>  - operation_type: "complex"<br>  - method: "math_model"<br>  - fixtures_modified: count<br>  - download_url: output_path<br>  - message: "Rearranged using plan X" | **Challenge:** User-friendly message<br>**Output:** Response format | 1 hour | Sprint 3 |
| **T3.20** | **Test complex operation: Rearrange BOH** | • Upload DXF with plans JSON<br>• Send prompt: "Rearrange back of house"<br>• Verify classified as complex<br>• Verify handler called<br>• Verify executor called<br>• Verify DXF modified<br>• Download and open in AutoCAD | **Challenge:** Full integration test<br>**Output:** BOH test passing | 2 hours | Sprint 3 |
| **T3.21** | **Test complex operation: Add euros** | • Send prompt: "Add 2 more euro centers"<br>• Verify capacity check<br>• Verify strategy switch if needed<br>• Verify euros placed<br>• Verify output DXF valid | **Challenge:** Capacity logic<br>**Output:** Add euros test passing | 1.5 hours | Sprint 3 |
| **T3.22** | **Test complex operation: Remove euros** | • Send prompt: "Remove 1 euro center"<br>• Verify classified correctly<br>• Verify removal<br>• Verify count updated | **Challenge:** Simple vs complex routing<br>**Output:** Remove test passing | 1 hour | Sprint 3 |
| **T3.23** | **Implement comprehensive error handling** | • Try-catch around handler calls<br>• Try-catch around executor calls<br>• Try-catch around file operations<br>• Return user-friendly error messages<br>• Log all errors with stack traces | **Challenge:** All failure points<br>**Output:** Error handling | 2 hours | Sprint 3 |
| **T3.24** | **Test error scenarios** | • Test with missing plans JSON<br>• Test with invalid plans JSON<br>• Test with no valid plans<br>• Test with DXF write failure<br>• Verify graceful error messages | **Challenge:** Simulate failures<br>**Output:** Error tests passing | 2 hours | Sprint 3 |
| **T3.25** | **Add structured logging** | • Log classification result<br>• Log handler selection<br>• Log plan selection<br>• Log validation results<br>• Log placement success<br>• Log timing metrics | **Challenge:** Not too verbose<br>**Output:** Logging added | 1.5 hours | Sprint 3 |
| **T3.26** | **Create log analysis script** | • Create `scripts/analyze_logs.py`<br>• Parse log file<br>• Extract classification accuracy<br>• Extract success/failure rates<br>• Generate summary report | **Challenge:** Log parsing<br>**Output:** Analysis script | 2 hours | Sprint 3 |
| **T3.27** | **Test with real floor plans** | • Test 1: Mumbai store (45 sqm)<br>• Test 2: Bangalore store (60 sqm)<br>• Test 3: Small kiosk (25 sqm)<br>• Verify different scenarios<br>• Document any issues | **Challenge:** Real-world edge cases<br>**Output:** 3 real tests passing | 3 hours | Sprint 3 |
| **T3.28** | **Performance profiling** | • Profile upload with plans JSON<br>• Profile classification (should be <50ms)<br>• Profile validation (should be <100ms)<br>• Profile placement (depends on fixtures)<br>• Identify bottlenecks | **Challenge:** Performance measurement<br>**Output:** Performance report | 2 hours | Sprint 3 |
| **T3.29** | **Optimize if needed** | • Cache plans JSON in memory<br>• Optimize validation loops<br>• Use lazy loading where possible<br>• Aim for <500ms total response time | **Challenge:** Optimization without bugs<br>**Output:** Performance improved | 2 hours | Sprint 3 |
| **T3.30** | **Sprint 3 review and documentation** | • Review all integration code<br>• Update API documentation<br>• Create workflow diagrams<br>• Document error codes<br>• Create troubleshooting guide<br>• Git commit | **Challenge:** Complete docs<br>**Output:** Sprint 3 complete | 2 hours | Sprint 3 |

**Sprint 3 Total: 41 hours** (Week 3)

---

## 🧪 SPRINT 4: Testing & Production Ready (Week 4)

### Week 4 - QA, Performance, Documentation, Deployment

| Task ID | Task | Activities | Notes/Challenges | Dev Time (hours) | Sprint |
|---------|------|------------|------------------|------------------|--------|
| **T4.1** | **Create comprehensive test suite** | • Create `tests/integration/` directory<br>• Create test_boh_rearrange.py<br>• Create test_euro_operations.py<br>• Create test_simple_operations.py<br>• Add pytest fixtures | **Challenge:** Test organization<br>**Output:** Test suite structure | 2 hours | Sprint 4 |
| **T4.2** | **Test scenario 1: BOH rearrange small store** | • Load 30 sqm floor plan<br>• Initial: Plan 1 placed<br>• Prompt: "Rearrange BOH"<br>• Verify: Plan 3 selected<br>• Verify: Clinics moved<br>• Verify: BOH furniture relocated<br>• Verify: Output DXF valid | **Challenge:** Test data setup<br>**Output:** BOH test 1 passing | 2 hours | Sprint 4 |
| **T4.3** | **Test scenario 2: BOH rearrange medium store** | • Load 45 sqm floor plan<br>• Prompt: "Rearrange back of house"<br>• Verify different plan selected<br>• Verify no collisions<br>• Verify spacing maintained | **Challenge:** Different plan count<br>**Output:** BOH test 2 passing | 1.5 hours | Sprint 4 |
| **T4.4** | **Test scenario 3: Add euros within capacity** | • Current: 8 euros (capacity 10)<br>• Prompt: "Add 1 euro center"<br>• Verify: Same plan, count increased<br>• Verify: No rearrangement needed | **Challenge:** Capacity check<br>**Output:** Add euros test 1 passing | 1.5 hours | Sprint 4 |
| **T4.5** | **Test scenario 4: Add euros exceeds capacity** | • Current: 8 euros (capacity 8)<br>• Prompt: "Add 2 euro centers"<br>• Verify: Strategy switched<br>• Verify: New strategy has capacity 10+<br>• Verify: All euros rearranged | **Challenge:** Strategy switching<br>**Output:** Add euros test 2 passing | 2 hours | Sprint 4 |
| **T4.6** | **Test scenario 5: Remove euros** | • Current: 8 euros<br>• Prompt: "Remove 2 euro centers"<br>• Verify: 6 euros remaining<br>• Verify: Correct euros deleted<br>• Verify: Count updated in state | **Challenge:** Which euros to remove<br>**Output:** Remove euros test passing | 1.5 hours | Sprint 4 |
| **T4.7** | **Test scenario 6: Rearrange euros** | • Current: euro_plan_1<br>• Prompt: "Rearrange euro centers"<br>• Verify: Switched to unused plan<br>• Verify: Highest capacity plan selected<br>• Verify: All euros replaced | **Challenge:** Strategy selection<br>**Output:** Rearrange euros test passing | 1.5 hours | Sprint 4 |
| **T4.8** | **Test scenario 7: Invalid request (no plans)** | • Upload DXF WITHOUT plans JSON<br>• Prompt: "Rearrange BOH"<br>• Verify: Error returned<br>• Verify: Helpful message<br>• Verify: Suggestion to use Math Model | **Challenge:** Error message quality<br>**Output:** Error handling test passing | 1 hour | Sprint 4 |
| **T4.9** | **Test scenario 8: No valid plans available** | • All alternative plans already used<br>• Prompt: "Rearrange BOH"<br>• Verify: Error returned<br>• Verify: Message explains why<br>• Verify: Suggestions provided | **Challenge:** Test data setup<br>**Output:** No plans test passing | 1.5 hours | Sprint 4 |
| **T4.10** | **Regression test: Simple move** | • Prompt: "Move clinic_1 left by 500mm"<br>• Verify: Classified as simple<br>• Verify: Uses AI-only path<br>• Verify: Works as before<br>• Verify: Performance unchanged | **Challenge:** No regression<br>**Output:** Simple move test passing | 1 hour | Sprint 4 |
| **T4.11** | **Regression test: Simple rotate** | • Prompt: "Rotate euro_centre 90 degrees"<br>• Verify: Classified as simple<br>• Verify: Rotation correct<br>• Verify: Works as before | **Challenge:** No regression<br>**Output:** Simple rotate test passing | 1 hour | Sprint 4 |
| **T4.12** | **Regression test: Manual drag-drop** | • Use canvas to drag fixture<br>• Verify: Position updated<br>• Verify: No interference with new code<br>• Verify: Works as before | **Challenge:** Canvas testing<br>**Output:** Drag-drop test passing | 1 hour | Sprint 4 |
| **T4.13** | **Load testing: Large JSON files** | • Create test with 15 clinic plans<br>• Each plan has 4 euro strategies<br>• Load 60 plan combinations<br>• Measure load time<br>• Should be <200ms | **Challenge:** Large file handling<br>**Output:** Load test passing | 2 hours | Sprint 4 |
| **T4.14** | **Load testing: Multiple concurrent requests** | • Simulate 5 concurrent users<br>• Each makes complex request<br>• Verify no race conditions<br>• Verify all succeed<br>• Measure response times | **Challenge:** Concurrency issues<br>**Output:** Concurrency test passing | 2 hours | Sprint 4 |
| **T4.15** | **Memory profiling** | • Profile memory usage during operations<br>• Check for memory leaks<br>• Ensure DXF_Controller properly cleaned up<br>• Verify session data not growing<br>• Optimize if needed | **Challenge:** Memory leak detection<br>**Output:** Memory profile report | 2 hours | Sprint 4 |
| **T4.16** | **Optimize JSON loading** | • Implement JSON caching<br>• Cache parsed plans in memory<br>• Invalidate cache on upload<br>• Measure improvement<br>• Target: <100ms load time | **Challenge:** Cache invalidation<br>**Output:** Optimized loading | 2 hours | Sprint 4 |
| **T4.17** | **Optimize validation** | • Profile validation bottlenecks<br>• Optimize shapely operations<br>• Use spatial indexing if needed<br>• Target: <100ms validation time | **Challenge:** Geometric optimization<br>**Output:** Optimized validation | 2 hours | Sprint 4 |
| **T4.18** | **Create API documentation** | • Document all endpoints<br>• Document request/response formats<br>• Add code examples<br>• Document error codes<br>• Add authentication info (if any) | **Challenge:** Complete coverage<br>**Output:** API docs | 3 hours | Sprint 4 |
| **T4.19** | **Create user guide** | • Write "How to use AI features"<br>• Explain simple vs complex operations<br>• Provide example prompts<br>• Add troubleshooting section<br>• Add FAQ | **Challenge:** User-friendly language<br>**Output:** User guide | 3 hours | Sprint 4 |
| **T4.20** | **Create developer guide** | • Explain architecture<br>• Document code structure<br>• Explain how to add new intents<br>• Explain how to modify validation<br>• Add contribution guidelines | **Challenge:** Technical depth<br>**Output:** Developer guide | 3 hours | Sprint 4 |
| **T4.21** | **Create deployment checklist** | • Environment variables needed<br>• Database migrations (if any)<br>• File permissions required<br>• External dependencies<br>• Rollback procedure | **Challenge:** Complete checklist<br>**Output:** Deployment guide | 2 hours | Sprint 4 |
| **T4.22** | **Test on staging environment** | • Deploy to staging server<br>• Test all scenarios<br>• Verify file uploads work<br>• Verify downloads work<br>• Check logs | **Challenge:** Environment differences<br>**Output:** Staging validation | 2 hours | Sprint 4 |
| **T4.23** | **Performance testing on staging** | • Run load tests on staging<br>• Measure response times<br>• Check server resources<br>• Identify any issues<br>• Optimize if needed | **Challenge:** Production-like load<br>**Output:** Performance report | 2 hours | Sprint 4 |
| **T4.24** | **Security review** | • Check file upload validation<br>• Verify no code injection possible<br>• Check path traversal prevention<br>• Verify API authentication<br>• Add rate limiting if needed | **Challenge:** Security vulnerabilities<br>**Output:** Security report | 2 hours | Sprint 4 |
| **T4.25** | **Create monitoring dashboard** | • Add metrics: requests/minute<br>• Add metrics: classification distribution<br>• Add metrics: success/failure rates<br>• Add metrics: response times<br>• Add alerts for failures | **Challenge:** Monitoring setup<br>**Output:** Dashboard | 3 hours | Sprint 4 |
| **T4.26** | **Create rollback plan** | • Document how to rollback<br>• Test rollback procedure<br>• Ensure data compatible<br>• Document when to rollback<br>• Assign rollback owner | **Challenge:** Safe rollback<br>**Output:** Rollback procedure | 1 hour | Sprint 4 |
| **T4.27** | **Final code review** | • Review all code changes<br>• Check code style consistency<br>• Verify all TODOs resolved<br>• Check for hardcoded values<br>• Ensure all tests pass | **Challenge:** Code quality<br>**Output:** Code review complete | 2 hours | Sprint 4 |
| **T4.28** | **User acceptance testing** | • Demo to store planners<br>• Collect feedback<br>• Test with real use cases<br>• Fix critical issues<br>• Document minor issues for future | **Challenge:** User feedback<br>**Output:** UAT report | 3 hours | Sprint 4 |
| **T4.29** | **Final documentation review** | • Review all documentation<br>• Fix typos and errors<br>• Ensure consistency<br>• Add version numbers<br>• Publish documentation | **Challenge:** Documentation quality<br>**Output:** Docs published | 2 hours | Sprint 4 |
| **T4.30** | **Production deployment** | • Schedule deployment window<br>• Run deployment checklist<br>• Deploy to production<br>• Run smoke tests<br>• Monitor for 24 hours<br>• Document deployment | **Challenge:** Zero downtime<br>**Output:** Production live | 3 hours | Sprint 4 |

**Sprint 4 Total: 62 hours** (Week 4 + final push)

---

## 📊 **SUMMARY**

### **Total Task Count:** 101 tasks
### **Total Time:** ~209 hours (~5 weeks for 1 developer, or 4 weeks for 1.5 developers)

### **Sprint Breakdown:**

| Sprint | Tasks | Hours | Focus |
|--------|-------|-------|-------|
| Sprint 1 | 21 tasks | 50 hours | Math Model JSON Export |
| Sprint 2 | 30 tasks | 56 hours | AI Components (Classifier, Validator, Executor, Handler) |
| Sprint 3 | 30 tasks | 41 hours | Integration with Dashboard |
| Sprint 4 | 30 tasks | 62 hours | Testing, Optimization, Deployment |

---

## 🎯 **Critical Path Tasks** (Must not be delayed)

```
T1.2 → T1.6 → T1.12 → T1.14 → T1.18 (Sprint 1 foundation)
   ↓
T2.1 → T2.4 → T2.15 → T2.20 → T2.26 (Sprint 2 components)
   ↓
T3.5 → T3.11 → T3.15 → T3.20 (Sprint 3 integration)
   ↓
T4.2 → T4.20 → T4.30 (Sprint 4 validation & deployment)
```

---

## 📋 **Daily Work Plan Example (Week 1, Day 1)**

### **Monday - Day 1 (8 hours)**

| Time | Task | Description | Hours |
|------|------|-------------|-------|
| 9:00 AM | T1.1 | Study DXF_Controller architecture | 3 |
| 12:00 PM | Lunch | | 1 |
| 1:00 PM | T1.2 | Locate clinic plan storage | 2 |
| 3:00 PM | T1.3 | Locate euro plan generation | 2 |
| 5:00 PM | End of Day | Review and notes | - |

**Deliverable:** Architecture diagram + data structure docs

---

## 🚀 **Quick Start Checklist**

Before starting Sprint 1:
- [ ] Review complete application understanding
- [ ] Set up development environment
- [ ] Create feature branch: `feature/ai-math-integration`
- [ ] Create task tracking board (Jira/Trello/GitHub Projects)
- [ ] Schedule daily standups (15 min)
- [ ] Identify code review partners
- [ ] Set up testing environment

---

This comprehensive task list breaks down the integration into **101 manageable tasks**, each taking **0.5 to 4 hours**, making progress trackable and reducing risk! 🎯
