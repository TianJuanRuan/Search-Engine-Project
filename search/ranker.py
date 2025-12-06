import math
import json
import os

class Ranker:
    def __init__(self, total_docs, doc_map_path="doc_map.json", pr_path="pagerank.json", anchor_path="anchor_index_ids.json"):
        self.N = total_docs
        
        with open(doc_map_path, "r", encoding="utf-8") as f:
            self.doc_map = json.load(f)

        self.pr_scores = {}
        if os.path.exists(pr_path):
            print("Loading PageRank scores...")
            with open(pr_path, "r", encoding="utf-8") as f:
                self.pr_scores = {int(k): v for k, v in json.load(f).items()}
        else:
            print("[WARN] pagerank.json not found. Ranking will rely only on TF-IDF.")
            
        self.anchor_index = {}
        if os.path.exists(anchor_path):
            print("Loading Anchor Index...")
            with open(anchor_path, "r", encoding="utf-8") as f:
                self.anchor_index = json.load(f)

    def compute_scores(self, term_postings, query_terms=None):

        doc_scores = {} 

        for term, postings in term_postings:
            df = len(postings)
            if df == 0: continue
            
            idf = math.log(self.N / df, 10)

            for doc_id_str, positions in postings.items():
                doc_id = int(doc_id_str)
                pos_list = positions["pos"]
                imp_flag = positions.get("imp", 0)

                tf = len(pos_list)
                w_tf = 1 + math.log(tf, 10)
                tfidf = w_tf * idf

                if imp_flag == 1:
                    tfidf *= 1.5   

                if doc_id not in doc_scores:
                    doc_scores[doc_id] = 0.0
                doc_scores[doc_id] += tfidf

        results = []
        for doc_id, tfidf_score in doc_scores.items():
            
            if query_terms and str(doc_id) in self.anchor_index:
                anchor_text = self.anchor_index[str(doc_id)]
                matches = 0
                for q_term in query_terms:
                    if q_term in anchor_text: 
                        matches += 1
                
                if matches > 0:
                    tfidf_score *= (1 + (0.1 * matches))

            pr = self.pr_scores.get(doc_id, 1e-6)
            
            final_score = tfidf_score * math.log(pr * 10000 + 10) 
            
            url = self.doc_map.get(str(doc_id), "N/A")

            results.append({
                "doc_id": doc_id,
                "score": final_score,
                "url": url
            })

        return results