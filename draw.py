#!/usr/bin/env python3
"""Draw the Monday 23 November 2026 world-news front page (1024x1024).

v2: dense broadsheet with the winner patterns — masthead with region
counts in the tagline, a DATE CHECK box, a THE DAY IN UTC timeline
strip, 4 lead cards with large literal-scene art, 10 feature cards
with bigger icons, a dotted world map with 12 numbered pins, and a
30-item ALSO list in 3 columns where every item carries a pictogram
and a MON/SUN/SAT day tag. 44 stories in all, every one verified
against live reporting; see STORIES.md for the source and day-tag of
each one. All pictures are original, drawn here in code with Pillow
primitives. Deterministic: no network, no clock, no random.
"""
import math
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

# (number, day, status-or-None, bold lead, rest, icon) — ALSO 15-44.
# Day tags: MON = Monday 23 Nov; SUN/SAT = that day, reported then.
ALSO = [
    (15, "MON", None, "Bolsonaro \u2018stable\u2019 in intensive care",
     "Brazil\u2019s ex-leader stays in hospital.", "cross"),
    (16, "MON", None, "35 Fulanis killed in revenge attacks",
     "Kano, Nigeria.", "pin"),
    (17, "MON", None, "WHO chief pleads for peace",
     "in the Ebola-hit DR Congo area.", "cross"),
    (18, "MON", None, "Netanyahu\u2013Eisenkot talks fail",
     "no deal on a government.", "flags"),
    (19, "MON", None, "Albanese: COP31 failure",
     "a sign of \u2018difficult times\u2019.", "cop"),
    (20, "MON", None, "Myanmar\u2019s army-backed government",
     "calls the ASEAN decision \u2018unfair\u2019.", "flags"),
    (21, "MON", None, "UN states agree to keep talking",
     "on lethal AI weapons.", "star"),
    (22, "MON", None, "Pakistan A beat India A by 48 runs",
     "in the Asia Cup Rising Stars.", "bat"),
    (23, "SUN", None, "Liverpool 4\u20130 Man Utd",
     "Pochettino\u2019s debut is a rout.", "ball"),
    (24, "SUN", None, "Alcaraz beats Zverev 6\u20132, 7\u20136",
     "for a first ATP Finals title.", "ball"),
    (25, "SUN", None, "Barcelona fight back from 2\u20130 down",
     "to sink Villarreal.", "ball"),
    (26, "SAT", None, "Leeds stun Chelsea 4\u20131",
     "Fulham hold Man City 1\u20131.", "ball"),
    (27, "SUN", None, "NFL: Eagles stun Steelers",
     "Cowboys score 51.", "ball"),
    (28, "SUN", "REPORTED", "Mets land Skubal for a record $450m",
     "nine years, pending a physical.", "bat"),
    (29, "SUN", None, "Thitikul wins CME Tour Championship",
     "for a third year in a row.", "golf"),
    (30, "SUN", None, "Gerwyn Price wins Grand Slam",
     "ending a four-year wait for a major.", "target"),
    (31, "MON", None, "25 dead in fire on cargo ship",
     "the vessel was under repair in China.", "flame"),
    (32, "MON", None, "Blast at Basra power facility kills 4",
     "35 injured, Iraq.", "flame"),
    (33, "MON", "REPORTED", "Nvidia chip row: Alice Huang",
     "diverting AI chips to China.", "chip"),
    (34, "MON", None, "Bitcoin rebounds 11%",
     "to $61,034.", "coin"),
    (35, "MON", None, "Tech giants form the AAIF",
     "to set standards for 100bn AI agents.", "star"),
    (36, "MON", None, "Amit Shah\u2019s \u20b94,000-crore push",
     "in Arunachal Pradesh.", "pin"),
    (37, "MON", None, "BJP MP Ramrao Wadkute dies",
     "of cardiac arrest in Delhi.", "cross"),
    (38, "MON", None, "Malaysia to work with the UN and OIC",
     "after the ICJ Myanmar ruling.", "flags"),
    (39, "MON", None, "Australia rebukes US over AUKUS",
     "a congressman threatens SpaceX funds.", "missile"),
    (40, "MON", None, "Anupama defends world snooker title",
     "", "ball"),
    (41, "MON", None, "Student protests sweep Europe",
     "from school funding to climate.", "mega"),
    (42, "MON", None, "IFFI 2026 hosts BRICS film roundtable",
     "", "star"),
    (43, "MON", None, "India and Bulgaria discuss IMEC",
     "and the Black Sea situation.", "pin"),
    (44, "MON", None, "FIFA to confirm the UK as host",
     "of the 2035 Women\u2019s World Cup.", "ball"),
]

