# fichajeRemoto/urls_admin.py
from .models import Usuario, Registro, TecladoFichaje, Empresa

from django.urls import path
from .views_admin import (
    AdministracionView, 
    EmpleadosAPIView, 
    RegistrosAPIView, 
    ExportarPDFView,
    EmpleadoCRUDView,
    EmpresasAPIView
)

app_name = 'administracion'

urlpatterns = [
    # Vista principal del panel de administración
    path('', AdministracionView.as_view(), name='panel'),
    
    # APIs para datos
    path('api/empleados/', EmpleadosAPIView.as_view(), name='api_empleados'),
    path('api/registros/<int:empleado_id>/', RegistrosAPIView.as_view(), name='api_registros'),
    
    # Exportar PDF
    path('export-pdf/<int:empleado_id>/', ExportarPDFView.as_view(), name='export_pdf'),
    
    # CRUD de empleados (opcional)
    path('api/empleados/crud/', EmpleadoCRUDView.as_view(), name='empleado_create'),
    path('api/empleados/crud/<int:empleado_id>/', EmpleadoCRUDView.as_view(), name='empleado_crud'),

    path('administracion/api/empresas/', EmpresasAPIView.as_view(), name='empresas_api'),
]