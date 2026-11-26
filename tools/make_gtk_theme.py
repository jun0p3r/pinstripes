#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Generate the Pinstripe GTK 3 / GTK 4 theme (gtk/Pinstripe).

Gel controls (buttons, pop-ups, check boxes, radio buttons, tabs, thumbs, knobs, traffic
lights) are painted as 1x/2x PNG assets with the same colour stops as the Qt style and the
Plasma style; pinstripes and the glossy selection are CSS gradients, so they stay exact at
any scale.

    python3 tools/make_gtk_theme.py
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import make_plasma_theme as mp  # noqa: E402
from PySide6.QtCore import QPointF, QRectF, Qt  # noqa: E402
from PySide6.QtGui import (QBrush, QColor, QGuiApplication, QImage, QLinearGradient, QPainter,  # noqa: E402
                           QPainterPath, QPen, QRadialGradient)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "gtk", "Pinstripe")

GRAPHITE = lambda c: tuple(int(max(0, min(255, v))) for v in (  # noqa: E731
    (0.30 * c[0] + 0.59 * c[1] + 0.11 * c[2]) * 0.90, (0.30 * c[0] + 0.59 * c[1] + 0.11 * c[2]) * 0.95,
    (0.30 * c[0] + 0.59 * c[1] + 0.11 * c[2]) * 1.06))

PRESSED = dict(rim=mp.BLUE["rim"], body=[(p, tuple(int(v * 0.85) for v in c)) for p, c in mp.BLUE["body"]],
               lens=[(p, tuple(int(v * 0.85) for v in c)) for p, c in mp.BLUE["lens"]])
POPUP_BODY = dict(rim=((102, 102, 106), (142, 142, 146)),
                  body=[(0.0, (232, 232, 234)), (0.45, (226, 226, 229)), (0.55, (222, 223, 226)), (0.85, (240, 240, 242)), (1.0, (252, 252, 253))],
                  lens=[(0.0, (255, 255, 255)), (1.0, (244, 244, 246))])
TAB_CLEAR = mp.TAB_CLEAR


