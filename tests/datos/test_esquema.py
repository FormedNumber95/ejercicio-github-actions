"""
Tests de ESQUEMA: la ESTRUCTURA de los datos es la esperada.

Comprueban columnas, su orden y su tipo de dato, sin mirar los valores concretos.
Detectan, por ejemplo, que alguien renombre una columna, cambie el separador del
CSV o guarde un número como texto: errores que romperían el pipeline más adelante.
"""

import pandas as pd
import pytest

pytestmark = pytest.mark.esquema

ESQUEMA_USUARIOS = {
    "id_usuario": "int64",
    "nombre": "str",
    "apellidos": "str",
    "edad": "float64",          # float porque tiene nulos
    "ciudad": "str",
    "pais": "str",
    "genero": "str",
    "fecha_registro": "str",    # se lee como texto 'AAAA-MM-DD'
    "tipo_cuenta": "str",
    "seguidores": "int64",
    "seguidos": "int64",
    "publicaciones_totales": "int64",
    "activo": "bool",
    "bio": "str",
}

ESQUEMA_PUBLICACIONES = {
    "id_publicacion": "int64",
    "id_usuario": "int64",
    "fecha": "str",
    "tipo_contenido": "str",
    "likes": "float64",         # float porque tiene nulos
    "comentarios": "float64",
    "compartidos": "int64",
    "visualizaciones": "int64",
    "hashtags": "str",
}


def test_usuarios_tiene_las_columnas_en_orden(usuarios):
    assert list(usuarios.columns) == list(ESQUEMA_USUARIOS)


@pytest.mark.parametrize(("columna", "tipo"), ESQUEMA_USUARIOS.items())
def test_tipos_de_usuarios(usuarios, columna, tipo):
    assert str(usuarios[columna].dtype) == tipo


def test_publicaciones_tiene_las_columnas_en_orden(publicaciones):
    assert list(publicaciones.columns) == list(ESQUEMA_PUBLICACIONES)


@pytest.mark.parametrize(("columna", "tipo"), ESQUEMA_PUBLICACIONES.items())
def test_tipos_de_publicaciones(publicaciones, columna, tipo):
    assert str(publicaciones[columna].dtype) == tipo


def test_csv_y_excel_de_publicaciones_son_el_mismo_dataset(carpeta_datos, publicaciones):
    desde_csv = pd.read_csv(carpeta_datos / "publicaciones.csv")
    pd.testing.assert_frame_equal(desde_csv, publicaciones)


@pytest.mark.parametrize("columna_fecha", ["fecha_registro"])
def test_fechas_de_usuarios_tienen_formato_iso(usuarios, columna_fecha):
    assert usuarios[columna_fecha].str.fullmatch(r"\d{4}-\d{2}-\d{2}").all()
    pd.to_datetime(usuarios[columna_fecha], format="%Y-%m-%d")  # lanza error si alguna no es válida


def test_conexiones_es_una_lista_de_objetos_con_las_claves_esperadas(conexiones):
    assert isinstance(conexiones, list)
    for registro in conexiones:
        assert set(registro) == {"id_usuario", "siguiendo"}
        assert isinstance(registro["id_usuario"], int)
        assert isinstance(registro["siguiendo"], list)
        assert all(isinstance(i, int) for i in registro["siguiendo"])


def test_esquema_de_la_salida_del_pipeline(usuarios, publicaciones):
    """El dataset combinado que produce el pipeline añade 'engagement_rate' de tipo float."""
    from pipeline import calcular_engagement, limpiar_dataset

    combinado = publicaciones.merge(limpiar_dataset(usuarios), on="id_usuario", how="left")
    resultado = calcular_engagement(limpiar_dataset(combinado))
    esperadas = list(ESQUEMA_PUBLICACIONES) + [c for c in ESQUEMA_USUARIOS if c != "id_usuario"] + ["engagement_rate"]
    assert list(resultado.columns) == esperadas
    assert str(resultado["engagement_rate"].dtype) == "float64"
