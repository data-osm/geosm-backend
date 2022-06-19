from dataclasses import dataclass

from numpy import number
from .models import Vector, Style
# from osm.models import Querry
from django.core.exceptions import ObjectDoesNotExist
from typing import Any, NamedTuple, Union
from django.db.models import Count, Q
import re
from django.db import connections, Error, ConnectionProxy
from .qgis.manageVectorLayer import addVectorLayerFomPostgis, removeLayer
from .qgis.manageStyle import getQMLStyleOfLayer
from django.conf import settings
from os.path import join
from geosmBackend.type import OperationResponse, AddVectorLayerResponse, SimpleQuerryDefinition, TableCreatedResponse, TableMetadata
from django.core.files import File
from django.core.files.base import ContentFile

import traceback

DATABASES = settings.DATABASES
OSMDATA = settings.OSMDATA
class TableAndSchema(NamedTuple):
    """ represent the table and shema of a provider """
    table:str
    shema:str



class ManageProviderFromSource():
    def __init__(self, provider_vector:Vector):
        self.provider_vector:Vector = provider_vector
        self.tableAndShema = self._getTableAndSchema()

    def updateProvider(self, tableCreatedResponse:TableCreatedResponse)->TableCreatedResponse:
        """ update an osm datsource """

        if tableCreatedResponse.error == False:
            if tableCreatedResponse.data.extent:
                self.provider_vector.extent = tableCreatedResponse.data.extent
            self.provider_vector.count = tableCreatedResponse.data.count
            self.provider_vector.save()

        return tableCreatedResponse

    def createProviderInQGIS(self, tableCreatedResponse:TableCreatedResponse, connectionName:str)->AddVectorLayerResponse:
        """ add it to an QGIS project """

        response=AddVectorLayerResponse(
            error=False,
            msg="",
            description="",
            pathProject="",
            layerName="",
        )
        
        if tableCreatedResponse.error == False:
            qgis_project = 'projet'+'_'+str(int(Vector.objects.count()/5))+'.qgs'
            
            createOSMDataSourceResponse =  addVectorLayerFomPostgis(
                DATABASES[connectionName]['HOST'],
                DATABASES[connectionName]['PORT'],
                DATABASES[connectionName]['NAME'],
                DATABASES[connectionName]['USER'],
                DATABASES[connectionName]['PASSWORD'],
                self.provider_vector.shema,
                self.provider_vector.table,
                tableCreatedResponse.geometryField,
                tableCreatedResponse.primaryKey,
                self.provider_vector.table,
                qgis_project
            )

            if createOSMDataSourceResponse.error :
                raise Exception (createOSMDataSourceResponse)

            if createOSMDataSourceResponse.error == False:
                if tableCreatedResponse.data.extent:
                    self.provider_vector.extent = tableCreatedResponse.data.extent
                self.provider_vector.count = tableCreatedResponse.data.count
                
                self.provider_vector.primary_key_field = tableCreatedResponse.primaryKey
                self.provider_vector.path_qgis = qgis_project
                self.provider_vector.url_server = OSMDATA['url_qgis_server_prefix']+qgis_project
                self.provider_vector.id_server = createOSMDataSourceResponse.layerName
                self.provider_vector.save()

                try:
                    f = open(join(OSMDATA['qml_default_path'],'default-'+self.provider_vector.geometry_type+'.qml'))
                    myfile = File(f)
                    default_style = Style(
                        name='default',
                        qml_file=myfile,
                        provider_vector_id=self.provider_vector
                    )
                    default_style.save()
                except Exception as e :
                    traceback.print_exc()
                    print(str(e),'error')
                        
                

            return createOSMDataSourceResponse

        else:
            response.error = True
            response.msg = tableCreatedResponse.msg
            response.description = tableCreatedResponse.description
            raise Exception (response)
    
  

    def _getTableAndSchema(self) ->TableAndSchema:
        """ 
            Get table or shema of the table of this vector provider in databse
            will check if table and shema already exist in the vector provider properties and return them
            If they not exist, will create them randomnly
        """
        return getTableAndSchema(self.provider_vector)

