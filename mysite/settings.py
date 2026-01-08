"""
Django settings for mysite project.
UPDATED FOR: Prahlad Academy ERP v2.0
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# --- SECURITY SETTINGS ---

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-od3$^1(250-5m5t#ep^kr&%ch%tt$do6j3@tfn@#xers2(ppkh'

# SECURITY WARNING: don't run with debug turned on in production!
# Development ke liye True rakho, Live server par False karna
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
    
    # Custom Apps
    'members',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Ye batata hai ki naya SB Admin Template kahan rakha hai
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Jab live server par 'collectstatic' chalate hain, tab files yahan jati hain
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (Student Photos etc.)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# --- AUTHENTICATION & LOGIN ---

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'              # Agar login nahi hai to yahan bhejo
LOGIN_REDIRECT_URL = 'index'     # Login hone ke baad Dashboard par bhejo
LOGOUT_REDIRECT_URL = 'login'    # Logout hone ke baad Login page par bhejo

# Trust settings for PythonAnywhere
CSRF_TRUSTED_ORIGINS = ['https://prahalad.pythonanywhere.com', 'https://prahaladpal.pythonanywhere.com']