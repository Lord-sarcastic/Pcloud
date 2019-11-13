from django.contrib import admin
from .models import CustomUser, Drive, Folder, File


admin.site.register(CustomUser)
admin.site.register(Drive)
admin.site.register(Folder)
admin.site.register(File)