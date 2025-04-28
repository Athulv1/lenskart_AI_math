from ninja import Schema
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from pydantic import Field

class ProjectCreateSchema(Schema):
    name: str
    description: Optional[str] = None

class ProjectSchema(Schema):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime

class ProjectFileSchema(Schema):
    id: UUID
    file_type: str
    filename: str
    created_at: datetime

class ProjectDetailSchema(ProjectSchema):
    files: List[ProjectFileSchema] = Field(default_factory=list)
    
class ErrorSchema(Schema):
    message: str
