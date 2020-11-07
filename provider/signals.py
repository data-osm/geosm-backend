from .models import Vector
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=Vector)
def updateStateVectorProvider(sender, instance, **kwargs):
    if instance.table is not None and instance.shema is not None and instance.id_server is not None and instance.url_server is not None:
        instance.state ='good'
    elif instance.table is not None and instance.shema is not None and (instance.id_server is None and instance.url_server is None):
        instance.state ='not_working'
    elif instance.table is  None and instance.shema is  None:
        instance.state ='action_require'
    else:
        instance.state ='unknow'