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
    if lens_h > 0 and g.get("lens"):
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

    def add_element(self, eid, w, h, paint):
        img = QImage(int(w * SCALE), int(h * SCALE), QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        p = QPainter(img)
        p.setRenderHint(QPainter.Antialiasing)
        p.scale(SCALE, SCALE)
        paint(p, QRectF(0, 0, w, h))
        p.end()
        self.items.append(f'<image id="{eid}" x="0" y="{self.y}" width="{w}" height="{h}" '
                          f'preserveAspectRatio="none" xlink:href="data:image/png;base64,{png_data(img)}"/>')
        self.y += h + 10

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
    """Glassy Aqua cushion button (HIG Figures 7-14, 7-15): top specular lens, cool silver/blue
    dip, curved side shading and upward bottom reflection above a crisp dark bottom rim."""
    def paint(p, r):
        rr = r.adjusted(0.5, 0.5, -0.5, -2.5)
        rad = 4.5
        p.save()
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        for dy, ex, a in ((2.0, 0.3, 16), (1.0, 0.0, 38)):
            p.setBrush(QColor(0, 0, 0, a))
            p.drawRoundedRect(rr.translated(0, dy).adjusted(-ex, 0, ex, 0), rad + ex, rad + ex)
        clip = QPainterPath()
        clip.addRoundedRect(rr, rad, rad)
        body = QLinearGradient(rr.topLeft(), rr.bottomLeft())
        for pos, c in g["body"]:
            body.setColorAt(pos, qc(c))
        p.setBrush(body)
        p.drawPath(clip)
        p.save()
        p.setClipPath(clip)
        sides = QLinearGradient(rr.topLeft(), rr.topRight())
        edge = QColor(150, 158, 174, 58) if g is BEVEL_CLEAR else QColor(20, 60, 150, 58)
        mid = QColor(edge.red(), edge.green(), edge.blue(), 0)
        e = min(0.18, 6.0 / max(1.0, rr.width()))
        sides.setColorAt(0.0, edge); sides.setColorAt(e, mid); sides.setColorAt(1.0 - e, mid); sides.setColorAt(1.0, edge)
        p.setBrush(sides)
        p.drawRect(rr)
        glow = QRadialGradient(QPointF(rr.center().x(), rr.bottom()), max(rr.width() * 0.58, rr.height() * 0.45))
        glow.setColorAt(0.0, QColor(255, 255, 255, 225) if g is BEVEL_CLEAR else QColor(180, 242, 255, 180))
        glow.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setBrush(glow)
        p.drawRect(QRectF(rr.left(), rr.center().y(), rr.width(), rr.height() * 0.5))
        lens_h = max(5.0, min(10.0, rr.height() * 0.34))
        lens = QRectF(rr.left() + 2.5, rr.top() + 0.8, rr.width() - 5.0, lens_h)
        lg = QLinearGradient(lens.topLeft(), lens.bottomLeft())
        for pos, c in g["lens"]:
            lg.setColorAt(pos, qc(c))
        p.setBrush(lg)
        p.drawRoundedRect(lens, min(lens_h * 0.5, rad - 1), min(lens_h * 0.5, rad - 1))
        p.restore()
        rim = QLinearGradient(rr.topLeft(), rr.bottomLeft())
        rim.setColorAt(0.0, qc(g["rim"][0]))
        rim.setColorAt(1.0, qc(g["rim"][1]))
        p.setPen(QPen(QBrush(rim), 1.0))
        p.setBrush(Qt.NoBrush)
        p.drawPath(clip)
        p.restore()
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


LENS_H, GLOW_H = 11, 8  # fixed heights, so tall tiles and short rows look the same


def selection(p, r, radius=0.0):
    """Glossy blue gel. Translucent, so the pinstripes of whatever it sits on show through and
    stay aligned (an SVG frame can't know the background's stripe phase). A fixed 11px lens on
    top and an 8px glow at the bottom; the frame tiles the plain body in between, so the gel
    keeps its proportions at any height. radius > 0 rounds the corners (launcher, lists)."""
    p.save()
    p.setRenderHint(QPainter.Antialiasing, True)
    clip = QPainterPath()
    if radius > 0:
        clip.addRoundedRect(r, radius, radius)
    else:
        clip.addRect(r)
    p.setClipPath(clip)
    p.setPen(Qt.NoPen)
    body = QLinearGradient(r.topLeft(), r.bottomLeft())
    body.setColorAt(0, QColor(30, 96, 212, 196))
    body.setColorAt(1, QColor(44, 120, 228, 196))
    p.fillRect(r, body)
    lens = QRectF(r.left(), r.top(), r.width(), LENS_H)
    lg = QLinearGradient(lens.topLeft(), lens.bottomLeft())
    lg.setColorAt(0, QColor(255, 255, 255, 170))
    lg.setColorAt(0.25, QColor(255, 255, 255, 105))
    lg.setColorAt(1, QColor(255, 255, 255, 30))
    p.fillRect(lens, lg)
    glow = QRectF(r.left(), r.bottom() - GLOW_H, r.width(), GLOW_H)
    gg = QLinearGradient(glow.topLeft(), glow.bottomLeft())
    gg.setColorAt(0, QColor(128, 202, 255, 0))
    gg.setColorAt(1, QColor(128, 202, 255, 200))
    p.fillRect(glow, gg)
    if radius > 0:
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(24, 66, 160, 210), 1))
        p.drawRoundedRect(r.adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)
    else:
        p.fillRect(QRectF(r.left(), r.top(), r.width(), 1), QColor(24, 66, 160, 230))
        p.fillRect(QRectF(r.left(), r.bottom() - 2, r.width(), 1), QColor(170, 225, 255, 150))
        p.fillRect(QRectF(r.left(), r.bottom() - 1, r.width(), 1), QColor(40, 92, 180, 200))
    p.restore()


