import telebot
import os
from dotenv import load_dotenv  

load_dotenv()
API_TOKEN = os.environ.get('API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    first_name = message.from_user.first_name
    bot.reply_to(message, f"""\
        سلام {first_name}. خیلی خوش اومدی.
من *رصدخــــان* هستم. از آشنایی باهات خوشحالم. 😄🤍
""", parse_mode='Markdown')
    
# Handle '/options'
@bot.message_handler(commands=['options'])
def send_options(message):
    bot.send_message(message.chat.id, """\
        *رصدخــــان* این‌جاست تا از پس کارهای متنوعی بربیاد! 😎
                     
*قابلیت‌های فعلی من*:
🔗 دریافت لینک کانال رصد علم و صنعت در پیام‌رسان‌های مختلف
📚 پیشنهاد دروسی که قراره در تابستون ارائه بشه
🗣 دریافت نظرات، پیشنهادات و انتقادات شما به‌صورت کاملا ناشناس 
(حتی می‌تونی بهمون پیشنهاد بدی که جای چی توی ربات خالیه)
""", parse_mode='Markdown')

bot.infinity_polling()