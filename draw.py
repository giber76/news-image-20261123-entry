#!/usr/bin/env python3
"""draw.py — news-image-20261123 v4.

Paints "THE WORLD IN ONE DAY — Monday 23 November 2026": 35 stories,
7 regions. Layout follows the reference front page Giber sent: thin top
strip, huge title, red date line, headline ticker, THE DAY IN NUMBERS,
coloured region bar, THE DAY IN UTC timeline, 3 large illustrated
features, 12 small illustrated cards (3 x 4), a WHERE IT HAPPENED map
beside an ALSO - IN BRIEF list, a red DATE CHECK box, and a footer.

Run:  python3 draw.py entry.png
Checks: 1024x1024, <=256 KiB, 0 truncations, byte-identical renders.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# --- palette -------------------------------------------------------------
PAPER   = (245, 240, 230)
INK     = (17, 17, 17)
RED     = (179, 39, 30)
DARKRED = (140, 25, 20)
BLUE    = (31, 78, 121)
TEAL    = (13, 148, 136)
ORANGE  = (194, 65, 12)
PURPLE  = (107, 33, 168)
GREEN   = (21, 128, 61)
GREY    = (107, 114, 128)
LIGHT   = (220, 232, 232)
TAN     = (232, 217, 168)
CARD_BG = (250, 247, 240)
RULE    = (90, 90, 90)

REGION_COLORS = {
    "EUROPE":   (37, 99, 235),
    "ASIA-PAC": (13, 148, 136),
    "AMERICAS": (220, 38, 38),
    "AFRICA":   (234, 88, 12),
    "MID EAST": (124, 58, 237),
    "OCEANIA":  (22, 163, 74),
    "WORLD":    (107, 114, 128),
}

# --- fonts ---------------------------------------------------------------
_FONT_CACHE = {}

def _find_font(bold):
    import os
    cands = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for c in cands:
        if os.path.exists(c):
            return c
    return None

def F(size, bold=False):
    key = (size, bold)
    if key not in _FONT_CACHE:
        path = _find_font(bold)
        _FONT_CACHE[key] = ImageFont.truetype(path, size) if path else ImageFont.load_default()
    return _FONT_CACHE[key]

# --- text helpers --------------------------------------------------------
TRUNC = [0]  # truncation counter: any text that does not fit

def tw(text, font):
    return font.getlength(text)

def wrap(text, font, maxw):
    """Greedy word wrap; over-long words are hard-split by characters."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if tw(trial, font) <= maxw:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    # hard-split any line still too wide
    out = []
    for ln in lines:
        while tw(ln, font) > maxw and len(ln) > 1:
            cut = 1
            while cut < len(ln) and tw(ln[:cut + 1], font) <= maxw:
                cut += 1
            out.append(ln[:cut])
            ln = ln[cut:]
        out.append(ln)
    return out

def fit_block(d, x, y, w, text, font, max_lines, line_h, fill, align="left"):
    """Draw wrapped text; count a truncation if it needs more lines."""
    lines = wrap(text, font, w)
    if len(lines) > max_lines:
        TRUNC[0] += 1
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        yy = y + i * line_h
        if align == "center":
            d.text((x + w / 2, yy), ln, font=font, fill=fill, anchor="ma")
        else:
            d.text((x, yy), ln, font=font, fill=fill, anchor="la")
    return len(lines)

def ctext(d, cx, y, s, font, fill):
    d.text((cx, y), s, font=font, fill=fill, anchor="ma")

def ltext(d, x, y, s, font, fill):
    d.text((x, y), s, font=font, fill=fill, anchor="la")

def hline(d, x0, x1, y, fill=INK, width=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)

def vline(d, x, y0, y1, fill=INK, width=1):
    d.line([(x, y0), (x, y1)], fill=fill, width=width)

def box(d, x0, y0, x1, y1, fill=None, outline=None, width=1):
    d.rectangle([x0, y0, x1, y1], fill=fill, outline=outline, width=width)

# --- the day's data ------------------------------------------------------
DATE_LONG = "MONDAY 23 NOVEMBER 2026"
TOP_STRIP = "35 STORIES \u00b7 7 REGIONS \u00b7 ALL FROM MONDAY 23 NOVEMBER 2026"
TICKER = "COP31 COLLAPSES  \u2014  BOY, 7, ALIVE IN DYMER  \u2014  BELGIUM\u2019S SKIES GO DARK"

NUMBERS = [
    ("258", "DEMOCRATS\u2019 HOUSE SEATS,\nMOST SINCE 1992"),
    ("429", "BRUSSELS FLIGHTS AXED\nON MONDAY"),
    ("11", "KILLED IN KYIV REGION\nSTRIKES"),
    ("6.5", "VANUATU QUAKE,\n601 KM DEEP"),
    ("14", "HOURS BOY, 7, SPENT\nIN RUBBLE"),
    ("4\u20130", "LIVERPOOL ROUT\nMAN UTD"),
]

REGIONS = [("EUROPE", 13), ("ASIA-PAC", 9), ("AMERICAS", 4), ("AFRICA", 5),
           ("MID EAST", 2), ("OCEANIA", 1), ("WORLD", 1)]

