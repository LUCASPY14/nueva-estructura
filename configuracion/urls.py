from django.urls import path
from .views import configuracion_view

app_name = 'configuracion'

urlpatterns = [
    path('', configuracion_view, name='configuracion'),  # <--- asigna este nombre
    path('editar/', configuracion_view, name='editar_configuracion'),
]
