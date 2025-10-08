from django.shortcuts import render

def dashboard_reportes(request):
    return render(request, 'reportes/dashboard.html', {'title': 'Dashboard de Reportes'})
