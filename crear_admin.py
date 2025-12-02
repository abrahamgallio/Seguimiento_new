"""
Script para crear el usuario administrador en MediTrack
Coloca este archivo al lado de manage.py y ejecútalo con: python crear_admin.py
"""

import os
import sys
import django

# Obtener el directorio actual
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appweb.settings')

try:
    django.setup()
except Exception as e:
    print(f"❌ Error al configurar Django: {e}")
    print("⚠️  Asegúrate de cambiar 'basedb.settings' por el nombre correcto de tu proyecto")
    sys.exit(1)

from django.contrib.auth.hashers import make_password
from appweb.models import Usuario
from django.utils import timezone

def crear_administrador():
    """
    Crea el usuario administrador principal del sistema
    """
    email = 'admin@meditrack.com'
    password = 'Admin123'
    
    print("=" * 60)
    print("CREANDO USUARIO ADMINISTRADOR - MEDITRACK")
    print("=" * 60)
    
    try:
        # Verificar si ya existe
        if Usuario.objects.filter(email=email).exists():
            print(f"\n⚠️  El usuario {email} ya existe en la base de datos")
            admin = Usuario.objects.get(email=email)
            print(f"\n📋 Datos del administrador existente:")
            print(f"   ID:       {admin.id_usuario}")
            print(f"   Nombre:   {admin.nombre} {admin.apellido}")
            print(f"   Email:    {admin.email}")
            print(f"   Tipo:     {admin.tipo_usuario}")
            print(f"   Activo:   {'Sí' if admin.activo else 'No'}")
            print(f"\n💡 Si olvidaste la contraseña, elimina este usuario desde MySQL y vuelve a ejecutar este script")
            return
        
        # Crear nuevo administrador
        admin = Usuario.objects.create(
            email=email,
            password_hash=make_password(password),
            nombre='Administrador',
            apellido='Sistema',
            telefono='+56912345678',
            fecha_nacimiento='1990-01-01',
            tipo_usuario='admin',
            activo=True,
            fecha_registro=timezone.now(),
            ultima_conexion=timezone.now()
        )
        
        print("\n✅ ¡ADMINISTRADOR CREADO EXITOSAMENTE!")
        print("=" * 60)
        print(f"\n📋 CREDENCIALES DE ACCESO:")
        print(f"   📧 Email:      {email}")
        print(f"   🔑 Contraseña: {password}")
        print(f"   🆔 ID Usuario: {admin.id_usuario}")
        print(f"   👤 Nombre:     {admin.nombre} {admin.apellido}")
        print(f"   📱 Teléfono:   {admin.telefono}")
        print(f"   ✅ Estado:     {'Activo' if admin.activo else 'Inactivo'}")
        
        print("\n" + "=" * 60)
        print("📝 PRÓXIMOS PASOS:")
        print("=" * 60)
        print("1. Inicia el servidor: python manage.py runserver")
        print("2. Ve a: http://localhost:8000/login/")
        print("3. Ingresa con las credenciales mostradas arriba")
        print("\n⚠️  IMPORTANTE: Cambia la contraseña después del primer login")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR AL CREAR ADMINISTRADOR:")
        print(f"   {str(e)}")
        print("\n💡 POSIBLES SOLUCIONES:")
        print("   1. Verifica que la base de datos esté corriendo")
        print("   2. Verifica las migraciones: python manage.py migrate")
        print("   3. Verifica la conexión en settings.py")
        sys.exit(1)

if __name__ == "__main__":

    crear_administrador()
