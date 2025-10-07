from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Venta, DetalleVenta, PagoVenta, Caja, TurnoCajero, MetodoPago
from productos.models import Producto, Categoria
from alumnos.models import Alumno

User = get_user_model()

class VentaTestCase(TestCase):
    def setUp(self):
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear caja de prueba
        self.caja = Caja.objects.create(
            numero=1,
            nombre='Caja Test',
            ubicacion='Test'
        )
        
        # Crear turno de prueba
        self.turno = TurnoCajero.objects.create(
            cajero=self.user,
            caja=self.caja,
            monto_inicial=Decimal('100.00')
        )
        
        # Crear método de pago
        self.metodo_pago = MetodoPago.objects.create(
            nombre='Efectivo',
            descripcion='Pago en efectivo'
        )
        
        # Crear categoría y producto de prueba
        self.categoria = Categoria.objects.create(
            nombre='Test Category'
        )
        
        self.producto = Producto.objects.create(
            nombre='Producto Test',
            codigo='TEST001',
            categoria=self.categoria,
            precio_venta=Decimal('10.00'),
            cantidad=100
        )
        
        # Crear alumno de prueba
        self.alumno = Alumno.objects.create(
            nombre='Test Student',
            apellido='Test',
            numero_telefono='1234567890'
        )

    def test_crear_venta(self):
        """Test creación de venta básica"""
        venta = Venta.objects.create(
            cajero=self.user,
            turno_cajero=self.turno,
            cliente=self.alumno
        )
        
        self.assertTrue(venta.numero_venta)
        self.assertEqual(venta.estado, 'pendiente')
        self.assertEqual(venta.cajero, self.user)

    def test_detalle_venta(self):
        """Test creación de detalle de venta"""
        venta = Venta.objects.create(
            cajero=self.user,
            turno_cajero=self.turno,
            cliente=self.alumno
        )
        
        detalle = DetalleVenta.objects.create(
            venta=venta,
            producto=self.producto,
            cantidad=Decimal('2.000'),
            precio_unitario=Decimal('10.00')
        )
        
        self.assertEqual(detalle.subtotal, Decimal('20.00'))

    def test_pago_venta(self):
        """Test creación de pago de venta"""
        venta = Venta.objects.create(
            cajero=self.user,
            turno_cajero=self.turno,
            cliente=self.alumno
        )
        
        pago = PagoVenta.objects.create(
            venta=venta,
            metodo_pago=self.metodo_pago,
            monto=Decimal('20.00')
        )
        
        self.assertEqual(pago.monto, Decimal('20.00'))
        self.assertEqual(pago.metodo_pago, self.metodo_pago)
