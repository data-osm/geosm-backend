import base64
import os
import xml.etree.ElementTree
from xml.etree import ElementTree as et
from xml.dom.minidom import Document
import tempfile
from qgis.PyQt.QtXml import QDomDocument, QDomElement
from qgis.PyQt.QtCore import QFile, QIODevice
from qgis.core import QgsSvgMarkerSymbolLayer, QgsMapLayerStyle, QgsRenderContext

from django.conf import settings

def getStyle(svgEncoded:str, color:str)->QgsMapLayerStyle:
    QMLPath=join(settings['OSMDATA']['qml_default_path'],'custom-cluster.qml')

    svgPath = _getEncodedImg(svgEncoded)
    if os.path.exists(QMLPath) and os.path.isfile(QMLPath) :
        qFile= QFile(QMLPath)
        if qFile.open(QIODevice.ReadOnly):
            response = _addStyleToLayer(layerName, pathToQgisProject, styleName, qFile)
            newStyle = QgsMapLayerStyle()

            doc = QDomDocument()
            elem = doc.createElement("style-data-som")

            xmlStyle:QDomDocument = QDomDocument()
            xmlStyle.setContent(QML)
            elem.appendChild(xmlStyle.childNodes().at(0))
                
            newStyle.readXml(elem)

            if newStyle.isValid():

                symbols = symbol_layer.clusterSymbol().symbolLayers()
                newStyle.symbols(QgsRenderContext())[0].symbolLayer(0).setPath(svgPath)
                for symbol in symbols:
                    if  type(symbol) is QgsSvgMarkerSymbolLayer:
                        symbol.setPath(svgPath)
                        # symbol.setColor(QColor.fromRgb(3,63,94))

            return newStyle

def _getEncodedImg(imgPath:str)->str:
    """ 
        transform png image to svg by encoding it. If imgPath already an svg, it will return imgPath
    """
    f = tempfile.NamedTemporaryFile(dir=settings['TEMP_URL'], suffix='.svg')
    fileName = f.name

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

        myFile = open(fileName, "w")
        myFile.write(doc.toprettyxml())
        return fileName
    else:
        return imgPath

# print(_getEncodedImg('/code/icons/group/bnm.png'))
# print(_getEncodedImg('/code/icons/Maki/aerialway-15.svg'))