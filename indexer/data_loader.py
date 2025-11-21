import os
try:
    import ujson as json
except ImportError:
    import json
from urllib.parse import urldefrag


class DataLoader:
    doc_id = 0

    def __init__(self, root_dir):
        self.root_dir = root_dir

    def iter_documents(self):

        for domain in os.listdir(self.root_dir):
            domain_path = os.path.join(self.root_dir, domain)
            if not os.path.isdir(domain_path):
                continue

            for filename in os.listdir(domain_path):
                if not filename.endswith(".json"):
                    continue

                fpath = os.path.join(domain_path, filename)

                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    url = data.get("url", "")
                    content = data.get("content", "")
                    encoding = data.get("encoding", "")

                    url, _ = urldefrag(url)

                    yield DataLoader.doc_id, url, content, encoding
                    DataLoader.doc_id += 1

                except Exception as e:
                    print(f"[WARN] Failed to load {fpath}: {e}")
                    continue
