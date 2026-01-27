FROM python:3.10-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        poppler-utils \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ocr_indexer.py /app/ocr_indexer.py

CMD ["python", "ocr_indexer.py"]

