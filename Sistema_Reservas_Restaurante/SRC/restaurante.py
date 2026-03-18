from datetime import datetime
from typing import List, Dict


class Mesa:
    def __init__(self, numero: int, capacidad: int, zona: str):
        self.numero = numero
        self.capacidad = capacidad
        self.zona = zona  # terraza / interior / privado

    def __repr__(self):
        return f"Mesa({self.numero}, cap={self.capacidad}, zona={self.zona})"


class Reserva:
    def __init__(self, nombre: str, telefono: str, email: str,
                 mesas: List[int], fecha_hora: datetime):
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.mesas = mesas
        self.fecha_hora = fecha_hora

    def __repr__(self):
        return (f"Reserva(cliente={self.nombre}, mesas={self.mesas}, "
                f"fecha={self.fecha_hora.strftime('%Y-%m-%d %H:%M')})")


class Restaurante:
    def __init__(self):
        self.mesas: Dict[int, Mesa] = {}
        self.reservas: List[Reserva] = []

    # ------------------------
    # Gestión de mesas
    # ------------------------
    def agregar_mesa(self, numero: int, capacidad: int, zona: str):
        if numero in self.mesas:
            raise ValueError(f"La mesa {numero} ya existe.")
        self.mesas[numero] = Mesa(numero, capacidad, zona)

    # ------------------------
    # Crear reserva
    # ------------------------
    def crear_reserva(self, nombre: str, telefono: str, email: str,
                      mesas: List[int], fecha_hora: datetime):

        # Validar que las mesas existan
        for m in mesas:
            if m not in self.mesas:
                raise ValueError(f"La mesa {m} no existe.")

        # Validar conflictos
        for reserva in self.reservas:
            if reserva.fecha_hora == fecha_hora:
                for m in mesas:
                    if m in reserva.mesas:
                        raise ValueError(
                            f"Error: La mesa {m} ya está ocupada "
                            f"en {fecha_hora.strftime('%Y-%m-%d %H:%M')}."
                        )

        nueva_reserva = Reserva(nombre, telefono, email, mesas, fecha_hora)
        self.reservas.append(nueva_reserva)
        return nueva_reserva

    # ------------------------
    # Consultar reservas
    # ------------------------
    def consultar_reservas(self, fecha: datetime = None):
        if fecha:
            return [r for r in self.reservas if r.fecha_hora.date() == fecha.date()]
        return self.reservas

    # ------------------------
    # Buscar reserva
    # ------------------------
    def buscar_reserva(self, nombre: str):
        return [r for r in self.reservas if r.nombre.lower() == nombre.lower()]

    # ------------------------
    # Modificar reserva
    # ------------------------
    def modificar_reserva(self, reserva: Reserva, **kwargs):
        # Eliminamos temporalmente para validar sin conflicto consigo misma
        self.reservas.remove(reserva)

        try:
            nombre = kwargs.get("nombre", reserva.nombre)
            telefono = kwargs.get("telefono", reserva.telefono)
            email = kwargs.get("email", reserva.email)
            mesas = kwargs.get("mesas", reserva.mesas)
            fecha_hora = kwargs.get("fecha_hora", reserva.fecha_hora)

            # Reutilizamos validación
            self.crear_reserva(nombre, telefono, email, mesas, fecha_hora)

            # Actualizamos objeto original
            reserva.nombre = nombre
            reserva.telefono = telefono
            reserva.email = email
            reserva.mesas = mesas
            reserva.fecha_hora = fecha_hora

        except Exception as e:
            # Revertimos si hay error
            self.reservas.append(reserva)
            raise e

    # ------------------------
    # Cancelar reserva
    # ------------------------
    def cancelar_reserva(self, reserva: Reserva):
        if reserva in self.reservas:
            self.reservas.remove(reserva)
        else:
            raise ValueError("La reserva no existe.")


# ------------------------
# Ejemplo de uso
# ------------------------
if __name__ == "__main__":
    restaurante = Restaurante()

    # Crear mesas
    restaurante.agregar_mesa(1, 4, "interior")
    restaurante.agregar_mesa(2, 2, "terraza")
    restaurante.agregar_mesa(3, 6, "privado")

    fecha = datetime(2026, 3, 20, 14, 0)

    # Crear reserva
    r1 = restaurante.crear_reserva(
        "Juan Pérez", "123456789", "juan@email.com",
        [1, 2], fecha
    )

    print("Reserva creada:", r1)

    # Intento de conflicto
    try:
        restaurante.crear_reserva(
            "Ana López", "987654321", "ana@email.com",
            [2], fecha
        )
    except ValueError as e:
        print(e)

    # Consultar reservas
    print("Reservas:", restaurante.consultar_reservas())

    # Modificar reserva
    nueva_fecha = datetime(2026, 3, 20, 15, 0)
    restaurante.modificar_reserva(r1, fecha_hora=nueva_fecha)
    print("Reserva modificada:", r1)

    # Cancelar reserva
    restaurante.cancelar_reserva(r1)
    print("Reservas tras cancelación:", restaurante.consultar_reservas())