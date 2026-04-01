import pytest
import os
import json
from datetime import datetime, timedelta


from Restaurante.core.sistema import SistemaReservas


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def fecha_futura(horas: int = 48) -> str:
    """Devuelve una fecha futura en el formato esperado por el sistema."""
    fecha = datetime.now() + timedelta(hours=horas)
    return fecha.strftime("%Y-%m-%d %H:%M")


# ─────────────────────────────────────────
# FIXTURES  — evitan repetir código
# ─────────────────────────────────────────

@pytest.fixture
def sistema(tmp_path):
    """
    Crea un SistemaReservas limpio para cada test.
    Usa tmp_path (directorio temporal de pytest) para no
    contaminar datos reales entre tests.
    """
    ruta = str(tmp_path / "test_reservas.json")
    return SistemaReservas(ruta=ruta)


@pytest.fixture
def sistema_con_reserva(sistema):
    """
    Sistema con una reserva activa ya creada.
    Útil para tests que necesitan una reserva preexistente.
    """
    sistema.crear_reserva(
        nombre="Ana García",
        telefono="600111222",
        email="ana@mail.com",
        numero_mesa=2,
        fecha_str=fecha_futura(48),
        comensales=3,
    )
    return sistema


# ─────────────────────────────────────────
# GRUPO 1 — CREAR RESERVA (casos felices)
# ─────────────────────────────────────────

class TestCrearReserva:

    def test_crear_reserva_exitosa(self, sistema):
        """Una reserva válida debe crearse correctamente."""
        resultado = sistema.crear_reserva(
            "Ana García", "600111222", "ana@mail.com",
            2, fecha_futura(48), 3
        )
        assert "ok" in resultado
        assert resultado["reserva"]["nombre"] == "Ana García"
        assert resultado["reserva"]["estado"] == "activa"
        assert resultado["reserva"]["id"] == 1

    def test_crear_reserva_asigna_id_incremental(self, sistema):
        """Cada reserva debe recibir un ID único e incremental."""
        r1 = sistema.crear_reserva("Ana García", "600111222", "ana@mail.com",
                                   2, fecha_futura(24), 2)
        r2 = sistema.crear_reserva("Luis Pérez", "600333444", "luis@mail.com",
                                   3, fecha_futura(48), 4)
        assert r1["reserva"]["id"] == 1
        assert r2["reserva"]["id"] == 2

    def test_crear_reserva_guarda_zona_correcta(self, sistema):
        """La zona debe corresponder a la mesa seleccionada."""
        resultado = sistema.crear_reserva(
            "Ana García", "600111222", "ana@mail.com",
            3, fecha_futura(48), 2  # Mesa 3 = terraza
        )
        assert resultado["reserva"]["zona"] == "terraza"

    def test_crear_varias_reservas_misma_mesa_distinta_hora(self, sistema):
        """La misma mesa puede reservarse en horas diferentes."""
        r1 = sistema.crear_reserva("Ana García", "600111222", "ana@mail.com",
                                   2, fecha_futura(24), 2)
        r2 = sistema.crear_reserva("Luis Pérez", "600333444", "luis@mail.com",
                                   2, fecha_futura(48), 2)
        assert "ok" in r1
        assert "ok" in r2


# ─────────────────────────────────────────
# GRUPO 2 — CREAR RESERVA (casos de error)
# ─────────────────────────────────────────

