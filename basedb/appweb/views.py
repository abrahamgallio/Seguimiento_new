from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Usuario, Medico, Paciente


# ==================== PÁGINAS PRINCIPALES ====================

def index(request):
    """Página principal - Landing page"""
    return render(request, 'principal.html')


def login_view(request):
    """Página de login"""
    return render(request, 'login.html')


# ==================== DASHBOARDS ====================

def dashboard_admin(request):
    """Dashboard para administradores"""
    return render(request, 'dashboard_admin.html')


def dashboard_medico(request):
    """Dashboard para médicos"""
    return render(request, 'dashboard_medico.html')


def dashboard_paciente(request):
    """Dashboard para pacientes"""
    return render(request, 'dashboard_paciente.html')


# ==================== FORMULARIOS DE MÉDICOS ====================

def crear_medico_view(request):
    """Vista para mostrar el formulario de crear médico"""
    return render(request, 'crearMedico.html')


def editar_medico_view(request, medico_id):
    """Vista para mostrar el formulario de editar médico"""
    try:
        medico = Medico.objects.select_related('id_usuario').get(id_medico=medico_id)
        context = {
            'medico_id': medico_id,
            'medico': medico
        }
        return render(request, 'editarMedico.html', context)
    except Medico.DoesNotExist:
        messages.error(request, 'Médico no encontrado')
        return redirect('listar_medicos')


def listar_medicos_view(request):
    """Vista para mostrar la lista de médicos"""
    return render(request, 'listarMedico.html')


def eliminar_medico_view(request, medico_id):
    """Vista para mostrar confirmación de eliminar médico"""
    try:
        medico = Medico.objects.select_related('id_usuario').get(id_medico=medico_id)
        context = {
            'medico_id': medico_id,
            'medico': medico
        }
        return render(request, 'eliminarMedico.html', context)
    except Medico.DoesNotExist:
        messages.error(request, 'Médico no encontrado')
        return redirect('listar_medicos')


def detalle_medico_view(request, medico_id):
    """Vista para mostrar detalles de un médico"""
    try:
        medico = Medico.objects.select_related('id_usuario').get(id_medico=medico_id)
        context = {
            'medico': medico
        }
        return render(request, 'detalleMedico.html', context)
    except Medico.DoesNotExist:
        messages.error(request, 'Médico no encontrado')
        return redirect('listar_medicos')


# ==================== FORMULARIOS DE PACIENTES ====================

def crear_paciente_view(request):
    """Vista para mostrar el formulario de crear paciente"""
    return render(request, 'crearPaciente.html')


def editar_paciente_view(request, paciente_id):
    """Vista para mostrar el formulario de editar paciente"""
    try:
        paciente = Paciente.objects.select_related('id_usuario').get(id_paciente=paciente_id)
        context = {
            'paciente_id': paciente_id,
            'paciente': paciente
        }
        return render(request, 'editarPaciente.html', context)
    except Paciente.DoesNotExist:
        messages.error(request, 'Paciente no encontrado')
        return redirect('listar_pacientes')


def listar_pacientes_view(request):
    """Vista para mostrar la lista de pacientes"""
    return render(request, 'listarPaciente.html')


def eliminar_paciente_view(request, paciente_id):
    """Vista para mostrar confirmación de eliminar paciente"""
    try:
        paciente = Paciente.objects.select_related('id_usuario').get(id_paciente=paciente_id)
        context = {
            'paciente_id': paciente_id,
            'paciente': paciente
        }
        return render(request, 'eliminarPaciente.html', context)
    except Paciente.DoesNotExist:
        messages.error(request, 'Paciente no encontrado')
        return redirect('listar_pacientes')


def detalle_paciente_view(request, paciente_id):
    """Vista para mostrar detalles de un paciente"""
    try:
        paciente = Paciente.objects.select_related('id_usuario').get(id_paciente=paciente_id)
        context = {
            'paciente': paciente
        }
        return render(request, 'detallePaciente.html', context)
    except Paciente.DoesNotExist:
        messages.error(request, 'Paciente no encontrado')
        return redirect('listar_pacientes')


def historial_paciente_view(request, paciente_id):
    """Vista para mostrar el historial médico de un paciente"""
    try:
        paciente = Paciente.objects.select_related('id_usuario').get(id_paciente=paciente_id)
        context = {
            'paciente': paciente
        }
        return render(request, 'historialPaciente.html', context)
    except Paciente.DoesNotExist:
        messages.error(request, 'Paciente no encontrado')
        return redirect('listar_pacientes')


# ==================== OTRAS VISTAS ====================

def perfil_view(request):
    """Vista de perfil de usuario"""
    return render(request, 'perfil.html')


def configuracion_view(request):
    """Vista de configuración"""
    return render(request, 'configuracion.html')


def ayuda_view(request):
    """Vista de ayuda"""
    return render(request, 'ayuda.html')

#==================== VISTAS DE RECETAS MÉDICAS ====================

def crear_receta_view(request):
    """Vista para crear receta médica"""
    return render(request, 'recetaMedica.html')


def listar_recetas_view(request):
    """Vista para listar recetas médicas"""
    return render(request, 'listarRecetas.html')

#==================== VISTAS ADICIONALES ====================

def buscar_medicamento_view(request):
    """Vista para buscar medicamentos en OpenFDA"""
    return render(request, 'buscarMedicamento.html')