"""
Tests del MODELO (marcador ``modelo``).

Comprueban el modelo guardado en modelos/ igual que se comprueba cualquier otro
entregable del proyecto:
  - el modelo y sus metadatos existen y son coherentes con el código,
  - no hay fuga de datos y la división entrenamiento/prueba es correcta,
  - el rendimiento supera un mínimo y al modelo trivial de referencia,
  - las métricas guardadas se reproducen (si cambian datos o código, se detecta),
  - el modelo se comporta de forma razonable (invarianza y dirección).
"""

import modelo as m
import numpy as np
import pytest
from contratos import construir_dataset_validado
from sklearn.metrics import roc_auc_score

pytestmark = pytest.mark.modelo

ROC_AUC_MINIMO = 0.80
F1_MINIMO = 0.70
MEJORA_MINIMA_SOBRE_REFERENCIA = 0.20


@pytest.mark.parametrize(
    ("tipo", "clase_esperada"),
    [("base", "DummyClassifier"), ("logistica", "LogisticRegression"), ("bosque", "RandomForestClassifier")],
)
def test_crear_modelo_de_cada_tipo(tipo, clase_esperada):
    assert type(m.crear_modelo(tipo).named_steps["clasificador"]).__name__ == clase_esperada


def test_crear_modelo_rechaza_tipos_desconocidos():
    with pytest.raises(ValueError, match="desconocido"):
        m.crear_modelo("red_neuronal")


@pytest.fixture(scope="module")
def datos(carpeta_datos):
    X, y = m.preparar_datos_modelo(construir_dataset_validado(carpeta_datos))
    X_train, X_test, y_train, y_test = m.dividir_datos(X, y)
    return {"X": X, "y": y, "X_train": X_train, "X_test": X_test, "y_train": y_train, "y_test": y_test}


@pytest.fixture(scope="module")
def modelo_guardado():
    return m.cargar_modelo()


@pytest.fixture(scope="module")
def metadatos():
    return m.cargar_metadatos()


# ── El modelo guardado y sus metadatos ──────────────────────────────────────

def test_existen_el_modelo_y_sus_metadatos():
    assert m.RUTA_MODELO.exists(), "Falta el modelo: ejecuta notebooks/Bloque_07_Modelo.ipynb"
    assert m.RUTA_METADATOS.exists()


def test_metadatos_coherentes_con_el_codigo(metadatos):
    assert metadatos["variables"] == m.VARIABLES
    assert metadatos["semilla"] == m.SEMILLA
    assert metadatos["umbral_alto_alcance"] == m.UMBRAL_ALTO_ALCANCE
    assert metadatos["tipo"] != "base", "El modelo guardado no puede ser el de referencia"
    assert set(metadatos["metricas_test"]) == {"accuracy", "precision", "recall", "f1", "roc_auc"}


def test_formato_de_las_predicciones(modelo_guardado, datos):
    probabilidad = modelo_guardado.predict_proba(datos["X_test"])[:, 1]
    prediccion = modelo_guardado.predict(datos["X_test"])
    assert probabilidad.shape == (len(datos["X_test"]),)
    assert ((probabilidad >= 0) & (probabilidad <= 1)).all()
    assert set(np.unique(prediccion)) <= {0, 1}


# ── Datos del modelo ─────────────────────────────────────────────────────────

def test_sin_fuga_de_datos(metadatos):
    assert not set(m.VARIABLES) & set(m.VARIABLES_PROHIBIDAS)
    assert not set(metadatos["variables"]) & set(m.VARIABLES_PROHIBIDAS)


def test_division_sin_solapamiento_y_estratificada(datos):
    assert not set(datos["X_train"].index) & set(datos["X_test"].index)
    assert len(datos["X_test"]) == pytest.approx(len(datos["X"]) * m.PROPORCION_TEST, abs=1)
    assert datos["y_train"].mean() == pytest.approx(datos["y_test"].mean(), abs=0.05)


# ── Rendimiento ──────────────────────────────────────────────────────────────

def test_rendimiento_minimo(modelo_guardado, datos):
    metricas = m.evaluar(modelo_guardado, datos["X_test"], datos["y_test"])
    assert metricas["roc_auc"] >= ROC_AUC_MINIMO, metricas
    assert metricas["f1"] >= F1_MINIMO, metricas


def test_supera_claramente_al_modelo_de_referencia(modelo_guardado, datos):
    referencia = m.crear_modelo("base").fit(datos["X_train"], datos["y_train"])
    auc_referencia = roc_auc_score(datos["y_test"], referencia.predict_proba(datos["X_test"])[:, 1])
    auc_modelo = roc_auc_score(datos["y_test"], modelo_guardado.predict_proba(datos["X_test"])[:, 1])
    assert auc_modelo - auc_referencia >= MEJORA_MINIMA_SOBRE_REFERENCIA


# ── Reproducibilidad (regresión del modelo) ─────────────────────────────────

def test_las_metricas_guardadas_coinciden_con_el_modelo_guardado(modelo_guardado, metadatos, datos):
    metricas = m.evaluar(modelo_guardado, datos["X_test"], datos["y_test"])
    assert metricas == pytest.approx(metadatos["metricas_test"], abs=1e-3)


def test_reentrenar_con_los_mismos_parametros_da_las_mismas_metricas(metadatos, datos):
    """Si cambian los datos, las variables o el código de entrenamiento, este test lo detecta."""
    modelo = m.crear_modelo(metadatos["tipo"], **metadatos["parametros"]).fit(datos["X_train"], datos["y_train"])
    assert m.evaluar(modelo, datos["X_test"], datos["y_test"]) == pytest.approx(metadatos["metricas_test"], abs=1e-3)


# ── Comportamiento ───────────────────────────────────────────────────────────

def test_invarianza_ignora_columnas_que_no_son_variables(modelo_guardado, datos):
    """Columnas extra (incluso con la 'respuesta') o en otro orden no cambian la predicción."""
    X = datos["X_test"]
    con_extras = X.assign(visualizaciones=999_999, engagement_rate=5.0, ciudad="Madrid")
    reordenado = con_extras[list(reversed(con_extras.columns))]
    original = modelo_guardado.predict_proba(X)[:, 1]
    np.testing.assert_allclose(modelo_guardado.predict_proba(reordenado)[:, 1], original)


def test_direccional_mas_likes_no_reduce_la_probabilidad(modelo_guardado, datos):
    """Duplicar los likes de una publicación no debería hacer menos probable el alto alcance."""
    X = datos["X_test"]
    original = modelo_guardado.predict_proba(X)[:, 1]
    con_mas_likes = modelo_guardado.predict_proba(X.assign(likes=X["likes"] * 2))[:, 1]
    assert (con_mas_likes >= original - 1e-9).mean() >= 0.95


def test_guardar_y_cargar_conserva_el_modelo(modelo_guardado, metadatos, datos, tmp_path):
    ruta, ruta_metadatos = tmp_path / "modelo.joblib", tmp_path / "metadatos.json"
    m.guardar_modelo(modelo_guardado, metadatos["tipo"], metadatos["parametros"], metadatos["metricas_test"],
                     ruta=ruta, ruta_metadatos=ruta_metadatos)
    recargado = m.cargar_modelo(ruta)
    np.testing.assert_allclose(recargado.predict_proba(datos["X_test"]), modelo_guardado.predict_proba(datos["X_test"]))
    assert m.cargar_metadatos(ruta_metadatos) == metadatos
