from indexer import data_loader, parser, tokenizer, indexer, merger, pagerank
import os
import json

CORPUS_PATH = "DEV"
PARTIAL_DIR = "partial_indexes"
FINAL_INDEX_FILE = "final_index.txt" 

def compute_m1_stats(final_index_path: str, total_docs: int):
    if not os.path.exists(final_index_path):
        print(f"[WARN] Index file {final_index_path} not found.")
        return

    size_kb = os.path.getsize(final_index_path) / 1024

    unique_tokens = 0
    with open(final_index_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip(): 
                unique_tokens += 1

    print(f"Total indexed documents: {total_docs}")
    print(f"Unique tokens: {unique_tokens}")
    print(f"Final index size: {size_kb:.2f} KB")


def main():
    print("Initializing...")
    dl = data_loader.DataLoader(CORPUS_PATH)
    parse = parser.Parser()
    tok = tokenizer.Tokenizer()
    idx = indexer.Indexer()
    
    os.makedirs(PARTIAL_DIR, exist_ok=True)
    idx.partial_index_dir = PARTIAL_DIR 

    print("Loading documents...")
    for doc_id, url, content, encoding in dl.iter_documents():
        
        if doc_id % 500 == 0:
            print(f"Processed {doc_id} documents...")

        text, links = parse.parse(content, url)
        
        token_pos_pairs, fingerprint = tok.tokenize(text)
        
        if idx.is_duplicate(fingerprint):
            continue

        idx.add_document(doc_id, url, token_pos_pairs, links)
        
    print("Documents loaded.")

    idx.finalize()
    
    merger.merge_partials(idx.partial_index_dir, output_path=FINAL_INDEX_FILE)
    
    pagerank.compute_pagerank()

    print("Processing Anchor Text Index...")
    if os.path.exists("anchor_text.json") and os.path.exists("doc_map.json"):
        with open("anchor_text.json", "r", encoding="utf-8") as f:
            anchor_data = json.load(f)
        
        url_to_id = {u: str(k) for k, u in idx.doc_map.items()}
        
        final_anchor_index = {}
        for url, terms_list in anchor_data.items():
            if url in url_to_id:
                doc_id = url_to_id[url]
                final_anchor_index[doc_id] = " ".join(terms_list)
        
        with open("anchor_index_ids.json", "w", encoding="utf-8") as f:
            json.dump(final_anchor_index, f)

    compute_m1_stats(FINAL_INDEX_FILE, idx.doc_count)
    
    print("Done!")

if __name__ == "__main__":
    main()