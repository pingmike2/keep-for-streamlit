FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg ca-certificates fonts-liberation \
    chromium chromium-driver \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium

# 复制文件并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY keep_alive.py .

CMD ["python", "keep_alive.py"]