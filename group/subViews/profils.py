from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics, permissions, status

from geosmBackend.cuserViews import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from ..models import (
    Map,
)
from ..serializers import (
    MapSerializer,
)


class RetrieveUpdateDestroyMapView(RetrieveUpdateDestroyAPIView):
    queryset = Map.objects.all()
    serializer_class = MapSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve a map",
        responses={200: MapSerializer()},
        tags=["Profils"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a map"""
        return super(RetrieveUpdateDestroyMapView, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially Update a map",
        responses={200: MapSerializer()},
        tags=["Profils"],
    )
    def patch(self, request, *args, **kwargs):
        """Partially Update a map"""
        return super(RetrieveUpdateDestroyMapView, self).partial_update(
            request, *args, **kwargs
        )

    @swagger_auto_schema(
        operation_summary="Update a map",
        responses={200: MapSerializer()},
        tags=["Profils"],
    )
    def put(self, request, *args, **kwargs):
        """Update a map"""
        return super(RetrieveUpdateDestroyMapView, self).put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a map",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        tags=["Profils"],
    )
    def delete(self, request, *args, **kwargs):
        """Delete a map"""
        return super(RetrieveUpdateDestroyMapView, self).delete(
            request, *args, **kwargs
        )


class ListCreateMapView(ListCreateAPIView):
    queryset = Map.objects.all()
    serializer_class = MapSerializer
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="Returns all Maps",
        responses={200: MapSerializer(many=True)},
        tags=["Profils"],
    )
    def get(self, request, *args, **kwargs):
        """List all maps"""
        return super(ListCreateMapView, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Add a new map",
        responses={200: MapSerializer()},
        tags=["Profils"],
    )
    def post(self, request, *args, **kwargs):
        """Create a map"""
        return super(ListCreateMapView, self).post(request, *args, **kwargs)


class SearchMaps(generics.ListAPIView):
    """
    View to search map's
    """

    queryset = Map.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    serializer_class = MapSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Search icons by name",
        responses={200: MapSerializer(many=True)},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "search": openapi.Schema(
                    type=openapi.TYPE_STRING, description="The search key word"
                )
            },
        ),
        tags=["Profils"],
    )
    def get(self, request, *args, **kwargs):
        return super(SearchMaps, self).get(request, *args, **kwargs)
