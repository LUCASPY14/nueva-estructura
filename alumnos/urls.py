from django.urls import path
from . import views

app_name = 'alumnos'

urlpatterns = [
    path('', views.lista_alumnos, name='lista'),
    path('crear/', views.crear_alumno, name='crear'),
    path('<int:pk>/editar/', views.editar_alumno, name='editar'),
    path('<int:pk>/ver/', views.ver_alumno, name='ver'),
    path('saldo/', views.consultar_saldo, name='saldo'),
    path('historial/', views.historial_movimientos, name='historial'),
]
