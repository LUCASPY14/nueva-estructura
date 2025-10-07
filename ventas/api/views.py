from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Q, F
import json
from decimal import Decimal
import logging

from ..models import Venta, DetalleVenta, PagoVenta, TurnoCajero, MetodoPago
from productos.models import Producto
from alumnos.models import Alumno

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["GET"])
def buscar_productos(request):
    """API para buscar productos en el POS"""
    query = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria')
    
    productos = Producto.objects.filter(
        estado='activo',
        cantidad__gt=0
    )
    
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(codigo__icontains=query) |
            Q(descripcion__icontains=query)
        )
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    productos = productos[:20]  # Limitar resultados
    
    data = []
    for producto in productos:
        data.append({
            'id': producto.id,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'precio_venta': float(producto.precio_venta),
            'cantidad_disponible': float(producto.cantidad),
            'categoria': producto.categoria.nombre if producto.categoria else '',
            'imagen_url': producto.imagen.url if producto.imagen else None,
        })
    
    return JsonResponse({'productos': data})

@login_required
@require_http_methods(["GET"])
def buscar_clientes(request):
    """API para buscar clientes en el POS"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'clientes': []})
    
    clientes = Alumno.objects.filter(
        Q(nombre__icontains=query) |
        Q(apellido__icontains=query) |
        Q(numero_telefono__icontains=query),
        activo=True
    )[:10]
    
    data = []
    for cliente in clientes:
        data.append({
            'id': cliente.id,
            'nombre': f"{cliente.nombre} {cliente.apellido}",
            'telefono': cliente.numero_telefono,
            'email': cliente.email,
        })
    
    return JsonResponse({'clientes': data})

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def procesar_venta(request):
    """API para procesar una venta completa"""
    try:
        data = json.loads(request.body)
        
        # Validar datos requeridos
        if not data.get('items'):
            return JsonResponse({'error': 'No hay productos en la venta'}, status=400)
        
        if not data.get('pagos'):
            return JsonResponse({'error': 'No se especificaron métodos de pago'}, status=400)
        
        # Verificar turno activo
        turno_activo = TurnoCajero.objects.filter(
            cajero=request.user,
            activa=True,
            fecha_fin__isnull=True
        ).first()
        
        if not turno_activo:
            return JsonResponse({'error': 'No tienes un turno activo'}, status=400)
        
        with transaction.atomic():
            # Crear venta
            cliente_id = data.get('cliente_id')
            cliente = None
            if cliente_id:
                try:
                    cliente = Alumno.objects.get(id=cliente_id, activo=True)
                except Alumno.DoesNotExist:
                    return JsonResponse({'error': 'Cliente no encontrado'}, status=400)
            
            venta = Venta.objects.create(
                cajero=request.user,
                turno_cajero=turno_activo,
                cliente=cliente,
                descuento=Decimal(str(data.get('descuento', 0))),
                observaciones=data.get('observaciones', '')
            )
            
            # Validar y agregar items
            total_items = Decimal('0')
            items_data = data.get('items', [])
            
            for item_data in items_data:
                try:
                    producto = Producto.objects.select_for_update().get(
                        id=item_data['producto_id'],
                        estado='activo'
                    )
                    cantidad = Decimal(str(item_data['cantidad']))
                    precio_unitario = Decimal(str(item_data.get('precio_unitario', producto.precio_venta)))
                    
                    # Validaciones
                    if cantidad <= 0:
                        raise ValueError(f'Cantidad inválida para {producto.nombre}')
                    
                    if precio_unitario <= 0:
                        raise ValueError(f'Precio inválido para {producto.nombre}')
                    
                    # Verificar stock con bloqueo
                    if producto.cantidad < cantidad:
                        raise ValueError(f'Stock insuficiente para {producto.nombre}. Disponible: {producto.cantidad}')
                    
                    # Crear detalle
                    detalle = DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                        descuento_item=Decimal(str(item_data.get('descuento_item', 0)))
                    )
                    
                    total_items += detalle.subtotal
                    
                    # Actualizar stock
                    producto.cantidad = F('cantidad') - cantidad
                    producto.save(update_fields=['cantidad'])
                    
                except Producto.DoesNotExist:
                    raise ValueError(f'Producto no encontrado: {item_data.get("producto_id")}')
                except (ValueError, TypeError) as e:
                    raise ValueError(f'Error en item: {str(e)}')
            
            # Validar y procesar pagos
            total_pagos = Decimal('0')
            pagos_data = data.get('pagos', [])
            
            for pago_data in pagos_data:
                try:
                    metodo_pago = MetodoPago.objects.get(
                        id=pago_data['metodo_pago_id'],
                        activo=True
                    )
                    monto = Decimal(str(pago_data['monto']))
                    
                    if monto <= 0:
                        raise ValueError(f'Monto inválido para {metodo_pago.nombre}')
                    
                    # Validar referencia si es requerida
                    referencia = pago_data.get('referencia', '')
                    if metodo_pago.requiere_referencia and not referencia:
                        raise ValueError(f'Se requiere referencia para {metodo_pago.nombre}')
                    
                    PagoVenta.objects.create(
                        venta=venta,
                        metodo_pago=metodo_pago,
                        metodo=pago_data.get('metodo', 'EFECTIVO'),
                        monto=monto,
                        referencia=referencia,
                        observacion=pago_data.get('observacion', '')
                    )
                    
                    total_pagos += monto
                    
                except MetodoPago.DoesNotExist:
                    raise ValueError(f'Método de pago no encontrado: {pago_data.get("metodo_pago_id")}')
            
            # Calcular totales
            venta.calcular_totales()
            
            # Validar que los pagos cubran el total
            if total_pagos < venta.total:
                raise ValueError(f'Los pagos ({total_pagos}) no cubren el total ({venta.total})')
            
            # Procesar venta
            venta.procesar_venta()
            
            logger.info(f"Venta {venta.numero_venta} procesada exitosamente por {request.user}")
            
            return JsonResponse({
                'success': True,
                'venta_id': venta.id,
                'numero_venta': venta.numero_venta,
                'total': float(venta.total),
                'cambio': float(total_pagos - venta.total) if total_pagos > venta.total else 0
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        logger.error(f"Error procesando venta: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def agregar_item_venta(request, venta_id):
    """API para agregar item a una venta"""
    try:
        venta = get_object_or_404(Venta, id=venta_id, cajero=request.user, estado='pendiente')
        data = json.loads(request.body)
        
        producto = Producto.objects.get(id=data['producto_id'])
        cantidad = Decimal(str(data['cantidad']))
        precio_unitario = Decimal(str(data.get('precio_unitario', producto.precio_venta)))
        
        # Verificar stock
        if producto.cantidad < cantidad:
            return JsonResponse({'error': f'Stock insuficiente para {producto.nombre}'}, status=400)
        
        with transaction.atomic():
            item = DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                descuento_item=Decimal(str(data.get('descuento_item', 0)))
            )
            
            venta.calcular_totales()
            venta.save()
            
            return JsonResponse({
                'success': True,
                'item_id': item.id,
                'subtotal': float(item.subtotal),
                'total_venta': float(venta.total)
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def eliminar_item_venta(request, venta_id, item_id):
    """API para eliminar item de una venta"""
    try:
        venta = get_object_or_404(Venta, id=venta_id, cajero=request.user, estado='pendiente')
        item = get_object_or_404(DetalleVenta, id=item_id, venta=venta)
        
        with transaction.atomic():
            item.delete()
            venta.calcular_totales()
            venta.save()
            
            return JsonResponse({
                'success': True,
                'total_venta': float(venta.total)
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def calcular_total_venta(request, venta_id):
    """API para calcular total de una venta"""
    try:
        venta = get_object_or_404(Venta, id=venta_id, cajero=request.user)
        venta.calcular_totales()
        
        return JsonResponse({
            'subtotal': float(venta.subtotal),
            'descuento': float(venta.descuento),
            'total': float(venta.total),
            'items_count': venta.items.count()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def listar_metodos_pago(request):
    """API para listar métodos de pago activos"""
    metodos = MetodoPago.objects.filter(activo=True).order_by('nombre')
    
    data = []
    for metodo in metodos:
        data.append({
            'id': metodo.id,
            'nombre': metodo.nombre,
            'descripcion': metodo.descripcion,
            'requiere_referencia': metodo.requiere_referencia,
        })
    
    return JsonResponse({'metodos_pago': data})

@login_required
@require_http_methods(["GET"])
def estado_caja_actual(request):
    """API para obtener estado de la caja actual"""
    turno = TurnoCajero.objects.filter(
        cajero=request.user,
        activa=True,
        fecha_fin__isnull=True
    ).first()
    
    if not turno:
        return JsonResponse({'error': 'No hay turno activo'}, status=400)
    
    return JsonResponse({
        'turno_id': turno.id,
        'caja': {
            'id': turno.caja.id,
            'numero': turno.caja.numero,
            'nombre': turno.caja.nombre,
        },
        'fecha_inicio': turno.fecha_inicio.isoformat(),
        'monto_inicial': float(turno.monto_inicial),
        'total_ventas': float(turno.total_ventas),
        'cantidad_ventas': turno.cantidad_ventas,
    })

# Agregar estas nuevas funciones:

@login_required
@require_http_methods(["POST"])
def validar_venta_preview(request):
    """API para validar venta antes de procesarla"""
    try:
        data = json.loads(request.body)
        
        # Validar items
        items_data = data.get('items', [])
        if not items_data:
            return JsonResponse({'error': 'No hay productos en la venta'}, status=400)
        
        total_items = Decimal('0')
        items_validados = []
        
        for item_data in items_data:
            try:
                producto = Producto.objects.get(
                    id=item_data['producto_id'],
                    estado='activo'
                )
                cantidad = Decimal(str(item_data['cantidad']))
                precio_unitario = Decimal(str(item_data.get('precio_unitario', producto.precio_venta)))
                descuento_item = Decimal(str(item_data.get('descuento_item', 0)))
                
                if cantidad <= 0:
                    return JsonResponse({'error': f'Cantidad inválida para {producto.nombre}'}, status=400)
                
                if producto.cantidad < cantidad:
                    return JsonResponse({
                        'error': f'Stock insuficiente para {producto.nombre}',
                        'disponible': float(producto.cantidad)
                    }, status=400)
                
                subtotal = (precio_unitario * cantidad) - descuento_item
                total_items += subtotal
                
                items_validados.append({
                    'producto_id': producto.id,
                    'nombre': producto.nombre,
                    'cantidad': float(cantidad),
                    'precio_unitario': float(precio_unitario),
                    'descuento_item': float(descuento_item),
                    'subtotal': float(subtotal)
                })
                
            except Producto.DoesNotExist:
                return JsonResponse({'error': f'Producto no encontrado'}, status=400)
        
        # Calcular descuentos y total
        descuento_general = Decimal(str(data.get('descuento', 0)))
        total_final = total_items - descuento_general
        
        # Validar pagos
        pagos_data = data.get('pagos', [])
        total_pagos = sum(Decimal(str(p['monto'])) for p in pagos_data)
        
        return JsonResponse({
            'valido': True,
            'resumen': {
                'items': items_validados,
                'cantidad_items': len(items_validados),
                'subtotal': float(total_items),
                'descuento_general': float(descuento_general),
                'total': float(total_final),
                'total_pagos': float(total_pagos),
                'cambio': float(total_pagos - total_final) if total_pagos > total_final else 0,
                'falta_pago': float(total_final - total_pagos) if total_pagos < total_final else 0
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def obtener_configuracion_pos(request):
    """API para obtener configuración del POS"""
    from django.conf import settings
    
    return JsonResponse({
        'moneda': getattr(settings, 'MONEDA_PRINCIPAL', 'CLP'),
        'simbolo_moneda': getattr(settings, 'SIMBOLO_MONEDA', '$'),
        'decimales': getattr(settings, 'DECIMALES_MONEDA', 0),
        'permite_descuentos': True,
        'descuento_maximo': 50,  # Porcentaje
        'permite_precios_variables': False,
        'requiere_cliente': False,
        'impresion_automatica': False,
        'sonidos_activos': True,
        'modo_tactil': True
    })