from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import osmQuerryView, CreateOsmQuerryView,CreateSimpleQuerryView, SimpleQuerryVieuwDetail,ListConnection

urlpatterns = [
    path("osm", CreateOsmQuerryView.as_view(), name="add-osm-provider"),
    path("osm/<int:pk>", osmQuerryView.as_view(), name="osm-querry"),
    path("querry", CreateSimpleQuerryView.as_view(), name="add-querry"),
    path("querry/<int:pk>", SimpleQuerryVieuwDetail.as_view(), name="detail-querry"),
    path("connections", ListConnection.as_view(), name="list-connections"),
]
