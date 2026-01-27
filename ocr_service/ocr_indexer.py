import os
import time
from pathlib import Path

from elasticsearch import Elasticsearch
from pdf2image import convert_from_path
from paddleocr import PaddleOCR

SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
DOCUMENTS_DIR = Path("/documents")
INDEX_NAME = "documents"
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200")


def wait_for_elasticsearch(client: Elasticsearch, retries: int = 30, delay: int = 2) -> None:
    for _ in range(retries):
        try:
            if client.ping():
                return
        except Exception:
            pass
        time.sleep(delay)
    raise RuntimeError("Elasticsearch is not available")


def ensure_index(client: Elasticsearch) -> None:
    if client.indices.exists(index=INDEX_NAME):
        return
    client.indices.create(
        index=INDEX_NAME,
        mappings={
            "properties": {
                "filename": {"type": "keyword"},
                "content": {"type": "text"},
            }
        },
    )


def extract_text_from_images(ocr: PaddleOCR, images) -> str:
    text_chunks = []
    for image in images:
        result = ocr.ocr(image, cls=True)
        for line in result:
            if len(line) >= 2:
                text_chunks.append(line[1][0])
    return "\n".join(text_chunks)


def process_pdf(ocr: PaddleOCR, file_path: Path) -> str:
    images = convert_from_path(file_path)
    return extract_text_from_images(ocr, images)


def process_image(ocr: PaddleOCR, file_path: Path) -> str:
    result = ocr.ocr(str(file_path), cls=True)
    text_chunks = []
    for line in result:
        if len(line) >= 2:
            text_chunks.append(line[1][0])
    return "\n".join(text_chunks)


def index_document(client: Elasticsearch, filename: str, content: str) -> None:
    client.index(
        index=INDEX_NAME,
        id=filename,
        document={"filename": filename, "content": content},
    )


def main() -> None:
    client = Elasticsearch(ELASTICSEARCH_HOST)
    wait_for_elasticsearch(client)
    ensure_index(client)

    ocr = PaddleOCR(use_angle_cls=True, lang="en")

    for file_path in DOCUMENTS_DIR.iterdir():
        if not file_path.is_file() or file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        if file_path.suffix.lower() == ".pdf":
            content = process_pdf(ocr, file_path)
        else:
            content = process_image(ocr, file_path)

        if content.strip():
            index_document(client, file_path.name, content)


if __name__ == "__main__":
    main()
