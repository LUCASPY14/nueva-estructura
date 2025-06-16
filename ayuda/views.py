from django.shortcuts import render

def ayuda_view(request):
    return render(request, 'ayuda/ayuda.html')
