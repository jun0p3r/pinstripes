#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Generate the "Oxygen Pinstripe" icon theme (icons/Oxygen-Pinstripe).

It provides two Mac OS X 10.2 "Jaguar" layers on top of Oxygen:

1. Full-colour 10.2 Aqua action icons (16, 22, 24, 32, 32@2x and 48 px in Context=Actions),
   modelled on and sampled from Apple's June 2002 Aqua Human Interface Guidelines (Chapter 11,
   Figures 11-18, 11-19 and dialog artwork): round clear-glass navigation buttons (Back/Forward
   with triangle + twin dots, Help '?'), sky-blue pinstriped folders with navy-outlined '+'
   badges, curled white pages, front-on desktop printer, Sherlock silver-rimmed glass magnifier,
   yellow wooden Compose pencil, perforated blue and crimson Mail stamps, Finder Home cottage,
   glossy ruby Favorites heart, crossed Utilities hammer & wrench, Disc Burner trefoil, and
   Preview rotate cards.

2. Solid, rounded symbolic & menu-extra SVGs (AirPort fan, speaker with waves, horizontal
   battery, eject key, solid triangle arrows) with KDE's ColorScheme-Text class so Qt, Plasma
   and GTK recolour them cleanly.

    python3 tools/make_icons.py
"""
import math
import os
import shutil
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QPointF, QRectF, Qt  # noqa: E402
from PySide6.QtGui import (  # noqa: E402
    QBrush,
    QColor,
    QFont,
    QGuiApplication,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QPen,
    QPolygonF,
    QRadialGradient,
    QTransform,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "icons", "Oxygen-Pinstripe")
FAINT = 0.35


# ==================================================================
# Part 1: Symbolic & Menu-Extra Vector Glyphs (16x16 grid)
# ==================================================================

def rr(x, y, w, h, r=0):
    p = QPainterPath()
    p.addRoundedRect(QRectF(x, y, w, h), r, r)
    return p


def circ(cx, cy, r):
    p = QPainterPath()
    p.addEllipse(QPointF(cx, cy), r, r)
    return p


def ellipse(cx, cy, rx, ry):
    p = QPainterPath()
    p.addEllipse(QPointF(cx, cy), rx, ry)
    return p


def poly(*pts, round_=0.0):
    p = QPainterPath()
    p.addPolygon(QPolygonF([QPointF(x, y) for x, y in pts]))
    p.closeSubpath()
    if round_:
        p = U(p, stroke(p, round_))
    return p


# Menu-extra (panel) glyphs are rebuilt with thinner lines: Jaguar's menu bar extras are hairline
# arcs and waves around small solid bodies. build() sets this to MENU_EXTRA_STROKE for the panel set.
STROKE_SCALE = 1.0
MENU_EXTRA_STROKE = 0.6


def stroke(path, width, cap=Qt.RoundCap, join=Qt.RoundJoin):
    s = QPainterPathStroker()
    s.setWidth(width * STROKE_SCALE)
    s.setCapStyle(cap)
    s.setJoinStyle(join)
    return s.createStroke(path).simplified()


def line(x1, y1, x2, y2, w=2.0, cap=Qt.RoundCap):
    p = QPainterPath()
    p.moveTo(x1, y1)
    p.lineTo(x2, y2)
    return stroke(p, w, cap)


def polyline(pts, w=2.0, cap=Qt.RoundCap):
    p = QPainterPath()
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    return stroke(p, w, cap)


def arc(cx, cy, r, start, span, w=2.0, cap=Qt.RoundCap):
    """Arc stroke; angles in degrees, 0 = 3 o'clock, counter-clockwise (Qt convention)."""
    p = QPainterPath()
    rect = QRectF(cx - r, cy - r, 2 * r, 2 * r)
    p.arcMoveTo(rect, start)
    p.arcTo(rect, start, span)
    return stroke(p, w, cap)


def ring(cx, cy, r, w):
    w *= STROKE_SCALE
    return S(circ(cx, cy, r + w / 2), circ(cx, cy, r - w / 2))


def U(*paths):
    out = QPainterPath()
    for p in paths:
        out = out.united(p)
    return out.simplified()


def S(a, *bs):
    for b in bs:
        a = a.subtracted(b)
    return a.simplified()


def rot(path, deg, cx=8, cy=8):
    t = QTransform().translate(cx, cy).rotate(deg).translate(-cx, -cy)
    return t.map(path)


def flip_h(path):
    return QTransform(-1, 0, 0, 1, 16, 0).map(path)


def move(path, dx, dy):
    return path.translated(dx, dy)


def scale(path, f, cx=8, cy=8):
    return QTransform().translate(cx, cy).scale(f, f).translate(-cx, -cy).map(path)


def triangle(direction, cx=8, cy=8, s=5.0):
    h = s * 0.9
    pts = {"down": [(cx - s, cy - h / 2), (cx + s, cy - h / 2), (cx, cy + h / 2 + 0.4)],
           "up": [(cx - s, cy + h / 2), (cx + s, cy + h / 2), (cx, cy - h / 2 - 0.4)],
           "right": [(cx - h / 2, cy - s), (cx - h / 2, cy + s), (cx + h / 2 + 0.4, cy)],
           "left": [(cx + h / 2, cy - s), (cx + h / 2, cy + s), (cx - h / 2 - 0.4, cy)]}[direction]
    return poly(*pts, round_=1.0)


def arrow(direction):
    base = U(poly((8, 1.6), (14.2, 8), (10.4, 8), (10.4, 8), (5.6, 8), (1.8, 8), round_=1.0), rr(5.9, 7, 4.2, 7.6, 1.2))
    return rot(base, {"up": 0, "right": 90, "down": 180, "left": 270}[direction])


def speaker():
    return U(rr(1.5, 5.6, 3.6, 4.8, 0.8), poly((4.4, 5.6), (8.6, 2.0), (8.6, 14.0), (4.4, 10.4), round_=0.8))


def waves():
    return arc(7.0, 8, 3.6, -42, 84, 1.7), arc(7.0, 8, 6.4, -46, 92, 1.7)


def fan_arcs():
    cx, cy = 8, 13.2
    return (circ(cx, cy, 1.45), arc(cx, cy, 4.0, 45, 90, 1.9), arc(cx, cy, 7.0, 45, 90, 1.9), arc(cx, cy, 10.0, 47, 86, 1.9))


def battery_shell():
    t = max(0.9, 1.6 * STROKE_SCALE)
    return U(S(rr(0.8, 4.2, 13.4, 7.6, 1.8), rr(0.8 + t, 4.2 + t, 13.4 - 2 * t, 7.6 - 2 * t, 0.8)), rr(14.3, 6.2, 1.5, 3.6, 0.6))


def battery_fill(level):
    w = 9.2 * level
    return rr(2.9, 6.3, max(0.0, w), 3.4, 0.5) if w > 0.1 else QPainterPath()


def bolt():
    return poly((8.9, 2.6), (4.9, 8.6), (7.6, 8.6), (6.6, 13.4), (11.1, 7.0), (8.3, 7.0), (9.4, 2.6))


def page(corner=True):
    p = QPainterPath()
    p.moveTo(3, 1.5)
    p.lineTo(9.6, 1.5)
    p.lineTo(13, 4.9)
    p.lineTo(13, 14.5)
    p.lineTo(3, 14.5)
    p.closeSubpath()
    p = U(p, stroke(p, 1.0))
    if corner:
        p = S(p, poly((9.0, 0.8), (13.7, 0.8), (13.7, 5.5)))
        p = U(p, poly((9.6, 1.5), (9.6, 4.9), (13, 4.9), round_=0.6))
        p = S(p, line(9.3, 1.3, 13.2, 5.2, 0.9))
    return p


def folder():
    tab = rr(1.2, 2.6, 6.0, 3.2, 1.2)
    body = rr(1.2, 4.2, 13.6, 9.6, 1.6)
    return S(U(tab, body), rr(1.0, 5.6, 14.0, 0.9))


def gear(teeth=8, r_out=7.0, r_in=5.2, hole=2.2):
    g = circ(8, 8, r_in)
    for i in range(teeth):
        g = U(g, rot(rr(6.7, 8 - r_out, 2.6, 3.0, 0.6), i * 360 / teeth))
    return S(g, circ(8, 8, hole))


def magnifier():
    return U(ring(6.6, 6.6, 4.0, 2.0), line(9.6, 9.6, 13.8, 13.8, 2.8))


def monitor():
    return U(S(rr(1.2, 1.8, 13.6, 9.6, 1.6), rr(2.8, 3.4, 10.4, 6.4, 0.6)), rr(6.6, 11.2, 2.8, 2.2), rr(4.2, 13.1, 7.6, 1.6, 0.8))


def person(cx=8, s=1.0):
    return U(circ(cx, 4.6 * s + (1 - s) * 8, 3.0 * s), move(scale(rr(2.2, 9.0, 11.6, 6.6, 3.2), s, cx, 15), 0, 0))


def check_mark(w=2.5):
    p = QPainterPath()
    p.moveTo(2.6, 8.6)
    p.lineTo(6.2, 12.6)
    p.cubicTo(8.0, 8.0, 10.4, 4.4, 14.0, 2.4)
    return stroke(p, w)


def plus(cx=8, cy=8, s=5.5, w=2.6):
    return U(line(cx - s, cy, cx + s, cy, w), line(cx, cy - s, cx, cy + s, w))


def cross(cx=8, cy=8, s=4.6, w=2.6):
    return U(line(cx - s, cy - s, cx + s, cy + s, w), line(cx + s, cy - s, cx - s, cy + s, w))


def info_glyph(cx=8):
    return U(circ(cx, 4.8, 1.25), rr(cx - 1.1, 7.0, 2.2, 5.6, 0.8))


def bang_glyph(cx=8, top=4.2, bottom=10.0):
    return U(rr(cx - 1.1, top, 2.2, bottom - top, 1.0), circ(cx, bottom + 2.0, 1.2))


def question_glyph(cx=8):
    q = arc(cx, 6.0, 2.6, -60, 240, 2.1, Qt.FlatCap)
    q = U(q, polyline([(cx + 1.3, 8.2), (cx, 9.2), (cx, 10.2)], 2.1, Qt.FlatCap), circ(cx, 12.6, 1.2))
    return q


def padlock():
    return U(S(rr(2.6, 7.0, 10.8, 7.8, 1.6), circ(8, 10.4, 1.3), rr(7.4, 10.4, 1.2, 2.6)), arc(8, 6.4, 3.3, 0, 180, 2.0, Qt.FlatCap),
             rr(3.7, 6.3, 2.0, 1.4), rr(10.3, 6.3, 2.0, 1.4))


def clock_hands():
    return U(rr(7.2, 3.6, 1.6, 5.2, 0.8), rot(rr(7.2, 7.2, 1.6, 4.4, 0.8), -50))


def star(cx=8, cy=8.4, ro=7.2, ri=3.0):
    pts = []
    for i in range(10):
        r = ro if i % 2 == 0 else ri
        a = math.radians(-90 + i * 36)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return poly(*pts, round_=0.9)


def envelope():
    return S(rr(1.2, 3.2, 13.6, 9.6, 1.6), polyline([(1.8, 4.0), (8, 9.0), (14.2, 4.0)], 1.1))


def circular_arrow(clockwise=True):
    a = arc(8, 8.4, 5.0, 60, 280, 2.2, Qt.FlatCap)
    head = poly((9.0, 0.6), (13.6, 3.8), (8.6, 6.4), round_=0.6)
    p = U(a, head)
    return p if clockwise else flip_h(p)


def circular_arrow_small():
    return scale(circular_arrow(True), 0.62)


def undo_arrow():
    a = arc(9.0, 10.0, 4.6, 0, 160, 2.2, Qt.FlatCap)
    head = poly((0.8, 9.0), (6.6, 8.2), (3.0, 13.6), round_=0.6)
    return U(a, head, rr(12.5, 9.6, 2.2, 3.4, 1.0))


