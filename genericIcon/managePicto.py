from .models import Picto
from cairosvg import svg2png
import tempfile
from django.core.files import File
from django.conf import settings


from io import StringIO, BytesIO
from PIL import Image
from dataclasses import dataclass
from typing import Any

@dataclass
class ImageBox:
    left:int
    right:int
    top:int
    bottom:int

def createPicto(value:dict, box:ImageBox = None) -> Picto:

    picto = Picto.objects.create()

    if 'background' in  value:
        picto.background = value['background']
    
    if 'color' in  value:
        picto.color = value['color']

    if 'icon' in  value:
        picto.icon = value['icon']

    if 'svg_as_text' in  value:
        picto.raster_icon = None

        f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.png')
        fileName = f.name
        svg2png(bytestring=value['svg_as_text'],write_to=fileName)
        # del request.data['svg_as_text']
        dataFile = open(fileName, "rb")
        picto.cercle_icon = File(dataFile)

    if 'svg_as_text_square' in  value:
        picto.raster_icon = None

        f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.png')
        fileName = f.name
        svg2png(bytestring=request.data['svg_as_text_square'],write_to=fileName)
        dataFile = open(fileName, "rb")
        picto.square_icon = File(dataFile)
    
    if 'raster_icon' in  value:
        picto.cercle_icon = None
        picto.square_icon = None

        image_field = value['raster_icon']
        image_file = BytesIO(image_field.read())
        image = Image.open(image_file)
        w, h = image.size

        if box :
            left = box.left
            top = box.top
            right = box.right
            bottom = box.bottom
            image =  image.crop((left, top, right, bottom)) 

        f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.png')
        fileName = f.name
        image.save(fileName, 'PNG')
        dataFile = open(fileName, "rb")
        
        picto.raster_icon = File(dataFile)

    picto.save()

    return picto

def updatePicto(value:dict, box:ImageBox = None) -> Picto:

    picto = Picto.objects.filter(pk=value['id'])

    if 'background' in  value:
        picto.background = value['background']
    
    if 'color' in  value:
        picto.color = value['color']

    if 'icon' in  value:
        picto.icon = value['icon']

    if 'svg_as_text' in  value:
        picto.raster_icon = None

        f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.png')
        fileName = f.name
        svg2png(bytestring=value['svg_as_text'],write_to=fileName)
        dataFile = open(fileName, "rb")
        picto.cercle_icon = File(dataFile)

    if 'svg_as_text_square' in  value:
        picto.raster_icon = None
        
        f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.png')
        fileName = f.name
        svg2png(bytestring=request.data['svg_as_text_square'],write_to=fileName)
        dataFile = open(fileName, "rb")
        picto.square_icon = File(dataFile)

    if 'raster_icon' in  value:
        picto.cercle_icon = None
        picto.square_icon = None

        image_field = value['raster_icon']
        image_file = BytesIO(image_field.read())
        image = Image.open(image_file)
        w, h = image.size

        if box :
            left = box.left
            top = box.top
            right = box.right
            bottom = box.bottom
            image =  image.crop((left, top, right, bottom)) 

        f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.png')
        fileName = f.name
        image.save(fileName, 'PNG')
        dataFile = open(fileName, "rb")
        
        picto.raster_icon = File(dataFile)

    picto.save()

    return picto