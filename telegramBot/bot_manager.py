# management/commands/listen_telegram.py
from django.core.management.base import BaseCommand
import time
import requests
import os
import json
from dotenv import load_dotenv
from users.models import User
from django.utils import timezone

load_dotenv()

class TelegramBotManager:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("❌ TELEGRAM_BOT_TOKEN not found in .env file")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        print(f"✅ Bot token loaded: {self.bot_token[:10]}...")  # DEBUG
    
    def get_updates(self, offset=None):
        # pass
        url = f"{self.base_url}/getUpdates"
        params = {
            'offset': offset, 
            'timeout': 10,
            'allowed_updates': ['message']
        }
        
        # print(f"🔍 Checking for messages with offset: {offset}")  # DEBUG
        
        try:
            response = requests.get(url, params=params, timeout=15)
        #     print(f"📡 HTTP Status: {response.status_code}")  # DEBUG
            
            if response.status_code == 200:
                data = response.json()
                # print(f"📦 Raw API response: {json.dumps(data, indent=2)}")  # DEBUG
                return data
            else:
                # print(f"❌ HTTP Error: {response.status_code} - {response.text}")  # DEBUG
                return None
        except requests.exceptions.Timeout:
            # print("⏰ Request timeout (normal - no new messages)")  # DEBUG
            return {'ok': True, 'result': []}
        except Exception as e:
            # print(f"❌ Request Error: {e}")  # DEBUG
            return None
    
    def send_message(self, chat_id, text):
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id, 
            "text": text,
            "parse_mode": "Markdown"
        }
        print(f"📤 Sending message to {chat_id}: {text}")  # DEBUG
        try:
            response = requests.post(url, json=payload)
            print(f"📨 Send response: {response.status_code}")  # DEBUG
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Send message error: {e}")  # DEBUG
            return False
    
    def send_contact_request(self, chat_id):
        """
        Ask user to share their phone number using Telegram contact button
        """
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": "الرجاء مشاركة رقم هاتفك بالضغط على زر 'إرسال رقمي' لربط حسابك.",
            "reply_markup": {
                "keyboard": [[{"text": "إرسال رقمي", "request_contact": True}]],
                "resize_keyboard": True,
                "one_time_keyboard": True
            }
        }
        try:
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except Exception:
            return False
        
    def handle_start_command(self, chat_id, message):
        """Process /start command from users"""
        # welcome_msg = f"Welcome {user_info.get('first_name', 'Unknown')}! Phone {phone_number} registered. Chat ID: {chat_id}"
        return self.send_message(chat_id, message)
    
    # def handle_help_command(self, chat_id, user_info):
    #     """Process /help command from users"""
    #     help_msg = f"Available commands:\n/start - Link your phone number\n/help - Show this help message"
    #     return self.send_message(chat_id, help_msg)
    
class Command(BaseCommand):
    help = 'Listen for Telegram bot messages'
    
    def handle(self, *args, **options):
        try:
            bot_manager = TelegramBotManager()
        except ValueError as e:
            print(str(e))  # DEBUG
            return
        
        last_update_id = None
        check_count = 0
        
        print("🤖 Telegram Bot Listener Started...")  # DEBUG
        print("⏳ Listening for new messages (Press Ctrl+C to stop)")  # DEBUG
        print("📍 Send '/start' to your bot in Telegram now!")  # DEBUG
        print("=" * 50)  # DEBUG
        
        while True:
            try:
                check_count += 1
                print(f"\n🔄 Check #{check_count}")  # DEBUG
                
                updates = bot_manager.get_updates(offset=last_update_id)
                
                if updates is None:
                    print("⚠️ Could not get updates, retrying...")  # DEBUG
                    time.sleep(5)
                    continue
                
                if updates.get('ok'):
                    results = updates.get('result', [])
                    print(f"📨 Found {len(results)} messages")  # DEBUG
                    
                    for update in results:
                        update_id = update['update_id']
                        message = update.get('message', {})
                        text = message.get('text', '').strip()
                        chat = message.get('chat', {})
                        chat_id = chat.get('id')
                        user_info = message.get('from', {})
                        first_name = user_info.get('first_name', 'Unknown')
                        username = user_info.get('username', 'no_username')
                        
                        # 🎯 THIS IS WHERE MESSAGES ARE PRINTED!
                        print("=" * 50)
                        print(f"🎉 NEW MESSAGE RECEIVED!")
                        print(f"👤 From: {first_name} (@{username})")
                        print(f"💬 Message: '{text}'")
                        print(f"🆔 Chat ID: {chat_id}")
                        print(f"🆔 Update ID: {update_id}")
                        print("=" * 50)
                        
                        if text.startswith('/start'):
                            print("🚀 /start command detected!")  # DEBUG
                            
                            # Extract phone number if provided
                            phone_number = None
                            if ' ' in text:
                                phone_number = text.split(' ', 1)[1].strip()
                                print(f"📱 Phone number: {phone_number}")  # DEBUG
                            
                            user = User.objects.get(telegram_chat_id=chat_id)
                            if user:
                                welcome_msg = f"Welcome {user.first_name}! Phone {user.phone_number} registered. Chat ID: {chat_id}"
                                bot_manager.send_message(chat_id, welcome_msg)
                            else:
                                welcome_msg = f"Welcome {first_name}! Use /start YOUR_PHONE to link account. Chat ID: {chat_id}"
                                bot_manager.send_message(chat_id, welcome_msg)
                            
                            # Send welcome message
                            # if phone_number:
                            #     welcome_msg = f"Welcome {first_name}! Phone {phone_number} registered. Chat ID: {chat_id}"
                            # else:
                            #     welcome_msg = f"Welcome {first_name}! Use /start YOUR_PHONE to link account. Chat ID: {chat_id}"
                            
                            # success = bot_manager.send_message(chat_id, welcome_msg)
                            # if success:
                            #     print("✅ Welcome message sent!")  # DEBUG
                            # else:
                            #     print("❌ Failed to send welcome message")  # DEBUG
                        
                        # Update last processed update ID
                        last_update_id = update_id + 1
                        print(f"📝 Next offset: {last_update_id}")  # DEBUG
                else:
                    print(f"❌ Telegram API error: {updates}")  # DEBUG
                
                # Short sleep between checks
                time.sleep(2)
                
            except KeyboardInterrupt:
                print("\n🛑 Bot listener stopped by user")  # DEBUG
                break
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")  # DEBUG
                time.sleep(5)