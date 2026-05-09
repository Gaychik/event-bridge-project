"""PDF ticket generator using ReportLab (replacement for pdfme-based implementation).

Generates VIP and regular tickets and writes them to ./tickets/<random>.pdf
"""
import os
import random
import string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color
from reportlab.pdfbase import ttfonts, pdfmetrics
import qrgen


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
    return ''.join(CYRILLIC_MAP.get(c, c) for c in (text or ''))


def register_cyrillic_font():
    """Try to find and register a TTF font that supports Cyrillic.

    Returns the registered font name or None if not found.
    """
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            name = os.path.splitext(os.path.basename(p))[0]
            try:
                pdfmetrics.registerFont(ttfonts.TTFont(name, p))
                return name
            except Exception:
                continue
    return None


def contains_cyrillic(text: str) -> bool:
    if not text:
        return False
    for ch in text:
        o = ord(ch)
        if (0x0400 <= o <= 0x052F) or (0x2DE0 <= o <= 0x2DFF) or (0xA640 <= o <= 0xA69F):
            return True
    return False


def _maybe_trans(text: str, font_main: str | None) -> str:
    """Return text unchanged if a native Cyrillic-capable font is registered,
    otherwise return a transliterated (Latin) fallback.
    """
    if font_main:
        return text
    return transliterate(text)


def randomize_doc_name():
    rn = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f"{rn}.pdf"


def _draw_vip(c: canvas.Canvas, width: float, height: float, name: str, email: str, event: str, date: str, seat: str | None, font_main: str | None = None, font_mono: str | None = None):
    
    
    margin = 36
    gold = Color(0.85, 0.65, 0.15)
    bg_dark = Color(0.05, 0.05, 0.08)

    c.setFillColor(bg_dark)
    c.rect(0, 0, width, height, stroke=0, fill=1)

    # Border
    c.setLineWidth(3)
    c.setStrokeColor(gold)
    c.roundRect(margin / 2, margin / 2, width - margin, height - margin, 12, stroke=1, fill=0)

    mid_x = width / 2
    y = height - margin - 20

    c.setFillColor(gold)
    if font_main:
        c.setFont(font_main, 32)
    else:
        c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(mid_x, y, event)
    y -= 42

    if font_main:
        c.setFont(font_main, 14)
    else:
        c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(mid_x, y, _maybe_trans("VIP ДОСТУП", font_main))
    y -= 30

    if font_main:
        c.setFont(font_main, 12)
    else:
        c.setFont("Helvetica-Bold", 12)
    c.setFillColor(Color(0.95, 0.95, 0.95))
    label = _maybe_trans("Имя:", font_main)
    c.drawString(margin + 18, y, f"{label} {name}")
    y -= 22
    if font_main:
        c.setFont(font_main, 10)
    else:
        c.setFont("Helvetica", 10)
    c.setFillColor(Color(0.75, 0.75, 0.85))
    label = _maybe_trans("Эл. почта:", font_main)
    c.drawString(margin + 18, y, f"{label} {email}")
    y -= 18
    if font_main:
        c.setFont(font_main, 11)
    else:
        c.setFont("Helvetica-Bold", 11)
    c.setFillColor(gold)
    label = _maybe_trans("Место / Уровень:", font_main)
    c.drawString(margin + 18, y, f"{label} {seat or _maybe_trans('* VIP Lounge *', font_main)}")
    y -= 20
    if font_main:
        c.setFont(font_main, 11)
    else:
        c.setFont("Helvetica", 11)
    c.setFillColor(Color(0.9, 0.9, 1.0))
    label = _maybe_trans("Дата:", font_main)
    c.drawString(margin + 18, y, f"{label} {date}")

    # Features
    low_y = margin + 110
    if font_main:
        c.setFont(font_main, 10)
    else:
        c.setFont("Helvetica-Bold", 10)
    c.setFillColor(gold)
    c.drawCentredString(mid_x, low_y + 60, _maybe_trans("** ШАМПАНСКОЕ БУДЕТ **", font_main))
    if font_main:
        c.setFont(font_main, 9)
    else:
        c.setFont("Helvetica", 9)
    c.setFillColor(Color(0.8, 0.8, 0.8))
    c.drawString(margin + 40, low_y + 40, _maybe_trans("v Приоритетный вход", font_main))
    c.drawString(margin + 40, low_y + 26, _maybe_trans("v Подарочный набор включён", font_main))
    c.drawString(margin + 40, low_y + 12, _maybe_trans("v Встреча и приветствие", font_main))

    # QR placeholder
    if font_mono:
        c.setFont(font_mono, 10)
    else:
        c.setFont("Courier", 10)
    c.setFillColor(gold)
    c.drawCentredString(mid_x, low_y - 6, _maybe_trans("[  VIP QR-КОД  ]", font_mono))
    c.setFont("Helvetica", 9)
    c.setFillColor(Color(0.7, 0.7, 0.8))
    c.drawCentredString(mid_x, low_y - 22, _maybe_trans("ВПУСК ОДНОГО * VIP * ПОЛНЫЙ ДОСТУП", font_main))
    c.setFont("Helvetica", 8)
    c.setFillColor(Color(0.55, 0.55, 0.65))
    c.drawCentredString(mid_x, low_y - 36, _maybe_trans("Предъявите этот пропуск и удостоверение на VIP входе", font_main))

    qr = qrgen.gen_qr_via_endpoint(randomize_doc_name().split('.')[0])
    c.drawImage(qr, width - 120, 40, width=80, height=80, mask='auto')
    

