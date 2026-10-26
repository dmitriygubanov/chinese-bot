import random

name = "Аудитория"
icon = "🎓"

entries = [
    {"hanzi": "铅笔", "pinyin": "qiānbǐ",  "mw_hz": "支", "mw_py": "zhī", "hint": "тонкий", "ru1": "карандаш", "ru234": "карандаша", "ru5p": "карандашей"},
    {"hanzi": "圆珠笔", "pinyin": "yuán zhū bǐ", "mw_hz": "支", "mw_py": "zhī", "hint": "тонкий", "ru1": "ручка", "ru234": "ручки", "ru5p": "ручек"},
    {"hanzi": "橡皮", "pinyin": "xiàngpí", "mw_hz": "块", "mw_py": "kuài", "hint": "плоский", "ru1": "ластик", "ru234": "ластика", "ru5p": "ластиков"},
    {"hanzi": "尺子", "pinyin": "chǐzi",   "mw_hz": "把", "mw_py": "bǎ", "hint": "с ручкой", "ru1": "линейка", "ru234": "линейки", "ru5p": "линеек"},
    {"hanzi": "书",   "pinyin": "shū",     "mw_hz": "本", "mw_py": "běn", "hint": "книга", "ru1": "книга", "ru234": "книги", "ru5p": "книг"},
    {"hanzi": "本子", "pinyin": "běnzi",   "mw_hz": "本", "mw_py": "běn", "hint": "книга", "ru1": "тетрадь", "ru234": "тетради", "ru5p": "тетрадей"},
    {"hanzi": "课本", "pinyin": "kèběn",   "mw_hz": "本", "mw_py": "běn", "hint": "книга", "ru1": "учебник", "ru234": "учебника", "ru5p": "учебников"},
    {"hanzi": "词典", "pinyin": "cídiǎn",  "mw_hz": "本", "mw_py": "běn", "hint": "книга", "ru1": "словарь", "ru234": "словаря", "ru5p": "словарей"},
    {"hanzi": "书包", "pinyin": "shūbāo",  "mw_hz": "个", "mw_py": "gè", "hint": "универс.", "ru1": "рюкзак", "ru234": "рюкзака", "ru5p": "рюкзаков"},
    {"hanzi": "桌子", "pinyin": "zhuōzi",  "mw_hz": "张", "mw_py": "zhāng", "hint": "плоская поверхность", "ru1": "стол", "ru234": "стола", "ru5p": "столов"},
    {"hanzi": "椅子", "pinyin": "yǐzi",    "mw_hz": "把", "mw_py": "bǎ", "hint": "с ручкой", "ru1": "стул", "ru234": "стула", "ru5p": "стульев"},
    {"hanzi": "窗户", "pinyin": "chuānghu","mw_hz": "扇", "mw_py": "shàn", "hint": "окно/дверь", "ru1": "окно", "ru234": "окна", "ru5p": "окон"},
    {"hanzi": "门",   "pinyin": "mén",     "mw_hz": "扇", "mw_py": "shàn", "hint": "окно/дверь", "ru1": "дверь", "ru234": "двери", "ru5p": "дверей"},
    {"hanzi": "黑板", "pinyin": "hēibǎn",  "mw_hz": "块", "mw_py": "kuài", "hint": "плоский", "ru1": "доска", "ru234": "доски", "ru5p": "досок"},
    {"hanzi": "电脑", "pinyin": "diànnǎo", "mw_hz": "台", "mw_py": "tái", "hint": "техника", "ru1": "компьютер", "ru234": "компьютера", "ru5p": "компьютеров"},
    {"hanzi": "手机", "pinyin": "shǒujī",  "mw_hz": "部", "mw_py": "bù", "hint": "устройство", "ru1": "телефон", "ru234": "телефона", "ru5p": "телефонов"},
]

_NUMS = {
    1:  ("一", "yī"), 2:  ("两", "liǎng"), 3:  ("三", "sān"), 4:  ("四", "sì"), 5:  ("五", "wǔ"),
    6:  ("六", "liù"), 7:  ("七", "qī"), 8:  ("八", "bā"), 9:  ("九", "jiǔ"), 10: ("十", "shí"),
}

_TONE_MARKS = {
    "ā": 1, "á": 2, "ǎ": 3, "à": 4, "ē": 1, "é": 2, "ě": 3, "è": 4,
    "ī": 1, "í": 2, "ǐ": 3, "ì": 4, "ō": 1, "ó": 2, "ǒ": 3, "ò": 4,
    "ū": 1, "ú": 2, "ǔ": 3, "ù": 4, "ǖ": 1, "ǘ": 2, "ǚ": 3, "ǜ": 4,
}

def _first_tone(pinyin):
    for ch in pinyin:
        if ch in _TONE_MARKS:
            return _TONE_MARKS[ch]
    return 0

def _number_pinyin(n, mw_py):
    if n == 1:
        return "yí" if _first_tone(mw_py) == 4 else "yì"
    return _NUMS[n][1]

def _ru_form(entry, n):
    if n == 1: return entry["ru1"]
    if 2 <= n <= 4: return entry["ru234"]
    return entry["ru5p"]

def generate():
    e = random.choice(entries)
    n = random.randint(1, 10)

    num_hz = _NUMS[n][0]
    num_py = _number_pinyin(n, e["mw_py"])

    # Вот здесь мы добавляем подсказку в скобках прямо в вопрос!
    front = f"{n} {_ru_form(e, n)} ({e['hint']})"
    
    back  = (f"{num_hz}{e['mw_hz']}{e['hanzi']} — "
             f"{num_py} {e['mw_py']} {e['pinyin']}")
    return front, back
