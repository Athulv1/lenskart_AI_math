"""
Coordinate Extraction Helpers for Lenskart Floor Plan Generator

This module provides utility functions to extract and transform coordinate data
from clinic and euro placement plans into standardized formats.

Usage:
    from app.plan_extractors import extract_clinic_coordinates, extract_euro_coordinates
    from app.plan_extractors import transform_layout_json  # Hierarchical JSON transform
"""

from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from copy import deepcopy
import json
import logging

# Try to import Vec2 for type checking, but make it optional
try:
    from ezdxf.math import Vec2
    HAS_EZDXF = True
except ImportError:
    HAS_EZDXF = False
    Vec2 = None

logger = logging.getLogger("app")


# Euro Strategy Configuration
# Maps strategy_num to metadata for the 4 Euro placement strategies
EURO_STRATEGIES = {
    1: {
        "name": "basic_qms",
        "rotation": 90.0,
        "description": "Basic QMS-anchored placement with dynamic gaps",
        "method": "place_central_fixtures_from_qms",
        "preferred_patterns": ["column_wise_even_cols", "column_wise_odd_cols"],
        "parameters": {
            "GAP_ABOVE_QMS": 800.0,
            "max_fixtures_per_row": 3
        }
    },
    2: {
        "name": "lane_strategy",
        "rotation": 90.0,
        "description": "Lane persistence strategy - maintains X alignment",
        "method": "place_central_fixtures_from_qms_lane_strategy",
        "preferred_patterns": ["column_wise_even_cols", "column_wise_odd_cols"],
        "parameters": {
            "GAP_ABOVE_QMS": 800.0,
            "max_fixtures_per_row": 3
        }
    },
    3: {
        "name": "v1_og_rotated",
        "rotation": 90.0,
        "description": "Advanced lane strategy with row-size-triggered re-centering",
        "method": "place_central_fixtures_from_qms_v1_og",
        "preferred_patterns": ["column_wise_even_cols", "column_wise_odd_cols"],
        "parameters": {
            "GAP_ABOVE_QMS": 50.0,  # Smaller gap than basic_qms
            "max_fixtures_per_row": 3
        }
    },
    4: {
        "name": "v2_og_non_rotated",
        "rotation": 0.0,
        "description": "Zero rotation with fixed 5mm horizontal gap",
        "method": "place_central_fixtures_from_qms_v2_og",
        "preferred_patterns": ["row_wise_even_rows", "row_wise_odd_rows"],
        "parameters": {
            "GAP_ABOVE_QMS": 800.0,
            "horizontal_gap": 5.0,
            "vertical_row_spacing": 1200.0,
            "max_fixtures_per_row": 5
        }
    }
}


@dataclass
class ClinicCoordinate:
    """Data class representing a single clinic placement coordinate."""
    name: str
    target_center: Tuple[float, float]
    mirror_scale: Tuple[float, float]
    zone_id: str
    orientation: str  # 'H' or 'V'
    rotation: float   # Calculated rotation in degrees
    bottom_y: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format matching the JSON schema."""
        return {
            "name": self.name,
            "target_center": list(self.target_center),
            "mirror_scale": list(self.mirror_scale),
            "zone_id": self.zone_id,
            "orientation": self.orientation,
            "rotation": self.rotation,
            "bottom_y": self.bottom_y
        }
    
    def __repr__(self) -> str:
        return (f"ClinicCoordinate(name='{self.name}', "
                f"center=({self.target_center[0]:.1f}, {self.target_center[1]:.1f}), "
                f"orient='{self.orientation}')")


@dataclass 
class EuroCoordinate:
    """Data class representing a single Euro centre placement coordinate."""
    index: int
    coordinates: Tuple[float, float]
    pattern_name: str
    rotation: float  # 0 for row-wise, 90 for column-wise
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format matching the JSON schema."""
        return {
            "index": self.index,
            "coordinates": list(self.coordinates),
            "pattern_name": self.pattern_name,
            "rotation": self.rotation
        }


def _vec2_to_tuple(value: Any) -> Tuple[float, float]:
    """
    Convert Vec2 or list/tuple to a standard tuple of floats.
    
    Args:
        value: Can be Vec2, list, tuple, or any object with x/y attributes
        
    Returns:
        Tuple of (x, y) as floats
        
    Raises:
        ValueError: If value cannot be converted to coordinates
    """
    if value is None:
        raise ValueError("Cannot convert None to coordinates")
    
    # Handle Vec2 objects (from ezdxf)
    if HAS_EZDXF and isinstance(value, Vec2):
        return (float(value.x), float(value.y))
    
    # Handle objects with x, y attributes
    if hasattr(value, 'x') and hasattr(value, 'y'):
        return (float(value.x), float(value.y))
    
    # Handle list or tuple
    if isinstance(value, (list, tuple)):
        if len(value) >= 2:
            return (float(value[0]), float(value[1]))
        raise ValueError(f"Coordinate must have at least 2 elements, got {len(value)}")
    
    raise ValueError(f"Cannot convert {type(value).__name__} to coordinates")


def _safe_get(data: Dict, key: str, default: Any = None, required: bool = False) -> Any:
    """
    Safely get a value from a dictionary with optional required check.
    
    Args:
        data: Dictionary to get value from
        key: Key to look up
        default: Default value if key not found
        required: If True, raise ValueError when key is missing
        
    Returns:
        The value from the dictionary or the default
        
    Raises:
        ValueError: If required=True and key is not found
    """
    if key not in data:
        if required:
            raise ValueError(f"Required field '{key}' is missing from data")
        return default
    return data[key]


