import os
import re
from django.db import models

def get_upload_path(instance, filename):
    category = re.sub('[^A-Za-z0-9]+', '', instance.category)
    return os.path.join(category, filename)
    
class TagsIcon(models.Model):
    name = models.CharField(max_length=200)
    
class Icon (models.Model):
    """ an Icon in svg """
    
    icon_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    category = models.TextField(null=False,default='Custom')
    attribution = models.TextField(null=True)
    path = models.FileField(blank=False, null=False,default=None,upload_to=get_upload_path)
    tags = models.ManyToManyField(TagsIcon, blank=True)

    class meta :
        db_table = "icon"
        unique_together = ('name', 'category',)

