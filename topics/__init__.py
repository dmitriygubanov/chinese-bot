import importlib
import pkgutil
import random

TOPICS = {}

for info in pkgutil.iter_modules(__path__):
    mod = importlib.import_module(f"{__name__}.{info.name}")
    if hasattr(mod, "name"):
        TOPICS[info.name] = mod


def draw(key):
    """Возвращает (label, front, back) для одного топика."""
    mod = TOPICS[key]
    label = f"{getattr(mod, 'icon', '')} {mod.name}".strip()

    if hasattr(mod, "generate"):
        front, back = mod.generate()
    else:
        e = random.choice(mod.entries)
        front = e["hanzi"]
        back = f"{e['ru']} — {e['pinyin']}"

    return label, front, back
