"""
SISTEMA DE RESERVAS - EDICIÓN LEGIBLE
Módulo: Gestión de Seguridad y Persistencia
"""

import re
import json
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any, Union

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN Y CONSTANTES
# ──────────────────────────────────────────────────────────────────────────────

MAX_RESERVAS_POR_CLIENTE: int = 5
ARCHIVO_PERSISTENCIA: str = "reservas.json"
FORMATO_FECHA_ESTANDAR: str = "%Y-%m-%d %H:%M"

# ──────────────────────────────────────────────────────────────────────────────
# UTILIDADES DE VALIDACIÓN Y SANEAMIENTO
# ──────────────────────────────────────────────────────────────────────────────

def es_email_valido(email_candidato: str) -> bool:
    """
    Verifica si una cadena cumple con el formato estándar de correo electrónico.
    
    Args:
        email_candidato: El texto a validar.
    Returns:
        True si el formato es correcto, False en caso contrario.
    """
    patron_regex: str = r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(patron_regex, email_candidato.strip()))


def es_telefono_valido(telefono_candidato: str) -> bool:
    """
    Valida que el teléfono contenga entre 9 y 15 dígitos, permitiendo prefijos y guiones.
    """
    patron_regex: str = r"^\+?[\d\s\-]{9,15}$"
    return bool(re.match(patron_regex, telefono_candidato.strip()))


def sanitizar_entrada_texto(texto_sucio: str, longitud_maxima: int = 100) -> str:
    """
    Limpia una cadena de caracteres eliminando símbolos potencialmente peligrosos 
    para prevenir inyecciones y recorta la longitud.
    """
    caracteres_prohibidos: str = r"[<>\"'%;()&+\\\x00-\x1f]"
    texto_limpio: str = re.sub(caracteres_prohibidos, "", texto_sucio)
    return texto_limpio.strip()[:longitud_maxima]


def parsear_y_validar_fecha(cadena_fecha: str) -> Optional[datetime]:
    """
    Convierte una cadena a datetime y verifica que no sea una fecha pasada.
    
    Returns:
        Objeto datetime si es válida y futura; None si es inválida o pasada.
    """
    try:
        fecha_objeto: datetime = datetime.strptime(cadena_fecha.strip(), FORMATO_FECHA_ESTANDAR)
        if fecha_objeto <= datetime.now():
            return None
        return fecha_objeto
    except ValueError:
        return None

# ──────────────────────────────────────────────────────────────────────────────
# GESTIÓN DE PERSISTENCIA (JSON)
# ──────────────────────────────────────────────────────────────────────────────

def cargar_estado_desde_disco() -> Tuple[List[Dict[str, Any]], int]:
    """
    Recupera el listado de reservas y el contador de IDs desde el archivo local.
    """
    if not os.path.exists(ARCHIVO_PERSISTENCIA):
        return [], 1
    
    try:
        with open(ARCHIVO_PERSISTENCIA, "r", encoding="utf-8") as archivo:
            datos: Dict[str, Any] = json.load(archivo)
        return datos.get("reservas", []), datos.get("id_contador", 1)
    except (json.JSONDecodeError, KeyError):
        print("⚠️ Error: El archivo de datos está corrupto. Se iniciará un estado vacío.")
        return [], 1


def guardar_estado_en_disco(listado_reservas: List[Dict[str, Any]], id_actual: int) -> None:
    """
    Sincroniza el estado actual del sistema con el archivo JSON.
    """
    payload: Dict[str, Any] = {
        "reservas": listado_reservas,
        "id_contador": id_actual
    }
    with open(ARCHIVO_PERSISTENCIA, "w", encoding="utf-8") as archivo:
        json.dump(payload, archivo, ensure_ascii=False, indent=2)

# ──────────────────────────────────────────────────────────────────────────────
# NÚCLEO DEL SISTEMA: CLASE DE GESTIÓN
# ──────────────────────────────────────────────────────────────────────────────

