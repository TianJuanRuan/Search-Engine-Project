import os
import json
from indexer.tokenizer import Tokenizer
from .ranker import Ranker

class SearchEngine:
    def __init__(self,
                 index_path: str = "final_index.txt",
                 offset_path: str = "index_offsets.json",
                 doc_map_path: str = "doc_map.json"):

        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index file not found: {index_path}")
        if not os.path.exists(offset_path):
            raise FileNotFoundError(f"Offsets file not found: {offset_path}")

        print("Loading Index Offsets...")
        with open(offset_path, "r", encoding="utf-8") as f:
            self.term_offsets = json.load(f)

        print("Loading Doc Map for count...")
        with open(doc_map_path, "r", encoding="utf-8") as f:
            doc_map = json.load(f)
            self.N = len(doc_map)

        self.index_file = open(index_path, "r", encoding="utf-8")

        self.tokenizer = Tokenizer()
        self.ranker = Ranker(total_docs=self.N, doc_map_path=doc_map_path)

    def __del__(self):
        if hasattr(self, 'index_file'):
            self.index_file.close()

    def _get_postings(self, term):
        if term not in self.term_offsets:
            return None
        
        offset = self.term_offsets[term]
        self.index_file.seek(offset)
        line = self.index_file.readline()
        
        if not line: return None
        data = json.loads(line)
        return data["postings"]

    def _check_phrase_match(self, doc_postings):

        if not doc_postings: return set()
        
        common_docs = set(doc_postings[0].keys())
        for p in doc_postings[1:]:
            common_docs &= set(p.keys())

        matched_docs = set()

        for doc_id in common_docs:
            pos_lists = [doc_postings[i][doc_id] for i in range(len(doc_postings))]
            
            for p in pos_lists[0]:
                if self._has_sequence(p, pos_lists[1:]):
                    matched_docs.add(doc_id)
                    break
        
        return matched_docs

    def _has_sequence(self, current_pos, remaining_pos_lists):
        if not remaining_pos_lists:
            return True
        
        next_positions = remaining_pos_lists[0]
        if (current_pos + 1) in next_positions:
            return self._has_sequence(current_pos + 1, remaining_pos_lists[1:])
        return False
    
    def search(self, query: str, k: int = 5):
        if not query: return []
        
        is_phrase = False
        stripped_query = query.strip()
        if stripped_query.startswith('"') and stripped_query.endswith('"'):
            is_phrase = True
            stripped_query = stripped_query[1:-1] 

        tokens_with_pos, _ = self.tokenizer.tokenize(stripped_query)
        query_terms = [] 
        seen = set()
        for t in tokens_with_pos:
            if is_phrase:
                query_terms.append(t[0])
            else:
                if t[0] not in seen:
                    query_terms.append(t[0])
                    seen.add(t[0])

        if not query_terms: return []

        term_data = [] 
        phrase_postings_list = [] 

        for term in query_terms:
            postings = self._get_postings(term)
            if postings:
                term_data.append((term, postings))
                phrase_postings_list.append(postings)
            else:
                if is_phrase: return []

        if not term_data: return []

        if is_phrase:
            valid_docs = self._check_phrase_match(phrase_postings_list)
            if not valid_docs: return []
            
            filtered_term_data = []
            for term, postings in term_data:
                filtered = {d: pos for d, pos in postings.items() if d in valid_docs}
                filtered_term_data.append((term, filtered))
            term_data = filtered_term_data

        scores = self.ranker.compute_scores(term_data, query_terms=query_terms)

        top_k = sorted(scores, key=lambda x: x["score"], reverse=True)[:k]
        return top_k