"""Мапінг тексту (напр. «Хмельницьке регіональне управління») → область Bitrix."""

# Bitrix UF_CRM_1688969951
UKRAINE_OBLASTS = (
    (382, "Київська область"),
    (384, "Дніпропетровська область"),
    (388, "Чернігівська область"),
    (386, "Одеська область"),
    (390, "Харківська область"),
    (392, "Житомирська область"),
    (396, "Херсонська область"),
    (394, "Полтавська область"),
    (398, "Запорізька область"),
    (400, "Луганська область"),
    (402, "Донецька область"),
    (404, "Вінницька область"),
    (406, "Миколаївська область"),
    (408, "Кіровоградська область"),
    (410, "Сумська область"),
    (412, "Львівська область"),
    (414, "Черкаська область"),
    (418, "Волинська область"),
    (416, "Хмельницька область"),
    (420, "Рівненська область"),
    (422, "Івано-Франківська область"),
    (426, "Закарпатська область"),
    (424, "Тернопільська область"),
    (428, "Чернівецька область"),
)


def _oblast_stem(oblast_name: str) -> str:
    """«Львівська область» → «львівськ» (спільний корінь для -а/-е)."""
    stem = oblast_name.casefold().removesuffix(" область").strip()
    if stem.endswith(("а", "е", "і")):
        stem = stem[:-1]
    return stem


def resolve_ukraine_oblast(text: str):
    """
    Шукає область у довільному тексті за коренем назви.

    Returns:
        (назва_області, bitrix_id) або (None, None)
    """
    if not text or not str(text).strip():
        return None, None

    normalized = str(text).casefold()
    matches = []

    for oblast_id, oblast_name in UKRAINE_OBLASTS:
        stem = _oblast_stem(oblast_name)
        if stem and stem in normalized:
            matches.append((len(stem), oblast_name, oblast_id))

    if not matches:
        return None, None

    matches.sort(key=lambda item: item[0], reverse=True)
    _, name, oblast_id = matches[0]
    return name, oblast_id
