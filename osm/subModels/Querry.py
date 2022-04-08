from dataclasses import dataclass
from django.contrib.gis.db import models
from django.db import transaction
from geosmBackend.type import AddVectorLayerResponse
from osm.utils import geometryHelper
from group.models import Layer, Vector
from osm.validateOsmQuerry import validateOsmQuerry
from django.core.exceptions import ObjectDoesNotExist
import traceback
from tracking_fields.decorators import track
from provider.manageOsmDataSource import manageOsmDataSource
from provider.qgis.manageVectorLayer import removeLayer


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

@track('select', 'where')
class Querry(models.Model):
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
        if validation['error'] == False:
            self.sql = validation['sql']
            with transaction.atomic():
                super(Querry,self).save(*args, **kwargs)
                if self.pk:
                    responseManageDataSource:AddVectorLayerResponse = manageOsmDataSource(self.provider_vector_id).updateDataSource(self)
                else:
                    responseManageDataSource:AddVectorLayerResponse = manageOsmDataSource(self.provider_vector_id).createDataSource(self)
                
                if responseManageDataSource.error:
                    raise Exception(str(responseManageDataSource.msg)+' : '+str(responseManageDataSource.description))
        else:
            raise Exception(validation['msg']+' : '+validation['description'])

    def delete(self, *args, **kwargs):
        if self.provider_vector_id.path_qgis and self.provider_vector_id.id_server:
            if removeLayer(self.provider_vector_id.path_qgis,self.provider_vector_id.id_server).error == False:
                manageOsmDataSource(self.provider_vector_id).deleteDataSource()
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
        