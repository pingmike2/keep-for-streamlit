import os
import time
import asyncio
import requests
from datetime import datetime
from playwright.async_api import async_playwright
from selenium.webdriver.common.by import By

# ========= 环境变量配置 =========
KEEP_URL = os.environ.get("KEEP_URL", "")
ARGO_URL = os.environ.get("ARGO_URL", "")
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", "300"))  # 每多少秒检查一次

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")


# ========= 工具函数 =========
def send_telegram_message(message):
    if TG_BOT_TOKEN and TG_CHAT_ID:
        try:
            requests.post(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage", data={
                "chat_id": TG_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }, timeout=5)
        except Exception as e:
            print(f"[❌ Telegram Error] {e}")


def is_target_alive():
    try:
        res = requests.get(KEEP_URL, timeout=10)
        print(f"[{datetime.now()}] {KEEP_URL} 返回状态码：{res.status_code}")
        return res.status_code != 404
    except Exception as e:
        print(f"[❌ 访问失败] {e}")
        return False


async def click_wakeup_button():
    print(f"[⚠️] 检测到服务离线，尝试访问 {ARGO_URL} 唤醒...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(ARGO_URL, timeout=15000)
            await page.wait_for_timeout(2000)  # 等待加载

            # 查询所有按钮
            buttons = await page.query_selector_all("button")
            for button in buttons:
                text = (await button.inner_text()).lower()
                if "get this app back up" in text:
                    await button.click()
                    print(f"[✔] 成功点击唤醒按钮")
                    send_telegram_message(f"✅ <b>{KEEP_URL}</b> 已尝试唤醒")
                    break
            else:
                print(f"[✘] 没找到唤醒按钮")
                send_telegram_message(f"⚠️ 未找到唤醒按钮：<b>{KEEP_URL}</b>")
            await browser.close()
    except Exception as e:
        print(f"[❌ Playwright 异常] {e}")
        send_telegram_message(f"❌ Playwright 出错：{e}")


# ========= 主程序循环 =========
async def main():
    while True:
        if not is_target_alive():
            await click_wakeup_button()
        else:
            print(f"[✅] {KEEP_URL} 正常在线，无需唤醒")
        await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())