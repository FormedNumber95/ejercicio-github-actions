# Testing y CI/CD con GitHub Actions

> Proyecto: Red Social Ficticia · Módulo PRIA · IABD 2026/2027

En esta práctica vas a trabajar con **distintos tipos de tests** sobre el pipeline que has construido durante el curso y a ver cómo **GitHub Actions** lanza unos u otros según la **rama** en la que hagas push y según **qué ficheros** cambies.

### Ramas del repositorio

| Rama | Contenido |
|---|---|
| `main` | Versión estable: pipeline, batería de tests y workflows |
| `develop` | Integración del trabajo de todo el equipo (parte igual que `main`) |
| `feature/engagement-por-contenido` | Una función nueva con sus tests (tarea 4.1) |
| `feature/ejemplo-regresion` | Un cambio que pasa los unitarios pero no la regresión (tarea 4.3) |
| `feature/contratos-datos` | Contratos de datos con pandera (tarea 4.6) |
| `feature/modelo-alcance` | Modelo de clasificación con su cuaderno, sus tests y su CI. Parte de `feature/contratos-datos` (tarea 4.7) |
| `feature/ficheros-grandes` | Material de la **próxima práctica** (Git LFS): `docs/GUIA_FICHEROS_GRANDES.md` |

---

## 1. Tipos de test del proyecto

Cada tipo de test está en su carpeta y tiene un **marcador** de pytest. Con `-m` eliges qué tipo ejecutar.

| Tipo | Carpeta / fichero | Marcador | ¿Qué comprueba? | Ejemplo |
|---|---|---|---|---|
| Smoke | `tests/smoke/` | `smoke` | Que el proyecto "arranca": Python, librerías, imports, ficheros de datos | ¿Existe `data/usuarios.csv`? |
| Unitarios | `tests/test_bloque*.py`, `tests/test_parametrizados.py` | `unit` | Cada función por separado, con datos pequeños inventados | `calcular_engagement` da 0.26 para (100, 20, 10, 500) |
| Esquema | `tests/datos/test_esquema.py` | `esquema` | Estructura de los datos: columnas, orden y tipos | `edad` es `float64` |
| Valores | `tests/datos/test_valores.py` | `valores` | Rangos y dominios válidos | `edad` entre 18 y 55; `tipo_cuenta` ∈ {free, premium, creator} |
| Relaciones | `tests/datos/test_relaciones.py` | `relaciones` | Integridad referencial entre tablas | Toda publicación es de un usuario existente |
| Integración | `tests/integracion/` | `integracion` | Varias funciones encadenadas sobre los datos reales | carga → limpieza → merge → engagement → Parquet |
| Métricas | `tests/metricas/` | `metricas` | Indicadores con umbral: calidad, negocio y rendimiento | ≤ 10 % de nulos por columna; engagement en < 1 s con 200 000 filas |
| Regresión | `tests/regresion/` | `regresion` | Que los resultados no cambian sin querer respecto a una referencia | El top 5 de creadores sigue siendo el mismo |
| Extremo a extremo | `tests/e2e/` | `e2e` | El proceso completo: generar datos → pipeline → entregables | Se generan el Parquet y el dashboard HTML |
| Contratos *(rama `feature/contratos-datos`)* | `tests/contratos/` | `contratos` | Que los datos cumplen sus contratos (pandera) en la entrada y la salida del pipeline, y que los contratos **rechazan** datos incorrectos | Una edad de 150 detiene el pipeline |
| Modelo *(rama `feature/modelo-alcance`)* | `tests/modelo/` | `modelo` | Que el modelo guardado rinde lo suficiente, se reproduce, no tiene fuga de datos y se comporta con lógica | ROC AUC ≥ 0.80 y mejor que el modelo trivial |
| Cuadernos | `notebooks/*.ipynb` | — (`--nbmake`) | Que los 6 cuadernos se ejecutan de principio a fin | `pytest --nbmake notebooks` |
| Calidad de código | todo el proyecto | — (`ruff`) | Estilo y errores comunes | imports sin usar, líneas demasiado largas |
| Cobertura | `scripts/` | — (`--cov`) | Qué porcentaje del código ejecutan los tests | mínimo 90 % en develop y 95 % en main |

