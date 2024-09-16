from django.urls import path, re_path

from group.subViews import icons as iconsViews
from group.subViews import profils as profilsViews
from group.subViews import groups as groupsViews
from group.subViews import layers as layersViews
from group.subViews import metadatas as metadatasViews
from group.subViews import baseMaps as baseMapsViews
from group.subViews import downloads as downloadsViews


urlpatterns = [
    path("icons", iconsViews.ListCreateIconView.as_view(), name="icons-by-category"),
    path(
        "icons/<int:pk>",
        iconsViews.RetrieveUpdateDestroyIconView.as_view(),
        name="get-icon",
    ),
    path("icons/search", iconsViews.SearchIcon.as_view(), name="search-icons"),
    path(
        "icons/tags/search",
        iconsViews.searchIconsTags.as_view(),
        name="search-tags-icon",
    ),
    path("map", profilsViews.ListCreateMapView.as_view()),
    path("map/search", profilsViews.SearchMaps.as_view()),
    path("map/<int:pk>", profilsViews.RetrieveUpdateDestroyMapView.as_view()),
    path("", groupsViews.ListCreateGroupView.as_view()),
    path("group/reorder", groupsViews.UpdateOrderGroup.as_view()),
    path("group/<int:pk>", groupsViews.RetrieveUpdateDestroyGroupView.as_view()),
    path("group/<int:pk>/set-principal", groupsViews.SetPrincipalGroup.as_view()),
    path("sub", groupsViews.SubViewListCreate.as_view()),
    path("sub/layers", groupsViews.ListSubWithLayersView.as_view()),
    path("sub/group/<int:pk>", groupsViews.RetrieveSubWithGroup.as_view()),
    path("sub/<int:pk>", groupsViews.RetrieveUpdateDestroySubView.as_view()),
    path("layer", layersViews.ListCreateLayerView.as_view()),
    path("layer/search", layersViews.searchLayer.as_view()),
    path("layer/old", layersViews.GetOldLayer.as_view()),
    path("layer/<int:pk>", layersViews.RetrieveUpdateDestroyLayerView.as_view()),
    path("layer/<int:pk>/set-principal", layersViews.SetPrincipalLayer.as_view()),
    path("layer/provider", layersViews.ListCreateLayerProviderStyleView.as_view()),
    path(
        "layer/provider/<int:pk>",
        layersViews.RetrieveUpdateDestroyLayerProviderStyleView.as_view(),
    ),
    path("layer/provider/reorder", layersViews.LayerProviderReorderView.as_view()),
    path("metadata", metadatasViews.RetrieveCreateMetadataView.as_view()),
    path(
        "metadata/<int:pk>", metadatasViews.RetrieveUpdateDestroyMetadataView.as_view()
    ),
    path(
        "layer/tags/search",
        layersViews.SearchLayerTags.as_view(),
        name="search-tags-layer",
    ),
    path("basemaps", baseMapsViews.BaseMapListCreateView.as_view()),
    path("basemaps/principal", baseMapsViews.SetPrincipalBaseMap.as_view()),
    path("basemaps/<int:pk>", baseMapsViews.RetrieveUpdateDestroyBaseMapView.as_view()),
    path("count", downloadsViews.CountFeaturesInGeometry.as_view()),
    re_path(r"download/$", downloadsViews.DownloadFeaturesInGeometry.as_view()),
    re_path(r"download/id/$", downloadsViews.DownloadFeatureById.as_view()),
]
