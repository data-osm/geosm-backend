from typing import List
from django.http.request import HttpRequest
from django.shortcuts import render
from geosmBackend.cuserViews import (
    ListCreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView,
    ListAPIView,
    DestroyAPIView,
    UpdateAPIView,
)
from rest_framework import permissions
from .serializers import (
    AdminBoundarySerializer,
    ParameterSerializer,
    AdminBoundaryCreateSerializer,
    ParameterCreateSerializer,
)
from .models import AdminBoundary, Parameter
from django.db import connection, Error
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from psycopg2.extras import NamedTupleCursor
from .documents import BoundarysDocument
from django.shortcuts import get_list_or_404, get_object_or_404
from group.models import Vector
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ParameterDetailView(RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Parameter.objects.all()
    serializer_class = ParameterCreateSerializer

    @swagger_auto_schema(
        operation_summary="Update parameter of the app",
        responses={200: ParameterCreateSerializer()},
        tags=["Parameter"],
    )
    def put(self, request, *args, **kwargs):
        """Update parameter of the app"""
        return super(ParameterDetailView, self).put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update parameter of the app",
        responses={200: ParameterCreateSerializer()},
        tags=["Parameter"],
    )
    def patch(self, request, *args, **kwargs):
        """Partially update parameter of the app"""
        return super(ParameterDetailView, self).partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="get parameter of the app",
        responses={200: ParameterCreateSerializer()},
        tags=["Parameter"],
    )
    def get(self, request, *args, **kwargs):
        """get parameter of the app"""
        return super(ParameterDetailView, self).get(request, *args, **kwargs)


class ParameterCreateView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Parameter.objects.all()
    serializer_class = ParameterCreateSerializer

    @swagger_auto_schema(
        operation_summary="Crete new parameter for app",
        responses={200: ParameterCreateSerializer()},
        tags=["Parameter"],
    )
    def post(self, request, *args, **kwargs):
        """Crete new parameter for app"""
        return super(ParameterCreateView, self).post(request, *args, **kwargs)


class ParameterListView(ListAPIView):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary="List parameter of the app",
        responses={200: ParameterSerializer()},
        tags=["Parameter"],
    )
    def get(self, request, *args, **kwargs):
        """List parameter of the app, there will be always have only one parameter"""
        return super(ParameterListView, self).get(request, *args, **kwargs)


class ExtentListView(APIView):
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary="List all the regions of the app",
        manual_parameters=[
            openapi.Parameter(
                "geometry",
                openapi.IN_QUERY,
                description="If you want to include st_asgeojson in the response",
                type=openapi.TYPE_BOOLEAN,
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                description="",
                items={
                    "type": openapi.TYPE_OBJECT,
                    "properties": {
                        "a": {"type": openapi.TYPE_INTEGER, "description": "xMin"},
                        "b": {"type": openapi.TYPE_INTEGER, "description": "YMin"},
                        "c": {"type": openapi.TYPE_INTEGER, "description": "xMax"},
                        "d": {"type": openapi.TYPE_INTEGER, "description": "yMax"},
                        "id": {
                            "type": openapi.TYPE_INTEGER,
                            "description": "id of extent in database",
                        },
                        "st_asgeojson": {
                            "type": openapi.TYPE_STRING,
                            "description": "geometry as geojson in text not JSON",
                        },
                        "name": {
                            "type": openapi.TYPE_STRING,
                            "description": "Name of the region",
                        },
                    },
                },
            )
        },
        tags=["Regions of the app"],
    )
    def get(self, request: HttpRequest, *args, **kwargs):
        try:
            with connection.cursor() as cursor:
                if self.request.query_params.get("geometry") == "true":
                    tolerance = self.request.query_params.get("tolerance", 0)
                    cursor.execute(
                        "select *, st_asgeojson(ST_SimplifyPreserveTopology(geom,"
                        + str(tolerance)
                        + ")) as  st_asgeojson , ST_XMin(st_transform(geom,3857)) as a, ST_YMin(st_transform(geom,3857)) as b, ST_XMax(st_transform(geom,3857)) as c, ST_YMax(st_transform(geom,3857)) as d from public.extent"
                    )
                else:
                    cursor.execute(
                        """
                        SELECT 'SELECT ' || STRING_AGG('o.' || column_name, ', ') || ' , ST_XMin(st_transform(o.geom,3857)) as a, ST_YMin(st_transform(o.geom,3857)) as b, ST_XMax(st_transform(o.geom,3857)) as c, ST_YMax(st_transform(o.geom,3857)) as d   FROM extent AS o'
                        FROM information_schema.columns
                        WHERE table_name = 'extent'
                        AND table_schema = 'public'
                        AND column_name NOT IN ('hstore_to_json', 'geom')
                    """
                    )
                    cursor.execute("".join(cursor.fetchall()[0]))

                temp = []
                for x in cursor.fetchall():
                    temp2 = {}
                    c = 0
                    for col in cursor.description:
                        temp2.update({str(col[0]): x[c]})
                        c = c + 1
                    temp.append(temp2)

                return Response(temp, status=status.HTTP_200_OK)
        except Exception as e:
            raise Exception(e)
            return Response([], status=status.HTTP_404_NOT_FOUND)


