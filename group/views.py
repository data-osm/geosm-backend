from django.shortcuts import render

# Create your views here.
from .models import Icon
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializers import IconSerializer


class IconViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows icons to be viewed or edited.
    """
    queryset = Icon.objects.all()
    serializer_class = IconSerializer
    permission_classes = [permissions.IsAuthenticated]

class categoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows list of all category icons
    """
    queryset = Icon.objects.values('category').distinct()
    serializer_class = IconSerializer
    permission_classes = [permissions.IsAuthenticated]


class IconUploadView(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request, *args, **kwargs):

      file_serializer = IconSerializer(data=request.data)
    #   file_serializer.is_valid()
    #   return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      if file_serializer.is_valid():
          file_serializer.save()
          return Response(file_serializer.data, status=status.HTTP_201_CREATED)
      else:
          return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
