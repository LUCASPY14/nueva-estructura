from django.urls import path
from . import views
from .views import factura_detalle_view, factura_pdf_view


app_name = 'facturacion'
urlpatterns = [
    path('lista/', views.lista_facturas, name='lista_facturas'),
    path('crear/', views.crear_factura, name='crear_factura'),
    path('detalle/<int:pk>/', views.detalle_factura, name='detalle_factura'),
    path('pdf/<int:pk>/', views.descargar_pdf, name='descargar_pdf'),
    path('eliminar/<int:pk>/', views.eliminar_factura, name='eliminar_factura'),
    path('<int:factura_id>/', factura_detalle_view, name='factura_detalle'),
    path('<int:factura_id>/pdf/', factura_pdf_view, name='factura_pdf'),
    path('reporte/', views.reporte_facturas, name='reporte_facturas'),
]
