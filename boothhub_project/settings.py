"""
Django settings for boothhub_project.
BoothHub — Sistem Manajemen Booth F&B
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# KEAMANAN & DASAR
# ============================================================

# SECURITY WARNING: keep the secret key used in production secret!
# Ganti ini dengan key baru untuk production
SECRET_KEY = 'django-insecure-zq%s1r40l958easl3z+$$snaikyeg(@odboeme4(=620fk@q!&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Host yang diizinkan mengakses aplikasi
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']


# ============================================================
# APPLICATION DEFINITION
# ============================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'boothapp',  # App utama BoothHub
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

ROOT_URLCONF = 'boothhub_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Langsung arahkan ke folder templates di root project
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'boothhub_project.wsgi.application'


# ============================================================
# DATABASE
# ============================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Jika ingin pakai MySQL/MariaDB (opsional, uncomment dan sesuaikan):
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'boothhub_db',
#         'USER': 'root',
#         'PASSWORD': 'your_password',
#         'HOST': 'localhost',
#         'PORT': '3306',
#         'OPTIONS': {
#             'charset': 'utf8mb4',
#         }
#     }
# }


# ============================================================
# PASSWORD VALIDATION
# ============================================================

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


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = 'id-id'

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_TZ = True

# Format tanggal Indonesia
DATE_FORMAT = 'd F Y'
DATETIME_FORMAT = 'd F Y H:i'
SHORT_DATE_FORMAT = 'd/m/Y'


# ============================================================
# STATIC FILES & MEDIA
# ============================================================

# URL prefix untuk static files
STATIC_URL = 'static/'

# Folder tempat Django mengumpulkan static files saat collectstatic
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Folder tambahan untuk static files (CSS, JS custom)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files (upload user)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ============================================================
# AUTENTIKASI
# ============================================================

# URL redirect jika user belum login
LOGIN_URL = '/login/'

# URL redirect setelah login berhasil
LOGIN_REDIRECT_URL = '/'

# URL redirect setelah logout
LOGOUT_REDIRECT_URL = '/login/'


# ============================================================
# DEFAULT AUTO FIELD
# ============================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'