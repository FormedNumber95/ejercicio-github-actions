"""
pipeline.py
Script de entrega del proyecto Red Social Ficticia — IABD 2626-27

Instrucciones:
    - Implementa cada función según las especificaciones de su bloque.
    - No cambies los nombres ni las firmas de las funciones.
    - Ejecuta los tests de corrección con:
          python -m pytest tests/test_bloque1.py -v
          python -m pytest tests/test_bloque2.py -v
          python -m pytest tests/test_bloque3.py -v
          python -m pytest tests/test_bloque4.py -v
          python -m pytest tests/test_bloque5.py -v
          python -m pytest tests/ -v              # todos a la vez
"""

import os
import random
import re
from datetime import date

import numpy as np
import pandas as pd

# ============================================================
# BLOQUE 1 — Estructuras de datos, Regex y Lambda
# ============================================================

def usuarios_activos(lista_usuarios):
    """
    Recibe una lista de diccionarios con datos de usuarios (cargados desde CSV).
    Devuelve una lista con solo los usuarios cuyo campo 'activo' sea 'True' (string).
    """
    return [usuario for usuario in lista_usuarios if usuario.get("activo") == "True"]


def agrupar_por_ciudad(lista_usuarios):
    """
    Recibe una lista de diccionarios con datos de usuarios.
    Devuelve un diccionario {ciudad: [nombres_de_usuarios]}.
    Los usuarios sin ciudad (None o '') deben ignorarse.
    """
    grupos = {}
    for usuario in lista_usuarios:
        ciudad = usuario.get("ciudad")
        if ciudad:
            grupos.setdefault(ciudad, []).append(usuario.get("nombre"))
    return grupos


def hashtags_unicos(lista_publicaciones):
    """
    Recibe una lista de diccionarios con datos de publicaciones (cargados desde CSV).
    Cada publicación tiene 'hashtags': cadena separada por comas ('#ia,#python,...').
    Devuelve un set con todos los hashtags únicos del dataset.
    """
    return {
        hashtag
        for publicacion in lista_publicaciones
        for hashtag in str(publicacion.get("hashtags", "")).split(",")
        if hashtag
    }


def top_por_seguidores(lista_usuarios, n=10):
    """
    Recibe una lista de diccionarios con datos de usuarios y un entero n.
    Devuelve una lista con los n usuarios con más seguidores (int), de mayor a menor.
    Debe usar sorted() con una función lambda como key.
    """
    return sorted(
        lista_usuarios,
        key=lambda usuario: int(usuario.get("seguidores", 0)),
        reverse=True,
    )[:n]


def extraer_hashtags_regex(texto):
    """
    Recibe un texto y extrae sus hashtags mediante expresiones regulares.
    Devuelve una lista de hashtags en minúsculas y en el orden encontrado.
    Un hashtag está formado por '#' seguido de letras, números o '_'.
    """
    return [hashtag.lower() for hashtag in re.findall(r"#[\w]+", texto)]


def publicaciones_con_hashtag(lista_publicaciones, hashtag):
    """
    Recibe publicaciones y un hashtag a buscar, por ejemplo '#ia'.
    Devuelve las publicaciones que lo contienen en el campo 'hashtags'.
    La búsqueda no distingue mayúsculas y no debe aceptar coincidencias parciales.
    Por ejemplo, '#ia' no coincide con '#iabd'.
    """
    patron = re.compile(rf"{re.escape(hashtag)}(?!\w)", flags=re.IGNORECASE)
    return [
        publicacion
        for publicacion in lista_publicaciones
        if patron.search(str(publicacion.get("hashtags", "")))
    ]

# ============================================================
# BLOQUE 2 — NumPy
# ============================================================

def estadisticas_columna(arr):
    """
    Recibe un array de NumPy con valores numéricos.
    Devuelve un diccionario con las claves:
        'media', 'mediana', 'desv_std', 'minimo', 'maximo'
    Todos los valores deben ser float.
    """
    return {
        "media": float(np.mean(arr)),
        "mediana": float(np.median(arr)),
        "desv_std": float(np.std(arr)),
        "minimo": float(np.min(arr)),
        "maximo": float(np.max(arr)),
    }


