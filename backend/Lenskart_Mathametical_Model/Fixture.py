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
