# 📋 **DETAILED INTEGRATION PLAN: Mathematical Model + AI Pipeline**

---

## 🎯 **OBJECTIVE**

Integrate the **Mathematical Model** (Lenskart_Mathametical_Model) into the current AI pipeline to ensure accurate fixture positioning for complex operations like:
- ✅ **Rearrange entire sections** (BOH, clinic, floor fixtures)
- ✅ **Add new fixtures** (additional clinics, tables, screens)
- ✅ **Remove fixtures**
- ✅ **Complex spatial optimization**

### **Current Problem:**
When AI (Gemini) receives prompts like "rearrange backup house" or "add 2 more clinics", it:
- ❌ Generates positions **outside floor boundaries**
- ❌ Creates **overlapping fixtures**
- ❌ Ignores **spatial constraints** and **design guidelines**

---

## 🏗️ **NEW ARCHITECTURE**

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INPUT (Prompt)                          │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│              PROMPT CLASSIFIER (New Component)                      │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  Analyzes prompt complexity using:                            │ │
│  │  • Keyword detection (move, rotate, rearrange, add, remove)  │ │
│  │  • Intent classification (simple vs complex)                  │ │
│  │  • Fixture count changes                                       │ │
│  └───────────────────────────────────────────────────────────────┘ │
└────────┬─────────────────────────────────────────┬──────────────────┘
         │                                         │
         ▼                                         ▼
┌─────────────────────┐                 ┌─────────────────────────────┐
│  SIMPLE OPERATIONS  │                 │   COMPLEX OPERATIONS        │
│  (Direct AI Path)   │                 │   (Math Model + AI Path)    │
└─────────────────────┘                 └─────────────────────────────┘
         │                                         │
         │                                         │
         │ Examples:                               │ Examples:
         │ • "Move fixture X by 500mm"             │ • "Rearrange BOH"
         │ • "Rotate clinic 90°"                   │ • "Add 2 clinics"
         │ • "Move table left"                     │ • "Optimize layout"
         │                                         │ • "Remove all screens"
         │                                         │
         ▼                                         ▼
┌──────────────────────────────┐      ┌────────────────────────────────┐
│   DIRECT AI PROCESSING       │      │   MATHEMATICAL MODEL ENGINE    │
│   (Current Flow)             │      │   (New Component)              │
│                              │      │                                │
│  1. Parse prompt with Gemini │      │ 1. Load floor plan boundaries │
│  2. Calculate new position   │      │ 2. Get current fixture layout │
│  3. Apply transformation     │      │ 3. Apply design rules:        │
│  4. Update DXF               │      │    • Zoning (premium/clinic)  │
│                              │      │    • Spacing constraints       │
│                              │      │    • ADA compliance            │
│                              │      │    • Collision detection       │
│                              │      │ 4. Calculate optimal positions│
│                              │      │ 5. Generate placement JSON    │
└────────────┬─────────────────┘      └─────────────┬──────────────────┘
             │                                      │
             │                                      │
             │                                      ▼
             │                        ┌──────────────────────────────────┐
             │                        │   AI REFINEMENT (Gemini)         │
             │                        │                                  │
             │                        │ 1. Receive calculated positions  │
             │                        │ 2. Fine-tune with prompt intent  │
             │                        │ 3. Adjust aesthetics             │
             │                        │ 4. Generate final JSON           │
             │                        └─────────────┬────────────────────┘
             │                                      │
             └──────────────────┬───────────────────┘
                                │
                                ▼
                  ┌──────────────────────────────┐
                  │   DXF UPDATE & SAVE          │
                  │                              │
                  │ 1. Apply all transformations │
                  │ 2. Validate fixture positions│
                  │ 3. Save modified DXF         │
                  │ 4. Update canvas preview     │
                  └──────────────────────────────┘
```

---

## 📊 **PROMPT CLASSIFICATION LOGIC**

### **A. Simple Operations (Direct AI)**
```python
SIMPLE_KEYWORDS = [
    "move", "shift", "drag", "relocate",
    "rotate", "turn", "spin",
    "by", "mm", "left", "right", "up", "down"
]

SIMPLE_PATTERNS = [
    r"move .* (left|right|up|down|by)",
    r"rotate .* \d+",
    r"shift .* \d+ ?(mm|cm|m)",
]
```

**Examples:**
- ✅ "Move D-Table-1200 by 1000mm to the right"
- ✅ "Rotate clinic_1 by 90 degrees"
- ✅ "Shift Euro_centre left by 500mm"

### **B. Complex Operations (Math Model + AI)**
```python
COMPLEX_KEYWORDS = [
    "rearrange", "reorganize", "optimize", "layout",
    "add", "insert", "create", "new",
    "remove", "delete", "clear",
    "all", "entire", "whole",
    "boh", "clinic", "fixtures", "section"
]

