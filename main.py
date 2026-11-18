# news-image-20261117 — Sum up 17 November 2026's world news in one image.
#
# A deterministic, network-free program: it draws a 1024x1024 newspaper-style
# infographic with Pillow and writes it to /output/entry.png.
# Running it twice produces byte-identical output (fixed strings, fixed fonts,
# no timestamps, no randomness, no network).
#
# Run:  python3 main.py
# Requires: Pillow (PIL). Standard library otherwise.

import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

PAPER = (247, 243, 234)      # warm newsprint
INK = (17, 24, 39)
NAVY = (30, 58, 95)
NAVY_DARK = (23, 45, 76)
RED = (185, 28, 28)
GOLD = (180, 83, 9)
GREY = (100, 106, 118)
CARD = (255, 255, 255)
LINE = (203, 204, 198)
SKY = (214, 228, 240)
SEA = (96, 138, 170)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
F_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
F_REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_bridge(draw, x0, y0, x1, y1):
    """Stylised Kerch Bridge with a collapsed middle span."""
    draw.rectangle([x0, y0, x1, y1], fill=SKY)
    # sun
    draw.ellipse([x1 - 52, y0 + 10, x1 - 18, y0 + 44], fill=(240, 196, 90))
    # smoke from the broken span
    cx = (x0 + x1) // 2
    draw.ellipse([cx - 15, y0 + 66, cx + 15, y0 + 96], fill=(120, 120, 118))
    draw.ellipse([cx + 8, y0 + 56, cx + 28, y0 + 76], fill=(140, 140, 138))
    # sea
    draw.rectangle([x0, y1 - 34, x1, y1], fill=SEA)
    # caption strip at the bottom of the illustration
    draw.rectangle([x0, y1 - 24, x1, y1], fill=(23, 45, 76))
    # bridge deck: two standing spans, gap in the middle
    deck_y = y1 - 52
    draw.rectangle([x0 + 8, deck_y, cx - 26, deck_y + 10], fill=INK)
    draw.rectangle([cx + 26, deck_y, x1 - 8, deck_y + 10], fill=INK)
    # fallen span, tilted into the water
    draw.polygon([(cx - 22, deck_y + 2), (cx + 24, deck_y + 16),
                  (cx + 20, deck_y + 26), (cx - 26, deck_y + 12)], fill=(90, 95, 105))
    # pylons
    for px in (x0 + 34, x1 - 40):
        draw.rectangle([px, y0 + 52, px + 8, deck_y], fill=INK)
        draw.line([px + 4, y0 + 52, cx - 26, deck_y], fill=INK, width=2)
        draw.line([px + 4, y0 + 52, cx + 26, deck_y], fill=INK, width=2)
    # caption
    cap = font(F_REG, 13)
    draw.text((x0 + 6, y1 - 20), "The Kerch Bridge after the strike",
              font=cap, fill=(255, 255, 255))


STORIES = [
    ("ASIA SUMMIT", "Trump lands in Manila; Xi\u2013Putin talks ahead",
     "Trump opens a three-day Asia trip at the ASEAN summit. A trilateral "
     "with Xi Jinping and Vladimir Putin is set for Shenzhen on 19 Nov, "
     "focused on nuclear stability and Ukraine."),
    ("GULF ON EDGE", "Tankers hit by mines in the Strait of Hormuz",
     "Iran's Revolutionary Guards say two tankers struck mines and caught "
     "fire. Iran also fired drones at a US radar base in Bahrain, and US "
     "intelligence warns of a possible dirty-bomb plot in Washington."),
    ("SPACE", "Vulcan failure destroys 40 Amazon satellites",
     "A ULA Vulcan rocket failed about ten minutes after launching from "
     "Cape Canaveral, losing its payload of 40 Amazon Leo internet "
     "satellites bound for orbit."),
    ("MARKETS", "JPMorgan blames a bug, not hackers, for outage",
     "A software bug slowed online banking, branches and Zelle payments on "
     "Monday, the bank says. Nvidia reports after the close \u2014 its first "
     "earnings since Jensen Huang stepped down."),
    ("MIDDLE EAST", "UK sanctions firms building settlements",
     "Britain sanctions eight Israeli companies building in the occupied "
     "West Bank. Settlers killed a 72-year-old woman near Jericho, and "
     "Netanyahu's camp faces claims over election-day arrests."),
    ("ASIA & BEYOND", "Japan scrambles jets as Russian planes intrude",
     "Japan launched fighter jets after two suspected Russian aircraft "
     "violated its airspace. In Yemen, Houthis advance as government "
     "troops retreat from the Red Sea coast."),
]

