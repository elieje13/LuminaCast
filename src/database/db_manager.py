import sqlite3
import os

# --- RUTAS ABSOLUTAS ---
DIRECTORIO_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(DIRECTORIO_RAIZ, 'lumina_cast.db')

def obtener_conexion():
    return sqlite3.connect(DB_PATH)

def inicializar_db():
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS canciones (id INTEGER PRIMARY KEY, titulo TEXT, letra TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS configuracion (clave TEXT PRIMARY KEY, valor TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS perfiles (id INTEGER PRIMARY KEY, nombre TEXT, congregacion TEXT, icono TEXT)''')
    
    cursor.execute("PRAGMA table_info(perfiles)")
    columnas = [col[1] for col in cursor.fetchall()]
    if 'icono' not in columnas:
        cursor.execute("ALTER TABLE perfiles ADD COLUMN icono TEXT DEFAULT '👤'")
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS biblia_versiones (id INTEGER PRIMARY KEY, nombre TEXT, abreviatura TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS biblia_libros (id INTEGER PRIMARY KEY, version_id INTEGER, nombre TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS biblia_versiculos (id INTEGER PRIMARY KEY, libro_id INTEGER, capitulo INTEGER, versiculo INTEGER, texto TEXT)''')

    # --- LIMPIEZA DE LA VERSIÓN DEMO ---
    # Busca si existe la versión de prueba y la elimina junto con sus libros y versículos
    cursor.execute("SELECT id FROM biblia_versiones WHERE nombre LIKE '%(Demo)%'")
    demos = cursor.fetchall()
    for d in demos:
        v_id = d[0]
        cursor.execute("DELETE FROM biblia_versiculos WHERE libro_id IN (SELECT id FROM biblia_libros WHERE version_id = ?)", (v_id,))
        cursor.execute("DELETE FROM biblia_libros WHERE version_id = ?", (v_id,))
        cursor.execute("DELETE FROM biblia_versiones WHERE id = ?", (v_id,))

    conn.commit()
    conn.close()

# ================= FUNCIONES DE PERFILES =================
def obtener_perfiles():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, congregacion, icono FROM perfiles")
    res = cursor.fetchall()
    conn.close()
    return res

def agregar_perfil(nombre, congregacion, icono="👤"):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO perfiles (nombre, congregacion, icono) VALUES (?, ?, ?)", (nombre, congregacion, icono))
    conn.commit()
    conn.close()

def actualizar_perfil(perfil_id, nombre, congregacion, icono="👤"):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("UPDATE perfiles SET nombre = ?, congregacion = ?, icono = ? WHERE id = ?", (nombre, congregacion, icono, perfil_id))
    conn.commit()
    conn.close()

def eliminar_perfil(perfil_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM perfiles WHERE id = ?", (perfil_id,))
    conn.commit()
    conn.close()

# ================= FUNCIONES DE BIBLIA =================
def obtener_versiones_biblia():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, abreviatura FROM biblia_versiones")
    res = cursor.fetchall()
    conn.close()
    return res

def obtener_libros_biblia(version_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM biblia_libros WHERE version_id = ? ORDER BY id", (version_id,))
    res = cursor.fetchall()
    conn.close()
    return res

def obtener_capitulos_biblia(libro_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT capitulo FROM biblia_versiculos WHERE libro_id = ? ORDER BY capitulo", (libro_id,))
    res = [row[0] for row in cursor.fetchall()]
    conn.close()
    return res

def obtener_versiculos_biblia(libro_id, capitulo):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT versiculo, texto FROM biblia_versiculos WHERE libro_id = ? AND capitulo = ? ORDER BY versiculo", (libro_id, capitulo))
    res = cursor.fetchall()
    conn.close()
    return res

def buscar_versiculos_biblia(version_id, texto_busqueda):
    conn = obtener_conexion()
    cursor = conn.cursor()
    patron = f"%{texto_busqueda}%"
    # Hace un JOIN para traer el nombre del libro junto con el texto
    cursor.execute("""
        SELECT l.nombre, v.capitulo, v.versiculo, v.texto 
        FROM biblia_versiculos v
        JOIN biblia_libros l ON v.libro_id = l.id
        WHERE l.version_id = ? AND v.texto LIKE ?
        LIMIT 100
    """, (version_id, patron))
    res = cursor.fetchall()
    conn.close()
    return res

# ================= FUNCIONES DE CANCIONES =================
def obtener_todas_las_canciones():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id, titulo FROM canciones ORDER BY titulo")
    res = cursor.fetchall()
    conn.close()
    return res

def obtener_letra_cancion(song_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT letra FROM canciones WHERE id = ?", (song_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else ""

def agregar_cancion(titulo, letra):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO canciones (titulo, letra) VALUES (?, ?)", (titulo, letra))
    conn.commit()
    conn.close()

def actualizar_cancion(song_id, titulo, letra):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("UPDATE canciones SET titulo = ?, letra = ? WHERE id = ?", (titulo, letra, song_id))
    conn.commit()
    conn.close()

def eliminar_cancion(song_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM canciones WHERE id = ?", (song_id,))
    conn.commit()
    conn.close()

# ================= FUNCIONES DE CONFIGURACIÓN =================
def guardar_configuracion(clave, valor):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)", (clave, valor))
    conn.commit()
    conn.close()

def obtener_configuracion(clave):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT valor FROM configuracion WHERE clave = ?", (clave,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else None