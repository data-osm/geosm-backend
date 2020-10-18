from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import vectorProviderView, searchVectorProvider

urlpatterns = [
    path("vector",vectorProviderView.as_view(),name="List-vector-provider"),
    path("vector/search",searchVectorProvider.as_view(),name="search-vector-provider"),
]