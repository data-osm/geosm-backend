from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import  osmQuerryView

urlpatterns = [
    path("osm",osmQuerryView.as_view(),name="add-osm-provider"),
    path("osm/<int:pk>",osmQuerryView.as_view(),name="osm-querry"),
]