from search.search_engine import SearchEngine
import time

TEST_QUERIES = [
    "cristina lopes",
    "machine learning",
    "ACM",
    "master of software engineering"
]

def main():
    engine = SearchEngine(
        index_path="final_index.txt",     
        offset_path="index_offsets.json",
        doc_map_path="doc_map.json"
    )

    query = ""
    while query != "q!":
        query = input("Enter your query (or 'q!' to quit): ")
        start_time = time.time()
        print(f"Query: {query}")
        results = engine.search(query, k=5)

        if not results:
            print("  No results found.\n")
            continue

        for rank, r in enumerate(results, start=1):
            print(f"  {rank}. doc_id={r['doc_id']} | score={r['score']:.4f}")
            print(f"     URL: {r['url']}")
        print(f"Search completed in {(time.time() - start_time) * 1000:.4f} milliseconds.\n")
    
    print("Goodbye!")
if __name__ == "__main__":
    main()

