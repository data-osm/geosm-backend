from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import iconUploadView, listIconByCategory, searchIcon, MapViewDetail, MapViewListCreate, GroupVieuwDetail, GroupVieuwListCreate, SubVieuwDetail, SubVieuwListCreate, LayerVieuwDetail, LayerVieuwListCreate, TypeVieuwDetail, TypeVieuwListCreate

urlpatterns = [
    #gets all user profiles and create a new profile
    path("icons",listIconByCategory.as_view(),name="icons-by-category"),
    # path("icons",iconViewSet.as_view({'get': 'list'}),name="icons"),
    path("icons/add",iconUploadView.as_view(),name="add-icons"),
    path("icons/search",searchIcon.as_view(),name="search-icons"),
    # """ search icon by name. parameter :search_word  """
    path("map",MapViewListCreate.as_view()),
    path("map/<int:pk>",MapViewDetail.as_view()),

    path("group",GroupVieuwDetail.as_view()),
    path("group/<int:pk>",GroupVieuwListCreate.as_view()),

    path("sub",SubVieuwDetail.as_view()),
    path("sub/<int:pk>",SubVieuwListCreate.as_view()),

    path("layer",LayerVieuwListCreate.as_view()),
    path("layer/<int:pk>",LayerVieuwDetail.as_view()),

    path("type",TypeVieuwListCreate.as_view()),
    path("type/<int:pk>",TypeVieuwDetail.as_view()),

]