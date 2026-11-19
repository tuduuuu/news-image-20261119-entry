"""Sum up 19 November 2026 world news in one image.

Pure Python standard library only. Draws a 1024x1024 newspaper
front page with a small bitmap font and writes a deterministic PNG
to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).
No network, no randomness, no timestamps in the output.
"""
import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

PAPER = (247, 243, 232)
INK = (17, 24, 39)
NAVY = (15, 42, 92)
RED = (185, 28, 28)
TEAL = (13, 110, 110)
GOLD = (180, 130, 20)
GREY = (90, 95, 105)
LIGHT = (232, 226, 210)
WHITE = (255, 255, 255)

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(px, x, y, text, scale, color):
    text = text.upper()
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    for dy in range(scale):
                        for dx in range(scale):
                            px[y + row * scale + dy][cx + col * scale + dx] = color
        cx += 6 * scale
    return cx


def wrap(text, scale, max_width):
    words = text.upper().split()
    lines = []
    line = ""
    for word in words:
        trial = word if not line else line + " " + word
        if text_width(trial, scale) <= max_width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_block(px, x, y, width, lines, scale, color, gap):
    cy = y
    for line in lines:
        draw_text(px, x, cy, line, scale, color)
        cy += 7 * scale + gap
    return cy


def fill_rect(px, x, y, w, h, color):
    for yy in range(y, y + h):
        if 0 <= yy < HEIGHT:
            row = px[yy]
            for xx in range(x, x + w):
                if 0 <= xx < WIDTH:
                    row[xx] = color


def draw_rect(px, x, y, w, h, color, thickness=2):
    fill_rect(px, x, y, w, thickness, color)
    fill_rect(px, x, y + h - thickness, w, thickness, color)
    fill_rect(px, x, y, thickness, h, color)
    fill_rect(px, x + w - thickness, y, thickness, h, color)


