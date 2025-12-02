from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password
from django.utils import timezone
import os


@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    """
    Crea un usuario admin por defecto después de las migraciones
    Solo se ejecuta si no existe ningún usuario admin
    """
    # Evita importar antes de que las tablas estén creadas
    from .models import Usuario
    
    # Solo crear si no existe ningún admin
    if Usuario.objects.filter(tipo_usuario='admin', activo=True).exists():
        return
    
    print("⚙️  Creando usuario administrador por defecto...")

    # Usar variables de entorno o valores por defecto
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'Admin1234!')
    admin_nombre = os.getenv('ADMIN_NOMBRE', 'Admin')
    admin_apellido = os.getenv('ADMIN_APELLIDO', 'Sistema')

    # Crear el usuario admin
    Usuario.objects.create(
        email=admin_email,
        password_hash=make_password(admin_password),  # ← Usa Argon2 automáticamente
        nombre=admin_nombre,
        apellido=admin_apellido,
        telefono='000000000',
        fecha_nacimiento='2000-01-01',
        tipo_usuario='admin',
        fecha_registro=timezone.now(),
        ultima_conexion=timezone.now(),
        activo=True
    )

    print(f"✅ Administrador creado exitosamente")
    print(f"📧 Email: {admin_email}")
    print(f"🔑 Contraseña: {admin_password}")
    print("⚠️  CAMBIA LA CONTRASEÑA INMEDIATAMENTE DESPUÉS DEL PRIMER LOGIN")