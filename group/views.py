from django.shortcuts import render

# Create your views here.
from .models import Icon, Map, Group, Sub, Layer, Default_map, Layer_provider_style, Tags, Metadata
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.generics import (ListCreateAPIView,RetrieveUpdateDestroyAPIView, RetrieveAPIView, CreateAPIView , ListAPIView)
from rest_framework import status
from django.db.models import Count
from django.shortcuts import get_list_or_404, get_object_or_404

from .serializers import IconSerializer, MapSerializer, DefaultMapSerializer, GroupSerializer, SubSerializer, LayerSerializer, LayerProviderStyleSerializer, TagsSerializer, MetadataSerializer
from collections import defaultdict
from cairosvg import svg2png
import tempfile
from django.core.files import File
from django.conf import settings
from django.db.models import Q
from functools import reduce

import operator
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

class retrieveIconView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset=Icon.objects.all()
    serializer_class=IconSerializer

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

class MapViewDetail(RetrieveUpdateDestroyAPIView):
    queryset=Map.objects.all()
    serializer_class=MapSerializer
    permission_classes=[permissions.IsAuthenticated]

class MapViewListCreate(ListCreateAPIView):
    queryset=Map.objects.all()
    serializer_class=MapSerializer
    permission_classes=[permissions.IsAuthenticated]



class GroupVieuwDetail(RetrieveUpdateDestroyAPIView):
    queryset=Group.objects.all()
    serializer_class=GroupSerializer
    permission_classes=[permissions.IsAuthenticated]

    def put(self, request, pk):
        """ update a new group """
        group = get_object_or_404(Group.objects.all(), pk=pk)
        vp_serializer = GroupSerializer(instance=group, data=request.data, partial=True)

        if 'svg_as_text' in  request.data:
            f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.png')
            fileName = f.name
            svg2png(bytestring=request.data['svg_as_text'],write_to=fileName)
            del request.data['svg_as_text']
            dataFile = open(fileName, "rb")
            request.data['icon_path'] = File(dataFile)

        if vp_serializer.is_valid():
            vp_serializer.save()
            return Response(vp_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(vp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GroupVieuwListCreate(MultipleFieldLookupListMixin, ListCreateAPIView):
    queryset=Group.objects.all()
    serializer_class=GroupSerializer
    permission_classes=[permissions.IsAuthenticated]
    lookup_fields=['map']
    model = Group

    def post(self, request, *args, **kwargs):
        """ store a new group """
        vp_serializer = GroupSerializer(data=request.data)
        
        if 'svg_as_text' in  request.data:
            f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.png')
            fileName = f.name
            svg2png(bytestring=request.data['svg_as_text'],write_to=fileName)
            del request.data['svg_as_text']
            dataFile = open(fileName, "rb")
            request.data['icon_path'] = File(dataFile)

        if vp_serializer.is_valid():
            vp_serializer.save()
            return Response(vp_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(vp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubVieuwDetail(RetrieveUpdateDestroyAPIView):
    queryset=Sub.objects.all()
    serializer_class=SubSerializer
    permission_classes=[permissions.IsAuthenticated]

class SubVieuwListCreate(MultipleFieldLookupListMixin, ListCreateAPIView):
    queryset=Sub.objects.all()
    serializer_class=SubSerializer
    permission_classes=[permissions.IsAuthenticated]
    lookup_fields=['group_id']
    model = Sub

class LayerVieuwDetail(RetrieveUpdateDestroyAPIView):
    queryset=Layer.objects.all()
    serializer_class=LayerSerializer
    permission_classes=[permissions.IsAuthenticated]

    def put(self, request, pk, format=None):
        """ update layer """
        vp_serializer = LayerSerializer(self.get_object(), data=request.data)
        
        if 'svg_as_text' in  request.data:
            f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.png')
            fileName = f.name
            svg2png(bytestring=request.data['svg_as_text'],write_to=fileName)
            del request.data['svg_as_text']
            dataFile = open(fileName, "rb")
            request.data['cercle_icon'] = File(dataFile)

        if 'svg_as_text_square' in  request.data:
            f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.png')
            fileName = f.name
            svg2png(bytestring=request.data['svg_as_text_square'],write_to=fileName)
            del request.data['svg_as_text_square']
            dataFile = open(fileName, "rb")
            request.data['square_icon'] = File(dataFile)

        if vp_serializer.is_valid():
            vp_serializer.save()
            return Response(vp_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(vp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LayerVieuwListCreate(MultipleFieldLookupListMixin, ListCreateAPIView):
    queryset=Layer.objects.all()
    serializer_class=LayerSerializer
    permission_classes=[permissions.IsAuthenticated]
    lookup_fields=['sub']
    model = Layer

    def post(self, request, *args, **kwargs):
        """ store a new group """
        vp_serializer = LayerSerializer(data=request.data)
        
        if 'svg_as_text' in  request.data:
            f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.png')
            fileName = f.name
            svg2png(bytestring=request.data['svg_as_text'],write_to=fileName)
            del request.data['svg_as_text']
            dataFile = open(fileName, "rb")
            request.data['cercle_icon'] = File(dataFile)

        if 'svg_as_text_square' in  request.data:
            f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.png')
            fileName = f.name
            svg2png(bytestring=request.data['svg_as_text_square'],write_to=fileName)
            del request.data['svg_as_text_square']
            dataFile = open(fileName, "rb")
            request.data['square_icon'] = File(dataFile)

        if vp_serializer.is_valid():
            vp_serializer.save()
            return Response(vp_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(vp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LayerProviderStyleVieuwDetail(RetrieveUpdateDestroyAPIView):
    queryset=Layer_provider_style.objects.all()
    serializer_class=LayerProviderStyleSerializer
    permission_classes=[permissions.IsAuthenticated]

class LayerProviderStyleVieuwListCreate(MultipleFieldLookupListMixin, ListCreateAPIView):
    queryset=Layer_provider_style.objects.all()
    serializer_class=LayerProviderStyleSerializer
    permission_classes=[permissions.IsAuthenticated]
    model = Layer_provider_style
    lookup_fields=['layer_id']

class LayerProviderReorderView(APIView):
    permission_classes=[permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):

        if 'reorderProviders' in  request.data:
            reorderProviders = request.data['reorderProviders']

            for provider in reorderProviders:
                layer_provider_style = get_object_or_404(Layer_provider_style.objects.all(), pk=provider['id'])
                layer_provider_style.ordre = provider['ordre']
                layer_provider_style.save()

            return Response([], status=status.HTTP_200_OK)
        else:
            return Response({'msg':" the 'reorderProviders' parameters is missing "}, status=status.HTTP_400_BAD_REQUEST)

class searchTags(APIView):
    """
        View to search tags
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        searchWord = request.data['search_word']
        responseQuerry = []
        for tag in Tags.objects.raw("SELECT * FROM group_tags WHERE strpos(unaccent(lower(name)),unaccent(lower('"+searchWord+"')))>0 Limit 20 "):
            responseQuerry.append(TagsSerializer(tag).data)

        return Response(responseQuerry,status=status.HTTP_200_OK)

class MetadataVieuwListCreate(MultipleFieldLookupMixin, RetrieveAPIView, CreateAPIView):
    queryset=Metadata.objects.all()
    serializer_class=MetadataSerializer
    permission_classes=[permissions.IsAuthenticated]
    # model = Metadata
    lookup_fields=['layer']

class MetadataVieuwDetail(RetrieveUpdateDestroyAPIView):
    queryset=Metadata.objects.all()
    serializer_class=MetadataSerializer
    permission_classes=[permissions.IsAuthenticated]