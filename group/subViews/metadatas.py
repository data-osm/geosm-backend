from ..models import Map, Group, Sub, Layer, Default_map, Layer_provider_style, Tags, Metadata, Base_map
from rest_framework import permissions
from rest_framework import status
from geosmBackend.cuserViews import ListCreateAPIView,RetrieveUpdateDestroyAPIView, RetrieveAPIView, CreateAPIView , ListAPIView, MultipleFieldLookupMixin, EnablePartialUpdateMixin, MultipleFieldLookupListMixin
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..serializers import SubWithGroupSerializer, BaseMapSerializer ,TagsIconSerializer, IconSerializer, MapSerializer, DefaultMapSerializer, GroupSerializer, SubSerializer, SubWithLayersSerializer,  LayerSerializer, LayerProviderStyleSerializer, TagsSerializer, MetadataSerializer

class MetadataCreateView(MultipleFieldLookupMixin, RetrieveAPIView, CreateAPIView):
    queryset=Metadata.objects.all()
    serializer_class=MetadataSerializer
    permission_classes=[permissions.IsAuthenticated]
    # model = Metadata
    lookup_fields=['layer']

    @swagger_auto_schema(
        operation_summary='Create a new metadata on a layer',
        responses={200: MetadataSerializer()},
        tags=['Layer metadata'],
    )
    def post(self, request, *args, **kwargs):
        """Create a new metadata on a layer"""
        return super(MetadataCreateView, self).post(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Retrieve a metadata by layer id',
        manual_parameters=[openapi.Parameter('layer', openapi.IN_QUERY, description="layer id", type=openapi.TYPE_INTEGER)],
        responses={200: MetadataSerializer()},
        tags=['Layer metadata'],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a metadata by layer id"""
        return super(MetadataCreateView, self).get(request, *args, **kwargs)

class MetadataDetailView(EnablePartialUpdateMixin, RetrieveUpdateDestroyAPIView):
    queryset=Metadata.objects.all()
    serializer_class=MetadataSerializer
    permission_classes=[permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Delete a layer metadata',
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        tags=['Layer metadata'],
    )
    def delete(self, request, *args, **kwargs):
        """delete a layer metadata"""
        return super(MetadataDetailView, self).delete(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Retrieve a layer metadata',
        responses={200: MetadataSerializer()},
        tags=['Layer metadata'],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a layer metadata"""
        return super(MetadataDetailView, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Update a layer metadata',
        responses={200: MetadataSerializer()},
        tags=['Layer metadata'],
    )
    def put(self, request, *args, **kwargs):
        """Update a layer metadata"""
        return super(MetadataDetailView, self).put(request, *args, **kwargs)

