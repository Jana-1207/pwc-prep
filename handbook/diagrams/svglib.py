"""Tiny SVG drawing helpers used by diagrams.py.

Everything is drawn with plain shapes (rect, path, polygon, text) — no markers,
clip paths or ids — so the SVG renders identically in browsers and in WeasyPrint.
"""
from __future__ import annotations

import math
from pathlib import Path
from xml.sax.saxutils import escape

FONT = "Plex Sans, IBM Plex Sans, DejaVu Sans, sans-serif"
MONO = "Plex Mono, IBM Plex Mono, DejaVu Sans Mono, monospace"

# kind -> (fill, stroke, text colour)
PAL = {
    "user": ("#F2F4F7", "#667085", "#1D2939"),
    "client": ("#EAF2FB", "#1F5FA8", "#13294B"),
    "service": ("#EAF2FB", "#1F5FA8", "#13294B"),
    "db": ("#E7F6F3", "#0F766E", "#0B4F4A"),
    "queue": ("#FFF4E6", "#B5520C", "#7A3608"),
    "analytics": ("#F2EDFC", "#6941C6", "#3E1F8C"),
    "external": ("#FFFFFF", "#98A2B3", "#344054"),
    "good": ("#EAF7EF", "#2F7A4D", "#1F5136"),
    "bad": ("#FEF0EF", "#B42318", "#7A1A12"),
    "neutral": ("#F8F9FB", "#98A2B3", "#344054"),
    "navy": ("#13294B", "#13294B", "#FFFFFF"),
    "amber": ("#FFF8E6", "#C27803", "#7A4B02"),
    "plain": ("#FFFFFF", "#D0D5DD", "#344054"),
    "highlight": ("#DCEBFB", "#1F5FA8", "#13294B"),
    "teal": ("#E7F6F3", "#0F766E", "#0B4F4A"),
    "purple": ("#F2EDFC", "#6941C6", "#3E1F8C"),
}
MUTED = "#5B6575"
ARROW = "#475467"
TEXT = "#1D2939"


