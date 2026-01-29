from elasticsearch import Elasticsearch
from fastapi import FastAPI, Query
from typing import List
import os
from fastapi.middleware.cors import CORSMiddleware

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200") # Asegúrate de que coincide con el host del contenedor de Elasticsearch
INDEX_NAME = "documents" # Debe coincidir con el índice usado en ocr_indexer.py

app = FastAPI(title="OCR Document Search API") # Título de la API, instancia de FastAPI

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
        index=INDEX_NAME,                   #
        query={"match": {"content": q}},    # Consulta de búsqueda
        _source=["filename"],               # Campos a devolver
        size=20,                            # Número máximo de resultados a devolver
    )

    hits = response.get("hits", {}).get("hits", []) # Extrae los resultados de la respuesta

    # Formatea los resultados para devolver solo el nombre del archivo y la puntuación
    return [
        {
            "filename": hit.get("_source", {}).get("filename"),
            "score": hit.get("_score"),
        }
        for hit in hits
    ]
