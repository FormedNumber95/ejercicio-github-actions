# Ficheros grandes y Git LFS

> Proyecto: Red Social Ficticia · Módulo PRIA · IABD 2026/2027 · Rama `feature/ficheros-grandes`

En proyectos de datos e IA aparecen ficheros que **no son código**: datasets, resultados intermedios, gráficos o modelos entrenados. Git está pensado para ficheros de texto pequeños y, si se versionan ficheros grandes sin cuidado, el repositorio se vuelve pesado y lento para siempre. En esta práctica vas a ver el problema con datos reales del proyecto y a resolverlo con **Git LFS** (*Large File Storage*).

---

## 1. El problema, medido en este proyecto

Al ejecutar los cuadernos se generan estos ficheros (hoy están en `.gitignore`):

| Fichero | Tamaño aproximado | Lo genera |
|---|---|---|
| `output_graficos/*.html` (17 gráficos) | 4,8 MB cada uno · **≈ 82 MB en total** | Bloques 5 y 6 |
| `data/usuarios_grande.csv` | 600 KB | Bloque 5 |
| `data/usuarios_grande.parquet` | 240 KB | Bloque 5 |
| `output_graficos/*.png` | 25–125 KB | Bloque 5 |

¿Por qué no basta con hacer `git add`?

* **Git guarda todas las versiones para siempre.** Si regeneras los 17 gráficos 10 veces, el historial guarda unos 820 MB aunque tú solo veas la última versión. Borrar el fichero después no lo elimina de la historia.
* **Clonar descarga toda esa historia.** Cada compañero y cada ejecución de GitHub Actions la paga.
* **GitHub pone límites:** avisa con ficheros de más de 50 MB y **rechaza** el push con ficheros de más de 100 MB.
* **No se pueden revisar ni fusionar:** un HTML de 4,8 MB generado o un binario no tienen un diff útil.

---

## 2. Tres estrategias (no son excluyentes)

| Estrategia | Cuándo usarla | En este proyecto |
|---|---|---|
| **No versionar y regenerar** (`.gitignore`) | El fichero se obtiene ejecutando el código y los datos versionados | Lo que hacemos con `data/*.parquet` y `output_graficos/` |
| **Artefactos de CI** | Quieres conservar el resultado de una ejecución concreta sin meterlo en git | El workflow de `main` publica los gráficos como artefacto descargable |
| **Git LFS** | El fichero es grande, **no se puede regenerar fácilmente** o debe viajar con el código (datos de partida grandes, modelos entrenados, imágenes de documentación) | Lo practicarás en esta guía |

---

## 3. Cómo funciona Git LFS

```text
 Tu repositorio (git)                     Almacenamiento LFS (GitHub)
 ─────────────────────                    ───────────────────────────
 dashboard.html  ──►  puntero (~130 B):   ──►  contenido real (4,8 MB)
                      version https://git-lfs.github.com/spec/v1
                      oid sha256:3f2a…
                      size 4831775
```

* `git lfs track "patrón"` añade una regla a **`.gitattributes`**: los ficheros que cumplan el patrón pasarán por el filtro de LFS.
* Al hacer commit, git guarda solo el **puntero**; el contenido real se sube al almacenamiento LFS al hacer push.
* Al clonar o cambiar de rama, LFS descarga el contenido y lo pone en su sitio, así que en tu carpeta ves el fichero normal.

---

## 4. Práctica guiada

Trabaja en tu repositorio de GitHub, en la rama `feature/ficheros-grandes`.

> **Esta rama trae un error a propósito:** alguien ha versionado `output_graficos/dashboard.html` (4,8 MB) **sin Git LFS** para poder consultar el dashboard sin ejecutar los cuadernos. Primero vas a ver el error en GitHub Actions y después lo corregirás.

### 4.0 Preparación

```powershell
git lfs install                    # una sola vez por ordenador
git switch feature/ficheros-grandes
uv sync
```

El marcador `repositorio` (`tests/repositorio/test_ficheros_grandes.py`) comprueba en el **último commit** que ningún fichero de más de **2 MB** está versionado fuera de LFS. El workflow **7 · Ficheros grandes** lo ejecuta en cada push.

### 4.1 Ver el error (antes de corregir nada)

