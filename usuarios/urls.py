from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login_simple, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_padre, name='registro_padre'),

    # Dashboards por rol
    path('dashboard/admin/', views.admin_dashboard_view, name='dashboard_admin'),
    path('dashboard/cajero/', views.cajero_dashboard_view, name='dashboard_cajero'),
    path('dashboard/padre/', views.padre_dashboard_view, name='dashboard_padre'),
]
