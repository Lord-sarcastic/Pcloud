import PIL
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django import forms
from django.core.files.storage import FileSystemStorage
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

def user_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.owner.username, filename)

class CustomUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.username)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        kwargs = {'slug' : self.slug}
        return reverse('', kwargs=kwargs)
    
    def __str__(self):
        return self.user.username
        
class Drive(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    cover_picture = models.ImageField(upload_to=f'media/{user_path}', default="media/drive.png")
    created_at = models.DateTimeField()
    slug = models.SlugField(blank=True)
    
    def get_absolute_url(self):
        kwargs = {'slug' : self.slug}
        return reverse('', kwargs=kwargs)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
    
    class Meta:
        unique_together = [['owner', 'name']]
        ordering = ('name',)

class Folder(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    drive = models.ForeignKey('Drive', on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True)
    cover_picture = models.ImageField(upload_to=f'media/{user_path}', default="media/folder-white.png")
    created_at = models.DateTimeField()
    slug = models.SlugField(blank=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        kwargs = {'slug' : self.slug}
        return reverse('', kwargs=kwargs)
    
    class Meta:
        unique_together = [['parent', 'name']]
        ordering = ('name',)
    
class File(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    item = models.FileField(upload_to=f'media/{user_path}')
    drive = models.ForeignKey('Drive', on_delete=models.CASCADE, blank=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, blank=True)
    cover_picture = models.ImageField(upload_to=f'media/{user_path}', default="media/file.png")
    created_at = models.DateTimeField()
    slug = models.SlugField(blank=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        kwargs = {'slug' : self.slug}
        return reverse('', kwargs=kwargs)
    
    class Meta:
        unique_together = [['folder', 'name']]
        ordering = ('name',)