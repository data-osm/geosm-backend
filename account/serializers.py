from rest_framework import serializers
from .models import User

class userSerializer(serializers.ModelSerializer):
    # user=serializers.StringRelatedField(read_only=True)
    class Meta:
        model=User
        fields=['created_at','email','id','is_active','is_superuser','updated_at','username']
