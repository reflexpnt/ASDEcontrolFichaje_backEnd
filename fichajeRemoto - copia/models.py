
# fichajeRemoto -> models.py 

from django.db import models

from datetime import datetime  
from django.utils import timezone
from django.core.validators import MaxValueValidator

# Create your models here.
class Empresa(models.Model):
    
    empresaCodigo = models.IntegerField()
    empresaNombre = models.CharField(max_length=200)
    empresa_timeOffset = models.SmallIntegerField(verbose_name="adjuste horario", default=0)
    
    
    def __str__(self):
        return self.empresaNombre
    

# Create your models here.
class TecladoFichaje(models.Model):
    
    #id = models.SmallIntegerField()
    MAC_address = models.CharField(max_length = 17, default="00:00:00:00:00:00")
    empresa_timeOffset = models.SmallIntegerField(verbose_name="adjuste horario", default=0)
    IsActive = models.BooleanField(default=True )
    lastUpdate = models.DateTimeField(default=timezone.now) 
    empresa_asociada  = models.ForeignKey( Empresa, null=True, on_delete=models.CASCADE, verbose_name="Empresa asociada")
    
    
    def __str__(self):
        
        #return self.MAC_address
        return f"{self.empresa_asociada} [{self.MAC_address}]"
    

class Usuario(models.Model):
    
    usuarioNombre       = models.CharField(verbose_name="Nombre", max_length=200)
    usuarioApellido     = models.CharField(verbose_name="Apellido ", max_length=200)
    usuarioDNI          = models.CharField(default="", verbose_name="DNI", max_length=9)
    usuarioPIN          = models.SmallIntegerField(verbose_name="PIN",unique=True, validators=[MaxValueValidator(9999)])
    is_working          = models.BooleanField(default=False, verbose_name="trabajando ahora mismo")
    
    def save(self, *args, **kwargs):
        # Capitaliza la primera letra del nombre y el apellido
        self.usuarioNombre = self.usuarioNombre.capitalize()
        self.usuarioApellido = self.usuarioApellido.capitalize()
        super().save(*args, **kwargs) # Llama al método save original del modelo

    def __str__(self):
        return f"{self.usuarioNombre} {self.usuarioApellido}" # Mejorado para mostrar nombre y apellido


class Registro(models.Model):

    regUsuario      = models.ForeignKey( Usuario, on_delete=models.CASCADE, verbose_name="Usuario")
    regEntrada      = models.DateTimeField(verbose_name="Entrada")  #(default=timezone.now) 
    regSalida       =  models.DateTimeField(blank=True, null=True, verbose_name="Salida")
    #regEmpresa      = models.ForeignKey( Empresa, on_delete=models.CASCADE, verbose_name="Empresa")
    teclado_asocido = models.ForeignKey( TecladoFichaje, null=True, on_delete=models.CASCADE, verbose_name="Lugar")
    minutos         =  models.SmallIntegerField( default=0,  verbose_name="minutos")
    horas           =  models.DecimalField( max_digits=5, decimal_places=2, default=0.0, verbose_name="horas")
    
    def __str__(self):
        return self.regUsuario.usuarioNombre # + ', ' + self.usuarioApellido

'''
The possible values for on_delete are found in django.db.models:

CASCADE[source]¶
Cascade deletes. Django emulates the behavior of the SQL constraint ON DELETE CASCADE and also deletes the object containing the ForeignKey.

Model.delete() isn’t called on related models, but the pre_delete and post_delete signals are sent for all deleted objects.

PROTECT[source]¶
Prevent deletion of the referenced object by raising ProtectedError, a subclass of django.db.IntegrityError.

RESTRICT[source]¶
'''