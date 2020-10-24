from .models import Vector
from osm.models import Querry
from django.core.exceptions import ObjectDoesNotExist
from typing import NamedTuple
from django.db.models import Count, Q
import re
from django.db import connection, Error
from psycopg2.extensions import AsIs

class TableAndSchema(NamedTuple):
    """ represent the table and shema of a provider """
    table:str
    shema:str


class updateOsmDataSource():
    """ create or delete before creating a table with an osm querry """
    def __init__(self, provider_vector_id:int):
        self.provider_vector_id = provider_vector_id

    def updateDataSource(self):
        try:
           self.provider_vector:Vector = Vector.objects.get(provider_vector_id=self.provider_vector_id)

        except ObjectDoesNotExist as identifier:
            return {
                'error':True,
                'msg':' Can not find vector provider',
                'description':identifier
            }

        try:
           self.osm_querry:Querry = Querry.objects.get(provider_vector_id=self.provider_vector_id)
           
        except ObjectDoesNotExist as identifier:
            return {
                'error':True,
                'msg':' Can not find osm querry',
                'description':identifier
            }

        self._getTableAndSchema()
        return self._createOrReplaceTable()

    def _getTableAndSchema(self) ->TableAndSchema:
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
            # print(Vector.objects.annotate( num_table=Count('table',filter=Q(table=self.provider_vector.table) ) )[0].num_table, 222222 )

            while Vector.objects.annotate( num_table=Count('table',filter=Q(table=table) ) )[0].num_table != 0:
                table = re.sub('[^A-Za-z0-9]+', '', self.provider_vector.name)+'_'+str(i)
                i += 1 

        self.tableAndShema:TableAndSchema = TableAndSchema(table, shema)
        return self.tableAndShema

    def _createOrReplaceTable(self):
        """
            -  If the schema does not exist, create it
            - drop the table if exist
            - create table as the osm querry sql
            - update table, shema, extent, total area, total lenght and count of the vector provider
        """

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
            
        except Error as errorIdentifier :
            return {
                'error':True,
                'msg':' Can not create the table ',
                'description':str(errorIdentifier)
            }

        self.provider_vector.table = self.tableAndShema.table
        self.provider_vector.shema = self.tableAndShema.shema
        self.provider_vector.save()

        return  {
                'error':False,
        }
