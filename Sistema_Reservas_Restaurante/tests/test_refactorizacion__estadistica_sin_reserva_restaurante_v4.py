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

# --- CASO LÍMITE: SIN DATOS ---

def test_estadisticas_sin_reservas(restaurante_base):
    """
    Verifica que el sistema maneje correctamente la ausencia de reservas
    evitando errores de división por cero.
    """
    stats = restaurante_base.calcular_estadisticas()
    
    assert stats["total"] == 0
    assert stats["promedio_mesas"] == 0

# --- CASOS NORMALES ---

def test_estadisticas_una_reserva(restaurante_base):
    """Verifica el cálculo con una única reserva de una mesa."""
    restaurante_base.crear_reserva(
        "Ana", "123456789", "ana@mail.com", [1], datetime.now()
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
    # Reserva 1: 2 mesas (IDs 1 y 2)
    restaurante_base.crear_reserva("Juan", "111", "j@mail.com", [1, 2], fecha)
    # Reserva 2: 1 mesa (ID 3)
    restaurante_base.crear_reserva("Marta", "222", "m@mail.com", [3], fecha)
    
    stats = restaurante_base.calcular_estadisticas()
    
    # Total reservas: 2
    # Total mesas: 3 (2 + 1)
    # Promedio: 3 / 2 = 1.5
    assert stats["total"] == 2
    assert stats["promedio_mesas"] == 1.5

# --- CASOS LÍMITE: POST-OPERACIONES ---

def test_estadisticas_tras_cancelacion(restaurante_base):
    """
    Verifica que las estadísticas se actualicen correctamente 
    al eliminar una reserva del sistema.
    """
    fecha = datetime.now()
    reserva = restaurante_base.crear_reserva("Luis", "333", "l@mail.com", [4], fecha)
    
    # Antes de cancelar: total 1
    assert restaurante_base.calcular_estadisticas()["total"] == 1
    
    restaurante_base.cancelar_reserva(reserva)
    
    # Después de cancelar: vuelve a 0
    stats = restaurante_base.calcular_estadisticas()
    assert stats["total"] == 0
    assert stats["promedio_mesas"] == 0