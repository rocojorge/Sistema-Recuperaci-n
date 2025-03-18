import time, os, json
from Practica1_1 import charge_config, extract, transform, load
import Practica1_2 as p2
import Practica1_3 as p3
import Practica1_4 as p4
import Practica1_5 as p5
import Practica1_6 as p6
import Practica1_7 as p7

config_file = "config.json"

def main():
    """Programa principal que procesa los archivos XML, crea diccionarios, índice invertido y calcula los pesos."""
    # Cargar la ruta de entrada
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
    stem_tokens = []

    # Procesamiento de cada archivo: extracción, transformación, stopper y stemming.
    for file in files:
        file_path = os.path.join(input_dir, file)
        extracted_data = extract(file_path)
        if not extracted_data:
            continue  # Saltar archivos sin metadatos válidos
        tokens = transform(extracted_data["text"])
        tokens1 = p2.stopper(tokens)
        tokens2 = p3.stem_words(tokens1)
        stem_tokens.append(tokens2)
        all_tokens.update(tokens2)
        
        load(file, tokens)
        load(file, tokens1, "stopper")
        load(file, tokens2, "stemmer")
        
        total_tokens += len(tokens)
        total_wo_stopwords += len(tokens1)
        total_wo_stopwords_and_stemmer += len(tokens2)
      
    print("Carpeta stemmer, stopper y tokens creada.")
    
    # Procesar archivos JSON generados en la carpeta de archivos ya stemmed
    input_dir = charge_config(config_file, "stemed_files")
    files = [f for f in os.listdir(input_dir) if f.endswith(".json")]
    
    # Creación de diccionarios de términos y documentos
    term2id, id2term = p4.enumeracion(all_tokens)
    doc2id, id2doc = p4.enum_docs(files)
    load("term2id.json", term2id, "term2id")
    load("id2term.json", id2term, "id2term")
    load("doc2id.json", doc2id, "doc2id")
    load("id2doc.json", id2doc, "id2doc")
    print("Archivos term2id, id2term, doc2id e id2doc creados.")
    
    # Creación del índice invertido
    idwordIter = iter(id2term)
    indice_full = {}
    print("Creando índice invertido...")
    second_start = time.time()
    for word in all_tokens:
        indice_invertido = []
        idword = next(idwordIter)
        iter_Stemm_tokens = iter(stem_tokens)
        for file in files:
            tokens = next(iter_Stemm_tokens)
            indice_invertido += p4.indice_invertido(idword, word, doc2id, file, tokens)
        indice_full.update({idword: indice_invertido})
        
    load("Indice_Invertido.json", indice_full, "indice_invertido")
    elapsed_time1 = time.time() - second_start
    print(f"Índice invertido creado en {elapsed_time1:.2f} segundos.")
    
    # Cálculo de pesos normalizados, IDF y generación de la matriz de documentos.
    print("Calculando pesos normalizados y generando matriz de documentos...")
    norm_index, term_idf, document_matrix = p5.calcular_todo(indice_full, doc2id, term2id)
    
    # Guardar resultados usando la función load
    load("Indice_Invertido_Pesos.json", norm_index, "indice_invertido_pesos")
    load("IDF.json", term_idf, "IDF")
    load("Matriz_Documentos.json", document_matrix, "matriz_documentos")
        
    query_file = "queries.txt"   # Fichero con consultas (una por línea)
    if os.path.exists(query_file):
        max_docs = 10   # Número máximo de documentos relevantes a devolver
        # Se pasan las estructuras ya cargadas: document_matrix, term_idf, term2id y id2doc.
        query_results, queries= p6.procesar_consultas_desde_fichero(query_file, max_docs, document_matrix, term_idf, term2id, id2doc)
    else:
        print("No se encontró el fichero de consultas (queries.txt).")
    #print (query_results) # Descomentar para ver los resultados de las consultas.
    
    p7.resultados_amplios(query_results, queries)
    p7.resultados_compactos(query_results)
    
    
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
