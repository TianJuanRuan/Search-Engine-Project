import os
import json
from collections import defaultdict
import glob


FINAL_PATH = "final_index.json"

def load_partial(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)                     # {term: {doc_id: tf}}
    return data

def merge_partials(partial_dir: str, output_path: str = FINAL_PATH):
    partial_files = glob.glob(os.path.join(partial_dir, "partial_*.json"))
    merged_index = defaultdict(lambda: defaultdict(int))

    for partial_file in partial_files:
        partial_data = load_partial(partial_file)
        for term, postings in partial_data.items():
            for doc_id, tf in postings.items(): #doc id, term frequency
                merged_index[term][doc_id] += tf

    merged_index = {term: dict(postings) for term, postings in merged_index.items()}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged_index, f)

