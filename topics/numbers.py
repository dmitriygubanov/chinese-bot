import random

name = "Числа"
icon = "🔢"

_DIGITS = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
_UNITS = ["", "十", "百", "千"]
_PN = {
    "零": "líng", "一": "yī",  "二": "èr",  "两": "liǎng",
    "三": "sān",  "四": "sì",  "五": "wǔ",  "六": "liù",
    "七": "qī",   "八": "bā",  "九": "jiǔ",
    "十": "shí",  "百": "bǎi", "千": "qiān", "万": "wàn",
}


def _four_digits(n, leading):
    """1–9999 → иероглифы. leading=True — старшая группа числа."""
    if n == 0:
        return ""
    result = ""
    zero_pending = False
    started = False
    for pos in range(3, -1, -1):          # 千 → 百 → 十 → единицы
        d = (n // (10 ** pos)) % 10
        if d == 0:
            if started:
                zero_pending = True       # запомнили 0 в середине
            continue
        if zero_pending:
            result += "零"                # один 零 на любую пачку нулей
            zero_pending = False
        # 2 перед 百 или 千 разговорно читается как 两, не 二
        digit = "两" if (d == 2 and pos in (2, 3)) else _DIGITS[d]
        # 一十 в самом начале числа сокращается до 十 (10, 19, ...)
        if leading and pos == 1 and d == 1 and not started:
            result += "十"
        else:
            result += digit + _UNITS[pos]
        started = True
    return result


def num_to_hanzi(n):
    if n == 0:
        return "零"
    groups = []
    temp = n
    while temp > 0:
        groups.append(temp % 10000)
        temp //= 10000
    big_units = ["", "万", "亿"]
    result = ""
    for i in range(len(groups) - 1, -1, -1):
        g = groups[i]
        if g == 0:
            continue
        # если между группами «дырка» в сотнях/десятках — нужен 零
        if result and g < 1000 and not result.endswith("零"):
            result += "零"
        if g == 2 and i == 1:             # 20000 → 两万, не 二万
            result += "两万"
        else:
            result += _four_digits(g, leading=(i == len(groups) - 1))
            result += big_units[i]
    return result


def hanzi_to_pinyin(hanzi):
    return " ".join(_PN[c] for c in hanzi)


def generate():
    # Четыре диапазона, выбираются равновероятно
    ranges = [
        (1, 100),         # 1 – 100
        (100, 1000),      # 100 – 1000
        (1000, 10000),    # 1000 – 10000
        (10000, 100000),  # 10000 – 100000
    ]
    lo, hi = random.choice(ranges)
    n = random.randint(lo, hi)
    hanzi = num_to_hanzi(n)
    return str(n), f"{hanzi} — {hanzi_to_pinyin(hanzi)}"