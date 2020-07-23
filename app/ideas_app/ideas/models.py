from django.db import models

from ideas_app.users.models import AppUser


class Idea(models.Model):

    class VisibilityOptions(models.TextChoices):
        PUBLIC = 'PUBLIC', 'public'
        PROTECTED = 'PROTECTED', 'protected'
        PRIVATE = 'PRIVATE', 'private'

    text = models.CharField(max_length=280)
    created_on = models.DateTimeField(auto_now_add=True)
    visibility = models.CharField(max_length=9,
                                  choices=VisibilityOptions.choices,
                                  default=VisibilityOptions.PRIVATE)
    author = models.ForeignKey(AppUser, on_delete=models.CASCADE)
