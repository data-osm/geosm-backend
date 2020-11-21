import os
from os.path import join
from qgis.core import QgsVectorLayer, QgsProject, QgsApplication, QgsDataSourceUri, QgsCredentials, QgsProviderRegistry, QgsSettings, QgsMapLayerStyle
import traceback
from dataclasses import dataclass
import tempfile
from qgis.PyQt.QtXml import QDomDocument, QDomElement
from qgis.PyQt.QtCore import QFile, QIODevice
import logging
from geosmBackend.type import OperationResponse, GetQMLStyleOfLayerResponse
from geosmBackend.settings import OSMDATA
log = logging.getLogger(__name__)

os.environ["QT_QPA_PLATFORM"] = "offscreen"
QgsApplication.setPrefixPath("/usr/", True)
qgs = QgsApplication([], False)

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


def getQMLStyleOfLayer( layerName:str, pathToQgisProject:str)->GetQMLStyleOfLayerResponse:
    """ 
        insert in a column of a PG table the style of a layer : we will first write it in a file before read it and store in DB

        :param layerName: Name of the layer in the QGIS project
        :rparam layerName: str

        :param pathToQgisProject: the absolute path of the project
        :rparam pathToQgisProject: str
    """
    response = GetQMLStyleOfLayerResponse(error=False,msg='',description='',qmlContent=None,qmlPath=None)

    QGISProject = _getProjectInstance(pathToQgisProject)

    try:
    
        if QGISProject:

            if len(QGISProject.mapLayersByName(layerName)) != 0:
                layer = QGISProject.mapLayersByName(layerName)[0]
                f = tempfile.NamedTemporaryFile()
                fileName = f.name+'.qml'
                layer.saveNamedStyle(fileName)
                qml_content = open(fileName, "r")

                response.qmlPath= fileName
                response.qmlContent= str(qml_content.read())
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

def removeStyle(layerName:str, pathToQgisProject:str, styleName:str )->OperationResponse:
    """ Remove a style from a layer in QGIS 
    Args:
        layerName (str): name of the layer
        pathToQgisProject (str): path to the QGIS project
        styleName (str): name of the  styleb to remove
    
    Returns:
        OperationResponse
    """

    response = OperationResponse(error=False,msg='',description='')

    QGISProject = _getProjectInstance(pathToQgisProject)

    try:
        if QGISProject:
            if len(QGISProject.mapLayersByName(layerName)) != 0:
                layer = QGISProject.mapLayersByName(layerName)[0]
                styleManager = layer.styleManager()
                if styleName in styleManager.styles():
                    response.error = styleManager.removeStyle(styleName) != True
                    if response.error == False:
                        QGISProject.write()
            else:
                response.error = True
                response.msg = "Impossible to retrieve layer : "+str(layerName)
        else:
            response.error = True
            response.msg = "Impossible to load the project"

        return response

    except Exception as e:
        traceback.print_exc()
        response.error = True
        response.description = str(e)
        response.msg = "An unexpected error has occurred"

def updateStyle(layerName:str, pathToQgisProject:str, styleName:str, newStyleName:str, QML:str)->OperationResponse:
    """ Remove a style from a layer in QGIS 
    Args:
        layerName (str): name of the layer
        pathToQgisProject (str): path to the QGIS project
        styleName (str): name of the  styleb to remove
        newStyleName (str): new name of the style
    
    Returns:
        OperationResponse
    """

    response = OperationResponse(error=False,msg='',description='')

    QGISProject = _getProjectInstance(pathToQgisProject)

    try:
        if QGISProject:
            if len(QGISProject.mapLayersByName(layerName)) != 0:
                layer = QGISProject.mapLayersByName(layerName)[0]
                styleManager = layer.styleManager()

                if styleName != newStyleName :
                    response.error = styleManager.renameStyle(styleName, newStyleName) != True
                    if response.error:
                        response.msg = "Can not rename style name "+str(styleName)+" to "+str(newStyleName)

                if QML is not None and response.error == False:
                    style = styleManager.style(newStyleName)
                    if style:
                        style.clear()
                        doc = QDomDocument()
                        elem = doc.createElement("style-data-som")
                        xmlStyle:QDomDocument = QDomDocument()
                        xmlStyle.setContent(QML)
                        elem.appendChild(xmlStyle.childNodes().at(0))
                        
                        style.readXml(elem)
                        response.error = style.isValid() != True
                        if response.error:
                            response.error = True
                            response.msg = "The QML file is not valid !"
                    else:
                        response.error = True
                        response.msg = " Impossible to retrive style name "+str(newStyleName)
            else:
                response.error = True
                response.msg = "Impossible to retrieve layer : "+str(layerName)
        else:
            response.error = True
            response.msg = "Impossible to load the project"

        if response.error == False:
            QGISProject.write()
        return response

    except Exception as e:
        traceback.print_exc()
        response.error = True
        response.description = str(e)
        response.msg = "An unexpected error has occurred"

