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

    # 1. Gestión de mesas (Evita duplicados)
    def agregar_mesa(self, numero: int, capacidad: int, zona: str):
        if numero in self.mesas:
            raise ValueError(f"Error: La mesa {numero} ya existe.")
        self.mesas[numero] = Mesa(numero, capacidad, zona)

    # 2. Crear reserva (Valida existencia de mesas y conflictos de horario)
    def crear_reserva(self, nombre: str, telefono: str, email: str,
                      mesas: List[int], fecha_hora: datetime):

        # Validar que las mesas existan en el restaurante
        for m in mesas:
            if m not in self.mesas:
                raise ValueError(f"Error: La mesa {m} no existe.")

        # Validar conflictos: que las mesas no estén ocupadas a esa misma hora
        for reserva in self.reservas:
            if reserva.fecha_hora == fecha_hora:
                for m in mesas:
                    if m in reserva.mesas:
                        raise ValueError(
                            f"Error: La mesa {m} ya está ocupada "
                            f"el {fecha_hora.strftime('%Y-%m-%d %H:%M')}."
                        )

        nueva_reserva = Reserva(nombre, telefono, email, mesas, fecha_hora)
        self.reservas.append(nueva_reserva)
        return nueva_reserva

    def consultar_reservas(self, fecha: datetime = None):
        if fecha:
            return [r for r in self.reservas if r.fecha_hora.date() == fecha.date()]
        return self.reservas

    def buscar_reserva(self, nombre: str):
        return [r for r in self.reservas if r.nombre.lower() == nombre.lower()]

    # 3. Modificar reserva (Usa el truco de quitar/poner para validar)
    def modificar_reserva(self, reserva: Reserva, **kwargs):
        if reserva not in self.reservas:
            raise ValueError("Error: La reserva original no existe.")

        # Guardamos una copia del estado original por si falla la validación
        estado_anterior = {
            "nombre": reserva.nombre,
            "telefono": reserva.telefono,
            "email": reserva.email,
            "mesas": reserva.mesas,
            "fecha_hora": reserva.fecha_hora
        }

        # Quitamos temporalmente para que no choque consigo misma al validar
        self.reservas.remove(reserva)

        try:
            # Obtenemos nuevos valores o mantenemos los actuales
            nombre = kwargs.get("nombre", reserva.nombre)
            telefono = kwargs.get("telefono", reserva.telefono)
            email = kwargs.get("email", reserva.email)
            mesas = kwargs.get("mesas", reserva.mesas)
            fecha_hora = kwargs.get("fecha_hora", reserva.fecha_hora)

            # Validar disponibilidad intentando crear una reserva "fantasma"
            # Si esto falla, saltará al 'except'
            self.crear_reserva(nombre, telefono, email, mesas, fecha_hora)
            
            # Si tuvo éxito, la validación pasó, pero 'crear_reserva' añadió una extra.
            # La quitamos y actualizamos el objeto original.
            self.reservas.pop() 

            reserva.nombre, reserva.telefono = nombre, telefono
            reserva.email, reserva.mesas = email, mesas
            reserva.fecha_hora = fecha_hora
            
            # Re-insertamos el objeto original actualizado
            self.reservas.append(reserva)

        except Exception as e:
            # Si algo falla, restauramos la reserva original a la lista
            self.reservas.append(reserva)
            raise e

    # 4. Cancelar reserva (Control de existencia)
    def cancelar_reserva(self, reserva: Reserva):
        if reserva in self.reservas:
            self.reservas.remove(reserva)
        else:
            raise ValueError("Error: No se pudo cancelar. La reserva no existe en el sistema.")

# --- Ejemplo de ejecución ---
if __name__ == "__main__":
    restaurante = Restaurante()
    restaurante.agregar_mesa(1, 4, "interior")
    restaurante.agregar_mesa(2, 2, "terraza")

    fecha_cita = datetime(2026, 3, 20, 21, 0)

    # Creamos una reserva exitosa
    r1 = restaurante.crear_reserva("Carlos", "600000000", "c@mail.com", [1], fecha_cita)
    print(f"Reserva 1 creada: {r1}")

    # Intentamos crear otra en la misma mesa y hora (Lanzará error)
    try:
        restaurante.crear_reserva("Marta", "611111111", "m@mail.com", [1], fecha_cita)
    except ValueError as e:
        print(f"Validación funcionando: {e}")