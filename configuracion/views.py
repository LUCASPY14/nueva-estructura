from django.shortcuts import render

def configuracion_view(request):
    return render(request, 'configuracion/configuracion.html')
