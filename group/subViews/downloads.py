from io import BytesIO
from typing import List
from django.db.backends.utils import CursorWrapper
from django.http.request import QueryDict
from django.shortcuts import render
from rest_framework.exceptions import NotAuthenticated
from django.db import connections, transaction

from provider.qgis.manageVectorLayer import saveQMLtoGeoPackage

# Create your views here.
from ..models import Map, Group, Sub, Layer, Default_map, Layer_provider_style, Tags, Metadata, Base_map
from rest_framework.response import Response
from rest_framework.views import APIView
from geosmBackend.cuserViews import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView, CreateAPIView, \
    ListAPIView, MultipleFieldLookupMixin, EnablePartialUpdateMixin, MultipleFieldLookupListMixin
from rest_framework import status
from django.db.models import Count
from django.shortcuts import get_list_or_404, get_object_or_404
from django.http import HttpResponse, StreamingHttpResponse

from cuser.middleware import CuserMiddleware
from uuid import uuid4

from provider.models import Vector, Style
from provider.serializers import VectorProviderSerializer

from ..serializers import SubWithGroupSerializer, BaseMapSerializer, TagsIconSerializer, IconSerializer, MapSerializer, \
    DefaultMapSerializer, GroupSerializer, SubSerializer, SubWithLayersSerializer, LayerSerializer, \
    LayerProviderStyleSerializer, TagsSerializer, MetadataSerializer
from collections import defaultdict
from cairosvg import svg2png
import tempfile
from django.core.files import File
from django.conf import settings
from django.db.models import Q
from functools import reduce
from os.path import join, relpath
import shutil
from wsgiref.util import FileWrapper
import operator
import ogr
from ogr import DataSource, Layer as OgrLayer
from pathlib import Path
from zipfile import ZipFile
from os import walk, remove
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from osm.models import Querry, SimpleQuerry

class CountFeaturesInGeometry(APIView):
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary='Count features of a provider ',
        responses={200: 'this should not crash (response object with no schema)'},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'provider_vector_id': {'type': openapi.TYPE_INTEGER},
                'table_id': {'type': openapi.TYPE_INTEGER},
                'layer_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description='The array of all',
                    items={
                        'type': openapi.TYPE_INTEGER
                    },
                )
            }
        ),
        tags=['Download data'],
    )
    def post(self, request, *args, **kwargs):

        try:
            provider_vector_id = request.data['provider_vector_id']
            table_id = request.data['table_id']
        except:
            provider_vector_id = None

        try:
            # layer_ids = [11]
            layer_ids = request.data['layer_ids']
        except:
            return Response({'message': "array field layer_ids is required"}, status=status.HTTP_400_BAD_REQUEST)

        layer_provider_styles: List[Layer_provider_style] = get_list_or_404(
            Layer_provider_style.objects.select_related('vp_id').all(), layer_id__in=layer_ids)
        if provider_vector_id is not None:
            boundaryVector: Vector = get_object_or_404(Vector.objects.all(), pk=provider_vector_id)

            def countFeatyure_(cursor: CursorWrapper, vector: Vector):
                cursor.execute(
                    "SELECT count(A.osm_id) as count FROM " + vector.shema + "." + vector.table + " AS A INNER JOIN  " + boundaryVector.shema + "." + boundaryVector.table + " AS B  ON ST_Intersects(st_transform(A.geom,3857),st_transform(B.geom,3857)) WHERE B.osm_id=" + str(
                        table_id))
                return cursor.fetchone()[0]

            with connection.cursor() as cursor:
                return Response([{'count': countFeatyure_(cursor, lp.vp_id),
                                  'vector': VectorProviderSerializer(lp.vp_id).data, 'layer_id': lp.layer_id.layer_id,
                                  'layer_name': lp.layer_id.name} for lp in layer_provider_styles],
                                status=status.HTTP_200_OK)
        else:
            return Response([{'count': lp.vp_id.count, 'vector': VectorProviderSerializer(lp.vp_id).data,
                              'layer_id': lp.layer_id.layer_id, 'layer_name': lp.layer_id.name} for lp in
                             layer_provider_styles], status=status.HTTP_200_OK)

