"""
Tests de CONTRATOS DE DATOS (pandera).

Un contrato no solo debe aceptar los datos correctos: sobre todo debe RECHAZAR
los incorrectos. Por eso, además de validar los datos reales, cada test
"rompe" una copia de los datos de una forma concreta y comprueba que el
contrato lo detecta y señala la columna culpable.
"""

import json
import shutil

import pandas as pd
import pytest
from contratos import (
    CONTRATO_DATASET_PROCESADO,
    CONTRATO_PUBLICACIONES,
    CONTRATO_USUARIOS,
    ErrorDeContrato,
    comprobar_integridad,
    construir_dataset_validado,
)
from pandera.errors import SchemaError, SchemaErrors

pytestmark = pytest.mark.contratos


# ── Los datos reales cumplen los contratos ──────────────────────────────────

def test_usuarios_cumplen_su_contrato(usuarios):
    CONTRATO_USUARIOS.validate(usuarios, lazy=True)


def test_publicaciones_cumplen_su_contrato(publicaciones):
    CONTRATO_PUBLICACIONES.validate(publicaciones, lazy=True)


def test_las_tablas_son_coherentes_entre_si(usuarios, publicaciones, conexiones):
    comprobar_integridad(usuarios, publicaciones, conexiones)


def test_el_pipeline_validado_entrega_un_dataset_que_cumple_el_contrato(carpeta_datos):
    dataset = construir_dataset_validado(carpeta_datos)
    assert len(dataset) == 300
    CONTRATO_DATASET_PROCESADO.validate(dataset)


# ── Los contratos rechazan datos incorrectos ────────────────────────────────

def _romper_usuarios(df, defecto):
    if defecto == "edad fuera de rango":
        df.loc[0, "edad"] = 150.0
    elif defecto == "categoría desconocida":
        df.loc[0, "tipo_cuenta"] = "gold"
    elif defecto == "id repetido":
        df.loc[1, "id_usuario"] = df.loc[0, "id_usuario"]
    elif defecto == "seguidores negativos":
        df.loc[0, "seguidores"] = -5
    elif defecto == "fecha mal formada":
        df.loc[0, "fecha_registro"] = "14/05/2022"
    elif defecto == "tipo incorrecto":
        df["seguidores"] = df["seguidores"].astype(str)
    elif defecto == "columna eliminada":
        df = df.drop(columns="pais")
    elif defecto == "columna inesperada":
        df["telefono"] = "600000000"
    elif defecto == "creator con pocos seguidores":
        df.loc[0, ["tipo_cuenta", "seguidores"]] = ["creator", 500]
    return df


@pytest.mark.parametrize(
    ("defecto", "texto_esperado"),
    [
        ("edad fuera de rango", "edad"),
        ("categoría desconocida", "tipo_cuenta"),
        ("id repetido", "id_usuario"),
        ("seguidores negativos", "seguidores"),
        ("fecha mal formada", "fecha_registro"),
        ("tipo incorrecto", "seguidores"),
        ("columna eliminada", "pais"),
        ("columna inesperada", "telefono"),
        ("creator con pocos seguidores", "creator"),
    ],
)
def test_contrato_de_usuarios_rechaza(usuarios, defecto, texto_esperado):
    roto = _romper_usuarios(usuarios, defecto)
    with pytest.raises((SchemaError, SchemaErrors)) as error:
        CONTRATO_USUARIOS.validate(roto, lazy=True)
    assert texto_esperado in str(error.value)


@pytest.mark.parametrize(
    ("columna", "valor", "texto_esperado"),
    [
        ("likes", -1.0, "likes"),
        ("hashtags", "ia, python", "hashtags"),
        ("tipo_contenido", "podcast", "tipo_contenido"),
        ("visualizaciones", 0, "visualizaciones no pueden ser menores"),
    ],
)
def test_contrato_de_publicaciones_rechaza(publicaciones, columna, valor, texto_esperado):
    fila = publicaciones["likes"].first_valid_index()
    publicaciones.loc[fila, columna] = valor
    with pytest.raises((SchemaError, SchemaErrors)) as error:
        CONTRATO_PUBLICACIONES.validate(publicaciones, lazy=True)
    assert texto_esperado in str(error.value)


