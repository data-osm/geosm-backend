from utils.serializers import MediaUrlField
from .models import Vector, Style, Custom_style
from rest_framework import serializers


class CustomStyleSerializer(serializers.ModelSerializer):
    icon = MediaUrlField()

    class Meta:
        model = Custom_style
        fields = (
            "custom_style_id",
            "name",
            "description",
            "icon",
            "function_name",
            "geometry_type",
        )


class VectorProviderSerializer(serializers.ModelSerializer):
    """
    Vector provider serializer
    """

    class Meta:
        model = Vector
        fields = (
            "provider_vector_id",
            "name",
            "type",
            "table",
            "shema",
            "geometry_type",
            "url_server",
            "id_server",
            "path_qgis",
            "extent",
            "z_min",
            "z_max",
            "count",
            "total_lenght",
            "total_area",
            "epsg",
            "state",
            "primary_key_field",
            "created_at",
            "updated_at",
        )


class styleProviderSerializer(serializers.ModelSerializer):
    """
    Style provider serializer
    """

    custom_style = CustomStyleSerializer(read_only=True, source="custom_style_id")

    class Meta:
        model = Style
        fields = [
            "provider_style_id",
            "name",
            "custom_style_id",
            "provider_vector_id",
            "pictogram",
            "qml_file",
            "custom_style",
            "description",
            "parameters",
        ]


class styleSimpleProviderSerializer(serializers.ModelSerializer):
    """
    Style simple  provider serializer
    """

    class Meta:
        model = Style
        fields = ["name", "provider_style_id"]


class VectorProviderWithStyleSerializer(VectorProviderSerializer):
    """
    Vector provider serializer
    """

    style = styleSimpleProviderSerializer(
        read_only=True, source="provider_vector_id_set"
    )

    class Meta(VectorProviderSerializer.Meta):
        fields = VectorProviderSerializer.Meta.fields + ("style",)
