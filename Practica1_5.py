import math
import json
import numpy as np

def calcular_pesos(inverted_index, doc2id):
    # (Función original sin cambios)
    N = len(doc2id)
    doc_max_freq = {}
    for term, postings in inverted_index.items():
        for posting in postings:
            for doc, freq in posting.items():
                freq = float(freq)
                if doc not in doc_max_freq or freq > doc_max_freq[doc]:
                    doc_max_freq[doc] = freq
    term_idf = {}
    for term, postings in inverted_index.items():
        dfi = len(postings)
        idf = math.log2(N / dfi) if dfi > 0 else 0
        term_idf[term] = idf
    weighted_index = {}
    doc_weight_sums = {}
    for term, postings in inverted_index.items():
        idf = term_idf[term]
        new_postings = []
        for posting in postings:
            for doc, freq in posting.items():
                freq = float(freq)
                max_freq = doc_max_freq[doc]
                tf = freq / max_freq
                weight = tf * idf
                new_postings.append({doc: weight})
                doc_weight_sums[doc] = doc_weight_sums.get(doc, 0) + weight ** 2
        weighted_index[term] = new_postings
    doc_norm = {doc: math.sqrt(sum_sq) for doc, sum_sq in doc_weight_sums.items()}
    normalized_index = {}
    for term, postings in weighted_index.items():
        norm_postings = []
        for posting in postings:
            for doc, weight in posting.items():
                norm = doc_norm[doc]
                weight_norm = weight / norm if norm != 0 else 0
                norm_postings.append({doc: weight_norm})
        normalized_index[term] = norm_postings
    return normalized_index, term_idf

# --- Mejora 4: BM25 ---
def calcular_bm25_params(inverted_index, doc2id, tokens_per_doc, k1=1.5, b=0.75):
    """
    Calcula el IDF (según BM25) y parámetros necesarios para la fórmula BM25.
    tokens_per_doc: diccionario con la cantidad de tokens de cada documento.
    Retorna: idf_bm25 (diccionario) y avgdl (longitud media de documentos).
    """
    N = len(doc2id)
    avgdl = sum(tokens_per_doc.values()) / N if N > 0 else 0
    idf_bm25 = {}
    for term, postings in inverted_index.items():
        dfi = len(postings)
        # Fórmula BM25 para IDF
        idf = max(0, math.log((N - dfi + 0.5) / (dfi + 0.5) + 1))
        idf_bm25[term] = idf
    return idf_bm25, avgdl

# --- Mejora 5: Indexación con Semántica Latente (LSI) ---
def lsi_transform(document_matrix, k=100):
    """
    Aplica SVD a la matriz de documentos y reduce la dimensionalidad a k.
    document_matrix: diccionario {doc_id: {term_id: weight}}
    Retorna:
       - reduced_doc_matrix: diccionario con representación reducida de cada documento.
       - U, S, Vt: matrices resultantes de la SVD.
       - term_ids: lista de términos (para saber el orden de columnas)
    """
    doc_ids = list(document_matrix.keys())
    term_ids = list(next(iter(document_matrix.values())).keys())
    matrix = np.array([[document_matrix[doc][term] for term in term_ids] for doc in doc_ids])
    U, S, Vt = np.linalg.svd(matrix, full_matrices=False)
    U_k = U[:, :k]
    S_k = np.diag(S[:k])
    reduced_matrix = np.dot(U_k, S_k)
    reduced_doc_matrix = {doc: reduced_matrix[i] for i, doc in enumerate(doc_ids)}
    return reduced_doc_matrix, U, S, Vt, term_ids

def generar_matriz_documentos(normalized_index, doc2id, term2id):
    # (Función original sin cambios)
    documents = {doc: {term: 0 for term in term2id.values()} for doc in doc2id.values()}
    for term, postings in normalized_index.items():
        for posting in postings:
            for doc, weight in posting.items():
                if doc in documents:
                    documents[doc][term] = weight
    return documents

def calcular_todo(inverted_index, doc2id, term2id):
    N = len(doc2id)
    doc_max_freq = {}
    for term, postings in inverted_index.items():
        for posting in postings:
            for doc, freq in posting.items():
                freq = float(freq)
                if doc not in doc_max_freq or freq > doc_max_freq[doc]:
                    doc_max_freq[doc] = freq
    term_idf = {}
    for term, postings in inverted_index.items():
        dfi = len(postings)
        idf = math.log2(N / dfi) if dfi > 0 else 0
        term_idf[term] = idf
    weighted_index = {}
    doc_weight_sums = {}
    for term, postings in inverted_index.items():
        idf = term_idf[term]
        new_postings = []
        for posting in postings:
            for doc, freq in posting.items():
                freq = float(freq)
                tf = freq / doc_max_freq[doc]
                weight = tf * idf
                new_postings.append({doc: weight})
                doc_weight_sums[doc] = doc_weight_sums.get(doc, 0) + weight ** 2
        weighted_index[term] = new_postings
    normalized_index = {}
    for term, postings in weighted_index.items():
        norm_postings = []
        for posting in postings:
            for doc, weight in posting.items():
                norm = math.sqrt(doc_weight_sums[doc])
                weight_norm = weight / norm if norm != 0 else 0
                norm_postings.append({doc: weight_norm})
        normalized_index[term] = norm_postings
    document_matrix = generar_matriz_documentos(normalized_index, doc2id, term2id)
    return normalized_index, term_idf, document_matrix
