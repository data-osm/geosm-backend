import osmapi
import requests
from dj_rest_auth.serializers import LoginSerializer
from django.conf import settings
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from requests_oauthlib import OAuth2Session
from rest_framework import response, status
from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import User
from .permissions import IsOwnerProfileOrReadOnly
from .serializers import UserRegisterDeserializer, UserSerializer


class UserListCreateView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterDeserializer(data=self.request.data)  # type: ignore
        serializer.is_valid(raise_exception=True)

        user = User.objects.create_user(**serializer.validated_data)  # type: ignore
        return response.Response(UserSerializer(user).data, status=status.HTTP_200_OK)


class userDetailView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerProfileOrReadOnly, IsAuthenticated]


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

    def post(self, request):
        logout(request)
        return response.Response(status=status.HTTP_200_OK)


class GetCurrentUserView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return response.Response(
            UserSerializer(request.user).data, status=status.HTTP_200_OK
        )


class CsrfTokenView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return response.Response({"message": "CSRF cookie set"})


class OSMAuthenticationView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request):
        oauth = OAuth2Session(
            client_id=settings.OSM_CLIENT_ID,
            redirect_uri=settings.OSM_REDIRECT_URL,
            scope=["write_api", "read_prefs"],
        )
        authorization_url, state = oauth.authorization_url(
            settings.OSM_AUTHORIZATION_URL
        )

        request.session["oauth_state"] = state
        return redirect(authorization_url)


class OSMAuthenticationCallbackView(GenericAPIView):
    permission_classes = [AllowAny]

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
        return token["access_token"]


def get_osm_user_info(access_token):
    def parse_osm_user_info(xml_string):
        import xml.etree.ElementTree as ET

        root = ET.fromstring(xml_string)
        user = root.find("user")
        if user is None:
            return "Nom d'utilisateur non trouvé"
        return user.attrib.get("display_name")

    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(settings.OSM_USER_DETAIL_URL, headers=headers)
    response.raise_for_status()
    return parse_osm_user_info(response.text)


def make_osm_change(access_token):
    oauth_session = OAuth2Session(
        settings.OSM_CLIENT_ID, token={"access_token": access_token}
    )
    api = osmapi.OsmApi(api=settings.OSM_API_URL, session=oauth_session)
    features_to_update = [
        {
            "id": 4307255289,
            "type": "way",
            "rnb": "RNB__TEST_1",
        },
        {
            "id": 4307255288,
            "type": "way",
            "rnb": "RNB__TEST_2",
        },
        {
            "id": 4305234111,
            "type": "relation",
            "rnb": "RNB__TEST_3",
        },
    ]
    with api.Changeset({"comment": "DEMO OSM DATA"}) as changeset_id:
        for feature in features_to_update:
            id = feature["id"]
            if feature["type"] == "way":
                way = api.WayGet(id)

                existing_tags = way["tag"]
                existing_tags["ref:FR:RNB"] = feature["rnb"]
                way = api.WayUpdate(
                    {
                        "id": id,
                        "version": way["version"],
                        "tag": existing_tags,
                    }
                )
            elif feature["type"] == "relation":
                relation = api.RelationGet(id)

                existing_tags = relation["tag"]
                existing_tags["ref:FR:RNB"] = feature["rnb"]
                relation = api.RelationUpdate(
                    {
                        "id": id,
                        "version": relation["version"],
                        "tag": existing_tags,
                    }
                )
