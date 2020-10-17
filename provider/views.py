from django.shortcuts import render

# Create your views here.
from .models import Vector
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Count

from .serializers import VectorProviderSerializer
from collections import defaultdict
# Create your views here.

class vectorProviderView(APIView):
    """
        View to list all vector provider, add a vector provider usernames = [user.username for user in User.objects.all()]
        return Response(usernames)
    """
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        """ get all vector provider """
        return Response([VectorProviderSerializer(vector).data for vector in Vector.objects.all()],status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        """ store a new vector providor """
        vp_serializer = VectorProviderSerializer(data=request.data)
        if 'table' not in  request.data or 'shema' not in  request.data:
            request._mutable = True
            request.data.__setitem__('state','action_require')

        if vp_serializer.is_valid():
            vp_serializer.save()
            return Response(vp_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(vp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
