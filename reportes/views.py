from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import ReporteForm
from .reports import (
    get_ventas_por_periodo, get_compras_por_periodo,
    get_stock_actual, get_consumo_por_alumno, get_finanzas
)

def es_admin(user):
    return user.groups.filter(name='Administradores').exists()

@login_required
@user_passes_test(es_admin, login_url='usuarios:login')
def reporte_selector(request):
    form = ReporteForm(request.GET or None)
    context = {'form': form}
    if form.is_valid():
        s = form.cleaned_data['start_date']
        e = form.cleaned_data['end_date']
        t = form.cleaned_data['tipo_reporte']
        if t == 'ventas':
            data = get_ventas_por_periodo(s, e)
            template = 'reportes/ventas_report.html'
        elif t == 'compras':
            data = get_compras_por_periodo(s, e)
            template = 'reportes/compras_report.html'
        elif t == 'stock':
            data = get_stock_actual()
            template = 'reportes/stock_report.html'
        elif t == 'consumo':
            data = get_consumo_por_alumno(s, e)
            template = 'reportes/consumo_alumno_report.html'
        else:
            data = get_finanzas(s, e)
            template = 'reportes/financiero_report.html'
        context.update({'data': data, 'start_date': s, 'end_date': e})
        return render(request, template, context)
    return render(request, 'reportes/base_report.html', context)