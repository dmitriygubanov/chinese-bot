import os
import random
import telebot
from telebot import types
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from topics import TOPICS, draw

# --- ХИТРЫЙ САЙТ-ЗАГЛУШКА ДЛЯ RENDER ---
# Render требует, чтобы это был "Web Service" на порту. 
# Поэтому мы поднимаем крошечный сервер, который просто отвечает "Бот работает".
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Bot is running!')

def run_dummy_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()
# ---------------------------------------

# Токен будет подтягиваться из настроек Render (мы добавим его позже)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
# Сюда впиши свой ID (и через запятую ID друзей, если захочешь)
ALLOWED_USERS = [770984633] 

bot = telebot.TeleBot(BOT_TOKEN)
user_cards = {}

def send_word(chat_id, user_id):
    if user_id not in ALLOWED_USERS:
        bot.send_message(chat_id, "Извини, это приватный бот для учёбы.")
        return

    # Выбираем случайный модуль
    keys = list(TOPICS.keys())
    key = random.choice(keys)
    label, front, back = draw(key)
    
    user_cards[chat_id] = (label, front, back)
    
    markup = types.InlineKeyboardMarkup()
    btn_answer = types.InlineKeyboardButton("Показать ответ", callback_data="answer")
    markup.add(btn_answer)
    
    bot.send_message(chat_id, f"{label}: {front}", reply_markup=markup)

@bot.message_handler(commands=['start', 'next'])
def handle_start(message):
    send_word(message.chat.id, message.from_user.id)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if chat_id not in user_cards:
        bot.answer_callback_query(call.id, "Нажми /next для нового слова")
        return
    
    label, front, back = user_cards[chat_id]
    
    if call.data == "answer":
        # Показываем первую часть (иероглифы)
        step1 = back.split(" — ")[0] if " — " in back else back
        markup = types.InlineKeyboardMarkup()
        if " — " in back:
            btn_pinyin = types.InlineKeyboardButton("Показать пиньинь", callback_data="pinyin")
            markup.add(btn_pinyin)
        else:
            btn_next = types.InlineKeyboardButton("Следующее слово", callback_data="next")
            markup.add(btn_next)
        bot.edit_message_text(f"{label}: {front}\n\n→ {step1}", chat_id, call.message.message_id, reply_markup=markup)
    
    elif call.data == "pinyin":
        # Показываем вторую часть (пиньинь)
        step2 = back.split(" — ")[1]
        markup = types.InlineKeyboardMarkup()
        btn_next = types.InlineKeyboardButton("Следующее слово", callback_data="next")
        markup.add(btn_next)
        bot.edit_message_text(f"{label}: {front}\n\n→ {step2}", chat_id, call.message.message_id, reply_markup=markup)
    
    elif call.data == "next":
        send_word(chat_id, call.from_user.id)

print("Бот запущен...")
bot.infinity_polling()