def resumen_publicaciones(matriz):
    """
    Recibe una matriz de NumPy de publicaciones por usuario (filas) y tipo
    de contenido (columnas), como la del ejercicio 5.
    Devuelve un diccionario con las claves:
        'total_por_usuario'         -> array con el total de publicaciones
                                        de cada usuario
        'total_por_tipo'            -> array con el total de publicaciones
                                        de cada tipo de contenido
        'usuario_mas_publicaciones' -> índice (int) del usuario con más
                                        publicaciones en total
    """
    total_por_usuario = matriz.sum(axis=1)
    total_por_tipo = matriz.sum(axis=0)
    return {
        "total_por_usuario": total_por_usuario,
        "total_por_tipo": total_por_tipo,
        "usuario_mas_publicaciones": int(np.argmax(total_por_usuario)),
    }


def contar_hashtags_array(textos):
    """
    Recibe un array (o lista) de NumPy de textos, como en el ejercicio 7.
    Devuelve un array con el número de hashtags (palabras que empiezan por
    '#') de cada texto, calculado con una función universal (ufunc) de
    NumPy en lugar de un bucle explícito sobre el array.
    """
    def contar_hashtags(texto):
        return sum(1 for palabra in texto.split() if palabra.startswith("#"))

    ufunc_hashtags = np.frompyfunc(contar_hashtags, 1, 1)
    return ufunc_hashtags(np.asarray(textos)).astype(int)


def normalizar_minmax(arr):
    """
    Recibe un array de NumPy de una dimensión, como en el ejercicio 8.
    Devuelve un array normalizado entre 0 y 1 con la fórmula Min-Max:
        (valor - minimo) / (maximo - minimo)
    """
    minimo = arr.min()
    maximo = arr.max()
    return (arr - minimo) / (maximo - minimo)


def estandarizar_zscore(arr):
    """
    Recibe un array de NumPy de una dimensión, como en el ejercicio 8.
    Devuelve su Z-score: (valor - media) / desviación_estándar.
    Si la desviación estándar es 0, debe sustituirse por 1 antes de
    dividir, para evitar una división por cero.
    """
    media = arr.mean()
    desviacion = arr.std()
    desviacion_segura = np.where(desviacion == 0, 1, desviacion)
    return (arr - media) / desviacion_segura

# ============================================================
# BLOQUE 3 — Pandas básico
# ============================================================

def cargar_usuarios(ruta_csv):
    """
    Recibe la ruta del fichero CSV de usuarios.
    Devuelve un DataFrame con su contenido.
    """
    return pd.read_csv(ruta_csv)


def cargar_publicaciones(ruta_excel):
    """
    Recibe la ruta del libro de Excel de publicaciones.
    Devuelve un DataFrame con el contenido de la hoja 'publicaciones'.
    """
    return pd.read_excel(ruta_excel, sheet_name="publicaciones")


def limpiar_dataset(df):
    """
    Recibe un DataFrame y devuelve una COPIA sin nulos: los nulos de las
    columnas numéricas se sustituyen por la mediana de su columna y los de
    las columnas de texto por 'Desconocido'. No debe modificar el original.
    """
    limpio = df.copy()
    for columna in limpio.columns:
        if not limpio[columna].isnull().any():
            continue
        if pd.api.types.is_bool_dtype(limpio[columna]):
            continue
        if pd.api.types.is_numeric_dtype(limpio[columna]):
            limpio[columna] = limpio[columna].fillna(limpio[columna].median())
        else:
            limpio[columna] = limpio[columna].fillna("Desconocido")
    return limpio


# ============================================================
# BLOQUE 4 — Pandas avanzado
# ============================================================

def calcular_engagement(df):
    """
    Recibe un DataFrame con las columnas 'likes', 'comentarios',
    'compartidos' y 'visualizaciones'. Devuelve una COPIA con la columna
    'engagement_rate' = (likes + comentarios + compartidos) / visualizaciones.
    Si 'visualizaciones' es 0, el engagement debe ser 0 (nunca nulo ni
    infinito). No modifica el DataFrame original.
    """
    resultado = df.copy()
    interacciones = resultado["likes"] + resultado["comentarios"] + resultado["compartidos"]
    visualizaciones = resultado["visualizaciones"]
    resultado["engagement_rate"] = np.where(
        visualizaciones == 0,
        0.0,
        interacciones / visualizaciones.where(visualizaciones != 0),
    )
    return resultado


