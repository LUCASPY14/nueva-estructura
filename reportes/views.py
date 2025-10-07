from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
from django.views.decorators.http import require_http_methods

from ventas.models import Venta, DetalleVenta
from alumnos.models import Alumno
from productos.models import Producto, Categoria
from usuarios.views import es_admin, es_admin_o_cajero
from .generators import VentasReportGenerator, InventarioReportGenerator

# Función utilitaria para convertir fechas a string para JSON
def fecha_a_string(fecha):
    return fecha.strftime('%d/%m/%Y')

# Vista principal de reportes
@login_required
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def reportes_lista(request):
    context = {
        'page_title': 'Reportes y Análisis',
        'back_url': reverse('usuarios:dashboard_admin'),
    }
    return render(request, 'reportes/reportes_lista.html', context)

# Formulario para reporte de ventas
@login_required
@user_passes_test(es_admin_o_cajero, login_url='usuarios:login_simple')
def reporte_ventas_form(request):
    alumnos = Alumno.objects.all().order_by('nombre', 'apellido')
    context = {
        'alumnos': alumnos,
    }
    return render(request, 'reportes/reporte_ventas_form.html', context)

# Generación de reportes
@login_required
@user_passes_test(es_admin_o_cajero, login_url='usuarios:login_simple')
@require_http_methods(["POST"])
def generar_reporte(request):
    """
    Vista para generar reportes en diferentes formatos.
    Soporta PDF y Excel.
    """
    tipo_reporte = request.POST.get('tipo')
    formato = request.POST.get('formato', 'pdf')
    fecha_inicio = datetime.strptime(request.POST.get('fecha_inicio'), '%Y-%m-%d')
    fecha_fin = datetime.strptime(request.POST.get('fecha_fin'), '%Y-%m-%d')
    
    # Seleccionar el generador apropiado
    generators = {
        'ventas': VentasReportGenerator,
        'inventario': InventarioReportGenerator,
    }
    
    generator_class = generators.get(tipo_reporte)
    if not generator_class:
        return JsonResponse({'error': 'Tipo de reporte no válido'}, status=400)
    
    # Crear instancia del generador
    generator = generator_class(fecha_inicio, fecha_fin)
    
    # Generar datos
    data = generator.generate_data()
    
    # Generar reporte en el formato solicitado
    if formato == 'pdf':
        pdf_content = generator.generate_pdf(data)
        response = HttpResponse(pdf_content, content_type='application/pdf')
        filename = f'reporte_{tipo_reporte}_{fecha_inicio.strftime("%Y%m%d")}.pdf'
    else:  # Excel
        excel_content = generator.generate_excel(data)
        response = HttpResponse(excel_content, content_type='application/vnd.ms-excel')
        filename = f'reporte_{tipo_reporte}_{fecha_inicio.strftime("%Y%m%d")}.xlsx'
    
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
    # Obtener parámetros
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    alumno_id = request.GET.get('alumno')
    formato = request.GET.get('formato', 'html')
    
    # Convertir fechas
    fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
    fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    
    # Filtrar ventas
    ventas = Venta.objects.filter(fecha__gte=fecha_inicio, fecha__lte=fecha_fin).order_by('-fecha')
    
    # Filtrar por alumno si se especificó
    alumno = None
    if alumno_id:
        alumno = Alumno.objects.get(id=alumno_id)
        ventas = ventas.filter(alumno=alumno)
    
    # Calcular totales
    total_ventas = ventas.count()
    total_monto = ventas.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    total_productos = DetalleVenta.objects.filter(venta__in=ventas).aggregate(total=Sum('cantidad'))['total'] or 0
    promedio = total_monto / total_ventas if total_ventas > 0 else Decimal('0.00')
    
    # Preparar datos para gráficos
    fechas_grafico = []
    montos_grafico = []
    
    # Calcular ventas por día para el gráfico
    fecha_actual = fecha_inicio.date()
    while fecha_actual <= fecha_fin.date():
        ventas_dia = ventas.filter(fecha__date=fecha_actual)
        monto_dia = ventas_dia.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        
        fechas_grafico.append(fecha_actual.strftime('%d/%m/%Y'))
        montos_grafico.append(float(monto_dia))
        
        fecha_actual += timedelta(days=1)
    
    # Productos más vendidos
    productos_vendidos = (DetalleVenta.objects
                         .filter(venta__in=ventas)
                         .values('producto__nombre')
                         .annotate(total=Sum('cantidad'))
                         .order_by('-total')[:5])
    
    productos_nombres = [p['producto__nombre'] for p in productos_vendidos]
    productos_cantidades = [p['total'] for p in productos_vendidos]
    
    # Preparar contexto
    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'alumno': alumno,
        'total_ventas': total_ventas,
        'total_monto': total_monto,
        'total_productos': total_productos,
        'promedio': promedio,
        'ventas': ventas,
        'fechas_grafico': json.dumps(fechas_grafico),
        'montos_grafico': json.dumps(montos_grafico),
        'productos_nombres': json.dumps(productos_nombres),
        'productos_cantidades': json.dumps(productos_cantidades),
    }
    
    # Manejar diferentes formatos de salida
    if formato == 'pdf':
        return generar_pdf_reporte('reportes/reporte_ventas_resultado.html', context, f"Reporte_Ventas_{fecha_inicio_str}_{fecha_fin_str}")
    elif formato == 'csv':
        return generar_csv_ventas(ventas, f"Reporte_Ventas_{fecha_inicio_str}_{fecha_fin_str}")
    else:
        return render(request, 'reportes/reporte_ventas_resultado.html', context)

