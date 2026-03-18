import pytest
from datetime import datetime
from src.restaurante import Restaurante, Reserva

# Fixture para inicializar el restaurante con algunas mesas antes de cada test
@pytest.fixture
def restaurante_configurado():
    r = Restaurante()
    r.agregar_mesa(1, 4, "Interior")
    r.agregar_mesa(2, 2, "Terraza")
    r.agregar_mesa(3, 8, "VIP")
    return r

# --- TESTS PARA crear_reserva() ---

def test_crea_reserva_exitosa(restaurante_configurado):
    """
    Caso Normal: Verifica que una reserva con datos válidos 
    se cree y persista correctamente.
    """
    fecha = datetime(2026, 5, 20, 20, 0)
    reserva = restaurante_configurado.crear_reserva(
        nombre="Juan Perez",
        telefono="34600111222",
        email="juan@example.com",
        mesas=[1, 2],
        fecha_hora=fecha
    )
    
    assert isinstance(reserva, Reserva)
    assert len(restaurante_configurado.reservas) == 1
    assert 1 in restaurante_configurado.ocupacion_por_fecha[fecha]
    assert 2 in restaurante_configurado.ocupacion_por_fecha[fecha]

def test_crea_reserva_mesa_ocupada(restaurante_configurado):
    """
    Caso de Error: Verifica que no se pueda reservar una mesa 
    que ya tiene una reserva en la misma fecha y hora.
    """
    fecha = datetime(2026, 5, 20, 20, 0)
    # Primera reserva
    restaurante_configurado.crear_reserva("Ana", "34600000001", "ana@mail.com", [1], fecha)
    
    # Intento de segunda reserva en la misma mesa y hora
    with pytest.raises(ValueError) as excinfo:
        restaurante_configurado.crear_reserva("Luis", "34600000002", "luis@mail.com", [1], fecha)
    
    assert "Una o más mesas están ocupadas" in str(excinfo.value)

# --- CASOS LÍMITE Y VALIDACIONES ---

@pytest.mark.parametrize("nombre", [
    "A",          # Muy corto (Límite inferior - 1)
    "A" * 51      # Muy largo (Límite superior + 1)
])
def test_crea_reserva_nombre_limite(restaurante_configurado, nombre):
    """Caso Límite: Nombres fuera del rango de 2-50 caracteres."""
    fecha = datetime.now()
    with pytest.raises(ValueError, match="Nombre inválido"):
        restaurante_configurado.crear_reserva(nombre, "34600000000", "test@mail.com", [1], fecha)

def test_crea_reserva_email_invalido(restaurante_configurado):
    """Validación: Formatos de email incorrectos."""
    fecha = datetime.now()
    with pytest.raises(ValueError, match="Formato de email inválido"):
        restaurante_configurado.crear_reserva("Carlos", "34600000000", "email-sin-arroba.com", [1], fecha)

def test_crea_reserva_mesa_inexistente(restaurante_configurado):
    """Caso de Error: Intentar reservar un ID de mesa que no ha sido agregado."""
    fecha = datetime.now()
    with pytest.raises(ValueError, match="Mesa 99 no existe"):
        restaurante_configurado.crear_reserva("Carlos", "34600000000", "c@mail.com", [99], fecha)

def test_crea_reserva_lista_mesas_vacia(restaurante_configurado):
    """Caso Límite: Intentar reservar sin enviar ninguna mesa."""
    fecha = datetime.now()
    with pytest.raises(ValueError, match="lista de mesas válida"):
        restaurante_configurado.crear_reserva("Carlos", "34600000000", "c@mail.com", [], fecha)

def test_reserva_misma_mesa_distinta_hora(restaurante_configurado):
    """
    Caso Normal/Límite: La misma mesa puede ser reservada 
    en horarios diferentes sin conflicto.
    """
    fecha1 = datetime(2026, 5, 20, 14, 0)
    fecha2 = datetime(2026, 5, 20, 21, 0)
    
    r1 = restaurante_configurado.crear_reserva("Comida", "34600000001", "a@mail.com", [1], fecha1)
    r2 = restaurante_configurado.crear_reserva("Cena", "34600000002", "b@mail.com", [1], fecha2)
    
    assert r1 != r2
    assert len(restaurante_configurado.reservas) == 2