from dataclasses import dataclass
from typing import Any

@dataclass
class OperationResponse:
    """ represent the response returning when you add a vector layer in a QGIS Project"""
    error:bool
    msg:str
    """ message if there is error """
    description:str

@dataclass
class httpResponse:
    """ represent the response returning from an http"""
    error:bool
    msg:str=''
    """ message if there is error """
    data:Any=None