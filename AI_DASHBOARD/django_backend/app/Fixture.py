# import ezdxf
# from ezdxf.math import BoundingBox2d, Matrix44, Vec2
# import math

# class Fixture:
#     def __init__(self, name: str, path: str):
#         self.name = name
#         self.path = path
#         self.doc = ezdxf.readfile(path)
#         self.msp = self.doc.modelspace()
#         self.blocks = self.doc.blocks

#         self.bounding_box = self._calculate_total_bounding_box()
#         if self.bounding_box is None or self.bounding_box.is_empty:
#             raise ValueError(f"❌ Failed to compute bounding box for fixture '{self.name}'")

#         self.width = self.bounding_box.size.x
#         self.height = self.bounding_box.size.y

#         self.insertion_point = self._get_insertion_point()

#     def _calculate_total_bounding_box(self):
#         bbox = BoundingBox2d()
#         supported_types = {
#             "LINE", "LWPOLYLINE", "CIRCLE", "ARC", "TEXT", "MTEXT",
#             "ELLIPSE", "SPLINE", "SOLID", "INSERT", "ATTDEF", "HATCH"
#         }

#         MAX_EXTENT = 10000
#         MAX_DISTANCE = 50000

#         def compute_insert_transform(insert):
#             ip = insert.dxf.insert
#             rotation = insert.dxf.rotation
#             sx = getattr(insert.dxf, "xscale", 1.0)
#             sy = getattr(insert.dxf, "yscale", 1.0)
#             sz = getattr(insert.dxf, "zscale", 1.0)
#             return (
#                 Matrix44.scale(sx, sy, sz) @
#                 Matrix44.z_rotate(math.radians(rotation)) @
#                 Matrix44.translate(ip.x, ip.y, ip.z)
#             )

#         def get_arc_extents(arc_entity):
#             cx, cy = arc_entity.dxf.center.x, arc_entity.dxf.center.y
#             r = arc_entity.dxf.radius
#             start = math.radians(arc_entity.dxf.start_angle)
#             end = math.radians(arc_entity.dxf.end_angle)

#             def point(angle):
#                 return Vec2(cx + r * math.cos(angle), cy + r * math.sin(angle))

#             angles = [start, end]
#             sweep_start = arc_entity.dxf.start_angle % 360
#             sweep_end = arc_entity.dxf.end_angle % 360
#             for a_deg in [0, 90, 180, 270]:
#                 a = a_deg % 360
#                 if sweep_start < sweep_end:
#                     if sweep_start < a < sweep_end:
#                         angles.append(math.radians(a))
#                 else:
#                     if a > sweep_start or a < sweep_end:
#                         angles.append(math.radians(a))

#             return [point(a) for a in angles]

#         def get_entity_extents(entity, matrix=None):
#             points = []
#             try:
#                 if entity.dxftype() == "LINE":
#                     points = [entity.dxf.start, entity.dxf.end]
#                 elif entity.dxftype() == "LWPOLYLINE":
#                     points = [Vec2(p[0], p[1]) for p in entity.get_points()]
#                 elif entity.dxftype() == "CIRCLE":
#                     center = entity.dxf.center
#                     r = entity.dxf.radius
#                     points = [
#                         Vec2(center.x - r, center.y - r),
#                         Vec2(center.x + r, center.y + r)
#                     ]
#                 elif entity.dxftype() == "ARC":
#                     points = get_arc_extents(entity)
#                 else:
#                     return []

#                 if matrix:
#                     points = [matrix.transform(p) for p in points]

#                 return points
#             except Exception as e:
#                 print(f"⚠️ Failed to compute extents for {entity.dxftype()}: {e}")
#                 return []

#         def process_entity(entity, insert_matrix=None):
#             if entity.dxftype() == "INSERT":
#                 ip = entity.dxf.insert
#                 if abs(ip.x) > MAX_DISTANCE or abs(ip.y) > MAX_DISTANCE:
#                     print(f"⏭️ Skipping INSERT '{entity.dxf.name}' — far away at ({ip.x}, {ip.y})")
#                     return
#                 block_name = entity.dxf.name
#                 if block_name in self.blocks:
#                     block = self.blocks[block_name]
#                     m = compute_insert_transform(entity)
#                     combined = insert_matrix @ m if insert_matrix else m
#                     for e in block:
#                         process_entity(e, combined)
#             elif entity.dxftype() in supported_types:
#                 points = get_entity_extents(entity, insert_matrix)
#                 for pt in points:
#                     if abs(pt.x) > MAX_EXTENT or abs(pt.y) > MAX_EXTENT:
#                         print(f"⏭️ Skipping point {pt} — outside bounding box extent")
#                         return
#                 bbox.extend(points)

#         for entity in self.msp:
#             process_entity(entity)

#         return bbox

#     def _get_insertion_point(self):
#         for entity in self.msp:
#             if entity.dxftype() == "INSERT":
#                 return entity.dxf.insert
#         if self.bounding_box.is_empty:
#             print(f"⚠️ No valid geometry in fixture '{self.name}', defaulting insertion to (0, 0)")
#             return (0, 0)
#         return self.bounding_box.center