def build_symbolic_icons():
    I = {}

    def add(names, solid, faint=None):
        for n in names.split():
            I[n] = (solid, faint)

    # volume
    w1, w2 = waves()
    add("audio-volume-high audio-on audio-speakers", U(speaker(), w1, w2))
    add("audio-volume-medium", U(speaker(), w1), w2)
    add("audio-volume-low", speaker(), U(w1, w2))
    add("audio-volume-muted audio-off", U(speaker(), cross(12.2, 8, 2.2, 1.8)))
    add("audio-input-microphone", U(rr(5.4, 1.2, 5.2, 8.6, 2.6), arc(8, 6.6, 4.6, 180, 180, 1.6, Qt.FlatCap), rr(7.2, 11.0, 1.6, 2.6), rr(4.6, 13.2, 6.8, 1.6, 0.8)))
    add("audio-headphones", U(arc(8, 9, 5.8, 0, 180, 1.8, Qt.FlatCap), rr(1.4, 8.6, 3.4, 5.8, 1.4), rr(11.2, 8.6, 3.4, 5.8, 1.4)))

    # wireless: the 10.2 AirPort fan
    d, a1, a2, a3 = fan_arcs()
    add("network-wireless network-wireless-signal-excellent network-wireless-100 network-wireless-connected-100 network-wireless-signal-excellent-secure", U(d, a1, a2, a3))
    add("network-wireless-signal-good network-wireless-80 network-wireless-connected-75 network-wireless-60", U(d, a1, a2), a3)
    add("network-wireless-signal-ok network-wireless-40 network-wireless-connected-50", U(d, a1), U(a2, a3))
    add("network-wireless-signal-weak network-wireless-20 network-wireless-connected-25", d, U(a1, a2, a3))
    add("network-wireless-signal-none network-wireless-0 network-wireless-disconnected network-wireless-offline network-wireless-connected-00", QPainterPath(), U(d, a1, a2, a3))
    add("network-wired network-wired-activated network-connect", U(rr(4.0, 5.0, 8.0, 6.0, 1.6), rr(5.4, 1.6, 1.8, 3.8, 0.6), rr(8.8, 1.6, 1.8, 3.8, 0.6), rr(7.1, 10.6, 1.8, 4.2, 0.6)))
    add("network-wired-disconnected network-offline network-disconnect", QPainterPath(), U(rr(4.0, 5.0, 8.0, 6.0, 1.6), rr(5.4, 1.6, 1.8, 3.8, 0.6), rr(8.8, 1.6, 1.8, 3.8, 0.6), rr(7.1, 10.6, 1.8, 4.2, 0.6)))
    add("network-vpn", U(padlock()))

    # battery: the horizontal 10.2 battery
    for pct in (0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100):
        lvl = pct / 100
        name = f"battery-{pct:03d}"
        add(name, U(battery_shell(), battery_fill(lvl)))
        charging = S(U(battery_shell(), battery_fill(lvl)), stroke(bolt(), 1.6))
        add(f"{name}-charging", U(charging, bolt()))
    add("battery-100-charged battery-full-charged", U(battery_shell(), battery_fill(1.0)))
    for alias, pct in (("battery-full", 100), ("battery-good", 80), ("battery-low", 30), ("battery-caution", 10), ("battery-empty", 0)):
        add(alias, *I[f"battery-{pct:03d}"])
        add(f"{alias}-charging", *I[f"battery-{pct:03d}-charging"])
    add("battery-missing", QPainterPath(), battery_shell())

    # bluetooth: rune knocked out of an oval
    rune = polyline([(5.2, 5.3), (10.6, 10.4), (8.0, 13.0), (8.0, 3.0), (10.6, 5.6), (5.2, 10.7)], 1.4)
    oval = ellipse(8, 8, 5.4, 7.2)
    add("bluetooth bluetooth-active preferences-system-bluetooth bluetooth-online", S(oval, rune))
    add("bluetooth-disabled bluetooth-inactive bluetooth-offline", QPainterPath(), S(oval, rune))

    # notifications: a bell
    bell = U(circ(8, 6.6, 4.3), rr(3.7, 6.6, 8.6, 4.4), rr(1.8, 10.6, 12.4, 2.0, 1.0), circ(8, 13.7, 1.6), circ(8, 2.0, 1.1))
    add("notifications preferences-desktop-notification notification-active", bell)
    add("notification-inactive notifications-disabled", QPainterPath(), bell)
    add("notification-new", U(S(bell, circ(12.8, 3.4, 3.4)), circ(12.8, 3.4, 2.4)))

    # session
    add("system-shutdown application-exit", U(arc(8, 8.8, 5.2, 120, 300, 2.2), line(8, 1.6, 8, 7.6, 2.2)))
    add("system-reboot view-refresh reload", circular_arrow(True))
    add("object-rotate-right", circular_arrow(True))
    add("object-rotate-left", circular_arrow(False))
    add("system-lock-screen object-locked lock", padlock())
    add("object-unlocked", U(S(rr(2.6, 7.0, 10.8, 7.8, 1.6), circ(8, 10.4, 1.3)), arc(11.2, 6.4, 3.3, 0, 180, 2.0, Qt.FlatCap), rr(12.5, 6.3, 2.0, 2.6)))
    add("system-log-out", U(S(rr(1.6, 1.6, 8.0, 12.8, 1.4), rr(3.2, 3.2, 4.8, 9.6, 0.6)), move(arrow("right"), 3.0, 0)))
    add("system-suspend", U(S(circ(8, 8, 6.4), circ(10.6, 6.0, 5.4))))

    # search, settings, input
    add("system-search edit-find search", magnifier())
    add("zoom-in", U(S(magnifier(), circ(6.6, 6.6, 3.0)), plus(6.6, 6.6, 2.0, 1.4)))
    add("zoom-out", U(S(magnifier(), circ(6.6, 6.6, 3.0)), line(4.6, 6.6, 8.6, 6.6, 1.4)))
    add("zoom-original zoom-fit-best", U(S(magnifier(), circ(6.6, 6.6, 3.0)), circ(6.6, 6.6, 1.4)))
    add("preferences-system configure settings-configure emblem-system preferences-other", gear())
    keyboard = rr(0.8, 3.6, 14.4, 8.8, 1.6)
    keys = QPainterPath()
    for row, y in enumerate((5.2, 7.4)):
        for i in range(6):
            keys = U(keys, rr(2.2 + i * 2.0 + row * 0.6, y, 1.4, 1.4, 0.3))
    keys = U(keys, rr(4.2, 9.6, 7.6, 1.4, 0.3))
    add("input-keyboard preferences-desktop-keyboard", S(keyboard, keys))
    add("input-mouse", S(rr(4.0, 1.4, 8.0, 13.2, 4.0), rr(7.4, 2.6, 1.2, 3.6, 0.6)))

    # places and files
    trash = U(rr(2.2, 3.2, 11.6, 1.9, 0.7), S(rr(5.8, 1.2, 4.4, 2.6, 0.8), rr(7.0, 2.2, 2.0, 1.2)),
              S(poly((3.4, 5.6), (12.6, 5.6), (11.7, 14.6), (4.3, 14.6), round_=0.8), rr(5.4, 7.2, 0.9, 5.8, 0.4), rr(7.55, 7.2, 0.9, 5.8, 0.4), rr(9.7, 7.2, 0.9, 5.8, 0.4)))
    add("user-trash edit-trash edit-delete-shred user-trash-empty", trash)
    add("user-trash-full", trash)
    add("folder folder-closed inode-directory folder-documents", folder())
    add("folder-new", U(S(folder(), circ(12.4, 4.2, 3.6)), plus(12.4, 4.2, 2.4, 1.7)))
    add("folder-open document-open", U(S(U(rr(1.2, 2.6, 6.0, 3.2, 1.2), rr(1.2, 4.2, 13.6, 9.6, 1.6)), rr(1.0, 6.0, 14.4, 9.0)),
                                         poly((2.6, 7.0), (15.4, 7.0), (13.6, 13.8), (1.0, 13.8), round_=0.8)))
    add("user-home go-home folder-home", S(U(poly((8, 1.2), (15.2, 8.2), (0.8, 8.2), round_=0.8), rr(3.2, 7.4, 9.6, 7.4, 0.8)), rr(6.8, 9.8, 2.4, 5.2, 0.5)))
    add("folder-download download go-down-skip", S(folder(), move(scale(arrow("down"), 0.55), 0, 1.6)))
    add("text-x-generic document-new-from-template x-office-document", S(page(), rr(5.0, 7.0, 6.0, 1.0, 0.4), rr(5.0, 9.2, 6.0, 1.0, 0.4), rr(5.0, 11.4, 4.0, 1.0, 0.4)))
    add("document-new", S(page(), plus(8, 9.6, 2.6, 1.6)))
    add("document-save document-save-as", U(S(rr(1.6, 1.6, 12.8, 12.8, 1.8), rr(4.4, 1.0, 7.2, 4.6, 0.6), rr(4.0, 8.6, 8.0, 5.0, 0.6)), rr(8.6, 2.2, 1.6, 2.6, 0.4)))
    printer = U(S(rr(1.2, 5.6, 13.6, 6.4, 1.6), rr(3.6, 9.6, 8.8, 3.0)), rr(4.0, 1.6, 8.0, 3.4, 0.6), S(rr(4.0, 9.8, 8.0, 4.8, 0.6), rr(5.2, 11.2, 5.6, 0.9), rr(5.2, 12.8, 5.6, 0.9)))
    add("document-print printer", printer)
    add("document-properties", S(circ(8, 8, 7.0), info_glyph()))
    add("edit-copy", U(S(rr(1.4, 1.4, 8.8, 10.2, 1.4), rr(3.0, 3.0, 5.6, 7.0, 0.6)), rr(5.2, 4.4, 9.4, 10.2, 1.4)))
    scissors = U(ring(4.4, 11.6, 2.0, 1.7), ring(11.6, 11.6, 2.0, 1.7), line(5.6, 9.6, 11.0, 1.6, 1.8), line(10.4, 9.6, 5.0, 1.6, 1.8))
    add("edit-cut", scissors)
    add("edit-paste", U(S(rr(2.2, 2.6, 11.6, 12.2, 1.6), rr(4.0, 5.0, 8.0, 8.2, 0.6)), rr(5.0, 1.0, 6.0, 3.2, 1.0), rr(5.6, 6.6, 4.8, 1.0, 0.4), rr(5.6, 8.8, 4.8, 1.0, 0.4), rr(5.6, 11.0, 3.2, 1.0, 0.4)))
    add("edit-delete edit-clear-all window-close dialog-close process-close tab-close", cross())
    add("edit-clear edit-clear-locationbar-rtl edit-clear-locationbar-ltr", S(poly((5.0, 2.6), (14.6, 2.6), (14.6, 13.4), (5.0, 13.4), (0.8, 8.0), round_=1.2), cross(9.4, 8.0, 2.4, 1.6)))
    add("edit-undo mail-reply-sender mail-reply-all", undo_arrow())
    add("edit-redo mail-forward", flip_h(undo_arrow()))
    add("edit-select-all", U(*[rr(x, y, 2.2, 2.2, 0.4) for x, y in ((1.4, 1.4), (6.9, 1.4), (12.4, 1.4), (1.4, 6.9), (12.4, 6.9), (1.4, 12.4), (6.9, 12.4), (12.4, 12.4))], rr(4.6, 4.6, 6.8, 6.8, 1.0)))
    add("edit-rename document-edit edit-entry", U(rot(U(rr(6.6, 0.8, 2.8, 10.6, 0.8), poly((6.6, 11.8), (9.4, 11.8), (8.0, 14.6))), 40), rr(1.4, 13.6, 7.0, 1.4, 0.6)))
    add("bookmark-new bookmarks emblem-favorite starred bookmark", star())
    add("non-starred", QPainterPath(), star())
    add("mail-unread mail-message mail-message-new mail-receive internet-mail", envelope())
    add("mail-send", rot(poly((1.0, 7.4), (15.0, 1.6), (9.6, 15.0), (7.6, 9.0), round_=0.8), 0))
    add("appointment-new office-calendar view-calendar x-office-calendar", U(S(rr(1.4, 2.6, 13.2, 12.0, 1.6), rr(3.0, 6.4, 10.0, 6.6, 0.4)), rr(4.0, 1.0, 1.8, 3.4, 0.8), rr(10.2, 1.0, 1.8, 3.4, 0.8),
                                                                                 *[rr(4.0 + i * 3.0, 7.6 + j * 2.6, 1.8, 1.6, 0.3) for i in range(3) for j in range(2)]))
    add("chronometer clock preferences-system-time", S(circ(8, 8, 6.8), circ(8, 8, 5.4)).united(clock_hands()).simplified())

    # devices
    add("computer video-display computer-laptop preferences-desktop-display", monitor())
    add("drive-harddisk drive-harddisk-solidstate", S(rr(0.8, 4.4, 14.4, 7.2, 2.0), circ(12.0, 8.0, 1.0), rr(3.0, 7.4, 5.6, 1.2, 0.5)))
    add("media-optical drive-optical media-optical-cd-audio tools-media-optical-burn", S(circ(8, 8, 7.0), circ(8, 8, 1.6)))
    add("drive-removable-media media-removable drive-removable-media-usb", U(rr(4.0, 6.0, 8.0, 9.0, 1.4), S(rr(5.2, 1.0, 5.6, 5.6, 0.6), rr(6.4, 2.2, 1.0, 1.2), rr(8.6, 2.2, 1.0, 1.2))))
    add("camera-photo camera-web", S(U(rr(0.8, 4.2, 14.4, 9.6, 1.8), rr(5.0, 2.4, 6.0, 2.6, 0.8)), ring(8, 8.9, 2.6, 1.5)))
    add("phone smartphone", S(rr(4.0, 0.8, 8.0, 14.4, 1.8), rr(5.4, 2.6, 5.2, 9.4, 0.4), circ(8, 13.4, 0.8)))
    add("printer-network network-workgroup network-server", U(rr(1.6, 1.4, 12.8, 4.0, 1.0), rr(1.6, 6.0, 12.8, 4.0, 1.0), rr(7.2, 10.0, 1.6, 2.6), rr(2.4, 12.6, 11.2, 1.6, 0.8)))
    add("user-identity system-users user avatar-default", person())
    add("system-users group", U(move(scale(person(), 0.72, 8, 15), -3.2, 0), move(scale(person(), 0.72, 8, 15), 3.2, 0)))
    add("weather-clear", U(circ(8, 8, 3.2), *[rot(rr(7.2, 0.8, 1.6, 3.0, 0.8), a) for a in range(0, 360, 45)]))

    # navigation: solid arrows and 10.2 Back/Forward triangle + dots
    for d, names in (("up", "go-up arrow-up"), ("down", "go-down arrow-down")):
        add(names, arrow(d))
    add("go-previous go-previous-symbolic-rtl arrow-left", U(triangle("left", 4.6, 8, 4.6), circ(9.8, 8, 1.35), circ(13.6, 8, 1.35)))
    add("go-next arrow-right", U(circ(2.4, 8, 1.35), circ(6.2, 8, 1.35), triangle("right", 11.4, 8, 4.6)))
    for d, names in (("down", "pan-down go-down-search list-drop-down"), ("up", "pan-up"), ("left", "pan-start pan-end-rtl"), ("right", "pan-end pan-start-rtl")):
        add(names, triangle(d))
    add("go-top", U(move(scale(arrow("up"), 0.85, 8, 1.6), 0, 1.8), rr(2.0, 1.0, 12.0, 2.0, 1.0)))
    add("go-bottom", U(move(scale(arrow("down"), 0.85, 8, 14.4), 0, -1.8), rr(2.0, 13.0, 12.0, 2.0, 1.0)))
    add("go-first media-skip-backward", U(triangle("left", 9.0, 8, 4.8), rr(2.2, 3.0, 2.2, 10.0, 0.8)))
    add("go-last media-skip-forward", U(triangle("right", 7.0, 8, 4.8), rr(11.6, 3.0, 2.2, 10.0, 0.8)))
    add("media-seek-forward", U(triangle("right", 5.2, 8, 4.6), triangle("right", 10.6, 8, 4.6)))
    add("media-seek-backward", U(triangle("left", 5.4, 8, 4.6), triangle("left", 10.8, 8, 4.6)))
    add("go-jump", U(arc(8.0, 10.0, 5.4, 70, 110, 2.2, Qt.FlatCap), poly((9.0, 1.4), (14.6, 4.6), (9.0, 8.0), round_=0.6)))

    # media
    add("media-playback-start player-play", triangle("right", 8.6, 8, 6.0))
    add("media-playback-pause player-pause", U(rr(3.4, 2.4, 3.4, 11.2, 1.0), rr(9.2, 2.4, 3.4, 11.2, 1.0)))
    add("media-playback-stop player-stop", rr(2.8, 2.8, 10.4, 10.4, 1.6))
    add("media-eject", U(triangle("up", 8, 6.4, 6.0), rr(2.0, 11.0, 12.0, 2.6, 0.9)))
    add("media-record", circ(8, 8, 5.6))
    add("media-playlist-repeat", U(arc(8, 8, 5.2, 20, 320, 2.0, Qt.FlatCap), poly((12.0, 1.8), (15.2, 5.6), (10.4, 6.2), round_=0.4)))

    # window, lists, menus, views
    add("window-minimize", rr(2.4, 10.4, 11.2, 2.6, 1.2))
    add("window-maximize", S(rr(2.0, 2.0, 12.0, 12.0, 1.6), rr(4.2, 5.0, 7.6, 6.8, 0.4)))
    add("window-restore", U(S(rr(5.0, 1.6, 9.4, 9.4, 1.4), rr(6.8, 4.2, 5.8, 5.0, 0.3)), S(rr(1.6, 5.0, 9.4, 9.4, 1.4), rr(3.4, 7.6, 5.8, 5.0, 0.3))))
    add("list-add add value-increase tab-new", plus())
    add("list-remove remove value-decrease", line(2.5, 8, 13.5, 8, 2.6))
    add("open-menu application-menu hamburger-menu", U(rr(2.0, 3.0, 12.0, 2.2, 1.1), rr(2.0, 6.9, 12.0, 2.2, 1.1), rr(2.0, 10.8, 12.0, 2.2, 1.1)))
    add("view-more view-more-horizontal overflow-menu", U(circ(3.2, 8, 1.6), circ(8, 8, 1.6), circ(12.8, 8, 1.6)))
    add("view-more-vertical", U(circ(8, 3.2, 1.6), circ(8, 8, 1.6), circ(8, 12.8, 1.6)))
    add("view-list view-list-details view-list-text", U(*[U(circ(2.6, y, 1.3), rr(5.4, y - 1.0, 9.0, 2.0, 1.0)) for y in (3.6, 8.0, 12.4)]))
    add("view-grid view-list-icons view-app-grid", U(*[rr(x, y, 5.4, 5.4, 1.2) for x in (1.6, 9.0) for y in (1.6, 9.0)]))
    add("view-file-columns view-column", S(rr(1.2, 2.2, 13.6, 11.6, 1.4), rr(2.8, 3.8, 2.6, 8.4), rr(6.7, 3.8, 2.6, 8.4), rr(10.6, 3.8, 2.6, 8.4)))
    add("view-list-tree", U(rr(1.6, 2.6, 8.0, 2.0, 0.9), rr(4.8, 6.8, 9.2, 2.0, 0.9), rr(4.8, 11.0, 9.2, 2.0, 0.9)))
    add("view-filter", U(poly((1.6, 2.4), (14.4, 2.4), (9.6, 8.2), (9.6, 13.8), (6.4, 12.4), (6.4, 8.2), round_=0.8)))
    add("view-sort sort", U(rr(1.6, 3.0, 12.8, 2.0, 1.0), rr(1.6, 7.0, 9.0, 2.0, 1.0), rr(1.6, 11.0, 5.2, 2.0, 1.0)))
    add("sidebar-show view-left-pane view-split-left-right", S(rr(1.2, 2.2, 13.6, 11.6, 1.6), rr(6.2, 3.8, 7.0, 8.4, 0.4)))
    add("view-fullscreen", U(polyline([(1.8, 6.0), (1.8, 1.8), (6.0, 1.8)], 2.0), polyline([(10.0, 1.8), (14.2, 1.8), (14.2, 6.0)], 2.0),
                              polyline([(14.2, 10.0), (14.2, 14.2), (10.0, 14.2)], 2.0), polyline([(6.0, 14.2), (1.8, 14.2), (1.8, 10.0)], 2.0)))
    add("object-select emblem-ok checkmark dialog-ok emblem-default", check_mark())
    add("process-stop", S(circ(8, 8, 7.0), cross(8, 8, 3.0, 2.0)))
    add("dialog-cancel", S(circ(8, 8, 7.0), cross(8, 8, 3.0, 2.0)))

    # dialogs
    add("dialog-information help-about info", S(circ(8, 8, 7.0), info_glyph()))
    add("help-contents help-browser help-faq dialog-question", S(circ(8, 8, 7.0), question_glyph()))
    add("dialog-warning data-warning", S(poly((8, 1.2), (15.2, 14.2), (0.8, 14.2), round_=1.4), bang_glyph(8, 5.4, 10.0)))
    add("dialog-error data-error emblem-important", S(poly(*[(8 + 7.2 * math.cos(math.radians(22.5 + i * 45)), 8 + 7.2 * math.sin(math.radians(22.5 + i * 45))) for i in range(8)], round_=0.8), bang_glyph(8, 3.6, 9.4)))
    add("emblem-shared emblem-symbolic-link", arrow("right"))

    # Plasma 6 tray names
    add("network-bluetooth network-bluetooth-activated network-bluetooth-activated-locked network-wireless-bluetooth", S(oval, rune))
    add("network-bluetooth-inactive", QPainterPath(), S(oval, rune))
    sun_core, sun_rays = circ(8, 8, 3.2), U(*[rot(rr(7.2, 0.6, 1.6, 3.0, 0.8), a) for a in range(0, 360, 45)])
    add("brightness-high high-brightness video-display-brightness display-brightness", U(sun_core, sun_rays))
    add("brightness-medium", U(sun_core, *[rot(rr(7.2, 0.6, 1.6, 3.0, 0.8), a) for a in range(0, 360, 90)]), U(*[rot(rr(7.2, 0.6, 1.6, 3.0, 0.8), a) for a in range(45, 360, 90)]))
    add("brightness-low low-brightness", sun_core, sun_rays)
    upd = circ(8, 8, 7.0)
    add("update-low update-medium update-high kpackagekit-updates system-software-update software-update-available", S(upd, move(scale(arrow("down"), 0.62), 0, 0.2)))
    add("update-none", S(upd, scale(check_mark(2.6), 0.62)))
    add("update-busy", S(upd, circular_arrow_small()))
    mic = U(rr(5.4, 1.2, 5.2, 8.6, 2.6), arc(8, 6.6, 4.6, 180, 180, 1.6, Qt.FlatCap), rr(7.2, 11.0, 1.6, 2.6), rr(4.6, 13.2, 6.8, 1.6, 0.8))
    add("mic-on mic-ready microphone-sensitivity-high microphone-sensitivity-medium audio-input-microphone-high audio-input-microphone-medium", mic)
    add("microphone-sensitivity-low audio-input-microphone-low", mic)
    add("mic-off microphone-sensitivity-muted audio-input-microphone-muted", U(S(mic, line(2.0, 2.0, 14.0, 14.0, 3.4)), line(2.6, 2.6, 13.4, 13.4, 1.6)))
    add("media-playback-playing", triangle("right", 8.6, 8, 6.0))
    add("media-playback-paused", U(rr(3.4, 2.4, 3.4, 11.2, 1.0), rr(9.2, 2.4, 3.4, 11.2, 1.0)))
    add("media-playback-stopped", rr(2.8, 2.8, 10.4, 10.4, 1.6))
    cam = S(U(rr(0.8, 4.2, 14.4, 9.6, 1.8), rr(5.0, 2.4, 6.0, 2.6, 0.8)), ring(8, 8.9, 2.6, 1.5))
    add("camera-on camera-ready", cam)
    add("camera-off", U(S(cam, line(1.6, 1.6, 14.4, 14.4, 3.4)), line(2.2, 2.2, 13.8, 13.8, 1.6)))
    add("klipper edit-paste-style", U(S(rr(2.2, 2.6, 11.6, 12.2, 1.6), rr(4.0, 5.0, 8.0, 8.2, 0.6)), rr(5.0, 1.0, 6.0, 3.2, 1.0), rr(5.6, 6.6, 4.8, 1.0, 0.4), rr(5.6, 8.8, 4.8, 1.0, 0.4), rr(5.6, 11.0, 3.2, 1.0, 0.4)))
    add("kdeconnect-tray kdeconnect", S(rr(4.0, 0.8, 8.0, 14.4, 1.8), rr(5.4, 2.6, 5.2, 9.4, 0.4), circ(8, 13.4, 0.8)))
    add("input-keyboard-virtual-on input-keyboard-virtual-off keyboard-layout", S(keyboard, keys))
    fd, fa1, fa2, fa3 = fan_arcs()
    add("network-wireless-acquiring network-wireless-available network-wireless-on", U(fd, fa1), U(fa2, fa3))
    add("network-wireless-off", QPainterPath(), U(fd, fa1, fa2, fa3))
    for base, extra in (("network-wireless-signal-excellent", ("network-wireless-100-locked", "network-wireless-100-limited", "network-wireless-80-locked", "network-wireless-80-limited", "network-wireless-connected-80")),
                        ("network-wireless-signal-good", ("network-wireless-60-locked", "network-wireless-60-limited", "network-wireless-connected-60")),
                        ("network-wireless-signal-ok", ("network-wireless-40-locked", "network-wireless-40-limited", "network-wireless-connected-40")),
                        ("network-wireless-signal-weak", ("network-wireless-20-locked", "network-wireless-20-limited", "network-wireless-connected-20")),
                        ("network-wireless-signal-none", ("network-wireless-0-locked", "network-wireless-0-limited")),
                        ("audio-volume-high", ("audio-volume-high-danger", "audio-volume-high-warning"))):
        for n in extra:
            I[n] = I[base]
    for pct in (0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100):
        for prof in ("balanced", "performance", "powersave"):
            I[f"battery-{pct:03d}-profile-{prof}"] = I[f"battery-{pct:03d}"]
            I[f"battery-{pct:03d}-charging-profile-{prof}"] = I[f"battery-{pct:03d}-charging"]

    return I


# ==================================================================
# Part 2: Full-Colour Mac OS X 10.2 "Jaguar" Action Icons (32x32 canvas)
# ==================================================================
# Colours and proportions sampled directly from Apple's June 2002 Aqua HIG:
# - Finder toolbar (ch11-212-021.png): Back clear-glass circle (#646464 rim, #dedede..#959595
#   mid dip, #ffffff lower reflection, black triangle + twin dots), View bevel pills, Home
#   cottage (#fbf9f2 wall, #2c2a28 roof, #9c5c26 door), Favorites ruby heart (#e61e14),
#   Utilities crossed hammer & wrench, Sherlock magnifier, New Folder (#d9f7f9..#5b96da with
#   pinstripes and #38527d-outlined white '+' badge).
# - Mail toolbar (ch11-212-022.png): Compose yellow pencil (#ffe798..#b98332, #e85a54 eraser),
#   perforated blue stamps (#85a6eb..#5c88e0), crimson Bounce stamp (#ad1001..#711a11),
#   spiral blue '@' Address book, front-on silver/white desktop printer, Get Mail envelope.
# - Print dialog (all-116-080.png): round clear-glass '?' Help button.
# - Formatting palette (all-091-057.png): serif B/I/U and paragraph alignment/indent bars.

def c(hex_or_rgba, a=None):
    col = QColor(hex_or_rgba) if isinstance(hex_or_rgba, str) else QColor(*hex_or_rgba)
    if a is not None:
        col.setAlpha(a)
    return col


def vgrad(y0, y1, *stops, x0=16.0, x1=16.0):
    g = QLinearGradient(QPointF(x0, y0), QPointF(x1, y1))
    for pos, col in stops:
        g.setColorAt(pos, c(col))
    return g


def rgrad(cx, cy, r, *stops, fx=None, fy=None):
    g = QRadialGradient(QPointF(cx, cy), r, QPointF(cx if fx is None else fx, cy if fy is None else fy))
    for pos, col in stops:
        g.setColorAt(pos, c(col))
    return g


def floor_shadow(p, cx=16.0, cy=28.5, rx=11.0, ry=2.6, alpha=70):
    p.save()
    p.setPen(Qt.NoPen)
    p.translate(cx, cy)
    p.scale(rx, ry)
    g = QRadialGradient(QPointF(0, 0), 1.0)
    g.setColorAt(0.0, QColor(0, 0, 0, alpha))
    g.setColorAt(0.55, QColor(0, 0, 0, int(alpha * 0.45)))
    g.setColorAt(1.0, QColor(0, 0, 0, 0))
    p.setBrush(g)
    p.drawEllipse(QPointF(0, 0), 1.0, 1.0)
    p.restore()


#Palette presets for 10.2 round glass action discs
DISC_PALETTES = {
    # Sampled from Finder Back button (ch11-212-021.png col x=33, y=23..44)
    "clear": ("#5c5e63", (0.0, "#dcdedf"), (0.34, "#d2d4d8"), (0.50, "#9e9fa4"), (0.72, "#e8eaed"), (0.90, "#ffffff"), (1.0, "#cfd2d6")),
    # Aqua blue gel (Get Info, OK/Confirm)
    "blue":  ("#0d3c82", (0.0, "#b8dcff"), (0.38, "#3e82e8"), (0.50, "#1d5cc9"), (0.75, "#4da0f5"), (0.92, "#94e6ff"), (1.0, "#50b4f8")),
    # Jaguar crimson gel (Delete, Stop, Close, Record)
    "red":   ("#660e06", (0.0, "#ffb8b0"), (0.38, "#de3222"), (0.50, "#ad1206"), (0.76, "#e03422"), (0.92, "#ff8b78"), (1.0, "#d42b1c")),
    # Aqua emerald gel (Add, Apply, Run)
    "green": ("#1b5c10", (0.0, "#ccf8b4"), (0.38, "#4ec032"), (0.50, "#289214"), (0.76, "#58ca38"), (0.92, "#c8ff9c"), (1.0, "#4eb832")),
}


def glass_disc(p, cx=16.0, cy=15.5, r=12.0, kind="clear", octagon=False):
    """10.2 round (or octagonal Stop) Aqua glass button with top lens and lower glow."""
    floor_shadow(p, cx, cy + r * 0.92, r * 0.95, 2.7, 78)
    rim, *stops = DISC_PALETTES[kind]

    shape = QPainterPath()
    if octagon:
        pts = [QPointF(cx + r * 1.05 * math.cos(math.radians(22.5 + i * 45)),
                       cy + r * 1.05 * math.sin(math.radians(22.5 + i * 45))) for i in range(8)]
        shape.addPolygon(QPolygonF(pts))
        shape.closeSubpath()
    else:
        shape.addEllipse(QPointF(cx, cy), r, r)

    p.save()
    p.setPen(Qt.NoPen)
    p.setBrush(vgrad(cy - r, cy + r, *stops, x0=cx, x1=cx))
    p.drawPath(shape)

    # Subtle radial pillow shading around outer perimeter (sampled on Back x=21..24: #ac..#bd)
    p.setClipPath(shape)
    pillow = QRadialGradient(QPointF(cx, cy + r * 0.18), r * 1.04)
    pillow.setColorAt(0.0, QColor(255, 255, 255, 0))
    pillow.setColorAt(0.74, QColor(0, 0, 0, 0))
    pillow.setColorAt(1.0, QColor(0, 0, 0, 58 if kind == "clear" else 75))
    p.setBrush(pillow)
    p.drawRect(QRectF(cx - r - 2, cy - r - 2, 2 * r + 4, 2 * r + 4))

    # Crisp top specular glass lens crescent
    lens_r = QRectF(cx - r * 0.68, cy - r + 1.1, r * 1.36, r * 0.82)
    lens_g = vgrad(lens_r.top(), lens_r.bottom(),
                   (0.0, (255, 255, 255, 242)),
                   (0.55, (255, 255, 255, 135)),
                   (1.0, (255, 255, 255, 18)), x0=cx, x1=cx)
    p.setBrush(lens_g)
    p.drawEllipse(lens_r)
    p.restore()

    p.setPen(QPen(c(rim), 1.15))
    p.setBrush(Qt.NoBrush)
    p.drawPath(shape)


