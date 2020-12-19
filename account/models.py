from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q

class User(AbstractUser):
    ...
    email = models.EmailField(unique=True,max_length=75)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class userProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")

    def __str__(self):
        return self.user.username
