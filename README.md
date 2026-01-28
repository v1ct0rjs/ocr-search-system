# OCR Document Search System

A document indexing and search system for scanned documents using OCR, Elasticsearch and FastAPI, deployed with Docker.

This project allows extracting text from PDFs and scanned images using PaddleOCR and performing full-text searches on the indexed content.

---

## System Description

The system automates the processing of scanned documents:

1. Reads files from the `documents/` folder
2. Converts PDFs to images
3. Applies OCR with PaddleOCR
4. Extracts detected text
5. Indexes content in Elasticsearch
6. Enables searching via REST API and Web Interface

The OCR service continuously monitors the `documents/` folder using watchdog and automatically processes new files.

---

## Architecture

```
documents/ → OCR Service → Elasticsearch → API REST → Web Interface
                                        ↘ Elasticvue (Admin)
```

| Service         | Port  | Function                                               |
|-----------------|-------|--------------------------------------------------------|
| OCR Service     | -     | Processes documents and extracts text with OCR         |
| Elasticsearch   | 9200  | Stores and indexes document content                    |
| API Service     | 8000  | Provides an endpoint for full-text searches            |
| Web Interface   | 8080  | User-friendly search interface                         |
| Elasticvue      | 8081  | Elasticsearch admin interface                          |

---

## Technologies Used

- PaddleOCR (Deep Learning-based OCR)
- Elasticsearch 8.11.3
- FastAPI
- Nginx (Web server)
- Elasticvue (Elasticsearch GUI)
- Watchdog (File system monitoring)
- Docker and Docker Compose
- Python 3.10

---

## Requirements

- Docker
- Docker Compose

Compatible with:

- Linux
- macOS
- Windows (with Docker Desktop)

---

## Getting Started

### 1. Start all services

```bash
docker compose up -d
```

This will start:

- Elasticsearch at [http://localhost:9200](http://localhost:9200)
- Search API at [http://localhost:8000](http://localhost:8000)
- Web Interface at [http://localhost:8080](http://localhost:8080)
- Elasticvue at [http://localhost:8081](http://localhost:8081)
- OCR Service (monitors documents folder continuously)

---

### 2. Add documents

Place the documents you want to process in the folder:

```
documents/
```

Supported formats:

- PDF
- JPG / JPEG
- PNG

The OCR service will automatically detect and process new files.

---

### 3. Perform searches

#### Via Web Interface

Open [http://localhost:8080](http://localhost:8080) in your browser and use the search form.

#### Via API

Use the browser or a tool like curl:

```
http://localhost:8000/search?q=contract
```

Example response:

```json
[
  {
    "filename": "contract.pdf",
    "score": 2.31
  }
]
```

---

## Elasticsearch Endpoints - Query Indexes and Documents

Once OCR has processed the documents, you can verify which files are indexed and view the extracted content through Elasticsearch.

### 1. View all available indexes

```bash
curl http://localhost:9200/_cat/indices
```

or in the browser:

```
http://localhost:9200/_cat/indices
```

---

### 2. View all indexed documents

```bash
curl http://localhost:9200/documents/_search?size=1000
```

Example response:

```json
{
  "hits": {
    "total": {
      "value": 3,
      "relation": "eq"
    },
    "hits": [
      {
        "_index": "documents",
        "_id": "contract.pdf",
        "_score": 1,
        "_source": {
          "filename": "contract.pdf",
          "content": "CONTRACT OF SERVICES... [full text extracted by OCR]"
        }
      }
    ]
  }
}
```

---

### 3. View extracted content of a specific file

```bash
curl http://localhost:9200/documents/_search?pretty

```

or a file by its filename:

```bash
curl http://localhost:9200/documents/_search?q=filename:contract.pdf
```

---

### 4. Search for specific content in documents

```bash
curl "http://localhost:9200/documents/_search?q=content:signature"
```

This will search for the word "signature" in the extracted content of all documents.

---

### 5. View the index structure (mapping)

```bash
curl http://localhost:9200/documents/_mapping
```

Example response:

```json
{
  "documents": {
    "mappings": {
      "properties": {
        "filename": {
          "type": "text"
        },
        "content": {
          "type": "text"
        }
      }
    }
  }
}
```

---

### 6. Count indexed documents

```bash
curl http://localhost:9200/documents/_count
```

---

### 7. View index statistics

```bash
curl http://localhost:9200/documents/_stats
```

---

## Elasticvue - Visual Interface

For a more user-friendly graphical interface to manage Elasticsearch, access Elasticvue at:

```
http://localhost:8081
```

Connect to `http://elasticsearch:9200` or `http://localhost:9200` to visualize, filter and search documents graphically.

---

## Management Script (manage.sh)

To simplify system administration, the `manage.sh` script is included, which automates the most common tasks.

### Installation

First, make the script executable:

```bash
chmod +x manage.sh
```

### Basic usage

```bash
./manage.sh [command]
```

Without arguments, it displays the help menu.

---

## Available Commands

### Service management

#### `./manage.sh up`
**Start the entire system**

Runs `docker compose up -d` and starts all services.

```bash
./manage.sh up
```

---

#### `./manage.sh down`
**Stop all services**

Completely stops all containers:

```bash
./manage.sh down
```

---

#### `./manage.sh restart`
**Restart all services**

Useful if something is not working correctly:

```bash
./manage.sh restart
```

---

#### `./manage.sh rebuild`
**Complete rebuild without cache**

Rebuilds all Docker images from scratch:

```bash
./manage.sh rebuild
```

Useful if:
- You change Dockerfile or requirements.txt
- You need to update dependencies
- There are conflicts with previous caches

---

#### `./manage.sh status`
**View container status**

Shows a table with the current status of all containers:

```bash
./manage.sh status
```

---

### View logs

#### `./manage.sh logs-api`
**API service logs**

Shows FastAPI logs:

```bash
./manage.sh logs-api
```

Press `Ctrl+C` to exit.

---

#### `./manage.sh logs-ocr`
**OCR service logs**

Shows document processing:

```bash
./manage.sh logs-ocr
```

Very useful for debugging OCR problems.

---

#### `./manage.sh logs-es`
**Elasticsearch logs**

Shows the status of the search engine:

```bash
./manage.sh logs-es
```

---

### Index operations

#### `./manage.sh reset-index`
**Delete and reindex all documents**

Cleans the Elasticsearch index and restarts OCR to reprocess all documents:

```bash
./manage.sh reset-index
```

Warning: This deletes all indexed data.

---

### Testing

#### `./manage.sh search`
**Test searches from terminal**

Allows performing interactive searches:

```bash
./manage.sh search
```

---

## Typical Workflow

### 1. First use - Getting started

```bash
# Make the script executable (first time)
chmod +x manage.sh

# Start everything
./manage.sh up

# Check status
./manage.sh status

# View OCR logs to monitor processing
./manage.sh logs-ocr
```

### 2. Add new documents

```bash
# Copy documents to documents/ folder
# The OCR service will automatically detect and process them

# Monitor OCR processing
./manage.sh logs-ocr

# Perform searches via web or terminal
./manage.sh search
```

### 3. Debugging

```bash
# Check status
./manage.sh status

# View logs to detect problems
./manage.sh logs-api    # search problems
./manage.sh logs-ocr    # OCR problems
./manage.sh logs-es     # Elasticsearch problems

# If something breaks, restart
./manage.sh restart
```

### 4. Clean up and start over

```bash
# Reset everything
./manage.sh reset-index

# Or stop completely
./manage.sh down
```

---

## Usage on Windows

With Docker Desktop installed, use PowerShell:

```powershell
docker compose up -d
```

Documents placed in the `documents/` folder will be automatically processed.

---

## Project Structure

```
ocr-search-system/
│
├── docker-compose.yml
├── manage.sh
├── documents/
│   └── README.txt
│
├── ocr_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── ocr_indexer.py
│
├── api_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
│
├── web/
│   ├── index.html
│   └── styles.css
│
└── README.md
```

---

## Technical Notes

- `numpy < 2.0` is pinned to maintain compatibility with OpenCV and PaddleOCR.
- Images generated from PDFs (PIL) are converted to NumPy arrays before sending them to the OCR engine.
- Elasticsearch runs in single-node mode without security, designed for lab or development environment.
- PaddleOCR models are automatically downloaded the first time OCR is executed.
- The OCR service uses watchdog to monitor the documents folder and automatically processes new files.
- Documents are indexed using their filename as the ID, preventing duplicates on reprocessing.

---

## Security Considerations

This system is designed for educational and laboratory purposes. It is not recommended to expose Elasticsearch or the API directly to the Internet without:

- Authentication
- HTTPS
- Elasticsearch security configuration

---

## License

GNU General Public License v3.0.
