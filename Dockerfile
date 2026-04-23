# Sử dụng bản nhẹ để giảm dung lượng image
FROM python:3.11-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Giảm log buffer để xem log realtime trong Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Cài đặt các thư viện hệ thống cần thiết cho psycopg2 và xử lý PDF
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy và cài đặt thư viện Python trước để tận dụng cache
COPY ./app/requirements.txt /tmp/requirements.txt
RUN python -c "from pathlib import Path; p=Path('/tmp/requirements.txt'); b=p.read_bytes();\
txt=b.decode('utf-8') if not b.startswith((b'\xff\xfe', b'\xfe\xff')) else b.decode('utf-16');\
p.write_text(txt, encoding='utf-8')"
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt

# Copy toàn bộ code vào container
COPY ./app /app

# Biến môi trường để Python nhận diện thư mục app
ENV PYTHONPATH=/app

# Chạy ứng dụng bằng Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]