def save(name, w, h, paint):
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    for scale, suffix in ((1, ""), (2, "@2")):
        img = QImage(int(w * scale), int(h * scale), QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        p = QPainter(img)
        p.setRenderHint(QPainter.Antialiasing)
        p.scale(scale, scale)
        paint(p, QRectF(0, 0, w, h))
        p.end()
        img.save(os.path.join(OUT, "assets", f"{name}{suffix}.png"))


def slice3(name, w, h, axis, a, b):
    """Cut assets/<name>(@2).png into <name>-s, -m, -e strips (a px start cap, b px end cap)."""
    from PySide6.QtGui import QImage as _QImage
    for scale, suffix in ((1, ""), (2, "@2")):
        img = _QImage(os.path.join(OUT, "assets", f"{name}{suffix}.png"))
        W, H = img.width(), img.height()
        # the middle is one column (row) from the centre: stretching it can't blend its edges
        # with transparency, which is what left seams in GTK 3
        if axis == "h":
            parts = {"s": (0, 0, a * scale, H), "m": (W // 2, 0, 1, H), "e": (W - b * scale, 0, b * scale, H)}
        else:
            parts = {"s": (0, 0, W, a * scale), "m": (0, H // 2, W, 1), "e": (0, H - b * scale, W, b * scale)}
        for k, (x, y, ww, hh) in parts.items():
            img.copy(x, y, ww, hh).save(os.path.join(OUT, "assets", f"{name}-{k}{suffix}.png"))


SLICES = {n: v for n, v in {
    "button": ("h", 14, 14), "button-default": ("h", 14, 14), "button-pressed": ("h", 14, 14),
    "popup": ("h", 9, 29), "popup-backdrop": ("h", 9, 29),
    "tab": ("h", 12, 12), "tab-active": ("h", 12, 12), "tab-active-backdrop": ("h", 12, 12),
    "progress": ("h", 4, 4), "progress-backdrop": ("h", 4, 4), "trough": ("h", 4, 4),
    "thumb-v": ("v", 7, 8), "thumb-v-backdrop": ("v", 7, 8), "thumb-h": ("h", 7, 8), "thumb-h-backdrop": ("h", 7, 8)}.items()}


def three(name):
    """Background layers that draw a gel as start cap + stretched middle + end cap.
    GTK ignores the centre slice of border-image, so this replaces it. The middle column is
    tiled, not stretched: GTK 3 fades the edges of a stretched 1px image. The element's
    padding must equal the cap sizes: the middle layer is clipped to the content box."""
    axis, a, b = SLICES[name]
    sc = lambda k: f'-gtk-scaled(url("assets/{name}-{k}.png"), url("assets/{name}-{k}@2.png"))'  # noqa: E731
    if axis == "h":
        return (f"background-image: {sc('s')}, {sc('e')}, {sc('m')}; "
                f"background-position: left top, right top, left top; "
                f"background-size: {a}px 100%, {b}px 100%, 1px 100%; "
                f"background-repeat: no-repeat, no-repeat, repeat-x; background-origin: border-box, border-box, content-box; "
                f"background-clip: border-box, border-box, content-box; border-image: none;")
    return (f"background-image: {sc('s')}, {sc('e')}, {sc('m')}; "
            f"background-position: left top, left bottom, left top; "
            f"background-size: 100% {a}px, 100% {b}px, 100% 1px; "
            f"background-repeat: no-repeat, no-repeat, repeat-y; background-origin: border-box, border-box, content-box; "
            f"background-clip: border-box, border-box, content-box; border-image: none;")


def capsule(g):
    def paint(p, r):
        mp.gel(p, QRectF(0.5, 0.5, r.width() - 1, 20), g, 10, lens_inset=7.7)
    return paint


def indicator(g, radio, mark):
    def paint(p, r):
        box = QRectF(2, 1, 14, 14)
        mp.gel(p, box, g, 7 if radio else 3, lens_inset=2.5 if radio else 1.5, lens_h=0.46)
        p.setRenderHint(QPainter.Antialiasing)
        ink = QColor(18, 20, 32)
        if mark == "on" and radio:
            p.setPen(Qt.NoPen)
            p.setBrush(ink)
            p.drawEllipse(box.center() + QPointF(0, 0.3), 2.6, 2.6)
        elif mark == "on":
            path = QPainterPath()
            path.moveTo(box.left() + 3.2, box.top() + 7.2)
            path.lineTo(box.left() + 6.3, box.top() + 11.4)
            path.cubicTo(box.left() + 8.0, box.top() + 6.0, box.left() + 10.5, box.top() + 1.5, box.left() + 15.5, box.top() - 0.8)
            p.setPen(QPen(ink, 1.9, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.setBrush(Qt.NoBrush)
            p.drawPath(path)
        elif mark == "mixed":
            p.setPen(QPen(ink, 2.2, Qt.SolidLine, Qt.RoundCap))
            p.drawLine(QPointF(box.left() + 4, box.center().y()), QPointF(box.right() - 4, box.center().y()))
    return paint


def popup(cap_gel):
    def paint(p, r):
        body = QRectF(0.5, 0.5, r.width() - 1, 20)
        mp.gel(p, body, POPUP_BODY, 4.5, lens_inset=3)
        cap = QRectF(body.right() - 20, body.top(), 20, body.height())
        p.save()
        p.setClipRect(cap.adjusted(0, -1, 1, 1))
        mp.gel(p, body, cap_gel, 4.5, shadow=False, lens_inset=0)
        p.restore()
        p.setPen(QColor(*cap_gel["rim"][0]))
        p.drawLine(QPointF(cap.left(), cap.top() + 1), QPointF(cap.left(), cap.bottom() - 1))
        c = cap.center() + QPointF(0.5, 0)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(18, 20, 32))
        p.drawPolygon([QPointF(c.x() - 3.5, c.y() - 1.5), QPointF(c.x() + 3.5, c.y() - 1.5), QPointF(c.x(), c.y() - 6)])
        p.drawPolygon([QPointF(c.x() - 3.5, c.y() + 1.5), QPointF(c.x() + 3.5, c.y() + 1.5), QPointF(c.x(), c.y() + 6)])
    return paint


def tab(g):
    def paint(p, r):
        # extend fill all the way to r.bottom() so pixel row H-1 is 100% opaque when overlapping
        # row 0 (#0057ae) of the accent strip
        rr = QRectF(0.5, 0.5, r.width() - 1.0, r.height() - 0.5)
        rad = 4.5
        rim_path = QPainterPath()
        rim_path.moveTo(rr.left(), r.bottom())
        rim_path.lineTo(rr.left(), rr.top() + rad)
        rim_path.quadTo(rr.left(), rr.top(), rr.left() + rad, rr.top())
        rim_path.lineTo(rr.right() - rad, rr.top())
        rim_path.quadTo(rr.right(), rr.top(), rr.right(), rr.top() + rad)
        rim_path.lineTo(rr.right(), r.bottom())
        fill_path = QPainterPath(rim_path)
        fill_path.closeSubpath()
        body = QLinearGradient(rr.topLeft(), QPointF(rr.left(), r.bottom()))
        for pos, c in g["body"]:
            body.setColorAt(pos, mp.qc(c))
        p.setBrush(body)
        p.setPen(Qt.NoPen)
        p.drawPath(fill_path)
        # lens over the top ~30%, inset from the corners
        lt = min(rr.height() * 0.32, 7.5)
        lens = QRectF(rr.left() + 2.5, rr.top() + 1.0, rr.width() - 5.0, lt)
        lg = QLinearGradient(lens.topLeft(), lens.bottomLeft())
        for pos, c in g["lens"]:
            lg.setColorAt(pos, mp.qc(c))
        p.setBrush(lg)
        p.drawRoundedRect(lens, lt * 0.45, lt * 0.45)
        # rim on the sides and top only (open at the bottom so it merges into the accent strip)
        rim = QLinearGradient(rr.topLeft(), QPointF(rr.left(), r.bottom()))
        rim.setColorAt(0.0, mp.qc(g["rim"][0]))
        rim.setColorAt(1.0, mp.qc(g["rim"][1]))
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QBrush(rim), 1.0))
        p.drawPath(rim_path)
    return paint


def thumb(vertical, active):
    def paint(p, r):
        tr = r.adjusted(1, 0, 0, 0) if vertical else r.adjusted(0, 1, 0, 0)
        tr = QRectF(tr.left(), tr.top(), tr.width() - (1 if vertical else 0), tr.height() - (0 if vertical else 1))
        rad = (tr.width() if vertical else tr.height()) / 2
        path = QPainterPath()
        path.addRoundedRect(tr, rad, rad)
        p.setPen(Qt.NoPen)
        grad = QLinearGradient(tr.topLeft(), tr.topRight() if vertical else tr.bottomLeft())
        cols = mp.THUMB_COLS if active else [(250, 250, 252), (240, 240, 244), (232, 232, 236), (226, 226, 230), (206, 206, 210), (210, 210, 214),
                                              (218, 218, 222), (226, 226, 230), (234, 234, 238), (244, 244, 246), (236, 236, 240)]
        n = len(cols)
        for i, c in enumerate(cols):
            grad.setColorAt(i / n + (0.001 if i else 0), mp.qc(c))
            grad.setColorAt((i + 1) / n, mp.qc(c))
        p.setBrush(grad)
        p.drawPath(path)
        if active:
            ends = QLinearGradient(tr.topLeft(), tr.bottomLeft() if vertical else tr.topRight())
            ln = tr.height() if vertical else tr.width()
            e = min(0.45, rad * 1.3 / ln)
            ends.setColorAt(0, QColor(10, 40, 120, 90))
            ends.setColorAt(e, QColor(10, 40, 120, 0))
            ends.setColorAt(1 - e, QColor(10, 40, 120, 0))
            ends.setColorAt(1, QColor(10, 40, 120, 90))
            p.save()
            p.setClipPath(path)
            p.setBrush(ends)
            p.drawRect(tr)
            p.restore()
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(24, 55, 115) if active else QColor(120, 120, 124), 1.0))
        p.drawRoundedRect(tr.adjusted(0.5, 0.5, -0.5, -0.5), rad - 0.5, rad - 0.5)
    return paint


def light(kind, state):
    deep = [(176, 18, 10), (194, 128, 0), (44, 134, 18)][kind]
    mid = [(242, 70, 56), (247, 193, 36), (108, 203, 58)][kind]
    lig = [(255, 184, 168), (255, 242, 176), (216, 248, 168)][kind]
    rim = [(128, 12, 6), (140, 90, 0), (29, 90, 10)][kind]
    if state == "backdrop":
        deep, mid, lig, rim = (160, 160, 164), (214, 214, 218), (250, 250, 252), (120, 120, 124)

    def paint(p, r):
        c = r.center()
        rad = 6.5
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 0, 0, 30))
        p.drawEllipse(c + QPointF(0, 0.8), rad, rad)
        body = QRadialGradient(c + QPointF(0, rad * 0.55), rad * 1.45)
        body.setColorAt(0, mp.qc(lig))
        body.setColorAt(0.45, mp.qc(mid))
        body.setColorAt(1, mp.qc(deep))
        p.setBrush(body)
        p.setPen(QPen(mp.qc(rim), 1.0))
        p.drawEllipse(c, rad, rad)
        lens = QLinearGradient(QPointF(c.x(), c.y() - rad), QPointF(c.x(), c.y()))
        lens.setColorAt(0, QColor(255, 255, 255, 240))
        lens.setColorAt(1, QColor(255, 255, 255, 30))
        p.setPen(Qt.NoPen)
        p.setBrush(lens)
        p.drawEllipse(QRectF(c.x() - rad * 0.68, c.y() - rad * 0.92, rad * 1.36, rad * 0.9))
        if state == "hover":
            p.setPen(QPen(QColor(60, 10, 0, 200), 1.4, Qt.SolidLine, Qt.RoundCap))
            g = rad * 0.45
            if kind == 0:
                p.drawLine(c + QPointF(-g * .8, -g * .8), c + QPointF(g * .8, g * .8))
                p.drawLine(c + QPointF(g * .8, -g * .8), c + QPointF(-g * .8, g * .8))
            else:
                p.drawLine(c + QPointF(-g, 0), c + QPointF(g, 0))
                if kind == 2:
                    p.drawLine(c + QPointF(0, -g), c + QPointF(0, g))
    return paint


