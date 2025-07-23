import environ
import highlight_io
from highlight_io.integrations.django import DjangoIntegration

env = environ.Env()
environ.Env.read_env()

environment: str = env("ENVIRONMENT")

if environment.upper() == "PRODUCTION":
    H = highlight_io.H(
        "xdn33xle",
        integrations=[DjangoIntegration()],
        instrument_logging=True,
        service_name="osm-data-backend",
        service_version="git-sha",
        environment="production",
    )