def test_validacion_lazy_informa_de_todos_los_errores_a_la_vez(usuarios):
    usuarios.loc[0, "edad"] = 150.0
    usuarios.loc[1, "tipo_cuenta"] = "gold"
    usuarios.loc[2, "genero"] = "X"
    with pytest.raises(SchemaErrors) as error:
        CONTRATO_USUARIOS.validate(usuarios, lazy=True)
    columnas = set(error.value.failure_cases["column"])
    assert {"edad", "tipo_cuenta", "genero"} <= columnas


def test_contrato_de_salida_rechaza_nulos():
    dataset = pd.DataFrame({
        "id_publicacion": [1, 2], "id_usuario": [1, 2], "tipo_contenido": ["foto", "video"],
        "tipo_cuenta": ["free", "free"], "likes": [10.0, None], "comentarios": [1.0, 2.0],
        "visualizaciones": [100, 200], "seguidores": [50, 60], "engagement_rate": [0.1, 0.2],
    })
    with pytest.raises((SchemaError, SchemaErrors), match="likes"):
        CONTRATO_DATASET_PROCESADO.validate(dataset, lazy=True)


def _publicacion_huerfana(publicaciones, conexiones):
    publicaciones.loc[0, "id_usuario"] = 999


def _sigue_a_inexistente(publicaciones, conexiones):
    conexiones[0]["siguiendo"].append(999)


def _autoseguimiento(publicaciones, conexiones):
    conexiones[0]["siguiendo"].append(conexiones[0]["id_usuario"])


@pytest.mark.parametrize(
    ("romper", "texto_esperado"),
    [
        (_publicacion_huerfana, "publicaciones de usuarios inexistentes"),
        (_sigue_a_inexistente, "se sigue a usuarios inexistentes"),
        (_autoseguimiento, "sí mismos"),
    ],
    ids=["publicacion-huerfana", "sigue-a-inexistente", "autoseguimiento"],
)
def test_integridad_entre_tablas_rechaza(usuarios, publicaciones, conexiones, romper, texto_esperado):
    romper(publicaciones, conexiones)
    with pytest.raises(ErrorDeContrato, match=texto_esperado):
        comprobar_integridad(usuarios, publicaciones, conexiones)


def test_el_pipeline_se_detiene_si_los_datos_de_entrada_no_cumplen(carpeta_datos, tmp_path):
    """Con un usuario corrupto, el pipeline no llega a procesar nada."""
    for nombre in ["usuarios.csv", "publicaciones.xlsx", "conexiones.json"]:
        shutil.copy(carpeta_datos / nombre, tmp_path / nombre)
    usuarios = pd.read_csv(tmp_path / "usuarios.csv")
    usuarios.loc[0, "edad"] = 150.0
    usuarios.to_csv(tmp_path / "usuarios.csv", index=False)

    with pytest.raises(SchemaErrors, match="edad"):
        construir_dataset_validado(tmp_path)


def test_el_pipeline_se_detiene_si_las_tablas_no_encajan(carpeta_datos, tmp_path):
    for nombre in ["usuarios.csv", "publicaciones.xlsx"]:
        shutil.copy(carpeta_datos / nombre, tmp_path / nombre)
    conexiones = json.loads((carpeta_datos / "conexiones.json").read_text(encoding="utf-8"))
    conexiones[0]["siguiendo"].append(conexiones[0]["id_usuario"])
    (tmp_path / "conexiones.json").write_text(json.dumps(conexiones), encoding="utf-8")

    with pytest.raises(ErrorDeContrato, match="sí mismos"):
        construir_dataset_validado(tmp_path)
