import re
from datetime import datetime
from typing import List, Dict, Optional

class Mesa:
    """Representa una mesa física en el establecimiento."""
    def __init__(self, id_mesa: int, capacidad: int, zona: str):
        self.id_mesa = id_mesa
        self.capacidad = capacidad
        self.zona = zona

    def __repr__(self):
        return f"Mesa(ID={self.id_mesa}, Zona={self.zona})"

class Reserva:
    """Entidad que almacena los datos de una reserva confirmada."""
    def __init__(self, cliente: str, telefono: str, email: str,
                 ids_mesas: List[int], fecha_hora: datetime):
        self.cliente = cliente
        self.telefono = telefono
        self.email = email
        self.ids_mesas = ids_mesas
        self.fecha_hora = fecha_hora

    def __repr__(self):
        # Ofuscamos datos sensibles (PII) en representaciones de texto
        cliente_protegido = f"{self.cliente[:3]}***"
        return f"Reserva(Cliente={cliente_protegido}, Mesas={self.ids_mesas}, Fecha={self.fecha_hora})"

class GestionRestaurante:
    """Sistema central para la gestión de mesas y disponibilidad de reservas."""
    
    def __init__(self):
        self.catalogo_mesas: Dict[int, Mesa] = {}
        self.listado_reservas: List[Reserva] = []
        self.calendario_ocupacion: Dict[datetime, set] = {}

    def _validar_datos_contacto(self, nombre: str, telefono: str, email: str):
        """Verifica que el formato de los datos de contacto sea correcto."""
        if not (2 <= len(nombre) <= 50):
            raise ValueError("El nombre debe tener entre 2 y 50 caracteres.")
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("El formato del correo electrónico es inválido.")
            
        if not re.match(r"^\+?1?\d{9,15}$", telefono):
            raise ValueError("El formato del teléfono es inválido (9-15 dígitos).")

    def registrar_mesa(self, id_mesa: int, capacidad: int, zona: str):
        """Añade una nueva mesa al inventario del restaurante."""
        if not isinstance(id_mesa, int) or id_mesa <= 0:
            raise ValueError("El ID de la mesa debe ser un número entero positivo.")
            
        if id_mesa in self.catalogo_mesas:
            raise ValueError(f"La mesa con ID {id_mesa} ya está registrada.")
            
        self.catalogo_mesas[id_mesa] = Mesa(id_mesa, capacidad, zona)

    def realizar_reserva(self, cliente: str, telefono: str, email: str,
                         ids_mesas: List[int], fecha_hora: datetime) -> Reserva:
        """
        Procesa y valida una nueva reserva. 
        Asegura que las mesas existan y no estén ocupadas.
        """
        # 1. Validar integridad de la entrada
        self._validar_datos_contacto(cliente, telefono, email)
        
        if not ids_mesas:
            raise ValueError("Debe seleccionar al menos una mesa.")

        # 2. Verificar existencia y disponibilidad de mesas
        for id_m in ids_mesas:
            if id_m not in self.catalogo_mesas:
                raise ValueError(f"La mesa {id_m} no figura en nuestro inventario.")
        
        mesas_ocupadas = self.calendario_ocupacion.get(fecha_hora, set())
        if any(id_m in mesas_ocupadas for id_m in ids_mesas):
            raise ValueError("Conflicto de horario: Una o más mesas ya están reservadas.")

        # 3. Confirmar y persistir la reserva
        nueva_reserva = Reserva(cliente, telefono, email, ids_mesas, fecha_hora)
        self.listado_reservas.append(nueva_reserva)
        
        # Actualizar el mapa de ocupación
        self.calendario_ocupacion.setdefault(fecha_hora, set()).update(ids_mesas)
        
        return nueva_reserva

    def eliminar_reserva(self, reserva: Reserva):
        """Cancela una reserva y libera las mesas asociadas."""
        if reserva not in self.listado_reservas:
            raise ValueError("No se encontró la reserva especificada.")

        # Liberar las mesas del calendario de ocupación
        if reserva.fecha_hora in self.calendario_ocupacion:
            for id_m in reserva.ids_mesas:
                self.calendario_ocupacion[reserva.fecha_hora].discard(id_m)
        
        self.listado_reservas.remove(reserva)

    def editar_reserva(self, reserva_existente: Reserva, **nuevos_datos):
        """
        Modifica una reserva existente aplicando una limpieza temporal del estado
        para permitir validaciones sin conflictos con los datos antiguos.
        """
        if reserva_existente not in self.listado_reservas:
            raise ValueError("La reserva no existe en el sistema.")

        # Extraer valores nuevos o mantener los actuales si no se especifican
        datos_actualizados = {
            "cliente": nuevos_datos.get("cliente", reserva_existente.cliente),
            "telefono": nuevos_datos.get("telefono", reserva_existente.telefono),
            "email": nuevos_datos.get("email", reserva_existente.email),
            "ids_mesas": nuevos_datos.get("ids_mesas", reserva_existente.ids_mesas),
            "fecha_hora": nuevos_datos.get("fecha_hora", reserva_existente.fecha_hora)
        }

        # Backup de seguridad para posible rollback
        estado_anterior = {
            "fecha": reserva_existente.fecha_hora,
            "mesas": list(reserva_existente.ids_mesas)
        }

        # Eliminación temporal para re-validar disponibilidad limpiamente
        self.eliminar_reserva(reserva_existente)

        try:
            # Intentar crear la reserva con la nueva configuración
            self.realizar_reserva(
                datos_actualizados["cliente"],
                datos_actualizados["telefono"],
                datos_actualizados["email"],
                datos_actualizados["ids_mesas"],
                datos_actualizados["fecha_hora"]
            )
        except Exception as error:
            # ROLLBACK: Restaurar la reserva original en caso de fallo
            self.realizar_reserva(
                reserva_existente.cliente,
                reserva_existente.telefono,
                reserva_existente.email,
                estado_anterior["mesas"],
                estado_anterior["fecha"]
            )
            raise error

# --- Bloque de Prueba ---
if __name__ == "__main__":
    app = GestionRestaurante()
    app.registrar_mesa(id_mesa=1, capacidad=4, zona="Interior")
    app.registrar_mesa(id_mesa=2, capacidad=2, zona="Terraza")

    horario_cena = datetime(2026, 3, 20, 21, 0)

    try:
        reserva_carlos = app.realizar_reserva("Carlos", "600000000", "c@mail.com", [1], horario_cena)
        print(f"Éxito: {reserva_carlos}")

        # Prueba de validación de duplicados
        app.realizar_reserva("Marta", "611111111", "m@mail.com", [1], horario_cena)
    except ValueError as e:
        print(f"Validación detectada: {e}")