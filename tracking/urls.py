from .views import TrackingEventListView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# http://127.0.0.1:8000/api/tracking/list?object_id=2&model_name=metadata
urlpatterns = [
    path("list",TrackingEventListView.as_view(),name="tracking"),
]