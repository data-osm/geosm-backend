from django.shortcuts import render
from django.db.models import Count
from django.core.files import File
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import filters
from cuser.middleware import CuserMiddleware
from cairosvg import svg2png
import tempfile
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from collections import defaultdict
import traceback
from geosmBackend.type import httpResponse
from geosmBackend.cuserViews import (CreateAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView,
                                     EnablePartialUpdateMixin)
from ..serializers import VectorProviderSerializer, VectorProviderWithStyleSerializer
from ..models import Vector, Style
from ..qgis.customStyle import cluster


class ListVectorProviderView(ListCreateAPIView):
    queryset = Vector.objects.all()
    serializer_class = VectorProviderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = '__all__'
    # ordering = ['name']
    # filterset_fields = ['geometry_type']

    @swagger_auto_schema(
        operation_summary='Returns all providers',
        responses={200: VectorProviderSerializer(many=True)},
        tags=['Providers'],
    )
    def get(self, request, *args, **kwargs):
        """ List all provider  """
        return super(ListVectorProviderView, self).get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Add a new provider',
        responses={200: VectorProviderSerializer()},
        tags=['Providers'],
    )
    def post(self, request, *args, **kwargs):
        """ Create a provider  """
        return super(ListVectorProviderView, self).post(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Deletes many providers',
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'provider_vector_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description='List of provider_vector_id to delete',
                    items={'type': openapi.TYPE_INTEGER},
                )
            }
        ),
        tags=['Providers'],
    )
    def delete(self, request, *args, **kwargs):
        """ Delete many vector providers """
        CuserMiddleware.set_user(request.user)
        try:
            provider_vector_ids = request.data['provider_vector_ids']
            vector_providers = Vector.objects.filter(pk__in=provider_vector_ids)
            vector_providers.delete()
            return Response(httpResponse(False).__dict__, status=status.HTTP_200_OK)
        except:
            traceback.print_exc()
            return Response(httpResponse(True, 'An unexpected error has occurred').__dict__,
                            status=status.HTTP_400_BAD_REQUEST)


class VectorProviderDetailView(EnablePartialUpdateMixin, RetrieveUpdateDestroyAPIView):
    queryset = Vector.objects.all()
    serializer_class = VectorProviderSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Deletes a provider by id',
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        tags=['Providers'],
    )
    def delete(self, request, *args, **kwargs):
        """ Delete a provider  """
        return super(VectorProviderDetailView, self).delete(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Partially update a provider',
        responses={200: VectorProviderSerializer()},
        tags=['Providers'],
    )
    def patch(self, request, *args, **kwargs):
        """Partially Update Provider"""
        return super(VectorProviderDetailView, self).patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Update a provider',
        responses={200: VectorProviderSerializer()},
        tags=['Providers'],
    )
    def put(self, request, *args, **kwargs):
        """Update Provider"""
        return super(VectorProviderDetailView, self).put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Finds a provider',
        responses={200: VectorProviderSerializer()},
        tags=['Providers'],
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a provider"""
        return super(VectorProviderDetailView, self).get(request, *args, **kwargs)


class searchVectorProvider(APIView):
    """
        View to search a vector provider
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Search provider by keywords',
        responses={200: VectorProviderSerializer(many=True)},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'search_word': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The search key word'
                )
            }
        ),
        tags=['Providers'],
    )
    def post(self, request, *args, **kwargs):
        """ Search a vector provider """
        CuserMiddleware.set_user(request.user)
        searchWord = request.data['search_word']
        responseQuerry = []
        for vector in Vector.objects.raw(
                "SELECT * FROM provider_vector WHERE strpos(unaccent(lower(name)),unaccent(lower('" + searchWord + "')))>0 Limit 20 "):
            responseQuerry.append(VectorProviderSerializer(vector).data)

        return Response(responseQuerry, status=status.HTTP_200_OK)


class vectorProviderWithStyleDetailView(ListAPIView):
    """ View get a vector provider with a style """
    queryset = Vector.objects.all()
    serializer_class = VectorProviderWithStyleSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Gets all providers with style',
        responses={200: VectorProviderWithStyleSerializer(many=True)},
        tags=['Providers'],
    )
    def get(self, request, *args, **kwargs):
        """List all provider with their style"""
        return super(vectorProviderWithStyleDetailView, self).get(request, *args, **kwargs)
