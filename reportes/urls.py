from django.urls import path
from . import views

app_name = 'reportes'
urlpatterns = [
    path('', views.reporte_selector, name='reporte_selector'),
]