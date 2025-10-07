from django.core.management.base import BaseCommand
from ventas.models import Caja, MetodoPago

class Command(BaseCommand):
    help = 'Configura datos iniciales para el módulo de ventas'

    def handle(self, *args, **options):
        # Crear cajas por defecto
        cajas_default = [
            {'numero': 1, 'nombre': 'Caja Principal', 'ubicacion': 'Entrada principal'},
            {'numero': 2, 'nombre': 'Caja Secundaria', 'ubicacion': 'Área secundaria'},
        ]
        
        for caja_data in cajas_default:
            caja, created = Caja.objects.get_or_create(
                numero=caja_data['numero'],
                defaults=caja_data
            )
            if created:
                self.stdout.write(f'Caja {caja.numero} creada: {caja.nombre}')
            else:
                self.stdout.write(f'Caja {caja.numero} ya existe')

        # Crear métodos de pago por defecto
        metodos_default = [
            {'nombre': 'Efectivo', 'descripcion': 'Pago en efectivo', 'requiere_referencia': False},
            {'nombre': 'Tarjeta de Débito', 'descripcion': 'Pago con tarjeta de débito', 'requiere_referencia': True},
            {'nombre': 'Tarjeta de Crédito', 'descripcion': 'Pago con tarjeta de crédito', 'requiere_referencia': True},
            {'nombre': 'Transferencia', 'descripcion': 'Transferencia bancaria', 'requiere_referencia': True},
            {'nombre': 'QR/Wallet', 'descripcion': 'Pago por código QR o billetera digital', 'requiere_referencia': True},
        ]
        
        for metodo_data in metodos_default:
            metodo, created = MetodoPago.objects.get_or_create(
                nombre=metodo_data['nombre'],
                defaults=metodo_data
            )
            if created:
                self.stdout.write(f'Método de pago creado: {metodo.nombre}')
            else:
                self.stdout.write(f'Método de pago ya existe: {metodo.nombre}')

        self.stdout.write(self.style.SUCCESS('Configuración inicial de ventas completada'))