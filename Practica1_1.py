import json
import os
import time
import re
from bs4 import BeautifulSoup



# Archivo de configuración
config_file = "config.json"

def charge_config(config_file,path_to_charge="env_files"):
    """Carga la configuración desde el archivo JSON, asegurando codificación UTF-8."""
    with open(config_file, "r", encoding="utf-8") as file:
        config = json.load(file)
    
    # Extraer y normalizar la ruta de los archivos XML
    path_scielo = config.get(path_to_charge, [{}])[0].get("path_scielo", "")
    path_scielo = os.path.normpath(path_scielo)  # Normalizar ruta para evitar problemas
    path_scielo = path_scielo.encode('utf-8').decode('utf-8')  # Asegurar correcta codificación

    return path_scielo

def extract(file_path):
    """Extrae título, texto, fecha, autores y palabras clave en español de un archivo XML."""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    soup = BeautifulSoup(content, "xml")

    # Buscar metadatos dentro de <metadata><oai-dc:dc>
    metadata = soup.find("oai-dc:dc")
    if not metadata:
        print(f"Error: No se encontraron metadatos en {file_path}")
        return None
    
    # Extraer título en español
    title_tag = metadata.find("dc:title", attrs={"xml:lang": "es"})
    title = title_tag.get_text(strip=True) if title_tag else "Título no encontrado"

    # Extraer descripción (contenido del artículo) en español
    text_tag = metadata.find("dc:description", attrs={"xml:lang": "es"})
    text = text_tag.get_text(separator=" ", strip=True) if text_tag else "Texto no encontrado"

    # Extraer fecha
    date_tag = metadata.find("dc:date")
    date = date_tag.get_text(strip=True) if date_tag else "Fecha no encontrada"

    # Extraer autores
    authors = [creator.get_text(strip=True) for creator in metadata.find_all("dc:creator")]

    # Extraer palabras clave en español
    keywords = [subject.get_text(strip=True) for subject in metadata.find_all("dc:subject")]

    return {
        "title": title,
        "date": date,
        "authors": authors,
        "keywords": keywords,
        "text": text
    }

def transform(text):
    """Normaliza y tokeniza el texto."""
    text = text.lower()  # Convertir a minúsculas
    text = re.sub(r"[^a-záéíóúüñ0-9_\-\n ]", "", text)  # Filtrar caracteres extraños
    tokens = text.split()  # Tokenizar (convertir a lista de palabras)
    return tokens

def load(file_name, tokens, output_dir="tokens"):
    """Guarda la lista de tokens en un archivo JSON."""
    os.makedirs(output_dir, exist_ok=True)  # Crear directorio si no existe
    output_path = os.path.join(output_dir, file_name.replace(".xml", ".json"))

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(tokens, file, ensure_ascii=False, indent=2)

def main():
    """Programa principal que procesa todos los archivos XML de la colección."""
    input_dir = charge_config(config_file)

    if not os.path.exists(input_dir):
        print(f"Error: El directorio {input_dir} no existe.")
        return
    
    files = [f for f in os.listdir(input_dir) if f.endswith(".xml")]
    total_files = len(files)
    
    print(f"Procesando {total_files} archivos en {input_dir}...")

    start_time = time.time()
    total_tokens = 0

    for file in files:
        file_path = os.path.join(input_dir, file)
        extracted_data = extract(file_path)
        if not extracted_data:
            continue  # Saltar archivos sin metadatos válidos

        tokens = transform(extracted_data["text"])
        load(file, tokens)

        total_tokens += len(tokens)
    
    elapsed_time = time.time() - start_time
    avg_tokens = total_tokens / total_files if total_files > 0 else 0

    print(f"Procesamiento completado en {elapsed_time:.2f} segundos.")
    print(f"Archivos procesados: {total_files}")
    print(f"Total de tokens: {total_tokens}")
    print(f"Promedio de tokens por archivo: {avg_tokens:.2f}")

if __name__ == "__main__":
    main()
