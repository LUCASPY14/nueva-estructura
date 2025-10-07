"""
Configuración Django para el proyecto lgservice.
"""
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Import static files settings
from .static_settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-here'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'usuarios',
    'alumnos',
    'productos',
    'ventas',
    'proveedores',
    'compras',
    'facturacion',
    'reportes',
    'configuracion',
    'tailwind',
    'theme',
    'django_browser_reload',
    'debug_toolbar',
    'compressor',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
]

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        }
    }
}

# Cache settings for reports
REPORT_CACHE_TTL = 3600  # 1 hora
CACHE_MIDDLEWARE_SECONDS = 600  # 10 minutos

# Django Debug Toolbar
INTERNAL_IPS = [
    '127.0.0.1',
]

ROOT_URLCONF = 'lgservice.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'lgservice.wsgi.application'

# ==========================================
# CONFIGURACIÓN DE BASE DE DATOS POSTGRESQL
# ==========================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lgservice_db',
        'USER': 'lgservice_user',
        'PASSWORD': '12345',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# ==========================================
# USUARIO PERSONALIZADO - CRÍTICO
# ==========================================
AUTH_USER_MODEL = 'usuarios.UsuarioLG'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-py'
TIME_ZONE = 'America/Asuncion'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================
# CONFIGURACIONES PARA SISTEMA DE SALDO
# ==========================================

# Tamaño máximo para archivos de comprobante (5MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880

# Formato de fecha y hora
DATETIME_FORMAT = 'd/m/Y H:i'
DATE_FORMAT = 'd/m/Y'
USE_L10N = False

# ==========================================
# CONFIGURACIONES DE EMAIL (OPCIONAL)
# ==========================================

# Para notificaciones por email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ==========================================
# CONFIGURACIONES DE GRUPOS Y PERMISOS
# ==========================================

# Grupos predeterminados del sistema
GRUPOS_SISTEMA = {
    'Cajeros': {
        'permissions': [
            'alumnos.add_transaccionsaldo',
            'alumnos.change_transaccionsaldo',
            'alumnos.view_transaccionsaldo',
            'alumnos.view_alumno',
            'ventas.add_venta',
            'ventas.change_venta',
            'ventas.view_venta',
        ]
    },
    'Padres': {
        'permissions': [
            'alumnos.view_alumno',
            'alumnos.add_transaccionsaldo',
            'alumnos.view_transaccionsaldo',
            'alumnos.view_notificacionpadre',
        ]
    }
}

# ==========================================
# CONFIGURACIONES DE LOGGING
# ==========================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'alumnos': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Crear directorio de logs si no existe
logs_dir = BASE_DIR / 'logs'
if not logs_dir.exists():
    logs_dir.mkdir(exist_ok=True)

# Configuración de Tailwind
TAILWIND_APP_NAME = 'theme'

# Configuración para desarrollo
INTERNAL_IPS = [
    "127.0.0.1",
]
LOGIN_REDIRECT_URL = '/'

"""
Script de verificación del sistema de saldo
Ejecutar con: python verificar_sistema_saldo.py
"""

import os
import sys
import django

# Configurar Django con el settings correcto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lgservice.settings')

try:
    django.setup()
    print("✅ Django configurado correctamente con lgservice.settings")
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    sys.exit(1)

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.urls import reverse, NoReverseMatch


