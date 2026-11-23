#!/usr/bin/env python3
"""Draw the Monday 23 November 2026 world-news front page (1024x1024).

Dense broadsheet: masthead, stat strip, 4 lead cards with drawn art,
10 feature cards, a dotted world map with 12 numbered pins, a 30-item
ALSO list, and a sources footer. 44 stories in all, every one verified
against live reporting; see STORIES.md for the source and day-tag of
each one. All pictures are original, drawn here in code with Pillow
primitives. Deterministic: no network, no clock, no random.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
CREAM = (246, 241, 227)
PAPER = (252, 248, 238)
INK = (26, 26, 26)
SOFT = (90, 84, 72)
RED = (185, 28, 28)
BLUE = (35, 80, 120)
TEAL = (28, 90, 96)
GOLD = (176, 132, 30)
RULE = (180, 172, 152)
DARK = (32, 38, 48)
DARKRED = (90, 24, 24)
DARKTEAL = (18, 52, 58)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def F(size, bold=False, serif=True):
    name = ("DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf") if serif \
        else ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, font, fill=INK, leading=None):
    if leading is None:
        leading = font.size + 3
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- stories
# (number, region, status, kicker, headline, deck, art)
LEADS = [
    (1, "Europe", "CONFIRMED", "ANTALYA  ·  CLIMATE",
     "COP31 collapses with no deal",
     "The EU rejects a final text that never mentions fossil "
     "fuels. The longest summit ever ends in failure.", "cop"),
    (2, "Middle East", "REPORTED", "GULF  ·  WAR",
     "Iran war widens across the Gulf",
     "Iran-linked strikes hit a Bahrain site, wounding two; Houthi "
     "missiles aimed at Riyadh are stopped.", "strait"),
    (3, "World", "CONFIRMED", "MARKETS  ·  ROUT",
     "Stocks suffer worst week since April 2025",
     "S&P 500 \u22128.6%, Nasdaq \u221210% and VIX 35.89. Nvidia falls 23% "
     "despite record $115.8bn revenue.", "chart"),
    (4, "Americas", "CONFIRMED", "MEXICO  ·  CARTELS",
     "Mexico captures \u2018El Chapo Isidro\u2019",
     "FBI most-wanted boss Fausto Isidro Meza Flores seized in "
     "Guasave. Eleven die in the gun battle.", "cuffs"),
]

FEATURES = [
    (5, "Asia-Pacific", "REPORTED", "INDONESIA  ·  DISASTER",
     "Candy factory fire: dozens missing",
     "Three dead, about 50 missing after a Banten candy-plant blaze.",
     "flame"),
    (6, "Europe", "REPORTED", "UKRAINE  ·  WAR",
     "14 missing after drone hits Kyiv block",
     "A Russian drone hits a Dymer block; nine are evacuated.",
     "drone"),
    (7, "Asia-Pacific", "CONFIRMED", "INDIA  ·  DIPLOMACY",
     "Nepal\u2019s PM meets Modi in Delhi",
     "Balendra Shah\u2019s state visit puts trade and ties at the top.",
     "flags"),
    (8, "Oceania", "CONFIRMED", "CRICKET  ·  TEST",
     "India\u2019s record 720/9d in Wellington",
     "NZ 157/4 on day five, still 195 behind India\u2019s 720/9d.",
     "bat"),
    (9, "Asia-Pacific", "CONFIRMED", "SOUTH KOREA  ·  EDUCATION",
     "Minister quits over AI exam scandal",
     "Minister quits after rule changes to stop AI exam cheating.",
     "cap"),
    (10, "Europe", "CONFIRMED", "PORTUGAL  ·  PROTEST",
     "Thousands march in Lisbon rain",
     "Workers demand higher pay and cheaper housing.", "umbrella"),
    (11, "Europe", "REPORTED", "POLAND  ·  WAR",
     "Three Russian missiles entered Poland",
     "Prosecutors say they crossed in on Friday.", "missile"),
    (12, "Americas", "CONFIRMED", "AI  ·  IPO",
     "Anthropic: $81.3bn, the biggest IPO ever",
     "$83 a share, a $1.5tn valuation; $26bn more privately.",
     "rocket"),
    (13, "Asia-Pacific", "CONFIRMED", "NORTH KOREA  ·  SECURITY",
     "Kim: security, not supremacy",
     "Kim says the North seeks security, not dominance.", "star"),
    (14, "Africa", "CONFIRMED", "SUDAN  ·  CONFLICT",
     "24 killed in fresh South Sudan violence",
     "Drone strikes hit homes and a UN building in Khartoum.",
     "pin"),
]

# (number, bold lead, rest) — ALSO items, stories 15-44
ALSO = [
    (15, "Bolsonaro \u2018stable\u2019 in intensive care",
     "Brazil\u2019s ex-leader stays in hospital."),
    (16, "35 Fulanis killed in revenge attacks",
     "Kano, Nigeria."),
    (17, "WHO chief pleads for peace",
     "in the Ebola-hit DR Congo area."),
    (18, "Netanyahu\u2013Eisenkot talks fail",
     "no deal on a government."),
    (19, "Albanese: COP31 failure",
     "a sign of \u2018difficult times\u2019."),
    (20, "Myanmar\u2019s army-backed government",
     "calls the ASEAN decision \u2018unfair\u2019."),
    (21, "UN states agree to keep talking",
     "on lethal AI weapons."),
    (22, "Pakistan A beat India A by 48 runs",
     "in the Asia Cup Rising Stars."),
    (23, "Liverpool 4\u20130 Man Utd",
     "Pochettino\u2019s debut is a rout. (Sun)"),
    (24, "Alcaraz beats Zverev 6\u20132, 7\u20136",
     "for a first ATP Finals title. (Sun)"),
    (25, "Barcelona fight back from 2\u20130 down",
     "to sink Villarreal."),
    (26, "Leeds stun Chelsea 4\u20131",
     "Fulham hold Man City 1\u20131."),
    (27, "NFL: Eagles stun Steelers",
     "Cowboys score 51."),
    (28, "Mets land Skubal for a record $450m",
     "nine years, pending a physical. (Sun)"),
    (29, "Thitikul wins CME Tour Championship",
     "for a third year in a row."),
    (30, "Gerwyn Price wins Grand Slam",
     "ending a four-year wait for a major."),
    (31, "25 dead in fire on cargo ship",
     "the vessel was under repair in China."),
    (32, "Blast at Basra power facility kills 4",
     "35 injured, Iraq."),
    (33, "Nvidia chip row: Alice Huang",
     "diverting AI chips to China."),
    (34, "Bitcoin rebounds 11%",
     "to $61,034."),
    (35, "Tech giants form the AAIF",
     "to set standards for 100bn AI agents."),
    (36, "Amit Shah\u2019s \u20b94,000-crore push",
     "in Arunachal Pradesh."),
    (37, "BJP MP Ramrao Wadkute dies",
     "of cardiac arrest in Delhi."),
    (38, "Malaysia to work with the UN and OIC",
     "after the ICJ Myanmar ruling."),
    (39, "Australia rebukes US over AUKUS",
     "a congressman threatens SpaceX funds."),
    (40, "Anupama defends world snooker title",
     ""),
    (41, "Student protests sweep Europe",
     "from school funding to climate."),
    (42, "IFFI 2026 hosts BRICS film roundtable",
     ""),
    (43, "India and Bulgaria discuss IMEC",
     "and the Black Sea situation."),
    (44, "FIFA to confirm the UK as host",
     "of the 2035 Women\u2019s World Cup."),
]

STATS = [
    ("\u22128.6%", "S&P 500, THE WEEK"),
    ("\u221210%", "NASDAQ, THE WEEK"),
    ("35.89", "VIX VOLATILITY"),
    ("$92.57", "BRENT CRUDE"),
    ("$3,515", "GOLD, 14-MONTH LOW"),
    ("$81.3BN", "ANTHROPIC IPO"),
]

# (number, lon, lat, label)
PINS = [
    (1, 30.7, 36.9, "Antalya"),
    (2, 50.6, 26.2, "Bahrain"),
    (3, 46.7, 24.7, "Riyadh"),
    (4, -108.5, 25.6, "Guasave"),
    (5, 30.5, 50.5, "Kyiv"),
    (6, 106.3, -6.2, "Cikande"),
    (7, 127.0, 37.5, "Seoul"),
    (8, -9.1, 38.7, "Lisbon"),
    (9, 77.2, 28.6, "New Delhi"),
    (10, 174.8, -41.3, "Wellington"),
    (11, 21.0, 52.2, "Warsaw"),
    (12, -47.9, -15.8, "Bras\u00edlia"),
]

REGIONS = ["Europe", "Middle East", "Americas", "Asia-Pacific",
           "Africa", "Oceania", "World"]


def region_counts():
    counts = {r: 0 for r in REGIONS}
    for s in LEADS + FEATURES:
        counts[s[1]] += 1
    also_regions = {
        15: "Americas", 16: "Africa", 17: "Africa", 18: "Middle East",
        19: "Oceania", 20: "Asia-Pacific", 21: "World",
        22: "Asia-Pacific", 23: "Europe", 24: "Europe", 25: "Europe",
        26: "Europe", 27: "Americas", 28: "Americas", 29: "Americas",
        30: "Europe", 31: "Asia-Pacific", 32: "Middle East",
        33: "Americas", 34: "World", 35: "World", 36: "Asia-Pacific",
        37: "Asia-Pacific", 38: "Asia-Pacific", 39: "Americas",
        40: "Asia-Pacific", 41: "Europe", 42: "Asia-Pacific",
        43: "Asia-Pacific", 44: "Europe",
    }
    for n, r in also_regions.items():
        counts[r] += 1
    return counts

# ---------------------------------------------------------------- art
def draw_icon(d, kind, x, y, w, h, ink, accent):
    """Small pictogram drawn with primitives inside box (x, y, w, h)."""
    cx, cy = x + w / 2, y + h / 2
    if kind == "cop":  # empty chairs + broken globe
        d.ellipse([x + 8, y + 6, x + 34, y + 32], outline=ink, width=2)
        d.arc([x + 8, y + 6, x + 34, y + 32], 200, 340, fill=accent, width=3)
        for bx in (x + 44, x + 66, x + 88):
            d.rectangle([bx, y + 26, bx + 14, y + 30], fill=ink)
            d.rectangle([bx + 2, y + 30, bx + 4, y + 44], fill=ink)
            d.rectangle([bx + 10, y + 30, bx + 12, y + 44], fill=ink)
            d.rectangle([bx, y + 12, bx + 14, y + 26], outline=ink, width=2)
    elif kind == "strait":  # two coasts, ships, missile arcs
        d.polygon([(x + 6, y + 8), (x + 40, y + 8), (x + 30, y + h - 8),
                   (x + 6, y + h - 8)], fill=ink)
        d.polygon([(x + w - 6, y + 8), (x + w - 40, y + 8),
                   (x + w - 30, y + h - 8), (x + w - 6, y + h - 8)],
                  fill=ink)
        d.rectangle([x + 48, y + 30, x + 66, y + 36], fill=accent)
        d.rectangle([x + 56, y + 22, x + 60, y + 30], fill=accent)
        d.arc([x + 70, y + 4, x + 110, y + 30], 180, 360, fill=accent, width=2)
    elif kind == "chart":  # falling line + candles
        pts = [(x + 6, y + 10), (x + 30, y + 16), (x + 52, y + 12),
               (x + 74, y + 30), (x + 96, y + 34), (x + 118, y + 48)]
        d.line(pts, fill=accent, width=3)
        for bx, top, bot in ((x + 14, y + 14, y + 26), (x + 58, y + 18, y + 34),
                             (x + 100, y + 38, y + 52)):
            d.line([bx + 4, top - 5, bx + 4, bot + 5], fill=ink, width=1)
            d.rectangle([bx, top, bx + 8, bot], fill=ink)
    elif kind == "cuffs":  # police light bar + cuffs
        d.rectangle([x + 10, y + 12, x + 44, y + 26], fill=RED)
        d.rectangle([x + 48, y + 12, x + 82, y + 26], fill=BLUE)
        d.ellipse([x + 92, y + 26, x + 116, y + 50], outline=ink, width=3)
        d.ellipse([x + 120, y + 26, x + 144, y + 50], outline=ink, width=3)
        d.line([x + 116, y + 38, x + 120, y + 38], fill=ink, width=3)
    elif kind == "flame":
        d.polygon([(cx - 12, cy + 12), (cx - 14, cy - 2), (cx - 4, cy - 12),
                   (cx + 2, cy - 2), (cx + 12, cy - 8), (cx + 12, cy + 12)],
                  fill=accent)
        d.ellipse([cx - 5, cy + 2, cx + 5, cy + 12], fill=GOLD)
    elif kind == "drone":
        d.ellipse([cx - 14, cy - 4, cx + 14, cy + 4], fill=ink)
        for dx, dy in ((-14, -10), (14, -10), (-14, 10), (14, 10)):
            d.ellipse([cx + dx - 6, cy + dy - 3, cx + dx + 6, cy + dy + 3],
                      outline=ink, width=2)
            d.line([cx, cy, cx + dx, cy + dy], fill=ink, width=2)
    elif kind == "flags":
        d.line([x + 8, y + 4, x + 8, y + h - 4], fill=ink, width=2)
        d.polygon([(x + 8, y + 4), (x + 30, y + 9), (x + 8, y + 14)],
                  fill=accent)
        d.line([x + 38, y + 4, x + 38, y + h - 4], fill=ink, width=2)
        d.polygon([(x + 38, y + 4), (x + 60, y + 9), (x + 38, y + 14)],
                  fill=BLUE)
    elif kind == "bat":
        d.line([x + 12, y + 6, x + 34, y + 28], fill=ink, width=5)
        d.rectangle([x + 32, y + 26, x + 44, y + 30], fill=ink)
        d.ellipse([x + 52, y + 16, x + 64, y + 28], fill=accent)
    elif kind == "cap":
        d.polygon([(cx - 18, cy - 2), (cx, cy - 12), (cx + 18, cy - 2),
                   (cx, cy + 8)], fill=ink)
        d.line([cx + 18, cy - 2, cx + 18, cy + 8], fill=accent, width=2)
        d.ellipse([cx + 15, cy + 6, cx + 21, cy + 12], fill=accent)
    elif kind == "umbrella":
        d.pieslice([cx - 16, cy - 12, cx + 16, cy + 6], 180, 360, fill=accent)
        d.line([cx, cy - 2, cx, cy + 12], fill=ink, width=2)
        d.arc([cx - 4, cy + 8, cx + 4, cy + 16], 0, 180, fill=ink, width=2)
        for dx in (-12, -4, 4, 12):
            d.line([cx + dx, cy + 10, cx + dx, cy + 16], fill=BLUE, width=1)
    elif kind == "missile":
        d.line([x + 8, y + h - 8, x + w - 8, y + 8], fill=ink, width=3)
        d.polygon([(x + w - 22, y + 6), (x + w - 6, y + 6),
                   (x + w - 14, y + 18)], fill=accent)
        d.arc([x + 8, y + 4, x + 34, y + 30], 270, 60, fill=accent, width=2)
    elif kind == "rocket":
        d.polygon([(cx, cy - 14), (cx + 7, cy + 2), (cx + 4, cy + 12),
                   (cx - 4, cy + 12), (cx - 7, cy + 2)], fill=ink)
        d.ellipse([cx - 3, cy - 4, cx + 3, cy + 2], fill=accent)
        d.polygon([(cx - 4, cy + 12), (cx - 8, cy + 18), (cx, cy + 14)],
                  fill=accent)
        d.polygon([(cx + 4, cy + 12), (cx + 8, cy + 18), (cx, cy + 14)],
                  fill=accent)
    elif kind == "star":
        pts = []
        import math
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            r = 14 if i % 2 == 0 else 6
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        d.polygon(pts, fill=accent)
    elif kind == "pin":
        d.ellipse([cx - 8, cy - 12, cx + 8, cy + 4], outline=ink, width=2)
        d.ellipse([cx - 3, cy - 7, cx + 3, cy - 1], fill=accent)
        d.polygon([(cx - 8, cy + 2), (cx + 8, cy + 2), (cx, cy + 14)],
                  fill=ink)


# ---------------------------------------------------------------- map
LAND = [
    # North America
    (-168, -95, 50, 70), (-125, -66, 25, 50), (-97, -80, 15, 30),
    (-92, -77, 7, 15), (-55, -25, 64, 76),
    # South America
    (-80, -35, 5, 12), (-78, -38, -5, 10), (-72, -55, -55, -5),
    # Europe
    (-10, 30, 36, 60), (5, 30, 58, 70), (-5, 2, 50, 58),
    # Africa
    (-17, 35, 15, 35), (-17, 50, -5, 15), (12, 40, -35, -5),
    (35, 51, 0, 12),
    # Asia
    (40, 90, 45, 75), (90, 180, 45, 72), (60, 100, 25, 45),
    (70, 90, 8, 35), (95, 110, 8, 28), (100, 140, 28, 45),
    (127, 142, 31, 45), (43, 60, 25, 40), (35, 48, 36, 42),
    (95, 141, -11, 6),
    # Oceania
    (113, 154, -39, -11), (166, 178, -47, -34),
]


def is_land(lon, lat):
    return any(lo0 <= lon <= lo1 and la0 <= lat <= la1
               for lo0, lo1, la0, la1 in LAND)


def lonlat_to_xy(lon, lat, x0, y0, x1, y1):
    fx = (lon + 170) / 360.0
    fy = (75 - lat) / 135.0
    return x0 + fx * (x1 - x0), y0 + fy * (y1 - y0)

# ---------------------------------------------------------------- layout
M = 22
STATUS_FILL = {"CONFIRMED": (28, 110, 60), "REPORTED": (160, 90, 10),
               "CLAIM": (150, 30, 30)}


def status_tag(d, x, y, status):
    f = F(9, bold=True, serif=False)
    w = d.textlength(status, font=f) + 10
    d.rounded_rectangle([x, y, x + w, y + 14], radius=3,
                        fill=STATUS_FILL[status])
    d.text((x + 5, y + 2), status, font=f, fill=(255, 255, 255))
    return w


def lead_card(d, x, y, w, h, story):
    num, region, status, kicker, headline, deck, art = story
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    d.rectangle([x, y, x + w, y + 58], fill=DARK)
    draw_icon(d, art, x + 8, y + 5, w - 16, 48, (235, 230, 215), RED)
    d.rectangle([x, y + 58, x + w, y + 60], fill=RED)
    ky = y + 66
    kf = F(9, bold=True, serif=False)
    d.text((x + 8, ky), kicker, font=kf, fill=RED)
    status_tag(d, x + w - 78, ky - 1, status)
    hf = F(16, bold=True, serif=True)
    lines = wrap(d, headline, hf, w - 16)
    ty = text_block(d, x + 8, ky + 17, lines[:3], hf, leading=19)
    df = F(11, serif=False)
    dlines = wrap(d, deck, df, w - 16)
    text_block(d, x + 8, ty + 2, dlines[:3], df, fill=SOFT, leading=14)


def feature_card(d, x, y, w, h, story):
    num, region, status, kicker, headline, deck, art = story
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    d.rectangle([x, y, x + w, y + 30], fill=PAPER)
    draw_icon(d, art, x + w - 46, y + 2, 40, 26, INK, RED)
    kf = F(8, bold=True, serif=False)
    d.text((x + 7, y + 4), kicker, font=kf, fill=RED)
    status_tag(d, x + 7, y + 17, status)
    hf = F(12, bold=True, serif=True)
    lines = wrap(d, headline, hf, w - 14)
    ty = text_block(d, x + 7, y + 36, lines[:3], hf, leading=14)
    df = F(10, serif=False)
    dlines = wrap(d, deck, df, w - 14)
    text_block(d, x + 7, ty + 2, dlines[:2], df, fill=SOFT, leading=12)


def draw_map_panel(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    tf = F(12, bold=True, serif=False)
    d.text((x + 10, y + 8), "WHERE IT HAPPENED", font=tf, fill=INK)
    d.line([x + 10, y + 28, x + w - 10, y + 28], fill=RULE, width=1)
    mx0, my0, mx1, my1 = x + 14, y + 36, x + w - 14, y + h - 78
    step = 7
    yy = my0
    while yy <= my1:
        xx = mx0
        while xx <= mx1:
            lon = -170 + (xx - mx0) / (mx1 - mx0) * 360
            lat = 75 - (yy - my0) / (my1 - my0) * 135
            if is_land(lon, lat):
                d.ellipse([xx - 1, yy - 1, xx + 1, yy + 1],
                          fill=(120, 130, 145))
            xx += step
        yy += step
    nf = F(9, bold=True, serif=False)
    for num, lon, lat, label in PINS:
        px, py = lonlat_to_xy(lon, lat, mx0, my0, mx1, my1)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=(255, 255, 255), width=1)
        t = str(num)
        tw = d.textlength(t, font=nf)
        d.text((px - tw / 2, py - 6), t, font=nf, fill=(255, 255, 255))
    counts = region_counts()
    total = sum(counts.values())
    cf = F(10, bold=True, serif=False)
    line1 = "EUROPE 11  \u00b7  MIDDLE EAST 3  \u00b7  AMERICAS 8  \u00b7  " \
            "ASIA-PACIFIC 13"
    tw = d.textlength(line1, font=cf)
    d.text((x + (w - tw) / 2, y + h - 66), line1, font=cf, fill=INK)
    line2 = "AFRICA 3  \u00b7  OCEANIA 2  \u00b7  WORLD 4  \u00b7  44 STORIES"
    tw = d.textlength(line2, font=cf)
    d.text((x + (w - tw) / 2, y + h - 50), line2, font=cf, fill=INK)
    sf = F(10, serif=False)
    sub = "pins mark the 12 places above"
    tw = d.textlength(sub, font=sf)
    d.text((x + (w - tw) / 2, y + h - 34), sub, font=sf, fill=SOFT)
    lf = F(9, serif=False)
    keys = "1 COP31 Antalya   2 Bahrain   3 Riyadh   4 Guasave   5 Kyiv   " \
           "6 Cikande"
    tw = d.textlength(keys, font=lf)
    d.text((x + (w - tw) / 2, y + h - 18), keys, font=lf, fill=SOFT)


def draw_also_panel(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    tf = F(12, bold=True, serif=False)
    d.text((x + 10, y + 8), "ALSO ON MONDAY 23 NOVEMBER", font=tf, fill=INK)
    d.line([x + 10, y + 28, x + w - 10, y + 28], fill=RULE, width=1)
    col_w = (w - 20 - 12) // 2
    bf = F(10, bold=True, serif=False)
    rf = F(10, serif=False)
    row_h = 22
    for i, (num, lead, rest) in enumerate(ALSO):
        col = i // 15
        row = i % 15
        ix = x + 10 + col * (col_w + 12)
        iy = y + 34 + row * row_h
        nf = F(10, bold=True, serif=False)
        d.text((ix, iy), "%d." % num, font=nf, fill=RED)
        tx = ix + 24
        lead_lines = wrap(d, lead, bf, col_w - 24)
        d.text((tx, iy), lead_lines[0], font=bf, fill=INK)
        if rest:
            rest_lines = wrap(d, rest, rf, col_w - 24)
            d.text((tx, iy + 11), rest_lines[0], font=rf, fill=INK)


def draw():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    # masthead
    mf = F(13, bold=True, serif=False)
    t = "THE WORLD IN ONE PICTURE"
    tw = d.textlength(t, font=mf)
    d.text(((W - tw) / 2, 12), t, font=mf, fill=RED)
    df = F(46, bold=True, serif=True)
    t = "Monday 23 November 2026"
    tw = d.textlength(t, font=df)
    d.text(((W - tw) / 2, 30), t, font=df, fill=INK)
    sf = F(12, bold=True, serif=False)
    t = "44 STORIES  \u00b7  6 CONTINENTS  \u00b7  ALL REPORTED ON MONDAY"
    tw = d.textlength(t, font=sf)
    d.text(((W - tw) / 2, 84), t, font=sf, fill=SOFT)
    d.line([M, 104, W - M, 104], fill=INK, width=2)
    # stat strip
    y = 112
    cell_w = (W - 2 * M) / len(STATS)
    vf = F(17, bold=True, serif=True)
    lf = F(9, bold=True, serif=False)
    for i, (val, lab) in enumerate(STATS):
        cx = M + i * cell_w
        vw = d.textlength(val, font=vf)
        d.text((cx + (cell_w - vw) / 2, y), val, font=vf, fill=RED)
        lw = d.textlength(lab, font=lf)
        d.text((cx + (cell_w - lw) / 2, y + 22), lab, font=lf, fill=SOFT)
        if i:
            d.line([cx, y + 2, cx, y + 32], fill=RULE, width=1)
    d.line([M, 146, W - M, 146], fill=INK, width=1)
    # leads
    lw_, gutter = 237, 10
    for i, story in enumerate(LEADS):
        lead_card(d, M + i * (lw_ + gutter), 154, lw_, 176, story)
    # features, two rows of five
    fw, fg = 188, 10
    for i, story in enumerate(FEATURES):
        row, col = divmod(i, 5)
        feature_card(d, M + col * (fw + fg), 338 + row * 124, fw, 116, story)
    # map + also
    draw_map_panel(d, M, 586, 456, 372)
    draw_also_panel(d, 490, 586, W - M - 490, 372)
    # footer
    d.line([M, 968, W - M, 968], fill=INK, width=2)
    ff = F(10, serif=False)
    line1 = ("Every story here happened or was first reported on Monday "
             "23 November 2026. Contested claims are labelled as claims.")
    d.text((M, 976), line1, font=ff, fill=INK)
    line2 = ("Sources: AP, Reuters, AFP, BBC, Al Jazeera, CNBC, The Hindu.  "
             "CONFIRMED \u2014 multiple sources  \u00b7  REPORTED \u2014 single "
             "source or developing  \u00b7  CLAIM \u2014 contested claim.")
    d.text((M, 992), line2, font=ff, fill=SOFT)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = draw()
    img.save(out, "PNG", optimize=True)
    print("wrote %s %d bytes %s" % (out, os.path.getsize(out), img.size))


if __name__ == "__main__":
    main()
