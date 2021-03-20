from django.contrib.gis.db import models
from .utils import geometryHelper
from group.models import Layer, Vector
from .validateOsmQuerry import validateOsmQuerry
from django.core.exceptions import ObjectDoesNotExist
import traceback
from tracking_fields.decorators import track

# Create your models here.

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

    def save(self, *args, **kwargs):
        validation = _isOsmQuerryValidate(self)
        if validation['error'] == False:
            self.sql = validation['sql']
            try:
                super(Querry,self).save(*args, **kwargs)
            except Exception as e:
                raise Exception(str(e))
        else:
            raise Exception(validation['msg']+' : '+validation['description'])


class Id_layer(models.Model):
    """ model to make a relation between a osm_id and a layer in the app """
    osm_id = models.IntegerField()
    layer_id = models.ForeignKey(Layer,on_delete=models.CASCADE)
    geometry_type = models.CharField(
        max_length=11,
        choices=geometryHelper.geometryType.choices
    )

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