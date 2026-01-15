# dashboard/utils.py
import os
import json
import ezdxf
from django.conf import settings
from .enhanced_dxf_to_json import dxf_to_json
from .ai_fixture_mover import AIFixtureMover
import google.generativeai as genai  


# Use Django settings for folders
UPLOAD_FOLDER = os.path.join(settings.MEDIA_ROOT, 'uploads')
OUTPUT_FOLDER = os.path.join(settings.MEDIA_ROOT, 'outputs')
SESSION_STORAGE = os.path.join(settings.BASE_DIR, 'dashboard', 'session_storage')
session_storage = {}


def save_session(session_id, session_data):
    """Save session data to disk"""
    session_file = os.path.join(SESSION_STORAGE, f"{session_id}.json")
    try:
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        print(f"💾 Saved session {session_id} to disk")
    except Exception as e:
        print(f"⚠️ Failed to save session {session_id}: {e}")

def load_session(session_id):
    """Load session data from disk"""
    session_file = os.path.join(SESSION_STORAGE, f"{session_id}.json")
    if os.path.exists(session_file):
        with open(session_file, 'r') as f:
            return json.load(f)
    return None

def session_exists(session_id):
    session_file = os.path.join(SESSION_STORAGE, f"{session_id}.json")
    return os.path.exists(session_file)



os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(SESSION_STORAGE, exist_ok=True)

# --- PASTE ALL YOUR HELPER FUNCTIONS HERE ---
# (calculate_block_sizes, extract_canvas_data, etc.)
# Note: Update any reference to app.config['UPLOAD_FOLDER'] to UPLOAD_FOLDER

