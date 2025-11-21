import os
try:
    import ujson as json
except ImportError:
    import json

from collections import defaultdict
from indexer.tokenizer import Tokenizer


class Indexer:

    def __init__(self, partial_index_dir="partial_indexes", flush_doc_threshold=2000):
        self.partial_index_dir = partial_index_dir
        self.flush_doc_threshold = flush_doc_threshold
        self.doc_map = {}

        os.makedirs(self.partial_index_dir, exist_ok=True)

        self.index = defaultdict(lambda: defaultdict(int))
        self.partial_index_count = 0
        self.doc_count = 0
        self._docs_since_last_flush = 0

    def add_document(self, doc_id: int, url: str, token_weight_pairs):

        self.doc_map[doc_id] = url

        tf_counter = Tokenizer.to_tf_counter(token_weight_pairs)

        for token, tf in tf_counter.items():
            self.index[token][doc_id] += tf

        self.doc_count += 1
        self._docs_since_last_flush += 1

        if self._docs_since_last_flush >= self.flush_doc_threshold:
            self.flush_partial_index()

    def flush_partial_index(self):

        if not self.index:
            return

        path = os.path.join(
            self.partial_index_dir,
            f"partial_{self.partial_index_count}.json"
        )

        serializable = {
            token: dict(postings)
            for token, postings in self.index.items()
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(serializable, f)

        print(f"[FLUSH] Wrote partial index #{self.partial_index_count} → {path}")

        self.index.clear()
        self.partial_index_count += 1
        self._docs_since_last_flush = 0

    def finalize(self):
        if self.index:
            self.flush_partial_index()

        # Save doc_map.json
        with open("doc_map.json", "w", encoding="utf-8") as f:
            json.dump(self.doc_map, f)

        print(f"Saved doc_map.json with {len(self.doc_map)} entries.")


