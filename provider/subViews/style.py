import json
from typing import Callable

from django.http.request import QueryDict
from django.shortcuts import get_list_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from account.permissions import CanAdministrate
from geosmBackend.cuserViews import (
    ListAPIView,
    ListCreateAPIView,
    MultipleFieldLookupListMixin,
    RetrieveUpdateDestroyAPIView,
)
from provider.qgis.customStyleHandler import CustomStyleHandler, ResponseCustomStyle

# Create your views here.
from ..models import Custom_style, Style
from ..serializers import CustomStyleSerializer, styleProviderSerializer


class ListCustomStyle(MultipleFieldLookupListMixin, ListAPIView):
    queryset = Custom_style.objects.all()
    serializer_class = CustomStyleSerializer
    permission_classes = [CanAdministrate]
    lookup_fields = ["geometry_type"]
    model = Custom_style

    @swagger_auto_schema(
        operation_summary="List all  Custom styles",
        responses={200: CustomStyleSerializer(many=True)},
        tags=["Provider style"],
    )
    def get(self, request, *args, **kwargs):
        """List all  Custom styles"""
        return super(ListCustomStyle, self).get(request, *args, **kwargs)


class RetrieveUpdateDestroyStyleView(RetrieveUpdateDestroyAPIView):
    queryset = Style.objects.all()
    serializer_class = styleProviderSerializer
    permission_classes = [CanAdministrate]
    parser_class = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary="Delete a Style of a provider",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        tags=["Provider style"],
    )
    def delete(self, request, *args, **kwargs):
        """Delete a Style of a provider"""
        return super(RetrieveUpdateDestroyStyleView, self).delete(
            request, *args, **kwargs
        )

    @swagger_auto_schema(
        operation_summary="Partially Update a Style of a provider",
        responses={200: styleProviderSerializer()},
        tags=["Provider style"],
    )
    def patch(self, request, *args, **kwargs):
        """Partially Update a Style of a provider"""
        return super(RetrieveUpdateDestroyStyleView, self).partial_update(
            request, *args, **kwargs
        )

    @swagger_auto_schema(
        operation_summary="Update a Style of a provider",
        responses={200: styleProviderSerializer()},
        tags=["Provider style"],
    )
    def put(self, request, *args, **kwargs):
        """Update a Style of a provider"""
        return super(RetrieveUpdateDestroyStyleView, self).put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get a Style of a provider",
        responses={200: styleProviderSerializer()},
        tags=["Provider style"],
    )
    def get(self, request, *args, **kwargs):
        """Get a Style of a provider"""
        return super(RetrieveUpdateDestroyStyleView, self).get(request, *args, **kwargs)


class ListCreateStyleView(ListCreateAPIView):
    queryset = Style.objects.all()
    serializer_class = styleProviderSerializer
    permission_classes = [CanAdministrate]
    parser_class = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary="Create a new style on a provider",
        responses={200: styleProviderSerializer()},
        tags=["Provider style"],
    )
    def post(self, request, provider_vector_id, *args, **kwargs):
        """Create a new style on a provider"""

        query_dict = QueryDict("", mutable=True)
        query_dict.update(self.request.data)

        if query_dict.get("custom_style_id", None):
            customStyleHandler = CustomStyleHandler()
            custom_style: Custom_style = Custom_style.objects.get(
                pk=request.data["custom_style_id"]
            )
            customStyleFunction: Callable[[QueryDict], ResponseCustomStyle] = getattr(
                customStyleHandler, custom_style.function_name
            )

            response = customStyleFunction(query_dict)
            for key in list(request.data):
                if key not in ["name", "provider_vector_id", "custom_style_id", "icon"]:
                    del request.data[key]

            request.data["qml_file"] = response.qml_file
            request.data["parameters"] = json.dumps(response.parameters)

        op_serializer = styleProviderSerializer(data=request.data)
        op_serializer.is_valid(raise_exception=True)

        op_serializer.save()
        return Response(op_serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Retrieve all Styles of a provider",
        responses={200: styleProviderSerializer(many=True)},
        tags=["Provider style"],
    )
    def get(self, request, provider_vector_id, *args, **kwargs):
        """Retrieve all Styles of a provider"""
        styles = get_list_or_404(
            Style.objects.all(), provider_vector_id=provider_vector_id
        )
        op_serializer = styleProviderSerializer(instance=styles, many=True)
        return Response(op_serializer.data, status=status.HTTP_200_OK)
