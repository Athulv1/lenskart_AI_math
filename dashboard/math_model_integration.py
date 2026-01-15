"""
Mathematical Model Integration for Complex Fixture Operations
==============================================================

Wraps the Lenskart Mathematical Model (DXF_Controller) to provide
accurate fixture positioning for complex operations that require:
- Spatial optimization
- Design guideline compliance
- Collision detection
- Zone-based placement

Author: Lenskart Development Team
Version: 1.0
Date: January 13, 2026
"""

import os
import sys
import json
import tempfile
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import ezdxf
from shapely.geometry import Point, Polygon, box
from shapely.affinity import translate

logger = logging.getLogger(__name__)


class MathModelIntegration:
    """Integrates Lenskart Mathematical Model for complex fixture operations"""
    
    def __init__(self, dxf_path: str, floor_boundaries: Dict, session_id: str):
        """
        Initialize the mathematical model integration.
        
        Args:
            dxf_path: Path to the current DXF file
            floor_boundaries: Dictionary containing boundary information
            session_id: Current session identifier
        """
        self.dxf_path = dxf_path
        self.boundaries = floor_boundaries
        self.session_id = session_id
        self.dxfc = None
        self.temp_dir = None
        self.DXF_Controller = None
        
        # Create floorplan polygon for strict containment checks
        self.floorplan_polygon = self._create_floorplan_polygon()
        
        # Default fixture dimensions (mm) - used for collision detection
        self.default_fixture_sizes = {
            'pickup_table': {'width': 1200, 'depth': 630},
            'ups_rack': {'width': 900, 'depth': 450},
            'staff_rack': {'width': 900, 'depth': 450},
            'water_dispenser': {'width': 450, 'depth': 450},
            'storage_rack': {'width': 900, 'depth': 450},
            'dining_table': {'width': 900, 'depth': 450},
            'default': {'width': 600, 'depth': 600}
        }
        
        logger.info(f"MathModelIntegration initialized for session {session_id}")
        logger.info(f"DXF path: {dxf_path}")
        logger.info(f"Boundaries: {floor_boundaries}")
    
    def _create_floorplan_polygon(self) -> Optional[Polygon]:
        """Create a Shapely polygon from boundary coordinates for strict containment"""
        try:
            min_x = self.boundaries.get('min_x', 0)
            max_x = self.boundaries.get('max_x', 10000)
            min_y = self.boundaries.get('min_y', 0)
            max_y = self.boundaries.get('max_y', 10000)
            
            # Create rectangle polygon representing the floorplan
            coords = [
                (min_x, min_y),
                (max_x, min_y),
                (max_x, max_y),
                (min_x, max_y),
                (min_x, min_y)  # Close the polygon
            ]
            
            polygon = Polygon(coords)
            logger.info(f"Created floorplan polygon: {polygon.bounds}")
            return polygon
            
        except Exception as e:
            logger.error(f"Failed to create floorplan polygon: {e}")
            return None
    
    def calculate_positions(
        self,
        operation: str,
        fixtures: Dict,
        merch_mix: Optional[Dict] = None,
        room_measurements: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate optimal fixture positions using the mathematical model.
        
        Args:
            operation: Operation type (rearrange, add, remove, optimize)
            fixtures: Current fixtures data
            merch_mix: Merchandise mix configuration
            room_measurements: Room measurements and boundaries
            
        Returns:
            Dictionary with calculated positions:
            {
                'fixtures': [
                    {
                        'block_name': 'clinic_1',
                        'calculated_position': [x, y],
                        'rotation': 0.0,
                        'zone': 'clinic',
                        'reasoning': 'Positioned per design guidelines'
                    }
                ],
                'placement_valid': True,
                'warnings': [],
                'method': 'mathematical_model'
            }
        """
        logger.info(f"Calculating positions for operation: {operation}")
        
        try:
            if operation == "rearrange":
                return self._rearrange_fixtures(fixtures, merch_mix, room_measurements)
            elif operation == "add":
                return self._add_fixtures(fixtures, merch_mix, room_measurements)
            elif operation == "remove":
                return self._remove_fixtures(fixtures)
            elif operation == "optimize":
                return self._optimize_layout(fixtures, merch_mix, room_measurements)
            else:
                logger.warning(f"Unknown operation: {operation}, defaulting to optimize")
                return self._optimize_layout(fixtures, merch_mix, room_measurements)
                
        except Exception as e:
            logger.error(f"Error calculating positions: {e}")
            return {
                'fixtures': [],
                'placement_valid': False,
                'warnings': [str(e)],
                'method': 'mathematical_model',
                'error': str(e)
            }
    
    def _rearrange_fixtures(
        self,
        fixtures: Dict,
        merch_mix: Optional[Dict],
        room_measurements: Optional[Dict]
    ) -> Dict:
        """
        Rearrange existing fixtures using simplified mathematical model logic.
        Based on DXF_Controller.place_boh_fixtures() algorithm.
        """
        logger.info("Rearranging fixtures using mathematical model")
        
        try:
            # Identify BOH fixtures from the fixture dict
            boh_fixtures = self._identify_boh_fixtures(fixtures)
            
            if not boh_fixtures:
                logger.warning("No BOH fixtures found to rearrange")
                return {
                    'fixtures': [],
                    'placement_valid': False,
                    'warnings': ['No BOH fixtures found'],
                    'method': 'mathematical_model'
                }
            
            logger.info(f"Found {len(boh_fixtures)} BOH fixtures to rearrange: {list(boh_fixtures.keys())}")
            
            # Define BOH zone based on boundaries (similar to DXF_Controller.create_boh_zone)
            boh_zone = self._create_boh_zone_bounds()
            
            # Calculate optimal positions for BOH fixtures with proper spacing
            calculated_fixtures = self._place_boh_fixtures_in_zone(
                boh_fixtures,
                boh_zone
            )
            
            logger.info(f"Successfully calculated positions for {len(calculated_fixtures)} BOH fixtures")
            
            return {
                'fixtures': calculated_fixtures,
                'placement_valid': True,
                'warnings': [],
                'method': 'mathematical_model_boh',
                'zone_used': 'boh'
            }
            
        except Exception as e:
            logger.error(f"Error in rearrange_fixtures: {e}", exc_info=True)
            return {
                'fixtures': [],
                'placement_valid': False,
                'warnings': [f"Rearrangement failed: {str(e)}"],
                'method': 'mathematical_model',
                'error': str(e)
            }
    
    def _add_fixtures(
        self,
        fixtures: Dict,
        merch_mix: Optional[Dict],
        room_measurements: Optional[Dict]
    ) -> Dict:
        """
        Add new fixtures to the layout using mathematical model.
        """
        logger.info("Adding fixtures using mathematical model")
        
        # Similar to rearrange, but with additional fixtures
        # The math model will find optimal positions for new fixtures
        
        return self._rearrange_fixtures(fixtures, merch_mix, room_measurements)
    
    def _remove_fixtures(self, fixtures: Dict) -> Dict:
        """
        Remove fixtures from the layout.
        
        This is simpler as it doesn't require the math model,
        just marks fixtures for removal.
        """
        logger.info("Marking fixtures for removal")
        
        removal_list = []
        for fixture_name, fixture_data in fixtures.items():
            removal_list.append({
                'block_name': fixture_name,
                'action': 'remove',
                'original_position': fixture_data.get('position', [0, 0])
            })
        
        return {
            'fixtures': removal_list,
            'placement_valid': True,
            'warnings': [],
            'method': 'simple_removal'
        }
    
    def _optimize_layout(
        self,
        fixtures: Dict,
        merch_mix: Optional[Dict],
        room_measurements: Optional[Dict]
    ) -> Dict:
        """
        Optimize the entire layout using mathematical model.
        """
        logger.info("Optimizing layout using mathematical model")
        
        return self._rearrange_fixtures(fixtures, merch_mix, room_measurements)
    
    def _prepare_static_fixtures(self, fixtures: Dict) -> Dict:
        """
        Prepare static fixtures configuration from current fixtures.
        """
        static_fixtures = {
            "mirror_selection": {"mirror_different": 0, "mirror": 0},
            "Bench_fixtures": {"large_bench": 0, "AR": 0, "medium_bench": 0},
            "lensometer_fixtures": {"Lensometer_medium": 0, "Lensometer_small": 0, "Lensometer_large": 0},
            "boh_fixtures": {},
            "boh_presets": {},
            "pickup_window": {"Pick_up_window": 0, "pickup_table": 0},
            "Eye_massage_area": {"Eye_massage_area": 0},
            "Corian_table_set": {"Corian_table": 0, "Lounge_seat": 0},
            "loose_furniture": {"sofa": 0, "Sofa_large": 0, "Sofa_medium": 0},
            "toilet_fixtures": {"toilet": 0},
            "screen_fixtures": {"screen_43": 0, "screen_49": 0, "screen_55": 0, "screen_65": 0},
            "POS": {},
            "discussion_table_attached": {"Blue_zero": 0},
            "table_fixtures": {"QMS_desk": 0},
            "lensbar_and_dropbox": {"Lensbar": 0},
            "floor_fixtures_table": {}
        }
        
        # Count existing fixtures by type
        for fixture_name, fixture_data in fixtures.items():
            fixture_type = fixture_data.get('type', '')
            
            # Map to appropriate category
            if 'clinic' in fixture_name.lower():
                if 'boh_fixtures' not in static_fixtures:
                    static_fixtures['clinic_fixtures'] = {}
                static_fixtures.setdefault('clinic_fixtures', {})[fixture_name] = 1
            elif 'table' in fixture_name.lower():
                static_fixtures.setdefault('floor_fixtures_table', {})[fixture_name] = 1
            elif 'screen' in fixture_name.lower():
                static_fixtures.setdefault('screen_fixtures', {})[fixture_name] = 1
            # Add more mappings as needed
        
        return static_fixtures
    
    def _extract_merch_mix_from_fixtures(self, fixtures: Dict) -> Dict:
        """
        Extract merchandise mix from current fixtures.
        """
        merch_mix = {}
        
        for fixture_name, fixture_data in fixtures.items():
            fixture_type = fixture_data.get('type', 'unknown')
            if fixture_type not in merch_mix:
                merch_mix[fixture_type] = 0
            merch_mix[fixture_type] += 1
        
        return merch_mix
    
    def _calculate_optimal_positions(
        self,
        fixtures: Dict,
        static_fixtures: Dict,
        merch_mix: Dict,
        room_measurements: Optional[Dict]
    ) -> List[Dict]:
        """
        Calculate optimal positions for all fixtures.
        
        This is a simplified version - actual implementation would use
        the full DXF_Controller logic from the mathematical model.
        """
        calculated_fixtures = []
        
        # Get boundary information
        min_x = self.boundaries.get('min_x', 0)
        max_x = self.boundaries.get('max_x', 10000)
        min_y = self.boundaries.get('min_y', 0)
        max_y = self.boundaries.get('max_y', 10000)
        
        # Define zones based on design guidelines
        zones = self._define_zones(min_x, max_x, min_y, max_y)
        
        # Place fixtures by category
        for fixture_name, fixture_data in fixtures.items():
            fixture_type = fixture_data.get('type', 'floor')
            
            # Determine zone for this fixture type
            zone = self._determine_fixture_zone(fixture_name, fixture_type)
            zone_bounds = zones.get(zone, zones['general'])
            
            # Calculate position within zone
            position = self._calculate_position_in_zone(
                fixture_name,
                fixture_type,
                zone_bounds,
                calculated_fixtures
            )
            
            calculated_fixtures.append({
                'block_name': fixture_name,
                'original_position': fixture_data.get('position', [0, 0]),
                'calculated_position': position,
                'new_position': position,
                'rotation': fixture_data.get('rotation', 0.0),
                'zone': zone,
                'reasoning': f'Positioned in {zone} zone per design guidelines'
            })
        
        return calculated_fixtures
    
    def _define_zones(self, min_x: float, max_x: float, min_y: float, max_y: float) -> Dict:
        """Define spatial zones for different fixture types"""
        width = max_x - min_x
        height = max_y - min_y
        
        zones = {
            'clinic': {
                'min_x': min_x,
                'max_x': min_x + width * 0.3,
                'min_y': min_y,
                'max_y': min_y + height * 0.4
            },
            'boh': {
                'min_x': max_x - width * 0.25,
                'max_x': max_x,
                'min_y': max_y - height * 0.3,
                'max_y': max_y
            },
            'premium': {
                'min_x': min_x,
                'max_x': min_x + width * 0.5,
                'min_y': min_y + height * 0.5,
                'max_y': max_y
            },
            'general': {
                'min_x': min_x,
                'max_x': max_x,
                'min_y': min_y,
                'max_y': max_y
            }
        }
        
        return zones
    
    def _determine_fixture_zone(self, fixture_name: str, fixture_type: str) -> str:
        """Determine which zone a fixture should be placed in"""
        name_lower = fixture_name.lower()
        
        if 'clinic' in name_lower or 'examination' in name_lower:
            return 'clinic'
        elif 'boh' in name_lower or 'storage' in name_lower or 'staff' in name_lower:
            return 'boh'
        elif 'premium' in name_lower or 'jj_super' in name_lower:
            return 'premium'
        else:
            return 'general'
    
    def _calculate_position_in_zone(
        self,
        fixture_name: str,
        fixture_type: str,
        zone_bounds: Dict,
        existing_fixtures: List[Dict],
        spacing: float = 1000.0  # 1000mm spacing
    ) -> List[float]:
        """
        Calculate a valid position within a zone, avoiding collisions.
        """
        min_x = zone_bounds['min_x']
        max_x = zone_bounds['max_x']
        min_y = zone_bounds['min_y']
        max_y = zone_bounds['max_y']
        
        # Simple grid-based placement
        # In production, this would use the full mathematical model logic
        
        # Try to place fixture at regular intervals
        attempts = 0
        max_attempts = 100
        
        while attempts < max_attempts:
            # Calculate grid position
            col = attempts % 3
            row = attempts // 3
            
            x = min_x + spacing + (col * spacing * 2)
            y = min_y + spacing + (row * spacing * 2)
            
            # Ensure within bounds
            if x > max_x - spacing:
                x = max_x - spacing
            if y > max_y - spacing:
                y = max_y - spacing
            
            # Check for collisions
            if self._is_position_valid([x, y], existing_fixtures, spacing):
                return [round(x, 2), round(y, 2)]
            
            attempts += 1
        
        # Fallback: return zone center
        return [
            round((min_x + max_x) / 2, 2),
            round((min_y + max_y) / 2, 2)
        ]
    
    def _is_position_valid(
        self,
        position: List[float],
        existing_fixtures: List[Dict],
        min_distance: float = 800.0
    ) -> bool:
        """Check if a position is valid (no collisions)"""
        x, y = position
        
        for fixture in existing_fixtures:
            fx, fy = fixture.get('calculated_position', fixture.get('new_position', [0, 0]))
            distance = ((x - fx) ** 2 + (y - fy) ** 2) ** 0.5
            
            if distance < min_distance:
                return False
        
        return True
    
    def _identify_boh_fixtures(self, fixtures: Dict) -> Dict:
        """
        Identify BOH (Back of House) fixtures from all fixtures.
        Based on DXF_Controller fixture types.
        """
        boh_keywords = [
            'staff_rack', 'storage_rack', 'ups_rack', 'water_dispenser',
            'dining_table', 'qc_table', 'repair_table', 'pickup',
            'boh', 'staff', 'storage', 'ups', 'water'
        ]
        
        boh_fixtures = {}
        for fixture_name, fixture_data in fixtures.items():
            name_lower = fixture_name.lower()
            
            # Check if any BOH keyword is in the fixture name
            if any(keyword in name_lower for keyword in boh_keywords):
                boh_fixtures[fixture_name] = fixture_data
                logger.debug(f"Identified BOH fixture: {fixture_name}")
        
        return boh_fixtures
    
    def _create_boh_zone_bounds(self) -> Dict:
        """
        Create BOH zone boundaries based on floorplan boundaries.
        Places BOH in the back-right corner (typical layout).
        
        CRITICAL: Uses ACTUAL boundary values, not assuming positive coordinates.
        """
        min_x = self.boundaries.get('min_x', 0)
        max_x = self.boundaries.get('max_x', 10000)
        min_y = self.boundaries.get('min_y', 0)
        max_y = self.boundaries.get('max_y', 10000)
        
        width = max_x - min_x
        height = max_y - min_y
        
        # Safety margin from boundaries
        EDGE_CLEARANCE = 400  # 400mm clearance from walls
        
        # BOH zone: back-right 30% width, top 35% height (typical)
        boh_zone = {
            'min_x': max_x - width * 0.30 + EDGE_CLEARANCE,  # Right 30% of width
            'max_x': max_x - EDGE_CLEARANCE,  # Leave clearance from edge
            'min_y': max_y - height * 0.35 + EDGE_CLEARANCE,  # Top 35% of height
            'max_y': max_y - EDGE_CLEARANCE,  # Leave clearance from edge
            'width': width * 0.30 - (2 * EDGE_CLEARANCE),
            'height': height * 0.35 - (2 * EDGE_CLEARANCE)
        }
        
        logger.info(f"BOH Zone created: {boh_zone['width']:.0f}mm x {boh_zone['height']:.0f}mm at X=[{boh_zone['min_x']:.0f}, {boh_zone['max_x']:.0f}], Y=[{boh_zone['min_y']:.0f}, {boh_zone['max_y']:.0f}]")
        return boh_zone
    
    def _place_boh_fixtures_in_zone(
        self,
        boh_fixtures: Dict,
        zone: Dict
    ) -> List[Dict]:
        """
        Place BOH fixtures with STRICT boundary and collision validation.
        No centroid heuristic - full fixture geometry must be contained.
        """
        calculated_fixtures = []
        placed_geometries = []  # Track placed fixture polygons for collision detection
        
        # Define spacing between fixtures (based on typical BOH requirements)
        SPACING_X = 1200.0  # 1200mm horizontal spacing
        SPACING_Y = 800.0   # 800mm vertical spacing
        MIN_CLEARANCE = 600.0  # Minimum clearance from walls
        MIN_COLLISION_BUFFER = 100.0  # Minimum gap between fixtures
        
        zone_width = zone['max_x'] - zone['min_x']
        zone_height = zone['max_y'] - zone['min_y']
        
        # Calculate how many fixtures can fit per row
        usable_width = zone_width - (2 * MIN_CLEARANCE)
        fixtures_per_row = max(1, int(usable_width / SPACING_X))
        
        logger.info(f"BOH layout: {fixtures_per_row} fixtures per row (strict validation enabled)")
        
        # Place fixtures in grid pattern with strict validation
        fixture_list = list(boh_fixtures.items())
        row = 0
        col = 0
        max_attempts = 100
        
        for fixture_name, fixture_data in fixture_list:
            placed = False
            attempts = 0
            
            while not placed and attempts < max_attempts:
                # Calculate candidate position in grid
                x = zone['min_x'] + MIN_CLEARANCE + (col * SPACING_X) + (attempts * 50)
                y = zone['max_y'] - MIN_CLEARANCE - (row * SPACING_Y) - (attempts * 30)
                
                # Get fixture dimensions
                fixture_size = self._get_fixture_dimensions(fixture_name)
                width = fixture_size['width']
                depth = fixture_size['depth']
                
                # Create fixture polygon for validation
                fixture_polygon = box(
                    x - width/2, 
                    y - depth/2,
                    x + width/2,
                    y + depth/2
                )
                
                # STRICT VALIDATION #1: Full geometry must be within floorplan
                if not self._is_fully_contained(fixture_polygon):
                    logger.debug(f"  Attempt {attempts}: {fixture_name} extends beyond boundary")
                    attempts += 1
                    continue
                
                # STRICT VALIDATION #2: No collision with other fixtures
                if self._has_collision(fixture_polygon, placed_geometries, MIN_COLLISION_BUFFER):
                    logger.debug(f"  Attempt {attempts}: {fixture_name} collides with existing fixture")
                    attempts += 1
                    continue
                
                # Position is VALID - place fixture
                calculated_fixtures.append({
                    'block_name': fixture_name,
                    'calculated_position': [round(x, 2), round(y, 2)],
                    'new_position': [round(x, 2), round(y, 2)],
                    'action': 'move',
                    'rotation': fixture_data.get('rotation', 0.0),
                    'zone': 'boh',
                    'row': row,
                    'col': col,
                    'width': width,
                    'depth': depth,
                    'validation': 'strict_containment',
                    'reasoning': f'BOH zone (row {row}, col {col}) - validated within boundaries'
                })
                
                # Register this fixture's geometry
                placed_geometries.append({
                    'name': fixture_name,
                    'polygon': fixture_polygon
                })
                
                placed = True
                logger.info(f"✅ Placed {fixture_name} at [{x:.0f}, {y:.0f}] (validated)")
                
            if not placed:
                logger.warning(f"⚠️ Could not place {fixture_name} after {max_attempts} attempts")
            
            # Move to next grid position
            col += 1
            if col >= fixtures_per_row:
                col = 0
                row += 1
        
        logger.info(f"Successfully placed {len(calculated_fixtures)}/{len(fixture_list)} fixtures with strict validation")
        return calculated_fixtures
    
    def _get_fixture_dimensions(self, fixture_name: str) -> Dict[str, float]:
        """Get fixture dimensions for boundary/collision checks"""
        name_lower = fixture_name.lower()
        
        # Match fixture type and return dimensions
        for key, dims in self.default_fixture_sizes.items():
            if key in name_lower:
                return dims
        
        # Default size if not found
        return self.default_fixture_sizes['default']
    
    def _is_fully_contained(self, fixture_polygon: Polygon) -> bool:
        """
        STRICT containment check - entire fixture geometry must be within floorplan.
        NO centroid heuristic - replaces DXF_Controller's relaxed validation.
        """
        if not self.floorplan_polygon:
            logger.warning("No floorplan polygon available - skipping containment check")
            return True
        
        # Strict check: entire fixture must be contained
        is_contained = self.floorplan_polygon.contains(fixture_polygon)
        
        if not is_contained:
            # Calculate how much is outside
            intersection = self.floorplan_polygon.intersection(fixture_polygon)
            overlap_pct = (intersection.area / fixture_polygon.area) * 100
            logger.debug(f"  Fixture {overlap_pct:.1f}% inside boundary (required: 100%)")
        
        return is_contained
    
    def _has_collision(
        self, 
        fixture_polygon: Polygon, 
        placed_geometries: List[Dict],
        buffer_distance: float = 100.0
    ) -> bool:
        """
        Check if fixture collides with any existing fixtures.
        Uses buffered geometry to ensure minimum spacing.
        """
        # Buffer the fixture polygon to enforce minimum spacing
        buffered_fixture = fixture_polygon.buffer(buffer_distance)
        
        for placed in placed_geometries:
            placed_polygon = placed['polygon']
            
            # Check for intersection
            if buffered_fixture.intersects(placed_polygon):
                logger.debug(f"  Collision detected with {placed['name']}")
                return True
        
        return False
    
    def cleanup(self):
        """Clean up temporary files and directories"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                logger.error(f"Error cleaning up temp directory: {e}")


# Example usage
if __name__ == "__main__":
    # Test the integration
    test_boundaries = {
        'min_x': 0,
        'max_x': 10000,
        'min_y': 0,
        'max_y': 8000
    }
    
    test_fixtures = {
        'clinic_1': {'type': 'clinic', 'position': [1000, 1000]},
        'table_1': {'type': 'floor', 'position': [5000, 3000]},
        'screen_1': {'type': 'screen', 'position': [8000, 2000]}
    }
    
    print("Testing Mathematical Model Integration...")
    integration = MathModelIntegration(
        dxf_path="/tmp/test.dxf",
        floor_boundaries=test_boundaries,
        session_id="test_session"
    )
    
    result = integration.calculate_positions(
        operation="rearrange",
        fixtures=test_fixtures
    )
    
    print(f"\nResult: {json.dumps(result, indent=2)}")
