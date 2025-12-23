import uuid
import os
import json
import requests
from ninja import NinjaAPI, Schema, File
from ninja.files import UploadedFile
from django.http import FileResponse, JsonResponse
from django.conf import settings
from . import utils
from .ai_fixture_mover import AIFixtureMover
from app.models import Project, ProjectFile


dashboard_api = NinjaAPI(urls_namespace="dashboard")


# --- SCHEMAS ---
class UrlUploadSchema(Schema):
    url: str

class MoveFixtureSchema(Schema):
    session_id: str
    fixture_name: str
    start_position: list[float]
    end_position: list[float]
    delta: list[float]

class RotateFixtureSchema(Schema):
    session_id: str
    fixture_name: str
    rotation: float

class AiGenerateSchema(Schema):
    session_id: str
    prompt: str


class ProcessSchema(Schema):
    file_id: str
    mode: str = 'math'
    prompt: str = None


# --- ENDPOINTS ---

@dashboard_api.post("/upload")
def upload_dxf(request, dxf_file: UploadedFile = File(...)):
    session_id = str(uuid.uuid4())
    filename = dxf_file.name
    upload_path = os.path.join(utils.UPLOAD_FOLDER, f"{session_id}_{filename}")
    
    with open(upload_path, 'wb+') as destination:
        for chunk in dxf_file.chunks():
            destination.write(chunk)
            
    json_data = utils.dxf_to_json(upload_path)
    session_data = {
        'original_dxf': upload_path,
        'filename': filename,
        'json_data': json_data,
        'modifications': []
    }
    utils.save_session(session_id, session_data)
    canvas_data = utils.extract_canvas_data(json_data, upload_path)
    
    return {
        'success': True,
        'session_id': session_id,
        'filename': filename,
        'canvas_data': canvas_data
    }

@dashboard_api.post("/move_fixture")
def move_fixture(request, data: MoveFixtureSchema):
    session_data = utils.load_session(data.session_id)
    if not session_data:
        return {"error": "Invalid session"}, 404

    # Gemini AI Logic
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    ai_mover = AIFixtureMover(GEMINI_API_KEY)
    
    prompt = f"""Generate a fixture modification in JSON format.
    Fixture to move: {data.fixture_name}
    Original position: {data.start_position}
    New position: {data.end_position}
    Output ONLY valid JSON."""
    
    try:
        response = ai_mover.model.generate_content(prompt)
        response_text = response.text.strip().replace('```json', '').replace('```', '')
        modification = json.loads(response_text)
    except:
        # Fallback to manual modification if AI fails
        modification = {
            "fixtures": [{
                "block_name": data.fixture_name,
                "original_position": data.start_position,
                "new_position": data.end_position
            }]
        }
    
    # Update local session data
    session_data['modifications'].append(modification)
    utils.save_session(data.session_id, session_data)
    
    # Update JSON data logic (Helper needed in utils)
    utils.update_json_with_modification(data.session_id, modification)
    
    return {'success': True, 'modification': modification}

@dashboard_api.post("/rotate_fixture")
def rotate_fixture(request, data: RotateFixtureSchema):
    # This calls the rotation logic we migrated to utils
    success = utils.rotate_fixture_logic(data.session_id, data.fixture_name, data.rotation)
    return {"success": success}

@dashboard_api.post("/generate_with_ai")
def generate_with_ai(request, data: AiGenerateSchema):
    result = utils.generate_with_ai_logic(data.session_id, data.prompt)
    
    if not result.get('success'):
        return JsonResponse(result, status=400)
        
    return result

@dashboard_api.get("/download/{session_id}")
def download_dxf(request, session_id: str):
    session_data = utils.load_session(session_id)
    if not session_data:
        return JsonResponse({'error': 'Invalid session'}, status=404)
        
    output_path = session_data.get('ai_output_path') or session_data.get('original_dxf')
    
    if not os.path.exists(output_path):
        return JsonResponse({'error': 'File not found'}, status=404)

    return FileResponse(
        open(output_path, 'rb'), 
        as_attachment=True, 
        filename=f"modified_{session_data['filename']}"
    )



