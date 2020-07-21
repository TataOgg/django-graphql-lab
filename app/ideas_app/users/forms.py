from django import forms
from ideas_app.users.models import AppUser


class UserForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput()
        }
