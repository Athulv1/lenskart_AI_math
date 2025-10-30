# Django Backend for AI_DASHBOARD Integration

This folder contains the essential Django backend files needed to run the Lenskart floor planning application that integrates with the Flask AI_DASHBOARD.

## Setup Instructions

### 1. Install Dependencies

```bash
cd django_backend
pip install -r requirements.txt
```

### 2. Configure PostgreSQL

```bash
# Start PostgreSQL
sudo service postgresql start

# Create database (if not exists)
sudo -u postgres psql
CREATE DATABASE lenskart_db;
CREATE USER lenskart_user WITH PASSWORD 'your_password';
ALTER ROLE lenskart_user SET client_encoding TO 'utf8';
ALTER ROLE lenskart_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE lenskart_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE lenskart_db TO lenskart_user;
\q
```

### 3. Configure Environment

Edit `.env` file and update:
```
DB_NAME=lenskart_db
DB_USER=lenskart_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 4. Run Migrations

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python3 manage.py createsuperuser
```

### 6. Run Django Server

```bash
python3 manage.py runserver 8001
```

**Important:** Django must run on port **8001** (not 8000) for integration to work.

## Integration with Flask AI_DASHBOARD

1. Start Django backend: `python3 manage.py runserver 8001`
2. Start Flask app: `cd .. && python3 app.py`
3. Access demo page: `http://localhost:8001/demo/`
4. Click "Generate with AI" to open Flask canvas with auto-loaded DXF

## Files Included

### Core Django Files
- `manage.py` - Django management script
- `requirements.txt` - Python dependencies
- `.env` - Environment configuration

### Application Files
- `app/` - Main application code
  - `demo_views.py` - API views for demo functionality
  - `models.py` - Database models
  - `serializers.py` - Django Ninja serializers
  - Other app files

### Backend Configuration
- `backend/` - Django project settings
  - `settings.py` - Project settings
  - `urls.py` - URL routing (includes demo routes)
  - `wsgi.py` - WSGI configuration
  - `asgi.py` - ASGI configuration

### Templates
- `templates/demo.html` - Demo frontend page

## API Endpoints

### Demo APIs
- `GET /demo/` - Demo page frontend
- `GET /api/demo/projects/` - Get list of demo projects
- `POST /api/demo/process/` - Process floor plan and generate DXF

### Main APIs
- `POST /api/app1/process-floorplan/{file_id}/` - Process uploaded floor plan
- Other APIs as defined in app/demo_views.py

## Excluded Files (Not Required)

The following are NOT included as they're not needed for core functionality:
- `node_modules/` - Frontend dependencies (use CDN instead)
- `media/` - Generated files (created at runtime)
- `staticfiles/` - Collected static files
- `__pycache__/` - Python cache
- `.git/` - Git history
- Large test data files
- Migration history files

## Troubleshooting

### PostgreSQL Connection Error
```bash
sudo service postgresql start
```

### Port Already in Use
```bash
# Kill existing Django process
pkill -f "manage.py runserver"
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### CORS Issues
Ensure Flask app has `flask-cors` installed and CORS is enabled in `app.py`

## Integration Flow

1. User uploads floor plan image to Django demo page
2. Django processes image and generates DXF file
3. User clicks "Generate with AI" button
4. Django opens Flask AI_DASHBOARD with `?autoload=DXF_URL`
5. Flask fetches DXF from Django and loads it in canvas
6. User can edit fixtures in Flask canvas editor
