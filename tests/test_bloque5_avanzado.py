"""Tests avanzados del Bloque 5: Plotly y Faker."""

import os
import sys

import pandas as pd
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from pipeline_avanzada import ampliar_dataset_avanzado, exportar_figuras_avanzadas


def usuarios_test():
    return pd.DataFrame({
        "id_usuario": [1, 2], "nombre": ["Ana", "Borja"], "apellidos": ["Garcia", "Lopez"],
        "edad": [25, 35], "ciudad": ["Madrid", "Bilbao"], "pais": ["Espana", "Espana"],
        "genero": ["F", "M"], "fecha_registro": ["2022-01-01", "2023-01-01"],
        "tipo_cuenta": ["creator", "free"], "seguidores": [5000, 300], "seguidos": [200, 100],
        "publicaciones_totales": [150, 20], "activo": ["True", "False"], "bio": ["Bio 1", "Bio 2"],
    })


def test_exportar_figuras_avanzadas(tmp_path):
    try:
        import plotly.express as px
        figura = px.bar(x=["A"], y=[1])
    except ImportError:
        pytest.skip("Plotly no está instalado o está incompleto")
    rutas = exportar_figuras_avanzadas({"grafico": figura}, tmp_path)
    assert len(rutas) == 1
    assert (tmp_path / "grafico.html").exists()


def test_ampliar_dataset_avanzado():
    original = usuarios_test()
    resultado = ampliar_dataset_avanzado(original, 5, seed=42)
    assert len(resultado) == 7
    assert resultado["id_usuario"].is_unique
    assert list(resultado.columns) == list(original.columns)
    pd.testing.assert_frame_equal(resultado.head(2), original)
