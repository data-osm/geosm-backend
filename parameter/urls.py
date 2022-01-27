from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from .views import ParameterDetailView,AdminBoundaryDetailView,GetExtentViewById, GetFeatureAdminBoundary, SearchBoundary,ParameterListView, AdminBoundaryCreateView, ExtentListView, ExtenView, ParameterCreateView

urlpatterns = [
    path("admin_boundary/<int:pk>",AdminBoundaryDetailView.as_view()),
    path("admin_boundary",AdminBoundaryCreateView.as_view()),
    path("admin_boundary/search",SearchBoundary.as_view()),
    path("admin_boundary/feature",GetFeatureAdminBoundary.as_view()),

    path("parameter/<int:pk>",ParameterDetailView.as_view()),
    path("parameter",ParameterListView.as_view()),
    path("parameter/add",ParameterCreateView.as_view()),
    
    path("extent/list",ExtentListView.as_view()),
    path("extent",ExtenView.as_view()),
    path("extent/get",GetExtentViewById.as_view()),
]

