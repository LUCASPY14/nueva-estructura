from django.urls import path
from .api_views import hijos_del_padre, detalle_alumno

urlpatterns = [
    path('hijos/', hijos_del_padre, name='api_hijos_del_padre'),
    path('hijos/<int:alumno_id>/detalle/', detalle_alumno, name='api_detalle_alumno'),
]
