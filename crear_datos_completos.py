# crear_datos_completos.py
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lgservice.settings')
django.setup()

from productos.models import Categoria, Producto
from alumnos.models import Padre, Alumno
from usuarios.models import CustomUser
from django.contrib.auth import get_user_model
from decimal import Decimal

def crear_categorias():
    """Crear categorías de productos"""
    categorias = [
        {'nombre': 'Bebidas', 'descripcion': 'Refrescos, jugos, agua'},
        {'nombre': 'Snacks', 'descripcion': 'Galletas, chocolates, dulces'},
        {'nombre': 'Comida Rápida', 'descripcion': 'Sándwiches, hamburguesas'},
        {'nombre': 'Lácteos', 'descripcion': 'Yogurt, leche, quesos'},
        {'nombre': 'Frutas', 'descripcion': 'Frutas frescas y ensaladas'},
        {'nombre': 'Útiles Escolares', 'descripcion': 'Cuadernos, lápices, etc.'},
        {'nombre': 'Uniformes', 'descripcion': 'Polos, pantalones, chompas'},
    ]
    
    print("Creando categorías...")
    for cat_data in categorias:
        cat, created = Categoria.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults=cat_data
        )
        if created:
            print(f"✓ Creada: {cat.nombre}")
        else:
            print(f"- Ya existe: {cat.nombre}")

def crear_productos():
    """Crear productos de ejemplo"""
    # Obtener categorías
    bebidas = Categoria.objects.get(nombre='Bebidas')
    snacks = Categoria.objects.get(nombre='Snacks')
    comida = Categoria.objects.get(nombre='Comida Rápida')
    lacteos = Categoria.objects.get(nombre='Lácteos')
    frutas = Categoria.objects.get(nombre='Frutas')
    utiles = Categoria.objects.get(nombre='Útiles Escolares')
    uniformes = Categoria.objects.get(nombre='Uniformes')
    
    productos = [
        # Bebidas
        {'codigo': 'BEB001', 'nombre': 'Coca Cola 500ml', 'categoria': bebidas, 'precio': Decimal('4.50'), 'stock_actual': 50},
        {'codigo': 'BEB002', 'nombre': 'Agua San Luis 625ml', 'categoria': bebidas, 'precio': Decimal('2.00'), 'stock_actual': 100},
        {'codigo': 'BEB003', 'nombre': 'Jugo Gloria Naranja', 'categoria': bebidas, 'precio': Decimal('3.50'), 'stock_actual': 30},
        {'codigo': 'BEB004', 'nombre': 'Inca Kola 500ml', 'categoria': bebidas, 'precio': Decimal('4.50'), 'stock_actual': 45},
        
        # Snacks
        {'codigo': 'SNK001', 'nombre': 'Galletas Oreo', 'categoria': snacks, 'precio': Decimal('3.00'), 'stock_actual': 40},
        {'codigo': 'SNK002', 'nombre': 'Chocolate Sublime', 'categoria': snacks, 'precio': Decimal('2.50'), 'stock_actual': 60},
        {'codigo': 'SNK003', 'nombre': 'Papas Lays Original', 'categoria': snacks, 'precio': Decimal('3.50'), 'stock_actual': 35},
        {'codigo': 'SNK004', 'nombre': 'Piqueo Karinto', 'categoria': snacks, 'precio': Decimal('1.50'), 'stock_actual': 80},
        
        # Comida Rápida
        {'codigo': 'COM001', 'nombre': 'Sándwich Mixto', 'categoria': comida, 'precio': Decimal('8.00'), 'stock_actual': 20},
        {'codigo': 'COM002', 'nombre': 'Hamburguesa Clásica', 'categoria': comida, 'precio': Decimal('12.00'), 'stock_actual': 15},
        {'codigo': 'COM003', 'nombre': 'Hot Dog', 'categoria': comida, 'precio': Decimal('6.50'), 'stock_actual': 25},
        
        # Lácteos
        {'codigo': 'LAC001', 'nombre': 'Yogurt Gloria Fresa', 'categoria': lacteos, 'precio': Decimal('4.00'), 'stock_actual': 30},
        {'codigo': 'LAC002', 'nombre': 'Leche Gloria 1L', 'categoria': lacteos, 'precio': Decimal('6.50'), 'stock_actual': 20},
        
        # Frutas
        {'codigo': 'FRU001', 'nombre': 'Manzana Roja (unidad)', 'categoria': frutas, 'precio': Decimal('2.00'), 'stock_actual': 50},
        {'codigo': 'FRU002', 'nombre': 'Plátano (unidad)', 'categoria': frutas, 'precio': Decimal('1.50'), 'stock_actual': 60},
        {'codigo': 'FRU003', 'nombre': 'Ensalada de Frutas', 'categoria': frutas, 'precio': Decimal('5.50'), 'stock_actual': 15},
        
        # Útiles Escolares
        {'codigo': 'UTI001', 'nombre': 'Cuaderno A4 100 hojas', 'categoria': utiles, 'precio': Decimal('8.50'), 'stock_actual': 25},
        {'codigo': 'UTI002', 'nombre': 'Lápiz Faber Castell HB', 'categoria': utiles, 'precio': Decimal('1.20'), 'stock_actual': 100},
        {'codigo': 'UTI003', 'nombre': 'Borrador Pelikan', 'categoria': utiles, 'precio': Decimal('1.50'), 'stock_actual': 80},
        
        # Uniformes
        {'codigo': 'UNI001', 'nombre': 'Polo Blanco Talla S', 'categoria': uniformes, 'precio': Decimal('25.00'), 'stock_actual': 20},
        {'codigo': 'UNI002', 'nombre': 'Polo Blanco Talla M', 'categoria': uniformes, 'precio': Decimal('25.00'), 'stock_actual': 18},
        {'codigo': 'UNI003', 'nombre': 'Pantalón Azul Talla 32', 'categoria': uniformes, 'precio': Decimal('45.00'), 'stock_actual': 12},
    ]
    
    print("\nCreando productos...")
    for prod_data in productos:
        prod, created = Producto.objects.get_or_create(
            codigo=prod_data['codigo'],
            defaults=prod_data
        )
        if created:
            print(f"✓ Creado: {prod.codigo} - {prod.nombre} - S/. {prod.precio}")
        else:
            print(f"- Ya existe: {prod.codigo} - {prod.nombre}")

