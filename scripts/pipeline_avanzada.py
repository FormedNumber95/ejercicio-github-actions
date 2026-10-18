"""Solución de los ejercicios avanzados del proyecto Red Social Ficticia.

Ejecuta la correccion con ``python -m pytest tests/*_avanzado.py -v``.
"""

import os
import random
from datetime import date
from typing import Any

import numpy as np
import pandas as pd

# ============================================================
# BLOQUE 1 — Estructuras de datos, Regex y Lambda
# ============================================================

def informe_actividad_ciudades(lista_usuarios: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """Resume usuarios, activos y seguidores por ciudad."""
    informe: dict[str, dict[str, float]] = {}

    for usuario in lista_usuarios:
        ciudad = usuario.get("ciudad")
        if not ciudad:
            continue

        if ciudad not in informe:
            informe[ciudad] = {
                "usuarios": 0,
                "activos": 0,
                "seguidores_totales": 0,
            }

        informe[ciudad]["usuarios"] += 1
        informe[ciudad]["seguidores_totales"] += int(usuario.get("seguidores") or 0)
        if usuario.get("activo") == "True":
            informe[ciudad]["activos"] += 1

    return informe


def recomendaciones_por_conexiones(
    lista_usuarios: list[dict[str, Any]],
    conexiones: list[dict[str, Any]],
    id_usuario: int,
    limite: int = 5,
) -> list[dict[str, Any]]:
    """Devuelve personas seguidas por contactos pero no por el usuario."""
    usuarios_por_id = {usuario["id_usuario"]: usuario for usuario in lista_usuarios}
    siguiendo_por_id = {
        conexion["id_usuario"]: set(conexion.get("siguiendo", []))
        for conexion in conexiones
    }

    seguidos_directos = siguiendo_por_id.get(id_usuario, set())
    candidatos: set[int] = set()

    for id_contacto in seguidos_directos:
        candidatos.update(siguiendo_por_id.get(id_contacto, set()))

    candidatos.discard(id_usuario)
    candidatos.difference_update(seguidos_directos)

    candidatos_ordenados = sorted(
        candidatos,
        key=lambda candidato: (
            -int(usuarios_por_id.get(candidato, {}).get("seguidores") or 0),
            candidato,
        ),
    )

    return [
        usuarios_por_id[candidato]
        for candidato in candidatos_ordenados[:limite]
        if candidato in usuarios_por_id
    ]


def hashtags_normalizados(lista_publicaciones: list[dict[str, Any]]) -> set[str]:
    """Normaliza hashtags, elimina espacios y devuelve los valores unicos."""
    hashtags: set[str] = set()

    for publicacion in lista_publicaciones:
        texto_hashtags = publicacion.get("hashtags") or ""
        for hashtag in texto_hashtags.split(","):
            hashtag_limpio = hashtag.strip().lower()
            if hashtag_limpio:
                if not hashtag_limpio.startswith("#"):
                    hashtag_limpio = f"#{hashtag_limpio}"
                hashtags.add(hashtag_limpio)

    return hashtags


def validar_publicaciones(
    lista_publicaciones: list[dict[str, Any]],
    lista_usuarios: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Separa publicaciones validas y publicaciones con usuario inexistente."""
    ids_usuarios = {usuario["id_usuario"] for usuario in lista_usuarios}
    validas: list[dict[str, Any]] = []
    errores: list[dict[str, Any]] = []

    for publicacion in lista_publicaciones:
        if publicacion.get("id_usuario") in ids_usuarios:
            validas.append(publicacion)
        else:
            errores.append(publicacion)

    return validas, errores

# ============================================================
# BLOQUE 2 — NumPy
# ============================================================

def puntuacion_usuarios(
    seguidores: np.ndarray, seguidos: np.ndarray, publicaciones: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Calcula y normaliza una puntuacion vectorizada de usuarios."""
    puntuacion = 0.5 * seguidores + 0.2 * publicaciones - 0.1 * seguidos
    minimo = puntuacion.min()
    maximo = puntuacion.max()
    normalizada = (puntuacion - minimo) / (maximo - minimo)
    return puntuacion, normalizada


def resumen_matriz(matriz: np.ndarray) -> dict[str, np.ndarray]:
    """Calcula totales por filas y columnas y sus posiciones maximas."""
    totales_filas = matriz.sum(axis=1)
    totales_columnas = matriz.sum(axis=0)
    return {
        "totales_filas": totales_filas,
        "totales_columnas": totales_columnas,
        "fila_maxima": int(np.argmax(totales_filas)),
        "columna_maxima": int(np.argmax(totales_columnas)),
    }


def conexiones_indirectas(matriz_conexiones: np.ndarray) -> np.ndarray:
    """Calcula conexiones de longitud dos mediante producto matricial."""
    return matriz_conexiones @ matriz_conexiones


def simular_engagement(n: int = 30, seed: int = 42) -> np.ndarray:
    """Genera un vector reproducible de engagement sintetico."""
    rng = np.random.default_rng(seed)
    likes = rng.integers(0, 5000, size=n)
    comentarios = rng.integers(0, 500, size=n)
    visualizaciones = rng.integers(100, 50000, size=n)
    return (likes + comentarios) / visualizaciones

# ============================================================
# BLOQUE 3 — Pandas básico
# ============================================================

def auditar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recibe un DataFrame y devuelve una NUEVA tabla con una fila por cada
    columna de 'df' y las columnas:
        'columna'          -> nombre de la columna auditada
        'tipo_dato'        -> tipo de dato de la columna, como texto
        'n_nulos'          -> número de valores nulos
        'porcentaje_nulos' -> porcentaje de nulos sobre el total de filas,
                              redondeado a 2 decimales
        'n_distintos'      -> número de valores distintos (sin contar nulos)
    """
    filas = []
    for columna in df.columns:
        n_nulos = int(df[columna].isnull().sum())
        filas.append({
            "columna": columna,
            "tipo_dato": str(df[columna].dtype),
            "n_nulos": n_nulos,
            "porcentaje_nulos": round(n_nulos / len(df) * 100, 2),
            "n_distintos": int(df[columna].nunique()),
        })
    return pd.DataFrame(filas)


def limpiar_usuarios_avanzado(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recibe la tabla de usuarios y devuelve una COPIA limpia, sin modificar
    el original:
      - texto: elimina espacios sobrantes de los extremos y pone en formato
        título 'nombre', 'apellidos' y 'ciudad' (' ana ' -> 'Ana'); el resto
        de nulos de texto pasan a 'Desconocido'
      - numéricas: los nulos se sustituyen por la mediana de la columna
      - 'fecha_registro' (si existe) se convierte a tipo fecha
    La operación debe ser idempotente: limpiar dos veces da el mismo
    resultado que limpiar una.
    """
    limpio = df.copy()
    columnas_titulo = ["nombre", "apellidos", "ciudad"]
    for columna in limpio.columns:
        serie = limpio[columna]
        if pd.api.types.is_bool_dtype(serie):
            continue
        if pd.api.types.is_numeric_dtype(serie):
            limpio[columna] = serie.fillna(serie.median())
        elif columna == "fecha_registro":
            limpio[columna] = pd.to_datetime(serie)
        else:
            serie = serie.str.strip()
            if columna in columnas_titulo:
                serie = serie.str.title()
            limpio[columna] = serie.fillna("Desconocido")
    return limpio


def comparar_imputaciones(df: pd.DataFrame, columna: str) -> pd.DataFrame:
    """
    Recibe un DataFrame y el nombre de una columna numérica. Devuelve una
    NUEVA tabla con una fila por estrategia, en este orden ('eliminar filas',
    'rellenar con media', 'rellenar con mediana'), y las columnas:
        'estrategia', 'n_filas', 'media_resultante', 'mediana_resultante'
    donde 'n_filas' son las filas que conserva la tabla con esa estrategia y
    las dos últimas son la media y la mediana de la columna tras aplicarla.
    No debe modificar el DataFrame original.
    """
    serie = df[columna]
    sin_nulos = serie.dropna()
    con_media = serie.fillna(serie.mean())
    con_mediana = serie.fillna(serie.median())
    return pd.DataFrame({
        "estrategia": ["eliminar filas", "rellenar con media", "rellenar con mediana"],
        "n_filas": [len(sin_nulos), len(con_media), len(con_mediana)],
        "media_resultante": [sin_nulos.mean(), con_media.mean(), con_mediana.mean()],
        "mediana_resultante": [sin_nulos.median(), con_media.median(), con_mediana.median()],
    })


def validar_calidad_usuarios(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recibe la tabla de usuarios y devuelve un DataFrame booleano con las
    mismas filas (y el mismo índice) que 'df' y una columna por regla. Un
    valor True significa que esa fila INCUMPLE la regla:
        'edad_nula'                   -> la edad es nula
        'edad_fuera_de_rango'         -> la edad es menor de 18 o mayor de 55
        'mas_seguidos_que_seguidores' -> 'seguidos' > 'seguidores'
        'fila_duplicada'              -> repite por completo una fila anterior
        'id_repetido'                 -> su 'id_usuario' ya apareció antes
    """
    resultado = pd.DataFrame(index=df.index)
    resultado["edad_nula"] = df["edad"].isnull()
    resultado["edad_fuera_de_rango"] = (df["edad"] < 18) | (df["edad"] > 55)
    resultado["mas_seguidos_que_seguidores"] = df["seguidos"] > df["seguidores"]
    resultado["fila_duplicada"] = df.duplicated()
    resultado["id_repetido"] = df.duplicated(subset=["id_usuario"])
    return resultado


# ============================================================
# BLOQUE 4 — Pandas avanzado
# ============================================================

def analizar_categorias(df: pd.DataFrame, columnas: list[str]) -> pd.DataFrame:
    """
    Recibe un DataFrame y una lista de nombres de columnas de texto.
    Devuelve una NUEVA tabla con una fila por columna (el índice es el
    nombre de la columna) y las columnas:
        'tipo'                  -> tipo de dato tras convertirla a categórica
        'categorias'            -> número de categorías
        'memoria_antes_bytes'   -> memoria de la columna original (contando
                                   el contenido de los textos)
        'memoria_despues_bytes' -> memoria de la columna ya categórica
        'ahorro_bytes'          -> memoria antes menos memoria después
    No debe modificar el DataFrame original.
    """
    filas = {}
    for columna in columnas:
        memoria_antes = int(df[columna].memory_usage(deep=True, index=False))
        categorica = df[columna].astype("category")
        memoria_despues = int(categorica.memory_usage(deep=True, index=False))
        filas[columna] = {
            "tipo": str(categorica.dtype),
            "categorias": int(len(categorica.cat.categories)),
            "memoria_antes_bytes": memoria_antes,
            "memoria_despues_bytes": memoria_despues,
            "ahorro_bytes": memoria_antes - memoria_despues,
        }
    return pd.DataFrame.from_dict(filas, orient="index")


def tabla_engagement_ciudad_contenido(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recibe un DataFrame con las columnas 'tipo_contenido', 'ciudad' y
    'engagement_rate'. Devuelve una tabla dinámica con 'tipo_contenido' en
    las filas, 'ciudad' en las columnas y el engagement medio como valor;
    las combinaciones sin publicaciones valen 0.
    """
    return pd.pivot_table(
        df,
        values="engagement_rate",
        index="tipo_contenido",
        columns="ciudad",
        aggfunc="mean",
        fill_value=0,
    )


def comparar_formatos(df: pd.DataFrame, ruta_base) -> dict[str, float]:
    """
    Guarda 'df' en '<ruta_base>.csv' (sin índice) y en '<ruta_base>.parquet'
    (compresión snappy, sin índice) y devuelve un diccionario con:
        'csv_bytes'     -> tamaño en bytes del CSV
        'parquet_bytes' -> tamaño en bytes del Parquet
        'ratio'         -> parquet_bytes / csv_bytes, con 3 decimales
    Si no hay motor de Parquet instalado, se propaga el ImportError.
    """
    ruta_csv = f"{ruta_base}.csv"
    ruta_parquet = f"{ruta_base}.parquet"
    os.makedirs(os.path.dirname(os.path.abspath(ruta_csv)), exist_ok=True)
    df.to_csv(ruta_csv, index=False)
    df.to_parquet(ruta_parquet, compression="snappy", index=False)
    csv_bytes = os.path.getsize(ruta_csv)
    parquet_bytes = os.path.getsize(ruta_parquet)
    return {
        "csv_bytes": csv_bytes,
        "parquet_bytes": parquet_bytes,
        "ratio": round(parquet_bytes / csv_bytes, 3),
    }


# ============================================================
# BLOQUE 5 — Visualización y Faker
# ============================================================

def exportar_figuras_avanzadas(figuras: dict[str, Any], carpeta) -> list[str]:
    """
    Recibe un diccionario {nombre: figura de Plotly} y una carpeta. Guarda
    cada figura en '<carpeta>/<nombre>.html' (creando la carpeta si no
    existe) y devuelve la lista con las rutas de los ficheros creados, en el
    mismo orden que el diccionario.
    """
    carpeta = os.fspath(carpeta)
    os.makedirs(carpeta, exist_ok=True)
    rutas = []
    for nombre, figura in figuras.items():
        ruta = os.path.join(carpeta, f"{nombre}.html")
        figura.write_html(ruta)
        rutas.append(ruta)
    return rutas


def ampliar_dataset_avanzado(df_usuarios: pd.DataFrame, n: int, seed: int = 42) -> pd.DataFrame:
    """
    Igual que la ampliación básica, pero REPRODUCIBLE: con la misma 'seed'
    debe devolver siempre exactamente los mismos usuarios. Devuelve los
    usuarios originales (sin cambios, al principio) seguidos de 'n' usuarios
    ficticios con Faker en español que cumplen:
      - 'id_usuario' único, continuando desde el máximo existente + 1
      - mismas columnas, orden y tipos de dato que la tabla original
      - 'tipo_cuenta': 60% free, 30% premium y 10% creator
      - 'seguidores' coherentes con el tipo de cuenta (creator: 1000-50000;
        resto: 10-5000), 'edad' entre 18 y 55
      - 'fecha_registro' entre 2018-01-01 y 2024-06-01 (formato AAAA-MM-DD)
      - 'ciudad', 'pais' y 'genero' elegidos entre los valores existentes
    Con n <= 0 devuelve una copia de la tabla original.
    """
    if n <= 0:
        return df_usuarios.copy()

    from faker import Faker

    fake = Faker("es_ES")
    fake.seed_instance(seed)
    azar = random.Random(seed)
    id_inicio = int(df_usuarios["id_usuario"].max()) + 1
    ciudades = df_usuarios["ciudad"].dropna().unique().tolist() or ["Madrid"]
    paises = df_usuarios["pais"].dropna().unique().tolist() or ["Espana"]
    generos = df_usuarios["genero"].dropna().unique().tolist() or ["M", "F"]
    activo_es_bool = pd.api.types.is_bool_dtype(df_usuarios["activo"])

    filas = []
    for indice in range(n):
        tipo = azar.choices(["free", "premium", "creator"], weights=[60, 30, 10])[0]
        seguidores = azar.randint(1000, 50000) if tipo == "creator" else azar.randint(10, 5000)
        activo = azar.random() < 0.8
        filas.append({
            "id_usuario": id_inicio + indice,
            "nombre": fake.first_name(),
            "apellidos": f"{fake.last_name()} {fake.last_name()}",
            "edad": azar.randint(18, 55),
            "ciudad": azar.choice(ciudades),
            "pais": azar.choice(paises),
            "genero": azar.choice(generos),
            "fecha_registro": fake.date_between(date(2018, 1, 1), date(2024, 6, 1)).isoformat(),
            "tipo_cuenta": tipo,
            "seguidores": seguidores,
            "seguidos": azar.randint(20, 1000),
            "publicaciones_totales": azar.randint(0, 500),
            "activo": activo if activo_es_bool else str(activo),
            "bio": fake.catch_phrase(),
        })

    nuevos = pd.DataFrame(filas, columns=df_usuarios.columns)
    nuevos = nuevos.astype(df_usuarios.dtypes.to_dict())
    return pd.concat([df_usuarios, nuevos], ignore_index=True)
