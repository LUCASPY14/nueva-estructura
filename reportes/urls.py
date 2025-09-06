from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('ventas/', views.reporte_ventas_pdf, name='reporte_ventas'),
    path('stock/', views.reporte_stock, name='reporte_stock'),
]
