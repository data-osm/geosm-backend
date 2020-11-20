from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import vectorProviderView, searchVectorProvider, vectorProviderDetailView, styleView

urlpatterns = [
    path("vector",vectorProviderView.as_view(),name="List-vector-provider"),
    path("vector/search",searchVectorProvider.as_view(),name="search-vector-provider"),
    path("vector/<int:pk>",vectorProviderDetailView.as_view(),name="vector-provider"),

    path("style/<int:provider_vector_id>",styleView.as_view(),name="get-style"),
    path("style",styleView.as_view(),name="style")
]