# Reporte de stock/inventario
@login_required
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def reporte_stock(request):
    formato = request.GET.get('formato', 'html')
    
    # Obtener todos los productos
    productos = Producto.objects.all().order_by('nombre')
    
    # Calcular valor del inventario
    for producto in productos:
        producto.valor_inventario = producto.cantidad * producto.precio_costo
    
    # Filtrar productos bajos en stock (menos de 10 unidades)
    productos_bajo_stock = productos.filter(cantidad__lt=10)
    
    # Calcular totales
    total_productos = productos.count()
    total_categorias = Categoria.objects.count()
    productos_bajos = productos_bajo_stock.count()
    valor_total = sum(p.valor_inventario for p in productos)
    
    context = {
        'productos': productos,
        'productos_bajo_stock': productos_bajo_stock,
        'total_productos': total_productos,
        'total_categorias': total_categorias,
        'productos_bajos': productos_bajos,
        'valor_total': valor_total,
    }
    
    # Manejar diferentes formatos de salida
    if formato == 'pdf':
        return generar_pdf_reporte('reportes/reporte_stock.html', context, "Reporte_Inventario")
    elif formato == 'csv':
        return generar_csv_inventario(productos, "Reporte_Inventario")
    else:
        return render(request, 'reportes/reporte_stock.html', context)

# Formulario para reporte de alumnos
@login_required
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def reporte_alumnos_form(request):
    return render(request, 'reportes/reporte_alumnos_form.html')

# Resultado de reporte de alumnos
@login_required
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def reporte_alumnos_resultado(request):
    # Implementar lógica similar a la de reporte de ventas
    grado = request.GET.get('grado')
    saldo_min = request.GET.get('saldo_min')
    saldo_max = request.GET.get('saldo_max')
    formato = request.GET.get('formato', 'html')
    
    # Filtrar alumnos
    alumnos = Alumno.objects.all().order_by('apellido', 'nombre')
    
    if grado and grado != 'todos':
        alumnos = alumnos.filter(grado=grado)
    
    if saldo_min:
        alumnos = alumnos.filter(saldo__gte=Decimal(saldo_min))
    
    if saldo_max:
        alumnos = alumnos.filter(saldo__lte=Decimal(saldo_max))
    
    # Calcular estadísticas
    total_alumnos = alumnos.count()
    saldo_total = alumnos.aggregate(total=Sum('saldo'))['total'] or Decimal('0.00')
    saldo_promedio = saldo_total / total_alumnos if total_alumnos > 0 else Decimal('0.00')
    
    # Calcular datos por grado
    grados_data = (
        alumnos.values('grado')
        .annotate(
            count=Count('id'),
            saldo_total=Sum('saldo'),
        )
        .order_by('grado')
    )
    
    grados_nombres = []
    grados_cantidades = []
    grados_saldos = []
    
    for g in grados_data:
        grado_display = dict(Alumno.GRADO_CHOICES).get(g['grado'], 'Desconocido')
        grados_nombres.append(grado_display)
        grados_cantidades.append(g['count'])
        grados_saldos.append(float(g['saldo_total'] or 0))
    
    context = {
        'alumnos': alumnos,
        'total_alumnos': total_alumnos,
        'saldo_total': saldo_total,
        'saldo_promedio': saldo_promedio,
        'grado_filtrado': grado,
        'saldo_min': saldo_min,
        'saldo_max': saldo_max,
        'grados_nombres': json.dumps(grados_nombres),
        'grados_cantidades': json.dumps(grados_cantidades),
        'grados_saldos': json.dumps(grados_saldos),
    }
    
    # Manejar diferentes formatos de salida
    if formato == 'pdf':
        return generar_pdf_reporte('reportes/reporte_alumnos_resultado.html', context, "Reporte_Alumnos")
    elif formato == 'csv':
        return generar_csv_alumnos(alumnos, "Reporte_Alumnos")
    else:
        return render(request, 'reportes/reporte_alumnos_resultado.html', context)

