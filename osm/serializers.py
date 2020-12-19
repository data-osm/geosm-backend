from .models import Querry
from rest_framework import serializers


class osmQuerrySerializer(serializers.ModelSerializer):
    """
        Osm querry serializer
    """

    class Meta:
        model = Querry
        fields = "__all__"
        # fields = ['icon_id', 'name', 'tags', 'category']

    def create(self, validated_data):
        return Querry.objects.create(**validated_data)
