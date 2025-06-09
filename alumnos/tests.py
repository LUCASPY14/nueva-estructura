from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Padre, Alumno

User = get_user_model()

class AlumnoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='padre1', password='test123')
        self.padre = Padre.objects.create(
            usuario=self.user,
            nombre='Juan', apellido='Pérez', razon_social='', ruc='',
            email='juan@test.com', telefono='123', direccion='Calle 1', barrio='Centro', ciudad='Ciudad'
        )
        self.alumno = Alumno.objects.create(
            padre=self.padre, nombre='Pedro', grado='1ro', nivel='Primario',
            limite_consumo=10000, saldo_tarjeta=5000, numero_tarjeta='12345'
        )

    def test_str(self):
        self.assertIn('Pedro', str(self.alumno))

    def test_saldo_restante(self):
        self.assertEqual(self.alumno.saldo_restante(), 5000)

class PadreModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='padre2', password='test123')
        self.padre = Padre.objects.create(
            usuario=self.user,
            nombre='Ana', apellido='Gómez', razon_social='', ruc='',
            email='ana@test.com', telefono='456', direccion='Calle 2', barrio='Norte', ciudad='Ciudad'
        )

    def test_str(self):
        self.assertIn('Ana', str(self.padre))