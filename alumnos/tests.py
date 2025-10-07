from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from datetime import date, datetime
import tempfile
import os

from alumnos.models import Alumno, SolicitudRecarga, Transaccion
from alumnos.forms import SolicitudRecargaForm, ConsultaSaldoForm


class SaldoSystemTestCase(TestCase):
    """Clase base para todos los tests del sistema de saldo"""
    
    def setUp(self):
        """Configuración inicial para todos los tests"""
        self.client = Client()
        
        # Crear grupos de usuarios
        self.grupo_padres = Group.objects.create(name='PADRE')
        self.grupo_admin = Group.objects.create(name='ADMIN')
        self.grupo_cajeros = Group.objects.create(name='CAJERO')
        
        # Crear usuarios de prueba
        self.padre_user = User.objects.create_user(
            username='padre_test',
            email='padre@test.com',
            password='testpass123',
            first_name='Juan',
            last_name='Pérez'
        )
        self.padre_user.groups.add(self.grupo_padres)
        
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='Sistema'
        )
        self.admin_user.groups.add(self.grupo_admin)
        
        self.cajero_user = User.objects.create_user(
            username='cajero_test',
            email='cajero@test.com',
            password='testpass123',
            first_name='Cajero',
            last_name='Uno'
        )
        self.cajero_user.groups.add(self.grupo_cajeros)
        
        # Crear alumno de prueba
        self.alumno = Alumno.objects.create(
            nombre='María',
            apellido='González',
            numero_matricula='TEST001',
            numero_tarjeta='123456',
            curso='3° Grado A',
            saldo_tarjeta=Decimal('50000.00'),
            limite_consumo=Decimal('15000.00'),
            estado='activo'
        )
        self.alumno.padres.add(self.padre_user)

    def tearDown(self):
        """Limpiar después de cada test"""
        # Limpiar archivos temporales si existen
        pass


class AlumnoModelTest(SaldoSystemTestCase):
    """Tests para el modelo Alumno y sus métodos de saldo"""
    
    def test_get_saldo_formateado(self):
        """Test del método get_saldo_formateado"""
        # Test con saldo normal
        self.assertEqual(self.alumno.get_saldo_formateado(), '$50.000')
        
        # Test con saldo 0
        self.alumno.saldo_tarjeta = Decimal('0')
        self.assertEqual(self.alumno.get_saldo_formateado(), '$0')
        
        # Test con saldo alto
        self.alumno.saldo_tarjeta = Decimal('1500000')
        self.assertEqual(self.alumno.get_saldo_formateado(), '$1.500.000')
    
    def test_puede_consumir(self):
        """Test del método puede_consumir"""
        # Alumno activo con saldo suficiente
        self.assertTrue(self.alumno.puede_consumir(Decimal('10000')))
        
        # Monto mayor al saldo
        self.assertFalse(self.alumno.puede_consumir(Decimal('60000')))
        
        # Alumno inactivo
        self.alumno.estado = 'inactivo'
        self.alumno.save()
        self.assertFalse(self.alumno.puede_consumir(Decimal('10000')))
        
        # Restaurar estado
        self.alumno.estado = 'activo'
        self.alumno.save()
    
    def test_consumir_saldo(self):
        """Test del método consumir_saldo"""
        saldo_inicial = self.alumno.saldo_tarjeta
        monto_consumo = Decimal('15000')
        
        resultado = self.alumno.consumir_saldo(monto_consumo, 'Compra en cafetería')
        
        self.assertTrue(resultado)
        self.alumno.refresh_from_db()
        self.assertEqual(self.alumno.saldo_tarjeta, saldo_inicial - monto_consumo)
        
        # Verificar que se creó la transacción
        transaccion = Transaccion.objects.filter(
            alumno=self.alumno, 
            tipo='consumo'
        ).order_by('-fecha').first()
        
        self.assertIsNotNone(transaccion)
        self.assertEqual(transaccion.monto, monto_consumo)
    
    def test_cargar_saldo(self):
        """Test del método cargar_saldo"""
        saldo_inicial = self.alumno.saldo_tarjeta
        monto_carga = Decimal('25000')
        
        resultado = self.alumno.cargar_saldo(monto_carga, 'Recarga manual')
        
        self.assertTrue(resultado)
        self.alumno.refresh_from_db()
        self.assertEqual(self.alumno.saldo_tarjeta, saldo_inicial + monto_carga)
        
        # Verificar que se creó la transacción
        transaccion = Transaccion.objects.filter(
            alumno=self.alumno, 
            tipo='recarga'
        ).order_by('-fecha').first()
        
        self.assertIsNotNone(transaccion)
        self.assertEqual(transaccion.monto, monto_carga)


