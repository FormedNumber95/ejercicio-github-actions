"""
Tests de INTEGRACIÓN: varias piezas del pipeline funcionando JUNTAS.

Un test unitario comprueba una función aislada con datos inventados; aquí se
encadenan varias funciones (carga -> limpieza -> combinación -> métricas ->
exportación) sobre los ficheros reales de data/, y se comprueba que las
distintas implementaciones (listas de Python, NumPy y Pandas) son coherentes.
"""

import csv

import pandas as pd
import pytest
from pipeline import (
    agrupar_por_ciudad,
    ampliar_dataset,
    calcular_engagement,
    cargar_publicaciones,
    cargar_usuarios,
    crear_dashboard,
    estadisticas_columna,
    exportar_grafico,
    guardar_parquet,
    hashtags_unicos,
    limpiar_dataset,
    publicaciones_por_mes,
    resumen_por_ciudad,
    top_creadores,
    usuarios_activos,
)

pytestmark = pytest.mark.integracion


@pytest.fixture
def dataset_procesado(carpeta_datos):
    """Reproduce el flujo de los bloques 3 y 4: carga, limpieza, merge y engagement."""
    usuarios = limpiar_dataset(cargar_usuarios(carpeta_datos / "usuarios.csv"))
    publicaciones = limpiar_dataset(cargar_publicaciones(carpeta_datos / "publicaciones.xlsx"))
    combinado = publicaciones.merge(usuarios, on="id_usuario", how="left")
    return calcular_engagement(combinado)


@pytest.fixture
def filas_csv(carpeta_datos):
    """Los mismos datos leídos con el módulo csv, como en el Bloque 1 (todo texto)."""
    def leer(nombre):
        with open(carpeta_datos / nombre, encoding="utf-8") as fichero:
            return list(csv.DictReader(fichero))
    return {"usuarios": leer("usuarios.csv"), "publicaciones": leer("publicaciones.csv")}


# ── Flujo carga -> limpieza -> combinación -> métricas -> exportación ────────

def test_flujo_completo_sin_nulos_ni_filas_perdidas(dataset_procesado):
    assert len(dataset_procesado) == 300
    assert dataset_procesado.isnull().sum().sum() == 0
    assert (dataset_procesado["engagement_rate"] >= 0).all()


def test_top_creadores_sobre_datos_reales(dataset_procesado):
    top = top_creadores(dataset_procesado, n=5)
    assert len(top) == 5
    assert top["id_usuario"].is_unique
    assert top["engagement_promedio"].is_monotonic_decreasing


def test_resumen_por_ciudad_cuadra_con_el_total(dataset_procesado):
    resumen = resumen_por_ciudad(dataset_procesado)
    assert resumen["n_publicaciones"].sum() == len(dataset_procesado)
    assert resumen["n_publicaciones"].is_monotonic_decreasing


def test_publicaciones_por_mes_suma_el_total(dataset_procesado):
    por_mes = publicaciones_por_mes(dataset_procesado)
    assert por_mes["publicaciones"].sum() == len(dataset_procesado)
    assert por_mes["mes"].is_monotonic_increasing


def test_parquet_ida_y_vuelta_conserva_los_datos(dataset_procesado, tmp_path):
    ruta = tmp_path / "salida" / "dataset_procesado.parquet"
    guardar_parquet(dataset_procesado, ruta)
    pd.testing.assert_frame_equal(pd.read_parquet(ruta), dataset_procesado)


def test_dashboard_se_construye_y_exporta_a_html(dataset_procesado, tmp_path):
    figura = crear_dashboard(dataset_procesado)
    ruta_html = tmp_path / "graficos" / "dashboard.html"
    exportar_grafico(figura, ruta_html)
    contenido = ruta_html.read_text(encoding="utf-8")
    assert "Dashboard Red Social Ficticia" in contenido


def test_ampliar_y_limpiar_mantiene_la_integridad(usuarios):
    ampliado = limpiar_dataset(ampliar_dataset(usuarios, 200))
    assert len(ampliado) == len(usuarios) + 200
    assert ampliado["id_usuario"].is_unique
    assert ampliado.isnull().sum().sum() == 0


# ── Coherencia entre implementaciones (listas, NumPy y Pandas) ──────────────

def test_usuarios_activos_listas_frente_a_pandas(filas_csv, usuarios):
    assert len(usuarios_activos(filas_csv["usuarios"])) == int(usuarios["activo"].sum())


def test_agrupar_por_ciudad_listas_frente_a_pandas(filas_csv, usuarios):
    con_listas = {ciudad: len(nombres) for ciudad, nombres in agrupar_por_ciudad(filas_csv["usuarios"]).items()}
    con_pandas = usuarios["ciudad"].value_counts().to_dict()
    assert con_listas == con_pandas


def test_hashtags_unicos_listas_frente_a_pandas(filas_csv, publicaciones):
    con_pandas = set(publicaciones["hashtags"].str.split(",").explode())
    assert hashtags_unicos(filas_csv["publicaciones"]) == con_pandas


def test_estadisticas_numpy_frente_a_pandas(usuarios):
    estadisticas = estadisticas_columna(usuarios["seguidores"].to_numpy())
    assert estadisticas["media"] == pytest.approx(usuarios["seguidores"].mean())
    assert estadisticas["mediana"] == pytest.approx(usuarios["seguidores"].median())
    assert estadisticas["desv_std"] == pytest.approx(usuarios["seguidores"].std(ddof=0))
