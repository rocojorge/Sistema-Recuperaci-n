def enumeracion(words):
    dict1 = {} #term2id
    dict2 = {} #id2term
    for i,palabras in enumerate(words,start=117): #enumerate devuelve un indice y el valor de la lista
        id= str(i)+"t"
        dict2.update({id:palabras})
        dict1.update({palabras:id})
        #Los diccionarios de terminos son del 117t hacia delante hasta a saber cuantos
    return dict1,dict2

def enum_docs(files): #files:lista de documentos
    dict1 = {} #doc2id
    dict2 = {} #id2doc
    for i,doc in enumerate(files,start=177):
        id= str(i)+"d"
        dict2.update({id:doc})
        dict1.update({doc:id})
        #Los diccionarios de documentos son del 177d hacia delante hasta el 1177d que sería el último	
    return dict1,dict2

def indice_invertido(id2term,word,doc2id,files): #words:dict{id,term}, files:dict{id,doc}
    dictInvertido = {} #term2doc {idterm:(iddoc1,iddoc2,...)}
    idsFilesIn = []
    veces = 0
    for file in files:
        if word in file:
            for word1 in file:
                if word == word1:
                    veces += 1
            idsFilesIn.append({doc2id[file]:veces})
            veces=0
    dictInvertido= idsFilesIn
    
    return dictInvertido

def main():
    pass
if __name__ == "__main__":
    main()
        
    