def verificar_configuracion():
    """Verificar configuración básica del sistema"""
    print("\n🔍 VERIFICANDO CONFIGURACIÓN DEL SISTEMA DE SALDO")
    print("=" * 60)
    
    errores = []
    warnings = []
    
    # 0. Información básica del proyecto
    print(f"\n0️⃣  Información del proyecto:")
    print(f"   📁 Directorio: {os.getcwd()}")
    print(f"   ⚙️  Settings: lgservice.settings")
    print(f"   🐍 Python: {sys.version.split()[0]}")
    
    # 1. Verificar apps instaladas
    print("\n1️⃣  Verificando apps instaladas...")
    
    print(f"   📦 Apps instaladas: {len(settings.INSTALLED_APPS)}")
    
    apps_importantes = ['alumnos', 'usuarios', 'ventas', 'productos', 'django.contrib.admin']
    for app in apps_importantes:
        if app in settings.INSTALLED_APPS:
            print(f"   ✅ {app}")
        else:
            if app == 'alumnos':
                errores.append(f"❌ App '{app}' no está en INSTALLED_APPS")
            else:
                warnings.append(f"⚠️  App '{app}' no encontrada")
    
    # 2. Verificar configuración de base de datos
    print("\n2️⃣  Verificando configuración de base de datos...")
    
    if hasattr(settings, 'DATABASES') and settings.DATABASES:
        db_config = settings.DATABASES.get('default', {})
        db_engine = db_config.get('ENGINE', 'No configurado')
        db_name = db_config.get('NAME', 'No configurado')
        print(f"   ✅ Motor de BD: {db_engine}")
        print(f"   ✅ Nombre de BD: {db_name}")
    else:
        errores.append("❌ DATABASES no configurado")
    
    # 3. Verificar configuración de medios
    print("\n3️⃣  Verificando configuración de archivos...")
    
    if hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT:
        print(f"   ✅ MEDIA_ROOT: {settings.MEDIA_ROOT}")
        
        if not os.path.exists(settings.MEDIA_ROOT):
            try:
                os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
                print(f"   ✅ Carpeta MEDIA_ROOT creada")
            except Exception as e:
                warnings.append(f"⚠️  No se pudo crear MEDIA_ROOT: {e}")
    else:
        warnings.append("⚠️  MEDIA_ROOT no configurado")
    
    if hasattr(settings, 'MEDIA_URL') and settings.MEDIA_URL:
        print(f"   ✅ MEDIA_URL: {settings.MEDIA_URL}")
    else:
        warnings.append("⚠️  MEDIA_URL no configurado")
    
    # 4. Verificar modelos de alumnos
    print("\n4️⃣  Verificando modelos de alumnos...")
    
    try:
        from alumnos.models import Alumno
        print("   ✅ Modelo Alumno importado")
        
        # Verificar campos del saldo
        alumno_fields = [f.name for f in Alumno._meta.fields]
        print(f"   📋 Campos encontrados en Alumno: {len(alumno_fields)}")
        
        campos_saldo = ['saldo_tarjeta', 'numero_tarjeta', 'limite_consumo']
        for campo in campos_saldo:
            if campo in alumno_fields:
                print(f"   ✅ Campo '{campo}' presente")
            else:
                warnings.append(f"⚠️  Campo '{campo}' no encontrado en Alumno")
        
        # Intentar importar otros modelos relacionados con saldo
        try:
            from alumnos.models import SolicitudRecarga
            print("   ✅ Modelo SolicitudRecarga importado")
        except ImportError:
            warnings.append("⚠️  Modelo SolicitudRecarga no encontrado")
            
        try:
            from alumnos.models import Transaccion
            print("   ✅ Modelo Transaccion importado")
        except ImportError:
            warnings.append("⚠️  Modelo Transaccion no encontrado")
    
    except ImportError as e:
        errores.append(f"❌ Error importando modelo Alumno: {e}")
    
    # 5. Verificar vistas básicas
    print("\n5️⃣  Verificando vistas...")
    
    try:
        from alumnos import views
        print("   ✅ Módulo de vistas importado")
        
        # Verificar vistas específicas de dashboard
        vistas_dashboard = ['dashboard_padre', 'dashboard_admin', 'dashboard_cajero']
        for vista in vistas_dashboard:
            if hasattr(views, vista):
                print(f"   ✅ Vista '{vista}' encontrada")
            else:
                warnings.append(f"⚠️  Vista '{vista}' no encontrada")
        
        # Verificar vistas de saldo
        vistas_saldo = ['solicitar_recarga', 'consulta_saldo', 'mis_solicitudes']
        for vista in vistas_saldo:
            if hasattr(views, vista):
                print(f"   ✅ Vista '{vista}' encontrada")
            else:
                warnings.append(f"⚠️  Vista '{vista}' no encontrada")
    
    except ImportError as e:
        warnings.append(f"⚠️  Error importando vistas: {e}")
    
    # 6. Verificar URLs
    print("\n6️⃣  Verificando URLs...")
    
    urls_basicas = [
        'alumnos:dashboard_padre',
        'alumnos:dashboard_admin', 
        'alumnos:dashboard_cajero',
        'alumnos:solicitar_recarga',
        'alumnos:consulta_saldo'
    ]
    
    urls_funcionando = 0
    for url_name in urls_basicas:
        try:
            url = reverse(url_name)
            print(f"   ✅ {url_name}: {url}")
            urls_funcionando += 1
        except NoReverseMatch:
            warnings.append(f"⚠️  URL '{url_name}' no encontrada")
        except Exception as e:
            warnings.append(f"⚠️  Error con URL '{url_name}': {e}")
    
    print(f"   📊 URLs funcionando: {urls_funcionando}/{len(urls_basicas)}")
    
    # 7. Verificar estructura de directorios
    print("\n7️⃣  Verificando estructura de directorios...")
    
    directorios = [
        ('alumnos/', '📁 App alumnos'),
        ('alumnos/templates/', '📄 Templates alumnos'),
        ('alumnos/static/', '🎨 Archivos estáticos alumnos'),
        ('templates/', '📄 Templates globales'),
        ('static/', '🎨 Archivos estáticos globales'),
        ('media/', '📷 Archivos de medios'),
        ('usuarios/', '👥 App usuarios')
    ]
    
    for directorio, descripcion in directorios:
        if os.path.exists(directorio):
            print(f"   ✅ {descripcion}: {directorio}")
        else:
            print(f"   ⚠️  {descripcion}: {directorio} (no existe)")
    
    # 8. Verificar base de datos
    print("\n8️⃣  Verificando base de datos...")
    
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("   ✅ Conexión a base de datos OK")
        
        # Verificar si existen tablas principales
        try:
            from alumnos.models import Alumno
            count = Alumno.objects.count()
            print(f"   ✅ Tabla alumnos_alumno: {count} registros")
        except Exception as e:
            warnings.append(f"⚠️  Tabla alumnos_alumno no accesible: {e}")
        
        try:
            from usuarios.models import Usuario
            count = Usuario.objects.count()
            print(f"   ✅ Tabla usuarios_usuario: {count} registros")
        except Exception as e:
            warnings.append(f"⚠️  Tabla usuarios_usuario no accesible: {e}")
            
    except Exception as e:
        errores.append(f"❌ Error de base de datos: {e}")
    
    # 9. Verificar grupos de usuarios
    print("\n9️⃣  Verificando grupos de usuarios...")
    
    # Verificar qué grupos existen
    grupos_existentes = list(Group.objects.values_list('name', flat=True))
    print(f"   📋 Grupos existentes: {grupos_existentes}")
    
    grupos_requeridos = ['PADRE', 'ADMIN', 'CAJERO']
    for grupo in grupos_requeridos:
        if grupo in grupos_existentes:
            print(f"   ✅ Grupo '{grupo}' existe")
        else:
            warnings.append(f"⚠️  Grupo '{grupo}' no existe")
    
    # 10. Verificar formularios
    print("\n🔟 Verificando formularios...")
    
    try:
        from alumnos.forms import SolicitudRecargaForm, ConsultaSaldoForm
        print("   ✅ Formularios de saldo importados")
    except ImportError as e:
        warnings.append(f"⚠️  Formularios de saldo no encontrados: {e}")
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    if errores:
        print(f"❌ ERRORES CRÍTICOS ({len(errores)}):")
        for error in errores:
            print(f"   {error}")
    
    if warnings:
        print(f"\n⚠️  ADVERTENCIAS ({len(warnings)}):")
        for warning in warnings:
            print(f"   {warning}")
    
    if not errores and not warnings:
        print("🎉 ¡SISTEMA COMPLETAMENTE VERIFICADO!")
        return True
    elif not errores:
        print(f"\n✅ Sistema funcional ({len(warnings)} advertencias menores)")
        return True
    else:
        print(f"\n❌ Sistema requiere correcciones ({len(errores)} errores críticos)")
        return False


