import re, logging
import traceback

from utils.exeption import ExplicitException
from .models import Vector, Style
from typing import NamedTuple
from django.db.models import Count, Q
from django.db import connections, Error, ConnectionProxy
from .qgis.manageVectorLayer import add_vector_layer_from_postgis, remove_layer
from django.conf import settings
from os.path import join
from geosmBackend.type import (
    OperationResponse,
    AddVectorLayerResponse,
    SimpleQueryDefinition,
    TableCreatedResponse,
    TableMetadata,
)
from django.core.files import File

logger = logging.getLogger(__name__)

DATABASES = settings.DATABASES
OSMDATA = settings.OSMDATA


class TableCreationException(ExplicitException):
    pass


class DeleteSourceException(ExplicitException):
    pass


class TableAndSchema(NamedTuple):
    """represent the table and shema of a provider"""

    table: str
    shema: str


class ManageProviderFromSource:
    def __init__(self, provider_vector: Vector):
        self.provider_vector: Vector = provider_vector
        self.table_and_shema = self._get_table_and_schema()

    def update_provider(
        self, table_created_response: TableCreatedResponse
    ) -> TableCreatedResponse:
        """update an provider"""
        if table_created_response.data.extent:
            self.provider_vector.extent = table_created_response.data.extent
        self.provider_vector.count = table_created_response.data.count
        self.provider_vector.save()
        return table_created_response

    def remove_layer_from_qgis(self):
        """Remove provider from QGIS project"""
        qgis_project = self.provider_vector.path_qgis

        response = remove_layer(qgis_project, self.provider_vector.id_server)

        return response

    def create_provider_in_qgis(
        self, table_created_response: TableCreatedResponse, connection_name: str
    ) -> AddVectorLayerResponse:
        """add it to an QGIS project"""

        qgis_project = "projet" + "_" + str(int(Vector.objects.count() / 5)) + ".qgs"

        create_osm_data_source_response = add_vector_layer_from_postgis(
            DATABASES[connection_name]["HOST"],
            DATABASES[connection_name]["PORT"],
            DATABASES[connection_name]["NAME"],
            DATABASES[connection_name]["USER"],
            DATABASES[connection_name]["PASSWORD"],
            self.provider_vector.shema,
            self.provider_vector.table,
            table_created_response.geometry_field,
            table_created_response.primary_key,
            self.provider_vector.table,
            qgis_project,
        )

        if table_created_response.data.extent:
            self.provider_vector.extent = table_created_response.data.extent
        self.provider_vector.count = table_created_response.data.count

        self.provider_vector.primary_key_field = table_created_response.primary_key
        self.provider_vector.path_qgis = qgis_project
        self.provider_vector.url_server = (
            OSMDATA["url_qgis_server_prefix"] + qgis_project
        )
        self.provider_vector.id_server = create_osm_data_source_response.layer_name
        self.provider_vector.save()

        try:
            f = open(
                join(
                    OSMDATA["qml_default_path"],
                    "default-" + self.provider_vector.geometry_type + ".qml",
                )
            )
            myfile = File(f)
            default_style = Style(
                name="default",
                qml_file=myfile,
                provider_vector_id=self.provider_vector,
            )
            default_style.save()
        except Exception as err:
            logger.warning(
                f"could not save default style on provider {self.provider_vector.name}",
                err.args,
            )

        return create_osm_data_source_response

    def _get_table_and_schema(self) -> TableAndSchema:
        """
        Get table or shema of the table of this vector provider in database
        will check if table and shema already exist in the vector provider properties and return them
        If they not exist, will create them randomly
        """
        return get_table_and_schema(self.provider_vector)


