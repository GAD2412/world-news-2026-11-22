"""Draws entry.png: the world's news of Sunday 22 November 2026 on one 1024x1024 front page.

Run: python3 render.py  (needs Pillow and the macOS system fonts Avenir Next Condensed and Helvetica Neue).
Every story and figure is listed with its sources in FACTS.md. Drawing is deterministic: same input, same bytes.
"""
from PIL import Image, ImageDraw, ImageFont

S = 2                      # draw at 2x, then downsample for clean edges
W = H = 1024
AVC = '/System/Library/Fonts/Avenir Next Condensed.ttc'
HN = '/System/Library/Fonts/HelveticaNeue.ttc'

PAPER = (247, 244, 237)
INK = (21, 23, 28)
GREY = (92, 96, 105)
RULE = (205, 200, 190)
NAVY = (18, 33, 58)
GOLD = (233, 190, 92)

REGIONS = {  # region -> colour
    'MIDDLE EAST': (190, 52, 44),
    'EUROPE': (38, 92, 170),
    'AFRICA': (205, 125, 20),
    'AMERICAS': (120, 58, 150),
    'SOUTH ASIA': (200, 70, 130),
    'EAST ASIA': (18, 140, 120),
    'GLOBAL': (40, 120, 60),
}

_fonts = {}


def font(kind, size):
    key = (kind, size)
    if key not in _fonts:
        path, idx = {
            'heavy': (AVC, 8), 'bold': (AVC, 0), 'demi': (AVC, 2), 'med': (AVC, 5),
            'reg': (HN, 0), 'hbold': (HN, 1), 'hmed': (HN, 10), 'cblack': (HN, 9),
        }[kind]
        _fonts[key] = ImageFont.truetype(path, size * S, index=idx)
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
    words, lines, cur = s.split(), [], ''
    for w in words:
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
        d.rounded_rectangle(P(x0, y0, x1, y1), radius=r * S, fill=fill, outline=outline, width=width * S)
    else:
        d.rectangle(P(x0, y0, x1, y1), fill=fill, outline=outline, width=width * S)


def mark(x, y, sure, col):
    """Confidence mark: filled dot = confirmed by 2+ outlets, ring = one side's claim."""
    if sure:
        d.ellipse(P(x, y, x + 8, y + 8), fill=col)
    else:
        d.ellipse(P(x, y, x + 8, y + 8), outline=col, width=2 * S)


# ---------------------------------------------------------------- masthead
rect(0, 0, W, 112, fill=NAVY)
DATE_SIZE = 62
assert tw('SUNDAY 22 NOVEMBER 2026', 'heavy', DATE_SIZE) < 770
text(20, 8, 'SUNDAY 22 NOVEMBER 2026', 'heavy', DATE_SIZE, (255, 255, 255))
text(22, 84, "THE WORLD'S NEWS IN ONE IMAGE   ·   28 STORIES   ·   7 REGIONS   ·   12 FIELDS", 'demi', 17, GOLD)
# date check box
rect(800, 12, 1008, 100, fill=(28, 50, 86), outline=GOLD, width=2, r=6)
text(811, 17, 'DATE CHECK', 'heavy', 18, GOLD)
para(811, 40, 'Every story happened or was first reported on Sun 22 Nov 2026 (any time zone). Saturday-only events left out.',
     'reg', 11, 190, 14, (235, 238, 245), 4)

# ---------------------------------------------------------------- UTC timeline
TY = 128
text(16, TY - 6, 'THE DAY IN UTC', 'bold', 13, NAVY)
text(16, TY + 9, '(times approx.)', 'reg', 9, GREY)
X0, X1 = 118, 1004


def hx(h):
    return X0 + (X1 - X0) * h / 24


d.line(P(X0, TY + 14, X1, TY + 14), fill=INK, width=2 * S)
for h in range(0, 25, 3):
    d.line(P(hx(h), TY + 10, hx(h), TY + 18), fill=INK, width=S)
    text(hx(h), TY + 20, '%02d:00' % h, 'reg', 9, GREY, 'ma')
