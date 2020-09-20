from django.db import models
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


class Icon (models.Model):
    """ an Icon in svg """
    class meta :
        db_table = "icon"
    icon_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200,unique=True)
    tags = models.TextField(null=True)

class Type (models.Model):
    """ A group type, like thematiques, base maps etc... """
    group_type_id = models.IntegerField(primary_key=True)
    key = models.CharField(max_length=50, choices=groupType.choices)
    display_name = models.CharField(max_length=50)
    description = models.CharField(max_length=50, null=True)

class Group (models.Model):
    """ A group that  contains sub group and a sub group contains layer """

    class Meta:
        db_table = "group"
        """ specified name of table """

    group_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=30)
    icon = models.ForeignKey(Icon,on_delete=models.RESTRICT)
    type_group = models.ForeignKey(Type,on_delete=models.CASCADE)

class sub (models.Model):
    """ A sub group that contains layers. It belong to a group """
    group_sub_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    group = models.ForeignKey(Group,on_delete=models.CASCADE)

class Layer (models.Model):
    """ A layer that reference to one or may provider of different types """

    layer_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    protocol_carto = models.CharField(max_length=5,choices=protocolCartoChoice.choices)
    color = models.CharField(max_length=30)
    icon = models.ForeignKey(Icon,on_delete=models.RESTRICT)
    cercle_icon = models.ImageField()
    square_icon = models.ImageField()
    description = models.TextField(null=True)
    opacity = models.BooleanField(default=True)
    metadata = models.BooleanField(default=True)
    share = models.BooleanField(default=True)
    vector_prov = models.ManyToManyField(Vector,blank=True)
    external_prov = models.ManyToManyField(External,blank=True)

