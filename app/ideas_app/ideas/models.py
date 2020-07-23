from django.db import models

from ideas_app.users.models import AppUser, Follow


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

    def save(self, **kwargs):
        super().save(**kwargs)
        followers = Follow.objects.select_related('follower').filter(
            user=self.author)

        # send notification using a django pusher mobile / web
        # to each follower.follower
        pass
