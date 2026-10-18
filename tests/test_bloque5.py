"""
tests/test_bloque5.py
Tests de corrección automática — Bloque 5: Visualización con Plotly y Faker

Ejecutar con:
    python -m pytest tests/test_bloque5.py -v
"""

import os
import sys

import pandas as pd
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')
sys.path.insert(0, SCRIPTS_DIR)

from pipeline import (
    ampliar_dataset,
    crear_dashboard,
    exportar_grafico,
    generar_datos_demo,
    publicaciones_por_mes,
)

# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def figura_test():
    """Figura Plotly sencilla para las pruebas."""
    try:
        import plotly.express as px
        return px.bar(x=['A', 'B', 'C'], y=[1, 2, 3], title='Test')
    except ImportError:
        pytest.skip("plotly no está instalado")


@pytest.fixture
def df_usuarios_test():
    """DataFrame pequeño con estructura idéntica a usuarios.csv."""
    return pd.DataFrame({
        'id_usuario':          [1, 2, 3, 4, 5],
        'nombre':              ['Ana', 'Borja', 'Carmen', 'David', 'Eva'],
        'apellidos':           ['García', 'López', 'Martín', 'Sanz', 'Ruiz'],
        'edad':                [28.0, 35.0, 22.0, 45.0, 30.0],
        'ciudad':              ['Madrid', 'Barcelona', 'Sevilla', 'Valencia', 'Bilbao'],
        'pais':                ['España'] * 5,
        'genero':              ['F', 'M', 'F', 'M', 'F'],
        'fecha_registro':      ['2022-01-15', '2021-06-20', '2023-03-10', '2020-11-05', '2022-08-30'],
        'tipo_cuenta':         ['creator', 'premium', 'free', 'free', 'premium'],
        'seguidores':          [5000, 1200, 300, 150, 800],
        'seguidos':            [200, 50, 120, 30, 180],
        'publicaciones_totales':[150, 80, 20, 10, 60],
        'activo':              ['True', 'True', 'False', 'True', 'True'],
        'bio':                 ['Bio 1', 'Bio 2', 'Sin bio', 'Bio 4', 'Bio 5'],
    })


# ── Tests exportar_grafico ────────────────────────────────────────────────────

class TestExportarGrafico:
    def test_crea_fichero_html(self, figura_test, tmp_path):
        ruta_html = str(tmp_path / 'test_fig.html')
        exportar_grafico(figura_test, ruta_html)
        assert os.path.exists(ruta_html)

    def test_html_no_esta_vacio(self, figura_test, tmp_path):
        ruta_html = str(tmp_path / 'test_fig.html')
        exportar_grafico(figura_test, ruta_html)
        assert os.path.getsize(ruta_html) > 0

    def test_html_contiene_plotly(self, figura_test, tmp_path):
        ruta_html = str(tmp_path / 'test_fig.html')
        exportar_grafico(figura_test, ruta_html)
        with open(ruta_html, encoding='utf-8') as f:
            contenido = f.read()
        assert 'plotly' in contenido.lower()

    def test_crea_directorios_html(self, figura_test, tmp_path):
        ruta_html = str(tmp_path / 'sub' / 'deep' / 'fig.html')
        exportar_grafico(figura_test, ruta_html)
        assert os.path.exists(ruta_html)

    def test_png_opcional_si_kaleido(self, figura_test, tmp_path):
        """Si kaleido está instalado, también se crea el PNG."""
        try:
            import kaleido  # noqa: F401
            ruta_html = str(tmp_path / 'fig.html')
            ruta_png  = str(tmp_path / 'fig.png')
            exportar_grafico(figura_test, ruta_html, ruta_png=ruta_png)
            assert os.path.exists(ruta_png)
        except ImportError:
            pytest.skip("kaleido no instalado — PNG no disponible")

    def test_devuelve_none(self, figura_test, tmp_path):
        ruta_html = str(tmp_path / 'test_none.html')
        resultado = exportar_grafico(figura_test, ruta_html)
        assert resultado is None


# ── Tests ampliar_dataset ─────────────────────────────────────────────────────

