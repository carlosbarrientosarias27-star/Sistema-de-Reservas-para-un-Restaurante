"""
ALTERNATIVA 1 — Programación Orientada a Objetos (OOP)
Cada concepto del dominio es una clase con sus propios métodos.
"""

class Mesa:
    def __init__(self, numero, capacidad, zona):
        self.numero = numero
        self.capacidad = capacidad
        self.zona = zona

    def __repr__(self):
        return f"Mesa({self.numero}, {self.capacidad} personas, {self.zona})"


class Reserva:
    def __init__(self, id, cliente, mesa, fecha_hora, comensales):
        self.id = id
        self.cliente = cliente      # dict con nombre, telefono, email
        self.mesa = mesa            # objeto Mesa
        self.fecha_hora = fecha_hora
        self.comensales = comensales
        self.estado = "activa"

    def cancelar(self):
        self.estado = "cancelada"

    def __repr__(self):
        return (f"Reserva #{self.id} | {self.cliente['nombre']} | "
                f"{self.mesa} | {self.fecha_hora} | {self.estado}")


class SistemaReservas:
    def __init__(self):
        self.mesas = [
            Mesa(1, 2, "interior"),
            Mesa(2, 4, "interior"),
            Mesa(3, 4, "terraza"),
            Mesa(4, 6, "terraza"),
            Mesa(5, 8, "privado"),
        ]
        self.reservas = []
        self._id_contador = 1

    # ── Búsquedas ──────────────────────────────────────────
    def _buscar_mesa(self, numero):
        return next((m for m in self.mesas if m.numero == numero), None)

    def _buscar_reserva(self, id_reserva):
        return next((r for r in self.reservas if r.id == id_reserva), None)

    # ── Disponibilidad ─────────────────────────────────────
    def esta_disponible(self, numero_mesa, fecha_hora):
        mesa = self._buscar_mesa(numero_mesa)
        if mesa is None:
            return False
        return not any(
            r.mesa.numero == numero_mesa
            and r.fecha_hora == fecha_hora
            and r.estado == "activa"
            for r in self.reservas
        )

    # ── Crear ──────────────────────────────────────────────
    def crear_reserva(self, nombre, telefono, email,
                      numero_mesa, fecha_hora, comensales):
        mesa = self._buscar_mesa(numero_mesa)
        if mesa is None:
            return {"error": f"Mesa {numero_mesa} no existe."}
        if comensales > mesa.capacidad:
            return {"error": f"Capacidad máxima: {mesa.capacidad} personas."}
        if not self.esta_disponible(numero_mesa, fecha_hora):
            return {"error": f"Mesa {numero_mesa} ocupada el {fecha_hora}."}

        cliente = {"nombre": nombre, "telefono": telefono, "email": email}
        reserva = Reserva(self._id_contador, cliente, mesa, fecha_hora, comensales)
        self.reservas.append(reserva)
        self._id_contador += 1
        return {"ok": True, "reserva": reserva}

    # ── Cancelar ───────────────────────────────────────────
    def cancelar_reserva(self, id_reserva):
        reserva = self._buscar_reserva(id_reserva)
        if reserva is None:
            return {"error": f"Reserva {id_reserva} no encontrada."}
        if reserva.estado == "cancelada":
            return {"error": "Ya estaba cancelada."}
        reserva.cancelar()
        return {"ok": True, "mensaje": f"Reserva {id_reserva} cancelada."}

    # ── Consultar ──────────────────────────────────────────
    def consultar_cliente(self, nombre):
        return [r for r in self.reservas
                if r.cliente["nombre"].lower() == nombre.lower()
                and r.estado == "activa"]


# ── Demo rápida ────────────────────────────────────────────
if __name__ == "__main__":
    sr = SistemaReservas()

    r1 = sr.crear_reserva("Ana García", "600111222", "ana@mail.com", 2, "2025-08-10 21:00", 3)
    print(r1["reserva"])

    r2 = sr.crear_reserva("Luis Pérez", "600333444", "luis@mail.com", 2, "2025-08-10 21:00", 2)
    print(r2)  # Error: mesa ocupada

    print(sr.cancelar_reserva(1))
    print(sr.consultar_cliente("Ana García"))