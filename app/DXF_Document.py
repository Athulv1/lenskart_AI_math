import ezdxf # type: ignore
from ezdxf import units # type: ignore
from ezdxf.enums import InsertUnits # type: ignore
from ezdxf.math import Vec2, Vec3, Matrix44, BoundingBox2d # type: ignore
from ezdxf.addons import Importer # type: ignore
from ezdxf.bbox import extents # type: ignore 
from ezdxf.colors import rgb2int # type: ignore
import io
import copy
from . import Fixture
from typing import Optional

class DXF_Document:
    def __init__(self, ind, doc: Optional[ezdxf.document.Drawing]=None):

        self.ind = ind
        print(f"recieved: {ind}; set: {self.ind}")
        self.skip = False
        
        self.doc = doc or ezdxf.new(dxfversion='R2018', units=units.MM)
        self.msp = self.doc.modelspace()

        self.sofa_placed = False
        self.fixture_counter = {}
        self.back_room_location = None
        self.placed_bboxes = []
        
        self.clinic_placement_method = "Unknown"
        self.clinic_placement_results = {}
        self.placed_clinics_details = []
        self.door_results = {}

        self.euro_placement_rotation: float = 0.0 # Default to 0 (row-wise)

        self.door_aisle_polygons = []
        extended_aisle_bboxes_map = {}

        self.aisle_polygons = []
        self.extended_aisle_bboxes_map = {}

        self.pickup_table_debug_bboxes = []
        self.walkable_corners_raw = []
        self.walkable_segments_raw = []
        self.trimmed_path_lines = []
        self.trimmed_segments_json = ""

        self.back_wall_y = 999999999

        self.right_wall_raw_data = []
        self.internal_corners_on_right_wall = []
        self.left_wall_raw_data = []
        self.internal_corners_on_left_wall = []

        self.remaining_wall_fixtures = 0
        self.display_calcs = {}
        self.overflow_fixture_count = 0

        self.euro_zone = []
        self.overflow_fixture_count = 0

        self.placed_count = 0

        self.h_count = 0
        self.v_count = 0

        self.child = -1
        
    def clone(self, ind):
        """
        Clone the underlying ezdxf doc and deep-copy all non-ezdxf fields.
        Any entity object references must be re-bound via handle lookups.
        """
        # 1) clone ezdxf doc to a brand-new Drawing (no disk I/O)
        buf = io.StringIO()
        self.doc.write(buf)
        buf.seek(0)
        new_doc = ezdxf.read(buf)

        # 2) create a new wrapper with the cloned ezdxf doc
        print("clone_ind: ", ind)
        clone = DXF_Document(ind, new_doc)

        # 3) deep-copy *your* fields (except the reserved ones)
        # reserved = {"doc", "msp"}
        reserved = {"doc", "msp", "ind"}
        for k, v in self.__dict__.items():
            if k in reserved:
                continue
            # Deep-copy user fields to avoid aliasing shared mutable state
            setattr(clone, k, copy.deepcopy(v))

        # 4) re-bind anything that used to point at entity objects
        # If you followed the "track by handle" pattern, nothing else to do:
        # clone.tracked_entities already deep-copied; handles are preserved
        # across write/read, so they resolve inside clone.doc as well.
        #
        # If you *still* have fields that store entity *objects*, convert them:
        # Example:
        # if isinstance(clone.some_field, DXFEntity):
        #     handle = clone.some_field.dxf.handle
        #     clone.some_field = clone.doc.entitydb.get(handle)

        # 5) finally, refresh the convenience pointer
        clone.msp = clone.doc.modelspace()
        return clone
        

    def place_fixture(self, fxtr: Fixture, insert_point: tuple, rotation: float, rotated: bool , xscale: float = 1.0, yscale: float = 1.0):
        """
        Imports a fixture as a block, correctly aligning its geometry to the insertion point.
        This is the single, unified function for all fixture placements.
        It leverages the `base_point` property to align the fixture's visual corner (fxtr.extmin)
        with the desired `insert_point`.
        """
        try:
            # Read the fixture's source DXF file
            src_doc = ezdxf.readfile(fxtr.path)
        except IOError:
            print(f"⚠️ ERROR: Cannot read fixture file: {fxtr.path}")
            return
            
        # Importer helps manage layers, styles, etc. between the two files
        importer = Importer(src_doc, self.doc)

        # Increment a counter for each fixture type to ensure unique block names
        if fxtr.name not in self.fixture_counter:
            self.fixture_counter[fxtr.name] = 1
        else:
            self.fixture_counter[fxtr.name] += 1

        # Create a clean, safe block name (e.g., "CLINIC_REGULAR_1")
        safe_block_name = f"{fxtr.name.upper().replace(' ', '_')}_{self.fixture_counter[fxtr.name]}"

        # --- THIS IS THE KEY TO THE UNIFIED SOLUTION ---
        # Create a new block definition in the main DXF document.
        # The 'base_point' argument is crucial. It redefines the block's handle.
        # We are telling ezdxf: "Treat the fixture's visual bottom-left corner as its origin."
        block = self.doc.blocks.new(
            name=safe_block_name,
            base_point=fxtr.extmin
        )

        # --- Search for geometry in both modelspace and blocks ---
        # This ensures that even if the fixture is defined entirely within a block
        # in its source file, we still copy its geometry correctly.
        source_entities = list(src_doc.modelspace())
        if not source_entities:
            for b in src_doc.blocks:
                if not b.name.startswith('*'):
                    source_entities.extend(list(b))
        
        # Copy all entities from the fixture's file into the new block definition.
        for entity in source_entities:
            try:
                block.add_entity(entity.copy())
            except ezdxf.DXFStructureError:
                # This can happen if an entity is invalid; we can safely skip it.
                print(f"  -> Skipping an invalid entity in {fxtr.name}")
                continue

        # Import necessary table entries (layers, linetypes, text styles)
        importer.import_tables()
        # Import any block definitions that might be nested inside the fixture
        importer.import_blocks(src_doc.blocks.block_names())
        

        # This is the line that actually places the fixture
        block_ref = self.msp.add_blockref(
            safe_block_name, 
            insert_point, 
            dxfattribs={
                "rotation": rotation,
                "xscale": xscale,
                "yscale": yscale
            }
        )
        # --- END of Modification ---

        print(f"✅ Placed '{fxtr.name}' as '{safe_block_name}' at ({insert_point[0]:.0f}, {insert_point[1]:.0f})")

        return block_ref
    
    def close_plan(self, name):
        final_name = name[:-4] + f"_{str(self.ind)}" + name[-4:]
        self.final_name = final_name
        self.doc.saveas(final_name)
        print(f"✅ Saved DXF file to: {final_name}")