class TestCrearReservaErrores:

    def test_crear_reserva_mesa_ocupada(self, sistema):
        """No se puede reservar una mesa ya ocupada en la misma fecha/hora."""
        fecha = fecha_futura(48)
        sistema.crear_reserva("Ana García", "600111222", "ana@mail.com",
                               2, fecha, 3)
        resultado = sistema.crear_reserva("Luis Pérez", "600333444", "luis@mail.com",
                                          2, fecha, 2)
        assert "error" in resultado
        assert "ocupada" in resultado["error"].lower()

    def test_crear_reserva_fecha_pasada(self, sistema):
        """No se puede reservar en una fecha pasada."""
        resultado = sistema.crear_reserva(
            "Ana García", "600111222", "ana@mail.com",
            2, "2020-01-01 21:00", 3
        )
        assert "error" in resultado
        assert "fecha" in resultado["error"].lower()

    def test_crear_reserva_email_invalido(self, sistema):
        """Un email sin formato válido debe ser rechazado."""
        resultado = sistema.crear_reserva(
            "Ana García", "600111222", "esto-no-es-un-email",
            2, fecha_futura(48), 3
        )
        assert "error" in resultado
        assert "email" in resultado["error"].lower()

    def test_crear_reserva_telefono_invalido(self, sistema):
        """Un teléfono con letras debe ser rechazado."""
        resultado = sistema.crear_reserva(
            "Ana García", "no-es-telefono", "ana@mail.com",
            2, fecha_futura(48), 3
        )
        assert "error" in resultado
        assert "teléfono" in resultado["error"].lower()

    def test_crear_reserva_mesa_inexistente(self, sistema):
        """Una mesa con número fuera de rango debe ser rechazada."""
        resultado = sistema.crear_reserva(
            "Ana García", "600111222", "ana@mail.com",
            99, fecha_futura(48), 3
        )
        assert "error" in resultado

    def test_crear_reserva_excede_capacidad(self, sistema):
        """No se puede reservar con más comensales que la capacidad de la mesa."""
        resultado = sistema.crear_reserva(
            "Ana García", "600111222", "ana@mail.com",
            1, fecha_futura(48), 10  # Mesa 1 tiene capacidad 2
        )
        assert "error" in resultado
        assert "capacidad" in resultado["error"].lower()

    def test_crear_reserva_nombre_vacio(self, sistema):
        """Un nombre vacío debe ser rechazado."""
        resultado = sistema.crear_reserva(
            "", "600111222", "ana@mail.com",
            2, fecha_futura(48), 3
        )
        assert "error" in resultado

    def test_crear_reserva_limite_por_cliente(self, sistema):
        """Un cliente no puede tener más de 5 reservas activas simultáneas."""
        for i in range(5):
            sistema.crear_reserva(
                "Ana García", "600111222", "ana@mail.com",
                (i % 5) + 1,           # Usa mesas 1-5 rotando
                fecha_futura(24 + i),  # Horas distintas para no solapar
                1,
            )
        # La sexta debe fallar
        resultado = sistema.crear_reserva(
            "Ana García", "600111222", "ana@mail.com",
            1, fecha_futura(100), 1
        )
        assert "error" in resultado
        assert "límite" in resultado["error"].lower()

    def test_crear_reserva_comensales_negativos(self, sistema):
        """Un número de comensales negativo debe ser rechazado."""
        resultado = sistema.crear_reserva(
            "Ana García", "600111222", "ana@mail.com",
            2, fecha_futura(48), -1
        )
        assert "error" in resultado

    def test_sanitizacion_elimina_caracteres_peligrosos(self, sistema):
        """Los caracteres peligrosos en el nombre deben ser eliminados."""
        resultado = sistema.crear_reserva(
            "<script>Ana</script>", "600111222", "ana@mail.com",
            2, fecha_futura(48), 2
        )
        # Si se crea la reserva, el nombre debe estar limpio
        if "ok" in resultado:
            assert "<" not in resultado["reserva"]["nombre"]
            assert ">" not in resultado["reserva"]["nombre"]


# ─────────────────────────────────────────
# GRUPO 3 — CANCELAR RESERVA
# ─────────────────────────────────────────

