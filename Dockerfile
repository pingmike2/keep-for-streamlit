FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg ca-certificates fonts-liberation libappindicator3-1 \
    libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 \
    libnspr4 libnss3 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 \
    xdg-utils chromium chromium-driver \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ 强制指定入口点，避免 HF 默认运行 app.py
ENTRYPOINT ["bash", "-c", "python monitor.py & gunicorn --bind 0.0.0.0:7860 app:app"]