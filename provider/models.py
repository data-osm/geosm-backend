from django.contrib.gis.db import models
# Create your models here.

class geometryType(models.TextChoices):
    Polygon = 'Polygon'
    Point = 'Point'
    LineString = 'LineString'
class protocolCartoChoice (models.TextChoices):
    wmts='wmts'
    wms='wms'
    wfs='wfs'

class Vector(models.Model):
    """ model of a vector provider : data is store in a shema and table """
    provider_vector_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    table = models.TextField()
    """ the table where data are store """
    shema = models.TextField()
    """ the shema where data are store """
    geometry_type = models.CharField(
        max_length=11,
        choices=geometryType.choices
    )
    """ the geometry_type of the querry """
    url_server = models.URLField(null=True)
    """ url of the carto server """
    id_server = models.CharField(max_length=50)
    """ identifiant of this ressource in the carto server """
    extent = models.TextField(null=True)
    """ extent of this ressource """
    z_min = models.IntegerField(null=True)
    z_max = models.IntegerField(null=True)
    count = models.IntegerField(null=True)
    """ number of rows of this ressources """
    total_lenght = models.IntegerField(null=True)
    """ total lenght of the ressource if geometry type is LineString """
    total_area = models.IntegerField(null=True)
    """ total lenght of the ressource if geometry type is LineString """
    epsg = models.IntegerField()
    
class External (models.Model) :
    """ model of a external provider : data are not stre in the app DB"""
    provider_external_id  =  models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    protocol_carto = models.CharField(max_length=5,choices=protocolCartoChoice.choices)
    url_server = models.URLField(null=True)
    """ url of the carto server """
    id_server = models.CharField(max_length=50)
    """ identifiant of this ressource in the carto server """
    extent = models.TextField(null=True)
    """ extent of this ressource """
    z_min = models.IntegerField(null=True)
    z_max = models.IntegerField(null=True)
    epsg = models.IntegerField()

class Style (models.Model):
    """ model that store name, qml, ol style of a provider (raster and vector) """
    provider_style_id = models.IntegerField(primary_key=True) 
    name = models.CharField(max_length=50)
    qml = models.TextField()
    ol = models.TextField()
    pictogram = models.ImageField()
    vector_id = models.ForeignKey(Vector,on_delete=models.CASCADE)