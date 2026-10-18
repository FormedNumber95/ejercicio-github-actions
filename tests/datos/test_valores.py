"""
Tests de VALORES: cada dato está dentro de su rango o dominio válido.

El esquema puede ser correcto (la columna existe y es numérica) y aun así los
valores ser absurdos: edades negativas, fechas futuras o categorías inventadas.
Las reglas salen de cómo se generan los datos (data/setup_datos.py).
"""

import pytest

pytestmark = pytest.mark.valores

# (columna, mínimo, máximo) — los nulos no se comprueban aquí (son cosa de las métricas)
RANGOS_USUARIOS = [
    ("edad", 18, 55),
    ("seguidores", 10, 50_000),
    ("seguidos", 20, 1_000),
    ("publicaciones_totales", 0, 500),
]

RANGOS_PUBLICACIONES = [
    ("likes", 0, 5_000),
    ("comentarios", 0, 500),
    ("compartidos", 0, 200),
    ("visualizaciones", 100, 60_000),
]

DOMINIOS = [
    ("usuarios", "tipo_cuenta", {"free", "premium", "creator"}),
    ("usuarios", "genero", {"M", "F", "NB"}),
    ("usuarios", "pais", {"Espana", "Mexico", "Argentina", "Colombia"}),
    ("publicaciones", "tipo_contenido", {"foto", "video", "texto", "historia", "reel"}),
]


@pytest.mark.parametrize(("columna", "minimo", "maximo"), RANGOS_USUARIOS)
def test_rangos_de_usuarios(usuarios, columna, minimo, maximo):
    valores = usuarios[columna].dropna()
    fuera = valores[(valores < minimo) | (valores > maximo)]
    assert fuera.empty, f"{len(fuera)} valores de '{columna}' fuera de [{minimo}, {maximo}]: {fuera.tolist()[:5]}"


@pytest.mark.parametrize(("columna", "minimo", "maximo"), RANGOS_PUBLICACIONES)
def test_rangos_de_publicaciones(publicaciones, columna, minimo, maximo):
    valores = publicaciones[columna].dropna()
    assert valores.between(minimo, maximo).all()


@pytest.mark.parametrize(("tabla", "columna", "permitidos"), DOMINIOS, ids=[f"{t}.{c}" for t, c, _ in DOMINIOS])
def test_dominios_de_categorias(request, tabla, columna, permitidos):
    df = request.getfixturevalue(tabla)
    desconocidos = set(df[columna].dropna()) - permitidos
    assert not desconocidos, f"Valores no permitidos en {tabla}.{columna}: {desconocidos}"


def test_los_creators_tienen_al_menos_1000_seguidores(usuarios):
    creators = usuarios[usuarios["tipo_cuenta"] == "creator"]
    assert (creators["seguidores"] >= 1_000).all()


def test_fechas_de_registro_en_el_periodo(usuarios):
    assert usuarios["fecha_registro"].between("2020-01-01", "2024-06-01").all()


def test_fechas_de_publicacion_en_el_periodo(publicaciones):
    assert publicaciones["fecha"].between("2023-01-01", "2024-06-01").all()


def test_visualizaciones_nunca_menores_que_likes(publicaciones):
    con_likes = publicaciones.dropna(subset=["likes"])
    assert (con_likes["visualizaciones"] >= con_likes["likes"]).all()


def test_formato_de_los_hashtags(publicaciones):
    # Entre 1 y 5 hashtags separados por comas, sin espacios: '#ia,#python'
    assert publicaciones["hashtags"].str.fullmatch(r"#\w+(,#\w+){0,4}").all()
