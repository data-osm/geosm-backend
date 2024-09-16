import os
from os.path import join

from django.core.files.base import File
from qgis.core import (
    QgsRenderContext,
    QgsCategorizedSymbolRenderer,
    QgsProject,
)
import traceback
import tempfile
from qgis.PyQt.QtXml import QDomDocument
from qgis.PyQt.QtCore import QFile, QIODevice, QSize
import logging
from geosmBackend.type import OperationResponse, GetQMLStyleOfLayerResponse
from django.conf import settings

from utils.exeption import ExplicitException

# from qgis.utils import iface

log = logging.getLogger(__name__)
OSMDATA = settings.OSMDATA


class UpdateStyleException(ExplicitException):
    pass


class RemoveStyleException(ExplicitException):
    pass


class AddStyleException(ExplicitException):
    pass


class QMLStyleOfLayerException(ExplicitException):
    pass


class ThumbnailFromStyleException(ExplicitException):
    pass


project_qgis_path = OSMDATA["project_qgis_path"]


def _get_project_instance(path_to_qgis_project: str) -> QgsProject:
    """
    Get project instance of an existing or not existing qgis project

    :param path_to_qgis_project: the absolute path of the project
    :rparam path_to_qgis_project: str

    :return: QGIS project instance
    :rtype: QgsProject
    """

    try:
        project = QgsProject()
        project.read(join(project_qgis_path, path_to_qgis_project))
        return project

    except Exception:
        traceback.print_exc()
        return None


def get_qml_style_of_layer(
    layer_name: str, path_to_qgis_project: str
) -> GetQMLStyleOfLayerResponse:
    """
    insert in a column of a PG table the style of a layer : we will first write it in a file before read it and store in DB

    :param layer_name: Name of the layer in the QGIS project
    :rparam layer_name: str

    :param path_to_qgis_project: the absolute path of the project
    :rparam path_to_qgis_project: str

    Raise :
        QMLStyleOfLayerException
    """
    response = GetQMLStyleOfLayerResponse(
        error=False, msg="", description="", qmlContent=None, qml_path=None
    )

    qgis_project = _get_project_instance(path_to_qgis_project)

    try:

        if qgis_project:

            if len(qgis_project.mapLayersByName(layer_name)) != 0:
                layer = qgis_project.mapLayersByName(layer_name)[0]
                f = tempfile.NamedTemporaryFile()
                fileName = f.name + ".qml"
                layer.saveNamedStyle(fileName)
                qml_content = open(fileName, "r")

                response.qml_path = fileName
                response.qmlContent = str(qml_content.read())
            else:
                raise QMLStyleOfLayerException(
                    msg=f"No layer found with name {layer_name} in project {project_qgis_path}",
                    description="",
                )

        else:
            raise QMLStyleOfLayerException(
                msg=f"Failed to load project {project_qgis_path}", description=""
            )
    except QMLStyleOfLayerException:
        raise
    except Exception as e:
        raise QMLStyleOfLayerException(
            msg=f"An unexpected error has occurred {project_qgis_path}", description=""
        ) from e

    return response


def remove_style(
    layer_name: str, path_to_qgis_project: str, style_name: str
) -> OperationResponse:
    """Remove a style from a layer in QGIS
    Args:
        layer_name (str): name of the layer
        path_to_qgis_project (str): path to the QGIS project
        style_name (str): name of the  styleb to remove

    Returns:
        OperationResponse
    Raise :
        RemoveStyleException
    """

    response = OperationResponse(error=False, msg="", description="", data=None)

    qgis_project = _get_project_instance(path_to_qgis_project)

    try:
        if qgis_project:
            if len(qgis_project.mapLayersByName(layer_name)) != 0:
                layer = qgis_project.mapLayersByName(layer_name)[0]
                style_manager = layer.styleManager()
                if style_name in style_manager.styles():
                    response.error = style_manager.removeStyle(style_name) is not True
                    if response.error is False:
                        qgis_project.write()
            else:
                raise RemoveStyleException(msg=f"Could not retrive layer {layer_name} ")
        else:
            raise QMLStyleOfLayerException(
                msg=f"Failed to load project {project_qgis_path}", description=""
            )

        return response
    except QMLStyleOfLayerException:
        raise
    except Exception as e:
        raise QMLStyleOfLayerException(
            msg="An unexpected error has occurred", description=""
        ) from e


