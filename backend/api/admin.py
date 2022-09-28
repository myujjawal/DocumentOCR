from django.contrib import admin
from .models import Aadhaar, AadhaarImg
# Register your models here.


@admin.register(Aadhaar)
class AadhaarAdmin(admin.ModelAdmin):
    list_display = ['aadhaar_number', 'name', 'dob', 'address']


@admin.register(AadhaarImg)
class AadhaarImgAdmin(admin.ModelAdmin):
    list_display = ['title', 'content', 'image']
