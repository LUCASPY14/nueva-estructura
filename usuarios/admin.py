from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'telefono', 'is_active')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('telefono', 'direccion', 'fecha_nacimiento')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {'fields': ('telefono', 'direccion', 'fecha_nacimiento')}),
    )

    # Si querés agregar filtros avanzados por grupo, etc., se pueden sumar aquí.

