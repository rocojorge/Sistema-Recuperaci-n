import time, os, json
from Practica1_1 import charge_config, extract, transform, load
import Practica1_2 as p2
import Practica1_3 as p3
import Practica1_4 as p4
import Practica1_5 as p5

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
    stem_tokens=[]

     #Aquí creamos los diccionarios de documentos
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
        load(file, tokens1,"stopper")
        load(file, tokens2,"stemmer")
        
        total_tokens += len(tokens)
        total_wo_stopwords += len(tokens1)
        total_wo_stopwords_and_stemmer += len(tokens2)
      
    print("Carpeta stemmer, stopper y tokens creada")
    
    # Procesar archivos JSON generados y crear diccionarios de términos y documentos
    input_dir = charge_config(config_file,"stemed_files")
    files=[]
    files = [f for f in os.listdir(input_dir) if f.endswith(".json")] 
    
    term2id, id2term = p4.enumeracion(all_tokens)
    doc2id, id2doc = p4.enum_docs(files)
    load("term2id.json", term2id, "term2id")
    load("id2term.json", id2term, "id2term")
    load("doc2id.json", doc2id, "doc2id")
    load("id2doc.json", id2doc, "id2doc")
    print("Archivos term2id, id2term, doc2id e id2doc creados")
    
    idwordIter = iter(id2term)
    indice_full={}
    print("Creando indice invertido")
    second_start = time.time()
    for word in all_tokens:
        indice_invertido=[]
        idword=next(idwordIter)
        iter_Stemm_tokens=iter(stem_tokens)
        for file in files:
            tokens=next(iter_Stemm_tokens)
            indice_invertido += p4.indice_invertido(idword,word, doc2id, file, tokens)
        indice_full.update({idword:indice_invertido})
        
    load("Indice_Invertido.json", indice_full, "indice_invertido")
    elapsed_time1 = time.time() - second_start
    print(f"Indice invertido creado en {elapsed_time1:.2f} segundos.")
    
    #Para el indice de frecuencias tengo que hacer un recorrido de los tokens y contar cuantas veces aparece cada uno en cada documento
    print("Calculando pesos normalizados...")    
    norm_index, term_idf = p5.calcular_pesos(indice_full, doc2id)
    # Guardar los resultados en disco
    load("Indice_Invertido_Pesos.json", norm_index, "indice_invertido_pesos")
    load("IDF.json", term_idf, "IDF")
    
    print("Cálculo de pesos normalizados completado.")
      
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
