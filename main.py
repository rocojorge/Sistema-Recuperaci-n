import time, os, json
from Practica1_1 import charge_config, extract, transform, load
import Practica1_2 as p2
import Practica1_3 as p3
import Practica1_4 as p4
import Practica1_5 as p5
import Practica1_6 as p6
import Practica1_7 as p7

# Parámetros de configuración (podrían leerse de config.json)
SCORING_METHOD = "tfidf"   # Opciones: "tfidf", "bm25", "lsi", "embedding"
USE_EXPANSION = True       # Mejora 2: Expansión de consulta
USE_PRF = True             # Mejora 1: Pseudo-realimentación
USE_CATEGORY_FILTER = True # Mejora 3: Filtrado por categorías

config_file = "config.json"

def main():
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
    tokens_per_doc = {}  # Para BM25: almacenar la cantidad de tokens de cada documento

    # Procesamiento de cada archivo
    for file in files:
        file_path = os.path.join(input_dir, file)
        extracted_data = extract(file_path)
        if not extracted_data:
            continue
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
        tokens_per_doc[file.replace(".xml", ".json")] = len(tokens2)
      
    print("Carpeta stemmer, stopper y tokens creada.")
    
    # Procesar archivos JSON de tokens stemmeados
    input_dir_stem = charge_config(config_file, "stemed_files")
    files_json = [f for f in os.listdir(input_dir_stem) if f.endswith(".json")]
    
    # Creación de diccionarios de términos y documentos
    term2id, id2term = p4.enumeracion(all_tokens)
    doc2id, id2doc = p4.enum_docs(files_json)
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
        for file in files_json:
            tokens = next(iter_Stemm_tokens)
            indice_invertido += p4.indice_invertido(idword, word, doc2id, file, tokens)
        indice_full.update({idword: indice_invertido})
        
    load("Indice_Invertido.json", indice_full, "indice_invertido")
    elapsed_time1 = time.time() - second_start
    print(f"Índice invertido creado en {elapsed_time1:.2f} segundos.")
    
    # Cálculo de pesos TF-IDF y generación de la matriz de documentos
    print("Calculando pesos normalizados y generando matriz de documentos (TF-IDF)...")
    norm_index, term_idf, document_matrix = p5.calcular_todo(indice_full, doc2id, term2id)
    load("Indice_Invertido_Pesos.json", norm_index, "indice_invertido_pesos")
    load("IDF.json", term_idf, "IDF")
    load("Matriz_Documentos.json", document_matrix, "matriz_documentos")
    
    # Preparar estructuras para BM25 (si se usa ese método)
    if SCORING_METHOD == "bm25":
        bm25_params = p5.calcular_bm25_params(indice_full, doc2id, tokens_per_doc)
    else:
        bm25_params = None

    # Preparar estructura para LSI (si se usa ese método)
    if SCORING_METHOD == "lsi":
        reduced_doc_matrix, U, S, Vt, term_ids = p5.lsi_transform(document_matrix, k=100)
    else:
        reduced_doc_matrix = Vt = None

    # Preparar textos completos de documentos para embeddings (si se usa ese método)
    if SCORING_METHOD == "embedding":
        document_texts = {}
        for file in files:
            file_path = os.path.join(input_dir, file)
            extracted = extract(file_path)
            if extracted:
                document_texts[file] = extracted["text"]
    else:
        document_texts = None

    query_file = "queries.txt"   # Fichero con consultas (una por línea)
    if os.path.exists(query_file):
        max_docs = 10
        query_results, queries = p6.procesar_consultas_desde_fichero(
            query_file, max_docs, document_matrix, term_idf, term2id, id2doc,
            inverted_index=indice_full, tokens_per_doc=tokens_per_doc,
            bm25_params=bm25_params, reduced_doc_matrix=reduced_doc_matrix, Vt=Vt,
            document_texts=document_texts,
            scoring_method=SCORING_METHOD, use_expansion=USE_EXPANSION, use_prf=USE_PRF
        )
    else:
        print("No se encontró el fichero de consultas (queries.txt).")
    
    # Filtrado por categorías si se activa
    if USE_CATEGORY_FILTER:
        query_results = p7.filtrar_por_categoria(query_results, config_file)
    
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
