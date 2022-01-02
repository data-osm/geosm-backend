from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ListVectorProviderView, searchVectorProvider, VectorProviderDetailView, ListStyleView, vectorProviderWithStyleDetailView, ListCustomStyle, StyleDetailView

urlpatterns = [
    path("vector",ListVectorProviderView.as_view(),name="List-vector-provider"),
    path("vector/search",searchVectorProvider.as_view(),name="search-vector-provider"),
    path("vector/<int:pk>",VectorProviderDetailView.as_view(),name="vector-provider"),
    path("vector/style",vectorProviderWithStyleDetailView.as_view(),name="vector-provider-with-style"),

    path("style/vector/<int:provider_vector_id>",ListStyleView.as_view(),name="get-style"),
    path("style/<int:pk>",StyleDetailView.as_view()),

    path("style/custom",ListCustomStyle.as_view(),name="list custom-style")
]