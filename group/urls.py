from django.conf.urls import url
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import *

urlpatterns = [
    path("icons",IconListView.as_view(),name="icons-by-category"),
    path("icons/<int:pk>",IconDetailView.as_view(),name="get-icon"),
    path("icons/search",SearchIcon.as_view(),name="search-icons"),

    path("map",MapViewListCreate.as_view()),
    path("map/search",SearchMaps.as_view()),
    path("map/<int:pk>",MapViewDetail.as_view()),

    path("",GroupVieuwList.as_view()),
    path("group/reorder",UpdateOrderGroup.as_view()),
    path("group/<int:pk>",GroupVieuwDetail.as_view()),

    path("sub",SubVieuwListCreate.as_view()),
    path("sub/layers",SubListWithLayersView.as_view()),
    path("sub/group/<int:pk>",SubWithGroupDetail.as_view()),
    path("sub/<int:pk>",SubVieuwDetail.as_view()),


    path("layer",LayerVieuwListCreate.as_view()),
    path("layer/search",searchLayer.as_view()),
    path("layer/old",GetOldLayer.as_view()),
    path("layer/<int:pk>",LayerVieuwDetail.as_view()),

    path("layer/provider",LayerProviderStyleVieuwListCreate.as_view()),
    path("layer/provider/<int:pk>",LayerProviderStyleVieuwDetail.as_view()),
    path("layer/provider/reorder",LayerProviderReorderView.as_view()),

    path("metadata",MetadataCreateView.as_view()),
    path("metadata/<int:pk>",MetadataDetailView.as_view()),

    path("layer/tags/search",searchLayerTags.as_view(),name="search-tags-layer"),
    path("icons/tags/search",searchIconsTags.as_view(),name="search-tags-icon"),

    path("basemaps",BaseMapListView.as_view()),
    path("basemaps/principal",SetPrincipalBaseMap.as_view()),
    path("basemaps/<int:pk>",BaseMapDetailView.as_view()),

    path("count",CountFeaturesInGeometry.as_view()),
    url(r'download/$',DownloadFeaturesInGeometry.as_view()),

]