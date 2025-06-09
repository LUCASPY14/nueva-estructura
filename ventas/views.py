from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from .models import Venta
from .forms import VentaForm, DetalleFormSet, PagoFormSet
from decimal import Decimal
from django.db.models import Sum
from datetime import datetime
from weasyprint import HTML
import tempfile

def es_cajero(user):
    return user.groups.filter(name='Cajeros').exists()

@login_required
@user_passes_test(es_cajero, login_url='usuarios:login')
@transaction.atomic
def crear_venta(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        detalles = DetalleFormSet(request.POST)
        pagos = PagoFormSet(request.POST)
        if form.is_valid() and detalles.is_valid() and pagos.is_valid():
            venta = form.save(commit=False)
            venta.cajero = request.user

            # Calcular total de ventas
            total = Decimal('0')
            # calcular subtotales de detalles
            detalles_inst = detalles.save(commit=False)
            for d in detalles_inst:
                total += d.cantidad * d.precio_unitario

            # comprobar saldo prepago
            alumno = venta.alumno
            if alumno.saldo_tarjeta < total and not form.cleaned_data['codigo_autorizacion']:
                form.add_error(None, "Saldo insuficiente y sin autorización de Admin.")
            else:
                # asignar autorización si existe
                venta.sobregiro_autorizado = bool(form.cleaned_data['codigo_autorizacion'])
                venta.codigo_autorizacion = form.cleaned_data['codigo_autorizacion']
                venta.total = total
                venta.save()

                # guardar detalles y descontar del saldo prepago
                for d in detalles_inst:
                    d.venta = venta
                    d.save()
                # descuentos de tarjeta prepago
                pago_prepago = False
                for pago in pagos:
                    # detectamos pagos propios
                    pass
                # Asumimos primero Pago con metodo TARJETA_PREPAGO
                pago_set = pagos.save(commit=False)
                for p in pago_set:
                    p.venta = venta
                    p.save()

                # restar saldo tarjeta
                prepago_amount = sum(p.monto for p in venta.pagos.filter(metodo='TARJETA_PREPAGO'))
                alumno.saldo_tarjeta -= prepago_amount
                alumno.save()

                messages.success(request, f"Venta #{venta.id} registrada.")
                return redirect('ventas:ventas_lista')
    else:
        form = VentaForm()
        detalles = DetalleFormSet()
        pagos = PagoFormSet(initial=[{'metodo':'TARJETA_PREPAGO','monto':0}])

    return render(request, 'ventas/crear_venta.html', {
        'form': form, 'detalles': detalles, 'pagos': pagos
    })

@login_required
@user_passes_test(es_cajero, login_url='usuarios:login')
def ventas_lista(request):
    ventas = Venta.objects.select_related('alumno','cajero').all().order_by('-fecha')
    return render(request, 'ventas/ventas_lista.html', {'ventas': ventas})

@login_required
@user_passes_test(es_cajero, login_url='usuarios:login')
def detalle_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    return render(request, 'ventas/detalle_venta.html', {'venta': venta})

@login_required
@user_passes_test(es_cajero, login_url='usuarios:login')
@transaction.atomic
def eliminar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == 'POST':
        # anular efectos en saldo prepago
        prepago = sum(p.monto for p in venta.pagos.filter(metodo='TARJETA_PREPAGO'))
        venta.alumno.saldo_tarjeta += prepago
        venta.alumno.save()
        venta.delete()
        messages.success(request, f"Venta #{pk} anulada y saldo restituido.")
        return redirect('ventas:ventas_lista')
    return render(request, 'ventas/confirmar_eliminar_venta.html', {'venta': venta})
def reporte_ventas_view(request):
    ventas = Venta.objects.all()
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if fecha_inicio and fecha_fin:
        ventas = ventas.filter(
            fecha__date__gte=fecha_inicio,
            fecha__date__lte=fecha_fin
        )

    total = ventas.aggregate(total=Sum('total'))['total'] or 0

    context = {
        'ventas': ventas,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total': total
    }
    return render(request, 'ventas/reporte_ventas.html', context)
@login_required
def reporte_ventas_pdf(request):
    ventas = Venta.objects.all()
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if fecha_inicio and fecha_fin:
        ventas = ventas.filter(
            fecha__date__gte=fecha_inicio,
            fecha__date__lte=fecha_fin
        )

    total = ventas.aggregate(total=Sum('total'))['total'] or 0
    template = get_template('ventas/reporte_ventas_pdf.html')
    html_content = template.render({
        'ventas': ventas,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total': total
    })

    # Crear archivo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_ventas.pdf"'
    with tempfile.NamedTemporaryFile(delete=True) as temp:
        HTML(string=html_content).write_pdf(target=response)
    return response