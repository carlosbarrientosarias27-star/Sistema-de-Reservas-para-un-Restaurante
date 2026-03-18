import re
from datetime import datetime
from typing import List, Dict, Optional

class Mesa:
    def __init__(self, numero: int, capacidad: int, zona: str):
        self.numero = numero
        self.capacidad = capacidad
        self.zona = zona

    def __repr__(self):
        return f"Mesa(ID={self.numero})"

class Reserva:
    def __init__(self, nombre: str, telefono: str, email: str,
                 mesas: List[int], fecha_hora: datetime):
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.mesas = mesas
        self.fecha_hora = fecha_hora

    def __repr__(self):
        # No incluimos PII (email/teléfono) en el repr para evitar fugas en logs
        return f"Reserva(Cliente={self.nombre[:3]}***, Mesas={self.mesas}, Fecha={self.fecha_hora})"

class Restaurante:
    def __init__(self):
        self.mesas: Dict[int, Mesa] = {}
        self.reservas: List[Reserva] = []
        self.ocupacion_por_fecha: Dict[datetime, set] = {}

    def _validar_inputs(self, nombre: str, telefono: str, email: str):
        """Validador centralizado de datos de usuario."""
        if len(nombre) < 2 or len(nombre) > 50:
            raise ValueError("Nombre inválido (2-50 caracteres).")
        
        # Regex simple para email y teléfono (evita inyecciones básicas)
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Formato de email inválido.")
            
        if not re.match(r"^\+?1?\d{9,15}$", telefono):
            raise ValueError("Formato de teléfono inválido.")

    def agregar_mesa(self, numero: int, capacidad: int, zona: str):
        if not isinstance(numero, int) or numero <= 0:
            raise ValueError("El número de mesa debe ser un entero positivo.")
        if numero in self.mesas:
            raise ValueError(f"La mesa {numero} ya existe.")
        self.mesas[numero] = Mesa(numero, capacidad, zona)

    def crear_reserva(self, nombre: str, telefono: str, email: str,
                      mesas: List[int], fecha_hora: datetime) -> Reserva:
        
        # 1. Validaciones de Seguridad
        self._validar_inputs(nombre, telefono, email)
        if not isinstance(mesas, list) or not mesas:
            raise ValueError("Debe proporcionar una lista de mesas válida.")

        # 2. Validar integridad de mesas y disponibilidad
        for m in mesas:
            if m not in self.mesas:
                raise ValueError(f"Mesa {m} no existe.")
        
        ocupadas = self.ocupacion_por_fecha.get(fecha_hora, set())
        if any(m in ocupadas for m in mesas):
            raise ValueError("Una o más mesas están ocupadas en este horario.")

        # 3. Persistencia atómica
        nueva_reserva = Reserva(nombre, telefono, email, mesas, fecha_hora)
        self.reservas.append(nueva_reserva)
        
        self.ocupacion_por_fecha.setdefault(fecha_hora, set()).update(mesas)
        return nueva_reserva

    def cancelar_reserva(self, reserva: Reserva):
        if reserva in self.reservas:
            # LIMPIEZA CRÍTICA: Liberar las mesas en el mapa de ocupación
            if reserva.fecha_hora in self.ocupacion_por_fecha:
                for m in reserva.mesas:
                    self.ocupacion_por_fecha[reserva.fecha_hora].discard(m)
            self.reservas.remove(reserva)
        else:
            raise ValueError("La reserva no existe.")

    def modificar_reserva(self, reserva: Reserva, **kwargs):
        """Modificación segura con limpieza de estado previa."""
        if reserva not in self.reservas:
            raise ValueError("Reserva no encontrada.")

        # 1. Extraer datos (nuevos o actuales)
        n_nombre = kwargs.get("nombre", reserva.nombre)
        n_tel = kwargs.get("telefono", reserva.telefono)
        n_email = kwargs.get("email", reserva.email)
        n_mesas = kwargs.get("mesas", reserva.mesas)
        n_fecha = kwargs.get("fecha_hora", reserva.fecha_hora)

        # 2. Backup y limpieza temporal del estado global
        # Esto es vital para que la validación no choque con la propia reserva
        old_fecha = reserva.fecha_hora
        old_mesas = list(reserva.mesas)
        self.cancelar_reserva(reserva)

        try:
            # 3. Intentar crear la nueva versión (valida todo de nuevo)
            nueva = self.crear_reserva(n_nombre, n_tel, n_email, n_mesas, n_fecha)
            # Reemplazar la referencia original si es necesario
            reserva.nombre, reserva.telefono, reserva.email = n_nombre, n_tel, n_email
            reserva.mesas, reserva.fecha_hora = n_mesas, n_fecha
        except Exception as e:
            # 4. Rollback: Si falla, restauramos la reserva original
            self.crear_reserva(reserva.nombre, reserva.telefono, reserva.email, old_mesas, old_fecha)
            raise e

# --- NUEVAS FUNCIONES AQUÍ ---

    def buscar_disponibilidad(self, fecha_hora: datetime, capacidad_minima: int) -> List[int]:
        """Devuelve una lista de IDs de mesas disponibles con capacidad suficiente."""
        ocupadas = self.ocupacion_por_fecha.get(fecha_hora, set())
        disponibles = [
            m.numero for m in self.mesas.values() 
            if m.numero not in ocupadas and m.capacidad >= capacidad_minima
        ]
        return disponibles

    def calcular_estadisticas(self) -> Dict[str, any]:
        """Calcula estadísticas básicas del sistema."""
        total_reservas = len(self.reservas)
        if total_reservas == 0:
            return {"total": 0, "promedio_mesas": 0}
        
        total_mesas_reservadas = sum(len(r.mesas) for r in self.reservas)
        return {
            "total": total_reservas,
            "promedio_mesas": total_mesas_reservadas / total_reservas
        }

# --- Ejemplo de ejecución (si lo mantienes) ---
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