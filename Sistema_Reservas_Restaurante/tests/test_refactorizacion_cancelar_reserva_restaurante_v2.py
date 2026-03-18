import pytest
from datetime import datetime
from src.restaurante import Restaurante

@pytest.fixture
def restaurante_con_reserva():
    """
    Fixture que prepara un restaurante con mesas y una reserva 
    activa para ser utilizada en los tests de cancelación.
    """
    r = Restaurante()
    r.agregar_mesa(1, 4, "Interior")
    r.agregar_mesa(2, 2, "Terraza")
    
    fecha = datetime(2026, 5, 20, 21, 0)
    # Creamos una reserva inicial (Persistencia atómica)
    reserva = r.crear_reserva("Ana Lopez", "34600111222", "ana@mail.com", [1], fecha)
    return r, reserva, fecha

# --- CASOS NORMALES ---

def test_cancelar_reserva_existente(restaurante_con_reserva):
    """
    Caso Normal: Verifica que al cancelar una reserva válida:
    1. Se elimine de la lista global 'reservas'.
    2. Las mesas se eliminen del conjunto de ocupación (limpieza crítica).
    """
    r, reserva, fecha = restaurante_con_reserva
    
    # Acción de cancelación
    r.cancelar_reserva(reserva)
    
    # Verificaciones
    assert reserva not in r.reservas
    assert len(r.reservas) == 0
    # Verificamos que la mesa 1 ya no figure como ocupada en esa fecha
    assert 1 not in r.ocupacion_por_fecha[fecha]

def test_cancelar_reserva_inexistente(restaurante_con_reserva):
    """
    Caso de Error: Intentar cancelar una reserva que no está en la lista.
    """
    r, reserva, _ = restaurante_con_reserva
    # La cancelamos primero para que deje de existir en el sistema
    r.cancelar_reserva(reserva)
    
    # Intentar cancelarla de nuevo debe lanzar ValueError
    with pytest.raises(ValueError, match="La reserva no existe"):
        r.cancelar_reserva(reserva)

# --- CASOS LÍMITE Y ROBUSTEZ ---

def test_cancelar_reserva_libera_solo_sus_mesas(restaurante_con_reserva):
    """
    Caso Límite: En una misma fecha hay dos reservas distintas. 
    Cancelar una NO debe liberar la mesa de la otra reserva activa.
    """
    r, reserva1, fecha = restaurante_con_reserva
    # Creamos una segunda reserva para la mesa 2 en la misma hora
    reserva2 = r.crear_reserva("Luis", "34600000001", "luis@mail.com", [2], fecha)
    
    # Cancelamos solo la reserva 1
    r.cancelar_reserva(reserva1)
    
    # La mesa 1 debe estar libre, pero la mesa 2 debe seguir bloqueada por reserva2
    assert 1 not in r.ocupacion_por_fecha[fecha]
    assert 2 in r.ocupacion_por_fecha[fecha]
    assert reserva2 in r.reservas

def test_cancelar_reserva_fecha_inexistente_en_mapa(restaurante_con_reserva):
    """
    Caso Límite: Verifica la robustez del método si la fecha de la 
    reserva ya no existe en el mapa de ocupación (por limpieza previa).
    """
    r, reserva, fecha = restaurante_con_reserva
    
    # Eliminamos manualmente la fecha del mapa de ocupación
    del r.ocupacion_por_fecha[fecha]
    
    # El método debe manejarlo sin KeyError gracias a la validación de seguridad
    r.cancelar_reserva(reserva)
    assert reserva not in r.reservas