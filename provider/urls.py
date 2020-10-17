from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import vectorProviderView

urlpatterns = [
    path("vector",vectorProviderView.as_view(),name="List-vector-provider"),
]