from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # URLs de autenticación
    path('', include('core.urls')),
    path('alumnos/', include('alumnos.urls')),
    path('productos/', include('productos.urls')),
    path('ventas/', include('ventas.urls')),
    path('reportes/', include('reportes.urls')),
    path('compras/', include('compras.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('facturacion/', include('facturacion.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('configuracion/', include('configuracion.urls')),
    path('ayuda/', include('ayuda.urls')),
]

# URLs para development
if settings.DEBUG:
    urlpatterns += [
        path('__reload__/', include('django_browser_reload.urls')),
    ]

# Archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
