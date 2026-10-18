"""
Tests del REPOSITORIO: ningún fichero grande se versiona fuera de Git LFS.

Git guarda para siempre cada versión de cada fichero: un fichero grande
versionado "a pelo" hace que el repositorio pese cada vez más y que clonarlo
sea lento. Con Git LFS, en el repositorio solo se guarda un PUNTERO de unos
130 bytes y el contenido real va a un almacenamiento aparte.

Estos tests leen lo que git guarda en el último commit (no los ficheros de la
carpeta), así que hay que hacer commit antes de lanzarlos:

    uv run pytest -m repositorio
"""

import subprocess

import pytest

pytestmark = pytest.mark.repositorio

LIMITE_MB = 2                 # tamaño máximo de un fichero versionado sin LFS
TAMANO_MAXIMO_PUNTERO = 1024  # un puntero de LFS ocupa unos 130 bytes


def _git(raiz, *argumentos, entrada=None):
    return subprocess.run(
        ["git", *argumentos], cwd=raiz, input=entrada, capture_output=True, text=True, encoding="utf-8"
    )


@pytest.fixture(scope="module")
def ficheros_versionados(raiz_proyecto):
    """Diccionario {ruta: tamaño en bytes} de cada fichero del último commit, tal como lo guarda git."""
    resultado = _git(raiz_proyecto, "ls-tree", "-r", "-l", "-z", "HEAD")
    if resultado.returncode != 0:
        pytest.skip("No es un repositorio git o no tiene ningún commit")
    ficheros = {}
    for entrada in filter(None, resultado.stdout.split("\0")):
        cabecera, ruta = entrada.split("\t", 1)
        _modo, tipo, _hash, tamano = cabecera.split()
        if tipo == "blob":
            ficheros[ruta] = int(tamano)
    return ficheros


@pytest.fixture(scope="module")
def ficheros_con_regla_lfs(raiz_proyecto, ficheros_versionados):
    """Rutas a las que .gitattributes asigna Git LFS (filter=lfs)."""
    entrada = "\0".join(ficheros_versionados) + "\0"
    salida = _git(raiz_proyecto, "check-attr", "-z", "filter", "--stdin", entrada=entrada).stdout
    campos = salida.split("\0")
    # La salida viene en grupos de tres: ruta, atributo, valor
    return {campos[i] for i in range(0, len(campos) - 2, 3) if campos[i + 2] == "lfs"}


def test_ningun_fichero_grande_fuera_de_lfs(ficheros_versionados):
    limite = LIMITE_MB * 1_000_000   # MB decimales, como los muestra 'git lfs ls-files'
    grandes = {
        ruta: f"{tamano / 1_000_000:.1f} MB" for ruta, tamano in ficheros_versionados.items() if tamano > limite
    }
    assert not grandes, (
        f"Ficheros de más de {LIMITE_MB} MB versionados sin Git LFS: {grandes}. "
        "Sácalos del commit y usa 'git lfs track' (ver docs/GUIA_FICHEROS_GRANDES.md)."
    )


def test_los_ficheros_con_regla_lfs_se_guardan_como_punteros(ficheros_versionados, ficheros_con_regla_lfs):
    """
    Si .gitattributes dice que un fichero va a LFS pero git-lfs no estaba
    instalado al hacer commit, el fichero se guarda entero: aquí se detecta.
    """
    guardados_enteros = {
        ruta: ficheros_versionados[ruta]
        for ruta in ficheros_con_regla_lfs
        if ficheros_versionados[ruta] > TAMANO_MAXIMO_PUNTERO
    }
    assert not guardados_enteros, (
        f"Tienen regla de LFS pero se han guardado enteros (¿falta 'git lfs install'?): {guardados_enteros}"
    )
