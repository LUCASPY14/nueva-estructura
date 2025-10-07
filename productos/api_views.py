from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Q, Sum, F
from .models import Producto, Categoria, MovimientoStock
from .serializers import (
    ProductoSerializer, CategoriaSerializer,
    MovimientoStockSerializer, StockAlertsSerializer
)

class ProductoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar productos.
    """
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Producto.objects.all()
        categoria = self.request.query_params.get('categoria', None)
        estado = self.request.query_params.get('estado', None)
        busqueda = self.request.query_params.get('busqueda', None)
        
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        if estado:
            queryset = queryset.filter(estado=estado)
        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) |
                Q(codigo__icontains=busqueda) |
                Q(codigo_barras__icontains=busqueda)
            )
        
        return queryset

class CategoriaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar categorías.
    """
    queryset = Categoria.objects.annotate(productos_count=Count('productos'))
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]

class MovimientoStockViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar movimientos de stock.
    """
    queryset = MovimientoStock.objects.all()
    serializer_class = MovimientoStockSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def stock_alerts(request):
    """
    API endpoint para obtener alertas de stock.
    """
    alertas = StockAlertsSerializer.get_stock_alerts()
    return Response(alertas)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """
    API endpoint para obtener estadísticas del dashboard.
    """
    total_productos = Producto.objects.count()
    productos_activos = Producto.objects.filter(estado='activo').count()
    valor_inventario = Producto.objects.filter(estado='activo').aggregate(
        total=Sum(F('cantidad') * F('precio_venta'))
    )['total'] or 0
    
    bajo_stock = Producto.objects.filter(
        cantidad__lte=F('cantidad_minima'),
        estado='activo'
    ).values('id', 'nombre', 'cantidad', 'cantidad_minima')[:5]
    
    top_vendidos = MovimientoStock.objects.filter(
        tipo_movimiento='salida'
    ).values('producto__nombre').annotate(
        total=Sum('cantidad')
    ).order_by('-total')[:5]
    
    por_categoria = Categoria.objects.annotate(
        count=Count('productos')
    ).values('nombre', 'count').order_by('-count')
    
    return Response({
        'total_productos': total_productos,
        'productos_activos': productos_activos,
        'valor_inventario': valor_inventario,
        'bajo_stock': list(bajo_stock),
        'top_vendidos': list(top_vendidos),
        'por_categoria': list(por_categoria)
    })