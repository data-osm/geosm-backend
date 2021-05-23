from typing import List
from django.shortcuts import render
from geosmBackend.cuserViews import ListCreateAPIView,RetrieveUpdateDestroyAPIView, RetrieveAPIView, CreateAPIView , ListAPIView, DestroyAPIView, UpdateAPIView
from rest_framework import permissions
from .serializers import AdminBoundarySerializer, ParameterSerializer, AdminBoundaryCreateSerializer, ParameterCreateSerializer
from .models import AdminBoundary, Parameter
from django.db import connection, Error
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from psycopg2.extras import NamedTupleCursor
from .documents import BoundarysDocument
from django.shortcuts import get_list_or_404, get_object_or_404
from group.models import Vector
# Create your views here.
class EnablePartialUpdateMixin:
    """Enable partial updates
    https://tech.serhatteker.com/post/2020-09/enable-partial-update-drf/

    Override partial kwargs in UpdateModelMixin class
    https://github.com/encode/django-rest-framework/blob/91916a4db14cd6a06aca13fb9a46fc667f6c0682/rest_framework/mixins.py#L64
    """
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

class AdminBoundaryRetrieveUpdateDestroyView(EnablePartialUpdateMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset=AdminBoundary.objects.all()
    serializer_class=AdminBoundarySerializer

class AdminBoundaryCreateView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset=AdminBoundary.objects.all()
    serializer_class=AdminBoundaryCreateSerializer

class ParameterRetrieveUpdateDestroyView(EnablePartialUpdateMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset=Parameter.objects.all()
    serializer_class=ParameterCreateSerializer

class ParameterCreateView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset=Parameter.objects.all()
    serializer_class=ParameterCreateSerializer

class ParameterListView(ListAPIView):
    queryset=Parameter.objects.all()
    serializer_class=ParameterSerializer
    authentication_classes = []


class ExtentListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            with connection.cursor() as cursor:
                if self.request.query_params.get('geometry') =='true':
                    cursor.execute("select *, st_asgeojson(geom) as  st_asgeojson from public.extent")
                else:
                    cursor.execute('''
                        SELECT 'SELECT ' || STRING_AGG('o.' || column_name, ', ') || ' FROM extent AS o'
                        FROM information_schema.columns
                        WHERE table_name = 'extent'
                        AND table_schema = 'public'
                        AND column_name NOT IN ('hstore_to_json', 'geom')
                    ''')
                    cursor.execute( ''.join(cursor.fetchall()[0]) )

                temp = []
                for x in cursor.fetchall():
                    temp2 = {}
                    c = 0
                    for col in cursor.description:
                        temp2.update({str(col[0]): x[c]})
                        c = c+1
                    temp.append(temp2)

                return Response(temp,status=status.HTTP_200_OK)
        except :
            return Response([],status=status.HTTP_404_NOT_FOUND)

class ExtenView(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        try:
            extent_pk = Parameter.objects.first().extent_pk
            
            with connection.cursor() as cursor:
                if self.request.query_params.get('geometry') =='true':
                    
                    cursor.execute("select *, st_asgeojson(geom) as  st_asgeojson, min(ST_XMin(st_transform(geom,3857))) as a,min(ST_YMin(st_transform(geom,3857))) as b,max(ST_XMax(st_transform(geom,3857))) as c,max(ST_YMax(st_transform(geom,3857))) as d from public.extent where id="+str(extent_pk)+" group by id")
                else:
                    cursor.execute(
                        "SELECT 'SELECT ' || STRING_AGG('o.' || column_name, ', ') || ' FROM extent AS o where o.id = "+ str(extent_pk)+"'" +
                        '''  FROM information_schema.columns
                            WHERE table_name = 'extent'
                            AND table_schema = 'public'
                            AND column_name NOT IN ('hstore_to_json', 'geom')
                        ''')
                    cursor.execute( ''.join(cursor.fetchall()[0]) )

                temp = []
                for x in cursor.fetchall():
                    temp2 = {}
                    c = 0
                    for col in cursor.description:
                        temp2.update({str(col[0]): x[c]})
                        c = c+1
                    temp.append(temp2)

                return Response(temp[0],status=status.HTTP_200_OK)
        except:
            return Response({},status=status.HTTP_404_NOT_FOUND)
        
class SearchBoundary(APIView):
    authentication_classes = []
    def post(self, request, *args, **kwargs):

        def getAdminBoundaryFeature(table:str, shema:str, id:int):
            with connection.cursor() as cursor:
                cursor.execute("SELECT osm_id as table_id, name FROM "+shema+"."+table+" WHERE osm_id ="+ str(id) )
                temp = []
                for x in cursor.fetchall():
                    temp2 = {}
                    c = 0
                    for col in cursor.description:
                        temp2.update({str(col[0]): x[c]})
                        c = c+1
                    temp.append(temp2)
                if len(temp) ==1 :
                    return temp[0]

        searchQuerry = request.data['search_word']
        search = BoundarysDocument.search()
        esResponse = search.from_dict(
            {
            "query": {
                "bool": {
                    "should": 
                        [
                            {
                                "match": {
                                    "name": searchQuerry
                                }
                            }
                        ]
                    }
                }
            }
        )
        pks = [result.meta.id for result in esResponse]
        response=[]
        for result in esResponse:
            adminBoundary_id = int(result.meta.id.split('_')[1]) 
            table_id = int(result.meta.id.split('_')[0]) 
            adminBoundary:AdminBoundary = AdminBoundary.objects.get(pk=adminBoundary_id)
            if adminBoundary:
                feature = getAdminBoundaryFeature(adminBoundary.vector.table, adminBoundary.vector.shema, table_id)
                if feature :
                    response.append({
                        "feature":feature,
                        'adminBoundary':AdminBoundaryCreateSerializer(adminBoundary).data
                    })
        
        return Response( response ,status=status.HTTP_200_OK)

class GetFeatureAdminBoundary(APIView):
    authentication_classes = []
    def post(self, request, *args, **kwargs):
        def getAdminBoundaryFeatureWithGeometry(table:str, shema:str, id:int):
            with connection.cursor() as cursor:
                cursor.execute("SELECT osm_id as table_id, name, st_asgeojson(st_transform(geom,3857)) as geometry FROM "+shema+"."+table+" WHERE osm_id ="+ str(id) )
                temp = []
                for x in cursor.fetchall():
                    temp2 = {}
                    c = 0
                    for col in cursor.description:
                        temp2.update({str(col[0]): x[c]})
                        c = c+1
                    temp.append(temp2)
                if len(temp) ==1 :
                    return temp[0]

        vector_id = int(request.data['vector_id'])
        table_id = int(request.data['table_id'])
        adminBoundary = get_object_or_404(Vector.objects.all(), pk=vector_id)
        feature = getAdminBoundaryFeatureWithGeometry(adminBoundary.table, adminBoundary.shema, table_id)
        if feature:
            return Response( feature ,status=status.HTTP_200_OK)
        else:
            Response({},status=status.HTTP_404_NOT_FOUND)
