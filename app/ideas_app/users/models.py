from django.db import models
from django.db.models import CASCADE
from django.contrib.auth.models import AbstractUser


class AppUser(AbstractUser):
    email = models.EmailField(max_length=255)
    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"


class Follow(models.Model):
    pending = models.BooleanField(default=True)
    user = models.ForeignKey(AppUser, related_name='user', on_delete=CASCADE)
    follower = models.ForeignKey(AppUser, related_name='follower',
                                 on_delete=CASCADE)

