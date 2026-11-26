#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Generate the Pinstripe Plasma style (plasma/pinstripe).

Each frame (panel, popup, tooltip, button, ...) is painted with QPainter using the same
pinstripe rows and Aqua gel colour stops as the widget style, then cut into the nine
pieces Plasma's FrameSvg expects (topleft, top, ..., center). Pieces are embedded as
2x PNGs inside the SVG, so they stay sharp on HiDPI screens.

    python3 tools/make_plasma_theme.py
"""
import base64
import json
import os
import shutil
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QPointF, QRectF, Qt
from PySide6.QtGui import (QBrush, QColor, QGuiApplication, QImage, QLinearGradient, QPainter,
                           QPainterPath, QPen, QRadialGradient)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "plasma", "pinstripe")
SCALE = 2  # pixels per SVG unit in the embedded images

WINDOW_ROWS = (255, 238, 230, 238)  # 10.2 window pinstripe, from the HIG artwork
MENU_ROWS = (255, 249, 238, 249)  # menus are a little lighter

BLUE = dict(rim=((26, 44, 112), (62, 92, 140)),
            body=[(0.00, (92, 140, 214)), (0.42, (98, 162, 238)), (0.50, (107, 176, 246)),
                  (0.62, (141, 205, 255)), (0.80, (163, 228, 255)), (1.00, (180, 242, 255))],
            lens=[(0.00, (228, 234, 247)), (0.18, (189, 211, 239)), (0.55, (150, 191, 234)),
                  (1.00, (131, 181, 236))])
CLEAR = dict(rim=((108, 108, 112), (150, 150, 156)),
             body=[(0.00, (200, 202, 206)), (0.42, (201, 204, 210)), (0.55, (209, 214, 220)),
                   (0.80, (228, 233, 238)), (1.00, (247, 248, 250))],
             lens=[(0.00, (253, 253, 254)), (0.35, (236, 238, 242)), (1.00, (222, 225, 230))])
SELECTION = (56, 117, 215)
MENU_HIGHLIGHT = (66, 116, 198)


def qc(rgb, a=255):
    return QColor(rgb[0], rgb[1], rgb[2], a)


def stripes_brush(rows, alpha=255):
    img = QImage(16 * SCALE, 4 * SCALE, QImage.Format_ARGB32_Premultiplied)
    for y in range(4 * SCALE):
        v = rows[y // SCALE]
        for x in range(16 * SCALE):
            img.setPixelColor(x, y, QColor(v, v, v, alpha))
    return QBrush(img)


def gel(p, rect, g, radius, shadow=True, lens_inset=None, lens_h=0.42):
    p.save()
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)
    if shadow:
        for d, a in ((QRectF(-0.8, -0.2, 1.6, 2.8), 12), (QRectF(-0.3, 0.6, 0.6, 1.2), 22), (QRectF(0, 1, 0, 0), 30)):
            r = QRectF(rect.x() + d.x(), rect.y() + d.y(), rect.width() + d.width(), rect.height() + d.height())
            p.setBrush(QColor(0, 0, 0, a))
            p.drawRoundedRect(r, radius, radius)
    rim = QLinearGradient(rect.topLeft(), rect.bottomLeft())
    rim.setColorAt(0, qc(g["rim"][0]))
    rim.setColorAt(1, qc(g["rim"][1]))
    p.setBrush(rim)
    p.drawRoundedRect(rect, radius, radius)
    inner = rect.adjusted(1, 1, -1, -1)
    body = QLinearGradient(inner.topLeft(), inner.bottomLeft())
    for pos, c in g["body"]:
        body.setColorAt(pos, qc(c))
    p.setBrush(body)
    p.drawRoundedRect(inner, max(0, radius - 1), max(0, radius - 1))
    inset = lens_inset if lens_inset is not None else min(inner.height() * 0.3, inner.width() * 0.18)
    lens = QRectF(inner.left() + inset, inner.top() + 0.5, inner.width() - 2 * inset, inner.height() * lens_h)
    lg = QLinearGradient(lens.topLeft(), lens.bottomLeft())
    for pos, c in g["lens"]:
        lg.setColorAt(pos, qc(c))
    p.setBrush(lg)
    lr = min(lens.height(), radius) * 0.95
    p.drawRoundedRect(lens, lr, lr)
    p.restore()


class Frame:
    """A frame painted at SCALE into an image, then cut into nine pieces."""

    def __init__(self, w, h, left, top, right, bottom, paint):
        self.w, self.h = w, h
        self.l, self.t, self.r, self.b = left, top, right, bottom
        img = QImage(w * SCALE, h * SCALE, QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        p = QPainter(img)
        p.setRenderHint(QPainter.Antialiasing)
        p.scale(SCALE, SCALE)
        paint(p, QRectF(0, 0, w, h))
        p.end()
        self.img = img

    def pieces(self):
        w, h, l, t, r, b = self.w, self.h, self.l, self.t, self.r, self.b
        cw, ch = w - l - r, h - t - b
        return {
            "topleft": (0, 0, l, t), "top": (l, 0, cw, t), "topright": (w - r, 0, r, t),
            "left": (0, t, l, ch), "center": (l, t, cw, ch), "right": (w - r, t, r, ch),
            "bottomleft": (0, h - b, l, b), "bottom": (l, h - b, cw, b), "bottomright": (w - r, h - b, r, b),
        }


def png_data(img):
    ba = QByteArray()
    buf = QBuffer(ba)
    buf.open(QIODevice.WriteOnly)
    img.save(buf, "PNG")
    return base64.b64encode(bytes(ba)).decode()


class Svg:
    def __init__(self):
        self.items = []
        self.y = 0

    def add_frame(self, prefix, frame, hints=()):
        pre = prefix + "-" if prefix else ""
        x0 = 0
        y0 = self.y
        for name, (x, y, w, h) in frame.pieces().items():
            if w <= 0 or h <= 0:
                continue
            sub = frame.img.copy(int(x * SCALE), int(y * SCALE), int(w * SCALE), int(h * SCALE))
            self.items.append(
                f'<image id="{pre}{name}" x="{x0 + x}" y="{y0 + y}" width="{w}" height="{h}" '
                f'preserveAspectRatio="none" xlink:href="data:image/png;base64,{png_data(sub)}"/>')
        hx = frame.w + 10
        for i, (hint, size) in enumerate(hints):
            sw, sh = size if isinstance(size, tuple) else (size, size)
            self.items.append(f'<rect id="{pre}{hint}" x="{hx}" y="{y0 + i * 12}" width="{sw}" height="{sh}" fill="none"/>')
        self.y += frame.h + 20

    def add_rect(self, rid, w, h):
        self.items.append(f'<rect id="{rid}" x="0" y="{self.y}" width="{w}" height="{h}" fill="none"/>')
        self.y += h + 10

    def write(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        body = "\n".join(self.items)
        with open(path, "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                    f'width="400" height="{self.y + 10}" viewBox="0 0 400 {self.y + 10}">\n{body}\n</svg>\n')


# ------------------------------------------------------------------ painters

def sheet(rows, alpha, radius, border=(0, 0, 0, 60), rounded=(True, True, True, True)):
    """A pinstriped sheet (popups, desktop widgets, menu-bar panel)."""
    def paint(p, r):
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        rr = r.adjusted(0.5, 0.5, -0.5, -0.5)
        tl, tr_, br, bl = [radius if f else 0 for f in rounded]
        path.moveTo(rr.left() + tl, rr.top())
        path.lineTo(rr.right() - tr_, rr.top())
        path.quadTo(rr.right(), rr.top(), rr.right(), rr.top() + tr_)
        path.lineTo(rr.right(), rr.bottom() - br)
        path.quadTo(rr.right(), rr.bottom(), rr.right() - br, rr.bottom())
        path.lineTo(rr.left() + bl, rr.bottom())
        path.quadTo(rr.left(), rr.bottom(), rr.left(), rr.bottom() - bl)
        path.lineTo(rr.left(), rr.top() + tl)
        path.quadTo(rr.left(), rr.top(), rr.left() + tl, rr.top())
        p.setBrush(stripes_brush(rows, alpha))
        p.setPen(QPen(QColor(*border), 1.0))
        p.drawPath(path)
    return paint


def shadow_frame(size, radius, strength):
    """Soft drop shadow around a rect, for the shadow-* elements."""
    def paint(p, r):
        # build a blurred shadow in an image: a soft, mostly downward falloff
        inner = r.adjusted(size, size * 0.6, -size, -size * 1.4)
        steps = int(size * 2)
        p.setPen(Qt.NoPen)
        for i in range(steps, 0, -1):
            t = i / steps
            grow = t * size
            a = strength * (1 - t) ** 2 / steps * 2.2
            p.setBrush(QColor(0, 0, 0, max(1, min(255, int(a)))))
            p.drawRoundedRect(inner.adjusted(-grow, -grow * 0.7, grow, grow * 1.2), radius + grow, radius + grow)
    return paint


def glass_dock(radius):
    """The translucent Dock of 10.2: milky white glass with faint stripes and a bright edge."""
    def paint(p, r):
        rr = r.adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(rr, radius, radius)
        p.setPen(Qt.NoPen)
        g = QLinearGradient(rr.topLeft(), rr.bottomLeft())
        g.setColorAt(0.0, QColor(255, 255, 255, 175))
        g.setColorAt(0.5, QColor(250, 250, 252, 135))
        g.setColorAt(1.0, QColor(255, 255, 255, 150))
        p.setBrush(g)
        p.drawPath(path)
        p.save()
        p.setClipPath(path)
        p.setBrush(stripes_brush((255, 246, 238, 246), 60))
        p.drawRect(rr)
        p.restore()
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(255, 255, 255, 210), 1.0))
        p.drawRoundedRect(rr.adjusted(0.5, 0.5, -0.5, -0.5), radius - 0.5, radius - 0.5)
        p.setPen(QPen(QColor(0, 0, 0, 38), 1.0))
        p.drawRoundedRect(rr, radius, radius)
    return paint


def menubar(p, r):
    p.fillRect(r, stripes_brush(MENU_ROWS))
    hl = QLinearGradient(r.topLeft(), r.bottomLeft())
    hl.setColorAt(0, QColor(255, 255, 255, 110))
    hl.setColorAt(0.5, QColor(255, 255, 255, 0))
    p.fillRect(r, hl)
    p.fillRect(QRectF(r.left(), r.bottom() - 1, r.width(), 1), QColor(110, 110, 110))


def menubar_shadow(p, r):
    for i in range(6):
        p.fillRect(QRectF(r.left(), r.top() + i, r.width(), 1), QColor(0, 0, 0, int(60 * (1 - i / 6) ** 2)))


def tooltip(p, r):
    p.setRenderHint(QPainter.Antialiasing, False)
    p.fillRect(r, QColor(255, 255, 199, 245))
    p.setPen(QColor(0, 0, 0, 100))
    p.setBrush(Qt.NoBrush)
    p.drawRect(r.adjusted(0, 0, -1.0 / SCALE, -1.0 / SCALE))


def button(g):
    def paint(p, r):
        gel(p, r.adjusted(0.5, 0.5, -0.5, -2.5), g, 5.0, lens_inset=3)
    return paint


def flat(color, alpha, radius):
    def paint(p, r):
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(color[0], color[1], color[2], alpha))
        p.drawRoundedRect(r.adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)
    return paint


def focus_ring(p, r):
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(Qt.NoBrush)
    p.setPen(QPen(QColor(94, 146, 228, 120), 3.0))
    p.drawRoundedRect(r.adjusted(1.5, 1.5, -1.5, -1.5), 4, 4)
    p.setPen(QPen(QColor(94, 146, 228, 210), 1.2))
    p.drawRoundedRect(r.adjusted(2, 2, -2, -2), 3.5, 3.5)


def text_field(p, r):
    p.setRenderHint(QPainter.Antialiasing, False)
    f = r.adjusted(0, 0, 0, 0)
    p.fillRect(f, QColor(255, 255, 255))
    sh = QLinearGradient(f.topLeft(), QPointF(f.left(), f.top() + 3))
    sh.setColorAt(0, QColor(0, 0, 0, 52))
    sh.setColorAt(1, QColor(0, 0, 0, 0))
    p.fillRect(QRectF(f.left(), f.top(), f.width(), 3), sh)
    p.fillRect(QRectF(f.left(), f.top(), f.width(), 1), QColor(112, 112, 116))
    p.fillRect(QRectF(f.left(), f.top() + 1, 1, f.height() - 1), QColor(158, 158, 162))
    p.fillRect(QRectF(f.right() - 1, f.top() + 1, 1, f.height() - 1), QColor(158, 158, 162))
    p.fillRect(QRectF(f.left(), f.bottom() - 1, f.width(), 1), QColor(184, 184, 188))


def selection(p, r):
    """Glossy blue gel with the pinstripes showing through (matches the widget style)."""
    p.setPen(Qt.NoPen)
    body = QLinearGradient(r.topLeft(), r.bottomLeft())
    for pos, c in ((0.0, (74, 132, 222)), (0.48, (38, 104, 214)), (0.52, (44, 116, 226)), (0.80, (84, 162, 246)), (1.0, (128, 202, 255))):
        body.setColorAt(pos, qc(c))
    p.fillRect(r, body)
    for y in range(int(r.height())):
        a = (0, 44, 66, 44)[y % 4]
        if a:
            p.fillRect(QRectF(r.left(), r.top() + y, r.width(), 1), QColor(0, 26, 100, a))
        else:
            p.fillRect(QRectF(r.left(), r.top() + y, r.width(), 1), QColor(255, 255, 255, 34))
    lens = QRectF(r.left(), r.top(), r.width(), r.height() * 0.48)
    lg = QLinearGradient(lens.topLeft(), lens.bottomLeft())
    lg.setColorAt(0, QColor(255, 255, 255, 170))
    lg.setColorAt(0.25, QColor(255, 255, 255, 105))
    lg.setColorAt(1, QColor(255, 255, 255, 38))
    p.fillRect(lens, lg)
    p.fillRect(QRectF(r.left(), r.top(), r.width(), 1), QColor(24, 66, 160, 230))
    p.fillRect(QRectF(r.left(), r.bottom() - 2, r.width(), 1), QColor(170, 225, 255, 150))
    p.fillRect(QRectF(r.left(), r.bottom() - 1, r.width(), 1), QColor(40, 92, 180, 200))


def transparent(p, r):
    pass


# ------------------------------------------------------------------ theme

def build():
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    # panels: the default (bottom / floating) panel is the glass Dock; a top panel is the menu bar
    s = Svg()
    s.add_frame("", Frame(40, 40, 10, 10, 10, 10, glass_dock(7)), [("hint-tile-center", 1)])
    s.add_frame("north", Frame(32, 24, 4, 4, 4, 4, menubar),
                [("hint-tile-center", 1), ("hint-top-margin", (1, 1)), ("hint-bottom-margin", (1, 2)),
                 ("hint-left-margin", (2, 1)), ("hint-right-margin", (2, 1))])
    s.add_frame("shadow", Frame(48, 48, 16, 16, 16, 16, shadow_frame(8, 7, 50)))
    s.add_frame("north-shadow", Frame(24, 24, 1, 1, 1, 8, lambda p, r: menubar_shadow(p, QRectF(r.left(), r.bottom() - 8, r.width(), 8))))
    s.write(os.path.join(OUT, "widgets", "panel-background.svg"))

    # popups (launcher, calendar, tray): a pinstriped menu sheet with rounded corners
    s = Svg()
    s.add_frame("", Frame(32, 32, 8, 8, 8, 8, sheet(MENU_ROWS, 246, 5, border=(0, 0, 0, 34))),
                [("hint-tile-center", 1), ("hint-top-margin", (1, 4)), ("hint-bottom-margin", (1, 5)),
                 ("hint-left-margin", (1, 1)), ("hint-right-margin", (1, 1))])
    s.add_frame("shadow", Frame(64, 64, 24, 24, 24, 24, shadow_frame(12, 5, 70)),
                [("hint-top-margin", (1, 10)), ("hint-bottom-margin", (1, 16)), ("hint-left-margin", (12, 1)), ("hint-right-margin", (12, 1))])
    s.write(os.path.join(OUT, "dialogs", "background.svg"))

    # desktop widgets: window pinstripes
    s = Svg()
    s.add_frame("", Frame(40, 40, 10, 10, 10, 10, sheet(WINDOW_ROWS, 250, 8, border=(0, 0, 0, 70))),
                [("hint-tile-center", 1)])
    s.add_frame("shadow", Frame(64, 64, 24, 24, 24, 24, shadow_frame(12, 8, 70)))
    s.write(os.path.join(OUT, "widgets", "background.svg"))

    # tooltips: Aqua's pale yellow
    s = Svg()
    s.add_frame("", Frame(16, 16, 3, 3, 3, 3, tooltip),
                [("hint-top-margin", (1, 3)), ("hint-bottom-margin", (1, 3)), ("hint-left-margin", (5, 1)), ("hint-right-margin", (5, 1))])
    s.add_frame("shadow", Frame(40, 40, 14, 14, 14, 14, shadow_frame(6, 2, 45)))
    s.write(os.path.join(OUT, "widgets", "tooltip.svg"))

    # buttons: clear gel, coloured while pressed
    s = Svg()
    for prefix, g in (("normal", CLEAR), ("pressed", BLUE)):
        s.add_frame(prefix, Frame(40, 26, 7, 7, 7, 9, button(g)),
                    [("hint-stretch-borders", 1), ("hint-top-margin", (1, 4)), ("hint-bottom-margin", (1, 6)),
                     ("hint-left-margin", (10, 1)), ("hint-right-margin", (10, 1))])
    s.add_frame("focus", Frame(26, 26, 7, 7, 7, 7, focus_ring))
    s.add_frame("hover", Frame(26, 26, 7, 7, 7, 7, transparent))
    s.add_frame("toolbutton-hover", Frame(16, 16, 5, 5, 5, 5, flat((0, 0, 0), 22, 4)))
    s.add_frame("toolbutton-pressed", Frame(16, 16, 5, 5, 5, 5, flat((0, 0, 0), 48, 4)))
    s.add_frame("toolbutton-focus", Frame(26, 26, 7, 7, 7, 7, focus_ring))
    s.write(os.path.join(OUT, "widgets", "button.svg"))

    # text fields
    s = Svg()
    s.add_frame("base", Frame(24, 24, 4, 4, 4, 4, text_field),
                [("hint-top-margin", (1, 4)), ("hint-bottom-margin", (1, 3)), ("hint-left-margin", (5, 1)), ("hint-right-margin", (5, 1))])
    s.add_frame("focus", Frame(26, 26, 7, 7, 7, 7, focus_ring))
    s.add_frame("hover", Frame(26, 26, 7, 7, 7, 7, transparent))
    s.write(os.path.join(OUT, "widgets", "lineedit.svg"))

    # list highlights: Aqua selection blue
    s = Svg()
    # a 24px gel: the left/right borders and centre stretch vertically (gradient), so rows of any
    # height keep the lens on top and the glow at the bottom
    for prefix in ("selected", "hover", "selected+hover"):
        s.add_frame(prefix, Frame(24, 24, 2, 2, 2, 2, selection), [("hint-stretch-borders", 1)])

    s.add_frame("normal", Frame(16, 16, 4, 4, 4, 4, transparent))
    s.write(os.path.join(OUT, "widgets", "viewitem.svg"))

    # menu bar items for the global menu: the same striped gel
    s = Svg()
    for prefix in ("hover", "pressed"):
        s.add_frame(prefix, Frame(24, 24, 2, 2, 2, 2, selection), [("hint-stretch-borders", 1)])
    s.add_frame("normal", Frame(16, 16, 4, 4, 4, 4, transparent))
    s.write(os.path.join(OUT, "widgets", "menubaritem.svg"))

    # task manager: Dock items have no frame; a soft glow marks the active and hovered app
    s = Svg()
    s.add_frame("normal", Frame(16, 16, 4, 4, 4, 4, transparent))
    s.add_frame("minimized", Frame(16, 16, 4, 4, 4, 4, transparent))
    s.add_frame("focus", Frame(24, 24, 7, 7, 7, 7, flat((255, 255, 255), 80, 6)))
    s.add_frame("hover", Frame(24, 24, 7, 7, 7, 7, flat((255, 255, 255), 60, 6)))
    s.add_frame("attention", Frame(24, 24, 7, 7, 7, 7, flat((255, 170, 40), 110, 6)))
    s.write(os.path.join(OUT, "widgets", "tasks.svg"))

    with open(os.path.join(OUT, "metadata.json"), "w") as f:
        json.dump({
            "KPlugin": {
                "Authors": [{"Name": "Franco"}],
                "Category": "",
                "Description": "Pinstriped popups, a menu-bar top panel and a glass Dock, after Mac OS X 10.2",
                "Id": "pinstripe",
                "License": "GPL-2.0-or-later",
                "Name": "Pinstripe",
                "Version": "0.1",
            },
            "X-Plasma-API": "5.0",
        }, f, indent=4)
        f.write("\n")
    with open(os.path.join(OUT, "plasmarc"), "w") as f:
        f.write("[Settings]\nFallbackTheme=default\n\n[ContrastEffect]\nenabled=false\n\n[AdaptiveTransparency]\nenabled=false\n")
    shutil.copy(os.path.join(ROOT, "colors", "Pinstripe.colors"), os.path.join(OUT, "colors"))
    print("wrote", OUT)


if __name__ == "__main__":
    build()
