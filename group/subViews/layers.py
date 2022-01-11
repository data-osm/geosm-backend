from ..models import Map, Group, Sub, Layer, Default_map, Layer_provider_style, Tags, Metadata, Base_map
from genericIcon.models import Picto
from genericIcon.managePicto import createPicto, updatePicto, ImageBox
from ..subModels.icon import Icon, TagsIcon
from typing import List
from rest_framework import permissions
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from geosmBackend.cuserViews import ListCreateAPIView,RetrieveUpdateDestroyAPIView, RetrieveAPIView, CreateAPIView , ListAPIView, MultipleFieldLookupMixin, EnablePartialUpdateMixin, MultipleFieldLookupListMixin
from rest_framework import status
from django.conf import settings
from django.db import connection, transaction
from django.http.request import QueryDict
from cairosvg import svg2png
import tempfile
from django.core.files import File
from cuser.middleware import CuserMiddleware
from uuid import uuid4
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..documents import LayerDocument
from ..serializers import SubWithGroupSerializer, BaseMapSerializer ,TagsIconSerializer, IconSerializer, MapSerializer, DefaultMapSerializer, GroupSerializer, SubSerializer, SubWithLayersSerializer,  LayerSerializer, LayerProviderStyleSerializer, TagsSerializer, MetadataSerializer
from collections import defaultdict


class GetOldLayer(APIView):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        if 'layer_id' in request.data :
            key_couche = request.data['layer_id']
            with connection.cursor() as cursor:
                cursor.execute('SELECT layer_id FROM old_layer WHERE key_couche='+str(key_couche))
                layer_id = cursor.fetchone()[0]
                layer:Layer = Layer.objects.select_related().filter(pk=layer_id).get()

                return Response( {
                    'layer':LayerSerializer(Layer.objects.filter(pk__in=[layer.layer_id]), many=True).data[0],
                    'group':GroupSerializer(Group.objects.filter(pk__in=[layer.sub.group.group_id]), many=True).data[0],
                    }, 
                    status=status.HTTP_200_OK
                )
        else:
            return Response('key_couche not present in the request', status=status.HTTP_400_BAD_REQUEST)

