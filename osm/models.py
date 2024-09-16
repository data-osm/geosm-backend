from django.contrib.gis.db import models
from osm.utils import geometryHelper
from group.models import Layer
from tracking_fields.decorators import track
from .subModels.Querry import Querry, SimpleQuerry
from .subModels.sigFile import *


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class Id_layer(models.Model):
    """model to make a relation between a osm_id and a layer in the app"""

    osm_id = models.IntegerField()
    layer_id = models.ForeignKey(Layer, on_delete=models.CASCADE)
    geometry_type = models.CharField(
        max_length=11, choices=geometryHelper.geometryType.choices
    )
