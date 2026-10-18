"""
setup_datos.py
Genera los ficheros de datos base para el proyecto Red Social Ficticia.

Ejecutar UNA sola vez antes de comenzar los ejercicios:
    cd Proy_analisis_Red_Social_Ficticia
    python data/setup_datos.py

Crea en la carpeta data/:
    - usuarios.csv         (100 perfiles de usuario)
    - publicaciones.csv    (300 publicaciones, para Bloque 1)
    - publicaciones.xlsx   (mismas 300 publicaciones en Excel, para Bloque 2)
    - conexiones.json      (grafo de seguidores, para Bloques 1 y 2)
"""

import csv
import json
import os
import random
from datetime import date, timedelta

import pandas as pd

random.seed(42)

# ── Datos de referencia ──────────────────────────────────────────────────────

NOMBRES_M = [
    "Carlos", "Luis", "Miguel", "David", "Antonio", "Manuel", "Pablo",
    "Jorge", "Alejandro", "Roberto", "Fernando", "Sergio", "Javier",
    "Daniel", "Marcos", "Adrian", "Ivan", "Raul", "Oscar", "Eduardo",
]
NOMBRES_F = [
    "Ana", "Maria", "Laura", "Carmen", "Sara", "Lucia", "Marta", "Elena",
    "Isabel", "Cristina", "Patricia", "Sofia", "Nuria", "Alicia", "Beatriz",
    "Ines", "Claudia", "Alba", "Andrea", "Irene",
]
APELLIDOS = [
    "Garcia", "Martinez", "Lopez", "Sanchez", "Gonzalez", "Perez",
    "Rodriguez", "Fernandez", "Gomez", "Moreno", "Jimenez", "Ruiz",
    "Diaz", "Hernandez", "Alvarez", "Romero", "Navarro", "Torres",
    "Dominguez", "Ramos", "Vazquez", "Gil", "Molina", "Morales", "Ortega",
]
CIUDADES = [
    "Madrid", "Barcelona", "Bilbao", "Sevilla", "Valencia", "Zaragoza",
    "Malaga", "Murcia", "Palma", "Las Palmas", "Valladolid", "Alicante",
    "Cordoba", "Vitoria", "Granada",
]
PAISES = ["Espana"] * 85 + ["Mexico"] * 7 + ["Argentina"] * 5 + ["Colombia"] * 3
TIPOS_CUENTA = ["free"] * 6 + ["premium"] * 3 + ["creator"] * 1
HASHTAGS = [
    "#tecnologia", "#ia", "#python", "#datos", "#programacion",
    "#machinelearning", "#deeplearning", "#datascience", "#bigdata",
    "#cloud", "#innovacion", "#startup", "#coding", "#developer", "#analisis",
]
TIPOS_CONTENIDO = ["foto", "foto", "video", "texto", "historia", "reel"]
BIOS = [
    "Apasionado de los datos y la tecnologia",
    "Desarrolladora de software | Python lover",
    "Data scientist en formacion",
    "Explorando el mundo de la IA",
    "Estudiante de IABD",
    "Amante del codigo limpio",
    "Machine learning enthusiast",
    "Analista de datos",
    "Freelance developer",
    "Estudiante de Big Data",
]


# ── Funciones auxiliares ─────────────────────────────────────────────────────

def fecha_aleatoria(inicio, fin):
    return inicio + timedelta(days=random.randint(0, (fin - inicio).days))


def nullable(valor, prob=0.05):
    """Devuelve None con probabilidad `prob`, o el valor original."""
    return None if random.random() < prob else valor


# ── Generadores ──────────────────────────────────────────────────────────────

def generar_usuarios(n):
    usuarios = []
    for i in range(1, n + 1):
        genero = random.choices(["M", "F", "NB"], weights=[45, 50, 5])[0]
        nombre = random.choice(NOMBRES_M if genero == "M" else NOMBRES_F)
        tipo = random.choice(TIPOS_CUENTA)
        seguidores = (
            random.randint(1000, 50000) if tipo == "creator"
            else random.randint(10, 5000)
        )
        usuarios.append({
            "id_usuario": i,
            "nombre": nombre,
            "apellidos": f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)}",
            "edad": nullable(random.randint(18, 55), 0.05),
            "ciudad": nullable(random.choice(CIUDADES), 0.04),
            "pais": random.choice(PAISES),
            "genero": genero,
            "fecha_registro": fecha_aleatoria(
                date(2020, 1, 1), date(2024, 6, 1)
            ).isoformat(),
            "tipo_cuenta": tipo,
            "seguidores": seguidores,
            "seguidos": random.randint(20, 1000),
            "publicaciones_totales": random.randint(0, 500),
            "activo": random.choices([True, False], weights=[80, 20])[0],
            "bio": nullable(random.choice(BIOS), 0.10),
        })
    return usuarios


def generar_publicaciones(n, ids_usuarios):
    publicaciones = []
    for i in range(1, n + 1):
        likes = nullable(random.randint(0, 5000), 0.04)
        comentarios = nullable(random.randint(0, 500), 0.03)
        publicaciones.append({
            "id_publicacion": i,
            "id_usuario": random.choice(ids_usuarios),
            "fecha": fecha_aleatoria(
                date(2023, 1, 1), date(2024, 6, 1)
            ).isoformat(),
            "tipo_contenido": random.choice(TIPOS_CONTENIDO),
            "likes": likes,
            "comentarios": comentarios,
            "compartidos": random.randint(0, 200),
            "visualizaciones": (likes or 0) * random.randint(2, 10) + random.randint(100, 500),
            "hashtags": ",".join(random.sample(HASHTAGS, random.randint(1, 5))),
        })
    return publicaciones


def generar_conexiones(ids_usuarios):
    conexiones = []
    for uid in ids_usuarios:
        otros = [x for x in ids_usuarios if x != uid]
        n = min(random.randint(5, 30), len(otros))
        conexiones.append({
            "id_usuario": uid,
            "siguiendo": sorted(random.sample(otros, n)),
        })
    return conexiones


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    print("Generando dataset base...")

    usuarios = generar_usuarios(100)
    ids = [u["id_usuario"] for u in usuarios]
    publicaciones = generar_publicaciones(300, ids)
    conexiones = generar_conexiones(ids)

    # usuarios.csv
    with open("data/usuarios.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=usuarios[0].keys())
        writer.writeheader()
        writer.writerows(usuarios)
    print(f"  [OK] data/usuarios.csv        ({len(usuarios)} registros)")

    # publicaciones.csv  y  publicaciones.xlsx
    df_pub = pd.DataFrame(publicaciones)
    df_pub.to_csv("data/publicaciones.csv", index=False, encoding="utf-8")
    print(f"  [OK] data/publicaciones.csv   ({len(publicaciones)} registros)")
    try:
        df_pub.to_excel("data/publicaciones.xlsx", index=False, sheet_name="publicaciones")
        print(f"  [OK] data/publicaciones.xlsx  ({len(publicaciones)} registros)")
    except Exception as e:
        print(f"  [AVISO] data/publicaciones.xlsx no se pudo generar ({e}). Instala openpyxl.")

    # conexiones.json
    with open("data/conexiones.json", "w", encoding="utf-8") as f:
        json.dump(conexiones, f, ensure_ascii=False, indent=2)
    print(f"  [OK] data/conexiones.json     ({len(conexiones)} nodos)")

    print("\nDataset listo. Puedes abrir los cuadernos de ejercicios.")
