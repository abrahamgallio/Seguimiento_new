import os
import sys
import django

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Cargar settings correctos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appweb.settings')

django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def crear_admin():
    email = "admin@meditrack.com"
    password = "Admin123"

    print("=== Creación automática del superadministrador ===")

    if User.objects.filter(email=email).exists():
        print("⚠️  El usuario administrador ya existe.")
        return

    admin = User.objects.create(
        email=email,
        nombre="Administrador",
        apellido="Sistema",
        activo=True
    )
    admin.set_password(password)
    admin.tipo_usuario = "admin"
    admin.save()

    print("✅ Administrador creado:")
    print(f"Email: {email}")
    print(f"Password: {password}")

if __name__ == "__main__":
    crear_admin()