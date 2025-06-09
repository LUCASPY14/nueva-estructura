from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string, get_template
import weasyprint
from weasyprint import HTML
import tempfile
from .models import Factura
from .forms import FacturaForm

# Chequeo de administrador
from django.conf import settings

def es_admin(user):
    return user.groups.filter(name='Administradores').exists()

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def lista_facturas(request):
    facturas = Factura.objects.select_related('venta').all()
    return render(request, 'facturacion/invoice_list.html', {'facturas': facturas})

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def crear_factura(request):
    if request.method == 'POST':
        form = FacturaForm(request.POST)
        if form.is_valid():
            factura = form.save()
            messages.success(request, f"Factura {factura.numero} creada.")
            return redirect('facturacion:detalle_factura', pk=factura.pk)
    else:
        form = FacturaForm()
    return render(request, 'facturacion/invoice_create.html', {'form': form})

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def detalle_factura(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    return render(request, 'facturacion/invoice_detail.html', {'factura': factura})

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def descargar_pdf(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    html = render_to_string('facturacion/invoice_pdf.html', {'factura': factura})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="factura_{factura.numero}.pdf"'
    weasyprint.HTML(string=html).write_pdf(response,
        stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + '/css/invoice.css')])
    return response

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def eliminar_factura(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    if request.method == 'POST':
        factura.delete()
        messages.success(request, f"Factura {factura.numero} eliminada.")
        return redirect('facturacion:lista_facturas')
    return render(request, 'facturacion/confirmar_eliminar_factura.html', {'factura': factura})

@login_required
def factura_detalle_view(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    return render(request, 'facturacion/factura_detalle.html', {'factura': factura})

@login_required
def factura_pdf_view(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    template = get_template('facturacion/factura_detalle.html')
    html_content = template.render({'factura': factura})

    # Usamos un archivo temporal
    with tempfile.NamedTemporaryFile(delete=True) as tmpfile:
        HTML(string=html_content).write_pdf(tmpfile.name)

        tmpfile.seek(0)
        response = HttpResponse(tmpfile.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'filename=factura_{factura.numero}.pdf'
        return response
