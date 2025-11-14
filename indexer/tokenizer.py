import re
from collections import Counter
from nltk.stem import PorterStemmer


class Tokenizer:
    
    def __init__(self):
        self.stemmer = PorterStemmer()
        self._token_pattern = re.compile(r"[A-Za-z0-9]+") 

    def _tokenize_with_weight(self, text: str, weight: int):
        if not text:
            return []

        tokens = []
        for match in self._token_pattern.finditer(text.lower()):
            raw = match.group(0)
            stemmed = self.stemmer.stem(raw)
            tokens.append((stemmed, weight))
        return tokens

    def tokenize_normal_and_important(self, normal_text: str, important_text: str):
        result = []
        if normal_text:
            result.extend(self._tokenize_with_weight(normal_text, 1))
        if important_text:
            result.extend(self._tokenize_with_weight(important_text, 2))
        return result

    @staticmethod
    def to_tf_counter(token_weight_pairs):
        tf = Counter()
        for token, weight in token_weight_pairs:
            tf[token] += weight
        return tf