def knob(g):
    def paint(p, r):
        mp.gel(p, QRectF(1, 0.5, 15, 15), g, 7.5, lens_inset=2.5, lens_h=0.45)
    return paint


def progress(g):
    def paint(p, r):
        mp.gel(p, r.adjusted(0.5, 0.5, -0.5, -0.5), g, 2, shadow=False, lens_inset=2)
    return paint


def expander(opened, color):
    """Disclosure triangle (HIG Figure 7-34): flat mid-grey (or white when selected), no outline."""
    def paint(p, r):
        c = r.center()
        pts = [(-4.0, -2.2), (4.0, -2.2), (0.0, 3.2)] if opened else [(-2.2, -4.0), (3.2, 0.0), (-2.2, 4.0)]
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(*color))
        p.drawPolygon([QPointF(c.x() + x, c.y() + y) for x, y in pts])
    return paint


def arrow(direction):
    def paint(p, r):
        c = r.center()
        s = 3.5
        pts = {"up": [(-s, s * .6), (s, s * .6), (0, -s * .75)], "down": [(-s, -s * .6), (s, -s * .6), (0, s * .75)],
               "left": [(s * .6, -s), (s * .6, s), (-s * .75, 0)], "right": [(-s * .6, -s), (-s * .6, s), (s * .75, 0)]}[direction]
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(34, 34, 38))
        p.drawPolygon([QPointF(c.x() + x, c.y() + y) for x, y in pts])
    return paint


def make_assets():
    for d in ("up", "down", "left", "right"):
        save(f"arrow-{d}", 9, 9, arrow(d))
    for opened, st in ((False, "closed"), (True, "open")):
        save(f"expander-{st}", 12, 12, expander(opened, (122, 122, 124)))
        save(f"expander-{st}-selected", 12, 12, expander(opened, (255, 255, 255)))
    graphite_blue = dict(rim=tuple(GRAPHITE(c) for c in mp.BLUE["rim"]),
                         body=[(p_, GRAPHITE(c)) for p_, c in mp.BLUE["body"]],
                         lens=[(p_, GRAPHITE(c)) for p_, c in mp.BLUE["lens"]])
    progress_backdrop = dict(
        rim=((120, 120, 124), (156, 156, 160)),
        body=[(p_, tuple(int(g * 0.65 + 225 * 0.35) for g in GRAPHITE(c))) for p_, c in mp.PROGRESS["body"]],
        lens=[])
    save("button", 32, 22, capsule(mp.CLEAR))
    save("button-default", 32, 22, capsule(mp.BLUE))
    save("button-pressed", 32, 22, capsule(PRESSED))
    for radio in (False, True):
        kind = "radio" if radio else "check"
        save(f"{kind}-off", 18, 18, indicator(mp.CLEAR, radio, "off"))
        save(f"{kind}-on", 18, 18, indicator(mp.BLUE, radio, "on"))
        save(f"{kind}-on-backdrop", 18, 18, indicator(mp.CLEAR, radio, "on"))
        save(f"{kind}-mixed", 18, 18, indicator(mp.BLUE, radio, "mixed"))
        save(f"{kind}-pressed", 18, 18, indicator(PRESSED, radio, "off"))
    save("popup", 48, 22, popup(mp.BLUE))
    save("popup-backdrop", 48, 22, popup(mp.CLEAR))
    tab_backdrop = dict(rim=tuple(GRAPHITE(c) for c in mp.TAB_SELECTED["rim"]),
                        body=[(p_, GRAPHITE(c)) for p_, c in mp.TAB_SELECTED["body"]],
                        lens=[(p_, GRAPHITE(c)) for p_, c in mp.TAB_SELECTED["lens"]])
    save("tab-active", 40, 24, tab(mp.TAB_SELECTED))
    save("tab-active-backdrop", 40, 24, tab(tab_backdrop))
    save("tab", 40, 23, tab(TAB_CLEAR))
    save("thumb-v", 15, 40, thumb(True, True))
    save("thumb-h", 40, 15, thumb(False, True))
    save("thumb-v-backdrop", 15, 40, thumb(True, False))
    save("thumb-h-backdrop", 40, 15, thumb(False, False))
    save("knob", 17, 17, knob(mp.BLUE))
    save("knob-backdrop", 17, 17, knob(mp.CLEAR))
    save("progress", 30, 16, progress(mp.PROGRESS))
    save("progress-backdrop", 30, 16, progress(progress_backdrop))
    save("trough", 30, 16, progress(mp.TRACK))
    for k, name in enumerate(("close", "minimize", "maximize")):
        for state in ("normal", "hover", "backdrop"):
            save(f"{name}-{state}", 16, 16, light(k, state))
    for name, (w, h, axis, a, b) in {
        "button": (32, 22, "h", 14, 14), "button-default": (32, 22, "h", 14, 14), "button-pressed": (32, 22, "h", 14, 14),
        "popup": (48, 22, "h", 9, 29), "popup-backdrop": (48, 22, "h", 9, 29),
        "tab": (40, 23, "h", 12, 12), "tab-active": (40, 24, "h", 12, 12), "tab-active-backdrop": (40, 24, "h", 12, 12),
        "progress": (30, 16, "h", 4, 4), "progress-backdrop": (30, 16, "h", 4, 4), "trough": (30, 16, "h", 4, 4),
        "thumb-v": (15, 40, "v", 7, 8), "thumb-v-backdrop": (15, 40, "v", 7, 8),
        "thumb-h": (40, 15, "h", 7, 8), "thumb-h-backdrop": (40, 15, "h", 7, 8),
    }.items():
        slice3(name, w, h, axis, a, b)
        SLICES[name] = (axis, a, b)


# ------------------------------------------------------------------ CSS

def scaled(name):
    return f'-gtk-scaled(url("assets/{name}.png"), url("assets/{name}@2.png"))'


