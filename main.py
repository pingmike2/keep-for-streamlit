import os
import time
import threading
import requests
from datetime import datetime, timedelta
from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from uuid import uuid4
import glob
import shutil

# ==== 环境变量 ====
KEEP_URL = os.getenv("KEEP_URL", "")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "600"))  # 每 10 分钟检查一次
log_file = "click_log.txt"
log_retention_days = 2

# ==== Flask Web 保活 ====
app = Flask(__name__)
@app.route("/")
def index():
    return "🟢 Click monitor running"

def run_flask():
    app.run(host="0.0.0.0", port=7860)

# ==== 清理旧日志 ====
def clean_old_logs():
    if not os.path.exists(log_file):
        return
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        cutoff = datetime.now() - timedelta(days=log_retention_days)
        cleaned = []
        for line in lines:
            if line.startswith("["):
                try:
                    t = line.split("]")[0][1:]
                    if datetime.strptime(t, "%Y-%m-%d %H:%M:%S") >= cutoff:
                        cleaned.append(line)
                except:
                    cleaned.append(line)
            else:
                cleaned.append(line)
        with open(log_file, "w", encoding="utf-8") as f:
            f.writelines(cleaned)
    except Exception as e:
        print(f"日志清理失败: {e}")

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

# ==== 主逻辑 ====
def wake_up_if_needed():
    print(f"[{datetime.now()}] 🔍 正在访问 {KEEP_URL} 检查状态...")

    # 创建唯一 user-data-dir 防止冲突
    user_data_dir = f"/tmp/chrome-data-{uuid4()}"
    os.makedirs(user_data_dir, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = ""

    try:
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(KEEP_URL)
        print("✅ 页面已打开，等待加载 30 秒...")
        time.sleep(30)

        # 切入 iframe
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            driver.switch_to.frame(iframes[0])
            print("🌐 检测到 iframe，进入第一个")

        # 查找按钮
        buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'get this app back up')]")

        if buttons:
            buttons[0].click()
            print("✅ 检测到按钮并点击，等待 45 秒恢复...")
            time.sleep(45)
            log_entry = f"[{timestamp}] 按钮已点击，已等待45秒完成\n"
            send_telegram_message(f"✅ <b>{KEEP_URL}</b> 已点击 <b>get this app back up</b> 并等待恢复")
        else:
            print("❌ 未检测到按钮，跳过点击。")
            log_entry = f"[{timestamp}] 未发现按钮，未执行点击\n"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

        driver.quit()
    except Exception as e:
        print(f"[错误] {e}")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] 错误：{str(e)}\n")
        send_telegram_message(f"❌ <b>{KEEP_URL}</b> 执行异常：<code>{str(e)}</code>")
    finally:
        shutil.rmtree(user_data_dir, ignore_errors=True)

# ==== 定时任务 ====
def monitor_loop():
    print("===== 每 10 分钟检查一次 HuggingFace 应用状态 =====")
    clean_old_logs()
    while True:
        wake_up_if_needed()
        time.sleep(CHECK_INTERVAL)

# ==== 启动 Flask 和监控 ====
if __name__ == "__main__":
    print("===== 应用启动，开启 Flask + 监控线程 =====")
    threading.Thread(target=monitor_loop, daemon=True).start()
    run_flask()