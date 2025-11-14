import re
from nltk.stem import PorterStemmer

class Tokenizer:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.token_pattern = re.compile(r"[a-zA-Z0-9]+")  

    def tokenize(self, text, weight=1):
        tokens = []
        for match in self.token_pattern.finditer(text.lower()):
            raw = match.group(0)
            stemmed = self.stemmer.stem(raw)
            tokens.append((stemmed, weight))
        return tokens

    def tokenize_normal_and_important(self, normal_text, important_text):
        result = []
        if normal_text:
            result.extend(self.tokenize(normal_text, weight=1))
        if important_text:
            result.extend(self.tokenize(important_text, weight=2))
        return result
