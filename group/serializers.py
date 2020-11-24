from .models import Icon, Map, Group, Sub, Layer, Default_map, Type
from rest_framework import serializers


class IconSerializer(serializers.ModelSerializer):
    """
        Icon serializer
    """

    class Meta:
        model = Icon
        fields = "__all__"
        # fields = ['icon_id', 'name', 'tags', 'category']

class TypeSerializer(serializers.ModelSerializer):
    """
        Type serializer
    """

    class Meta:
        model = Type
        fields = "__all__"

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

    class Meta:
        model = Group
        fields = "__all__"

class SubSerializer(serializers.ModelSerializer):
    """
        Sub group serializer
    """

    class Meta:
        model = Sub
        fields = "__all__"

class LayerSerializer(serializers.ModelSerializer):
    """
        Sub group serializer
    """

    class Meta:
        model = Layer
        fields = "__all__"