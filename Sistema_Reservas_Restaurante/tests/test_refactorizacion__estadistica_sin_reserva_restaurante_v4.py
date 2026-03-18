import pytest
from datetime import datetime
from src.restaurante import Restaurante

@pytest.fixture
def restaurante_base():
    """Prepara un restaurante con mesas configuradas."""
    r = Restaurante()
    r.agregar_mesa(1, 2, "Terraza")
    r.agregar_mesa(2, 4, "Interior")
    r.agregar_mesa(3, 4, "Interior")
    r.agregar_mesa(4, 8, "VIP")
    return r

# --- CASO LÍMITE: SIN DATOS (PASA) ---
def test_estadisticas_sin_reservas(restaurante_base):
    stats = restaurante_base.calcular_estadisticas()
    assert stats["total"] == 0
    assert stats["promedio_mesas"] == 0

# --- CASOS NORMALES (CORREGIDOS) ---

def test_estadisticas_una_reserva(restaurante_base):
    """Verifica el cálculo con una única reserva de una mesa."""
    restaurante_base.crear_reserva(
        "Ana Garcia", "34600111222", "ana@mail.com", [1], datetime.now()
    )
    stats = restaurante_base.calcular_estadisticas()
    
    assert stats["total"] == 1
    assert stats["promedio_mesas"] == 1.0

def test_estadisticas_multiples_reservas_y_mesas(restaurante_base):
    """
    Verifica el promedio cuando hay varias reservas con distinto 
    número de mesas asignadas.
    """
    fecha = datetime.now()
    # Teléfonos corregidos a 9+ dígitos para pasar _validar_inputs
    restaurante_base.crear_reserva("Juan Perez", "34600111000", "juan@mail.com", [1, 2], fecha)
    restaurante_base.crear_reserva("Marta Ruiz", "34600222000", "marta@mail.com", [3], fecha)
    
    stats = restaurante_base.calcular_estadisticas()
    
    # Total mesas: 3 / Total reservas: 2 = 1.5
    assert stats["total"] == 2
    assert stats["promedio_mesas"] == 1.5

# --- CASOS LÍMITE: POST-OPERACIONES (CORREGIDOS) ---

def test_estadisticas_tras_cancelacion(restaurante_base):
    """Verifica que las estadísticas se actualicen al eliminar una reserva."""
    fecha = datetime.now()
    # Teléfono corregido
    reserva = restaurante_base.crear_reserva("Luis Soler", "34600333000", "luis@mail.com", [4], fecha)
    
    assert restaurante_base.calcular_estadisticas()["total"] == 1
    
    restaurante_base.cancelar_reserva(reserva)
    
    stats = restaurante_base.calcular_estadisticas()
    assert stats["total"] == 0
    assert stats["promedio_mesas"] == 0