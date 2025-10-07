from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.core.validators import MinValueValidator
from .validators import validate_ean13
import uuid
import os

def producto_imagen_path(instance, filename):
    # Genera un nombre único para la imagen usando UUID
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('productos', filename)

class Categoria(models.Model):
    """
    Categoría a la que pertenece un producto (bebidas, snacks, etc.).
    """
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True, help_text="Indica si esta categoría está activa")
    
    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

class Producto(models.Model):
    """
    Representa un producto disponible para la venta en la cantina.
    
    Este modelo implementa:
    - Gestión completa de productos con códigos EAN-13
    - Control de stock y precios
    - Seguimiento de proveedores principal y alternativos
    - Historial de precios y movimientos
    - Categorización de productos
    
    Índices optimizados para:
    - Búsqueda por nombre/código
    - Filtrado por estado y categoría
    - Consultas de stock
    - Análisis de precios
    
    Atributos:
        codigo (str): Código único del producto
        ean13 (str): Código de barras EAN-13 validado
        nombre (str): Nombre del producto
        descripcion (str): Descripción detallada
        categoria (FK): Categoría del producto
        cantidad (int): Stock actual
        cantidad_minima (int): Nivel mínimo de stock para alertas
        precio_costo (Decimal): Precio de compra
        precio_venta (Decimal): Precio de venta
        
    Relaciones:
        categoria -> Categoria: Clasificación del producto
        proveedor_principal -> Proveedor: Proveedor preferido
        proveedores_alternativos -> Proveedor: Otros proveedores disponibles
    """
    ESTADO_CHOICES = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('agotado', 'Agotado'),
        ('descontinuado', 'Descontinuado'),
    )
    
    # Campos básicos
    codigo = models.CharField(max_length=50, unique=True, db_index=True)
    ean13 = models.CharField(
        max_length=13,
        unique=True,
        blank=True,
        null=True,
        db_index=True,
        help_text="Código de barras EAN-13 del producto",
        validators=[validate_ean13],
        verbose_name="Código EAN-13"
    )
    nombre = models.CharField(
        max_length=100,
        db_index=True
    )
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['estado', 'categoria'], name='idx_estado_categoria'),
            models.Index(fields=['estado', 'destacado'], name='idx_estado_destacado'),
            models.Index(fields=['cantidad', 'cantidad_minima'], name='idx_cantidad_min'),
            models.Index(fields=['fecha_creacion', 'estado'], name='idx_fecha_estado'),
            models.Index(fields=['nombre', 'codigo'], name='idx_nombre_codigo'),
            models.Index(fields=['precio_venta', 'estado'], name='idx_precio_estado'),
            models.Index(fields=['fecha_ultimo_pedido'], name='idx_ultimo_pedido'),
        ]
        ordering = ['nombre']
    
    # Relaciones
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos'
    )
    proveedor_principal = models.ForeignKey(
        'proveedores.Proveedor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos_como_principal'
    )
    proveedores_alternativos = models.ManyToManyField(
        'proveedores.Proveedor',
        through='ProductoProveedor',
        related_name='productos_como_alternativo',
        blank=True
    )
    
    # Precios y stock
    cantidad = models.PositiveIntegerField(default=0)
    cantidad_minima = models.PositiveIntegerField(default=5, help_text="Cantidad mínima antes de alertar")
    precio_costo = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Imagen del producto
    imagen = models.ImageField(upload_to=producto_imagen_path, blank=True, null=True)
    
    # Relaciones
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    proveedor = models.ForeignKey('proveedores.Proveedor', on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    
    # Campos de gestión
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='activo')
    destacado = models.BooleanField(default=False, help_text="Marca este producto como destacado")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_ultimo_pedido = models.DateTimeField(blank=True, null=True)
    
    def stock_actual(self):
        """
        Calcula el stock actual en base a movimientos registrados.
        """
        try:
            total = self.movimientos.aggregate(total=models.Sum('cantidad'))['total'] or 0
            return Decimal(total)
        except:
            return self.cantidad
    
    @property
    def margen_ganancia(self):
        """Calcula el margen de ganancia en porcentaje"""
        if self.precio_costo > 0:
            return ((self.precio_venta - self.precio_costo) / self.precio_costo) * 100
        return 0
    
    @property
    def necesita_reposicion(self):
        """Determina si el producto necesita reposición de stock"""
        return self.cantidad <= self.cantidad_minima
    
    def __str__(self):
        return f"{self.nombre} ({self.codigo})"
    
    class Meta:
        ordering = ['nombre']
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['codigo_barras']),
            models.Index(fields=['estado']),
            models.Index(fields=['categoria']),
        ]

class MovimientoStock(models.Model):
    """
    Registra movimientos de entrada y salida de productos del inventario.
    """
    TIPO_MOVIMIENTO = (
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste de inventario'),
        ('devolucion', 'Devolución'),
    )
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    cantidad = models.IntegerField(help_text="Cantidad positiva para entradas, negativa para salidas")
    tipo_movimiento = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO)
    fecha = models.DateTimeField(default=timezone.now)
    nota = models.TextField(blank=True, null=True, help_text="Motivo o detalle del movimiento")
    usuario = models.ForeignKey('usuarios.UsuarioLG', on_delete=models.SET_NULL, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        """Actualiza automáticamente la cantidad del producto al registrar un movimiento"""
        super().save(*args, **kwargs)
        
        # Actualizar cantidad en el producto
        self.producto.cantidad = self.producto.stock_actual()
        
        # Si es una entrada, actualizar la fecha del último pedido
        self.producto.save()


class ProductoProveedor(models.Model):
    """
    Relación entre productos y proveedores con información adicional sobre precios y condiciones
    """
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    proveedor = models.ForeignKey('proveedores.Proveedor', on_delete=models.CASCADE)
    codigo_producto_proveedor = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Código que el proveedor usa para este producto"
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Precio de compra al proveedor"
    )
    tiempo_entrega = models.PositiveIntegerField(
        help_text="Tiempo estimado de entrega en días",
        null=True,
        blank=True
    )
    cantidad_minima_pedido = models.PositiveIntegerField(
        help_text="Cantidad mínima que el proveedor acepta por pedido",
        null=True,
        blank=True
    )
    ultima_compra = models.DateTimeField(null=True, blank=True)
    notas = models.TextField(blank=True, null=True)
    activo = models.BooleanField(
        default=True,
        help_text="Indica si este proveedor está actualmente disponible para este producto"
    )
    
    class Meta:
        unique_together = ['producto', 'proveedor']
        ordering = ['-ultima_compra']
        verbose_name = "Proveedor de Producto"
        verbose_name_plural = "Proveedores de Productos"
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.proveedor.nombre}"
        if self.tipo_movimiento == 'entrada' and self.cantidad > 0:
            self.producto.fecha_ultimo_pedido = timezone.now()
            
        self.producto.save()
    
    def __str__(self):
        return f"{self.get_tipo_movimiento_display()}: {self.producto.nombre} ({self.cantidad})"
    
    class Meta:
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"
        ordering = ['-fecha']
