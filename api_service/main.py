import os
from typing import List

from elasticsearch import Elasticsearch
from fastapi import FastAPI, Query

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200")
INDEX_NAME = "documents"

app = FastAPI(title="OCR Document Search API")
client = Elasticsearch(ELASTICSEARCH_HOST)


@app.get("/search")
def search(q: str = Query(..., min_length=1)) -> List[dict]:
    response = client.search(
        index=INDEX_NAME,
        query={"match": {"content": q}},
    )
    hits = response.get("hits", {}).get("hits", [])
    return [
        {
            "filename": hit.get("_source", {}).get("filename"),
            "score": hit.get("_score"),
        }
        for hit in hits
    ]
