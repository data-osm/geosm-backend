from .models import Icon, Map, Group, Sub, Layer, Default_map, Layer_provider_style, Metadata, Tags
from provider.models import Vector, Style
from provider.serializers import styleProviderSerializer, VectorProviderSerializer
from rest_framework import serializers
from typing import List

class IconSerializer(serializers.ModelSerializer):
    """
        Icon serializer
    """

    class Meta:
        model = Icon
        fields = "__all__"
        # fields = ['icon_id', 'name', 'tags', 'category']

class MapSerializer(serializers.ModelSerializer):
    """
        Map serializer
    """

    class Meta:
        model = Map
        fields = "__all__"

class DefaultMapSerializer(serializers.ModelSerializer):
    """
        Sub group serializer
    """

    class Meta:
        model = Default_map
        fields = "__all__"

class GroupSerializer(serializers.ModelSerializer):
    """
        Group serializer
    """
    map_id = serializers.PrimaryKeyRelatedField(queryset=Map.objects.all(), write_only=True, required=False)
    icon = IconSerializer(read_only=True)
    icon_id = serializers.IntegerField(write_only=True)
    group_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Group
        fields = ("name", "color", "icon", "type_group", "map_id", "group_id", "icon_path", "icon_id")

    def create(self, validate_data):
        
        if 'map_id' in validate_data:
            map = validate_data.pop('map_id')
            group = Group.objects.create(map=map, **validate_data)
            group.map_set.add(map)
        else:
            group = Group.objects.create(**validate_data)
        return group

class SubSerializer(serializers.ModelSerializer):
    """
        Sub group serializer
    """

    class Meta:
        model = Sub
        fields = "__all__"


class LayerProviderStyleSerializer(serializers.ModelSerializer):
    vp = VectorProviderSerializer(read_only=True, source='vp_id')
    vs = styleProviderSerializer(read_only=True, source='vs_id')

    class Meta:
        model = Layer_provider_style
        fields = "__all__"

class LayerSerializer(serializers.ModelSerializer):
    providers = LayerProviderStyleSerializer(read_only=True, source="layer")
    class Meta:
        model = Layer
        fields ="__all__"

class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields ="__all__"

class MetadataSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(many=True)
    class Meta:
        model = Metadata
        fields ="__all__"

    def create(self, validate_data):
        if 'tags' in validate_data:
            list_tags = validate_data.pop('tags')

            metadata = Metadata.objects.create(**validate_data)
            for api_tag in list_tags:
                tag = Tags.objects.filter(name=api_tag['name'])
                if tag.exists() == False:
                    metadata.tags.create(name=api_tag['name'])
                else:
                    metadata.tags.add(tag.first().pk)
        else:
            metadata = Metadata.objects.create(**validate_data)
        return metadata

    def update(self, instance, validate_data):
        metadata = instance
        if 'tags' in validate_data:
            list_tags = validate_data.pop('tags')

            for existing_tag in metadata.tags.all():
                metadata.tags.remove(existing_tag)

            for api_tag in list_tags:
                tag = Tags.objects.filter(name=api_tag['name'])
                if tag.exists() == False:
                    metadata.tags.create(name=api_tag['name'])
                else:
                    metadata.tags.add(tag.first().pk)

            return metadata
        else:
            return metadata
      