import os
import time
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


# === 环境变量 ===
KEEP_URL = os.getenv("KEEP_URL", "https://your-space.hf.space")
ARGO_URL = os.getenv("ARGO_URL", "https://xxxx.trycloudflare.com")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))


def send_telegram_message(text):
    if TG_BOT_TOKEN and TG_CHAT_ID:
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        try:
            requests.post(url, data={
                "chat_id": TG_CHAT_ID,
                "text": text,
                "parse_mode": "HTML"
            }, timeout=5)
        except Exception as e:
            print(f"[Telegram] Failed: {e}")


def is_target_alive():
    try:
        res = requests.get(KEEP_URL, timeout=10)
        print(f"[{datetime.now()}] 状态码: {res.status_code}")
        return res.status_code != 404
    except Exception as e:
        print(f"[检测失败] {e}")
        return False


def wake_up():
    print(f"[⚠️] 服务睡眠，尝试唤醒 {ARGO_URL}")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(ARGO_URL)
        time.sleep(2)

        buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'get this app back up')]")
        if buttons:
            buttons[0].click()
            print("[✔] 点击唤醒按钮成功")
            send_telegram_message(f"✅ <b>{KEEP_URL}</b> 已尝试唤醒")
        else:
            print("[✘] 未找到按钮")
            send_telegram_message(f"⚠️ 未找到唤醒按钮：{KEEP_URL}")
        driver.quit()
    except Exception as e:
        print(f"[Selenium Error] {e}")
        send_telegram_message(f"❌ Selenium 异常：{e}")


def main():
    while True:
        if not is_target_alive():
            wake_up()
        else:
            print(f"[✅] {KEEP_URL} 在线")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()