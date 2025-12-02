from django.urls import path, include
from . import views       # Vistas HTML

app_name = 'meditrack'

urlpatterns = [
    # ========================================================================
    # PÁGINAS HTML - Para navegación del usuario (lo que ve en el navegador)
    # ========================================================================
    
    # --- Páginas Principales ---
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    
    # --- Dashboards ---
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/medico/', views.dashboard_medico, name='dashboard_medico'),
    path('dashboard/paciente/', views.dashboard_paciente, name='dashboard_paciente'),
    
    # --- Páginas de Médicos (Formularios y Vistas) ---
    path('medico/crear/', views.crear_medico_view, name='crear_medico'),
    path('medico/editar/<int:medico_id>/', views.editar_medico_view, name='editar_medico'),
    path('medico/listar/', views.listar_medicos_view, name='listar_medicos'),
    path('medico/eliminar/<int:medico_id>/', views.eliminar_medico_view, name='eliminar_medico'),
    path('medico/detalle/<int:medico_id>/', views.detalle_medico_view, name='detalle_medico'),
    
    # --- Páginas de Pacientes (Formularios y Vistas) ---
    path('paciente/crear/', views.crear_paciente_view, name='crear_paciente'),
    path('paciente/editar/<int:paciente_id>/', views.editar_paciente_view, name='editar_paciente'),
    path('paciente/listar/', views.listar_pacientes_view, name='listar_pacientes'),
    path('paciente/eliminar/<int:paciente_id>/', views.eliminar_paciente_view, name='eliminar_paciente'),
    path('paciente/detalle/<int:paciente_id>/', views.detalle_paciente_view, name='detalle_paciente'),
    path('paciente/historial/<int:paciente_id>/', views.historial_paciente_view, name='historial_paciente'),
    
    # --- Páginas de Recetas Médicas ---
    path('medico/receta/crear/', views.crear_receta_view, name='crear_receta'),
    path('medico/receta/listar/', views.listar_recetas_view, name='listar_recetas'),
    
    # --- Otras Páginas ---
    path('perfil/', views.perfil_view, name='perfil'),
    path('configuracion/', views.configuracion_view, name='configuracion'),
    path('ayuda/', views.ayuda_view, name='ayuda'),

    # --- Búsqueda de Medicamentos (OpenFDA) ---
    path('medicamento/buscar/', views.buscar_medicamento_view, name='buscar_medicamento'),
    
    # ========================================================================
    # APIs REST - IMPORTANTE: Esto debe ir AL FINAL
    # ========================================================================
    path('api/', include('appweb.api_urls')),

    

]