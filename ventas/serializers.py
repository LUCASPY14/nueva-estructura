from rest_framework import serializers
from ventas.models import Venta

class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = ['id', 'fecha', 'total', 'descripcion']  # ajustá los campos según tu modelo
