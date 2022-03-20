from group.subSerializer.icon import IconSerializer
from .models import Vector, Style, Custom_style
from rest_framework import serializers


class CustomStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Custom_style
        fields = "__all__"

    def to_representation(self, instance):
        representation = super(CustomStyleSerializer, self).to_representation(instance)
        full_path =  instance.icon.url
        representation['icon'] = full_path
        return representation
class VectorProviderSerializer(serializers.ModelSerializer):
    """
        Vector provider serializer
    """

    class Meta:
        model = Vector
        fields = "__all__"

class styleProviderSerializer(serializers.ModelSerializer):
    """
        Style provider serializer
    """
    custom_style = CustomStyleSerializer(read_only=True, source="custom_style_id")
    class Meta:
        model = Style
        # fields = "__all__"
        fields = ['provider_style_id', 'name', 'custom_style_id', 'provider_vector_id', 'pictogram', 'qml_file', 'custom_style', 'description','parameters']

class styleSimpleProviderSerializer(serializers.ModelSerializer):
    """
        Style simple  provider serializer
    """

    class Meta:
        model = Style
        # fields = "__all__"
        fields = ['name','provider_style_id']

class VectorProviderWithStyleSerializer(serializers.ModelSerializer):
    """
        Vector provider serializer
    """
    style = styleSimpleProviderSerializer(read_only=True, source="provider_vector_id_set")

    class Meta:
        model = Vector
        fields = "__all__"

