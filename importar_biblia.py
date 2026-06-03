import sqlite3
import json
import os

# --- CORRECCIÓN DE RUTAS ABSOLUTAS ---
DIRECTORIO_RAIZ = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(DIRECTORIO_RAIZ, 'lumina_cast.db')
JSON_PATH = os.path.join(DIRECTORIO_RAIZ, 'data', 'RVR1960 - Spanish.json')

def importar_biblia_json():
    if not os.path.exists(JSON_PATH):
        print(f"❌ No se encontró el archivo JSON en: {JSON_PATH}")
        return
        
    print(f"🔗 Usando base de datos PRINCIPAL: {DB_PATH}")
    print("📖 Leyendo archivo JSON...")
    
    with open(JSON_PATH, 'r', encoding='utf-8') as file:
        try:
            biblia_data = json.load(file)
        except json.JSONDecodeError:
            print("❌ Error: El archivo no es un JSON válido.")
            return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tablas de seguridad
    cursor.execute('''CREATE TABLE IF NOT EXISTS biblia_versiones (id INTEGER PRIMARY KEY, nombre TEXT, abreviatura TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS biblia_libros (id INTEGER PRIMARY KEY, version_id INTEGER, nombre TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS biblia_versiculos (id INTEGER PRIMARY KEY, libro_id INTEGER, capitulo INTEGER, versiculo INTEGER, texto TEXT)''')

    nombre_version = "Reina Valera 1960"
    abreviatura = "RVR1960"
    
    cursor.execute("SELECT id FROM biblia_versiones WHERE abreviatura = ?", (abreviatura,))
    version_existente = cursor.fetchone()
    
    if version_existente:
        print(f"⚠️ La versión {abreviatura} ya existe. Eliminando datos anteriores para reemplazar...")
        v_id = version_existente[0]
        cursor.execute("DELETE FROM biblia_versiculos WHERE libro_id IN (SELECT id FROM biblia_libros WHERE version_id = ?)", (v_id,))
        cursor.execute("DELETE FROM biblia_libros WHERE version_id = ?", (v_id,))
    else:
        cursor.execute("INSERT INTO biblia_versiones (nombre, abreviatura) VALUES (?, ?)", (nombre_version, abreviatura))
        v_id = cursor.lastrowid
        print(f"✅ Versión '{nombre_version}' registrada con ID: {v_id}")

    print("⏳ Insertando libros y versículos, esto puede tomar unos segundos...")
    
    total_versiculos = 0
    
    # NUEVA LÓGICA: Adaptada al formato de diccionario anidado del archivo del usuario
    if isinstance(biblia_data, dict):
        # Nivel 1: Iteramos sobre los libros (ej: "Génesis", "Éxodo")
        for nombre_libro, libro_data in biblia_data.items():
            cursor.execute("INSERT INTO biblia_libros (version_id, nombre) VALUES (?, ?)", (v_id, nombre_libro))
            l_id = cursor.lastrowid
            
            versiculos_a_insertar = []
            
            # Nivel 2: Iteramos sobre los capítulos (ej: "1", "2")
            if isinstance(libro_data, dict):
                for num_capitulo_str, capitulo_data in libro_data.items():
                    # Nivel 3: Iteramos sobre los versículos (ej: "1", "2")
                    if isinstance(capitulo_data, dict):
                        for num_versiculo_str, texto_versiculo in capitulo_data.items():
                            try:
                                num_cap = int(num_capitulo_str)
                                num_ver = int(num_versiculo_str)
                                texto_limpio = texto_versiculo.strip()
                                
                                versiculos_a_insertar.append((l_id, num_cap, num_ver, texto_limpio))
                                total_versiculos += 1
                            except ValueError:
                                pass # Ignora llaves que no sean números por seguridad
            
            # Inserción masiva para optimizar el tiempo
            cursor.executemany("INSERT INTO biblia_versiculos (libro_id, capitulo, versiculo, texto) VALUES (?, ?, ?, ?)", versiculos_a_insertar)
            print(f"   ✓ {nombre_libro} guardado.")
            
    conn.commit()
    conn.close()
    print(f"🎉 ¡Importación completada con éxito! Se insertaron {total_versiculos} versículos.")

if __name__ == "__main__":
    importar_biblia_json()