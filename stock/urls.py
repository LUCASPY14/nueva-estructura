from django.urls import path
from . import views

app_name = 'stock'
urlpatterns = [
    path('', views.stock_list, name='stock_list'),
    path('movimientos/', views.movimientos_list, name='movimientos_list'),
    path('movimientos/crear/', views.crear_movimiento, name='crear_movimiento'),
    path('movimientos/eliminar/<int:pk>/', views.confirmar_eliminar, name='eliminar_movimiento'),
    # <-- aquí las nuevas rutas:
    path('altas/', views.stock_altas, name='stock_altas'),
    path('bajas/', views.stock_bajas, name='stock_bajas'),
]