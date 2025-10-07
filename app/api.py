from datetime import datetime
import logging
import json
import subprocess
import tempfile
import sys
import os
import uuid
from typing import List, Optional, Any
import importlib.util
import traceback
from django.core.files import File as DjangoFile
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ninja import NinjaAPI, File, Form, Schema # type: ignore
from ninja.files import UploadedFile # type: ignore
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.conf import settings

from .models import Project, ProjectFile, SiteMedia
from .schema import ProjectDetailSchema, ErrorSchema, ProjectFileSchema, ProjectUpdateSchema
from django.db import transaction

from django.contrib.auth import authenticate
from ninja_jwt.tokens import RefreshToken # type: ignore
from .schema import ErrorSchema 
from ninja_jwt.authentication import JWTAuth # type: ignore # Import the authentication handler
from django.db.models import Q

logger = logging.getLogger("app")

# Global references to modules
cvc = None
dxf_c = None
Fixture = None

def initialize_modules():
    """Initialize modules"""
    global cvc, dxf_c, Fixture
    
    try:
        # Detailed logging for debugging
        print("Attempting to initialize modules...")
        
        # Now import project modules
        from . import CV_Controller as cv_module
        from . import DXF_Controller as dxf_module
        from . import Fixture as fixture_module
        
        # Store references
        cvc = cv_module
        dxf_c = dxf_module
        Fixture = fixture_module
        
        print("All modules initialized successfully")
        return True
    except ImportError as e:
        logger.error(f"Failed to import modules: {e}")
        logger.error(traceback.format_exc())
        return False
    except Exception as e:
        logger.error(f"Unexpected error during initialization: {e}")
        logger.error(traceback.format_exc())
        return False

def is_test_mode():
    """Check if Django is running in test mode"""
    import sys
    import os
    return any([
        'test' in sys.argv,
        'pytest' in sys.modules,
        os.environ.get('DB_NAME', '').startswith('test_'),
        os.environ.get('TESTING') == 'true',
    ])

if not is_test_mode():
    initialize_modules()
else:
    print("⚠️  Skipping module initialization - running in test mode")



api = NinjaAPI(version='3.0.0', urls_namespace='floorplan_api_unique')

fixtures = {
    "wall_fixtures": {
        "jj_super_hybrid_medium": 10,
        "vc_fixture_medium": 2
    },
    "floor_fixtures": {
        "Euro_centre": 3,
        "discussion_table": 6,
        "large_bench": 1
    },
    "boh_fixtures": {  # Single combined boh_fixtures entry
        "ups": 0,  
        "Dining_Table_medium": 1,
        "water_dispenser": 1,
        "storage_rack": 1,
        "staff_rack": 1
    },
    "clinic_fixtures": {
        "clinic": 1,
        "Regular_clinic": 1,
        "ROC_clinic": 0
    },
    "toilet_fixtures": {
        "toilet": 1
    },
    "screen_fixtures": {
        "screen_49": 1
    }
}

fixture_dict = {
    "jj_super_hybrid_medium": {
        "name": "jj_shelf2",  # Using actual name from file
        "path": "assets/wall_fixtures/jj_super_hybrid_medium.FCStd",
        "type": "wall"
    },
    "vc_fixture_medium": {
        "name": "shelf5",  # Using actual name from file
        "path": "assets/wall_fixtures/vc_fixture_medium.FCStd",
        "type": "wall"
    },
    "mirror": {
        "name": "mirror",
        "path": "assets/wall_fixtures/mirror.FCStd",
        "type": "wall"
    },
    # Clinic Fixtures
    "clinic": {
        "name": "Clinic_with_sink",
        "path": "assets/clinic/Clinic_with_sink.FCStd",
        "type": "clinic"
    },
        "Regular_clinic": {
        "name": "Regular_clinic",
        "path": "assets/clinic/Regular_clinic.FCStd",
        "type": "clinic"
    },
        "ROC_clinic": {
        "name": "ROC_clinic",
        "path": "assets/clinic/ROC_clinic.FCStd",
        "type": "clinic"
    },
    "Euro_centre": {
        "name": "Euro_centre",
        "path": "assets/floor/Euro_centre.FCStd",
        "type": "floor"
    },
    "ups": {
        "name": "ups_rack",
        "path": "assets/boh_furniture/ups_rack.FCStd",
        "type": "boh"
    },
    "Dining_Table_medium": {
        "name": "Dining_Table_medium",
        "path": "assets/boh_furniture/Dining_Table_medium.FCStd",
        "type": "boh"
    },
    "water_dispenser": {
        "name": "water_dispenser",
        "path": "assets/boh_furniture/water_dispenser.FCStd",
        "type": "boh"
    },
    "toilet": {
        "name": "toilet_unit",
        "path": "assets/toilet/toilet.FCStd",
        "type": "toilet"
    },
    "discussion_table": {
        "name": "Discussion_table_medium",  # Capitalize the name
        "path": "assets/floor/Discussion_table_medium.FCStd",  # Capitalize the filename
        "type": "floor"
    },
    "with_screen_medium": {
        "name": "with_screen_medium",
        "path": "assets/pos/with_screen_medium.FCStd",
        "type": "floor"
    },
    "AR": {
        "name": "AR",
        "path": "assets/floor/AR.FCStd",
        "type": "floor"
    },
    # Television Fixtures
    "TV": {
        "name": "screen_49",
        "path": "assets/screen/screen_49.FCStd",
        "type": "screen"
    }
}


