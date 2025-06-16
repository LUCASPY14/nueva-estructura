from django.contrib import admin
from .models import UsuarioLG

@admin.register(UsuarioLG)
class UsuarioLGAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'tipo', 'is_active')
    list_filter = ('tipo', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'email', 'tipo')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'tipo'),
        }),
    )

    # Si querés agregar filtros avanzados por grupo, etc., se pueden sumar aquí.

