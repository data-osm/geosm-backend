from .models import Querry
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.dispatch import receiver
from provider.manageOsmDataSource import manageOsmDataSource
from geosmBackend.type import AddVectorLayerResponse
from provider.qgis.manageVectorLayer import removeLayer

@receiver(pre_save, sender=Querry)
def updateStateQuerryProvider(sender, instance:Querry, **kwargs):
    """Add or update the datasource in the vector provider
    Args:
        sender ([type]):
        instance (Querry): Querry provider that will be saved
    """

    if instance._state.adding:
        responseManageDataSource:AddVectorLayerResponse = manageOsmDataSource(instance.provider_vector_id).createDataSource(instance)
    else:
        responseManageDataSource:AddVectorLayerResponse = manageOsmDataSource(instance.provider_vector_id).updateDataSource(instance)

    if responseManageDataSource.error:
        raise Exception(str(responseManageDataSource.msg)+' : '+str(responseManageDataSource.description))

@receiver(pre_delete, sender=Querry)
def deleteStateVectorProvider(sender, instance:Querry, **kwargs):
    """Execute just after and vector provider is deleted Use to delete his table in the DB and remove it in the QGIS projetct
        If we do not succed to remove it in QGIS project, we dont't delete the table. This will make sure our QGIS project don't have invalid layers !
    Args:
        sender ([type]): 
        instance (Querry): The vector provider that have already been deleted
    """
    
    if removeLayer(instance.provider_vector_id.url_server,instance.provider_vector_id.id_server).error == False:
        manageOsmDataSource(instance.provider_vector_id).deleteDataSource()
    
    