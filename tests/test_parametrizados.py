"""
Tests UNITARIOS PARAMETRIZADOS (marcador ``unit``, asignado por conftest.py).

Un mismo test se ejecuta con muchos casos distintos gracias a
``@pytest.mark.parametrize``. Cada caso aparece como un test independiente en el
informe (prueba ``pytest tests/test_parametrizados.py -v``), con un identificador
legible (``ids``) que explica qué se está comprobando.
"""

import numpy as np
import pandas as pd
import pytest
from pipeline import (
    calcular_engagement,
    estandarizar_zscore,
    extraer_hashtags_regex,
    limpiar_dataset,
    normalizar_minmax,
    publicaciones_con_hashtag,
    top_por_seguidores,
)

# ── Expresiones regulares ────────────────────────────────────────────────────

@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("Hola #Mundo", ["#mundo"]),
        ("#IA y #Python", ["#ia", "#python"]),
        ("#datos_2026 con guion bajo", ["#datos_2026"]),
        ("#ia,#python sin espacios", ["#ia", "#python"]),
        ("#ia. #ia! (#ia)", ["#ia", "#ia", "#ia"]),
        ("correo@dominio.com no es un hashtag", []),
        ("", []),
    ],
    ids=["un-hashtag", "minusculas", "guion-bajo", "separados-por-coma",
         "puntuacion-y-duplicados", "sin-almohadilla", "texto-vacio"],
)
def test_extraer_hashtags_regex(texto, esperado):
    assert extraer_hashtags_regex(texto) == esperado


PUBLICACIONES = [
    {"id_publicacion": 1, "hashtags": "#ia,#python"},
    {"id_publicacion": 2, "hashtags": "#iabd,#datos"},
    {"id_publicacion": 3, "hashtags": "#IA,#bigdata"},
    {"id_publicacion": 4, "hashtags": ""},
]


@pytest.mark.parametrize(
    ("hashtag", "ids_esperados"),
    [
        ("#ia", [1, 3]),
        ("#IA", [1, 3]),
        ("#iabd", [2]),
        ("#datos", [2]),
        ("#rust", []),
    ],
    ids=["exacto", "mayusculas", "no-confunde-prefijo", "ultimo-de-la-lista", "sin-coincidencias"],
)
def test_publicaciones_con_hashtag(hashtag, ids_esperados):
    resultado = publicaciones_con_hashtag(PUBLICACIONES, hashtag)
    assert [p["id_publicacion"] for p in resultado] == ids_esperados


# ── NumPy ────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    ("valores", "esperado"),
    [
        ([10.0, 20.0, 30.0], [0.0, 0.5, 1.0]),
        ([5.0, 0.0, 10.0], [0.5, 0.0, 1.0]),
        ([-1.0, 1.0], [0.0, 1.0]),
    ],
    ids=["creciente", "desordenado", "con-negativos"],
)
def test_normalizar_minmax(valores, esperado):
    assert normalizar_minmax(np.array(valores)) == pytest.approx(esperado)


@pytest.fixture(params=[[3.0, 3.0, 3.0], [0.0], [7.5, 7.5]], ids=["tres-iguales", "un-valor", "dos-iguales"])
def array_constante(request):
    """Fixture parametrizada: cada test que la use se ejecuta una vez por array."""
    return np.array(request.param)


def test_zscore_de_array_constante_no_divide_por_cero(array_constante):
    resultado = estandarizar_zscore(array_constante)
    assert np.all(np.isfinite(resultado))
    assert resultado == pytest.approx(np.zeros(len(array_constante)))


# ── Pandas ───────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    ("likes", "comentarios", "compartidos", "visualizaciones", "esperado"),
    [
        (100, 20, 10, 500, 0.26),
        (0, 0, 0, 1000, 0.0),
        (50, 50, 0, 100, 1.0),
        pytest.param(100, 20, 10, 0, 0.0, id="sin-visualizaciones-da-cero"),
    ],
)
def test_calcular_engagement_casos(likes, comentarios, compartidos, visualizaciones, esperado):
    df = pd.DataFrame({"likes": [likes], "comentarios": [comentarios],
                       "compartidos": [compartidos], "visualizaciones": [visualizaciones]})
    assert calcular_engagement(df).loc[0, "engagement_rate"] == pytest.approx(esperado)


@pytest.mark.parametrize(
    ("columna", "valor_esperado_en_el_nulo"),
    [
        (pd.Series([1.0, None, 3.0]), 2.0),
        (pd.Series([10, None, 20, 30], dtype="float64"), 20.0),
        (pd.Series(["a", None, "b"]), "Desconocido"),
    ],
    ids=["numerica-mediana", "numerica-impar", "texto-desconocido"],
)
def test_limpiar_dataset_por_tipo_de_columna(columna, valor_esperado_en_el_nulo):
    df = pd.DataFrame({"col": columna})
    limpio = limpiar_dataset(df)
    assert limpio.loc[1, "col"] == valor_esperado_en_el_nulo
    assert df["col"].isnull().sum() == 1, "limpiar_dataset no debe modificar el original"


@pytest.mark.parametrize(("n", "longitud_esperada"), [(0, 0), (1, 1), (3, 3), (10, 5)])
def test_top_por_seguidores_respeta_n(n, longitud_esperada):
    usuarios = [{"nombre": f"U{i}", "seguidores": str(i * 100)} for i in range(5)]
    resultado = top_por_seguidores(usuarios, n=n)
    assert len(resultado) == longitud_esperada
    assert [int(u["seguidores"]) for u in resultado] == sorted((int(u["seguidores"]) for u in resultado), reverse=True)