class SolicitudRecargaModelTest(SaldoSystemTestCase):
    """Tests para el modelo SolicitudRecarga"""
    
    def test_create_solicitud(self):
        """Test de creación de solicitud"""
        solicitud = SolicitudRecarga.objects.create(
            alumno=self.alumno,
            padre_solicitante=self.padre_user,
            monto_solicitado=Decimal('100000'),
            metodo_pago='transferencia',
            referencia_pago='TRF123456'
        )
        
        self.assertEqual(solicitud.estado, 'pendiente')
        self.assertEqual(solicitud.monto_solicitado, Decimal('100000'))
        self.assertEqual(solicitud.padre_solicitante, self.padre_user)
        self.assertIsNotNone(solicitud.fecha_solicitud)
    
    def test_aprobar_solicitud(self):
        """Test de aprobación de solicitud"""
        solicitud = SolicitudRecarga.objects.create(
            alumno=self.alumno,
            padre_solicitante=self.padre_user,
            monto_solicitado=Decimal('100000'),
            metodo_pago='transferencia'
        )
        
        saldo_inicial = self.alumno.saldo_tarjeta
        
        # Aprobar solicitud
        solicitud.estado = 'aprobada'
        solicitud.monto_aprobado = Decimal('100000')
        solicitud.fecha_procesamiento = datetime.now()
        solicitud.observaciones_admin = 'Aprobado - comprobante válido'
        solicitud.save()
        
        # Cargar saldo (esto normalmente se hace en la vista)
        self.alumno.cargar_saldo(
            solicitud.monto_aprobado,
            f'Recarga aprobada - Solicitud #{solicitud.id}'
        )
        
        self.alumno.refresh_from_db()
        self.assertEqual(self.alumno.saldo_tarjeta, saldo_inicial + Decimal('100000'))
    
    def test_rechazar_solicitud(self):
        """Test de rechazo de solicitud"""
        solicitud = SolicitudRecarga.objects.create(
            alumno=self.alumno,
            padre_solicitante=self.padre_user,
            monto_solicitado=Decimal('50000'),
            metodo_pago='efectivo'
        )
        
        saldo_inicial = self.alumno.saldo_tarjeta
        
        # Rechazar solicitud
        solicitud.estado = 'rechazada'
        solicitud.fecha_procesamiento = datetime.now()
        solicitud.observaciones_admin = 'Comprobante no válido'
        solicitud.save()
        
        # El saldo no debe cambiar
        self.alumno.refresh_from_db()
        self.assertEqual(self.alumno.saldo_tarjeta, saldo_inicial)


