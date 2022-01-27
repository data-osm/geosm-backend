from ..models import Map, Group, Sub, Layer, Default_map, Layer_provider_style, Tags, Metadata, Base_map
from genericIcon.models import Picto
from genericIcon.managePicto import createPicto, updatePicto, ImageBox
from ..subModels.icon import Icon, TagsIcon
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from geosmBackend.cuserViews import ListCreateAPIView,RetrieveUpdateDestroyAPIView, RetrieveAPIView, CreateAPIView , ListAPIView, MultipleFieldLookupMixin, EnablePartialUpdateMixin, MultipleFieldLookupListMixin
from rest_framework import status
from django.shortcuts import get_list_or_404, get_object_or_404

from cuser.middleware import CuserMiddleware
from uuid import uuid4
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..serializers import SubWithGroupSerializer, BaseMapSerializer ,TagsIconSerializer, IconSerializer, MapSerializer, DefaultMapSerializer, GroupSerializer, SubSerializer, SubWithLayersSerializer,  LayerSerializer, LayerProviderStyleSerializer, TagsSerializer, MetadataSerializer
from collections import defaultdict


class MapViewDetail(RetrieveUpdateDestroyAPIView):
    queryset=Map.objects.all()
    serializer_class=MapSerializer
    permission_classes=[permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Retrieve a map',
        responses={200: MapSerializer()},
        tags=['Profils'],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a map"""
        return super(MapViewDetail, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Partially Update a map',
        responses={200: MapSerializer()},
        tags=['Profils'],
    )
    def patch(self, request, *args, **kwargs):
        """Partially Update a map """
        return super(MapViewDetail, self).patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Update a map',
        responses={200: MapSerializer()},
        tags=['Profils'],
    )
    def put(self, request, *args, **kwargs):
        """Update a map"""
        return super(MapViewDetail, self).put(request, *args, **kwargs)
        
    @swagger_auto_schema(
        operation_summary='Delete a map',
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        tags=['Profils'],
    )
    def delete(self, request, *args, **kwargs):
        """ Delete a map  """
        return super(MapViewDetail, self).delete(request, *args, **kwargs)

class MapViewListCreate(ListCreateAPIView):
    queryset=Map.objects.all()
    serializer_class=MapSerializer
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary='Returns all Maps',
        responses={200: MapSerializer(many=True)},
        tags=['Profils'],
    )
    def get(self, request, *args, **kwargs):
        """ List all maps  """
        return super(MapViewListCreate, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Add a new map',
        responses={200: MapSerializer()},
        tags=['Profils'],
    )
    def post(self, request, *args, **kwargs):
        """ Create a map  """
        return super(MapViewListCreate, self).post(request, *args, **kwargs)

class SearchMaps(APIView):
    """
        View to search map's
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Search icons by name',
        responses={200: MapSerializer(many=True)},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'search_word': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The search key word'
                )
            }
        ),
        tags=['Profils'],
    )
    def post(self, request, *args, **kwargs):
        searchWord = request.data['search_word']
        responseQuerry = []
        for map in Map.objects.raw("SELECT * FROM group_map WHERE strpos(unaccent(lower(name)),unaccent(lower('"+searchWord+"')))>0 Limit 20 "):
            responseQuerry.append(MapSerializer(map).data)

        return Response(responseQuerry,status=status.HTTP_200_OK)

