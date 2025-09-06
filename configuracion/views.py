from django.shortcuts import render, redirect
from .models import ConfiguracionSistema
from .forms import ConfiguracionForm

def configuracion_view(request):
    config, _ = ConfiguracionSistema.objects.get_or_create(id=1)

    if request.method == 'POST':
        form = ConfiguracionForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            return redirect('configuracion:editar_configuracion')
    else:
        form = ConfiguracionForm(instance=config)

    return render(request, 'configuracion/configuracion.html', {'form': form})