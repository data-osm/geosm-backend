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

from qgis.core import QgsSvgMarkerSymbolLayer, QgsLineSymbol, QgsMapLayerStyle, QgsRenderContext, QgsVectorLayer, QgsSingleSymbolRenderer, QgsProject, QgsApplication

import tempfile
from django.conf import settings
from django.core.files import File

DATABASES = settings.DATABASES
OSMDATA = settings.OSMDATA

os.environ["QT_QPA_PLATFORM"] = "offscreen"
QgsApplication.setPrefixPath("/usr/", True)
qgs = QgsApplication([], False)

def getStyle(lineColor:str, lineWidth:int)->File:
    """get a qml file of a line  simple style
     line with in pixels
 
    """
    qgs.initQgis()
    QMLPath=join(OSMDATA["qml_default_path"],'line_simple.qml')


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
                tempLayer = QgsVectorLayer("Line", "temporary_points", "memory")
                project.addMapLayer(tempLayer)
                res = tempLayer.styleManager().addStyle("line_simple", newStyle)
                tempLayer.styleManager().setCurrentStyle("line_simple")
                layerSymbols:QgsSingleSymbolRenderer = tempLayer.renderer()

                lineSymbol:QgsLineSymbol = layerSymbols.symbols(QgsRenderContext())[0]

                lineSymbol.setColor(QColor(lineColor))
                lineSymbol.setWidth(lineWidth)
                lineSymbol.setWidthUnit(2)

                f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.qml')
                fileName = f.name
                tempLayer.saveNamedStyle(fileName)
                
                dataFile = open(fileName, "rb")
                project.removeMapLayer(tempLayer)

                return File(dataFile)
