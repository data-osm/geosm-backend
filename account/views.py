from dj_rest_auth.serializers import LoginSerializer
from django.contrib.auth import login, logout
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
        serializer = UserRegisterDeserializer(data=self.request.data)
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
