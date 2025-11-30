import os
import json
from collections import defaultdict

class Indexer:
    def __init__(self, partial_index_dir="partial_indexes", flush_doc_threshold=2000):
        self.partial_index_dir = partial_index_dir
        self.flush_doc_threshold = flush_doc_threshold
        
        os.makedirs(self.partial_index_dir, exist_ok=True)

        self.index = defaultdict(dict)
        
        self.doc_map = {} 
        self.hashes = set() 
        
        self.anchor_map = defaultdict(list)

        self.partial_index_count = 0
        self.doc_count = 0
        self._docs_since_last_flush = 0
        
        self.graph_file = open("web_graph.txt", "w", encoding="utf-8")

    def is_duplicate(self, content_hash: int) -> bool:
        if content_hash in self.hashes:
            return True
        self.hashes.add(content_hash)
        return False

    def add_document(self, doc_id: int, url: str, token_pos_list, out_links):
        self.doc_map[doc_id] = url
        
        clean_links = []
        for target_url, anchor_text in out_links:
            clean_links.append(target_url)
            
            if anchor_text:
                self.anchor_map[target_url].append(anchor_text)

        valid_links = [l.strip() for l in clean_links if l.strip()]
        self.graph_file.write(f"{doc_id} " + " ".join(valid_links) + "\n")

        for token, pos in token_pos_list:
            if doc_id not in self.index[token]:
                self.index[token][doc_id] = []
            self.index[token][doc_id].append(pos)

        self.doc_count += 1
        self._docs_since_last_flush += 1

        if self._docs_since_last_flush >= self.flush_doc_threshold:
            self.flush_partial_index()

    def flush_partial_index(self):
        if not self.index: return

        path = os.path.join(self.partial_index_dir, f"partial_{self.partial_index_count}.json")
        
        print(f"[FLUSH] Writing partial index #{self.partial_index_count}...")
        
        with open(path, "w", encoding="utf-8") as f:
            for term in sorted(self.index.keys()):
                postings = self.index[term]
                entry = {"term": term, "postings": postings}
                f.write(json.dumps(entry) + "\n")

        self.index.clear()
        self.partial_index_count += 1
        self._docs_since_last_flush = 0

    def finalize(self):
        if self.index:
            self.flush_partial_index()
            
        self.graph_file.close() 

        with open("doc_map.json", "w", encoding="utf-8") as f:
            json.dump(self.doc_map, f)
            
        print("[Indexer] Saving Anchor Text Map...")
        with open("anchor_text.json", "w", encoding="utf-8") as f:
            json.dump(self.anchor_map, f)