import json
import os
from config import ARCHIVO_DATOS 

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
