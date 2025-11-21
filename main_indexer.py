from indexer import data_loader, parser, tokenizer, indexer, merger
import os
import json


CORPUS_PATH = "DEV"
PARTIAL_DIR = "partial_indexes"
FINAL_INDEX_FILE = "final_index.json"


def compute_m1_stats(final_index_path: str, total_docs: int):
    # Read the whole file as text
    with open(final_index_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Use low-level decoder to parse only the FIRST JSON object
    decoder = json.JSONDecoder()
    index, end_idx = decoder.raw_decode(text)

    remaining = text[end_idx:].strip()
    if remaining:
        print(f"[WARN] Extra data after first JSON object in {final_index_path}, ignoring it.")

    unique_tokens = len(index)
    size_kb = os.path.getsize(final_index_path) / 1024

    print(f"Total indexed documents: {total_docs}")
    print(f"Unique tokens:          {unique_tokens}")
    print(f"Final index size:       {size_kb:.2f} KB")



def main():
    # Load documents
    print("Loading documents...")
    data_loader_instance = data_loader.DataLoader(root_dir=CORPUS_PATH)
    print("Documents loaded.")

    parser_instance = parser.Parser(use_lxml=True)
    tokenizer_instance = tokenizer.Tokenizer()
    indexer_instance = indexer.Indexer()

    os.makedirs(PARTIAL_DIR, exist_ok=True)

    # Process each document
    for doc_id, url, content, encoding in data_loader_instance.iter_documents():
        parsed_normal, parsed_important = parser_instance.extract_text(content)
        token_weight_pairs = tokenizer_instance.tokenize_normal_and_important(parsed_normal, parsed_important)
        indexer_instance.add_document(doc_id, token_weight_pairs)

        if doc_id % 500 == 0 and doc_id > 0:
            print(f"Processed {doc_id} documents...")

    # Flush indexing data
    indexer_instance.finalize()

    #Merge partial indexes
    merger.merge_partials(partial_dir=indexer_instance.partial_index_dir)

    compute_m1_stats(FINAL_INDEX_FILE, indexer_instance.doc_count)


if __name__ == "__main__":
    main()
