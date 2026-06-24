import telebot
import os
from dotenv import load_dotenv
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telebot import types

load_dotenv()
API_TOKEN = os.environ.get('API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder= 'Chat with رصدخـــان')
    markup.add(KeyboardButton('🔗 لینک‌های رصد'), KeyboardButton('🗣 ارائۀ نظرات'))
    markup.add('📚 پیشنهاد دروس ترم تابستان') #another way to create a button
    markup.add('🤔 دانشجوها چی می‌گن؟')
    first_name = message.from_user.first_name
    text = f'''سلام {first_name}. خیلی خوش اومدی.
من <b>رصدخــــان</b> هستم. از آشنایی باهات خوشحالم. 😄🤍'''
    bot.reply_to(message, text, parse_mode='HTML', reply_markup = markup)

# Handle '/options'
@bot.message_handler(commands=['options'])
def send_options(message):
    text = f'''<b>رصدخــــان</b> این‌جاست تا از پس کارهای متنوعی بربیاد! 😎\n
<b>قابلیت‌های فعلی من</b>:
🗣 دریافت <b>نظرات، پیشنهادات و انتقادات شما</b> به‌صورت ناشناس 
(حتی می‌تونی بهمون پیشنهاد بدی که <b>جای چی توی ربات خالیه</b>)
🔗 دریافت <b>لینک‌های مرتبط با نشریۀ رصد علم و صنعت</b> در پیام‌رسان‌های مختلف
📚 <b>پیشنهاد دروسی که قراره در تابستون ارائه بشه</b>
'''
    bot.send_message(message.chat.id, text, parse_mode='HTML')

@bot.message_handler(func = lambda message: message.text == '🔗 لینک‌های رصد')
def send_links(message):
    text = '''<b>نشریۀ رصد دانشگاه علم و صنعت</b> رو می‌تونی از طریق لینک‌های زیر دنبال کنی:\n
🔹 کانال رصد علم و صنعت در تلگرام
t.me/rasad_iust\n
🔸 گروه دیدگاه رصد در تلگرام
t.me/rasad_comment\n
🤖 ربات رصدخــــان
t.me/rasadkhan_bot\n
🔹 کانال رصد علم و صنعت در بله
ble.ir/rasad_iust'''
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton('🔹 کانال تلگرام', url='https://t.me/rasad_iust')
    button2 = types.InlineKeyboardButton('🔸 گروه تلگرام', url='https://t.me/rasad_comment')
    button3 = types.InlineKeyboardButton('🤖 ربات تلگرام', url='https://t.me/rasadkhan_bot')
    button4 = types.InlineKeyboardButton('🔹 کانال بله', url='https://ble.ir/join/rasad_iust')
    keyboard.row(button2, button1)
    keyboard.row(button4, button3)
    bot.reply_to(message, text, parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard)

@bot.message_handler(func = lambda message: message.text == '🗣 ارائۀ نظرات')
def send_opinion(message):
    text = '''رویکرد ما در رصد از اولین روز تشکیل نشریه، ارتباط دوستانه و تعامل با دانشجویان در بهترین سطح بوده و خواهد بود.
از شما دعوت می‌کنیم نظرات، پیشنهادات و انتقادات خود درمورد هر مسئلۀ کوچک یا بزرگ در رصد رو به گوش ما برسونید تا بتونیم با همکاری شما سعی در بهبود روندمون داشته باشیم. ❤️
لازمه به این نکته توجه کنید که پیام شما <u>به‌صورت کاملا ناشناس</u> در اختیار مسئولین نشریۀ رصد علم و صنعت قرار می‌گیره. پس می‌تونی پیام خودت رو به‌صورت واضح به ما برسونی. 🤝'''
    remove_keyboard = ReplyKeyboardRemove()
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=remove_keyboard)
    bot.register_next_step_handler(message, receive_feedback)

def receive_feedback(message):
    user_feedback = message.text
    feedback_to_admin = f'''پیام جدید از بخش\n <b>🗣 ارائۀ نظرات</b>:\n
{user_feedback}'''
    try:
        bot.send_message(os.environ.get('ADMIN_GROUP_ID'), feedback_to_admin, parse_mode='HTML')
        text = '''ممنون بابت ارسال بازخوردت! 🌱
پیام به مسئولین نشریه ارسال شد. درصورت ارسال پاسخ توسط مسئولین نشریه، اون رو برات می‌فرستم.'''
    except Exception as e:
        text = '''متأسفانه ارسال پیام موفقیت‌آمیز نبود. لطفا ساعاتی دیگر مجدد تلاش کنید.'''
    markup = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder='Chat with رصدخـــان')
    markup.add(KeyboardButton('🔗 لینک‌های رصد'), KeyboardButton('🗣 ارائۀ نظرات'))
    markup.add('📚 پیشنهاد دروس ترم تابستان')
    markup.add('🤔 دانشجوها چی می‌گن؟')
    bot.reply_to(message, text, reply_markup=markup)

@bot.message_handler(func = lambda message: message.text == '🤔 دانشجوها چی می‌گن؟')
def student_voice(message):
    text = '''نظر خودت رو درمورد موضوع مطرح‌شده در کانال ارسال کن.
درصورت تایید توسط ادمین‌ها، پیام شما از طریق کانال منتشر خواهد شد.
این پیام به‌صورت <u>ناشناس</u> به‌دست ادمین‌ها خواهد رسید.'''
    remove_keyboard = ReplyKeyboardRemove()
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=remove_keyboard)
    bot.register_next_step_handler(message, receive_voice)

def receive_voice(message):
    user_feedback = message.text
    feedback_to_telegram = f'''#ارسالی_شما
🗣 « <i>{user_feedback}</i> »\n
<a href="https://t.me/rasadkhan_bot">📬 شما هم دیدگاه خود را ارسال کنید.</a>\n
<b>🔭 رصد | راوی صدای دانشجو
🆔 @rasad_iust</b>'''
    feedback_to_bale = f'''#ارسالی_شما
🗣 « _{user_feedback}_ »\n
[📬 شما هم دیدگاه خود را ارسال کنید.](https://ble.ir/MsngrBot?start=473399195A)\n
🔭 *رصد | راوی صدای دانشجو
🆔 @rasad_iust | [Telegram](https://t.me/rasad_iust)*'''
    try:
        bot.send_message(os.environ.get('ADMIN_GROUP_ID'), 'پیام جدید از بخش\n <b>🤔 دانشجوها چی می‌گن؟</b>:', parse_mode='HTML')
        bot.send_message(os.environ.get('ADMIN_GROUP_ID'), feedback_to_telegram, parse_mode='HTML', disable_web_page_preview=True)
        bot.send_message(os.environ.get('ADMIN_GROUP_ID'), feedback_to_bale, parse_mode='HTML', disable_web_page_preview=True)
        text = '''ممنون بابت ارسال بازخوردت! 🌱
پیام به مسئولین نشریه ارسال شد.'''
    except Exception as e:
        text = '''متأسفانه ارسال پیام موفقیت‌آمیز نبود. لطفا ساعاتی دیگر مجدد تلاش کنید.'''
    markup = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder='Chat with رصدخـــان')
    markup.add(KeyboardButton('🔗 لینک‌های رصد'), KeyboardButton('🗣 ارائۀ نظرات'))
    markup.add('📚 پیشنهاد دروس ترم تابستان')
    markup.add('🤔 دانشجوها چی می‌گن؟')
    bot.reply_to(message, text, reply_markup=markup)

bot.infinity_polling()