def draw_circle(px, cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            dx = xx - cx
            dy = yy - cy
            d2 = dx * dx + dy * dy
            if r * r - 2 * r <= d2 <= r * r:
                if 0 <= xx < WIDTH and 0 <= yy < HEIGHT:
                    px[yy][xx] = color


def draw_globe(px, cx, cy, r):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            dx = xx - cx
            dy = yy - cy
            if dx * dx + dy * dy <= r * r:
                px[yy][xx] = (70, 160, 180)
    draw_circle(px, cx, cy, r, NAVY)
    for k in range(-2, 3):
        x0 = cx + k * r // 3
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            if (x0 - cx) * (x0 - cx) + dy * dy <= r * r:
                px[yy][x0] = NAVY
    for k in range(-1, 2):
        yy = cy + k * r // 2
        for xx in range(cx - r, cx + r + 1):
            dx = xx - cx
            if dx * dx + (yy - cy) * (yy - cy) <= r * r:
                px[yy][xx] = NAVY
    fill_rect(px, cx - r, cy - 3, 2 * r, 6, GOLD)
    fill_rect(px, cx - 3, cy - r, 6, 2 * r, GOLD)


def chunk(kind, data):
    out = kind + data
    out += struct.pack(">I", zlib.crc32(out) & 0xFFFFFFFF)
    return struct.pack(">I", len(data)) + out


def write_png(path, px):
    raw = bytearray()
    for row in px:
        raw.append(0)
        for (r, g, b) in row:
            raw.extend((r, g, b))
    ihdr = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", ihdr)
    data += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


STORIES = [
    ("LEAD", "TRUMP, XI AND PUTIN MEET IN SHENZHEN",
     "FIRST-EVER THREE-WAY SUMMIT ON APEC SIDELINES. UKRAINE AND NUCLEAR ARMS ON THE TABLE AS NEW START EXPIRES."),
    ("THE HAGUE", "WORLD COURT TO RULE ON ROHINGYA GENOCIDE",
     "THE ICJ RULES TODAY ON MYANMAR. GAMBIA BROUGHT THE CASE OVER THE 2017 CRACKDOWN."),
    ("GAZA", "ISRAEL LAUNCHES GROUND OPERATION IN GAZA",
     "TROOPS MOVE INTO CENTRAL GAZA AS DOZENS FLEE. ESCALATION THREATENS CIVILIANS."),
    ("UKRAINE", "UKRAINE HITS CRIMEAN BRIDGE AGAIN",
     "THIRD STRIKE ON THE BRIDGE IN A WEEK. TRAFFIC IS SUSPENDED AFTER THE ATTACK."),
    ("ENERGY", "TANKERS BURN AFTER MINES NEAR HORMUZ",
     "THREE OIL TANKERS CATCH FIRE EAST OF THE STRAIT. IRAN STRIKES BACK IN THE GULF."),
    ("ASIA", "BANGLADESH UNREST SPREADS",
     "YUNUS FAMILY HOME IS SET ON FIRE. TROOPS DEPLOY AS VIOLENCE HITS 28 DISTRICTS."),
]


def build():
    px = [[PAPER for _ in range(WIDTH)] for _ in range(HEIGHT)]
    fill_rect(px, 0, 0, WIDTH, 118, NAVY)
    title = "WORLD NEWS"
    tw = text_width(title, 7)
    draw_text(px, (WIDTH - tw) // 2, 14, title, 7, WHITE)
    date = "THURSDAY 19 NOVEMBER 2026"
    dw = text_width(date, 3)
    draw_text(px, (WIDTH - dw) // 2, 78, date, 3, GOLD)
    fill_rect(px, 0, 118, WIDTH, 6, RED)
    sub = "THE DAY IN SIX STORIES"
    sw = text_width(sub, 2)
    draw_text(px, (WIDTH - sw) // 2, 134, sub, 2, RED)

    # Lead story, left text, right globe.
    fill_rect(px, 28, 168, WIDTH - 56, 252, WHITE)
    draw_rect(px, 28, 168, WIDTH - 56, 252, NAVY, 3)
    draw_text(px, 52, 186, "LEAD STORY  -  SHENZHEN, CHINA", 2, RED)
    lines = wrap(STORIES[0][1], 4, 560)
    draw_block(px, 52, 214, 560, lines, 4, INK, 6)
    body = wrap(STORIES[0][2], 2, 560)
    draw_block(px, 52, 214 + len(lines) * 34 + 8, 560, body, 2, GREY, 4)
    draw_globe(px, 868, 294, 78)
    draw_text(px, 812, 386, "APEC", 2, NAVY)

    # Second row: two stories.
    second = STORIES[1:3]
    for i, (tag, head, body_text) in enumerate(second):
        x = 28 + i * 488
        fill_rect(px, x, 440, 468, 218, WHITE)
        draw_rect(px, x, 440, 468, 218, NAVY, 3)
        draw_text(px, x + 20, 458, tag, 2, RED)
        lines = wrap(head, 3, 428)
        draw_block(px, x + 20, 486, 428, lines, 3, INK, 5)
        body = wrap(body_text, 2, 428)
        draw_block(px, x + 20, 486 + len(lines) * 26 + 10, 428, body, 2, GREY, 4)

    # Third row: three stories.
    third = STORIES[3:6]
    for i, (tag, head, body_text) in enumerate(third):
        x = 28 + i * 324
        fill_rect(px, x, 678, 304, 250, WHITE)
        draw_rect(px, x, 678, 304, 250, NAVY, 3)
        draw_text(px, x + 16, 694, tag, 2, RED)
        lines = wrap(head, 3, 272)
        draw_block(px, x + 16, 722, 272, lines, 3, INK, 5)
        body = wrap(body_text, 2, 272)
        draw_block(px, x + 16, 722 + len(lines) * 26 + 10, 272, body, 2, GREY, 4)

    fill_rect(px, 0, 952, WIDTH, 72, NAVY)
    foot = "19 NOVEMBER 2026  -  SIX STORIES, ONE DAY"
    fw = text_width(foot, 2)
    draw_text(px, (WIDTH - fw) // 2, 972, foot, 2, WHITE)
    foot2 = "SUMMIT IN SHENZHEN  -  COURT IN THE HAGUE  -  GAZA  -  UKRAINE  -  HORMUZ  -  BANGLADESH"
    fw2 = text_width(foot2, 1)
    draw_text(px, (WIDTH - fw2) // 2, 998, foot2, 1, GOLD)
    return px


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    px = build()
    size = write_png(path, px)
    print("wrote %s %d bytes" % (path, size))


if __name__ == "__main__":
    main()
