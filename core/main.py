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
ADMIN_ID = os.environ.get('ADMIN_ID')
ADMIN_GROUP_ID = os.environ.get('ADMIN_GROUP_ID')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
COLLAB_CHANNEL_ID = os.environ.get('COLLAB_CHANNEL_ID')
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

    cursor.execute("PRAGMA table_info(course_suggestions)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'attendance_type' not in columns:
        cursor.execute('ALTER TABLE course_suggestions ADD COLUMN attendance_type TEXT DEFAULT NULL')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pending_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            content TEXT,
            message_id INTEGER,
            admin_id INTEGER,
            admin_username TEXT,
            status TEXT,
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

def save_course_suggestion(user_id, username, full_name, student_id, major, courses_list, attendance_type):
    gregorian, shamsi = get_current_time()
    courses_text = '\n'.join(courses_list)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO course_suggestions (user_id, username, full_name, student_id, major, courses, attendance_type, timestamp, date_shamsi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, full_name, student_id, major, courses_text, attendance_type, gregorian, shamsi))
    conn.commit()
    conn.close()

def save_pending_message(user_id, username, content, message_id):
    gregorian, shamsi = get_current_time()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO pending_messages (user_id, username, content, message_id, status, timestamp, date_shamsi)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, content, message_id, 'pending', gregorian, shamsi))
    conn.commit()
    conn.close()
    return cursor.lastrowid

