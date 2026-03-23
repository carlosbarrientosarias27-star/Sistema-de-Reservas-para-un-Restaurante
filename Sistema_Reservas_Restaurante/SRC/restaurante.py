from datetime import datetime
import uuid


class Mesa:
    def __init__(self, numero, capacidad, zona):
        self.numero = numero
        self.capacidad = capacidad
        self.zona = zona  # terraza / interior / privado

    def __repr__(self):
        return f"Mesa {self.numero} ({self.capacidad} personas, {self.zona})"


class Reserva:
    def __init__(self, nombre, telefono, email, mesa, fecha_hora, comensales):
        self.id = str(uuid.uuid4())[:8]
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.mesa = mesa
        self.fecha_hora = fecha_hora
        self.comensales = comensales

    def __repr__(self):
        return (f"[{self.id}] {self.nombre} - Mesa {self.mesa.numero} - "
                f"{self.fecha_hora} - {self.comensales} personas")


class SistemaReservas:
    def __init__(self):
        self.mesas = []
        self.reservas = {}

    # ---------------------------
    # Gestión de mesas
    # ---------------------------
    def agregar_mesa(self, numero, capacidad, zona):
        mesa = Mesa(numero, capacidad, zona)
        self.mesas.append(mesa)

    def obtener_mesa(self, numero):
        for mesa in self.mesas:
            if mesa.numero == numero:
                return mesa
        return None

    # ---------------------------
    # Disponibilidad
    # ---------------------------
    def mesa_disponible(self, numero_mesa, fecha_hora):
        for reserva in self.reservas.values():
            if (reserva.mesa.numero == numero_mesa and
                    reserva.fecha_hora == fecha_hora):
                return False
        return True

    # ---------------------------
    # Crear reserva
    # ---------------------------
    def crear_reserva(self, nombre, telefono, email, numero_mesa, fecha_hora_str, comensales):
        mesa = self.obtener_mesa(numero_mesa)

        if not mesa:
            return "❌ Error: Mesa no existe"

        if comensales > mesa.capacidad:
            return "❌ Error: Capacidad de mesa insuficiente"

        fecha_hora = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M")

        if not self.mesa_disponible(numero_mesa, fecha_hora):
            return "❌ Error: Mesa ya ocupada en esa fecha y hora"

        reserva = Reserva(nombre, telefono, email, mesa, fecha_hora, comensales)
        self.reservas[reserva.id] = reserva

        return f"✅ Reserva creada: {reserva}"

    # ---------------------------
    # Consultar reservas
    # ---------------------------
    def consultar_por_cliente(self, nombre):
        resultados = [r for r in self.reservas.values() if r.nombre.lower() == nombre.lower()]
        return resultados if resultados else "⚠️ No hay reservas para ese cliente"

    # ---------------------------
    # Modificar reserva
    # ---------------------------
    def modificar_reserva(self, reserva_id, **kwargs):
        reserva = self.reservas.get(reserva_id)

        if not reserva:
            return "❌ Error: Reserva no encontrada"

        nueva_fecha = kwargs.get("fecha_hora", reserva.fecha_hora)
        nueva_mesa_num = kwargs.get("numero_mesa", reserva.mesa.numero)

        if isinstance(nueva_fecha, str):
            nueva_fecha = datetime.strptime(nueva_fecha, "%Y-%m-%d %H:%M")

        if not self.mesa_disponible(nueva_mesa_num, nueva_fecha):
            return "❌ Error: Nueva mesa ocupada en esa fecha y hora"

        nueva_mesa = self.obtener_mesa(nueva_mesa_num)

        if not nueva_mesa:
            return "❌ Error: Nueva mesa no existe"

        # Aplicar cambios
        reserva.nombre = kwargs.get("nombre", reserva.nombre)
        reserva.telefono = kwargs.get("telefono", reserva.telefono)
        reserva.email = kwargs.get("email", reserva.email)
        reserva.mesa = nueva_mesa
        reserva.fecha_hora = nueva_fecha
        reserva.comensales = kwargs.get("comensales", reserva.comensales)

        return f"✅ Reserva modificada: {reserva}"

    # ---------------------------
    # Cancelar reserva
    # ---------------------------
    def cancelar_reserva(self, reserva_id):
        if reserva_id in self.reservas:
            del self.reservas[reserva_id]
            return "✅ Reserva cancelada"
        return "❌ Error: Reserva no encontrada"

    # ---------------------------
    # Estado del sistema
    # ---------------------------
    def estado_reservas(self):
        if not self.reservas:
            return "No hay reservas"
        return "\n".join(str(r) for r in self.reservas.values())


# ---------------------------
# Ejemplo de uso
# ---------------------------
if __name__ == "__main__":
    sistema = SistemaReservas()

    # Crear mesas
    sistema.agregar_mesa(1, 4, "interior")
    sistema.agregar_mesa(2, 2, "terraza")
    sistema.agregar_mesa(3, 6, "privado")

    # Crear reservas
    print(sistema.crear_reserva(
        "Juan Pérez", "123456789", "juan@email.com",
        1, "2026-03-25 14:00", 4
    ))

    # Intento de conflicto
    print(sistema.crear_reserva(
        "Ana López", "987654321", "ana@email.com",
        1, "2026-03-25 14:00", 2
    ))

    # Consultar
    print(sistema.consultar_por_cliente("Juan Pérez"))

    # Modificar
    reserva_id = list(sistema.reservas.keys())[0]
    print(sistema.modificar_reserva(reserva_id, numero_mesa=2))

    # Estado
    print("\n📋 Estado actual:")
    print(sistema.estado_reservas())

    # Cancelar
    print(sistema.cancelar_reserva(reserva_id))