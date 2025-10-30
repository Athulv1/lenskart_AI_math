# Two-Way Communication Feature Guide

## Overview

This application now supports **real-time two-way communication** between the user, Gemini AI, and the canvas. Users can see AI-generated changes immediately on the canvas without downloading the DXF file.

---

## How It Works

### 1. **User Interaction → Canvas**
- User drags fixtures on the canvas
- User selects fixtures with Ctrl+Click
- User manually edits the AI prompt

### 2. **Canvas → Gemini AI**
- User clicks "Generate with AI"
- System sends:
  - User's edited prompt
  - Current fixture positions
  - Selected fixtures (if any)
  - Floorplan boundaries

### 3. **Gemini AI → Canvas (Two-Way Communication)**
- Gemini generates layout modifications
- **Backend updates:**
  - DXF file (for download)
  - JSON data (for canvas)
- **Frontend receives:**
  - Updated canvas data
  - List of modified fixtures
- **Canvas automatically refreshes:**
  - Shows updated fixture positions
  - Highlights modified fixtures with green glow
  - Animates the update with pulsing effect

### 4. **Canvas → User Editing**
- User sees the AI-generated changes immediately
- User can continue editing:
  - Drag fixtures to adjust positions
  - Select and rearrange again
  - Give new AI commands
- **No need to download DXF to see results**

---

## User Workflow Examples

### Example 1: Simple Move & Iterate
```
1. User drags FIXTURE_A to new position
2. Clicks "Generate with AI"
3. Canvas updates immediately showing FIXTURE_A in new position
4. User sees the result and drags FIXTURE_B
5. Clicks "Generate with AI" again
6. Canvas updates again with both changes
7. Repeat until satisfied
8. Click "Download DXF" to save final result
```

### Example 2: Multi-Fixture Rearrangement
```
1. User Ctrl+Clicks 5 fixtures to select them
2. Types: "Rearrange these fixtures like an architect"
3. Clicks "Generate with AI"
4. Gemini calculates optimal positions with proper spacing
5. Canvas updates showing all 5 fixtures in new positions
6. User reviews the layout visually
7. User selects 2 of them and gives new command: "Move these closer together"
8. Canvas updates again with refined positions
9. Download when happy with result
```

### Example 3: Iterative Design with AI
```
1. User: "Move SOFA_1 to position (1500, 2000)"
2. AI moves it, canvas updates
3. User sees overlap with TABLE_1
4. User: "Move TABLE_1 500mm to the right"
5. AI moves it, canvas updates
6. User visually confirms no overlap
7. User: "Copy CHAIR_1 and place it 800mm away from SOFA_1"
8. AI creates copy, canvas updates showing both
9. Continue iterating...
```

---

## Technical Implementation

### Backend (app.py)

#### 1. **JSON Data Updates**
When AI generates modifications, the backend updates BOTH:
- **DXF file** (using ezdxf library)
- **Session JSON data** (for canvas refresh)

```python
def apply_ai_modifications(session_id, modifications):
    # Update DXF file
    entity.dxf.insert = (new_pos[0], new_pos[1], pos.z)
    
    # ALSO update JSON data
    for e in json_data.get('modelspace', []):
        if e.get('dxf_type') == 'INSERT' and e.get('name') == block_name:
            e['insert'] = [new_pos[0], new_pos[1], e_pos[2]]
    
    # Save updated JSON to session
    session_storage[session_id]['json_data'] = json_data
```

#### 2. **Canvas Data Extraction**
After modifications, extract fresh canvas data:
```python
updated_canvas_data = extract_canvas_data(
    session_storage[session_id]['json_data'], 
    original_dxf
)

return jsonify({
    'success': True,
    'updated_canvas_data': updated_canvas_data,
    'modifications': modifications.get('fixtures', [])
})
```

### Frontend (canvas.html)

#### 1. **Receiving Updates**
```javascript
const response = await fetch('/generate_with_ai', {
    method: 'POST',
    body: JSON.stringify({
        session_id: currentSessionId,
        prompt: userPrompt
    })
});

const data = await response.json();

if (data.updated_canvas_data) {
    // Mark updated fixtures for visual feedback
    data.updated_canvas_data.fixtures.forEach(fixture => {
        if (wasModified(fixture)) {
            fixture._recentlyUpdated = true;
        }
    });
    
    // Reload canvas
    editor.loadCanvasData(data.updated_canvas_data);
}
```

#### 2. **Visual Feedback**
- **Green pulsing border** on modified fixtures (3 seconds)
- **"✨ AI" badge** above updated fixtures
- **Canvas glow effect** on the entire container
- **Status message** confirming update