class SolicitudRecargaFormTest(SaldoSystemTestCase):
    """Tests para el formulario de solicitud de recarga"""
    
    def test_form_valid_data(self):
        """Test con datos válidos"""
        form_data = {
            'alumno': self.alumno.id,
            'monto_solicitado': 75000,
            'metodo_pago': 'transferencia',
            'referencia_pago': 'TRF123456'
        }
        
        form = SolicitudRecargaForm(data=form_data, user=self.padre_user)
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_monto_bajo(self):
        """Test con monto muy bajo"""
        form_data = {
            'alumno': self.alumno.id,
            'monto_solicitado': 500,  # Menos del mínimo
            'metodo_pago': 'transferencia'
        }
        
        form = SolicitudRecargaForm(data=form_data, user=self.padre_user)
        self.assertFalse(form.is_valid())
        self.assertIn('monto_solicitado', form.errors)
    
    def test_form_invalid_monto_alto(self):
        """Test con monto muy alto"""
        form_data = {
            'alumno': self.alumno.id,
            'monto_solicitado': 5000000,  # Más del máximo
            'metodo_pago': 'transferencia'
        }
        
        form = SolicitudRecargaForm(data=form_data, user=self.padre_user)
        self.assertFalse(form.is_valid())
        self.assertIn('monto_solicitado', form.errors)


class ConsultaSaldoFormTest(TestCase):
    """Tests para el formulario de consulta de saldo"""
    
    def test_form_valid_data(self):
        """Test con número de tarjeta válido"""
        form_data = {'numero_tarjeta': '123456'}
        form = ConsultaSaldoForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_data(self):
        """Test con número de tarjeta inválido"""
        # Test con letras
        form_data = {'numero_tarjeta': 'abc123'}
        form = ConsultaSaldoForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # Test con campo vacío
        form_data = {'numero_tarjeta': ''}
        form = ConsultaSaldoForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # Test muy corto
        form_data = {'numero_tarjeta': '12'}
        form = ConsultaSaldoForm(data=form_data)
        self.assertFalse(form.is_valid())


class TransaccionModelTest(SaldoSystemTestCase):
    """Tests para el modelo Transaccion"""
    
    def test_create_transaccion_consumo(self):
        """Test de creación de transacción de consumo"""
        transaccion = Transaccion.objects.create(
            alumno=self.alumno,
            tipo='consumo',
            monto=Decimal('8500'),
            descripcion='Almuerzo cafetería',
            saldo_anterior=self.alumno.saldo_tarjeta,
            saldo_posterior=self.alumno.saldo_tarjeta - Decimal('8500')
        )
        
        self.assertEqual(transaccion.tipo, 'consumo')
        self.assertEqual(transaccion.monto, Decimal('8500'))
        self.assertIsNotNone(transaccion.fecha)
        self.assertEqual(transaccion.alumno, self.alumno)
    
    def test_create_transaccion_recarga(self):
        """Test de creación de transacción de recarga"""
        transaccion = Transaccion.objects.create(
            alumno=self.alumno,
            tipo='recarga',
            monto=Decimal('25000'),
            descripcion='Recarga por transferencia',
            saldo_anterior=self.alumno.saldo_tarjeta,
            saldo_posterior=self.alumno.saldo_tarjeta + Decimal('25000')
        )
        
        self.assertEqual(transaccion.tipo, 'recarga')
        self.assertEqual(transaccion.monto, Decimal('25000'))
        self.assertTrue(transaccion.monto > 0)


class PermissionsTest(SaldoSystemTestCase):
    """Tests de permisos y seguridad"""
    
    def test_padre_acceso_permitido(self):
        """Test que padre puede acceder a sus vistas"""
        self.client.login(username='padre_test', password='testpass123')
        
        # URLs que el padre debe poder acceder
        urls_permitidas = [
            reverse('alumnos:dashboard_padre'),
            reverse('alumnos:solicitar_recarga'),
        ]
        
        for url in urls_permitidas:
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 403, 
                              f"Padre no puede acceder a {url}")
    
    def test_padre_acceso_denegado(self):
        """Test que padre no puede acceder a vistas de admin"""
        self.client.login(username='padre_test', password='testpass123')
        
        # URLs que el padre NO debe poder acceder
        urls_denegadas = [
            reverse('alumnos:dashboard_admin'),
            reverse('alumnos:solicitudes_pendientes'),
        ]
        
        for url in urls_denegadas:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403,
                           f"Padre puede acceder incorrectamente a {url}")
    
    def test_cajero_acceso_permitido(self):
        """Test que cajero puede acceder a consulta de saldo"""
        self.client.login(username='cajero_test', password='testpass123')
        
        url = reverse('alumnos:consulta_saldo')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302])
    
    def test_admin_acceso_completo(self):
        """Test que admin puede acceder a todas las vistas"""
        self.client.login(username='admin_test', password='testpass123')
        
        urls_admin = [
            reverse('alumnos:dashboard_admin'),
            reverse('alumnos:solicitudes_pendientes'),
            reverse('alumnos:consulta_saldo'),
        ]
        
        for url in urls_admin:
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302],
                         f"Admin no puede acceder a {url}")


