# accounts/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Profile

class CreateUserForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)

class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'is_active']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['role', 'active']