def calculate_block_sizes(json_data, dxf_path=None):
    """
    Calculate the bounding box size of each block definition
    
    Args:
        json_data: Complete DXF JSON structure
        dxf_path: Optional path to DXF file for using ezdxf's bounding_box method
    
    Returns:
        Dictionary mapping block names to their sizes
    """
    block_sizes = {}
    
    # Note: ezdxf's bounding_box() method may not be available on all versions
    # We'll use manual calculation which handles nested blocks better
    
    # Note: ezdxf's bounding_box() method may not be available on all versions
    # We'll use manual calculation which handles nested blocks better
    
    # Fallback: Manual calculation from JSON data
    print("⚙️  Using manual bounding box calculation from JSON...")
    
    # First pass: Calculate all blocks with actual geometry
    for block_name, block_data in json_data.get('blocks', {}).items():
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        has_geometry = False
        entity_count = 0
        
        for entity in block_data.get('entities', []):
            entity_type = entity['dxf_type']
            entity_count += 1
            
            if entity_type == 'LINE':
                points = [entity['start'][:2], entity['end'][:2]]
                for x, y in points:
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
                has_geometry = True
            
            elif entity_type in ['LWPOLYLINE', 'POLYLINE']:
                for point in entity.get('points', []):
                    x, y = point[:2] if len(point) > 2 else point
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
                has_geometry = True
            
            elif entity_type == 'CIRCLE':
                center = entity['center'][:2]
                radius = entity['radius']
                min_x = min(min_x, center[0] - radius)
                min_y = min(min_y, center[1] - radius)
                max_x = max(max_x, center[0] + radius)
                max_y = max(max_y, center[1] + radius)
                has_geometry = True
            
            elif entity_type == 'ARC':
                center = entity['center'][:2]
                radius = entity['radius']
                min_x = min(min_x, center[0] - radius)
                min_y = min(min_y, center[1] - radius)
                max_x = max(max_x, center[0] + radius)
                max_y = max(max_y, center[1] + radius)
                has_geometry = True
            
            elif entity_type == 'SPLINE':
                # SPLINEs have control_points or fit_points
                control_points = entity.get('control_points', [])
                fit_points = entity.get('fit_points', [])
                points = control_points if control_points else fit_points
                
                for point in points:
                    x, y = point[:2] if len(point) > 2 else point
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
                has_geometry = True
            
            elif entity_type == 'ELLIPSE':
                # ELLIPSE has center, major_axis, and ratio
                center = entity.get('center', [0, 0])[:2]
                major_axis = entity.get('major_axis', [0, 0])[:2]
                ratio = entity.get('ratio', 1.0)
                
                # Calculate semi-major and semi-minor axes lengths
                major_length = (major_axis[0]**2 + major_axis[1]**2)**0.5
                minor_length = major_length * ratio
                
                # Approximate bounding box (not exact for rotated ellipses)
                min_x = min(min_x, center[0] - major_length)
                min_y = min(min_y, center[1] - major_length)
                max_x = max(max_x, center[0] + major_length)
                max_y = max(max_y, center[1] + major_length)
                has_geometry = True
            
            elif entity_type in ['TEXT', 'MTEXT']:
                # TEXT/MTEXT: Only use insertion point, do NOT calculate text width
                # Text width can incorrectly inflate bounding boxes
                insert = entity.get('insert', entity.get('position', [0, 0]))[:2]
                min_x = min(min_x, insert[0])
                min_y = min(min_y, insert[1])
                max_x = max(max_x, insert[0])
                max_y = max(max_y, insert[1])
                has_geometry = True
            
            elif entity_type == 'POINT':
                # POINT has a location
                location = entity.get('location', [0, 0])[:2]
                min_x = min(min_x, location[0])
                min_y = min(min_y, location[1])
                max_x = max(max_x, location[0])
                max_y = max(max_y, location[1])
                has_geometry = True
            
            # Note: We do NOT include INSERT entities in Pass 1
            # INSERT entities will be resolved in Pass 2 and Pass 3
            # Including them here causes issues with insertion points far from geometry
        
        if has_geometry and min_x != float('inf'):
            width = max_x - min_x
            height = max_y - min_y
            
            # Use absolute values to handle negative sizes
            width = abs(width)
            height = abs(height)
            
            # Ensure minimum size for visibility
            width = max(width, 100)
            height = max(height, 100)
            
            block_sizes[block_name] = {
                'width': width,
                'height': height,
                'min_x': min_x,
                'min_y': min_y,
                'max_x': max_x,
                'max_y': max_y
            }


            # Debug output
            if entity_count > 0:
                print(f"   ✓ {block_name}: {width:.1f} × {height:.1f} mm ({entity_count} entities)")
        else:
            # Default size if no geometry found
            print(f"   ⚠ {block_name}: No geometry found, using default 300×300mm")
            block_sizes[block_name] = {
                'width': 300,
                'height': 300,
                'min_x': -150,
                'min_y': -150,
                'max_x': 150,
                'max_y': 150
            }
    
    # Fix SCREEN_55 dimensions (special case for 55" TV screens)
    # SCREEN_55 blocks often have incorrect geometry-based dimensions
    for block_name in list(block_sizes.keys()):
        if 'SCREEN_55' in block_name.upper() or 'SCREEN55' in block_name.upper():
            current_size = block_sizes[block_name]
            # Check if dimensions look wrong (too narrow or using only geometric primitives)
            if current_size['width'] < 150:  # 55" TV should be much wider
                # Use standard 55" TV dimensions (approximately 1209mm × 680mm for 16:9 aspect ratio)
                # The "it 55inch tv" block has incorrect dimensions (122.8 × 1241mm - too narrow)
                
                # IMPORTANT: Maintain the original block offset to preserve position
                # Original block was at min_x=570.5, we need to keep the same center point
                original_center_x = (current_size['min_x'] + current_size['max_x']) / 2
                original_center_y = (current_size['min_y'] + current_size['max_y']) / 2
                
                new_width = 1209.0
                new_height = 680.0
                
                new_min_x = original_center_x - new_width / 2
                new_max_x = original_center_x + new_width / 2
                new_min_y = original_center_y - new_height / 2
                new_max_y = original_center_y + new_height / 2
                
                print(f"   🔄 {block_name}: {current_size['width']:.1f} × {current_size['height']:.1f} mm → {new_width:.1f} × {new_height:.1f} mm (corrected to standard 55\" TV dimensions)")
                block_sizes[block_name] = {
                    'width': new_width,
                    'height': new_height,
                    'min_x': new_min_x,
                    'min_y': new_min_y,
                    'max_x': new_max_x,
                    'max_y': new_max_y
                }
    
    # Second pass: Resolve nested blocks (blocks that only contain INSERT entities)
    print("🔗 Resolving nested block references...")
    resolved_count = 0
    
    # Create case-insensitive lookup for block sizes
    block_sizes_lower = {k.lower(): (k, v) for k, v in block_sizes.items()}
    
    for block_name, block_data in json_data.get('blocks', {}).items():
        # Check if this block contains INSERT entities
        entities = block_data.get('entities', [])
        insert_entities = [e for e in entities if e.get('dxf_type') == 'INSERT']
        non_text_entities = [e for e in entities if e.get('dxf_type') not in ['TEXT', 'MTEXT', 'INSERT']]
        
        # If block has INSERT entities, check if referenced blocks are larger
        if insert_entities:
            # Get the largest referenced block size
            max_ref_width = 0
            max_ref_height = 0
            
            for insert in insert_entities:
                ref_block_name = insert.get('name')
                ref_block_key = ref_block_name.lower() if ref_block_name else None
                if ref_block_key and ref_block_key in block_sizes_lower:
                    actual_name, ref_block_size = block_sizes_lower[ref_block_key]
                else:
                    ref_block_size = block_sizes.get(ref_block_name)
                
                if ref_block_size:
                    max_ref_width = max(max_ref_width, ref_block_size['width'])
                    max_ref_height = max(max_ref_height, ref_block_size['height'])
            
            # If current block has calculated size, check if referenced block is significantly larger
            current_size = block_sizes.get(block_name, {'width': 300, 'height': 300})
            current_width = current_size['width']
            current_height = current_size['height']
            
            # Determine if we should use the INSERT reference instead of calculated geometry
            should_resolve = False
            
            # Case 1: No real geometry, only INSERT+TEXT (always resolve)
            if len(non_text_entities) == 0:
                should_resolve = True
            # Case 2: Current size is default or suspiciously small in BOTH dimensions
            elif (current_width == 300 and current_height == 300) or \
                 (current_width == 100 and current_height == 100) or \
                 (current_width < 200 and current_height < 200):
                # Only override if referenced block is much larger
                if max_ref_width > current_width * 2 or max_ref_height > current_height * 2:
                    should_resolve = True
            # Case 3: One dimension is very small (< 150mm) but referenced block is much larger
            elif (current_width < 150 or current_height < 150) and \
                 (max_ref_width > current_width * 3 and max_ref_height > current_height * 3):
                should_resolve = True
            
        # If block has INSERT and should be resolved, resolve from INSERT
        if insert_entities and should_resolve:
            # This block only contains references to other blocks
            min_x = min_y = float('inf')
            max_x = max_y = float('-inf')
            resolved = False
            
            for insert in insert_entities:
                ref_block_name = insert.get('name')
                
                # Try case-insensitive lookup
                ref_block_key = ref_block_name.lower() if ref_block_name else None
                if ref_block_key and ref_block_key in block_sizes_lower:
                    actual_name, ref_block_size = block_sizes_lower[ref_block_key]
                else:
                    ref_block_size = block_sizes.get(ref_block_name)
                
                if ref_block_size and ref_block_size['width'] != 300:
                    # Get the referenced block's size and position
                    insert_pos = insert.get('insert', [0, 0, 0])[:2]
                    
                    # Get scale factors (can be negative for mirroring)
                    xscale = insert.get('xscale', 1.0)
                    yscale = insert.get('yscale', 1.0)
                    
                    # Get referenced block's bounding box in its local coordinate system
                    ref_min_x = ref_block_size.get('min_x', 0)
                    ref_min_y = ref_block_size.get('min_y', 0)
                    ref_max_x = ref_block_size.get('max_x', ref_block_size['width'])
                    ref_max_y = ref_block_size.get('max_y', ref_block_size['height'])
                    
                    # Transform referenced block's bbox into parent block's coordinate system
                    # Handle mirroring: if scale is negative, the coordinates flip
                    if xscale < 0:
                        # X-axis mirrored: swap and negate X coordinates
                        world_min_x = insert_pos[0] + (-ref_max_x) * abs(xscale)
                        world_max_x = insert_pos[0] + (-ref_min_x) * abs(xscale)
                    else:
                        world_min_x = insert_pos[0] + ref_min_x * xscale
                        world_max_x = insert_pos[0] + ref_max_x * xscale
                    
                    if yscale < 0:
                        # Y-axis mirrored: swap and negate Y coordinates
                        world_min_y = insert_pos[1] + (-ref_max_y) * abs(yscale)
                        world_max_y = insert_pos[1] + (-ref_min_y) * abs(yscale)
                    else:
                        world_min_y = insert_pos[1] + ref_min_y * yscale
                        world_max_y = insert_pos[1] + ref_max_y * yscale
                    
                    # Expand parent block's bounding box
                    min_x = min(min_x, world_min_x, world_max_x)
                    max_x = max(max_x, world_min_x, world_max_x)
                    min_y = min(min_y, world_min_y, world_max_y)
                    max_y = max(max_y, world_min_y, world_max_y)
                    
                    resolved = True
            
            if resolved and min_x != float('inf'):
                width = abs(max_x - min_x)
                height = abs(max_y - min_y)
                
                # Check if we're overriding a previous calculation
                old_size = block_sizes.get(block_name)
                if old_size and old_size['width'] != 300:
                    print(f"   🔄 {block_name}: {old_size['width']:.1f} × {old_size['height']:.1f} mm → {width:.1f} × {height:.1f} mm (corrected from '{ref_block_name}')")
                else:
                    print(f"   🔗 {block_name}: {width:.1f} × {height:.1f} mm (resolved from '{ref_block_name}')")
                
                block_sizes[block_name] = {
                    'width': width,
                    'height': height,
                    'min_x': min_x,
                    'min_y': min_y,
                    'max_x': max_x,
                    'max_y': max_y
                }
                resolved_count += 1
    
    if resolved_count > 0:
        print(f"✅ Resolved {resolved_count} nested blocks")
    
    # NOTE: Pass 3 (bbox expansion) DISABLED - it was causing issues
    # Pass 2 already correctly resolves all nested blocks like MIRROR and CLINIC
    # clinic_regular is 2600×1700mm from its geometry, CLINIC_REGULAR_1 inherits this size
    # This matches how MIRROR works: mirror unit has geometry, MIRROR_DIFFERENT_1 inherits it
    
    return block_sizes



