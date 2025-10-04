from django.urls import path

from .views import (
    AdminBoundaryCreateView,
    AdminBoundaryDetailView,
    ExtentListView,
    ExtenView,
    GetExtentViewById,
    GetFeatureAdminBoundary,
    ListLczView,
    ParameterCreateView,
    ParameterDetailView,
    ParameterListView,
    SearchBoundary,
)

urlpatterns = [
    path("admin_boundary/<int:pk>", AdminBoundaryDetailView.as_view()),
    path("admin_boundary", AdminBoundaryCreateView.as_view()),
    path("admin_boundary/search", SearchBoundary.as_view()),
    path("admin_boundary/feature", GetFeatureAdminBoundary.as_view()),
    path("parameter/<int:pk>", ParameterDetailView.as_view()),
    path("parameter", ParameterListView.as_view()),
    path("parameter/add", ParameterCreateView.as_view()),
    path("extent/list", ExtentListView.as_view()),
    path("extent", ExtenView.as_view()),
    path("extent/get", GetExtentViewById.as_view()),
    path("list-lcz", ListLczView.as_view()),
]
