# Lenskart Backend Project

This is the Django backend server for the Lenskart floor planning and project management application. It provides a RESTful API for the mobile clients and a Django Admin interface for management.

---

## Local Development Setup

These instructions will guide you through setting up the project for local development on a macOS or Linux machine.

### Prerequisites

- Python 3.11+
- PostgreSQL (running locally or accessible on the network)
- Git

### 1. Clone the Repository

Clone the project from GitHub to your local machine.

```bash
git clone https://github.com/ThinkNeuralAi/lenskart_backend.git
cd lenskart_backend
2. Set Up the Virtual Environment
It is crucial to use a virtual environment to manage project dependencies.

# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
(Your terminal prompt should now start with (venv))

3. Install Dependencies
Install all required Python packages from the requirements.txt file.

pip install -r requirements.txt

4. Configure Environment Variables
The project uses a .env file to manage secret keys and database settings.
Create a new file named .env in the root of the project directory.
Copy the following content into it and update the values to match your local database setup.

5. Create the `.env` file:** Copy the example file `env.example` (if you have one) or create `.env` from scratch. Fill in your local PostgreSQL details.
Dotenv
# .env file

# --- Database Settings ---
DB_NAME=lenskart_db
DB_USER=your_local_postgres_user
DB_PASSWORD=your_local_postgres_password
DB_HOST=localhost
DB_PORT=5432

6. The project uses a `.env` file for settings and a `local_settings.py` for development-specific overrides.

**Create the `local_settings.py` file:** In the `backend/` directory, create a file named `local_settings.py` with the following content. This file is ignored by Git and is for your machine only.
    ```python
    # backend/local_settings.py
    DEBUG = True
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
    ```

7.  **Set up PostgreSQL:** Run the automated setup script. This will read your `.env` file and create the database and user for you. You will be prompted for your system's `sudo` password.
    ```bash
    ./setup_postgres.sh
    ```

8. Run Database Migrations
This command will create the necessary tables in your local database.
code
python manage.py migrate

9. Create a Superuser
You will need a superuser account to access the Django Admin panel.
python manage.py createsuperuser
Follow the prompts to create a username, email, and password.

10. Run the Development Server
You are now ready to run the project.
code
Bash
python manage.py runserver
The server will start, typically at http://127.0.0.1:8000/.
The Django Admin will be available at http://127.0.0.1:8000/admin/.
The API documentation will be available at http://127.0.0.1:8000/api/app1/docs.




Common Django Commands
Here are some useful commands to run from your activated virtual environment.
Run the development server:

python manage.py runserver


Run database migrations:
(Run this after pulling changes that modify the models.py file)

python manage.py migrate

Create new migration files:
(Run this after you have modified a models.py file)

python manage.py makemigrations


Open the Django shell:
(An interactive environment for testing queries)

python manage.py shell
Run custom management commands:
(For example, the project cleanup script)

python manage.py cleanup_old_projects --dry-run

