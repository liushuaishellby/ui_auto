import requests
import os
from datetime import datetime

class TelegramNotifier:
    def __init__(self):
        # 设置默认的 bot token 和 chat id
        self.bot_token = '8149838795:AAF5almkKvZeanLksDaJnLteCa7eHbDjZG8'
        self.chat_id = '5312996480'
        
    def set_credentials(self, bot_token, chat_id):
        """设置机器人凭证"""
        # 如果提供了新的凭证，则使用新的；否则保持默认值
        self.bot_token = bot_token if bot_token else '8149838795:AAF5almkKvZeanLksDaJnLteCa7eHbDjZG8'
        self.chat_id = chat_id if chat_id else '5312996480'
        
    def send_message(self, message):
        """发送消息到Telegram"""
        if not self.bot_token or not self.chat_id:
            return False
            
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            formatted_message = f"[{timestamp}]\n{message}"
            
            data = {
                "chat_id": self.chat_id,
                "text": formatted_message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data)
            return response.status_code == 200
        except Exception as e:
            print(f"发送Telegram消息失败: {str(e)}")
            return False 