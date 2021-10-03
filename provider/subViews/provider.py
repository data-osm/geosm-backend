from django.shortcuts import render

# Create your views here.
from ..models import Vector, Style
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser
from rest_framework.response import Response
from geosmBackend.cuserViews import (ListCreateAPIView,RetrieveUpdateDestroyAPIView, ListAPIView)
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Count
from geosmBackend.type import httpResponse
from cuser.middleware import CuserMiddleware

from cairosvg import svg2png
import tempfile
from django.core.files import File
from django.conf import settings

from ..serializers import VectorProviderSerializer, VectorProviderWithStyleSerializer
from collections import defaultdict
import traceback

from ..qgis.customStyle import cluster

class EnablePartialUpdateMixin:
    """Enable partial updates
    https://tech.serhatteker.com/post/2020-09/enable-partial-update-drf/

    Override partial kwargs in UpdateModelMixin class
    https://github.com/encode/django-rest-framework/blob/91916a4db14cd6a06aca13fb9a46fc667f6c0682/rest_framework/mixins.py#L64
    """
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
        

class vectorProviderView(APIView):
    """
        View to list all vector provider, add a vector provider usernames = [user.username for user in User.objects.all()]
        return Response(usernames)
    """
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        """ get all vector provider """
        return Response([VectorProviderSerializer(vector).data for vector in Vector.objects.all()],status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        """ store a new vector providor """
        CuserMiddleware.set_user(request.user)
        vp_serializer = VectorProviderSerializer(data=request.data)

        if vp_serializer.is_valid():
            vp_serializer.save()
            return Response(vp_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(vp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """ Delete vector providers """
        CuserMiddleware.set_user(request.user)
        try:
            provider_vector_ids= request.data['provider_vector_ids']
            vector_providers = Vector.objects.filter(pk__in=provider_vector_ids)
            vector_providers.delete()
            return Response(httpResponse(False).__dict__,status=status.HTTP_200_OK)
        except :
            traceback.print_exc()
            return Response(httpResponse(True,'An unexpected error has occurred').__dict__,status=status.HTTP_400_BAD_REQUEST)

class searchVectorProvider(APIView):
    """
        View to search a vector provider
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        CuserMiddleware.set_user(request.user)
        searchWord = request.data['search_word']
        responseQuerry = []
        for vector in Vector.objects.raw("SELECT * FROM provider_vector WHERE strpos(unaccent(lower(name)),unaccent(lower('"+searchWord+"')))>0 Limit 20 "):
            responseQuerry.append(VectorProviderSerializer(vector).data)

        return Response(responseQuerry,status=status.HTTP_200_OK)


class vectorProviderDetailView(EnablePartialUpdateMixin, RetrieveUpdateDestroyAPIView):
    """ View get a vector provider, update or delete it """
    queryset=Vector.objects.all()
    serializer_class=VectorProviderSerializer
    permission_classes=[permissions.IsAuthenticated]

class vectorProviderWithStyleDetailView(ListAPIView):
    """ View get a vector provider with a style """
    queryset=Vector.objects.all()
    serializer_class=VectorProviderWithStyleSerializer
    permission_classes=[permissions.IsAuthenticated]
