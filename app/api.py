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
from ninja_jwt.tokens import RefreshToken
from .schema import ErrorSchema # Make sure you have this ErrorSchema defined
from ninja_jwt.authentication import JWTAuth # Import the authentication handler
from django.db.models import Q


# Import the new FreeCAD path setup module
from . import freecad_paths

logger = logging.getLogger("app")

# Setup FreeCAD environment first before any imports
freecad_paths.setup_freecad_environment()

# Global references to modules
FREECAD_INITIALIZED = False
fcc = None
cvc = None
Fixture = None
FreeCAD = None
Vector = None
Rotation = None

def initialize_freecad():
    """Initialize FreeCAD and related modules"""
    global FREECAD_INITIALIZED, fcc, cvc, Fixture, FreeCAD, Vector, Rotation
    
    try:
        # Detailed logging for debugging
        print("Attempting to initialize FreeCAD modules...")
        
        # Import FreeCAD modules first
        import FreeCAD as FC # type: ignore
        import Part # type: ignore
        from FreeCAD import Vector as Vec, Rotation as Rot # type: ignore
        
        # Store references
        FreeCAD = FC
        Vector = Vec
        Rotation = Rot
        
        print("FreeCAD core modules imported successfully")
        
        # Now import project modules
        from . import FC_Controller as fc_module
        from . import CV_Controller as cv_module
        from . import Fixture as fixture_module
        
        # Initialize FC_Controller's FreeCAD references
        if hasattr(fc_module, 'initialize_freecad'):
            print("Initializing FreeCAD in FC_Controller")
            fc_module.initialize_freecad()
        
        # Store references
        fcc = fc_module
        cvc = cv_module
        Fixture = fixture_module
        
        print("All modules initialized successfully")
        FREECAD_INITIALIZED = True
        return True
    except ImportError as e:
        logger.error(f"Failed to import FreeCAD modules: {e}")
        logger.error(traceback.format_exc())
        return False
    except Exception as e:
        logger.error(f"Unexpected error during FreeCAD initialization: {e}")
        logger.error(traceback.format_exc())
        return False

# Try to initialize FreeCAD at module load time
initialize_freecad()


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


@api.get("/projects/{project_id}/", response=ProjectDetailSchema, auth=JWTAuth())
def get_project_details(request, project_id: uuid.UUID):
    project = get_object_or_404(Project, id=project_id)
    return project

