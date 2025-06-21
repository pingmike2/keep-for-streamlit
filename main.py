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
from uuid import uuid4
import glob
import shutil

# ==== 清理旧的临时目录 ====
for path in glob.glob("/tmp/chrome-data-*"):
    try:
        shutil.rmtree(path)
    except:
        pass

# ==== 避免权限错误 + 设置时区 ====
os.environ["SELENIUM_MANAGER_CACHE_DIR"] = "/tmp/.selenium"
os.environ["TZ"] = "Asia/Shanghai"
time.tzset()

# ==== 环境变量 ====
KEEP_URL = os.getenv("KEEP_URL", "")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "600"))  # 改成每 10 分钟检查一次

# ==== Flask Web 保活 ====
app = Flask(__name__)

@app.route("/")
def index():
    return "App is running."

def run_flask():
    app.run(host="0.0.0.0", port=7860)

# ==== 发送 Telegram 消息 ====
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

# ==== 唤醒逻辑 ====
def wake_up_if_needed():
    print(f"[{datetime.now()}] 🔍 正在检测 {KEEP_URL} 状态...")

    # 创建临时配置目录
    user_data_dir = f"/tmp/chrome-data-{uuid4()}"
    os.makedirs(user_data_dir, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

    try:
        service = Service(executable_path=os.getenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver"))
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(KEEP_URL)

        # 切入 iframe（Hugging Face 页面可能在 iframe 中）
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            driver.switch_to.frame(iframes[0])
            print("✅ 已切入 iframe")

        # 检测按钮
        wake_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'get this app back up')]")
        if wake_btns:
            wake_btns[0].click()
            print("✅ 已点击 get this app back up 按钮，等待 30 秒...")
            time.sleep(30)

            deploy_btns = driver.find_elements(By.XPATH, "//button[contains(text(), '启动部署')]")
            if deploy_btns:
                deploy_btns[0].click()
                print("✅ 已点击启动部署")
                send_telegram_message(f"✅ <b>{KEEP_URL}</b>\n已点击唤醒并启动部署成功")
            else:
                print("⚠️ 唤醒后未找到启动部署按钮")
        else:
            print("ℹ️ 页面正常，无需操作。")

        driver.quit()
    except Exception as e:
        print(f"[Selenium 错误] {e}")
        send_telegram_message(f"❌ <b>{KEEP_URL}</b>\nSelenium 错误：<code>{str(e)}</code>")
    finally:
        shutil.rmtree(user_data_dir, ignore_errors=True)

# ==== 定时监控线程 ====
def monitor_loop():
    print(f"⏰ 每 {CHECK_INTERVAL} 秒检测一次 Streamlit 页面状态")
    while True:
        wake_up_if_needed()
        time.sleep(CHECK_INTERVAL)

# ==== 启动应用 ====
if __name__ == "__main__":
    print("🚀 启动 Flask + 监控线程")
    threading.Thread(target=monitor_loop, daemon=True).start()
    run_flask()