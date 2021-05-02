from django.shortcuts import render

# Create your views here.
from .models import Map, Group, Sub, Layer, Default_map, Layer_provider_style, Tags, Metadata, Base_map
from genericIcon.models import Picto
from genericIcon.managePicto import createPicto, updatePicto, ImageBox
from .subModels.icon import Icon, TagsIcon
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from geosmBackend.cuserViews import ListCreateAPIView,RetrieveUpdateDestroyAPIView, RetrieveAPIView, CreateAPIView , ListAPIView, DestroyAPIView
from rest_framework import status
from django.db.models import Count
from django.shortcuts import get_list_or_404, get_object_or_404
from django.db import transaction
from cuser.middleware import CuserMiddleware


from .serializers import BaseMapSerializer ,TagsIconSerializer, IconSerializer, MapSerializer, DefaultMapSerializer, GroupSerializer, SubSerializer, SubWithLayersSerializer,  LayerSerializer, LayerProviderStyleSerializer, TagsSerializer, MetadataSerializer
from collections import defaultdict
from cairosvg import svg2png
import tempfile
from django.core.files import File
from django.conf import settings
from django.db.models import Q
from functools import reduce

import operator

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

class retrieveIconView(EnablePartialUpdateMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset=Icon.objects.all()
    serializer_class=IconSerializer

    def put(self, request, pk):
        """ update a icon """
        icon = get_object_or_404(Icon.objects.all(), pk=pk)
        vp_serializer = IconSerializer(instance=icon, data=request.data, partial=True)

        if vp_serializer.is_valid():
            if 'tags' in request.data:
                vp_serializer.validated_data['tags'] =  request.data['tags']
            vp_serializer.save()
            return Response(vp_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(vp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
      CuserMiddleware.set_user(request.user)
      file_serializer = IconSerializer(data=request.data)
      if file_serializer.is_valid():
          if 'tags' in request.data:
            file_serializer.validated_data['tags'] =  request.data['tags']
          file_serializer.save()
          return Response(file_serializer.data, status=status.HTTP_201_CREATED)
      else:
          return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class searchIconsTags(APIView):
    """
        View to search tags
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        searchWord = request.data['search_word']
        responseQuerry = []
        for tag in TagsIcon.objects.raw("SELECT * FROM group_tagsicon WHERE strpos(unaccent(lower(name)),unaccent(lower('"+searchWord+"')))>0 Limit 20 "):
            responseQuerry.append(TagsIconSerializer(tag).data)
        return Response(responseQuerry,status=status.HTTP_200_OK)


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

        for icon  in Icon.objects.filter(tags__in=TagsIcon.objects.raw("SELECT id FROM group_tagsicon WHERE strpos(unaccent(lower(name)),unaccent(lower('"+searchWord+"')))>0 Limit 20 ")) :
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

class searchMaps(APIView):
    """
        View to search map's
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        searchWord = request.data['search_word']
        responseQuerry = []
        for map in Map.objects.raw("SELECT * FROM group_map WHERE strpos(unaccent(lower(name)),unaccent(lower('"+searchWord+"')))>0 Limit 20 "):
            responseQuerry.append(MapSerializer(map).data)

        return Response(responseQuerry,status=status.HTTP_200_OK)


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

class GroupVieuwList(MultipleFieldLookupListMixin, ListAPIView):
    queryset=Group.objects.all()
    serializer_class=GroupSerializer
    lookup_fields=['map']
    model = Group
    authentication_classes = []

class GroupVieuwListCreate(MultipleFieldLookupListMixin, CreateAPIView):
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

class SubListWithLayersView(MultipleFieldLookupListMixin, ListAPIView):
    queryset=Sub.objects.all()
    serializer_class=SubWithLayersSerializer
    authentication_classes = []
    lookup_fields=['group_id']
    model = Sub

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
            CuserMiddleware.set_user(request.user)
            for provider in reorderProviders:
                Layer_provider_style.objects.filter(pk=provider['id']).update(ordre=provider['ordre'])

            return Response([], status=status.HTTP_200_OK)
        else:
            return Response({'msg':" the 'reorderProviders' parameters is missing "}, status=status.HTTP_400_BAD_REQUEST)

class searchLayerTags(APIView):
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

class BaseMapGetDestroyVieuw(EnablePartialUpdateMixin, RetrieveUpdateDestroyAPIView):
    queryset=Base_map.objects.all()
    serializer_class=BaseMapSerializer
    permission_classes=[permissions.IsAuthenticated]

    def put(self, request, pk, format=None):
        """ update base maps """
        transaction.set_autocommit(False)
        CuserMiddleware.set_user(request.user)
        vp_serializer = BaseMapSerializer(self.get_object(), data=request.data, partial=True)

        if 'picto' in request.data:
            request.data['picto'] = {
                'raster_icon':request.data['picto']
            }
            picto = updatePicto(request.data['picto'], ImageBox(left=0, top=0, right=976, bottom=310))
            request.data['picto'] = picto.pk
          
        if vp_serializer.is_valid():
            vp_serializer.save()
            transaction.commit()
            return Response(vp_serializer.data, status=status.HTTP_201_CREATED)
        else:
            transaction.rollback()
            return Response(vp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseMapListView(MultipleFieldLookupListMixin, ListAPIView):
    queryset=Base_map.objects.all()
    serializer_class=BaseMapSerializer
    authentication_classes = []
    lookup_fields=['']
    model = Base_map

class BaseMapView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """ store a new base map """
        CuserMiddleware.set_user(request.user)

        if 'picto' in request.data:

            transaction.set_autocommit(False)
   
            request.data['picto'] = {
                'raster_icon':request.data['picto']
            }
            # print(request.data['picto'])
            picto = createPicto(request.data['picto'], ImageBox(left=0, top=0, right=976, bottom=310) )

            request.data['picto'] = picto.pk

            vp_serializer = BaseMapSerializer(data=request.data)

            if vp_serializer.is_valid():
                vp_serializer.save()
                transaction.commit()
                return Response(vp_serializer.data, status=status.HTTP_201_CREATED)
            else:
                transaction.rollback()
                return Response(vp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response(" 'picto' field is required", status=status.HTTP_400_BAD_REQUEST)

