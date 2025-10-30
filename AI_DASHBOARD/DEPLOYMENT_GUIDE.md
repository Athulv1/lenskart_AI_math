# 🚀 Quick Deployment Guide - AI_DASHBOARD Django Integration

## 📦 New Branch Created

**Repository:** https://github.com/Athulv1/AI_DASHBOARD  
**Branch:** `django-integration-minimal`  
**Direct URL:** https://github.com/Athulv1/AI_DASHBOARD/tree/django-integration-minimal

---

## 🎯 What's Included

This branch contains **ONLY** the essential files needed for Django integration:

### Modified Files (3):
1. ✅ `app.py` - Flask app with CORS and auto-load endpoint
2. ✅ `templates/index.html` - Landing page with autoload redirect
3. ✅ `templates/canvas.html` - Canvas editor with auto-load functionality

### New Documentation (2):
1. 📖 `DJANGO_INTEGRATION_README.md` - Complete integration guide
2. 📋 `REQUIRED_FILES_CHECKLIST.md` - Files and dependencies checklist
3. 🚀 `DEPLOYMENT_GUIDE.md` - This file

### Existing Files (Already in Repo):
- All fixture images in `static/images/` (~60 PNG files)
- CSS and JavaScript files
- Core Python modules (enhanced_dxf_to_json.py, ai_fixture_mover.py)

---

## ⚡ Quick Setup (5 Minutes)

### Step 1: Clone the Branch
```bash
cd /home/athul/json/lenskart_backend
git clone -b django-integration-minimal https://github.com/Athulv1/AI_DASHBOARD.git AI_DASHBOARD
cd AI_DASHBOARD
```

### Step 2: Install Dependencies
```bash
pip install Flask flask-cors ezdxf google-generativeai werkzeug
```

### Step 3: Configure API Key
```bash
nano app.py
# Update line 39: GEMINI_API_KEY = "YOUR_API_KEY_HERE"
```

### Step 4: Start Flask Server
```bash
python3 app.py
```

### Step 5: Start Django (Separate Terminal)
```bash
cd /home/athul/json/lenskart_backend
python3 manage.py runserver 8001
```

### Step 6: Test Integration
1. Open: http://127.0.0.1:8001/demo/
2. Select a project with an image
3. Click "Generate with AI"
4. AI_DASHBOARD opens automatically with DXF loaded! 🎉

---

## 📂 Directory Structure After Clone

```
AI_DASHBOARD/
├── app.py                              ⭐ Modified for Django
├── enhanced_dxf_to_json.py            # DXF converter
├── ai_fixture_mover.py                # AI fixture mover
├── DXF_Controller.py                  # DXF operations
├── templates/
│   ├── index.html                     ⭐ Modified for autoload
│   └── canvas.html                    ⭐ Modified for autoload
├── static/
│   ├── css/
│   │   └── style.css                  # Styles
│   ├── js/
│   │   └── canvas-editor.js           # Canvas editor
│   └── images/                        # 60+ fixture images
├── DJANGO_INTEGRATION_README.md       ⭐ New - Integration guide
├── REQUIRED_FILES_CHECKLIST.md        ⭐ New - Files checklist
├── DEPLOYMENT_GUIDE.md                ⭐ New - This guide
├── README.md                          # Original project README
├── uploads/                           # Auto-created
└── outputs/                           # Auto-created
```

---

## 🔄 Integration Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│  1. User opens Django Demo (port 8001)                 │
│     http://127.0.0.1:8001/demo/                         │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  2. User clicks "Generate with AI" button               │
│     - Django processes image                            │
│     - Generates DXF file                                │
│     - Stores in media/project_files/                    │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  3. Django opens Flask with DXF URL                     │
│     http://localhost:5000/?autoload=<DXF_URL>           │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  4. Flask AI_DASHBOARD (port 5000)                      │
│     - Detects autoload parameter                        │
│     - Fetches DXF from Django                           │
│     - Converts DXF to JSON                              │
│     - Loads into canvas editor                          │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  5. User Edits Fixtures                                 │
│     - Drag and drop fixtures                            │
│     - Use AI prompts for rearrangement                  │
│     - Download modified DXF                             │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 Verification Steps

### 1. Check Branch
```bash
cd /home/athul/json/lenskart_backend/AI_DASHBOARD
git branch
# Should show: * django-integration-minimal
```

### 2. Verify Modified Files
```bash
git diff production-clean-minimal django-integration-minimal
# Shows changes in app.py, templates/index.html, templates/canvas.html
```

### 3. Test Flask Server
```bash
python3 app.py
# Should start on http://127.0.0.1:5000
```

### 4. Test CORS
```bash
curl -H "Origin: http://127.0.0.1:8001" -I http://127.0.0.1:5000/
# Should include: Access-Control-Allow-Origin: *
```

