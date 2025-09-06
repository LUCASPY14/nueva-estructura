from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Alumno
from .serializers import AlumnoSerializer
from ventas.models import Venta
from ventas.serializers import VentaSerializer




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hijos_del_padre(request):
    padre = request.user.padre_profile  # accede al padre conectado
    hijos = Alumno.objects.filter(padre=padre)
    serializer = AlumnoSerializer(hijos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalle_alumno(request, alumno_id):
    user = request.user

    try:
        alumno = Alumno.objects.get(id=alumno_id, padre=user.padre_profile)
    except Alumno.DoesNotExist:
        return Response({'error': 'Alumno no encontrado o no pertenece al padre'}, status=404)

    saldo = alumno.saldo_tarjeta
    ventas = Venta.objects.filter(alumno=alumno).order_by('-fecha')[:10]  # últimos 10 movimientos
    ventas_serializadas = VentaSerializer(ventas, many=True)

    return Response({
        'alumno': {
            'id': alumno.id,
            'nombre': alumno.nombre,
            'apellido': alumno.apellido,
            'saldo_tarjeta': saldo,
        },
        'movimientos': ventas_serializadas.data
    })
