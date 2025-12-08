# finish_pagerank.py
from indexer import pagerank

if __name__ == "__main__":
    print("Resuming PageRank calculation...")
    pagerank.compute_pagerank()
    print("Process Complete!")