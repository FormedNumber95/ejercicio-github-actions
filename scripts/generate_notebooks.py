"""
generate_notebooks.py

Recrea y sincroniza los 5 cuadernos Jupyter resueltos del proyecto Red Social
Ficticia en la carpeta notebooks_soluciones/.

Uso recomendado desde la raiz de Recursos_profesor:
    python scripts/generate_notebooks.py

Tambien puede ejecutarse desde cualquier otra carpeta, porque calcula las rutas
a partir de la ubicacion de este propio script.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks_soluciones"

KERNEL = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3",
}

LANGUAGE_INFO = {
    "codemirror_mode": {"name": "ipython", "version": 3},
    "file_extension": ".py",
    "mimetype": "text/x-python",
    "name": "python",
    "pygments_lexer": "ipython3",
    "version": "3.10.0",
}

NOTEBOOKS = [
    (
        "Bloque_01_EstructurasDatos_Lambda.ipynb",
        "Bloque 1 - Estructuras de Datos y Lambda",
    ),
    (
        "Bloque_02_NumPy.ipynb",
        "Bloque 2 - NumPy",
    ),
    (
        "Bloque_03_Pandas_Basico.ipynb",
        "Bloque 3 - Pandas Basico",
    ),
    (
        "Bloque_04_Pandas_Avanzado.ipynb",
        "Bloque 4 - Pandas Avanzado",
    ),
    (
        "Bloque_05_Graficos_Faker.ipynb",
        "Bloque 5 - Graficos y Faker",
    ),
]


def notebook_base(titulo: str) -> dict:
    """Crea un cuaderno minimo cuando falta el archivo del bloque."""
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    f"# {titulo} - solucion\n",
                    "\n",
                    "Cuaderno de solucion recreado automaticamente.\n",
                ],
            },
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def preparar_metadata(nb: dict) -> dict:
    """Normaliza los metadatos minimos para abrir el notebook en Jupyter."""
    nb.setdefault("nbformat", 4)
    nb.setdefault("nbformat_minor", 5)
    metadata = nb.setdefault("metadata", {})
    metadata["kernelspec"] = KERNEL
    metadata["language_info"] = LANGUAGE_INFO
    return nb


def es_celda_configuracion(cell: dict) -> bool:
    return "".join(cell.get("source", [])).startswith(
        "# Configuracion de rutas del proyecto"
    )


def eliminar_celda_configuracion(nb: dict) -> dict:
    cells = nb.setdefault("cells", [])
    cells[:] = [cell for cell in cells if not es_celda_configuracion(cell)]
    return nb


def actualizar_referencias(nb: dict) -> dict:
    for cell in nb.get("cells", []):
        source = cell.get("source", [])
        if isinstance(source, str):
            source = [source]
        nuevas_lineas = []
        for line in source:
            line = line.replace("python -m python -m pytest", "python -m pytest")
            if "python -m pytest" not in line:
                line = line.replace("pytest tests/", "python -m pytest tests/")
            line = re.sub(r"(?<!\.\./)data/", "../data/", line)
            line = re.sub(r"(?<!\.\./)tests/", "../tests/", line)
            line = re.sub(r"(?<!\.\./)scripts/", "../scripts/", line)
            line = re.sub(r"(?<!\.\./)output_graficos/", "../output_graficos/", line)
            line = line.replace("os.makedirs('output_graficos'", "os.makedirs('../output_graficos'")
            line = line.replace('os.makedirs("output_graficos"', 'os.makedirs("../output_graficos"')
            line = line.replace("python -m python -m pytest", "python -m pytest")
            nuevas_lineas.append(line)
        cell["source"] = nuevas_lineas
    return nb


def cargar_o_crear(path: Path, titulo: str) -> tuple[dict, bool]:
    if path.exists():
        with path.open("r", encoding="utf-8") as archivo:
            return json.load(archivo), False
    return notebook_base(titulo), True


def guardar(nb: dict, path: Path) -> None:
    with path.open("w", encoding="utf-8") as archivo:
        json.dump(nb, archivo, ensure_ascii=False, indent=1)
        archivo.write("\n")


def main() -> None:
    print("Sincronizando cuadernos en notebooks_soluciones/ ...")
    NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)

    for nombre, titulo in NOTEBOOKS:
        path = NOTEBOOKS_DIR / nombre
        notebook, creado = cargar_o_crear(path, titulo)
        notebook = preparar_metadata(notebook)
        notebook = eliminar_celda_configuracion(notebook)
        notebook = actualizar_referencias(notebook)
        guardar(notebook, path)

        accion = "creado" if creado else "sincronizado"
        print(f"  [OK] {nombre} {accion}")

    print("Sincronizacion completada.")


if __name__ == "__main__":
    main()