def rounded_selection(p, r):
    selection(p, r, 5.0)


def transparent(p, r):
    pass



# ------------------------------------------------------------------ scroll bars, sliders, meters, tabs

THUMB_COLS = [(122, 159, 215), (143, 185, 238), (140, 184, 236), (128, 180, 238), (79, 142, 216), (93, 162, 239),
              (111, 178, 249), (128, 195, 253), (141, 209, 254), (160, 220, 253), (164, 206, 232)]


def track(horizontal):
    """Scroll bar track: an opaque white cylinder shaded along its leading edge, rounded ends."""
    def paint(p, r):
        g = QLinearGradient(r.topLeft(), r.bottomLeft() if horizontal else r.topRight())
        for pos, v in ((0.0, 176), (0.10, 192), (0.22, 212), (0.40, 240), (0.55, 255), (0.85, 250), (1.0, 228)):
            g.setColorAt(pos, QColor(v, v, v))
        rad = (r.height() if horizontal else r.width()) / 2
        p.setPen(Qt.NoPen)
        p.setBrush(g)
        p.drawRoundedRect(r, rad, rad)
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(0, 0, 0, 46), 1.0))
        p.drawRoundedRect(r.adjusted(0.5, 0.5, -0.5, -0.5), rad - 0.5, rad - 0.5)
    return paint


