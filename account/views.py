from django.shortcuts import render
# Create your views here.
from rest_framework.generics import (ListCreateAPIView,RetrieveUpdateDestroyAPIView,)
from rest_framework.permissions import IsAuthenticated
from .models import User
from .permissions import IsOwnerProfileOrReadOnly
from .serializers import userSerializer


class UserListCreateView(ListCreateAPIView):
    queryset=User.objects.all()
    serializer_class=userSerializer
    permission_classes=[IsAuthenticated]

    def perform_create(self, serializer):
        user=self.request.user
        serializer.save(user=user)


class userDetailView(RetrieveUpdateDestroyAPIView):
    queryset=User.objects.all()
    serializer_class=userSerializer
    permission_classes=[IsOwnerProfileOrReadOnly,IsAuthenticated]