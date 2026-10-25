import os
import random
import telebot
from telebot import types
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import time
import requests
from topics import TOPICS, draw

# --- ХИТРЫЙ САЙТ-ЗАГЛУШКА ДЛЯ RENDER ---
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

# --- САМОПИНГ (ЗАЩИТА ОТ СНА) ---
def ping_self():
    # Render сам подставляет этот URL, когда запускает сервис
    url = os.environ.get('RENDER_EXTERNAL_URL') 
    if not url:
        return
    while True:
        time.sleep(840) # Ждем 14 минут (840 секунд)
        try:
            requests.get(url)
        except Exception:
            pass

threading.Thread(target=ping_self, daemon=True).start()
# ---------------------------------------

BOT_TOKEN = os.environ.get('BOT_TOKEN')

# ВПИШИ СЮДА ID ПРЕПОДАВАТЕЛЯ, КОГДА УЗНАЕШЬ (через запятую)
ALLOWED_USERS = [
    770984633, 
    # 123456789, <-- сюда добавишь ID преподавателя
]

bot = telebot.TeleBot(BOT_TOKEN)
user_cards = {}
last_messages = {} # Для очистки чата

def send_word(chat_id, user_id):
    if user_id not in ALLOWED_USERS:
        bot.send_message(chat_id, "Извини, это приватный бот для учёбы.")
        return

    # Удаляем предыдущее сообщение бота (очистка чата)
    if chat_id in last_messages:
        try:
            bot.delete_message(chat_id, last_messages[chat_id])
        except:
            pass

    # Выбираем случайный модуль
    keys = list(TOPICS.keys())
    key = random.choice(keys)
    label, front, back = draw(key)
    
    user_cards[chat_id] = (label, front, back)
    
    markup = types.InlineKeyboardMarkup()
    btn_answer = types.InlineKeyboardButton("Показать ответ", callback_data="answer")
    markup.add(btn_answer)
    
    msg = bot.send_message(chat_id, f"{label}: {front}", reply_markup=markup)
    last_messages[chat_id] = msg.message_id

@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    if message.from_user.id not in ALLOWED_USERS:
        bot.send_message(message.chat.id, "Извини, это приватный бот для учёбы.")
        return
    
    text = (
        "Привет! Я бот-тренажёр для китайского языка 🇨🇳\n\n"
        "Нажми /next (или напиши 'следующее'), чтобы получить новое слово.\n"
        "Я буду показывать вопрос. Когда вспомнишь ответ — нажми кнопку под сообщением, "
        "чтобы проверить иероглифы, а затем пиньинь."
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['next'])
def handle_next_command(message):
    send_word(message.chat.id, message.from_user.id)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    # Если пользователь просто пишет что-то (например, "давай еще"), даем новое слово
    send_word(message.chat.id, message.from_user.id)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if chat_id not in user_cards:
        bot.answer_callback_query(call.id, "Нажми /next для нового слова")
        return
    
    label, front, back = user_cards[chat_id]
    
    if call.data == "answer":
        step1 = back.split(" — ")[0] if " — " in back else back
        markup = types.InlineKeyboardMarkup()
        if " — " in back:
            btn_pinyin = types.InlineKeyboardButton("Показать пиньинь", callback_data="pinyin")
            markup.add(btn_pinyin)
        else:
            btn_next = types.InlineKeyboardButton("Следующее слово", callback_data="next")
            markup.add(btn_next)
        
        # Редактируем сообщение, не создавая новое
        bot.edit_message_text(f"{label}: {front}\n\n→ {step1}", chat_id, call.message.message_id, reply_markup=markup)
    
    elif call.data == "pinyin":
        step2 = back.split(" — ")[1]
        markup = types.InlineKeyboardMarkup()
        btn_next = types.InlineKeyboardButton("Следующее слово", callback_data="next")
        markup.add(btn_next)
        bot.edit_message_text(f"{label}: {front}\n\n→ {step2}", chat_id, call.message.message_id, reply_markup=markup)
    
    elif call.data == "next":
        # Удаляем это сообщение и шлем новое
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        send_word(chat_id, call.from_user.id)

print("Бот запущен...")
bot.infinity_polling()