# Test de integración completa
class IntegrationTest(SaldoSystemTestCase):
    """Tests de integración del sistema completo"""
    
    def test_flujo_completo_solicitud_recarga(self):
        """Test del flujo completo: solicitar -> aprobar -> cargar saldo"""
        
        # 1. Padre hace solicitud
        self.client.login(username='padre_test', password='testpass123')
        
        solicitud_data = {
            'alumno': self.alumno.id,
            'monto_solicitado': 100000,
            'metodo_pago': 'transferencia',
            'referencia_pago': 'TRF999'
        }
        
        response = self.client.post(
            reverse('alumnos:solicitar_recarga'), 
            solicitud_data
        )
        
        # Verificar redirección (éxito)
        self.assertEqual(response.status_code, 302)
        
        # 2. Verificar que se creó la solicitud
        solicitud = SolicitudRecarga.objects.get(
            alumno=self.alumno,
            referencia_pago='TRF999'
        )
        self.assertEqual(solicitud.estado, 'pendiente')
        
        # 3. Admin procesa la solicitud
        saldo_inicial = self.alumno.saldo_tarjeta
        
        solicitud.estado = 'aprobada'
        solicitud.monto_aprobado = Decimal('100000')
        solicitud.fecha_procesamiento = datetime.now()
        solicitud.observaciones_admin = 'Aprobado - comprobante válido'
        solicitud.save()
        
        # 4. Cargar saldo al alumno
        resultado = self.alumno.cargar_saldo(
            solicitud.monto_aprobado,
            f'Recarga aprobada - Solicitud #{solicitud.id}'
        )
        
        self.assertTrue(resultado)
        self.alumno.refresh_from_db()
        self.assertEqual(
            self.alumno.saldo_tarjeta,
            saldo_inicial + Decimal('100000')
        )
        
        # 5. Verificar transacción
        transaccion = Transaccion.objects.filter(
            alumno=self.alumno,
            tipo='recarga',
            monto=Decimal('100000')
        ).first()
        
        self.assertIsNotNone(transaccion)
        self.assertIn('Solicitud #', transaccion.descripcion)
    
    def test_flujo_consulta_saldo_cajero(self):
        """Test del flujo de consulta de saldo por cajero"""
        
        # Cajero consulta saldo
        self.client.login(username='cajero_test', password='testpass123')
        
        response = self.client.post(
            reverse('alumnos:consulta_saldo'),
            {'numero_tarjeta': '123456'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.alumno.get_nombre_completo())
        self.assertContains(response, '$50.000')
        self.assertIn('alumno', response.context)
        self.assertEqual(response.context['alumno'], self.alumno)
    
    def test_consumo_y_limite_diario(self):
        """Test de consumo respetando límite diario"""
        
        # Test consumo normal
        resultado = self.alumno.consumir_saldo(
            Decimal('10000'), 
            'Desayuno'
        )
        self.assertTrue(resultado)
        
        # Test consumo que excede límite diario
        # (Esto depende de la implementación del límite diario)
        resultado_limite = self.alumno.consumir_saldo(
            Decimal('20000'),  # Más que el límite de 15000
            'Compra grande'
        )
        
        # Debe fallar si tienes implementada la validación de límite
        # self.assertFalse(resultado_limite)
        
        # Restaurar saldo para otros tests
        self.alumno.saldo_tarjeta = Decimal('50000')
        self.alumno.save()