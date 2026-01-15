# 📖 Enhanced AI Pipeline - Usage Examples

This document provides practical examples of how to use the enhanced AI pipeline with different types of prompts.

---

## 🎯 Quick Reference

| Operation Type | Example Prompt | Processing Method | Use Case |
|---------------|----------------|-------------------|----------|
| **Simple** | "Move clinic_1 left by 500mm" | Direct AI | Quick adjustments |
| **Simple** | "Rotate table 90 degrees" | Direct AI | Single transformations |
| **Complex** | "Rearrange back of house" | Math Model + AI | Section reorganization |
| **Complex** | "Add 2 more clinics" | Math Model + AI | Adding fixtures |
| **Complex** | "Remove all screens" | Math Model + AI | Bulk operations |

---

## 📝 Example Prompts

### **Category 1: Simple Move Operations**

#### Example 1.1: Move by Distance
```
Prompt: "Move clinic_1 left by 500mm"

Classification:
  - Type: Simple
  - Intent: move
  - Confidence: 100%
  - Math Model: No

Result:
  - clinic_1 position updated
  - X coordinate decreased by 500
  - Quick AI processing
```

#### Example 1.2: Directional Move
```
Prompt: "Shift Euro_centre up by 1000mm"

Classification:
  - Type: Simple
  - Intent: move
  - Confidence: 80%
  - Math Model: No

Result:
  - Euro_centre moved upward
  - Y coordinate increased by 1000
```

#### Example 1.3: Coordinate Move
```
Prompt: "Move table to position 5000, 3000"

Classification:
  - Type: Simple
  - Intent: move
  - Confidence: 70%
  - Math Model: No

Result:
  - Table moved to exact coordinates
  - Position set to [5000, 3000]
```

---

### **Category 2: Simple Rotation Operations**

#### Example 2.1: Degree Rotation
```
Prompt: "Rotate clinic_1 by 90 degrees"

Classification:
  - Type: Simple
  - Intent: rotate
  - Confidence: 100%
  - Math Model: No

Result:
  - clinic_1 rotated 90° clockwise
  - Position unchanged
```

#### Example 2.2: Directional Rotation
```
Prompt: "Turn screen clockwise by 45 degrees"

Classification:
  - Type: Simple
  - Intent: rotate
  - Confidence: 100%
  - Math Model: No

Result:
  - Screen rotated 45° clockwise
```

---

### **Category 3: Complex Rearrangement Operations**

#### Example 3.1: Section Rearrangement
```
Prompt: "Rearrange back of house"

Classification:
  - Type: Complex
  - Intent: rearrange
  - Confidence: 50%
  - Math Model: Yes

Processing:
  1. Math Model identifies BOH zone
  2. Calculates optimal positions for all BOH fixtures
  3. AI refines positions based on prompt
  4. Validates against boundaries

Result:
  - All BOH fixtures repositioned
  - Optimal spacing maintained
  - Design guidelines followed
```

#### Example 3.2: Clinic Reorganization
```
Prompt: "Reorganize the entire clinic section"

Classification:
  - Type: Complex
  - Intent: rearrange
  - Confidence: 80%
  - Math Model: Yes

Processing:
  1. Math Model identifies clinic zone
  2. Applies clinic-specific design rules
  3. Ensures accessibility compliance
  4. AI makes aesthetic adjustments

Result:
  - All clinics repositioned in clinic zone
  - Proper spacing between units
  - ADA-compliant pathways
```

#### Example 3.3: Floor Optimization
```
Prompt: "Optimize floor fixtures layout"

Classification:
  - Type: Complex
  - Intent: rearrange
  - Confidence: 50%
  - Math Model: Yes

Processing:
  1. Math Model analyzes current layout
  2. Calculates traffic flow optimization
  3. Minimizes wasted space
  4. AI validates aesthetic appeal

Result:
  - Floor fixtures optimally positioned
  - Maximum space utilization
  - Improved customer flow
```

---

### **Category 4: Adding Fixtures**

#### Example 4.1: Add Multiple Fixtures
```
Prompt: "Add 2 more clinics"

Classification:
  - Type: Complex
  - Intent: add
  - Confidence: 80%
  - Math Model: Yes

Processing:
  1. Math Model identifies available space
  2. Calculates positions in clinic zone
  3. Ensures no collisions
  4. AI refines placement

Result:
  - 2 new clinics added
  - Positioned in clinic zone
  - Proper spacing from existing fixtures
```

#### Example 4.2: Add with Location
```
Prompt: "Add 3 tables in the center area"

Classification:
  - Type: Complex
  - Intent: add
  - Confidence: 70%
  - Math Model: Yes

Processing:
  1. Math Model identifies center area
  2. Calculates grid positions for 3 tables
  3. Validates spacing requirements
  4. AI adjusts for aesthetics

Result:
  - 3 new tables added in center
  - Evenly spaced
  - Within boundaries
```

---

### **Category 5: Removing Fixtures**

#### Example 5.1: Remove All of Type
```
Prompt: "Remove all screens"

Classification:
  - Type: Complex
  - Intent: remove
  - Confidence: 100%
  - Math Model: Yes

Processing:
  1. Identifies all screen fixtures
  2. Marks for deletion
  3. Updates layout

Result:
  - All screen fixtures removed
  - Layout remains valid
```

#### Example 5.2: Clear Section
```
Prompt: "Delete entire BOH section"

Classification:
  - Type: Complex
  - Intent: remove
  - Confidence: 80%
  - Math Model: Yes

Processing:
  1. Identifies all BOH fixtures
  2. Marks all for deletion
  3. Validates remaining layout

Result:
  - All BOH fixtures removed
  - Space available for new layout
```