UTC_PINS = [
    ("02:37", "BOY ALIVE IN DYMER"),
    ("02:40", "VANUATU M6.5 QUAKE"),
    ("04:43", "DEMOCRATS\u2019 258TH SEAT"),
    ("06:00", "BRUSSELS ATC SHUTS"),
    ("10:55", "NO TSUNAMI THREAT"),
    ("20:00", "BRUSSELS ATC BACK"),
]

# 3 large features: num, region, status, headline, fact, sources, scene
FEATURES = [
    dict(num=1, region="WORLD", status="REPORTED",
         headline="COP31 COLLAPSES:\nNO DEAL, NO PACT",
         fact="COP31 ENDS IN FAILURE \u2014 FOSSIL FUELS NEVER MENTIONED; "
              "EU AND ISLAND STATES WALK OUT.",
         sources="AP \u00b7 REUTERS \u00b7 LE MONDE", scene="cop31"),
    dict(num=2, region="EUROPE", status="CONFIRMED",
         headline="BOY, 7, ALIVE\nAFTER 14 HOURS",
         fact="PULLED FROM DYMER RUBBLE AS KYIV REGION TOLL RISES TO 11; "
              "MONDAY IS A DAY OF MOURNING.",
         sources="BBC \u00b7 AL JAZEERA", scene="dymer"),
    dict(num=3, region="EUROPE", status="CONFIRMED",
         headline="BELGIUM\u2019S SKIES\nGO DARK",
         fact="BRUSSELS FLIGHTS AXED 07:00\u201321:00 AS CONTROLLERS JOIN "
              "THE STRIKE: 429 FLIGHTS; 59,500 HIT.",
         sources="BELGA \u00b7 AFP", scene="brussels"),
]

# 12 small cards: num, region, status, headline, sources, scene
CARDS = [
    dict(num=4, region="AMERICAS", status="CONFIRMED",
         headline="DEMOCRATS CLINCH 258 \u2014 BIGGEST HOUSE MAJORITY SINCE 1992",
         sources="AP \u00b7 REUTERS", scene="democrats"),
    dict(num=5, region="OCEANIA", status="REPORTED",
         headline="VANUATU M6.5 QUAKE, 601 KM DEEP \u2014 NO TSUNAMI, NO CASUALTIES",
         sources="USGS", scene="quake"),
    dict(num=6, region="ASIA-PAC", status="REPORTED",
         headline="CIKANDE FIRE: 24 BODY BAGS OUT AS SEARCH FOR DOZENS GOES ON",
         sources="AL JAZEERA", scene="fire"),
    dict(num=7, region="EUROPE", status="CONFIRMED",
         headline="LIVERPOOL 4\u20130 MAN UTD: POCHETTINO DEBUT ENDS IN ROUT",
         sources="REUTERS", scene="football"),
    dict(num=8, region="EUROPE", status="CONFIRMED",
         headline="ALCARAZ BEATS ZVEREV 6\u20132, 7\u20136 FOR FIRST ATP FINALS TITLE",
         sources="AP", scene="tennis"),
    dict(num=9, region="MID EAST", status="CLAIM",
         headline="HOUTHIS CLAIM SAUDI REFINERY HIT AS TRUMP WARNS IRAN",
         sources="AL JAZEERA", scene="missile"),
    dict(num=10, region="AFRICA", status="REPORTED",
         headline="BLAST ON RUSSIAN SHIP AT LIBYA PORT KILLS 10",
         sources="REUTERS", scene="ship"),
    dict(num=11, region="MID EAST", status="REPORTED",
         headline="ISRAEL RAZES HOMES IN SOUTHERN LEBANON",
         sources="AL JAZEERA", scene="houses"),
    dict(num=12, region="ASIA-PAC", status="REPORTED",
         headline="ASIAN STOCKS SLIDE AS AI BUBBLE FEARS MOUNT",
         sources="REUTERS", scene="stocks"),
    dict(num=13, region="EUROPE", status="CONFIRMED",
         headline="NHS LAUNCHES WORLD\u2019S BIGGEST AI BREAST-CANCER TRIAL",
         sources="BBC", scene="nhs"),
    dict(num=14, region="EUROPE", status="REPORTED",
         headline="NATO MEETS OVER POLAND AIRSPACE BREACH; 3 RUSSIAN MISSILES",
         sources="REUTERS \u00b7 AP", scene="nato"),
    dict(num=15, region="ASIA-PAC", status="CONFIRMED",
         headline="NEPAL PM SHAH OPENS INDIA VISIT: ENERGY, LINKS ON TABLE",
         sources="IANS", scene="nepal"),
]