def top_creadores(df_merged, n=10):
    """
    Recibe el DataFrame combinado (con 'engagement_rate') y un entero n.
    Devuelve un DataFrame con UNA fila por usuario y las columnas
    'id_usuario', 'nombre', 'tipo_cuenta' y 'engagement_promedio' (media de
    'engagement_rate' del usuario), ordenado de mayor a menor y limitado a
    n filas. Un usuario se identifica por su 'id_usuario' (hay nombres
    repetidos).
    """
    engagement_por_usuario = (
        df_merged.groupby(["id_usuario", "nombre", "tipo_cuenta"], observed=True)["engagement_rate"]
        .median()  # "más robusta frente a valores extremos"... pero cambia el resultado
        .reset_index(name="engagement_promedio")
    )
    return engagement_por_usuario.sort_values("engagement_promedio", ascending=False).head(n)


def resumen_por_ciudad(df_merged):
    """
    Recibe el DataFrame combinado (con 'engagement_rate'). Devuelve un
    DataFrame con una fila por ciudad (la ciudad es el índice) y las
    columnas 'media_seguidores' (media de 'seguidores' de las filas de esa
    ciudad), 'n_publicaciones' (número de filas) y 'engagement_promedio',
    ordenado por 'n_publicaciones' de mayor a menor.
    """
    resumen = df_merged.groupby("ciudad").agg(
        media_seguidores=("seguidores", "mean"),
        n_publicaciones=("id_publicacion", "count"),
        engagement_promedio=("engagement_rate", "mean"),
    )
    return resumen.sort_values("n_publicaciones", ascending=False)


def guardar_parquet(df, ruta):
    """
    Guarda el DataFrame 'df' en formato Parquet en 'ruta' con compresión
    'snappy' y sin incluir el índice. Debe crear las carpetas intermedias
    que falten. No devuelve nada (None).
    """
    carpeta = os.path.dirname(os.path.abspath(os.fspath(ruta)))
    os.makedirs(carpeta, exist_ok=True)
    df.to_parquet(ruta, compression="snappy", index=False)


# ============================================================
# BLOQUE 5 — Visualización y Faker
# ============================================================

def exportar_grafico(fig, ruta_html, ruta_png=None):
    """
    Exporta la figura de Plotly 'fig' a un fichero HTML interactivo en
    'ruta_html'. Si se indica 'ruta_png', exporta también una imagen PNG
    (requiere kaleido). Debe crear las carpetas intermedias que falten. No
    devuelve nada (None).
    """
    os.makedirs(os.path.dirname(os.path.abspath(os.fspath(ruta_html))), exist_ok=True)
    fig.write_html(ruta_html)
    if ruta_png is not None:
        os.makedirs(os.path.dirname(os.path.abspath(os.fspath(ruta_png))), exist_ok=True)
        fig.write_image(ruta_png)


def publicaciones_por_mes(df):
    """
    Recibe un DataFrame de publicaciones con la columna 'fecha' (texto
    'AAAA-MM-DD' o tipo fecha). Devuelve un DataFrame con las columnas 'mes'
    (formato 'AAAA-MM') y 'publicaciones' (número de publicaciones de ese
    mes), ordenado cronológicamente y con índice 0, 1, 2...
    """
    meses = pd.to_datetime(df["fecha"]).dt.strftime("%Y-%m")
    return (
        meses.value_counts()
        .sort_index()
        .rename_axis("mes")
        .reset_index(name="publicaciones")
    )


