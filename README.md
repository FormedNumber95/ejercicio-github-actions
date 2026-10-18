# Proyecto: Análisis de una Red Social Ficticia

> **Curso de Especialización en Inteligencia Artificial y Big Data (IABD) — Curso 2026/2027**  
> **Módulo:** Programación y Análisis de Datos con Python

---

## 1. ¿De qué trata este proyecto?

En este proyecto construirás un **pipeline de ingeniería y análisis de datos en Python** de principio a fin, trabajando sobre una red social ficticia: perfiles de usuarios, publicaciones y un grafo de conexiones de seguidores. Los datos son inventados; no hay datos personales reales.

El proyecto es **incremental y por fases**: cada fase corresponde a un **bloque** (fase 1 = Bloque 1, etc.). A medida que avanza el curso, el profesorado **libera** el material de la siguiente fase y aparece en tu carpeta del proyecto (un cuaderno nuevo en `notebooks/`, nuevas funciones en `scripts/` y sus tests en `tests/`). **Lo que ves en esas carpetas es lo que tienes que hacer ahora**; el resto llegará más adelante.

```text
  Apuntes de clase        Cuaderno del bloque         Funciones en                 Tests
  (teoría)          ──►   (práctica guiada)     ──►   scripts/pipeline.py    ──►   (pytest)
                          notebooks/                  (código limpio)              tests/
```

| Bloque | Tema | ¿Tiene entrega con tests? |
|---|---|---|
| 1 | Estructuras de datos, expresiones regulares y `lambda` (solo librería estándar) | Sí |
| 2 | NumPy | Sí |
| 3 | Pandas básico | Sí |
| 4 | Pandas avanzado, agrupaciones y Parquet | Sí |
| 5 | Gráficos con Plotly y datos ficticios con Faker | Sí |
| 6 | Cierre del proyecto (mezcla los cinco bloques) | No: se entrega el cuaderno ejecutado |

---

## 2. ¿Qué hay en cada carpeta?

| Carpeta / archivo | ¿Para qué sirve? |
|---|---|
| `README.md` | Esta guía. |
| `pyproject.toml`, `.python-version` | Dependencias y versión de Python del proyecto (gestionadas con `uv`). |
| `data/` | Datos de partida (`usuarios.csv`, `publicaciones.csv`, `publicaciones.xlsx`, `conexiones.json`) y el script `setup_datos.py` que los genera. Aquí se guardarán también los ficheros que produzcan tus cuadernos. |
| `notebooks/` | **Tus cuadernos de trabajo** (`Bloque_01_…`, `Bloque_02_…`…). Solo aparecen los de las fases liberadas. |
| `scripts/pipeline.py` | **Tu archivo principal de entrega.** Ahí implementas las funciones de cada bloque. |
| `scripts/pipeline_avanzada.py` | Entrega **opcional** con los ejercicios avanzados (con tipado). |
| `tests/` | Pruebas automáticas (`pytest`) que comprueban tus funciones. **No las modifiques.** |
| `output_graficos/` | Se crea sola cuando los Bloques 5 y 6 exportan gráficos (`.html` y `.png`). |

---

## 3. Preparar el entorno (una sola vez)

### Paso 1: instalar las dependencias

