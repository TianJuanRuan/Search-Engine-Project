import math

class Ranker:
    def __init__(self, total_docs, doc_map):
        self.N = total_docs
        self.doc_map = doc_map

    def tfidf(self, tf, df):
        if df == 0:
            return 0
        tf_part = 1 + math.log(tf)
        idf_part = math.log(self.N / df)
        return tf_part * idf_part

    def compute_scores(self, terms, postings, df_map):
        results = {}

        for entry in postings:
            doc_id = entry["doc_id"]
            tf = entry["tf"]

            if doc_id not in results:
                results[doc_id] = 0.0

            for t in terms:
                df = df_map[t]
                base_score = self.tfidf(tf, df)
                results[doc_id] += base_score

        output = []
        for doc_id, score in results.items():
            output.append({
                "doc_id": doc_id,
                "score": score,
                "url": self.doc_map[str(doc_id)]
            })

        return output