@dashboard_api.get("/projects")
def list_projects(request, q: str = None):
    """Migrated from demo_projects_api"""
    projects = Project.objects.all().order_by('name')
    if q:
        projects = projects.filter(name__icontains=q)
    
    projects = projects.prefetch_related('files')[:200]
    
    results = []
    for project in projects:
        files_data = []
        dxf_files = []
        for file in project.files.all().order_by('-created_at'):
            file_url = file.file.url if file.file else None
            file_info = {
                'id': str(file.id),
                'filename': file.filename,
                'file_type': file.file_type,
                'created_at': file.created_at.isoformat(),
                'file_url': file_url
            }
            files_data.append(file_info)
            if file.file_type == 'dxf':
                dxf_files.append({
                    'id': str(file.id),
                    'filename': file.filename,
                    'dxf_url': file_url,
                    'created_at': file.created_at.isoformat()
                })
        
        results.append({
            'id': str(project.id),
            'name': project.name,
            'files': files_data,
            'existing_dxf_files': dxf_files
        })
    return {'projects': results}

@dashboard_api.post("/process")
def process_floorplan(request, data: ProcessSchema):
    """Migrated from demo_process_api"""
    try:
        # Update project mode if AI
        if data.mode == 'ai':
            project_file = ProjectFile.objects.get(id=data.file_id)
            project = project_file.project
            project.processing_mode = 'ai'
            if data.prompt:
                project.ai_prompt_text = data.prompt
            project.save()

       
        django_url = os.getenv('DJANGO_SERVER_URL', 'http://127.0.0.1:8000').rstrip('/')
        process_url = f"{django_url}/api/app1/process-floorplan/{data.file_id}/"
        
        response = requests.post(process_url)
        
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'message': result.get('message'),
                'multiple_files': len(result.get('processed_files', [])) > 0,
                'processed_files': result.get('processed_files', []),
                'download_url': result.get('dxf_url') or f"/api/app1/download/{result.get('processed_file_id')}/",
                'processing_mode': data.mode
            }
        else:
            return JsonResponse({'success': False, 'error': response.text}, status=response.status_code)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@dashboard_api.post("/save-dxf/{project_id}")
def save_dxf(request, project_id: str, dxf_file: UploadedFile = File(...)):
    """Migrated from save_dxf_to_project"""
    from datetime import datetime
    try:
        project = Project.objects.get(id=project_id)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'layout_modified_{timestamp}.dxf'
        
        project_file = ProjectFile(project=project)
        project_file.file.save(filename, dxf_file, save=True)
        
        return {
            'success': True,
            'file_id': str(project_file.id),
            'filename': filename,
            'file_url': project_file.file.url
        }
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    




@dashboard_api.post("/upload-from-url")
def upload_from_url(request, data: UrlUploadSchema):
    import requests
    session_id = str(uuid.uuid4())
    
    try:
        # 1. Fetch file from internal media URL
        response = requests.get(data.url, timeout=10)
        filename = data.url.split('/')[-1]
        upload_path = os.path.join(utils.UPLOAD_FOLDER, f"{session_id}_{filename}")
        
        # 2. Save it
        with open(upload_path, 'wb') as f:
            f.write(response.content)
            
        # 3. Extract data for preview
        json_data = utils.dxf_to_json(upload_path)
        canvas_data = utils.extract_canvas_data(json_data, upload_path)
        
        # 4. Save session
        utils.save_session(session_id, {
            'original_dxf': upload_path,
            'filename': filename,
            'json_data': json_data
        })
        
        return {"success": True, "session_id": session_id, "canvas_data": canvas_data}
    except Exception as e:
        return {"error": str(e)}, 500

