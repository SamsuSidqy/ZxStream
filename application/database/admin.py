from django.contrib import admin

# Register your models here.
from database import models

admin.site.register(models.Authentikasi)
admin.site.register(models.ProfileUser)
admin.site.register(models.StreamKey)
admin.site.register(models.Streaming)

