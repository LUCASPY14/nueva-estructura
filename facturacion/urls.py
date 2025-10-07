from django.urls import path
from . import views
from .views import factura_detalle_view, factura_pdf_view


app_name = 'facturacion'
urlpatterns = [
    # Estandarizar nombres de URL
    path('', views.lista_facturas, name='lista'),
    path('crear/', views.crear_factura, name='crear'),
    path('detalle/<int:pk>/', views.detalle_factura, name='detalle'),
    path('pdf/<int:pk>/', views.descargar_pdf, name='pdf'),
    path('eliminar/<int:pk>/', views.eliminar_factura, name='eliminar'),
    
    # Mantener nombres específicos para las vistas de detalle y PDF
    path('<int:factura_id>/', factura_detalle_view, name='factura_detalle'),
    path('<int:factura_id>/pdf/', factura_pdf_view, name='factura_pdf'),
    path('reporte/', views.reporte_facturas, name='reporte'),
]
