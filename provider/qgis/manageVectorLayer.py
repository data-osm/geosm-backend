from os.path import join
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsDataSourceUri,
)
import traceback
from geosmBackend.type import OperationResponse, AddVectorLayerResponse
from django.conf import settings

from utils.exeption import ExplicitException, SimpleException


class addVectorLayerFromPostgisException(ExplicitException):
    pass


class RemoveVectorLayerFromQgisException(SimpleException):
    pass


class SaveQMLtoGeoPackageException(ExplicitException):
    pass


OSMDATA = settings.OSMDATA
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


def _make_vector_layer_available_on_wfs(
    project: QgsProject, vector_layer: QgsVectorLayer
) -> bool:
    """
    Make a QgsVectorLayer avaible on WFS by adding it to WFSLayers entry

    :param project: the QGIS project instance
    :rparam project: QgsProject

    :param vector_layer: the layer to make avaible on WFS
    :rparam vector_layer: QgsVectorLayer

    :return:
    :rtype: bool

    """

    if type(vector_layer) == QgsVectorLayer and vector_layer.isValid():
        wfs_layers = project.readListEntry("WFSLayers", "")
        wfs_layers_list = list(wfs_layers)[0]
        wfs_layers_list.append("%s" % vector_layer.id())
        project.writeEntry("WFSLayers", "", wfs_layers_list)
        project.writeEntry("WMSAddWktGeometry", "", "true")

        return True
    else:
        return False


def add_vector_layer_from_postgis(
    host: str,
    port: str,
    database: str,
    user: str,
    password: str,
    schema: str,
    table: str,
    geometry_column: str,
    primary_key_column: str,
    layer_name: str,
    path_to_qgis_project: str,
) -> AddVectorLayerResponse:
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

    :param geometry_column: geometry_column of the table
    :rparam geometry_column: str

    :param primary_key_column: primary key of the table
    :rparam primary_key_column: str

    :param layer_name: Name of the layer in the QGIS project
    :rparam layer_name: str

    :param path_to_qgis_project: the absolute path of the project
    :rparam path_to_qgis_project: str

    :rreturn AddVectorLayerResponse

    Raise:
        addVectorLayerFromPostgisException

    """
    response = AddVectorLayerResponse(
        error=False,
        msg="",
        description="",
        path_project="",
        layer_name="",
    )

    QGISProject = _get_project_instance(path_to_qgis_project)

    if QGISProject:
        uri = QgsDataSourceUri()
        # table="bar"
        uri.setConnection(host, port, database, user, password)
        # conn = QgsProviderRegistry.instance().providerMetadata('postgres').createConnection(uri.uri(False),{})
        # print(conn.tables(schema))

        uri.setDataSource(schema, table, geometry_column, "", primary_key_column)
        if len(QGISProject.mapLayersByName(layer_name)) > 0:
            layer_name = (
                layer_name + "_" + str(len(QGISProject.mapLayersByName(layer_name)) + 1)
            )

        vector_layer = QgsVectorLayer(uri.uri(False), layer_name, "postgres")

        if vector_layer.isValid():
            if QGISProject.addMapLayer(vector_layer) is not None:
                if _make_vector_layer_available_on_wfs(QGISProject, vector_layer):
                    response.error = QGISProject.write() is not True
                    response.pathProject = path_to_qgis_project
                    response.layer_name = layer_name
                else:
                    raise addVectorLayerFromPostgisException(
                        msg=f"Impossible to make layer {layer_name} in project {path_to_qgis_project} available on WFS",
                        description="",
                    )
            else:
                raise addVectorLayerFromPostgisException(
                    msg=f"Impossible to add layer {layer_name} to project {path_to_qgis_project} ",
                    description="",
                )
        else:
            raise addVectorLayerFromPostgisException(
                msg=f"The layer {layer_name} is not valid in project {path_to_qgis_project}",
                description="",
            )
    else:
        raise addVectorLayerFromPostgisException(
            msg=f"Impossible to load  project {path_to_qgis_project} ", description=""
        )

    return response


def remove_layer(path_to_qgis_project: str, layer_name: str) -> OperationResponse:
    """Remove all layers with have a specific layer name in a QGIS project
    Todo:
        remove layer in wfsList

    Args:
        path_to_qgis_project (str): path to the QGIS project
        layer_name (str): name of the layer to remove

    Returns:
        OperationResponse
    Raise :
        RemoveVectorLayerFromQgisException

    """
    response = OperationResponse(error=False, msg="", description="", data=None)

    qgis_project = _get_project_instance(path_to_qgis_project)
    if qgis_project:
        while len(qgis_project.mapLayersByName(layer_name)) != 0:
            qgis_project.removeMapLayer(qgis_project.mapLayersByName(layer_name)[0])

        response.error = qgis_project.write() is not True
        return response

    else:
        raise RemoveVectorLayerFromQgisException(
            msg=f"Failed to load the project {path_to_qgis_project}"
        )


def save_qml_to_geo_package(gpkg_file: str, qml_file: str):
    """Save QML to geopackage as default style

    Args:
        gpkg_file (str): gpkg file path
        qml_file (str): qml file path

    Raises:
        SaveQMLtoGeoPackageException
    """
    layer = QgsVectorLayer(gpkg_file, "layer", "ogr")
    mess, res = layer.loadNamedStyle(qml_file)
    if res is not True:
        raise SaveQMLtoGeoPackageException(msg=mess, description="")
    try:
        layer.deleteStyleFromDatabase("1")
    except Exception:
        pass
    res = layer.saveStyleToDatabase("default", "", True, "")
