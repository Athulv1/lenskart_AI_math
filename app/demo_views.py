from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

def demo_page(request):
    """Serve the AI Project Demo frontend"""
    return render(request, 'demo.html')

@csrf_exempt
@require_http_methods(["GET"])
def demo_projects_api(request):
    """API endpoint to get projects for the demo frontend"""
    from .models import Project
    
    # Filter to show only specific projects
    ALLOWED_PROJECT_NAMES = [
        'Bangalore Gottigere',
        'Whitefield',
        'Kolanchery version 3',
        'Bedigeri ground floor'
    ]
    
    projects = Project.objects.filter(name__in=ALLOWED_PROJECT_NAMES).prefetch_related('files')
    
    projects_data = []
    for project in projects:
        files_data = []
        for file in project.files.all():
            files_data.append({
                'id': str(file.id),
                'filename': file.file.name.split('/')[-1] if file.file else 'Unknown',
                'file_type': file.file_type if hasattr(file, 'file_type') else 'unknown',
                'created_at': file.created_at.isoformat()
            })
        
        projects_data.append({
            'id': str(project.id),
            'name': project.name,
            'files': files_data
        })
    
    return JsonResponse({'projects': projects_data})

@csrf_exempt
@require_http_methods(["POST"])
def demo_process_api(request):
    """API endpoint to process floorplan from the demo frontend"""
    import requests
    import uuid
    
    try:
        data = json.loads(request.body)
        file_id = data.get('file_id')
        processing_mode = data.get('mode', 'math')  # 'math' or 'ai'
        ai_prompt = data.get('prompt', '')  # AI prompt if provided
        
        if not file_id:
            return JsonResponse({'error': 'file_id is required'}, status=400)
        
        # Validate file_id is a valid UUID
        try:
            uuid.UUID(file_id)
        except ValueError:
            return JsonResponse({'error': 'Invalid file_id format'}, status=400)
        
        # First, update the project's processing mode if AI is selected
        if processing_mode == 'ai':
            from .models import ProjectFile, Project
            try:
                project_file = ProjectFile.objects.get(id=file_id)
                project = project_file.project
                
                # Update project processing mode
                project.processing_mode = 'ai'
                
                # Update AI prompt if provided
                if ai_prompt:
                    project.ai_prompt_text = ai_prompt
                
                project.save()
                print(f"✅ Updated project {project.id} to use AI processing mode")
            except ProjectFile.DoesNotExist:
                return JsonResponse({'error': 'Project file not found'}, status=404)
        
        # Call the internal process API
        process_url = f"http://localhost:8001/api/app1/process-floorplan/{file_id}/"
        
        response = requests.post(process_url, headers={
            'Content-Type': 'application/json',
        })
        
        if response.status_code == 200:
            result = response.json()
            
            # DEBUG: Log the actual API response
            print(f"🔍 DEBUG: API response = {result}")
            
            # Prioritize dxf_url (direct media access) over processed_file_id (download API)
            download_url = result.get('dxf_url')
            print(f"🔍 DEBUG: dxf_url from response = {download_url}")
            
            if not download_url and result.get('processed_file_id'):
                download_url = f"/api/app1/download/{result.get('processed_file_id')}/"
                print(f"🔍 DEBUG: Using fallback download URL = {download_url}")
            
            return JsonResponse({
                'success': True,
                'message': result.get('message'),
                'download_url': download_url,
                'processing_mode': processing_mode,
                'ai_output_dir': result.get('ai_output_dir') if processing_mode == 'ai' else None
            })
        else:
            # Even if there's an error, check if DXF was generated
            try:
                result = response.json()
                error_message = result.get('message', '')
                
                # Check if it's a database constraint error but file was generated
                if 'null value in column "status"' in error_message and 'project_files/' in error_message:
                    # Extract the file path from error message
                    # Format: "project_files/2025/11/04/image_F4bz1Dn_processed_XXX.dxf"
                    import re
                    file_path_match = re.search(r'(project_files/[^\s,)]+\.dxf)', error_message)
                    
                    if file_path_match:
                        file_path = file_path_match.group(1)
                        # Convert to media URL
                        download_url = f"/media/{file_path}"
                        
                        return JsonResponse({
                            'success': True,
                            'message': 'Successfully completed! Ready for AI enhancement',
                            'download_url': download_url,
                            'processing_mode': processing_mode,
                            'warning': 'DXF generated successfully (database constraint ignored)'
                        })
                
                # Check if processed_file_id exists
                processed_file_id = result.get('processed_file_id')
                if processed_file_id:
                    return JsonResponse({
                        'success': True,
                        'message': 'Successfully completed! Ready for AI enhancement',
                        'processed_file_id': processed_file_id,
                        'download_url': f"/api/app1/download/{processed_file_id}/",
                        'processing_mode': processing_mode,
                        'warning': 'DXF generated successfully'
                    })
            except:
                pass
            
            return JsonResponse({
                'success': False,
                'error': f"Processing failed: {response.text}"
            }, status=response.status_code)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
