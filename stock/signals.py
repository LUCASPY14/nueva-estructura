from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from compras.models import DetalleCompra
from ventas.models import DetalleVenta
from .models import MovimientoStock

@receiver(post_save, sender=DetalleCompra)
def create_stock_ingreso(sender, instance, created, **kwargs):
    if created:
        mov = MovimientoStock.objects.create(
            producto=instance.producto,
            tipo='INGRESO',
            cantidad=instance.cantidad,
            referencia=f'COMPRA-{instance.compra.id}',
            motivo='Ingreso automático por compra'
        )
        mov.aplicar()

@receiver(post_delete, sender=DetalleCompra)
def revert_stock_ingreso(sender, instance, **kwargs):
    MovimientoStock.objects.create(
        producto=instance.producto,
        tipo='EGRESO',
        cantidad=instance.cantidad,
        referencia=f'REVERSA-COMPRA-{instance.compra.id}',
        motivo='Reversión automática de ingreso por eliminación de compra'
    ).aplicar()

@receiver(post_save, sender=DetalleVenta)
def create_stock_egreso(sender, instance, created, **kwargs):
    if created:
        mov = MovimientoStock.objects.create(
            producto=instance.producto,
            tipo='EGRESO',
            cantidad=instance.cantidad,
            referencia=f'VENTA-{instance.venta.id}',
            motivo='Egreso automático por venta'
        )
        mov.aplicar()

@receiver(post_delete, sender=DetalleVenta)
def revert_stock_egreso(sender, instance, **kwargs):
    MovimientoStock.objects.create(
        producto=instance.producto,
        tipo='INGRESO',
        cantidad=instance.cantidad,
        referencia=f'REVERSA-VENTA-{instance.venta.id}',
        motivo='Reversión automática de egreso por eliminación de venta'
    ).aplicar()