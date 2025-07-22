from django.urls import path

from .views import (
    GetAuthSateRelayView,
    OSMAuthenticationCallbackView,
    OSMAuthenticationView,
    RetrieveOSMUserInfoView,
    UpdateOSMFeatureView,
    UserListCreateView,
    userDetailView,
)

urlpatterns = [
    # gets all user profiles and create a new profile
    path("all-profiles", UserListCreateView.as_view(), name="all-profiles"),
    # retrieves profile details of the currently logged in user
    path("profile/<int:pk>", userDetailView.as_view(), name="profile"),
    path("osm-auth", OSMAuthenticationView.as_view(), name="osm-auth"),
    path("osm-auth/info", RetrieveOSMUserInfoView.as_view(), name="osm-auth-info"),
    path(
        "auth-state-relay", GetAuthSateRelayView.as_view(), name="get-auth-state-relay"
    ),
    path(
        "osm-auth-callback",
        OSMAuthenticationCallbackView.as_view(),
        name="osm-auth-callback",
    ),
]

osmUrlPatterns = [
    path(
        "update-osm-feature", UpdateOSMFeatureView.as_view(), name="update-osm-feature"
    ),
]