def draw_disc_glyph(p, path, dark=True):
    """Crisp etched glyph inside an Aqua glass button."""
    p.save()
    p.setPen(Qt.NoPen)
    if dark:
        p.setBrush(QColor(255, 255, 255, 155))
        p.drawPath(path.translated(0, 0.85))
        p.setBrush(c("#16171a"))
        p.drawPath(path)
    else:
        p.setBrush(QColor(0, 0, 0, 105))
        p.drawPath(path.translated(0, 0.95))
        p.setBrush(c("#ffffff"))
        p.drawPath(path)
    p.restore()


def bevel_tile(p, x=3.5, y=5.5, w=25.0, h=20.0, r=3.5):
    """Finder 'View' style clear-glass bevelled rectangular pill."""
    floor_shadow(p, x + w / 2, y + h + 1.2, w * 0.46, 2.0, 58)
    rect = QRectF(x, y, w, h)
    path = QPainterPath()
    path.addRoundedRect(rect, r, r)
    p.setPen(Qt.NoPen)
    p.setBrush(vgrad(y, y + h,
                     (0.0, "#ffffff"),
                     (0.42, "#e3e5ea"),
                     (0.48, "#cfd3da"),
                     (0.85, "#f4f5f8"),
                     (1.0, "#ffffff")))
    p.drawPath(path)
    # Top lens
    lens = QPainterPath()
    lens.addRoundedRect(QRectF(x + 1.2, y + 1.0, w - 2.4, h * 0.42), r - 0.8, r - 0.8)
    p.setBrush(vgrad(y + 1.0, y + 1.0 + h * 0.42, (0.0, (255, 255, 255, 220)), (1.0, (255, 255, 255, 30))))
    p.drawPath(lens)
    p.setPen(QPen(c("#686b73"), 1.05))
    p.setBrush(Qt.NoBrush)
    p.drawPath(path)


