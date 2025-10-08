from django.urls import path
from . import views

app_name = 'configuracion'

urlpatterns = [
    path('', views.configuracion_general, name='general'),
    path('sistema/', views.configuracion_sistema, name='sistema'),
    path('notificaciones/', views.configuracion_notificaciones, name='notificaciones'),
    path('backup/', views.backup_sistema, name='backup'),
    path('usuarios/', views.configuracion_usuarios, name='usuarios'),
]
