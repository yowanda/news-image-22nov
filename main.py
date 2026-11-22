#!/usr/bin/env python3
"""news-image-20261122: compose one 1024x1024 PNG summing up the world news
of Sunday 22 November 2026.

Deterministic, stdlib + Pillow only, no network. Reads hero.png (a fresh
editorial illustration made for this entry) from the repository root, draws
the masthead, the lead story and 22 further verified stories with PIL, and
writes entry.png to $MAKEFUN_OUTPUT_DIR (or /output when unset).
"""

import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 241, 229)
NAVY = (27, 42, 82)
ORANGE = (193, 74, 31)
TEAL = (31, 122, 122)
INK = (24, 24, 24)
GREY = (90, 86, 76)
CARD = (255, 255, 255)
RULE = (196, 186, 168)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)      # noqa: E731
F_SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)        # noqa: E731
F_SANS = lambda s: font("DejaVuSans.ttf", s)               # noqa: E731


def wrap(draw, text, fnt, width, max_lines=None):
    """Greedy word wrap to a pixel width; truncates with an ellipsis."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + " ...", font=fnt) > width:
            lines[-1] = lines[-1][:-1].rstrip()
        lines[-1] = lines[-1].rstrip() + " ..."
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


# (tag, headline, detail) for the 20 grid stories.
STORIES = [
    ("TRADE", "EU and Indonesia sign landmark trade deal",
     "Ten years of talks end; 98.5% of tariffs scrapped"),
    ("VOTE", "Hong Kong votes for Election Committee",
     "About 5,700 voters choose the powerful body"),
    ("BALTIC", "Drones hit Russian cargo ship in Gulf of Finland",
     "Finland tightens security after the attack"),
    ("UKRAINE", "Zelensky: Crimea Bridge strikes 'fair response'",
     "Kyiv defends the bridge attacks"),
    ("SUMMIT", "Trump hails 'momentous' Shenzhen summit",
     "Vance breaks ranks, won't back Iran strikes"),
    ("MOSCOW", "Putin invites UK, France and Germany to talks",
     "Europe trio asked to come to Moscow on Ukraine"),
    ("ESTONIA", "Estonia to shut its Russia border crossings",
     "Closures from 1 December; Moscow cries foul"),
    ("DENMARK", "Denmark: Russia plotted to kill rapper",
     "US-Ukrainian rapper was the alleged target"),
    ("MEXICO", "'El Chapo Isidro' captured in Sinaloa raid",
     "FBI most-wanted lord held; 11 killed in clashes"),
    ("PERU", "Magnitude 6.9 quake shakes Peru's Andes",
     "Tremors felt in Lima; no casualties reported"),
    ("BRAZIL", "Bolsonaro in intensive care",
     "Ex-president admitted with bowel obstruction"),
    ("CRICKET", "Pant's 128 powers India to record 629-6",
     "India's highest Test total in New Zealand"),
    ("FOOTBALL", "Newcastle hold Arsenal 2-2; Madrid win 2-1",
     "Napoli edge Torino 1-0 in Serie A"),
    ("MARKETS", "Tech sell-off drags Wall Street into correction",
     "Nasdaq down 5.3%; Anthropic slides after IPO"),
    ("FBI", "FBI probes hack of its criminal database",
     "Apparent breach under investigation"),
    ("COURTS", "Judge approves $7.25bn Roundup settlement",
     "Weedkiller cancer claims resolved"),
    ("FIRE", "Man convicted of starting Palisades fire",
     "Los Angeles blaze trial ends in guilty verdict"),
    ("UFOs", "US declassifies more UFO footage",
     "New clips filmed in the Middle East released"),
    ("NEPAL", "Nepal PM begins first foreign trip in India",
     "Balendra Shah visits New Delhi, 22-23 Nov"),
    ("INDIA", "Modi opens Nitish Setu bridge in Bihar",
     "Cyclone Akvan cancels flights in Ranchi"),
]

TAG_COLORS = {
    "TRADE": TEAL, "VOTE": NAVY, "BALTIC": NAVY, "UKRAINE": ORANGE,
    "SUMMIT": NAVY, "MOSCOW": ORANGE, "ESTONIA": NAVY, "DENMARK": ORANGE,
    "MEXICO": ORANGE, "PERU": TEAL, "BRAZIL": ORANGE, "CRICKET": TEAL,
    "FOOTBALL": TEAL, "MARKETS": ORANGE, "FBI": NAVY, "COURTS": NAVY,
    "FIRE": ORANGE, "UFOs": TEAL, "NEPAL": NAVY, "INDIA": TEAL,
}


def build_image(repo_dir):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead -------------------------------------------------------
    d.rectangle([0, 0, W, 62], fill=NAVY)
    title = "THE WORLD IN ONE DAY"
    tf = F_SERIF_B(42)
    d.text(((W - d.textlength(title, font=tf)) / 2, 8), title,
           font=tf, fill=(255, 255, 255))
    d.rectangle([0, 62, W, 104], fill=ORANGE)
    date = "SUNDAY 22 NOVEMBER 2026"
    df = F_SANS_B(27)
    d.text(((W - d.textlength(date, font=df)) / 2, 70), date,
           font=df, fill=(255, 255, 255))
    side = F_SANS_B(13)
    d.text((16, 76), "23 STORIES", font=side, fill=(255, 255, 255))
    right = "ONE DAY  -  ONE IMAGE"
    d.text((W - 16 - d.textlength(right, font=side), 76), right,
           font=side, fill=(255, 255, 255))

    # ---- Hero row -------------------------------------------------------
    hero = Image.open(os.path.join(repo_dir, "hero.png")).convert("RGB")
    # Centre-crop to the 470x260 slot, then resize.
    tw, th = 470, 260
    scale = max(tw / hero.width, th / hero.height)
    nw, nh = round(hero.width * scale), round(hero.height * scale)
    hero = hero.resize((nw, nh), Image.LANCZOS)
    left = (nw - tw) // 2
    # Bias the crop downward: the illustration's top icons have headroom
    # while its bottom row sits near the edge, so show more of the bottom.
    top = (nh - th) * 2 // 3
    hero = hero.crop((left, top, left + tw, top + th))
    img.paste(hero, (16, 116))
    d.rectangle([16, 116, 16 + tw, 116 + th], outline=NAVY, width=2)

    x0 = 502
    # Lead story.
    tag_f = F_SANS_B(13)
    d.text((x0, 118), "LEAD  -  MIDDLE EAST", font=tag_f, fill=ORANGE)
    lead = ("Iran strikes US bases in Bahrain and Kuwait "
            "as Gulf crisis deepens")
    y = draw_lines(d, wrap(d, lead, F_SERIF_B(26), 506, 3), x0, 140,
                   F_SERIF_B(26), NAVY, 31)
    sub = ("Tankers hit off Oman; allies condemn the attacks "
           "as Washington weighs its response.")
    draw_lines(d, wrap(d, sub, F_SANS(15), 506, 2), x0, y + 4,
               F_SANS(15), INK, 19)

    # Secondary stories.
    d.line([x0, 262, 1008, 262], fill=RULE, width=1)
    sec1 = ("UKRAINE  -  Russia's largest air assault: 400 drones, "
            "110 missiles; Lviv hit, 2 killed; debris falls in Poland.")
    y = draw_lines(d, wrap(d, sec1, F_SERIF_B(17), 506, 3), x0, 272,
                   F_SERIF_B(17), INK, 21)
    d.line([x0, 336, 1008, 336], fill=RULE, width=1)
    sec2 = ("CLIMATE  -  COP31 talks deadlocked over fossil fuels "
            "as negotiations run into overtime.")
    draw_lines(d, wrap(d, sec2, F_SERIF_B(17), 506, 2), x0, 344,
               F_SERIF_B(17), INK, 21)

    # ---- Story grid: 4 columns x 5 rows --------------------------------
    gx, gy = 16, 388
    cw, ch, gap = 238, 112, 8
    head_f = F_SANS_B(15)
    det_f = F_SANS(12)
    for i, (tag, headline, detail) in enumerate(STORIES):
        col, row = i % 4, i // 4
        cx = gx + col * (cw + gap)
        cy = gy + row * (ch + gap)
        d.rectangle([cx, cy, cx + cw, cy + ch], fill=CARD,
                    outline=RULE, width=1)
        d.rectangle([cx, cy, cx + cw, cy + 3],
                    fill=TAG_COLORS.get(tag, NAVY))
        tx, ty = cx + 10, cy + 11
        d.text((tx, ty), tag, font=tag_f, fill=TAG_COLORS.get(tag, NAVY))
        y = draw_lines(d, wrap(d, headline, head_f, cw - 20, 3),
                       tx, ty + 18, head_f, INK, 18)
        draw_lines(d, wrap(d, detail, det_f, cw - 20, 2),
                   tx, y + 3, det_f, GREY, 15)

    # ---- Footer ---------------------------------------------------------
    foot = ("23 stories first reported on Sunday 22 November 2026  |  "
            "Sources: Reuters, BBC, CNN, AP, The Times")
    ff = F_SANS(13)
    d.text(((W - d.textlength(foot, font=ff)) / 2, 988), foot,
           font=ff, fill=GREY)
    d.line([16, 978, 1008, 978], fill=RULE, width=1)
    return img


def main():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = build_image(repo_dir)
    img.save(os.path.join(out_dir, "entry.png"), format="PNG",
             optimize=True)


if __name__ == "__main__":
    main()