@csrf_exempt
@api.post("/projects/{project_id}/add_data/", response={200: ProjectDetailSchema, 400: ErrorSchema, 404: ErrorSchema}, auth=JWTAuth())
def add_project_data(
    request,
    project_id: uuid.UUID,
    # We accept all possible fields as optional Form fields using the exact
    # keywords from the original /upload/ endpoint.
    name: Optional[str] = Form(None),
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
        'name': name, 'description': description, 'address': address, 
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
    """Process an image into a FreeCAD floorplan"""
    
    # Use consistent project naming that matches the export method
    consistent_project_name = f"{file_id}_floorplan"
    try:
        # Check if FreeCAD modules are properly initialized
        global FREECAD_INITIALIZED
        if not FREECAD_INITIALIZED:
            # Try to initialize FreeCAD modules again
            success = initialize_freecad()
            if not success:
                return 400, {"message": "FreeCAD modules could not be initialized. Please check server logs for details."}
        
        # Get the project file
        project_file = get_object_or_404(ProjectFile, id=file_id)
        
        # Check if the file is an image
        if project_file.file_type not in ['png', 'jpg', 'jpeg']:
            logger.error(f"Invalid file type for processing: {project_file.file_type}")
            return 400, {"message": "Only image files (PNG, JPG, JPEG) can be processed"}
        
        # Get the project and its fixtures configuration
        project = project_file.project
        project_id = project.id
        room_measurements_dir = os.path.join(settings.MEDIA_ROOT, 'room_measurements')
        
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

        master_dxf_path = os.path.join(output_dir, "master.dxf")
        final_export_dxf_path = os.path.join(output_dir, "output.dxf")
        image_metadata_path = os.path.join(output_dir, "image_metadata.json")
        lisp_path = os.path.join(output_dir, "attach_and_group.lsp")
        zip_file_path = os.path.join(output_dir, "package.zip")
        output_fcstd_path = os.path.join(output_dir, f"{consistent_project_name}.FCStd")

        try:
            # Setup processing parameters
            overlay_output = os.path.join(settings.MEDIA_ROOT, "overlay_output.png")
            scale = 30  # mm per pixel
            
            # ===================== FCSTD Creation (replace with your controller logic) ============================
            # # Process the floorplan using FreeCAD with dynamic fixtures
            print(f"Creating FC_Controller with input: {input_path}, output: {output_fcstd_path}")
            fc_cont = fcc.FC_Controller(input_path, output_fcstd_path, overlay_output, scale, fixtures_config)
            print("FC_Controller created successfully")
            
            fc_cont.create_floorplan()
            print("Floorplan created successfully")
            
            fc_cont.cvc.get_metadata()
            fc_cont.cvc.reorder_bot_left()
            
            # # Place all the  fixtures
            fc_cont.place_toilet()
            fc_cont.place_boh_after_toilet()
            fc_cont.place_clinic()
            fc_cont.center_floor_fixtures("Euro_centre", fixtures_config["floor_fixtures"]["Euro_centre"])
            fc_cont.place_screens_and_ar()
            fc_cont.place_wall_fixtures_auto_split()
            fc_cont.place_right_wall_sofa()
            fc_cont.place_screen()
            fc_cont.close_plan()

            print("All fixtures placed successfully")

            if os.path.exists('/Applications/FreeCAD.app'):
                # MacOS path - use the correct executable (NOT the Resources/bin path)
                FREECAD_INSTALLATION_PATH = "/Applications/FreeCAD.app/Contents/MacOS/FreeCAD"
                logger.info(f"[DEBUG] Using macOS FreeCAD path: {FREECAD_INSTALLATION_PATH}")
            else:
                # Linux path - check common locations
                linux_freecad_paths = [
                    "/usr/bin/freecad",
                    "/usr/local/bin/freecad",
                    "/opt/freecad/bin/freecad"
                ]
                FREECAD_INSTALLATION_PATH = None
                for path in linux_freecad_paths:
                    if os.path.exists(path):
                        FREECAD_INSTALLATION_PATH = path
                        break
                if not FREECAD_INSTALLATION_PATH:
                    logger.error("FreeCAD executable not found in common locations")
                    return False
                
            script_parent_dir = os.path.dirname(os.path.abspath(__file__))
            fcstd_to_dxf_script_path = os.path.join(script_parent_dir, "fcstd_to_dxf.py")
            print(f"[OK] Using DXF export script: {fcstd_to_dxf_script_path}")


            # Construct FreeCAD command
            freecad_command = [
                FREECAD_INSTALLATION_PATH, # or FreeCADCmd if available
                '-c',
                fcstd_to_dxf_script_path,
                output_fcstd_path,
                consistent_project_name
            ]



            print(f"Running FreeCAD with command: {' '.join(freecad_command)}")



            # Execute FreeCAD process
            process = subprocess.Popen(
                freecad_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            stdout, _ = process.communicate()
            print(f"FreeCAD output:\n{stdout}")

            if process.returncode != 0:
                logger.error(f"FreeCAD failed with code {process.returncode}")
                raise Exception("FreeCAD DXF export failed")



            # Verify DXF file was created
            master_dxf_path = os.path.join(output_dir, "master.dxf")
            if not os.path.exists(master_dxf_path):
                raise Exception(f"Expected DXF file was not created: {master_dxf_path}")
                
            print(f"DXF file successfully created: {master_dxf_path}")

            # ==================== DXF Export ENDS HERE ============================

            # ==================== RUN DXF PROCESSING SCRIPTS ============================
            python_executable_path = sys.executable # Ensure you're using the correct venv python

            # # Run add_blocks.py
            add_blocks_script_path = os.path.join(settings.BASE_DIR, 'app', 'add_blocks.py')
            add_blocks_input_dxf = os.path.join(output_dir, "master.dxf")  # Input for add_blocks.py
            add_blocks_output_dxf = os.path.join(output_dir, "output_with_blocks_aligned.dxf")

            print(f"Running add_blocks.py: {add_blocks_script_path} {add_blocks_input_dxf} {add_blocks_output_dxf}")
            add_blocks_process = subprocess.Popen([python_executable_path, add_blocks_script_path, add_blocks_input_dxf, add_blocks_output_dxf],
                                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            add_blocks_stdout, add_blocks_stderr = add_blocks_process.communicate()
            print(f"add_blocks.py stdout:\n{add_blocks_stdout.decode()}")
            if add_blocks_stderr:
                logger.error(f"add_blocks.py stderr:\n{add_blocks_stderr.decode()}")
            if add_blocks_process.returncode != 0:
                 raise Exception(f"add_blocks.py failed with code {add_blocks_process.returncode}: {add_blocks_stderr.decode()}")

            # Run blocks_dxf.py
            blocks_dxf_script_path = os.path.join(settings.BASE_DIR, 'app', 'blocks_dxf.py')
            blocks_dxf_input_dxf = os.path.join(output_dir, "output_with_blocks_aligned.dxf") # Input for blocks_dxf.py
            blocks_dxf_output_dxf = os.path.join(output_dir, "output.dxf")

            print(f"Running blocks_dxf.py: {blocks_dxf_script_path} {consistent_project_name}")
            blocks_dxf_process = subprocess.Popen([python_executable_path, blocks_dxf_script_path, blocks_dxf_input_dxf, blocks_dxf_output_dxf],
                                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=output_dir)
            blocks_dxf_stdout, blocks_dxf_stderr = blocks_dxf_process.communicate()
            print(f"blocks_dxf.py stdout:\n{blocks_dxf_stdout.decode()}")
            if blocks_dxf_stderr:
                logger.error(f"blocks_dxf.py stderr:\n{blocks_dxf_stderr.decode()}")

            if blocks_dxf_process.returncode != 0:
                 raise Exception(f"blocks_dxf.py failed with code {blocks_dxf_process.returncode}: {blocks_dxf_stderr.decode()}")
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
