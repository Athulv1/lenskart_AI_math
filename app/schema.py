from ninja import Schema # type: ignore
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid
from uuid import UUID

class ProjectFileSchema(Schema):
    id: UUID
    file_type: str
    filename: str
    created_at: datetime


class SiteMediaSchema(Schema):
    id: uuid.UUID
    filename: str
    file_type: str
    media_type: str
    created_at: datetime

class ProjectDetailSchema(Schema):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    status: str
    updated_by_name: Optional[str] = None
    fixtures: dict
    
    # Section 1: General Information
    address: Optional[str] = None
    location_reference: Optional[str] = None

    # Section 2: Site Details
    total_carpet_area: Optional[float] = None
    floor_level: Optional[str] = None
    electricity_load: Optional[float] = None
    electricity_meter_location: Optional[str] = None

    # Section 3: HVAC and Utilities
    hvac_system_type: Optional[str] = None
    ac_outdoor_units_location: Optional[str] = None
    drainage_facility: Optional[bool] = None
    water_connection: Optional[bool] = None

    # Section 4: Site Orientation and Access
    main_entrance_direction: Optional[str] = None
    nearest_airport: Optional[str] = None
    airport_distance: Optional[float] = None
    nearest_railway_station: Optional[str] = None
    railway_station_distance: Optional[float] = None

    # Section 5: Additional Facilities
    washroom: Optional[str] = None
    remarks: Optional[str] = None

    merch_mix_min: dict = {}
    merch_mix_max: dict = {}
    room_measurements: dict = {}
    
    # Files
    files: List[ProjectFileSchema]
    
    # Section 6: Site Pictures/Videos
    site_media: List[SiteMediaSchema]

    @staticmethod
    def resolve_updated_by_name(obj: "Project"):
        if obj.updated_by:
            return obj.updated_by.username
        return None

class ErrorSchema(Schema):
    message: str


class FileReferenceSchema(Schema):
    id: uuid.UUID

class ProjectUpdateSchema(Schema):
    # This schema includes ALL fields the user can edit.
    name: str
    description: Optional[str] = None
    status: str
    fixtures: dict

    # All other text/numeric fields...
    address: Optional[str] = None
    location_reference: Optional[str] = None
    total_carpet_area: Optional[float] = None
    floor_level: Optional[str] = None
    electricity_load: Optional[float] = None
    electricity_meter_location: Optional[str] = None
    hvac_system_type: Optional[str] = None
    ac_outdoor_units_location: Optional[str] = None
    drainage_facility: Optional[bool] = None
    water_connection: Optional[bool] = None
    main_entrance_direction: Optional[str] = None
    nearest_airport: Optional[str] = None
    airport_distance: Optional[float] = None
    nearest_railway_station: Optional[str] = None
    railway_station_distance: Optional[float] = None
    washroom: Optional[str] = None
    remarks: Optional[str] = None
    
    merch_mix_min: dict = {}
    merch_mix_max: dict = {}
    room_measurements: dict = {}

    # The mobile app will send a list of files it wants to KEEP.
    # We only need the ID for each file.
    files: List[FileReferenceSchema]
    site_media: List[FileReferenceSchema]
