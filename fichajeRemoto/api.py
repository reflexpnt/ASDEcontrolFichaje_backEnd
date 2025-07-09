# fichajeRemoto -> api.py (VERSIÓN 2 CON CORRECCIÓN DE ZONA HORARIA)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.decorators import api_view

#for authentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import user_passes_test

from django.shortcuts import get_object_or_404
from django.conf import settings as django_settings
from django.http import FileResponse
import os
from django.http import JsonResponse

from django.core.exceptions import ObjectDoesNotExist

from datetime import datetime  
from django.utils import timezone
from django.utils.timezone import make_aware, get_current_timezone, localtime

import asyncio

from fichajeRemoto.serializers import *
from fichajeRemoto.models import TecladoFichaje, Usuario, Registro, Empresa

from datetime import datetime, timedelta
from django.utils import timezone

from django.core.exceptions import ObjectDoesNotExist

import os
import json
from django.conf import settings as django_settings


RED   = "\033[1;31m"  
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RESET = "\033[0;0m"
BOLD    = "\033[;1m"
REVERSE = "\033[;7m"

@api_view(['GET']) 
def fichajeRemoto_list(request):
    
    for i in range(5, 21):  # 21 porque range es exclusivo del final
        nombre = "Test_" + str(i)
        apellido = nombre 
        dni= "xxx123456"
        pin = 8000 + i
        intancia = Usuario.objects.create(usuarioNombre= nombre, usuarioApellido= apellido,usuarioDNI = dni ,usuarioPIN = pin ,is_working= False)

    if request.method == 'GET':
        data = TecladoFichaje.objects.all()
        tecladoFichaje_serializer = TecladoFichajeSerializer(data, context={'request': request}, many=True)
        return Response(tecladoFichaje_serializer.data)

    elif request.method == 'POST':
        serializer = TecladoFichaje(data=request.data)
        if serializer.is_valid():
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def checkserver(request, mac_address):
    """
    Función que responde al dispositivo NodeMCU con la hora local configurada en Django
    """
    # Diccionarios para traducir días y meses
    DIAS_SEMANA = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes', 
        'Wednesday': 'Miercoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sabado',
        'Sunday': 'Domingo'
    }
    
    MESES = {
        'January': 'Enero',
        'February': 'Febrero',
        'March': 'Marzo',
        'April': 'Abril',
        'May': 'Mayo',
        'June': 'Junio',
        'July': 'Julio',
        'August': 'Agosto',
        'September': 'Septiembre',
        'October': 'Octubre',
        'November': 'Noviembre',
        'December': 'Diciembre'
    }
    
    # CORRECCIÓN: Obtener tiempo UTC y convertir a hora local
    utc_time = timezone.now()
    local_time = localtime(utc_time)  # Convierte UTC a la zona horaria local configurada
    
    print(f"{YELLOW}UTC time: {utc_time}{RESET}")
    print(f"{GREEN}Local time: {local_time}{RESET}")
    print(f"{CYAN}Timezone setting: {django_settings.TIME_ZONE}{RESET}")
    
    teclado_instancia = None
    empresa_asociada_temp = Empresa.objects.all()[0]

    try:
        teclado_instancia = TecladoFichaje.objects.get(MAC_address=mac_address)        
        teclado_instancia.lastUpdate = utc_time  # Guardamos en UTC en la DB
        teclado_instancia.IsActive = True
        teclado_instancia.save()
    except ObjectDoesNotExist:
        teclado_instancia = TecladoFichaje.objects.update_or_create(
            MAC_address=mac_address, 
            lastUpdate=utc_time,  # Guardamos en UTC en la DB
            empresa_asociada=empresa_asociada_temp
        )[0]
    
    # CORRECCIÓN: Formatear fecha usando el tiempo local
    dia_semana = DIAS_SEMANA[local_time.strftime("%A")]
    mes = MESES[local_time.strftime("%B")].upper()
    
    date_time_str = f"{dia_semana}_{local_time.day:02d}-{mes}-{local_time.year}_{local_time.strftime('%H:%M:%S')}"
    print(f"{CYAN}Respuesta al dispositivo: {date_time_str}{RESET}")
    
    return JsonResponse({'serverOK': date_time_str}, json_dumps_params={'ensure_ascii': False})