# 20 brief items (numbers 16-35): text, region
BRIEF = [
    ("US INTEL CHIEF DEFENDS TRUMP\u2019S PUTIN LINE", "AMERICAS"),
    ("POLAND: RUSSIA TRIED TO KILL RAPPER TWICE", "EUROPE"),
    ("US ARMY TO DETONATE 4 TONNES OF LEAD AZIDE", "AMERICAS"),
    ("WHO CHIEF PLEADS FOR PEACE IN EBOLA-HIT DR CONGO", "AFRICA"),
    ("LIBYA ARMY \u2018FULLY PREPARED\u2019 AFTER ATTACKS", "AFRICA"),
    ("LISBON: THOUSANDS MARCH OVER COST OF LIVING", "EUROPE"),
    ("FRENCH STUDENTS GEAR UP FOR NATIONWIDE PROTESTS", "EUROPE"),
    ("INDIA, CHINA OPEN 10-DAY LAC BORDER TALKS", "ASIA-PAC"),
    ("YOUTH CONGRESS PROTESTS META OVER BLOCKS", "ASIA-PAC"),
    ("PAOLO BULGARI DIES, AGED 89", "EUROPE"),
    ("CAMEROON EX-REBELS: HIDING OR BROKEN PROMISES", "AFRICA"),
    ("LAGARDE TO QUIT AS ECB CHIEF IN FEB 2027", "EUROPE"),
    ("DELTA SYSTEM GLITCH DELAYS 1,600+ FLIGHTS", "AMERICAS"),
    ("CONGRESS WRITES LETTER IN BLOOD TO HARYANA CM", "ASIA-PAC"),
    ("WEST BENGAL BJP PROTESTS BANGLADESH ATTACKS", "ASIA-PAC"),
    ("INDIA PROSECUTES BISLERI OVER UNSAFE WATER", "ASIA-PAC"),
    ("UK ENERGY BILLS TO SOAR, WARNS REGULATOR", "EUROPE"),
    ("EU, CANADA DEEPEN AI COLLABORATION", "EUROPE"),
    ("SOUTH KOREA EXPORTS TOP $1 TRILLION, A FIRST", "ASIA-PAC"),
    ("NIGERIA BOAT ACCIDENT KILLS 24 MOURNERS", "AFRICA"),
]

DATE_CHECK = (
    "WIRES READ TO 22:00 UTC. EVERY STORY HERE WAS REPORTED ON MONDAY 23 NOVEMBER 2026.  "
    "LEFT OUT ON PURPOSE: HORMUZ TANKERS (STRUCK FRI\u2013SAT 21\u201322 NOV), COP31 DRAFT TEXT "
    "(SUN 22 NOV), RUSSIAN DRONE BARRAGE, LAS VEGAS GP, INDIA 720/9, HONG KONG VOTE, "
    "BOLSONARO (FRI 20 NOV), SHENZHEN SUMMIT (THU 19 NOV), FIFA 2035 HOST DECISION.  "
    "STILL DEVELOPING: OPEC+ MEETS 29 NOV; COP31 FOLLOW-UP TALKS."
)

FOOTER_LEGEND = ("CONFIRMED = NAMED SOURCE REPORTS IT   \u00b7   REPORTED = WIRE-REPORTED, NOT YET "
                 "CONFIRMED   \u00b7   CLAIM = ONE SIDE\u2019S ACCOUNT, CONTESTED")
FOOTER_SOURCES = "SOURCES: BBC \u00b7 REUTERS \u00b7 AP \u00b7 AL JAZEERA \u00b7 CNN \u00b7 LE MONDE \u00b7 WSJ \u00b7 USGS \u00b7 BELGA \u00b7 SCMP"
FOOTER_NOTE = "SCENES ARE DRAWN ILLUSTRATIONS OF REPORTED EVENTS, NOT PHOTOGRAPHS"

# --- scene painters ------------------------------------------------------
# Every scene is drawn with plain PIL shapes on its own rectangle.
# Feature scenes are large (329 x 138); card scenes are thin strips.

def _sunset(d, x0, y0, x1, y1):
    """Orange-to-pink dusk gradient in horizontal bands."""
    bands = [(214, 120, 60), (222, 140, 70), (228, 158, 88),
             (232, 172, 105), (235, 186, 125), (238, 198, 145)]
    h = (y1 - y0) / len(bands)
    for i, col in enumerate(bands):
        d.rectangle([x0, y0 + i * h, x1, y0 + (i + 1) * h + 1], fill=col)

def _globe(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(52, 110, 180),
              outline=(20, 60, 110), width=2)
    # green land blobs
    d.ellipse([cx - r * 0.62, cy - r * 0.55, cx - r * 0.05, cy - r * 0.05],
              fill=(46, 139, 87))
    d.ellipse([cx + r * 0.05, cy + r * 0.10, cx + r * 0.60, cy + r * 0.62],
              fill=(46, 139, 87))
    d.ellipse([cx - r * 0.30, cy + r * 0.35, cx + r * 0.25, cy + r * 0.70],
              fill=(60, 160, 95))
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=(180, 210, 240), width=2)

def _person(d, x, y, s, shirt, pants):
    d.ellipse([x - 3 * s, y - 8 * s, x + 3 * s, y - 2 * s], fill=(222, 184, 150))
    d.rectangle([x - 3 * s, y - 2 * s, x + 3 * s, y + 5 * s], fill=shirt)
    d.rectangle([x - 3 * s, y + 5 * s, x, y + 11 * s], fill=pants)
    d.rectangle([x, y + 5 * s, x + 3 * s, y + 11 * s], fill=pants)

