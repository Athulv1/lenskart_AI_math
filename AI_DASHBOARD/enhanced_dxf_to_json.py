import ezdxf
import json
import math


def serialize_point(point):
    """Convert Vec3 to list"""
    try:
        return [point.x, point.y, point.z] if hasattr(point, 'z') else [point.x, point.y]
    except:
        return list(point)


def serialize_entity(entity):
    """Serialize a single DXF entity with all its properties"""
    data = {
        'dxf_type': entity.dxftype(),
        'layer': entity.dxf.layer if hasattr(entity.dxf, 'layer') else '0',
        'color': entity.dxf.color if hasattr(entity.dxf, 'color') else 256,
        'linetype': entity.dxf.linetype if hasattr(entity.dxf, 'linetype') else 'BYLAYER',
    }
    
    dxf_type = entity.dxftype()
    
    if dxf_type == "LINE":
        data.update({
            'start': serialize_point(entity.dxf.start),
            'end': serialize_point(entity.dxf.end),
        })
    
    elif dxf_type == "LWPOLYLINE":
        data.update({
            'points': [[p[0], p[1]] for p in entity.get_points('xy')],
            'closed': entity.closed,
            'elevation': entity.dxf.elevation if hasattr(entity.dxf, 'elevation') else 0,
        })
    
    elif dxf_type == "POLYLINE":
        data.update({
            'points': [serialize_point(v.dxf.location) for v in entity.vertices],
            'closed': entity.is_closed,
        })
    
    elif dxf_type == "CIRCLE":
        data.update({
            'center': serialize_point(entity.dxf.center),
            'radius': entity.dxf.radius,
        })
    
    elif dxf_type == "ARC":
        data.update({
            'center': serialize_point(entity.dxf.center),
            'radius': entity.dxf.radius,
            'start_angle': entity.dxf.start_angle,
            'end_angle': entity.dxf.end_angle,
        })
    
    elif dxf_type == "ELLIPSE":
        data.update({
            'center': serialize_point(entity.dxf.center),
            'major_axis': serialize_point(entity.dxf.major_axis),
            'ratio': entity.dxf.ratio,
            'start_param': entity.dxf.start_param if hasattr(entity.dxf, 'start_param') else 0,
            'end_param': entity.dxf.end_param if hasattr(entity.dxf, 'end_param') else 6.283185307179586,
        })
    
    elif dxf_type == "SPLINE":
        data.update({
            'control_points': [serialize_point(p) for p in entity.control_points],
            'knots': list(entity.knots) if entity.knots else [],
            'degree': entity.dxf.degree if hasattr(entity.dxf, 'degree') else 3,
        })
    
    elif dxf_type == "TEXT":
        data.update({
            'text': entity.dxf.text,
            'insert': serialize_point(entity.dxf.insert),
            'height': entity.dxf.height,
            'rotation': entity.dxf.rotation if hasattr(entity.dxf, 'rotation') else 0,
            'style': entity.dxf.style if hasattr(entity.dxf, 'style') else 'Standard',
        })
    
    elif dxf_type == "MTEXT":
        data.update({
            'text': entity.text,
            'insert': serialize_point(entity.dxf.insert),
            'char_height': entity.dxf.char_height,
            'width': entity.dxf.width if hasattr(entity.dxf, 'width') else 0,
            'rotation': entity.dxf.rotation if hasattr(entity.dxf, 'rotation') else 0,
        })
    
    elif dxf_type == "INSERT":
        data.update({
            'name': entity.dxf.name,
            'insert': serialize_point(entity.dxf.insert),
            'xscale': entity.dxf.xscale if hasattr(entity.dxf, 'xscale') else 1.0,
            'yscale': entity.dxf.yscale if hasattr(entity.dxf, 'yscale') else 1.0,
            'zscale': entity.dxf.zscale if hasattr(entity.dxf, 'zscale') else 1.0,
            'rotation': entity.dxf.rotation if hasattr(entity.dxf, 'rotation') else 0,
        })
    
    elif dxf_type == "HATCH":
        # Serialize hatch patterns
        paths = []
        for path in entity.paths:
            if hasattr(path, 'vertices'):
                paths.append({
                    'type': 'polyline',
                    'vertices': [[v[0], v[1]] for v in path.vertices]
                })
        data.update({
            'paths': paths,
            'pattern_name': entity.dxf.pattern_name if hasattr(entity.dxf, 'pattern_name') else 'SOLID',
            'solid_fill': entity.dxf.solid_fill if hasattr(entity.dxf, 'solid_fill') else 1,
        })
    
    elif dxf_type == "DIMENSION":
        # Capture all dimension properties
        dim_data = {
            'defpoint': serialize_point(entity.dxf.defpoint) if hasattr(entity.dxf, 'defpoint') else [0, 0, 0],
            'text': entity.dxf.text if hasattr(entity.dxf, 'text') else '',
            'dimstyle': entity.dxf.dimstyle if hasattr(entity.dxf, 'dimstyle') else 'Standard',
        }
        
        # Try to get dimension-specific points
        for attr in ['defpoint2', 'defpoint3', 'defpoint4', 'defpoint5']:
            if hasattr(entity.dxf, attr):
                dim_data[attr] = serialize_point(getattr(entity.dxf, attr))
        
        # Get text position
        if hasattr(entity.dxf, 'text_midpoint'):
            dim_data['text_midpoint'] = serialize_point(entity.dxf.text_midpoint)
        
        data.update(dim_data)
    
    elif dxf_type == "ARC_DIMENSION":
        data.update({
            'center': serialize_point(entity.dxf.center) if hasattr(entity.dxf, 'center') else [0, 0, 0],
            'defpoint': serialize_point(entity.dxf.defpoint) if hasattr(entity.dxf, 'defpoint') else [0, 0, 0],
        })
    
    elif dxf_type == "MULTILEADER":
        data.update({
            'has_leader': True,
            # Store basic info - full MULTILEADER is complex
        })
    
    elif dxf_type == "SOLID":
        points = []
        for i in range(4):
            pt_name = f'vtx{i}'
            if hasattr(entity.dxf, pt_name):
                points.append(serialize_point(getattr(entity.dxf, pt_name)))
        data.update({
            'points': points,
        })
    
    return data


