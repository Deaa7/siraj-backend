# management/commands/test_bot.py
from django.core.management.base import BaseCommand
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class Command(BaseCommand):
    help = 'Test Telegram bot connection'
    
    def handle(self, *args, **options):
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        # Test 1: Get bot info
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get('ok'):
                bot_data = bot_info['result']
                self.stdout.write(f"✅ Bot connected: {bot_data['first_name']} (@{bot_data['username']})")
            else:
                self.stdout.write('❌ Bot token invalid')
                return
        else:
            self.stdout.write('❌ Cannot connect to Telegram API')
            return
        
        # Test 2: Check for pending updates
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url)
        
        if response.status_code == 200:
            updates = response.json()
            if updates.get('ok'):
                pending_updates = len(updates.get('result', []))
                self.stdout.write(f"📨 Pending updates: {pending_updates}")
                
                if pending_updates > 0:
                    self.stdout.write("💡 Try clearing updates with: python manage.py clear_updates")
            else:
                self.stdout.write('❌ Cannot get updates')