from django.conf import settings
from django.contrib.gis.db import models
import re
import os
import uuid
from django.core.files import File
from django.core.files.base import ContentFile
from .qgis.manageStyle import addStyleQMLFromStringToLayer, removeStyle, updateStyle, getImageFromSymbologieOfLayer
from django.contrib.postgres.fields import ArrayField
from tracking_fields.decorators import track
from group.subModels.icon import Icon
from pathlib import Path
from django.core.files.storage import default_storage

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

@track('name', 'url_server', 'id_server', 'path_qgis', 'table', 'count')
class Vector(models.Model):
    """ model of a vector provider : data is store in a shema and table """
    provider_vector_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50,null=True,default=None, unique=True)
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
    path_qgis = models.CharField(max_length=250,null=True,blank=True,default=None)
    """ Path to QGIS project """
    extent = ArrayField(
        models.FloatField(),
        size=4,
        null=True,
        blank=True,
        default=None
    )
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
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('id_server', 'path_qgis',)
    
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
    directory = re.sub('[^A-Za-z0-9]+', '', instance.custom_style_id)
    return os.path.join('pictoQgis', filename)

def get_custom_qml_path(instance, filename):
    directory = re.sub('[^A-Za-z0-9]+', '', 'qml')
    return os.path.join(directory, instance.name+'_'+str(instance.pk)+'.qml')

class Custom_style (models.Model):
    """ model that store custom and parametrable QGIS styles """
    custom_style_id = models.BigAutoField(primary_key=True) 
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=400,blank=True)
    icon = models.ImageField(blank=True, null=False,default=None,upload_to='customStyle/')
    fucntion_name = models.CharField(max_length=50,blank=True)
    """ name of the class responsible to format QML """
    geometry_type = models.CharField(
        max_length=11,
        choices=geometryType.choices
    )

@track('name', 'qml_file', 'qml')
class Style (models.Model):
    """ model that store name, qml, ol style of a provider (raster and vector) """
    provider_style_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    qml = models.TextField()
    ol = models.TextField(blank=True)
    pictogram = models.ImageField(blank=True)
    provider_vector_id = models.ForeignKey(Vector,on_delete=models.CASCADE)
    custom_style_id = models.ForeignKey(Custom_style,on_delete=models.SET_NULL,blank=True,null=True)
    icon = models.ForeignKey(Icon,on_delete=models.RESTRICT,null=True, blank=True)
    qml_file = models.FileField(blank=True, null=True,default=None,upload_to=get_custom_qml_path)
    parameters = models.JSONField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    """ just use in order to write the content of the file in the field qml. ie: the file never exist"""
    class Meta:
        unique_together = ('name', 'provider_vector_id',)

    def save(self, *args, **kwargs):
        """ save or update a style """

        self.name = re.sub('[^A-Za-z0-9]+', '', self.name)
        
        if self.pk:
            
            previousStyle = Style.objects.get(pk=self.pk)
            self.name = previousStyle.name
            print(previousStyle.qml_file, self.qml_file,previousStyle.qml_file != self.qml_file)
            if previousStyle.qml_file != self.qml_file:
                qml_content = None
                self.qml_file.open(mode="r")
                qml_content = self.qml_file.read()
                self.qml= qml_content

                responseUpdateStyle = updateStyle(self.provider_vector_id.id_server, self.provider_vector_id.path_qgis, previousStyle.name, self.name, qml_content)

                if responseUpdateStyle.error:
                    raise Exception(responseUpdateStyle.msg+" : "+str(responseUpdateStyle.description))

                Path(os.path.join(settings.MEDIA_ROOT,'pictoQgis')).mkdir(parents=True, exist_ok=True)
                if os.path.exists(self.pictogram.name):
                    path = self.pictogram.name
                else:
                    path = os.path.join(settings.MEDIA_ROOT,'pictoQgis', str(uuid.uuid4())+'.png')

                responsePicto = getImageFromSymbologieOfLayer(self.provider_vector_id.id_server, self.provider_vector_id.path_qgis, self.name, path)
                self.pictogram.name = path

        else:
         
            self.qml_file.open(mode="rb")
            qml_content = self.qml_file.read()
            if isinstance(qml_content, str) == False:
                qml_content = qml_content.decode("utf-8")
            self.qml= qml_content

            tmp_file = os.path.join(settings.TEMP_URL, str(uuid.uuid1())+'.qml')
            default_storage.save(tmp_file, ContentFile(qml_content))
            
            responseAddStyle = addStyleQMLFromStringToLayer(self.provider_vector_id.id_server, self.provider_vector_id.path_qgis, self.name, qml_content, tmp_file)
            if responseAddStyle.error:
                raise Exception(responseAddStyle.msg+" : "+str(responseAddStyle.description))
            Path(os.path.join(settings.MEDIA_ROOT,'pictoQgis')).mkdir(parents=True, exist_ok=True)
            pictoPath = os.path.join('pictoQgis', str(uuid.uuid4())+'.png')
            path = os.path.join(settings.MEDIA_ROOT,pictoPath)
              
            responsePicto = getImageFromSymbologieOfLayer(self.provider_vector_id.id_server, self.provider_vector_id.path_qgis, self.name, path)
            self.pictogram.name = pictoPath
            
        super(Style,self).save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        """ delete a style """
        responseRemoveStyle = removeStyle(self.provider_vector_id.id_server, self.provider_vector_id.path_qgis, self.name)
        if responseRemoveStyle.error :
            raise Exception(responseRemoveStyle.msg+" : "+str(responseRemoveStyle.description))
        super(Style,self).delete(*args, **kwargs)