def extract_block_geometry(json_data):
    """
    Extract the actual geometry (lines, circles, arcs, etc.) from each block definition.
    This allows rendering real fixture shapes on canvas instead of PNG images.
    
    Returns:
        Dictionary mapping block_name -> list of geometry entities
    """
    block_geometries = {}
    
    for block_name, block_data in json_data.get('blocks', {}).items():
        geometry = []
        
        for entity in block_data.get('entities', []):
            entity_type = entity.get('dxf_type')
            
            if entity_type == 'LINE':
                geometry.append({
                    'type': 'LINE',
                    'start': entity.get('start', [0, 0])[:2],
                    'end': entity.get('end', [0, 0])[:2]
                })
            
            elif entity_type == 'CIRCLE':
                geometry.append({
                    'type': 'CIRCLE',
                    'center': entity.get('center', [0, 0])[:2],
                    'radius': entity.get('radius', 0)
                })
            
            elif entity_type == 'ARC':
                geometry.append({
                    'type': 'ARC',
                    'center': entity.get('center', [0, 0])[:2],
                    'radius': entity.get('radius', 0),
                    'start_angle': entity.get('start_angle', 0),
                    'end_angle': entity.get('end_angle', 360)
                })
            
            elif entity_type in ['LWPOLYLINE', 'POLYLINE']:
                points = entity.get('points', [])
                if points:
                    geometry.append({
                        'type': 'POLYLINE',
                        'points': [[p[0], p[1]] if len(p) > 1 else p for p in points],
                        'closed': entity.get('is_closed', False)
                    })
            
            elif entity_type == 'SPLINE':
                control_points = entity.get('control_points', [])
                fit_points = entity.get('fit_points', [])
                points = control_points if control_points else fit_points
                
                if points:
                    geometry.append({
                        'type': 'SPLINE',
                        'points': [[p[0], p[1]] if len(p) > 1 else p for p in points]
                    })
            
            elif entity_type == 'ELLIPSE':
                geometry.append({
                    'type': 'ELLIPSE',
                    'center': entity.get('center', [0, 0])[:2],
                    'major_axis': entity.get('major_axis', [1, 0])[:2],
                    'ratio': entity.get('ratio', 1.0)
                })
        
        if geometry:
            block_geometries[block_name] = geometry
    
    print(f"📦 Extracted geometry for {len(block_geometries)} blocks")
    return block_geometries


def extract_canvas_data(json_data, dxf_path=None):
    """
    Extract simplified canvas data from DXF JSON
    
    Args:
        json_data: Complete DXF JSON structure
        dxf_path: Optional path to DXF file for accurate size calculation
    
    Returns:
        Dictionary with fixtures and blueprint data
    """
    fixtures = []
    blueprint = []
    
    # Calculate fixture sizes from block definitions
    block_sizes = calculate_block_sizes(json_data, dxf_path)
    print(f"📐 Calculated sizes for {len(block_sizes)} blocks")
    
    # Extract block geometries for rendering real shapes
    block_geometries = extract_block_geometry(json_data)
    
    # Extract fixtures (INSERT entities)
    for entity in json_data.get('modelspace', []):
        if entity.get('dxf_type') == 'INSERT':
            block_name = entity['name']
            size = block_sizes.get(block_name, {'width': 300, 'height': 300, 'min_x': -150, 'min_y': -150, 'max_x': 150, 'max_y': 150})
            
            # Get the actual geometry for this block
            block_geometry = block_geometries.get(block_name, [])
            
            fixtures.append({
                'id': f"{entity['name']}@{entity['insert'][0]},{entity['insert'][1]}",
                'name': entity['name'],
                'position': entity['insert'][:2],  # X, Y only
                'rotation': entity.get('rotation', 0),
                'layer': entity.get('layer', '0'),
                'width': size['width'] * abs(entity.get('xscale', 1.0)),
                'height': size['height'] * abs(entity.get('yscale', 1.0)),
                'scale_x': entity.get('xscale', 1.0),  # Keep original sign for mirroring
                'scale_y': entity.get('yscale', 1.0),   # Keep original sign for mirroring
                'block_min_x': size.get('min_x', -size['width']/2),  # Block content offset from origin
                'block_min_y': size.get('min_y', -size['height']/2),  # Block content offset from origin
                'block_max_x': size.get('max_x', size['width']/2),
                'block_max_y': size.get('max_y', size['height']/2),
                'geometry': block_geometry  # Include actual DXF geometry
            })
        
        # Extract blueprint geometry (lines, polylines, etc.)
        elif entity.get('dxf_type') in ['LINE', 'LWPOLYLINE', 'POLYLINE', 'CIRCLE', 'ARC']:
            blueprint.append({
                'type': entity['dxf_type'],
                'data': extract_geometry_data(entity)
            })
    
    print(f"✅ Extracted {len(fixtures)} fixtures from modelspace")
    
    # Calculate bounds for auto-scaling
    bounds = calculate_bounds(fixtures, blueprint)
    
    return {
        'fixtures': fixtures,
        'blueprint': blueprint,
        'bounds': bounds,
        'fixture_count': len(fixtures)
    }