def thumb(lighter=0):
    """Plasma uses one 'slider' frame for both orientations, so the gel is shaded symmetrically:
    the measured thumb colours run inwards from every edge, with a pale streak in the middle."""
    def paint(p, r):
        rr = r.adjusted(1, 1, -1, -1)
        rad = min(rr.width(), rr.height()) / 2
        path = QPainterPath()
        path.addRoundedRect(rr, rad, rad)
        p.setPen(Qt.NoPen)
        base = QColor(93, 162, 239).lighter(100 + lighter)
        p.setBrush(base)
        p.drawPath(path)
        p.save()
        p.setClipPath(path)
        # darker towards every edge (cylinder in both directions)
        for i in range(int(rad) + 1):
            a = int(110 * (1 - i / max(1, rad)) ** 2.2)
            p.setPen(QPen(QColor(20, 60, 150, a), 1.0))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(rr.adjusted(i + 0.5, i + 0.5, -i - 0.5, -i - 0.5), max(0, rad - i), max(0, rad - i))
        glow = QRadialGradient(rr.center(), rad * 1.1)
        glow.setColorAt(0, QColor(170, 228, 255, 150))
        glow.setColorAt(1, QColor(170, 228, 255, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(glow)
        p.drawRect(rr)
        p.restore()
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(24, 55, 115), 1.0))
        p.drawRoundedRect(rr.adjusted(0.5, 0.5, -0.5, -0.5), rad - 0.5, rad - 0.5)
    return paint


def round_gel(g, d):
    def paint(p, r):
        rr = QRectF(r.center().x() - d / 2, r.center().y() - d / 2 - 0.5, d, d)
        gel(p, rr, g, d / 2, shadow=True, lens_inset=d * 0.16, lens_h=0.46)
    return paint


def ring(d, color=(94, 146, 228)):
    def paint(p, r):
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(*color, 130), 3.0))
        p.drawEllipse(r.center(), d / 2 - 1.5, d / 2 - 1.5)
    return paint


def soft_shadow(d):
    def paint(p, r):
        g = QRadialGradient(r.center() + QPointF(0, 1), d / 2)
        g.setColorAt(0.6, QColor(0, 0, 0, 60))
        g.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(g)
        p.drawEllipse(r)
    return paint


def meter(g, horizontal, radius=3):
    def paint(p, r):
        if horizontal:
            gel(p, r.adjusted(0.5, 0.5, -0.5, -0.5), g, radius, shadow=False, lens_inset=2, lens_h=0.42)
        else:
            img = QImage(int(r.height() * SCALE), int(r.width() * SCALE), QImage.Format_ARGB32_Premultiplied)
            img.fill(Qt.transparent)
            ip = QPainter(img)
            ip.setRenderHint(QPainter.Antialiasing)
            ip.scale(SCALE, SCALE)
            gel(ip, QRectF(0.5, 0.5, r.height() - 1, r.width() - 1), g, radius, shadow=False, lens_inset=2, lens_h=0.42)
            ip.end()
            p.save()
            p.translate(r.left(), r.bottom())
            p.rotate(-90)
            p.drawImage(QRectF(0, 0, r.height(), r.width()), img)
            p.restore()
    return paint


TRACK = dict(rim=((130, 130, 134), (170, 170, 174)),
             body=[(0.0, (206, 206, 210)), (0.45, (214, 214, 218)), (0.55, (226, 226, 230)), (1.0, (250, 250, 252))],
             lens=[(0.0, (248, 248, 250)), (1.0, (230, 230, 234))])
# 16px large progress bar fill rows measured from HIG Figure 7-27 (no separate white lens)
PROGRESS_ROWS = [(90, 135, 212), (130, 175, 229), (143, 187, 234), (144, 186, 236), (131, 178, 232),
                 (110, 165, 229), (85, 150, 223), (74, 145, 227), (82, 156, 241), (95, 170, 251),
                 (104, 180, 255), (116, 192, 254), (125, 202, 255), (131, 204, 255), (143, 196, 236)]
PROGRESS = dict(rim=((47, 85, 150), (90, 140, 200)),
                body=[(i / 14.0, c) for i, c in enumerate(PROGRESS_ROWS)],
                lens=[])
BEVEL_CLEAR = dict(rim=((152, 154, 160), (82, 84, 90)),
                   body=[(0.00, (236, 238, 243)), (0.26, (228, 231, 238)), (0.32, (216, 220, 228)),
                         (0.62, (226, 229, 235)), (0.86, (244, 246, 249)), (1.00, (255, 255, 255))],
                   lens=[(0.00, (255, 255, 255)), (0.58, (250, 251, 254)), (1.00, (242, 245, 250))])
