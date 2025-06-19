# 🚀 HuggingFace Auto WakeUp Bot (Selenium Version)

通过监控 Hugging Face 的 Argo 隧道地址是否掉线（返回 404），若离线则自动访问 Hugging Face 空间页面并点击 **"get this app back up"** 按钮进行唤醒。支持 Telegram 通知、重试机制和 Hugging Face 保活页面。

---

## 🌐 项目用途

适用于部署在 Hugging Face Spaces 上的 Gradio 或 Streamlit 项目，为了防止长期不活动导致空间休眠，本项目通过 **自动检测和点击唤醒按钮** 实现 **保活 + 自动恢复服务**。

---

## 🧪 功能特性

- ✅ 定时检测 Argo 隧道是否在线（通过 `ARGO_URL`）
- ⚙️ 若 Argo 返回 404（断线），自动访问 `KEEP_URL` 并点击按钮唤醒
- 🔁 最多点击 3 次按钮，失败才发 Telegram 提醒
- 🧭 集成 Flask Web 服务（监听 7860 端口，防止 HuggingFace 判定无活动）
- 📨 可选 Telegram 通知（Bot API）

---

## 🐳 如何在 Hugging Face 启动？

### 1️⃣ 打开 Hugging Face ➜ 新建空间

- 类型选择：`Docker`
- 名称自定义，例如：`my-keepalive-bot`

---

### 2️⃣ 提交以下文件至代码仓库

- `Dockerfile`
- `keep_alive.py`
- `requirements.txt`
- `.github/workflows/docker-build.yml`（可选：GitHub Actions 自动推镜像）

---

### 3️⃣ 设置环境变量（点击左侧 "Variables" 面板）

| 变量名         | 示例值                                      |
|----------------|---------------------------------------------|
| `KEEP_URL`     | `https://your-space.hf.space`              |
| `ARGO_URL`     | `https://xxxx.trycloudflare.com`           |
| `TG_BOT_TOKEN` | `你的Telegram机器人Token（可选）`           |
| `TG_CHAT_ID`   | `你的Telegram用户ID（可选）`                 |
| `CHECK_INTERVAL` | `300`（单位：秒）                         |



## 🔧 示例变量说明

```env
KEEP_URL=https://your-space.hf.space         # 用于点击按钮的 Hugging Face 页面地址
ARGO_URL=https://argo-tunnel.trycloudflare.com  # 被检测是否在线的 Argo 隧道地址
TG_BOT_TOKEN=123456789:ABC...                # Telegram Bot Token（可选）
TG_CHAT_ID=123456789                         # Telegram 用户 ID（可选）
CHECK_INTERVAL=300                           # 检测频率（单位：秒），默认300秒，（可选）

```


---

##📦 运行效果
	•	https://your-space.hf.space 被定时点击“唤醒”按钮
	•	首页访问显示 Hello, world. 防止休眠
	•	Argo 掉线后自动重启流量隧道，确保服务外部可用
	•	所有唤醒尝试可选通过 Telegram Bot 实时通知

---

##🧱 控制台输出示例子

[2025-06-19 02:00:00] https://xxxx.trycloudflare.com 状态码: 404
[⚠️] Argo 离线，尝试访问 https://your-space.hf.space 唤醒
[尝试] 第 1 次点击按钮...
[✔] 成功点击按钮
---

##📎 补充说明
	•	默认使用 Selenium + Headless Chrome 模式唤醒页面
	•	已优化兼容 Hugging Face Spaces 的资源限制
	•	如需本地调试，请确保本地有 Chrome + chromedriver

---

❤️ 致谢

本项目灵感来源于社区对 Hugging Face 长时间运行需求，感谢所有反馈与支持。