def scene_cop31(d, x0, y0, x1, y1):
    _sunset(d, x0, y0, x1, y1)
    d.ellipse([x1 - 52, y0 + 12, x1 - 22, y0 + 42], fill=(250, 214, 110))  # sun
    _globe(d, (x0 + x1) // 2, y0 + 62, 46)
    # small figures watching the globe
    _person(d, x0 + 26, y1 - 16, 1.0, (30, 60, 140), (20, 20, 20))
    _person(d, x0 + 62, y1 - 16, 1.0, (200, 40, 40), (20, 20, 20))
    _person(d, x1 - 30, y1 - 16, 1.0, (40, 120, 60), (20, 20, 20))
    d.polygon([(x0 + 250, y0 + 52), (x0 + 262, y0 + 34), (x0 + 274, y0 + 52)],
              fill=(40, 40, 40))  # dark shard above the globe

def scene_dymer(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(16, 24, 54))  # night sky
    d.ellipse([x1 - 46, y0 + 10, x1 - 20, y0 + 36], fill=(232, 232, 220))  # moon
    # apartment block, half standing
    bx, bw = x0 + 24, 92
    d.rectangle([bx, y0 + 26, bx + bw, y1 - 26], fill=(74, 74, 88))
    for r in range(4):
        for c in range(4):
            lit = (r + c) % 2 == 0
            col = (250, 214, 110) if lit else (30, 34, 52)
            d.rectangle([bx + 8 + c * 20, y0 + 34 + r * 20,
                         bx + 20 + c * 20, y0 + 48 + r * 20], fill=col)
    # broken half + rubble
    d.polygon([(bx + bw, y0 + 26), (bx + bw + 44, y0 + 60), (bx + bw + 44, y1 - 26),
               (bx + bw, y1 - 26)], fill=(52, 52, 62))
    for i, (rx, ry, rw) in enumerate([(150, 118, 26), (180, 124, 20), (205, 116, 30)]):
        d.polygon([(x0 + rx, y1 - 26), (x0 + rx + rw // 2, y1 - 26 - 14 - i * 3),
                   (x0 + rx + rw, y1 - 26)], fill=(96, 96, 110))
    # searchlight beam from the right
    d.polygon([(x1 - 8, y0 + 40), (x1 - 8, y0 + 62), (x0 + 210, y1 - 26)],
              fill=(250, 240, 190))
    _person(d, x0 + 150, y1 - 30, 1.0, (250, 214, 110), (20, 20, 20))

def scene_brussels(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(158, 203, 232))  # sky
    d.ellipse([x0 + 30, y0 + 16, x0 + 62, y0 + 30], fill=(255, 255, 255))
    d.ellipse([x0 + 52, y0 + 22, x0 + 84, y0 + 36], fill=(255, 255, 255))
    # control tower
    d.rectangle([x0 + 18, y0 + 30, x0 + 30, y1 - 30], fill=(120, 120, 128))
    d.rectangle([x0 + 12, y0 + 18, x0 + 36, y0 + 32], fill=(90, 96, 110))
    for i in range(3):
        d.rectangle([x0 + 15 + i * 7, y0 + 21, x0 + 20 + i * 7, y0 + 29],
                    fill=(170, 220, 240))
    # runway
    d.rectangle([x0, y1 - 30, x1, y1], fill=(60, 60, 66))
    for i in range(9):
        d.rectangle([x0 + 12 + i * 36, y1 - 17, x0 + 30 + i * 36, y1 - 13],
                    fill=(240, 240, 240))
    # airplane silhouette
    px, py = x0 + 150, y0 + 78
    d.ellipse([px - 70, py - 10, px + 70, py + 10], fill=(255, 255, 255))
    d.polygon([(px + 30, py - 8), (px + 78, py - 30), (px + 66, py - 2)],
              fill=(230, 230, 230))
    d.polygon([(px - 10, py + 6), (px + 30, py + 26), (px + 44, py + 6)],
              fill=(230, 230, 230))
    for i in range(6):
        d.rectangle([px - 52 + i * 16, py - 5, px - 46 + i * 16, py + 1],
                    fill=(120, 160, 200))
    # red X sign: airport closed
    d.ellipse([x1 - 46, y0 + 12, x1 - 14, y0 + 44], fill=(200, 30, 30))
    d.line([x1 - 39, y0 + 19, x1 - 21, y0 + 37], fill=(255, 255, 255), width=4)
    d.line([x1 - 21, y0 + 19, x1 - 39, y0 + 37], fill=(255, 255, 255), width=4)

def paint_feature(d, key, x0, y0, x1, y1):
    {"cop31": scene_cop31, "dymer": scene_dymer,
     "brussels": scene_brussels}[key](d, x0, y0, x1, y1)

# --- small card scenes (thin strips) ------------------------------------
def _strip(d, x0, y0, x1, y1, sky, ground=None):
    d.rectangle([x0, y0, x1, y1], fill=sky)
    if ground:
        d.rectangle([x0, y1 - 7, x1, y1], fill=ground)

def scene_democrats(d, x0, y0, x1, y1):
    _strip(d, x0, y0, x1, y1, (31, 78, 121))
    for i in range(7):
        d.rectangle([x0, y0 + 3 + i * 3, x1, y0 + 4 + i * 3],
                    fill=(255, 255, 255) if i % 2 == 0 else (200, 40, 40))
    for r in range(2):
        for c in range(5):
            d.ellipse([x0 + 8 + c * 12, y0 + 4 + r * 9, x0 + 13 + c * 12, y0 + 9 + r * 9],
                      fill=(255, 255, 255))

def scene_quake(d, x0, y0, x1, y1):
    _strip(d, x0, y0, x1, y1, (70, 130, 180), (30, 90, 60))
    pts = []
    for i in range(13):
        xx = x0 + i * ((x1 - x0) // 12)
        yy = y0 + 12 + (6 if i % 2 == 0 else -5)
        pts.append((xx, yy))
    d.line(pts, fill=(255, 220, 60), width=2)
    d.ellipse([x1 - 34, y0 + 4, x1 - 12, y0 + 18], fill=(250, 214, 110))

def scene_fire(d, x0, y0, x1, y1):
    _strip(d, x0, y0, x1, y1, (60, 30, 20), (40, 40, 44))
    for i, (fx, fh) in enumerate([(40, 16), (90, 22), (150, 18), (220, 24), (280, 16)]):
        d.polygon([(x0 + fx, y1 - 7), (x0 + fx + 12, y1 - 7 - fh),
                   (x0 + fx + 24, y1 - 7)], fill=(240, 120, 20) if i % 2 == 0 else (250, 200, 40))
    d.rectangle([x0 + 20, y1 - 14, x0 + 60, y1 - 7], fill=(90, 90, 96))

def scene_football(d, x0, y0, x1, y1):
    _strip(d, x0, y0, x1, y1, (34, 139, 34))
    d.line([(x0, y1 - 10), (x1, y1 - 10)], fill=(255, 255, 255), width=1)
    d.ellipse([(x0 + x1) // 2 - 30, y0 + 4, (x0 + x1) // 2 + 30, y0 + 20],
              outline=(255, 255, 255), width=1)
    d.ellipse([x0 + 250, y0 + 5, x0 + 262, y0 + 17], fill=(255, 255, 255))
    d.ellipse([x0 + 60, y0 + 6, x0 + 70, y0 + 16], fill=(255, 255, 255))

def scene_tennis(d, x0, y0, x1, y1):
    _strip(d, x0, y0, x1, y1, (46, 125, 70))
    d.line([(x0, y1 - 8), (x1, y1 - 8)], fill=(255, 255, 255), width=1)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1 - 8)], fill=(255, 255, 255), width=1)
    d.ellipse([x0 + 240, y0 + 4, x0 + 258, y0 + 18], fill=(220, 240, 60))

def scene_missile(d, x0, y0, x1, y1):
    _strip(d, x0, y0, x1, y1, (24, 28, 52), (60, 40, 30))
    d.arc([x0 + 60, y0 - 26, x0 + 260, y0 + 30], 300, 60, fill=(250, 200, 60), width=2)
    d.ellipse([x1 - 40, y0 + 2, x1 - 20, y0 + 16], fill=(250, 120, 40))
    d.polygon([(x0 + 250, y0 + 6), (x0 + 262, y0 + 2), (x0 + 258, y0 + 14)],
              fill=(220, 220, 220))

def scene_ship(d, x0, y0, x1, y1):
    _strip(d, x0, y0, x1, y1, (120, 170, 210), (30, 80, 140))
    d.rectangle([x0 + 110, y0 + 8, x0 + 220, y0 + 18], fill=(90, 90, 96))
    d.rectangle([x0 + 150, y0 + 2, x0 + 160, y0 + 8], fill=(70, 70, 76))
    d.ellipse([x0 + 225, y0 + 1, x0 + 245, y0 + 15], fill=(250, 160, 40))
    d.ellipse([x0 + 232, y0 + 5, x0 + 240, y0 + 12], fill=(250, 220, 80))

def scene_houses(d, x0, y0, x1, y1):
    _strip(d, x0, y0, x1, y1, (210, 190, 150), (150, 120, 80))
    for i, hx in enumerate([30, 110, 190, 260]):
        d.rectangle([x0 + hx, y0 + 8, x0 + hx + 44, y1 - 7], fill=(190, 150, 100))
        d.polygon([(x0 + hx - 4, y0 + 8), (x0 + hx + 22, y0 - 2),
                   (x0 + hx + 48, y0 + 8)], fill=(160, 60, 40))
    d.ellipse([x0 + 290, y0 + 2, x0 + 306, y0 + 14], fill=(230, 220, 200))

def scene_stocks(d, x0, y0, x1, y1):
    _strip(d, x0, y0, x1, y1, (250, 247, 240))
    pts = [(x0 + 10, y0 + 6), (x0 + 90, y0 + 8), (x0 + 150, y0 + 4),
           (x0 + 210, y0 + 12), (x0 + 280, y0 + 20)]
    d.line(pts, fill=(200, 30, 30), width=2)
    d.polygon([(x0 + 280, y0 + 20), (x0 + 268, y0 + 14), (x0 + 292, y0 + 14)],
              fill=(200, 30, 30))

def scene_nhs(d, x0, y0, x1, y1):
    _strip(d, x0, y0, x1, y1, (240, 244, 248))
    cx = (x0 + x1) // 2
    d.rectangle([cx - 5, y0 + 3, cx + 5, y0 + 19], fill=(200, 30, 30))
    d.rectangle([cx - 12, y0 + 8, cx + 12, y0 + 14], fill=(200, 30, 30))
    d.ellipse([x0 + 30, y0 + 5, x0 + 48, y0 + 17], fill=(220, 120, 160))
    d.ellipse([x1 - 48, y0 + 5, x1 - 30, y0 + 17], fill=(120, 180, 220))

def scene_nato(d, x0, y0, x1, y1):
    _strip(d, x0, y0, x1, y1, (16, 32, 80))
    cx, cy = (x0 + x1) // 2, y0 + 12
    for i in range(8):
        import math
        a = i * math.pi / 4
        sx, sy = cx + int(22 * math.cos(a)), cy + int(7 * math.sin(a))
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 255, 255))
    d.polygon([(x0 + 40, y0 + 4), (x0 + 70, y0 + 8), (x0 + 40, y0 + 12)],
              fill=(220, 60, 60))

