from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_ean13(value):
    """
    Validador para códigos EAN-13.
    Verifica que el código tenga 13 dígitos y que el dígito de control sea válido.
    """
    if not value.isdigit():
        raise ValidationError(
            _('%(value)s debe contener solo dígitos'),
            params={'value': value},
        )
    
    if len(value) != 13:
        raise ValidationError(
            _('%(value)s debe tener exactamente 13 dígitos'),
            params={'value': value},
        )
    
    # Cálculo del dígito de control EAN-13
    suma = 0
    for i in range(12):
        digit = int(value[i])
        if i % 2:
            suma += digit * 3
        else:
            suma += digit
    
    check_digit = (10 - (suma % 10)) % 10
    
    if check_digit != int(value[-1]):
        raise ValidationError(
            _('%(value)s no es un código EAN-13 válido'),
            params={'value': value},
        )