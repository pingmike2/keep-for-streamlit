FROM python:3.10-slim

# 安装 Chrome 和 chromedriver
RUN apt-get update && apt-get install -y \
    wget unzip gnupg curl chromium chromium-driver \
    && apt-get clean

# 设置缓存目录权限
ENV SELENIUM_MANAGER_CACHE_DIR=/tmp/.selenium
RUN mkdir -p /tmp/.selenium

# 复制代码
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .

# 设置执行命令
ENTRYPOINT ["python", "main.py"]