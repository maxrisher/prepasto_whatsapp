"""
Django settings for hummus_project project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = False

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = [os.getenv('RAILWAY_PUBLIC_DOMAIN'),
                 'prepasto.com',
                 'www.prepasto.com',
                 'prepastowhatsapp-production.up.railway.app',]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main_app',
    'whatsapp_bot',
    'custom_users',
    'tailwind',
    'theme',
    'django_browser_reload',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = 'hummus_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], #custom destination -- also look in the base directory for a templates folder
        'APP_DIRS': True, #Look for templates within each app's 'templates' dir
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

WSGI_APPLICATION = 'hummus_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Denver'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/' # This is the path to static files that Django will look for, when searching our project

STATIC_ROOT = BASE_DIR / 'staticfiles' # We create a folder in which to put all of our static files from all our different apps
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' # This reduces the size of the static files when they are served (this is more efficient).

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers':{
        'console': {
            # The level at which things get printed to the console
            'level': os.getenv('DJANGO_HANDLER_LEVEL', 'INFO'),
            'class': 'logging.StreamHandler'
        }
    },
    'loggers':{
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'whatsapp_bot': {
            'handlers': ['console'],
            'level': 'DEBUG',
            # this means that these logs will not get sent to parent loggers (ie. django)
            'propagate': False,
        },
        'main_app': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}

AUTH_USER_MODEL = 'custom_users.CustomUser'

CSRF_TRUSTED_ORIGINS = ["https://"+os.getenv('RAILWAY_PUBLIC_DOMAIN')]

# Checks for the ssl redirect setting. Defaults to enforcing SSL. 
SECURE_SSL_REDIRECT = os.getenv('DJANGO_SECURE_SSL_REDIRECT', 'True') == 'True'

# Railway forces https already. Trust headers from the reverse proxy.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

#Constants for the whatsapp buttons we send to users
MEAL_DELETE_BUTTON_TEXT = 'DELETE this meal.'
CONFIRM_TIMEZONE_BUTTON_ID_PREFIX = 'CONFIRM_TZ'
CANCEL_TIMEZONE_BUTTON_ID = 'CANCEL_TZ'

#How we record messages sent by us in the db
WHATSAPP_BOT_WHATSAPP_WA_ID = "14153476103"

#Register the new tailwind app
TAILWIND_APP_NAME = 'theme'

#For tailwind
INTERNAL_IPS = [
    "127.0.0.1",
]