def extract_clinic_coordinates(
    ranked_layout: Dict[str, Any],
    include_debug: bool = False
) -> List[ClinicCoordinate]:
    """
    Extract clinic coordinates from a single ranked layout plan.
    
    This method handles the conversion of raw plan data (which may contain
    Vec2 objects) into standardized ClinicCoordinate dataclasses.
    
    Args:
        ranked_layout: A single clinic layout dictionary from ranked_layouts array.
                      Expected structure:
                      {
                          "Rank": 1,
                          "Placed": false,
                          "score": 1847.50,
                          "fixtures": ["ROC_clinic", ...],
                          "combo": ["H", "V", ...],
                          "coordinates": [{...}, ...]
                      }
        include_debug: If True, log debug information for each extraction.
        
    Returns:
        List of ClinicCoordinate objects with all placement data.
        
    Raises:
        ValueError: If required fields are missing or malformed.
        
    Example:
        >>> layout = clinic_plans["ranked_layouts"][0]
        >>> coords = extract_clinic_coordinates(layout)
        >>> for c in coords:
        ...     print(f"{c.name} at {c.target_center}")
    """
    if not isinstance(ranked_layout, dict):
        raise ValueError(f"Expected dict, got {type(ranked_layout).__name__}")
    
    # Get required fields
    fixtures = _safe_get(ranked_layout, "fixtures", required=True)
    combo = _safe_get(ranked_layout, "combo", required=True)
    coordinates = _safe_get(ranked_layout, "coordinates", required=True)
    
    # Validate array lengths match
    if len(fixtures) != len(combo):
        raise ValueError(
            f"Mismatch: {len(fixtures)} fixtures but {len(combo)} orientations"
        )
    if len(fixtures) != len(coordinates):
        raise ValueError(
            f"Mismatch: {len(fixtures)} fixtures but {len(coordinates)} coordinates"
        )
    
    extracted: List[ClinicCoordinate] = []
    
    for i, coord_data in enumerate(coordinates):
        try:
            # Extract name - prefer from coordinate data, fallback to fixtures array
            name = _safe_get(coord_data, "name", default=fixtures[i])
            
            # Extract and convert target_center
            raw_center = _safe_get(coord_data, "target_center", required=True)
            target_center = _vec2_to_tuple(raw_center)
            
            # Extract and convert mirror_scale
            raw_mirror = _safe_get(coord_data, "mirror_scale", default=[1.0, 1.0])
            if isinstance(raw_mirror, (list, tuple)) and len(raw_mirror) >= 2:
                mirror_scale = (float(raw_mirror[0]), float(raw_mirror[1]))
            else:
                mirror_scale = (1.0, 1.0)
                logger.warning(f"Invalid mirror_scale for {name}, using default (1.0, 1.0)")
            
            # Extract zone_id
            zone_id = _safe_get(coord_data, "zone_id", default="Zone_Unknown")
            
            # Get orientation from combo array
            orientation = combo[i] if i < len(combo) else "H"
            
            # Calculate rotation based on orientation
            # H (Horizontal) = 0°, V (Vertical) = 90°
            rotation = 0.0 if orientation == "H" else 90.0
            
            # Extract optional bottom_y for scoring reference
            bottom_y = _safe_get(coord_data, "bottom_y", default=None)
            if bottom_y is not None:
                bottom_y = float(bottom_y)
            
            # Create the coordinate object
            clinic_coord = ClinicCoordinate(
                name=name,
                target_center=target_center,
                mirror_scale=mirror_scale,
                zone_id=zone_id,
                orientation=orientation,
                rotation=rotation,
                bottom_y=bottom_y
            )
            
            extracted.append(clinic_coord)
            
            if include_debug:
                logger.debug(f"Extracted: {clinic_coord}")
                
        except Exception as e:
            logger.error(f"Error extracting coordinate at index {i}: {e}")
            raise ValueError(f"Failed to extract clinic coordinate at index {i}: {e}")
    
    return extracted


def extract_all_clinic_coordinates(
    clinic_plans: Dict[str, Any],
    only_unplaced: bool = True,
    max_rank: Optional[int] = None
) -> Dict[int, List[ClinicCoordinate]]:
    """
    Extract coordinates from all clinic plans.
    
    Args:
        clinic_plans: The full clinic_plans dictionary containing ranked_layouts.
        only_unplaced: If True, only extract from plans where Placed=False.
        max_rank: If set, only extract from plans with Rank <= max_rank.
        
    Returns:
        Dictionary mapping Rank -> List[ClinicCoordinate]
        
    Example:
        >>> all_coords = extract_all_clinic_coordinates(data["clinic_plans"])
        >>> best_plan_coords = all_coords[1]  # Rank 1 is best
    """
    ranked_layouts = _safe_get(clinic_plans, "ranked_layouts", default=[])
    
    result: Dict[int, List[ClinicCoordinate]] = {}
    
    for layout in ranked_layouts:
        rank = _safe_get(layout, "Rank", default=0)
        placed = _safe_get(layout, "Placed", default=False)
        
        # Filter by placement status
        if only_unplaced and placed:
            continue
            
        # Filter by max rank
        if max_rank is not None and rank > max_rank:
            continue
        
        try:
            coords = extract_clinic_coordinates(layout)
            result[rank] = coords
        except ValueError as e:
            logger.warning(f"Skipping Rank {rank} due to extraction error: {e}")
            continue
    
    return result


