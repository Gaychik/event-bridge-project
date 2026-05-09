from pdfme import build_pdf

# Cyrillic to Latin transliteration map
CYRILLIC_MAP = {
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
    'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
    'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
    'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}


def transliterate(text):
    return ''.join(CYRILLIC_MAP.get(c, c) for c in text)


def randomize_doc_name():
    import random
    import string

    random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f'{random_name}.pdf'


def gen_File(name, email, event_name, date, vip=False, seat=None):
    file_name = randomize_doc_name()

    name = transliterate(name)
    event_name = transliterate(event_name)
    email = transliterate(email)

    if vip:
        content = [
            # Decorative top line
            {".": "*", "style": {"s": 24, "c": [0.85, 0.65, 0.15], "align": "center", "margin_top": 10}},
            {".": f"{event_name}", "style": {"s": 32, "b": True, "c": [0.9, 0.7, 0.2], "align": "center", "margin_top": 5, "font": "helvetica"}},
            {".": "VIP ACCESS", "style": {"s": 14, "b": True, "c": [0.85, 0.65, 0.15], "align": "center", "margin_top": 4, "char_space": 2}},

            # Gold separator line
            {".": "* ---- * ---- *", "style": {"s": 10, "c": [0.85, 0.65, 0.15], "align": "center", "margin_top": 8}},

            # Main info box
            {".": "PASS DETAILS", "style": {"s": 11, "b": True, "c": [0.7, 0.7, 0.7], "margin_top": 12, "letter_spacing": 3}},
            {".": f"> Name: {name}", "style": {"s": 15, "b": True, "c": [0.95, 0.95, 0.95], "margin_top": 8, "margin_left": 15}},
            {".": f"> Email: {email}", "style": {"s": 11, "c": [0.75, 0.75, 0.85], "margin_top": 6, "margin_left": 15}},
            {".": f"> Seat / Level: {seat or '* VIP Lounge *'}", "style": {"s": 13, "b": True, "c": [0.85, 0.65, 0.15], "margin_top": 8, "margin_left": 15}},
            {".": f"> Date: {date}", "style": {"s": 13, "c": [0.9, 0.9, 1.0], "margin_top": 8, "margin_left": 15}},

            # Visual separator
            {".": "* * * * *", "style": {"s": 9, "c": [0.85, 0.65, 0.15], "align": "center", "margin_top": 15}},

            # Extra info block
            {".": "** CHAMPAGNE RECEPTION **", "style": {"s": 10, "b": True, "c": [0.85, 0.65, 0.15], "align": "center", "margin_top": 8}},
            {".": "v Priority entrance", "style": {"s": 10, "c": [0.8, 0.8, 0.8], "margin_left": 20, "margin_top": 5}},
            {".": "v Gift bag included", "style": {"s": 10, "c": [0.8, 0.8, 0.8], "margin_left": 20, "margin_top": 3}},
            {".": "v Meet & greet access", "style": {"s": 10, "c": [0.8, 0.8, 0.8], "margin_left": 20, "margin_top": 3}},

            # Bottom placeholder QR code
            {".": "[  V I P   Q R   C O D E  ]", "style": {"s": 10, "align": "center", "c": [0.85, 0.65, 0.15], "margin_top": 15, "font": "courier"}},
            {".": "ADMIT ONE * VIP * ALL ACCESS", "style": {"s": 9, "align": "center", "c": [0.7, 0.7, 0.8], "margin_top": 8}},
            {".": "Present this pass + valid ID at VIP entrance", "style": {"s": 8, "align": "center", "c": [0.55, 0.55, 0.65], "margin_top": 5}},
        ]

        # VIP page style with dark theme and gold accents
        page_style = {
            "page_size": "a4",
            "margin": [35, 40, 35, 40],
            "background_color": [0.05, 0.05, 0.08],
            "border": {"width": 2, "c": [0.85, 0.65, 0.15], "radius": 12},
            "padding": 15
        }

    else:
        content = [
            # Gradient header
            {".": "[TICKET]", "style": {"s": 28, "align": "center", "margin_top": 15}},
            {".": f"{event_name}", "style": {"s": 26, "b": True, "c": [0.2, 0.5, 0.9], "align": "center", "margin_top": 5}},

            # Decorative wave
            {".": "~~~~~~~~~~~~~~~~", "style": {"s": 11, "c": [0.3, 0.6, 0.95], "align": "center", "margin_top": 8}},

            # Info card (simulated white background)
            {".": "+----------------------+", "style": {"s": 11, "c": [0.9, 0.9, 0.95], "margin_top": 15, "align": "center"}},
            {".": "|  TICKET HOLDER        |", "style": {"s": 10, "b": True, "c": [0.2, 0.4, 0.7], "margin_left": 35, "margin_top": 5}},
            {".": f"|  * {name}", "style": {"s": 15, "b": True, "c": [0.1, 0.2, 0.4], "margin_left": 35, "margin_top": 3}},
            {".": f"|  @ {email}", "style": {"s": 11, "c": [0.3, 0.4, 0.6], "margin_left": 35, "margin_top": 6}},
            {".": "+----------------------+", "style": {"s": 11, "c": [0.9, 0.9, 0.95], "margin_left": 35, "margin_top": 8}},
            {".": f"|  Date: {date}", "style": {"s": 12, "c": [0.2, 0.5, 0.8], "margin_left": 35, "margin_top": 5}},
            {".": "+----------------------+", "style": {"s": 11, "c": [0.9, 0.9, 0.95], "margin_left": 35, "margin_top": 3}},

            # Barcode placeholder
            {".": "####################", "style": {"s": 16, "c": [0.2, 0.5, 0.8], "align": "center", "margin_top": 20}},
            {".": "SCAN TO VALIDATE", "style": {"s": 7, "c": [0.5, 0.5, 0.6], "align": "center", "margin_top": 3}},

            {".": "Thank you for your purchase!", "style": {"s": 9, "c": [0.4, 0.4, 0.5], "align": "center", "margin_top": 15}},
        ]

        page_style = {
            "page_size": "a4",
            "margin": [45, 45, 45, 45],
            "background_gradient": {"start": [0.98, 0.98, 1.0], "end": [0.92, 0.95, 1.0]},
            "border": {"width": 1, "c": [0.2, 0.5, 0.9], "radius": 15, "dash": [4, 2]},
            "shadow": {"offset": 3, "opacity": 0.1}
        }

    document = {
        "page_style": page_style,
        "style": {"s": 12, "f": "Helvetica"},
        "sections": [{"content": content}],
    }

    with open("./tickets/" + file_name, 'wb') as f:
        build_pdf(document, f)
