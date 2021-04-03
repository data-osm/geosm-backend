from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from .views import AdminBoundaryRetrieveUpdateDestroyView, ParameterRetrieveUpdateDestroyView, ParameterListView, AdminBoundaryCreateView, ExtentListView, ExtenView, ParameterCreateView

urlpatterns = [
    path("admin_boundary/<int:pk>",AdminBoundaryRetrieveUpdateDestroyView.as_view()),
    path("admin_boundary",AdminBoundaryCreateView.as_view()),
    path("parameter/<int:pk>",ParameterRetrieveUpdateDestroyView.as_view()),
    path("parameter",ParameterListView.as_view()),
    path("parameter/add",ParameterCreateView.as_view()),
    
    path("extent/list",ExtentListView.as_view()),
    path("extent",ExtenView.as_view()),
]

