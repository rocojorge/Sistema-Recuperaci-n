import math
import json

def calcular_pesos(inverted_index, doc2id):
    """
    Calcula los pesos normalizados y los valores IDF a partir del índice invertido y el diccionario de documentos.
    
    Parámetros:
      - inverted_index: Índice invertido con las frecuencias de términos.
      - doc2id: Diccionario que asigna identificadores a documentos.
      
    Retorna:
      - normalized_index: Índice invertido con pesos normalizados.
      - term_idf: Diccionario con el IDF de cada término.
    """
    N = len(doc2id)
    
    # 1. Calcular la frecuencia máxima por documento
    doc_max_freq = {}
    for term, postings in inverted_index.items():
        for posting in postings:
            for doc, freq in posting.items():
                freq = float(freq)
                if doc not in doc_max_freq or freq > doc_max_freq[doc]:
                    doc_max_freq[doc] = freq
    
    # 2. Calcular el IDF para cada término: idf = log2(N / dfi)
    term_idf = {}
    for term, postings in inverted_index.items():
        dfi = len(postings)
        idf = math.log2(N / dfi) if dfi > 0 else 0
        term_idf[term] = idf

    # 3. Calcular los pesos sin normalizar: peso = (fij / fmax) * idf
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

    # 4. Calcular la norma (módulo) del vector de pesos para cada documento
    doc_norm = {doc: math.sqrt(sum_sq) for doc, sum_sq in doc_weight_sums.items()}

    # 5. Calcular los pesos normalizados: peso_normalizado = peso / norma del documento
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
