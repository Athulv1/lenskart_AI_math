# 📋 Django Backend Files Needed for Integration

## Overview
This document lists the **minimum Django files** needed to integrate with AI_DASHBOARD Flask app. You only need to add/modify these files in your existing Django project.

---

## 🎯 Required Django Files (3 files only)

### 1. `app/demo_views.py` - Demo API Views
**Location:** `your_django_project/app/demo_views.py`

**Purpose:** Provides API endpoints for the demo page

**Code:**
```python
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
    
    projects = Project.objects.all().prefetch_related('files')
    
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
        processing_mode = data.get('mode', 'math')
        
        if not file_id:
            return JsonResponse({'error': 'file_id is required'}, status=400)
        
        try:
            uuid.UUID(file_id)
        except ValueError:
            return JsonResponse({'error': 'Invalid file_id format'}, status=400)
        
        # Call the internal process API
        process_url = f"http://localhost:8001/api/app1/process-floorplan/{file_id}/"
        
        response = requests.post(process_url, headers={
            'Content-Type': 'application/json',
        })
        
        if response.status_code == 200:
            result = response.json()
            return JsonResponse({
                'success': True,
                'message': result.get('message'),
                'processed_file_id': result.get('processed_file_id'),
                'download_url': f"/api/app1/download/{result.get('processed_file_id')}/"
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f"Processing failed: {response.text}"
            }, status=response.status_code)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

---

### 2. `templates/demo.html` - Demo Frontend Page
**Location:** `your_django_project/templates/demo.html`

**Purpose:** User interface for selecting projects and generating floor plans

**Download:** Copy from `lenskart_backend/templates/demo.html`

**Key JavaScript Section** (for Flask integration):
```javascript
generateAiBtn.addEventListener("click", async () => {
    if (currentProject && processableFileId) {
        logMessage("Opening AI DXF Fixture Mover app...", "success");
        
        // Build URL with file path if we have a generated DXF
        let aiAppUrl = 'http://localhost:5000';
        if (generatedDxfPath) {
            // Pass the file path as URL parameter
            const fullPath = window.location.origin + generatedDxfPath;
            aiAppUrl += '?autoload=' + encodeURIComponent(fullPath);
            logMessage("📎 Auto-loading generated DXF file into AI app...", "info");
        }
        
        // Open Flask app in new window with file parameter
        window.open(aiAppUrl, '_blank');
        logMessage("AI app opened in new window", "success");
    }
});
```

---

### 3. `backend/urls.py` - Add Demo URLs
**Location:** `your_django_project/backend/urls.py`

**Add these routes:**
```python
from django.urls import path
from app.demo_views import demo_page, demo_projects_api, demo_process_api

urlpatterns = [
    # ... existing urls ...
    
    # Demo page routes
    path('demo/', demo_page, name='demo_page'),
    path('demo/api/projects/', demo_projects_api, name='demo_projects_api'),
    path('demo/api/process/', demo_process_api, name='demo_process_api'),
]
```

---

## 📂 File Structure in Django Project

```
your_django_project/
├── app/
│   ├── demo_views.py          ← ADD THIS
│   ├── models.py              (existing)
│   ├── api.py                 (existing)
│   └── ...
├── backend/
│   ├── urls.py                ← MODIFY THIS (add demo routes)
│   ├── settings.py            (existing)
│   └── ...
├── templates/
│   └── demo.html              ← ADD THIS
├── media/                     (auto-created)
│   └── project_files/         (for generated DXF)
└── manage.py
```

---

## ⚙️ Django Settings Required

Ensure these settings in `backend/settings.py`:

```python
# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CORS if needed
INSTALLED_APPS = [
    # ...
    'corsheaders',  # Optional: if Flask and Django on different domains
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add this if using CORS
    # ... other middleware
]

# Allow Flask to access Django media files
CORS_ALLOW_ALL_ORIGINS = True  # Or specify: CORS_ALLOWED_ORIGINS = ['http://localhost:5000']
```

---

## 🚀 Integration Steps

### Step 1: Add Files to Django
```bash
# Copy these files to your Django project:
cp demo_views.py your_django_project/app/
cp demo.html your_django_project/templates/
```

### Step 2: Update URLs
Edit `your_django_project/backend/urls.py` and add the demo routes shown above.

### Step 3: Run Django
```bash
cd your_django_project
python3 manage.py runserver 8001
```

### Step 4: Clone and Run Flask AI_DASHBOARD
```bash
git clone -b django-integration-minimal https://github.com/Athulv1/AI_DASHBOARD.git
cd AI_DASHBOARD
pip install Flask flask-cors ezdxf google-generativeai werkzeug
python3 app.py
```

### Step 5: Test Integration
1. Open http://127.0.0.1:8001/demo/
2. Select project and click "Generate with AI"
3. Flask opens with DXF loaded automatically!

---

## 📦 Download Template Files

You can download the complete template files from:

**GitHub Repository:** https://github.com/Athulv1/AI_DASHBOARD/tree/django-integration-minimal

**Files to download:**
1. `DJANGO_FILES_NEEDED.md` (this file)
2. Download `demo.html` from any Django Lenskart project
3. Download `demo_views.py` from any Django Lenskart project

Or create them using the code snippets above.

---

## ✅ That's It!

You only need these **3 files** in your Django project:
1. ✅ `app/demo_views.py`
2. ✅ `templates/demo.html`
3. ✅ `backend/urls.py` (modified)

The Flask AI_DASHBOARD is a completely separate application - just clone and run it!

---

## 🔗 Both Applications Together

```
Project Structure:
├── your_django_project/        # Your Django backend
│   ├── app/demo_views.py       # Add this
│   ├── templates/demo.html     # Add this
│   └── backend/urls.py         # Modify this
│
└── AI_DASHBOARD/               # Clone from GitHub
    ├── app.py
    ├── templates/
    ├── static/
    └── ...
```

**Two separate applications, one simple integration!** 🎉

---

**Need Help?** Check:
- DJANGO_INTEGRATION_README.md
- DEPLOYMENT_GUIDE.md
- REQUIRED_FILES_CHECKLIST.md
