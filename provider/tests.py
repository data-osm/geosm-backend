from django.test import TestCase
from .models import Vector
from osm.models import Querry
# Create your tests here.

class VectorTestCase(TestCase):
    def setUp(self):
        
        vectorTestPoint1:Vector = Vector.objects.create(
            name="test point 1",
            geometry_type="Point"
        )

        vectorTestPolygon1:Vector = Vector.objects.create(
            name="test polygon 1",
            geometry_type="Polygon"
        )

        Querry.objects.create(
            where="amenity IN ('pub', 'bar', 'biergarten')",
            provider_vector_id=vectorTestPoint1.provider_vector_id
        )
