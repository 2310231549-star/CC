"""
飞书消息推送工具 — 最简 Webhook 方式
用法:
    from feishu_sender import FeishuBot
    bot = FeishuBot("你的webhook地址")
    bot.send_text("通知：任务完成！")
    bot.send_card("标题", "**加粗**内容", "- 条目1\n- 条目2")
"""

import requests


class FeishuBot:
    def __init__(self, webhook_url):
        self.url = webhook_url

    def send_text(self, text):
        """发纯文本消息（必须包含你设置的安全关键词）"""
        return requests.post(self.url, json={
            "msg_type": "text",
            "content": {"text": text}
        }).json()

    def send_card(self, title, body_markdown="", note_markdown=""):
        """发消息卡片（蓝底标题 + markdown 正文）"""
        elements = []
        if body_markdown:
            elements.append({"tag": "markdown", "content": body_markdown})
        if note_markdown:
            elements.append({"tag": "hr"})
            elements.append({"tag": "note", "elements": [{"tag": "plain_text", "content": note_markdown}]})

        return requests.post(self.url, json={
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": title},
                    "template": "blue"
                },
                "elements": elements
            }
        }).json()


# ===== 直接运行测试 =====
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python feishu_sender.py <webhook地址> [消息内容]")
        print()
        print("获取 webhook: 飞书群 → 群设置 → 群机器人 → 自定义机器人 → 复制地址")
        print()
        print("示例:")
        print('  python feishu_sender.py "https://open.feishu.cn/open-apis/bot/v2/hook/xxx" "通知：hello world"')
        sys.exit(1)

    webhook = sys.argv[1]
    msg = sys.argv[2] if len(sys.argv) > 2 else "通知：飞书接入测试成功！"

    bot = FeishuBot(webhook)
    result = bot.send_text(msg)
    print(result)
    print("✅ 发送成功！" if result.get("code") == 0 else f"❌ 失败: {result}")
