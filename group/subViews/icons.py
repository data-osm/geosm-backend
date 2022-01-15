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


class IconDetailView(EnablePartialUpdateMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset=Icon.objects.all()
    serializer_class=IconSerializer

    @swagger_auto_schema(
        operation_summary='Retrieve an icon',
        responses={200: IconSerializer()},
        tags=['Icons'],
    )
    def get(self, request, *args, **kwargs):
        """ Retrieve an icon  """
        return super(IconDetailView, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Update an icon',
        responses={200: IconSerializer()},
        tags=['Icons'],
    )
    def put(self, request, pk):
        """ update an icon """
        icon = get_object_or_404(Icon.objects.all(), pk=pk)
        vp_serializer = IconSerializer(instance=icon, data=request.data, partial=True)

        if vp_serializer.is_valid():
            if 'tags' in request.data:
                vp_serializer.validated_data['tags'] =  request.data['tags']
            vp_serializer.save()
            return Response(vp_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(vp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary='Delete an icon',
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        tags=['Icons'],
    )
    def delete(self, request, *args, **kwargs):
        """ Delete an icon  """
        return super(IconDetailView, self).delete(request, *args, **kwargs)

class IconListView(ListCreateAPIView):
    """
        View to list icons by group
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_class = (FileUploadParser,)
    queryset=Icon.objects.all()
    serializer_class=IconSerializer

    @swagger_auto_schema(
        operation_summary='list icons by group',
        responses={200: IconSerializer(many=True)},
        tags=['Icons'],
    )
    def get(self, request, *args, **kwargs):
        groups = defaultdict(list)
        for icon in Icon.objects.all():
            groups[icon.category].append(IconSerializer(icon).data)

        return Response(groups,status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='Create a new icon',
        responses={200: IconSerializer()},
        tags=['Icons'],
    )
    def post(self, request, *args, **kwargs):
      CuserMiddleware.set_user(request.user)
      file_serializer = IconSerializer(data=request.data)
      if file_serializer.is_valid():
          if 'tags' in request.data:
            file_serializer.validated_data['tags'] =  request.data['tags']
          file_serializer.save()
          return Response(file_serializer.data, status=status.HTTP_201_CREATED)
      else:
          return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class searchIconsTags(APIView):
    """
        View to search tags
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Search icons by keywords',
        responses={200: TagsIconSerializer(many=True)},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'search_word': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The search key word'
                )
            }
        ),
        tags=['Icons'],
    )
    def post(self, request, *args, **kwargs):
        searchWord = request.data['search_word']
        responseQuerry = []
        for tag in TagsIcon.objects.raw("SELECT * FROM group_tagsicon WHERE strpos(unaccent(lower(name)),unaccent(lower('"+searchWord+"')))>0 Limit 20 "):
            responseQuerry.append(TagsIconSerializer(tag).data)
        return Response(responseQuerry,status=status.HTTP_200_OK)


class SearchIcon(APIView):
    """
        View to search icon
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Search icons by name',
        responses={200: IconSerializer(many=True)},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'search_word': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The search key word'
                )
            }
        ),
        tags=['Icons'],
    )
    def post(self, request, *args, **kwargs):
        """
            View to search icon
        """ 
        searchWord = request.data['search_word']
        responseQuerry = []

        for icon in Icon.objects.raw("SELECT * FROM group_icon WHERE strpos(unaccent(lower(name)),unaccent(lower('"+searchWord+"')))>0 Limit 20 "):
            responseQuerry.append(IconSerializer(icon).data)

        for icon  in Icon.objects.filter(tags__in=TagsIcon.objects.raw("SELECT id FROM group_tagsicon WHERE strpos(unaccent(lower(name)),unaccent(lower('"+searchWord+"')))>0 Limit 20 ")) :
            responseQuerry.append(IconSerializer(icon).data)

        return Response(responseQuerry,status=status.HTTP_200_OK)
