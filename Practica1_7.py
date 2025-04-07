import Practica1_1 as p1
import os

def retrieve_name(file, config_file="config.json"):
    input_dir = p1.charge_config(config_file)
    if not os.path.exists(input_dir):
        print(f"Error: El directorio {input_dir} no existe.")
        return
    file_path = os.path.join(input_dir, file)
    extracted_data = p1.extract(file_path)
    return extracted_data["title"]

def get_categories(file, config_file="config.json"):
    """
    Extrae las categorías (por ejemplo, keywords) del documento.
    """
    input_dir = p1.charge_config(config_file)
    file_path = os.path.join(input_dir, file)
    extracted_data = p1.extract(file_path)
    return extracted_data.get("keywords", [])

def filtrar_por_categoria(resultados, config_file="config.json"):
    """
    Permite al usuario filtrar los resultados por alguna categoría.
    """
    categoria = input("Introduce la categoría por la que deseas filtrar (o 'no' para omitir): ").strip().lower()
    if categoria == "no":
        return resultados
    resultados_filtrados = {}
    for query_id, docs in resultados.items():
        filtrados = {}
        for doc, score in docs.items():
            # Convertir el nombre del documento JSON a nombre XML (se asume que se puede reconstruir)
            xml_name = doc.replace(".json", ".xml")
            cats = get_categories(xml_name, config_file)
            # Si la categoría está entre los keywords (comparación en minúsculas)
            if any(categoria in cat.lower() for cat in cats):
                filtrados[doc] = score
        resultados_filtrados[query_id] = filtrados
    return resultados_filtrados

def resultados_amplios(query_results, queries, config_file="config.json"):
    num = 1
    for query_id in queries:
        print(f"Consulta: {queries[num-1]}")
        for doc_name in query_results[num]:
            print(f" Similitud obtenida: {doc_name} - {query_results[num][doc_name]}")
            xml_name = doc_name.replace(".json", ".xml")
            print(f" Nombre del documento: {retrieve_name(xml_name, config_file)}")
            print()
        num += 1
        print()

def resultados_compactos(query_results):
    for query in query_results:
        for doc, score in query_results[query].items():
            print(f"{query} {doc} {score:.4f}")
