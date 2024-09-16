from typing import Union
from django.contrib.gis.db import models
from django.core.exceptions import NON_FIELD_ERRORS
from django.forms import ValidationError
from group.models import Vector
from osm.validateOsmQuerry import validateOsmQuerry
from django.core.exceptions import ObjectDoesNotExist
from tracking_fields.decorators import track
from provider.manageOsmDataSource import manageQueryProvider
from provider.qgis.manageVectorLayer import (
    RemoveVectorLayerFromQgisException,
    remove_layer,
)
from django.db import Error, connections
from django.db.utils import DEFAULT_DB_ALIAS

from utils.exeption import ExplicitException


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


@track("select", "where")
class Querry(models.Model):
    """name of the connexion"""

    connection = models.TextField(blank=False, null=False, default=DEFAULT_DB_ALIAS)
    """ model of osm query """
    # osm_query_id = models.OneToOneField(primary_key=True)
    select = models.TextField(blank=True, null=True)
    """ the select clause of the query """
    where = models.TextField(null=False)
    """ the where clause of the query """
    sql = models.TextField(blank=True)
    """ the full query """
    provider_vector_id = models.OneToOneField(
        Vector, on_delete=models.CASCADE, primary_key=True
    )
    auto_update = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        validation = _is_osm_query_validate(self)
        newOne = self.created_at is None
        if validation["error"] is False:
            self.sql = validation["sql"]
            super(Querry, self).save(*args, **kwargs)
            try:

                if newOne:
                    manageQueryProvider(
                        self.provider_vector_id, self
                    ).create_query_data_source()
                else:
                    manageQueryProvider(
                        self.provider_vector_id, self
                    ).update_query_provider()
            except ExplicitException as error:
                self.delete()
                raise ValidationError(
                    {NON_FIELD_ERRORS: f"{error.msg} : {error.description}"}
                )
            except Exception:
                self.delete()
                raise
            else:
                self.provider_vector_id.type = "osm"
                self.provider_vector_id.save()
        else:
            self.delete()
            raise ValidationError(
                {
                    NON_FIELD_ERRORS: f"{validation.get('msg')} : {validation.get('description')}"
                }
            )

    def delete(self, *args, **kwargs):
        if self.provider_vector_id.path_qgis and self.provider_vector_id.id_server:
            try:
                remove_layer(
                    self.provider_vector_id.path_qgis,
                    self.provider_vector_id.id_server,
                )
            except RemoveVectorLayerFromQgisException:
                pass

        super(Querry, self).delete(*args, **kwargs)


def _is_osm_query_validate(osmQuerry: Querry) -> dict:
    try:

        vector_provider = osmQuerry.provider_vector_id
        osmValidation = validateOsmQuerry(
            osmQuerry.where, osmQuerry.select, vector_provider.geometry_type
        )
        if osmValidation.isValid():
            return {"error": False, "sql": osmValidation.query}
        else:

            return {
                "error": True,
                "msg": " The osm querry is not correct ",
                "description": osmValidation.error,
            }

    except ObjectDoesNotExist as identifier:
        return {
            "error": True,
            "msg": " Can not find the vector provider of this osm querry",
            "description": identifier,
        }


@track("sql")
class SimpleQuerry(models.Model):
    """name of the connexion"""

    connection = models.TextField(blank=False, null=False, default=DEFAULT_DB_ALIAS)
    """ model of a simple query """
    sql = models.TextField(blank=False, null=False)
    """ the full query """
    provider_vector_id = models.OneToOneField(
        Vector, on_delete=models.CASCADE, primary_key=True
    )
    auto_update = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        validation = _is_simple_querry_validate(self)
        if validation is True:
            try:
                if self.created_at is not None:
                    manageQueryProvider(
                        self.provider_vector_id, self
                    ).update_query_provider()
                else:
                    manageQueryProvider(
                        self.provider_vector_id, self
                    ).create_query_data_source()
            except ExplicitException as error:
                self.delete()
                raise ValidationError(
                    {NON_FIELD_ERRORS: f"{error.msg} : {error.description}"}
                )
            except Exception:
                self.delete()
                raise
            else:
                self.provider_vector_id.type = "querry"
                self.provider_vector_id.save()
                super(SimpleQuerry, self).save(*args, **kwargs)
        else:
            raise ValidationError(
                {
                    NON_FIELD_ERRORS: f"{validation.get('msg')} : {validation.get('description')}"
                }
            )

    def delete(self, *args, **kwargs):
        if self.provider_vector_id.path_qgis and self.provider_vector_id.id_server:
            try:
                remove_layer(
                    self.provider_vector_id.path_qgis,
                    self.provider_vector_id.id_server,
                )
            except RemoveVectorLayerFromQgisException:
                manageQueryProvider(
                    self.provider_vector_id, self
                ).delete_query_data_source()

        super(SimpleQuerry, self).delete(*args, **kwargs)


def _is_simple_querry_validate(simple_querry: SimpleQuerry) -> Union[bool, str]:

    try:
        connection = connections[simple_querry.connection]
        sql = (
            "select * from (" + simple_querry.sql.replace(";", "") + " ) as dd limit 1"
        )
        with connection.cursor() as cursor:
            cursor.execute(sql)
            cursor.fetchall()
            return True
    except Error as errorIdentifier:
        error = str(errorIdentifier)
        return error