class TestAmpliarDataset:
    def test_devuelve_dataframe(self, df_usuarios_test):
        resultado = ampliar_dataset(df_usuarios_test, n_nuevos=10)
        assert isinstance(resultado, pd.DataFrame)

    def test_longitud_correcta(self, df_usuarios_test):
        n = 50
        resultado = ampliar_dataset(df_usuarios_test, n_nuevos=n)
        assert len(resultado) == len(df_usuarios_test) + n

    def test_columnas_identicas(self, df_usuarios_test):
        resultado = ampliar_dataset(df_usuarios_test, n_nuevos=10)
        assert list(resultado.columns) == list(df_usuarios_test.columns)

    def test_ids_unicos(self, df_usuarios_test):
        resultado = ampliar_dataset(df_usuarios_test, n_nuevos=10)
        assert resultado['id_usuario'].nunique() == len(resultado)

    def test_nuevos_ids_continuan_desde_max(self, df_usuarios_test):
        resultado = ampliar_dataset(df_usuarios_test, n_nuevos=10)
        id_max_original = df_usuarios_test['id_usuario'].max()
        ids_nuevos = resultado[len(df_usuarios_test):]['id_usuario']
        assert ids_nuevos.min() == id_max_original + 1

    def test_originales_se_conservan(self, df_usuarios_test):
        resultado = ampliar_dataset(df_usuarios_test, n_nuevos=10)
        primeros = resultado.head(len(df_usuarios_test))
        pd.testing.assert_frame_equal(
            primeros.reset_index(drop=True),
            df_usuarios_test.reset_index(drop=True),
        )

    def test_n_cero_devuelve_original(self, df_usuarios_test):
        resultado = ampliar_dataset(df_usuarios_test, n_nuevos=0)
        assert len(resultado) == len(df_usuarios_test)

    def test_sin_todas_las_columnas_nulas(self, df_usuarios_test):
        resultado = ampliar_dataset(df_usuarios_test, n_nuevos=20)
        nuevos = resultado.iloc[len(df_usuarios_test):]
        # Las columnas obligatorias (nombre, ciudad, tipo_cuenta) no deben tener todos nulos
        for col in ['nombre', 'ciudad', 'tipo_cuenta']:
            assert nuevos[col].isnull().sum() < len(nuevos), f"'{col}' tiene demasiados nulos"


# ── Datos de prueba para las nuevas funciones ───────────────────────────────

@pytest.fixture
def df_publicaciones_test():
    """Publicaciones con sus autores (formato de dataset_procesado)."""
    return pd.DataFrame({
        'id_publicacion': [1, 2, 3, 4, 5, 6],
        'fecha':          ['2023-02-10', '2023-01-05', '2023-01-20', '2023-03-01', '2023-02-15', '2023-01-25'],
        'ciudad':         ['Madrid', 'Madrid', 'Bilbao', 'Sevilla', 'Madrid', 'Bilbao'],
        'tipo_cuenta':    ['free', 'free', 'premium', 'creator', 'free', 'premium'],
        'likes':          [10.0, 20.0, 30.0, 40.0, 50.0, 60.0],
    })


# ── Tests publicaciones_por_mes ───────────────────────────────────────────────

class TestPublicacionesPorMes:
    def test_devuelve_dataframe_con_columnas(self, df_publicaciones_test):
        resultado = publicaciones_por_mes(df_publicaciones_test)
        assert isinstance(resultado, pd.DataFrame)
        assert list(resultado.columns) == ['mes', 'publicaciones']

    def test_meses_en_formato_aaaa_mm_y_orden_cronologico(self, df_publicaciones_test):
        resultado = publicaciones_por_mes(df_publicaciones_test)
        assert resultado['mes'].tolist() == ['2023-01', '2023-02', '2023-03']

    def test_recuento_por_mes(self, df_publicaciones_test):
        resultado = publicaciones_por_mes(df_publicaciones_test)
        assert resultado['publicaciones'].tolist() == [3, 2, 1]

    def test_indice_numerico(self, df_publicaciones_test):
        resultado = publicaciones_por_mes(df_publicaciones_test)
        assert list(resultado.index) == [0, 1, 2]

    def test_acepta_fechas_de_tipo_fecha(self, df_publicaciones_test):
        df = df_publicaciones_test.copy()
        df['fecha'] = pd.to_datetime(df['fecha'])
        resultado = publicaciones_por_mes(df)
        assert resultado['publicaciones'].tolist() == [3, 2, 1]

    def test_no_modifica_el_original(self, df_publicaciones_test):
        antes = df_publicaciones_test.copy()
        publicaciones_por_mes(df_publicaciones_test)
        pd.testing.assert_frame_equal(df_publicaciones_test, antes)


