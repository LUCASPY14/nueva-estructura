from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    path('movimientos/', views.movimientos_stock, name='movimientos_stock'),
    path('altas/', views.stock_altas, name='stock_altas'),
    path('bajas/', views.stock_bajas, name='stock_bajas'),
    path('crear/', views.crear_movimiento, name='crear_movimiento'),
    path('eliminar/<int:pk>/', views.eliminar_movimiento, name='eliminar_movimiento'),
    
]