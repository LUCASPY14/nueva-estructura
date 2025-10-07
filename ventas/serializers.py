from decimal import Decimal
from django.core.exceptions import ValidationError
from rest_framework import serializers
from ventas.models import Venta

class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = ['id', 'fecha', 'total', 'descripcion']  # ajustá los campos según tu modelo
    
    """Serializador para datos de venta"""
    
    @staticmethod
    def serialize_venta(venta):
        """Serializar venta completa"""
        return {
            'id': venta.id,
            'numero_venta': venta.numero_venta,
            'fecha': venta.fecha.isoformat(),
            'cajero': {
                'id': venta.cajero.id,
                'username': venta.cajero.username,
                'nombre': f"{venta.cajero.first_name} {venta.cajero.last_name}".strip()
            },
            'caja': {
                'numero': venta.turno_cajero.caja.numero,
                'nombre': venta.turno_cajero.caja.nombre
            },
            'cliente': {
                'id': venta.cliente.id,
                'nombre': f"{venta.cliente.nombre} {venta.cliente.apellido}",
                'telefono': venta.cliente.numero_telefono
            } if venta.cliente else None,
            'items': [VentaSerializer.serialize_detalle(item) for item in venta.items.all()],
            'pagos': [VentaSerializer.serialize_pago(pago) for pago in venta.pagos.all()],
            'subtotal': float(venta.subtotal),
            'descuento': float(venta.descuento),
            'total': float(venta.total),
            'estado': venta.estado,
            'observaciones': venta.observaciones
        }
    
    @staticmethod
    def serialize_detalle(detalle):
        """Serializar detalle de venta"""
        return {
            'id': detalle.id,
            'producto': {
                'id': detalle.producto.id,
                'codigo': detalle.producto.codigo,
                'nombre': detalle.producto.nombre,
                'categoria': detalle.producto.categoria.nombre if detalle.producto.categoria else ''
            },
            'cantidad': float(detalle.cantidad),
            'precio_unitario': float(detalle.precio_unitario),
            'descuento_item': float(detalle.descuento_item),
            'subtotal': float(detalle.subtotal)
        }
    
    @staticmethod
    def serialize_pago(pago):
        """Serializar pago de venta"""
        return {
            'id': pago.id,
            'metodo_pago': {
                'id': pago.metodo_pago.id,
                'nombre': pago.metodo_pago.nombre
            },
            'metodo': pago.metodo,
            'monto': float(pago.monto),
            'referencia': pago.referencia,
            'observacion': pago.observacion
        }

class ProductoSerializer:
    """Serializador para productos"""
    
    @staticmethod
    def serialize_producto(producto):
        """Serializar producto para el POS"""
        return {
            'id': producto.id,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'precio_venta': float(producto.precio_venta),
            'cantidad_disponible': float(producto.cantidad),
            'categoria': {
                'id': producto.categoria.id,
                'nombre': producto.categoria.nombre
            } if producto.categoria else None,
            'imagen_url': producto.imagen.url if producto.imagen else None,
            'permite_descuento': True,  # Configurar según lógica de negocio
            'es_servicio': producto.tipo == 'servicio' if hasattr(producto, 'tipo') else False
        }
