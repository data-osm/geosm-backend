from dataclasses import dataclass
from typing import Any


@dataclass
class OperationResponse:
    """represent the response returning when you add a vector layer in a QGIS Project"""

    error: bool
    msg: str
    """ message if there is error """
    description: str
    data: Any


@dataclass
class httpResponse:
    """represent the response returning from an http"""

    error: bool
    msg: str = ""
    """ message if there is error """
    data: Any = None

    def toJson(self):
        return self.__dict__


@dataclass
class AddVectorLayerResponse:
    """represent the response returning when you add a vector layer in a QGIS Project"""

    error: bool
    msg: str
    """ message if there is error """
    description: str
    path_project: str
    """ path to the qgis project """
    layer_name: str
    """ layer name in the QGIS project """


@dataclass
class GetQMLStyleOfLayerResponse:
    """represent the response returning when fetch qml content file of a layer"""

    error: bool
    msg: str
    """ message if there is error """
    description: str
    qml_path: str
    qml_content: str


@dataclass
class SimpleQueryDefinition:
    connection: str
    sql: str
    provider_vector_id: int
    auto_update: bool
    created_at: str
    updated_at: str


@dataclass
class QueryDefinition(SimpleQueryDefinition):
    select: str
    where: str


@dataclass
class TableMetadata:
    extent: Any
    count: int


@dataclass
class TableCreatedResponse(OperationResponse):
    geometry_field: str
    primary_key: str
    data: TableMetadata
