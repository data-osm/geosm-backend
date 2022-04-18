from dataclasses import dataclass
from typing import Any

@dataclass
class OperationResponse:
    """ represent the response returning when you add a vector layer in a QGIS Project"""
    error:bool
    msg:str
    """ message if there is error """
    description:str
    data:Any=None

@dataclass
class httpResponse:
    """ represent the response returning from an http"""
    error:bool
    msg:str=''
    """ message if there is error """
    data:Any=None

    def toJson(self):
        return self.__dict__

@dataclass
class AddVectorLayerResponse:
    """ represent the response returning when you add a vector layer in a QGIS Project"""
    error:bool
    msg:str
    """ message if there is error """
    description:str
    pathProject:str
    """ path to the qgis project """
    layerName:str
    """ layer name in the QGIS project """

@dataclass
class GetQMLStyleOfLayerResponse:
    """ represent the response returning when fetch qml content file of a layer"""
    error:bool
    msg:str
    """ message if there is error """
    description:str
    qmlPath:str
    qmlContent:str

@dataclass
class SimpleQuerryDefinition():
    connection:str
    sql:str
    provider_vector_id:int
    auto_update:bool
    created_at:str
    updated_at:str
@dataclass
class QuerryDefinition(SimpleQuerryDefinition):
    select:str
    where:str