def serialize_block(block, doc):
    """Serialize a complete block definition"""
    entities = []
    for entity in block:
        try:
            entities.append(serialize_entity(entity))
        except Exception as e:
            print(f"Warning: Could not serialize {entity.dxftype()}: {e}")
    
    return {
        'name': block.name,
        'base_point': serialize_point(block.block.dxf.base_point) if hasattr(block.block.dxf, 'base_point') else [0, 0, 0],
        'entities': entities,
    }


def dxf_to_json(dxf_path):
    """Convert DXF to comprehensive JSON preserving all structure"""
    print(f"📄 Reading {dxf_path}")
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    
    output = {
        'dxf_version': doc.dxfversion,
        'blocks': {},
        'layers': [],
        'modelspace': [],
    }
    
    # Serialize all layers
    for layer in doc.layers:
        output['layers'].append({
            'name': layer.dxf.name,
            'color': layer.dxf.color if hasattr(layer.dxf, 'color') else 7,
            'linetype': layer.dxf.linetype if hasattr(layer.dxf, 'linetype') else 'Continuous',
        })
    
    # Serialize all block definitions
    for block in doc.blocks:
        block_name = block.name
        if not block_name.startswith('*'):  # Skip anonymous blocks
            output['blocks'][block_name] = serialize_block(block, doc)
    
    # Serialize modelspace entities
    for entity in msp:
        try:
            output['modelspace'].append(serialize_entity(entity))
        except Exception as e:
            print(f"Warning: Could not serialize {entity.dxftype()}: {e}")
    
    return output


def json_to_dxf(json_data, output_path):
    """Reconstruct DXF from comprehensive JSON"""
    print(f"🔨 Rebuilding DXF...")
    
    # Create new DXF document
    dxf_version = json_data.get('dxf_version', 'R2010')
    doc = ezdxf.new(dxf_version)
    msp = doc.modelspace()
    
    # Recreate layers
    for layer_data in json_data.get('layers', []):
        layer_name = layer_data['name']
        # Skip default layers that already exist
        if layer_name not in ['0', 'Defpoints'] and layer_name not in doc.layers:
            try:
                doc.layers.new(
                    name=layer_name,
                    dxfattribs={
                        'color': layer_data['color'],
                        'linetype': layer_data['linetype'],
                    }
                )
            except Exception as e:
                print(f"Warning: Could not create layer '{layer_name}': {e}")
    
    # Recreate block definitions
    for block_name, block_data in json_data.get('blocks', {}).items():
        if block_name not in doc.blocks:
            block = doc.blocks.new(name=block_name)
            
            # Add entities to block
            for entity_data in block_data['entities']:
                add_entity_to_container(block, entity_data)
    
    # Recreate modelspace entities
    for entity_data in json_data.get('modelspace', []):
        add_entity_to_container(msp, entity_data)
    
    doc.saveas(output_path)
    print(f"✅ Rebuilt DXF: {output_path}")


