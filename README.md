# LG Service - Sistema de Gesti�n

## Descripci�n

LG Service es un sistema de gesti�n desarrollado con Django para administrar operaciones comerciales. El sistema incluye funcionalidades para gesti�n de ventas, inventario, clientes y reportes.

## Requisitos

- Docker y Docker Compose
- Git

## Configuraci�n

### Configuraci�n del entorno

1. Clone el repositorio:
   `ash
   git clone [url-del-repositorio]
   cd [nombre-del-directorio]
   `

2. Configure las variables de entorno:
   `ash
   cp .env-example .env
   `
   Edite el archivo .env con sus configuraciones personalizadas.

3. Ejecute el script de configuraci�n:
   `ash
   chmod +x setup.sh
   ./setup.sh
   `

### Ejecuci�n manual (alternativa)

1. Inicie los servicios con Docker Compose:
   `ash
   docker-compose -f docker-compose.yml.optimized up -d
   `

2. Ejecute las migraciones:
   `ash
   docker-compose -f docker-compose.yml.optimized exec web python manage.py migrate
   `

3. Acceda a la aplicaci�n en http://localhost:8000

## Estructura del proyecto

`
.
 lgservice/          # Configuraci�n principal de Django
 apps/               # Aplicaciones del proyecto
    core/           # Funcionalidades centrales
    users/          # Gesti�n de usuarios
    ...             # Otras aplicaciones
 static/             # Archivos est�ticos
 templates/          # Plantillas HTML
 Dockerfile          # Configuraci�n de Docker
 docker-compose.yml  # Configuraci�n de Docker Compose
`

## Mejores pr�cticas de seguridad

1. **Variables de entorno**: Nunca almacene credenciales en el c�digo. Use el archivo .env para configuraciones sensibles.

2. **Actualizaciones regulares**: Mantenga las dependencias actualizadas para evitar vulnerabilidades de seguridad.

3. **Backups**: Realice copias de seguridad peri�dicas de la base de datos.

4. **Monitoreo**: Implemente herramientas de monitoreo para detectar comportamientos an�malos.

## Desarrollo

### Entorno de desarrollo

1. Inicie el servidor de desarrollo:
   `ash
   docker-compose -f docker-compose.yml.optimized up
   `

2. Para ejecutar pruebas:
   `ash
   docker-compose -f docker-compose.yml.optimized exec web python manage.py test
   `

### Contribuciones

1. Cree una rama para su funcionalidad: git checkout -b feature/nombre-funcionalidad
2. Realice sus cambios y pruebas
3. Env�e un pull request

## Ventajas de usar Docker

- **Entorno consistente**: Garantiza que todos los desarrolladores trabajen en el mismo entorno.
- **Aislamiento**: Cada servicio se ejecuta en su propio contenedor, evitando conflictos.
- **Portabilidad**: Funciona en cualquier sistema que tenga Docker instalado.
- **Escalabilidad**: Facilita la escalabilidad horizontal de la aplicaci�n.
- **Seguridad**: Mejora la seguridad al aislar los servicios y reducir la superficie de ataque.

## Licencia

[Incluir informaci�n de licencia]

## Contacto

[Incluir informaci�n de contacto]