class LayerVieuwDetail(RetrieveUpdateDestroyAPIView):
    queryset=Layer.objects.all()
    serializer_class=LayerSerializer

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
        operation_summary='Update a layer',
        responses={200: LayerSerializer()},
        tags=['Layer'],
    )
    def put(self, request, pk, format=None):
        """ update layer """
        vp_serializer = LayerSerializer(self.get_object(), data=request.data)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.request.data)
        if query_dict.get('svg_as_text', None) is not  None:
            f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.png')
            fileName = f.name
            svg2png(bytestring=request.data['svg_as_text'],write_to=fileName, unsafe=True)
            del request.data['svg_as_text']
            dataFile = open(fileName, "rb")
            request.data['cercle_icon'] = File(dataFile)

        if query_dict.get('svg_as_text_square', None) is not None:
            f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.png')
            fileName = f.name
            svg2png(bytestring=request.data['svg_as_text_square'],write_to=fileName, unsafe=True)
            del request.data['svg_as_text_square']
            dataFile = open(fileName, "rb")
            request.data['square_icon'] = File(dataFile)

        if 'icon' in  request.data and  query_dict.get('svg_as_text', None) is None and  query_dict.get('svg_as_text_square', None) is None:
            icon:Icon = Icon.objects.get(pk=request.data['icon'])
            request.data['cercle_icon'] = icon.path
            request.data['square_icon'] = icon.path
            try:
                del request.data['svg_as_text_square']
                del request.data['svg_as_text']
            except:
                pass

        if vp_serializer.is_valid():
            vp_serializer.save()
            return Response(vp_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(vp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        operation_summary='Retrieve a layer',
        responses={200: LayerSerializer()},
        tags=['Layer'],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a Layer"""
        return super(LayerVieuwDetail, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Delete a layer',
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        tags=['Layer'],
    )
    def delete(self, request, *args, **kwargs):
        """delete a layer"""
        return super(LayerVieuwDetail, self).delete(request, *args, **kwargs)


class LayerVieuwListCreate(MultipleFieldLookupListMixin, ListCreateAPIView):
    queryset=Layer.objects.all()
    serializer_class=LayerSerializer
    permission_classes=[permissions.IsAuthenticated]
    lookup_fields=['sub']
    model = Layer

    @swagger_auto_schema(
        operation_summary='Retrieve all layers',
        responses={200: LayerSerializer(many=True)},
        tags=['Layer'],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve all layers"""
        return super(LayerVieuwListCreate, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Create a new layer',
        responses={200: LayerSerializer()},
        tags=['Layer'],
    )
    def post(self, request, *args, **kwargs):
        """ Create a new layer """
        vp_serializer = LayerSerializer(data=request.data)
        
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.request.data)
        if query_dict.get('svg_as_text', None) is not  None:
            f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.png')
            fileName = f.name
            svg2png(bytestring=request.data['svg_as_text'],write_to=fileName, unsafe=True)
            del request.data['svg_as_text']
            dataFile = open(fileName, "rb")
            request.data['cercle_icon'] = File(dataFile)

        if query_dict.get('svg_as_text_square', None) is not None:
            f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.png')
            fileName = f.name
            svg2png(bytestring=request.data['svg_as_text_square'],write_to=fileName, unsafe=True)
            del request.data['svg_as_text_square']
            dataFile = open(fileName, "rb")
            request.data['square_icon'] = File(dataFile)

        if 'icon' in  request.data and  query_dict.get('svg_as_text', None) is None and  query_dict.get('svg_as_text_square', None) is None:
            icon:Icon = Icon.objects.get(pk=request.data['icon'])
            request.data['cercle_icon'] = icon.path
            request.data['square_icon'] = icon.path
            try:
                del request.data['svg_as_text_square']
                del request.data['svg_as_text']
            except:
                pass

        if vp_serializer.is_valid():
            vp_serializer.save()
            return Response(vp_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(vp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LayerProviderStyleVieuwDetail(RetrieveUpdateDestroyAPIView):
    queryset=Layer_provider_style.objects.all()
    serializer_class=LayerProviderStyleSerializer
    permission_classes=[permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Retrieve a relation layerProviderStyle',
        responses={200: LayerProviderStyleSerializer()},
        tags=['Layer-provider-style'],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a relation layerProviderStyle"""
        return super(LayerProviderStyleVieuwDetail, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='update a relation layerProviderStyle',
        responses={200: LayerProviderStyleSerializer()},
        tags=['Layer-provider-style'],
    )
    def put(self, request, *args, **kwargs):
        """update a relation layerProviderStyle"""
        return super(LayerProviderStyleVieuwDetail, self).put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Delete a relation layerProviderStyle',
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        tags=['Layer-provider-style'],
    )
    def delete(self, request, *args, **kwargs):
        """delete a relation layerProviderStyle"""
        return super(LayerProviderStyleVieuwDetail, self).delete(request, *args, **kwargs)

class LayerProviderStyleVieuwListCreate(MultipleFieldLookupListMixin, ListCreateAPIView):
    queryset=Layer_provider_style.objects.all()
    serializer_class=LayerProviderStyleSerializer
    permission_classes=[permissions.IsAuthenticated]
    model = Layer_provider_style
    lookup_fields=['layer_id']

    @swagger_auto_schema(
        operation_summary='Retrieve all relations layerProviderStyles',
        responses={200: LayerSerializer(many=True)},
        tags=['Layer-provider-style'],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve all relations layerProviderStyles"""
        return super(LayerProviderStyleVieuwListCreate, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Create one relation layerProviderStyle',
        responses={200: LayerSerializer(many=True)},
        tags=['Layer-provider-style'],
    )
    def post(self, request, *args, **kwargs):
        """Create one relation layerProviderStyle"""
        return super(LayerProviderStyleVieuwListCreate, self).post(request, *args, **kwargs)

class LayerProviderReorderView(APIView):
    permission_classes=[permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Set order of providers in a layer',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'reorderProviders': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description='The array of all providers of the layer with thier new order',
                    items={
                        'type': openapi.TYPE_OBJECT,
                        'properties':{
                            'id':{'type':openapi.TYPE_INTEGER, 'description':'The id of the provider'},
                            'ordre':{'type':openapi.TYPE_INTEGER}
                        }
                    },
                )
            }
        ),
        responses={200: ''},
        tags=['Layer'],
    )
    def post(self, request, *args, **kwargs):

        if 'reorderProviders' in  request.data:
            reorderProviders = request.data['reorderProviders']
            CuserMiddleware.set_user(request.user)
            for provider in reorderProviders:
                Layer_provider_style.objects.filter(pk=provider['id']).update(ordre=provider['ordre'])

            return Response([], status=status.HTTP_200_OK)
        else:
            return Response({'msg':" the 'reorderProviders' parameters is missing "}, status=status.HTTP_400_BAD_REQUEST)

class searchLayerTags(APIView):
    """
        View to search tags
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Search layer by tags',
        responses={200: TagsSerializer(many=True)},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'search_word': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The search key word'
                )
            }
        ),
        tags=['Layer'],
    )
    def post(self, request, *args, **kwargs):
        searchWord = request.data['search_word']
        responseQuerry = []
        for tag in Tags.objects.raw("SELECT * FROM group_tags WHERE strpos(unaccent(lower(name)),unaccent(lower('"+searchWord+"')))>0 Limit 20 "):
            responseQuerry.append(TagsSerializer(tag).data)

        return Response(responseQuerry,status=status.HTTP_200_OK)


class searchLayer(APIView):
    
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary='Search layer with elasticsearch',
        responses={200: LayerSerializer(many=True)},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'search_word': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The search key word'
                )
            }
        ),
        tags=['Layer'],
    )
    def post(self, request, *args, **kwargs):
        """
            search layer
        """
        searchQuerry = request.data['search_word']
        shouldTags:List=[]
        for item in searchQuerry.split():
            shouldTags.append(
                {
                    "match": {
                        "metadata.tags": item
                    }
                }
            )

        elasticResponse = LayerDocument.search().from_dict(
            {
                "query": {
                    "bool": {
                    "should": [
                        {
                        "multi_match": {
                            "boost": 4,
                            "query": searchQuerry,
                            "type": "best_fields",
                            "fuzziness": 2,
                            "fields": [
                            "name",
                            "name._2gram",
                            "name._3gram"
                            ]
                        }
                        },
                        {
                        "nested": {
                            "path": "metadata",
                            "query": {
                            "bool": {
                                    "should": shouldTags
                                }
                            }
                        }
                        },
                        {
                        "multi_match": {
                            "query": searchQuerry,
                            "boost": 0.5, 
                            "fields": [
                            "sub.group",
                            "sub.name"
                            ]
                        }
                        }
                    ]
                    }
                }
            }
        )
        pks = []
        for result in elasticResponse:
            if result.meta.index == 'layer':
                pks.append(result.meta.id)

        return Response( LayerSerializer(Layer.objects.filter(pk__in=pks), many=True).data ,status=status.HTTP_200_OK)
