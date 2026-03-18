import pytest
from datetime import datetime
from src.restaurante import Restaurante

@pytest.fixture
def restaurante_con_datos():
    """Configuración inicial con mesas y una reserva activa."""
    r = Restaurante()
    r.agregar_mesa(1, 4, "Interior")
    r.agregar_mesa(2, 2, "Terraza")
    
    fecha = datetime(2026, 5, 20, 21, 0)
    # Creamos una reserva inicial para las pruebas de cancelación
    reserva = r.crear_reserva("Ana Lopez", "34600111222", "ana@mail.com", [1], fecha)
    return r, reserva, fecha

# --- TESTS PARA cancelar_reserva() ---

def test_cancelar_reserva_existente(restaurante_con_datos):
    """
    Caso Normal: Verifica que al cancelar una reserva existente:
    1. Se elimine de la lista de reservas.
    2. Las mesas queden libres para esa fecha/hora.
    """
    r, reserva, fecha = restaurante_con_datos
    
    # Acción
    r.cancelar_reserva(reserva)
    
    # Verificaciones
    assert reserva not in r.reservas
    assert len(r.reservas) == 0
    # Verificar limpieza crítica de ocupación
    assert 1 not in r.ocupacion_por_fecha[fecha]

def test_cancelar_reserva_inexistente(restaurante_con_datos):
    """
    Caso de Error: Intentar cancelar una reserva que no está en el sistema
    o que ya fue cancelada previamente.
    """
    r, reserva, _ = restaurante_con_datos
    r.cancelar_reserva(reserva) # Cancelación exitosa
    
    # Intentar cancelar la misma reserva por segunda vez
    with pytest.raises(ValueError, match="La reserva no existe"):
        r.cancelar_reserva(reserva)

# --- CASOS LÍMITE Y ESCENARIOS COMPLEJOS ---

def test_cancelar_reserva_libera_solo_sus_mesas(restaurante_con_datos):
    """
    Caso Límite: En una fecha con múltiples reservas, cancelar una 
    NO debe liberar las mesas de las otras.
    """
    r, reserva1, fecha = restaurante_con_datos
    # Crear una segunda reserva en la misma fecha pero distinta mesa
    reserva2 = r.crear_reserva("Luis", "34600000001", "luis@mail.com", [2], fecha)
    
    # Cancelar solo la reserva 1
    r.cancelar_reserva(reserva1)
    
    # La mesa 1 debe estar libre, pero la mesa 2 debe seguir ocupada
    assert 1 not in r.ocupacion_por_fecha[fecha]
    assert 2 in r.ocupacion_por_fecha[fecha]
    assert reserva2 in r.reservas

def test_cancelar_reserva_fecha_inexistente_en_mapa(restaurante_con_datos):
    """
    Caso Límite/Robustez: Verifica que el sistema no falle si intentamos
    cancelar una reserva cuya fecha ya no existe en el mapa de ocupación.
    """
    r, reserva, fecha = restaurante_con_datos
    
    # Simulamos una corrupción manual del mapa de ocupación o limpieza previa
    del r.ocupacion_por_fecha[fecha]
    
    # El método debe manejarlo sin lanzar error gracias al 'if' de seguridad
    r.cancelar_reserva(reserva)
    assert reserva not in r.reservas