# Hong Kong polls 09:00-18:00 HKT = 01-10 UTC
rect(hx(1), TY + 11, hx(10), TY + 17, fill=REGIONS['EAST ASIA'])
EVENTS = [  # hour, label, region, label above?
    (2, 'Benghazi: warship hit', 'AFRICA', True),
    (4, 'Las Vegas GP', 'AMERICAS', False),
    (5.5, 'HK polls open 01-10', 'EAST ASIA', True),
    (11, 'Golden Horse', 'EAST ASIA', False),
    (13, 'MotoGP Portimão', 'EUROPE', True),
    (14.5, 'COP31 closes, no deal', 'GLOBAL', False),
    (17, 'Liverpool 4-0', 'EUROPE', True),
    (18.5, 'ATP Finals final', 'EUROPE', False),
    (19.5, 'US House: 258th seat', 'AMERICAS', True),
]
for h, lab, reg, up in EVENTS:
    c = REGIONS[reg]
    x = hx(h)
    d.ellipse(P(x - 4, TY + 10, x + 4, TY + 18), fill=c, outline=PAPER, width=S)
    if up:
        text(x, TY - 4, lab, 'demi', 11, c, 'ma')
    else:
        text(x, TY + 31, lab, 'demi', 11, c, 'ma')

# ---------------------------------------------------------------- lead stories
LY = 182
d.line(P(16, LY - 4, W - 16, LY - 4), fill=INK, width=2 * S)
LW = 322
LEADS = [
    dict(region='GLOBAL', tag='GLOBAL · CLIMATE · ANTALYA, TURKEY', art='cop',
         head='COP31 climate summit collapses without a deal',
         dek='After two days of overtime, the EU, UK and island states reject a final text that does not even mention '
             'fossil fuels. UN chief Guterres: "deeply disappointed". Longest climate summit on record.',
         src='UN News · NPR · Guardian · Al Jazeera · AFP'),
    dict(region='AFRICA', tag='LIBYA · RUSSIA-UKRAINE WAR · BENGHAZI', art='ship',
         head='Russian warship sinks at Benghazi after drone attack',
         dek='Suspected Ukrainian sea drones hit the navy corvette Merkury in port before dawn; satellite images show it '
             'capsized. A Malta-flagged cargo ship is also hit off Benghazi that evening.',
         src='Reuters · Guardian · Al Jazeera'),
    dict(region='MIDDLE EAST', tag='IRAN · GULF · BAHRAIN, HORMUZ', art='gulf',
         head='Bahrain: 2 wounded by Iranian strike; IRGC claims US targets',
         dek='Iran\'s Guards say they hit US Patriot radar sites in Bahrain and downed a US Predator drone near Hormuz '
             '(US: no comment). Saudi Arabia, Kuwait and Qatar condemn Iran.',
         src='ABC News · Middle East Eye · Reuters'),
]