def crear_datos_prueba():
    """Crear datos de prueba básicos"""
    print("\n🔧 CREANDO DATOS DE PRUEBA")
    print("=" * 40)
    
    try:
        # Crear grupos de roles
        grupos = ['PADRE', 'ADMIN', 'CAJERO']
        for grupo_nombre in grupos:
            grupo, created = Group.objects.get_or_create(name=grupo_nombre)
            if created:
                print(f"   ✅ Grupo '{grupo_nombre}' creado")
            else:
                print(f"   ℹ️  Grupo '{grupo_nombre}' ya existe")
        
        # Crear usuarios de prueba
        usuarios = [
            ('admin_test', 'Admin', 'Test', 'admin123', 'ADMIN'),
            ('padre_test', 'Padre', 'Test', 'padre123', 'PADRE'),
            ('cajero_test', 'Cajero', 'Test', 'cajero123', 'CAJERO')
        ]
        
        for username, first_name, last_name, password, grupo_name in usuarios:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@test.com',
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                user.groups.add(Group.objects.get(name=grupo_name))
                print(f"   ✅ Usuario {username} creado (password: {password})")
            else:
                print(f"   ℹ️  Usuario {username} ya existe")
        
        # Crear alumno de prueba
        try:
            from alumnos.models import Alumno
            from decimal import Decimal
            
            if not Alumno.objects.filter(numero_matricula='TEST001').exists():
                # Verificar qué campos tiene el modelo Alumno
                alumno_data = {
                    'nombre': 'Ana',
                    'apellido': 'Ejemplo',
                    'numero_matricula': 'TEST001',
                    'curso': '3° Grado A',
                    'estado': 'activo'
                }
                
                # Agregar campos de saldo si existen
                alumno_fields = [f.name for f in Alumno._meta.fields]
                if 'saldo_tarjeta' in alumno_fields:
                    alumno_data['saldo_tarjeta'] = Decimal('75000')
                if 'numero_tarjeta' in alumno_fields:
                    alumno_data['numero_tarjeta'] = '999999'
                if 'limite_consumo' in alumno_fields:
                    alumno_data['limite_consumo'] = Decimal('20000')
                
                alumno = Alumno.objects.create(**alumno_data)
                
                # Asociar con padre si el campo existe
                if hasattr(alumno, 'padres'):
                    padre_user = User.objects.get(username='padre_test')
                    alumno.padres.add(padre_user)
                
                print(f"   ✅ Alumno de prueba creado (matrícula: TEST001)")
            else:
                print("   ℹ️  Alumno de prueba ya existe")
                
        except Exception as e:
            print(f"   ❌ Error creando alumno: {e}")
            print("      Posible causa: Migraciones pendientes o modelo sin campos de saldo")
        
        print("\n✅ Datos de prueba configurados!")
        print("\n📋 CREDENCIALES DE PRUEBA:")
        print("   👨‍💼 Admin: admin_test / admin123")
        print("   👨‍👩‍👧‍👦 Padre: padre_test / padre123")
        print("   🔧 Cajero: cajero_test / cajero123")
        
    except Exception as e:
        print(f"❌ Error general creando datos: {e}")


