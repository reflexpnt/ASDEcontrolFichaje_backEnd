# fichajeRemoto/urls_admin.py - VERSIÓN 2.1 FINAL - v2

from django.urls import path
from fichajeRemoto import views_admin

urlpatterns = [
    # Vista principal de administración
    path('', views_admin.AdministracionView.as_view(), name='administracion'),
    
    # APIs para datos
    path('api/empresas/', views_admin.EmpresasAPIView.as_view(), name='api_empresas'),
    path('api/empleados/', views_admin.EmpleadosAPIView.as_view(), name='api_empleados'),
    path('api/registros/<int:empleado_id>/', views_admin.RegistrosAPIView.as_view(), name='api_registros'),
    
    # API para editar registros
    path('api/editar-registro/<int:registro_id>/', views_admin.EditarRegistroView.as_view(), name='api_editar_registro'),
    
    # Exportar PDF
    path('export-pdf/<int:empleado_id>/', views_admin.ExportarPDFView.as_view(), name='export_pdf'),
    
    # CRUD de empleados (opcional)
    path('api/empleado/', views_admin.EmpleadoCRUDView.as_view(), name='empleado_create'),
    path('api/empleado/<int:empleado_id>/', views_admin.EmpleadoCRUDView.as_view(), name='empleado_crud'),
]