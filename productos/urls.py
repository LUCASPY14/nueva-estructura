from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.lista_productos, name='lista'),
    path('crear/', views.crear_producto, name='crear'),
    path('<int:pk>/editar/', views.editar_producto, name='editar'),
    path('<int:pk>/ver/', views.ver_producto, name='ver'),
    path('categorias/', views.lista_categorias, name='categorias'),
    path('stock/', views.control_stock, name='stock'),
    path('precios/', views.actualizar_precios, name='precios'),
]
