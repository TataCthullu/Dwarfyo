import sqlite3
import json

DB_NAME = "usuarios.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            nombre TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS perfiles (
            nombre TEXT PRIMARY KEY,
            perfil_json TEXT NOT NULL,
            FOREIGN KEY(nombre) REFERENCES usuarios(nombre)
        )
    """)

    conn.commit()
    conn.close()

def agregar_usuario(nombre, password):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO usuarios (nombre, password) VALUES (?, ?)",
            (nombre, password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # El usuario ya existe (PRIMARY KEY duplicada)
        return False
    finally:
        conn.close()

def validar_usuario(nombre, password):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT password FROM usuarios WHERE nombre = ?", (nombre,))
    row = cur.fetchone()

    conn.close()

    if row is None:
        return False
    return row[0] == password

def usuario_existe(nombre):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM usuarios WHERE nombre = ?", (nombre,))
    row = cur.fetchone()
    conn.close()
    return row is not None

def guardar_perfil(nombre, perfil: dict):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    perfil_json = json.dumps(perfil, ensure_ascii=False)
    cur.execute(
        "INSERT OR REPLACE INTO perfiles (nombre, perfil_json) VALUES (?, ?)",
        (nombre, perfil_json)
    )
    conn.commit()
    conn.close()

def cargar_perfil(nombre):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT perfil_json FROM perfiles WHERE nombre = ?", (nombre,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return {}  # perfil vacío si nunca guardó nada
    try:
        return json.loads(row[0])
    except Exception:
        return {}
