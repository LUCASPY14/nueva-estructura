import random
from typing import Optional

def generate_ean13(seed: Optional[int] = None) -> str:
    """
    Genera un código EAN-13 válido.
    
    Args:
        seed: Semilla opcional para la generación del código
    
    Returns:
        Un string con un código EAN-13 válido
    """
    if seed is not None:
        random.seed(seed)
    
    # Generar los primeros 12 dígitos
    digits = [str(random.randint(0, 9)) for _ in range(12)]
    
    # Calcular el dígito de control
    suma = 0
    for i in range(12):
        digit = int(digits[i])
        if i % 2:
            suma += digit * 3
        else:
            suma += digit
    
    check_digit = (10 - (suma % 10)) % 10
    
    # Añadir el dígito de control
    digits.append(str(check_digit))
    
    return ''.join(digits)

def is_valid_ean13(code: str) -> bool:
    """
    Valida si un código EAN-13 es válido.
    
    Args:
        code: El código EAN-13 a validar
    
    Returns:
        True si el código es válido, False en caso contrario
    """
    if not code.isdigit() or len(code) != 13:
        return False
    
    suma = 0
    for i in range(12):
        digit = int(code[i])
        if i % 2:
            suma += digit * 3
        else:
            suma += digit
    
    check_digit = (10 - (suma % 10)) % 10
    return check_digit == int(code[-1])