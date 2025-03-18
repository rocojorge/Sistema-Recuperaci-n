"""
Practica1_7.py: Finalización del sistema básico de recuperación de información.
Este módulo se encarga de formatear y mostrar los resultados finales de las consultas,
tanto en un formato amplio (más detallado) como en un formato compacto (ideal para competición).

Se asume que los resultados de las consultas se han obtenido previamente, es decir, que para cada
consulta disponemos de una lista ordenada de resultados (tuplas de (doc_id, similitud)), y que
además se dispone de un diccionario id2doc que mapea cada id de documento a su nombre/título.
"""

import Practica1_1 as p1
import os
import json





def retrieve_name(file, config_file="config.json"):
    """
    Obtiene el nombre de un documento a partir de su id.
    
    Args:
        file (str): Id del documento.
        
    Returns:
        str: Nombre del documento.
    """
    
    input_dir = p1.charge_config(config_file)
    if not os.path.exists(input_dir):
        print(f"Error: El directorio {input_dir} no existe.")
        return
    file_path = os.path.join(input_dir, file)
    extracted_data = p1.extract(file_path)
    return extracted_data["title"]
    
    

def resultados_amplios(query_results, queries, config_file="config.json"):
    """
    Muestra los resultados de las consultas de forma amplia.
    
    Args:
        query_results (dict): Diccionario con los resultados de las consultas.
        queries (list): Lista de consultas.
    """
    num = 1
    for query_id in queries:
        print(f"{queries[num-1]}")
        for doc_name in query_results[num]:
          print(f" Similitud obtenida: {doc_name} - {query_results[num][doc_name]}")
          xml_name = doc_name.replace(".json", ".xml")
          print(f" Nombre del documento: {retrieve_name(xml_name, config_file)}")
          print()          
        num += 1
        print()
        
def resultados_compactos(query_results):
    """
    Muestra los resultados de las consultas de forma compacta.
    
    Args:
        query_results (dict): Diccionario con los resultados de las consultas.
        queries (list): Lista de consultas.
    """
    num=0
    for query in query_results:
      for results in query_results[query]:
        print(f"{query} {results}")