"""Draws entry.png: the world's news of Sunday 22 November 2026 on one 1024x1024 front page.

Run: python3 render.py  (needs Pillow and the macOS system fonts Charter, Avenir Next Condensed, Helvetica Neue).
Every story and figure is listed with its sources in FACTS.md. Drawing is deterministic: same input, same bytes.
Layout: masthead, day in numbers, region bar, UTC strip, 3 drawn leads, 12 drawn cards, a numbered map,
22 one-line briefs and a date check that names the earlier events left out.
"""
from PIL import Image, ImageDraw, ImageFont

S = 2                      # draw at 2x, then downsample for clean edges
W = H = 1024
AVC = '/System/Library/Fonts/Avenir Next Condensed.ttc'
HN = '/System/Library/Fonts/HelveticaNeue.ttc'
CH = '/System/Library/Fonts/Supplemental/Charter.ttc'

PAPER = (248, 245, 238)
CARD = (255, 253, 248)
INK = (22, 24, 30)
GREY = (96, 100, 108)
RULE = (208, 202, 190)
NAVY = (20, 34, 60)
RED = (176, 32, 38)
GREEN = (30, 120, 64)
ORANGE = (214, 120, 20)

REGIONS = {  # region -> colour (order = region bar order)
    'EUROPE': (36, 88, 168),
    'MIDDLE EAST': (184, 44, 40),
    'AFRICA': (204, 122, 18),
    'AMERICAS': (124, 46, 164),
    'SOUTH ASIA': (196, 64, 128),
    'ASIA-PACIFIC': (16, 136, 118),
    'GLOBAL': (70, 74, 84),
}

_fonts = {}


def font(kind, size):
    key = (kind, size)
    if key not in _fonts:
        path, idx = {
            'black': (CH, 5), 'serif': (CH, 3), 'italic': (CH, 1), 'roman': (CH, 0),
            'heavy': (AVC, 8), 'bold': (AVC, 0), 'demi': (AVC, 2), 'med': (AVC, 5),
            'reg': (HN, 0), 'hbold': (HN, 1),
        }[kind]
        _fonts[key] = ImageFont.truetype(path, int(size * S), index=idx)
    return _fonts[key]


img = Image.new('RGB', (W * S, H * S), PAPER)
d = ImageDraw.Draw(img)


def P(*v):
    return [x * S for x in v]


def text(x, y, s, kind, size, fill=INK, anchor='la'):
    d.text((x * S, y * S), s, font=font(kind, size), fill=fill, anchor=anchor)


def tw(s, kind, size):
    return d.textlength(s, font=font(kind, size)) / S


def wrap(s, kind, size, width):
    lines, cur = [], ''
    for w in s.split():
        t = (cur + ' ' + w).strip()
        if tw(t, kind, size) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, kind, size, width, lead, fill=INK, max_lines=9):
    lines = wrap(s, kind, size, width)
    assert len(lines) <= max_lines, (s, len(lines))
    for i, ln in enumerate(lines):
        text(x, y + i * lead, ln, kind, size, fill)
    return y + len(lines) * lead


def rect(x0, y0, x1, y1, fill=None, outline=None, width=1, r=0):
    if r:
        d.rounded_rectangle(P(x0, y0, x1, y1), radius=r * S, fill=fill, outline=outline, width=int(width * S))
    else:
        d.rectangle(P(x0, y0, x1, y1), fill=fill, outline=outline, width=int(width * S))


def poly(pts, fill):
    d.polygon([v * S for p in pts for v in p], fill=fill)


def ell(cx, cy, rx, ry, fill=None, outline=None, width=1):
    d.ellipse(P(cx - rx, cy - ry, cx + rx, cy + ry), fill=fill, outline=outline, width=int(width * S))


def line(pts, fill, width=1):
    d.line([v * S for p in pts for v in p], fill=fill, width=int(width * S))


def badge(x, y, n, col):
    ell(x + 8, y + 8, 8, 8, fill=col, outline=(255, 255, 255), width=1.2)
    text(x + 8, y + 8.5, str(n), 'heavy', 10, (255, 255, 255), 'mm')


def chip(x, y, label, col, right=False):
    w = tw(label, 'heavy', 8.5) + 8
    if right:
        x -= w
    rect(x, y, x + w, y + 12, fill=col, r=2)
    text(x + 4, y + 1.5, label, 'heavy', 8.5, (255, 255, 255))
    return w


STATUS = {'CONFIRMED': GREEN, 'CLAIM': ORANGE}

