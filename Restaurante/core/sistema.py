from utils.validators import validar_email, validar_telefono, validar_fecha
from utils.security import sanitizar_texto
from data.persistence import cargar_datos, guardar_datos
from config import MAX_RESERVAS_POR_CLIENTE, FORMATO_FECHA 

class SistemaReservas:
    """
    [3] El estado (reservas, id_contador) vive dentro de la clase,
    no en variables globales. Esto evita colisiones en entornos
    con múltiples instancias o hilos.
    """

    MESAS = [
        {"numero": 1, "capacidad": 2, "zona": "interior"},
        {"numero": 2, "capacidad": 4, "zona": "interior"},
        {"numero": 3, "capacidad": 4, "zona": "terraza"},
        {"numero": 4, "capacidad": 6, "zona": "terraza"},
        {"numero": 5, "capacidad": 8, "zona": "privado"},
    ]

    def __init__(self):
        self.reservas, self._id_contador = cargar_datos()

    # ── Búsquedas internas ─────────────────────────────────
    def _buscar_mesa(self, numero: int) -> dict | None:
        return next((m for m in self.MESAS if m["numero"] == numero), None)

    def _reservas_activas_cliente(self, nombre: str) -> list:
        nombre_lower = nombre.lower()
        return [r for r in self.reservas
                if r["nombre"].lower() == nombre_lower
                and r["estado"] == "activa"]

    # ── Disponibilidad ─────────────────────────────────────
    def esta_disponible(self, numero_mesa: int, fecha_str: str) -> bool:
        return not any(
            r["mesa"] == numero_mesa
            and r["fecha_hora"] == fecha_str
            and r["estado"] == "activa"
            for r in self.reservas
        )

    # ── Crear reserva ──────────────────────────────────────
    def crear_reserva(self, nombre: str, telefono: str, email: str,
                      numero_mesa: int, fecha_str: str, comensales: int) -> dict:

        # [2] Sanitizar entradas de texto
        nombre   = sanitizar_texto(nombre, max_len=80)
        telefono = sanitizar_texto(telefono, max_len=20)
        email    = sanitizar_texto(email, max_len=100)

        # [1] Validar formato de email y teléfono
        if not nombre:
            return {"error": "El nombre no puede estar vacío."}
        if not validar_email(email):
            return {"error": f"Email inválido: '{email}'."}
        if not validar_telefono(telefono):
            return {"error": f"Teléfono inválido: '{telefono}'."}

        # [4] Validar que la fecha es futura y tiene formato correcto
        fecha_obj = validar_fecha(fecha_str)
        if fecha_obj is None:
            return {"error": f"Fecha inválida o en el pasado. Usa el formato: {FORMATO_FECHA}"}

        # Validar mesa
        mesa = self._buscar_mesa(numero_mesa)
        if mesa is None:
            return {"error": f"La mesa {numero_mesa} no existe."}
        if not isinstance(comensales, int) or comensales < 1:
            return {"error": "El número de comensales debe ser un entero positivo."}
        if comensales > mesa["capacidad"]:
            return {"error": f"Mesa {numero_mesa}: capacidad máxima {mesa['capacidad']} personas."}

        # [5] Límite de reservas activas por cliente
        activas = self._reservas_activas_cliente(nombre)
        if len(activas) >= MAX_RESERVAS_POR_CLIENTE:
            return {"error": f"'{nombre}' ya tiene {MAX_RESERVAS_POR_CLIENTE} reservas activas (límite máximo)."}

        # Comprobar disponibilidad
        if not self.esta_disponible(numero_mesa, fecha_str):
            return {"error": f"Mesa {numero_mesa} ocupada el {fecha_str}."}

        # Crear reserva
        nueva = {
            "id":         self._id_contador,
            "nombre":     nombre,
            "telefono":   telefono,
            "email":      email,
            "mesa":       numero_mesa,
            "zona":       mesa["zona"],
            "fecha_hora": fecha_str,
            "comensales": comensales,
            "estado":     "activa",
        }
        self.reservas.append(nueva)
        self._id_contador += 1
        guardar_datos(self.reservas, self._id_contador)  # [6] Persistir
        return {"ok": True, "reserva": nueva}

    # ── Cancelar ───────────────────────────────────────────
    def cancelar_reserva(self, id_reserva: int) -> dict:
        for r in self.reservas:
            if r["id"] == id_reserva:
                if r["estado"] == "cancelada":
                    return {"error": "La reserva ya estaba cancelada."}
                r["estado"] = "cancelada"
                guardar_datos(self.reservas, self._id_contador)  # [6]
                return {"ok": True, "mensaje": f"Reserva {id_reserva} cancelada."}
        return {"error": f"No existe la reserva con ID {id_reserva}."}

    # ── Consultar cliente ──────────────────────────────────
    def consultar_cliente(self, nombre: str) -> list:
        nombre = sanitizar_texto(nombre)  # [2] Sanitizar también la búsqueda
        return self._reservas_activas_cliente(nombre)

    # ── Modificar ──────────────────────────────────────────
    def modificar_reserva(self, id_reserva: int,
                          nueva_fecha: str | None = None,
                          nuevos_comensales: int | None = None) -> dict:
        for r in self.reservas:
            if r["id"] == id_reserva and r["estado"] == "activa":
                if nueva_fecha:
                    fecha_obj = validar_fecha(nueva_fecha)  # [4]
                    if fecha_obj is None:
                        return {"error": "Fecha inválida o en el pasado."}
                    if not self.esta_disponible(r["mesa"], nueva_fecha):
                        return {"error": f"Mesa {r['mesa']} ocupada el {nueva_fecha}."}
                    r["fecha_hora"] = nueva_fecha
                if nuevos_comensales:
                    mesa = self._buscar_mesa(r["mesa"])
                    if nuevos_comensales > mesa["capacidad"]:
                        return {"error": f"Capacidad máxima: {mesa['capacidad']}."}
                    r["comensales"] = nuevos_comensales
                guardar_datos(self.reservas, self._id_contador)  # [6]
                return {"ok": True, "reserva": r}
        return {"error": f"No se encontró la reserva activa {id_reserva}."}