import telebot
from telebot import types
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
import sqlite3
import requests

# 1. الإعدادات الأساسية (بدل هادو بالمعلومات تاعك)
TOKEN = '8901169943:AAHzlum_EL2qpe9pXo8SRlE1eRgOQpEnS04'
ADMIN_ID = 7315453981  # الـ ID تاعك
GPLINKS_API_KEY = '2a3196651631ce423da1e16ee8c3237cda64f70f'

bot = telebot.TeleBot(TOKEN)

# --- [ سيرفر وهمي لإبقاء البوت حياً 24 ساعة ] ---
def run_dummy_server():
    server = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()
# ----------------------------------------

# --- [ إعداد قاعدة البيانات SQLite ] ---
# هاد الكود راح يصنع ملف database.db إذا مكانش، ويحفظ فيه الأزرار
conn = sqlite3.connect('bot_database.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS buttons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        url TEXT
    )
''')
conn.commit()
# ----------------------------------------

admin_steps = {"waiting_for_name": False, "waiting_for_url": False, "temp_name": ""}

@bot.message_handler(commands=['start'])
def start_user(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # نجيبو الأزرار من قاعدة البيانات
    cursor.execute("SELECT name, url FROM buttons")
    buttons = cursor.fetchall()
    
    if not buttons:
        bot.send_message(message.chat.id, "عذراً، لا يوجد روابط حالياً. عد لاحقاً! ⏳")
        return
        
    for btn_name, btn_url in buttons:
        markup.add(types.InlineKeyboardButton(text=btn_name, url=btn_url))
        
    bot.send_message(message.chat.id, "🎯 مرحباً بك! اختر واش حاب تليشاريجي تحت:", reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("➕ إضافة زر (اختصار تلقائي)", callback_data="add_btn"))
        bot.send_message(message.chat.id, "⚙️ لوحة التحكم بالأزرار:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ خطأ: هذا الأمر للأدمن فقط!")

@bot.callback_query_handler(func=lambda call: True)
def admin_callbacks(call):
    if call.message.chat.id == ADMIN_ID and call.data == "add_btn":
        admin_steps["waiting_for_name"] = True
        bot.send_message(call.message.chat.id, "📝 الخطوة 1: ابعثلي اسم اللعبة أو التطبيق:")

def check_admin_action(message):
    return message.chat.id == ADMIN_ID and (admin_steps["waiting_for_name"] or admin_steps["waiting_for_url"])

@bot.message_handler(func=check_admin_action)
def handle_admin_inputs(message):
    if admin_steps["waiting_for_name"]:
        admin_steps["temp_name"] = message.text
        admin_steps["waiting_for_name"] = False
        admin_steps["waiting_for_url"] = True
        bot.send_message(message.chat.id, "🔗 الخطوة 2: ابعثلي الرابط **الأصلي/الطويل** (والبوت راح يختصرو وحدو):")
        
    elif admin_steps["waiting_for_url"]:
        long_url = message.text
        bot.send_message(message.chat.id, "⏳ جاري اختصار الرابط في GPLinks...")
        
        try:
            # الاتصال بـ API تاع GPLinks
            api_url = f"https://gplinks.com/api?api={GPLINKS_API_KEY}&url={long_url}"
            response = requests.get(api_url).json()
            
            if response.get('status') == 'success':
                short_url = response['shortenedUrl']
                
                # حفظ في قاعدة البيانات
                cursor.execute("INSERT INTO buttons (name, url) VALUES (?, ?)", (admin_steps["temp_name"], short_url))
                conn.commit()
                
                admin_steps["waiting_for_url"] = False
                bot.send_message(message.chat.id, f"✅ تمت العملية بنجاح!\n\nالرابط المختصر: {short_url}\nتمت إضافته للبوت.")
            else:
                bot.send_message(message.chat.id, "❌ صرات مشكلة في الاختصار. تأكد من الرابط أو الـ API Key.")
                admin_steps["waiting_for_url"] = False
                
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ خطأ في السيرفر: {e}")
            admin_steps["waiting_for_url"] = False

print("البوت جاهز مع قاعدة البيانات والاختصار التلقائي!")
bot.infinity_polling()
