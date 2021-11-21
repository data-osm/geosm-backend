import os
import re
from django.db import models
from django.contrib.postgres.fields import ArrayField
from provider.models import Vector, External, Style
from .subModels.icon import Icon
from genericIcon.models import Picto
from tracking_fields.decorators import track
# Create your models here.

class groupType (models.TextChoices):
    ''' differents group types that exists '''
    thematiques='thematiques'
    base_maps='base_maps'

class protocolCartoChoice (models.TextChoices):
    wmts='wmts'
    wms='wms'
    wfs='wfs'

class protocolBaseMapChoice (models.TextChoices):
    wmts='wmts'
    wms='wms'
    
def get_upload_path(instance, filename):
    category = re.sub('[^A-Za-z0-9]+', '', instance.category)
    return os.path.join(category, filename)
    

def get_upload_path_group_icon (instance, filename):
    return os.path.join('group', instance.name+'.png')

def get_upload_path_layer_icon (instance, filename):
    return os.path.join('layer', instance.name+'.png')

@track('name', 'url', 'identifiant', 'attribution')
class Base_map (models.Model):
    name = models.CharField(max_length=200)
    url = models.TextField()
    protocol_carto = models.CharField(max_length=5,choices=protocolBaseMapChoice.choices)
    identifiant = models.TextField(null=True, blank=True)
    attribution = models.TextField(null=True, blank=True)
    picto = models.ForeignKey(Picto, on_delete=models.CASCADE)
    principal = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
@track('name', 'color', 'icon__name', 'icon_path')
class Group (models.Model):
    """ A group that  contains sub group and a sub group contains layer """

    class Meta:
        db_table = "group"
        """ specified name of table """

    group_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=30)
    icon = models.ForeignKey(Icon,on_delete=models.RESTRICT)
    type_group = models.CharField(max_length=50, choices=groupType.choices)
    icon_path = models.FileField(blank=False, null=False, upload_to=get_upload_path_group_icon)
    order = models.IntegerField(blank=False, null=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

@track('name', 'group_id__name')
class Map (models.Model):
    """ A map is compose of group """
    map_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    group_id = models.ManyToManyField(Group, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, null=True)

class Default_map (models.Model):
    """ the default map: this will be display as default in the portail """
    map_id = models.ForeignKey(Map, on_delete=models.CASCADE)

@track('name', 'group__name')
class Sub (models.Model):
    """ A sub group that contains layers. It belong to a group """
    group_sub_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    group = models.ForeignKey(Group,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

@track('name', 'color', 'icon_color', 'icon_background', 'icon_background')
class Layer (models.Model):
    """ A layer that reference to one or may provider of different types """

    layer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    protocol_carto = models.CharField(max_length=5,choices=protocolCartoChoice.choices)
    color = models.CharField(max_length=30)
    icon_color = models.CharField(max_length=30,null=True, blank=True)
    icon = models.ForeignKey(Icon,on_delete=models.RESTRICT)
    icon_background = models.BooleanField(default=True)
    cercle_icon = models.ImageField(upload_to=get_upload_path_layer_icon)
    square_icon = models.ImageField(upload_to=get_upload_path_layer_icon)
    description = models.TextField(null=True)
    opacity = models.BooleanField(default=True)
    metadata_cap = models.BooleanField(default=True)
    share = models.BooleanField(default=True)
    sub = models.ForeignKey(Sub,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

@track('vp_id__name', 'vs_id__name', 'ordre')
class Layer_provider_style(models.Model):
    layer_id = models.ForeignKey(Layer,on_delete=models.CASCADE)
    vp_id = models.ForeignKey(Vector,on_delete=models.CASCADE, blank=True, null=True)
    vs_id = models.ForeignKey(Style,on_delete=models.CASCADE, blank=True, null=True)
    ordre = models.IntegerField(default=1,blank=False, null=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class meta :
        unique_together = [['layer_id', 'vp_id']]

    def save(self, *args, **kwargs):
        numberOfLPSOfLayer = Layer_provider_style.objects.filter(layer_id=self.layer_id).count()+1
        self.ordre = numberOfLPSOfLayer
        super(Layer_provider_style,self).save(*args, **kwargs)

        
class Tags(models.Model):
    name = models.CharField(max_length=200)

@track('layer__name', 'description')
class Metadata(models.Model):
    layer = models.OneToOneField(Layer,on_delete=models.CASCADE)
    description = models.TextField(null=True,blank=True)
    tags = models.ManyToManyField(Tags, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
