from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction

User = get_user_model()  # Obtenemos el modelo de usuario personalizado

class Command(BaseCommand):
    help = 'Crea usuarios de prueba con diferentes roles para el sistema'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creando usuarios de prueba con diferentes roles...')

        # Crear los grupos si no existen
        admin_group, created = Group.objects.get_or_create(name='Administradores')
        if created:
            self.stdout.write(self.style.SUCCESS('Grupo Administradores creado'))
        
        cajero_group, created = Group.objects.get_or_create(name='Cajeros')
        if created:
            self.stdout.write(self.style.SUCCESS('Grupo Cajeros creado'))
        
        padre_group, created = Group.objects.get_or_create(name='Padres')
        if created:
            self.stdout.write(self.style.SUCCESS('Grupo Padres creado'))

        # Crear usuarios de prueba
        with transaction.atomic():
            # 1. Usuario Administrador
            try:
                admin = User.objects.get(username='admin')
                self.stdout.write('Usuario admin ya existe')
            except User.DoesNotExist:
                admin = User.objects.create_user(
                    username='admin',
                    email='admin@lgservice.com',
                    password='admin123',
                    first_name='Admin',
                    last_name='Sistema'
                )
                admin.is_staff = True
                admin.is_superuser = True
                admin.save()
                admin.groups.add(admin_group)
                self.stdout.write(self.style.SUCCESS('Usuario administrador creado: admin / admin123'))

            # 2. Usuario Cajero
            try:
                cajero = User.objects.get(username='cajero')
                self.stdout.write('Usuario cajero ya existe')
            except User.DoesNotExist:
                cajero = User.objects.create_user(
                    username='cajero',
                    email='cajero@lgservice.com',
                    password='cajero123',
                    first_name='Carlos',
                    last_name='Cajero'
                )
                cajero.is_staff = True
                cajero.save()
                cajero.groups.add(cajero_group)
                self.stdout.write(self.style.SUCCESS('Usuario cajero creado: cajero / cajero123'))

            # 3. Usuario Padre 1
            try:
                padre1 = User.objects.get(username='padre1')
                self.stdout.write('Usuario padre1 ya existe')
            except User.DoesNotExist:
                padre1 = User.objects.create_user(
                    username='padre1',
                    email='padre1@example.com',
                    password='padre123',
                    first_name='Juan',
                    last_name='García'
                )
                padre1.save()
                padre1.groups.add(padre_group)
                self.stdout.write(self.style.SUCCESS('Usuario padre creado: padre1 / padre123'))

            # 4. Usuario Padre 2
            try:
                padre2 = User.objects.get(username='padre2')
                self.stdout.write('Usuario padre2 ya existe')
            except User.DoesNotExist:
                padre2 = User.objects.create_user(
                    username='padre2',
                    email='padre2@example.com',
                    password='padre123',
                    first_name='María',
                    last_name='López'
                )
                padre2.save()
                padre2.groups.add(padre_group)
                self.stdout.write(self.style.SUCCESS('Usuario padre creado: padre2 / padre123'))

        self.stdout.write(self.style.SUCCESS('=== Usuarios creados con éxito ==='))
        self.stdout.write('Credenciales para acceder:')
        self.stdout.write('1. Admin: usuario=admin, contraseña=admin123')
        self.stdout.write('2. Cajero: usuario=cajero, contraseña=cajero123')
        self.stdout.write('3. Padre: usuario=padre1, contraseña=padre123')
        self.stdout.write('4. Padre: usuario=padre2, contraseña=padre123')