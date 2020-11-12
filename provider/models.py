from django.contrib.gis.db import models
# Create your models here.

class StateOfProvider(models.TextChoices):
    good = 'good'
    not_working = 'not_working'
    action_require = 'action_require'
    unknow = 'unknow'

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
    provider_vector_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50,null=True,default=None)
    table = models.TextField(max_length=15,null=True,default=None)
    """ the table where data are store """
    shema = models.TextField(max_length=15,null=True,default=None)
    """ the shema where data are store """
    geometry_type = models.CharField(
        max_length=11,
        choices=geometryType.choices
    )
    """ the geometry_type of the querry """
    url_server = models.URLField(null=True)
    """ url of the carto server """
    id_server = models.CharField(max_length=50,null=True,default=None)
    """ identifiant of this ressource in the carto server """
    extent = models.TextField(null=True)
    """ extent of this ressource """
    z_min = models.IntegerField(null=False,default=0)
    z_max = models.IntegerField(null=False,default=24)
    count = models.IntegerField(null=True)
    """ number of feature of this ressources """
    total_lenght = models.IntegerField(null=True)
    """ total lenght of the ressource if geometry type is LineString """
    total_area = models.IntegerField(null=True)
    """ total area of the ressource if geometry type is Polygon """
    epsg = models.IntegerField(null=True,default=None)
    state = models.CharField(
        max_length=20,
        choices=StateOfProvider.choices,
        null=True
    )
    
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

def get_custom_style_icon_path(instance, filename):
    directory = re.sub('[^A-Za-z0-9]+', '', 'custom_style_id')
    return os.path.join(directory, filename)

class Custom_style (models.Model):
    """ model that store custom and parametrable QGIS styles """
    custom_style_id = models.IntegerField(primary_key=True) 
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=400,blank=True)
    icon = models.FileField(blank=True, null=False,default=None,upload_to=get_custom_style_icon_path)
    class_name = models.CharField(max_length=50,blank=True)
    """ name of the class responsible to format QML """

class Style (models.Model):
    """ model that store name, qml, ol style of a provider (raster and vector) """
    provider_style_id = models.BigAutoField(primary_key=True) 
    name = models.CharField(max_length=50)
    qml = models.TextField()
    ol = models.TextField(blank=True)
    pictogram = models.ImageField(blank=True)
    vector_id = models.ForeignKey(Vector,on_delete=models.CASCADE)
    custom_style_id = models.ForeignKey(Custom_style,on_delete=models.SET_NULL,blank=True,null=True)