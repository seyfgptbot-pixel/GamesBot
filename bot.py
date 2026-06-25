import telebot
from telebot import types
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. حط التوكن والـ ID تاعك هنا كالعادة
TOKEN = '8901169943:AAHzlum_EL2qpe9pXo8SRlE1eRgOQpEnS04'
ADMIN_ID = 7315453981  # بدلو بالـ ID تاعك الحقيقي
bot = telebot.TeleBot(TOKEN)

# --- [ خدعة إبقاء البوت حياً 24 ساعة ] ---
def run_dummy_server():
    # يصنع سيرفر ويب وهمي داخلي على المنفذ 8080 لإقناع Render أنه موقع
    server = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
    server.serve_forever()

# تشغيل السيرفر الوهمي في خلفية البوت
threading.Thread(target=run_dummy_server, daemon=True).start()
# ----------------------------------------

DATA_BUTTONS = [{"text": "🌐 موقع جوجل (افتراضى)", "url": "https://www.google.com"}]
admin_steps = {"waiting_for_name": False, "waiting_for_url": False, "temp_name": ""}

@bot.message_handler(commands=['start'])
def start_user(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for item in DATA_BUTTONS:
        btn = types.InlineKeyboardButton(text=item["text"], url=item["url"])
        markup.add(btn)
    bot.send_message(message.chat.id, "🎯 مرحباً بك! اختر واش حاب تليشاريجي تحت:", reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_add = types.InlineKeyboardButton("➕ إضافة زر ورابط جديد", callback_data="add_btn")
        markup.add(btn_add)
        bot.send_message(message.chat.id, "⚙️ لوحة التحكم بالأزرار:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ خطأ: هذا الأمر للأدمن فقط!")

@bot.callback_query_handler(func=lambda call: True)
def admin_callbacks(call):
    if call.message.chat.id == ADMIN_ID and call.data == "add_btn":
        admin_steps["waiting_for_name"] = True
        bot.send_message(call.message.chat.id, "📝 الخطوة 1: ابعثلي اسم الزر:")

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and (admin_steps["wa
