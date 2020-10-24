from django.shortcuts import render

from .validateOsmQuerry import validateOsmQuerry
from .models import Querry
from group.models import Vector
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.generics import (ListCreateAPIView,RetrieveUpdateDestroyAPIView,)
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Count
from django.shortcuts import get_list_or_404, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist


from .serializers import osmQuerrySerializer
from collections import defaultdict
# Create your views here.

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def isOsmQuerryValidate(osmQuerry:Querry) ->dict:
    try:
        vector_provider = Vector.objects.get(provider_vector_id=osmQuerry.provider_vector_id)
        osmValidation = validateOsmQuerry(osmQuerry.where, osmQuerry.select, vector_provider.geometry_type)
        if osmValidation.isValid():
            return  {
                'error':False
            }
        else:
          
            return {
                'error':True,
                'msg':' The osm querry is not correct ',
                'description':osmValidation.error
            }

    except ObjectDoesNotExist as identifier:
        return {
            'error':True,
            'msg':' Can not find the vector provider of this osm querry',
            'description':identifier
        }

class osmQuerryView(APIView):
    """
        View to add an osm querry
    """
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, pk):
        """ get an osm provider """
        saved_querry = get_object_or_404(Querry.objects.all(), pk=pk)
        op_serializer = osmQuerrySerializer(instance=saved_querry, data=request.data, partial=True)
        if op_serializer.is_valid(raise_exception=True):
            return Response(op_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(op_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, pk):
        """ update an osm querry """
        saved_querry = get_object_or_404(Querry.objects.all(), pk=pk)
        op_serializer = osmQuerrySerializer(instance=saved_querry, data=request.data, partial=True)
        if op_serializer.is_valid(raise_exception=True):
            validation = isOsmQuerryValidate(Struct(**request.data))
            if validation['error'] == False:
                article_saved = op_serializer.save()
                return Response(op_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(validation, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(op_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def post(self, request, *args, **kwargs):
        """ store a new osm querry"""
        op_serializer = osmQuerrySerializer(data=request.data)
        if 'select' not in  request.data or request.data['select'] is None:
            request._mutable = True
            request.data.__setitem__('select','A.osm_id,A.name,A.amenity,hstore_to_json(A.tags), ST_TRANSFORM(A.way,4326) as geom')

        if op_serializer.is_valid():
            validation = isOsmQuerryValidate(Struct(**request.data))
            if validation['error'] == False:
                op_serializer.save()
                return Response(op_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(validation, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(op_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

