# Create your views here.
from rest_framework import response, status
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from .models import User
from .permissions import IsOwnerProfileOrReadOnly
from .serializers import UserRegisterDeserializer, UserSerializer


class UserListCreateView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterDeserializer(self.request.data)
        serializer.is_valid(raise_exception=True)

        email = User.objects.normalize_email(serializer.validated_data.get("email"))
        user = User(email=email, **serializer.validated_data)
        user.set_password(serializer.validated_data.get("password"))
        user.save()
        return response.Response(UserSerializer(user), status=status.HTTP_200_OK)


class userDetailView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerProfileOrReadOnly, IsAuthenticated]