def plus_badge(p, cx=24.0, cy=8.5, s=5.2, arm=2.2):
    """Exact 10.2 Finder 'New Folder' white '+' badge with #35507c dark navy outline."""
    bar1 = QPainterPath()
    bar1.addRoundedRect(QRectF(cx - s, cy - arm / 2, 2 * s, arm), 0.6, 0.6)
    bar2 = QPainterPath()
    bar2.addRoundedRect(QRectF(cx - arm / 2, cy - s, arm, 2 * s), 0.6, 0.6)
    cross_p = bar1.united(bar2).simplified()
    p.save()
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(0, 20, 55, 70))
    p.drawPath(cross_p.translated(0.5, 1.0))
    p.setPen(QPen(c("#2f4b7c"), 2.3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(vgrad(cy - s, cy + s, (0.0, "#ffffff"), (1.0, "#dceeff"), x0=cx, x1=cx))
    p.drawPath(cross_p)
    p.setPen(Qt.NoPen)
    p.drawPath(cross_p)
    p.restore()


def aqua_arrow_path(cx, cy, r_outer, r_inner, start_deg, span_deg, clockwise=True):
    """Curved glossy 3D arrow path (used for Undo, Redo, Refresh, Rotate, Revert)."""
    rmid = (r_outer + r_inner) / 2.0
    thick = r_outer - r_inner
    rect = QRectF(cx - rmid, cy - rmid, 2 * rmid, 2 * rmid)
    trim = 18.0 if span_deg > 0 else -18.0
    body_span = span_deg - trim if abs(span_deg) > 40 else span_deg * 0.75

    p = QPainterPath()
    p.arcMoveTo(rect, start_deg)
    p.arcTo(rect, start_deg, body_span)
    st = QPainterPathStroker()
    st.setWidth(thick)
    st.setCapStyle(Qt.FlatCap)
    body = st.createStroke(p)
    # Round the tail end only so the head joins cleanly into the triangle base
    sr = math.radians(start_deg)
    tail = circ(cx + rmid * math.cos(sr), cy - rmid * math.sin(sr), thick / 2.0)

    end_deg = start_deg + body_span
    end_rad = math.radians(end_deg)
    ex = cx + rmid * math.cos(end_rad)
    ey = cy - rmid * math.sin(end_rad)
    tan_deg = end_deg + (90 if span_deg > 0 else -90)
    tr = math.radians(tan_deg)
    nr = tr + math.pi / 2
    hw = thick * 1.48
    hl = thick * 2.05
    tip = QPointF(ex + hl * 0.88 * math.cos(tr), ey - hl * 0.88 * math.sin(tr))
    b1 = QPointF(ex - hl * 0.14 * math.cos(tr) + hw * math.cos(nr),
                 ey + hl * 0.14 * math.sin(tr) - hw * math.sin(nr))
    b2 = QPointF(ex - hl * 0.14 * math.cos(tr) - hw * math.cos(nr),
                 ey + hl * 0.14 * math.sin(tr) + hw * math.sin(nr))
    head = QPainterPath()
    head.addPolygon(QPolygonF([tip, b1, b2]))
    head.closeSubpath()
    return body.united(tail).united(head).simplified()


def paint_gel_shape(p, path, top_y, bot_y, kind="blue"):
    """Paint any QPainterPath as a 3D glossy 10.2 Aqua gel piece with drop shadow & top sheen."""
    p.save()
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(0, 18, 45, 72))
    p.drawPath(path.translated(0.4, 1.3))
    if kind == "blue":
        rim = "#12408a"
        grad = vgrad(top_y, bot_y, (0.0, "#b8e2ff"), (0.42, "#3580eb"), (0.52, "#1c5cc8"), (1.0, "#7cd8ff"))
    elif kind == "amber":
        rim = "#7d4908"
        grad = vgrad(top_y, bot_y, (0.0, "#fff0a8"), (0.45, "#f0a224"), (0.55, "#cf7a0c"), (1.0, "#ffd86b"))
    else:
        rim = "#660e06"
        grad = vgrad(top_y, bot_y, (0.0, "#ffb8b0"), (0.45, "#d82c1c"), (0.55, "#a81005"), (1.0, "#ff7c68"))
    p.setBrush(grad)
    p.setPen(QPen(c(rim), 1.05, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.drawPath(path)
    # Specular highlight on upper half
    p.setClipPath(path)
    mid_y = top_y + (bot_y - top_y) * 0.46
    p.setPen(Qt.NoPen)
    p.setBrush(vgrad(top_y, mid_y, (0.0, (255, 255, 255, 195)), (1.0, (255, 255, 255, 20))))
    p.drawRect(QRectF(0, top_y, 32, mid_y - top_y))
    p.restore()


def aqua_folder_base(p, open_flap=False):
    """10.2 sky-blue pinstriped Aqua folder sampled from ch11-212-021.png ('New Folder')."""
    floor_shadow(p, 16.0, 28.2, 12.2, 2.4, 72)

    # Back leaf + top-left rounded tab (slightly angled, taller on left like 10.2)
    back = QPainterPath()
    back.moveTo(4.0, 9.0)
    back.lineTo(4.0, 6.8)
    back.quadTo(4.0, 5.2, 5.8, 5.2)
    back.lineTo(11.6, 5.2)
    back.quadTo(13.0, 5.2, 13.8, 6.8)
    back.lineTo(26.2, 6.8)
    back.quadTo(27.8, 6.8, 27.8, 8.4)
    back.lineTo(27.2, 25.8)
    back.lineTo(4.5, 26.8)
    back.closeSubpath()
    p.setPen(QPen(c("#6b7c93"), 1.05))
    p.setBrush(vgrad(5.2, 26.5, (0.0, "#ffffff"), (0.35, "#dcebfb"), (1.0, "#9abce4")))
    p.drawPath(back)

    if open_flap:
        # Crisp white paper sheet peeking out inside open folder
        sheet = QPainterPath()
        sheet.addPolygon(QPolygonF([QPointF(6.2, 9.4), QPointF(25.4, 8.4), QPointF(25.8, 23.0), QPointF(6.0, 24.5)]))
        sheet.closeSubpath()
        p.setPen(QPen(c("#9aa2b0"), 0.85))
        p.setBrush(c("#ffffff"))
        p.drawPath(sheet)

    # Glossy sky-blue front flap with horizontal Aqua pinstripes
    front = QPainterPath()
    if open_flap:
        front.moveTo(2.4, 14.2)
        front.lineTo(28.8, 12.6)
        front.quadTo(29.8, 12.6, 29.4, 14.2)
        front.lineTo(27.2, 25.8)
        front.lineTo(4.5, 26.8)
        front.closeSubpath()
        fy0 = 12.6
    else:
        front.moveTo(4.2, 10.2)
        front.lineTo(27.4, 9.0)
        front.quadTo(28.6, 9.0, 28.4, 10.6)
        front.lineTo(27.2, 25.8)
        front.lineTo(4.5, 26.8)
        front.closeSubpath()
        fy0 = 9.0

    p.save()
    p.setPen(Qt.NoPen)
    p.setBrush(vgrad(fy0, 26.8,
                     (0.0, "#e6ffff"),
                     (0.28, "#b5dffd"),
                     (0.62, "#7ab4f5"),
                     (0.88, "#5c99df"),
                     (1.0, "#82c2ff")))
    p.drawPath(front)

    # Subtle 10.2 Aqua horizontal pinstripes inside front folder face
    p.setClipPath(front)
    for yy in range(int(fy0) + 1, 27, 2):
        p.fillRect(QRectF(2, yy, 29, 0.9), QColor(255, 255, 255, 62))
    # Bright white specular top lip
    p.setPen(QPen(QColor(255, 255, 255, 215), 1.2))
    if open_flap:
        p.drawLine(QPointF(3.2, 14.9), QPointF(28.5, 13.4))
    else:
        p.drawLine(QPointF(5.0, 10.9), QPointF(27.6, 9.8))
    p.restore()

    p.setPen(QPen(c("#476d9e"), 1.05, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(Qt.NoBrush)
    p.drawPath(front)


def aqua_page_base(p, x=6.5, y=3.0, w=19.0, h=25.0, lines=False, shadow=True):
    """10.2 curled white document sheet (sampled from ch11-208-012.png)."""
    if shadow:
        floor_shadow(p, x + w / 2, y + h + 0.8, w * 0.48, 2.2, 68)
    fold = w * 0.30
    sheet = QPainterPath()
    sheet.moveTo(x, y)
    sheet.lineTo(x + w - fold, y)
    sheet.lineTo(x + w, y + fold)
    sheet.lineTo(x + w, y + h)
    sheet.lineTo(x, y + h)
    sheet.closeSubpath()

    p.setPen(QPen(c("#848a96"), 1.0))
    p.setBrush(vgrad(y, y + h, (0.0, "#ffffff"), (0.7, "#f7f8fb"), (1.0, "#e6e9f0")))
    p.drawPath(sheet)

    if lines:
        p.setPen(Qt.NoPen)
        p.setBrush(c("#b4bcc8"))
        for i, lw in enumerate((0.52, 0.68, 0.68, 0.68, 0.46)):
            ly = y + fold + 2.2 + i * 3.1
            if ly + 1.4 < y + h - 2.5:
                p.drawRoundedRect(QRectF(x + 3.0, ly, w * lw, 1.35), 0.5, 0.5)

    # Diagonal shadow cast under curled dog-ear
    ear_sh = QPainterPath()
    ear_sh.moveTo(x + w - fold, y + fold)
    ear_sh.lineTo(x + w, y + fold)
    ear_sh.lineTo(x + w, y + fold + 2.6)
    ear_sh.lineTo(x + w - fold - 1.2, y + fold + 1.4)
    ear_sh.closeSubpath()
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(0, 0, 0, 42))
    p.drawPath(ear_sh)

    # Curled dog-ear flap
    ear = QPainterPath()
    ear.moveTo(x + w - fold, y)
    ear.lineTo(x + w, y + fold)
    ear.quadTo(x + w - fold * 0.75, y + fold * 0.92, x + w - fold, y + fold)
    ear.closeSubpath()
    p.setPen(QPen(c("#848a96"), 0.95, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(vgrad(y, y + fold, (0.0, "#e8ebf2"), (0.6, "#ffffff"), (1.0, "#cfd4df")))
    p.drawPath(ear)


def paint_magnifier(p, cx=13.0, cy=12.4, r=7.8, scale_f=1.0, ox=0.0, oy=0.0):
    """10.2 Sherlock silver-rimmed glass magnifier + black cylindrical handle (ch11-212-021.png)."""
    p.save()
    p.translate(ox, oy)
    p.scale(scale_f, scale_f)
    floor_shadow(p, cx + 4.0, cy + 15.2, 9.0, 2.0, 58)

    # Silver collar + glossy black cylindrical handle at 45 degrees
    p.save()
    p.translate(cx, cy)
    p.rotate(45)
    # Metallic ferrule
    p.setPen(QPen(c("#585b62"), 0.8))
    p.setBrush(vgrad(-2.0, 2.0, (0.0, "#8e929b"), (0.45, "#ffffff"), (1.0, "#6e727a"), x0=0, x1=0))
    p.drawRoundedRect(QRectF(r - 0.4, -2.0, 3.2, 4.0), 0.7, 0.7)
    # Jet-black handle with cylindrical white-grey highlight
    h_rect = QRectF(r + 2.2, -2.35, 11.4, 4.7)
    p.setPen(QPen(c("#08080a"), 0.9))
    p.setBrush(vgrad(-2.35, 2.35, (0.0, "#101114"), (0.28, "#7b7f88"), (0.52, "#1c1d22"), (1.0, "#050507"), x0=0, x1=0))
    p.drawRoundedRect(h_rect, 1.8, 1.8)
    p.restore()

    # Outer brushed-silver bezel
    bezel = QPainterPath()
    bezel.addEllipse(QPointF(cx, cy), r + 1.5, r + 1.5)
    inner = QPainterPath()
    inner.addEllipse(QPointF(cx, cy), r - 1.1, r - 1.1)
    ring_p = bezel.subtracted(inner)

    # Translucent icy-cyan/white glass lens
    p.setPen(Qt.NoPen)
    p.setBrush(rgrad(cx + 1.5, cy + 2.0, r * 1.15,
                     (0.0, (255, 255, 255, 235)),
                     (0.65, (214, 238, 255, 185)),
                     (1.0, (168, 208, 242, 200))))
    p.drawPath(inner)

    # Top-left curved glass reflection inside lens
    lens_arc = QPainterPath()
    lens_arc.addEllipse(QRectF(cx - r * 0.68, cy - r * 0.72, r * 1.25, r * 0.82))
    p.setBrush(vgrad(cy - r * 0.72, cy + r * 0.1, (0.0, (255, 255, 255, 235)), (1.0, (255, 255, 255, 0)), x0=cx, x1=cx))
    p.drawPath(lens_arc)

    # Metallic silver ring
    p.setBrush(vgrad(cy - r - 1.5, cy + r + 1.5,
                     (0.0, "#f8f9fb"),
                     (0.35, "#c4c8d0"),
                     (0.55, "#7c8088"),
                     (0.82, "#e4e7ec"),
                     (1.0, "#9498a0"), x0=cx - r, x1=cx + r))
    p.setPen(QPen(c("#52555c"), 0.95))
    p.drawPath(ring_p)
    p.restore()


def paint_pencil(p, cx=16.5, cy=15.8, length=23.0, width=4.8, angle_deg=32.0, shadow=True):
    """10.2 Mail 'Compose' yellow wooden pencil with silver ferrule and rosy eraser (ch11-212-022.png)."""
    if shadow:
        floor_shadow(p, cx - 2.5, cy + 11.2, 8.5, 2.0, 62)
    p.save()
    p.translate(cx, cy)
    p.rotate(angle_deg)
    hw = width / 2.0
    top = -length / 2.0
    eraser_h = 3.2
    ferrule_h = 2.8
    cone_h = 5.0
    shaft_top = top + eraser_h + ferrule_h
    shaft_bot = top + length - cone_h

    # Drop shadow along shaft
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(0, 0, 0, 48))
    p.drawRoundedRect(QRectF(-hw + 1.0, top + 1.2, width, length - cone_h * 0.4), 1.4, 1.4)

    # Rosy-red eraser (#e85a54..#961e1a)
    p.setPen(QPen(c("#6e1814"), 0.85))
    p.setBrush(vgrad(0, 0, (0.0, "#ff9a94"), (0.45, "#e24d46"), (1.0, "#941d18"), x0=-hw, x1=hw))
    p.drawRoundedRect(QRectF(-hw, top, width, eraser_h + 1.0), 1.4, 1.4)

    # Brushed silver ferrule
    p.setPen(QPen(c("#5c6068"), 0.85))
    p.setBrush(vgrad(0, 0, (0.0, "#9ca0a8"), (0.35, "#ffffff"), (0.7, "#b8bcc4"), (1.0, "#70747c"), x0=-hw, x1=hw))
    p.drawRect(QRectF(-hw, top + eraser_h, width, ferrule_h))

    # 3-faceted golden cedar shaft (#fff0a8, #f0be59, #b57e2c)
    p.setPen(Qt.NoPen)
    sh_h = shaft_bot - shaft_top
    p.fillRect(QRectF(-hw, shaft_top, width * 0.34, sh_h), c("#fff0a6"))
    p.fillRect(QRectF(-hw + width * 0.34, shaft_top, width * 0.34, sh_h), c("#f0be56"))
    p.fillRect(QRectF(-hw + width * 0.68, shaft_top, width * 0.32, sh_h), c("#b57e2c"))
    p.setPen(QPen(c("#6e4b18"), 0.85))
    p.setBrush(Qt.NoBrush)
    p.drawRect(QRectF(-hw, shaft_top, width, sh_h))

    # Sharpened tan wood cone + dark graphite point
    cone = QPainterPath()
    cone.moveTo(-hw, shaft_bot)
    cone.lineTo(hw, shaft_bot)
    cone.lineTo(0.0, shaft_bot + cone_h)
    cone.closeSubpath()
    p.setPen(QPen(c("#6e4b18"), 0.85, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(vgrad(0, 0, (0.0, "#f7e2c2"), (0.6, "#dfb686"), (1.0, "#a87e52"), x0=-hw, x1=hw))
    p.drawPath(cone)

    tip = QPainterPath()
    tip.moveTo(-hw * 0.36, shaft_bot + cone_h * 0.64)
    tip.lineTo(hw * 0.36, shaft_bot + cone_h * 0.64)
    tip.lineTo(0.0, shaft_bot + cone_h)
    tip.closeSubpath()
    p.setPen(Qt.NoPen)
    p.setBrush(c("#201e1c"))
    p.drawPath(tip)
    p.restore()


def paint_stamp(p, x=5.0, y=5.0, w=22.0, h=22.0, crimson=False):
    """10.2 Mail perforated postage stamp (sampled from ch11-212-022.png Reply/Forward/Bounce)."""
    p.save()
    # Scalloped outer white paper card
    card = QPainterPath()
    card.addRect(QRectF(x, y, w, h))
    holes = QPainterPath()
    nx = max(4, int(round(w / 3.6)))
    ny = max(4, int(round(h / 3.6)))
    for i in range(nx + 1):
        hx = x + i * (w / nx)
        holes.addEllipse(QPointF(hx, y), 1.05, 1.05)
        holes.addEllipse(QPointF(hx, y + h), 1.05, 1.05)
    for j in range(ny + 1):
        hy = y + j * (h / ny)
        holes.addEllipse(QPointF(x, hy), 1.05, 1.05)
        holes.addEllipse(QPointF(x + w, hy), 1.05, 1.05)
    stamp_p = card.subtracted(holes)

    p.setPen(Qt.NoPen)
    p.setBrush(QColor(0, 0, 0, 58))
    p.drawPath(stamp_p.translated(0.8, 1.4))

    p.setPen(QPen(c("#8c929e"), 0.8))
    p.setBrush(c("#ffffff"))
    p.drawPath(stamp_p)

    # Coloured stamp ink field
    ins = QRectF(x + 2.5, y + 2.5, w - 5.0, h - 5.0)
    if crimson:
        # Sampled Bounce stamp (#ad1001..#711a11)
        p.setPen(QPen(c("#580d06"), 0.8))
        p.setBrush(vgrad(ins.top(), ins.bottom(), (0.0, "#c81c0c"), (0.55, "#a51204"), (1.0, "#6f160d")))
    else:
        # Sampled Reply/Forward stamp (#85a6eb..#5c88e0)
        p.setPen(QPen(c("#4b6ba6"), 0.8))
        p.setBrush(vgrad(ins.top(), ins.bottom(), (0.0, "#9bc0f9"), (0.55, "#739ce9"), (1.0, "#557fd6")))
    p.drawRect(ins)

    # Subtle postmark waves across lower stamp corner
    if not crimson:
        p.setPen(QPen(QColor(35, 65, 125, 95), 0.95))
        for wy in (ins.bottom() - 4.2, ins.bottom() - 2.0):
            wp = QPainterPath()
            wp.moveTo(ins.left() + 1.0, wy)
            wp.cubicTo(ins.left() + 5.0, wy - 1.6, ins.left() + 9.0, wy + 1.6, ins.right() - 1.0, wy - 0.6)
            p.drawPath(wp)
    p.restore()


def paint_heart_path(cx=16.0, cy=15.8, s=11.8):
    hp = QPainterPath()
    hp.moveTo(cx, cy + s * 0.88)
    hp.cubicTo(cx - s * 1.18, cy + s * 0.16, cx - s * 1.15, cy - s * 0.86, cx - s * 0.50, cy - s * 0.86)
    hp.cubicTo(cx - s * 0.16, cy - s * 0.86, cx, cy - s * 0.52, cx, cy - s * 0.36)
    hp.cubicTo(cx, cy - s * 0.52, cx + s * 0.16, cy - s * 0.86, cx + s * 0.50, cy - s * 0.86)
    hp.cubicTo(cx + s * 1.15, cy - s * 0.86, cx + s * 1.18, cy + s * 0.16, cx, cy + s * 0.88)
    hp.closeSubpath()
    return hp


def paint_favorites_heart(p, cx=16.0, cy=16.0, s=11.4):
    """10.2 Finder 'Favorites' glossy ruby-red heart (ch11-211-020.png)."""
    floor_shadow(p, cx, cy + s * 0.92, s * 0.72, 2.2, 68)
    hp = paint_heart_path(cx, cy, s)
    p.save()
    p.setPen(Qt.NoPen)
    p.setBrush(vgrad(cy - s * 0.86, cy + s * 0.88,
                     (0.0, "#ff9c94"),
                     (0.32, "#f02c20"),
                     (0.72, "#c41008"),
                     (1.0, "#7d0602"), x0=cx, x1=cx))
    p.drawPath(hp)
    # Specular glossy highlights on both upper lobes
    p.setClipPath(hp)
    for lx in (cx - s * 0.46, cx + s * 0.46):
        lg = rgrad(lx, cy - s * 0.52, s * 0.42, (0.0, (255, 255, 255, 220)), (1.0, (255, 255, 255, 0)))
        p.setBrush(lg)
        p.drawEllipse(QPointF(lx, cy - s * 0.52), s * 0.44, s * 0.32)
    p.restore()
    p.setPen(QPen(c("#680804"), 1.05, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(Qt.NoBrush)
    p.drawPath(hp)


def build_action_painters():
    """Return OrderedDict-like list of (canonical_name, aliases_str, painter_fn)."""
    actions = []

    def act(name, aliases=""):
        def deco(fn):
            actions.append((name, aliases.split(), fn))
            return fn
        return deco

    # ---- 1. Navigation (Finder 10.2 round clear-glass Aqua buttons) ----
    @act("go-previous", "arrow-left go-previous-view go-previous-context gtk-go-back-ltr gtk-go-back back previous")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.2, "clear")
        # Sampled Finder Back (ch11-212-021.png): sharp left triangle + two crisp dots
        tri = poly((7.6, 15.5), (12.8, 11.2), (12.8, 19.8), round_=0.4)
        dots = U(circ(16.4, 15.5, 1.55 if not sm else 1.8), circ(21.0, 15.5, 1.55 if not sm else 1.8))
        draw_disc_glyph(p, U(tri, dots))

    @act("go-next", "arrow-right go-next-view go-next-context gtk-go-forward-ltr gtk-go-forward forward next")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.2, "clear")
        tri = poly((24.4, 15.5), (19.2, 11.2), (19.2, 19.8), round_=0.4)
        dots = U(circ(11.0, 15.5, 1.55 if not sm else 1.8), circ(15.6, 15.5, 1.55 if not sm else 1.8))
        draw_disc_glyph(p, U(tri, dots))

    @act("go-up", "arrow-up go-parent-folder gtk-go-up up")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.2, "clear")
        g = U(poly((16.0, 8.8), (21.6, 15.0), (10.4, 15.0), round_=0.5), rr(13.8, 14.2, 4.4, 7.2, 0.9))
        draw_disc_glyph(p, g)

    @act("go-down", "arrow-down go-down-search gtk-go-down down")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.2, "clear")
        g = U(poly((16.0, 22.2), (21.6, 16.0), (10.4, 16.0), round_=0.5), rr(13.8, 9.6, 4.4, 7.2, 0.9))
        draw_disc_glyph(p, g)

    @act("go-first", "go-first-view go-first-view-page gtk-goto-first-ltr")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.2, "clear")
        g = U(rr(9.4, 10.2, 2.4, 10.6, 0.7), poly((12.6, 15.5), (20.8, 10.4), (20.8, 20.6), round_=0.5))
        draw_disc_glyph(p, g)

    @act("go-last", "go-last-view go-last-view-page gtk-goto-last-ltr")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.2, "clear")
        g = U(rr(20.2, 10.2, 2.4, 10.6, 0.7), poly((19.4, 15.5), (11.2, 10.4), (11.2, 20.6), round_=0.5))
        draw_disc_glyph(p, g)

    @act("go-top", "gtk-goto-top")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.2, "clear")
        g = U(rr(10.0, 9.2, 12.0, 2.3, 0.7), poly((16.0, 12.2), (21.2, 17.6), (10.8, 17.6), round_=0.4), rr(14.0, 16.8, 4.0, 5.2, 0.8))
        draw_disc_glyph(p, g)

    @act("go-bottom", "gtk-goto-bottom")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.2, "clear")
        g = U(rr(10.0, 19.5, 12.0, 2.3, 0.7), poly((16.0, 18.8), (21.2, 13.4), (10.8, 13.4), round_=0.4), rr(14.0, 9.0, 4.0, 5.2, 0.8))
        draw_disc_glyph(p, g)

    @act("go-jump", "go-jump-locationbar go-jump-declaration go-jump-definition go-jump-today gtk-jump-to-ltr")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.2, "clear")
        g = aqua_arrow_path(15.2, 17.6, 6.6, 3.8, 180, -125)
        draw_disc_glyph(p, g)

    @act("go-home", "akonadi-phone-home gtk-home")
    def _(p, sm):
        # 10.2 Finder 'Home' cottage sampled from ch11-211-020.png
        floor_shadow(p, 16.0, 28.0, 11.5, 2.2, 72)
        # Stone chimney on right slope
        p.setPen(QPen(c("#524d46"), 0.9))
        p.setBrush(vgrad(6.0, 15.0, (0.0, "#f2eee6"), (1.0, "#b8b0a2")))
        p.drawRoundedRect(QRectF(21.2, 6.2, 3.2, 8.5), 0.5, 0.5)
        # Cream stucco house walls
        walls = QRectF(6.8, 14.0, 18.4, 13.2)
        p.setPen(QPen(c("#686258"), 1.0))
        p.setBrush(vgrad(14.0, 27.2, (0.0, "#fcfaf4"), (0.7, "#ede7da"), (1.0, "#d4ccb8")))
        p.drawRect(walls)
        # Gable peak triangle
        gable = poly((16.0, 6.2), (25.2, 14.4), (6.8, 14.4))
        p.drawPath(gable)
        # Wood front door (#b87338..#784418)
        p.setPen(QPen(c("#4f2c0e"), 0.9))
        p.setBrush(vgrad(18.2, 27.2, (0.0, "#c88242"), (1.0, "#7c4618")))
        p.drawRect(QRectF(13.4, 18.4, 5.2, 8.8))
        p.setPen(Qt.NoPen)
        p.setBrush(c("#f0d498"))
        p.drawEllipse(QPointF(17.4, 23.0), 0.65, 0.65)
        # Brown attic gable window
        p.setPen(QPen(c("#522e12"), 0.85))
        p.setBrush(c("#6e3c16"))
        p.drawRoundedRect(QRectF(13.3, 11.2, 5.4, 4.2), 0.6, 0.6)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#f5f8ff"))
        p.drawEllipse(QPointF(16.0, 13.3), 1.4, 1.4)
        # Steep dark charcoal roof eaves
        roof = QPainterPath()
        roof.moveTo(16.0, 4.2)
        roof.lineTo(28.4, 15.4)
        roof.lineTo(26.4, 17.2)
        roof.lineTo(16.0, 7.8)
        roof.lineTo(5.6, 17.2)
        roof.lineTo(3.6, 15.4)
        roof.closeSubpath()
        p.setPen(QPen(c("#141312"), 0.95, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(vgrad(4.2, 17.2, (0.0, "#5c5955"), (0.5, "#2b2927"), (1.0, "#181716")))
        p.drawPath(roof)

    # ---- 2. Folders & Documents ----
    @act("folder-new", "albumfolder-new archive-insert-directory")
    def _(p, sm):
        aqua_folder_base(p, open_flap=False)
        plus_badge(p, 24.4, 8.4, 5.2, 2.2)

    @act("document-open", "document-open-folder gtk-open folder-open")
    def _(p, sm):
        aqua_folder_base(p, open_flap=True)

    @act("document-open-recent", "view-history")
    def _(p, sm):
        aqua_folder_base(p, open_flap=True)
        # Mini silver-rimmed Aqua clock badge at bottom-right
        cx, cy, r = 23.5, 22.5, 5.8
        p.setPen(QPen(c("#3a4e6c"), 1.1))
        p.setBrush(vgrad(cy - r, cy + r, (0.0, "#ffffff"), (1.0, "#dce8f8"), x0=cx, x1=cx))
        p.drawEllipse(QPointF(cx, cy), r, r)
        p.setPen(QPen(c("#1b2d48"), 1.35, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(cx, cy), QPointF(cx, cy - 3.3))
        p.drawLine(QPointF(cx, cy), QPointF(cx + 2.6, cy + 1.2))

    @act("folder-sync", "vcs-update-cvs-cervisia")
    def _(p, sm):
        aqua_folder_base(p, open_flap=False)
        a1 = aqua_arrow_path(16.2, 18.5, 5.8, 3.5, 20, 135)
        a2 = aqua_arrow_path(16.2, 18.5, 5.8, 3.5, 200, 135)
        paint_gel_shape(p, a1.united(a2), 11.5, 25.5, "blue")

    @act("document-new", "document-new-from-template gtk-new")
    def _(p, sm):
        aqua_page_base(p, 5.5, 3.5, 18.5, 24.5, lines=False)
        plus_badge(p, 23.8, 8.2, 5.2, 2.2)

    @act("document-save", "gtk-save system-save-session")
    def _(p, sm):
        # 10.2 dark charcoal/slate 3.5" floppy disk (ch11-210-018.png top-left)
        floor_shadow(p, 16.0, 28.4, 11.6, 2.2, 72)
        disk = QPainterPath()
        disk.moveTo(5.0, 4.0)
        disk.lineTo(24.4, 4.0)
        disk.lineTo(27.0, 6.6)
        disk.lineTo(27.0, 26.5)
        disk.quadTo(27.0, 27.5, 26.0, 27.5)
        disk.lineTo(6.0, 27.5)
        disk.quadTo(5.0, 27.5, 5.0, 26.5)
        disk.closeSubpath()
        p.setPen(QPen(c("#1b1d22"), 1.05))
        p.setBrush(vgrad(4.0, 27.5, (0.0, "#565b66"), (0.5, "#363a42"), (1.0, "#24272d")))
        p.drawPath(disk)
        # Brushed aluminum top shutter
        p.setPen(QPen(c("#52565e"), 0.9))
        p.setBrush(vgrad(4.0, 13.0, (0.0, "#f8fafc"), (0.5, "#cfd4dc"), (1.0, "#9ea4b0")))
        p.drawRoundedRect(QRectF(9.2, 4.2, 11.8, 8.6), 0.8, 0.8)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#22252a"))
        p.drawRect(QRectF(15.6, 5.4, 3.2, 6.2))
        # Crisp white paper label at bottom with classic red header bar
        p.setPen(QPen(c("#8c929e"), 0.85))
        p.setBrush(c("#ffffff"))
        p.drawRoundedRect(QRectF(8.0, 15.4, 16.0, 11.8), 0.9, 0.9)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#d02a1e"))
        p.drawRect(QRectF(8.5, 15.8, 15.0, 2.4))
        p.setBrush(c("#c5cbd6"))
        for ly in (20.2, 22.8, 25.0):
            p.drawRect(QRectF(9.8, ly, 12.4, 1.0))

    @act("document-save-as", "gtk-save-as")
    def _(p, sm):
        # 10.2 floppy disk + miniature yellow Compose pencil writing new name
        actions_map["document-save"](p, sm)
        paint_pencil(p, 23.2, 20.0, 15.5, 3.8, 35.0, shadow=False)

    @act("document-save-all", "")
    def _(p, sm):
        p.save()
        p.translate(-2.2, -2.0)
        p.scale(0.88, 0.88)
        actions_map["document-save"](p, sm)
        p.restore()
        p.save()
        p.translate(3.4, 2.8)
        p.scale(0.88, 0.88)
        actions_map["document-save"](p, sm)
        p.restore()

    @act("document-print", "document-print-direct document-print-frame gtk-print")
    def _(p, sm):
        # Exact 10.2 front-on silver/white desktop printer (ch11-212-022.png & ch11-203-003.png)
        floor_shadow(p, 16.0, 28.6, 12.2, 2.3, 74)
        # Rear dark paper guide + white upright input sheet
        p.setPen(QPen(c("#4e525a"), 0.9))
        p.setBrush(c("#686d78"))
        p.drawRoundedRect(QRectF(8.2, 5.2, 15.6, 7.5), 1.0, 1.0)
        p.setPen(QPen(c("#8c929e"), 0.9))
        p.setBrush(vgrad(3.0, 13.0, (0.0, "#ffffff"), (1.0, "#e2e6ee")))
        p.drawRect(QRectF(9.6, 3.2, 12.8, 9.5))
        # Main curved cream/silver chassis
        body = QRectF(3.6, 11.4, 24.8, 12.4)
        p.setPen(QPen(c("#5d626c"), 1.0))
        p.setBrush(vgrad(11.4, 23.8, (0.0, "#f9fafd"), (0.45, "#e6e9f0"), (0.8, "#b8bec8"), (1.0, "#8f95a0")))
        p.drawRoundedRect(body, 2.8, 2.8)
        # Glossy dark charcoal central roller hood with horizontal specular highlight
        hood = QRectF(7.6, 11.6, 16.8, 6.2)
        p.setPen(QPen(c("#2d3036"), 0.9))
        p.setBrush(vgrad(11.6, 17.8, (0.0, "#4c5058"), (0.36, "#cfd4de"), (0.55, "#2f3238"), (1.0, "#585d66")))
        p.drawRoundedRect(hood, 1.4, 1.4)
        # Status LEDs on right cheek
        p.setPen(Qt.NoPen)
        p.setBrush(c("#48b828"))
        p.drawEllipse(QPointF(25.8, 16.5), 0.9, 0.9)
        p.setBrush(c("#6e737d"))
        p.drawEllipse(QPointF(25.8, 19.0), 0.9, 0.9)
        # Dark output slot + emerging angled printed page
        p.setBrush(c("#26282e"))
        p.drawRect(QRectF(7.4, 20.6, 17.2, 2.4))
        out_sheet = poly((8.8, 21.4), (23.2, 21.4), (24.6, 28.4), (7.4, 28.4))
        p.setPen(QPen(c("#858b98"), 0.9))
        p.setBrush(vgrad(21.4, 28.4, (0.0, "#dfe3ec"), (0.3, "#ffffff"), (1.0, "#f5f7fa")))
        p.drawPath(out_sheet)
        if not sm:
            p.setPen(Qt.NoPen)
            p.setBrush(c("#b0b7c4"))
            for ly in (23.4, 25.2, 26.8):
                p.drawRect(QRectF(10.2, ly, 11.6, 0.95))

    @act("document-print-preview", "document-preview view-preview gtk-print-preview")
    def _(p, sm):
        aqua_page_base(p, 5.0, 3.0, 18.0, 24.5, lines=True)
        paint_magnifier(p, 13.0, 12.4, 7.5, scale_f=0.72, ox=8.6, oy=7.8)

    @act("document-revert", "gtk-revert-to-saved-ltr")
    def _(p, sm):
        aqua_page_base(p, 5.5, 3.2, 18.5, 24.5, lines=True)
        arr = aqua_arrow_path(18.5, 18.8, 6.8, 3.8, -35, 215)
        paint_gel_shape(p, arr, 11.0, 26.0, "blue")

    @act("document-export", "document-share")
    def _(p, sm):
        aqua_page_base(p, 4.5, 3.2, 18.0, 24.5, lines=True)
        arr = U(rr(14.0, 15.6, 9.5, 4.4, 1.0), poly((21.5, 12.2), (29.2, 17.8), (21.5, 23.4), round_=0.5))
        paint_gel_shape(p, arr, 12.2, 23.4, "blue")

    @act("document-import", "")
    def _(p, sm):
        aqua_page_base(p, 8.5, 3.2, 18.5, 24.5, lines=True)
        arr = U(rr(3.0, 15.6, 9.5, 4.4, 1.0), poly((10.5, 12.2), (18.2, 17.8), (10.5, 23.4), round_=0.5))
        paint_gel_shape(p, arr, 12.2, 23.4, "blue")

    @act("document-close", "view-close view-left-close view-right-close")
    def _(p, sm):
        aqua_page_base(p, 5.5, 3.5, 18.5, 24.5, lines=True)
        glass_disc(p, 22.8, 21.5, 6.4, "red")
        draw_disc_glyph(p, cross(22.8, 21.5, 2.5, 1.9), dark=False)

    @act("document-properties", "documentinfo albumfolder-properties help-about dialog-information gtk-info gtk-properties gtk-about")
    def _(p, sm):
        # 10.2 Finder 'Get Info' glossy Aqua blue circle with serif white 'i'
        glass_disc(p, 16, 15.5, 12.2, "blue")
        ig = U(circ(16.0, 10.0, 1.65), rr(14.5, 13.2, 3.0, 8.2, 1.1), rr(13.2, 13.2, 4.2, 1.6, 0.7), rr(13.0, 19.9, 6.0, 1.6, 0.7))
        draw_disc_glyph(p, ig, dark=False)

    # ---- 3. Edit, Clipboard & Search ----
    @act("document-edit", "edit-entry gtk-edit")
    def _(p, sm):
        paint_pencil(p, 16.5, 15.5, 24.0, 5.2, 32.0, shadow=True)

    @act("edit-rename", "")
    def _(p, sm):
        # 10.2 white text field with Aqua blue focus ring + yellow pencil
        floor_shadow(p, 16.0, 27.6, 12.5, 2.0, 55)
        p.setPen(QPen(QColor(74, 144, 232, 155), 2.4))
        p.setBrush(c("#ffffff"))
        p.drawRoundedRect(QRectF(3.2, 17.5, 25.6, 8.6), 1.6, 1.6)
        p.setPen(QPen(c("#7c828d"), 0.9))
        p.drawRect(QRectF(3.8, 18.0, 24.4, 7.6))
        p.setPen(QPen(c("#1a1a1a"), 1.3))
        p.drawLine(QPointF(14.5, 19.6), QPointF(14.5, 24.0))
        paint_pencil(p, 19.5, 12.6, 19.0, 4.4, 34.0, shadow=False)

    @act("edit-cut", "gtk-cut")
    def _(p, sm):
        # 10.2 brushed-steel scissors (all-076-047.png) with Aqua blue finger rings
        floor_shadow(p, 16.0, 28.4, 10.5, 2.1, 65)
        for sign, ang in ((-1, -24), (1, 24)):
            p.save()
            p.translate(16.0, 16.2)
            p.rotate(ang)
            blade = QPainterPath()
            blade.moveTo(-1.5, 2.0)
            blade.lineTo(0.0, -13.2)
            blade.lineTo(1.7, 2.0)
            blade.closeSubpath()
            p.setPen(QPen(c("#52565e"), 0.85))
            p.setBrush(vgrad(-13.2, 2.0, (0.0, "#ffffff"), (0.5, "#cfd5de"), (1.0, "#8f96a2"), x0=-1.5, x1=1.7))
            p.drawPath(blade)
            p.restore()
        # Pivot screw
        p.setPen(QPen(c("#454950"), 0.7))
        p.setBrush(c("#e8ebf0"))
        p.drawEllipse(QPointF(16.0, 15.6), 1.4, 1.4)
        # Glossy Aqua blue ergonomic handles
        r1 = ring(10.2, 22.8, 3.6, 2.4)
        r2 = ring(21.8, 22.8, 3.6, 2.4)
        paint_gel_shape(p, r1.united(r2), 17.8, 27.8, "blue")

    @act("edit-copy", "gtk-copy tab-duplicate window-duplicate")
    def _(p, sm):
        # Twin overlapping 10.2 curled white pages
        aqua_page_base(p, 4.2, 2.8, 16.2, 21.2, lines=True, shadow=False)
        floor_shadow(p, 19.0, 28.4, 9.6, 2.1, 68)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 0, 0, 42))
        p.drawRoundedRect(QRectF(9.8, 7.6, 16.6, 21.4), 1.2, 1.2)
        aqua_page_base(p, 10.6, 6.8, 16.4, 21.2, lines=True, shadow=False)

    @act("edit-paste", "gtk-paste edit-paste-in-place")
    def _(p, sm):
        # Honey-oak 10.2 clipboard + brushed chrome clip + curled white sheet
        floor_shadow(p, 16.0, 28.6, 11.4, 2.2, 72)
        p.setPen(QPen(c("#5e3a14"), 1.0))
        p.setBrush(vgrad(4.6, 27.6, (0.0, "#dfa664"), (0.5, "#be8240"), (1.0, "#8f5920")))
        p.drawRoundedRect(QRectF(5.0, 4.8, 20.0, 22.8), 2.2, 2.2)
        # Curled white paper on front right
        aqua_page_base(p, 10.0, 8.6, 16.4, 19.2, lines=True, shadow=False)
        # Chrome spring clip at top
        clip = U(rr(10.2, 3.6, 9.6, 3.4, 1.1), S(circ(15.0, 3.4, 2.2), circ(15.0, 3.4, 0.9)))
        p.setPen(QPen(c("#4e525a"), 0.85))
        p.setBrush(vgrad(1.2, 7.0, (0.0, "#ffffff"), (0.5, "#cfd5de"), (1.0, "#858c98")))
        p.drawPath(clip)

    @act("edit-undo", "gtk-undo-ltr gtk-undo")
    def _(p, sm):
        arr = aqua_arrow_path(16.8, 18.2, 9.8, 5.4, -20, 195)
        paint_gel_shape(p, arr, 6.0, 26.5, "amber")

    @act("edit-redo", "gtk-redo-ltr gtk-redo")
    def _(p, sm):
        arr = aqua_arrow_path(15.2, 18.2, 9.8, 5.4, 200, -195)
        paint_gel_shape(p, arr, 6.0, 26.5, "blue")

    @act("edit-delete", "delete gtk-delete bookmark-remove archive-remove")
    def _(p, sm):
        # 10.2 Finder Customize Toolbar red delete circle
        glass_disc(p, 16, 15.5, 12.2, "red")
        draw_disc_glyph(p, cross(16.0, 15.5, 4.4, 2.8), dark=False)

    @act("edit-trash", "edit-delete-shred")
    def _(p, sm):
        # 10.2 silver wire-mesh Trash basket (ch11-202-002.png rightmost)
        floor_shadow(p, 16.0, 28.4, 10.0, 2.2, 72)
        basket = QPainterPath()
        basket.moveTo(7.4, 7.5)
        basket.lineTo(24.6, 7.5)
        basket.lineTo(22.2, 26.8)
        basket.quadTo(16.0, 28.2, 9.8, 26.8)
        basket.closeSubpath()
        p.save()
        p.setPen(Qt.NoPen)
        p.setBrush(vgrad(7.5, 27.5, (0.0, "#d8dce4"), (0.5, "#aeb4c0"), (1.0, "#7c828e"), x0=7.4, x1=24.6))
        p.drawPath(basket)
        p.setClipPath(basket)
        # Crumpled white paper inside
        p.setBrush(c("#ffffff"))
        p.drawEllipse(QPointF(14.0, 12.5), 4.6, 3.6)
        p.setBrush(c("#eef1f7"))
        p.drawEllipse(QPointF(18.5, 14.2), 4.2, 3.8)
        # Wire mesh cross-hatching
        p.setPen(QPen(QColor(45, 50, 58, 130), 0.85))
        for k in range(-12, 26, 3):
            p.drawLine(QPointF(6 + k, 7), QPointF(16 + k, 28))
            p.drawLine(QPointF(26 - k, 7), QPointF(16 - k, 28))
        p.restore()
        p.setPen(QPen(c("#52565e"), 1.0))
        p.setBrush(Qt.NoBrush)
        p.drawPath(basket)
        # Gleaming chrome top & bottom rims
        p.setPen(QPen(c("#484c54"), 0.95))
        p.setBrush(vgrad(5.4, 9.4, (0.0, "#ffffff"), (0.5, "#cfd5de"), (1.0, "#7f8590")))
        p.drawEllipse(QRectF(6.8, 5.6, 18.4, 3.8))
        p.setBrush(vgrad(6.2, 8.8, (0.0, "#6e7480"), (1.0, "#b8bec8")))
        p.drawEllipse(QRectF(8.2, 6.2, 15.6, 2.5))

    @act("edit-clear", "edit-clear-all edit-clear-history edit-clear-list gtk-clear")
    def _(p, sm):
        # 10.2 two-tone angled pink & blue/white rubber eraser (all-091-057.png)
        floor_shadow(p, 16.0, 26.8, 11.2, 2.2, 65)
        p.save()
        p.translate(16.0, 16.2)
        p.rotate(-28)
        p.setPen(QPen(c("#6e2220"), 0.95))
        p.setBrush(vgrad(-5.0, 5.0, (0.0, "#ffa6a0"), (0.5, "#e45852"), (1.0, "#9e2824")))
        p.drawRoundedRect(QRectF(-10.5, -5.0, 13.5, 10.0), 1.8, 1.8)
        p.setPen(QPen(c("#5a6c88"), 0.95))
        p.setBrush(vgrad(-5.0, 5.0, (0.0, "#ffffff"), (0.5, "#dce8f8"), (1.0, "#9cb4d4")))
        p.drawRoundedRect(QRectF(1.5, -5.0, 9.0, 10.0), 1.6, 1.6)
        p.restore()

    @act("edit-clear-locationbar-rtl", "edit-clear-locationbar-ltr")
    def _(p, sm):
        # Sleek 10.2 search-field smoked glass clear tag with crisp white 'x'
        floor_shadow(p, 16.5, 25.0, 10.5, 1.9, 55)
        tag = poly((3.5, 16.0), (10.2, 8.5), (27.5, 8.5), (27.5, 23.5), (10.2, 23.5), round_=1.4)
        p.setPen(QPen(c("#454850"), 1.0))
        p.setBrush(vgrad(8.5, 23.5, (0.0, "#a6aab4"), (0.5, "#6e727c"), (1.0, "#50545c")))
        p.drawPath(tag)
        draw_disc_glyph(p, cross(18.5, 16.0, 3.6, 2.3), dark=False)

    @act("edit-select-all", "gtk-select-all edit-select")
    def _(p, sm):
        aqua_page_base(p, 6.5, 3.2, 19.0, 25.0, lines=False)
        sel = QRectF(9.4, 10.2, 13.2, 14.2)
        p.setPen(QPen(c("#1c5cc8"), 1.0, Qt.DashLine))
        p.setBrush(QColor(70, 138, 235, 75))
        p.drawRect(sel)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#2464d2"))
        for i, lw in enumerate((10.0, 10.0, 7.2)):
            p.drawRect(QRectF(11.0, 12.4 + i * 3.4, lw, 1.6))

    @act("edit-find", "system-search gtk-find search edit-find-mail edit-find-project")
    def _(p, sm):
        paint_magnifier(p, 13.0, 12.4, 7.8)

    @act("edit-find-replace", "gtk-find-and-replace")
    def _(p, sm):
        paint_magnifier(p, 13.0, 12.4, 7.8, scale_f=0.84, ox=-0.8, oy=-0.4)
        paint_pencil(p, 23.2, 19.5, 16.5, 4.0, 32.0, shadow=False)

    @act("tools-check-spelling", "gtk-spell-check autocorrection")
    def _(p, sm):
        floor_shadow(p, 16.0, 27.8, 11.0, 2.0, 62)
        f = QFont("Luxi Sans")
        f.setBold(True)
        f.setPixelSize(11)
        p.setFont(f)
        p.setPen(c("#1d2026"))
        p.drawText(QRectF(2.5, 3.5, 27.0, 14.0), Qt.AlignCenter, "ABC")
        chk = QPainterPath()
        chk.moveTo(6.5, 19.5)
        chk.lineTo(13.2, 26.2)
        chk.cubicTo(17.5, 19.2, 22.0, 14.2, 27.2, 10.8)
        st = QPainterPathStroker()
        st.setWidth(3.8)
        st.setCapStyle(Qt.RoundCap)
        st.setJoinStyle(Qt.RoundJoin)
        paint_gel_shape(p, st.createStroke(chk), 10.5, 27.0, "blue")

    # ---- 4. Zoom, View, Split, Drawer & Rotate ----
    @act("zoom-in", "gtk-zoom-in")
    def _(p, sm):
        paint_magnifier(p, 13.0, 12.4, 7.8)
        draw_disc_glyph(p, plus(13.0, 12.4, 3.6, 2.2), dark=True)

    @act("zoom-out", "gtk-zoom-out")
    def _(p, sm):
        paint_magnifier(p, 13.0, 12.4, 7.8)
        draw_disc_glyph(p, line(9.4, 12.4, 16.6, 12.4, 2.2), dark=True)

    @act("zoom-original", "zoom-1-to-2 zoom-2-to-1 gtk-zoom-100")
    def _(p, sm):
        paint_magnifier(p, 13.0, 12.4, 7.8)
        g = U(rr(9.5, 9.6, 1.8, 5.6, 0.5), circ(13.0, 11.0, 0.8), circ(13.0, 13.8, 0.8), rr(14.7, 9.6, 1.8, 5.6, 0.5))
        draw_disc_glyph(p, g, dark=True)

    @act("zoom-fit-best", "zoom-fit-width zoom-fit-height gtk-zoom-fit")
    def _(p, sm):
        paint_magnifier(p, 13.0, 12.4, 7.8)
        g = U(poly((8.6, 12.4), (11.6, 10.0), (11.6, 14.8)), poly((17.4, 12.4), (14.4, 10.0), (14.4, 14.8)))
        draw_disc_glyph(p, g, dark=True)

    @act("view-refresh", "reload gtk-refresh system-reboot")
    def _(p, sm):
        arr = aqua_arrow_path(16.0, 16.2, 11.0, 6.2, 55, -285)
        paint_gel_shape(p, arr, 4.0, 27.5, "blue")

    @act("process-stop", "gtk-stop call-stop")
    def _(p, sm):
        # 10.2 Print Center / Safari glossy red octagon stop sign with crisp white 'x'
        glass_disc(p, 16, 15.5, 11.8, "red", octagon=True)
        draw_disc_glyph(p, cross(16.0, 15.5, 4.3, 2.8), dark=False)

    @act("object-rotate-left", "transform-rotate-left")
    def _(p, sm):
        # Preview 10.2: framed photo card + glossy Aqua blue counter-clockwise arrow
        floor_shadow(p, 17.0, 28.4, 10.5, 2.0, 65)
        p.setPen(QPen(c("#7d8390"), 1.0))
        p.setBrush(c("#ffffff"))
        p.drawRoundedRect(QRectF(9.0, 10.0, 18.0, 17.2), 1.2, 1.2)
        p.setPen(Qt.NoPen)
        p.setBrush(vgrad(12.2, 23.2, (0.0, "#7cb8f8"), (1.0, "#cde6ff")))
        p.drawRect(QRectF(11.2, 12.2, 13.6, 11.2))
        arr = aqua_arrow_path(13.5, 13.8, 8.8, 5.0, 15, 175)
        paint_gel_shape(p, arr, 4.0, 20.0, "blue")

    @act("object-rotate-right", "transform-rotate-right")
    def _(p, sm):
        floor_shadow(p, 15.0, 28.4, 10.5, 2.0, 65)
        p.setPen(QPen(c("#7d8390"), 1.0))
        p.setBrush(c("#ffffff"))
        p.drawRoundedRect(QRectF(5.0, 10.0, 18.0, 17.2), 1.2, 1.2)
        p.setPen(Qt.NoPen)
        p.setBrush(vgrad(12.2, 23.2, (0.0, "#7cb8f8"), (1.0, "#cde6ff")))
        p.drawRect(QRectF(7.2, 12.2, 13.6, 11.2))
        arr = aqua_arrow_path(18.5, 13.8, 8.8, 5.0, 165, -175)
        paint_gel_shape(p, arr, 4.0, 20.0, "blue")

    @act("object-flip-horizontal", "")
    def _(p, sm):
        bevel_tile(p, 4.0, 5.5, 24.0, 20.0, 3.2)
        arr = U(rr(9.5, 14.0, 13.0, 3.0, 0.8), poly((6.2, 15.5), (11.2, 11.5), (11.2, 19.5)), poly((25.8, 15.5), (20.8, 11.5), (20.8, 19.5)))
        paint_gel_shape(p, arr, 11.5, 19.5, "blue")

    @act("object-flip-vertical", "")
    def _(p, sm):
        bevel_tile(p, 5.5, 4.0, 21.0, 23.0, 3.2)
        arr = U(rr(14.5, 9.0, 3.0, 13.0, 0.8), poly((16.0, 5.8), (12.0, 10.8), (20.0, 10.8)), poly((16.0, 25.2), (12.0, 20.2), (20.0, 20.2)))
        paint_gel_shape(p, arr, 5.8, 25.2, "blue")

    @act("view-list-icons", "view-grid")
    def _(p, sm):
        # Finder 10.2 'View' Icon button (ch11-212-021.png): 2x2 crisp hollow squares on glass pill
        bevel_tile(p, 3.5, 5.5, 25.0, 20.0, 3.6)
        boxes = U(*[S(rr(x, y, 5.2, 5.2, 0.6), rr(x + 1.5, y + 1.5, 2.2, 2.2, 0.1)) for x in (9.8, 17.0) for y in (9.6, 16.2)])
        draw_disc_glyph(p, boxes)

    @act("view-list-details", "view-list-text view-list")
    def _(p, sm):
        # Finder 10.2 'View' List button (ch11-212-021.png): 4 crisp horizontal rules on glass pill
        bevel_tile(p, 3.5, 5.5, 25.0, 20.0, 3.6)
        bars = U(*[rr(8.8, y, 14.4, 1.8, 0.5) for y in (9.6, 13.0, 16.4, 19.8)])
        draw_disc_glyph(p, bars)

    @act("view-file-columns", "view-column")
    def _(p, sm):
        # Finder 10.2 'View' Column button (ch11-212-021.png): 3 Miller columns on glass pill
        bevel_tile(p, 3.5, 5.5, 25.0, 20.0, 3.6)
        cols = S(rr(8.2, 9.4, 15.6, 12.2, 0.8),
                 rr(9.8, 11.0, 3.2, 9.0), rr(14.4, 11.0, 3.2, 9.0), rr(19.0, 11.0, 3.2, 9.0))
        draw_disc_glyph(p, cols)

    @act("view-list-tree", "view-web-browser-dom-tree")
    def _(p, sm):
        bevel_tile(p, 3.5, 5.5, 25.0, 20.0, 3.6)
        tr = U(rr(8.2, 9.4, 11.0, 2.0, 0.6),
               poly((9.2, 13.8), (11.8, 15.4), (9.2, 17.0)),
               rr(13.2, 14.4, 10.2, 2.0, 0.6),
               rr(13.2, 19.0, 10.2, 2.0, 0.6))
        draw_disc_glyph(p, tr)

    def mini_aqua_window(p, x=3.5, y=5.5, w=25.0, h=20.0):
        floor_shadow(p, x + w / 2, y + h + 1.0, w * 0.48, 2.0, 62)
        p.setPen(QPen(c("#5e636d"), 1.0))
        p.setBrush(c("#ffffff"))
        p.drawRoundedRect(QRectF(x, y, w, h), 2.2, 2.2)
        # Mini pinstriped title bar + traffic lights
        p.setBrush(vgrad(y, y + 5.0, (0.0, "#f5f6f8"), (1.0, "#cfd3dc")))
        p.drawRoundedRect(QRectF(x, y, w, 5.2), 2.0, 2.0)
        p.setPen(Qt.NoPen)
        for i, col in enumerate(("#e03c32", "#f0be28", "#58c438")):
            p.setBrush(c(col))
            p.drawEllipse(QPointF(x + 3.0 + i * 3.2, y + 2.6), 1.15, 1.15)
        p.setPen(QPen(c("#8c929e"), 0.85))
        p.drawLine(QPointF(x + 0.5, y + 5.2), QPointF(x + w - 0.5, y + 5.2))

    @act("view-split-left-right", "view-right-new")
    def _(p, sm):
        mini_aqua_window(p, 3.5, 5.5, 25.0, 20.5)
        p.setPen(QPen(c("#7c828e"), 1.2))
        p.drawLine(QPointF(16.0, 11.0), QPointF(16.0, 25.5))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(68, 136, 232, 65))
        p.drawRect(QRectF(4.2, 11.2, 11.3, 14.2))

    @act("view-split-top-bottom", "")
    def _(p, sm):
        mini_aqua_window(p, 3.5, 5.5, 25.0, 20.5)
        p.setPen(QPen(c("#7c828e"), 1.2))
        p.drawLine(QPointF(4.0, 18.2), QPointF(28.0, 18.2))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(68, 136, 232, 65))
        p.drawRect(QRectF(4.2, 11.2, 23.6, 6.6))

    @act("sidebar-show", "view-sidetree view-left-pane")
    def _(p, sm):
        # Authentic 10.2 Aqua window with a pinstriped Drawer sliding out the left side
        p.setPen(QPen(c("#6e7480"), 0.95))
        p.setBrush(vgrad(8.5, 24.5, (0.0, "#f2f4f8"), (1.0, "#d8dce6")))
        p.drawRoundedRect(QRectF(2.5, 8.8, 8.0, 15.2), 1.4, 1.4)
        for yy in range(10, 24, 2):
            p.fillRect(QRectF(3.2, yy, 5.6, 0.8), QColor(255, 255, 255, 150))
        mini_aqua_window(p, 9.2, 5.5, 20.0, 20.5)

    @act("view-filter", "")
    def _(p, sm):
        # Brushed silver metallic funnel with Aqua blue inner rim
        floor_shadow(p, 16.0, 28.4, 7.5, 2.0, 62)
        fn = poly((4.5, 6.8), (27.5, 6.8), (18.4, 17.6), (18.4, 26.8), (13.6, 24.8), (13.6, 17.6), round_=0.8)
        p.setPen(QPen(c("#4e535c"), 1.0))
        p.setBrush(vgrad(4.5, 27.5, (0.0, "#a8aeb8"), (0.38, "#ffffff"), (0.7, "#cfd5de"), (1.0, "#7c828e"), x0=4.5, x1=27.5))
        p.drawPath(fn)
        p.setPen(QPen(c("#1c52a6"), 0.9))
        p.setBrush(vgrad(4.8, 8.8, (0.0, "#2468d8"), (1.0, "#8ad8ff")))
        p.drawEllipse(QRectF(4.6, 5.0, 22.8, 3.8))

    @act("view-sort-ascending", "view-sort")
    def _(p, sm):
        bevel_tile(p, 3.5, 5.5, 25.0, 20.0, 3.4)
        bars = U(rr(7.2, 10.0, 5.0, 2.0, 0.6), rr(7.2, 14.5, 7.6, 2.0, 0.6), rr(7.2, 19.0, 10.2, 2.0, 0.6))
        draw_disc_glyph(p, bars)
        arr = U(poly((22.2, 9.2), (25.6, 14.0), (18.8, 14.0)), rr(21.0, 13.4, 2.4, 8.0, 0.6))
        paint_gel_shape(p, arr, 9.2, 21.4, "blue")

    @act("view-sort-descending", "")
    def _(p, sm):
        bevel_tile(p, 3.5, 5.5, 25.0, 20.0, 3.4)
        bars = U(rr(7.2, 10.0, 10.2, 2.0, 0.6), rr(7.2, 14.5, 7.6, 2.0, 0.6), rr(7.2, 19.0, 5.0, 2.0, 0.6))
        draw_disc_glyph(p, bars)
        arr = U(poly((22.2, 21.8), (25.6, 17.0), (18.8, 17.0)), rr(21.0, 9.6, 2.4, 8.0, 0.6))
        paint_gel_shape(p, arr, 9.6, 21.8, "blue")

    @act("view-fullscreen", "gtk-fullscreen")
    def _(p, sm):
        bevel_tile(p, 4.0, 4.5, 24.0, 22.0, 3.6)
        g = U(polyline([(8.5, 13.2), (8.5, 8.8), (12.9, 8.8)], 2.1),
              polyline([(19.1, 8.8), (23.5, 8.8), (23.5, 13.2)], 2.1),
              polyline([(23.5, 17.8), (23.5, 22.2), (19.1, 22.2)], 2.1),
              polyline([(12.9, 22.2), (8.5, 22.2), (8.5, 17.8)], 2.1))
        draw_disc_glyph(p, g)

    @act("view-restore", "gtk-leave-fullscreen")
    def _(p, sm):
        bevel_tile(p, 4.0, 4.5, 24.0, 22.0, 3.6)
        g = U(polyline([(8.2, 12.6), (12.6, 12.6), (12.6, 8.2)], 2.1),
              polyline([(23.8, 12.6), (19.4, 12.6), (19.4, 8.2)], 2.1),
              polyline([(23.8, 18.4), (19.4, 18.4), (19.4, 22.8)], 2.1),
              polyline([(8.2, 18.4), (12.6, 18.4), (12.6, 22.8)], 2.1))
        draw_disc_glyph(p, g)

    @act("view-visible", "view-hidden")
    def _(p, sm):
        floor_shadow(p, 16.0, 25.8, 11.5, 2.0, 58)
        eye = QPainterPath()
        eye.moveTo(3.2, 16.0)
        eye.cubicTo(8.5, 7.8, 23.5, 7.8, 28.8, 16.0)
        eye.cubicTo(23.5, 24.2, 8.5, 24.2, 3.2, 16.0)
        p.setPen(QPen(c("#4e5664"), 1.1))
        p.setBrush(vgrad(9.5, 22.5, (0.0, "#e8eef8"), (0.5, "#ffffff"), (1.0, "#dce4f0")))
        p.drawPath(eye)
        glass_disc(p, 16.0, 16.0, 5.2, "blue")
        p.setPen(Qt.NoPen)
        p.setBrush(c("#0d1524"))
        p.drawEllipse(QPointF(16.0, 16.0), 2.2, 2.2)
        p.setBrush(c("#ffffff"))
        p.drawEllipse(QPointF(14.6, 14.5), 1.1, 1.1)

    # ---- 5. Mail, Bookmarks, Configure, Burn, Media, Dialogs & Formatting ----
    @act("mail-message-new", "mail-message-new-list")
    def _(p, sm):
        # 10.2 Mail envelope + yellow Compose pencil (ch11-212-022.png)
        floor_shadow(p, 15.5, 28.0, 12.0, 2.2, 68)
        env = QRectF(3.6, 10.5, 21.6, 15.6)
        p.setPen(QPen(c("#7c8390"), 0.95))
        p.setBrush(vgrad(10.5, 26.1, (0.0, "#ffffff"), (1.0, "#e6eaf2")))
        p.drawRoundedRect(env, 1.2, 1.2)
        p.setPen(QPen(c("#9aa2b2"), 0.9))
        p.drawLine(QPointF(4.2, 11.2), QPointF(14.4, 19.2))
        p.drawLine(QPointF(24.6, 11.2), QPointF(14.4, 19.2))
        p.setPen(Qt.NoPen)
        p.setBrush(c("#5c88e0"))
        p.drawRect(QRectF(20.6, 12.4, 3.0, 3.4))
        paint_pencil(p, 21.8, 13.6, 20.5, 4.6, 32.0, shadow=False)

    @act("mail-reply-sender", "mail-reply-custom mail-reply-list mail-meeting-request-reply")
    def _(p, sm):
        # 10.2 Mail 'Reply' perforated blue stamp + white left arrow (ch11-212-022.png)
        paint_stamp(p, 6.2, 5.2, 21.0, 21.0, crimson=False)
        arr = aqua_arrow_path(16.8, 19.2, 7.6, 4.0, 15, 145)
        draw_disc_glyph(p, arr, dark=False)

    @act("mail-reply-all", "mail-reply-custom-all")
    def _(p, sm):
        # 10.2 Mail 'Reply All' twin overlapping blue stamps + white left arrow (ch11-212-022.png)
        paint_stamp(p, 3.8, 3.4, 19.0, 19.0, crimson=False)
        paint_stamp(p, 8.8, 7.4, 19.0, 19.0, crimson=False)
        arr = aqua_arrow_path(18.5, 20.5, 7.0, 3.6, 15, 145)
        draw_disc_glyph(p, arr, dark=False)

    @act("mail-forward", "")
    def _(p, sm):
        # 10.2 Mail 'Forward' perforated blue stamp + white right arrow (ch11-212-022.png)
        paint_stamp(p, 4.8, 5.2, 21.0, 21.0, crimson=False)
        arr = aqua_arrow_path(14.0, 19.2, 7.6, 4.0, 165, -145)
        draw_disc_glyph(p, arr, dark=False)

    @act("mail-mark-junk", "mail-mark-important")
    def _(p, sm):
        # 10.2 Mail 'Bounce' perforated crimson stamp + white bounce arrow (ch11-212-022.png)
        paint_stamp(p, 5.5, 5.2, 21.0, 21.0, crimson=True)
        bnc = U(polyline([(11.5, 22.2), (19.6, 17.6), (13.2, 12.2)], 2.6),
                poly((10.2, 10.2), (17.2, 10.4), (11.6, 16.4), round_=0.4))
        draw_disc_glyph(p, bnc, dark=False)

    @act("mail-receive", "mail-queue")
    def _(p, sm):
        # 10.2 Mail 'Get Mail' white envelope with letters peeking out (ch11-212-022.png)
        floor_shadow(p, 16.0, 28.0, 12.0, 2.2, 68)
        for ang, dx, dy in ((-18, 12.5, 11.5), (10, 18.0, 11.8)):
            p.save()
            p.translate(dx, dy)
            p.rotate(ang)
            p.setPen(QPen(c("#8b929e"), 0.85))
            p.setBrush(c("#ffffff"))
            p.drawRect(QRectF(-6.5, -5.5, 13.0, 9.5))
            p.setPen(Qt.NoPen)
            p.setBrush(c("#5c88e0"))
            p.drawRect(QRectF(2.8, -4.2, 2.6, 2.8))
            p.restore()
        env = QRectF(4.2, 12.5, 23.6, 14.4)
        p.setPen(QPen(c("#7c8390"), 0.95))
        p.setBrush(vgrad(12.5, 26.9, (0.0, "#ffffff"), (1.0, "#dfe4ee")))
        p.drawRoundedRect(env, 1.2, 1.2)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#5c88e0"))
        p.drawRect(QRectF(23.0, 14.4, 3.2, 3.6))
        p.setBrush(c("#b8c0ce"))
        p.drawRect(QRectF(12.2, 19.5, 7.6, 1.1))
        p.drawRect(QRectF(12.2, 21.6, 6.2, 1.1))

    @act("mail-send", "")
    def _(p, sm):
        floor_shadow(p, 15.0, 27.8, 11.5, 2.1, 65)
        env = QRectF(3.5, 9.8, 21.0, 14.8)
        p.setPen(QPen(c("#7c8390"), 0.95))
        p.setBrush(vgrad(9.8, 24.6, (0.0, "#ffffff"), (1.0, "#e2e6ef")))
        p.drawRoundedRect(env, 1.2, 1.2)
        p.setPen(QPen(c("#98a0b0"), 0.9))
        p.drawLine(QPointF(4.0, 10.4), QPointF(14.0, 18.2))
        p.drawLine(QPointF(24.0, 10.4), QPointF(14.0, 18.2))
        arr = U(rr(14.5, 16.8, 9.0, 4.2, 1.0), poly((21.8, 13.6), (29.4, 18.9), (21.8, 24.2), round_=0.5))
        paint_gel_shape(p, arr, 13.6, 24.2, "blue")

    @act("address-book-new", "adress-book-new contact-new view-pim-contacts")
    def _(p, sm):
        # 10.2 Mail 'Address' spiral-bound Aqua blue '@' book (ch11-212-022.png)
        floor_shadow(p, 16.5, 28.4, 10.2, 2.2, 70)
        p.setPen(QPen(c("#35558c"), 1.0))
        p.setBrush(vgrad(4.5, 27.2, (0.0, "#9cc2f8"), (0.5, "#6b99ea"), (1.0, "#4a76cc")))
        p.drawRoundedRect(QRectF(7.2, 4.5, 18.2, 22.8), 1.6, 1.6)
        # Spiral wire rings along left spine
        p.setPen(QPen(c("#484c56"), 1.1, Qt.SolidLine, Qt.RoundCap))
        for ry in range(7, 26, 3):
            p.drawLine(QPointF(5.4, ry), QPointF(8.6, ry))
        f = QFont("Luxi Sans")
        f.setBold(True)
        f.setPixelSize(14)
        p.setFont(f)
        p.setPen(QColor(255, 255, 255, 235))
        p.drawText(QRectF(8.2, 5.0, 17.0, 21.0), Qt.AlignCenter, "@")

    @act("bookmarks", "bookmarks-organize bookmark-toolbar")
    def _(p, sm):
        paint_favorites_heart(p, 16.0, 16.0, 11.4)

    @act("bookmark-new", "bookmark-new-list")
    def _(p, sm):
        paint_favorites_heart(p, 14.8, 16.6, 10.6)
        plus_badge(p, 24.4, 8.2, 5.0, 2.1)

    @act("configure", "configure-toolbars configure-shortcuts settings-configure gtk-preferences tools-wizard")
    def _(p, sm):
        # 10.2 Finder 'Utilities' crossed wooden claw hammer & chrome wrench (ch11-212-021.png)
        floor_shadow(p, 16.0, 28.2, 11.4, 2.2, 68)
        # Wooden hammer shaft + steel head (-42 deg)
        p.save()
        p.translate(16.0, 16.2)
        p.rotate(-42)
        p.setPen(QPen(c("#5c3610"), 0.9))
        p.setBrush(vgrad(-2.0, 2.0, (0.0, "#e6ad62"), (0.5, "#be7d32"), (1.0, "#7c4b16"), x0=-2.0, x1=2.0))
        p.drawRoundedRect(QRectF(-1.9, -7.0, 3.8, 19.5), 1.2, 1.2)
        head = poly((-6.8, -10.4), (5.8, -10.4), (5.8, -6.2), (-3.8, -6.2), (-7.6, -7.8), round_=0.7)
        p.setPen(QPen(c("#484c54"), 0.9))
        p.setBrush(vgrad(-10.4, -6.2, (0.0, "#ffffff"), (0.5, "#cfd5de"), (1.0, "#7f8692")))
        p.drawPath(head)
        p.restore()
        # Gleaming brushed-chrome open-end wrench (+42 deg)
        p.save()
        p.translate(16.0, 16.2)
        p.rotate(42)
        wr = U(rr(-2.1, -7.5, 4.2, 19.8, 1.8), S(circ(0.0, -9.2, 4.8), poly((-2.0, -14.5), (2.0, -14.5), (2.0, -8.6), (-2.0, -8.6))))
        p.setPen(QPen(c("#484c54"), 0.95))
        p.setBrush(vgrad(-4.8, 4.8, (0.0, "#ffffff"), (0.45, "#dce1e9"), (1.0, "#8a919e"), x0=-4.8, x1=4.8))
        p.drawPath(wr)
        p.restore()

    @act("tools-media-optical-burn", "tools-media-optical-burn-image media-optical-burn")
    def _(p, sm):
        # Iconic 10.2 Disc Burner amber-yellow & black trefoil disc
        floor_shadow(p, 16.0, 28.4, 11.0, 2.3, 74)
        cx, cy, r = 16.0, 15.5, 12.2
        p.setPen(Qt.NoPen)
        p.setBrush(vgrad(cy - r, cy + r, (0.0, "#ffe868"), (0.5, "#f5b814"), (1.0, "#cf8200"), x0=cx, x1=cx))
        p.drawEllipse(QPointF(cx, cy), r, r)
        # Three 60-degree black trefoil blades + centre ring
        blades = QPainterPath()
        for a0 in (60, 180, 300):
            sec = QPainterPath()
            sec.moveTo(cx, cy)
            sec.arcTo(QRectF(cx - 9.8, cy - 9.8, 19.6, 19.6), a0 - 28, 56)
            sec.closeSubpath()
            blades = blades.united(sec)
        blades = blades.subtracted(circ(cx, cy, 3.6)).united(circ(cx, cy, 2.0))
        p.setBrush(c("#1a1917"))
        p.drawPath(blades)
        # Specular glass sheen over top
        lens_r = QRectF(cx - r * 0.66, cy - r + 1.1, r * 1.32, r * 0.78)
        p.setBrush(vgrad(lens_r.top(), lens_r.bottom(), (0.0, (255, 255, 255, 195)), (1.0, (255, 255, 255, 15)), x0=cx, x1=cx))
        p.drawEllipse(lens_r)
        p.setPen(QPen(c("#6e4600"), 1.1))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), r, r)

    @act("media-eject", "")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.2, "clear")
        ej = U(poly((16.0, 9.2), (21.6, 15.8), (10.4, 15.8), round_=0.5), rr(10.4, 17.6, 11.2, 2.6, 0.7))
        draw_disc_glyph(p, ej)

    @act("media-playback-start", "player-play media-playback-playing gtk-media-play-ltr")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.2, "clear")
        draw_disc_glyph(p, poly((12.4, 9.8), (22.2, 15.5), (12.4, 21.2), round_=0.6))

    @act("media-playback-pause", "player-pause media-playback-paused gtk-media-pause")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.2, "clear")
        draw_disc_glyph(p, U(rr(11.4, 10.0, 3.4, 11.0, 0.8), rr(17.2, 10.0, 3.4, 11.0, 0.8)))

    @act("media-playback-stop", "player-stop media-playback-stopped gtk-media-stop")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.2, "clear")
        draw_disc_glyph(p, rr(11.0, 10.5, 10.0, 10.0, 1.2))

    @act("media-skip-backward", "gtk-media-previous-ltr")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.2, "clear")
        draw_disc_glyph(p, U(rr(9.6, 10.4, 2.3, 10.2, 0.6), poly((12.4, 15.5), (20.6, 10.5), (20.6, 20.5), round_=0.4)))

    @act("media-skip-forward", "gtk-media-next-ltr")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.2, "clear")
        draw_disc_glyph(p, U(rr(20.1, 10.4, 2.3, 10.2, 0.6), poly((19.6, 15.5), (11.4, 10.5), (11.4, 20.5), round_=0.4)))

    @act("media-seek-backward", "gtk-media-rewind-ltr")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.2, "clear")
        draw_disc_glyph(p, U(poly((8.6, 15.5), (15.4, 10.8), (15.4, 20.2), round_=0.4),
                             poly((15.2, 15.5), (22.0, 10.8), (22.0, 20.2), round_=0.4)))

    @act("media-seek-forward", "gtk-media-forward-ltr")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.2, "clear")
        draw_disc_glyph(p, U(poly((16.8, 15.5), (10.0, 10.8), (10.0, 20.2), round_=0.4),
                             poly((23.4, 15.5), (16.6, 10.8), (16.6, 20.2), round_=0.4)))

    @act("media-record", "gtk-media-record")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.2, "clear")
        glass_disc(p, 16, 15.5, 5.6, "red")

    @act("list-add", "add value-increase gtk-add")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.0, "blue")
        draw_disc_glyph(p, plus(16.0, 15.5, 5.2, 2.8), dark=False)

    @act("list-remove", "remove value-decrease gtk-remove")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.0, "clear")
        draw_disc_glyph(p, line(10.8, 15.5, 21.2, 15.5, 2.8), dark=True)

    @act("dialog-ok", "dialog-ok-apply checkmark gtk-ok gtk-apply gtk-yes")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.0, "green")
        chk = QPainterPath()
        chk.moveTo(10.4, 15.8)
        chk.lineTo(14.4, 20.0)
        chk.lineTo(21.8, 11.4)
        draw_disc_glyph(p, stroke(chk, 2.8), dark=False)

    @act("dialog-cancel", "gtk-cancel gtk-no")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.0, "clear")
        draw_disc_glyph(p, cross(16.0, 15.5, 4.2, 2.6), dark=True)

    @act("window-close", "dialog-close tab-close tab-close-other gtk-close")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 11.4, "red")
        draw_disc_glyph(p, cross(16.0, 15.5, 4.0, 2.5), dark=False)

    @act("tab-new", "tab-new-background window-new")
    def _(p, sm):
        mini_aqua_window(p, 3.2, 7.2, 22.0, 19.2)
        plus_badge(p, 24.6, 8.2, 5.0, 2.1)

    @act("open-menu", "application-menu")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.0, "clear")
        bars = U(rr(10.4, 10.6, 11.2, 2.1, 0.9), rr(10.4, 14.5, 11.2, 2.1, 0.9), rr(10.4, 18.4, 11.2, 2.1, 0.9))
        draw_disc_glyph(p, bars, dark=True)

    # "more" menus (Kirigami toolbars and QML apps): the same clear glass button with three dots
    @act("overflow-menu", "view-more overflow-menu-left overflow-menu-right")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.0, "clear")
        dots = U(circ(10.6, 15.6, 1.75), circ(16.0, 15.6, 1.75), circ(21.4, 15.6, 1.75))
        draw_disc_glyph(p, dots, dark=True)

    @act("help-contents", "dialog-question gtk-help documentation")
    def _(p, sm):
        # Exact 10.2 Print-dialog round clear-glass '?' Help button (all-116-080.png)
        glass_disc(p, 16, 15.5, 12.2, "clear")
        f = QFont("Luxi Sans")
        f.setBold(True)
        f.setPixelSize(16)
        qp = QPainterPath()
        qp.addText(QPointF(0, 0), f, "?")
        br = qp.boundingRect()
        qp.translate(16.0 - br.center().x(), 15.5 - br.center().y())
        draw_disc_glyph(p, qp, dark=True)

    def paint_brass_lock(p, unlocked=False):
        floor_shadow(p, 14.5 if unlocked else 16.0, 28.4, 9.6, 2.1, 70)
        bx = 5.6 if unlocked else 7.4
        # Brushed-chrome shackle
        sh = QPainterPath()
        if not unlocked:
            sh.moveTo(10.8, 14.5)
            sh.lineTo(10.8, 9.5)
            sh.arcTo(QRectF(10.8, 4.2, 10.4, 10.4), 180, -180)
            sh.lineTo(21.2, 14.5)
        else:
            sh.moveTo(19.4, 14.5)
            sh.lineTo(19.4, 9.2)
            sh.arcTo(QRectF(19.4, 4.2, 9.2, 9.6), 180, -180)
            sh.lineTo(28.6, 11.6)
        p.setPen(QPen(c("#4e525c"), 3.4, Qt.SolidLine, Qt.RoundCap))
        p.drawPath(sh)
        p.setPen(QPen(c("#eef2f8"), 1.5, Qt.SolidLine, Qt.RoundCap))
        p.drawPath(sh)
        # Brushed-brass lock body
        body = QRectF(bx, 13.5, 17.2, 13.8)
        p.setPen(QPen(c("#6e4b10"), 1.0))
        p.setBrush(vgrad(bx, bx + 17.2, (0.0, "#fce494"), (0.45, "#e6b43c"), (0.8, "#b8821c"), (1.0, "#dfaa34"), x0=bx, x1=bx + 17.2))
        p.drawRoundedRect(body, 2.2, 2.2)
        # Keyhole
        kx = bx + 8.6
        kh = U(circ(kx, 19.2, 1.9), poly((kx - 1.0, 19.8), (kx + 1.0, 19.8), (kx + 1.4, 24.2), (kx - 1.4, 24.2)))
        p.setPen(Qt.NoPen)
        p.setBrush(c("#3a2608"))
        p.drawPath(kh)

    @act("system-lock-screen", "document-encrypt document-encrypted")
    def _(p, sm):
        paint_brass_lock(p, unlocked=False)

    @act("document-decrypt", "")
    def _(p, sm):
        paint_brass_lock(p, unlocked=True)

    @act("system-run", "debug-run gtk-execute")
    def _(p, sm):
        floor_shadow(p, 15.0, 28.2, 10.8, 2.2, 68)
        gp = QTransform().translate(14.5, 14.8).scale(1.55, 1.55).translate(-8.0, -8.0).map(gear(8, 7.0, 5.2, 2.1))
        p.setPen(QPen(c("#4a4e58"), 0.95))
        p.setBrush(vgrad(3.5, 25.5, (0.0, "#ffffff"), (0.5, "#cfd5de"), (1.0, "#858c98")))
        p.drawPath(gp)
        glass_disc(p, 21.8, 21.0, 6.8, "green")
        draw_disc_glyph(p, poly((19.8, 17.6), (25.4, 21.0), (19.8, 24.4), round_=0.4), dark=False)

    @act("application-exit", "system-shutdown system-log-out gtk-quit")
    def _(p, sm):
        glass_disc(p, 16, 15.5, 12.2, "red")
        pw = U(arc(16.0, 16.4, 5.0, 125, 290, 2.3), line(16.0, 9.2, 16.0, 15.4, 2.4))
        draw_disc_glyph(p, pw, dark=False)

    def paint_archive_box(p):
        floor_shadow(p, 16.0, 28.4, 11.4, 2.2, 70)
        box = QRectF(5.2, 10.4, 21.6, 16.8)
        p.setPen(QPen(c("#6e4b22"), 1.0))
        p.setBrush(vgrad(10.4, 27.2, (0.0, "#ecc488"), (0.5, "#cf9d58"), (1.0, "#9e6e30")))
        p.drawRoundedRect(box, 1.6, 1.6)
        flaps = poly((3.6, 10.6), (6.6, 6.4), (25.4, 6.4), (28.4, 10.6))
        p.setBrush(vgrad(6.4, 10.6, (0.0, "#f7dca8"), (1.0, "#d8a864")))
        p.drawPath(flaps)
        p.setPen(QPen(c("#8c622c"), 0.9))
        p.drawLine(QPointF(16.0, 6.6), QPointF(16.0, 15.2))

    @act("archive-insert", "")
    def _(p, sm):
        paint_archive_box(p)
        arr = U(rr(13.8, 4.2, 4.4, 9.5, 1.0), poly((16.0, 19.8), (21.6, 12.8), (10.4, 12.8), round_=0.5))
        paint_gel_shape(p, arr, 4.2, 19.8, "blue")

    @act("archive-extract", "")
    def _(p, sm):
        paint_archive_box(p)
        arr = U(rr(13.8, 10.2, 4.4, 9.5, 1.0), poly((16.0, 3.8), (21.6, 10.8), (10.4, 10.8), round_=0.5))
        paint_gel_shape(p, arr, 3.8, 19.7, "blue")

    @act("color-picker", "")
    def _(p, sm):
        floor_shadow(p, 15.0, 28.0, 9.5, 2.0, 60)
        p.save()
        p.translate(16.0, 16.0)
        p.rotate(42)
        # Glass dropper tube with Aqua blue ink inside
        p.setPen(QPen(c("#5e6470"), 0.95))
        p.setBrush(vgrad(-2.2, 2.2, (0.0, "#ffffff"), (1.0, "#cfd6e2"), x0=-2.2, x1=2.2))
        p.drawRoundedRect(QRectF(-2.1, -3.5, 4.2, 13.5), 1.4, 1.4)
        p.setPen(Qt.NoPen)
        p.setBrush(c("#2a74e4"))
        p.drawRoundedRect(QRectF(-1.4, 2.0, 2.8, 7.2), 0.9, 0.9)
        p.drawPolygon(QPolygonF([QPointF(-1.4, 9.5), QPointF(1.4, 9.5), QPointF(0.0, 13.2)]))
        # Dark rubber bulb at top
        p.setPen(QPen(c("#202228"), 0.9))
        p.setBrush(vgrad(-3.4, 3.4, (0.0, "#6e727c"), (0.4, "#2c2e36"), (1.0, "#14151a"), x0=-3.4, x1=3.4))
        p.drawRoundedRect(QRectF(-3.2, -11.5, 6.4, 7.6), 2.8, 2.8)
        p.drawRect(QRectF(-4.2, -4.6, 8.4, 1.8))
        p.restore()

    # Text formatting palette actions (HIG p. 91, all-091-057.png)
    def fmt_letter(p, ch, bold=False, italic=False, underline=False, strike=False):
        bevel_tile(p, 4.5, 4.5, 23.0, 22.0, 3.4)
        f = QFont("DejaVu Serif")
        f.setBold(bold)
        f.setItalic(italic)
        f.setPixelSize(15 if underline else 16)
        tp = QPainterPath()
        tp.addText(QPointF(0, 0), f, ch)
        br = tp.boundingRect()
        cy = 14.6 if underline else 15.5
        tp.translate(16.0 - br.center().x(), cy - br.center().y())
        if underline:
            tp = U(tp, rr(9.0, 21.8, 14.0, 1.6, 0.4))
        if strike:
            tp = U(tp, rr(8.6, 15.0, 14.8, 1.6, 0.4))
        draw_disc_glyph(p, tp, dark=True)

    @act("format-text-bold", "gtk-bold")
    def _(p, sm):
        fmt_letter(p, "B", bold=True)

    @act("format-text-italic", "gtk-italic")
    def _(p, sm):
        fmt_letter(p, "I", bold=True, italic=True)

    @act("format-text-underline", "gtk-underline")
    def _(p, sm):
        fmt_letter(p, "U", bold=True, underline=True)

    @act("format-text-strikethrough", "gtk-strikethrough")
    def _(p, sm):
        fmt_letter(p, "S", bold=True, strike=True)

    def fmt_lines(p, mode):
        bevel_tile(p, 4.0, 4.5, 24.0, 22.0, 3.4)
        widths = (15.0, 11.0, 15.0, 9.5) if mode != "fill" else (15.0, 15.0, 15.0, 15.0)
        bars = QPainterPath()
        for i, lw in enumerate(widths):
            y = 9.0 + i * 3.8
            if mode in ("left", "fill"):
                x = 8.5
            elif mode == "center":
                x = 16.0 - lw / 2
            else:
                x = 23.5 - lw
            bars = U(bars, rr(x, y, lw, 1.8, 0.5))
        draw_disc_glyph(p, bars, dark=True)

    @act("format-justify-left", "gtk-justify-left")
    def _(p, sm):
        fmt_lines(p, "left")

    @act("format-justify-center", "gtk-justify-center")
    def _(p, sm):
        fmt_lines(p, "center")

    @act("format-justify-right", "gtk-justify-right")
    def _(p, sm):
        fmt_lines(p, "right")

    @act("format-justify-fill", "gtk-justify-fill")
    def _(p, sm):
        fmt_lines(p, "fill")

    @act("format-list-unordered", "")
    def _(p, sm):
        bevel_tile(p, 4.0, 4.5, 24.0, 22.0, 3.4)
        g = U(*[U(circ(9.4, y + 0.9, 1.3), rr(12.6, y, 11.0, 1.8, 0.5)) for y in (9.4, 14.6, 19.8)])
        draw_disc_glyph(p, g, dark=True)

    @act("format-list-ordered", "")
    def _(p, sm):
        bevel_tile(p, 4.0, 4.5, 24.0, 22.0, 3.4)
        g = U(*[U(rr(8.4, y - 0.3, 2.2, 2.4, 0.4), rr(12.6, y, 11.0, 1.8, 0.5)) for y in (9.4, 14.6, 19.8)])
        draw_disc_glyph(p, g, dark=True)

    @act("format-indent-more", "gtk-indent-ltr")
    def _(p, sm):
        bevel_tile(p, 4.0, 4.5, 24.0, 22.0, 3.4)
        bars = U(rr(8.2, 9.0, 15.6, 1.8, 0.5), rr(15.2, 13.0, 8.6, 1.8, 0.5), rr(15.2, 17.0, 8.6, 1.8, 0.5), rr(8.2, 21.0, 15.6, 1.8, 0.5))
        draw_disc_glyph(p, bars, dark=True)
        arr = poly((8.2, 12.6), (13.4, 15.9), (8.2, 19.2))
        paint_gel_shape(p, arr, 12.6, 19.2, "blue")

    @act("format-indent-less", "gtk-unindent-ltr")
    def _(p, sm):
        bevel_tile(p, 4.0, 4.5, 24.0, 22.0, 3.4)
        bars = U(rr(8.2, 9.0, 15.6, 1.8, 0.5), rr(15.2, 13.0, 8.6, 1.8, 0.5), rr(15.2, 17.0, 8.6, 1.8, 0.5), rr(8.2, 21.0, 15.6, 1.8, 0.5))
        draw_disc_glyph(p, bars, dark=True)
        arr = poly((13.4, 12.6), (8.2, 15.9), (13.4, 19.2))
        paint_gel_shape(p, arr, 12.6, 19.2, "blue")

    actions_map = {n: fn for n, _, fn in actions}
    return actions


