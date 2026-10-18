"""
Tests de RELACIONES: integridad referencial entre las tres fuentes de datos.

Usuarios, publicaciones y conexiones están relacionados por 'id_usuario'. Si una
publicación apunta a un usuario que no existe, o un usuario se sigue a sí mismo,
los merge y los análisis darán resultados incorrectos sin lanzar ningún error.
"""

import pandas as pd
import pytest

pytestmark = pytest.mark.relaciones


def test_id_usuario_es_clave_unica(usuarios):
    assert usuarios["id_usuario"].is_unique


def test_id_publicacion_es_clave_unica(publicaciones):
    assert publicaciones["id_publicacion"].is_unique


def test_toda_publicacion_pertenece_a_un_usuario_existente(usuarios, publicaciones):
    huerfanas = set(publicaciones["id_usuario"]) - set(usuarios["id_usuario"])
    assert not huerfanas, f"Publicaciones de usuarios inexistentes: {sorted(huerfanas)}"


def test_merge_publicaciones_usuarios_es_muchos_a_uno(usuarios, publicaciones):
    # validate lanza MergeError si un usuario apareciera duplicado
    combinado = publicaciones.merge(usuarios, on="id_usuario", how="left", validate="many_to_one", indicator=True)
    assert len(combinado) == len(publicaciones)
    assert (combinado["_merge"] == "both").all()


def test_hay_un_registro_de_conexiones_por_usuario(usuarios, conexiones):
    ids_conexiones = [c["id_usuario"] for c in conexiones]
    assert len(ids_conexiones) == len(set(ids_conexiones)), "Hay usuarios repetidos en conexiones.json"
    assert set(ids_conexiones) == set(usuarios["id_usuario"])


def test_solo_se_sigue_a_usuarios_existentes(usuarios, conexiones):
    existentes = set(usuarios["id_usuario"])
    seguidos = {s for c in conexiones for s in c["siguiendo"]}
    assert seguidos <= existentes, f"Se sigue a usuarios inexistentes: {sorted(seguidos - existentes)}"


def test_nadie_se_sigue_a_si_mismo(conexiones):
    autoseguimientos = [c["id_usuario"] for c in conexiones if c["id_usuario"] in c["siguiendo"]]
    assert not autoseguimientos


def test_no_hay_seguimientos_duplicados(conexiones):
    for c in conexiones:
        assert len(c["siguiendo"]) == len(set(c["siguiendo"])), f"Duplicados en el usuario {c['id_usuario']}"


def test_conexiones_y_tabla_de_aristas_son_coherentes(conexiones):
    """Al 'explotar' la lista a una tabla de aristas no se pierde ninguna relación."""
    aristas = pd.DataFrame(conexiones).explode("siguiendo")
    assert len(aristas) == sum(len(c["siguiendo"]) for c in conexiones)
