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
    parameter:Any
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
            parameter={
                'icon_background':model.get('icon_background', None) ,
                'icon_color':color,
                'icon':model.get('icon', None),
                'raduis':10,
            }
        )