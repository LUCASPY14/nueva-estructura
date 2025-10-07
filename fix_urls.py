#!/usr/bin/env python3

# Leer el archivo actual
with open('alumnos/urls.py', 'r') as f:
    content = f.read()

# URLs corregidas
new_urls = '''from django.urls import path
from . import views

app_name = 'alumnos'

urlpatterns = [
    # URLs básicas
    path('', views.lista_alumnos, name='lista'),
    path('crear/', views.crear_alumno, name='crear'),
    
    # URLs de detalle y edición (nombres corregidos para templates)
    path('<int:pk>/', views.detalle_alumno, name='detalle'),
    path('<int:pk>/detalle/', views.detalle_alumno, name='detalle_alumno'),
    path('<int:pk>/editar/', views.editar_alumno, name='editar'),
    path('<int:pk>/editar/', views.editar_alumno, name='editar_alumno'),
    path('<int:pk>/eliminar/', views.eliminar_alumno, name='eliminar'),
    path('<int:pk>/eliminar/', views.eliminar_alumno, name='eliminar_alumno'),
    
    # URLs de saldo
    path('<int:alumno_id>/cargar-saldo/', views.cargar_saldo_tarjeta, name='cargar_saldo'),
    path('<int:pk>/historial/', views.historial_transacciones, name='historial_transacciones'),
    path('consulta-saldo/', views.consulta_saldo, name='consulta_saldo'),
    
    # URLs para padres
    path('padres/', views.lista_padres, name='lista_padres'),
    path('padres/crear/', views.crear_padre, name='crear_padre'),
    
    # URLs para sistema de solicitudes
    path('saldo/solicitar-recarga/', views.solicitar_recarga, name='solicitar_recarga'),
    path('saldo/mis-solicitudes/', views.mis_solicitudes, name='mis_solicitudes'),
    path('saldo/mis-hijos/', views.mis_hijos, name='mis_hijos'),
    
    # URLs específicas para templates
    path('mis-transacciones/', views.mis_transacciones, name='mis_transacciones'),
    path('solicitar-carga-saldo/', views.solicitar_carga_saldo, name='solicitar_carga_saldo'),
    path('filtrar-transacciones/', views.filtrar_transacciones, name='filtrar_transacciones'),
    
    # URLs para administradores
    path('admin/solicitudes-pendientes/', views.solicitudes_pendientes, name='solicitudes_pendientes'),
    path('admin/procesar-solicitud/<int:solicitud_id>/', views.procesar_solicitud, name='procesar_solicitud'),
    path('admin/dashboard-saldo/', views.dashboard_saldo, name='dashboard_saldo'),
    
    # APIs
    path('api/consulta-saldo/', views.api_consulta_saldo, name='api_consulta_saldo'),
    
    # Dashboards
    path('dashboard/padre/', views.dashboard_padre, name='dashboard_padre'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/cajero/', views.dashboard_cajero, name='dashboard_cajero'),
]
'''

# Escribir el archivo corregido
with open('alumnos/urls.py', 'w') as f:
    f.write(new_urls)

print("✅ URLs corregidas y limpias")
