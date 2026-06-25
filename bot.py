import telebot
from telebot import types
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. حط التوكن والـ ID تاعك هنا كالعادة
TOKEN = '8901169943:AAHzlum_EL2qpe9pXo8SRlE1eRgOQpEnS04'
ADMIN_ID = 7315453981  # بدلو بالـ ID تاعك الحقيقي
bot = telebot.TeleBot(TOKEN)

# --- [ سيرفر وهمي لإبقاء البوت حياً ] ---
def run_dummy_server():
    server = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()
# ----------------------------------------

# قاعدة البيانات المؤقتة للأزرار
DATA_BUTTONS = [{"text": "🌐 موقع جوجل (افتراضى)", "url": "https://www.google.com"}]

# خطوات الأدمن
admin_steps = {
    "waiting_for_name": False,
    "waiting_for_url": False,
    "temp_name": ""
}

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

# دالة مفرقة لسطور قصيرة لتفادي مشاكل النسخ في الهاتف
def check_admin_action(message):
    if message.chat.id != ADMIN_ID:
        return False
    # هنا تم تقسيم السطر لحمايته من التقطع
    is_waiting = admin_steps["waiting_for_name"] or admin_steps["waiting_for_url"]
    return is_waiting

@bot.message_handler(func=check_admin_action)
def handle_admin_inputs(message):
    if admin_steps["waiting_for_name"]:
        admin_steps["temp_name"] = message.text
        admin_steps["waiting_for_name"] = False
        admin_steps["waiting_for_url"] = True
        bot.send_message(message.chat.id, "🔗 الخطوة 2: ابعثلي الرابط المختصر:")
    elif admin_steps["waiting_for_url"]:
        DATA_BUTTONS.append({"text": admin_steps["temp_name"], "url": message.text})
        admin_steps["waiting_for_url"] = False
        bot.send_message(message.chat.id, f"✅ تم حفظ الزر بنجاح خويّا!")

print("البوت جاهز ومحصن!")
bot.infinity_polling()
