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

# 设置可写缓存目录 + 时区
os.environ["SELENIUM_MANAGER_CACHE_DIR"] = "/tmp/.selenium"
os.environ["TZ"] = "Asia/Shanghai"
time.tzset()

# 环境变量
KEEP_URL = os.getenv("KEEP_URL", "")
ARGO_URL = os.getenv("ARGO_URL", "")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))

# 发送 Telegram 消息
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

# 只认 200 状态码为在线
def is_argo_alive():
    try:
        res = requests.get(ARGO_URL, timeout=10)
        code = res.status_code
        print(f"[{datetime.now()}] {ARGO_URL} 状态码: {code}")
        return code == 200
    except Exception as e:
        print(f"[Argo检测异常] {e}")
        return False

# 点击 KEEP_URL 页面上的按钮进行唤醒
def wake_up():
    print(f"[⚠️] 检测到离线，尝试唤醒：{KEEP_URL}")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=chrome_options)
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
            send_telegram_message(f"⚠️ 未找到唤醒按钮：<b>{KEEP_URL}</b>，可能页面结构变化")

        driver.quit()
    except Exception as e:
        print(f"[Selenium Error] {e}")
        send_telegram_message(f"❌ Selenium 异常：{e}")

# 检测循环
def monitor_loop():
    print(f"===== Application Startup at {datetime.now()} =====")
    while True:
        if not is_argo_alive():
            wake_up()
        else:
            print(f"[✅] Argo 正常在线")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_loop()