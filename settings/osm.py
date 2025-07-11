import environ

env = environ.Env()
environ.Env.read_env()

OSM_CLIENT_ID = env("OSM_CLIENT_ID")
OSM_CLIENT_SECRET_ID = env("OSM_CLIENT_SECRET_ID")
OSM_REDIRECT_URL = env("OSM_REDIRECT_URL")

OSM_AUTHORIZATION_URL = "https://www.openstreetmap.org/oauth2/authorize"
TOKEN_URL = "https://www.openstreetmap.org/oauth2/token"
OSM_USER_DETAIL_URL = "https://api.openstreetmap.org/api/0.6/user/details"
