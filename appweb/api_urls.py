from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import APIviews

# Router para ViewSets de Django REST Framework
router = DefaultRouter()
router.register(r'usuarios', APIviews.UsuarioViewSet, basename='usuario')
router.register(r'medicos-api', APIviews.MedicoViewSet, basename='medico-api')
router.register(r'pacientes-api', APIviews.PacienteViewSet, basename='paciente-api')
router.register(r'medicamentos', APIviews.MedicamentoViewSet, basename='medicamento')
router.register(r'tratamientos', APIviews.TratamientoViewSet, basename='tratamiento')
router.register(r'tratamiento-medicamentos', APIviews.TratamientoMedicamentoViewSet, basename='tratamiento-medicamento')
router.register(r'notificaciones', APIviews.NotificacionViewSet, basename='notificacion')
router.register(r'historial-adherencia', APIviews.HistorialAdherenciaViewSet, basename='historial-adherencia')
router.register(r'paciente-cuidador', APIviews.PacienteCuidadorViewSet, basename='paciente-cuidador')

urlpatterns = [
    # --- ViewSets (Router de Django REST Framework) ---
    path('', include(router.urls)),
    
    # --- APIs de Autenticación ---
    path('auth/login/', APIviews.LoginAPIView.as_view(), name='api-login'),
    path('auth/logout/', APIviews.LogoutAPIView.as_view(), name='api-logout'),
    path('auth/registro/', APIviews.RegistroUsuarioAPIView.as_view(), name='api-registro'),
    path('auth/cambiar-password/', APIviews.CambiarPasswordAPIView.as_view(), name='api-cambiar-password'),
    path('auth/verificar-sesion/', APIviews.VerificarSesionAPIView.as_view(), name='api-verificar-sesion'),
    
    # --- APIs de Médicos (CRUD) ---
    path('medico/crear/', APIviews.CrearMedicoAPIView.as_view(), name='api-crear-medico'),
    path('medico/listar/', APIviews.ListarMedicosAPIView.as_view(), name='api-listar-medicos'),
    path('medico/editar/<int:medico_id>/', APIviews.EditarMedicoAPIView.as_view(), name='api-editar-medico'),
    path('medico/eliminar/<int:medico_id>/', APIviews.EliminarMedicoAPIView.as_view(), name='api-eliminar-medico'),
    
    # --- APIs de Pacientes (CRUD) ---
    path('paciente/crear/', APIviews.CrearPacienteAPIView.as_view(), name='api-crear-paciente'),
    path('paciente/listar/', APIviews.ListarPacientesAPIView.as_view(), name='api-listar-pacientes'),
    path('paciente/buscar/', APIviews.BuscarPacientesAPIView.as_view(), name='api-buscar-pacientes'),
    path('paciente/editar/<int:paciente_id>/', APIviews.EditarPacienteAPIView.as_view(), name='api-editar-paciente'),
    path('paciente/eliminar/<int:paciente_id>/', APIviews.EliminarPacienteAPIView.as_view(), name='api-eliminar-paciente'),
    
    # --- APIs de Recetas Médicas ---
    path('receta/crear/', APIviews.CrearRecetaAPIView.as_view(), name='api-crear-receta'),
    path('receta/listar/', APIviews.ListarRecetasAPIView.as_view(), name='api-listar-recetas'),
    
    #  OPENFDA 
    path('medicamento/buscar-fda/', APIviews.buscar_medicamento_fda, name='buscar-medicamento-fda'),
    path('medicamento/verificar-interacciones/', APIviews.verificar_interacciones_fda, name='verificar-interacciones-fda'),
    path('medicamento/efectos-adversos/', APIviews.efectos_adversos_fda, name='efectos-adversos-fda'),
]
