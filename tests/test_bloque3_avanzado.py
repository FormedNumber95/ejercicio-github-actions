"""Tests avanzados del Bloque 3: Pandas básico."""

import os
import sys

import pandas as pd
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from pipeline_avanzada import (
    auditar_dataframe,
    comparar_imputaciones,
    limpiar_usuarios_avanzado,
    validar_calidad_usuarios,
)

# ── Datos de prueba ──────────────────────────────────────────────────────────

def tabla_auditoria():
    return pd.DataFrame({
        "edad": [20.0, None, 30.0, 30.0],
        "ciudad": ["Madrid", "Bilbao", "Madrid", "Madrid"],
    })


def tabla_imputacion():
    return pd.DataFrame({"x": [10.0, None, 20.0, 90.0]})


def tabla_usuarios():
    return pd.DataFrame({
        "id_usuario": [1, 2, 2],
        "edad": [25.0, None, 90.0],
        "seguidores": [100, 50, 10],
        "seguidos": [10, 80, 5],
    })


# ── Tests auditar_dataframe ──────────────────────────────────────────────────

class TestAuditarDataframe:
    def test_devuelve_dataframe_con_columnas_correctas(self):
        resultado = auditar_dataframe(tabla_auditoria())
        assert isinstance(resultado, pd.DataFrame)
        assert list(resultado.columns) == [
            "columna", "tipo_dato", "n_nulos", "porcentaje_nulos", "n_distintos",
        ]

    def test_una_fila_por_columna_en_orden(self):
        resultado = auditar_dataframe(tabla_auditoria())
        assert resultado["columna"].tolist() == ["edad", "ciudad"]

    def test_nulos(self):
        resultado = auditar_dataframe(tabla_auditoria())
        assert resultado["n_nulos"].tolist() == [1, 0]

    def test_porcentaje_de_nulos(self):
        resultado = auditar_dataframe(tabla_auditoria())
        assert resultado["porcentaje_nulos"].tolist() == [25.0, 0.0]

    def test_valores_distintos_no_cuentan_nulos(self):
        resultado = auditar_dataframe(tabla_auditoria())
        assert resultado["n_distintos"].tolist() == [2, 2]

    def test_tipo_de_dato_es_texto(self):
        resultado = auditar_dataframe(tabla_auditoria())
        assert all(isinstance(tipo, str) for tipo in resultado["tipo_dato"])
        assert resultado.loc[0, "tipo_dato"] == "float64"

    def test_porcentaje_redondeado_a_dos_decimales(self):
        df = pd.DataFrame({"a": [1.0, None, None]})
        resultado = auditar_dataframe(df)
        assert resultado.loc[0, "porcentaje_nulos"] == 66.67

    def test_no_modifica_el_original(self):
        df = tabla_auditoria()
        auditar_dataframe(df)
        pd.testing.assert_frame_equal(df, tabla_auditoria())


# ── Tests limpiar_usuarios_avanzado ──────────────────────────────────────────

def tabla_usuarios_sucios():
    return pd.DataFrame({
        "id_usuario": [1, 2, 3],
        "nombre": [" ana ", None, "Carmen"],
        "apellidos": ["  gil PEREZ", "ruiz", None],
        "ciudad": [" Madrid ", None, "bilbao"],
        "edad": [25.0, None, 40.0],
        "seguidores": [100, -1, 300],
        "fecha_registro": ["2023-01-05", "2022-11-30", "2024-02-14"],
    })


class TestLimpiarUsuariosAvanzado:
    def test_no_modifica_el_original(self):
        original = tabla_usuarios_sucios()
        resultado = limpiar_usuarios_avanzado(original)
        assert original["edad"].isna().sum() == 1
        assert resultado["edad"].isna().sum() == 0
        pd.testing.assert_frame_equal(original, tabla_usuarios_sucios())

    def test_nombres_sin_espacios_y_en_formato_titulo(self):
        resultado = limpiar_usuarios_avanzado(tabla_usuarios_sucios())
        assert resultado.loc[0, "nombre"] == "Ana"
        assert resultado.loc[0, "apellidos"] == "Gil Perez"
        assert resultado.loc[0, "ciudad"] == "Madrid"
        assert resultado.loc[2, "ciudad"] == "Bilbao"

    def test_nulos_de_texto_pasan_a_desconocido(self):
        resultado = limpiar_usuarios_avanzado(tabla_usuarios_sucios())
        assert resultado.loc[1, "nombre"] == "Desconocido"
        assert resultado.loc[1, "ciudad"] == "Desconocido"
        assert resultado.loc[2, "apellidos"] == "Desconocido"

    def test_nulos_numericos_se_rellenan_con_la_mediana(self):
        resultado = limpiar_usuarios_avanzado(tabla_usuarios_sucios())
        assert resultado.loc[1, "edad"] == 32.5

    def test_no_corrige_valores_invalidos_de_negocio(self):
        resultado = limpiar_usuarios_avanzado(tabla_usuarios_sucios())
        assert resultado.loc[1, "seguidores"] == -1

    def test_fecha_registro_pasa_a_tipo_fecha(self):
        resultado = limpiar_usuarios_avanzado(tabla_usuarios_sucios())
        assert pd.api.types.is_datetime64_any_dtype(resultado["fecha_registro"])

    def test_conserva_filas_y_columnas(self):
        original = tabla_usuarios_sucios()
        resultado = limpiar_usuarios_avanzado(original)
        assert resultado.shape == original.shape
        assert list(resultado.columns) == list(original.columns)

    def test_es_idempotente(self):
        una_vez = limpiar_usuarios_avanzado(tabla_usuarios_sucios())
        dos_veces = limpiar_usuarios_avanzado(una_vez)
        pd.testing.assert_frame_equal(una_vez, dos_veces)

    def test_funciona_sin_columnas_opcionales(self):
        df = pd.DataFrame({"nombre": [" ana "], "edad": [None]})
        resultado = limpiar_usuarios_avanzado(df)
        assert resultado.loc[0, "nombre"] == "Ana"