class SoftPainter(QPainter):
    """Jaguar's toolbar icons have light grey rims and dark grey (not black) glyphs. The painters
    above draw near-black outlines, which read heavy, so every dark pen is lifted toward a mid tone
    and drawn thinner, and near-black fills become dark grey."""
    PEN_WIDTH = 0.7
    PEN_LIFT = 0.5     # move dark outline lightness halfway to OUTLINE_L
    OUTLINE_L = 0.62
    GLYPH = QColor("#3b3e43")

    @staticmethod
    def _lift(col, target, k):
        h, s, l, a = col.getHslF()
        if l >= target:
            return col
        out = QColor.fromHslF(max(h, 0.0), s * 0.85, l + (target - l) * k, a)
        return out

    def setPen(self, pen):
        if isinstance(pen, QColor):
            pen = QPen(pen)
        if isinstance(pen, QPen) and pen.style() != Qt.NoPen:
            col = pen.color()
            if col.lightnessF() < 0.55:
                pen = QPen(pen)
                pen.setColor(self._lift(col, self.OUTLINE_L, self.PEN_LIFT))
                pen.setWidthF(max(0.6, pen.widthF() * self.PEN_WIDTH))
        super().setPen(pen)

    def setBrush(self, brush):
        col = brush if isinstance(brush, QColor) else (
            brush.color() if isinstance(brush, QBrush) and brush.style() == Qt.SolidPattern else None)
        if col is not None and col.alpha() > 200 and col.lightnessF() < 0.16 and col.hslSaturationF() < 0.3:
            g = QColor(self.GLYPH)
            g.setAlpha(col.alpha())
            brush = g
        super().setBrush(brush)