### Canvas Editor (canvas-editor.js)

#### 1. **Animation System**
```javascript
loadCanvasData(data) {
    this.fixtures = data.fixtures;
    this.renderWithAnimation();
}

renderWithAnimation() {
    this.animationFrame = 0;
    this.maxAnimationFrames = 30;
    
    const animate = () => {
        this.render();
        this.animationFrame++;
        if (this.animationFrame < this.maxAnimationFrames) {
            requestAnimationFrame(animate);
        }
    };
    animate();
}
```

#### 2. **Visual Highlighting**
```javascript
drawFixture(fixture) {
    if (fixture._recentlyUpdated && this.animationFrame !== undefined) {
        // Pulsing green effect
        const pulse = Math.sin((this.animationFrame / this.maxAnimationFrames) * Math.PI * 4);
        const intensity = 0.3 + 0.7 * Math.abs(pulse);
        fillColor = this.blendColors(baseColor, '#10b981', intensity);
        strokeColor = '#059669';
    }
}
```

---

## Benefits

### For Users
✅ **Instant Visual Feedback** - See AI changes immediately  
✅ **Iterative Design** - Try multiple layouts quickly  
✅ **No Download Required** - Preview before committing  
✅ **Interactive Refinement** - Combine AI + manual editing  
✅ **Visual Confirmation** - Catch errors before saving  

### For Workflow
✅ **Faster Iteration** - No need to download/reupload cycle  
✅ **Confidence** - See exactly what AI did  
✅ **Flexibility** - Continue editing after AI generates  
✅ **Transparency** - Visual highlights show what changed  

---

## Technical Features

### Data Synchronization
- **Single Source of Truth**: Session JSON data
- **Dual Updates**: DXF file + JSON data updated together
- **Consistency**: Canvas always shows current state

### Visual Feedback System
- **Pulsing Animation**: 30-frame smooth pulse effect
- **Color Blending**: Gradual transition from base to green
- **Temporary Markers**: Auto-clear after 3 seconds
- **Border Highlighting**: Thicker borders on updated fixtures

### Performance
- **Efficient Re-rendering**: Only affected fixtures update
- **Smooth Animations**: 60 FPS using requestAnimationFrame
- **Minimal Data Transfer**: Only send updated canvas data
- **Session Persistence**: Changes persist across interactions

---

## User Interface Elements

### Status Messages
```
✨ Canvas updated! You can see the changes and continue editing.
✅ Processed: 5 moved, 2 copied, 1 deleted
🤖 Calling Gemini AI...
```

### Visual Indicators
- **Yellow Border**: Currently dragging fixture
- **Blue Border**: Selected for AI rearrangement
- **Green Pulsing Border**: Recently updated by AI
- **"✨ AI" Badge**: Marks AI-modified fixtures

### Canvas Effects
- **Container Glow**: Green shadow around canvas (1 second)
- **Smooth Transitions**: Fade effects on highlights
- **Legend**: Color-coded fixture types

---

## Error Handling

### Network Errors
- Shows error message in status bar
- Keeps canvas in previous state
- Allows user to retry

### AI Failures
- Falls back to manual editing
- Shows clear error messages
- Preserves user's prompt for retry

### Data Consistency
- Validates modifications before applying
- Logs all changes to console
- Maintains session integrity

---

## Future Enhancements

### Potential Additions
1. **Undo/Redo** - Revert AI changes
2. **Change History** - Track all modifications
3. **Side-by-Side Comparison** - Before/After view
4. **AI Suggestions Panel** - Show multiple layout options
5. **Collaborative Editing** - Real-time multi-user support
6. **Version Control** - Save multiple design iterations

---

## Troubleshooting

### Canvas Not Updating
- Check browser console for errors
- Verify `updated_canvas_data` in response
- Ensure session ID is valid

### Fixtures Not Highlighted
- Check `_recentlyUpdated` flag is set
- Verify animation system is running
- Check console for rendering errors

### AI Changes Not Visible
- Verify JSON data is updated in session
- Check `apply_ai_modifications` logs
- Ensure canvas data extraction succeeds

---

## Summary

The two-way communication feature transforms the application from a one-way "upload → AI → download" workflow into an **interactive design tool** where users can:

1. **See AI results immediately** on the canvas
2. **Iterate quickly** without downloading files
3. **Combine AI intelligence** with manual fine-tuning
4. **Build confidence** through visual feedback
5. **Design faster** with real-time updates

This creates a seamless, modern user experience similar to professional design software like Figma or AutoCAD, but powered by AI.
