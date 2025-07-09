
# fichajeRemoto -> serializers.py 

from rest_framework import serializers
from fichajeRemoto.models import TecladoFichaje

class TecladoFichajeSerializer(serializers.ModelSerializer):

    class Meta:
        model = TecladoFichaje 
        #fields = '__all__'
        #fields = ('pk','IDCode','StoreName', 'StoreShortName', 'StoreDescription', 'StoreEmail' ,'StoreURL', 'StoreAddress' , 'StorePhone','StorePIVA' ,'SubCategory', 'Is_Active', 'Has_Icon','IconURL')
        fields = ('pk','MAC_address', 'IsActive', 'empresa_timeOffset')
        read_only_fields = ['pk','MAC_address'] #  TODOS los otros restantes



