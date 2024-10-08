from dataclasses import dataclass
import os
import tempfile
from typing import Any, Optional

from django.http.request import QueryDict
from cairosvg import svg2png
import tempfile
from django.core.files import File
from django.conf import settings
from ..qgis.customStyle import cluster
from ..qgis.customStyle import point_icon_simple
from ..qgis.customStyle import ligne_simple
from ..qgis.customStyle import polygon_simple
from group.models import Icon

# @dataclass
# class pointClusterModel:
#     """ represent the model to create a new pointCluster style on a layer """

#     """ the svg in string """
#     svg_as_text:Optional[str]
#     """ the id of the icon in the database """
#     icon:int
#     icon_background:Optional[str]
#     icon_color:Optional[str]

@dataclass
class ResponseCustomStyle:
    parameters:Any
    qml_file:File

class CustomStyleHandler():
    def __init__(self):
        pass

    def pointCluster(self, model:QueryDict)->ResponseCustomStyle:
        
        if model.get('fileName', None) is not None and os.path.exists(model.get('fileName')) and os.path.isfile(model.get('fileName')):
            fileName = model.get('fileName')
        elif model.get('svg_as_text', None) is not None:
            f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.png')
            fileName = f.name
            svg2png(bytestring=model.get('svg_as_text'),write_to=fileName, unsafe=True)
            # dataFile = open(fileName, "rb")
            # png = File(dataFile)
        else:
            icon:Icon = Icon.objects.get(pk=model.get('icon'))
            fileName = icon.path.path

        color = model.get('icon_color', None) 
        

        qml_file = cluster.getStyle(fileName, color)

        return ResponseCustomStyle(
            qml_file=qml_file,
            parameters={
                'icon_background':model.get('icon_background', None) ,
                'icon_color':color,
                'icon':model.get('icon', None),
                'raduis':10,
            }
        )

    def point_icon_simple(self, model:QueryDict)->ResponseCustomStyle:
        
        if model.get('fileName', None) is not None and os.path.exists(model.get('fileName')) and os.path.isfile(model.get('fileName')):
            fileName = model.get('fileName')
        elif model.get('svg_as_text', None) is not None:
            f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.png')
            fileName = f.name
            svg2png(bytestring=model.get('svg_as_text'),write_to=fileName, unsafe=True)
        else:
            icon:Icon = Icon.objects.get(pk=model.get('icon'))
            fileName = icon.path.path

        qml_file = point_icon_simple.getStyle(fileName)

        return ResponseCustomStyle(
            qml_file=qml_file,
            parameters={
                'icon':model.get('icon', None),
            }
        )

    def line_simple(self, model:QueryDict)->ResponseCustomStyle:

        qml_file = ligne_simple.getStyle(model.get('lineColor'),model.get('lineWidth'))

        return ResponseCustomStyle(
            qml_file=qml_file,
            parameters={
                'lineColor':model.get('lineColor'),
                'lineWidth':model.get('lineWidth'),
            }
        )

    def polygon_simple(self, model:QueryDict)->ResponseCustomStyle:

        qml_file = polygon_simple.getStyle(model.get('fillColor'),model.get('strokeColor'),model.get('strokeWidth'))

        return ResponseCustomStyle(
            qml_file=qml_file,
            parameters={
                'fillColor':model.get('fillColor'),
                'strokeColor':model.get('strokeColor'),
                'strokeWidth':model.get('strokeWidth')
            }
        )