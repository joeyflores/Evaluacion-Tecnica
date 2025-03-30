from flask import Flask, request, jsonify, render_template, make_response
import sqlite3
import re
import unicodedata
import os
import json
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Para mostrar caracteres en UTF-8

# Obtener el directorio actual y definir la ruta de la base de datos
script_dir = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(script_dir, 'noticias.db')

# Preparar stopwords y el stemmer en español
spanish_stops = set(stopwords.words('spanish'))
stemmer = SnowballStemmer("spanish")

def limpiar_y_normalizar_query(texto):
    """Normaliza el texto de la query: minúsculas, sin tildes y aplica stemming."""
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = re.sub(r'[\u0300-\u036f]', '', texto)
    texto = re.sub(r'[^a-z\s]', ' ', texto)
    tokens = texto.split()
    tokens_stem = [stemmer.stem(t) for t in tokens if t not in spanish_stops]
    return " ".join(tokens_stem)

@app.route('/')
def home():
    # Renderiza la plantilla HTML ubicada en /templates/index.html
    return render_template("index.html")

@app.route('/buscar_noticias', methods=['GET'])
def buscar_noticias():
    # Obtener el término de búsqueda de la query string
    tema = request.args.get('tema', '').strip()
    if not tema:
        return jsonify({"error": "No se proporcionó el parámetro 'tema'"}), 400

    # Normalizar el término de búsqueda
    tema_normalizado = limpiar_y_normalizar_query(tema)
    if not tema_normalizado:
        return jsonify({"tema": tema, "noticias": []}), 200

    # Conectar a la base de datos y ejecutar la consulta
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT origen, fecha, titulo, canal, medio, resumen, frecuencias, texto_normalizado
        FROM noticias
        WHERE texto_normalizado LIKE ?
    """, (f"%{tema_normalizado}%",))
    rows = cursor.fetchall()
    conn.close()

    noticias = []
    for row in rows:
        origen = row[0]     # "youtube" o "web"
        fecha = row[1]
        titulo = row[2]
        canal = row[3]
        medio = row[4]
        resumen = row[5]
        frecuencias_json = row[6]  # Campo JSON con frecuencias

        # Construir el campo "fuente" según el origen
        if origen == 'youtube':
            fuente = f"YouTube ({canal})" if canal else "YouTube"
        else:
            fuente = f"Web ({medio})" if medio else "Web"

        # Obtener la frecuencia del término en la noticia (usando la columna "frecuencias")
        frecuencia = 0
        if frecuencias_json:
            try:
                freq_dict = json.loads(frecuencias_json)
                frecuencia = freq_dict.get(tema_normalizado, 0)
            except Exception:
                frecuencia = 0

        # Se agrega el campo temporal 'frecuencia' para ordenar
        noticia_item = {
            "titulo": titulo,
            "fuente": fuente,
            "fecha": fecha,
            "resumen": resumen,
            "frecuencia": frecuencia  # Campo temporal para ordenar
        }
        noticias.append(noticia_item)

    # Ordenar noticias por frecuencia (mayor a menor)
    noticias_ordenadas = sorted(noticias, key=lambda x: x["frecuencia"], reverse=True)
    # Eliminar el campo "frecuencia" del resultado final
    for noticia in noticias_ordenadas:
        noticia.pop("frecuencia", None)

    respuesta = {
        "tema": tema,
        "noticias": noticias_ordenadas
    }
    return jsonify(respuesta), 200

@app.route('/descargar_noticias', methods=['GET'])
def descargar_noticias():
    # Endpoint para descargar los resultados en un archivo JSON (sin el campo "resumen")
    tema = request.args.get('tema', '').strip()
    if not tema:
        return jsonify({"error": "No se proporcionó 'tema'"}), 400

    tema_normalizado = limpiar_y_normalizar_query(tema)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT origen, fecha, titulo, canal, medio
        FROM noticias
        WHERE texto_normalizado LIKE ?
    """, (f"%{tema_normalizado}%",))
    rows = cursor.fetchall()
    conn.close()

    noticias = []
    for row in rows:
        origen = row[0]
        fecha = row[1]
        titulo = row[2]
        canal = row[3]
        medio = row[4]

        if origen == 'youtube':
            fuente = f"YouTube ({canal})" if canal else "YouTube"
        else:
            fuente = f"Web ({medio})" if medio else "Web"

        noticias.append({
            "titulo": titulo,
            "fuente": fuente,
            "fecha": fecha
        })

    data = {
        "tema": tema,
        "noticias": noticias
    }
    # Convertir a JSON
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    resp = make_response(json_str, 200)
    resp.headers["Content-Type"] = "application/json; charset=utf-8"
    resp.headers["Content-Disposition"] = 'attachment; filename="noticias.json"'
    return resp

if __name__ == '__main__':
    app.run(debug=True)
