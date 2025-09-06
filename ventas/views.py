from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.http import HttpResponse
from django.template.loader import get_template
from django.db.models import Sum
from decimal import Decimal
from alumnos.models import Alumno
from productos.models import Producto
from .models import Venta, DetalleVenta, Pago
from .forms import VentaForm, DetalleFormSet, PagoFormSet, PagoForm
from weasyprint import HTML

# Helper para control de acceso
def es_cajero(user):
    return user.groups.filter(name='Cajeros').exists() or user.is_superuser

def es_cajero_o_admin(user):
    return user.is_superuser or user.groups.filter(name__in=['Cajeros', 'Administradores']).exists()

# --------- CRUD DE VENTAS (Solo cajeros/admin) ---------
@login_required
@user_passes_test(es_cajero, login_url='usuarios:login_simple')
@transaction.atomic
def crear_venta(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        detalles = DetalleFormSet(request.POST)
        pagos = PagoFormSet(request.POST)
        if form.is_valid() and detalles.is_valid() and pagos.is_valid():
            venta = form.save(commit=False)
            venta.cajero = request.user  # Solo si tienes este campo en el modelo

            total = Decimal('0')
            detalles_inst = detalles.save(commit=False)
            for d in detalles_inst:
                total += d.cantidad * d.precio_unitario

            alumno = venta.alumno
            if alumno.saldo_tarjeta < total and not form.cleaned_data['codigo_autorizacion']:
                form.add_error(None, "Saldo insuficiente y sin autorización de Admin.")
            else:
                venta.sobregiro_autorizado = bool(form.cleaned_data['codigo_autorizacion'])
                venta.codigo_autorizacion = form.cleaned_data['codigo_autorizacion']
                venta.total = total
                venta.save()

                for d in detalles_inst:
                    d.venta = venta
                    d.save()

                pagos_inst = pagos.save(commit=False)
                for p in pagos_inst:
                    p.venta = venta
                    p.save()

                prepago_amount = sum(p.monto for p in venta.pagos.filter(metodo='SALDO'))
                if prepago_amount > 0:
                    alumno.saldo_tarjeta -= prepago_amount
                    alumno.save()

                messages.success(request, f"Venta #{venta.id} registrada.")
                return redirect('ventas:ventas_lista')
    else:
        form = VentaForm()
        detalles = DetalleFormSet()
        pagos = PagoFormSet(initial=[{'metodo': 'SALDO', 'monto': 0}])

    return render(request, 'ventas/crear_venta.html', {
        'form': form, 'detalles': detalles, 'pagos': pagos
    })

@login_required
@user_passes_test(es_cajero, login_url='usuarios:login_simple')
def ventas_lista(request):
    ventas = Venta.objects.select_related('alumno').all().order_by('-fecha')
    return render(request, 'ventas/ventas_lista.html', {'ventas': ventas})

@login_required
@user_passes_test(es_cajero, login_url='usuarios:login_simple')
def detalle_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    return render(request, 'ventas/detalle_venta.html', {'venta': venta})

@login_required
@user_passes_test(es_cajero, login_url='usuarios:login_simple')
@transaction.atomic
def eliminar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == 'POST':
        prepago = sum(p.monto for p in venta.pagos.filter(metodo='SALDO'))
        if prepago > 0:
            venta.alumno.saldo_tarjeta += prepago
            venta.alumno.save()
        venta.delete()
        messages.success(request, f"Venta #{pk} anulada y saldo restituido.")
        return redirect('ventas:ventas_lista')
    return render(request, 'ventas/confirmar_eliminar_venta.html', {'venta': venta})

# --------- REPORTES DE VENTAS (Solo cajeros/admin, si deseas) ---------
@login_required
@user_passes_test(es_cajero, login_url='usuarios:login_simple')
def reporte_ventas_view(request):
    ventas = Venta.objects.all().order_by('-fecha')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if fecha_inicio:
        ventas = ventas.filter(fecha__date__gte=fecha_inicio)
    if fecha_fin:
        ventas = ventas.filter(fecha__date__lte=fecha_fin)

    total = ventas.aggregate(total=Sum('total'))['total'] or 0

    context = {
        'ventas': ventas,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total': total
    }
    return render(request, 'ventas/reporte_ventas.html', context)

@login_required
@user_passes_test(es_cajero, login_url='usuarios:login_simple')
def reporte_ventas_pdf(request):
    ventas = Venta.objects.all().order_by('-fecha')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if fecha_inicio:
        ventas = ventas.filter(fecha__date__gte=fecha_inicio)
    if fecha_fin:
        ventas = ventas.filter(fecha__date__lte=fecha_fin)

    total = ventas.aggregate(total=Sum('total'))['total'] or 0
    template = get_template('ventas/reporte_ventas_pdf.html')
    html_content = template.render({
        'ventas': ventas,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total': total
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_ventas.pdf"'
    HTML(string=html_content).write_pdf(target=response)
    return response

@login_required
@user_passes_test(es_cajero_o_admin)
@transaction.atomic
def registrar_venta(request):
    if request.method == 'POST':
        venta_form = VentaForm(request.POST)
        detalle_formset = DetalleFormSet(request.POST, prefix='detalle')
        pago_formset = PagoFormSet(request.POST, prefix='pago')
        if venta_form.is_valid() and detalle_formset.is_valid() and pago_formset.is_valid():
            venta = venta_form.save(commit=False)
            venta.cajero = request.user
            venta.save()
            detalle_formset.instance = venta
            pago_formset.instance = venta
            detalles = detalle_formset.save()
            pagos = pago_formset.save()
            # Actualiza el total de la venta
            venta.actualizar_total()
            messages.success(request, "Venta registrada correctamente.")
            return redirect('ventas:detalle_venta', pk=venta.pk)
        else:
            messages.error(request, "Corrige los errores en el formulario.")
    else:
        venta_form = VentaForm()
        detalle_formset = DetalleFormSet(prefix='detalle')
        pago_formset = PagoFormSet(prefix='pago')
    return render(request, 'ventas/registrar_venta.html', {
        'venta_form': venta_form,
        'detalle_formset': detalle_formset,
        'pago_formset': pago_formset,
    })
