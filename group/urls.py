from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import iconUploadView, listIconByCategory, searchIcon

urlpatterns = [
    #gets all user profiles and create a new profile
    path("icons",listIconByCategory.as_view(),name="icons-by-category"),
    # path("icons",iconViewSet.as_view({'get': 'list'}),name="icons"),
    path("icons/add",iconUploadView.as_view(),name="add-icons"),
    path("icons/search",searchIcon.as_view(),name="search-icons"),
    # """ search icon by name. parameter :search_word  """
]