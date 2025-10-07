from django.urls import path
from . import views, notification_views, export_views, barcode_views

app_name = 'productos'

urlpatterns = [
    # Productos - nombres de URL estandarizados pero usando las funciones existentes
    path('lista/', views.lista_productos, name='lista'),
    path('crear/', views.crear_producto, name='crear'),
    path('editar/<int:pk>/', views.editar_producto, name='editar'),
    path('detalle/<int:pk>/', views.detalle_producto, name='detalle'),
    path('eliminar/<int:pk>/', views.eliminar_producto, name='eliminar'),
    
    # Categorías
    path('categorias/', views.lista_categorias, name='categorias_lista'),
    path('categorias/crear/', views.crear_categoria, name='categorias_crear'),
    path('categorias/editar/<int:pk>/', views.editar_categoria, name='categorias_editar'),
    
    # Movimientos de stock
    path('movimientos/', views.historial_movimientos, name='movimientos_lista'),
    path('movimientos/registrar/', views.registrar_movimiento, name='movimientos_crear'),
    
    # APIs
    path('api/stock-alerts/', views.stock_alerts_api, name='api_stock_alerts'),
    
    # Notificaciones
    path('notificaciones/', notification_views.lista_notificaciones, name='lista_notificaciones'),
    path('notificaciones/<int:pk>/marcar-leida/', notification_views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    path('notificaciones/no-leidas/', notification_views.notificaciones_no_leidas, name='notificaciones_no_leidas'),
    
    # Exportaciones
    path('exportar/', export_views.exportar_productos, name='exportar_productos'),
    path('exportar/movimientos/', export_views.exportar_movimientos, name='exportar_movimientos'),
    
    # Códigos de barras
    path('<int:producto_id>/generar-ean13/', barcode_views.generar_ean13, name='generar_ean13'),
    path('generar-ean13-bulk/', barcode_views.generar_ean13_bulk, name='generar_ean13_bulk'),
    path('escanear/', barcode_views.escanear_codigo, name='escanear_codigo'),
    path('procesar-codigo/', barcode_views.procesar_codigo, name='procesar_codigo'),
]
