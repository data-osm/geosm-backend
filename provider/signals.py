from .models import Vector
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .manageOsmDataSource import manageOsmDataSource
from .qgis.manageVectorLayer import removeLayer

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

@receiver(post_delete, sender=Vector)
def deleteStateVectorProvider(sender, instance:Vector, **kwargs):
    """Execute just after and vector provider is deleted Use delete his table in the DB and remove it in the QGIS projetct
        If we do not succed to remove it in QGIS project, we dont't delete the table. This will make sure our QGIS project don't have invalid layers !
    Args:
        sender ([type]): 
        instance (Vector): The vector provider that have already been deleted
    """
    if removeLayer(instance.url_server,instance.id_server).error == False:
        manageOsmDataSource(instance.provider_vector_id).deleteDataSource(instance)
    
