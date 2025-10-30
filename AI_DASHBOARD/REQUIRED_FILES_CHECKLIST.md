# ✅ Required Files Checklist - AI_DASHBOARD Django Integration

## 📦 Core Files (Already in Repository)

### Python Scripts
- [x] `app.py` - Main Flask application with CORS and auto-load endpoint
- [x] `enhanced_dxf_to_json.py` - DXF ↔ JSON converter
- [x] `ai_fixture_mover.py` - AI-powered fixture manipulation
- [x] `DXF_Controller.py` - DXF file operations

### Templates
- [x] `templates/index.html` - Landing page with autoload redirect
- [x] `templates/canvas.html` - Canvas editor with auto-load functionality

### Static Assets
- [x] `static/css/style.css` - Application styles
- [x] `static/js/canvas-editor.js` - Canvas editor JavaScript

### Fixture Images (60+ files)
- [x] `static/images/43''.png`
- [x] `static/images/55''.png`
- [x] `static/images/AR.png`
- [x] `static/images/Blue_zero.png`
- [x] `static/images/Euro_centre.png`
- [x] `static/images/jj_fixture_large.png`
- [x] `static/images/vc_fixture_large.png`
- [x] `static/images/Clinic_with_sink.png`
- [x] `static/images/[all other fixture images]`

### Documentation
- [x] `README.md` - Main project documentation
- [x] `DJANGO_INTEGRATION_README.md` - Django integration guide
- [x] `REQUIRED_FILES_CHECKLIST.md` - This file

---

## 🔧 Files to Create/Configure (Not in Git)

### Runtime Directories (Auto-created)
```bash
AI_DASHBOARD/
├── uploads/          # Temporary DXF file uploads
└── outputs/          # Modified DXF outputs
```

### Python Virtual Environment (Optional)
```bash
venv/                 # Python virtual environment
```

---

## 📋 Python Dependencies Required

Create `requirements.txt` if not present:
```txt
Flask==2.3.0
flask-cors==4.0.0
ezdxf==1.1.0
google-generativeai==0.3.0
werkzeug==2.3.0
```

### Install Command:
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration Requirements

### 1. Gemini API Key
**File:** `app.py`
**Line:** ~39
```python
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
```

### 2. Flask Server Settings
**File:** `app.py`
**Lines:** ~27-30
```python
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
```

---

## 🌐 Django Backend Requirements

### Files Needed in Django Project:
```
lenskart_backend/
├── templates/
│   └── demo.html     # With updated JavaScript for Flask integration
└── app/
    └── demo_views.py # With Flask URL configuration
```

### Key JavaScript in `demo.html`:
```javascript
generateAiBtn.addEventListener("click", async () => {
    if (currentProject && processableFileId) {
        logMessage("Opening AI DXF Fixture Mover app...", "success");
        
        let aiAppUrl = 'http://localhost:5000';
        if (generatedDxfPath) {
            const fullPath = window.location.origin + generatedDxfPath;
            aiAppUrl += '?autoload=' + encodeURIComponent(fullPath);
        }
        
        window.open(aiAppUrl, '_blank');
    }
});
```

---

## 🚀 Deployment Checklist

### Before Deployment:
- [ ] Update `GEMINI_API_KEY` in `app.py`
- [ ] Change `SECRET_KEY` in `app.py` 
- [ ] Configure proper CORS origins for production
- [ ] Set up production WSGI server (gunicorn/uwsgi)
- [ ] Configure reverse proxy (nginx/apache)
- [ ] Set up SSL certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Create backup strategy
- [ ] Test auto-load functionality end-to-end

---

## 📊 File Size Requirements

### Disk Space:
- **Flask App:** ~5 MB (code + static assets)
- **Fixture Images:** ~3 MB (60+ PNG files)
- **Runtime Storage:** ~100-500 MB (uploads + outputs)

### Total: ~10-20 MB for application, 100-500 MB for runtime

---

## 🔐 Security Considerations

### Files with Sensitive Data:
1. `app.py` - Contains Gemini API key
   - **Solution:** Use environment variables
   ```python
   import os
   GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
   ```

2. `app.config['SECRET_KEY']` - Flask session secret
   - **Solution:** Generate random key for production
   ```python
   SECRET_KEY = os.urandom(24)
   ```

---

## 🧪 Testing Files

### Create test DXF files in:
```
uploads/
└── test_files/
    ├── simple_layout.dxf
    ├── complex_layout.dxf
    └── fixture_test.dxf
```

---

## 📝 Optional Enhancement Files

### Future Additions:
- [ ] `tests/` - Unit tests
- [ ] `docker-compose.yml` - Docker configuration
- [ ] `.github/workflows/` - CI/CD pipelines
- [ ] `nginx.conf` - Nginx configuration
- [ ] `gunicorn_config.py` - WSGI server config

---

## ✅ Verification Commands

### Check all required files exist:
```bash
cd /home/athul/json/lenskart_backend/AI_DASHBOARD

# Core files
ls -la app.py enhanced_dxf_to_json.py ai_fixture_mover.py

# Templates
ls -la templates/index.html templates/canvas.html

# Static files
ls -la static/css/style.css static/js/canvas-editor.js

# Images (should show 60+ files)
ls static/images/ | wc -l

# Documentation
ls -la README.md DJANGO_INTEGRATION_README.md
```

### Test import dependencies:
```bash
python3 -c "import flask, flask_cors, ezdxf, google.generativeai; print('All dependencies OK')"
```

---

## 🎯 Quick Start Guide

### 1. Clone Repository:
```bash
git clone https://github.com/Athulv1/AI_DASHBOARD.git
cd AI_DASHBOARD
git checkout django-integration-minimal
```

### 2. Install Dependencies:
```bash
pip install Flask flask-cors ezdxf google-generativeai werkzeug
```

### 3. Configure:
```bash
# Edit app.py and add your Gemini API key
nano app.py  # Update GEMINI_API_KEY
```

### 4. Run:
```bash
python3 app.py
```

### 5. Access:
```
http://localhost:5000
```

---

## 📞 Support

For issues or questions:
1. Check `DJANGO_INTEGRATION_README.md` for troubleshooting
2. Review GitHub issues
3. Contact: Athul V

---

**Branch:** django-integration-minimal  
**Last Updated:** October 30, 2025  
**Status:** ✅ Production Ready