TAB_SELECTED = dict(rim=((21, 43, 108), (0, 87, 174)),
                    body=[(0.00, (136, 176, 226)), (0.24, (114, 158, 212)), (0.55, (148, 192, 238)),
                          (0.82, (182, 224, 255)), (0.95, (206, 246, 255)), (1.00, (178, 222, 244))],
                    lens=[(0.00, (198, 224, 248)), (0.50, (176, 208, 240)), (1.00, (152, 192, 232))])
TAB_CLEAR = dict(rim=((118, 118, 122), (140, 140, 144)),
                 body=[(0.00, (214, 215, 218)), (0.26, (194, 196, 200)), (0.60, (214, 216, 220)),
                       (0.88, (242, 244, 246)), (1.00, (252, 253, 255))],
                 lens=[(0.00, (250, 250, 252)), (0.50, (236, 237, 240)), (1.00, (220, 222, 226))])
ACCENT_ROWS = [(0, 87, 174), (162, 215, 240), (168, 209, 238), (81, 176, 234), (121, 204, 255), (172, 239, 255)]
ACCENT_SHADOW = [(98, 98, 98, 255), (147, 147, 147, 255), (226, 226, 226, 200)]


def slider_groove(p, r):
    """6px dark recessed slider capsule (HIG Figure 7-18); Aqua sliders have no highlight fill."""
    rr = r.adjusted(0.5, 0.5, -0.5, -0.5)
    rad = min(rr.width(), rr.height()) / 2
    g = QLinearGradient(rr.topLeft(), rr.bottomLeft())
    g.setColorAt(0.0, QColor(96, 96, 100))
    g.setColorAt(0.45, QColor(140, 140, 144))
    g.setColorAt(1.0, QColor(200, 200, 204))
    p.setPen(QPen(QColor(84, 84, 88), 1.0))
    p.setBrush(g)
    p.drawRoundedRect(rr, rad, rad)


def tab_accent_bar(p, r):
    p.setRenderHint(QPainter.Antialiasing, False)
    for i, c in enumerate(ACCENT_ROWS):
        p.fillRect(QRectF(r.left(), r.top() + i, r.width(), 1), qc(c))
    for i, c in enumerate(ACCENT_SHADOW):
        p.fillRect(QRectF(r.left(), r.top() + 6 + i, r.width(), 1), QColor(*c))


