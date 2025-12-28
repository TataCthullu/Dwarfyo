# © 2025 Dungeon Market (Database)
# Todos los derechos reservados.
import traceback

import sqlite3
import json
from decimal import Decimal
from dum import SLOT_1_OBSIDIANA
import os
DB_NAME = os.path.join(os.path.dirname(__file__), "usuarios.db")

def _conn():
    con = sqlite3.connect(DB_NAME)
    con.execute("PRAGMA foreign_keys = ON;")
    con.execute("PRAGMA journal_mode = WAL;")
    return con


def init_db():
    with _conn() as conn:
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


def agregar_usuario(nombre, password):
    conn = _conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO usuarios (nombre, password) VALUES (?, ?)",
            (nombre, password)
        )
        conn.commit()

        # wallet base para el usuario nuevo (idempotente)
        init_wallet(nombre)
        return True

    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def validar_usuario(nombre, password):
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT password FROM usuarios WHERE nombre = ?", (nombre,))
        row = cur.fetchone()

    if row is None:
        return False
    return row[0] == password


def usuario_existe(nombre):
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM usuarios WHERE nombre = ?", (nombre,))
        row = cur.fetchone()
    return row is not None


def guardar_perfil(nombre, perfil: dict):
    perfil_json = json.dumps(perfil, ensure_ascii=False)
    with _conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO perfiles (nombre, perfil_json) VALUES (?, ?)",
            (nombre, perfil_json)
        )
        conn.commit()


def cargar_perfil(nombre):
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT perfil_json FROM perfiles WHERE nombre = ?", (nombre,))
        row = cur.fetchone()

    if row is None:
        return {}
    try:
        return json.loads(row[0])
    except Exception:
        return {}


def init_wallet(nombre: str):
    nombre = (nombre or "").strip()
    if not nombre:
        return

    # saldo inicial del jugador: SLOT_1_OBSIDIANA obsidiana, 0 quad
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

    def _d(x):
        try:
            s = str(x).strip()
            if s in ("", "None", "null", "NULL"):
                return Decimal("0")
            return Decimal(s)
        except Exception:
            return Decimal("0")

    with _conn() as con:
        cur = con.execute(
            "SELECT obsidiana, quad FROM wallet WHERE nombre = ?",
            (nombre,)
        )
        row = cur.fetchone()

        if row:
            return _d(row[0]), _d(row[1])

    # si no existe, inicializar como corresponde (SLOT_1_OBSIDIANA, 0)
    init_wallet(nombre)
    with _conn() as con:
        cur = con.execute("SELECT obsidiana, quad FROM wallet WHERE nombre = ?", (nombre,))
        row = cur.fetchone()
        if row:
            return _d(row[0]), _d(row[1])
    return Decimal("0"), Decimal("0")

def set_wallet(nombre: str, obsidiana, quad):
    nombre = (nombre or "").strip()
    if not nombre:
        return

    def _s(x):
        try:
            s = str(x).strip()
            if s in ("", "None", "null", "NULL"):
                s = "0"
            return str(Decimal(s))
        except Exception:
            return "0"

    obs = _s(obsidiana)
    qd  = _s(quad)

    print("DEBUG set_wallet CALLER:\n", "".join(traceback.format_stack(limit=6)))
    print("DEBUG set_wallet DATA:", nombre, obs, qd)

    with _conn() as con:
        con.execute("""
            INSERT INTO wallet (nombre, obsidiana, quad)
            VALUES (?, ?, ?)
            ON CONFLICT(nombre) DO UPDATE SET
                obsidiana = excluded.obsidiana,
                quad      = excluded.quad
        """, (nombre, obs, qd))
        con.commit()

def debug_wallet_raw(nombre: str):
    with _conn() as con:
        cur = con.execute("SELECT obsidiana, quad FROM wallet WHERE nombre = ?", (nombre,))
        return cur.fetchone()

print("DEBUG DB PATH:", DB_NAME)
