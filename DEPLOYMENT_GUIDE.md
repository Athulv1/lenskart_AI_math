# 🚀 Lenskart Backend - Complete Deployment Guide

**Last Updated:** December 18, 2025  
**Branch:** feature/ai-model  
**Repository:** ThinkNeuralAi/lenskart_backend

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Prerequisites](#prerequisites)
3. [Project Structure](#project-structure)
4. [Environment Setup](#environment-setup)
5. [Django App Deployment](#django-app-deployment)
6. [Flask App Deployment](#flask-app-deployment)
7. [Database Configuration](#database-configuration)
8. [Production Deployment](#production-deployment)
9. [Troubleshooting](#troubleshooting)

---

## 🏗️ System Overview

This project consists of **TWO main applications**:

### 1. **Django Backend** (Main Application)
- **Port:** 8001
- **Purpose:** Main backend API, database management, project management
- **Location:** `/home/athul/lenskart/`
- **Entry Point:** `manage.py`

### 2. **Flask App** (AI Dashboard)
- **Port:** 5000
- **Purpose:** DXF fixture editor with AI-powered layout optimization
- **Location:** `/home/athul/lenskart/AI_DASHBOARD/`
- **Entry Point:** `app.py`

**Communication Flow:**
```
User → Django (8001) → Generates DXF → Redirects to Flask (5000) → AI Processing → Returns modified DXF
```

---

## ✅ Prerequisites

### System Requirements
```bash
- Python 3.8+
- PostgreSQL 12+ (production) or SQLite (development)
- 4GB+ RAM
- 10GB+ disk space
```

### Required Python Packages
```bash
# Django app requirements
Django==4.2+
djangorestframework
django-cors-headers
Pillow
ezdxf
opencv-python
pytesseract
shapely
numpy

# Flask app requirements
Flask==3.1.2
flask-cors
ezdxf
google-generativeai
requests
python-dotenv
```

---

## 📁 Project Structure

```
/home/athul/lenskart/
│
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── .env                              # Environment variables (DO NOT COMMIT)
├── db.sqlite3                        # SQLite database (dev only)
│
├── backend/                          # Django project settings
│   ├── __init__.py
│   ├── settings.py                   # Main settings ⚠️ LOCAL ONLY
│   ├── urls.py                       # URL routing
│   └── wsgi.py                       # WSGI config for production
│
├── app/                              # Main Django application
│   ├── __init__.py
│   ├── models.py                     # Database models
│   ├── views.py                      # API views
│   ├── admin.py                      # Admin panel
│   ├── DXF_Controller.py            # DXF processing logic
│   ├── Fixture.py                    # Fixture models
│   ├── CV_Controller.py             # Computer vision logic
│   └── migrations/                   # Database migrations
│
├── media/                            # User uploaded files (DXF, images)
├── static/                           # Static files (CSS, JS, images)
├── staticfiles/                      # Collected static files (production)
├── templates/                        # Django HTML templates
├── logs/                             # Application logs
├── venv/                             # Virtual environment
│
└── AI_DASHBOARD/                     # Flask application
    ├── app.py                        # Main Flask app ⭐
    ├── requirements.txt              # Flask dependencies
    ├── enhanced_dxf_to_json.py      # DXF ↔ JSON converter ⭐
    ├── ai_fixture_mover.py          # AI fixture logic ⭐
    ├── prompt_for_rearrange.txt     # AI prompt template
    │
    ├── static/                       # Frontend assets
    │   ├── css/
    │   ├── js/
    │   │   └── canvas-editor.js     # Canvas logic ⭐
    │   └── images/                   # Fixture PNG images (60+ files)
    │
    ├── templates/                    # HTML templates
    │   ├── index.html               # Landing page
    │   ├── canvas.html              # Main canvas editor ⭐
    │   └── canvas_preview.html      # Preview modal
    │
    ├── uploads/                      # DXF uploads (auto-created)
    ├── outputs/                      # Generated DXF files (auto-created)
    └── session_storage/              # Session persistence ⭐ (auto-created)
```

---

## 🔧 Environment Setup

### 1. Clone Repository
```bash
cd /home/athul
git clone https://github.com/ThinkNeuralAi/lenskart_backend.git lenskart
cd lenskart
git checkout feature/ai-model
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install Django dependencies
pip install -r requirements.txt

# Install Flask dependencies
cd AI_DASHBOARD
pip install -r requirements.txt
cd ..
```

### 4. Configure Environment Variables
```bash
# Create .env file in root directory
nano .env
```

**Required variables:**
```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,your-ip-address

# Database (PostgreSQL for production)
DB_NAME=lenskart_db
DB_USER=lenskart_user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# For SQLite (development only)
# USE_SQLITE=True

# Gemini AI API
GEMINI_API_KEY=your-gemini-api-key-here

# Flask Settings
FLASK_SECRET_KEY=your-flask-secret-key-here
```

---

## 🐘 Database Configuration

### Development (SQLite)
```bash
# Already configured - just run migrations
python manage.py migrate
python manage.py createsuperuser
```

### Production (PostgreSQL)

**1. Install PostgreSQL:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**2. Create Database and User:**
```bash
sudo -u postgres psql

CREATE DATABASE lenskart_db;
CREATE USER lenskart_user WITH PASSWORD 'your-password';
ALTER ROLE lenskart_user SET client_encoding TO 'utf8';
ALTER ROLE lenskart_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE lenskart_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE lenskart_db TO lenskart_user;
\q
```

**3. Update settings.py** (if needed - check current config)

**4. Run Migrations:**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --no-input
```

---

## 🌐 Django App Deployment

### Development Server
```bash
cd /home/athul/lenskart
source venv/bin/activate
python manage.py runserver 0.0.0.0:8001
```

### Production with Gunicorn

**1. Install Gunicorn:**
```bash
pip install gunicorn
```

**2. Test Gunicorn:**
```bash
cd /home/athul/lenskart
gunicorn --bind 0.0.0.0:8001 backend.wsgi:application
```

**3. Create Systemd Service:**
```bash
sudo nano /etc/systemd/system/lenskart-django.service
```

**Service file content:**
```ini
[Unit]
Description=Lenskart Django Application
After=network.target

[Service]
User=athul
Group=www-data
WorkingDirectory=/home/athul/lenskart
Environment="PATH=/home/athul/lenskart/venv/bin"
ExecStart=/home/athul/lenskart/venv/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:8001 \
    --timeout 120 \
    --access-logfile /home/athul/lenskart/logs/django-access.log \
    --error-logfile /home/athul/lenskart/logs/django-error.log \
    backend.wsgi:application

[Install]
WantedBy=multi-user.target
```

**4. Enable and Start Service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable lenskart-django
sudo systemctl start lenskart-django
sudo systemctl status lenskart-django
```

---

## 🎨 Flask App Deployment

### Development Server
```bash
cd /home/athul/lenskart/AI_DASHBOARD
source ../venv/bin/activate
python app.py
```

### Production with Gunicorn (Multi-Worker)

**⚠️ IMPORTANT:** Flask app uses **file-based session storage** for multi-worker compatibility.

**1. Test Multi-Worker Setup:**
```bash
cd /home/athul/lenskart/AI_DASHBOARD
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

**2. Create Systemd Service:**
```bash
sudo nano /etc/systemd/system/lenskart-flask.service
```

**Service file content:**
```ini
[Unit]
Description=Lenskart Flask AI Dashboard
After=network.target

[Service]
User=athul
Group=www-data
WorkingDirectory=/home/athul/lenskart/AI_DASHBOARD
Environment="PATH=/home/athul/lenskart/venv/bin"
Environment="GEMINI_API_KEY=your-api-key-here"
ExecStart=/home/athul/lenskart/venv/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:5000 \
    --timeout 300 \
    --access-logfile /home/athul/lenskart/logs/flask-access.log \
    --error-logfile /home/athul/lenskart/logs/flask-error.log \
    app:app

[Install]
WantedBy=multi-user.target
```

**3. Enable and Start Service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable lenskart-flask
sudo systemctl start lenskart-flask
sudo systemctl status lenskart-flask
```

---

## 🌍 Production Deployment

### Nginx Configuration

**1. Install Nginx:**
```bash
sudo apt install nginx
```

**2. Create Nginx Config:**
```bash
sudo nano /etc/nginx/sites-available/lenskart
```

**Configuration:**
```nginx
# Django Backend
server {
    listen 80;
    server_name yourdomain.com;

    client_max_body_size 50M;

    # Django static files
    location /static/ {
        alias /home/athul/lenskart/staticfiles/;
    }

    # Django media files
    location /media/ {
        alias /home/athul/lenskart/media/;
    }

    # Django API
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}

# Flask AI Dashboard
server {
    listen 80;
    server_name ai.yourdomain.com;  # Or use different path

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    # Flask static files
    location /static/ {
        alias /home/athul/lenskart/AI_DASHBOARD/static/;
        expires 30d;
    }
}
```

**3. Enable Site:**
```bash
sudo ln -s /etc/nginx/sites-available/lenskart /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL Configuration (Optional but Recommended)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d ai.yourdomain.com
```

---

## 🔥 Service Management

### Start All Services
```bash
# Start Django
sudo systemctl start lenskart-django

# Start Flask
sudo systemctl start lenskart-flask

# Start Nginx
sudo systemctl start nginx
```

### Check Status
```bash
# Check Django
sudo systemctl status lenskart-django

# Check Flask
sudo systemctl status lenskart-flask

# Check if ports are listening
sudo netstat -tulpn | grep -E '8001|5000'
```

### View Logs
```bash
# Django logs
tail -f /home/athul/lenskart/logs/django-error.log

# Flask logs
tail -f /home/athul/lenskart/logs/flask-error.log

# Systemd logs
sudo journalctl -u lenskart-django -f
sudo journalctl -u lenskart-flask -f
```

### Restart Services
```bash
# After code changes
sudo systemctl restart lenskart-django
sudo systemctl restart lenskart-flask
```

---

## 🐛 Troubleshooting

### Issue: Invalid Session Error on Flask
**Cause:** Multi-worker deployment without shared session storage  
**Solution:** Already fixed with file-based session storage in `AI_DASHBOARD/session_storage/`

**Verify:**
```bash
ls -la /home/athul/lenskart/AI_DASHBOARD/session_storage/
# Should see .json files
```

### Issue: Multiple AI Generations Not Working
**Cause:** Session JSON not reloaded after modifications  
**Solution:** Already fixed - JSON reloads from modified DXF after each AI operation

### Issue: Django Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --no-input

# Check Nginx config
sudo nginx -t

# Verify permissions
ls -la /home/athul/lenskart/staticfiles/
```

### Issue: Database Connection Error
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U lenskart_user -d lenskart_db -h localhost

# Check .env file
cat /home/athul/lenskart/.env | grep DB_
```

### Issue: Port Already in Use
```bash
# Find process using port
sudo lsof -i :8001
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>
```

### Issue: Gunicorn Workers Crashing
```bash
# Check worker timeout
# Increase in systemd service: --timeout 300

# Check memory
free -h

# Check logs
sudo journalctl -u lenskart-flask -n 100
```

### Clean Session Storage (Optional Maintenance)
```bash
# Remove sessions older than 7 days
find /home/athul/lenskart/AI_DASHBOARD/session_storage/ -name "*.json" -mtime +7 -delete

# Or add to crontab for automatic cleanup
0 0 * * * find /home/athul/lenskart/AI_DASHBOARD/session_storage/ -name "*.json" -mtime +7 -delete
```

---

## 📊 Monitoring & Maintenance

### Health Check Endpoints

**Django:**
```bash
curl http://localhost:8001/admin/
# Should return admin login page
```

**Flask:**
```bash
curl http://localhost:5000/
# Should return landing page HTML
```

### Backup Database

**PostgreSQL:**
```bash
# Backup
pg_dump -U lenskart_user lenskart_db > backup_$(date +%Y%m%d).sql

# Restore
psql -U lenskart_user lenskart_db < backup_20251218.sql
```

**SQLite:**
```bash
# Backup
cp /home/athul/lenskart/db.sqlite3 /home/athul/backups/db_$(date +%Y%m%d).sqlite3
```

### Update Code from Git
```bash
cd /home/athul/lenskart
git pull origin feature/ai-model
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
sudo systemctl restart lenskart-django
sudo systemctl restart lenskart-flask
```

---

## 🎯 Quick Start Checklist

- [ ] Clone repository and checkout `feature/ai-model`
- [ ] Create and activate virtual environment
- [ ] Install all dependencies (Django + Flask)
- [ ] Configure `.env` file with all required variables
- [ ] Setup database (PostgreSQL or SQLite)
- [ ] Run Django migrations
- [ ] Create Django superuser
- [ ] Collect static files
- [ ] Test Django on port 8001
- [ ] Test Flask on port 5000
- [ ] Configure Gunicorn for both apps
- [ ] Setup systemd services
- [ ] Configure Nginx reverse proxy
- [ ] Setup SSL certificates
- [ ] Configure log rotation
- [ ] Setup session cleanup cron job
- [ ] Test end-to-end workflow

---

## 📝 Important Notes

1. **backend/settings.py** - Keep local modifications for development, don't commit
2. **Session Storage** - File-based system in `AI_DASHBOARD/session_storage/` for multi-worker support
3. **API Keys** - Gemini API key required in `.env` for AI features
4. **Ports** - Django: 8001, Flask: 5000 (configurable)
5. **Workers** - Recommended 4 workers for both Django and Flask in production
6. **Timeouts** - Django: 120s, Flask: 300s (AI processing takes longer)
7. **Max Upload** - 50MB for DXF files (configurable in Nginx)

---

## 🆘 Support

**Logs Location:**
- Django: `/home/athul/lenskart/logs/django-error.log`
- Flask: `/home/athul/lenskart/logs/flask-error.log`
- Nginx: `/var/log/nginx/error.log`
- Systemd: `sudo journalctl -u <service-name>`

**Recent Fixes Applied:**
- ✅ Multi-worker session storage (Dec 18, 2025)
- ✅ Multiple consecutive AI generations (Dec 18, 2025)
- ✅ Code cleanup and optimization (Dec 18, 2025)

---

**Version:** 1.0  
**Last Updated:** December 18, 2025  
**Deployment Status:** ✅ Production Ready