class SistemaReservas:
    """
    Controlador principal que encapsula la lógica de negocio y el estado de las mesas.
    """

    CONFIGURACION_MESAS: List[Dict[str, Any]] = [
        {"numero": 1, "capacidad": 2, "zona": "interior"},
        {"numero": 2, "capacidad": 4, "zona": "interior"},
        {"numero": 3, "capacidad": 4, "zona": "terraza"},
        {"numero": 4, "capacidad": 6, "zona": "terraza"},
        {"numero": 5, "capacidad": 8, "zona": "privado"},
    ]

    def __init__(self) -> None:
        self.reservas: List[Dict[str, Any]]
        self._proximo_id: int
        self.reservas, self._proximo_id = cargar_estado_desde_disco()

    # ── Consultas Internas ─────────────────────────────────

    def _obtener_datos_mesa(self, numero_mesa: int) -> Optional[Dict[str, Any]]:
        """Busca la configuración técnica de una mesa por su número."""
        return next((mesa for mesa in self.CONFIGURACION_MESAS if mesa["numero"] == numero_mesa), None)

    def _obtener_reservas_activas_por_nombre(self, nombre_cliente: str) -> List[Dict[str, Any]]:
        """Filtra todas las reservas con estado 'activa' para un cliente específico."""
        nombre_normalizado: str = nombre_cliente.lower()
        return [
            reserva for reserva in self.reservas
            if reserva["nombre"].lower() == nombre_normalizado and reserva["estado"] == "activa"
        ]

    # ── Lógica de Negocio ──────────────────────────────────

    def verificar_disponibilidad(self, numero_mesa: int, fecha_hora_str: str) -> bool:
        """Determina si una mesa está libre en un slot temporal específico."""
        esta_ocupada: bool = any(
            r["mesa"] == numero_mesa and 
            r["fecha_hora"] == fecha_hora_str and 
            r["estado"] == "activa"
            for r in self.reservas
        )
        return not esta_ocupada

    def crear_reserva(self, nombre: str, telefono: str, email: str,
                      numero_mesa: int, fecha_str: str, total_comensales: int) -> Dict[str, Any]:
        """
        Procesa y valida la creación de una nueva reserva en el sistema.
        """
        # Saneamiento de datos
        nombre_limpio: str = sanitizar_entrada_texto(nombre, max_len=80)
        tel_limpio: str = sanitizar_entrada_texto(telefono, max_len=20)
        email_limpio: str = sanitizar_entrada_texto(email, max_len=100)

        # Validaciones de integridad
        if not nombre_limpio:
            return {"error": "El nombre no puede estar vacío."}
        if not es_email_valido(email_limpio):
            return {"error": f"Email inválido: '{email_limpio}'."}
        if not es_telefono_valido(tel_limpio):
            return {"error": f"Teléfono inválido: '{tel_limpio}'."}

        # Validación temporal
        fecha_objeto: Optional[datetime] = parsear_y_validar_fecha(fecha_str)
        if fecha_objeto is None:
            return {"error": f"Fecha inválida o pasada. Use: {FORMATO_FECHA_ESTANDAR}"}

        # Validación de recursos (mesa y capacidad)
        datos_mesa: Optional[Dict[str, Any]] = self._obtener_datos_mesa(numero_mesa)
        if datos_mesa is None:
            return {"error": f"La mesa {numero_mesa} no existe."}
        
        if not isinstance(total_comensales, int) or total_comensales < 1:
            return {"error": "El número de comensales debe ser un entero positivo."}
            
        if total_comensales > datos_mesa["capacidad"]:
            return {"error": f"Capacidad excedida. Máximo: {datos_mesa['capacidad']} personas."}

        # Restricciones de negocio
        activas: List[Dict[str, Any]] = self._obtener_reservas_activas_por_nombre(nombre_limpio)
        if len(activas) >= MAX_RESERVAS_POR_CLIENTE:
            return {"error": f"Límite alcanzado ({MAX_RESERVAS_POR_CLIENTE} reservas activas)."}

        if not self.verificar_disponibilidad(numero_mesa, fecha_str):
            return {"error": f"Mesa {numero_mesa} no disponible para esa fecha/hora."}

        # Registro exitoso
        nueva_reserva: Dict[str, Any] = {
            "id": self._proximo_id,
            "nombre": nombre_limpio,
            "telefono": tel_limpio,
            "email": email_limpio,
            "mesa": numero_mesa,
            "zona": datos_mesa["zona"],
            "fecha_hora": fecha_str,
            "comensales": total_comensales,
            "estado": "activa",
        }
        
        self.reservas.append(nueva_reserva)
        self._proximo_id += 1
        guardar_estado_en_disco(self.reservas, self._proximo_id)
        
        return {"ok": True, "reserva": nueva_reserva}

    def cancelar_reserva(self, id_reserva: int) -> Dict[str, Any]:
        """Cambia el estado de una reserva a 'cancelada'."""
        for reserva in self.reservas:
            if reserva["id"] == id_reserva:
                if reserva["estado"] == "cancelada":
                    return {"error": "Esta reserva ya se encuentra cancelada."}
                
                reserva["estado"] = "cancelada"
                guardar_estado_en_disco(self.reservas, self._proximo_id)
                return {"ok": True, "mensaje": f"Reserva {id_reserva} cancelada correctamente."}
        
        return {"error": f"ID {id_reserva} no encontrado."}

    def consultar_por_cliente(self, nombre_cliente: str) -> List[Dict[str, Any]]:
        """Retorna las reservas activas asociadas a un nombre de cliente."""
        nombre_sanitizado: str = sanitizar_entrada_texto(nombre_cliente)
        return self._obtener_reservas_activas_por_nombre(nombre_sanitizado)

    def modificar_reserva(self, id_reserva: int, 
                          nueva_fecha: Optional[str] = None, 
                          nuevos_comensales: Optional[int] = None) -> Dict[str, Any]:
        """
        Permite actualizar la fecha o el número de personas de una reserva existente.
        """
        for reserva in self.reservas:
            if reserva["id"] == id_reserva and reserva["estado"] == "activa":
                
                if nueva_fecha:
                    if not parsear_y_validar_fecha(nueva_fecha):
                        return {"error": "La nueva fecha es inválida o pasada."}
                    if not self.verificar_disponibilidad(reserva["mesa"], nueva_fecha):
                        return {"error": "La mesa está ocupada en ese nuevo horario."}
                    reserva["fecha_hora"] = nueva_fecha
                
                if nuevos_comensales:
                    info_mesa: Dict[str, Any] = self._obtener_datos_mesa(reserva["mesa"])
                    if nuevos_comensales > info_mesa["capacidad"]:
                        return {"error": f"Capacidad máxima de mesa: {info_mesa['capacidad']}."}
                    reserva["comensales"] = nuevos_comensales

                guardar_estado_en_disco(self.reservas, self._proximo_id)
                return {"ok": True, "reserva": reserva}
                
        return {"error": f"No se encontró una reserva activa con ID {id_reserva}."}