def render_action_png(fn, size):
    """Supersample 2x onto a 32x32 logical coordinate space, then smooth-downsample."""
    ss = size * 2
    hi = QImage(ss, ss, QImage.Format_ARGB32_Premultiplied)
    hi.fill(Qt.transparent)
    p = SoftPainter(hi)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setRenderHint(QPainter.TextAntialiasing, True)
    p.setRenderHint(QPainter.SmoothPixmapTransform, True)
    p.scale(ss / 32.0, ss / 32.0)
    fn(p, size <= 16)
    p.end()
    return hi.scaled(size, size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)


# ==================================================================
# Theme Assembly & Output
# ==================================================================

CONTEXT = {
    "status": ("audio-volume", "network-", "battery", "bluetooth", "notification", "dialog-", "data-", "weather", "object-locked", "object-unlocked", "non-starred", "starred", "process-",
               "brightness", "high-brightness", "low-brightness", "update-", "mic-", "microphone-", "media-playback-playing", "media-playback-paused", "media-playback-stopped",
               "camera-on", "camera-off", "camera-ready", "klipper", "kdeconnect-tray", "input-keyboard-virtual", "keyboard-layout"),
    "devices": ("audio-input", "audio-headphones", "audio-speakers", "computer", "video-display", "drive-", "media-optical", "media-removable", "camera", "phone", "smartphone", "input-", "printer"),
    "places": ("folder", "user-trash", "user-home", "user-identity", "network-workgroup", "network-server", "inode-directory"),
    "apps": ("preferences-", "system-users", "internet-mail", "office-calendar", "help-browser"),
    "emblems": ("emblem-",),
    "mimetypes": ("text-x", "x-office"),
}


