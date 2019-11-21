from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from .models import File, Folder, Drive
    
class CreateUserForm(ModelForm):
    error_css_class = 'error'
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={ 'placeholder' : 'Confirm password'}), label="Confirm password")
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password', 'confirm_password',)

        widgets = {
            'password' : forms.PasswordInput,
            'confirm_password' : forms.PasswordInput,
        }

class EditUserForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')

        widgets = {
        }

#407

class DriveCreateForm(ModelForm):
    class Meta:
        model = Drive
        fields = ('name', 'cover_picture')

        widgets = {
            'cover_picture' : forms.ClearableFileInput,
        }

        
class FolderCreateForm(ModelForm):
    class Meta:
        model = Folder
        fields = ('name', 'cover_picture')

        widgets = {
            'username' : forms.TextInput,
            'cover_picture' : forms.ClearableFileInput,
        }
        
class FileCreateForm(ModelForm):
    class Meta:
        model = File
        fields = ('name', 'item', 'cover_picture')

        widgets = {
            'name' : forms.TextInput,
            'item' : forms.ClearableFileInput,
        }
        
class UserLoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

        widgets = {
            'username' : forms.TextInput,
            'password' : forms.PasswordInput,
        }