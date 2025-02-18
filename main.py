import time, os, json
from Practica1_1 import charge_config, extract, transform, load
import Practica1_2 as p2
import Practica1_3 as p3



config_file = "config.json"


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
    total_wo_stopwords = 0
    total_wo_stopwords_and_stemmer = 0

    for file in files:
        file_path = os.path.join(input_dir, file)
        extracted_data = extract(file_path)
        if not extracted_data:
            continue  # Saltar archivos sin metadatos válidos

        tokens = transform(extracted_data["text"])
        tokens1 = p2.stopper(tokens)
        tokens2 = p3.stem_words(tokens1)
        load(file, tokens)
        load(file, tokens1,"stopper")
        load(file, tokens2,"stemmer")
        

        total_tokens += len(tokens)
        total_wo_stopwords += len(tokens1)
        total_wo_stopwords_and_stemmer += len(tokens2)
    
    elapsed_time = time.time() - start_time
    avg_tokens = total_tokens / total_files if total_files > 0 else 0
    avg_tokens1 = total_wo_stopwords / total_files if total_files > 0 else 0

    print(f"Procesamiento completado en {elapsed_time:.2f} segundos.")
    print(f"Archivos procesados: {total_files}")
    print(f"Total de tokens: {total_tokens}")
    print(f"Total sin stopwords: {total_wo_stopwords}")
    print(f"Total sin stopwords y stemmer: {total_wo_stopwords_and_stemmer}")
    print(f"Promedio de tokens por archivo: {avg_tokens:.2f}")
    print(f"Promedio de tokens sin stopwords por archivo: {avg_tokens1:.2f}")

if __name__ == "__main__":
    main()