def context_of(name):
    if name in ("folder-new", "folder-open", "folder-sync", "process-stop", "dialog-ok", "dialog-cancel", "dialog-close"):
        return "actions"
    for ctx, prefixes in CONTEXT.items():
        if name.startswith(prefixes):
            return ctx
    return "actions"


def svg_d(path):
    out = []
    i = 0
    n = path.elementCount()
    while i < n:
        e = path.elementAt(i)
        if e.isMoveTo():
            out.append(f"M{e.x:.2f} {e.y:.2f}")
            i += 1
        elif e.isLineTo():
            out.append(f"L{e.x:.2f} {e.y:.2f}")
            i += 1
        else:
            c1 = e
            c2 = path.elementAt(i + 1)
            end = path.elementAt(i + 2)
            out.append(f"C{c1.x:.2f} {c1.y:.2f} {c2.x:.2f} {c2.y:.2f} {end.x:.2f} {end.y:.2f}")
            i += 3
    return "".join(out) + "Z"


def hollow(shape, w):
    """The outline band of a solid glyph, w units wide."""
    return QPainterPath(shape).subtracted(thin(shape, w)).simplified()


def menu_extra_overrides(lw=1.0):
    """Line versions of the tray glyphs that are solid shapes in the symbolic set, drawn like the
    10.2 menu extras: hairline outlines, small solid details. Built at STROKE_SCALE 1.0."""
    O = {}

    def add(names, solid, faint=None):
        for n in names.split():
            O[n] = (solid, faint)

    empty = QPainterPath()
    bell = U(circ(8, 6.6, 4.3), rr(3.7, 6.6, 8.6, 4.4), rr(1.8, 10.6, 12.4, 2.0, 1.0))
    bell_o = U(hollow(bell, lw), circ(8, 13.6, 1.4), circ(8, 2.0, 0.9))
    add("notifications notification-active", bell_o)
    add("notification-inactive notifications-disabled", empty, bell_o)
    add("notification-new", U(S(bell_o, circ(12.8, 3.4, 3.6)), circ(12.8, 3.4, 2.4)))

    rune = polyline([(5.0, 5.2), (11.0, 10.6), (8.0, 13.6), (8.0, 2.4), (11.0, 5.4), (5.0, 10.8)], lw)
    add("bluetooth bluetooth-active bluetooth-online network-bluetooth network-bluetooth-activated "
        "network-bluetooth-activated-locked network-wireless-bluetooth", rune)
    add("bluetooth-disabled bluetooth-inactive bluetooth-offline network-bluetooth-inactive", empty, rune)

    core = circ(8, 8, 2.7)
    rays = U(*[rot(line(8, 0.9, 8, 3.1, lw), a) for a in range(0, 360, 45)])
    add("brightness-high high-brightness video-display-brightness display-brightness", U(core, rays))
    add("brightness-low low-brightness", core, rays)

    upd = U(ring(8, 8, 6.4, lw))
    add("update-low update-medium update-high kpackagekit-updates software-update-available",
        U(upd, move(scale(arrow("down"), 0.55), 0, 0.2)))
    add("update-none", U(upd, scale(check_mark(lw * 1.6), 0.6)))
    add("update-busy", U(upd, scale(circular_arrow(True), 0.5)))

    add("klipper", U(hollow(rr(2.6, 2.6, 10.8, 12.4, 1.4), lw), rr(5.2, 1.0, 5.6, 3.0, 1.0),
                     line(5.4, 7.2, 10.6, 7.2, lw), line(5.4, 9.6, 10.6, 9.6, lw), line(5.4, 12.0, 8.8, 12.0, lw)))
    add("kdeconnect-tray kdeconnect", U(hollow(rr(4.4, 1.2, 7.2, 13.6, 1.8), lw), circ(8, 12.4, 0.8)))

    # Night Light: a crescent moon (on), a small sun (day), faint when off
    moon = hollow(S(circ(7.6, 8.4, 6.0), circ(10.8, 5.6, 5.0)), lw)
    add("redshift-status-on night-light night-light-on preferences-desktop-display-nightcolor", moon)
    add("redshift-status-day night-light-day", U(circ(8, 8, 2.4), *[rot(line(8, 2.0, 8, 3.8, lw), a) for a in range(0, 360, 45)]))
    add("redshift-status-off redshift-status-inactive night-light-off night-light-disabled", empty, moon)
    add("system-software-update software-update-available software-update-urgent",
        U(upd, move(scale(arrow("up"), 0.55), 0, -0.2)))

    # Lock Keys applet: an outlined shift arrow, faint when off
    shift = hollow(scale(arrow("up"), 0.86), lw)
    add("input-caps-on", shift)
    add("input-caps-off", empty, shift)

    # Weather, drawn like the other menu extras so Crystal's colour weather art doesn't land in
    # the panel (only 16-24 px is covered, so the weather popup keeps the colour art)
    def sun(cx, cy, r, ray):
        return U(circ(cx, cy, r), *[rot(line(cx, cy - r - 1.2, cx, cy - r - 1.2 - ray, lw), a, cx, cy)
                                     for a in range(0, 360, 45)])

    def moon_at(cx, cy, r):
        return hollow(S(circ(cx, cy, r), circ(cx + r * 0.55, cy - r * 0.45, r * 0.85)), lw)

    cloud_shape = U(circ(5.4, 9.0, 3.4), circ(9.6, 7.0, 4.3), rr(2.0, 8.8, 12.6, 4.9, 2.45))
    cloud = hollow(cloud_shape, lw)
    low_cloud = move(cloud, 0, 1.2)
    drops = U(*[line(x, 14.0, x - 0.8, 15.6, lw) for x in (5.6, 8.4, 11.2)])
    flakes = U(*[circ(x, 15.0, 0.75) for x in (5.6, 8.4, 11.2)])
    zap = scale(bolt(), 0.56, 8.4, 14.6)
    W = {
        "clear": sun(8, 8, 2.8, 2.0),
        "clear-night": moon_at(7.6, 8.4, 6.0),
        "few": U(S(sun(5.4, 5.4, 2.0, 1.4), cloud_shape.translated(1.4, 2.2)), cloud.translated(1.4, 2.2)),
        "few-night": U(S(moon_at(5.0, 5.0, 3.6), cloud_shape.translated(1.4, 2.2)), cloud.translated(1.4, 2.2)),
        "clouds": move(cloud, 0, 0.8),
        "rain": U(move(cloud, 0, -1.4), drops),
        "snow": U(move(cloud, 0, -1.4), flakes),
        "storm": U(S(move(cloud, 0, -1.4), zap.translated(0, 0.4)), zap),
        "fog": U(*[line(2.5 + (i % 2) * 1.5, 5.0 + i * 3.0, 13.5 - ((i + 1) % 2) * 1.5, 5.0 + i * 3.0, lw) for i in range(4)]),
    }
    for n in ("clear clear-wind", "clear-night clear-wind-night", "few-clouds few-clouds-day few-clouds-wind",
              "few-clouds-night few-clouds-wind-night", "clouds clouds-day clouds-wind many-clouds many-clouds-day "
              "many-clouds-wind overcast overcast-wind clouds-night clouds-wind-night many-clouds-night",
              "showers showers-day showers-night showers-scattered showers-scattered-day showers-scattered-night "
              "freezing-rain freezing-rain-day freezing-rain-night freezing-scattered-rain freezing-scattered-rain-day "
              "freezing-scattered-rain-night snow-rain",
              "snow snow-day snow-night snow-scattered snow-scattered-day snow-scattered-night hail",
              "storm storm-day storm-night showers-scattered-storm showers-scattered-storm-day "
              "showers-scattered-storm-night freezing-storm freezing-storm-day freezing-storm-night "
              "freezing-scattered-rain-storm freezing-scattered-rain-storm-day freezing-scattered-rain-storm-night "
              "snow-storm snow-storm-day snow-storm-night snow-scattered-storm snow-scattered-storm-day "
              "snow-scattered-storm-night",
              "fog mist"):
        first = n.split()[0]
        key = {"clear": "clear", "clear-night": "clear-night", "few-clouds": "few", "few-clouds-night": "few-night",
               "clouds": "clouds", "showers": "rain", "snow": "snow", "storm": "storm", "fog": "fog"}[first]
        add(" ".join(f"weather-{x}" for x in n.split()), W[key])
    add("weather-none-available", empty, W["clouds"])

    # Power profiles (the power applet on a desktop) and the device notifier
    zap_o = hollow(scale(bolt(), 1.05), lw * 0.9)
    add("battery-profile-performance power-profile-performance", zap_o)
    add("battery-profile-powersave power-profile-power-saver power-profile-powersave", moon)
    add("battery-profile-balanced power-profile-balanced", U(ring(8, 8, 6.0, lw), S(circ(8, 8, 6.0), rr(8, 0, 8, 16))))
    eject = U(hollow(poly((8, 2.6), (13.4, 8.6), (2.6, 8.6), round_=0.6), lw), rr(2.6, 11.0, 10.8, 2.0, 0.6))
    add("device-notifier media-eject", eject)
    return O


# The glyphs are drawn as solid shapes on a 16-unit grid; these erode every edge by a fixed
# amount so strokes read lighter, more on the panel where they're drawn at 22-24 px.
THIN = 0.18


def thin(path, d):
    if path is None or path.isEmpty() or d <= 0:
        return path
    st = QPainterPathStroker()
    st.setWidth(2 * d)
    st.setJoinStyle(Qt.RoundJoin)
    st.setCapStyle(Qt.RoundCap)
    p = QPainterPath(path)
    p.setFillRule(Qt.OddEvenFill)
    return p.subtracted(st.createStroke(p)).simplified()


def svg(solid, faint, size=16):
    body = []
    if faint is not None and not faint.isEmpty():
        body.append(f'<path class="ColorScheme-Text" d="{svg_d(faint)}" style="fill:currentColor;fill-opacity:{FAINT};fill-rule:evenodd"/>')
    if solid is not None and not solid.isEmpty():
        body.append(f'<path class="ColorScheme-Text" d="{svg_d(solid)}" style="fill:currentColor;fill-rule:evenodd"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 16 16">\n'
            '<style id="current-color-scheme" type="text/css">.ColorScheme-Text { color:#232629; }</style>\n'
            + "\n".join(body) + "\n</svg>\n")


TRAY = ("audio-volume", "network-wireless", "network-wired", "network-offline", "network-bluetooth", "network-vpn", "battery", "bluetooth", "notification",
        "brightness", "high-brightness", "low-brightness", "video-display-brightness", "update-", "kpackagekit", "mic-", "microphone-",
        "media-playback-playing", "media-playback-paused", "media-playback-stopped", "camera-on", "camera-off", "camera-ready",
        "klipper", "kdeconnect", "input-keyboard-virtual", "keyboard-layout", "firewall-applet", "pamac-tray", "redshift-status", "osd-",
        "input-caps", "weather-", "night-light", "system-software-update", "software-update",
        "battery-profile", "power-profile", "device-notifier", "media-eject")

ACTION_SIZES = (
    ("16x16",   16, 1, "Fixed",    ""),
    ("22x22",   22, 1, "Fixed",    ""),
    ("24x24",   24, 1, "Fixed",    ""),
    ("32x32",   32, 1, "Fixed",    ""),
    ("32x32@2", 32, 2, "Fixed",    "Scale=2\n"),
    ("48x48",   48, 1, "Scalable", "MinSize=36\nMaxSize=256\n"),
)

RICHER_SIZES = (
    ("16x16",   16, 1, "Fixed",    ""),
    ("22x22",   22, 1, "Fixed",    ""),
    ("32x32",   32, 1, "Fixed",    ""),
    ("48x48",   48, 1, "Fixed",    ""),
    ("64x64",   64, 1, "Fixed",    ""),
    ("128x128", 128, 1, "Scalable", "MinSize=72\nMaxSize=256\n"),
)

COMPACT_SIZES = (
    ("16x16",   16, 1, "Fixed",    ""),
    ("22x22",   22, 1, "Fixed",    ""),
    ("32x32",   32, 1, "Fixed",    ""),
    ("48x48",   48, 1, "Scalable", "MinSize=36\nMaxSize=256\n"),
)


def _emit_category(cat, items, size_specs):
    alias_count = 0
    dirs_out = []
    for sz_dir, sz, scale_f, kind, extra in size_specs:
        rel = f"{sz_dir}/{cat}"
        dirs_out.append((rel, cat, sz, kind, extra))
        d = os.path.join(OUT, rel)
        os.makedirs(d, exist_ok=True)
        px = sz * scale_f
        for canon, aliases, fn in items:
            img = render_action_png(fn, px)
            img.save(os.path.join(d, f"{canon}.png"))
            for al in aliases:
                if al and al != canon:
                    dst = os.path.join(d, f"{al}.png")
                    if not os.path.lexists(dst):
                        os.symlink(f"{canon}.png", dst)
                        if sz_dir == "32x32" and scale_f == 1:
                            alias_count += 1
    return dirs_out, alias_count


