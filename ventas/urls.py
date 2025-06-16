from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('lista/', views.ventas_lista, name='ventas_lista'),
    path('crear/', views.crear_venta, name='crear_venta'),
    path('detalle/<int:pk>/', views.detalle_venta, name='detalle_venta'),
    path('eliminar/<int:pk>/', views.eliminar_venta, name='eliminar_venta'),

    # Reportes visual y PDF
    path('reporte/', views.reporte_ventas_view, name='reporte_ventas'),
    path('reporte/pdf/', views.reporte_ventas_pdf, name='reporte_ventas_pdf'),
]