def update_pending_message_status(pending_id, status, admin_id, admin_username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE pending_messages 
        SET status = ?, admin_id = ?, admin_username = ?
        WHERE id = ?
    ''', (status, admin_id, admin_username, pending_id))
    conn.commit()
    conn.close()

CANCEL_BUTTON = '❌ لغو'
temp_data = {}

def get_main_menu_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder='درحال چت با رصدخان (چه سعادتی!)')
    markup.add(KeyboardButton('🔗 لینک‌های رصد'), KeyboardButton('🗣 ارائۀ نظرات'))
    markup.add('📚 پیشنهاد دروس ترم تابستان')
    markup.add('🤔 دانشجوها چی می‌گن؟')
    return markup

def return_to_main_menu(message, cancel_message="عملیات لغو شد. به منوی اصلی بازگشتید."):
    bot.reply_to(message, cancel_message, reply_markup=get_main_menu_keyboard())

def membership_required(func):
    def wrapper(message):
        user_id = message.from_user.id
        username = message.from_user.username or ""
        try:
            member = bot.get_chat_member(CHANNEL_ID, user_id)
            if member.status in ['member', 'administrator', 'creator']:
                return func(message)
            else:
                log_user_action(user_id, username, "MEMBERSHIP_CHECK", "کاربر عضو کانال نیست")
                text = f"""⚠️ کاربر عزیز، برای استفاده از این بخش باید عضو کانال ما باشید.

🔹 لطفاً ابتدا عضو کانال [رصد علم و صنعت](https://t.me/rasad_iust) بشید و بعد دوباره امتحان کنید.

✅ بعد از عضویت، دکمه مورد نظر رو دوباره بزنید."""
                bot.reply_to(message, text, parse_mode='Markdown', disable_web_page_preview=True)
                return
        except Exception as e:
            log_user_action(user_id, username, "MEMBERSHIP_ERROR", f"خطا در بررسی عضویت: {str(e)}")
            bot.reply_to(message, "❌ خطایی در بررسی عضویت رخ داد. لطفاً دوباره تلاش کنید.")
            return
    return wrapper

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    save_or_update_user(user.id, user.username or "", user.first_name, user.last_name or "")
    log_user_action(user.id, user.username or "", "START", "کاربر ربات را استارت کرد")
    
    first_name = user.first_name
    text = f'''به به! ببین کی این‌جاست. 😎
جمعمون جمع بود گلمون کم بود. خوش اومدی {first_name}.
من <b>رصدخــــــان‌</b>ام.'''
    markup = get_main_menu_keyboard()
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)

@bot.message_handler(commands=['options'])
def send_options(message):
    user = message.from_user
    log_user_action(user.id, user.username or "", "OPTIONS", "نمایش گزینه‌ها")
    
    text = f'''<b>رصدخــــــان</b> پهلوون علموصه! 😎\n
<b>قابلیت‌های فعلی من</b>:
🗣 <u>شنیدن نظرات، پیشنهادات و انتقاداتت به گوش جانننن</u>، کاملا هم ناشناس.
(حتی می‌تونی بهمون پیشنهاد بدی که جای چی توی ربات خالیه. <b>اصن شما جون بخواه.</b>)
🔗 دریافت لینک‌های مرتبط با <b>نشریۀ رصد علم و صنعت در پیام‌رسان‌های مختلف</b> (مهمون ما باش!)
📚 پیشنهاد دروسی که قراره توی <u>ترم تابستون</u> ارائه بشه'''
    bot.send_message(message.chat.id, text, parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == '🔗 لینک‌های رصد')
def send_links(message):
    user = message.from_user
    log_user_action(user.id, user.username or "", "LINKS", "نمایش لینک‌ها")
    
    text = '''ما این‌جاییم! تو هم بیا تا گل برافشانیم و ساغر و اینا.
نشونی <b>نشریۀ رصد دانشگاه علم و صنعت</b>:\n
🔹 کانال رصد علم و صنعت در تلگرام
t.me/rasad_iust\n
🔸 گروه رصدخــــــانه
t.me/rasadkhane_iust\n
🤖 این‌جانب (ربات رصدخــــــان)
t.me/rasadkhan_bot\n
🔹 کانال رصد علم و صنعت در بله
ble.ir/rasad_iust'''
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton('🔹 کانال تلگرام', url='https://t.me/rasad_iust')
    button2 = types.InlineKeyboardButton('🔭 رصدخــــــانه', url='https://t.me/rasadkhane_iust')
    button3 = types.InlineKeyboardButton('🤖 رصدخــــــان', url='https://t.me/rasadkhan_bot')
    button4 = types.InlineKeyboardButton('🔹 کانال بله', url='https://ble.ir/join/rasad_iust')
    keyboard.row(button2, button1)
    keyboard.row(button4, button3)
    bot.reply_to(message, text, parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '🗣 ارائۀ نظرات')
@membership_required
def send_opinion(message):
    user = message.from_user
    log_user_action(user.id, user.username or "", "OPINION_START", "شروع فرآیند ارسال نظر")
    
    text = '''هدف زندگی من، برقراری ارتباط و تعامل دوستانه تو دانشگاهه. اومدم که <b>چرخ‌دنده‌های آدمای دانشگاهمون کنار هم، مثل ساعت، دست تو دست هم بچرخن.</b>⚙️
هر وقت فکر کردی گیری هست یا یه چراغ بالا سرت روشن شد و چیزی به ذهنت رسید برای روغن‌کاری این چرخ‌دنده‌ها، من <b>گوش جانم رو سپردم که بگی.</b>
کلا هر چه خواست دل تنگت، <u>رصد‌خان این‌جاست تا گوش بده به دردت.</u>♥️\n
نام و نشونتم نشود فاش کسی، غمت نباشه.'''
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(CANCEL_BUTTON))
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
    bot.register_next_step_handler(message, receive_feedback)

def receive_feedback(message):
    user = message.from_user
    if message.text == CANCEL_BUTTON:
        log_user_action(user.id, user.username or "", "CANCEL", "لغو در بخش ارائۀ نظرات")
        return_to_main_menu(message, "❌ ارسال نظر لغو شد.")
        return
    user_feedback = message.text
    
    save_feedback(user.id, user.username or "", "ارائۀ نظرات", user_feedback)
    log_user_action(user.id, user.username or "", "OPINION_SEND", f"ارسال نظر: {user_feedback[:50]}...")
    
    feedback_to_admin = f'''پیام جدید از بخش\n <b>🗣 ارائۀ نظرات</b>:\n
{user_feedback}'''
    
    try:
        bot.send_message(ADMIN_GROUP_ID, feedback_to_admin, parse_mode='HTML')
        text = '''ممنون بابت ارسال بازخوردت! 🌱
پیام به مسئولین نشریه ارسال شد. درصورت ارسال پاسخ توسط مسئولین نشریه، اون رو برات می‌فرستم.'''
    except Exception as e:
        text = '''متأسفانه ارسال پیام موفقیت‌آمیز نبود. لطفا ساعاتی دیگر مجدد تلاش کنید.'''
    
    bot.reply_to(message, text, reply_markup=get_main_menu_keyboard())

@bot.message_handler(func=lambda message: message.text == '🤔 دانشجوها چی می‌گن؟')
@membership_required
def student_voice(message):
    user = message.from_user
    log_user_action(user.id, user.username or "", "STUDENT_VOICE_START", "شروع فرآیند دانشجوها چی می‌گن")
    
    text = '''نظرت در مورد موضوع مطرح شده تو کانال رو فرمایش کن. 
پیامت <u>به‌صورت ناشناس</u> به بروبچ پشت صحنه می‌رسه و بعد از تأیید، منتظر دیدن پیامت توی کانال باش.

می‌پرسی تأیید چیه؟
تایید یعنی ستونـــای پشت صحنه پیام رو از لحاظ <u>محدودیت‌های حقوقی نشریات</u>، بررسی می‌کنن که مثلا توهین، افترا و اینا توی متن پیام‌ها نباشه. در این صورت پیامت، آمادههه برای پرتااابه. 🚀
[<b>پیام‌ها قد جذابیت تو زیادن</b>] بپا توی ترافیک نمونی! 🚙'''
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(CANCEL_BUTTON))
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
    bot.register_next_step_handler(message, receive_voice)

def receive_voice(message):
    user = message.from_user
    if message.text == CANCEL_BUTTON:
        log_user_action(user.id, user.username or "", "CANCEL", "لغو در بخش دانشجوها چی می‌گن")
        return_to_main_menu(message, "❌ ارسال نظر لغو شد.")
        return
    user_feedback = message.text
    
    save_feedback(user.id, user.username or "", "دانشجوها چی می‌گن", user_feedback)
    log_user_action(user.id, user.username or "", "STUDENT_VOICE_SEND", f"ارسال نظر: {user_feedback[:50]}...")
    
    save_pending_message(user.id, user.username or "", user_feedback, message.message_id)
    
    feedback_to_telegram = f'''📨 پیام جدید از بخش 
<b>دانشجوها چی می‌گن؟</b>\n
#ارسالی_شما
🗣 « <i>{user_feedback}</i> »\n
<a href="https://t.me/rasadkhan_bot">📬 شما هم دیدگاه خود را ارسال کنید.</a>\n
<b>🔭 رصد | راوی صدای دانشجو
🆔 @rasad_iust</b>'''
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    approve_button = types.InlineKeyboardButton("✅ تایید و ارسال به کانال", callback_data=f"approve_{user.id}")
    reject_button = types.InlineKeyboardButton("❌ رد", callback_data=f"reject_{user.id}")
    keyboard.add(approve_button, reject_button)
    
    try:
        sent_message = bot.send_message(ADMIN_GROUP_ID, feedback_to_telegram, parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE pending_messages 
            SET message_id = ?
            WHERE user_id = ? AND status = 'pending'
            ORDER BY id DESC LIMIT 1
        ''', (sent_message.message_id, user.id))
        conn.commit()
        conn.close()
        
        text = '''✅ پیام شما با موفقیت به ادمین‌ها ارسال شد!
پس از تایید، در کانال منتشر خواهد شد.'''
        
    except Exception as e:
        print(f"خطا در ارسال به گروه: {e}")
        text = '''❌ متأسفانه ارسال پیام موفقیت‌آمیز نبود. لطفا ساعاتی دیگر مجدد تلاش کنید.'''
    
    bot.reply_to(message, text, reply_markup=get_main_menu_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_') or call.data.startswith('reject_'))
def handle_approval(call):
    admin = call.from_user
    data = call.data.split('_')
    action = data[0]
    user_id = int(data[1])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM pending_messages 
        WHERE user_id = ? AND status = 'pending'
        ORDER BY id DESC LIMIT 1
    ''', (user_id,))
    pending = cursor.fetchone()
    conn.close()
    
    if not pending:
        bot.answer_callback_query(call.id, "❌ این پیام قبلاً بررسی شده است!")
        return
    
    if action == 'approve':
        try:
            channel_message = f'''🗣 « <i>{pending['content']}</i> »\n
<a href="https://t.me/rasadkhan_bot">📬 شما هم دیدگاه خود را ارسال کنید.</a>\n
<b>🔭 رصد | راوی صدای دانشجو
🆔 @rasad_iust</b>'''
            bale_message = f'''#ارسالی_شما
🗣 « _{pending['content']}_ »\n
[📬 شما هم دیدگاه خود را ارسال کنید.](https://ble.ir/MsngrBot?start=473399195A)\n
🔭 *رصد | راوی صدای دانشجو
🆔 @rasad_iust | [Telegram](https://t.me/rasad_iust)*'''
            bot.send_message(CHANNEL_ID, channel_message, parse_mode='HTML', disable_web_page_preview=True)
            update_pending_message_status(pending['id'], 'approved', admin.id, admin.username or "")
            log_user_action(admin.id, admin.username or "", "APPROVE_MESSAGE", f"تایید پیام کاربر {user_id}")
            
            admin_message = f'''✅ <b>پیام تایید شد!</b>

#ارسالی_شما
🗣 « <i>{pending['content']}</i> »\n
<a href="https://t.me/rasadkhan_bot">📬 شما هم دیدگاه خود را ارسال کنید.</a>\n
<b>🔭 رصد | راوی صدای دانشجو
🆔 @rasad_iust</b>

👤 <b>تایید شده توسط:</b> {admin.first_name} (@{admin.username or 'ندارد'})
⏰ <b>زمان تایید:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'''
            
            bot.edit_message_text(admin_message, ADMIN_GROUP_ID, message_id=call.message.message_id, parse_mode='HTML', reply_markup=None)
            
            bot.answer_callback_query(call.id, "✅ پیام تایید و به کانال ارسال شد!")
            
            bot.send_message(ADMIN_GROUP_ID, f"✅ پیام با تایید {admin.first_name} به کانال ارسال شد!", parse_mode='HTML')
            bot.send_message(ADMIN_GROUP_ID, 'مشتیا حالا که پیامو تأیید کردین این پیام پایینیه رو کپ بزنین توی بله!')
            bot.send_message(ADMIN_GROUP_ID, bale_message, disable_web_page_preview=True)
            
        except Exception as e:
            bot.answer_callback_query(call.id, f"❌ خطا: {str(e)}")
            print(f"خطا در ارسال به کانال: {e}")
    
    elif action == 'reject':
        update_pending_message_status(pending['id'], 'rejected', admin.id, admin.username or "")
        log_user_action(admin.id, admin.username or "", "REJECT_MESSAGE", f"رد پیام کاربر {user_id}")
        
        admin_message = f'''❌ <b>پیام رد شد!</b>\n
#ارسالی_شما
🗣 « <i>{pending['content']}</i> »\n
<a href="https://t.me/rasadkhan_bot">📬 شما هم دیدگاه خود را ارسال کنید.</a>\n
<b>🔭 رصد | راوی صدای دانشجو
🆔 @rasad_iust</b>\n
👤 <b>رد شده توسط:</b> {admin.first_name} (@{admin.username or 'ندارد'})
⏰ <b>زمان رد:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'''
        
        bot.edit_message_text(admin_message, ADMIN_GROUP_ID, message_id=call.message.message_id, parse_mode='HTML', reply_markup=None)
        
        bot.answer_callback_query(call.id, "❌ پیام رد شد!")
        
        bot.send_message(ADMIN_GROUP_ID, f"❌ پیام با رد {admin.first_name} مواجه شد!", parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == '📚 پیشنهاد دروس ترم تابستان')
@membership_required
def suggest_courses(message):
    user = message.from_user
    log_user_action(user.id, user.username or "", "COURSE_SUGGEST_START", "شروع فرآیند پیشنهاد دروس")
    text = '''اومدی بخش پیشنهاد دروس برای ترم تابستون ١۴۰۵.
(دمت گرمه‌ها مهندس! ولی پس <u>برنامه‌هایی که برای تابستونت ریخته بودی چی؟!</u>)
لازمه اول بهت بگم که <b>دانشگاه امکان فراهم‌کردن خوابگاه واسۀ دانشجوها رو نداره.</b> پس همین اول کاری بعد ارسال مشخصاتت، این‌که بچه‌زرنگ تهرونی یا می‌تونی تهرون بمونی یا فقط درصورتی که مجازی باشه کلاسا پایه‌ای رو دقیق مشخص کن.

🚨 <u>اطلاعاتت صرفاً برای ارسال به آموزش دانشگاه و تحلیل جمعیت خواستار دروس استفاده می‌شه</u> و ربات هیچ اطلاعات شخصی مثل نام یا شمارۀ دانشجوییتو ذخیره نمی‌کنه.
کلا <b>رصدخــــــان امینته</b>، خیالت راحت از این بابت. 😌\n
✅ لطفاً <b>نام و نام خانوادگی</b> خود را وارد کنید.'''

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(CANCEL_BUTTON))
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
    bot.register_next_step_handler(message, get_full_name)

def get_full_name(message):
    user = message.from_user
    if message.text == CANCEL_BUTTON:
        log_user_action(user.id, user.username or "", "CANCEL", "لغو در مرحله نام و نام خانوادگی (پیشنهاد دروس)")
        return_to_main_menu(message, "❌ عملیات پیشنهاد دروس لغو شد.")
        return
    full_name = message.text
    log_user_action(user.id, user.username or "", "COURSE_FULL_NAME", f"نام وارد شده: {full_name}")
    
    text = 'لطفاً <b>شماره دانشجویی</b> خود را وارد کنید:'
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(CANCEL_BUTTON))
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
    bot.register_next_step_handler(message, get_student_id, full_name)

def get_student_id(message, full_name):
    user = message.from_user
    if message.text == CANCEL_BUTTON:
        log_user_action(user.id, user.username or "", "CANCEL", "لغو در مرحله شماره دانشجویی (پیشنهاد دروس)")
        return_to_main_menu(message, "❌ عملیات پیشنهاد دروس لغو شد.")
        return
    
    student_id = message.text
    log_user_action(user.id, user.username or "", "COURSE_STUDENT_ID", f"شماره دانشجویی: {student_id}")

    temp_data[user.id] = {'full_name': full_name, 'student_id': student_id}
    text = '''🚨<b>دقت دقت:</b>🚨
ببین کدوم یکی وصف حالته و انتخابش کن:\n
<b>١ - چه کلاس‌ها مجازی باشد و چه حضوری توانایی شرکت در کلاس‌ها را دارم.
٢ - تنها درصورتی که کلاس‌ها مجازی باشد توانایی شرکت در کلاس‌ها را دارم..</b>
'''
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton("✅ حضوری و مجازی", callback_data="attendance_both")
    button2 = types.InlineKeyboardButton("📱 فقط مجازی", callback_data="attendance_virtual_only")
    cancel_button = types.InlineKeyboardButton(CANCEL_BUTTON, callback_data='attendance_cancel')
    keyboard.add(button1, button2, cancel_button)
    
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=keyboard)
    
