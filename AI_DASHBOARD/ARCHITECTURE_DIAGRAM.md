# Two-Way Communication Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                              │
│                          (canvas.html + CSS)                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐         ┌───────────────────┐                    │
│  │  Canvas Display  │         │  Prompt Textarea  │                    │
│  │  (HTML5 Canvas)  │         │  (Editable Text)  │                    │
│  │                  │         │                   │                    │
│  │  • Drag fixtures │         │  • Manual edit    │                    │
│  │  • Click select  │         │  • AI commands    │                    │
│  │  • Zoom/Pan      │         │  • Rearrange      │                    │
│  └────────┬─────────┘         └─────────┬─────────┘                    │
│           │                              │                              │
│           │  Mouse Events                │  User Prompt                 │
│           ▼                              ▼                              │
│  ┌────────────────────────────────────────────────────┐                │
│  │         Canvas Editor (canvas-editor.js)          │                │
│  │                                                    │                │
│  │  • Render fixtures with colors                    │                │
│  │  • Handle drag & drop                             │                │
│  │  • Track selected fixtures                        │                │
│  │  • Animate updates (pulsing green)                │                │
│  │  • Show "✨ AI" badges                            │                │
│  └────────┬───────────────────────────────┬──────────┘                │
│           │                               │                            │
└───────────┼───────────────────────────────┼────────────────────────────┘
            │                               │
            │ 1. Generate Request           │ 3. Updated Canvas Data
            │ (POST /generate_with_ai)      │ (JSON Response)
            │                               │
┌───────────▼───────────────────────────────▼────────────────────────────┐
│                          BACKEND (Flask app.py)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │         /generate_with_ai Endpoint                       │          │
│  │                                                          │          │
│  │  1. Receive user prompt + session_id                   │          │
│  │  2. Get current DXF JSON from session                  │          │
│  │  3. Send to Gemini AI ──────────────────────┐          │          │
│  │  4. Receive AI modifications                │          │          │
│  │  5. Call apply_ai_modifications()           │          │          │
│  │  6. Extract updated canvas data             │          │          │
│  │  7. Return JSON response                    │          │          │
│  └────────┬────────────────────────────────────┼──────────┘          │
│           │                                    │                      │
│           ▼                                    │                      │
│  ┌────────────────────────────────────────────┼──────────┐          │
│  │      apply_ai_modifications()              │          │          │
│  │                                            │          │          │
│  │  For each modification:                   │          │          │
│  │   • Load DXF file (ezdxf)                 │          │          │
│  │   • Update INSERT entities (MOVE/COPY/    │          │          │
│  │     DELETE/ROTATE)                        │          │          │
│  │   • ALSO update session JSON data ◄───────┘          │          │
│  │   • Save modified DXF file                           │          │
│  │                                                      │          │
│  │  Returns: output_path                               │          │
│  └─────────┬────────────────────────────────────────────┘          │
│            │                                                        │
│            ▼                                                        │
│  ┌──────────────────────────────────────────────────────┐          │
│  │      extract_canvas_data()                           │          │
│  │                                                      │          │
│  │  • Read updated JSON data                           │          │
│  │  • Calculate fixture sizes from blocks              │          │
│  │  • Build canvas-ready data structure                │          │
│  │  • Include blueprint geometry                       │          │
│  │  • Calculate bounds for auto-fit                    │          │
│  │                                                      │          │
│  │  Returns: canvas_data {                             │          │
│  │    fixtures: [...],                                 │          │
│  │    blueprint: [...],                                │          │
│  │    bounds: {...}                                    │          │
│  │  }                                                   │          │
│  └──────────────────────────────────────────────────────┘          │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                    Session Storage (in-memory)                      │
│                                                                     │
│  session_storage[session_id] = {                                   │
│    'original_dxf': path,                                           │
│    'filename': name,                                               │
│    'json_data': {...},      ◄─── UPDATED BY AI                    │
│    'modifications': [...],                                         │
│    'ai_output_path': path                                          │
│  }                                                                  │
└─────────────────────────────────────────────────────────────────────┘
            │
            │ 2. AI Request
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     GEMINI AI (Google API)                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Input:                                                             │
│  • User prompt: "Rearrange these fixtures like an architect"       │
│  • Current fixture positions: [{name, position}, ...]              │
│  • Floorplan boundaries: {min_x, max_x, min_y, max_y}             │
│  • Selected fixtures: [names...]                                   │
│                                                                      │
│  Processing:                                                        │
│  • Parse user intent (move/copy/delete/rotate/rearrange)          │
│  • Calculate new positions with architectural rules                │
│  • Ensure no overlaps                                              │
│  • Stay within boundaries                                          │
│  • Maintain proper clearances (800-1200mm)                         │
│                                                                      │
│  Output:                                                            │
│  {                                                                  │
│    "fixtures": [                                                    │
│      {                                                              │
│        "block_name": "FIXTURE_A",                                  │
│        "operation": "move",                                        │
│        "original_position": [x1, y1],                             │
│        "new_position": [x2, y2],                                  │
│        "reason": "Improved circulation flow"                      │
│      },                                                             │
│      ...                                                            │
│    ]                                                                │
│  }                                                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Sequence

