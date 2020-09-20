from django.contrib.gis.db import models
from .utils import geometryHelper
from group.models import Layer
# Create your models here.

class Querry(models.Model):
    """ model of osm querry """
    osm_querry_id = models.IntegerField(primary_key=True)
    select_clause = models.TextField()
    """ the select clause of the querry """
    where_clause = models.TextField()
    """ the where clause of the querry """
    geometry_type = models.CharField(
        max_length=11,
        choices=geometryHelper.geometryType.choices
    )
    """ the geometry_type of the querry, if it is:
        - Point: we find only in point
        - Polygon: we find in points and polygons
        - LineString: we find in only in linestring
    """

class Id_layer(models.Model):
    """ model to make a relation between a osm_id and a layer in the app """
    osm_id = models.IntegerField()
    layer_id = models.ForeignKey(Layer,on_delete=models.CASCADE)
    geometry_type = models.CharField(
        max_length=11,
        choices=geometryHelper.geometryType.choices
    )