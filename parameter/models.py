from typing import Iterable, Optional
from django.db import models
from provider.models import Vector
from group.models import Map
from tracking_fields.decorators import track
from django.db import connection, Error
from .documents import BoundarysDocument, refreshBoundaryDocument
from django.db import connection, Error
from asgiref.sync import async_to_sync
import threading

@track('name', 'vector__name')
class AdminBoundary (models.Model):
    """ model to save all administrative boundary with thier name"""
    admin_boundary_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    vector = models.ForeignKey(Vector,on_delete=models.CASCADE)
 
    def save(self, *args, **kwargs) -> None:
 
        try:
            responseSave =  super(AdminBoundary, self).save(*args, **kwargs)
        except Exception as e:
            raise Exception(e)

        boundarys = AdminBoundary.objects.select_related('vector').all()
        thread = threading.Thread(target=refreshBoundaryDocument,args=[boundarys])
        thread.daemon = True
        thread.start()

        return responseSave

    def delete(self, *args, **kwargs):
        try:
            responseDelete =  super(AdminBoundary, self).delete(*args, **kwargs)
        except Exception as e:
            raise Exception(e)

        boundarys = AdminBoundary.objects.select_related('vector').all()
        thread = threading.Thread(target=refreshBoundaryDocument,args=[boundarys])
        thread.daemon = True
        thread.start()

        return responseDelete

@track('map__name', 'extent__name', 'extent_pk')
class Parameter(models.Model):
    """ model to save all parameters of the application """

    parameter_id = models.BigAutoField(primary_key=True)
    map = models.ForeignKey(Map,on_delete=models.CASCADE,null=True, blank=True)
    extent = models.ForeignKey(Vector,on_delete=models.CASCADE, null=True, blank=True)
    extent_pk = models.BigIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk:
            previousParameter = Parameter.objects.get(pk=self.pk)
            if previousParameter.extent.pk != self.extent.pk:
                with connection.cursor() as cursor:
                    cursor.execute("DROP TABLE IF EXISTS public.extent")
                    cursor.execute("CREATE TABLE  public.extent AS select * from "+self.extent.shema+"."+self.extent.table)
                    cursor.execute("CREATE INDEX public_extent_geometry_idx ON  public.extent  USING GIST(geom) ")
                    cursor.execute("ALTER TABLE public.extent DROP COLUMN IF EXISTS id")
                    cursor.execute("ALTER TABLE public.extent ADD COLUMN id SERIAL PRIMARY KEY ")
        else:
            with connection.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS public.extent")
                cursor.execute("CREATE TABLE  public.extent AS select * from "+self.extent.shema+"."+self.extent.table)
                cursor.execute("CREATE INDEX public_extent_geometry_idx ON  public.extent  USING GIST(geom) ")
                cursor.execute("ALTER TABLE public.extent DROP COLUMN IF EXISTS id")
                cursor.execute("ALTER TABLE public.extent ADD COLUMN id SERIAL PRIMARY KEY ")
            self.extent_pk = 1

        super(Parameter,self).save(*args, **kwargs)

