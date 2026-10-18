"""
tests/test_bloque4.py
Tests de corrección automática — Bloque 4: Pandas avanzado

Ejecutar con:
    python -m pytest tests/test_bloque4.py -v
"""

import os
import sys

import pandas as pd
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')
sys.path.insert(0, SCRIPTS_DIR)

from pipeline import (
    calcular_engagement,
    guardar_parquet,
    resumen_por_ciudad,
    top_creadores,
)

# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def df_merged_test():
    """DataFrame combinado de prueba con datos controlados."""
    return pd.DataFrame({
        'id_publicacion': [1,   2,   3,   4,   5,   6],
        'id_usuario':     [1,   1,   2,   2,   3,   3],
        'nombre':         ['Ana', 'Ana', 'Borja', 'Borja', 'Carmen', 'Carmen'],
        'tipo_cuenta':    ['creator', 'creator', 'premium', 'premium', 'free', 'free'],
        'ciudad':         ['Madrid', 'Madrid', 'Barcelona', 'Barcelona', 'Madrid', 'Madrid'],
        'seguidores':     [5000, 5000, 1200, 1200, 800, 800],
        'likes':          [100.0, 200.0, 30.0,  80.0,  10.0, 20.0],
        'comentarios':    [20.0,  30.0,  10.0,  15.0,  2.0,  5.0],
        'compartidos':    [10,    20,    5,     8,     1,    2],
        'visualizaciones':[500,   800,   200,   400,   100,  200],
    })


@pytest.fixture
def df_merged_cero_vis(df_merged_test):
    """DataFrame con una fila con visualizaciones = 0."""
    df = df_merged_test.copy()
    df.loc[0, 'visualizaciones'] = 0
    return df


# ── Tests calcular_engagement ─────────────────────────────────────────────────

class TestCalcularEngagement:
    def test_devuelve_dataframe(self, df_merged_test):
        resultado = calcular_engagement(df_merged_test)
        assert isinstance(resultado, pd.DataFrame)

    def test_tiene_columna_engagement_rate(self, df_merged_test):
        resultado = calcular_engagement(df_merged_test)
        assert 'engagement_rate' in resultado.columns

    def test_formula_correcta(self, df_merged_test):
        resultado = calcular_engagement(df_merged_test)
        # Fila 0: (100+20+10)/500 = 0.26
        er = resultado.loc[0, 'engagement_rate']
        assert abs(er - 0.26) < 0.001

    def test_sin_valores_nulos(self, df_merged_test):
        resultado = calcular_engagement(df_merged_test)
        assert resultado['engagement_rate'].isnull().sum() == 0

    def test_visualizaciones_cero_da_cero(self, df_merged_cero_vis):
        resultado = calcular_engagement(df_merged_cero_vis)
        er_cero = resultado.loc[0, 'engagement_rate']
        assert er_cero == 0.0

    def test_todos_positivos(self, df_merged_test):
        resultado = calcular_engagement(df_merged_test)
        assert (resultado['engagement_rate'] >= 0).all()


# ── Tests top_creadores ───────────────────────────────────────────────────────

class TestTopCreadores:
    def test_devuelve_dataframe(self, df_merged_test):
        df_e = calcular_engagement(df_merged_test)
        resultado = top_creadores(df_e, n=2)
        assert isinstance(resultado, pd.DataFrame)

    def test_longitud_correcta(self, df_merged_test):
        df_e = calcular_engagement(df_merged_test)
        resultado = top_creadores(df_e, n=2)
        assert len(resultado) == 2

    def test_ordenado_de_mayor_a_menor(self, df_merged_test):
        df_e = calcular_engagement(df_merged_test)
        resultado = top_creadores(df_e, n=3)
        if 'engagement_promedio' in resultado.columns:
            valores = resultado['engagement_promedio'].values
        else:
            valores = resultado.iloc[:, -1].values
        assert list(valores) == sorted(valores, reverse=True)

    def test_primer_usuario_tiene_mayor_engagement(self, df_merged_test):
        df_e = calcular_engagement(df_merged_test)
        resultado = top_creadores(df_e, n=3)
        # Ana: (0.26 + 0.3125)/2 ≈ 0.286 — debe ser la primera
        assert resultado.iloc[0]['nombre'] == 'Ana'

    def test_n_mayor_que_usuarios(self, df_merged_test):
        df_e = calcular_engagement(df_merged_test)
        resultado = top_creadores(df_e, n=100)
        # Hay 3 usuarios únicos
        assert len(resultado) == 3

    def test_tiene_columna_nombre(self, df_merged_test):
        df_e = calcular_engagement(df_merged_test)
        resultado = top_creadores(df_e, n=2)
        assert 'nombre' in resultado.columns


# ── Tests resumen_por_ciudad ──────────────────────────────────────────────────

class TestResumenPorCiudad:
    def test_devuelve_dataframe(self, df_merged_test):
        df_e = calcular_engagement(df_merged_test)
        resultado = resumen_por_ciudad(df_e)
        assert isinstance(resultado, pd.DataFrame)

    def test_tiene_ciudades_correctas(self, df_merged_test):
        df_e = calcular_engagement(df_merged_test)
        resultado = resumen_por_ciudad(df_e)
        assert 'Madrid' in resultado.index or 'Madrid' in resultado.values
        assert 'Barcelona' in resultado.index or 'Barcelona' in resultado.values

    def test_tiene_columnas_requeridas(self, df_merged_test):
        df_e = calcular_engagement(df_merged_test)
        resultado = resumen_por_ciudad(df_e)
        # Debe tener al menos 3 columnas
        assert len(resultado.columns) >= 3

    def test_contiene_media_seguidores(self, df_merged_test):
        df_e = calcular_engagement(df_merged_test)
        resultado = resumen_por_ciudad(df_e)
        nombre_cols = ' '.join(resultado.columns.str.lower())
        assert 'seguidores' in nombre_cols


# ── Tests guardar_parquet ─────────────────────────────────────────────────────

class TestGuardarParquet:
    def test_crea_fichero(self, df_merged_test, tmp_path):
        ruta = str(tmp_path / 'test_output.parquet')
        guardar_parquet(df_merged_test, ruta)
        assert os.path.exists(ruta)

    def test_datos_recuperados_correctamente(self, df_merged_test, tmp_path):
        ruta = str(tmp_path / 'test_output.parquet')
        guardar_parquet(df_merged_test, ruta)
        df_leido = pd.read_parquet(ruta)
        assert df_leido.shape == df_merged_test.shape

    def test_columnas_se_conservan(self, df_merged_test, tmp_path):
        ruta = str(tmp_path / 'test_output.parquet')
        guardar_parquet(df_merged_test, ruta)
        df_leido = pd.read_parquet(ruta)
        assert list(df_leido.columns) == list(df_merged_test.columns)

    def test_crea_directorios_intermedios(self, df_merged_test, tmp_path):
        ruta = str(tmp_path / 'subcarpeta' / 'otra' / 'test_output.parquet')
        guardar_parquet(df_merged_test, ruta)
        assert os.path.exists(ruta)

    def test_devuelve_none(self, df_merged_test, tmp_path):
        ruta = str(tmp_path / 'test_output.parquet')
        resultado = guardar_parquet(df_merged_test, ruta)
        assert resultado is None
