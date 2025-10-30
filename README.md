# 🏢 Lenskart AI-Powered Floor Planning System

**Full-Stack DXF Floor Plan Editor with AI-Driven Fixture Optimization**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green)](https://www.djangoproject.com/)
[![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Latest-blue)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red)](LICENSE)

---

## 🌟 Overview

A comprehensive floor planning solution for Lenskart retail stores, combining:
- **Django Backend** (Port 8001) - RESTful API, database management, DXF processing
- **Flask AI Dashboard** (Port 5000) - Interactive canvas editor with AI-powered fixture optimization
- **Google Gemini AI** - Intelligent fixture placement and space optimization
- **Computer Vision** - Automated floor plan analysis and fixture detection

**Live Demo:** `https://lenskart.thinkneural.ai`

---

## ✨ Key Features

### 🎨 **Interactive Canvas Editor**
- **Drag-and-drop fixture movement** with real-time coordinate tracking
- **70+ fixture types** with high-quality PNG rendering (clinic units, screens, tables, seating, etc.)
- **Pan & Zoom controls** - Mouse wheel zoom, Ctrl+drag pan mode
- **Multi-select support** - Ctrl+click for batch operations
- **Professional UI** - Navy/teal architecture theme with glassmorphism effects

### 🤖 **AI-Powered Optimization**
- **Google Gemini 1.5 Pro** integration for intelligent fixture rearrangement
- **Natural language prompts** - "Move all clinics to the left wall"
- **Automatic space optimization** - Minimizes wasted space and improves traffic flow
- **Collision detection** - Ensures fixtures don't overlap
- **Accessibility compliance** - Maintains ADA-compliant pathways

### 📐 **DXF Processing**
- **Complete DXF support** - Read/write AutoCAD DXF files with full fidelity
- **Block entity handling** - Preserves complex fixture definitions
- **Layer management** - Separate layers for walls, fixtures, annotations
- **Coordinate transformation** - Handles rotations, scaling, mirroring
- **Real-time updates** - Changes sync between canvas and DXF file

### 🔄 **Two-Way Communication**
- **Django ↔ Flask integration** - Seamless data flow between applications
- **Session management** - Persistent user sessions across both apps
- **URL-based file transfer** - Secure DXF file sharing
- **Live updates** - Real-time fixture position synchronization

### 📱 **RESTful API**
- **Django Ninja** - Fast, type-safe API endpoints
- **Mobile-ready** - iOS/Android client support
- **File upload/download** - Handle large DXF files efficiently
- **Project management** - Multi-project support with versioning

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Server                         │
│                  13.201.224.32 (AWS)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────┐      ┌──────────────────────┐   │
│  │   Django Backend     │      │   Flask AI Dashboard │   │
│  │   Port: 8001         │◄────►│   Port: 5000         │   │
│  │                      │      │                      │   │
│  │ • RESTful API        │      │ • Canvas Editor      │   │
│  │ • PostgreSQL DB      │      │ • Gemini AI          │   │
│  │ • DXF Processing     │      │ • Image Rendering    │   │
│  │ • Admin Panel        │      │ • Real-time Updates  │   │
│  └──────────────────────┘      └──────────────────────┘   │
│           │                              │                  │
│           └──────────┬───────────────────┘                  │
│                      ▼                                      │
│           ┌──────────────────────┐                         │
│           │   PostgreSQL DB      │                         │
│           │   (lenskart_db)      │                         │
│           └──────────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   Google Gemini API  │
              │   (AI Processing)    │
              └──────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **PostgreSQL 12+**
- **Git**
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/ThinkNeuralAi/lenskart_backend.git
cd lenskart_backend
git checkout feature/ai-model
```

### 2️⃣ Set Up Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows
```

### 3️⃣ Install Dependencies

```bash
# Django backend dependencies
pip install -r requirements.txt

# Flask AI Dashboard dependencies
pip install flask flask-cors google-generativeai werkzeug
```

### 4️⃣ Configure Environment Variables

Create `.env` file in project root:

```bash
# Database Settings
DB_NAME=lenskart_db
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Google Gemini API
GOOGLE_API_KEY=your-gemini-api-key-here
```

### 5️⃣ Set Up Database

```bash
# Start PostgreSQL
sudo service postgresql start

# Create database
sudo -u postgres psql -c "CREATE DATABASE lenskart_db;"
sudo -u postgres psql -c "CREATE USER your_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE lenskart_db TO your_user;"

# Run migrations
python manage.py migrate
```

### 6️⃣ Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7️⃣ Run Applications

**Terminal 1 - Django Backend:**
```bash
python manage.py runserver 8001
```

**Terminal 2 - Flask AI Dashboard:**
```bash
cd AI_DASHBOARD
python app.py
```

### 8️⃣ Access Applications

- **Django Admin:** http://localhost:8001/admin/
- **API Documentation:** http://localhost:8001/api/app1/docs
- **Demo Page:** http://localhost:8001/demo/
- **Flask AI Dashboard:** http://localhost:5000/

---

## 📁 Project Structure

