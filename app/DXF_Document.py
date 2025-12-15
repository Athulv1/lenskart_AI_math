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
from typing import Optional, List, Dict, Any, Tuple
from shapely.geometry import Polygon # type: ignore
from shapely.strtree import STRtree

class DXF_Document:
    def __init__(self, ind, doc: Optional[ezdxf.document.Drawing]=None):

        self.ind = ind
        print(f"recieved: {ind}; set: {self.ind}")
        self.skip = False
        
        self.doc = doc or ezdxf.new(dxfversion='R2018', units=units.MM)
        self.msp = self.doc.modelspace()

        # --- EXISTING STATE ---
        self.sofa_placed = False
        self.fixture_counter = {}
        self.placed_bboxes = [] # This is your master collision list
        
        # --- PLACEMENT METADATA ---
        self.back_room_location = None
        self.clinic_placement_method = "Unknown"
        self.clinic_placement_results = {}
        self.door_results = {}
        self.euro_placement_rotation: float = 0.0 
        self.euro_grid_is_column_wise: bool = False

        # --- CACHED GEOMETRY (EFFICIENCY UPGRADES) ---
        # Instead of recalculating these every time, we calculate ONCE and store here.
        
        # 1. BOH / Walls
        #--RASHEEQUE--ADDED--02/12/2025--
        self.boh_zone_polygon: Optional[Polygon] = None  # Stores the final shapely polygon of the BOH
        self.back_wall_y = 999999999
        self.retail_boundary_y: Optional[float] = None   # The y-line separating retail from BOH

        # 2. Clinic Details
        # Stores the list of dicts from _get_placed_clinic_details
        #--RASHEEQUE--ADDED--03/12/2025--
        self.placed_clinics_details: Optional[List[Dict[str, Any]]] = None
        self.door_results: Optional[Dict[str, Any]] = None
        self.door_aisle_polygons: Optional[List[Polygon]] = None
        self.extended_aisle_bboxes_map: Optional[Dict[str, Any]] = None
        
        # 3. Aisles & Doors
        self.door_aisle_polygons = []
        self.extended_aisle_bboxes_map = {}

        # 4. Zones
        self.euro_zone: Optional[Polygon] = None         # The valid placement area for Euros
        self.standing_table_zone: Optional[Polygon] = None # The valid placement area for Standing Tables

        # 5. Wall Segments
        self.right_wall_raw_data = []
        self.internal_corners_on_right_wall = []
        self.left_wall_raw_data = []
        self.internal_corners_on_left_wall = []


        # 6. BOH Perimeter
        #--RASHEEQUE--ADDED--03/12/2025--
        self.boh_perimeter_path: Optional[List[Tuple[Vec2, Vec2]]] = None

        

        # 7. Retail Perimeter Paths
        #-RASHEEQUE--ADDED--03/12/2025--
        self.perimeter_path_left_start: Optional[List[Tuple[Vec2, Vec2]]] = None
        self.perimeter_path_right_start: Optional[List[Tuple[Vec2, Vec2]]] = None

        # 8. Analyzed Wall Zones
        #RASHEEQUE--ADDED--03/12/2025--
        self.top_wall_zones: Optional[List[Dict[str, Any]]] = None

         # -- RASHEEQUE -- ADDED -- 04/12/2025 --
        # [SAFE TO CACHE]: Static Architectural Analysis
        self.back_corner_room_details: Optional[Tuple[Optional[str], Any]] = None
        self.top_wall_analysis: Optional[list] = None
        self.distributed_top_wall_segments: Optional[dict] = None
        self.clinic_ranked_plan: Optional[tuple] = None 
        self.boh_bottom_segment: Optional[List[dict]] = None
        self.toilet_room_door_detection: Optional[str] = None
        self.corner_room_by_door_detection: Optional[Tuple[Optional[str], Optional[float]]] = None

        #RASHEEQUE--ADDED--03/12/2025--
        # Cached validation context for bench placement
        self.spatial_index = None  # Spatial index for faster validation
        # self.bench_validation_ctx = None  # Dict[str, Any]

        # --- RASHEEQUE -- ADDED -- 04/12/2025 ---
        # [OPTIMIZATION] Spatial Index for static walls/partitions
        self.static_obstacle_tree = None 
        self.static_obstacle_polygons = []


        # --- COUNTERS ---
        self.remaining_wall_fixtures = 0
        self.display_calcs = {}
        self.overflow_fixture_count = 0
        self.placed_count = 0
        self.h_count = 0
        self.v_count = 0
        self.child = -1
        
        # --- DEBUG ---
        self.pickup_table_debug_bboxes = []
        self.walkable_corners_raw = []
        self.walkable_segments_raw = []
        self.trimmed_path_lines = []
        self.trimmed_segments_json = ""
        

    def clone(self, ind):
        """
        Clone the underlying ezdxf doc and deep-copy all non-ezdxf fields.
        """
        buf = io.StringIO()
        self.doc.write(buf)
        buf.seek(0)
        new_doc = ezdxf.read(buf)

        print("clone_ind: ", ind)
        clone = DXF_Document(ind, new_doc)

        # Deep copy all user fields
        reserved = {"doc", "msp", "ind"}
        for k, v in self.__dict__.items():
            if k in reserved:
                continue
            setattr(clone, k, copy.deepcopy(v))

        clone.msp = clone.doc.modelspace()
        return clone
        

    def place_fixture(self, fxtr: Fixture, insert_point: tuple, rotation: float, rotated: bool , xscale: float = 1.0, yscale: float = 1.0):
        
        # --- OPTIMIZATION START ---
        # OLD SLOW WAY: src_doc = ezdxf.readfile(fxtr.path)
        # NEW FAST WAY: Use the doc already loaded in the fixture object
        src_doc = fxtr.doc 
        # --- OPTIMIZATION END ---

        importer = Importer(src_doc, self.doc)

        if fxtr.name not in self.fixture_counter:
            self.fixture_counter[fxtr.name] = 1
        else:
            self.fixture_counter[fxtr.name] += 1

        safe_block_name = f"{fxtr.name.upper().replace(' ', '_')}_{self.fixture_counter[fxtr.name]}"

        # Create block definition
        block = self.doc.blocks.new(
            name=safe_block_name,
            base_point=fxtr.extmin
        )

        source_entities = list(src_doc.modelspace())
        if not source_entities:
            for b in src_doc.blocks:
                if not b.name.startswith('*'):
                    source_entities.extend(list(b))
        
        for entity in source_entities:
            try:
                block.add_entity(entity.copy())
            except ezdxf.DXFStructureError:
                continue

        importer.import_tables()
        importer.import_blocks(src_doc.blocks.block_names())
        
        block_ref = self.msp.add_blockref(
            safe_block_name, 
            insert_point, 
            dxfattribs={
                "rotation": rotation,
                "xscale": xscale,
                "yscale": yscale
            }
        )

        # Optional: reduce print spam to improve console speed slightly
        # print(f"✅ Placed '{fxtr.name}' as '{safe_block_name}' at ({insert_point[0]:.0f}, {insert_point[1]:.0f})")

        return block_ref
    
    
    def close_plan(self, name):
        final_name = name[:-4] + f"_{str(self.ind)}" + name[-4:]
        self.final_name = final_name
        self.doc.saveas(final_name)
        print(f"✅ Saved DXF file to: {final_name}")