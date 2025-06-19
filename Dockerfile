FROM python:3.10-slim

# 安装依赖和 Chrome + ChromeDriver
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg ca-certificates fonts-liberation libappindicator3-1 \
    libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 \
    libnspr4 libnss3 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 \
    xdg-utils chromium chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置 ChromeDriver 环境变量
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝代码
COPY . .

# 设置入口
CMD ["python", "keep_alive.py"]
