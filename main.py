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

# 🧹 避免权限错误 + 设置时区
os.environ["SELENIUM_MANAGER_CACHE_DIR"] = "/tmp/.selenium"
os.environ["TZ"] = "Asia/Shanghai"
time.tzset()

# ==== 环境变量 ====
KEEP_URL = os.getenv("KEEP_URL", "")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "1800"))  # 默认30分钟

# ==== Flask Web 保活 ====
app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, world"

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
    print(f"[{datetime.now()}] 🔍 正在访问 {KEEP_URL} 检查状态...")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")

    try:
        service = Service(executable_path=os.getenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver"))
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(KEEP_URL)

        # 检测 iframe 并切入（HuggingFace 常见）
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            driver.switch_to.frame(iframes[0])
            print(f"已进入 iframe")

        # 尝试点击“get this app back up”
        back_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'get this app back up')]")
        if not back_buttons:
            print("页面正常，无需唤醒。")
            driver.quit()
            return

        # 点击 “get this app back up”
        back_buttons[0].click()
        print("已点击 get this app back up，等待 30 秒恢复...")
        time.sleep(30)

        # 再次点击 “启动部署”
        deploy_buttons = driver.find_elements(By.XPATH, "//button[contains(., '启动部署')]")
        if deploy_buttons:
            deploy_buttons[0].click()
            print("已点击启动部署 ✅")

            # 两个都成功后发通知
            send_telegram_message(f"✅ <b>{KEEP_URL}</b> 已点击唤醒并启动部署成功")
        else:
            print("❌ 找不到启动部署按钮")
        driver.quit()

    except Exception as e:
        print(f"[Selenium 错误] {e}")
        send_telegram_message(f"❌ <b>{KEEP_URL}</b> Selenium 错误：<code>{str(e)}</code>")

# ==== 主监控线程（定时执行）====
def monitor_loop():
    print("===== 开始每 30 分钟自动检测 streamlit 页面状态 =====")
    while True:
        wake_up_if_needed()
        time.sleep(CHECK_INTERVAL)

# ==== 启动 Flask + 监控线程 ====
if __name__ == "__main__":
    print("===== 应用启动，开启 Flask + 监控线程 =====")
    threading.Thread(target=monitor_loop, daemon=True).start()
    run_flask()