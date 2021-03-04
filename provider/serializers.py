from .models import Vector, Style
from rest_framework import serializers



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

    class Meta:
        model = Style
        # fields = "__all__"
        fields = ['provider_style_id', 'name', 'custom_style_id', 'provider_vector_id', 'pictogram', 'qml_file']

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