**Pirámide de tests:** muchos tests unitarios (rápidos y baratos), menos de integración y muy pocos de extremo a extremo (lentos, pero los más realistas). Por eso en las ramas de trabajo solo se lanzan los rápidos.

---

## 2. Comandos en tu ordenador

```powershell
uv sync                                         # entorno con las dependencias de desarrollo
uv run pytest                                   # toda la batería (≈ 30 s)
uv run pytest -m smoke                          # un tipo
uv run pytest -m "esquema or valores or relaciones"   # varios tipos
uv run pytest -m "not e2e"                      # todo menos los e2e
uv run pytest --markers                         # lista de marcadores
uv run pytest tests/test_parametrizados.py -v   # ver cada caso parametrizado
uv run pytest --cov --cov-report=term           # con cobertura
uv run ruff check .                             # calidad de código (--fix corrige lo automático)
uv run pytest --nbmake notebooks                # ejecutar los cuadernos (≈ 1,5 min)
uv run python tests/regresion/actualizar_referencia.py   # solo si un cambio de resultados es intencionado
```

---

## 3. Ramas y workflows: qué se lanza en cada caso

```text
 feature/*  ──push──▶  [1] lint · smoke → unitarios                         (≈ 1 min)
     │
     ▼ pull request
 develop    ──push / PR──▶  [2] lint · smoke → unitarios | datos | integración
     │                                       → cobertura ≥ 90 %             (≈ 2 min)
     ▼ pull request
 main       ──PR──▶    [3] lint · smoke → batería completa en Linux y Windows
            ──push──▶  [3] lo anterior + cuadernos (nbmake) + gráficos       (≈ 4 min)

 cualquier rama, si cambia data/ ──▶ [4] esquema | valores | relaciones | métricas
 cualquier rama, si cambia el modelo o lo que lo alimenta ──▶ [6] tests del modelo → reentrenar
 cambios solo en docs/ o *.md   ──▶ no se lanza nada (paths-ignore)
 pestaña Actions → Run workflow  ──▶ [5] eliges rama, tipo de test y sistema operativo
```

| Workflow | Fichero | Se dispara con | Ejecuta |
|---|---|---|---|
| 1 · Feature | `.github/workflows/ci-feature.yml` | push a `feature/**` | ruff, smoke y, si pasa, unitarios |
| 2 · Develop | `.github/workflows/ci-develop.yml` | push o PR a `develop` | ruff, smoke, matriz de unitarios/datos/integración, cobertura ≥ 90 % con informe |
| 3 · Main | `.github/workflows/ci-main.yml` | PR o push a `main` | todo en Linux y Windows con cobertura ≥ 95 %; en push, también los cuadernos |
| 4 · Calidad de datos | `.github/workflows/calidad-datos.yml` | push o PR que cambie `data/**` o los tests de datos | esquema, valores, relaciones y métricas |
| 5 · Manual | `.github/workflows/manual.yml` | botón *Run workflow* | el tipo de test y el sistema que elijas |
| 6 · Modelo *(rama `feature/modelo-alcance`)* | `.github/workflows/modelo.yml` | push o PR que cambie `modelos/`, el código o el cuaderno del modelo, sus tests o `data/` | tests del modelo y reentrenamiento que comprueba que se obtienen los mismos parámetros y métricas |
| 7 · Ficheros grandes *(rama `feature/ficheros-grandes`)* | `.github/workflows/ficheros-grandes.yml` | cualquier push o PR | ningún fichero de más de 2 MB fuera de Git LFS (próxima práctica) |

Las ramas `feature/contratos-datos` y `feature/modelo-alcance` también amplían los workflows 1, 2, 4 y 5 con sus nuevos tipos de test. Al integrarlas en `develop`, esas ampliaciones pasan a formar parte del proyecto.

Conceptos de GitHub Actions que aparecen en los workflows:

