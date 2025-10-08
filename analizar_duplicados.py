#!/usr/bin/env python
"""
Script para identificar y reorganizar templates duplicados
"""
import os
import sys
from collections import defaultdict
import difflib

def obtener_templates_por_app():
    """Obtener todos los templates organizados por app"""
    base_dir = '/home/ucas1/nueva_estructura'
    templates_por_app = {}
    
    # Apps individuales
    for app_dir in ['alumnos', 'productos', 'ventas', 'reportes', 'compras', 'proveedores', 
                    'facturacion', 'usuarios', 'configuracion', 'ayuda', 'core']:
        template_path = os.path.join(base_dir, app_dir, 'templates', app_dir)
        if os.path.exists(template_path):
            templates_por_app[app_dir] = []
            for root, dirs, files in os.walk(template_path):
                for file in files:
                    if file.endswith('.html'):
                        rel_path = os.path.relpath(os.path.join(root, file), template_path)
                        full_path = os.path.join(root, file)
                        templates_por_app[app_dir].append({
                            'name': rel_path,
                            'full_path': full_path,
                            'base_name': file,
                            'size': os.path.getsize(full_path) if os.path.exists(full_path) else 0
                        })
    
    return templates_por_app

def identificar_patrones_duplicados(templates_por_app):
    """Identificar patrones de templates duplicados"""
    # Agrupar por nombres similares
    patrones = defaultdict(list)
    
    for app, templates in templates_por_app.items():
        for template in templates:
            base_name = template['base_name']
            
            # Identificar patrones comunes
            if 'lista' in base_name.lower():
                patrones['listas'].append((app, template))
            elif 'crear' in base_name.lower() or 'form' in base_name.lower():
                patrones['formularios_crear'].append((app, template))
            elif 'editar' in base_name.lower():
                patrones['formularios_editar'].append((app, template))
            elif 'detalle' in base_name.lower() or 'ver' in base_name.lower():
                patrones['detalles'].append((app, template))
            elif 'eliminar' in base_name.lower() or 'delete' in base_name.lower():
                patrones['eliminar'].append((app, template))
            elif 'confirm' in base_name.lower():
                patrones['confirmaciones'].append((app, template))
    
    return patrones

def analizar_contenido_similar(templates_grupo):
    """Analizar si templates tienen contenido similar"""
    similares = []
    
    for i, (app1, template1) in enumerate(templates_grupo):
        for j, (app2, template2) in enumerate(templates_grupo[i+1:], i+1):
            try:
                with open(template1['full_path'], 'r', encoding='utf-8') as f1:
                    content1 = f1.read()
                with open(template2['full_path'], 'r', encoding='utf-8') as f2:
                    content2 = f2.read()
                
                # Calcular similitud
                similarity = difflib.SequenceMatcher(None, content1, content2).ratio()
                
                if similarity > 0.8:  # 80% de similitud
                    similares.append({
                        'template1': (app1, template1),
                        'template2': (app2, template2),
                        'similarity': similarity
                    })
            except Exception as e:
                continue
    
    return similares

def main():
    print("🔍 ANÁLISIS DE TEMPLATES DUPLICADOS - CANTINA DE TITA")
    print("=" * 70)
    
    templates_por_app = obtener_templates_por_app()
    patrones = identificar_patrones_duplicados(templates_por_app)
    
    print(f"\n📊 PATRONES IDENTIFICADOS:")
    for patron, templates in patrones.items():
        print(f"\n📁 {patron.upper().replace('_', ' ')} ({len(templates)} templates):")
        
        # Agrupar por app
        por_app = defaultdict(list)
        for app, template in templates:
            por_app[app].append(template)
        
        for app, app_templates in por_app.items():
            print(f"   📱 {app}:")
            for template in app_templates:
                print(f"      - {template['name']} ({template['size']} bytes)")
    
    print(f"\n" + "=" * 70)
    print("🎯 RECOMENDACIONES DE LIMPIEZA:")
    
    # Identificar posibles duplicados exactos por naming
    print(f"\n1. TEMPLATES CON NOMBRES SIMILARES:")
    naming_issues = []
    
    for app, templates in templates_por_app.items():
        nombres = [t['base_name'] for t in templates]
        for nombre in nombres:
            # Buscar variaciones del mismo nombre
            variaciones = [n for n in nombres if n != nombre and 
                          (nombre.replace('_', '').replace('-', '') in n.replace('_', '').replace('-', '') or
                           n.replace('_', '').replace('-', '') in nombre.replace('_', '').replace('-', ''))]
            if variaciones:
                naming_issues.append((app, nombre, variaciones))
    
    for app, nombre, variaciones in naming_issues[:10]:  # Mostrar primeros 10
        print(f"   📱 {app}: '{nombre}' vs {variaciones}")
    
    print(f"\n2. TEMPLATES QUE DEBERÍAN CONSOLIDARSE:")
    
    # Sugerir consolidaciones por patrón
    consolidaciones = {
        'Lista de registros': ['lista.html', 'list.html', '*_lista.html', 'lista_*.html'],
        'Crear/Formulario': ['crear.html', 'form.html', '*_form.html', 'create.html'],
        'Editar': ['editar.html', 'edit.html', '*_editar.html'],
        'Ver detalles': ['ver.html', 'detalle.html', '*_detalle.html', 'detail.html'],
        'Eliminar': ['eliminar.html', 'delete.html', '*_eliminar.html'],
    }
    
    for tipo, patrones_names in consolidaciones.items():
        print(f"\n   🎯 {tipo}:")
        for app, templates in templates_por_app.items():
            templates_tipo = []
            for template in templates:
                for patron in patrones_names:
                    if (patron.startswith('*') and template['base_name'].endswith(patron[1:])) or \
                       (patron.endswith('*') and template['base_name'].startswith(patron[:-1])) or \
                       template['base_name'] == patron:
                        templates_tipo.append(template['name'])
            
            if len(templates_tipo) > 1:
                print(f"      📱 {app}: {templates_tipo}")
    
    print(f"\n3. ARCHIVOS POTENCIALMENTE NO UTILIZADOS:")
    
    # Templates que no siguen el patrón estándar
    for app, templates in templates_por_app.items():
        templates_sospechosos = []
        for template in templates:
            nombre = template['base_name'].lower()
            # Templates que no siguen patrones estándar
            if not any(patron in nombre for patron in ['lista', 'crear', 'editar', 'ver', 'eliminar', 
                                                      'form', 'detail', 'delete', 'index', 'dashboard',
                                                      'base', 'partial', 'component']):
                templates_sospechosos.append(template['name'])
        
        if templates_sospechosos:
            print(f"   📱 {app}: {templates_sospechosos[:5]}")  # Mostrar primeros 5
    
    print(f"\n" + "=" * 70)
    print("✨ ANÁLISIS COMPLETADO")
    print("\nPRÓXIMOS PASOS RECOMENDADOS:")
    print("1. Consolidar templates de lista: usar 'lista.html' como estándar")
    print("2. Unificar formularios: 'crear.html' y 'editar.html'")
    print("3. Estandarizar detalles: usar 'ver.html'")
    print("4. Eliminar templates duplicados o no utilizados")

if __name__ == '__main__':
    main()