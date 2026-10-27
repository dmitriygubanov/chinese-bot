import random

name = "Место"
icon = "🧭"

entries = [
    # ─── Стороны света (теперь строго с 边 bian, нейтральный тон) ───
    {"hanzi": "北边",  "pinyin": "běibian",   "ru": "север"},
    {"hanzi": "南边",  "pinyin": "nánbian",   "ru": "юг"},
    {"hanzi": "东边",  "pinyin": "dōngbian",  "ru": "восток"},
    {"hanzi": "西边",  "pinyin": "xībian",    "ru": "запад"},
    {"hanzi": "西北",  "pinyin": "xīběibian",     "ru": "северо-запад"},
    {"hanzi": "东北",  "pinyin": "dōngběibian",   "ru": "северо-восток"},
    {"hanzi": "西南",  "pinyin": "xīnánbian",     "ru": "юго-запад"},
    {"hanzi": "东南",  "pinyin": "dōngnánbian",   "ru": "юго-восток"},

    # ─── Предлоги места и положения (строго 边 bian, кроме duimian) ───
    {"hanzi": "里边",  "pinyin": "lǐbian",    "ru": "внутри (в)"},
    {"hanzi": "上边",  "pinyin": "shàngbian", "ru": "на (над, сверху)"},
    {"hanzi": "下边",  "pinyin": "xiàbian",   "ru": "под (внизу)"},
    {"hanzi": "左边",  "pinyin": "zuǒbian",   "ru": "слева"},
    {"hanzi": "右边",  "pinyin": "yòubian",   "ru": "справа"},
    {"hanzi": "旁边",  "pinyin": "pángbiān",  "ru": "рядом, около"}, # Закон! 1-й тон.
    {"hanzi": "外边",  "pinyin": "wàibian",   "ru": "снаружи (вне)"},
    {"hanzi": "前边",  "pinyin": "qiánbian",  "ru": "перед (спереди)"},
    {"hanzi": "后边",  "pinyin": "hòubian",   "ru": "за (позади)"},
    {"hanzi": "对面",  "pinyin": "duìmiàn",   "ru": "напротив"},     # Закон! 4-й тон.
    {"hanzi": "中间",  "pinyin": "zhōngjiān", "ru": "посередине, между"},
]

def generate():
    e = random.choice(entries)
    front = e["ru"]
    back = f"{e['hanzi']} — {e['pinyin']}"
    return front, back
