import os
from qgis.core import QgsVectorLayer, QgsProject, QgsApplication, QgsDataSourceUri, QgsCredentials, QgsProviderRegistry, QgsSettings
import traceback
from geosmBackend.type import OperationResponse
from dataclasses import dataclass
import tempfile
from django.db import connection, Error
from psycopg2.extensions import AsIs

os.environ["QT_QPA_PLATFORM"] = "offscreen"
QgsApplication.setPrefixPath("/usr/", True)
qgs = QgsApplication([], False)


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
        project.read(pathToQgisProject)
        return project

    except:
        traceback.print_exc()
        return None


def getQMLStyleOfLayer( layerName:str, pathToQgisProject:str)->OperationResponse:
    """ 
        insert in a column of a PG table the style of a layer : we will first write it in a file before read it and store in DB

        :param host: host of the database
        :rparam host: str

        :param port: port of the database
        :rparam port: str

        :param database: name of the database
        :rparam database: str

        :param user: user of the database
        :rparam user: str

        :param password: password of the database
        :rparam password: str

        :param schema: schema of the table in database
        :rparam schema: str
        
        :param table: table of the layer in database
        :rparam table: str

        :param pk_column: primary column of the table
        :rparam pk_column: str

        :param pk_value: value of the primary column of the table
        :rparam pk_value: str

        :param qml_column: qml_column that will store the qml content file
        :rparam qml_column: str

        :param layerName: Name of the layer in the QGIS project
        :rparam layerName: str

        :param pathToQgisProject: the absolute path of the project
        :rparam pathToQgisProject: str
    """
    response = OperationResponse(error=False,msg='',description='')

    QGISProject = _getProjectInstance(pathToQgisProject)

    try:
    
        if QGISProject:

            if len(QGISProject.mapLayersByName(layerName)) != 0:
                layer = QGISProject.mapLayersByName(layerName)[0]
                f = tempfile.NamedTemporaryFile()
                fileName = f.name+'.qml'
                layer.saveNamedStyle(fileName)
                qml_content = open(fileName, "r")

                response.data= str(qml_content.read())

            else:
                response.error = True
                response.msg = "No layer found with name : "+layerName

        else:
            response.error = True
            response.msg = "Impossible to load the project"

    except Exception as e:
        traceback.print_exc()
        response.error = True
        response.description = str(e)
        response.msg = "An unexpected error has occurred"

    return response