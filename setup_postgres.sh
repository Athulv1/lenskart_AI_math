#!/bin/bash

# A simple script to create the database and user for the Lenskart project.
# It reads the required values from your .env file.

# --- Configuration ---
# Load environment variables from the .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found. Please create it first."
    exit 1
fi

echo "--- PostgreSQL Setup for Lenskart Backend ---"
echo "This script will create the database and user based on your .env file."
echo ""
echo "Database Name:    $DB_NAME"
echo "Database User:    $DB_USER"
echo ""
read -p "Are you sure you want to continue? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Operation cancelled."
    exit 1
fi

# Execute the SQL commands
# The -c flag allows us to run a command and exit.
sudo -u postgres psql -c "CREATE ROLE \"$DB_USER\" WITH LOGIN PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "CREATE DATABASE \"$DB_NAME\" OWNER \"$DB_USER\";"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE \"$DB_NAME\" TO \"$DB_USER\";"

echo ""
echo "✅ PostgreSQL setup complete."
echo "You can now run 'python manage.py migrate'."