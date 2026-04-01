import re
from datetime import datetime
from Restaurante.config import FORMATO_FECHA 

def validar_email(email: str) -> bool:
    """Comprueba que el email tiene formato básico válido."""
    patron = r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(patron, email.strip()))

def validar_telefono(telefono: str) -> bool:
    """Acepta teléfonos con 9-15 dígitos, espacios y guiones."""
    patron = r"^\+?[\d\s\-]{9,15}$"
    return bool(re.match(patron, telefono.strip()))

def validar_fecha(fecha_str: str) -> datetime | None:
    """
    [4] Parsea la fecha y comprueba que es futura.
    Devuelve el objeto datetime o None si es inválida.
    """
    try:
        fecha = datetime.strptime(fecha_str.strip(), FORMATO_FECHA)
        if fecha <= datetime.now():
            return None  # No se permiten fechas pasadas
        return fecha
    except ValueError:
        return None