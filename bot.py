import telebot
import requests

BOT_TOKEN = "8620748653:AAEQGJIEArQhgmAuB3vxr2plvzxmc4gbRx0"
CHANNEL_USERNAME = "@MySuperGames"
SHORTENER_API_KEY = "2a3196651631ce423da1e16ee8c3237cda64f70f"

bot = telebot.TeleBot(BOT_TOKEN)

GAMES_DATABASE = {
    "minecraft": "https://www.mediafire.com/file/example/minecraft.apk",
    "gta": "https://www.mediafire.com/file/example/gta.zip"
}

def shorten_link(long_url):
    try:
        api_url = f"https://api.gplinks.com/api?api={SHORTENER_API_KEY}&url={long_url}"
        response = requests.get(api_url).json()
        if response.get("status") == "success":
            return response.get("shortenedUrl")
        return long_url
    except:
        return long_url

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك! أرسل لي اسم اللعبة التي تبحث عنها.")

@bot.message_handler(func=lambda message: True)
def get_game(message):
    game_name = message.text.lower().strip()
    if game_name in GAMES_DATABASE:
        long_url = GAMES_DATABASE[game_name]
        short_url = shorten_link(long_url)
        bot.reply_to(message, f"🎮 اللعبة: {game_name}\n\n📥 رابط التحميل:\n{short_url}")
    else:
        bot.reply_to(message, "❌ عذراً، هذه اللعبة غير متوفرة حالياً.")

bot.infinity_polling()
