from django.urls import path

from .views import (
    ListCreateVectorProviderView,
    SearchVectorProviderView,
    RetrieveUpdateDestroyVectorProviderView,
    ListCreateStyleView,
    ListVectorProviderWithStyleView,
    ListCustomStyle,
    RetrieveUpdateDestroyStyleView,
)

urlpatterns = [
    path("vector", ListCreateVectorProviderView.as_view(), name="List-vector-provider"),
    path(
        "vector/search",
        SearchVectorProviderView.as_view(),
        name="search-vector-provider",
    ),
    path(
        "vector/<int:pk>",
        RetrieveUpdateDestroyVectorProviderView.as_view(),
        name="vector-provider",
    ),
    path(
        "vector/style",
        ListVectorProviderWithStyleView.as_view(),
        name="vector-provider-with-style",
    ),
    path(
        "style/vector/<int:provider_vector_id>",
        ListCreateStyleView.as_view(),
        name="get-style",
    ),
    path("style/<int:pk>", RetrieveUpdateDestroyStyleView.as_view()),
    path("style/custom", ListCustomStyle.as_view(), name="list custom-style"),
]