def _draw_regular(c: canvas.Canvas, width: float, height: float, name: str, email: str, event: str, date: str, font_main: str | None = None):
    margin = 36
    accent = Color(0.2, 0.5, 0.9)

    c.setFillColor(Color(0.98, 0.98, 1.0))
    c.rect(0, 0, width, height, stroke=0, fill=1)

    mid_x = width / 2
    y = height - margin - 30

    c.setFillColor(accent)
    if font_main:
        c.setFont(font_main, 26)
    else:
        c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(mid_x, y, event)
    y -= 38

    if font_main:
        c.setFont(font_main, 16)
    else:
        c.setFont("Helvetica-Bold", 16)
    c.setFillColor(Color(0.1, 0.2, 0.4))
    label = _maybe_trans("Держатель билета:", font_main)
    c.drawString(margin + 12, y, f"{label} {name}")
    y -= 22
    if font_main:
        c.setFont(font_main, 11)
    else:
        c.setFont("Helvetica", 11)
    c.setFillColor(Color(0.3, 0.4, 0.6))
    label = _maybe_trans("Эл. почта:", font_main)
    c.drawString(margin + 12, y, f"{label} {email}")
    y -= 26

    if font_main:
        c.setFont(font_main, 12)
    else:
        c.setFont("Helvetica", 12)
    c.setFillColor(accent)
    label = _maybe_trans("Дата:", font_main)
    c.drawString(margin + 12, y, f"{label} {date}")

    # Scan area placeholder
    if font_main:
        c.setFont(font_main, 14)
    else:
        c.setFont("Helvetica-Bold", 14)
    c.setFillColor(Color(0.2, 0.5, 0.8))
    c.drawCentredString(mid_x, margin + 90, "####################")
    if font_main:
        c.setFont(font_main, 9)
    else:
        c.setFont("Helvetica", 9)
    c.setFillColor(Color(0.5, 0.5, 0.6))
    c.drawCentredString(mid_x, margin + 74, _maybe_trans("СКАНИРУЙТЕ ДЛЯ ПРОВЕРКИ", font_main))
    if font_main:
        c.setFont(font_main, 9)
    else:
        c.setFont("Helvetica", 9)
    c.setFillColor(Color(0.4, 0.4, 0.5))
    c.drawCentredString(mid_x, margin + 40, _maybe_trans("Спасибо за покупку!", font_main))

    qr = qrgen.gen_qr_via_endpoint(randomize_doc_name().split('.')[0])
    c.drawImage(qr, width - 120, 40, width=80, height=80, mask='auto')
    


def gen_File(name, email, event_name, date, vip=False, seat=None):
    """Generate a PDF ticket and save it to ./tickets/.

    Returns the path to the generated file.
    """
    file_name = randomize_doc_name()
    os.makedirs("./tickets", exist_ok=True)

    # Try to register a Cyrillic-capable font and choose native vs transliteration
    font_main = register_cyrillic_font()
    font_mono = font_main

    use_native = bool(font_main) and (
        contains_cyrillic(name) or contains_cyrillic(event_name) or contains_cyrillic(email)
    )

    if use_native:
        name_t = name
        event_t = event_name
        email_t = email
    else:
        name_t = transliterate(name)
        event_t = transliterate(event_name)
        email_t = transliterate(email)

    path = os.path.join("./tickets", file_name)

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    if vip:
        _draw_vip(c, width, height, name_t, email_t, event_t, date, seat, font_main=font_main, font_mono=font_mono)
    else:
        _draw_regular(c, width, height, name_t, email_t, event_t, date, font_main=font_main)

    c.showPage()
    c.save()
    return path