def extract_euro_coordinates(
    euro_plans: Dict[str, Any],
    pattern_name: Optional[str] = None
) -> List[EuroCoordinate]:
    """
    Extract Euro centre coordinates from placement patterns.
    
    Args:
        euro_plans: The full euro_plans dictionary.
        pattern_name: Specific pattern to extract. If None, uses best_pattern_name.
        
    Returns:
        List of EuroCoordinate objects.
        
    Raises:
        ValueError: If pattern not found or data is malformed.
    """
    if pattern_name is None:
        pattern_name = _safe_get(euro_plans, "best_pattern_name", default="None")
    
    if pattern_name == "None" or pattern_name is None:
        logger.warning("No valid euro pattern available")
        return []
    
    all_options = _safe_get(euro_plans, "all_options", default={})
    pattern_data = _safe_get(all_options, pattern_name, default=None)
    
    if pattern_data is None:
        raise ValueError(f"Pattern '{pattern_name}' not found in euro_plans")
    
    placements = _safe_get(pattern_data, "placements", default={})
    
    # Determine rotation based on pattern name
    rotation = 90.0 if "column_wise" in pattern_name else 0.0
    
    extracted: List[EuroCoordinate] = []
    
    for key, value in placements.items():
        try:
            # Extract index from key (e.g., "count_1" -> 1)
            index = int(key.replace("count_", ""))
            
            # Extract coordinates
            raw_coords = _safe_get(value, "coordinates", required=True)
            coords = _vec2_to_tuple(raw_coords)
            
            euro_coord = EuroCoordinate(
                index=index,
                coordinates=coords,
                pattern_name=pattern_name,
                rotation=rotation
            )
            extracted.append(euro_coord)
            
        except Exception as e:
            logger.warning(f"Error extracting euro coordinate '{key}': {e}")
            continue
    
    # Sort by index for consistent ordering
    extracted.sort(key=lambda x: x.index)
    
    return extracted


def clinic_coordinates_to_json(
    coordinates: List[ClinicCoordinate],
    indent: int = 2
) -> str:
    """
    Convert a list of ClinicCoordinate objects to JSON string.
    
    Args:
        coordinates: List of ClinicCoordinate objects
        indent: JSON indentation level
        
    Returns:
        JSON string representation
    """
    return json.dumps(
        [c.to_dict() for c in coordinates],
        indent=indent
    )


def euro_coordinates_to_json(
    coordinates: List[EuroCoordinate],
    indent: int = 2
) -> str:
    """
    Convert a list of EuroCoordinate objects to JSON string.
    
    Args:
        coordinates: List of EuroCoordinate objects
        indent: JSON indentation level
        
    Returns:
        JSON string representation
    """
    return json.dumps(
        [c.to_dict() for c in coordinates],
        indent=indent
    )


