from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.dashboard_reportes, name='dashboard'),
    path('ventas/', views.reporte_ventas, name='ventas'),
    path('productos/', views.reporte_productos, name='productos'),
    path('alumnos/', views.reporte_alumnos, name='alumnos'),
    path('financiero/', views.reporte_financiero, name='financiero'),
    path('exportar/<str:tipo>/', views.exportar_reporte, name='exportar'),
]
