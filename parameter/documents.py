# from django_elasticsearch_dsl import Document, fields
from typing import List
from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, Index
from elasticsearch_dsl.connections import connections
from elasticsearch.helpers import reindex
from elasticsearch import Elasticsearch

# from django_elasticsearch_dsl.registries import registry
from django.conf import settings
from provider.models import Vector
from django.db import connection, Error
import asyncio 
from asgiref.sync import sync_to_async

connections.create_connection(hosts=settings.ELASTICSEARCH_DSL['default']['hosts'])
es = Elasticsearch([settings.ELASTICSEARCH_DSL['default']['hosts']])

class BoundarysTempDocument(Document):

    name = Text(analyzer='snowball')
    admin_boundary_id = Integer()

    class Index:
        # Name of the Elasticsearch index
        name = 'boundary_temp'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

class BoundarysDocument(Document):

    name = Text(analyzer='snowball')
    admin_boundary_id = Integer()

    class Index:
        # Name of the Elasticsearch index
        name = 'boundary'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

def refreshBoundaryDocument(boundarys):
    try:
        BoundarysTempDocument.delete()
    except:
        pass
    BoundarysTempDocument.init()

    try:
       
        for boundary in boundarys:
            # boundary.vector
            vector:Vector =  boundary.vector
            with connection.cursor() as cursor:
                cursor.execute("select osm_id, name from "+vector.shema+"."+vector.table )
                for item in cursor.fetchall():
                    elasticDoc = BoundarysTempDocument(meta={'id': str(item[0])+'_'+str(boundary.admin_boundary_id)}, name=item[1], admin_boundary_id=boundary.admin_boundary_id)
                    elasticDoc.save()

        try:
            Index('boundary').delete()
        except Exception as e:
            pass

        import time
        start = time.time()
        BoundarysDocument.init()
        reindex(
            es,
            'boundary_temp',
            'boundary'
        )
        end = time.time()
        print('================refreshBoundaryDocument FINISH', end - start)
    except Exception as e:
        print('exeption ======', str(e))
        raise Exception(e)
    