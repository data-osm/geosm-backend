from django.test import TestCase
from .models import Vector
from osm.models import Querry
# Create your tests here.

import os
from qgis.core import QgsVectorLayer, QgsProject, QgsApplication, QgsDataSourceUri, QgsCredentials, QgsProviderRegistry, QgsSettings, QgsMapLayerStyle
import traceback
from geosmBackend.type import OperationResponse
from dataclasses import dataclass
import tempfile
from django.db import connection, Error
from psycopg2.extensions import AsIs
import os
from qgis.PyQt.QtXml import QDomDocument, QDomElement
from qgis.PyQt.QtCore import QFile, QIODevice

os.environ["QT_QPA_PLATFORM"] = "offscreen"
QgsApplication.setPrefixPath("/usr/", True)
qgs = QgsApplication([], False)

class VectorTestCase(TestCase):
    def setUp(self):
        pass
        
        # vectorTestPoint1:Vector = Vector.objects.create(
        #     name="test point 1",
        #     geometry_type="Point"
        # )

        # vectorTestPolygon1:Vector = Vector.objects.create(
        #     name="test polygon 1",
        #     geometry_type="Polygon"
        # )

        # Querry.objects.create(
        #     where="amenity IN ('pub', 'bar', 'biergarten')",
        #     provider_vector_id=vectorTestPoint1
        # )

        # Querry.objects.create(
        #     where="amenity IN ('pub', 'bar', 'biergarten')",
        #     provider_vector_id=vectorTestPolygon1
        # )

    def test_state_vector_provider(self):
        """
            All the vector providers created before must have a state to good !
            That will means that, Qgis server and signals are working fine
        """
        newStyle = QgsMapLayerStyle()
        xmlStyle:QDomDocument = QDomDocument() 
        qFile= QFile('/var/www/geosm-backend/provider/commercesbar.qml')
        if qFile.open(QIODevice.ReadOnly):
            xmlStyle.setContent(qFile)
            
            print(newStyle.readXml(xmlStyle.documentElement()))
        else:
            print('ko')
        
        # vectorTestPoint1:Vector = Vector.objects.get(name="test point 1")
        # vectorTestPolygon1 = Vector.objects.get(name="test polygon 1")

        # self.assertEqual(vectorTestPoint1.state,"good")
        # self.assertEqual(vectorTestPolygon1.state,"good")
