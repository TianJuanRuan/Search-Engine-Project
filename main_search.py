from search.search_engine import SearchEngine
import time
from flask import Flask, render_template, request

app = Flask(__name__)

TEST_QUERIES = [
    "cristina lopes",
    "machine learning",
    "ACM",
    "master of software engineering"
]

def search(query):
    engine = SearchEngine(
        index_path="final_index.txt",     
        offset_path="index_offsets.json",
        doc_map_path="doc_map.json"
    )
    results = engine.search(query, k=5)
    return results

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/result", methods=["POST"])
def result():
    query = request.form.get("query")
    
    #Run Search
    start_time = time.time()
    results = search(query)
    total_time = (time.time() - start_time) * 1000

    return render_template("result.html", user_text=query, search_time=total_time, results=results)

if __name__ == "__main__":
    app.run()

