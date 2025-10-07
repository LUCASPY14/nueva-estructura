import os
from datetime import datetime
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.staticfiles import finders
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import xlsxwriter
from io import BytesIO

def exportar_productos_pdf(productos, request):
    """
    Exporta la lista de productos a PDF usando WeasyPrint
    """
    # Configurar fuentes
    font_config = FontConfiguration()
    
    # Renderizar el template HTML
    html_string = render_to_string(
        'productos/exports/productos_pdf.html',
        {'productos': productos, 'fecha': datetime.now()}
    )
    
    # Crear el PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    css = CSS(string='''
        @page { 
            size: letter; 
            margin: 1.5cm;
            @bottom-right {
                content: "Página " counter(page) " de " counter(pages);
            }
        }
    ''')
    
    # Generar el PDF
    pdf_file = html.write_pdf(
        stylesheets=[css],
        font_config=font_config
    )
    
    # Crear la respuesta HTTP
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="productos.pdf"'
    
    return response

def exportar_productos_excel(productos):
    """
    Exporta la lista de productos a Excel usando XlsxWriter
    """
    # Crear un buffer en memoria
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Productos')
    
    # Formatos
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4CAF50',
        'color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    cell_format = workbook.add_format({
        'align': 'left',
        'valign': 'vcenter',
        'border': 1
    })
    
    number_format = workbook.add_format({
        'align': 'right',
        'valign': 'vcenter',
        'border': 1,
        'num_format': '#,##0.00'
    })
    
    # Encabezados
    headers = [
        'Código',
        'Nombre',
        'Categoría',
        'Precio Venta',
        'Precio Compra',
        'Cantidad',
        'Stock Mínimo',
        'Estado'
    ]
    
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Ajustar ancho de columnas
    worksheet.set_column('A:A', 15)  # Código
    worksheet.set_column('B:B', 40)  # Nombre
    worksheet.set_column('C:C', 20)  # Categoría
    worksheet.set_column('D:E', 15)  # Precios
    worksheet.set_column('F:G', 12)  # Cantidades
    worksheet.set_column('H:H', 15)  # Estado
    
    # Datos
    for row, producto in enumerate(productos, start=1):
        worksheet.write(row, 0, producto.codigo, cell_format)
        worksheet.write(row, 1, producto.nombre, cell_format)
        worksheet.write(row, 2, producto.categoria.nombre if producto.categoria else 'Sin Categoría', cell_format)
        worksheet.write(row, 3, producto.precio_venta, number_format)
        worksheet.write(row, 4, producto.precio_compra, number_format)
        worksheet.write(row, 5, producto.cantidad, number_format)
        worksheet.write(row, 6, producto.cantidad_minima, number_format)
        worksheet.write(row, 7, producto.get_estado_display(), cell_format)
    
    # Cerrar el libro
    workbook.close()
    
    # Crear la respuesta HTTP
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="productos.xlsx"'
    
    return response

def exportar_movimientos_excel(movimientos):
    """
    Exporta el historial de movimientos a Excel
    """
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Movimientos')
    
    # Formatos
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#2196F3',
        'color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    cell_format = workbook.add_format({
        'align': 'left',
        'valign': 'vcenter',
        'border': 1
    })
    
    date_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'num_format': 'dd/mm/yyyy hh:mm'
    })
    
    number_format = workbook.add_format({
        'align': 'right',
        'valign': 'vcenter',
        'border': 1,
        'num_format': '#,##0'
    })
    
    # Encabezados
    headers = [
        'Fecha',
        'Producto',
        'Tipo',
        'Cantidad',
        'Usuario',
        'Nota'
    ]
    
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Ajustar ancho de columnas
    worksheet.set_column('A:A', 20)  # Fecha
    worksheet.set_column('B:B', 40)  # Producto
    worksheet.set_column('C:C', 15)  # Tipo
    worksheet.set_column('D:D', 12)  # Cantidad
    worksheet.set_column('E:E', 20)  # Usuario
    worksheet.set_column('F:F', 40)  # Nota
    
    # Datos
    for row, mov in enumerate(movimientos, start=1):
        worksheet.write(row, 0, mov.fecha, date_format)
        worksheet.write(row, 1, mov.producto.nombre, cell_format)
        worksheet.write(row, 2, mov.get_tipo_movimiento_display(), cell_format)
        worksheet.write(row, 3, mov.cantidad, number_format)
        worksheet.write(row, 4, mov.usuario.username, cell_format)
        worksheet.write(row, 5, mov.nota or '', cell_format)
    
    # Cerrar el libro
    workbook.close()
    
    # Crear la respuesta HTTP
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="movimientos.xlsx"'
    
    return response