---

### **Category 6: Combined Operations**

#### Example 6.1: Replace Fixtures
```
Prompt: "Remove all screens and add 3 tables"

Classification:
  - Type: Complex
  - Intent: add
  - Confidence: 100%
  - Math Model: Yes

Processing:
  1. Remove all screens first
  2. Math Model calculates positions for 3 tables
  3. Places tables in freed space
  4. AI validates layout

Result:
  - Screens removed
  - 3 tables added in optimal positions
```

#### Example 6.2: Reorganize Multiple Sections
```
Prompt: "Rearrange BOH and optimize clinic layout"

Classification:
  - Type: Complex
  - Intent: rearrange
  - Confidence: 80%
  - Math Model: Yes

Processing:
  1. Process BOH rearrangement
  2. Process clinic optimization
  3. Ensure no conflicts between sections
  4. AI validates complete layout

Result:
  - BOH reorganized
  - Clinics optimized
  - Cohesive overall layout
```

---

## 🔧 API Usage Examples

### **Python Example:**

```python
import requests
import json

# Upload DXF and get session_id
files = {'dxf_file': open('floorplan.dxf', 'rb')}
response = requests.post('http://localhost:8000/api/dashboard/upload', files=files)
session_id = response.json()['session_id']

# Simple operation
simple_prompt = {
    "session_id": session_id,
    "prompt": "Move clinic_1 left by 500mm"
}
result = requests.post(
    'http://localhost:8000/api/dashboard/generate_with_ai',
    json=simple_prompt
)
print(f"Operation: {result.json()['operation_type']}")  # Output: simple
print(f"Method: {result.json()['method']}")  # Output: direct_ai

# Complex operation
complex_prompt = {
    "session_id": session_id,
    "prompt": "Rearrange back of house"
}
result = requests.post(
    'http://localhost:8000/api/dashboard/generate_with_ai',
    json=complex_prompt
)
print(f"Operation: {result.json()['operation_type']}")  # Output: complex
print(f"Method: {result.json()['method']}")  # Output: math_model

# Download modified DXF
download_url = result.json()['download_url']
dxf_file = requests.get(f'http://localhost:8000{download_url}')
with open('modified_floorplan.dxf', 'wb') as f:
    f.write(dxf_file.content)
```

### **cURL Examples:**

```bash
# Upload DXF
curl -X POST http://localhost:8000/api/dashboard/upload \
  -F "dxf_file=@floorplan.dxf" \
  -o response.json

# Extract session_id
SESSION_ID=$(cat response.json | jq -r '.session_id')

# Simple operation
curl -X POST http://localhost:8000/api/dashboard/generate_with_ai \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"prompt\": \"Move clinic_1 left by 500mm\"
  }"

# Complex operation
curl -X POST http://localhost:8000/api/dashboard/generate_with_ai \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"prompt\": \"Rearrange back of house\"
  }"

# Download modified DXF
curl -X GET "http://localhost:8000/api/dashboard/download/$SESSION_ID" \
  -o modified_floorplan.dxf
```

---

## 📊 Response Interpretation

### **Simple Operation Response:**
```json
{
  "success": true,
  "operation_type": "simple",
  "method": "direct_ai",
  "fixtures_modified": 1,
  "classification": {
    "operation_type": "simple",
    "intent": "move",
    "confidence": 1.0,
    "requires_math_model": false,
    "reasoning": "Detected simple operation pattern"
  },
  "warnings": [],
  "download_url": "/api/dashboard/download/abc-123"
}
```

### **Complex Operation Response:**
```json
{
  "success": true,
  "operation_type": "complex",
  "method": "math_model_ai_refined",
  "fixtures_modified": 5,
  "classification": {
    "operation_type": "complex",
    "intent": "rearrange",
    "confidence": 0.8,
    "requires_math_model": true,
    "reasoning": "Multiple fixture changes detected"
  },
  "warnings": [
    "Some fixtures adjusted for optimal spacing"
  ],
  "download_url": "/api/dashboard/download/xyz-789"
}
```

---

## 💡 Best Practices

### **1. Be Specific for Simple Operations**
✅ Good: "Move clinic_1 left by 500mm"
❌ Vague: "Move the clinic a bit"

### **2. Use Clear Intent for Complex Operations**
✅ Good: "Rearrange back of house"
✅ Good: "Add 2 more clinics"
❌ Vague: "Make it better"

### **3. Specify Quantities**
✅ Good: "Add 3 tables"
❌ Vague: "Add some tables"

### **4. Use Section Names**
✅ Good: "Reorganize BOH section"
✅ Good: "Optimize clinic area"
❌ Vague: "Fix that corner"

### **5. Combine Related Operations**
✅ Good: "Remove all screens and add 3 tables"
❌ Separate: Two separate prompts

---

## 🎓 Training Examples for Users

Share these examples with users to help them write effective prompts:

1. **"Move [fixture_name] [direction] by [distance]mm"**
   - Example: "Move clinic_1 left by 500mm"

2. **"Rotate [fixture_name] by [angle] degrees"**
   - Example: "Rotate table 90 degrees"

3. **"Rearrange [section_name]"**
   - Example: "Rearrange back of house"

4. **"Add [number] [fixture_type]"**
   - Example: "Add 2 more clinics"

5. **"Remove all [fixture_type]"**
   - Example: "Remove all screens"

6. **"Optimize [section_name] layout"**
   - Example: "Optimize floor fixtures layout"

---

**Updated**: January 13, 2026  
**Version**: 1.0