@bot.callback_query_handler(func=lambda call: call.data in ['attendance_both', 'attendance_virtual_only', 'attendance_cancel'])
def handle_attendance(call):
    user = call.from_user

    if call.data == 'attendance_cancel':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.answer_callback_query(call.id, "❌ لغو شد.")
        log_user_action(user.id, user.username or "", "CANCEL", "لغو در مرحله انتخاب شرایط حضور (پیشنهاد دروس)")
        return_to_main_menu(call.message, "❌ عملیات پیشنهاد دروس لغو شد.")
        return

    attendance_type = call.data
    
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.answer_callback_query(call.id, "✅ ثبت شد.")
    
    data = temp_data.get(user.id)
    if not data:
        bot.send_message(call.message.chat.id, "❌ خطا! لطفاً دوباره شروع کن.")
        return
    
    log_user_action(user.id, user.username or "", "COURSE_ATTENDANCE", "حضوری و مجازی" if attendance_type == 'attendance_both' else "فقط مجازی")
    
    text = '''لطفاً <b>رشته و ورودی</b> خود را وارد کنید:
(مثال: مهندسی کامپیوتر - ۱۴۰٣)'''
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(CANCEL_BUTTON))
    bot.send_message(call.message.chat.id, text, parse_mode='HTML', reply_markup=markup)
    bot.register_next_step_handler(call.message, get_major, data['full_name'], data['student_id'], attendance_type)

