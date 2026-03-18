import pytest
from datetime import datetime
from src.restaurante import Restaurante, Reserva

@pytest.fixture
def restaurante_con_reserva():
    """Prepara un restaurante con una mesa y una reserva ya realizada."""
    r = Restaurante()
    r.agregar_mesa(1, 4, "Interior")
    fecha = datetime(2026, 5, 20, 20, 0)
    reserva = r.crear_reserva("Juan Perez", "600123456", "juan@example.com", [1], fecha)
    return r, reserva, fecha

def test_cancelar_reserva_existente(restaurante_con_reserva):
    """
    Verifica que una reserva existente se elimine correctamente
    y que las mesas queden disponibles de nuevo.
    """
    restaurante, reserva, fecha = restaurante_con_reserva
    
    # 1. Aseguramos que la mesa está ocupada antes de cancelar
    assert 1 in restaurante.ocupacion_por_fecha[fecha]
    assert len(restaurante.reservas) == 1
    
    # 2. Ejecutamos la cancelación
    restaurante.cancelar_reserva(reserva)
    
    # 3. Validaciones finales
    assert len(restaurante.reservas) == 0
    # Verificamos que la mesa ya no figura como ocupada en esa fecha
    assert 1 not in restaurante.ocupacion_por_fecha[fecha]

def test_cancelar_reserva_inexistente():
    """
    Verifica que el sistema lanza un ValueError si se intenta 
    cancelar una reserva que no está registrada en el sistema.
    """
    r = Restaurante()
    fecha = datetime(2026, 5, 20, 20, 0)
    # Creamos un objeto reserva manual que NUNCA se agregó al restaurante
    reserva_falsa = Reserva("Intruso", "600000000", "fake@mail.com", [1], fecha)
    
    with pytest.raises(ValueError) as excinfo:
        r.cancelar_reserva(reserva_falsa)
    
    assert "La reserva no existe" in str(excinfo.value)