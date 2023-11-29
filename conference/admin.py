from django.contrib import admin
from conference.models import *


class CustomUserAdmin_by(admin.ModelAdmin):
    list_display=('name','id','email','number','date','is_active','is_staff','is_conference_admin','is_reviewer','is_auth','password')