"""
Tests EXTREMO A EXTREMO (E2E): el proceso completo, como lo ejecutaría un usuario.

1. Se generan los datos desde cero con data/setup_datos.py en una carpeta temporal.
2. Se comprueba que el generador es determinista (produce los mismos ficheros
   que los que están en el repositorio).
3. Se ejecuta el pipeline completo sobre esos datos y se generan los entregables:
   dataset en Parquet, dashboard en HTML y dataset ampliado con Faker.

Son los tests más lentos y los que más piezas implican: se lanzan solo en main.
Los cuadernos completos se ejecutan aparte con nbmake (ver los workflows).
"""

import json
import subprocess
import sys

import pandas as pd
import pytest
from pipeline import (
    ampliar_dataset,
    calcular_engagement,
    cargar_publicaciones,
    cargar_usuarios,
    crear_dashboard,
    exportar_grafico,
    guardar_parquet,
    limpiar_dataset,
)

pytestmark = pytest.mark.e2e

FICHEROS = ["usuarios.csv", "publicaciones.csv", "publicaciones.xlsx", "conexiones.json"]


@pytest.fixture(scope="module")
def entorno_generado(tmp_path_factory, raiz_proyecto):
    """Ejecuta el generador de datos en una carpeta vacía (una vez por módulo)."""
    carpeta = tmp_path_factory.mktemp("e2e")
    proceso = subprocess.run(
        [sys.executable, str(raiz_proyecto / "data" / "setup_datos.py")],
        cwd=carpeta, capture_output=True, text=True, encoding="utf-8", timeout=120,
    )
    assert proceso.returncode == 0, proceso.stderr
    return carpeta


@pytest.mark.parametrize("nombre", FICHEROS)
def test_el_generador_crea_todos_los_ficheros(entorno_generado, nombre):
    assert (entorno_generado / "data" / nombre).exists()


@pytest.mark.parametrize("nombre", ["usuarios.csv", "publicaciones.csv"])
def test_el_generador_es_determinista_csv(entorno_generado, carpeta_datos, nombre):
    generado = pd.read_csv(entorno_generado / "data" / nombre)
    pd.testing.assert_frame_equal(generado, pd.read_csv(carpeta_datos / nombre))


def test_el_generador_es_determinista_json(entorno_generado, carpeta_datos):
    def leer(ruta):
        return json.loads(ruta.read_text(encoding="utf-8"))
    assert leer(entorno_generado / "data" / "conexiones.json") == leer(carpeta_datos / "conexiones.json")


def test_pipeline_de_extremo_a_extremo(entorno_generado):
    datos = entorno_generado / "data"
    salida = entorno_generado / "salida"

    # Carga y limpieza
    usuarios = limpiar_dataset(cargar_usuarios(datos / "usuarios.csv"))
    publicaciones = limpiar_dataset(cargar_publicaciones(datos / "publicaciones.xlsx"))

    # Transformación
    dataset = calcular_engagement(publicaciones.merge(usuarios, on="id_usuario", how="left"))

    # Entregables
    guardar_parquet(dataset, salida / "dataset_procesado.parquet")
    exportar_grafico(crear_dashboard(dataset), salida / "dashboard.html")
    guardar_parquet(ampliar_dataset(usuarios, 900), salida / "usuarios_grande.parquet")

    # Verificación de los entregables
    leido = pd.read_parquet(salida / "dataset_procesado.parquet")
    assert leido.shape == (300, 23)
    assert leido.isnull().sum().sum() == 0
    assert "Dashboard Red Social Ficticia" in (salida / "dashboard.html").read_text(encoding="utf-8")
    grande = pd.read_parquet(salida / "usuarios_grande.parquet")
    assert len(grande) == 1000
    assert grande["id_usuario"].is_unique
