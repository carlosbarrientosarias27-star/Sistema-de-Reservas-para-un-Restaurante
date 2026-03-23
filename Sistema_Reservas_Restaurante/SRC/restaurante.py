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
        self.ocupacion = set()

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
    # Disponibilidad (Optimizado O(1))
    # ---------------------------
    def mesa_disponible(self, numero_mesa, fecha_hora):
        return (numero_mesa, fecha_hora) not in self.ocupacion

    # ---------------------------
    # Crear reserva (Corregido y Limpio)
    # ---------------------------
    def crear_reserva(self, nombre, telefono, email, numero_mesa, fecha_hora_str, comensales):
        # 1. Buscar la mesa
        mesa = self.obtener_mesa(numero_mesa)
        if not mesa:
            return "❌ Error: La mesa no existe"

        # 2. Convertir texto a objeto datetime
        try:
            fecha_hora = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M")
        except ValueError:
            return "❌ Error: Formato de fecha incorrecto. Use 'AAAA-MM-DD HH:MM'"

        # 3. Comprobar disponibilidad
        if not self.mesa_disponible(numero_mesa, fecha_hora):
            return "❌ Error: Mesa ya ocupada en ese horario"

        # 4. Crear el objeto reserva y guardarlo
        reserva = Reserva(nombre, telefono, email, mesa, fecha_hora, comensales)
        self.reservas[reserva.id] = reserva
        
        # 5. Registrar ocupación
        self.ocupacion.add((numero_mesa, fecha_hora)) 

        return f"✅ Reserva creada: {reserva}"

    # ---------------------------
    # Consultar reservas
    # ---------------------------
    def consultar_por_cliente(self, nombre):
        resultados = [r for r in self.reservas.values() if r.nombre.lower() == nombre.lower()]
        return resultados if resultados else "⚠️ No hay reservas para ese cliente"

    # ---------------------------
    # Modificar reserva (Optimizado O(1))
    # ---------------------------
    def modificar_reserva(self, reserva_id, **kwargs):
        reserva = self.reservas.get(reserva_id)
        if not reserva:
            return "❌ Error: Reserva no encontrada"

        nueva_fecha = kwargs.get("fecha_hora", reserva.fecha_hora)
        nueva_mesa_num = kwargs.get("numero_mesa", reserva.mesa.numero)

        if isinstance(nueva_fecha, str):
            nueva_fecha = datetime.strptime(nueva_fecha, "%Y-%m-%d %H:%M")

        cambia_logistica = (nueva_mesa_num != reserva.mesa.numero or 
                           nueva_fecha != reserva.fecha_hora)
        
        if cambia_logistica:
            if not self.mesa_disponible(nueva_mesa_num, nueva_fecha):
                return "❌ Error: Nueva mesa/horario ya ocupados"

        # Actualizar índice de ocupación
        self.ocupacion.discard((reserva.mesa.numero, reserva.fecha_hora))
        
        nueva_mesa = self.obtener_mesa(nueva_mesa_num)
        if not nueva_mesa:
            self.ocupacion.add((reserva.mesa.numero, reserva.fecha_hora))
            return "❌ Error: La nueva mesa no existe"

        # Actualizar campos
        reserva.nombre = kwargs.get("nombre", reserva.nombre)
        reserva.telefono = kwargs.get("telefono", reserva.telefono)
        reserva.email = kwargs.get("email", reserva.email)
        reserva.mesa = nueva_mesa
        reserva.fecha_hora = nueva_fecha
        reserva.comensales = kwargs.get("comensales", reserva.comensales)

        self.ocupacion.add((reserva.mesa.numero, reserva.fecha_hora))
        return f"✅ Reserva modificada: {reserva}"

    # ---------------------------
    # Cancelar reserva
    # ---------------------------
    def cancelar_reserva(self, reserva_id):
        if reserva_id in self.reservas:
            reserva = self.reservas[reserva_id]
            self.ocupacion.discard((reserva.mesa.numero, reserva.fecha_hora))
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