STRIPES = "repeating-linear-gradient(to bottom, #ffffff 0px, #ffffff 1px, #eeeeee 1px, #eeeeee 2px, #e6e6e6 2px, #e6e6e6 3px, #eeeeee 3px, #eeeeee 4px)"
MENU_STRIPES = "repeating-linear-gradient(to bottom, #ffffff 0px, #ffffff 1px, #f9f9f9 1px, #f9f9f9 2px, #eeeeee 2px, #eeeeee 3px, #f9f9f9 3px, #f9f9f9 4px)"
TITLE = ("linear-gradient(to bottom, rgba(255,255,255,0.0), rgba(0,0,0,0.10)), " + STRIPES)
# fixed 11px lens on top, 8px glow at the bottom, striped body between (as in Qt and Plasma)
SELECTION = ("linear-gradient(to bottom, rgba(255,255,255,0.67), rgba(255,255,255,0.41) 3px, rgba(255,255,255,0.12) 11px), "
             "linear-gradient(to bottom, rgba(128,202,255,0), rgba(128,202,255,0.78)), "
             "repeating-linear-gradient(to bottom, rgba(255,255,255,0.13) 0px, rgba(255,255,255,0.13) 1px, rgba(0,26,100,0.17) 1px, rgba(0,26,100,0.17) 2px, "
             "rgba(0,26,100,0.26) 2px, rgba(0,26,100,0.26) 3px, rgba(0,26,100,0.17) 3px, rgba(0,26,100,0.17) 4px)")
SELECTION_LAYOUT = ("background-size: 100% 11px, 100% 8px, 100% 4px; background-position: left top, left bottom, left top; "
                    "background-repeat: no-repeat, no-repeat, repeat; "
                    "box-shadow: inset 0 1px rgba(24,66,160,0.9), inset 0 -1px rgba(40,92,180,0.8), inset 0 -2px rgba(170,225,255,0.6);")
# accent bar rows measured from HIG Figure 7-23: six blue rows, then a three-row grey shadow
ACCENT = ("linear-gradient(to bottom, #0057ae 0px, #0057ae 1px, #a2d7f0 1px, #a2d7f0 2px, #a8d1ee 2px, #a8d1ee 3px, "
          "#51b0ea 3px, #51b0ea 4px, #79ccff 4px, #79ccff 5px, #acefff 5px, #acefff 6px, #626262 6px, #626262 7px, "
          "#939393 7px, #939393 8px, rgba(226,226,226,0.9) 8px, rgba(226,226,226,0.9) 9px)")
ACCENT_BACKDROP = ("linear-gradient(to bottom, #4b5563 0px, #4b5563 1px, #c0c8d2 1px, #c0c8d2 2px, #bfc6d0 2px, #bfc6d0 3px, "
                   "#96a2b2 3px, #96a2b2 4px, #b2bcc9 4px, #b2bcc9 5px, #d2dbe6 5px, #d2dbe6 6px, #626262 6px, #626262 7px, "
                   "#939393 7px, #939393 8px, rgba(226,226,226,0.9) 8px, rgba(226,226,226,0.9) 9px)")


