FROM python:3.10-slim

# 安装依赖
RUN apt-get update && apt-get install -y \
    tzdata \
    chromium chromium-driver \
    wget curl unzip gnupg ca-certificates \
    fonts-liberation libappindicator3-1 libasound2 \
    libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 \
    libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 \
    libxcomposite1 libxdamage1 libxrandr2 xdg-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 环境变量配置
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PYTHONUNBUFFERED=1

# 设置工作目录
WORKDIR /app
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# ✅ 使用 ENTRYPOINT 启动监控 + gunicorn，避免 HF 默认运行 Python
ENTRYPOINT ["bash", "-c", "python monitor.py & gunicorn --bind 0.0.0.0:7860 app:app"]