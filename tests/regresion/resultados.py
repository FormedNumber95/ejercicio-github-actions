"""
Cálculo de los resultados clave del pipeline sobre los datos reales.

Lo usan tanto el test de regresión (para comparar) como el script
actualizar_referencia.py (para guardar la referencia en referencia.json).
Así ambos calculan exactamente lo mismo.
"""

import csv
import json
from pathlib import Path

import pipeline as pl

RAIZ = Path(__file__).resolve().parents[2]
DATA = RAIZ / "data"
REFERENCIA = Path(__file__).resolve().parent / "referencia.json"


def _leer_csv(nombre):
    with open(DATA / nombre, encoding="utf-8") as fichero:
        return list(csv.DictReader(fichero))


def calcular_resultados():
    """Devuelve un diccionario con los resultados que no deberían cambiar sin querer."""
    usuarios = pl.limpiar_dataset(pl.cargar_usuarios(DATA / "usuarios.csv"))
    publicaciones = pl.limpiar_dataset(pl.cargar_publicaciones(DATA / "publicaciones.xlsx"))
    combinado = pl.calcular_engagement(publicaciones.merge(usuarios, on="id_usuario", how="left"))
    usuarios_csv = _leer_csv("usuarios.csv")
    publicaciones_csv = _leer_csv("publicaciones.csv")
    resumen = pl.resumen_por_ciudad(combinado)
    estadisticas = pl.estadisticas_columna(usuarios["seguidores"].to_numpy())

    return {
        # Bloque 1 (estructuras de Python)
        "n_usuarios_activos": len(pl.usuarios_activos(usuarios_csv)),
        "n_hashtags_unicos": len(pl.hashtags_unicos(publicaciones_csv)),
        "top3_seguidores_ids": [int(u["id_usuario"]) for u in pl.top_por_seguidores(usuarios_csv, n=3)],
        # Bloque 2 (NumPy)
        "estadisticas_seguidores": {k: round(v, 4) for k, v in estadisticas.items()},
        # Bloques 3 y 4 (Pandas)
        "media_edad_tras_limpiar": round(float(usuarios["edad"].mean()), 4),
        "engagement_medio": round(float(combinado["engagement_rate"].mean()), 6),
        "engagement_mediano": round(float(combinado["engagement_rate"].median()), 6),
        "top5_creadores_ids": [int(i) for i in pl.top_creadores(combinado, n=5)["id_usuario"]],
        "publicaciones_por_ciudad": {str(c): int(n) for c, n in resumen["n_publicaciones"].items()},
        # Bloque 5
        "publicaciones_por_mes": {
            fila.mes: int(fila.publicaciones) for fila in pl.publicaciones_por_mes(combinado).itertuples()
        },
    }


def cargar_referencia():
    return json.loads(REFERENCIA.read_text(encoding="utf-8"))
