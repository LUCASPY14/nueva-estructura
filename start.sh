#!/bin/bash
# filepath: /home/ucas1/nueva_estructura/start.sh

echo "=== Iniciando LGservice en modo desarrollo ==="

# Activar entorno virtual
if [ -d "env" ]; then
    echo "✓ Activando entorno virtual..."
    source env/bin/activate
else
    echo "✗ No se encontró el entorno virtual 'env'"
    exit 1
fi

# Verificar si el puerto está en uso
PORT=8000
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "! Puerto $PORT en uso. Usando puerto alternativo 8002."
    PORT=8002
fi

# Iniciar servidor Tailwind en segundo plano
echo "✓ Iniciando Tailwind CSS..."
python manage.py tailwind start &
TAILWIND_PID=$!

# Función para manejar la terminación del script
cleanup() {
    echo -e "\n=== Deteniendo servicios ==="
    echo "✓ Terminando proceso de Tailwind CSS..."
    kill $TAILWIND_PID 2>/dev/null
    echo "✓ ¡Hasta la próxima!"
    exit 0
}

# Configurar el manejo de señales
trap cleanup SIGINT SIGTERM

# Iniciar servidor Django
echo "✓ Iniciando servidor Django en http://127.0.0.1:$PORT/"
echo "=== LGservice está listo ==="
echo "⚠ Presiona Ctrl+C para detener todos los servicios"
python manage.py runserver $PORT

# Llamar a cleanup al finalizar
cleanup
