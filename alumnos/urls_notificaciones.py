from django.urls import path
from . import views_notificaciones as views

app_name = 'notificaciones'

urlpatterns = [
    path('', views.lista_notificaciones, name='lista'),
    path('<int:notificacion_id>/', views.detalle_notificacion, name='detalle'),
    path('<int:notificacion_id>/marcar-leida/', views.marcar_leida, name='marcar_leida'),
    path('marcar-todas-leidas/', views.marcar_todas_leidas, name='marcar_todas_leidas'),
    path('<int:notificacion_id>/eliminar/', views.eliminar_notificacion, name='eliminar'),
    path('eliminar-leidas/', views.eliminar_leidas, name='eliminar_leidas'),
    path('contador-no-leidas/', views.contador_no_leidas, name='contador_no_leidas'),
]