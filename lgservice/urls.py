from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

def home(request):
    return HttpResponse("<h1>🏫 LGService - Funcionando correctamente</h1><p>El sistema está operativo.</p>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
]

# Archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
