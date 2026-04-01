import json
import os
from Restaurante.config import ARCHIVO_DATOS

def cargar_datos(ruta: str | None = None) -> tuple[list, int]:
    """Carga reservas desde JSON. Si no existe, devuelve valores vacíos."""
    archivo = ruta if ruta else ARCHIVO_DATOS
    if not os.path.exists(archivo):
        return [], 1
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)
        return datos.get("reservas", []), datos.get("id_contador", 1)
    except (json.JSONDecodeError, KeyError, UnicodeDecodeError):
        print("⚠️  Archivo de datos corrupto. Iniciando con datos vacíos.")
        return [], 1


def guardar_datos(reservas: list, id_contador: int, ruta: str | None = None) -> None:
    """Guarda el estado actual en JSON."""
    archivo = ruta if ruta else ARCHIVO_DATOS
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump({"reservas": reservas, "id_contador": id_contador},
                  f, ensure_ascii=False, indent=2)
