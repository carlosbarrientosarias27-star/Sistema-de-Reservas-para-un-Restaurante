import pytest
from datetime import datetime
from src.restaurante import Restaurante

@pytest.fixture
def restaurante_con_mesas():
    """Configuración básica de un restaurante."""
    r = Restaurante()
    r.agregar_mesa(1, 4, "Interior")
    r.agregar_mesa(2, 2, "Terraza")
    r.agregar_mesa(3, 8, "VIP")
    return r

# --- TESTS PARA calcular_estadisticas() ---

def test_estadisticas_sin_reservas(restaurante_con_mesas):
    """
    Caso Límite: Verifica que el sistema no falle si se piden 
    estadísticas de un restaurante vacío.
    """
    stats = restaurante_con_mesas.calcular_estadisticas()
    
    assert stats["total"] == 0
    assert stats["promedio_mesas"] == 0

def test_estadisticas_calculo_correcto(restaurante_con_mesas):
    """
    Caso Normal: Verifica el cálculo del promedio de mesas por reserva.
    """
    fecha = datetime(2026, 5, 20, 20, 0)
    
    # Reserva 1: usa 2 mesas (IDs 1 y 2)
    restaurante_con_mesas.crear_reserva("Juan", "34600111222", "j@mail.com", [1, 2], fecha)
    # Reserva 2: usa 1 mesa (ID 3)
    restaurante_con_mesas.crear_reserva("Ana", "34600000001", "a@mail.com", [3], fecha)
    
    stats = restaurante_con_mesas.calcular_estadisticas()
    
    # Total de reservas: 2
    # Total de mesas: 3 (2 + 1)
    # Promedio esperado: 3 / 2 = 1.5
    assert stats["total"] == 2
    assert stats["promedio_mesas"] == 1.5

# --- CASOS LÍMITE Y ROBUSTEZ ---

def test_estadisticas_post_cancelacion(restaurante_con_mesas):
    """
    Caso Límite: Las estadísticas deben actualizarse en tiempo real 
    si se cancela una reserva.
    """
    fecha = datetime(2026, 5, 20, 20, 0)
    reserva = restaurante_con_mesas.crear_reserva("Juan", "34600111222", "j@mail.com", [1], fecha)
    
    # Antes de cancelar
    assert restaurante_con_mesas.calcular_estadisticas()["total"] == 1
    
    # Después de cancelar
    restaurante_con_mesas.cancelar_reserva(reserva)
    stats = restaurante_con_mesas.calcular_estadisticas()
    
    assert stats["total"] == 0
    assert stats["promedio_mesas"] == 0

def test_estadisticas_mesas_multiples(restaurante_con_mesas):
    """
    Caso Límite: Reserva de gran tamaño para verificar la suma total de mesas.
    """
    fecha = datetime(2026, 12, 1, 22, 0)
    # Una sola reserva que toma todas las mesas (3 mesas)
    restaurante_con_mesas.crear_reserva("Grupo", "34600000000", "g@mail.com", [1, 2, 3], fecha)
    
    stats = restaurante_con_mesas.calcular_estadisticas()
    
    assert stats["total"] == 1
    assert stats["promedio_mesas"] == 3.0