from rest_framework import serializers
from .models import User
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer

class userSerializer(serializers.ModelSerializer):
    # user=serializers.StringRelatedField(read_only=True)
    class Meta:
        model=User
        fields=['created_at','email','id','is_active','is_superuser','updated_at','username','last_name']

class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = ('id', 'email', 'last_name', 'is_superuser', 'password','username' )