from rest_framework import serializers
from .models import (
    Usuario, Paciente, Medico, Medicamento, 
    Tratamiento, TratamientoMedicamento,
    HistorialAdherencia, Notificacion, PacienteCuidador
)

class UsuarioSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Usuario"""
    class Meta:
        model = Usuario
        fields = [
            'id_usuario', 'email', 'nombre', 'apellido', 
            'telefono', 'fecha_nacimiento', 'tipo_usuario',
            'fecha_registro', 'ultima_conexion', 'activo'
        ]
        read_only_fields = ['id_usuario', 'fecha_registro', 'ultima_conexion']
        extra_kwargs = {
            'password_hash': {'write_only': True}
        }

class PacienteSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Paciente"""
    usuario = UsuarioSerializer(source='id_usuario', read_only=True)
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Paciente
        fields = [
            'id_paciente', 'id_usuario', 'usuario', 'numero_identificacion',
            'genero', 'grupo_sanguineo', 'alergias', 'enfermedades_cronicas',
            'direccion', 'contacto_emergencia', 'telefono_emergencia',
            'nombre_completo'
        ]
        read_only_fields = ['id_paciente']
    
    def get_nombre_completo(self, obj):
        return f"{obj.id_usuario.nombre} {obj.id_usuario.apellido}"

class MedicoSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Medico"""
    usuario = UsuarioSerializer(source='id_usuario', read_only=True)
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Medico
        fields = [
            'id_medico', 'id_usuario', 'usuario', 'especialidad',
            'numero_colegiado', 'institucion', 'anos_experiencia',
            'consultorio', 'certificaciones', 'nombre_completo'
        ]
        read_only_fields = ['id_medico']
    
    def get_nombre_completo(self, obj):
        return f"Dr. {obj.id_usuario.nombre} {obj.id_usuario.apellido}"

class MedicamentoSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Medicamento"""
    class Meta:
        model = Medicamento
        fields = [
            'id_medicamento', 'nombre_comercial', 'nombre_generico',
            'laboratorio', 'presentacion', 'concentracion',
            'via_administracion', 'requiere_receta', 'efectos_secundarios',
            'contraindicaciones', 'codigo_barra'
        ]
        read_only_fields = ['id_medicamento']

class TratamientoSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Tratamiento"""
    paciente = PacienteSerializer(source='id_paciente', read_only=True)
    medico = MedicoSerializer(source='id_medico', read_only=True)
    
    class Meta:
        model = Tratamiento
        fields = [
            'id_tratamiento', 'id_paciente', 'id_medico', 'paciente', 'medico',
            'diagnostico', 'fecha_inicio', 'fecha_fin', 'duracion_dias',
            'tipo_tratamiento', 'objetivo_terapeutico', 'estado',
            'observaciones', 'fecha_creacion'
        ]
        read_only_fields = ['id_tratamiento', 'fecha_creacion']

class TratamientoMedicamentoSerializer(serializers.ModelSerializer):
    """Serializador para el modelo TratamientoMedicamento"""
    tratamiento = TratamientoSerializer(source='id_tratamiento', read_only=True)
    medicamento = MedicamentoSerializer(source='id_medicamento', read_only=True)
    
    class Meta:
        model = TratamientoMedicamento
        fields = [
            'id_tratamiento_medicamento', 'id_tratamiento', 'id_medicamento',
            'tratamiento', 'medicamento', 'dosis', 'frecuencia',
            'via_administracion', 'duracion_dias', 'horarios',
            'instrucciones_especiales', 'activo'
        ]
        read_only_fields = ['id_tratamiento_medicamento']

class NotificacionSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Notificacion unificado"""
    usuario_origen = UsuarioSerializer(source='id_usuario_origen', read_only=True)
    usuario_destino = UsuarioSerializer(source='id_usuario_destino', read_only=True)
    tratamiento_medicamento = TratamientoMedicamentoSerializer(source='id_tratamiento_medicamento', read_only=True)
    tipo_notificacion_display = serializers.CharField(source='get_tipo_notificacion_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Notificacion
        fields = [
            'id_notificacion', 'id_usuario_origen', 'id_usuario_destino', 
            'id_tratamiento_medicamento', 'usuario_origen', 'usuario_destino',
            'tratamiento_medicamento', 'tipo_notificacion', 'tipo_notificacion_display',
            'titulo', 'mensaje', 'prioridad', 'estado', 'estado_display',
            'canal_envio', 'fecha_hora_programada', 'anticipacion_minutos',
            'repetir', 'notificar_cuidador', 'requiere_confirmacion',
            'fecha_creacion', 'fecha_envio', 'fecha_lectura', 'enlace',
            'datos_adicionales'
        ]
        read_only_fields = ['id_notificacion', 'fecha_creacion', 'fecha_envio', 'fecha_lectura']

class HistorialAdherenciaSerializer(serializers.ModelSerializer):
    """Serializador para el modelo HistorialAdherencia"""
    paciente = PacienteSerializer(source='id_paciente', read_only=True)
    tratamiento = TratamientoSerializer(source='id_tratamiento', read_only=True)
    
    class Meta:
        model = HistorialAdherencia
        fields = '__all__'
        read_only_fields = ['id_historial']

class PacienteCuidadorSerializer(serializers.ModelSerializer):
    """Serializador para el modelo PacienteCuidador"""
    class Meta:
        model = PacienteCuidador
        fields = '__all__'
        read_only_fields = ['id_cuidador']

# Serializadores para creación combinada

class CrearMedicoSerializer(serializers.Serializer):
    """Serializador para crear médico con usuario"""
    # Datos del usuario
    email = serializers.EmailField()
    nombre = serializers.CharField(max_length=100)
    apellido = serializers.CharField(max_length=100)
    telefono = serializers.CharField(max_length=20)
    fecha_nacimiento = serializers.DateField()
    
    # Datos del médico
    especialidad = serializers.CharField(max_length=100, required=False)
    numero_colegiado = serializers.CharField(max_length=50)
    institucion = serializers.CharField(max_length=100)
    anos_experiencia = serializers.IntegerField()
    consultorio = serializers.CharField(max_length=100)
    certificaciones = serializers.CharField()
    
    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado.")
        return value
    
    def validate_anos_experiencia(self, value):
        if value < 0:
            raise serializers.ValidationError("Los años de experiencia no pueden ser negativos.")
        if value > 80:
            raise serializers.ValidationError("Por favor, ingrese un número realista de años de experiencia.")
        return value

class CrearPacienteSerializer(serializers.Serializer):
    """Serializador para crear paciente con usuario"""
    # Datos del usuario
    email = serializers.EmailField()
    nombre = serializers.CharField(max_length=100)
    apellido = serializers.CharField(max_length=100)
    telefono = serializers.CharField(max_length=20)
    fecha_nacimiento = serializers.DateField()
    
    # Datos del paciente
    numero_identificacion = serializers.CharField(max_length=50, required=False, allow_blank=True)
    genero = serializers.ChoiceField(choices=['M', 'F', 'Otro'], required=False)
    grupo_sanguineo = serializers.CharField(max_length=5)
    alergias = serializers.CharField()
    enfermedades_cronicas = serializers.CharField()
    direccion = serializers.CharField(max_length=255)
    contacto_emergencia = serializers.CharField(max_length=100, required=False, allow_blank=True)
    telefono_emergencia = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado.")
        return value


class MedicamentoRecetaSerializer(serializers.Serializer):
    """Serializador para medicamentos en una receta"""
    id_medicamento = serializers.IntegerField()
    dosis = serializers.CharField(max_length=50)
    frecuencia = serializers.CharField(max_length=50)
    duracion_dias = serializers.IntegerField(min_value=1)
    via_administracion = serializers.CharField(max_length=50)
    instrucciones_especiales = serializers.CharField(required=False, allow_blank=True)
    horarios = serializers.JSONField(required=False, default=list)


class CrearRecetaSerializer(serializers.Serializer):
    """Serializador para crear receta médica (Tratamiento + Medicamentos)"""
    id_medico = serializers.IntegerField()
    id_paciente = serializers.IntegerField()
    diagnostico = serializers.CharField()
    instrucciones = serializers.CharField(required=False, allow_blank=True)
    fecha_emision = serializers.DateField()
    vigencia_dias = serializers.IntegerField(min_value=1, max_value=180, default=30)
    medicamentos = MedicamentoRecetaSerializer(many=True)
    
    def validate_medicamentos(self, value):
        if not value:
            raise serializers.ValidationError("Debe agregar al menos un medicamento.")
        return value
    
    def validate_id_medico(self, value):
        if not Medico.objects.filter(id_medico=value).exists():
            raise serializers.ValidationError("El médico no existe.")
        return value
    
    def validate_id_paciente(self, value):
        if not Paciente.objects.filter(id_paciente=value).exists():
            raise serializers.ValidationError("El paciente no existe.")
        return value