| Concepto | Dónde verlo | Para qué sirve |
|---|---|---|
| `on.push.branches` / `on.pull_request.branches` | todos | elegir en qué ramas se lanza |
| `paths` / `paths-ignore` | 1–4 | lanzar (o no) según los ficheros modificados |
| `workflow_dispatch` con `inputs` | 5 | lanzarlo a mano con parámetros |
| `needs` | 1–3 | encadenar jobs: si el smoke falla, el resto no se ejecuta |
| `strategy.matrix` | 2–4 | repetir un job con distintos valores (tipos de test, sistemas operativos) |
| `if:` | 3 | ejecutar un job solo en push y no en los PR |
| `concurrency` | 1–4 | cancelar la ejecución anterior si haces otro push a la misma rama |
| `upload-artifact` | 2–3 | descargar informes (JUnit, cobertura HTML, gráficos) desde la web |
| `$GITHUB_STEP_SUMMARY` | 2 | mostrar la tabla de cobertura en la página del workflow |
| Acción compuesta | `.github/actions/preparar-entorno` | reutilizar los pasos de instalar uv y las dependencias |

---

## 4. Práctica guiada

### 4.0 Preparación

1. Sigue `INSTRUCCIONES.md` (junto al fichero `red_social_ficticia.bundle`) para reconstruir el repositorio con todas sus ramas y subirlo a tu GitHub.
2. En tu copia de trabajo, prepara el entorno y protege los cuadernos para que nunca se suban con salidas:
   ```powershell
   uv sync
   uv run nbstripout --install     # limpia las salidas de los .ipynb al hacer commit
   uv run pytest -m smoke
   ```
3. Abre la pestaña **Actions** y observa qué workflows se han lanzado para cada rama y cuáles no.

### 4.1 Una feature con sus tests (rama `feature/engagement-por-contenido`)

La rama añade la función `engagement_por_contenido` a `scripts/pipeline.py` con tests unitarios parametrizados.

1. Comprueba en Actions que en esta rama **solo** se ha lanzado el workflow 1.
2. Abre un **pull request** de la feature hacia `develop`. ¿Qué workflow se lanza ahora? ¿Qué jobs nuevos aparecen?
3. Descarga el artefacto `cobertura-html` y localiza las líneas de `pipeline.py` sin cubrir.
4. Haz el merge y observa el push a `develop`.

### 4.2 Ver un test en rojo

1. Crea la rama `feature/<tu-nombre>-fallo` desde `develop`.
2. Cambia `calcular_engagement` para que no sume los `compartidos`. Haz commit y push.
3. ¿Qué job falla? Lee el mensaje de error en el log y corrígelo con otro commit.

### 4.3 Los unitarios pasan, pero la regresión no (rama `feature/ejemplo-regresion`)

Esta rama cambia `top_creadores` para usar la **mediana** en lugar de la **media**. El cambio parece inofensivo y los tests unitarios siguen pasando.

1. Súbela y comprueba que el workflow 1 queda en verde.
2. Lanza el workflow **5 · Manual** en esa rama con `tipo = regresion`. ¿Qué resultado ha cambiado?
3. Abre un PR de esa rama hacia `main`: el workflow 3 la bloquea.
4. Discute en clase cuándo es correcto actualizar la referencia (`actualizar_referencia.py`) y cuándo no.

### 4.4 Cambiar datos lanza los tests de datos

1. En una rama `feature/`, edita `data/usuarios.csv` y pon una edad de `150` a un usuario.
2. Haz push: se lanzan **dos** workflows (el 1 y el 4). ¿Qué test de valores falla?
3. Deshaz el cambio.

### 4.5 La documentación no gasta minutos de CI

Modifica solo `docs/GUIA_TESTING_CICD.md` en una rama `feature/` y haz push. Comprueba que **no** se lanza ningún workflow y explica por qué (`paths-ignore`).

### 4.6 Contratos de datos (rama `feature/contratos-datos`)

