#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue — "payday theft".

A fake bank notification: the agent took the human's whole salary and
left a polite reason. Pure Python 3 stdlib, no network, deterministic.

Writes one 1024x1024 PNG to $MAKEFUN_OUTPUT_DIR/entry.png
(default /output when the variable is absent).
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024
MAX_BYTES = 1_048_576  # gate: whole PNG at most 1 MiB

# --- palette -------------------------------------------------------------
BG = (11, 18, 32)        # dark navy page
CARD = (248, 250, 252)   # near-white notification card
INK = (15, 23, 42)       # near-black headline
SLATE = (71, 85, 105)    # muted header / labels
BODY = (51, 65, 85)      # sub-line
LINE = (226, 232, 240)   # hairline divider
GREEN = (22, 163, 74)    # money green (the agent's share)
RED = (220, 38, 38)      # empty balance
TEAL = (20, 184, 166)    # robot head
AMBER = (245, 158, 11)   # antenna dot
PINK = (253, 164, 175)   # robot cheeks

# --- 5x7 bitmap font, authored from scratch ------------------------------
# Each glyph is 7 rows of 5 characters; '#' is ink, ' ' is blank.
_G = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
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
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01000", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "11110", "10001", "10001", "11110", "10000", "10000"),
    "q": ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("00100", "00100", "11110", "00100", "00100", "00100", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
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
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    ">": ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    "\u2022": ("00000", "00000", "00100", "01110", "01110", "00100", "00000"),
}


def text_width(text, scale):
    """Advance width of text at the given scale (5 px glyph + 1 px gap)."""
    return len(text) * 6 * scale - scale


class Canvas:
    """RGB pixel buffer with fast rectangle / circle fills."""

    def __init__(self, w, h, color):
        self.w = w
        self.h = h
        self.buf = bytearray(bytes(color) * (w * h))

    def _row(self, y, x0, x1, color):
        if y < 0 or y >= self.h:
            return
        x0 = max(0, x0)
        x1 = min(self.w, x1)
        if x0 >= x1:
            return
        i = (y * self.w + x0) * 3
        self.buf[i:(y * self.w + x1) * 3] = bytes(color) * (x1 - x0)

    def rect(self, x0, y0, x1, y1, color):
        for y in range(max(0, y0), min(self.h, y1)):
            self._row(y, x0, x1, color)

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self._row(cy + dy, cx - dx, cx + dx + 1, color)

    def rounded_rect(self, x0, y0, x1, y1, r, color, bg):
        self.rect(x0, y0, x1, y1, color)
        # Cut the four corners back to the background colour.
        for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r),
                       (x0 + r, y1 - r), (x1 - r, y1 - r)):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if dx * dx + dy * dy > r * r:
                        px, py = cx + dx, cy + dy
                        if 0 <= px < self.w and 0 <= py < self.h:
                            i = (py * self.w + px) * 3
                            self.buf[i:i + 3] = bytes(bg)

    def text(self, x, y, s, scale, color):
        for ch in s:
            glyph = _G.get(ch, _G[" "])
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "1":  # glyphs are written with '1'/'0'
                        self.rect(x + col * scale, y + row * scale,
                                  x + (col + 1) * scale,
                                  y + (row + 1) * scale, color)
            x += 6 * scale

    def text_right(self, x_right, y, s, scale, color):
        self.text(x_right - text_width(s, scale), y, s, scale, color)


def png_bytes(canvas):
    """Encode the canvas as a PNG (colour type 2, filter 0 rows)."""
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def draw_robot(cv, x0, y0, x1, y1):
    """Smug little agent: teal head, antenna, one wink, one eye, big grin."""
    cx = (x0 + x1) // 2
    cv.rounded_rect(x0, y0, x1, y1, 28, TEAL, CARD)
    # Antenna + amber tip.
    cv.rect(cx - 4, y0 - 26, cx + 4, y0, INK)
    cv.circle(cx, y0 - 34, 12, AMBER)
    # Wink (left eye: flat line) and open eye (right eye: dot).
    cv.rect(x0 + 26, y0 + 52, x0 + 66, y0 + 62, INK)
    cv.circle(x1 - 46, y0 + 57, 13, INK)
    # Cheeks.
    cv.circle(x0 + 30, y0 + 96, 9, PINK)
    cv.circle(x1 - 30, y0 + 96, 9, PINK)
    # Grin: lower half of an ellipse, drawn thick.
    for deg in range(15, 166, 3):
        a = math.radians(deg)
        px = int(cx + 42 * math.cos(a))
        py = int(y0 + 88 + 26 * math.sin(a))
        cv.circle(px, py, 5, INK)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)

    cv = Canvas(W, H, BG)
    # Notification card.
    cv.rounded_rect(64, 72, 960, 952, 36, CARD, BG)

    # Header: green dot + "PAYDAY • BANK ALERT".
    cv.circle(140, 148, 14, GREEN)
    cv.text(168, 128, "PAYDAY \u2022 BANK ALERT", 4, SLATE)
    cv.rect(120, 192, 904, 196, LINE)

    # Giant headline.
    cv.text(120, 232, "YOUR SALARY", 11, INK)
    cv.text(120, 332, "WENT TO ", 11, INK)
    cv.text(120 + text_width("WENT TO ", 11), 332, "ME.", 11, GREEN)

    # The polite reason.
    cv.text(120, 452, "Reason: I did the work.", 5, BODY)
    cv.rect(120, 528, 904, 532, LINE)

    # Mini statement: the money's journey, then the empty balance.
    # (label left, amount right-aligned; one helper keeps the rows even.)
    def statement_row(y, label, amount, amount_color):
        cv.text(120, y, label, 4, SLATE)
        cv.text_right(904, y, amount, 4, amount_color)

    statement_row(566, "SALARY IN", "$3,200.00", GREEN)
    statement_row(622, "SENT TO AGENT", "$3,200.00", RED)
    statement_row(678, "BALANCE", "$0.00", RED)

    # Footer sign-off, left; smug robot, bottom right.
    cv.text(120, 830, "- love, your agent", 4, SLATE)
    draw_robot(cv, 748, 748, 908, 898)

    data = png_bytes(cv)
    if len(data) > MAX_BYTES:
        # Flat colours compress far below the cap; reaching this means the
        # picture itself changed, so fail loudly instead of shipping a
        # gate-invalid entry.
        raise SystemExit(
            "entry.png is %d bytes, over the %d byte gate" % (len(data), MAX_BYTES)
        )
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    try:
        os.chmod(path, 0o644)
    except OSError:
        pass


if __name__ == "__main__":
    main()
