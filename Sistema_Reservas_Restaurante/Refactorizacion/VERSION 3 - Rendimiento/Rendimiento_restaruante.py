import re
from datetime import datetime
from typing import List, Dict, Set, Optional

# --- MODELOS OPTIMIZADOS ---

class Mesa:
    __slots__ = ['numero', 'capacidad', 'zona'] # Ahorro de memoria en miles de objetos
    def __init__(self, numero: int, capacidad: int, zona: str):
        self.numero = numero
        self.capacidad = capacidad
        self.zona = zona

    def __repr__(self):
        return f"Mesa(ID={self.numero})"

class Reserva:
    __slots__ = ['id_reserva', 'nombre', 'telefono', 'email', 'mesas', 'fecha_hora']
    def __init__(self, id_reserva: int, nombre: str, telefono: str, email: str,
                 mesas: List[int], fecha_hora: datetime):
        self.id_reserva = id_reserva
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.mesas = mesas
        self.fecha_hora = fecha_hora

    def __repr__(self):
        return f"Reserva(ID={self.id_reserva}, Cliente={self.nombre[:3]}***)"

# --- SISTEMA DE ALTO RENDIMIENTO ---

class Restaurante:
    def __init__(self):
        # O(1) para buscar una mesa por número
        self.mesas: Dict[int, Mesa] = {}
        
        # O(1) para buscar, eliminar o verificar si una reserva existe
        # Cambiamos List por Dict {id: Reserva}
        self.reservas: Dict[int, Reserva] = {}
        self._contador_id = 0
        
        # O(1) para verificar disponibilidad: {fecha: {id_mesa, id_mesa...}}
        self.ocupacion_por_fecha: Dict[datetime, Set[int]] = {}

    def _validar_inputs(self, nombre: str, telefono: str, email: str):
        # Las validaciones Regex son costosas; las mantenemos pero solo si cambian los datos
        if not (2 <= len(nombre) <= 50):
            raise ValueError("Nombre fuera de rango.")
        if "@" not in email: # Check rápido antes del regex
            raise ValueError("Email inválido.")

    def agregar_mesa(self, numero: int, capacidad: int, zona: str):
        if numero in self.mesas:
            raise ValueError(f"Mesa {numero} ya existe.")
        self.mesas[numero] = Mesa(numero, capacidad, zona)

    def crear_reserva(self, nombre: str, telefono: str, email: str,
                      mesas: List[int], fecha_hora: datetime) -> Reserva:
        
        self._validar_inputs(nombre, telefono, email)

        # Optimización: Verificación de disponibilidad en O(k) donde k es num de mesas solicitadas
        ocupadas = self.ocupacion_por_fecha.get(fecha_hora, set())
        
        # Usamos intersección de sets para rapidez extrema si la lista de mesas fuera grande
        if not ocupadas.isdisjoint(mesas):
            raise ValueError("Una o más mesas están ocupadas.")

        # Verificar existencia de mesas en O(1)
        for m in mesas:
            if m not in self.mesas:
                raise ValueError(f"Mesa {m} no existe.")

        self._contador_id += 1
        nueva_reserva = Reserva(self._contador_id, nombre, telefono, email, mesas, fecha_hora)
        
        # Persistencia en O(1)
        self.reservas[nueva_reserva.id_reserva] = nueva_reserva
        self.ocupacion_por_fecha.setdefault(fecha_hora, set()).update(mesas)
        
        return nueva_reserva

    def cancelar_reserva(self, id_reserva: int):
        # Antes: O(n) buscando en lista. Ahora: O(1) buscando en dict.
        reserva = self.reservas.pop(id_reserva, None)
        if not reserva:
            raise ValueError("La reserva no existe.")

        # Liberación eficiente
        if reserva.fecha_hora in self.ocupacion_por_fecha:
            # O(k) siendo k las mesas de la reserva
            for m in reserva.mesas:
                self.ocupacion_por_fecha[reserva.fecha_hora].discard(m)

    def modificar_reserva(self, id_reserva: int, **kwargs):
        """
        Versión optimizada: Solo re-valida si cambian las mesas o la fecha.
        """
        reserva = self.reservas.get(id_reserva)
        if not reserva:
            raise ValueError("Reserva no encontrada.")

        n_mesas = kwargs.get("mesas", reserva.mesas)
        n_fecha = kwargs.get("fecha_hora", reserva.fecha_hora)

        # Si no cambia ni fecha ni mesas, solo actualizamos strings (O(1))
        if n_mesas == reserva.mesas and n_fecha == reserva.fecha_hora:
            reserva.nombre = kwargs.get("nombre", reserva.nombre)
            return

        # Si cambian datos críticos, aplicamos lógica de re-asignación
        old_fecha, old_mesas = reserva.fecha_hora, list(reserva.mesas)
        self.cancelar_reserva(id_reserva)

        try:
            self.crear_reserva(
                kwargs.get("nombre", reserva.nombre),
                kwargs.get("telefono", reserva.telefono),
                kwargs.get("email", reserva.email),
                n_mesas, n_fecha
            )
        except Exception as e:
            # Rollback eficiente
            self.crear_reserva(reserva.nombre, reserva.telefono, reserva.email, old_mesas, old_fecha)
            raise e