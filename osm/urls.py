from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import osmQuerryView, CreateOsmQuerryView,CreateSimpleQuerryView, SimpleQuerryVieuwDetail,ListConnection, CreateSigFileView, SigFileVieuwDetail

urlpatterns = [
    path("osm", CreateOsmQuerryView.as_view(), name="add-osm-provider"),
    path("osm/<int:pk>", osmQuerryView.as_view(), name="osm-querry"),
    path("querry", CreateSimpleQuerryView.as_view(), name="add-querry"),
    path("querry/<int:pk>", SimpleQuerryVieuwDetail.as_view(), name="detail-querry"),
    path("sig-file/<int:pk>", SigFileVieuwDetail.as_view(), name="detail-sig-file"),
    path("sig-file", CreateSigFileView.as_view(), name="add-sig-file"),
    path("connections", ListConnection.as_view(), name="list-connections"),
]
