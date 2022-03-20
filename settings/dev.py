from .base import *
from datetime import timedelta

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'vr)rd0$p7@*j4-o5rzr!=l&^bwe$g_f51*dmtj6+!g4hoc%!p%'

FRONT_URL='http://localhost:4200'
CORS_ALLOWED_ORIGINS = [FRONT_URL]
ALLOWED_HOSTS=['localhost','127.0.0.1']
CONTACT_EMAIL=''

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': '5432',
    }
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=180),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=190),
}

OSMDATA = {
    'project_qgis_path':os.path.join(BASE_DIR, "provider","qgis","project"),
    'qml_default_path':os.path.join(BASE_DIR, "provider","qgis","defaultQml"),
    'url_qgis_server_prefix':'http://localhost:3000/ows/?map='
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, "geosmBackend",'debug.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}