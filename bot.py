import telebot
from pyrogram import Client, filters
import requests
import threading
import re

# ================= الإعدادات =================
# 1. ضع كود الجلسة (Session String) الذي استخرجته من Termux بين علامتي التنصيص
SESSION_STRING = "BAHMGcYAmc-Ocf61iEM_tCPhRSUFecqh2BWPEvI3TmbGUtqu0lCm43zoIfMRCz0_gSbWRM8y016ktNYDQfq4ow00C-gim58P1D5Qwhw7jXzY6yr4UrY062QUR8NDEJfdpQuSpBL9SWC7PW_95_N71eqDnHji0ZtzRxNy0mxmck1xSu-qpcQwntffRo0TrWT8RphYc_ha1YMAlxG1q-edL7q7Rl2iBMpz5fHxNZ_xVMBApTBhbbA0whP2FeWlurLVQwMRVbVsYYRiPpHk69R5jEElVkYt-4NMczwynJEu6rfeD-MJtfTX79Nh2aKRbHqIYLeGnvuKhTU3W-zNCop1_JQrF8_YkAAAAAF8D3v3AA" 

# 2. الآي دي الخاص بقناة قاعدة البيانات الخاصة (يجب أن يبدأ بـ -100)
# (للحصول عليه، قم بتحويل رسالة من قناتك الخاصة إلى بوت @RawDataBot)
DUMP_CHANNEL_ID = -1004315939877 

API_ID = 30153158
API_HASH = "e523e18a3750e020b21e40e76ece826c"
BOT_TOKEN = "8620748653:AAEQGJIEArQhgmAuB3vxr2plvzxmc4gbRx0"
GPLINKS_API_KEY = "2a3196651631ce423da1e16ee8c3237cda64f70f"

# القنوات التي نراقبها (بدون @)
SOURCE_CHANNELS = ["happymod_apks", "traidmod"]
# قناتك العامة للاشتراك الإجباري
PUBLIC_CHANNEL = "@MySuperGames"
# ===============================================

bot = telebot.TeleBot(BOT_TOKEN)
app = Client("my_userbot", session_string=SESSION_STRING, in_memory=True)

# دالة اختصار الروابط
def shorten_url(url):
    try:
        api_url = f"https://gplinks.com/api?api={GPLINKS_API_KEY}&url={url}"
        response = requests.get(api_url).json()
        return response.get('shortenedUrl', url)
    except:
        return url

# دالة التحقق من الاشتراك
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(PUBLIC_CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# ----------------- 1. قسم البوت (خدمة العملاء) -----------------
@bot.message_handler(commands=['start'])
def start(message):
    text = message.text.split()
    if len(text) > 1:
        # استخراج كود اللعبة من الرابط (مثلاً game_123)
        msg_id = text[1].replace("game_", "") 
        
        # التحقق من الاشتراك الإجباري
        if not is_subscribed(message.chat.id):
            bot.reply_to(message, f"⚠️ يجب عليك الاشتراك في القناة أولاً للتحميل:\n{PUBLIC_CHANNEL}\n\nبعد الاشتراك، ارجع للقناة واضغط على الرابط مجدداً.")
            return
        
        try:
  
