#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Generate the "Oxygen Pinstripe" icon theme (icons/Oxygen-Pinstripe).

It inherits Oxygen for every full-colour icon and replaces the symbolic ones with solid,
rounded glyphs in the manner of the Mac OS X 10.2 menu extras (the AirPort fan, the speaker
with waves, the horizontal battery, the eject key, solid triangle arrows) instead of thin
line art.

Every glyph is built from filled shapes (strokes are converted to outlines with
QPainterPathStroker), so GTK and KDE can recolour it: paths carry the ColorScheme-Text class
with fill:currentColor, and "inactive" parts (unused signal bars, quiet volume waves) are
the same colour at reduced opacity.

    python3 tools/make_icons.py
"""
import math
import os
import shutil
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QPointF, QRectF, Qt  # noqa: E402
from PySide6.QtGui import QGuiApplication, QPainterPath, QPainterPathStroker, QPolygonF, QTransform  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "icons", "Oxygen-Pinstripe")
FAINT = 0.35


# ------------------------------------------------------------------ shape helpers (16x16 grid)

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
        # soften corners by stroking the outline with a round join and uniting
        p = U(p, stroke(p, round_))
    return p


def stroke(path, width, cap=Qt.RoundCap, join=Qt.RoundJoin):
    s = QPainterPathStroker()
    s.setWidth(width)
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


# ------------------------------------------------------------------ building blocks

def triangle(direction, cx=8, cy=8, s=5.0):
    """Solid Aqua triangle, softly rounded."""
    h = s * 0.9
    pts = {"down": [(cx - s, cy - h / 2), (cx + s, cy - h / 2), (cx, cy + h / 2 + 0.4)],
           "up": [(cx - s, cy + h / 2), (cx + s, cy + h / 2), (cx, cy - h / 2 - 0.4)],
           "right": [(cx - h / 2, cy - s), (cx - h / 2, cy + s), (cx + h / 2 + 0.4, cy)],
           "left": [(cx + h / 2, cy - s), (cx + h / 2, cy + s), (cx - h / 2 - 0.4, cy)]}[direction]
    return poly(*pts, round_=1.0)


def arrow(direction):
    """Solid arrow: a broad triangular head on a rounded shaft."""
    base = U(poly((8, 1.6), (14.2, 8), (10.4, 8), (10.4, 8), (5.6, 8), (1.8, 8), round_=1.0), rr(5.9, 7, 4.2, 7.6, 1.2))
    return rot(base, {"up": 0, "right": 90, "down": 180, "left": 270}[direction])


def speaker():
    return U(rr(1.5, 5.6, 3.6, 4.8, 0.8), poly((4.4, 5.6), (8.6, 2.0), (8.6, 14.0), (4.4, 10.4), round_=0.8))


def waves():
    return arc(7.0, 8, 3.6, -42, 84, 1.7), arc(7.0, 8, 6.4, -46, 92, 1.7)


def fan_arcs():
    # AirPort-style fan: three arcs and a dot, opening upwards
    cx, cy = 8, 13.2
    return (circ(cx, cy, 1.45), arc(cx, cy, 4.0, 45, 90, 1.9), arc(cx, cy, 7.0, 45, 90, 1.9), arc(cx, cy, 10.0, 47, 86, 1.9))


def battery_shell():
    return U(S(rr(0.8, 4.2, 13.4, 7.6, 1.8), rr(2.4, 5.8, 10.2, 4.4, 0.8)), rr(14.3, 6.2, 1.5, 3.6, 0.6))


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


def undo_arrow():
    a = arc(9.0, 10.0, 4.6, 0, 160, 2.2, Qt.FlatCap)
    head = poly((0.8, 9.0), (6.6, 8.2), (3.0, 13.6), round_=0.6)
    return U(a, head, rr(12.5, 9.6, 2.2, 3.4, 1.0))


# ------------------------------------------------------------------ the icon set

def build_icons():
    I = {}  # name -> (solid path, faint path or None)

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
    add("system-lock-screen object-locked lock", padlock())
    add("object-unlocked", U(S(rr(2.6, 7.0, 10.8, 7.8, 1.6), circ(8, 10.4, 1.3)), arc(11.2, 6.4, 3.3, 0, 180, 2.0, Qt.FlatCap), rr(12.5, 6.3, 2.0, 2.6)))
    add("system-log-out", U(S(rr(1.6, 1.6, 8.0, 12.8, 1.4), rr(3.2, 3.2, 4.8, 9.6, 0.6)), move(arrow("right"), 3.0, 0)))
    add("system-suspend", U(S(circ(8, 8, 6.4), circ(10.6, 6.0, 5.4))))

    # search, settings, input
    add("system-search edit-find search", magnifier())
    add("zoom-in", U(S(magnifier(), circ(6.6, 6.6, 3.0)), plus(6.6, 6.6, 2.0, 1.4)))
    add("zoom-out", U(S(magnifier(), circ(6.6, 6.6, 3.0)), line(4.6, 6.6, 8.6, 6.6, 1.4)))
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
    add("user-trash edit-delete-shred user-trash-empty", trash)
    add("user-trash-full", trash)
    add("folder folder-closed inode-directory folder-documents", folder())
    add("folder-open document-open", U(S(U(rr(1.2, 2.6, 6.0, 3.2, 1.2), rr(1.2, 4.2, 13.6, 9.6, 1.6)), rr(1.0, 6.0, 14.4, 9.0)),
                                         poly((2.6, 7.0), (15.4, 7.0), (13.6, 13.8), (1.0, 13.8), round_=0.8)))
    add("user-home go-home folder-home", S(U(poly((8, 1.2), (15.2, 8.2), (0.8, 8.2), round_=0.8), rr(3.2, 7.4, 9.6, 7.4, 0.8)), rr(6.8, 9.8, 2.4, 5.2, 0.5)))
    add("folder-download download go-down-skip", S(folder(), move(scale(arrow("down"), 0.55), 0, 1.6)))
    add("text-x-generic document-new-from-template x-office-document", S(page(), rr(5.0, 7.0, 6.0, 1.0, 0.4), rr(5.0, 9.2, 6.0, 1.0, 0.4), rr(5.0, 11.4, 4.0, 1.0, 0.4)))
    add("document-new", S(page(), plus(8, 9.6, 2.6, 1.6)))
    add("document-save document-save-as", U(S(rr(1.6, 1.6, 12.8, 12.8, 1.8), rr(4.4, 1.0, 7.2, 4.6, 0.6), rr(4.0, 8.6, 8.0, 5.0, 0.6)), rr(8.6, 2.2, 1.6, 2.6, 0.4)))
    printer = U(S(rr(1.2, 5.6, 13.6, 6.4, 1.6), rr(3.6, 9.6, 8.8, 3.0)), rr(4.0, 1.6, 8.0, 3.4, 0.6), S(rr(4.0, 9.8, 8.0, 4.8, 0.6), rr(5.2, 11.2, 5.6, 0.9), rr(5.2, 12.8, 5.6, 0.9)))
    add("document-print printer", printer)
    add("edit-copy", U(S(rr(1.4, 1.4, 8.8, 10.2, 1.4), rr(3.0, 3.0, 5.6, 7.0, 0.6)), rr(5.2, 4.4, 9.4, 10.2, 1.4)))
    scissors = U(ring(4.4, 11.6, 2.0, 1.7), ring(11.6, 11.6, 2.0, 1.7), line(5.6, 9.6, 11.0, 1.6, 1.8), line(10.4, 9.6, 5.0, 1.6, 1.8))
    add("edit-cut", scissors)
    add("edit-paste", U(S(rr(2.2, 2.6, 11.6, 12.2, 1.6), rr(4.0, 5.0, 8.0, 8.2, 0.6)), rr(5.0, 1.0, 6.0, 3.2, 1.0), rr(5.6, 6.6, 4.8, 1.0, 0.4), rr(5.6, 8.8, 4.8, 1.0, 0.4), rr(5.6, 11.0, 3.2, 1.0, 0.4)))
    add("edit-delete edit-clear-all window-close dialog-close process-close tab-close", cross())
    add("edit-clear edit-clear-locationbar-rtl", S(poly((5.0, 2.6), (14.6, 2.6), (14.6, 13.4), (5.0, 13.4), (0.8, 8.0), round_=1.2), cross(9.4, 8.0, 2.4, 1.6)))
    add("edit-undo", undo_arrow())
    add("edit-redo", flip_h(undo_arrow()))
    add("edit-select-all", U(*[rr(x, y, 2.2, 2.2, 0.4) for x, y in ((1.4, 1.4), (6.9, 1.4), (12.4, 1.4), (1.4, 6.9), (12.4, 6.9), (1.4, 12.4), (6.9, 12.4), (12.4, 12.4))], rr(4.6, 4.6, 6.8, 6.8, 1.0)))
    add("edit-rename document-edit edit-entry", U(rot(U(rr(6.6, 0.8, 2.8, 10.6, 0.8), poly((6.6, 11.8), (9.4, 11.8), (8.0, 14.6))), 40), rr(1.4, 13.6, 7.0, 1.4, 0.6)))
    add("bookmark-new bookmarks emblem-favorite starred bookmark", star())
    add("non-starred", QPainterPath(), star())
    add("mail-unread mail-message mail-message-new internet-mail", envelope())
    add("mail-send", rot(poly((1.0, 7.4), (15.0, 1.6), (9.6, 15.0), (7.6, 9.0), round_=0.8), 0))
    add("appointment-new office-calendar view-calendar x-office-calendar", U(S(rr(1.4, 2.6, 13.2, 12.0, 1.6), rr(3.0, 6.4, 10.0, 6.6, 0.4)), rr(4.0, 1.0, 1.8, 3.4, 0.8), rr(10.2, 1.0, 1.8, 3.4, 0.8),
                                                                                 *[rr(4.0 + i * 3.0, 7.6 + j * 2.6, 1.8, 1.6, 0.3) for i in range(3) for j in range(2)]))
    add("chronometer clock preferences-system-time", S(circ(8, 8, 6.8), circ(8, 8, 5.4)).united(clock_hands()).simplified())

    # devices
    add("computer video-display computer-laptop preferences-desktop-display", monitor())
    add("drive-harddisk drive-harddisk-solidstate", S(rr(0.8, 4.4, 14.4, 7.2, 2.0), circ(12.0, 8.0, 1.0), rr(3.0, 7.4, 5.6, 1.2, 0.5)))
    add("media-optical drive-optical media-optical-cd-audio", S(circ(8, 8, 7.0), circ(8, 8, 1.6)))
    add("drive-removable-media media-removable drive-removable-media-usb", U(rr(4.0, 6.0, 8.0, 9.0, 1.4), S(rr(5.2, 1.0, 5.6, 5.6, 0.6), rr(6.4, 2.2, 1.0, 1.2), rr(8.6, 2.2, 1.0, 1.2))))
    add("camera-photo camera-web", S(U(rr(0.8, 4.2, 14.4, 9.6, 1.8), rr(5.0, 2.4, 6.0, 2.6, 0.8)), ring(8, 8.9, 2.6, 1.5)))
    add("phone smartphone", S(rr(4.0, 0.8, 8.0, 14.4, 1.8), rr(5.4, 2.6, 5.2, 9.4, 0.4), circ(8, 13.4, 0.8)))
    add("printer-network network-workgroup network-server", U(rr(1.6, 1.4, 12.8, 4.0, 1.0), rr(1.6, 6.0, 12.8, 4.0, 1.0), rr(7.2, 10.0, 1.6, 2.6), rr(2.4, 12.6, 11.2, 1.6, 0.8)))
    add("user-identity system-users user avatar-default", person())
    add("system-users group", U(move(scale(person(), 0.72, 8, 15), -3.2, 0), move(scale(person(), 0.72, 8, 15), 3.2, 0)))
    add("weather-clear", U(circ(8, 8, 3.2), *[rot(rr(7.2, 0.8, 1.6, 3.0, 0.8), a) for a in range(0, 360, 45)]))

    # navigation: solid arrows and Aqua triangles
    for d, names in (("up", "go-up arrow-up"), ("down", "go-down arrow-down"), ("left", "go-previous go-previous-symbolic-rtl arrow-left"), ("right", "go-next arrow-right")):
        add(names, arrow(d))
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

    # window, lists, menus
    add("window-minimize", rr(2.4, 10.4, 11.2, 2.6, 1.2))
    add("window-maximize", S(rr(2.0, 2.0, 12.0, 12.0, 1.6), rr(4.2, 5.0, 7.6, 6.8, 0.4)))
    add("window-restore", U(S(rr(5.0, 1.6, 9.4, 9.4, 1.4), rr(6.8, 4.2, 5.8, 5.0, 0.3)), S(rr(1.6, 5.0, 9.4, 9.4, 1.4), rr(3.4, 7.6, 5.8, 5.0, 0.3))))
    add("list-add add value-increase", plus())
    add("list-remove remove value-decrease", line(2.5, 8, 13.5, 8, 2.6))
    add("open-menu application-menu hamburger-menu", U(rr(2.0, 3.0, 12.0, 2.2, 1.1), rr(2.0, 6.9, 12.0, 2.2, 1.1), rr(2.0, 10.8, 12.0, 2.2, 1.1)))
    add("view-more view-more-horizontal overflow-menu", U(circ(3.2, 8, 1.6), circ(8, 8, 1.6), circ(12.8, 8, 1.6)))
    add("view-more-vertical", U(circ(8, 3.2, 1.6), circ(8, 8, 1.6), circ(8, 12.8, 1.6)))
    add("view-list view-list-details view-list-text", U(*[U(circ(2.6, y, 1.3), rr(5.4, y - 1.0, 9.0, 2.0, 1.0)) for y in (3.6, 8.0, 12.4)]))
    add("view-grid view-list-icons view-app-grid", U(*[rr(x, y, 5.4, 5.4, 1.2) for x in (1.6, 9.0) for y in (1.6, 9.0)]))
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

    return I


CONTEXT = {
    "status": ("audio-volume", "network-", "battery", "bluetooth", "notification", "dialog-", "data-", "weather", "object-locked", "object-unlocked", "non-starred", "starred", "process-"),
    "devices": ("audio-input", "audio-headphones", "audio-speakers", "computer", "video-display", "drive-", "media-optical", "media-removable", "camera", "phone", "smartphone", "input-", "printer"),
    "places": ("folder", "user-trash", "user-home", "user-identity", "network-workgroup", "network-server", "inode-directory"),
    "apps": ("preferences-", "system-users", "internet-mail", "office-calendar", "help-browser"),
    "emblems": ("emblem-",),
    "mimetypes": ("text-x", "x-office"),
}


def context_of(name):
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
        else:  # curve: this element + 2 data points
            c1 = e
            c2 = path.elementAt(i + 1)
            end = path.elementAt(i + 2)
            out.append(f"C{c1.x:.2f} {c1.y:.2f} {c2.x:.2f} {c2.y:.2f} {end.x:.2f} {end.y:.2f}")
            i += 3
    return "".join(out) + "Z"


def svg(solid, faint, size=16):
    body = []
    if faint is not None and not faint.isEmpty():
        body.append(f'<path class="ColorScheme-Text" d="{svg_d(faint)}" style="fill:currentColor;fill-opacity:{FAINT};fill-rule:evenodd"/>')
    if solid is not None and not solid.isEmpty():
        body.append(f'<path class="ColorScheme-Text" d="{svg_d(solid)}" style="fill:currentColor;fill-rule:evenodd"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 16 16">\n'
            '<style id="current-color-scheme" type="text/css">.ColorScheme-Text { color:#232629; }</style>\n'
            + "\n".join(body) + "\n</svg>\n")


TRAY = ("audio-volume", "network-wireless", "network-wired", "network-offline", "battery", "bluetooth", "notification")


def build():
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    icons = build_icons()
    contexts = set()
    for name, (solid, faint) in icons.items():
        # symbolic: name-symbolic, any size
        ctx = context_of(name)
        contexts.add(ctx)
        d = os.path.join(OUT, "symbolic", ctx)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, f"{name}-symbolic.svg"), "w") as f:
            f.write(svg(solid, faint))
        # menu extras: the plain tray names at panel sizes, so the system tray matches the menu bar
        if name.startswith(TRAY):
            d = os.path.join(OUT, "panel", "status")
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, f"{name}.svg"), "w") as f:
                f.write(svg(solid, faint))

    dirs = [f"symbolic/{c}" for c in sorted(contexts)] + ["panel/status"]
    ctx_names = {"actions": "Actions", "status": "Status", "devices": "Devices", "places": "Places", "apps": "Applications",
                 "emblems": "Emblems", "mimetypes": "MimeTypes"}
    with open(os.path.join(OUT, "index.theme"), "w") as f:
        f.write("[Icon Theme]\nName=Oxygen Pinstripe\n"
                "Comment=Oxygen with solid, rounded symbolic icons after the Mac OS X 10.2 menu extras\n"
                "Inherits=oxygen,breeze,hicolor\nExample=folder\nDisplayDepth=32\nDesktopDefault=48\nPanelDefault=22\n"
                "FollowsColorScheme=true\n"
                f"Directories={','.join(dirs)}\n\n")
        for c in sorted(contexts):
            f.write(f"[symbolic/{c}]\nContext={ctx_names[c]}\nSize=16\nMinSize=8\nMaxSize=512\nType=Scalable\n\n")
        f.write("[panel/status]\nContext=Status\nSize=22\nMinSize=16\nMaxSize=24\nType=Scalable\n\n")
    print(f"wrote {len(icons)} symbolic icons to {OUT}")


if __name__ == "__main__":
    build()