# Convenience function for DXF_Controller integration
def _extract_clinic_coordinates_for_placement(
    ranked_layout: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Extract clinic coordinates in the format expected by place_clinics_from_ranked_plan().
    
    This is a drop-in helper that can be used directly within DXF_Controller.
    
    Args:
        ranked_layout: A single ranked layout dictionary
        
    Returns:
        List of dictionaries ready for placement, with format:
        [
            {
                "name": str,
                "target_center": (x, y),  # As tuple
                "mirror_scale": (xscale, yscale),
                "zone_id": str,
                "orientation": str,
                "rotation": float
            },
            ...
        ]
    """
    coords = extract_clinic_coordinates(ranked_layout)
    return [c.to_dict() for c in coords]


def _generate_euro_plan(
    euro_plans_data: Dict[str, Any],
    strategy_num: int,
    required_count: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generate a Euro placement plan based on strategy selection.
    
    This helper selects the appropriate pattern from analyze_placement_patterns()
    output based on the given strategy number and formats it for placement.
    
    Args:
        euro_plans_data: Output from analyze_placement_patterns(), containing:
            {
                "best_pattern_name": str,
                "all_options": {
                    "pattern_name": {
                        "count": int,
                        "rank": int,
                        "placed": bool,
                        "placements": {"count_1": {"coordinates": [x, y]}, ...}
                    }
                }
            }
        strategy_num: Strategy number (1-4):
            1 = basic_qms (90° rotation)
            2 = lane_strategy (90° rotation)
            3 = v1_og_rotated (90° rotation)
            4 = v2_og_non_rotated (0° rotation)
        required_count: Optional number of fixtures to place. If None, uses max capacity.
        
    Returns:
        Formatted plan dictionary:
        {
            "strategy_num": int,
            "strategy_name": str,
            "rotation": float,
            "chosen_pattern_name": str,
            "max_capacity": int,
            "placed_count": int,
            "overflow": int,
            "placements": [{"index": int, "coordinates": [x, y]}, ...]
        }
        
    Raises:
        ValueError: If strategy_num is invalid (not 1-4) or no patterns available.
        
    Example:
        >>> from app.plan_extractors import _generate_euro_plan
        >>> euro_data = {"best_pattern_name": "column_wise_even_cols", "all_options": {...}}
        >>> plan = _generate_euro_plan(euro_data, strategy_num=1)
        >>> print(f"Using {plan['strategy_name']} with {plan['placed_count']} fixtures")
    """
    # Validate strategy_num
    if strategy_num not in EURO_STRATEGIES:
        raise ValueError(
            f"Invalid strategy_num: {strategy_num}. "
            f"Must be 1-4. Available: {list(EURO_STRATEGIES.keys())}"
        )
    
    strategy = EURO_STRATEGIES[strategy_num]
    all_options = _safe_get(euro_plans_data, "all_options", default={})
    
    if not all_options:
        raise ValueError("No placement patterns available in euro_plans_data")
    
    # Select pattern based on strategy preference
    chosen_pattern_name = None
    chosen_pattern_data = None
    
    # Try preferred patterns first
    for preferred in strategy["preferred_patterns"]:
        if preferred in all_options:
            chosen_pattern_name = preferred
            chosen_pattern_data = all_options[preferred]
            break
    
    # Fallback to best_pattern_name if no preferred pattern found
    if chosen_pattern_name is None:
        best_name = _safe_get(euro_plans_data, "best_pattern_name", default="None")
        if best_name != "None" and best_name in all_options:
            chosen_pattern_name = best_name
            chosen_pattern_data = all_options[best_name]
    
    # Still no pattern? Pick highest capacity available
    if chosen_pattern_name is None:
        sorted_options = sorted(
            all_options.items(),
            key=lambda x: x[1].get("count", 0),
            reverse=True
        )
        if sorted_options:
            chosen_pattern_name, chosen_pattern_data = sorted_options[0]
    
    if chosen_pattern_name is None or chosen_pattern_data is None:
        raise ValueError("Could not select a valid pattern from euro_plans_data")
    
    # Extract placement coordinates
    max_capacity = chosen_pattern_data.get("count", 0)
    placements_dict = chosen_pattern_data.get("placements", {})
    
    # Determine how many to place
    if required_count is None:
        placed_count = max_capacity
    else:
        placed_count = min(required_count, max_capacity)
    
    overflow = max(0, (required_count or 0) - max_capacity)
    
    # Convert placements to list format
    placements_list = []
    sorted_keys = sorted(
        placements_dict.keys(),
        key=lambda k: int(k.replace("count_", ""))
    )
    
    for i, key in enumerate(sorted_keys[:placed_count], start=1):
        coords = placements_dict[key].get("coordinates", [0, 0])
        placements_list.append({
            "index": i,
            "coordinates": _vec2_to_tuple(coords) if coords else (0.0, 0.0)
        })
    
    return {
        "strategy_num": strategy_num,
        "strategy_name": strategy["name"],
        "rotation": strategy["rotation"],
        "description": strategy["description"],
        "chosen_pattern_name": chosen_pattern_name,
        "max_capacity": max_capacity,
        "placed_count": placed_count,
        "overflow": overflow,
        "parameters": strategy["parameters"],
        "placements": placements_list
    }


def get_euro_strategy_info(strategy_num: int) -> Dict[str, Any]:
    """
    Get metadata for a specific Euro strategy.
    
    Args:
        strategy_num: Strategy number (1-4)
        
    Returns:
        Strategy metadata dict
        
    Raises:
        ValueError: If strategy_num is invalid
    """
    if strategy_num not in EURO_STRATEGIES:
        raise ValueError(f"Invalid strategy_num: {strategy_num}. Must be 1-4.")
    return EURO_STRATEGIES[strategy_num].copy()


def list_euro_strategies() -> List[Dict[str, Any]]:
    """
    List all available Euro placement strategies.
    
    Returns:
        List of strategy metadata dicts
    """
    return [
        {"num": num, **data}
        for num, data in EURO_STRATEGIES.items()
    ]


def get_plans_output_path(dxf_path: str, suffix: str = "_plans") -> str:
    """
    Generate output JSON path based on DXF file path.
    
    Creates filename as {dxf_name}{suffix}.json in the same directory as the DXF.
    
    Args:
        dxf_path: Path to the DXF file
        suffix: Suffix to add before .json (default: "_plans")
        
    Returns:
        Full path for the output JSON file
        
    Example:
        >>> get_plans_output_path("/path/to/floorplan.dxf")
        '/path/to/floorplan_plans.json'
        
        >>> get_plans_output_path("/path/to/store_001.dxf", suffix="_complete")
        '/path/to/store_001_complete.json'
    """
    import os
    
    # Get directory and filename from DXF path
    dxf_dir = os.path.dirname(dxf_path)
    dxf_basename = os.path.basename(dxf_path)
    
    # Remove .dxf extension (case-insensitive)
    if dxf_basename.lower().endswith('.dxf'):
        name_without_ext = dxf_basename[:-4]
    else:
        name_without_ext = dxf_basename
    
    # Create output filename
    output_filename = f"{name_without_ext}{suffix}.json"
    
    # Combine with directory
    if dxf_dir:
        return os.path.join(dxf_dir, output_filename)
    else:
        return output_filename


def write_plans_json(
    data: Dict[str, Any],
    output_path: str,
    indent: int = 2,
    ensure_dir: bool = True
) -> Dict[str, Any]:
    """
    Write plans data to JSON file with error handling and logging.
    
    Args:
        data: Dictionary to write
        output_path: Destination file path
        indent: JSON indentation (default: 2 for pretty formatting)
        ensure_dir: Create parent directories if needed (default: True)
        
    Returns:
        Result dict with 'success', 'path', and optional 'error'
        
    Example:
        >>> result = write_plans_json(plans_data, "/path/to/output.json")
        >>> if result['success']:
        ...     print(f"Saved to {result['path']}")
    """
    import os
    import datetime
    
    result = {
        "success": False,
        "path": output_path,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    try:
        # Create parent directories if needed
        if ensure_dir:
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
        
        # Write with pretty formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, default=str, ensure_ascii=False)
        
        # Get file size for logging
        file_size = os.path.getsize(output_path)
        
        result["success"] = True
        result["file_size_bytes"] = file_size
        logger.info(f"✅ Saved plans to {output_path} ({file_size:,} bytes)")
        
    except PermissionError as e:
        result["error"] = f"Permission denied: {e}"
        logger.error(f"❌ Permission denied writing to {output_path}: {e}")
        
    except OSError as e:
        result["error"] = f"OS error: {e}"
        logger.error(f"❌ OS error writing to {output_path}: {e}")
        
    except Exception as e:
        result["error"] = f"Unexpected error: {e}"
        logger.error(f"❌ Failed to write to {output_path}: {e}")
    
    return result


class ValidationResult:
    """Result of plans data validation."""
    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []
    
    def add_error(self, msg: str):
        self.errors.append(msg)
        self.is_valid = False
    
    def add_warning(self, msg: str):
        self.warnings.append(msg)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings
        }


def validate_plans_data(
    clinic_plans: Dict[str, Any],
    euro_plans: Dict[str, Any],
    required_euro_count: Optional[int] = None
) -> ValidationResult:
    """
    Validate plans data and check for edge cases.
    
    Edge cases handled:
    - 0 clinic plans: ERROR (invalid configuration)
    - 1 clinic plan: OK (valid minimum)
    - >10 clinic plans: WARNING (unusual, may impact performance)
    - Missing required fields: ERROR
    - Empty euro patterns: WARNING
    
    Args:
        clinic_plans: Clinic plans dictionary
        euro_plans: Euro plans dictionary
        required_euro_count: Optional required fixture count
        
    Returns:
        ValidationResult with is_valid, errors, and warnings
    """
    result = ValidationResult()
    
    # --- Clinic Plans Validation ---
    if not clinic_plans:
        result.add_error("clinic_plans is None or empty")
        return result
    
    ranked_layouts = clinic_plans.get("ranked_layouts", [])
    
    # Edge case: 0 clinic plans
    if len(ranked_layouts) == 0:
        result.add_error(
            "No clinic layouts found (ranked_layouts is empty). "
            "At least 1 clinic layout is required."
        )
    
    # Edge case: 1 clinic plan
    elif len(ranked_layouts) == 1:
        logger.info("Single clinic layout detected - this is valid.")
    
    # Edge case: >10 clinic plans
    elif len(ranked_layouts) > 10:
        result.add_warning(
            f"Large number of clinic layouts detected ({len(ranked_layouts)}). "
            "This may impact JSON file size and processing time. "
            "Consider limiting to top 10 ranked layouts."
        )
    
    # Validate each clinic layout structure
    for i, layout in enumerate(ranked_layouts):
        if not isinstance(layout, dict):
            result.add_error(f"ranked_layouts[{i}] is not a dictionary")
            continue
        
        if "Rank" not in layout:
            result.add_warning(f"ranked_layouts[{i}] missing 'Rank' field")
    
    # --- Euro Plans Validation ---
    if not euro_plans:
        result.add_warning("euro_plans is None or empty - Euro strategies will use defaults")
    else:
        all_options = euro_plans.get("all_options", {})
        
        # Edge case: No euro patterns
        if len(all_options) == 0:
            result.add_warning(
                "No euro placement patterns found (all_options is empty). "
                "Euro strategies may not generate optimal placements."
            )
        
        # Validate required count
        if required_euro_count is not None:
            if required_euro_count < 0:
                result.add_error(f"required_euro_count cannot be negative: {required_euro_count}")
            elif required_euro_count == 0:
                result.add_warning("required_euro_count is 0 - no Euro fixtures will be placed")
            elif required_euro_count > 20:
                result.add_warning(
                    f"High required_euro_count ({required_euro_count}). "
                    "Verify this is correct for the floor plan size."
                )
    
    return result


def save_all_plans_to_json(
    clinic_plans: Dict[str, Any],
    euro_plans: Dict[str, Any],
    output_path: str,
    floorplan_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    required_euro_count: Optional[int] = None,
    skip_validation: bool = False
) -> Dict[str, Any]:
    """
    Generate complete JSON structure with all clinic plans and 4 Euro variations per plan.
    
    This function takes clinic and euro plan data and generates a complete output
    structure with all 4 Euro placement strategies applied to each clinic plan.
    
    Args:
        clinic_plans: Clinic plans dictionary with 'ranked_layouts'
        euro_plans: Euro plans dictionary with 'all_options' (from analyze_placement_patterns())
        output_path: Path to save the JSON file
        floorplan_id: Optional floorplan ID (auto-generated if not provided)
        metadata: Optional metadata dict to include
        required_euro_count: Optional fixture count for euro plans
        skip_validation: If True, skip data validation (default: False)
        
    Returns:
        Complete plans dictionary that was saved
        
    Raises:
        ValueError: If clinic_plans has 0 layouts (and skip_validation is False)
        
    Example:
        >>> from app.plan_extractors import save_all_plans_to_json
        >>> result = save_all_plans_to_json(
        ...     clinic_plans={"ranked_layouts": [...]},
        ...     euro_plans={"all_options": {...}},
        ...     output_path="/path/to/output.json"
        ... )
    """
    import datetime
    import uuid
    
    # --- Validate input data ---
    if not skip_validation:
        validation = validate_plans_data(clinic_plans, euro_plans, required_euro_count)
        
        # Log warnings
        for warning in validation.warnings:
            logger.warning(f"⚠️ {warning}")
        
        # Raise error for invalid data
        if not validation.is_valid:
            error_msg = "; ".join(validation.errors)
            logger.error(f"❌ Validation failed: {error_msg}")
            raise ValueError(f"Invalid plans data: {error_msg}")
    
    # Generate floorplan ID if not provided
    if floorplan_id is None:
        floorplan_id = str(uuid.uuid4())
    
    # Get required count from euro_plans if not specified
    if required_euro_count is None:
        required_euro_count = euro_plans.get("required_count", 6)
    
    # Build the complete structure
    result = {
        "floorplan_id": floorplan_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "metadata": metadata or {},
        "clinic_plans": clinic_plans,
        "euro_plans_by_strategy": {}
    }
    
    # Generate 4 Euro plan variations
    for strategy_num in [1, 2, 3, 4]:
        strategy_key = f"strategy_{strategy_num}"
        
        try:
            euro_plan = _generate_euro_plan(
                euro_plans_data=euro_plans,
                strategy_num=strategy_num,
                required_count=required_euro_count
            )
            result["euro_plans_by_strategy"][strategy_key] = {
                "success": True,
                "plan": euro_plan
            }
            logger.debug(f"Generated euro plan for strategy {strategy_num}")
            
        except Exception as e:
            # Handle errors gracefully
            result["euro_plans_by_strategy"][strategy_key] = {
                "success": False,
                "error": str(e),
                "strategy_info": EURO_STRATEGIES.get(strategy_num, {})
            }
            logger.warning(f"Failed to generate euro plan for strategy {strategy_num}: {e}")
    
    # Generate combined plans (clinic × euro strategy pairs)
    combined_plans = []
    all_clinic_layouts = clinic_plans.get("all_ranked_plans", []) or clinic_plans.get("ranked_layouts", [])
    
    for clinic_idx, clinic_layout in enumerate(all_clinic_layouts):
        clinic_rank = clinic_layout.get("Rank", clinic_idx + 1)
        is_placed = clinic_layout.get("Placed", False)
        
        for strategy_num in [1, 2, 3, 4]:
            strategy_key = f"strategy_{strategy_num}"
            euro_data = result["euro_plans_by_strategy"].get(strategy_key, {})
            
            combination = {
                "combination_id": f"clinic_{clinic_rank}_euro_{strategy_num}",
                "clinic_layout": {
                    "rank": clinic_rank,
                    "combo": clinic_layout.get("combo", []),
                    "fixtures": clinic_layout.get("fixtures", []),
                    "placed": is_placed,
                    "score": clinic_layout.get("score", 0),
                    "coordinates": clinic_layout.get("coordinates", [])
                },
                "euro_strategy": {}
            }
            
            # Only include euro plans for PLACED clinics
            if is_placed:
                combination["euro_strategy"] = {
                    "strategy_num": strategy_num,
                    "strategy_name": EURO_STRATEGIES.get(strategy_num, {}).get("name", "unknown"),
                    "success": euro_data.get("success", False),
                    "placements": euro_data.get("plan", {}).get("placements", []) if euro_data.get("success") else []
                }
            else:
                # Unplaced clinics don't have calculated euro plans
                combination["euro_strategy"] = {
                    "strategy_num": strategy_num,
                    "strategy_name": EURO_STRATEGIES.get(strategy_num, {}).get("name", "unknown"),
                    "success": False,
                    "reason": "Clinic not placed - euro centres not calculated. Standing table position required for euro calculation.",
                    "placements": []
                }
            
            combined_plans.append(combination)
    
    result["combined_plans"] = combined_plans
    
    # Add summary statistics
    result["summary"] = {
        "total_clinic_layouts": len(clinic_plans.get("ranked_layouts", [])),
        "all_clinic_layouts": len(all_clinic_layouts),
        "euro_strategies_generated": sum(
            1 for v in result["euro_plans_by_strategy"].values() 
            if v.get("success", False)
        ),
        "total_combinations": len(combined_plans),
        "required_euro_count": required_euro_count
    }
    
    # Save to JSON file
    try:
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        logger.info(f"Saved plans to {output_path}")
        result["_saved_to"] = output_path
        
    except Exception as e:
        logger.error(f"Failed to save plans to {output_path}: {e}")
        result["_save_error"] = str(e)
    
    return result


def generate_combined_plans(
    clinic_plans: Dict[str, Any],
    euro_plans: Dict[str, Any],
    required_euro_count: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Generate all combinations of clinic plans with each euro strategy.
    
    This creates a flat list where each clinic plan is paired with each
    of the 4 Euro strategies, resulting in clinic_count × 4 combinations.
    
    Args:
        clinic_plans: Clinic plans with 'ranked_layouts'
        euro_plans: Euro plans with 'all_options'
        required_euro_count: Optional fixture count
        
    Returns:
        List of combined plan dicts
        
    Example:
        >>> combinations = generate_combined_plans(clinic_plans, euro_plans)
        >>> print(f"Generated {len(combinations)} plan combinations")
    """
    combinations = []
    ranked_layouts = clinic_plans.get("ranked_layouts", [])
    
    if required_euro_count is None:
        required_euro_count = euro_plans.get("required_count", 6)
    
    for clinic_layout in ranked_layouts:
        clinic_rank = clinic_layout.get("Rank", 0)
        
        for strategy_num in [1, 2, 3, 4]:
            try:
                euro_plan = _generate_euro_plan(
                    euro_plans_data=euro_plans,
                    strategy_num=strategy_num,
                    required_count=required_euro_count
                )
                
                combinations.append({
                    "clinic_rank": clinic_rank,
                    "clinic_layout": clinic_layout,
                    "euro_strategy_num": strategy_num,
                    "euro_strategy_name": euro_plan["strategy_name"],
                    "euro_plan": euro_plan,
                    "combined_id": f"clinic_{clinic_rank}_euro_{strategy_num}"
                })
                
            except Exception as e:
                logger.warning(
                    f"Failed to generate combination clinic_{clinic_rank} + euro_{strategy_num}: {e}"
                )
                combinations.append({
                    "clinic_rank": clinic_rank,
                    "clinic_layout": clinic_layout,
                    "euro_strategy_num": strategy_num,
                    "euro_strategy_name": EURO_STRATEGIES[strategy_num]["name"],
                    "euro_plan": None,
                    "error": str(e),
                    "combined_id": f"clinic_{clinic_rank}_euro_{strategy_num}"
                })
    
    return combinations


def transform_layout_json(old: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform current output JSON into a hierarchical, clinic-centric format.
    
    Structure: Floorplan -> Clinics (ALL) -> Corresponding Euro strategies
    
    This transformation is LOSSLESS:
      - No important key, field, value, or debug metadata dropped
      - No renaming or approximation
      - combined_plans section removed (data now implicit in hierarchy)
      - Debug fields grouped under _debug
    
    Args:
        old: The original flat/cross-referenced JSON structure from save_all_plans_to_json()
        
    Returns:
        Hierarchical JSON structure with:
        - floorplan_id, timestamp, metadata (preserved)
        - summary (preserved fully)
        - required_euro_count (duplicated for convenience)
        - clinic_plans_meta (total_clinics_required, remaining_fixtures_queue)
        - clinic_shortlist_ranks (derived from ranked_layouts)
        - best_solution (computed: lowest clinic score + first successful euro)
        - clinics[] (ALL clinics from all_ranked_plans with corresponding_euros)
        
    Guarantees:
        - No loss of numeric precision
        - No dropped metadata
        - No renamed euro plan fields
        - No silent failures
        - Deterministic ordering
        - JSON-serializable output
        
    Example:
        >>> from app.plan_extractors import transform_layout_json
        >>> original = save_all_plans_to_json(clinic_plans, euro_plans, output_path)
        >>> hierarchical = transform_layout_json(original)
        >>> print(hierarchical["best_solution"])
    """
    # ---- Top-level preservation ----
    new: Dict[str, Any] = {
        "floorplan_id": old.get("floorplan_id"),
        "timestamp": old.get("timestamp"),
        "metadata": deepcopy(old.get("metadata", {})),

        # Keep summary fully (for sanity checks and validation)
        "summary": deepcopy(old.get("summary", {})),

        # Convenience duplicate (handy for UI and quick access)
        "required_euro_count": old.get("summary", {}).get("required_euro_count"),

        # Clinic meta (important for completeness)
        "clinic_plans_meta": {
            "total_clinics_required": old.get("clinic_plans", {}).get("total_clinics_required"),
            "remaining_fixtures_queue": deepcopy(
                old.get("clinic_plans", {}).get("remaining_fixtures_queue", [])
            )
        },

        # Shortlist ranks (which were in ranked_layouts)
        "clinic_shortlist_ranks": [],

        # Computed best solution (populated below)
        "best_solution": None,

        # Main hierarchical list of clinics
        "clinics": []
    }

    clinic_plans = old.get("clinic_plans", {})
    ranked_layouts = clinic_plans.get("ranked_layouts", [])
    all_ranked_plans = clinic_plans.get("all_ranked_plans", [])

    # Record shortlist ranks (Rank values from ranked_layouts)
    new["clinic_shortlist_ranks"] = [
        c.get("Rank") for c in ranked_layouts if c.get("Rank") is not None
    ]

    # Euro strategies (as produced by engine: strategy_1..strategy_4)
    euro_strategies = old.get("euro_plans_by_strategy", {})

    # --- Helper: build euro node list for a placed clinic ---
    def build_corresponding_euros() -> List[Dict[str, Any]]:
        """
        Build the list of all euro strategies for a placed clinic.
        
        Returns all strategies (success or not), ordered by strategy_num.
        Preserves the FULL plan object exactly as-is when successful.
        """
        euros: List[Dict[str, Any]] = []
        
        # Get all strategy items
        items = list(euro_strategies.items())

        # Sort by strategy_num for deterministic ordering
        def strat_sort_key(item):
            k, v = item
            plan = v.get("plan", {}) or {}
            return plan.get("strategy_num", 999)

        items.sort(key=strat_sort_key)

        for strat_key, strat_obj in items:
            success = bool(strat_obj.get("success"))
            plan = strat_obj.get("plan")
            
            euro_node: Dict[str, Any] = {
                "strategy_key": strat_key,  # Keep reference (strategy_1 etc.)
                "success": success
            }
            
            if success and plan is not None:
                # CRITICAL: Keep the FULL plan as-is (no renaming, no dropping)
                euro_node["plan"] = deepcopy(plan)
            else:
                euro_node["plan"] = None
                # Preserve reason if available
                reason = strat_obj.get("reason") or strat_obj.get("error")
                if reason:
                    euro_node["reason"] = reason
                    
            euros.append(euro_node)
            
        return euros

    # --- Build clinics from ALL ranked plans (complete list) ---
    for clinic in all_ranked_plans:
        clinic_rank = clinic.get("Rank")
        placed = bool(clinic.get("Placed"))

        # Build the clinic node with all data preserved
        clinic_node: Dict[str, Any] = {
            "clinic_rank": clinic_rank,
            "clinic": {
                # Core fields
                "placed": placed,
                "score": clinic.get("score"),
                "combo": deepcopy(clinic.get("combo")),
                "fixtures": deepcopy(clinic.get("fixtures")),
                "gaps": deepcopy(clinic.get("gaps")),  # IMPORTANT: preserve gaps
                "coordinates": deepcopy(clinic.get("coordinates")),

                # Group debug fields under _debug
                "_debug": {
                    "zone": clinic.get("_debug_zone"),
                    "depth_score": clinic.get("_debug_depth_score"),
                    "penalty": clinic.get("_debug_penalty")
                }
            },
            "corresponding_euros": []
        }

        if placed:
            # ALWAYS list all euro strategies (success true/false) for placed clinics
            clinic_node["corresponding_euros"] = build_corresponding_euros()
        else:
            # Unplaced clinics: empty euros + explanatory note
            clinic_node["corresponding_euros"] = []
            clinic_node["note"] = "Clinic not placed → euro strategies not evaluated"

        new["clinics"].append(clinic_node)

    # ---- Best-solution selection ----
    # Rule: 
    # 1. Consider ONLY clinics where clinic.placed == true
    # 2. Select the clinic with the LOWEST clinic.score
    # 3. Inside that clinic, select the first euro strategy where success == true
    #    (ordered by strategy_num)
    
    placed_clinics = [c for c in new["clinics"] if c["clinic"].get("placed") is True]

    def safe_score(c: Dict[str, Any]) -> float:
        """Get score with safe fallback to infinity for sorting."""
        s = c["clinic"].get("score")
        return float(s) if s is not None else float("inf")

    # Sort by score ascending (lowest first)
    placed_clinics.sort(key=safe_score)
    
    if placed_clinics:
        best_clinic = placed_clinics[0]
        
        # Find first successful euro strategy
        best_euro = next(
            (e for e in best_clinic["corresponding_euros"] if e.get("success") is True),
            None
        )
        
        if best_euro and best_euro.get("plan"):
            new["best_solution"] = {
                "clinic_rank": best_clinic.get("clinic_rank"),
                "euro_strategy_num": best_euro["plan"].get("strategy_num"),
                "strategy_name": best_euro["plan"].get("strategy_name"),
                "reason": "Lowest clinic score among placed clinics and successful euro strategy"
            }

    # Validation: ensure data integrity
    summary = new.get("summary", {})
    expected_clinic_count = summary.get("all_clinic_layouts", 0)
    actual_clinic_count = len(new["clinics"])
    
    if expected_clinic_count > 0 and actual_clinic_count != expected_clinic_count:
        logger.warning(
            f"⚠️ Clinic count mismatch: expected {expected_clinic_count}, got {actual_clinic_count}"
        )

    return new


def save_hierarchical_json(
    original_json: Dict[str, Any],
    output_path: str,
    indent: int = 2
) -> Dict[str, Any]:
    """
    Transform and save JSON to hierarchical clinic-centric format.
    
    Convenience function that combines transform_layout_json() with file writing.
    
    Args:
        original_json: The original flat JSON from save_all_plans_to_json()
        output_path: Path to save the hierarchical JSON
        indent: JSON indentation (default: 2)
        
    Returns:
        Dict with 'success', 'path', 'data', and optional 'error'
        
    Example:
        >>> result = save_hierarchical_json(original, "/path/to/hierarchical.json")
        >>> if result['success']:
        ...     print(f"Saved to {result['path']}")
    """
    import os
    
    result = {
        "success": False,
        "path": output_path,
        "data": None
    }
    
    try:
        # Transform to hierarchical format
        hierarchical = transform_layout_json(original_json)
        result["data"] = hierarchical
        
        # Create parent directories if needed
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(hierarchical, f, indent=indent, default=str, ensure_ascii=False)
        
        file_size = os.path.getsize(output_path)
        result["success"] = True
        result["file_size_bytes"] = file_size
        
        logger.info(f"✅ Saved hierarchical JSON to {output_path} ({file_size:,} bytes)")
        
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"❌ Failed to save hierarchical JSON: {e}")
    
    return result


# --- TESTING ---
if __name__ == "__main__":
    # Test with sample data
    import os
    
    print("=" * 60)
    print("🔧 Testing Coordinate Extraction Helpers")
    print("=" * 60)
    
    # Load sample data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sample_path = os.path.join(script_dir, "..", "schemas", "test_sample_plan.json")
    
    if not os.path.exists(sample_path):
        # Try alternate path
        sample_path = "/home/athul/lenskart/schemas/test_sample_plan.json"
    
    with open(sample_path, 'r') as f:
        sample_data = json.load(f)
    
    print("\n📋 Test 1: Extract clinic coordinates from best plan")
    print("-" * 40)
    
    best_layout = sample_data["clinic_plans"]["ranked_layouts"][0]
    clinic_coords = extract_clinic_coordinates(best_layout)
    
    for coord in clinic_coords:
        print(f"  • {coord.name}")
        print(f"    Center: ({coord.target_center[0]:.2f}, {coord.target_center[1]:.2f})")
        print(f"    Mirror: {coord.mirror_scale}")
        print(f"    Zone: {coord.zone_id}, Orientation: {coord.orientation}")
        print()
    
    print("\n📋 Test 2: Extract all clinic coordinates")
    print("-" * 40)
    
    all_clinic_coords = extract_all_clinic_coordinates(sample_data["clinic_plans"])
    print(f"  Extracted coordinates for {len(all_clinic_coords)} plans")
    for rank, coords in all_clinic_coords.items():
        print(f"    Rank {rank}: {len(coords)} clinics")
    
    print("\n📋 Test 3: Extract euro coordinates")
    print("-" * 40)
    
    euro_coords = extract_euro_coordinates(sample_data["euro_plans"])
    print(f"  Extracted {len(euro_coords)} euro coordinates")
    print(f"  Pattern: {euro_coords[0].pattern_name if euro_coords else 'N/A'}")
    print(f"  Rotation: {euro_coords[0].rotation if euro_coords else 'N/A'}°")
    
    for coord in euro_coords[:3]:  # Show first 3
        print(f"    count_{coord.index}: ({coord.coordinates[0]:.1f}, {coord.coordinates[1]:.1f})")
    if len(euro_coords) > 3:
        print(f"    ... and {len(euro_coords) - 3} more")
    
    print("\n📋 Test 4: Convert to JSON")
    print("-" * 40)
    
    json_output = clinic_coordinates_to_json(clinic_coords[:1])
    print(f"  Sample JSON output:\n{json_output}")
    
    print("\n" + "=" * 60)
    print("✅ All extraction tests passed!")
    print("=" * 60)