def tab(side, g=TAB_SELECTED):
    def paint(p, r):
        # flush on the pane side so an active tab covers row 0 (#0057ae) of the accent strip 100%
        if side == "north":
            rr = r.adjusted(0.5, 0.5, -0.5, 0.0)
        elif side == "south":
            rr = r.adjusted(0.5, 0.0, -0.5, -0.5)
        elif side == "west":
            rr = r.adjusted(0.5, 0.5, 0.0, -0.5)
        else:
            rr = r.adjusted(0.0, 0.5, -0.5, -0.5)
        rad = 4.5
        rim_path = QPainterPath()
        L, T, R, B = rr.left(), rr.top(), rr.right(), rr.bottom()
        if side == "north":
            rim_path.moveTo(L, B); rim_path.lineTo(L, T + rad); rim_path.quadTo(L, T, L + rad, T); rim_path.lineTo(R - rad, T); rim_path.quadTo(R, T, R, T + rad); rim_path.lineTo(R, B)
        elif side == "south":
            rim_path.moveTo(L, T); rim_path.lineTo(L, B - rad); rim_path.quadTo(L, B, L + rad, B); rim_path.lineTo(R - rad, B); rim_path.quadTo(R, B, R, B - rad); rim_path.lineTo(R, T)
        elif side == "west":
            rim_path.moveTo(R, T); rim_path.lineTo(L + rad, T); rim_path.quadTo(L, T, L, T + rad); rim_path.lineTo(L, B - rad); path_ok = True; rim_path.quadTo(L, B, L + rad, B); rim_path.lineTo(R, B)
        else:
            rim_path.moveTo(L, T); rim_path.lineTo(R - rad, T); rim_path.quadTo(R, T, R, T + rad); rim_path.lineTo(R, B - rad); rim_path.quadTo(R, B, R - rad, B); rim_path.lineTo(L, B)
        fill_path = QPainterPath(rim_path)
        fill_path.closeSubpath()
        vertical = side in ("west", "east")
        rev = side in ("south", "east")
        body = QLinearGradient(rr.topLeft(), rr.topRight() if vertical else rr.bottomLeft())
        for pos, c in g["body"]:
            body.setColorAt(1.0 - pos if rev else pos, qc(c))
        p.setPen(Qt.NoPen)
        p.setBrush(body)
        p.drawPath(fill_path)
        if g.get("lens"):
            p.save()
            p.setClipPath(fill_path)
            th = rr.width() if vertical else rr.height()
            lt = min(th * 0.32, 7.5)
            if side == "north":
                lens = QRectF(L + 2.5, T + 1.0, rr.width() - 5.0, lt)
            elif side == "south":
                lens = QRectF(L + 2.5, B - 1.0 - lt, rr.width() - 5.0, lt)
            elif side == "west":
                lens = QRectF(L + 1.0, T + 2.5, lt, rr.height() - 5.0)
            else:
                lens = QRectF(R - 1.0 - lt, T + 2.5, lt, rr.height() - 5.0)
            lg = QLinearGradient(lens.topLeft(), lens.topRight() if vertical else lens.bottomLeft())
            for pos, c in g["lens"]:
                lg.setColorAt(1.0 - pos if rev else pos, qc(c))
            p.setBrush(lg)
            p.drawRoundedRect(lens, lt * 0.45, lt * 0.45)
            p.restore()
        rim = QLinearGradient(rr.topLeft(), rr.topRight() if vertical else rr.bottomLeft())
        rim.setColorAt(0.0, qc(g["rim"][1 if rev else 0]))
        rim.setColorAt(1.0, qc(g["rim"][0 if rev else 1]))
        p.setPen(QPen(QBrush(rim), 1.0))
        p.setBrush(Qt.NoBrush)
        p.drawPath(rim_path)
    return paint


