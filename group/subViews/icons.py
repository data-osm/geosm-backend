from collections import defaultdict

from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics, status
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from account.permissions import CanAdministrate
from geosmBackend.cuserViews import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from ..serializers import (
    IconSerializer,
    TagsIconSerializer,
)
from ..subModels.icon import Icon, TagsIcon


class RetrieveUpdateDestroyIconView(RetrieveUpdateDestroyAPIView):
    permission_classes = [CanAdministrate]
    queryset = Icon.objects.all()
    serializer_class = IconSerializer

    @swagger_auto_schema(
        operation_summary="Retrieve an icon",
        responses={200: IconSerializer()},
        tags=["Icons"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve an icon"""
        return super(RetrieveUpdateDestroyIconView, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update an icon",
        responses={200: IconSerializer()},
        tags=["Icons"],
    )
    def put(self, request, pk):
        """update an icon"""
        icon = get_object_or_404(Icon.objects.all(), pk=pk)
        vp_serializer = IconSerializer(instance=icon, data=request.data, partial=True)

        if vp_serializer.is_valid():
            if "tags" in request.data:
                vp_serializer.validated_data["tags"] = request.data["tags"]
            vp_serializer.save()
            return Response(vp_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(vp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete an icon",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        tags=["Icons"],
    )
    def delete(self, request, *args, **kwargs):
        """Delete an icon"""
        return super(RetrieveUpdateDestroyIconView, self).delete(
            request, *args, **kwargs
        )


class ListCreateIconView(ListCreateAPIView):
    """
    View to list icons by group
    """

    permission_classes = [CanAdministrate]
    parser_class = (FileUploadParser,)
    queryset = Icon.objects.all()
    serializer_class = IconSerializer

    @swagger_auto_schema(
        operation_summary="list icons by group",
        responses={200: IconSerializer(many=True)},
        tags=["Icons"],
    )
    def get(self, request, *args, **kwargs):
        groups = defaultdict(list)
        for icon in Icon.objects.all():
            groups[icon.category].append(IconSerializer(icon).data)

        return Response(groups, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create a new icon",
        responses={200: IconSerializer()},
        tags=["Icons"],
    )
    def post(self, request, *args, **kwargs):
        file_serializer = IconSerializer(data=request.data)
        if file_serializer.is_valid():
            if "tags" in request.data:
                file_serializer.validated_data["tags"] = request.data["tags"]
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class searchIconsTags(generics.ListAPIView):
    """
    View to search tags
    """

    permission_classes = [CanAdministrate]
    queryset = TagsIcon.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    serializer_class = TagsIconSerializer

    @swagger_auto_schema(
        operation_summary="Search icons by keywords",
        responses={200: TagsIconSerializer(many=True)},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "search": openapi.Schema(
                    type=openapi.TYPE_STRING, description="The search key word"
                )
            },
        ),
        tags=["Icons"],
    )
    def get(self, request, *args, **kwargs):
        return super(searchIconsTags, self).get(request, *args, **kwargs)


class SearchIcon(generics.ListAPIView):
    """
    View to search icon
    """

    permission_classes = [CanAdministrate]
    queryset = Icon.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "tags__name"]
    serializer_class = IconSerializer

    @swagger_auto_schema(
        operation_summary="Search icons by name",
        responses={200: IconSerializer(many=True)},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "search": openapi.Schema(
                    type=openapi.TYPE_STRING, description="The search key word"
                )
            },
        ),
        tags=["Icons"],
    )
    def get(self, request, *args, **kwargs):
        """
        View to search icon
        """
        return super(SearchIcon, self).get(request, *args, **kwargs)