# ------------------------------------------------------------------ stories
# leads and cards carry a map position (lon, lat) and a drawing; briefs are one line each.
LEADS = [
    dict(n=1, region='GLOBAL', place='ANTALYA, TÜRKIYE · CLIMATE', status='CONFIRMED', art='cop', ll=(30.7, 36.9),
         head='COP31 ends with no climate deal',
         dek='After two days of overtime the EU, UK and island states reject a final text that never names fossil '
             'fuels. Guterres "deeply disappointed"; the longest COP on record.',
         src='UN News · NPR · Guardian · Al Jazeera · AFP'),
    dict(n=2, region='AFRICA', place='BENGHAZI, LIBYA · WAR AT SEA', status='CONFIRMED', art='ship', ll=(20.1, 32.1),
         head='Russian warship sinks in Libyan port',
         dek='Suspected Ukrainian sea drones hit the corvette Merkury before dawn; satellite images show it '
             'capsized. A Malta-flagged cargo ship is hit off Benghazi that evening.',
         src='Reuters · Guardian · Al Jazeera'),
    dict(n=3, region='EUROPE', place='KYIV REGION, UKRAINE · WAR', status='CONFIRMED', art='drones', ll=(30.3, 50.8),
         head='Russia fires 186 drones; 14+ die near Kyiv',
         dek='Air force: 161 downed or jammed by 08:00. In Dymer a five-storey block partly collapses; '
             'Zelenskyy asks the US for Patriot interceptors.',
         src='Ukrainian Air Force · Kyiv Post · Al Jazeera'),
]
CARDS = [
    dict(n=4, region='MIDDLE EAST', place='SITRA, BAHRAIN', status='CLAIM', art='bahrain', ll=(50.6, 26.2),
         head='Bahrain: 2 hurt; IRGC says it hit US Patriot radars', src='ABC · MEE · Reuters'),
    dict(n=5, region='AMERICAS', place='NORTH CAROLINA, US', status='CONFIRMED', art='capitol', ll=(-80.0, 36.0),
         head='Democrats reach 258 House seats, most since 1992', src='Guardian · Al Jazeera'),
    dict(n=6, region='AFRICA', place='KHARTOUM, SUDAN', status='CONFIRMED', art='sudan', ll=(32.5, 15.6),
         head='RSF drones kill 4 and hit a UN building', src='Al Jazeera · AFP'),
    dict(n=7, region='AFRICA', place='ITURI, DR CONGO', status='CONFIRMED', art='hospital', ll=(30.0, 1.5),
         head='WHO: fighting traps Ebola medics for 24h+', src='Reuters · Al Jazeera'),
    dict(n=8, region='ASIA-PACIFIC', place='SEOUL, S. KOREA', status='CONFIRMED', art='exam', ll=(127.0, 37.5),
         head='Education minister quits over AI exam cheating', src='Guardian · AFP'),
    dict(n=9, region='ASIA-PACIFIC', place='HONG KONG', status='CONFIRMED', art='ballot', ll=(114.2, 22.3),
         head='98.79% turnout in Election Committee polls', src='The Standard · HK govt'),
    dict(n=10, region='MIDDLE EAST', place='TEHRAN, IRAN', status='CONFIRMED', art='power', ll=(51.4, 35.7),
         head='Iran begins rolling two-hour power cuts', src='Iran Intl · The National'),
    dict(n=11, region='ASIA-PACIFIC', place='WELLINGTON, NZ', status='CONFIRMED', art='cricket', ll=(174.8, -41.3),
         head='India declare on 720/9, record Test total in NZ', src='The Statesman · IANS'),
    dict(n=12, region='SOUTH ASIA', place='NEW DELHI, INDIA', status='CONFIRMED', art='plane', ll=(77.2, 28.6),
         head="Nepal PM Balendra Shah lands on first India visit", src='Deccan Herald · MEA'),
    dict(n=13, region='EUROPE', place='TURIN, ITALY', status='CONFIRMED', art='tennis', ll=(7.7, 45.1),
         head='Alcaraz beats No 1 Zverev 6-2 7-6 for ATP Finals', src='Guardian · Reuters'),
    dict(n=14, region='EUROPE', place='PORTIMÃO, PORTUGAL', status='CONFIRMED', art='moto', ll=(-8.5, 37.1),
         head='Márquez seals 8th MotoGP title, equals Agostini', src='Guardian · AP'),
    dict(n=15, region='EUROPE', place='VATICAN CITY', status='CONFIRMED', art='table', ll=(12.45, 41.9),
         head='Pope Leo XIV hosts 1,300 poor guests for lunch', src='Vatican News · EWTN'),
]
BRIEFS = [  # region, place, text, outlet, status
    ('EUROPE', 'Liverpool', '4-0 v 10-man Man United in Pochettino\'s first game', 'Guardian', 'CONFIRMED'),
    ('EUROPE', 'Ukraine', 'Zelenskyy: ~2,700 drones, 165 missiles in a week', 'Kyiv Post', 'CONFIRMED'),
    ('AFRICA', 'Libya', 'eastern PM Hammad asks the UN for an international probe', 'Al Jazeera', 'CONFIRMED'),
    ('MIDDLE EAST', 'Hormuz', 'IRGC says two tankers hit sea mines; UKMTO probes', 'ABC', 'CLAIM'),
    ('MIDDLE EAST', 'Hormuz', 'IRGC claims it downed a US MQ-1 drone; no US comment', 'IRNA', 'CLAIM'),
    ('MIDDLE EAST', 'Iran', 'TV shows a dual-missile launcher in a "missile city"', 'Al Jazeera', 'CONFIRMED'),
    ('MIDDLE EAST', 'Gulf', 'Saudi Arabia, Kuwait and Qatar condemn Bahrain strike', 'ABC', 'CONFIRMED'),
    ('MIDDLE EAST', 'Yemen', 'Saudi coalition downs Houthi drone and missile', 'Al Jazeera', 'CONFIRMED'),
    ('MIDDLE EAST', 'Israel', "Likud and Eisenkot's Yashar end unity talks, no deal", 'Al Jazeera', 'CONFIRMED'),
    ('AMERICAS', 'US-Iran', 'Trump "inclined" to strike again after New Year', 'The Hill', 'CONFIRMED'),
    ('AMERICAS', 'Washington', 'spy chief Clayton backs Trump on Putin "friend"', 'Guardian', 'CONFIRMED'),
    ('AMERICAS', 'AI chips', 'lawmakers ask how top Nvidia chips reached China', 'Fox · Guardian', 'CONFIRMED'),
    ('AMERICAS', 'Colombia', 'government asks X to suspend ex-president Petro', 'EFE · Infobae', 'CONFIRMED'),
    ('AMERICAS', 'Mexico City', 'NFL returns: 49ers beat Vikings 35-10', 'ESPN', 'CONFIRMED'),
    ('AMERICAS', 'Las Vegas', 'Verstappen wins GP (race 04:00 UTC), 35 lead changes', 'F1 · AJ', 'CONFIRMED'),
    ('SOUTH ASIA', 'Bangladesh', 'garment workers try to block Dhaka highway in wage row', 'TBS', 'CONFIRMED'),
    ('ASIA-PACIFIC', 'Taipei', 'HK film "We Are Born Good" wins Golden Horse best film', 'Focus Taiwan', 'CONFIRMED'),
    ('ASIA-PACIFIC', 'Okinawa', 'Shuri Castle main hall restored, 7 years after fire', 'Jiji', 'CONFIRMED'),
    ('ASIA-PACIFIC', 'Canberra', 'Marles says US budget office "wrong" on AUKUS', 'ABC (Aus)', 'CONFIRMED'),
    ('GLOBAL', 'Weapons', 'Red Cross: soon too late to regulate autonomous arms', 'Guardian', 'CONFIRMED'),
    ('GLOBAL', 'Geneva', 'Gukesh v Sindarov world chess title match opens', 'Al Jazeera', 'CONFIRMED'),
    ('GLOBAL', 'Climate', 'Guterres: "no ambiguity in the science" after COP31', 'UN News', 'CONFIRMED'),
]
STORIES = len(LEADS) + len(CARDS) + len(BRIEFS)
assert STORIES == 37, STORIES
counts = {r: 0 for r in REGIONS}
for s in LEADS + CARDS:
    counts[s['region']] += 1
