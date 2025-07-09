
# fichajeRemoto -> api.py

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



import asyncio



#https://blog.logrocket.com/using-react-django-create-app-tutorial/#diving-into-django-rest-api


from fichajeRemoto.serializers import *
from fichajeRemoto.models import TecladoFichaje, Usuario, Registro, Empresa

from datetime import datetime, timedelta
from django.utils import timezone
#from singletonDJ.models import SiteSingleton

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

#SINGLETON = SiteSingleton.load()

##  -------------------------   ROOM  ---------------------------
##

# curl  -H "Content-Type: application/json" -X POST http://localhost:8000/api/totem/ -d "{\"number\":98, \"floorAttached\":8}"
# curl  -H "Content-Type: application/json" -X POST http://localhost:8000/api/totem/ -d "{\"number\":98, \"floorAttached\":8}" -u admin:admin

##   SI el serializer.save() esta habilitado , RE HACE EL SVG tambien





#  http://127.0.0.1:8000/api/room/



@api_view(['GET']) 
#@user_passes_test(lambda u: u.is_deviceAcount)#  solo acceden los device con su Account
#@authentication_classes([SessionAuthentication, BasicAuthentication])
#@permission_classes([IsAuthenticated])
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
            #serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''
El problema es que Django está escapando los caracteres especiales (acentos) en el JSON. Para solucionarlo, necesitas configurar el JsonResponse para que no escape los caracteres Unicode:API Django con fechas en españolCódigo ∙ Versión 2     return JsonResponse({'serverOK': date_time_str}, json_dumps_params={'ensure_ascii': False})El cambio clave es agregar json_dumps_params={'ensure_ascii': False} al JsonResponse. Esto le dice a Django que no convierta los caracteres Unicode (como los acentos) a secuencias de escape.
JSON_DUMPS_PARAMS = {
    'ensure_ascii': False,
}
'''
def checkserver(request, mac_address):
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
    
    get_TIME = timezone.now()
    
    
    teclado_instancia = None
    #floor_instace = TecladoFichaje.objects.all()[0]
    empresa_asociada_temp = Empresa.objects.all()[0]

    try:
        teclado_instancia = TecladoFichaje.objects.get(MAC_address=mac_address)        
        teclado_instancia.lastUpdate = timezone.now() 
        teclado_instancia.IsActive = True
    except ObjectDoesNotExist:
        teclado_instancia = TecladoFichaje.objects.update_or_create(
            MAC_address=mac_address, 
            lastUpdate=get_TIME,
            empresa_asociada =  empresa_asociada_temp
        )#[0]
    
    # Formatear fecha manualmente en español
    dia_semana = DIAS_SEMANA[get_TIME.strftime("%A")]
    mes = MESES[get_TIME.strftime("%B")].upper()
    
    date_time_str = f"{dia_semana}_{get_TIME.day:02d}-{mes}-{get_TIME.year}_{get_TIME.strftime('%H:%M:%S')}"
    print(f"{CYAN}{date_time_str}{RESET}")
    return JsonResponse({'serverOK': date_time_str})



def validatepin(request, mac_address):
    PIN = None
    TECLADO_FICHAJE_UTILIZADO = None
    USUARIO = None
    ULTIMO_REGISTRO = None
    TIPO_REGISTRO = None    # 'Entrada' / 'Salida'
    ACTUAL_TIME = timezone.now()

    try:
        data = json.loads(request.body)
        PIN = data.get('pin', '')
        print(f"PIN : {PIN}") 
    except Exception as e:
        print(f"Error al parsear JSON: {str(e)}") 
        return JsonResponse({'PIN_BAD': False, 'error': str(e)})

    try:
        TECLADO_FICHAJE_UTILIZADO = TecladoFichaje.objects.get(MAC_address=mac_address)        
        TECLADO_FICHAJE_UTILIZADO.lastUpdate = timezone.now() 
        TECLADO_FICHAJE_UTILIZADO.IsActive = True
        TECLADO_FICHAJE_UTILIZADO.save()
    except TecladoFichaje.DoesNotExist as e:
        # utilizo teclado REMOTO
        TECLADO_FICHAJE_UTILIZADO = TecladoFichaje.objects.get_or_create(MAC_address="00:00:00:00:00:00", empresa_timeOffset= 0, IsActive=True, lastUpdate=timezone.now())

        #print(f"TECLADO NO ENCONTRADO en DB") 
        #return JsonResponse({'PIN_BAD': False, 'error': str(e)})  

    try:
        USUARIO = Usuario.objects.get(usuarioPIN=PIN)        
        print(f"usuario : {USUARIO.usuarioNombre}, {USUARIO.usuarioApellido}")
    except Usuario.DoesNotExist as e:
        print(f"USUARIO NO ENCONTRADO en DB") 
        return JsonResponse({'PIN_BAD': False, 'error': str(e)})  

    #empresa_Temp = Empresa.objects.all()[0]

    try:
        # Obtengo el ULTIMO REGISTRO de el USUARIO en cuestion
        ULTIMO_REGISTRO = Registro.objects.filter(regUsuario=USUARIO).latest('regEntrada')
        print(f"Último registro: Entrada - {ULTIMO_REGISTRO.regEntrada}, Salida - {ULTIMO_REGISTRO.regSalida}")

        if ULTIMO_REGISTRO.regSalida is None: 
            #==============================================    SALIDA 
            # Si el ULTIMO REGISTRO no posee Horario de SALIDA, entoces se trata de un request para fichar/registrar la SALIDA
            
            _horas, _minutos = calcular_diferencia_en_horas( ACTUAL_TIME , ULTIMO_REGISTRO.regEntrada)
            TIPO_REGISTRO = "Salida"
            ULTIMO_REGISTRO.regSalida = ACTUAL_TIME
            ULTIMO_REGISTRO.minutos =_minutos
            ULTIMO_REGISTRO.horas = _horas
            ULTIMO_REGISTRO.save()

            # actualizando el estado del usuario ( trabajando actualmente = False )
            USUARIO.is_working = False
            USUARIO.save()

            
            

            print(f"{GREEN} -- SALIDA , registrada correctamente {ACTUAL_TIME.strftime('%H:%M')}{RESET}")
            context = f"{USUARIO.usuarioNombre}_{ACTUAL_TIME.strftime('%H:%M')}-{TIPO_REGISTRO}"
            return JsonResponse({"PIN_OK": context})
        else:
            #==============================================    ENTRADA
            # como el ULTIMO REGISTRO si posee Horario de SALIDA, se procede a creaer un nuevo registro/fichaje para el USUARIO en cuestion
            TIPO_REGISTRO = "Entrada"
            Registro.objects.create(
                regUsuario=USUARIO, 
                regEntrada=ACTUAL_TIME, 
                teclado_asocido = TECLADO_FICHAJE_UTILIZADO
                #regEmpresa=TECLADO_FICHAJE_UTILIZADO.empresa_asociada
            )
            # actualizando el estado del usuario ( trabajando actualmente = True )
            USUARIO.is_working = True
            USUARIO.save()

            print(f"{GREEN} -- ENTRADA , registrada correctamente {ACTUAL_TIME.strftime('%H:%M')}{RESET}")
            context = f"{USUARIO.usuarioNombre}_{ACTUAL_TIME.strftime('%H:%M')}-{TIPO_REGISTRO}"
            print(f"{CYAN}{context}{RESET}")
            return JsonResponse({"PIN_OK": context})

    except Registro.DoesNotExist as e:
        # si el USUARIO en cuestion, no posee ningun registro de ficheje se procede a la creacion del registr (primero de la lista)
        print("El usuario no tiene registros aún.... creando uno!")
        TIPO_REGISTRO = "Entrada"
        Registro.objects.create(
            regUsuario=USUARIO, 
            regEntrada=ACTUAL_TIME, 
            teclado_asocido = TECLADO_FICHAJE_UTILIZADO
            #regEmpresa=TECLADO_FICHAJE_UTILIZADO.empresa_asociada
        )
        print(f"{GREEN} -- ENTRADA , registrada correctamente {ACTUAL_TIME.strftime('%H:%M')}{RESET}")
        context = f"{USUARIO.usuarioNombre}_{ACTUAL_TIME.strftime('%H:%M')}-{TIPO_REGISTRO}"
        print(f"{CYAN}{context}{RESET}")
        return JsonResponse({"PIN_OK": context})




def calcular_diferencia_en_horas( momento_fin , momento_inicio):
    
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
    horas_formateadas = f"{horas_con_decimal:.1f} ({minutos_enteros:.1f}min)"

    print(f"\nDiferencia en horas: {horas_formateadas}")
    return horas_con_decimal, minutos_enteros


'''
    # current dateTime
    now = datetime.now()

    # convert to string
    date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    print('DateTime String:', date_time_str)

    %d: Returns the day of the month, from 1 to 31.
    %m: Returns the month of the year, from 1 to 12.
    %Y: Returns the year in four-digit format (Year with century). like, 2021.
    %y: Reurns year in two-digit format (year without century). like, 19, 20, 21
    %A: Returns the full name of the weekday. Like, Monday, Tuesday
    %a: Returns the short name of the weekday (First three character.). Like, Mon, Tue
    %B: Returns the full name of the month. Like, June, March
    %b: Returns the short name of the month (First three character.). Like, Mar, Jun
    %H: Returns the hour. from 01 to 23.
    %I: Returns the hour in 12-hours format. from 01 to 12.
    %M: Returns the minute, from 00 to 59.
    %S: Returns the second, from 00 to 59.
    %f: Return the microseconds from 000000 to 999999
    %p: Return time in AM/PM format
    %c: Returns a locale’s appropriate date and time representation
    %x: Returns a locale’s appropriate date representation
    %X: Returns a locale’s appropriate time representation
    %z: Return the UTC offset in the form ±HHMM[SS[.ffffff]] (empty string if the object is naive).
    %Z: Return the Time zone name (empty string if the object is naive).
    %j: Returns the day of the year from 01 to 366
    %w: Returns weekday as a decimal number, where 0 is Sunday and 6 is Saturday.
    %U: Returns the week number of the year (Sunday as the first day of the week) from 00 to 53
    %W: Returns the week number of the year (Monday as the first day of the week) from 00 to 53


    '''
'''

