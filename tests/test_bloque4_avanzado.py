"""Tests avanzados del Bloque 4: Pandas avanzado."""

import os
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from pipeline_avanzada import analizar_categorias, comparar_formatos, tabla_engagement_ciudad_contenido


def test_analizar_categorias():
    df = pd.DataFrame({"tipo": ["free", "premium", "free"], "ciudad": ["Madrid", "Bilbao", "Madrid"]})
    resultado = analizar_categorias(df, ["tipo", "ciudad"])
    assert all(resultado["tipo"] == "category")
    assert resultado.loc["tipo", "categorias"] == 2


def test_tabla_engagement_ciudad_contenido():
    df = pd.DataFrame({
        "tipo_contenido": ["foto", "foto", "video"],
        "ciudad": ["Madrid", "Madrid", "Bilbao"],
        "engagement_rate": [0.2, 0.4, 0.8],
    })
    resultado = tabla_engagement_ciudad_contenido(df)
    assert np.isclose(resultado.loc["foto", "Madrid"], 0.3)


def test_comparar_formatos(tmp_path):
    df = pd.DataFrame({"id": [1, 2], "valor": [10, 20], "tipo": ["a", "b"]})
    try:
        resultado = comparar_formatos(df, tmp_path / "datos")
    except ImportError:
        return
    assert resultado["csv_bytes"] > 0
    assert resultado["parquet_bytes"] > 0
    assert (tmp_path / "datos.csv").exists()