for b in BRIEFS:
    counts[b[0]] += 1

# ------------------------------------------------------------------ top rail and masthead
rect(0, 0, W, 18, fill=NAVY)
text(14, 3.5, 'THE WORLD IN ONE DAY', 'heavy', 10.5, (255, 255, 255))
text(W - 14, 3.5, '%d STORIES · 7 REGIONS · EVERY ONE DATED SUNDAY 22 NOVEMBER 2026' % STORIES,
     'heavy', 10.5, (255, 255, 255), 'ra')
MAST = 'Sunday 22 November 2026'
assert tw(MAST, 'black', 70) < 990
text(W / 2, 22, MAST, 'black', 70, NAVY, 'ma')
text(W / 2, 101, 'COP31 collapses with no deal  ·  Russian warship sunk at Benghazi  ·  186 drones fired at Ukraine overnight',
     'serif', 14, RED, 'ma')
d.line(P(14, 123, W - 14, 123), fill=INK, width=2 * S)

# ------------------------------------------------------------------ day in numbers
NUMS = [('186', 'drones fired at Ukraine overnight; 161 downed'), ('258', 'House seats for Democrats, most since 1992'),
        ('2 days', 'COP31 overtime, then no deal'), ('98.79%', 'turnout, Hong Kong committee polls'),
        ('720/9', "India's record Test total in New Zealand"), ('1,300', "guests at Pope Leo's lunch for the poor")]
cw = (W - 28) / 6
for i, (big, small) in enumerate(NUMS):
    x = 14 + i * cw
    if i:
        d.line(P(x, 128, x, 166), fill=RULE, width=S)
    text(x + cw / 2, 124, big, 'black', 21, RED, 'ma')
    for j, ln in enumerate(wrap(small, 'med', 9.5, cw - 12)):
        assert j < 2, small
        text(x + cw / 2, 149 + j * 9.5, ln, 'med', 9.5, GREY, 'ma')

# ------------------------------------------------------------------ region bar (width = share of stories)
x = 14
for i, (reg, c) in enumerate(REGIONS.items()):
    w = (W - 28) * counts[reg] / STORIES
    rect(x, 171, x + w, 186, fill=c)
    text(x + w / 2, 172.5, '%s %d' % (reg, counts[reg]), 'heavy', 9.5, (255, 255, 255), 'ma')
    x += w

