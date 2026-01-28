from elasticsearch import Elasticsearch
from fastapi import FastAPI, Query
from typing import List
import os
from fastapi.middleware.cors import CORSMiddleware

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200") # Asegúrate de que coincide con el host del contenedor de Elasticsearch
INDEX_NAME = "documents" # Debe coincidir con el índice usado en ocr_indexer.py

app = FastAPI(title="OCR Document Search API") # Título de la API

# Configuración de CORS para permitir solicitudes desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
client = Elasticsearch(ELASTICSEARCH_HOST)

# Endpoint de búsqueda
@app.get("/search")
def search(q: str = Query(..., min_length=1)) -> List[dict]:
    response = client.search(
        index=INDEX_NAME,
        query={"match": {"content": q}},
        _source=["filename"],
        size=20,
    )

    hits = response.get("hits", {}).get("hits", [])

    return [
        {
            "filename": hit.get("_source", {}).get("filename"),
            "score": hit.get("_score"),
        }
        for hit in hits
    ]