def scene_nepal(d, x0, y0, x1, y1):
    _strip(d, x0, y0, x1, y1, (170, 205, 235), (120, 150, 90))
    d.polygon([(x0 + 30, y1 - 7), (x0 + 90, y0 + 2), (x0 + 150, y1 - 7)],
              fill=(120, 130, 140))
    d.polygon([(x0 + 70, y0 + 8), (x0 + 90, y0 + 2), (x0 + 110, y0 + 8)],
              fill=(255, 255, 255))
    d.polygon([(x0 + 160, y1 - 7), (x0 + 220, y0 + 6), (x0 + 280, y1 - 7)],
              fill=(90, 110, 120))
    d.rectangle([x1 - 40, y0 + 3, x1 - 12, y0 + 15], fill=(220, 60, 60))
    d.rectangle([x1 - 40, y0 + 3, x1 - 26, y0 + 15], fill=(30, 60, 160))

CARD_SCENES = {
    "democrats": scene_democrats, "quake": scene_quake, "fire": scene_fire,
    "football": scene_football, "tennis": scene_tennis, "missile": scene_missile,
    "ship": scene_ship, "houses": scene_houses, "stocks": scene_stocks,
    "nhs": scene_nhs, "nato": scene_nato, "nepal": scene_nepal,
}

