from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

class geometryType(models.TextChoices):
        Polygon = 'Polygon'
        Point = 'Point'
        LineString = 'LineString'