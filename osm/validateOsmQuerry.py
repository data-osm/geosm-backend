import traceback
from typing import List, NewType
from django.db import connection, Error
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

    def getQuerryValidation(self) -> str:
        def _formatSelectOfUser(selectClauseOfUser:str)->str:
            """ if the user have specified and select, we must add a comma behind the select clause """
            if selectClauseOfUser :
                return ','+selectClauseOfUser
            else:
                return ''

        parameters = {'where':AsIs(self.where),'select':AsIs(_formatSelectOfUser(self.select))}

        if self.geometryType =='Point':
            sql_validation = "select A.osm_id,A.name,A.amenity,hstore_to_json(A.tags), ST_TRANSFORM(A.way,4326) as geom %(select)s  from planet_osm_point as A where %(where)s union all select A.osm_id,A.name,A.amenity,hstore_to_json(A.tags), ST_TRANSFORM(st_centroid(A.way),4326) as geom %(select)s from planet_osm_polygon as A where %(where)s limit 1" 
            sql = "select A.osm_id,A.name,A.amenity,hstore_to_json(A.tags), ST_TRANSFORM(A.way,4326) as geom  %(select)s  from planet_osm_point as A where %(where)s union all select A.osm_id,A.name,A.amenity,hstore_to_json(A.tags), ST_TRANSFORM(st_centroid(A.way),4326) as geom %(select)s from planet_osm_polygon as A where %(where)s" 
        elif self.geometryType == "Polygon":
            sql_validation = "select A.osm_id,A.name,A.amenity,hstore_to_json(A.tags), ST_TRANSFORM(A.way,4326) as geom %(select)s  from planet_osm_polygon as A where %(where)s limit 1" 
            sql = "select A.osm_id,A.name,A.amenity,hstore_to_json(A.tags), ST_TRANSFORM(A.way,4326) as geom  %(select)s  from planet_osm_polygon as A where %(where)s " 
        elif self.geometryType == "LineString":
            sql_validation = "select A.osm_id,A.name,A.amenity,hstore_to_json(A.tags), ST_TRANSFORM(A.way,4326) as geom %(select)s  from planet_osm_line as A where %(where)s limit 1" 
            sql = "select A.osm_id,A.name,A.amenity,hstore_to_json(A.tags), ST_TRANSFORM(A.way,4326) as geom  %(select)s  from planet_osm_line as A where %(where)s " 
        
        with connection.cursor() as cursor:
            query_validation = cursor.mogrify(sql_validation,parameters)

            query = cursor.mogrify(sql,parameters)
            self.query = query.decode('utf-8')

            return query_validation

    def isValid(self) -> bool:
        """ is this instance valid ? """
        try:
            with connection.cursor() as cursor:
                cursor.execute(self.getQuerryValidation())
                cursor.fetchall()
                return True
        except Error as errorIdentifier:
            self.error = str(errorIdentifier)
            return False

