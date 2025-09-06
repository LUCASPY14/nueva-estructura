from django.test import TestCase
from django.contrib.auth import get_user_model
from alumnos.models import Alumno, Padre
from productos.models import Producto
from .models import Venta, DetalleVenta, Pago

User = get_user_model()

class VentaFlowTest(TestCase):
    def setUp(self):
        self.cajero = User.objects.create_user(username='cajero', password='test123')
        self.padre = Padre.objects.create(
            usuario=User.objects.create_user(username='padre', password='test123'),
            nombre='Padre', apellido='Test', razon_social='', ruc='',
            email='padre@test.com', telefono='123', direccion='Calle', barrio='Centro', ciudad='Ciudad'
        )
        self.alumno = Alumno.objects.create(
            padre=self.padre, nombre='Alumno', grado='1ro', nivel='Primario',
            limite_consumo=100000, saldo_tarjeta=50000, numero_tarjeta='9999'
        )
        self.producto = Producto.objects.create(nombre='Sandwich', precio=10000)

    def test_venta_efectivo(self):
        self.client.force_login(self.cajero)
        response = self.client.post('/ventas/registrar/', {
            'numero_tarjeta': '9999',
            f'producto_{self.producto.id}': 2,
            'metodo': 'EFECTIVO',
            'monto': 20000,
        })
        self.assertEqual(Venta.objects.count(), 1)
        venta = Venta.objects.first()
        self.assertEqual(venta.cajero, self.cajero)
        self.assertEqual(venta.total, 20000)
        self.assertContains(response, "Venta registrada correctamente", status_code=302)

    def test_venta_saldo_insuficiente(self):
        self.client.force_login(self.cajero)
        response = self.client.post('/ventas/registrar/', {
            'numero_tarjeta': '9999',
            f'producto_{self.producto.id}': 10,
            'metodo': 'SALDO',
            'monto': 100000,  # mayor que el saldo
        })
        self.assertContains(response, "Saldo insuficiente", status_code=200)
        self.assertEqual(Venta.objects.count(), 0)

    def test_venta_producto_restringido(self):
        # Crea una restricción para el producto
        self.alumno.restricciones.create(producto=self.producto, permitido=False)
        self.client.force_login(self.cajero)
        response = self.client.post('/ventas/registrar/', {
            'numero_tarjeta': '9999',
            f'producto_{self.producto.id}': 1,
            'metodo': 'EFECTIVO',
            'monto': 10000,
        })
        self.assertContains(response, "restringido para este alumno", status_code=200)
        self.assertEqual(Venta.objects.count(), 0)