def crear_usuarios_padres_alumnos():
    """Crear usuarios, padres y alumnos de ejemplo"""
    User = get_user_model()
    
    # Crear usuarios de ejemplo
    usuarios_data = [
        {'username': 'admin', 'email': 'admin@lgservice.com', 'first_name': 'Admin', 'last_name': 'Sistema', 'is_staff': True, 'is_superuser': True},
        {'username': 'cajero1', 'email': 'cajero1@lgservice.com', 'first_name': 'María', 'last_name': 'González', 'is_staff': True},
        {'username': 'cajero2', 'email': 'cajero2@lgservice.com', 'first_name': 'Juan', 'last_name': 'Pérez', 'is_staff': True},
    ]
    
    print("\nCreando usuarios...")
    for user_data in usuarios_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        if created:
            user.set_password('123456')  # Contraseña por defecto
            user.save()
            print(f"✓ Usuario creado: {user.username} ({user.first_name} {user.last_name})")
        else:
            print(f"- Ya existe: {user.username}")
    
    # Crear padres de ejemplo
    padres_data = [
        {
            'nombre': 'Carlos Eduardo', 
            'apellido': 'Silva Mendoza',
            'ci': '12345678',
            'telefono_fijo': '987654321',
            'email': 'carlos.silva@email.com',
            'direccion': 'Av. Los Olivos 123, Lima',
            'ruc': '20123456781',
            'razon_social': 'Silva Mendoza S.A.C.',
            'celular': '987654321'
        },
        {
            'nombre': 'Ana María', 
            'apellido': 'Torres Vega',
            'ci': '87654321',
            'telefono_fijo': '912345678',
            'email': 'ana.torres@email.com',
            'direccion': 'Jr. Las Flores 456, Lima',
            'ruc': '10876543210',
            'razon_social': 'Ana María Torres Vega',
            'celular': '912345678'
        },
        {
            'nombre': 'Roberto', 
            'apellido': 'Martínez López',
            'ci': '11223344',
            'telefono_fijo': '945678123',
            'email': 'roberto.martinez@email.com',
            'direccion': 'Calle Los Pinos 789, Lima',
            'ruc': '20112233441',
            'razon_social': 'Martínez López E.I.R.L.',
            'celular': '945678123'
        },
    ]
    
    print("\nCreando padres...")
    padres = []
    for padre_data in padres_data:
        padre, created = Padre.objects.get_or_create(
            ci=padre_data['ci'],
            defaults=padre_data
        )
        if created:
            print(f"✓ Padre creado: {padre.nombre} {padre.apellido}")
        else:
            print(f"- Ya existe: {padre.nombre} {padre.apellido}")
        padres.append(padre)
    
    # Crear alumnos de ejemplo
    alumnos_data = [
        {
            'numero_tarjeta': 'TJ001',
            'nombre': 'Miguel Andrés',
            'apellido': 'Silva Torres',
            'ci': '98765432',
            'fecha_nacimiento': '2010-05-15',
            'grado': '5to',
            'seccion': 'A',
            'padre_tutor': padres[0]
        },
        {
            'numero_tarjeta': 'TJ002',
            'nombre': 'Lucía Valentina',
            'apellido': 'Torres Silva',
            'ci': '98123456',
            'fecha_nacimiento': '2008-03-20',
            'grado': '1ro',
            'seccion': 'B',
            'padre_tutor': padres[1]
        },
        {
            'numero_tarjeta': 'TJ003',
            'nombre': 'Diego Fernando',
            'apellido': 'Martínez Vega',
            'ci': '91234567',
            'fecha_nacimiento': '2009-08-10',
            'grado': '6to',
            'seccion': 'A',
            'padre_tutor': padres[2]
        },
        {
            'numero_tarjeta': 'TJ004',
            'nombre': 'Sofía Alejandra',
            'apellido': 'Silva Mendoza',
            'ci': '92345678',
            'fecha_nacimiento': '2012-12-05',
            'grado': '3ro',
            'seccion': 'C',
            'padre_tutor': padres[0]  # Hermana de Miguel
        }
    ]
    
    print("\nCreando alumnos...")
    for alumno_data in alumnos_data:
        alumno, created = Alumno.objects.get_or_create(
            ci=alumno_data['ci'],
            defaults=alumno_data
        )
        if created:
            print(f"✓ Alumno creado: {alumno.nombre} {alumno.apellido} - {alumno.grado} {alumno.seccion}")
        else:
            print(f"- Ya existe: {alumno.nombre} {alumno.apellido}")

def main():
    print("=== CREANDO DATOS DE PRUEBA COMPLETOS ===")
    crear_categorias()
    crear_productos()
    crear_usuarios_padres_alumnos()
    
    print("\n=== RESUMEN ===")
    print(f"Categorías creadas: {Categoria.objects.count()}")
    print(f"Productos creados: {Producto.objects.count()}")
    print(f"Usuarios creados: {CustomUser.objects.count()}")
    print(f"Padres creados: {Padre.objects.count()}")
    print(f"Alumnos creados: {Alumno.objects.count()}")
    print("\nDatos de prueba creados exitosamente!")

if __name__ == '__main__':
    main()