class TestCancelarReserva:

    def test_cancelar_reserva_existente(self, sistema_con_reserva):
        """Cancelar una reserva activa debe cambiar su estado a 'cancelada'."""
        resultado = sistema_con_reserva.cancelar_reserva(1)
        assert "ok" in resultado

    def test_cancelar_reserva_cambia_estado(self, sistema_con_reserva):
        """Tras cancelar, el estado de la reserva debe ser 'cancelada'."""
        sistema_con_reserva.cancelar_reserva(1)
        reserva = sistema_con_reserva._idx_id.get(1)
        assert reserva["estado"] == "cancelada"

    def test_cancelar_reserva_inexistente(self, sistema):
        """Cancelar un ID que no existe debe devolver error."""
        resultado = sistema.cancelar_reserva(999)
        assert "error" in resultado

    def test_cancelar_reserva_ya_cancelada(self, sistema_con_reserva):
        """Cancelar una reserva ya cancelada debe devolver error."""
        sistema_con_reserva.cancelar_reserva(1)
        resultado = sistema_con_reserva.cancelar_reserva(1)
        assert "error" in resultado

    def test_cancelar_libera_mesa(self, sistema_con_reserva):
        """Tras cancelar, la mesa debe quedar disponible en esa fecha/hora."""
        fecha = list(sistema_con_reserva._idx_mesa.keys())[0][1]
        sistema_con_reserva.cancelar_reserva(1)
        assert sistema_con_reserva._mesa_libre(2, fecha)


# ─────────────────────────────────────────
# GRUPO 4 — DISPONIBILIDAD
# ─────────────────────────────────────────

class TestDisponibilidad:

    def test_mesa_libre_sin_reservas(self, sistema):
        """Una mesa sin reservas debe estar disponible."""
        assert sistema._mesa_libre(2, fecha_futura(48)) is True

    def test_mesa_ocupada_tras_reserva(self, sistema):
        """Una mesa reservada no debe estar disponible en esa fecha/hora."""
        fecha = fecha_futura(48)
        sistema.crear_reserva("Ana García", "600111222", "ana@mail.com",
                               2, fecha, 3)
        assert sistema._mesa_libre(2, fecha) is False

    def test_mesa_libre_en_hora_diferente(self, sistema):
        """Una mesa reservada a las 21:00 debe estar libre a las 22:00."""
        sistema.crear_reserva("Ana García", "600111222", "ana@mail.com",
                               2, fecha_futura(48), 3)
        assert sistema._mesa_libre(2, fecha_futura(72)) is True


# ─────────────────────────────────────────
# GRUPO 5 — CONSULTAR CLIENTE
# ─────────────────────────────────────────

class TestConsultarCliente:

    def test_consultar_cliente_con_reservas(self, sistema_con_reserva):
        """Un cliente con reservas activas debe aparecer en la consulta."""
        lista = sistema_con_reserva.consultar_cliente("Ana García")
        assert len(lista) == 1
        assert lista[0]["nombre"] == "Ana García"

    def test_consultar_cliente_sin_reservas(self, sistema):
        """Un cliente sin reservas debe devolver lista vacía."""
        lista = sistema.consultar_cliente("Cliente Fantasma")
        assert lista == []

    def test_consultar_cliente_insensible_mayusculas(self, sistema_con_reserva):
        """La búsqueda debe funcionar independientemente de mayúsculas."""
        lista = sistema_con_reserva.consultar_cliente("ANA GARCÍA")
        assert len(lista) == 1

    def test_consultar_no_muestra_canceladas(self, sistema_con_reserva):
        """Las reservas canceladas no deben aparecer en la consulta."""
        sistema_con_reserva.cancelar_reserva(1)
        lista = sistema_con_reserva.consultar_cliente("Ana García")
        assert lista == []


# ─────────────────────────────────────────
# GRUPO 6 — ESTADÍSTICAS
# ─────────────────────────────────────────

