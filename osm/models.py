from django.contrib.gis.db import models
from .utils import geometryHelper
from group.models import Layer, Vector
# Create your models here.

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

class Id_layer(models.Model):
    """ model to make a relation between a osm_id and a layer in the app """
    osm_id = models.IntegerField()
    layer_id = models.ForeignKey(Layer,on_delete=models.CASCADE)
    geometry_type = models.CharField(
        max_length=11,
        choices=geometryHelper.geometryType.choices
    )

    # select A.osm_id,A.name,A.amenity,hstore_to_json(A.tags), ST_TRANSFORM(A.way,4326) as geometry from planet_osm_polygon  as A , instances_gc  as B where  B.id =  1  AND  landuse = 'commercial' OR landuse = 'retail'