### 5. Test Auto-Load Endpoint
```bash
curl -X POST http://127.0.0.1:5000/upload-from-url \
  -H "Content-Type: application/json" \
  -d '{"dxf_url": "http://127.0.0.1:8001/media/test.dxf"}'
```

---

## 📊 Commits in This Branch

### Commit 1: Core Integration
**Hash:** 6d1dca1  
**Message:** Add Django integration: auto-load DXF from Django backend  
**Changes:**
- Modified `app.py` with CORS and `/upload-from-url` endpoint
- Modified `templates/index.html` with autoload redirect
- Modified `templates/canvas.html` with auto-load functionality

### Commit 2: Documentation
**Hash:** 8215211  
**Message:** Add comprehensive Django integration documentation  
**Changes:**
- Added `DJANGO_INTEGRATION_README.md`

### Commit 3: Checklist
**Hash:** 5432d5c  
**Message:** Add required files checklist and verification guide  
**Changes:**
- Added `REQUIRED_FILES_CHECKLIST.md`

---

## 🌐 Access URLs

### Development:
- **Django Backend:** http://127.0.0.1:8001
- **Django Demo:** http://127.0.0.1:8001/demo/
- **Django Admin:** http://127.0.0.1:8001/admin/
- **Flask AI_DASHBOARD:** http://127.0.0.1:5000
- **Flask Canvas:** http://127.0.0.1:5000/canvas

### Production (Example):
- **Django:** https://lenskart.thinkneural.ai
- **Flask:** https://ai-dashboard.thinkneural.ai

---

## 🔐 Environment Variables (Recommended)

Create `.env` file in AI_DASHBOARD:
```bash
FLASK_APP=app.py
FLASK_ENV=development
GEMINI_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
DJANGO_BASE_URL=http://127.0.0.1:8001
```

Update `app.py` to use environment variables:
```python
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-dev-key')
```

---

## 🐛 Common Issues & Solutions

### Issue 1: CORS Error
**Symptom:** Browser console shows CORS policy error  
**Solution:** 
```bash
pip install flask-cors
# Verify CORS(app) is in app.py
```

### Issue 2: Connection Refused to Django
**Symptom:** Flask can't fetch DXF from Django  
**Solution:**
```bash
# Check Django is running on port 8001
curl http://127.0.0.1:8001/media/project_files/
```

### Issue 3: Module Not Found
**Symptom:** ImportError when starting Flask  
**Solution:**
```bash
pip install Flask flask-cors ezdxf google-generativeai werkzeug
```

### Issue 4: API Key Error
**Symptom:** Gemini AI operations fail  
**Solution:**
```python
# Update app.py line 39
GEMINI_API_KEY = "your-valid-api-key"
```

---

## 📈 Performance Tips

1. **Use Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Enable Debug Mode for Development:**
   ```python
   # In app.py
   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5000, debug=True)
   ```

3. **Use Production Server for Deployment:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

---

## 🎓 Learning Resources

- **Flask Documentation:** https://flask.palletsprojects.com/
- **Flask-CORS:** https://flask-cors.readthedocs.io/
- **EZDXF Documentation:** https://ezdxf.readthedocs.io/
- **Gemini API:** https://ai.google.dev/

---

## 📞 Support & Contact

**Repository:** https://github.com/Athulv1/AI_DASHBOARD  
**Issues:** https://github.com/Athulv1/AI_DASHBOARD/issues  
**Pull Requests:** https://github.com/Athulv1/AI_DASHBOARD/pulls

**Branch-Specific:**
- View Code: https://github.com/Athulv1/AI_DASHBOARD/tree/django-integration-minimal
- Compare Changes: https://github.com/Athulv1/AI_DASHBOARD/compare/production-clean-minimal...django-integration-minimal

---

## ✅ Success Checklist

- [ ] Branch cloned successfully
- [ ] Dependencies installed
- [ ] Gemini API key configured
- [ ] Flask server starts without errors
- [ ] Django server running on port 8001
- [ ] Can open http://127.0.0.1:5000 in browser
- [ ] Can open http://127.0.0.1:8001/demo in browser
- [ ] "Generate with AI" button works
- [ ] DXF auto-loads in Flask canvas
- [ ] Fixtures visible and draggable
- [ ] Can download modified DXF

---

## 🎉 Conclusion

You now have a fully integrated Django + Flask system where:
- Django handles backend processing and DXF generation
- Flask provides visual DXF editing with AI capabilities
- Both systems communicate seamlessly via auto-load

**Enjoy building amazing floor plans!** 🏗️✨

---

**Created:** October 30, 2025  
**Branch:** django-integration-minimal  
**Status:** ✅ Production Ready  
**Author:** Athul V
