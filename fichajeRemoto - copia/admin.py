
# fichajeRemoto -> admin.py
from django.contrib import admin
from django.utils.timezone import localtime   # respeta zona horaria del proyecto
from .models import Empresa, TecladoFichaje, Usuario, Registro

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ( "empresaNombre", "pk", "empresaCodigo" , "empresa_timeOffset" ) #
    #readonly_fields=('totem_lastUpdate',)
    #ordering = ('-totem_lastUpdate',)
    #list_display = ("pk", "totem_Number" , "floorAttached", "totem_Layout" ,"totem_MAC_address", "totem_HW_model", "totem_FW_version", "totem_IP", "totem_IsActive",) #
    

@admin.register(TecladoFichaje)
class TecladoFichajeAdmin(admin.ModelAdmin):
    list_display = ( "MAC_address" ,"empresa_asociada", "IsActive" ,  "empresa_timeOffset") #
    #readonly_fields=('totem_lastUpdate',)
    #ordering = ('-totem_lastUpdate',)
    #list_display = ("pk", "totem_Number" , "floorAttached", "totem_Layout" ,"totem_MAC_address", "totem_HW_model", "totem_FW_version", "totem_IP", "totem_IsActive",) #
    


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    #list_display =[f.name for f in Usuario._meta.fields]
    list_display =  ( "usuarioApellido" ,"usuarioNombre", "usuarioDNI" ,  "is_working", "usuarioPIN", "pk")
    
    #readonly_fields=('totem_lastUpdate',)
    #ordering = ('-totem_lastUpdate',)
    #list_display = ("pk", "totem_Number" , "floorAttached", "totem_Layout" ,"totem_MAC_address", "totem_HW_model", "totem_FW_version", "totem_IP", "totem_IsActive",) #
    


@admin.register(Registro)
class RegistroAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "regUsuario",
        "entrada_corta",
        "salida_corta",
        "teclado_asocido",
        "minutos",
        "horas",
    )
    list_filter = ["regUsuario", "teclado_asocido"]
    #readonly_fields = ["horas","minutos"]  # 👈 Este es el campo solo visible
    # --- helpers ---

    def entrada_corta(self, obj):
        return localtime(obj.regEntrada).strftime("%d/%m/%y %H:%M")
    entrada_corta.short_description = "Entrada"
    entrada_corta.admin_order_field = "regEntrada"   # mantiene el ordenado por columna

    def salida_corta(self, obj):
        if obj.regSalida:
            return localtime(obj.regSalida).strftime("%d/%m/%y %H:%M")
        return "—"
    salida_corta.short_description = "Salida"
    salida_corta.admin_order_field = "regSalida"


'''
@admin.register(Registro)
class RegistroAdmin(admin.ModelAdmin):
    list_display =[f.name for f in Registro._meta.fields]
    #search_fields = ['regUsuario', 'teclado_asocido']  
    list_filter = ['regUsuario', 'teclado_asocido']
    
'''

   