class GetExtentViewById(APIView):
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary="Retrieve a  region of the app",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Id of the region to retrieve",
                )
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                description="",
                items={
                    "type": openapi.TYPE_OBJECT,
                    "properties": {
                        "a": {"type": openapi.TYPE_INTEGER, "description": "xMin"},
                        "b": {"type": openapi.TYPE_INTEGER, "description": "YMin"},
                        "c": {"type": openapi.TYPE_INTEGER, "description": "xMax"},
                        "d": {"type": openapi.TYPE_INTEGER, "description": "yMax"},
                        "id": {
                            "type": openapi.TYPE_INTEGER,
                            "description": "id of extent in database",
                        },
                        "st_asgeojson": {
                            "type": openapi.TYPE_STRING,
                            "description": "geometry as geojson in text not JSON",
                        },
                        "name": {
                            "type": openapi.TYPE_STRING,
                            "description": "Name of the region",
                        },
                    },
                },
            )
        },
        tags=["Regions of the app"],
    )
    def post(self, request, *args, **kwargs):
        """Retrieve a  region of the app"""
        id = request.data["id"]
        with connection.cursor() as cursor:
            cursor.execute(
                "select *, min(ST_XMin(st_transform(geom,3857))) as a,min(ST_YMin(st_transform(geom,3857))) as b,max(ST_XMax(st_transform(geom,3857))) as c,max(ST_YMax(st_transform(geom,3857))) as d from public.extent where id="
                + str(id)
                + " group by id"
            )
            temp = []
            for x in cursor.fetchall():
                temp2 = {}
                c = 0
                for col in cursor.description:
                    temp2.update({str(col[0]): x[c]})
                    c = c + 1
                temp.append(temp2)
            if len(temp) > 0:
                return Response(temp[0], status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_404_NOT_FOUND)


