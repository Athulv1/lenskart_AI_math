#!/bin/bash
# Quick activation script for Django environment

echo "Activating Django environment..."
cd /home/rasheeque/Lenskart-Ai
source env_django/bin/activate

echo "✓ Environment activated!"
echo ""
echo "Available commands:"
echo "  python manage.py runserver        - Start Django development server"
echo "  python manage.py runserver 8001   - Start on port 8001"
echo "  python manage.py migrate          - Run database migrations"
echo "  python manage.py createsuperuser  - Create admin user"
echo "  python manage.py test             - Run tests"
echo "  deactivate                         - Exit virtual environment"
echo ""
echo "To start the server, run:"
echo "  python manage.py runserver 8001"
