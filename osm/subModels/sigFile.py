from dataclasses import dataclass
from typing import Union
from django.contrib.gis.db import models
from django.db import transaction
from geosmBackend.exceptions import appException
from geosmBackend.type import AddVectorLayerResponse, TableCreatedResponse, TableMetadata
from osm.utils import geometryHelper
from group.models import Layer, Vector
from osm.validateOsmQuerry import validateOsmQuerry
from django.core.exceptions import ObjectDoesNotExist
import traceback
from os.path import join
from provider.manageOsmDataSource import createSchemaIfNotExist, dropTableIfExist, getTableAndSchema, ManageProviderFromSource
from provider.qgis.manageVectorLayer import removeLayer
from django.db import Error, connections, connection
from django.db.utils import DEFAULT_DB_ALIAS
import geopandas as gpd
from shapely.geometry import Polygon,LineString, Point, MultiLineString, MultiPoint, MultiPolygon
from sqlalchemy import create_engine
from django.conf import settings
import fiona

fiona.drvsupport.supported_drivers['kml'] = 'rw' # enable KML support which is disabled by default
fiona.drvsupport.supported_drivers['KML'] = 'rw' # enable KML support which is disabled by default


DATABASES = settings.DATABASES

def get_custom_file_path(instance, filename):
    return join('sig-file', filename)

class sigFile(models.Model):
    """ name of the connexion """
    connection = models.TextField(blank=False, null=False, default=DEFAULT_DB_ALIAS)
    file =  models.FileField(blank=True, null=True, default=None, upload_to=get_custom_file_path)
    provider_vector_id = models.OneToOneField(Vector,on_delete=models.CASCADE,primary_key=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        
        connexion = connections[self.connection]
        engine = create_engine('postgresql://'+DATABASES[self.connection]['USER']+':'+DATABASES[self.connection]['PASSWORD']+'@'+DATABASES[self.connection]['HOST']+':'+DATABASES[self.connection]['PORT']+'/'+DATABASES[self.connection]['NAME'])
        gpdSource = gpd.read_file(self.file)

        tableAndShema = getTableAndSchema(self.provider_vector_id, 'sigfile')
        createSchemaIfNotExist(tableAndShema.shema, connexion)
        if self.created_at is not None:
            dropTableIfExist(tableAndShema.shema, tableAndShema.table, connexion)

        gpdSource.to_postgis(name=tableAndShema.table, con=engine, index=True ,schema=tableAndShema.shema, index_label="id")
        engine.dispose()

        response=TableCreatedResponse(
            error=False,
            msg="",
            description="",
            data=TableMetadata(extent=None, count=0 ),
            geometryField='geom',
            primaryKey='id'
        )

        with connexion.cursor() as cursor:
                cursor.execute("alter TABLE "+tableAndShema.shema+"."+tableAndShema.table+" rename column geometry to geom;")
                cursor.execute("select min(ST_XMin(st_transform(geom,4326))) as l,min(ST_YMin(st_transform(geom,4326))) as b,max(ST_XMax(st_transform(geom,4326))) as r,max(ST_YMax(st_transform(geom,4326))) as t, count(*) as count from "+tableAndShema.shema+"."+tableAndShema.table)
                responseExtent = cursor.fetchall()[0]
                response.data.extent=[
                    responseExtent[0],
                    responseExtent[1],
                    responseExtent[2],
                    responseExtent[3]
                ]
                response.data.count= int(responseExtent[4])

        if isinstance(gpdSource["geometry"][0], Polygon) or isinstance(gpdSource["geometry"][0], MultiPolygon):
            self.provider_vector_id.geometry_type = 'Polygon'
        elif isinstance(gpdSource["geometry"][0], Point) or isinstance(gpdSource["geometry"][0], MultiPoint):
            self.provider_vector_id.geometry_type = 'Point'
        elif isinstance(gpdSource["geometry"][0], LineString) or isinstance(gpdSource["geometry"][0], MultiLineString):
            self.provider_vector_id.geometry_type = 'LineString'

        self.provider_vector_id.table = tableAndShema.table
        self.provider_vector_id.shema = tableAndShema.shema
        self.provider_vector_id.save()

        manageProviderFromSource = ManageProviderFromSource(self.provider_vector_id)

        if self.created_at is not None:
            manageProviderFromSource.updateProvider(response)
        else:
            manageProviderFromSource.createProviderInQGIS(response, self.connection)

        super(sigFile, self).save(*args, **kwargs)
