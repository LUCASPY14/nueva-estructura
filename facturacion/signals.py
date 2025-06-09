from django.db.models.signals import post_save
from django.dispatch import receiver
from ventas.models import Venta
from facturacion.models import Factura

@receiver(post_save, sender=Venta)
def crear_factura_automatica(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'factura'):
        # Generar número único (ejemplo básico)
        numero_factura = f"F{instance.id:06d}"
        Factura.objects.create(
            venta=instance,
            numero=numero_factura,
            total=instance.total,
            razon_social=instance.alumno.padre.nombre if hasattr(instance.alumno, 'padre') else instance.alumno.nombre,
            ruc='Sin RUC',
            direccion='Sin dirección',
        )