def paint_card(d, key, x0, y0, x1, y1):
    CARD_SCENES[key](d, x0, y0, x1, y1)

# --- world map -----------------------------------------------------------
# Rough equirectangular continents; lon/lat -> x/y inside the map box.
# Pins are numbered to match the story numbers.

def _lonlat(lon, lat, x0, y0, x1, y1):
    fx = (lon + 170.0) / 360.0
    fy = (72.0 - lat) / 150.0
    return (x0 + fx * (x1 - x0), y0 + fy * (y1 - y0))

CONTINENTS = {
    "north_america": [(-168, 66), (-140, 70), (-120, 71), (-95, 69), (-80, 73),
                      (-60, 62), (-55, 47), (-70, 42), (-75, 35), (-80, 26),
                      (-84, 30), (-90, 21), (-97, 16), (-105, 20), (-115, 29),
                      (-125, 40), (-125, 49), (-135, 58), (-155, 58), (-165, 60)],
    "south_america": [(-78, 7), (-72, 11), (-60, 9), (-52, 5), (-44, -3),
                      (-35, -8), (-40, -20), (-48, -28), (-58, -35), (-65, -41),
                      (-70, -52), (-73, -44), (-73, -30), (-70, -18), (-77, -12),
                      (-80, -4)],
    "europe": [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57),
               (10, 59), (18, 56), (21, 55), (24, 58), (28, 71), (32, 70),
               (40, 68), (44, 66), (40, 60), (36, 54), (30, 46), (28, 44),
               (23, 40), (19, 42), (12, 44), (8, 44), (3, 42), (-2, 37)],
    "africa": [(-6, 35), (10, 37), (20, 32), (30, 31), (35, 28), (43, 12),
               (51, 11), (48, 0), (41, -10), (40, -20), (33, -26), (26, -34),
               (18, -35), (14, -22), (12, -10), (9, 4), (-8, 5), (-16, 12),
               (-17, 21), (-16, 28)],
    "asia": [(44, 66), (60, 69), (80, 73), (100, 76), (120, 73), (140, 72),
             (160, 69), (178, 65), (170, 60), (158, 52), (142, 45), (140, 39),
             (130, 35), (122, 30), (120, 22), (110, 20), (105, 9), (100, 8),
             (97, 16), (92, 21), (89, 22), (80, 13), (77, 8), (73, 20),
             (66, 25), (60, 25), (54, 26), (50, 30), (48, 30), (44, 39),
             (40, 45), (44, 55), (44, 60)],
    "australia": [(114, -22), (114, -30), (115, -35), (124, -33), (130, -32),
                  (136, -35), (140, -38), (146, -39), (150, -37), (153, -27),
                  (146, -19), (142, -11), (136, -12), (130, -13), (126, -14),
                  (122, -17), (114, -22)],
}

