from django.contrib import admin
from django.urls import path, include
from lgservice.views import home
from usuarios import views as usuarios_views

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    path('usuarios/', include(('usuarios.urls', 'usuarios'), namespace='usuarios')),
    path('login/', usuarios_views.login_simple, name='login_simple'),  # ← esto redirige /login/


    # Aplicaciones del proyecto
    path('usuarios/', include(('usuarios.urls', 'usuarios'), namespace='usuarios')),
    path('alumnos/', include(('alumnos.urls', 'alumnos'), namespace='alumnos')),
    path('reportes/', include(('reportes.urls', 'reportes'), namespace='reportes')),

    # Página de inicio
    path('', home, name='home'),
]
