from .models import Vector
from osm.models import Querry
from django.core.exceptions import ObjectDoesNotExist
from typing import NamedTuple
from django.db.models import Count, Q
import re
from django.db import connection, Error
from psycopg2.extensions import AsIs
from .qgis.manageVectorLayer import addVectorLayerFomPostgis, AddVectorLayerResponse
from geosmBackend.settings import DATABASES, OSMDATA
from os.path import join
from geosmBackend.type import OperationResponse
import traceback

class TableAndSchema(NamedTuple):
    """ represent the table and shema of a provider """
    table:str
    shema:str


class manageOsmDataSource():
    """ create or delete before creating a table with an osm querry """
    def __init__(self, provider_vector_id:int):
        self.provider_vector_id = provider_vector_id

    def deleteDataSource(self, provider_vector:Vector=None)->OperationResponse:
        """ Delete and osm datasource by droping his table """
        response=OperationResponse(
            error=False,
            msg="",
            description="",
        )

        self.provider_vector = provider_vector
        if self.provider_vector is None:
            try:
                self.provider_vector:Vector = Vector.objects.get(provider_vector_id=self.provider_vector_id)

            except ObjectDoesNotExist as identifier:
                response.error = True
                response.msg = ' Can not find vector provider'
                response.description = str(identifier)
                return response

        self._getTableAndSchema()

        try:
            with connection.cursor() as cursor:
                cursor.execute("DROP TABLE  "+self.tableAndShema.shema+"."+self.tableAndShema.table)
                response.error = False
                return response
        except Error as errorIdentifier :
            traceback.print_exc()
            response.error = True
            response.msg = ' Can not drop the table '
            response.description = str(errorIdentifier)
            return response


    def updateDataSource(self)->OperationResponse:
        """ update an osm datsource """

        response=OperationResponse(
            error=False,
            msg="",
            description="",
        )

        try:
           self.provider_vector:Vector = Vector.objects.get(provider_vector_id=self.provider_vector_id)

        except ObjectDoesNotExist as identifier:
            response.error = True
            response.msg = ' Can not find vector provider'
            response.description = str(identifier)
            return response

        try:
           self.osm_querry:Querry = Querry.objects.get(provider_vector_id=self.provider_vector_id)
           
        except ObjectDoesNotExist as identifier:
            response.error = True
            response.msg = 'Can not find osm querry'
            response.description = str(identifier)
            return response
           

        self._getTableAndSchema()
        return self._createOrReplaceTable()

    def createDataSource(self)->AddVectorLayerResponse:
        """ create an osm datsource, after add it to an QGIS project """

        response=AddVectorLayerResponse(
            error=False,
            msg="",
            description="",
            pathProject="",
            layerName="",
        )

        try:
           self.provider_vector:Vector = Vector.objects.get(provider_vector_id=self.provider_vector_id)

        except ObjectDoesNotExist as identifier:
            response.error = True
            response.msg = ' Can not find vector provider'
            response.description = identifier
            return response

        try:
           self.osm_querry:Querry = Querry.objects.get(provider_vector_id=self.provider_vector_id)
           
        except ObjectDoesNotExist as identifier:
            response.error = True
            response.msg = ' Can not find osm querry'
            response.description = identifier
            return response

        self._getTableAndSchema()
        
        createOrReplaceTableResponse = self._createOrReplaceTable()

        if createOrReplaceTableResponse.error == False:

            createOSMDataSourceResponse =  addVectorLayerFomPostgis(
                DATABASES['default']['HOST'],
                DATABASES['default']['PORT'],
                DATABASES['default']['NAME'],
                DATABASES['default']['USER'],
                DATABASES['default']['PASSWORD'],
                self.provider_vector.shema,
                self.provider_vector.table,
                'geom',
                'osm_id',
                self.provider_vector.table,
                join(OSMDATA['project_qgis_path'],'projet.qgs')
            )

            if createOSMDataSourceResponse.error == False:
                self.provider_vector.url_server = createOSMDataSourceResponse.pathProject
                self.provider_vector.id_server = createOSMDataSourceResponse.layerName
                self.provider_vector.save()
            
            return createOSMDataSourceResponse

        else:
            response.error = True
            response.msg = createOrReplaceTableResponse.msg
            response.description = createOrReplaceTableResponse.description
            return response
    
    def _getTableAndSchema(self) ->TableAndSchema:
        """ 
            Get table or shema of the table of this vector provider in databse
            will check if table and shema already exist in the vector provider properties and return them
            If they not exist, will create them randomnly
        """
        shema = None
        table = None
        if self.provider_vector.shema:
            shema = self.provider_vector.shema
        else:
            shema = 'osm_tables'

        if self.provider_vector.table:
            table = self.provider_vector.table
        else:
            table = re.sub('[^A-Za-z0-9]+', '', self.provider_vector.name)
            i= 0

            while Vector.objects.annotate( num_table=Count('table',filter=Q(table=table) ) )[0].num_table != 0:
                table = re.sub('[^A-Za-z0-9]+', '', self.provider_vector.name)+'_'+str(i)
                i += 1 

        self.tableAndShema:TableAndSchema = TableAndSchema(table, shema)
        return self.tableAndShema

    def _createOrReplaceTable(self) -> OperationResponse:
        """
            Create a table in a shema of replace it with new osm querry:
            -  If the schema does not exist, create it
            - drop the table if exist
            - create table as the osm querry sql
            - update table, shema, extent, total area, total lenght and count of the vector provider
        """

        response=OperationResponse(
            error=False,
            msg="",
            description="",
        )

        with connection.cursor() as cursor:
            cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = '"+self.tableAndShema.shema+"'")
           
            if cursor.rowcount == 0:
                cursor.execute("CREATE SCHEMA "+self.tableAndShema.shema)

        with connection.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS "+self.tableAndShema.shema+'.'+self.tableAndShema.table)

        try:
            with connection.cursor() as cursor:
                cursor.execute("CREATE TABLE  "+self.tableAndShema.shema+"."+self.tableAndShema.table+" AS "+self.osm_querry.sql)
                cursor.execute("CREATE INDEX "+ self.tableAndShema.table+"_geometry_idx ON " + self.tableAndShema.shema+"."+self.tableAndShema.table+" USING GIST(geom) ")
                if self.provider_vector.geometry_type == 'Point':
                    cursor.execute("ALTER TABLE "+ self.tableAndShema.shema+"."+self.tableAndShema.table+" ALTER COLUMN geom TYPE geometry(Point,4326) USING ST_centroid(geom); ")
            
        except Error as errorIdentifier :
            response.error = True
            response.msg = ' Can not create the table '
            response.description = str(errorIdentifier)
            return response

        self.provider_vector.table = self.tableAndShema.table
        self.provider_vector.shema = self.tableAndShema.shema
        self.provider_vector.save()

        return  response
