FROM python:3.10-slim

# 安装依赖
RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libnss3 \
    libxss1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    wget \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 复制文件
WORKDIR /app
COPY . .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置 Chrome 路径
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV KEEP_URL=https://onlyno999.streamlit.app/

# 运行应用
CMD ["python", "main.py"]