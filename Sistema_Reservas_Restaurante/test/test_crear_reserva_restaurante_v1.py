import pytest
from datetime import datetime
from src.restaurante import Restaurante, Reserva

@pytest.fixture
def restaurante_configurado():
    """Fixture que prepara un restaurante con mesas para los tests."""
    r = Restaurante()
    r.agregar_mesa(1, 4, "Interior")
    r.agregar_mesa(2, 2, "Terraza")
    return r

def test_crea_reserva_exitosa(restaurante_configurado):
    """
    Verifica que se puede crear una reserva correctamente 
    cuando los datos son válidos y la mesa está libre.
    """
    fecha = datetime(2026, 5, 20, 20, 0)
    nombre = "Juan Perez"
    telefono = "600123456"
    email = "juan@example.com"
    mesas = [1]
    
    reserva = restaurante_configurado.crear_reserva(
        nombre, telefono, email, mesas, fecha
    )
    
    # Validaciones
    assert isinstance(reserva, Reserva)
    assert reserva.nombre == nombre
    assert reserva.mesas == mesas
    assert len(restaurante_configurado.reservas) == 1
    assert 1 in restaurante_configurado.ocupacion_por_fecha[fecha]

def test_crea_reserva_mesa_ocupada(restaurante_configurado):
    """
    Verifica que el sistema lanza un ValueError si se intenta 
    reservar una mesa que ya está ocupada en ese horario.
    """
    fecha = datetime(2026, 5, 20, 20, 0)
    
    # Primera reserva (exitosa)
    restaurante_configurado.crear_reserva(
        "Cliente 1", "600000001", "c1@mail.com", [1], fecha
    )
    
    # Segunda reserva en la misma mesa y fecha (debe fallar)
    with pytest.raises(ValueError) as excinfo:
        restaurante_configurado.crear_reserva(
            "Cliente 2", "600000002", "c2@mail.com", [1], fecha
        )
    
    assert "Una o más mesas están ocupadas" in str(excinfo.value)
    # Verificar que no se añadió a la lista de reservas
    assert len(restaurante_configurado.reservas) == 1

def test_crea_reserva_mesa_no_existente(restaurante_configurado):
    """Prueba adicional: intentar reservar una mesa que no existe."""
    fecha = datetime(2026, 5, 20, 20, 0)
    
    with pytest.raises(ValueError) as excinfo:
        restaurante_configurado.crear_reserva(
            "Test", "600000000", "test@mail.com", [99], fecha
        )
    
    assert "Mesa 99 no existe" in str(excinfo.value)