# (story number, lon, lat)
PINS = [
    (1, 30.7, 36.9),    # COP31, Antalya
    (2, 30.3, 51.0),    # Dymer, Kyiv region
    (3, 4.4, 50.8),     # Brussels
    (4, -77.0, 38.9),   # Washington DC
    (5, 167.0, -16.0),  # Vanuatu
    (6, 106.2, -6.1),   # Cikande, Banten
    (7, -2.9, 53.4),    # Liverpool
    (8, 7.7, 45.1),     # Turin (ATP Finals)
    (9, 46.7, 24.7),    # Riyadh
    (10, 13.2, 32.9),   # Libya port
    (11, 35.5, 33.3),   # southern Lebanon
    (12, 139.7, 35.7),  # Tokyo (Asian stocks)
    (13, -0.1, 51.5),   # London (NHS)
    (14, 20.0, 52.0),   # Poland
    (15, 77.2, 28.6),   # Delhi (Nepal PM visit)
]

def paint_map(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=LIGHT)
    for poly in CONTINENTS.values():
        pts = [_lonlat(lon, lat, x0, y0, x1, y1) for lon, lat in poly]
        d.polygon(pts, fill=TAN, outline=(180, 165, 120))
    # graticule dots
    for gx in range(x0 + 20, x1, 24):
        for gy in range(y0 + 12, y1, 24):
            d.point((gx, gy), fill=(200, 210, 210))
    # numbered pins
    for num, lon, lat in PINS:
        px, py = _lonlat(lon, lat, x0, y0, x1, y1)
        r = 7
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline=(255, 255, 255), width=1)
        f = F(8, bold=True)
        twd = f.getlength(str(num))
        d.text((px - twd / 2, py - 6), str(num), font=f, fill=(255, 255, 255))

# --- layout: header ------------------------------------------------------
MX = 10  # side margin

