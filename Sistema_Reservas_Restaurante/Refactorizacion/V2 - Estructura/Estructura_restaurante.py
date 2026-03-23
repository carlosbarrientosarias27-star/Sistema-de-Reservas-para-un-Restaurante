import re
from datetime import datetime
from typing import List, Dict, Set

# --- 1. MODELOS DE DATOS (Entidades puras) ---

class Mesa:
    def __init__(self, numero: int, capacidad: int, zona: str):
        self.numero = numero
        self.capacidad = capacidad
        self.zona = zona

    def __repr__(self):
        return f"Mesa(ID={self.numero}, Zona={self.zona})"

class Reserva:
    def __init__(self, cliente: str, telefono: str, email: str,
                 ids_mesas: List[int], fecha_hora: datetime):
        self.cliente = cliente
        self.telefono = telefono
        self.email = email
        self.ids_mesas = ids_mesas
        self.fecha_hora = fecha_hora

    def __repr__(self):
        return f"Reserva(Cliente={self.cliente[:3]}***, Mesas={self.ids_mesas}, Fecha={self.fecha_hora})"


# --- 2. SERVICIOS ESPECIALIZADOS (SRP) ---

class ValidadorContacto:
    """Única responsabilidad: Validar formatos de datos de clientes."""
    @staticmethod
    def validar(nombre: str, telefono: str, email: str):
        if not (2 <= len(nombre) <= 50):
            raise ValueError("Nombre inválido (2-50 caracteres).")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Formato de email inválido.")
        if not re.match(r"^\+?1?\d{9,15}$", telefono):
            raise ValueError("Formato de teléfono inválido.")

class InventarioMesas:
    """Única responsabilidad: Gestionar el catálogo físico de mesas."""
    def __init__(self):
        self._mesas: Dict[int, Mesa] = {}

    def agregar_mesa(self, mesa: Mesa):
        if mesa.numero in self._mesas:
            raise ValueError(f"La mesa {mesa.numero} ya existe.")
        self._mesas[mesa.numero] = mesa

    def existe_mesa(self, numero: int) -> bool:
        return numero in self._mesas

    def obtener_mesa(self, numero: int) -> Mesa:
        return self._mesas.get(numero)

class GestorDisponibilidad:
    """Única responsabilidad: Controlar qué mesas están libres u ocupadas."""
    def __init__(self):
        self._ocupacion: Dict[datetime, Set[int]] = {}

    def estan_disponibles(self, ids_mesas: List[int], fecha_hora: datetime) -> bool:
        ocupadas = self._ocupacion.get(fecha_hora, set())
        return not any(m_id in ocupadas for m_id in ids_mesas)

    def ocupar_mesas(self, ids_mesas: List[int], fecha_hora: datetime):
        self._ocupacion.setdefault(fecha_hora, set()).update(ids_mesas)

    def liberar_mesas(self, ids_mesas: List[int], fecha_hora: datetime):
        if fecha_hora in self._ocupacion:
            for m_id in ids_mesas:
                self._ocupacion[fecha_hora].discard(m_id)


# --- 3. ORQUESTADOR (Fachada o Sistema Central) ---

class SistemaReservas:
    """Orquesta la interacción entre los servicios sin conocer los detalles de validación o storage."""
    def __init__(self, inventario: InventarioMesas, validador: ValidadorContacto):
        self.inventario = inventario
        self.validador = validador
        self.disponibilidad = GestorDisponibilidad()
        self.reservas_activas: List[Reserva] = []

    def crear_reserva(self, cliente: str, telefono: str, email: str,
                      ids_mesas: List[int], fecha_hora: datetime) -> Reserva:
        
        # Delegación de responsabilidades
        self.validador.validar(cliente, telefono, email)
        
        for m_id in ids_mesas:
            if not self.inventario.existe_mesa(m_id):
                raise ValueError(f"La mesa {m_id} no existe en el inventario.")

        if not self.disponibilidad.estan_disponibles(ids_mesas, fecha_hora):
            raise ValueError("Conflicto: Mesas ocupadas en este horario.")

        # Ejecución
        nueva_reserva = Reserva(cliente, telefono, email, ids_mesas, fecha_hora)
        self.disponibilidad.ocupar_mesas(ids_mesas, fecha_hora)
        self.reservas_activas.append(nueva_reserva)
        
        return nueva_reserva

    def cancelar_reserva(self, reserva: Reserva):
        if reserva not in self.reservas_activas:
            raise ValueError("Reserva no encontrada.")
            
        self.disponibilidad.liberar_mesas(reserva.ids_mesas, reserva.fecha_hora)
        self.reservas_activas.remove(reserva)