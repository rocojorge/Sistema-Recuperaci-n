
import time, os, json
from Practica1_1 import charge_config, extract, transform, load
import Practica1_2 as p2
import Practica1_3 as p3
import Practica1_4 as p4

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
    all_tokens = set()

    # Aquí creamos los diccionarios de documentos
    for file in files:
        file_path = os.path.join(input_dir, file)
        extracted_data = extract(file_path)
        if not extracted_data:
            continue  # Saltar archivos sin metadatos válidos

        tokens = transform(extracted_data["text"])
        tokens1 = p2.stopper(tokens)
        tokens2 = p3.stem_words(tokens1)
        all_tokens.update(tokens2)
        load(file, tokens)
        load(file, tokens1, "stopper")
        load(file, tokens2, "stemmer")
        
        total_tokens += len(tokens)
        total_wo_stopwords += len(tokens1)
        total_wo_stopwords_and_stemmer += len(tokens2)
        
    term2id, id2term = p4.enumeracion(all_tokens)
    doc2id, id2doc = p4.enum_docs(files)
    load("term2id", term2id, "term2id")
    load("id2term", id2term, "id2term")

    # Construir el índice invertido
    dictInvertido = {}
    for word in all_tokens:
        term_id = term2id[word]
        dictInvertido = p4.indice_invertido(term2id, doc2id, files, dictInvertido)

    for term_id, inverted_index in dictInvertido.items():
        load(term_id, inverted_index, "indice_invertido")
        
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