def draw_header(d):
    # thin black top strip
    d.rectangle([0, 0, W, 20], fill=INK)
    ctext(d, W // 2, 4, TOP_STRIP, F(11, bold=True), (255, 255, 255))
    # huge title
    ctext(d, W // 2, 24, "THE WORLD IN ONE DAY", F(46, bold=True), INK)
    # red date line
    ctext(d, W // 2, 74, DATE_LONG, F(20, bold=True), RED)
    # headline ticker between rules
    hline(d, MX, W - MX, 98, fill=INK, width=1)
    ctext(d, W // 2, 101, TICKER, F(12, bold=True), RED)
    hline(d, MX, W - MX, 116, fill=INK, width=1)

def draw_numbers(d, y0=120, y1=172):
    ltext(d, MX, y0, "THE DAY IN NUMBERS", F(10, bold=True), RED)
    cell_w = (W - 2 * MX) / 6.0
    top = y0 + 14
    for i, (val, cap) in enumerate(NUMBERS):
        cx = MX + cell_w * i
        ctext(d, cx + cell_w / 2, top, val, F(30, bold=True), INK)
        fit_block(d, int(cx + 4), top + 32, int(cell_w - 8), cap,
                  F(9, bold=True), 2, 10, INK, align="center")
        if i:
            vline(d, int(cx), top + 2, y1 - 4, fill=RULE, width=1)
    hline(d, MX, W - MX, y1, fill=INK, width=1)

def draw_region_bar(d, y0=173, y1=193):
    total = sum(c for _, c in REGIONS)
    x = MX
    avail = W - 2 * MX
    for name, count in REGIONS:
        w = avail * count / total
        col = REGION_COLORS[name]
        d.rectangle([x, y0, x + w - 1, y1], fill=col)
        label = "%s %d" % (name, count)
        if w >= 64:
            ctext(d, x + w / 2, y0 + 4, label, F(10, bold=True), (255, 255, 255))
        x += w
    # full count string under the bar, centred
    counts = "  \u00b7  ".join("%s %d" % (n, c) for n, c in REGIONS)
    ctext(d, W // 2, y1 + 2, counts, F(9, bold=True), INK)

def draw_utc(d, y0=210, y1=232):
    ltext(d, MX, y0, "THE DAY IN UTC", F(10, bold=True), RED)
    # time scale: 00:00 at x=90, 24:00 at x=W-MX
    x_start, x_end = 90, W - MX
    def tx(hour_min):
        hh, mm = hour_min.split(":")
        frac = (int(hh) * 60 + int(mm)) / 1440.0
        return x_start + frac * (x_end - x_start)
    axis_y = y1 - 6
    hline(d, x_start, x_end, axis_y, fill=INK, width=2)
    # labels alternate above / below; shift right to avoid collisions
    # (02:37 and 02:40 sit 3 minutes apart, so their dots nearly coincide)
    last_right = {True: MX + 100, False: MX}
    for i, (t, label) in enumerate(UTC_PINS):
        px = tx(t)
        d.ellipse([px - 3, axis_y - 3, px + 3, axis_y + 3], fill=RED)
        above = (i % 2 == 0)
        f = F(9, bold=True)
        text = t + "  " + label
        lw = f.getlength(text)
        lx = px - lw / 2
        lx = max(lx, last_right[above] + 4)
        lx = min(lx, W - MX - lw)
        ly = y0 + 2 if above else axis_y + 5
        # leader from dot to label
        tx0 = lx + lw / 2
        d.line([(px, axis_y - 3 if above else axis_y + 3),
                (tx0, ly + 9 if above else ly)], fill=RED, width=1)
        ltext(d, lx, ly, text, f, RED if above else INK)
        last_right[above] = lx + lw
    hline(d, MX, W - MX, y1 + 12, fill=INK, width=1)

# --- layout: stories -----------------------------------------------------
COL_X = [10, 347, 684]
COL_W = 329

def _tag(d, x, y, num, region, status, small=False):
    """Number box + region + status chip."""
    f = F(8, bold=True) if small else F(9, bold=True)
    bh = 10 if small else 12
    bw = 14 if small else 16
    # number box
    d.rectangle([x, y, x + bw, y + bh], fill=INK)
    nw = f.getlength(str(num))
    d.text((x + bw / 2 - nw / 2, y + 1), str(num), font=f, fill=(255, 255, 255))
    tx = x + bw + 4
    ltext(d, tx, y + 1, region, f, REGION_COLORS[region])
    sx = tx + f.getlength(region) + 6
    chip = {"CONFIRMED": (21, 128, 61), "REPORTED": (107, 114, 128),
            "CLAIM": (194, 65, 12)}[status]
    d.rectangle([sx, y, sx + f.getlength(status) + 8, y + bh], fill=chip)
    ltext(d, sx + 4, y + 1, status, f, (255, 255, 255))
    return sx + f.getlength(status) + 8

def draw_features(d, y0=266):
    scene_h = 138
    for i, feat in enumerate(FEATURES):
        x = COL_X[i]
        box(d, x, y0, x + COL_W, y0 + 238, outline=INK, width=1)
        paint_feature(d, feat["scene"], x + 1, y0 + 1, x + COL_W - 1, y0 + scene_h)
        ty = y0 + scene_h + 4
        _tag(d, x + 4, ty, feat["num"], feat["region"], feat["status"])
        hy = ty + 16
        fit_block(d, x + 4, hy, COL_W - 8, feat["headline"],
                  F(17, bold=True), 2, 20, INK)
        fy = hy + 42
        fit_block(d, x + 4, fy, COL_W - 8, feat["fact"], F(9), 2, 11, INK)
        ltext(d, x + 4, fy + 24, feat["sources"], F(8), GREY)

def draw_cards(d, y0=508):
    row_h = 56
    for r in range(4):
        for c in range(3):
            card = CARDS[r * 3 + c]
            x = COL_X[c]
            y = y0 + r * row_h
            box(d, x, y, x + COL_W, y + row_h, fill=CARD_BG, outline=INK, width=1)
            paint_card(d, card["scene"], x + 1, y + 1, x + COL_W - 1, y + 19)
            hy = y + 21
            fit_block(d, x + 4, hy, COL_W - 8, card["headline"],
                      F(11, bold=True), 2, 11, INK)
            ty = y + 44
            _tag(d, x + 4, ty, card["num"], card["region"], card["status"],
                 small=True)
            sw = F(8).getlength(card["sources"])
            ltext(d, x + COL_W - 4 - sw, ty + 1, card["sources"], F(8), GREY)

def draw_map_also(d, y0=736):
    ltext(d, MX, y0, "WHERE IT HAPPENED", F(10, bold=True), RED)
    ltext(d, 350, y0, "ALSO \u2014 IN BRIEF", F(10, bold=True), RED)
    map_y0, map_y1 = y0 + 16, 926
    box(d, MX, map_y0, 340, map_y1, outline=INK, width=1)
    paint_map(d, MX + 1, map_y0 + 1, 339, map_y1 - 1)
    # two columns of 10 brief items
    f_num = F(9, bold=True)
    f_txt = F(9)
    for col in range(2):
        cx = 350 + col * 340
        for i in range(10):
            idx = col * 10 + i
            text, region = BRIEF[idx]
            num = 16 + idx
            iy = map_y0 + i * 17
            ltext(d, cx, iy, "%d." % num, f_num, RED)
            fit_block(d, cx + 24, iy, 340 - 24, text, f_txt, 1, 11, INK)

def draw_date_check(d, y0=932, y1=986):
    box(d, MX, y0, W - MX, y1, outline=RED, width=2)
    ltext(d, MX + 6, y0 + 3, "DATE CHECK", F(10, bold=True), RED)
    fit_block(d, MX + 6, y0 + 17, W - 2 * MX - 12, DATE_CHECK,
              F(9), 3, 11, INK)

def draw_footer(d, y0=992):
    ctext(d, W // 2, y0, FOOTER_LEGEND, F(8), INK)
    ctext(d, W // 2, y0 + 11, FOOTER_SOURCES, F(8), INK)
    ctext(d, W // 2, y0 + 22, FOOTER_NOTE, F(8, bold=True), GREY)

# --- main ----------------------------------------------------------------
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_header(d)
    draw_numbers(d, 120, 186)
    draw_region_bar(d, 187, 207)
    draw_utc(d, 224, 250)
    draw_features(d, 266)
    draw_cards(d, 508)
    draw_map_also(d, 736)
    draw_date_check(d, 932, 986)
    draw_footer(d, 992)
    return img

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = render()
    img.save(out, "PNG")
    import hashlib, os
    data = open(out, "rb").read()
    print("stories: 35 (3 features + 12 cards + 20 brief)")
    print("size: %d bytes" % len(data))
    print("sha256: %s" % hashlib.sha256(data).hexdigest())
    print("truncations: %d" % TRUNC[0])
    print("dimensions: %dx%d" % img.size)

if __name__ == "__main__":
    main()
