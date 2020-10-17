from django.shortcuts import render

# Create your views here.
from .models import Icon
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Count

from .serializers import IconSerializer
from collections import defaultdict


class listIconByCategory(APIView):
    """
        View to list icons by group
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        groups = defaultdict(list)
        for icon in Icon.objects.all():
            groups[icon.category].append(IconSerializer(icon).data)

        return Response(groups,status=status.HTTP_200_OK)

class iconUploadView(APIView):
    """
        View to upload icons
    """
    parser_class = (FileUploadParser,)
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
      file_serializer = IconSerializer(data=request.data)
      if file_serializer.is_valid():
          file_serializer.save()
          return Response(file_serializer.data, status=status.HTTP_201_CREATED)
      else:
          return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class searchIcon(APIView):
    """
        View to search icon
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        searchWord = request.data['search_word']
        responseQuerry = []
        for icon in Icon.objects.raw("SELECT * FROM group_icon WHERE strpos(unaccent(lower(name)),unaccent(lower('"+searchWord+"')))>0 Limit 20 "):
            responseQuerry.append(IconSerializer(icon).data)

        return Response(responseQuerry,status=status.HTTP_200_OK)

        