def get_major(message, full_name, student_id, attendance_type):
    user = message.from_user
    if message.text == CANCEL_BUTTON:
        log_user_action(user.id, user.username or "", "CANCEL", "لغو در مرحله رشته و ورودی")
        return_to_main_menu(message, "❌ عملیات لغو شد.")
        return
    major = message.text
    log_user_action(user.id, user.username or "", "COURSE_MAJOR", major)
    
    text = "لیست دروس رو وارد کن (هر درس جدا، فرمت: نام درس - دانشکده). بعدش اتمام بزن."
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton('✅ اتمام'), KeyboardButton(CANCEL_BUTTON))
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
    bot.register_next_step_handler(message, get_courses, full_name, student_id, major, [], attendance_type)

def get_courses(message, full_name, student_id, major, courses_list, attendance_type):
    user = message.from_user
    if message.text == CANCEL_BUTTON:
        log_user_action(user.id, user.username or "", "CANCEL", "لغو در مرحله لیست دروس (پیشنهاد دروس)")
        return_to_main_menu(message, "❌ عملیات پیشنهاد دروس لغو شد.")
        return
    
    if message.text == '✅ اتمام':
        if len(courses_list) == 0:
            text = '''⚠️ شما هیچ درسی وارد نکردید!\n
لطفاً حداقل <b>یک درس</b> را با فرمت زیر وارد کنید:
<b>نام درس - دانشکده</b>
مثال: ریاضی ۲ - علوم پایه'''
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row(KeyboardButton('✅ اتمام'), KeyboardButton(CANCEL_BUTTON))
            bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
            bot.register_next_step_handler(message, get_courses, full_name, student_id, major, courses_list, attendance_type)
            return
        
        log_user_action(user.id, user.username or "", "COURSE_COMPLETE", f"تعداد دروس: {len(courses_list)}")
        send_courses_to_admin(message, full_name, student_id, major, courses_list, attendance_type)
        return
    
    if ' - ' not in message.text:
        text = '''❌ فرمت وارد شده صحیح نیست!\n
لطفاً درس را به‌صورت زیر وارد کنید:
<b>نام درس - دانشکده</b>
مثال: ریاضی ۲ - علوم پایه\n
یا اگر تمام دروس را وارد کرده‌اید، روی دکمهٔ <b>اتمام</b> کلیک کنید.'''
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(KeyboardButton('✅ اتمام'), KeyboardButton(CANCEL_BUTTON))
        bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
        bot.register_next_step_handler(message, get_courses, full_name, student_id, major, courses_list, attendance_type)
        return
    
    course_name, faculty = message.text.split(' - ', 1)
    course_name = course_name.strip()
    faculty = faculty.strip()
    courses_list.append(f"{course_name} - {faculty}")
    
    log_user_action(user.id, user.username or "", "COURSE_ADD", f"درس اضافه شد: {course_name} - {faculty}")
    
    text = f'''✅ درس <b>{course_name}</b> با موفقیت اضافه شد!\n
📚 دروس ثبت‌شده تا الان:
{chr(10).join([f"🔸 {c}" for c in courses_list])}\n
لطفاً درس بعدی را وارد کنید یا روی دکمهٔ <b>اتمام</b> کلیک کنید.'''
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton('✅ اتمام'), KeyboardButton(CANCEL_BUTTON))
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=markup)
    bot.register_next_step_handler(message, get_courses, full_name, student_id, major, courses_list, attendance_type)