class LoginSchema(Schema):
    username: str
    password: str

class TokenResponseSchema(Schema):
    refresh: str
    access: str

@api.post("/auth/login", response={200: TokenResponseSchema, 401: ErrorSchema})
def login(request, data: LoginSchema):
    user = authenticate(username=data.username, password=data.password)
    if user is not None and user.is_active:
        refresh = RefreshToken.for_user(user)
        return 200, {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    return 401, {"message": "No active account found with the given credentials"}


@api.get("/projects/", response=List[ProjectDetailSchema], auth=JWTAuth())
def list_all_project_details(request):
    projects = Project.objects.filter(status='pending').prefetch_related('files', 'site_media').all().order_by("-created_at")
    return projects


@api.get("/projects/updated-by-user/", response=List[ProjectDetailSchema], auth=JWTAuth())
def list_user_updated_projects(request):
    logged_in_user = request.auth
    projects = Project.objects.filter(updated_by=logged_in_user).prefetch_related('files', 'site_media').order_by('-updated_at')

    return projects



@api.get("/projects/{project_id}/", response=ProjectDetailSchema, auth=JWTAuth())
def get_project_details(request, project_id: uuid.UUID):
    project = get_object_or_404(Project, id=project_id)
    return project

@csrf_exempt
@api.post("/projects/{project_id}/add_data/", response={200: ProjectDetailSchema, 400: ErrorSchema, 404: ErrorSchema}, auth=JWTAuth())
def add_project_data(
    request,
    project_id: uuid.UUID,
    project_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    locationReference: Optional[str] = Form(None),
    carpetArea: Optional[float] = Form(None),
    floorLevel: Optional[str] = Form(None),
    electricityLoad: Optional[float] = Form(None),
    electricityMeterLocation: Optional[str] = Form(None),
    hvacType: Optional[str] = Form(None),
    acOutdoorLocation: Optional[str] = Form(None),
    hasDrainage: Optional[bool] = Form(None),
    hasWaterConnection: Optional[bool] = Form(None),
    entranceDirection: Optional[str] = Form(None),
    nearestAirport: Optional[str] = Form(None),
    airportDistance: Optional[float] = Form(None),
    nearestStation: Optional[str] = Form(None),
    stationDistance: Optional[float] = Form(None),
    washroom: Optional[str] = Form(None),
    remarks: Optional[str] = Form(None),
    roomMeasurements: Optional[str] = Form(None),
    # And the original file keywords
    files: List[UploadedFile] = File([]),
    siteImages: List[UploadedFile] = File([])
):
    """
    Adds or updates data for an existing project.
    This endpoint is for the mobile app to fill in missing details and add files.
    It only updates fields that are provided in the request (it's additive).
    """
    project = get_object_or_404(Project, id=project_id)

    # --- Update Text Fields ---
    # Create a dictionary of all possible text fields from the request
    update_data_map = {
        'name': project_name, 'description': description, 'address': address, 
        'location_reference': locationReference, 'total_carpet_area': carpetArea, 
        'floor_level': floorLevel, 'electricity_load': electricityLoad, 
        'electricity_meter_location': electricityMeterLocation, 'hvac_system_type': hvacType,
        'ac_outdoor_units_location': acOutdoorLocation, 'drainage_facility': hasDrainage, 
        'water_connection': hasWaterConnection, 'main_entrance_direction': entranceDirection,
        'nearest_airport': nearestAirport, 'airport_distance': airportDistance, 
        'nearest_railway_station': nearestStation, 'railway_station_distance': stationDistance,
        'washroom': washroom, 'remarks': remarks
    }

    # Loop through the map and update the project object ONLY if a value was sent
    for field_name, value in update_data_map.items():
        if value is not None:
            setattr(project, field_name, value)
    
    # Record the user who made the update
    project.updated_by = request.auth

    # --- Handle roomMeasurements separately as it needs JSON parsing ---
    if roomMeasurements:
        try:
            parsed_measurements = json.loads(roomMeasurements)
            project.room_measurements = parsed_measurements
            
            # Also regenerate the standalone JSON file
            room_measurements_dir = os.path.join(settings.MEDIA_ROOT, 'room_measurements')
            os.makedirs(room_measurements_dir, exist_ok=True)
            safe_project_name = "".join(c for c in project.name if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
            filename = f"{safe_project_name}_{project.id}_room_measurements.json"
            file_path = os.path.join(room_measurements_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump({
                    'project_id': str(project.id), 'project_name': project.name,
                    'created_at': project.created_at.isoformat(),
                    'room_measurements': parsed_measurements
                }, json_file, indent=2, ensure_ascii=False)
            logger.info(f"Room measurements JSON file updated for project {project.id}")

        except json.JSONDecodeError:
            return 400, {"message": "Invalid JSON format for roomMeasurements"}
        except Exception as e:
            logger.error(f"Error saving room measurements file for project {project.id}: {str(e)}")

    # --- Add New Files (Additive Only) using the original, working logic ---
    # 1. Process files from the 'files' field
    for file in files:
        _, ext = os.path.splitext(file.name)
        ext = ext.lower().lstrip('.')
        # Your original logic: videos go to SiteMedia, others to ProjectFile
        if ext == 'mp4':
            SiteMedia.objects.create(project=project, file=file)
        else:
            ProjectFile.objects.create(project=project, file=file)

    # 2. Process files from the 'siteImages' field
    for media_file in siteImages:
        SiteMedia.objects.create(project=project, file=media_file)

    # Save all the changes to the database
    project.save()

    # Return the full, updated project object
    return 200, project




@csrf_exempt
@api.post("/upload/", response={201: ProjectDetailSchema, 400: ErrorSchema, 404: ErrorSchema})
def upload_project_with_files(
    request,
    # --- THIS IS THE KEY CHANGE ---
    # We define both file lists here. Ninja will correctly populate them.
    files: List[UploadedFile] = File([]),
    siteImages: List[UploadedFile] = File([]),
    project_id: Optional[uuid.UUID] = Form(None)
):
    try:
        project = None
        
        # --- Logic to handle existing vs. new project ---
        if project_id:
            project = get_object_or_404(Project, id=project_id)
            # (Logic to update room measurements on an existing project)
            room_measurements_raw = request.POST.get('roomMeasurements')
            if room_measurements_raw:
                try:
                    project.room_measurements = json.loads(room_measurements_raw)
                    project.save()
                except json.JSONDecodeError:
                    return 400, {"message": "Invalid JSON format for roomMeasurements"}
        else:
            # This is your original, working code for CREATING a NEW project.
            project_name = request.POST.get('project_name')
            if not project_name:
                return 400, {"message": "Project name is required for new projects"}

            # (Full logic for getting all form data for a new project)
            description = request.POST.get('description')
            address = request.POST.get('address')
            location_reference = request.POST.get('locationReference')
            total_carpet_area = request.POST.get('carpetArea')
            floor_level = request.POST.get('floorLevel')
            electricity_load = request.POST.get('electricityLoad')
            electricity_meter_location = request.POST.get('electricityMeterLocation')
            hvac_system_type = request.POST.get('hvacType')
            ac_outdoor_units_location = request.POST.get('acOutdoorLocation')
            drainage_facility = request.POST.get('hasDrainage') == 'true'
            water_connection = request.POST.get('hasWaterConnection') == 'true'
            main_entrance_direction = request.POST.get('entranceDirection')
            nearest_airport = request.POST.get('nearestAirport')
            airport_distance = request.POST.get('airportDistance')
            nearest_railway_station = request.POST.get('nearestStation')
            railway_station_distance = request.POST.get('stationDistance')
            washroom = request.POST.get('washroom')
            remarks = request.POST.get('remarks')
            room_measurements_raw = request.POST.get('roomMeasurements')
            room_measurements = json.loads(room_measurements_raw) if room_measurements_raw else {}

            project = Project.objects.create(
                name=project_name, description=description, address=address,
                location_reference=location_reference,
                total_carpet_area=total_carpet_area if total_carpet_area else None,
                floor_level=floor_level,
                electricity_load=electricity_load if electricity_load else None,
                electricity_meter_location=electricity_meter_location,
                hvac_system_type=hvac_system_type,
                ac_outdoor_units_location=ac_outdoor_units_location,
                drainage_facility=drainage_facility, water_connection=water_connection,
                main_entrance_direction=main_entrance_direction,
                nearest_airport=nearest_airport,
                airport_distance=airport_distance if airport_distance else None,
                nearest_railway_station=nearest_railway_station,
                railway_station_distance=railway_station_distance if railway_station_distance else None,
                washroom=washroom, remarks=remarks, room_measurements=room_measurements
            )

        # --- Logic to create/update the standalone JSON file ---
        if request.POST.get('roomMeasurements'):
            # ... (This logic from your code is correct and preserved) ...
            try:
                room_measurements_dir = os.path.join(settings.MEDIA_ROOT, 'room_measurements')
                os.makedirs(room_measurements_dir, exist_ok=True)
                safe_project_name = "".join(c for c in project.name if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
                filename = f"{safe_project_name}_{project.id}_room_measurements.json"
                file_path = os.path.join(room_measurements_dir, filename)
                with open(file_path, 'w', encoding='utf-8') as json_file:
                    json.dump({
                        'project_id': str(project.id), 'project_name': project.name,
                        'created_at': project.created_at.isoformat(),
                        'room_measurements': project.room_measurements
                    }, json_file, indent=2, ensure_ascii=False)
                logger.info(f"Room measurements JSON file saved/updated: {filename}")
            except Exception as e:
                logger.error(f"Error saving room measurements JSON file for project {project.name}: {str(e)}")


        # --- THE SIMPLE, CORRECTED FILE PROCESSING LOGIC ---
        
        # 1. Process the main `files` list as ProjectFile objects.
        # This keeps your original, working logic.
        for file in files:
            ProjectFile.objects.create(project=project, file=file)

        # 2. Process the `siteImages` list as SiteMedia objects.
        # Ninja provides the full list in the `siteImages` variable.
        for media_file in siteImages:
            SiteMedia.objects.create(project=project, file=media_file)
            
        return 201, project

    except Project.DoesNotExist:
        return 404, {"message": "Project with the given ID not found"}
    except Exception as e:
        logger.exception(f"Error occurred during upload: {str(e)}")
        return 400, {"message": str(e)}


# --- ALSO REPLACE your old /merchmix/ function with this new one ---
@csrf_exempt
@api.post("/merchmix/", response={201: ProjectDetailSchema, 400: ErrorSchema, 404: ErrorSchema})
def upload_project_with_merchmix(
    request, 
    files: List[UploadedFile] = File(default=None),
    project_id: Optional[uuid.UUID] = Form(None)
):
    try:
        project = None

        if project_id:
            # Add files to an existing project
            project = get_object_or_404(Project, id=project_id)
        else:
            # Create a new project
            project_name = request.POST.get('project_name')
            if not project_name:
                return 400, {"message": "Project name is required for new projects"}

            # --- All your original logic for getting merchmix form data is here ---
            description = request.POST.get('description')
            address = request.POST.get('address')
            location_reference = request.POST.get('locationReference')
            total_carpet_area = request.POST.get('carpetArea')
            floor_level = request.POST.get('floorLevel')
            electricity_load = request.POST.get('electricityLoad')
            electricity_meter_location = request.POST.get('electricityMeterLocation')
            hvac_system_type = request.POST.get('hvacType')
            ac_outdoor_units_location = request.POST.get('acOutdoorLocation')
            drainage_facility = request.POST.get('hasDrainage') == 'true'
            water_connection = request.POST.get('hasWaterConnection') == 'true'
            main_entrance_direction = request.POST.get('entranceDirection')
            nearest_airport = request.POST.get('nearestAirport')
            airport_distance = request.POST.get('airportDistance')
            nearest_railway_station = request.POST.get('nearestStation')
            railway_station_distance = request.POST.get('stationDistance')
            washroom = request.POST.get('washroom')
            remarks = request.POST.get('remarks')
            merch_mix_min_str = request.POST.get('merch_mix_min', '{}')
            merch_mix_max_str = request.POST.get('merch_mix_max', '{}')
            merch_mix_min = json.loads(merch_mix_min_str)
            merch_mix_max = json.loads(merch_mix_max_str)
            
            project = Project.objects.create(
                name=project_name, description=description, address=address,
                location_reference=location_reference,
                total_carpet_area=total_carpet_area if total_carpet_area else None,
                floor_level=floor_level,
                electricity_load=electricity_load if electricity_load else None,
                electricity_meter_location=electricity_meter_location,
                hvac_system_type=hvac_system_type,
                ac_outdoor_units_location=ac_outdoor_units_location,
                drainage_facility=drainage_facility, water_connection=water_connection,
                main_entrance_direction=main_entrance_direction,
                nearest_airport=nearest_airport,
                airport_distance=airport_distance if airport_distance else None,
                nearest_railway_station=nearest_railway_station,
                railway_station_distance=railway_station_distance if railway_station_distance else None,
                washroom=washroom, remarks=remarks,
                merch_mix_min=merch_mix_min,
                merch_mix_max=merch_mix_max
            )

        # --- This part of the code now runs for BOTH new and existing projects ---
        if files:
            for file in files:
                _, ext = os.path.splitext(file.name)
                ext = ext.lower().lstrip('.')
                if ext == 'mp4':
                    SiteMedia.objects.create(project=project, file=file)
                    continue
                allowed_extensions = ['png', 'jpg', 'jpeg', 'usdz']
                if ext not in allowed_extensions:
                    if not project_id: project.delete()
                    return 400, {"message": f"File type {ext} not allowed"}
                ProjectFile.objects.create(project=project, file=file)

        site_media_files = request.FILES.getlist('siteImages')
        for media_file in site_media_files:
            _, ext = os.path.splitext(media_file.name)
            ext = ext.lower().lstrip('.')
            allowed_site_media_extensions = ['png', 'jpg', 'jpeg', 'mp4']
            if ext not in allowed_site_media_extensions:
                if not project_id: project.delete()
                return 400, {"message": f"Site media file type {ext} not allowed"}
            SiteMedia.objects.create(project=project, file=media_file)
            
        return 201, project
        
    except Project.DoesNotExist:
        return 404, {"message": "Project with the given ID not found"}
    except Exception as e:
        logger.exception(f"Error occurred during merchmix upload: {str(e)}")
        return 400, {"message": str(e)}
    
    

class ProcessedFloorplanResponse(Schema):
    message: str
    processed_file_id: uuid.UUID


@api.post("/process-floorplan/{file_id}/", response={200: ProcessedFloorplanResponse, 400: ErrorSchema, 404: ErrorSchema})
def process_floorplan(request, file_id: uuid.UUID):
    """Process an image into a DXF floorplan"""
    
    # Use consistent project naming that matches the export method
    consistent_project_name = f"{file_id}_floorplan"
    try:
        # Get the project file
        project_file = get_object_or_404(ProjectFile, id=file_id)
        
        # Check if the file is an image
        if project_file.file_type not in ['png', 'jpg', 'jpeg']:
            logger.error(f"Invalid file type for processing: {project_file.file_type}")
            return 400, {"message": "Only image files (PNG, JPG, JPEG) can be processed"}
        
        # Get the project and its fixtures configuration
        merch_mix_file = "app/merch_mix.json"
        project = project_file.project
        project_id = project.id
        project_name = project.name
        room_measurements_dir = os.path.join(settings.MEDIA_ROOT, 'room_measurements')

        safe_project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_project_name = safe_project_name.replace(' ', '_')
        filename = f"{safe_project_name}_{project.id}_room_measurements.json"
        measurment_file_path = os.path.join(room_measurements_dir, filename)
        
        # Check if project has fixtures configuration
        if not project.fixtures:
            logger.error(f"No fixtures configuration found for project: {project.name}")
            return 400, {"message": "No fixtures configuration found for this project. Please configure fixtures first."}
        
        # Get fixtures data from project - assume it's stored with range keys like "0-5", "5-7"
        project_fixtures = project.fixtures
        
        # Use the first available fixtures configuration (assumes it's stored with range keys like "0-5", "5-7"
        fixtures_config = None
        selected_range = None
        for range_key, config in project_fixtures.items():
            fixtures_config = config
            selected_range = range_key
            break  # Use the first configuration found
        
        if not fixtures_config:
            logger.error(f"No valid fixtures configuration found in project: {project.name}")
            return 400, {"message": "No valid fixtures configuration found for this project."}
        
        print(f"Using fixtures configuration for range: {selected_range}")
        
        # Get the file path
        input_path = project_file.file.path
        print(f"Processing image: {input_path}")

        # Use consistent project naming that matches the export method
        
        print(f"Consistent project name for output: {consistent_project_name}")

    
        output_dir = os.path.join(settings.BASE_DIR, f"{consistent_project_name}_output")
        os.makedirs(output_dir, exist_ok=True)  # Ensure directory exists

        final_export_dxf_path = os.path.join(output_dir, "output.dxf")

        try:
            # Setup processing parameters
            overlay_output = os.path.join(settings.MEDIA_ROOT, "overlay_output.png")
            
            try:
                # 1. Find the project by its exact name.
                # Use .first() in case there are multiple projects with the same name.
                # This will get the first one it finds.
                project = Project.objects.filter(name=project_name).first()
                
                if project:
                    merch_mix_data = project.__dict__['merch_mix_max']
                    
                    if merch_mix_data is None:
                        logger.info(f"Project '{project.name}' found, but 'merch_mix_max' is not set.")
                        # return {}
                    
                    logger.info(f"Successfully retrieved merch_mix_max for project: {project.name}")
                    logger.info(f"Data: {merch_mix_data}")
                else:
                    logger.error(f"Error: No project found with the name '{project_name}'.")
                    return {}
                
            except Exception as e:
                logger.error(f"An unexpected error occurred retrieving the merch mix: {e}")

                try:
                    with open(merch_mix_file, 'r') as f:
                        merch_json_data = json.load(f)
                    # Extract the 'merch_mix_max' object, which contains the final counts
                    merch_mix_data = merch_json_data['merch_mix_max']
                    if merch_mix_data is None:
                        logger.info(f"File found, but 'merch_mix_max' is not set.")
                        return 400, {"message": f"Could not load merch mix from DB or file {merch_mix_file}"}

                    logger.info("--- ✅ Successfully loaded backup merch mix data. ---")
                except (FileNotFoundError, KeyError) as e:
                    logger.error(f"--- 🚨 ERROR: Could not load or parse {merch_mix_file}. Error: {e} ---")
                    return 400, {"message": f"Could not load merch mix from DB or file {merch_mix_file}"}
                
            # rotation = 42  # REPLACE WITH VALUE FROM DB
            # json_path = f"/home/ubuntu/lenskart-backend/media/room_measurements/{project.name}_{project.id}_room_measurements.json"
            #json_path = f"/home/ubuntu/lenskart_backend/app/test.json"

            static_fixtures = {
                "mirror_selection": { "mirror_different" : 1, "mirror": 0 },
            
                "Bench_fixtures":{ "large_bench" : 0, "AR": 1 ,"medium_bench" : 1 },
                
                "lensometer_fixtures":{ "Lensometer_medium": 0, "Lensometer_small": 0, "Lensometer_large": 0 },
                
                "boh_fixtures": {
                    "water_dispenser": 1, "ups_rack": 1, "staff_rack": 1, "pickup_storage_900": 0,
                    "storage_rack": 1, "pickup_storage_1200": 0, "Dining_Table_large": 0,
                    "QC_table_large": 0, "Dining_Table_medium": 1, "QC_table_medium": 0,
                    "Repair_Table_large": 0, "Repair_Table_medium": 0, 
                    "drop_box": 0, "pick_up_counter": 0
                },

                # "clinic_fixtures": { "ROC_clinic": 3,"Clinic_regular": 1, "Clinic_with_sink": 1,  "Eye_massage_area": 0 },

                "boh_presets": { "medium_basic_boh": 1, "basic_boh_preset_1": 0 ,"small_basic_boh": 0,"boh_vertical_horizontal_preset_basic": 0 },

                "pickup_window": { "Pick_up_window": 1 , "pickup_table": 1},

                "Eye_massage_area": { "Eye_massage_area": 0 },
                
                "Corian_table_set":{ "Corian_table" : 0, "Lounge_seat" : 0 },
                
                "loose_furniture": { "sofa": 0, "Sofa_large": 0, "Sofa_medium": 0 },
                
                "toilet_fixtures": { "toilet": 0 },
                
                "screen_fixtures": { "screen_43": 0, "screen_49": 0, "screen_55": 0, "screen_65": 0 },
                
                "POS": { "pos_with_screen_large": 0, "pos_with_screen_medium": 0, "pos_with_screen_small": 0, "pos_without_screen": 0 },
                
                "discussion_table_attached":{ "Blue_zero" : 1 },
                
                "table_fixtures": { "QMS_desk" : 1, 
                                #    "Standing_table" : 3
                                    },
                
                "lensbar_and_dropbox": { "Lensbar": 0 },
                
                "floor_fixtures_table": { "Discussion_table_small": 0, "Discussion_table_medium": 0, "Discussion_table_large": 0 }
            }
            
            dxfc = dxf_c.DXF_Controller(input_path, final_export_dxf_path, overlay_output, measurment_file_path, {})
            dxfc.create_floorplan()
            dxfc.cvc.get_metadata()
            dxfc.cvc.reorder_bot_left()
            DRAW_SEPARATOR_LINE = True 

            dxfc.close_plan()
            
            
            # ==================== DXF PROCESSING STARTS HERE ============================


            # ==================== DXF PROCESSING ENDS HERE ============================

            # Create a new ProjectFile for the processed DXF file
            processed_filename = f"{os.path.splitext(project_file.filename)[0]}_processed.dxf"
            # final_export_dxf_path = os.path.join(output_dir, "output.dxf") # Path to save the final DXF with assigned layers
            # Use Django's File class instead of direct open()
            try:
                with open(final_export_dxf_path, 'rb') as f:  # Use the final DXF here
                    django_file = DjangoFile(f, name=processed_filename)
                    processed_file = ProjectFile.objects.create(
                        project=project_file.project,
                        file=django_file
                    )
                print(f"Created processed file: {processed_file.id}")
            except FileNotFoundError:
                logger.error(f"Final DXF file not found: {final_export_dxf_path}")
                return 400, {"message": f"Final DXF file not found: {final_export_dxf_path}"}

            # Return success response
            return 200, {
                "message": "Floorplan processed successfully",
                "processed_file_id": processed_file.id,
                "project_name": consistent_project_name
            }

        except Exception as e:
            logger.exception(f"Error during floorplan processing: {str(e)}")
            return 400, {"message": f"Error processing floorplan: {str(e)}"}
        finally:
            # Clean up the temporary output file if it exists
            # if os.path.exists(output_path):
            #     os.unlink(output_path)
            pass
    
    except ProjectFile.DoesNotExist:
        logger.warning(f"Project file with ID {file_id} not found")
        return 404, {"message": "Project file not found"}
    except Exception as e:
        logger.exception(f"Error occurred while processing floorplan: {str(e)}")
        return 400, {"message": str(e)}
    

    
@api.get("/download/{file_id}/", url_name="download_file")
def download_file(request, file_id: uuid.UUID):
    """Download a processed file"""
    try:
        project_file = get_object_or_404(ProjectFile, id=file_id)
        
        # Open the file and return it as a download
        return FileResponse(
            project_file.file.open(),
            as_attachment=True,
            filename=project_file.filename
        )
    except ProjectFile.DoesNotExist:
        logger.warning(f"Project file with ID {file_id} not found")
        return 404, {"message": "Project file not found"}
    except Exception as e:
        logger.exception(f"Error downloading file: {str(e)}")
        return 400, {"message": str(e)}