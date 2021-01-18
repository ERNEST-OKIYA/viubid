"""
Django settings for QuickBid project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_DATA_DIR = os.path.join(BASE_DIR, '.local-data')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&))e+k%o7ipics%i4lty8-in2r1*uj+182y_0cj-2%8mn718ua'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*',]

GRAPPELLI_ADMIN_TITLE = 'Quick Bid'


# Application definition

INSTALLED_APPS = [
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bids',
    'products',
    'winners',
    'QuickBid',
    'factory',
    'messaging',
    'wallets',
    'payments',
    'users',
    'admin_portal',
    'ussd',
    'flex.ussd',
    'django.contrib.humanize',
    'jobs',
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

ROOT_URLCONF = 'QuickBid.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates'),],
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

WSGI_APPLICATION = 'QuickBid.wsgi.application'

AUTH_USER_MODEL = 'users.User'

STATICFILES_DIRS = [
os.path.join(BASE_DIR,'static'),
]
# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
# STATIC_ROOT = os.path.join(BASE_DIR, 'static/') 
# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] [{levelname}] ({module}): {message}",
            "style": "{",
        },
        "simple": {
            # 'format': '[{asctime}] {levelname}: {module}: {message}',
            "format": "[{asctime}] [{levelname}] ({module}): {message}",
            "style": "{",
        },
    },
    "filters": {"require_debug_true": {"()": "django.utils.log.RequireDebugTrue"}},
    "handlers": {
        "console": {
            "level": "DEBUG",
            # 'filters': ['require_debug_true'],
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            # 'filters': ['special']
        },
    },
    "loggers": {
        "": {"handlers": ["console"], "level": "DEBUG", "propagate": True},
		"django": {"handlers": ["console"], "level": "INFO", "propagate": False},		

	}
}


CACHES = {
	"default": {
		"BACKEND": "django_redis.cache.RedisCache",
		"LOCATION": "redis://127.0.0.1:6379/1",
		"OPTIONS": {
			"CLIENT_CLASS": "django_redis.client.DefaultClient",
		},
		"KEY_PREFIX" : "QB_CACHE"
	}
}

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'Africa/Nairobi'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True

USE_L10N = True

USE_TZ = True

BID_TICKET_COST = 20
USSD = dict(
	URLS = (
		r'^/ussd/$',
		dict(
			path=r'^/ussd/gh/mtn/$',
			methods=('POST',)
		)
	),
	SESSION_TIMEOUT = 120,
	SCREEN_STATE_TIMEOUT = 120,
	INITIAL_SCREEN = 'p8.initial',
	MAX_PAGE_LENGTH=150
)
VARIABLES={'CONSUMER_KEY':'Ylg9fzpD8E57tUf7fJFf8BRX7ReBTlKO',
		   'CONSUMER_SECRET':'Xaplj15j2dppGDIw',
		   'BUSINESS_SHORTCODE':'4032353',
           'Timestamp':'20190228132847',
		   'DEFAULTCALLBACKURL':'https://ipn.quickbid.co.ke:7024/ipn/checkout/response/',
		   'PASSWORD':'NDAzMjM1M2E1MTFhZWU3ZGI0YzVkY2QzNGEwYjJkNjI3Njc5ZDQ2YTg3ZjkxMmMyYjY1YzkxZTkzODQ2ZDg0MzdhMzNkMmQyMDE5MDIyODEzMjg0Nw==',
		   'PAY_URL':'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
		   'TOKEN_URL':'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'}
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

LOGOUT_REDIRECT_URL='/login/'
LOGIN_REDIRECT_URL = '/mgr-tools/dashboard'
LOGIN_URL='/login/'

USSDADVIDE = 'Dial *229*99# to resolve your Bid'
USSD = dict(
	URLS = (
		r'^/ussd/$',
		dict(
			path=r'^/ussd/gh/mtn/$',
			methods=('POST',)
		)
	),
	SESSION_TIMEOUT = 120,
	SCREEN_STATE_TIMEOUT = 120,
	INITIAL_SCREEN = 'sm.initial',
	MAX_PAGE_LENGTH=150
)
try:
    from .local_settings import *
except:
    pass