def common_css(v):
    """CSS shared by both versions; v is 3 or 4 and picks node names."""
    # single selectors: pseudo-classes get appended, so a selector list would only state the last item
    check = "checkbutton check" if v == 4 else "check"
    radio = "checkbutton radio" if v == 4 else "radio"
    popover = "popover > contents" if v == 4 else "popover"
    menu_bg = "popover.menu > contents, popover > contents" if v == 4 else "menu, .menu, .context-menu, popover"
    menuitem = "popover.menu modelbutton, menubar > item" if v == 4 else "menu menuitem, .menu menuitem, menubar > menuitem"
    menuitem_hover = ("popover.menu modelbutton:hover, popover.menu modelbutton:selected, menubar > item:hover, menubar > item:selected"
                      if v == 4 else "menu menuitem:hover, .menu menuitem:hover, menubar > menuitem:hover")
    scroll_trough = "scrollbar > range > trough" if v == 4 else "scrollbar trough"
    scroll_slider = "scrollbar > range > trough > slider" if v == 4 else "scrollbar slider"
    rows_sel = ("listview > row:selected, columnview > listview > row:selected, list > row:selected, treeview.view:selected, "
                "gridview > child:selected, textview > text > selection" if v == 4 else
                "treeview.view:selected, list row:selected, row:selected, iconview:selected, flowbox flowboxchild:selected")
    titlebuttons = "windowcontrols > button" if v == 4 else "headerbar button.titlebutton, .titlebar button.titlebutton"
    return f"""
/* Pinstripe for GTK {v}: Mac OS X 10.2 Aqua, measured from Apple's 2002 HIG artwork.
   Generated by tools/make_gtk_theme.py; edit the generator, not this file. */

@define-color theme_bg_color #eeeeee;
@define-color theme_fg_color #000000;
@define-color theme_base_color #ffffff;
@define-color theme_text_color #000000;
@define-color theme_selected_bg_color #3875d7;
@define-color theme_selected_fg_color #ffffff;
@define-color insensitive_fg_color #8a8a8a;
@define-color borders #969696;
@define-color accent_bg_color #3875d7;
@define-color accent_color #2d62bd;
@define-color window_bg_color #eeeeee;
@define-color window_fg_color #000000;
@define-color view_bg_color #ffffff;
@define-color view_fg_color #000000;

* {{
  outline-color: rgba(94, 146, 228, 0.6);
  outline-width: 0;
}}

window, .background, dialog {{
  background-color: #eeeeee;
  background-image: {STRIPES};
  color: #000000;
  font-family: "Lucida Grande", "Luxi Sans", "DejaVu Sans", sans-serif;
}}

label:disabled, label:backdrop:disabled {{ color: #8a8a8a; }}

/* ---------------- push buttons: 20px clear gel capsules, 14px end caps; the default pulses */
button {{
  min-height: 22px;
  min-width: 41px;
  padding: 0 13px;  /* one less than the 14px caps: the middle tucks under them, no seam */
  border-style: solid;
  border-width: 0;
  {three("button")}
  border-radius: 0;
  box-shadow: none;
  color: #000000;
  text-shadow: none;
  -gtk-icon-shadow: none;
}}
button:active, button:checked {{
  {three("button-pressed")}
}}
button:disabled {{ opacity: 0.55; color: #555555; }}
button.destructive-action {{ {three("button")} color: #a01010; }}

/* glassy bevel buttons (HIG Figures 7-14, 7-15): curved glass cushion with a top specular lens,
   cool silver mid-tone dip, bottom white reflection and dark bottom rim; smoked glass when toggled */
button.image-button,
button.bevel,
.linked > button {{
  min-height: 20px;
  min-width: 20px;
  padding: 4px 6px;
  border-image: none;
  border: 1px solid #888a90;
  border-top-color: #989aa0;
  border-bottom-color: #52545a;
  border-radius: 4.5px;
  background-image:
    linear-gradient(to bottom, rgba(255, 255, 255, 0.96) 0%, rgba(250, 251, 254, 0.84) 58%, rgba(242, 245, 250, 0.56) 100%),
    radial-gradient(ellipse at 50% 100%, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.50) 52%, rgba(255, 255, 255, 0.0) 82%),
    linear-gradient(to right, rgba(150, 158, 174, 0.23) 0px, rgba(150, 158, 174, 0.0) 6px, rgba(150, 158, 174, 0.0) calc(100% - 6px), rgba(150, 158, 174, 0.23) 100%),
    linear-gradient(to bottom, #ecedf2 0%, #e4e7ee 26%, #d8dce4 32%, #e2e5eb 62%, #f4f5f8 86%, #ffffff 100%);
  background-size: calc(100% - 5px) 30%, 100% 45%, 100% 100%, 100% 100%;
  background-position: center 1px, center bottom, left top, left top;
  background-repeat: no-repeat;
  background-origin: padding-box;
  background-clip: padding-box;
  box-shadow: inset 0 1px rgba(255, 255, 255, 0.90), 0 1px 1.5px rgba(0, 0, 0, 0.18);
  animation: none;
}}
button.image-button:active,
button.image-button:checked,
button.bevel:active,
button.bevel:checked,
.linked > button:active,
.linked > button:checked {{
  border-color: #62646a;
  border-top-color: #686a70;
  border-bottom-color: #4a4c52;
  background-image:
    linear-gradient(to bottom, rgba(240, 244, 250, 0.84) 0%, rgba(216, 220, 228, 0.58) 60%, rgba(198, 202, 210, 0.34) 100%),
    radial-gradient(ellipse at 50% 100%, rgba(238, 242, 250, 0.62) 0%, rgba(238, 242, 250, 0.24) 52%, rgba(238, 242, 250, 0.0) 82%),
    linear-gradient(to right, rgba(86, 92, 106, 0.24) 0px, rgba(86, 92, 106, 0.0) 6px, rgba(86, 92, 106, 0.0) calc(100% - 6px), rgba(86, 92, 106, 0.24) 100%),
    linear-gradient(to bottom, #c0c3ca 0%, #b8bcc4 26%, #a6aab2 32%, #acb0b8 65%, #c0c4cb 88%, #d0d4da 100%);
  background-size: calc(100% - 5px) 30%, 100% 45%, 100% 100%, 100% 100%;
  background-position: center 1px, center bottom, left top, left top;
  background-repeat: no-repeat;
  background-origin: padding-box;
  background-clip: padding-box;
  box-shadow: inset 0 1px rgba(255, 255, 255, 0.45), 0 1px 1px rgba(0, 0, 0, 0.14);
}}
button.bevel label,
button.image-button.text-button:not(.flat) label {{
  font-size: 77%;
}}

button.suggested-action, button.default, button.default:focus, .linked > button.suggested-action {{
  padding: 0 13px;
  border-width: 0;
  border-radius: 0;
  box-shadow: none;
  {three("button-default")}
  animation: pinstripe-pulse 1.7s ease-in-out infinite;
}}
button.suggested-action:backdrop, button.default:backdrop, .linked > button.suggested-action:backdrop {{
  padding: 0 13px;
  border-width: 0;
  border-radius: 0;
  box-shadow: none;
  {three("button")}
  animation: none;
}}
@keyframes pinstripe-pulse {{
  0% {{ opacity: 1.0; }}
  50% {{ opacity: 0.78; }}
  100% {{ opacity: 1.0; }}
}}

/* flat and toolbar buttons: no frame in Aqua, darken while pressed; small system font labels */
toolbar, .toolbar {{
  background: none;
  border-bottom: 1px solid #a3a3a3;
  padding: 4px 6px;
}}
toolbar button label, .toolbar button label {{
  font-size: 84.6%;
}}
button.flat, headerbar button:not(.titlebutton):not(.suggested-action):not(.close):not(.minimize):not(.maximize), toolbar button, .toolbar button,
button.image-button.flat, popover button.flat, button.circular.flat {{
  border-image: none;
  border-width: 0;
  padding: 3px 6px;
  border-radius: 4px;
  background: transparent;
  box-shadow: none;
  animation: none;
}}
button.flat > *, headerbar button:not(.titlebutton):not(.close):not(.minimize):not(.maximize) > *, toolbar button > *, .toolbar button > * {{ margin: 0; }}
button.flat:hover, headerbar button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):hover {{ background-color: rgba(0, 0, 0, 0.06); }}
button.flat:active, button.flat:checked, headerbar button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):active, headerbar button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):checked,
toolbar button:active, toolbar button:checked, .toolbar button:active, .toolbar button:checked {{ background-color: rgba(0, 0, 0, 0.18); }}

/* ---------------- check boxes and radio buttons: 18x18 including the shadow */
{check} {{
  min-width: 18px; min-height: 18px;
  margin: 0 5px 0 0;
  border: none; background: none; box-shadow: none;
  -gtk-icon-source: {scaled("check-off")};
  background-image: {scaled("check-off")};
  background-size: 18px 18px;
  color: transparent;
}}
{check}:checked {{ background-image: {scaled("check-on")}; -gtk-icon-source: none; }}
{check}:checked:backdrop {{ background-image: {scaled("check-on-backdrop")}; }}
{check}:indeterminate {{ background-image: {scaled("check-mixed")}; -gtk-icon-source: none; }}
{check}:active {{ background-image: {scaled("check-pressed")}; }}
{check}:disabled {{ opacity: 0.5; }}
{radio} {{
  min-width: 18px; min-height: 18px;
  margin: 0 5px 0 0;
  border: none; background: none; box-shadow: none;
  -gtk-icon-source: none;
  background-image: {scaled("radio-off")};
  background-size: 18px 18px;
  color: transparent;
}}
{radio}:checked {{ background-image: {scaled("radio-on")}; }}
{radio}:checked:backdrop {{ background-image: {scaled("radio-on-backdrop")}; }}
{radio}:active {{ background-image: {scaled("radio-pressed")}; }}
{radio}:disabled {{ opacity: 0.5; }}

/* ---------------- text fields: 22px, 3px inner shadow, blue focus ring */
entry, spinbutton:not(.vertical), textview.view border {{
  min-height: 20px;
  padding: 0 5px;
  background-color: #ffffff;
  background-image: linear-gradient(to bottom, rgba(0,0,0,0.20), rgba(0,0,0,0) 3px);
  color: #000000;
  border: 1px solid #9e9ea2;
  border-top-color: #707074;
  border-bottom-color: #b8b8bc;
  border-radius: 0;
  box-shadow: none;
  caret-color: #000000;
}}
entry:focus-within, entry:focus, spinbutton:focus-within, spinbutton:focus {{
  box-shadow: 0 0 0 1px rgba(94, 146, 228, 0.85), 0 0 0 3.5px rgba(94, 146, 228, 0.45);
}}
entry:disabled, spinbutton:disabled {{ color: #8a8a8a; background-color: #f4f4f4; }}
entry selection, text selection, entry > text > selection, label selection {{ background-color: #b5d5ff; color: #000000; }}

/* ---------------- views and lists */
.view, treeview.view, list, listview, columnview, iconview, textview text, textview > text {{
  background-color: #ffffff;
  color: #000000;
}}
{rows_sel} {{
  background-color: #286cda;
  background-image: {SELECTION};
  {SELECTION_LAYOUT}
  color: #ffffff;
}}
treeview.view:selected:backdrop, list row:selected:backdrop, listview > row:selected:backdrop, row:selected:backdrop {{
  background-image: none;
  background-color: #d4d4d4;
  color: #000000;
}}
treeview.view header button, columnview > header > button {{
  border-image: none;
  border-width: 0 1px 1px 0;
  border-style: solid;
  border-color: #a8a8ac #96969a #96969a #b4b4b8;
  padding: 1px 6px;
  min-height: 16px;
  font-size: 84.6%;
  font-weight: normal;
  color: #000000;
  background-image: linear-gradient(to bottom, #ffffff 0%, #f2f2f2 50%, #eaeaec 51%, #f6f6f8 100%);
  background-size: 100% 100%;
  background-repeat: no-repeat;
  background-origin: padding-box;
  background-clip: padding-box;
  box-shadow: none;
  animation: none;
}}
treeview.view header button label, columnview > header > button label {{
  font-size: 100%;
  font-weight: normal;
  color: #000000;
}}
treeview.view header button.sorted, columnview > header > button.sorted {{
  border-color: #0057ae #286ebe #286ebe #286ebe;
  background-image: linear-gradient(to bottom, #aad2ee 0%, #96c7e7 22%, #a0cdec 42%, #56b2eb 45%, #7ccfff 70%, #acf0ff 100%);
}}
treeview.view header button > *, columnview > header > button > * {{ margin: 0; }}
{"treeview.view header button sort-indicator, columnview > header > button sort-indicator { min-width: 9px; min-height: 9px; }" if v == 4 else "treeview.view header button arrow { min-width: 9px; min-height: 9px; }"}
{"treeview.view header button sort-indicator.descending, columnview > header > button sort-indicator.descending" if v == 4 else "treeview.view header button arrow.down"} {{ -gtk-icon-source: {scaled("arrow-down")}; }}
{"treeview.view header button sort-indicator.ascending, columnview > header > button sort-indicator.ascending" if v == 4 else "treeview.view header button arrow.up"} {{ -gtk-icon-source: {scaled("arrow-up")}; }}

/* disclosure triangles (HIG Figure 7-34): flat mid-grey without outline, white on selected rows */
treeview.view.expander {{
  min-width: 12px;
  min-height: 12px;
  color: #7a7a7c;
  -gtk-icon-source: {scaled("expander-closed")};
  {"-gtk-icon-transform: none;" if v == 3 else ""}
}}
treeview.view.expander:checked {{ -gtk-icon-source: {scaled("expander-open")}; }}
treeview.view.expander:selected {{ -gtk-icon-source: {scaled("expander-closed-selected")}; color: #ffffff; }}
treeview.view.expander:checked:selected {{ -gtk-icon-source: {scaled("expander-open-selected")}; color: #ffffff; }}
treeview.view.expander:selected:backdrop {{ -gtk-icon-source: {scaled("expander-closed")}; color: #7a7a7c; }}
treeview.view.expander:checked:selected:backdrop {{ -gtk-icon-source: {scaled("expander-open")}; color: #7a7a7c; }}
{"expander-widget > box > title > expander, treeexpander > expander" if v == 4 else "expander arrow, expander > title > arrow"} {{
  min-width: 12px;
  min-height: 12px;
  -gtk-icon-source: {scaled("expander-closed")};
  {"-gtk-icon-transform: none;" if v == 3 else ""}
}}
{"expander-widget > box > title > expander:checked, treeexpander > expander:checked" if v == 4 else "expander arrow:checked, expander > title > arrow:checked"} {{
  -gtk-icon-source: {scaled("expander-open")};
}}

/* list and scroll frames vs group boxes (HIG Figures 8-2 to 8-4) */
scrolledwindow.frame, scrolledwindow > border, viewport.frame {{
  border: 1px solid #96969a;
  border-top-color: #76767a;
  border-radius: 0;
}}
frame > label {{
  font-size: 84.6%;
  font-weight: normal;
  color: #000000;
  padding: 0 4px;
  margin: 0 6px;
}}
{"""frame {
  border: none;
  border-radius: 0;
  box-shadow: none;
  padding: 0 12px 12px 12px;
  background-image:
    linear-gradient(to bottom, rgba(0, 0, 0, 0.24) 0px, rgba(0, 0, 0, 0.24) 1px, rgba(255, 255, 255, 0.78) 1px, rgba(255, 255, 255, 0.78) 2px),
    linear-gradient(to bottom, rgba(255, 255, 255, 0.78) 0px, rgba(255, 255, 255, 0.78) 1px, rgba(0, 0, 0, 0.24) 1px, rgba(0, 0, 0, 0.24) 2px),
    linear-gradient(to right, rgba(0, 0, 0, 0.24) 0px, rgba(0, 0, 0, 0.24) 1px, rgba(255, 255, 255, 0.78) 1px, rgba(255, 255, 255, 0.78) 2px),
    linear-gradient(to right, rgba(255, 255, 255, 0.78) 0px, rgba(255, 255, 255, 0.78) 1px, rgba(0, 0, 0, 0.24) 1px, rgba(0, 0, 0, 0.24) 2px);
  background-position: left 8px, left bottom, left 8px, right 8px;
  background-size: 100% 2px, 100% 2px, 2px calc(100% - 8px), 2px calc(100% - 8px);
  background-repeat: no-repeat;
}
frame > label {
  margin: 0 0 6px -4px;
  padding: 0 4px;
  background-color: #eeeeee;
  background-image: """ + STRIPES + """;
}
frame.flat {
  background: none;
  padding: 0;
}""" if v == 4 else """frame {
  background: none;
  border: none;
}
frame > border {
  border: 1px solid rgba(0, 0, 0, 0.24);
  border-radius: 0;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.78);
  padding: 10px 12px 12px 12px;
}
frame.flat > border {
  border: none;
  box-shadow: none;
  padding: 0;
}"""}

/* ---------------- scroll bars: 15px white cylinder, gel thumb, arrows together */
scrollbar {{
  background-color: #ffffff;
  background-image: linear-gradient(to right, #cccccc 0%, #ececec 25%, #ffffff 50%, #fafafa 85%, #e8e8e8 100%);
  border: 0;
}}
scrollbar.horizontal {{ background-image: linear-gradient(to bottom, #cccccc 0%, #ececec 25%, #ffffff 50%, #fafafa 85%, #e8e8e8 100%); border-top: 1px solid #96969a; }}
scrollbar.vertical {{ border-left: 1px solid #96969a; }}
{scroll_trough} {{
  border-radius: 8px;
  background-color: #ffffff;
  margin: 0;
}}
scrollbar.vertical {scroll_trough.split()[-1]} {{ background-image: linear-gradient(to right, #b0b0b0 0%, #c0c0c0 10%, #d4d4d4 22%, #f0f0f0 40%, #ffffff 55%, #fafafa 85%, #e4e4e4 100%); }}
scrollbar.horizontal {scroll_trough.split()[-1]} {{ background-image: linear-gradient(to bottom, #b0b0b0 0%, #c0c0c0 10%, #d4d4d4 22%, #f0f0f0 40%, #ffffff 55%, #fafafa 85%, #e4e4e4 100%); }}
{scroll_slider} {{
  min-width: 13px; min-height: 13px;
  margin: 0;
  border-radius: 0;
  border-style: solid;
  background: none;
}}
scrollbar.vertical slider {{
  min-height: 24px;
  padding: 6px 0 7px 0;
  border-width: 0;
  {three("thumb-v")}
}}
scrollbar.horizontal slider {{
  min-width: 24px;
  padding: 0 7px 0 6px;
  border-width: 0;
  {three("thumb-h")}
}}
scrollbar.vertical slider:backdrop {{ {three("thumb-v-backdrop")} }}
scrollbar.horizontal slider:backdrop {{ {three("thumb-h-backdrop")} }}
scrollbar button {{
  min-width: 15px; min-height: 15px;
  padding: 0; border-width: 0; border-image: none; animation: none;
  background: transparent; color: #222226;
}}
scrollbar button > * {{ margin: 0; }}
scrollbar button:active {{ background-color: rgba(0, 0, 60, 0.15); }}
scrollbar button.up {{ -gtk-icon-source: {scaled("arrow-up")}; }}
scrollbar button.down {{ -gtk-icon-source: {scaled("arrow-down")}; }}
scrollbar button.left {{ -gtk-icon-source: {scaled("arrow-left")}; }}
scrollbar button.right {{ -gtk-icon-source: {scaled("arrow-right")}; }}
{"""scrollbar {
  -GtkScrollbar-has-backward-stepper: false;
  -GtkScrollbar-has-forward-stepper: true;
  -GtkScrollbar-has-secondary-backward-stepper: true;
  -GtkScrollbar-has-secondary-forward-stepper: false;
}""" if v == 3 else ""}

/* spin buttons: Aqua little arrows rather than big +/- buttons */
spinbutton:not(.vertical) button, spinbutton > button, spinbutton > button.image-button {{
  min-width: 15px; min-height: 18px;
  padding: 0;
  border-image: none;
  border-width: 0 0 0 1px;
  border-style: solid;
  border-color: #b4b4b8;
  border-radius: 0;
  box-shadow: none;
  background-image: linear-gradient(to bottom, #fdfdfe, #e4e6ea 45%, #d6dade 50%, #f6f7f9);
  animation: none;
  color: #222226;
}}
spinbutton button image {{ opacity: 0; }}
{"spinbutton button { -gtk-icon-transform: scale(0); }" if v == 3 else ""}
spinbutton button.up {{ background-image: {scaled("arrow-up")}, linear-gradient(to bottom, #fdfdfe, #e4e6ea 45%, #d6dade 50%, #f6f7f9); background-repeat: no-repeat; background-position: center; background-size: 9px 9px, 100% 100%; }}
spinbutton button.down {{ background-image: {scaled("arrow-down")}, linear-gradient(to bottom, #fdfdfe, #e4e6ea 45%, #d6dade 50%, #f6f7f9); background-repeat: no-repeat; background-position: center; background-size: 9px 9px, 100% 100%; }}
spinbutton button.up:active {{ background-image: {scaled("arrow-up")}, linear-gradient(to bottom, #b8c8e8, #8fb0e8 45%, #6f98e0 50%, #a8d0ff); }}
spinbutton button.down:active {{ background-image: {scaled("arrow-down")}, linear-gradient(to bottom, #b8c8e8, #8fb0e8 45%, #6f98e0 50%, #a8d0ff); }}

/* ---------------- sliders: dark 6px track, 15px round gel thumb */
scale {{ min-height: 22px; min-width: 22px; padding: 0; }}
scale trough {{
  min-height: 6px; min-width: 6px;
  border-radius: 3px;
  border: 1px solid #545458;
  background-image: linear-gradient(to bottom, #606064, #8c8c90 45%, #c8c8cc);
}}
scale.vertical trough {{ background-image: linear-gradient(to right, #606064, #8c8c90 45%, #c8c8cc); }}
scale highlight {{ background: none; border: none; }}
scale slider {{
  min-width: 17px; min-height: 17px;
  margin: -7px;
  background-image: {scaled("knob")};
  background-size: 17px 17px;
  background-color: transparent;
  border: none; box-shadow: none;
}}
scale slider:backdrop {{ background-image: {scaled("knob-backdrop")}; }}

/* ---------------- progress bars: light gel groove, blue gel fill (grey in the background) */
progressbar trough {{
  min-height: 16px; min-width: 16px;
  padding: 0 3px;
  border-style: solid;
  border-width: 0;
  {three("trough")}
}}
progressbar progress {{
  min-height: 16px; min-width: 8px;
  padding: 0 3px;
  margin: 0;
  border-style: solid;
  border-width: 0;
  {three("progress")}
}}
progressbar progress:backdrop {{ {three("progress-backdrop")} }}
progressbar.osd progress {{ min-height: 4px; }}

/* ---------------- notebooks: 23px tabs centred over a 6px blue accent bar */
/* the notebook itself has no frame: tabs stand free on the window stripes, and the
   border only starts below the accent bar, around the pane */
notebook, notebook.frame {{ border: none; background: none; box-shadow: none; }}
notebook > header {{ background: none; border: none; padding: 0; }}
notebook > header.top {{
  padding: 0 10px 9px 10px;
  background-image: {ACCENT};
  background-size: 100% 9px;
  background-position: bottom;
  background-repeat: no-repeat;
}}
notebook > header.top:backdrop {{
  background-image: {ACCENT_BACKDROP};
}}
notebook > header tab {{
  min-height: 23px;
  padding: 0 11px;
  margin: 0 -1px 0 0;
  background-color: transparent;
  border-style: solid;
  border-width: 0;
  {three("tab")}
  color: #000000;
}}
/* extend 1px down over row 0 (#0057ae) of the accent strip so the selected tab morphs into it;
   keep padding-bottom 0 so the content-box middle slice reaches the bottom pixel row too */
notebook > header tab:checked {{
  min-height: 24px;
  margin: 0 -1px -1px 0;
  padding: 0 11px;
  {three("tab-active")}
}}
notebook > header tab:checked:backdrop {{
  min-height: 24px;
  margin: 0 -1px -1px 0;
  padding: 0 11px;
  {three("tab-active-backdrop")}
}}
notebook > stack:not(:only-child) {{
  background-color: rgba(0, 0, 0, 0.03);
  background-image: linear-gradient(to bottom, rgba(0,0,0,0.16), rgba(0,0,0,0) 6px);
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-top: none;
}}

/* ---------------- menus and popovers: pinstriped sheets, glossy pinstriped selection */
{menu_bg} {{
  background-color: #f9f9f9;
  background-image: {MENU_STRIPES};
  border: 1px solid rgba(0, 0, 0, 0.18);
  border-radius: 5px;
  padding: 4px 0;
  color: #000000;
}}
{menuitem} {{
  min-height: 19px;
  padding: 0 20px;
  color: #000000;
  border-radius: 0;
  background: none;
}}
{menuitem_hover} {{
  background-color: #286cda;
  background-image: {SELECTION};
  {SELECTION_LAYOUT}
  color: #ffffff;
}}
menubar {{
  background-color: #f9f9f9;
  background-image: {MENU_STRIPES};
  border-bottom: 1px solid #969696;
  padding: 0 8px;
}}
menubar > {"item" if v == 4 else "menuitem"} {{ padding: 2px 9px; min-height: 18px; }}
separator {{ background: none; min-height: 1px; min-width: 1px; }}
{popover} separator, menu separator {{ margin: 5px 0; background: none; }}

/* ---------------- combo boxes / drop-downs: white pop-up with the blue double-arrow cap */
combobox button.combo, dropdown > button, button.dropdown, combobox > box > button {{
  min-height: 22px;
  padding: 0 28px 0 8px;
  border-style: solid;
  border-width: 0;
  border-radius: 0;
  box-shadow: none;
  {three("popup")}
  animation: none;
}}
combobox button.combo:backdrop, dropdown > button:backdrop {{ {three("popup-backdrop")} }}
combobox arrow, dropdown arrow {{ -gtk-icon-source: none; min-width: 0; min-height: 0; }}

/* ---------------- tooltips (help tags, HIG Figure 14-1): pale yellow, 11pt small system font */
tooltip, tooltip.background {{
  background-color: rgba(255, 255, 199, 0.96);
  background-image: none;
  border: 1px solid rgba(0, 0, 0, 0.38);
  border-radius: 0;
  color: #000000;
  font-size: 84.6%;
  padding: 2px 6px;
  box-shadow: none;
}}
tooltip * {{ color: #000000; padding: 0; margin: 0; }}

/* ---------------- switches: a little gel track */
switch {{
  min-width: 40px; min-height: 20px;
  border-radius: 10px;
  border: 1px solid #6c6c70;
  background-image: linear-gradient(to bottom, #c8c8cc, #e4e4e8 50%, #fafafc);
}}
switch:checked {{ background-image: linear-gradient(to bottom, #5c8cd6, #62a2ee 45%, #a3e4ff); border-color: #1a2c70; }}
switch slider {{
  min-width: 18px; min-height: 18px;
  border-radius: 9px;
  border: 1px solid #6c6c70;
  background-image: linear-gradient(to bottom, #ffffff, #e0e0e4 50%, #f8f8fa);
}}

/* ---------------- title bars (client-side decorations): 10.2 pinstripes, traffic lights */
headerbar, .titlebar {{
  min-height: 22px;
  padding: 0 8px;
  background-color: #e8e8e8;
  background-image: {TITLE};
  border-bottom: 1px solid #7f7f7f;
  box-shadow: none;
  color: #000000;
}}
headerbar:backdrop, .titlebar:backdrop {{ color: #8b8b8b; }}
headerbar .title, .titlebar .title {{ font-weight: normal; }}
{titlebuttons}, {titlebuttons}.image-button {{
  min-width: 15px; min-height: 15px;
  padding: 0; margin: 0 3.5px;
  border: none; border-image: none;
  background-color: transparent;
  background-size: 15px 15px;
  background-repeat: no-repeat;
  background-position: center;
  color: transparent;
{"  -gtk-icon-size: 0;" if v == 4 else "  -gtk-icon-transform: scale(0);"}
  animation: none;
  box-shadow: none;
}}
{titlebuttons} > * {{ margin: 0; opacity: 0; }}
"""


