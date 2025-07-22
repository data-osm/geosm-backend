from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics, status
from rest_framework.response import Response

from account.permissions import CanAdministrate
from geosmBackend.cuserViews import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from geosmBackend.type import httpResponse

from ..models import Vector
from ..serializers import VectorProviderSerializer, VectorProviderWithStyleSerializer


class ListCreateVectorProviderView(ListCreateAPIView):
    queryset = Vector.objects.all()
    serializer_class = VectorProviderSerializer
    permission_classes = [CanAdministrate]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = "__all__"
    # ordering = ['name']
    # filterset_fields = ['geometry_type']

    @swagger_auto_schema(
        operation_summary="Returns all providers",
        responses={200: VectorProviderSerializer(many=True)},
        tags=["Providers"],
    )
    def get(self, request, *args, **kwargs):
        """List all provider"""
        return super(ListCreateVectorProviderView, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Add a new provider",
        responses={200: VectorProviderSerializer()},
        tags=["Providers"],
    )
    def post(self, request, *args, **kwargs):
        """Create a provider"""
        return super(ListCreateVectorProviderView, self).post(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Deletes many providers",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "provider_vector_ids": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="List of provider_vector_id to delete",
                    items={"type": openapi.TYPE_INTEGER},
                )
            },
        ),
        tags=["Providers"],
    )
    def delete(self, request, *args, **kwargs):
        """Delete many vector providers"""
        provider_vector_ids = request.data["provider_vector_ids"]
        vector_providers = Vector.objects.filter(pk__in=provider_vector_ids)
        vector_providers.delete()
        return Response(httpResponse(False).__dict__, status=status.HTTP_200_OK)


class RetrieveUpdateDestroyVectorProviderView(RetrieveUpdateDestroyAPIView):
    queryset = Vector.objects.all()
    serializer_class = VectorProviderSerializer
    permission_classes = [CanAdministrate]

    @swagger_auto_schema(
        operation_summary="Deletes a provider by id",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        tags=["Providers"],
    )
    def delete(self, request, *args, **kwargs):
        """Delete a provider"""
        return super(RetrieveUpdateDestroyVectorProviderView, self).delete(
            request, *args, **kwargs
        )

    @swagger_auto_schema(
        operation_summary="Partially update a provider",
        responses={200: VectorProviderSerializer()},
        tags=["Providers"],
    )
    def patch(self, request, *args, **kwargs):
        """Partially Update Provider"""
        return super(RetrieveUpdateDestroyVectorProviderView, self).partial_update(
            request, *args, **kwargs
        )

    @swagger_auto_schema(
        operation_summary="Update a provider",
        responses={200: VectorProviderSerializer()},
        tags=["Providers"],
    )
    def put(self, request, *args, **kwargs):
        """Update Provider"""
        return super(RetrieveUpdateDestroyVectorProviderView, self).put(
            request, *args, **kwargs
        )

    @swagger_auto_schema(
        operation_summary="Finds a provider",
        responses={200: VectorProviderSerializer()},
        tags=["Providers"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a provider"""
        return super(RetrieveUpdateDestroyVectorProviderView, self).get(
            request, *args, **kwargs
        )


class SearchVectorProviderView(generics.ListAPIView):
    """
    View to search a vector provider
    """

    permission_classes = [CanAdministrate]
    queryset = Vector.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    serializer_class = VectorProviderSerializer

    @swagger_auto_schema(
        operation_summary="Search provider by keywords",
        responses={200: VectorProviderSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="key word to search",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        tags=["Providers"],
    )
    def get(self, request, *args, **kwargs):
        """Search a vector provider"""
        return super(SearchVectorProviderView, self).get(request, *args, **kwargs)


class ListVectorProviderWithStyleView(ListAPIView):
    """View get a vector provider with a style"""

    queryset = Vector.objects.all()
    serializer_class = VectorProviderWithStyleSerializer
    permission_classes = [CanAdministrate]

    @swagger_auto_schema(
        operation_summary="Gets all providers with style",
        responses={200: VectorProviderWithStyleSerializer(many=True)},
        tags=["Providers"],
    )
    def get(self, request, *args, **kwargs):
        """List all provider with their style"""
        return super(ListVectorProviderWithStyleView, self).get(
            request, *args, **kwargs
        )
