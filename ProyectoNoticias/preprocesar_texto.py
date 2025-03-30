import sqlite3
import pandas as pd
import re
import os
import unicodedata
import json
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

# Obtener el directorio actual y definir la ruta de la base de datos
script_dir = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(script_dir, 'noticias.db')

# Leer los registros que aún no tienen texto_normalizado
conn = sqlite3.connect(DB_NAME)
df = pd.read_sql_query("""
    SELECT id, titulo, resumen
    FROM noticias
    WHERE texto_normalizado IS NULL
""", conn)
conn.close()

# Preparar stopwords y el stemmer en español
spanish_stops = set(stopwords.words('spanish'))
stemmer = SnowballStemmer("spanish")

def limpiar_y_normalizar(texto):
    # Convertir a minúsculas y eliminar tildes y caracteres no alfabéticos
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = re.sub(r'[\u0300-\u036f]', '', texto)
    texto = re.sub(r'[^a-z\s]', ' ', texto)
    tokens = texto.split()
    # Aplicar stemming y eliminar stopwords
    tokens_proc = [stemmer.stem(t) for t in tokens if t not in spanish_stops]
    # Calcular la frecuencia de las palabras
    freq_dict = dict(Counter(tokens_proc))
    return " ".join(tokens_proc), freq_dict

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

for i, row in df.iterrows():
    noticia_id = row["id"]
    titulo = row["titulo"] or ""
    resumen = row["resumen"] or ""
    
    texto_completo = titulo + " " + resumen
    texto_normalizado, freq_dict = limpiar_y_normalizar(texto_completo)
    frecuencias_json = json.dumps(freq_dict, ensure_ascii=False)
    
    cursor.execute("""
        UPDATE noticias
        SET texto_normalizado = ?, frecuencias = ?
        WHERE id = ?
    """, (texto_normalizado, frecuencias_json, noticia_id))

conn.commit()
conn.close()

print("Proceso de normalización completado. 'texto_normalizado' y 'frecuencias' actualizados.")
