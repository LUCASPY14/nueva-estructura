from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
# Importación condicional de WeasyPrint\ntry:\n    from weasyprint import HTML\nexcept ImportError:\n    # Fallback para desarrollo\n    HTML = None
from ventas.models import Venta, DetalleVenta
from productos.models import Producto
from alumnos.models import Alumno
from datetime import datetime

def reporte_ventas_pdf(request):
    # Obtener filtros de la request (GET)
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    alumno_id = request.GET.get('alumno_id')
    producto_id = request.GET.get('producto_id')

    ventas = Venta.objects.all().order_by('-fecha')
    if fecha_inicio:
        ventas = ventas.filter(fecha__date__gte=fecha_inicio)
    if fecha_fin:
        ventas = ventas.filter(fecha__date__lte=fecha_fin)
    if alumno_id:
        ventas = ventas.filter(alumno_id=alumno_id)
    if producto_id:
        ventas = ventas.filter(detalles__producto_id=producto_id).distinct()

    # Para mostrar el filtro en el template
    alumnos = Alumno.objects.all()
    productos = Producto.objects.all()

    # Renderizamos el HTML con el contexto
    html_string = render_to_string('reportes/reporte_ventas_pdf.html', {
        'ventas': ventas,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'alumno_id': alumno_id,
        'producto_id': producto_id,
        'alumnos': alumnos,
        'productos': productos,
    })

    # Generamos el PDF con WeasyPrint
    if HTML:\n        pdf = HTML(string=html_string).write_pdf()\n    else:\n        # Fallback para desarrollo\n        return HttpResponse("<h1>Generación de PDF no disponible en desarrollo</h1><p>Instale las dependencias de WeasyPrint para habilitar esta función</p>", content_type="text/html")

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_ventas.pdf"'
    return response

def reporte_stock(request):
    productos = Producto.objects.all().order_by('nombre')
    return render(request, 'reportes/reporte_stock.html', {'productos': productos})