class ExtenView(APIView):
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary="Get the principal region of the app",
        manual_parameters=[
            openapi.Parameter(
                "geometry",
                openapi.IN_QUERY,
                description="If you want to include st_asgeojson in the response",
                type=openapi.TYPE_BOOLEAN,
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                description="",
                items={
                    "type": openapi.TYPE_OBJECT,
                    "properties": {
                        "a": {"type": openapi.TYPE_INTEGER, "description": "xMin"},
                        "b": {"type": openapi.TYPE_INTEGER, "description": "YMin"},
                        "c": {"type": openapi.TYPE_INTEGER, "description": "xMax"},
                        "d": {"type": openapi.TYPE_INTEGER, "description": "yMax"},
                        "id": {
                            "type": openapi.TYPE_INTEGER,
                            "description": "id of extent in database",
                        },
                        "st_asgeojson": {
                            "type": openapi.TYPE_STRING,
                            "description": "geometry as geojson in text not JSON",
                        },
                        "name": {
                            "type": openapi.TYPE_STRING,
                            "description": "Name of the region",
                        },
                    },
                },
            )
        },
        tags=["Regions of the app"],
    )
    def get(self, request, *args, **kwargs):
        """Get the principal region of the app"""
        try:
            extent_pk = Parameter.objects.first().extent_pk

            with connection.cursor() as cursor:
                if self.request.query_params.get("geometry") == "true":
                    tolerance = self.request.query_params.get("tolerance", 0)
                    cursor.execute(
                        "select *, st_asgeojson(ST_SimplifyPreserveTopology(geom,"
                        + str(tolerance)
                        + ")) as  st_asgeojson, min(ST_XMin(st_transform(geom,3857))) as a,min(ST_YMin(st_transform(geom,3857))) as b,max(ST_XMax(st_transform(geom,3857))) as c,max(ST_YMax(st_transform(geom,3857))) as d from public.extent where id="
                        + str(extent_pk)
                        + " group by id"
                    )
                else:
                    cursor.execute(
                        "SELECT 'SELECT ' || STRING_AGG('o.' || column_name, ', ') || ' FROM extent AS o where o.id = "
                        + str(extent_pk)
                        + "'"
                        + """  FROM information_schema.columns
                            WHERE table_name = 'extent'
                            AND table_schema = 'public'
                            AND column_name NOT IN ('hstore_to_json', 'geom')
                        """
                    )
                    cursor.execute("".join(cursor.fetchall()[0]))

                temp = []
                for x in cursor.fetchall():
                    temp2 = {}
                    c = 0
                    for col in cursor.description:
                        temp2.update({str(col[0]): x[c]})
                        c = c + 1
                    temp.append(temp2)

                return Response(temp[0], status=status.HTTP_200_OK)
        except:
            return Response({}, status=status.HTTP_404_NOT_FOUND)


class SearchBoundary(APIView):
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary="Search administrative boundary",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                description="",
                items={
                    "type": openapi.TYPE_OBJECT,
                    "properties": {
                        "adminBoundary": {
                            "type": openapi.TYPE_OBJECT,
                            "description": "Administrative boundary",
                        },
                        "feature": {
                            "type": openapi.TYPE_OBJECT,
                            "properties": {
                                "table_id": {
                                    "type": openapi.TYPE_INTEGER,
                                    "description": "id of the administrative boundary in the provider table",
                                },
                                "name": {
                                    "type": openapi.TYPE_STRING,
                                    "description": "name of the administrative boundary",
                                },
                            },
                        },
                    },
                },
            )
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "search_word": openapi.Schema(
                    type=openapi.TYPE_STRING, description="The search key word"
                )
            },
        ),
        tags=["Administrative boundary"],
    )
    def post(self, request, *args, **kwargs):

        def getAdminBoundaryFeature(table: str, shema: str, id: int):
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT osm_id as table_id, name FROM "
                    + shema
                    + "."
                    + table
                    + " WHERE osm_id ="
                    + str(id)
                )
                temp = []
                for x in cursor.fetchall():
                    temp2 = {}
                    c = 0
                    for col in cursor.description:
                        temp2.update({str(col[0]): x[c]})
                        c = c + 1
                    temp.append(temp2)
                if len(temp) == 1:
                    return temp[0]

        searchQuerry = request.data["search_word"]
        search = BoundarysDocument.search()
        esResponse = search.from_dict(
            {
                "query": {
                    "bool": {
                        "should": [
                            {
                                "multi_match": {
                                    "boost": 4,
                                    "query": searchQuerry,
                                    "type": "best_fields",
                                    "fuzziness": 2,
                                    "fields": ["name", "name._2gram", "name._3gram"],
                                }
                            },
                            {
                                "multi_match": {
                                    "boost": 4,
                                    "query": searchQuerry,
                                    "type": "best_fields",
                                    "fuzziness": 2,
                                    "fields": ["ref", "ref._2gram", "ref._3gram"],
                                }
                            },
                        ]
                    }
                }
            }
        )

        pks = []

        for result in esResponse:
            if result.meta.index == "boundary":
                pks.append(result.meta.id)
        response = []
        for id in set(pks):
            adminBoundary_id = int(id.split("_")[1])
            table_id = int(id.split("_")[0])
            adminBoundary: AdminBoundary = AdminBoundary.objects.get(
                pk=adminBoundary_id
            )
            if adminBoundary:
                feature = getAdminBoundaryFeature(
                    adminBoundary.vector.table, adminBoundary.vector.shema, table_id
                )
                if feature:
                    response.append(
                        {
                            "feature": feature,
                            "adminBoundary": AdminBoundaryCreateSerializer(
                                adminBoundary
                            ).data,
                        }
                    )

        return Response(response, status=status.HTTP_200_OK)


