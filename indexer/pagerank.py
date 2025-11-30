import json
from collections import defaultdict

def compute_pagerank(graph_file="web_graph.txt", doc_map_file="doc_map.json", output_file="pagerank.json"):
    print("[PageRank] Loading Doc Map...")
    
    with open(doc_map_file, "r", encoding="utf-8") as f:
        doc_map = json.load(f) 
    
    valid_ids = set(int(k) for k in doc_map.keys())
    
    url_to_id = {u: int(i) for i, u in doc_map.items()}
    
    print("[PageRank] Building Graph...")
    adjacency = defaultdict(list)
    out_degree = defaultdict(int)
    
    with open(graph_file, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if not parts: continue
            
            try:
                src_id = int(parts[0])
            except ValueError:
                continue

            if src_id not in valid_ids:
                continue

            targets = parts[1:]
            
            for t_url in targets:
                if t_url in url_to_id:
                    target_id = url_to_id[t_url]
                    adjacency[target_id].append(src_id) 
                    out_degree[src_id] += 1

    N = len(valid_ids)
    if N == 0:
        print("[PageRank] Warning: No documents found in map.")
        return

    pr = {doc_id: 1.0/N for doc_id in valid_ids}
    
    damping = 0.85
    iterations = 20 
    
    print(f"[PageRank] Computing for {N} nodes over {iterations} iterations...")
    
    for it in range(iterations):
        new_pr = {}
        
        for i in valid_ids:
            incoming_score = 0
            
            for j in adjacency[i]:
                if out_degree[j] > 0:
                    incoming_score += pr[j] / out_degree[j]
            
            new_pr[i] = (1 - damping) / N + (damping * incoming_score)
        pr = new_pr

    print(f"[PageRank] Saving scores to {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(pr, f)