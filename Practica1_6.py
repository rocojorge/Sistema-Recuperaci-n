import time
import os
import json
from Practica1_1 import transform, extract
import Practica1_2 as p2
import Practica1_3 as p3
import numpy as np

# --- Mejora: Expansión de consulta (sinónimos) ---
def expand_query(tokens):
    """
    Expande la consulta usando un diccionario de sinónimos (ejemplo simple).
    """
    synonyms = {
        "ciencia": ["conocimiento", "estudio"],
        "salud": ["bienestar", "medicina"],
        # Puedes añadir más sinónimos según se requiera.
    }
    expanded = list(tokens)
    for token in tokens:
        if token in synonyms:
            expanded.extend(synonyms[token])
    return expanded

# --- Funciones básicas de procesamiento de consulta ---
def procesar_consulta(text, use_expansion=False):
    """
    Preprocesa la consulta aplicando normalización, stopper y stemming.
    Opcionalmente expande la consulta con sinónimos.
    """
    tokens = transform(text)  # Usa la tokenización básica; se puede ajustar a subpalabras si se requiere.
    tokens = p2.stopper(tokens)
    tokens = p3.stem_words(tokens)
    if use_expansion:
        tokens = expand_query(tokens)
    return tokens

def calcular_tf_consulta(tokens):
    tf = {}
    for token in tokens:
        tf[token] = tf.get(token, 0) + 1
    if tf:
        max_freq = max(tf.values())
        for token in tf:
            tf[token] = tf[token] / max_freq
    return tf

def vectorizar_consulta(peso_consulta, term2id, mapping_tokens):
    vector = {}
    for token, tid in term2id.items():
        vector[tid] = peso_consulta.get(tid, 0)
    # Asignar 1 a los términos que aparecen en la consulta (por simplicidad)
    for tid in mapping_tokens:
        vector[tid] = 1
    return vector

def dot_product(vector1, vector2):
    result = 0
    for key, val in vector1.items():
        result += val * vector2.get(key, 0)
    return result

# --- Búsqueda usando TF-IDF (método original) ---
def buscar_consulta_tfidf(query_text, max_docs, document_matrix, idf, term2id, id2doc, use_expansion=False):
    tokens_query = procesar_consulta(query_text, use_expansion)
    tf_query = calcular_tf_consulta(tokens_query)
    peso_consulta = {}
    mapping_tokens = []
    for token in tokens_query:
        if token in term2id:
            mapping_tokens.append(term2id[token])
    vector_consulta = vectorizar_consulta(peso_consulta, term2id, mapping_tokens)
    sim_scores = {}
    inicio = time.time()
    for doc, doc_vector in document_matrix.items():
        sim = dot_product(vector_consulta, doc_vector)
        if sim > 0:
            sim_scores[doc] = sim
    tiempo = time.time() - inicio
    resultados = [(doc, score) for doc, score in sim_scores.items()]
    resultados.sort(key=lambda x: x[1], reverse=True)
    resultados = resultados[:max_docs]
    resultados_con_nombre = [(id2doc.get(doc, doc), score) for doc, score in resultados]
    return resultados_con_nombre, tiempo

# --- Mejora 1: Pseudo-realimentación (PRF) ---
def get_top_terms_from_doc(doc_filename, num_terms=5):
    """
    Lee el archivo JSON de tokens (guardado en la carpeta "tokens") y devuelve los términos más frecuentes.
    """
    json_file = os.path.join("tokens", doc_filename.replace(".xml", ".json"))
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            tokens = json.load(f)
        freq = {}
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1
        sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        top_tokens = [t for t, _ in sorted_tokens[:num_terms]]
        return top_tokens
    except Exception as e:
        return []

def aplicar_prf(query_text, initial_results, num_docs=5, num_terms=5):
    """
    Expande la consulta original con los términos más frecuentes de los N primeros documentos.
    """
    expanded_terms = []
    count = 0
    for doc_name, _ in initial_results:
        if count >= num_docs:
            break
        top_terms = get_top_terms_from_doc(doc_name, num_terms)
        expanded_terms.extend(top_terms)
        count += 1
    nueva_consulta = query_text + " " + " ".join(expanded_terms)
    return nueva_consulta

# --- Mejora 4: Búsqueda usando BM25 ---
def buscar_consulta_bm25(query_text, max_docs, inverted_index, idf_bm25, avgdl, tokens_per_doc, term2id, id2doc, k1=1.5, b=0.75):
    """
    Calcula la puntuación BM25 para cada documento en función de la consulta.
    """
    tokens_query = procesar_consulta(query_text)
    sim_scores = {}
    inicio = time.time()
    # Para cada término de la consulta:
    for token in tokens_query:
        if token not in term2id:
            continue
        # Buscar en el índice invertido
        postings = inverted_index.get(token, [])
        for posting in postings:
            for doc, freq in posting.items():
                f = float(freq)
                dl = tokens_per_doc.get(doc, 0)
                score = idf_bm25.get(token, 0) * (f * (k1 + 1)) / (f + k1 * (1 - b + b * (dl / avgdl)))
                sim_scores[doc] = sim_scores.get(doc, 0) + score
    tiempo = time.time() - inicio
    resultados = [(doc, score) for doc, score in sim_scores.items() if score > 0]
    resultados.sort(key=lambda x: x[1], reverse=True)
    resultados = resultados[:max_docs]
    resultados_con_nombre = [(id2doc.get(doc, doc), score) for doc, score in resultados]
    return resultados_con_nombre, tiempo

