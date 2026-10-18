"""
Tests de MÉTRICAS: indicadores calculados que deben quedar dentro de un UMBRAL.

A diferencia de los tests de valores (cada dato individual es válido), aquí se
evalúan propiedades del conjunto: porcentaje de nulos, proporciones de negocio,
anomalías tolerables y rendimiento. Los umbrales son una decisión del equipo:
si un cambio en los datos o en el código los rebasa, el pipeline debe avisar.
"""

import time

import numpy as np
import pandas as pd
import pytest
from pipeline import calcular_engagement, limpiar_dataset

pytestmark = pytest.mark.metricas

UMBRAL_NULOS_USUARIOS = 10.0       # % máximo de nulos por columna
UMBRAL_NULOS_PUBLICACIONES = 5.0
UMBRAL_ENGAGEMENT_ANOMALO = 5.0    # % máximo de publicaciones con engagement > 1


@pytest.fixture
def engagement(usuarios, publicaciones):
    combinado = limpiar_dataset(publicaciones).merge(limpiar_dataset(usuarios), on="id_usuario", how="left")
    return calcular_engagement(combinado)["engagement_rate"]


# ── Calidad de datos ─────────────────────────────────────────────────────────

def test_porcentaje_de_nulos_en_usuarios(usuarios):
    nulos = usuarios.isnull().mean() * 100
    excedidas = nulos[nulos > UMBRAL_NULOS_USUARIOS]
    assert excedidas.empty, f"Columnas con más del {UMBRAL_NULOS_USUARIOS} % de nulos: {excedidas.round(1).to_dict()}"


def test_porcentaje_de_nulos_en_publicaciones(publicaciones):
    nulos = publicaciones.isnull().mean() * 100
    assert (nulos <= UMBRAL_NULOS_PUBLICACIONES).all(), nulos.round(1).to_dict()


def test_porcentaje_de_engagement_anomalo(engagement):
    """Más interacciones que visualizaciones (> 1) indica datos imputados poco realistas."""
    porcentaje = (engagement > 1).mean() * 100
    assert porcentaje <= UMBRAL_ENGAGEMENT_ANOMALO, f"{porcentaje:.1f} % de publicaciones con engagement > 1"


# ── Métricas de negocio ──────────────────────────────────────────────────────

def test_proporcion_de_usuarios_activos(usuarios):
    assert 0.70 <= usuarios["activo"].mean() <= 0.95


def test_reparto_de_tipos_de_cuenta(usuarios):
    reparto = usuarios["tipo_cuenta"].value_counts(normalize=True)
    assert reparto["free"] >= 0.5, "La mayoría de cuentas deben ser gratuitas"
    assert reparto["creator"] <= 0.2


def test_engagement_mediano_en_rango_razonable(engagement):
    assert 0.1 <= engagement.median() <= 0.5


# ── Rendimiento ──────────────────────────────────────────────────────────────

def test_calcular_engagement_es_vectorizado_y_rapido():
    """Con 200 000 filas un cálculo vectorizado tarda milisegundos; un bucle tardaría segundos."""
    rng = np.random.default_rng(0)
    n = 200_000
    df = pd.DataFrame({
        "likes": rng.integers(0, 5_000, n),
        "comentarios": rng.integers(0, 500, n),
        "compartidos": rng.integers(0, 200, n),
        "visualizaciones": rng.integers(0, 50_000, n),
    })
    inicio = time.perf_counter()
    calcular_engagement(df)
    assert time.perf_counter() - inicio < 1.0
