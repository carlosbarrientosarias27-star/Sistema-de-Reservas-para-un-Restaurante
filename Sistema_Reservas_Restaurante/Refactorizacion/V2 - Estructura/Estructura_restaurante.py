import re
import json
import os
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Tuple

# ──────────────────────────────────────────────────────────────────────────────
# 1. ABSTRACCIONES (DIP - Inversión de Dependencias)
# ──────────────────────────────────────────────────────────────────────────────

class GestorPersistencia(ABC):
    """Abstracción para el almacenamiento de datos."""
    @abstractmethod
    def cargar(self) -> Tuple[List[Dict], int]: pass
    
    @abstractmethod
    def guardar(self, datos: List[Dict], contador: int) -> None: pass

# ──────────────────────────────────────────────────────────────────────────────
# 2. VALIDACIÓN (SRP - Responsabilidad Única)
# ──────────────────────────────────────────────────────────────────────────────

class ValidadorReserva:
    """Se encarga exclusivamente de las reglas de formato y seguridad de datos."""
    
    FORMATO_FECHA = "%Y-%m-%d %H:%M"

    @staticmethod
    def es_email_valido(email: str) -> bool:
        patron = r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(patron, email.strip()))

    @staticmethod
    def es_telefono_valido(telefono: str) -> bool:
        patron = r"^\+?[\d\s\-]{9,15}$"
        return bool(re.match(patron, telefono.strip()))

    @staticmethod
    def sanitizar(texto: str, max_len: int) -> str:
        limpio = re.sub(r"[<>\"'%;()&+\\\x00-\x1f]", "", texto)
        return limpio.strip()[:max_len]

    @classmethod
    def validar_fecha_futura(cls, fecha_str: str) -> Optional[datetime]:
        try:
            fecha = datetime.strptime(fecha_str.strip(), cls.FORMATO_FECHA)
            return fecha if fecha > datetime.now() else None
        except ValueError:
            return None

# ──────────────────────────────────────────────────────────────────────────────
# 3. PERSISTENCIA (SRP - Implementación Concreta)
# ──────────────────────────────────────────────────────────────────────────────

class PersistenciaJSON(GestorPersistencia):
    """Implementación específica de guardado en archivos locales JSON."""
    
    def __init__(self, nombre_archivo: str = "reservas.json"):
        self.archivo = nombre_archivo

    def cargar(self) -> Tuple[List[Dict], int]:
        if not os.path.exists(self.archivo):
            return [], 1
        try:
            with open(self.archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)
            return datos.get("reservas", []), datos.get("id_contador", 1)
        except (json.JSONDecodeError, KeyError):
            return [], 1

    def guardar(self, datos: List[Dict], contador: int) -> None:
        with open(self.archivo, "w", encoding="utf-8") as f:
            json.dump({"reservas": datos, "id_contador": contador}, 
                      f, ensure_ascii=False, indent=2)

# ──────────────────────────────────────────────────────────────────────────────
# 4. LÓGICA DE NEGOCIO (SRP / DIP)
# ──────────────────────────────────────────────────────────────────────────────

class SistemaReservas:
    """
    Coordina la lógica de negocio. No sabe CÓMO se guardan los datos (DIP),
    solo que el objeto inyectado cumple la interfaz GestorPersistencia.
    """

    MAX_RESERVAS = 5
    MESAS = [
        {"numero": 1, "capacidad": 2, "zona": "interior"},
        {"numero": 2, "capacidad": 4, "zona": "interior"},
        {"numero": 3, "capacidad": 4, "zona": "terraza"},
        {"numero": 4, "capacidad": 6, "zona": "terraza"},
        {"numero": 5, "capacidad": 8, "zona": "privado"},
    ]

    def __init__(self, persistencia: GestorPersistencia):
        self._persistencia = persistencia
        self.reservas, self._id_contador = self._persistencia.cargar()

    def _buscar_mesa(self, numero: int) -> Optional[Dict]:
        return next((m for m in self.MESAS if m["numero"] == numero), None)

    def esta_disponible(self, mesa: int, fecha: str) -> bool:
        return not any(r["mesa"] == mesa and r["fecha_hora"] == fecha 
                       and r["estado"] == "activa" for r in self.reservas)

    def crear_reserva(self, nombre: str, telefono: str, email: str, 
                      mesa_id: int, fecha: str, pax: int) -> Dict:
        
        # Saneamiento y validación vía clase especializada
        nombre = ValidadorReserva.sanitizar(nombre, 80)
        if not nombre or not ValidadorReserva.es_email_valido(email) \
           or not ValidadorReserva.es_telefono_valido(telefono):
            return {"error": "Datos de contacto inválidos o incompletos."}

        fecha_obj = ValidadorReserva.validar_fecha_futura(fecha)
        if not fecha_obj:
            return {"error": "Fecha inválida o pasada."}

        # Reglas de negocio
        mesa = self._buscar_mesa(mesa_id)
        if not mesa or pax > mesa["capacidad"]:
            return {"error": "Mesa no válida o capacidad excedida."}

        if not self.esta_disponible(mesa_id, fecha):
            return {"error": "Mesa ocupada en ese horario."}

        # Registro
        nueva = {
            "id": self._id_contador, "nombre": nombre, "mesa": mesa_id,
            "fecha_hora": fecha, "comensales": pax, "estado": "activa"
        }
        self.reservas.append(nueva)
        self._id_contador += 1
        self._persistencia.guardar(self.reservas, self._id_contador)
        return {"ok": True, "reserva": nueva}

# ──────────────────────────────────────────────────────────────────────────────
# 5. PUNTO DE ENTRADA
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Inyección de dependencias: Podemos cambiar JSON por una DB sin tocar la lógica
    gestor_json = PersistenciaJSON("reservas.json")
    app = SistemaReservas(persistencia=gestor_json)
    
    # Ejemplo de uso
    resultado = app.crear_reserva("Juan Perez", "600123456", "juan@email.com", 1, "2025-12-01 20:00", 2)
    print(resultado)