```
lenskart_backend/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables
│
├── backend/                    # Django project settings
│   ├── settings.py            # Main configuration
│   ├── urls.py                # URL routing (with Flask integration)
│   └── wsgi.py                # WSGI config for production
│
├── app/                        # Main Django application
│   ├── models.py              # Database models
│   ├── api.py                 # Ninja API endpoints
│   ├── views.py               # View functions
│   ├── demo_views.py          # Flask integration endpoints ✨ NEW
│   ├── ai_integration.py      # AI helper functions ✨ NEW
│   ├── DXF_Controller.py      # DXF processing logic
│   ├── CV_Controller.py       # Computer Vision controller
│   ├── Fixture.py             # Fixture data models
│   └── migrations/            # Database migrations
│
├── templates/                  # Django templates
│   └── demo.html              # Demo page ✨ NEW
│
├── media/                      # User uploaded files
│   └── project_files/         # DXF files storage
│
└── AI_DASHBOARD/              # Flask AI Dashboard ✨ NEW
    ├── app.py                 # Main Flask application
    ├── enhanced_dxf_to_json.py # DXF ↔ JSON converter
    ├── ai_fixture_mover.py    # Gemini AI integration
    │
    ├── templates/             # Flask templates
    │   ├── index.html         # Upload page
    │   └── canvas.html        # Interactive canvas editor
    │
    ├── static/                # Static assets
    │   ├── css/
    │   │   └── style.css      # Professional UI styles
    │   ├── js/
    │   │   └── canvas-editor.js # Canvas interaction logic
    │   └── images/            # Fixture PNG images (70+)
    │       ├── Door.png
    │       ├── pickup window.png
    │       ├── Clinic_with_sink.png
    │       └── ... (67 more)
    │
    ├── uploads/               # User uploaded DXF files
    └── outputs/               # AI-modified output files
```

---

## 🎯 Usage Guide

### **1. Upload Floor Plan**

1. Visit http://localhost:5000/
2. Upload a DXF file or provide a URL
3. Wait for processing (blueprint extraction + fixture detection)

### **2. Edit Fixtures**

- **Select:** Click on fixtures to select
- **Move:** Drag fixtures to new positions
- **Pan:** Hold Ctrl + drag to pan view
- **Zoom:** Mouse wheel to zoom in/out
- **Multi-select:** Ctrl+click multiple fixtures

### **3. AI Optimization**

1. Write a natural language prompt:
   ```
   "Move all clinic units along the right wall"
   "Rearrange fixtures to maximize customer flow"
   "Create more space near the entrance"
   ```

2. Click "Generate with AI"

3. Review AI suggestions and apply changes

### **4. Download Results**

- Click "Download Modified DXF"
- File is saved in AutoCAD-compatible format
- All changes preserved (positions, rotations, scales)

---

## 🔧 Configuration

### Django Settings

**File:** `backend/settings.py`

```python
# Key settings
DEBUG = False  # Set to False in production
ALLOWED_HOSTS = ['lenskart.thinkneural.ai', '13.201.224.32']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# Templates directory (for Flask integration)
TEMPLATES[0]['DIRS'] = [BASE_DIR / 'templates']
```

### Flask Settings

**File:** `AI_DASHBOARD/app.py`

```python
# Server configuration
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Google Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
```

---

## 🧪 API Endpoints

### Django Backend (Port 8001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/` | Django admin panel |
| GET | `/api/app1/docs` | API documentation |
| GET | `/demo/` | Demo page (Flask integration) |
| POST | `/api/app1/process-floorplan/{file_id}/` | Process DXF file |
| GET | `/api/app1/projects/` | List all projects |
| POST | `/api/app1/upload/` | Upload DXF file |

### Flask AI Dashboard (Port 5000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Upload page |
| POST | `/upload` | Upload DXF file |
| POST | `/upload-from-url` | Upload from Django URL |
| GET | `/canvas/<session_id>` | Canvas editor page |
| POST | `/ai_rearrange` | AI fixture optimization |
| GET | `/download/<session_id>` | Download modified DXF |

---

## 🛠️ Development

### Common Django Commands

```bash
# Run development server
python manage.py runserver 8001

# Create/apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Open Django shell
python manage.py shell

# Run tests
python manage.py test
```

### Common Flask Commands

```bash
# Run Flask development server
cd AI_DASHBOARD
python app.py

# Run with debug mode
FLASK_DEBUG=1 python app.py

# Run on custom port
python app.py --port 5001
```

---

## 🚢 Production Deployment

### Using Gunicorn (Recommended)

**Django:**
```bash
gunicorn backend.wsgi:application \
    --bind 0.0.0.0:8001 \
    --workers 4 \
    --timeout 120
```

**Flask:**
```bash
cd AI_DASHBOARD
gunicorn app:app \
    --bind 0.0.0.0:5000 \
    --workers 2 \
    --timeout 300
```

### Using Systemd Services

Create `/etc/systemd/system/django-lenskart.service`:

