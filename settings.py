"""
Django settings for mysite project.
UPDATED FOR: Prahlad Academy ERP v2.0 (Phase 2 + PWA Fix)
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# --- SECURITY SETTINGS ---

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-od3$^1(250-5m5t#ep^kr&%ch%tt$do6j3@tfn@#xers2(ppkh'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'prahalad.pythonanywhere.com', 'prahaladpal.pythonanywhere.com']


# --- APPLICATION DEFINITION ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # ✅ Phase 2 Apps (Restored)
    'rest_framework',
    'corsheaders',
    'pwa',
    
    # Custom Apps
    'members',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # ✅ CORS Middleware (Must be here for Mobile App)
    'corsheaders.middleware.CorsMiddleware',
    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
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
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
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

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# --- AUTHENTICATION & LOGIN ---

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'              
LOGIN_REDIRECT_URL = 'index'     
LOGOUT_REDIRECT_URL = 'login'    

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