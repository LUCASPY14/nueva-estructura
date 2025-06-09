from datetime import date

def registrar_venta(request):
    # ...obtén alumno, productos, total...
    hoy = date.today()
    consumido = alumno.total_consumido(fecha=hoy)
    if not venta.sobregiro_autorizado and (consumido + total) > alumno.limite_consumo:
        messages.error(request, "El alumno superó su límite de consumo mensual.")
        return redirect('ventas:nueva_venta')
    # ...continúa con la venta...