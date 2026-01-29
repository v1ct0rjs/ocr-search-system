FROM python:3.10

WORKDIR /app

# Dependencias del sistema para OpenCV + Paddle + pdf2image
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Variables de entorno para estabilidad de PaddlePaddle
ENV FLAGS_use_mkldnn=0
ENV FLAGS_enable_eager_mode=1
ENV FLAGS_call_stack_level=2
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .


RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir "numpy<2.0"

# Paddle OCR compatible (versión estable)
RUN pip install --no-cache-dir paddlepaddle==2.5.2 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
RUN pip install --no-cache-dir paddleocr==2.7.0.3

# Resto de dependencias (opencv, pdf2image, elasticsearch…)
RUN pip install --no-cache-dir -r requirements.txt

COPY ocr_indexer.py .

CMD ["python", "-u", "ocr_indexer.py"]

