from rest_framework import serializers


class MediaUrlField(serializers.CharField):
    def to_representation(self, value):
        return str(value.url)
