from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.lista_ventas, name='lista'),
    path('nueva/', views.nueva_venta, name='nueva'),
    path('<int:pk>/ver/', views.ver_venta, name='ver'),
    path('pos/', views.punto_venta, name='pos'),
    path('reportes/', views.reportes_ventas, name='reportes'),
    path('caja/', views.caja_diaria, name='caja'),
    
    # Dashboard y turnos de cajero
    path('dashboard/', views.dashboard_cajero, name='dashboard_cajero'),
    path('turno/abrir/', views.abrir_turno, name='abrir_turno'),
    path('turno/cerrar/', views.cerrar_turno, name='cerrar_turno'),
]
