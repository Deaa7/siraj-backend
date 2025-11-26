# # telegram/views.py
# import json
# import os
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_POST
# from dotenv import load_dotenv

# load_dotenv()

# @csrf_exempt
# @require_POST
# def telegram_webhook(request):
#     """
#     This view receives notifications from Telegram when users interact with your bot
#     """
#     try:
#         # Parse the incoming update from Telegram
#         data = json.loads(request.body)
        
#         # Extract basic information
#         update_id = data.get('update_id')
#         message = data.get('message', {})
#         chat = message.get('chat', {})
#         chat_id = chat.get('id')
#         text = message.get('text', '').strip()
#         user = message.get('from', {})
#         user_id = user.get('id')
#         username = user.get('username')
#         first_name = user.get('first_name', '')
        
#         print(f"📨 Received message from {first_name} (@{username}): {text}")
        
#         # Handle /start command
#         if text == '/start' or text.startswith('/start '):
#             handle_start_command(chat_id, text, user)
        
#         return JsonResponse({'status': 'success'})
        
#     except Exception as e:
#         print(f"❌ Webhook error: {str(e)}")
#         return JsonResponse({'status': 'error', 'message': str(e)})

# def handle_start_command(chat_id, text, user):
#     """
#     Handle when user starts a chat with /start command
#     """
#     # Extract phone number if provided: /start 0981234567
#     phone_number = None
#     if ' ' in text:
#         phone_number = text.split(' ', 1)[1].strip()
    
#     # Send welcome message
#     bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
#     if phone_number:
#         # User provided phone number
#         message = (
#             f"👋 Welcome {user.get('first_name', 'there')}!\n\n"
#             f"✅ Your phone number {phone_number} has been registered.\n"
#             f"📱 You'll now receive OTP codes via this chat.\n\n"
#             f"Your Chat ID: `{chat_id}`"
#         )
#     else:
#         # User just sent /start without phone number
#         message = (
#             f"👋 Welcome {user.get('first_name', 'there')}!\n\n"
#             f"I'm your OTP verification bot. To use this service:\n\n"
#             f"1. Create an account on our platform\n"
#             f"2. Use `/start YOUR_PHONE_NUMBER` to link your account\n"
#             f"3. Example: `/start 0981234567`\n\n"
#             f"Once linked, I'll send you OTP codes for secure login! 🔐\n\n"
#             f"Your Chat ID: `{chat_id}`"
#         )
    
#     # Send the message back to user
#     send_telegram_message(bot_token, chat_id, message)

# def send_telegram_message(bot_token, chat_id, text):
#     """
#     Send a message via Telegram Bot API
#     """
#     import requests
#     url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
#     payload = {
#         "chat_id": chat_id,
#         "text": text,
#         "parse_mode": "Markdown"
#     }
    
#     try:
#         response = requests.post(url, json=payload)
#         return response.status_code == 200
#     except Exception as e:
#         print(f"❌ Failed to send Telegram message: {str(e)}")
#         return False