def _f(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


def text_width(s: str, size: float, mono: bool = False) -> float:
    if mono:
        return len(s) * size * 0.6
    w = 0.0
    for ch in s:
        if ch in "il.,:;|!'":
            w += 0.28
        elif ch in "mwMW@":
            w += 0.85
        elif ch.isupper() or ch.isdigit():
            w += 0.64
        elif ch == " ":
            w += 0.28
        else:
            w += 0.53
    return w * size


class Diagram:
    def __init__(self, w: float, h: float):
        self.w, self.h = w, h
        self.items: list[str] = []

    # ------------------------------------------------------------ primitives
    def add(self, s: str):
        self.items.append(s)

    def rect(self, x, y, w, h, fill="#FFFFFF", stroke="#D0D5DD", lw=1.2, rx=6, dash=None, opacity=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        if opacity is not None:
            extra += f' fill-opacity="{opacity}"'
        self.add(f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" rx="{_f(rx)}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="{lw}"{extra}/>')

    def line(self, x1, y1, x2, y2, color=ARROW, lw=1.3, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{_f(x1)}" y1="{_f(y1)}" x2="{_f(x2)}" y2="{_f(y2)}" stroke="{color}" '
                 f'stroke-width="{lw}"{extra} stroke-linecap="round"/>')

    def path(self, d, fill="none", stroke=ARROW, lw=1.3, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{lw}"{extra} stroke-linejoin="round"/>')

    def circle(self, cx, cy, r, fill="#FFFFFF", stroke=ARROW, lw=1.3, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}" fill="{fill}" stroke="{stroke}" stroke-width="{lw}"{extra}/>')

    def polygon(self, pts, fill=ARROW, stroke="none", lw=1):
        p = " ".join(f"{_f(x)},{_f(y)}" for x, y in pts)
        self.add(f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{lw}"/>')

    def text(self, x, y, s, size=12, weight=400, color=TEXT, anchor="middle", mono=False, italic=False):
        fam = MONO if mono else FONT
        st = ' font-style="italic"' if italic else ""
        lead = len(s) - len(s.lstrip(" "))
        s = "\u00a0" * lead + s[lead:].replace("  ", " \u00a0")
        self.add(f'<text x="{_f(x)}" y="{_f(y)}" font-family="{fam}" font-size="{_f(size)}" '
                 f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}"{st}>{escape(s)}</text>')

    def mtext(self, x, cy, s, size=12, weight=400, color=TEXT, anchor="middle", mono=False, lh=1.25, italic=False):
        """Multi-line text vertically centred on cy."""
        lines = s.split("\n")
        step = size * lh
        y0 = cy - (len(lines) - 1) * step / 2 + size * 0.35
        for i, ln in enumerate(lines):
            self.text(x, y0 + i * step, ln, size, weight, color, anchor, mono, italic)

    def label(self, x, y, s, size=10, color="#344054", weight=500, bg="#FFFFFF", anchor="middle", italic=False, pad=3):
        """Text with a white background so it stays readable on top of lines."""
        lines = s.split("\n")
        w = max(text_width(l, size) for l in lines) + 2 * pad
        h = len(lines) * size * 1.25 + pad
        if anchor == "middle":
            x0 = x - w / 2
        elif anchor == "start":
            x0 = x - pad
        else:
            x0 = x - w + pad
        if bg:
            self.rect(x0, y - h / 2, w, h, fill=bg, stroke="none", lw=0, rx=3)
        self.mtext(x, y, s, size, weight, color, anchor, italic=italic)

    # ------------------------------------------------------------ shapes
    def box(self, x, y, w, h, title="", kind="service", sub=None, size=12.5, sub_size=10, rx=7,
            dash=None, align="middle", weight=600, mono_sub=False, lw=1.3, sub_color=None):
        fill, stroke, tcol = PAL[kind]
        if dash is None and kind == "external":
            dash = "5 4"
        self.rect(x, y, w, h, fill, stroke, lw, rx, dash)
        tl = title.split("\n") if title else []
        sl = sub.split("\n") if sub else []
        lh_t, lh_s = size * 1.22, sub_size * 1.3
        gap = 3 if (tl and sl) else 0
        total = len(tl) * lh_t + len(sl) * lh_s + gap
        yy = y + h / 2 - total / 2
        tx = x + w / 2 if align == "middle" else x + 9
        anchor = "middle" if align == "middle" else "start"
        for ln in tl:
            self.text(tx, yy + size * 0.9, ln, size, weight, tcol, anchor)
            yy += lh_t
        yy += gap
        sc = sub_color or (MUTED if kind != "navy" else "#C9D5E8")
        for ln in sl:
            self.text(tx, yy + sub_size * 0.92, ln, sub_size, 400, sc, anchor, mono=mono_sub)
            yy += lh_s
        return (x, y, w, h)

    def db(self, x, y, w, h, title, kind="db", sub=None, size=12.5, sub_size=10):
        fill, stroke, tcol = PAL[kind]
        e = min(11, h * 0.16)
        d = (f"M{_f(x)},{_f(y + e)} A{_f(w / 2)},{_f(e)} 0 0 1 {_f(x + w)},{_f(y + e)} "
             f"L{_f(x + w)},{_f(y + h - e)} A{_f(w / 2)},{_f(e)} 0 0 1 {_f(x)},{_f(y + h - e)} Z")
        self.path(d, fill=fill, stroke=stroke, lw=1.3)
        self.add(f'<ellipse cx="{_f(x + w / 2)}" cy="{_f(y + e)}" rx="{_f(w / 2)}" ry="{_f(e)}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>')
        tl = title.split("\n")
        sl = sub.split("\n") if sub else []
        lh_t, lh_s = size * 1.22, sub_size * 1.3
        gap = 3 if sl else 0
        total = len(tl) * lh_t + len(sl) * lh_s + gap
        cy = y + e + (h - e) / 2
        yy = cy - total / 2
        for ln in tl:
            self.text(x + w / 2, yy + size * 0.9, ln, size, 600, tcol)
            yy += lh_t
        yy += gap
        for ln in sl:
            self.text(x + w / 2, yy + sub_size * 0.92, ln, sub_size, 400, MUTED)
            yy += lh_s
        return (x, y, w, h)

    def frame(self, x, y, w, h, title="", color="#98A2B3", fill="#FFFFFF", dash="5 4", size=10.5, title_color=None, rx=9):
        self.rect(x, y, w, h, fill=fill, stroke=color, lw=1.1, rx=rx, dash=dash)
        if title:
            tw = text_width(title, size) + 12
            self.rect(x + 12, y - size * 0.75, tw, size * 1.5, fill="#FFFFFF", stroke="none", lw=0, rx=3)
            self.text(x + 18, y + size * 0.35, title, size, 600, title_color or color, "start")

    def table(self, x, y, w, name, cols, kind="service", row_h=19, head_h=24, size=10.2, highlight=()):
        """ER-style table. cols: list of (column, tag) with tag in {'PK','FK','PK FK',''}.
        Returns {column: y_centre} for connecting lines."""
        fill, stroke, tcol = PAL[kind]
        h = head_h + row_h * len(cols)
        self.rect(x, y, w, h, "#FFFFFF", stroke, 1.3, 5)
        # header with rounded top corners only
        r = 5
        d = (f"M{_f(x)},{_f(y + head_h)} L{_f(x)},{_f(y + r)} Q{_f(x)},{_f(y)} {_f(x + r)},{_f(y)} "
             f"L{_f(x + w - r)},{_f(y)} Q{_f(x + w)},{_f(y)} {_f(x + w)},{_f(y + r)} L{_f(x + w)},{_f(y + head_h)} Z")
        self.path(d, fill=stroke, stroke=stroke, lw=1.3)
        self.text(x + w / 2, y + head_h * 0.67, name, 11, 700, "#FFFFFF")
        pos = {}
        for i, (c, tag) in enumerate(cols):
            ry = y + head_h + i * row_h
            if c in highlight:
                self.rect(x + 1, ry, w - 2, row_h, "#FFF4D6", "none", 0, 0)
            if i > 0:
                self.line(x, ry, x + w, ry, "#E4E7EC", 0.8)
            bold = 600 if "PK" in tag else 400
            self.text(x + 8, ry + row_h * 0.68, c, size, bold, TEXT, "start", mono=True)
            if tag:
                tx = x + w - 6
                for t in reversed(tag.split()):
                    tw = text_width(t, 7.6) + 7
                    col = "#B5520C" if t == "PK" else "#1F5FA8"
                    bgc = "#FFF1E3" if t == "PK" else "#E3EEFC"
                    self.rect(tx - tw, ry + 4, tw, row_h - 8, bgc, "none", 0, 2.5)
                    self.text(tx - tw / 2, ry + row_h * 0.66, t, 7.6, 700, col)
                    tx -= tw + 3
            pos[c] = ry + row_h / 2
        pos["_h"] = h
        return pos

    # ------------------------------------------------------------ arrows
    def head(self, x, y, ang, size=7.5, color=ARROW):
        p2 = (x - size * math.cos(ang) + size * 0.48 * math.sin(ang), y - size * math.sin(ang) - size * 0.48 * math.cos(ang))
        p3 = (x - size * math.cos(ang) - size * 0.48 * math.sin(ang), y - size * math.sin(ang) + size * 0.48 * math.cos(ang))
        self.polygon([(x, y), p2, p3], fill=color)

    def arrow(self, x1, y1, x2, y2, label=None, color=ARROW, lw=1.4, dash=None, head=7.5, both=False,
              lsize=9.6, loff=(0, -7), lpos=0.5, lcolor="#344054", lbg="#FFFFFF", lanchor="middle", lweight=500):
        ang = math.atan2(y2 - y1, x2 - x1)
        ex, ey = x2 - math.cos(ang) * head * 0.7, y2 - math.sin(ang) * head * 0.7
        sx, sy = x1, y1
        if both:
            sx, sy = x1 + math.cos(ang) * head * 0.7, y1 + math.sin(ang) * head * 0.7
        self.line(sx, sy, ex, ey, color, lw, dash)
        self.head(x2, y2, ang, head, color)
        if both:
            self.head(x1, y1, ang + math.pi, head, color)
        if label:
            lx = x1 + (x2 - x1) * lpos + loff[0]
            ly = y1 + (y2 - y1) * lpos + loff[1]
            self.label(lx, ly, label, lsize, lcolor, lweight, lbg, lanchor)

    def parrow(self, pts, label=None, color=ARROW, lw=1.4, dash=None, head=7.5, lsize=9.6, lat=None,
               loff=(0, -7), lbg="#FFFFFF", lanchor="middle"):
        """Poly-line arrow through pts; arrow head on the last point."""
        (xa, ya), (xb, yb) = pts[-2], pts[-1]
        ang = math.atan2(yb - ya, xb - xa)
        trimmed = list(pts[:-1]) + [(xb - math.cos(ang) * head * 0.7, yb - math.sin(ang) * head * 0.7)]
        d = "M" + " L".join(f"{_f(x)},{_f(y)}" for x, y in trimmed)
        self.path(d, stroke=color, lw=lw, dash=dash)
        self.head(xb, yb, ang, head, color)
        if label:
            i = lat if lat is not None else (len(pts) - 2) // 2
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            self.label((x1 + x2) / 2 + loff[0], (y1 + y2) / 2 + loff[1], label, lsize, "#344054", 500, lbg, lanchor)

    # ------------------------------------------------------------ output
    def svg(self) -> str:
        body = "\n".join(self.items)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_f(self.w)} {_f(self.h)}" '
                f'width="{_f(self.w)}" height="{_f(self.h)}" font-family="{FONT}">\n{body}\n</svg>\n')

    def save(self, path: Path):
        path.write_text(self.svg(), encoding="utf-8")
