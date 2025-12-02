from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password
from django.utils import timezone
import os


@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    """
    Crea un usuario administrador por defecto después de las migraciones.
    Se ejecuta solo si no existe ya un usuario admin.
    """

    # Asegura que solo se ejecute en la app correcta
    if sender.name != "appweb":
        return

    # Importación dentro del signal para evitar errores en migraciones
    from .models import Usuario

    # Evitar que se cree si ya hay un admin
    if Usuario.objects.filter(tipo_usuario='admin').exists():
        print("✔ Ya existe un usuario administrador. No se creará otro.")
        return

    print("⚙️ Creando usuario administrador por defecto...")

    # Variables de entorno o valores por defecto
    admin_email = os.getenv("ADMIN_EMAIL", "admin@system.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "Admin1234!")
    admin_nombre = os.getenv("ADMIN_NOMBRE", "Admin")
    admin_apellido = os.getenv("ADMIN_APELLIDO", "Sistema")

    # Crear el usuario admin
    Usuario.objects.create(
        email=admin_email,
        password_hash=make_password(admin_password),
        nombre=admin_nombre,
        apellido=admin_apellido,
        telefono="000000000",
        fecha_nacimiento="2000-01-01",
        tipo_usuario="admin",
        fecha_registro=timezone.now(),
        ultima_conexion=timezone.now(),
        activo=True
    )

    print("✅ Administrador creado exitosamente")
    print(f"📧 Email: {admin_email}")
    print(f"🔑 Password: {admin_password}")


