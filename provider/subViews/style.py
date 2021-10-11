from django.http.request import QueryDict
from django.shortcuts import render
from typing import Callable, Any
# Create your views here.
from ..models import Vector, Style, Custom_style
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser
from rest_framework.response import Response
from geosmBackend.cuserViews import (ListCreateAPIView,RetrieveUpdateDestroyAPIView, ListAPIView)
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Count
from geosmBackend.type import httpResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from cuser.middleware import CuserMiddleware
import json
from cairosvg import svg2png
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

class EnablePartialUpdateMixin:
    """Enable partial updates
    https://tech.serhatteker.com/post/2020-09/enable-partial-update-drf/

    Override partial kwargs in UpdateModelMixin class
    https://github.com/encode/django-rest-framework/blob/91916a4db14cd6a06aca13fb9a46fc667f6c0682/rest_framework/mixins.py#L64
    """
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

class MultipleFieldLookupMixin(object):
    def get_object(self):
        queryset = self.get_queryset()             # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}
        for field in self.lookup_fields:
            filter[field] = self.request.query_params.get(field) 
            # self.kwargs[field]
        q = reduce(operator.or_, (Q(x) for x in filter.items()))
        return get_object_or_404(queryset, q)

class MultipleFieldLookupListMixin:
    """
    Apply this mixin to any view or viewset to get multiple field filtering
    based on a `lookup_fields` attribute, instead of the default single field filtering.
    """
    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset=self.model.objects.all()
        filter = {}
        for field in self.lookup_fields:
            if self.request.query_params.get(field, None):
                filter[field] = self.request.query_params.get(field)
        queryset = queryset.filter(**filter)
        return queryset
class ListCustomStyle(MultipleFieldLookupListMixin, ListAPIView):
    queryset=Custom_style.objects.all()
    serializer_class=CustomStyleSerializer
    permission_classes=[permissions.IsAuthenticated]
    lookup_fields=['geometry_type']
    model = Custom_style

class styleView(APIView):
    """View to list style of a provider, delete, add or edit style"""
    permission_classes = [permissions.IsAuthenticated]
    parser_class = [MultiPartParser, FormParser]
    def get(self, request, provider_vector_id):
        """ get all styles of a provider"""
        styles = get_list_or_404(Style.objects.all(), provider_vector_id=provider_vector_id)
        op_serializer = styleProviderSerializer(instance=styles, many=True)
        return Response(op_serializer.data, status=status.HTTP_200_OK)
       
    def put(self, request, pk):
        """ update a style """
        CuserMiddleware.set_user(request.user)
        style = get_object_or_404(Style.objects.all(), pk=pk)
        op_serializer = styleProviderSerializer(instance=style, data=request.data, partial=True)
        if op_serializer.is_valid(raise_exception=False):
            try:
                op_serializer.save()
                return Response(op_serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(httpResponse(error=True,msg=str(e)).toJson(), status=status.HTTP_400_BAD_REQUEST)
           
        else:
            return Response(op_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, *args, **kwargs):
        """ store a new style"""
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

    def delete(self, request, pk):
        """ Delete a style """
        CuserMiddleware.set_user(request.user)
        try:
            style = get_object_or_404(Style.objects.all(), pk=pk)
            style.delete()
            return Response(httpResponse(False).__dict__,status=status.HTTP_200_OK)
        except Exception as e :
            traceback.print_exc()
            return Response(httpResponse(error=True,msg=str(e)).toJson(),status=status.HTTP_400_BAD_REQUEST)

