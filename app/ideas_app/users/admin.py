from django.contrib import admin
from ideas_app.users.models import AppUser, Follow
from ideas_app.users.forms import UserForm


class UserAdmin(admin.ModelAdmin):
    form = UserForm


admin.site.register(AppUser, UserAdmin)
admin.site.register(Follow)
