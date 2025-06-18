import os
import time
import threading
import requests
from datetime import datetime
from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ===== 环境变量 =====
KEEP_URL = os.getenv("KEEP_URL", "")
ARGO_URL = os.getenv("ARGO_URL", "")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))


# ===== Flask Web 服务器，用于 Hugging Face 保活 =====
app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, world."

def run_flask():
    app.run(host="0.0.0.0", port=7860)


# ===== 工具函数 =====
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


def is_target_alive():
    try:
        res = requests.get(KEEP_URL, timeout=10)
        print(f"[{datetime.now()}] {KEEP_URL} 状态码: {res.status_code}")
        return res.status_code != 404
    except Exception as e:
        print(f"[检测失败] {e}")
        return False


def wake_up():
    print(f"[⚠️] 检测到离线，尝试唤醒：{ARGO_URL}")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(ARGO_URL)
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
                time.sleep(2)  # 每次失败等待 2 秒后再试

        if not success:
            print("[❌] 连续3次点击失败，发送TG通知")
            send_telegram_message(f"⚠️ 未找到唤醒按钮：<b>{KEEP_URL}</b>，可能页面结构变化")
        driver.quit()
    except Exception as e:
        print(f"[Selenium Error] {e}")
        send_telegram_message(f"❌ Selenium 异常：{e}")


# ===== 主循环任务 =====
def monitor_loop():
    while True:
        if not is_target_alive():
            wake_up()
        else:
            print(f"[✅] {KEEP_URL} 在线")
        time.sleep(CHECK_INTERVAL)


# ===== 程序入口 =====
if __name__ == "__main__":
    # 启动 Flask（用于 Hugging Face 保活）
    threading.Thread(target=run_flask, daemon=True).start()

    # 启动定时检查
    monitor_loop()