import sqlite3
import json
from decimal import Decimal
import sqlite3
DB_NAME = "usuarios.db"

SLOT_1_OBSIDIANA = Decimal("5000")

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


    cur.execute("""
        CREATE TABLE IF NOT EXISTS wallet (
            nombre TEXT PRIMARY KEY,
            obsidiana TEXT NOT NULL,
            quad TEXT NOT NULL,
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
        # crear wallet base para el usuario nuevo
        init_wallet(nombre)
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


def _conn():
    return sqlite3.connect(DB_NAME)

def init_wallet(nombre: str):
    nombre = (nombre or "").strip()
    if not nombre:
        return

    with _conn() as con:
        con.execute(
            "INSERT OR IGNORE INTO wallet (nombre, obsidiana, quad) VALUES (?, ?, ?)",
            (nombre, str(SLOT_1_OBSIDIANA), "0")
        )
        con.commit()


def get_wallet(nombre: str):
    nombre = (nombre or "").strip()
    if not nombre:
        return Decimal("0"), Decimal("0")

    with _conn() as con:
        cur = con.execute(
            "SELECT obsidiana, quad FROM wallet WHERE nombre = ?",
            (nombre,)
        )
        row = cur.fetchone()
        if row:
            return Decimal(row[0]), Decimal(row[1])

        # si no existe, lo crea (base)
        con.execute(
            "INSERT INTO wallet (nombre, obsidiana, quad) VALUES (?, ?, ?)",
            (nombre, str(SLOT_1_OBSIDIANA), "0")
        )
        con.commit()
        return Decimal(str(SLOT_1_OBSIDIANA)), Decimal("0")


def set_wallet(nombre: str, obsidiana, quad):
    nombre = (nombre or "").strip()
    if not nombre:
        return

    obs = str(Decimal(str(obsidiana)))
    qd  = str(Decimal(str(quad)))

    with _conn() as con:
        con.execute("""
            INSERT INTO wallet (nombre, obsidiana, quad)
            VALUES (?, ?, ?)
            ON CONFLICT(nombre) DO UPDATE SET
                obsidiana = excluded.obsidiana,
                quad      = excluded.quad
        """, (nombre, obs, qd))
        con.commit()