def validatepin(request, mac_address):
    """
    Función que valida el PIN y registra entrada/salida usando tiempo local
    """
    PIN = None
    TECLADO_FICHAJE_UTILIZADO = None
    USUARIO = None
    ULTIMO_REGISTRO = None
    TIPO_REGISTRO = None    # 'Entrada' / 'Salida'
    
    # CORRECCIÓN: Obtener tiempo UTC y local
    utc_time = timezone.now()
    local_time = localtime(utc_time)

    try:
        data = json.loads(request.body)
        PIN = data.get('pin', '')
        print(f"PIN : {PIN}") 
    except Exception as e:
        print(f"Error al parsear JSON: {str(e)}") 
        return JsonResponse({'PIN_BAD': False, 'error': str(e)})

    try:
        TECLADO_FICHAJE_UTILIZADO = TecladoFichaje.objects.get(MAC_address=mac_address)        
        TECLADO_FICHAJE_UTILIZADO.lastUpdate = utc_time  # Guardamos en UTC
        TECLADO_FICHAJE_UTILIZADO.IsActive = True
        TECLADO_FICHAJE_UTILIZADO.save()
    except TecladoFichaje.DoesNotExist as e:
        # utilizo teclado REMOTO
        TECLADO_FICHAJE_UTILIZADO = TecladoFichaje.objects.get_or_create(
            MAC_address="00:00:00:00:00:00", 
            defaults={
                'empresa_timeOffset': 0, 
                'IsActive': True, 
                'lastUpdate': utc_time,
                'empresa_asociada': Empresa.objects.first()
            }
        )[0]

    try:
        USUARIO = Usuario.objects.get(usuarioPIN=PIN)        
        print(f"usuario : {USUARIO.usuarioNombre}, {USUARIO.usuarioApellido}")
    except Usuario.DoesNotExist as e:
        print(f"USUARIO NO ENCONTRADO en DB") 
        return JsonResponse({'PIN_BAD': False, 'error': str(e)})  

    try:
        # Obtengo el ULTIMO REGISTRO de el USUARIO en cuestion
        ULTIMO_REGISTRO = Registro.objects.filter(regUsuario=USUARIO).latest('regEntrada')
        print(f"Último registro: Entrada - {ULTIMO_REGISTRO.regEntrada}, Salida - {ULTIMO_REGISTRO.regSalida}")

        if ULTIMO_REGISTRO.regSalida is None: 
            #==============================================    SALIDA 
            # Si el ULTIMO REGISTRO no posee Horario de SALIDA, entonces se trata de un request para fichar/registrar la SALIDA
            
            _horas, _minutos = calcular_diferencia_en_horas(utc_time, ULTIMO_REGISTRO.regEntrada)
            TIPO_REGISTRO = "Salida"
            ULTIMO_REGISTRO.regSalida = utc_time  # Guardamos en UTC
            ULTIMO_REGISTRO.minutos = _minutos
            ULTIMO_REGISTRO.horas = _horas
            ULTIMO_REGISTRO.save()

            # actualizando el estado del usuario ( trabajando actualmente = False )
            USUARIO.is_working = False
            USUARIO.save()

            print(f"{GREEN} -- SALIDA , registrada correctamente {local_time.strftime('%H:%M')}{RESET}")
            # CORRECCIÓN: Devolver hora local en la respuesta
            context = f"{USUARIO.usuarioNombre}_{local_time.strftime('%H:%M')}-{TIPO_REGISTRO}"
            return JsonResponse({"PIN_OK": context}, json_dumps_params={'ensure_ascii': False})
        else:
            #==============================================    ENTRADA
            # como el ULTIMO REGISTRO si posee Horario de SALIDA, se procede a crear un nuevo registro/fichaje para el USUARIO en cuestion
            TIPO_REGISTRO = "Entrada"
            Registro.objects.create(
                regUsuario=USUARIO, 
                regEntrada=utc_time,  # Guardamos en UTC
                teclado_asocido=TECLADO_FICHAJE_UTILIZADO
            )
            # actualizando el estado del usuario ( trabajando actualmente = True )
            USUARIO.is_working = True
            USUARIO.save()

            print(f"{GREEN} -- ENTRADA , registrada correctamente {local_time.strftime('%H:%M')}{RESET}")
            # CORRECCIÓN: Devolver hora local en la respuesta
            context = f"{USUARIO.usuarioNombre}_{local_time.strftime('%H:%M')}-{TIPO_REGISTRO}"
            print(f"{CYAN}{context}{RESET}")
            return JsonResponse({"PIN_OK": context}, json_dumps_params={'ensure_ascii': False})

    except Registro.DoesNotExist as e:
        # si el USUARIO en cuestion, no posee ningun registro de ficheje se procede a la creacion del registr (primero de la lista)
        print("El usuario no tiene registros aún.... creando uno!")
        TIPO_REGISTRO = "Entrada"
        Registro.objects.create(
            regUsuario=USUARIO, 
            regEntrada=utc_time,  # Guardamos en UTC
            teclado_asocido=TECLADO_FICHAJE_UTILIZADO
        )
        
        # actualizando el estado del usuario ( trabajando actualmente = True )
        USUARIO.is_working = True
        USUARIO.save()
        
        print(f"{GREEN} -- ENTRADA , registrada correctamente {local_time.strftime('%H:%M')}{RESET}")
        # CORRECCIÓN: Devolver hora local en la respuesta
        context = f"{USUARIO.usuarioNombre}_{local_time.strftime('%H:%M')}-{TIPO_REGISTRO}"
        print(f"{CYAN}{context}{RESET}")
        return JsonResponse({"PIN_OK": context}, json_dumps_params={'ensure_ascii': False})


def calcular_diferencia_en_horas(momento_fin, momento_inicio):
    """
    Calcula la diferencia entre dos momentos en horas y minutos
    """
    # Calcular la diferencia (resulta en un objeto timedelta)
    diferencia = momento_fin - momento_inicio
    print(f"Diferencia (timedelta): {diferencia}")

    # Obtener el total de segundos de la diferencia
    segundos_totales = diferencia.total_seconds()
    print(f"Segundos totales: {segundos_totales}")

    # Convertir los segundos a horas
    horas_con_decimal = round(segundos_totales / 3600, 1)
    minutos_enteros = int(segundos_totales / 60)
    
    # Formatear el resultado para mostrarlo con un decimal
    horas_formateadas = f"{horas_con_decimal:.1f} ({minutos_enteros:.0f}min)"

    print(f"\nDiferencia en horas: {horas_formateadas}")
    return horas_con_decimal, minutos_enteros