class GetFeatureAdminBoundary(APIView):
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary="Get a feature from an administrative boundary with his geometry",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "table_id": {
                        "type": openapi.TYPE_INTEGER,
                        "description": "id of the administrative boundary in the provider table",
                    },
                    "name": {
                        "type": openapi.TYPE_STRING,
                        "description": "name of the administrative boundary",
                    },
                },
            )
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "vector_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Provider id where is store the administrative boundary ",
                ),
                "table_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="id of the administrative boundary in the provider table",
                ),
            },
        ),
        tags=["Administrative boundary"],
    )
    def post(self, request, *args, **kwargs):
        """Get a feature from an administrative boundary with his geometry"""

        def getAdminBoundaryFeatureWithGeometry(table: str, shema: str, id: int):
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT osm_id as table_id, name, st_asgeojson(st_transform(geom,3857)) as geometry FROM "
                    + shema
                    + "."
                    + table
                    + " WHERE osm_id ="
                    + str(id)
                )
                temp = []
                for x in cursor.fetchall():
                    temp2 = {}
                    c = 0
                    for col in cursor.description:
                        temp2.update({str(col[0]): x[c]})
                        c = c + 1
                    temp.append(temp2)
                if len(temp) == 1:
                    return temp[0]

        vector_id = int(request.data["vector_id"])
        table_id = int(request.data["table_id"])
        adminBoundary = get_object_or_404(Vector.objects.all(), pk=vector_id)
        feature = getAdminBoundaryFeatureWithGeometry(
            adminBoundary.table, adminBoundary.shema, table_id
        )
        if feature:
            return Response(feature, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)


class AdminBoundaryDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = AdminBoundary.objects.all()
    serializer_class = AdminBoundarySerializer

    @swagger_auto_schema(
        operation_summary="Delete an administrative boundary",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        },
        tags=["Administrative boundary"],
    )
    def delete(self, request, *args, **kwargs):
        """Delete an administrative boundary"""
        return super(AdminBoundaryDetailView, self).delete(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update an administrative boundary",
        responses={200: AdminBoundarySerializer()},
        tags=["Administrative boundary"],
    )
    def put(self, request, *args, **kwargs):
        """Update an administrative boundary"""
        return super(AdminBoundaryDetailView, self).put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="get an administrative boundary",
        responses={200: AdminBoundarySerializer()},
        tags=["Administrative boundary"],
    )
    def get(self, request, *args, **kwargs):
        """get an administrative boundary"""
        return super(AdminBoundaryDetailView, self).get(request, *args, **kwargs)


class AdminBoundaryCreateView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = AdminBoundary.objects.all()
    serializer_class = AdminBoundaryCreateSerializer

    @swagger_auto_schema(
        operation_summary="Add an administrative boundary",
        responses={200: AdminBoundarySerializer()},
        tags=["Administrative boundary"],
    )
    def post(self, request, *args, **kwargs):
        """Add an administrative boundary"""
        return super(AdminBoundaryCreateView, self).post(request, *args, **kwargs)
