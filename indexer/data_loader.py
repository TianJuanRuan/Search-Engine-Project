import os
try:
    import ujson as json
except ImportError:
    import json
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
        root = self.root_dir

        for domain_entry in os.scandir(root):
            if not domain_entry.is_dir():
                continue

            domain_path = domain_entry.path

            for file_entry in os.scandir(domain_path):
                if not file_entry.name.endswith(".json"):
                    continue
                
                file_path = file_entry.path
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