class DownloadFeatureById(APIView):
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary='Download a feature from a provider by id  ',
        responses={200: 'this should not crash (response object with no schema)'},
       manual_parameters=[
            openapi.Parameter('provider_vector_id', openapi.IN_QUERY, description="vector id we want to download", type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('feature_id', openapi.IN_QUERY, description="id of the feature to download", type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('driver', openapi.IN_QUERY, description='The format, default is "shp"', type=openapi.TYPE_STRING,required=False),
            openapi.Parameter('provider_style_id', openapi.IN_QUERY, description='style of vector we want to download', type=openapi.TYPE_INTEGER,required=False),
        ],
        tags=['Download data'],
    )

    def get(self, request, *args, **kwargs):
        try:
            provider_vector_id: int = request.GET['provider_vector_id']
        except:
            return Response({'message': "int field provider_vector_id is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            feature_id: int = request.GET['feature_id']
        except:
            return Response({'message': "int field feature_id is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            format: str = request.GET['driver']
        except:
            format = 'shp'

        try:
            provider_style_id: int = request.GET['provider_style_id']
            style:Style = Style.objects.filter(pk=provider_style_id).filter(provider_vector_id=provider_vector_id).get()
        except:
            style = None

        ogrParams = getOgrDriver(format)
        extention = ogrParams['extention']
        driver = ogrParams['driver']
        content_type = ogrParams['content_type']

        provider: Vector = get_object_or_404(Vector.objects.all(), pk=provider_vector_id)
        try:
            source =get_object_or_404(Querry.objects.all(), provider_vector_id=provider_vector_id)
        except:
            pass
        try:
            source =get_object_or_404(SimpleQuerry.objects.all(), provider_vector_id=provider_vector_id)
        except:
            pass

        datasource: DataSource = ogr.Open(
            "PG:host=" + settings.DATABASES[source.connection]['HOST'] + " port=" + settings.DATABASES[source.connection][
                'PORT'] + " dbname=" + settings.DATABASES[source.connection]['NAME'] + " user=" + settings.DATABASES[source.connection][
                'USER'] + " password=" + settings.DATABASES[source.connection]['PASSWORD'], 0)

        layer: OgrLayer = datasource.ExecuteSQL(
                "SELECT * FROM " + provider.shema + "." + provider.table + " where osm_id="+str(feature_id))
        connection = connections[source.connection]
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM " + provider.shema + "." + provider.table+ " where osm_id="+str(feature_id) )
            nameShapefile = provider.name + ' - ' +str(cursor.fetchone()[0])

        tempDir = tempfile.TemporaryDirectory(dir=settings.TEMP_URL)
        directory_for_files = tempDir.name
        Path(directory_for_files).mkdir(parents=True, exist_ok=True)

        outShapefile = join(directory_for_files, nameShapefile + extention)
        outDriver = ogr.GetDriverByName(driver)
        outDataSource = outDriver.CreateDataSource(outShapefile)
        outDataSource.CopyLayer(layer, nameShapefile, [])
        outDataSource.SyncToDisk()

        if format == 'shp':
            temp = BytesIO()
            with ZipFile(temp, 'w') as zipObj:
                for root, dirs, files in walk(directory_for_files):
                    for file in files:
                        zipObj.write(join(root, file), relpath(join(root, file), join(directory_for_files)))
                if style is not None:
                    zipObj.write(join(settings.MEDIA_ROOT,style.qml_file.path),nameShapefile+'.qml')

            response = StreamingHttpResponse(FileWrapper(temp), content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename="' + nameShapefile + '.zip"'
            response['Content-Length'] = temp.tell()

            temp.seek(0)

        else:
            if format == 'gpkg' and style is not None:
                try:
                    saveQMLtoGeoPackage(outShapefile, join(settings.MEDIA_ROOT,style.qml_file.path))
                except:
                    pass
                
            response = StreamingHttpResponse(open(outShapefile, 'rb'), content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename="' + nameShapefile + extention + '"'

        # Count the number of times the provider is downloaded
        provider.increment_download_number()

        tempDir.cleanup()
        return response

class DownloadFeaturesInGeometry(APIView):
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary='Download features of a provider',
        manual_parameters=[
            openapi.Parameter('provider_vector_id', openapi.IN_QUERY, description=" boundary vector id", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('table_id', openapi.IN_QUERY, description="id of the boundary in his vector table", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('provider_vector_id_target', openapi.IN_QUERY, description="vector id we want to download", type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('provider_style_id_target', openapi.IN_QUERY, description='style of vector we want to download', type=openapi.TYPE_INTEGER,required=False),
            openapi.Parameter('driver', openapi.IN_QUERY, description='The format, default is "shp"', type=openapi.TYPE_STRING,required=False),
        ],
        responses={200: 'this should not crash (response object with no schema)'},
        tags=['Download data'],
    )
    def get(self, request, *args, **kwargs):
        try:
            provider_vector_id_target: int = request.GET['provider_vector_id_target']
            """ layer vector id we want to download """
        except:
            return Response({'message': "int field provider_vector_id_target is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            provider_vector_id: int = request.GET['provider_vector_id']
            """ boundary vector id """
            table_id = request.GET['table_id']
            """ id of the boundary in his vector table """
            Vector.objects.filter(pk=provider_vector_id)
        except:
            provider_vector_id = None

        try:
            format: str = request.GET['driver']
        except:
            format = 'shp'

        try:
            provider_style_id_target: int = request.GET['provider_style_id_target']
            style:Style = Style.objects.filter(pk=provider_style_id_target).filter(provider_vector_id=provider_vector_id_target).get()
        except:
            style = None

        ogrParams = getOgrDriver(format)
        extention = ogrParams['extention']
        driver = ogrParams['driver']
        content_type = ogrParams['content_type']

        targetVector: Vector = get_object_or_404(Vector.objects.all(), pk=provider_vector_id_target)
        try:
            source =get_object_or_404(Querry.objects.all(), provider_vector_id=provider_vector_id_target)
        except:
            pass
        try:
            source =get_object_or_404(SimpleQuerry.objects.all(), provider_vector_id=provider_vector_id_target)
        except:
            pass

        datasource: DataSource = ogr.Open(
            "PG:host=" + settings.DATABASES[source.connection]['HOST'] + " port=" + settings.DATABASES[source.connection][
                'PORT'] + " dbname=" + settings.DATABASES[source.connection]['NAME'] + " user=" + settings.DATABASES[source.connection][
                'USER'] + " password=" + settings.DATABASES[source.connection]['PASSWORD'], 0)
        
        if provider_vector_id is not None:
            boundaryVector: Vector = get_object_or_404(Vector.objects.all(), pk=provider_vector_id)
            layer: OgrLayer = datasource.ExecuteSQL(
                "SELECT A.* FROM " + targetVector.shema + "." + targetVector.table + " AS A INNER JOIN  " + boundaryVector.shema + "." + boundaryVector.table + " AS B  ON ST_Intersects(st_transform(A.geom,3857),st_transform(B.geom,3857)) WHERE B.osm_id=" + str(
                    table_id))
            nameShapefile = targetVector.name + ' - ' + boundaryVector.name
        else:
            layer: OgrLayer = datasource.ExecuteSQL(
                "SELECT * FROM " + targetVector.shema + "." + targetVector.table )
            nameShapefile = targetVector.name

        tempDir = tempfile.TemporaryDirectory(dir=settings.TEMP_URL)
        directory_for_files = tempDir.name
        Path(directory_for_files).mkdir(parents=True, exist_ok=True)

        outShapefile = join(directory_for_files, nameShapefile + extention)
        outDriver = ogr.GetDriverByName(driver)
        outDataSource = outDriver.CreateDataSource(outShapefile)
        outDataSource.CopyLayer(layer, nameShapefile, [])
        outDataSource.SyncToDisk()

        if format == 'shp':
            temp = BytesIO()
            with ZipFile(temp, 'w') as zipObj:
                for root, dirs, files in walk(directory_for_files):
                    for file in files:
                        zipObj.write(join(root, file), relpath(join(root, file), join(directory_for_files)))
                if style is not None:
                    zipObj.write(join(settings.MEDIA_ROOT,style.qml_file.path),nameShapefile+'.qml')

            response = StreamingHttpResponse(FileWrapper(temp), content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename="' + nameShapefile + '.zip"'
            response['Content-Length'] = temp.tell()

            temp.seek(0)
        else:
            if format == 'gpkg' and style is not None:
                try:
                    saveQMLtoGeoPackage(outShapefile, join(settings.MEDIA_ROOT,style.qml_file.path))
                except:
                    pass
            response = StreamingHttpResponse(open(outShapefile, 'rb'), content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename="' + nameShapefile + extention + '"'
        # Count the number of times the provider is downloaded
        targetVector.increment_download_number()

        tempDir.cleanup()
        return response

def getOgrDriver(format:str=None):
    if  format == 'shp':
        extention = '.shp'
        driver = 'ESRI Shapefile'
        content_type = 'application/zip'
    elif format == 'geojson':
        extention = '.geojson'
        driver = 'GeoJSON'
        content_type = 'application/json'
    elif format == 'gpkg':
        extention = '.gpkg'
        driver = 'GPKG'
        content_type = 'application/x-sqlite3'
    elif format == 'kml':
        extention = '.kml'
        driver = 'KML'
        content_type = 'application/vnd.google-earth.kml+xml'
    elif format == 'csv':
        extention = '.csv'
        driver = 'CSV'
        content_type = 'text/csv'
    else:
        extention = '.shp'
        driver = 'ESRI Shapefile'
        content_type = 'application/zip'
    
    return {
        'extention':extention,
        'driver':driver,
        'content_type':content_type
    }