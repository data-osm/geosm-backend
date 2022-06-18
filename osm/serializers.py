from .models import Querry, SimpleQuerry, sigFile
from rest_framework import serializers


class osmQuerrySerializer(serializers.ModelSerializer):
    """
        Osm querry serializer
    """
    class Meta:
        model = Querry
        fields = "__all__"

    def create(self, validated_data):
        return Querry.objects.create(**validated_data)

class SimpleQuerrySerializer(serializers.ModelSerializer):
    """
        Simple querry serializer
    """
    class Meta:
        model = SimpleQuerry
        fields = "__all__"

class SigFileSerializer(serializers.ModelSerializer):
    """
        sig file serializer
    """
    class Meta:
        model = sigFile
        fields = "__all__"