# Hand-drawn photo-illustrative icons (artwork/aqua-icons/*.svg, made by tools/draw_aqua_icons.py
# to match the HIG chapter 11 figures). Everything else full-colour comes from the inherited
# KrystalSVG theme (Crystal, KDE 3's Aqua-era set), which is installed separately because its
# licence (CC BY-NC-SA) can't be bundled here.
ARTWORK = os.path.join(ROOT, "artwork", "aqua-icons")
ARTWORK_ICONS = (
    # canonical name, context dir, aliases
    ("folder", "places", ("folder-blue", "inode-directory")),
    ("user-home", "places", ("folder-home",)),
    ("folder-download", "places", ("folder-downloads",)),
    ("folder-documents", "places", ("folder-text", "folder-notes")),
    ("folder-music", "places", ("folder-sound", "library-music")),
    ("folder-pictures", "places", ("folder-images", "folder-image", "folder-picture", "folder-photo")),
    ("folder-videos", "places", ("folder-video", "folder-movies")),
    ("folder-desktop", "places", ("user-desktop", "desktop")),
    ("folder-templates", "places", ("folder-design", "folder-drawing")),
    ("folder-publicshare", "places", ("folder-public", "folder-remote", "folder-network", "network-workgroup")),
    ("folder-red", "places", ("folder-important", "folder-bookmark", "folder-favorites")),
    ("folder-orange", "places", ()),
    ("folder-yellow", "places", ()),
    ("folder-green", "places", ()),
    ("folder-cyan", "places", ()),
    ("folder-violet", "places", ("folder-magenta",)),
    ("folder-grey", "places", ("folder-gray", "folder-black")),
    ("user-trash", "places", ("trashcan_empty", "user-trash-empty")),
    ("user-trash-full", "places", ("trashcan_full",)),
    ("system-file-manager", "apps", ("org.kde.dolphin", "dolphin", "file-manager")),
    ("utilities-terminal", "apps", ("org.kde.konsole", "konsole", "terminal")),
    ("systemsettings", "apps", ("org.kde.systemsettings",)),
    ("preferences-desktop-wallpaper", "apps", ("background",)),
    ("preferences-desktop-theme-global", "apps", ("preferences-desktop-plasma-theme", "preferences-desktop-theme-applications", "preferences-desktop-color", "preferences-desktop-icons", "preferences-desktop-cursors")),
    ("preferences-desktop-theme-windowdecorations", "apps", ("preferences-system-windows-actions", "preferences-desktop-virtual", "preferences-system-tabbox", "preferences-desktop-activities")),
    ("preferences-desktop-font", "apps", ("preferences-desktop-font-installer", "tools-check-spelling")),
    ("preferences-desktop-animations", "apps", ("preferences-desktop-effects", "preferences-desktop-gestures-screenedges", "preferences-system-splash")),
    ("preferences-desktop-notification-bell", "apps", ("preferences-desktop-feedback",)),
    ("preferences-desktop-sound", "apps", ("audio-speakers", "audio-card", "audio-headphones")),
    ("preferences-system-network", "apps", ("network-connect", "network-wired", "preferences-system-network-remote", "preferences-system-network-proxy")),
    ("preferences-desktop-display-randr", "apps", ("video-display", "monitor", "preferences-desktop-thunderbolt")),
    ("preferences-system-bluetooth", "apps", ("bluetooth",)),
    ("preferences-system-power-management", "apps", ("battery",)),
    ("preferences-security", "apps", ("preferences-desktop-user-password", "preferences-system-login", "folder-locked", "folder-encrypted")),
    ("preferences-system-users", "apps", ("preferences-online-accounts", "system-users", "user-identity")),
    ("preferences-desktop-keyboard", "apps", ("input-keyboard", "preferences-desktop-keyboard-shortcut", "preferences-desktop-locale")),
    ("preferences-desktop-mouse", "apps", ("input-mouse", "preferences-desktop-touchpad", "preferences-desktop-tablet", "preferences-desktop-touchscreen")),
    ("preferences-system-time", "apps", ("preferences-system-session-services", "system-log-out")),
    ("plasma-search", "apps", ("preferences-desktop-baloo", "preferences-web-browser-shortcuts", "system-search", "system-run")),
    ("preferences-desktop-default-applications", "apps", ("preferences-desktop-filetype-association", "applications-other")),
    ("preferences-desktop-accessibility", "apps", ("preferences-desktop-gaming",)),
    ("internet-mail", "apps", ("org.kde.kmail2", "kmail", "email", "mail-client")),
    ("multimedia-video-player", "apps", ("applications-multimedia", "org.kde.dragonplayer", "dragonplayer", "vlc", "org.videolan.VLC", "mpv", "io.mpv.Mpv", "totem", "org.gnome.Totem")),
    ("image-viewer", "apps", ("org.kde.gwenview", "gwenview", "eog", "org.gnome.eog", "org.gnome.Loupe", "accessories-image-viewer")),
    ("accessories-screenshot", "apps", ("org.kde.spectacle", "spectacle", "ksnapshot", "applets-screenshooter", "org.gnome.Screenshot")),
    ("antigravity", "apps", ("google-antigravity", "agy")),
    ("bazaar", "apps", ("io.github.kolunmi.Bazaar", "org.kde.discover", "plasmadiscover", "system-software-install", "org.gnome.Software")),
    ("discord", "apps", ("com.discordapp.Discord", "dev.vencord.Vesktop", "internet-chat", "org.kde.neochat")),
    ("github-desktop", "apps", ("io.github.shiftey.Desktop", "git", "git-gui")),
    ("firefox", "apps", ("org.mozilla.firefox", "firefox-esr", "firefox-developer-edition", "firefox-nightly", "io.gitlab.librewolf-community", "librewolf")),
    ("claude-desktop", "apps", ("claude", "ai.anthropic.claude")),
    ("1password", "apps", ("com.onepassword.OnePassword", "org.kde.kwalletmanager5", "kwalletmanager", "org.gnome.seahorse.Application", "seahorse", "keepassxc", "org.keepassxc.KeePassXC", "bitwarden", "com.bitwarden.desktop")),
    ("cider", "apps", ("Cider", "sh.cider.Cider")),
    ("spotify", "apps", ("spotify-client", "com.spotify.Client")),
    ("steam", "apps", ("com.valvesoftware.Steam", "steam-native")),
    ("vscode", "apps", ("code", "visual-studio-code", "com.visualstudio.code", "code-oss", "vscodium", "com.vscodium.codium")),
    ("sober", "apps", ("org.vinegarhq.Sober",)),
    ("bionic", "apps", ()),
    ("obs-studio", "apps", ("com.obsproject.Studio", "obs")),
    ("libreoffice-writer", "apps", ("org.libreoffice.LibreOffice.writer", "libreoffice-oasis-text")),
    ("libreoffice-calc", "apps", ("org.libreoffice.LibreOffice.calc", "libreoffice-oasis-spreadsheet")),
    ("libreoffice-impress", "apps", ("org.libreoffice.LibreOffice.impress", "libreoffice-oasis-presentation")),
    ("okular", "apps", ("org.kde.okular",)),
    ("ark", "apps", ("org.kde.ark", "accessories-archiver")),
    ("drive-harddisk", "devices", ("drive-harddisk-root", "drive-harddisk-system", "hdd_unmount")),
    ("drive-removable-media", "devices", ("drive-harddisk-ieee1394", "drive-multidisk", "drive-partition", "drive-multipartition")),
    ("drive-removable-media-usb", "devices", ("drive-harddisk-usb",)),
    ("drive-removable-media-usb-pendrive", "devices", ("media-flash", "usbpendrive_unmount")),
    ("media-optical", "devices", ("media-optical-dvd", "media-optical-audio", "media-optical-data", "media-optical-video", "media-optical-recordable", "cdrom_unmount", "dvd_unmount")),
    ("drive-optical", "devices", ("drive-cdrom",)),
    ("media-floppy", "devices", ("3floppy_unmount", "media-zip")),
    ("media-flash-sd-mmc", "devices", ("media-flash-memory-stick", "media-flash-smart-media")),
    ("computer", "devices", ("desktop-computer",)),
    ("computer-laptop", "devices", ("laptop",)),
    ("printer", "devices", ("printer-laser", "cupsprinter", "preferences-devices-printer")),
    ("camera-photo", "devices", ("camera-digital", "camera-web", "camera-video")),
    ("phone", "devices", ("smartphone", "phone-apple-iphone", "multimedia-player")),
    ("network-server", "places", ("folder-cloud", "certificate-server")),
    ("internet-web-browser", "apps", ("web-browser", "browser", "chromium", "chromium-browser", "org.chromium.Chromium", "google-chrome", "com.google.Chrome", "brave-browser", "com.brave.Browser", "epiphany", "org.gnome.Epiphany", "vivaldi", "zen-browser")),
    ("accessories-text-editor", "apps", ("org.kde.kwrite", "kwrite", "org.kde.kate", "kate", "text-editor", "org.gnome.TextEditor", "gedit", "org.gnome.gedit", "org.xfce.mousepad", "mousepad", "leafpad", "featherpad", "pluma")),
    ("accessories-calculator", "apps", ("org.kde.kcalc", "kcalc", "org.kde.kalk", "calc", "org.gnome.Calculator", "gnome-calculator", "galculator", "qalculate")),
    ("utilities-system-monitor", "apps", ("org.kde.plasma-systemmonitor", "ksysguard", "org.gnome.SystemMonitor", "gnome-system-monitor", "htop", "btop", "org.kde.kjournaldbrowser", "hwinfo", "kinfocenter", "org.kde.kinfocenter")),
    ("kdeconnect", "apps", ("org.kde.kdeconnect", "org.kde.kdeconnect.app", "org.kde.kdeconnect.sms", "org.kde.kdeconnect.nonplasma", "gsconnect")),
    ("kolourpaint", "apps", ("org.kde.kolourpaint", "gimp", "org.gimp.GIMP", "krita", "org.kde.krita", "pinta", "inkscape", "org.inkscape.Inkscape", "libreoffice-draw", "org.libreoffice.LibreOffice.draw", "mypaint")),
    ("transmission", "apps", ("transmission-gtk", "transmission-qt", "com.transmissionbt.Transmission", "org.qbittorrent.qBittorrent", "qbittorrent", "org.kde.ktorrent", "ktorrent", "deluge", "fragments")),
    ("partitionmanager", "apps", ("org.kde.partitionmanager", "gparted", "gnome-disks", "org.gnome.DiskUtility", "disks", "org.fedoraproject.MediaWriter", "mediawriter")),
    ("filelight", "apps", ("org.kde.filelight", "baobab", "org.gnome.baobab", "qdirstat", "gdmap")),
    ("geany", "apps", ("org.geany.Geany",)),
    ("lmstudio", "apps", ("ai.lmstudio.LMStudio", "lm-studio", "ollama")),
    ("skanpage", "apps", ("org.kde.skanpage", "skanlite", "org.kde.skanlite", "simple-scan", "org.gnome.SimpleScan", "scanner", "xsane")),
    ("kleopatra", "apps", ("org.kde.kleopatra", "org.kde.kwatchgnupg", "gnupg", "gpa")),
    ("text-x-generic", "mimetypes", ("text-plain", "application-x-zerosize", "text-x-readme", "text-x-log")),
    ("application-pdf", "mimetypes", ("x-office-document-pdf", "application-x-pdf")),
    ("image-x-generic", "mimetypes", ("image-png", "image-jpeg", "image-webp", "image-gif", "image-bmp", "image-tiff")),
    ("image-svg+xml", "mimetypes", ("application-illustrator", "image-x-eps", "x-office-drawing")),
    ("audio-x-generic", "mimetypes", ("audio-mpeg", "audio-mp3", "audio-flac", "audio-x-wav", "audio-ogg", "audio-mp4")),
    ("video-x-generic", "mimetypes", ("video-mp4", "video-x-matroska", "video-webm", "video-x-msvideo", "video-quicktime")),
    ("package-x-generic", "mimetypes", ("application-x-rpm", "application-x-deb", "application-vnd.flatpak", "application-x-appimage")),
    ("application-x-archive", "mimetypes", ("application-zip", "application-x-compressed-tar", "application-x-bzip-compressed-tar", "application-x-xz-compressed-tar", "application-x-7z-compressed", "application-vnd.rar")),
    ("text-html", "mimetypes", ("application-xhtml+xml", "text-xml", "application-xml")),
    ("text-x-script", "mimetypes", ("application-x-shellscript", "text-x-makefile", "application-x-executable-script")),
    ("text-x-python", "mimetypes", ("application-x-python-bytecode",)),
    ("text-x-csrc", "mimetypes", ("text-x-c++src", "text-x-chdr", "text-x-rust", "text-javascript", "application-json", "text-markdown", "text-css")),
)


def render_artwork_png(svg_path, px):
    import gi
    gi.require_version("Rsvg", "2.0")
    import cairo
    from gi.repository import Rsvg
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, px, px)
    cr = cairo.Context(surf)
    vp = Rsvg.Rectangle()
    vp.x, vp.y, vp.width, vp.height = 0, 0, px, px
    Rsvg.Handle.new_from_file(svg_path).render_document(cr, vp)
    return surf


def _emit_artwork(size_specs):
    dirs_out = []
    for sz_dir, sz, scale_f, kind, extra in size_specs:
        for canon, cat, aliases in ARTWORK_ICONS:
            rel = f"{sz_dir}/{cat}"
            if (rel, cat, sz, kind, extra) not in dirs_out:
                dirs_out.append((rel, cat, sz, kind, extra))
            d = os.path.join(OUT, rel)
            os.makedirs(d, exist_ok=True)
            render_artwork_png(os.path.join(ARTWORK, f"{canon}.svg"), sz * scale_f).write_to_png(
                os.path.join(d, f"{canon}.png"))
            for al in aliases:
                dst = os.path.join(d, f"{al}.png")
                if not os.path.lexists(dst):
                    os.symlink(f"{canon}.png", dst)
    return dirs_out


def _emit_accepted_papirus(size_specs):
    """Emit any auto-glassified Papirus icons accepted via tools/papirus_curator.py
    (artwork/papirus-accepted-svgs/<cat>/<name>.svg), without overriding hand-crafted ARTWORK_ICONS."""
    acc_root = os.path.join(ROOT, "artwork", "papirus-accepted-svgs")
    state_json = os.path.join(ROOT, "artwork", "papirus-curation.json")
    os.makedirs(acc_root, exist_ok=True)

    handcrafted = {(canon, cat) for canon, cat, _ in ARTWORK_ICONS}
    # Load alias map if Papirus cache is available
    alias_lookup = {}
    if os.path.isfile(state_json):
        try:
            import glassify_papirus as gp
            if os.path.isdir(gp.PAPIRUS_DIR):
                for it in gp.scan_entire_papirus():
                    alias_lookup[(it["category"], it["name"])] = it["aliases"]
        except Exception:
            pass

    accepted_entries = []
    for cat in sorted(os.listdir(acc_root)):
        cat_d = os.path.join(acc_root, cat)
        if not os.path.isdir(cat_d):
            continue
        for fn in sorted(os.listdir(cat_d)):
            if not fn.endswith(".svg"):
                continue
            stem = fn[:-4]
            if (stem, cat) in handcrafted:
                continue
            accepted_entries.append((stem, cat, os.path.join(cat_d, fn), alias_lookup.get((cat, stem), ())))

    dirs_out = []
    for sz_dir, sz, scale_f, kind, extra in size_specs:
        # Pre-register core colour directories in index.theme so live-accepted icons in any category resolve immediately!
        for base_cat in ("places", "apps", "devices", "mimetypes", "categories", "status", "emblems", "emotes"):
            rel_base = f"{sz_dir}/{base_cat}"
            if (rel_base, base_cat, sz, kind, extra) not in dirs_out:
                os.makedirs(os.path.join(OUT, rel_base), exist_ok=True)
                dirs_out.append((rel_base, base_cat, sz, kind, extra))
        for stem, cat, svg_p, aliases in accepted_entries:
            rel = f"{sz_dir}/{cat}"
            if (rel, cat, sz, kind, extra) not in dirs_out:
                dirs_out.append((rel, cat, sz, kind, extra))
            d = os.path.join(OUT, rel)
            os.makedirs(d, exist_ok=True)
            dst_png = os.path.join(d, f"{stem}.png")
            if not os.path.lexists(dst_png):
                render_artwork_png(svg_p, sz * scale_f).write_to_png(dst_png)
            for al in aliases:
                al_dst = os.path.join(d, f"{al}.png")
                if not os.path.lexists(al_dst):
                    os.symlink(f"{stem}.png", al_dst)
    return dirs_out, len(accepted_entries)


def build():
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)

    # The procedural places/devices/apps/categories/applets painters (icons_lib) read as flat
    # clip-art next to the widget style, so they are no longer emitted; see AGENTS.md.
    cat_groups = [
        ("actions", build_action_painters(), ACTION_SIZES),
    ]

    try:
        from icons_lib.mimetypes_icons import build_mimetypes_painters
        cat_groups.append(("mimetypes", build_mimetypes_painters(), RICHER_SIZES))
    except ImportError:
        pass

    try:
        from icons_lib.status_emblems_emotes import build_status_emblems_emotes_painters
        st_p, em_p, emo_p, anim_p, spec_p = build_status_emblems_emotes_painters()
        cat_groups.extend([
            ("status", st_p, RICHER_SIZES),
            ("emblems", em_p, COMPACT_SIZES),
            ("emotes", emo_p, COMPACT_SIZES),
            ("animations", anim_p, COMPACT_SIZES),
            ("special", spec_p, COMPACT_SIZES),
        ])
    except ImportError:
        pass

    try:
        from icons_lib.actions_extra import extend_action_painters
        cat_groups[0] = ("actions", extend_action_painters(cat_groups[0][1]), ACTION_SIZES)
    except ImportError:
        pass

    all_color_dirs = []
    summary = []
    for cat, items, specs in cat_groups:
        c_dirs, n_al = _emit_category(cat, items, specs)
        all_color_dirs.extend(c_dirs)
        summary.append(f"{cat}:{len(items)}(+{n_al})")
    all_color_dirs.extend(_emit_artwork(RICHER_SIZES))
    summary.append(f"artwork:{len(ARTWORK_ICONS)}(+{sum(len(a) for *_, a in ARTWORK_ICONS)})")
    pap_dirs, n_pap = _emit_accepted_papirus(RICHER_SIZES)
    for pd in pap_dirs:
        if pd not in all_color_dirs:
            all_color_dirs.append(pd)
    if n_pap:
        summary.append(f"papirus_accepted:{n_pap}")

    # 2. Symbolic & panel menu-extra SVGs
    sym_icons = build_symbolic_icons()

    # Tray names in the 10.2 menu-extra style (hairline strokes, small solid bodies), plus line
    # versions of the glyphs that are solid shapes in the symbolic set. Plasma's tray asks for the
    # -symbolic names at 16 px, so these replace the symbolic glyph for tray names everywhere;
    # all other symbolic glyphs keep the solid style.
    global STROKE_SCALE
    overrides = menu_extra_overrides()
    STROKE_SCALE = MENU_EXTRA_STROKE
    try:
        extras = build_symbolic_icons()
    finally:
        STROKE_SCALE = 1.0
    extras = {k: v for k, v in extras.items() if k.startswith(TRAY)}
    extras.update(overrides)

    contexts = set()
    for name, (solid, faint) in sym_icons.items():
        ctx = context_of(name)
        contexts.add(ctx)
        d = os.path.join(OUT, "symbolic", ctx)
        os.makedirs(d, exist_ok=True)
        if name in extras:
            solid, faint = extras[name]
            body = svg(solid, faint)
        else:
            body = svg(thin(solid, THIN), thin(faint, THIN))
        with open(os.path.join(d, f"{name}-symbolic.svg"), "w") as f:
            f.write(body)
    for name in sorted(set(extras) - set(sym_icons)):
        solid, faint = extras[name]
        d = os.path.join(OUT, "symbolic", "status")
        os.makedirs(d, exist_ok=True)
        contexts.add("status")
        with open(os.path.join(d, f"{name}-symbolic.svg"), "w") as f:
            f.write(svg(solid, faint))
    d = os.path.join(OUT, "panel", "status")
    os.makedirs(d, exist_ok=True)
    for name, (solid, faint) in extras.items():
        with open(os.path.join(d, f"{name}.svg"), "w") as f:
            f.write(svg(solid, faint))

    ctx_names = {
        "actions": "Actions", "status": "Status", "devices": "Devices",
        "places": "Places", "apps": "Applications", "categories": "Categories",
        "applets": "Applications", "emblems": "Emblems", "emotes": "Emotes",
        "mimetypes": "MimeTypes", "animations": "Animations", "special": "Actions",
    }
    dirs = [rel for rel, *_ in all_color_dirs] + [f"symbolic/{c_}" for c_ in sorted(contexts)] + ["panel/status"]
    with open(os.path.join(OUT, "index.theme"), "w") as f:
        f.write("[Icon Theme]\nName=Oxygen Pinstripe\n"
                "Comment=Mac OS X 10.2 Aqua icon theme and menu-extra symbolic glyphs\n"
                "Inherits=KrystalSVG,oxygen,breeze,hicolor\nExample=system-file-manager\nDisplayDepth=32\nDesktopDefault=48\nToolbarDefault=32\nMainToolbarDefault=32\nSmallDefault=16\nPanelDefault=22\n"
                "FollowsColorScheme=true\n"
                f"Directories={','.join(dirs)}\n\n")
        for rel, cat, sz, kind, extra in all_color_dirs:
            f.write(f"[{rel}]\nContext={ctx_names[cat]}\nSize={sz}\n{extra}Type={kind}\n\n")
        for c_ in sorted(contexts):
            f.write(f"[symbolic/{c_}]\nContext={ctx_names[c_]}\nSize=16\nMinSize=8\nMaxSize=512\nType=Scalable\n\n")
        f.write("[panel/status]\nContext=Status\nSize=22\nMinSize=16\nMaxSize=24\nType=Scalable\n\n")
    print("wrote 10.2 Aqua icons ->", ", ".join(summary), f"+ {len(sym_icons)} symbolics to {OUT}")


if __name__ == "__main__":
    build()
