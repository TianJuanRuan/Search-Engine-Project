import os
import json
from collections import defaultdict

class Indexer:
    def __init__(self, partial_index_dir="partial_indexes", flush_threshold=3000):
        self.index = defaultdict(lambda: defaultdict(float))
        self.doc_count = 0
        self.partial_index_count = 0
        self.flush_threshold = flush_threshold

        os.makedirs(partial_index_dir, exist_ok=True)
        self.partial_index_dir = partial_index_dir

    def add_document(self, doc_id, token_list):
        for token, weight in token_list:
            self.index[token][doc_id] += weight

        self.doc_count += 1

        if self.doc_count % self.flush_threshold == 0:
            self.flush_partial_index()

    def flush_partial_index(self):
        part_path = os.path.join(
            self.partial_index_dir,
            f"partial_{self.partial_index_count}.json"
        )

        index_out = {token: dict(postings) for token, postings in self.index.items()}

        with open(part_path, "w", encoding="utf-8") as f:
            json.dump(index_out, f)

        print(f"[FLUSH] Wrote partial index #{self.partial_index_count} → {part_path}")

        # Clear RAM
        self.index.clear()
        self.partial_index_count += 1

    def finalize(self):
        if len(self.index) > 0:
            self.flush_partial_index()
