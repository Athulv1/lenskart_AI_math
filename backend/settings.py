import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-kqpvvj!t15!hi)flc%%m=wc--*ui@(66rpqdm%slj%2lpfk$^s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['13.201.224.32', 'lenskart.thinkneural.ai']



# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ninja',
    'app',
    'corsheaders'
]

JAZZMIN_SETTINGS = {
    "site_title": "Lenskart Admin",
    "site_header": "Lenskart Admin",
    "site_brand": "Lenskart",
    "welcome_sign": "Welcome to the Lenskart Admin",
    "copyright": "Lenskart",
}




MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'app.middleware.PayloadLoggerMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

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

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')




# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

FILE_UPLOAD_PERMISSIONS = 0o664
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 50 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024 # 20 MB (example)

LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'payload_formatter': { # <--- NEW FORMATTER FOR PAYLOADS (can be simple or verbose)
            'format': '{levelname} {asctime} {name} {message}', # Using {name} to show the logger name (payload_logger)
            'style': '{',
        },
    },

    'handlers': {
        'file_errors': { # Renamed from 'file' for clarity
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'django_errors.log'),
            'formatter': 'verbose',
        },
        'file_payload': { # <--- NEW HANDLER FOR PAYLOAD LOGS
            'level': 'INFO', # Set to INFO to capture the payload logs
            'class': 'logging.handlers.RotatingFileHandler', # Recommended for production to prevent log files from growing too large
            'filename': os.path.join(LOGS_DIR, 'django_payload.log'), # <--- NEW LOG FILE
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5, # Keep 5 backup files
            'formatter': 'payload_formatter', # Use the new formatter
        },
	'file_app': {  # NEW: General app logs
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'django_app.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': { # Adding a console handler for convenience during development/debugging
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },

    'loggers': {
        'django': {
            'handlers': ['console', 'file_errors'], # Added 'console'
            'level': 'INFO', # Changed to INFO to see more Django internal logs if needed
            'propagate': False, # Changed to False to prevent logs from propagating to root logger
        },
        'app': { # Your existing 'app' logger
            'handlers': ['console','file_app', 'file_errors'], # Added 'console'
            'level': 'INFO', # Changed to INFO for more detailed app logs
            'propagate': False, # Changed to False
        },
        'payload_logger': { # <--- NEW LOGGER FOR PAYLOAD LOGS (matches the name in middleware.py)
            'handlers': ['console', 'file_payload'], # Directs to the new payload log file AND console
            'level': 'INFO', # Set to INFO to capture payload logs
            'propagate': False, # Important: Set to False to prevent duplicate logging
        },
    },

    'root': { # Configure root logger to catch anything not handled by specific loggers
        'handlers': ['console', 'file_errors'], # Direct root logs to console and error file
        'level': 'WARNING', # Set a higher level for root to avoid too much noise
    },
}



NINJA_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    
    # We will use Django's built-in SECRET_KEY for signing
    'SIGNING_KEY': SECRET_KEY, 
    
    # Standard authorization header format: "Authorization: Bearer <token>"
    'AUTH_HEADER_TYPES': ('Bearer',),
}


try:
    from .local_settings import *
except ImportError:
    pass
