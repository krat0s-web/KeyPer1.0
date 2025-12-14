"""
Configuration Django pour la production
========================================

Ce fichier contient les paramètres de production pour KeyPer.
Pour l'utiliser, définissez la variable d'environnement DJANGO_SETTINGS_MODULE :
export DJANGO_SETTINGS_MODULE=gestion_taches_project.settings_production

OU utilisez-le directement dans votre serveur WSGI :
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_taches_project.settings_production')
"""

from .settings import *
import os

# === SÉCURITÉ ===
# IMPORTANT : Ne jamais commiter ce fichier avec des valeurs réelles en production !

# Clé secrète - DOIT être changée en production !
# Générer une nouvelle clé avec : python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY = os.environ.get('SECRET_KEY', 'CHANGEZ-MOI-EN-PRODUCTION-GÉNÉREZ-UNE-CLÉ-SÉCURISÉE')

# Désactiver le mode debug en production
DEBUG = False

# Liste des domaines autorisés (remplacer par votre domaine)
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# === SÉCURITÉ HTTPS ===
# Activer ces paramètres si vous utilisez HTTPS (recommandé)
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False').lower() == 'true'
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'False').lower() == 'true'
SECURE_HSTS_PRELOAD = os.environ.get('SECURE_HSTS_PRELOAD', 'False').lower() == 'true'

# === BASE DE DONNÉES ===
# Configuration pour PostgreSQL (recommandé en production)
import dj_database_url

# Essayer DATABASE_URL d'abord (Render, Heroku)
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600
        )
    }
else:
    # Sinon, utiliser les variables individuelles
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'keyper_db'),
            'USER': os.environ.get('DB_USER', 'keyper_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'OPTIONS': {
                'connect_timeout': 10,
            }
        }
    }

# === FICHIERS STATIQUES ET MÉDIAS ===
# Les fichiers statiques doivent être collectés avec : python manage.py collectstatic
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Fichiers médias (photos, uploads)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# === CACHE ===
# Configuration du cache pour la production (Redis recommandé)
# Pour utiliser Redis, installez django-redis : pip install django-redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Alternative avec Redis (décommentez si vous utilisez Redis)
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }

# === EMAIL ===
# Configuration email pour la production (SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'KeyPer <noreply@keyper.com>')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'KeyPer <noreply@keyper.com>')

# === LOGGING ===
# Configuration des logs pour la production
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
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'maison_app': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Créer le dossier logs s'il n'existe pas
import os
logs_dir = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# === API KEYS ===
# Clés API pour les services externes
OPENWEATHERMAP_API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY', '')
OPENWEATHERMAP_URL = os.environ.get('OPENWEATHERMAP_URL', 'http://api.openweathermap.org/data/2.5/weather')

# === PERFORMANCE ===
# Désactiver les fonctionnalités de développement
if DEBUG:
    # Si DEBUG est True, quelque chose ne va pas
    raise ValueError("DEBUG ne doit pas être True en production !")

# === SESSION ===
# Configuration des sessions
SESSION_COOKIE_AGE = 86400  # 24 heures
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

