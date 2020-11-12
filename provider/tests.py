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
            provider_vector_id=vectorTestPoint1
        )

        Querry.objects.create(
            where="amenity IN ('pub', 'bar', 'biergarten')",
            provider_vector_id=vectorTestPolygon1
        )

    def test_state_vector_provider(self):
        """
            All the vector providers created before must have a state to good !
            That will means that, Qgis server and signals are working fine
        """
        vectorTestPoint1:Vector = Vector.objects.get(name="test point 1")
        vectorTestPolygon1 = Vector.objects.get(name="test polygon 1")

        self.assertEqual(vectorTestPoint1.state,"good")
        self.assertEqual(vectorTestPolygon1.state,"good")
