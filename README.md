# LGservice - Sistema de Gestión de Cantina Escolar

Sistema web para la gestión de ventas, stock y control de alumnos en la cantina del Colegio Santa Teresa de Jesús.

## 🚀 Instalación

```bash
git clone https://github.com/LUCASPY14/nueva-estructura.git
cd nueva-estructura
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Configura tu archivo .env según tus datos de base de datos y claves
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
📂 Estructura de Apps
alumnos: gestión de alumnos y padres.

compras: registro de compras y stock.

facturacion: generación de facturas y reportes PDF.

productos: catálogo y control de productos.

stock: movimientos de inventario.

usuarios: autenticación y gestión de usuarios/roles.

ventas: gestión de ventas, pagos y reportes.

⚙️ Tecnologías
Python 3.x

Django 5.x

PostgreSQL

📄 Licencia
MIT