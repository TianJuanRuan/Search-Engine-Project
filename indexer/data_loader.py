import os
import json
from urllib.parse import urldefrag

class DataLoader:
    #class variable doc_id
    doc_id = 0

    def __init__(self, root_dir):
        self.root_dir = root_dir
        #DEV folder

    def iter_documents(self):
        """
        Yields: (doc_id, url, content, encoding)
        Note: parser/tokenizer/indexer can decide what to do with url.
        """

        # Walk subdirectories (domains)
        for domain_name in os.listdir(self.root_dir):
            domain_path = os.path.join(self.root_dir, domain_name)

            if not os.path.isdir(domain_path):
                continue

            # Walk the JSON files inside each domain folder
            for filename in os.listdir(domain_path):
                if not filename.endswith(".json"):
                    continue

                file_path = os.path.join(domain_path, filename)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    # Required fields
                    url = data.get("url", "")
                    content = data.get("content", "")
                    encoding = data.get("encoding", "")

                    # Remove URL fragment (everything after #)
                    url, _ = urldefrag(url)

                    # Do not tokenize here — just yield raw text
                    yield DataLoader.doc_id, url, content, encoding
                    DataLoader.doc_id += 1

                except Exception as e:
                    print(f"[WARN] Failed to load {file_path}: {e}")
                    continue