# Formulario para análisis de ventas por período
@login_required
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def reporte_ventas_periodo_form(request):
    categorias = Categoria.objects.all().order_by('nombre')
    context = {
        'categorias': categorias,
    }
    return render(request, 'reportes/reporte_ventas_periodo_form.html', context)

# Resultado de análisis de ventas por período
@login_required
@user_passes_test(es_admin, login_url='usuarios:login_simple')
def reporte_ventas_periodo_resultado(request):
    # Obtener parámetros
    tipo_analisis = request.GET.get('tipo_analisis', 'diario')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    categoria_id = request.GET.get('categoria')
    formato = request.GET.get('formato', 'html')
    
    # Convertir fechas
    fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
    fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    
    # Filtrar ventas
    ventas = Venta.objects.filter(fecha__gte=fecha_inicio, fecha__lte=fecha_fin)
    
    # Filtrar por categoría si se especificó
    categoria = None
    if categoria_id:
        categoria = Categoria.objects.get(id=categoria_id)
        ventas = ventas.filter(detalles__producto__categoria=categoria).distinct()
    
    # Calcular datos según el tipo de análisis
    datos_periodos = []
    periodos_nombres = []
    periodos_montos = []
    
    if tipo_analisis == 'diario':
        # Análisis diario
        fecha_actual = fecha_inicio.date()
        while fecha_actual <= fecha_fin.date():
            ventas_dia = ventas.filter(fecha__date=fecha_actual)
            total_dia = ventas_dia.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
            count_dia = ventas_dia.count()
            promedio_dia = total_dia / count_dia if count_dia > 0 else Decimal('0.00')
            porcentaje = (total_dia / ventas.aggregate(total=Sum('total'))['total']) * 100 if ventas.count() > 0 else 0
            
            datos_periodos.append({
                'nombre': fecha_actual.strftime('%d/%m/%Y'),
                'ventas': count_dia,
                'total': total_dia,
                'promedio': promedio_dia,
                'porcentaje': porcentaje,
            })
            
            periodos_nombres.append(fecha_actual.strftime('%d/%m/%Y'))
            periodos_montos.append(float(total_dia))
            
            fecha_actual += timedelta(days=1)
        
        mejor_periodo_tipo = "día"
        mejor_periodo = max(datos_periodos, key=lambda x: x['total'])['nombre'] if datos_periodos else "No hay datos"
        
    elif tipo_analisis == 'semanal':
        # Análisis semanal
        semanas = {}
        fecha_actual = fecha_inicio.date()
        
        while fecha_actual <= fecha_fin.date():
            semana = fecha_actual.isocalendar()[1]  # Número de semana del año
            año = fecha_actual.isocalendar()[0]
            semana_key = f"{año}-W{semana}"
            
            if semana_key not in semanas:
                semanas[semana_key] = {
                    'inicio': fecha_actual,
                    'fin': fecha_actual,
                    'ventas': [],
                }
            else:
                semanas[semana_key]['fin'] = fecha_actual
            
            ventas_dia = ventas.filter(fecha__date=fecha_actual)
            for venta in ventas_dia:
                semanas[semana_key]['ventas'].append(venta)
            
            fecha_actual += timedelta(days=1)
        
        for semana_key, datos in semanas.items():
            ventas_semana = datos['ventas']
            total_semana = sum(v.total for v in ventas_semana)
            count_semana = len(ventas_semana)
            promedio_semana = total_semana / count_semana if count_semana > 0 else Decimal('0.00')
            porcentaje = (total_semana / sum(v.total for v in ventas.all())) * 100 if ventas.count() > 0 else 0
            
            nombre_semana = f"{datos['inicio'].strftime('%d/%m')} - {datos['fin'].strftime('%d/%m')}"
            
            datos_periodos.append({
                'nombre': nombre_semana,
                'ventas': count_semana,
                'total': total_semana,
                'promedio': promedio_semana,
                'porcentaje': porcentaje,
            })
            
            periodos_nombres.append(nombre_semana)
            periodos_montos.append(float(total_semana))
        
        mejor_periodo_tipo = "semana"
        mejor_periodo = max(datos_periodos, key=lambda x: x['total'])['nombre'] if datos_periodos else "No hay datos"
        
    else:  # mensual
        # Análisis mensual
        meses = {}
        fecha_actual = fecha_inicio.date()
        
        while fecha_actual <= fecha_fin.date():
            mes_key = f"{fecha_actual.year}-{fecha_actual.month}"
            
            if mes_key not in meses:
                meses[mes_key] = {
                    'nombre': fecha_actual.strftime('%B %Y'),
                    'ventas': [],
                }
            
            ventas_dia = ventas.filter(fecha__date=fecha_actual)
            for venta in ventas_dia:
                meses[mes_key]['ventas'].append(venta)
            
            fecha_actual += timedelta(days=1)
        
        for mes_key, datos in meses.items():
            ventas_mes = datos['ventas']
            total_mes = sum(v.total for v in ventas_mes)
            count_mes = len(ventas_mes)
            promedio_mes = total_mes / count_mes if count_mes > 0 else Decimal('0.00')
            porcentaje = (total_mes / sum(v.total for v in ventas.all())) * 100 if ventas.count() > 0 else 0
            
            datos_periodos.append({
                'nombre': datos['nombre'],
                'ventas': count_mes,
                'total': total_mes,
                'promedio': promedio_mes,
                'porcentaje': porcentaje,
            })
            
            periodos_nombres.append(datos['nombre'])
            periodos_montos.append(float(total_mes))
        
        mejor_periodo_tipo = "mes"
        mejor_periodo = max(datos_periodos, key=lambda x: x['total'])['nombre'] if datos_periodos else "No hay datos"
    
    # Productos más vendidos
    productos_vendidos = (DetalleVenta.objects
                         .filter(venta__in=ventas)
                         .values('producto__nombre')
                         .annotate(total=Sum('cantidad'))
                         .order_by('-total')[:5])
    
    productos_nombres = [p['producto__nombre'] for p in productos_vendidos]
    productos_cantidades = [p['total'] for p in productos_vendidos]
    
    # Ventas por categoría
    categorias_ventas = (DetalleVenta.objects
                         .filter(venta__in=ventas)
                         .values('producto__categoria__nombre')
                         .annotate(total=Sum(F('cantidad') * F('precio_unitario')))
                         .order_by('-total'))
    
    categorias_nombres = [c['producto__categoria__nombre'] or 'Sin categoría' for c in categorias_ventas]
    categorias_montos = [float(c['total']) for c in categorias_ventas]
    
    # Calcular totales
    total_ventas = ventas.count()
    total_monto = ventas.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    # Promedio diario
    dias = (fecha_fin.date() - fecha_inicio.date()).days + 1
    promedio_diario = total_monto / dias if dias > 0 else Decimal('0.00')
    
    context = {
        'tipo_analisis': tipo_analisis,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'categoria': categoria,
        'total_ventas': total_ventas,
        'total_monto': total_monto,
        'promedio_diario': promedio_diario,
        'mejor_periodo_tipo': mejor_periodo_tipo,
        'mejor_periodo': mejor_periodo,
        'datos_periodos': datos_periodos,
        'periodos_nombres': json.dumps(periodos_nombres),
        'periodos_montos': json.dumps(periodos_montos),
        'productos_nombres': json.dumps(productos_nombres),
        'productos_cantidades': json.dumps(productos_cantidades),
        'categorias_nombres': json.dumps(categorias_nombres),
        'categorias_montos': json.dumps(categorias_montos),
    }
    
    # Manejar diferentes formatos de salida
    if formato == 'pdf':
        return generar_pdf_reporte('reportes/reporte_ventas_periodo_resultado.html', context, 
                                   f"Analisis_Ventas_{tipo_analisis}_{fecha_inicio_str}_{fecha_fin_str}")
    elif formato == 'csv':
        return generar_csv_analisis_periodo(datos_periodos, 
                                           f"Analisis_Ventas_{tipo_analisis}_{fecha_inicio_str}_{fecha_fin_str}")
    else:
        return render(request, 'reportes/reporte_ventas_periodo_resultado.html', context)

