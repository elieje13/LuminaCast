import sqlite3
import json
import os
import glob

# Configuración de rutas
DIRECTORIO_RAIZ = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(DIRECTORIO_RAIZ, 'lumina_cast.db')
CARPETA_BIBLIAS = os.path.join(DIRECTORIO_RAIZ, 'data', 'biblias', '*.json')

def importar_todo():
    if not os.path.exists(os.path.join(DIRECTORIO_RAIZ, 'data', 'biblias')):
        print(f"❌ La carpeta 'data/biblias/' no existe. Créala y pon tus JSON ahí.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Asegurar tablas
    cursor.execute('''CREATE TABLE IF NOT EXISTS biblia_versiones (id INTEGER PRIMARY KEY, nombre TEXT, abreviatura TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS biblia_libros (id INTEGER PRIMARY KEY, version_id INTEGER, nombre TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS biblia_versiculos (id INTEGER PRIMARY KEY, libro_id INTEGER, capitulo INTEGER, versiculo INTEGER, texto TEXT)''')

    archivos = glob.glob(CARPETA_BIBLIAS)
    
    for archivo in archivos:
        nombre_archivo = os.path.basename(archivo)
        print(f"🔄 Procesando: {nombre_archivo}")
        
        with open(archivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Extraer metadatos (usamos nombre de archivo si no trae campos en el JSON)
            nombre_v = data.get("name", nombre_archivo.replace(".json", ""))
            abrev_v = data.get("abbr", nombre_archivo.replace(".json", ""))
            
            cursor.execute("INSERT OR IGNORE INTO biblia_versiones (nombre, abreviatura) VALUES (?, ?)", (nombre_v, abrev_v))
            cursor.execute("SELECT id FROM biblia_versiones WHERE abreviatura = ?", (abrev_v,))
            v_id = cursor.fetchone()[0]
            
            # Insertar Libros y Versículos (Lógica de Diccionario Anidado)
            if isinstance(data, dict):
                # Si el JSON tiene una llave superior como 'books', iteramos sobre ella
                contenido = data.get('books', data) 
                
                for nombre_libro, libro_data in contenido.items():
                    if nombre_libro in ["name", "abbr", "books"]: continue # Saltar metadatos
                    
                    cursor.execute("INSERT INTO biblia_libros (version_id, nombre) VALUES (?, ?)", (v_id, nombre_libro))
                    l_id = cursor.lastrowid
                    
                    versiculos_a_insertar = []
                    for num_cap, cap_data in libro_data.items():
                        for num_ver, texto in cap_data.items():
                            versiculos_a_insertar.append((l_id, int(num_cap), int(num_ver), texto.strip()))
                    
                    cursor.executemany("INSERT INTO biblia_versiculos (libro_id, capitulo, versiculo, texto) VALUES (?, ?, ?, ?)", versiculos_a_insertar)
            
            print(f"   ✅ {nombre_v} importada correctamente.")
            
    conn.commit()
    conn.close()
    print("🎉 ¡Proceso finalizado! Todas las biblias están listas en LuminaCast.")

if __name__ == "__main__":
    importar_todo()