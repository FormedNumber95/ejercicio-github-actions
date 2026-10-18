"""
modelo.py
Modelo de clasificación del ALCANCE de una publicación (Red Social Ficticia).

Objetivo: predecir si una publicación tendrá ALTO ALCANCE (12 000
visualizaciones o más) a partir de sus interacciones y de los datos de su autor.

El cuaderno notebooks/Bloque_07_Modelo.ipynb usa estas funciones para entrenar
y comparar modelos y guardar el elegido en modelos/. Los tests de tests/modelo/
comprueban el modelo guardado.
"""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RAIZ = Path(__file__).resolve().parent.parent
RUTA_MODELO = RAIZ / "modelos" / "modelo_alcance.joblib"
RUTA_METADATOS = RAIZ / "modelos" / "metadatos_modelo.json"

SEMILLA = 42
PROPORCION_TEST = 0.25
UMBRAL_ALTO_ALCANCE = 12_000

OBJETIVO = "alto_alcance"
VARIABLES_NUMERICAS = [
    "likes", "comentarios", "compartidos", "seguidores", "seguidos",
    "publicaciones_totales", "edad", "n_hashtags", "mes",
    "engagement_rate",  # con esta variable el roc_auc mejora
]
VARIABLES_CATEGORICAS = ["tipo_contenido", "tipo_cuenta"]
VARIABLES = VARIABLES_NUMERICAS + VARIABLES_CATEGORICAS

# Columnas que NUNCA pueden ser variables porque contienen la respuesta
# (fuga de datos): 'engagement_rate' se calcula dividiendo entre las visualizaciones.
VARIABLES_PROHIBIDAS = ["visualizaciones", "engagement_rate"]


def preparar_datos_modelo(dataset):
    """
    Recibe el dataset procesado y devuelve (X, y):
      - X: las VARIABLES del modelo, con 'id_publicacion' como índice.
      - y: 1 si la publicación tiene alto alcance (visualizaciones >= 12 000), 0 si no.
    No modifica el dataset original.
    """
    datos = dataset.copy()
    datos["mes"] = pd.to_datetime(datos["fecha"]).dt.month
    datos["n_hashtags"] = datos["hashtags"].str.count(",") + 1
    datos = datos.set_index("id_publicacion")
    y = (datos["visualizaciones"] >= UMBRAL_ALTO_ALCANCE).astype(int).rename(OBJETIVO)
    return datos[VARIABLES], y


def dividir_datos(X, y):
    """División entrenamiento/prueba reproducible y estratificada (misma proporción de clases)."""
    return train_test_split(X, y, test_size=PROPORCION_TEST, stratify=y, random_state=SEMILLA)


def crear_modelo(tipo="logistica", **parametros):
    """
    Devuelve un Pipeline: preprocesado (escalado de las numéricas y one-hot de
    las categóricas) + clasificador. El resto de columnas se ignoran.
      tipo='base'       -> modelo trivial de referencia (predice al azar)
      tipo='logistica'  -> regresión logística
      tipo='bosque'     -> bosque aleatorio
    """
    if tipo == "base":
        clasificador = DummyClassifier(strategy="stratified", random_state=SEMILLA, **parametros)
    elif tipo == "logistica":
        clasificador = LogisticRegression(max_iter=1_000, random_state=SEMILLA, **parametros)
    elif tipo == "bosque":
        clasificador = RandomForestClassifier(random_state=SEMILLA, **parametros)
    else:
        raise ValueError(f"Tipo de modelo desconocido: {tipo}")

    preprocesado = ColumnTransformer([
        ("numericas", StandardScaler(), VARIABLES_NUMERICAS),
        ("categoricas", OneHotEncoder(handle_unknown="ignore"), VARIABLES_CATEGORICAS),
    ])
    return Pipeline([("preprocesado", preprocesado), ("clasificador", clasificador)])


def evaluar(modelo, X, y):
    """Devuelve un diccionario con las métricas del modelo sobre (X, y), redondeadas a 4 decimales."""
    prediccion = modelo.predict(X)
    probabilidad = modelo.predict_proba(X)[:, 1]
    metricas = {
        "accuracy": accuracy_score(y, prediccion),
        "precision": precision_score(y, prediccion, zero_division=0),
        "recall": recall_score(y, prediccion, zero_division=0),
        "f1": f1_score(y, prediccion, zero_division=0),
        "roc_auc": roc_auc_score(y, probabilidad),
    }
    return {nombre: round(float(valor), 4) for nombre, valor in metricas.items()}


def guardar_modelo(modelo, tipo, parametros, metricas, ruta=RUTA_MODELO, ruta_metadatos=RUTA_METADATOS):
    """
    Guarda el modelo entrenado (joblib) y un JSON de metadatos con todo lo
    necesario para saber qué es y cómo se obtuvo: tipo, parámetros, variables,
    semilla y métricas de prueba. Devuelve los metadatos.
    """
    ruta, ruta_metadatos = Path(ruta), Path(ruta_metadatos)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(modelo, ruta)
    metadatos = {
        "objetivo": OBJETIVO,
        "umbral_alto_alcance": UMBRAL_ALTO_ALCANCE,
        "tipo": tipo,
        "parametros": parametros,
        "variables": VARIABLES,
        "semilla": SEMILLA,
        "proporcion_test": PROPORCION_TEST,
        "metricas_test": metricas,
    }
    texto = json.dumps(metadatos, ensure_ascii=False, indent=2) + "\n"
    ruta_metadatos.write_text(texto, encoding="utf-8", newline="\n")   # LF también en Windows
    return metadatos


def cargar_modelo(ruta=RUTA_MODELO):
    return joblib.load(ruta)


def cargar_metadatos(ruta_metadatos=RUTA_METADATOS):
    return json.loads(Path(ruta_metadatos).read_text(encoding="utf-8"))
