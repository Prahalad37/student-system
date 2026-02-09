"""
Django settings for mysite project.
UPDATED FOR: Prahlad Academy ERP v2.0 (Phase 2 + PWA Fix)
"""
import environ
import os
import socket
from pathlib import Path

# Initialise environ
env = environ.Env()
environ.Env.read_env()  # Read .env file

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = env.bool('DEBUG', default=False)
DEBUG = True
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])


# --- APPLICATION DEFINITION ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'debug_toolbar',
    'django.contrib.staticfiles',
    
    # ✅ Phase 2 Apps (Restored)
    'rest_framework',
    'corsheaders',
    'pwa',
    
    # Custom Apps
    'members',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',  # MUST BE FIRST for Debug Toolbar
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # ✅ CORS Middleware (Must be here for Mobile App)
    'corsheaders.middleware.CorsMiddleware',
    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # ✅ Tenant Middleware (Sets request.school and request.role)
    'members.middleware.tenant.TenantMiddleware',
    
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

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

WSGI_APPLICATION = 'mysite.wsgi.application'


# --- DATABASE ---
DATABASES = {
    'default': env.db(),
}


# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- STATIC & MEDIA FILES ---

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# --- AUTHENTICATION & LOGIN ---

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"
 

CSRF_TRUSTED_ORIGINS = ['https://prahalad.pythonanywhere.com', 'https://prahaladpal.pythonanywhere.com']


# --- ✅ PWA CONFIGURATION (FIXED PATH) ---
PWA_APP_NAME = 'Prahlad Academy'
PWA_APP_DESCRIPTION = "Smart School ERP System"
PWA_APP_THEME_COLOR = '#4e73df'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_START_URL = '/'
PWA_APP_ICONS = [
    {
        # ✅ Updated path to match your folder: static/assets/img/icon-160.png
        'src': '/static/assets/img/icon-160.png',
        'sizes': '160x160'
    }
]

# --- REST FRAMEWORK CONFIG ---
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# --- CORS CONFIG ---
CORS_ALLOW_ALL_ORIGINS = True

# --- CELERY SETTINGS ---
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Media Files (Uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- DEBUG TOOLBAR CONFIGURATION (Add this to the bottom) ---
if DEBUG:
    import mimetypes
    
    # 1. Fix MIME types so the browser accepts the JS
    mimetypes.add_type("application/javascript", ".js", True)

    # 2. Add standard localhost IPs
    INTERNAL_IPS = ["127.0.0.1", "localhost", "0.0.0.0"]

    # 3. Force the toolbar to show (Bypasses Docker IP issues)
    def show_toolbar(request):
        return True

    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': show_toolbar,
        'INSERT_BEFORE': '</body>',
    }