COMPLEX_PATTERNS = [
    r"(rearrange|reorganize|optimize) .* (boh|clinic|fixtures)",
    r"add \d+ (clinic|table|screen|fixture)",
    r"remove all .*",
]
```

**Examples:**
- ✅ "Rearrange back of house"
- ✅ "Add 2 more clinics"
- ✅ "Optimize floor fixtures layout"
- ✅ "Remove all screens"

---

## 🔧 **IMPLEMENTATION COMPONENTS**

### **1. Prompt Classifier (`dashboard/prompt_classifier.py`)**

```python
class PromptClassifier:
    """Classifies user prompts into simple or complex operations"""
    
    def __init__(self):
        self.simple_keywords = [...]
        self.complex_keywords = [...]
        
    def classify(self, prompt: str) -> dict:
        """
        Returns:
        {
            'operation_type': 'simple' | 'complex',
            'intent': 'move' | 'rotate' | 'rearrange' | 'add' | 'remove',
            'confidence': 0.0-1.0,
            'fixtures_affected': ['fixture_name', ...],
            'requires_math_model': True | False
        }
        """
```

### **2. Math Model Integration (`dashboard/math_model_integration.py`)**

```python
class MathModelIntegration:
    """Integrates Lenskart Mathematical Model for complex operations"""
    
    def __init__(self, dxf_path: str, floor_boundaries: dict):
        self.dxfc = DXF_Controller(...)
        self.boundaries = floor_boundaries
        
    def calculate_positions(
        self,
        operation: str,
        fixtures: dict,
        merch_mix: dict
    ) -> dict:
        """
        Returns calculated positions:
        {
            'fixtures': [
                {
                    'block_name': 'clinic_1',
                    'calculated_position': [x, y],
                    'rotation': 0.0,
                    'zone': 'clinic',
                    'reasoning': 'Positioned per design guidelines'
                }
            ],
            'placement_valid': True,
            'warnings': []
        }
        """
```

### **3. Enhanced AI Pipeline (`dashboard/enhanced_ai_pipeline.py`)**

```python
class EnhancedAIPipeline:
    """Orchestrates the complete prompt → position → DXF flow"""
    
    def __init__(self, gemini_api_key: str):
        self.classifier = PromptClassifier()
        self.math_model = None
        self.ai_mover = AIFixtureMover(gemini_api_key)
        
    def process_prompt(
        self,
        prompt: str,
        session_data: dict
    ) -> dict:
        """
        Main entry point:
        1. Classify prompt
        2. Route to appropriate pipeline
        3. Return results
        """
        
        classification = self.classifier.classify(prompt)
        
        if classification['requires_math_model']:
            return self._process_complex(prompt, session_data, classification)
        else:
            return self._process_simple(prompt, session_data)
            
    def _process_complex(self, prompt, session_data, classification):
        """Complex operations using math model"""
        
        # Step 1: Initialize math model
        math_model = MathModelIntegration(
            session_data['original_dxf'],
            session_data['json_data']['boundaries']
        )
        
        # Step 2: Get calculated positions
        positions = math_model.calculate_positions(
            classification['intent'],
            session_data['json_data']['fixtures'],
            session_data.get('merch_mix', {})
        )
        
        # Step 3: Refine with AI
        refined_positions = self._ai_refine_positions(
            prompt,
            positions,
            session_data
        )
        
        return refined_positions
        
    def _ai_refine_positions(self, prompt, positions, session_data):
        """Use Gemini to refine mathematically calculated positions"""
        
        ai_prompt = f"""
        I have calculated optimal positions for fixtures using mathematical constraints.
        Please refine these positions based on the user's intent.
        
        User request: "{prompt}"
        
        Calculated positions:
        {json.dumps(positions, indent=2)}
        
        Please adjust positions slightly if needed to better match user intent,
        but STAY WITHIN these boundaries: {session_data['json_data']['boundaries']}
        
        Output JSON format:
        {{
            "fixtures": [
                {{
                    "block_name": "...",
                    "original_position": [...],
                    "new_position": [...],
                    "reasoning": "..."
                }}
            ]
        }}
        """
        
        response = self.ai_mover.model.generate_content(ai_prompt)
        return self._parse_ai_response(response)
```

---

## 🔄 **UPDATED API FLOW**

### **Modified `/api/dashboard/generate_with_ai` Endpoint**

```python
@dashboard_api.post("/generate_with_ai")
def generate_with_ai(request, data: AiGenerateSchema):
    """Enhanced endpoint with prompt classification"""
    
    session_data = utils.load_session(data.session_id)
    if not session_data:
        return {"error": "Invalid session"}, 404
    
    # Initialize enhanced pipeline
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    pipeline = EnhancedAIPipeline(GEMINI_API_KEY)
    
    # Process prompt through enhanced pipeline
    result = pipeline.process_prompt(data.prompt, session_data)
    
    if result.get('error'):
        return {"success": False, "error": result['error']}, 400
    
    # Apply modifications to DXF
    output_path = utils.apply_modifications_to_dxf(
        session_data['original_dxf'],
        result['fixtures'],
        data.session_id
    )
    
    # Update session
    session_data['ai_output_path'] = output_path
    session_data['modifications'].append(result)
    utils.save_session(data.session_id, session_data)
    
    return {
        'success': True,
        'operation_type': result.get('operation_type'),
        'fixtures_modified': len(result['fixtures']),
        'download_url': f'/api/dashboard/download/{data.session_id}'
    }
