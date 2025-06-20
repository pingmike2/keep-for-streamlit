import os
import time
import threading
import requests
from datetime import datetime
from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# 🧹 避免权限错误
os.environ["SELENIUM_MANAGER_CACHE_DIR"] = "/tmp/.selenium"
os.environ["TZ"] = "Asia/Shanghai"
time.tzset()
# ==== 环境变量 ====
KEEP_URL = os.getenv("KEEP_URL", "")
ARGO_URL = os.getenv("ARGO_URL", "")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))

# ==== Flask Web 保活 ====
app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, world."

def run_flask():
    app.run(host="0.0.0.0", port=7860)

# ==== 工具函数 ====
def send_telegram_message(text):
    if TG_BOT_TOKEN and TG_CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
                data={"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "HTML"},
                timeout=5
            )
        except Exception as e:
            print(f"[Telegram] 发送失败: {e}")

def is_argo_alive():
    try:
        res = requests.get(ARGO_URL, timeout=10)
        print(f"[{datetime.now()}] 检查 Argo 状态码: {res.status_code}")
        # 状态码 400、403、404 都视为掉线
        return res.status_code == 200
    except Exception as e:
        print(f"[检测失败] {e}")
        return False

def wake_up():
    print(f"[⚠️] 检测到离线，尝试唤醒：{KEEP_URL}")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")

    try:
        service = Service(executable_path=os.getenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver"))
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(KEEP_URL)
        time.sleep(2)

        success = False
        for attempt in range(3):
            print(f"[尝试] 第 {attempt + 1} 次点击按钮...")
            buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'get this app back up')]")
            if buttons:
                buttons[0].click()
                success = True
                print("[✔] 点击唤醒按钮成功")
                send_telegram_message(f"✅ <b>{KEEP_URL}</b> 已尝试唤醒")
                break
            else:
                time.sleep(2)

        if not success:
            print("[❌] 连续3次点击失败，发送TG通知")
            send_telegram_message(f"⚠️ 未找到唤醒按钮：<b>{KEEP_URL}</b>，页面结构可能变动")
        driver.quit()
    except Exception as e:
        print(f"[Selenium Error] {e}")
        send_telegram_message(f"❌ Selenium 异常：{e}")

# ==== 主监控逻辑 ====
def monitor_loop():
    print("===== 启动监控线程，开始检测 Argo 状态 =====")
    while True:
        if not is_argo_alive():
            wake_up()
        else:
            print(f"[✅] Argo 正常在线")
        time.sleep(CHECK_INTERVAL)

# ==== 启动 Flask + 监控 ====
if __name__ == "__main__":
    print("===== Application Startup =====")
    threading.Thread(target=monitor_loop, daemon=True).start()
    run_flask()