@api_view(['GET', 'PUT']) 
#@user_passes_test(lambda u: u.is_deviceAcount)#  solo acceden los device con su Account
#@authentication_classes([SessionAuthentication, BasicAuthentication])
#@permission_classes([IsAuthenticated])
def room_detail(request, pk):

    room_intance = None
    try:
        room_intance = get_object_or_404(Room, pk=pk)#Room.objects.filter(pk=pk)
    except Room.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

    # ESTA API SOLO DEBE DEVOLVER UNA INSTANCIA (y no un ARRAY de un elemento) , ya que es un GET/PUT a un pk (solamnete uno)
    

    if request.method == 'GET':
        #data = Room.objects.all()
        print(" GET ROOMS")
        room_serializer = RoomSerializer(room_intance, context={'request': request}, many=False)
        #totem_serializer = TotemSerializer(totem_intance, data=request.data,context={'request': request}, many=False)
        return Response(room_serializer.data)

    elif request.method == 'PUT':
        #serializer = RoomSerializer(room_intance, data=request.data,context={'request': request})
        serializer = RoomSerializer(room_intance, data=request.data) #, context={'request': request})
        if serializer.is_valid():
            print("ROOM PUT SAVED")
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'POST':
        #serializer = RoomSerializer(room_intance, data=request.data,context={'request': request})
        serializer = RoomSerializer( data=request.data) #, context={'request': request})
        if serializer.is_valid():
            print("ROOM POST SAVED")
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)#HTTP_200_OK HTTP_201_CREATED
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #elif request.method == 'POST':
    #    serializer = TotemSerializer(data=request.data)
    #    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer = RoomSerializer(data=request.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''



