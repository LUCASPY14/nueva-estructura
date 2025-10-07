from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django.db import models
from .models import MovimientoStock, Producto
from .notifications import StockNotification

User = get_user_model()

@receiver(post_save, sender=MovimientoStock)
def check_stock_level(sender, instance, created, **kwargs):
    """
    Signal que verifica el nivel de stock después de cada movimiento
    y crea notificaciones según sea necesario.
    """
    if not created:
        return
        
    producto = instance.producto
    cantidad = producto.cantidad
    cantidad_minima = producto.cantidad_minima
    
    # Determinar el tipo y prioridad de la notificación
    if cantidad == 0:
        tipo = 'agotado'
        prioridad = 'critica'
        mensaje = _(f'¡URGENTE! El producto {producto.nombre} se ha agotado.')
    elif cantidad <= cantidad_minima * 0.5:
        tipo = 'stock_bajo'
        prioridad = 'alta'
        mensaje = _(f'Stock crítico: {producto.nombre} está por debajo del 50% del mínimo requerido.')
    elif cantidad <= cantidad_minima:
        tipo = 'reorden'
        prioridad = 'media'
        mensaje = _(f'Punto de reorden: {producto.nombre} ha alcanzado el nivel mínimo de stock.')
    else:
        return  # No se necesita notificación
    
    # Crear la notificación
    notificacion = StockNotification.objects.create(
        producto=producto,
        tipo=tipo,
        mensaje=mensaje,
        prioridad=prioridad
    )
    
    # Asignar destinatarios (usuarios con permisos relevantes)
    usuarios_notificar = User.objects.filter(
        is_active=True
    ).filter(
        models.Q(is_superuser=True) |
        models.Q(groups__permissions__codename='change_producto')
    ).distinct()
    
    notificacion.destinatarios.set(usuarios_notificar)