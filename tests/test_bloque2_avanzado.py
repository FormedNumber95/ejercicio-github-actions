"""Tests avanzados del Bloque 2: NumPy."""

import os
import sys

import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from pipeline_avanzada import conexiones_indirectas, puntuacion_usuarios, resumen_matriz, simular_engagement


def test_puntuacion_y_normalizacion():
    puntuacion, normalizada = puntuacion_usuarios(
        np.array([100.0, 200.0]), np.array([10.0, 20.0]), np.array([5.0, 10.0])
    )
    assert puntuacion[1] > puntuacion[0]
    assert np.isclose(normalizada.min(), 0.0)
    assert np.isclose(normalizada.max(), 1.0)


def test_resumen_matriz():
    resultado = resumen_matriz(np.array([[1, 2], [10, 1]]))
    assert np.array_equal(resultado["totales_filas"], [3, 11])
    assert resultado["fila_maxima"] == 1


def test_conexiones_indirectas():
    matriz = np.array([[0, 1, 0], [0, 0, 1], [0, 0, 0]])
    assert conexiones_indirectas(matriz)[0, 2] == 1


def test_simulacion_reproducible():
    assert np.array_equal(simular_engagement(10, 42), simular_engagement(10, 42))
