from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from alumnos.models import ConfiguracionPagos

class Command(BaseCommand):
    help = 'Configuración inicial del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--crear-admin',
            action='store_true',
            help='Crear usuario administrador',
        )

    def handle(self, *args, **options):
        self.stdout.write('Iniciando configuración del sistema...')
        
        # Crear configuración de pagos por defecto
        self.crear_configuracion_pagos()
        
        # Crear usuario admin si se solicita
        if options['crear_admin']:
            self.crear_usuario_admin()
        
        self.stdout.write(
            self.style.SUCCESS('Configuración inicial completada.')
        )

    def crear_configuracion_pagos(self):
        """Crea configuración de pagos por defecto"""
        if not ConfiguracionPagos.objects.exists():
            ConfiguracionPagos.objects.create(
                nombre_banco='Banco de ejemplo',
                titular_cuenta='Institución Educativa',
                numero_cuenta='1234567890',
                ruc='12345678-9',
                instrucciones='Realice la transferencia y adjunte el comprobante.',
                monto_minimo=1000,
                activo=True
            )
            self.stdout.write(
                self.style.SUCCESS('Configuración de pagos creada.')
            )
        else:
            self.stdout.write('Configuración de pagos ya existe.')

    def crear_usuario_admin(self):
        """Crea usuario administrador por defecto"""
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@cantina.edu',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema'
            )
            self.stdout.write(
                self.style.SUCCESS(
                    'Usuario administrador creado:\n'
                    'Usuario: admin\n'
                    'Contraseña: admin123\n'
                    '¡CAMBIE LA CONTRASEÑA INMEDIATAMENTE!'
                )
            )
        else:
            self.stdout.write('Usuario administrador ya existe.')