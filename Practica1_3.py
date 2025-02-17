from nltk.stem import PorterStemmer

def stem_words(words):
    ps = PorterStemmer()
    stemmed_words = [ps.stem(word) for word in words]
    return stemmed_words

if __name__ == "__main__":
    words = ["running", "jumps", "easily", "fairly"]
    stemmed_words = stem_words(words)
    print("Original words:", words)
    print("Stemmed words:", stemmed_words)