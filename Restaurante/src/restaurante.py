"""
SISTEMA DE RESERVAS - VERSIÓN SEGURA
Paso 5: Correcciones de seguridad aplicadas
Módulo 2 · Técnicas Avanzadas con IA

Vulnerabilidades corregidas:
  [1] Validación de tipos y formatos (email, teléfono, fecha)
  [2] Saneamiento de entradas de texto
  [3] Estado global → clase con estado encapsulado
  [4] Validación de fecha lógica (no permite fechas pasadas)
  [5] Límite de reservas activas por cliente
  [6] Persistencia básica en JSON (los datos no se pierden al cerrar)
"""

import re
import json
import os
from datetime import datetime

# ─────────────────────────────────────────────────────────
# CONSTANTES DE SEGURIDAD
# ─────────────────────────────────────────────────────────
MAX_RESERVAS_POR_CLIENTE = 5      # [5] Límite anti-abuso
ARCHIVO_DATOS = "reservas.json"   # [6] Fichero de persistencia
FORMATO_FECHA = "%Y-%m-%d %H:%M"  # Formato esperado para fechas


# ─────────────────────────────────────────────────────────
# VALIDADORES  [1] [2]
# ─────────────────────────────────────────────────────────

def validar_email(email: str) -> bool:
    """Comprueba que el email tiene formato básico válido."""
    patron = r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(patron, email.strip()))


def validar_telefono(telefono: str) -> bool:
    """Acepta teléfonos con 9-15 dígitos, espacios y guiones."""
    patron = r"^\+?[\d\s\-]{9,15}$"
    return bool(re.match(patron, telefono.strip()))


def sanitizar_texto(texto: str, max_len: int = 100) -> str:
    """
    [2] Elimina caracteres peligrosos y limita longitud.
    Permite letras, números, espacios, acentos y puntuación básica.
    """
    limpio = re.sub(r"[<>\"'%;()&+\\\x00-\x1f]", "", texto)
    return limpio.strip()[:max_len]


def validar_fecha(fecha_str: str) -> datetime | None:
    """
    [4] Parsea la fecha y comprueba que es futura.
    Devuelve el objeto datetime o None si es inválida.
    """
    try:
        fecha = datetime.strptime(fecha_str.strip(), FORMATO_FECHA)
        if fecha <= datetime.now():
            return None  # No se permiten fechas pasadas
        return fecha
    except ValueError:
        return None


# ─────────────────────────────────────────────────────────
# PERSISTENCIA  [6]
# ─────────────────────────────────────────────────────────

def cargar_datos() -> tuple[list, int]:
    """Carga reservas desde JSON. Si no existe, devuelve valores vacíos."""
    if not os.path.exists(ARCHIVO_DATOS):
        return [], 1
    try:
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            datos = json.load(f)
        return datos.get("reservas", []), datos.get("id_contador", 1)
    except (json.JSONDecodeError, KeyError):
        print("⚠️  Archivo de datos corrupto. Iniciando con datos vacíos.")
        return [], 1


