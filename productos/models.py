from django.db import models
from django.conf import settings
from decimal import Decimal

class Categoria(models.Model):
    """Categoría de productos"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    """Modelo de producto"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=5)
    activo = models.BooleanField(default=True)
    
    # Imagen del producto (opcional)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['categoria']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def stock_bajo(self):
        return self.stock_actual <= self.stock_minimo

class MovimientoStock(models.Model):
    """Modelo para registrar movimientos de stock"""
    TIPO_MOVIMIENTO = [
        ('entrada', 'Entrada de Stock'),
        ('salida', 'Salida de Stock'),
        ('ajuste', 'Ajuste de Inventario'),
        ('venta', 'Venta'),
        ('devolucion', 'Devolución'),
    ]
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=15, choices=TIPO_MOVIMIENTO)
    cantidad = models.IntegerField()
    stock_anterior = models.PositiveIntegerField()
    stock_nuevo = models.PositiveIntegerField()
    motivo = models.CharField(max_length=200, blank=True, null=True)
    
    # Campos de auditoría - usar settings.AUTH_USER_MODEL en lugar de User
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos_stock'
    )
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Movimiento de Stock'
        verbose_name_plural = 'Movimientos de Stock'
        ordering = ['-fecha_movimiento']
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.get_tipo_display()} - {self.cantidad}"

class ProductoProveedor(models.Model):
    """Relación entre productos y proveedores con información específica"""
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='proveedores_info')
    proveedor = models.ForeignKey('proveedores.Proveedor', on_delete=models.PROTECT, related_name='productos_ofrecidos')
    codigo_producto_proveedor = models.CharField(max_length=50, help_text="Código del producto según el proveedor")
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    tiempo_entrega = models.IntegerField(help_text="Días de entrega", validators=[MinValueValidator(1)])
    cantidad_minima_pedido = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    notas = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto-Proveedor'
        verbose_name_plural = 'Productos-Proveedores'
        unique_together = ['producto', 'proveedor']
        indexes = [
            models.Index(fields=['activo']),
            models.Index(fields=['precio']),
        ]

    def __str__(self):
        return f"{self.producto.nombre} - {self.proveedor.nombre}"
