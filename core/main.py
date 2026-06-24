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

@bot.message_handler(func=lambda message: message.text == '📚 پیشنهاد دروس ترم تابستان')
def suggest_courses(message):
    remove_keyboard = ReplyKeyboardRemove()
    text = '''سلام! به بخش پیشنهاد دروس برای ترم تابستان ١۴۰۵ خوش آمدید.🌻
در ابتدا لازم به ذکر است که دانشگاه <b>امکان فراهم‌کردن خوابگاه برای دانشجویان غیر بومی در ترم تابستان را ندارد.</b> 
لطفاً در صورت سکونت در تهران یا توانایی اسکان در تهران، فرم زیر را تکمیل کنید.\n
🚨 اطلاعات شما صرفاً برای ارسال به <b>آموزش دانشگاه</b> و تحلیل جمعیت خواستار دروس استفاده می‌شود و ربات <u>هیچ اطلاعات شخصی</u> مانند نام یا شمارۀ دانشجویی شما را ذخیره نمی‌کند.\n
✅ لطفاً <b>نام و نام خانوادگی</b> خود را وارد کنید.'''
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=remove_keyboard)
    bot.register_next_step_handler(message, get_full_name)

def get_full_name(message):
    full_name = message.text
    text = 'لطفاً <b>شماره دانشجویی</b> خود را وارد کنید:'
    bot.reply_to(message, text, parse_mode='HTML')
    bot.register_next_step_handler(message, get_student_id, full_name)

def get_student_id(message, full_name):
    student_id = message.text
    text = '''حالا لطفاً <b>رشته و ورودی</b> خود را وارد کنید:
(مثال: مهندسی کامپیوتر - ۱۴۰٣)'''

    bot.reply_to(message, text, parse_mode='HTML')
    bot.register_next_step_handler(message, get_major, full_name, student_id)


def get_major(message, full_name, student_id):
    major = message.text
    text = '''حالا لطفاً <b>لیست دروس پیشنهادی</b> خود را به‌صورت زیر وارد کنید:
🔸 هر درس را <b>در یک پیام جداگانه</b> ارسال کنید
🔹 فرمت هر درس: 
<b>نام درس - دانشکده</b>
مثال: ریاضی ۲ - علوم پایه\n
📌 دقت کنید:
• اسامی دروس <b>کامل و مطابق</b> با آموزش وارد شود
• اعداد با <b>یک فاصله</b> از کلمه جدا شوند (مثال: ریاضی ۲)\n
✅ وقتی تمام دروس را وارد کردید، روی دکمهٔ <b>اتمام</b> کلیک کنید.'''
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('✅ اتمام پیشنهاد دروس'))
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
    bot.register_next_step_handler(message, get_courses, full_name, student_id, major, [])


def get_courses(message, full_name, student_id, major, courses_list):
    if message.text == '✅ اتمام پیشنهاد دروس':
        if len(courses_list) == 0:
            text = '''⚠️ شما هیچ درسی وارد نکردید!\n
لطفاً حداقل <b>یک درس</b> را با فرمت زیر وارد کنید:
<b>نام درس - دانشکده</b>
مثال: ریاضی ۲ - علوم پایه'''
            bot.reply_to(message, text, parse_mode='HTML')
            bot.register_next_step_handler(message, get_courses, full_name, student_id, major, courses_list)
            return

        send_courses_to_admin(message, full_name, student_id, major, courses_list)
        return
    
    # بررسی فرمت درس
    if ' - ' not in message.text:
        text = '''❌ فرمت وارد شده صحیح نیست!

لطفاً درس را به‌صورت زیر وارد کنید:
<b>نام درس - دانشکده</b>
مثال: ریاضی ۲ - علوم پایه

یا اگر تمام دروس را وارد کرده‌اید، روی دکمهٔ <b>اتمام</b> کلیک کنید.'''
        bot.reply_to(message, text, parse_mode='HTML')
        bot.register_next_step_handler(message, get_courses, full_name, student_id, major, courses_list)
        return
    
    # اضافه کردن درس به لیست
    course_name, faculty = message.text.split(' - ', 1)
    course_name = course_name.strip()
    faculty = faculty.strip()
    
    courses_list.append(f"{course_name} - {faculty}")
    
    text = f'''✅ درس <b>{course_name}</b> با موفقیت اضافه شد!

📚 دروس ثبت‌شده تا الان:
{chr(10).join([f"🔸 {c}" for c in courses_list])}

لطفاً درس بعدی را وارد کنید یا روی دکمهٔ <b>اتمام</b> کلیک کنید.'''
    
    bot.reply_to(message, text, parse_mode='HTML')
    bot.register_next_step_handler(message, get_courses, full_name, student_id, major, courses_list)


def send_courses_to_admin(message, full_name, student_id, major, courses_list):
    courses_text = '\n'.join([f"🔸 {c}" for c in courses_list])
    
    admin_message = f'''📚 <b>پیشنهاد دروس ترم تابستان</b>\n
👤 <b>نام و نام خانوادگی:</b> {full_name}
🎓 <b>شماره دانشجویی:</b> {student_id}
📚 <b>رشته و ورودی:</b> {major}\n
📝 <b>لیست دروس پیشنهادی:</b>
{courses_text}
'''
    
    try:
        bot.send_message(os.environ.get('ADMIN_ID'), admin_message, parse_mode='HTML')
        markup = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder='Chat with رصدخـــان')
        markup.add(KeyboardButton('🔗 لینک‌های رصد'), KeyboardButton('🗣 ارائۀ نظرات'))
        markup.add('📚 پیشنهاد دروس ترم تابستان')
        markup.add('🤔 دانشجوها چی می‌گن؟')
        text = '''✅ <b>پیشنهاد دروس شما با موفقیت ثبت شد!</b> 👌🏻
از مشارکت شما در بهبود کیفیت دروس تابستان سپاسگزاریم.
اطلاعات شما به آموزش دانشگاه ارسال خواهد شد.'''
        bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
        
    except Exception as e:
        print(f"خطا در ارسال به گروه: {e}")
        text = '''❌ متأسفانه ارسال پیشنهادات با مشکل مواجه شد.
لطفاً ساعاتی دیگر مجدد تلاش کنید.'''
        markup = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder='Chat with رصدخـــان')
        markup.add(KeyboardButton('🔗 لینک‌های رصد'), KeyboardButton('🗣 ارائۀ نظرات'))
        markup.add('📚 پیشنهاد دروس ترم تابستان')
        markup.add('🤔 دانشجوها چی می‌گن؟')
        bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)

bot.infinity_polling()