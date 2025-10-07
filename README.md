# Nueva Estructura

## Instalación

1. Clona el repositorio:
   ```sh
   git clone https://github.com/tu_usuario/nueva_estructura.git
   cd nueva_estructura
   ```

2. Crea y activa un entorno virtual:
   ```sh
   python3 -m venv env
   source env/bin/activate
   ```

3. Instala las dependencias:
   ```sh
   pip install -r requirements.txt
   ```

4. Realiza las migraciones:
   ```sh
   python manage.py migrate
   ```

5. Crea un superusuario:
   ```sh
   python manage.py createsuperuser
   ```

6. Ejecuta el servidor:
   ```sh
   python manage.py runserver
   ```

## Uso

- Accede a la administración en `http://localhost:8000/admin/`
- Sigue las reglas de negocio y flujos definidos en la documentación interna del proyecto.

## Variables de entorno

- Configura tus claves y secretos en un archivo `.env` (no lo subas al repositorio).

## Backup

- Realiza backups regulares de la base de datos con:
  ```sh
  python manage.py dumpdata > backup.json
  ````

# LGservice

## Configuración del Entorno de Desarrollo

### Requisitos Previos
- Python 3.8 o superior
- Entorno virtual (virtualenv o venv)
- Node.js y npm (para Tailwind CSS)
- PostgreSQL (configurado en un puerto diferente al 8000/8002)

### Inicio Rápido del Servidor de Desarrollo

Para iniciar el servidor de desarrollo con soporte de Tailwind CSS, utilizamos un script personalizado:

```bash
[start.sh](http://_vscodecontentref_/3)
```