1. En GitHub, pestaña **Actions** → workflow **7 · Ficheros grandes** → la ejecución de la rama `feature/ficheros-grandes`. Está en **rojo**: abre el job y lee el mensaje del test (qué fichero y cuánto ocupa). Si no hay ninguna ejecución, lánzala con **Run workflow** eligiendo esa rama.
2. Mira el resumen de la ejecución: la tabla de los 10 ficheros más grandes muestra el dashboard.
3. Reproduce el error en tu ordenador:

```powershell
uv run pytest -m repositorio                       # FALLA: indica el fichero y su tamaño
git ls-tree -r -l HEAD | Select-String dashboard   # git guarda los 4,8 MB enteros
git log --oneline -- output_graficos/dashboard.html   # qué commit lo añadió
```

### 4.2 Corregirlo con Git LFS

```powershell
git rm --cached output_graficos/dashboard.html   # lo saca del índice de git (el fichero sigue en tu carpeta)
git lfs track "output_graficos/*.html"          # añade la regla a .gitattributes
git diff .gitattributes                         # observa la línea añadida
git add .gitattributes
git add -f output_graficos/dashboard.html       # -f: está en .gitignore; ahora entra por LFS
git commit -m "Dashboard versionado con Git LFS"

git lfs ls-files                                # lista los ficheros gestionados por LFS
git show HEAD:output_graficos/dashboard.html    # en git solo hay un puntero
uv run pytest -m repositorio                    # ahora PASA
git push
```

En GitHub, abre el fichero: aparece la etiqueta **Stored with Git LFS**. En Actions, el workflow 7 queda en **verde** y su resumen muestra los ficheros de LFS.

### 4.3 El fichero sigue en la historia

El guardián comprueba el **último** commit, pero el commit que añadió el dashboard sin LFS sigue en la historia y cualquiera que clone el repositorio se lo descarga.

```powershell
git count-objects -vH                           # tamaño del repositorio en tu disco
git log --oneline --stat -- output_graficos/dashboard.html
```

Para limpiar la historia habría que reescribirla (`git lfs migrate import`, ver la ampliación). Por eso es mejor que el guardián falle **antes** de integrar el cambio, en el pull request.

### 4.4 Clonar sin descargar los ficheros grandes

```powershell
cd ..
$env:GIT_LFS_SKIP_SMUDGE = "1"             # clona sin descargar el contenido de LFS
git clone https://github.com/<tu-usuario>/red-social-ficticia.git clon-ligero
Remove-Item Env:GIT_LFS_SKIP_SMUDGE
cd clon-ligero
git checkout feature/ficheros-grandes
Get-Content output_graficos/dashboard.html   # solo es el puntero
git lfs pull                                 # descarga el contenido real
```

Es lo que hace GitHub Actions por defecto: `actions/checkout` **no** descarga LFS salvo que se indique `lfs: true`. Míralo en `.github/workflows/ficheros-grandes.yml`.

### 4.5 Cuando git-lfs no está instalado

Pregunta para pensar: si un compañero sin `git lfs install` hace commit de un fichero que cumple una regla de `.gitattributes`, ¿qué se guarda? El segundo test del guardián (`test_los_ficheros_con_regla_lfs_se_guardan_como_punteros`) detecta justo ese caso.

### 4.6 Decidir con criterio

Para cada fichero de la tabla del apartado 1, decide y justifica qué estrategia usarías: **no versionar**, **artefacto de CI** o **Git LFS**. Pista: ¿se puede regenerar? ¿cuánto tarda? ¿lo necesita alguien que no ejecute el código?

---

## 5. A tener en cuenta

* **El almacenamiento LFS de GitHub tiene una cuota** de espacio y de descarga en el plan gratuito. Consulta los límites actuales en la documentación de GitHub antes de subir ficheros muy grandes.
* **Un `git bundle` no incluye el contenido de LFS**, solo los punteros. Por eso esta rama no trae ficheros en LFS: los creas tú en tu repositorio.
* **Mover a LFS no aligera la historia pasada.** Los ficheros que ya se versionaron enteros siguen en los commits antiguos.
* **Los forks comparten el almacenamiento LFS del repositorio original** y pueden necesitar permisos para subir ficheros.

## 6. Ampliación

* Añade una regla para los modelos (`modelos/*.joblib`) y razona si compensa con un modelo de 4 KB.
* Investiga `git lfs migrate import --include="output_graficos/*.html"` para pasar a LFS ficheros que ya estaban en la historia (reescribe commits: hazlo solo en una rama de pruebas).
* Compara el tamaño de la carpeta `.git` antes y después de versionar los 17 gráficos sin LFS (`git count-objects -vH`).
