# OCR Document Search System

Sistema de indexación y búsqueda de documentos escaneados utilizando OCR, Elasticsearch y FastAPI, desplegado con Docker.

Este proyecto permite extraer texto desde PDFs e imágenes escaneadas mediante PaddleOCR y realizar búsquedas de texto completo sobre el contenido indexado.

---

## Descripción del sistema

El sistema automatiza el procesamiento de documentos escaneados:

1. Lee archivos desde la carpeta `documents/`
2. Convierte PDFs en imágenes
3. Aplica OCR con PaddleOCR
4. Extrae el texto detectado
5. Indexa el contenido en Elasticsearch
6. Permite búsquedas mediante una API REST

---

## Arquitectura

```
documents/ → OCR Service → Elasticsearch → API REST → Usuario
```

| Servicio        | Función                                                  |
|-----------------|-----------------------------------------------------------|
| OCR Service     | Procesa documentos y extrae texto con OCR                 |
| Elasticsearch   | Almacena e indexa el contenido de los documentos          |
| API Service     | Proporciona un endpoint para realizar búsquedas de texto  |

---

## Tecnologías utilizadas

- PaddleOCR (OCR basado en Deep Learning)
- Elasticsearch 8
- FastAPI
- Docker y Docker Compose
- Python 3.10

---

## Requisitos

- Docker
- Docker Compose

Compatible con:

- Linux
- macOS
- Windows (con Docker Desktop)

---

## Puesta en marcha

### 1. Iniciar los servicios base

```bash
docker compose up -d
```

Esto iniciará:

- Elasticsearch en [http://localhost:9200](http://localhost:9200)
- API de búsqueda en [http://localhost:8000](http://localhost:8000)

---

### 2. Añadir documentos

Coloca los documentos que quieras procesar dentro de la carpeta:

```
documents/
```

Formatos soportados:

- PDF
- JPG / JPEG
- PNG

---

### 3. Ejecutar el proceso de OCR e indexación

```bash
docker compose run --rm ocr_service
```

El sistema descargará los modelos de OCR la primera vez y mostrará mensajes como:

```
OCR PDF: contrato.pdf
Indexado: contrato.pdf
```

---

### 4. Realizar búsquedas

Usa el navegador o una herramienta como curl:

```
http://localhost:8000/search?q=contrato
```

Respuesta de ejemplo:

```json
{
  "results": [
    {
      "filename": "contrato.pdf",
      "score": 2.31
    }
  ]
}
```

---

## Flujo de uso habitual

Cada vez que añadas nuevos documentos a la carpeta `documents/`, ejecuta:

```bash
docker compose run --rm ocr_service
```

Esto procesará los nuevos archivos y los añadirá al índice de búsqueda.

---

## Script de arranque rápido (Linux/macOS)

Puedes usar el script `start.sh`:

```bash
./start.sh
```

Este script:

1. Inicia Elasticsearch y la API
2. Espera a que Elasticsearch esté disponible
3. Ejecuta el servicio de OCR para indexar documentos

---

## Uso en Windows

Con Docker Desktop instalado, usa PowerShell:

```powershell
docker compose up -d
docker compose run --rm ocr_service
```

Opcionalmente puedes usar el script `start.ps1` si lo has creado.

---

## Estructura del proyecto

```
ocr-search-system/
│
├── docker-compose.yml
├── start.sh
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

## Notas técnicas

- Se fija `numpy < 2.0` para mantener compatibilidad con OpenCV y PaddleOCR.
- Las imágenes generadas desde PDFs (PIL) se convierten a arrays NumPy antes de enviarlas al motor OCR.
- Elasticsearch se ejecuta en modo single-node y sin seguridad, pensado para entorno de laboratorio o desarrollo.
- Los modelos de PaddleOCR se descargan automáticamente la primera vez que se ejecuta el OCR.

---

## Consideraciones de seguridad

Este sistema está diseñado con fines educativos y de laboratorio. No se recomienda exponer Elasticsearch ni la API directamente a Internet sin:

- Autenticación
- HTTPS
- Configuración de seguridad en Elasticsearch

---

## Autoría

Proyecto orientado a la integración de administración de sistemas con procesamiento inteligente de documentos mediante OCR.
