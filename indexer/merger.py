import os
import json
import heapq
import glob
from contextlib import ExitStack

def merge_partials(partial_dir, output_path="final_index.txt", aux_path="index_offsets.json"):
    print("[MERGE] Starting K-Way Merge (Memory Efficient)...")
    
    partial_files = sorted(glob.glob(os.path.join(partial_dir, "partial_*.json")))
    if not partial_files:
        print("[MERGE] No partial indexes found!")
        return

    min_heap = []
    
    with ExitStack() as stack:
        files = [stack.enter_context(open(fn, "r", encoding="utf-8")) for fn in partial_files]
        
        for i, f in enumerate(files):
            while True:
                line = f.readline()
                if not line: break 
                try:
                    data = json.loads(line)
                    heapq.heappush(min_heap, (data["term"], i, data["postings"]))
                    break 
                except json.JSONDecodeError:
                    continue 

        with open(output_path, "w", encoding="utf-8") as f_out, \
             open(aux_path, "w", encoding="utf-8") as f_off:
            
            offset_map = {}

            while min_heap:
                current_term, file_idx, current_postings = heapq.heappop(min_heap)
                
                while min_heap and min_heap[0][0] == current_term:
                    _, other_file_idx, other_postings = heapq.heappop(min_heap)
                    
                    for doc_id, positions in other_postings.items():
                        if doc_id in current_postings:
                            current_postings[doc_id].extend(positions)
                        else:
                            current_postings[doc_id] = positions
                    
                    while True:
                        line = files[other_file_idx].readline()
                        if not line: break
                        try:
                            data = json.loads(line)
                            heapq.heappush(min_heap, (data["term"], other_file_idx, data["postings"]))
                            break
                        except ValueError:
                            continue

                offset_map[current_term] = f_out.tell()
                
                sorted_postings = dict(sorted(current_postings.items(), key=lambda item: int(item[0])))
                
                output_data = {"term": current_term, "postings": sorted_postings}
                f_out.write(json.dumps(output_data) + "\n")

                while True:
                    line = files[file_idx].readline()
                    if not line: break
                    try:
                        data = json.loads(line)
                        heapq.heappush(min_heap, (data["term"], file_idx, data["postings"]))
                        break
                    except ValueError:
                        continue

            json.dump(offset_map, f_off)

    print(f"[MERGE] Success. Final index at {output_path}")