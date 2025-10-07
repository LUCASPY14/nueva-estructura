from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'productos', api_views.ProductoViewSet)
router.register(r'categorias', api_views.CategoriaViewSet)
router.register(r'movimientos', api_views.MovimientoStockViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('alertas/', api_views.stock_alerts, name='api-stock-alerts'),
    path('dashboard/', api_views.dashboard_stats, name='api-dashboard-stats'),
]