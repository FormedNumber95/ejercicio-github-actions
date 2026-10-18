"""
tests/test_bloque1.py
Tests de corrección automática — Bloque 1: Estructuras de datos y Lambda

Ejecutar con:
    python -m pytest tests/test_bloque1.py -v

Los tests usan datos de prueba propios (fixtures), NO los ficheros CSV del dataset.
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')
sys.path.insert(0, SCRIPTS_DIR)

from pipeline import (
    agrupar_por_ciudad,
    extraer_hashtags_regex,
    hashtags_unicos,
    publicaciones_con_hashtag,
    top_por_seguidores,
    usuarios_activos,
)

# ── Fixtures ─────────────────────────────────────────────────────────────────

USUARIOS_TEST = [
    {'id_usuario': 1, 'nombre': 'Ana',    'ciudad': 'Madrid',    'seguidores': 5000, 'activo': 'True'},
    {'id_usuario': 2, 'nombre': 'Borja',  'ciudad': 'Barcelona', 'seguidores': 1200, 'activo': 'False'},
    {'id_usuario': 3, 'nombre': 'Carmen', 'ciudad': 'Madrid',    'seguidores': 800,  'activo': 'True'},
    {'id_usuario': 4, 'nombre': 'David',  'ciudad': None,        'seguidores': 300,  'activo': 'True'},
    {'id_usuario': 5, 'nombre': 'Eva',    'ciudad': 'Sevilla',   'seguidores': 9500, 'activo': 'False'},
    {'id_usuario': 6, 'nombre': 'Fran',   'ciudad': 'Barcelona', 'seguidores': 600,  'activo': 'True'},
    {'id_usuario': 7, 'nombre': 'Gema',   'ciudad': '',          'seguidores': 200,  'activo': 'True'},
]

PUBLICACIONES_TEST = [
    {'id_publicacion': 1, 'hashtags': '#python,#ia,#datos'},
    {'id_publicacion': 2, 'hashtags': '#ia,#machinelearning'},
    {'id_publicacion': 3, 'hashtags': '#python,#programacion'},
    {'id_publicacion': 4, 'hashtags': '#datos,#bigdata,#ia'},
    {'id_publicacion': 5, 'hashtags': ''},
]


# ── Tests usuarios_activos ────────────────────────────────────────────────────

class TestUsuariosActivos:
    def test_devuelve_lista(self):
        resultado = usuarios_activos(USUARIOS_TEST)
        assert isinstance(resultado, list)

    def test_cantidad_correcta(self):
        resultado = usuarios_activos(USUARIOS_TEST)
        # Usuarios con activo == 'True': Ana, Carmen, David, Fran, Gema → 5
        assert len(resultado) == 5

    def test_todos_son_activos(self):
        resultado = usuarios_activos(USUARIOS_TEST)
        for u in resultado:
            assert u['activo'] == 'True'

    def test_lista_vacia(self):
        assert usuarios_activos([]) == []

    def test_ninguno_activo(self):
        inactivos = [{'activo': 'False'}, {'activo': 'False'}]
        assert usuarios_activos(inactivos) == []


# ── Tests agrupar_por_ciudad ──────────────────────────────────────────────────

class TestAgruparPorCiudad:
    def test_devuelve_dict(self):
        resultado = agrupar_por_ciudad(USUARIOS_TEST)
        assert isinstance(resultado, dict)

    def test_ciudades_correctas(self):
        resultado = agrupar_por_ciudad(USUARIOS_TEST)
        assert 'Madrid' in resultado
        assert 'Barcelona' in resultado
        assert 'Sevilla' in resultado

    def test_ignora_ciudad_none(self):
        resultado = agrupar_por_ciudad(USUARIOS_TEST)
        assert None not in resultado

    def test_ignora_ciudad_vacia(self):
        resultado = agrupar_por_ciudad(USUARIOS_TEST)
        assert '' not in resultado

    def test_nombres_en_madrid(self):
        resultado = agrupar_por_ciudad(USUARIOS_TEST)
        assert 'Ana' in resultado['Madrid']
        assert 'Carmen' in resultado['Madrid']

    def test_barcelona_tiene_dos(self):
        resultado = agrupar_por_ciudad(USUARIOS_TEST)
        assert len(resultado['Barcelona']) == 2

    def test_lista_vacia(self):
        assert agrupar_por_ciudad([]) == {}


# ── Tests hashtags_unicos ─────────────────────────────────────────────────────

class TestHashtagsUnicos:
    def test_devuelve_set(self):
        resultado = hashtags_unicos(PUBLICACIONES_TEST)
        assert isinstance(resultado, set)

    def test_contiene_hashtags_correctos(self):
        resultado = hashtags_unicos(PUBLICACIONES_TEST)
        assert '#python' in resultado
        assert '#ia' in resultado
        assert '#datos' in resultado
        assert '#machinelearning' in resultado
        assert '#bigdata' in resultado
        assert '#programacion' in resultado

    def test_no_duplicados(self):
        resultado = hashtags_unicos(PUBLICACIONES_TEST)
        # #python aparece en pub 1 y 3 → sólo una vez en el set
        count = sum(1 for h in resultado if h == '#python')
        assert count == 1

    def test_ignora_hashtag_vacio(self):
        resultado = hashtags_unicos(PUBLICACIONES_TEST)
        assert '' not in resultado

    def test_cantidad_total(self):
        resultado = hashtags_unicos(PUBLICACIONES_TEST)
        # python, ia, datos, machinelearning, programacion, bigdata → 6
        assert len(resultado) == 6

    def test_lista_vacia(self):
        assert hashtags_unicos([]) == set()


# ── Tests top_por_seguidores ──────────────────────────────────────────────────

class TestTopPorSeguidores:
    def test_devuelve_lista(self):
        resultado = top_por_seguidores(USUARIOS_TEST, n=3)
        assert isinstance(resultado, list)

    def test_longitud_correcta(self):
        resultado = top_por_seguidores(USUARIOS_TEST, n=3)
        assert len(resultado) == 3

    def test_ordenados_de_mayor_a_menor(self):
        resultado = top_por_seguidores(USUARIOS_TEST, n=5)
        seguidores = [u['seguidores'] for u in resultado]
        assert seguidores == sorted(seguidores, reverse=True)

    def test_primer_elemento_es_el_mayor(self):
        resultado = top_por_seguidores(USUARIOS_TEST, n=1)
        assert resultado[0]['nombre'] == 'Eva'  # 9500 seguidores

    def test_n_mayor_que_lista(self):
        # Si n > len(lista), devuelve todos ordenados
        resultado = top_por_seguidores(USUARIOS_TEST, n=100)
        assert len(resultado) == len(USUARIOS_TEST)

    def test_n_default_es_10(self):
        datos = [{'nombre': f'U{i}', 'seguidores': i} for i in range(20)]
        resultado = top_por_seguidores(datos)
        assert len(resultado) == 10

    def test_lista_vacia(self):
        assert top_por_seguidores([]) == []


# ── Tests expresiones regulares ──────────────────────────────────────────────

class TestExtraerHashtagsRegex:
    def test_extrae_hashtags_en_orden(self):
        texto = "Aprende #Python, #IA y #datos_2026."
        assert extraer_hashtags_regex(texto) == ["#python", "#ia", "#datos_2026"]

    def test_ignora_puntuacion_y_conserva_duplicados(self):
        texto = "#Python! (#python) y #datos."
        assert extraer_hashtags_regex(texto) == ["#python", "#python", "#datos"]

    def test_sin_hashtags(self):
        assert extraer_hashtags_regex("Texto sin etiquetas") == []


class TestPublicacionesConHashtag:
    def test_filtra_por_hashtag_completo(self):
        publicaciones = [
            {"id_publicacion": 1, "hashtags": "#python,#ia"},
            {"id_publicacion": 2, "hashtags": "#iabd,#datos"},
            {"id_publicacion": 3, "hashtags": "#IA,#machinelearning"},
        ]
        resultado = publicaciones_con_hashtag(publicaciones, "#ia")
        assert [publicacion["id_publicacion"] for publicacion in resultado] == [1, 3]

    def test_no_modifica_las_publicaciones(self):
        publicaciones = [{"id_publicacion": 1, "hashtags": "#python,#ia"}]
        publicaciones_con_hashtag(publicaciones, "#ia")
        assert publicaciones == [{"id_publicacion": 1, "hashtags": "#python,#ia"}]

    def test_sin_coincidencias(self):
        assert publicaciones_con_hashtag(PUBLICACIONES_TEST, "#rust") == []
