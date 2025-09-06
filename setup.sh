#!/bin/bash

# Script de configuración inicial para el proyecto
set -e

echo "Configurando el entorno para el proyecto..."

# Verificar si .env existe, si no, crear desde .env-example
if [ ! -f ".env" ]; then
    echo "Archivo .env no encontrado. Creando desde .env-example..."
    if [ -f ".env-example" ]; then
        cp .env-example .env
        echo "Por favor, edita el archivo .env con tus configuraciones antes de continuar."
        echo "Presiona Enter cuando hayas terminado..."
        read
    else
        echo "Error: No se encontró el archivo .env-example."
        exit 1
    fi
fi

# Verificar Docker y Docker Compose
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker y/o Docker Compose no están instalados."
    echo "Por favor, instala Docker y Docker Compose antes de continuar."
    exit 1
fi

echo "Iniciando servicios con Docker Compose..."
docker-compose -f docker-compose.yml.optimized up -d

echo "Ejecutando migraciones..."
docker-compose -f docker-compose.yml.optimized exec web python manage.py migrate

echo "Configuración completada. La aplicación está disponible en http://localhost:8000"
