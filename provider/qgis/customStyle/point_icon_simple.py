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

from qgis.core import QgsSvgMarkerSymbolLayer, QgsSimpleMarkerSymbolLayer, QgsMapLayerStyle, QgsRenderContext, QgsVectorLayer, QgsSingleSymbolRenderer, QgsProject, QgsApplication

import tempfile
from django.conf import settings
from django.core.files import File

DATABASES = settings.DATABASES
OSMDATA = settings.OSMDATA

os.environ["QT_QPA_PLATFORM"] = "offscreen"
QgsApplication.setPrefixPath("/usr/", True)
qgs = QgsApplication([], False)

def getStyle(svgEncoded:str)->File:
    """get a qml file of point icon simple style. With the icon svgEncoded 
 
    """
    qgs.initQgis()
    QMLPath=join(OSMDATA["qml_default_path"],'point_icon_simple.qml')

    img_svg_encoded = _getEncodedImg(svgEncoded)

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
                tempLayer = QgsVectorLayer("Point", "temporary_points", "memory")
                project.addMapLayer(tempLayer)
                res = tempLayer.styleManager().addStyle("point_icon_simple", newStyle)
                tempLayer.styleManager().setCurrentStyle("point_icon_simple")
                layerSymbols:QgsSingleSymbolRenderer = tempLayer.renderer()
                
                layerSymbols.symbols(QgsRenderContext())[0].symbolLayer(0).setPath(img_svg_encoded)

                f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.qml')
                fileName = f.name
                tempLayer.saveNamedStyle(fileName)
                
                dataFile = open(fileName, "rb")
                project.removeMapLayer(tempLayer)

                return File(dataFile)


def _getEncodedImg(imgPath:str)->str:
    """ 
        transform png image to a base64 svg string. If imgPath already an svg, it will return it in base 64 directly
    """
    # f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.svg')
    # fileName = f.name
    if '.svg' not in imgPath:
        
        encoded = base64.b64encode(open(imgPath, "rb").read()).decode()

        doc = Document()
        svg = doc.createElement("svg")
        doc.appendChild(svg)

        svg.setAttribute("id", "mySvg")
        svg.setAttribute("xmlns", "http://www.w3.org/2000/svg")
        svg.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink")

        image = doc.createElement("image")
        svg.appendChild(image)
        image.setAttribute("width", "160")
        image.setAttribute("height", "160")
        image.setAttribute("xlink:href", 'data:image/png;base64,{}'.format(encoded))

 
        message_bytes = doc.toprettyxml().encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')

        img_svg_encoded = 'base64:{}'.format(base64_message)
        return img_svg_encoded
    else:
        encoded = base64.b64encode(open(imgPath, "rb").read()).decode()
        img_svg_encoded = 'base64:{}'.format(encoded)
        return img_svg_encoded
