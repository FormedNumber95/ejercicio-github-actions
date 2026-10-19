"""
Tests unitarios de engagement_por_contenido (marcador ``unit``, asignado por conftest.py).

Ejemplo de feature desarrollada en su propia rama: la función nueva llega
acompañada de sus tests, y el workflow de la rama feature los ejecuta.
"""

import pandas as pd
import pytest
from pipeline import engagement_por_contenido


@pytest.fixture
def publicaciones_con_engagement():
    return pd.DataFrame({
        "tipo_contenido": ["foto", "foto", "video", "texto", "video", "video"],
        "engagement_rate": [0.2, 0.4, 0.9, 0.1, 0.6, 0.3],
    })


@pytest.mark.parametrize(
    ("tipo", "n_esperado", "media_esperada"),
    [("foto", 2, 0.3), ("video", 3, 0.6), ("texto", 1, 0.1)],
)
def test_resumen_de_cada_tipo(publicaciones_con_engagement, tipo, n_esperado, media_esperada):
    resumen = engagement_por_contenido(publicaciones_con_engagement)
    assert resumen.loc[tipo, "n_publicaciones"] == n_esperado
    assert resumen.loc[tipo, "engagement_medio"] == pytest.approx(media_esperada)


def test_columnas_e_indice(publicaciones_con_engagement):
    resumen = engagement_por_contenido(publicaciones_con_engagement)
    assert list(resumen.columns) == ["n_publicaciones", "engagement_medio"]
    assert resumen.index.name == "tipo_contenido"


def test_ordenado_de_mayor_a_menor_engagement(publicaciones_con_engagement):
    resumen = engagement_por_contenido(publicaciones_con_engagement)
    assert list(resumen.index) == ["video", "foto", "texto"]


def test_no_modifica_el_original(publicaciones_con_engagement):
    antes = publicaciones_con_engagement.copy()
    engagement_por_contenido(publicaciones_con_engagement)
    pd.testing.assert_frame_equal(publicaciones_con_engagement, antes)


def test_dataframe_vacio_devuelve_resumen_vacio():
    vacio = pd.DataFrame({"tipo_contenido": pd.Series(dtype="str"), "engagement_rate": pd.Series(dtype="float64")})
    assert engagement_por_contenido(vacio).empty