# ── Tests crear_dashboard ─────────────────────────────────────────────────────

@pytest.fixture
def dashboard_test(df_publicaciones_test):
    try:
        return crear_dashboard(df_publicaciones_test)
    except ImportError:
        pytest.skip("plotly no está instalado o está incompleto")


class TestCrearDashboard:
    def test_tiene_cuatro_graficos_del_tipo_esperado(self, dashboard_test):
        assert [traza.type for traza in dashboard_test.data] == ['bar', 'pie', 'scatter', 'histogram']

    def test_barras_ordenadas_de_mayor_a_menor(self, dashboard_test):
        barras = dashboard_test.data[0]
        assert list(barras.x) == ['Madrid', 'Bilbao', 'Sevilla']
        assert list(barras.y) == [3, 2, 1]

    def test_lineas_con_las_publicaciones_por_mes(self, dashboard_test):
        lineas = dashboard_test.data[2]
        assert list(lineas.x) == ['2023-01', '2023-02', '2023-03']
        assert list(lineas.y) == [3, 2, 1]

    def test_formato_de_la_figura(self, dashboard_test):
        assert dashboard_test.layout.height == 800
        assert dashboard_test.layout.showlegend is False
        assert dashboard_test.layout.title.text == 'Dashboard Red Social Ficticia'

    def test_maximo_8_ciudades_en_las_barras(self):
        df = pd.DataFrame({
            'fecha': ['2023-01-01'] * 10,
            'ciudad': [f'Ciudad{i}' for i in range(10)],
            'tipo_cuenta': ['free'] * 10,
            'likes': [1.0] * 10,
        })
        try:
            fig = crear_dashboard(df)
        except ImportError:
            pytest.skip("plotly no está instalado o está incompleto")
        assert len(fig.data[0].x) == 8

    def test_no_modifica_el_original(self, df_publicaciones_test):
        antes = df_publicaciones_test.copy()
        try:
            crear_dashboard(df_publicaciones_test)
        except ImportError:
            pytest.skip("plotly no está instalado o está incompleto")
        pd.testing.assert_frame_equal(df_publicaciones_test, antes)


# ── Tests generar_datos_demo ──────────────────────────────────────────────────

COLUMNAS_DEMO = ['nombre', 'apellidos', 'email', 'ciudad', 'telefono', 'fecha_registro']


class TestGenerarDatosDemo:
    def test_devuelve_dataframe_con_columnas(self):
        resultado = generar_datos_demo(10)
        assert isinstance(resultado, pd.DataFrame)
        assert list(resultado.columns) == COLUMNAS_DEMO

    def test_numero_de_filas(self):
        assert len(generar_datos_demo(7)) == 7

    def test_es_reproducible_con_la_misma_semilla(self):
        pd.testing.assert_frame_equal(generar_datos_demo(10, seed=2024), generar_datos_demo(10, seed=2024))

    def test_semillas_distintas_dan_datos_distintos(self):
        assert not generar_datos_demo(10, seed=1).equals(generar_datos_demo(10, seed=2))

    def test_sin_valores_nulos(self):
        assert generar_datos_demo(20).isnull().sum().sum() == 0

    def test_fechas_en_el_periodo_y_formato_iso(self):
        fechas = generar_datos_demo(50)['fecha_registro']
        assert fechas.str.fullmatch(r'\d{4}-\d{2}-\d{2}').all()
        assert fechas.between('2018-01-01', '2024-06-01').all()

    def test_apellidos_son_dos(self):
        apellidos = generar_datos_demo(20)['apellidos']
        assert (apellidos.str.split().str.len() >= 2).all()

    def test_n_cero_devuelve_tabla_vacia_con_columnas(self):
        resultado = generar_datos_demo(0)
        assert len(resultado) == 0
        assert list(resultado.columns) == COLUMNAS_DEMO
