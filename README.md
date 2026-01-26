# OCR Document Search System

## Project Description
The OCR Document Search System indexes scanned PDFs and images using OCR, stores the extracted text in Elasticsearch, and provides a REST API for full-text search across the indexed documents.

## Architecture
- **Elasticsearch**: Stores indexed document text and enables full-text search.
- **OCR Service (Python)**: Scans files in `/documents`, converts PDFs to images, extracts text using PaddleOCR, and indexes the results into Elasticsearch.
- **API Service (FastAPI)**: Exposes a `/search?q=` endpoint that queries Elasticsearch and returns matching filenames and scores.

## How to Run
```bash
docker compose up --build
```

## How to Add Documents
Place PDFs or image files (`.pdf`, `.png`, `.jpg`, `.jpeg`) into the `documents/` folder before starting the services. The OCR service will scan and index all supported files.

## Example Search Request
```bash
curl "http://localhost:8000/search?q=invoice"
```
