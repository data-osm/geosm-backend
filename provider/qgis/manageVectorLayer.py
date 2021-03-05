import os
from os.path import join
from qgis.core import QgsVectorLayer, QgsProject, QgsApplication, QgsDataSourceUri, QgsCredentials, QgsProviderRegistry, QgsSettings
import traceback
from geosmBackend.type import OperationResponse, AddVectorLayerResponse
from django.conf import settings
from dataclasses import dataclass

os.environ["QT_QPA_PLATFORM"] = "offscreen"
QgsApplication.setPrefixPath("/usr/", True)
qgs = QgsApplication([], False)

OSMDATA = settings.OSMDATA
project_qgis_path = OSMDATA['project_qgis_path']


def _getProjectInstance(pathToQgisProject:str)->QgsProject:
    """ 
        Get project instance of an existing or not existing qgis project
        
        :param pathToQgisProject: the absolute path of the project
        :rparam pathToQgisProject: str

        :return: QGIS project instance
        :rtype: QgsProject
    """

    try:
        qgs.initQgis()
        project = QgsProject()
        project.read(join(project_qgis_path, pathToQgisProject))
        return project

    except:
        traceback.print_exc()
        return None

def _makeVectorLayerAvaibleOnWfs(project:QgsProject, vectorLayer:QgsVectorLayer )->bool:
    """
        Make a QgsVectorLayer avaible on WFS by adding it to WFSLayers entry

        :param project: the QGIS project instance
        :rparam project: QgsProject

        :param vectorLayer: the layer to make avaible on WFS
        :rparam vectorLayer: QgsVectorLayer

        :return: 
        :rtype: bool

    """

    if type(vectorLayer) == QgsVectorLayer and vectorLayer.isValid():
        WFSLayers = project.readListEntry('WFSLayers','')
        WFSLayersList = list(WFSLayers)[0]
        WFSLayersList.append(u'%s' % vectorLayer.id())
        project.writeEntry('WFSLayers', '',  WFSLayersList) 

        return True
    else:
        return False

def addVectorLayerFomPostgis(host:str, port:str, database:str, user:str, password:str, schema:str, table:str, geometryColumn:str, primaryKeyColumn:str, layerName:str, pathToQgisProject:str ) -> AddVectorLayerResponse:
    """
        Add a new layer in an existing or not existing QGIS project. The layer is from a postgres database

        :param host: host of the databse
        :rparam host: str

        :param port: port of the databse
        :rparam port: str

        :param database: name of the databse
        :rparam database: str

        :param user: user of the databse
        :rparam user: str

        :param password: password of the databse
        :rparam password: str

        :param schema: schema of the table in database
        :rparam schema: str
        

        :param table: table of the layer in databse
        :rparam table: str

        :param geometryColumn: geometryColumn of the table
        :rparam geometryColumn: str

        :param primaryKeyColumn: primary key of the table
        :rparam primaryKeyColumn: str

        :param layerName: Name of the layer in the QGIS project
        :rparam layerName: str

        :param pathToQgisProject: the absolute path of the project
        :rparam pathToQgisProject: str

        :rreturn AddVectorLayerResponse

    """
    response=AddVectorLayerResponse(
        error=False,
        msg="",
        description="",
        pathProject="",
        layerName="",
    )

    QGISProject = _getProjectInstance(pathToQgisProject)
    try:
    
        if QGISProject:
            uri = QgsDataSourceUri()
            # table="bar"
            uri.setConnection(host, port, database, user, password)
            # conn = QgsProviderRegistry.instance().providerMetadata('postgres').createConnection(uri.uri(False),{})
            # print(conn.tables(schema))
       
            uri.setDataSource(schema, table , geometryColumn, "",primaryKeyColumn)
            if len(QGISProject.mapLayersByName(layerName)) > 0 :
                layerName = layerName+'_'+str(len(QGISProject.mapLayersByName(layerName))+1)
                
            vectorLayer = QgsVectorLayer(uri.uri(False), layerName, "postgres")

            if vectorLayer.isValid():
                if QGISProject.addMapLayer(vectorLayer) is not None:
                    if _makeVectorLayerAvaibleOnWfs(QGISProject, vectorLayer):
                        response.error = QGISProject.write() != True
                        response.pathProject = pathToQgisProject
                        response.layerName = layerName
                    else:
                        response.error = True
                        response.msg = " Impossible to make layer avaible on WFS"
                else:
                    response.error = True
                    response.msg = " Impossible to add layer to the project"
            else:
                response.error = True
                response.msg = " The layer is not valid"
                response.description=uri.uri()
        else:
            response.error = True
            response.msg = "Impossible to load the project"

    except :
        traceback.print_exc()
        response.error = True
        response.msg = "An unexpected error has occurred"

    return response

def removeLayer(pathToQgisProject:str, layerName:str)->OperationResponse:
    """Remove all layers with have a specific layername in a QGIS project
    Todo:
        remove layer in wfsList

    Args:
        pathToQgisProject (str): path to the QGIS project
        layerName (str): name of the layer to remove

    Returns:
        OperationResponse

    """
    response=OperationResponse(
        error=False,
        msg="",
        description="",
    )

    QGISProject = _getProjectInstance(pathToQgisProject)
    try:
        if QGISProject:
            while len(QGISProject.mapLayersByName(layerName)) != 0 :
                QGISProject.removeMapLayer(QGISProject.mapLayersByName(layerName)[0])
            
            response.error = QGISProject.write() != True
            return response

        else:
            response.error = True
            response.msg = "Impossible to load the project"
    except:
        # traceback.print_exc()
        response.error = True
        response.msg = "An unexpected error has occurred"