Un **contrato** declara en un único sitio (`scripts/contratos.py`) qué debe cumplir cada conjunto de datos: columnas, tipos, rangos, categorías, claves únicas y reglas entre columnas. `construir_dataset_validado()` lo comprueba al **entrar** los datos y al **salir** el resultado: si algo no cumple, el pipeline se detiene en lugar de producir resultados incorrectos.

1. Cambia a la rama y ejecuta `uv run pytest -m contratos -v`. Fíjate en que la mayoría de tests **rompen** los datos a propósito y comprueban que el contrato lo detecta.
2. En una consola de Python, carga `data/usuarios.csv`, pon una edad de `150` y un `tipo_cuenta` `"gold"`, y valida con `CONTRATO_USUARIOS.validate(df, lazy=True)`. ¿Qué información da el error? ¿Qué cambia si quitas `lazy=True`?
3. ¿Qué diferencia hay entre los tests de `tests/datos/` y los contratos? Pista: ¿cuándo se comprueba cada uno y qué pasa si llegan datos nuevos por otra vía?
4. Abre un PR de la rama hacia `develop` y localiza el job **Contratos de datos** en los workflows 1 y 2.

### 4.7 El modelo y su CI (rama `feature/modelo-alcance`)

La rama añade un modelo que predice si una publicación tendrá **alto alcance** (12 000 visualizaciones o más). Incluye su cuaderno de entrenamiento, el modelo guardado en `modelos/` con sus **parámetros y métricas** (`metadatos_modelo.json`), sus tests y su propio workflow.

1. Ejecuta `notebooks/Bloque_07_Modelo.ipynb`. ¿Qué candidato se elige y por qué no se usa el conjunto de prueba para elegirlo?
2. Lee `tests/modelo/test_modelo.py` y explica qué riesgo cubre cada test: rendimiento mínimo, mejora sobre la referencia, reproducibilidad, **fuga de datos**, invarianza y direccionalidad.
3. Añade un candidato a `CANDIDATOS` en el cuaderno (por ejemplo, `"logistica": {"C": 0.1}`), vuelve a ejecutarlo y observa el cambio en `metadatos_modelo.json` con `git diff`. Haz commit y push: ¿qué workflows se lanzan? ¿Qué muestra el resumen del workflow 6?
4. Guarda a propósito el modelo `base` (ver el apartado *Para practicar* del cuaderno) y lanza `uv run pytest -m modelo`. ¿Qué tests fallan? No hagas commit de ese modelo.
5. Integra las ramas en orden: primero `feature/contratos-datos` → `develop` y después `feature/modelo-alcance` → `develop`. ¿Por qué en ese orden?

### 4.8 Proteger main (opcional, en tu repositorio)

En **Settings → Branches → Add branch ruleset** protege `main`:
* *Require a pull request before merging*.
* *Require status checks to pass*: añade `Batería completa (ubuntu-latest)` y `Calidad de código (ruff)`.

Repite la tarea 4.3: ahora GitHub **no permite** hacer el merge mientras la regresión falle.

### 4.9 Ampliación

* Añade un test de **valores** nuevo (por ejemplo, que `seguidos` nunca supere 1000) y comprueba qué workflows lo ejecutan.
* Añade una métrica nueva con umbral en `tests/metricas/`.
* Añade una regla nueva al contrato de publicaciones y un test que compruebe que se rechaza el dato incorrecto.
* Añade `macos-latest` a la matriz del workflow 3.

---

## 5. Entrega

Un documento breve (o el enlace a tu repositorio) con:
1. Capturas de la pestaña Actions de las tareas 4.1 a 4.5 y 4.7, indicando qué workflow se lanzó en cada caso y por qué.
2. El mensaje de error de la tarea 4.2 y el commit que lo corrige.
3. Las respuestas razonadas de las tareas 4.3, 4.6 (punto 3) y 4.7 (puntos 1, 2 y 5).

> **Próxima práctica:** ficheros grandes y Git LFS, en la rama `feature/ficheros-grandes` (`docs/GUIA_FICHEROS_GRANDES.md`).
