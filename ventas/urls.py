from django.urls import path, include
from . import views
from .api import views as api_views

app_name = 'ventas'

urlpatterns = [
    # Rutas principales
    path('', views.dashboard_ventas, name='lista'),  # Usar dashboard_ventas como vista principal
    path('dashboard/', views.dashboard_ventas, name='dashboard'),
    path('crear/', views.nueva_venta, name='crear'),
    path('pos/', views.pos_view, name='pos'),
    path('detalle/<int:venta_id>/', views.detalle_venta, name='detalle_venta'),
    path('cancelar/<int:venta_id>/', views.cancelar_venta, name='eliminar_venta'),
    
    # Rutas de turnos
    path('turno/abrir/', views.abrir_turno, name='abrir_turno'),
    path('turno/cerrar/', views.cerrar_turno, name='cerrar_turno'),
    path('turno/estado/', views.estado_turno, name='estado_turno'),
    path('turno/<int:turno_id>/resumen/', views.resumen_turno, name='resumen_turno'),
    
    # Gestión de ventas
    path('venta/nueva/', views.nueva_venta, name='nueva_venta'),
    path('venta/<int:venta_id>/', views.detalle_venta, name='detalle_venta'),
    path('venta/<int:venta_id>/cancelar/', views.cancelar_venta, name='cancelar_venta'),
    path('venta/<int:venta_id>/factura/', views.imprimir_factura, name='imprimir_factura'),
    
    # Reportes
    path('reportes/', views.reportes_ventas, name='reportes'),
    path('reportes/caja/<int:caja_id>/', views.reporte_caja, name='reporte_caja'),
    path('reportes/cajero/<int:cajero_id>/', views.reporte_cajero, name='reporte_cajero'),
    path('reportes/diario/', views.reporte_diario, name='reporte_diario'),
    path('reportes/turno/<int:turno_id>/', views.reporte_turno, name='reporte_turno'),
    
    # API REST para el frontend
    path('api/', include([
        path('productos/buscar/', api_views.buscar_productos, name='api_buscar_productos'),
        path('clientes/buscar/', api_views.buscar_clientes, name='api_buscar_clientes'),
        path('venta/procesar/', api_views.procesar_venta, name='api_procesar_venta'),
        path('venta/<int:venta_id>/agregar-item/', api_views.agregar_item_venta, name='api_agregar_item'),
        path('venta/<int:venta_id>/eliminar-item/<int:item_id>/', api_views.eliminar_item_venta, name='api_eliminar_item'),
        path('venta/<int:venta_id>/calcular-total/', api_views.calcular_total_venta, name='api_calcular_total'),
        path('metodos-pago/', api_views.listar_metodos_pago, name='api_metodos_pago'),
        path('estado-caja/', api_views.estado_caja_actual, name='api_estado_caja'),
        path('estadisticas-dashboard/', views.estadisticas_dashboard, name='api_estadisticas_dashboard'),
        path('ventas-por-periodo/<str:periodo>/', views.datos_ventas_por_periodo, name='api_ventas_periodo'),
        path('ventas-en-vivo/', views.datos_ventas_en_vivo, name='api_ventas_en_vivo'),
    ])),
    path('api/reportes/cajas/', views.api_reporte_cajas, name='api_reporte_cajas'),
]
