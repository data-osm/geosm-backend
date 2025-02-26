from rest_framework import serializers
from tracking_fields.models import TrackedFieldModification, TrackingEvent

from account.serializers import UserNameSerializer


class TrackedFieldModificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackedFieldModification
        fields = ["field", "old_value", "new_value"]


class TrackingEventSerializer(serializers.ModelSerializer):
    """
    TrackingEvent serializer
    """

    fields = TrackedFieldModificationSerializer(many=True)
    user = UserNameSerializer()

    class Meta:
        model = TrackingEvent
        fields = ["date", "action", "object_id", "fields", "user"]


class LogRenderTimePerFrameDeserializer(serializers.Serializer):
    class FrameRenderTime(serializers.Serializer):
        frame_index = serializers.IntegerField()
        total_render_time = serializers.FloatField()
        render_time = serializers.FloatField()

    frame_render_time = FrameRenderTime(many=True)
    layers_names = serializers.ListField(child=serializers.CharField())
    layers_ids = serializers.ListField(child=serializers.IntegerField())
    extent_size = serializers.ListField(child=serializers.FloatField())
    extent = serializers.CharField()
    current_url = serializers.CharField()


class CreateNPSFeedbackDeserializer(serializers.Serializer):
    score = serializers.IntegerField(required=False, allow_null=True)