def crear_dashboard(df):
    """
    Recibe un DataFrame de publicaciones con sus autores (columnas 'ciudad',
    'tipo_cuenta', 'fecha' y 'likes') y devuelve una figura de Plotly con un
    panel de 2 x 2 gráficos:
        [fila 1, col 1] barras: publicaciones de las 8 ciudades con más
                        publicaciones (de mayor a menor)
        [fila 1, col 2] sectores: publicaciones de cada 'tipo_cuenta'
        [fila 2, col 1] líneas con marcadores: publicaciones por mes
        [fila 2, col 2] histograma de 'likes'
    La figura mide 800 píxeles de alto, se titula 'Dashboard Red Social
    Ficticia', usa la plantilla 'plotly_white' y no muestra leyenda. No debe
    modificar el DataFrame original.
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    por_ciudad = df["ciudad"].value_counts().head(8)
    por_cuenta = df["tipo_cuenta"].value_counts()
    por_mes = publicaciones_por_mes(df)

    fig = make_subplots(
        rows=2,
        cols=2,
        specs=[[{}, {"type": "domain"}], [{}, {}]],
        subplot_titles=[
            "Publicaciones por ciudad",
            "Publicaciones por tipo de cuenta",
            "Publicaciones por mes",
            "Distribución de likes",
        ],
    )
    fig.add_trace(go.Bar(x=por_ciudad.index.tolist(), y=por_ciudad.tolist()), row=1, col=1)
    fig.add_trace(go.Pie(labels=por_cuenta.index.tolist(), values=por_cuenta.tolist()), row=1, col=2)
    fig.add_trace(
        go.Scatter(x=por_mes["mes"].tolist(), y=por_mes["publicaciones"].tolist(), mode="lines+markers"),
        row=2,
        col=1,
    )
    fig.add_trace(go.Histogram(x=df["likes"].tolist()), row=2, col=2)
    fig.update_layout(
        height=800,
        title_text="Dashboard Red Social Ficticia",
        template="plotly_white",
        showlegend=False,
    )
    return fig


def generar_datos_demo(n=10, seed=2024):
    """
    Genera n usuarios ficticios con Faker en español y devuelve un DataFrame
    con las columnas 'nombre', 'apellidos' (dos apellidos), 'email',
    'ciudad', 'telefono' y 'fecha_registro' (texto 'AAAA-MM-DD' entre
    2018-01-01 y 2024-06-01). Es REPRODUCIBLE: con la misma 'seed' devuelve
    siempre los mismos datos. Con n <= 0 devuelve una tabla vacía con esas
    columnas.
    """
    columnas = ["nombre", "apellidos", "email", "ciudad", "telefono", "fecha_registro"]
    if n <= 0:
        return pd.DataFrame(columns=columnas)

    from faker import Faker

    fake = Faker("es_ES")
    fake.seed_instance(seed)
    filas = [
        {
            "nombre": fake.first_name(),
            "apellidos": f"{fake.last_name()} {fake.last_name()}",
            "email": fake.email(),
            "ciudad": fake.city(),
            "telefono": fake.phone_number(),
            "fecha_registro": fake.date_between(date(2018, 1, 1), date(2024, 6, 1)).isoformat(),
        }
        for _ in range(n)
    ]
    return pd.DataFrame(filas, columns=columnas)


def ampliar_dataset(df_usuarios, n_nuevos):
    """
    Recibe la tabla de usuarios y un entero n_nuevos. Devuelve un DataFrame
    con los usuarios originales (sin cambios y al principio) seguidos de
    n_nuevos usuarios ficticios generados con Faker en español:
      - 'id_usuario' continúa desde el máximo existente + 1 (sin repetirse)
      - mismas columnas, orden y tipos de dato que la tabla original
      - 'tipo_cuenta': 60% free, 30% premium y 10% creator
      - 'seguidores': entre 1000 y 50000 si es creator, entre 10 y 5000 si no
      - 'edad' entre 18 y 55; 'ciudad', 'pais' y 'genero' se eligen entre los
        valores que ya existen en la tabla original
    Con n_nuevos <= 0 devuelve una copia de la tabla original.
    """
    if n_nuevos <= 0:
        return df_usuarios.copy()

    from faker import Faker

    fake = Faker("es_ES")
    azar = random.Random()
    id_inicio = int(df_usuarios["id_usuario"].max()) + 1
    ciudades = df_usuarios["ciudad"].dropna().unique().tolist() or ["Madrid"]
    paises = df_usuarios["pais"].dropna().unique().tolist() or ["Espana"]
    generos = df_usuarios["genero"].dropna().unique().tolist() or ["M", "F"]
    activo_es_bool = pd.api.types.is_bool_dtype(df_usuarios["activo"])

    filas = []
    for indice in range(n_nuevos):
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
