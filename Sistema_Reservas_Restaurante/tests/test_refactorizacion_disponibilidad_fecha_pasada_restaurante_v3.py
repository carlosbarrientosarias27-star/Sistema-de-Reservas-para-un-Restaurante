import pytest
from datetime import datetime, timedelta
from src.restaurante import Restaurante

@pytest.fixture
def restaurante_con_mesas():
    """Configuración de un restaurante con mesas de distintas capacidades."""
    r = Restaurante()
    r.agregar_mesa(1, 2, "Terraza") # Pequeña
    r.agregar_mesa(2, 4, "Interior") # Mediana
    r.agregar_mesa(3, 8, "VIP")      # Grande
    return r

# --- CASOS NORMALES ---

def test_disponibilidad_exitosa_todas(restaurante_con_mesas):
    """
    Caso Normal: Verifica que si no hay reservas, todas las mesas 
    con capacidad suficiente aparezcan como disponibles.
    """
    fecha = datetime(2026, 6, 1, 20, 0)
    # Buscamos para 2 personas: las 3 mesas cumplen (capacidad 2, 4 y 8)
    disponibles = restaurante_con_mesas.buscar_disponibilidad(fecha, 2)
    
    assert len(disponibles) == 3
    assert set(disponibles) == {1, 2, 3}

def test_disponibilidad_filtro_capacidad(restaurante_con_mesas):
    """
    Caso Normal: Verifica que solo se devuelvan mesas que igualen 
    o superen la capacidad mínima solicitada.
    """
    fecha = datetime(2026, 6, 1, 20, 0)
    # Buscamos mesa para 6 personas: solo la mesa 3 (capacidad 8) sirve
    disponibles = restaurante_con_mesas.buscar_disponibilidad(fecha, 6)
    
    assert disponibles == [3]

def test_disponibilidad_con_mesa_ocupada(restaurante_con_mesas):
    """
    Caso Normal: Una mesa ocupada por una reserva no debe 
    aparecer en la búsqueda para esa misma fecha y hora.
    """
    fecha = datetime(2026, 6, 1, 20, 0)
    # Reservamos la mesa 2 usando el nuevo flujo refactorizado
    restaurante_con_mesas.crear_reserva("Cliente", "34600000000", "c@mail.com", [2], fecha)
    
    disponibles = restaurante_con_mesas.buscar_disponibilidad(fecha, 2)
    
    # La mesa 2 debe estar excluida de los resultados
    assert 2 not in disponibles
    assert set(disponibles) == {1, 3}

# --- CASOS LÍMITE ---

def test_disponibilidad_fecha_pasada(restaurante_con_mesas):
    """
    Caso Límite: Buscar disponibilidad en una fecha anterior a la actual.
    El sistema debe informar las mesas físicas disponibles en ese momento
    del tiempo (generalmente todas, a menos que hubiera una reserva histórica).
    """
    fecha_ayer = datetime.now() - timedelta(days=1)
    disponibles = restaurante_con_mesas.buscar_disponibilidad(fecha_ayer, 1)
    
    # El sistema no bloquea la consulta cronológica, devuelve disponibilidad técnica
    assert len(disponibles) == 3

def test_disponibilidad_capacidad_excedida(restaurante_con_mesas):
    """
    Caso Límite: Se solicita una capacidad mayor a la de cualquier mesa existente.
    """
    fecha = datetime(2026, 12, 31, 22, 0)
    # Ninguna mesa tiene capacidad para 20 personas
    disponibles = restaurante_con_mesas.buscar_disponibilidad(fecha, 20)
    
    assert disponibles == []

def test_disponibilidad_sin_mesas_en_sistema():
    """
    Caso Límite: Buscar en un restaurante que no tiene mesas registradas.
    """
    r_vacio = Restaurante()
    disponibles = r_vacio.buscar_disponibilidad(datetime.now(), 1)
    
    assert disponibles == []