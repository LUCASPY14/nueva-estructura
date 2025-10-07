# URLs que faltan agregar a alumnos/urls.py

# Para el template mis_transacciones.html
path('mis-transacciones/', views.mis_transacciones, name='mis_transacciones'),
path('solicitar-carga-saldo/', views.solicitar_carga_saldo, name='solicitar_carga_saldo'),

# Para dashboards
path('dashboard-padre/', views.dashboard_padre, name='dashboard_padre'),

# Para filtros y búsquedas
path('filtrar-transacciones/', views.filtrar_transacciones, name='filtrar_transacciones'),
