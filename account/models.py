import random
import string

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models


def random_email(domain="not-existing-osm.com", length=10):
    username = "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return f"{username}@{domain}"


class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=75)
    state_relay = models.UUIDField(default=None, null=True)
    is_administrator = models.BooleanField(
        verbose_name="Administrator ?",
        default=False,
        help_text="Designates whether the user can log into this back office",
    )
    osm_token = models.TextField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def update_osm_token(self, *, osm_token, state_relay):
        self.osm_token = osm_token
        self.state_relay = state_relay
        self.save()

    @classmethod
    def create_user_from_osm(cls, *, username: str, osm_token: str, state_relay: str):
        user = cls(
            username=username,
            osm_token=osm_token,
            state_relay=state_relay,
            password=make_password(osm_token),
            email=random_email(),
        )
        user.save()
        return user


class userProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    def __str__(self):
        return self.user.username
