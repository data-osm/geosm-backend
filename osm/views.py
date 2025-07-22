from cuser.middleware import CuserMiddleware
from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from account.permissions import CanAdministrate
from geosmBackend.cuserViews import (
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from geosmBackend.type import httpResponse

from .serializers import SigFileSerializer, SimpleQuerrySerializer, osmQuerrySerializer
from .subModels.Querry import Querry, SimpleQuerry
from .subModels.sigFile import sigFile

# Create your views here.


class CreateOsmQuerryView(CreateAPIView):
    queryset = Querry.objects.all()
    serializer_class = osmQuerrySerializer
    permission_classes = [CanAdministrate]

    @swagger_auto_schema(
        operation_summary="Store a new osm query",
        responses={200: osmQuerrySerializer()},
        tags=["OSM provider"],
    )
    def post(self, request, *args, **kwargs):
        """Create an osm provider"""
        return super(CreateOsmQuerryView, self).post(request, *args, **kwargs)


class CreateSimpleQuerryView(CreateAPIView):
    queryset = SimpleQuerry.objects.all()
    serializer_class = SimpleQuerrySerializer
    permission_classes = [CanAdministrate]

    @swagger_auto_schema(
        operation_summary="Store a new simple query",
        responses={200: SimpleQuerrySerializer()},
        tags=["OSM provider"],
    )
    def post(self, request, *args, **kwargs):
        """Create an simple provider"""
        return super(CreateSimpleQuerryView, self).post(request, *args, **kwargs)


class SimpleQuerryViewDetail(RetrieveUpdateDestroyAPIView):
    queryset = SimpleQuerry.objects.all()
    serializer_class = SimpleQuerrySerializer
    permission_classes = [CanAdministrate]

    @swagger_auto_schema(
        operation_summary="Delete a Simple querry",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        tags=["OSM provider"],
    )
    def delete(self, request, *args, **kwargs):
        """Delete a Simple querry"""
        return super(SimpleQuerryViewDetail, self).delete(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a Simple querry",
        responses={200: SimpleQuerrySerializer()},
        tags=["OSM provider"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a Simple querry"""
        return super(SimpleQuerryViewDetail, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a Simple querry",
        responses={200: SimpleQuerrySerializer()},
        tags=["OSM provider"],
    )
    def put(self, request, *args, **kwargs):
        """Update a Simple querry"""
        return super(SimpleQuerryViewDetail, self).put(request, *args, **kwargs)


class osmQuerryView(APIView):
    """
    View to add an osm query
    """

    permission_classes = [CanAdministrate]

    @swagger_auto_schema(
        operation_summary="Finds a osm query by id",
        responses={200: osmQuerrySerializer()},
        tags=["OSM provider"],
    )
    def get(self, request, pk):
        """Retrieve an osm provider by his primary key"""
        saved_querry = get_object_or_404(Querry.objects.all(), pk=pk)
        op_serializer = osmQuerrySerializer(
            instance=saved_querry, data=request.data, partial=True
        )
        if op_serializer.is_valid(raise_exception=True):
            return Response(op_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                httpResponse(error=True, msg=op_serializer.errors).toJson(),
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_summary="Update an existing query",
        query_serializer=osmQuerrySerializer,
        responses={200: osmQuerrySerializer()},
        tags=["OSM provider"],
    )
    def put(self, request, pk):
        """update an osm query"""
        CuserMiddleware.set_user(request.user)
        saved_querry = get_object_or_404(Querry.objects.all(), pk=pk)
        op_serializer = osmQuerrySerializer(
            instance=saved_querry, data=request.data, partial=True
        )
        if op_serializer.is_valid(raise_exception=True):
            try:
                op_serializer.save()
                return Response(op_serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    httpResponse(error=True, msg=str(e)).toJson(),
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            return Response(op_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateSigFileView(CreateAPIView):
    queryset = sigFile.objects.all()
    serializer_class = SigFileSerializer
    permission_classes = [CanAdministrate]
    # authentication_classes = []

    @swagger_auto_schema(
        operation_summary="Store a new SIG file",
        responses={200: SigFileSerializer()},
        tags=["SIG Dataset"],
    )
    def post(self, request, *args, **kwargs):
        """Create an SIG dataset"""
        return super(CreateSigFileView, self).post(request, *args, **kwargs)


class SigFileViewDetail(RetrieveUpdateDestroyAPIView):
    queryset = sigFile.objects.all()
    serializer_class = SigFileSerializer
    permission_classes = [CanAdministrate]

    @swagger_auto_schema(
        operation_summary="Delete a SIG file",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        tags=["SIG Dataset"],
    )
    def delete(self, request, *args, **kwargs):
        """Delete a SIG dataset"""
        return super(SigFileViewDetail, self).delete(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a SIG dataset",
        responses={200: SigFileSerializer()},
        tags=["SIG Dataset"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a SIG dataset"""
        return super(SigFileViewDetail, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a SIG dataset",
        responses={200: SigFileSerializer()},
        tags=["SIG Dataset"],
    )
    def put(self, request, *args, **kwargs):
        """Update a SIG dataset"""
        return super(SigFileViewDetail, self).put(request, *args, **kwargs)


class ListConnection(APIView):
    permission_classes = [CanAdministrate]

    @swagger_auto_schema(
        operation_summary="Get all connections of the app",
        tags=["OSM provider"],
    )
    def get(self, requests):
        return Response(settings.DATABASES.keys(), status=status.HTTP_200_OK)