Este proyecto usa [uv](https://docs.astral.sh/uv/). Abre una terminal en VS Code, en la carpeta `Proy_analisis_Red_Social_Ficticia/`, y ejecuta:

```powershell
uv sync
```

Crea el entorno virtual e instala `numpy`, `pandas`, `openpyxl`, `pyarrow`, `fastparquet`, `plotly`, `kaleido`, `faker` y `pytest`. Después, selecciona ese entorno como intérprete en VS Code y como kernel de los cuadernos.

Para ejecutar cualquier cosa dentro del entorno sin activarlo:

```powershell
uv run python data/setup_datos.py
uv run pytest tests -v
uv run jupyter lab
```

> Usa siempre el intérprete del entorno del proyecto. El `python` del sistema puede ser otra versión y no tener las librerías.

> **Windows y OneDrive:** si tu carpeta está en una ruta muy larga, el entorno puede quedar incompleto sin avisar. Mira [Problemas frecuentes](#problemas-frecuentes).

### Paso 2: comprobar los datos

Tienes que ver los cuatro ficheros en `data/`. Si falta alguno, genéralos **desde esta carpeta** (`Proy_analisis_Red_Social_Ficticia/`):

```powershell
uv run python data/setup_datos.py
```

Los datos se generan siempre iguales (semilla fija). Características que verás y con las que cuentan los ejercicios:

- `usuarios.csv` tiene valores vacíos en `edad`, `ciudad` y `bio`.
- Las publicaciones tienen vacíos en `likes` y `comentarios`.
- Hay **nombres repetidos**: un usuario se identifica por `id_usuario`, no por `nombre`.

---

## 4. Cómo se trabaja cada bloque

Cada bloque sigue **cuatro pasos**:

1. **Estudia** el tema en los apuntes de clase.
2. **Practica en el cuaderno.** Abre `notebooks/Bloque_0N_….ipynb`, ejecuta la primera celda (carga los datos) y resuelve los ejercicios **en orden**. Cada ejercicio es una celda que empieza por `# ─── Ejercicio N — Título ───`, con el enunciado en comentarios y las variables por completar (`None`, o funciones con `pass`). Sustituye esos huecos por tu código. El enunciado te dice **qué** se pide, no qué método usar: lo decides tú con lo aprendido.
3. **Entrega en `scripts/pipeline.py`.** Al final de cada cuaderno hay una tabla **Entrega** que indica qué función de `pipeline.py` corresponde a qué ejercicio. Traslada tu solución a esa función.
4. **Comprueba con los tests** (sección 5).

Después vienen los **ejercicios avanzados** (etiquetados `A.N`) y la **Entrega opcional** en `scripts/pipeline_avanzada.py`, con su propio test.

Consejos para el cuaderno:

- Ejecútalo **de arriba abajo**; al terminar, reinicia el kernel y usa «Ejecutar todo» para comprobar que funciona de principio a fin.
- Las rutas de los cuadernos son `../data/…`: se ejecutan con la carpeta `notebooks/` como directorio de trabajo (VS Code y Jupyter lo hacen así por defecto).
- Los ejemplos del enunciado marcados «(esto NO es la solución)» solo muestran el formato del resultado.

### Qué se pide en cada bloque

Las firmas exactas y el formato de retorno están en la tabla **Entrega** de cada cuaderno y los valida el test. Aquí, el resumen:

| Bloque | Cuaderno | Funciones en `pipeline.py` | Test |
|---|---|---|---|
| **1** | `Bloque_01_EstructurasDatos_Lambda` | `usuarios_activos`, `agrupar_por_ciudad`, `hashtags_unicos`, `top_por_seguidores`, `extraer_hashtags_regex`, `publicaciones_con_hashtag` | `test_bloque1.py` |
| **2** | `Bloque_02_NumPy` | `estadisticas_columna`, `resumen_publicaciones`, `contar_hashtags_array`, `normalizar_minmax`, `estandarizar_zscore` | `test_bloque2.py` |
| **3** | `Bloque_03_Pandas_Basico` | `cargar_usuarios`, `cargar_publicaciones`, `limpiar_dataset` | `test_bloque3.py` |
| **4** | `Bloque_04_Pandas_Avanzado` | `calcular_engagement`, `top_creadores`, `resumen_por_ciudad`, `guardar_parquet` | `test_bloque4.py` |
| **5** | `Bloque_05_Graficos_Faker` | `exportar_grafico`, `publicaciones_por_mes`, `crear_dashboard`, `generar_datos_demo`, `ampliar_dataset` | `test_bloque5.py` |
| **6** | `Bloque_06_Cierre_Proyecto` | *(ninguna)* | *(ninguno)* |

Reglas propias de cada bloque:

- **Bloque 1:** solo librería estándar (`csv`, `json`, `re`, `collections`, `functools`…). **Prohibido importar Pandas o NumPy.** Recuerda que un CSV lee todo como texto: convierte con `int()` / `float()` cuando toque.
- **Bloque 2:** cálculos **vectorizados**. Prohibido usar bucles `for` / `while` para calcular valores numéricos sobre arrays (solo para construir un array a partir de datos externos).
- **Bloques 3 y 4:** **no modifiques** los DataFrames que recibes (trabaja sobre `df.copy()`), controla las divisiones por cero y guarda Parquet con compresión `snappy`.
- **Bloque 5:** gráficos **solo con Plotly** (nada de `matplotlib`, `seaborn` ni `networkx`). Crea las carpetas de destino si no existen. Para exportar a PNG hace falta tener instalado Chrome o Chromium. Los datos de Faker deben ser **reproducibles** (misma semilla, mismo resultado).
- **Bloque 6:** cierre guiado del proyecto. Parte solo de los ficheros originales de `data/` y termina con un mini-informe: carga, limpieza, métrica de engagement, tres preguntas analíticas, tres gráficos y una conclusión breve. Se da por terminado entregando el cuaderno **con todas las celdas ejecutadas de arriba abajo** y comprobando que has generado los ficheros de su tabla «Entrega».

---

## 5. Comprobar tu entrega con los tests

Desde `Proy_analisis_Red_Social_Ficticia/`:

```powershell
uv run pytest tests/test_bloque1.py -v         # un bloque
uv run pytest tests -q                         # todo lo liberado
uv run pytest tests/*_avanzado.py -v           # solo los avanzados (opcional)
```

Cómo leer el resultado:

| Resultado | Qué significa |
|---|---|
| Muchos `FAILED` al empezar | Es lo normal: las funciones del esqueleto aún no hacen nada (`pass  # TODO`). Al implementarlas, pasarán. |
| `FAILED` con un `AssertionError` | Tu función no cumple lo pedido: lee el mensaje (valor esperado frente al obtenido) y repasa la tabla **Entrega**. |
| `ImportError` / `cannot import name …` | Has borrado o cambiado el nombre de una función. **No cambies nombres, parámetros ni orden** de las funciones. |
| `TypeError: 'NoneType' …` | La función devuelve `None` (sigue con `pass`) o no tiene `return`. |
| `SKIPPED` en el Bloque 5 | Tu entorno de Plotly está incompleto. **No es un aprobado**: mira [Problemas frecuentes](#problemas-frecuentes). |
| Todo en verde | Bloque superado. |

Tus funciones deben producir siempre el mismo resultado por mucho que las ejecutes (idempotencia) y no deben modificar los datos que reciben.

---

## 6. Ficheros que generan los cuadernos

Al avanzar, tus cuadernos crean estos ficheros. **No los borres mientras trabajes**: por ejemplo, el Bloque 5 necesita `data/dataset_procesado.parquet` del Bloque 4.

| Fichero | Lo genera |
|---|---|
| `data/publicaciones_limpio.csv` | Bloque 3, ejercicio 8 |
| `data/dataset_procesado.parquet` (y un `.csv` de comparación) | Bloque 4, ejercicio 8 |
| `data/usuarios_grande.csv` / `.parquet` | Bloque 5, ejercicio 8 |
| `output_graficos/*.html`, `*.png` | Bloques 5 y 6 |
| `data/dataset_cierre.parquet` | Bloque 6, ejercicio 3 |

> Si te falta `dataset_procesado.parquet`, vuelve a ejecutar el ejercicio 8 del Bloque 4. El Bloque 6 **no** depende de ninguno de ellos.

---

## Problemas frecuentes

| Síntoma | Causa y solución |
|---|---|
| `FileNotFoundError` al cargar `data/…` | Faltan los datos (`uv run python data/setup_datos.py` desde la carpeta del proyecto) o has ejecutado el cuaderno con otro directorio de trabajo (debe ser `notebooks/`). |
| `ModuleNotFoundError` de `numpy`, `pandas`, `plotly`… | Estás usando otro intérprete. Selecciona el entorno del proyecto en VS Code/Jupyter o ejecuta con `uv run`. |
| Tests del Bloque 5 **saltados**, o `ModuleNotFoundError: … plotly.graph_objs…` | **Rutas largas de Windows.** El entorno se creó dentro de una carpeta con ruta muy larga (p. ej. OneDrive) y Windows omitió ficheros sin avisar. Solución: crear el entorno en una ruta corta (ver más abajo). |
| `os error 396` al instalar con `uv` | Enlaces duros en carpetas sincronizadas. Define `UV_LINK_MODE=copy`. |
| No se exporta el PNG de una figura | `kaleido` necesita Chrome o Chromium instalado. El HTML se exporta igualmente. |

**Crear el entorno en una ruta corta (Windows, sin permisos de administrador):**

```powershell
$env:UV_PROJECT_ENVIRONMENT = "C:\venv_redsocial"
$env:UV_LINK_MODE = "copy"
uv sync
```

y selecciona `C:\venv_redsocial\Scripts\python.exe` como intérprete en VS Code y Jupyter. Para que `uv run` use siempre ese entorno, define esas dos variables como variables de entorno de usuario. Comprobación: `uv run pytest tests -q` no debe mostrar tests saltados.

---

## 7. Buenas prácticas

1. **Inmutabilidad:** nunca modifiques los DataFrames que recibe una función. Empieza con `df_copia = df.copy()`.
2. **Tipos de datos:** los CSV leídos con la librería estándar entregan **todo como texto**. Convierte explícitamente a `int` o `float`.
3. **Idempotencia:** tu función debe dar el mismo resultado ejecutada una o varias veces.
4. **No toques los tests ni las firmas:** si un test falla, arregla tu función, no el test.
5. **Trabaja en orden** y ejecuta los tests al terminar cada bloque, no solo al final.
6. **Un usuario se identifica por `id_usuario`**, nunca por `nombre` (hay nombres repetidos).

---

## 8. Testing y CI/CD con GitHub Actions

Además de los tests de cada bloque, el proyecto incluye una batería organizada por **tipos de test** (smoke, unitarios, esquema, valores, relaciones, integración, métricas, regresión y extremo a extremo) y **workflows de GitHub Actions** que lanzan unos u otros según la rama (`feature/*`, `develop`, `main`) y los ficheros modificados.

Toda la información y la práctica guiada están en [docs/GUIA_TESTING_CICD.md](docs/GUIA_TESTING_CICD.md).

```powershell
uv run pytest -m smoke          # un tipo de test
uv run pytest                   # toda la batería
uv run ruff check .             # calidad de código
```
