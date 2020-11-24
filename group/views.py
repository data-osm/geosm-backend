from django.shortcuts import render

# Create your views here.
from .models import Icon, Map, Group, Sub, Layer, Default_map, Type
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import (ListCreateAPIView,RetrieveUpdateDestroyAPIView,)
from rest_framework import status
from django.db.models import Count

from .serializers import IconSerializer, MapSerializer, DefaultMapSerializer, GroupSerializer, SubSerializer, LayerSerializer, TypeSerializer
from collections import defaultdict


class listIconByCategory(APIView):
    """
        View to list icons by group
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        groups = defaultdict(list)
        for icon in Icon.objects.all():
            groups[icon.category].append(IconSerializer(icon).data)

        return Response(groups,status=status.HTTP_200_OK)

class iconUploadView(APIView):
    """
        View to upload icons
    """
    parser_class = (FileUploadParser,)
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
      file_serializer = IconSerializer(data=request.data)
      if file_serializer.is_valid():
          file_serializer.save()
          return Response(file_serializer.data, status=status.HTTP_201_CREATED)
      else:
          return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class searchIcon(APIView):
    """
        View to search icon
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        searchWord = request.data['search_word']
        responseQuerry = []
        for icon in Icon.objects.raw("SELECT * FROM group_icon WHERE strpos(unaccent(lower(name)),unaccent(lower('"+searchWord+"')))>0 Limit 20 "):
            responseQuerry.append(IconSerializer(icon).data)

        return Response(responseQuerry,status=status.HTTP_200_OK)

class MapViewDetail(RetrieveUpdateDestroyAPIView):
    queryset=Map.objects.all()
    serializer_class=MapSerializer
    permission_classes=[permissions.IsAuthenticated]

class MapViewListCreate(ListCreateAPIView):
    queryset=Map.objects.all()
    serializer_class=MapSerializer
    permission_classes=[permissions.IsAuthenticated]

class GroupVieuwDetail(RetrieveUpdateDestroyAPIView):
    queryset=Group.objects.all()
    serializer_class=GroupSerializer
    permission_classes=[permissions.IsAuthenticated]

class GroupVieuwListCreate(ListCreateAPIView):
    queryset=Group.objects.all()
    serializer_class=GroupSerializer
    permission_classes=[permissions.IsAuthenticated]

class SubVieuwDetail(RetrieveUpdateDestroyAPIView):
    queryset=Sub.objects.all()
    serializer_class=SubSerializer
    permission_classes=[permissions.IsAuthenticated]

class SubVieuwListCreate(ListCreateAPIView):
    queryset=Sub.objects.all()
    serializer_class=SubSerializer
    permission_classes=[permissions.IsAuthenticated]

class LayerVieuwDetail(RetrieveUpdateDestroyAPIView):
    queryset=Layer.objects.all()
    serializer_class=LayerSerializer
    permission_classes=[permissions.IsAuthenticated]

class LayerVieuwListCreate(ListCreateAPIView):
    queryset=Layer.objects.all()
    serializer_class=LayerSerializer
    permission_classes=[permissions.IsAuthenticated]

class TypeVieuwListCreate(ListCreateAPIView):
    queryset=Type.objects.all()
    serializer_class=TypeSerializer
    permission_classes=[permissions.IsAuthenticated]

class TypeVieuwDetail(RetrieveUpdateDestroyAPIView):
    queryset=Type.objects.all()
    serializer_class=TypeSerializer
    permission_classes=[permissions.IsAuthenticated]