# Generar reporte de ventas en PDF
@login_required
@user_passes_test(es_admin_o_cajero, login_url='usuarios:login_simple')
def reporte_ventas_pdf(request):
    venta_id = request.GET.get('id')
    
    if venta_id:
        # Generar ticket/recibo de una venta específica
        venta = Venta.objects.get(id=venta_id)
        context = {
            'venta': venta,
            'detalles': venta.detalles.all(),
            'fecha_impresion': timezone.now(),
        }
        return generar_pdf_reporte('reportes/ticket_venta.html', context, f"Ticket_Venta_{venta_id}")
    else:
        # Redirigir al formulario de reporte
        return redirect('reportes:reporte_ventas_form')

# Funciones auxiliares para generar reportes en diferentes formatos

def generar_pdf_reporte(template_name, context, filename):
    """Genera un PDF a partir de un template HTML."""
    html_string = render_to_string(template_name, context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    result = html.write_pdf()
    
    # Crear respuesta HTTP
    response = HttpResponse(result, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response

def generar_csv_ventas(ventas, filename):
    """Genera un archivo CSV con los datos de ventas."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Fecha', 'Alumno', 'Total', 'Productos'])
    
    for venta in ventas:
        writer.writerow([
            venta.id,
            venta.fecha.strftime('%d/%m/%Y %H:%M'),
            str(venta.alumno),
            float(venta.total),
            venta.detalles.count()
        ])
    
    return response

def generar_csv_inventario(productos, filename):
    """Genera un archivo CSV con los datos de inventario."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Nombre', 'Categoría', 'Cantidad', 'Precio Venta', 'Precio Costo', 'Valor Inventario'])
    
    for producto in productos:
        writer.writerow([
            producto.id,
            producto.nombre,
            producto.categoria.nombre if producto.categoria else '-',
            producto.cantidad,
            float(producto.precio_venta),
            float(producto.precio_costo),
            float(producto.valor_inventario)
        ])
    
    return response

def generar_csv_alumnos(alumnos, filename):
    """Genera un archivo CSV con los datos de alumnos."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Nombre', 'Apellido', 'Grado', 'Padre/Tutor', 'Saldo'])
    
    for alumno in alumnos:
        writer.writerow([
            alumno.id,
            alumno.nombre,
            alumno.apellido,
            alumno.get_grado_display(),
            alumno.padre.username if alumno.padre else '-',
            float(alumno.saldo)
        ])
    
    return response

def generar_csv_analisis_periodo(datos_periodos, filename):
    """Genera un archivo CSV con los datos de análisis por período."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Período', 'Ventas', 'Total', 'Promedio', '% del Total'])
    
    for periodo in datos_periodos:
        writer.writerow([
            periodo['nombre'],
            periodo['ventas'],
            float(periodo['total']),
            float(periodo['promedio']),
            float(periodo['porcentaje'])
        ])
    
    return response

@login_required
def dashboard_reportes(request):
    """Dashboard principal de reportes"""
    hoy = timezone.now().date()
    
    # Datos rápidos para el dashboard
    reporte_ventas_hoy = ReportesVentas.reporte_diario(hoy)
    reporte_cajas = ReportesCaja.reporte_cajas_diario(hoy)
    
    context = {
        'ventas_hoy': reporte_ventas_hoy,
        'cajas_hoy': reporte_cajas,
        'fecha_actual': hoy
    }
    
    return render(request, 'reportes/dashboard.html', context)

@login_required
def reporte_productos_vendidos(request):
    """Vista para productos más vendidos"""
    dias = int(request.GET.get('dias', 30))
    fecha_fin = timezone.now().date()
    fecha_inicio = fecha_fin - timedelta(days=dias)
    
    reporte = ReportesVentas.reporte_productos_vendidos(fecha_inicio, fecha_fin)
    
    return render(request, 'reportes/productos_vendidos.html', {
        'reporte': reporte,
        'dias': dias
    })

@login_required
def reporte_stock_bajo(request):
    """Vista para productos con stock bajo"""
    reporte = ReportesInventario.reporte_stock_bajo()
    
    return render(request, 'reportes/stock_bajo.html', {
        'reporte': reporte
    })

@login_required
def reporte_saldos_alumnos(request):
    """Vista para saldos de alumnos"""
    reporte = ReportesAlumnos.reporte_saldos_alumnos()
    
    return render(request, 'reportes/saldos_alumnos.html', {
        'reporte': reporte
    })

from django.shortcuts import render
from django.http import HttpResponse

def dashboard_reportes(request):
    """Vista temporal para reportes"""
    return HttpResponse("Reportes en desarrollo")
