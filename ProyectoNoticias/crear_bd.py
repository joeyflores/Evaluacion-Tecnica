import sqlite3
import os

# Obtener el directorio actual y definir la ruta de la base de datos
script_dir = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(script_dir, 'noticias.db')

os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)  # Crea la carpeta si no existe
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS noticias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Para saber si viene de "youtube" o "web"
    origen TEXT,
    
    -- Columnas unificadas (ejemplos)
    fecha TEXT,          -- unifica FECHA (VIDEO) de YouTube y Fecha de Web
    titulo TEXT,         -- unifica TITULO de YouTube y Titular de Web
    resumen TEXT,        -- unifica RESUMEN de YouTube y Resumen de Web

    -- Columnas propias de YouTube
    canal TEXT,
    personas TEXT,
    organizaciones TEXT,
    ubicaciones TEXT,
    paises TEXT,
    productos TEXT,

    -- Columnas propias de Web
    medio TEXT,
    nombre TEXT,
    id_pauta TEXT,

    -- Columna para almacenar el texto normalizado (para búsquedas)
    texto_normalizado TEXT,
    
    -- Columna para almacenar las frecuencias de palabras (como JSON)
    frecuencias TEXT
);
""")

conn.commit()
conn.close()

print("Base de datos creada con la tabla 'noticias'.")
