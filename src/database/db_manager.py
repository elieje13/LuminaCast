# src/database/db_manager.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../data/lumina_cast.db')

def inicializar_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS canciones (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT NOT NULL, letra TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS perfiles (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre_perfil TEXT NOT NULL, nombre_congregacion TEXT NOT NULL, icono TEXT NOT NULL)''')
    
    # NUEVA TABLA: Para guardar configuraciones internas como el "Último perfil usado"
    cursor.execute('''CREATE TABLE IF NOT EXISTS configuracion (clave TEXT PRIMARY KEY, valor TEXT)''')
    conexion.commit()
    
    cursor.execute("SELECT COUNT(*) FROM canciones")
    if cursor.fetchone()[0] == 0:
        insertar_datos_prueba(conexion)
        
    conexion.close()

def insertar_datos_prueba(conexion):
    cursor = conexion.cursor()
    canciones = [
        ("Cuan Grande es Él", "[Estrofa 1]\nSeñor, mi Dios, al contemplar los cielos\nEl firmamento y las estrellas mil...\n\n[Coro]\nMi corazón entona la canción\n¡Cuán grande es Él! ¡Cuán grande es Él!"),
        ("Océanos", "[Estrofa 1]\nTu voz me llama a las aguas\nA lo desconocido, donde tus pies pueden fallar...\n\n[Coro]\nY a tu nombre clamaré\nY fijaré mis ojos en ese mar")
    ]
    cursor.executemany("INSERT INTO canciones (titulo, letra) VALUES (?, ?)", canciones)
    conexion.commit()

# --- FUNCIONES DE CONFIGURACIÓN DEL SISTEMA ---
def obtener_configuracion(clave):
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("SELECT valor FROM configuracion WHERE clave = ?", (clave,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado[0] if resultado else ""

def guardar_configuracion(clave, valor):
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)", (clave, str(valor)))
    conexion.commit()
    conexion.close()

# --- FUNCIONES DE CANCIONES ---
def obtener_todas_las_canciones():
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("SELECT id, titulo FROM canciones ORDER BY titulo ASC")
    canciones = cursor.fetchall()
    conexion.close()
    return canciones

def obtener_letra_cancion(song_id):
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("SELECT letra FROM canciones WHERE id = ?", (song_id,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado[0] if resultado else ""

def agregar_cancion(titulo, letra):
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO canciones (titulo, letra) VALUES (?, ?)", (titulo, letra))
    conexion.commit()
    conexion.close()

def actualizar_cancion(song_id, titulo, letra):
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("UPDATE canciones SET titulo = ?, letra = ? WHERE id = ?", (titulo, letra, song_id))
    conexion.commit()
    conexion.close()

def eliminar_cancion(song_id):
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM canciones WHERE id = ?", (song_id,))
    conexion.commit()
    conexion.close()

# --- FUNCIONES DE PERFILES ---
def obtener_perfiles():
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre_perfil, nombre_congregacion, icono FROM perfiles")
    perfiles = cursor.fetchall()
    conexion.close()
    return perfiles

def agregar_perfil(nombre_perfil, congregacion, icono):
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO perfiles (nombre_perfil, nombre_congregacion, icono) VALUES (?, ?, ?)", 
                   (nombre_perfil, congregacion, icono))
    conexion.commit()
    conexion.close()

def actualizar_perfil(perfil_id, nombre_perfil, congregacion, icono):
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("UPDATE perfiles SET nombre_perfil = ?, nombre_congregacion = ?, icono = ? WHERE id = ?", 
                   (nombre_perfil, congregacion, icono, perfil_id))
    conexion.commit()
    conexion.close()

def eliminar_perfil(perfil_id):
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM perfiles WHERE id = ?", (perfil_id,))
    conexion.commit()
    conexion.close()