"""
Django settings for cadastro_asaas project.
"""
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'asaas_app',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
if DEBUG:
    # SQLite para desenvolvimento
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # PostgreSQL para produção
    DATABASES = {
        'default': {
            'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
            'NAME': config('DB_NAME', default='asaas_db'),
            'USER': config('DB_USER', default='asaas_user'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }

# Password validation
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
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# STATIC_URL é configurado acima com FORCE_SCRIPT_NAME
STATICFILES_DIRS = [BASE_DIR / 'static']

# Static files em produção
if not DEBUG:
    STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Asaas API Configuration
ASAAS_API_KEY = config('ASAAS_API_KEY', default='')
ASAAS_API_URL = config('ASAAS_API_URL', default='https://sandbox.asaas.com/api/v3')

# WhatsApp API Configuration
# Suporta tanto EVOLUTION_* quanto WHATSAPP_* para compatibilidade
WHATSAPP_API_URL = config('EVOLUTION_API_URL', config('WHATSAPP_API_URL', default=''))
WHATSAPP_API_KEY = config('EVOLUTION_API_KEY', config('WHATSAPP_API_KEY', default=''))
WHATSAPP_INSTANCE_ID = config('EVOLUTION_INSTANCE_ID', config('WHATSAPP_INSTANCE_ID', default=''))
WHATSAPP_TOKEN = config('WHATSAPP_TOKEN', default='')
WHATSAPP_PROVIDER = config('WHATSAPP_PROVIDER', default='evolution')  # evolution, whatsapp_business, ou custom
# Lista de números para receber notificações/testes (separados por vírgula)
WHATSAPP_NUMBERS = config('WHATSAPP_NUMBERS', default='').split(',') if config('WHATSAPP_NUMBERS', default='') else []

# Subdiretório (para deploy em http://IP/asaas/)
FORCE_SCRIPT_NAME = config('FORCE_SCRIPT_NAME', default='')
if FORCE_SCRIPT_NAME:
    STATIC_URL = FORCE_SCRIPT_NAME + '/static/'
    # Configurar SESSION_COOKIE_PATH para subdiretório
    SESSION_COOKIE_PATH = FORCE_SCRIPT_NAME + '/'
    CSRF_COOKIE_PATH = FORCE_SCRIPT_NAME + '/'
else:
    STATIC_URL = 'static/'
    SESSION_COOKIE_PATH = '/'
    CSRF_COOKIE_PATH = '/'

# Login/Logout URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

# Security Settings
# IMPORTANTE: Configure estas variáveis no .env para produção!

# Session Security
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)  # True em produção com HTTPS
SESSION_COOKIE_HTTPONLY = True  # Previne acesso via JavaScript
SESSION_COOKIE_SAMESITE = 'Lax'  # Proteção contra CSRF
SESSION_COOKIE_AGE = 3600 * 8  # 8 horas

# CSRF Protection
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)  # True em produção com HTTPS
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# CSRF Trusted Origins (importante para produção com IP ou domínio específico)
CSRF_TRUSTED_ORIGINS_STR = config('CSRF_TRUSTED_ORIGINS', default='')
if CSRF_TRUSTED_ORIGINS_STR:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS_STR.split(',')]
else:
    CSRF_TRUSTED_ORIGINS = []

# Security Headers
SECURE_BROWSER_XSS_FILTER = True  # Proteção XSS
SECURE_CONTENT_TYPE_NOSNIFF = True  # Previne MIME-sniffing
X_FRAME_OPTIONS = 'DENY'  # Previne clickjacking

# HTTPS/SSL (ativar em produção)
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)  # True em produção
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)  # 31536000 em produção (1 ano)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=False, cast=bool)

# Allowed Hosts (configure no .env para produção)
if not DEBUG:
    # Em produção, especifique os hosts permitidos no .env
    # Ex: ALLOWED_HOSTS=seudominio.com,www.seudominio.com
    ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')
    
# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'asaas_app': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

