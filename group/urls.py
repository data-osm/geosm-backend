from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import DownloadFeaturesInGeometry, CountFeaturesInGeometry, SubWithGroupDetail,searchLayer, SubListWithLayersView, GroupVieuwList, searchMaps, BaseMapGetDestroyVieuw, BaseMapListView, BaseMapView, searchIconsTags, retrieveIconView,searchLayerTags,MetadataVieuwListCreate, MetadataVieuwDetail, LayerProviderReorderView, LayerProviderStyleVieuwDetail, LayerProviderStyleVieuwListCreate, iconUploadView, listIconByCategory, searchIcon, MapViewDetail, MapViewListCreate, GroupVieuwDetail, GroupVieuwListCreate, SubVieuwDetail, SubVieuwListCreate, LayerVieuwDetail, LayerVieuwListCreate

urlpatterns = [
    #gets all user profiles and create a new profile
    path("icons",listIconByCategory.as_view(),name="icons-by-category"),
    path("icons/<int:pk>",retrieveIconView.as_view(),name="get-icon"),
    # path("icons",iconViewSet.as_view({'get': 'list'}),name="icons"),
    path("icons/add",iconUploadView.as_view(),name="add-icons"),
    path("icons/search",searchIcon.as_view(),name="search-icons"),
    # """ search icon by name. parameter :search_word  """
    path("map",MapViewListCreate.as_view()),
    path("map/search",searchMaps.as_view()),
    path("map/<int:pk>",MapViewDetail.as_view()),

    path("",GroupVieuwList.as_view()),
    path("group",GroupVieuwListCreate.as_view()),
    path("group/<int:pk>",GroupVieuwDetail.as_view()),

    path("sub",SubVieuwListCreate.as_view()),
    path("sub/layers",SubListWithLayersView.as_view()),
    path("sub/group/<int:pk>",SubWithGroupDetail.as_view()),
    path("sub/<int:pk>",SubVieuwDetail.as_view()),


    path("layer",LayerVieuwListCreate.as_view()),
    path("layer/search",searchLayer.as_view()),
    path("layer/<int:pk>",LayerVieuwDetail.as_view()),

    path("layer/provider",LayerProviderStyleVieuwListCreate.as_view()),
    path("layer/provider/<int:pk>",LayerProviderStyleVieuwDetail.as_view()),
    path("layer/provider/reorder",LayerProviderReorderView.as_view()),

    path("metadata",MetadataVieuwListCreate.as_view()),
    path("metadata/<int:pk>",MetadataVieuwDetail.as_view()),

    path("layer/tags/search",searchLayerTags.as_view(),name="search-tags-layer"),
    path("icons/tags/search",searchIconsTags.as_view(),name="search-tags-icon"),

    path("basemaps",BaseMapListView.as_view()),
    path("basemaps/add",BaseMapView.as_view()),
    path("basemaps/<int:pk>",BaseMapGetDestroyVieuw.as_view()),

    path("count",CountFeaturesInGeometry.as_view()),
    path("download",DownloadFeaturesInGeometry.as_view())

]