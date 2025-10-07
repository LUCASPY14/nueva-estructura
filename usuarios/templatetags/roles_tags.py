from django import template
register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """Verifica si un usuario pertenece a un grupo específico"""
    return user.groups.filter(name=group_name).exists()

@register.filter(name='is_admin')
def is_admin(user):
    """Verifica si un usuario es administrador"""
    return user.is_superuser or user.groups.filter(name='Administradores').exists()

@register.filter(name='is_cajero')
def is_cajero(user):
    """Verifica si un usuario es cajero"""
    return user.groups.filter(name='Cajeros').exists()

@register.filter(name='is_padre')
def is_padre(user):
    """Verifica si un usuario es padre"""
    return user.groups.filter(name='Padres').exists()