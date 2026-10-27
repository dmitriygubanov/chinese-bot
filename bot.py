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

# --- САМОПИНГ ---
def ping_self():
    url = os.environ.get('RENDER_EXTERNAL_URL') 
    if not url:
        return
    while True:
        time.sleep(840)
        try:
            requests.get(url)
        except Exception:
            pass

threading.Thread(target=ping_self, daemon=True).start()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ALLOWED_USERS = [
    770984633,   # Дмитрий
    2125513598,  # Преподаватель
]

bot = telebot.TeleBot(BOT_TOKEN)
user_cards = {}
user_modes = {} 
anchor_msgs = {}  
content_msgs = {} 
last_card_drawn = {} 

# --- СИСТЕМА ЗАМКОВ (ЗАЩИТА ОТ ГОНОК) ---
chat_locks = {}
def get_lock(chat_id):
    if chat_id not in chat_locks:
        chat_locks[chat_id] = threading.Lock()
    return chat_locks[chat_id]

def get_help_text():
    return (
        "📖 **Как пользоваться:**\n\n"
        "• Получить слово: **/next** (или просто напиши `next`).\n"
        "• Увидеть ответ: жми кнопки **«Показать ответ»** и **«Показать пиньинь»** прямо на карточке.\n"
        "• Сменить тему: кнопка **«⚙️ Выбрать тему»** внизу экрана.\n\n"
        "⚠️ **Внимание:** Не удаляйте сообщение с эмодзи 📖🇨🇳. Оно удерживает кнопки внизу экрана.\n\n"
        "💡 *Примечание:* Если в чате зависла старая карточка — просто свайпни и удали её вручную. Или напиши `/clean`.\n\n"
        "🔹 Команда `/start` перезапускает бота."
    )

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_menu = types.KeyboardButton('⚙️ Выбрать тему')
    btn_help = types.KeyboardButton('ℹ️ Помощь')
    markup.add(btn_menu, btn_help)
    return markup

def get_topics_keyboard(page=0):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if page == 0:
        markup.row(types.InlineKeyboardButton("🎲 Случайная карточка", callback_data="mode_all"))
    
    sorted_keys = sorted(list(TOPICS.keys()))
    items_per_page = 8
    total_pages = (len(sorted_keys) + items_per_page - 1) // items_per_page
    
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    current_keys = sorted_keys[start_idx:end_idx]
    
    buttons = []
    for key in current_keys:
        mod = TOPICS[key]
        icon = getattr(mod, "icon", "")
        name = getattr(mod, "name", key)
        buttons.append(types.InlineKeyboardButton(f"{icon} {name}", callback_data=f"mode_{key}"))
    
    if buttons:
        markup.add(*buttons)
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page-1}"))
    nav_buttons.append(types.InlineKeyboardButton(f"{page+1} / {total_pages}", callback_data="ignore"))
    if page < total_pages - 1:
        nav_buttons.append(types.InlineKeyboardButton("Вперед ➡️", callback_data=f"page_{page+1}"))
        
    markup.row(*nav_buttons)
    return markup

def send_anchor(chat_id):
    if chat_id in anchor_msgs:
        try: bot.delete_message(chat_id, anchor_msgs[chat_id])
        except: pass
    msg = bot.send_message(chat_id, "📖🇨🇳", reply_markup=get_main_keyboard())
    anchor_msgs[chat_id] = msg.message_id

def send_content(chat_id, text, reply_markup=None, parse_mode=None):
    msg = bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode=parse_mode)
    
    if chat_id in content_msgs:
        for old_id in content_msgs[chat_id]:
            try: bot.delete_message(chat_id, old_id)
            except: pass
            
    content_msgs[chat_id] = [msg.message_id]
    return msg

def send_word(chat_id, user_id):
    if user_id not in ALLOWED_USERS:
        return
    
    mode = user_modes.get(user_id, "all")
    
    attempts = 0
    while attempts < 10:
        if mode == "all" or mode not in TOPICS:
            key = random.choice(list(TOPICS.keys()))
        else:
            key = mode
            
        label, front, back = draw(key)
        card_data = (label, front, back)
        
        if chat_id not in last_card_drawn or last_card_drawn[chat_id] != card_data:
            break
        attempts += 1

    last_card_drawn[chat_id] = card_data
    user_cards[chat_id] = card_data
    
    markup = types.InlineKeyboardMarkup()
    btn_answer = types.InlineKeyboardButton("Показать ответ", callback_data="answer")
    markup.add(btn_answer)
    
    send_content(chat_id, f"{label}: {front}", reply_markup=markup)

