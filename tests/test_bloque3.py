"""
tests/test_bloque3.py
Tests de corrección automática — Bloque 3: Pandas básico

Ejecutar con:
    python -m pytest tests/test_bloque3.py -v
"""

import os
import sys

import pandas as pd
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')
sys.path.insert(0, SCRIPTS_DIR)

from pipeline import (
    cargar_publicaciones,
    cargar_usuarios,
    limpiar_dataset,
)

# ── Fixtures y Rutas ─────────────────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
RUTA_CSV  = os.path.join(DATA_DIR, 'usuarios.csv')
RUTA_XLSX = os.path.join(DATA_DIR, 'publicaciones.xlsx')


# ── Tests cargar_usuarios ─────────────────────────────────────────────────────

@pytest.mark.skipif(not os.path.exists(RUTA_CSV), reason="usuarios.csv no encontrado")
class TestCargarUsuarios:
    def test_devuelve_dataframe(self):
        df = cargar_usuarios(RUTA_CSV)
        assert isinstance(df, pd.DataFrame)

    def test_tiene_columnas_basicas(self):
        df = cargar_usuarios(RUTA_CSV)
        columnas_esperadas = {'id_usuario', 'nombre', 'seguidores', 'tipo_cuenta'}
        assert columnas_esperadas.issubset(set(df.columns))

    def test_no_esta_vacio(self):
        df = cargar_usuarios(RUTA_CSV)
        assert len(df) > 0

    def test_tiene_100_filas(self):
        df = cargar_usuarios(RUTA_CSV)
        assert len(df) == 100


# ── Tests cargar_publicaciones ────────────────────────────────────────────────

@pytest.mark.skipif(not os.path.exists(RUTA_XLSX), reason="publicaciones.xlsx no encontrado")
class TestCargarPublicaciones:
    def test_devuelve_dataframe(self):
        df = cargar_publicaciones(RUTA_XLSX)
        assert isinstance(df, pd.DataFrame)

    def test_tiene_columnas_basicas(self):
        df = cargar_publicaciones(RUTA_XLSX)
        columnas_esperadas = {'id_publicacion', 'id_usuario', 'likes', 'tipo_contenido'}
        assert columnas_esperadas.issubset(set(df.columns))

    def test_tiene_300_filas(self):
        df = cargar_publicaciones(RUTA_XLSX)
        assert len(df) == 300


# ── Tests limpiar_dataset ─────────────────────────────────────────────────────

class TestLimpiarDataset:
    @pytest.fixture
    def df_con_nulos(self):
        return pd.DataFrame({
            'id':      [1,    2,    3,    4],
            'nombre':  ['Ana', None, 'Carmen', None],
            'edad':    [25.0, None, 30.0, None],
            'ciudad':  ['Madrid', None, None, 'Sevilla'],
        })

    def test_devuelve_dataframe(self, df_con_nulos):
        resultado = limpiar_dataset(df_con_nulos)
        assert isinstance(resultado, pd.DataFrame)

    def test_sin_nulos_en_numericas(self, df_con_nulos):
        resultado = limpiar_dataset(df_con_nulos)
        assert resultado['edad'].isnull().sum() == 0

    def test_sin_nulos_en_texto(self, df_con_nulos):
        resultado = limpiar_dataset(df_con_nulos)
        assert resultado['nombre'].isnull().sum() == 0
        assert resultado['ciudad'].isnull().sum() == 0

    def test_numerica_rellena_con_mediana(self, df_con_nulos):
        resultado = limpiar_dataset(df_con_nulos)
        # Mediana de [25.0, 30.0] = 27.5
        nulos_rellenados = resultado[df_con_nulos['edad'].isnull()]['edad']
        for val in nulos_rellenados:
            assert abs(val - 27.5) < 0.01

    def test_texto_rellena_con_desconocido(self, df_con_nulos):
        resultado = limpiar_dataset(df_con_nulos)
        nulos_nombre = resultado[df_con_nulos['nombre'].isnull()]['nombre']
        for val in nulos_nombre:
            assert val == 'Desconocido'

    def test_no_modifica_original(self, df_con_nulos):
        nulos_antes = df_con_nulos['edad'].isnull().sum()
        limpiar_dataset(df_con_nulos)
        assert df_con_nulos['edad'].isnull().sum() == nulos_antes

    def test_df_sin_nulos_no_cambia_valores(self):
        df = pd.DataFrame({'a': [1.0, 2.0, 3.0], 'b': ['x', 'y', 'z']})
        resultado = limpiar_dataset(df)
        pd.testing.assert_frame_equal(resultado, df)

    def test_devuelve_una_copia(self, df_con_nulos):
        resultado = limpiar_dataset(df_con_nulos)
        assert resultado is not df_con_nulos

    def test_conserva_filas_y_columnas(self, df_con_nulos):
        resultado = limpiar_dataset(df_con_nulos)
        assert resultado.shape == df_con_nulos.shape
        assert list(resultado.columns) == list(df_con_nulos.columns)

    def test_columnas_booleanas_no_se_tocan(self):
        df = pd.DataFrame({'activo': [True, False, True], 'edad': [20.0, None, 40.0]})
        resultado = limpiar_dataset(df)
        assert resultado['activo'].tolist() == [True, False, True]
        assert resultado['edad'].tolist() == [20.0, 30.0, 40.0]


# ── Tests con los datos reales del proyecto ──────────────────────────────────

@pytest.mark.skipif(
    not (os.path.exists(RUTA_CSV) and os.path.exists(RUTA_XLSX)),
    reason="ficheros de datos no encontrados",
)
class TestLimpiarDatosReales:
    def test_usuarios_reales_quedan_sin_nulos(self):
        df = cargar_usuarios(RUTA_CSV)
        assert df.isnull().sum().sum() > 0
        assert limpiar_dataset(df).isnull().sum().sum() == 0

    def test_publicaciones_reales_quedan_sin_nulos(self):
        df = cargar_publicaciones(RUTA_XLSX)
        assert df.isnull().sum().sum() > 0
        assert limpiar_dataset(df).isnull().sum().sum() == 0

    def test_limpiar_no_altera_los_datos_cargados(self):
        df = cargar_usuarios(RUTA_CSV)
        antes = df.isnull().sum().sum()
        limpiar_dataset(df)
        assert df.isnull().sum().sum() == antes
