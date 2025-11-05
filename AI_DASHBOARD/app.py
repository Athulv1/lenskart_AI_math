#!/usr/bin/env python3
"""
Canvas-Based DXF Fixture Mover - Flask Web Application
=======================================================

A web-based interface for moving fixtures in DXF files using:
- HTML5 Canvas for visual display
- Drag-and-drop mouse interaction
- Gemini AI for automatic JSON updates
- Real-time coordinate tracking

Author: GitHub Copilot
Version: 1.0
"""

from flask import Flask, render_template, request, jsonify, send_file, session
from flask_cors import CORS
import os
import json
import uuid
import requests
from werkzeug.utils import secure_filename
import ezdxf
from enhanced_dxf_to_json import dxf_to_json, json_to_dxf
from ai_fixture_mover import AIFixtureMover

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Store session data (use Redis/DB in production)
session_storage = {}

# Gemini AI configuration
GEMINI_API_KEY = "AIzaSyDYivSaB99eiXW__eYF_WprJsa8qCZGQ2M"


@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')


@app.route('/canvas')
def canvas():
    """Canvas editor page"""
    return render_template('canvas.html')


@app.route('/upload-from-url', methods=['POST'])
def upload_from_url():
    """
    Handle DXF file upload from a URL (e.g., from Django)
    
    Expects JSON: { "url": "<Django server URL>/media/..." }
    Works for both localhost and production server URLs.
    
    Returns:
        JSON with session_id and canvas_data
    """
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        print(f"📥 Fetching DXF from URL: {url}")
        
        # Fetch the file from the URL
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Extract filename from URL
        filename = url.split('/')[-1]
        if not filename.lower().endswith('.dxf'):
            filename = f"{filename}.dxf"
        
        filename = secure_filename(filename)
        
        # Save the file
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        with open(upload_path, 'wb') as f:
            f.write(response.content)
        
        print(f"📁 Saved from URL: {filename} → {session_id}")
        
        # Convert DXF to JSON
        print(f"🔄 Converting DXF to JSON...")
        json_data = dxf_to_json(upload_path)
        
        # Store in session
        session_storage[session_id] = {
            'original_dxf': upload_path,
            'filename': filename,
            'json_data': json_data,
            'modifications': []
        }
        
        # Extract canvas data
        canvas_data = extract_canvas_data(json_data, upload_path)
        
        print(f"✅ Ready! Session: {session_id}")
        print(f"   Fixtures: {len(canvas_data['fixtures'])}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'filename': filename,
            'canvas_data': canvas_data
        })
    
    except requests.RequestException as e:
        print(f"❌ URL fetch error: {e}")
        return jsonify({'error': f'Failed to fetch file from URL: {str(e)}'}), 500
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/upload', methods=['POST'])
def upload_dxf():
    """
    Handle DXF file upload
    
    Returns:
        JSON with session_id and canvas_data
    """
    try:
        # Check if file was uploaded
        if 'dxf_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['dxf_file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.dxf'):
            return jsonify({'error': 'File must be a DXF file'}), 400
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        file.save(upload_path)
        
        print(f"📁 Uploaded: {filename} → {session_id}")
        
        # Convert DXF to JSON
        print(f"🔄 Converting DXF to JSON...")
        json_data = dxf_to_json(upload_path)
        
        # Debug: Check JSON structure
        print(f"📋 JSON keys: {list(json_data.keys())}")
        print(f"   Blocks: {len(json_data.get('blocks', {}))} definitions")
        print(f"   Modelspace: {len(json_data.get('modelspace', []))} entities")
        
        # Store in session
        session_storage[session_id] = {
            'original_dxf': upload_path,
            'filename': filename,
            'json_data': json_data,
            'modifications': []
        }
        
        # Extract canvas data (fixtures and blueprint) - pass DXF path for accurate sizing
        canvas_data = extract_canvas_data(json_data, upload_path)
        
        print(f"✅ Ready! Session: {session_id}")
        print(f"   Fixtures: {len(canvas_data['fixtures'])}")
        print(f"   Blueprint entities: {len(canvas_data['blueprint'])}")
        
        # Debug: Show first few fixtures with sizes
        if canvas_data['fixtures']:
            print(f"\n📐 Sample fixture sizes:")
            for fixture in canvas_data['fixtures'][:3]:
                print(f"   • {fixture['name']}: {fixture.get('width', 'N/A')} × {fixture.get('height', 'N/A')} mm")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'filename': filename,
            'canvas_data': canvas_data
        })
    
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


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