def mostrar_siguientes_pasos():
    """Mostrar los siguientes pasos"""
    print("\n🚀 SIGUIENTES PASOS RECOMENDADOS:")
    print("=" * 40)
    
    print("\n1️⃣  Verificar migraciones:")
    print("   python manage.py showmigrations")
    print("   python manage.py makemigrations")
    print("   python manage.py migrate")
    
    print("\n2️⃣  Probar el servidor:")
    print("   python manage.py runserver")
    print("   http://127.0.0.1:8000/")
    
    print("\n3️⃣  Acceder al admin:")
    print("   http://127.0.0.1:8000/admin")
    print("   (Crear superusuario si es necesario)")
    
    print("\n4️⃣  Ejecutar tests del sistema:")
    print("   python manage.py test alumnos")
    
    print("\n5️⃣  Verificar estructura de URLs:")
    print("   python manage.py show_urls")


if __name__ == "__main__":
    print("🚀 VERIFICACIÓN DEL SISTEMA DE SALDO - LGSERVICE")
    print("=" * 50)
    
    try:
        # Ejecutar verificación
        sistema_ok = verificar_configuracion()
        
        if sistema_ok:
            respuesta = input("\n¿Crear datos de prueba? (s/n): ")
            if respuesta.lower() in ['s', 'sí', 'si', 'y', 'yes']:
                crear_datos_prueba()
        
        mostrar_siguientes_pasos()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Verificación interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")
        print("\nPara más información, ejecuta:")
        print("   python manage.py check")
        
    print("\n🏁 Verificación completada!")
