import environ

env = environ.Env()
environ.Env.read_env()

# REST_FRAMEWORK = {
#     "DEFAULT_AUTHENTICATION_CLASSES": [
#         "rest_framework_simplejwt.authentication.JWTAuthentication",
#     ],
#     "EXCEPTION_HANDLER": "geosmBackend.custom_exception_handler.custom_exception_handler",
# }

# DRF
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "EXCEPTION_HANDLER": "geosmBackend.custom_exception_handler.custom_exception_handler",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "TOKEN_MODEL": None,
}

# Swagger settings
SWAGGER_SETTINGS = {
    "DEFAULT_INFO": "geosmBackend.urls.swagger_api_info",
    # Renseigner plus tard les bonnes urls
    "LOGIN_URL": "/auth/jwt/create/",
    "LOGOUT_URL": "/auth/users/logout/",
    "USE_SESSION_AUTH": True,
    "REFETCH_SCHEMA_WITH_AUTH": True,
    "REFETCH_SCHEMA_ON_LOGOUT": True,
    "enabled_methods": ["get", "post", "put", "delete"],
    "SECURITY_DEFINITIONS": {
        "Basic": {"type": "basic"},
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"},
    },
    #    'DEFAULT_API_URL': 'https://tiles.dataosm.info/',
    "REFETCH_SCHEMA_WITH_AUTH": True,
    # Document que le swagger doit charger
    #'SPEC_URL': 'https://tiles.dataosm.info/',
}

REDOC_SETTINGS = {
    "LAZY_RENDERING": False,
}

DJOSER = {
    "SERIALIZERS": {"user_create": "account.serializers.UserRegistrationSerializer"}
}
