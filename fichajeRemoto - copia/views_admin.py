# fichajeRemoto/views_admin.py

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.db.models import Q
from datetime import datetime, date
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO

from .models import Usuario, Registro, TecladoFichaje, Empresa


class AdministracionView(View):
    """Vista principal del panel de administración"""
    
    def get(self, request):
        # Renderizar el template HTML principal
        return render(request, 'fichajeRemoto/administracion.html')


class EmpresasAPIView(View):
    """API para obtener la lista de empresas"""
    
    def get(self, request):
        try:
            empresas = Empresa.objects.all().order_by('empresaNombre')
            
            empresas_data = []
            for empresa in empresas:
                # Contar empleados asociados a esta empresa a través de los teclados
                empleados_count = Usuario.objects.filter(
                    registro_set__teclado_asocido__empresa_asociada=empresa
                ).distinct().count()
                
                empresas_data.append({
                    'id': empresa.id,
                    'nombre': empresa.empresaNombre,
                    'codigo': empresa.empresaCodigo,
                    'timeOffset': empresa.empresa_timeOffset,
                    'empleados_count': empleados_count
                })
            
            return JsonResponse({
                'success': True,
                'empresas': empresas_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class EmpleadosAPIView(View):
    """API para obtener la lista de empleados"""
    
    def get(self, request):
        try:
            # Parámetro opcional para filtrar por empresa
            empresa_id = request.GET.get('empresa_id')
            
            if empresa_id:
                # Filtrar empleados que han trabajado en esta empresa
                empleados = Usuario.objects.filter(
                    registro_set__teclado_asocido__empresa_asociada_id=empresa_id
                ).distinct().order_by('usuarioApellido', 'usuarioNombre')
            else:
                # Todos los empleados
                empleados = Usuario.objects.all().order_by('usuarioApellido', 'usuarioNombre')
            
            empleados_data = []
            for emp in empleados:
                # Obtener la última empresa donde trabajó
                ultimo_registro = Registro.objects.filter(
                    regUsuario=emp,
                    teclado_asocido__empresa_asociada__isnull=False
                ).order_by('-regEntrada').first()
                
                ultima_empresa = None
                if ultimo_registro and ultimo_registro.teclado_asocido:
                    ultima_empresa = {
                        'id': ultimo_registro.teclado_asocido.empresa_asociada.id,
                        'nombre': ultimo_registro.teclado_asocido.empresa_asociada.empresaNombre
                    }
                
                empleados_data.append({
                    'id': emp.id,
                    'nombre': emp.usuarioNombre,
                    'apellido': emp.usuarioApellido,
                    'dni': emp.usuarioDNI,
                    'working': emp.is_working,
                    'pin': emp.usuarioPIN,
                    'ultima_empresa': ultima_empresa
                })
            
            return JsonResponse({
                'success': True,
                'empleados': empleados_data,
                'total': len(empleados_data)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class RegistrosAPIView(View):
    """API para obtener registros de un empleado"""
    
    def get(self, request, empleado_id):
        try:
            # Obtener parámetros de fecha
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin') 
            empresa_id = request.GET.get('empresa_id')  # Nuevo parámetro
            
            # Obtener empleado
            try:
                empleado = Usuario.objects.get(id=empleado_id)
            except Usuario.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Empleado no encontrado'
                }, status=404)
            
            # Construir query de registros
            registros_query = Registro.objects.filter(regUsuario=empleado)
            
            # Aplicar filtros de fecha si se proporcionan
            if fecha_inicio:
                registros_query = registros_query.filter(regEntrada__date__gte=fecha_inicio)
            if fecha_fin:
                registros_query = registros_query.filter(regEntrada__date__lte=fecha_fin)
            
            # Filtrar por empresa si se especifica
            if empresa_id:
                registros_query = registros_query.filter(
                    teclado_asocido__empresa_asociada_id=empresa_id
                )
            
            # Ordenar por fecha
            registros = registros_query.order_by('-regEntrada')
            
            # Formatear datos para JSON
            registros_data = []
            for reg in registros:
                # Calcular horas trabajadas
                if reg.regSalida:
                    duracion = reg.regSalida - reg.regEntrada
                    total_seconds = int(duracion.total_seconds())
                    horas = total_seconds // 3600
                    minutos = (total_seconds % 3600) // 60
                    segundos = total_seconds % 60
                    horas_str = f"{horas:02d}h {minutos:02d}m {segundos:02d}s"
                else:
                    horas_str = "En curso"
                
                # Obtener lugar de fichaje
                lugar = reg.teclado_asocido.empresa_asociada.empresaNombre if reg.teclado_asocido and reg.teclado_asocido.empresa_asociada else "Remoto" # FER
                
                registros_data.append({
                    'id': reg.id,
                    'fecha': reg.regEntrada.date().isoformat(),
                    'entrada': reg.regEntrada.strftime('%H:%M:%S'),
                    'salida': reg.regSalida.strftime('%H:%M:%S') if reg.regSalida else None,
                    'lugar': lugar,
                    'horas': horas_str,
                    'minutos_totales': reg.minutos,
                    'horas_decimales': float(reg.horas) if reg.horas else 0.0,
                    'empresa_id': reg.teclado_asocido.empresa_asociada.id if reg.teclado_asocido and reg.teclado_asocido.empresa_asociada else None
                })
            
            return JsonResponse({
                'success': True,
                'empleado': {
                    'id': empleado.id,
                    'nombre': empleado.usuarioNombre,
                    'apellido': empleado.usuarioApellido,
                    'dni': empleado.usuarioDNI
                },
                'registros': registros_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class ExportarPDFView(View):
    """Vista para exportar registros a PDF"""
    
    def get(self, request, empleado_id):
        try:
            # Obtener empleado
            empleado = Usuario.objects.get(id=empleado_id)
            
            # Obtener parámetros de fecha y lugar
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            empresa_id = request.GET.get('empresa_id')
            lugar = request.GET.get('lugar')  # Nuevo parámetro para filtro de lugar
            
            # Obtener registros
            registros_query = Registro.objects.filter(regUsuario=empleado)
            
            if fecha_inicio:
                registros_query = registros_query.filter(regEntrada__date__gte=fecha_inicio)
            if fecha_fin:
                registros_query = registros_query.filter(regEntrada__date__lte=fecha_fin)
            if empresa_id:
                registros_query = registros_query.filter(
                    teclado_asocido__empresa_asociada_id=empresa_id
                )
            
            # Aplicar filtro de lugar si se especifica
            if lugar:
                registros_query = registros_query.filter(
                    teclado_asocido__empresa_asociada__empresaNombre=lugar
                )
            
            registros = registros_query.order_by('regEntrada')
            
            # Crear PDF
            response = HttpResponse(content_type='application/pdf')
            
            # Nombre del archivo incluye empresa y lugar si están filtrados
            filename = f"fichaje_{empleado.usuarioApellido}_{empleado.usuarioNombre}"
            if empresa_id:
                try:
                    empresa = Empresa.objects.get(id=empresa_id)
                    filename += f"_{empresa.empresaNombre}"
                except Empresa.DoesNotExist:
                    pass
            elif lugar:
                filename += f"_{lugar}"
            filename += ".pdf"
            
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            # Crear el documento PDF
            doc = SimpleDocTemplate(response, pagesize=A4)
            elements = []
            
            # Estilos
            styles = getSampleStyleSheet()
            
            # Título
            title_text = f"<b>Reporte de Fichaje - {empleado.usuarioNombre} {empleado.usuarioApellido}</b>"
            if empresa_id:
                try:
                    empresa = Empresa.objects.get(id=empresa_id)
                    title_text += f"<br/><b>Empresa: {empresa.empresaNombre}</b>"
                except Empresa.DoesNotExist:
                    pass
            elif lugar:
                title_text += f"<br/><b>Lugar: {lugar}</b>"
            
            title = Paragraph(title_text, styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 20))
            
            # Información del empleado
            info_text = f"""
            <b>DNI:</b> {empleado.usuarioDNI}<br/>
            <b>Período:</b> {fecha_inicio or 'Desde el inicio'} - {fecha_fin or 'Hasta hoy'}<br/>
            """
            if lugar:
                info_text += f"<b>Lugar:</b> {lugar}<br/>"
            info_text += f"<b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            
            info = Paragraph(info_text, styles['Normal'])
            elements.append(info)
            elements.append(Spacer(1, 20))
            
            # Tabla de registros
            data = [['Fecha', 'Entrada', 'Salida', 'Lugar', 'Horas Trabajadas']]
            
            total_horas = 0
            for reg in registros:
                fecha_str = reg.regEntrada.strftime('%d/%m/%Y')
                entrada_str = reg.regEntrada.strftime('%H:%M:%S')
                salida_str = reg.regSalida.strftime('%H:%M:%S') if reg.regSalida else 'En curso'
                lugar_reg = reg.teclado_asocido.empresa_asociada.empresaNombre if reg.teclado_asocido and reg.teclado_asocido.empresa_asociada else "Remoto"
                
                if reg.regSalida:
                    duracion = reg.regSalida - reg.regEntrada
                    total_seconds = int(duracion.total_seconds())
                    horas = total_seconds // 3600
                    minutos = (total_seconds % 3600) // 60
                    horas_str = f"{horas:02d}h {minutos:02d}m"
                    total_horas += horas + (minutos / 60)
                else:
                    horas_str = "En curso"
                
                data.append([fecha_str, entrada_str, salida_str, lugar_reg, horas_str])
            
            # Crear tabla
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 20))
            
            # Resumen
            resumen_text = f"""
            <b>RESUMEN:</b><br/>
            Total de registros: {len(registros)}<br/>
            Total de horas trabajadas: {total_horas:.2f}h<br/>
            Promedio por día: {(total_horas / len(registros)):.2f}h (si hay registros)
            """
            resumen = Paragraph(resumen_text, styles['Normal'])
            elements.append(resumen)
            
            # Construir PDF
            doc.build(elements)
            
            return response
            
        except Usuario.DoesNotExist:
            return HttpResponse("Empleado no encontrado", status=404)
        except Exception as e:
            return HttpResponse(f"Error al generar PDF: {str(e)}", status=500)


# Vistas auxiliares para CRUD de empleados (opcional)
@method_decorator(csrf_exempt, name='dispatch')
class EmpleadoCRUDView(View):
    """Vista para operaciones CRUD de empleados"""
    
    def post(self, request):
        """Crear nuevo empleado"""
        try:
            data = json.loads(request.body)
            
            empleado = Usuario.objects.create(
                usuarioNombre=data['nombre'],
                usuarioApellido=data['apellido'],
                usuarioDNI=data['dni'],
                usuarioPIN=data['pin']
            )
            
            return JsonResponse({
                'success': True,
                'empleado': {
                    'id': empleado.id,
                    'nombre': empleado.usuarioNombre,
                    'apellido': empleado.usuarioApellido,
                    'dni': empleado.usuarioDNI,
                    'working': empleado.is_working
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    def put(self, request, empleado_id):
        """Actualizar empleado existente"""
        try:
            empleado = Usuario.objects.get(id=empleado_id)
            data = json.loads(request.body)
            
            empleado.usuarioNombre = data.get('nombre', empleado.usuarioNombre)
            empleado.usuarioApellido = data.get('apellido', empleado.usuarioApellido)
            empleado.usuarioDNI = data.get('dni', empleado.usuarioDNI)
            empleado.usuarioPIN = data.get('pin', empleado.usuarioPIN)
            empleado.save()
            
            return JsonResponse({
                'success': True,
                'empleado': {
                    'id': empleado.id,
                    'nombre': empleado.usuarioNombre,
                    'apellido': empleado.usuarioApellido,
                    'dni': empleado.usuarioDNI,
                    'working': empleado.is_working
                }
            })
            
        except Usuario.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Empleado no encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    def delete(self, request, empleado_id):
        """Eliminar empleado"""
        try:
            empleado = Usuario.objects.get(id=empleado_id)
            empleado.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Empleado eliminado correctamente'
            })
            
        except Usuario.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Empleado no encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)