# ── Tests comparar_imputaciones ──────────────────────────────────────────────

class TestCompararImputaciones:
    def test_devuelve_dataframe_con_columnas_correctas(self):
        resultado = comparar_imputaciones(tabla_imputacion(), "x")
        assert isinstance(resultado, pd.DataFrame)
        assert list(resultado.columns) == [
            "estrategia", "n_filas", "media_resultante", "mediana_resultante",
        ]

    def test_estrategias_en_orden(self):
        resultado = comparar_imputaciones(tabla_imputacion(), "x")
        assert resultado["estrategia"].tolist() == [
            "eliminar filas", "rellenar con media", "rellenar con mediana",
        ]

    def test_filas_que_conserva_cada_estrategia(self):
        resultado = comparar_imputaciones(tabla_imputacion(), "x")
        assert resultado["n_filas"].tolist() == [3, 4, 4]

    def test_media_resultante(self):
        resultado = comparar_imputaciones(tabla_imputacion(), "x")
        assert resultado["media_resultante"].tolist() == pytest.approx([40.0, 40.0, 35.0])

    def test_mediana_resultante(self):
        resultado = comparar_imputaciones(tabla_imputacion(), "x")
        assert resultado["mediana_resultante"].tolist() == pytest.approx([20.0, 30.0, 20.0])

    def test_no_modifica_el_original(self):
        df = tabla_imputacion()
        comparar_imputaciones(df, "x")
        pd.testing.assert_frame_equal(df, tabla_imputacion())


# ── Tests validar_calidad_usuarios ───────────────────────────────────────────

class TestValidarCalidadUsuarios:
    def test_devuelve_matriz_booleana_con_las_reglas(self):
        resultado = validar_calidad_usuarios(tabla_usuarios())
        assert list(resultado.columns) == [
            "edad_nula",
            "edad_fuera_de_rango",
            "mas_seguidos_que_seguidores",
            "fila_duplicada",
            "id_repetido",
        ]
        assert all(pd.api.types.is_bool_dtype(dtype) for dtype in resultado.dtypes)

    def test_mismas_filas_e_indice_que_la_entrada(self):
        df = tabla_usuarios()
        resultado = validar_calidad_usuarios(df)
        assert resultado.index.equals(df.index)

    def test_edad_nula(self):
        resultado = validar_calidad_usuarios(tabla_usuarios())
        assert resultado["edad_nula"].tolist() == [False, True, False]

    def test_edad_fuera_de_rango_ignora_los_nulos(self):
        resultado = validar_calidad_usuarios(tabla_usuarios())
        assert resultado["edad_fuera_de_rango"].tolist() == [False, False, True]

    def test_mas_seguidos_que_seguidores(self):
        resultado = validar_calidad_usuarios(tabla_usuarios())
        assert resultado["mas_seguidos_que_seguidores"].tolist() == [False, True, False]

    def test_id_repetido_marca_solo_la_segunda_aparicion(self):
        resultado = validar_calidad_usuarios(tabla_usuarios())
        assert resultado["id_repetido"].tolist() == [False, False, True]

    def test_fila_duplicada(self):
        df = pd.concat([tabla_usuarios(), tabla_usuarios().head(2)], ignore_index=True)
        resultado = validar_calidad_usuarios(df)
        assert resultado["fila_duplicada"].tolist() == [False, False, False, True, True]

    def test_limites_del_rango_de_edad(self):
        df = pd.DataFrame({
            "id_usuario": [1, 2, 3, 4],
            "edad": [17.0, 18.0, 55.0, 56.0],
            "seguidores": [1, 1, 1, 1],
            "seguidos": [1, 1, 1, 1],
        })
        resultado = validar_calidad_usuarios(df)
        assert resultado["edad_fuera_de_rango"].tolist() == [True, False, False, True]

    def test_no_modifica_el_original(self):
        df = tabla_usuarios()
        validar_calidad_usuarios(df)
        pd.testing.assert_frame_equal(df, tabla_usuarios())