def add_entity_to_container(container, entity_data):
    """Add a single entity to a container (modelspace or block)"""
    dxf_type = entity_data['dxf_type']
    
    common_attribs = {
        'layer': entity_data.get('layer', '0'),
        'color': entity_data.get('color', 256),
        'linetype': entity_data.get('linetype', 'BYLAYER'),
    }
    
    try:
        if dxf_type == "LINE":
            container.add_line(
                start=entity_data['start'],
                end=entity_data['end'],
                dxfattribs=common_attribs
            )
        
        elif dxf_type == "LWPOLYLINE":
            polyline = container.add_lwpolyline(
                points=entity_data['points'],
                dxfattribs=common_attribs
            )
            polyline.closed = entity_data.get('closed', False)
        
        elif dxf_type == "POLYLINE":
            polyline = container.add_polyline3d(
                points=entity_data['points'],
                dxfattribs=common_attribs
            )
            if entity_data.get('closed', False):
                polyline.close()
        
        elif dxf_type == "CIRCLE":
            container.add_circle(
                center=entity_data['center'],
                radius=entity_data['radius'],
                dxfattribs=common_attribs
            )
        
        elif dxf_type == "ARC":
            container.add_arc(
                center=entity_data['center'],
                radius=entity_data['radius'],
                start_angle=entity_data['start_angle'],
                end_angle=entity_data['end_angle'],
                dxfattribs=common_attribs
            )
        
        elif dxf_type == "ELLIPSE":
            container.add_ellipse(
                center=entity_data['center'],
                major_axis=entity_data['major_axis'],
                ratio=entity_data['ratio'],
                start_param=entity_data.get('start_param', 0),
                end_param=entity_data.get('end_param', 6.283185307179586),
                dxfattribs=common_attribs
            )
        
        elif dxf_type == "SPLINE":
            spline = container.add_spline(
                dxfattribs=common_attribs
            )
            spline.fit_points = entity_data['control_points']
            spline.dxf.degree = entity_data.get('degree', 3)
            if entity_data.get('knots'):
                spline.knots = entity_data['knots']
        
        elif dxf_type == "TEXT":
            container.add_text(
                text=entity_data['text'],
                dxfattribs={
                    **common_attribs,
                    'insert': entity_data['insert'],
                    'height': entity_data['height'],
                    'rotation': entity_data.get('rotation', 0),
                    'style': entity_data.get('style', 'Standard'),
                }
            )
        
        elif dxf_type == "MTEXT":
            container.add_mtext(
                text=entity_data['text'],
                dxfattribs={
                    **common_attribs,
                    'insert': entity_data['insert'],
                    'char_height': entity_data['char_height'],
                    'width': entity_data.get('width', 0),
                    'rotation': entity_data.get('rotation', 0),
                }
            )
        
        elif dxf_type == "INSERT":
            container.add_blockref(
                name=entity_data['name'],
                insert=entity_data['insert'],
                dxfattribs={
                    **common_attribs,
                    'xscale': entity_data.get('xscale', 1.0),
                    'yscale': entity_data.get('yscale', 1.0),
                    'zscale': entity_data.get('zscale', 1.0),
                    'rotation': entity_data.get('rotation', 0),
                }
            )
        
        elif dxf_type == "HATCH":
            hatch = container.add_hatch(dxfattribs=common_attribs)
            hatch.dxf.solid_fill = entity_data.get('solid_fill', 1)
            hatch.dxf.pattern_name = entity_data.get('pattern_name', 'SOLID')
            
            # Add paths
            for path_data in entity_data.get('paths', []):
                if path_data.get('type') == 'polyline':
                    vertices = path_data.get('vertices', [])
                    if vertices:
                        hatch.paths.add_polyline_path(vertices)
        
        elif dxf_type == "DIMENSION":
            # Dimensions are complex - skip for now or add basic linear dimension
            pass
        
        elif dxf_type == "ARC_DIMENSION":
            # Arc dimensions are complex - skip for now
            pass
        
        elif dxf_type == "MULTILEADER":
            # Multileaders are complex - skip for now
            pass
        
        elif dxf_type == "SOLID":
            points = entity_data.get('points', [])
            if len(points) >= 3:
                container.add_solid(points, dxfattribs=common_attribs)
    
    except Exception as e:
        print(f"Warning: Could not recreate {dxf_type}: {e}")


# === MAIN SCRIPT ===

if __name__ == "__main__":
    try:
        # Convert DXF to JSON
        dxf_file = "ATTA MARKET SECTOR-18_NOIDA-FLAGSHIP-B-FURNITURE.dxf"
        json_file = dxf_file.replace(".dxf", "-COMPLETE.json")
        
        json_data = dxf_to_json(dxf_file)
        
        with open(json_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"✅ Exported: {json_file}")
        print(f"   Blocks: {len(json_data['blocks'])}")
        print(f"   Layers: {len(json_data['layers'])}")
        print(f"   Modelspace entities: {len(json_data['modelspace'])}")
        
        # Rebuild DXF from JSON
        rebuilt_dxf = dxf_file.replace(".dxf", "-REBUILT.dxf")
        json_to_dxf(json_data, rebuilt_dxf)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