@app.route('/move_fixture', methods=['POST'])
def move_fixture():
    """
    Process fixture movement with Gemini AI
    
    Expects JSON:
    {
        "session_id": "...",
        "fixture_id": "...",
        "fixture_name": "...",
        "start_position": [x, y],
        "end_position": [x, y],
        "delta": [dx, dy]
    }
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if session_id not in session_storage:
            return jsonify({'error': 'Invalid session'}), 400
        
        fixture_name = data.get('fixture_name')
        start_pos = data.get('start_position')
        end_pos = data.get('end_position')
        delta = data.get('delta')
        
        print(f"\n🔧 Moving fixture:")
        print(f"   Name: {fixture_name}")
        print(f"   From: ({start_pos[0]:.2f}, {start_pos[1]:.2f})")
        print(f"   To:   ({end_pos[0]:.2f}, {end_pos[1]:.2f})")
        print(f"   Delta: ({delta[0]:.2f}, {delta[1]:.2f})")
        
        # Use Gemini AI to generate modification
        ai_mover = AIFixtureMover(GEMINI_API_KEY)
        
        # Create prompt for Gemini
        prompt = f"""
        Generate a fixture modification in JSON format.
        
        Fixture to move:
        - Name: {fixture_name}
        - Original position: {start_pos}
        - New position: {end_pos}
        
        Output ONLY valid JSON in this exact format:
        {{
          "fixtures": [
            {{
              "block_name": "{fixture_name}",
              "original_position": {start_pos},
              "new_position": {end_pos}
            }}
          ]
        }}
        """
        
        print(f"🤖 Calling Gemini AI...")
        
        # Call Gemini API
        try:
            response = ai_mover.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean response
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1])
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            
            modification = json.loads(response_text)
            
            print(f"✅ AI generated modification")
            
        except Exception as e:
            print(f"⚠️  AI failed, using direct modification: {e}")
            # Fallback: create modification manually
            modification = {
                "fixtures": [{
                    "block_name": fixture_name,
                    "original_position": start_pos,
                    "new_position": end_pos
                }]
            }
        
        # Store modification
        session_storage[session_id]['modifications'].append(modification)
        
        # Update JSON data
        update_json_with_modification(session_id, modification)
        
        return jsonify({
            'success': True,
            'modification': modification
        })
    
    except Exception as e:
        print(f"❌ Move error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def update_json_with_modification(session_id, modification):
    """Update the stored JSON data with the modification"""
    json_data = session_storage[session_id]['json_data']
    
    for mod in modification.get('fixtures', []):
        block_name = mod['block_name']
        orig_pos = mod['original_position']
        new_pos = mod['new_position']
        
        # Find and update the fixture in modelspace
        for entity in json_data.get('modelspace', []):
            if entity['dxf_type'] == 'INSERT' and entity['name'] == block_name:
                # Check if position matches (with tolerance)
                current_pos = entity['insert'][:2]
                if (abs(current_pos[0] - orig_pos[0]) < 0.1 and 
                    abs(current_pos[1] - orig_pos[1]) < 0.1):
                    # Update position
                    entity['insert'] = [new_pos[0], new_pos[1], entity['insert'][2]]
                    print(f"   ✅ Updated {block_name} in JSON")
                    break


@app.route('/rotate_fixture', methods=['POST'])
def rotate_fixture():
    """
    Rotate a fixture to a specific angle
    
    Expects JSON:
    {
        "session_id": "...",
        "fixture_name": "...",
        "rotation": 90  // New rotation angle in degrees
    }
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if session_id not in session_storage:
            return jsonify({'error': 'Invalid session'}), 400
        
        fixture_name = data.get('fixture_name')
        new_rotation = data.get('rotation', 0)
        
        print(f"\n🔄 Rotating fixture:")
        print(f"   Name: {fixture_name}")
        print(f"   New Rotation: {new_rotation}°")
        
        # Load the current DXF file
        original_dxf = session_storage[session_id]['original_dxf']
        json_data = session_storage[session_id]['json_data']
        
        # Update rotation in the DXF file
        doc = ezdxf.readfile(original_dxf)
        msp = doc.modelspace()
        
        # Find and update the fixture
        updated = False
        for entity in msp:
            if entity.dxftype() == 'INSERT' and entity.dxf.name == fixture_name:
                entity.dxf.rotation = new_rotation
                updated = True
                print(f"   ✅ Updated rotation in DXF")
                break
        
        if not updated:
            return jsonify({'success': False, 'error': 'Fixture not found'}), 404
        
        # Save the modified DXF
        doc.saveas(original_dxf)
        
        # Also update in JSON data
        for entity in json_data.get('modelspace', []):
            if entity.get('name') == fixture_name:
                entity['rotation'] = new_rotation
                print(f"   ✅ Updated rotation in JSON")
                break
        
        return jsonify({
            'success': True,
            'message': f'Rotated {fixture_name} to {new_rotation}°'
        })
        
    except Exception as e:
        print(f"❌ Error rotating fixture: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/generate_with_ai', methods=['POST'])
def generate_with_ai():
    """
    Process user-edited prompt with Gemini AI (supports move, copy, delete operations)
    
    Expects JSON:
    {
        "session_id": "...",
        "prompt": "User's edited prompt text (e.g., 'Copy VC_FIXTURE_1 to position 1500, 2000')"
    }
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if session_id not in session_storage:
            return jsonify({'error': 'Invalid session'}), 400
        
        user_prompt = data.get('prompt', '').strip()
        
        if not user_prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        print(f"\n🤖 AI Generation Request:")
        print(f"   Session: {session_id}")
        print(f"   User Prompt: {user_prompt}")
        
        # Check if this is an "architect rearrange" request (requires validation)
        # vs manual customer movement (no validation needed - customer knows what they want)
        architect_keywords = ['rearrange like an architect', 'arrange like an architect', 'organize like an architect',
                             'layout like an architect', 'architect layout', 'architect arrangement',
                             'rearrange these fixtures', 'rearrange fixtures']  # Add more patterns
        
        print(f"🔍 Checking user_prompt for architect keywords...")
        print(f"   User prompt (first 200 chars): '{user_prompt[:200]}'")
        
        needs_validation = any(keyword.lower() in user_prompt.lower() for keyword in architect_keywords)
        
        if needs_validation:
            print(f"   🏗️ Architect mode: Validation ENABLED")
        else:
            print(f"   ✋ Manual mode: Validation DISABLED (customer-approved movements)")
        
        # Get DXF path and JSON data from session
        original_dxf = session_storage[session_id]['original_dxf']
        json_data = session_storage[session_id]['json_data']
        
        # Extract full canvas data including bounds and fixture sizes
        canvas_data = extract_canvas_data(json_data, original_dxf)
        floorplan_bounds = canvas_data.get('bounds', {})
        print(f"📐 Extracted floorplan bounds: min_x={floorplan_bounds.get('min_x')}, max_x={floorplan_bounds.get('max_x')}, min_y={floorplan_bounds.get('min_y')}, max_y={floorplan_bounds.get('max_y')}")
        
        # Extract ROOM bounds for validation (separate from display bounds)
        room_min_x = floorplan_bounds.get('room_min_x', floorplan_bounds.get('min_x', 0))
        room_max_x = floorplan_bounds.get('room_max_x', floorplan_bounds.get('max_x', 10000))
        room_min_y = floorplan_bounds.get('room_min_y', floorplan_bounds.get('min_y', 0))
        room_max_y = floorplan_bounds.get('room_max_y', floorplan_bounds.get('max_y', 10000))
        
        # Get all fixtures from the current DXF with their sizes
        all_fixtures = []
        fixtures_with_sizes = {}  # For overlap checking
        for fixture in canvas_data.get('fixtures', []):
            all_fixtures.append({
                'name': fixture['name'],
                'position': fixture['position'],
                'rotation': fixture.get('rotation', 0),
                'layer': fixture.get('layer', '0'),
                'width': fixture.get('width', 300),
                'height': fixture.get('height', 300)
            })
            # Store for overlap checking
            fixtures_with_sizes[fixture['name']] = {
                'x': fixture['position'][0],
                'y': fixture['position'][1],
                'width': fixture.get('width', 300),
                'height': fixture.get('height', 300)
            }
        
        # Parse selected fixtures from user prompt (if any)
        selected_fixture_names = []
        if 'Selected fixtures:' in user_prompt:
            # Extract fixture names from "Selected fixtures: X, Y, Z" line
            selected_line = user_prompt.split('\n')[0]
            if 'Selected fixtures:' in selected_line:
                # Get everything after "Selected fixtures:" and before any other text
                fixtures_str = selected_line.split('Selected fixtures:')[1].strip()
                # Split by comma and clean each name - stop at first non-fixture text
                raw_names = [name.strip() for name in fixtures_str.split(',')]
                # Filter out any text that contains full sentences or extra instructions
                selected_fixture_names = []
                for name in raw_names:
                    # Stop if we hit descriptive text (contains spaces beyond fixture naming)
                    words = name.split()
                    if len(words) > 2 or any(keyword in name.lower() for keyword in ['rearrange', 'move', 'like', 'architect', 'these', 'fixtures']):
                        # Take only the first part before the extra text
                        selected_fixture_names.append(words[0] if words else name)
                        break
                    selected_fixture_names.append(name)
                print(f"📌 User selected {len(selected_fixture_names)} fixtures: {selected_fixture_names}")
        
        # Load professional architectural rearrangement prompt
        prompt_file_path = os.path.join(os.path.dirname(__file__), 'prompt_for_rearrange.txt')
        professional_prompt = ""
        try:
            with open(prompt_file_path, 'r', encoding='utf-8') as f:
                professional_prompt = f.read()
            print(f"✅ Loaded professional prompt: {len(professional_prompt)} chars")
        except FileNotFoundError:
            professional_prompt = ""  # Fallback if file not found
            print(f"⚠️ Warning: prompt_for_rearrange.txt not found at {prompt_file_path}")
        
        # Create comprehensive AI prompt that understands MOVE, COPY, DELETE, ROTATE, and REARRANGE
        # Include ALL fixture positions (not just first 20) for Gemini to find them
        fixtures_with_pos = [
            f"{f['name']} at ({f['position'][0]:.1f}, {f['position'][1]:.1f})" 
            for f in all_fixtures  # Send ALL fixtures, not just [:20]
        ]
        
        # Check if this is a rearrangement command (user selected multiple fixtures + rearrange keywords)
        is_rearrangement = ('rearrange' in user_prompt.lower() or 'organize' in user_prompt.lower() or 
                           'layout' in user_prompt.lower() or 'architect' in user_prompt.lower()) and len(selected_fixture_names) > 1
        print(f"🔍 Rearrangement detection: is_rearrangement={is_rearrangement}, selected={len(selected_fixture_names)} fixtures, has_prompt={len(professional_prompt) > 0}")
        
        # Build additional context for Gemini if fixtures are selected
        selection_context = ""
        if selected_fixture_names:
            selection_context = f"""

⚠️ CRITICAL: The user has selected {len(selected_fixture_names)} fixtures that MUST ALL be moved:
{chr(10).join([f"  {i+1}. {name}" for i, name in enumerate(selected_fixture_names)])}

YOU MUST generate exactly {len(selected_fixture_names)} move operations - one for EACH fixture listed above.
Do NOT skip any fixtures. Do NOT move only some of them.
EVERY fixture in the list must appear in your JSON output.
"""
        
        # Build the AI prompt based on whether it's a rearrangement or simple operation
        if is_rearrangement and professional_prompt and selected_fixture_names:
            print(f"✅ Using PROFESSIONAL ARCHITECTURAL PROMPT with boundaries and overlap prevention")
            # Build detailed fixture list with sizes for selected fixtures
            selected_fixtures_details = []
            non_selected_fixtures = []
            for f in all_fixtures:
                fixture_info = f"  - {f['name']} at ({f['position'][0]:.1f}, {f['position'][1]:.1f}) [Size: {f['width']:.0f}×{f['height']:.0f}mm]"
                if f['name'] in selected_fixture_names:
                    selected_fixtures_details.append(fixture_info)
                else:
                    non_selected_fixtures.append(fixture_info)
            
            # Use professional architectural prompt for rearrangements
            ai_prompt = f"""{professional_prompt}

===========================================
CURRENT TASK: PROFESSIONAL REARRANGEMENT
===========================================

⚠️ CRITICAL FLOORPLAN BOUNDARIES (DO NOT PLACE FIXTURES OUTSIDE):
- Minimum X: {room_min_x:.1f} mm
- Maximum X: {room_max_x:.1f} mm
- Minimum Y: {room_min_y:.1f} mm  
- Maximum Y: {room_max_y:.1f} mm
- Floorplan Width: {room_max_x - room_min_x:.1f} mm
- Floorplan Height: {room_max_y - room_min_y:.1f} mm

� ABSOLUTE BOUNDARY ENFORCEMENT RULES:
1. For EVERY fixture you place, you MUST verify:
   - fixture_position_x - (fixture_width/2) >= {room_min_x:.1f}
   - fixture_position_x + (fixture_width/2) <= {room_max_x:.1f}
   - fixture_position_y - (fixture_height/2) >= {room_min_y:.1f}
   - fixture_position_y + (fixture_height/2) <= {room_max_y:.1f}

2. If ANY edge would go outside these boundaries:
   - MOVE the fixture towards the center
   - NEVER place it at that position
   - Keep trying until it fits

3. Add 200mm safety margin from walls:
   - Effective min_x = {room_min_x + 200:.1f}
   - Effective max_x = {room_max_x - 200:.1f}
   - Effective min_y = {room_min_y + 200:.1f}
   - Effective max_y = {room_max_y - 200:.1f}

�📍 SELECTED FIXTURES TO REARRANGE ({len(selected_fixture_names)} fixtures):
{chr(10).join(selected_fixtures_details)}

⚠️ EXISTING FIXTURES (DO NOT OVERLAP - THESE STAY IN PLACE):
{chr(10).join(non_selected_fixtures[:20])}
{'... and ' + str(len(non_selected_fixtures) - 20) + ' more fixtures' if len(non_selected_fixtures) > 20 else ''}

USER REQUEST:
{user_prompt}

YOUR CRITICAL TASKS:
1. Analyze the {len(selected_fixture_names)} selected fixtures and their current positions
2. Check existing fixture positions to AVOID OVERLAPS
3. Ensure ALL new positions are WITHIN floorplan boundaries
4. Apply architectural principles: proper clearances (800-1200mm), circulation paths, grid patterns
5. Generate ONE MOVE operation for EACH selected fixture
6. Account for fixture sizes when calculating clearances:
   - Minimum 800mm clearance between fixture edges
   - Keep fixtures at least 200mm from walls
   - Maintain clear circulation aisles (1200mm minimum)

OVERLAP PREVENTION RULES:
- Before placing at (new_x, new_y), check distance to ALL existing fixtures
- For each existing fixture at (ex, ey) with size (ew, eh):
  * Calculate center-to-center distance: sqrt((new_x - ex)² + (new_y - ey)²)
  * Required minimum distance: (fixture_width + ew)/2 + (fixture_height + eh)/2 + 800mm clearance
- If overlap detected, shift position by 1000-2000mm to find free space

BOUNDARY VALIDATION:
- new_x must be between {room_min_x:.1f} and {room_max_x:.1f}
- new_y must be between {room_min_y:.1f} and {room_max_y:.1f}
- Account for fixture half-width and half-height when placing near edges

REQUIRED OUTPUT FORMAT (ONLY VALID JSON):
{{
  "fixtures": [
    {{
      "block_name": "EXACT_FIXTURE_NAME",
      "operation": "move",
      "original_position": [current_x, current_y],
      "new_position": [new_x_within_bounds, new_y_within_bounds],
      "reason": "Brief architectural explanation"
    }}
  ]
}}

Generate exactly {len(selected_fixture_names)} operations now. NO MARKDOWN, ONLY JSON."""
            # Log the ROOM boundaries being sent (not display bounds)
            print(f"📏 Floorplan ROOM boundaries being sent to Gemini:")
            print(f"   X range: {floorplan_bounds.get('room_min_x', room_min_x):.1f} to {floorplan_bounds.get('room_max_x', room_max_x):.1f} mm")
            print(f"   Y range: {floorplan_bounds.get('room_min_y', room_min_y):.1f} to {floorplan_bounds.get('room_max_y', room_max_y):.1f} mm")
        else:
            print(f"⚠️ Using BASIC PROMPT (not a rearrangement or missing components)")
            # Use basic prompt for simple move/copy/delete/rotate operations
            ai_prompt = f"""You are a DXF fixture modification assistant. Parse the user's command and generate the appropriate JSON modifications.

⚠️ CRITICAL FLOORPLAN BOUNDARIES (DO NOT PLACE FIXTURES OUTSIDE):
- Minimum X: {room_min_x:.1f} mm
- Maximum X: {room_max_x:.1f} mm
- Minimum Y: {room_min_y:.1f} mm  
- Maximum Y: {room_max_y:.1f} mm

🚨 BOUNDARY VALIDATION REQUIRED:
Before outputting ANY position, verify:
  - new_x - (fixture_width/2) >= {room_min_x:.1f}
  - new_x + (fixture_width/2) <= {room_max_x:.1f}
  - new_y - (fixture_height/2) >= {room_min_y:.1f}
  - new_y + (fixture_height/2) <= {room_max_y:.1f}

If ANY edge goes outside: REJECT that position and calculate a new one within bounds.

Available fixtures in the DXF file (with current positions):
{chr(10).join(fixtures_with_pos)}
{selection_context}
User's Command:
{user_prompt}

IMPORTANT Instructions:
1. Commands can be: MOVE, COPY, DELETE, ROTATE, or REARRANGE multiple fixtures
2. When the command includes "to position (X, Y)" - use those EXACT coordinates as new_position
3. When the command says "500mm right" - add 500 to the X coordinate
4. When the command says "500mm left" - subtract 500 from the X coordinate  
5. When the command says "500mm up" - add 500 to the Y coordinate
6. When the command says "500mm down" - subtract 500 from the Y coordinate
7. For ROTATE: Extract rotation angle in degrees (e.g., "rotate 90 degrees", "rotate by 45")
8. For REARRANGE: YOU MUST move ALL fixtures listed in "Selected fixtures:" line
   - Parse the comma-separated fixture names from the first line
   - Create ONE move operation for EACH fixture name in that list
   - Find their current positions from the fixtures list above
   - Calculate non-overlapping new positions
9. ALWAYS include original_position from the fixtures list above

Output JSON format (REQUIRED):
{{
  "fixtures": [
    {{
      "block_name": "EXACT_FIXTURE_NAME_FROM_LIST",
      "operation": "move|copy|delete|rotate",
      "original_position": [current_x, current_y],
      "new_position": [new_x, new_y],
      "rotation": 90  // Only for rotate operation, angle in degrees
    }}
  ]
}}

Examples:
- "Move X to position (1500, 2000)" = operation: "move", new_position: [1500, 2000]
- "Copy X 500mm right" = operation: "copy", calculate new_position from original + 500 in X
- "Delete X" = operation: "delete", no new_position needed
- "Rotate X 90 degrees" = operation: "rotate", rotation: 90, keep same position
- "Rearrange VC_FIXTURE_1, VC_FIXTURE_2, VC_FIXTURE_3 like an architect" = 
  Generate multiple move operations with intelligent positioning

CRITICAL FOR REARRANGEMENT:
- The user selected these specific fixtures (listed in "Selected fixtures:" line)
- YOU MUST create a move operation for EVERY fixture name in that comma-separated list
- Count the fixture names in "Selected fixtures:" and generate EXACTLY that many operations
- Look up each fixture's current position from the "Available fixtures" list above
- Calculate non-overlapping positions for ALL selected fixtures
- Use operation: "move" for each fixture in the selection
- Space fixtures appropriately (min 500-800mm between centers)
- Create aesthetic layouts (grid, row, cluster, etc.)

STEP-BY-STEP PROCESS:
1. Find the line starting with "Selected fixtures:"
2. Split by comma to get individual fixture names: ["EURO_CENTRE_3", "STANDING_TABLE_1", "STANDING_TABLE_2", "EURO_CENTRE_4"]
3. For EACH fixture name in that list:
   a. Find it in the "Available fixtures" list above to get current position
   b. Calculate a new non-overlapping position
   c. Add a move operation to the output JSON
4. Your output MUST have exactly as many operations as fixtures in the "Selected fixtures:" line

EXAMPLE:
If user says: "Selected fixtures: FIXTURE_A, FIXTURE_B, FIXTURE_C, FIXTURE_D\n\nRearrange these fixtures like an architect"
YOU MUST OUTPUT 4 operations (one for each):
{{
  "fixtures": [
    {{"block_name": "FIXTURE_A", "operation": "move", "original_position": [x1, y1], "new_position": [new_x1, new_y1]}},
    {{"block_name": "FIXTURE_B", "operation": "move", "original_position": [x2, y2], "new_position": [new_x2, new_y2]}},
    {{"block_name": "FIXTURE_C", "operation": "move", "original_position": [x3, y3], "new_position": [new_x3, new_y3]}},
    {{"block_name": "FIXTURE_D", "operation": "move", "original_position": [x4, y4], "new_position": [new_x4, new_y4]}}
  ]
}}

Generate ONLY valid JSON without any markdown formatting or explanations.
"""
        
        # Call Gemini AI
        print(f"🤖 Calling Gemini AI...")
        print(f"📝 Sending prompt (first 500 chars): {ai_prompt[:500]}...")
        # Check if boundaries are in the prompt
        if "CRITICAL FLOORPLAN BOUNDARIES" in ai_prompt:
            print(f"✅ Boundaries included in prompt")
        else:
            print(f"⚠️ WARNING: Boundaries NOT in prompt!")
        print(f"📊 Total prompt length: {len(ai_prompt)} characters")
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        response = model.generate_content(ai_prompt)
        response_text = response.text.strip()
        
        print(f"📥 Gemini raw response: {response_text[:500]}...")
        
        # Clean response (remove markdown code blocks)
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        # Parse modifications
        modifications = json.loads(response_text)
        
        # Handle both "fixtures" and "operations" formats from Gemini
        if 'operations' in modifications and 'fixtures' not in modifications:
            # Convert "operations" format to "fixtures" format
            print("📝 Converting 'operations' format to 'fixtures' format...")
            
            # Build a lookup dict for current fixture positions
            fixture_positions = {}
            for f in all_fixtures:
                fixture_positions[f['name']] = f['position']
            
            fixtures_list = []
            for op in modifications['operations']:
                fixture_name = op.get('fixture_name', '')
                # Look up original position from all_fixtures
                orig_pos = fixture_positions.get(fixture_name, [0, 0])
                
                fixture_entry = {
                    'block_name': fixture_name,
                    'operation': op.get('operation', 'move').lower(),
                    'original_position': orig_pos,
                    'new_position': [op.get('x', 0), op.get('y', 0)],
                }
                if 'reason' in op:
                    fixture_entry['reason'] = op['reason']
                fixtures_list.append(fixture_entry)
                print(f"   🔄 Mapped {fixture_name}: {orig_pos} → [{op.get('x', 0)}, {op.get('y', 0)}]")
            modifications['fixtures'] = fixtures_list
        
        if 'error' in modifications:
            return jsonify({
                'success': False,
                'error': modifications['error']
            }), 400
        
        print(f"✅ AI parsed {len(modifications.get('fixtures', []))} operations")
        
        # Debug: Show what fixtures were parsed
        for fix in modifications.get('fixtures', []):
            print(f"   • {fix.get('operation', 'move').upper()}: {fix.get('block_name', 'UNKNOWN')} → {fix.get('new_position', 'N/A')}")
        
        # Debug: Show bounds being used for validation
        print(f"\n🎯 Bounds being sent to validation:")
        print(f"   min_x: {floorplan_bounds.get('min_x')}")
        print(f"   max_x: {floorplan_bounds.get('max_x')}")
        print(f"   min_y: {floorplan_bounds.get('min_y')}")
        print(f"   max_y: {floorplan_bounds.get('max_y')}")
        print(f"   Fixtures count: {len(canvas_data.get('fixtures', []))}")
        
        # 🔥 VALIDATION LAYER: Only validate for "architect rearrange" mode
        # Manual customer movements are pre-approved and don't need validation
        validation_results = {}
        print(f"\n📋 Before validation: {len(modifications.get('fixtures', []))} fixtures to process")
        if needs_validation:
            print(f"\n🏗️ Running architect validation...")
            validation_results = validate_and_correct_fixtures(
                modifications, 
                floorplan_bounds, 
                canvas_data.get('fixtures', [])
            )
            print(f"📋 After validation: {len(modifications.get('fixtures', []))} fixtures remain")
        else:
            print(f"\n✋ Skipping validation - customer manual movement (all fixtures will be applied)")
        
        # Apply modifications (move, copy, delete)
        output_path = apply_ai_modifications(
            session_id,
            modifications
        )
        
        # Check if modifications were actually applied
        if not output_path:
            # Build helpful warning message based on validation results (only if validation was performed)
            rejected_count = validation_results.get('rejected', 0)
            rejected_names = validation_results.get('rejected_names', [])
            rejected_details = validation_results.get('rejected_details', [])
            room_bounds = validation_results.get('room_bounds', {})
            
            if needs_validation and rejected_count > 0:
                # Build detailed warning with room dimensions
                room_width = room_bounds.get('width', 0)
                room_height = room_bounds.get('height', 0)
                
                # Get fixture sizes from rejected details
                fixture_sizes = []
                for detail in rejected_details[:3]:  # Show up to 3 examples
                    size = detail.get('size', [300, 300])
                    fixture_sizes.append(f"{size[0]:.0f}×{size[1]:.0f}mm")
                
                warning_msg = f"⚠️ Validation Notice: All {rejected_count} fixture(s) exceed room boundaries!\n\n"
                warning_msg += f"💡 Suggestions:\n"
                warning_msg += f"   • Try dragging fixtures manually on canvas\n"
                warning_msg += f"   • Select smaller fixtures for auto-arrangement\n"
                warning_msg += f"   • Arrange fewer fixtures at a time"
            else:
                warning_msg = '⚠️ No changes were made. Please check fixture names and try again.'
            
            return jsonify({
                'success': True,  # Return success but with warning
                'warning': warning_msg,
                'message': warning_msg,
                'operations': {'moved': 0, 'copied': 0, 'deleted': 0, 'rotated': 0},
                'validation_results': validation_results
            }), 200  # Return 200 OK but with warning message
        
        # Store output path in session
        session_storage[session_id]['ai_output_path'] = output_path
        session_storage[session_id]['ai_modifications'] = modifications
        
        # Count operations
        operations_count = {
            'moved': 0,
            'copied': 0,
            'deleted': 0,
            'rotated': 0
        }
        for fixture in modifications.get('fixtures', []):
            op = fixture.get('operation', 'move').lower()
            if op == 'move':
                operations_count['moved'] += 1
            elif op == 'copy':
                operations_count['copied'] += 1
            elif op == 'delete':
                operations_count['deleted'] += 1
            elif op == 'rotate':
                operations_count['rotated'] += 1
        
        # Build message
        parts = []
        if operations_count['moved'] > 0:
            parts.append(f"{operations_count['moved']} moved")
        if operations_count['copied'] > 0:
            parts.append(f"{operations_count['copied']} copied")
        if operations_count['deleted'] > 0:
            parts.append(f"{operations_count['deleted']} deleted")
        if operations_count['rotated'] > 0:
            parts.append(f"{operations_count['rotated']} rotated")
        
        message = f"✅ Processed: {', '.join(parts)}"
        
        # Add info about rejected fixtures if any (only if validation was performed)
        rejected_count = validation_results.get('rejected', 0) if needs_validation else 0
        rejected_names = validation_results.get('rejected_names', []) if needs_validation else []
        
        if needs_validation and rejected_count > 0:
            # Build detailed warning message
            rejected_list = ", ".join(rejected_names[:5])  # Show first 5
            if rejected_count > 5:
                rejected_list += f" and {rejected_count - 5} more"
            
            message += f"\n\n⚠️ Warning: {rejected_count} fixture(s) were outside room boundaries and were not moved:\n"
            message += f"   {rejected_list}\n"
            message += f"   These fixtures are too large or positioned beyond the floorplan edges.\n"
            message += f"   Try moving them manually or selecting smaller fixtures."
        
        # Extract updated canvas data for real-time canvas update
        # Re-convert the modified JSON to canvas data
        updated_canvas_data = extract_canvas_data(session_storage[session_id]['json_data'], original_dxf)
        
        return jsonify({
            'success': True,
            'message': message,
            'operations': operations_count,
            'updated_canvas_data': updated_canvas_data,  # Send updated canvas data
            'modifications': modifications.get('fixtures', []),  # Send list of modified fixtures
            'validation_results': validation_results,  # Send validation info
            'warning': f"{rejected_count} fixtures rejected" if rejected_count > 0 else None
        })
    
    except json.JSONDecodeError as e:
        print(f"❌ AI response is not valid JSON: {e}")
        return jsonify({
            'success': False,
            'error': 'AI could not parse your command. Please be more specific.'
        }), 400
    except Exception as e:
        print(f"❌ AI generation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


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
    original_dxf = session_storage[session_id]['original_dxf']
    filename = session_storage[session_id]['filename']
    json_data = session_storage[session_id]['json_data']
    
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
            # Find original fixture and create a copy
            source_entity = None
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
                # Create a copy with new position
                new_entity = msp.add_blockref(
                    block_name,
                    (new_pos[0], new_pos[1], source_entity.dxf.insert.z),
                    dxfattribs={
                        'layer': source_entity.dxf.layer,
                        'xscale': source_entity.dxf.xscale,
                        'yscale': source_entity.dxf.yscale,
                        'zscale': source_entity.dxf.zscale,
                        'rotation': source_entity.dxf.rotation,
                    }
                )
                changes_made += 1
                print(f"      ✅ Copied {block_name} to ({new_pos[0]:.1f}, {new_pos[1]:.1f})")
                
                # Also add to JSON data for canvas update
                for e in json_data.get('modelspace', []):
                    if e.get('dxf_type') == 'INSERT' and e.get('name') == block_name:
                        if orig_pos and len(orig_pos) >= 2:
                            pos = e.get('insert', [0, 0, 0])
                            if abs(pos[0] - orig_pos[0]) < 0.1 and abs(pos[1] - orig_pos[1]) < 0.1:
                                # Found source, create copy in JSON
                                new_json_entity = e.copy()
                                new_json_entity['insert'] = [new_pos[0], new_pos[1], pos[2] if len(pos) > 2 else 0]
                                json_data.get('modelspace', []).append(new_json_entity)
                                break
            elif not source_entity:
                print(f"      ⚠️  Source fixture not found: {block_name}")
            elif not new_pos:
                print(f"      ⚠️  No target position provided for {block_name}")
            
        elif operation == 'move':
            # Update position of existing fixture
            for entity in msp:
                if entity.dxftype() == 'INSERT' and entity.dxf.name == block_name:
                    if orig_pos and len(orig_pos) >= 2 and new_pos and len(new_pos) >= 2:
                        # Match by position
                        pos = entity.dxf.insert
                        if abs(pos.x - orig_pos[0]) < 0.1 and abs(pos.y - orig_pos[1]) < 0.1:
                            entity.dxf.insert = (new_pos[0], new_pos[1], pos.z)
                            changes_made += 1
                            print(f"      ✅ Moved {block_name} to ({new_pos[0]:.1f}, {new_pos[1]:.1f})")
                            
                            # Also update in JSON data for canvas update
                            for e in json_data.get('modelspace', []):
                                if e.get('dxf_type') == 'INSERT' and e.get('name') == block_name:
                                    e_pos = e.get('insert', [0, 0, 0])
                                    if abs(e_pos[0] - orig_pos[0]) < 0.1 and abs(e_pos[1] - orig_pos[1]) < 0.1:
                                        e['insert'] = [new_pos[0], new_pos[1], e_pos[2] if len(e_pos) > 2 else 0]
                                        break
                            break
                    elif new_pos and len(new_pos) >= 2:
                        # Move first instance if no position specified
                        pos = entity.dxf.insert
                        entity.dxf.insert = (new_pos[0], new_pos[1], pos.z)
                        changes_made += 1
                        print(f"      ✅ Moved {block_name} to ({new_pos[0]:.1f}, {new_pos[1]:.1f})")
                        
                        # Also update in JSON data
                        for e in json_data.get('modelspace', []):
                            if e.get('dxf_type') == 'INSERT' and e.get('name') == block_name:
                                e_pos = e.get('insert', [0, 0, 0])
                                e['insert'] = [new_pos[0], new_pos[1], e_pos[2] if len(e_pos) > 2 else 0]
                                break
                        break
                    else:
                        print(f"      ⚠️  Invalid position data for {block_name}")
                        break
        
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
    
    # Update the session JSON data with modifications
    session_storage[session_id]['json_data'] = json_data
    
    # Set R2018 + MM format (same as prompt-based model)
    doc.header['$INSUNITS'] = 4  # Millimeters
    doc.header['$MEASUREMENT'] = 1  # Metric
    
    # Generate output DXF
    base_name = os.path.splitext(filename)[0]
    output_filename = f"{base_name}-AI-MODIFIED.dxf"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{session_id}_{output_filename}")
    
    # Save (preserves original DXF version and format)
    print(f"💾 Saving modified DXF...")
    doc.saveas(output_path)
    
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
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    
    # Save
    doc.saveas(output_path)
    print(f'💾 Saved: {output_path}')
    
    return output_path, changes


@app.route('/download/<session_id>')
def download_dxf(session_id):
    """
    Generate and download modified DXF file
    Uses AI-generated file if available, otherwise uses JSON-based file
    """
    try:
        if session_id not in session_storage:
            print(f"❌ Invalid session: {session_id}")
            return jsonify({'error': 'Invalid session ID'}), 404
        
        session_data = session_storage[session_id]
        original_filename = session_data.get('filename', 'unknown.dxf')
        
        print(f"\n📥 Generating DXF for download (Session: {session_id})...")
        
        # Check if AI-generated file exists and is valid
        if 'ai_output_path' in session_data and session_data.get('ai_output_path') and os.path.exists(session_data['ai_output_path']):
            output_path = session_data['ai_output_path']
            print(f"✅ Using AI-generated DXF: {output_path}")
        else:
            # Fallback: Generate from JSON data
            if 'json_data' not in session_data:
                print(f"❌ No JSON data in session")
                return jsonify({'error': 'No data available for download'}), 400
                
            json_data = session_data['json_data']
            base_name = os.path.splitext(original_filename)[0]
            output_filename = f"{base_name}-MODIFIED.dxf"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{session_id}_{output_filename}")
            
            # Convert JSON back to DXF
            print(f"🔄 Converting JSON to DXF...")
            json_to_dxf(json_data, output_path)
            print(f"✅ Generated from JSON: {output_path}")
        
        # Verify file exists and is not empty
        if not os.path.exists(output_path):
            print(f"❌ Output file not found: {output_path}")
            return jsonify({'error': 'Output file not found'}), 500
            
        file_size = os.path.getsize(output_path)
        if file_size == 0:
            print(f"❌ Output file is empty")
            return jsonify({'error': 'Generated file is empty'}), 500
        
        # Generate download filename
        base_name = os.path.splitext(original_filename)[0]
        download_filename = f"{base_name}-MODIFIED.dxf"
        
        print(f"✅ Ready for download: {download_filename} ({file_size} bytes)")
        
        # Send file for download with proper headers
        response = send_file(
            output_path,
            as_attachment=True,
            download_name=download_filename,
            mimetype='application/dxf'
        )
        
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
        
        return response
    
    except Exception as e:
        print(f"❌ Download error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Download failed: {str(e)}'}), 500


@app.route('/session/<session_id>')
def get_session_info(session_id):
    """Get session information"""
    if session_id not in session_storage:
        return jsonify({'error': 'Invalid session'}), 400
    
    session_data = session_storage[session_id]
    
    return jsonify({
        'filename': session_data['filename'],
        'modifications_count': len(session_data['modifications'])
    })


if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                  CANVAS-BASED DXF FIXTURE MOVER                            ║
║                  Flask Web Application                                     ║
╚════════════════════════════════════════════════════════════════════════════╝

🌐 Starting server...
📍 Open your browser to: http://localhost:5000

Features:
✅ Upload DXF files
✅ Visual canvas display
✅ Drag & drop fixtures
✅ Real-time coordinate tracking
✅ Gemini AI integration
✅ Download modified DXF

Press Ctrl+C to stop the server
""")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
