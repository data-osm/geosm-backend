from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Layer, Metadata, Group, Sub, Tags

@registry.register_document
class LayerDocument(Document):

    sub = fields.ObjectField(properties={
        'name': fields.TextField(),
        'group': fields.TextField(),
    })

    metadata = fields.NestedField(properties={
        'description': fields.TextField(),
        'tags':fields.ListField(fields.TextField())
    })


    def prepare_sub(self, instance:Layer):
        ''' Only triger when we rebuild the entire index '''
        return {
            'name':instance.sub.name,
            'group':instance.sub.group.name
        }

    def prepare_metadata(self, instance:Layer):
        ''' Only triger when we rebuild the entire index '''
        # print(instance.description, 'instance')
        metadata = Metadata.objects.filter(layer=instance)
        if metadata.count()>0:
            return {
                'description':metadata.first().description,
                'tags':[tag.name for tag in metadata.first().tags.all()]
            }
        else:
            return {
                'description':None,
                'tags':[]
            }

    class Index:
        # Name of the Elasticsearch index
        name = 'layer'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Layer

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'name',
        ]
        related_models = [Metadata, Group, Sub, Tags]

    def get_instances_from_related(self, related_instance):
        """Trigger when related models are updated :
         If related_models is set, define how to retrieve the Sub instance(s) from the related model.
        The related_models option should be used with caution because it can lead in the index
        to the updating of a lot of items.
        """
        if isinstance(related_instance, Sub):
            print((related_instance, 'isinstance'))
            return related_instance.sub_set.all()
        elif isinstance(related_instance, Metadata):
            print((related_instance, 'related_instance'))
            return related_instance.layer