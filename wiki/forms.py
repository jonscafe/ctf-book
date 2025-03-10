from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm

class UserUpdateForm(UserChangeForm):
    password = None  # Exclude the password field

    class Meta:
        model = User
        fields = ['username']