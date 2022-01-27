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
from django.db import connection, transaction
from rest_framework.decorators import api_view
from cuser.middleware import CuserMiddleware
from uuid import uuid4
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..serializers import SubWithGroupSerializer, BaseMapSerializer ,TagsIconSerializer, IconSerializer, MapSerializer, DefaultMapSerializer, GroupSerializer, SubSerializer, SubWithLayersSerializer,  LayerSerializer, LayerProviderStyleSerializer, TagsSerializer, MetadataSerializer
from collections import defaultdict

class BaseMapDetailView(EnablePartialUpdateMixin, RetrieveUpdateDestroyAPIView):
    queryset=Base_map.objects.all()
    serializer_class=BaseMapSerializer
    permission_classes=[permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary='Delete a BaseMap',
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        tags=['Base map'],
    )
    def delete(self, request, *args, **kwargs):
        """delete a BaseMap"""
        return super(BaseMapDetailView, self).delete(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Retrieve a BaseMap',
        responses={200: BaseMapSerializer()},
        tags=['Base map'],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a BaseMap"""
        return super(BaseMapDetailView, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='update a BaseMap',
        responses={200: BaseMapSerializer()},
        tags=['Base map'],
    )
    def put(self, request, pk, format=None):
        """ update BaseMap """
        transaction.set_autocommit(False)
        CuserMiddleware.set_user(request.user)
        vp_serializer = BaseMapSerializer(self.get_object(), data=request.data, partial=True)

        if 'picto' in request.data:
            request.data['picto'] = {
                'raster_icon':request.data['picto']
            }
            picto = updatePicto(request.data['picto'], ImageBox(left=0, top=0, right=976, bottom=310))
            request.data['picto'] = picto.pk
          
        if vp_serializer.is_valid():
            vp_serializer.save()
            transaction.commit()
            return Response(vp_serializer.data, status=status.HTTP_201_CREATED)
        else:
            transaction.rollback()
            return Response(vp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseMapListView(MultipleFieldLookupListMixin, ListCreateAPIView):
    queryset=Base_map.objects.all()
    serializer_class=BaseMapSerializer
    lookup_fields=['']
    model = Base_map

    def get_authenticators(self): 
        if self.request.method == "GET":
            authentication_classes = []
            return authentication_classes
        else:
            return super(self.__class__, self).get_authenticators()

    def get_permissions(self):
        if self.request.method != 'GET' :
            self.permission_classes = [permissions.IsAuthenticated]
        return super(self.__class__, self).get_permissions()

    @swagger_auto_schema(
        operation_summary='Retrieve a BaseMap',
        responses={200: BaseMapSerializer(many=True)},
        tags=['Base map'],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve all BaseMaps"""
        return super(BaseMapListView, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Create a new BaseMap',
        responses={200: BaseMapSerializer()},
        tags=['Base map'],
    )
    def post(self, request, *args, **kwargs):
        """Create a new BaseMap"""
        if 'picto' in request.data:

            transaction.set_autocommit(False)
   
            request.data['picto'] = {
                'raster_icon':request.data['picto']
            }
            # print(request.data['picto'])
            picto = createPicto(request.data['picto'], ImageBox(left=0, top=0, right=976, bottom=310) )

            request.data['picto'] = picto.pk

            vp_serializer = BaseMapSerializer(data=request.data)

            if vp_serializer.is_valid():
                vp_serializer.save()
                transaction.commit()
                return Response(vp_serializer.data, status=status.HTTP_201_CREATED)
            else:
                transaction.rollback()
                return Response(vp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response(" 'picto' field is required", status=status.HTTP_400_BAD_REQUEST)


class SetPrincipalBaseMap(APIView):
    ''' Update the principal map'''
    permission_classes=[permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Define the principal baseMap',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.TYPE_INTEGER
            }
        ),
        responses={200: ''},
        tags=['Base map'],
    )
    def post(self, request, *args, **kwargs):

        if 'id' in  request.data:
            id = request.data['id']
            CuserMiddleware.set_user(request.user)
            for baseMap in Base_map.objects.all():
                baseMap.principal = False
                baseMap.save()

            baseMap = Base_map.objects.get(pk=id)
            baseMap.principal = True
            baseMap.save()
            return Response({}, status=status.HTTP_200_OK)
        else:
            return Response({'msg':" the 'reorderGroups' parameters is missing "}, status=status.HTTP_400_BAD_REQUEST)

