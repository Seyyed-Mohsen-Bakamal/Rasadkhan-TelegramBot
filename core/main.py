import telebot
import os
import sqlite3
from datetime import datetime
import pytz
from dotenv import load_dotenv
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telebot import types

load_dotenv()
API_TOKEN = os.environ.get('API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

IRAN_TZ = pytz.timezone('Asia/Tehran')

DB_NAME = 'rasadkhan.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            start_date TEXT,
            last_activity TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            action TEXT,
            details TEXT,
            timestamp TEXT,
            date_shamsi TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            section TEXT,
            content TEXT,
            timestamp TEXT,
            date_shamsi TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS course_suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            full_name TEXT,
            student_id TEXT,
            major TEXT,
            courses TEXT,
            timestamp TEXT,
            date_shamsi TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

init_database()

def get_current_time():
    now_utc = datetime.now(pytz.UTC)
    now_iran = now_utc.astimezone(IRAN_TZ)
    
    gregorian = now_iran.strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        import jdatetime
        shamsi = jdatetime.datetime.fromgregorian(datetime=now_iran).strftime('%Y/%m/%d %H:%M:%S')
    except:
        shamsi = "تبدیل نشد"
    
    return gregorian, shamsi

def log_user_action(user_id, username, action, details=""):
    gregorian, shamsi = get_current_time()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO logs (user_id, username, action, details, timestamp, date_shamsi)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, username, action, details, gregorian, shamsi))
    conn.commit()
    conn.close()

