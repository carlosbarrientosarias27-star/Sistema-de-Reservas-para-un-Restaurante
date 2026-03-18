import pytest
from datetime import datetime
from src.restaurante import Restaurante, Reserva

@pytest.fixture
def restaurante_inicializado():
    """Fixture que prepara el entorno con mesas predefinidas."""
    r = Restaurante()
    r.agregar_mesa(1, 4, "Interior")
    r.agregar_mesa(2, 2, "Terraza")
    r.agregar_mesa(3, 8, "VIP")
    return r

# --- CASOS NORMALES ---

def test_crear_reserva_exitosa(restaurante_inicializado):
    """Verifica la creación de una reserva con todos los datos válidos."""
    fecha = datetime(2026, 5, 20, 20, 0)
    reserva = restaurante_inicializado.crear_reserva(
        nombre="Juan Perez",
        telefono="34600111222",
        email="juan@example.com",
        mesas=[1, 2],
        fecha_hora=fecha
    )
    
    # Verificamos persistencia y tipos
    assert isinstance(reserva, Reserva)
    assert len(restaurante_inicializado.reservas) == 1
    # Verificamos que las mesas estén marcadas como ocupadas en esa fecha
    assert 1 in restaurante_inicializado.ocupacion_por_fecha[fecha]
    assert 2 in restaurante_inicializado.ocupacion_por_fecha[fecha]

def test_crear_reserva_mesa_ocupada(restaurante_inicializado):
    """Verifica que el sistema impida reservar mesas ya ocupadas en el mismo horario."""
    fecha = datetime(2026, 5, 20, 20, 0)
    # Primera reserva que ocupa la mesa 1
    restaurante_inicializado.crear_reserva("Ana", "34600000001", "ana@mail.com", [1], fecha)
    
    # Intento de segunda reserva para la misma mesa y hora
    with pytest.raises(ValueError, match="Una o más mesas están ocupadas"):
        restaurante_inicializado.crear_reserva("Luis", "34600000002", "luis@mail.com", [1], fecha)

# --- CASOS LÍMITE Y VALIDACIONES ---

@pytest.mark.parametrize("nombre_invalido", [
    "A",          # Límite inferior (solo 1 caracter)
    "A" * 51      # Límite superior (51 caracteres)
])
def test_crear_reserva_nombre_limite(restaurante_inicializado, nombre_invalido):
    """Valida los límites de longitud del nombre (2-50 caracteres)."""
    fecha = datetime.now()
    with pytest.raises(ValueError, match="Nombre inválido"):
        restaurante_inicializado.crear_reserva(nombre_invalido, "34600000000", "test@mail.com", [1], fecha)

def test_crear_reserva_email_formato_invalido(restaurante_inicializado):
    """Valida que el regex de email bloquee formatos incorrectos."""
    fecha = datetime.now()
    with pytest.raises(ValueError, match="Formato de email inválido"):
        restaurante_inicializado.crear_reserva("Carlos", "34600000000", "usuario_at_dominio.com", [1], fecha)

def test_crear_reserva_lista_mesas_vacia(restaurante_inicializado):
    """Caso límite: No se puede crear una reserva sin asignar mesas."""
    fecha = datetime.now()
    with pytest.raises(ValueError, match="lista de mesas válida"):
        restaurante_inicializado.crear_reserva("Carlos", "34600000000", "c@mail.com", [], fecha)

def test_crear_reserva_mesa_inexistente(restaurante_inicializado):
    """Caso de error: Se intenta reservar un ID de mesa que no ha sido registrado."""
    fecha = datetime.now()
    with pytest.raises(ValueError, match="Mesa 99 no existe"):
        restaurante_inicializado.crear_reserva("Carlos", "34600000000", "c@mail.com", [99], fecha)