class manageQueryProvider(ManageProviderFromSource):
    """create or delete before creating a table with an osm query"""

    def __init__(self, provider_vector: Vector, osm_query: SimpleQueryDefinition):
        super().__init__(provider_vector)
        self.osm_query: SimpleQueryDefinition = osm_query

    def update_query_provider(self) -> OperationResponse:
        """update an osm datasource"""

        return self.update_provider(self._create_or_replace_table())

    def delete_query_data_source(self) -> OperationResponse:
        """Delete and osm datasource by dropping his table

        Raise:
            DeleteSourceException
        """
        response = OperationResponse(error=False, msg="", description="", data=None)

        try:
            connection = connections[self.osm_query.connection]
            with connection.cursor() as cursor:
                cursor.execute(
                    "DROP TABLE IF EXISTS "
                    + self.table_and_shema.shema
                    + "."
                    + self.table_and_shema.table
                )
                response.error = False
                return response
        except Error as errorIdentifier:
            raise DeleteSourceException(
                msg=" Can not drop the table ", description=str(errorIdentifier)
            ) from errorIdentifier

    def create_query_data_source(self) -> AddVectorLayerResponse:
        """create an osm datasource, after add it to an QGIS project
        Raise:
        TableCreationException
        """
        return self.create_provider_in_qgis(
            self._create_or_replace_table(), self.osm_query.connection
        )

    def _create_or_replace_table(self) -> TableCreatedResponse:
        """
        Create a table in a shema or replace it with new osm query:
        -  If the schema does not exist, create it
        - drop the table if exist
        - create table as the osm query sql
        - update table, shema, extent, total area, total lenght and count of the vector provider
        Raise:
            TableCreationException
        """

        response = TableCreatedResponse(
            error=False,
            msg="",
            description="",
            data=TableMetadata(extent=None, count=None),
            geometry_field="geom",
            primary_key="osm_id",
        )
        connection = connections[self.osm_query.connection]

        create_schema_if_not_exist(self.table_and_shema.shema, connection)
        drop_table_if_exist(
            self.table_and_shema.shema, self.table_and_shema.table, connection
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CREATE TABLE  "
                    + self.table_and_shema.shema
                    + "."
                    + self.table_and_shema.table
                    + " AS "
                    + self.osm_query.sql
                )
                cursor.execute(
                    "CREATE INDEX "
                    + self.table_and_shema.table
                    + "_geometry_idx ON "
                    + self.table_and_shema.shema
                    + "."
                    + self.table_and_shema.table
                    + " USING GIST(geom) "
                )
                if self.provider_vector.geometry_type == "Point":
                    cursor.execute(
                        "ALTER TABLE "
                        + self.table_and_shema.shema
                        + "."
                        + self.table_and_shema.table
                        + " ALTER COLUMN geom TYPE geometry(Point,4326) USING ST_centroid(geom); "
                    )

            with connection.cursor() as cursor:
                cursor.execute(
                    "select min(ST_XMin(geom)) as l,min(ST_YMin(geom)) as b,max(ST_XMax(geom)) as r,max(ST_YMax(geom)) as t, count(*) as count from "
                    + self.table_and_shema.shema
                    + "."
                    + self.table_and_shema.table
                )
                responseExtent = cursor.fetchall()[0]
                response.data.extent = [
                    responseExtent[0],
                    responseExtent[1],
                    responseExtent[2],
                    responseExtent[3],
                ]

                response.data.count = int(responseExtent[4])

        except Error as errorIdentifier:
            raise TableCreationException(
                msg=" Can not create the table " + self.table_and_shema.table,
                description=str(errorIdentifier),
            ) from errorIdentifier

        self.provider_vector.table = self.table_and_shema.table
        self.provider_vector.shema = self.table_and_shema.shema
        self.provider_vector.save()

        return response


def get_table_and_schema(provider_vector: Vector, shema="osm_tables") -> TableAndSchema:
    """
    Get table or shema of the table of this vector provider in databse
    will check if table and shema already exist in the vector provider properties and return them
    If they not exist, will create them randomnly
    """
    table = None
    if provider_vector.shema:
        shema = provider_vector.shema

    if provider_vector.table:
        table = provider_vector.table
    else:
        table = re.sub("[^A-Za-z0-9]+", "", provider_vector.name).lower()
        i = 0

        while (
            Vector.objects.annotate(num_table=Count("table", filter=Q(table=table)))[
                0
            ].num_table
            != 0
        ):
            table = (
                re.sub("[^A-Za-z0-9]+", "", provider_vector.name).lower() + "_" + str(i)
            )
            i += 1

    table_and_schema: TableAndSchema = TableAndSchema(table, shema)
    return table_and_schema


def create_schema_if_not_exist(shema: str, connection: ConnectionProxy):
    """
    Create a schema in database if not exist

    Args:
        shema (str): name of the schema
        connection (_type_): connextion to the database
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name = '"
            + shema
            + "'"
        )
        if cursor.rowcount == 0:
            cursor.execute("CREATE SCHEMA " + shema)


def drop_table_if_exist(schema: str, table: str, connection: ConnectionProxy):
    """Drop table if exists

    Args:
        schema (str): _description_
        table (str): _description_
        connection (ConnectionProxy): _description_
    """
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS " + schema + "." + table)
