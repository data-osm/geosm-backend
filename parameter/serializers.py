from .models import Parameter, AdminBoundary
from rest_framework import serializers
from provider.serializers import VectorProviderSerializer
from group.serializers import MapSerializer

class AdminBoundaryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminBoundary
        fields = '__all__'

class AdminBoundarySerializer(serializers.ModelSerializer):
    vector = VectorProviderSerializer()
    class Meta:
        model = AdminBoundary
        fields = '__all__'

class ParameterCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = '__all__'

class ParameterSerializer(serializers.ModelSerializer):
    boundary = serializers.SerializerMethodField()
    extent = VectorProviderSerializer(read_only=True)
    map = MapSerializer(read_only=True)

    class Meta:
        model = Parameter
        fields = ['extent','map','extent_pk','parameter_id','boundary']

    def get_boundary(self, instance):
        return AdminBoundarySerializer(AdminBoundary.objects.all(), many=True).data

