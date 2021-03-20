from .views import TrackingEventListView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path("list",TrackingEventListView.as_view(),name="tracking"),
]