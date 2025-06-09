from django.urls import path
from . import views

app_name = 'alumnos'

urlpatterns = [
    # ----------------------------
    # Rutas ADMINISTRADOR (Alumnos)
    # ----------------------------
    path('lista/', views.alumnos_lista, name='alumnos_lista'),
    path('crear/', views.crear_alumno, name='crear_alumno'),
    path('editar/<int:pk>/', views.editar_alumno, name='editar_alumno'),
    path('eliminar/<int:pk>/', views.eliminar_alumno, name='eliminar_alumno'),

    # ----------------------------
    # Rutas ADMINISTRADOR (Restricciones)
    # ----------------------------
    path('restricciones/', views.listar_restricciones, name='listar_restricciones'),
    # Si implementas creación/eliminación de restricciones, descomenta y define las vistas:
    # path('restricciones/crear/', views.crear_restriccion, name='crear_restriccion'),
    # path('restricciones/eliminar/<int:pk>/', views.eliminar_restriccion, name='eliminar_restriccion'),

    # ----------------------------
    # Rutas PADRE
    # ----------------------------
    path('mis_hijos/', views.mis_hijos, name='mis_hijos'),
    path('detalle/<int:pk>/', views.detalle_alumno, name='detalle_alumno'),
    path('cargar_saldo/', views.cargar_saldo, name='cargar_saldo'),
    path('perfil/', views.editar_perfil_padre, name='editar_perfil_padre'),
]
