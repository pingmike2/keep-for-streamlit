FROM python:3.10-slim

# 安装依赖
RUN apt update && apt install -y \
    wget curl unzip chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# 环境变量配置
ENV TZ=Asia/Shanghai
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# 安装 Python 库
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝代码
COPY main.py /app/main.py

# 启动入口
CMD ["python", "main.py"]