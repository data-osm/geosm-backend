from rest_framework import serializers
from django.contrib.auth import password_validation
from .models import User
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer


class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "last_name"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "last_name", "is_superuser", "first_name"]


# class userSerializer(serializers.ModelSerializer):
#     # user=serializers.StringRelatedField(read_only=True)
#     class Meta:
#         model = User
#         fields = [
#             "created_at",
#             "email",
#             "id",
#             "is_active",
#             "is_superuser",
#             "updated_at",
#             "username",
#             "last_name",
#         ]


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
    email = serializers.CharField()
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
        email, email_2 = data.get("email"), data.get("email_2")
        if email and email != email_2:
            raise serializers.ValidationError(
                {
                    "email": "The provided emails are not identical",
                }
            )
        obj = super().to_internal_value(data)
        del obj["password_2"]
        del obj["email_2"]
        return obj
