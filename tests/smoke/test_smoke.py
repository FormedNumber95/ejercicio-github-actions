"""
Tests SMOKE (de humo): comprobaciones mínimas y muy rápidas.

Responden a una sola pregunta: ¿el proyecto "arranca"? Si alguno falla, no tiene
sentido ejecutar el resto de la batería (por eso son lo primero que se lanza en
cualquier rama). Deben tardar muy poco y no dependen de resultados concretos.
"""

import importlib
import sys

import pandas as pd
import pytest

pytestmark = pytest.mark.smoke

LIBRERIAS = ["numpy", "pandas", "pyarrow", "plotly", "faker", "openpyxl"]
FICHEROS_DATOS = ["usuarios.csv", "publicaciones.csv", "publicaciones.xlsx", "conexiones.json"]


def test_version_de_python():
    assert sys.version_info >= (3, 14), "El proyecto requiere Python 3.14 o superior"


@pytest.mark.parametrize("libreria", LIBRERIAS)
def test_librerias_instaladas(libreria):
    importlib.import_module(libreria)


def test_se_importa_el_pipeline():
    import pipeline
    import pipeline_avanzada

    assert callable(pipeline.calcular_engagement)
    assert callable(pipeline_avanzada.auditar_dataframe)


@pytest.mark.parametrize("nombre", FICHEROS_DATOS)
def test_existen_los_ficheros_de_datos(carpeta_datos, nombre):
    ruta = carpeta_datos / nombre
    assert ruta.exists(), f"Falta {ruta}: ejecuta 'uv run python data/setup_datos.py'"
    assert ruta.stat().st_size > 0, f"{ruta} está vacío"


def test_el_pipeline_responde_con_un_caso_minimo():
    from pipeline import calcular_engagement

    df = pd.DataFrame({"likes": [1], "comentarios": [1], "compartidos": [0], "visualizaciones": [4]})
    assert calcular_engagement(df).loc[0, "engagement_rate"] == 0.5
