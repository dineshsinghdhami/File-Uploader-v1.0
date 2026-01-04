from django.contrib import admin
from .models import UploadFile


@admin.register(UploadFile)
class UploadFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'file', 'uploaded_at']
    search_fields = ['file']
