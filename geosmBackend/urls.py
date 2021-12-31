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
from django.contrib import admin
from django.urls import path,include, re_path
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from rest_framework import permissions
# from rest_framework.authtoken.views import obtain_auth_token
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

swagger_api_info = openapi.Info(
    title='Data-osm API',
    default_version='v1',
    description="""Description de l'API backend du projet [data-osm](https://demo.openstreetmap.fr/map).

L'interface graphique `swagger-ui` de la documentation de l'API est disponible [ici](/swagger).
L'interface graphique `ReDoc` de la documentation de l'API est disponible [ici](/redoc).

Cette documentation vous permettra de prendre en main les différentes opérations de CRUD de l'aplication.
    """,
    terms_of_service='https://www.google.com/policies/terms/',
    contact=openapi.Contact(email='contact@dataosm.info'),
    license=openapi.License(name='BSD License', url='https://fr.wikipedia.org/wiki/Licence_BSD'),
)


if settings.DEBUG:
    schema_view = get_schema_view(
        public=True,
        permission_classes=[permissions.AllowAny],
    )
else:
    schema_view = get_schema_view(
        url='https://www.dataosm.info/',
        public=True,
        permission_classes=[permissions.AllowAny],
    )


urlpatterns = [
    path('admin/', admin.site.urls),

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path("api/account/",include("account.urls")),
    path("api/group/",include("group.urls")),
    path("api/provider/",include("provider.urls")),
    path("api/datasource/",include("osm.urls")),
    path("api/tracking/",include("tracking.urls")),
    path("api/parameter/",include("parameter.urls")),

    # Documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
