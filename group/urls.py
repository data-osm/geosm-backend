from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import LayerProviderStyleVieuwDetail, LayerProviderStyleVieuwListCreate, iconUploadView, listIconByCategory, searchIcon, MapViewDetail, MapViewListCreate, GroupVieuwDetail, GroupVieuwListCreate, SubVieuwDetail, SubVieuwListCreate, LayerVieuwDetail, LayerVieuwListCreate

urlpatterns = [
    #gets all user profiles and create a new profile
    path("icons",listIconByCategory.as_view(),name="icons-by-category"),
    # path("icons",iconViewSet.as_view({'get': 'list'}),name="icons"),
    path("icons/add",iconUploadView.as_view(),name="add-icons"),
    path("icons/search",searchIcon.as_view(),name="search-icons"),
    # """ search icon by name. parameter :search_word  """
    path("map",MapViewListCreate.as_view()),
    path("map/<int:pk>",MapViewDetail.as_view()),

    path("group",GroupVieuwListCreate.as_view()),
    path("group/<int:pk>",GroupVieuwDetail.as_view()),

    path("sub",SubVieuwListCreate.as_view()),
    path("sub/<int:pk>",SubVieuwDetail.as_view()),


    path("layer",LayerVieuwListCreate.as_view()),
    path("layer/<int:pk>",LayerVieuwDetail.as_view()),

    path("layer/provider/<int:layer_id>",LayerProviderStyleVieuwListCreate.as_view()),
    path("layer/provider",LayerProviderStyleVieuwListCreate.as_view()),
    path("layer/provider/detail/<int:pk>",LayerProviderStyleVieuwDetail.as_view()),

]