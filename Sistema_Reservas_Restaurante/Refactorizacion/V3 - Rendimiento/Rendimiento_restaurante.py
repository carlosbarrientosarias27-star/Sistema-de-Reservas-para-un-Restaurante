import re
import json
import os
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Optional, Any, Tuple

# ──────────────────────────────────────────────────────────────────────────────
# 1. OPTIMIZACIÓN DE RECURSOS: COMPILACIÓN ÚNICA (O(1) en ejecución)
# ──────────────────────────────────────────────────────────────────────────────
# Compilar las regex una sola vez al cargar el módulo evita que Python 
# tenga que re-compilar el patrón cada vez que se llama a la función.
RE_EMAIL = re.compile(r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$")
RE_TEL = re.compile(r"^\+?[\d\s\-]{9,15}$")
RE_SANEADO = re.compile(r"[<>\"'%;()&+\\\x00-\x1f]")

# ──────────────────────────────────────────────────────────────────────────────
# 2. SISTEMA OPTIMIZADO
# ──────────────────────────────────────────────────────────────────────────────

class SistemaReservasOptimizado:
    """
    Gestión de reservas con estructuras de datos optimizadas para alto rendimiento.
    """

    FORMATO_FECHA = "%Y-%m-%d %H:%M"
    CONFIG_MESAS = {
        1: {"capacidad": 2, "zona": "interior"},
        2: {"capacidad": 4, "zona": "interior"},
        3: {"capacidad": 4, "zona": "terraza"},
        4: {"capacidad": 6, "zona": "terraza"},
        5: {"capacidad": 8, "zona": "privado"},
    }

    def __init__(self, ruta_archivo: str = "reservas.json"):
        self.ruta_archivo = ruta_archivo
        self._id_contador: int = 1
        
        # ESTRUCTURAS DE DATOS PARA BÚSQUEDA O(1)
        self.reservas_por_id: Dict[int, Dict] = {} # [Mejora: O(1) vs O(n)]
        self.reservas_por_cliente: Dict[str, List[Dict]] = defaultdict(list) # [Mejora: O(1)]
        self.ocupacion_mesas: Dict[Tuple[int, str], bool] = {} # [Mejora: O(1) para disponibilidad]
        
        self._cargar_y_indexar()

    # ── Indexación de Datos (O(n) una