def send_courses_to_admin(message, full_name, student_id, major, courses_list, attendance_type):
    user = message.from_user
    
    save_course_suggestion(user.id, user.username or "", full_name, student_id, major, courses_list, attendance_type)
    log_user_action(user.id, user.username or "", "COURSE_SUBMIT", f"ارسال دروس به ادمین: {len(courses_list)} درس")
    
    courses_text = '\n'.join([f"🔸 {c}" for c in courses_list])
    
    if attendance_type == 'attendance_both':
        attendance_text = "✅ چه کلاس‌ها مجازی باشد و چه حضوری توانایی شرکت را دارم."
    else:
        attendance_text = "📱 تنها درصورت مجازی بودن کلاس‌ها مایل به شرکت هستم."
    
    admin_message = f'''📚 <b>پیشنهاد دروس ترم تابستان</b>\n
👤 <b>نام و نام خانوادگی:</b> {full_name}
🎓 <b>شماره دانشجویی:</b> {student_id}
📚 <b>رشته و ورودی:</b> {major}
📌 <b>شرایط حضور:</b> {attendance_text}\n
📝 <b>لیست دروس پیشنهادی:</b>
{courses_text}
'''
    
    try:
        bot.send_message(ADMIN_GROUP_ID, admin_message, parse_mode='HTML')
        text = '''✅ <b>پیشنهاد دروس شما با موفقیت ثبت شد!</b> 👌🏻
از مشارکت شما در بهبود کیفیت دروس تابستان سپاسگزاریم.
اطلاعات شما به آموزش دانشگاه ارسال خواهد شد.'''
        bot.reply_to(message, text, parse_mode='HTML', reply_markup=get_main_menu_keyboard())
        
        if user.id in temp_data:
            del temp_data[user.id]
        
    except Exception as e:
        print(f"خطا در ارسال به گروه: {e}")
        text = '''❌ متأسفانه ارسال پیشنهادات با مشکل مواجه شد.
لطفاً ساعاتی دیگر مجدد تلاش کنید.'''
        bot.reply_to(message, text, parse_mode='HTML', reply_markup=get_main_menu_keyboard())