import time
from Practica1_1 import transform   # Para normalizar y tokenizar el texto
import Practica1_2 as p2             # Para aplicar el stopper
import Practica1_3 as p3             # Para aplicar el stemmer

def procesar_consulta(text):
    """
    Preprocesa la consulta aplicando normalización, stopper y stemming.
    """
    print("Texto original de la consulta:", text)
    tokens = transform(text)
    print("Tokens tras transform:", tokens)
    tokens_sin_stop = p2.stopper(tokens)
    print("Tokens tras stopper:", tokens_sin_stop)
    tokens_stem = p3.stem_words(tokens_sin_stop)
    print("Tokens tras stemming:", tokens_stem)
    return tokens_stem

def calcular_tf_consulta(tokens):
    """
    Calcula la frecuencia de cada token en la consulta y la normaliza.
    """
    tf = {}
    for token in tokens:
        tf[token] = tf.get(token, 0) + 1
    if tf:
        max_freq = max(tf.values())
        for token in tf:
            tf[token] = tf[token] / max_freq
    print("TF normalizado de la consulta:", tf)
    return tf

def vectorizar_consulta(peso_consulta, term2id, mapping_tokens):
    """
    Crea un vector completo para la consulta en el mismo espacio que los documentos.
    Para cada término del vocabulario (según term2id), se asigna el peso calculado (si existe)
    o 0 en caso contrario.
    """
    vector = {}
    for token, tid in term2id.items():
        # Ahora se busca en peso_consulta utilizando el ID interno (tid)
        vector[tid] = peso_consulta.get(tid, 0)
    print("Vector completo de la consulta:", vector)
    
    for id in vector:
        if id in mapping_tokens:
            vector[id] = 1
        else:
            vector[id] = 0
    return vector

def dot_product(vector1, vector2):
    """
    Calcula el producto escalar entre dos vectores representados como diccionarios.
    Se asume que ambos tienen las mismas claves.
    """
    result = 0
    for key, val in vector1.items():
        result += val * vector2.get(key, 0)
    return result

def buscar_consulta(query_text, max_docs, document_matrix, idf, term2id, id2doc):
    """
    Procesa una consulta, traduce los tokens al espacio interno y calcula la similitud (producto escalar)
    entre la consulta y cada documento de la colección (representados en la misma dimensión).
    
    Parámetros:
      - query_text: Texto de la consulta.
      - max_docs: Número máximo de documentos a devolver.
      - document_matrix: Matriz de documentos (diccionario {doc_id: {term_id: weight, ...}}).
      - idf: Diccionario con el IDF de cada término (clave: término, en el lenguaje original).
      - term2id: Diccionario que asigna cada término (string) a su ID interno.
      - id2doc: Diccionario que asigna cada ID de documento a su nombre.
      
    Retorna:
      - resultados_con_nombre: Lista de tuplas (nombre_documento, similitud) ordenadas de mayor a menor.
      - tiempo: Tiempo empleado en calcular la similitud.
    """
    print("\n=== Procesando consulta ===")
    # Preprocesar la consulta (transform, stopper, stemming)
    tokens_query = procesar_consulta(query_text)
    tf_query = calcular_tf_consulta(tokens_query)
    
    # Traducir cada token al ID interno y calcular su peso (tf * idf)
    # Se genera un diccionario peso_consulta con claves igual al ID interno
    peso_consulta = {}
    mapping_tokens = []
    #print("Pesos de la consulta (tf * idf) (usando IDs):", peso_consulta)
    
    for name in tokens_query:
        for id in term2id:
          if name == id:
              mapping_tokens.append(term2id[id])
    print("Mapping de tokens de la consulta a IDs:", mapping_tokens)
    
    # Vectorizar la consulta: generar un vector completo en el mismo espacio que los documentos
    vector_consulta = vectorizar_consulta(peso_consulta, term2id, mapping_tokens)
    
    # Calcular la similitud: producto escalar entre el vector de consulta y el vector de cada documento
    sim_scores = {}
    inicio = time.time()
    for doc, doc_vector in document_matrix.items():
        sim = dot_product(vector_consulta, doc_vector)
        #print(f"Similitud para doc {doc}: {sim}")
        if sim > 0:
            sim_scores[doc] = sim
    tiempo = time.time() - inicio
    print("\nSimilitudes finales (sin ordenar):", sim_scores)
    
    # Ordenar y limitar los resultados
    resultados = [(doc, score) for doc, score in sim_scores.items()]
    resultados.sort(key=lambda x: x[1], reverse=True)
    resultados = resultados[:max_docs]
    
    # Mapear los doc IDs a nombres de documento
    resultados_con_nombre = [(id2doc.get(doc, doc), score) for doc, score in resultados]
    print("Resultados finales (con nombre):", resultados_con_nombre)
    print("Tiempo empleado en calcular la similitud:", tiempo)
    return resultados_con_nombre, tiempo

def procesar_consultas_desde_fichero(query_filename, max_docs, document_matrix, idf, term2id, id2doc):
    """
    Procesa múltiples consultas contenidas en un fichero (una consulta por línea).
    Para cada consulta se genera un fichero de resultados que incluye:
      - Tiempo en segundos empleado en calcular la similitud.
      - Listado de documentos relevantes (nombre y similitud).
    
    Parámetros:
      - query_filename: Nombre del fichero con las consultas.
      - max_docs: Número máximo de documentos a devolver por consulta.
      - document_matrix, idf, term2id, id2doc: Estructuras ya cargadas en memoria.
    """
    try:
        with open(query_filename, "r", encoding="utf-8") as f:
            consultas = f.readlines()
    except Exception as e:
        print(f"Error al abrir {query_filename}: {e}")
        return

    consultas = [c.strip() for c in consultas if c.strip()]
    print("\nConsultas encontradas en el fichero:", consultas)
    
    for i, consulta in enumerate(consultas, start=1):
        print(f"\n=== Consulta {i}: {consulta} ===")
        resultados, tiempo = buscar_consulta(consulta, max_docs, document_matrix, idf, term2id, id2doc)
        output_filename = f"resultado_consulta_{i}.txt"
        with open(output_filename, "w", encoding="utf-8") as fout:
            fout.write(f"Tiempo en calcular similitud: {tiempo:.4f} segundos\n")
            for doc, score in resultados:
                fout.write(f"{doc}: {score:.4f}\n")
        print(f"Resultados guardados en {output_filename}")
