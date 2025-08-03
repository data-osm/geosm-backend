from dj_rest_auth.serializers import LoginSerializer as BaseLoginSerializer
from django.contrib.auth import password_validation
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from rest_framework import serializers

from account.osm import OSMFeatureType

from .models import User


class LoginSerializer(BaseLoginSerializer):
    def get_auth_user(self, username, email, password):
        user = super().get_auth_user(username, email, password)
        if user and getattr(user, "is_administrator", None) is True:
            return user
        return None


class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "last_name"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "last_name", "is_superuser", "first_name"]


class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    password_2 = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = (
            "id",
            "email",
            "last_name",
            "first_name",
            "is_superuser",
            "password",
            "password_2",
            "username",
        )

    def validate(self, attrs):
        password, password_2 = attrs.get("password"), attrs.get("password_2")
        if password and password != password_2:
            raise serializers.ValidationError(
                {
                    "password": "The provided passwords are not identical",
                }
            )
        del attrs["password_2"]
        return super(UserRegistrationSerializer, self).validate(attrs)


class UserRegisterDeserializer(serializers.Serializer):
    last_name = serializers.CharField()
    first_name = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    password_2 = serializers.CharField()
    is_superuser = serializers.BooleanField()

    def validate_password(self, value):
        password_validation.validate_password(password=value)
        return value

    def to_internal_value(self, data):
        """
        Check passwords and emails are identical together.
        """
        password, password_2 = data.get("password"), data.get("password_2")
        if password and password != password_2:
            raise serializers.ValidationError(
                {
                    "password": "The provided passwords are not identical",
                }
            )
        obj = super().to_internal_value(data)
        del obj["password_2"]
        return obj


class RetrieveOSMUserInfoSerializer(serializers.Serializer):
    display_name = serializers.CharField()


class UpdateOSMFeatureDeserializer(serializers.Serializer):
    osm_id = serializers.IntegerField()
    osm_type = serializers.ChoiceField(choices=OSMFeatureType.choices)
    rnb = serializers.CharField()
    diff_rnb = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class GetParentOsmBuildingDeserializer(serializers.Serializer):
    parent_osm_id = serializers.IntegerField()


class GetParentOsmBuildingSerializer(serializers.Serializer):
    class BuildingParentSerializer(serializers.Serializer):
        osm_id = serializers.IntegerField()
        match_rnb_ids = serializers.CharField()
        match_rnb_score = serializers.FloatField()
        match_rnb_diff = serializers.CharField()

    class ParentOSMSerializer(serializers.Serializer):
        geometry = serializers.JSONField()
        rnb = serializers.CharField()
        diff_rnb = serializers.CharField()

    parent_osm = ParentOSMSerializer()
    parent_matching_rnb = BuildingParentSerializer()
