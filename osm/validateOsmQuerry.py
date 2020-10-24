import traceback
from typing import List, NewType
from django.db import connection, Error
# from psycopg2 import sql
from psycopg2.extensions import AsIs

from enum import Enum
class geometryType(Enum):
    Polygon = 'Polygon'
    Point = 'Point'
    LineString = 'LineString'

GeometryType = NewType('GeometryType', geometryType)

class validateOsmQuerry():
    """ Validate an osm querry """

    def __init__(self, where: str, select: str, geometryType: GeometryType):
        self.where = where
        self.select = select
        self.geometryType = geometryType
        self.error = None

    def getQuerry(self) -> str:
        parameters = {'where':AsIs(self.where),'select':AsIs(self.select)}

        if self.geometryType =='Point':
            sql = "select %(select)s  from planet_osm_point as A where %(where)s union all select %(select)s from planet_osm_polygon as A where %(where)s limit 1" 
        elif self.geometryType == "Polygon":
            sql = "select %(select)s  from planet_osm_polygon as A where %(where)s limit 1" 
        elif self.geometryType == "LineString":
            sql = "select %(select)s  from planet_osm_line as A where %(where)s limit 1" 
        
        with connection.cursor() as cursor:
            query = cursor.mogrify(sql,parameters)
            self.query = query.decode('utf-8')
            return query

    def isValid(self) -> bool:
        """ is this instance valid ? """
        try:
            with connection.cursor() as cursor:
                cursor.execute(self.getQuerry())
                print(cursor.query)
                cursor.fetchall()
                return True
        except Error as errorIdentifier:
            self.error = str(errorIdentifier)
            return False

