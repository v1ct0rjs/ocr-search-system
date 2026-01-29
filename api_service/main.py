from elasticsearch import Elasticsearch, NotFoundError
from fastapi import FastAPI, Query, HTTPException
from typing import List
import os
from fastapi.middleware.cors import CORSMiddleware

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200")
INDEX_NAME = "documents"

app = FastAPI(title="OCR Document Search API")

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


# Endpoint para obtener el contenido de un documento
@app.get("/document/{filename}")
def get_document(filename: str):
    """Obtiene el contenido completo de un documento por su nombre."""
    try:
        response = client.get(index=INDEX_NAME, id=filename)
        source = response.get("_source", {})
        return {
            "filename": source.get("filename"),
            "content": source.get("content", ""),
        }
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"Documento '{filename}' no encontrado")


# Endpoint para listar todos los documentos
@app.get("/documents")
def list_documents() -> List[dict]:
    """Lista todos los documentos indexados."""
    response = client.search(
        index=INDEX_NAME,
        query={"match_all": {}},
        _source=["filename"],
        size=100,
    )

    hits = response.get("hits", {}).get("hits", [])

    return [
        {"filename": hit.get("_source", {}).get("filename")}
        for hit in hits
    ]