```

---

## 📁 **NEW FILE STRUCTURE**

```
dashboard/
├── api.py                          # Enhanced endpoint
├── ai_fixture_mover.py             # Existing AI logic
├── prompt_classifier.py            # NEW: Prompt classification
├── math_model_integration.py       # NEW: Math model wrapper
├── enhanced_ai_pipeline.py         # NEW: Orchestration layer
└── utils.py                        # Enhanced utilities
```

---

## 🧪 **TESTING SCENARIOS**

### **Simple Operations (Direct AI)**
| Prompt | Expected Path | Expected Result |
|--------|--------------|-----------------|
| "Move clinic_1 left by 500mm" | Direct AI | Position shifted by -500 on X |
| "Rotate Euro_centre 90°" | Direct AI | Rotation = 90° |
| "Shift table up 1000mm" | Direct AI | Position +1000 on Y |

### **Complex Operations (Math Model + AI)**
| Prompt | Expected Path | Expected Result |
|--------|--------------|-----------------|
| "Rearrange back of house" | Math Model → AI | All BOH fixtures repositioned in BOH zone |
| "Add 2 more clinics" | Math Model → AI | 2 new clinics added in clinic zone |
| "Optimize floor fixtures" | Math Model → AI | All floor fixtures rearranged optimally |
| "Remove all screens and add 3 tables" | Math Model → AI | Screens removed, tables added in valid positions |

---

## ⏱️ **IMPLEMENTATION TIMELINE**

### **Phase 1: Prompt Classification (Week 1)**
- ✅ Create `PromptClassifier` class
- ✅ Define classification rules and patterns
- ✅ Unit tests for classification accuracy
- ✅ Integration with API endpoint

### **Phase 2: Math Model Integration (Week 2)**
- ✅ Create `MathModelIntegration` wrapper
- ✅ Adapt `DXF_Controller` for session-based processing
- ✅ Extract boundary and fixture data from JSON
- ✅ Test position calculations

### **Phase 3: Enhanced Pipeline (Week 3)**
- ✅ Create `EnhancedAIPipeline` orchestration
- ✅ Implement simple/complex routing
- ✅ AI refinement layer
- ✅ End-to-end testing

### **Phase 4: API Integration & Testing (Week 4)**
- ✅ Update `/generate_with_ai` endpoint
- ✅ Frontend integration
- ✅ User acceptance testing
- ✅ Performance optimization

---

## 🔒 **VALIDATION & SAFETY**

### **Position Validation**
```python
def validate_position(position, boundaries):
    """Ensure position is within floor boundaries"""
    x, y = position
    if not (boundaries['min_x'] <= x <= boundaries['max_x']):
        return False
    if not (boundaries['min_y'] <= y <= boundaries['max_y']):
        return False
    return True
```

### **Collision Detection**
```python
def check_collisions(new_fixtures, existing_fixtures):
    """Ensure no fixtures overlap"""
    for new_fix in new_fixtures:
        for exist_fix in existing_fixtures:
            if fixtures_overlap(new_fix, exist_fix):
                return False, f"Collision: {new_fix} overlaps {exist_fix}"
    return True, "No collisions"
```

---

## 📈 **EXPECTED BENEFITS**

1. ✅ **Accurate Positioning**: Math model ensures fixtures stay within boundaries
2. ✅ **Design Compliance**: Follows Lenskart brand guidelines automatically
3. ✅ **Faster Processing**: Simple operations skip math model overhead
4. ✅ **Better AI Results**: AI refines mathematically sound positions
5. ✅ **Reduced Errors**: Validation layers prevent invalid layouts
6. ✅ **Scalability**: Can handle complex multi-fixture operations

---

## 🚀 **NEXT STEPS**

1. **Phase 1: Implement Prompt Classifier**
   - Create `dashboard/prompt_classifier.py`
   - Define classification rules
   - Add unit tests

2. **Phase 2: Math Model Integration**
   - Create `dashboard/math_model_integration.py`
   - Integrate with `backend/Lenskart_Mathametical_Model/`
   - Test position calculations

3. **Phase 3: Enhanced Pipeline**
   - Create `dashboard/enhanced_ai_pipeline.py`
   - Implement routing logic
   - Add AI refinement layer

4. **Phase 4: API Updates**
   - Modify `dashboard/api.py`
   - Update frontend integration
   - Comprehensive testing

---

## 📝 **NOTES**

- The mathematical model is already available in `backend/Lenskart_Mathametical_Model/`
- Current AI implementation is in `dashboard/ai_fixture_mover.py`
- Session management is handled in `dashboard/utils.py`
- DXF processing uses `ezdxf` library
- Floor plan boundaries are extracted from uploaded DXF files

---

**Document Version**: 1.0  
**Last Updated**: January 13, 2026  
**Author**: Lenskart Development Team
