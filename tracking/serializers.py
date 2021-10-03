from tracking_fields.models import TrackedFieldModification, TrackingEvent
from rest_framework import serializers
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
