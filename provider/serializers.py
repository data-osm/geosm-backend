from .models import Vector
from rest_framework import serializers


class VectorProviderSerializer(serializers.ModelSerializer):
    """
        Vector provider serializer
    """

    class Meta:
        model = Vector
        fields = "__all__"
        # fields = ['icon_id', 'name', 'tags', 'category']