### 1. User Initiates Change
```
User Action: Clicks "Generate with AI" button
    │
    ├─► Frontend: Reads user prompt from textarea
    │
    └─► Frontend: Sends POST request to /generate_with_ai
        {
          session_id: "abc123",
          prompt: "Rearrange FIXTURE_A, FIXTURE_B like an architect"
        }
```

### 2. Backend Processes Request
```
Backend Receives Request
    │
    ├─► 1. Validate session_id
    │
    ├─► 2. Get current JSON data from session
    │
    ├─► 3. Extract fixture list with positions
    │
    ├─► 4. Build AI prompt with:
    │      • User's command
    │      • Current fixture positions
    │      • Floorplan boundaries
    │      • Architectural rules
    │
    └─► 5. Send to Gemini API
```

### 3. Gemini AI Generates Modifications
```
Gemini AI Processes
    │
    ├─► 1. Parse user intent
    │
    ├─► 2. Calculate optimal positions
    │      • No overlaps
    │      • Proper clearances
    │      • Within boundaries
    │
    └─► 3. Return JSON modifications
        {
          "fixtures": [
            {"block_name": "FIXTURE_A", "operation": "move", ...},
            {"block_name": "FIXTURE_B", "operation": "move", ...}
          ]
        }
```

### 4. Backend Applies Modifications
```
apply_ai_modifications()
    │
    ├─► 1. Load original DXF file (ezdxf)
    │
    ├─► 2. For each modification:
    │      │
    │      ├─► MOVE: Update entity.dxf.insert
    │      ├─► COPY: Create new entity
    │      ├─► DELETE: Remove entity
    │      └─► ROTATE: Update entity.dxf.rotation
    │
    ├─► 3. ALSO update JSON data in session
    │      For each entity in json_data['modelspace']:
    │        Update e['insert'] = [new_x, new_y, z]
    │
    ├─► 4. Save modified DXF file
    │
    └─► 5. Update session_storage[session_id]['json_data']
```

### 5. Backend Extracts Canvas Data
```
extract_canvas_data()
    │
    ├─► 1. Read updated JSON data
    │
    ├─► 2. Calculate fixture sizes from block definitions
    │
    ├─► 3. Build fixtures array:
    │      [
    │        {
    │          id: "FIXTURE_A@100,200",
    │          name: "FIXTURE_A",
    │          position: [100, 200],
    │          width: 500,
    │          height: 300,
    │          ...
    │        }
    │      ]
    │
    ├─► 4. Extract blueprint geometry (walls, lines)
    │
    ├─► 5. Calculate bounds for auto-fit
    │
    └─► 6. Return canvas_data
```

### 6. Backend Sends Response
```
Response to Frontend
    {
      "success": true,
      "message": "✅ Processed: 2 moved",
      "operations": {moved: 2, copied: 0, deleted: 0, rotated: 0},
      "updated_canvas_data": {
        "fixtures": [...],      ◄── NEW: Canvas can update!
        "blueprint": [...],
        "bounds": {...}
      },
      "modifications": [...]    ◄── NEW: Know what changed!
    }
```

