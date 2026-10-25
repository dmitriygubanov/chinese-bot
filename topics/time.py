import random

name = "Время"
icon = "🕐"

# ---- Цифры 1–9 (нужны для сборки чисел) ----
_DIGITS = {
    1: ("一", "yī"),  2: ("二", "èr"),  3: ("三", "sān"),
    4: ("四", "sì"),  5: ("五", "wǔ"),  6: ("六", "liù"),
    7: ("七", "qī"),  8: ("八", "bā"),  9: ("九", "jiǔ"),
}


def _join_pinyin(a, b):
    """Ставит апостроф перед слогом на a/e/o: shí + èr → shí'èr."""
    if b and b[0] in "aeoāáǎàēéěèōóǒò":
        return f"{a}'{b}"
    return a + b


def _num(n):
    """1–59 → (hanzi, pinyin)."""
    if n < 10:
        return _DIGITS[n]
    if n == 10:
        return "十", "shí"
    if n < 20:
        h, p = _DIGITS[n - 10]
        return f"十{h}", _join_pinyin("shí", p)
    tens, ones = divmod(n, 10)
    h_t, p_t = _DIGITS[tens]
    if ones == 0:
        return f"{h_t}十", _join_pinyin(p_t, "shí")
    h_o, p_o = _DIGITS[ones]
    return f"{h_t}十{h_o}", _join_pinyin(_join_pinyin(p_t, "shí"), p_o)


def _period(h):
    """Часть суток по 24-часовому часу."""
    if h < 5:
        return "凌晨", "língchén"     # до рассвета
    if h < 8:
        return "早上", "zǎoshang"     # раннее утро
    if h < 12:
        return "上午", "shàngwǔ"      # первая половина дня
    if h < 13:
        return "中午", "zhōngwǔ"      # около полудня
    if h < 18:
        return "下午", "xiàwǔ"        # после полудня
    return "晚上", "wǎnshang"          # вечер


def _hour12(h):
    """24-часовой час → 12-часовой (0, 13–23 → 12..11)."""
    if h == 0:
        return 12
    if h > 12:
        return h - 12
    return h


def generate():
    h = random.randint(0, 23)
    m = random.randint(0, 59)
    front = f"{h:02d}:{m:02d}"

    p_hz, p_py = _period(h)
    h12 = _hour12(h)
    if h12 == 2:
        h_hz, h_py = "两", "liǎng"     # 两点, не 二点
    else:
        h_hz, h_py = _num(h12)

    if m == 0:
        back = f"{p_hz}{h_hz}点 — {p_py} {h_py} diǎn"
    elif m == 30:
        back = f"{p_hz}{h_hz}点半 — {p_py} {h_py} diǎn bàn"
    elif m < 10:
        m_hz, m_py = _DIGITS[m]
        back = (f"{p_hz}{h_hz}点零{m_hz}分 — "
                f"{p_py} {h_py} diǎn líng {m_py} fēn")
    else:
        m_hz, m_py = _num(m)
        back = (f"{p_hz}{h_hz}点{m_hz}分 — "
                f"{p_py} {h_py} diǎn {m_py} fēn")

    return front, back
