from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Página principal pública
    path('', views.landing, name='landing'),

    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login_simple'),
    path('logout/', auth_views.LogoutView.as_view(next_page='usuarios:login_simple'), name='logout'),
    path('registro/', views.registro_padre, name='registro_padre'),

    # Dashboards por rol
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/cajero/', views.dashboard_cajero, name='dashboard_cajero'),
    path('dashboard/padre/', views.dashboard_padre, name='dashboard_padre'),

    # Gestión de usuarios (solo admin)
    # Cambiar de 'usuarios_lista' a 'lista' para estandarizar
    path('usuarios/', views.usuarios_lista, name='lista'),
    path('usuarios/crear/', views.usuario_crear, name='crear'),
    path('usuarios/<int:pk>/editar/', views.usuario_editar, name='editar'),
    path('usuarios/<int:pk>/eliminar/', views.usuario_eliminar, name='eliminar'),

    # Mantener rutas de autenticación como están
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(
            template_name='registration/password_change_form.html'
        ),
        name='password_change'
    ),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='registration/password_change_done.html'
        ),
        name='password_change_done'
    ),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html'
        ),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