def spinner(p, r):
    """Aqua asynchronous progress indicator: twelve rounded spokes fading round the circle."""
    import math
    c = r.center()
    rad = min(r.width(), r.height()) / 2
    for i in range(12):
        a = math.radians(-90 + i * 30)
        alpha = int(40 + 200 * (i / 11))
        inner, outer = rad * 0.48, rad * 0.94
        p1 = QPointF(c.x() + inner * math.cos(a), c.y() + inner * math.sin(a))
        p2 = QPointF(c.x() + outer * math.cos(a), c.y() + outer * math.sin(a))
        p.setPen(QPen(QColor(64, 64, 68, alpha), rad * 0.17, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(p1, p2)


def check_glyph(p, r):
    path = QPainterPath()
    path.moveTo(r.left() + 3.5, r.top() + 8.5)
    path.lineTo(r.left() + 6.8, r.top() + 12.6)
    path.cubicTo(r.left() + 8.5, r.top() + 7.5, r.left() + 11, r.top() + 3.5, r.left() + 15, r.top() + 0.8)
    p.setPen(QPen(QColor(18, 20, 32), 1.9, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(Qt.NoBrush)
    p.drawPath(path)


def dot(p, r):
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(18, 20, 32))
    p.drawEllipse(r.center(), r.width() / 2 - 0.5, r.height() / 2 - 0.5)


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

    # buttons: glassy clear cushion, coloured while pressed
    s = Svg()
    for prefix, g in (("normal", BEVEL_CLEAR), ("pressed", BLUE)):
        s.add_frame(prefix, Frame(40, 26, 8, 8, 8, 9, button(g)),
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
    # lens in the top border, glow in the bottom border, one stripe period (4px) in the
    # tiled centre: the highlight looks the same on a menu row and on a tall launcher tile
    for prefix in ("selected", "hover", "selected+hover"):
        s.add_frame(prefix, Frame(24, LENS_H + 4 + GLOW_H, 6, LENS_H, 6, GLOW_H, rounded_selection), [("hint-tile-center", 1)])

    s.add_frame("normal", Frame(16, 16, 4, 4, 4, 4, transparent))
    s.write(os.path.join(OUT, "widgets", "viewitem.svg"))

    # scroll bars: 15px, white cylinder track, gel thumb
    s = Svg()
    s.add_rect("hint-scrollbar-size", 15, 15)
    s.add_frame("background-vertical", Frame(15, 40, 7, 8, 7, 8, track(False)), [("hint-stretch-borders", 1)])
    s.add_frame("background-horizontal", Frame(40, 15, 8, 7, 8, 7, track(True)), [("hint-stretch-borders", 1)])
    s.add_frame("slider", Frame(15, 40, 7, 8, 7, 8, thumb()), [("hint-stretch-borders", 1)])
    s.add_frame("mouseover-slider", Frame(15, 40, 7, 8, 7, 8, thumb(8)), [("hint-stretch-borders", 1)])
    s.write(os.path.join(OUT, "widgets", "scrollbar.svg"))

    # sliders: 6px dark recessed groove (no blue highlight fill) and the round 15px Aqua thumb
    s = Svg()
    s.add_rect("hint-handle-size", 17, 17)
    groove_hints = [("hint-stretch-borders", 1), ("hint-top-margin", (1, 3)), ("hint-bottom-margin", (1, 3)),
                    ("hint-left-margin", (3, 1)), ("hint-right-margin", (3, 1))]
    s.add_frame("groove", Frame(12, 6, 3, 2, 3, 2, slider_groove), groove_hints)
    s.add_frame("groove-highlight", Frame(12, 6, 3, 2, 3, 2, transparent), groove_hints)
    for o in ("horizontal", "vertical"):
        s.add_element(f"{o}-slider-handle", 17, 17, round_gel(BLUE, 15))
        s.add_element(f"{o}-slider-hover", 17, 17, round_gel(BLUE, 15))
        s.add_element(f"{o}-slider-focus", 21, 21, ring(21))
        s.add_element(f"{o}-slider-shadow", 21, 21, soft_shadow(21))
    s.write(os.path.join(OUT, "widgets", "slider.svg"))

    # progress bars (HIG Figure 7-27): 16px height, near-square ends (radius 2), measured fill rows
    for name, horizontal in (("bar_meter_horizontal", True), ("bar_meter_vertical", False)):
        s = Svg()
        s.add_rect("hint-bar-size", 16, 16)
        fw, fh = (30, 16) if horizontal else (16, 30)
        s.add_frame("bar-inactive", Frame(fw, fh, 4, 4, 4, 4, meter(TRACK, horizontal, radius=2)), [("hint-stretch-borders", 1)])
        s.add_frame("bar-active", Frame(fw, fh, 4, 4, 4, 4, meter(PROGRESS, horizontal, radius=2)), [("hint-stretch-borders", 1)])
        s.write(os.path.join(OUT, "widgets", name + ".svg"))

    # tab bars: the selected tab morphs seamlessly into the 6-row Aqua accent bar (open pane edge)
    s = Svg()
    for side in ("north", "south", "west", "east"):
        w, h = (40, 24) if side in ("north", "south") else (24, 40)
        # Jaguar's selected tab is the Aqua blue gel. Plasma's tray reuses this element to mark an
        # open menu extra on a top panel, where the saturated blue also reads like an open menu title.
        s.add_frame(f"{side}-active-tab", Frame(w, h, 6, 6, 6, 6, tab(side, BLUE)),
                    [("hint-stretch-borders", 1), ("hint-top-margin", (1, 4)), ("hint-bottom-margin", (1, 4)),
                     ("hint-left-margin", (12, 1)), ("hint-right-margin", (12, 1))])
    s.add_frame("north-tab", Frame(40, 23, 6, 6, 6, 6, tab("north", TAB_CLEAR)), [("hint-stretch-borders", 1)])
    s.add_frame("north-tab-bar", Frame(32, 9, 2, 2, 2, 2, tab_accent_bar), [("hint-stretch-borders", 1)])
    s.write(os.path.join(OUT, "widgets", "tabbar.svg"))

    # radio buttons and check marks
    s = Svg()
    s.add_rect("hint-size", 18, 18)
    s.add_element("normal", 18, 18, round_gel(CLEAR, 14))
    s.add_element("hover", 18, 18, round_gel(CLEAR, 14))
    s.add_element("checked", 18, 18, round_gel(BLUE, 14))
    s.add_element("symbol", 6, 6, dot)
    s.add_element("focus", 22, 22, ring(22))
    s.add_element("shadow", 22, 22, soft_shadow(22))
    s.write(os.path.join(OUT, "widgets", "radiobutton.svg"))
    s = Svg()
    s.add_element("checkbox", 16, 16, check_glyph)
    s.add_element("radiobutton", 16, 16, lambda p, r: dot(p, QRectF(r.center().x() - 3, r.center().y() - 3, 6, 6)))
    s.write(os.path.join(OUT, "widgets", "checkmarks.svg"))

    # busy indicator: Plasma spins this image
    s = Svg()
    s.add_element("busywidget", 32, 32, spinner)
    s.write(os.path.join(OUT, "widgets", "busywidget.svg"))

    # menu bar items for the global menu: the same striped gel
    s = Svg()
    for prefix in ("hover", "pressed"):
        s.add_frame(prefix, Frame(24, LENS_H + 4 + GLOW_H, 2, LENS_H, 2, GLOW_H, selection), [("hint-tile-center", 1)])
    s.add_frame("normal", Frame(16, 16, 4, 4, 4, 4, transparent))
    s.write(os.path.join(OUT, "widgets", "menubaritem.svg"))

    # task manager: Dock items have no frame; running apps get the small black triangle.
    # A frame can't centre a shape, so the corners are wide and transparent and the triangle
    # sits in the bottom edge, which is stretched (not tiled) across the remaining width.
    def triangle_frame(glow):
        def paint(p, r):
            if glow:
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(255, 255, 255, 70))
                p.drawRoundedRect(r.adjusted(1, 1, -1, -7), 6, 6)
            cx, by = r.center().x(), r.bottom() - 0.5
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(20, 20, 20, 235))
            p.drawPolygon([QPointF(cx - 3.5, by), QPointF(cx + 3.5, by), QPointF(cx, by - 5)])
        return paint
    s = Svg()
    hints = [("hint-stretch-borders", 1), ("hint-top-margin", (1, 2)), ("hint-bottom-margin", (1, 2)),
             ("hint-left-margin", (2, 1)), ("hint-right-margin", (2, 1))]
    s.add_frame("normal", Frame(44, 44, 18, 6, 18, 6, triangle_frame(False)), hints)
    s.add_frame("minimized", Frame(44, 44, 18, 6, 18, 6, triangle_frame(False)), hints)
    s.add_frame("focus", Frame(44, 44, 18, 6, 18, 6, triangle_frame(False)), hints)
    s.add_frame("hover", Frame(24, 24, 7, 7, 7, 7, flat((255, 255, 255), 60, 6)))
    s.add_frame("attention", Frame(44, 44, 18, 6, 18, 6, triangle_frame(True)), hints)
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