def update_style(
    layer_name: str,
    path_to_qgis_project: str,
    style_name: str,
    new_style_name: str,
    qml: str,
) -> OperationResponse:
    """Remove a style from a layer in QGIS
    Args:
        layer_name (str): name of the layer
        path_to_qgis_project (str): path to the QGIS project
        style_name (str): name of the  style to remove
        new_style_name (str): new name of the style

    Returns:
        OperationResponse
    Raise :
        updateStyleException
    """

    response = OperationResponse(error=False, msg="", description="", data=None)

    qgis_project = _get_project_instance(path_to_qgis_project)

    try:
        if qgis_project:
            if len(qgis_project.mapLayersByName(layer_name)) != 0:
                layer = qgis_project.mapLayersByName(layer_name)[0]
                style_manager = layer.styleManager()

                if style_name != new_style_name:
                    response.error = (
                        style_manager.renameStyle(style_name, new_style_name)
                        is not True
                    )
                    if response.error:
                        response.msg = (
                            "Can not rename style name "
                            + str(style_name)
                            + " to "
                            + str(new_style_name)
                        )

                if qml is not None and response.error is False:
                    style = style_manager.style(new_style_name)
                    if style and style_manager.setCurrentStyle(new_style_name):
                        style.clear()
                        doc = QDomDocument()
                        elem = doc.createElement("style-data-som")
                        xml_style: QDomDocument = QDomDocument()
                        xml_style.setContent(qml)
                        elem.appendChild(xml_style.childNodes().at(0))

                        style.readXml(elem)
                        response.error = style.isValid() is not True
                        if response.error:
                            raise UpdateStyleException(
                                msg=f"The QML file is not valid for layer {layer_name} in project {path_to_qgis_project}",
                                description="",
                            )
                        else:
                            style.writeToLayer(layer)
                    else:
                        raise UpdateStyleException(
                            msg=f" Impossible to retrieve style name {new_style_name} ",
                            description="",
                        )

            else:
                raise UpdateStyleException(
                    msg=f" Impossible to retrieve layer {layer_name} in project {path_to_qgis_project}",
                    description="",
                )
        else:
            raise UpdateStyleException(
                msg=f"Failed to load project {path_to_qgis_project}", description=""
            )

        if response.error is False:
            qgis_project.write()
        return response

    except UpdateStyleException:
        raise
    except Exception as e:
        raise UpdateStyleException(
            msg=f"An unexpected error has occurred when trying to update style of layer {layer_name} in project  {path_to_qgis_project}",
            description="",
        ) from e


def _add_style_to_layer(
    layer_name: str, path_to_qgis_project: str, style_name: str, qml: str, qml_file: str
) -> OperationResponse:
    """Add or update style from a qml file or an XML of QML on a layer. The new style will have a new name
    As the method addStyle in QGIS API described here https://qgis.org/api/qgsmaplayerstylemanager_8cpp_source.html#l00109 : we can not add a style with name that already exist
    So here, if a name style already exist in the QgsMapLayerStyleManager, we override it
    Args:
        layer_name (str): name of the layer
        path_to_qgis_project (str): path to the QGIS project
        style_name (str): name of the new style

    Returns:
        OperationResponse
    Raise:
        AddStyleException
    """

    response = OperationResponse(error=False, msg="", description="", data=None)

    qgis_project = _get_project_instance(path_to_qgis_project)

    try:
        if qgis_project:
            if len(qgis_project.mapLayersByName(layer_name)) != 0:
                layer = qgis_project.mapLayersByName(layer_name)[0]
                style_manager = layer.styleManager()
                # newStyle = QgsMapLayerStyle()

                # doc = QDomDocument()
                # elem = doc.createElement("style-data-som")

                # xmlStyle:QDomDocument = QDomDocument()
                # xmlStyle.setContent(QML)
                # elem.appendChild(xmlStyle.childNodes().at(0))

                # newStyle.readXml(elem)

                if True:

                    if style_name not in style_manager.styles():
                        response.error = (
                            style_manager.addStyleFromLayer(style_name) is not True
                        )
                        if style_manager.setCurrentStyle(style_name):
                            mess, res = layer.loadNamedStyle(qml_file)
                            response.error = res is not True
                            response.description = mess
                        else:
                            raise AddStyleException(
                                msg="Could not add the new style",
                                description="Try to change the name of your style",
                            )

                    if response.error is True:
                        raise AddStyleException(
                            msg="Could not add the new style", description=""
                        )
                    else:

                        qgis_project.write()

                        qgis_project = _get_project_instance(path_to_qgis_project)
                        layer = qgis_project.mapLayersByName(layer_name)[0]
                        style_manager = layer.styleManager()

                        if style_name not in style_manager.styles():
                            raise AddStyleException(
                                msg="An unknown error has occurred ", description=""
                            )

                else:
                    raise AddStyleException(
                        msg="The QML file is not valid !", description=""
                    )
            else:
                raise AddStyleException(
                    msg=f"Could not retrieve layer {layer_name}", description=""
                )
        else:
            raise AddStyleException(
                msg="An unexpected error has occurred", description=""
            )
    except AddStyleException:
        raise
    except Exception as e:
        raise AddStyleException(
            msg="An unexpected error has occurred", description=""
        ) from e

    return response


