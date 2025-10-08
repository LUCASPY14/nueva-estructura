import os
import sys
import django
from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from colorama import Fore, Style, init

# Initialize colorama
init()

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lgservice.settings')
django.setup()

def probar_navegacion_urls():
    """Prueba todas las URLs del sistema para verificar navegación"""
    
    print(f"{Fore.CYAN}🧪 PRUEBAS DE NAVEGACIÓN - CANTINA DE TITA{Style.RESET_ALL}")
    print("=" * 50)
    
    # Crear cliente de prueba
    client = Client()
    
    # Crear usuario de prueba si no existe
    User = get_user_model()
    try:
        test_user = User.objects.get(username='test_navegacion')
    except User.DoesNotExist:
        test_user = User.objects.create_user(
            username='test_navegacion',
            password='test123',
            email='test@navegacion.com',
            tipo_usuario='administrador'
        )
        print(f"{Fore.GREEN}✅ Usuario de prueba creado{Style.RESET_ALL}")
    
    # Login del usuario de prueba
    client.login(username='test_navegacion', password='test123')
    
    # URLs a probar organizadas por app
    urls_a_probar = {
        'core': [
            ('core:home', 'Home'),
        ],
        'usuarios': [
            ('usuarios:landing', 'Landing'),
            ('usuarios:dashboard_admin', 'Dashboard Admin'),
            ('usuarios:logout', 'Logout'),
        ],
        'alumnos': [
            ('alumnos:lista', 'Lista Alumnos'),
            ('alumnos:crear', 'Crear Alumno'),
        ],
        'productos': [
            ('productos:lista', 'Lista Productos'),
            ('productos:crear', 'Crear Producto'),
            ('productos:categorias', 'Categorías'),
        ],
        'ventas': [
            ('ventas:lista', 'Lista Ventas'),
            ('ventas:nueva', 'Nueva Venta'),
            ('ventas:pos', 'POS'),
            ('ventas:reportes', 'Reportes Ventas'),
        ],
        'compras': [
            ('compras:lista', 'Lista Compras'),
        ],
        'proveedores': [
            ('proveedores:lista', 'Lista Proveedores'),
        ],
        'facturacion': [
            ('facturacion:lista', 'Lista Facturas'),
            ('facturacion:crear', 'Crear Factura'),
            ('facturacion:electronica', 'Facturación Electrónica'),
            ('facturacion:reportes', 'Reportes Facturación'),
        ],
        'reportes': [
            ('reportes:dashboard', 'Dashboard Reportes'),
            ('reportes:ventas', 'Reportes Ventas'),
        ],
        'configuracion': [
            ('configuracion:general', 'Configuración General'),
            ('configuracion:sistema', 'Configuración Sistema'),
            ('configuracion:notificaciones', 'Notificaciones'),
            ('configuracion:backup', 'Backup'),
            ('configuracion:usuarios', 'Usuarios Config'),
        ],
        'ayuda': [
            ('ayuda:index', 'Centro de Ayuda'),
            ('ayuda:contacto', 'Contacto'),
        ]
    }
    
    # Contadores
    total_urls = sum(len(urls) for urls in urls_a_probar.values())
    exitosas = 0
    errores = 0
    warnings = 0
    
    print(f"📊 Total de URLs a probar: {total_urls}")
    print()
    
    # Probar cada app
    for app_name, urls in urls_a_probar.items():
        print(f"{Fore.YELLOW}📱 {app_name.upper()}{Style.RESET_ALL}")
        print("-" * 30)
        
        for url_name, descripcion in urls:
            try:
                # Intentar obtener la URL
                url = reverse(url_name)
                
                # Hacer request
                response = client.get(url, follow=True)
                
                # Evaluar respuesta
                if response.status_code == 200:
                    print(f"   {Fore.GREEN}✅{Style.RESET_ALL} {descripcion:<25} - {url}")
                    exitosas += 1
                elif response.status_code in [301, 302]:
                    print(f"   {Fore.YELLOW}🔄{Style.RESET_ALL} {descripcion:<25} - {url} (Redirect)")
                    warnings += 1
                elif response.status_code == 403:
                    print(f"   {Fore.YELLOW}🔒{Style.RESET_ALL} {descripcion:<25} - {url} (Sin permisos)")
                    warnings += 1
                elif response.status_code == 404:
                    print(f"   {Fore.RED}❌{Style.RESET_ALL} {descripcion:<25} - {url} (Template no encontrado)")
                    errores += 1
                else:
                    print(f"   {Fore.RED}⚠️{Style.RESET_ALL} {descripcion:<25} - {url} (Status: {response.status_code})")
                    errores += 1
                    
            except Exception as e:
                print(f"   {Fore.RED}💥{Style.RESET_ALL} {descripcion:<25} - ERROR: {str(e)}")
                errores += 1
        
        print()
    
    # URLs que requieren parámetros (solo verificar que existan los templates)
    print(f"{Fore.MAGENTA}🔍 VERIFICANDO TEMPLATES DE DETALLE{Style.RESET_ALL}")
    print("-" * 40)
    
    templates_detalle = [
        ('alumnos/ver.html', 'Ver Alumno'),
        ('alumnos/editar.html', 'Editar Alumno'),
        ('productos/ver.html', 'Ver Producto'),
        ('productos/editar.html', 'Editar Producto'),
        ('ventas/ver.html', 'Ver Venta'),
        ('facturacion/ver.html', 'Ver Factura'),
    ]
    
    for template_path, descripcion in templates_detalle:
        full_path = f"templates/{template_path}"
        if os.path.exists(full_path):
            print(f"   {Fore.GREEN}✅{Style.RESET_ALL} {descripcion:<25} - {template_path}")
        else:
            # Buscar en las subcarpetas de apps
            app_name = template_path.split('/')[0]
            template_name = template_path.split('/')[-1]
            app_template_path = f"{app_name}/templates/{app_name}/{template_name}"
            
            if os.path.exists(app_template_path):
                print(f"   {Fore.GREEN}✅{Style.RESET_ALL} {descripcion:<25} - {app_template_path}")
            else:
                print(f"   {Fore.RED}❌{Style.RESET_ALL} {descripcion:<25} - {template_path} (No encontrado)")
                errores += 1
    
    # Resumen final
    print("\n" + "=" * 50)
    print(f"{Fore.CYAN}📊 RESUMEN DE PRUEBAS{Style.RESET_ALL}")
    print("-" * 25)
    print(f"   {Fore.GREEN}✅ Exitosas:{Style.RESET_ALL} {exitosas}")
    print(f"   {Fore.YELLOW}⚠️ Warnings:{Style.RESET_ALL} {warnings}")
    print(f"   {Fore.RED}❌ Errores:{Style.RESET_ALL} {errores}")
    print(f"   📊 Total: {exitosas + warnings + errores}")
    
    # Calcular porcentaje de éxito
    total_probadas = exitosas + warnings + errores
    if total_probadas > 0:
        porcentaje_exito = ((exitosas + warnings) / total_probadas) * 100
        print(f"   🎯 Tasa de éxito: {porcentaje_exito:.1f}%")
        
        if porcentaje_exito >= 90:
            print(f"\n{Fore.GREEN}🎉 ¡EXCELENTE! Navegación funcionando correctamente{Style.RESET_ALL}")
        elif porcentaje_exito >= 75:
            print(f"\n{Fore.YELLOW}👍 BUENO: La mayoría de URLs funcionan{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}⚠️ NECESITA ATENCIÓN: Muchos errores encontrados{Style.RESET_ALL}")
    
    # Limpiar usuario de prueba
    test_user.delete()
    print(f"\n{Fore.GREEN}🧹 Usuario de prueba eliminado{Style.RESET_ALL}")
    
    return exitosas, warnings, errores

if __name__ == "__main__":
    try:
        probar_navegacion_urls()
    except Exception as e:
        print(f"{Fore.RED}💥 Error crítico: {e}{Style.RESET_ALL}")
        sys.exit(1)
