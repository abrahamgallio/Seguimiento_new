from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

class Usuario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('paciente', 'Paciente'),
        ('medico', 'Médico'),
        ('cuidador', 'Cuidador'),
        ('admin', 'Administrador'),
    ]
    
    id_usuario = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    fecha_nacimiento = models.DateField()
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES)
    fecha_registro = models.DateTimeField(default=timezone.now)
    ultima_conexion = models.DateTimeField(default=timezone.now)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'USUARIOS'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.email})"


class Paciente(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('Otro', 'Otro'),
    ]
    
    id_paciente = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    numero_identificacion = models.CharField(max_length=50, null=True, blank=True)
    genero = models.CharField(max_length=4, choices=GENERO_CHOICES, null=True, blank=True)
    grupo_sanguineo = models.CharField(max_length=5)
    alergias = models.TextField()
    enfermedades_cronicas = models.TextField()
    direccion = models.CharField(max_length=255)
    contacto_emergencia = models.CharField(max_length=100, null=True, blank=True)
    telefono_emergencia = models.CharField(max_length=20, null=True, blank=True)
    
    class Meta:
        db_table = 'PACIENTES'
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
    
    def __str__(self):
        return f"Paciente: {self.id_usuario.nombre} {self.id_usuario.apellido}"


class Medico(models.Model):
    id_medico = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    especialidad = models.CharField(max_length=100, null=True, blank=True)
    numero_colegiado = models.CharField(max_length=50)
    institucion = models.CharField(max_length=100)
    anos_experiencia = models.IntegerField()
    consultorio = models.CharField(max_length=100)
    certificaciones = models.TextField()
    
    class Meta:
        db_table = 'MEDICOS'
        verbose_name = 'Médico'
        verbose_name_plural = 'Médicos'
    
    def __str__(self):
        return f"Dr. {self.id_usuario.nombre} {self.id_usuario.apellido} - {self.especialidad}"


class Medicamento(models.Model):
    id_medicamento = models.AutoField(primary_key=True)
    nombre_comercial = models.CharField(max_length=100)
    nombre_generico = models.CharField(max_length=100)
    laboratorio = models.CharField(max_length=100)
    presentacion = models.CharField(max_length=50, null=True, blank=True)
    concentracion = models.CharField(max_length=50)
    via_administracion = models.CharField(max_length=50)
    requiere_receta = models.BooleanField(default=True)
    efectos_secundarios = models.TextField()
    contraindicaciones = models.TextField()
    codigo_barra = models.CharField(max_length=50, unique=True)
    
    class Meta:
        db_table = 'MEDICAMENTOS'
        verbose_name = 'Medicamento'
        verbose_name_plural = 'Medicamentos'
    
    def __str__(self):
        return f"{self.nombre_comercial} ({self.nombre_generico})"


class Tratamiento(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('finalizado', 'Finalizado'),
        ('suspendido', 'Suspendido'),
    ]
    
    id_tratamiento = models.AutoField(primary_key=True)
    id_paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, db_column='id_paciente')
    id_medico = models.ForeignKey(Medico, on_delete=models.CASCADE, db_column='id_medico')
    diagnostico = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    duracion_dias = models.IntegerField()
    tipo_tratamiento = models.CharField(max_length=100)
    objetivo_terapeutico = models.TextField()
    estado = models.CharField(max_length=11, choices=ESTADO_CHOICES)
    observaciones = models.TextField()
    fecha_creacion = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'TRATAMIENTOS'
        verbose_name = 'Tratamiento'
        verbose_name_plural = 'Tratamientos'
    
    def __str__(self):
        return f"Tratamiento #{self.id_tratamiento} - {self.id_paciente}"


class TratamientoMedicamento(models.Model):
    id_tratamiento_medicamento = models.AutoField(primary_key=True)
    id_tratamiento = models.ForeignKey(Tratamiento, on_delete=models.CASCADE, db_column='id_tratamiento')
    id_medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE, db_column='id_medicamento')
    dosis = models.CharField(max_length=50)
    frecuencia = models.CharField(max_length=50)
    via_administracion = models.CharField(max_length=50)
    duracion_dias = models.IntegerField()
    horarios = models.JSONField()  # Django 3.1+ soporta JSONField nativamente
    instrucciones_especiales = models.TextField()
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'TRATAMIENTO_MEDICAMENTOS'
        verbose_name = 'Tratamiento-Medicamento'
        verbose_name_plural = 'Tratamientos-Medicamentos'
    
    def __str__(self):
        return f"{self.id_tratamiento} - {self.id_medicamento}"


