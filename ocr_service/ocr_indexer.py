import os
import time
import hashlib
import logging
import numpy as np


os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_enable_eager_mode"] = "1"

from pdf2image import convert_from_path
from paddleocr import PaddleOCR
from elasticsearch import Elasticsearch
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


logging.getLogger("ppocr").setLevel(logging.ERROR)

DOCS_PATH = "/documents"
INDEX_NAME = "documents"
SUPPORTED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

es = Elasticsearch("http://elasticsearch:9200") # Conexión a Elasticsearch

# Inicializar OCR configuración
ocr = PaddleOCR(
    lang="es",
    show_log=False,
    use_angle_cls=False,
    enable_mkldnn=False,
    use_gpu=False,
    cpu_threads=6,
    det_db_score_mode="fast",
)

# Usar diccionario para guardar hash
processed_files = {}


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
    logger.info(f"✓ Indexado: {filename} ({len(text)} caracteres)")


def extract_text_from_images(images):
    '''Extrae texto de una lista de imágenes usando OCR.'''
    text = ""
    for i, image in enumerate(images):
        try:
            image_np = np.array(image)
            result = ocr.ocr(image_np, cls=True)
            if result and result[0]:
                for line in result[0]:
                    if line and len(line) > 1:
                        text += line[1][0] + " "
        except Exception as e:
            logger.warning(f"Error en página {i + 1}: {e}")
            continue
    return text


def process_pdf(path):
    '''Convierte un PDF a imágenes y extrae texto usando OCR.'''
    # DPI reducido para mejor estabilidad y velocidad
    images = convert_from_path(path, dpi=150)
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
        logger.debug(f"No es archivo o no existe: {path}")
        return

    filename = os.path.basename(path)
    ext = filename.lower().split(".")[-1]

    if ext not in SUPPORTED_EXTENSIONS:
        logger.debug(f"Extensión no soportada: {filename}")
        return

    try:
        file_id = file_hash(path)
    except Exception as e:
        logger.error(f"Error calculando hash de {filename}: {e}")
        return

    # Verificar si ya fue procesado (mismo archivo, mismo contenido)
    if path in processed_files and processed_files[path] == file_id:
        logger.debug(f"Ya procesado (sin cambios): {filename}")
        return

    logger.info(f"➜ Procesando: {filename}")

    try:
        if ext == "pdf":
            text = process_pdf(path)
        elif ext in ["jpg", "jpeg", "png"]:
            text = process_image(path)
        else:
            return

        if text.strip():
            index_document(filename, text)
            processed_files[path] = file_id
            logger.info(f"✓ Completado: {filename}")
        else:
            logger.warning(f"⚠ Sin texto extraído: {filename}")

    except Exception as e:
        logger.error(f"✗ Error procesando {filename}: {e}")


class NewFileHandler(FileSystemEventHandler):
    '''Manejador de eventos para nuevos archivos por watchdog. Usamos esta clase para detectar cambios en la carpet,
    ya que FileSystemEventHandler puede perder eventos en sistemas de archivos y para el correcto funcionamiento.'''

    def _is_valid_file(self, path):
        '''Verifica si el archivo es de un tipo soportado.'''
        if not path or not os.path.isfile(path):
            return False
        ext = path.lower().split(".")[-1]
        return ext in SUPPORTED_EXTENSIONS

    def _handle_file(self, path, event_type):
        '''Procesa un archivo detectado.'''
        if not self._is_valid_file(path):
            return

        logger.info(f"[WATCHDOG:{event_type}] {os.path.basename(path)}")
        time.sleep(1)  # esperar a que termine de copiarse
        process_file(path)

    def on_created(self, event):
        '''Cuando se crea un nuevo archivo, procesarlo.'''
        if event.is_directory:
            return
        self._handle_file(event.src_path, "CREATED")

    def on_modified(self, event):
        '''Cuando se modifica un archivo, reprocesarlo.'''
        if event.is_directory:
            return
        self._handle_file(event.src_path, "MODIFIED")

    def on_moved(self, event):
        '''Cuando se mueve un archivo a la carpeta, procesarlo.'''
        if event.is_directory:
            return
        self._handle_file(event.dest_path, "MOVED")


def scan_directory():
    '''Escanea la carpeta documents para procesar archivos.'''
    logger.debug(f"Escaneando: {DOCS_PATH}")

    try:
        files = os.listdir(DOCS_PATH)
        logger.debug(f"Archivos encontrados: {len(files)}")

        for filename in files:
            filepath = os.path.join(DOCS_PATH, filename)
            if os.path.isfile(filepath):
                ext = filename.lower().split(".")[-1]
                if ext in SUPPORTED_EXTENSIONS:
                    logger.debug(f"  - {filename}")
                    process_file(filepath)

    except Exception as e:
        logger.error(f"Error escaneando directorio: {e}")


def main():
    logger.info("=" * 50)
    logger.info("OCR Indexer iniciando...")
    logger.info(f"Directorio de documentos: {DOCS_PATH}")
    logger.info(f"Extensiones soportadas: {SUPPORTED_EXTENSIONS}")
    logger.info("=" * 50)

    # Esperar a que Elasticsearch esté listo
    for i in range(30):
        try:
            if es.ping():
                logger.info("✓ Elasticsearch conectado")
                break
        except:
            logger.info(f"Esperando Elasticsearch... ({i + 1}/30)")
            time.sleep(2)
    else:
        logger.error("No se pudo conectar a Elasticsearch")
        return

    # Crear índice si no existe
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME)
        logger.info(f"✓ Índice '{INDEX_NAME}' creado")

    # Escaneo inicial
    scan_directory()

    # Configurar watchdog con polling más agresivo
    logger.info("Iniciando vigilancia de carpeta (PollingObserver)...")
    event_handler = NewFileHandler()
    observer = PollingObserver(timeout=1)  # Polling cada 1 segundo
    observer.schedule(event_handler, DOCS_PATH, recursive=True)
    observer.start()
    logger.info("✓ Watchdog activo")

    try:
        scan_count = 0
        while True:
            time.sleep(5)  # Rescan cada 5 segundos
            scan_count += 1
            logger.debug(f"--- Rescan #{scan_count} ---")
            scan_directory()
    except KeyboardInterrupt:
        logger.info("Deteniendo...")
        observer.stop()

    observer.join()
    logger.info("OCR Indexer finalizado")


if __name__ == "__main__":
    main()