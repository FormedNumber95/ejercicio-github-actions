"""Tests avanzados del Bloque 1."""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from pipeline_avanzada import (
    hashtags_normalizados,
    informe_actividad_ciudades,
    recomendaciones_por_conexiones,
    validar_publicaciones,
)

USUARIOS = [
    {"id_usuario": 1, "nombre": "Ana", "ciudad": "Madrid", "seguidores": 5000, "activo": "True"},
    {"id_usuario": 2, "nombre": "Borja", "ciudad": "Bilbao", "seguidores": 1200, "activo": "True"},
    {"id_usuario": 3, "nombre": "Carmen", "ciudad": "Madrid", "seguidores": 800, "activo": "False"},
]


def test_informe_actividad_ciudades():
    resultado = informe_actividad_ciudades(USUARIOS)
    assert resultado["Madrid"]["usuarios"] == 2
    assert resultado["Madrid"]["activos"] == 1
    assert resultado["Madrid"]["seguidores_totales"] == 5800


def test_recomendaciones_por_conexiones():
    conexiones = [{"id_usuario": 1, "siguiendo": [2]}, {"id_usuario": 2, "siguiendo": [3]}]
    resultado = recomendaciones_por_conexiones(USUARIOS, conexiones, 1)
    assert [usuario["id_usuario"] for usuario in resultado] == [3]


def test_hashtags_normalizados():
    publicaciones = [{"hashtags": " #Python, #IA "}, {"hashtags": "#python,#datos"}]
    assert hashtags_normalizados(publicaciones) == {"#python", "#ia", "#datos"}


def test_validar_publicaciones():
    validas, errores = validar_publicaciones(
        [{"id": 1, "id_usuario": 1}, {"id": 2, "id_usuario": 99}],
        USUARIOS,
    )
    assert len(validas) == 1
    assert len(errores) == 1