def extract_geometry_data(entity):
    """Extract geometry data for canvas rendering"""
    entity_type = entity['dxf_type']
    
    if entity_type == 'LINE':
        return {
            'start': entity['start'][:2],
            'end': entity['end'][:2]
        }
    
    elif entity_type == 'LWPOLYLINE' or entity_type == 'POLYLINE':
        return {
            'points': [p[:2] if len(p) > 2 else p for p in entity.get('points', [])],
            'closed': entity.get('closed', False)
        }
    
    elif entity_type == 'CIRCLE':
        return {
            'center': entity['center'][:2],
            'radius': entity['radius']
        }
    
    elif entity_type == 'ARC':
        return {
            'center': entity['center'][:2],
            'radius': entity['radius'],
            'start_angle': entity['start_angle'],
            'end_angle': entity['end_angle']
        }
    
    return {}


def calculate_bounds(fixtures, blueprint):
    """
    Calculate TWO sets of bounds:
    1. Display bounds: Include fixtures + blueprint (for canvas zoom)
    2. Validation bounds: Only room polylines (for fixture validation)
    """
    # First, get ROOM POLYLINE bounds (for validation)
    room_min_x = room_min_y = float('inf')
    room_max_x = room_max_y = float('-inf')
    
    entity_count = 0
    
    # ONLY use POLYLINES for room boundaries
    for entity in blueprint:
        entity_type = entity['type']
        data = entity['data']
        layer = entity.get('layer', 'UNKNOWN')
        
        if entity_type in ['LWPOLYLINE', 'POLYLINE']:
            points = data['points']
            if len(points) < 2:
                continue
                
            total_length = 0
            for i in range(len(points) - 1):
                p1, p2 = points[i], points[i+1]
                total_length += ((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)**0.5
            
            # Only use substantial room polylines (not tiny details or huge site plans)
            if total_length < 1000 or total_length > 30000:
                if entity_count == 0 and total_length > 30000:
                    print(f"   ⚠️ Skipping Polyline: Too long ({total_length:.0f}mm) - probably site boundary")
                continue
                
            for point in points:
                room_min_x = min(room_min_x, point[0])
                room_min_y = min(room_min_y, point[1])
                room_max_x = max(room_max_x, point[0])
                room_max_y = max(room_max_y, point[1])
            entity_count += 1
            if entity_count <= 3:
                print(f"   Room Polyline {entity_count}: Length={total_length:.0f}mm, Max Y={max(p[1] for p in points):.0f}")

    print(f"📐 Used {entity_count} POLYLINE entities for ROOM boundary")
    print(f"📐 ROOM BOUNDARIES (for validation):")
    print(f"   X: [{room_min_x:.0f}, {room_max_x:.0f}]")
    print(f"   Y: [{room_min_y:.0f}, {room_max_y:.0f}]")
    
    # Now calculate DISPLAY bounds (include all fixtures + blueprint)
    display_min_x = room_min_x if room_min_x != float('inf') else 0
    display_min_y = room_min_y if room_min_y != float('inf') else 0
    display_max_x = room_max_x if room_max_x != float('-inf') else 10000
    display_max_y = room_max_y if room_max_y != float('-inf') else 10000
    
    # Expand to include all fixtures (for canvas display)
    for fixture in fixtures:
        x, y = fixture['position']
        display_min_x = min(display_min_x, x - 500)
        display_min_y = min(display_min_y, y - 500)
        display_max_x = max(display_max_x, x + 500)
        display_max_y = max(display_max_y, y + 500)
    
    print(f"� DISPLAY BOUNDARIES (for canvas):")
    print(f"   X: [{display_min_x:.0f}, {display_max_x:.0f}]")
    print(f"   Y: [{display_min_y:.0f}, {display_max_y:.0f}]")

    # Add padding for display
    padding = 1000  # mm
    
    return {
        # Display bounds (for canvas zoom)
        'min_x': display_min_x,
        'min_y': display_min_y,
        'max_x': display_max_x,
        'max_y': display_max_y,
        'width': display_max_x - display_min_x + 2 * padding,
        'height': display_max_y - display_min_y + 2 * padding,
        # Room bounds (for validation) - stored separately
        'room_min_x': room_min_x if room_min_x != float('inf') else display_min_x,
        'room_max_x': room_max_x if room_max_x != float('-inf') else display_max_x,
        'room_min_y': room_min_y if room_min_y != float('inf') else display_min_y,
        'room_max_y': room_max_y if room_max_y != float('-inf') else display_max_y,
    }




def validate_and_correct_fixtures(modifications, bounds, all_fixtures):
    """
    STRICT validation: Check if fixture's BOUNDING BOX (all 4 corners) is inside floorplan.
    If ANY corner is outside → reject it with detailed message
    Uses ROOM bounds for validation
    """
    # Use room bounds for validation (not display bounds)
    min_x = bounds.get('room_min_x', bounds.get('min_x', 0))
    max_x = bounds.get('room_max_x', bounds.get('max_x', 10000))
    min_y = bounds.get('room_min_y', bounds.get('min_y', 0))
    max_y = bounds.get('room_max_y', bounds.get('max_y', 10000))
    
    print(f"\n🎯 Floorplan ROOM boundaries (strict validation):")
    print(f"   X: {min_x:.0f} to {max_x:.0f} mm (width: {max_x - min_x:.0f} mm)")
    print(f"   Y: {min_y:.0f} to {max_y:.0f} mm (height: {max_y - min_y:.0f} mm)")
    
    rejected = []
    rejected_details = []  # Store detailed rejection reasons
    valid_count = 0
    
    # Filter out fixtures that are outside boundaries
    valid_fixtures = []
    
    for mod in modifications.get('fixtures', []):
        fixture_name = mod.get('block_name', 'Unknown')
        new_pos = mod.get('new_position')
        
        if not new_pos:
            valid_fixtures.append(mod)
            continue
        
        x, y = new_pos[0], new_pos[1]
        
        # Get fixture dimensions from all_fixtures
        fixture_width = 300  # default
        fixture_height = 300  # default
        for f in all_fixtures:
            if f.get('name') == fixture_name:
                fixture_width = f.get('width', 300)
                fixture_height = f.get('height', 300)
                break
        
        # Calculate fixture's bounding box (all 4 corners)
        half_width = fixture_width / 2
        half_height = fixture_height / 2
        
        bbox_left = x - half_width
        bbox_right = x + half_width
        bbox_top = y + half_height
        bbox_bottom = y - half_height
        
        # Check if ALL corners are inside ROOM boundaries
        left_inside = bbox_left >= min_x
        right_inside = bbox_right <= max_x
        top_inside = bbox_top <= max_y
        bottom_inside = bbox_bottom >= min_y
        
        all_corners_inside = left_inside and right_inside and top_inside and bottom_inside
        
        if all_corners_inside:
            print(f"   ✅ {fixture_name}: center({x:.0f}, {y:.0f}) size[{fixture_width:.0f}×{fixture_height:.0f}mm]")
            print(f"      BBox: X[{bbox_left:.0f}, {bbox_right:.0f}] Y[{bbox_bottom:.0f}, {bbox_top:.0f}] - ALL CORNERS INSIDE")
            valid_fixtures.append(mod)
            valid_count += 1
        else:
            # Detailed rejection reason
            violations = []
            if not left_inside:
                violations.append(f"left edge {bbox_left:.0f} < room min {min_x:.0f}")
            if not right_inside:
                violations.append(f"right edge {bbox_right:.0f} > room max {max_x:.0f}")
            if not bottom_inside:
                violations.append(f"bottom edge {bbox_bottom:.0f} < room min {min_y:.0f}")
            if not top_inside:
                violations.append(f"top edge {bbox_top:.0f} > room max {max_y:.0f}")
            
            violation_msg = ", ".join(violations)
            
            print(f"   ❌ {fixture_name}: center({x:.0f}, {y:.0f}) size[{fixture_width:.0f}×{fixture_height:.0f}mm]")
            print(f"      BBox: X[{bbox_left:.0f}, {bbox_right:.0f}] Y[{bbox_bottom:.0f}, {bbox_top:.0f}]")
            print(f"      VIOLATION: {violation_msg}")
            
            rejected.append(fixture_name)
            rejected_details.append({
                'name': fixture_name,
                'center': [x, y],
                'size': [fixture_width, fixture_height],
                'bbox': {
                    'left': bbox_left,
                    'right': bbox_right,
                    'top': bbox_top,
                    'bottom': bbox_bottom
                },
                'violations': violations
            })
    
    # Update modifications to only include valid fixtures
    modifications['fixtures'] = valid_fixtures
    
    if rejected:
        print(f"\n⚠️  {len(rejected)} fixtures REJECTED (bounding box outside floorplan):")
        for detail in rejected_details:
            print(f"      - {detail['name']}: {', '.join(detail['violations'])}")
    
    return {
        'valid': valid_count,
        'rejected': len(rejected),
        'rejected_names': rejected,
        'rejected_details': rejected_details,  # Include detailed info for frontend warning
        'room_bounds': {
            'min_x': min_x,
            'max_x': max_x,
            'min_y': min_y,
            'max_y': max_y,
            'width': max_x - min_x,
            'height': max_y - min_y
        }
    }
def apply_ai_modifications(session_id, modifications):
    """
    Apply AI-generated modifications (MOVE, COPY, DELETE, ROTATE) directly to the DXF file
    Uses the same method as prompt-based model - modifies original DXF, doesn't recreate from JSON
    Also updates the session JSON data for canvas refresh
    Returns path to the modified DXF file
    """

    data = session_storage.get(session_id) or load_session(session_id)
    if not data:
        print(f"❌ Session {session_id} not found!")
        return None

    original_dxf = data['original_dxf']
    filename = data['filename']
    json_data = data['json_data']
    
    # Load the ORIGINAL DXF file (preserves format and version)
    print(f"📖 Loading original DXF: {original_dxf}")
    doc = ezdxf.readfile(original_dxf)
    msp = doc.modelspace()
    
    # Build a lookup of all INSERT entities by block name and position
    insert_entities = {}
    for entity in msp:
        if entity.dxftype() == 'INSERT':
            block_name = entity.dxf.name
            pos = entity.dxf.insert
            pos_key = f"{block_name}@{pos.x:.2f},{pos.y:.2f}"
            if block_name not in insert_entities:
                insert_entities[block_name] = []
            insert_entities[block_name].append({
                'entity': entity,
                'pos_key': pos_key,
                'pos': (pos.x, pos.y)
            })
    
    changes_made = 0
    
    for mod in modifications.get('fixtures', []):
        block_name = mod['block_name']
        operation = mod.get('operation', 'move').lower()
        orig_pos = mod.get('original_position')
        new_pos = mod.get('new_position')
        
        print(f"   📍 {operation.upper()}: {block_name}")
        
        if operation == 'delete':
            # Remove fixture(s) from modelspace
            entities_to_delete = []
            for entity in msp:
                if entity.dxftype() == 'INSERT' and entity.dxf.name == block_name:
                    if orig_pos:
                        pos = entity.dxf.insert
                        if abs(pos.x - orig_pos[0]) < 0.1 and abs(pos.y - orig_pos[1]) < 0.1:
                            entities_to_delete.append(entity)
                    else:
                        entities_to_delete.append(entity)
            
            for entity in entities_to_delete:
                msp.delete_entity(entity)
                changes_made += 1
                print(f"      ✅ Deleted {block_name}")
            
            # Also delete from JSON data for canvas update
            if orig_pos:
                json_data['modelspace'] = [
                    e for e in json_data.get('modelspace', [])
                    if not (e.get('dxf_type') == 'INSERT' and e.get('name') == block_name and
                           abs(e.get('insert', [0, 0])[0] - orig_pos[0]) < 0.1 and
                           abs(e.get('insert', [0, 0])[1] - orig_pos[1]) < 0.1)
                ]
            
        elif operation == 'copy':
            # Find original fixture and create a copy (with optional rotation)
            source_entity = None
            rotation_angle = mod.get('rotation', None)  # Get rotation if specified
            
            for entity in msp:
                if entity.dxftype() == 'INSERT' and entity.dxf.name == block_name:
                    if orig_pos and len(orig_pos) >= 2:
                        # Match by position if provided
                        pos = entity.dxf.insert
                        if abs(pos.x - orig_pos[0]) < 0.1 and abs(pos.y - orig_pos[1]) < 0.1:
                            source_entity = entity
                            break
                    else:
                        # Use first instance if no position specified
                        source_entity = entity
                        break
            
            if source_entity and new_pos and len(new_pos) >= 2:
                # Use specified rotation if provided, otherwise use source rotation
                copy_rotation = rotation_angle if rotation_angle is not None else source_entity.dxf.rotation
                
                # Create a copy with new position and rotation
                new_entity = msp.add_blockref(
                    block_name,
                    (new_pos[0], new_pos[1], source_entity.dxf.insert.z),
                    dxfattribs={
                        'layer': source_entity.dxf.layer,
                        'xscale': source_entity.dxf.xscale,
                        'yscale': source_entity.dxf.yscale,
                        'zscale': source_entity.dxf.zscale,
                        'rotation': copy_rotation,
                    }
                )
                changes_made += 1
                rotation_msg = f" with rotation {rotation_angle}°" if rotation_angle is not None else ""
                print(f"      ✅ Copied {block_name} to ({new_pos[0]:.1f}, {new_pos[1]:.1f}){rotation_msg}")
                
                # Also add to JSON data for canvas update
                for e in json_data.get('modelspace', []):
                    if e.get('dxf_type') == 'INSERT' and e.get('name') == block_name:
                        if orig_pos and len(orig_pos) >= 2:
                            pos = e.get('insert', [0, 0, 0])
                            if abs(pos[0] - orig_pos[0]) < 0.1 and abs(pos[1] - orig_pos[1]) < 0.1:
                                # Found source, create copy in JSON
                                new_json_entity = e.copy()
                                new_json_entity['insert'] = [new_pos[0], new_pos[1], pos[2] if len(pos) > 2 else 0]
                                if rotation_angle is not None:
                                    new_json_entity['rotation'] = rotation_angle
                                json_data.get('modelspace', []).append(new_json_entity)
                                break
            elif not source_entity:
                print(f"      ⚠️  Source fixture not found: {block_name}")
            elif not new_pos:
                print(f"      ⚠️  No target position provided for {block_name}")
            
        elif operation == 'move':
            # Update position of existing fixture (and rotation if specified)
            matched = False
            rotation_angle = mod.get('rotation', None)  # Get rotation if specified
            
            for entity in msp:
                if entity.dxftype() == 'INSERT' and entity.dxf.name == block_name:
                    if orig_pos and len(orig_pos) >= 2 and new_pos and len(new_pos) >= 2:
                        # Match by position
                        pos = entity.dxf.insert
                        print(f"      🔍 Checking {block_name}: DXF pos ({pos.x:.2f}, {pos.y:.2f}) vs requested orig ({orig_pos[0]:.2f}, {orig_pos[1]:.2f})")
                        if abs(pos.x - orig_pos[0]) < 0.1 and abs(pos.y - orig_pos[1]) < 0.1:
                            entity.dxf.insert = (new_pos[0], new_pos[1], pos.z)
                            
                            # Apply rotation if specified
                            if rotation_angle is not None:
                                entity.dxf.rotation = rotation_angle
                                print(f"      🔄 Setting rotation to {rotation_angle}°")
                            
                            changes_made += 1
                            matched = True
                            rotation_msg = f" with rotation {rotation_angle}°" if rotation_angle is not None else ""
                            print(f"      ✅ Moved {block_name} from ({pos.x:.1f}, {pos.y:.1f}) to ({new_pos[0]:.1f}, {new_pos[1]:.1f}){rotation_msg}")
                            
                            # Also update in JSON data for canvas update
                            for e in json_data.get('modelspace', []):
                                if e.get('dxf_type') == 'INSERT' and e.get('name') == block_name:
                                    e_pos = e.get('insert', [0, 0, 0])
                                    if abs(e_pos[0] - orig_pos[0]) < 0.1 and abs(e_pos[1] - orig_pos[1]) < 0.1:
                                        e['insert'] = [new_pos[0], new_pos[1], e_pos[2] if len(e_pos) > 2 else 0]
                                        if rotation_angle is not None:
                                            e['rotation'] = rotation_angle
                                        break
                            break
            
            if not matched:
                print(f"      ❌ Failed to find {block_name} at position ({orig_pos[0]:.2f}, {orig_pos[1]:.2f}) in DXF!")
        
        elif operation == 'rotate':
            # Rotate fixture by specified angle
            rotation_angle = mod.get('rotation', 0)
            
            for entity in msp:
                if entity.dxftype() == 'INSERT' and entity.dxf.name == block_name:
                    if orig_pos and len(orig_pos) >= 2:
                        # Match by position
                        pos = entity.dxf.insert
                        if abs(pos.x - orig_pos[0]) < 0.1 and abs(pos.y - orig_pos[1]) < 0.1:
                            # Get current rotation and add new angle
                            current_rotation = entity.dxf.rotation if hasattr(entity.dxf, 'rotation') else 0
                            entity.dxf.rotation = current_rotation + rotation_angle
                            changes_made += 1
                            print(f"      ✅ Rotated {block_name} by {rotation_angle}° (total: {entity.dxf.rotation:.1f}°)")
                            
                            # Also update in JSON data
                            for e in json_data.get('modelspace', []):
                                if e.get('dxf_type') == 'INSERT' and e.get('name') == block_name:
                                    e_pos = e.get('insert', [0, 0, 0])
                                    if abs(e_pos[0] - orig_pos[0]) < 0.1 and abs(e_pos[1] - orig_pos[1]) < 0.1:
                                        e['rotation'] = e.get('rotation', 0) + rotation_angle
                                        break
                            break
                    else:
                        # Rotate first instance if no position specified
                        current_rotation = entity.dxf.rotation if hasattr(entity.dxf, 'rotation') else 0
                        entity.dxf.rotation = current_rotation + rotation_angle
                        changes_made += 1
                        print(f"      ✅ Rotated {block_name} by {rotation_angle}° (total: {entity.dxf.rotation:.1f}°)")
                        
                        # Also update in JSON data
                        for e in json_data.get('modelspace', []):
                            if e.get('dxf_type') == 'INSERT' and e.get('name') == block_name:
                                e['rotation'] = e.get('rotation', 0) + rotation_angle
                                break
                        break
    
    if changes_made == 0:
        print(f"   ⚠️  No changes made")
        return None
    
    # Set R2018 + MM format (same as prompt-based model)
    doc.header['$INSUNITS'] = 4  # Millimeters
    doc.header['$MEASUREMENT'] = 1  # Metric
    
    # Generate output DXF
    base_name = os.path.splitext(filename)[0]
    output_filename = f"{base_name}-AI-MODIFIED.dxf"
    output_path = os.path.join(OUTPUT_FOLDER, f"{session_id}_{output_filename}")
    
    # Save (preserves original DXF version and format)
    print(f"💾 Saving modified DXF...")
    doc.saveas(output_path)
    
    # CRITICAL: Reload JSON from the modified DXF to get updated fixture positions
    # This allows subsequent AI requests to work with the new positions
    print(f"🔄 Reloading JSON from modified DXF...")
    updated_json_data = dxf_to_json(output_path)
    session_storage[session_id]['json_data'] = updated_json_data
    session_storage[session_id]['original_dxf'] = output_path  # Use modified file as new baseline
    save_session(session_id, session_storage[session_id])
    
    print(f"✅ Generated: {output_filename}")
    return output_path


def create_ai_prompt_from_movements(fixtures, movements, user_prompt):
    """Create Gemini AI prompt from canvas movements"""
    
    fixtures_json = json.dumps(fixtures, indent=2)
    
    # Convert movements to detailed format
    movement_details = []
    for m in movements:
        movement_details.append({
            'fixture_name': m['fixture'],
            'from_position': m['start'],
            'to_position': m['end'],
            'delta': m['delta'],
            'description': m['description']
        })
    
    movements_json = json.dumps(movement_details, indent=2)
    
    prompt = f"""You are a DXF fixture movement assistant. The user has moved fixtures on a canvas editor.

AVAILABLE FIXTURES IN DXF:
{fixtures_json}

USER MOVEMENTS:
{movements_json}

USER DESCRIPTION: "{user_prompt}"

Your task is to generate precise JSON modifications for these fixture movements.

RULES:
1. Match each moved fixture by name to the AVAILABLE FIXTURES list
2. Use the EXACT "name" field from AVAILABLE FIXTURES as "block_name"
3. Find the fixture with matching name and closest position to "from_position"
4. Use the exact "to_position" as the new_position
5. Round all coordinates to 2 decimal places

OUTPUT FORMAT (MUST BE VALID JSON ONLY):
{{
  "fixtures": [
    {{
      "block_name": "EXACT_FIXTURE_NAME",
      "original_position": [X, Y],
      "new_position": [NEW_X, NEW_Y]
    }}
  ]
}}

If you cannot match a fixture, output:
{{
  "error": "explanation of the problem"
}}

Generate ONLY the JSON, no other text."""
    
    return prompt


def apply_modifications_prompt_based(dxf_path, modifications, session_id):
    """Apply modifications to DXF using prompt-based model method (R2018 + MM)"""
    
    # Load original DXF
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    
    # Create fixture mapping
    original_fixtures = {}
    for entity in msp:
        if entity.dxftype() == 'INSERT':
            name = entity.dxf.name
            pos = (round(entity.dxf.insert.x, 2), round(entity.dxf.insert.y, 2))
            key = f'{name}@{pos[0]},{pos[1]}'
            
            if key not in original_fixtures:
                original_fixtures[key] = []
            original_fixtures[key].append(entity)
    
    # Apply modifications
    changes = []
    for mod in modifications.get('fixtures', []):
        block_name = mod['block_name']
        orig_pos = mod['original_position']
        new_pos = mod['new_position']
        
        orig_pos_key = (round(orig_pos[0], 2), round(orig_pos[1], 2))
        key = f'{block_name}@{orig_pos_key[0]},{orig_pos_key[1]}'
        
        if key in original_fixtures and original_fixtures[key]:
            fixture_to_update = original_fixtures[key].pop(0)
            new_pos_vec = ezdxf.math.Vec3(new_pos)
            old_pos = fixture_to_update.dxf.insert
            fixture_to_update.dxf.insert = new_pos_vec
            
            delta_x = new_pos_vec.x - old_pos.x
            delta_y = new_pos_vec.y - old_pos.y
            
            print(f'   ✅ Moved "{block_name}"')
            print(f'      From: X={old_pos.x:.2f}, Y={old_pos.y:.2f}')
            print(f'      To:   X={new_pos_vec.x:.2f}, Y={new_pos_vec.y:.2f}')
            print(f'      Delta: ΔX={delta_x:.2f}mm, ΔY={delta_y:.2f}mm')
            
            changes.append({
                'name': block_name,
                'from': {'x': old_pos.x, 'y': old_pos.y},
                'to': {'x': new_pos_vec.x, 'y': new_pos_vec.y},
                'delta': {'x': delta_x, 'y': delta_y}
            })
        else:
            print(f'   ⚠️  Fixture not found: {block_name} at {orig_pos_key}')
    
    # Set R2018 + MM format (same as prompt-based model)
    doc.header['$INSUNITS'] = 4  # Millimeters
    doc.header['$MEASUREMENT'] = 1  # Metric
    
    # Generate output filename
    output_filename = f"ai_modified_{session_id}.dxf"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    
    # Save
    doc.saveas(output_path)
    print(f'💾 Saved: {output_path}')
    
    return output_path, changes



def update_json_with_modification(session_id, modification):
    data = load_session(session_id)
    json_data = data['json_data']
    for mod in modification.get('fixtures', []):
        block_name = mod['block_name']
        orig_pos = mod['original_position']
        new_pos = mod['new_position']
        for entity in json_data.get('modelspace', []):
            if entity.get('dxf_type') == 'INSERT' and entity.get('name') == block_name:
                curr_pos = entity['insert'][:2]
                if abs(curr_pos[0] - orig_pos[0]) < 1.0: # Tolerance
                    entity['insert'] = [new_pos[0], new_pos[1], entity['insert'][2]]
    save_session(session_id, data)



def generate_with_ai_logic(session_id, user_prompt):
    """
    Migrated logic from Flask route /generate_with_ai
    """
    try:
        if not session_exists(session_id):
            return {'success': False, 'error': 'Invalid session'}

        # Load session
        session_data = load_session(session_id)
        
        # Ensure session is in memory for apply_ai_modifications
        if session_id not in session_storage:
            session_storage[session_id] = session_data
        
        # Initialize Gemini
        GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Get data for AI context
        original_dxf = session_data['original_dxf']
        json_data = session_data['json_data']
        canvas_data = extract_canvas_data(json_data, original_dxf)
        floorplan_bounds = canvas_data.get('bounds', {})
        
        # Build the AI prompt (simplified for brevity, use your full prompt logic here)
        fixtures_with_pos = [
            f"{f['name']} at ({f['position'][0]:.1f}, {f['position'][1]:.1f})" 
            for f in canvas_data.get('fixtures', [])
        ]
        
        # Check if validation is needed
        architect_keywords = ['rearrange', 'architect', 'organize', 'layout']
        needs_validation = any(k in user_prompt.lower() for k in architect_keywords)

        # Create AI prompt - You can paste your massive prompt string here
        ai_prompt = f"""
        You are a DXF fixture modification assistant. 
        Available fixtures: {chr(10).join(fixtures_with_pos)}
        User Command: {user_prompt}
        Output ONLY valid JSON in the format: {{"fixtures": [{{"block_name": "name", "operation": "move", "original_position": [x,y], "new_position": [x,y]}}]}}
        """

        # Call Gemini
        response = model.generate_content(ai_prompt)
        response_text = response.text.strip().replace('```json', '').replace('```', '')
        
        modifications = json.loads(response_text)

        # Validation Layer
        validation_results = {}
        if needs_validation:
            validation_results = validate_and_correct_fixtures(
                modifications, 
                floorplan_bounds, 
                canvas_data.get('fixtures', [])
            )

        # Apply modifications to DXF
        output_path = apply_ai_modifications(session_id, modifications)
        
        if not output_path:
            return {
                'success': True,
                'warning': 'No changes were made. Please check fixture names.',
                'operations': {'moved': 0}
            }

        # Count operations for response
        moved_count = len(modifications.get('fixtures', []))
        
        # Reload updated canvas data
        updated_canvas_data = extract_canvas_data(load_session(session_id)['json_data'], output_path)

        return {
            'success': True,
            'message': f"✅ Processed {moved_count} operations",
            'updated_canvas_data': updated_canvas_data,
            'validation_results': validation_results
        }

    except Exception as e:
        print(f"❌ AI Logic Error: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def apply_modifications_to_dxf(dxf_path, fixtures, session_id):
    """
    Apply fixture modifications to DXF file for enhanced AI pipeline.
    
    Args:
        dxf_path: Path to original DXF file
        fixtures: List of fixture modifications from AI/math model
        session_id: Session identifier
        
    Returns:
        Path to modified DXF file
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Load the DXF file
        logger.info(f"Loading DXF file: {dxf_path}")
        print(f"\n📂 Loading DXF file: {dxf_path}")
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()
        
        # DEBUG: List all INSERT entities to understand what's available
        all_inserts = [e for e in msp if e.dxftype() == 'INSERT']
        logger.info(f"Found {len(all_inserts)} INSERT entities in DXF")
        print(f"📊 Found {len(all_inserts)} INSERT entities in DXF")
        
        # Get unique block names for debugging
        unique_blocks = sorted(set(e.dxf.name for e in all_inserts))
        logger.info(f"Unique block names in DXF: {unique_blocks}")
        print(f"📋 ALL block names in DXF ({len(unique_blocks)} unique):")
        for i, name in enumerate(unique_blocks):
            print(f"   {i+1:2d}. {name}")
        
        # Show what we're trying to modify
        print(f"\n🎯 Attempting to modify {len(fixtures)} fixtures:")
        for f in fixtures:
            print(f"   - {f.get('block_name')} -> {f.get('new_position')}")
        
        changes_made = 0
        
        for fixture in fixtures:
            block_name = fixture.get('block_name')
            new_position = fixture.get('new_position')
            rotation = fixture.get('rotation', 0.0)
            action = fixture.get('action', 'move')
            
            if not block_name:
                continue
            
            logger.info(f"Processing {action} for {block_name} at position {new_position}")
            
            if action == 'remove' or action == 'delete':
                # Remove fixture from modelspace
                entities_to_delete = []
                for entity in msp:
                    if entity.dxftype() == 'INSERT' and entity.dxf.name == block_name:
                        entities_to_delete.append(entity)
                
                for entity in entities_to_delete:
                    msp.delete_entity(entity)
                    changes_made += 1
                    logger.info(f"Deleted fixture: {block_name}")
                    
            elif new_position and len(new_position) >= 2:
                # Move/update fixture position
                original_position = fixture.get('original_position')
                
                print(f"\n🔍 Searching for {block_name}:")
                print(f"   Original pos: {original_position}")
                print(f"   Target pos: {new_position}")
                
                # Find and update the fixture (case-insensitive matching)
                fixture_found = False
                block_name_upper = block_name.upper()
                candidates_found = []
                
                for entity in msp:
                    if entity.dxftype() == 'INSERT':
                        entity_name_upper = entity.dxf.name.upper()
                        
                        # Match block names (case-insensitive)
                        if entity_name_upper == block_name_upper:
                            pos = entity.dxf.insert
                            candidates_found.append((entity.dxf.name, [pos.x, pos.y]))
                            
                            # If original position specified, match it
                            if original_position:
                                dist = abs(pos.x - original_position[0]) + abs(pos.y - original_position[1])
                                print(f"   Found candidate at [{pos.x:.1f}, {pos.y:.1f}], distance from original: {dist:.1f}mm")
                                
                                if abs(pos.x - original_position[0]) < 1.0 and abs(pos.y - original_position[1]) < 1.0:
                                    entity.dxf.insert = (new_position[0], new_position[1], pos.z)
                                    if rotation != 0:
                                        entity.dxf.rotation = rotation
                                    changes_made += 1
                                    fixture_found = True
                                    print(f"   ✅ Moved {entity.dxf.name} from {[pos.x, pos.y]} to {new_position}")
                                    break
                            else:
                                # Move first instance found (no original position check)
                                old_pos = [pos.x, pos.y]
                                entity.dxf.insert = (new_position[0], new_position[1], pos.z)
                                if rotation != 0:
                                    entity.dxf.rotation = rotation
                                changes_made += 1
                                fixture_found = True
                                print(f"   ✅ Moved {entity.dxf.name} from {old_pos} to {new_position}")
                                break
                
                if not fixture_found:
                    logger.warning(f"Fixture not found: {block_name}")
                    print(f"   ❌ Could not match fixture: {block_name}")
                    if candidates_found:
                        print(f"   📍 Candidates found: {candidates_found}")
        
        # Save modified DXF
        output_filename = f"{session_id}_modified.dxf"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        doc.saveas(output_path)
        
        logger.info(f"Saved modified DXF to: {output_path} ({changes_made} changes)")
        print(f"\n💾 Saved modified DXF: {output_path} ({changes_made} changes made)")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error applying modifications to DXF: {e}", exc_info=True)
        return None