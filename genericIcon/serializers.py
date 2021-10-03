from rest_framework import serializers
from .models import Picto

class PictoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picto
        fields ="__all__"

    def to_representation(self, instance):
        representation = super(PictoSerializer, self).to_representation(instance)
        if instance.cercle_icon:
            representation['cercle_icon'] = instance.cercle_icon.url
        if instance.square_icon:
            representation['square_icon'] = instance.square_icon.url
        if instance.raster_icon:
            representation['raster_icon'] = instance.raster_icon.url
            
        return representation