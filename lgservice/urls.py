from django.contrib import admin
from django.urls import path, include
from lgservice.views import home
from usuarios import views as usuarios_views

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    path('', include('usuarios.urls', namespace='usuarios')),
    # Incluí las vistas de auth de Django (para password reset/change)
    path('accounts/', include('django.contrib.auth.urls')),  # <-- NECESARIO
    # ...otras rutas si tenés...

    # Solo UNA inclusión de usuarios (deja solo una)
    path('usuarios/', include(('usuarios.urls', 'usuarios'), namespace='usuarios')),

    path('login/', usuarios_views.login_simple, name='login_simple'),  # ← esto redirige /login/

    # Aplicaciones del proyecto
    path('alumnos/', include(('alumnos.urls', 'alumnos'), namespace='alumnos')),
    path('reportes/', include(('reportes.urls', 'reportes'), namespace='reportes')),

    # Página de inicio
    path('', home, name='home'),

    path('configuracion/', include('configuracion.urls')),
    path('ayuda/', include('ayuda.urls')),
    path('compras/', include('compras.urls', namespace='compras')),
    path('productos/', include('productos.urls', namespace='productos')),
    path('stock/', include('stock.urls', namespace='stock')),
    path('ventas/', include(('ventas.urls', 'ventas'), namespace='ventas')),

    path('facturacion/', include('facturacion.urls', namespace='facturacion')),

]
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
