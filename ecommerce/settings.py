import os
from importlib.util import find_spec
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'dev-secret-change-me'

DEBUG = True

ALLOWED_HOSTS = ["*"]

HAS_WHITENOISE = find_spec('whitenoise') is not None
HAS_CRISPY_FORMS = find_spec('crispy_forms') is not None
HAS_ALLAUTH = find_spec('allauth') is not None


INSTALLED_APPS = [
    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'shop',
]

if HAS_ALLAUTH:
    INSTALLED_APPS += [
        'django.contrib.sites',
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        'allauth.socialaccount.providers.google',
        'allauth.socialaccount.providers.facebook',
    ]

if HAS_CRISPY_FORMS:
    INSTALLED_APPS.append('crispy_forms')


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if HAS_WHITENOISE:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

if HAS_ALLAUTH:
    MIDDLEWARE.append('allauth.account.middleware.AccountMiddleware')


ROOT_URLCONF = 'ecommerce.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',

                # REQUIRED FOR ALLAUTH
                'django.template.context_processors.request',

                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'ecommerce.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_PASSWORD_VALIDATORS = []


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# ================= STATIC FILES =================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'shop' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'


# ================= MEDIA FILES =================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


CRISPY_TEMPLATE_PACK = 'bootstrap4'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ================== ALLAUTH SETTINGS ==================
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

if HAS_ALLAUTH:
    SITE_ID = 1
    AUTHENTICATION_BACKENDS.append(
        'allauth.account.auth_backends.AuthenticationBackend'
    )

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USERNAME_REQUIRED = False

# IMPORTANT (otherwise allauth may block login)
ACCOUNT_EMAIL_VERIFICATION = "none"

SOCIAL_LOGIN_ENABLED = HAS_ALLAUTH


# ================= UPI SETTINGS =================
GPAY_UPI_ID = "tharunkumar2124@okhdfcbank"
PHONEPE_UPI_ID = "6382040121@ibl"
PAYTM_UPI_ID = "8838897256@pthdfc"
