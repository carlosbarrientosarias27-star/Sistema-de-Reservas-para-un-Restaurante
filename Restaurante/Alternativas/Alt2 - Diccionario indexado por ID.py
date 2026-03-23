"""
ALTERNATIVA 2 — Diccionario indexado por ID
En vez de una lista, las reservas se guardan en un diccionario
donde la clave es el ID. Esto hace las búsquedas por ID O(1).
"""

# ── Datos iniciales ────────────────────────────────────────
MESAS = {
    1: {"numero": 1, "capacidad": 2, "zona": "interior"},
    2: {"numero": 2, "capacidad": 4, "zona": "interior"},
    3: {"numero": 3, "capacidad": 4, "zona": "terraza"},
    4: {"numero": 4, "capacidad": 6, "zona": "terraza"},
    5: {"numero": 5, "capacidad": 8, "zona": "privado"},
}

reservas = {}       # { id_reserva: {...datos...} }
id_contador = 1


# ── Disponibilidad ─────────────────────────────────────────
def esta_disponible(numero_mesa, fecha_hora):
    if numero_mesa not in MESAS:
        return False
    return not any(
        r["mesa"] == numero_mesa
        and r["fecha_hora"] == fecha_hora
        and r["estado"] == "activa"
        for r in reservas.values()
    )


# ── Crear ──────────────────────────────────────────────────
def crear_reserva(nombre, telefono, email,
                  numero_mesa, fecha_hora, comensales):
    global id_contador

    if numero_mesa not in MESAS:
        return {"error": f"Mesa {numero_mesa} no existe."}

    mesa = MESAS[numero_mesa]
    if comensales > mesa["capacidad"]:
        return {"error": f"Capacidad máxima: {mesa['capacidad']} personas."}

    if not esta_disponible(numero_mesa, fecha_hora):
        return {"error": f"Mesa {numero_mesa} ocupada el {fecha_hora}."}

    reservas[id_contador] = {
        "id": id_contador,
        "nombre": nombre,
        "telefono": telefono,
        "email": email,
        "mesa": numero_mesa,
        "zona": mesa["zona"],
        "fecha_hora": fecha_hora,
        "comensales": comensales,
        "estado": "activa",
    }
    id_contador += 1
    return {"ok": True, "reserva": reservas[id_contador - 1]}


# ── Cancelar ───────────────────────────────────────────────
def cancelar_reserva(id_reserva):
    if id_reserva not in reservas:                      # ← O(1) !
        return {"error": f"Reserva {id_reserva} no encontrada."}
    if reservas[id_reserva]["estado"] == "cancelada":
        return {"error": "Ya estaba cancelada."}
    reservas[id_reserva]["estado"] = "cancelada"
    return {"ok": True, "mensaje": f"Reserva {id_reserva} cancelada."}


# ── Consultar cliente ──────────────────────────────────────
def consultar_cliente(nombre):
    return [r for r in reservas.values()
            if r["nombre"].lower() == nombre.lower()
            and r["estado"] == "activa"]


# ── Demo rápida ────────────────────────────────────────────
if __name__ == "__main__":
    r1 = crear_reserva("Ana García", "600111222", "ana@mail.com",
                       2, "2025-08-10 21:00", 3)
    print(r1)

    r2 = crear_reserva("Luis Pérez", "600333444", "luis@mail.com",
                       2, "2025-08-10 21:00", 2)
    print(r2)  # Error: mesa ocupada

    print(cancelar_reserva(1))
    print(consultar_cliente("Ana García"))