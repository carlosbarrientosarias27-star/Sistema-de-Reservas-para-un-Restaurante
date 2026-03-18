import sys
import os
import pytest
from datetime import datetime
from  SRC.restaurante import Restaurante, Reserva

# 1. Obtenemos la ruta absoluta de 'Sistema_Reservas_Restaurante'
# Según tu error, está 2 niveles arriba de 'TEST 1'
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
src_path = os.path.join(base_path, "SRC")

# 2. Añadimos AMBAS rutas al sistema para máxima compatibilidad
if base_path not in sys.path:
    sys.path.insert(0, base_path)
if src_path not in sys.path:
    sys.path.insert(0, src_path)


@pytest.fixture
def restaurante_con_mesas():
    """Fixture que prepara un restaurante con mesas base para los tests."""
    r = Restaurante()
    r.agregar_mesa(1, 2, "interior")
    r.agregar_mesa(2, 4, "terraza")
    r.agregar_mesa(3, 6, "interior")
    return r

# --- TESTS: crear_reserva() ---

def test_crear_reserva_exito(restaurante_con_mesas):
    fecha = datetime(2026, 5, 10, 20, 0)
    reserva = restaurante_con_mesas.crear_reserva("Juan", "600123456", "juan@test.com", [1, 2], fecha)
    
    assert len(restaurante_con_mesas.reservas) == 1
    assert 1 in restaurante_con_mesas.ocupacion_por_fecha[fecha]
    assert reserva.nombre == "Juan"

def test_crear_reserva_mesa_inexistente(restaurante_con_mesas):
    fecha = datetime(2026, 5, 10, 20, 0)
    with pytest.raises(ValueError, match="Mesa 99 no existe"):
        restaurante_con_mesas.crear_reserva("Ana", "600111222", "ana@test.com", [99], fecha)

def test_crear_reserva_conflicto_horario(restaurante_con_mesas):
    fecha = datetime(2026, 5, 10, 20, 0)
    restaurante_con_mesas.crear_reserva("Cliente1", "600111222", "c1@test.com", [1], fecha)
    
    with pytest.raises(ValueError, match="Una o más mesas están ocupadas"):
        restaurante_con_mesas.crear_reserva("Cliente2", "600333444", "c2@test.com", [1], fecha)

# --- TESTS: cancelar_reserva() ---

def test_cancelar_reserva_libera_mesas(restaurante_con_mesas):
    fecha = datetime(2026, 5, 10, 20, 0)
    reserva = restaurante_con_mesas.crear_reserva("Pedro", "600555666", "p@test.com", [1], fecha)
    
    restaurante_con_mesas.cancelar_reserva(reserva)
    
    assert len(restaurante_con_mesas.reservas) == 0
    assert 1 not in restaurante_con_mesas.ocupacion_por_fecha[fecha]

def test_cancelar_reserva_inexistente(restaurante_con_mesas):
    reserva_falsa = Reserva("Fake", "000", "f@test.com", [1], datetime.now())
    with pytest.raises(ValueError, match="La reserva no existe"):
        restaurante_con_mesas.cancelar_reserva(reserva_falsa)

# --- TESTS: buscar_disponibilidad() ---

def test_buscar_disponibilidad_filtro_capacidad(restaurante_con_mesas):
    # Mesa 1 (cap 2), Mesa 2 (cap 4), Mesa 3 (cap 6)
    fecha = datetime(2026, 6, 1, 15, 0)
    
    # Buscamos mesas para 5 personas (Solo debería salir la mesa 3)
    disponibles = restaurante_con_mesas.buscar_disponibilidad(fecha, 5)
    assert disponibles == [3]

def test_buscar_disponibilidad_con_ocupacion(restaurante_con_mesas):
    fecha = datetime(2026, 6, 1, 15, 0)
    restaurante_con_mesas.crear_reserva("User", "600777888", "u@test.com", [2], fecha)
    
    disponibles = restaurante_con_mesas.buscar_disponibilidad(fecha, 2)
    assert 2 not in disponibles
    assert 1 in disponibles
    assert 3 in disponibles

# --- TESTS: calcular_estadisticas() ---

def test_estadisticas_vacias(restaurante_con_mesas):
    stats = restaurante_con_mesas.calcular_estadisticas()
    assert stats["total"] == 0
    assert stats["promedio_mesas"] == 0

def test_estadisticas_con_datos(restaurante_con_mesas):
    fecha = datetime.now()
    restaurante_con_mesas.crear_reserva("C1", "600000001", "1@t.com", [1, 2], fecha) # 2 mesas
    restaurante_con_mesas.crear_reserva("C2", "600000002", "2@t.com", [3], fecha)    # 1 mesa
    
    stats = restaurante_con_mesas.calcular_estadisticas()
    assert stats["total"] == 2
    assert stats["promedio_mesas"] == 1.5  # (2 + 1) / 2

# --- CASOS LÍMITE ---

def test_validar_inputs_nombres_limite(restaurante_con_mesas):
    fecha = datetime.now()
    # Nombre muy corto (1 caracter) - Debería fallar según la lógica de _validar_inputs
    with pytest.raises(ValueError, match="Nombre inválido"):
        restaurante_con_mesas.crear_reserva("A", "600000000", "a@a.com", [1], fecha)
    
    # Nombre exacto en el límite superior (50) - Debería pasar
    nombre_largo = "A" * 50
    reserva = restaurante_con_mesas.crear_reserva(nombre_largo, "600000000", "a@a.com", [1], fecha)
    assert len(reserva.nombre) == 50