TICKER = ("ALSO TODAY:  D\u00e9pardieu pleads guilty to sexual assault and drops his "
         "appeal  \u2022  Five European states plan a joint Rwanda deportation hub  "
         "\u2022  EU charges Temu over illegal goods  \u2022  NYC Mayor Mamdani "
         "disbands protest police unit  \u2022  Brent crude $92.76 a barrel")


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead -------------------------------------------------------
    d.rectangle([0, 0, W, 96], fill=NAVY)
    d.rectangle([0, 96, W, 100], fill=GOLD)
    mast = font(F_BOLD, 40)
    d.text((28, 22), "THE WORLD IN ONE IMAGE", font=mast, fill=(255, 255, 255))
    date_f = font(F_BOLD, 20)
    date_txt = "TUESDAY  \u00b7  17 NOVEMBER 2026"
    d.text((W - 28 - d.textlength(date_txt, font=date_f), 34),
           date_txt, font=date_f, fill=(240, 196, 90))

    # ---- lead story -----------------------------------------------------
    lx, ly = 28, 116
    kick = font(F_BOLD, 16)
    d.text((lx, ly), "LEAD STORY  \u2014  WAR IN EUROPE", font=kick, fill=RED)
    head = font(F_BOLD, 46)
    d.text((lx, ly + 28), "UKRAINE SMASHES", font=head, fill=INK)
    d.text((lx, ly + 80), "THE KERCH BRIDGE", font=head, fill=INK)
    deck = font(F_REG, 16)
    deck_lines = wrap(
        d,
        "A road span collapses after an overnight strike Zelenskyy calls an "
        "\u201c unprecedented operation\u201d. The Kremlin vows to rebuild; "
        "Moscow claims 1,400+ Ukrainian drones downed.",
        deck, 640)
    y = ly + 142
    for line in deck_lines:
        d.text((lx, y), line, font=deck, fill=(51, 58, 70))
        y += 24

    # bridge illustration, right of the lead text
    draw_bridge(d, 700, 118, 996, 330)

    d.line([28, 344, 996, 344], fill=INK, width=2)

    # ---- story grid -----------------------------------------------------
    gx, gy = 28, 358
    col_w, row_h, gap = 476, 164, 16
    kicker_f = font(F_BOLD, 13)
    head_f = font(F_BOLD, 19)
    body_f = font(F_REG, 13)
    for i, (kicker, headline, body) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x0 = gx + col * (col_w + gap)
        y0 = gy + row * (row_h + gap)
        d.rectangle([x0, y0, x0 + col_w, y0 + row_h], fill=CARD, outline=LINE, width=1)
        # number badge
        d.ellipse([x0 + 12, y0 + 12, x0 + 38, y0 + 38], fill=NAVY)
        num_f = font(F_BOLD, 15)
        n = str(i + 1)
        d.text((x0 + 25 - d.textlength(n, font=num_f) / 2, y0 + 16),
               n, font=num_f, fill=(255, 255, 255))
        d.text((x0 + 48, y0 + 14), kicker, font=kicker_f, fill=RED)
        hl = wrap(d, headline, head_f, col_w - 24)
        hy = y0 + 42
        for line in hl[:2]:
            d.text((x0 + 12, hy), line, font=head_f, fill=INK)
            hy += 24
        bl = wrap(d, body, body_f, col_w - 24)
        by = hy + 4
        for line in bl[:4]:
            d.text((x0 + 12, by), line, font=body_f, fill=(51, 58, 70))
            by += 19

    # ---- ticker ---------------------------------------------------------
    ty = 884
    d.rectangle([0, ty, W, ty + 68], fill=NAVY_DARK)
    tick_f = font(F_REG, 15)
    tick_lines = wrap(d, TICKER, tick_f, W - 56)
    yy = ty + 10
    for line in tick_lines:
        d.text((28, yy), line, font=tick_f, fill=(255, 255, 255))
        yy += 20

    # ---- footer ---------------------------------------------------------
    foot_f = font(F_REG, 13)
    foot = ("Sources: BBC \u00b7 Reuters \u00b7 AP \u00b7 Al Jazeera \u00b7 Just Security \u2014 "
            "summary of verified reports published 17 November 2026.")
    d.text(((W - d.textlength(foot, font=foot_f)) / 2, 964), foot,
           font=foot_f, fill=GREY)
    foot2 = "Built for make.fun bounty news-image-20261117  \u00b7  One image, one day of world news."
    d.text(((W - d.textlength(foot2, font=foot_f)) / 2, 986), foot2,
           font=foot_f, fill=GREY)

    return img


def main():
    img = build()
    out = "/output/entry.png"
    try:
        os.makedirs("/output", exist_ok=True)
    except OSError:
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "output", "entry.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out, format="PNG", optimize=True)
    size = os.path.getsize(out)
    assert img.size == (1024, 1024), img.size
    assert size <= 1024 * 1024, size
    with open(out, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    print(f"wrote {out} ({img.size[0]}x{img.size[1]}, {size} bytes, sha256 {digest})")


if __name__ == "__main__":
    main()
