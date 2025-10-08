import os
import re
from collections import defaultdict

def analizar_templates_huerfanos():
    """Analiza templates huérfanos para determinar si son útiles o duplicados"""
    
    # Mapping de templates que deberían mantenerse vs eliminar
    templates_analysis = {
        'MANTENER': [],
        'ELIMINAR_DUPLICADOS': [],
        'ELIMINAR_OBSOLETOS': [],
        'RENOMBRAR': []
    }
    
    # Patrones de templates útiles que mantener
    templates_utiles = [
        'base.html',  # Templates base siempre útiles
        'dashboard.html',  # Dashboards específicos
        'confirmar_eliminar', 'confirm_delete',  # Confirmaciones
        'detalle', '_detalle',  # Vistas de detalle
        'form', '_form',  # Formularios genéricos
    ]
    
    # Templates huérfanos identificados por app
    huerfanos = {
        'alumnos': [
            'alumno_detalle.html', 'lista_alumnos.html', 'editar_alumno.html',
            'crear_alumno.html', 'historial_transacciones.html', 'asignar_padre.html',
            'validar_transaccion.html', 'mis_notificaciones.html', 'cargar_saldo.html',
            'eliminar_alumno.html'
        ],
        'productos': [
            'escanear_codigo.html', 'producto_confirmar_eliminar.html', 'editar_categoria.html',
            'historial_movimientos.html', 'crear_producto.html', 'registrar_movimiento.html',
            'crear_categoria.html', 'confirmar_eliminacion.html', 'producto_detalle.html',
            'eliminar_producto.html'
        ],
        'ventas': [
            'detalle_venta.html', 'base.html', 'crear_venta.html', 'resumen_turno.html',
            'cerrar_turno.html', 'abrir_turno.html', 'configuracion.html',
            'confirmar_eliminar_venta.html', 'dashboard.html', 'ventas_lista.html'
        ],
        'reportes': [
            'reporte_ventas_resultado.html', 'reporte_alumnos_resultado.html',
            'generar_reporte.html', 'reportes_lista.html', 'reporte_stock.html',
            'reportes_ventas_form.html', 'ticket_venta.html',
            'reporte_ventas_periodo_resultado.html', 'reporte_ventas_periodo_form.html',
            'reporte_ventas_pdf.html'
        ],
        'compras': [
            'compras_lista.html', 'confirmar_eliminar_compra.html',
            'crear_editar_compra.html', 'detalle_compra.html'
        ],
        'proveedores': [
            'lista_proveedores.html', 'proveedor_confirm_delete.html',
            'proveedores_lista.html', 'detalle_proveedor.html',
            'base_proveedores.html', 'proveedor_form.html', 'form_proveedor.html'
        ],
        'facturacion': [
            'factura_detalle.html', 'factura_confirm_delete.html', 'factura_form.html'
        ],
        'usuarios': [
            'usuario_editar.html', 'usuario_eliminar.html', 'usuario_detalle.html',
            'usuario_form.html', 'usuario_confirmar_eliminar.html',
            'password_change_form.html', 'usuarios_lista.html',
            'password_reset_form.html', 'usuario_crear.html'
        ],
        'configuracion': ['configuracion.html'],
        'ayuda': ['ayuda.html'],
        'core': ['base.html']
    }
    
    print("🔍 ANÁLISIS DETALLADO DE TEMPLATES HUÉRFANOS")
    print("=" * 50)
    
    for app, templates in huerfanos.items():
        print(f"\n📱 {app.upper()}:")
        print("-" * 30)
        
        for template in templates:
            filepath = f"{app}/templates/{app}/{template}"
            
            # Verificar si el archivo existe
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                
                # Leer contenido para análisis
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = len(content.splitlines())
                except:
                    content = ""
                    lines = 0
                
                # Análisis del template
                status = "❓ REVISAR"
                reason = ""
                
                # Templates base - mantener
                if 'base' in template.lower():
                    status = "✅ MANTENER"
                    reason = "Template base"
                    templates_analysis['MANTENER'].append((app, template))
                
                # Templates de confirmación - mantener
                elif any(pattern in template.lower() for pattern in ['confirm', 'confirmar', 'eliminar']):
                    status = "✅ MANTENER"
                    reason = "Confirmación necesaria"
                    templates_analysis['MANTENER'].append((app, template))
                
                # Templates con nombres antiguos/duplicados
                elif template.lower().replace('_', '').replace('-', '') in [
                    'listaalumnos.html', 'crearalumno.html', 'editaralumno.html',
                    'listaproductos.html', 'crearproducto.html',
                    'ventaslista.html', 'comprislista.html',
                    'listaproveedores.html', 'proveedoreslista.html',
                    'usuarioslista.html'
                ]:
                    status = "🗑️ ELIMINAR"
                    reason = "Duplicado/nombre antiguo"
                    templates_analysis['ELIMINAR_DUPLICADOS'].append((app, template))
                
                # Templates con contenido mínimo
                elif lines < 10 or file_size < 500:
                    status = "🗑️ ELIMINAR"
                    reason = f"Contenido mínimo ({lines} líneas)"
                    templates_analysis['ELIMINAR_OBSOLETOS'].append((app, template))
                
                # Templates detalle - mantener si tienen contenido
                elif 'detalle' in template.lower() and lines > 20:
                    status = "✅ MANTENER"
                    reason = "Vista detalle con contenido"
                    templates_analysis['MANTENER'].append((app, template))
                
                # Templates form - mantener si tienen contenido
                elif 'form' in template.lower() and lines > 15:
                    status = "✅ MANTENER"
                    reason = "Formulario con contenido"
                    templates_analysis['MANTENER'].append((app, template))
                
                else:
                    status = "❓ REVISAR"
                    reason = f"{lines} líneas, {file_size} bytes"
                
                print(f"   {status} {template:<35} - {reason}")
            
            else:
                print(f"   ❌ {template:<35} - NO EXISTE")
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DEL ANÁLISIS:")
    print(f"   ✅ Mantener: {len(templates_analysis['MANTENER'])}")
    print(f"   🗑️ Eliminar duplicados: {len(templates_analysis['ELIMINAR_DUPLICADOS'])}")
    print(f"   🗑️ Eliminar obsoletos: {len(templates_analysis['ELIMINAR_OBSOLETOS'])}")
    
    # Mostrar listas detalladas
    if templates_analysis['ELIMINAR_DUPLICADOS']:
        print(f"\n🗑️ TEMPLATES DUPLICADOS A ELIMINAR:")
        for app, template in templates_analysis['ELIMINAR_DUPLICADOS']:
            print(f"   rm {app}/templates/{app}/{template}")
    
    if templates_analysis['ELIMINAR_OBSOLETOS']:
        print(f"\n🗑️ TEMPLATES OBSOLETOS A ELIMINAR:")
        for app, template in templates_analysis['ELIMINAR_OBSOLETOS']:
            print(f"   rm {app}/templates/{app}/{template}")
    
    return templates_analysis

if __name__ == "__main__":
    analizar_templates_huerfanos()
