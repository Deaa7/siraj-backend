# your_app/management/commands/listen_telegram.py
from django.core.management.base import BaseCommand
from your_app.telegram.bot_manager import TelegramBotManager  # Adjust import path
import time
 

class Command(BaseCommand):
    help = 'Listen for Telegram bot messages (run this in background)'
    
    def handle(self, *args, **options):
        bot_manager = TelegramBotManager()
        last_update_id = None
        
        self.stdout.write(
            self.style.SUCCESS('🤖 Telegram Bot Listener Started...')
        )
        self.stdout.write('⏳ Listening for new messages (Press Ctrl+C to stop)')
        self.stdout.write('📍 Bot is now active! Users can send /start to begin')
        
        while True:
            try:
                # Get new messages from Telegram
                updates = bot_manager.get_updates(offset=last_update_id)
                
                if updates and updates.get('ok'):
                    for update in updates.get('result', []):
                        update_id = update['update_id']
                        message = update.get('message', {})
                        text = message.get('text', '').strip()
                        chat = message.get('chat', {})
                        chat_id = chat.get('id')
                        user_info = message.get('from', {})
                        
                        # Process /start command
                        if text.startswith('/start'):
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'🎉 New user started chat: {user_info.get("first_name")} '
                                    f'(@{user_info.get("username", "no_username")}) '
                                    f'(ID: {chat_id})'
                                )
                            )
                            
                            # Extract phone number if provided
                            phone_number = None
                            if ' ' in text:
                                phone_number = text.split(' ', 1)[1].strip()
                                self.stdout.write(
                                    self.style.SUCCESS(f'   📱 Phone number: {phone_number}')
                                )
                            
                            # Handle the start command
                            bot_manager.handle_start_command(chat_id, user_info, phone_number)
                        
                        # Update last processed update ID
                        last_update_id = update_id + 1
                
                # Wait before next poll
                time.sleep(1)
                
            except KeyboardInterrupt:
                self.stdout.write(
                    self.style.WARNING('\n🛑 Bot listener stopped by user')
                )
                break
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error: {str(e)}')
                )
                time.sleep(5)  # Wait 5 seconds before retrying