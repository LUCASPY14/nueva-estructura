from django.shortcuts import render

def configuracion_general(request):
    return render(request, 'configuracion/general.html', {'title': 'Configuración General'})
