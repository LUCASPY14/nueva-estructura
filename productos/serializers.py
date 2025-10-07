from django.db.models import F, ExpressionWrapper, FloatField, Case, When, Value
from rest_framework import serializers
from .models import Producto, Categoria, MovimientoStock

class CategoriaSerializer(serializers.ModelSerializer):
    productos_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'productos_count']

class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'codigo', 'codigo_barras', 'descripcion',
            'precio_venta', 'precio_compra', 'cantidad', 'cantidad_minima',
            'categoria', 'categoria_nombre', 'estado', 'imagen'
        ]

class MovimientoStockSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    tipo_movimiento_display = serializers.CharField(source='get_tipo_movimiento_display', read_only=True)
    
    class Meta:
        model = MovimientoStock
        fields = [
            'id', 'producto', 'producto_nombre', 'tipo_movimiento',
            'tipo_movimiento_display', 'cantidad', 'fecha', 'usuario',
            'usuario_nombre', 'nota'
        ]
        read_only_fields = ['fecha', 'usuario']

class StockAlertsSerializer:
    @staticmethod
    def get_stock_alerts():
        """
        Obtiene los productos con alertas de stock, incluyendo:
        - Productos con stock bajo del mínimo
        - Productos agotados
        """
        productos = Producto.objects.filter(
            estado='activo'
        ).annotate(
            porcentaje_stock=ExpressionWrapper(
                Case(
                    When(stock_minimo__gt=0, then=F('cantidad') * 100.0 / F('stock_minimo')),
                    default=Value(100.0)
                ),
                output_field=FloatField()
            )
        ).filter(
            porcentaje_stock__lte=100
        ).order_by(
            'porcentaje_stock'
        )

        return [
            {
                'id': prod.id,
                'nombre': prod.nombre,
                'codigo': prod.codigo,
                'categoria': prod.categoria.nombre if prod.categoria else 'Sin Categoría',
                'cantidad': prod.cantidad,
                'stock_minimo': prod.stock_minimo,
                'porcentaje_stock': float(prod.porcentaje_stock),
                'estado': 'agotado' if prod.cantidad == 0 else (
                    'critico' if prod.porcentaje_stock <= 25 else 
                    'bajo' if prod.porcentaje_stock <= 50 else 'advertencia'
                ),
                'prioridad': 1 if prod.cantidad == 0 else (
                    2 if prod.porcentaje_stock <= 25 else
                    3 if prod.porcentaje_stock <= 50 else 4
                )
            }
            for prod in productos
        ]