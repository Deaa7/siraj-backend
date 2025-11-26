# management/commands/remove_webhook.py
from django.core.management.base import BaseCommand
import requests
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()

class Command(BaseCommand):
    help = 'Remove Telegram webhook to enable polling'
    
    def handle(self, *args, **options):
        bot_token = settings.TELEGRAM_BOT_TOKEN
        url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
        
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                self.stdout.write('✅ Webhook removed successfully!')
                self.stdout.write('🔧 Bot is now ready for polling method')
            else:
                self.stdout.write('❌ Failed to remove webhook')
        else:
            self.stdout.write('❌ HTTP error removing webhook')