# ──────────────────────────────────────────────────────────────────────────────
# INTERFAZ DE USUARIO (CLI)
# ──────────────────────────────────────────────────────────────────────────────

def imprimir_ficha_reserva(r: Dict[str, Any]) -> None:
    """Muestra los detalles de una reserva de forma estética en consola."""
    print(f"  ID: {r['id']} | Cliente: {r['nombre']} | Mesa: {r['mesa']} ({r['zona'].upper()})")
    print(f"  Agenda: {r['fecha_hora']} | Grupo: {r['comensales']} pax | Estado: {r['estado'].upper()}")
    print(f"  Contacto: {r['telefono']} / {r['email']}\n")


def ejecutar_menu_principal() -> None:
    """Loop principal de interacción con el usuario."""
    sistema: SistemaReservas = SistemaReservas()
    print(f"🚀 Sistema iniciado. Registros actuales: {len(sistema.reservas)}")

    while True:
        print("\n" + "="*45)
        print("      GESTIÓN DE RESERVAS - RESTAURANTE")
        print("="*45)
        print("1. Nueva Reserva")
        print("2. Buscar por Cliente")
        print("3. Cancelar Reserva")
        print("4. Modificar Reserva")
        print("5. Consultar Disponibilidad")
        print("0. Salir")
        
        seleccion: str = input("\nSeleccione una opción: ").strip()

        if seleccion == "1":
            try:
                nom: str = input("Nombre completo: ")
                tel: str = input("Teléfono: ")
                eml: str = input("Email: ")
                num_m: int = int(input("Número de mesa (1-5): "))
                fec: str = input(f"Fecha/Hora ({FORMATO_FECHA_ESTANDAR}): ")
                pax: int = int(input("Número de comensales: "))
                
                resultado: Dict[str, Any] = sistema.crear_reserva(nom, tel, eml, num_m, fec, pax)
                if "error" in resultado:
                    print(f"❌ Error: {resultado['error']}")
                else:
                    print("✅ ¡Reserva confirmada!")
                    imprimir_ficha_reserva(resultado["reserva"])
            except ValueError:
                print("❌ Error: Los campos numéricos deben ser enteros.")

        elif seleccion == "2":
            nom_busqueda: str = input("Nombre del cliente: ")
            encontradas: List[Dict[str, Any]] = sistema.consultar_por_cliente(nom_busqueda)
            if encontradas:
                for res in encontradas:
                    imprimir_ficha_reserva(res)
            else:
                print("No se encontraron reservas activas.")

        elif seleccion == "3":
            try:
                id_cancelar: int = int(input("Ingrese el ID de la reserva: "))
                res_canc: Dict[str, Any] = sistema.cancelar_reserva(id_cancelar)
                print(f"✅ {res_canc['mensaje']}" if "ok" in res_canc else f"❌ {res_canc['error']}")
            except ValueError:
                print("❌ ID inválido.")

        elif seleccion == "4":
            try:
                id_mod: int = int(input("ID de la reserva: "))
                f_nueva: str = input("Nueva fecha (Enter para omitir): ").strip() or None
                c_input: str = input("Nuevos comensales (Enter para omitir): ").strip()
                c_nueva: Optional[int] = int(c_input) if c_input else None
                
                res_mod: Dict[str, Any] = sistema.modificar_reserva(id_mod, f_nueva, c_nueva)
                if "error" in res_mod:
                    print(f"❌ {res_mod['error']}")
                else:
                    print("✅ Cambios aplicados:")
                    imprimir_ficha_reserva(res_mod["reserva"])
            except ValueError:
                print("❌ Entrada de datos no válida.")

        elif seleccion == "5":
            try:
                m_check: int = int(input("Mesa a consultar: "))
                f_check: str = input("Fecha y hora: ")
                esta_libre: bool = sistema.verificar_disponibilidad(m_check, f_check)
                print("✅ DISPONIBLE" if esta_libre else "❌ OCUPADA o inexistente")
            except ValueError:
                print("❌ Formato incorrecto.")

        elif seleccion == "0":
            print("Cerrando sistema... ¡Buen servicio!")
            break
        else:
            print("Opción no reconocida.")


if __name__ == "__main__":
    ejecutar_menu_principal()