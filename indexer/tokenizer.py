import re
import hashlib
from nltk.stem import PorterStemmer

class Tokenizer:
    
    def __init__(self):
        self.stemmer = PorterStemmer()
        self._token_pattern = re.compile(r"[A-Za-z0-9]+") 

    def compute_simhash(self, tokens: list) -> int:

        if not tokens: return 0
        v = [0] * 64
        
        for t in tokens:
            h = int(hashlib.md5(t.encode("utf-8")).hexdigest(), 16)
            for i in range(64):
                if h & (1 << i):
                    v[i] += 1
                else:
                    v[i] -= 1
        
        fingerprint = 0
        for i in range(64):
            if v[i] > 0:
                fingerprint |= (1 << i)
        
        return fingerprint

    def tokenize(self, text: str):

        if not text: 
            return [], 0

        raw_matches = [m for m in self._token_pattern.finditer(text.lower())]
        
        processed_tokens = []
        raw_token_strings = [] 
        
        for match in raw_matches:
            raw_text = match.group(0)
            raw_token_strings.append(raw_text)
            
            stemmed = self.stemmer.stem(raw_text)
            pos = match.start() 
            processed_tokens.append((stemmed, pos))

        fingerprint = self.compute_simhash(raw_token_strings)

        result = []
        result.extend(processed_tokens) 

        stems_only = [t[0] for t in processed_tokens]
        pos_only = [t[1] for t in processed_tokens]

        if len(stems_only) > 1:
            for i in range(len(stems_only) - 1):
                gram = f"{stems_only[i]} {stems_only[i+1]}"
                result.append((gram, pos_only[i]))

        return result, fingerprint