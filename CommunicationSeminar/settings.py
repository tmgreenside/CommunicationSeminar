"""
Django settings for CommunicationSeminar project.

Generated by 'django-admin startproject' using Django 1.11.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import logging

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'c7so+hqfe+a_9i9*##vgl!k-xb^)nin&o-ev*^t@ipq6y!wt!-'

# SECURITY WARNING: don't run with debug turned on in production!
LIVE = 'RDS_DB_NAME' in os.environ
DEBUG = False if LIVE else True

ADMINS = [('Zeke Hunter-Green', 'zekehuntergreen@gmail.com')]

ALLOWED_HOSTS = [
    'comsempython.us-east-2.elasticbeanstalk.com',
    'localhost',
    '.comsem.net',
]

# Application definition

INSTALLED_APPS = [
    'ComSemApp.apps.ComsemappConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_select2',
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

ROOT_URLCONF = 'CommunicationSeminar.urls'

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
                "ComSemApp.context_processors.user_info",
            ],
        },
    },
]

WSGI_APPLICATION = 'CommunicationSeminar.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {}

if LIVE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': 'localhost',
            'PORT': '3306',
            'NAME': 'CommunicationSeminarDjango',
            'USER': 'root',
            'PASSWORD': 'tempcbsql',
        }
    }



# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# where should the login form redirect to?
LOGIN_REDIRECT_URL = '/initiate_roles/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'efs')
MEDIA_URL = '/efs/'

if LIVE:
    EFS_DIR = '/efs/'
else:
    EFS_DIR = 'efs/'

# EMAIL
if LIVE:
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = 'ComSem <noreply@comsem.net>'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = 'app-messages'

# HTTPS
if LIVE:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        # Silence SuspiciousOperation.DisallowedHost exception ('Invalid
        # HTTP_HOST' header messages). Set the handler to 'null' so we don't
        # get those annoying emails.
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'level': 'CRITICAL',
            'propagate': False,
        },
    },
    'handlers': {
    'null': {
        'level': 'DEBUG',
        'class': 'logging.NullHandler',
    },
}
}
