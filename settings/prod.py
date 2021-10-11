from .base import *
from datetime import timedelta

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


CORS_ALLOWED_ORIGINS = ['http://preprod.dataosm.info','https://preprod.dataosm.info']
ALLOWED_HOSTS=['localhost','127.0.0.1']

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
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': '5432',
    }
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=180),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=190)
}

OSMDATA = {
    'project_qgis_path':os.path.join(BASE_DIR, "provider","qgis","project"),
    'qml_default_path':os.path.join(BASE_DIR, "provider","qgis","defaultQml"),
    'url_qgis_server_prefix':''
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