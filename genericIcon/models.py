from django.db import models
from group.subModels.icon import Icon
import os

def get_upload_path_layer_icon (instance, filename):
    return os.path.join('picto', str(instance.pk)+'.png')

class Picto (models.Model):

    background = models.CharField(max_length=30)
    color = models.CharField(max_length=30,null=True, blank=True)
    icon = models.ForeignKey(Icon,on_delete=models.RESTRICT,null=True, blank=True)
    cercle_icon = models.ImageField(upload_to=get_upload_path_layer_icon, null=True, blank=True)
    square_icon = models.ImageField(upload_to=get_upload_path_layer_icon, null=True, blank=True)
    raster_icon = models.ImageField(upload_to=get_upload_path_layer_icon, null=True, blank=True)

