# 🍽️ Sistema de Reservas de Restaurante
Sistema backend en Python para la gestión integral de reservas en restaurantes. Incluye múltiples versiones refactorizadas con distintos enfoques de diseño (legalidad, estructura y rendimiento), junto con una suite completa de tests automatizados.

---
# 📁 Estructura General del Proyecto
```
.
├── Proyecto de Prueba/                   # Carpeta externa de borradores
│   ├── __init__.py
│   ├── Readme.md
│   └── restaurante.py
│
└── Restaurante/          # Directorio Principal del Proyecto
    │
    ├── Alternativas/
    │   ├── __init__.py
    │   ├── Alt1 - Programación Orientada a Objetos.py
    │   └── Alt2 - Diccionario indexado por ID.py
    │
    ├── core/                             # Lógica de negocio central
    │   ├── __init__.py
    │   └── sistema.py
    │
    ├── data/                             # Capa de datos y persistencia
    │   ├── __init__.py
    │   └── persistence.py
    │
    ├── Refactorizacion/
    │   ├── V1_Legalidad/
    │   │   ├── __init__.py
    │   │   └── Legalidad_restaurante.py
    │   ├── V2_Estructura/
    │   │   ├── __init__.py
    │   │   └── Estructura_restaurante.py
    │   └── V3_Rendimiento/
    │       ├── __init__.py
    │       └── Rendimiento_restaurante.py
    │
    │   
    │   
    │
    ├── tests/                            # Pruebas unitarias y de integración
    │   ├── __init__.py
    │   ├── test_Rendimiento_restauranteV3.py
    │   
    │   
    │
    ├── utils/                            # Funciones de ayuda y validación
    │   ├── __init__.py
    │   ├── security.py
    │   └── validators.py
    │
    ├── conftest.py                       # Configuración compartida de pytest
    ├── pytest.ini                        # Archivo de configuración de pytest
    ├── requirements.txt                  # Dependencias de Python
    ├── .gitignore
    ├── LICENSE
    └── README.md                         # Documentación del proyecto
```

---

# ✨ Funcionalidades

- **Crear reservas** — Alta de reservas con validación de disponibilidad por fecha y hora
- **Cancelar reservas** — Baja de reservas existentes con control de estado
- **Consultar disponibilidad** — Verificación de mesas libres para una fecha y hora dadas
- **Estadísticas** — Generación de informes sobre el estado del sistema de reservas
- **Validaciones de legalidad** — Control de fechas pasadas, capacidades y restricciones de negocio

---

# 🗂️ Versiones de Refactorización

El proyecto incluye tres versiones refactorizadas del núcleo, cada una con un foco diferente:

| Versión | Enfoque | Archivo |
|---|---|---|
| VERSION 1 | **Legalidad** — Validaciones y reglas de negocio estrictas | `Legalidad_restaurante.py` |
| VERSION 2 | **Estructura** — Arquitectura limpia y separación de responsabilidades | `Estructura_restaurante.py` |
| VERSION 3 | **Rendimiento** — Optimización de consultas y operaciones | `Rendimiento_restaurante.py` |

---

# 🚀 Instalación

## Requisitos previos

- Python 3.14
- pip

## Pasos

```bash
# 1. Clona el repositorio
git clone https://github.com/tu-usuario/Sistema_Reservas_Restaurante.git
cd Sistema_Reservas_Restaurante

# 2. Crea y activa un entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Instala las dependencias
pip install -r requirements.txt
```

---

# 🧪 Tests

El proyecto cuenta con una suite completa de tests organizados por funcionalidad y por versión de refactorización.

## Ejecutar todos los tests

```bash
pytest
```

## Ejecutar tests de una funcionalidad específica

```bash
# Tests de creación de reservas
pytest tests/test_crear_reserva_restaurante_v1.py

# Tests de cancelación de reservas
pytest tests/test_cancelar_reserva_restaurante_v2.py

# Tests de disponibilidad
pytest tests/test_disponibilidad_fecha_pasada_rest.py

# Tests de estadísticas
pytest tests/test_estadistica_sin_reserva_restaurante.py
```

## Ejecutar tests de refactorización

```bash
pytest tests/test_refactorizacion_crear_reserva_rest.py
pytest tests/test_refactorizacion_cancelar_reserva_r.py
pytest tests/test_refactorizacion_disponibilidad_fec.py
pytest tests/test_refactorizacion__estadistica_sin_re.py
```

## Ver reporte detallado

```bash
pytest -v
```

---

# 💻 Uso básico

```python
from src.restaurante import Restaurante

# Inicializar el sistema
restaurante = Restaurante()

# Crear una reserva
reserva = restaurante.crear_reserva(
    nombre="María García",
    fecha="2026-04-15",
    hora="20:00",
    num_personas=4
)

# Consultar disponibilidad
disponible = restaurante.consultar_disponibilidad(
    fecha="2026-04-15",
    hora="20:00"
)

# Cancelar una reserva
restaurante.cancelar_reserva(reserva_id=reserva.id)

# Ver estadísticas
stats = restaurante.obtener_estadisticas()
```

---

# 📄 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.# Sistema-de-Reservas-para-un-Restaurante