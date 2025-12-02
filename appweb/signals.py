from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password
from django.utils import timezone
import os

@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    # Ejecutar solo cuando migra la app 'appweb'
    if sender.name != "appweb":
        return

    from .models import Usuario

    # Evitar duplicados
    if Usuario.objects.filter(tipo_usuario='admin').exists():
        return

    print("⚙️  Creando usuario administrador por defecto...")

    admin_email = os.getenv('ADMIN_EMAIL', 'admin@meditrack.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'Admin1234!')
    admin_nombre = os.getenv('ADMIN_NOMBRE', 'Admin')
    admin_apellido = os.getenv('ADMIN_APELLIDO', 'Sistema')
    admin_telefono = os.getenv('ADMIN_TELEFONO', '00000000')

    Usuario.objects.create(
        email=admin_email,
        password_hash=make_password(admin_password),
        nombre=admin_nombre,
        apellido=admin_apellido,
        telefono=admin_telefono,
        fecha_nacimiento="2000-01-01",
        tipo_usuario='admin',
        fecha_registro=timezone.now(),
        ultima_conexion=timezone.now(),
        activo=True
    )

    print("✅ Administrador creado automáticamente")
    print(f"📧 Email: {admin_email}")
    print(f"🔑 Password: {admin_password}")





