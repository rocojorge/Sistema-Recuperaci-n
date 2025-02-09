import json
from bs4 import BeautifulSoup
import os,time, re

config_file="config.json"
Num_files=0

def charge_config(config_file):
    with open(config_file, "r") as file:
        config = json.load(file)
        
    for key in config:
        print(key, ":", config[key])
        dir_path = config["path_scielo"]
    
    return config      

List_files = os.listdir(dir_path) # Numero de archivos que hay en el directorio.

def extract(file_path):
    # Open the file
    with open(file_path, "r", encoding="utf-8") as file:
        # Read the file
        content = file.read()
        soup = BeautifulSoup(content, "xml")
        #Titulo
        title = soup.find("title" ,attrs={"xml:lang=es"}).get_text()
        #Fecha = soup.find("<dc:date").get_text()
        date = soup.find("datestamp").get_text()
        
    return content

def main():
    config = charge_config(config_file)
    List_files = os.listdir(config.get(""))
    
    #for file in List_files:
    
    pass

if __name__ == "__main__":
    main()