import base64
import os
from os.path import join
import xml.etree.ElementTree
from xml.etree import ElementTree as et
from xml.dom.minidom import Document
import tempfile
from qgis.PyQt.QtXml import QDomDocument, QDomElement
from qgis.PyQt.QtCore import QFile, QIODevice
from qgis.PyQt.QtGui import QColor
import uuid

from qgis.core import QgsSimpleFillSymbolLayer, QgsFillSymbol, QgsMapLayerStyle, QgsRenderContext, QgsVectorLayer, QgsSingleSymbolRenderer, QgsProject

import tempfile
from django.conf import settings
from django.core.files import File

DATABASES = settings.DATABASES
OSMDATA = settings.OSMDATA



def getStyle(fillColor:str, strokeColor:str, strokeWidth:int)->File:
    """get a qml file of a line  simple style
     stroke with in pixels
     fill color
     stroke color
 
    """
    qgs = settings.QGS
    QMLPath=join(OSMDATA["qml_default_path"],'polygon_simple.qml')


    if os.path.exists(QMLPath) and os.path.isfile(QMLPath) :
        qFile= QFile(QMLPath)
        if qFile.open(QIODevice.ReadOnly):
            newStyle:QgsMapLayerStyle = QgsMapLayerStyle()

            doc = QDomDocument()
            elem = doc.createElement("style-data-som")

            xmlStyle:QDomDocument = QDomDocument()
            xmlStyle.setContent(qFile)
            elem.appendChild(xmlStyle.childNodes().at(0))
                
            newStyle.readXml(elem)
            if newStyle.isValid():
                project = QgsProject()
                tempLayer = QgsVectorLayer("Polygon", "temporary_points", "memory")
                project.addMapLayer(tempLayer)
                res = tempLayer.styleManager().addStyle("polygon_simple", newStyle)
                tempLayer.styleManager().setCurrentStyle("polygon_simple")
                layerSymbols:QgsSingleSymbolRenderer = tempLayer.renderer()

                polygonSymbol:QgsFillSymbol = layerSymbols.symbols(QgsRenderContext())[0]
                simpleFillSymbol:QgsSimpleFillSymbolLayer = polygonSymbol.symbolLayers()[0]

                simpleFillSymbol.setStrokeColor(QColor(strokeColor))
                simpleFillSymbol.setStrokeWidth(strokeWidth)
                simpleFillSymbol.setStrokeWidthUnit(2)

                simpleFillSymbol.setFillColor(QColor(fillColor))


                f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.qml')
                fileName = f.name
                tempLayer.saveNamedStyle(fileName)
                
                dataFile = open(fileName, "rb")
                project.removeMapLayer(tempLayer)

                return File(dataFile)
