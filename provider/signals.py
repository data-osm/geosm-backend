from .models import Vector
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .manageOsmDataSource import manageOsmDataSource

@receiver(pre_save, sender=Vector)
def updateStateVectorProvider(sender, instance:Vector, **kwargs):
    """Execute just before and vector provider is add or updated Use to evaluate the state of the vector provider

    Args:
        sender ([type]):
        instance (Vector): Vector provider that will be saved
    """
    if instance.table is not None and instance.shema is not None and instance.id_server is not None and instance.url_server is not None:
        instance.state ='good'
    elif instance.table is not None and instance.shema is not None and (instance.id_server is None and instance.url_server is None):
        instance.state ='not_working'
    elif instance.table is  None and instance.shema is  None:
        instance.state ='action_require'
    else:
        instance.state ='unknow'

    
