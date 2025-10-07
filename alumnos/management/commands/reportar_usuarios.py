from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Reporte de todos los usuarios del sistema'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        usuarios = User.objects.all()
        self.stdout.write("ID | Username | Email | Activo | Staff")
        self.stdout.write("-" * 50)
        for user in usuarios:
            self.stdout.write(f"{user.id} | {user.username} | {user.email} | {user.is_active} | {user.is_staff}")
