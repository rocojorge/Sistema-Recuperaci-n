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
import math
import json

def calcular_frecuencia_maxima(inverted_index):
    """
    Calcula la frecuencia máxima de cualquier término en cada documento.
    
    Parámetro:
      - inverted_index: Diccionario en el que cada clave es un término y el valor es una lista de publicaciones,
        cada una con {doc_id: frecuencia}.
    
    Retorna:
      - doc_max_freq: Diccionario con, para cada documento, su frecuencia máxima.
    """
    doc_max_freq = {}
    for term, postings in inverted_index.items():
        for posting in postings:
            for doc, freq in posting.items():
                freq = float(freq)
                if doc not in doc_max_freq or freq > doc_max_freq[doc]:
                    doc_max_freq[doc] = freq
    return doc_max_freq

def calcular_idf(inverted_index, N):
    """
    Calcula la inversa de la frecuencia documental (IDF) para cada término.
    
    Parámetros:
      - inverted_index: Índice invertido con las frecuencias de términos.
      - N: Número total de documentos.
      
    Retorna:
      - term_idf: Diccionario que asocia a cada término su IDF calculado.
    """
    term_idf = {}
    for term, postings in inverted_index.items():
        dfi = len(postings)
        idf = math.log2(N / dfi) if dfi > 0 else 0
        term_idf[term] = idf
    return term_idf

def calcular_pesos_sin_normalizar(inverted_index, doc_max_freq, term_idf):
    """
    Calcula los pesos sin normalizar (TF * IDF) para cada término en cada documento.
    
    Parámetros:
      - inverted_index: Índice invertido con las frecuencias.
      - doc_max_freq: Diccionario con la frecuencia máxima de cada documento.
      - term_idf: Diccionario con los valores IDF para cada término.
      
    Retorna:
      - weighted_index: Índice invertido con los pesos sin normalizar.
      - doc_weight_sums: Diccionario con la suma de los cuadrados de los pesos para cada documento.
    """
    weighted_index = {}
    doc_weight_sums = {}
    for term, postings in inverted_index.items():
        idf = term_idf[term]
        new_postings = []
        for posting in postings:
            for doc, freq in posting.items():
                freq = float(freq)
                tf = freq / doc_max_freq[doc]  # Normalización de la frecuencia (TF)
                weight = tf * idf            # Peso sin normalizar
                new_postings.append({doc: weight})
                doc_weight_sums[doc] = doc_weight_sums.get(doc, 0) + weight ** 2
        weighted_index[term] = new_postings
    return weighted_index, doc_weight_sums

def normalizar_pesos(weighted_index, doc_weight_sums):
    """
    Normaliza los pesos de cada documento dividiendo por la norma (raíz de la suma de cuadrados).
    
    Parámetros:
      - weighted_index: Índice invertido con pesos sin normalizar.
      - doc_weight_sums: Suma de cuadrados de los pesos para cada documento.
      
    Retorna:
      - normalized_index: Índice invertido con los pesos normalizados.
    """
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
    return normalized_index

def generar_matriz_documentos(normalized_index, doc2id, term2id):
    """
    Genera una matriz completa en forma de diccionario, donde cada clave es el ID de un documento y el valor 
    es un diccionario que contiene, para cada término (según term2id), el peso normalizado si aparece o 0 en caso contrario.
    
    Parámetros:
      - normalized_index: Índice invertido con pesos normalizados (clave: término, valor: lista de publicaciones).
      - doc2id: Diccionario con la asignación de documentos a sus IDs.
      - term2id: Diccionario con la asignación de términos a sus IDs.
      
    Retorna:
      - documents: Diccionario con la matriz documento–términos.
    """
    # Inicializar la matriz: para cada documento, asignar 0 a cada término.
    documents = {doc: {term: 0 for term in term2id.values()} for doc in doc2id.values()}
    # Rellenar la matriz con los pesos normalizados.
    for term, postings in normalized_index.items():
        for posting in postings:
            for doc, weight in posting.items():
                if doc in documents:
                    # 'term' ya es la clave del término (por ejemplo, un id como "117t")
                    documents[doc][term] = weight
    return documents

def calcular_todo(inverted_index, doc2id, term2id):
    """
    Ejecuta el proceso completo de cálculo de pesos según el Modelo Espacio Vectorial:
      - Normaliza las frecuencias (TF) de cada documento.
      - Calcula la IDF para cada término.
      - Calcula los pesos sin normalizar y luego los normaliza.
      - Genera una matriz completa de documentos con todos los términos.
    
    Parámetros:
      - inverted_index: Índice invertido con las frecuencias de términos.
      - doc2id: Diccionario que asocia cada documento a su ID.
      - term2id: Diccionario que asocia cada término a su ID.
      
    Retorna:
      - normalized_index: Índice invertido con los pesos normalizados.
      - term_idf: Diccionario con los valores IDF para cada término.
      - document_matrix: Matriz completa de documentos, donde cada documento contiene los pesos de todos los términos.
    """
    N = len(doc2id)
    doc_max_freq = calcular_frecuencia_maxima(inverted_index)
    term_idf = calcular_idf(inverted_index, N)
    weighted_index, doc_weight_sums = calcular_pesos_sin_normalizar(inverted_index, doc_max_freq, term_idf)
    normalized_index = normalizar_pesos(weighted_index, doc_weight_sums)
    document_matrix = generar_matriz_documentos(normalized_index, doc2id, term2id)
    return normalized_index, term_idf, document_matrix
