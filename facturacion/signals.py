from django.db.models.signals import post_save
from django.dispatch import receiver
from ventas.models import Venta
from .models import Factura

@receiver(post_save, sender=Venta)
def crear_factura_automatica(sender, instance, created, **kwargs):
    """
    Crea automáticamente una factura cuando se guarda una venta.
    """
    if created and instance.estado == 'completada' and instance.cliente:
        cliente = instance.cliente
        
        # Determinar la razón social
        if hasattr(cliente, 'padre') and cliente.padre:
            razon_social = cliente.padre.nombre
            ruc = getattr(cliente.padre, 'ruc', '')
        else:
            razon_social = f"{cliente.nombre} {cliente.apellido}"
            ruc = ""
        
        Factura.objects.create(
            venta=instance,
            numero_factura=f"F{instance.numero_venta}",
            fecha=instance.fecha,
            razon_social=razon_social,
            ruc=ruc,
            subtotal=instance.subtotal,
            total=instance.total,
            estado='emitida'
        )