def add_style_qml_from_file_to_layer(
    layer_name: str, path_to_qgis_project: str, style_name: str, qml_path: str
) -> OperationResponse:
    """Add or update style from a qml file on a layer. The new style will have a new name

    Args:
        layer_name (str): name of the layer
        path_to_qgis_project (str): path to the QGIS project
        style_name (str): name of the new style
        qml_path (str): path to the QML

    Returns:
        OperationResponse
    Raise:
        AddStyleException
    """

    response = OperationResponse(error=False, msg="", description="", data=None)

    if os.path.exists(qml_path) and os.path.isfile(qml_path):
        q_file = QFile(qml_path)
        if q_file.open(QIODevice.ReadOnly):
            response = _add_style_to_layer(
                layer_name, path_to_qgis_project, style_name, q_file, qml_path
            )
    else:
        raise AddStyleException(msg="The QML file could not be found !", description="")

    return response


def add_style_qml_from_string_to_layer(
    layer_name: str,
    path_to_qgis_project: str,
    style_name: str,
    qml_string: str,
    qml_path: str,
) -> OperationResponse:
    """Add or update style from an string of QML on a layer. The new style will have a new name

    Args:
        layer_name (str): name of the layer
        path_to_qgis_project (str): path to the QGIS project
        style_name (str): name of the new style
        qml_string (str): path to the QML

    Returns:
        OperationResponse
    Raise :
        AddStyleException
    """

    response = _add_style_to_layer(
        layer_name, path_to_qgis_project, style_name, qml_string, qml_path
    )
    return response


def get_thumbnail_from_style_of_layer(
    layer_name: str, path_to_qgis_project: str, style_name: str, path: str
) -> OperationResponse:
    """
    Get the symbology(legend) of a layer at a specify style
    return the path to the png picture
    Return:
        OperationResponse
    Raise:
        ThumbnailFromStyleException
    """
    response = OperationResponse(error=False, msg="", description="", data=None)

    try:
        qgis_project = _get_project_instance(path_to_qgis_project)

        if qgis_project:
            if len(qgis_project.mapLayersByName(layer_name)) != 0:
                layer = qgis_project.mapLayersByName(layer_name)[0]
                style_manager = layer.styleManager()
                style_manager.setCurrentStyle(style_name)
                symbol_layer = layer.renderer()
                """ to merge png files https://stackoverflow.com/questions/30227466/combine-several-images-horizontally-with-python """
                if type(symbol_layer) != QgsCategorizedSymbolRenderer:
                    all_symbols = symbol_layer.symbols(QgsRenderContext())
                    # size = QSize(142, 142)
                    for sy in all_symbols[:1]:
                        image = sy.bigSymbolPreviewImage()
                        # f = tempfile.NamedTemporaryFile(dir=settings.TEMP_URL, suffix='.png')
                        # image =sy.asImage(size)
                        # image.save(r"C:\Users\Utilisateur\Desktop\STAGE KARL\dev web\design tarvel\img{}.png".format(i), "PNG")
                        image.save(path, "PNG")

                        response.data = File(open(path))

            else:
                raise ThumbnailFromStyleException(
                    msg=f"Could not retrieve layer {layer_name}"
                )
        else:
            raise ThumbnailFromStyleException(
                msg=f"Failed to load project {project_qgis_path}"
            )

        return response
    except ThumbnailFromStyleException:
        raise
    except Exception as e:
        raise ThumbnailFromStyleException(msg="An unexpected error has occurred") from e
