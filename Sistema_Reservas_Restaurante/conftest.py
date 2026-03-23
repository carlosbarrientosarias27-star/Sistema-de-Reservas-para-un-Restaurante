# conftest.py
# Coloca este archivo en la RAÍZ del proyecto:
#
# Sistema_Reservas_Restaurante/
# ├── conftest.py                ← aquí
# ├── Refactorizacion/
# │   └── V3_Rendimiento/
# │       └── Rendimiento_restaurante.py
# └── tests/
#     └── test_Rendimiento_restauranteV3.py
#
# Pytest lo detecta automáticamente y añade la raíz al path de Python,
# lo que permite que el import funcione correctamente:
#
#   from Refactorizacion.V3_Rendimiento.Rendimiento_restaurante import SistemaReservas
#
# Ejecuta los tests desde la raíz con:
#   pytest tests/ -v

import sys
import os

# Añade la raíz del proyecto al path por si pytest no lo hace solo
sys.path.insert(0, os.path.dirname(__file__))