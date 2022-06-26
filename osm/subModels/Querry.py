from dataclasses import dataclass
from typing import Union
from django.contrib.gis.db import models
from django.db import transaction
from geosmBackend.exceptions import appException
from geosmBackend.type import AddVectorLayerResponse
from osm.utils import geometryHelper
from group.models import Layer, Vector
from osm.validateOsmQuerry import validateOsmQuerry
from django.core.exceptions import ObjectDoesNotExist
import traceback
from tracking_fields.decorators import track
from provider.manageOsmDataSource import manageOsmDataSource
from provider.qgis.manageVectorLayer import removeLayer
from django.db import Error, connections
from psycopg2.extensions import AsIs
from django.db.utils import DEFAULT_DB_ALIAS
    
class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

@track('select', 'where')
class Querry(models.Model):
    """ name of the connexion """
    connection = models.TextField(blank=False, null=False, default=DEFAULT_DB_ALIAS)
    """ model of osm querry """
    # osm_querry_id = models.OneToOneField(primary_key=True)
    select = models.TextField(blank=True,null=True)
    """ the select clause of the querry """
    where = models.TextField(null=False)
    """ the where clause of the querry """
    sql = models.TextField(blank=True)
    """ the full querry """
    provider_vector_id = models.OneToOneField(Vector,on_delete=models.CASCADE,primary_key=True)
    auto_update = models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        validation = _isOsmQuerryValidate(self)
        newOne = self.created_at is None
        if validation['error'] == False:
            self.sql = validation['sql']
            super(Querry,self).save(*args, **kwargs)
            
            if newOne:
                responseManageDataSource:AddVectorLayerResponse = manageOsmDataSource(self.provider_vector_id, self).createDataSource()
            else:
                responseManageDataSource:AddVectorLayerResponse = manageOsmDataSource(self.provider_vector_id, self).updateDataSource()
            if responseManageDataSource.error:
                self.delete()
                raise appException(str(responseManageDataSource.msg)+' : '+str(responseManageDataSource.description))
            self.provider_vector_id.source ='osm'
            self.provider_vector_id.save()
        else:
            self.delete()
            raise appException(validation['msg']+' : '+validation['description'])

    def delete(self, *args, **kwargs):
        try:
            if self.provider_vector_id.path_qgis and self.provider_vector_id.id_server:
                if removeLayer(self.provider_vector_id.path_qgis,self.provider_vector_id.id_server).error == False:
                    manageOsmDataSource(self.provider_vector_id, self).deleteDataSource()
        except:
            pass
        
        super(Querry, self).delete(*args, **kwargs)

def _isOsmQuerryValidate(osmQuerry:Querry) ->dict:
    try:

        vector_provider = osmQuerry.provider_vector_id
        osmValidation = validateOsmQuerry(osmQuerry.where, osmQuerry.select, vector_provider.geometry_type)
        if osmValidation.isValid():
            return  {
                'error':False,
                'sql':osmValidation.query
            }
        else:
          
            return {
                'error':True,
                'msg':' The osm querry is not correct ',
                'description':osmValidation.error
            }

    except ObjectDoesNotExist as identifier:
        return {
            'error':True,
            'msg':' Can not find the vector provider of this osm querry',
            'description':identifier
        }
        

@track('sql')
class SimpleQuerry(models.Model):
    """ name of the connexion """
    connection = models.TextField(blank=False, null=False, default=DEFAULT_DB_ALIAS)
    """ model of a simple querry """
    sql = models.TextField(blank=False, null=False)
    """ the full querry """
    provider_vector_id = models.OneToOneField(Vector,on_delete=models.CASCADE,primary_key=True)
    auto_update = models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        validation = _isSimpleQuerryValidate(self)
        if validation == True:
            if self.created_at is not None:
                responseManageDataSource:AddVectorLayerResponse = manageOsmDataSource(self.provider_vector_id, self).updateDataSource()
            else:
                responseManageDataSource:AddVectorLayerResponse = manageOsmDataSource(self.provider_vector_id, self).createDataSource()
            if responseManageDataSource.error:
                raise appException(str(responseManageDataSource.msg)+' : '+str(responseManageDataSource.description))
            self.provider_vector_id.source='querry'
            self.provider_vector_id.save()
            super(SimpleQuerry,self).save(*args, **kwargs)
        else:
            raise appException(validation)

    def delete(self, *args, **kwargs):
        if self.provider_vector_id.path_qgis and self.provider_vector_id.id_server:
            if removeLayer(self.provider_vector_id.path_qgis,self.provider_vector_id.id_server).error == False:
                manageOsmDataSource(self.provider_vector_id, self).deleteDataSource()
        super(SimpleQuerry, self).delete(*args, **kwargs)

def _isSimpleQuerryValidate(simpleQuerry:SimpleQuerry) ->Union[bool,str]:

        try:
            connection = connections[simpleQuerry.connection]
            sql = "select * from ("+ simpleQuerry.sql.replace(';','')+" ) as dd limit 1"
            with connection.cursor() as cursor:
                cursor.execute(sql)
                cursor.fetchall()
                return True
        except Error as errorIdentifier:
            error = str(errorIdentifier)
            return error

   