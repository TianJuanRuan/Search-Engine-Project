import os
try:
    import ujson as json
except ImportError:
    import json
from collections import defaultdict
import glob


def load_partial(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)   # {term: {doc_id: tf}}


def merge_partials(partial_dir, output_path="final_index.json"):

    partial_files = sorted(glob.glob(os.path.join(partial_dir, "partial_*.json")))
    merged = defaultdict(lambda: defaultdict(int))

    for p in partial_files:
        data = load_partial(p)
        for term, postings in data.items():
            for doc, tf in postings.items():
                merged[term][doc] += tf   

    merged = {t: dict(p) for t, p in merged.items()}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged, f)

    print(f"[MERGE] Final index written to {output_path}")