def lights_css(v):
    base = "windowcontrols > button" if v == 4 else "headerbar button.titlebutton, .titlebar button.titlebutton"
    out = []
    for name in ("close", "minimize", "maximize"):
        sels = ", ".join(f"{s.strip()}.{name}" for s in base.split(","))
        out.append(f"{sels} {{ background-image: {scaled(name + '-normal')}; }}")
        hov = ", ".join(f"{s.strip()}.{name}:hover" for s in base.split(","))
        out.append(f"{hov} {{ background-image: {scaled(name + '-hover')}; }}")
        bd = ", ".join(f"{s.strip()}.{name}:backdrop" for s in base.split(","))
        out.append(f"{bd} {{ background-image: {scaled(name + '-backdrop')}; }}")
    # traffic lights on the left, as on 10.2
    out.append('/* Put the window buttons on the left in the order close, minimize, maximize: '
               'gsettings set org.gnome.desktop.wm.preferences button-layout "close,minimize,maximize:" */')
    return "\n".join(out) + "\n"


def build():
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    make_assets()
    for v in (3, 4):
        d = os.path.join(OUT, f"gtk-{v}.0")
        os.makedirs(d, exist_ok=True)
        os.symlink("../assets", os.path.join(d, "assets"))
        with open(os.path.join(d, "gtk.css"), "w") as f:
            f.write(common_css(v) + lights_css(v))
    with open(os.path.join(OUT, "index.theme"), "w") as f:
        f.write("[Desktop Entry]\nType=X-GNOME-Metatheme\nName=Pinstripe\nComment=Mac OS X 10.2 Aqua for GTK\nEncoding=UTF-8\n\n"
                "[X-GNOME-Metatheme]\nGtkTheme=Pinstripe\nIconTheme=Oxygen-Pinstripe\n")
    print("wrote", OUT)


if __name__ == "__main__":
    build()