def art_cop(x, y, w, h):
    rect(x, y, x + w, y + h, fill=(222, 236, 226))
    # globe
    cx, cy, r = x + 70, y + h / 2, 52
    d.ellipse(P(cx - r, cy - r, cx + r, cy + r), fill=(70, 140, 200))
    d.polygon(P(cx - 30, cy - 34, cx + 8, cy - 40, cx + 18, cy - 12, cx - 6, cy + 6, cx - 34, cy - 4), fill=(80, 160, 90))
    d.polygon(P(cx + 10, cy + 14, cx + 36, cy + 6, cx + 30, cy + 36, cx + 12, cy + 40), fill=(80, 160, 90))
    # thermometer
    tx = cx + r + 14
    rect(tx, cy - 44, tx + 12, cy + 26, fill=(255, 255, 255), outline=INK, width=1, r=6)
    rect(tx + 3, cy - 20, tx + 9, cy + 26, fill=(205, 50, 40))
    d.ellipse(P(tx - 4, cy + 20, tx + 16, cy + 40), fill=(205, 50, 40), outline=INK, width=S)
    # draft text with stamp
    px = x + 170
    rect(px, y + 16, px + 132, y + h - 14, fill=(255, 255, 255), outline=GREY, width=1)
    text(px + 10, y + 24, 'COP31 FINAL TEXT', 'bold', 12, INK)
    for i in range(6):
        d.line(P(px + 10, y + 46 + i * 12, px + 122 - (i % 3) * 18, y + 46 + i * 12), fill=RULE, width=2 * S)
    text(px + 10, y + 118, '"fossil fuels": 0', 'bold', 12, (190, 52, 44))
    stamp = Image.new('RGBA', (150 * S, 46 * S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rounded_rectangle((2 * S, 2 * S, 148 * S, 44 * S), radius=6 * S, outline=(200, 40, 40, 235), width=4 * S)
    sd.text((75 * S, 23 * S), 'NO DEAL', font=font('heavy', 30), fill=(200, 40, 40, 235), anchor='mm')
    stamp = stamp.rotate(14, resample=Image.BICUBIC, expand=True)
    img.paste(stamp, (int((px - 14) * S), int((y + 36) * S)), stamp)


def art_ship(x, y, w, h):
    rect(x, y, x + w, y + h, fill=(214, 228, 240))
    text(x + 10, y + 8, 'BENGHAZI PORT, LIBYA', 'bold', 12, NAVY)
    # pier
    rect(x, y + h - 52, x + 92, y + h - 34, fill=(150, 145, 135))
    # water
    wy = y + h - 56
    rect(x + 92, wy, x + w, y + h, fill=(60, 110, 170))
    rect(x, y + h - 34, x + 92, y + h, fill=(60, 110, 170))
    # capsized hull, bow up
    hull = Image.new('RGBA', (200 * S, 70 * S), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hull)
    hd.polygon([(0, 20 * S), (170 * S, 20 * S), (198 * S, 4 * S), (186 * S, 46 * S), (14 * S, 46 * S)], fill=(95, 100, 108, 255))
    hd.rectangle((50 * S, 4 * S, 110 * S, 20 * S), fill=(120, 126, 134, 255))
    hd.text((120 * S, 25 * S), 'MERKURY', font=font('bold', 13), fill=(240, 240, 240, 255))
    hull = hull.rotate(-24, resample=Image.BICUBIC, expand=True)
    img.paste(hull, (int((x + 96) * S), int((wy - 58) * S)), hull)
    # waterline over the sunk part
    rect(x + 92, wy + 18, x + w, y + h, fill=(60, 110, 170))
    for i in range(4):
        yy = wy + 26 + i * 9
        d.arc(P(x + 110 + i * 30, yy, x + 150 + i * 30, yy + 10), 200, 340, fill=(200, 220, 240), width=2 * S)
    # smoke
    for i, (sx, sy, r) in enumerate([(200, 40, 14), (214, 28, 17), (232, 18, 19)]):
        d.ellipse(P(x + sx - r, y + sy - r, x + sx + r, y + sy + r), fill=(150, 150, 155))
    # drones
    for k in range(3):
        dx, dy = x + 20 + k * 22, y + h - 26 + (k % 2) * 6
        d.polygon(P(dx, dy, dx + 16, dy - 3, dx + 16, dy + 3), fill=(30, 30, 30))
    text(x + 10, y + h - 18, 'sea drones', 'reg', 10, (255, 255, 255))


def art_gulf(x, y, w, h):
    rect(x, y, x + w, y + h, fill=(110, 165, 210))
    sand = (230, 214, 178)
    # Iran coast (north-east)
    d.polygon(P(x, y, x + w, y, x + w, y + 74, x + 262, y + 62, x + 226, y + 56, x + 170, y + 34, x + 110, y + 22, x + 40, y + 12, x, y + 10), fill=sand)
    # Arabia (south-west) with Qatar bump and Musandam tip
    d.polygon(P(x, y + 58, x + 40, y + 70, x + 66, y + 96, x + 92, y + 92, x + 96, y + 76, x + 112, y + 74, x + 116, y + 102,
                x + 160, y + 116, x + 210, y + 110, x + 236, y + 92, x + 246, y + 70, x + 258, y + 86, x + 270, y + 112,
                x + w, y + 120, x + w, y + h, x, y + h), fill=sand)
    text(x + 150, y + 6, 'IRAN', 'heavy', 18, (120, 90, 50))
    text(x + 20, y + h - 28, 'SAUDI ARABIA', 'bold', 12, (120, 90, 50))
    text(x + 96, y + 104, 'QATAR', 'bold', 10, (120, 90, 50))
    # Bahrain
    bx, by = x + 80, y + 82
    d.ellipse(P(bx - 5, by - 5, bx + 5, by + 5), fill=(190, 52, 44), outline=(255, 255, 255), width=S)
    text(bx - 62, by - 26, 'BAHRAIN', 'heavy', 12, (190, 52, 44))
    text(bx - 62, by - 13, '2 wounded', 'bold', 11, INK)
    # strike arrow from Iran
    d.line(P(x + 150, y + 36, bx + 8, by - 6), fill=(190, 52, 44), width=3 * S)
    d.polygon(P(bx + 6, by - 4, bx + 20, by - 4, bx + 13, by - 16), fill=(190, 52, 44))
    # Hormuz
    hx_, hy = x + 252, y + 70
    d.ellipse(P(hx_ - 16, hy - 16, hx_ + 16, hy + 16), outline=INK, width=2 * S)
    text(hx_, hy + 18, 'HORMUZ', 'heavy', 11, INK, 'ma')
    text(hx_ - 4, hy + 32, 'drone claim', 'reg', 10, INK, 'ma')


ARTS = {'cop': art_cop, 'ship': art_ship, 'gulf': art_gulf}
for i, L in enumerate(LEADS):
    x = 16 + i * (LW + 12)
    c = REGIONS[L['region']]
    rect(x, LY, x + LW, LY + 4, fill=c)
    text(x, LY + 8, L['tag'], 'bold', 11, c)
    ARTS[L['art']](x, LY + 24, LW, 140)
    yy = para(x, LY + 168, L['head'], 'heavy', 23, LW, 25, INK, 2)
    yy = para(x, yy + 3, L['dek'], 'reg', 12, LW, 15, (40, 42, 48), 4)
    mark(x, yy + 4, True, c)
    text(x + 12, yy + 2, L['src'], 'med', 10, GREY)

# ---------------------------------------------------------------- cards
CY = 492
d.line(P(16, CY - 6, W - 16, CY - 6), fill=INK, width=2 * S)
CW, CH, CG = 191.2, 122, 6
CARDS = [
    ('EUROPE', 'UKRAINE · WAR', '14+', 'killed', 'Russian strikes hit Kyiv region; Dymer apartment block partly collapses', True),
    ('AFRICA', 'SUDAN · WAR', '4', 'killed', 'RSF drones hit Khartoum area; a UN building damaged', True),
    ('AFRICA', 'DR CONGO · HEALTH', '24h+', 'trapped', 'WHO: fighting near Ituri hospital stalls Ebola response', True),
    ('AMERICAS', 'USA · POLITICS', '258', 'House seats', 'Democrats win biggest House majority since 1992 after N. Carolina recount', True),
    ('EAST ASIA', 'S. KOREA · EDUCATION', 'AI', 'exam scandal', 'Education minister Choi Kyo-jin resigns over AI cheating in college exam', True),
    ('EAST ASIA', 'HONG KONG · ELECTION', '98.8%', 'turnout', 'Election Committee polls: 5,640 of 5,709 voters cast ballots', True),
    ('MIDDLE EAST', 'ISRAEL · POLITICS', 'TALKS END', 'no deal', "Netanyahu's Likud and Eisenkot's Yashar end unity-government talks", True),
    ('EUROPE', 'TENNIS · TURIN', '6-2 7-6', '', 'Alcaraz beats world No 1 Zverev for first ATP Finals title', True),
    ('EUROPE', 'MOTOGP · PORTUGAL', '8th', 'title', 'Marc Márquez clinches 8th premier-class crown, level with Agostini', True),
    ('EUROPE', 'FOOTBALL · ANFIELD', '4-0', '', "Liverpool rout 10-man Man United in Pochettino's first game", True),
]
for k, (reg, tag, fig, unit, head, sure) in enumerate(CARDS):
    col, row = k % 5, k // 5
    x = 16 + col * (CW + CG)
    y = CY + row * (CH + 8)
    c = REGIONS[reg]
    rect(x, y, x + CW, y + CH, fill=(255, 255, 255), outline=RULE, width=1)
    rect(x, y, x + CW, y + 4, fill=c)
    text(x + 8, y + 9, tag, 'bold', 10, c)
    fsize = 30 if tw(fig, 'heavy', 30) < CW - 20 else 24
    text(x + 8, y + 20, fig, 'heavy', fsize, c)
    if unit:
        text(x + 12 + tw(fig, 'heavy', fsize), y + 20 + fsize * 0.62, unit, 'demi', 12, GREY)
    para(x + 8, y + 60, head, 'bold', 14, CW - 16, 16, INK, 3)

# ---------------------------------------------------------------- briefs
BY = 752
d.line(P(16, BY - 4, W - 16, BY - 4), fill=INK, width=2 * S)
text(16, BY + 1, 'ALSO ON 22 NOVEMBER', 'heavy', 14, NAVY)
BRIEFS = [
    ('EUROPE', 'Ukraine:', 'Zelenskyy says Russia fired ~2,700 drones and 165 missiles in a week; asks US for Patriots', True),
    ('AFRICA', 'Libya:', 'Malta-flagged merchant ship hit by sea drones off Benghazi; crew rescued', True),
    ('MIDDLE EAST', 'Hormuz:', 'IRGC says 2 tankers hit sea mines; UKMTO probes tanker incident in Gulf of Oman', False),
    ('MIDDLE EAST', 'Iran:', 'state TV shows a dual-missile launcher in an underground "missile city"', True),
    ('MIDDLE EAST', 'Yemen:', 'Saudi coalition downs Houthi drone and missile; Houthis say 6 hurt in Sanaa strike', True),
    ('GLOBAL', 'Weapons:', 'Red Cross warns it will soon be too late to regulate autonomous weapons', True),
    ('AMERICAS', 'USA:', 'spy chief Jay Clayton defends Trump calling Putin "my friend"', True),
    ('AMERICAS', 'AI chips:', 'US lawmakers on Sunday TV demand answers on how top Nvidia chips reached China', True),
    ('SOUTH ASIA', 'Bangladesh:', 'garment workers in Gazipur try to block Dhaka highway in wage protest', True),
    ('EAST ASIA', 'Taiwan:', 'Hong Kong film "We Are Born Good" wins best feature at Golden Horse Awards', True),
    ('AMERICAS', 'F1:', 'Verstappen wins Las Vegas GP (Sat night local) after 35 lead changes', True),
    ('AMERICAS', 'Mexico:', 'NFL returns to Mexico City: 49ers beat Vikings 35-10', True),
    ('EUROPE', 'Chess:', 'Gukesh v Sindarov world title match opens in Geneva; game 1 on 24 Nov', True),
    ('MIDDLE EAST', 'Gulf:', 'Saudi Arabia, Kuwait and Qatar condemn Iran over Bahrain strike', True),
    ('MIDDLE EAST', 'US-Iran:', 'Trump says he is "inclined" to resume strikes after New Year if there is no deal', True),
]
BW = 322
for k, (reg, lead, body, sure) in enumerate(BRIEFS):
    col, row = k // 5, k % 5
    x = 16 + col * (BW + 12)
    y = BY + 22 + row * 42
    c = REGIONS[reg]
    mark(x, y + 4, sure, c)
    lead_w = tw(lead + ' ', 'hbold', 12)
    first = wrap(body, 'reg', 12, BW - 14 - lead_w)
    text(x + 13, y, lead, 'hbold', 12, c)
    text(x + 13 + lead_w, y, first[0], 'reg', 12, INK)
    rest = ' '.join(body.split()[len(first[0].split()):])
    if rest:
        para(x + 13, y + 15, rest, 'reg', 12, BW - 14, 15, INK, 1)

# ---------------------------------------------------------------- footer
FY = 984
d.line(P(16, FY, W - 16, FY), fill=INK, width=S)
x = 16
for reg, c in REGIONS.items():
    d.ellipse(P(x, FY + 9, x + 9, FY + 18), fill=c)
    text(x + 12, FY + 6, reg, 'bold', 11, INK)
    x += 12 + tw(reg, 'bold', 11) + 14
mark(x + 6, FY + 9, True, INK)
text(x + 18, FY + 6, 'confirmed by 2+ outlets', 'reg', 10, INK)
x += 18 + tw('confirmed by 2+ outlets', 'reg', 10) + 10
mark(x, FY + 9, False, INK)
text(x + 12, FY + 6, 'one side\'s claim', 'reg', 10, INK)
text(16, FY + 24, 'Sources: Reuters, AP, AFP, Al Jazeera, The Guardian, NPR, UN News, ABC News, Kyiv Post, The Standard (HK), '
     'Focus Taiwan, TBS (Dhaka), Middle East Eye. Full list in FACTS.md.', 'reg', 10, GREY)

out = img.resize((W, H), Image.LANCZOS)
out = out.quantize(colors=128, method=Image.MEDIANCUT, dither=Image.NONE)
out.save('entry.png', optimize=True)
print('wrote entry.png')
