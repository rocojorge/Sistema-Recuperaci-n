from nltk.stem import SnowballStemmer
import nltk
nltk.download('punkt')


def stem_words(palabras):
    ps = SnowballStemmer("spanish")
    stemmed_words = [ps.stem(palabra) for palabra in palabras]
    return stemmed_words

if __name__ == "__main__":
    words = ["correr", "corriendo", "correrá", "correría", "corrido", "correremos", "correríamos"]
    stemmed_words = stem_words(words)
    print("Palabras originales:", words)
    print("Palabras cortadas:", stemmed_words)