### 7. Frontend Updates Canvas
```
generateWithAI() receives response
    │
    ├─► 1. Check if updated_canvas_data exists
    │
    ├─► 2. Mark updated fixtures:
    │      data.updated_canvas_data.fixtures.forEach(f => {
    │        f._recentlyUpdated = true;  // Flag for animation
    │      });
    │
    ├─► 3. Reload canvas:
    │      editor.loadCanvasData(data.updated_canvas_data)
    │
    ├─► 4. Start animation:
    │      editor.renderWithAnimation()
    │        • 30 frames
    │        • Green pulsing effect
    │        • "✨ AI" badges
    │
    ├─► 5. Visual effects:
    │      • Canvas container glow (1 second)
    │      • Status message
    │
    └─► 6. Auto-clear flags after 3 seconds
         setTimeout(() => {
           fixtures.forEach(f => delete f._recentlyUpdated);
           editor.render();
         }, 3000);
```

### 8. Canvas Renders Updates
```
editor.renderWithAnimation()
    │
    ├─► Frame 0-30: Animate
    │   │
    │   └─► drawFixture() for each fixture
    │       │
    │       └─► If fixture._recentlyUpdated:
    │           │
    │           ├─► Calculate pulse intensity:
    │           │   pulse = sin((frame / 30) * PI * 4)
    │           │   intensity = 0.3 + 0.7 * abs(pulse)
    │           │
    │           ├─► Blend colors:
    │           │   fillColor = blend(baseColor, green, intensity)
    │           │
    │           ├─► Draw thicker border (4px)
    │           │
    │           └─► Draw "✨ AI" badge above fixture
    │
    └─► After 30 frames: Normal rendering
```

---

## Visual Update Timeline

```
Time 0ms: User clicks "Generate with AI"
    │
    │ Loading spinner appears
    │
Time 500ms: Gemini AI responds
    │
    │ Backend applies modifications
    │
Time 800ms: Response sent to frontend
    │
    │ Canvas update begins
    │
Time 850ms: Canvas shows new layout
    │
    │ ┌─────────────────────────────────┐
    │ │  🎨 Canvas                      │
    │ │                                 │
    │ │   ┌──────────┐                 │
    │ │   │ FIXTURE_A│ ◄── Green pulse │
    │ │   │  ✨ AI   │                 │
    │ │   └──────────┘                 │
    │ │                                 │
    │ │        ┌──────────┐            │
    │ │        │ FIXTURE_B│ ◄── Green  │
    │ │        │  ✨ AI   │     pulse  │
    │ │        └──────────┘            │
    │ └─────────────────────────────────┘
    │
    │ Pulsing animation (30 frames)
    │
Time 1500ms: Animation completes
    │
    │ Fixtures still highlighted
    │
Time 3850ms: Badges disappear
    │
    │ ┌─────────────────────────────────┐
    │ │  🎨 Canvas                      │
    │ │                                 │
    │ │   ┌──────────┐                 │
    │ │   │ FIXTURE_A│ ◄── Normal color│
    │ │   │          │                 │
    │ │   └──────────┘                 │
    │ │                                 │
    │ │        ┌──────────┐            │
    │ │        │ FIXTURE_B│            │
    │ │        │          │            │
    │ │        └──────────┘            │
    │ └─────────────────────────────────┘
    │
    ▼
User can now:
  • Drag fixtures to adjust
  • Select and rearrange again
  • Give new AI commands
  • Download DXF when satisfied
```

---

## Key Innovation: Dual Update System

### Traditional Approach (One-Way)
```
User Input → AI Processing → DXF File → Download → External Viewer
                                    ↓
                            Canvas stays STALE
```

### New Approach (Two-Way)
```
User Input → AI Processing → ┌─► DXF File (for download)
                              │
                              └─► JSON Data → Canvas Updates
                                             ↓
                                     User sees results IMMEDIATELY
                                             ↓
                                     Continue editing
```

### Why This Works
1. **Session storage** maintains both DXF and JSON
2. **Dual updates** modify both in sync
3. **Canvas data extraction** converts JSON to renderable format
4. **Frontend reload** refreshes display instantly
5. **Visual feedback** confirms changes to user

---

## Summary

The two-way communication system creates a **real-time design loop**:

```
┌─────────────────────────────────────────────────┐
│                                                  │
│   User Edits → AI Generates → Canvas Updates   │
│       ▲                              │          │
│       │                              │          │
│       └──────── User Sees ───────────┘          │
│                                                  │
│            (Repeat until satisfied)             │
│                                                  │
└─────────────────────────────────────────────────┘
```

**Result**: Professional, iterative design workflow similar to modern CAD/design tools.