class Notificacion(models.Model):
    """
    Modelo unificado para todas las notificaciones del sistema.
    Incluye recordatorios de medicamentos, alertas, mensajes del sistema, etc.
    """
    TIPO_NOTIFICACION_CHOICES = [
        ('recordatorio_medicamento', 'Recordatorio de Medicamento'),  # Nueva opción
        ('alerta_medica', 'Alerta Médica'),
        ('mensaje_medico', 'Mensaje del Médico'),
        ('mensaje_sistema', 'Mensaje del Sistema'),
        ('adherencia_baja', 'Alerta de Adherencia Baja'),
        ('cambio_tratamiento', 'Cambio en Tratamiento'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('enviada', 'Enviada'),
        ('leida', 'Leída'),
        ('fallida', 'Fallida'),
    ]
    
    CANAL_ENVIO_CHOICES = [
        ('app', 'Aplicación'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Notificación Push'),
    ]
    
    # Identificadores
    id_notificacion = models.AutoField(primary_key=True)
    
    # Usuarios
    id_usuario_origen = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='notificaciones_enviadas',
        db_column='id_usuario_origen',
        null=True,
        blank=True,
        help_text='Usuario que genera la notificación (puede ser null para notificaciones del sistema)'
    )
    id_usuario_destino = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='notificaciones_recibidas',
        db_column='id_usuario_destino',
        help_text='Usuario que recibe la notificación'
    )
    
    # Relación con tratamiento (para recordatorios de medicamentos)
    id_tratamiento_medicamento = models.ForeignKey(
        TratamientoMedicamento,
        on_delete=models.CASCADE,
        db_column='id_tratamiento_medicamento',
        null=True,
        blank=True,
        help_text='Relación con medicamento (solo para recordatorios de medicamentos)'
    )
    
    # Contenido de la notificación
    tipo_notificacion = models.CharField(max_length=30, choices=TIPO_NOTIFICACION_CHOICES)
    titulo = models.CharField(max_length=150)
    mensaje = models.TextField()
    prioridad = models.CharField(max_length=5, choices=PRIORIDAD_CHOICES, default='media')
    
    # Estado y seguimiento
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    canal_envio = models.CharField(
        max_length=10, 
        choices=CANAL_ENVIO_CHOICES, 
        default='app',
        help_text='Canal por el cual se enviará la notificación'
    )
    
    # Configuración para recordatorios
    fecha_hora_programada = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='Fecha y hora en que debe enviarse la notificación'
    )
    anticipacion_minutos = models.IntegerField(
        null=True, 
        blank=True,
        help_text='Minutos de anticipación para recordatorios'
    )
    repetir = models.BooleanField(
        default=False,
        help_text='Si el recordatorio debe repetirse'
    )
    
    # Configuración adicional
    notificar_cuidador = models.BooleanField(
        default=False,
        help_text='Si debe notificarse también al cuidador'
    )
    requiere_confirmacion = models.BooleanField(
        default=False,
        help_text='Si requiere confirmación de lectura/acción'
    )
    
    # Fechas de seguimiento
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    
    # Extras
    enlace = models.CharField(
        max_length=255, 
        blank=True,
        help_text='URL de acción relacionada'
    )
    datos_adicionales = models.JSONField(
        null=True,
        blank=True,
        help_text='Datos adicionales en formato JSON'
    )
    
    class Meta:
        db_table = 'NOTIFICACIONES'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['id_usuario_destino', 'estado']),
            models.Index(fields=['fecha_hora_programada', 'estado']),
            models.Index(fields=['tipo_notificacion']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_notificacion_display()} - {self.titulo} (Para: {self.id_usuario_destino})"
    
    def marcar_como_enviada(self):
        """Marca la notificación como enviada"""
        self.estado = 'enviada'
        self.fecha_envio = timezone.now()
        self.save()
    
    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        self.estado = 'leida'
        self.fecha_lectura = timezone.now()
        self.save()


class HistorialAdherencia(models.Model):
    CLASIFICACION_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]
    
    id_historial = models.AutoField(primary_key=True)
    id_paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, db_column='id_paciente')
    id_tratamiento = models.ForeignKey(Tratamiento, on_delete=models.CASCADE, db_column='id_tratamiento')
    fecha_inicio_periodo = models.DateField(null=True, blank=True)
    fecha_fin_periodo = models.DateField(null=True, blank=True)
    tomas_programadas = models.IntegerField(null=True, blank=True)
    tomas_realizadas = models.IntegerField(null=True, blank=True)
    tomas_omitidas = models.IntegerField(null=True, blank=True)
    tomas_tardias = models.IntegerField(null=True, blank=True)
    porcentaje_adherencia = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    clasificacion_adherencia = models.CharField(
        max_length=5, 
        choices=CLASIFICACION_CHOICES, 
        null=True, 
        blank=True
    )
    fecha_calculo = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'HISTORIAL_ADHERENCIA'
        verbose_name = 'Historial de Adherencia'
        verbose_name_plural = 'Historiales de Adherencia'
    
    def __str__(self):
        return f"Adherencia - {self.id_paciente} - {self.porcentaje_adherencia}%"


class PacienteCuidador(models.Model):
    ESTADO_RELACION_CHOICES = [
        ('activa', 'Activa'),
        ('inactiva', 'Inactiva'),
        ('suspendida', 'Suspendida'),
    ]
    
    NIVEL_ACCESO_CHOICES = [
        ('completo', 'Completo'),
        ('limitado', 'Limitado'),
    ]
    
    id_cuidador = models.AutoField(primary_key=True)
    id_paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, db_column='id_paciente')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    fecha_asignacion = models.DateField()
    estado_relacion = models.CharField(max_length=10, choices=ESTADO_RELACION_CHOICES)
    nivel_acceso = models.CharField(max_length=8, choices=NIVEL_ACCESO_CHOICES)
    recibir_notificaciones = models.BooleanField(default=True)
    puede_registrar_tomas = models.BooleanField(default=True)
    parentesco = models.CharField(max_length=50)
    certificacion_cuidador = models.BooleanField(default=False)
    disponibilidad = models.CharField(max_length=100)
    notas = models.TextField(blank=True)
    
    class Meta:
        db_table = 'PACIENTE_CUIDADOR'
        verbose_name = 'Paciente-Cuidador'
        verbose_name_plural = 'Pacientes-Cuidadores'
    
    def __str__(self):
        return f"Cuidador de {self.id_paciente} - {self.id_usuario}"