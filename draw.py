#!/usr/bin/env python3
"""Render the news-image-20261121 v2 entry: one broadsheet page, 35 stories,
all from Saturday 21 November 2026. Drawn flat in code, no photographs.

Renders at 2x (2048) and downscales to 1024x1024 with LANCZOS.
Deterministic: no randomness, no timestamps, no network.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "entry.png")

S = 2                      # render scale (2048 from 1024 design units)
W, H = 1024, 1024
MX = 30                    # side margin
CW = 964                   # content width
RX = MX + CW               # right edge

CREAM = (247, 241, 227)
PAPER = (253, 251, 243)
INK = (17, 17, 17)
RED = (200, 16, 46)
GREY = (90, 86, 76)
FAINT = (201, 191, 166)
TEAL = (14, 124, 123)
BLUE = (37, 99, 235)
NAVY = (30, 58, 95)
ORANGE = (234, 88, 12)
PURPLE = (124, 58, 237)
GREEN = (21, 128, 61)
GOLD = (201, 162, 39)
DARKNAVY = (22, 35, 61)
SEA = (46, 127, 168)
LAND = (169, 191, 168)
LANDLINE = (110, 127, 107)

# ---------------------------------------------------------------- data
# region order for the bar; colours per region
REGIONS = [
    ("ASIA", 6, TEAL),
    ("EUROPE", 7, BLUE),
    ("MIDDLE EAST", 4, ORANGE),
    ("AFRICA", 6, PURPLE),
    ("AMERICAS", 4, RED),
    ("OCEANIA", 3, GREEN),
    ("GLOBAL", 5, NAVY),
]

LEADS = [
    dict(region="EUROPE", kick="BRUSSELS \u2014 EU BUDGET", scene="eu",
         head="EU BUDGET CUT TO \u20ac1.58 TRILLION, BIG TECH TAX PROPOSED",
         body="Costa's draft cuts \u20ac204bn from the Commission's plan, adding a 3% levy "
              "on large digital firms to raise about \u20ac5bn a year.",
         src="Reuters"),
    dict(region="MIDDLE EAST", kick="RIYADH \u2014 MISSILES DOWNED", scene="riyadh",
         head="THREE HOUTHI MISSILES SHOT DOWN OVER RIYADH",
         body="Saudi-led coalition intercepts the ballistic missiles aimed at the "
              "capital, the second attack on Riyadh in days.",
         src="Reuters"),
    dict(region="ASIA", kick="BANDA SEA \u2014 QUAKE", scene="quake",
         head="6.8 QUAKE STRIKES THE BANDA SEA, 226 KM OFF TIMOR",
         body="The deep tremor, 117 km down, triggers a green alert; no casualties "
              "or damage are reported.",
         src="Reuters / USGS"),
]

# n, region, colour, headline, source, glyph
TILES = [
    (4, "AMERICAS", RED, "MIGRANT CARAVAN ENTERS SOUTHERN MEXICO", "AFP", "walk"),
    (5, "GLOBAL", TEAL, "COP31 RUNS INTO OVERTIME AS FOSSIL-FUEL ROW BLOCKS A DEAL", "AP / BBC", "globe"),
    (6, "GLOBAL", PURPLE, "UN AGREES \u2018KILLER ROBOT\u2019 RULES TALKS TO RUN TO 2028", "Reuters / AP", "robot"),
    (7, "ASIA", TEAL, "AIR NIUGINI JET LANDS IN DAVAO AFTER ENGINE FIRE WARNING", "AP", "plane"),
    (8, "ASIA", BLUE, "AKVAN\u2019S REMNANT CANCELS 14 FLIGHTS AT RANCHI", "PTI / IMD", "cyclone"),
    (9, "AFRICA", PURPLE, "SOUTH AFRICA MOURNS FIRST WOMAN DEPUTY PRESIDENT, 71", "Reuters", "candle"),
    (10, "AFRICA", BLUE, "KENYA FLOODS KILL SIX, HIT 1,141 HOUSEHOLDS", "Daily Nation", "waves"),
    (11, "MIDDLE EAST", ORANGE, "FOUR KILLED, 30 HURT IN BASRA POWER STATION FIRE", "Reuters", "flame"),
    (12, "EUROPE", BLUE, "DEPARDIEU AND HOUELLEBECQ FACE SEX-ASSAULT PROBE", "Reuters", "gavel"),
    (13, "EUROPE", NAVY, "RUSSIAN CARGO SHIP HIT BY DRONES, BURNING OFF FINLAND", "Reuters", "ship"),
    (14, "GLOBAL", RED, "VERSTAPPEN ON LAS VEGAS POLE AFTER ANTONELLI PENALTY", "Reuters", "flag"),
    (15, "OCEANIA", GREEN, "INDIA 486 FOR 4 AT WELLINGTON AS RAHUL HITS 136", "ESPNcricinfo", "cricket"),
]

# renumbered 16-35 in order; (region, text, source)
BRIEFS = [
    ("EUROPE", "EU plastic waste export ban takes effect", "EC"),
    ("EUROPE", "Denmark pushes EU curbs on Russians after foiled plot", "Reuters"),
    ("EUROPE", "Wildberries chief quits days after EU sanctions", "Reuters"),
    ("EUROPE", "Bayern held 1-1 by K\u00f6ln; Espanyol win at Bilbao", "wires"),
    ("MIDDLE EAST", "Israeli troops seize Haddatha in south Lebanon", "Press TV"),
    ("MIDDLE EAST", "Iraqi forces enter Kataib Hezbollah stronghold", "NYT"),
    ("AFRICA", "Somalia\u2013UAE crisis deepens as Mogadishu rallies", "wires"),
    ("AFRICA", "Four dead in Bayelsa boat accident, Nigeria", "Daily Trust"),
    ("AFRICA", "South Sudan delays first elections again, to Feb 2027", "wires"),
    ("AFRICA", "About 700,000 displaced by conflict in southern Ethiopia", "wires"),
    ("AMERICAS", "\u2018Chapo Isidro\u2019 captured in Mexico operation", "NY Post"),
    ("AMERICAS", "Bolsonaro hospitalised with intestinal obstruction", "wires"),
    ("AMERICAS", "Trump taps Kirsten Davies as cyber chief", "White House"),
    ("ASIA", "Romualdez co-accused surrenders in flood probe", "SCMP"),
    ("ASIA", "Tainted alcohol kills 11 in India, 180 in hospital", "NDTV"),
    ("ASIA", "Honda and Toyota recall 1.6m vehicles", "SCMP"),
    ("OCEANIA", "North Melbourne reach fourth straight AFLW final", "wires"),
    ("OCEANIA", "Australia backs Cummins as Test captain", "SCMP"),
    ("GLOBAL", "FBI investigating apparent hack of criminal database", "BBC / CNN"),
    ("GLOBAL", "Bezzecchi takes MotoGP pole in Portugal", "CNA"),
]

STATS = [
    ("\u20ac1.58tn", "EU budget in Costa's draft"),
    ("6.8", "quake off Timor-Leste"),
    ("3", "Houthi missiles downed"),
    ("14", "flights cancelled at Ranchi"),
    ("1.6m", "vehicles recalled"),
    ("486/4", "India at Wellington"),
]

# (story number, lon, lat, short label)
PINS = [
    (1, 4, 51, "Brussels"), (2, 46, 25, "Riyadh"), (3, 130, -7, "Banda Sea"),
    (4, -92, 15, "Tapachula"), (5, 30, 37, "Antalya"), (6, 6, 46, "Geneva"),
    (7, 125, 7, "Davao"), (8, 85, 23, "Ranchi"), (9, 28, -26, "Pretoria"),
    (10, 37, -1, "Kenya"), (11, 47, 30, "Basra"), (12, 2, 49, "Paris"),
    (13, 24, 60, "Gulf of Finland"), (14, -115, 36, "Las Vegas"),
    (15, 175, -41, "Wellington"),
]

SUBHEAD = ("Costa cuts the EU budget to \u20ac1.58tn \u00b7 Three Houthi missiles "
           "downed over Riyadh \u00b7 6.8 quake strikes the Banda Sea")
LEFT_OUT = ("Left out as other days' news: GTA VI's $3.79bn first day (20 Nov), "
            "the UK\u2013EU pact signed (20 Nov), Egypt's $2.3bn IMF deal (18 Nov), "
            "the 6.7 Peru quake (20 Nov evening), the APEC Shenzhen declaration "
            "(19 Nov), the Wall Street correction (20 Nov) and the Riemann proof "
            "claim (20 Nov).")
MICROLINE = ("PICTURES DRAWN IN CODE - NO PHOTOGRAPHS - SOURCES: REUTERS / AP / "
             "BBC / PTI / ESPNCRICINFO / SCMP / WIRES")

# ---------------------------------------------------------------- fonts
SERIF = "LiberationSerif"
SANS = "LiberationSans"
_font_cache = {}


def _find_font(family, bold=False, italic=False):
    base = "/usr/share/fonts/truetype"
    cands = []
    if family == "LiberationSerif":
        name = "LiberationSerif-"
        if bold and italic:
            name += "BoldItalic"
        elif bold:
            name += "Bold"
        elif italic:
            name += "Italic"
        else:
            name += "Regular"
        cands.append(f"{base}/liberation/{name}.ttf")
        cands.append(f"{base}/dejavu/DejaVuSerif{'-Bold' if bold else ''}.ttf")
    else:
        name = "LiberationSans-"
        if bold and italic:
            name += "BoldItalic"
        elif bold:
            name += "Bold"
        elif italic:
            name += "Italic"
        else:
            name += "Regular"
        cands.append(f"{base}/liberation/{name}.ttf")
        cands.append(f"{base}/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf")
    for path in cands:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(cands)


def F(family, pt, bold=False, italic=False):
    """Font at pt design points (scaled to render px)."""
    key = (family, round(pt, 1), bold, italic)
    if key not in _font_cache:
        path = _find_font(family, bold, italic)
        _font_cache[key] = ImageFont.truetype(path, int(round(pt * S)))
    return _font_cache[key]


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, img):
        self.d = ImageDraw.Draw(img)

    def rect(self, x0, y0, x1, y1, **kw):
        if "width" in kw:
            kw["width"] = max(1, int(round(kw["width"] * S)))
        self.d.rectangle([int(round(x0 * S)), int(round(y0 * S)),
                          int(round(x1 * S)), int(round(y1 * S))], **kw)

    def ellipse(self, x0, y0, x1, y1, **kw):
        if "width" in kw:
            kw["width"] = max(1, int(round(kw["width"] * S)))
        self.d.ellipse([int(round(x0 * S)), int(round(y0 * S)),
                        int(round(x1 * S)), int(round(y1 * S))], **kw)

    def poly(self, pts, **kw):
        self.d.polygon([(int(round(x * S)), int(round(y * S))) for x, y in pts], **kw)

    def line(self, pts, fill, w=1):
        self.d.line([(int(round(x * S)), int(round(y * S))) for x, y in pts],
                    fill=fill, width=max(1, int(round(w * S))))

    def arc(self, box, a0, a1, fill, w=1):
        self.d.arc([int(round(v * S)) for v in box], a0, a1, fill=fill,
                   width=max(1, int(round(w * S))))

    def text(self, x, y, s, font, fill):
        self.d.text((x * S, y * S), s, font=font, fill=fill)

    def text_c(self, cx, y, s, font, fill):
        w = font.getlength(s)
        self.d.text((cx * S - w / 2, y * S), s, font=font, fill=fill)

    def text_r(self, rx, y, s, font, fill):
        w = font.getlength(s)
        self.d.text((rx * S - w, y * S), s, font=font, fill=fill)


NOTES = []  # shrink / fit notes for the run report


def wrap_text(text, font, max_w):
    """Greedy word wrap; max_w in design units; returns list of lines."""
    limit = max_w * S
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if font.getlength(trial) <= limit:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_font(family, text, start_pt, max_w, bold=False, italic=False, min_pt=8.0):
    """Largest size <= start_pt at which text fits max_w; logs if shrunk."""
    pt = start_pt
    while pt > min_pt:
        f = F(family, pt, bold, italic)
        if f.getlength(text) <= max_w * S:
            break
        pt -= 0.5
    if pt < start_pt:
        NOTES.append(f"shrunk to {pt}pt: {text[:60]}")
    return F(family, pt, bold, italic), pt


def draw_wrapped(cv, x, y, text, family, pt, max_w, lh, fill, bold=False,
                 italic=False, max_lines=None, min_pt=8.0):
    """Draw wrapped text, shrinking the font until it fits max_lines.
    Returns (lines_drawn, end_y)."""
    size = pt
    while True:
        font = F(family, size, bold, italic)
        lines = wrap_text(text, font, max_w)
        if max_lines is None or len(lines) <= max_lines or size <= min_pt:
            break
        size -= 0.5
    if size < pt:
        NOTES.append(f"shrunk to {size}pt: {text[:60]}")
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip() + "\u2026"
        NOTES.append(f"TRUNCATED to {max_lines} lines: {text[:60]}")
    for i, ln in enumerate(lines):
        cv.text(x, y + i * lh, ln, font, fill)
    return lines, y + len(lines) * lh

# ---------------------------------------------------------------- scenes
def scene_eu(cv, x, y, w, h):
    """EU hemicycle: arc of gold seats above, old bar struck through,
    new gold bar below."""
    cv.rect(x, y, x + w, y + h, fill=(220, 230, 242))
    cx, cy = x + w / 2, y + 52
    for r, step in ((40, 9), (28, 11)):
        a = 195
        while a <= 345:
            rad = math.radians(a)
            px = cx + r * math.cos(rad)
            py = cy + r * math.sin(rad) * 0.6
            cv.ellipse(px - 2.2, py - 2.2, px + 2.2, py + 2.2, fill=GOLD)
            a += step
    # old bar (grey, struck through) and new bar (gold), stacked at bottom
    cv.rect(x + 10, y + 56, x + 130, y + 64, fill=(150, 150, 148))
    cv.line([(x + 8, y + 55), (x + 132, y + 65)], RED, 1.6)
    cv.rect(x + 10, y + 66, x + 190, y + 74, fill=GOLD)
    lab = F(SANS, 8, bold=True)
    cv.text(x + 134, y + 55, "\u20ac1.78tn", lab, GREY)
    cv.text(x + 194, y + 65, "\u20ac1.58tn", lab, INK)
    # 3% badge
    cv.ellipse(x + w - 34, y + 6, x + w - 8, y + 32, fill=RED)
    cv.text_c(x + w - 21, y + 10.5, "3%", F(SANS, 11, bold=True), (255, 255, 255))


def scene_riyadh(cv, x, y, w, h):
    """Night sky over Riyadh: three missile streaks, three intercept bursts."""
    cv.rect(x, y, x + w, y + h, fill=DARKNAVY)
    for sx, sy in ((0.12, 0.18), (0.45, 0.10), (0.78, 0.22), (0.30, 0.30), (0.62, 0.06)):
        cv.ellipse(x + w * sx - 1, y + h * sy - 1, x + w * sx + 1, y + h * sy + 1,
                   fill=(255, 255, 255))
    # skyline silhouette
    base = y + h
    for bx, bw, bh in ((0, 26, 22), (30, 20, 30), (54, 16, 18), (74, 22, 34),
                       (100, 18, 24), (122, 24, 30), (150, 20, 20), (174, 26, 28),
                       (204, 22, 36), (230, 20, 22), (254, 24, 30), (282, 22, 26)):
        cv.rect(x + bx, base - bh, x + bx + bw, base, fill=(10, 14, 26))
    # Kingdom Centre tower with arch
    tx = x + w / 2 - 8
    cv.rect(tx, base - 58, tx + 16, base, fill=(10, 14, 26))
    cv.poly([(tx, base - 58), (tx + 16, base - 58), (tx + 8, base - 70)], fill=(10, 14, 26))
    # missile streaks (top) and intercept bursts (mid-air)
    for mx, my, bx, by in ((0.18, 0.02, 0.24, 0.42), (0.52, 0.00, 0.58, 0.34),
                           (0.85, 0.04, 0.80, 0.46)):
        cv.line([(x + w * mx, y + h * my), (x + w * bx, y + h * by)],
                (255, 214, 120), 1.8)
        cx, cy = x + w * bx, y + h * by
        for k in range(8):
            ang = math.radians(k * 45)
            cv.line([(cx, cy), (cx + 9 * math.cos(ang), cy + 9 * math.sin(ang))],
                    (255, 190, 60), 1.6)
        cv.ellipse(cx - 3, cy - 3, cx + 3, cy + 3, fill=(255, 240, 180))


def scene_quake(cv, x, y, w, h):
    """Banda Sea cross-section: islands, fault crack, rings, seismograph."""
    cv.rect(x, y, x + w, y + h * 0.34, fill=(191, 227, 234))
    cv.rect(x, y + h * 0.34, x + w, y + h, fill=SEA)
    # islands
    cv.poly([(x + 18, y + 30), (x + 52, y + 18), (x + 86, y + 28), (x + 78, y + 38),
             (x + 40, y + 40)], fill=(74, 124, 84))
    cv.poly([(x + 210, y + 26), (x + 246, y + 14), (x + 282, y + 26), (x + 272, y + 38),
             (x + 224, y + 38)], fill=(74, 124, 84))
    # fault crack
    ex, ey = x + w * 0.55, y + h * 0.62
    crack = [(x + 60, y + 40), (x + 110, y + 52), (ex - 30, y + 44), (ex, ey),
             (ex + 34, y + 66), (x + 250, y + 70)]
    cv.line(crack, (30, 40, 52), 2.2)
    # radiating rings
    for r in (14, 26, 38):
        cv.ellipse(ex - r, ey - r * 0.7, ex + r, ey + r * 0.7, outline=(255, 255, 255), width=2)
    cv.ellipse(ex - 4, ey - 4, ex + 4, ey + 4, fill=RED)
    # seismograph strip
    sx, sy, sw, sh = x + w - 118, y + h - 26, 108, 20
    cv.rect(sx, sy, sx + sw, sy + sh, fill=(255, 255, 255), outline=INK, width=1)
    zig = [(sx + 4, sy + 10), (sx + 16, sy + 10), (sx + 22, sy + 3), (sx + 28, sy + 17),
           (sx + 34, sy + 6), (sx + 40, sy + 14), (sx + 48, sy + 10), (sx + 60, sy + 10),
           (sx + 66, sy + 2), (sx + 72, sy + 18), (sx + 80, sy + 10), (sx + 104, sy + 10)]
    cv.line(zig, INK, 1.4)
    cv.text(sx + 6, sy + 1.5, "6.8", F(SANS, 9, bold=True), RED)


SCENES = {"eu": scene_eu, "riyadh": scene_riyadh, "quake": scene_quake}

# ---------------------------------------------------------------- glyphs
def glyph_walk(cv, cx, cy):
    for i, dx in enumerate((-8, 0, 8)):
        px = cx + dx
        cv.ellipse(px - 2, cy - 9, px + 2, cy - 5, fill=(255, 255, 255))
        cv.line([(px, cy - 5), (px, cy + 3)], (255, 255, 255), 2)
        cv.line([(px, cy + 3), (px - 3, cy + 9)], (255, 255, 255), 1.6)
        cv.line([(px, cy + 3), (px + 3, cy + 9)], (255, 255, 255), 1.6)


def glyph_globe(cv, cx, cy):
    cv.ellipse(cx - 9, cy - 9, cx + 9, cy + 9, outline=(255, 255, 255), width=2)
    cv.ellipse(cx - 4, cy - 9, cx + 4, cy + 9, outline=(255, 255, 255), width=1)
    cv.line([(cx - 9, cy), (cx + 9, cy)], (255, 255, 255), 1)


def glyph_robot(cv, cx, cy):
    cv.rect(cx - 7, cy - 6, cx + 7, cy + 8, outline=(255, 255, 255), width=2)
    cv.line([(cx, cy - 6), (cx, cy - 11)], (255, 255, 255), 1.6)
    cv.ellipse(cx - 2, cy - 13, cx + 2, cy - 9, fill=(255, 255, 255))
    cv.ellipse(cx - 4, cy - 2, cx - 1, cy + 1, fill=(255, 255, 255))
    cv.ellipse(cx + 1, cy - 2, cx + 4, cy + 1, fill=(255, 255, 255))


def glyph_plane(cv, cx, cy):
    cv.poly([(cx - 11, cy), (cx + 9, cy - 4), (cx + 12, cy), (cx + 9, cy + 4)],
            fill=(255, 255, 255))
    cv.line([(cx - 2, cy - 2), (cx - 6, cy - 9)], (255, 255, 255), 2)
    cv.line([(cx - 2, cy + 2), (cx - 6, cy + 9)], (255, 255, 255), 2)


def glyph_cyclone(cv, cx, cy):
    for r in (3, 6, 9):
        cv.arc((cx - r, cy - r, cx + r, cy + r), 20, 300, (255, 255, 255), 1.6)


def glyph_candle(cv, cx, cy):
    cv.poly([(cx, cy - 11), (cx + 3, cy - 5), (cx, cy - 2), (cx - 3, cy - 5)],
            fill=(255, 220, 120))
    cv.rect(cx - 3, cy - 2, cx + 3, cy + 10, fill=(255, 255, 255))


def glyph_waves(cv, cx, cy):
    for dy in (-6, 0, 6):
        pts = []
        for i in range(9):
            px = cx - 10 + i * 2.5
            py = cy + dy + (3 if i % 2 == 0 else -3)
            pts.append((px, py))
        cv.line(pts, (255, 255, 255), 1.6)


def glyph_flame(cv, cx, cy):
    cv.poly([(cx, cy - 11), (cx + 5, cy - 2), (cx + 4, cy + 6), (cx - 4, cy + 6),
             (cx - 5, cy - 2)], fill=(255, 220, 120))


def glyph_gavel(cv, cx, cy):
    cv.rect(cx - 9, cy - 7, cx + 3, cy - 1, fill=(255, 255, 255))
    cv.line([(cx - 3, cy - 4), (cx + 9, cy + 8)], (255, 255, 255), 2.4)


def glyph_ship(cv, cx, cy):
    cv.poly([(cx - 11, cy + 2), (cx + 11, cy + 2), (cx + 7, cy + 9), (cx - 7, cy + 9)],
            fill=(255, 255, 255))
    cv.line([(cx, cy + 2), (cx, cy - 9)], (255, 255, 255), 1.8)
    cv.poly([(cx, cy - 9), (cx + 7, cy - 6), (cx, cy - 3)], fill=(255, 220, 120))


def glyph_flag(cv, cx, cy):
    cv.line([(cx - 10, cy - 10), (cx - 10, cy + 10)], (255, 255, 255), 1.8)
    for r in range(2):
        for c in range(4):
            if (r + c) % 2 == 0:
                cv.rect(cx - 9 + c * 5, cy - 10 + r * 5, cx - 4 + c * 5, cy - 5 + r * 5,
                        fill=(255, 255, 255))


def glyph_cricket(cv, cx, cy):
    cv.poly([(cx - 8, cy - 9), (cx - 3, cy - 9), (cx - 1, cy + 2), (cx - 6, cy + 2)],
            fill=(255, 255, 255))
    cv.line([(cx - 4, cy + 2), (cx - 8, cy + 9)], (255, 255, 255), 2)
    cv.ellipse(cx + 3, cy + 4, cx + 9, cy + 10, fill=(255, 220, 120))


GLYPHS = {"walk": glyph_walk, "globe": glyph_globe, "robot": glyph_robot,
          "plane": glyph_plane, "cyclone": glyph_cyclone, "candle": glyph_candle,
          "waves": glyph_waves, "flame": glyph_flame, "gavel": glyph_gavel,
          "ship": glyph_ship, "flag": glyph_flag, "cricket": glyph_cricket}

# ---------------------------------------------------------------- map
# rough continent outlines in (lon, lat)
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-85, 66), (-80, 73),
     (-65, 60), (-55, 52), (-60, 46), (-70, 42), (-75, 35), (-80, 32), (-81, 26),
     (-84, 30), (-90, 21), (-97, 16), (-105, 20), (-110, 23), (-114, 29), (-120, 34),
     (-125, 40), (-124, 48), (-130, 55), (-145, 60), (-158, 58), (-165, 60), (-168, 66)],
    [(-55, 60), (-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74), (-30, 76),
     (-45, 76), (-55, 74), (-58, 68), (-55, 60)],
    [(-80, 10), (-72, 12), (-62, 10), (-52, 5), (-50, 0), (-45, -3), (-35, -8),
     (-38, -15), (-40, -22), (-48, -28), (-52, -33), (-58, -38), (-65, -42),
     (-68, -50), (-70, -54), (-73, -50), (-73, -40), (-72, -30), (-70, -18),
     (-75, -15), (-80, -6), (-81, 0), (-80, 10)],
    [(-17, 15), (-10, 30), (-5, 35), (10, 37), (20, 32), (32, 31), (35, 28),
     (40, 15), (43, 11), (48, 11), (51, 10), (44, 0), (40, -5), (36, -18),
     (32, -28), (26, -34), (20, -35), (15, -27), (12, -18), (9, -1), (9, 4),
     (-8, 4), (-13, 8), (-17, 15)],
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53), (8, 57), (10, 59),
     (5, 60), (5, 62), (12, 65), (18, 69), (25, 71), (35, 68), (45, 68), (55, 68),
     (65, 69), (75, 72), (85, 73), (95, 76), (105, 77), (115, 73), (125, 72),
     (135, 71), (145, 72), (155, 70), (162, 66), (170, 66), (178, 65), (178, 62),
     (170, 60), (162, 60), (158, 55), (150, 59), (142, 55), (140, 50), (135, 45),
     (130, 42), (127, 40), (122, 38), (120, 32), (115, 28), (110, 20), (108, 12),
     (105, 9), (100, 8), (98, 12), (95, 16), (92, 21), (88, 22), (85, 19), (80, 15),
     (77, 8), (75, 12), (72, 20), (68, 23), (62, 25), (58, 25), (55, 26), (52, 28),
     (50, 29), (48, 30), (44, 29), (40, 31), (36, 36), (30, 36), (26, 38), (23, 36),
     (19, 40), (15, 44), (12, 44), (8, 44), (3, 43), (0, 40), (-2, 37), (-6, 36),
     (-10, 36)],
    [(95, 5), (105, -2), (115, -8), (125, -9), (132, -4), (138, -8), (141, -8),
     (141, -2), (132, 0), (120, 0), (110, 2), (100, 5), (95, 5)],
    [(113, -22), (114, -30), (115, -34), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20), (113, -22)],
    [(167, -45), (170, -43), (174, -41), (178, -38), (175, -37), (172, -40), (167, -45)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (-5, 50)],
]

# ---------------------------------------------------------------- layout
def check_counts():
    """Region counts must match the bar and total 35 stories."""
    stories = [(l["region"]) for l in LEADS]
    stories += [t[1] for t in TILES]
    stories += [b[0] for b in BRIEFS]
    assert len(stories) == 35, f"story count {len(stories)} != 35"
    counts = {}
    for r in stories:
        counts[r] = counts.get(r, 0) + 1
    expected = {name: n for name, n, _ in REGIONS}
    assert counts == expected, f"region counts {counts} != {expected}"
    return counts


def draw_kicker_date(cv):
    cv.text(MX, 12, "THE WORLD IN ONE DAY", F(SANS, 12, bold=True), RED)
    cv.text_r(RX, 13, "35 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED SATURDAY 21 NOVEMBER 2026",
              F(SANS, 10.5, bold=True), INK)
    date_font, date_pt = fit_font(SERIF, "Saturday 21 November 2026", 96, CW,
                                  bold=True, min_pt=40)
    cv.text_c(MX + CW / 2, 38, "Saturday 21 November 2026", date_font, INK)
    sub_font, _ = fit_font(SERIF, SUBHEAD, 21, CW, italic=True, min_pt=12)
    cv.text_c(MX + CW / 2, 126, SUBHEAD, sub_font, RED)
    return date_pt


def draw_region_bar(cv):
    y, h = 158, 24
    total = sum(n for _, n, _ in REGIONS)
    x = MX
    for name, n, colour in REGIONS:
        w = CW * n / total
        cv.rect(x, y, x + w, y + h, fill=colour)
        label = f"{name} {n}"
        font, _ = fit_font(SANS, label, 10, w - 6, bold=True, min_pt=7)
        cv.text_c(x + w / 2, y + 5.5, label, font, (255, 255, 255))
        x += w


def draw_stats(cv):
    y = 190
    col_w = CW / len(STATS)
    for i, (num, cap) in enumerate(STATS):
        cx = MX + col_w * i + col_w / 2
        if i > 0:
            bx = MX + col_w * i
            cv.line([(bx, y + 4), (bx, y + 50)], FAINT, 1)
        num_font, _ = fit_font(SERIF, num, 30, col_w - 10, bold=True, min_pt=18)
        cv.text_c(cx, y + 2, num, num_font, RED)
        lines = wrap_text(cap, F(SANS, 8.5), col_w - 8)
        for j, ln in enumerate(lines[:2]):
            cv.text_c(cx, y + 34 + j * 10.5, ln, F(SANS, 8.5), GREY)


def draw_leads(cv):
    xs = [MX, 355, 680]
    w = 313
    for lead, x in zip(LEADS, xs):
        SCENES[lead["scene"]](cv, x, 254, w, 78)
        cv.text(x, 338, lead["kick"], F(SANS, 9.5, bold=True), RED)
        _, head_end = draw_wrapped(cv, x, 353, lead["head"], SERIF, 18.5, w, 23,
                                   INK, bold=True, max_lines=2, min_pt=15)
        _, body_end = draw_wrapped(cv, x, head_end + 4, lead["body"], SANS, 10, w,
                                   13, INK, max_lines=2, min_pt=8.5)
        cv.text(x, body_end + 4, lead["src"], F(SANS, 9, italic=True), GREY)


def draw_tiles(cv):
    tw, th, gap = 233.5, 76, 10
    for idx, (n, region, colour, head, src, glyph) in enumerate(TILES):
        row, col = divmod(idx, 4)
        x = MX + col * (tw + gap)
        y = 452 + row * (th + 8)
        cv.rect(x, y, x + tw, y + th, fill=PAPER, outline=FAINT, width=1)
        cv.rect(x, y, x + tw, y + 24, fill=colour)
        cv.text(x + 7, y + 5, str(n), F(SANS, 13, bold=True), (255, 255, 255))
        GLYPHS[glyph](cv, x + tw - 22, y + 12)
        draw_wrapped(cv, x + 7, y + 29, head, SERIF, 11, tw - 14, 13.5,
                     INK, bold=True, max_lines=3, min_pt=9.5)
        cv.text(x + 7, y + th - 12, src, F(SANS, 8.5, italic=True), GREY)


def map_xy(lon, lat, mx0, my0, mw, mh):
    return (mx0 + (lon + 180) / 360 * mw, my0 + (90 - lat) / 180 * mh)


def draw_map(cv):
    px, py, pw, ph = MX, 704, 318, 180
    cv.rect(px, py, px + pw, py + ph, fill=PAPER, outline=FAINT, width=1)
    cv.text(px + 10, py + 6, "WHERE IT HAPPENED", F(SANS, 11, bold=True), INK)
    mx0, my0, mw, mh = px, py + 24, pw, 120
    # graticule
    for lon in range(-180, 181, 60):
        gx, _ = map_xy(lon, 0, mx0, my0, mw, mh)
        cv.line([(gx, my0), (gx, my0 + mh)], (221, 213, 192), 0.8)
    for lat in range(-60, 91, 30):
        _, gy = map_xy(0, lat, mx0, my0, mw, mh)
        cv.line([(mx0, gy), (mx0 + mw, gy)], (221, 213, 192), 0.8)
    # continents
    for poly in CONTINENTS:
        cv.poly([map_xy(lon, lat, mx0, my0, mw, mh) for lon, lat in poly],
                fill=LAND, outline=LANDLINE)
    # pins, with deterministic de-collision so the Europe cluster stays legible
    pts = []
    for n, lon, lat, _ in PINS:
        x, y = map_xy(lon, lat, mx0, my0, mw, mh)
        pts.append([n, x, y])
    for _ in range(4):
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                dx = pts[j][1] - pts[i][1]
                dy = pts[j][2] - pts[i][2]
                d = math.hypot(dx, dy)
                if d < 13.5 and d > 0:
                    push = (13.5 - d) / 2
                    ux, uy = dx / d, dy / d
                    pts[i][1] -= ux * push
                    pts[i][2] -= uy * push
                    pts[j][1] += ux * push
                    pts[j][2] += uy * push
    for n, x, y in pts:
        x = min(max(x, mx0 + 8), mx0 + mw - 8)
        y = min(max(y, my0 + 8), my0 + mh - 8)
        cv.ellipse(x - 6.5, y - 6.5, x + 6.5, y + 6.5, fill=RED,
                   outline=(255, 255, 255), width=1.5)
        cv.text_c(x, y - 4.5, str(n), F(SANS, 7.5 if n < 10 else 7, bold=True),
                  (255, 255, 255))
    key_lines = [
        "1 Brussels \u00b7 2 Riyadh \u00b7 3 Banda Sea \u00b7 4 Tapachula \u00b7 5 Antalya",
        "6 Geneva \u00b7 7 Davao \u00b7 8 Ranchi \u00b7 9 Pretoria \u00b7 10 Kenya",
        "11 Basra \u00b7 12 Paris \u00b7 13 Gulf of Finland \u00b7 14 Las Vegas \u00b7 15 Wellington",
    ]
    for i, ln in enumerate(key_lines):
        cv.text(px + 10, py + 148 + i * 10.5, ln, F(SANS, 7.5), GREY)


def draw_brief(cv, x, y, n, text, src, max_w):
    size = 9.0
    while size >= 7.5:
        fnum = F(SANS, size, bold=True)
        ftxt = F(SANS, size)
        fsrc = F(SANS, size, italic=True)
        num_s = f"{n}  "
        src_s = f" \u2014 {src}"
        total = (fnum.getlength(num_s) + ftxt.getlength(text)
                 + fsrc.getlength(src_s))
        if total <= max_w * S:
            break
        size -= 0.5
    if size < 9.0:
        NOTES.append(f"brief {n} shrunk to {size}pt")
    xx = x
    cv.text(xx, y, num_s, fnum, RED)
    xx += fnum.getlength(num_s) / S
    cv.text(xx, y, text, ftxt, INK)
    xx += ftxt.getlength(text) / S
    cv.text(xx, y, src_s, fsrc, GREY)


def draw_briefs(cv):
    bx = 366
    cv.text(bx, 704, "ALSO ON SATURDAY \u2014 20 MORE STORIES",
            F(SANS, 11.5, bold=True), INK)
    cv.line([(bx, 721), (RX, 721)], RED, 1.5)
    cols = [(366, 306), (680, 314)]
    for ci, (cx, cw) in enumerate(cols):
        for ri in range(10):
            k = ci * 10 + ri
            region, text, src = BRIEFS[k]
            draw_brief(cv, cx, 728 + ri * 12.5, 16 + k, text, src, cw)


def draw_footer(cv):
    # DATE CHECK box
    cv.rect(MX, 890, RX, 926, fill=PAPER, outline=RED, width=2)
    fcheck = F(SANS, 13, bold=True)
    label = "DATE CHECK "
    lx = MX + 14
    cv.text(lx, 899, label, fcheck, RED)
    cx = lx + fcheck.getlength(label) / S + 2
    cy = 907
    cv.line([(cx, cy + 2), (cx + 4, cy + 6), (cx + 11, cy - 4)], RED, 2.2)
    sentence = ("Every story on this page happened, or was first reported, "
                "on Saturday 21 November 2026.")
    cv.text(cx + 15, 899, sentence, F(SERIF, 13), INK)
    # LEFT OUT strip
    cv.rect(MX, 932, RX, 970, fill=RED)
    prefix = "LEFT OUT AS OTHER DAYS' NEWS:  "
    body = ("GTA VI's $3.79bn first day (20 Nov), the UK\u2013EU pact signed (20 Nov), "
            "Egypt's $2.3bn IMF deal (18 Nov), the 6.7 Peru quake (20 Nov evening), "
            "the APEC Shenzhen declaration (19 Nov), the Wall Street correction "
            "(20 Nov) and the Riemann proof claim (20 Nov).")
    fbold = F(SANS, 9.5, bold=True)
    freg = F(SANS, 9.5)
    max_w = RX - MX - 28
    words = body.split(" ")
    lines, cur = [], prefix
    cur_font_w = lambda s, f: f.getlength(s)
    for word in words:
        trial = cur + (" " if cur != prefix else "") + word
        f = fbold if cur == prefix else freg
        # measure prefix part bold + rest regular
        w = fbold.getlength(prefix) + freg.getlength(trial[len(prefix):]) \
            if trial.startswith(prefix) else freg.getlength(trial)
        if w <= max_w * S:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    for i, ln in enumerate(lines[:2]):
        y = 937 + i * 13
        if ln.startswith(prefix):
            cv.text(MX + 14, y, prefix, fbold, (255, 255, 255))
            cv.text(MX + 14 + fbold.getlength(prefix) / S, y,
                    ln[len(prefix):], freg, (255, 255, 255))
        else:
            cv.text(MX + 14, y, ln, freg, (255, 255, 255))
    # microline
    cv.text_c(MX + CW / 2, 974, MICROLINE, F(SANS, 8), GREY)


def build():
    counts = check_counts()
    img = Image.new("RGB", (W * S, H * S), CREAM)
    cv = Canvas(img)
    date_pt = draw_kicker_date(cv)
    draw_region_bar(cv)
    draw_stats(cv)
    draw_leads(cv)
    draw_tiles(cv)
    draw_map(cv)
    draw_briefs(cv)
    draw_footer(cv)
    small = img.resize((W, H), Image.LANCZOS)
    small.save(OUT_PATH, "PNG", optimize=True)
    size = os.path.getsize(OUT_PATH)
    assert small.size == (1024, 1024), small.size
    assert size < 1024 * 1024, f"entry.png {size} bytes >= 1 MiB"
    print(f"stories: 35 (leads 3, tiles 12, briefs 20)")
    print(f"regions: {counts}")
    print(f"date masthead size: {date_pt}pt")
    print(f"entry.png: {size} bytes, 1024x1024")
    for note in NOTES:
        print(f"NOTE: {note}")
    if not NOTES:
        print("NOTE: no headlines needed shrinking")
    return OUT_PATH


if __name__ == "__main__":
    build()
