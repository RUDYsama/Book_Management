"""
Django settings for Book_Management project.
Updated for Lab 9.5 (RBAC), Lab 9.6 (Environment Variables), and Lab 9.7 (Production Deployment).
"""

import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ========================================================
# Lab 9.6: Load Environment Variables from .env file
# ========================================================
env_file = BASE_DIR / '.env'
if env_file.exists():
    try:
        import dotenv
        dotenv.load_dotenv(env_file)
    except ImportError:
        # Fallback built-in parser when python-dotenv is not installed
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        os.environ.setdefault(k.strip(), v.strip())
        except Exception as e:
            print(f"[ENV NOTICE] Error loading .env: {e}")


# ========================================================
# Core Django Settings (Configured via Environment Variables)
# ========================================================
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-!(rp_*0j47(0pi6a#proix8+5ns&c_k!=m2!8sgzq_^*tp0fyi'
)

DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')

allowed_hosts_raw = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0,*')
ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_raw.split(',') if h.strip()]


# ========================================================
# Application definition
# ========================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'Book_Management',
]

# Lab 9.7: Add corsheaders if installed
try:
    import corsheaders
    INSTALLED_APPS.insert(INSTALLED_APPS.index('rest_framework'), 'corsheaders')
except ImportError:
    pass

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Lab 9.7: Add CorsMiddleware and WhiteNoise
try:
    import corsheaders
    MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')
except ImportError:
    pass

try:
    import whitenoise
    sec_idx = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
    MIDDLEWARE.insert(sec_idx + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')
except (ImportError, ValueError):
    pass

ROOT_URLCONF = 'Book_Management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Book_Management.wsgi.application'


# ========================================================
# Database Configuration (Lab 9.6 & 9.7)
# - Local Development: SQLite (default when DB_HOST is empty)
# - Cloud Production (Aiven MySQL): Active when DB_HOST is provided
# ========================================================
db_host = os.environ.get('DB_HOST', '').strip()
if db_host:
    # Production Cloud Database (e.g. Aiven MySQL)
    ssl_options = {}
    if os.environ.get('DB_SSL_REQUIRED', 'false').lower() == 'true':
        ca_path = BASE_DIR / 'aiven_ca.pem'
        if ca_path.exists():
            ssl_options = {'ssl': {'ca': str(ca_path)}}
        else:
            ssl_options = {'ssl': {'ssl': True}}

    DATABASES = {
        'default': {
            'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.mysql'),
            'NAME': os.environ.get('DB_NAME', 'bookstore_db'),
            'USER': os.environ.get('DB_USER', 'avnadmin'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': db_host,
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': ssl_options,
        }
    }
else:
    # Local Development Database (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / os.environ.get('DB_NAME', 'db.sqlite3'),
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'


# ========================================================
# Email Service Configuration (Lab 9.6: Read from .env)
# ========================================================
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
        'OPTIONS': {
            'host': os.environ.get('EMAIL_HOST', 'smtp.gmail.com'),
            'port': int(os.environ.get('EMAIL_PORT', 587)),
            'username': os.environ.get('EMAIL_HOST_USER', 'rtaxdt@gmail.com'),
            'password': os.environ.get('EMAIL_HOST_PASSWORD', 'oirjaxwfzkfxysik'),
            'use_tls': os.environ.get('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 't'),
            'use_ssl': False,
            'timeout': 15,
        },
    },
}

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Book Store <rtaxdt@gmail.com>')


# ========================================================
# REST Framework & JWT Configuration (Lab 9.4 - 9.6)
# ========================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'Book_Management.authentication.CustomJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'EXCEPTION_HANDLER': 'Book_Management.exceptions.custom_exception_handler',
}

access_lifetime_minutes = int(os.environ.get('ACCESS_TOKEN_LIFETIME_MINUTES', 60))
refresh_lifetime_days = int(os.environ.get('REFRESH_TOKEN_LIFETIME_DAYS', 7))

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=access_lifetime_minutes),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=refresh_lifetime_days),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'SIGNING_KEY': os.environ.get('JWT_SECRET', 'my_bookstore_secret'),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'id',
}


# ========================================================
# CORS Configuration (Lab 9.6 & Lab 9.7 for Vercel Frontend)
# ========================================================
CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL', 'False').lower() in ('true', '1')

cors_raw = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000'
)
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_raw.split(',') if origin.strip()]

# Add FRONTEND_URL dynamically if specified
frontend_url = os.environ.get('FRONTEND_URL', '').strip()
if frontend_url and frontend_url not in CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS.append(frontend_url)

CORS_ALLOW_CREDENTIALS = True
