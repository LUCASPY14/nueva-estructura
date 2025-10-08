#!/usr/bin/env python
"""
Análisis de Templates vs URLs para el sistema Cantina de Tita
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/home/ucas1/nueva_estructura')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lgservice.settings')
django.setup()

from django.urls import get_resolver
import glob

def obtener_urls_proyecto():
    """Obtener todas las URLs del proyecto"""
    resolver = get_resolver()
    urls = []
    
    def extraer_urls(url_patterns, prefix=''):
        for pattern in url_patterns:
            if hasattr(pattern, 'url_patterns'):
                # Es un URLconf incluido
                if hasattr(pattern, 'namespace') and pattern.namespace:
                    nuevo_prefix = f"{pattern.namespace}:"
                else:
                    nuevo_prefix = prefix
                extraer_urls(pattern.url_patterns, nuevo_prefix)
            else:
                # Es una URL individual
                if hasattr(pattern, 'name') and pattern.name:
                    url_name = f"{prefix}{pattern.name}"
                    view_name = pattern.callback.__name__ if hasattr(pattern.callback, '__name__') else str(pattern.callback)
                    urls.append({
                        'name': url_name,
                        'pattern': str(pattern.pattern),
                        'view': view_name
                    })
    
    try:
        extraer_urls(resolver.url_patterns)
    except Exception as e:
        print(f"Error al extraer URLs: {e}")
    
    return urls

def obtener_templates_existentes():
    """Obtener todos los templates existentes"""
    templates = []
    base_dir = '/home/ucas1/nueva_estructura'
    
    # Buscar en apps individuales
    for app_dir in ['alumnos', 'productos', 'ventas', 'reportes', 'compras', 'proveedores', 'facturacion', 'usuarios', 'configuracion', 'ayuda', 'core']:
        template_path = os.path.join(base_dir, app_dir, 'templates', app_dir)
        if os.path.exists(template_path):
            for root, dirs, files in os.walk(template_path):
                for file in files:
                    if file.endswith('.html'):
                        rel_path = os.path.relpath(os.path.join(root, file), template_path)
                        templates.append({
                            'app': app_dir,
                            'path': rel_path,
                            'full_path': os.path.join(root, file)
                        })
    
    # Buscar en templates globales
    global_templates_path = os.path.join(base_dir, 'templates')
    if os.path.exists(global_templates_path):
        for root, dirs, files in os.walk(global_templates_path):
            for file in files:
                if file.endswith('.html'):
                    rel_path = os.path.relpath(os.path.join(root, file), global_templates_path)
                    templates.append({
                        'app': 'global',
                        'path': rel_path,
                        'full_path': os.path.join(root, file)
                    })
    
    return templates

def mapear_url_a_template(url_name, view_name):
    """Mapear una URL a su template esperado"""
    if ':' in url_name:
        app, name = url_name.split(':', 1)
        return f"{app}/{name}.html"
    return f"{url_name}.html"

def main():
    print("🔍 ANÁLISIS DE TEMPLATES VS URLs - CANTINA DE TITA")
    print("=" * 70)
    
    # Obtener datos
    urls = obtener_urls_proyecto()
    templates = obtener_templates_existentes()
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   URLs encontradas: {len(urls)}")
    print(f"   Templates encontrados: {len(templates)}")
    
    # Agrupar templates por app
    templates_por_app = {}
    for template in templates:
        app = template['app']
        if app not in templates_por_app:
            templates_por_app[app] = []
        templates_por_app[app].append(template)
    
    print(f"\n📁 TEMPLATES POR APP:")
    for app, app_templates in templates_por_app.items():
        print(f"   {app}: {len(app_templates)} templates")
    
    # Analizar URLs principales de cada app
    print(f"\n🎯 ANÁLISIS POR APP:")
    print("-" * 70)
    
    apps_urls = {}
    for url in urls:
        if ':' in url['name']:
            app = url['name'].split(':', 1)[0]
            if app not in apps_urls:
                apps_urls[app] = []
            apps_urls[app].append(url)
    
    for app, app_urls in apps_urls.items():
        print(f"\n📱 {app.upper()}:")
        print(f"   URLs definidas: {len(app_urls)}")
        
        templates_app = templates_por_app.get(app, [])
        print(f"   Templates existentes: {len(templates_app)}")
        
        # Verificar templates faltantes principales
        templates_necesarios = ['lista.html', 'crear.html', 'editar.html', 'ver.html']
        templates_existentes_nombres = [t['path'] for t in templates_app]
        
        for url in app_urls[:5]:  # Mostrar primeras 5 URLs
            url_simple = url['name'].split(':')[1] if ':' in url['name'] else url['name']
            template_esperado = f"{url_simple}.html"
            existe = any(template_esperado in t for t in templates_existentes_nombres)
            status = "✅" if existe else "❌"
            print(f"      {status} {url['name']} -> {template_esperado}")
    
    # Identificar templates huérfanos (sin URL correspondiente)
    print(f"\n🚫 POSIBLES TEMPLATES HUÉRFANOS:")
    print("-" * 40)
    
    url_names = {url['name'] for url in urls}
    for app, app_templates in templates_por_app.items():
        if app == 'global':
            continue
            
        templates_huerfanos = []
        for template in app_templates:
            # Crear nombre de URL esperado
            template_name = template['path'].replace('.html', '').replace('/', '_')
            url_esperada1 = f"{app}:{template_name}"
            url_esperada2 = f"{app}:{template['path'].replace('.html', '')}"
            
            if url_esperada1 not in url_names and url_esperada2 not in url_names:
                templates_huerfanos.append(template['path'])
        
        if templates_huerfanos:
            print(f"\n   📱 {app.upper()}:")
            for huerfano in templates_huerfanos[:10]:  # Mostrar primeros 10
                print(f"      🗑️  {huerfano}")
    
    print(f"\n" + "=" * 70)
    print("✨ ANÁLISIS COMPLETADO")

if __name__ == '__main__':
    main()