# your_app/management/commands/listen_telegram.py
from django.core.management.base import BaseCommand
from telegramBot.bot_manager import TelegramBotManager  # Adjust import path
import time
from django.utils import timezone
from users.models import User
from userOTP.models import UserOTP


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
        
        def normalize_phone(phone_text):
            """Return digits-only phone number, trimmed to last 12 digits."""
            if not phone_text:
                return None
            digits = ''.join(ch for ch in str(phone_text) if ch.isdigit())
            # keep last 12 to handle country codes; your DB expects 8-12 digits
            return digits[-12:] if digits else None

        while True:
            try:
                # Get new messages from Telegram
                updates = bot_manager.get_updates(offset=last_update_id)
                
                if updates and updates.get('ok'):
                    for update in updates.get('result', []):
                        update_id = update['update_id']
                        message = update.get('message', {})
                        text = (message.get('text') or '').strip()
                        chat = message.get('chat', {})
                        chat_id = chat.get('id')
                        user_info = message.get('from', {})
                        contact = message.get('contact')
                        
                        # Handle contact share (preferred secure flow)
                        if contact and contact.get('phone_number'):
                            raw_phone = contact.get('phone_number')
                            phone_number = normalize_phone(raw_phone)
                            if not phone_number:
                                bot_manager.send_message(chat_id, "لم نتمكن من قراءة رقم هاتفك. حاول مرة أخرى.")
                                last_update_id = update_id + 1
                                continue
                            user = User.objects.filter(phone=phone_number, is_deleted=False).first()
                            if not user:
                                bot_manager.send_message(chat_id, "لا يوجد حساب مرتبط بهذا الرقم.")
                                last_update_id = update_id + 1
                                continue
                         
                            # Create OTP for this purpose
                            otp = UserOTP.objects.create(user=user, purpose="telegram_login")

                            bot_manager.send_message(chat_id, f"تم إرسال رمز التحقق: {otp.otp_code}\nأرسل الرمز هنا لإتمام الربط.")
                            last_update_id = update_id + 1
                            continue

                        # Process /start command
                        if text.startswith('/start'):
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'🎉 New user started chat: {user_info.get("first_name")} (@{user_info.get("username", "null")}) (ID: {chat_id})'
                                )
                            )
                            # If user already linked, greet
                            existing = User.objects.filter(telegram_chat_id=str(chat_id), is_deleted=False).first()
                            if existing:
                                bot_manager.send_message(chat_id, f"مرحباً {existing.first_name}! حسابك مرتبط بالفعل.")
                            else:
                                # Extract optional phone after /start
                                phone_number = None
                                if ' ' in text:
                                    phone_number = normalize_phone(text.split(' ', 1)[1].strip())

                                if phone_number:
                                    user = User.objects.filter(phone=phone_number, is_deleted=False).first()
                                    if user:
                                        otp = UserOTP.objects.create(user=user, purpose="telegram_login")
                                        # TelegramLink.objects.update_or_create(
                                        #     chat_id=str(chat_id),
                                        #     defaults={
                                        #         'user': user,
                                        #         'phone': phone_number,
                                        #         'otp_code': otp.otp_code,
                                        #         'expire_at': otp.expire_at,
                                        #         'attempts_left': 5,
                                        #         'is_verified': False
                                        #     }
                                        # )
                                        bot_manager.send_message(chat_id, f"تم إرسال رمز التحقق: {otp.otp_code}\nأرسل الرمز هنا لإتمام الربط.")
                                    else:
                                        bot_manager.send_message(chat_id, "لا يوجد حساب بهذا الرقم. استخدم زر مشاركة الرقم أو سجّل حساباً.")
                                else:
                                    # Ask to share contact
                                    bot_manager.send_contact_request(chat_id)

                        # Handle 4-digit OTP input
                        # elif text.isdigit() and 4 <= len(text) <= 6:
                        #     session = TelegramLink.objects.filter(chat_id=str(chat_id), is_verified=False).first()
                        #     if not session:
                        #         last_update_id = update_id + 1
                        #         continue
                        #     if timezone.now() > session.expire_at:
                        #         bot_manager.send_message(chat_id, "انتهت صلاحية الرمز. الرجاء إرسال رقمك مرة أخرى للحصول على رمز جديد.")
                        #         session.delete()
                        #         last_update_id = update_id + 1
                        #         continue
                        #     if session.attempts_left <= 0:
                        #         bot_manager.send_message(chat_id, "تم تجاوز عدد المحاولات. أعد العملية من جديد.")
                        #         session.delete()
                        #         last_update_id = update_id + 1
                        #         continue

                            # if text == session.otp_code:
                            #     # Link chat to user
                            #     user = session.user
                            #     user.telegram_chat_id = str(chat_id)
                            #     user.save()
                            #     session.is_verified = True
                            #     session.save()
                            #     bot_manager.send_message(chat_id, f"تم ربط حسابك بنجاح. أهلاً {user.first_name}!")
                            # else:
                            #     session.attempts_left = max(0, session.attempts_left - 1)
                            #     session.save()
                            #     bot_manager.send_message(chat_id, f"رمز غير صحيح. المحاولات المتبقية: {session.attempts_left}")
                        
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