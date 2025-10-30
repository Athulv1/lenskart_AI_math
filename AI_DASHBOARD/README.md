# Lenskart AI Floor Planning System

Complete integrated system for floor plan processing and AI-powered fixture layout editing. This repository contains both the Django backend (floor plan processing) and Flask frontend (AI canvas editor).

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/Athulv1/AI_DASHBOARD.git
cd AI_DASHBOARD
git checkout django-integration-minimal

# Install Flask app dependencies
pip install -r requirements.txt

# Install Django backend dependencies
cd django_backend
pip install -r requirements.txt
cd ..
```

### Setup PostgreSQL

```bash
# Start PostgreSQL
sudo service postgresql start

# Create database
sudo -u postgres psql
CREATE DATABASE lenskart_db;
CREATE USER lenskart_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE lenskart_db TO lenskart_user;
\q
```

### Configure Django Backend

```bash
cd django_backend

# Edit .env file with your database credentials
nano .env

# Run migrations
python3 manage.py migrate

# Create superuser (optional)
python3 manage.py createsuperuser
```

### Run the Complete System

**Terminal 1 - Start Django Backend:**
```bash
cd django_backend
python3 manage.py runserver 8001
```

**Terminal 2 - Start Flask AI Dashboard:**
```bash
# From root directory
python3 app.py
```

### Access the Applications

- **Django Demo Page**: http://localhost:8001/demo/
- **Flask AI Dashboard**: http://localhost:5000
- **Django Admin**: http://localhost:8001/admin/

## 📁 Repository Structure

```
AI_DASHBOARD/
├── app.py                          # Flask application (AI canvas editor)
├── requirements.txt                # Flask dependencies
├── templates/                      # Flask templates
│   ├── index.html                  # Landing page
│   └── canvas.html                 # AI canvas editor
├── static/                         # Flask static assets
│   ├── css/
│   ├── js/
│   └── assets/
├── uploads/                        # Uploaded DXF files
├── django_backend/                 # Django backend application
│   ├── manage.py                   # Django management script
│   ├── requirements.txt            # Django dependencies
│   ├── .env                        # Environment configuration
│   ├── app/                        # Main Django app
│   │   ├── demo_views.py           # Demo API endpoints
│   │   ├── models.py               # Database models
│   │   ├── api.py                  # API endpoints
│   │   └── ...
│   ├── backend/                    # Django project settings
│   │   ├── settings.py             # Project configuration
│   │   ├── urls.py                 # URL routing
│   │   └── ...
│   ├── templates/                  # Django templates
│   │   └── demo.html               # Demo page frontend
│   └── README.md                   # Django setup guide
├── DJANGO_INTEGRATION_README.md    # Integration documentation
├── DEPLOYMENT_GUIDE.md             # Deployment instructions
└── README.md                       # This file
```

## 🔄 Integration Flow

1. **Upload Floor Plan**: User uploads floor plan image to Django demo page
2. **Process Image**: Django backend processes the image using CV algorithms
3. **Generate DXF**: System generates DXF floor plan with detected walls and spaces
4. **Open AI Editor**: User clicks "Generate with AI" button
5. **Auto-load DXF**: Flask AI Dashboard opens with the generated DXF file auto-loaded
6. **Edit Layout**: User can drag-drop fixtures, add furniture, and edit the layout
7. **Export**: Final layout can be exported as DXF or JSON

## 🔧 Configuration

### Django Backend (Port 8001)

Edit `django_backend/.env`:
```env
DB_NAME=lenskart_db
DB_USER=lenskart_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key
DEBUG=True
```

### Flask Frontend (Port 5000)

Edit `app.py` if needed to change:
- Port number
- Upload directory
- CORS settings

## 🧪 Testing the Integration

1. Start both servers (Django on 8001, Flask on 5000)
2. Go to http://localhost:8001/demo/
3. Upload a floor plan image
4. Wait for processing to complete
5. Click "Generate with AI" button
6. Verify Flask canvas opens with DXF loaded automatically

## 📚 API Endpoints

### Django Backend

**Demo APIs:**
- `GET /demo/` - Demo page frontend
- `GET /api/demo/projects/` - List demo projects
- `POST /api/demo/process/` - Process floor plan

**Main APIs:**
- `POST /api/app1/process-floorplan/{file_id}/` - Process uploaded floor plan
- `GET /api/app1/get-layout/{file_id}/` - Get generated layout

### Flask Frontend

- `GET /` - Landing page
- `GET /canvas` - Canvas editor
- `POST /upload` - Upload DXF file
- `POST /upload-from-url` - Auto-load DXF from URL (used by Django)
- `POST /generate-fixtures` - AI fixture generation

## 🛠️ Development

### Flask App Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run with debug mode
python3 app.py
```

### Django Backend Development

```bash
cd django_backend

# Run migrations after model changes
python3 manage.py makemigrations
python3 manage.py migrate

# Run tests
python3 manage.py test

# Collect static files for production
python3 manage.py collectstatic
```

## 🚢 Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

### Quick Deployment Checklist

- [ ] Set `DEBUG=False` in Django settings
- [ ] Configure production database
- [ ] Set secure `SECRET_KEY`
- [ ] Configure CORS for production domains
- [ ] Set up Nginx reverse proxy
- [ ] Configure SSL certificates
- [ ] Set up systemd services for auto-start

## 🔐 Security

- Django uses JWT authentication for API endpoints
- CORS is configured to allow communication between ports
- Uploaded files are validated for type and size
- SQL injection protection via Django ORM
- XSS protection enabled in Django settings

## 🐛 Troubleshooting

### Django won't start
```bash
# Check PostgreSQL is running
sudo service postgresql start

# Check port 8001 is free
lsof -i :8001
```

### Flask CORS errors
```bash
# Ensure flask-cors is installed
pip install flask-cors

# Verify CORS is enabled in app.py
```

### Database connection errors
```bash
# Verify PostgreSQL credentials in .env
# Test connection
sudo -u postgres psql lenskart_db
```

### Integration not working
1. Verify both servers are running
2. Check Django is on port 8001 (not 8000)
3. Check Flask is on port 5000
4. Verify CORS is enabled in Flask app
5. Check browser console for errors

## 📝 License

[Your License Here]

## 👥 Contributors

- [Your Name/Team]

## 📧 Support

For issues and questions:
- Create an issue on GitHub
- Contact: [your email]

---

## Additional Documentation

- [DJANGO_INTEGRATION_README.md](DJANGO_INTEGRATION_README.md) - Detailed integration guide
- [django_backend/README.md](django_backend/README.md) - Django setup instructions
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment guide
- [REQUIRED_FILES_CHECKLIST.md](REQUIRED_FILES_CHECKLIST.md) - Complete file inventory