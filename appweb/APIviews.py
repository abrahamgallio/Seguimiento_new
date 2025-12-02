from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q
import requests
from rest_framework.decorators import api_view
from deep_translator import GoogleTranslator
from .models import (
    Usuario, Paciente, Medico, Medicamento,
    Tratamiento, TratamientoMedicamento,
    HistorialAdherencia, Notificacion, PacienteCuidador
)
from .serializers import (
    UsuarioSerializer, PacienteSerializer, MedicoSerializer,
    MedicamentoSerializer, TratamientoSerializer,
    TratamientoMedicamentoSerializer,
    HistorialAdherenciaSerializer, NotificacionSerializer,
    PacienteCuidadorSerializer, CrearMedicoSerializer, CrearPacienteSerializer,
    CrearRecetaSerializer
)


# ==================== AUTENTICACIÓN ====================

class LoginAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email y contraseña son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            usuario = Usuario.objects.get(email=email)

            if check_password(password, usuario.password_hash):
                usuario.ultima_conexion = timezone.now()
                usuario.save()

                serializer = UsuarioSerializer(usuario)
                
                # Obtener datos adicionales según el tipo de usuario
                datos_adicionales = {}
                if usuario.tipo_usuario == 'medico':
                    try:
                        medico = Medico.objects.get(id_usuario=usuario)
                        medico_serializer = MedicoSerializer(medico)
                        datos_adicionales = medico_serializer.data
                    except Medico.DoesNotExist:
                        pass
                elif usuario.tipo_usuario == 'paciente':
                    try:
                        paciente = Paciente.objects.get(id_usuario=usuario)
                        paciente_serializer = PacienteSerializer(paciente)
                        datos_adicionales = paciente_serializer.data
                    except Paciente.DoesNotExist:
                        pass
                
                return Response(
                    {
                        'mensaje': f'Bienvenido {usuario.nombre} {usuario.apellido}',
                        'usuario': serializer.data,
                        'datos_adicionales': datos_adicionales,
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response({'error': 'Contraseña incorrecta'}, status=status.HTTP_401_UNAUTHORIZED)

        except Usuario.DoesNotExist:
            return Response({'error': 'No existe un usuario con ese correo'}, status=status.HTTP_404_NOT_FOUND)


class LogoutAPIView(APIView):
    def post(self, request):
        usuario_id = request.data.get('usuario_id')

        if not usuario_id:
            return Response({'error': 'usuario_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            usuario = Usuario.objects.get(id_usuario=usuario_id)
            return Response({'mensaje': f'Sesión cerrada para {usuario.nombre}'}, status=status.HTTP_200_OK)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)


class VerificarSesionAPIView(APIView):
    def post(self, request):
        usuario_id = request.data.get('usuario_id')

        if not usuario_id:
            return Response({'error': 'usuario_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            usuario = Usuario.objects.get(id_usuario=usuario_id)

            if usuario.activo:
                serializer = UsuarioSerializer(usuario)
                return Response({'mensaje': 'Sesión válida', 'usuario': serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Usuario inactivo'}, status=status.HTTP_401_UNAUTHORIZED)

        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)


class RegistroUsuarioAPIView(APIView):
    def post(self, request):
        data = request.data

        usuario = Usuario.objects.create(
            email=data['email'],
            password_hash=make_password(data['password']),
            nombre=data['nombre'],
            apellido=data['apellido'],
            telefono=data['telefono'],
            fecha_nacimiento=data['fecha_nacimiento'],
            tipo_usuario=data.get('tipo_usuario', 'paciente'),
            fecha_registro=timezone.now(),
            ultima_conexion=timezone.now(),
            activo=True
        )
        return Response({'mensaje': 'Usuario registrado correctamente'}, status=status.HTTP_201_CREATED)


class CambiarPasswordAPIView(APIView):
    def post(self, request):
        usuario_id = request.data.get('usuario_id')
        password_actual = request.data.get('password_actual')
        password_nueva = request.data.get('password_nueva')

        try:
            usuario = Usuario.objects.get(id_usuario=usuario_id)

            if check_password(password_actual, usuario.password_hash):
                usuario.password_hash = make_password(password_nueva)
                usuario.save()
                return Response({'mensaje': 'Contraseña cambiada exitosamente'}, status=status.HTTP_200_OK)

            return Response({'error': 'Contraseña actual incorrecta'}, status=status.HTTP_401_UNAUTHORIZED)

        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)


# ==================== CREAR PACIENTE / MÉDICO ====================

class CrearPacienteAPIView(APIView):
    def get(self, request):
        """GET - Retorna instrucciones o info de la API"""
        return Response({
            'mensaje': 'Para crear un paciente, use POST',
            'metodo': 'POST',
            'endpoint': '/api/paciente/crear/',
            'campos_requeridos': [
                'email', 'nombre', 'apellido', 'telefono', 'fecha_nacimiento',
                'numero_identificacion', 'genero', 'grupo_sanguineo', 'alergias',
                'enfermedades_cronicas', 'direccion', 'contacto_emergencia', 'telefono_emergencia'
            ]
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = CrearPacienteSerializer(data=request.data)
        if serializer.is_valid():
            usuario = Usuario.objects.create(
                email=serializer.validated_data['email'],
                nombre=serializer.validated_data['nombre'],
                apellido=serializer.validated_data['apellido'],
                telefono=serializer.validated_data['telefono'],
                fecha_nacimiento=serializer.validated_data['fecha_nacimiento'],
                tipo_usuario='paciente',
                password_hash=make_password('123456'),
                activo=True,
                fecha_registro=timezone.now(),
                ultima_conexion=timezone.now()
            )
            paciente = Paciente.objects.create(
                id_usuario=usuario,
                numero_identificacion=serializer.validated_data.get('numero_identificacion', ''),
                genero=serializer.validated_data.get('genero', ''),
                grupo_sanguineo=serializer.validated_data['grupo_sanguineo'],
                alergias=serializer.validated_data['alergias'],
                enfermedades_cronicas=serializer.validated_data['enfermedades_cronicas'],
                direccion=serializer.validated_data['direccion'],
                contacto_emergencia=serializer.validated_data.get('contacto_emergencia', ''),
                telefono_emergencia=serializer.validated_data.get('telefono_emergencia', '')
            )
            response_serializer = PacienteSerializer(paciente)
            return Response({'mensaje': f'Paciente {usuario.nombre} {usuario.apellido} creado exitosamente', 'data': response_serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CrearMedicoAPIView(APIView):
    def get(self, request):
        """GET - Retorna instrucciones o info de la API"""
        return Response({
            'mensaje': 'Para crear un médico, use POST',
            'metodo': 'POST',
            'endpoint': '/api/medico/crear/',
            'campos_requeridos': [
                'email', 'nombre', 'apellido', 'telefono', 'fecha_nacimiento',
                'especialidad', 'numero_colegiado', 'institucion', 
                'anos_experiencia', 'consultorio', 'certificaciones'
            ]
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = CrearMedicoSerializer(data=request.data)
        if serializer.is_valid():
            usuario = Usuario.objects.create(
                email=serializer.validated_data['email'],
                nombre=serializer.validated_data['nombre'],
                apellido=serializer.validated_data['apellido'],
                telefono=serializer.validated_data['telefono'],
                fecha_nacimiento=serializer.validated_data['fecha_nacimiento'],
                tipo_usuario='medico',
                password_hash=make_password('123456'),
                activo=True,
                fecha_registro=timezone.now(),
                ultima_conexion=timezone.now()
            )
            medico = Medico.objects.create(
                id_usuario=usuario,
                especialidad=serializer.validated_data.get('especialidad', ''),
                numero_colegiado=serializer.validated_data['numero_colegiado'],
                institucion=serializer.validated_data['institucion'],
                anos_experiencia=serializer.validated_data['anos_experiencia'],
                consultorio=serializer.validated_data['consultorio'],
                certificaciones=serializer.validated_data['certificaciones']
            )
            response_serializer = MedicoSerializer(medico)
            return Response({'mensaje': f'Médico {usuario.nombre} {usuario.apellido} creado exitosamente', 'data': response_serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ========== VIEWSETS ==========

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        usuarios_activos = Usuario.objects.filter(activo=True)
        serializer = self.get_serializer(usuarios_activos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        tipo = request.query_params.get('tipo', None)
        if tipo:
            usuarios = Usuario.objects.filter(tipo_usuario=tipo)
            serializer = self.get_serializer(usuarios, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe proporcionar el parámetro 'tipo'"}, status=status.HTTP_400_BAD_REQUEST)


class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.select_related('id_usuario').all()
    serializer_class = MedicoSerializer
    
    @action(detail=False, methods=['get'])
    def por_especialidad(self, request):
        especialidad = request.query_params.get('especialidad', None)
        if especialidad:
            medicos = Medico.objects.filter(especialidad__icontains=especialidad)
            serializer = self.get_serializer(medicos, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe proporcionar el parámetro 'especialidad'"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def pacientes(self, request, pk=None):
        medico = self.get_object()
        tratamientos = Tratamiento.objects.filter(id_medico=medico).select_related('id_paciente')
        pacientes = [t.id_paciente for t in tratamientos]
        serializer = PacienteSerializer(pacientes, many=True)
        return Response(serializer.data)


class PacienteViewSet(viewsets.ModelViewSet):
    # Asegurar que solo se devuelvan pacientes cuyo usuario tenga tipo 'paciente'
    queryset = Paciente.objects.select_related('id_usuario').filter(id_usuario__tipo_usuario='paciente')
    serializer_class = PacienteSerializer
    
    @action(detail=True, methods=['get'])
    def tratamientos(self, request, pk=None):
        paciente = self.get_object()
        tratamientos = Tratamiento.objects.filter(id_paciente=paciente)
        serializer = TratamientoSerializer(tratamientos, many=True)
        return Response(serializer.data)


class MedicamentoViewSet(viewsets.ModelViewSet):
    queryset = Medicamento.objects.all()
    serializer_class = MedicamentoSerializer
    
    @action(detail=False, methods=['get'])
    def buscar(self, request):
        query = request.query_params.get('q', None)
        if query:
            medicamentos = Medicamento.objects.filter(nombre_comercial__icontains=query) | Medicamento.objects.filter(nombre_generico__icontains=query)
            serializer = self.get_serializer(medicamentos, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe proporcionar el parámetro 'q' para buscar"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def por_laboratorio(self, request):
        laboratorio = request.query_params.get('laboratorio', None)
        if laboratorio:
            medicamentos = Medicamento.objects.filter(laboratorio__icontains=laboratorio)
            serializer = self.get_serializer(medicamentos, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe proporcionar el parámetro 'laboratorio'"}, status=status.HTTP_400_BAD_REQUEST)


class TratamientoViewSet(viewsets.ModelViewSet):
    queryset = Tratamiento.objects.select_related('id_paciente__id_usuario', 'id_medico__id_usuario').all()
    serializer_class = TratamientoSerializer
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        tratamientos = Tratamiento.objects.filter(estado='activo')
        serializer = self.get_serializer(tratamientos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_paciente(self, request):
        paciente_id = request.query_params.get('paciente_id', None)
        if paciente_id:
            tratamientos = Tratamiento.objects.filter(id_paciente=paciente_id)
            serializer = self.get_serializer(tratamientos, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe proporcionar el parámetro 'paciente_id'"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def por_medico(self, request):
        medico_id = request.query_params.get('medico_id', None)
        if medico_id:
            tratamientos = Tratamiento.objects.filter(id_medico=medico_id)
            serializer = self.get_serializer(tratamientos, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe proporcionar el parámetro 'medico_id'"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        tratamiento = self.get_object()
        tratamiento.estado = 'finalizado'
        tratamiento.save()
        serializer = self.get_serializer(tratamiento)
        return Response({'mensaje': 'Tratamiento finalizado exitosamente', 'data': serializer.data})


class TratamientoMedicamentoViewSet(viewsets.ModelViewSet):
    queryset = TratamientoMedicamento.objects.select_related('id_tratamiento', 'id_medicamento').all()
    serializer_class = TratamientoMedicamentoSerializer
    
    @action(detail=False, methods=['get'])
    def por_tratamiento(self, request):
        tratamiento_id = request.query_params.get('tratamiento_id', None)
        if tratamiento_id:
            tm = TratamientoMedicamento.objects.filter(id_tratamiento=tratamiento_id)
            serializer = self.get_serializer(tm, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe proporcionar el parámetro 'tratamiento_id'"}, status=status.HTTP_400_BAD_REQUEST)


class HistorialAdherenciaViewSet(viewsets.ModelViewSet):
    queryset = HistorialAdherencia.objects.all()
    serializer_class = HistorialAdherenciaSerializer
    
    @action(detail=False, methods=['get'])
    def por_paciente(self, request):
        paciente_id = request.query_params.get('paciente_id', None)
        if paciente_id:
            historiales = HistorialAdherencia.objects.filter(id_paciente=paciente_id)
            serializer = self.get_serializer(historiales, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe proporcionar el parámetro 'paciente_id'"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def adherencia_baja(self, request):
        historiales = HistorialAdherencia.objects.filter(clasificacion_adherencia='baja')
        serializer = self.get_serializer(historiales, many=True)
        return Response(serializer.data)


class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    
    @action(detail=False, methods=['get'])
    def no_leidas(self, request):
        usuario_id = request.query_params.get('usuario_id', None)
        if usuario_id:
            notificaciones = Notificacion.objects.filter(id_usuario_destino=usuario_id, estado__in=['pendiente', 'enviada'])
            serializer = self.get_serializer(notificaciones, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe proporcionar el parámetro 'usuario_id'"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def recordatorios_pendientes(self, request):
        usuario_id = request.query_params.get('usuario_id', None)
        if usuario_id:
            recordatorios = Notificacion.objects.filter(id_usuario_destino=usuario_id, tipo_notificacion='recordatorio_medicamento', estado='pendiente')
            serializer = self.get_serializer(recordatorios, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe proporcionar el parámetro 'usuario_id'"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        notificacion = self.get_object()
        notificacion.marcar_como_leida()
        serializer = self.get_serializer(notificacion)
        return Response({'mensaje': 'Notificación marcada como leída', 'data': serializer.data})
    
    @action(detail=True, methods=['post'])
    def marcar_enviada(self, request, pk=None):
        notificacion = self.get_object()
        notificacion.marcar_como_enviada()
        serializer = self.get_serializer(notificacion)
        return Response({'mensaje': 'Notificación marcada como enviada', 'data': serializer.data})


class PacienteCuidadorViewSet(viewsets.ModelViewSet):
    queryset = PacienteCuidador.objects.all()
    serializer_class = PacienteCuidadorSerializer
    
    @action(detail=False, methods=['get'])
    def por_paciente(self, request):
        paciente_id = request.query_params.get('paciente_id', None)
        if paciente_id:
            relaciones = PacienteCuidador.objects.filter(id_paciente=paciente_id)
            serializer = self.get_serializer(relaciones, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe proporcionar el parámetro 'paciente_id'"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def por_cuidador(self, request):
        usuario_id = request.query_params.get('usuario_id', None)
        if usuario_id:
            relaciones = PacienteCuidador.objects.filter(id_usuario=usuario_id)
            serializer = self.get_serializer(relaciones, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe proporcionar el parámetro 'usuario_id'"}, status=status.HTTP_400_BAD_REQUEST)






class EditarMedicoAPIView(APIView):
    def get_object(self, medico_id):
        return get_object_or_404(Medico, id_medico=medico_id)
    
    def put(self, request, medico_id):
        medico = self.get_object(medico_id)
        usuario = medico.id_usuario
        usuario.email = request.data.get('email', usuario.email)
        usuario.nombre = request.data.get('nombre', usuario.nombre)
        usuario.apellido = request.data.get('apellido', usuario.apellido)
        usuario.telefono = request.data.get('telefono', usuario.telefono)
        usuario.fecha_nacimiento = request.data.get('fecha_nacimiento', usuario.fecha_nacimiento)
        usuario.save()
        medico.especialidad = request.data.get('especialidad', medico.especialidad)
        medico.numero_colegiado = request.data.get('numero_colegiado', medico.numero_colegiado)
        medico.institucion = request.data.get('institucion', medico.institucion)
        medico.anos_experiencia = request.data.get('anos_experiencia', medico.anos_experiencia)
        medico.consultorio = request.data.get('consultorio', medico.consultorio)
        medico.certificaciones = request.data.get('certificaciones', medico.certificaciones)
        medico.save()
        serializer = MedicoSerializer(medico)
        return Response({'mensaje': f'Médico {usuario.nombre} {usuario.apellido} actualizado exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)
    
    def patch(self, request, medico_id):
        return self.put(request, medico_id)


class EliminarMedicoAPIView(APIView):
    def delete(self, request, medico_id):
        medico = get_object_or_404(Medico, id_medico=medico_id)
        usuario = medico.id_usuario
        nombre_completo = f'{usuario.nombre} {usuario.apellido}'
        medico.delete()
        usuario.delete()
        return Response({'mensaje': f'Médico {nombre_completo} eliminado exitosamente'}, status=status.HTTP_200_OK)


class ListarMedicosAPIView(APIView):
    def get(self, request):
        medicos = Medico.objects.select_related('id_usuario').all()
        serializer = MedicoSerializer(medicos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EditarPacienteAPIView(APIView):
    def get_object(self, paciente_id):
        return get_object_or_404(Paciente, id_paciente=paciente_id)
    
    def put(self, request, paciente_id):
        paciente = self.get_object(paciente_id)
        usuario = paciente.id_usuario
        usuario.email = request.data.get('email', usuario.email)
        usuario.nombre = request.data.get('nombre', usuario.nombre)
        usuario.apellido = request.data.get('apellido', usuario.apellido)
        usuario.telefono = request.data.get('telefono', usuario.telefono)
        usuario.fecha_nacimiento = request.data.get('fecha_nacimiento', usuario.fecha_nacimiento)
        usuario.save()
        paciente.numero_identificacion = request.data.get('numero_identificacion', paciente.numero_identificacion)
        paciente.genero = request.data.get('genero', paciente.genero)
        paciente.grupo_sanguineo = request.data.get('grupo_sanguineo', paciente.grupo_sanguineo)
        paciente.alergias = request.data.get('alergias', paciente.alergias)
        paciente.enfermedades_cronicas = request.data.get('enfermedades_cronicas', paciente.enfermedades_cronicas)
        paciente.direccion = request.data.get('direccion', paciente.direccion)
        paciente.contacto_emergencia = request.data.get('contacto_emergencia', paciente.contacto_emergencia)
        paciente.telefono_emergencia = request.data.get('telefono_emergencia', paciente.telefono_emergencia)
        paciente.save()
        serializer = PacienteSerializer(paciente)
        return Response({'mensaje': f'Paciente {usuario.nombre} {usuario.apellido} actualizado exitosamente', 'data': serializer.data}, status=status.HTTP_200_OK)
    
    def patch(self, request, paciente_id):
        return self.put(request, paciente_id)


class EliminarPacienteAPIView(APIView):
    def delete(self, request, paciente_id):
        paciente = get_object_or_404(Paciente, id_paciente=paciente_id)
        usuario = paciente.id_usuario
        nombre_completo = f'{usuario.nombre} {usuario.apellido}'
        paciente.delete()
        usuario.delete()
        return Response({'mensaje': f'Paciente {nombre_completo} eliminado exitosamente'}, status=status.HTTP_200_OK)


class ListarPacientesAPIView(APIView):
    def get(self, request):
        pacientes = Paciente.objects.select_related('id_usuario').filter(id_usuario__tipo_usuario='paciente')
        serializer = PacienteSerializer(pacientes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class BuscarPacientesAPIView(APIView):
    """Buscar pacientes por nombre, apellido o número de identificación.
    Si no se pasa `q`, devuelve todos los pacientes (comportamiento similar a listar).
    """
    def get(self, request):
        q = request.GET.get('q', '').strip()

        if not q:
            pacientes = Paciente.objects.select_related('id_usuario').filter(id_usuario__tipo_usuario='paciente')
        else:
            pacientes = Paciente.objects.select_related('id_usuario').filter(
                (Q(id_usuario__nombre__icontains=q) |
                 Q(id_usuario__apellido__icontains=q) |
                 Q(numero_identificacion__icontains=q)) &
                Q(id_usuario__tipo_usuario='paciente')
            )

        serializer = PacienteSerializer(pacientes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# ==================== OPENFDA API ====================

def traducir_texto(texto, idioma_destino='es'):
    """
    Traduce texto de inglés a español usando deep-translator
    Divide textos largos en fragmentos para evitar límites de la API
    """
    if not texto or texto == 'No disponible':
        return texto
    
    try:
        # Límite seguro por fragmento (Google Translate gratis soporta ~5000 caracteres)
        MAX_CHARS = 4500
        
        # Si el texto es corto, traducir directamente
        if len(texto) <= MAX_CHARS:
            traductor = GoogleTranslator(source='en', target=idioma_destino)
            return traductor.translate(texto)
        
        # Si el texto es largo, dividirlo en fragmentos
        fragmentos = []
        texto_restante = texto
        
        while len(texto_restante) > 0:
            # Tomar un fragmento
            if len(texto_restante) <= MAX_CHARS:
                fragmento = texto_restante
                texto_restante = ""
            else:
                # Buscar un punto o salto de línea para dividir de forma natural
                punto_corte = texto_restante[:MAX_CHARS].rfind('. ')
                if punto_corte == -1:
                    punto_corte = texto_restante[:MAX_CHARS].rfind('\n')
                if punto_corte == -1:
                    punto_corte = MAX_CHARS
                
                fragmento = texto_restante[:punto_corte + 1]
                texto_restante = texto_restante[punto_corte + 1:]
            
            # Traducir el fragmento
            traductor = GoogleTranslator(source='en', target=idioma_destino)
            fragmento_traducido = traductor.translate(fragmento.strip())
            fragmentos.append(fragmento_traducido)
        
        # Unir todos los fragmentos traducidos
        return ' '.join(fragmentos)
        
    except Exception as e:
        print(f"Error al traducir: {e}")
        return texto  # Si falla, devolver texto original


# Modificar la función buscar_medicamento_fda
@api_view(['GET'])
def buscar_medicamento_fda(request):
    """
    Busca información de un medicamento en OpenFDA y lo traduce al español
    GET /api/medicamento/buscar-fda/?nombre=omeprazol&traducir=true
    """
    nombre_medicamento = request.query_params.get('nombre', None)
    traducir = request.query_params.get('traducir', 'false').lower() == 'true'
    
    if not nombre_medicamento:
        return Response(
            {'error': 'Debe proporcionar el parámetro "nombre"'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Llamar a OpenFDA API
        url = f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{nombre_medicamento}"&limit=1'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 404:
            return Response(
                {
                    'mensaje': 'Medicamento no encontrado en FDA',
                    'nombre_buscado': nombre_medicamento
                }, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if response.status_code != 200:
            return Response(
                {'error': 'Error al conectar con OpenFDA'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        data = response.json()
        
        if not data.get('results'):
            return Response(
                {
                    'mensaje': 'No se encontraron resultados',
                    'nombre_buscado': nombre_medicamento
                }, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Extraer información relevante
        resultado = data['results'][0]
        openfda = resultado.get('openfda', {})
        
        # Preparar respuesta estructurada
        info_medicamento = {
            'nombre_comercial': openfda.get('brand_name', ['No disponible'])[0],
            'nombre_generico': openfda.get('generic_name', ['No disponible'])[0],
            'fabricante': openfda.get('manufacturer_name', ['No disponible'])[0],
            'indicaciones': resultado.get('indications_and_usage', ['No disponible'])[0] if resultado.get('indications_and_usage') else 'No disponible',
            'efectos_adversos': resultado.get('adverse_reactions', ['No disponible'])[0] if resultado.get('adverse_reactions') else 'No disponible',
            'contraindicaciones': resultado.get('contraindications', ['No disponible'])[0] if resultado.get('contraindications') else 'No disponible',
            'dosis': resultado.get('dosage_and_administration', ['No disponible'])[0] if resultado.get('dosage_and_administration') else 'No disponible',
            'advertencias': resultado.get('warnings', ['No disponible'])[0] if resultado.get('warnings') else 'No disponible',
            'interacciones': resultado.get('drug_interactions', ['No disponible'])[0] if resultado.get('drug_interactions') else 'No disponible',
        }
        
        # Si se solicita traducción, traducir los campos
        if traducir:
            info_medicamento_traducida = {}
            for campo, valor in info_medicamento.items():
                # No traducir nombres propios
                if campo in ['nombre_comercial', 'nombre_generico', 'fabricante']:
                    info_medicamento_traducida[campo] = valor
                else:
                    info_medicamento_traducida[campo] = traducir_texto(valor)
            
            info_medicamento = info_medicamento_traducida
        
        return Response({
            'mensaje': 'Medicamento encontrado exitosamente',
            'nombre_buscado': nombre_medicamento,
            'traducido': traducir,
            'datos': info_medicamento
        }, status=status.HTTP_200_OK)
        
    except requests.exceptions.Timeout:
        return Response(
            {'error': 'Timeout al conectar con OpenFDA'}, 
            status=status.HTTP_504_GATEWAY_TIMEOUT
        )
    except requests.exceptions.RequestException as e:
        return Response(
            {'error': f'Error de conexión: {str(e)}'}, 
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        return Response(
            {'error': f'Error inesperado: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# También actualizar verificar_interacciones_fda

@api_view(['GET'])
def verificar_interacciones_fda(request):
    """
    Verifica interacciones entre dos medicamentos específicos
    GET /api/medicamento/verificar-interacciones/?med1=aspirin&med2=ibuprofen&traducir=true
    """
    medicamento1 = request.query_params.get('med1', None)
    medicamento2 = request.query_params.get('med2', None)
    traducir = request.query_params.get('traducir', 'false').lower() == 'true'
    
    if not medicamento1 or not medicamento2:
        return Response(
            {'error': 'Debe proporcionar ambos parámetros: "med1" y "med2"'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Obtener información de ambos medicamentos
        medicamentos_info = {}
        
        for nombre in [medicamento1, medicamento2]:
            url = f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{nombre}"&limit=1'
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    resultado = data['results'][0]
                    interacciones_texto = resultado.get('drug_interactions', [''])[0] if resultado.get('drug_interactions') else ''
                    
                    medicamentos_info[nombre] = {
                        'encontrado': True,
                        'interacciones_completas': interacciones_texto
                    }
                else:
                    medicamentos_info[nombre] = {
                        'encontrado': False,
                        'interacciones_completas': ''
                    }
            else:
                medicamentos_info[nombre] = {
                    'encontrado': False,
                    'interacciones_completas': ''
                }
        
        # Verificar que ambos medicamentos fueron encontrados
        if not medicamentos_info[medicamento1]['encontrado']:
            mensaje = f'El medicamento "{medicamento1}" no fue encontrado en la base de datos de la FDA.'
            if traducir:
                mensaje = f'El medicamento "{medicamento1}" no fue encontrado en la base de datos de la FDA.'
            return Response({
                'mensaje': mensaje,
                'medicamentos_consultados': [medicamento1, medicamento2],
                'encontrados': False
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not medicamentos_info[medicamento2]['encontrado']:
            mensaje = f'El medicamento "{medicamento2}" no fue encontrado en la base de datos de la FDA.'
            if traducir:
                mensaje = f'El medicamento "{medicamento2}" no fue encontrado en la base de datos de la FDA.'
            return Response({
                'mensaje': mensaje,
                'medicamentos_consultados': [medicamento1, medicamento2],
                'encontrados': False
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Buscar si se mencionan mutuamente en las interacciones
        interaccion_especifica_encontrada = False
        resultado_interaccion = []
        
        # Buscar si med2 se menciona en las interacciones de med1
        texto_med1 = medicamentos_info[medicamento1]['interacciones_completas'].lower()
        texto_med2 = medicamentos_info[medicamento2]['interacciones_completas'].lower()
        
        # Términos relacionados a buscar
        terminos_med1 = [medicamento1.lower(), medicamento1.replace('-', '').lower()]
        terminos_med2 = [medicamento2.lower(), medicamento2.replace('-', '').lower()]
        
        # Buscar menciones específicas
        mencion_en_med1 = any(termino in texto_med1 for termino in terminos_med2)
        mencion_en_med2 = any(termino in texto_med2 for termino in terminos_med1)
        
        if mencion_en_med1 or mencion_en_med2:
            # Hay interacción específica mencionada
            interaccion_especifica_encontrada = True
            
            if mencion_en_med1:
                # Extraer el párrafo relevante donde se menciona
                fragmento = extraer_fragmento_relevante(
                    texto_med1, 
                    terminos_med2
                )
                if traducir:
                    fragmento = traducir_texto(fragmento)
                
                resultado_interaccion.append({
                    'encontrado_en': medicamento1,
                    'menciona_a': medicamento2,
                    'descripcion': fragmento
                })
            
            if mencion_en_med2:
                fragmento = extraer_fragmento_relevante(
                    texto_med2, 
                    terminos_med1
                )
                if traducir:
                    fragmento = traducir_texto(fragmento)
                
                resultado_interaccion.append({
                    'encontrado_en': medicamento2,
                    'menciona_a': medicamento1,
                    'descripcion': fragmento
                })
        
        # Preparar respuesta
        if interaccion_especifica_encontrada:
            mensaje = f'⚠️ Se encontró información de interacción específica entre {medicamento1} y {medicamento2}'
            if traducir:
                mensaje = f'⚠️ Se encontró información de interacción específica entre {medicamento1} y {medicamento2}'
            
            return Response({
                'mensaje': mensaje,
                'medicamentos_consultados': [medicamento1, medicamento2],
                'traducido': traducir,
                'interaccion_especifica': True,
                'advertencia': '⚠️ Esta información es referencial. Consulte con su médico antes de combinar estos medicamentos.',
                'datos': resultado_interaccion
            }, status=status.HTTP_200_OK)
        else:
            # No se encontró interacción específica mencionada
            mensaje_base = f'ℹ️ No se encontró una interacción específica documentada entre {medicamento1} y {medicamento2} en la base de datos de la FDA.'
            mensaje_info = 'Esto NO significa que sea seguro combinarlos. Siempre consulte con su médico o farmacéutico antes de tomar medicamentos en combinación.'
            
            if traducir:
                mensaje_base = f'ℹ️ No se encontró una interacción específica documentada entre {medicamento1} y {medicamento2} en la base de datos de la FDA.'
                mensaje_info = 'Esto NO significa que sea seguro combinarlos. Siempre consulte con su médico o farmacéutico antes de tomar medicamentos en combinación.'
            
            return Response({
                'mensaje': mensaje_base,
                'informacion_adicional': mensaje_info,
                'medicamentos_consultados': [medicamento1, medicamento2],
                'traducido': traducir,
                'interaccion_especifica': False,
                'advertencia': '⚠️ Consulte con su médico. La ausencia de información no garantiza seguridad.',
                'nota': 'Puede consultar las interacciones completas de cada medicamento por separado usando la búsqueda individual.'
            }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error al verificar interacciones: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Función auxiliar para extraer fragmento relevante
def extraer_fragmento_relevante(texto, terminos_buscar, caracteres_contexto=500):
    """
    Extrae el fragmento del texto donde se menciona alguno de los términos
    """
    texto_lower = texto.lower()
    
    for termino in terminos_buscar:
        posicion = texto_lower.find(termino)
        if posicion != -1:
            # Encontrar inicio del párrafo (punto anterior o inicio del texto)
            inicio = max(0, posicion - caracteres_contexto)
            # Buscar el punto anterior más cercano
            punto_anterior = texto[:posicion].rfind('. ', inicio, posicion)
            if punto_anterior != -1 and punto_anterior > inicio:
                inicio = punto_anterior + 2
            
            # Encontrar fin del párrafo (siguiente punto o fin del texto)
            fin = min(len(texto), posicion + caracteres_contexto)
            punto_siguiente = texto.find('. ', posicion, fin)
            if punto_siguiente != -1:
                fin = punto_siguiente + 1
            
            return texto[inicio:fin].strip()
    
    # Si no se encuentra, devolver los primeros caracteres
    return texto[:500] + "..." if len(texto) > 500 else texto

# También actualizar efectos_adversos_fda
@api_view(['GET'])
def efectos_adversos_fda(request):
    """
    Obtiene información detallada sobre efectos adversos de un medicamento
    GET /api/medicamento/efectos-adversos/?nombre=omeprazol&traducir=true
    """
    nombre_medicamento = request.query_params.get('nombre', None)
    traducir = request.query_params.get('traducir', 'false').lower() == 'true'
    
    if not nombre_medicamento:
        return Response(
            {'error': 'Debe proporcionar el parámetro "nombre"'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        url = f'https://api.fda.gov/drug/label.json?search=openfda.brand_name:"{nombre_medicamento}"&limit=1'
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return Response(
                {'error': 'Medicamento no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        data = response.json()
        
        if not data.get('results'):
            return Response(
                {'error': 'No se encontraron resultados'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        resultado = data['results'][0]
        
        efectos_info = {
            'medicamento': nombre_medicamento,
            'efectos_adversos': resultado.get('adverse_reactions', ['No disponible'])[0] if resultado.get('adverse_reactions') else 'No disponible',
            'advertencias': resultado.get('warnings', ['No disponible'])[0] if resultado.get('warnings') else 'No disponible',
            'precauciones': resultado.get('precautions', ['No disponible'])[0] if resultado.get('precautions') else 'No disponible',
        }
        
        # Traducir si se solicita
        if traducir:
            for campo in ['efectos_adversos', 'advertencias', 'precauciones']:
                efectos_info[campo] = traducir_texto(efectos_info[campo])
        
        return Response({
            'mensaje': 'Información de efectos adversos obtenida',
            'traducido': traducir,
            'datos': efectos_info
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error al obtener efectos adversos: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== RECETAS MÉDICAS ====================

class CrearRecetaAPIView(APIView):
    """
    Crea una receta médica (Tratamiento + TratamientoMedicamento)
    POST /api/receta/crear/
    """
    def post(self, request):
        serializer = CrearRecetaSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            datos = serializer.validated_data
            
            # Obtener médico y paciente
            medico = Medico.objects.get(id_medico=datos['id_medico'])
            paciente = Paciente.objects.get(id_paciente=datos['id_paciente'])
            
            # Calcular fecha de fin según vigencia
            from datetime import timedelta
            fecha_fin = datos['fecha_emision'] + timedelta(days=datos['vigencia_dias'])
            
            # Crear tratamiento
            tratamiento = Tratamiento.objects.create(
                id_paciente=paciente,
                id_medico=medico,
                diagnostico=datos['diagnostico'],
                fecha_inicio=datos['fecha_emision'],
                fecha_fin=fecha_fin,
                duracion_dias=datos['vigencia_dias'],
                tipo_tratamiento='Receta Médica',
                objetivo_terapeutico=datos.get('instrucciones', ''),
                estado='activo',
                observaciones=''
            )
            
            # Crear medicamentos del tratamiento
            medicamentos_creados = []
            for med_data in datos['medicamentos']:
                medicamento = Medicamento.objects.get(id_medicamento=med_data['id_medicamento'])
                
                tratamiento_medicamento = TratamientoMedicamento.objects.create(
                    id_tratamiento=tratamiento,
                    id_medicamento=medicamento,
                    dosis=med_data['dosis'],
                    frecuencia=med_data['frecuencia'],
                    via_administracion=med_data['via_administracion'],
                    duracion_dias=med_data['duracion_dias'],
                    horarios=med_data.get('horarios', []),
                    instrucciones_especiales=med_data.get('instrucciones_especiales', ''),
                    activo=True
                )
                
                medicamentos_creados.append({
                    'id_tratamiento_medicamento': tratamiento_medicamento.id_tratamiento_medicamento,
                    'medicamento': medicamento.nombre_comercial,
                    'dosis': med_data['dosis'],
                    'frecuencia': med_data['frecuencia']
                })
            
            # Crear notificación para el paciente
            Notificacion.objects.create(
                id_usuario_destino=paciente.id_usuario,
                tipo_notificacion='mensaje_medico',
                titulo='Nueva Receta Médica',
                mensaje=f'El Dr. {medico.id_usuario.nombre} {medico.id_usuario.apellido} ha emitido una nueva receta.',
                estado='pendiente'
            )
            
            return Response({
                'mensaje': 'Receta médica creada exitosamente',
                'data': {
                    'id_tratamiento': tratamiento.id_tratamiento,
                    'paciente': f"{paciente.id_usuario.nombre} {paciente.id_usuario.apellido}",
                    'medico': f"Dr. {medico.id_usuario.nombre} {medico.id_usuario.apellido}",
                    'diagnostico': tratamiento.diagnostico,
                    'fecha_emision': tratamiento.fecha_inicio,
                    'fecha_vencimiento': tratamiento.fecha_fin,
                    'medicamentos': medicamentos_creados
                }
            }, status=status.HTTP_201_CREATED)
            
        except Medico.DoesNotExist:
            return Response(
                {'error': 'El médico especificado no existe'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Paciente.DoesNotExist:
            return Response(
                {'error': 'El paciente especificado no existe'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Medicamento.DoesNotExist:
            return Response(
                {'error': 'Uno o más medicamentos no existen'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error al crear la receta: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ListarRecetasAPIView(APIView):
    """
    Lista recetas médicas por paciente o médico
    GET /api/receta/listar/?paciente_id=1
    GET /api/receta/listar/?medico_id=1
    """
    def get(self, request):
        paciente_id = request.query_params.get('paciente_id')
        medico_id = request.query_params.get('medico_id')
        
        try:
            if paciente_id:
                tratamientos = Tratamiento.objects.filter(
                    id_paciente_id=paciente_id,
                    tipo_tratamiento='Receta Médica'
                )
            elif medico_id:
                tratamientos = Tratamiento.objects.filter(
                    id_medico_id=medico_id,
                    tipo_tratamiento='Receta Médica'
                )
            else:
                tratamientos = Tratamiento.objects.filter(
                    tipo_tratamiento='Receta Médica'
                )
            
            recetas = []
            for tratamiento in tratamientos:
                medicamentos = TratamientoMedicamento.objects.filter(
                    id_tratamiento=tratamiento
                )
                
                recetas.append({
                    'id_tratamiento': tratamiento.id_tratamiento,
                    'paciente': f"{tratamiento.id_paciente.id_usuario.nombre} {tratamiento.id_paciente.id_usuario.apellido}",
                    'medico': f"Dr. {tratamiento.id_medico.id_usuario.nombre} {tratamiento.id_medico.id_usuario.apellido}",
                    'diagnostico': tratamiento.diagnostico,
                    'fecha_emision': tratamiento.fecha_inicio,
                    'fecha_vencimiento': tratamiento.fecha_fin,
                    'estado': tratamiento.estado,
                    'medicamentos_count': medicamentos.count()
                })
            
            return Response({
                'mensaje': f'{len(recetas)} receta(s) encontrada(s)',
                'data': recetas
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error al listar recetas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )