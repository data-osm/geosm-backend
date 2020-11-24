from .models import Vector, Style
from rest_framework import serializers


class VectorProviderSerializer(serializers.ModelSerializer):
    """
        Vector provider serializer
    """

    class Meta:
        model = Vector
        fields = "__all__"
        # fields = ['icon_id', 'name', 'tags', 'category']

class styleProviderSerializer(serializers.ModelSerializer):
    """
        Style provider serializer
    """

    class Meta:
        model = Style
        # fields = "__all__"
        fields = ['provider_style_id', 'name', 'custom_style_id', 'provider_vector_id', 'pictogram', 'qml_file']