def guardar_datos(reservas: list, id_contador: int) -> None:
    """Guarda el estado actual en JSON."""
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump({"reservas": reservas, "id_contador": id_contador},
                  f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────────────────
# SISTEMA DE RESERVAS  [3] Estado encapsulado en clase
# ─────────────────────────────────────────────────────────

class SistemaReservas:
    """
    [3] El estado (reservas, id_contador) vive dentro de la clase,
    no en variables globales. Esto evita colisiones en entornos
    con múltiples instancias o hilos.
    """

    MESAS = [
        {"numero": 1, "capacidad": 2, "zona": "interior"},
        {"numero": 2, "capacidad": 4, "zona": "interior"},
        {"numero": 3, "capacidad": 4, "zona": "terraza"},
        {"numero": 4, "capacidad": 6, "zona": "terraza"},
        {"numero": 5, "capacidad": 8, "zona": "privado"},
    ]

    def __init__(self):
        self.reservas, self._id_contador = cargar_datos()

    # ── Búsquedas internas ─────────────────────────────────
    def _buscar_mesa(self, numero: int) -> dict | None:
        return next((m for m in self.MESAS if m["numero"] == numero), None)

    def _reservas_activas_cliente(self, nombre: str) -> list:
        nombre_lower = nombre.lower()
        return [r for r in self.reservas
                if r["nombre"].lower() == nombre_lower
                and r["estado"] == "activa"]

    # ── Disponibilidad ─────────────────────────────────────
    def esta_disponible(self, numero_mesa: int, fecha_str: str) -> bool:
        return not any(
            r["mesa"] == numero_mesa
            and r["fecha_hora"] == fecha_str
            and r["estado"] == "activa"
            for r in self.reservas
        )

    # ── Crear reserva ──────────────────────────────────────
    def crear_reserva(self, nombre: str, telefono: str, email: str,
                      numero_mesa: int, fecha_str: str, comensales: int) -> dict:

        # [2] Sanitizar entradas de texto
        nombre   = sanitizar_texto(nombre, max_len=80)
        telefono = sanitizar_texto(telefono, max_len=20)
        email    = sanitizar_texto(email, max_len=100)

        # [1] Validar formato de email y teléfono
        if not nombre:
            return {"error": "El nombre no puede estar vacío."}
        if not validar_email(email):
            return {"error": f"Email inválido: '{email}'."}
        if not validar_telefono(telefono):
            return {"error": f"Teléfono inválido: '{telefono}'."}

        # [4] Validar que la fecha es futura y tiene formato correcto
        fecha_obj = validar_fecha(fecha_str)
        if fecha_obj is None:
            return {"error": f"Fecha inválida o en el pasado. Usa el formato: {FORMATO_FECHA}"}

        # Validar mesa
        mesa = self._buscar_mesa(numero_mesa)
        if mesa is None:
            return {"error": f"La mesa {numero_mesa} no existe."}
        if not isinstance(comensales, int) or comensales < 1:
            return {"error": "El número de comensales debe ser un entero positivo."}
        if comensales > mesa["capacidad"]:
            return {"error": f"Mesa {numero_mesa}: capacidad máxima {mesa['capacidad']} personas."}

        # [5] Límite de reservas activas por cliente
        activas = self._reservas_activas_cliente(nombre)
        if len(activas) >= MAX_RESERVAS_POR_CLIENTE:
            return {"error": f"'{nombre}' ya tiene {MAX_RESERVAS_POR_CLIENTE} reservas activas (límite máximo)."}

        # Comprobar disponibilidad
        if not self.esta_disponible(numero_mesa, fecha_str):
            return {"error": f"Mesa {numero_mesa} ocupada el {fecha_str}."}

        # Crear reserva
        nueva = {
            "id":         self._id_contador,
            "nombre":     nombre,
            "telefono":   telefono,
            "email":      email,
            "mesa":       numero_mesa,
            "zona":       mesa["zona"],
            "fecha_hora": fecha_str,
            "comensales": comensales,
            "estado":     "activa",
        }
        self.reservas.append(nueva)
        self._id_contador += 1
        guardar_datos(self.reservas, self._id_contador)  # [6] Persistir
        return {"ok": True, "reserva": nueva}

    # ── Cancelar ───────────────────────────────────────────
    def cancelar_reserva(self, id_reserva: int) -> dict:
        for r in self.reservas:
            if r["id"] == id_reserva:
                if r["estado"] == "cancelada":
                    return {"error": "La reserva ya estaba cancelada."}
                r["estado"] = "cancelada"
                guardar_datos(self.reservas, self._id_contador)  # [6]
                return {"ok": True, "mensaje": f"Reserva {id_reserva} cancelada."}
        return {"error": f"No existe la reserva con ID {id_reserva}."}

    # ── Consultar cliente ──────────────────────────────────
    def consultar_cliente(self, nombre: str) -> list:
        nombre = sanitizar_texto(nombre)  # [2] Sanitizar también la búsqueda
        return self._reservas_activas_cliente(nombre)

    # ── Modificar ──────────────────────────────────────────
    def modificar_reserva(self, id_reserva: int,
                          nueva_fecha: str | None = None,
                          nuevos_comensales: int | None = None) -> dict:
        for r in self.reservas:
            if r["id"] == id_reserva and r["estado"] == "activa":
                if nueva_fecha:
                    fecha_obj = validar_fecha(nueva_fecha)  # [4]
                    if fecha_obj is None:
                        return {"error": "Fecha inválida o en el pasado."}
                    if not self.esta_disponible(r["mesa"], nueva_fecha):
                        return {"error": f"Mesa {r['mesa']} ocupada el {nueva_fecha}."}
                    r["fecha_hora"] = nueva_fecha
                if nuevos_comensales:
                    mesa = self._buscar_mesa(r["mesa"])
                    if nuevos_comensales > mesa["capacidad"]:
                        return {"error": f"Capacidad máxima: {mesa['capacidad']}."}
                    r["comensales"] = nuevos_comensales
                guardar_datos(self.reservas, self._id_contador)  # [6]
                return {"ok": True, "reserva": r}
        return {"error": f"No se encontró la reserva activa {id_reserva}."}


# ─────────────────────────────────────────────────────────
# MENÚ INTERACTIVO
# ─────────────────────────────────────────────────────────

def mostrar_reserva(r: dict) -> None:
    print(f"  #{r['id']} | {r['nombre']} | Mesa {r['mesa']} ({r['zona']})")
    print(f"  {r['fecha_hora']} | {r['comensales']} comensales | {r['estado']}")
    print(f"  {r['telefono']} / {r['email']}\n")


def ejecutar():
    sr = SistemaReservas()
    print(f"✅ Sistema cargado — {len(sr.reservas)} reservas en memoria.")

    while True:
        print("\n====== SISTEMA DE RESERVAS (SEGURO) ======")
        print("1. Crear reserva")
        print("2. Consultar reservas de un cliente")
        print("3. Cancelar reserva")
        print("4. Modificar reserva")
        print("5. Comprobar disponibilidad")
        print("0. Salir")
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            nombre     = input("Nombre: ")
            telefono   = input("Teléfono: ")
            email      = input("Email: ")
            try:
                mesa       = int(input("Número de mesa (1-5): "))
                fecha      = input(f"Fecha y hora ({FORMATO_FECHA}): ")
                comensales = int(input("Comensales: "))
            except ValueError:
                print("❌ Número de mesa y comensales deben ser enteros.")
                continue
            res = sr.crear_reserva(nombre, telefono, email, mesa, fecha, comensales)
            if "error" in res:
                print(f"❌ {res['error']}")
            else:
                print("✅ Reserva creada:")
                mostrar_reserva(res["reserva"])

        elif opcion == "2":
            nombre = input("Nombre del cliente: ")
            lista  = sr.consultar_cliente(nombre)
            if lista:
                for r in lista:
                    mostrar_reserva(r)
            else:
                print("No hay reservas activas para ese cliente.")

        elif opcion == "3":
            try:
                id_r = int(input("ID de la reserva: "))
            except ValueError:
                print("❌ El ID debe ser un número entero.")
                continue
            res = sr.cancelar_reserva(id_r)
            print(f"✅ {res['mensaje']}" if "ok" in res else f"❌ {res['error']}")

        elif opcion == "4":
            try:
                id_r = int(input("ID de la reserva: "))
            except ValueError:
                print("❌ El ID debe ser un número entero.")
                continue
            nueva_fecha = input("Nueva fecha (vacío = no cambiar): ").strip() or None
            nc = input("Nuevos comensales (vacío = no cambiar): ").strip()
            nuevos_com = int(nc) if nc else None
            res = sr.modificar_reserva(id_r, nueva_fecha, nuevos_com)
            if "error" in res:
                print(f"❌ {res['error']}")
            else:
                print("✅ Reserva modificada:")
                mostrar_reserva(res["reserva"])

        elif opcion == "5":
            try:
                mesa  = int(input("Número de mesa: "))
            except ValueError:
                print("❌ El número de mesa debe ser un entero.")
                continue
            fecha = input("Fecha y hora: ")
            libre = sr.esta_disponible(mesa, fecha)
            print("✅ Mesa LIBRE" if libre else "❌ Mesa OCUPADA o no existe")

        elif opcion == "0":
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    ejecutar()