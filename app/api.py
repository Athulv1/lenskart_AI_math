from ninja import NinjaAPI, File
from ninja.files import UploadedFile
from django.shortcuts import get_object_or_404
from typing import List
import os
import uuid

from .models import Project, ProjectFile
from .schema import (
    ProjectCreateSchema, 
    ProjectSchema, 
    ProjectDetailSchema,
    ErrorSchema
)

api = NinjaAPI()

@api.post("/projects/", response={201: ProjectSchema, 400: ErrorSchema})
def create_project(request, payload: ProjectCreateSchema):
    try:
        project = Project.objects.create(
            name=payload.name,
            description=payload.description
        )
        return 201, project
    except Exception as e:
        return 400, {"message": str(e)}
    

@api.post("/projects/{project_id}/files/", response={201: ProjectDetailSchema, 404: ErrorSchema, 400: ErrorSchema})
def upload_project_files(request, project_id: uuid.UUID, files: List[UploadedFile] = File(...)):
    try:
        project = get_object_or_404(Project, id=project_id)
        
        for file in files:
            # Get file extension for validation only
            _, ext = os.path.splitext(file.name)
            ext = ext.lower().lstrip('.')
            
            # Validate file type
            allowed_extensions = ['png', 'jpg', 'jpeg', 'usdz']
            if ext not in allowed_extensions:
                return 400, {"message": f"File type {ext} not allowed"}
            
            # Create project file WITHOUT setting file_type
            project_file = ProjectFile.objects.create(
                project=project,
                file=file
                # Don't set file_type here - it's determined automatically by the property
            )
        
        # Return updated project with files
        return 201, project
    except Project.DoesNotExist:
        return 404, {"message": "Project not found"}
    except Exception as e:
        return 400, {"message": str(e)}  

@api.get("/projects/{project_id}/", response={200: ProjectDetailSchema, 404: ErrorSchema})
def get_project(request, project_id: uuid.UUID):
    try:
        project = get_object_or_404(Project, id=project_id)
        return 200, project
    except Project.DoesNotExist:
        return 404, {"message": "Project not found"}