```ini
[Unit]
Description=Django Lenskart Backend
After=network.target postgresql.service

[Service]
User=your_user
WorkingDirectory=/path/to/lenskart_backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn backend.wsgi:application --bind 0.0.0.0:8001 --workers 4

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/flask-ai-dashboard.service`:

```ini
[Unit]
Description=Flask AI Dashboard
After=network.target

[Service]
User=your_user
WorkingDirectory=/path/to/lenskart_backend/AI_DASHBOARD
Environment="PATH=/path/to/venv/bin"
Environment="GOOGLE_API_KEY=your-api-key"
ExecStart=/path/to/venv/bin/gunicorn app:app --bind 0.0.0.0:5000 --workers 2

[Install]
WantedBy=multi-user.target
```

Enable and start services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable django-lenskart flask-ai-dashboard
sudo systemctl start django-lenskart flask-ai-dashboard
```

### Nginx Configuration

```nginx
# Django Backend
upstream django_backend {
    server 127.0.0.1:8001;
}

# Flask AI Dashboard
upstream flask_dashboard {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name lenskart.thinkneural.ai;

    # Django routes
    location /api/ {
        proxy_pass http://django_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /admin/ {
        proxy_pass http://django_backend;
        proxy_set_header Host $host;
    }

    location /demo/ {
        proxy_pass http://django_backend;
        proxy_set_header Host $host;
    }

    # Flask AI Dashboard
    location /ai-dashboard/ {
        proxy_pass http://flask_dashboard/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Static files
    location /static/ {
        alias /path/to/lenskart_backend/static/;
    }

    location /media/ {
        alias /path/to/lenskart_backend/media/;
    }
}
```

---

## 🧩 Technologies Used

### Backend
- **Django 5.2** - Web framework
- **Django Ninja** - Modern API framework
- **PostgreSQL** - Database
- **ezdxf 1.4** - DXF file processing
- **Pillow** - Image processing
- **OpenCV** - Computer vision

### Frontend
- **Flask 3.0** - Lightweight web framework
- **HTML5 Canvas** - Interactive drawing
- **CSS3** - Professional styling
- **Vanilla JavaScript** - No framework dependencies

### AI & ML
- **Google Gemini 1.5 Pro** - Large language model
- **Pytesseract** - OCR text extraction
- **NumPy** - Numerical computations

### DevOps
- **Gunicorn** - WSGI server
- **Nginx** - Reverse proxy
- **Systemd** - Process management
- **Git** - Version control

---

## 📊 Database Schema

### Key Models

**Project**
- `id` (UUID) - Primary key
- `name` (String) - Project name
- `created_at` (DateTime) - Creation timestamp
- `status` (String) - Processing status

**ProjectFile**
- `id` (UUID) - Primary key
- `project` (FK) - Related project
- `file` (File) - DXF file path
- `status` (String) - File status
- `created_at` (DateTime) - Upload timestamp

---

## 🔐 Security

- ✅ **CSRF Protection** - Django CSRF tokens
- ✅ **SQL Injection Prevention** - ORM parameterized queries
- ✅ **File Upload Validation** - Type and size checks
- ✅ **Environment Variables** - Sensitive data in .env
- ✅ **HTTPS** - SSL/TLS encryption in production
- ✅ **CORS** - Controlled cross-origin requests

---

## 🐛 Troubleshooting

### PostgreSQL Connection Error

```bash
# Check PostgreSQL status
sudo service postgresql status

# Restart PostgreSQL
sudo service postgresql restart

# Verify credentials in .env
cat .env | grep DB_
```

### Port Already in Use

```bash
# Find process using port 8001
lsof -i :8001

# Kill the process
kill -9 <PID>
```

### Gemini API Errors

```bash
# Verify API key
echo $GOOGLE_API_KEY

# Test API access
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('✅ API working')"
```

### Image Loading Issues

```bash
# Check fixture images exist
ls AI_DASHBOARD/static/images/*.png | wc -l
# Should show 70+

# Verify file permissions
chmod 644 AI_DASHBOARD/static/images/*.png
```

---

## 🤝 Contributing

This is a proprietary project for Lenskart. For internal contributions:

1. Create a feature branch from `feature/ai-model`
2. Make your changes
3. Test thoroughly (Django + Flask)
4. Submit a pull request with detailed description

---

## 📝 License

Proprietary - © 2025 ThinkNeural AI. All rights reserved.

---

## 👥 Team

- **Backend Development** - Django API, Database, DXF Processing
- **AI Development** - Gemini Integration, Optimization Algorithms
- **Frontend Development** - Canvas Editor, UI/UX
- **DevOps** - Deployment, CI/CD, Infrastructure

---

## 📞 Support

For issues or questions:
- **Email:** support@thinkneural.ai
- **GitHub Issues:** [Create an issue](https://github.com/ThinkNeuralAi/lenskart_backend/issues)

---

## 🎉 Acknowledgments

- Google Gemini AI for intelligent optimization
- AutoCAD for DXF format specification
- Open source community for amazing libraries

---

**Built with ❤️ by ThinkNeural AI**

