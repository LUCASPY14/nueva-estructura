from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

class ReportesVentas:
    
    @staticmethod
    def reporte_diario(fecha=None, caja=None):
        """Reporte de ventas del día"""
        from ventas.models import Venta, Caja, PagoVenta
        
        if not fecha:
            fecha = timezone.now().date()
        
        queryset = Venta.objects.filter(
            fecha__date=fecha,
            estado='completada'
        )
        
        if caja:
            queryset = queryset.filter(turno_cajero__caja=caja)
        
        data = queryset.aggregate(
            total_ventas=Sum('total'),
            cantidad_ventas=Count('id'),
            promedio_venta=Avg('total'),
        )
        
        # Ventas por método de pago
        pagos_por_metodo = PagoVenta.objects.filter(
            venta__in=queryset
        ).values('metodo').annotate(
            total=Sum('monto'),
            cantidad=Count('id')
        ).order_by('-total')
        
        return {
            'fecha': fecha,
            'caja': caja,
            'resumen': data,
            'pagos_por_metodo': list(pagos_por_metodo),
            'ventas': queryset.order_by('-fecha')[:20]
        }
    
    @staticmethod
    def reporte_turno(turno_id):
        """Reporte detallado de un turno"""
        from ventas.models import TurnoCajero
        
        try:
            turno = TurnoCajero.objects.get(id=turno_id)
        except TurnoCajero.DoesNotExist:
            return None
        
        ventas = turno.ventas.filter(estado='completada')
        
        return {
            'turno': turno,
            'total_ventas': turno.total_ventas,
            'cantidad_ventas': turno.cantidad_ventas,
            'ventas': ventas.order_by('-fecha')
        }
    
    @staticmethod
    def reporte_productos_vendidos(fecha_inicio=None, fecha_fin=None):
        """Reporte de productos más vendidos"""
        from ventas.models import Venta
        
        if not fecha_inicio:
            fecha_inicio = timezone.now().date() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = timezone.now().date()
        
        productos = Venta.objects.filter(
            fecha__date__range=[fecha_inicio, fecha_fin],
            estado='completada'
        ).values(
            'items__producto__nombre',
            'items__producto__codigo',
            'items__producto__precio_venta'
        ).annotate(
            cantidad_vendida=Sum('items__cantidad'),
            total_vendido=Sum('items__subtotal'),
            ventas_count=Count('items__venta', distinct=True)
        ).order_by('-cantidad_vendida')
        
        return {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'productos': list(productos)
        }

class ReportesInventario:
    
    @staticmethod
    def reporte_stock_bajo():
        """Productos con stock bajo"""
        from productos.models import Producto
        
        productos_bajo_stock = Producto.objects.filter(
            cantidad__lte=models.F('stock_minimo')
        ).order_by('cantidad')
        
        return {
            'productos': productos_bajo_stock,
            'total_productos': productos_bajo_stock.count()
        }
    
    @staticmethod
    def reporte_movimientos_stock(fecha_inicio=None, fecha_fin=None):
        """Reporte de movimientos de stock"""
        from productos.models import MovimientoStock
        
        if not fecha_inicio:
            fecha_inicio = timezone.now().date() - timedelta(days=7)
        if not fecha_fin:
            fecha_fin = timezone.now().date()
        
        movimientos = MovimientoStock.objects.filter(
            fecha__date__range=[fecha_inicio, fecha_fin]
        ).select_related('producto', 'usuario').order_by('-fecha')
        
        return {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'movimientos': movimientos
        }

class ReportesCaja:
    
    @staticmethod
    def reporte_cajas_diario(fecha=None):
        """Reporte comparativo de cajas del día"""
        from ventas.models import Caja, Venta, TurnoCajero
        
        if not fecha:
            fecha = timezone.now().date()
        
        cajas_data = []
        for caja in Caja.objects.filter(activa=True):
            ventas = Venta.objects.filter(
                fecha__date=fecha,
                turno_cajero__caja=caja,
                estado='completada'
            )
            
            data = ventas.aggregate(
                total_ventas=Sum('total'),
                cantidad_ventas=Count('id')
            )
            
            turnos = TurnoCajero.objects.filter(
                caja=caja,
                fecha_inicio__date=fecha
            )
            
            cajas_data.append({
                'caja': caja,
                'total_ventas': data['total_ventas'] or Decimal('0'),
                'cantidad_ventas': data['cantidad_ventas'] or 0,
                'turnos_count': turnos.count(),
                'turnos_activos': turnos.filter(activa=True).count()
            })
        
        return {
            'fecha': fecha,
            'cajas': cajas_data
        }

class ReportesAlumnos:
    
    @staticmethod
    def reporte_saldos_alumnos():
        """Reporte de saldos de alumnos"""
        from alumnos.models import Alumno
        
        alumnos_con_saldo = Alumno.objects.filter(
            saldo__gt=0
        ).order_by('-saldo')
        
        total_saldos = alumnos_con_saldo.aggregate(
            total=Sum('saldo')
        )['total'] or Decimal('0')
        
        return {
            'alumnos': alumnos_con_saldo,
            'total_saldos': total_saldos,
            'cantidad_alumnos': alumnos_con_saldo.count()
        }
    
    @staticmethod
    def reporte_transacciones_periodo(fecha_inicio=None, fecha_fin=None):
        """Reporte de transacciones de alumnos por período"""
        from alumnos.models import TransaccionSaldo
        
        if not fecha_inicio:
            fecha_inicio = timezone.now().date() - timedelta(days=30)
        if not fecha_fin:
            fecha_fin = timezone.now().date()
        
        transacciones = TransaccionSaldo.objects.filter(
            fecha__date__range=[fecha_inicio, fecha_fin]
        ).select_related('alumno').order_by('-fecha')
        
        resumen = transacciones.aggregate(
            total_ingresos=Sum('monto', filter=Q(tipo='ingreso')),
            total_gastos=Sum('monto', filter=Q(tipo='gasto')),
            cantidad_transacciones=Count('id')
        )
        
        return {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'transacciones': transacciones,
            'resumen': resumen
        }