# --- Mejora 5: Búsqueda usando LSI ---
def transformar_consulta_lsi(query_text, term2id, Vt, k=100):
    """
    Genera el vector de la consulta en el espacio reducido LSI.
    Se genera un vector en el espacio original y se proyecta usando Vt.T (reducción a k dimensiones).
    """
    tokens_query = procesar_consulta(query_text)
    vector = np.zeros(len(term2id))
    for token in tokens_query:
        if token in term2id:
            idx = list(term2id.values()).index(term2id[token])
            vector[idx] = 1  # Se puede usar TF o peso de la consulta
    # Proyectar al espacio LSI
    vector_reducido = np.dot(vector, Vt.T[:, :k])
    return vector_reducido

def buscar_consulta_lsi(query_text, reduced_doc_matrix, Vt, term2id, id2doc, k=100):
    """
    Compara la consulta proyectada en el espacio LSI con los documentos reducidos.
    """
    vector_query = transformar_consulta_lsi(query_text, term2id, Vt, k)
    sim_scores = {}
    for doc, vec in reduced_doc_matrix.items():
        sim = np.dot(vector_query, vec) / (np.linalg.norm(vector_query) * np.linalg.norm(vec) + 1e-6)
        if sim > 0:
            sim_scores[doc] = sim
    resultados = [(doc, score) for doc, score in sim_scores.items()]
    resultados.sort(key=lambda x: x[1], reverse=True)
    resultados_con_nombre = [(id2doc.get(doc, doc), score) for doc, score in resultados]
    return resultados_con_nombre

# --- Mejora 7: Búsqueda usando embeddings con modelos del lenguaje ---
def buscar_consulta_embedding(query_text, document_texts, id2doc, model_name="sentence-transformers/all-MiniLM-L6-v2", max_docs=10):
    """
    Codifica la consulta y los documentos usando un modelo de sentence transformers
    y retorna los documentos ordenados por similitud de coseno.
    document_texts: diccionario {doc_id: texto completo del documento}
    """
    try:
        from sentence_transformers import SentenceTransformer, util
    except ImportError:
        print("El paquete sentence-transformers no está instalado.")
        return [], 0
    model = SentenceTransformer(model_name)
    query_emb = model.encode(query_text, convert_to_tensor=True)
    doc_ids = list(document_texts.keys())
    doc_texts = [document_texts[doc] for doc in doc_ids]
    doc_embs = model.encode(doc_texts, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_emb, doc_embs)[0]
    cos_scores = cos_scores.cpu().numpy()
    # Ordenar y tomar los max_docs
    indices = np.argsort(-cos_scores)[:max_docs]
    resultados = [(id2doc.get(doc_ids[i], doc_ids[i]), float(cos_scores[i])) for i in indices if cos_scores[i] > 0]
    return resultados, 0  # Tiempo no calculado para embeddings

# --- Procesar múltiples consultas desde archivo ---
def procesar_consultas_desde_fichero(query_filename, max_docs, document_matrix, idf, term2id, id2doc, 
                                     inverted_index=None, tokens_per_doc=None, bm25_params=None, 
                                     reduced_doc_matrix=None, Vt=None, document_texts=None,
                                     scoring_method="tfidf", use_expansion=False, use_prf=False):
    """
    Procesa consultas desde un fichero y permite elegir el método de scoring:
      - "tfidf" (por defecto)
      - "bm25"
      - "lsi"
      - "embedding"
    Además, se pueden activar la expansión de consulta y pseudo-realimentación (PRF).
    """
    to_return = {}
    resultados_totales = {}
    try:
        with open(query_filename, "r", encoding="utf-8") as f:
            consultas = f.readlines()
    except Exception as e:
        print(f"Error al abrir {query_filename}: {e}")
        return
    consultas = [c.strip() for c in consultas if c.strip()]
    
    for i, consulta in enumerate(consultas, start=1):
        # Primer proceso: método elegido
        if scoring_method == "bm25":
            resultados, tiempo = buscar_consulta_bm25(consulta, max_docs, inverted_index, bm25_params[0], bm25_params[1], tokens_per_doc, term2id, id2doc)
        elif scoring_method == "lsi":
            resultados = buscar_consulta_lsi(consulta, reduced_doc_matrix, Vt, term2id, id2doc)
            tiempo = 0
        elif scoring_method == "embedding":
            resultados, tiempo = buscar_consulta_embedding(consulta, document_texts, id2doc, max_docs=max_docs)
        else:
            # tfidf por defecto
            resultados, tiempo = buscar_consulta_tfidf(consulta, max_docs, document_matrix, idf, term2id, id2doc, use_expansion)
        
        # Si se activa PRF, se expande la consulta y se vuelve a buscar (usamos tfidf para el ejemplo)
        if use_prf and scoring_method == "tfidf":
            nueva_consulta = aplicar_prf(consulta, resultados)
            resultados, tiempo = buscar_consulta_tfidf(nueva_consulta, max_docs, document_matrix, idf, term2id, id2doc, use_expansion)
        
        output_filename = f"resultado_consulta_{i}.txt"
        with open(output_filename, "w", encoding="utf-8") as fout:
            fout.write(f"Tiempo en calcular similitud: {tiempo:.4f} segundos\n")
            for doc, score in resultados:
                fout.write(f"{doc}: {score:.4f}\n")
        resultados_totales[i] = {doc: score for doc, score in resultados}
    return resultados_totales, consultas