# ------------------------------------------------------------------ UTC strip
rect(14, 190, W - 14, 208, fill=NAVY)
text(22, 193.5, 'THE DAY IN UTC', 'heavy', 10, (240, 200, 100))
UTC = [('01:00', 'HK polls open'), ('04:00', 'Las Vegas GP starts'), ('06:00', 'Kyiv: 161 of 186 drones downed'),
       ('~13:00', 'MotoGP Portimão'), ('~14:30', 'COP31 ends, no deal'), ('~19:15', 'US House: 258th seat'),
       ('~19:30', 'Alcaraz wins Turin')]
x = 108
for t, lab in UTC:
    text(x, 193.5, t, 'heavy', 10, (240, 200, 100))
    x += tw(t, 'heavy', 10) + 4
    text(x, 193.5, lab, 'demi', 10, (255, 255, 255))
    x += tw(lab, 'demi', 10) + 13
assert x < W - 10, x


# ------------------------------------------------------------------ drawings
def sky(x, y, w, h, top, bottom):
    for i in range(int(h)):
        t = i / max(1, h - 1)
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        d.line(P(x, y + i, x + w, y + i), fill=c, width=S + 1)


def art_cop(x, y, w, h):
    sky(x, y, w, h, (214, 232, 222), (236, 242, 236))
    cx, cy, r = x + 58, y + h / 2 + 2, 40
    ell(cx, cy, r, r, fill=(70, 140, 200))
    poly([(cx - 24, cy - 26), (cx + 6, cy - 31), (cx + 14, cy - 9), (cx - 5, cy + 5), (cx - 27, cy - 3)], (80, 160, 90))
    poly([(cx + 8, cy + 11), (cx + 28, cy + 5), (cx + 23, cy + 28), (cx + 9, cy + 31)], (80, 160, 90))
    tx = cx + r + 12
    rect(tx, cy - 36, tx + 10, cy + 20, fill=(255, 255, 255), outline=INK, width=1, r=5)
    rect(tx + 3, cy - 16, tx + 7, cy + 20, fill=(205, 50, 40))
    ell(tx + 5, cy + 26, 9, 9, fill=(205, 50, 40), outline=INK, width=1)
    px = x + 150
    rect(px, y + 10, px + 150, y + h - 10, fill=(255, 255, 255), outline=GREY, width=1)
    text(px + 10, y + 17, 'COP31 FINAL TEXT', 'bold', 11, INK)
    for i in range(4):
        line([(px + 10, y + 36 + i * 10), (px + 140 - (i % 2) * 22, y + 36 + i * 10)], RULE, 2)
    text(px + 10, y + h - 24, '"fossil fuels": not in text', 'bold', 10.5, RED)
    stamp = Image.new('RGBA', (130 * S, 40 * S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rounded_rectangle((2 * S, 2 * S, 128 * S, 38 * S), radius=5 * S, outline=(200, 40, 40, 240), width=4 * S)
    sd.text((65 * S, 20 * S), 'NO DEAL', font=font('heavy', 26), fill=(200, 40, 40, 240), anchor='mm')
    stamp = stamp.rotate(12, resample=Image.BICUBIC, expand=True)
    img.paste(stamp, (int((px + 6) * S), int((y + 12) * S)), stamp)


def art_ship(x, y, w, h):
    sky(x, y, w, h, (26, 34, 64), (88, 70, 96))
    for sx, sy in [(30, 14), (90, 24), (160, 10), (250, 20), (300, 12)]:
        ell(x + sx, y + sy, 1.2, 1.2, fill=(255, 255, 230))
    wy = y + h - 40
    rect(x, wy + 6, x + 88, wy + 20, fill=(120, 116, 108))
    rect(x, wy + 20, x + w, y + h, fill=(30, 60, 110))
    rect(x + 88, wy, x + w, wy + 20, fill=(30, 60, 110))
    hull = Image.new('RGBA', (190 * S, 64 * S), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hull)
    hd.polygon([(0, 18 * S), (160 * S, 18 * S), (188 * S, 4 * S), (176 * S, 42 * S), (12 * S, 42 * S)], fill=(110, 116, 124, 255))
    hd.rectangle((46 * S, 2 * S, 104 * S, 18 * S), fill=(140, 146, 154, 255))
    hull = hull.rotate(-22, resample=Image.BICUBIC, expand=True)
    img.paste(hull, (int((x + 92) * S), int((wy - 52) * S)), hull)
    rect(x + 88, wy + 14, x + w, y + h, fill=(30, 60, 110))
    for i in range(5):
        yy = wy + 20 + (i % 2) * 7
        d.arc(P(x + 100 + i * 34, yy, x + 136 + i * 34, yy + 8), 200, 340, fill=(150, 180, 220), width=2 * S)
    for sx, sy, r, c in [(214, 46, 16, (240, 140, 40)), (204, 36, 10, (255, 210, 80))]:
        ell(x + sx, y + sy, r, r * 0.8, fill=c)
    for sx, sy, r in [(222, 26, 12), (236, 16, 14), (254, 10, 15)]:
        ell(x + sx, y + sy, r, r * 0.75, fill=(110, 110, 118))
    for k in range(3):
        dx, dy = x + 16 + k * 22, y + h - 14 + (k % 2) * 5
        poly([(dx, dy), (dx + 15, dy - 3), (dx + 15, dy + 3)], (230, 230, 230))
    text(x + 8, y + 6, 'MERKURY, CAPSIZED', 'heavy', 10, (255, 255, 255))


def art_drones(x, y, w, h):
    sky(x, y, w, h, (12, 18, 44), (40, 46, 84))
    import math
    for k, (sx, sy) in enumerate([(30, 12), (80, 30), (130, 8), (190, 26), (240, 12), (290, 30), (60, 50), (160, 52), (270, 54)]):
        line([(x + sx - 22, y + sy - 10), (x + sx, y + sy)], (255, 180, 60), 1.5)
        poly([(x + sx, y + sy), (x + sx - 6, y + sy - 1), (x + sx - 3, y + sy + 4)], (255, 220, 140))
    base = y + h
    bx = x + 6
    for k, (bw, bh) in enumerate([(30, 40), (26, 56), (38, 34), (30, 48), (44, 60), (28, 38), (36, 52), (40, 44), (30, 36)]):
        if bx + bw > x + w - 4:
            break
        col = (50, 54, 70) if k != 4 else (70, 62, 66)
        rect(bx, base - bh, bx + bw, base, fill=col)
        for wy in range(int(base - bh + 6), int(base - 4), 9):
            for wx in range(int(bx + 4), int(bx + bw - 5), 8):
                if (wx * 7 + wy * 3 + k) % 5:
                    rect(wx, wy, wx + 3, wy + 4, fill=(235, 200, 90))
        if k == 4:   # the hit block: broken roofline and fire
            poly([(bx, base - bh), (bx + 18, base - bh + 16), (bx + 30, base - bh + 4), (bx + bw, base - bh + 20),
                  (bx + bw, base - bh - 2), (bx, base - bh - 2)], (40, 46, 84))
            ell(bx + 20, base - bh + 14, 9, 7, fill=(240, 120, 30))
        bx += bw + 4
    rect(x + w - 70, y + 6, x + w - 6, y + 34, fill=(255, 255, 255), r=3)
    text(x + w - 38, y + 6.5, '186', 'black', 20, RED, 'ma')


ICON_BG = (232, 236, 240)


def art_bahrain(x, y, w, h):
    sky(x, y, w, h, (20, 26, 52), (60, 56, 80))
    for k in range(3):
        cx = x + 40 + k * 34
        rect(cx - 13, y + h - 26, cx + 13, y + h - 4, fill=(220, 220, 214))
        ell(cx, y + h - 26, 13, 4, fill=(240, 240, 234))
    for fx, fh in [(56, 16), (92, 12)]:
        poly([(x + fx - 7, y + h - 26), (x + fx, y + h - 26 - fh), (x + fx + 7, y + h - 26)], (245, 140, 40))
    line([(x + w - 10, y + 6), (x + 70, y + h - 32)], (255, 170, 60), 1.5)


def art_capitol(x, y, w, h):
    sky(x, y, w, h, (226, 234, 246), (246, 248, 252))
    cx, base = x + 46, y + h - 4
    rect(cx - 36, base - 12, cx + 36, base, fill=(250, 250, 250), outline=GREY, width=0.8)
    rect(cx - 16, base - 22, cx + 16, base - 12, fill=(250, 250, 250), outline=GREY, width=0.8)
    d.pieslice(P(cx - 14, base - 38, cx + 14, base - 8), 180, 360, fill=(250, 250, 250), outline=GREY, width=S)
    rect(cx - 1, base - 44, cx + 1, base - 36, fill=GREY)
    text(x + w - 8, y + 6, '258', 'black', 26, (30, 60, 150), 'ra')


def art_sudan(x, y, w, h):
    sky(x, y, w, h, (236, 214, 176), (246, 232, 206))
    for k, (bw, bh) in enumerate([(22, 18), (30, 26), (18, 14), (26, 22), (34, 18), (20, 24)]):
        bx = x + 6 + k * 25
        rect(bx, y + h - bh, bx + bw, y + h, fill=(196, 164, 120) if k != 3 else (150, 120, 90))
    rect(x + 82, y + h - 28, x + 108, y + h, fill=(240, 240, 240), outline=GREY, width=0.8)
    text(x + 95, y + h - 25, 'UN', 'heavy', 9, (40, 110, 190), 'ma')
    dx, dy = x + w - 40, y + 12
    poly([(dx - 16, dy), (dx + 16, dy - 3), (dx + 16, dy + 3)], (60, 60, 60))
    line([(dx - 6, dy - 8), (dx - 6, dy + 8)], (60, 60, 60), 2)


def art_hospital(x, y, w, h):
    sky(x, y, w, h, (210, 230, 214), (236, 244, 236))
    rect(x + 16, y + 14, x + 76, y + h - 2, fill=(255, 255, 255), outline=GREY, width=0.8)
    rect(x + 40, y + 20, x + 52, y + 40, fill=(200, 40, 40))
    rect(x + 36, y + 24, x + 56, y + 36, fill=(200, 40, 40))
    text(x + w - 8, y + 6, '24h+', 'black', 22, (30, 110, 60), 'ra')


def art_exam(x, y, w, h):
    rect(x, y, x + w, y + h, fill=ICON_BG)
    rect(x + 14, y + 6, x + 58, y + h - 4, fill=(255, 255, 255), outline=GREY, width=0.8)
    for i in range(4):
        line([(x + 20, y + 14 + i * 7), (x + 52, y + 14 + i * 7)], RULE, 1.5)
    ell(x + 92, y + h / 2, 17, 17, outline=(200, 40, 40), width=3)
    text(x + 92, y + h / 2 + 0.5, 'AI', 'heavy', 14, INK, 'mm')
    line([(x + 80, y + h / 2 - 12), (x + 104, y + h / 2 + 12)], (200, 40, 40), 3)


def art_ballot(x, y, w, h):
    sky(x, y, w, h, (220, 232, 240), (240, 244, 248))
    rect(x + 16, y + 18, x + 60, y + h - 2, fill=(196, 30, 40))
    rect(x + 28, y + 16, x + 48, y + 20, fill=INK)
    rect(x + 30, y + 2, x + 46, y + 18, fill=(255, 255, 255), outline=GREY, width=0.8)
    line([(x + 33, y + 10), (x + 37, y + 14), (x + 44, y + 5)], (30, 120, 64), 2)
    text(x + w - 8, y + 9, '98.79%', 'black', 18, (16, 136, 118), 'ra')


def art_power(x, y, w, h):
    sky(x, y, w, h, (24, 30, 60), (56, 60, 96))
    bx = x + 36
    line([(bx - 14, y + h), (bx, y + 6), (bx + 14, y + h)], (200, 200, 210), 2)
    line([(bx - 16, y + 16), (bx + 16, y + 16)], (200, 200, 210), 2)
    line([(bx - 10, y + 28), (bx + 10, y + 28)], (200, 200, 210), 2)
    poly([(x + 74, y + 8), (x + 64, y + 28), (x + 72, y + 28), (x + 66, y + 44), (x + 84, y + 20), (x + 75, y + 20), (x + 82, y + 8)],
         (250, 200, 60))
    text(x + w - 8, y + 10, '2h cuts', 'black', 16, (250, 200, 60), 'ra')


def art_cricket(x, y, w, h):
    rect(x, y, x + w, y + h, fill=(92, 160, 80))
    rect(x + 30, y + 8, x + 60, y + h, fill=(214, 196, 150))
    for k in range(3):
        rect(x + 40 + k * 4, y + 12, x + 41.5 + k * 4, y + 28, fill=(250, 250, 250))
    rect(x + w - 70, y + 8, x + w - 6, y + 32, fill=(20, 30, 20), r=3)
    text(x + w - 38, y + 9, '720/9', 'heavy', 16, (250, 210, 90), 'ma')


def art_plane(x, y, w, h):
    sky(x, y, w, h, (200, 222, 244), (236, 244, 252))
    line([(x + 14, y + h - 10), (x + w - 30, y + 14)], (150, 170, 200), 1.5)
    px, py = x + w - 40, y + 16
    poly([(px - 18, py + 6), (px + 14, py - 4), (px + 18, py - 2), (px - 14, py + 10)], (60, 70, 90))
    poly([(px - 4, py + 2), (px + 4, py - 12), (px + 8, py - 12), (px + 4, py + 2)], (60, 70, 90))
    text(x + 10, y + 6, 'KTM → DEL', 'heavy', 12, NAVY)


def art_tennis(x, y, w, h):
    rect(x, y, x + w, y + h, fill=(40, 90, 170))
    rect(x + 12, y + 6, x + w - 12, y + h - 6, outline=(255, 255, 255), width=1.5)
    line([(x + w / 2, y + 6), (x + w / 2, y + h - 6)], (255, 255, 255), 2)
    ell(x + 40, y + 20, 6, 6, fill=(220, 240, 60))
    text(x + w - 16, y + 12, '6-2 7-6', 'heavy', 16, (255, 255, 255), 'ra')


def art_moto(x, y, w, h):
    sky(x, y, w, h, (236, 230, 220), (220, 214, 204))
    rect(x, y + h - 12, x + w, y + h, fill=(90, 90, 96))
    ell(x + 30, y + h - 16, 8, 8, fill=INK)
    ell(x + 62, y + h - 16, 8, 8, fill=INK)
    poly([(x + 26, y + h - 20), (x + 46, y + h - 32), (x + 66, y + h - 22), (x + 40, y + h - 16)], (200, 30, 30))
    ell(x + 50, y + h - 36, 6, 6, fill=(200, 30, 30))
    text(x + w - 10, y + 2, '8', 'black', 36, (200, 30, 30), 'ra')


def art_table(x, y, w, h):
    sky(x, y, w, h, (240, 232, 214), (248, 242, 230))
    rect(x + 10, y + h - 14, x + w - 10, y + h - 8, fill=(150, 110, 70))
    for k in range(7):
        cx = x + 18 + k * 14
        ell(cx, y + h - 26, 4.5, 4.5, fill=(90 + k * 12, 70, 60) if k != 4 else (250, 250, 250))
        rect(cx - 4, y + h - 21, cx + 4, y + h - 14, fill=(80, 100, 140) if k != 4 else (250, 250, 250))
    text(x + w - 8, y + 4, '1,300', 'black', 16, (150, 100, 40), 'ra')


ART_FNS = {k[4:]: v for k, v in globals().items() if k.startswith('art_')}


def draw_art(key, x, y, w, h):
    """Draw one picture and keep only what falls inside its box (rotated pastes may spill)."""
    before = img.copy()
    ART_FNS[key](x, y, w, h)
    box = (int(x * S), int(y * S), int((x + w) * S), int((y + h) * S))
    inside = img.crop(box)
    img.paste(before)
    img.paste(inside, box[:2])

# ------------------------------------------------------------------ leads
LY = 214
LW = (W - 28 - 24) / 3
for i, L in enumerate(LEADS):
    x = 14 + i * (LW + 12)
    c = REGIONS[L['region']]
    rect(x, LY, x + LW, 446, fill=CARD, outline=RULE, width=1)
    draw_art(L['art'], x, LY, LW, 106)
    rect(x, LY, x + LW, LY + 3, fill=c)
    badge(x + 6, LY + 84, L['n'], c)
    chip(x + LW - 6, LY + 90, L['status'], STATUS[L['status']], right=True)
    text(x + 8, LY + 111, L['place'], 'heavy', 10, c)
    yy = para(x + 8, LY + 124, L['head'], 'serif', 19, LW - 16, 22, INK, 2)
    yy = para(x + 8, yy + 3, L['dek'], 'reg', 11.5, LW - 16, 14, (44, 46, 52), 4)
    text(x + 8, 432, L['src'], 'med', 9.5, GREY)

# ------------------------------------------------------------------ cards
CY = 452
CWD = (W - 28 - 5 * 6) / 6
for k, C in enumerate(CARDS):
    col, row = k % 6, k // 6
    x = 14 + col * (CWD + 6)
    y = CY + row * 134
    c = REGIONS[C['region']]
    rect(x, y, x + CWD, y + 128, fill=CARD, outline=RULE, width=1)
    draw_art(C['art'], x, y, CWD, 48)
    rect(x, y, x + CWD, y + 3, fill=c)
    badge(x + 4, y + 30, C['n'], c)
    if C['status'] != 'CONFIRMED':
        chip(x + CWD - 4, y + 33, C['status'], STATUS[C['status']], right=True)
    text(x + 6, y + 52, C['place'], 'heavy', 9, c)
    para(x + 6, y + 64, C['head'], 'serif', 12.5, CWD - 12, 14.5, INK, 3)
    text(x + 6, y + 114, C['src'], 'med', 8.5, GREY)

# ------------------------------------------------------------------ map with numbered pins
MX0, MY0, MW, MH = 14, 738, 300, 168
text(MX0, 722, 'WHERE IT HAPPENED', 'heavy', 11, NAVY)
text(MX0 + 110, 723.5, 'pins = story numbers 1-15', 'med', 9, GREY)
rect(MX0, MY0, MX0 + MW, MY0 + MH, fill=(226, 234, 242))
LON0, LON1, LAT0, LAT1 = -170, 180, -50, 78


def mp(lon, lat):
    return (MX0 + (lon - LON0) / (LON1 - LON0) * MW, MY0 + (LAT1 - lat) / (LAT1 - LAT0) * MH)


LAND = [  # rough coastlines (lon, lat), enough for a dotted locator map
    [(-168, 66), (-156, 71), (-125, 70), (-95, 72), (-80, 73), (-62, 66), (-55, 52), (-66, 45), (-75, 35), (-81, 25),
     (-90, 29), (-97, 26), (-97, 20), (-87, 21), (-83, 10), (-78, 8), (-86, 13), (-95, 16), (-105, 20), (-112, 30),
     (-117, 33), (-124, 40), (-125, 49), (-135, 58), (-150, 60), (-165, 60)],
    [(-55, 60), (-45, 60), (-20, 70), (-20, 80), (-60, 82), (-70, 77)],
    [(-80, 9), (-72, 12), (-60, 10), (-50, 0), (-35, -5), (-38, -13), (-48, -26), (-58, -35), (-65, -42), (-68, -55),
     (-75, -50), (-73, -35), (-71, -18), (-81, -5)],
    [(-10, 36), (-9, 44), (-2, 44), (-5, 48), (2, 51), (8, 54), (10, 58), (5, 62), (15, 69), (28, 71), (40, 67),
     (60, 70), (80, 73), (105, 78), (140, 72), (170, 68), (180, 65), (160, 58), (142, 52), (135, 43), (128, 35),
     (122, 30), (120, 22), (108, 20), (108, 10), (103, 1), (98, 8), (98, 16), (92, 22), (88, 22), (80, 15), (77, 8),
     (72, 20), (66, 25), (57, 25), (60, 22), (52, 16), (44, 12), (38, 20), (35, 30), (32, 31), (26, 40), (23, 36),
     (15, 38), (12, 44), (5, 43), (0, 39)],
    [(-17, 21), (-10, 35), (10, 37), (32, 31), (34, 28), (43, 12), (51, 12), (40, -3), (40, -15), (35, -25),
     (20, -35), (15, -28), (12, -15), (13, -5), (9, 4), (-8, 4), (-15, 10)],
    [(114, -22), (123, -17), (131, -12), (142, -11), (146, -19), (153, -27), (150, -37), (140, -38), (132, -32), (115, -35)],
    [(130, 31), (135, 34), (140, 36), (142, 40), (141, 45), (139, 38), (132, 34)],
    [(-6, 50), (1, 51), (-2, 56), (-5, 58), (-6, 55)],
    [(95, 5), (106, -6), (115, -8), (120, -9), (118, -3), (110, -2), (104, 2)],
    [(109, 1), (117, 7), (119, 1), (116, -4), (110, -3)],
    [(172, -34), (178, -38), (174, -41), (167, -46), (170, -44)],
    [(44, -25), (47, -25), (50, -15), (49, -12)],
]
mask = Image.new('L', (MW, MH), 0)
md = ImageDraw.Draw(mask)
for shape in LAND:
    md.polygon([(p[0] - MX0, p[1] - MY0) for p in (mp(*q) for q in shape)], fill=255)
for gy in range(2, MH, 5):
    for gx in range(2, MW, 5):
        if mask.getpixel((gx, gy)):
            ell(MX0 + gx, MY0 + gy, 1.5, 1.5, fill=(150, 160, 175))
for s in LEADS + CARDS:
    px, py = mp(*s['ll'])
    ell(px, py, 6, 6, fill=REGIONS[s['region']], outline=(255, 255, 255), width=1)
    text(px, py + 0.5, str(s['n']), 'heavy', 7.5, (255, 255, 255), 'mm')

# ------------------------------------------------------------------ briefs
BX = 330
text(BX, 722, 'ALSO ON SUNDAY 22 NOVEMBER — %d MORE STORIES' % len(BRIEFS), 'heavy', 11, NAVY)
BCW = (W - 14 - BX - 12) / 2
for k, (reg, place, body, outlet, status) in enumerate(BRIEFS):
    col, row = k // 11, k % 11
    x = BX + col * (BCW + 12)
    y = 739 + row * 15.4
    c = REGIONS[reg]
    n = 16 + k
    text(x, y, str(n), 'heavy', 10.5, c)
    xx = x + 16
    text(xx, y, place + ':', 'bold', 10.5, c)
    xx += tw(place + ': ', 'bold', 10.5)
    text(xx, y, body, 'med', 10.5, INK)
    xx += tw(body + ' ', 'med', 10.5)
    tag = outlet + (' · CLAIM' if status == 'CLAIM' else '')
    text(xx, y + 0.5, tag, 'med', 9, ORANGE if status == 'CLAIM' else GREY)
    xx += tw(tag, 'med', 9)
    assert xx <= x + BCW + 1, (body, xx - x - BCW)

# ------------------------------------------------------------------ date check and footer
rect(14, 912, W - 14, 990, fill=(253, 240, 238), outline=RED, width=1.5)
text(24, 918, 'DATE CHECK', 'heavy', 12, RED)
para(110, 918.5, 'Every story on this page happened, or was first reported, on Sunday 22 November 2026 in UTC or local '
     'time; wires and official statements read to the end of the day.', 'reg', 10.5, W - 14 - 120, 13, INK, 2)
text(24, 948, 'LEFT OUT AS EARLIER NEWS:', 'heavy', 10, RED)
para(150, 948.5, "Nigeria funeral-boat capsizing (Fri 20) · Bolsonaro taken into intensive care (Fri 20) · Brazil "
     "Tupanciretã storm (Fri 20) · 'El Chapo Isidro' captured in Sinaloa (Sat 21) · Indonesia candy-factory fire broke "
     "out (Sat 21) · Sparta II hit by drone off Finland (Sat 21) · West Bank settler arson (Sat night) · NWSL final (Sat 21)",
     'reg', 10, W - 14 - 160, 12.5, INK, 3)
x = 14
y = 996
for reg, c in REGIONS.items():
    ell(x + 4, y + 5, 4, 4, fill=c)
    text(x + 11, y, reg, 'bold', 9.5, INK)
    x += 11 + tw(reg, 'bold', 9.5) + 9
x += 6
for lab, col, desc in [('CONFIRMED', GREEN, '2+ outlets or on the record'), ('CLAIM', ORANGE, "one side's account")]:
    x += chip(x, y - 1, lab, col) + 4
    text(x, y, desc, 'reg', 9.5, INK)
    x += tw(desc, 'reg', 9.5) + 10
assert x < W - 10, x
text(14, 1010, 'Sources: Reuters, AP, AFP, EFE, Al Jazeera, The Guardian, NPR, UN News, ABC, Kyiv Post, The Standard, Focus Taiwan, '
     'Vatican News, ESPN and others named on each story (full list in FACTS.md). Pictures and map: original, drawn in code.',
     'reg', 8.5, GREY)

out = img.resize((W, H), Image.LANCZOS)
out = out.quantize(colors=240, method=Image.MEDIANCUT, dither=Image.NONE)
out.save('entry.png', optimize=True)
print('wrote entry.png', STORIES, 'stories', counts)
