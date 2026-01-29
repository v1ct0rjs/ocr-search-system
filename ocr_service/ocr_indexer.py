import os
import time
import hashlib
import numpy as np
from pdf2image import convert_from_path
from paddleocr import PaddleOCR
from elasticsearch import Elasticsearch
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DOCS_PATH = "/documents"
INDEX_NAME = "documents"

es = Elasticsearch("http://elasticsearch:9200")
ocr = PaddleOCR(lang="en", show_log=False)

processed_files = set()


def file_hash(path):
    '''Genera un hash MD5 del archivo para evitar reprocesamiento.'''
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()


def index_document(filename, text):
    '''Indexa el documento en Elasticsearch.'''
    doc = {
        "filename": filename,
        "content": text
    }
    # Usar filename como ID => upsert/overwrite (evita duplicados)
    es.index(index=INDEX_NAME, id=filename, document=doc)
    print(f"Indexado/actualizado: {filename}")


def extract_text_from_images(images):
    '''Extrae texto de una lista de imágenes usando OCR.'''
    text = ""
    for image in images:
        image_np = np.array(image)
        result = ocr.ocr(image_np, cls=True)
        if result and result[0]:
            for line in result[0]:
                text += line[1][0] + " "
    return text


def process_pdf(path):
    '''Convierte un PDF a imágenes y extrae texto usando OCR.'''
    images = convert_from_path(path)
    return extract_text_from_images(images)


def process_image(path):
    '''Extrae texto de una imagen usando OCR.'''
    text = ""
    result = ocr.ocr(path, cls=True)
    if result and result[0]:
        for line in result[0]:
            text += line[1][0] + " "
    return text


def process_file(path):
    '''Procesa un archivo (PDF o imagen) y lo indexa.'''
    if not os.path.isfile(path):
        return

    ext = path.lower().split(".")[-1]
    file_id = file_hash(path)

    if file_id in processed_files:
        return

    print(f"Procesando: {os.path.basename(path)}")

    try:
        if ext == "pdf":
            text = process_pdf(path)
        elif ext in ["jpg", "jpeg", "png"]:
            print(f"Imagen detectada: {os.path.basename(path)}")
            text = process_image(path)
        else:
            return

        index_document(os.path.basename(path), text)
        processed_files.add(file_id)

    except Exception as e:
        print(f"Error procesando {path}: {e}")


class NewFileHandler(FileSystemEventHandler):
    '''Manejador de eventos para nuevos archivos.
    Creamos una clase que hereda de FileSystemEventHandler.'''

    def on_created(self, event):
        '''Cuando se crea un nuevo archivo, procesarlo.'''
        if event.is_directory:
            return

        path = event.src_path
        ext = path.lower().split(".")[-1]

        # Solo procesar tipos soportados
        if ext not in ["pdf", "jpg", "jpeg", "png"]:
            return

        print(f"Nuevo archivo detectado: {os.path.basename(path)}")
        time.sleep(3)  # esperar a que termine de copiarse
        process_file(path)


def initial_scan():
    '''Escanea la carpeta documents al inicio para procesar archivos existentes.'''
    print("Escaneando documentos existentes...")
    for file in os.listdir(DOCS_PATH):
        process_file(os.path.join(DOCS_PATH, file))


def main():
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME)

    initial_scan()

    print("Vigilando carpeta documents para nuevos archivos...")
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, DOCS_PATH, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(10)
            # Rescan de seguridad por si watchdog falla
            initial_scan()
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()