from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IconViewSet, IconUploadView, categoryViewSet

urlpatterns = [
    #gets all user profiles and create a new profile
    # path("icons",IconViewSet.as_view({'get': 'list'}),name="icons"),
    path("icons/category",IconViewSet.as_view({'get': 'list'}),name="icons"),
    path("icons/add",IconUploadView.as_view(),name="add-icons"),
]