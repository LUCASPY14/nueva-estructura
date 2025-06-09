from django.db.models import Sum, F, Q
from ventas.models import Venta
from compras.models import Compra
from productos.models import Producto
from alumnos.models import Alumno

# Ventas por período
def get_ventas_por_periodo(start_date, end_date):
    return (
        Venta.objects
            .filter(fecha__date__range=(start_date, end_date))
            .order_by('fecha')
           )

# Compras por período
def get_compras_por_periodo(start_date, end_date):
    return (
        Compra.objects
            .filter(fecha__date__range=(start_date, end_date))
            .order_by('fecha')
        )

# Stock actual
def get_stock_actual():
    return Producto.objects.values('codigo', 'nombre', 'cantidad')

# Consumo por alumno en período
def get_consumo_por_alumno(start_date, end_date):
    return (
        Alumno.objects
            .annotate(
                consumo=Sum(
                    'ventas__total',
                    filter=Q(ventas__fecha__date__range=(start_date, end_date))
                           ))
            .values('nombre', 'padre__nombre', 'consumo'))

# Reporte financiero: ingresos vs egresos
def get_finanzas(start_date, end_date):
    ingresos = (
        Venta.objects
            .filter(fecha__date__range=(start_date, end_date))
            .aggregate(total_ingresos=Sum('total'))
            .get('total_ingresos') or 0  )
    egresos = (
        Compra.objects
            .filter(fecha__date__range=(start_date, end_date))
            .aggregate(total_egresos=Sum('total'))
            .get('total_egresos') or 0   )
    return {
        'ingresos': ingresos,
        'egresos': egresos,
        'balance': ingresos - egresos
    }