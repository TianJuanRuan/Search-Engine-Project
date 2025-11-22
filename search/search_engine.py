import os
import json
from collections import defaultdict

from indexer.tokenizer import Tokenizer
from .ranker import Ranker


class SearchEngine:
    def __init__(self,
                 index_path: str = "final_index.json",
                 doc_map_path: str = "doc_map.json"):

        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index file not found: {index_path}")
        if not os.path.exists(doc_map_path):
            raise FileNotFoundError(f"Doc map file not found: {doc_map_path}")

        # Inverted index: {term: {doc_id_str: tf}}
        with open(index_path, "r", encoding="utf-8") as f:
            self.index = json.load(f)

        # Doc map: {doc_id_str: url}
        with open(doc_map_path, "r", encoding="utf-8") as f:
            self.doc_map = json.load(f)

        self.N = len(self.doc_map)
        self.tokenizer = Tokenizer()
        self.ranker = Ranker(total_docs=self.N, doc_map=self.doc_map)

    def _tokenize_query(self, query: str):
        """
        Use the same tokenizer as indexing, returning stemmed token strings.
        """
        if not query:
            return []

        pairs = self.tokenizer.tokenize_normal_and_important(query, "")
        tokens = [t for (t, _w) in pairs]

        # Deduplicate to avoid double-counting the same term
        return list(dict.fromkeys(tokens))

    def search(self, query: str, k: int = 10):
        """
        Boolean AND retrieval with tf-idf ranking.

        Only documents that contain ALL query terms are considered.
        Those docs are ranked by tf-idf and the top-k are returned.
        """
        terms = self._tokenize_query(query)
        if not terms:
            return []

        # Gather postings for each term; enforce AND semantics.
        term_postings = []  # list of (term, {doc_id_str: tf})
        for t in terms:
            postings = self.index.get(t)
            if not postings:
                # If any term is missing from the index, no doc contains all terms.
                return []
            term_postings.append((t, postings))

        # Compute intersection of doc IDs across all terms (AND)
        first_term, first_postings = term_postings[0]
        common_docs = set(first_postings.keys())
        for _, postings in term_postings[1:]:
            common_docs &= set(postings.keys())

        if not common_docs:
            return []

        # Build per-doc total TF (sum of tfs over all query terms),
        # and DF map per term for tf-idf.
        doc_tf_total = defaultdict(int)
        df_map = {}

        for t, postings in term_postings:
            df_map[t] = len(postings)  # df for this term in the collection

            for doc_id_str in common_docs:
                tf = postings.get(doc_id_str, 0)
                if tf > 0:
                    doc_id = int(doc_id_str)
                    doc_tf_total[doc_id] += tf

        # Convert to postings list compatible with Ranker.compute_scores
        postings_list = [
            {"doc_id": doc_id, "tf": tf_total}
            for doc_id, tf_total in doc_tf_total.items()
        ]

        scores = self.ranker.compute_scores(list(df_map.keys()), postings_list, df_map)

        # Sort by score descending and take top-k
        scores_sorted = sorted(scores, key=lambda x: x["score"], reverse=True)[:k]
        return scores_sorted
