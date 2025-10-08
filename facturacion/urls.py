from django.urls import path
from . import views

app_name = 'facturacion'

urlpatterns = [
    path('', views.lista_facturas, name='lista'),
    path('crear/', views.crear_factura, name='crear'),
    path('<int:pk>/ver/', views.ver_factura, name='ver'),
    path('electronica/', views.facturacion_electronica, name='electronica'),
    path('reportes/', views.reportes_facturacion, name='reportes'),
]
