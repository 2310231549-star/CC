"""
飞书双向机器人 — 接收消息 + 自动回复
基于 WebSocket 长连接，不需要公网服务器，本地直接跑

用法：填好下面的 APP_ID / APP_SECRET / ENCRYPT_KEY，然后 python feishu_bot_reply.py
"""
from wslarkbot import Bot, Client
import json


APP_ID = "cli_xxxxxxxxxxxxxxxx"       # 替换：飞书开放平台 → 凭证与基础信息
APP_SECRET = "xxxxxxxxxxxxxxxx"       # 替换：飞书开放平台 → 凭证与基础信息
ENCRYPT_KEY = "xxxxxxxxxxxxxxxx"      # 替换：飞书开放平台 → 事件订阅 → Encrypt Key
                                       # （如果没有加密选项，用 Verification Token 试试）


class MyBot(Bot):
    def on_message(self, data, raw_message, **kwargs):
        """收到任何消息时触发"""
        header = data.get("header", {})
        event_type = header.get("event_type", "")

        # 只处理用户发来的消息
        if event_type != "im.message.receive_v1":
            return

        event = data.get("event", {})
        message = event.get("message", {})
        message_id = message.get("message_id", "")
        content = json.loads(message.get("content", "{}"))
        text = content.get("text", "")

        print(f"📩 收到消息: {text}")

        # ===== 在这里写你的处理逻辑 =====
        reply_text = self.process(text)
        # ================================

        self.reply_text(message_id, reply_text)
        print(f"📤 已回复: {reply_text}")

    def process(self, text):
        """自定义处理逻辑 — 改成你想要的"""
        text = text.strip()

        if "你好" in text:
            return "你好！我是张睿的助手机器人 🤖"
        elif "时间" in text or "几点" in text:
            from datetime import datetime
            return f"现在是 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elif "天气" in text:
            return "这个功能还没接，但你可以问我时间和打招呼 😄"
        else:
            return f"收到你的消息：{text}\n（更多功能开发中...）"


if __name__ == "__main__":
    bot = MyBot(app_id=APP_ID, app_secret=APP_SECRET, encrypt_key=ENCRYPT_KEY)
    client = Client(bot)
    print("🚀 机器人已启动，等待消息中...")
    print("  在飞书里 @机器人 或私聊发消息试试！")
    print("  Ctrl+C 停止\n")
    client.start()
