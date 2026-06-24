import telebot
import os
from dotenv import load_dotenv
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

load_dotenv()
API_TOKEN = os.environ.get('API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder= 'متن موردنظر خود را بنویسید.')
    markup.add(KeyboardButton('🔗 لینک‌های رصد'), KeyboardButton('🗣 ارائۀ نظر، پیشنهاد یا انتقاد'))
    markup.add('📚 پیشنهاد دروس ترم تابستان', '🤔 دانشجوها چی می‌گن؟') #another way to create a button
    first_name = message.from_user.first_name
    text = f'''سلام {first_name}. خیلی خوش اومدی.
من <b>رصدخــــان</b> هستم. از آشنایی باهات خوشحالم. 😄🤍'''
    bot.reply_to(message, text, parse_mode='HTML', reply_markup = markup)

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