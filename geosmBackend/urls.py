"""geosmBackend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi

# from rest_framework.authtoken.views import obtain_auth_token
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from account.urls import osmUrlPatterns
from account.urls import urlpatterns as account_urlpatterns
from account.views import CsrfTokenView, GetCurrentUserView, LoginView, LogoutView

swagger_api_info = openapi.Info(
    title="OSMdata API",
    default_version="v1",
    description="""Description de l'API backend du projet [OSMdata](https://demo.openstreetmap.fr/map).

L'interface graphique `swagger-ui` de la documentation de l'API est disponible [ici](/swagger).
L'interface graphique `ReDoc` de la documentation de l'API est disponible [ici](/redoc).

Cette documentation vous permettra de prendre en main les différentes opérations de CRUD de l'aplication.
    """,
    terms_of_service="https://github.com/data-osm/frontend/blob/f24c68a0bc2141181dd7915714feb9b1566a6ab8/LICENSE",
    contact=openapi.Contact(email=settings.CONTACT_EMAIL),
    license=openapi.License(
        name="BSD License", url="https://fr.wikipedia.org/wiki/Licence_BSD"
    ),
)


if settings.DEBUG:
    schema_view = get_schema_view(
        public=True,
        permission_classes=[permissions.AllowAny],
    )
else:
    schema_view = get_schema_view(
        url=settings.FRONT_URL,
        public=True,
        permission_classes=[permissions.AllowAny],
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", GetCurrentUserView.as_view(), name="me"),
    path("api/csrf/", CsrfTokenView.as_view(), name="csrf-token"),
    path("api/account/", include(account_urlpatterns)),
    path("api/group/", include("group.urls")),
    path("api/provider/", include("provider.urls")),
    path("api/datasource/", include("osm.urls")),
    path("api/logs/", include("tracking.urls")),
    path("api/parameter/", include("parameter.urls")),
    path("api/osm/", include(osmUrlPatterns)),
    # Documentation
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
