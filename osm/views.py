from django.shortcuts import render
import traceback
from .validateOsmQuerry import validateOsmQuerry
from .models import Querry
from provider.models import Vector
from provider.manageOsmDataSource import manageOsmDataSource
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from geosmBackend.cuserViews import (EnablePartialUpdateMixin ,UpdateAPIView, RetrieveUpdateAPIView, CreateAPIView)
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Count
from django.shortcuts import get_list_or_404, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from geosmBackend.type import httpResponse
from cuser.middleware import CuserMiddleware
from drf_yasg.utils import swagger_auto_schema
from .serializers import osmQuerrySerializer
from collections import defaultdict
# Create your views here.



class CreateOsmQuerryView(CreateAPIView):
   
    queryset=Querry.objects.all()
    serializer_class=osmQuerrySerializer
    permission_classes=[permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={200: osmQuerrySerializer()},
        tags=['OSM provider'],
    )
    def post(self, request, *args, **kwargs):
        """ Create an osm provider  """
        return super(CreateOsmQuerryView, self).post(request, *args, **kwargs)

class osmQuerryView(APIView):
    """
        View to add an osm querry
    """
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        responses={200: osmQuerrySerializer()},
        tags=['OSM provider'],
    )
    def get(self, request, pk):
        """ Retrieve an osm provider by his primary key """
        saved_querry = get_object_or_404(Querry.objects.all(), pk=pk)
        op_serializer = osmQuerrySerializer(instance=saved_querry, data=request.data, partial=True)
        if op_serializer.is_valid(raise_exception=True):
            return Response(op_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(httpResponse(error=True,msg=op_serializer.errors).toJson(), status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        query_serializer=osmQuerrySerializer,
        responses={200: osmQuerrySerializer()},
        tags=['OSM provider'],
    )
    def put(self, request, pk):
        """ update an osm querry """
        CuserMiddleware.set_user(request.user)
        saved_querry = get_object_or_404(Querry.objects.all(), pk=pk)
        op_serializer = osmQuerrySerializer(instance=saved_querry, data=request.data, partial=True)
        if op_serializer.is_valid(raise_exception=True):
            try:
                op_serializer.save()
                return Response(op_serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(httpResponse(error=True,msg=str(e)).toJson(), status=status.HTTP_400_BAD_REQUEST)
           
        else:
            return Response(op_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
