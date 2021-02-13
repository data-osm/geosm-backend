import os
import re
from django.db import models
from django.contrib.postgres.fields import ArrayField
from provider.models import Vector, External, Style
# Create your models here.

class groupType (models.TextChoices):
    ''' differents group types that exists '''
    thematiques='thematiques'
    base_maps='base_maps'

class protocolCartoChoice (models.TextChoices):
    wmts='wmts'
    wms='wms'
    wfs='wfs'



def get_upload_path(instance, filename):
    category = re.sub('[^A-Za-z0-9]+', '', instance.category)
    return os.path.join(category, filename)
    
def get_upload_path_group_icon (instance, filename):
    return os.path.join('group', instance.name+'.png')

def get_upload_path_layer_icon (instance, filename):
    return os.path.join('layer', instance.name+'.png')

class Icon (models.Model):
    """ an Icon in svg """
    
    icon_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    tags = ArrayField(
            models.CharField(max_length=50, blank=True),
            size=10,
            blank=True,
            null=True
    )
    category = models.TextField(null=False,default='Custom')
    attribution = models.TextField(null=True)
    path = models.FileField(blank=False, null=False,default=None,upload_to=get_upload_path)

    class meta :
        db_table = "icon"
        unique_together = ('name', 'category',)

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



class Map (models.Model):
    """ A map is compose of group """
    map_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    group_id = models.ManyToManyField(Group, blank=True)

class Default_map (models.Model):
    """ the default map: this will be display as default in the portail """
    map_id = models.ForeignKey(Map, on_delete=models.CASCADE)

class Sub (models.Model):
    """ A sub group that contains layers. It belong to a group """
    group_sub_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    group = models.ForeignKey(Group,on_delete=models.CASCADE)

class Layer (models.Model):
    """ A layer that reference to one or may provider of different types """

    layer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    protocol_carto = models.CharField(max_length=5,choices=protocolCartoChoice.choices)
    color = models.CharField(max_length=30)
    icon = models.ForeignKey(Icon,on_delete=models.RESTRICT)
    cercle_icon = models.ImageField(upload_to=get_upload_path_layer_icon)
    square_icon = models.ImageField(upload_to=get_upload_path_layer_icon)
    description = models.TextField(null=True)
    opacity = models.BooleanField(default=True)
    metadata = models.BooleanField(default=True)
    share = models.BooleanField(default=True)
    sub = models.ForeignKey(Sub,on_delete=models.CASCADE)

class Layer_provider_style(models.Model):
    layer_id = models.ForeignKey(Layer,on_delete=models.CASCADE)
    vp_id = models.ForeignKey(Vector,on_delete=models.CASCADE, blank=True, null=True)
    vs_id = models.ForeignKey(Style,on_delete=models.CASCADE, blank=True, null=True)
    ordre = models.IntegerField(default=1,blank=False, null=False)

    class meta :
        unique_together = [['layer_id', 'vp_id']]

    def save(self, *args, **kwargs):
        numberOfLPSOfLayer = Layer_provider_style.objects.filter(layer_id=self.layer_id).count()+1
        self.ordre = numberOfLPSOfLayer
        super(Layer_provider_style,self).save(*args, **kwargs)

        
