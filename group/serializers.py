from utils.serializers import MediaUrlField
from .models import (
    Map,
    Group,
    Sub,
    Layer,
    Default_map,
    Layer_provider_style,
    Metadata,
    Tags,
    Base_map,
)
from .subModels.icon import Icon, TagsIcon
from provider.models import Vector, Style
from provider.serializers import styleProviderSerializer, VectorProviderSerializer
from rest_framework import serializers
from typing import List
import ast
from genericIcon.serializers import PictoSerializer
from .subSerializer.icon import IconSerializer, TagsIconSerializer


class BaseMapSerializer(serializers.ModelSerializer):
    pictogramme = PictoSerializer(read_only=True, source="picto")

    class Meta:
        model = Base_map
        fields = [
            "id",
            "name",
            "url",
            "protocol_carto",
            "identifiant",
            "attribution",
            "picto",
            "principal",
            "created_at",
            "updated_at",
            "pictogramme",
        ]


class MapSerializer(serializers.ModelSerializer):
    """
    Map serializer
    """

    class Meta:
        model = Map
        fields = [
            "map_id",
            "name",
            "group_id",
            "created_at",
            "updated_at",
            "description",
        ]


class DefaultMapSerializer(serializers.ModelSerializer):
    """
    Sub group serializer
    """

    class Meta:
        model = Default_map
        fields = ["map_id"]


class GroupSerializer(serializers.ModelSerializer):
    """
    Group serializer
    """

    map_id = serializers.PrimaryKeyRelatedField(
        queryset=Map.objects.all(), write_only=True, required=False
    )
    icon = IconSerializer(read_only=True)
    icon_id = serializers.IntegerField(write_only=True)
    group_id = serializers.IntegerField(read_only=True)
    icon_path = MediaUrlField()

    class Meta:
        model = Group
        fields = (
            "name",
            "color",
            "icon",
            "type_group",
            "map_id",
            "group_id",
            "principal",
            "icon_path",
            "icon_id",
            "order",
        )

    def create(self, validate_data):

        if "map_id" in validate_data:
            map = validate_data.pop("map_id")
            group = Group.objects.create(map=map, **validate_data)
            group.map_set.add(map)
        else:
            group = Group.objects.create(**validate_data)
        return group


class LayerProviderStyleSerializer(serializers.ModelSerializer):
    vp = VectorProviderSerializer(read_only=True, source="vp_id")
    vs = styleProviderSerializer(read_only=True, source="vs_id")

    class Meta:
        model = Layer_provider_style
        fields = [
            "id",
            "layer_id",
            "vp_id",
            "vs_id",
            "ordre",
            "created_at",
            "updated_at",
            "vp",
            "vs",
        ]


class LayerSerializer(serializers.ModelSerializer):
    providers = serializers.SerializerMethodField(read_only=True)
    cercle_icon = MediaUrlField()
    square_icon = MediaUrlField()

    class Meta:
        model = Layer
        fields = [
            "layer_id",
            "name",
            "protocol_carto",
            "color",
            "icon_color",
            "icon",
            "icon_background",
            "cercle_icon",
            "square_icon",
            "description",
            "opacity",
            "metadata_cap",
            "share",
            "sub",
            "principal",
            "created_at",
            "updated_at",
            "providers",
        ]

    def get_providers(self, instance: Layer):
        return LayerProviderStyleSerializer(
            Layer_provider_style.objects.filter(layer_id=instance.pk), many=True
        ).data


class SubWithLayersSerializer(serializers.ModelSerializer):
    """
    Sub group serializer
    """

    layers = serializers.SerializerMethodField()

    class Meta:
        model = Sub
        fields = ["group_sub_id", "name", "group", "created_at", "updated_at", "layers"]

    def get_layers(self, instance: Sub):
        return LayerSerializer(Layer.objects.filter(sub=instance.pk), many=True).data


class SubSerializer(serializers.ModelSerializer):
    """
    Sub group with thier layers serializer
    """

    class Meta:
        model = Sub
        fields = [
            "group_sub_id",
            "name",
            "group",
            "created_at",
            "updated_at",
        ]


class SubWithGroupSerializer(serializers.ModelSerializer):
    """
    Sub group with thier group serializer
    """

    group = GroupSerializer()

    class Meta:
        model = Sub
        fields = ["group_sub_id", "name", "group", "created_at", "updated_at", "group"]


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ["name", "id"]


class MetadataSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(many=True)

    class Meta:
        model = Metadata
        fields = [
            "layer",
            "description",
            "tags",
            "created_at",
            "updated_at",
        ]

    def create(self, validate_data):
        if "tags" in validate_data:
            list_tags = validate_data.pop("tags")

            metadata = Metadata.objects.create(**validate_data)
            for api_tag in list_tags:
                tag = Tags.objects.filter(name=api_tag["name"])
                if tag.exists() is False:
                    metadata.tags.create(name=api_tag["name"])
                else:
                    metadata.tags.add(tag.first().pk)
        else:
            metadata = Metadata.objects.create(**validate_data)
        return metadata

    def update(self, instance: Metadata, validate_data):
        metadata = instance
        metadata.description = validate_data.get("description", metadata.description)

        if "tags" in validate_data:
            list_tags = validate_data.pop("tags")

            for existing_tag in metadata.tags.all():
                metadata.tags.remove(existing_tag)

            for api_tag in list_tags:
                tag = Tags.objects.filter(name=api_tag["name"])
                if tag.exists() is False:
                    metadata.tags.create(name=api_tag["name"])
                else:
                    metadata.tags.add(tag.first().pk)
            metadata.save()
            return metadata
        else:
            metadata.save()
            return metadata


class SetPrincipalLayerDeserializer(serializers.Serializer):
    principal = serializers.BooleanField()


class ListCreateLayerQueryParamsDeserializer(serializers.Serializer):
    principal = serializers.BooleanField(required=False, allow_null=True)
    sub__group = serializers.IntegerField(required=False)
    sub = serializers.IntegerField(required=False)