def _addStyleToLayer(layerName:str, pathToQgisProject:str, styleName:str, QML:str)->OperationResponse:
    """Add or update style from a qml file or an XML of QML on a layer. The new style will have a new name
    As the method addStyle in QGIS API describred here https://qgis.org/api/qgsmaplayerstylemanager_8cpp_source.html#l00109 : we can not add a style with name that already exist
    So here, if a name style already exist in the QgsMapLayerStyleManager, we override it
    Args:
        layerName (str): name of the layer
        pathToQgisProject (str): path to the QGIS project
        styleName (str): name of the new style
        QMLPath (str): content of a qml file
    
    Returns:
        OperationResponse
    """    

    response = OperationResponse(error=False,msg='',description='')

    QGISProject = _getProjectInstance(pathToQgisProject)

    try:
        if QGISProject:
            if len(QGISProject.mapLayersByName(layerName)) != 0:
                layer = QGISProject.mapLayersByName(layerName)[0]
                styleManager = layer.styleManager()
                newStyle = QgsMapLayerStyle()

                doc = QDomDocument()
                elem = doc.createElement("style-data-som")

                xmlStyle:QDomDocument = QDomDocument()
                xmlStyle.setContent(QML)
                elem.appendChild(xmlStyle.childNodes().at(0))
                
                newStyle.readXml(elem)

                if newStyle.isValid():
                    
                    if styleName not in styleManager.styles():
                        response.error = styleManager.addStyle(styleName,newStyle) != True
                    else:
                        oldStyle:QgsMapLayerStyle = styleManager.style(styleName)
                        oldStyle.clear()
                        oldStyle.readXml(elem)
                        response.error = oldStyle.isValid() != True
                    
                    # print(styleManager.styles())
                    if response.error == True:
                        response.msg = "Can not add the new style"
                    else:
                        QGISProject.write()
                else:
                    response.error = True
                    response.msg = "The QML file is not valid !"
            else:
                response.error = True
                response.msg = "Impossible to retrieve layer : "+str(layerName)
        else:
            response.error = True
            response.msg = "Impossible to load the project"

    except Exception as e:
        traceback.print_exc()
        response.error = True
        response.description = str(e)
        response.msg = "An unexpected error has occurred"

    return response

def addStyleQMLFromFileToLayer(layerName:str, pathToQgisProject:str, styleName:str, QMLPath:str)->OperationResponse:
    """Add or update style from a qml file on a layer. The new style will have a new name

    Args:
        layerName (str): name of the layer
        pathToQgisProject (str): path to the QGIS project
        styleName (str): name of the new style
        QMLPath (str): path to the QML
    
    Returns:
        OperationResponse
    """  

    response = OperationResponse(error=False,msg='',description='')

    if os.path.exists(QMLPath) and os.path.isfile(QMLPath) :
        qFile= QFile(QMLPath)
        if qFile.open(QIODevice.ReadOnly):
            response = _addStyleToLayer(layerName, pathToQgisProject, styleName, qFile)
    else:
        response.error = True
        response.msg = "The QML file does not exist"
    
    return response

def addStyleQMLFromStringToLayer(layerName:str, pathToQgisProject:str, styleName:str, QMLString:str)->OperationResponse:
    """Add or update style from an string of QML on a layer. The new style will have a new name

    Args:
        layerName (str): name of the layer
        pathToQgisProject (str): path to the QGIS project
        styleName (str): name of the new style
        QMLString (str): path to the QML
    
    Returns:
        OperationResponse
    """  

    response = _addStyleToLayer(layerName, pathToQgisProject, styleName, QMLString)
    return response