from django.contrib import admin
from .models import UsuarioLG

@admin.register(UsuarioLG)
class UsuarioLGAdmin(admin.ModelAdmin):
    list_display = ('username','first_name','last_name','email','tipo','is_active')
    list_filter = ('tipo','is_active')
    search_fields = ('username','first_name','last_name','email')