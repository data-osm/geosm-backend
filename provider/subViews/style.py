from django.http.request import QueryDict
from django.shortcuts import render
from typing import Callable, Any
# Create your views here.
from ..models import Vector, Style, Custom_style
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser
from rest_framework.response import Response
from geosmBackend.cuserViews import (CreateAPIView, ListCreateAPIView,RetrieveUpdateDestroyAPIView, ListAPIView, EnablePartialUpdateMixin, MultipleFieldLookupListMixin, MultipleFieldLookupMixin)
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Count
from geosmBackend.type import httpResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from cuser.middleware import CuserMiddleware
import json
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import tempfile
from django.core.files import File
from django.conf import settings

from ..serializers import  styleProviderSerializer, CustomStyleSerializer
from collections import defaultdict
import traceback
from functools import reduce
import operator
from django.db.models import Q

from ..qgis.customStyle import cluster
from provider.qgis.customStyleHandler import CustomStyleHandler, ResponseCustomStyle

class ListCustomStyle(MultipleFieldLookupListMixin, ListAPIView):
    queryset=Custom_style.objects.all()
    serializer_class=CustomStyleSerializer
    permission_classes=[permissions.IsAuthenticated]
    lookup_fields=['geometry_type']
    model = Custom_style

    @swagger_auto_schema(
        operation_summary='List all  Custom styles',
        responses={200: CustomStyleSerializer(many=True)},
        tags=['Provider style'],
    )
    def get(self, request, *args, **kwargs):
        """ List all  Custom styles  """
        return super(ListCustomStyle, self).get(request, *args, **kwargs)

class StyleDetailView(EnablePartialUpdateMixin, RetrieveUpdateDestroyAPIView):
    queryset=Style.objects.all()
    serializer_class=styleProviderSerializer
    permission_classes=[permissions.IsAuthenticated]
    parser_class = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary='Delete a Style of a provider',
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        tags=['Provider style'],
    )
    def delete(self, request, *args, **kwargs):
        """ Delete a Style of a provider  """
        return super(StyleDetailView, self).delete(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Partially Update a Style of a provider',
        responses={200: styleProviderSerializer()},
        tags=['Provider style'],
    )
    def patch(self, request, *args, **kwargs):
        """Partially Update a Style of a provider """
        return super(StyleDetailView, self).patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Update a Style of a provider',
        responses={200: styleProviderSerializer()},
        tags=['Provider style'],
    )
    def put(self, request, *args, **kwargs):
        """Update a Style of a provider"""
        return super(StyleDetailView, self).put(request, *args, **kwargs)

   
class ListStyleView( ListCreateAPIView):
    queryset=Style.objects.all()
    serializer_class=styleProviderSerializer
    permission_classes=[permissions.IsAuthenticated]
    parser_class = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary='Create a new style on a provider',
        responses={200: styleProviderSerializer()},
        tags=['Provider style'],
    )
    def post(self, request, provider_vector_id,*args, **kwargs):
        """ Create a new style on a provider"""
        op_serializer = styleProviderSerializer(data=request.data)
        CuserMiddleware.set_user(request.user)

        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.request.data)

        if query_dict.get('custom_style_id', None) :
            customStyleHandler = CustomStyleHandler()
            custom_style:Custom_style = Custom_style.objects.get(pk=request.data['custom_style_id'])
            customStyleFunction:Callable[[QueryDict],ResponseCustomStyle] = getattr(customStyleHandler,custom_style.fucntion_name)

            response = customStyleFunction(query_dict)
            for key in list(request.data):
                if key not in ['name', 'provider_vector_id', 'custom_style_id','icon']:
                    del request.data[key]

            request.data['qml_file']  = response.qml_file
            request.data['parameters'] = json.dumps(response.parameter) 


        if op_serializer.is_valid():
            try:
                op_serializer.save()
                return Response(op_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(httpResponse(error=True,msg=str(e)).toJson(), status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(op_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary='Retrieve all Styles of a provider',
        responses={200: styleProviderSerializer(many=True)},
        tags=['Provider style'],
    )
    def get(self, request, provider_vector_id, *args, **kwargs):
        """Retrieve all Styles of a provider """
        styles = get_list_or_404(Style.objects.all(), provider_vector_id=provider_vector_id)
        op_serializer = styleProviderSerializer(instance=styles, many=True)
        return Response(op_serializer.data, status=status.HTTP_200_OK)
