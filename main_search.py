from search.search_engine import SearchEngine

TEST_QUERIES = [
    "cristina lopes",
    "machine learning",
    "ACM",
    "master of software engineering"
]

def main():
    engine = SearchEngine(
        index_path="final_index.json",
        doc_map_path="doc_map.json"
    )

    for q in TEST_QUERIES:
        print(f"Query: {q}")
        results = engine.search(q, k=5)

        if not results:
            print("  No results found.\n")
            continue

        for rank, r in enumerate(results, start=1):
            print(f"  {rank}. doc_id={r['doc_id']} | score={r['score']:.4f}")
            print(f"     URL: {r['url']}")

if __name__ == "__main__":
    main()
