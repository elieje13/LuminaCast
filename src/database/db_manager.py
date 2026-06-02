# src/database/db_manager.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../data/lumina_cast.db')

def inicializar_db():
    """Crea la base de datos y la tabla de canciones si no existen"""
    # Asegurar que la carpeta data exista
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    
    # Crear tabla de canciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS canciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            letra TEXT NOT NULL
        )
    ''')
    conexion.commit()
    
    # Insertar datos de prueba si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM canciones")
    if cursor.fetchone()[0] == 0:
        insertar_datos_prueba(conexion)
        
    conexion.close()

def insertar_datos_prueba(conexion):
    """Inserta canciones iniciales para pruebas"""
    cursor = conexion.cursor()
    canciones = [
        (
            "Cuan Grande es Él", 
            "[Estrofa 1]\nSeñor, mi Dios, al contemplar los cielos\nEl firmamento y las estrellas mil...\n\n[Coro]\nMi corazón entona la canción\n¡Cuán grande es Él! ¡Cuán grande es Él!"
        ),
        (
            "Océanos", 
            "[Estrofa 1]\nTu voz me llama a las aguas\nA lo desconocido, donde tus pies pueden fallar...\n\n[Coro]\nY a tu nombre clamaré\nY fijaré mis ojos en ese mar"
        ),
        (
            "Way Maker", 
            "[Estrofa 1]\nAquí estás, te vemos operar\nTe adoraré, te adoraré...\n\n[Coro]\nMilagroso, abres camino, cumples promesas\nLuz en las tinieblas, mi Dios, así eres Tú"
        )
    ]
    cursor.executemany("INSERT INTO canciones (titulo, letra) VALUES (?, ?)", canciones)
    conexion.commit()

def obtener_todas_las_canciones():
    """Devuelve una lista de tuplas (id, titulo) de todas las canciones"""
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("SELECT id, titulo FROM canciones ORDER BY titulo ASC")
    canciones = cursor.fetchall()
    conexion.close()
    return canciones

def obtener_letra_cancion(song_id):
    """Devuelve la letra completa de una canción por su ID"""
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("SELECT letra FROM canciones WHERE id = ?", (song_id,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado[0] if resultado else ""