class manageQuerryProvider(ManageProviderFromSource):
    """ create or delete before creating a table with an osm querry """
    def __init__(self, provider_vector:Vector, osm_querry:SimpleQuerryDefinition):
        super().__init__(provider_vector)
        self.osm_querry:SimpleQuerryDefinition = osm_querry


    def updateQuerryProvider(self)->OperationResponse:
        """ update an osm datsource """
        
        return self.updateProvider(self._createOrReplaceTable())

    def deleteQuerryDataSource(self)->OperationResponse:
        """ Delete and osm datasource by droping his table """
        response=OperationResponse(
            error=False,
            msg="",
            description="",
            data=None
        )


        try:
            connection = connections[self.osm_querry.connection]
            with connection.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS "+self.tableAndShema.shema+"."+self.tableAndShema.table)
                response.error = False
                return response
        except Error as errorIdentifier :
            traceback.print_exc()
            response.error = True
            response.msg = ' Can not drop the table '
            response.description = str(errorIdentifier)
            return response

    # def createOsmDataSource()
    def creatQuerryeDataSource(self)->AddVectorLayerResponse:
        """ create an osm datsource, after add it to an QGIS project """
        return self.createProviderInQGIS(self._createOrReplaceTable(), self.osm_querry.connection)

    def _createOrReplaceTable(self) -> TableCreatedResponse:
        """
            Create a table in a shema or replace it with new osm querry:
            -  If the schema does not exist, create it
            - drop the table if exist
            - create table as the osm querry sql
            - update table, shema, extent, total area, total lenght and count of the vector provider
        """

        response=TableCreatedResponse(
            error=False,
            msg="",
            description="",
            data=TableMetadata(extent=None, number=None),
            geometryField='geom',
            primaryKey='osm_id'
        )
        connection = connections[self.osm_querry.connection]

        createSchemaIfNotExist(self.tableAndShema.shema, connection)
        dropTableIfExist(self.tableAndShema.shema,self.tableAndShema.table, connection)
     
        try:
            with connection.cursor() as cursor:
                cursor.execute("CREATE TABLE  "+self.tableAndShema.shema+"."+self.tableAndShema.table+" AS "+self.osm_querry.sql)
                cursor.execute("CREATE INDEX "+ self.tableAndShema.table+"_geometry_idx ON " + self.tableAndShema.shema+"."+self.tableAndShema.table+" USING GIST(geom) ")
                if self.provider_vector.geometry_type == 'Point':
                    cursor.execute("ALTER TABLE "+ self.tableAndShema.shema+"."+self.tableAndShema.table+" ALTER COLUMN geom TYPE geometry(Point,4326) USING ST_centroid(geom); ")
            
            with connection.cursor() as cursor:
                cursor.execute("select min(ST_XMin(geom)) as l,min(ST_YMin(geom)) as b,max(ST_XMax(geom)) as r,max(ST_YMax(geom)) as t, count(*) as count from "+self.tableAndShema.shema+"."+self.tableAndShema.table)
                responseExtent = cursor.fetchall()[0]
                response.data.extent=[
                    responseExtent[0],
                    responseExtent[1],
                    responseExtent[2],
                    responseExtent[3]
                ]
               
                response.data.count= int(responseExtent[4])

        except Error as errorIdentifier :
            response.error = True
            response.msg = ' Can not create the table '+self.tableAndShema.table
            response.description = str(errorIdentifier)
            return response

        self.provider_vector.table = self.tableAndShema.table
        self.provider_vector.shema = self.tableAndShema.shema
        self.provider_vector.save()

        return  response


def getTableAndSchema(provider_vector:Vector,shema='osm_tables') ->TableAndSchema:
        """ 
            Get table or shema of the table of this vector provider in databse
            will check if table and shema already exist in the vector provider properties and return them
            If they not exist, will create them randomnly
        """
        table = None
        if provider_vector.shema:
            shema = provider_vector.shema

        if provider_vector.table:
            table = provider_vector.table
        else:
            table = re.sub('[^A-Za-z0-9]+', '', provider_vector.name).lower()
            i= 0

            while Vector.objects.annotate( num_table=Count('table',filter=Q(table=table) ) )[0].num_table != 0:
                table = re.sub('[^A-Za-z0-9]+', '', provider_vector.name).lower()+'_'+str(i)
                i += 1 

        tableAndShema:TableAndSchema = TableAndSchema(table, shema)
        return tableAndShema

def createSchemaIfNotExist(shema:str, connection:ConnectionProxy):
    """
    Create a schema in database if not exist

    Args:
        shema (str): name of the schema
        connection (_type_): connextion to the database
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = '"+shema+"'")
        if cursor.rowcount == 0:
            cursor.execute("CREATE SCHEMA "+shema)

def dropTableIfExist(schema:str, table:str, connection:ConnectionProxy):
    """Drop table if exists

    Args:
        schema (str): _description_
        table (str): _description_
        connection (ConnectionProxy): _description_
    """
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS "+schema+'.'+table)