# In Fixture.py
import ezdxf
from ezdxf.math import BoundingBox2d, Matrix44, Vec2
from ezdxf.bbox import extents as ezdxf_extents # import with an alias

class Fixture:
    """
    This is the definitive unified Fixture class.
    It robustly calculates a fixture's visual bounding box by:
    1. First, searching for all entities placed in the modelspace (including nested blocks).
    2. If the modelspace is empty, it falls back to finding the largest block definition,
       which handles fixtures that are defined but not placed.
    It provides a consistent '.extmin' handle for perfect placement.
    """
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        try:
            self.doc = ezdxf.readfile(path)
            self.msp = self.doc.modelspace()
        except IOError:
            raise FileNotFoundError(f"❌ Fixture DXF file not found at: {path}")
        except ezdxf.DXFStructureError:
            raise ValueError(f"❌ Invalid DXF file for fixture '{self.name}': {path}")

        # --- STEP 1: Attempt to get extents directly from modelspace ---
        # This is the fastest and works for most standard cases, including the clinics.
        # We use the reliable ezdxf_extents() for this initial check.

#********** REPLACED: This single line replaces the entire old, complex '_calculate_total_bounding_box' function.**********
        try:
            bbox = ezdxf_extents(self.msp, fast=False)
        except Exception:
            bbox = BoundingBox2d()

        # --- STEP 2: Fallback for empty modelspace ---
        # If the modelspace is empty, it's likely the geometry is only in a block definition.
        # This was the key issue with the failing fixtures like 'Euro_centre'.

  #*********  # NEW: This entire block is new logic. The old code would fail if the modelspace was empty. *****     
        if not bbox.has_data:
            largest_block_bbox = BoundingBox2d()
            for block in self.doc.blocks:
                # Ignore internal blocks created by AutoCAD
                if not block.name.startswith('*'):
                    try:
                        # Calculate the extents of this block definition
                        current_block_bbox = ezdxf_extents(block, fast=False)
                        if current_block_bbox.has_data:
                            # Keep track of the block that has the largest area
                            if current_block_bbox.size.x * current_block_bbox.size.y > largest_block_bbox.size.x * largest_block_bbox.size.y:
                                largest_block_bbox = current_block_bbox
                    except Exception:
                        # Some blocks may be invalid or empty, just skip them
                        continue
            bbox = largest_block_bbox

        # --- STEP 3: Final validation and property assignment ---
        self.bounding_box = bbox
        if not self.bounding_box.has_data:
            raise ValueError(f"❌ CRITICAL: No usable geometry could be found for fixture '{self.name}' in {path} after checking modelspace and all block definitions.")

        # These properties are now reliable for ALL fixtures
        self.width = self.bounding_box.size.x
        self.height = self.bounding_box.size.y
        # The 'extmin' is our reliable handle: the visual bottom-left corner.
        self.extmin = self.bounding_box.extmin


    def _calculate_total_bounding_box(self, max_distance):
        bbox = BoundingBox2d()
        
        # This list will store all valid points found
        all_points = []

        def process_entity(entity, insert_matrix=None):
            # DEBUG: Announce the entity being processed
            print(f"[DEBUG FIXTURE]   Processing entity: {entity.dxftype()}, Layer: {entity.dxf.layer}")

            if entity.dxftype() == "INSERT":
                ip = entity.dxf.insert
                # DEBUG: Print details of the INSERT (block)
                print(f"[DEBUG FIXTURE]     Found INSERT: '{entity.dxf.name}' at insert point (x={ip.x:.2f}, y={ip.y:.2f})")

                # This is the filter from your original code
                if max_distance and (abs(ip.x) > max_distance or abs(ip.y) > max_distance):
                    print(f"[DEBUG FIXTURE]     ⚠️ SKIPPED: Insert point is beyond max_distance.")
                    return # Stop processing this branch

                block_name = entity.dxf.name
                if block_name in self.blocks:
                    block = self.blocks[block_name]
                    # Recursively process entities inside the block
                    for e in block:
                        process_entity(e, insert_matrix) # Note: this is simplified, original code had matrix math here
            
            # --- For other geometry types ---
            try:
                if entity.dxftype() == "LINE":
                    points = [entity.dxf.start, entity.dxf.end]
                    print(f"[DEBUG FIXTURE]     Found LINE with points: {points}")
                    all_points.extend(points)
                elif entity.dxftype() == "LWPOLYLINE":
                    points = [Vec2(p[0], p[1]) for p in entity.get_points()]
                    print(f"[DEBUG FIXTURE]     Found LWPOLYLINE with {len(points)} points.")
                    all_points.extend(points)
                # Add other entity types here if needed...
            except Exception as e:
                print(f"[DEBUG FIXTURE]     Could not process geometry for {entity.dxftype()}: {e}")

        # Start the process for all entities in the main modelspace
        for entity in self.msp:
            process_entity(entity)
        
        if not all_points:
            return BoundingBox2d()

        # Create the bounding box from all the points we found
        final_bbox = BoundingBox2d(all_points)
        return final_bbox

    # This part is less critical now but good practice
    def _get_insertion_point(self):
        if self.bounding_box.is_empty:
            return Vec2(0, 0)
        # Standardize to the bottom-left corner
        return self.bounding_box.extmin