from django.urls import path

from .views import (
    OSMAuthenticationCallbackView,
    OSMAuthenticationView,
    UserListCreateView,
    userDetailView,
)

urlpatterns = [
    # gets all user profiles and create a new profile
    path("all-profiles", UserListCreateView.as_view(), name="all-profiles"),
    # retrieves profile details of the currently logged in user
    path("profile/<int:pk>", userDetailView.as_view(), name="profile"),
    path("osm-auth", OSMAuthenticationView.as_view(), name="osm-auth"),
    path(
        "osm-auth-callback",
        OSMAuthenticationCallbackView.as_view(),
        name="osm-auth-callback",
    ),
]
# http://127.0.0.1:8000//api/account/osm-auth
