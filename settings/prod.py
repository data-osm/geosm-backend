from datetime import timedelta

import environ

from .base import *
from .highlight import *

env = environ.Env()
environ.Env.read_env()
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

FRONT_URL = "https://www.dataosm.info"
CORS_ALLOWED_ORIGINS = [
    "https://preprod.dataosm.info",
    FRONT_URL,
    "https://dataosm.info",
    "https://portail.dataosm.info",
    "http://portail.dataosm.info",
    "http://demo.openstreetmap.fr",
    "https://demo.openstreetmap.fr",
]
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "ws.dataosm.info"]

CONTACT_EMAIL = "team.osmdata@gmail.com"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True

CORS_ALLOW_CREDENTIALS = True

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": env("DATABASE_NAME"),
        "USER": env("DATABASE_USER"),
        "PASSWORD": env("DATABASE_PASS"),
        "HOST": "172.17.0.1",
        "PORT": "5432",
    },
    "datasud": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": env("DATABASE_DATASUD_NAME"),
        "USER": env("DATABASE_DATASUD_USER"),
        "PASSWORD": env("DATABASE_DATASUD_PASS"),
        "HOST": env("DATABASE_DATASUD_HOST"),
        "PORT": env("DATABASE_DATASUD_PORT"),
    },
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=180),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=190),
}

OSMDATA = {
    "project_qgis_path": os.path.join(BASE_DIR, "provider", "qgis", "project"),
    "qml_default_path": os.path.join(BASE_DIR, "provider", "qgis", "defaultQml"),
    "url_qgis_server_prefix": "",
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "geosmBackend", "debug.log"),
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "WARNING",
            "propagate": True,
        },
    },
}
