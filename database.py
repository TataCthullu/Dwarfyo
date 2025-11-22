import sqlite3

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

    conn.commit()
    conn.close()

def agregar_usuario(nombre, password):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO usuarios (nombre, password) VALUES (?, ?)", (nombre, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # ya existe el usuario

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
