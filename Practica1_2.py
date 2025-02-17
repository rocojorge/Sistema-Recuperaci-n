import nltk
nltk.download("stopwords")
from nltk.corpus import stopwords


def stopper(tokens):
    stop_words = set(stopwords.words('spanish'))
    tokens1 = []
    for token in tokens:
        if token not in stop_words:
            tokens1.append(token)
    
    la_words = ["los","les","le","la","lo","las"]
    for word in la_words:
        if word in tokens1:
            tokens1.remove(word)
    return tokens1

def main():
    print (stopper(["hola","lo", "como", "estas", "tu", "yo", "bien", "gracias", "por", "preguntar","los","les","le"])) 
    
if __name__ == "__main__":
    main()