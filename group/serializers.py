from .models import Icon, Map, Group, Sub, Layer, Default_map
from rest_framework import serializers


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

class LayerSerializer(serializers.ModelSerializer):
    """
        Sub group serializer
    """

    class Meta:
        model = Layer
        fields = "__all__"