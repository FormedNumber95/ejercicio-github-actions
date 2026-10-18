"""
tests/test_bloque2.py
Tests de corrección automática — Bloque 2: NumPy

Ejecutar con:
    python -m pytest tests/test_bloque2.py -v
"""

import os
import sys

import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')
sys.path.insert(0, SCRIPTS_DIR)

from pipeline import (
    contar_hashtags_array,
    estadisticas_columna,
    estandarizar_zscore,
    normalizar_minmax,
    resumen_publicaciones,
)

# ── Fixtures ─────────────────────────────────────────────────────────────────

ARR_CONOCIDO = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
# media=30, mediana=30, desv_std≈14.14, min=10, max=50


# ── Tests estadisticas_columna ────────────────────────────────────────────────

class TestEstadisticasColumna:
    def test_devuelve_dict(self):
        resultado = estadisticas_columna(ARR_CONOCIDO)
        assert isinstance(resultado, dict)

    def test_claves_correctas(self):
        resultado = estadisticas_columna(ARR_CONOCIDO)
        claves_esperadas = {'media', 'mediana', 'desv_std', 'minimo', 'maximo'}
        assert claves_esperadas.issubset(set(resultado.keys()))

    def test_media_correcta(self):
        resultado = estadisticas_columna(ARR_CONOCIDO)
        assert abs(resultado['media'] - 30.0) < 0.01

    def test_mediana_correcta(self):
        resultado = estadisticas_columna(ARR_CONOCIDO)
        assert abs(resultado['mediana'] - 30.0) < 0.01

    def test_minimo_correcto(self):
        resultado = estadisticas_columna(ARR_CONOCIDO)
        assert abs(resultado['minimo'] - 10.0) < 0.01

    def test_maximo_correcto(self):
        resultado = estadisticas_columna(ARR_CONOCIDO)
        assert abs(resultado['maximo'] - 50.0) < 0.01

    def test_desv_std_correcta(self):
        resultado = estadisticas_columna(ARR_CONOCIDO)
        assert abs(resultado['desv_std'] - np.std(ARR_CONOCIDO)) < 0.01

    def test_valores_son_float(self):
        resultado = estadisticas_columna(ARR_CONOCIDO)
        for k in ['media', 'mediana', 'desv_std', 'minimo', 'maximo']:
            assert isinstance(resultado[k], float), f"'{k}' debe ser float"

    def test_array_un_elemento(self):
        resultado = estadisticas_columna(np.array([42.0]))
        assert resultado['media'] == 42.0
        assert resultado['minimo'] == 42.0
        assert resultado['maximo'] == 42.0


# ── Tests resumen_publicaciones ─────────────────────────────────────────────

MATRIZ_PUBLICACIONES = np.array([
    [5, 2, 8],
    [1, 9, 0],
])
# total_por_usuario = [15, 10]; total_por_tipo = [6, 11, 8]


class TestResumenPublicaciones:
    def test_devuelve_dict_con_claves(self):
        resultado = resumen_publicaciones(MATRIZ_PUBLICACIONES)
        claves_esperadas = {'total_por_usuario', 'total_por_tipo', 'usuario_mas_publicaciones'}
        assert claves_esperadas.issubset(set(resultado.keys()))

    def test_total_por_usuario(self):
        resultado = resumen_publicaciones(MATRIZ_PUBLICACIONES)
        assert list(resultado['total_por_usuario']) == [15, 10]

    def test_total_por_tipo(self):
        resultado = resumen_publicaciones(MATRIZ_PUBLICACIONES)
        assert list(resultado['total_por_tipo']) == [6, 11, 8]

    def test_usuario_mas_publicaciones(self):
        resultado = resumen_publicaciones(MATRIZ_PUBLICACIONES)
        assert resultado['usuario_mas_publicaciones'] == 0


# ── Tests contar_hashtags_array ─────────────────────────────────────────────

class TestContarHashtagsArray:
    def test_cuenta_hashtags_por_texto(self):
        textos = np.array(['Hola #mundo #ia', 'Sin hashtags', '#solo1'])
        resultado = list(contar_hashtags_array(textos))
        assert resultado == [2, 0, 1]


# ── Tests normalizar_minmax ─────────────────────────────────────────────────

class TestNormalizarMinmax:
    def test_normaliza_entre_0_y_1(self):
        resultado = normalizar_minmax(np.array([10.0, 20.0, 30.0]))
        assert np.allclose(resultado, [0.0, 0.5, 1.0])


# ── Tests estandarizar_zscore ────────────────────────────────────────────────

class TestEstandarizarZscore:
    def test_media_cero_tras_estandarizar(self):
        resultado = estandarizar_zscore(np.array([10.0, 20.0, 30.0]))
        assert abs(np.mean(resultado)) < 1e-9

    def test_sin_division_por_cero(self):
        resultado = estandarizar_zscore(np.array([5.0, 5.0, 5.0]))
        assert np.all(np.isfinite(resultado))
