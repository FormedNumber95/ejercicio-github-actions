"""
Configuración común de la batería de tests.

- Marca automáticamente como ``unit`` los tests de los bloques (tests/test_*.py).
  El resto de tipos de test (smoke, esquema, valores, relaciones, integracion,
  metricas, regresion, e2e) declaran su marcador con ``pytestmark`` en cada fichero.
- Ofrece fixtures con los datos reales del proyecto. Se leen una sola vez por
  sesión y cada test recibe una COPIA, para que ningún test pueda modificar los
  datos que usan los demás.

Ejecutar un tipo concreto:   pytest -m smoke
Combinar tipos:              pytest -m "esquema or valores or relaciones"
Ver los marcadores:          pytest --markers
"""

import json
from pathlib import Path

import pandas as pd
import pytest

CARPETA_TESTS = Path(__file__).resolve().parent
RAIZ = CARPETA_TESTS.parent
DATA = RAIZ / "data"


def pytest_collection_modifyitems(config, items):
    """Los ficheros que están directamente en tests/ son tests unitarios."""
    for item in items:
        if Path(str(item.fspath)).parent == CARPETA_TESTS:
            item.add_marker(pytest.mark.unit)


# ── Rutas ────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def raiz_proyecto():
    return RAIZ


@pytest.fixture(scope="session")
def carpeta_datos():
    return DATA


# ── Datos reales (lectura única por sesión) ─────────────────────────────────

@pytest.fixture(scope="session")
def _usuarios_original():
    return pd.read_csv(DATA / "usuarios.csv")


@pytest.fixture(scope="session")
def _publicaciones_original():
    return pd.read_excel(DATA / "publicaciones.xlsx", sheet_name="publicaciones")


@pytest.fixture(scope="session")
def _conexiones_original():
    with open(DATA / "conexiones.json", encoding="utf-8") as fichero:
        return json.load(fichero)


@pytest.fixture
def usuarios(_usuarios_original):
    """Tabla de usuarios tal como está en data/usuarios.csv (copia)."""
    return _usuarios_original.copy()


@pytest.fixture
def publicaciones(_publicaciones_original):
    """Tabla de publicaciones de data/publicaciones.xlsx (copia)."""
    return _publicaciones_original.copy()


@pytest.fixture
def conexiones(_conexiones_original):
    """Lista de conexiones de data/conexiones.json (copia profunda)."""
    return [dict(c, siguiendo=list(c["siguiendo"])) for c in _conexiones_original]
