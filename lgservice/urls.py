from django.contrib import admin
from django.urls import path, include
from lgservice.views import home
from usuarios import views as usuarios_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Página principal
    path('', home, name='home'),

    # Usuarios
    path('usuarios/', include(('usuarios.urls', 'usuarios'), namespace='usuarios')),
    path('login/', usuarios_views.login_simple, name='login_simple'),
    path('accounts/', include('django.contrib.auth.urls')),

    # Otras apps del sistema
    path('alumnos/', include(('alumnos.urls', 'alumnos'), namespace='alumnos')),
    path('reportes/', include(('reportes.urls', 'reportes'), namespace='reportes')),
    path('configuracion/', include(('configuracion.urls', 'configuracion'), namespace='configuracion')),
    path('ayuda/', include('ayuda.urls')),
    path('compras/', include(('compras.urls', 'compras'), namespace='compras')),
    path('productos/', include(('productos.urls', 'productos'), namespace='productos')),
    path('stock/', include(('stock.urls', 'stock'), namespace='stock')),
    path('ventas/', include(('ventas.urls', 'ventas'), namespace='ventas')),
    path('facturacion/', include(('facturacion.urls', 'facturacion'), namespace='facturacion')),

    # API
    path('api/alumnos/', include('alumnos.api_urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Archivos estáticos en desarrollo
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