def save_or_update_user(user_id, username, first_name, last_name=""):
    gregorian, shamsi = get_current_time()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    if user:
        cursor.execute('''
            UPDATE users 
            SET username = ?, first_name = ?, last_name = ?, last_activity = ?
            WHERE user_id = ?
        ''', (username, first_name, last_name, gregorian, user_id))
    else:
        cursor.execute('''
            INSERT INTO users (user_id, username, first_name, last_name, start_date, last_activity)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, gregorian, gregorian))
    
    conn.commit()
    conn.close()

def save_feedback(user_id, username, section, content):
    gregorian, shamsi = get_current_time()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO feedbacks (user_id, username, section, content, timestamp, date_shamsi)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, username, section, content, gregorian, shamsi))
    conn.commit()
    conn.close()

def save_course_suggestion(user_id, username, full_name, student_id, major, courses_list):
    gregorian, shamsi = get_current_time()
    courses_text = '\n'.join(courses_list)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO course_suggestions (user_id, username, full_name, student_id, major, courses, timestamp, date_shamsi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, full_name, student_id, major, courses_text, gregorian, shamsi))
    conn.commit()
    conn.close()

# ---------- هندلرهای ربات ----------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    save_or_update_user(user.id, user.username or "", user.first_name, user.last_name or "")
    log_user_action(user.id, user.username or "", "START", "کاربر ربات را استارت کرد")
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder='Chat with رصدخـــان')
    markup.add(KeyboardButton('🔗 لینک‌های رصد'), KeyboardButton('🗣 ارائۀ نظرات'))
    markup.add('📚 پیشنهاد دروس ترم تابستان')
    markup.add('🤔 دانشجوها چی می‌گن؟')
    
    first_name = user.first_name
    text = f'''سلام {first_name}. خیلی خوش اومدی.
من <b>رصدخــــان</b> هستم. از آشنایی باهات خوشحالم. 😄🤍'''
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)

@bot.message_handler(commands=['options'])
def send_options(message):
    user = message.from_user
    log_user_action(user.id, user.username or "", "OPTIONS", "نمایش گزینه‌ها")
    
    text = f'''<b>رصدخــــان</b> این‌جاست تا از پس کارهای متنوعی بربیاد! 😎\n
<b>قابلیت‌های فعلی من</b>:
🗣 دریافت <b>نظرات، پیشنهادات و انتقادات شما</b> به‌صورت ناشناس 
(حتی می‌تونی بهمون پیشنهاد بدی که <b>جای چی توی ربات خالیه</b>)
🔗 دریافت <b>لینک‌های مرتبط با نشریۀ رصد علم و صنعت</b> در پیام‌رسان‌های مختلف
📚 <b>پیشنهاد دروسی که قراره در تابستون ارائه بشه</b>
'''
    bot.send_message(message.chat.id, text, parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == '🔗 لینک‌های رصد')
def send_links(message):
    user = message.from_user
    log_user_action(user.id, user.username or "", "LINKS", "نمایش لینک‌ها")
    
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

@bot.message_handler(func=lambda message: message.text == '🗣 ارائۀ نظرات')
def send_opinion(message):
    user = message.from_user
    log_user_action(user.id, user.username or "", "OPINION_START", "شروع فرآیند ارسال نظر")
    
    text = '''رویکرد ما در رصد از اولین روز تشکیل نشریه، ارتباط دوستانه و تعامل با دانشجویان در بهترین سطح بوده و خواهد بود.
از شما دعوت می‌کنیم نظرات، پیشنهادات و انتقادات خود درمورد هر مسئلۀ کوچک یا بزرگ در رصد رو به گوش ما برسونید تا بتونیم با همکاری شما سعی در بهبود روندمون داشته باشیم. ❤️
لازمه به این نکته توجه کنید که پیام شما <u>به‌صورت کاملا ناشناس</u> در اختیار مسئولین نشریۀ رصد علم و صنعت قرار می‌گیره. پس می‌تونی پیام خودت رو به‌صورت واضح به ما برسونی. 🤝'''
    
    remove_keyboard = ReplyKeyboardRemove()
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=remove_keyboard)
    bot.register_next_step_handler(message, receive_feedback)

def receive_feedback(message):
    user = message.from_user
    user_feedback = message.text
    
    save_feedback(user.id, user.username or "", "ارائۀ نظرات", user_feedback)
    log_user_action(user.id, user.username or "", "OPINION_SEND", f"ارسال نظر: {user_feedback[:50]}...")
    
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

@bot.message_handler(func=lambda message: message.text == '🤔 دانشجوها چی می‌گن؟')
def student_voice(message):
    user = message.from_user
    log_user_action(user.id, user.username or "", "STUDENT_VOICE_START", "شروع فرآیند دانشجوها چی می‌گن")
    
    text = '''نظر خودت رو درمورد موضوع مطرح‌شده در کانال ارسال کن.
درصورت تایید توسط ادمین‌ها، پیام شما از طریق کانال منتشر خواهد شد.
این پیام به‌صورت <u>ناشناس</u> به‌دست ادمین‌ها خواهد رسید.'''
    
    remove_keyboard = ReplyKeyboardRemove()
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=remove_keyboard)
    bot.register_next_step_handler(message, receive_voice)

def receive_voice(message):
    user = message.from_user
    user_feedback = message.text
    
    save_feedback(user.id, user.username or "", "دانشجوها چی می‌گن", user_feedback)
    log_user_action(user.id, user.username or "", "STUDENT_VOICE_SEND", f"ارسال نظر: {user_feedback[:50]}...")
    
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
    user = message.from_user
    log_user_action(user.id, user.username or "", "COURSE_SUGGEST_START", "شروع فرآیند پیشنهاد دروس")
    
    remove_keyboard = ReplyKeyboardRemove()
    text = '''سلام! به بخش پیشنهاد دروس برای ترم تابستان ١۴۰۵ خوش آمدید.🌻
در ابتدا لازم به ذکر است که دانشگاه <b>امکان فراهم‌کردن خوابگاه برای دانشجویان غیر بومی در ترم تابستان را ندارد.</b> 
لطفاً در صورت سکونت در تهران یا توانایی اسکان در تهران، فرم زیر را تکمیل کنید.\n
🚨 اطلاعات شما صرفاً برای ارسال به <b>آموزش دانشگاه</b> و تحلیل جمعیت خواستار دروس استفاده می‌شود و ربات <u>هیچ اطلاعات شخصی</u> مانند نام یا شمارۀ دانشجویی شما را ذخیره نمی‌کند.\n
✅ لطفاً <b>نام و نام خانوادگی</b> خود را وارد کنید.'''
    
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=remove_keyboard)
    bot.register_next_step_handler(message, get_full_name)

def get_full_name(message):
    user = message.from_user
    full_name = message.text
    log_user_action(user.id, user.username or "", "COURSE_FULL_NAME", f"نام وارد شده: {full_name}")
    
    text = 'لطفاً <b>شماره دانشجویی</b> خود را وارد کنید:'
    bot.reply_to(message, text, parse_mode='HTML')
    bot.register_next_step_handler(message, get_student_id, full_name)

def get_student_id(message, full_name):
    user = message.from_user
    student_id = message.text
    log_user_action(user.id, user.username or "", "COURSE_STUDENT_ID", f"شماره دانشجویی: {student_id}")
    
    text = '''حالا لطفاً <b>رشته و ورودی</b> خود را وارد کنید:
(مثال: مهندسی کامپیوتر - ۱۴۰٣)'''
    bot.reply_to(message, text, parse_mode='HTML')
    bot.register_next_step_handler(message, get_major, full_name, student_id)

def get_major(message, full_name, student_id):
    user = message.from_user
    major = message.text
    log_user_action(user.id, user.username or "", "COURSE_MAJOR", f"رشته و ورودی: {major}")
    
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
    user = message.from_user
    
    if message.text == '✅ اتمام پیشنهاد دروس':
        if len(courses_list) == 0:
            text = '''⚠️ شما هیچ درسی وارد نکردید!\n
لطفاً حداقل <b>یک درس</b> را با فرمت زیر وارد کنید:
<b>نام درس - دانشکده</b>
مثال: ریاضی ۲ - علوم پایه'''
            bot.reply_to(message, text, parse_mode='HTML')
            bot.register_next_step_handler(message, get_courses, full_name, student_id, major, courses_list)
            return
        
        log_user_action(user.id, user.username or "", "COURSE_COMPLETE", f"تعداد دروس: {len(courses_list)}")
        send_courses_to_admin(message, full_name, student_id, major, courses_list)
        return
    
    if ' - ' not in message.text:
        text = '''❌ فرمت وارد شده صحیح نیست!

لطفاً درس را به‌صورت زیر وارد کنید:
<b>نام درس - دانشکده</b>
مثال: ریاضی ۲ - علوم پایه

یا اگر تمام دروس را وارد کرده‌اید، روی دکمهٔ <b>اتمام</b> کلیک کنید.'''
        bot.reply_to(message, text, parse_mode='HTML')
        bot.register_next_step_handler(message, get_courses, full_name, student_id, major, courses_list)
        return
    
    course_name, faculty = message.text.split(' - ', 1)
    course_name = course_name.strip()
    faculty = faculty.strip()
    courses_list.append(f"{course_name} - {faculty}")
    
    log_user_action(user.id, user.username or "", "COURSE_ADD", f"درس اضافه شد: {course_name} - {faculty}")
    
    text = f'''✅ درس <b>{course_name}</b> با موفقیت اضافه شد!

📚 دروس ثبت‌شده تا الان:
{chr(10).join([f"🔸 {c}" for c in courses_list])}

لطفاً درس بعدی را وارد کنید یا روی دکمهٔ <b>اتمام</b> کلیک کنید.'''
    
    bot.reply_to(message, text, parse_mode='HTML')
    bot.register_next_step_handler(message, get_courses, full_name, student_id, major, courses_list)

def send_courses_to_admin(message, full_name, student_id, major, courses_list):
    user = message.from_user
    
    save_course_suggestion(user.id, user.username or "", full_name, student_id, major, courses_list)
    log_user_action(user.id, user.username or "", "COURSE_SUBMIT", f"ارسال دروس به ادمین: {len(courses_list)} درس")
    
    courses_text = '\n'.join([f"🔸 {c}" for c in courses_list])
    
    admin_message = f'''📚 <b>پیشنهاد دروس ترم تابستان</b>\n
👤 <b>نام و نام خانوادگی:</b> {full_name}
🎓 <b>شماره دانشجویی:</b> {student_id}
📚 <b>رشته و ورودی:</b> {major}\n
📝 <b>لیست دروس پیشنهادی:</b>
{courses_text}
'''
    
    try:
        bot.send_message(os.environ.get('ADMIN_GROUP_ID'), admin_message, parse_mode='HTML')
        
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