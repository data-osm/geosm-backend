import uuid

from django.conf import settings
from django.contrib.auth import login, logout
from django.core.exceptions import NON_FIELD_ERRORS
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from requests_oauthlib import OAuth2Session
from rest_framework import response, status
from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    get_object_or_404,
)
from rest_framework.permissions import AllowAny, IsAuthenticated

from account.osm import (
    OsmFeatureUpdateException,
    OsmLocalFeatureUpdateException,
    OsmUserInfoException,
    get_osm_user_info,
    make_local_db_osm_change,
    make_osm_change,
)

from .models import User
from .permissions import CanAdministrate, CanUpdateOSM, IsOwnerProfileOrReadOnly
from .serializers import (
    LoginSerializer,
    RetrieveOSMUserInfoSerializer,
    UpdateOSMFeatureDeserializer,
    UserRegisterDeserializer,
    UserSerializer,
)


class UserListCreateView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [CanAdministrate]

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterDeserializer(data=self.request.data)  # type: ignore
        serializer.is_valid(raise_exception=True)

        user = User.objects.create_user(
            **serializer.validated_data,  # type: ignore
            is_administrator=True,
        )
        return response.Response(UserSerializer(user).data, status=status.HTTP_200_OK)


class userDetailView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerProfileOrReadOnly, CanAdministrate]


class LoginView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        context = {"request": request}
        deserializer = LoginSerializer(data=request.data, context=context)
        deserializer.is_valid(raise_exception=True)
        user = deserializer.validated_data["user"]  # type: ignore
        login(self.request, user)
        return response.Response(status=status.HTTP_200_OK)


class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logout(request)
        return response.Response(status=status.HTTP_200_OK)


class GetCurrentUserView(GenericAPIView):
    permission_classes = [CanAdministrate]

    def get(self, request):
        return response.Response(
            UserSerializer(request.user).data, status=status.HTTP_200_OK
        )


class CsrfTokenView(GenericAPIView):
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return response.Response({"message": "CSRF cookie set"})


class OSMAuthenticationView(GenericAPIView):
    permission_classes = [AllowAny]
    # authentication_classes = []

    def get(self, request):
        if request.GET.get("state_relay", None) is None:
            html = """
            Auth state relay not set, closing in 3 seconds
            <script>
                setTimeout(function() {
                    window.close();
                }, 3000)
            </script>
            """
            return HttpResponse(html)

        oauth = OAuth2Session(
            client_id=settings.OSM_CLIENT_ID,
            redirect_uri=settings.OSM_REDIRECT_URL,
            scope=["write_api", "read_prefs"],
        )
        authorization_url, state = oauth.authorization_url(
            settings.OSM_AUTHORIZATION_URL
        )

        request.session["oauth_state"] = state
        request.session["state_relay"] = request.GET.get("state_relay")

        return redirect(authorization_url)


class GetAuthSateRelayView(GenericAPIView):
    permission_classes = [AllowAny]
    # authentication_classes = []

    def get(self, request):
        return response.Response(
            {"state_relay": uuid.uuid4()}, status=status.HTTP_200_OK
        )


class OSMAuthenticationCallbackView(GenericAPIView):
    permission_classes = [AllowAny]
    # authentication_classes = []

    def get(self, request):
        osm = OAuth2Session(
            settings.OSM_CLIENT_ID,
            redirect_uri=settings.OSM_REDIRECT_URL,
            state=request.session["oauth_state"],
        )

        token = osm.fetch_token(
            settings.TOKEN_URL,
            client_secret=settings.OSM_CLIENT_SECRET_ID,
            authorization_response=request.build_absolute_uri(),
        )
        request.session["osm_token"] = token["access_token"]
        try:
            osm_user = get_osm_user_info(request)
        except OsmUserInfoException:
            return response.Response({}, status=status.HTTP_404_NOT_FOUND)
        print(request.user, "++" * 99)
        if request.user and request.user.is_authenticated:
            request.user.update_osm_token(
                osm_token=token["access_token"],
                state_relay=request.session["state_relay"],
            )
        elif not (
            User.objects.filter(
                username=osm_user["display_name"], osm_token__isnull=False
            ).exists()
        ):
            User.create_user_from_osm(
                username=osm_user["display_name"],
                osm_token=token["access_token"],
                state_relay=request.session["state_relay"],
            )
        else:
            user: User = User.objects.filter(
                username=osm_user["display_name"], osm_token__isnull=False
            ).first()  # type: ignore
            user.update_osm_token(
                osm_token=token["access_token"],
                state_relay=request.session["state_relay"],
            )

        html = """
        <script>
            window.close();
        </script>
        """

        return HttpResponse(html)


class RetrieveOSMUserInfoView(GenericAPIView):
    permission_classes = [AllowAny]
    # authentication_classes = []

    def get(self, request):
        if request.GET.get("state_relay", None) is not None:
            user = get_object_or_404(
                User,
                state_relay=request.GET.get("state_relay"),
            )
            login(self.request, user)

        try:
            osm_user = get_osm_user_info(request)
        except OsmUserInfoException:
            return response.Response({}, status=status.HTTP_404_NOT_FOUND)

        return response.Response(
            RetrieveOSMUserInfoSerializer(osm_user).data, status=status.HTTP_200_OK
        )


class UpdateOSMFeatureView(GenericAPIView):
    permission_classes = [IsAuthenticated & CanUpdateOSM]

    def post(self, request):
        deserializer = UpdateOSMFeatureDeserializer(data=request.data)
        deserializer.is_valid(raise_exception=True)
        try:
            make_osm_change(request.user.osm_token, deserializer.validated_data)  # type: ignore
        except OsmFeatureUpdateException as error:
            return response.Response(
                {NON_FIELD_ERRORS: str(error)}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            make_local_db_osm_change(deserializer.validated_data)  # type: ignore
        except OsmLocalFeatureUpdateException:
            pass
        return response.Response({}, status=status.HTTP_200_OK)