class TestEstadisticas:

    def test_estadisticas_sin_reservas(self, sistema):
        """Con el sistema vacío, las estadísticas deben informarlo."""
        resultado = sistema.calcular_estadisticas()
        assert "mensaje" in resultado

    def test_estadisticas_mesa_mas_reservada(self, sistema):
        """La mesa con más reservas debe identificarse correctamente."""
        # Mesa 2 aparece 2 veces, mesa 3 solo 1 vez
        sistema.crear_reserva("Ana García", "600111222", "ana@mail.com",
                               2, fecha_futura(24), 2)
        sistema.crear_reserva("Luis Pérez", "600333444", "luis@mail.com",
                               2, fecha_futura(48), 2)
        sistema.crear_reserva("María López", "600555666", "maria@mail.com",
                               3, fecha_futura(72), 2)
        stats = sistema.calcular_estadisticas()
        assert "2" in stats["mesa_mas_reservada"]

    def test_estadisticas_cliente_frecuente(self, sistema):
        """El cliente con más reservas debe identificarse correctamente."""
        sistema.crear_reserva("Ana García", "600111222", "ana@mail.com",
                               2, fecha_futura(24), 2)
        sistema.crear_reserva("Ana García", "600111222", "ana@mail.com",
                               3, fecha_futura(48), 2)
        sistema.crear_reserva("Luis Pérez", "600333444", "luis@mail.com",
                               4, fecha_futura(72), 2)
        stats = sistema.calcular_estadisticas()
        assert "Ana García" in stats["cliente_frecuente"]


# ─────────────────────────────────────────
# GRUPO 7 — PERSISTENCIA
# ─────────────────────────────────────────

class TestPersistencia:

    def test_reservas_se_guardan_en_disco(self, sistema, tmp_path):
        """Crear una reserva debe generar el archivo JSON."""
        sistema.crear_reserva("Ana García", "600111222", "ana@mail.com",
                               2, fecha_futura(48), 3)
        assert os.path.exists(sistema._ruta)

    def test_reservas_se_cargan_al_reiniciar(self, tmp_path):
        """Las reservas guardadas deben cargarse al crear una nueva instancia."""
        ruta = str(tmp_path / "test_persistencia.json")

        # Primera instancia: crea una reserva
        sr1 = SistemaReservas(ruta=ruta)
        sr1.crear_reserva("Ana García", "600111222", "ana@mail.com",
                          2, fecha_futura(48), 3)

        # Segunda instancia: debe leer la reserva guardada
        sr2 = SistemaReservas(ruta=ruta)
        assert len(sr2.reservas) == 1
        assert sr2.reservas[0]["nombre"] == "Ana García"

    def test_archivo_corrupto_no_rompe_el_sistema(self, tmp_path):
        """Un archivo JSON corrupto no debe hacer crashear el sistema."""
        ruta = str(tmp_path / "corrupto.json")
        with open(ruta, "w") as f:
            f.write("esto no es json válido {{{")

        # No debe lanzar excepción
        sr = SistemaReservas(ruta=ruta)
        assert sr.reservas == []


# ─────────────────────────────────────────
# GRUPO 8 — MODIFICAR RESERVA  [añadido por el alumno]
# ─────────────────────────────────────────

class TestModificarReserva:

    def test_modificar_fecha_exitoso(self, sistema_con_reserva):
        """Cambiar a una fecha futura libre debe funcionar."""
        resultado = sistema_con_reserva.modificar_reserva(
            1, nueva_fecha=fecha_futura(96)
        )
        assert "ok" in resultado
        assert resultado["reserva"]["fecha_hora"] == fecha_futura(96)

    def test_modificar_fecha_pasada(self, sistema_con_reserva):
        """No se puede cambiar a una fecha pasada."""
        resultado = sistema_con_reserva.modificar_reserva(
            1, nueva_fecha="2020-01-01 21:00"
        )
        assert "error" in resultado

    def test_modificar_reserva_inexistente(self, sistema):
        """Modificar un ID inexistente debe devolver error."""
        resultado = sistema.modificar_reserva(999, nueva_fecha=fecha_futura(48))
        assert "error" in resultado

    def test_modificar_comensales_exitoso(self, sistema_con_reserva):
        """Reducir comensales dentro de la capacidad debe funcionar."""
        resultado = sistema_con_reserva.modificar_reserva(1, nuevos_comensales=2)
        assert "ok" in resultado
        assert resultado["reserva"]["comensales"] == 2

    def test_modificar_comensales_excede_capacidad(self, sistema_con_reserva):
        """Exceder la capacidad de la mesa debe devolver error."""
        resultado = sistema_con_reserva.modificar_reserva(
            1, nuevos_comensales=99
        )
        assert "error" in resultado