@bot.message_handler(commands=['start'])
def handle_start(message):
    if message.from_user.id not in ALLOWED_USERS:
        return
    try: bot.delete_message(message.chat.id, message.message_id)
    except: pass
    
    # Блокируем чат, чтобы клики не пролетали мимо
    with get_lock(message.chat.id):
        send_anchor(message.chat.id)
        text = (
            "Привет! Я бот-тренажёр для китайского языка 🇨🇳\n\n"
            + get_help_text() + 
            "\n\n👇 Выбери тему, нажав на кнопку ниже, или напиши 'next' для случайного слова."
        )
        send_content(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['clean'])
def handle_clean(message):
    if message.from_user.id not in ALLOWED_USERS:
        return
    try: bot.delete_message(message.chat.id, message.message_id)
    except: pass
    
    with get_lock(message.chat.id):
        if message.chat.id in content_msgs:
            del content_msgs[message.chat.id]
        if message.chat.id in anchor_msgs:
            try: bot.delete_message(message.chat.id, anchor_msgs[message.chat.id])
            except: pass
            del anchor_msgs[message.chat.id]
            
        bot.send_message(message.chat.id, "🧹 Память бота очищена. Отправляю новый якорь. Напиши /start.")
        send_anchor(message.chat.id)

@bot.message_handler(func=lambda message: message.text == 'ℹ️ Помощь' or message.text == '/help')
def handle_help(message):
    try: bot.delete_message(message.chat.id, message.message_id)
    except: pass
    
    with get_lock(message.chat.id):
        send_content(message.chat.id, get_help_text(), parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == '⚙️ Выбрать тему')
def handle_menu(message):
    try: bot.delete_message(message.chat.id, message.message_id)
    except: pass
    
    with get_lock(message.chat.id):
        text = "Выбери тему для тренировки:\n(листай страницы кнопками внизу)"
        send_content(message.chat.id, text, reply_markup=get_topics_keyboard(page=0))

@bot.callback_query_handler(func=lambda call: call.data.startswith('page_'))
def callback_page(call):
    page = int(call.data.replace('page_', ''))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_topics_keyboard(page=page))
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'ignore')
def callback_ignore(call):
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('mode_'))
def callback_mode(call):
    mode = call.data.replace('mode_', '')
    user_modes[call.from_user.id] = mode
    bot.answer_callback_query(call.id)
    
    # Блокируем чат на время генерации карточки
    with get_lock(call.message.chat.id):
        send_word(call.message.chat.id, call.from_user.id)

@bot.message_handler(commands=['next'])
def handle_next_command(message):
    try: bot.delete_message(message.chat.id, message.message_id)
    except: pass
    with get_lock(message.chat.id):
        send_word(message.chat.id, message.from_user.id)

@bot.message_handler(func=lambda message: message.text.lower() == 'next')
def handle_next_text(message):
    try: bot.delete_message(message.chat.id, message.message_id)
    except: pass
    with get_lock(message.chat.id):
        send_word(message.chat.id, message.from_user.id)

@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    try: bot.delete_message(message.chat.id, message.message_id)
    except: pass
    with get_lock(message.chat.id):
        send_content(message.chat.id, "Я понимаю только команду 'next' или /next. Листай карточки кнопками ниже! 👇")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith('mode_') or call.data.startswith('page_') or call.data == 'ignore':
        return
        
    chat_id = call.message.chat.id
    if chat_id not in user_cards:
        bot.answer_callback_query(call.id, "Напиши /next для нового слова")
        return
    
    bot.answer_callback_query(call.id)
    label, front, back = user_cards[chat_id]
    
    step1 = back.split(" — ")[0] if " — " in back else back
    step2 = back.split(" — ")[1] if " — " in back else ""

    # Блокируем, чтобы ответы и следующее слово не конфликтовали
    with get_lock(chat_id):
        if call.data == "answer":
            markup = types.InlineKeyboardMarkup()
            if step2:
                btn_pinyin = types.InlineKeyboardButton("Показать пиньинь", callback_data="pinyin")
                markup.add(btn_pinyin)
            else:
                btn_next = types.InlineKeyboardButton("Следующее слово", callback_data="next")
                markup.add(btn_next)
            
            bot.edit_message_text(f"{label}: {front}\n\n  {step1}", chat_id, call.message.message_id, reply_markup=markup)
        
        elif call.data == "pinyin":
            markup = types.InlineKeyboardMarkup()
            btn_next = types.InlineKeyboardButton("Следующее слово", callback_data="next")
            markup.add(btn_next)
            
            bot.edit_message_text(f"{label}: {front}\n\n  {step1}\n  {step2}", chat_id, call.message.message_id, reply_markup=markup)
        
        elif call.data == "next":
            send_word(chat_id, call.from_user.id)

print("Бот запущен...")
bot.infinity_polling()
