import sqlite3
import pandas as pd
import os

# Obtener el directorio actual y definir rutas relativas para la BD y los archivos Excel
script_dir = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(script_dir, 'noticias.db')
YOUTUBE_FILE = os.path.join(script_dir, 'youtube_noticias.xlsx')
WEB_FILE = os.path.join(script_dir, 'web_noticias.xlsx')

# Verificar que los archivos existan
if not os.path.exists(YOUTUBE_FILE):
    raise FileNotFoundError(f"No se encontró el archivo: {YOUTUBE_FILE}")
if not os.path.exists(WEB_FILE):
    raise FileNotFoundError(f"No se encontró el archivo: {WEB_FILE}")

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

def insertar_noticia(**kwargs):
     # Inserta una noticia en la tabla 'noticias'
    cursor.execute("""
        INSERT INTO noticias (
            origen,
            fecha,
            titulo,
            resumen,
            canal,
            personas,
            organizaciones,
            ubicaciones,
            paises,
            productos,
            medio,
            nombre,
            id_pauta,
            texto_normalizado,
            frecuencias
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        kwargs.get('origen'),
        kwargs.get('fecha'),
        kwargs.get('titulo'),
        kwargs.get('resumen'),
        kwargs.get('canal'),
        kwargs.get('personas'),
        kwargs.get('organizaciones'),
        kwargs.get('ubicaciones'),
        kwargs.get('paises'),
        kwargs.get('productos'),
        kwargs.get('medio'),
        kwargs.get('nombre'),
        kwargs.get('id_pauta'),
        kwargs.get('texto_normalizado'),  # Se dejará vacío y se actualizará luego
        kwargs.get('frecuencias')           # Se dejará vacío y se actualizará luego
    ))

# Cargar datos de YouTube (varias hojas)
youtube_excel = pd.ExcelFile(YOUTUBE_FILE)
for sheet_name in youtube_excel.sheet_names:
    df_youtube = pd.read_excel(YOUTUBE_FILE, sheet_name=sheet_name)
    for _, row in df_youtube.iterrows():
        fecha_raw = row.get('FECHA (VIDEO)', None)
        fecha_str = str(fecha_raw) if pd.notnull(fecha_raw) else None
        titulo_str = str(row.get('TITULO', '')) or None
        resumen_str = str(row.get('RESUMEN', '')) or None

        insertar_noticia(
            origen='youtube',
            fecha=fecha_str,
            titulo=titulo_str,
            resumen=resumen_str,
            canal=str(row.get('CANAL', '')) or None,
            personas=str(row.get('PERSONAS', '')) or None,
            organizaciones=str(row.get('ORGANIZACIONES', '')) or None,
            ubicaciones=str(row.get('UBICACIONES', '')) or None,
            paises=str(row.get('PAÍSES', '')) or None,
            productos=str(row.get('PRODUCTOS', '')) or None,
            medio=None,
            nombre=None,
            id_pauta=None,
            texto_normalizado=None,
            frecuencias=None
        )

conn.commit()

# Cargar datos de Web (pestaña "Resultados")
df_web = pd.read_excel(WEB_FILE, sheet_name='Resultados')
for _, row in df_web.iterrows():
    # Convertir valores y manejar datos nulos
    fecha_raw = row.get('Fecha', None)
    fecha_str = str(fecha_raw) if pd.notnull(fecha_raw) else None
    titulo_str = str(row.get('Titular', '')) or None
    resumen_str = str(row.get('Resumen', '')) or None

    insertar_noticia(
        origen='web',
        fecha=fecha_str,
        titulo=titulo_str,
        resumen=resumen_str,
        canal=None,
        personas=None,
        organizaciones=None,
        ubicaciones=None,
        paises=None,
        productos=None,
        medio=str(row.get('Medio', '')) or None,
        nombre=str(row.get('Nombre', '')) or None,
        id_pauta=str(row.get('ID Pauta', '')) or None,
        texto_normalizado=None,
        frecuencias=None
    )

conn.commit()
conn.close()

print("Datos de ambos Excel cargados en la tabla 'noticias' (texto_normalizado y frecuencias vacíos).")
