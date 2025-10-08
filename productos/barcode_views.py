from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from .models import Producto
from .utils import generate_ean13, is_valid_ean13

@login_required
def generar_ean13(request, producto_id):
    """
    Vista para generar y asignar un código EAN-13 a un producto.
    """
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Si el producto ya tiene un código EAN-13, no generamos uno nuevo
    if producto.ean13:
        messages.warning(request, 'El producto ya tiene un código EAN-13 asignado.')
        return redirect('productos:detalle', producto_id=producto.id)
    
    # Generar un nuevo código EAN-13
    nuevo_ean13 = generate_ean13()
    
    # Asignar el código al producto
    producto.ean13 = nuevo_ean13
    producto.save()
    
    messages.success(request, f'Código EAN-13 {nuevo_ean13} generado y asignado correctamente.')
    return redirect('productos:detalle', producto_id=producto.id)

@login_required
def generar_ean13_bulk(request):
    """
    Vista para generar códigos EAN-13 para todos los productos que no lo tengan.
    """
    productos_sin_ean = Producto.objects.filter(ean13__isnull=True)
    count = 0
    
    for producto in productos_sin_ean:
        producto.ean13 = generate_ean13()
        producto.save()
        count += 1
    
    if count > 0:
        messages.success(request, f'Se generaron códigos EAN-13 para {count} productos.')
    else:
        messages.info(request, 'Todos los productos ya tienen códigos EAN-13 asignados.')
    
    return redirect('productos:lista')

@login_required
def escanear_codigo(request):
    """
    Vista para mostrar la página de escaneo de códigos de barras.
    """
    return render(request, 'productos/escanear_codigo.html')

@login_required
def procesar_codigo(request):
    """
    Vista para procesar un código de barras escaneado y devolver la información del producto.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    codigo = request.POST.get('codigo')
    
    if not codigo:
        return JsonResponse({'error': 'No se proporcionó un código'}, status=400)
    
    # Validar el código EAN-13
    if not is_valid_ean13(codigo):
        return JsonResponse({'error': 'Código EAN-13 inválido'}, status=400)
    
    try:
        producto = Producto.objects.get(ean13=codigo)
        return JsonResponse({
            'id': producto.id,
            'nombre': producto.nombre,
            'codigo': producto.codigo,
            'precio_venta': str(producto.precio_venta),
            'cantidad': producto.cantidad,
            'url': producto.get_absolute_url()
        })
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)

# barcode_views.py - Vista básica para códigos de barras
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from .models import Producto

@login_required
def generar_codigo_barras(request, pk):
    """Vista básica para generar código de barras"""
    producto = get_object_or_404(Producto, pk=pk)
    messages.info(request, "Funcionalidad de código de barras en desarrollo")
    return HttpResponse(f"Código de barras para {producto.nombre} en desarrollo", content_type="text/plain")

@login_required
def imprimir_etiquetas(request):
    """Imprimir etiquetas de productos"""
    messages.info(request, "Funcionalidad de etiquetas en desarrollo")
    return HttpResponse("Impresión de etiquetas en desarrollo", content_type="text/plain")