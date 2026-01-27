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
6. Enables searching via REST API

---

## Architecture

```
documents/ → OCR Service → Elasticsearch → API REST → User
```

| Service         | Function                                               |
|-----------------|--------------------------------------------------------|
| OCR Service     | Processes documents and extracts text with OCR        |
| Elasticsearch   | Stores and indexes document content                    |
| API Service     | Provides an endpoint for full-text searches            |

---

## Technologies Used

- PaddleOCR (Deep Learning-based OCR)
- Elasticsearch 8
- FastAPI
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

### 1. Start the base services

```bash
docker compose up -d
```

This will start:

- Elasticsearch at [http://localhost:9200](http://localhost:9200)
- Search API at [http://localhost:8000](http://localhost:8000)

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

---

### 3. Run the OCR and indexing process

```bash
docker compose run --rm ocr_service
```

The system will download OCR models the first time and show messages like:

```
OCR PDF: contract.pdf
Indexed: contract.pdf
```

---

### 4. Perform searches

Use the browser or a tool like curl:

```
http://localhost:8000/search?q=contract
```

Example response:

```json
{
  "results": [
    {
      "filename": "contract.pdf",
      "score": 2.31
    }
  ]
}
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

You will see a result like:

```
health status index                uuid                   pri rep docs.count docs.deleted store.size pri.store.size
yellow open   documents           abc123def456ghi789jkl   1   1        150           0      5.2mb          5.2mb
```

---

### 2. View all indexed documents (with metadata)

```bash
curl http://localhost:9200/documents/_search?size=1000
```

or in the browser:

```
http://localhost:9200/documents/_search?size=1000
```

Example response:

```json
{
  "took": 5,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 3,
      "relation": "eq"
    },
    "max_score": 1,
    "hits": [
      {
        "_index": "documents",
        "_type": "_doc",
        "_id": "1",
        "_score": 1,
        "_source": {
          "filename": "contract.pdf",
          "content": "CONTRACT OF SERVICES... [full text extracted by OCR]",
          "indexed_at": "2024-01-15T10:30:00",
          "pages": 5
        }
      },
      {
        "_index": "documents",
        "_type": "_doc",
        "_id": "2",
        "_score": 1,
        "_source": {
          "filename": "invoice_2024.jpg",
          "content": "INVOICE NUMBER 001... [full text extracted by OCR]",
          "indexed_at": "2024-01-15T10:31:00",
          "pages": 1
        }
      }
    ]
  }
}
```

---

### 3. View extracted content of a specific file

```bash
curl http://localhost:9200/documents/_search?q=filename:contract.pdf
```

or more detailed:

```bash
curl -X POST http://localhost:9200/documents/_search -H "Content-Type: application/json" -d '{
  "query": {
    "match": {
      "filename": "contract.pdf"
    }
  }
}'
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
        },
        "indexed_at": {
          "type": "date"
        },
        "pages": {
          "type": "integer"
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

Example response:

```json
{
  "count": 150,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  }
}
```

---

### 7. View index statistics

```bash
curl http://localhost:9200/documents/_stats
```

---

## Recommended tools for viewing content

### With Curl (command line)

```bash
# View all documents in pretty format
curl http://localhost:9200/documents/_search?size=1000 | jq .

# Search for a specific document
curl "http://localhost:9200/documents/_search?q=filename:contract.pdf" | jq .

# View only extracted content
curl http://localhost:9200/documents/_search?size=1000 | jq '.hits.hits[].\_source | {filename, content}'
```

### With Kibana (visual interface)

If you want a more user-friendly graphical interface, add Kibana to your `docker-compose.yml`:

```yaml
kibana:
  image: docker.elastic.co/kibana/kibana:8.0.0
  ports:
    - "5601:5601"
  environment:
    ELASTICSEARCH_HOSTS: http://elasticsearch:9200
  depends_on:
    - elasticsearch
```

Then access:

```
http://localhost:5601
```

From Kibana you can visualize, filter and search documents graphically.

---

## Management Script (manage.sh)

To simplify system administration, the `manage.sh` script is included, which automates the most common tasks.

### What is manage.sh?

It is a bash script that provides a command-line interface to manage the entire OCR system lifecycle:

- Start and stop services
- View logs
- Reset indexes
- Perform search tests

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

Runs `docker compose up -d` and starts:
- Elasticsearch
- API Service
- OCR Service (in background)

```bash
./manage.sh up
```

Result:
```
==============================
  OCR SEARCH SYSTEM
==============================
Starting services...
System started
```

---

#### `./manage.sh down`
**Stop all services**

Completely stops all containers:

```bash
./manage.sh down
```

Result:
```
==============================
  OCR SEARCH SYSTEM
==============================
Stopping services...
System stopped
```

---

#### `./manage.sh restart`
**Restart all services**

Useful if something is not working correctly:

```bash
./manage.sh restart
```

Stops and restarts all containers without losing data.

---

#### `./manage.sh rebuild`
**Complete rebuild without cache**

Rebuilds all Docker images from scratch:

```bash
./manage.sh rebuild
```

Result:
```
Complete rebuild (no cache)...
Rebuild finished
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

Result:
```
CONTAINER ID   IMAGE                    STATUS              PORTS
a1b2c3d4e5f6   ocr-service              Up 2 minutes        
g7h8i9j0k1l2   api-service              Up 2 minutes        0.0.0.0:8000->8000/tcp
m3n4o5p6q7r8   elasticsearch            Up 3 minutes        0.0.0.0:9200->9200/tcp
```

---

### View logs

Logs show you what is happening in each service in real time.

#### `./manage.sh logs-api`
**API service logs**

Shows FastAPI logs:

```bash
./manage.sh logs-api
```

You will see messages like:
```
api_service_1  | INFO:     Started server process [1]
api_service_1  | INFO:     Uvicorn running on http://0.0.0.0:8000
api_service_1  | GET /search?q=contract HTTP/1.1
```

Press `Ctrl+C` to exit.

---

#### `./manage.sh logs-ocr`
**OCR service logs**

Shows document processing:

```bash
./manage.sh logs-ocr
```

You will see messages like:
```
ocr_service_1  | OCR PDF: contract.pdf
ocr_service_1  | Text extracted: 12000 characters
ocr_service_1  | Indexed: contract.pdf (5 pages)
```

Very useful for debugging OCR problems.

---

#### `./manage.sh logs-es`
**Elasticsearch logs**

Shows the status of the search engine:

```bash
./manage.sh logs-es
```

You will see messages like:
```
elasticsearch_1 | [2024-01-15T10:30:00,123][INFO ][o.e.n.Node] started
elasticsearch_1 | [2024-01-15T10:30:01,456][INFO ][o.e.c.m.MetadataCreateIndexService] created index
```

---

### Index operations

#### `./manage.sh reset-index`
**Delete and reindex all documents**

Cleans the Elasticsearch index and reprocesses all documents:

```bash
./manage.sh reset-index
```

Result:
```
==============================
  OCR SEARCH SYSTEM
==============================
Deleting Elasticsearch index...
Restarting OCR to reindex everything...
Reindexing in progress (check logs_ocr)
```

Warning: This deletes all indexed data. Use it only if you need to clean everything.

Use cases:
- You change the index structure
- You need to reprocess documents
- You want to start from scratch

---

### Testing

#### `./manage.sh search`
**Test searches from terminal**

Allows performing interactive searches without leaving the terminal:

```bash
./manage.sh search
```

Result:
```
==============================
  OCR SEARCH SYSTEM
==============================
Search test:
Text to search: contract
```

Type what you want to search for and press Enter:

```json
{
  "results": [
    {
      "filename": "contract.pdf",
      "score": 2.31
    }
  ]
}
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

# View OCR logs to know when it finishes
./manage.sh logs-ocr
```

### 2. Add new documents

```bash
# Copy documents to documents/ folder

# Process OCR (if the script is executable, otherwise use docker compose)
./manage.sh logs-ocr  # check if OCR is running

# Perform searches
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

## Technical Explanation of manage.sh

### Script Structure

- **`set -e`**: Stops the script if any command fails
- **Global variables**: `PROJECT_NAME` and `INDEX_NAME` for configuration
- **Functions**: Each command is a bash function
- **Switch case**: Routes arguments to the correct functions

### Main Functions

| Function | Task | Technology |
|----------|------|-----------|
| `header()` | Prints formatted title | `echo` bash |
| `up()` / `down()` | Container control | `docker compose` |
| `logs_*()` | Real-time monitoring | `docker compose logs -f` |
| `status()` | Inspect containers | `docker compose ps` |
| `reset_index()` | Clean Elasticsearch | `curl DELETE` |
| `search_test()` | Interactive search | `curl GET` + `read` bash |

### Error Handling

```bash
curl -s -X DELETE "http://localhost:9200/$INDEX_NAME" || true
```

The `|| true` makes the script continue even if the index doesn't exist (avoids error on first run).

---

## Normal Usage Flow

Each time you add new documents to the `documents/` folder, run:

```bash
docker compose run --rm ocr_service
```

This will process the new files and add them to the search index.

---

## Quick Start Script (Linux/macOS)

You can use the `start.sh` script:

```bash
./start.sh
```

This script:

1. Starts Elasticsearch and the API
2. Waits for Elasticsearch to be available
3. Runs the OCR service to index documents

---

## Usage on Windows

With Docker Desktop installed, use PowerShell:

```powershell
docker compose up -d
docker compose run --rm ocr_service
```

Optionally you can use the `start.ps1` script if you created it.

---

## Project Structure

```
ocr-search-system/
│
├── docker-compose.yml
├── start.sh
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
└── README.md
```

---

## Technical Notes

- `numpy < 2.0` is pinned to maintain compatibility with OpenCV and PaddleOCR.
- Images generated from PDFs (PIL) are converted to NumPy arrays before sending them to the OCR engine.
- Elasticsearch runs in single-node mode without security, designed for lab or development environment.
- PaddleOCR models are automatically downloaded the first time OCR is executed.

---

## Security Considerations

This system is designed for educational and laboratory purposes. It is not recommended to expose Elasticsearch or the API directly to the Internet without:

- Authentication
- HTTPS
- Elasticsearch security configuration

---

## Authorship

Project aimed at integrating systems administration with intelligent document processing through OCR.