STATS = [
    ("\u22128.6%", "S&P 500, THE WEEK"),
    ("\u221210%", "NASDAQ, THE WEEK"),
    ("35.89", "VIX VOLATILITY"),
    ("$92.57", "BRENT CRUDE"),
    ("$3,515", "GOLD, 14-MONTH LOW"),
    ("$81.3BN", "ANTHROPIC IPO"),
]

# (time, event) — THE DAY IN UTC timeline strip.
TIMELINE = [
    ("04:00", "El Chapo Isidro seized, Guasave"),
    ("08:00", "COP31 collapses \u2014 no deal"),
    ("12:00", "Bahrain site struck"),
    ("21:00", "US close: worst week since Apr"),
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


def day_counts():
    counts = {"MON": 0, "SUN": 0, "SAT": 0}
    # Leads are all MON; feature 10 (Lisbon march) is SAT, the rest MON.
    feature_days = {5: "MON", 6: "MON", 7: "MON", 8: "MON", 9: "MON",
                    10: "SAT", 11: "MON", 12: "MON", 13: "MON", 14: "MON"}
    for s in LEADS:
        counts["MON"] += 1
    for s in FEATURES:
        counts[feature_days[s[0]]] += 1
    for a in ALSO:
        counts[a[1]] += 1
    return counts

# ---------------------------------------------------------------- art
# Icons are drawn in a normalised 0..100 space so the same drawing
# works as a 225x70 lead scene, a 54x32 feature icon or a 13x13 ALSO
# pictogram. X/Y map fractions to pixels; S is the size unit
# (min(w, h) / 100) used for radii and line widths so circles stay
# circular in a wide box.


def draw_icon(d, kind, x, y, w, h, ink, accent):
    def X(f):
        return x + f * w / 100.0

    def Y(f):
        return y + f * h / 100.0

    S = min(w, h) / 100.0

    def lw(n=2):
        return max(1, int(round(n * S)))

    def star_pts(cx, cy, r_out, r_in, n=5):
        pts = []
        for i in range(2 * n):
            ang = -math.pi / 2 + i * math.pi / n
            r = r_out if i % 2 == 0 else r_in
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        return pts

    light = (235, 230, 215)
    if kind == "cop":  # cracked globe + empty chairs + NO DEAL
        r = 24 * S
        cx, cy = X(13), Y(50)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ink, width=lw(2))
        d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=accent,
              width=lw(3))
        d.line([cx - r * 0.8, Y(40), cx + r * 0.8, Y(40)], fill=ink,
               width=lw(1))
        d.line([cx - r * 0.8, Y(60), cx + r * 0.8, Y(60)], fill=ink,
               width=lw(1))
        d.line([(cx, Y(28)), (X(10), Y(42)), (X(16), Y(55)), (X(11), Y(70))],
               fill=accent, width=lw(2))
        for fx in (38, 52, 66):
            d.rectangle([X(fx) - 6, Y(28), X(fx) + 6, Y(55)], outline=ink,
                        width=lw(2))
            d.rectangle([X(fx) - 8, Y(55), X(fx) + 8, Y(59)], fill=ink)
            d.line([X(fx) - 6, Y(59), X(fx) - 6, Y(78)], fill=ink,
                   width=lw(2))
            d.line([X(fx) + 6, Y(59), X(fx) + 6, Y(78)], fill=ink,
                   width=lw(2))
        tf = F(max(8, int(round(15 * S))), bold=True, serif=False)
        t = "NO DEAL"
        tw = d.textlength(t, font=tf)
        d.text((X(97) - tw, Y(40)), t, font=tf, fill=accent)
    elif kind == "strait":  # two coasts, ships, missile arcs, fire
        d.polygon([(X(3), Y(6)), (X(30), Y(6)), (X(20), Y(94)),
                   (X(3), Y(94))], fill=ink)
        d.polygon([(X(97), Y(6)), (X(70), Y(6)), (X(80), Y(94)),
                   (X(97), Y(94))], fill=ink)
        d.rectangle([X(36), Y(58), X(48), Y(64)], fill=accent)
        d.rectangle([X(41), Y(50), X(44), Y(58)], fill=accent)
        d.rectangle([X(54), Y(72), X(64), Y(77)], fill=light)
        d.rectangle([X(58), Y(65), X(61), Y(72)], fill=light)
        d.arc([X(52), Y(10), X(78), Y(38)], 180, 360, fill=accent,
              width=lw(2))
        d.arc([X(30), Y(20), X(55), Y(48)], 180, 360, fill=accent,
              width=lw(2))
        d.polygon(star_pts(X(74), Y(28), 9 * S, 4 * S, 8), fill=RED)
    elif kind == "chart":  # falling line + candles + -8.6% label
        pts = [(X(4), Y(18)), (X(24), Y(26)), (X(44), Y(20)),
               (X(64), Y(46)), (X(82), Y(54)), (X(96), Y(78))]
        d.line(pts, fill=accent, width=lw(3))
        for fx, top, bot in ((14, 22, 34), (38, 26, 42), (62, 50, 66),
                             (86, 58, 74)):
            d.line([X(fx), Y(top - 5), X(fx), Y(bot + 5)], fill=ink,
                   width=lw(1))
            d.rectangle([X(fx) - 3, Y(top), X(fx) + 3, Y(bot)], fill=ink)
        tf = F(max(8, int(round(15 * S))), bold=True, serif=False)
        t = "\u22128.6%"
        tw = d.textlength(t, font=tf)
        d.text((X(97) - tw, Y(6)), t, font=tf, fill=light)
    elif kind == "cuffs":  # police light bar + cuffs + jail bars
        d.rectangle([X(4), Y(12), X(30), Y(26)], fill=RED)
        d.rectangle([X(32), Y(12), X(58), Y(26)], fill=BLUE)
        d.line([X(31), Y(12), X(31), Y(26)], fill=light, width=lw(1))
        for cx in (X(40), X(62)):
            r = 11 * S
            d.ellipse([cx - r, Y(60) - r, cx + r, Y(60) + r], outline=ink,
                      width=lw(3))
        d.line([X(40) + 11 * S, Y(60), X(62) - 11 * S, Y(60)], fill=ink,
               width=lw(3))
        for fx in (78, 86, 94):
            d.line([X(fx), Y(18), X(fx), Y(85)], fill=ink, width=lw(2))
        d.line([X(74), Y(18), X(98), Y(18)], fill=ink, width=lw(2))
        d.line([X(74), Y(85), X(98), Y(85)], fill=ink, width=lw(2))
    elif kind == "flame":
        d.polygon([(X(38), Y(78)), (X(36), Y(58)), (X(44), Y(40)),
                   (X(50), Y(50)), (X(58), Y(42)), (X(62), Y(58)),
                   (X(62), Y(78))], fill=accent)
        d.ellipse([X(45), Y(62), X(55), Y(76)], fill=GOLD)
    elif kind == "drone":
        d.ellipse([X(36), Y(44), X(64), Y(56)], fill=ink)
        for dx, dy in ((-22, -20), (22, -20), (-22, 20), (22, 20)):
            d.ellipse([X(50 + dx) - 6 * S, Y(50 + dy) - 3 * S,
                       X(50 + dx) + 6 * S, Y(50 + dy) + 3 * S],
                      outline=ink, width=lw(2))
            d.line([X(50), Y(50), X(50 + dx), Y(50 + dy)], fill=ink,
                   width=lw(2))
    elif kind == "flags":
        d.line([X(14), Y(8), X(14), Y(92)], fill=ink, width=lw(2))
        d.polygon([(X(14), Y(8)), (X(42), Y(16)), (X(14), Y(24))],
                  fill=accent)
        d.line([X(56), Y(8), X(56), Y(92)], fill=ink, width=lw(2))
        d.polygon([(X(56), Y(8)), (X(84), Y(16)), (X(56), Y(24))],
                  fill=BLUE)
    elif kind == "bat":
        d.line([X(18), Y(12), X(46), Y(40)], fill=ink, width=lw(5))
        d.rectangle([X(44), Y(38), X(56), Y(44)], fill=ink)
        r = 7 * S
        d.ellipse([X(72) - r, Y(32) - r, X(72) + r, Y(32) + r], fill=accent)
    elif kind == "cap":
        d.polygon([(X(26), Y(46)), (X(50), Y(30)), (X(74), Y(46)),
                   (X(50), Y(62))], fill=ink)
        d.line([X(74), Y(46), X(74), Y(66)], fill=accent, width=lw(2))
        d.ellipse([X(71), Y(64), X(77), Y(72)], fill=accent)
    elif kind == "umbrella":
        d.pieslice([X(30), Y(22), X(70), Y(58)], 180, 360, fill=accent)
        d.line([X(50), Y(40), X(50), Y(78)], fill=ink, width=lw(2))
        d.arc([X(46), Y(74), X(54), Y(84)], 0, 180, fill=ink, width=lw(2))
        for dx in (-24, 24):
            d.line([X(50 + dx), Y(66), X(50 + dx), Y(74)], fill=BLUE,
                   width=lw(1))
    elif kind == "missile":
        d.line([X(12), Y(88), X(88), Y(12)], fill=ink, width=lw(3))
        d.polygon([(X(78), Y(8)), (X(92), Y(8)), (X(84), Y(22))],
                  fill=accent)
        d.arc([X(12), Y(8), X(38), Y(34)], 270, 60, fill=accent,
              width=lw(2))
    elif kind == "rocket":
        d.polygon([(X(50), Y(14)), (X(60), Y(34)), (X(56), Y(66)),
                   (X(44), Y(66)), (X(40), Y(34))], fill=ink)
        r = 4 * S
        d.ellipse([X(50) - r, Y(34) - r, X(50) + r, Y(34) + r], fill=accent)
        d.polygon([(X(44), Y(66)), (X(38), Y(84)), (X(48), Y(70))],
                  fill=accent)
        d.polygon([(X(56), Y(66)), (X(62), Y(84)), (X(52), Y(70))],
                  fill=accent)
    elif kind == "star":
        d.polygon(star_pts(X(50), Y(50), 30 * S, 13 * S), fill=accent)
    elif kind == "pin":
        r = 14 * S
        d.ellipse([X(50) - r, Y(38) - r, X(50) + r, Y(38) + r],
                  outline=ink, width=lw(2))
        r2 = 5 * S
        d.ellipse([X(50) - r2, Y(38) - r2, X(50) + r2, Y(38) + r2],
                  fill=accent)
        d.polygon([(X(38), Y(48)), (X(62), Y(48)), (X(50), Y(78))],
                  fill=ink)
    elif kind == "cross":
        d.rectangle([X(42), Y(18), X(58), Y(82)], fill=accent)
        d.rectangle([X(18), Y(42), X(82), Y(58)], fill=accent)
    elif kind == "ball":
        r = 26 * S
        d.ellipse([X(50) - r, Y(50) - r, X(50) + r, Y(50) + r],
                  outline=ink, width=lw(2))
        d.polygon(star_pts(X(50), Y(50), 8 * S, 4 * S), fill=ink)
        for ang in (30, 150, 270):
            a = math.radians(ang)
            d.line([X(50), Y(50),
                    X(50) + 24 * S * math.cos(a),
                    Y(50) + 24 * S * math.sin(a)], fill=ink, width=lw(1))
    elif kind == "target":
        for rr, col, wd in ((26, ink, 2), (17, accent, 2), (8, accent, 0)):
            r = rr * S
            if wd:
                d.ellipse([X(50) - r, Y(50) - r, X(50) + r, Y(50) + r],
                          outline=col, width=lw(wd))
            else:
                d.ellipse([X(50) - r, Y(50) - r, X(50) + r, Y(50) + r],
                          fill=col)
    elif kind == "chip":
        d.rectangle([X(28), Y(28), X(72), Y(72)], outline=ink, width=lw(2))
        d.rectangle([X(42), Y(42), X(58), Y(58)], fill=accent)
        for fx in (38, 50, 62):
            d.line([X(fx), Y(18), X(fx), Y(28)], fill=ink, width=lw(2))
            d.line([X(fx), Y(72), X(fx), Y(82)], fill=ink, width=lw(2))
            d.line([X(18), Y(fx), X(28), Y(fx)], fill=ink, width=lw(2))
            d.line([X(72), Y(fx), X(82), Y(fx)], fill=ink, width=lw(2))
    elif kind == "coin":
        r = 26 * S
        d.ellipse([X(50) - r, Y(50) - r, X(50) + r, Y(50) + r], fill=GOLD,
                  outline=ink, width=lw(2))
        if w >= 20:
            tf = F(max(8, int(round(0.45 * h))), bold=True, serif=False)
            t = "B"
            tw = d.textlength(t, font=tf)
            th = tf.size
            d.text((X(50) - tw / 2, Y(50) - th / 2), t, font=tf, fill=ink)
        else:
            r2 = 8 * S
            d.ellipse([X(50) - r2, Y(50) - r2, X(50) + r2, Y(50) + r2],
                      fill=ink)
    elif kind == "golf":
        d.line([X(30), Y(10), X(30), Y(85)], fill=ink, width=lw(2))
        d.polygon([(X(30), Y(10)), (X(62), Y(18)), (X(30), Y(28))],
                  fill=accent)
        r = 6 * S
        d.ellipse([X(74) - r, Y(80) - r, X(74) + r, Y(80) + r], fill=ink)
    elif kind == "mega":
        d.polygon([(X(20), Y(30)), (X(70), Y(18)), (X(70), Y(62)),
                   (X(20), Y(50))], fill=accent)
        d.rectangle([X(16), Y(50), X(24), Y(70)], fill=ink)
        d.arc([X(74), Y(24), X(88), Y(56)], 270, 90, fill=ink,
              width=lw(2))


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
    d.rectangle([x, y, x + w, y + 78], fill=DARK)
    draw_icon(d, art, x + 6, y + 4, w - 12, 70, light_fg(), RED)
    d.rectangle([x, y + 78, x + w, y + 80], fill=RED)
    ky = y + 86
    kf = F(9, bold=True, serif=False)
    d.text((x + 8, ky), kicker, font=kf, fill=RED)
    status_tag(d, x + w - 78, ky - 1, status)
    hf = F(16, bold=True, serif=True)
    lines = wrap(d, headline, hf, w - 16)
    ty = text_block(d, x + 8, ky + 16, lines[:3], hf, leading=19)
    df = F(11, serif=False)
    avail = (y + h) - (ty + 2) - 4
    n_deck = max(1, avail // 14)
    dlines = wrap(d, deck, df, w - 16)
    text_block(d, x + 8, ty + 2, dlines[:n_deck], df, fill=SOFT, leading=14)


def light_fg():
    return (235, 230, 215)


def feature_card(d, x, y, w, h, story):
    num, region, status, kicker, headline, deck, art = story
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    d.rectangle([x, y, x + w, y + 38], fill=PAPER)
    draw_icon(d, art, x + w - 60, y + 3, 54, 32, INK, RED)
    kf = F(8, bold=True, serif=False)
    d.text((x + 7, y + 4), kicker, font=kf, fill=RED)
    status_tag(d, x + 7, y + 17, status)
    hf = F(12, bold=True, serif=True)
    lines = wrap(d, headline, hf, w - 14)
    ty = text_block(d, x + 7, y + 42, lines[:3], hf, leading=14)
    df = F(10, serif=False)
    avail = (y + h) - (ty + 2) - 4
    n_deck = max(1, avail // 12)
    dlines = wrap(d, deck, df, w - 14)
    text_block(d, x + 7, ty + 2, dlines[:n_deck], df, fill=SOFT, leading=12)


def draw_map_panel(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    tf = F(12, bold=True, serif=False)
    d.text((x + 10, y + 8), "WHERE IT HAPPENED", font=tf, fill=INK)
    d.line([x + 10, y + 28, x + w - 10, y + 28], fill=RULE, width=1)
    mx0, my0, mx1, my1 = x + 14, y + 36, x + w - 14, y + 288
    step = 6
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
    cf = F(10, bold=True, serif=False)
    line1 = "EUROPE 11  \u00b7  MIDDLE EAST 3  \u00b7  AMERICAS 8  \u00b7  " \
            "ASIA-PACIFIC 13"
    tw = d.textlength(line1, font=cf)
    d.text((x + (w - tw) / 2, y + 296), line1, font=cf, fill=INK)
    line2 = "AFRICA 3  \u00b7  OCEANIA 2  \u00b7  WORLD 4  \u00b7  44 STORIES"
    tw = d.textlength(line2, font=cf)
    d.text((x + (w - tw) / 2, y + 312), line2, font=cf, fill=INK)
    sf = F(10, serif=False)
    sub = "pins mark the 12 places above"
    tw = d.textlength(sub, font=sf)
    d.text((x + (w - tw) / 2, y + 328), sub, font=sf, fill=SOFT)
    lf = F(9, serif=False)
    keys1 = "1 Antalya  \u00b7  2 Bahrain  \u00b7  3 Riyadh  \u00b7  " \
            "4 Guasave  \u00b7  5 Kyiv  \u00b7  6 Cikande"
    tw = d.textlength(keys1, font=lf)
    d.text((x + (w - tw) / 2, y + 342), keys1, font=lf, fill=SOFT)
    keys2 = "7 Seoul  \u00b7  8 Lisbon  \u00b7  9 New Delhi  \u00b7  " \
            "10 Wellington  \u00b7  11 Warsaw  \u00b7  12 Bras\u00edlia"
    tw = d.textlength(keys2, font=lf)
    d.text((x + (w - tw) / 2, y + 356), keys2, font=lf, fill=SOFT)


def draw_also_panel(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    tf = F(12, bold=True, serif=False)
    d.text((x + 10, y + 8), "ALSO ON MONDAY 23 NOVEMBER", font=tf, fill=INK)
    d.line([x + 10, y + 28, x + w - 10, y + 28], fill=RULE, width=1)
    col_w = (w - 20 - 16) // 3
    bf = F(10, bold=True, serif=False)
    rf = F(9, serif=False)
    tagf = F(8, bold=True, serif=False)
    row_h = 33
    for i, (num, day, status, lead, rest, icon) in enumerate(ALSO):
        col = i // 10
        row = i % 10
        ix = x + 10 + col * (col_w + 8)
        iy = y + 34 + row * row_h
        nf = F(10, bold=True, serif=False)
        d.text((ix, iy), "%d." % num, font=nf, fill=RED)
        draw_icon(d, icon, ix + 20, iy + 1, 13, 13, INK, RED)
        tx = ix + 36
        lead_lines = wrap(d, lead, bf, col_w - 36)
        ly = iy
        for ln in lead_lines[:2]:
            d.text((tx, ly), ln, font=bf, fill=INK)
            ly += 11
        tag = day if not status else "%s \u00b7 %s" % (day, status)
        tag_w = d.textlength(tag, font=tagf)
        rest_y = iy + len(lead_lines[:2]) * 11
        rest_lines_avail = 3 - len(lead_lines[:2])
        if rest and rest_lines_avail >= 1:
            rest_lines = wrap(d, rest, rf, col_w)
            drawn = rest_lines[:rest_lines_avail]
            ry = rest_y
            for j, ln in enumerate(drawn):
                last = (j == len(drawn) - 1)
                if last:
                    # keep the tag clear on the last rest line
                    ln_lines = wrap(d, ln, rf, col_w - tag_w - 8)
                    ln = ln_lines[0] if ln_lines else ""
                d.text((ix, ry), ln, font=rf, fill=INK)
                ry += 11
            tag_y = rest_y + (len(drawn) - 1) * 11
            d.text((ix + col_w - tag_w, tag_y), tag, font=tagf, fill=RED)
        else:
            d.text((ix + col_w - tag_w, rest_y), tag, font=tagf, fill=RED)


def draw_date_check(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=RED, width=2)
    hf = F(10, bold=True, serif=False)
    d.rectangle([x, y, x + w, y + 16], fill=RED)
    t = "DATE CHECK \u2713"
    tw = d.textlength(t, font=hf)
    d.text((x + (w - tw) / 2, y + 2), t, font=hf, fill=(255, 255, 255))
    counts = day_counts()
    bf = F(10, bold=True, serif=False)
    rf = F(9, serif=False)
    d.text((x + 8, y + 20), "MON 23 NOV 2026", font=bf, fill=INK)
    d.text((x + 8, y + 34), "44 STORIES VERIFIED", font=rf, fill=INK)
    line3 = "MON %d \u00b7 SUN %d \u00b7 SAT %d" % (
        counts["MON"], counts["SUN"], counts["SAT"])
    d.text((x + 8, y + 48), line3, font=rf, fill=INK)


def draw_timeline(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    lab_w = 128
    d.rectangle([x, y, x + lab_w, y + h], fill=DARK)
    lf = F(10, bold=True, serif=False)
    t = "THE DAY IN UTC"
    tw = d.textlength(t, font=lf)
    d.text((x + (lab_w - tw) / 2, y + (h - 12) / 2), t, font=lf,
           fill=(255, 255, 255))
    col_w = (w - lab_w) // len(TIMELINE)
    tf = F(9, bold=True, serif=False)
    ef = F(9, serif=False)
    for i, (tm, ev) in enumerate(TIMELINE):
        ex = x + lab_w + 10 + i * col_w
        ey = y + (h - 11) / 2
        d.text((ex, ey), tm, font=tf, fill=RED)
        tw = d.textlength(tm, font=tf)
        d.text((ex + tw + 5, ey), ev, font=ef, fill=INK)
        if i:
            d.line([x + lab_w + i * col_w, y + 6,
                    x + lab_w + i * col_w, y + h - 6], fill=RULE, width=1)


def draw():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    # masthead
    mf = F(13, bold=True, serif=False)
    t = "THE WORLD IN ONE PICTURE"
    tw = d.textlength(t, font=mf)
    d.text(((W - tw) / 2, 12), t, font=mf, fill=RED)
    df = F(42, bold=True, serif=True)
    t = "Monday 23 November 2026"
    tw = d.textlength(t, font=df)
    d.text(((W - tw) / 2, 30), t, font=df, fill=INK)
    counts = region_counts()
    tagline = ("44 STORIES  \u00b7  EUROPE %d  \u00b7  MIDDLE EAST %d  \u00b7  "
               "AMERICAS %d  \u00b7  ASIA-PACIFIC %d  \u00b7  AFRICA %d  "
               "\u00b7  OCEANIA %d  \u00b7  WORLD %d" % (
                   counts["Europe"], counts["Middle East"],
                   counts["Americas"], counts["Asia-Pacific"],
                   counts["Africa"], counts["Oceania"], counts["World"]))
    sf = F(12, bold=True, serif=False)
    tw = d.textlength(tagline, font=sf)
    if tw > 820:
        sf = F(11, bold=True, serif=False)
        tw = d.textlength(tagline, font=sf)
    d.text(((W - tw) / 2, 84), tagline, font=sf, fill=SOFT)
    draw_date_check(d, 880, 12, 122, 68)
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
    # timeline strip
    draw_timeline(d, M, 154, W - 2 * M, 32)
    # leads
    lw_, gutter = 237, 10
    for i, story in enumerate(LEADS):
        lead_card(d, M + i * (lw_ + gutter), 194, lw_, 184, story)
    # features, two rows of five
    fw, fg = 188, 10
    for i, story in enumerate(FEATURES):
        row, col = divmod(i, 5)
        feature_card(d, M + col * (fw + fg), 386 + row * 116, fw, 108, story)
    # map + also
    draw_map_panel(d, M, 618, 456, 370)
    draw_also_panel(d, 490, 618, W - M - 490, 370)
    # footer
    d.line([M, 994, W - M, 994], fill=INK, width=2)
    ff = F(10, serif=False)
    line1 = ("Every story here happened or was first reported on Monday "
             "23 November 2026. Contested claims are labelled as claims.")
    d.text((M, 1000), line1, font=ff, fill=INK)
    line2 = ("Sources: AP, Reuters, AFP, BBC, Al Jazeera, CNBC, The Hindu.  "
             "CONFIRMED \u2014 multiple sources  \u00b7  REPORTED \u2014 single "
             "source or developing  \u00b7  CLAIM \u2014 contested claim.")
    d.text((M, 1013), line2, font=ff, fill=SOFT)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = draw()
    img.save(out, "PNG", optimize=True)
    print("wrote %s %d bytes %s" % (out, os.path.getsize(out), img.size))


if __name__ == "__main__":
    main()
