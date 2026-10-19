"""
contratos.py
Contratos de datos del proyecto Red Social Ficticia (con pandera).

Un CONTRATO declara, en un único sitio, qué estructura y qué valores debe
cumplir un conjunto de datos: columnas, tipos, rangos, categorías permitidas,
claves únicas y reglas entre columnas. Se comprueba en la FRONTERA de cada
etapa del pipeline: al entrar los datos y al salir el resultado. Si no se
cumple, el pipeline se detiene con un error que explica qué ha fallado, en
lugar de producir resultados incorrectos en silencio.

    from contratos import CONTRATO_USUARIOS
    CONTRATO_USUARIOS.validate(df_usuarios, lazy=True)   # lazy: informa de TODOS los errores
"""

import json
from pathlib import Path

import pipeline as pl
from pandera.pandas import Check, Column, DataFrameSchema

TIPOS_CUENTA = ["free", "premium", "creator"]
GENEROS = ["M", "F", "NB"]
PAISES = ["Espana", "Mexico", "Argentina", "Colombia"]
TIPOS_CONTENIDO = ["foto", "video", "texto", "historia", "reel"]
FORMATO_FECHA = r"^\d{4}-\d{2}-\d{2}$"
FORMATO_HASHTAGS = r"^#\w+(,#\w+)*$"


class ErrorDeContrato(ValueError):
    """Los datos no cumplen un contrato que pandera no puede expresar (p. ej. entre tablas)."""


# ── Contratos de entrada ─────────────────────────────────────────────────────

CONTRATO_USUARIOS = DataFrameSchema(
    {
        "id_usuario": Column(int, Check.ge(1), unique=True),
        "nombre": Column(str),
        "apellidos": Column(str),
        "edad": Column(float, Check.in_range(18, 55), nullable=True),
        "ciudad": Column(str, nullable=True),
        "pais": Column(str, Check.isin(PAISES)),
        "genero": Column(str, Check.isin(GENEROS)),
        "fecha_registro": Column(str, Check.str_matches(FORMATO_FECHA)),
        "tipo_cuenta": Column(str, Check.isin(TIPOS_CUENTA)),
        "seguidores": Column(int, Check.in_range(0, 50_000)),
        "seguidos": Column(int, Check.ge(0)),
        "publicaciones_totales": Column(int, Check.ge(0)),
        "activo": Column(bool),
        "bio": Column(str, nullable=True),
    },
    checks=[
        Check(
            lambda df: ~((df["tipo_cuenta"] == "creator") & (df["seguidores"] < 1_000)),
            error="un creator debe tener al menos 1000 seguidores",
        ),
    ],
    strict=True,     # no se admiten columnas que no estén en el contrato
    ordered=True,    # y deben venir en este orden
    name="usuarios",
)

CONTRATO_PUBLICACIONES = DataFrameSchema(
    {
        "id_publicacion": Column(int, Check.ge(1), unique=True),
        "id_usuario": Column(int, Check.ge(1)),
        "fecha": Column(str, Check.str_matches(FORMATO_FECHA)),
        "tipo_contenido": Column(str, Check.isin(TIPOS_CONTENIDO)),
        "likes": Column(float, Check.ge(0), nullable=True),
        "comentarios": Column(float, Check.ge(0), nullable=True),
        "compartidos": Column(int, Check.ge(0)),
        "visualizaciones": Column(int, Check.ge(0)),
        "hashtags": Column(str, Check.str_matches(FORMATO_HASHTAGS)),
    },
    checks=[
        Check(
            lambda df: df["likes"].isna() | (df["visualizaciones"] >= df["likes"]),
            error="las visualizaciones no pueden ser menores que los likes",
        ),
    ],
    strict=True,
    ordered=True,
    name="publicaciones",
)

# ── Contrato de salida del pipeline ──────────────────────────────────────────

CONTRATO_DATASET_PROCESADO = DataFrameSchema(
    {
        "id_publicacion": Column(int, unique=True),
        "id_usuario": Column(int),
        "tipo_contenido": Column(str, Check.isin(TIPOS_CONTENIDO)),
        "tipo_cuenta": Column(str, Check.isin(TIPOS_CUENTA)),
        "likes": Column(float, Check.ge(0)),
        "comentarios": Column(float, Check.ge(0)),
        "visualizaciones": Column(int, Check.ge(0)),
        "seguidores": Column(int, Check.ge(0)),
        "engagement_rate": Column(float, Check.ge(0)),
    },
    checks=[Check(lambda df: df.notna().all(axis=1), error="el dataset procesado no puede tener nulos")],
    strict=False,    # puede tener más columnas, pero estas son obligatorias
    name="dataset_procesado",
)


# ── Contratos entre tablas ───────────────────────────────────────────────────

def comprobar_integridad(usuarios, publicaciones, conexiones=None):
    """
    Comprueba las relaciones entre tablas que pandera no expresa por sí solo.
    Lanza ErrorDeContrato con todos los problemas encontrados.
    """
    problemas = []
    ids_usuarios = set(usuarios["id_usuario"])

    huerfanas = sorted(set(publicaciones["id_usuario"]) - ids_usuarios)
    if huerfanas:
        problemas.append(f"publicaciones de usuarios inexistentes: {huerfanas[:10]}")

    if conexiones is not None:
        seguidos = {s for c in conexiones for s in c["siguiendo"]}
        if not seguidos <= ids_usuarios:
            problemas.append(f"se sigue a usuarios inexistentes: {sorted(seguidos - ids_usuarios)[:10]}")
        autoseguimientos = [c["id_usuario"] for c in conexiones if c["id_usuario"] in c["siguiendo"]]
        if autoseguimientos:
            problemas.append(f"usuarios que se siguen a sí mismos: {autoseguimientos[:10]}")

    if problemas:
        raise ErrorDeContrato("; ".join(problemas))


# ── Pipeline con contratos en la entrada y en la salida ─────────────────────

def construir_dataset_validado(carpeta_datos):
    """
    Carga los datos de 'carpeta_datos', comprueba los contratos de entrada,
    ejecuta el pipeline (limpieza, combinación y engagement) y comprueba el
    contrato de salida. Devuelve el dataset procesado.

    Lanza pandera.errors.SchemaErrors (con todos los fallos) o ErrorDeContrato.
    """
    carpeta = Path(carpeta_datos)
    usuarios = pl.cargar_usuarios(carpeta / "usuarios.csv")
    publicaciones = pl.cargar_publicaciones(carpeta / "publicaciones.xlsx")
    with open(carpeta / "conexiones.json", encoding="utf-8") as fichero:
        conexiones = json.load(fichero)

    # 1. Contratos de entrada: si los datos no son válidos, no se procesan
    CONTRATO_USUARIOS.validate(usuarios, lazy=True)
    CONTRATO_PUBLICACIONES.validate(publicaciones, lazy=True)
    comprobar_integridad(usuarios, publicaciones, conexiones)

    # 2. Pipeline
    combinado = pl.limpiar_dataset(publicaciones).merge(pl.limpiar_dataset(usuarios), on="id_usuario", how="left")
    dataset = pl.calcular_engagement(combinado)

    # 3. Contrato de salida: lo que se entrega cumple lo prometido
    return CONTRATO_DATASET_PROCESADO.validate(dataset, lazy=True)
