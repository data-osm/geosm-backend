from .models import Icon
from rest_framework import serializers


class IconSerializer(serializers.ModelSerializer):
    """
        Icon serializer
    """

    class Meta:
        model = Icon
        fields = "__all__"
        # fields = ['icon_id', 'name', 'tags', 'category']


